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
      [docs/SIDECAR_DESIGN.md](docs/SIDECAR_DESIGN.md), in file order. Each one ends
      as a rule in that file plus an enforcement in `validate.py` or the schema.
      Nothing else in this section starts before they are settled.
- [ ] **Regenerate the TIES sidecar** once the rules are settled. It is the only
      accepted sidecar, it was hand-written before the drafter existed, and it is
      the file every reader will look at first — it currently disagrees with all 19
      drafts on casing, voice and claim count (3 claims against a median of 16).
- [ ] **Fold the settled rules into the drafting prompt**, which lives in
      `scripts/draft_sidecars.py`. Today the rules have three homes — that prompt,
      the schema's `description` strings, and `docs/PAPERS.md` — so they are already
      three slightly different rule sets.
- [ ] **Add the shape enforcement** the schema cannot express: key order, field
      length bands, claims with no `qa` pointing at them, `qa` pointing at ids that
      do not exist. Formatter where mechanical, validator where not.

## Next — the papers themselves

- [ ] Verify the 19 drafts. Counted in `WORKLIST.md`, so no list here.
- [ ] Draft the remaining 93. The `draft` step does 10 a run; it finishes itself.
- [ ] `FAQPage` / `mainEntity` JSON-LD on paper pages — gated on the `qa` decisions,
      because which of 2–4 paraphrases becomes the canonical `name` is one of them.
- [ ] Generate the README/model-card claim snippet from the sidecar. [SHARED.md
      §5](docs/SHARED.md#5-say-the-same-thing-the-same-way) requires the canonical
      sentence to appear identically in several places; nothing enforces that, so
      today it is maintained by hand, which means it is not maintained.

## Then — repos

Deferred with a release condition in [`data/declines.yaml`](data/declines.yaml), so
`WORKLIST.md` keeps it counted at the bottom until the papers are done.

- [ ] Review the 30 proposed repo labels.
- [ ] Delete the `nlp-free` topic from the DORA proposal before any push — it looks
      invented, and a wrong topic is the failure mode `SKILL.md` names by example.
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

- [ ] `data/papers.yaml` stores observed, volatile state (`citations`,
      `hf_upvotes`, `hf_github_stars`) alongside stable identifiers, so an online
      run produces a diff that is mostly noise and the file's history cannot answer
      "what changed about my papers". The time series belongs in
      `measure/`, which already has the shape for it.
- [ ] `WORKLIST.md` emits a `- [ ]` item immediately followed by a `###` heading
      with no blank line between them, so that heading renders inside the list.
- [ ] Four ORCID works we cannot place are listed with `- ` rather than `- [ ]`,
      which means `declines.yaml`'s `items:` filter cannot match them.
