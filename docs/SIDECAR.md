# The sidecar

One file per paper, `data/sidecars/<slug>.md`. It is the only artifact in this repo
whose content is judgment rather than derivation — everything else is re-fetched
from public sources each run and therefore cannot drift. This one can, and has.

**§2 is the drafting prompt.** Not a description of it: `scripts/draft_sidecars.py`
reads the block between the markers and sends it to the model, so editing §2 changes
what the drafter is told in the same commit.

A model drafts, the author accepts ([../RUN.md](../RUN.md)). **§2–§4 are settled**,
enforced where the last column of §4 says so. **§6 is open** — each row is a decision
nobody has made, with the real options and what ships if we keep not deciding.

## How a draft is made

Six stages. The first two and the last three are code; the model does one of them,
and it is the only stage whose output is not reproducible from public sources.

| | What happens | Where |
|---|---|---|
| 1 | **Text is resolved.** arXiv HTML, ar5iv, or a hand-dropped PDF, cached and delined. No text, no draft — see §1 | `scripts/fulltext.py` |
| 2 | **Evidence is packed.** Metadata, then the paper's own numbering extracted — which sections, figures, tables and appendices exist, and every caption — then the full text. The numbering block exists so pointers are read rather than guessed, and the captions because the truncation cuts mid-paper ones | `evidence()`, `inventory()` in `scripts/draft_sidecars.py` |
| 3 | **A task file is written** carrying the system prompt (this file's §2, read live), the schema, and one task per paper with `sidecar: null` | `emit_tasks()` → `build/sidecar_tasks.json` |
| 4 | **The model fills `sidecar`.** The only judgment stage: claims, scope, questions, misreadings, terminology, one-liner. It writes nothing else, anywhere | the agent |
| 5 | **Drafts are ingested and checked.** Structural checks against the schema, then the quality tier — claim length, numbers traceable to the text, pointers that exist, questions that stand alone. Each draft is stamped with a hash of the rules that judged it, so a later rule change marks it stale rather than silently passing | `--ingest`, `validate_draft()`, `--restamp` |
| 6 | **The author reviews and accepts.** `--review` builds one page with every flag and every claim linked into the paper's own sentence; `--accept <slug>` promotes it out of `drafts/` and is the only step a human must perform | `build/sidecar_review.html` |

Between 5 and 6 nothing is published: the site, the validator, the fidelity check and
the coverage count all glob `data/sidecars/*.md` non-recursively and cannot see
`drafts/`.

---

## 1. Before drafting: is there anything to draft from?

`python scripts/fulltext.py --report` says which papers resolved to real text and
which are thin. Each task in `build/sidecar_tasks.json` carries the same answer on
the first line of its `evidence` field: the source it came from and whether the text
was truncated.

A paper with no available text gets **no draft at all** — a sidecar written from a
title and an abstract is a page of confident guesses published under an author's name.
Drop the paper's PDF into `data/fulltext/<slug>.pdf` (gitignored, checked first) and
re-run, or leave it in the thin list.

## 2. The rules

Nine steps, in the order the fields depend on each other. The index below gives what
each step is *for* and the one emphasis that dominates it — a way into the block, not a
second copy of it. The rules themselves are stated once, in the block; §4 says what
enforces each. A test asserts this table has a row per step, so a tenth step cannot be
added without appearing here.

| Step | Writes | The emphasis it is built around |
|---|---|---|
| 1 | *(nothing — reading)* | Every figure in the draft appears in the paper's own text. The one rule with no exceptions, because a wrong number is what a reader cannot detect and the author is publicly answerable for. Then: get them onto the page, at least half the `result` claims carrying one, written as numerals |
| 2 | `claims` | A claim asserts something a reader wanted to know; it does not describe a part of the paper. Applied as: if a stranger read only this sentence, what do they now know that they can use? Each claim stands alone, names its subject, carries one proposition, and leads with the whole thing |
| 3 | `scope` | Content, not a disclaimer — the condition that actually bounds the result. Shorter than the claim it bounds, because it is published after the literal words `Holds for:` and has to survive being quoted with it |
| 4 | `qa` | Every phrasing names its own subject, in the vocabulary of someone who has not read the paper. Paraphrase the question deliberately; never paraphrase the claim. One group must be a general question of the field |
| 5 | `misreadings` | A correction the paper gives you a reason to expect, never an invented one, and readable with nothing beside it |
| 6 | `terminology` | Define the term, not its role on this page — the definition is published alone as a `DefinedTerm` |
| 7 | `coined`, `gloss` | The gloss is the lexical route from what people type to a name they have never seen |
| 8 | `one_liner` | One sentence the author reuses verbatim in the page, the README, the model card and the talk. Identical reuse is the mechanism |
| 9 | *(how much of each)* | Bands, not targets: every claim and question group competes with its siblings on its own page, so write fewer, better ones and stop |

Above all of them, and the reason to leave a field out rather than fill it:
**accuracy over coverage** — the draft is read by the paper's own author, who will
verify every line.

<!-- prompt:start -->
What you produce is consumed two ways: rendered on the paper's canonical page, and
retrieved as isolated passages by retrieval-augmented systems. The second drives
every rule below.

Write the fields in this order. They depend on each other in this direction, and
writing the questions first produces questions whose answers you then have to
invent.

**1. Start from the paper's own numbers.** The evidence you were given opens with the
paper's numbering extracted for you — which sections, figures, tables and appendices
exist, and every figure and table caption, which is both where the magnitudes are and
the part the truncated full text may have cut. Read that block before writing a word,
and **cite only pointers it lists**: a claim whose `evidence` names a section the paper
does not have is rejected at accept time, and that has already happened once. Then hold
to one rule for the rest of the draft:
**every figure you write must appear in the paper's own text.** Not "a plausible
magnitude", not one inferred from a chart, not one carried over from a similar
paper. If you cannot find the number for a finding, the finding can still become a
claim — stated without a magnitude — but it never gets an invented one. This is the
only rule here with no exceptions, because a wrong number is the one error a reader
cannot detect and the author is publicly answerable for.

**And check it against the pointer you are about to cite, not merely against the
paper.** The accept-time check asks only whether the number appears somewhere in the
text, so a real magnitude filed under the wrong table passes it and is still wrong: one
redraft put a same-task-checkpoint result under "Table 3" when that experiment is
Figure 7, and nothing but reading caught it. Find the number inside the thing you name
in `evidence`.

**Then get those numbers onto the page: at least half of the `result` claims must
carry one.** A figure is the single strongest thing a claim can contain — it is what
makes a passage worth quoting rather than paraphrasing, and a paraphrase is a citation
lost. Across the drafts the median page manages 61% and the weakest 33%, which is a
page mostly asserting that something was demonstrated. Under half, the fix is to go
back to the tables for magnitudes the claims dropped, or to fold two number-free
claims into the one measured claim they are both circling. It is never to invent one —
see above — and a page whose paper genuinely reports few figures is allowed to say so
and stay under.

**Write a magnitude as a numeral, not a word.** "4 latent dimensions", not "four".
This is not a style preference: the check above and the one that verifies every figure
against the paper's own text both read numerals, so a magnitude spelled out is a
magnitude nothing can verify — and the paper's tables wrote it as a numeral anyway.

**2. Claims are the core**; everything else is scaffolding.

**A claim asserts something a reader wanted to know. It does not describe a part of the
paper.** This is the rule that decides whether the page is worth anything, and it is the
one the drafts break most often without breaking any other rule. The failing claims are
all true, all in the paper, and all answer a question nobody asked:

> *"Q² works in three steps: mark every named entity and noun phrase in the response as
> an informative span, generate a question for each…"*
> *"Examples are clustered into representative anchor points, and what ships is the
> fitted IRT item parameters rather than the vector of model correctness."*
> *"Each match is factorised into a multinomial logistic model over how the game ended
> and, conditional on that, a model of who won."*

Each is a method section compressed. Retrieved on its own it hands a summariser
machinery to paraphrase and nothing to quote, and it answers no query, because the
reader who would type its words has already read the paper.

The test, applied to every claim before it goes in: **if a stranger read only this
sentence, what do they now know that they can use?** "Examples are clustered into anchor
points" fails it — the reader knows a design detail and can do nothing with it. The
finding underneath it passes: *"100 examples per scenario estimate an unseen model's
full-benchmark score to within about 2%."* Same paper, same section, one is the
mechanism and the other is why anyone cares.

The mechanism is not wasted. It goes in the **second sentence** of the claim it explains,
where it is the *because* of a finding; or into `terminology`, which exists to define the
paper's own machinery; or it is dropped. What it may not be is the claim.

Two honest exceptions, and they are narrow. A mechanism is the claim when the mechanism
*is* the contribution and stating it is the finding — *"RLCR adds a Brier-score
calibration term to the correctness reward"* is what the paper did. And a `context`
claim's job is to say what the work *is*, so it names the contribution by design. Both
still have to say what the reader gets, not walk through how the thing is assembled.

**A claim never states what is true of the field.** The highest-volume queries are
topic-level — *"does merging fine-tuned models actually work"*, *"how few examples can
evaluate a model"* — and this paper is one contributor to the answer. Answering one as a
claim publishes a statement about other people's results under this author's name, with
the paper's own evidence unable to support it; and getting it wrong misattributes work to
the wrong group, which is the error a reader who knows the field spots immediately.

So a topic question is answered from this side of it only: say what **this** work
established, and refer to everything else generically and unnamed — *"one of several
approaches to X"*, *"alongside other work on X"*. Never a named alternative, a named
group, or a claim about what the field now believes. That is the line scenario class 5 is
already ruled out on: characterising someone else's work inside our own claim. The
`context` claim is where a general question lands, and its subject is the work, not the
area.

The `one_liner` is not one of the claims. Both are published -- the one-liner as the
page's description and every claim in its own list -- so a one-liner copied from a claim
makes the page state one sentence twice and spends a claim slot saying nothing new. Give
the one-liner the paper's point, usually the mechanism, and let the claims carry the
measurements.

Each claim:

- **is self-contained.** It will be retrieved alone, with no title and no
  surrounding paragraph, so it must name the object and the finding without
  depending on anything outside itself. No "we", no "this paper", no pronoun
  pointing outside the claim. **Name the thing, never "the paper".** 8% of drafted
  claims open with *"The paper proves…"*, *"The contribution is a frame as much as a
  method"*, *"The diagnosis behind the method:"* — which spends the quotable front on
  commentary and, extracted alone, says nothing about *which* paper. "KnOTS reframes
  LoRA merging as an alignment problem" is the same sentence with a subject. This
  holds for `context` claims too: a claim about what the work contributes still names
  the work.
- **never enumerates.** A claim whose text runs *"the key contributions are: (1) a
  method to align task updates, and (2) a new benchmark"* is two claims sharing one id,
  and each half is retrieved alone and answers its question badly. It is usually the
  abstract's contributions bullet pasted in. Split it, and give each half its own scope
  and evidence.
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

**Name what the number beats.** 37 of 343 claims say a method "outperforms other
methods" or "outperforms existing methods", which is a comparative with no comparator:
the reader cannot tell whether the 2.3% is over simple averaging or over the previous
best, so the claim is unquotable exactly where it is strongest. Write the baseline the
paper measured against -- "outperforms task arithmetic", "beats averaging, Fisher
merging and ensembling". This is not scenario class 5 in [§6](#the-question-list),
which stays ruled out: reporting the baseline a paper measured against is that paper's
own result, whereas characterising the baseline as bad work is ours to avoid.

**When a sweep is not clean, the exception is part of the claim.** A merged model that
wins on two of three tasks is not one that "outperforms other methods", and the honest
sentence is barely longer: *"beats averaging, Fisher merging and ensembling on all
three tasks, and beats task vectors on two of the three"*. Two claims in one redraft
were clean sweeps in the draft and had WNLI as the exception in the paper -- the same
exception both times, which is what an overstated sweep looks like when the model is
generalising from a table's bottom row. Stating the exception in the claim also keeps
it out of `scope`, where it would read as a caveat rather than as the result.

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

**Once it passes 160 characters it must be shorter than the claim it bounds, and it is
at most three sentences either way.** The floor is there because the two rules meet the
80-character band floor and, on a short claim, leave a target a few characters wide that
nothing can hit; below 160 the whole published answer is two short sentences and no part
of it is drowning the other. This is the
rule current drafts break hardest: the published answer in a `FAQPage` is literally
the claim, then the words "Holds for:", then the whole scope — and 290 of 325 scopes
are longer than the claim they qualify, at a median of 1.5×, up to one that is 14
sentences and 1368 characters against a 348-character claim. So the median published
answer is mostly caveat, which fails in both directions at once: an extractive
summariser quotes the front and cuts, so the part you wrote to protect the claim is
the part that gets dropped, while the embedding of the whole answer is dragged toward
hedging vocabulary and away from the finding. Scope earns its place by being short
enough to survive being quoted with the claim.

If more than three conditions are genuinely load-bearing, **the claim is too broad —
narrow the claim.** That is the move, and it is not a loss of honesty: a claim stated
about what it actually covers needs fewer caveats than one stated broadly and then
walked back. Two things also do not belong here and account for much of the length: a
restatement of the finding, and anything a reader could only misread *if* they read
past the page — that second one is `misreadings`, which exists for it.
The restatement has one recurring shape, so it is worth naming: **a trailing
participle commenting on the result** — "merging 2 to 11 tasks, showing consistent
performance improvements", "on eight vision tasks, demonstrating significant gains".
The first half is the condition and the second half is the claim again, so the clause
is deleted rather than rewritten. Whether the result is good is the claim's job; scope
says under what conditions it is. For the same reason, **do not open a `result` claim's
scope with "the analysis of…" or "the experiment on…"**: that names where the result came
from, which is `evidence`'s field, and it bounds the claim by nothing. The bound is the
sweep — which models, which datasets, which values of the hyperparameter.
The bound also includes **what the method was allowed to use**, whenever the paper's
setup grants it something. A merging result obtained with a validation set available to
tune the trimming threshold is a different claim from one obtained with no held-out
data, and that condition is the thing a practitioner reading the page most needs and
most often does not get. A validation set, a shared pre-trained initialization, a
coefficient tuned per task: if the paper states an enabling condition, it belongs in
`scope` beside the models and the datasets.

**It is published after the literal words `Holds for:`** — in the page's claim list,
in each `FAQPage` answer, and in `llms.txt`. So write it to complete that sentence,
and **do not write those two words yourself**: the page adds them, so a scope opening
"Holds for" or "Applies to" publishes them twice. Start at the condition.
"Holds for: T5-base and T5-large, up to seven models" reads. "Holds for: This is a
description of the published algorithm, so it is as reliable as reading it" does not
parse, and 12% of drafted scopes open exactly like that — classifying the claim
instead of bounding it. **No sentence of `scope` may say what kind of claim this is** —
not the first, and not a later one, which is where another 27 of them hide.
If the reliability of a claim is worth saying, it is a clause at the end, after the
conditions; and for a `context` claim the honest bound *is* a condition — "as of
publication in 2023", "about English-language benchmarks only" — so say that
instead.

**4. Questions.** Each `qa` entry is **one question asked by four different kinds of
person**, answered by a list of claim **ids** in `answered_by`. It is a form, and you
fill it:

```yaml
- ask:
    plain: how much data does it take to fit a latent-skill model of arena outcomes?
    jargon: what sample size does an IRT ability estimate over pairwise arena data need?
    task: how do I estimate model skill from arena votes without collecting new battles?
    practitioner: can I reuse existing arena votes instead of running my own evaluation?
  answered_by: [sample-size]
```

`plain` is required. Fill **at least one other**, and fill all four when all four are
real questions. The roles are not four wordings of one sentence — each is a different
**vocabulary**, because that is the only kind of variation that buys anything:

| role | who types it |
|---|---|
| `plain` | someone who has not read the paper, in their own words: no jargon, no coined name |
| `jargon` | a specialist, in the field's own terms |
| `task` | the same question asked in terms of what they are trying to do — *"how do I merge two adapters without retraining?"*. Asked, never described: *"I am trying to merge two adapters without retraining."* is a sentence about a person, and no one types it into anything |
| `practitioner` | someone deciding, in the first person — *"should I use this for my model"*. The highest-intent phrasing, and the one a person asks an assistant |

Engines fan one query into many synthetic sub-queries and you cannot know which
phrasing wins, so cover several routes. Three lexical routes reach three query
populations; three rewordings of one sentence reach one. What is *never* paraphrased is
a claim: a restated claim is a second, drifting copy of the author's own finding, and
the two then compete for the same citation.

**Every role is a natural question, ending in `?`.** Setting the scene first is fine, and is often what a real person types — *"I have ten fine-tuning runs of one task, should I merge them or ensemble them?"* — but a role that ends in a period is a statement of what someone is doing, not a query anyone issues. Never a keyword string
(*"ties merging retraining required"*): the phrasing is published as visible page text
and as a `Question.name`, both of which are read, and a keyword string in either place
is the pattern search engines have penalised for twenty years.

**Never emit `unsorted`.** It holds phrasings written before the roles existed, and it
exists only so migrating 1263 groups did not require guessing which route each one took.
A redraft empties it.

So `answered_by` holds ids and never prose. The renderer resolves each id to the claim's
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

The same failure one step subtler, and the one that survives every rule above: **a bare
`the` plus a role noun.** *"Is there a guarantee that the estimator is correct?"* has no
demonstrative and no pronoun and is still not a question anyone will ask, because *which*
estimator is the entire question. So is *"how are the model parameters estimated?"*, and
*"does the method use pseudo-labels?"*. What fixes them is a qualifier or a name, and it
is the same word a stranger would have typed: *"is the tinyBenchmarks IRT correction
proved consistent?"*, *"how are IRT item difficulty and discrimination estimated from
model correctness?"*. Naming something anywhere in the question is enough — *"does the
anchor-point method apply to prompt selection?"* is specific, and *"the models I merge"*
is bound by its own relative clause. Bare `the estimator`, `the method`, `the framework`,
`the dataset`, `the authors`, `the paper` are the forms to avoid.

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
Each one renders as its own bullet and is extracted as one, so **a misreading may not
say "here" or "we"** — 15% of drafted ones do, and a correction that opens *"Low
agreement here is not weak annotation"* corrects nothing once "here" is gone.

**6. Terminology** is only for terms this paper coins or uses in a non-obvious
sense. Not a glossary of the field.

Each entry is published as a schema.org `DefinedTerm` inside a `DefinedTermSet`, which
means the definition travels **alone**, with nothing but the term beside it — so it
gets the same self-containment rule as a claim, and 30% of drafted definitions break
it. *"The metric for every merging table here"*, *"used here on the residual stream"*,
*"This paper's shorthand for ordinary finetuning"* — as an extracted definition each
of those points at a page that is not there. Define the term, not its role on this
page: *"the merged model's accuracy on a task divided by the accuracy of that task's
own finetuned model"* is the same fact with nothing dangling. The attribution is not
lost by dropping the deixis; the enclosing set is already named "Terminology in
&lt;paper title&gt;".

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
| `scope` | **40–800 chars** | a condition list, and usually the longest field — it is the one summarisers drop, so brevity here buys nothing. The ceiling is where it stops being a list of conditions and becomes an essay that dilutes the claim it qualifies. The floor was 80 and is 40 because rule 31 made it wrong: strip the trailing "…, demonstrating robust performance" that 18 scopes carried and what is left — "Llama3-8B models finetuned with LoRA on NLI tasks" — is a real condition of 50 chars, so the two rules together were demanding the padding back |
| `qa` | **4–20 groups**, ≥1 answered by a `context` claim | question groups are query surface, so the ceiling is loose: it exists to catch a run of invented questions, not to ration real ones |
| `ask` per group | **`plain` plus ≥1 other role**, all four when all four are real | the roles are a closed set, so four is the ceiling by construction. The old band was a count of 2–4 phrasings, which three rewordings of one sentence satisfied — the routes are the thing being asked for, so they are what is counted |
| `misreadings` | **0–14**, each stated as a correction and never as a question | only ones the paper gives you a reason to expect |
| `terminology` | **0–13** | this paper's own terms, not a glossary of the field |

The three character ceilings are the 90th percentile of what the 324 already drafted
claims do, so they cut a tail and leave honest practice alone. The `claims`, `ask` and
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
"Notes from the author" — a sentence in the author's own voice, which is why this is a
`.md` file rather than a `.yaml`. It is escaped, not parsed as markdown: blank lines
split paragraphs and nothing else is interpreted. The drafter never writes it.

```yaml
---
key: yadav2023ties
coined: TIES-Merging
gloss: merging fine-tuned models by trimming, electing signs, and averaging
one_liner: >
  TIES-Merging combines independently fine-tuned models into one by resolving
  parameter-sign conflicts, outperforming task arithmetic across 11 tasks.

qa:
  - ask:
      plain: why does averaging fine-tuned weights hurt performance?
      jargon: what causes degradation when task vectors are added?
      task: how do I combine multiple fine-tuned models without retraining?
      practitioner: should I just average my fine-tuned checkpoints?
    answered_by: [sign-conflict]
  - ask:
      plain: what should I read first about merging fine-tuned models?
      jargon: which paper introduced sign conflicts as the reason merging fails?
    answered_by: [standing]

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

Everything above as a validator takes it. The last column is part of the rule.

Three tiers. **Schema** rules are structural: a violation breaks something downstream,
so it exits 1 and stops the run. **Shape** rules are the bands in §2 §9 and the
coverage rules: a violation is a quality problem on a page that still renders, so
`validate.py` reports it and exits 0 (`--strict` makes it fatal) — but `--accept`
refuses, because accepting is the moment the author asserts it in public.
**Accept-time** rules run only at `--accept` and on the review page, either because
they need the paper's full text (a build artifact that may be absent) or because they
are about what to write next rather than about retracting what is already published —
`validate.py` reads the author's live words in `data/sidecars/*.md`, so a readability
finding there would make `--strict` demand a page be retracted over a long sentence.
`--anyway` overrides the whole tier.

| | Rule | Tier | Enforced by |
|---|---|---|---|
| 1 | required: `one_liner`, `claims` | schema | `schema/sidecar.schema.json` |
| 2 | `one_liner` ≤ 320 chars | schema | schema |
| 3 | claim `id` matches `^[a-z0-9-]+$`, unique | schema / shape | schema pattern; `validate.py check_sidecars` for duplicates |
| 4 | every claim has `text` and `scope` | schema | schema |
| 5 | `kind` is `result` or `context` | schema | schema `enum`, default `result` when absent |
| 6 | a `result` claim has `evidence` | schema | schema `if/then`. A `context` claim does not need it — [§2](#2-the-rules) |
| 7 | no key outside the schema | schema | `additionalProperties: false` |
| 8 | `qa[].ask` holds only the four roles (plus legacy `unsorted`) | schema | `additionalProperties: false` on `ask`, plus `check_sidecars` for the empty case |
| 9 | every `answered_by` entry is an existing claim id | schema-tier | `validate.py check_sidecars` — a dangling id renders a question with no answer |
| 10 | the rules block in §2 exists and is non-trivial | schema-tier | `validate.py`, and `rules_block()` raises rather than sending an empty prompt |
| 11 | a draft can never reach a page | file layout | the site globs `data/sidecars/*.md`; drafts sit one level down |
| 12 | 5–15 claims, ≥1 `context`, and more `result` than `context` | shape | `validate.py check_sidecar_shape` |
| 13 | `text` 60–450 chars, `scope` 40–800 chars | shape | `check_sidecar_shape` |
| 14 | 4–20 `qa` groups; each fills `plain` plus ≥1 other role, and every role ends in `?` | shape | `check_sidecar_shape`. A group still holding `unsorted` is exempt — it predates the roles, and a redraft is what fills them |
| 15 | ≥1 `qa` group answered by a `context` claim | shape | `check_sidecar_shape` |
| 16 | every claim is pointed at by some `qa` entry | shape | `check_sidecar_shape` (was D3) |
| 17 | no `qa` group where every phrasing contains the coined name | shape | `check_sidecar_shape` |
| 18 | `coined` present ⇒ `gloss` present | shape | `check_sidecar_shape` (was D2) |
| 19 | ≤14 `misreadings`, ≤13 `terminology` entries, and no misreading phrased as a question | shape | `check_sidecar_shape` |
| 20 | **every number in a claim appears in the paper's own text** | accept-time | `validate.py check_claim_numbers` against `build/fulltext/<slug>.txt`, and `--accept` refuses. Skipped, loudly, when the text is not cached |
| 21 | claim `text` is ≤2 sentences of ≤32 words, with ≤1 colon/semicolon/dash | accept-time | `validate.py readability` — [§2 rule 2](#2-the-rules) |
| 22 | no sentence of `scope` classifies the claim | accept-time | `readability` — it is published after "Holds for:", so every sentence has to complete that phrase |
| 23 | no `qa` phrasing leans on a reference with no antecedent in it | accept-time | `readability` — bare `this`/`these`, `this paper`, `the authors`, trailing `here`, opening `it`/`they` |
| 24 | `scope` is ≤3 sentences, and no longer than its own claim once it passes 160 chars | accept-time | `readability` — the `FAQPage` answer is claim + "Holds for:" + scope, so a long scope makes the published answer mostly caveat. The 160 floor keeps the rule off the case it was never about, where it collides with the 80-char band floor and leaves nothing a scope can be |
| 25 | claim `text` does not open with "the paper"/"the contribution" | accept-time | `readability` — [§2 rule 2](#2-the-rules)'s self-containment bullet, which until now nothing enforced |
| 26 | no `terminology` definition and no misreading says "here"/"we"/"this paper" | accept-time | `readability` — a `DefinedTerm` travels alone, so a definition of its role on the page defines nothing |
| 27 | ≥half of a page's `result` claims carry a number | accept-time | `readability`, page-level — [§2 rule 1](#2-the-rules). Never satisfied by inventing one; rule 20 would catch that |
| 28 | **every section, figure and table a claim's `evidence` cites exists in the paper** | accept-time | `validate.py check_claim_evidence` against the cached text, and `--accept` refuses. Only existence, never support: no check here can tell whether Figure 4 shows what the claim says it shows |
| 29 | no `qa` phrasing leans on a bare `the` + role noun | accept-time | `readability` — rule 23's subtler form. Yields to any question that names something, so a qualifier or a name is the fix |
| 30 | a `result` claim does not describe construction without asserting a finding | accept-time | `readability`, partial by construction — a small allowlist of frames ("works by", "consists of", "is clustered"), suppressed when the claim also does a claim's job. Prose [§2 rule 2](#2-the-rules) carries the rest, because whether a sentence says something a reader wanted is not a regex |
| 31 | no clause of `scope` comments on what the result shows | accept-time | `readability` — [§2 rule 3](#2-the-rules) has always said a restatement of the finding does not belong in `scope`; this is the shape it takes, a trailing participial comment ("merging 2 to 11 tasks, showing consistent performance improvements") that bounds the claim in its first half and asserts it again in the second. 18 of 344 scopes, all from one model. Reporting verbs in the -ing form only, because the same verbs in a finite or past form are real conditions |
| 32 | a `result` claim's `scope` does not open by naming the analysis it came from | accept-time | `readability` — "the analysis of sign conflicts and their impact on merging" is falsifiable by nothing, and where a result lives in the paper is what `evidence` is for. 5 of 344 scopes. `context` claims are exempt: they have no measurement to state conditions on, and §2 names the publication date as their bound |
| 33 | a claim's `text` does not enumerate `(1) ... (2)` | accept-time | `readability` — two claims sharing one id, and the sentence-count rule misses it because the enumeration is one sentence. 1 of 343 claims, and it was the abstract's contributions bullet pasted in. Checked because the check is two lines and a numbered list is never the shortest way to say one thing |
| 34 | `one_liner` is not a claim restated | accept-time | `readability`, page-level — both are published, so the page said one sentence twice and spent a claim slot on it. 1 of 343, at ratio 1.00; the threshold is 0.9 on content words because sharing a subject and verb with a claim is expected and only near-identity is the defect |
| 35 | canonical key order | — | **nothing, by decision — see D1** |

## 5. What the drift actually looks like

Measured across the 19 drafts plus the one accepted sidecar.

| | min | median | max |
|---|---|---|---|
| claims per paper | 3 | 16.5 | 22 |
| question groups | 2 | 14 | 19 |
| phrasings per group | 2.7 | 3.1 | 3.6 |
| of which first person | 0% | 8% | 67% |
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

### Measured and left to prose

Each of these looks like an obvious check and is not. The count is here so it does
not get re-proposed.

| Class | Measured | Why no check |
|---|---|---|
| unnamed comparator — "outperforms other methods" | 37 of 343 claims | The phrase is a real sentence when what follows it *is* the paper's baseline set. Telling those apart needs the paper |
| circular `scope` — the claim's own subject as its condition | 19 of 343 | Mostly "ViT-B/32 models", a genuine bound that happens to repeat the claim's noun. No regex separates those |
| a magnitude filed under the wrong pointer | 1 of 343, found by hand | Needs the number located inside the specific figure. The cached full text does not preserve which table a number sat in |
| `qa` phrasings that are only syntactic rewrites | 0 of 308 groups by any measure a regex has | Still semantic, and this row is why Q2 was answered with structure instead of a check: nothing caught the rewrites, so the fix was to ask for named routes rather than to grade a list |
| near-duplicate claim `text` by character similarity | fires only on claims that should exist | Two claims measuring the same thing on ViT-B/32 and on ViT-L/14 score 0.8 similar and both belong |
| entity-first claim `text` | 39 of 343 open with a subordinate or prepositional clause | Proposed as a rule and refuted by the measurement: those 39 are the strongest claims in the corpus, and a uniform "X outperforms Y" opener is the weaker pattern, not the better one |
| two claims asserting one finding in different words | — | Semantic, so it stays agent or human judgement; §2's one-proposition rule is the guidance |

## 6. The open decisions

Each row is answerable as it stands. "If we do nothing" is what ships otherwise.
Tracked in [../BACKLOG.md](../BACKLOG.md).

**Settled, and where the answer went.**

| | Was | Decided |
|---|---|---|
| D2 | which optional keys become conditional requirements | `coined ⇒ gloss` and `result ⇒ evidence`. §4 rows 6 and 18 |
| D3 | a claim no question points at | a shape violation, not an error: the page renders, but the claim has no route to it. §4 row 16 |
| Q4 | may a question have an answer that is not a claim | no — promote it to a claim. Which is what `kind: context` is for: the answer to *"what should I read about X"* is a claim like any other, it just has nothing to cite |
| Q6 | which scenario classes the question set must cover | classes 1 and 2 are required (bottom lines, and one general question of the field answered by a `context` claim); 6 and 8 stay in `scope` and `terminology`; 5 and 7 are ruled out — 5 characterises someone else's work, 7 is the identity track. Cap comes from the 4–20 band |
| C1 | granularity of one claim | one finding, bounded by the 5–15 band. Splitting a finding to reach a count is paraphrasing, which is separately forbidden |
| C2 | `scope` shape | prose with a 40–800 band. A template was rejected: a paper whose scope is genuinely one clause would be padded to fit it — and the floor was lowered from 80 for the same reason, once rule 31 stopped the padding that was hiding it |
| C3 | is `evidence` required | on `kind: result`, yes. On `kind: context`, no — and that asymmetry *is* the answer to "can we ship useful unverified claims" |
| A2 | minimum viable sidecar | 5 claims, from the band |
| C7 | where a topic-level claim lives | nowhere new. A claim about the state of a field is not one this paper supports, and both candidate homes — a `kind: topic` claim, and per-line-of-work topic pages — needed a defensible account of who else established it, which is a literature review with no gate behind it. The general question stays a `context` claim about *this* work, with others referred to generically and unnamed. §2, and the same line as scenario class 5 |
| D1, D4 | canonical key order, and a formatter for it | **no rule, and no formatter.** Key order, list order and id casing are invisible past the parser: the published page and its JSON-LD are generated from the parsed values, so no ordering of the source file reaches a crawler or a model. The whole cost is noisier `git diff`s on files that change rarely, and the whole benefit would be quieter ones — which does not pay for a tool that rewrites 113 accepted files, each one an assertion published under the author's name. `--fix-counts` is not the precedent it looked like: a stale count in a doc is *wrong*, and a key in an unusual order is not |
| E1 | `FAQPage` / `mainEntity` JSON-LD | **shipped** — `build_site.faq_jsonld`, one `Question` per group, the claim text plus its scope as the accepted answer. It was blocked on which paraphrase is canonical, and the `ask` roles answer it: `plain` is required and leads, so it is the `Question.name` and the other routes are `alternateName` |
| C6 | how many `context` claims before a page reads as self-promotion | ≥1 required, and `result` must outnumber `context`. A page whose majority is unverifiable standing claims is an advert; the majority rule is the cheapest expression of that. §4 row 12 |

### Shape and enforcement

| | Decision | Options | If we do nothing |
|---|---|---|---|
| D5 | do the shape bands apply to a sidecar accepted before they existed | they are non-fatal by design, so old files report and keep working. But `--accept --replace` on a redraft *will* enforce them, so the first redraft of any paper is where the band bites | the corpus splits into pre-band and post-band files |

### The question list

All five closed together, because four of them were the same decision: a rule that
*names what to cover* and then leaves the drafter to decide whether it did. `q: [a, b, c]`
with "2–4 paraphrases, vary them deliberately" produced 3692 phrasings that are 90% third
person and mostly syntactic rewrites of one wording — every one of them satisfying the
letter of the rule. So the group became a form with named roles ([§2 rule 4](#2-the-rules)),
and each rule below is now a field that is either filled or visibly empty.

| | Was | Decided |
|---|---|---|
| Q1 | natural questions or keyword search queries | **natural only, and enforced**: every role has to end in `?`. Not a preference — a phrasing is published twice, as visible page text and as a `Question.name`, and a keyword string is what search engines have penalised for twenty years in the first position and unreadable in the second. Nothing was gained by the second field either: the engines this project targets match on meaning, not on term overlap |
| Q2 | what varies between the 2–4 paraphrases | **the axis rule, as structure**: `plain` / `jargon` / `task` / `practitioner`, each a different vocabulary rather than a different word order. `plain` plus one other is the floor; four is the ceiling by construction |
| Q3 | first person or not | **required as a role**, not as a share of a list. `practitioner` is the first-person route and it is one of the four fields; 299 of the corpus's existing first-person phrasings migrated straight into it |
| Q5 | field names | **`ask` / `answered_by`**, and `q` / `answers` are gone. Asked as "what would we pick with no technical debt" the answer is not close: `ask` holds a mapping of roles and `answered_by` holds claim ids, and both say what they hold. The debt was one mechanical rewrite of 113 files, done in the same commit as the roles |
| Q8 | a minimum *share* of general questions | **no share rule.** ≥1 group answered by a `context` claim stays the requirement (rule 15). A share would be a quota on a number the paper decides: a paper with four findings and eight groups does not owe the field three entry points, and the only way to meet a quota on a page that has one honest general question is to invent the other two — which is the padding failure C2 and rule 31 already exist to stop |

**The scenario classes**, as decided in Q6. Two of them are things we could write and
have chosen not to.

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
| E2 | publish the machine-readable sidecar | a `.yaml` or `.jsonld` beside each page would let co-authors consume claims verbatim instead of paraphrasing them, which is the mechanism [RULES.md §5](RULES.md#5-say-the-same-thing-the-same-way) depends on | they paraphrase |
| E3 | what a co-author's site emits for a paper it does not own | `rel=canonical` at the owner — but does it also carry the claim sentences (corroboration) or only the pointer (no duplicate content)? The two rules point opposite ways | unresolved in the docs too |
| F1 | review granularity | `--accept` is all-or-nothing over ~16 claims and ~14 question groups | the author reviews thirty items or none |
| F2 | re-drafting an accepted sidecar | `--replace` overwrites, and author edits are lost silently. Immutable, three-way merged, or diffed for review? | silent loss |
| F3 | what a collaborator's install needs | the propagation target: 30 papers, defensible sidecars, without reading this file. Schema + formatter + prompt + one worked example? And what keeps their files from drifting from ours — a shared spec, or a shared tooling version? | they fork and diverge |
| F4 | staleness | `supersedes` / `superseded_by` exist and nothing sets them; a preprint claim can be corrected in camera-ready | stale claims look current |
