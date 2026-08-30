#!/usr/bin/env python3
"""Audit the identity surfaces you do not control, against what they should say.

Everything else in this repo checks *our* artifacts. This reads the five external
surfaces that decide whether a retrieval system can resolve you to one person, over
their public APIs -- no login, no key, read-only:

    ORCID          public works count, researcher URLs, name variants, keywords
    arXiv          which papers your account is actually registered as author on
    Wikidata       whether an author item carrying your ORCID exists yet
    Hugging Face   which paper pages exist, and which you have claimed
    Semantic Sch.  how the corpus is split across author records
    arXiv metadata whether its author list spells your name right at all

arxiv.org/a/<orcid> is built from arXiv's *authority records*, and being on one is the
gate on editing a paper: you cannot add a journal-ref to a paper you do not own. So the
arXiv diff is a prerequisite list, not a vanity metric.

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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (BUILD, DATA, ROOT, TASKS, clipped, declined,  # noqa: E402
                    get_status, in_halves, load_config, name_match, norm_title, org_name,
                    paper_doi, plural, read_yaml, replied, synth_bibtex, title_tokens,
                    write_json, write_task)
from wikidata_audit import (carry_wikidata, paper_item,  # noqa: E402
                            wikidata_followup_file, wikidata_gaps, wikidata_item,
                            wikidata_paper_coverage, wikidata_papers_qs)

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

    `reachable` is the third case, which the other two must never be confused with. Half of
    what the audit reports is read from this record, and an unread one reports the whole
    corpus as absent from ORCID and every work as self-asserted.
    """
    st, doc, why = replied(f"https://pub.orcid.org/v3.0/{orcid}/record")
    d = doc or {}
    act, person = d.get("activities-summary") or {}, d.get("person") or {}
    urls = [(u.get("url-name"), (u.get("url") or {}).get("value"))
            for u in ((person.get("researcher-urls") or {}).get("researcher-url") or [])]
    # Titles, not just the count. A bulk BibTeX import is one click and cannot be
    # undone in one click, so the record can silently end up asserting authorship of
    # works that were in the source file by mistake -- and nothing on ORCID will ever
    # tell you, because the record has no idea what you meant to claim.
    titles = []
    # Who asserted each work, tallied: the only public evidence that the Crossref and
    # DataCite auto-update permissions are live. A work they added carries their name in
    # `source`; anything imported by hand carries the author's. In the works list the
    # distinction is only visible by opening a work and reading its *Source* line.
    sources = {}
    for gidx, g in enumerate(((act.get("works") or {}).get("group") or [])):
        # The group's external ids are what ORCID groups on and the only reliable key back to
        # the corpus. Titles drift between preprint and proceedings ("TIES-Merging: Resolving
        # Interference" -> "Resolving Interference") and then look like unknown works.
        ids = [((e.get("external-id-type") or "").lower(), e.get("external-id-value") or "")
               for e in ((g.get("external-ids") or {}).get("external-id") or [])]
        for s in (g.get("work-summary") or []):
            src = ((s.get("source") or {}).get("source-name") or {}).get("value") or "(self)"
            sources[src] = sources.get(src, 0) + 1
            t = ((s.get("title") or {}).get("title") or {}).get("value")
            if not t:
                continue
            # Every work in the group, not just the first, and each tagged with the ids *it*
            # carries rather than the group's union. ORCID groups on shared identifiers, so a
            # work carrying the wrong DOI lands in another paper's group; reading only `i == 0`,
            # or resolving from the union, reports that work as missing from ORCID while it sits
            # on the record.
            own = [((e.get("external-id-type") or "").lower(), e.get("external-id-value") or "")
                   for e in ((s.get("external-ids") or {}).get("external-id") or [])]
            # The group index rides along because it separates a real duplicate from a cosmetic
            # one. Two works in *different* groups show as two works and every service counting
            # output counts both; two in the *same* group are one entry with "2 versions". Same
            # slug, two severities, so they cannot share a report section.
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
        "reachable": not why and bool(d),
        "status": st,
    }


