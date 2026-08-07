# The sidecar

One file per paper, `data/sidecars/<slug>.md`. It is the only artifact in this repo
whose content is judgment rather than derivation — everything else is re-fetched
from public sources each run and therefore cannot drift. This one can, and has.

**§2 is the drafting prompt.** Not a description of it: `scripts/draft_sidecars.py`
reads the block between the markers and sends it to the model, so editing §2 changes
what the drafter is told in the same commit. That is the one-source rule this file
used to violate.

Who does what: a model drafts, the author accepts. Nothing else in the pipeline can
read a draft — the site, the validator, the fidelity check and the coverage count
all glob `data/sidecars/*.md` non-recursively, and drafts sit in `drafts/` one level
down. See [../RUN.md](../RUN.md).

Two halves, deliberately separate: **§2–§4 are settled** and enforced where the
last column of §4 says so. **§6 is open** — each row is a decision nobody has made,
with the real options and what ships if we keep not deciding.

---

## 1. Before drafting: is there anything to draft from?

`python scripts/fulltext.py --report` says which papers resolved to real text and
which are thin. Each task in `build/sidecar_tasks.json` carries the same answer on
the first line of its `evidence` field: the source it came from and whether the text
was truncated.

A paper with no available text gets **no draft at all**. That is a stop, not a
degraded mode — a sidecar written from a title and an abstract is a page of
confident guesses published under an author's name, which is worse than a missing
page in every way that matters. Drop the paper's PDF into `data/fulltext/<slug>.pdf`
(gitignored, checked first) and re-run, or leave it in the thin list.

## 2. The rules

<!-- prompt:start -->
What you produce is consumed two ways: rendered on the paper's canonical page, and
retrieved as isolated passages by retrieval-augmented systems. The second drives
every rule below.

Write the fields in this order. They depend on each other in this direction, and
writing the questions first produces questions whose answers you then have to
invent.

**1. Find the paper's own numbers first.** Locate the tables and figures carrying
the results before writing a word. Every claim will cite one of them. If you cannot
find the number for a finding, that finding does not become a claim with an invented
magnitude — either the claim says the paper reports no magnitude, or it is left out.

**2. Claims are the core**; everything else is scaffolding. Each one:

- **is self-contained.** It will be retrieved alone, with no title and no
  surrounding paragraph, so it must name the object, the finding and the magnitude
  in one sentence. No "we", no "this paper", no pronoun pointing outside the
  sentence.
- **carries the number the paper reports, with its unit and its baseline.**
  "Improves accuracy" is worthless; "raises exact-match by 4.6 points over the
  fine-tuned baseline on the WMT16 en-de test set" is a claim.
- **has an `id`** matching `^[a-z0-9-]+$`. Ids are internal — no reader ever sees
  one.

**3. `scope`, per claim:** the conditions under which the claim holds, and where it
does not. This is **content, not a disclaimer**. "Further research is needed" is
worthless; "holds for models above 1B parameters; the 125M model shows no effect" is
scope. It is a separate, adjacent field because summarisers drop scope far more
often than they drop findings, which is the most common way a paper ends up
misrepresented.

**4. `evidence`, per claim:** where it comes from — "Table 2", "Figure 4b",
"Section 5.1". Cheap to write, and the strongest signal to a skeptical reader that
the claim was not generated.

**5. Questions.** Each `qa` entry is **one question in 2–4 paraphrases**, answered
by a list of claim **ids**. The rule that is easy to get backwards:

| | Rule | Why |
|---|---|---|
| Questions | **paraphrase deliberately** | engines fan one query into many synthetic sub-queries; you cannot know which phrasing wins, so cover several |
| Claims | **never paraphrase** | a restated claim is a second, drifting copy of the author's own finding, and the two then compete for the same citation |

So `answers` holds ids and never prose. The renderer resolves each id to the claim's
sentence verbatim plus its scope, so a reader sees the question followed immediately
by the real answer — never a slug, never a paraphrase. **Never a question whose
answer is not adjacent.**

Phrase questions in the vocabulary of someone who has **not** read the paper. A
question built around the paper's own coined name has no lexical path from what
people actually type.

**6. Misreadings** are stated as corrections, not as questions: what people wrongly
conclude, and what is actually true. Only include one the paper gives you a reason
to expect — a result that is easy to over-generalise, a negative result, a method
whose name promises more than it does. Do not invent a plausible misunderstanding.

