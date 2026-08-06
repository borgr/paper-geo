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
| [docs/PAPERS.md](docs/PAPERS.md) | 112 papers. Claims, metadata correctness, sidecars, the `links` map |
| [docs/REPOS.md](docs/REPOS.md) | 31 repos. Topics, descriptions, the three `kind`s, `CITATION.cff` |
| [docs/RUNBOOK.md](docs/RUNBOOK.md) | **the procedure** — what runs on which clock, what an agent does step by step and when to stop |
| [docs/SIDECAR_DESIGN.md](docs/SIDECAR_DESIGN.md) | how to write a sidecar, step by step, plus the format decisions still open |
| [docs/COLLAB.md](docs/COLLAB.md) | co-author ownership protocol: who owns a page, who links to it |
| [docs/MEASURE.md](docs/MEASURE.md) | how to tell whether any of it worked |
| [docs/SETUP.md](docs/SETUP.md) | the one-time account checklist — ORCID, arXiv ownership, Scholar, Wikidata, HF, Zenodo |
| [USAGE.md](USAGE.md) | how a human runs it: refresh, new paper, sidecars, co-authors |
| [STUDY.md](STUDY.md) | the evidence and mechanism behind all of it |

Only 1 of 31 repos maps to a paper — paper code mostly lives in collaborators'
accounts. Do not treat the repo track as "the code for the papers".

The generated artifacts are the visibility assets; this repo is where the facts
live so they stay consistent and regenerable. Nothing is published without an
explicit `--apply`.

## The steady state, which is the point

Setting this up was the one-time cost and it is nearly paid. From here the work is
an update loop, and **the loop is where this skill spends its effort**: find what
changed about the papers, produce the GEO for it, hand a human one link. Ranked by
what should own each part — code, then a model, then a person:

