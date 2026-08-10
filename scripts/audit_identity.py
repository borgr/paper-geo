#!/usr/bin/env python3
"""Audit the identity surfaces you do not control, against what they should say.

Everything else in this repo checks *our* artifacts. This checks the five external
surfaces that decide whether a retrieval system can resolve you to one person, by
reading their public APIs -- no login, no key, read-only:

    ORCID          public works count, researcher URLs, name variants, keywords
    arXiv          which papers your account is actually registered as author on
    Wikidata       whether an author item carrying your ORCID exists yet
    Hugging Face   which paper pages exist, and which you have claimed
    Semantic Sch.  how the corpus is split across author records
    arXiv metadata whether its author list spells your name right at all

The arXiv check is the one worth the network round-trip. Linking ORCID to arXiv
gives you a public list at arxiv.org/a/<orcid> built from arXiv's *authority
records* -- papers your account is registered as an author on. For a co-authored
corpus that is usually a fraction of your papers, and it is also the gate on
editing them: you cannot add a journal-ref to a paper you do not own. So this
diff is a prerequisite list, not a vanity metric.

Writes tasks/identity_audit.md, tasks/arxiv_ownership.md, tasks/hf_worklist.md and
tasks/arxiv_name_fixes.md.

Usage:
    python scripts/audit_identity.py               # everything (~60s, HF dominates)
    python scripts/audit_identity.py --no-hf       # skip the per-paper HF checks
    python scripts/audit_identity.py --no-names    # skip the arXiv author-name check
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (BUILD, DATA, ROOT, WD_IDENTIFIERS, declined, get,  # noqa: E402
                    get_json, load_config, name_match, norm_name, norm_title,
                    org_name, paper_doi, plural, read_yaml, synth_bibtex,
                    title_tokens)

TASKS = os.path.join(ROOT, "tasks")
ATOM = {"a": "http://www.w3.org/2005/Atom"}
_ABS = re.compile(r"abs/([0-9]{4}\.[0-9]{4,5}|[a-z\-]+/[0-9]{7})")


def _org_match(a: str, b: str) -> bool:
    """Loose organisation-name match.

    Registries and CVs disagree on the same institution in ways that are never
    meaningful: `The Hebrew University of Jerusalem` vs `Hebrew University of
    Jerusalem`, `MIT-IBM Watson AI Lab` vs `Massachusetts Institute of Technology`.
    Exact comparison would report every one of those as a missing affiliation, so the
    check is on significant words and either direction containing the other.
    """
    stop = {"the", "of", "and", "institute", "university", "research", "lab",
            "laboratory", "school", "center", "centre", "for"}
    wa = {w for w in re.findall(r"[a-z]+", a.lower()) if w not in stop}
    wb = {w for w in re.findall(r"[a-z]+", b.lower()) if w not in stop}
    if not wa or not wb:
        return False
    return wa <= wb or wb <= wa


def orcid_public(orcid: str) -> dict:
    """Read the public ORCID record.

    The public API is what Semantic Scholar, OpenAlex and Crossref see. An item
    whose visibility is "trusted parties" is invisible here -- so a works count of
    0 does not distinguish "empty" from "private", and both fail identically.
    """
    d = get_json(f"https://pub.orcid.org/v3.0/{orcid}/record") or {}
    act, person = d.get("activities-summary") or {}, d.get("person") or {}
    urls = [(u.get("url-name"), (u.get("url") or {}).get("value"))
            for u in ((person.get("researcher-urls") or {}).get("researcher-url") or [])]
    # Titles, not just the count. A bulk BibTeX import is one click and cannot be
    # undone in one click, so the record can silently end up asserting authorship of
    # works that were in the source file by mistake -- and nothing on ORCID will ever
    # tell you, because the record has no idea what you meant to claim.
    titles = []
    # Who asserted each work, tallied. This is the only public evidence that the
    # Crossref and DataCite auto-update permissions are live: a work those add carries
    # their name in `source`, while everything you imported yourself carries yours. The
    # distinction is invisible in the works list unless you open a work and read the
    # *Source* line, and it is the difference between "the pipeline is running" and "I
    # clicked through a wizard and nothing was granted".
    sources = {}
    for gidx, g in enumerate(((act.get("works") or {}).get("group") or [])):
        # The group's external ids are what ORCID itself groups on, and they are the
        # only reliable key back to the corpus: a title changes between preprint and
        # proceedings ("Transition based Graph Decoder" -> "Enhancing the Transformer
        # Decoder with Transition-based Syntax") and a subtitle gets dropped
        # ("TIES-Merging: Resolving Interference" -> "Resolving Interference"), and
        # both then look like works we have never heard of. Identifiers do not drift.
        ids = [((e.get("external-id-type") or "").lower(), e.get("external-id-value") or "")
               for e in ((g.get("external-ids") or {}).get("external-id") or [])]
        for s in (g.get("work-summary") or []):
            src = ((s.get("source") or {}).get("source-name") or {}).get("value") or "(self)"
            sources[src] = sources.get(src, 0) + 1
            t = ((s.get("title") or {}).get("title") or {}).get("value")
            if not t:
                continue
            # Every work in the group, not just the first, and each with the ids *it*
            # carries rather than the group's union. Reading only `i == 0` was hiding a
            # whole class of error: ORCID groups on shared identifiers, so a work that
            # carries the wrong DOI lands inside another paper's group and its title is
            # never looked at. The live case is put-code 222829712, "Resolving
            # Interference (RI): Disentangling Models for Improved Model Merging" (2026),
            # filed under TIES-Merging's `10.48550/ARXIV.2306.01708`. The group resolved
            # to TIES, RI's own arXiv id `2603.13467` appears nowhere on the record as an
            # identifier, and the audit therefore reported RI as *missing from ORCID*
            # while it was sitting on the record the whole time. Own ids over group ids
            # for the same reason: the union would resolve every work in a group to
            # whichever paper the group is about, which is what made the error invisible.
            own = [((e.get("external-id-type") or "").lower(), e.get("external-id-value") or "")
                   for e in ((s.get("external-ids") or {}).get("external-id") or [])]
            # The group index rides along because it is the difference between a real
            # duplicate and a cosmetic one. Two works in *different* groups show on the
            # profile as two works, and every service counting output counts both. Two
            # works in the *same* group are one entry with "2 versions" -- ORCID already
            # unified them, and nothing downstream double-counts. Same slug reached twice,
            # two different severities, so they cannot share a report section.
            titles.append((t, s.get("put-code"), own or ids, gidx))
    affs = {}
    for sect in ("employments", "educations"):
        rows = []
        for g in ((act.get(sect) or {}).get("affiliation-group") or []):
            for summary in (g.get("summaries") or []):
                v = next(iter(summary.values()), {}) or {}
                sd, ed = v.get("start-date") or {}, v.get("end-date") or {}
                # Who asserted the entry. An affiliation added by the institution
                # itself is read-only for the researcher: ORCID offers *Delete*, and
                # no *Edit*. Reporting "add the degree to the Role field" on one of
                # those sends someone looking for a control that is not there.
                src = ((v.get("source") or {}).get("source-name") or {}).get("value")
                rows.append({
                    "org": ((v.get("organization") or {}).get("name")),
                    "role": v.get("role-title"),
                    "dept": v.get("department-name"),
                    "start": (sd.get("year") or {}).get("value"),
                    "end": (ed.get("year") or {}).get("value") if ed else None,
                    "source": src,
                    "put": v.get("put-code"),
                })
        affs[sect] = rows
    return {
        "works": len((act.get("works") or {}).get("group") or []),
        "work_titles": titles,
        "work_sources": sources,
        "employments": len(affs["employments"]),
        "educations": len(affs["educations"]),
        "employment_rows": affs["employments"],
        "education_rows": affs["educations"],
        "urls": urls,
        "other_names": [n.get("content") for n in
                        ((person.get("other-names") or {}).get("other-name") or [])],
        "keywords": [k.get("content") for k in
                     ((person.get("keywords") or {}).get("keyword") or [])],
        "biography": bool(person.get("biography")),
        "reachable": bool(d),
    }


def arxiv_registered(orcid: str) -> set[str] | None:
    """arXiv ids your account is registered as an author on.

    Read from the Atom flavour of arxiv.org/a/<orcid>: the HTML page 303-redirects
    and is JS-free, but the feed is the parseable one. None means the page does not
    exist yet, which happens when the ORCID is not linked to an arXiv account.
    """
    raw = get(f"https://arxiv.org/a/{orcid}.atom2", retries=2)
    if not raw:
        return None
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        # An unlinked ORCID serves the arXiv 404 page, which is HTML, not Atom.
        return None
    out = set()
    for e in root.findall("a:entry", ATOM):
        m = _ABS.search((e.findtext("a:id", "", ATOM) or ""))
        if m:
            out.add(m.group(1))
    return out


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
        j = get_json("https://www.wikidata.org/w/api.php?action=query&list=search"
                     f"&srsearch={q}&srlimit=5&format=json") or {}
        for hit in ((j.get("query") or {}).get("search") or []):
            return hit["title"]
    return None




def wikidata_gaps(qid: str, cfg) -> dict:
    """Diff a live Wikidata item against the identifiers config says it should carry.

    Worth checking rather than assuming, because hand-created items acquire two
    specific defects that are invisible on the page: a statement added twice (the
    editor does not warn), and an alias pasted as one string when it was meant as
    several -- markdown backticks and all, which is what happened here. Both are
    silent: the item looks complete and queries against it come back wrong.
    """
    d = get_json(f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json") or {}
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
    return {"qid": qid, "missing": missing, "wrong": wrong, "dupes": dupes,
            "aliases": aliases, "bad_aliases": bad_aliases,
            "want_aliases": want_aliases,
            "n_p856": len(vals.get("P856") or []),
            "label": (ent.get("labels") or {}).get("en", {}).get("value", ""),
            "description": (ent.get("descriptions") or {}).get("en", {}).get("value", "")}


def wikidata_paper_coverage(papers, chunk: int = 50) -> dict:
    """How many of your papers exist as Wikidata items -- measured, not assumed.

    This function exists because the assumption was wrong. The standard advice for a
    new author item is "your papers are already on Wikidata as Crossref imports, so
    linking them is nearly free", and Author Disambiguator reinforces it: the tool
    only ever shows you items that already exist, so a short list looks like a short
    job rather than like thin coverage. Measured here, coverage was 3 of 122. Which
    inverts the advice -- the work is creating items, not relinking strings.

    Matching is on DOI (P356) and arXiv id (P818), never on name. Those are exact
    keys, so a hit is the paper and not a paper that cites it. DOIs go in twice, as
    given and uppercased, because Wikidata's convention is uppercase and SPARQL
    string match is case-sensitive.

    The endpoint is the one detail here that will silently produce a wrong answer.
    Wikidata split its query service: scholarly articles were moved out of the main
    graph into their own, and `query.wikidata.org` serves the main one. So a paper
    query against the usual endpoint returns zero rows with HTTP 200 -- verified
    against "Attention is all you need" (Q30249683), which the scholarly endpoint
    finds by arXiv id and the main endpoint does not. Any SPARQL over publications,
    here or by hand, needs query-scholarly.

    Returns {} when the endpoint does not answer. An empty result and a failed query
    must not be indistinguishable, or a timeout silently becomes evidence of absence.
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
    answered = False
    for i in range(0, len(ordered), chunk):
        vals = " ".join('"%s"' % k.replace('"', "") for k in ordered[i:i + chunk])
        # One query, two properties: the identifier forms are disjoint, so a UNION
        # over both costs the same as testing each list separately.
        sparql = ("SELECT ?item ?v WHERE { VALUES ?v {" + vals + "} "
                  "{ ?item wdt:P818 ?v } UNION { ?item wdt:P356 ?v } }")
        j = get_json("https://query-scholarly.wikidata.org/sparql?format=json&query="
                     + quote(sparql))
        if j is None:
            continue
        answered = True
        for b in ((j.get("results") or {}).get("bindings") or []):
            v = (b.get("v") or {}).get("value", "")
            qid = ((b.get("item") or {}).get("value", "")).rsplit("/", 1)[-1]
            if v in keys and qid:
                found[keys[v]["slug"]] = qid
    if not answered:
        return {}

    present = [(p, found[p["slug"]]) for p in papers if p["slug"] in found]
    absent = [p for p in papers if p["slug"] not in found]
    return {"present": present, "absent": absent,
            "checked": len({p["slug"] for p in keys.values()}), "total": len(papers)}