**7. Terminology** is only for terms this paper coins or uses in a non-obvious
sense. Not a glossary of the field.

**8. `coined` and `gloss`,** only if the paper actually coins a name. `gloss` is the
plain-language phrase that goes adjacent to the name everywhere.
`TIES-Merging` has no lexical route from "how do I combine fine-tuned models"; the
gloss is that route.

**9. `one_liner`:** the one sentence the author will reuse verbatim in the page, the
README, the model card and the talk abstract. Under 320 characters, quotable,
specific. Identical reuse is the mechanism — rewording it in each place fragments
the corroboration that makes retrieval systems trust it.

**Accuracy over coverage, everywhere.** Three claims you can point at a table for
are worth more than eight that read well. If the evidence you were given does not
support something, leave the field out rather than filling it. Never infer results
from the title, the venue, or what similar papers usually find. You are drafting for
the paper's own author, who will verify every line, so precise and checkable beats
complete and smooth.
<!-- prompt:end -->

## 3. What one looks like

Front matter is the machine-readable part. The body below the closing `---` is
optional author prose, rendered on the paper page and in its `llms.txt` under
"Notes from the author" — it is where a sentence in the author's own voice goes, and
the reason this is a `.md` file rather than a `.yaml`. It is escaped, not parsed as
markdown: blank lines split paragraphs and nothing else is interpreted. The drafter
never writes it; it is the one part of the file a model has no business filling.

```yaml
---
key: yadav2023ties
coined: TIES-Merging
gloss: merging fine-tuned models by trimming, electing signs, and averaging
one_liner: >
  TIES-Merging combines independently fine-tuned models into one by resolving
  parameter-sign conflicts, outperforming task arithmetic across 11 tasks.

qa:
  - q:
      - how do I combine multiple fine-tuned models without retraining?
      - why does averaging fine-tuned weights hurt performance?
      - what is model merging?
    answers: [sign-conflict]

claims:
  - id: sign-conflict
    text: >
      Trimming low-magnitude parameter changes and resolving sign conflicts
      before averaging outperforms plain weight averaging across 11 tasks.
    scope: T5-base/large and ViT; up to 7 models; same architecture and init.
    evidence: Table 2

misreadings:
  - It is not a training method -- no gradient steps are required.
  - It does not merge models with different architectures.

terminology:
  interference: >
    Two specific things in this paper: redundant parameter values, and
    disagreement on a parameter's sign across models. Not a general term.

links_extra:
  code: https://github.com/prateeky2806/ties-merging
---
```

The accepted `data/sidecars/ties-merging-*.md` is the live worked example. Schema:
[`../schema/sidecar.schema.json`](../schema/sidecar.schema.json), whose `description`
strings carry the *reasoning* for each field.

## 4. The rules in checkable form

Everything above as a validator takes it. Anything stated as a rule and not enforced
gets violated without anyone noticing, so the last column is part of the rule.

| | Rule | Enforced by |
|---|---|---|
| 1 | required: `one_liner`, `claims` | schema |
| 2 | `one_liner` ≤ 320 chars | schema |
| 3 | claim `id` matches `^[a-z0-9-]+$` | schema |
| 4 | every claim has `text` and `scope` | schema |
| 5 | no key outside the schema | schema (`additionalProperties: false`) |
| 6 | `qa[].q` has 1–5 entries | schema, plus `validate.py check_sidecars` for the empty case |
| 7 | every `answers` entry is an existing claim id | `validate.py check_sidecars` |
| 8 | the rules block in §2 exists and is non-trivial | `validate.py`, and `draft_sidecars.py` raises rather than sending an empty prompt |
| 9 | a draft can never reach a page | file layout: the site globs `data/sidecars/*.md`, drafts sit one level down |
| 10 | every claim is pointed at by some `qa` entry | **nothing — open, D3** |
| 11 | `coined` present ⇒ `gloss` present | **nothing — open, D2** |
| 12 | canonical key order | **nothing — open, D1** |
| 13 | `text` and `scope` within a length band | **nothing — open, C2** |

## 5. What the drift actually looks like

Measured across the 19 drafts plus the one accepted sidecar. This is the evidence
for §6 existing, and the reason to distrust any rule not in the table above.

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

