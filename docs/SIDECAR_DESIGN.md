# The open design questions for the per-paper file

The sidecar is the only artifact in this repo whose content is a judgment rather
than a derivation. Everything else — links, ids, labels, pages — is re-derived
from public sources on every run, so it cannot drift. The sidecar can, and it
has: see the measurements below.

This file is the worklist for fixing that. It is **questions, not answers**, on
purpose. Each one gets decided once, written into
[PAPERS.md](PAPERS.md) as a rule and into
[`schema/sidecar.schema.json`](../schema/sidecar.schema.json) or
[`scripts/validate.py`](../scripts/validate.py) as an enforcement, and then never
re-litigated. A decision that lives only in a drafting prompt is a decision that
drifts on the next model, the next co-author, and the next paper.

The target is not "a good file for these 112 papers". It is a spec another
scientist can point a tool at and get a defensible file with no taste and no
effort. That constrains every answer below: **anything that requires the author
to have read this document is a design failure.**

---

## What we actually measured

Across all 19 drafts plus the one accepted sidecar:

| | min | median | max |
|---|---|---|---|
| claims per paper | 3 | 16.5 | 22 |
| question groups | 2 | 14 | 19 |
| phrasings per group | 2.7 | 3.1 | 3.6 |
| claim text length (chars) | 182 | 306 | 411 |
| **scope length (chars)** | **124** | **530** | **694** |
| misreadings | 3 | 10.5 | 16 |
| terminology entries | 2 | 9 | 13 |

Three findings worth separating, because they are not the same problem:

1. **Question style is already consistent.** 100% of questions in every draft are
   capitalized and end in `?`. The one file that looks different — TIES, all
   lowercase, 38% first-person — is the *accepted* sidecar, hand-written before
   the drafter existed. So "Q2 looks utterly different from TIES" is real, but
   the drafts agree with each other and disagree with the old hand-written file.
   Whatever we settle on, TIES needs regenerating to match.
2. **Key order is genuinely arbitrary.** Three different orders appear
   (`one_liner` first, `key` first, `coined` first) and optional keys come and go
   with no rule: `key` present in 8 of 20, `links_extra` in 12, `gloss` in 17.
   Nothing in the schema constrains order, and JSON Schema cannot.
3. **`scope` is 5× more variable than anything else** — 124 to 694 characters.
   The schema says scope is "conditions under which it holds and does not", which
   is a description of intent with no shape. This is the single largest drift in
   the corpus and the field where drift costs most, because scope is what stops a
   claim being quoted outside its conditions.

Also: `build_site.py` emits `ScholarlyArticle` JSON-LD but **no `FAQPage` /
`mainEntity`** for the Q&A block. The questions exist as visible HTML only.

---

## Section A — what the file is

