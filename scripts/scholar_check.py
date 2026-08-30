#!/usr/bin/env python3
"""Diff your Google Scholar profile against the corpus, to catch silent drops.

The pipeline's input is one bibliography file, so a paper missing from it -- or dropped
by the authorship gate -- is invisible to every check downstream. Scholar is the only
list maintained by a different process, so it is the only one capable of disagreeing.
Titles in, diff out: its metadata is too poor to copy (truncated author lists, venues
that are sometimes an arXiv id), so nothing here writes to `data/`.

Three outcomes per Scholar row, worst first:

    gate dropped it   Scholar attributes it to you and `build/not_mine.json` says the
                      gate excluded it. Either fix the gate (or add the title under
                      `also_mine` in overrides.yaml), or delete the Scholar row.
    not in the bib    Absent from the source bibliography -- add it there, not to the
                      output. `tasks/bib_missing.md` carries a resolved BibTeX entry
                      per paper, so the human act is pasting one.
    present           Matched a corpus record.

And the other direction: corpus records with no Scholar row, usually indexing lag.

Read-only, no login. Google serves this profile to a browser User-Agent; a challenge page
makes the check say so and exit 0 -- it is an audit, not a gate. Every unattended run
gets challenged, and the Semantic Scholar half then still runs `attributed_gaps`, a
narrower version of the same question.

Set `S2_API_KEY` if you have one -- the anonymous pool refuses often, and that is the
difference between resolving a missing paper and reporting that nobody indexes it.

Writes build/scholar_diff.json and tasks/bib_missing.md.

Usage:
    python scripts/scholar_check.py
    python scripts/scholar_check.py --quiet    # write the file, print only the counts
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (ARXIV_NS, BUILD, DATA, ROOT, TASKS, declined, get,  # noqa: E402
                    get_json, load_config, norm_title, note_fetch, read_yaml,
                    synth_bibtex, write_json, write_task)


# Scholar answers the paper-geo User-Agent with a consent interstitial and no rows.
# This is not evasion of a rate limit -- it is two GETs of a public profile page that
# has no API -- but it is the one place in the repo that does not identify itself, so
# it is the one place that says why.
BROWSER = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 "
                         "Safari/537.36",
           "Accept-Language": "en-US,en;q=0.9"}
PROFILE = ("https://scholar.google.com/citations?user={uid}&hl=en&cstart={start}"
           "&pagesize=100&view_op=list_works&sortby=pubdate")
PAGE = 100
ROW = re.compile(r'<tr class="gsc_a_tr">(.*?)</tr>', re.S)
TITLE = re.compile(r'<a [^>]*class="gsc_a_at"[^>]*>(.*?)</a>', re.S)
GRAY = re.compile(r'<div class="gs_gray">(.*?)</div>', re.S)
CITES = re.compile(r'class="gsc_a_ac[^"]*"[^>]*>(\d*)<')
YEAR = re.compile(r'class="gsc_a_h[^"]*"[^>]*>(\d{4})<')
CID = re.compile(r"citation_for_view=([^&\"]+)")
TAG = re.compile(r"<[^>]+>")
# Rows that are yours but are not papers, and which field says so. Reported apart from
# the missing papers because "add it to the bibliography" is the wrong advice for a
# patent, and worse for a proceedings volume: that one would enter the corpus as a
# paper whose every claim belongs to somebody else.
NOT_PAPER = ((re.compile(r"\bpatent\b|\bUS\d{7,}", re.I), "venue", "patent"),
             (re.compile(r"\b(thesis|dissertation)\b", re.I), "venue", "thesis"),
             (re.compile(r"\bblog\b", re.I), "venue", "blog post"),
             (re.compile(r"^proceedings of\b", re.I), "title", "proceedings volume"))


def not_paper(r: dict) -> str | None:
    """Which kind of non-paper this row is, or None for a paper.

    Which field each pattern reads is half the rule. *Proceedings of …* in the
    **venue** is where every conference paper in the corpus lives; in the **title** it
    is the volume itself, which is an editorship. Matching both patterns against one
    concatenated string cannot tell those apart, and getting it wrong in the generous
    direction costs a real paper.
    """
    for rx, field, label in NOT_PAPER:
        if rx.search(r.get(field) or ""):
            return label
    return None


def text(s: str) -> str:
    """Inner text of a Scholar cell. The titles carry markup, not just entities.

    Coined names are wrapped in a `gs_fscp` span -- "Elements of World Knowledge
    (<span>EWoK</span>): ..." -- so stripping entities alone leaves the tags in the
    title and every such row reads as a mismatch.
    """
    return " ".join(html.unescape(TAG.sub("", s)).split())


def fetch(uid: str, start: int) -> str:
    """One page of the profile, or "" -- recorded either way in the health ledger.

    Not through `common.get`, because Scholar needs the browser header and no backoff. In the
    ledger anyway: when this source stops working the symptom is a whole worklist section
    quietly absent, which reads as "nothing to report".
    """
    url = PROFILE.format(uid=uid, start=start)
    req = urllib.request.Request(url, headers=BROWSER)
    try:
        page = urllib.request.urlopen(req, timeout=40).read().decode("utf8", "replace")
        note_fetch(url, True)
        return page
    except Exception as e:                                          # noqa: BLE001
        note_fetch(url, False)
        print(f"scholar: {type(e).__name__} {e} -- skipping the check", file=sys.stderr)
        return ""


def scholar_rows(uid: str) -> tuple[list[dict], bool]:
    """Every row of the citations table, and whether the whole table was read.

    Paging stops when a page comes back short, and a page that refuses stops it too --
    which returns a prefix of the profile. Every finding the caller draws from a title
    being *absent* from this list is wrong on a prefix, so the second value says whether
    the list is one.
    """
    out, start, whole = [], 0, False
    while True:
        page = fetch(uid, start)
        if not page and start:
            # The profile answered at least once, so this is one page refusing rather than
            # Scholar refusing the profile. Asked for twice more before the read is short.
            for _ in range(2):
                time.sleep(5)
                if page := fetch(uid, start):
                    break
        if not page:
            break
        rows = ROW.findall(page)
        if not rows and start == 0:
            # Rows absent from a page that did load: a challenge, a renamed class, or a profile
            # gone private. All three mean "no data" and none means "you have no papers", so the
            # count is never reported as zero. Recorded as a failed fetch even though the HTTP call
            # succeeded -- a 200 carrying no data is the failure this source actually has, and a
            # ledger counting only transport errors would call it healthy for months.
            note_fetch(PROFILE.format(uid=uid, start=start), False)
            print("scholar: the page loaded but has no citation rows -- a challenge "
                  "page, or the profile is private. Nothing checked.", file=sys.stderr)
            break
        for r in rows:
            t = TITLE.search(r)
            g = GRAY.findall(r)
            c, y, i = CITES.search(r), YEAR.search(r), CID.search(r)
            out.append({"title": text(t.group(1)) if t else "",
                        "authors": text(g[0]) if g else "",
                        "venue": text(g[1]) if len(g) > 1 else "",
                        "year": int(y.group(1)) if y else None,
                        "citations": int(c.group(1)) if c and c.group(1) else 0,
                        "url": f"https://scholar.google.com/citations?view_op="
                               f"view_citation&hl=en&user={uid}&citation_for_view="
                               f"{i.group(1)}" if i else None})
        if len(rows) < PAGE:
            whole = True
            break
        start += PAGE
        time.sleep(2)
    return out, whole


def index(titles) -> dict[str, str]:
    """Normalised title -> the title as stored, for the ones that are non-empty."""
    return {n: t for t in titles if (n := norm_title(t))}


def find(n: str, idx: dict[str, str]) -> str | None:
    """Match a normalised title against an index, exactly then by prefix.

    Prefix matching is not fuzziness for its own sake. The same paper reaches the two
    sides through different hands: a bibliography entry stops at the colon where the
    published version carries a subtitle, Scholar sometimes keeps the arXiv title
    after a venue retitle. 40 characters of agreement is long enough that two
    different papers sharing it would be a naming collision worth knowing about
    anyway.
    """
    if n in idx:
        return idx[n]
    for k, v in idx.items():
        if len(n) >= 40 and len(k) >= 40 and (k.startswith(n) or n.startswith(k)):
            return v
    return None


STOP = {"the", "of", "a", "an", "and", "for", "to", "in", "on", "is", "are", "with",
        "your", "you", "can", "how", "as", "at", "by", "its", "it", "be", "from",
        "we", "do", "does", "using", "via", "not", "or", "that", "this", "all"}


def words(t: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", t.lower()) if w not in STOP}


def head(t: str) -> str:
    """The part before the first colon or question mark -- usually the coined name."""
    return re.split(r"[:?]", t, maxsplit=1)[0].strip().lower()


def variant_score(a: str, b: str) -> tuple[float, str] | None:
    """Whether two titles are plausibly one paper renamed, and on what evidence.

    Two signals, either sufficient. Word overlap catches a reworded subtitle; an identical
    coined name before the colon catches a fully rewritten one, which overlap cannot --
    "LLM Hypnosis: Exploiting User Feedback ..." and "LLM Hypnosis: Characterizing the
    Fragility of RLHF ..." share four words out of fifteen.

    Reported as a question, not a fact, so a loose threshold is the right side to err on: a
    wrong pair costs one line a human dismisses, and a missed pair costs a duplicated public
    page plus the same paper reported twice, in two distant sections.
    """
    ha, hb = head(a), head(b)
    if ha and ha == hb and len(ha) >= 8:
        return 1.0, f"same name before the colon: {ha!r}"
    wa, wb = words(a), words(b)
    if not wa or not wb:
        return None
    j = len(wa & wb) / len(wa | wb)
    return (j, f"{len(wa & wb)} of {len(wa | wb)} words shared") if j >= 0.35 else None


def same_paper(a: str, b: str) -> bool:
    """Are these two title strings the same title, allowing for house style.

    Loose on purpose, and only safe because of who the two strings belong to: both sides
    are already known to be yours -- a corpus paper against a Scholar row, or against
    your own Semantic Scholar author record. Use `same_work` for a title that came out
    of an index.
    """
    if norm_title(a) == norm_title(b):
        return True
    sc = variant_score(a, b)
    return bool(sc and sc[0] >= 0.5)


def first_word(t: str) -> str:
    """A title's first subject-matter word, articles and prepositions skipped."""
    return next((w for w in re.findall(r"[a-z0-9]+", t.lower()) if w not in STOP), "")


