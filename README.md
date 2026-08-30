# paper-geo

**How do you make your papers and code findable — and correctly described — by AI
answer engines and scholarly indexes?** This is a pipeline that audits the gap,
fixes the automatable part, and hands you a ranked list of what only you can do.

Built for one researcher's corpus (114 papers, 33 repos) and config-driven, so it
runs for yours too. [Set it up for your own papers](#set-it-up-for-your-own-papers)
is the five-step version of that.

## Start here

Python 3.10 or newer, and two dependencies. Everything else is the standard library,
so a run in three years needs nothing that has since moved. The GitHub steps shell out
to the [`gh` CLI](https://cli.github.com), so run `gh auth login` once. Without it the
`repos` step reports a failure and the other nine carry on.

```bash
git clone https://github.com/borgr/paper-geo && cd paper-geo
pip install -r requirements.txt
python update.py
```

That runs against the corpus already in `data/`, which is the quickest way to see the
output before deciding whether you want it for your own. It writes only inside this
checkout — `data/` holds the derived records, `build/` is gitignored scratch plus the
rendered site, `tasks/` holds payloads to paste, and `WORKLIST.md` is the ranked list
of what is left. No write reaches GitHub, arXiv, ORCID or Hugging Face until you pass
`--apply` or `--deploy`.

Then read two files. **`WORKLIST.md`** is what needs you, ranked by citations.
**`build/site/index.html`** is the corpus as a reader meets it. [RUN.md](RUN.md) is
the manual for everything after that.

## Set it up for your own papers

Five steps, in order. None of them writes outward, so a wrong answer here costs a
re-run and nothing else.

**1. Fork [borgr/paper-geo](https://github.com/borgr/paper-geo) and clone your fork**,
then `pip install -r requirements.txt`.

**2. Empty the previous author's data.** This is the step that matters.

```bash
python scripts/bootstrap_fork.py         # prints what it would do, changes nothing
python scripts/bootstrap_fork.py --yes   # do it
```

`data/` holds three kinds of file and all three have to go. The derived records
(`papers.yaml`, `repos.yaml`, `fulltext/`) cost one slow run to rebuild. The receipts
(`slug_history.yaml`, `wikidata_created.yaml`, `arxiv_submissions.yaml`) are true
statements about someone else's records, and kept, they redirect your URLs to their
retired pages and skip creating items you do not have. The decision files
(`paper_code.yaml`, `overrides.yaml`, `declines.yaml`, `followups.yaml`, `sidecars/`)
are one researcher's judgement about their own work, several of them decisions *not*
to publish something — inherited, they publish that judgement under your name and
nothing downstream can tell the difference. The comment block at the head of each
file is kept, which is how you find out what the file is for.

**3. Put yourself in `config.yaml`.** `identity` and `ids` are who you are.
`sources.bibtex_url` points at your own `.bib`. `site.repo` and `site.base_url` decide
where the site lands, and [Where the site ends up](#where-the-site-ends-up) is worth
reading before you set `site.repo`, because deploying over a Pages repo that already
serves a page replaces that page.

**4. Check nothing of theirs survived.**

```bash
python scripts/bootstrap_fork.py --check
```

It exits non-zero and prints every `config.yaml` line still carrying the previous
author's name, ORCID, ids or URLs. No other check in the repo catches those, because
for them those values were correct.

**5. Build.**

```bash
python update.py
```

`collect` compares each run against the last committed `papers.yaml` and refuses to
write when coverage drops sharply, which is what a source outage looks like. It stands
down on its own when the two corpora share no slug at all. If you have co-authored
with the previous author some slugs do overlap, so pass
`python scripts/collect.py --allow-shrink` once and then re-run.

Then work through [docs/SETUP.md](docs/SETUP.md), the one-time checklist for the
surfaces themselves. Its first three items fix *who you are* across every index, and
nothing downstream resolves properly until that does.

To hand a colleague a bundle with their own records already looked up,
`python scripts/handover.py "Their Name"` builds one —
[handover/tamar-rott-shaham/](handover/tamar-rott-shaham/) is what it produces.

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

### The core, and everything else

The part that carries the effect is small. One accurate record per paper, a page per
paper carrying structured data an answer engine can read, and an identity that
resolves to one person across the indexes. That is the `collect`, `audit`, `render`
and `worklist` steps, `build_site.py --deploy`, and items 1–3 of
[docs/SETUP.md](docs/SETUP.md). A corpus with those done is findable and correctly
attributed, and stopping there is reasonable.

The rest is worth doing and none of it is a prerequisite. Repo labels (`repos`,
`propose`, `sweep_github.py`) matter for code nobody has described. Per-paper sidecars
(`draft`) are the strongest lever on being described *correctly* and also the most
expensive, because they need a model gateway and the author's approval on every claim.
The code-and-project-page deduction (`links`), co-author reconciliation (`ownership`),
Wikidata items, Hugging Face paper pages and the two measurement scripts are each a
surface to pick up once the core is in place.

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
