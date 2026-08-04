---
name: paper-geo
description: >
  Keep a researcher's papers and code findable and correctly described by search
  engines, AI answer engines, and scholarly indexes. Use when asked to refresh
  paper metadata, label repositories, write a paper sidecar (claims / scope /
  misreadings), regenerate the publications site, or check what changed since the
  last run. Also use after posting a new paper or creating a new repo.
---

# paper-geo

One source of truth (`data/`), one command (`update.py`), and a short list of
things only a human can do (`WORKLIST.md`).

**Two tracks with different rules.** Read the one you're working in:

| | |
|---|---|
| [docs/SHARED.md](docs/SHARED.md) | rules that apply to both — identity, chunking, coined names, what not to do |
| [docs/PAPERS.md](docs/PAPERS.md) | 135 papers. Claims, metadata correctness, sidecars, the `links` map |
| [docs/REPOS.md](docs/REPOS.md) | 30 repos. Topics, descriptions, the three `kind`s, `CITATION.cff` |
| [docs/COLLAB.md](docs/COLLAB.md) | co-author ownership protocol: who owns a page, who links to it |
| [docs/MEASURE.md](docs/MEASURE.md) | how to tell whether any of it worked |
| [docs/SETUP.md](docs/SETUP.md) | the one-time account checklist — ORCID, arXiv ownership, Scholar, Wikidata, HF, Zenodo |
| [USAGE.md](USAGE.md) | how a human runs it: refresh, new paper, sidecars, co-authors |
| [STUDY.md](STUDY.md) | the evidence and mechanism behind all of it |

Only 1 of 30 repos maps to a paper — paper code mostly lives in collaborators'
accounts. Do not treat the repo track as "the code for the papers".

The generated artifacts are the visibility assets; this repo is where the facts
live so they stay consistent and regenerable. Nothing is published without an
explicit `--apply`.

## Routine refresh

```bash
python update.py                    # read-only: refresh, then report what needs a human
python scripts/sweep_github.py diff # exactly what would change on GitHub
python update.py --apply            # write it
```

`update.py` runs seven steps, each independently re-runnable:

| Step | Does | Writes |
|---|---|---|
| `collect` | bibliography + Semantic Scholar + arXiv + Hugging Face → one record per paper | `data/papers.yaml` |
| `repos` | refresh GitHub repo state, preserving prior edits | `data/repos.yaml` |
| `propose` | label repos that still lack topics or a description | `build/llm_tasks.json` |
| `ownership` | reconcile paper ownership with collaborators' manifests | `paper-geo.json` |
| `audit` | live-read the surfaces we don't control — ORCID, arXiv authority records, Wikidata, HF, S2 — and regenerate their payloads | `tasks/*` |
| `validate` | schema-check every data file, plus regression checks for bugs already shipped once | — |
| `worklist` | rank what only a human can do, by citations | `WORKLIST.md` |

Then, separately: `scripts/build_site.py --deploy` publishes the site,
`scripts/links_block.py` maintains README link blocks, `measure/check_structure.py`
and `measure/fidelity.py` are the two measurement instruments.

Run one with `--step <name>`. Add `--refresh-bib` to re-run the upstream
`publications` pipeline first (needs `sources.publications_path` in `config.yaml`).

## Labelling repos (the `propose` step)

Default mode is `skill`: the step writes `build/llm_tasks.json` and stops. Fill in
each task's `proposal` object against the embedded JSON schema, then:

```bash
python scripts/propose_topics.py --ingest
```

When labelling, two rules matter more than sounding good:

- **Accuracy over coverage.** A wrong topic misleads retrieval and reads as
  careless. If the evidence doesn't support a label, leave it out and lower
  `confidence`. An earlier keyword-matching version tagged a
  grammatical-error-correction repo `model-merging` and a sentence-similarity
  metric `pretraining` — that is the failure mode to avoid.
- **Search vocabulary, not project vocabulary.** Use the words someone who
  doesn't know the project would type. Coined names (TextArena, ZipNN, DOVE) are
  branding; put the plain phrasing in `generic_gloss`.

Set `reviewed: true` on a repo in `data/repos.yaml` to freeze it — later runs will
never re-propose or overwrite it.

For unattended runs (cron), set `llm.mode: api` in `config.yaml`; it needs
`ANTHROPIC_API_KEY` or an `ant auth login` profile.

## Writing a sidecar (the part no tool can do)

One file per paper at `data/sidecars/<slug>.md` — the only hand-written per-paper
input, and the highest-value ~10 minutes per paper. Full schema and drafting rules:
[docs/PAPERS.md](docs/PAPERS.md#rule-5-the-sidecar-is-the-only-thing-no-tool-can-write).

The rule that is easy to get backwards:

- **Questions: paraphrase deliberately.** Give 2–4 phrasings of each question.
  Engines fan a query out into many synthetic sub-queries and you cannot guess
  which phrasing wins.
- **Claims: never paraphrase.** A restated claim is a second, slightly different
  version of your own finding — it fragments corroboration and the two drift apart.
  So `qa` entries reference claim **ids**; the renderer emits each claim verbatim.
- **Never a question without its answer adjacent.** A question-only passage matches
  the query and then loses the citation, because the concrete answer isn't in the
  chunk. That is the worst of both outcomes.

Draft `claims` and `misreadings`, then hand back — a model can report what a paper
*says* about its limits but cannot rank which limitation actually binds. Don't strip
legitimate caveats to sound confident; precise claim plus explicit scope.

## New paper just posted

1. `python update.py --refresh-bib` — picks it up and reports what it needs.
2. Claim it on arXiv unless you submitted it — arXiv ownership defaults to whoever
   pressed submit, and step 4 is impossible without it (`tasks/arxiv_ownership.md`).
3. Index and claim its Hugging Face paper page: `hf.co/papers/<arxiv-id>`.
4. Once it has a venue, add the journal-ref to the arXiv record (see `WORKLIST.md`).
5. Write its sidecar.
6. If it has a repo: `python update.py --step repos` then label and apply.

## Recording a decision so it survives reruns

Everything is re-derived from live sources on each run, so a judgment call made by
hand must be written down or it gets undone:

- **Papers** → `data/overrides.yaml` (`force_merge`, `force_distinct`, `drop`, `fields`)
- **Repos** → the `reviewed: true` flag in `data/repos.yaml`

If the same item keeps reappearing in `WORKLIST.md`, it needs an override — and
usually an upstream fix too, so the correction propagates to Scholar, Semantic
Scholar, and OpenAlex rather than only to us.

## Don't

- Keyword stuffing, or padding topics to look complete — measured *negative* for
  generative-engine visibility.
- Hidden text or instructions aimed at automated readers. Retraction-adjacent.
- Publishing to extra preprint mirrors: it multiplies versions and defeats the
  version-matching that merges a paper's preprint and published records.
- Writing to GitHub without `diff` first.
