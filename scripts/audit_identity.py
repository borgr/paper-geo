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

The two largest surfaces read next door, in `orcid_audit.py` and `wikidata_audit.py`.
This file reads the rest, tables what every surface said, and writes the pages.

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
from common import (BUILD, ROOT, TASKS, clipped, get_status, in_halves, load_config,  # noqa: E402
                    name_match, norm_title, paper_doi, plural, read_overrides, read_papers,
                    replied, title_of, write_json, write_task)
from orcid_audit import (asserted_by_them, dup_pairs, orcid_findings,  # noqa: E402
                         orcid_missing_files, orcid_public, orcid_remove_file)
from wikidata_audit import (carry_wikidata, paper_item,  # noqa: E402
                            wikidata_followup_file, wikidata_gaps, wikidata_item,
                            wikidata_paper_coverage, wikidata_papers_qs)

ATOM = {"a": "http://www.w3.org/2005/Atom"}
_ABS = re.compile(r"abs/([0-9]{4}\.[0-9]{4,5}|[a-z\-]+/[0-9]{7})")






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
                f"{clipped(title_of(p), 70)}" for p in group]

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
                     f"{clipped(title_of(p), 60)}")
            L.append(f"      HF lists: {', '.join(p.get('hf_authors') or [])[:150]}")
        L.append("")
    write_task(path, L)
    return path


















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
                     f"{clipped(title_of(p), 60)}")
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
                     f"{clipped(title_of(p), 60)}")
            L.append(f"      arXiv lists: {', '.join(p['arxiv_authors'])[:150]}")
        L.append("")
    if not (typo or absent):
        L += ["Nothing to fix — every retrieved record names you exactly.", ""]
    write_task(path, L)
    return path, typo, absent, len(found)


