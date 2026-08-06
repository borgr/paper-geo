# The runbook: what runs, when, and who does it

The operating design, in one place. [USAGE.md](../USAGE.md) is the same loop
written for a human at a terminal and [SKILL.md](../SKILL.md) is the agent's entry
point; this file is the design those two implement — cadence, ownership, hand-off
points, and where each of them is weak.

Read the criticism at the bottom before trusting the top. It is part of the design,
not an appendix.

---

## 1. Cadence — four clocks, not one

Almost every mistake in a project like this comes from running the wrong clock's
work. There are exactly four.

| Clock | Trigger | What runs | Who |
|---|---|---|---|
| **Every run** | monthly, or after any change | `python update.py` — all ten steps, read-only | code, unattended |
| **On new material** | a paper posted, a repo created | `python update.py --refresh-bib`, then §5 | code, then a human once |
| **On a hand-back** | the run reports a draft or a proposal | fill the task file, `--ingest`, then the author accepts | agent, then the author |
| **On a decision** | the format or a rule is wrong | change the rule *and* its enforcement, together | a human, deliberately |

The fourth clock is the one this repo has been running lately, and it is the only
one where writing prose is the work. Confusing it with the first is how a rules
document turns into a diary.

Nothing is scheduled that publishes. `--apply` and `--deploy` are outside all four
clocks on purpose.

## 2. Every run: what the code does without being asked

`python update.py`. Ten steps, each independently re-runnable with
`--step <name>`, each read-only. What matters per step is not what it does but
**what it will not do** — that column is the contract.

| Step | Reads | Writes | Will not |
|---|---|---|---|
| `collect` | bib, Semantic Scholar, arXiv, HF | `data/papers.yaml` | overwrite anything in `overrides.yaml` |
| `repos` | GitHub | `data/repos.yaml` | touch a row with `reviewed: true` |
| `propose` | `data/repos.yaml` | `build/llm_tasks.json` | write to GitHub |
| `draft` | each paper's full text | `data/sidecars/drafts/` | write where the site can read it |
| `links` | full text, `data/papers.yaml` | `data/paper_code.yaml` | change a row with `reviewed: true`, or push to HF |
| `ownership` | collaborators' manifests | `paper-geo.json` | claim a paper someone else owns |
| `audit` | ORCID, arXiv, Wikidata, HF, S2 | `tasks/*` | edit any of those surfaces |
| `validate` | every data file + the docs | doc count sentences | fix a count that feeds an arithmetic claim |
| `render` | `data/` | `build/site/` | publish |
| `worklist` | all of the above + `followups`, `declines` | `WORKLIST.md` | list anything already done |

Two invariants hold this together, and both are worth stating as design rather
than as trivia:

- **Nothing derived is ever hand-edited.** A hand edit to a derived file survives
  until the next run and then vanishes, which is worse than failing, because it
  looks like it worked. Hand edits go to the four decision files in §6.
- **Every step degrades rather than fails.** A source outage costs one field, not
  the run. This is what makes the loop safe to schedule.

## 3. Every run: what a human reads, in order

The run ends by handing back three things, and the order is the design — it goes
from "look at the product" to "make a decision" to "publish".

1. **The rendered site**, `build/site/index.html`. The only artifact that shows the
   corpus as a reader meets it. Look here first; a report cannot tell you that a
   page reads badly.
2. **`WORKLIST.md`**, which is open items only. A section that is absent is done —
   that absence *is* the report, which is why nothing static is ever written into
   it. `## Deferred` at the bottom is real work with a release condition.
3. **The two gates**, if anything is ready: `sweep_github.py diff` then
   `update.py --apply`, and `build_site.py --deploy`.

## 4. Every run: what an agent does, in order

This is the procedure. Each step names what to read, what to produce, and **when
to stop and hand back** — the stop conditions are the load-bearing part, because
an agent that guesses instead of stopping produces confident wrongness under
someone else's name.

**Step 1 — run the loop.** `python update.py`. Read its output, not the files it
wrote. If a step failed, that is the whole task: report it and stop.

