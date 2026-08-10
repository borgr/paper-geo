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

- [ ] **Work through the remaining open decisions** in
      [docs/SIDECAR.md §6](docs/SIDECAR.md#6-the-open-decisions), in file order. Each
      one ends as a rule in §2 (which is the prompt) plus an enforcement in
      `validate.py` or the schema. The claim-side decisions are settled and recorded
      there (D2, D3, C1, C2, C3, C6, A2, Q4, Q6); what is left is **the question
      list** — Q1 natural-vs-query, Q2 what varies between paraphrases, Q3 person,
      Q5 field names, Q8 minimum share of general questions — and the formatter pair
      D1/D4 below.
- [ ] **Re-draft the 17 stale drafts, or delete them.** Every one was written before
      `kind`, the bands and the no-invented-number check existed: none has a `context`
      claim, so `--accept` refuses each of them, and `pending()` skips any paper that
      already has a draft — so no run will replace them. `draft_sidecars.py --all`
      re-queues them. **The design hole behind it:** nothing marks a draft as written
      under superseded rules, so a stale draft is indistinguishable from a fresh one
      until an accept fails. A rules-version stamp in the draft header would make it
      mechanical.
- [ ] **Finish the shape enforcement** the schema cannot express. Field length bands,
      claim-count bands and claims with no `qa` pointing at them are now
      `check_sidecar_shape()` in `validate.py`; key order, list order, id casing and
      wrapping are not, and are the formatter question D1/D4. (`qa` pointing at ids
      that do not exist is an error in `check_sidecars`.)
- [ ] **Reconcile the schema's `description` strings with the prompt.** The rules now
      have two homes, not three: `docs/SIDECAR.md` §2 is read verbatim by the drafter,
      but `schema/sidecar.schema.json` still states the reasoning per field in its own
      words. Either the schema descriptions get generated from the doc, or they shrink
      to the mechanical constraint and point at the doc for the why.

## Next — the papers themselves

- [ ] Verify the drafts. Counted in `WORKLIST.md`, so no list here.
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

- [ ] Review the proposed repo labels. Nearly all are already live on GitHub verbatim,
      so this reads as "audit what shipped", not "approve a proposal" —
      `sweep_github.py diff` is down to one CITATION.cff line.
      A topic you delete needs `declined_topics` next to it, or the next `--ingest`
      puts it back — see [RULES.md §11.2](docs/RULES.md#112-labelling-topics-and-descriptions).
      Two descriptions on GitHub (`l---l`, `chara`) are low-confidence model text that
      was promoted before the confidence gate existed. Both repos are now `skip: true`,
      so nothing will rewrite them; the text stands until someone edits it by hand.
- [ ] `tai314159/MuLER` is private; it has to be made public before it can be linked.

## Blocked, not forgotten

- [ ] The four queued Wikidata edits on Q140867203. Credentials are installed and
      the dry run is clean; the sandbox classifier blocks the write from here, so it
      is one command for a human:
      `python scripts/wikidata_apply.py --apply`.
- [ ] `sweep_github.py apply` and `build_site.py --deploy` — both wait on an
      explicit go-ahead by design, not by accident.

## Decided against, with the measurement

- [x] **Splitting `scripts/audit_identity.py` by surface. Declined — it would decouple
      nothing.** The file is 1,595 lines and the obvious read is "five surfaces jammed
      together", so this is written down to stop the next person acting on that read.
      Measured with an AST walk: **zero calls between the orcid, wikidata, arxiv and hf
      function groups.** They are already independent. All coupling runs through `main()`,
      which is 501 lines — 60 of collect and 441 of one report — so a by-surface split
      moves 967 lines, breaks no dependency that exists, and leaves the actual monolith
      untouched.

      The split that *would* pay is **by layer, not by surface**: 23 of the 24 report
      sections read only their own surface's variables (the exception counts HF pages
      against the arXiv list), so each surface could own its collect functions and its
      report sections, leaving a ~150-line orchestrator. Blocked on a real question rather
      than effort — the summary table reads 21 values from all five surfaces, so it stays
      in the orchestrator, and the alternative is five per-surface reports instead of the
      one table that answers "is my identity in order" at a glance. That table is the most
      useful artifact the audit produces.

      And the safety net is thin: the file has no offline mode, every surface is a live
      read, and nothing pins its output — only its wiring. Verifying the move means a
      golden-file diff over the 7 task files it writes, across two live runs whose counts
      legitimately drift between them. Worth doing after the sidecar format, not before.

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
- [ ] **`data/papers.yaml` also carries 224 lines of derived nothing.**
      `ownership.py reconcile()` writes `owner: null` + `owner_source: unclaimed` for
      every unclaimed paper, so 112 papers contribute 224 lines that say only "no one
      has claimed this yet" — the default, stated 112 times. It is committed because
      nothing derived is ever hand-edited, and it is stable rather than volatile, so it
      churns once and then sits still. The fix is for the absence of an `owner` key to
      mean unclaimed — most readers already spell it `p.get("owner")` — but two do
      not: `ownership.py`'s report filters on `owner_source == "unclaimed"` and
      `build_site.py` indexes `p["owner"]` directly. And `owner_source` is what
      distinguishes "unclaimed" from "deferred to a peer's manifest", so dropping the
      first case makes the second easier to misread. Small, not free.
- [ ] **No formatter, only a validator.** `validate.py --fix-counts` set the
      precedent that mechanical things get fixed rather than reported, and then
      nothing else followed it. Key order, list order, id casing and line wrapping in
      the sidecars are all mechanical and all currently hand-fixed, inconsistently.
      This is the same item as the shape enforcement above, seen from the tooling
      side: whichever way D4 in `docs/SIDECAR.md` goes decides both.
- [ ] **The agent's procedure is only half tested.** One of the two proxies now
      exists: no claim may contain a figure absent from the paper's own full text
      (`check_sidecar_numbers()`), which is what caught an invented gap in a draft.
      The other does not: there is no fixture paper with a known set of numbers, so
      the check runs against whatever text the chain happened to resolve, and a
      thin extraction weakens it silently rather than failing. Everything else about
      "did the model follow the drafting rules" — voice, paraphrase axes, whether a
      scope states the real bound — is still checked only by a human reading the draft.
- [ ] **`WORKLIST.md` mixes two kinds of instruction.** Account actions no code can
      take ("open this arXiv form and paste this journal-ref") sit in the same ranked
      list as commands to run, and a reader has to notice which is which per item.
      Splitting them would help; ranking by citations across both is what makes it
      one list today.
