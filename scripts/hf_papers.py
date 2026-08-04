#!/usr/bin/env python3
"""Index missing Hugging Face paper pages and report unclaimed ones.

HF Papers is the successor to Papers with Code and the main paper<->artifact join
surface in ML: a model or dataset whose README links the arXiv URL is auto-tagged
and cross-listed on the paper page. A paper with no page there has no such join.

Indexing CANNOT be automated. HF's docs say visiting hf.co/papers/<arxiv-id>
indexes the paper, but that is only true for a logged-in browser session: an
unauthenticated GET returns 404 and creates nothing (verified on 50 papers -- 0
created). Claiming authorship is likewise a per-page clickthrough.

So this script does the part that IS automatable: it produces an ordered, clickable
worklist you run through once while logged in, and afterwards re-checks which pages
now exist. Two links per paper, ordered by citation count, so the highest-value
pages are created first and you can stop whenever.

Usage:
    python scripts/hf_papers.py            # report + write the clickable worklist
    python scripts/hf_papers.py --verify   # re-check which pages now exist
"""
from __future__ import annotations

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import BUILD, DATA, get_json, load_config, read_yaml  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true",
                    help="re-check which pages now exist, after working the list")
    args = ap.parse_args()
    cfg = load_config()
    me = cfg["ids"]["huggingface"]
    papers = (read_yaml(os.path.join(DATA, "papers.yaml")) or {})["papers"]
    have_arxiv = [p for p in papers if p.get("arxiv")]
    by_cites = sorted(have_arxiv, key=lambda p: -(p.get("citations") or 0))

    missing = [p for p in by_cites if p.get("hf_indexed") is False]
    unclaimed = [p for p in by_cites
                 if p.get("hf_indexed") and not p.get("hf_claimed_by_me")]

    print(f"arXiv papers: {len(have_arxiv)}   no HF page: {len(missing)}   "
          f"page exists but not claimed by {me}: {len(unclaimed)}")

    if args.verify:
        print("\nre-checking ...")
        now = 0
        for p in missing:
            ok = get_json(f"https://huggingface.co/api/papers/{p['arxiv']}",
                          retries=1) is not None
            now += ok
            if ok:
                print(f"  now indexed: {p['arxiv']}  {p['title'][:50]}")
            time.sleep(0.3)
        print(f"\n{now} of {len(missing)} previously-missing pages now exist.")
        print("Run `python scripts/collect.py` to record the new state.")
        return

    if missing:
        print("\nMissing pages, highest citations first:")
        for p in missing[:12]:
            print(f"  https://hf.co/papers/{p['arxiv']}   "
                  f"{p.get('citations') or 0:>4} cites  {p['title'][:44]}")
        if len(missing) > 12:
            print(f"  ... and {len(missing) - 12} more")
    if unclaimed:
        print(f"\nIndexed but not claimed by {me}, highest citations first:")
        for p in unclaimed[:12]:
            print(f"  https://hf.co/papers/{p['arxiv']}   "
                  f"{p.get('citations') or 0:>4} cites  {p['title'][:44]}")
        if len(unclaimed) > 12:
            print(f"  ... and {len(unclaimed) - 12} more")

    # A clickable list is the actual deliverable: the work is manual, so make the
    # manual pass as short as possible rather than pretending to automate it.
    os.makedirs(BUILD, exist_ok=True)
    out = os.path.join(BUILD, "hf_worklist.html")
    rows = []
    for label, group in (("Index (visit while logged in)", missing),
                         ("Claim authorship", unclaimed)):
        rows.append(f"<h2>{label} — {len(group)}</h2><ol>")
        for p in group:
            rows.append(
                f'<li><a href="https://huggingface.co/papers/{p["arxiv"]}" '
                f'target="_blank" rel="noreferrer">{p["arxiv"]}</a> '
                f'<small>{p.get("citations") or 0} cites</small> — {p["title"]}</li>')
        rows.append("</ol>")
    with open(out, "w") as f:
        f.write("<!DOCTYPE html><meta charset=utf-8><title>HF paper worklist</title>"
                "<style>body{font:15px/1.5 system-ui;max-width:52rem;margin:2rem auto;"
                "padding:0 1rem}li{margin:.3rem 0}small{color:#666}</style>"
                "<h1>Hugging Face paper worklist</h1><p>Log in to Hugging Face first, "
                "then middle-click down the list. Visiting a paper URL while logged in "
                "is what indexes it. Re-run <code>python scripts/hf_papers.py --verify"
                "</code> afterwards.</p>" + "\n".join(rows))
    print(f"\nwrote {out} — log in, then click through it.")


if __name__ == "__main__":
    main()