**Step 2 — check full-text coverage before drafting anything.**
`python scripts/fulltext.py --report`. Anything listed as thin will produce a thin
draft. *Stop condition:* a paper whose evidence says NOT AVAILABLE gets no draft
at all. Put it in the thin list; a sidecar written from a title is a page of
guesses.

**Step 3 — sidecar drafts.** If `build/sidecar_tasks.json` has unfilled tasks:
read its `system` and `user_template` first — they are the actual rules and they
override any summary of them, including this file. Then read
[SIDECAR_DESIGN.md](SIDECAR_DESIGN.md) for the settled shape rules, fill each
task's `sidecar` object against the embedded schema, and run
`python scripts/draft_sidecars.py --ingest`.
*Stop conditions:* never invent a magnitude — if the paper states no number, say
so in the claim text. Never accept your own draft; `--accept` is the author's.

**Step 4 — repo labels.** If `build/llm_tasks.json` has unfilled tasks: fill each
`proposal`, `python scripts/propose_topics.py --ingest`.
*Stop condition:* if the evidence does not support a label, leave it out and lower
`confidence`. A wrong topic is worse than a missing one, and it is the failure
this step has actually produced before.

**Step 5 — report, do not publish.** Say what changed, what is waiting, and which
of the two gates is ready. *Stop condition:* every write that leaves the machine
is the author's, with no exception and no "it was obviously fine".

**What an agent should not read** unless the task is about them: `STUDY.md`,
`docs/MEASURE.md`, `docs/SETUP.md`. They are evidence and one-time human
procedure. Reading them to draft a sidecar is 1,300 lines of context for no
decision.

## 5. On new material

1. `python update.py --refresh-bib` — picks it up and reports what it needs.
2. Claim it on arXiv unless you pressed submit yourself; step 4 is impossible
   without it.
3. Index and claim its Hugging Face paper page, `hf.co/papers/<arxiv-id>`.
4. Once it has a venue, add the journal-ref to the arXiv record.
5. Its sidecar is drafted automatically within a run or two; verify it.
6. Its code repo and project page are already deduced — read the row in
   `data/paper_code.yaml`, correct it, `reviewed: true`.

Only items 2–4 need a human, and all three are account actions no code can take.
Everything else arrives on its own, which is the property the whole design is
for.

## 6. Where a decision goes so it survives the next run

Four files, one per kind of decision. This is not bookkeeping: the loop re-derives
everything, so a decision recorded nowhere is a decision made again every month.

| Decision | Goes to |
|---|---|
| this paper record is wrong / these two are one paper | `data/overrides.yaml` |
| this repo's labels are right, freeze them | `reviewed: true` in `data/repos.yaml` |
| this paper's code/project link is right, freeze it | `reviewed: true` in `data/paper_code.yaml` |
| this task is not worth doing | `data/declines.yaml` |
| this task is worth doing, but not before X | `deferred:` in the same file |
| this can only happen after a date | `data/followups.yaml` |
| this claim is correct and I stand behind it | `draft_sidecars.py --accept <slug>` |
| we should build this, some day | [BACKLOG.md](../BACKLOG.md) |

---

## 7. Criticism: where this design is weak

**The loop is sound; the writing around it is not.** The ten steps, the four
decision files, and the two human gates are the right shape, and the evidence is
that a new paper now needs a human for exactly three account actions. Everything
below is about form, and form is why an agent gets it wrong anyway.

1. **One rule has three homes.** The sidecar rules live in the prompt inside
   `scripts/draft_sidecars.py`, in the `description` strings of
   `schema/sidecar.schema.json`, and in prose in `docs/PAPERS.md` §5. Three copies
   of a rule are three versions of it within a month, and the measured drift across
   20 sidecars is the proof. Fix: the prompt should be *generated* from the schema
   plus one rules file, so there is exactly one editable source.

