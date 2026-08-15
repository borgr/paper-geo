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
the results before writing a word. Then hold to one rule for the rest of the draft:
**every figure you write must appear in the paper's own text.** Not "a plausible
magnitude", not one inferred from a chart, not one carried over from a similar
paper. If you cannot find the number for a finding, the finding can still become a
claim — stated without a magnitude — but it never gets an invented one. This is the
only rule here with no exceptions, because a wrong number is the one error a reader
cannot detect and the author is publicly answerable for.

**2. Claims are the core**; everything else is scaffolding. Each one:

- **is self-contained.** It will be retrieved alone, with no title and no
  surrounding paragraph, so it must name the object and the finding without
  depending on anything outside itself. No "we", no "this paper", no pronoun
  pointing outside the claim.
- **carries one proposition,** and is as long as that takes. Not a paragraph
  covering three findings — a passage about three things embeds as their average
  and is retrieved weakly for each. Not one sentence with three findings stacked
  behind colons and dashes either, which is the failure the drafts actually have:
  the median claim's first sentence runs **43 words**, and the longest runs 79.
  A second finding is a second claim, not a second clause.
- **leads with the whole claim, then stops or explains.** Extractive answers quote
  the front of a passage and cut, so sentence one has to be true and complete on
  its own; sentence two, if there is one, carries the mechanism or the comparison.
  Two sentences of ordinary length are better than one of 43 words in every way
  that matters here — easier to read, and safe to truncate.
- **has an `id`** matching `^[a-z0-9-]+$`. Ids are internal — no reader ever sees
  one.
- **has a `kind`,** which decides what else it owes:

| `kind` | Asserts | `evidence` | Numbers |
|---|---|---|---|
| `result` *(the default)* | something the paper measured, demonstrated or reports | **required** — "Table 2", "Figure 4b", "Section 5.1" | carry the one the paper reports, with its unit and its baseline |
| `context` | what the paper *is*: what it contributes, what problem it opened, where it sits in its literature | optional, and usually absent | usually none — and any you do write still has to be in the paper |

A `result` claim without a magnitude is weak but honest. "Improves accuracy" is
worthless; "raises exact-match by 4.6 points over the fine-tuned baseline on the
WMT16 en-de test set" is a claim.

**Write at least one `context` claim, and treat it as load-bearing rather than as
filler.** The highest-volume questions an answer engine receives about any paper are
not about its Table 2. They are *"what is a good paper on evaluating language
models"*, *"who established that benchmarks saturate"*, *"what should I read first
about model merging"*. Those have no answer anywhere in a set of result claims, so a
page made only of result claims is invisible to them — and being the paper that gets
named there is worth more than being cited accurately on a number nobody asked for.
A `context` claim is how the page answers them, and it is expected to be
unverifiable against the paper: the paper does not contain a sentence certifying its
own standing.

That is a deliberate trade, and `scope` is what pays for it. An unverified claim is
safe in proportion to how honestly it is bounded, so a `context` claim's scope is
where the limit goes: *"one of the first to do X for Y; earlier work covered Y
without X"*, *"as of publication in 2023"*, *"about English-language benchmarks
only"*. A `context` claim with a vague scope is the one thing in this file that is
actually dangerous. Do not write superlatives you cannot bound — "the first",
"the definitive", "state of the art" — and do not characterise anyone else's work as
worse.

**3. `scope`, per claim** and required on every one of them: the conditions under
which the claim holds, and where it does not. This is **content, not a disclaimer**.
"Further research is needed" is worthless; "holds for models above 1B parameters;
the 125M model shows no effect" is scope. It is a separate, adjacent field because
summarisers drop scope far more often than they drop findings, which is the most
common way a paper ends up misrepresented.

**It is published after the literal words `Holds for:`** — in the page's claim list,
in each `FAQPage` answer, and in `llms.txt`. So write it to complete that sentence.
"Holds for: T5-base and T5-large, up to seven models" reads. "Holds for: This is a
description of the published algorithm, so it is as reliable as reading it" does not
parse, and 12% of drafted scopes open exactly like that — classifying the claim
instead of bounding it. **Never open `scope` by saying what kind of claim this is.**
If the reliability of a claim is worth saying, it is a clause at the end, after the
conditions; and for a `context` claim the honest bound *is* a condition — "as of
publication in 2023", "about English-language benchmarks only" — so say that
instead.

