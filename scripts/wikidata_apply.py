#!/usr/bin/env python3
"""Apply the Wikidata author-item diff through the API instead of by hand.

`audit_identity.py` measures the difference between the live item and what `config.yaml`
says it should carry -- identifiers absent or wrong, statements added twice, aliases
pasted as one string. All of it is a property id and a value, so the only thing missing
was the credential.

A **bot password** (Special:BotPasswords) is a scoped second password for your own
account, and `wbcreateclaim`/`wbeditentity` accept it immediately. Autoconfirmed (4 days
+ 50 edits) is a *QuickStatements* policy, not a MediaWiki one, so nothing here waits on
it. The batch in `tasks/wikidata_papers.qs` is a fallback for a revoked password.

Setup, once:

    https://www.wikidata.org/wiki/Special:BotPasswords
      -> create one named e.g. `paper-geo`
      -> grants: "Edit existing pages" and "Create, edit, and move pages"
      -> it shows a password ONCE, in the form `Username@botname` + a long string

    export WIKIDATA_BOT_USER='Ktilana@paper-geo'
    export WIKIDATA_BOT_PASSWORD='<the long string>'

Or put those two lines in `.wikidata_bot` in the repo root -- gitignored, and read
automatically. Never in `config.yaml`, which is committed and public.

    python scripts/wikidata_apply.py                  # dry run: exactly what would change
    python scripts/wikidata_apply.py --apply          # do it
    python scripts/wikidata_apply.py --check-account  # age, edit count, autoconfirmed
    python scripts/wikidata_apply.py --papers         # dry run: the items that are missing
    python scripts/wikidata_apply.py --papers --apply --limit 5   # create five of them

Dry run is the default and prints one line per intended edit with the API action it
would call. Read-only until `--apply`.

`--papers` creates rather than corrects, so it keeps a ledger: every item is recorded in
`data/wikidata_created.yaml` before the next one starts, and the coverage query trusts
that file over the query service, which lags hours behind an edit. `--max-new N` refuses
to run when more than N items are missing -- a backlog is a decision, one new paper is
not.
"""
from __future__ import annotations

import argparse
import http.cookiejar
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import (ROOT, UA, affil_index, load_config, mw_replied, norm_name,  # noqa: E402
                    read_papers, read_yaml, write_yaml)

API = "https://www.wikidata.org/w/api.php"
CREDS_FILE = os.path.join(ROOT, ".wikidata_bot")


# --------------------------------------------------------------- credentials

def read_creds() -> tuple[str | None, str | None]:
    """Bot credentials from the environment, falling back to a gitignored file.

    Two sources rather than one because the two failure modes differ: an env var is
    invisible in a new shell (so a working setup stops working for no visible reason),
    and a file is easy to commit by accident. The file is in .gitignore and this
    function refuses to read it if git is tracking it, which is the check that
    actually prevents the accident.
    """
    u, p = os.environ.get("WIKIDATA_BOT_USER"), os.environ.get("WIKIDATA_BOT_PASSWORD")
    if u and p:
        return u, p
    if os.path.exists(CREDS_FILE):
        if os.popen(f"git -C {ROOT} ls-files --error-unmatch "
                    f"{CREDS_FILE} 2>/dev/null").read().strip():
            sys.exit(f"{CREDS_FILE} is tracked by git. Remove it from the index "
                     f"before putting a password in it:\n"
                     f"  git rm --cached .wikidata_bot")
        vals = {}
        with open(CREDS_FILE) as f:
            for line in f:
                line = line.strip().removeprefix("export ").strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    vals[k.strip()] = v.strip().strip("'\"")
        return vals.get("WIKIDATA_BOT_USER"), vals.get("WIKIDATA_BOT_PASSWORD")
    return None, None