def same_work(a: str, b: str) -> bool:
    """`same_paper`, plus the same first content word. For pairing against an index.

    `same_paper` compares two titles already known to be the author's, where a wrong pair
    costs one dismissed line. An index answers from every paper ever published, where the
    same threshold pastes a stranger's paper into the bibliography -- word overlap alone
    accepted "Attention is all you need" against "Tensor Product Attention Is All You Need".

    Legitimate variants keep their opening, such as a dropped subtitle or an appended venue
    retitle, while prepended words change the subject. A title rearranged across the colon
    comes back as a near-miss line to confirm rather than resolving on its own.
    """
    if norm_title(a) == norm_title(b):
        return True
    return bool(same_paper(a, b) and (w := first_word(a)) and w == first_word(b))


def arxiv_titles() -> dict[str, str] | None:
    """slug -> the title arXiv states, for the papers where it differs from ours.

    `collect.py` compares every paper that carries an arXiv id and writes only the
    disagreements, so a slug absent from the file is an answer rather than a gap: arXiv and
    the bibliography agree on that paper's title.

    `None` means the file is not there, which is the collect step not having run. `{}` and
    `None` would otherwise both mean "arXiv disagrees with nothing", and that reading turns
    every title variant into `stale_side`'s reassuring outcome.
    """
    try:
        with open(os.path.join(BUILD, "title_diffs.json")) as f:
            return {d["slug"]: d["arxiv_says"] for d in json.load(f)
                    if d.get("slug") and d.get("arxiv_says")}
    except (OSError, ValueError, AttributeError, TypeError):
        return None


