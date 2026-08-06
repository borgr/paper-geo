# Rules that apply to everything

The parts that don't depend on whether the thing is a paper or a repository.
Track-specific rules: [PAPERS.md](PAPERS.md) · [REPOS.md](REPOS.md).
Evidence and mechanism behind all of it: [../STUDY.md](../STUDY.md).

---

## 1. Which pipeline are you optimizing?

Every action below belongs to exactly one. Naming it prevents most wasted work.

| | Pipeline | Entry condition | Latency |
|---|---|---|---|
| **P1** | Crawl/web retrieval — Bing (→ChatGPT), Brave (→Claude), Perplexity, Google | an HTML page a crawler can fetch and parse | days–weeks |
| **P2** | Scholarly graph — Scholar, Semantic Scholar, OpenAlex, DBLP, ACL | correctly-parsed bibliographic records + resolvable ids | weeks–months |
| **P3** | Model weights — what a model knows with no retrieval | being in the pretraining corpus, and being *talked about* | 6–24 months, one-way |

If you can't say which pipeline a change targets, it probably isn't a change worth making.

## 2. Identity: assert it once, everywhere, identically

The single highest-leverage category, and it's shared because it's about the
person, not the artifact.

- **One canonical URL.** Same string in ORCID, Semantic Scholar, arXiv, GitHub,
  LinkedIn, and every JSON-LD `sameAs`. Changing it later costs more than
  choosing it carefully now.
- **One name form.** `Leshem Choshen`, never `L. Choshen`. Every variant is a
  disambiguation risk; list the ones that exist in `config.yaml` →
  `identity.name_variants` so the tooling can flag records using them.
- **One profile per index.** Two Semantic Scholar author pages means every
  S2-backed tool sees half the corpus. Their docs are explicit: claim one, ask
  support to merge the rest, never claim two.
- **Identifiers are the source of truth; URLs are derived.** Store `arxiv`,
  `doi`, `acl`, `s2_corpus_id`, and let the tooling resolve them to links on
  every run. A stored URL drifts; a resolved one can't.

## 3. Retrievability: write for the chunk, not the page

Retrieval happens at passage level, and the embedding of a passage is roughly an
average of what's in it. Two consequences that apply to a paper claim and a
README section alike:

- **Self-contained.** A passage must make sense retrieved alone, with no
  surrounding context. No "this improves on the above" — name the thing.
- **One idea per passage.** A passage covering three topics embeds near none of
  them.

Formatting is *not* part of this. The 252k-trial study found sectioned-vs-dense
layout had no measurable effect and explicitly deprioritizes formatting work.
Adjacency of question and answer is mechanical; visual FAQ markup is cosmetic.

## 4. The coined-name rule

Coined names are good branding and bad retrieval. `tinyBenchmarks`,
`TIES-Merging`, `ZipNN`, `DOVE`, `ToRR`, `ColPret`, `TextArena` have no lexical
path from the question someone actually asks.

**Every coined name gets a generic gloss adjacent to it** — in the title if you
still can, and in the abstract's first sentence, the README's first line, the
page `<h1>` subtitle, and the repo description. `tinyBenchmarks: evaluating LLMs
with fewer examples` already does this. `Sloth` and `DOVE` don't.

Both tracks carry a `generic_gloss` field for exactly this.

## 5. Say the same thing the same way

RAG systems weight claims that recur across independent sources and drop
single-source ones. So the canonical sentence describing a result should appear
**in the same words** in the paper, the README, the model card, the blog post,
and the talk abstract.

This inverts the writing instinct to reword each time. Rewording fragments the
signal. Pick the sentence once, reuse it verbatim, and make it easy for others to
copy — models learn about your work largely from how *other people* describe it
in related-work sections.

Corollary: never paraphrase a claim into a second slightly-different version.
Point at the canonical one.

## 6. Don't

Measured negative or norm-violating, for both tracks:

