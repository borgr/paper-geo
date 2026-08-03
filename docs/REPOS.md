# The repositories track

30 non-fork repos. Read [SHARED.md](SHARED.md) first — this file only covers what
is specific to repositories.

## What makes this track different

The papers track fights for position in surfaces someone else owns. This track
owns its surface completely, and GitHub is a top-5 AI-cited domain — so the
ceiling is higher and the work is cheaper. The catch is that almost none of it
is about papers.

**The paper↔repo link barely exists here: 1 of 30 repos maps to a paper.** Paper
code lives in collaborators' and organisations' accounts (`prateeky2806/ties-merging`,
`ibm-research/*`). Planning this track around "paper code" would mis-target 29 of
30 repos.

## The three kinds, and why they need different treatment

Set on each repo as `kind` in [`repos.yaml`](../data/repos.yaml).

### `guide` — the highest-value category, and the one easiest to overlook

`facultips`, `post`, `arXiv_stuck`, `paper_updated`, `tutEval`, `paper-sharpener`.

These answer **question-shaped queries** — literally what people type into an
assistant: *"why is my arXiv paper stuck"*, *"how do I apply for a tenure-track
job"*, *"how do I find a postdoc"*, *"how do I evaluate an LLM"*. Under
query-fan-out, that is the closest match to real demand in the whole account, on a
top-5 cited domain.

They were at 0 stars, 0 topics, some with no description. Rules:

- The README's **first line answers the question in the title.** Not "this repo
  contains…" — the answer.
- One heading per sub-question, phrased as the question.
- Dated. Recency is a gatekeeper-level factor and a guide's date is not frozen the
  way a paper's is. Add "last reviewed: YYYY-MM" and mean it.
- Several already publish via GitHub Pages (`facultips`, `post`, `arXiv_stuck`).
  Set `homepage` to the site so the repo and the site reinforce each other.
- **No `CITATION.cff`** — there is no paper to cite.

### `paper-code` — a minority, and mostly not in this account

`DORA`, `USim`, `EoE`, `IBGEC`, `auto_challenge_sets`, `ordert`,
`GEC_UD_divergences`, `assess_learner_language`, `GEC_BOTHER`, `languageClustering`.

Retrieved by citation-shaped queries. The lever is a bidirectional paper↔repo link:

- **`CITATION.cff`** — GitHub renders a "Cite this repository" widget from it, and
  it is machine-readable. **0 of 9 flagship repos had one.** Generated from the
  paper's verbatim `bibtex`.
- **arXiv link in the README** — Hugging Face extracts the id from it and
  auto-tags the repo on the paper page, cross-listing it with any models and
  datasets. This is the cheapest paper↔repo edge that exists.
- **README states the finding, with the number**, not just usage instructions.
  For method questions the README, not the PDF, is what gets cited.
- `homepage` → the paper's page on the site, once generated. Until then the
  sweep defers it rather than publishing a link to a 404.

For paper code in **someone else's** repo, the equivalent is a pull request:
`CITATION.cff` plus the arXiv link. That is social, not automatable, and belongs
on a person's todo list rather than in this pipeline.

### `tool` / `dataset` / `teaching` / `website` / `other`

`PoissonBinomial`, `gcn_tf`, `wit3scripts`, `social-follow`, `ATProto-links-bot`,
`grant_search`, `publications`, `C-course`, `intro2cs`, `borgr.github.io`,
`autofly`, `chara`, `chera`, `l---l`.

Standard hygiene: accurate description, honest topics, and for `teaching`/`other`,
don't over-invest. Two repos (`chera`, `chara`) have no content at all — candidates
for `skip: true` or archiving. An empty repo with a confident description is worse
than an empty repo.

## Topic rules

GitHub topics are its primary discovery facet and this account had **zero on every
repo**.

- **Accuracy over coverage.** A wrong topic misleads retrieval and reads as
  careless. The keyword-matching first attempt tagged a grammatical-error-correction
  repo `model-merging` and a sentence-similarity metric `pretraining` — about a
  third wrong. That is why labelling moved to a model with a review gate, and why
  `confidence` is a required field.
- **3–8 topics.** Padding is keyword stuffing wearing a different hat.
- **Widely-used terms over project names.** `grammatical-error-correction`, not
  `gec-ud-divergences`.
- **Omit rather than guess.** Empty-but-correct beats full-but-wrong. Two repos
  legitimately have no topics.
- Forks get nothing. They are not yours to describe, and topics on a fork are
  noise. 60 of the 90 repos are forks and are excluded.

## Description rules

One line, under ~120 chars, saying what the thing **is** and what it's **for**.
No marketing. Coined name → put the plain phrasing in `generic_gloss` and lead
the description with it.

Seven repos had no description at all. A repo with no description is invisible to
GitHub search regardless of its topics.

## Workflow

```bash
python update.py --step repos          # refresh live state, preserve every edit
python scripts/propose_topics.py       # label what still lacks topics/description
python scripts/propose_topics.py --ingest
python scripts/sweep_github.py diff    # exactly what would change
python update.py --apply               # write it
```

`reviewed: true` on a repo freezes it permanently against future proposals. That
flag is the whole idempotency story for this track: re-running `propose` refreshes
stars, current topics, and paper links, and carries forward `description`,
`topics`, `homepage`, `kind`, `generic_gloss`, `skip`, and `reviewed`.

## Priority order

1. Topics + descriptions on all 30 — fully automatable, one afternoon, ships today
2. `CITATION.cff` on the paper-code repos that are yours
3. README first-line rewrite on the six `guide` repos — highest query-match in the account
4. arXiv links in READMEs → free HF paper-page cross-listing
5. PRs adding `CITATION.cff` to collaborators' repos — social, slow, optional
6. `skip: true` or archive the empty repos