def stale_side(scholar: str, p: dict, diffs: dict[str, str] | None) -> tuple[str, str]:
    """Which of the two titles is out of date, on arXiv's evidence.

    arXiv holds the current title and a run has already fetched it, so this is mostly not the
    judgement call it looks like. Four outcomes, of which only `open` is a decision:

        bib      arXiv states the Scholar title, so the bibliography entry is behind. The
                 same finding `collect.py` reports as `title differs from arXiv`, and the
                 fix is one edit upstream rather than an override here.
        scholar  arXiv states our title, so the Scholar row kept an earlier one. Nothing to
                 fix: editing the row changes what it displays, not which citations Scholar
                 clusters under it.
        open     no arXiv record, or arXiv agrees with neither. Yours to decide.
        unknown  nothing fetched arXiv's titles this run, so there is no evidence either
                 way. Not `open`, which states that arXiv was asked.
    """
    if diffs is None:
        return "unknown", ""
    says = diffs.get(p.get("slug") or "")
    if says:
        return ("bib", says) if same_paper(says, scholar) else ("open", says)
    return ("scholar", p.get("title") or "") if p.get("arxiv") else ("open", "")


def searchable(title: str) -> str:
    """A title as a search phrase: words only.

    Both APIs index words, and both parse punctuation in the *query* -- so a title
    carrying a colon or a question mark returns nothing at all rather than fewer
    results. `Llm merging: Building llms efficiently through merging` finds zero papers
    on arXiv; the same words without the colon find the paper.
    """
    return " ".join(re.findall(r"[A-Za-z0-9]+", title))


def run_len(a: str, b: str) -> int:
    """Longest run of consecutive words two titles share.

    The near-miss gate against an index, stricter than `variant_score` because an index
    answers from the whole literature: there, 4 of 9 shared words is *Framework-based
    Roguelike Game for AI/ML Education* against *A Statistical Framework for Game-Based AI
    Evaluation*, a stranger's paper offered as "the same paper renamed?".

    A run separates them on the real cases. The genuine rename in this corpus keeps five
    words in order ("... Building LLMs Efficiently through Merging"); the Roguelike paper
    shares no two adjacent words with anything of yours.
    """
    wa, wb = re.findall(r"[a-z0-9]+", a.lower()), re.findall(r"[a-z0-9]+", b.lower())
    best = 0
    for i in range(len(wa)):
        for j in range(len(wb)):
            n = 0
            while i + n < len(wa) and j + n < len(wb) and wa[i + n] == wb[j + n]:
                n += 1
            best = max(best, n)
    return best


NEAR_RUN = 4


def near_miss(got: str, title: str) -> bool:
    """Is an index's non-matching answer worth showing as a possible rename?"""
    return run_len(got, title) >= NEAR_RUN


S2_FIELDS = "title,year,venue,authors,externalIds,publicationTypes,paperId"


def s2_mine(cfg: dict) -> list[dict] | None:
    """Every paper Semantic Scholar attributes to you, or None if it did not answer.

    The author endpoint, not search: two requests for the whole check instead of one per
    title, already depended on by `collect.py` every run, and it answers a better question --
    a paper on your author record is one S2 attributes to *you*, so a hit resolves "is it
    yours" at the same time as the metadata. Unauthenticated search answers 429 too often to
    be usable here.
    """
    out: list[dict] = []
    for aid in (cfg.get("ids") or {}).get("semantic_scholar") or []:
        d = get_json(f"https://api.semanticscholar.org/graph/v1/author/{aid}/papers"
                     f"?fields={S2_FIELDS}&limit=500")
        if d is None:
            return None
        out.extend((d.get("data") or []))
        time.sleep(1)
    return out


def attributed_gaps(attributed: list[dict], papers: list[dict], corpus: dict[str, str],
                    gated: dict[str, str]) -> tuple[list[dict], list[dict]]:
    """Papers an index attributes to you that the corpus has never received.

    Returns `(gaps, unverifiable)` -- the rows worth acting on, and the rows S2 holds with
    no external identifier, which are counted on stderr and written to
    `build/scholar_diff.json` but not listed.

    A floor rather than a substitute for the Scholar leg's `not_in_corpus`. On this corpus
    Scholar finds three absent papers and this leg finds none of them, because S2's author
    record does not hold them. What it catches is a new paper that reached an index and not
    the bibliography.

    Rows carrying no identifier, patents, and proceedings volumes are all dropped.
    """
    ids = {v.lower() for p in papers for v in
           (p.get("arxiv"), (p.get("doi") or "").removeprefix("doi:")) if v}
    out, unverifiable, seen = [], [], set()
    for p in attributed:
        ext = {k: str(v) for k, v in (p.get("externalIds") or {}).items() if v}
        ax, doi = ext.get("ArXiv", ""), ext.get("DOI", "")
        n = norm_title(p.get("title"))
        if not n or n in seen:
            continue
        # Identifier before title, and both before reporting. An arXiv id or a DOI is
        # the same paper or it is not; a title has to survive S2's capitalisation and the
        # rename between preprint and proceedings.
        if ax.lower() in ids or doi.lower() in ids or find(n, corpus) or find(n, gated):
            continue
        seen.add(n)
        row = {"title": p.get("title") or "", "year": p.get("year"),
               "venue": p.get("venue") or "", "arxiv": ax or None, "doi": doi or None,
               "url": f"https://www.semanticscholar.org/paper/{p['paperId']}"
                      if p.get("paperId") else None}
        # The Scholar leg's patents-and-volumes filter, for the same reason: "add it to
        # the bibliography" is wrong advice for a patent and harmful for a proceedings
        # volume, which would enter the corpus as a paper whose every claim is somebody
        # else's.
        if not_paper(row):
            continue
        (out if (ax or doi) else unverifiable).append(row)
    return (sorted(out, key=lambda r: -(r.get("year") or 0)),
            sorted(unverifiable, key=lambda r: -(r.get("year") or 0)))