class Session:
    """A logged-in MediaWiki API session.

    Cookies matter here and urllib does not keep them by default: the login response
    sets a session cookie, and a CSRF token fetched without it is a token for the
    anonymous user. That combination fails with `badtoken` rather than with anything
    mentioning cookies, which is the one confusing error in this flow.
    """

    def __init__(self):
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        self.csrf = None
        self.user = None

    def call(self, post: dict | None = None, **params) -> dict:
        params.setdefault("format", "json")
        params.setdefault("formatversion", "2")
        url = API + "?" + urllib.parse.urlencode(params)
        data = urllib.parse.urlencode(post).encode() if post else None
        req = urllib.request.Request(url, data=data, headers=dict(UA))
        with self.opener.open(req, timeout=60) as r:
            return json.loads(r.read().decode())

    def login(self, user: str, password: str) -> None:
        tok = self.call(action="query", meta="tokens", type="login")
        lt = tok["query"]["tokens"]["logintoken"]
        # action=login, not the newer clientlogin: bot passwords are only accepted by
        # this one, and clientlogin rejects them with a message about the web form.
        r = self.call(action="login",
                      post={"lgname": user, "lgpassword": password, "lgtoken": lt})
        res = (r.get("login") or {})
        if res.get("result") != "Success":
            sys.exit(f"login failed: {res.get('result')} {res.get('reason', '')}\n"
                     f"Check the credential is a bot password from "
                     f"Special:BotPasswords and that the grants include editing.")
        self.user = res.get("lgusername")
        self.csrf = self.call(action="query", meta="tokens")["query"]["tokens"]["csrftoken"]

    def edit(self, action: str, **post) -> dict:
        post.update({"token": self.csrf, "bot": "1"})
        r = self.call(action=action, post=post)
        if "error" in r:
            raise RuntimeError(f"{action}: {r['error'].get('code')} "
                               f"{r['error'].get('info')}")
        return r


# --------------------------------------------------------------- the account check

def check_account(user: str | None) -> int:
    """Age, edit count and autoconfirmed for the account, read from the public API.

    Reported because the two halves of autoconfirmed fail differently and the wiki
    never says which one you are short of: 50 edits with a 2-day-old account and a
    4-day-old account with 10 edits both just refuse QuickStatements.
    """
    name = user.split("@")[0] if user else None
    if not name:
        print("No account known. Set WIKIDATA_BOT_USER, or pass the account name:\n"
              "  python scripts/wikidata_apply.py --check-account --user Ktilana")
        return 1
    _st, d, why = mw_replied(f"{API}?action=query&list=users&ususers="
                          f"{urllib.parse.quote(name)}&usprop=editcount|registration|groups"
                          f"&format=json&formatversion=2")
    if why:
        # The API answers 200 with `missing` for an account that does not exist, so a
        # refusal is something else -- and every line below would read as a brand-new
        # account four days short of autoconfirmed.
        print(f"wikidata did not answer ({why}), so nothing is known about {name}")
        return 1
    u = ((d.get("query") or {}).get("users") or [{}])[0]
    if "missing" in u:
        print(f"No such account: {name}")
        return 1
    groups = u.get("groups") or []
    auto = "autoconfirmed" in groups
    print(f"account       {u.get('name')}")
    print(f"registered    {u.get('registration')}")
    print(f"edits         {u.get('editcount')}  "
          f"({'50 reached' if (u.get('editcount') or 0) >= 50 else 'need 50'})")
    print(f"groups        {', '.join(groups)}")
    print(f"autoconfirmed {'yes' if auto else 'not yet'}")
    if not auto:
        print("\nAutoconfirmed gates QuickStatements only. Statements on the item go\n"
              "through this script with a bot password and do not wait for it.")
    return 0


# --------------------------------------------------------------- the plan

