#!/usr/bin/env python3
"""Turn the four identity fixes into artifacts you can paste or upload.

Each of these is blocked on an authenticated account, not on knowing what to do.
So this generates the exact payload and prints the exact clicks:

    tasks/orcid_import.bib   BibTeX for ORCID's "Add works" importer
    tasks/orcid_dois.txt     the DOI list, for the Add DOI path
    tasks/wikidata.qs        QuickStatements to create the author item
    tasks/s2_merge.md        the papers to pull onto the claimed S2 page
    tasks/openalex_merge.md  what to put in the OpenAlex correction form

These go in tasks/ rather than build/ on purpose: they are worklists a human reads
and works through over days, so they need to be committed, browsable on GitHub, and
diffable between runs. build/ is gitignored scratch.

Property and item IDs below were looked up against Wikidata, not recalled.

Usage:
    python scripts/identity_tasks.py
"""
from __future__ import annotations

import os
import re
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (DATA, ROOT, WD_IDENTIFIERS, load_config, paper_doi,  # noqa: E402
                    read_yaml)

TASKS = os.path.join(ROOT, "tasks")

# Verified against wbsearchentities.
P = {"instance_of": "P31", "occupation": "P106", "employer": "P108",
     "orcid": "P496", "website": "P856", "google_scholar": "P1960",
     "semantic_scholar": "P4012", "openalex": "P10283", "github": "P2037",
     "dblp": "P2456", "field_of_work": "P101"}
P.update({"educated_at": "P69", "academic_degree": "P512", "position_held": "P39"})
Q = {"human": "Q5", "researcher": "Q1650915", "computer_scientist": "Q82594",
     "MIT": "Q49108", "IBM Research": "Q3146518",
     "MIT-IBM Watson AI Lab": "Q117720866",
     "Weizmann Institute of Science": "Q4182",
     "Hebrew University of Jerusalem": "Q174158",
     "postdoctoral researcher": "Q1125292", "PhD": "Q752297",
     "natural language processing": "Q30642", "machine learning": "Q2539"}
# The lab has its own item, so use it rather than its parent university. A P108 of
# `Massachusetts Institute of Technology` is not wrong, but it is a coarser claim than
# the one you can make, and it merges you into a 10,000-person institution on exactly
# the query -- "who works on this at that lab" -- where the finer item is the answer.
EMPLOYER_Q = {"MIT-IBM Watson AI Lab": Q["MIT-IBM Watson AI Lab"],
              "IBM Research": Q["IBM Research"],
              "Weizmann Institute of Science": Q["Weizmann Institute of Science"]}
# Institutions we can resolve for `educated at`. Unlisted ones are emitted with a
# blank Q-number for you to autocomplete, rather than guessed -- a wrong institution
# on P69 is a false claim about a degree.
SCHOOL_Q = {"Hebrew University of Jerusalem": Q["Hebrew University of Jerusalem"]}
DEGREE_Q = {"PhD": Q["PhD"]}


_HAS_DOI = re.compile(r"(?im)^\s*doi\s*=")
_ENTRY_HEAD = re.compile(r"^(\s*@\w+\s*\{[^,]*,)")


def _with_doi_field(entry: str, doi: str) -> str:
    """Insert `doi = {...}` into a BibTeX entry that lacks one.

    This is the difference between a safe bulk import and a duplicating one, and it
    is invisible from the metadata: 40 of these entries had a DOI in *our* record and
    no `doi` field in the *entry text*, so the earlier version of this file labelled
    them "safe to import, groups by identifier" while handing ORCID nothing to group
    on. ORCID reads the entry, not our YAML.
    """
    if not doi or _HAS_DOI.search(entry):
        return entry
    m = _ENTRY_HEAD.match(entry)
    if not m:
        return entry
    return entry[:m.end()] + f'\n  doi          = {{{doi}}},' + entry[m.end():]