2. **Nine documents, ~2,200 lines, and no single entry point that is a
   procedure.** An agent asked to do a routine run has to synthesise SKILL.md,
   PAPERS.md and an embedded prompt. This file is an attempt at the missing one; it
   is also, honestly, the tenth document, and it earns its place only if SKILL.md
   and USAGE.md shrink to pointers into it.

3. **The rules are prose where they should be checkable.** "Every coined name gets
   a generic gloss" is a machine-checkable condition written as a paragraph.
   Anything stated as a rule and not enforced by `validate.py` will be violated,
   and the violation will not be noticed.

4. **`validate.py` checks structure, not shape.** Schema-valid files vary 5× in
   `scope` length and appear in three different key orders. A formatter would end
   the whole class of problem; a validator that reports it would at least surface
   it. Neither exists.

5. **Two lists, one reader.** `WORKLIST.md` is generated and ranked; `tasks/*.md`
   are generated payloads; `BACKLOG.md` is hand-held intention. That is defensible,
   but the reader has to learn which is which before any of them helps.

6. **The agent's own procedure is not testable.** Every code step has a regression
   guard. Nothing checks that an agent following §4 produces an acceptable draft,
   so the only detector is the author noticing during `--accept` — which is exactly
   the review load the design was supposed to reduce.

## 8. Criticism: is each file's *form* right for its job?

The content is mostly right. The question here is only whether the shape fits what
the file is for.

| File | Job | Form verdict |
|---|---|---|
| `update.py` | one entry point | **right.** Ten dispatched steps, docstring per step stating why the tier below does not own it |
| `data/papers.yaml` | derived record per paper | **wrong in one way.** 8,487 lines mixing stable identifiers with volatile counts (`citations`, `hf_upvotes`), so every online run diffs noise and the history cannot answer "what changed". Move the counts to `measure/` |
| `data/overrides.yaml` | author's corrections | **right.** Small, keyed, commented, and the only thing that survives `collect` |
| `data/paper_code.yaml` | one deduced link pair per paper | **right shape, wrong container.** A dict keyed by slug is correct; carrying `score` and `why[]` — a model's reasoning — in the same row as a frozen human decision means the audit trail and the decision churn together |
| `data/declines.yaml` | decisions recorded as absence | **right,** and the `deferred:` key made it the only file that can express "later" |
| `data/followups.yaml` | dated waits | **right.** Date and reason in one place, surfaced by the next run |
| `data/sidecars/*.md` | the author's claims | **wrong form.** A `.md` file whose entire content is YAML front matter and a one-line body. Either the body carries prose the page uses, or this is a `.yaml` file pretending |
| `schema/sidecar.schema.json` | the contract | **half right.** It carries the *reasoning* for each field in `description`, which is the best thing about it — and it cannot express order, length, or cross-references, which is most of what actually drifts |
| `build/sidecar_tasks.json` | the agent's work order | **right, and underused.** Task plus system prompt plus schema plus evidence in one file is exactly the correct interface. It should be the *only* place the drafting rules live |
| `WORKLIST.md` | what needs the author | **right in principle** — generated, open-items-only, ranked by citations. Two blemishes: a `- [ ]` item collides with the next heading, and it mixes "click this account form" with "run this command" |
| `tasks/*.md` | one payload per external surface | **right.** Committed so they are browsable on GitHub, regenerated so they cannot go stale |
| `docs/SHARED.md`, `PAPERS.md`, `REPOS.md` | the rules | **wrong form for an agent.** Numbered rules with rationale read well and are unusable as a checklist. They should end in a table of checkable conditions, each pointing at the check that enforces it |
| `docs/SETUP.md` | one-time human setup | **right.** Long is fine; it is read once, by a person, in order |
| `docs/MEASURE.md`, `STUDY.md` | evidence | **right,** and correctly separated from the rules so neither is read during a run |
| `docs/SIDECAR_DESIGN.md` | the format's rules | **was wrong** — a retrospective list of open questions with no steps, which is what prompted this file. Rewritten as settled rules first, open decisions in a table |
| `BACKLOG.md` | parked intentions | **right, and the only correct place for it.** Nothing can derive an intention |
