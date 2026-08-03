#!/usr/bin/env python3
"""paper-geo: one command, re-runnable, safe to schedule.

    python update.py                 # refresh everything read-only, report what needs you
    python update.py --refresh-bib   # also re-run the publications pipeline first
    python update.py --apply         # additionally write the approved repo changes
    python update.py --step collect  # run a single step

Design rules, because this is meant to be re-run for years:

  * Read-only by default. Nothing leaves this machine unless you pass --apply.
  * Idempotent. Every step is safe to run twice; steps that would clobber a human
    decision read data/overrides.yaml (papers) or the `reviewed` flag (repos).
  * Degrading, not failing. A source outage costs one field, not the run.
  * New work surfaces itself. New papers and new repos appear in the report with
    what they still need, so a rerun months from now tells you what changed.

Mirrors the convention of borgr/publications/update.py: one master script that
runs the steps in order and then tells you what a human still has to do.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from common import DATA, load_config, read_yaml  # noqa: E402

STEPS = ("collect", "repos", "propose", "validate", "worklist")


def run(argv: list[str], cwd: str | None = None) -> int:
    print(f"\n$ {' '.join(argv)}", flush=True)
    return subprocess.call(argv, cwd=cwd or ROOT)


def step_collect(cfg, args) -> None:
    """Rebuild data/papers.yaml from bibliography + S2 + arXiv + HF."""
    if args.refresh_bib:
        path = cfg["sources"].get("publications_path")
        if path and os.path.isdir(path):
            # publications owns the bibliography; let it refresh itself first so
            # newly-published venues land in enhanced.bib before we read it.
            run([sys.executable, "update.py"], cwd=path)
        else:
            print("  (sources.publications_path not set -- reading bib over HTTP)")
    run([sys.executable, "scripts/collect.py"])


def step_repos(cfg, args) -> None:
    """Refresh GitHub repo state, preserving prior edits."""
    run([sys.executable, "scripts/sweep_github.py", "propose"])


def step_propose(cfg, args) -> None:
    """Ask a model to label repos that still lack topics or a description."""
    run([sys.executable, "scripts/propose_topics.py"])


def step_validate(cfg, args) -> None:
    """Fail loudly on a malformed hand edit or a bad model proposal."""
    run([sys.executable, "scripts/validate.py"])


def step_worklist(cfg, args) -> None:
    """Report what only a human can do, ranked by citations."""
    papers = (read_yaml(os.path.join(DATA, "papers.yaml")) or {}).get("papers", [])
    repos = (read_yaml(os.path.join(DATA, "repos.yaml")) or {}).get("repos", [])
    ident, ids = cfg["identity"], cfg["ids"]

    def top(pred, n=8):
        return sorted([p for p in papers if pred(p)],
                      key=lambda p: -(p.get("citations") or 0))[:n]

    lines = ["# What still needs a human", "",
             "Regenerate with `python update.py`. Ordered by leverage.", ""]

    lines.append("## Once-only identity fixes")
    if len(ids["semantic_scholar"]) > 1:
        lines.append(f"- [ ] **Merge the {len(ids['semantic_scholar'])} Semantic Scholar author "
                     f"records** into {ids['semantic_scholar_primary']}. Claim the primary, then "
                     "email support to merge the others; do not claim two pages. Splits "
                     "author-level retrieval across every S2-backed tool.")
    if not ids.get("wikidata"):
        lines.append("- [ ] **Create a Wikidata item** (no notability bar) and put the QID in "
                     "`config.yaml` -> `ids.wikidata`. Feeds Google's Knowledge Graph and gives "
                     "every JSON-LD `sameAs` a real target.")
    lines.append(f"- [ ] **Populate ORCID {ident['orcid']}** via the Crossref + DataCite "
                 "Search & Link wizards and enable standing auto-update.")
    if ids.get("openalex_duplicates"):
        lines.append(f"- [ ] **Merge {len(ids['openalex_duplicates'])} duplicate OpenAlex author "
                     "records** into " + ids["openalex"][0] + ".")
    lines.append("")

    missing_jr = top(lambda p: p.get("arxiv") and not p.get("arxiv_journal_ref"), 12)
    if missing_jr:
        lines += [f"## arXiv journal-ref missing ({sum(1 for p in papers if p.get('arxiv') and not p.get('arxiv_journal_ref'))} papers)",
                  "",
                  "Scholar matches citations and merges preprint/published versions on exactly "
                  "these fields. No write API -- one web form each, so do them by citation count.",
                  ""]
        for p in missing_jr:
            venue = (p.get("venue") or "?")[:52]
            lines.append(f"- [ ] `{p['arxiv']}` ({p.get('citations') or 0} cites) -> {venue}  "
                         f"<https://arxiv.org/abs/{p['arxiv']}>")
        lines.append("")

    no_hf = top(lambda p: p.get("arxiv") and p.get("hf_indexed") is False, 10)
    if no_hf:
        lines += [f"## Hugging Face paper page missing ({sum(1 for p in papers if p.get('hf_indexed') is False and p.get('arxiv'))})",
                  "", "Visit the URL once to index it, then claim authorship.", ""]
        for p in no_hf:
            lines.append(f"- [ ] <https://hf.co/papers/{p['arxiv']}>  ({p.get('citations') or 0} cites)")
        lines.append("")

    unclaimed = top(lambda p: p.get("hf_indexed") and not p.get("hf_claimed_by_me"), 10)
    if unclaimed:
        lines += [f"## Hugging Face page indexed but not claimed by you ({sum(1 for p in papers if p.get('hf_indexed') and not p.get('hf_claimed_by_me'))})", ""]
        for p in unclaimed:
            lines.append(f"- [ ] <https://hf.co/papers/{p['arxiv']}>  ({p.get('citations') or 0} cites)")
        lines.append("")

    review = [p for p in papers if p.get("similar_but_distinct")]
    if review:
        lines += ["## Same paper or different? (decide once in data/overrides.yaml)", ""]
        for p in review:
            for o in p["similar_but_distinct"]:
                lines.append(f"- [ ] `{p['title'][:64]}`  vs  `{o[:64]}`")
        lines.append("")

    no_side = [p for p in papers if not p.get("has_sidecar")]
    if no_side:
        lines += [f"## Sidecars not written ({len(no_side)}/{len(papers)})", "",
                  "The one input no tool can supply: claims, scope conditions, terminology, "
                  "common misreadings. ~10 min each; do them by citation count.", ""]
        for p in sorted(no_side, key=lambda p: -(p.get("citations") or 0))[:10]:
            lines.append(f"- [ ] `data/sidecars/{p['slug']}.md`  ({p.get('citations') or 0} cites) "
                         f"{p['title'][:56]}")
        lines.append("")

    pend = [r for r in repos if not r.get("reviewed") and not r.get("skip")]
    if pend:
        lines += [f"## Repo labels awaiting your review ({len(pend)}/{len(repos)})", "",
                  "Check `data/repos.yaml`, fix anything wrong, set `reviewed: true` to freeze "
                  "it, then `python scripts/sweep_github.py diff`.", ""]

    out = os.path.join(ROOT, "WORKLIST.md")
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nwrote {out}")
    print("\n".join(l for l in lines if l.startswith("## ")))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", choices=STEPS, help="run one step instead of all")
    ap.add_argument("--refresh-bib", action="store_true",
                    help="run the publications pipeline first (needs sources.publications_path)")
    ap.add_argument("--apply", action="store_true",
                    help="also push approved repo changes to GitHub")
    args = ap.parse_args()
    cfg = load_config()

    fns = {"collect": step_collect, "repos": step_repos, "propose": step_propose,
           "validate": step_validate, "worklist": step_worklist}
    for name in ([args.step] if args.step else STEPS):
        print(f"\n{'=' * 62}\n== {name}\n{'=' * 62}")
        fns[name](cfg, args)

    if args.apply:
        print(f"\n{'=' * 62}\n== apply (writes to GitHub)\n{'=' * 62}")
        run([sys.executable, "scripts/sweep_github.py", "apply", "--yes"])
    else:
        print("\nRead-only run. Review data/repos.yaml and WORKLIST.md, then:")
        print("  python scripts/sweep_github.py diff      # see exactly what would change")
        print("  python update.py --apply                 # write it")


if __name__ == "__main__":
    main()
