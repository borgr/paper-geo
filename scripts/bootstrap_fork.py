#!/usr/bin/env python3
"""Reset a fork so it holds a new researcher's corpus and none of the old one's judgement.

`config.yaml` says a fork has to replace two things: itself, and `data/`. That is only
half a procedure, because `data/` is three kinds of file and they need three different
treatments -- and getting the third one wrong is the failure this script exists to
prevent:

    derived    papers.yaml, repos.yaml, fulltext/  -- rebuilt from public sources on the
               first run. Deleting them costs one slow run and nothing else.
    receipts   slug_history.yaml, wikidata_created.yaml, arxiv_submissions.yaml -- true
               statements about someone else's records. Kept, they would redirect your
               URLs to their retired slugs and skip creating items you do not have.
    judgement  paper_code.yaml, overrides.yaml, declines.yaml, followups.yaml,
               sidecars/ -- one researcher's decisions about their own work, several of
               them decisions to publish or not publish something. Inherited, they
               publish that person's judgement under your name, silently, because
               nothing downstream can tell an inherited decision from yours.

So every one of them is emptied, and the documentation comments at the head of each file
are kept: they are how a fork learns what the file means, and they are the one part that
is not about a particular person.

    python scripts/bootstrap_fork.py --check   # what still names the previous author
    python scripts/bootstrap_fork.py --yes     # empty the data, then --check

`--check` is the half worth running twice. It greps `config.yaml` for the values the
previous author's identity is made of and prints each line still carrying one, because a
fork that empties `data/` but keeps `orcid:` produces a site that asserts your papers are
theirs -- and no other check in the repo can catch it, since for the author those values
are correct.
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import DATA, ROOT, load_config  # noqa: E402

# key -> the empty value to leave behind. A key absent from a file is skipped, so this
# table is also the record of what each file is allowed to contain.
EMPTY = {
    "paper_code.yaml": {"papers": {}},
    "overrides.yaml": {"force_merge": [], "force_distinct": [], "also_mine": [],
                       "extra_arxiv": [], "extra_openreview": [], "drop": [],
                       "hf_claim_requested": [], "fields": {}},
    "declines.yaml": {"sections": [], "items": [], "deferred": []},
    "followups.yaml": {"followups": []},
    "slug_history.yaml": {"retired": {}},
    "wikidata_created.yaml": {"items": {}},
}
# No key survives: every top-level key is itself one of the previous author's arXiv ids.
WIPE = ["arxiv_submissions.yaml"]
DERIVED = ["papers.yaml", "repos.yaml"]
DERIVED_DIRS = ["fulltext"]
JUDGEMENT_DIRS = ["sidecars"]


def header(text: str) -> str:
    """The leading comment block, which documents the file rather than the author."""
    out = []
    for line in text.splitlines():
        if line.strip() and not line.lstrip().startswith("#"):
            break
        out.append(line)
    return "\n".join(out).rstrip() + "\n" if out else ""


def rewrite(path: str, empties: dict) -> str:
    """Empty a decision file, keeping its comments and its documentation strings."""
    import yaml
    text = open(path).read()
    doc = yaml.safe_load(text) or {}
    keep = {k: v for k, v in doc.items() if isinstance(v, str)}   # note:, _comment:
    keep.update({k: empties[k] for k in doc if k in empties})
    with open(path, "w") as f:
        f.write(header(text))
        f.write(yaml.safe_dump(keep, sort_keys=False, allow_unicode=True, width=100))
    return f"emptied {os.path.relpath(path, ROOT)}"


def check() -> list[str]:
    """Lines of `config.yaml` that still carry a value from the previous author."""
    cfg, ident = load_config(), None
    ident = cfg["identity"]
    needles = {ident["name"], ident.get("email") or "", ident.get("orcid") or "",
               ident["canonical_url"]}
    needles |= set(ident.get("name_variants") or []) | set(ident.get("name_typos") or [])
    needles |= set(ident.get("other_pages") or [])
    ids = cfg.get("ids") or {}
    needles |= {str(v) for v in ids.values() if isinstance(v, (str, int))}
    for v in ids.values():
        if isinstance(v, list):
            needles |= {str(x) for x in v}
    if ids.get("github"):
        needles.add(str(ids["github"]))
    needles = {n for n in needles if len(str(n)) > 3}
    hits = []
    for i, line in enumerate(open(os.path.join(ROOT, "config.yaml")), 1):
        if line.lstrip().startswith("#"):
            continue                      # a comment naming the author is documentation
        for n in sorted(needles, key=len, reverse=True):
            if n in line:
                hits.append(f"  config.yaml:{i}  {line.strip()[:88]}")
                break
    return hits


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--yes", action="store_true",
                    help="actually empty data/ (without this, only says what it would do)")
    ap.add_argument("--check", action="store_true",
                    help="only report config.yaml lines that still name the old author")
    args = ap.parse_args()

    if not args.check:
        acts = []
        for name, empties in EMPTY.items():
            p = os.path.join(DATA, name)
            if os.path.exists(p):
                acts.append(rewrite(p, empties) if args.yes
                            else f"would empty data/{name}")
        for name in WIPE:
            p = os.path.join(DATA, name)
            if os.path.exists(p):
                if args.yes:
                    open(p, "w").write(header(open(p).read()))
                acts.append(f"{'wiped' if args.yes else 'would wipe'} data/{name}")
        for name in DERIVED:
            p = os.path.join(DATA, name)
            if os.path.exists(p):
                if args.yes:
                    os.remove(p)
                acts.append(f"{'deleted' if args.yes else 'would delete'} data/{name} "
                            f"(rebuilt by the first run)")
        for name in DERIVED_DIRS + JUDGEMENT_DIRS:
            d = os.path.join(DATA, name)
            n = len(glob.glob(os.path.join(d, "*")))
            if n:
                if args.yes:
                    for p in glob.glob(os.path.join(d, "*")):
                        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
                acts.append(f"{'cleared' if args.yes else 'would clear'} data/{name}/ "
                            f"({n} file(s))")
        b = os.path.join(ROOT, "build")
        if os.path.isdir(b):
            if args.yes:
                shutil.rmtree(b)
            acts.append(f"{'deleted' if args.yes else 'would delete'} build/")
        print("\n".join(f"  {a}" for a in acts) or "  nothing to reset")
        if not args.yes:
            print("\nNothing changed. Re-run with --yes.")
            return

    hits = check()
    print("\nconfig.yaml still names the previous author:" if hits
          else "\nconfig.yaml carries no value from the previous author.")
    for h in hits:
        print(h)
    if hits:
        print("\nReplace every line above, then: python update.py")
    sys.exit(1 if hits and args.check else 0)


if __name__ == "__main__":
    main()
