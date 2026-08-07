# Backlog — work we have parked on purpose

Hand-maintained. **Not generated, and nothing derives it** — which is exactly why
it exists: every other list in this repo is re-derived from live state, so none of
them can hold an intention.

The dividing line, so this file does not rot into a second worklist:

| Belongs here | Belongs elsewhere |
|---|---|
| a design decision not yet made | anything countable from `data/` → generated into [WORKLIST.md](WORKLIST.md) |
| code that should exist and doesn't | a task waiting on a date → [`data/followups.yaml`](data/followups.yaml) |
| an order of operations we agreed on | a task ruled out → [`data/declines.yaml`](data/declines.yaml) |
| a known wrongness we chose to ship | a section parked with a release condition → `deferred:` in the same file |

If an item here becomes countable, delete it and let the worklist count it.

---

## Now — the sidecar format

Everything else waits on this. The format is the one artifact that is judgment
rather than derivation, it has measurably drifted across 20 files, and it is what
gets copied to other people's installs — so drift here propagates.

- [ ] **Work through the open decisions** in
      [docs/SIDECAR.md §6](docs/SIDECAR.md#6-the-open-decisions), in file order. Each
      one ends as a rule in §2 (which is the prompt) plus an enforcement in
      `validate.py` or the schema. Nothing else in this section starts before they are
      settled.
- [ ] **Regenerate the TIES sidecar** once the rules are settled. It is the only
      accepted sidecar, it was hand-written before the drafter existed, and it is
      the file every reader will look at first — it currently disagrees with all 19
      drafts on casing, voice and claim count (3 claims against a median of 16). Its
      body is now empty on purpose: the body renders publicly as "Notes from the
      author", and what was there described the file's own review status. If you want
      a sentence in your own voice under the claims, that is where it goes — nothing
      else writes it.
- [ ] **Add the shape enforcement** the schema cannot express: key order, field
      length bands, claims with no `qa` pointing at them. Formatter where mechanical,
      validator where not. (`qa` pointing at ids that do not exist is already an error
      in `validate.py check_sidecars`.)
- [ ] **Reconcile the schema's `description` strings with the prompt.** The rules now
      have two homes, not three: `docs/SIDECAR.md` §2 is read verbatim by the drafter,
      but `schema/sidecar.schema.json` still states the reasoning per field in its own
      words. Either the schema descriptions get generated from the doc, or they shrink
      to the mechanical constraint and point at the doc for the why.

## Next — the papers themselves

- [ ] Verify the 19 drafts. Counted in `WORKLIST.md`, so no list here.
- [ ] Draft the remaining 93. The `draft` step does 10 a run; it finishes itself.
- [ ] `FAQPage` / `mainEntity` JSON-LD on paper pages — gated on the `qa` decisions,
      because which of 2–4 paraphrases becomes the canonical `name` is one of them.
- [ ] Generate the README/model-card claim snippet from the sidecar. [RULES.md
      §5](docs/RULES.md#5-say-the-same-thing-the-same-way) requires the canonical
      sentence to appear identically in several places; nothing enforces that, so
      today it is maintained by hand, which means it is not maintained.

## Then — repos

Deferred with a release condition in [`data/declines.yaml`](data/declines.yaml), so
`WORKLIST.md` keeps it counted at the bottom until the papers are done.

- [ ] Review the 30 proposed repo labels. 29 of the 30 are already live on GitHub
      verbatim, so this reads as "audit what shipped", not "approve a proposal" —
      `sweep_github.py diff` is down to one CITATION.cff line.
- [ ] **The `nlp-free` deletion is not recorded anywhere, so it will come back.**
      It was the one invented topic in 30 proposals, it is correctly absent from
      DORA's live topics — and it is still sitting in that row's `llm_proposal`.
      `promote()` skips only `reviewed: true` rows, DORA is not one, so the next
      `--ingest` copies the proposal back over `topics` including `nlp-free`. This
      violates the repo's own rule that human decisions are recorded rather than
      remembered, and it is the only place that rule is currently broken. Options:
      `reviewed: true` on the row (freezes everything, including the description),
      a per-topic decline, or `promote()` learning to treat a topic a human removed
      as a decision. Pick one before the next `--ingest`.
- [ ] `tai314159/MuLER` is private; it has to be made public before it can be linked.

## Blocked, not forgotten

- [ ] The four queued Wikidata edits on Q140867203. Credentials are installed and
      the dry run is clean; the sandbox classifier blocks the write from here, so it
      is one command for a human:
      `python scripts/wikidata_apply.py --apply`.
- [ ] `sweep_github.py apply` and `build_site.py --deploy` — both wait on an
      explicit go-ahead by design, not by accident.

## Known wrongness we chose to ship

Recorded rather than fixed, so the next person does not rediscover it as a bug.

- [ ] **`data/papers.yaml` stores observed, volatile state** (`citations`,
      `hf_upvotes`, `hf_github_stars`) alongside stable identifiers, so an online
      run produces a diff that is mostly noise and the file's history cannot answer
      "what changed about my papers". The time series belongs in `measure/`, which
      already has the shape for it. **Costed and declined for now:** those three
      fields have 59 call sites across 12 files, including the worklist's citation
      ranking, and the benefit is cleaner diffs — the wrong trade today, but a real
      wrongness rather than a preference.
- [ ] **No formatter, only a validator.** `validate.py --fix-counts` set the
      precedent that mechanical things get fixed rather than reported, and then
      nothing else followed it. Key order, list order, id casing and line wrapping in
      the sidecars are all mechanical and all currently hand-fixed, inconsistently.
      This is the same item as the shape enforcement above, seen from the tooling
      side: whichever way D4 in `docs/SIDECAR.md` goes decides both.
- [ ] **The agent's procedure has no test.** Every data-shaped rule has a schema or a
      `validate.py` check behind it, and `selftest()` covers the code paths with no
      data footprint — but "did the model follow the drafting rules" is checked only
      by a human reading the draft. The nearest mechanical proxies would be a fixture
      paper with a known set of numbers, and an assertion that no claim contains a
      figure absent from the evidence text. Neither exists.
- [ ] **`WORKLIST.md` mixes two kinds of instruction.** Account actions no code can
      take ("open this arXiv form and paste this journal-ref") sit in the same ranked
      list as commands to run, and a reader has to notice which is which per item.
      Splitting them would help; ranking by citations across both is what makes it
      one list today.