def arxiv_registered(orcid: str) -> set[str] | None:
    """arXiv ids your account is registered as an author on.

    Read from the Atom flavour of arxiv.org/a/<orcid>: the HTML page 303-redirects
    and is JS-free, but the feed is the parseable one. An empty set means the ORCID is
    not linked to an arXiv account yet, and None means arXiv did not answer -- the
    "claim ownership" section is built from this, and an unread feed reads as nobody
    being registered on anything.
    """
    st, raw = get_status(f"https://arxiv.org/a/{orcid}.atom2", retries=2)
    if st in (404, 410):
        return set()
    if st != 200 or not raw:
        return None
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        # An unlinked ORCID serves the arXiv 404 page, which is HTML. A feed that stops
        # mid-document fails to parse the same way and this one runs to 245 KB, past the
        # size at which a body arrives cut off -- read as unlinked it puts every paper in
        # the "claim ownership" list.
        return None if b"<feed" in raw[:200] else set()
    out = set()
    for e in root.findall("a:entry", ATOM):
        m = _ABS.search((e.findtext("a:id", "", ATOM) or ""))
        if m:
            out.add(m.group(1))
    return out




























# Hugging Face records a per-author `status` beside the linked user. These two mean
# the link is live; anything else with a user attached is a claim in flight.
HF_CLAIM_DONE = {"claimed_verified", "admin_assigned"}


def hf_state(papers, me: str, variants, requested=()) -> dict[str, list]:
    """Live per-paper Hugging Face state, keyed by what can be done about it.

        missing    no page at all -- visit it while logged in
        unclaimed  page exists, the author list carries your name, no user linked
        pending    you are linked, not yet verified -- wait, do not redo
        blocked    no author string resembles your name, so no claim control exists and
                   the upstream metadata is the task
        claimed    done
        refused    Hugging Face did not answer, so nothing above is known about it

    `requested` (data/overrides.yaml -> hf_claim_requested) moves a page to `pending`. HF
    exposes the `user` link only after moderation, so a request sent an hour ago reads over
    the API exactly like one never made.

    Only a 404 puts a paper in `missing`, which is Hugging Face saying it has no page for
    that arXiv id. Any other non-answer is a `refused`, because `missing` is a list the
    author works through one browser visit at a time and an outage would fill it with the
    whole corpus.
    """
    me = me.lower()
    out = {k: [] for k in ("missing", "unclaimed", "pending", "blocked", "claimed",
                           "refused")}
    for p in papers:
        st, j, why = replied(f"https://huggingface.co/api/papers/{p['arxiv']}", retries=1)
        if why:
            out["missing" if st in (404, 410) else "refused"].append(p)
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
                f"{clipped(p.get('title_display') or p['title'], 70)}" for p in group]

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
                     f"{clipped(p.get('title_display') or p['title'], 60)}")
            L.append(f"      HF lists: {', '.join(p.get('hf_authors') or [])[:150]}")
        L.append("")
    write_task(path, L)
    return path










