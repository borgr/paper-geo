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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA, ROOT, load_config, read_yaml  # noqa: E402

TASKS = os.path.join(ROOT, "tasks")

# Verified against wbsearchentities.
P = {"instance_of": "P31", "occupation": "P106", "employer": "P108",
     "orcid": "P496", "website": "P856", "google_scholar": "P1960",
     "semantic_scholar": "P4012", "openalex": "P10283", "github": "P2037",
     "dblp": "P2456", "field_of_work": "P101"}
Q = {"human": "Q5", "researcher": "Q1650915", "computer_scientist": "Q82594",
     "MIT": "Q49108", "IBM Research": "Q3146518",
     "Weizmann Institute of Science": "Q4182",
     "natural language processing": "Q30642", "machine learning": "Q2539"}
EMPLOYER_Q = {"MIT-IBM Watson AI Lab": Q["MIT"], "IBM Research": Q["IBM Research"],
              "Weizmann Institute of Science": Q["Weizmann Institute of Science"]}


def orcid_files(cfg, papers) -> tuple[str, str, int]:
    """BibTeX + DOI list for populating ORCID.

    Order matters and the docs are easy to misread: auto-update only covers works
    whose *deposited metadata already contains your iD*, so it fixes the future,
    not the backlog. Search & Link fills the backlog from the registries. A BibTeX
    import is the last resort, because works sourced from you personally are lower
    trust than Crossref/DataCite-sourced ones and can duplicate what auto-update
    later adds. Hence: auto-update first, wizards second, this file third.
    """
    # ORCID groups works that share an identifier, so a BibTeX entry carrying a
    # DOI merges with the Crossref-sourced version when auto-update later finds it,
    # rather than showing as a duplicate. Entries WITHOUT a DOI have nothing to
    # group on, so those are the only genuinely risky ones -- sorted last, and
    # counted separately so you can stop before them.
    with_doi = [p for p in papers if p.get("bibtex") and p.get("doi")]
    without = [p for p in papers if p.get("bibtex") and not p.get("doi")]
    with_doi.sort(key=lambda p: -(p.get("citations") or 0))
    without.sort(key=lambda p: -(p.get("citations") or 0))
    entries = ([f"% ---- {len(with_doi)} entries WITH a DOI: safe to import, ORCID "
                f"groups them with the registry copy by identifier ----"]
               + [p["bibtex"] for p in with_doi]
               + [f"% ---- {len(without)} entries WITHOUT a DOI: nothing for ORCID to "
                  f"group on, so these can show as standalone duplicates later ----"]
               + [p["bibtex"] for p in without])
    bib = os.path.join(TASKS, "orcid_import.bib")
    with open(bib, "w") as f:
        f.write("\n\n".join(e.strip() for e in entries) + "\n")

    dois, seen = [], set()
    for p in sorted(papers, key=lambda p: -(p.get("citations") or 0)):
        d = (p.get("doi") or "").strip()
        if d and d.lower() not in seen:
            seen.add(d.lower())
            dois.append(f"{d}\t{p.get('title_display') or p['title']}")
    doi_path = os.path.join(TASKS, "orcid_dois.txt")
    with open(doi_path, "w") as f:
        f.write("\n".join(dois) + "\n")
    return bib, doi_path, len(entries)


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
    add(P["google_scholar"], f'"{ids["google_scholar"]}"')
    add(P["semantic_scholar"], f'"{ids["semantic_scholar_primary"]}"')
    add(P["openalex"], f'"{ids["openalex"][0].rsplit("/", 1)[-1]}"')
    add(P["github"], f'"{ids["github"]}"')
    add(P["dblp"], f'"{ids["dblp"].replace(" ", "_")}"')
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
    rows += [("Google Scholar author ID", "P1960", ids["google_scholar"], ""),
             ("Semantic Scholar author ID", "P4012", ids["semantic_scholar_primary"], ""),
             ("OpenAlex ID", "P10283", ids["openalex"][0].rsplit("/", 1)[-1], ""),
             ("GitHub username", "P2037", ids["github"], ""),
             ("DBLP author ID", "P2456", ids["dblp"].replace(" ", "_"), "")]
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
         "- **Aliases:** " + ", ".join(f"`{a}`" for a in aliases),
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
          "validates the format and will refuse a malformed one, which is a useful check",
          "that the id in `config.yaml` is right.", "",
          "## 4. Record the result", "",
          "Copy the new Q-number from the URL into `config.yaml` → `ids.wikidata`, then",
          "`python scripts/build_site.py --deploy`. It lands in the site's `sameAs` array,",
          "which is what lets an engine fuse the Wikidata item with your pages.", "",
          "## 5. Worth ten more minutes: link your existing paper items", "",
          "Some of your papers already exist as Wikidata items, imported from Crossref,",
          "carrying your name as *author name string* (`P2093`) — a bare string, not a",
          "link. Replacing those with *author* (`P50`) pointing at your new item is what",
          "turns the item from an isolated record into a hub that resolves.", "",
          "The tool for this is Author Disambiguator:",
          "<https://author-disambiguator.toolforge.org> — search your name, it lists every",
          "paper item with a matching name string and reassigns them in bulk.", "",
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
    print("wrote:")
    print(f"  {bib}   ({n} entries, for ORCID's BibTeX importer)")
    print(f"  {dois}   (DOI list, for the Add DOI path -- the reliable one)")
    print(f"  {manual}   (create the Wikidata item by hand -- START HERE)")
    print(f"  {qs}   (same item as a QuickStatements batch; needs an autoconfirmed account)")
    print(f"  {s2}   ({n_strays} papers to pull onto the claimed S2 page)")
    print(f"  {oa}")
    print("\nFor the live state of ORCID, arXiv, Wikidata and Hugging Face:")
    print("  python scripts/audit_identity.py")


if __name__ == "__main__":
    main()
