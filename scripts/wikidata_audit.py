#!/usr/bin/env python3
"""What Wikidata says about the author and the papers, and the edits that would fix it.

Two readings, both over the public SPARQL and API endpoints. `wikidata_gaps` reads the
author item -- whether one carries the ORCID at all, and which statements it is missing.
`wikidata_paper_coverage` reads the papers, matching each against items by DOI, arXiv id
and title. Both report an absence, so `_wd_quiet` records a call that did not answer.

The write side is QuickStatements text and a followup page, never an edit: an item this
creates would be the author's own claim about themself.
"""
from __future__ import annotations

import os
import sys
import textwrap
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (DATA, ROOT, TASKS, WD_IDENTIFIERS, clipped,  # noqa: E402
                    get_json, mw_replied, norm_name, org_name, plural, read_yaml,
                    write_task, write_yaml)

# Set to the first Wikidata call that did not answer. Both readings below report an
# absence -- no item claims this identifier, this item states no gaps -- and every way of
# not answering reports the same absence, which reads on the page as an item in order.
_wd_quiet = ""


def wd_asked(url: str) -> dict:
    """One Wikidata call, `{}` if it did not answer, with the refusal recorded.

    Both endpoints answer 200 with an empty result for something they do not have, so any
    other status is a refusal rather than a report.
    """
    global _wd_quiet
    _st, d, why = mw_replied(url)
    if why:
        _wd_quiet = _wd_quiet or why
    return d or {}


def wikidata_item(cfg) -> str | None:
    """Find an author item by any identifier we already know, not by name.

    Name search on Wikidata returns paper items that merely mention you, which is
    the failure mode that made this look done once already. Statement search is
    exact: either an item claims the identifier or none does.
    """
    ident, ids = cfg["identity"], cfg["ids"]
    probes = [("P496", ident["orcid"]), ("P4012", ids["semantic_scholar_primary"]),
              ("P1960", ids["google_scholar"]), ("P2037", ids["github"])]
    for prop, val in probes:
        q = quote(f'haswbstatement:"{prop}={val}"')
        j = wd_asked("https://www.wikidata.org/w/api.php?action=query&list=search"
                     f"&srsearch={q}&srlimit=5&format=json")
        for hit in ((j.get("query") or {}).get("search") or []):
            return hit["title"]
    return None


def wd_labels(qids) -> dict:
    """QID -> English label for up to 50 items, `{}` if the API does not answer.

    Through `wd_asked`, so a refusal here reaches `carry_wikidata` like every other one.
    Callers fall back to the QID, which is a readable row rather than a missing one.
    """
    ids = sorted({q for q in qids if q})
    if not ids:
        return {}
    d = wd_asked(f"https://www.wikidata.org/w/api.php?action=wbgetentities&format=json"
                 f"&props=labels&languages=en&ids={'|'.join(ids[:50])}")
    return {q: ((e.get("labels") or {}).get("en") or {}).get("value", q)
            for q, e in (d.get("entities") or {}).items()}


