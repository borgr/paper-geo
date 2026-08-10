#!/usr/bin/env python3
"""Diff your Google Scholar profile against the corpus, to catch silent drops.

Every other check in this repo validates the corpus against itself: the schema says
the fields are well-formed, `validate.py` says the ids resolve, the authorship gate
says each record carries your name. None of them can see a paper that never arrived.
The pipeline's input is one bibliography file, so a paper missing from that file is
invisible everywhere downstream -- and so is a paper the authorship gate dropped,
because after the gate it does not exist.

Scholar is the one list that is maintained by a different process (Google's crawler
plus your own profile edits) and is therefore capable of disagreeing. That makes it
worth exactly one thing: an independent count of what should be there. It is a poor
source of *metadata* -- truncated author lists, venue strings that are sometimes the
arXiv id -- so nothing here is copied into `data/`. Titles in, diff out.

Three outcomes per Scholar row, in descending order of how much they should worry
you:

    gate dropped it   Scholar attributes the paper to you and `build/not_mine.json`
                      says the gate excluded it. Either the gate is wrong (fix it, or
                      add the title under `also_mine` in overrides.yaml) or Scholar
                      is (a namesake's paper merged into your profile -- delete it
                      there, since a wrong Scholar row also misleads every human).
    not in the bib    The paper reached neither -- it is absent from the source
                      bibliography. Add it there; the bibliography is the input, and
                      patching the output would be undone on the next run. The check
                      does the citation lookup for you: `tasks/bib_missing.md` gets a
                      BibTeX entry per paper, resolved from your Semantic Scholar
                      author record, arXiv or Crossref, so the human act is reading
                      one entry and pasting it rather than finding it.
    present           Matched a corpus record. The expected case.

And one in the other direction: corpus records with no Scholar row. Usually benign
-- Scholar indexes on its own schedule and a week-old preprint may not be there yet
-- but a *cited* paper of yours missing from your profile is a retrieval loss, since
Scholar is where most humans look you up.

Read-only and no login anywhere. Two requests to Scholar, two to your Semantic
Scholar author record, and -- only when a paper turns out to be missing -- up to three
lookups for that one paper. Google serves this profile to a browser User-Agent; if it
ever answers with a challenge instead, the check says so and exits 0. It is an audit,
not a gate: no run should stop because Google felt crawled, or because an index was
busy.

When Google does refuse -- which is every unattended run, because a datacenter IP gets
a challenge page -- the author-record half still runs and asks a narrower version of
the same question: papers an index attributes to you that the corpus has never received
(`attributed_gaps`). It finds strictly less than Scholar does, by a margin measured in
that function's docstring, so it does not replace running this from a desk. What it
changes is that an unattended run stops being silent, and silence and "nothing is
wrong" are not the same claim.

Set `S2_API_KEY` in the environment if you have one. Semantic Scholar's anonymous
pool is shared with the world and refuses often; the key is what makes the difference
between resolving a missing paper and reporting that nobody indexes it.

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
from common import (ARXIV_NS, BUILD, DATA, ROOT, TASKS, get,  # noqa: E402
                    get_json, load_config, norm_title, note_fetch, read_yaml,
                    synth_bibtex)


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

    This does not go through `common.get`, because Scholar needs the browser header
    and no backoff, so it was also the one HTTP source outside the ledger. It is the
    worst one to leave out: Scholar is the only list of these papers built by a
    process this pipeline does not control, so it is the only check that can see a
    paper the pipeline never received -- and when it stops working the symptom is a
    whole section quietly missing from the worklist, which reads as "nothing to
    report". A line on stderr during a ten-step run is not a signal anybody sees.
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


def scholar_rows(uid: str) -> list[dict]:
    """Every row of the citations table, paging until a page comes back short."""
    out, start = [], 0
    while True:
        page = fetch(uid, start)
        if not page:
            break
        rows = ROW.findall(page)
        if not rows and start == 0:
            # Rows absent from a page that did load: a challenge, a renamed class, or
            # a profile that went private. All three mean "no data", and none of them
            # means "you have no papers", so the count is never reported as zero.
            # Also recorded as a failed fetch even though the HTTP call succeeded: a
            # 200 carrying no data is the failure this source will actually have, and
            # a ledger that only counts transport errors would call it healthy for
            # months while the coverage check silently checked nothing.
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
            break
        start += PAGE
        time.sleep(2)
    return out


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

    Retitles between a preprint and its published version are common enough that
    without this the same paper is reported twice -- once as "Scholar has a paper you
    do not" and once as "you have a paper Scholar does not" -- and the two lines are
    nowhere near each other. Reported as a question, not a fact, so a loose threshold
    is the right side to err on: a wrong pair costs one line a human dismisses, and a
    missed pair costs a duplicated public page.

    Two signals, either sufficient. Word overlap catches a reworded subtitle; an
    identical coined name before the colon catches a fully rewritten one, which
    overlap cannot -- "LLM Hypnosis: Exploiting User Feedback ..." and "LLM Hypnosis:
    Characterizing the Fragility of RLHF ..." share four words out of fifteen.
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
    """Are these two title strings the same title, allowing for house style."""
    if norm_title(a) == norm_title(b):
        return True
    sc = variant_score(a, b)
    return bool(sc and sc[0] >= 0.5)


def arxiv_titles() -> dict[str, str]:
    """slug -> the title arXiv states, for the papers where it differs from ours.

    `collect.py` compares every paper that carries an arXiv id and writes only the
    disagreements to `build/title_diffs.json`, so absence from that file is itself an
    answer rather than a gap: arXiv and the bibliography agree on that paper's title.
    """
    try:
        with open(os.path.join(BUILD, "title_diffs.json")) as f:
            return {d["slug"]: d["arxiv_says"] for d in json.load(f)
                    if d.get("slug") and d.get("arxiv_says")}
    except (OSError, ValueError, AttributeError, TypeError):
        return {}


def stale_side(scholar: str, p: dict, diffs: dict[str, str]) -> tuple[str, str]:
    """Which of the two titles is out of date, on arXiv's evidence.

    One paper under two titles reads like a judgement call, and mostly is not one:
    arXiv holds the current title and a run has already fetched it. Three outcomes, of
    which only the last is a decision.

        bib      arXiv states the Scholar title, so the bibliography entry is behind.
                 This is the same finding `collect.py` reports as `title differs from
                 arXiv`, arrived at from the other side, and the fix is one edit
                 upstream rather than an override here.
        scholar  arXiv states our title, so the Scholar row kept an earlier one.
                 Nothing to fix: editing the row on your profile changes what it
                 displays, not which citations Scholar clusters under it.
        open     no arXiv record, or arXiv agrees with neither. Yours to decide.
    """
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

    The near-miss gate, and it has to be stricter than `variant_score`. That one pairs
    two titles already known to be yours -- a corpus paper against a Scholar row -- so
    a loose word-overlap threshold costs at worst a line you dismiss. An index answers
    from the whole literature, and there 4 of 9 shared words is *Framework-based
    Roguelike Game for AI/ML Education* against *A Statistical Framework for Game-Based
    AI Evaluation*: a stranger's paper, offered to you as "the same paper renamed?".

    A run separates them on the real cases. The genuine rename in this corpus keeps
    five words in order ("... Building LLMs Efficiently through Merging"); the
    Roguelike paper shares no two adjacent words with anything of yours.
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

    The author endpoint, not the search endpoint. Search costs one request per title
    and answers 429 to an unauthenticated caller often enough to be useless -- three
    titles in a row, through the shared backoff, on the run that prompted this. The
    author endpoint is two requests for the whole check, it is the one `collect.py`
    already depends on every run, and it answers a better question: a paper on your
    author record is one S2 attributes to *you*, so a hit resolves "is it yours" at
    the same time as it resolves the metadata.
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

    Returns (gaps, unverifiable): the rows worth acting on, and the rows S2 holds with
    no external identifier, which are counted but not listed. See below for why that
    split and not some other one.

    The same question the Scholar leg's `not_in_corpus` answers, asked of an endpoint
    that answers from anywhere. It exists because the Scholar leg cannot run unattended
    at all -- Google serves a datacenter IP a challenge page rather than a profile, so
    the one check that can see a paper the pipeline never received was also the only
    check that ran solely when somebody remembered to run it from a desk.

    Measurably the weaker source, and worth being exact about how much weaker, because
    the temptation is to read a quiet CI run as an all-clear. On this corpus the Scholar
    leg finds three papers absent from the bibliography and this leg finds none of the
    three: S2's author record does not contain them at all (125 records, 117 with an
    identifier, and none of those three among them). So it is not a substitute, it is a
    floor -- what it catches is a *new* paper that reached an index and not the
    bibliography, which is the case where the delay costs something, and the case a
    monthly unattended run is actually for. A paper missing for three years is one the
    author already knows about.

    **An identifier is required, and that is the whole design.** A row is reported only
    if S2 gives it an arXiv id or a DOI. Measured on this author's record, that rule is
    what makes the check worth reading: the first live run reported six absent papers and
    every one of the six carried neither identifier. They are S2's citation-derived
    stubs -- one is a journal name in the title field, one is the v1 title of a corpus
    paper since renamed to something with no words in common, so no title-similarity
    rule could have paired them either. Six rows of judgement work and nothing to act on
    is how an unattended warning teaches its reader to skip it.

    Nothing is lost by the rule that matters. A paper new enough to have gone missing has
    an arXiv id, and a paper with no identifier anywhere cannot be added to a
    bibliography from this list regardless -- the reader would have to go find it, which
    is the local Scholar run's job. The suppressed rows are still counted on stderr and
    written to `build/scholar_diff.json`, so this is a ranking, not a deletion.
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


def from_s2(title: str, mine: list[dict]) -> tuple[dict | None, str]:
    """Match a title against the fetched author record. No request of its own."""
    near = ""
    for p in mine:
        got = p.get("title") or ""
        if not same_paper(got, title):
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
        if not same_paper(got, title):
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
    """The Crossref record for a title, the nearest title offered, and whether it
    replied.

    Neither of the first two resolvers can answer for a paper that was never
    preprinted and never landed on your author record, which is most of what goes
    missing: competition reports, workshop papers, proceedings-only papers. Crossref
    holds those, because the publisher registered the DOI -- and the DOI is the field
    that makes a BibTeX entry worth pasting, since it is what ORCID and every citation
    manager group on.

    Its ranking is fuzzy: an unmatched query returns five plausible strangers rather
    than nothing, which is why the `same_paper` filter decides and the query only
    proposes. Verified against three known ACL entries from the corpus -- all three
    came back with the exact registered DOI.
    """
    d = get_json(CROSSREF + urllib.parse.quote(searchable(title)), retries=2)
    if d is None:
        return None, "", False
    near = ""
    for it in ((d.get("message") or {}).get("items") or []):
        got = " ".join(((it.get("title") or [""])[0] or "").split())
        if not same_paper(got, title):
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


def from_s2_search(title: str) -> tuple[dict | None, str, bool]:
    """S2's title search, last and deliberately impatient.

    It is the only index that held the one genuinely resolvable paper here -- a
    competition report that is on nobody's arXiv and on no author record, indexed under
    a longer title than Scholar displays. So it is worth asking. But unauthenticated
    search answers 429 from a pool shared with the world, and it did so on every
    attempt of the run that added this, while the *author* endpoint above answered
    both times. Three tries at the shared backoff is ~12s per paper: enough to win when
    the pool is free, short enough that a rate-limited day costs the audit half a minute
    and says so rather than stalling it.
    """
    q = urllib.parse.quote(searchable(title))
    d = get_json(f"https://api.semanticscholar.org/graph/v1/paper/search?query={q}"
                 f"&limit=5&fields={S2_FIELDS}", retries=3)
    if d is None:
        return None, "", False
    rec, near = from_s2(title, d.get("data") or [])
    return rec, near, True


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
        down.append("your Semantic Scholar author record")
    for fn, name in ((from_arxiv, "arXiv"), (from_crossref, "Crossref"),
                     (from_s2_search, "Semantic Scholar search")):
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
evidence than it looks: arXiv and Crossref match on title alone and know nothing about
whose paper it is. **Is the entry right** — a resolved entry carries the index's author
list and venue, not yours; a stub carries only what Scholar displayed, which is a
truncated author list and a venue string that is sometimes an arXiv id.

Patents, theses, blog posts and proceedings volumes never reach this file -- the check
classifies those and reports them apart. An entry marked `UNRESOLVED` was looked for in
all three indexes and found in none, which for a proceedings-only paper usually means
nobody registered it anywhere machine-readable. Pasting that stub as it stands would
put a `TODO` in your bibliography.

"""