def orcid_files(cfg, papers) -> tuple[str, str, int]:
    """BibTeX + DOI list for populating ORCID.

    The BibTeX file is the *primary* route, not the fallback it was written as: it is
    one upload for the whole backlog against one form submission per paper. The usual
    warning against it -- that self-asserted works are lower trust and duplicate what
    auto-update later adds -- only bites for entries with no identifier, because ORCID
    groups works that share one. So the fix is to make sure every entry carries a DOI
    (see _with_doi_field), after which the objection mostly evaporates.

    Auto-update still comes first in time, but it only covers works whose *deposited
    metadata already contains your iD* -- it fixes the future, not the backlog.
    """
    have = [p for p in papers if p.get("bibtex")]
    # Emit the DOI-bearing entries first and count them from the *emitted text*, so
    # the header cannot claim a grouping guarantee the file does not deliver.
    prepared = [(p, _with_doi_field(p["bibtex"].strip(), paper_doi(p) or "")) for p in have]
    prepared.sort(key=lambda t: -(t[0].get("citations") or 0))
    with_doi = [t for t in prepared if _HAS_DOI.search(t[1])]
    without = [t for t in prepared if not _HAS_DOI.search(t[1])]
    entries = ([f"% ---- {len(with_doi)} entries WITH a DOI: safe to import in one go. "
                f"ORCID groups works by identifier, so each merges with the "
                f"Crossref/DataCite copy rather than duplicating it. ----",
                "% Missing DOIs were filled from arXiv (10.48550/arXiv.<id>), which "
                "arXiv registers for every paper."]
               + [t[1] for t in with_doi]
               + [f"% ---- {len(without)} entries WITHOUT any DOI: no identifier to "
                  f"group on, so these are the only ones that can show as standalone "
                  f"duplicates later. Import them last, or not at all. ----"]
               + [t[1] for t in without])
    bib = os.path.join(TASKS, "orcid_import.bib")
    with open(bib, "w") as f:
        f.write("\n\n".join(entries) + "\n")

    dois, seen = [], set()
    for p in sorted(papers, key=lambda p: -(p.get("citations") or 0)):
        d = (paper_doi(p) or "").strip()
        if d and d.lower() not in seen:
            seen.add(d.lower())
            dois.append(f"{d}\t{p.get('title_display') or p['title']}")
    doi_path = os.path.join(TASKS, "orcid_dois.txt")
    with open(doi_path, "w") as f:
        f.write("# The bulk route is orcid_import.bib -- one upload instead of this\n"
                "# list one form at a time. Keep this for spot-fixing single works.\n"
                + "\n".join(dois) + "\n")
    return bib, doi_path, len(with_doi) + len(without)


def wikidata_qs(cfg, papers) -> str:
    """QuickStatements v1 commands to create the author item.

    Deliberately minimal: identity plus external identifiers. No claims about
    importance, no unsourced biography -- the item exists to be a stable anchor
    that other statements can point at, which is what Wikidata's structural-need
    criterion covers.

    NOTE: QuickStatements requires an *autoconfirmed* Wikidata account (4 days old,
    50 edits), so this file is unusable from a fresh account and the error message
    does not explain why. wikidata_manual() below is the route that works on day
    one; this stays for later runs and for anyone who already edits Wikidata.
    """
    ident, ids = cfg["identity"], cfg["ids"]
    L = ["CREATE"]
    def add(prop, val):
        L.append(f"LAST\t{prop}\t{val}")
    L.append(f'LAST\tLen\t"{ident["name"]}"')
    L.append('LAST\tDen\t"researcher in natural language processing"')
    for v in ident["name_variants"]:
        if v != ident["name"]:
            L.append(f'LAST\tAen\t"{v}"')
    add(P["instance_of"], Q["human"])
    add(P["occupation"], Q["researcher"])
    add(P["occupation"], Q["computer_scientist"])
    add(P["field_of_work"], Q["natural language processing"])
    add(P["field_of_work"], Q["machine learning"])
    add(P["orcid"], f'"{ident["orcid"]}"')
    add(P["website"], f'"{ident["canonical_url"]}"')
    for a in ident["affiliations"]:
        if a in EMPLOYER_Q:
            add(P["employer"], EMPLOYER_Q[a])
    # educated at, for degree-granting study only -- a postdoc is P108 above, since no
    # degree was awarded and the institution was the employer.
    for e in ident.get("education") or []:
        q = SCHOOL_Q.get(e.get("institution"))
        if not q:
            continue
        line = f"LAST\t{P['educated_at']}\t{q}"
        if DEGREE_Q.get(e.get("degree")):
            line += f"\t{P['academic_degree']}\t{DEGREE_Q[e['degree']]}"
        L.append(line)
    # Identifiers from the shared table rather than a second hand-kept list: this
    # file, the by-hand guide and the audit's completeness check all have to name the
    # same properties, and three copies is how one of them silently lags the others.
    for pid, _label, pick in WD_IDENTIFIERS:
        v = pick(cfg)
        if v and pid not in (P["orcid"], P["website"]):
            add(pid, f'"{str(v).rsplit("/", 1)[-1] if pid == P["openalex"] else v}"')
    path = os.path.join(TASKS, "wikidata.qs")
    with open(path, "w") as f:
        f.write("\n".join(L) + "\n")
    return path


