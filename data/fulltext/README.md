# Papers the open chain cannot reach

Drop a file here when `scripts/fulltext.py` reports a paper as thin and you hold a copy:

    data/fulltext/<slug>.pdf     # or .txt, or .md

`<slug>` is the paper's slug in `data/papers.yaml` — the same string as the filename in
`data/sidecars/`. `python scripts/fulltext.py --report` lists every slug with the number
of characters found and the source it came from; anything under 4000 is a paper the chain
missed.

This directory is checked *first*, before arXiv and before every aggregator. A file here
means you looked and decided, and that judgement beats a guess from an API.

## Everything here is gitignored, deliberately

`.gitignore` excludes `data/fulltext/*` except this README. A paywalled PDF is not ours
to redistribute, and a public repo is redistribution. What leaves this directory is a
sidecar: a dozen claims with their magnitudes and scope conditions, which is a
distillation you are entitled to publish about your own paper.

So this is the one input to the pipeline that is deliberately not reproducible from a
fresh clone. A rerun on another machine will report those papers as thin again until the
same files are put back, which is the correct failure — the alternative is a repo that
mirrors publisher PDFs.
