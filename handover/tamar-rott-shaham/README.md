# paper-geo for Tamar Rott Shaham

A generated starter bundle. `config.yaml` here holds the blocks to paste into a fork of
[paper-geo](https://github.com/borgr/paper-geo); everything in it is either a public fact
or a `# CONFIRM` line naming a value only you can supply. It decides nothing on your
behalf -- in particular `site.repo` is blank, because deploying over a GitHub Pages repo
that already serves a page replaces that page.

## What the lookup already found

- **2 Semantic Scholar record(s)**: `3459255` (28 papers, 1562 citations), `2223799647` (1 papers, 31 citations).
  Two records for one person is the ordinary case and this repo handles it; both are listed so the merge can happen.
- **29 papers**, 23 of them with an arXiv id. The collector reaches an arXiv
  paper on its own; the remainder need either a DOI or a line in `data/overrides.yaml`.
- **DBLP**: `185/7904`
- **ORCID**: 0000-0002-1455-2266

`records.json` holds the raw responses, so any value above can be traced rather than
re-argued.

## Setup, in order

1. Fork `borgr/paper-geo` and clone it.
2. Empty the previous author's judgement out of `data/`, which is the step that matters:

       python scripts/bootstrap_fork.py --yes

   It deletes what the first run rebuilds, wipes the receipts that would otherwise
   redirect your URLs to someone else's retired pages, and empties the decision files
   (`paper_code.yaml`, `overrides.yaml`, `declines.yaml`, `followups.yaml`, `sidecars/`)
   while keeping the comment block at the head of each, which is how you find out what
   the file is for. Inheriting those files publishes another researcher's decisions --
   including decisions not to publish something -- under your name.
3. Paste the blocks from this `config.yaml` over the same blocks in the fork's
   `config.yaml`, then work through every `# CONFIRM`.
4. Check nothing of the previous author's is left:

       python scripts/bootstrap_fork.py --check

   It exits non-zero and prints each `config.yaml` line still carrying their name, ORCID,
   ids or URLs. No other check in the repo catches those, because for them they were right.
5. Build:

       python update.py

   Read `WORKLIST.md` when it finishes. It asks only for things no code can do: account
   actions behind a login, and approving text that would go out under your name.

## What it will and will not do for you

It re-derives your bibliography from public sources every run, builds a site with
per-paper structured data, and writes a worklist of the gaps. It does not touch any of
your accounts: every outward write (`--deploy`, `--apply`, `--accept`) is a separate
command you run deliberately.