def wikidata_manual(cfg) -> str:
    """The by-hand route, because QuickStatements is gated on autoconfirmed.

    QuickStatements requires an *autoconfirmed* Wikidata account: 4 days old and 50
    edits. A researcher creating an account for this has neither, so the .qs file is
    unusable on day one and the tool fails with an authorisation error rather than
    an explanation. Creating an item by hand has no such gate, so that is the
    primary route and the batch file is the shortcut for later.

    Statements are emitted as (label to type, value to type) because the Wikidata
    editor autocompletes on labels, not P/Q numbers -- the numbers are here only so
    you can confirm the autocomplete picked the right one.
    """
    ident, ids = cfg["identity"], cfg["ids"]
    rows = [("instance of", "P31", "human", "Q5"),
            ("occupation", "P106", "researcher", "Q1650915"),
            ("occupation", "P106", "computer scientist", "Q82594"),
            ("field of work", "P101", "natural language processing", "Q30642"),
            ("field of work", "P101", "machine learning", "Q2539"),
            ("ORCID iD", "P496", ident["orcid"], ""),
            ("official website", "P856", ident["canonical_url"], "")]
    for a in ident["affiliations"]:
        if a in EMPLOYER_Q:
            rows.append(("employer", "P108", a, EMPLOYER_Q[a]))
    for e in ident.get("education") or []:
        rows.append(("educated at", "P69", e.get("institution", ""),
                     SCHOOL_Q.get(e.get("institution"), "")))
        if e.get("degree"):
            rows.append(("  ↳ qualifier: academic degree", "P512", e["degree"],
                         DEGREE_Q.get(e["degree"], "")))
    for pid, label, pick in WD_IDENTIFIERS:
        v = pick(cfg)
        if v and pid not in (P["orcid"], P["website"]):
            rows.append((label, pid,
                         str(v).rsplit("/", 1)[-1] if pid == P["openalex"] else v, ""))
    aliases = [v for v in ident["name_variants"] if v != ident["name"]]

    L = ["# Wikidata: create the author item by hand", "",
         "**Do this instead of QuickStatements if your account is new.**",
         "QuickStatements requires an *autoconfirmed* account — 4 days old and 50 edits",
         "— and fails with an authorisation error rather than saying so. Creating an item",
         "through the normal editor has no such requirement. `wikidata.qs` stays in this",
         "directory for when the account qualifies, or for a second person's item.", "",
         "Fifteen minutes, once.", "",
         "## 1. Check it does not already exist", "",
         f"<https://www.wikidata.org/wiki/Special:Search?search=haswbstatement%3AP496%3D{ident['orcid']}>",
         "",
         "Empty result means no item claims your ORCID. Searching your *name* instead is",
         "misleading — it returns paper items that merely list you as an author string,",
         "which looks like a hit and is not one.", "",
         "## 2. Create the item", "",
         "<https://www.wikidata.org/wiki/Special:NewItem>", "",
         f"- **Label:** `{ident['name']}`",
         "- **Description:** `researcher in natural language processing`",
         "  (a description is what separates you from a namesake; it must not repeat the",
         "  label, and Wikidata rejects an item whose label+description pair already",
         "  exists)",
         # One per line and no backticks. Comma-joining them inside backticks is
         # exactly how the first attempt at this went wrong: the rendered string was
         # pasted whole into the single-alias box, producing one alias containing two
         # names and two stray backticks, which matches no citation at all.
         "- **Aliases** — add each as its own entry, not one comma-joined string:",
         *[f"    - {a}" for a in aliases],
         "",
         "## 3. Add these statements", "",
         "In the editor, click *+ Add statement*, type the **property name** — it",
         "autocompletes — then the value. The P/Q numbers are only to confirm the",
         "autocomplete resolved to the right thing.", "",
         "| property | | value | |", "|---|---|---|---|"]
    for label, p, val, q in rows:
        L.append(f"| {label} | `{p}` | {val} | {f'`{q}`' if q else ''} |")
    L += ["",
          "Identifier values (ORCID, the author IDs) are plain strings — Wikidata",
          "validates the format and **warns** on a malformed one rather than refusing it,",
          "so the statement saves and then sits there with a yellow triangle. Two that",
          "catch people, because the wrong value looks entirely reasonable:", "",
          "- **DBLP author ID** is the numeric pid (`218/5237`), *not* your name. The",
          "  property's formatter URL is `dblp.org/pid/$1`, so a name-shaped value builds",
          "  a link that 404s — which is what the constraint warning is telling you. Read",
          "  the number off your own dblp page's URL.",
          "- **Mastodon address** is `user@server`, with **no** leading `@`, even though",
          "  that is the form your own profile shows you.", "",
          "### Rows marked *qualifier*", "",
          "A qualifier is a statement *on* a statement, not a new one: add the parent row",
          "first, then click *+ add qualifier* underneath it. The academic-degree row",
          "belongs inside the `educated at` statement, so the item says \"PhD, from there\"",
          "rather than two disconnected facts.", "",
          "### educated at vs employer — the one people get wrong", "",
          "**A postdoc is employment, not education.** You were not enrolled, no degree",
          "was awarded, and the institution was paying you. It goes in `employer` (P108),",
          "optionally qualified with `position held` (P39) = *postdoctoral researcher*",
          "(`Q1125292`); putting it in `educated at` asserts a degree you do not hold. The",
          "test is just: was a degree awarded? PhD, MSc, BSc → P69. Postdoc, visiting",
          "researcher, internship, fellowship → P108.", "",
          "Both are worth having, for different reasons. P108 is what institutional",
          "disambiguation matches on, so it should agree with ORCID's *Employment* exactly.",
          "P69 is what connects you to older papers carrying a student affiliation, which",
          "is the period where a namesake is hardest to tell apart from you.", "",
          "## 4. Record the result", "",
          "Copy the new Q-number from the URL into `config.yaml` → `ids.wikidata`, then",
          "`python scripts/build_site.py --deploy`. It lands in the site's `sameAs` array,",
          "which is what lets an engine fuse the Wikidata item with your pages.", "",
          "## 5. Your paper items: measure first, because the standard advice may not apply",
          "",
          "The advice you will find everywhere is: your papers already exist as items",
          "auto-imported from Crossref, carrying your name as *author name string*",
          "(`P2093`) rather than a link, and <https://author-disambiguator.toolforge.org>",
          "reassigns them to *author* (`P50`) → your item in bulk. Where that holds it is",
          "the best ten minutes on this page — it turns an isolated item into a hub, and",
          "the edits carry you to autoconfirmed as a by-product.", "",
          "**Check whether it holds before planning around it.** `audit_identity.py` looks",
          "up every paper's DOI and reports how many are in Wikidata; the search below is",
          "the by-hand version of the other half — items with your name as a *string*.", "",
          f"<https://www.wikidata.org/wiki/Special:Search?search={urllib.parse.quote('haswbstatement:P2093=' + ident['name'])}>",
          "",
          "Wikidata's coverage of CS literature is **sporadic rather than a pipeline**: the",
          "systematic Crossref imports ran years ago, publisher DOIs fare far better than",
          "arXiv DataCite ones, and a recent item is as likely to be one interested human's",
          "work as a bot's. A corpus that is mostly preprints and ACL Anthology papers can",
          "sit in the single digits — and then there is nothing for Author Disambiguator to",
          "reassign, no `P2093` strings to upgrade, and no free route to 50 edits.", "",
          "**If the count is low, that is a decision point, not a failure.** Creating items",
          "for your own papers is ~2 minutes each and it is the only remaining path to",
          "autoconfirmed. Worth it if you want a queryable graph of the corpus; not worth it",
          "merely to unlock QuickStatements, since everything on *this* page is 15 minutes",
          "by hand and that is where the identity gain is. Either way, link the items that",
          "*do* exist: open each, and on its `author name string` statement for you, replace",
          "it with `author` → your Q-number.", "",
          "## Is this legitimate?", "",
          "Yes, and it is worth knowing why so you are not uneasy about it. Wikidata's",
          "notability policy is not Wikipedia's: criterion 2 admits any *clearly",
          "identifiable entity that can be described using serious and publicly available",
          "references*, and criterion 3 admits items that *fulfil a structural need*. An",
          "author item with an ORCID and published papers is squarely both — and hundreds",
          "of thousands exist already, mostly auto-created from ORCID and Crossref.",
          "Unlike Wikipedia there is no prohibition on creating an item about yourself.",
          "The requirement is accuracy, not distance, which is why the statements above",
          "are identifiers and affiliations only: nothing about importance, nothing",
          "unsourced, nothing a reader could not verify."]
    path = os.path.join(TASKS, "wikidata_manual.md")
    with open(path, "w") as f:
        f.write("\n".join(L) + "\n")
    return path