def report_gaps(gaps: list[dict], unverifiable: list[dict], quiet: bool) -> None:
    """The lines the unattended run exists to be able to print."""
    if gaps:
        print(f"  {len(gaps)} paper(s) on your Semantic Scholar author record that the "
              f"corpus does not have -- add to the bibliography, or to the authorship "
              f"gate if not yours:", file=sys.stderr)
        if not quiet:
            for r in gaps[:20]:
                print(f"    {r['year'] or '????'} {r['title'][:56]}  "
                      f"({r.get('arxiv') or r.get('doi')})", file=sys.stderr)
            if len(gaps) > 20:
                print(f"    ... and {len(gaps) - 20} more in "
                      f"build/scholar_diff.json", file=sys.stderr)
    if unverifiable:
        # Counted, never listed. The count exists so that a reader comparing the author
        # record's size against the corpus can see where the difference went, and so that
        # the day it jumps from six to sixty is a day somebody notices.
        print(f"  {len(unverifiable)} author-record row(s) carry no arXiv id or DOI -- "
              f"S2 stubs, not checkable from here (build/scholar_diff.json)",
              file=sys.stderr)


def from_s2(title: str, mine: list[dict],
            strict: bool = False) -> tuple[dict | None, str]:
    """Match a title against the fetched author record. No request of its own.

    `strict` because `from_s2_search` reuses this to read a *search* answer, and the two
    candidate sets are not the same kind of thing: your author record holds papers
    Semantic Scholar already believes are yours, where a loose title match is recovering
    a retitle, and the search endpoint holds the literature, where it is picking up
    somebody else's paper.
    """
    ok = same_work if strict else same_paper
    near = ""
    for p in mine:
        got = p.get("title") or ""
        if not ok(got, title):
            if near_miss(got, title):
                near = near or got
            continue
        ext = p.get("externalIds") or {}
        kinds = p.get("publicationTypes") or []
        return {"title": got, "year": str(p.get("year") or ""),
                "authors": [a.get("name") for a in p.get("authors") or []
                            if a.get("name")],
                "venue": p.get("venue") or "",
                "doi": ext.get("DOI"), "arxiv": ext.get("ArXiv"),
                "type": "inproceedings" if "Conference" in kinds else "article",
                "url": f"https://www.semanticscholar.org/paper/{p['paperId']}"}, ""
    return None, near


def from_arxiv(title: str) -> tuple[dict | None, str, bool]:
    """The arXiv record for a title, the nearest title offered, and whether it replied.

    Scholar gives a title, a year and a truncated author list -- enough to notice a
    paper is missing, not enough to cite it. arXiv answers a title query with the
    authors in full, so an entry that reaches `tasks/bib_missing.md` compiles.
    """
    q = urllib.parse.quote(f'ti:"{searchable(title)}"')
    raw = get(f"http://export.arxiv.org/api/query?search_query={q}&max_results=5",
              retries=2)
    try:
        entries = ET.fromstring(raw).findall("a:entry", ARXIV_NS) if raw else None
    except ET.ParseError:
        entries = None
    if entries is None:
        return None, "", False
    near = ""
    for e in entries:
        got = " ".join((e.findtext("a:title", "", ARXIV_NS) or "").split())
        if not same_work(got, title):
            if near_miss(got, title):
                near = near or got
            continue
        tail = (e.findtext("a:id", "", ARXIV_NS) or "").split("/abs/")[-1]
        ax = tail.rsplit("v", 1)[0] if "v" in tail.split("/")[-1] else tail
        pub = e.findtext("a:published", "", ARXIV_NS) or ""
        return {"title": got, "arxiv": ax, "year": pub[:4],
                "authors": [n.text for n in e.findall("a:author/a:name", ARXIV_NS)
                            if n.text],
                "venue": e.findtext("ar:journal_ref", "", ARXIV_NS)
                         or f"arXiv preprint arXiv:{ax}",
                "url": f"https://arxiv.org/abs/{ax}"}, "", True
    return None, near, True


CROSSREF = ("https://api.crossref.org/works?rows=5&select=title,author,issued,DOI,"
            "container-title,type&query.bibliographic=")


def from_crossref(title: str) -> tuple[dict | None, str, bool]:
    """The Crossref record for a title, the nearest title offered, and whether it replied.

    Covers what the first two resolvers cannot: a paper never preprinted and not on your
    author record, which is most of what goes missing -- competition reports, workshop papers,
    proceedings-only papers. The publisher registered the DOI, and the DOI is the field that
    makes a BibTeX entry worth pasting, being what ORCID and every citation manager group on.

    Its ranking is fuzzy -- an unmatched query returns five plausible strangers rather than
    nothing -- so the query proposes and `same_work` decides.
    """
    d = get_json(CROSSREF + urllib.parse.quote(searchable(title)), retries=2)
    if d is None:
        return None, "", False
    near = ""
    for it in ((d.get("message") or {}).get("items") or []):
        got = " ".join(((it.get("title") or [""])[0] or "").split())
        if not same_work(got, title):
            if near_miss(got, title):
                near = near or got
            continue
        parts = [" ".join(x for x in (a.get("given"), a.get("family")) if x)
                 for a in it.get("author") or []]
        when = ((it.get("issued") or {}).get("date-parts") or [[None]])[0]
        return {"title": got, "year": str(when[0] or ""), "authors": parts,
                "venue": (it.get("container-title") or [""])[0],
                "doi": it.get("DOI"),
                "type": ("inproceedings" if it.get("type") == "proceedings-article"
                         else "article"),
                "url": f"https://doi.org/{it['DOI']}"}, "", True
    return None, near, True


OPENREVIEW = "https://api2.openreview.net/notes/search?limit=10&term="

# "NeurIPS 2025 LLM Evaluation Workshop Poster" -- the last word is how the paper was
# presented, not where. A bibliography that says "Poster" is describing the furniture.
_DECISION = re.compile(r"\s+(virtual)?(poster|oral|spotlight|talk|paper)$", re.I)