def wikidata_papers_qs(cov: dict, cfg) -> tuple[str | None, int]:
    """QuickStatements batch that creates items for the papers Wikidata lacks.

    Only generated because the measurement came back low. If coverage had been the
    "dozens already imported" the usual advice assumes, the job would be relinking
    author name strings and this file would be the wrong tool.

    Restricted to papers carrying a DOI or an arXiv id. That is not a formatting
    convenience: an external identifier anyone can resolve is what makes a
    publication item uncontroversially in scope, and it is also the key this batch
    was deduplicated on, so a row without one could be creating a duplicate.

    Co-authors go in as `author name string` (P2093) with a series-ordinal
    qualifier, not as `author` (P50). Pointing P50 at a guessed person item is the
    error that takes someone else's item and welds it to your paper -- the same
    asymmetry that governs the authorship gate in the collector. Strings are what
    the Crossref importers themselves deposit, and a later disambiguator upgrades
    them safely.
    """
    absent = [p for p in (cov.get("absent") or []) if p.get("doi") or p.get("arxiv")]
    if not absent:
        return None, 0
    me = cfg["ids"].get("wikidata")
    L: list[str] = []
    for p in absent:
        title = (p.get("title_display") or p["title"]).replace('"', "'").strip()
        # Wikidata rejects a label over 250 characters outright, and the batch stops
        # on the offending row rather than skipping it.
        label = title[:245]
        # A 10.48550 DOI is arXiv minting one for its own preprint, so it is not
        # evidence of publication -- classing those as scholarly articles would assert
        # a venue that does not exist.
        published = bool(p.get("doi")) and not str(p["doi"]).lower().startswith("10.48550/")
        L += ["CREATE",
              f'LAST\tLen\t"{label}"',
              f"LAST\tP31\t{'Q13442814' if published else 'Q580922'}",
              f'LAST\tP1476\ten:"{title}"']
        if p.get("year"):
            L.append(f'LAST\tP577\t+{int(p["year"])}-00-00T00:00:00Z/9')
        if p.get("doi"):
            L.append('LAST\tP356\t"%s"' % str(p["doi"]).upper())
        if p.get("arxiv"):
            L.append('LAST\tP818\t"%s"' % p["arxiv"])
        for i, a in enumerate(p.get("authors") or [], 1):
            a = a.replace('"', "'").strip()
            if not a:
                continue
            if me and norm_name(a) == norm_name(cfg["identity"]["name"]):
                L.append(f'LAST\tP50\t{me}\tP1545\t"{i}"')
            else:
                L.append(f'LAST\tP2093\t"{a}"\tP1545\t"{i}"')
    path = os.path.join(TASKS, "wikidata_papers.qs")
    with open(path, "w") as f:
        f.write("\n".join(L) + "\n")
    return path, len(absent)


# Hugging Face records a per-author `status` beside the linked user. These two mean
# the link is live; anything else with a user attached is a claim in flight.
HF_CLAIM_DONE = {"claimed_verified", "admin_assigned"}


def hf_state(papers, me: str, variants, requested=()) -> dict[str, list]:
    """Live per-paper Hugging Face state, by what you can actually do about it.

    Five buckets, because "not claimed" was hiding three different situations and
    only one of them is a click:

        missing    no page at all -- visit it while logged in
        unclaimed  page exists, your name is in the author list, no user linked
        pending    you are linked but status is not yet verified -- wait, do not redo
        blocked    no author string resembles your name, so there is no claim control
                   to press: the upstream metadata is wrong and that is the real task
        claimed    done

    `requested` (data/overrides.yaml -> hf_claim_requested) is the one thing here
    that cannot be read from outside. Hugging Face only exposes the `user` link once
    moderation has granted the claim, so a request you submitted an hour ago is
    indistinguishable over the API from one you never made -- and the worklist then
    tells you to go and do it again. Which action you took is a durable fact about
    you, not observed state, so it is declared in overrides.yaml and the audit moves
    those pages to `pending`.

    Splitting out `pending` stops the worklist from re-listing claims already in
    moderation, which reads as "your click did not work". Splitting out `blocked`
    matters more: those pages cannot be claimed at all, so leaving them among the
    clicks makes the list end in three items that never complete.

    Deliberately live rather than read from papers.yaml. This list is worked by
    hand over days, and a stale copy sends you back to pages you already did --
    which is exactly what happened the first time.
    """
    me = me.lower()
    out = {k: [] for k in ("missing", "unclaimed", "pending", "blocked", "claimed")}
    for p in papers:
        j = get_json(f"https://huggingface.co/api/papers/{p['arxiv']}", retries=1)
        if j is None:
            out["missing"].append(p)
            continue
        authors = j.get("authors") or []
        mine = [a for a in authors if (a.get("user") or {}).get("user", "").lower() == me]
        if mine:
            done = any((a.get("status") or "") in HF_CLAIM_DONE for a in mine)
            out["claimed" if done else "pending"].append(p)
        elif any(name_match(a.get("name") or "", variants) for a in authors):
            out["pending" if str(p["arxiv"]) in requested
                else "unclaimed"].append(p)
        else:
            p = dict(p)
            p["hf_authors"] = [a.get("name") or "" for a in authors]
            out["blocked"].append(p)
        time.sleep(0.2)
    return out


def hf_worklist_file(st: dict) -> str:
    """Every Hugging Face bucket, in full, committed so it diffs between runs.

    All buckets in one file and in full: the previous version printed a truncated
    top-12, which reads as "that is all of it".

    Only ever called with live state. Writing a cached view into the same file would
    quietly replace checked numbers with older ones, and the file gives no hint which
    it is holding.
    """
    def rows(group, task=True):
        # A checkbox is an instruction, so only the buckets you can act on get one. The
        # pending bucket said "Nothing to do" in its own prose and then printed twelve
        # checkboxes under it, which is the file arguing with itself -- and it put two
        # items on the open-task count that no amount of work could close.
        box = "- [ ] " if task else "- "
        return [f"{box}{p.get('citations') or 0:>4} cites — "
                f"<https://hf.co/papers/{p['arxiv']}> — "
                f"{(p.get('title_display') or p['title'])[:70]}" for p in group]

    n = {k: len(v) for k, v in st.items()}
    path = os.path.join(TASKS, "hf_worklist.md")
    L = ["# Hugging Face paper pages", "",
         "Live as of the last `python scripts/audit_identity.py` (`--no-names` skips "
         "the slow half): "
         f"**{n['claimed']} claimed**, **{n['pending']} pending**, "
         f"**{n['unclaimed']} to claim**, **{n['missing']} to index**, "
         f"**{n['blocked']} blocked upstream**.", "",
         "Indexing and claiming both need a logged-in browser. An unauthenticated visit",
         "to a paper URL returns 404 and creates nothing (verified on 50 papers — 0",
         "created), which is why this is a list and not a script.", ""]
    if n["missing"]:
        L += [f"## Index — {n['missing']} papers with no page yet", "",
              "Log in to Hugging Face, then open each link. The visit is what creates",
              "the page. Nothing else to fill in.", ""] + rows(st["missing"]) + [""]
    if n["unclaimed"]:
        L += [f"## Claim — {n['unclaimed']} pages that exist but are not linked to you", "",
              "On each page: find your name in the author list and use the claim control",
              "next to it. This is what joins the paper to your HF profile, and what",
              "makes your models and datasets cross-list on it.", ""]
        L += rows(st["unclaimed"]) + [""]
    if n["pending"]:
        L += [f"## Pending — {n['pending']} claims in moderation", "",
              "Your user is linked but the status is not verified yet. Nothing to do;",
              "listed only so a re-run does not look like the claim failed.", "",
              "If one of these is still here weeks from now the claim was probably",
              "dropped rather than queued: open the page, and if your name is no longer",
              "linked, claim it again.", ""]
        L += rows(st["pending"], task=False) + [""]
    if n["blocked"]:
        L += [f"## Blocked upstream — {n['blocked']} pages you cannot claim", "",
              "No author string on these pages resembles your name, so there is no claim",
              "control to press. Hugging Face copies its author list from arXiv, so the",
              "fix is on arXiv, not here — see `arxiv_name_fixes.md`. Once the arXiv",
              "metadata is corrected these move to the claim list on a later run.", ""]
        for p in st["blocked"]:
            # No checkbox for the same reason as `pending`: there is no control on the
            # page to press, so the action is the arXiv one and lives in that file.
            L.append(f"- <https://hf.co/papers/{p['arxiv']}> — "
                     f"{(p.get('title_display') or p['title'])[:60]}")
            L.append(f"      HF lists: {', '.join(p.get('hf_authors') or [])[:150]}")
        L.append("")
    with open(path, "w") as f:
        f.write("\n".join(L) + "\n")
    return path