| Who | Does | Why not the tier below |
|---|---|---|
| **Code** | `collect`, `repos`, `ownership`, `audit`, `validate`, `render` | All of it is re-derived from public sources. A human here is a human retyping a fetch. |
| **A model** | `propose` (repo labels), `draft` (sidecars from each paper's own full text) | Needs reading and judgement, so no rule does it — but it is a *reading*, so it lands as a draft nothing publishes. |
| **The author** | `--accept` a sidecar draft; any write that leaves the machine (`--apply`, `--deploy`) | An accepted sidecar is an assertion under the author's name, and only the author knows which misreading actually keeps happening. |

So the honest description of a monthly run is: one command, then one link. Everything
between them is code and a model, and the two human touches are both *decisions*
rather than transcription.

**Drafting from the paper, not from its title.** `scripts/fulltext.py` resolves each
paper's actual text through a chain of open sources — arXiv HTML, ACL Anthology,
Unpaywall, Semantic Scholar, Europe PMC, arXiv PDF — and `data/fulltext/` is the
escape hatch for the handful with no public copy. It exists because the first version
read one field and 12 papers therefore got sidecars written from their titles. Check
coverage with `python scripts/fulltext.py --report`; anything it lists as thin will
produce a thin draft, so fix that before drafting rather than after.

**Unattended, if you want it that way.** Every step is read-only and idempotent, so
the loop is safe on a schedule (`llm.mode: api` in `config.yaml` for the model steps).
What must not be scheduled is the accept and the publish — see the table.

## Routine refresh

```bash
python update.py                    # read-only: refresh, then report what needs a human
python scripts/sweep_github.py diff # exactly what would change on GitHub
python update.py --apply            # write it
```

`update.py` runs ten steps, each independently re-runnable:

| Step | Does | Writes |
|---|---|---|
| `collect` | bibliography + Semantic Scholar + arXiv + Hugging Face → one record per paper | `data/papers.yaml` |
| `repos` | refresh GitHub repo state, preserving prior edits | `data/repos.yaml` |
| `propose` | label repos that still lack topics or a description | `build/llm_tasks.json` |
| `draft` | draft sidecars for the next batch of papers that have none | `data/sidecars/drafts/` |
| `links` | deduce each paper's code repo and project page from its own full text | `data/paper_code.yaml` |
| `ownership` | reconcile paper ownership with collaborators' manifests | `paper-geo.json` |
| `audit` | live-read the surfaces we don't control — ORCID, arXiv authority records, Wikidata, HF, S2 — and regenerate their payloads | `tasks/*` |
| `validate` | schema-check every data file, plus regression checks for bugs already shipped once; refresh the corpus sizes stated in the docs | the doc sentences |
| `render` | rebuild the site locally, so the run ends in a page rather than a report | `build/site/` |
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

## Sidecars (the `draft` step)

One file per paper at `data/sidecars/<slug>.md`: the claims in quotable form, the
scope each holds under, coined terminology, and the misreadings worth pre-empting.
Full schema and rules:
[docs/PAPERS.md](docs/PAPERS.md#rule-5-the-sidecar-is-drafted-by-a-tool-and-verified-by-the-author).

**You draft; the author verifies.** A claim with its magnitude, a scope condition and
the gloss of a coined term are all in the paper — what the author uniquely holds is
whether a draft got them right and which misreading actually keeps happening. So:

```bash
python scripts/draft_sidecars.py --limit 20   # queue (or --slug <slug> ...)
python scripts/draft_sidecars.py --ingest     # fold your answers into drafts/
```

In `skill` mode the step writes `build/sidecar_tasks.json` and stops. Fill each task's
`sidecar` object against the embedded schema — the evidence field carries the paper's
full text, so use the paper's own numbers and cite where each came from (`Table 2`).
Drafts land in `data/sidecars/drafts/`, which **nothing reads**: the site, validator,
fidelity check and coverage count all glob `data/sidecars/*.md` one level up, so an
unverified draft cannot reach a published page. Only the author runs `--accept`.

Never invent a magnitude. If the evidence gives no number for a finding, say so in the
claim text — a wrong number is the one failure here that is worse than silence, because
it is quotable.

Each task's evidence names the source it came from (`full text (from acl-anthology
https://... , truncated)`). Read that line first: if it says the text is NOT AVAILABLE,
the honest move is to draft nothing and put the paper in `--report`'s thin list instead,
because a sidecar written from a title is a page of confident guesses under someone's
name. The chain and the `data/fulltext/` escape hatch are in `scripts/fulltext.py`.

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

A model can report what a paper *says* about its limits but cannot rank which
limitation actually binds — so draft it and hand back. Don't strip legitimate caveats
to sound confident; precise claim plus explicit scope.

## New paper just posted

1. `python update.py --refresh-bib` — picks it up and reports what it needs.
2. Claim it on arXiv unless you submitted it — arXiv ownership defaults to whoever
   pressed submit, and step 4 is impossible without it (`tasks/arxiv_ownership.md`).
3. Index and claim its Hugging Face paper page: `hf.co/papers/<arxiv-id>`.
4. Once it has a venue, add the journal-ref to the arXiv record (see `WORKLIST.md`).
5. Write its sidecar.
6. Its code repo and project page are already deduced from its own full text by the
   `links` step — read the row in `data/paper_code.yaml`, correct it if wrong, set
   `reviewed: true` to freeze it. `--apply` pushes the accepted ones to the Hugging
   Face paper page; the site shows them without waiting for that.
7. For the repo's own topics and description: `python update.py --step repos`, then
   label and apply.

## Recording a decision so it survives reruns

Everything is re-derived from live sources on each run, so a judgment call made by
hand must be written down or it gets undone:

- **Papers** → `data/overrides.yaml` (`force_merge`, `force_distinct`, `drop`, `fields`)
- **Repos** → the `reviewed: true` flag in `data/repos.yaml`
- **Code and project links** → the `reviewed: true` flag in `data/paper_code.yaml`,
  which also makes that row's own URLs the ones `--apply` pushes
- **A task ruled out** → `data/declines.yaml`, which stops `WORKLIST.md` asking

If the same item keeps reappearing in `WORKLIST.md`, it needs an override — and
usually an upstream fix too, so the correction propagates to Scholar, Semantic
Scholar, and OpenAlex rather than only to us. If it reappears because it was
*decided against* rather than left undone, that is `declines.yaml`: deciding not to
do something is a decision, and an unrecorded decision is made again every run.

## Don't

- Keyword stuffing, or padding topics to look complete — measured *negative* for
  generative-engine visibility.
- Hidden text or instructions aimed at automated readers. Retraction-adjacent.
- Publishing to extra preprint mirrors: it multiplies versions and defeats the
  version-matching that merges a paper's preprint and published records.
- Writing to GitHub without `diff` first.