def val(c: dict, k: str):
    """OpenReview's api2 wraps every content field as {"value": ...}; api1 did not."""
    v = (c or {}).get(k)
    return v.get("value") if isinstance(v, dict) else v


def published(c: dict) -> bool:
    """Did this OpenReview note actually get in anywhere.

    OpenReview hosts the submission as well as the paper, so a note whose venue reads *ICLR
    2026 Conference Withdrawn Submission* would otherwise be cited as an `@inproceedings`
    with `booktitle = {ICLR 2026}`.

    One rule covers every rejected state, since OpenReview names them all the same way. A
    note that did not get in lives in a group whose last path segment ends in `Submission` --
    `Withdrawn_Submission`, `Desk_Rejected_Submission`, `Rejected_Submission`, or plain
    `Submission` while review is still running. An accepted paper's `venueid` ends in
    `Conference`, `Workshop`, or the workshop's name. `Submitted to ...` catches the venues
    that put the state in the display string and leave the id off.
    """
    vid, venue = (val(c, "venueid") or "").strip(), (val(c, "venue") or "").strip()
    if venue.lower().startswith("submitted to") or venue.lower().endswith("submission"):
        return False
    return bool(vid) and not vid.rsplit("/", 1)[-1].lower().endswith("submission")


def from_openreview(title: str) -> tuple[dict | None, str, bool]:
    """The OpenReview record for a title, the nearest title offered, and whether it replied.

    The resolvers above share a blind spot the size of a publication venue: a workshop paper
    is not preprinted, gets no registered DOI, and reaches Semantic Scholar late or never.

    Three filters, all load-bearing. `same_work` decides, as everywhere an index answers:
    this endpoint reports thousands of loosely ranked matches for any query, so it proposes
    and never decides. A note is accepted only if it carries an author list -- reviews and
    comments are notes too and come back from the same search, and a review's title is
    sometimes the paper's, so a title match alone would produce an entry whose authors are
    the reviewers. And `published` refuses a submission that was withdrawn, rejected, or is
    still under review.
    """
    d = get_json(OPENREVIEW + urllib.parse.quote(searchable(title)), retries=2)
    if d is None:
        return None, "", False
    near = ""
    for n in (d.get("notes") or []):
        c = n.get("content") or {}
        got = " ".join((val(c, "title") or "").split())
        if not got:
            continue
        if not same_work(got, title):
            if near_miss(got, title):
                near = near or got
            continue
        authors = [a for a in (val(c, "authors") or []) if a]
        if not authors or not published(c):
            continue
        vid = (val(c, "venueid") or "").strip()
        venue = _DECISION.sub("", (val(c, "venue") or "").strip())
        # The venue string carries the year ("NeurIPS 2025 LLM Evaluation Workshop"), and
        # so does the venue id. Both beat the note's timestamps, which are when it was
        # uploaded and can fall on the wrong side of a new year.
        m = re.search(r"\b(19|20)\d{2}\b", f"{venue} {vid}")
        return {"title": got, "year": m.group(0) if m else "",
                "authors": authors, "venue": venue,
                # For `collect.from_openreview_titles`, which builds a corpus record from
                # this and needs the two things a citation does not: the abstract a page
                # renders, and the forum id, which is the paper's stable address here --
                # a note id changes when a revision is filed, the forum does not.
                "abstract": " ".join((val(c, "abstract") or "").split()) or None,
                "openreview": n.get("forum") or n["id"],
                # Workshop and conference papers are both `inproceedings`, and they are
                # nearly all of what OpenReview hosts itself. The exception is a note
                # mirrored from dblp or deposited as a public article, where the venue is
                # a journal -- `inproceedings` there would assert proceedings that do not
                # exist, the same mistake `published` guards on the other axis.
                "type": ("article"
                         if "/journals/" in vid or vid.endswith("Public_Article")
                         else "inproceedings"),
                "url": f"https://openreview.net/forum?id={n['id']}"}, "", True
    return None, near, True


def from_s2_search(title: str) -> tuple[dict | None, str, bool]:
    """S2's title search, last and deliberately impatient.

    The only index that held the one genuinely resolvable paper here -- a competition report
    on nobody's arXiv and on no author record, indexed under a longer title than Scholar
    displays -- so it is worth asking. But unauthenticated search answers 429 from a pool
    shared with the world. Three tries at the shared backoff is ~12s per paper: enough to win
    when the pool is free, short enough that a rate-limited day costs the audit half a minute
    and says so rather than stalling it.
    """
    q = urllib.parse.quote(searchable(title))
    d = get_json(f"https://api.semanticscholar.org/graph/v1/paper/search?query={q}"
                 f"&limit=5&fields={S2_FIELDS}", retries=3)
    if d is None:
        return None, "", False
    rec, near = from_s2(title, d.get("data") or [], strict=True)
    return rec, near, True


S2_RECORD = "your Semantic Scholar author record"

# Every index `resolve` asks a title question of, in the order it asks them. A list and
# not four calls, because `bib_payload` has to name the ones that had nothing: with two
# copies of these names, adding a resolver to one of them leaves the other reporting "not
# in all three indexes" after asking four -- which is how OpenReview's arrival went
# unmentioned in the file a human actually reads.
OPEN_INDEXES = ((from_arxiv, "arXiv"), (from_crossref, "Crossref"),
                (from_openreview, "OpenReview"),
                (from_s2_search, "Semantic Scholar search"))


def resolve(title: str, mine: list[dict] | None) -> tuple[dict | None, str, list[str]]:
    """Find a citable record for a Scholar title: (record, nearest title, unreachable).

    Cheapest and most authoritative first, and `unreachable` names the indexes that did
    not answer. That last part is load-bearing: reporting "no index has this paper" when
    an index was merely rate-limited is the one failure mode here that puts a false
    statement in front of a human, and it is the likely one, because the index most
    worth asking is the one most likely to refuse.
    """
    down = []
    rec, near = from_s2(title, mine or [])
    if rec:
        return rec, "", down
    if mine is None:
        down.append(S2_RECORD)
    for fn, name in OPEN_INDEXES:
        rec, got, ok = fn(title)
        if rec:
            return rec, "", down
        near = near or got
        if not ok:
            down.append(name)
    return None, near, down