def wikidata_followup_file(g: dict, cfg, cov: dict, qs_path: str | None) -> str:
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

    edu = [f"{e.get('institution')}" + (f" ({e['degree']})" if e.get("degree") else "")
           for e in (ident.get("education") or [])] or ["your PhD institution"]
    L += ["## Worth adding while you are in the editor", "",
          "Not identifiers — statements that help a disambiguator separate you from a",
          "namesake, which is the whole job of this item.", "",
          "| property | | value | why |",
          "|---|---|---|---|",
          f"| given name | `P735` | {given} | lets a query match the name parts "
          "separately from the label string |",
          f"| family name | `P734` | {family} | same |",
          f"| educated at | `P69` | {'; '.join(edu)} | the single strongest "
          "disambiguating fact about a researcher |",
          "| employer | `P108` | with *start time* qualifiers | turns flat "
          "affiliations into a career an engine can order |",
          "",
          "`educated at` is for degree-granting study only. A postdoc goes in `employer`",
          "(`P108`), optionally qualified with *position held* (`P39`) = `Q1125292`",
          "(postdoctoral researcher) — no degree was awarded, and the institution was",
          "paying you. The test is just: was a degree awarded?", "",
          "Skip date of birth, sex or gender, and image. None of them help retrieval",
          "and all of them are personal data you would then be maintaining.", ""]

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
    for p, qid in cov["present"]:
        L.append(f"- [{qid}](https://www.wikidata.org/wiki/{qid}) — "
                 f"{(p.get('title_display') or p['title'])[:70]}")
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
        L += ["**Creating the missing items — optional, and read this first.**", "",
              f"`{os.path.relpath(qs_path, ROOT)}` holds a QuickStatements batch for",
              f"{n_new} papers: title, publication date, DOI or arXiv id, and the author",
              f"list with you as `author` → {q} and co-authors as `author name string`",
              "with position qualifiers. Only papers carrying a DOI or arXiv id are",
              "included — a resolvable identifier is what puts a publication item",
              "clearly in scope, and it is the key the batch was deduplicated on.", "",
              "Honest accounting before you run it: this buys a Scholia profile, a",
              "SPARQL-answerable corpus, and an authorship graph — real, but a weaker",
              "surface than arXiv, ORCID or your own pages. It costs an autoconfirmed",
              "account, a batch review, and permanent public items. Items created here",
              "are much harder to clean up than a page in this repo. Run it in",
              "QuickStatements with the batch preview open, on the first ten rows,",
              "before releasing the rest.", "",
              "One gap the dedup cannot cover: a paper item that exists with neither a",
              "DOI nor an arXiv id would not have matched, so it could be recreated.",
              "Searching the exact title in Wikidata's own search box is the check.", ""]
    return L


def _write_followup(L: list[str]) -> str:
    """Kept as its own function only so the two halves above can each end in a return."""

    path = os.path.join(TASKS, "wikidata_followup.md")
    with open(path, "w") as f:
        f.write("\n".join(L) + "\n")
    return path


def orcid_strays(orc: dict, papers) -> list[tuple]:
    """Works on the ORCID record that are not in your corpus.

    A bulk BibTeX import is one click; removing 13 works is 13. That asymmetry is why
    this check exists rather than being left to care at import time. The specific
    failure it caught: the bibliography we import from is a CV bibliography, so it
    also holds the works the CV *cites*, and the record ended up asserting authorship
    of "Attention is all you need". Nothing on ORCID will ever flag that -- the record
    cannot know what you meant to claim -- and every service that trusts ORCID
    (Semantic Scholar, OpenAlex, publisher lookups) reads it as your claim.

    Each stray is tagged `confirmed` when the collector also rejected it on author
    name, `declined` when `data/declines.yaml` says its absence from the bibliography
    was a decision, and `unknown` otherwise -- a title we simply do not have, which is
    as likely to be a real paper missing from the bibliography as an error.

    The `declined` tag is not a shade of `unknown`; it is its opposite. "Check before
    deleting" over a work whose absence *is* the decision asks the reader to redo the
    thinking that produced the decline, and the live case is a competition report the
    author ruled out on purpose -- a legitimate ORCID entry that this corpus will never
    hold, so nothing but a recorded decision can ever stop the question coming back.

    Matching is by identifier first and title only as a fallback, because titles drift
    and identifiers do not. Every "unknown" this check ever reported turned out to be
    a title-drift artefact: a paper retitled between preprint and proceedings, or a
    subtitle dropped by whoever typed the entry. Three works, all the author's own, all
    already in the corpus -- and the file said *check before deleting* about papers
    there was never any reason to doubt.

    Title matching runs in three widening passes, and the third exists because the first
    two share a blind spot: both read word *order* as content. "Tie the KnOTS: Model
    Merging with SVD" against a corpus holding "Model merging with SVD to tie the Knots"
    is not an equal string, and once the words move across the colon neither string
    contains the other either -- so the widest check on offer still called a paper of the
    author's own a work it could not place. The third pass compares content-word sets
    (`title_tokens`), which is exactly and only insensitive to arrangement.

    Returns `(strays, duplicate_groups, matched_slugs, misfiled, merged_versions)`.

    `duplicate_groups` and `merged_versions` are both "this paper appears more than once"
    and they are split because only one of them is a problem. Two works in *different*
    ORCID groups show on the profile as two works and every service counting output counts
    both; two works in the *same* group are one profile entry with "N versions", which
    ORCID has already unified and nothing downstream double-counts.

    `misfiled` is the class that hid behind all of this: a work whose identifier belongs
    to a *different* paper. ORCID groups on shared identifiers, so such a work is filed
    inside another paper's group, and reading one title per group meant its own title was
    never compared to anything. The absorbed paper then reports as missing from a record
    that has held it all along — and the fix the report offered, adding it, would have
    produced a second copy. It is detected by disagreement: the identifier resolves to
    one corpus paper while the title matches another *exactly*. Nothing looser counts,
    because looser disagreement is the ordinary preprint/proceedings drift that
    identifier-first matching exists to survive.

    `duplicate_groups` is what identifier matching exposes on the way: two ORCID work
    groups resolving to one corpus paper, which is the same paper listed twice. ORCID
    groups works that share an identifier, so a record holding both the publisher DOI
    and arXiv's `10.48550/arXiv.<id>` DOI for one paper gets two groups, not one.
    `orcid_import.bib` fills missing DOIs from arXiv, so importing it over a record
    that already had publisher DOIs is exactly how this happens.

    `matched_slugs` is the direction nothing else measures: which of your papers the
    record does *not* hold. A works count cannot answer that -- 105 works against a
    117-paper corpus can be twelve papers missing, or sixteen missing and four listed
    twice, and those are different fixes.
    """
    ARXIV_DOI = re.compile(r"10\.48550/arxiv\.(.+)$", re.I)
    by_doi = {p["doi"].lower(): p for p in papers if p.get("doi")}
    by_arxiv = {str(p["arxiv"]).lower(): p for p in papers if p.get("arxiv")}
    by_title = {norm_title(p["title"]): p for p in papers}
    # Same corpus keyed by content-word set, for the reordering fallback below. A set two
    # corpus papers share is dropped rather than resolved: which one an ORCID work meant
    # would be a guess, and the guess would be invisible -- the work vanishes from this
    # report either way, so a wrong pick reads exactly like a right one. Four tokens
    # minimum, because the shorter the set the cheaper an accidental collision.
    _tok = {}
    for p in papers:
        t = title_tokens(p["title"])
        if len(t) >= 4:
            _tok.setdefault(t, []).append(p)
    by_tokens = {t: v[0] for t, v in _tok.items() if len(v) == 1}
    rejected = {}
    try:
        with open(os.path.join(BUILD, "not_mine.json")) as f:
            rejected = {norm_title(x["title"]): x for x in json.load(f)}
    except (OSError, ValueError):
        pass

    def by_ids(ids):
        for typ, val in ids:
            v = val.lower()
            if typ == "doi":
                m = ARXIV_DOI.match(v)
                if m and m.group(1) in by_arxiv:
                    return by_arxiv[m.group(1)]
                if v in by_doi:
                    return by_doi[v]
            elif typ == "arxiv" and v.lstrip("arxiv:") in by_arxiv:
                return by_arxiv[v.lstrip("arxiv:")]
        return None

    def by_titles(title):
        """The corpus paper this title names, and how sure the match is.

        The confidence matters to one caller only, and only for the exact case: an
        identifier disagreeing with an *exact* title is a mistyped identifier, while an
        identifier disagreeing with a looser match is just title drift.
        """
        n = norm_title(title)
        if n in by_title:
            return by_title[n], "exact"
        # Only in the containment direction: an ORCID title that is a prefix or suffix
        # of a corpus title is a dropped subtitle, not a new paper. Guarded by length so
        # a short title cannot swallow a long unrelated one.
        if len(n) >= 25:
            for cn, p in by_title.items():
                if n in cn or cn in n:
                    return p, "loose"
        # Rearranged, which both checks above read as a different paper: the string is
        # not equal and, once the words move across the colon, neither title contains
        # the other. Live case, and the one that motivated this -- ORCID holds "Tie the
        # KnOTS: Model Merging with SVD" for the corpus's "Model merging with SVD to tie
        # the Knots", and the audit called it a work it could not place.
        p = by_tokens.get(title_tokens(title))
        return (p, "loose") if p else (None, None)

    out, seen, misfiled = [], {}, []
    for title, put, ids, gidx in orc.get("work_titles") or []:
        hid = by_ids(ids)
        tid, how = by_titles(title)
        # The identifier normally wins -- titles drift between preprint and proceedings
        # and identifiers do not. The exception is the whole reason this branch exists: an
        # identifier pointing at paper A while the title is character-for-character paper
        # B is not drift, it is the wrong DOI typed into the work. Trusting the id there
        # silently merges two different papers, and the *absorbed* one then reports as
        # missing from a record that holds it. Only `exact` overrides, because a loose
        # match is exactly the drift the identifier is there to survive.
        if hid is not None and tid is not None and hid["slug"] != tid["slug"]:
            if how == "exact":
                misfiled.append((title, put, ids, tid, hid))
                hit = tid
            else:
                hit = hid
        else:
            hit = hid or tid
        if hit is None:
            # `confirmed` outranks `declined`: "no form of your name is on this paper"
            # is a stronger statement than "not going in the bibliography", and it is
            # the one that ends in a deletion.
            out.append((title, put,
                        "confirmed" if norm_title(title) in rejected
                        else "declined" if declined(title) else "unknown"))
        else:
            seen.setdefault(hit["slug"], []).append((title, put, ids, gidx))
    # Split on group membership, not on count. `dups` is the profile actually showing a
    # paper twice; `versions` is one entry ORCID has already folded, which is worth a
    # mention and is not worth a **fix**.
    dups = {s: v for s, v in seen.items() if len({g for *_r, g in v}) > 1}
    versions = {s: v for s, v in seen.items()
                if s not in dups and len(v) > 1}
    return out, dups, set(seen), misfiled, versions


