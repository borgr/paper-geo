# paper-geo

**How do you make your papers and code findable — and correctly described — by AI
answer engines and scholarly indexes?** This is a pipeline that audits the gap,
fixes the automatable part, and hands you a ranked list of what only you can do.

Built for one researcher's corpus (114 papers, 33 repos) but config-driven: fork
it, replace `config.yaml` and `data/`, and it runs for yours.

## Start here

Python 3.10 or newer, and two dependencies. Everything else is the standard library,
so a run in three years needs nothing that has since moved.

```bash
git clone https://github.com/borgr/paper-geo && cd paper-geo
pip install -r requirements.txt
python update.py
```

That first run is read-only in the sense that matters. It writes only inside this
checkout — `data/` holds the derived records, `build/` is gitignored scratch plus the
rendered site, `tasks/` holds payloads to paste, and `WORKLIST.md` is the ranked list
of what is left. No write reaches GitHub, arXiv, ORCID or Hugging Face until you pass
`--apply` or `--deploy`.

Then read two files. **`WORKLIST.md`** is what needs you, ranked by citations.
**`build/site/index.html`** is the corpus as a reader meets it. [RUN.md](RUN.md) is
the manual for everything after that.

To point it at your own corpus, replace `identity` and `ids` in `config.yaml` and
point `sources.bibtex_url` at your own `.bib`. Empty the `papers:` list in
`data/papers.yaml` so the first run rebuilds it from that bibliography, and pass
`python scripts/collect.py --allow-shrink` once, because the guard that refuses a run
holding much less data than the last commit is otherwise doing its job.
[docs/SETUP.md](docs/SETUP.md) is the account-by-account checklist that has to happen
alongside it.

## Where the site ends up

The generator writes into `build/site/` and publishes to GitHub Pages, so **you do
not need a domain to have somewhere to point at**. Without a dedicated domain, Pages
serves a `<user>.github.io` repo at that name. For this corpus that is
[borgr.github.io](https://borgr.github.io), with one page per paper beneath it.

    https://borgr.github.io/papers/tinybenchmarks-evaluating-llms-with-fewer-examples/

`site.repo` and `site.base_url` in `config.yaml` set both of those. Every canonical
URL, sitemap entry and JSON-LD `@id` in the output is derived from them, so moving to
a custom domain later is one config change and a rebuild rather than a hunt through
generated files.

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

Ten re-runnable steps, each independently `--step`-able: build one record per paper
from bibliography + Semantic Scholar + arXiv + Hugging Face; refresh repo state;
propose labels for anything unlabelled; draft the next batch of sidecars from each
paper's own full text; deduce each paper's code repo and project page; reconcile
ownership with co-authors; audit the surfaces we don't control; validate; render the
site; rank what only a human can do into `WORKLIST.md`. Eight of the ten are pure
code, two hand back a draft that nothing publishes, and the whole thing is read-only
unless you pass `--apply` — every outward-facing write goes through
`propose → diff → apply`.

What the first run found on this corpus: two Semantic Scholar author records
splitting the publication list in half, an ORCID with zero works, no Wikidata item,
94% of arXiv records missing a journal-ref (which is what Scholar matches citations
on), nearly half the papers with no Hugging Face page, zero GitHub topics across
every repo, and a venue name sitting in an index as a paper title. The full baseline
is [docs/EVIDENCE.md §6](docs/EVIDENCE.md#6-the-baseline-what-the-corpus-looked-like-before-any-of-this).

## Documentation

Eight files, and each rule has exactly one of them as its home. Two are read by a
model rather than a person: the drafting rules in `docs/SIDECAR.md` §2 and the
labelling rules in `docs/RULES.md` §11.2 are the literal prompt text, read out of the
markdown at runtime, so editing the doc changes what the model is told in the same
commit.

| | |
|---|---|
| [RUN.md](RUN.md) | **how to run it** — the four clocks, what each step will not do, a new paper, sidecars, co-authors |
| [docs/RULES.md](docs/RULES.md) | **the rules, once** — identity, chunking, coined names, papers, repos, co-authors, and what is actually enforced |
| [docs/SIDECAR.md](docs/SIDECAR.md) | the per-paper sidecar: the drafting prompt, the checkable rules, and the format decisions still open |
| [docs/SETUP.md](docs/SETUP.md) | **the one-time checklist** — ORCID, Scholar, Wikidata, HF, in order |
| [docs/EVIDENCE.md](docs/EVIDENCE.md) | what is actually known about GEO/AI retrieval, graded, including what is measured null — and how to tell whether this worked |
| [BACKLOG.md](BACKLOG.md) | what we parked on purpose — the only list here that nothing derives |
| [SKILL.md](SKILL.md) | agent entry point (Claude Code skill): the contract, the loop, the stop conditions |

## Design rules

- **Identifiers are truth; URLs are derived.** A stored URL drifts.
- **Human decisions are recorded, not remembered.** Everything is re-derived each
  run, so a judgment call goes in `data/overrides.yaml`, a `reviewed: true` flag, or
  `data/declines.yaml` — or it silently reverts. Deciding *not* to do something is a
  decision too, which is what the last of those is for.
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

All of it runs. See [RUN.md](RUN.md).

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