def s2_merge(cfg, papers) -> tuple[str, int]:
    """The papers sitting on the secondary S2 record.

    There is no self-service merge, but a claimed page has an "Add Papers" tool --
    so the split is fixable without support by pulling each paper across. That is
    the path this file supports, because support has already been asked once.
    """
    ids = cfg["ids"]
    primary = ids["semantic_scholar_primary"]
    others = [a for a in ids["semantic_scholar"] if a != primary]
    strays = sorted([p for p in papers if p.get("s2_author_record") in others],
                    key=lambda p: -(p.get("citations") or 0))
    path = os.path.join(TASKS, "s2_merge.md")
    L = [f"# Semantic Scholar: pull {len(strays)} papers onto the claimed page", "",
         f"Claimed (primary): https://www.semanticscholar.org/author/{primary}",
         *[f"Secondary:         https://www.semanticscholar.org/author/{o}" for o in others],
         "",
         "Support has already been asked to merge and did not. The self-service route",
         "is the claimed page's own editor, which can pull papers across one at a time:",
         "",
         "1. Open your claimed author page and choose **Edit Author Page → Add Papers**.",
         "2. For each paper below, paste its Semantic Scholar URL, pick it, and select",
         "   *the author is correct, but the paper is missing from my author page*.",
         "3. Submit. Changes appear in roughly 24 hours.",
         "",
         "Highest-citation first, so stopping early still helps most.", "",
         "| citations | paper | S2 |", "|---|---|---|"]
    for p in strays:
        s2 = (f"https://www.semanticscholar.org/paper/{p['s2_corpus_id']}"
              if p.get("s2_corpus_id") else "—")
        title = (p.get("title_display") or p["title"]).replace("|", "/")
        L.append(f"| {p.get('citations') or 0} | {title[:70]} | {s2} |")
    L += ["", "## Why bother",
          "Every Semantic-Scholar-backed tool -- Elicit, Consensus, SciSpace, and most",
          "literature agents -- resolves an author to one page. A split profile means",
          "each of them sees roughly half your corpus and ranks both halves lower.",
          "", "## The durable fix",
          "Populate ORCID. S2's disambiguation uses it, so an ORCID with all works",
          "attached reduces the chance the split reappears after future re-clustering."]
    with open(path, "w") as f:
        f.write("\n".join(L) + "\n")
    return path, len(strays)