def orcid_missing_files(missing: list[dict], orcid: str) -> list[str]:
    """tasks/orcid_missing.md + .bib — papers of yours the ORCID record does not hold.

    Two files because there are two ways to fix it and they suit different sizes: a
    BibTeX upload is one action for the whole set, and a DOI at a time is what you want
    when three are left. The .bib is the same shape as `orcid_import.bib` but narrowed
    to what is actually absent, which matters — re-uploading the full import is what
    created the duplicate groups this audit now reports.
    """
    md = [f"# ORCID is missing {len(missing)} of your papers", "",
          "Regenerated live by `python scripts/audit_identity.py`. Matched by DOI and",
          "arXiv id against the work groups on the record, so this is absence and not a",
          "title-matching guess.", "",
          "**Fix it with the narrowed BibTeX, not the full import.** "
          "`tasks/orcid_missing.bib`",
          "holds exactly these entries. Uploading `orcid_import.bib` again would re-add",
          "the works already there under arXiv DOIs, and ORCID cannot group a work",
          "carrying only the arXiv DOI with the same work carrying only the publisher",
          "DOI — that is where the *listed twice* entries in `orcid_remove.md` came from.",
          "",
          f"On <https://orcid.org/my-orcid#works>: *Works* → **+ Add** → *Add BibTeX* →",
          "choose `tasks/orcid_missing.bib` → review the list → *Add all*.", "",
          "| # | cites | title | identifier |", "|---|---|---|---|"]
    for i, p in enumerate(missing, 1):
        # paper_doi, not p["doi"]: it fills a missing DOI from the arXiv id, and it is
        # what the .bib next to this table emits. Two columns disagreeing about a
        # paper's identifier is how you end up checking the wrong one on ORCID.
        ident = paper_doi(p) or "— none —"
        md.append(f"| {i} | {p.get('citations') or 0} | "
                  f"{(p.get('title_display') or p['title'])[:64]} | `{ident}` |")
    noid = [p for p in missing if not paper_doi(p)]
    if noid:
        md += ["",
               f"**{len(noid)} of these carry no identifier at all.** Those are the entries",
               "where a BibTeX import genuinely can duplicate later, because ORCID has",
               "nothing to group them on. Add them last, or leave them out — a work with no",
               "DOI and no arXiv id is also a work nothing downstream can resolve.", ""]
    md += ["", "Then re-run the audit: the *ORCID holds your papers* row is the check.", ""]
    bib = [(p.get("bibtex") or synth_bibtex(p)).strip() for p in missing]
    out = []
    for name, body in (("orcid_missing.md", "\n".join(md) + "\n"),
                       ("orcid_missing.bib", "\n\n".join(bib) + "\n" if bib else "")):
        path = os.path.join(TASKS, name)
        with open(path, "w") as f:
            f.write(body)
        out.append(path)
    return out


def orcid_remove_file(strays: list[tuple], dups: dict, papers, cfg) -> str:
    """tasks/orcid_remove.md — works to delete from the ORCID record, with put-codes."""
    conf = [s for s in strays if s[2] == "confirmed"]
    unk = [s for s in strays if s[2] == "unknown"]
    dec = [s for s in strays if s[2] == "declined"]
    L = ["# ORCID: works to remove", "",
         "Works on the record that are not in `data/papers.yaml`. Regenerated live by",
         "`python scripts/audit_identity.py`; the file is empty when the record is clean.",
         "",
         "**How this happens.** The bibliography this tool reads is a CV bibliography, so",
         "it contains the works the CV *cites* as well as the works it lists. Those were",
         "included in the bulk import before the collector learned to check author names.",
         "The import is one click and the removal is one click *per work*, which is the",
         "whole reason this page exists rather than the check being left to import time.",
         "",
         "**Why it matters more than it looks.** ORCID is not a private list. Semantic",
         "Scholar, OpenAlex, Crossref and publisher submission systems read it as your",
         "assertion of authorship, and a claim on a famous paper is the kind of error",
         "someone eventually notices and reads uncharitably.", ""]
    if conf:
        L += [f"## Confirmed not yours ({len(conf)})", "",
              "The collector rejected each of these because no form of your name appears",
              "in the author list from any source. Delete them.", "",
              "On <https://orcid.org/my-orcid#works>: *Works* → find the title → the",
              "**⋮ / Actions** menu on that entry → *Delete*. There is no multi-select, so",
              "it is one at a time. Sorting by *Date added* groups the whole import",
              "together, which makes them faster to find than searching by title.", "",
              "| # | title | ORCID put-code |", "|---|---|---|"]
        L += [f"| {i} | {t[:78]} | `{p}` |" for i, (t, p, _) in enumerate(conf, 1)]
        L += ["", "The put-code is the record's internal id, shown in the URL when you open a",
              "work. It is here so you can confirm you are deleting the right entry when two",
              "titles are similar.", ""]
    if unk:
        L += [f"## On ORCID, unknown to us ({len(unk)})", "",
              "Not necessarily wrong — a paper missing from the bibliography looks exactly",
              "like this. **Check before deleting.** If it is yours, the fix is upstream in",
              "the bibliography, not here.",
              "",
              "These are matched by identifier first (the group's DOI or arXiv id), then by",
              "title, then by the title's content words with the order discarded — so a paper",
              "retitled between preprint and proceedings, or rearranged around its colon, no",
              "longer lands here. A work reaching this section carries *no* identifier ORCID",
              "could group on — which is also why nothing else can place it.", ""]
        L += [f"- {t}  (`{p}`)" for t, p, _ in unk]
        L += [""]
    if dec:
        # Plain bullets and its own heading, below the section that asks a question. These
        # are not candidates for anything: they are on ORCID legitimately and absent from
        # the corpus on purpose, so the only honest instruction is "nothing".
        L += [f"## On ORCID, deliberately not in the bibliography ({len(dec)})", "",
              "**Nothing to do.** Each of these is a work you decided not to add to the",
              "source bibliography, so it can never match a corpus paper and would sit under",
              "*check before deleting* forever -- asking you to redo the thinking that",
              "produced the decision. The decision itself is the line quoted after each one,",
              "in [`data/declines.yaml`](../data/declines.yaml); delete that line and the work",
              "moves back up to the section above.", "",
              "Leave them on ORCID. A work being outside a CV bibliography says nothing about",
              "whether it is yours, and these are.", ""]
        L += [f"- {t}  (`{p}`) — declined as `{declined(t)}`" for t, p, _ in dec]
        L += [""]
    if dups:
        by_slug = {p["slug"]: p for p in papers}
        L += [f"## Listed twice ({plural(len(dups), 'paper')}, "
              f"{plural(sum(len(v) for v in dups.values()), 'entry', 'entries')})",
              "",
              "One paper, two ORCID works. ORCID groups works that share an external",
              "identifier; these pairs share none, because one entry carries the publisher",
              "DOI and the other carries arXiv's `10.48550/arXiv.<id>` DOI. The titles",
              "differ too — usually a preprint title that changed on acceptance, or a",
              "subtitle typed into one entry and not the other — so they do not even look",
              "like the same paper on the page.",
              "",
              "**Merge them; do not delete either.** The two entries carry different",
              "titles, and both titles are real: one is what the paper was called as a",
              "preprint and the other is what it was called on acceptance. Deleting the",
              "preprint entry throws away a title that is cited in the wild and an",
              "identifier that resolves — so the merge keeps more than it costs, and the",
              "extra work is one field.",
              "",
              "ORCID has no merge button, and does not need one: it groups works that share",
              "an external identifier. Put the *other* entry's DOI on the entry you keep",
              "and the pair folds into a single work with a version selector, both titles",
              "and both DOIs intact. Nothing is deleted, so nothing can be lost by getting",
              "it wrong.",
              "",
              "For each row: open the **keep** entry (its put-code is the last path segment",
              "at <https://orcid.org/my-orcid#works>), then *Edit* → **+ Add identifier** →",
              "type `doi` → paste the value in the last column → *Save*. The two entries",
              "collapse on the next page load.", "",
              "| paper | keep (published, has the venue) | folds in | DOI to add to the keep entry |",
              "|---|---|---|---|"]
        arx = re.compile(r"^10\.48550/arxiv\.", re.I)

        def doi_of(ids):
            return next((v for t, v in ids if t == "doi"), None)

        for slug, entries in dups.items():
            t = (by_slug.get(slug) or {}).get("title", slug)[:44]
            # The preprint entry is the one whose DOI is arXiv's DataCite prefix, which
            # is what makes this generatable rather than a judgement: the published
            # entry is simply the other one, and its DOI is the venue's.
            pre = [e for e in entries if arx.match(doi_of(e[2]) or "")]
            pub = [e for e in entries if e not in pre]
            if len(pre) == 1 and len(pub) == 1:
                L.append(f"| {t} | `{pub[0][1]}` — {pub[0][0][:30]} | "
                         f"`{pre[0][1]}` — {pre[0][0][:30]} | `{doi_of(pre[0][2])}` |")
            else:
                # No arXiv DOI, or more than two entries: say so rather than guess which
                # to keep. Either way the fix is the same shape, one identifier.
                L.append(f"| {t} | " + " | ".join(f"`{p}` — {ti[:28]} ({doi_of(i) or 'no DOI'})"
                                                  for ti, p, i, _g in entries)
                         + " | *pick the entry with the venue; add the other's DOI* |")
        L += ["", "If you would rather have one entry than a grouped pair, delete the",
              "**folds in** one instead — *Works* → the entry → **⋮ / Actions** →",
              "*Delete*. Same number of clicks, and the preprint title stops being",
              "findable on your record.", ""]
    if not strays and not dups:
        L += ["Nothing to remove: every public work on the record is in the corpus, and",
              "none is listed twice.", ""]
    return "\n".join(L)


