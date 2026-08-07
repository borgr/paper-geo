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

112 papers and 31 repos, one command (`update.py`), one source of truth (`data/`),
and a short ranked list of what only a human can do (`WORKLIST.md`).

## Your contract

**Everything except the soft text is code.** Eight of the ten steps re-derive public
facts from public sources; a human or a model in them is a human retyping a fetch.

**Your whole job in a run is filling two JSON objects** — `sidecar` in
`build/sidecar_tasks.json` and `proposal` in `build/llm_tasks.json`. Claims, scope,
evidence, questions, misreadings, terminology, gloss, topics, descriptions. That is
the part that needs reading and judgement, which is why it is yours.

**You never hand-edit `data/*.yaml`, never accept your own draft, never write
outward.** A hand edit to a derived file survives until the next run and then
vanishes, which is worse than failing because it looked like it worked. `--accept`
makes a claim an assertion under the author's name. `--apply` and `--deploy` write to
public records other people's tooling reads. All three are the author's.

## The loop

```bash
python update.py                              # read-only: ten steps, then a report
python scripts/draft_sidecars.py --ingest     # fold your sidecar answers into drafts/
python scripts/propose_topics.py --ingest     # fold your repo proposals into repos.yaml
```

1. **Run it.** `python update.py`, or one step with `--step <name>`. Read-only.
   `--refresh-bib` first if the bibliography has new entries.
2. **Read what it handed back.** The `propose` step writes `build/llm_tasks.json` and
   stops; the `draft` step writes `build/sidecar_tasks.json` and stops. Each task
   carries its own schema and its own evidence. If neither file appeared, the run
   needed nothing from you — say so and stop.
3. **Fill the objects, against the rules, not against your instinct for what reads
   well.** Sidecars: [docs/SIDECAR.md §2](docs/SIDECAR.md#2-the-rules), which is the
   literal prompt text, so it is also already in the task's `system` field. Repo
   labels: [docs/RULES.md §11.2](docs/RULES.md#112-labelling-topics-and-descriptions).
4. **`--ingest`.** Sidecars land in `data/sidecars/drafts/`, which **nothing reads** —
   the site, the validator, the fidelity check and the coverage count all glob
   `data/sidecars/*.md` one level up, so an unverified draft cannot reach a published
   page.
5. **Hand back.** Re-run `--step worklist` if you changed anything, then report what
   `WORKLIST.md` says needs a person, shortest path first. Stop there.

## When to stop instead of producing something

| If | Then |
|---|---|
| the task's `evidence` says the full text is **NOT AVAILABLE** | draft nothing. A sidecar written from a title is a page of confident guesses under someone's name. Report it as thin |
| the evidence gives no number for a finding | the claim says the paper reports no magnitude, or it is left out. **Never invent a magnitude** — a wrong number is the one failure worse than silence, because it is quotable |
| `scripts/fulltext.py --report` lists a paper as thin | fix that first, not after. A thin source produces a thin draft, and the first version of this read one field, so 12 papers got sidecars written from their titles |
| a repo or a `paper_code` row has `reviewed: true` | it is frozen. Do not re-propose it |
| the schema rejects what you wrote | fix the content. Do not loosen the schema |
| you are about to run `--accept`, `--apply`, `--deploy`, or `sweep_github.py apply` | that is the author's. Print the command instead |
| the same item keeps reappearing in `WORKLIST.md` | it needs a recorded decision, not another pass |
| you are tempted to read `docs/EVIDENCE.md` or `docs/SETUP.md` mid-run | don't. Neither is a procedure; one is why the rules exist, the other is one-time account work |

**Only 1 of 31 repos maps to a paper** — paper code mostly lives in collaborators'
accounts. Do not treat the repo track as "the code for the papers".

## Where the rules live

| | |
|---|---|
| [docs/RULES.md](docs/RULES.md) | the GEO rules, once: identity, chunking, coined names, papers, repos, co-authors, and a table of what is actually enforced |
| [docs/SIDECAR.md](docs/SIDECAR.md) | the sidecar spec. §2 **is** the drafting prompt, and §6 is what is still undecided |
| [RUN.md](RUN.md) | the operating design and the human's terminal guide — the four clocks, what each step will not do, the new-paper flow |
| [docs/SETUP.md](docs/SETUP.md) | the one-time account checklist. Read once, in order, by a human |
| [docs/EVIDENCE.md](docs/EVIDENCE.md) | what is known and how to tell whether it worked. Read rarely |
| [BACKLOG.md](BACKLOG.md) | parked on purpose. The only list here that nothing derives |

## Recording a decision so it survives the next run

Everything is re-derived each run, so a judgment call that is not written down is
made again every month. Where each kind goes is
[RULES.md §7](docs/RULES.md#7-record-every-decision-or-lose-it); the short form:
papers → `data/overrides.yaml`, repos and code links → `reviewed: true`, a task ruled
out → `data/declines.yaml`, a maybe-later → `data/followups.yaml`, an intention →
`BACKLOG.md`. Deciding *not* to do something is a decision.

If an item reappears because a public record is wrong, fix it upstream too, so the
correction reaches Scholar, Semantic Scholar and OpenAlex rather than only us.

## Don't

- Keyword stuffing, or padding topics to look complete — **measured negative** for
  generative-engine visibility, not merely useless.
- Hidden text or instructions aimed at automated readers. Retraction-adjacent.
- Stripping legitimate caveats to sound confident. Precise claim, explicit scope.
- Paraphrasing a claim. Paraphrase the *questions*, never the finding —
  [SIDECAR.md §2](docs/SIDECAR.md#2-the-rules) rule 5.
- Writing to GitHub without `diff` first.