BIB_HEAD = """# Papers on your Scholar profile that the bibliography does not have

Written by `scripts/scholar_check.py`. Each entry below is a paper Google Scholar
attributes to you and [`{bib}`]({bib}) does not contain, so the pipeline never
received it and no amount of work inside this repo will produce a page for it.

**The fix is upstream, and it is one paste.** Add the entries you want to the source
bibliography, then `python update.py --refresh-bib`. Nothing here writes to that repo:
it is your publication list, and what belongs on it is a claim about your own work.

Two things to check per entry, because neither is decidable from a Scholar row.
**Is it yours** — Scholar merges a namesake's paper into a profile now and then, and a
wrong entry here would become a page under your name. A resolved entry is weaker
evidence than it looks: an index matches on title and knows nothing about whose paper it
is. Titles that merely *contain* yours are refused, so the resolvers no longer hand you
*Tensor Product Attention Is All You Need* — but a genuine namesake collision still
reads as a match. **Is the entry right** — a resolved entry carries the index's author
list and venue, not yours; a stub carries only what Scholar displayed, which is a
truncated author list and a venue string that is sometimes an arXiv id.

Patents, theses, blog posts and proceedings volumes never reach this file -- the check
classifies those and reports them apart. An entry marked `UNRESOLVED` names the indexes
that were asked and had nothing, which for a proceedings-only paper usually means nobody
registered it anywhere machine-readable. Pasting that stub as it stands would put a
`TODO` in your bibliography. A paper on OpenReview that was withdrawn, rejected, or is
still under review resolves to nothing on purpose: there is no venue to cite yet.

"""


def bib_payload(rows: list[dict], bib_url: str, mine: list[dict] | None,
                ruled_out: list[dict] | None = None) -> tuple[str, int, int, int]:
    """Write `tasks/bib_missing.md`: (path, papers, resolved, worth retrying).

    Absent when nothing is missing, and absent when everything missing was declined -- a file
    that says "none" is one more thing to read and disbelieve. `ruled_out` is named at the
    foot of the page when there is a page.

    A near miss is printed rather than pasted: the indexes routinely hold a paper under a
    close-but-different title, which is exactly where an automatic match would write somebody
    else's paper into a bibliography under a citation key that looks checked.
    """
    path = os.path.join(TASKS, "bib_missing.md")
    if not rows:
        if os.path.exists(path):
            os.remove(path)
        return path, 0, 0, 0
    out, done, retry = [BIB_HEAD.format(bib=bib_url)], 0, 0
    for i, r in enumerate(sorted(rows, key=lambda r: -(r.get("citations") or 0))):
        if i:
            time.sleep(3)                   # arXiv asks for one query every 3 seconds
        rec, near, down = resolve(r["title"], mine)
        cites = r.get("citations") or 0
        out.append(f"## {r['title']}\n")
        out.append(f"- {cites} citation{'s' * (cites != 1)}, "
                   f"{r.get('year') or 'year unknown'}, Scholar says *"
                   f"{r.get('venue') or 'no venue'}*")
        if r.get("url"):
            out.append(f"- [the Scholar row]({r['url']})")
        if rec:
            done += 1
            where = (f"[arXiv:{rec['arxiv']}](https://arxiv.org/abs/{rec['arxiv']})"
                     if rec.get("arxiv") else
                     f"[doi:{rec['doi']}]({rec['url']})" if rec.get("doi")
                     else f"[the record]({rec['url']})")
            out.append(f"- resolved: {where}, {len(rec['authors'])} authors\n")
            out.append("```bibtex\n" + synth_bibtex(rec) + "\n```\n")
        else:
            # Naming the indexes is the point: "not found" and "not asked" are
            # different facts, and only one of them is worth acting on.
            asked = [n for n in (S2_RECORD, *(n for _, n in OPEN_INDEXES))
                     if n not in down]
            out.append(f"- **UNRESOLVED** — not in "
                       f"{', '.join(asked[:-1])} or {asked[-1]}." if len(asked) > 1
                       else f"- **UNRESOLVED** — not in {asked[0]}." if asked
                       else "- **UNRESOLVED** — no index answered.")
            if down:
                retry += 1
                out.append(f"- {' and '.join(down)} did not answer — a re-run may "
                           f"resolve this without any work from you.")
            if near:
                out.append(f"- nearest indexed title: *{near}* — the same paper "
                           f"renamed, or a different one?")
            out.append("")
            out.append("```bibtex\n@misc{TODO,\n"
                       f"  title        = {{{r['title']}}},\n"
                       f"  year         = {{{r.get('year') or ''}}},\n"
                       f"  note         = {{TODO: authors, venue, DOI}}\n}}\n```\n")
    if ruled_out:
        # Named, not silently absent. The point of this page is that Scholar and the
        # bibliography disagree, so a reader counting the rows here against the count on
        # the Scholar profile needs to know the difference is a decision and not a bug.
        out.append("\n---\n")
        out.append(f"Also absent, and deliberately: "
                   + ", ".join(f"*{r['title']}*" for r in ruled_out)
                   + ". Declined in [`data/declines.yaml`](../data/declines.yaml) — delete "
                     "the line there and the entry comes back with a resolved BibTeX "
                     "block like the ones above.\n")
    os.makedirs(TASKS, exist_ok=True)
    write_task(path, "\n".join(out).rstrip() + "\n")
    return path, len(rows), done, retry


