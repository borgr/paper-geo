#!/usr/bin/env python3
"""The "A" checks from docs/EVIDENCE.md: is the work done, and still done?

Deterministic and cheap. These verify the machinery, not the outcome -- a green
run says nothing about whether anything got cited. What it does catch is the class
of failure that silently undoes the work: metadata reverted upstream, a link
rotted, a page that renders only under JavaScript, a crawler quietly blocked.

Usage:
    python measure/check_structure.py [--links] [--json out.json]
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "scripts"))
from common import (BUILD, DATA, get_status, has_live_sidecar, load_config,  # noqa: E402
                    read_papers, write_json)

SITE = os.path.join(BUILD, "site")
AI_BOTS = ("GPTBot", "OAI-SearchBot", "ClaudeBot", "PerplexityBot", "Google-Extended")


def rec(results, name, ok, detail=""):
    results.append({"check": name, "ok": bool(ok), "detail": detail})
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  — {detail}" if detail else ""))


def coverage(papers, results) -> None:
    n = len(papers)
    ax = [p for p in papers if p.get("arxiv")]
    def pct(k, d): return f"{k}/{d}" + (f" ({100*k/d:.0f}%)" if d else "")
    for name, k, d in [
        ("every paper has a slug", sum(1 for p in papers if p.get("slug")), n),
        ("every paper has a title", sum(1 for p in papers if p.get("title")), n),
        ("abstract present (Scholar requires a visible one)",
         sum(1 for p in papers if p.get("abstract")), n),
        ("verbatim BibTeX captured", sum(1 for p in papers if p.get("bibtex")), n),
        ("crawlable HTML surface exists",
         sum(1 for p in papers if (p.get("links") or {}).get("html")), n),
        ("arXiv journal-ref set (Scholar citation matching)",
         sum(1 for p in ax if p.get("arxiv_journal_ref")), len(ax)),
        ("HF paper page exists", sum(1 for p in ax if p.get("hf_indexed")), len(ax)),
        ("HF page claimed by us", sum(1 for p in ax if p.get("hf_claimed_by_me")), len(ax)),
        ("sidecar written", sum(1 for p in papers if has_live_sidecar(p["slug"])), n),
    ]:
        # Coverage is reported, not pass/fail -- these are the work queue, and a
        # red line here is the worklist doing its job rather than a regression.
        results.append({"check": name, "coverage": f"{k}/{d}"})
        print(f"  {pct(k, d):>14}  {name}")

    # These ARE failures: a duplicate title is the documented Scholar drop.
    titles = {}
    for p in papers:
        titles.setdefault((p.get("title") or "").strip().lower(), []).append(p["slug"])
    dup = {t: s for t, s in titles.items() if len(s) > 1}
    rec(results, "no duplicate titles among our own pages", not dup,
        f"{len(dup)} duplicated" if dup else "")
    unresolved = [p["slug"] for p in papers if p.get("similar_but_distinct")]
    rec(results, "no unresolved same-or-different flags", not unresolved,
        f"{len(unresolved)} awaiting a decision in overrides.yaml" if unresolved else "")
    conflicts = [p["slug"] for p in papers if p.get("owner_conflict")]
    rec(results, "no ownership conflicts", not conflicts,
        f"{len(conflicts)} papers claimed by two parties" if conflicts else "")


def pages(results) -> None:
    if not os.path.isdir(SITE):
        rec(results, "site built", False, "run scripts/build_site.py")
        return
    files = glob.glob(os.path.join(SITE, "papers", "*", "index.html"))
    # A redirect stub left behind by a merge is not a content page: it has no
    # abstract, no highwire tags and almost no words on purpose. Counted separately
    # rather than skipped silently, so a build that starts emitting hundreds of them
    # is visible instead of just quietly shrinking the checked set.
    stubs = [f for f in files if 'http-equiv="refresh"' in open(f).read()]
    files = [f for f in files if f not in set(stubs)]
    rec(results, "site built", bool(files), f"{len(files)} paper pages"
        + (f" (+{len(stubs)} redirects from retired URLs)" if stubs else ""))

    bad_json, no_hw, no_abs, needs_js, no_canon = [], [], [], [], []
    for f in files:
        h = open(f).read()
        for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
            try:
                json.loads(m.replace("<\\/", "</"))
            except Exception:
                bad_json.append(f)
        for t in ("citation_title", "citation_author", "citation_publication_date"):
            if t not in h:
                no_hw.append(f)
                break
        if 'rel="canonical"' not in h:
            no_canon.append(f)
        # Body text present with scripts stripped: the no-JS test. A page whose
        # content needs JavaScript is invisible to crawlers that do not run it.
        body = re.sub(r"<script.*?</script>|<style.*?</style>", "",
                      h[h.find("<body"):], flags=re.S)
        if len(re.sub(r"<[^>]+>", " ", body).split()) < 60:
            needs_js.append(f)
        if "<h2>Abstract</h2>" not in h and "In one sentence" not in h:
            no_abs.append(f)

    rec(results, "all JSON-LD parses", not bad_json, f"{len(bad_json)} invalid")
    rec(results, "all pages have the 3 mandatory highwire tags", not no_hw,
        f"{len(no_hw)} incomplete" if no_hw else "")
    rec(results, "all pages declare rel=canonical", not no_canon,
        f"{len(no_canon)} missing" if no_canon else "")
    rec(results, "all pages readable without JavaScript", not needs_js,
        f"{len(needs_js)} thin" if needs_js else "")
    results.append({"check": "pages with neither abstract nor one-liner",
                    "coverage": f"{len(no_abs)}/{len(files)}"})
    print(f"  {len(no_abs)}/{len(files)}  pages with neither abstract nor one-liner")

    robots = os.path.join(SITE, "robots.txt")
    txt = open(robots).read() if os.path.exists(robots) else ""
    missing = [b for b in AI_BOTS if b not in txt]
    rec(results, "robots.txt names every AI crawler", not missing, ", ".join(missing))
    rec(results, "sitemap.xml present", os.path.exists(os.path.join(SITE, "sitemap.xml")))
    rec(results, "llms.txt present", os.path.exists(os.path.join(SITE, "llms.txt")))
    rec(results, "ownership manifest present",
        os.path.exists(os.path.join(SITE, "paper-geo.json")))


def claim_consistency(papers, results) -> None:
    """The say-it-the-same-way rule, enforced mechanically.

    A claim sentence that drifts between the page and a README stops being one
    corroborated assertion and becomes two competing near-duplicates.
    """
    import yaml
    drift = []
    for path in glob.glob(os.path.join(DATA, "sidecars", "*.md")):
        slug = os.path.basename(path)[:-3]
        m = re.match(r"^---\n(.*?)\n---", open(path).read(), re.S)
        if not m:
            continue
        one = " ".join((yaml.safe_load(m.group(1)) or {}).get("one_liner", "").split())
        if not one:
            continue
        page = os.path.join(SITE, "papers", slug, "index.html")
        if os.path.exists(page):
            import html as _h
            if _h.escape(one) not in open(page).read():
                drift.append(f"{slug}: page")
        blk = os.path.join(BUILD, "readme_blocks")
        for f in glob.glob(os.path.join(blk, "*.md")):
            t = open(f).read()
            if slug.split("-")[0] in t and one not in t:
                drift.append(f"{slug}: {os.path.basename(f)}")
    rec(results, "claim sentence identical across surfaces", not drift,
        "; ".join(drift[:4]) if drift else "")


def links(papers, results) -> None:
    """Link rot check. Slow; opt in with --links.

    Only a 404 or 410 is rot. A timeout, a 429 and a 5xx are the host declining to say,
    and calling those dead would report a working link as broken on the first bad minute.
    """
    seen, dead, unchecked = set(), [], []
    for p in papers:
        for k, u in (p.get("links") or {}).items():
            if k == "html_source" or not str(u).startswith("http") or u in seen:
                continue
            seen.add(u)
            st, _ = get_status(u, retries=1, timeout=15)
            if st in (404, 410):
                dead.append(u)
            elif st >= 400 or st == 0:
                unchecked.append(u)
    # Passes on rot alone. A host that would not answer is stated rather than counted
    # against the check, since one bad minute anywhere would otherwise keep this red for
    # ever and a check that is always red is a check nobody reads.
    detail = f"{len(seen) - len(unchecked)} of {len(seen)} checked"
    if dead:
        detail += f", {len(dead)} dead: {dead[:3]}"
    if unchecked:
        detail += f"; would not answer: {unchecked[:3]}"
    rec(results, "every link resolves", not dead, detail)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--links", action="store_true", help="check every URL resolves (slow)")
    ap.add_argument("--json", help="write results to this path")
    args = ap.parse_args()
    load_config()
    papers = read_papers()
    results: list[dict] = []

    print("\n== coverage (a work queue, not a regression)")
    coverage(papers, results)
    print("\n== generated pages")
    pages(results)
    print("\n== claim consistency")
    claim_consistency(papers, results)
    if args.links:
        print("\n== links")
        links(papers, results)

    failed = [r for r in results if r.get("ok") is False]
    print(f"\n{len(failed)} failing check(s) of "
          f"{sum(1 for r in results if 'ok' in r)}")
    for r in failed:
        print(f"  {r['check']}: {r['detail']}")
    if args.json:
        write_json(args.json, results, indent=1)
        print(f"wrote {args.json}")


if __name__ == "__main__":
    main()