def plan(gaps: dict, cfg: dict) -> list[dict]:
    """Turn the audit's diff into an ordered list of API calls.

    Ordering is deliberate. Aliases first, because a wrong alias is the only defect
    here that makes the item match *nothing* -- an absent identifier merely fails to
    help. Then wrong values, then duplicates, then additions: corrections before
    growth, so a run that fails halfway leaves the item more correct rather than
    bigger.
    """
    steps = []
    if gaps.get("bad_aliases") or gaps.get("want_aliases"):
        keep = [a for a in gaps.get("aliases") or [] if a not in gaps["bad_aliases"]]
        # Every name variant config asks for, not just the ones the audit calls missing: a
        # backticked alias holding "L. Choshen" normalises to the string a real alias would,
        # so "missing" reads 0 while the useful alias is absent. Building the list from config
        # makes the outcome independent of that.
        #
        # Plus the known misspellings, published nowhere else. A Wikidata alias is a lookup key
        # rather than a claim about spelling, so it can absorb the one form nothing upstream will
        # fix -- a typo already set in another author's reference list.
        want = [v for v in (list(cfg["identity"]["name_variants"])
                            + list(cfg["identity"].get("name_typos") or []))
                if v != cfg["identity"]["name"]]
        # Set the whole alias list in one call rather than remove-then-add: two calls
        # means two revisions and a window where the item has no alias at all.
        final = keep + [w for w in want
                        if not any(norm_name(w) == norm_name(k) for k in keep)]
        if not final:
            sys.exit("refusing to clear every alias: config.yaml lists no name "
                     "variants to put back. Add identity.name_variants first.")
        steps.append({"what": f"aliases -> {final}",
                      "why": (f"drop {len(gaps['bad_aliases'])} pasted-as-one-string, "
                              f"set {len(final)} from config.yaml"),
                      "action": "wbsetaliases",
                      "post": {"id": gaps["qid"], "language": "en",
                               "set": "|".join(final)}})
    for pid, label, want, have in gaps.get("wrong") or []:
        steps.append({"what": f"{pid} ({label}): {have} -> {want}",
                      "why": "value does not match config.yaml",
                      "action": "REPLACE", "pid": pid, "value": want, "old": have})
    for pid, value, n in gaps.get("dupes") or []:
        steps.append({"what": f"{pid}: remove {n - 1} duplicate of {value!r}",
                      "why": "the same statement added more than once",
                      "action": "DEDUPE", "pid": pid, "value": value})
    for pid, label, want in gaps.get("missing") or []:
        steps.append({"what": f"{pid} ({label}) = {want}",
                      "why": "typed identifier, absent from the item",
                      "action": "wbcreateclaim",
                      "post": {"entity": gaps["qid"], "property": pid,
                               "snaktype": "value", "value": json.dumps(str(want))}})
    steps += qualifier_steps(gaps, cfg)
    return steps


# ORCID states the role in free text, so only titles that map to a Wikidata item become
# a `position held` qualifier. Anything else keeps its start time and no role.
ROLES = {"postdoctoral researcher": ("Q1125292", "postdoctoral researcher"),
         "postdoc": ("Q1125292", "postdoctoral researcher"),
         "research scientist": ("Q1650915", "research scientist"),
         "phd student": ("Q12722588", "doctoral student")}

DEGREES = {"phd": ("Q752297", "Doctor of Philosophy"),
           "msc": ("Q12047422", "Master of Science"),
           "ma": ("Q1765120", "Master of Arts"),
           "bsc": ("Q798137", "Bachelor of Science")}


def date_snak(year, precision: int = 9) -> str:
    """A Wikibase time value for a year, as the JSON `wbsetqualifier` wants."""
    return json.dumps({"time": f"+{int(year)}-00-00T00:00:00Z", "timezone": 0,
                       "before": 0, "after": 0, "precision": precision,
                       "calendarmodel": CAL})


def item_snak(qid: str) -> str:
    """A Wikibase item value, as the JSON `wbsetqualifier` wants."""
    return json.dumps({"entity-type": "item", "id": qid})