def orcid_strays(orc: dict, papers) -> list[tuple]:
    """Works on the ORCID record that are not in the corpus.

    Returns `(strays, duplicate_groups, matched_slugs, misfiled, merged_versions)`. A work
    matches a corpus paper by identifier, then exact title, then content-word set
    (`title_tokens`), the pass that places a paper of the author's own that was retitled.
    Each stray is tagged `confirmed` (the collector rejected it on author name too),
    `declined` (`data/declines.yaml` records its absence as a decision), or `unknown`.

        duplicate_groups  one corpus paper in two ORCID groups, double-counted downstream
        merged_versions   two works in one group, already unified
        misfiled          a work whose identifier belongs to a different paper, so it sits
                          in that paper's group and its own title is never compared
        matched_slugs     the other direction, which corpus papers the record lacks
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
        # The identifier normally wins, since titles drift and identifiers do not. The
        # exception this branch exists for: an identifier pointing at paper A while the title
        # is character-for-character paper B is a wrong DOI typed into the work, and trusting
        # the id there merges two papers and reports the absorbed one as missing. Only an
        # `exact` title match overrides -- a loose match is the drift the id survives.
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
                  f"{clipped(p.get('title_display') or p['title'], 64)} | `{ident}` |")
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
        write_task(path, body)
        out.append(path)
    return out


def dup_pairs(dups: dict, papers: list[dict]) -> list[dict]:
    """One row per ORCID duplicate: which entry to keep, which folds in, what to paste.

    Which to keep is derived, not judged: the preprint entry is the one whose DOI carries
    arXiv's DataCite prefix, so the published entry is the other one. When that does not
    hold -- neither DOI is arXiv's, or there are more than two entries -- the row says so
    and names every entry rather than guessing, and `doi` is None.

    Split out of `orcid_remove_file`'s table so build/identity_state.json carries the same
    title, put-code and DOI, which is what the worklist item needs to be workable in place.
    """
    by_slug = {p["slug"]: p for p in papers}
    arx = re.compile(r"^10\.48550/arxiv\.", re.I)

    def doi_of(ids):
        return next((v for t, v in ids if t == "doi"), None)

    out = []
    for slug, entries in (dups or {}).items():
        pre = [e for e in entries if arx.match(doi_of(e[2]) or "")]
        pub = [e for e in entries if e not in pre]
        row = {"slug": slug,
               "title": (by_slug.get(slug) or {}).get("title") or slug,
               "entries": [{"put": p, "title": t, "doi": doi_of(i)}
                           for t, p, i, _g in entries]}
        if len(pre) == 1 and len(pub) == 1:
            row |= {"keep": pub[0][1], "keep_title": pub[0][0],
                    "folds": pre[0][1], "folds_title": pre[0][0],
                    "doi": doi_of(pre[0][2])}
        out.append(row)
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
        # Rows from `dup_pairs`, which the state file reads too -- the table and the
        # worklist have to name the same put-code or one of them is lying.
        for row in dup_pairs(dups, papers):
            t = clipped(row["title"], 44)
            if row.get("doi"):
                L.append(f"| {t} | `{row['keep']}` — {clipped(row['keep_title'], 30)} | "
                         f"`{row['folds']}` — {clipped(row['folds_title'], 30)} "
                         f"| `{row['doi']}` |")
            else:
                # No arXiv DOI, or more than two entries: say so rather than guess which
                # to keep. Either way the fix is the same shape, one identifier.
                L.append(f"| {t} | "
                         + " | ".join(f"`{e['put']}` — {clipped(e['title'], 28)} "
                                      f"({e['doi'] or 'no DOI'})" for e in row["entries"])
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

    A chunk that arrived but did not parse is halved and asked again. 50 entries carry 50
    abstracts and run to 120 KB, and a body too large to deliver comes back cut off under
    HTTP 200. A refusal answers `[]` rather than None, because a smaller ask does not
    answer it, and what it does not carry is left out rather than reported as absent.
    """
    def one(chunk: list[str]) -> tuple[list | None, str]:
        st, raw = get_status("https://export.arxiv.org/api/query?id_list="
                             f"{','.join(chunk)}&max_results={len(chunk)}", retries=3)
        time.sleep(3)
        if st != 200 or not raw:
            return [], f"HTTP {st}"
        try:
            return ET.fromstring(raw).findall("a:entry", ATOM), ""
        except ET.ParseError:
            return None, f"an answer that stopped after {len(raw)} bytes"

    out: dict[str, list[str]] = {}
    for _chunk, entries, _why in in_halves(ids, one, batch):
        for e in entries or []:
            m = _ABS.search(e.findtext("a:id", "", ATOM) or "")
            if not m:
                continue
            out[m.group(1)] = [a.findtext("a:name", "", ATOM) or ""
                               for a in e.findall("a:author", ATOM)]
    return out


