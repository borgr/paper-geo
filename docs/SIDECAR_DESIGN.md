# The sidecar: how to write one, and what is still undecided

One file per paper, `data/sidecars/<slug>.md`. It is the only artifact in this repo
whose content is judgment rather than derivation — everything else is re-fetched
from public sources each run and therefore cannot drift. This one can, and has.

Two halves, deliberately separate:

- **§1–§3 are settled.** Follow them, in order. They are the rules the drafting
  prompt in `scripts/draft_sidecars.py` already enforces, restated here in the
  order you do them.
- **§5 is open.** Each row is a decision nobody has made, with the actual options
  and what ships if we keep not deciding. Work through them in order; each one ends
  as a rule in §1–§3 plus an enforcement in `validate.py` or the schema.

Who does what: an agent drafts, the author accepts. See
[RUNBOOK.md §4](RUNBOOK.md#4-every-run-what-an-agent-does-in-order).

---

## 1. Before writing anything

**Step 1. Get the paper's actual text.** `python scripts/fulltext.py --report`, or
read the `evidence` field of the task in `build/sidecar_tasks.json` — its first
line names the source and says whether the text was truncated.

**Step 2. If the text is not available, stop.** Draft nothing. A sidecar written
from a title is a page of confident guesses published under the author's name,
which is worse than a missing page in every way that matters. Report the paper as
thin instead.

**Step 3. Find the paper's own numbers.** Before writing a word, locate the tables
and figures carrying the results. Every claim will cite one of them. If you cannot
find the number for a finding, that finding does not become a claim with an
invented magnitude — it becomes a claim that says the paper reports no magnitude,
or it is left out.

## 2. Writing it, in the order the fields depend on each other

Claims first, then the questions that point at them, then everything else. Writing
questions first produces questions whose answers you then have to invent.

**Step 4. Claims.** The core; everything else is scaffolding. Each one is a single
sentence that will be **retrieved alone**, with no title and no surrounding
paragraph. So:

- Name the object, the finding and the magnitude in that one sentence. No `we`, no
  `this paper`, no pronoun pointing outside the sentence.
- Carry the number the paper reports, with its unit and its baseline. *"improves
  accuracy"* is worthless; *"raises exact-match by 4.6 points over the fine-tuned
  baseline on the WMT16 en-de test set"* is a claim.
- Give it an `id` matching `^[a-z0-9-]+$`. Ids are internal — no reader sees one.

**Step 5. Scope, per claim.** The conditions under which the claim holds and where
it does not. This is **content, not a disclaimer**: *"further research is needed"*
is worthless, *"holds for models above 1B parameters; the 125M model shows no
effect"* is scope. It is a separate field because summarisers drop scope far more
often than they drop findings, which is the most common way a paper ends up
misrepresented.

**Step 6. Evidence, per claim.** `Table 2`, `Figure 4b`, `Section 5.1`. Cheap to
write, and the strongest signal to a skeptical reader that the claim was not
generated.

**Step 7. Questions.** Each `qa` entry is **one question in 2–4 paraphrases**,
answered by a list of claim **ids**. The rule that is easy to get backwards:

| | Rule | Why |
|---|---|---|
| Questions | **paraphrase deliberately** | engines fan one query into many synthetic sub-queries; you cannot know which phrasing wins, so cover several |
| Claims | **never paraphrase** | a restated claim is a second, drifting copy of the author's own finding, and the two then compete for the same citation |

That is why `answers` holds ids and never prose. The renderer resolves each id to
the claim's sentence verbatim plus its scope, so a reader sees the question
followed immediately by the real answer — never a slug, never a paraphrase.

Phrase questions in the vocabulary of someone who has **not** read the paper. A
question built around the paper's own coined name has no lexical path from what
people actually type.

**Step 8. Misreadings.** What people wrongly conclude, stated as a correction and
not as a question. Only include one the paper gives you a reason to expect: a
result that is easy to over-generalise, a negative result, a method whose name
promises more than it does. Do not invent a plausible misunderstanding.

**Step 9. Terminology.** Only terms this paper coins or uses in a non-obvious
sense. Not a glossary of the field.

**Step 10. Coined name and gloss.** If the paper coins a name, `coined` holds it
and `gloss` holds the plain-language phrase that goes adjacent to it everywhere.
`TIES-Merging` has no lexical route from *"how do I combine fine-tuned models"*;
the gloss is that route. [SHARED.md §4](SHARED.md#4-the-coined-name-rule).

**Step 11. `one_liner`.** The one sentence the author reuses verbatim in the page,
the README, the model card and the talk abstract. Under 320 characters, quotable,
specific. Identical reuse is the mechanism — rewording it in each place fragments
the corroboration that makes retrieval systems trust it
([SHARED.md §5](SHARED.md#5-say-the-same-thing-the-same-way)).

## 3. The rules, in checkable form

Everything above as a validator would take it. Anything stated as a rule and not
enforced gets violated without anyone noticing, so the last column is part of the
rule rather than a footnote.

| | Rule | Enforced by |
|---|---|---|
| 1 | required: `one_liner`, `claims` | schema |
| 2 | `one_liner` ≤ 320 chars | schema |
| 3 | claim `id` matches `^[a-z0-9-]+$` | schema |
| 4 | every claim has `text` and `scope` | schema |
| 5 | no key outside the schema | schema (`additionalProperties: false`) |
| 6 | `qa[].q` has 1–5 entries | schema |
| 7 | every `answers` entry is an existing claim id | **nothing — open, D3** |
| 8 | every claim is pointed at by some `qa` entry | **nothing — open, D3** |
| 9 | `coined` present ⇒ `gloss` present | **nothing — open, D2** |
| 10 | canonical key order | **nothing — open, D1** |
| 11 | `text` and `scope` within a length band | **nothing — open, C2** |
| 12 | a draft can never reach a page | file layout: the site globs `data/sidecars/*.md`, drafts sit one level down |

## 4. What the drift actually looks like

Measured across the 19 drafts plus the one accepted sidecar. This is the evidence
for §5 existing, and the reason to distrust any rule not in the table above.

| | min | median | max |
|---|---|---|---|
| claims per paper | 3 | 16.5 | 22 |
| question groups | 2 | 14 | 19 |
| phrasings per group | 2.7 | 3.1 | 3.6 |
| claim text length | 182 | 306 | 411 |
| **`scope` length** | **124** | **530** | **694** |
| misreadings | 3 | 10.5 | 16 |
| terminology entries | 2 | 9 | 13 |

Three findings, which are not the same problem:

1. **Question style is already uniform** — 100% capitalized, 100% ending in `?`,
   ~3.1 phrasings, in every draft. The lowercase first-person outlier is TIES, the
   *accepted* one, hand-written before the drafter existed. The drafts agree with
   each other and disagree with the old file, so TIES is what needs regenerating.
2. **Key order is arbitrary** — three orders across 20 files; `key`, `links_extra`
   and `gloss` appear or vanish with no rule. JSON Schema cannot express order, so
   nothing catches it.
3. **`scope` varies 5×**, more than any other field, and it is the field where
   drift costs most.

Separately: `build_site.py` emits `ScholarlyArticle` JSON-LD but no `FAQPage` /
`mainEntity`, so the Q&A block is visible HTML only.

## 5. The open decisions

Each row is answerable as it stands. "If we do nothing" is what ships otherwise —
a real outcome in every case, which is why leaving these open is itself a choice.
Tracked in [BACKLOG.md](../BACKLOG.md).

### Shape and enforcement

| | Decision | Options | If we do nothing |
|---|---|---|---|
| D1 | canonical key order | (a) fixed order, rewritten by a formatter; (b) fixed order, reported by the validator; (c) no rule | three orders, growing |
| D2 | which optional keys become conditional requirements | `coined ⇒ gloss` is already prose in SHARED.md §4 and machine-checkable; same question for `key`, `terminology`, `misreadings` | a documented rule nothing enforces |
| D3 | cross-reference checks | dangling `answers` ids, and claims no question points at: error, warning, or ignored | a typo'd id silently renders nothing |
| D4 | formatter or validator | `validate.py --fix-counts` set the precedent that mechanical things get fixed rather than reported. Key order, list order, id casing and wrapping are all mechanical | hand-fixing, inconsistently |
| D5 | `.md` holding only front matter, or `.yaml` | (a) move to `.yaml`; (b) keep `.md` and give the body a job the page uses | a file whose extension lies |

### The question list

| | Decision | Options | If we do nothing |
|---|---|---|---|
| Q1 | natural questions or search queries | *"Does merging models require retraining?"* vs *"ties merging retraining required"*. (a) natural only; (b) both in one array; (c) both, separate fields — and whether the answer differs between crawl-fed engines and what a model already knows | natural only, by drafter habit rather than by decision |
| Q2 | what varies between the 2–4 paraphrases | (a) no rule; (b) an axis rule — one lay phrasing, one field-jargon phrasing, one task-oriented phrasing. Three syntactic rewrites of one wording buy far less than three lexical routes | syntactic near-duplicates |
| Q3 | first person or not | 0%–67% across the corpus. Practitioner queries are first-person (*"should I use this"*), literature queries are not. (a) allow both; (b) require one of each; (c) third person only | whatever the model felt like |
| Q4 | is `answers` needed at all | adjacency on the *page* is settled and not in question. The open part is whether a question may have an answer that is not already a claim — (a) no, promote it to a claim; (b) yes, allow prose | never tested, so unclear |
| Q5 | field names | `q` vs `questions` vs `phrasings`; `answers` vs `answered_by` vs `claims`. `q` holds an array, so a singular-looking name is mildly wrong and `question` would be worse. Cosmetic once, permanent after: every co-author's file and every future tool reads it | `q` / `answers` |
| Q6 | which scenarios the question set must cover | the table below | bottom lines only, ~14 of them |
| Q7 | how many question groups | 2 to 19 today. (a) a band, e.g. 5–10; (b) tied to claim count; (c) no rule. Nineteen groups means every passage competes with eighteen siblings on its own page | unbounded |

**Q6 in detail** — candidate scenario classes, to accept, reject or extend:

| # | Scenario | Query looks like | Covered today? | Ours to answer? |
|---|---|---|---|---|
| 1 | the paper's bottom lines | "does X help Y" | yes — nearly all of every draft | unambiguously |
| 2 | background / domain entry | "what is model merging" | rarely, and it is the highest-volume class | risks writing a survey we did not write |
| 3 | method selection | "best way to merge fine-tuned models" | sometimes | yes, if scoped to this method |
| 4 | reproduction / practical | "how many samples does tinyBenchmarks need" | sometimes | yes, and cheap |
| 5 | comparison to a named alternative | "TIES vs task arithmetic" | rarely | risks characterising someone else's work |
| 6 | negative results and limits | "when does merging fail" | this is what `scope` holds, not `qa` | yes, and it is the honest half |
| 7 | provenance / who | "who works on model merging" | not at all | no — that is the identity track |
| 8 | terminology | "what does interference mean in merging" | `terminology` holds it, never rendered as Q&A | yes |

The sub-question that matters more than the list: is there a **minimum per class**,
or a **cap per class**? Fourteen bottom-line questions crowding out the one
background question that gets 100× the query volume is today's outcome, and it is
an accident rather than a choice.

### The claims

| | Decision | Options | If we do nothing |
|---|---|---|---|
| C1 | what granularity is one claim | one experimental result, one takeaway, or one quotable sentence. 3 to 22 per paper is a factor of 7 | a factor of 7 |
| C2 | `scope` shape | (a) prose with a length cap; (b) a template — *holds for … ; untested for … ; fails when …*; (c) structured subfields. Whichever it is, it has to survive a paper whose scope is genuinely one clause | 124–694 chars |
| C3 | is `evidence` required | optional today; cheap to write; the strongest anti-hallucination signal on the page | present when the model bothered |
| C4 | are claim ids stable identifiers | if anything ever links `#no-retraining`, renaming breaks it. Either promise stability, or state that they are internal and unlinkable | undefined, so unsafe either way |

### Ownership and reach

| | Decision | Options | If we do nothing |
|---|---|---|---|
| A1 | one file per paper, or one per (paper × author) | [SHARED.md §10](SHARED.md#10-duplication-which-kind-helps-which-kind-hurts) settles the *page* — never duplicate it. Open: does a co-author hold their own sidecar for a shared paper? A second copy is either corroboration (§5) or two competing near-identical claim sets | whoever runs the tool first owns it, by accident |
| A2 | is the author's slant separable | if two authors lead with different claims, is that an overlay on one shared claim set, or two files? | not expressible |
| A3 | minimum viable sidecar | 3 claims vs 22 — is there a floor below which we render no page? | a thin page ships |
| A4 | a "no sidecar, ever" verdict | 93 papers have no draft and some never should — workshop reports, position pieces someone else led. Absence currently reads as "not done yet" | the worklist asks forever |
| E1 | `FAQPage` / `mainEntity` JSON-LD | absent today. [SHARED.md §6](SHARED.md#6-dont) warns against markup not backed by visible text — here it *is* backed, which is the exempt case. Blocked on Q2: `Question` takes one `name`, so one paraphrase has to be canonical | visible HTML only |
| E2 | publish the machine-readable sidecar | a `.yaml` or `.jsonld` beside each page would let co-authors consume claims verbatim instead of paraphrasing them, which is the mechanism §5 depends on | they paraphrase |
| E3 | what a co-author's site emits for a paper it does not own | `rel=canonical` at the owner, per §10 — but does it also carry the claim sentences (corroboration) or only the pointer (no duplicate content)? The two rules point opposite ways | unresolved in the docs too |
| F1 | one source for the rules | they live in three places: the prompt in `draft_sidecars.py`, the schema `description`s, and this file. Generate the prompt from the schema plus one rules file | three drifting rule sets |
| F2 | review granularity | `--accept` is all-or-nothing over ~16 claims and ~14 question groups | the author reviews thirty items or none |
| F3 | re-drafting an accepted sidecar | `--replace` overwrites, and author edits are lost silently. Immutable, three-way merged, or diffed for review? | silent loss |
| F4 | what a collaborator's install needs | the propagation target: 30 papers, defensible sidecars, without reading this file. Schema + formatter + prompt + one worked example? And what keeps their files from drifting from ours — a shared spec, or a shared tooling version? | they fork and diverge |
| F5 | staleness | `supersedes` / `superseded_by` exist and nothing sets them; a preprint claim can be corrected in camera-ready | stale claims look current |