def openalex_merge(cfg) -> str:
    ids = cfg["ids"]
    keep = ids["openalex"][0].rsplit("/", 1)[-1]
    dups = [d.rsplit("/", 1)[-1] for d in ids.get("openalex_duplicates") or []]
    path = os.path.join(TASKS, "openalex_merge.md")
    L = ["# OpenAlex: merge duplicate author profiles", "",
         f"Keep: https://openalex.org/{keep}",
         *[f"Merge in: https://openalex.org/{d}" for d in dups], "",
         "## Route 1 — let ORCID do it (preferred, no form)",
         "",
         "OpenAlex's disambiguation is ORCID-driven, and they are actively running",
         "ORCID-based merges of split profiles. Populating ORCID is therefore likely",
         "to fix this without a request, and fixes it durably rather than once.",
         "",
         "## Route 2 — the curation form",
         "",
         "OpenAlex publishes Google Forms for curation requests, linked from",
         "<https://help.openalex.org/hc/en-us/articles/27714298573719-Fix-errors-in-OpenAlex>",
         "(*Fixing Author Profiles*). That form can merge multiple author profiles",
         "into one, set the preferred display name, and remove wrongly-attached works.",
         "Include:", "",
         f"- the profile to keep: `https://openalex.org/{keep}`",
         "- the profiles to merge in: " + (", ".join(f"`{d}`" for d in dups) or "—"),
         f"- your ORCID: `{cfg['identity']['orcid']}`",
         f"- the display name to keep: `{cfg['identity']['name']}`", "",
         "`support@openalex.org` is the fallback if the form does not cover a case.",
         "", "## Scale check",
         "The duplicates hold a handful of works between them against 140+ on the main",
         "profile, so this is tidying, not a broken profile. Do it after ORCID and the",
         "Semantic Scholar merge."]
    with open(path, "w") as f:
        f.write("\n".join(L) + "\n")
    return path


