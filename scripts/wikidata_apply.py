#!/usr/bin/env python3
"""Apply the Wikidata author-item diff through the API instead of by hand.

`audit_identity.py` already measures the difference between the live item and what
`config.yaml` says it should carry: identifiers absent, one identifier holding the
wrong value, statements added twice, aliases pasted as a single string. Everything it
reports is mechanical -- a property id and a value -- so nothing about it needed a
human except the credential.

That was the actual blocker, and it is worth being precise about which credential.
Two are often confused:

- **Autoconfirmed** (4 days old AND 50 edits) is a *QuickStatements* requirement, not
  a MediaWiki one. QuickStatements imposes it as its own policy because it runs
  unattended batches under your name.
- **A bot password** (Special:BotPasswords) is a scoped second password for the
  account you already have. `action=wbcreateclaim` and friends accept it immediately.
  No autoconfirmed, no bot flag, no community approval -- those are needed to run an
  *unattended bot account*, which this is not: it is your account, editing your own
  item, when you run the script.

So the item's statements never had to wait for the 50 edits. Only the two `.qs`
batch files do.

Setup, once:

    https://www.wikidata.org/wiki/Special:BotPasswords
      -> create one named e.g. `paper-geo`
      -> grants: "Edit existing pages" and "Create, edit, and move pages"
      -> it shows a password ONCE, in the form `Username@botname` + a long string

    export WIKIDATA_BOT_USER='Ktilana@paper-geo'
    export WIKIDATA_BOT_PASSWORD='<the long string>'

Or put those two lines in `.wikidata_bot` in the repo root -- gitignored, and read
automatically. Never in `config.yaml`: that file is committed and is the one place
this project asks you to put things about yourself in public.

    python scripts/wikidata_apply.py                 # dry run: exactly what would change
    python scripts/wikidata_apply.py --apply         # do it
    python scripts/wikidata_apply.py --check-account  # age, edit count, autoconfirmed

Dry run is the default and prints one line per intended edit with the API action it
would call. Read-only until `--apply`, like everything else here.
"""
from __future__ import annotations

import argparse
import http.cookiejar
import json
import os
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import ROOT, UA, get_json, load_config, norm_name  # noqa: E402

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
    d = get_json(f"{API}?action=query&list=users&ususers="
                 f"{urllib.parse.quote(name)}&usprop=editcount|registration|groups"
                 f"&format=json&formatversion=2") or {}
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
        # Every name variant config asks for, not just the ones the audit calls
        # missing. Those two sets differ in the case this step exists to handle: a
        # backticked alias holding "L. Choshen" normalises to the same string a real
        # alias would, so "missing" reads 0 while the useful alias is absent. Building
        # the final list from config makes the outcome independent of that.
        # Plus the known misspellings. This is the only surface they are published to,
        # and the reason is that a Wikidata alias is a lookup key rather than a claim
        # about spelling -- so it can absorb the one form nothing upstream will ever
        # fix, a typo already set in another author's reference list.
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
    return steps


def claim_guids(qid: str, pid: str) -> list[tuple[str, str]]:
    """(guid, value) for every statement of one property, so a claim can be removed."""
    d = get_json(f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json") or {}
    ent = ((d.get("entities") or {}).get(qid)) or {}
    out = []
    for c in ((ent.get("claims") or {}).get(pid) or []):
        v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
        if isinstance(v, dict):
            v = v.get("id") or v.get("text") or ""
        out.append((c.get("id"), str(v)))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--apply", action="store_true", help="write to Wikidata")
    ap.add_argument("--check-account", action="store_true",
                    help="age, edit count and autoconfirmed, then exit")
    ap.add_argument("--user", help="account name for --check-account")
    args = ap.parse_args()

    cfg = load_config()
    user, password = read_creds()
    if args.check_account:
        return check_account(args.user or user or cfg["ids"].get("wikidata_account"))

    qid = cfg["ids"].get("wikidata")
    if not qid:
        sys.exit("config.yaml has no ids.wikidata -- nothing to update.")
    # Import here, not at module scope: audit_identity pulls in the whole audit and
    # this script only wants its one diff function.
    from audit_identity import wikidata_gaps
    gaps = wikidata_gaps(qid, cfg)
    if not gaps:
        sys.exit(f"could not read {qid}")
    steps = plan(gaps, cfg)
    if not steps:
        print(f"{qid} already matches config.yaml -- nothing to do.")
        return 0

    print(f"{qid} — {len(steps)} edit{'' if len(steps) == 1 else 's'} "
          f"{'to apply' if args.apply else 'that WOULD be applied'}:\n")
    for i, s in enumerate(steps, 1):
        print(f"  {i}. {s['what']}\n     {s['why']}")
    print()

    if not args.apply:
        print("Dry run. Re-run with --apply to write.")
        if not (user and password):
            print("\nNo credentials yet. Create a bot password at\n"
                  "  https://www.wikidata.org/wiki/Special:BotPasswords\n"
                  "then set WIKIDATA_BOT_USER and WIKIDATA_BOT_PASSWORD "
                  "(or put them in .wikidata_bot).")
        return 0

    if not (user and password):
        sys.exit("--apply needs WIKIDATA_BOT_USER and WIKIDATA_BOT_PASSWORD "
                 "(see the header of this file).")
    s = Session()
    s.login(user, password)
    print(f"logged in as {s.user}\n")

    ok = 0
    for i, step in enumerate(steps, 1):
        try:
            if step["action"] == "REPLACE":
                # Remove the wrong statement and create the right one, rather than
                # editing the snak in place: wbsetclaim needs the full claim JSON and
                # gets it wrong in ways that are hard to see, while remove+create is
                # two calls whose effect is obvious in the item history.
                for guid, val in claim_guids(gaps["qid"], step["pid"]):
                    if val in step["old"]:
                        s.edit("wbremoveclaims", claim=guid,
                               summary=f"remove {step['pid']} value replaced by "
                                       f"{step['value']} (paper-geo)")
                s.edit("wbcreateclaim", entity=gaps["qid"], property=step["pid"],
                       snaktype="value", value=json.dumps(str(step["value"])),
                       summary=f"set {step['pid']} from config.yaml (paper-geo)")
            elif step["action"] == "DEDUPE":
                guids = [g for g, v in claim_guids(gaps["qid"], step["pid"])
                         if v == step["value"]]
                for guid in guids[1:]:
                    s.edit("wbremoveclaims", claim=guid,
                           summary=f"remove duplicate {step['pid']} statement "
                                   f"(paper-geo)")
            else:
                s.edit(step["action"], summary="from config.yaml (paper-geo)",
                       **step["post"])
            ok += 1
            print(f"  {i}. done — {step['what']}")
        except (RuntimeError, urllib.error.URLError) as e:
            print(f"  {i}. FAILED — {step['what']}\n     {e}")
    print(f"\n{ok}/{len(steps)} applied. Re-run "
          f"`python scripts/audit_identity.py` to confirm the diff cleared.")
    return 0 if ok == len(steps) else 1


if __name__ == "__main__":
    raise SystemExit(main())
