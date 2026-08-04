#!/usr/bin/env python3
"""Turn the four identity fixes into artifacts you can paste or upload.

Each of these is blocked on an authenticated account, not on knowing what to do.
So this generates the exact payload and prints the exact clicks:

    build/orcid_import.bib   BibTeX for ORCID's "Add works" importer
    build/orcid_dois.txt     the DOI list, for the wizard/DOI-lookup path
    build/wikidata.qs        QuickStatements to create the author item
    build/s2_merge.md        the papers to pull onto the claimed S2 page
    build/openalex_merge.md  what to put in the OpenAlex correction form

Property and item IDs below were looked up against Wikidata, not recalled.

Usage:
    python scripts/identity_tasks.py
"""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import BUILD, DATA, load_config, read_yaml  # noqa: E402

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
    entries = [p["bibtex"] for p in papers if p.get("bibtex")]
    bib = os.path.join(BUILD, "orcid_import.bib")
    with open(bib, "w") as f:
        f.write("\n\n".join(e.strip() for e in entries) + "\n")

    dois, seen = [], set()
    for p in sorted(papers, key=lambda p: -(p.get("citations") or 0)):
        d = (p.get("doi") or "").strip()
        if d and d.lower() not in seen:
            seen.add(d.lower())
            dois.append(f"{d}\t{p.get('title_display') or p['title']}")
    doi_path = os.path.join(BUILD, "orcid_dois.txt")
    with open(doi_path, "w") as f:
        f.write("\n".join(dois) + "\n")
    return bib, doi_path, len(entries)


def wikidata_qs(cfg, papers) -> str:
    """QuickStatements v1 commands to create the author item.

    Deliberately minimal: identity plus external identifiers. No claims about
    importance, no unsourced biography -- the item exists to be a stable anchor
    that other statements can point at, which is what Wikidata's structural-need
    criterion covers.
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
    path = os.path.join(BUILD, "wikidata.qs")
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
    path = os.path.join(BUILD, "s2_merge.md")
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
    path = os.path.join(BUILD, "openalex_merge.md")
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
    os.makedirs(BUILD, exist_ok=True)
    bib, dois, n = orcid_files(cfg, papers)
    qs = wikidata_qs(cfg, papers)
    s2, n_strays = s2_merge(cfg, papers)
    oa = openalex_merge(cfg)
    print("wrote:")
    print(f"  {bib}   ({n} entries, for ORCID's BibTeX importer -- last resort)")
    print(f"  {dois}   (DOI list, for the Search & Link / DOI-lookup path)")
    print(f"  {qs}   (paste into QuickStatements while logged in to Wikidata)")
    print(f"  {s2}   ({n_strays} papers to pull onto the claimed S2 page)")
    print(f"  {oa}")


if __name__ == "__main__":
    main()