def partial_answer(uid: str, rows: list, papers: list, attributed: list | None,
                   gaps: list, stubs: list, quiet: bool) -> None:
    """Write and report what the author record could answer when Scholar refused.

    Google refusing is the normal case from a datacenter IP and says nothing about the
    corpus, so this writes rather than nothing -- a file absent and a file reporting no gaps
    are indistinguishable to every reader downstream, and only one of them is true.

    A page that refused part-way counts the same. The profile pages at 100 and this corpus
    is larger, so a lost second page puts every paper on it into `not_on_scholar`, under a
    heading asking the author to add papers Scholar has.
    """
    write_json(
        os.path.join(BUILD, "scholar_diff.json"),
        {"scholar_profile": uid, "scholar_rows": len(rows),
         "scholar_answered": False, "corpus": len(papers),
         "s2_answered": attributed is not None,
         "not_in_corpus_by_index": gaps,
         "index_stubs_no_id": stubs}, indent=1)
    read = ("profile unavailable" if not rows
            else f"read {len(rows)} row(s), then a page refused")
    print(f"scholar: {read}; author record answered for "
          f"{len(attributed or [])} paper(s)", file=sys.stderr)
    report_gaps(gaps, stubs, quiet)


def sort_rows(rows: list, mine: dict, slug: dict,
              gated: dict) -> tuple[set[str], list, list]:
    """Each Scholar row against the corpus, as (matched corpus titles, gated, unmatched).

    Matched rows gain a `slug`, unmatched ones a `kind`. Keyed on the *corpus* title, never
    the Scholar one: a prefix match means the two strings differ, so recording the Scholar
    side leaves the corpus paper looking unmatched and reports every retitle twice, in two
    different sections.
    """
    seen: set[str] = set()
    in_gate, missing = [], []
    for r in rows:
        n = norm_title(r["title"])
        if not n:
            continue
        if hit := find(n, mine):
            seen.add(norm_title(hit))
            r["slug"] = slug.get(norm_title(hit))
        elif find(n, gated):
            in_gate.append(r)
        else:
            r["kind"] = not_paper(r) or "paper"
            missing.append(r)
    return seen, in_gate, missing


