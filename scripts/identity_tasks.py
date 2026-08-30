#!/usr/bin/env python3
"""Turn the identity fixes into artifacts you can paste or upload.

Each of these is blocked on an authenticated account, not on knowing what to do.
So this generates the exact payload and prints the exact clicks:

    tasks/orcid_import.bib   BibTeX for ORCID's "Add works" importer
    tasks/orcid_dois.txt     the DOI list, for the Add DOI path
    tasks/wikidata.qs        QuickStatements to create the author item
    tasks/s2_merge.md        the papers to pull onto the claimed S2 page
    tasks/openalex_merge.md  what to put in the OpenAlex correction form
    tasks/arxiv_jref.md      the journal-ref and DOI to add to each arXiv listing

These go in tasks/ rather than build/ on purpose: they are worklists a human reads
and works through over days, so they need to be committed, browsable on GitHub, and
diffable between runs. build/ is gitignored scratch.

Property and item IDs below were looked up against Wikidata, not recalled.

Usage:
    python scripts/identity_tasks.py
    python scripts/identity_tasks.py --user-page ~/Downloads/arxiv-user.html
"""
from __future__ import annotations

import argparse
import datetime
import os
import re
import sys
import urllib.parse
from html.parser import HTMLParser

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (DATA, TASKS, WD_IDENTIFIERS, clean_latex, is_preprint_venue,  # noqa: E402
                    load_config, org_name, paper_doi, parse_bibtex, read_papers, read_yaml,
                    synth_bibtex, title_of, write_task)

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