**A1. One file per paper, or one per (paper × author)?**
[SHARED.md §10](SHARED.md#10-duplication-which-kind-helps-which-kind-hurts)
already answers the *page* half — never duplicate the page, share the source,
duplicate the pointer. It does not answer whether a co-author who runs this tool
should hold their own sidecar for a shared paper. Sub-questions: does a
second-author sidecar add corroboration (§5 says recurring claims are weighted
up) or fragmentation (two near-identical claim sentences)? If one owner, who —
first author, corresponding author, whoever ran the tool first? What does the
non-owner's install do: fetch the owner's sidecar, or hold a stub pointing at it?

**A2. Is the sidecar one artifact or two?**
It currently serves two masters: the source of truth for claims (author-facing,
version-controlled, quotable) and the input to a rendered page (machine-facing).
Should the per-author *slant* — which claims this author leads with, their own
framing — be a separate overlay file, leaving the claim set shared?

**A3. What is the smallest sidecar that is still worth publishing?**
3 claims (TIES, accepted) versus 22 (global-m). Is there a floor below which we
render nothing rather than a thin page? Is there a ceiling above which the page
stops being retrievable because every passage competes with 21 siblings?

**A4. Do we need a per-paper "no sidecar" verdict?**
93 of 112 papers have no draft. Some never will — workshop reports, position
pieces someone else led. Right now their absence is indistinguishable from
"not done yet", which is exactly the problem `declines.yaml` exists to solve for
tasks.

## Section B — the question list itself

**B1. Natural questions or search queries?**
His question. These are different objects: *"Does merging models require
retraining?"* versus *"ties merging retraining required"*. Which one do retrieval
pipelines actually match, and does the answer differ between P1 (crawl/web) and
P3 (weights)? If the answer is "both", do they live in the same array or in two?

**B2. How many phrasings per question, and paraphrased along which axis?**
Schema says 2–4, drafts average 3.1. But *what* varies between the three
phrasings is undefined — vocabulary, syntax, specificity, or persona. Three
syntactic rewrites of one wording buy less than three genuinely different lexical
routes. Is there a rule ("one lay phrasing, one field-jargon phrasing, one
task-oriented phrasing") or is it taste?

**B3. First person or not?**
0% to 67% across the corpus. *"Should I use this for my merge?"* versus *"When is
this method appropriate?"* Practitioner queries are first-person; literature
queries are not. Both audiences exist.

**B4. Do we need `answers` at all after the question?**
His question. Two things are tangled in it:
 - *Adjacency*: the schema's own rationale is that a question without its answer
   adjacent matches the query and then loses the citation. That argues the
   rendered page must keep them together — and it does.
 - *Representation*: the file stores answers as **claim ids**, and the renderer
   resolves each id to the claim's verbatim text plus its scope, so no reader
   ever sees a slug. The ids exist to make paraphrasing a claim structurally
   impossible (§5). The open question is whether a question can ever have an
   answer that is *not* an existing claim, and if so whether that answer should
   be promoted to a claim or allowed as prose.

**B5. `q` or `question` or `questions`?**
His question. The field holds an array of paraphrases, so `q` is short but
singular-looking, and `question` would be worse (a plural value under a singular
key). Candidates: `q`, `questions`, `asks`, `phrasings`. This is cosmetic *once*
and permanent after: every co-author's file and every future tool reads it.
Related: is `answers` the right name if the value is claim ids — `claims`,
`answered_by`, `cites`?

**B6. What is the coverage rule for the question set?**
His question, and the substantial one. Candidate scenario classes, to accept,
reject or extend:

| # | Scenario | Query looks like | Currently covered? |
|---|---|---|---|
| 1 | The paper's bottom lines | "does X help Y" | yes, this is most of every draft |
| 2 | Background / domain entry | "what is model merging" | rarely — and it is the highest-volume class |
| 3 | Method selection | "best way to merge fine-tuned models" | sometimes |
| 4 | Reproduction / practical | "how many samples do I need for tinyBenchmarks" | sometimes |
| 5 | Comparison to a named alternative | "TIES vs task arithmetic" | rarely, and it names someone else's work |
| 6 | Negative / limits | "when does merging fail" | this is what `scope` holds, not `qa` |
| 7 | Provenance / who | "who works on model merging" | not at all — this is the identity half |
| 8 | Terminology | "what does interference mean in merging" | `terminology` holds it, unrendered as Q&A |

Sub-questions: which classes are worth the tokens? Which are *ours* to answer at
all — class 2 invites writing a survey we did not write, class 5 invites
characterizing others' work. Is there a required minimum per class, or a cap per
class to stop 19 bottom-line questions crowding out the one background question
that gets 100× the query volume?

**B7. When does this work, and what is the honest expected effect?**
[MEASURE.md](MEASURE.md) already separates "was it done" from "did it work". Q&A
blocks are a P1 lever with days-to-weeks latency and no P3 path. Before we spend
112 papers' worth of author attention: what is the measurable prediction, and
what would falsify it? Related: [SHARED.md §3](SHARED.md#3-retrievability-write-for-the-chunk-not-the-page)
says the 252k-trial study found *formatting* null and deprioritized it — we need
to be sure the Q&A block is content and not formatting wearing content's name.

## Section C — the claims

**C1. What is a claim, exactly, and what is the granularity rule?**
3 to 22 per paper is a factor of 7. Is a claim one experimental result, one
takeaway, or one sentence someone might quote? Does a claim that only exists to
be an `answers` target belong in the file?

**C2. What shape is `scope`?** The 124–694 char spread is the worst drift we
have. Options: free prose with a length cap; a fixed template (*holds for … ;
untested for … ; fails when …*); structured subfields. Which of these survives
contact with a paper whose scope is genuinely one clause?

**C3. Is `evidence` required?** Optional today. "Table 2" is cheap to write, is
the strongest anti-hallucination signal on the page, and is the thing a skeptical
reader checks first.

**C4. Are claim ids stable identifiers or incidental?** If someone cites
`#no-retraining` or we ever emit per-claim anchors, renaming a claim breaks a
link. Do we promise stability, and if so what happens when a claim is corrected?

**C5. Where does a claim's canonical sentence live if it must be identical across
paper, README, model card and talk?** §5 demands verbatim reuse. Nothing today
generates the README snippet from the sidecar, so identity is maintained by hand
— which is to say, not maintained.

## Section D — shape, order, enforcement

**D1. Canonical key order, and is it enforced or merely documented?**
JSON Schema cannot express order. So either `validate.py` checks it, or a
formatter rewrites it, or it drifts. Which?

**D2. Which optional keys become required?** `gloss` is already conditionally
mandatory in prose (§4: every coined name gets a gloss) but optional in schema —
that condition is machine-checkable. `key`, `terminology`, `misreadings`,
`links_extra` all vary with no rule.

**D3. Do we need a formatter (`--fmt`) rather than a validator?**
`validate.py --fix-counts` set the precedent: for anything mechanical, fix it
rather than report it. Key order, list ordering, wrapping, and id casing are all
mechanical.

**D4. What does the schema *not* catch that we care about?**
Counts, lengths, casing, question/claim ratio, orphan claims (no `qa` points at
them), dangling ids, duplicated claim text across papers. Which of these are
errors, which are warnings, and which are just reported?

**D5. Markdown-front-matter or YAML?** The file is `.md` with a YAML front matter
block and no body. Either the body should carry something (long-form prose the
page can use) or the file should be `.yaml` and stop pretending.

## Section E — what the page emits

**E1. `FAQPage` / `mainEntity` JSON-LD: yes or no?**
Absent today. [SHARED.md §6](SHARED.md#6-dont) warns that schema markup not
backed by visible page text is discounted and a spam signal — but here it *is*
backed by visible text, which is the case the warning exempts. Also `Question`
with multiple `name` values is not valid schema.org, so B2's paraphrases and this
question interact: which phrasing becomes the canonical `name`?

**E2. Should claims be individually addressable?** Per-claim `id` anchors,
`Claim`/`ClaimReview` types, or a quotable permalink per claim.

**E3. What does a co-author's site emit for a paper it does not own?**
`rel=canonical` at the owner's page, per §10. But does it emit the claim
sentences too (corroboration, §5) or only the pointer (no duplicate content)?
These two rules point in opposite directions and the conflict is unresolved.

**E4. Is the machine-readable form of the sidecar published?**
A `.jsonld` or `.yaml` next to each page would let co-authors and other tools
consume claims verbatim instead of paraphrasing them — which is exactly the
mechanism §5 depends on.

## Section F — how this stays true without effort

**F1. Where does the drafting rule actually live?**
Today: partly in `draft_sidecars.py`'s prompt, partly in the schema's
descriptions, partly in PAPERS.md. Three homes means three versions. Should the
prompt be *generated* from the schema plus a rules file, so there is one source?

**F2. What is the review affordance for the author?**
`--accept` today is all-or-nothing on a whole file with ~16 claims and ~14
question groups. Is per-claim accept needed, and if so what does the diff look
like on a re-draft?

**F3. What happens on a re-draft of an accepted sidecar?**
`--replace` overwrites. Author edits are lost silently. Does an accepted sidecar
become immutable, three-way merged, or diffed for review?

**F4. What does a collaborator's install of this need?**
The propagation target. A scientist with 30 papers should get defensible
sidecars without reading this file. What is the minimum: the schema, the
formatter, the prompt, and a worked example? And what stops their 30 files
drifting from ours — shared spec, or shared tooling version?

**F5. How do we know a sidecar has gone stale?**
A paper gets published, retitled, superseded. `supersedes` / `superseded_by`
exist but nothing sets them. A claim that was true at preprint time can be
corrected in camera-ready.

---

## Deferred, on purpose

**Repo labels.** 30 of 31 proposed repo descriptions and topic sets are
unreviewed. Deliberately parked until the papers are settled — the papers are the
higher-leverage half and the repo sweep is a bounded afternoon. `WORKLIST.md`
regenerates the section on every run, so it cannot be forgotten; this line
records that the silence is a choice.