def pair_leftovers(missing: list, papers: list,
                   unmatched: dict) -> tuple[list, list, set]:
    """Leftover Scholar rows paired against the corpus, as (retitles, duplicates, slugs hit).

    Pairs against the whole corpus, not just its unmatched part, because which side the pair
    lands on decides who has the work: paired with an unmatched paper it is one paper under
    two titles, and paired with a paper that already matched another row it is Scholar
    listing the same work twice, which nothing here can fix.
    """
    variants, dupes, taken = [], [], set()
    for r in sorted(missing, key=lambda r: -r["citations"]):
        best = None
        for p in papers:
            if p.get("slug") in taken:
                continue
            if sc := variant_score(r["title"], p.get("title") or ""):
                if not best or sc[0] > best[0][0]:
                    best = (sc, p)
        if not best:
            continue
        (score, why), p = best
        taken.add(p["slug"])
        row = {"scholar": r["title"], "scholar_url": r.get("url"),
               "corpus": p.get("title"), "slug": p["slug"],
               "score": round(score, 2), "why": why}
        (variants if p["slug"] in unmatched else dupes).append(row)
    return variants, dupes, taken


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true",
                    help="write build/scholar_diff.json, print only the counts")
    args = ap.parse_args()
    cfg = load_config()
    uid = (cfg.get("ids") or {}).get("google_scholar")
    if not uid:
        print("scholar: no ids.google_scholar in config.yaml -- nothing to check",
              file=sys.stderr)
        return

    papers = (read_yaml(os.path.join(DATA, "papers.yaml")) or {}).get("papers", [])
    mine = index(p.get("title") for p in papers)
    slug = {norm_title(p.get("title")): p.get("slug") for p in papers}
    try:
        with open(os.path.join(BUILD, "not_mine.json")) as f:
            dropped = json.load(f)
    except (OSError, ValueError):
        dropped = []
    gated = index(r.get("title") for r in dropped)

    # Fetched before the Scholar leg and used by both, so that the expensive half of
    # this check still produces an answer on the runs where Google refuses. One request
    # per author id, and `bib_payload` below reuses the same list rather than asking
    # again.
    attributed = s2_mine(cfg)
    gaps, stubs = attributed_gaps(attributed or [], papers, mine, gated)

    rows, whole = scholar_rows(uid)
    if not rows or not whole:
        partial_answer(uid, rows, papers, attributed, gaps, stubs, args.quiet)
        return

    seen, in_gate, missing = sort_rows(rows, mine, slug, gated)
    absent = [p for p in papers if norm_title(p.get("title")) not in seen]
    unmatched = {p["slug"]: p for p in absent}
    variants, dupes, taken = pair_leftovers(missing, papers, unmatched)
    diffs = arxiv_titles()
    for v in variants:
        v["stale"], v["arxiv_says"] = stale_side(v["scholar"], unmatched[v["slug"]],
                                                 diffs)
    paired = {v["scholar"] for v in variants} | {d["scholar"] for d in dupes}
    missing = [r for r in missing if r["title"] not in paired]
    # The identifier travels with the row because this list is the only one here whose
    # remedy is *adding* something to Scholar rather than correcting it, and Scholar's
    # "Add article manually" form wants a link. A title alone would make the reader
    # search for their own paper.
    absent = [{"slug": p.get("slug"), "title": p.get("title"),
               "title_display": p.get("title_display") or p.get("title"),
               "year": p.get("year"),
               "citations": p.get("citations"), "arxiv": p.get("arxiv"),
               "doi": p.get("doi"), "url": p.get("url")}
              for p in absent if p["slug"] not in taken]

    os.makedirs(BUILD, exist_ok=True)
    out = {"scholar_profile": uid, "scholar_rows": len(rows), "scholar_answered": True,
           "corpus": len(papers), "matched": len(seen),
           "s2_answered": attributed is not None,
           "not_in_corpus_by_index": gaps, "index_stubs_no_id": stubs,
           "gate_dropped": sorted(in_gate, key=lambda r: -r["citations"]),
           "title_variants": sorted(variants, key=lambda v: -v["score"]),
           "scholar_duplicates": sorted(dupes, key=lambda v: -v["score"]),
           "not_in_corpus": sorted(missing, key=lambda r: -r["citations"]),
           "not_on_scholar": sorted(absent, key=lambda p: -(p.get("citations") or 0)),
           # Per-row counts for the matched rows, which no other file has: Scholar
           # normally counts *more* than the API indexes, so a row counting fewer is
           # the signature of a split Scholar record. `scholar_strays.py` reads it.
           "paired": [{"slug": r["slug"], "scholar": r["title"],
                       "scholar_citations": r.get("citations") or 0,
                       "scholar_url": r.get("url")}
                      for r in rows if r.get("slug")]}
    write_json(os.path.join(BUILD, "scholar_diff.json"), out, indent=1)

    print(f"scholar: {len(rows)} rows, {len(seen)}/{len(papers)} corpus papers "
          f"matched", file=sys.stderr)
    for side, what in (("bib", "the bibliography title is behind arXiv -- fix the "
                               "entry in the source .bib"),
                       ("open", "decide which is canonical, then set it in "
                                "data/overrides.yaml")):
        group = [v for v in variants if v["stale"] == side]
        if not group:
            continue
        print(f"  {len(group)} paper(s) under two titles -- {what}:", file=sys.stderr)
        if not args.quiet:
            for v in group:
                print(f"    scholar: {v['scholar'][:64]}", file=sys.stderr)
                print(f"    corpus : {v['corpus'][:64]}   ({v['why']})",
                      file=sys.stderr)
                if v["arxiv_says"] and side == "open":
                    print(f"    arxiv  : {v['arxiv_says'][:64]}", file=sys.stderr)
    if stale_rows := [v for v in variants if v["stale"] == "scholar"]:
        print(f"  {len(stale_rows)} Scholar row(s) kept an older title than arXiv and "
              f"the corpus -- nothing to fix", file=sys.stderr)
    if blind := [v for v in variants if v["stale"] == "unknown"]:
        print(f"  {len(blind)} paper(s) under two titles that nothing asked arXiv about "
              f"-- run `python update.py --step collect`, which writes "
              f"build/title_diffs.json", file=sys.stderr)
    if dupes:
        print(f"  {len(dupes)} paper(s) listed twice on Scholar -- merge them there "
              f"(nothing here can):", file=sys.stderr)
        if not args.quiet:
            for d in dupes:
                print(f"    {d['slug']}  <-  {d['scholar'][:56]}", file=sys.stderr)
    if in_gate:
        print(f"  {len(in_gate)} Scholar paper(s) the authorship gate excluded "
              f"-- this is the one that matters:", file=sys.stderr)
        if not args.quiet:
            for r in in_gate:
                print(f"    [{r['citations']:>5} cites] {r['title'][:66]}",
                      file=sys.stderr)
    # Split on `data/declines.yaml` before resolving anything. A row the author has ruled
    # out of the bibliography is not a gap: it was costing an arXiv and a Crossref round
    # trip every run to produce a pasteable entry for a paste that is never going to
    # happen, and `WORKLIST.md` -- which reads the same file -- had already stopped
    # listing it, so the payload and the summary disagreed about how many were open.
    real, ruled_out = [], []
    for r in sorted((r for r in missing if r["kind"] == "paper"),
                    key=lambda r: -(r.get("citations") or 0)):
        (ruled_out if declined(r["title"]) else real).append(r)
    path, _, done, retry = bib_payload(
        real, (cfg.get("sources") or {}).get("bibtex_url") or "", attributed or [],
        ruled_out)
    if ruled_out:
        print(f"  {len(ruled_out)} more absent because you ruled them out in "
              f"data/declines.yaml: "
              + ", ".join(f"{r['title'][:44]!r}" for r in ruled_out), file=sys.stderr)
    if real:
        how = (f"{done} with a pasteable BibTeX entry" if done else
               "none resolvable, though an index was down for "
               f"{retry} of them -- a re-run may resolve those" if retry else
               "none of them known to any index")
        print(f"  {len(real)} Scholar paper(s) absent from the bibliography, {how} "
              f"-- {os.path.relpath(path, ROOT)}:", file=sys.stderr)
        if not args.quiet:
            for r in real[:20]:
                print(f"    [{r['citations']:>5} cites] {r['year'] or '????'} "
                      f"{r['title'][:60]}", file=sys.stderr)
            if len(real) > 20:
                print(f"    ... and {len(real) - 20} more in "
                      f"build/scholar_diff.json", file=sys.stderr)
    other = [r for r in missing if r["kind"] != "paper"]
    if other:
        kinds = Counter(r["kind"] for r in other)
        how = ", ".join(f"{n} {k}" + "s" * (n != 1) for k, n in kinds.most_common())
        print(f"  {len(other)} Scholar row(s) that are not papers ({how}) "
              f"-- ignored on purpose", file=sys.stderr)
    if absent:
        cited = [p for p in absent if (p.get("citations") or 0) > 0]
        # "with no Scholar row" is the measurement; "worth adding to your profile" is an
        # inference this check cannot make. The profile lists one title per record, so a paper
        # Scholar merged into another record is indistinguishable from one it does not have --
        # and adding a merged paper by hand splits its future citations. All five cases the
        # stronger wording named were merges.
        print(f"  {len(absent)} corpus paper(s) whose title is not in the Scholar listing"
              + (f", {len(cited)} of them cited -- check for a merge before adding any"
                 if cited else " (Scholar indexes on its own schedule)"),
              file=sys.stderr)
        if cited and not args.quiet:
            for p in cited[:10]:
                print(f"    [{p['citations']:>5} cites] "
                      f"{(p.get('title_display') or p['title'] or '')[:60]}",
                      file=sys.stderr)
    # Reported on both paths. On this one it is a cross-check of the Scholar leg rather
    # than a substitute for it: a paper both sources agree the corpus lacks is not a
    # Scholar indexing quirk.
    report_gaps(gaps, stubs, args.quiet)


if __name__ == "__main__":
    main()