def employer_q(a) -> str:
    """The Q-number for one `identity.affiliations` entry, or "" to leave blank.

    An affiliation carrying its own `wikidata` wins over this file's table -- two places
    holding the same QID is how one of them silently lags. The table is the fallback for a
    bare-name entry, and for a config that has not been upgraded.

    Returning "" rather than guessing, as with `SCHOOL_Q`: an unresolved employer is a row you
    autocomplete by hand, while a wrong one asserts he works somewhere he does not.
    """
    if isinstance(a, dict) and a.get("wikidata"):
        return str(a["wikidata"])
    return EMPLOYER_Q.get(org_name(a), "")
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

    The BibTeX file is the primary route: one upload for the whole backlog against one form
    submission per paper. The usual warning against it -- self-asserted works are lower trust
    and duplicate what auto-update later adds -- only bites for entries with no identifier,
    since ORCID groups works that share one, so `_with_doi_field` puts a DOI on every entry.

    Auto-update still comes first in time, but only covers works whose deposited metadata
    already contains your iD: it fixes the future, not the backlog.
    """
    # Every paper, not only the ones with entry text. A paper discovered on arXiv or
    # Semantic Scholar has no `bibtex` field, and filtering on that field is how 16 of
    # them -- including one with 112 citations -- were quietly left out of this file and
    # therefore out of the ORCID record. `synth_bibtex` builds the entry from the fields
    # we do have; the audit's "ORCID holds your papers" row is what caught the gap.
    prepared = [(p, _with_doi_field((p.get("bibtex") or synth_bibtex(p)).strip(),
                                    paper_doi(p) or "")) for p in papers]
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
            dois.append(f"{d}\t{title_of(p)}")
    doi_path = os.path.join(TASKS, "orcid_dois.txt")
    with open(doi_path, "w") as f:
        f.write("# The bulk route is orcid_import.bib -- one upload instead of this\n"
                "# list one form at a time. Keep this for spot-fixing single works.\n"
                + "\n".join(dois) + "\n")
    return bib, doi_path, len(with_doi) + len(without)


def wikidata_qs(cfg, papers) -> str:
    """QuickStatements v1 commands for the author item.

    Identity and external identifiers only. No claims about importance and no unsourced
    biography, so the item stays the stable anchor other statements point at.

    Targets the item `ids.wikidata` names, and falls back to `CREATE` only when it names
    none. Addressed to a QID the same statements are a safe top-up, since QuickStatements
    skips a statement already present, while an unconditional `CREATE` adds a second person
    and duplicates need a merge request rather than an edit.

    NOTE: QuickStatements requires an *autoconfirmed* Wikidata account (4 days old, 50
    edits), and the error it gives does not say so. `wikidata_manual` below works on day one.
    """
    ident, ids = cfg["identity"], cfg["ids"]
    qid = ids.get("wikidata")
    subject = qid or "LAST"
    L = [] if qid else ["CREATE"]
    def add(prop, val):
        L.append(f"{subject}\t{prop}\t{val}")
    # Label and description only on a new item. Aliases are additive, so they are safe
    # to re-send, but `Len`/`Den` *overwrite* -- and on an existing item that means a
    # batch silently reverting a label someone improved by hand.
    if not qid:
        L.append(f'LAST\tLen\t"{ident["name"]}"')
        L.append('LAST\tDen\t"researcher in natural language processing"')
    for v in ident["name_variants"]:
        if v != ident["name"]:
            L.append(f'{subject}\tAen\t"{v}"')
    add(P["instance_of"], Q["human"])
    add(P["occupation"], Q["researcher"])
    add(P["occupation"], Q["computer_scientist"])
    add(P["field_of_work"], Q["natural language processing"])
    add(P["field_of_work"], Q["machine learning"])
    add(P["orcid"], f'"{ident["orcid"]}"')
    add(P["website"], f'"{ident["canonical_url"]}"')
    for a in ident["affiliations"]:
        # No blank rows here: QuickStatements would reject the line, not prompt for it.
        if employer_q(a):
            add(P["employer"], employer_q(a))
    # educated at, for degree-granting study only -- a postdoc is P108 above, since no
    # degree was awarded and the institution was the employer.
    for e in ident.get("education") or []:
        q = SCHOOL_Q.get(e.get("institution"))
        if not q:
            continue
        line = f"{subject}\t{P['educated_at']}\t{q}"
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


def wd_statements(cfg) -> list[tuple[str, str, str, str]]:
    """Every statement the item should carry, as (label, property, value, item).

    Labels rather than P/Q numbers, because the Wikidata editor autocompletes on labels.
    The numbers ride along only so you can confirm the autocomplete picked the right one.
    """
    ident = cfg["identity"]
    rows = [("instance of", "P31", "human", "Q5"),
            ("occupation", "P106", "researcher", "Q1650915"),
            ("occupation", "P106", "computer scientist", "Q82594"),
            ("field of work", "P101", "natural language processing", "Q30642"),
            ("field of work", "P101", "machine learning", "Q2539"),
            ("ORCID iD", "P496", ident["orcid"], ""),
            ("official website", "P856", ident["canonical_url"], "")]
    for a in ident["affiliations"]:
        # Unlike the batch file, a blank Q-number is useful here: the row still tells you
        # to add the employer and to autocomplete the item yourself.
        rows.append(("employer", "P108", org_name(a), employer_q(a)))
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
    return rows


def wd_head(ident: dict, qid: str) -> list[str]:
    """The page down to the statements table's header row.

    Two documents from one generator. Once the item exists the create half is not "done
    and harmless to leave up" -- it is four numbered steps telling you to make a second
    item, on a page whose title says that is the job. What survives the switch is the
    reference table and the caveats, which are what you actually come back for.
    """
    aliases = [v for v in ident["name_variants"] if v != ident["name"]]

    if qid:
        return [
            f"# Wikidata: your author item ({qid})", "",
            "Generated by `python scripts/identity_tasks.py`.", "",
            f"<https://www.wikidata.org/wiki/{qid}>", "",
            "**The item exists, so nothing on this page creates one.** It is the reference",
            "for what the item should hold, and the caveats worth re-reading before an",
            f"edit. `tasks/wikidata.qs` is addressed to {qid} rather than to `CREATE`, so",
            "running it tops up whatever is missing and does nothing where the statement is",
            "already there.", "",
            "Whether anything *is* missing is the `Wikidata item complete` row of",
            "[identity_audit.md](identity_audit.md) — it compares the live item against the",
            "table below on every run, so that row is the answer and this table is what it",
            "checked.", "",
            "## What the item should hold", "",
            f"Label `{ident['name']}`, description `researcher in natural language "
            "processing`, and these aliases, each its own entry:",
            *[f"- {a}" for a in aliases],
            "",
            "In the editor, click *+ Add statement*, type the **property name** — it",
            "autocompletes — then the value. The P/Q numbers are only to confirm the",
            "autocomplete resolved to the right thing.", "",
            "| property | | value | |", "|---|---|---|---|"]
    else:
        return [
            "# Wikidata: create the author item by hand", "",
            "Generated by `python scripts/identity_tasks.py`.", "",
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

def wd_caveats(ident: dict, qid: str) -> list[str]:
    """What follows the table. The two values Wikidata warns about rather than refuses,
    qualifiers, employer against educated at, and whether the paper items are worth it."""
    return [
        "",
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
          # Dropped once the Q-number is in config, which is the only thing this step
          # asks for -- leaving it up is an instruction to go and do what is done.
          *([] if qid else
         ["## 4. Record the result", "",
          "Copy the new Q-number from the URL into `config.yaml` → `ids.wikidata`, then",
          "`python scripts/build_site.py --deploy`. It lands in the site's `sameAs` array,",
          "which is what lets an engine fuse the Wikidata item with your pages.", ""]),
          f"## {'' if qid else '5. '}Your paper items: measure first, because the "
          "standard advice may not apply",
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


def wikidata_manual(cfg) -> str:
    """The by-hand route, because QuickStatements is gated on autoconfirmed.

    A researcher creating an account for this has neither 4 days nor 50 edits, so the .qs file
    fails with an authorisation error rather than an explanation. Creating an item by hand has
    no such gate, so that is the primary route and the batch file is the shortcut for later.
    """
    ident = cfg["identity"]
    qid = cfg["ids"].get("wikidata")
    L = wd_head(ident, qid)
    for label, p, val, q in wd_statements(cfg):
        L.append(f"| {label} | `{p}` | {val} | {f'`{q}`' if q else ''} |")
    L += wd_caveats(ident, qid)
    path = os.path.join(TASKS, "wikidata_manual.md")
    write_task(path, L)
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
         "Generated by `python scripts/identity_tasks.py`.", "",
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
        title = (title_of(p)).replace("|", "/")
        L.append(f"| {p.get('citations') or 0} | {title[:70]} | {s2} |")
    L += ["", "## Why bother",
          "Every Semantic-Scholar-backed tool -- Elicit, Consensus, SciSpace, and most",
          "literature agents -- resolves an author to one page. A split profile means",
          "each of them sees roughly half your corpus and ranks both halves lower.",
          "", "## The durable fix",
          "Populate ORCID. S2's disambiguation uses it, so an ORCID with all works",
          "attached reduces the chance the split reappears after future re-clustering."]
    write_task(path, L)
    return path, len(strays)


def openalex_merge(cfg) -> str:
    ids = cfg["ids"]
    keep = ids["openalex"][0].rsplit("/", 1)[-1]
    dups = [d.rsplit("/", 1)[-1] for d in ids.get("openalex_duplicates") or []]
    path = os.path.join(TASKS, "openalex_merge.md")
    L = ["# OpenAlex: merge duplicate author profiles", "",
         "Generated by `python scripts/identity_tasks.py`.", "",
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
    write_task(path, L)
    return path


# ------------------------------------------------------------------ arXiv journal-ref
#
# No code can fill this form, for three independently final reasons: arXiv's public API
# has no metadata-update endpoint at any access level; their robots.txt disallows `/user`,
# which is the only page mapping an arXiv id to the submission id `/jref` needs; and
# `/jref` itself is not a paste-an-identifier form.
#
# So the author signs in and saves that one page, code reads the local file, and no
# request is made on his behalf -- `--user-page` is that path. Without it the file still
# works; it just links to the abs page and says to find the row.

# A trailing comma-segment worth keeping. DBLP writes booktitles as
# `<name>, <ACRO> <year>, <city>, <country>, <dates>[, Volume N: Long Papers]`, so the
# first segment is the venue and the rest is conference logistics -- except the track,
# which is part of what was published and belongs in a journal-ref.
_TRACK = re.compile(r"^\(?(?:Volume\b|.*\b(?:Papers|Demonstrations|Demos|Track)\b)", re.I)
# `EMNLP 2022 - System Demonstrations` -> `System Demonstrations`: the acronym is already
# in the first segment, so repeating it reads like two venues.
_ACRO_YEAR = re.compile(r"^[A-Z][\w@.*-]*(?:[ -][A-Z][\w@.*-]*)*\s+\d{4}\s*[-–]\s*")
# Findings volumes are per-conference, and a bibliography that says only "Findings of the
# Association for Computational Linguistics" has dropped the half that identifies which.
# The Anthology DOI still carries it.
_FINDINGS_DOI = re.compile(r"/(\d{4})\.findings-(emnlp|acl|naacl|eacl)\b", re.I)
# `Findings of the Association for Computational Linguistics, ACL 2024, Bangkok, ...`:
# here the acronym segment is the sub-venue rather than logistics, which is the one case
# where dropping it loses information the first segment does not carry.
_SUBVENUE = re.compile(r"^([A-Z][\w@.*&-]*(?:[ -][A-Z][\w@.*&-]*)*)\s+(\d{4})$")


def journal_ref(p: dict) -> str:
    """arXiv's Journal-ref field for one paper: name, volume, year, pages.

    Built from the cached bibtex rather than from `venue`, because the bibtex is the
    publisher's own record of what was published and `venue` has been through this
    project's shortener. Returns "" when there is no venue string to work from, which
    the caller reports rather than papering over.
    """
    e = (parse_bibtex(p.get("bibtex") or "") or [{}])[0]
    name = re.sub(r"\bthe The\b", "the",
                  clean_latex(e.get("journal") or e.get("booktitle") or ""))
    segs = [s.strip() for s in name.split(",") if s.strip()]
    if not segs:
        return ""
    name = ", ".join([segs[0]] + [_ACRO_YEAR.sub("", s) for s in segs[1:] if _TRACK.match(s)])
    if "findings" in name.lower() and ":" not in name:
        for s in segs[1:]:
            if m := _SUBVENUE.match(s):
                name = f"{name}: {m.group(1)} {m.group(2)}"
                break
    if m := _FINDINGS_DOI.search(journal_doi(p)):
        # A Findings paper whose bibliography entry says only `EACL` is claiming the main
        # conference, which is the one kind of wrong worth overruling a source over. The
        # DOI spells out which Findings volume it is, so use the Anthology's own title.
        which = f"{m.group(2).upper()} {m.group(1)}"
        low = name.lower()
        if "findings" not in low:
            name = f"Findings of the Association for Computational Linguistics: {which}"
        elif which.lower() not in low:
            name = f"{name}: {which}"
    year = str(e.get("year") or p.get("year") or "").strip()
    pages = re.sub(r"-{2,}", "-", (e.get("pages") or "").strip())
    # Only a real volume number. DBLP puts the sub-venue in `volume` on some Findings
    # entries, and `Findings of the ACL: EMNLP 2020 {EMNLP} 2020 (2020) 2678-2697` is
    # what that produces if you trust the field.
    if (vol := (e.get("volume") or "").strip()) and vol.isdigit():
        return f"{name} {vol} ({year}) {pages}".strip()
    if pages:
        name += f", pages {pages}"
    return f"{name}, {year}" if year and year not in name else name


def journal_doi(p: dict) -> str:
    """The published version's DOI, or "" -- never the arXiv one.

    `paper_doi` falls back to `10.48550/arXiv.<id>`, which is right for ORCID (any
    identifier beats none, because ORCID groups on it) and wrong here: this field means
    "the version of record lives at this DOI", and pointing it at the arXiv listing the
    field is attached to asserts that the preprint is the published version.
    """
    e = (parse_bibtex(p.get("bibtex") or "") or [{}])[0]
    for d in (p.get("doi"), e.get("doi")):
        d = (d or "").strip().removeprefix("doi:").removeprefix("https://doi.org/")
        if d and not d.lower().startswith("10.48550"):
            # The Anthology mints these entirely lowercase and one source shouts them
            # back, `/V1/` and `2021.EMNLP-MAIN.619` alike. Lowercased whole rather than
            # patched segment by segment, and only for this prefix, because it is the one
            # registrant here whose canonical form is known.
            return d.lower() if d.startswith("10.18653/") else d
    return ""


class _ArticlesPage(HTMLParser):
    """arXiv id -> submission id, from a saved copy of the signed-in articles list.

    Pairs each `/submit/<n>/jref` link with the most recent arXiv id seen before it, in
    document order, rather than assuming a table structure -- the page has been a table,
    a list of divs, and a table again over the years, and document order has held
    throughout because the link is inside the row it belongs to.
    """

    ID = re.compile(r"\b(\d{4}\.\d{4,5})(?:v\d+)?\b")
    JREF = re.compile(r"/submit/(\d+)/jref")

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.found: dict[str, str] = {}
        self._last = ""

    def handle_starttag(self, tag, attrs):
        href = dict(attrs).get("href") or ""
        if m := self.ID.search(href):
            self._last = m.group(1)
        if (m := self.JREF.search(href)) and self._last:
            self.found[self._last] = m.group(1)

    def handle_data(self, data):
        if m := self.ID.search(data):
            self._last = m.group(1)


def read_articles_page(path: str) -> dict[str, str]:
    with open(path, encoding="utf8", errors="replace") as f:
        parser = _ArticlesPage()
        parser.feed(f.read())
    return parser.found


# Written by hand rather than through `common.write_yaml` for the header: a bare map of
# five-digit numbers to five-digit numbers is unreadable without one, and the reader who
# needs it is whoever finds this file in a diff two years from now.
SUBS_HEADER = """\
# arXiv id -> submission id, read out of a copy of https://arxiv.org/user that the author
# saved while signed in. Regenerate or extend with:
#
#   python scripts/identity_tasks.py --user-page ~/Downloads/arxiv-user.html
#
# Committed because it is stable input rather than observed state -- a submission id never
# changes -- and because without it `tasks/arxiv_jref.md` cannot link straight to the form
# for each paper. Not a secret: the form behind it requires the owner's session.
"""


def save_submissions(path: str, subs: dict) -> None:
    with open(path, "w") as f:
        f.write(SUBS_HEADER)
        yaml.safe_dump(dict(sorted(subs.items())), f, sort_keys=False, default_style="'")


def arxiv_jref(cfg, papers, subs: dict) -> tuple[str, int, int]:
    """The papers whose arXiv listing does not say where they were published.

    Two fields, tracked separately because they go missing separately: the API reports both
    `journal_ref` and the author-entered `doi`, and a paper can have one and not the other.
    Listing only the no-journal-ref papers would miss the DOI-shaped half of the same visit to
    the same form.

    Held back: a paper with no publisher DOI whose venue year has not passed. arXiv's help
    page is explicit that "to appear in" is not an appropriate journal reference, and a minted
    DOI is the cheapest proof the version of record exists rather than being scheduled. Weak
    in the safe direction -- it holds back a published paper sometimes, and the section says
    so, but never puts a promise on a listing.
    """
    year_now = datetime.date.today().year
    ready, wait = [], []
    for p in sorted(papers, key=lambda p: -(p.get("citations") or 0)):
        if not p.get("arxiv"):
            continue
        doi = journal_doi(p)
        jr = ("" if p.get("arxiv_journal_ref")
                    or not (p.get("venue") and not is_preprint_venue(p["venue"]))
              else journal_ref(p))
        row = (p, jr, doi if not p.get("arxiv_doi") else "")
        if not jr and not row[2]:
            continue
        (wait if not doi and int(p.get("year") or 0) >= year_now else ready).append(row)

    path = os.path.join(TASKS, "arxiv_jref.md")
    L = [f"# arXiv: the journal reference and DOI for {len(ready)} papers", "",
         "Generated by `python scripts/identity_tasks.py`.", "",
         "Every one of these is a paper that appeared somewhere, whose arXiv listing does not",
         "fully say so. That listing is what most answer engines and half the citation graph",
         "read, so the effect is a published paper that reads as a preprint.",
         "",
         "A paper is here if its listing is missing the journal-ref **or** the published DOI --",
         "they go missing separately, and both are fields on the same form, so splitting them",
         "into two lists would mean visiting the same page twice."
         + (f" {len(wait)} more are held back at the bottom." if wait else ""),
         "",
         "**Adding these does not create a new version.** No recompile, no v2, no new",
         "announcement -- arXiv's own help page says the journal reference, DOI and report",
         "number fields can be updated at any time without generating a new version. The",
         "cost of doing all of them in one sitting is the clicking, nothing else.",
         "",
         "## The three fields", "",
         "| Field | What to put | Why |", "|---|---|---|",
         "| `Report number:` | **leave blank** | It means an *institutional* preprint number "
         "-- a lab's own report series, like `MIT-CSAIL-TR-2019-002`. None of these papers "
         "has one, and arXiv is explicit that it is not for anything else. |",
         "| `Journal-ref:` | the line below each paper | arXiv asks for journal name, volume, "
         "year and page numbers. Built here from the publisher's own bibtex. |",
         "| `Journal version DOI:` | the line below each paper | The *published* DOI, with no "
         "`doi:` prefix. Never the `10.48550/arXiv.…` one: that is this listing, so putting it "
         "here claims the preprint is the version of record. |",
         "",
         "Multiple report numbers, if there ever were any, are separated by `; `.",
         "",
         "A few `Journal-ref:` lines below are thin -- `ICLR, 2025` rather than the spelled-out",
         "proceedings title -- because that is all the bibliography had for a venue that",
         "publishes through OpenReview and mints no DOI. arXiv accepts either, so expand one",
         "if you feel like it and paste it if you do not.",
         "",
         "## Could a script fill this in?", "",
         "No, and the answer is not \"nobody wrote it yet\":", "",
         "1. arXiv's API is read-only. There is no metadata-write endpoint at any access level.",
         "2. `robots.txt` disallows `/user`, and that is the only page mapping an arXiv id to",
         "   the submission id the form needs -- so a scraper does the one thing arXiv asked",
         "   automated clients not to do.",
         "3. `/jref` takes no identifier. Signed out it redirects to login; signed in it is",
         "   your articles list, and each row links to its own form.",
         "",
         "What *is* automatable is the part below: knowing which papers, and exactly what to",
         "type in each field. That is the whole of the work that is not a click.",
         "",
         "### Getting the links to go straight to the form", "",
         "The per-paper links below are deep links into your own submissions when this file",
         "knows the submission ids, and abs-page links when it does not. To fill them in:",
         "",
         "1. Sign in and open <https://arxiv.org/user>.",
         "2. Save the page (⌘S, \"Page Source\" is enough).",
         "3. `python scripts/identity_tasks.py --user-page ~/Downloads/arxiv-user.html`",
         "",
         "The ids are cached in `data/arxiv_submissions.yaml`, so this is once, not per run.",
         "No request is made on your behalf at any point -- code reads the file you saved.",
         ""]
    if not subs:
        L += ["> Submission ids not known yet, so the links below go to the abs page. Do the",
              "> three steps above once and they become one-click.", ""]
    def block(n: int, p: dict, jr: str, doi: str) -> list[str]:
        title = (title_of(p)).strip()
        cites = p.get("citations")
        sub = subs.get(p["arxiv"])
        # Only the fields that are actually empty, and the one that is not gets a line
        # saying what is already there -- otherwise the form and this file disagree and
        # the reader has to work out which of them is stale.
        fields = []
        if jr:
            fields.append(f"Journal-ref:          {jr}")
        elif p.get("arxiv_journal_ref"):
            fields.append(f"# already set:        {p['arxiv_journal_ref']}")
        if doi:
            fields.append(f"Journal version DOI:  {doi}")
        elif p.get("arxiv_doi"):
            fields.append(f"# already set:        {p['arxiv_doi']}")
        else:
            fields.append("Journal version DOI:  (none minted — leave blank)")
        return [f"### {n}. {title}" + (f" — cited {cites}" if cites else ""), "",
                f"<https://arxiv.org/submit/{sub}/jref>" if sub else
                f"<https://arxiv.org/abs/{p['arxiv']}> — find this row in "
                f"<https://arxiv.org/user> and use its own *journal ref* link",
                "", "```", *fields, "```", ""]

    L += [f"## {len(ready)} to fill in", "",
          "Highest citations first, so stopping early still helps most. A commented line is a",
          "field the listing already has -- shown so you can check it rather than retype it.",
          ""]
    for i, row in enumerate(ready, 1):
        L += block(i, *row)
    if wait:
        L += [f"## {len(wait)} to leave alone for now", "",
              "No publisher DOI yet and the venue year has not passed, so as far as this file",
              "can tell the proceedings are not out -- and arXiv says \"to appear in\" and",
              "\"accepted for publication in\" are *not* appropriate journal references. Each",
              "moves into the list above on its own once a DOI appears.",
              "",
              "If you know better than the test -- the event happened, the proceedings are up --",
              "the values are here and they are as good as any above.", ""]
        for i, row in enumerate(wait, 1):
            L += block(i, *row)
    L += ["## After filling these in", "",
          "`python update.py` re-reads the abs pages, so the next run drops each paper from",
          "this file by itself. Nothing here needs ticking off by hand."]
    write_task(path, L)
    return path, len(ready), len(wait)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--user-page", metavar="FILE",
                    help="a saved copy of https://arxiv.org/user; read once to learn the "
                         "submission ids that make the journal-ref links one-click")
    args = ap.parse_args()

    cfg = load_config()
    papers = read_papers()
    os.makedirs(TASKS, exist_ok=True)
    bib, dois, n = orcid_files(cfg, papers)
    qs = wikidata_qs(cfg, papers)
    manual = wikidata_manual(cfg)
    s2, n_strays = s2_merge(cfg, papers)
    oa = openalex_merge(cfg)
    # The cache is committed, so the ids survive; a re-read of the same page is a no-op
    # and a re-read of a newer one adds the papers submitted since.
    subs_path = os.path.join(DATA, "arxiv_submissions.yaml")
    subs = read_yaml(subs_path) or {}
    if args.user_page:
        found = read_articles_page(args.user_page)
        if not found:
            sys.exit(f"no arXiv-id-to-submission-id pairs in {args.user_page}\n"
                     "Is it the signed-in https://arxiv.org/user page? A saved login page "
                     "or an abs page has no /submit/<n>/jref links in it.")
        new = {k: v for k, v in found.items() if subs.get(k) != v}
        subs.update(found)
        save_submissions(subs_path, subs)
        print(f"read {args.user_page}: {len(found)} submissions, {len(new)} new -> {subs_path}\n")
    jref, n_jref, n_wait = arxiv_jref(cfg, papers, subs)
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
    print(f"  {jref}   ({n_jref} arXiv listings to add a journal-ref to"
          + (f", {n_wait} waiting on a DOI)" if n_wait else ")")
          + ("" if subs else " -- run with --user-page for one-click links"))
    print("\nFor the live state of ORCID, arXiv, Wikidata and Hugging Face:")
    print("  python scripts/audit_identity.py")


if __name__ == "__main__":
    main()