def wikidata_gaps(qid: str, cfg) -> dict:
    """Diff a live Wikidata item against the identifiers config says it should carry.

    Worth checking rather than assuming, because hand-created items acquire two
    specific defects that are invisible on the page: a statement added twice (the
    editor does not warn), and an alias pasted as one string when it was meant as
    several -- markdown backticks and all, which is what happened here. Both are
    silent: the item looks complete and queries against it come back wrong.
    """
    d = wd_asked(f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json")
    ent = ((d.get("entities") or {}).get(qid)) or {}
    if not ent:
        return {}
    vals: dict[str, list[str]] = {}
    for pid, claims in (ent.get("claims") or {}).items():
        for c in claims:
            v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
            if isinstance(v, dict):
                v = v.get("id") or v.get("text") or v.get("amount") or ""
            vals.setdefault(pid, []).append(str(v))

    missing, wrong, dupes = [], [], []
    for pid, label, pick in WD_IDENTIFIERS:
        want = pick(cfg)
        if not want:
            continue
        have = vals.get(pid) or []
        if not have:
            missing.append((pid, label, want))
        elif not any(str(want).rstrip("/") == h.rstrip("/") for h in have):
            wrong.append((pid, label, want, have))
    for pid, have in vals.items():
        for v in {h for h in have if have.count(h) > 1}:
            dupes.append((pid, v, have.count(v)))

    aliases = [a.get("value", "") for a in ((ent.get("aliases") or {}).get("en") or [])]
    # An alias carrying a backtick or a comma-plus-quote came from pasting a markdown
    # table cell into the single-alias box, so several names became one string that
    # matches nothing.
    bad_aliases = [a for a in aliases if "`" in a or a.count(",") > 1]
    # Compare against the *good* aliases only. A backticked string containing "L.
    # Choshen" normalises to the same thing the real alias would, so counting it as
    # present reported "0 missing" for a name the item does not usefully carry -- and
    # anything acting on this diff would then remove the bad alias and add nothing.
    good = [a for a in aliases if a not in bad_aliases]
    # Typos belong in this list and in no other published surface: a Wikidata alias is
    # a search key, not an assertion about how the name is spelled, and their guidelines
    # name common misspellings as a reason to add one. The payoff is the citation
    # already printed in someone else's paper, which cannot be fixed upstream ever.
    want = [v for v in (list(cfg["identity"]["name_variants"])
                        + list(cfg["identity"].get("name_typos") or []))
            if v != cfg["identity"]["name"]]
    want_aliases = [v for v in want
                    if not any(norm_name(v) == norm_name(a) for a in good)]
    # A statement with no qualifier is not a gap the identifier diff above can see, and
    # two of them carry most of the disambiguating weight: an employer with no start time
    # is not a career an engine can order, and a degree-less `educated at` does not say
    # which degree.
    bare = [(pid, ((c.get("mainsnak") or {}).get("datavalue") or {})
             .get("value", {}).get("id", ""))
            for pid, want in (("P108", "P580"), ("P69", "P512"))
            for c in (ent.get("claims") or {}).get(pid, [])
            if want not in (c.get("qualifiers") or {})]
    lab = wd_labels([q for _p, q in bare])
    unqualified = [(pid, q, lab.get(q, q)) for pid, q in bare]
    return {"qid": qid, "missing": missing, "wrong": wrong, "dupes": dupes,
            "aliases": aliases, "bad_aliases": bad_aliases,
            "want_aliases": want_aliases, "has": vals, "unqualified": unqualified,
            "n_p856": len(vals.get("P856") or []),
            "label": (ent.get("labels") or {}).get("en", {}).get("value", ""),
            "description": (ent.get("descriptions") or {}).get("en", {}).get("value", "")}


CREATED = os.path.join(DATA, "wikidata_created.yaml")


def carry_wikidata(state: dict, prev: dict) -> str:
    """Put the last run's Wikidata counts back, if Wikidata did not answer this run.

    Returns what did not answer, or `""`. Every one of these counts is `None` when the
    item could not be read, and the worklist builds its Wikidata sections from them, so
    writing them would take the sections away -- which reads as work already done rather
    than as a reading this run does not have.
    """
    if not _wd_quiet:
        return ""
    for k in ("wikidata_gaps", "wikidata_papers_present", "wikidata_papers_absent",
              "wikidata_papers_creatable"):
        if k in prev:
            state[k] = prev[k]
    return _wd_quiet


def created_items() -> dict:
    """slug -> QID for every Wikidata item this repo created, read from `data/`.

    Committed, and never hand-edited: it is a receipt for an edit on a wiki, and it cannot
    be re-derived because the query service lags behind the edit, which is the problem it
    exists to solve. Under `build/` it would be empty on every CI clone, so every scheduled
    run would look like the first. A stale line is self-correcting -- coverage would have
    found the item by its DOI anyway.
    """
    return (read_yaml(CREATED) or {}).get("items") or {}


def record_created(slug: str, qid: str) -> None:
    """Append one created item to the ledger, immediately.

    Written per item rather than once at the end of the batch: the run that most needs
    this file is the one that dies in the middle, and a ledger written after the loop
    records nothing about the eleven items already on the wiki.
    """
    d = read_yaml(CREATED) or {}
    items = d.setdefault("items", {})
    if items.get(slug) == qid:
        return
    items[slug] = qid
    write_yaml(CREATED, d)


def wikidata_paper_coverage(papers, chunk: int = 50) -> dict:
    """How many of the corpus papers exist as Wikidata items, measured rather than assumed.

    Returns {} when the endpoint does not answer, so a timeout never reads as absence.
    Matching is on DOI (P356) and arXiv id (P818), never name. DOIs go in twice, as given
    and uppercased, since Wikidata's convention is uppercase and SPARQL match is not.

    The endpoint must be query-scholarly. Scholarly articles have their own graph now, and
    `query.wikidata.org` answers a publication query with zero rows and HTTP 200.

    Items from `data/wikidata_created.yaml` are folded in whatever the query says, since the
    scholarly endpoint can take hours to index a new item and a second run inside that
    window would recreate the batch. A duplicate publication item needs somebody else to
    merge it.
    """
    keys: dict[str, dict] = {}
    for p in papers:
        if p.get("arxiv"):
            keys.setdefault(str(p["arxiv"]).strip(), p)
        if p.get("doi"):
            d = str(p["doi"]).strip()
            keys.setdefault(d, p)
            keys.setdefault(d.upper(), p)
    if not keys:
        return {}

    ordered = list(keys)
    found: dict[str, str] = {}
    answered: set[str] = set()
    for i in range(0, len(ordered), chunk):
        block = ordered[i:i + chunk]
        vals = " ".join('"%s"' % k.replace('"', "") for k in block)
        # One query, two properties: the identifier forms are disjoint, so a UNION
        # over both costs the same as testing each list separately.
        sparql = ("SELECT ?item ?v WHERE { VALUES ?v {" + vals + "} "
                  "{ ?item wdt:P818 ?v } UNION { ?item wdt:P356 ?v } }")
        j = get_json("https://query-scholarly.wikidata.org/sparql?format=json&query="
                     + quote(sparql))
        if j is None:
            continue
        answered.update(block)
        for b in ((j.get("results") or {}).get("bindings") or []):
            v = (b.get("v") or {}).get("value", "")
            qid = ((b.get("item") or {}).get("value", "")).rsplit("/", 1)[-1]
            if v in keys and qid:
                found[keys[v]["slug"]] = qid
    if not answered:
        return {}
    for slug, qid in (created_items() or {}).items():
        found.setdefault(slug, qid)

    # A paper is absent only when the endpoint answered for one of its keys. `absent` is
    # what `wikidata_apply.py --papers --apply` turns into item creations, so a chunk that
    # timed out must not land there -- that mints a duplicate publication item, and merging
    # one needs somebody else.
    asked = {p["slug"] for k, p in keys.items() if k in answered}
    present = [(p, found[p["slug"]]) for p in papers if p["slug"] in found]
    rest = [p for p in papers if p["slug"] not in found]
    return {"present": present,
            "absent": [p for p in rest if p["slug"] in asked],
            "unchecked": [p for p in rest if p["slug"] not in asked],
            "checked": len(asked), "total": len(papers)}


def paper_item(p: dict, cfg) -> dict | None:
    """The Wikidata item one paper should become, as one dict two renderers share.

    Returns None for a paper carrying neither a DOI nor an arXiv id. A resolvable external
    identifier is what puts a publication item uncontroversially in scope, and it is the key
    coverage is measured on, so an item without one could be a duplicate nothing detects.

    Both creators render this dict -- the QuickStatements batch below and `wikidata_apply.py
    --papers` -- so the file read to check the batch cannot describe different items from
    the ones the API path creates.

    Co-authors go in as `author name string` (P2093) with a series-ordinal qualifier rather
    than `author` (P50), which would weld a guessed person item to the paper. A later
    disambiguator upgrades the strings safely.
    """
    if not (p.get("doi") or p.get("arxiv")):
        return None
    me = cfg["ids"].get("wikidata")
    title = (p.get("title_display") or p["title"]).replace('"', "'").strip()
    authors = []
    for i, a in enumerate(p.get("authors") or [], 1):
        a = a.replace('"', "'").strip()
        if not a:
            continue
        if me and norm_name(a) == norm_name(cfg["identity"]["name"]):
            authors.append({"pid": "P50", "qid": me, "ordinal": i})
        else:
            authors.append({"pid": "P2093", "name": a, "ordinal": i})
    return {
        "slug": p["slug"],
        # Wikidata rejects a label over 250 characters outright, and a QuickStatements
        # batch stops on the offending row rather than skipping it.
        "label": title[:245],
        "title": title,
        # A 10.48550 DOI is arXiv minting one for its own preprint, so it is not
        # evidence of publication -- classing those as scholarly articles would assert
        # a venue that does not exist.
        "instance_of": ("Q13442814"
                        if p.get("doi")
                        and not str(p["doi"]).lower().startswith("10.48550/")
                        else "Q580922"),
        "year": int(p["year"]) if p.get("year") else None,
        # Uppercase because that is Wikidata's convention for P356, and coverage
        # matches the string exactly.
        "doi": str(p["doi"]).upper() if p.get("doi") else None,
        "arxiv": str(p["arxiv"]) if p.get("arxiv") else None,
        "authors": authors,
    }


def wikidata_papers_qs(cov: dict, cfg) -> tuple[str | None, int]:
    """QuickStatements batch that creates items for the papers Wikidata lacks.

    Kept alongside `wikidata_apply.py --papers`, which does the same work through the API,
    because the two fail differently: a paste into QuickStatements needs no autoconfirmed
    account and no stored credential, so it is the fallback if the bot password is ever
    revoked. Both render `paper_item`, so they agree by construction.
    """
    items = [i for i in (paper_item(p, cfg) for p in (cov.get("absent") or [])) if i]
    path = os.path.join(TASKS, "wikidata_papers.qs")
    if not items:
        # Deleted, not left alone. This file is a paste-into-QuickStatements batch of
        # CREATEs, so a stale copy is not merely out of date -- pasting it creates a
        # second item for every paper that has since been imported. The batch from
        # 2026-08-12 carried 108 CREATEs and survived every run after coverage reached
        # 111 of 113, because returning early skipped the write instead of clearing it.
        if os.path.exists(path):
            os.remove(path)
        return None, 0
    L: list[str] = []
    for it in items:
        L += ["CREATE",
              f'LAST\tLen\t"{it["label"]}"',
              f"LAST\tP31\t{it['instance_of']}",
              f'LAST\tP1476\ten:"{it["title"]}"']
        if it["year"]:
            L.append(f'LAST\tP577\t+{it["year"]}-00-00T00:00:00Z/9')
        if it["doi"]:
            L.append('LAST\tP356\t"%s"' % it["doi"])
        if it["arxiv"]:
            L.append('LAST\tP818\t"%s"' % it["arxiv"])
        for a in it["authors"]:
            val = a["qid"] if a["pid"] == "P50" else '"%s"' % a["name"]
            L.append(f'LAST\t{a["pid"]}\t{val}\tP1545\t"{a["ordinal"]}"')
    with open(path, "w") as f:
        f.write("\n".join(L) + "\n")
    return path, len(items)


def disambiguating_statements(g: dict, ident, given: str, family: str,
                             orc: dict | None = None) -> list[str]:
    """The non-identifier statements the item does not carry yet, or `[]`.

    A diff against the live item, so every row is open work and the block disappears
    once the item is complete. Qualifier gaps are split by who can settle them: a start
    time the ORCID record states belongs to `wikidata_apply.py`, and only an employment
    ORCID does not list is the author's to date.
    """
    have, L = g.get("has") or {}, []
    edu = "; ".join(f"{e.get('institution')}"
                    + (f" ({e['degree']})" if e.get("degree") else "")
                    for e in (ident.get("education") or [])) or "your PhD institution"
    def _wd(a):
        q = a.get("wikidata") if isinstance(a, dict) else None
        return f" (`{q}`)" if q else ""

    emp = "; ".join(f"{org_name(a)}{_wd(a)}"
                    for a in (ident.get("affiliations") or [])) or "your employers"
    rows = [(lab, pid, val, why) for pid, lab, val, why in (
        ("P735", "given name", given,
         "lets a query match the name parts separately from the label string"),
        ("P734", "family name", family, "same"),
        ("P69", "educated at", edu,
         "the single strongest disambiguating fact about a researcher"),
        ("P108", "employer", emp, "turns a name into a career an engine can order"),
    ) if not have.get(pid)]
    if rows:
        L += ["## Worth adding while you are in the editor", "",
              "Not identifiers — statements that help a disambiguator separate you",
              "from a namesake, which is the whole job of this item. Only what the",
              "item does not carry yet is listed.", "",
              "| property | | value | why |", "|---|---|---|---|"]
        L += [f"| {lab} | `{pid}` | {val} | {why} |" for lab, pid, val, why in rows]
        L += ["",
              "`educated at` is for degree-granting study only. A postdoc goes in "
              "`employer`",
              "(`P108`), optionally qualified with *position held* (`P39`) = `Q1125292`",
              "(postdoctoral researcher) — no degree was awarded, and the institution",
              "was paying you. The test is just: was a degree awarded?", "",
              "Skip date of birth, sex or gender, and image. None of them help retrieval",
              "and all of them are personal data you would then be maintaining.", ""]

    dated = {norm_name(str(r.get("org") or "").replace("The ", "")): r
             for sect in ("employment_rows", "education_rows")
             for r in ((orc or {}).get(sect) or [])}
    mine = [lab for pid, _q, lab in g.get("unqualified") or []
            if (dated.get(norm_name(lab)) or {}).get("start")
            or (pid == "P69" and norm_name(lab) in dated)]
    yours = [(pid, q, lab) for pid, q, lab in g.get("unqualified") or []
             if lab not in mine]
    if mine:
        L += [f"## {plural(len(mine), 'qualifier')} a run will add", "",
              "`P108` with no *start time* is a set of employers rather than a career,",
              "and `P69` with no *academic degree* does not say which degree. The ORCID",
              "record states both, so nothing here is yours:", "",
              "```", "python scripts/wikidata_apply.py --apply", "```", ""]
        L += [textwrap.fill("It qualifies " + ", ".join(sorted(mine)) + ".", 78), ""]
    empl = [(q, lab) for pid, q, lab in yours if pid == "P108"]
    if empl:
        L += ["## Employers only you can date", "",
              "These carry no *start time* and the ORCID record has no employment row to",
              "take one from, so the year is the one fact no public source settles.", "",
              "Adding the employment to <https://orcid.org/my-orcid#employment> instead",
              "leaves the qualifier to `python scripts/wikidata_apply.py --apply`, and",
              "every service that reads ORCID gets the affiliation too.", "",
              f"On <https://www.wikidata.org/wiki/{g['qid']}#P108>, click the statement,",
              "*add qualifier* → *start time* → the year:", ""]
        L += [f"- [ ] **{lab}** (`{q}`)" for q, lab in empl] + [""]
    return L


def wikidata_followup_file(g: dict, cfg, cov: dict, qs_path: str | None,
                           orc: dict | None = None) -> str:
    """What is left to do on an item that already exists.

    Separate from wikidata_manual.md, which is about creating one. Once the item is
    there the remaining work is different in kind -- corrections, typed identifiers,
    and linking papers to it -- and mixing the two makes the creation guide look
    unfinished forever.
    """
    ident = cfg["identity"]
    q = g["qid"]
    # P735/P734 want the parts, not the label. Split on the last space: `Leshem Choshen`
    # -> given `Leshem`, family `Choshen`. Naive for compound surnames (`de Oc{\'a}riz
    # Borde`) and for the order some cultures write, which is exactly why the value goes
    # into a table a human reads and confirms rather than into an automated write.
    given, _, family = ident["name"].rpartition(" ")
    given, family = given or ident["name"], family or ""
    L = [f"# Wikidata follow-up — [{q}](https://www.wikidata.org/wiki/{q})", "",
         f"Label **{g['label']}** · description *{g['description']}*", "",
         "Live diff against `config.yaml`. Re-run `python scripts/audit_identity.py`",
         "after editing to confirm each line cleared.", ""]

    if g["bad_aliases"]:
        L += ["## Fix first: an alias was stored as one string", "",
              "Wikidata holds this as a single *also known as* value:", ""]
        # Shown in a fenced block, not backticks: the value *contains* backticks, so
        # inline code would break exactly in the paragraph explaining the breakage.
        L += ["```"] + list(g["bad_aliases"]) + ["```"]
        # The example is the stored variant that actually looks like a citation, not a
        # literal: a forked config has different names in it.
        cited = next((v for v in ident["name_variants"] if "," in v),
                     f"{family}, {given}")
        L += ["", "That is one alias whose text happens to contain backticks and a comma,",
              f"not two aliases — so a citation reading *{cited}* matches nothing.",
              "The aliases box takes one name per entry.", "",
              f"On <https://www.wikidata.org/wiki/{q}>: click the *also known as* area,",
              "delete that entry, then add each of these as its own alias:", ""]
        L += [f"- [ ] `{v}`" for v in (list(ident["name_variants"])
                                      + list(ident.get("name_typos") or []))
              if v != ident["name"]]
        L += [""]
    elif g["want_aliases"]:
        typos = set(ident.get("name_typos") or [])
        L += ["## Aliases to add", "",
              "*Also known as* is what matches a citation that uses a different form.",
              "Misspellings included, and marked as such below: an alias is a search key",
              "rather than a claim about spelling, so the one form that can never be",
              "fixed at its source — a typo already printed in someone else's reference",
              "list — is exactly the one worth carrying here.", ""]
        L += [f"- [ ] `{v}`" + ("  *(misspelling; deliberate)*" if v in typos else "")
              for v in g["want_aliases"]] + [""]

    if g["dupes"]:
        L += ["## Duplicate statements to remove", "",
              "The editor does not warn when the same value is added twice, and the item",
              "page renders the two identically, so this is only visible from the API.", ""]
        for pid, val, n in g["dupes"]:
            L.append(f"- [ ] `{pid}` = `{val}` appears {n}× — delete all but one "
                     f"(<https://www.wikidata.org/wiki/{q}#{pid}>)")
        L.append("")

    if g["n_p856"] > 1:
        L += ["## More than one official website", "",
              f"`P856` has {g['n_p856']} values. It should have exactly one, the canonical",
              f"URL (`{ident['canonical_url']}`). A second URL here is a second candidate",
              "homepage, which is the thing the canonical URL exists to prevent. Other",
              "pages belong in `described at URL` (P973) or in their own identifier",
              "property — see the table below.", ""]

    if g["missing"] or g["wrong"]:
        L += ["## Identifiers to add", "",
              "Each of these has a *typed* property, which is why none of them belong in",
              "`official website`. A typed identifier is format-validated, renders as a",
              "link anyway, and is traversable: Scholia, Author Disambiguator and any",
              "SPARQL query can hop from it to the record. A bare URL is none of those.",
              "", "Add with *+ Add statement* → type the property name → paste the value.",
              ""]
        for pid, label, want in g["missing"]:
            L.append(f"- [ ] **{label}** (`{pid}`) = `{want}`")
        for pid, label, want, have in g["wrong"]:
            L.append(f"- [ ] **{label}** (`{pid}`) reads `{', '.join(have)}` — "
                     f"expected `{want}`")
        L.append("")
        if any(pid == "P2456" for pid, *_ in g["wrong"]):
            L += ["`P2456` is the reason for the warning triangle on the item. It takes",
                  "DBLP's *pid* — the numeric path in `dblp.org/pid/218/5237` — not the",
                  "name-shaped URL DBLP also answers on. Wikidata builds the link by",
                  "substituting the value into `dblp.org/pid/$1`, so a name value both",
                  "trips the format constraint and produces a 404. Constraint violations",
                  "do not block saving, which is why it saved and then complained.", "",
                  "*0 references* on that statement is not the warning and is not a",
                  "problem: external identifiers are normally unsourced, since the",
                  "identifier resolving is the source. Ignore it.", ""]
    if not cfg["ids"].get("openreview"):
        L += ["- [ ] **OpenReview.net profile ID** (`P8964`) — fill "
              "`ids.openreview` in `config.yaml` first. Open your OpenReview profile "
              "and copy the `~Name1` from the URL; it is left blank rather than guessed "
              "because a duplicate profile would make the guess wrong, and a wrong "
              "identifier is worse than a missing one.", ""]

    L += disambiguating_statements(g, ident, given, family, orc)

    L += paper_link_section(q, cov, qs_path)
    return _write_followup(L)


def paper_link_section(q: str, cov: dict, qs_path: str | None) -> list[str]:
    """The papers half of the follow-up, written from the measurement.

    Kept separate because it is the section that was wrong. It used to open with
    "dozens of your papers already exist as Wikidata items, imported from Crossref"
    -- received wisdom, never checked, and false here. Whether the job is relinking
    strings or creating items depends entirely on a number, so the section now reads
    that number rather than asserting one.
    """
    if not cov:
        return ["## Then: link your papers to the item", "",
                "Coverage not measured — the scholarly query endpoint did not answer on",
                "this run. Re-run the audit; the number below decides what the work is.",
                ""]
    n_have, n_tot = len(cov["present"]), cov["total"]
    L = ["## Then: your papers", "",
         f"**Measured this run: {n_have} of {n_tot} have a Wikidata item.**",
         f"(Matched on DOI and arXiv id across {cov['checked']} papers that carry one",
         "— exact keys, so this is coverage and not a name-search guess.)", ""]
    if cov.get("unchecked"):
        u = len(cov["unchecked"])
        L += [f"The endpoint would not answer about {plural(u, 'more paper')} on this run, so "
              f"{'it is' if u == 1 else 'they are'} neither counted above nor queued for "
              "creation. Retried next run.", ""]
    for p, qid in cov["present"]:
        L.append(f"- [{qid}](https://www.wikidata.org/wiki/{qid}) — "
                 f"{clipped(p.get('title_display') or p['title'], 70)}")
    L += ["",
          "Two facts follow from that number, and both cut against the usual advice.",
          "",
          "**Author Disambiguator is nearly empty for you.** Its job is to convert an",
          f"`author name string` (P2093) into `author` (P50) pointing at {q}. That only",
          "works on items that already exist, so it can reach at most those listed",
          "above. It is worth one pass — <https://author-disambiguator.toolforge.org>,",
          f"log in, paste `{q}` into *Author details*, tick rows whose **co-author list**",
          "matches (the title is the weaker tell against a namesake), submit. Repeat per",
          "name variant; it searches one string at a time. Do not press *create missing",
          "author item* while your item exists — that is how duplicate author items",
          "appear.", "",
          # Phrased so it cannot go stale. It used to read "the autoconfirmed threshold
          # *was going to* be paid for by this step", which asserted a live state this
          # generator cannot see: the account name lives in an env var or a gitignored
          # file, so a run has no way to know whether the 50 are still owed -- and the
          # paragraph went on describing a wait that had been over for days.
          "**It will not get you to 50 edits.** Worth saying because the autoconfirmed",
          "threshold QuickStatements needs — 4 days old and 50 edits — looks like",
          "something this step would pay for, and with a handful of linkable items it",
          "cannot. Whether you still owe them is one command rather than an assumption:",
          "`python scripts/wikidata_apply.py --check-account`. If you do, either make the",
          "50 elsewhere or skip QuickStatements and edit by hand — the item's own",
          "statements are a 15-minute job either way.", ""]
    if qs_path:
        n_new = sum(1 for x in open(qs_path) if x.strip() == "CREATE")
        L += ["**Creating the missing items — read this first, then run it in batches.**",
              "",
              f"{n_new} papers have no Wikidata item. Each would get its title,",
              f"publication date, DOI or arXiv id, and the author list with you as",
              f"`author` → {q} and co-authors as `author name string` with position",
              "qualifiers. Only papers carrying a DOI or arXiv id are included — a",
              "resolvable identifier is what puts a publication item clearly in scope,",
              "and it is the key coverage was measured on.", "",
              "```bash",
              "python scripts/wikidata_apply.py --papers              # what it would create",
              "python scripts/wikidata_apply.py --papers --apply --limit 10",
              "```", "",
              "No autoconfirmed account and no browser tool: this is the same bot password",
              "the author item uses. Each item is one atomic `wbeditentity`, recorded in",
              "`data/wikidata_created.yaml` before the next one starts — so an interrupted",
              "run resumes where it stopped, and a re-run in the hours before the query",
              "service catches up does not create everything twice.",
              f"`{os.path.relpath(qs_path, ROOT)}` holds the same statements as a",
              "QuickStatements batch, kept as the fallback if the bot password is ever",
              "revoked.", "",
              "Honest accounting before you run it: this buys a Scholia profile, a",
              "SPARQL-answerable corpus, and an authorship graph — real, but a weaker",
              "surface than arXiv, ORCID or your own pages. It costs permanent public",
              "items on somebody else's wiki, which are much harder to clean up than a",
              "page in this repo: undoing a statement is one click, undoing an item is a",
              "deletion request a volunteer has to action. Which is the whole argument for",
              "`--limit 10` — open two of the first ten on the wiki before continuing.", "",
              "One gap the dedup cannot cover: a paper item that exists with neither a",
              "DOI nor an arXiv id would not have matched, so it could be recreated.",
              "Searching the exact title in Wikidata's own search box is the check.", ""]
    return L


def _write_followup(L: list[str]) -> str:
    """Kept as its own function only so the two halves above can each end in a return."""

    path = os.path.join(TASKS, "wikidata_followup.md")
    write_task(path, L)
    return path