def bib_payload(rows: list[dict], bib_url: str, mine: list[dict] | None
                ) -> tuple[str, int, int, int]:
    """Write `tasks/bib_missing.md`: (path, papers, resolved, worth retrying).

    Absent when there is nothing missing, on the same principle as the worklist's
    sections -- a file that says "none" is one more thing to read and disbelieve.

    A near miss is printed rather than pasted. The indexes routinely hold a paper under
    a title that is close but not the same -- a competition report renamed for the
    proceedings -- and that is exactly the case where an automatic match would write
    somebody else's paper into a bibliography under a citation key that looks checked.
    Naming the candidate leaves the judgement where it belongs and still saves the
    search.
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
            asked = [n for n in ("your Semantic Scholar author record", "arXiv",
                                 "Crossref", "Semantic Scholar search")
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
    os.makedirs(TASKS, exist_ok=True)
    with open(path, "w") as f:
        f.write("\n".join(out).rstrip() + "\n")
    return path, len(rows), done, retry


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

    rows = scholar_rows(uid)
    if not rows:
        # Google refused, which is the normal case from a datacenter IP and says nothing
        # about the corpus. Write what the author record could answer rather than
        # nothing: a file absent and a file reporting no gaps are indistinguishable to
        # every reader downstream, and only one of them is true.
        os.makedirs(BUILD, exist_ok=True)
        with open(os.path.join(BUILD, "scholar_diff.json"), "w") as f:
            json.dump({"scholar_profile": uid, "scholar_rows": 0,
                       "scholar_answered": False, "corpus": len(papers),
                       "s2_answered": attributed is not None,
                       "not_in_corpus_by_index": gaps,
                       "index_stubs_no_id": stubs}, f, indent=1)
        print(f"scholar: profile unavailable; author record answered for "
              f"{len(attributed or [])} paper(s)", file=sys.stderr)
        report_gaps(gaps, stubs, args.quiet)
        return

    missing, in_gate = [], []
    # Keyed on the *corpus* title, never the Scholar one. A prefix match means the two
    # strings differ, so recording the Scholar side here left the corpus paper looking
    # unmatched and every retitle was reported twice, in two different sections.
    seen: set[str] = set()
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

    absent = [p for p in papers if norm_title(p.get("title")) not in seen]
    # Pair every leftover Scholar row against the corpus before reporting it as a gap,
    # and against the whole corpus rather than only the unmatched part -- because which
    # side the pair lands on decides who has the work. A pair with an unmatched paper
    # is one paper under two titles and the question is which is current. A pair with a
    # paper that already matched some other row means Scholar itself lists it twice,
    # which nothing in this repo can fix.
    variants, dupes, taken = [], [], set()
    unmatched = {p["slug"]: p for p in absent}
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
    absent = [{"slug": p.get("slug"), "title": p.get("title"), "year": p.get("year"),
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
           "not_on_scholar": sorted(absent, key=lambda p: -(p.get("citations") or 0))}
    with open(os.path.join(BUILD, "scholar_diff.json"), "w") as f:
        json.dump(out, f, indent=1)

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
    real = sorted((r for r in missing if r["kind"] == "paper"),
                  key=lambda r: -(r.get("citations") or 0))
    path, _, done, retry = bib_payload(
        real, (cfg.get("sources") or {}).get("bibtex_url") or "", attributed or [])
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
        print(f"  {len(absent)} corpus paper(s) with no Scholar row"
              + (f", {len(cited)} of them cited -- worth adding to your profile"
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
