#!/usr/bin/env python3
"""What the public ORCID record says, against what the corpus says.

The public API is what Semantic Scholar, OpenAlex and Crossref see, so this reads what
they read. `orcid_strays` diffs the record's works against the corpus in both directions,
identifier first, then exact title, then content-word set.

The write side is a BibTeX file, a DOI list and a page of removals. ORCID has no write
API without a token, so every fix here is a click the author makes.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (BUILD, TASKS, clipped, declined, norm_title, org_name, paper_doi,  # noqa: E402
                    plural, replied, synth_bibtex, title_of, title_tokens, write_task)
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


def _work_rows(act: dict) -> tuple[list[tuple], dict[str, int]]:
    """The works on the record, and a tally of who asserted each one.

    Returns (titles, sources). Each entry of `titles` is (title, put-code, the external
    ids that work itself carries, the index of the group ORCID filed it under).
    """
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
    return titles, sources


def _affiliation_rows(act: dict, sect: str) -> list[dict]:
    """One affiliation section, flattened out of ORCID's group-of-summaries shape."""
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
                "end": (ed.get("year") or {}).get("value"),
                "source": src,
                "put": v.get("put-code"),
            })
    return rows


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
    titles, sources = _work_rows(act)
    affs = {sect: _affiliation_rows(act, sect)
            for sect in ("employments", "educations")}
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

_ARXIV_DOI = re.compile(r"10\.48550/arxiv\.(.+)$", re.I)


def _index(papers) -> dict:
    """The corpus keyed the four ways a work is matched: DOI, arXiv id, title, token set."""
    # A token set two corpus papers share is dropped rather than resolved: which one an
    # ORCID work meant would be a guess, and the guess would be invisible -- the work
    # vanishes from this report either way, so a wrong pick reads exactly like a right one.
    # Four tokens minimum, because the shorter the set the cheaper an accidental collision.
    tok: dict = {}
    for p in papers:
        t = title_tokens(p["title"])
        if len(t) >= 4:
            tok.setdefault(t, []).append(p)
    return dict(doi={p["doi"].lower(): p for p in papers if p.get("doi")},
                arxiv={str(p["arxiv"]).lower(): p for p in papers if p.get("arxiv")},
                title={norm_title(p["title"]): p for p in papers},
                tokens={t: v[0] for t, v in tok.items() if len(v) == 1})


def _rejected() -> dict:
    """Works the collector threw out on author name, keyed by normalised title."""
    try:
        with open(os.path.join(BUILD, "not_mine.json")) as f:
            return {norm_title(x["title"]): x for x in json.load(f)}
    except (OSError, ValueError):
        return {}


def _by_ids(ids, ix: dict) -> dict | None:
    """The corpus paper one of these identifiers names."""
    for typ, val in ids:
        v = val.lower()
        if typ == "doi":
            m = _ARXIV_DOI.match(v)
            if m and m.group(1) in ix["arxiv"]:
                return ix["arxiv"][m.group(1)]
            if v in ix["doi"]:
                return ix["doi"][v]
        elif typ == "arxiv" and v.lstrip("arxiv:") in ix["arxiv"]:
            return ix["arxiv"][v.lstrip("arxiv:")]
    return None


def _by_title(title: str, ix: dict) -> tuple:
    """The corpus paper this title names, and how sure the match is.

    The confidence matters to `_placed` and only for the exact case: an identifier
    disagreeing with an *exact* title is a mistyped identifier, while an identifier
    disagreeing with a looser match is just title drift.
    """
    n = norm_title(title)
    if n in ix["title"]:
        return ix["title"][n], "exact"
    # Only in the containment direction: an ORCID title that is a prefix or suffix of a
    # corpus title is a dropped subtitle, not a new paper. Guarded by length so a short
    # title cannot swallow a long unrelated one.
    if len(n) >= 25:
        for cn, p in ix["title"].items():
            if n in cn or cn in n:
                return p, "loose"
    # Rearranged, which both checks above read as a different paper: the string is not
    # equal and, once the words move across the colon, neither title contains the other.
    # Live case, and the one that motivated this -- ORCID holds "Tie the KnOTS: Model
    # Merging with SVD" for the corpus's "Model merging with SVD to tie the Knots", and
    # the audit called it a work it could not place.
    p = ix["tokens"].get(title_tokens(title))
    return (p, "loose") if p else (None, None)


def _placed(title: str, ids, ix: dict) -> tuple:
    """The corpus paper a work belongs to, and `(right, wrong)` when its identifier lies.

    The identifier normally wins, since titles drift and identifiers do not. The exception
    the second half exists for: an identifier pointing at paper A while the title is
    character-for-character paper B is a wrong DOI typed into the work, and trusting the id
    there merges two papers and reports the absorbed one as missing. Only an `exact` title
    match overrides -- a loose match is the drift the id survives.
    """
    hid = _by_ids(ids, ix)
    tid, how = _by_title(title, ix)
    if hid is not None and tid is not None and hid["slug"] != tid["slug"]:
        return (tid, (tid, hid)) if how == "exact" else (hid, None)
    return hid or tid, None


def orcid_strays(orc: dict, papers) -> tuple:
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
    ix, rejected = _index(papers), _rejected()
    out, seen, misfiled = [], {}, []
    for title, put, ids, gidx in orc.get("work_titles") or []:
        hit, wrong = _placed(title, ids, ix)
        if wrong:
            misfiled.append((title, put, ids, *wrong))
        if hit is None:
            # `confirmed` outranks `declined`: "no form of your name is on this paper" is a
            # stronger statement than "not going in the bibliography", and it is the one
            # that ends in a deletion.
            out.append((title, put,
                        "confirmed" if norm_title(title) in rejected
                        else "declined" if declined(title) else "unknown"))
        else:
            seen.setdefault(hit["slug"], []).append((title, put, ids, gidx))
    # Split on group membership, not on count. `dups` is the profile actually showing a
    # paper twice; `versions` is one entry ORCID has already folded, which is worth a
    # mention and is not worth a **fix**.
    dups = {s: v for s, v in seen.items() if len({g for *_r, g in v}) > 1}
    versions = {s: v for s, v in seen.items() if s not in dups and len(v) > 1}
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
                  f"{clipped(title_of(p), 64)} | `{ident}` |")
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


def _incomplete(r: dict) -> bool:
    """An education row stating no degree, or no end year -- which still reads as *enrolled*."""
    return not r["role"] or not r["end"]


def asserted_by_them(r: dict, name: str) -> bool:
    """Somebody other than the author asserted the row, so ORCID offers Delete and no Edit."""
    s = (r.get("source") or "").lower()
    return bool(s) and s != (name or "").lower()


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
    edu_open = [r for r in rows if _incomplete(r) and not asserted_by_them(r, name)]
    edu_theirs = [r for r in rows if _incomplete(r) and asserted_by_them(r, name)]
    return dict(canon=canon, url_vals=url_vals, has_canon=has_canon,
                missing_variants=missing_variants, other_pages=other_pages, want_kw=want_kw,
                o_stray=o_stray, o_dups=o_dups, o_have=o_have, o_misfiled=o_misfiled,
                o_vers=o_vers, o_conf=o_conf, o_unk=o_unk, o_missing=o_missing,
                auto_src=auto_src, missing_empl=missing_empl, missing_edu=missing_edu,
                edu_open=edu_open, edu_theirs=edu_theirs)