## 6. The open decisions

Each row is answerable as it stands. "If we do nothing" is what ships otherwise — a
real outcome in every case, which is why leaving these open is itself a choice.
Tracked in [../BACKLOG.md](../BACKLOG.md).

### Shape and enforcement

| | Decision | Options | If we do nothing |
|---|---|---|---|
| D1 | canonical key order | (a) fixed order, rewritten by a formatter; (b) fixed order, reported by the validator; (c) no rule | three orders, growing |
| D2 | which optional keys become conditional requirements | `coined ⇒ gloss` is already a rule in [RULES.md §4](RULES.md#4-the-coined-name-rule) and is machine-checkable; same question for `key`, `terminology`, `misreadings` | a documented rule nothing enforces |
| D3 | cross-reference checks | a claim no question points at: error, warning, or ignored. (Dangling `answers` ids are already an error) | a claim renders with no route to it |
| D4 | formatter or validator | `validate.py --fix-counts` set the precedent that mechanical things get fixed rather than reported. Key order, list order, id casing and wrapping are all mechanical | hand-fixing, inconsistently |

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
background question that gets 100× the query volume is today's outcome, and it is an
accident rather than a choice.

### The claims

| | Decision | Options | If we do nothing |
|---|---|---|---|
| C1 | what granularity is one claim | one experimental result, one takeaway, or one quotable sentence. 3 to 22 per paper is a factor of 7 | a factor of 7 |
| C2 | `scope` shape | (a) prose with a length cap; (b) a template — *holds for … ; untested for … ; fails when …*; (c) structured subfields. Whichever it is, it has to survive a paper whose scope is genuinely one clause | 124–694 chars |
| C3 | is `evidence` required | optional today; cheap to write; the strongest anti-hallucination signal on the page | present when the model bothered |
| C4 | are claim ids stable identifiers | if anything ever links `#no-retraining`, renaming breaks it. Either promise stability, or state that they are internal and unlinkable | undefined, so unsafe either way |

### Reach and lifecycle

Ownership is settled: one sidecar per paper, one owner, and a co-author who wants to
contribute claims PRs the owner's file rather than keeping their own
([RULES.md §12](RULES.md#12-co-authors)). What is open is everything downstream of
that.

| | Decision | Options | If we do nothing |
|---|---|---|---|
| A1 | is the author's slant separable | if two authors lead with different claims, is that an overlay on one shared claim set, or two files? | not expressible |
| A2 | minimum viable sidecar | 3 claims vs 22 — is there a floor below which we render no page? | a thin page ships |
| A3 | a "no sidecar, ever" verdict | most papers have no draft and some never should — workshop reports, position pieces someone else led. Absence currently reads as "not done yet" | the worklist asks forever |
| E1 | `FAQPage` / `mainEntity` JSON-LD | absent today. [RULES.md §6](RULES.md#6-dont) warns against markup not backed by visible text — here it *is* backed, which is the exempt case. Blocked on Q2: `Question` takes one `name`, so one paraphrase has to be canonical | visible HTML only |
| E2 | publish the machine-readable sidecar | a `.yaml` or `.jsonld` beside each page would let co-authors consume claims verbatim instead of paraphrasing them, which is the mechanism [RULES.md §5](RULES.md#5-say-the-same-thing-the-same-way) depends on | they paraphrase |
| E3 | what a co-author's site emits for a paper it does not own | `rel=canonical` at the owner — but does it also carry the claim sentences (corroboration) or only the pointer (no duplicate content)? The two rules point opposite ways | unresolved in the docs too |
| F1 | review granularity | `--accept` is all-or-nothing over ~16 claims and ~14 question groups | the author reviews thirty items or none |
| F2 | re-drafting an accepted sidecar | `--replace` overwrites, and author edits are lost silently. Immutable, three-way merged, or diffed for review? | silent loss |
| F3 | what a collaborator's install needs | the propagation target: 30 papers, defensible sidecars, without reading this file. Schema + formatter + prompt + one worked example? And what keeps their files from drifting from ours — a shared spec, or a shared tooling version? | they fork and diverge |
| F4 | staleness | `supersedes` / `superseded_by` exist and nothing sets them; a preprint claim can be corrected in camera-ready | stale claims look current |