def main() -> None:
    cfg = load_config()
    papers = (read_yaml(os.path.join(DATA, "papers.yaml")) or {})["papers"]
    os.makedirs(TASKS, exist_ok=True)
    bib, dois, n = orcid_files(cfg, papers)
    qs = wikidata_qs(cfg, papers)
    manual = wikidata_manual(cfg)
    s2, n_strays = s2_merge(cfg, papers)
    oa = openalex_merge(cfg)
    # Once the item exists, pointing at the creation guide is worse than not
    # mentioning it: the reader has to work out that the file no longer applies.
    made = cfg["ids"].get("wikidata")
    print("wrote:")
    print(f"  {bib}   ({n} entries -- ONE upload: Works + Add > Add BibTeX)")
    print(f"  {dois}   (same works one at a time, for spot-fixing)")
    if made:
        print(f"  {manual}   (already done -- item is {made}; what is left is in "
              f"tasks/wikidata_followup.md)")
    else:
        print(f"  {manual}   (create the Wikidata item by hand -- START HERE)")
    print(f"  {qs}   (same item as a QuickStatements batch; needs an autoconfirmed account)")
    print(f"  {s2}   ({n_strays} papers to pull onto the claimed S2 page)")
    print(f"  {oa}")
    print("\nFor the live state of ORCID, arXiv, Wikidata and Hugging Face:")
    print("  python scripts/audit_identity.py")


if __name__ == "__main__":
    main()