def arxiv_author_strings(ids: list[str], batch: int = 50) -> dict[str, list[str]]:
    """arXiv's own author list for each id, batched.

    The API takes up to 100 ids per `id_list` query, so the whole corpus is two or
    three requests rather than one per paper -- which matters because arXiv asks for
    a 3-second gap between calls, and 105 sequential requests would be five minutes.
    """
    out: dict[str, list[str]] = {}
    for i in range(0, len(ids), batch):
        chunk = ids[i:i + batch]
        raw = get("https://export.arxiv.org/api/query?id_list="
                  f"{','.join(chunk)}&max_results={len(chunk)}", retries=3)
        if not raw:
            continue
        try:
            root = ET.fromstring(raw)
        except ET.ParseError:
            continue
        for e in root.findall("a:entry", ATOM):
            m = _ABS.search(e.findtext("a:id", "", ATOM) or "")
            if not m:
                continue
            out[m.group(1)] = [a.findtext("a:name", "", ATOM) or ""
                               for a in e.findall("a:author", ATOM)]
        time.sleep(3)
    return out


def arxiv_name_file(papers, variants) -> tuple[str, list, list]:
    """Papers whose arXiv author list misspells or omits your name.

    Worth a dedicated check because arXiv metadata is *upstream* of nearly every
    index in this repo: Hugging Face, Semantic Scholar, OpenAlex and Google Scholar
    all read it. A one-character typo there does not degrade gracefully -- it creates
    a second author who owns that paper's citations and cannot be merged with you,
    and no amount of work on the pages downstream repairs it.

    Two failure modes, different fixes, so they are reported separately:
      typo    a near-miss author string -- correct it in the arXiv metadata
      absent  no resembling string at all -- the submitter left you off the paper
    """
    found = arxiv_author_strings([p["arxiv"] for p in papers])
    typo, absent = [], []
    for p in papers:
        names = found.get(p["arxiv"])
        if not names:
            continue  # not retrievable this run; silence beats a false accusation
        kinds = {name_match(n, variants): n for n in names}
        if "exact" in kinds:
            continue
        p = dict(p)
        p["arxiv_authors"] = names
        if "near" in kinds:
            p["near_miss"] = kinds["near"]
            typo.append(p)
        else:
            absent.append(p)

    path = os.path.join(TASKS, "arxiv_name_fixes.md")
    L = ["# arXiv author-name problems", "",
         f"Checked **{len(found)}** arXiv records against your name variants: "
         f"**{len(typo)} misspelled**, **{len(absent)} missing you entirely**.", "",
         "This is upstream of everything else. Hugging Face, Semantic Scholar, OpenAlex",
         "and Google Scholar all build author identity from arXiv metadata, so a name",
         "that is wrong here is wrong in all of them at once — and it does not read as a",
         "typo to them, it reads as a different person, who then owns that paper's",
         "citations and cannot be merged into you.", ""]
    if typo:
        L += [f"## Misspelled — {len(typo)}", "",
              "Fix the author list in the arXiv metadata. You must own the paper first",
              "(`arxiv_ownership.md`); metadata changes go through *Update this article*",
              "on your submission page. A name correction is a metadata edit, not a new",
              "version of the paper.", "",
              "Note the ordering trap: <https://arxiv.org/auth/request-ownership> matches",
              "your name against the author list, and on these papers that list is the",
              "thing that is wrong — so the request can bounce. If it does, ask the",
              "submitting co-author for the paper password instead",
              "(<https://arxiv.org/auth/need-paper-password>), which does not name-match.",
              ""]
        for p in typo:
            L.append(f"- [ ] [`{p['arxiv']}`](https://arxiv.org/abs/{p['arxiv']}) — "
                     f"reads **{p['near_miss']}** — "
                     f"{(p.get('title_display') or p['title'])[:60]}")
        L.append("")
    if absent:
        L += [f"## Missing you entirely — {len(absent)}", "",
              "arXiv's author list for these does not contain anything close to your",
              "name. Either the submitter left you off, or the bibliography entry points",
              "at the wrong arXiv id — check which before asking anyone to change",
              "anything. If the paper is genuinely yours, only the submitter can add you;",
              "an ownership request will fail the name match.", ""]
        for p in absent:
            L.append(f"- [ ] [`{p['arxiv']}`](https://arxiv.org/abs/{p['arxiv']}) — "
                     f"{(p.get('title_display') or p['title'])[:60]}")
            L.append(f"      arXiv lists: {', '.join(p['arxiv_authors'])[:150]}")
        L.append("")
    if not (typo or absent):
        L += ["Nothing to fix — every retrieved record names you exactly.", ""]
    with open(path, "w") as f:
        f.write("\n".join(L) + "\n")
    return path, typo, absent


def _rows(group, extra=lambda p: "") -> list[str]:
    return [f"- [ ] {p.get('citations') or 0:>4} cites — "
            f"[`{p['arxiv']}`](https://arxiv.org/abs/{p['arxiv']}) "
            f"{(p.get('title_display') or p['title'])[:72]}{extra(p)}"
            for p in group]