def _rows(group, extra=lambda p: "") -> list[str]:
    return [f"- [ ] {p.get('citations') or 0:>4} cites — "
            f"[`{p['arxiv']}`](https://arxiv.org/abs/{p['arxiv']}) "
            f"{clipped(title_of(p), 72)}{extra(p)}"
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






def read_surfaces(cfg: dict, args) -> dict | None:
    """Every live read the audit makes, and the task files written while reading.

    `None` when ORCID did not answer: half the report comes from that record, so the run
    writes nothing and the last one's numbers stand.
    """
    ident, ids = cfg["identity"], cfg["ids"]
    papers = read_papers()
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
        requested = {str(a) for a in read_overrides().get("hf_claim_requested") or []}
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




def audit_page(cfg: dict, r: dict, d: dict) -> list[str]:
    """The audit page: a table of what every surface says, then a section per open fix."""
    return audit_table(cfg, r, d) + audit_fixes(cfg, r, d)

def _mark(ok: bool) -> str:
    """The verdict column for a row that is either clean or a fix."""
    return "ok" if ok else "**fix**"


def _orcid_rows(cfg: dict, r: dict, d: dict) -> list[str]:
    """The rows read off the ORCID record itself, in the order they should be worked."""
    ident, orc, papers = cfg["identity"], r["orc"], r["papers"]
    kw, pages = ident.get("keywords") or [], ident.get("other_pages") or []
    theirs = d["edu_theirs"]
    return [
        f"| ORCID works (public) | {orc['works']} | {_mark(orc['works'] > 0)} |",
        # Two rows, not one: the count says the record is not empty, the coverage says
        # whether it holds your work. `105 of 117` graded "ok" for months because the
        # check behind it only ever asked whether the count was above zero.
        f"| ORCID holds your papers | {len(papers) - len(d['o_missing'])} of "
        f"{len(papers)} | {_mark(not d['o_missing'])} |",
        # Above the two rows it causes, because it is the row to act on first: a wrong
        # identifier inflates *missing* and *listed twice* at the same time, and fixing
        # either of those in the order the page reads them makes the record worse.
        f"| ORCID identifiers point at the right paper | "
        f"{orc['works'] - len(d['o_misfiled'])} of {orc['works']} works | "
        f"{_mark(not d['o_misfiled'])} |",
        f"| ORCID canonical URL | {'present' if d['has_canon'] else 'absent'} | "
        f"{_mark(d['has_canon'])} |",
        f"| ORCID name variants | {len(orc['other_names'])} listed | "
        f"{_mark(not d['missing_variants'])} |",
        f"| ORCID keywords | {len(orc['keywords'])} of {len(kw)} | "
        f"{_mark(not d['want_kw'])} |",
        f"| ORCID lists other personal pages | {len(pages) - len(d['other_pages'])} of "
        f"{len(pages)} | {_mark(not d['other_pages'])} |",
        f"| ORCID employment | {orc['employments']} listed, "
        f"{len(d['missing_empl'])} missing | {_mark(not d['missing_empl'])} |",
        f"| ORCID education | {orc['educations']} listed, {len(d['missing_edu'])} "
        f"missing, {len(d['edu_open'])} incomplete"
        + (f", {len(theirs)} institution-asserted" if theirs else "") + " | "
        f"{_mark(not d['missing_edu'] and not d['edu_open'])} |",
        f"| ORCID works added by Crossref/DataCite | {sum(d['auto_src'].values())} | "
        f"{'ok' if d['auto_src'] else 'nothing yet'} |",
    ]


def _orcid_trouble_rows(d: dict) -> list[str]:
    """Works on the record that are not cleanly yours, one row per kind that has any."""
    L = []
    if d["o_conf"]:
        L.append(f"| ORCID works that are not yours | {len(d['o_conf'])} | **fix** |")
    if d["o_unk"]:
        L.append(f"| ORCID works we cannot place | {len(d['o_unk'])} | **check** |")
    if d["o_dups"]:
        L.append(f"| ORCID works listed twice | {len(d['o_dups'])} | **fix** |")
    if d["o_vers"]:
        # Not **fix**: ORCID shows these as one entry with N versions, so nothing
        # downstream double-counts them. Listed only so this table and the profile page
        # agree about how many works are there, which is the one reason to look.
        L.append(f"| ORCID works ORCID already merged | {len(d['o_vers'])} | optional |")
    return L


def _arxiv_owner_row(r: dict) -> list[str]:
    """How many of the corpus's arXiv ids the author feed claims."""
    ids, reg = {p["arxiv"] for p in r["ax"]}, r["reg"]
    # Intersection, not len(reg): the feed also lists papers that are not in the
    # bibliography at all, and counting those made the row read "105 of 105" while
    # still flagging a gap.
    return [f"| arXiv registered author | "
            + (f"{len(ids & reg)} of {len(ids)} | {_mark(r['n_gap'] == 0)} |"
               if reg is not None else "arXiv did not answer | re-run |")]


def _arxiv_name_rows(r: dict) -> list[str]:
    """What the arXiv records say about the author's name, and papers the corpus is missing."""
    ax, n_typo, L = r["ax"], r["n_typo"], []
    if n_typo is not None:
        # `of n_read`, because both counts are zero when arXiv served nothing, and a bare
        # zero on both rows is the shape a clean corpus has. Neither row reaches "ok" on a
        # partial read, so the next run checks the rest rather than the page saying done.
        read, whole = r["n_read"], r["n_read"] == len(ax)
        L += [f"| arXiv records misspelling your name | {len(n_typo)} of {read} read | "
              f"{_mark(not n_typo and whole)} |",
              f"| arXiv records omitting you | {len(r['n_absent'])} of {read} read | "
              f"{_mark(not r['n_absent'] and whole)} |"]
        if not whole:
            L.append(f"| arXiv records it would not serve | {len(ax) - read} | "
                     f"retried next run |")
    if r["stray"]:
        L.append(f"| arXiv papers missing from your bibliography | {len(r['stray'])} | "
                 f"**check** |")
    return L


def _wikidata_rows(r: dict) -> list[str]:
    """The item, how complete it is, and how much of the bibliography Wikidata has imported."""
    wd, gaps, cov = r["wd"], r["wd_gaps"], r["wd_cov"]
    L = [f"| Wikidata author item | {wd or 'none'} | {_mark(bool(wd))} |"]
    if gaps:
        n = sum(len(gaps[k]) for k in
                ("missing", "wrong", "dupes", "bad_aliases", "want_aliases"))
        L.append(f"| Wikidata item complete | {n} gaps | {_mark(not n)} |")
    elif wd:
        # Dropping the row would read as one fewer thing to check rather than as a
        # reading this run does not have.
        L.append("| Wikidata item complete | Wikidata did not answer | re-run |")
    if cov:
        # Not scored. Low coverage is a fact about Wikidata's imports, not a defect in
        # your record, and a red mark here would read as 119 tasks you are behind on.
        L.append(f"| Wikidata paper items | {len(cov['present'])} of {cov['total']} | "
                 f"optional |")
    return L


def _hf_rows(r: dict) -> list[str]:
    """The Hugging Face paper pages, or nothing when that half of the run was skipped."""
    ax, hf = r["ax"], r["hf"]
    if hf is None:
        return []
    # Claimable, not total: three of these pages carry no author string resembling
    # your name, so they cannot be claimed at all. Scoring them against the total
    # leaves a row that can never reach "ok" and gives no hint why.
    claimable = len(ax) - len(hf["missing"]) - len(hf["blocked"])
    L = [f"| HF pages indexed | {len(ax) - len(hf['missing'])} of {len(ax)} | "
         f"{_mark(not hf['missing'])} |",
         f"| HF pages claimed | {len(hf['claimed'])} of {claimable} claimable | "
         f"{_mark(not hf['unclaimed'])} |"]
    if hf["pending"]:
        L.append(f"| HF claims in moderation | {len(hf['pending'])} | waiting |")
    if hf["blocked"]:
        L.append(f"| HF pages not claimable (name wrong upstream) | "
                 f"{len(hf['blocked'])} | see arXiv row |")
    return L


def audit_table(cfg: dict, r: dict, d: dict) -> list[str]:
    """One row per surface, each marked ok, **fix**, **check** or optional.

    Grouped by surface in the order a reader works them, and each group is empty rather
    than wrong when its surface did not answer.
    """
    ss = cfg["ids"]["semantic_scholar"]
    return (["# Identity audit", "",
             "Live read of the surfaces you do not control. Regenerate with",
             "`python scripts/audit_identity.py`. Every row is checkable without a login,",
             "which is why it can be re-run — the fixes all need one.", "",
             "| surface | state | |", "|---|---|---|"]
            + _orcid_rows(cfg, r, d)
            + _arxiv_owner_row(r)
            + _wikidata_rows(r)
            + _hf_rows(r)
            + _arxiv_name_rows(r)
            + _orcid_trouble_rows(d)
            + [f"| Semantic Scholar records | {len(ss)} | {_mark(len(ss) == 1)} |", ""])


def audit_fixes(cfg: dict, r: dict, d: dict) -> list[str]:
    """One section per surface with something open, carrying the URL, the clicks and the
    values to paste. Empty when every row of the table above reads ok.

    A section below returns nothing when its own surface has nothing open, so this holds
    the order they print in and nothing else.
    """
    orc, name = r["orc"], cfg["identity"]["name"]
    return (orcid_no_public_works(orc)
            + orcid_canonical_url(d["canon"], d["url_vals"], d["has_canon"])
            + orcid_name_variants(d["missing_variants"])
            + orcid_keywords(d["want_kw"])
            + orcid_auto_update(orc, d["auto_src"])
            + orcid_affiliations(orc, name, d["missing_empl"], d["missing_edu"],
                                 d["edu_open"], d["edu_theirs"])
            + orcid_other_pages(d["other_pages"])
            + arxiv_unregistered(r["reg"], r["n_gap"])
            + wikidata_author_gaps(r["wd"], r["wd_gaps"])
            + wikidata_paper_gaps(r["wd_cov"], r["wd_qs"])
            + arxiv_strays(r["stray"])
            + wikidata_no_author_item(r["wd"])
            + hf_gaps(r["hf"])
            + orcid_confirmed_strays(d["o_conf"])
            + orcid_unplaceable(d["o_unk"])
            + orcid_misfiled(d["o_misfiled"])
            + orcid_missing(d["o_missing"])
            + orcid_duplicates(d["o_dups"])
            + arxiv_misspellings(r["n_typo"]))


def orcid_no_public_works(orc: dict) -> list[str]:
    """The one-file BibTeX import, when the public API reports no works at all."""
    if orc["works"]:
        return []
    return ["## ORCID has 0 public works", "",
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


def orcid_canonical_url(canon: str, url_vals: list, has_canon: bool) -> list[str]:
    """The canonical URL is not among the researcher URLs the record lists."""
    if has_canon:
        return []
    return ["## ORCID researcher URLs point somewhere else", "",
            "Listed: " + (", ".join(f"`{u}`" for u in url_vals) or "none") + "  ",
            f"Expected: `{canon}`", "",
            "Two separate problems if one of those is a site-builder page. It competes",
            "with your canonical URL for the same identity — engines cannot fuse two",
            "candidate homepages — and Wix/Squarespace/Notion pages are JS-rendered, so",
            "AI crawlers that do not execute JavaScript see an empty document. Add the",
            "canonical URL, and either delete the other or make it redirect.", ""]


def orcid_name_variants(missing_variants: list) -> list[str]:
    """Name forms in `config.yaml` that *Also known as* does not carry."""
    if not missing_variants:
        return []
    return ["## ORCID name variants not listed", "",
            "*Also known as* is what a disambiguation model matches on when a citation",
            "uses a different form. Add: " +
            ", ".join(f"`{v}`" for v in missing_variants), ""]


def orcid_keywords(want_kw: list) -> list[str]:
    """Keywords in `config.yaml` the record does not carry."""
    if not want_kw:
        return []
    return ["## ORCID keywords to add", "",
            "One of the few facets ORCID exposes for subject search, and free. Multi-word",
            "phrases someone would actually type — `model merging` is a query, `merging`",
            "is not — and no coined names, which have no lexical path from any real",
            "question. The same list fills Google Scholar's five interest slots (pick the",
            "top five). Edit `config.yaml` → `identity.keywords` to change it.", "",
            *[f"- [ ] {k}" for k in want_kw], ""]


def orcid_auto_update(orc: dict, auto_src: dict) -> list[str]:
    """No work on the record came from Crossref or DataCite rather than the author."""
    if auto_src:
        return []
    return ["## Crossref / DataCite auto-update: no evidence it is live", "",
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


def orcid_affiliations(orc: dict, name: str, missing_empl: list, missing_edu: list,
                       edu_open: list, edu_theirs: list) -> list[str]:
    """Employment and education entries the record misses or states incompletely."""
    L = []
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
                theirs = asserted_by_them(r, name)
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
    return L


def orcid_other_pages(other_pages: list) -> list[str]:
    """Personal pages the record does not list beside the canonical URL."""
    if not other_pages:
        return []
    return ["## Other personal pages not declared on ORCID", "",
            "Not a demand to delete them. A second page is only a problem while nothing",
            "says it is the same person — then two candidate homepages compete. Listing it",
            "in *Websites & social links* next to the canonical URL is what fuses them.", "",
            *[f"- [ ] {u}" for u in other_pages], ""]


def arxiv_unregistered(reg: set | None, n_gap: int) -> list[str]:
    """How many papers the arXiv author feed does not claim, over the full list."""
    if reg is None or not n_gap:
        return []
    return [f"## arXiv: {n_gap} papers you are not registered as author on", "",
            "The biggest finding here, and a prerequisite rather than a task: you cannot",
            "add a journal-ref to a paper you do not own. Full list and both claim",
            "routes: [arxiv_ownership.md](arxiv_ownership.md).", ""]


def wikidata_author_gaps(wd: str | None, wd_gaps: dict) -> list[str]:
    """Identifiers and aliases the author item is missing, over the full diff."""
    L = []
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
    return L


def wikidata_paper_gaps(wd_cov: dict, wd_qs: str | None) -> list[str]:
    """How many papers have items, and the command that creates the rest."""
    L = []
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
    return L


def arxiv_strays(stray: list) -> list[str]:
    """arXiv papers the author is registered on that the bibliography does not hold."""
    if not stray:
        return []
    return [f"## {len(stray)} arXiv papers you own are not in your bibliography", "",
            "Read off `arxiv.org/a/<orcid>`, which is the only place this shows up: the",
            "collector starts from the .bib, so a paper missing there is invisible to",
            "every other check here. Add it to the bibliography (or, if the claim was a",
            "mistake, unclaim it on arXiv).", "",
            *[f"- [ ] <https://arxiv.org/abs/{a}>" for a in stray], ""]


def wikidata_no_author_item(wd: str | None) -> list[str]:
    """No item claims any identifier the author has."""
    if wd:
        return []
    return ["## No Wikidata author item", "",
            "Searched by ORCID (P496), Semantic Scholar (P4012), Google Scholar (P1960)",
            "and GitHub (P2037) — no item claims any of them. Name search is not used",
            "here on purpose: it returns *paper* items that merely mention you.",
            "", "Walkthrough: [wikidata_manual.md](wikidata_manual.md).", ""]


def hf_gaps(hf: dict | None) -> list[str]:
    """Live Hugging Face counts, over the lists."""
    if not hf or not (hf["missing"] or hf["unclaimed"] or hf["blocked"]):
        return []
    return [f"## Hugging Face: {len(hf['missing'])} to index, "
            f"{len(hf['unclaimed'])} to claim, {len(hf['blocked'])} blocked", "",
            "Live counts, not the ones cached in `papers.yaml`. Lists:",
            "[hf_worklist.md](hf_worklist.md).", ""]


def orcid_confirmed_strays(o_conf: list) -> list[str]:
    """Works on the record that are somebody else's."""
    if not o_conf:
        return []
    return [f"## {len(o_conf)} works on your ORCID are not yours", "",
            "Imported from the bibliography before the collector checked author names —",
            "a CV bibliography holds the works it *cites* as well as the works it lists.",
            "ORCID is read as your authorship claim by Semantic Scholar, OpenAlex and",
            "publisher systems, so this is worth clearing before anything else on this",
            "page. One deletion each, put-codes included:",
            "[orcid_remove.md](orcid_remove.md).", ""]


def orcid_unplaceable(o_unk: list) -> list[str]:
    """Works on the record the corpus cannot place, which is a check and not a fix."""
    if not o_unk:
        return []
      # The summary table has carried a `**check**` on this count for as long as it has
      # existed, and nothing under it -- the titles were only ever in `orcid_remove.md`,
      # which the table does not link. A count flagged for attention with no way to
      # reach the thing it counts is how a row stops being read.
    return [f"## {len(o_unk)} works on your ORCID we cannot place", "",
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


def orcid_misfiled(o_misfiled: list) -> list[str]:
    """Works carrying another paper's identifier, with the put-code and the DOI to set."""
    L = []
    if o_misfiled:
        n = plural(len(o_misfiled), "work on your ORCID carries",
                   "works on your ORCID carry")
        L += [f"## {n} another paper's identifier", "",
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
            full = title_of(right)
            other = clipped(title_of(wrong), 52)
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
    return L


def orcid_missing(o_missing: list) -> list[str]:
    """Papers with no work group on the record, highest citations first."""
    L = []
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
                     f"{clipped(title_of(p), 66)}")
        if len(o_missing) > 10:
            L.append(f"- … and {len(o_missing) - 10} more")
        L.append("")
    return L


def orcid_duplicates(o_dups: list) -> list[str]:
    """Papers listed twice because their two entries share no identifier."""
    if not o_dups:
        return []
    return [f"## {plural(len(o_dups), 'paper is', 'papers are')} listed twice on "
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


def arxiv_misspellings(n_typo: list) -> list[str]:
    """arXiv author lists that misspell the name, over the fix order."""
    if not n_typo:
        return []
    return [f"## arXiv metadata misspells your name on {len(n_typo)} papers", "",
            "Upstream of every other surface here — Hugging Face, Semantic Scholar,",
            "OpenAlex and Scholar all read arXiv's author list, so one wrong character",
            "creates one wrong author in all of them, holding citations that cannot be",
            "merged back. Details and the fix order:",
            "[arxiv_name_fixes.md](arxiv_name_fixes.md).", ""]


def _last_reading(path: str) -> dict:
    """The state file from the previous run, or `{}` when there is not one yet."""
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _carried(prev: dict, *keys) -> dict:
    """The previous reading for a check this run skipped.

    A skipped check made no claim either way, so writing empty lists for it would report
    "nothing to do" -- the one output indistinguishable from success, and the one that
    quietly removes a section from WORKLIST.md. Carrying the last real reading keeps the
    section, with numbers that were true once.
    """
    return {k: prev[k] for k in keys if k in prev}


def _hf_counts(hf, prev: dict) -> dict:
    """Which papers the Hugging Face page lists, is missing, and cannot claim."""
    if hf is None:
        return _carried(prev, "hf_missing", "hf_unclaimed", "hf_pending", "hf_blocked")
    return {"hf_missing": [p["arxiv"] for p in hf["missing"]],
            "hf_unclaimed": [p["arxiv"] for p in hf["unclaimed"]],
            "hf_pending": [p["arxiv"] for p in hf["pending"]],
            "hf_blocked": [p["arxiv"] for p in hf["blocked"]]}


def _name_counts(r: dict, args, prev: dict) -> dict:
    """Papers whose arXiv author list misspells the name or omits it."""
    if args.no_names:
        return _carried(prev, "arxiv_name_typos", "arxiv_name_absent")
    # Highest-leverage arXiv item and the only one upstream of every other surface, so
    # the worklist needs the ids, not just a count.
    return {"arxiv_name_typos": [{"arxiv": p["arxiv"], "reads": p["near_miss"],
                                  "slug": p["slug"]} for p in r["n_typo"]],
            "arxiv_name_absent": [p["arxiv"] for p in r["n_absent"]]}


def _ownership_counts(r: dict, prev: dict) -> dict:
    """How much of the corpus the arXiv author feed claims."""
    reg = r["reg"]
    # An unread feed would report every paper as somebody else's and blank the section
    # that says so, so the last reading stands.
    if reg is None:
        return _carried(prev, "arxiv_registered", "arxiv_unowned")
    return {"arxiv_registered": len(reg),
            "arxiv_unowned": [p["arxiv"] for p in r["ax"] if p["arxiv"] not in reg]}


def _orcid_profile_counts(orc: dict, d: dict) -> dict:
    """What the ORCID record says about the person, before its list of works."""
    return {"orcid_public_works": orc["works"],
            "orcid_has_canonical_url": d["has_canon"],
            "orcid_missing_variants": d["missing_variants"],
            "orcid_keywords": len(orc["keywords"]),
            "orcid_missing_keywords": d["want_kw"],
            "orcid_missing_other_pages": d["other_pages"]}


def _orcid_work_counts(r: dict, d: dict) -> dict:
    """Where the ORCID list of works disagrees with the corpus, with what to paste."""
    return {"orcid_strays_confirmed": [t for t, _p, _k in d["o_conf"]],
            "orcid_strays_unknown": [t for t, _p, _k in d["o_unk"]],
            "orcid_duplicate_groups": sorted(d["o_dups"]),
            # `orcid_remove.md` has the pairs in a table; the worklist had a pointer to
            # it and no values, which reads as "there is something here" over an empty
            # section. Both put-codes and the one DOI to paste travel with the count now,
            # so the summary can say the whole job in a line.
            "orcid_duplicate_pairs": dup_pairs(d["o_dups"], r["papers"]),
            # `should_carry` as well as `should_be`, so the worklist can name the paper and give
            # the string to paste; `carried_*` so it can link the wrong DOI. That link is the
            # evidence for the item -- following the identifier on your own record and landing on
            # somebody else's paper -- and without it the instruction is "trust us, replace this".
            "orcid_misfiled_ids": [{"put": put, "should_be": right["slug"],
                                    "should_carry": paper_doi(right),
                                    "carries": [f"{t}:{v}" for t, v in ids],
                                    "carried_doi": next((v for t, v in ids
                                                         if t == "doi"), None),
                                    "carried_title": (title_of(wrong))}
                                   for _t, put, ids, right, wrong in d["o_misfiled"]],
            "orcid_missing_papers": [p["slug"] for p in d["o_missing"]],
            "orcid_autoupdate_works": sum(d["auto_src"].values()),
            "orcid_missing_employment": d["missing_empl"],
            "orcid_missing_education": d["missing_edu"],
            "orcid_education_incomplete": [e["org"] for e in d["edu_open"]]}


def _wikidata_counts(cfg: dict, r: dict) -> dict:
    """The item, its own gaps, and how much of the corpus has an item.

    Every count is None rather than 0 when the surface did not answer, which is what
    `carry_wikidata` replaces with the previous reading.
    """
    gaps, cov = r["wd_gaps"], r["wd_cov"]
    return {"wikidata": r["wd"],
            "wikidata_gaps": (len(gaps.get("missing") or [])
                              + len(gaps.get("wrong") or [])
                              + len(gaps.get("dupes") or [])
                              + len(gaps.get("bad_aliases") or [])
                              + len(gaps.get("want_aliases") or []))
            if gaps else None,
            "wikidata_papers_present": (len(cov["present"]) if cov else None),
            "wikidata_papers_absent": (len(cov["absent"]) if cov else None),
            "wikidata_papers_unchecked": (len(cov.get("unchecked") or []) if cov
                                          else None),
            # How many of the absent ones can actually be created, which is smaller: a paper with
            # neither a DOI nor an arXiv id has no key to deduplicate against, so nothing will
            # mint an item for it. The worklist heads its section with this rather than `absent`,
            # because a heading saying 109 over a command that creates 108 is a count that does
            # not match its list.
            "wikidata_papers_creatable": (
                sum(1 for p in cov["absent"] if paper_item(p, cfg)) if cov else None)}


def audit_state(cfg: dict, args, r: dict, d: dict, path: str) -> dict:
    """The counts WORKLIST.md reads, carrying `path`'s numbers for whatever this run skipped.

    They live in `build/` because they are observed state, re-derivable from the live APIs.
    Committing them would store someone else's data and let it go stale, and an absent file
    means the worklist skips the section rather than reporting a zero.
    """
    prev = _last_reading(path)
    state = _hf_counts(r["hf"], prev)
    state.update(_name_counts(r, args, prev))
    state.update(_ownership_counts(r, prev))
    state.update(_orcid_profile_counts(r["orc"], d))
    state.update({"arxiv_total": len({p["arxiv"] for p in r["ax"]}),
                  "arxiv_stray": r["stray"]})
    state.update(_orcid_work_counts(r, d))
    state.update(_wikidata_counts(cfg, r))
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
