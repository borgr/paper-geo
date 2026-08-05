# paper-geo

**How do you make your papers and code findable — and correctly described — by AI
answer engines and scholarly indexes?** This is a pipeline that audits the gap,
fixes the automatable part, and hands you a ranked list of what only you can do.

Built for one researcher's corpus (135 papers, 30 repos) but config-driven: fork
it, replace `config.yaml` and `data/`, and it runs for yours.

## Why

Three separate systems have to find your work, and they have different entry
conditions: web crawlers (Bing → ChatGPT, Brave → Claude, Perplexity, Google), the
scholarly graph (Scholar, Semantic Scholar, OpenAlex, DBLP — what Elicit,
Consensus, and most literature agents actually query), and model pretraining.
Optimising one does little for the others, and most advice conflates them.

For work that is already well known, the failure mode is usually not being
unfindable. It's being found and described **wrongly** — overstated, mis-scoped, or
credited to the wrong result. LLM summaries overstate scientific conclusions about
5× more often than human ones. No index can fix that for you; publishing your own
claims and scope conditions is the only lever.

## What it does

```bash
python update.py                     # read-only: refresh everything, report what needs you
python scripts/sweep_github.py diff  # exactly what would change on GitHub
python update.py --apply             # write it
```

Four re-runnable steps: build one record per paper from bibliography + Semantic
Scholar + arXiv + Hugging Face; refresh repo state; label anything unlabelled with
a model; regenerate `WORKLIST.md`. Read-only unless you pass `--apply`, and every
outward-facing write goes through `propose → diff → apply`.

Real findings from the first run on this corpus: two Semantic Scholar author
records splitting the publication list in half, an ORCID with zero works, no
Wikidata item, 103 of 109 arXiv records missing a journal-ref (which is what
Scholar matches citations on), 50 papers with no Hugging Face page, zero GitHub
topics across every repo, and a venue name sitting in an index as a paper title.

## Documentation

| | |
|---|---|
| [STUDY.md](STUDY.md) | what's actually known about SEO/GEO/AI retrieval, graded by evidence quality, including what's claimed but measured null |
| [docs/SETUP.md](docs/SETUP.md) | **the one-time checklist** — ORCID, Scholar, Wikidata, HF, in order |
| [docs/SHARED.md](docs/SHARED.md) | rules for both tracks: identity, chunking, coined names, what not to do |
| [docs/PAPERS.md](docs/PAPERS.md) | the papers track — metadata correctness, the `links` map, sidecars |
| [docs/REPOS.md](docs/REPOS.md) | the repos track — topics, descriptions, `CITATION.cff` |
| [docs/COLLAB.md](docs/COLLAB.md) | co-author ownership protocol: who owns a page, who links to it |
| [docs/MEASURE.md](docs/MEASURE.md) | how to tell whether it worked, including a controlled design |
| [USAGE.md](USAGE.md) | **how to run it** — routine refresh, new paper, sidecars, co-authors |
| [SKILL.md](SKILL.md) | agent entry point (Claude Code skill) |

## Design rules

- **Identifiers are truth; URLs are derived.** A stored URL drifts.
- **Human decisions are recorded, not remembered.** Everything is re-derived each
  run, so a judgment call goes in `data/overrides.yaml` or a `reviewed: true` flag
  or it silently reverts.
- **Flag, don't auto-merge.** A wrong merge costs more to undo than a flag costs to
  read — the guard that keeps "BabyLM Turns 3" and "Turns 4" apart also blocks some
  real duplicates, and that's the right trade.
- **Accuracy over coverage.** A wrong topic or a padded claim is worse than an
  absent one. Keyword stuffing measures *negative*.
- **Read-only by default.** These writes land on public records other people's
  tooling reads.

## Not this

No hidden text, no instructions aimed at automated readers, no keyword stuffing,
no extra preprint mirrors, no citation-count games. Some of those are measured
counterproductive; the rest are norm-violating. The overlap between "helps machines
find your work" and "is honest scholarship" is large, and this stays inside it.

## Status

All of it runs. See [USAGE.md](USAGE.md).

Collection and deduplication, the override layer, repo labelling and the GitHub
sweep, collaborator ownership reconciliation, the site generator (135 paper pages
with `ScholarlyArticle` JSON-LD, highwire meta, per-paper `llms.txt`, sitemap,
robots), the README links block, the Hugging Face worklist, schema validation, and
the two measurement instruments.

Deliberately not automated: arXiv journal-refs (no write API), Hugging Face paper
indexing and authorship claims (needs an authenticated browser session), and
*accepting* a sidecar — the claims in one are drafted from the paper by
`scripts/draft_sidecars.py`, but only an author can confirm a magnitude and rank
which limitation actually binds, so drafts stay in `data/sidecars/drafts/` until
promoted.