def arxiv_ownership_file(cfg, papers, registered: set[str] | None) -> tuple[str, int]:
    ident = cfg["identity"]
    path = os.path.join(TASKS, "arxiv_ownership.md")
    if registered is None:
        body = ["# arXiv ownership", "",
                f"`https://arxiv.org/a/{ident['orcid']}` does not resolve yet. Link your",
                "arXiv account to your ORCID first: <https://arxiv.org/user/confirm_orcid_id>",
                "then re-run `python scripts/audit_identity.py`."]
        with open(path, "w") as f:
            f.write("\n".join(body) + "\n")
        return path, 0

    seen, gap = set(), []
    for p in sorted(papers, key=lambda p: -(p.get("citations") or 0)):
        a = p["arxiv"]
        if a in seen:
            continue
        seen.add(a)
        if a not in registered:
            gap.append(p)
    L = [f"# arXiv: claim ownership of {len(gap)} papers", "",
         f"Registered as author on **{len(registered)}** of **{len(seen)}** arXiv papers.",
         f"Public list: <https://arxiv.org/a/{ident['orcid']}>", "",
         "## Why this is first, not last",
         "",
         "Two things depend on it, and both are invisible until you look:",
         "",
         "1. **You cannot add a journal-ref or DOI to a paper you do not own.** The",
         "   journal-ref list further down `WORKLIST.md` is *blocked* on this for any",
         "   paper here — and journal-ref is what Google Scholar matches citations on.",
         f"2. `https://arxiv.org/a/{ident['orcid']}` is a public, indexable publication",
         "   list on arxiv.org, with an Atom feed and an embeddable widget. Right now it",
         "   shows less than half your corpus, on a domain with far more crawl authority",
         "   than any personal site.",
         "",
         "arXiv's own January 2026 endorsement-policy post recommends claiming ownership",
         "of every paper you co-authored, so this is the documented intent, not a hack.",
         "",
         "## Two routes",
         "",
         "**With the paper password (instant).** The password is in the submitter's",
         "acceptance email. Ask the submitting co-author for it, then enter the arXiv id",
         "and password at <https://arxiv.org/auth/need-paper-password>.",
         "",
         "**Without it (a couple of days).** <https://arxiv.org/auth/request-ownership>",
         "— arXiv staff verify manually. No co-author involvement needed, so for a long",
         "tail of old papers this is the path of least effort: submit them in a batch and",
         "forget about it.",
         "",
         "If a paper is already in your owned list but you are not listed as an author,",
         "that is a different form: <https://arxiv.org/auth/change-author-status>.",
         "",
         "For your own future submissions: share the paper password with every co-author",
         "in the announcement email. It costs nothing and saves them this page.",
         "",
         f"## The {len(gap)} papers, citation-ordered", ""]
    L += _rows(gap)
    with open(path, "w") as f:
        f.write("\n".join(L) + "\n")
    return path, len(gap)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-hf", action="store_true",
                    help="skip the per-paper Hugging Face checks (the slow part)")
    ap.add_argument("--no-names", action="store_true",
                    help="skip the arXiv author-name check (needs ~3s per 50 papers)")
    args = ap.parse_args()
    cfg = load_config()
    ident, ids = cfg["identity"], cfg["ids"]
    papers = (read_yaml(os.path.join(DATA, "papers.yaml")) or {})["papers"]
    # One row per arXiv id, not per record: a few papers legitimately carry two
    # records (a retitled version), and checking the same page twice reads as two
    # separate jobs on a worklist worked by hand.
    ax, seen = [], set()
    for p in sorted(papers, key=lambda p: -(p.get("citations") or 0)):
        if p.get("arxiv") and p["arxiv"] not in seen:
            seen.add(p["arxiv"])
            ax.append(p)
    os.makedirs(TASKS, exist_ok=True)

    print("reading ORCID ...", flush=True)
    orc = orcid_public(ident["orcid"])
    print("reading arXiv authority records ...", flush=True)
    reg = arxiv_registered(ident["orcid"])
    print("searching Wikidata by identifier ...", flush=True)
    wd = wikidata_item(cfg) or ids.get("wikidata")
    wd_path, wd_gaps, wd_cov, wd_qs = None, {}, {}, None
    if wd:
        wd_gaps = wikidata_gaps(wd, cfg)
        print("measuring Wikidata paper coverage ...", flush=True)
        wd_cov = wikidata_paper_coverage(papers)
        wd_qs, _ = wikidata_papers_qs(wd_cov, cfg)
        if wd_gaps:
            wd_path = wikidata_followup_file(wd_gaps, cfg, wd_cov, wd_qs)
    # --no-hf means "leave the HF artifacts alone", not "regenerate them from cache".
    # Writing the cached view here would silently overwrite a freshly-checked
    # worklist with older numbers, which is worse than not writing at all.
    variants = [ident["name"]] + list(ident.get("name_variants") or [])
    hf = None
    hf_path = None
    if not args.no_hf:
        print(f"checking {len(ax)} Hugging Face paper pages ...", flush=True)
        requested = {str(a) for a in
                     ((read_yaml(os.path.join(DATA, "overrides.yaml")) or {})
                      .get("hf_claim_requested") or [])}
        hf = hf_state(ax, ids["huggingface"], variants, requested)
        hf_path = hf_worklist_file(hf)

    name_path = n_typo = n_absent = None
    if not args.no_names:
        print("checking arXiv author lists for your name ...", flush=True)
        name_path, n_typo, n_absent = arxiv_name_file(ax, variants)

    ax_path, n_gap = arxiv_ownership_file(cfg, ax, reg)
    # Papers arXiv says you own that the bibliography does not mention. Usually a new
    # paper the .bib has not caught up with, occasionally an ownership claim on
    # someone else's paper -- either way it is the one direction of this diff that
    # nothing else in the repo would ever surface.
    stray = sorted((reg or set()) - {p["arxiv"] for p in ax})

    # --- the audit report -------------------------------------------------------
    canon = ident["canonical_url"].rstrip("/")
    url_vals = [u for _, u in orc["urls"] if u]
    has_canon = any(canon in (u or "").rstrip("/") for u in url_vals)
    missing_variants = [v for v in ident["name_variants"]
                        if v != ident["name"] and v not in orc["other_names"]]
    # Other personal pages count as satisfied when *listed*, not when removed: a
    # second page declared to be the same person fuses with the canonical one, and
    # only an undeclared one competes with it.
    other_pages = [u for u in (ident.get("other_pages") or [])
                   if not any(u.rstrip("/") in (v or "").rstrip("/") for v in url_vals)]
    want_kw = [k for k in (ident.get("keywords") or [])
               if k.lower() not in {k2.lower() for k2 in orc["keywords"]}]

    o_stray, o_dups, o_have, o_misfiled, o_vers = orcid_strays(orc, papers)
    o_conf = [s for s in o_stray if s[2] == "confirmed"]
    o_unk = [s for s in o_stray if s[2] == "unknown"]
    # Papers of yours the record does not hold. Sorted by citations, because the cost of
    # a missing work is proportional to how often something looks the paper up.
    o_missing = sorted((p for p in papers if p["slug"] not in o_have),
                       key=lambda p: -(p.get("citations") or 0))

    # Auto-update evidence, and affiliations the record does not yet state.
    auto_src = {k: v for k, v in (orc["work_sources"] or {}).items()
                if any(w in k.lower() for w in ("crossref", "datacite"))}
    orc_orgs = [(r["org"] or "") for r in orc["employment_rows"]]
    missing_empl = [org_name(a) for a in ident["affiliations"]
                    if not any(_org_match(org_name(a), o) for o in orc_orgs)]
    missing_edu = [e["institution"] for e in (ident.get("education") or [])
                   if not any(_org_match(e["institution"], r["org"] or "")
                              for r in orc["education_rows"])]
    # An education row with no role-title states an institution but not a degree, and
    # one with no end year still reads as *enrolled* -- which, next to a postdoc
    # employment, is a record contradicting itself about what you are.
    #
    # Split by who asserted it, because the fix is different and only one of the two is
    # a fix at all. A self-asserted row is editable in place. An institution-asserted
    # row is not: ORCID shows no *Edit* control on it, only *Delete*, so "add the degree
    # to the Role field" is an instruction that cannot be followed. Those are reported
    # separately, as a decision (leave it, or delete and re-add your own) rather than as
    # an open task -- and an institution-asserted row is *better* evidence than anything
    # you could type, which is the argument for leaving it alone.
    def _incomplete(r):
        return not r["role"] or not r["end"]

    def _theirs(r):
        s = (r.get("source") or "").lower()
        return bool(s) and s != (ident["name"] or "").lower()

    edu_open = [r for r in orc["education_rows"] if _incomplete(r) and not _theirs(r)]
    edu_theirs = [r for r in orc["education_rows"] if _incomplete(r) and _theirs(r)]

    def status(ok: bool) -> str:
        return "ok" if ok else "**fix**"

    L = ["# Identity audit", "",
         "Live read of the surfaces you do not control. Regenerate with",
         "`python scripts/audit_identity.py`. Every row is checkable without a login,",
         "which is why it can be re-run — the fixes all need one.", "",
         "| surface | state | |", "|---|---|---|",
         f"| ORCID works (public) | {orc['works']} | {status(orc['works'] > 0)} |",
         # Two rows, not one: the count says the record is not empty, the coverage says
         # whether it holds your work. `105 of 117` graded "ok" for months because the
         # check behind it only ever asked whether the count was above zero.
         f"| ORCID holds your papers | {len(papers) - len(o_missing)} of {len(papers)} | "
         f"{status(not o_missing)} |",
         # Above the two rows it causes, because it is the row to act on first: a wrong
         # identifier inflates *missing* and *listed twice* at the same time, and fixing
         # either of those in the order the page reads them makes the record worse.
         f"| ORCID identifiers point at the right paper | "
         f"{orc['works'] - len(o_misfiled)} of {orc['works']} works | "
         f"{status(not o_misfiled)} |",
         f"| ORCID canonical URL | {'present' if has_canon else 'absent'} | {status(has_canon)} |",
         f"| ORCID name variants | {len(orc['other_names'])} listed | {status(not missing_variants)} |",
         f"| ORCID keywords | {len(orc['keywords'])} of "
         f"{len(ident.get('keywords') or [])} | {status(not want_kw)} |",
         f"| ORCID lists other personal pages | "
         f"{len((ident.get('other_pages') or [])) - len(other_pages)} of "
         f"{len(ident.get('other_pages') or [])} | {status(not other_pages)} |",
         f"| ORCID employment | {orc['employments']} listed, "
         f"{len(missing_empl)} missing | {status(not missing_empl)} |",
         f"| ORCID education | {orc['educations']} listed, "
         f"{len(missing_edu)} missing, {len(edu_open)} incomplete"
         + (f", {len(edu_theirs)} institution-asserted" if edu_theirs else "") + " | "
         f"{status(not missing_edu and not edu_open)} |",
         f"| ORCID works added by Crossref/DataCite | {sum(auto_src.values())} | "
         f"{'ok' if auto_src else 'nothing yet'} |",
         # Intersection, not len(reg): the feed also lists papers that are not in the
         # bibliography at all, and counting those made the row read "105 of 105" while
         # still flagging a gap.
         f"| arXiv registered author | {len({p['arxiv'] for p in ax} & (reg or set()))}"
         f" of {len({p['arxiv'] for p in ax})} | {status(n_gap == 0)} |",
         f"| Wikidata author item | {wd or 'none'} | {status(bool(wd))} |"]
    if wd_gaps:
        n_wd = (len(wd_gaps["missing"]) + len(wd_gaps["wrong"]) + len(wd_gaps["dupes"])
                + len(wd_gaps["bad_aliases"]) + len(wd_gaps["want_aliases"]))
        L.append(f"| Wikidata item complete | {n_wd} gaps | {status(not n_wd)} |")
    if wd_cov:
        # Not scored. Low coverage is a fact about Wikidata's imports, not a defect in
        # your record, and a red mark here would read as 119 tasks you are behind on.
        L.append(f"| Wikidata paper items | {len(wd_cov['present'])} of "
                 f"{wd_cov['total']} | optional |")
    if hf is not None:
        # Claimable, not total: three of these pages carry no author string resembling
        # your name, so they cannot be claimed at all. Scoring them against the total
        # leaves a row that can never reach "ok" and gives no hint why.
        claimable = len(ax) - len(hf["missing"]) - len(hf["blocked"])
        L += [f"| HF pages indexed | {len(ax) - len(hf['missing'])} of {len(ax)} | "
              f"{status(not hf['missing'])} |",
              f"| HF pages claimed | {len(hf['claimed'])} of {claimable} claimable | "
              f"{status(not hf['unclaimed'])} |"]
        if hf["pending"]:
            L.append(f"| HF claims in moderation | {len(hf['pending'])} | waiting |")
        if hf["blocked"]:
            L.append(f"| HF pages not claimable (name wrong upstream) | "
                     f"{len(hf['blocked'])} | see arXiv row |")
    if n_typo is not None:
        L.append(f"| arXiv records misspelling your name | {len(n_typo)} | "
                 f"{status(not n_typo)} |")
        L.append(f"| arXiv records omitting you | {len(n_absent)} | "
                 f"{status(not n_absent)} |")
    if stray:
        L.append(f"| arXiv papers missing from your bibliography | {len(stray)} | "
                 f"**check** |")
    if o_conf or o_unk:
        if o_conf:
            L.append(f"| ORCID works that are not yours | {len(o_conf)} | **fix** |")
        if o_unk:
            L.append(f"| ORCID works we cannot place | {len(o_unk)} | **check** |")
    if o_dups:
        L.append(f"| ORCID works listed twice | {len(o_dups)} | **fix** |")
    if o_vers:
        # Not **fix**: ORCID shows these as one entry with N versions, so nothing
        # downstream double-counts them. Listed only so this table and the profile page
        # agree about how many works are there, which is the one reason to look.
        L.append(f"| ORCID works ORCID already merged | {len(o_vers)} | optional |")
    L += [f"| Semantic Scholar records | {len(ids['semantic_scholar'])} | "
          f"{status(len(ids['semantic_scholar']) == 1)} |", ""]

    if orc["works"] == 0:
        L += ["## ORCID has 0 public works", "",
              "Note the *public*: an item set to “trusted parties” is invisible to the",
              "public API, which is the only thing Semantic Scholar, OpenAlex and Crossref",
              "read. So before importing, set **Account settings → Visibility preferences**",
              "to *Everyone*, or the import lands somewhere nothing can see.",
              "",
              "Then one upload: *Works → + Add → Add BibTeX* → `tasks/orcid_import.bib`.",
              "Not the DOI form 100 times — every entry in that file now carries a DOI",
              "(missing ones filled from arXiv), and ORCID groups works by identifier, so",
              "the whole file merges with the registry copies instead of duplicating them.",
              ""]
    if not has_canon:
        L += ["## ORCID researcher URLs point somewhere else", "",
              "Listed: " + (", ".join(f"`{u}`" for u in url_vals) or "none") + "  ",
              f"Expected: `{canon}`", "",
              "Two separate problems if one of those is a site-builder page. It competes",
              "with your canonical URL for the same identity — engines cannot fuse two",
              "candidate homepages — and Wix/Squarespace/Notion pages are JS-rendered, so",
              "AI crawlers that do not execute JavaScript see an empty document. Add the",
              "canonical URL, and either delete the other or make it redirect.", ""]
    if missing_variants:
        L += ["## ORCID name variants not listed", "",
              "*Also known as* is what a disambiguation model matches on when a citation",
              "uses a different form. Add: " +
              ", ".join(f"`{v}`" for v in missing_variants), ""]
    if want_kw:
        L += ["## ORCID keywords to add", "",
              "One of the few facets ORCID exposes for subject search, and free. Multi-word",
              "phrases someone would actually type — `model merging` is a query, `merging`",
              "is not — and no coined names, which have no lexical path from any real",
              "question. The same list fills Google Scholar's five interest slots (pick the",
              "top five). Edit `config.yaml` → `identity.keywords` to change it.", "",
              *[f"- [ ] {k}" for k in want_kw], ""]
    if not auto_src:
        L += ["## Crossref / DataCite auto-update: no evidence it is live", "",
              f"All {orc['works']} public works are **self-asserted** — the `source` on every",
              "one of them is your own name. A work that Crossref or DataCite adds carries",
              "*their* name instead, so this row is the only public read on whether those",
              "connections exist. It is currently reading zero.", "",
              "**Zero is the expected reading today, and that is the trap.** Auto-update is",
              "not a sync and it does not backfill: it fires only when a *newly deposited*",
              "record already contains your iD. So a granted permission and a permission",
              "that never completed look identical until your next paper is published —",
              "months from now, with nothing to connect the silence to the click.", "",
              "Two checks separate them, both two minutes:", "",
              "1. **Was the permission actually granted?** *ORCID → Account settings →",
              "   Trusted parties*. `Crossref Metadata Search` and `DataCite` should each",
              "   be listed there with permission to add and update your works. The wizards",
              "   send you off to `search.crossref.org` / DataCite's own site, which is what",
              "   makes this ambiguous: landing there proves the redirect worked, not that",
              "   you came back and completed the OAuth grant. If they are absent from",
              "   Trusted parties, nothing was granted — redo *Works → Search & link*.",
              "2. **Is your iD in the deposits at all?** Permissions cannot help if",
              "   publishers never put your iD in the metadata they deposit. Search a recent",
              "   published DOI at <https://search.crossref.org> and look for your ORCID in",
              "   the author list. Absent means the fix is upstream: supply your iD in the",
              "   submission system for every future paper. That single habit is what makes",
              "   auto-update work without you.", "",
              "Re-run this audit after the next publication lands. A non-zero count here is",
              "the proof; until then, Trusted parties is the evidence.", ""]
    if missing_empl or missing_edu or edu_open or edu_theirs:
        L += ["## ORCID employment and education are thinner than your record", "",
              "These two sections are what institutional disambiguation matches on — the",
              "signal that separates you from a namesake when the name alone cannot. They",
              "are also the sections nothing ever fills for you.", ""]
        if orc["employment_rows"] or orc["education_rows"]:
            L += ["Currently on the record:", ""]
            for r in orc["employment_rows"]:
                L.append(f"- *employment* — {r['org']} · {r['role'] or 'no role title'}"
                         f" · {r['start'] or '?'}–{r['end'] or 'present'}")
            for r in orc["education_rows"]:
                L.append(f"- *education* — {r['org']} · {r['role'] or 'no degree stated'}"
                         f" · {r['start'] or '?'}–{r['end'] or 'present'}"
                         + (f" · asserted by {r['source']}" if _theirs(r) else ""))
            L.append("")
        if missing_empl:
            L += ["**Affiliations in `config.yaml` with no employment entry.** Each is one",
                  "form under *Employment → + Add*. Worth the two minutes each: a paper",
                  "carrying an affiliation your ORCID never mentions is a paper a",
                  "disambiguator has one less reason to attach to you.", "",
                  *[f"- [ ] {a}" for a in missing_empl], ""]
        if missing_edu:
            L += ["**Degrees in `config.yaml` with no education entry.**", "",
                  *[f"- [ ] {e}" for e in missing_edu], ""]
        if edu_open:
            L += ["**Education entries that state less than they should.** ORCID's education",
                  "*Role* field is where the degree goes (`PhD`), and an entry with no end",
                  "year reads as *still enrolled*. Left as-is next to a postdoc employment,",
                  "the record contradicts itself about what you currently are — and it is a",
                  "human-obvious inconsistency that a machine reads literally.", ""]
            for r in edu_open:
                gaps = ", ".join(x for x in [
                    "no degree in the Role field" if not r["role"] else "",
                    "no end year" if not r["end"] else ""] if x)
                L.append(f"- [ ] {r['org']} — {gaps}")
            L.append("")
        if edu_theirs:
            L += ["**One education entry your institution asserted, not you.** This one is",
                  "not a task, it is a decision — and the default is to leave it.", ""]
            for r in edu_theirs:
                gaps = ", ".join(x for x in [
                    "no degree in the Role field" if not r["role"] else "",
                    "no end year" if not r["end"] else ""] if x)
                L.append(f"- {r['org']} — {gaps} — asserted by **{r['source']}** "
                         f"(put-code `{r['put']}`)")
            L += ["",
                  "ORCID shows no *Edit* control on an entry someone else asserted, only",
                  "*Delete*, so it cannot be corrected in place. The three routes, in the",
                  "order worth trying them:",
                  "",
                  "1. **Leave it.** An institution-asserted affiliation is the strongest form",
                  "   this section takes: the university's own ORCID integration vouched for",
                  "   it, and consumers can see that in the source line. A thinner entry from",
                  "   a better source beats a complete one you typed yourself.",
                  "2. **Add your own alongside it.** *Education → + Add* with the degree in",
                  "   *Role* and the real end year. ORCID groups affiliations by organization,",
                  "   so yours joins theirs as a second source on the same block rather than",
                  "   displacing it. This is the fix that costs nothing and loses nothing.",
                  "3. **Ask them to correct it** — whoever runs the ORCID integration, usually",
                  "   the library or the research office. Slow, and the only route that",
                  "   changes what the institution asserts.",
                  "",
                  "Do not delete it and re-add your own: that trades a vouched-for entry for a",
                  "self-asserted one, which is a downgrade in exactly the signal this section",
                  "exists to provide.", ""]
    if other_pages:
        L += ["## Other personal pages not declared on ORCID", "",
              "Not a demand to delete them. A second page is only a problem while nothing",
              "says it is the same person — then two candidate homepages compete. Listing it",
              "in *Websites & social links* next to the canonical URL is what fuses them.", "",
              *[f"- [ ] {u}" for u in other_pages], ""]
    if reg is not None and n_gap:
        L += [f"## arXiv: {n_gap} papers you are not registered as author on", "",
              "The biggest finding here, and a prerequisite rather than a task: you cannot",
              "add a journal-ref to a paper you do not own. Full list and both claim",
              "routes: [arxiv_ownership.md](arxiv_ownership.md).", ""]
    if wd_gaps and (wd_gaps["missing"] or wd_gaps["wrong"] or wd_gaps["dupes"]
                    or wd_gaps["bad_aliases"] or wd_gaps["want_aliases"]):
        bad = wd_gaps["bad_aliases"]
        n_add = len(wd_gaps["missing"])
        L += [f"## Wikidata item {wd} exists — {'a correction and ' if bad else ''}"
              f"{n_add} identifier{'' if n_add == 1 else 's'} to add", ""]
        if bad:
            L += ["An alias was stored as one string with its markdown intact "
                  f"(`{bad[0][:60]}`), so it matches nothing. Fix that first.", ""]
        L += ["Full diff, plus what the measured paper coverage means for the "
              "Author Disambiguator pass: "
              "[wikidata_followup.md](wikidata_followup.md).", ""]
    if wd_cov:
        n_have = len(wd_cov["present"])
        L += [f"## Wikidata paper coverage: {n_have} of {wd_cov['total']}", "",
              "Matched on DOI and arXiv id, not on name. This number matters because it",
              "decides which Wikidata job is worth doing: relinking author strings on",
              "items that already exist, or creating the items. At this coverage it is",
              "the second, and the first cannot pay for the 50 edits QuickStatements",
              "needs. One trap worth writing down — scholarly articles were moved out of",
              "Wikidata's main query graph, so a publication query against",
              "`query.wikidata.org` returns zero rows with a 200, and looks like an",
              "answer. This uses `query-scholarly.wikidata.org`.", ""]
        if wd_qs:
            L += [f"An opt-in batch for the {len(wd_cov['absent'])} missing items is in "
                  f"`{os.path.relpath(wd_qs, ROOT)}`; read the cautions in "
                  "[wikidata_followup.md](wikidata_followup.md) before running it.", ""]
    if stray:
        L += [f"## {len(stray)} arXiv papers you own are not in your bibliography", "",
              "Read off `arxiv.org/a/<orcid>`, which is the only place this shows up: the",
              "collector starts from the .bib, so a paper missing there is invisible to",
              "every other check here. Add it to the bibliography (or, if the claim was a",
              "mistake, unclaim it on arXiv).", "",
              *[f"- [ ] <https://arxiv.org/abs/{a}>" for a in stray], ""]
    if not wd:
        L += ["## No Wikidata author item", "",
              "Searched by ORCID (P496), Semantic Scholar (P4012), Google Scholar (P1960)",
              "and GitHub (P2037) — no item claims any of them. Name search is not used",
              "here on purpose: it returns *paper* items that merely mention you.",
              "", "Walkthrough: [wikidata_manual.md](wikidata_manual.md).", ""]
    if hf and (hf["missing"] or hf["unclaimed"] or hf["blocked"]):
        L += [f"## Hugging Face: {len(hf['missing'])} to index, "
              f"{len(hf['unclaimed'])} to claim, {len(hf['blocked'])} blocked", "",
              "Live counts, not the ones cached in `papers.yaml`. Lists:",
              "[hf_worklist.md](hf_worklist.md).", ""]
    if o_conf:
        L += [f"## {len(o_conf)} works on your ORCID are not yours", "",
              "Imported from the bibliography before the collector checked author names —",
              "a CV bibliography holds the works it *cites* as well as the works it lists.",
              "ORCID is read as your authorship claim by Semantic Scholar, OpenAlex and",
              "publisher systems, so this is worth clearing before anything else on this",
              "page. One deletion each, put-codes included:",
              "[orcid_remove.md](orcid_remove.md).", ""]
    if o_unk:
        # The summary table has carried a `**check**` on this count for as long as it has
        # existed, and nothing under it -- the titles were only ever in `orcid_remove.md`,
        # which the table does not link. A count flagged for attention with no way to
        # reach the thing it counts is how a row stops being read.
        L += [f"## {len(o_unk)} works on your ORCID we cannot place", "",
              "Not necessarily wrong, which is why this is *check* and not *fix*: a paper",
              "missing from your bibliography looks exactly like a work that is not yours.",
              "",
              "Matched against the corpus by identifier, then by title, then by the title's",
              "content words with the order discarded — so a paper retitled between preprint",
              "and proceedings, or rearranged around its colon, no longer lands here. What",
              "reaches this list carries no identifier ORCID could group on, which is also",
              "why nothing else can place it.",
              "",
              "Two things end up here and they have opposite fixes. A paper of yours the",
              "bibliography never held is fixed **upstream, in the bibliography** — deleting",
              "it from ORCID loses a real work. Anything that is not a paper (a workshop",
              "listing, a proceedings volume) is a deletion. Titles and put-codes:",
              "[orcid_remove.md](orcid_remove.md).", ""]
    if o_misfiled:
        L += [f"## {plural(len(o_misfiled), 'work on your ORCID carries', 'works on your ORCID carry')} "
              f"another paper's identifier", "",
              "**Fix these before the two sections below**, because this is what puts entries",
              "in them. A work whose DOI belongs to a different paper gets filed by ORCID into",
              "that paper's group — ORCID groups on shared identifiers and has no other way to",
              "know. The real paper then has no identifier anywhere on the record, so it reads",
              "as *missing from ORCID*, and the group it was absorbed into reads as *listed",
              "twice*. Both of those are wrong, and both suggested fixes make it worse: adding",
              "the paper creates a second copy, merging the group destroys a distinct work.",
              "",
              "Not a title guess. Each of these has an identifier resolving to one of your",
              "papers and a title matching another one character-for-character.", ""]
        for title, put, ids, right, wrong in o_misfiled:
            want = paper_doi(right) or "— the paper has no DOI to set —"
            full = right.get("title_display") or right["title"]
            other = (wrong.get("title_display") or wrong["title"])[:52]
            # The DOI the work actually carries, resolved -- not the other paper's
            # canonical DOI, which is a different string and would send you somewhere
            # that does not demonstrate the problem. The point of this link is that
            # following the identifier on your own record lands on someone else's paper.
            carried = next((v for t, v in ids if t == "doi"), None)
            has = ", ".join(f"{t}:{v}" for t, v in ids) or "— none —"
            blame = f"[{other}](https://doi.org/{carried})" if carried else other
            L += [f"- [ ] **{full[:70]}**"]
            # Compared untruncated, printed truncated: comparing the 70-character display
            # form against the full ORCID title made every long title look like a mismatch
            # and printed the same words twice.
            if norm_title(title) != norm_title(full):
                L.append(f"      - on ORCID it is titled {title[:70]!r}")
            L += [f"      - put-code `{put}`",
                  f"      - carries `{has}` — that identifier is {blame}",
                  f"      - should carry `{want}`",
                  "      - fix: <https://orcid.org/my-orcid#works> → find that work → the",
                  "        pencil icon → replace the DOI under *Identifiers* → *Save changes*.",
                  "        Edit rather than delete-and-re-add, so the put-code keeps its",
                  "        citations and its source attribution.", ""]
    if o_missing:
        L += [f"## {plural(len(o_missing), 'of your papers is', 'of your papers are')} "
              f"missing from ORCID", "",
              "Measured by identifier, not by counting: each of these has no work group on",
              "the record carrying its DOI or arXiv id.",
              "",
              "This is the row that matters most on the page and the one a works *count*",
              "hides. ORCID is the key Semantic Scholar disambiguates on and the key OpenAlex",
              "is running profile merges from, so a paper absent here is a paper those two",
              "have no authoritative reason to attach to you — which is the same failure the",
              "split S2 record is made of.",
              "",
              "Highest citations first; the full list with DOIs is",
              "[orcid_missing.md](orcid_missing.md).", ""]
        for p in o_missing[:10]:
            L.append(f"- [ ] {(p.get('citations') or 0):>4} cites — "
                     f"{(p.get('title_display') or p['title'])[:66]}")
        if len(o_missing) > 10:
            L.append(f"- … and {len(o_missing) - 10} more")
        L.append("")
    if o_dups:
        L += [f"## {plural(len(o_dups), 'paper is', 'papers are')} listed twice on "
              f"your ORCID", "",
              "ORCID groups works that share an identifier. A paper whose record holds",
              "the publisher DOI in one entry and arXiv's `10.48550/arXiv.<id>` DOI in",
              "another shares no identifier between them, so it does not group: it shows",
              "as two works with two different titles, and every service counting your",
              "output counts it twice.",
              "",
              "This is a side effect of `orcid_import.bib` filling missing DOIs from arXiv.",
              "It is worth fixing and it is not urgent. The fix is a merge, not a deletion:",
              "both titles are real, and adding one entry's DOI to the other folds them into",
              "one work with both. Which entry to open and what to paste into it:",
              "[orcid_remove.md](orcid_remove.md).", ""]
    if n_typo:
        L += [f"## arXiv metadata misspells your name on {len(n_typo)} papers", "",
              "Upstream of every other surface here — Hugging Face, Semantic Scholar,",
              "OpenAlex and Scholar all read arXiv's author list, so one wrong character",
              "creates one wrong author in all of them, holding citations that cannot be",
              "merged back. Details and the fix order:",
              "[arxiv_name_fixes.md](arxiv_name_fixes.md).", ""]

    path = os.path.join(TASKS, "identity_audit.md")
    with open(path, "w") as f:
        f.write("\n".join(L) + "\n")

    # Counts for WORKLIST.md, in build/ because they are observed state: entirely
    # re-derivable from the live APIs, so committing them would be storing someone
    # else's data and letting it go stale. Absent file = the section is skipped.
    os.makedirs(BUILD, exist_ok=True)
    state_path = os.path.join(BUILD, "identity_state.json")
    prev = {}
    try:
        with open(state_path) as f:
            prev = json.load(f)
    except (OSError, ValueError):
        pass

    def carried(*keys) -> dict:
        """The previous reading for a check this run skipped.

        A skipped check made no claim either way, so writing empty lists for it would
        report "nothing to do" -- the one output indistinguishable from success, and
        the one that quietly removes a section from WORKLIST.md. Carrying the last
        real reading through keeps the section, with numbers that were true once,
        which is the honest degradation.
        """
        return {k: prev[k] for k in keys if k in prev}

    state = carried("hf_missing", "hf_unclaimed", "hf_pending", "hf_blocked") \
        if args.no_hf else \
        {"hf_missing": [p["arxiv"] for p in hf["missing"]],
         "hf_unclaimed": [p["arxiv"] for p in hf["unclaimed"]],
         "hf_pending": [p["arxiv"] for p in hf["pending"]],
         "hf_blocked": [p["arxiv"] for p in hf["blocked"]]}
    state.update(carried("arxiv_name_typos", "arxiv_name_absent")
                 if args.no_names else
                 # Highest-leverage arXiv item and the only one upstream of every
                 # other surface, so the worklist needs the ids, not just a count.
                 {"arxiv_name_typos": [{"arxiv": p["arxiv"], "reads": p["near_miss"],
                                        "slug": p["slug"]} for p in n_typo],
                  "arxiv_name_absent": [p["arxiv"] for p in n_absent]})
    state.update({"orcid_public_works": orc["works"],
                  "orcid_has_canonical_url": has_canon,
                  "orcid_missing_variants": missing_variants,
                  "orcid_keywords": len(orc["keywords"]),
                  "orcid_missing_keywords": want_kw,
                  "orcid_missing_other_pages": other_pages,
                  "arxiv_registered": len(reg) if reg is not None else None,
                  "arxiv_total": len({p["arxiv"] for p in ax}),
                  "arxiv_unowned": [p["arxiv"] for p in ax
                                    if reg is not None and p["arxiv"] not in reg],
                  "arxiv_stray": stray,
                  "orcid_strays_confirmed": [t for t, _p, _k in o_conf],
                  "orcid_strays_unknown": [t for t, _p, _k in o_unk],
                  "orcid_duplicate_groups": sorted(o_dups),
                  "orcid_misfiled_ids": [{"put": put, "should_be": right["slug"],
                                          "carries": [f"{t}:{v}" for t, v in ids]}
                                         for _t, put, ids, right, _w in o_misfiled],
                  "orcid_missing_papers": [p["slug"] for p in o_missing],
                  "orcid_autoupdate_works": sum(auto_src.values()),
                  "orcid_missing_employment": missing_empl,
                  "orcid_missing_education": missing_edu,
                  "orcid_education_incomplete": [r["org"] for r in edu_open],
                  "wikidata": wd,
                  "wikidata_gaps": (len(wd_gaps.get("missing") or [])
                                    + len(wd_gaps.get("wrong") or [])
                                    + len(wd_gaps.get("dupes") or [])
                                    + len(wd_gaps.get("bad_aliases") or [])
                                    + len(wd_gaps.get("want_aliases") or []))
                  if wd_gaps else None,
                  "wikidata_papers_present": (len(wd_cov["present"]) if wd_cov
                                              else None),
                  "wikidata_papers_absent": (len(wd_cov["absent"]) if wd_cov
                                             else None)})
    with open(state_path, "w") as f:
        json.dump(state, f, indent=1)

    rm_path = os.path.join(TASKS, "orcid_remove.md")
    with open(rm_path, "w") as f:
        f.write(orcid_remove_file(o_stray, o_dups, papers, cfg))
    miss_paths = orcid_missing_files(o_missing, ident["orcid"]) if o_missing else []

    wrote = [path, ax_path, rm_path] + miss_paths \
        + [q for q in (hf_path, name_path, wd_path) if q]
    print("\nwrote " + "\n      ".join(wrote))
    for line in L:
        if line.startswith("| ") and "---" not in line:
            print("  " + line)


if __name__ == "__main__":
    main()