**4. Questions.** Each `qa` entry is **one question in 2–4 paraphrases**, answered
by a list of claim **ids**. The rule that is easy to get backwards:

| | Rule | Why |
|---|---|---|
| Questions | **paraphrase deliberately** | engines fan one query into many synthetic sub-queries; you cannot know which phrasing wins, so cover several |
| Claims | **never paraphrase** | a restated claim is a second, drifting copy of the author's own finding, and the two then compete for the same citation |

So `answers` holds ids and never prose. The renderer resolves each id to the claim's
sentence verbatim plus its scope, so a reader sees the question followed immediately
by the real answer — never a slug, never a paraphrase. **Never a question whose
answer is not adjacent.** Every claim should be reachable from some question; a claim
no question points at renders with no route to it.

**Every phrasing has to name its own subject.** A question is a *query*: it is
matched against what a stranger typed, and it is then published inside a `FAQPage`
where `Question.name` is extracted and shown with no page around it. "How much data
does it take to fit a model like this?" fails both times over — nobody types "a model
like this", so it matches nothing, and quoted alone it is unanswerable because
nothing on screen says what "this" was. Vagueness does not broaden reach here; it
removes the only words that could have matched. Write the subject in: *"how much data
does it take to fit a latent-skill model of arena outcomes?"* — longer, and the extra
words are the ones a query would contain.

So no phrasing may lean on **`this`/`these`/`those` with nothing before them**, on
**`this paper`/`this method`/`this approach`**, on **`the authors`**, on a trailing
**`here`**, or on **`it`/`they` as the opening subject**. A pronoun bound to a noun
inside the same question is fine and often the natural English — *"can I compare two
models by their skill profile"* names its subject. The rule is about references with
no antecedent on screen, not about pronouns.

Phrase questions in the vocabulary of someone who has **not** read the paper. A
question built around the paper's own coined name has no lexical path from what
people actually type, so **no question group may consist entirely of phrasings
containing the coined name** — at least one phrasing in each has to be answerable by
someone who has never heard it.

**At least one group must be a general question of the field**, answered by a
`context` claim: *"what is a good paper on X"*, *"what work established Y"*,
*"where should I start reading about Z"*. This is the entry-point class, it is the
one with real query volume, and it is the reason `context` claims exist.

**5. Misreadings** are stated as corrections, not as questions: what people wrongly
conclude, and what is actually true. Only include one the paper gives you a reason
to expect — a result that is easy to over-generalise, a negative result, a method
whose name promises more than it does. Do not invent a plausible misunderstanding.

**6. Terminology** is only for terms this paper coins or uses in a non-obvious
sense. Not a glossary of the field.

**7. `coined` and `gloss`,** only if the paper actually coins a name. `gloss` is the
plain-language phrase that goes adjacent to the name everywhere.
`TIES-Merging` has no lexical route from "how do I combine fine-tuned models"; the
gloss is that route.

**8. `one_liner`:** the one sentence the author will reuse verbatim in the page, the
README, the model card and the talk abstract. Under 320 characters, quotable,
specific. Identical reuse is the mechanism — rewording it in each place fragments
the corroboration that makes retrieval systems trust it.

**9. How much of each.** These are bands, not targets, and the reason is the same
one every time: each claim and each question group is a passage that competes with
its siblings on its own page, so a page of thirty is a page where nothing stands
out. Write fewer, better ones and stop.

| Field | Band | Why this band |
|---|---|---|
| `claims` | **5–15**, of which **≥1 `context`** and **more `result` than `context`** | a paper has a handful of real findings; twenty claims means one finding split five ways, which is paraphrasing under another name. The `result` majority is what keeps a page a record of work rather than a page about its own importance |
| claim `text` | **60–450 chars**, **≤2 sentences**, **≤32 words each**, **≤1** colon/semicolon/dash | one proposition, quotable verbatim. Aim near `one_liner`'s 320. The char band alone let a 79-word single sentence pass, which is why the sentence caps exist: each extra separator is where a second finding got bolted on instead of becoming its own claim |
| `scope` | **80–800 chars** | a condition list, and the longest field on purpose — it is the one summarisers drop, so brevity here buys nothing. The ceiling is where it stops being a list of conditions and becomes an essay that dilutes the claim it qualifies |
| `qa` | **4–20 groups**, ≥1 answered by a `context` claim | question groups are query surface, so the ceiling is loose: it exists to catch a run of invented questions, not to ration real ones |
| `q` per group | **2–4 phrasings** | |
| `misreadings` | **0–14**, each stated as a correction and never as a question | only ones the paper gives you a reason to expect |
| `terminology` | **0–13** | this paper's own terms, not a glossary of the field |