def qualifier_steps(gaps: dict, cfg: dict) -> list[dict]:
    """Start times, roles and degrees for statements the item carries bare.

    `P108` with no `P580` is a set of employers rather than a career, and `P69` with no
    `P512` does not say which degree. Both are on the ORCID record, which is the same
    source `config.yaml` was written from, so neither is a question for the author.
    Statements ORCID has no row for are left alone and stay in the follow-up file.
    """
    bare = gaps.get("unqualified") or []
    if not bare:
        return []
    from audit_identity import orcid_public
    rec = orcid_public(cfg["identity"]["orcid"]) or {}
    rows = {"P108": affil_index(rec.get("employment_rows")),
            "P69": affil_index(rec.get("education_rows"))}
    guids = {pid: {v: g for g, v in claim_guids(gaps["qid"], pid)}
             for pid in ("P108", "P69")}
    named = [str(e.get("degree") or "") for e in cfg["identity"].get("education") or []]
    steps = []
    for pid, q, label in bare:
        guid = guids.get(pid, {}).get(q)
        row = rows.get(pid, {}).get(re.sub(r"^the ", "", norm_name(label)))
        if not (guid and row):
            continue

        def qual(prop: str, value: str, what: str, why: str) -> dict:
            return {"what": f"{pid} {label}: {what}", "why": why,
                    "action": "wbsetqualifier",
                    "summary": "qualifier from the ORCID record (paper-geo)",
                    "post": {"claim": guid, "property": prop, "snaktype": "value",
                             "value": value}}

        if row.get("start"):
            steps.append(qual("P580", date_snak(row["start"]),
                              f"start time {row['start']}",
                              f"ORCID states {row['start']} for this affiliation"))
        if row.get("end"):
            steps.append(qual("P582", date_snak(row["end"]), f"end time {row['end']}",
                              f"ORCID states it ended {row['end']}"))
        if pid == "P108":
            role = next((ROLES[r.strip().lower()] for r in row["roles"]
                         if r.strip().lower() in ROLES), None)
            if role:
                steps.append(qual("P39", item_snak(role[0]),
                                  f"position held {role[1]}",
                                  f"ORCID states the role as {row['roles'][0]!r}"))
        else:
            deg = next((DEGREES[d] for d in
                        (n.strip().lower().replace(".", "") for n in row["roles"] + named)
                        if d in DEGREES), None)
            if deg:
                steps.append(qual("P512", item_snak(deg[0]),
                                  f"academic degree {deg[1]}",
                                  "the degree is what separates a doctorate from a "
                                  "semester abroad"))
    return steps


