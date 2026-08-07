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
                      patching the output would be undone on the next run.
    present           Matched a corpus record. The expected case.

And one in the other direction: corpus records with no Scholar row. Usually benign
-- Scholar indexes on its own schedule and a week-old preprint may not be there yet
-- but a *cited* paper of yours missing from your profile is a retrieval loss, since
Scholar is where most humans look you up.

Read-only, two requests, no login. Google serves this profile to a browser
User-Agent; if it ever answers with a challenge instead, the check says so and exits
0. It is an audit, not a gate: no run should stop because Google felt crawled.

Writes build/scholar_diff.json.

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
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import BUILD, DATA, load_config, norm_title, read_yaml  # noqa: E402

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
# A Scholar row that is not a paper. Reported separately rather than as a missing
# paper, because "add it to the bibliography" is the wrong advice for a patent.
NOT_A_PAPER = re.compile(r"\b(patent|thesis|dissertation|US\d{7,})\b", re.I)


def text(s: str) -> str:
    """Inner text of a Scholar cell. The titles carry markup, not just entities.

    Coined names are wrapped in a `gs_fscp` span -- "Elements of World Knowledge
    (<span>EWoK</span>): ..." -- so stripping entities alone leaves the tags in the
    title and every such row reads as a mismatch.
    """
    return " ".join(html.unescape(TAG.sub("", s)).split())


def fetch(uid: str, start: int) -> str:
    req = urllib.request.Request(PROFILE.format(uid=uid, start=start), headers=BROWSER)
    try:
        return urllib.request.urlopen(req, timeout=40).read().decode("utf8", "replace")
    except Exception as e:                                          # noqa: BLE001
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

    rows = scholar_rows(uid)
    if not rows:
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
            r["kind"] = ("not a paper" if NOT_A_PAPER.search(r["venue"] + r["title"])
                         else "paper")
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
    paired = {v["scholar"] for v in variants} | {d["scholar"] for d in dupes}
    missing = [r for r in missing if r["title"] not in paired]
    absent = [{"slug": p.get("slug"), "title": p.get("title"), "year": p.get("year"),
               "citations": p.get("citations")}
              for p in absent if p["slug"] not in taken]

    os.makedirs(BUILD, exist_ok=True)
    out = {"scholar_profile": uid, "scholar_rows": len(rows), "corpus": len(papers),
           "matched": len(seen),
           "gate_dropped": sorted(in_gate, key=lambda r: -r["citations"]),
           "title_variants": sorted(variants, key=lambda v: -v["score"]),
           "scholar_duplicates": sorted(dupes, key=lambda v: -v["score"]),
           "not_in_corpus": sorted(missing, key=lambda r: -r["citations"]),
           "not_on_scholar": sorted(absent, key=lambda p: -(p.get("citations") or 0))}
    with open(os.path.join(BUILD, "scholar_diff.json"), "w") as f:
        json.dump(out, f, indent=1)

    print(f"scholar: {len(rows)} rows, {len(seen)}/{len(papers)} corpus papers "
          f"matched", file=sys.stderr)
    if variants:
        print(f"  {len(variants)} paper(s) under two titles -- decide which is "
              f"canonical, then set it in data/overrides.yaml:", file=sys.stderr)
        if not args.quiet:
            for v in variants:
                print(f"    scholar: {v['scholar'][:64]}", file=sys.stderr)
                print(f"    corpus : {v['corpus'][:64]}   ({v['why']})",
                      file=sys.stderr)
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
    real = [r for r in missing if r["kind"] == "paper"]
    if real:
        print(f"  {len(real)} Scholar paper(s) absent from the bibliography "
              f"(add them to the source .bib, not to data/):", file=sys.stderr)
        if not args.quiet:
            for r in real[:20]:
                print(f"    [{r['citations']:>5} cites] {r['year'] or '????'} "
                      f"{r['title'][:60]}", file=sys.stderr)
            if len(real) > 20:
                print(f"    ... and {len(real) - 20} more in "
                      f"build/scholar_diff.json", file=sys.stderr)
    other = [r for r in missing if r["kind"] != "paper"]
    if other:
        print(f"  {len(other)} Scholar row(s) that are not papers (patent, thesis) "
              f"-- ignored on purpose", file=sys.stderr)
    if absent:
        cited = [p for p in absent if (p.get("citations") or 0) > 0]
        print(f"  {len(absent)} corpus paper(s) with no Scholar row"
              + (f", {len(cited)} of them cited -- worth adding to your profile"
                 if cited else " (Scholar indexes on its own schedule)"),
              file=sys.stderr)
        if cited and not args.quiet:
            for p in cited[:10]:
                print(f"    [{p['citations']:>5} cites] {(p['title'] or '')[:60]}",
                      file=sys.stderr)


if __name__ == "__main__":
    main()