The three character ceilings are the 90th percentile of what the 324 already drafted
claims do, so they cut a tail and leave honest practice alone. The `claims`, `q` and
sentence limits are not: they are the anti-paraphrase and anti-overloading rules, and
most current drafts break them. Median first sentence today is 43 words against a cap
of 32; 99 of 324 claims stack two or more separators. That is the intended reading —
the fix is a period, not a wider band, because splitting one 43-word sentence into
two costs no content and is what makes the front of the passage safe to quote.

**Accuracy over coverage, everywhere.** Three claims you can point at a table for
are worth more than eight that read well. If the evidence you were given does not
support something, leave the field out rather than filling it. Never infer a result
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
  - q:
      - what should I read first about merging fine-tuned models?
      - which paper introduced sign conflicts as the reason merging fails?
    answers: [standing]

claims:
  - id: sign-conflict
    kind: result
    text: >
      Trimming low-magnitude parameter changes and resolving sign conflicts
      before averaging outperforms plain weight averaging across 11 tasks.
    scope: T5-base/large and ViT; up to 7 models; same architecture and init.
    evidence: Table 2
  - id: standing
    kind: context
    text: >
      TIES-Merging identified parameter-sign disagreement, rather than
      redundancy alone, as a cause of degradation when fine-tuned models are
      merged, and is a common starting point for work on training-free merging.
    scope: >
      About merging same-architecture models fine-tuned from one
      initialisation; says nothing about merging across architectures or about
      routing and mixture methods. As of publication in 2023.

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

Three tiers, and which tier a rule is in is itself a decision. **Schema** rules are
structural: a violation breaks something downstream, so it exits 1 and stops the run.
**Shape** rules are the bands in §2 §9 and the coverage rules: a violation is a
quality problem on a page that still renders, so `validate.py` reports it and exits 0
(`--strict` makes it fatal) — but `--accept` refuses, because accepting is the moment
the author asserts it in public. **Accept-time** rules run only at `--accept` and on
the review page, either because they need the paper's full text (a build artifact that
may be absent) or because they are about what to write next rather than about
retracting what is already published: `validate.py` reads `data/sidecars/*.md`, which
is the author's live words, so a readability finding there would make `--strict` demand
he retract a page over a long sentence. `--anyway` overrides the whole tier.