def claim_guids(qid: str, pid: str) -> list[tuple[str, str]]:
    """(guid, value) for every statement of one property, so a claim can be removed.

    Raises when the item did not answer. `[]` means the item carries no statement of this
    property, which is what a `REPLACE` step reads before creating the replacement -- so a
    refusal read as `[]` leaves the wrong value in place beside the new one.
    """
    _st, d, why = mw_replied(
        f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json")
    if why:
        raise RuntimeError(f"could not read {qid} ({why}), so the statements it "
                           f"carries for {pid} are unknown")
    ent = ((d.get("entities") or {}).get(qid)) or {}
    out = []
    for c in ((ent.get("claims") or {}).get(pid) or []):
        v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        if isinstance(v, dict):
            v = v.get("id") or v.get("text") or ""
        out.append((c.get("id"), str(v)))
    return out


# --------------------------------------------------------------- paper items

# Proleptic Gregorian, which is the calendar every Wikibase date carries whether or not
# it matters. Omitting it is accepted and then stored as this anyway.
CAL = "http://www.wikidata.org/entity/Q1985727"


def snak(pid: str, v: str) -> dict:
    """One `wbeditentity` snak from the three value forms the QuickStatements files use.

    A QID, a quoted string, or a date with the precision after a slash.
    """
    v = str(v)
    if v.startswith("Q"):
        dv = {"value": {"entity-type": "item", "id": v}, "type": "wikibase-entityid"}
    elif v.startswith("+"):
        stamp, _, prec = v.partition("/")
        dv = {"value": {"time": stamp, "timezone": 0, "before": 0, "after": 0,
                        "precision": int(prec or 11), "calendarmodel": CAL},
              "type": "time"}
    else:
        dv = {"value": v.strip('"'), "type": "string"}
    return {"snaktype": "value", "property": pid, "datavalue": dv}


def item_json(it: dict) -> dict:
    """One paper from `wikidata_audit.paper_item`, as a `wbeditentity` payload.

    One call per item rather than a create followed by a claim per statement. An item
    that exists with a title and no identifier is indistinguishable from a placeholder
    somebody should delete, and a run interrupted between the two calls leaves exactly
    that -- under your name, on a wiki, with no way for a later run to recognise it.
    `wbeditentity` is atomic: the item arrives whole or not at all.
    """
    def claim(pid: str, dv, dtype: str, quals: dict | None = None) -> dict:
        c = {"mainsnak": {"snaktype": "value", "property": pid,
                          "datavalue": {"value": dv, "type": dtype}},
             "type": "statement", "rank": "normal"}
        if quals:
            c["qualifiers"] = quals
        return c

    claims = [claim("P31", {"entity-type": "item", "id": it["instance_of"]},
                    "wikibase-entityid"),
              claim("P1476", {"text": it["title"], "language": "en"}, "monolingualtext")]
    if it["year"]:
        # Precision 9 is "year". The bibliography carries a year and no month, and a
        # date of January would be a fact nothing in this pipeline knows.
        claims.append(claim("P577", {"time": f"+{it['year']}-00-00T00:00:00Z",
                                     "timezone": 0, "before": 0, "after": 0,
                                     "precision": 9, "calendarmodel": CAL}, "time"))
    if it["doi"]:
        claims.append(claim("P356", it["doi"], "string"))
    if it["arxiv"]:
        claims.append(claim("P818", it["arxiv"], "string"))
    for a in it["authors"]:
        ordinal = {"P1545": [{"snaktype": "value", "property": "P1545",
                              "datavalue": {"value": str(a["ordinal"]),
                                            "type": "string"}}]}
        if a["pid"] == "P50":
            claims.append(claim("P50", {"entity-type": "item", "id": a["qid"]},
                                "wikibase-entityid", ordinal))
        else:
            claims.append(claim("P2093", a["name"], "string", ordinal))
    return {"labels": {"en": {"language": "en", "value": it["label"]}}, "claims": claims}


def papers_plan(cfg: dict, limit: int | None = None) -> list[dict] | None:
    """The paper items Wikidata is missing, measured now rather than read from a file.

    `tasks/wikidata_papers.qs` is as old as the last `update.py`, and the thing being avoided is
    creating an item that already exists. Coverage folds in `data/wikidata_created.yaml`, so a
    run minutes after the last one still knows what it did.

    Returns None -- not [] -- when the query service does not answer. "Nothing is missing" and
    "I could not find out" differ by 108 items. A run the endpoint answered only part of
    yields only the papers it answered about, so a refused chunk is never created twice.
    """
    from audit_identity import paper_item, wikidata_paper_coverage
    papers = read_papers()
    if not papers:
        sys.exit("data/papers.yaml is empty -- run `python update.py --step collect` first.")
    cov = wikidata_paper_coverage(papers)
    if not cov:
        return None
    out = [i for i in (paper_item(p, cfg) for p in cov["absent"]) if i]
    return out[:limit] if limit else out


def create_papers(s: "Session", items: list[dict]) -> int:
    """Create each item, recording the QID before moving on. Returns how many landed."""
    from audit_identity import record_created
    ok = 0
    for i, it in enumerate(items, 1):
        try:
            r = s.edit("wbeditentity", new="item", data=json.dumps(item_json(it)),
                       summary=f"create item for {it['doi'] or it['arxiv']} (paper-geo)")
            qid = ((r.get("entity") or {}).get("id")) or ""
            if not qid:
                raise RuntimeError("no entity id in the response")
            # Before the next create, not after the loop: the run that most needs this
            # written is the one that dies in the middle.
            record_created(it["slug"], qid)
            ok += 1
            print(f"  {i}/{len(items)} {qid} — {it['label'][:58]}")
        except (RuntimeError, urllib.error.URLError) as e:
            print(f"  {i}/{len(items)} FAILED — {it['label'][:58]}\n     {e}")
        # Politeness, not a rate limit: nothing here is close to one. It keeps a
        # hundred creations off the recent-changes feed as a single burst, which is
        # what gets a good-faith batch reverted wholesale.
        time.sleep(1.5)
    return ok


def logged_in(user: str | None = None, password: str | None = None) -> "Session":
    """A logged-in session, or exit saying which credential is missing.

    Reads the credential from the environment or `.wikidata_bot` when not handed one.
    """
    if not (user and password):
        user, password = read_creds()
    if not (user and password):
        sys.exit("no bot credential. Set WIKIDATA_BOT_USER and WIKIDATA_BOT_PASSWORD, or "
                 "put them in .wikidata_bot -- see the module docstring of "
                 "scripts/wikidata_apply.py")
    s = Session()
    s.login(user, password)
    print(f"logged in as {s.user}\n")
    return s


def recorded(ledger: str) -> dict[str, str]:
    """The key-to-QID receipts in one ledger file."""
    return (read_yaml(ledger) or {}).get("items") or {}


def create_items(s: "Session", items: list[tuple[str, str, dict]], ledger: str,
                 summary: str, note: str = "") -> int:
    """Create each item atomically, writing its QID to the ledger before the next starts.

    `items` is (key, label, wbeditentity payload). One call per item rather than a create
    followed by a claim each: an interrupted run would otherwise leave a labelled item
    with no identifier on it, which is indistinguishable from something to delete.

    The query service lags hours behind an edit, so until it catches up the ledger is the
    only thing that knows these exist. Returns how many landed.
    """
    d = read_yaml(ledger) or {}
    if note and not d.get("note"):
        d["note"] = note
    got = d.setdefault("items", {})
    # The label is kept beside the QID so a later run can name what it made without asking
    # the query service, which does not answer about a new item for hours.
    named = d.setdefault("labels", {})
    ok = 0
    for i, (key, label, payload) in enumerate(items, 1):
        try:
            r = s.edit("wbeditentity", new="item", data=json.dumps(payload),
                       summary=f"{summary} (paper-geo)")
            qid = ((r.get("entity") or {}).get("id")) or ""
            if not qid:
                raise RuntimeError("no entity id in the response")
            got[key] = qid
            named[qid] = label
            write_yaml(ledger, d)
            ok += 1
            print(f"  {i}/{len(items)} {qid} — {label[:58]}")
        except (RuntimeError, urllib.error.URLError) as e:
            print(f"  {i}/{len(items)} FAILED — {label[:58]}\n     {e}")
        # Politeness rather than a rate limit. It keeps a batch off the recent-changes
        # feed as a single burst, which is what gets a good-faith run reverted wholesale.
        time.sleep(1.5)
    return ok


def papers_main(args, cfg: dict, user: str | None, password: str | None) -> int:
    items = papers_plan(cfg, args.limit)
    if items is None:
        sys.exit("query-scholarly.wikidata.org did not answer, so what is missing is "
                 "unknown. Nothing was created. Try again later.")
    if not items:
        print("Every paper with a DOI or an arXiv id already has a Wikidata item.")
        return 0
    if args.max_new and len(items) > args.max_new:
        # The unattended guard. An automated run should keep up with new papers and
        # should never decide, on its own, to add a hundred items to somebody's wiki.
        print(f"{len(items)} items are missing, which is more than --max-new "
              f"{args.max_new}. That is a backlog rather than a new paper, so it is "
              f"yours to start:\n  python scripts/wikidata_apply.py --papers --apply")
        return 0

    print(f"{len(items)} paper item{'' if len(items) == 1 else 's'} "
          f"{'to create' if args.apply else 'that WOULD be created'}:\n")
    for i, it in enumerate(items, 1):
        kind = "article" if it["instance_of"] == "Q13442814" else "preprint"
        print(f"  {i}. {it['label'][:64]}")
        print(f"     {kind}, {it['year'] or 'no year'}, "
              f"{it['doi'] or it['arxiv']}, {len(it['authors'])} authors")
    print()
    if not args.apply:
        print("Dry run. Re-run with --apply to create these.\n"
              "Same statements as tasks/wikidata_papers.qs, which is the "
              "paste-it-yourself route.")
        return 0
    s = logged_in(user, password)
    ok = create_papers(s, items)
    print(f"\n{ok}/{len(items)} created, recorded in data/wikidata_created.yaml.\n"
          f"Commit that file -- it is what stops the next run recreating them while "
          f"the query service catches up.")
    return 0 if ok == len(items) else 1


def parse_args():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--apply", action="store_true", help="write to Wikidata")
    ap.add_argument("--check-account", action="store_true",
                    help="age, edit count and autoconfirmed, then exit")
    ap.add_argument("--user", help="account name for --check-account")
    ap.add_argument("--papers", action="store_true",
                    help="create items for your papers Wikidata lacks, instead of "
                         "updating the author item")
    ap.add_argument("--limit", type=int, help="--papers: create at most this many")
    ap.add_argument("--max-new", type=int,
                    help="--papers: do nothing at all if more than this many are "
                         "missing. For unattended runs.")
    return ap.parse_args()


def author_plan(cfg: dict) -> tuple[str, dict, list[dict]]:
    """The author item named in config.yaml, its gaps, and the edits that close them.

    Exits rather than returning on the three ways there is nothing to plan: no item
    configured, an item that would not read, and a config the planner refuses.
    """
    qid = cfg["ids"].get("wikidata")
    if not qid:
        sys.exit("config.yaml has no ids.wikidata -- nothing to update.")
    # Import here, not at module scope: audit_identity pulls in the whole audit and
    # this script only wants its one diff function.
    from audit_identity import wikidata_gaps
    gaps = wikidata_gaps(qid, cfg)
    if not gaps:
        sys.exit(f"could not read {qid}")
    try:
        return qid, gaps, plan(gaps, cfg)
    except RuntimeError as e:
        sys.exit(str(e))


def show_steps(qid: str, steps: list[dict], applying: bool) -> None:
    """Print each planned edit and the reason the planner gives for it."""
    print(f"{qid} — {len(steps)} edit{'' if len(steps) == 1 else 's'} "
          f"{'to apply' if applying else 'that WOULD be applied'}:\n")
    for i, s in enumerate(steps, 1):
        print(f"  {i}. {s['what']}\n     {s['why']}")
    print()


def apply_step(s: "Session", qid: str, step: dict) -> None:
    """Make one planned edit against `qid`."""
    if step["action"] == "REPLACE":
        # Remove the wrong statement and create the right one, rather than
        # editing the snak in place: wbsetclaim needs the full claim JSON and
        # gets it wrong in ways that are hard to see, while remove+create is
        # two calls whose effect is obvious in the item history.
        for guid, val in claim_guids(qid, step["pid"]):
            if val in step["old"]:
                s.edit("wbremoveclaims", claim=guid,
                       summary=f"remove {step['pid']} value replaced by "
                               f"{step['value']} (paper-geo)")
        s.edit("wbcreateclaim", entity=qid, property=step["pid"],
               snaktype="value", value=json.dumps(str(step["value"])),
               summary=f"set {step['pid']} from config.yaml (paper-geo)")
    elif step["action"] == "DEDUPE":
        guids = [g for g, v in claim_guids(qid, step["pid"])
                 if v == step["value"]]
        for guid in guids[1:]:
            s.edit("wbremoveclaims", claim=guid,
                   summary=f"remove duplicate {step['pid']} statement "
                           f"(paper-geo)")
    else:
        s.edit(step["action"],
               summary=step.get("summary", "from config.yaml (paper-geo)"),
               **step["post"])


def apply_steps(s: "Session", qid: str, steps: list[dict]) -> int:
    """Make every planned edit, reporting each, and return how many landed.

    One step failing does not stop the rest: the steps are independent statements and
    a rerun re-plans from the live item, so a partial pass leaves no half-edit behind.
    """
    ok = 0
    for i, step in enumerate(steps, 1):
        try:
            apply_step(s, qid, step)
            ok += 1
            print(f"  {i}. done — {step['what']}")
        except (RuntimeError, urllib.error.URLError) as e:
            print(f"  {i}. FAILED — {step['what']}\n     {e}")
    return ok


def main() -> int:
    args = parse_args()
    cfg = load_config()
    user, password = read_creds()
    if args.check_account:
        return check_account(args.user or user or cfg["ids"].get("wikidata_account"))
    if args.papers:
        return papers_main(args, cfg, user, password)

    qid, gaps, steps = author_plan(cfg)
    if not steps:
        print(f"{qid} already matches config.yaml -- nothing to do.")
        return 0
    show_steps(qid, steps, args.apply)

    if not args.apply:
        print("Dry run. Re-run with --apply to write.")
        if not (user and password):
            print("\nNo credentials yet. Create a bot password at\n"
                  "  https://www.wikidata.org/wiki/Special:BotPasswords\n"
                  "then set WIKIDATA_BOT_USER and WIKIDATA_BOT_PASSWORD "
                  "(or put them in .wikidata_bot).")
        return 0

    # The item the gaps were read from, which is what a redirect makes different from
    # the one config.yaml names.
    ok = apply_steps(logged_in(user, password), gaps["qid"], steps)
    print(f"\n{ok}/{len(steps)} applied. Re-run "
          f"`python scripts/audit_identity.py` to confirm the diff cleared.")
    return 0 if ok == len(steps) else 1


if __name__ == "__main__":
    raise SystemExit(main())