| | Why |
|---|---|
| Keyword stuffing / padding topic lists | Measured *worse than nothing* (17.7 vs 19.3 baseline; −10% on live Perplexity) |
| `llms.txt` as a crawler protocol | Google, June 2026: zero effect. The *content* artifact is a different thing wearing the same name |
| Formatting churn | Measured null; the study's authors deprioritize it by name |
| Backlink building as the primary lever | 0.218 correlation vs 0.664 for mentions |
| Extra preprint mirrors | Actively harmful — multiplies versions and defeats the matching that merges preprint and published records |
| Hidden text, prompt injection at automated readers | Retraction-adjacent. Anything that only works because a human can't see it is out |
| Schema markup not backed by visible page text | Discounted, and a spam signal |

## 7. Record every decision, or lose it

Everything is re-derived from live sources on each run. A judgment call that
isn't written down gets silently undone next month.

- Papers → [`data/overrides.yaml`](../data/overrides.yaml)
- Repos → `reviewed: true` in [`data/repos.yaml`](../data/repos.yaml)
- Code and project links → `reviewed: true` in [`data/paper_code.yaml`](../data/paper_code.yaml)
- Tasks you have ruled out → [`data/declines.yaml`](../data/declines.yaml)

If an item keeps reappearing in [`WORKLIST.md`](../WORKLIST.md), it needs an
override — and usually an upstream fix too, so the correction propagates to
Scholar, S2, and OpenAlex instead of only to us. If it reappears because you
decided against it rather than because it is undone, that is what
`declines.yaml` is for: deciding not to do something is a decision, and it has
to be recorded somewhere or it is made again every run. Deciding *not yet* is
also a decision — its `deferred:` key moves a section to the bottom of the
worklist with the condition that brings it back, so "later" survives without
anyone having to remember it.

## 8. Nothing outward-facing without a diff

`propose` → `diff` → `apply --yes`. Read-only by default. This is not
ceremony: these writes land on public records that other people's tooling reads.

## 9. Measurement is part of the work, not after it

See [MEASURE.md](MEASURE.md). Infrastructure counts ("103 papers missing a
journal-ref") verify the work was *done*. They say nothing about whether it
*worked*. Those are different claims and need different instruments.

---

## 10. Duplication: which kind helps, which kind hurts

The question comes up as soon as co-authors or students run this too. The answer
is not uniform — it depends on *what* is duplicated, and the two cases point in
opposite directions.

### Duplicating a claim across owners — **helps**

Retrieval systems weight assertions that recur across independent sources and drop
single-source ones. A co-author's README carrying the same canonical claim
sentence is a genuine independent corroboration. So is the model card, the project
site, and the talk abstract.

This is the mechanism in §5, and more owners makes it stronger, not weaker —
**provided the wording is identical.** Two co-authors independently paraphrasing
the same finding produces two competing near-duplicate claims, which is the
fragmentation problem multiplied by the number of authors. That is the real risk
of this spreading, and it is a wording problem, not a duplication problem.

### Duplicating a canonical page across owners — **hurts**

N personal sites each hosting their own landing page for the same paper is
actively harmful:

- Duplicate-content handling picks one canonical and discards the rest, so the
  authority splits instead of accumulating.
- Scholar's own docs name duplicate titles across repositories as a failure mode
  that can make papers **vanish** as presumed duplicates.
- Every copy is one more thing to drift out of date.

### The rule

**Share the source. Duplicate the pointer. Never duplicate the page.**

| | Where it lives | Who owns it |
|---|---|---|
| The sidecar (claims, scope, misreadings) | one file, one place | one owner per paper — usually first author |
| The canonical paper page | exactly one URL | whoever's site or the project site |
| Links to that page | every co-author's README, repo, site, profile | everyone |
| The claim sentence, verbatim | everywhere | everyone, identically |
| Scholarly-graph listings (ORCID, S2, DBLP) | every co-author lists it | everyone — this is expected and correct, not duplication |

Concretely, when a co-author owns a paper's page, set `canonical_page` on that
paper (`schema/papers.schema.json`) and we link to it instead of generating a
competing one. If a page must be mirrored anyway, `rel=canonical` must point at
the original.

A collaborator forking this tool and running it on *their* corpus is unambiguously
good — they are labelling their own repos and asserting their own identity graph.
The only collision is per-paper pages for shared papers, and `canonical_page`
resolves it.