| | Rule | Tier | Enforced by |
|---|---|---|---|
| 1 | required: `one_liner`, `claims` | schema | `schema/sidecar.schema.json` |
| 2 | `one_liner` ≤ 320 chars | schema | schema |
| 3 | claim `id` matches `^[a-z0-9-]+$`, unique | schema / shape | schema pattern; `validate.py check_sidecars` for duplicates |
| 4 | every claim has `text` and `scope` | schema | schema |
| 5 | `kind` is `result` or `context` | schema | schema `enum`, default `result` when absent |
| 6 | a `result` claim has `evidence` | schema | schema `if/then`. A `context` claim does not need it — [§2](#2-the-rules) |
| 7 | no key outside the schema | schema | `additionalProperties: false` |
| 8 | `qa[].q` has 1–5 entries | schema | schema, plus `check_sidecars` for the empty case |
| 9 | every `answers` entry is an existing claim id | schema-tier | `validate.py check_sidecars` — a dangling id renders a question with no answer |
| 10 | the rules block in §2 exists and is non-trivial | schema-tier | `validate.py`, and `rules_block()` raises rather than sending an empty prompt |
| 11 | a draft can never reach a page | file layout | the site globs `data/sidecars/*.md`; drafts sit one level down |
| 12 | 5–15 claims, ≥1 `context`, and more `result` than `context` | shape | `validate.py check_sidecar_shape` |
| 13 | `text` 60–450 chars, `scope` 80–800 chars | shape | `check_sidecar_shape` |
| 14 | 4–20 `qa` groups, 2–4 phrasings each | shape | `check_sidecar_shape` |
| 15 | ≥1 `qa` group answered by a `context` claim | shape | `check_sidecar_shape` |
| 16 | every claim is pointed at by some `qa` entry | shape | `check_sidecar_shape` (was D3) |
| 17 | no `qa` group where every phrasing contains the coined name | shape | `check_sidecar_shape` |
| 18 | `coined` present ⇒ `gloss` present | shape | `check_sidecar_shape` (was D2) |
| 19 | ≤14 `misreadings`, ≤13 `terminology` entries, and no misreading phrased as a question | shape | `check_sidecar_shape` |
| 20 | **every number in a claim appears in the paper's own text** | accept-time | `validate.py check_claim_numbers` against `build/fulltext/<slug>.txt`, and `--accept` refuses. Skipped, loudly, when the text is not cached |
| 21 | claim `text` is ≤2 sentences of ≤32 words, with ≤1 colon/semicolon/dash | accept-time | `validate.py readability` — [§2 rule 2](#2-the-rules) |
| 22 | `scope` does not open by classifying the claim | accept-time | `readability` — it is published after "Holds for:", so it has to complete that sentence |
| 23 | no `qa` phrasing leans on a reference with no antecedent in it | accept-time | `readability` — bare `this`/`these`, `this paper`, `the authors`, trailing `here`, opening `it`/`they` |
| 24 | canonical key order | — | **nothing — open, D1** |

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

**Settled, and where the answer went.** Kept as a list rather than deleted, because a
decision with no record of having been made gets re-litigated.

| | Was | Decided |
|---|---|---|
| D2 | which optional keys become conditional requirements | `coined ⇒ gloss` and `result ⇒ evidence`. §4 rows 6 and 18 |
| D3 | a claim no question points at | a shape violation, not an error: the page renders, but the claim has no route to it. §4 row 16 |
| Q4 | may a question have an answer that is not a claim | no — promote it to a claim. Which is what `kind: context` is for: the answer to *"what should I read about X"* is a claim like any other, it just has nothing to cite |
| Q6 | which scenario classes the question set must cover | classes 1 and 2 are required (bottom lines, and one general question of the field answered by a `context` claim); 6 and 8 stay in `scope` and `terminology`; 5 and 7 are ruled out — 5 characterises someone else's work, 7 is the identity track. Cap comes from the 4–20 band |
| C1 | granularity of one claim | one finding, bounded by the 5–15 band. Splitting a finding to reach a count is paraphrasing, which is separately forbidden |
| C2 | `scope` shape | prose with an 80–800 band. A template was rejected: a paper whose scope is genuinely one clause would be padded to fit it |
| C3 | is `evidence` required | on `kind: result`, yes. On `kind: context`, no — and that asymmetry *is* the answer to "can we ship useful unverified claims" |
| A2 | minimum viable sidecar | 5 claims, from the band |
| C6 | how many `context` claims before a page reads as self-promotion | ≥1 required, and `result` must outnumber `context`. A page whose majority is unverifiable standing claims is an advert; the majority rule is the cheapest expression of that. §4 row 12 |

### Shape and enforcement

| | Decision | Options | If we do nothing |
|---|---|---|---|
| D1 | canonical key order | (a) fixed order, rewritten by a formatter; (b) fixed order, reported by the validator; (c) no rule | three orders, growing |
| D4 | formatter or validator | `validate.py --fix-counts` set the precedent that mechanical things get fixed rather than reported. Key order, list order, id casing and wrapping are all mechanical | hand-fixing, inconsistently |
| D5 | do the shape bands apply to a sidecar accepted before they existed | they are non-fatal by design, so old files report and keep working. But `--accept --replace` on a redraft *will* enforce them, so the first redraft of any paper is where the band bites | the corpus splits into pre-band and post-band files |

### The question list

| | Decision | Options | If we do nothing |
|---|---|---|---|
| Q1 | natural questions or search queries | *"Does merging models require retraining?"* vs *"ties merging retraining required"*. (a) natural only; (b) both in one array; (c) both, separate fields — and whether the answer differs between crawl-fed engines and what a model already knows | natural only, by drafter habit rather than by decision |
| Q2 | what varies between the 2–4 paraphrases | (a) no rule; (b) an axis rule — one lay phrasing, one field-jargon phrasing, one task-oriented phrasing. Three syntactic rewrites of one wording buy far less than three lexical routes | syntactic near-duplicates |
| Q3 | first person or not | 0%–67% across the corpus. Practitioner queries are first-person (*"should I use this"*), literature queries are not. (a) allow both; (b) require one of each; (c) third person only | whatever the model felt like |
| Q5 | field names | `q` vs `questions` vs `phrasings`; `answers` vs `answered_by` vs `claims`. `q` holds an array, so a singular-looking name is mildly wrong and `question` would be worse. Cosmetic once, permanent after: every co-author's file and every future tool reads it | `q` / `answers` |
| Q8 | how many general questions | one is required and the band caps the total, but a page could reasonably carry three entry-point questions out of eight. Is there a *minimum share*, not just a minimum count? | exactly one, by the letter of the rule |

**The scenario classes**, as decided in Q6. Kept because the rejections are the
useful half: two of these are things we could write and have chosen not to.

| # | Scenario | Query looks like | Where it goes |
|---|---|---|---|
| 1 | the paper's bottom lines | "does X help Y" | `qa` → `result` claims. **Required** |
| 2 | background / domain entry | "what is model merging", "what should I read about X" | `qa` → a `context` claim. **Required**, ≥1 group |
| 3 | method selection | "best way to merge fine-tuned models" | `qa`, if it can be scoped to this method |
| 4 | reproduction / practical | "how many samples does tinyBenchmarks need" | `qa`. Cheap and useful |
| 5 | comparison to a named alternative | "TIES vs task arithmetic" | **ruled out** — characterising someone else's work in our own claim |
| 6 | negative results and limits | "when does merging fail" | `scope`, not `qa`. It is the honest half of every claim rather than a question of its own |
| 7 | provenance / who | "who works on model merging" | **ruled out here** — that is the identity track, and it is answered by the author page, not a paper page |
| 8 | terminology | "what does interference mean in merging" | `terminology`. Not rendered as Q&A today, which is E4 below |

### The claims

| | Decision | Options | If we do nothing |
|---|---|---|---|
| C4 | are claim ids stable identifiers | if anything ever links `#no-retraining`, renaming breaks it. Either promise stability, or state that they are internal and unlinkable | undefined, so unsafe either way |
| C5 | should a `context` claim be marked as such on the page | today the absence of an evidence pointer is the only signal, which is subtle. (a) leave it — the reader infers from the missing "Table 2"; (b) label it; (c) a separate section. Labelling an unverified claim is more honest and also invites a reader to discount it | unmarked, distinguishable only by what is missing |

### Reach and lifecycle

Ownership is settled: one sidecar per paper, one owner, and a co-author who wants to
contribute claims PRs the owner's file rather than keeping their own
([RULES.md §12](RULES.md#12-co-authors)). What is open is everything downstream of
that.

| | Decision | Options | If we do nothing |
|---|---|---|---|
| A1 | is the author's slant separable | if two authors lead with different claims, is that an overlay on one shared claim set, or two files? | not expressible |
| A3 | a "no sidecar, ever" verdict | most papers have no draft and some never should — workshop reports, position pieces someone else led. Absence currently reads as "not done yet" | the worklist asks forever |
| E1 | `FAQPage` / `mainEntity` JSON-LD | absent today. [RULES.md §6](RULES.md#6-dont) warns against markup not backed by visible text — here it *is* backed, which is the exempt case. Blocked on Q2: `Question` takes one `name`, so one paraphrase has to be canonical | visible HTML only |
| E2 | publish the machine-readable sidecar | a `.yaml` or `.jsonld` beside each page would let co-authors consume claims verbatim instead of paraphrasing them, which is the mechanism [RULES.md §5](RULES.md#5-say-the-same-thing-the-same-way) depends on | they paraphrase |
| E3 | what a co-author's site emits for a paper it does not own | `rel=canonical` at the owner — but does it also carry the claim sentences (corroboration) or only the pointer (no duplicate content)? The two rules point opposite ways | unresolved in the docs too |
| F1 | review granularity | `--accept` is all-or-nothing over ~16 claims and ~14 question groups | the author reviews thirty items or none |
| F2 | re-drafting an accepted sidecar | `--replace` overwrites, and author edits are lost silently. Immutable, three-way merged, or diffed for review? | silent loss |
| F3 | what a collaborator's install needs | the propagation target: 30 papers, defensible sidecars, without reading this file. Schema + formatter + prompt + one worked example? And what keeps their files from drifting from ours — a shared spec, or a shared tooling version? | they fork and diverge |
| F4 | staleness | `supersedes` / `superseded_by` exist and nothing sets them; a preprint claim can be corrected in camera-ready | stale claims look current |