def arxiv_name_file(papers, variants) -> tuple[str, list, list, int]:
    """Papers whose arXiv author list misspells or omits your name.

    Also returns how many records arXiv actually served, because zero problems out of
    zero records read is the same number as a clean corpus.

    arXiv metadata is upstream of nearly every index here -- Hugging Face, Semantic Scholar,
    OpenAlex and Google Scholar all read it -- and a one-character typo creates a second
    author who owns that paper's citations and cannot be merged with you.

    Two failure modes, reported separately because the fixes differ:
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
         "Generated by `python scripts/audit_identity.py`.", "",
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
                     f"{clipped(p.get('title_display') or p['title'], 60)}")
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
                     f"{clipped(p.get('title_display') or p['title'], 60)}")
            L.append(f"      arXiv lists: {', '.join(p['arxiv_authors'])[:150]}")
        L.append("")
    if not (typo or absent):
        L += ["Nothing to fix — every retrieved record names you exactly.", ""]
    write_task(path, L)
    return path, typo, absent, len(found)


def _rows(group, extra=lambda p: "") -> list[str]:
    return [f"- [ ] {p.get('citations') or 0:>4} cites — "
            f"[`{p['arxiv']}`](https://arxiv.org/abs/{p['arxiv']}) "
            f"{clipped(p.get('title_display') or p['title'], 72)}{extra(p)}"
            for p in group]


def arxiv_ownership_file(cfg, papers, registered: set[str] | None) -> tuple[str | None,
                                                                             int | None]:
    """Writes `tasks/arxiv_ownership.md` and returns it with the count of unowned papers.

    `registered` of None is arXiv not answering, and nothing is written for it: this page
    is the claim list itself, so a run during an outage would replace 64 papers and their
    two claim routes with a line telling the author to go link an account they linked
    years ago.
    """
    ident = cfg["identity"]
    path = os.path.join(TASKS, "arxiv_ownership.md")
    if registered is None:
        return None, None
    if not registered:
        body = ["# arXiv ownership", "",
                f"`https://arxiv.org/a/{ident['orcid']}` does not resolve yet. Link your",
                "arXiv account to your ORCID first: <https://arxiv.org/user/confirm_orcid_id>",
                "then re-run `python scripts/audit_identity.py`."]
        write_task(path, body)
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
         "Generated by `python scripts/audit_identity.py`.", "",
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
    write_task(path, L)
    return path, len(gap)


def _incomplete(r: dict) -> bool:
    """An education row stating no degree, or no end year -- which still reads as *enrolled*."""
    return not r["role"] or not r["end"]


def _asserted_by_them(r: dict, name: str) -> bool:
    """Somebody other than the author asserted the row, so ORCID offers Delete and no Edit."""
    s = (r.get("source") or "").lower()
    return bool(s) and s != (name or "").lower()


def read_surfaces(cfg: dict, args) -> dict | None:
    """Every live read the audit makes, and the task files written while reading.

    `None` when ORCID did not answer: half the report comes from that record, so the run
    writes nothing and the last one's numbers stand.
    """
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
    if not orc["reachable"]:
        print("ORCID did not answer (status %s). Half of this report is read from that "
              "record, so nothing is written -- re-run when it is back."
              % (orc["status"] or "no reply"), file=sys.stderr)
        return None
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
            wd_path = wikidata_followup_file(wd_gaps, cfg, wd_cov, wd_qs, orc)
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
        if hf["refused"]:
            # Read as "no page yet", these would put every one of them on the author's
            # list as a browser visit. The last run's reading stands instead.
            print("hugging face did not answer for %d of %d page(s), so its half of this "
                  "report is carried from the last run" % (len(hf["refused"]), len(ax)),
                  file=sys.stderr)
            hf = None
        else:
            hf_path = hf_worklist_file(hf)

    name_path = n_typo = n_absent = None
    n_read = 0
    if not args.no_names:
        print("checking arXiv author lists for your name ...", flush=True)
        name_path, n_typo, n_absent, n_read = arxiv_name_file(ax, variants)

    ax_path, n_gap = arxiv_ownership_file(cfg, ax, reg)
    if reg is None:
        print("arxiv did not answer for the author feed, so tasks/arxiv_ownership.md and "
              "the ownership rows are left as the last run read them", file=sys.stderr)
    # Papers arXiv says you own that the bibliography does not mention. Usually a new
    # paper the .bib has not caught up with, occasionally an ownership claim on
    # someone else's paper -- either way it is the one direction of this diff that
    # nothing else in the repo would ever surface.
    stray = sorted((reg or set()) - {p["arxiv"] for p in ax})
    return dict(papers=papers, ax=ax, orc=orc, reg=reg,
                wd=wd, wd_path=wd_path, wd_gaps=wd_gaps, wd_cov=wd_cov,
                wd_qs=wd_qs, hf=hf, hf_path=hf_path, name_path=name_path,
                n_typo=n_typo, n_absent=n_absent, n_read=n_read, ax_path=ax_path,
                n_gap=n_gap, stray=stray)


def orcid_findings(cfg: dict, orc: dict, papers: list[dict]) -> dict:
    """What the ORCID record says against what `config.yaml` claims, read by page and state."""
    ident = cfg["identity"]
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
    # An education row with no role-title states an institution but not a degree, and one
    # with no end year still reads as *enrolled* -- next to a postdoc employment, a record
    # contradicting itself.
    #
    # Split by who asserted the row, because only one of the two is fixable. A self-asserted
    # row is editable in place. An institution-asserted row shows no *Edit* control in ORCID,
    # only *Delete*, so those are reported as a decision (leave it, or delete and re-add your
    # own) rather than as an open task -- and institution-asserted is the better evidence.
    rows = orc["education_rows"]
    name = ident["name"]
    edu_open = [r for r in rows if _incomplete(r) and not _asserted_by_them(r, name)]
    edu_theirs = [r for r in rows if _incomplete(r) and _asserted_by_them(r, name)]
    return dict(canon=canon, url_vals=url_vals, has_canon=has_canon,
                missing_variants=missing_variants, other_pages=other_pages, want_kw=want_kw,
                o_stray=o_stray, o_dups=o_dups, o_have=o_have, o_misfiled=o_misfiled,
                o_vers=o_vers, o_conf=o_conf, o_unk=o_unk, o_missing=o_missing,
                auto_src=auto_src, missing_empl=missing_empl, missing_edu=missing_edu,
                edu_open=edu_open, edu_theirs=edu_theirs)


def audit_page(cfg: dict, r: dict, d: dict) -> list[str]:
    """The audit page: a table of what every surface says, then a section per open fix."""
    return audit_table(cfg, r, d) + audit_fixes(cfg, r, d)


def audit_table(cfg: dict, r: dict, d: dict) -> list[str]:
    """One row per surface, each marked ok, **fix**, **check** or optional."""
    ident, ids = cfg["identity"], cfg["ids"]
    papers, ax, orc = r["papers"], r["ax"], r["orc"]
    reg, wd, wd_gaps = r["reg"], r["wd"], r["wd_gaps"]
    wd_cov, hf, n_typo = r["wd_cov"], r["hf"], r["n_typo"]
    n_absent, n_read, n_gap = r["n_absent"], r["n_read"], r["n_gap"]
    stray = r["stray"]
    has_canon, missing_variants = d["has_canon"], d["missing_variants"]
    other_pages = d["other_pages"]
    want_kw, o_dups, o_misfiled = d["want_kw"], d["o_dups"], d["o_misfiled"]
    o_vers, o_conf, o_unk = d["o_vers"], d["o_conf"], d["o_unk"]
    o_missing, auto_src, missing_empl = d["o_missing"], d["auto_src"], d["missing_empl"]
    missing_edu, edu_open, edu_theirs = d["missing_edu"], d["edu_open"], d["edu_theirs"]
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
         f"| arXiv registered author | "
         + (f"{len({p['arxiv'] for p in ax} & reg)} of {len({p['arxiv'] for p in ax})} "
            f"| {status(n_gap == 0)} |" if reg is not None
            else "arXiv did not answer | re-run |"),
         f"| Wikidata author item | {wd or 'none'} | {status(bool(wd))} |"]
    if wd_gaps:
        n_wd = (len(wd_gaps["missing"]) + len(wd_gaps["wrong"]) + len(wd_gaps["dupes"])
                + len(wd_gaps["bad_aliases"]) + len(wd_gaps["want_aliases"]))
        L.append(f"| Wikidata item complete | {n_wd} gaps | {status(not n_wd)} |")
    elif wd:
        # Dropping the row would read as one fewer thing to check rather than as a
        # reading this run does not have.
        L.append("| Wikidata item complete | Wikidata did not answer | re-run |")
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
        # `of n_read`, because both counts are zero when arXiv served nothing, and a bare
        # zero on both rows is the shape a clean corpus has. Neither row reaches "ok" on a
        # partial read, so the next run checks the rest rather than the page saying done.
        whole = n_read == len(ax)
        L.append(f"| arXiv records misspelling your name | {len(n_typo)} of {n_read} "
                 f"read | {status(not n_typo and whole)} |")
        L.append(f"| arXiv records omitting you | {len(n_absent)} of {n_read} read | "
                 f"{status(not n_absent and whole)} |")
        if not whole:
            L.append(f"| arXiv records it would not serve | {len(ax) - n_read} | "
                     f"retried next run |")
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
    return L


def audit_fixes(cfg: dict, r: dict, d: dict) -> list[str]:
    """One section per surface with something open, carrying the URL, the clicks and the
    values to paste. Empty when every row of the table above reads ok."""
    ident, ids = cfg["identity"], cfg["ids"]
    orc, reg, wd = r["orc"], r["reg"], r["wd"]
    wd_gaps, wd_cov, wd_qs = r["wd_gaps"], r["wd_cov"], r["wd_qs"]
    hf, n_typo, n_gap = r["hf"], r["n_typo"], r["n_gap"]
    stray = r["stray"]
    canon, url_vals, has_canon = d["canon"], d["url_vals"], d["has_canon"]
    missing_variants, other_pages = d["missing_variants"], d["other_pages"]
    want_kw = d["want_kw"]
    o_dups, o_misfiled, o_conf = d["o_dups"], d["o_misfiled"], d["o_conf"]
    o_unk, o_missing, auto_src = d["o_unk"], d["o_missing"], d["auto_src"]
    missing_empl, missing_edu, edu_open = d["missing_empl"], d["missing_edu"], d["edu_open"]
    edu_theirs = d["edu_theirs"]
    L = []
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
                theirs = _asserted_by_them(r, ident["name"])
                L.append(f"- *education* — {r['org']} · {r['role'] or 'no degree stated'}"
                         f" · {r['start'] or '?'}–{r['end'] or 'present'}"
                         + (f" · asserted by {r['source']}" if theirs else ""))
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
              "the second, and there is nothing to relink until they exist.",
              "One trap worth writing down — scholarly articles were moved out of",
              "Wikidata's main query graph, so a publication query against",
              "`query.wikidata.org` returns zero rows with a 200, and looks like an",
              "answer. This uses `query-scholarly.wikidata.org`.", ""]
        if wd_cov.get("unchecked"):
            u = len(wd_cov["unchecked"])
            L += [f"The endpoint would not answer about {plural(u, 'paper')} on this run, so "
                  f"{'it is' if u == 1 else 'they are'} missing from that number. Whether "
                  f"{'it has' if u == 1 else 'they have'} an item is unknown, and nothing "
                  "creates one until a run gets an answer.", ""]
        if wd_qs:
            L += [f"The {len(wd_cov['absent'])} missing items are created by "
                  "`python scripts/wikidata_apply.py --papers --apply --limit 10`, which "
                  "needs the bot password and nothing else; "
                  f"`{os.path.relpath(wd_qs, ROOT)}` is the same statements as a "
                  "QuickStatements batch, as a fallback. Read the cautions in "
                  "[wikidata_followup.md](wikidata_followup.md) first — these are "
                  "permanent public items.", ""]
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
            other = clipped(wrong.get("title_display") or wrong["title"], 52)
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
                L.append(f"      - on ORCID it is titled {clipped(title, 70)!r}")
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
                     f"{clipped(p.get('title_display') or p['title'], 66)}")
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
    return L


def audit_state(cfg: dict, args, r: dict, d: dict, path: str) -> dict:
    """The counts WORKLIST.md reads, carrying `path`'s numbers for whatever this run skipped.

    They live in `build/` because they are observed state, re-derivable from the live APIs.
    Committing them would store someone else's data and let it go stale, and an absent file
    means the worklist skips the section rather than reporting a zero.
    """
    ids = cfg["ids"]
    papers, ax, orc = r["papers"], r["ax"], r["orc"]
    reg, wd, wd_gaps = r["reg"], r["wd"], r["wd_gaps"]
    wd_cov, hf, n_typo = r["wd_cov"], r["hf"], r["n_typo"]
    n_absent, stray = r["n_absent"], r["stray"]
    has_canon, missing_variants = d["has_canon"], d["missing_variants"]
    other_pages, want_kw = d["other_pages"], d["want_kw"]
    o_dups, o_misfiled = d["o_dups"], d["o_misfiled"]
    o_conf, o_unk, o_missing = d["o_conf"], d["o_unk"], d["o_missing"]
    auto_src, missing_empl, missing_edu = d["auto_src"], d["missing_empl"], d["missing_edu"]
    edu_open = d["edu_open"]
    prev = {}
    try:
        with open(path) as f:
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
        if hf is None else \
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
    # An unread feed would report every paper as somebody else's and blank the section
    # that says so, so the last reading stands.
    state.update(carried("arxiv_registered", "arxiv_unowned") if reg is None else
                 {"arxiv_registered": len(reg),
                  "arxiv_unowned": [p["arxiv"] for p in ax if p["arxiv"] not in reg]})
    state.update({"orcid_public_works": orc["works"],
                  "orcid_has_canonical_url": has_canon,
                  "orcid_missing_variants": missing_variants,
                  "orcid_keywords": len(orc["keywords"]),
                  "orcid_missing_keywords": want_kw,
                  "orcid_missing_other_pages": other_pages,
                  "arxiv_total": len({p["arxiv"] for p in ax}),
                  "arxiv_stray": stray,
                  "orcid_strays_confirmed": [t for t, _p, _k in o_conf],
                  "orcid_strays_unknown": [t for t, _p, _k in o_unk],
                  "orcid_duplicate_groups": sorted(o_dups),
                  # `orcid_remove.md` has the pairs in a table; the worklist had a
                  # pointer to it and no values, which reads as "there is something here"
                  # over an empty section. Both put-codes and the one DOI to paste travel
                  # with the count now, so the summary can say the whole job in a line.
                  "orcid_duplicate_pairs": dup_pairs(o_dups, papers),
                  # `should_carry` as well as `should_be`, so the worklist can name the paper and give
                  # the string to paste; `carried_*` so it can link the wrong DOI. That link is the
                  # evidence for the item -- following the identifier on your own record and landing on
                  # somebody else's paper -- and without it the instruction is "trust us, replace this".
                  "orcid_misfiled_ids": [{"put": put, "should_be": right["slug"],
                                          "should_carry": paper_doi(right),
                                          "carries": [f"{t}:{v}" for t, v in ids],
                                          "carried_doi": next((v for t, v in ids
                                                               if t == "doi"), None),
                                          "carried_title": (wrong.get("title_display")
                                                            or wrong["title"])}
                                         for _t, put, ids, right, wrong in o_misfiled],
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
                                             else None),
                  "wikidata_papers_unchecked": (len(wd_cov.get("unchecked") or [])
                                                if wd_cov else None),
                  # How many of the absent ones can actually be created, which is smaller: a paper with
                  # neither a DOI nor an arXiv id has no key to deduplicate against, so nothing will
                  # mint an item for it. The worklist heads its section with this rather than `absent`,
                  # because a heading saying 109 over a command that creates 108 is a count that does
                  # not match its list.
                  "wikidata_papers_creatable": (
                      sum(1 for p in wd_cov["absent"] if paper_item(p, cfg))
                      if wd_cov else None)})
    quiet = carry_wikidata(state, prev)
    if quiet:
        print("wikidata did not answer (%s), so its half of this report is carried from "
              "the last run" % quiet, file=sys.stderr)
    return state


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-hf", action="store_true",
                    help="skip the per-paper Hugging Face checks (the slow part)")
    ap.add_argument("--no-names", action="store_true",
                    help="skip the arXiv author-name check (needs ~3s per 50 papers)")
    args = ap.parse_args()
    cfg = load_config()
    r = read_surfaces(cfg, args)
    if r is None:
        return 1
    d = orcid_findings(cfg, r["orc"], r["papers"])
    papers, wd_path, hf_path = r["papers"], r["wd_path"], r["hf_path"]
    name_path, ax_path = r["name_path"], r["ax_path"]
    o_stray, o_dups, o_missing = d["o_stray"], d["o_dups"], d["o_missing"]

    L = audit_page(cfg, r, d)
    path = os.path.join(TASKS, "identity_audit.md")
    write_task(path, L)

    os.makedirs(BUILD, exist_ok=True)
    state_path = os.path.join(BUILD, "identity_state.json")
    write_json(state_path, audit_state(cfg, args, r, d, state_path), indent=1)

    rm_path = os.path.join(TASKS, "orcid_remove.md")
    write_task(rm_path, orcid_remove_file(o_stray, o_dups, papers, cfg))
    miss_paths = (orcid_missing_files(o_missing, cfg["identity"]["orcid"])
                  if o_missing else [])

    wrote = [path, rm_path] + miss_paths \
        + [q for q in (ax_path, hf_path, name_path, wd_path) if q]
    print("\nwrote " + "\n      ".join(wrote))
    for line in L:
        if line.startswith("| ") and "---" not in line:
            print("  " + line)


if __name__ == "__main__":
    raise SystemExit(main())
