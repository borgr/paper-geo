# The rules

Every rule this repo obeys, stated once. Nothing here is procedure — how to run a
refresh is [../RUN.md](../RUN.md), the sidecar's own spec is
[SIDECAR.md](SIDECAR.md), the evidence behind these rules is
[EVIDENCE.md](EVIDENCE.md), and the one-time account work is
[SETUP.md](SETUP.md).

§1–§9 apply to everything. §10 is papers, §11 is repositories, §12 is co-authors.
§13 is the same rules as a table of checkable conditions and what enforces each —
read that one if you are looking for what will actually stop you.

---

## 1. Which pipeline are you optimizing?

Every action belongs to exactly one. Naming it prevents most wasted work.

| | Pipeline | Entry condition | Latency |
|---|---|---|---|
| **P1** | Crawl/web retrieval — Bing (→ChatGPT), Brave (→Claude), Perplexity, Google | an HTML page a crawler can fetch and parse | days–weeks |
| **P2** | Scholarly graph — Scholar, Semantic Scholar, OpenAlex, DBLP, ACL | correctly-parsed bibliographic records + resolvable ids | weeks–months |
| **P3** | Model weights — what a model knows with no retrieval | being in the pretraining corpus, and being *talked about* | 6–24 months, one-way |

If you cannot say which pipeline a change targets, it probably is not a change
worth making.

## 2. Identity: assert it once, everywhere, identically

The highest-leverage category, and the one that is about the person rather than the
artifact.

- **One canonical URL.** The same string in ORCID, Semantic Scholar, arXiv,
  GitHub, LinkedIn, and every JSON-LD `sameAs`. Changing it later costs more than
  choosing it carefully now.
- **One name form.** `Leshem Choshen`, never `L. Choshen`. Every variant is a
  disambiguation risk; the ones that exist go in `config.yaml` →
  `identity.name_variants` so the tooling can flag records using them.
  `name_typos` is a *different* list and the two must stay disjoint — a variant is
  asserted outward as a name you use, a typo is only matched so it can be reported
  and fixed upstream.
- **One profile per index.** Two Semantic Scholar author pages means every
  S2-backed tool sees half the corpus. Their docs are explicit: claim one, ask
  support to merge the rest, never claim two.
- **Identifiers are the source of truth; URLs are derived.** Store `arxiv`, `doi`,
  `acl`, `s2_corpus_id` and let each run resolve them to links. A stored URL
  drifts; a resolved one cannot.

## 3. Retrievability: write for the chunk, not the page

Retrieval happens at passage level, and a passage's embedding is roughly an
average of what is in it. Two consequences, identical for a paper claim and a
README section:

- **Self-contained.** A passage must make sense retrieved alone, with nothing
  around it. No "this improves on the above" — name the thing.
- **One idea per passage.** A passage covering three topics embeds near none of
  them.

Formatting is *not* part of this. The 252k-trial study found sectioned-vs-dense
layout had no measurable effect and deprioritizes formatting work by name.
Adjacency of question and answer is mechanical and matters; visual FAQ markup is
cosmetic.

## 4. The coined-name rule

Coined names are good branding and bad retrieval. `tinyBenchmarks`,
`TIES-Merging`, `ZipNN`, `DOVE`, `ToRR`, `ColPret`, `TextArena` have no lexical
path from the question someone actually asks.

**Every coined name gets a generic gloss adjacent to it** — in the title if you
still can, and in the abstract's first sentence, the README's first line, the page
`<h1>` subtitle, and the repo description. `tinyBenchmarks: evaluating LLMs with
fewer examples` already does this; `Sloth` and `DOVE` do not.

Both tracks carry a `generic_gloss` field for exactly this.

## 5. Say the same thing the same way

RAG systems weight claims that recur across independent sources and drop
single-source ones. So the canonical sentence describing a result appears **in the
same words** in the paper, the README, the model card, the blog post, and the talk
abstract.

This inverts the writing instinct to reword each time. Rewording fragments the
signal. Pick the sentence once, reuse it verbatim, and make it easy for others to
copy — models learn about your work largely from how *other people* describe it in
related-work sections.

Corollary, and the one people get wrong: **never paraphrase a claim** into a
second slightly-different version. Point at the canonical one.

## 6. Don't

Measured negative or norm-violating, for both tracks:

| | Why |
|---|---|
| Keyword stuffing / padding topic lists | Measured *worse than nothing* (17.7 vs 19.3 baseline; −10% on live Perplexity) |
| `llms.txt` as a crawler protocol | Google, June 2026: zero effect. The *content* artifact is a different thing wearing the same name |
| Formatting churn | Measured null; the study's authors deprioritize it by name |
| Backlink building as the primary lever | 0.218 correlation vs 0.664 for mentions |
| Extra preprint mirrors | Actively harmful — multiplies versions and defeats the matching that merges preprint and published records |
| Hidden text, prompt injection at automated readers | Retraction-adjacent. Anything that only works because a human cannot see it is out |
| Schema markup not backed by visible page text | Discounted, and a spam signal |

## 7. Record every decision, or lose it

Everything is re-derived from live sources on each run, so a judgment call that is
not written down is silently undone next month. One file per kind of decision:

| Decision | Goes to |
|---|---|
| this paper record is wrong / these two are one paper | [`data/overrides.yaml`](../data/overrides.yaml) |
| this repo's labels are right, freeze them | `reviewed: true` in [`data/repos.yaml`](../data/repos.yaml) |
| this paper's code/project link is right, freeze it | `reviewed: true` in [`data/paper_code.yaml`](../data/paper_code.yaml) |
| this task is not worth doing | [`data/declines.yaml`](../data/declines.yaml) |
| this task is worth doing, but not before X | `deferred:` in the same file |
| this can only happen after a date | [`data/followups.yaml`](../data/followups.yaml) |
| this claim is correct and I stand behind it | `draft_sidecars.py --accept <slug>` |
| we should build this, some day | [../BACKLOG.md](../BACKLOG.md) |

If an item keeps reappearing in [`WORKLIST.md`](../WORKLIST.md) it needs one of
these — and usually an upstream fix too, so the correction propagates to Scholar,
S2 and OpenAlex instead of only to us. Deciding *against* something is a decision
and belongs in `declines.yaml`; deciding *not yet* is also one, and `deferred:`
moves that section to the bottom of the worklist with the condition that brings it
back, so "later" survives without anyone having to remember it.

**Nothing derived is ever hand-edited.** A hand edit to a derived file survives
until the next run and then vanishes, which is worse than failing because it looks
like it worked.

## 8. Nothing outward-facing without a diff

`propose` → `diff` → `apply --yes`. Read-only by default. This is not ceremony:
these writes land on public records that other people's tooling reads.

## 9. Duplication: which kind helps, which kind hurts

**Duplicating a claim across owners helps.** Retrieval systems weight assertions
that recur across independent sources. A co-author's README carrying the same
canonical claim sentence is genuine independent corroboration, as is the model
card, the project site, and the talk abstract. More owners makes it stronger —
**provided the wording is identical.** Two co-authors independently paraphrasing
one finding produces two competing near-duplicates, which is §5's fragmentation
problem multiplied by author count — a wording problem, not a duplication problem.

**Duplicating a canonical page across owners hurts.** N personal sites each
hosting a landing page for the same paper splits authority: duplicate-content
handling picks one canonical and discards the rest, Scholar's own docs name
duplicate titles across repositories as a failure mode that can make papers
**vanish** as presumed duplicates, and every copy is one more thing to go stale.

**The rule: share the source, duplicate the pointer, never duplicate the page.**

| | Where it lives | Who owns it |
|---|---|---|
| The sidecar (claims, scope, misreadings) | one file, one place | one owner per paper — usually first author |
| The canonical paper page | exactly one URL | whoever's site, or the project site |
| Links to that page | every co-author's README, repo, site, profile | everyone |
| The claim sentence, verbatim | everywhere | everyone, identically |
| Scholarly-graph listings (ORCID, S2, DBLP) | every co-author lists it | everyone — expected and correct, not duplication |

When a co-author owns a paper's page, `canonical_page` on that paper
(`schema/papers.schema.json`) makes us link to it instead of generating a
competitor. If a page must be mirrored anyway, `rel=canonical` points at the
original.

A collaborator forking this tool and running it on *their* corpus is fine: the only
collision is per-paper pages for shared papers, and `canonical_page` resolves it.

---

## 10. Papers

|  | Papers | Repos |
|---|---|---|
| Retrievable unit | a **claim** | a **how-to** |
| Query shape | citation-shaped: "what's the method for X" | question-shaped: "how do I X" |
| Who owns the surface | arXiv, the publisher, the indexes — **not you** | you, entirely |
| What "correct" means | faithful to what the paper actually showed | the instructions work |
| Cadence | once per paper, at publication, then frozen | continuous |
| Automatable share | metadata: high. Claims: zero | high |

The consequence that shapes the whole track: **you do not control the surfaces
that matter most.** arXiv, ACL Anthology and Scholar hold the canonical records,
and your only levers there are getting their metadata right and publishing a page
you *do* control that they can link to.

### 10.1 Metadata correctness is not cosmetic

Scholar's parser is fully automated with no human correction. Its docs are
explicit that wrong bibliographic data means "(incorrect) bibliographic data would
not match (correct) references to them from other papers" — which lowers ranking
and can drop the paper. One documented failure mode: a venue name extracted as a
title makes papers vanish as presumed duplicates, and this corpus had a live
instance (`"Journal of Memory and Language"` as a paper title, now `drop` in
`overrides.yaml`).

The governing principle, from those docs: present the article **as it would
normally be cited in the References section of another paper.**

Missing journal-refs are this track's largest single gap. arXiv has no write API,
so it is one web form each — do them in citation order, from `WORKLIST.md`, and
note that each one needs arXiv ownership of the paper first.

### 10.2 Every paper needs an HTML surface

A PDF-only paper is retrievable in P2 (Scholar parses PDFs) and near-invisible in
P1. `links.html` in [`papers.yaml`](../data/papers.yaml) resolves to the arXiv
rendering where it exists and the ar5iv fallback where it does not — pre-2024
papers have no `arxiv.org/html/`. Papers with no arXiv id at all have no HTML
surface anywhere, so their page on our own site is the only one.

### 10.3 The `links` map is the identity of the work

One paper is five to twelve URLs. An engine either treats them as one work with
many locations or as many unrelated pages, and a `sameAs` array is what decides.

Derived on every run from identifiers, never stored by hand: `arxiv`,
`arxiv_pdf`, `html` (+ `html_source`), `huggingface`, `alphaxiv`, `doi`,
`acl_anthology`, `semantic_scholar`, `publisher`, `code`.

Hand-supplied, via the sidecar's `links_extra`: project page, talk video, slides,
poster, leaderboard, blog post, dataset, demo. These cannot be derived and are
often the highest-value ones.

### 10.4 Publish the citation verbatim

`papers.yaml` carries `bibtex` copied byte-for-byte from `enhanced.bib` rather
than regenerated from parsed fields. A regenerated key would differ from the one
people have already cited, and §5 applies to citation strings too: one canonical
form everywhere beats a tidier one.

### 10.5 The sidecar

One file per paper at `data/sidecars/<slug>.md`, holding the claims in quotable
form, the scope each holds under, coined terminology and the misreadings worth
pre-empting. It is the one artifact here whose content is judgment rather than
derivation, and the only one that targets **fidelity** rather than visibility —
which is the real problem for work that is already well known, since LLM summaries
overstate scientific conclusions about 5× more often than human ones.

A model drafts it from the paper's own full text; the author accepts it. The full
spec, the drafting procedure and the open format decisions are
[SIDECAR.md](SIDECAR.md), which is also the literal source of the drafting prompt.
Two rules from it are load-bearing enough to state here as well, because
everything on a paper page depends on them: **questions get 2–4 deliberate
paraphrases, claims get none**, and **a question never appears without its answer
adjacent**.

### 10.6 What a paper page emits

Per paper at `borgr.github.io/papers/<slug>/`, generated from `papers.yaml` plus
the sidecar:

1. `ScholarlyArticle` JSON-LD — authors with ORCID `@id`s, venue, date, DOI, the
   full `links` map as `sameAs`, `codeRepository`, `dataset`.
2. Highwire meta tags — `citation_title`, one `citation_author` per author,
   `citation_publication_date`, `citation_conference_title`, and an absolute
   `citation_pdf_url` in the same subdirectory. All three mandatory ones or
   Scholar ignores the lot.
3. A visible abstract, no gate, plus a reference list under a literal `References`
   heading (Scholar's PDF-layout fallback rules).
4. The Q&A block, the claims with their scope, terminology, misreadings.
5. `rel=canonical` to itself; the sidecar in the repo is source, not a competitor.
6. Flagship results as CSV next to the figure — an LLM handed a PNG of a
   regression table sees pixels.

---

## 11. Repositories

You own this surface completely and GitHub is a top-5 AI-cited domain, so the
ceiling is higher and the work is cheaper than the papers track. Almost none of it is
about papers, though: **only 1 of 31 repos maps to a paper.** Paper code lives in
collaborators' and organisations' accounts (`prateeky2806/ties-merging`,
`ibm-research/*`), so planning this track around "the code for the papers"
mis-targets nearly all of it.

### 11.1 The three kinds that need different treatment

Set as `kind` on each repo in [`repos.yaml`](../data/repos.yaml). Forks are
excluded from all of it — they are not yours to describe, and topics on a fork are
noise.

**`guide` — the highest-value category, and the easiest to overlook.**
`facultips`, `post`, `arXiv_stuck`, `paper_updated`, `tutEval`,
`paper-sharpener`. These answer **question-shaped queries**, literally what people
type into an assistant: *"why is my arXiv paper stuck"*, *"how do I apply for a
tenure-track job"*, *"how do I evaluate an LLM"*. Under query fan-out that is the
closest match to real demand in the whole account, on a heavily-cited domain.

- The README's **first line answers the question in the title.** Not "this repo
  contains…" — the answer.
- One heading per sub-question, phrased as the question.
- Dated. Recency is a gatekeeper-level factor and a guide's date is not frozen the
  way a paper's is. Add "last reviewed: YYYY-MM" and mean it.
- Where one publishes via GitHub Pages, set `homepage` to the site so the repo and
  the site reinforce each other.
- **No `CITATION.cff`** — there is no paper to cite.

**`paper-code` — a minority, and mostly not in this account.** `DORA`, `USim`,
`EoE`, `IBGEC`, `auto_challenge_sets`, `ordert`, `GEC_UD_divergences`,
`assess_learner_language`, `GEC_BOTHER`, `languageClustering`. Retrieved by
citation-shaped queries, and the lever is a bidirectional paper↔repo link:

- **`CITATION.cff`**, generated from the paper's verbatim `bibtex`. GitHub renders
  a "Cite this repository" widget from it and it is machine-readable.
- **A generated links block in the README**, carrying the paper's *whole* link set
  the way the paper page does — paper, HTML rendering, HF paper page, data,
  models, project page. Three reasons: Hugging Face extracts the arXiv id and
  auto-tags the repo on the paper page, which is the cheapest paper↔repo edge
  there is; GitHub is heavily crawled, so a README link to the canonical page is a
  real P1 edge; and it is §5's corroboration mechanism, asserting the same link
  set on a second high-authority domain. Maintained between markers so it is
  regenerable without touching hand-written prose, and switched by
  `write_links_block` on the repo entry:

  ```markdown
  <!-- paper-geo:links:start -->
  ...generated...
  <!-- paper-geo:links:end -->
  ```

  Where several people hold repos for one paper, every block points at the **same**
  canonical page rather than each owner publishing their own (§9).
- **The README states the finding, with the number**, not only usage instructions.
  For method questions the README, not the PDF, is what gets cited.
- `homepage` → the paper's page on the site. Until that page exists the sweep
  defers it rather than publishing a link to a 404.

For paper code in **someone else's** repo the equivalent is a pull request:
`CITATION.cff` plus the arXiv link. That is social, not automatable, and belongs on
a person's todo list rather than in this pipeline.

**`tool` / `dataset` / `teaching` / `website` / `other`.** Standard hygiene:
accurate description, honest topics, and for `teaching`/`other`, do not
over-invest. A repo with no content at all is a candidate for `skip: true` or
archiving — an empty repo with a confident description is worse than an empty repo.

### 11.2 Labelling: topics and descriptions

The rules below are the source of the labelling prompt in
`scripts/propose_topics.py`, which reads this block by its markers. Editing them
here changes what the model is told, in the same commit.

<!-- prompt:start -->
Two things matter more than sounding good:

1. **Accuracy over coverage.** A wrong topic actively misleads retrieval and reads
   as careless. If the evidence does not support a label, leave it out and set
   `confidence` lower. An empty-ish but correct set beats a full but wrong one. The
   keyword-matching first attempt at this tagged a grammatical-error-correction
   repo `model-merging` and a sentence-similarity metric `pretraining` — about a
   third wrong. That is the failure mode to avoid, and the reason labelling moved
   to a model with a review gate.

2. **Search vocabulary, not project vocabulary.** Use the words someone who does
   not already know this project would type: `grammatical-error-correction`, not
   `gec-ud-divergences`. Coined names are branding; the plain phrasing goes in
   `generic_gloss`.

Judge only from the evidence provided. Do not infer a research area from the
author's other work, and do not assume a repo is paper code because the author is a
researcher — many are guides, teaching material, or small utilities.

**Topics:** 3–8 of them. Padding is keyword stuffing wearing a different hat.
Omit rather than guess; some repos legitimately have none.

**Description:** one line saying what the thing **is** and what it is **for**. Aim
under 120 characters. No marketing. If the name is coined, lead with the plain
phrasing.
<!-- prompt:end -->

GitHub topics are the account's primary discovery facet, and a repo with no
description is invisible to GitHub search regardless of its topics.

### 11.3 Desired state only

`reviewed: true` on a repo freezes it permanently against future proposals, and
that flag is the whole idempotency story for this track: re-running `propose` adds
newly created repos and refreshes paper links while carrying forward every field
you or the model set.

You do not need the flag to correct one label. A proposal is promoted into the
applied fields only in the run where that proposal *changed*, so deleting a wrong
topic survives every run in between — but not the run where the proposal changes, and
nothing distinguishes a topic you deleted from one never proposed. So **a deletion you
mean to keep goes in `declined_topics`**, next to `topics` on the same row:

```yaml
topics:
- reinforcement-learning
declined_topics:
- nlp-free            # invented; the model keeps proposing it
```

`promote()` subtracts that list from every future proposal and says so when it does.
Use `reviewed: true` for the other thing: freezing a whole row against answers not yet
written.

`repos.yaml` holds **desired state only** — no stars, no `current_*` mirrors of
GitHub, which would churn the file on every run and go stale between them. `diff`
fetches live state at the moment it runs, so it compares intent against reality rather
than against a snapshot.

### 11.4 What pays first

`WORKLIST.md` ranks the paper work by citations, which is the right order for
anything per-paper. The orderings that are *not* derivable, and so belong here:

- **Papers.** Identity fixes (§2) first — hours, once, largest effect, and
  [SETUP.md](SETUP.md) has their internal order (ORCID, then arXiv ownership,
  which every journal-ref depends on). Then journal-refs and HF paper pages in
  citation order. Then sidecars, in citation order, top-down.
- **Repos.** Topics and descriptions on all of them first — fully automatable.
  Then `CITATION.cff` on the paper-code repos that are yours. Then the `guide`
  READMEs' first lines, which is the highest query-match work in the account and
  cannot be automated. Then arXiv links in READMEs, for the free HF cross-listing.
  Then, optionally, PRs adding `CITATION.cff` to collaborators' repos — social and
  slow. Last, `skip: true` or archive the empty repos.

Twenty verified sidecars beat a hundred rushed ones, and ten negotiated
co-authorships beat a hundred (§12).

---

## 12. Co-authors

Exactly one party owns each paper's canonical page and its sidecar; everyone else
links to it (§9). The protocol for agreeing on that has no server, no registry and no
accounts: each participant publishes a static JSON file at a stable URL saying which
papers they claim:

```
https://borgr.github.io/paper-geo.json
```

```json
{
  "paper_geo_manifest": 1,
  "owner": "borgr",
  "name": "Leshem Choshen",
  "orcid": "0000-0002-0085-6496",
  "canonical_url": "https://borgr.github.io",
  "claims": [
    {
      "ids": ["doi:10.52202/075280-0310", "arxiv:2306.01708"],
      "title": "TIES-Merging: Resolving Interference When Merging Models",
      "canonical_page": "https://borgr.github.io/papers/ties-merging-.../",
      "has_sidecar": true
    }
  ]
}
```

Peers' manifest URLs go in `config.yaml` under `collaboration.peers`, and every
run reconciles:

| Situation | What happens locally |
|---|---|
| A peer claims it | `canonical_page` → theirs; we generate a **link**, not a page |
| We claim it | we own it: generate the page, own the sidecar |
| Nobody claims it | left unclaimed, with a suggested owner. **We never auto-claim** |
| Two parties claim it | **flagged, never auto-resolved** — this is the exact harm being prevented |

Not auto-claiming is the important default: silently claiming a paper a co-author is
about to claim is how two canonical pages come to exist. A peer who does not run this
tool can hand-write six lines of JSON and participate.

**Who should own a paper** — advisory, and the tool only ever suggests: the first
or corresponding author usually, since they wrote the claims and can rank which
limitation binds; whoever has the stronger web presence when that differs sharply,
because the page benefits from the better-crawled domain; a project site for a
multi-paper project (BabyLM, TextArena, EvalEval), since one site owning a
coherent cluster beats the same pages scattered; and you, for anything nobody else
will maintain, because an unmaintained canonical page is worse than none.

**What everyone else does, which is most of the value.** Per paper, a non-owner
should link to the canonical page from their README, site and profile; reuse the
claim sentence **verbatim** from the owner's sidecar rather than paraphrasing it;
list the paper in their own ORCID / Semantic Scholar / DBLP, which is the
scholarly graph, where every co-author listing a paper is expected and correct;
and not publish their own page for it. One sidecar per paper, one owner, shared
rather than forked — a co-author who wants to contribute claims PRs the owner's
sidecar.

**What co-authors add beyond you running the code alone —** nothing for coverage:
run it across your whole corpus and every paper already has a canonical page. The
gains are a 5-author paper's page linked from 5 independent accounts and domains
instead of 1 (independent mentions correlate with AI-Overview visibility at 0.664 vs
0.218 for backlinks, and you cannot post in someone else's README); N co-authors
asserting the *identical* claim sentence, which needs coordination because it needs
the same words; and preventing a co-author from spinning up a competing page for the
same paper.

So use it for multi-author flagship papers with active co-authors, the top of
`WORKLIST.md`. Do not negotiate over the long tail; claim those yourself and move
on. Ten negotiated papers is a good outcome.

---

## 13. What is actually enforced

The right-hand column is the truth; the prose above is the explanation. A rule with
nothing in that column is in bold at the bottom.

| Condition | Enforced by |
|---|---|
| `topics` ≤ 8, lowercase-hyphen, no duplicates | `schema/repos.schema.json` |
| a topic contains no comma or space | `validate.py` regression check (the API rejects it 422) |
| `description` ≤ 160 chars | `schema/repos.schema.json` (the 120 target is style, not enforced) |
| `kind` is one of the seven | `schema/repos.schema.json` |
| a proposal carries `confidence` | the embedded schema in `scripts/propose_topics.py` |
| `reviewed: true` is never overwritten | `scripts/propose_topics.py` and the `repos` step skip those rows |
| a hand edit to `repos.yaml` survives the next ingest | `propose_topics.promote()` only touches repos whose proposal changed in that run |
| no two papers share a slug | `validate.py` regression check (one page used to overwrite another) |
| no LaTeX residue in `title_display` / `venue_display` | `validate.py` regression check |
| no private `pretitle` macro in published BibTeX | `validate.py` regression check |
| a paper claimed by two parties blocks publication | `validate.py` regression check on `owner_conflict` |
| a paper of yours is never dropped for a group-shaped author list | `collect.py authorship_gate` asks arXiv for the full list on every rejection with an arXiv id, and `build/not_mine.json` grades each remaining drop by whether it could be checked at all |
| the corpus is complete, not merely well-formed | `scholar_check.py` against your Scholar profile. The only check whose reference list is built elsewhere, so the only one that can see a paper that never arrived — reported into `WORKLIST.md`, never fatal |
| `name_typos` disjoint from `name_variants` and `name` | `validate.py check_name_lists` |
| affiliations are a bare name or `{name, url, ror, wikidata}`, ROR and QID well-formed | `validate.py check_affiliations` |
| every `overrides.yaml` key is one something reads, and every `fields:` slug names a live paper | `validate.py check_overrides` (both failures are silent no-ops that look done) |
| a retired slug redirects to a live page, or explicitly to `null` | `validate.py check_slug_history`. That the file is append-only is convention, not a check — deleting a line breaks a published URL |
| every sidecar `answered_by` id names a real claim | `validate.py check_sidecars` |
| every `qa` entry has at least one phrasing | `validate.py check_sidecars` |
| the corpus sizes stated in the docs are current | `validate.py check_doc_counts`, `--fix-counts` to rewrite. Reported, not fatal — the one problem class that does not mean something is broken |
| the prompt blocks in this file and `SIDECAR.md` exist | `validate.py` marker check, and `rules_block()` raises rather than sending a model an empty prompt |
| a structural failure stops the run before anything renders | `validate.py` exits 1 and `update.py step_validate` turns that into a `SystemExit` |
| a sidecar draft can never reach a page | file layout: the site globs `data/sidecars/*.md`, drafts sit one level down |
| nothing outward-facing without an explicit flag | `--apply` / `--deploy` / `--yes`, absent by default |
| **every coined name has a generic gloss** | **nothing — the field exists and is optional** |
| **claim and scope shape, key order, question coverage** | **nothing — [SIDECAR.md](SIDECAR.md) §5, open** |
| **a README's first line answers its title** | **nothing — a human reading the six `guide` repos** |
| **the identical claim sentence really is identical across surfaces** | `measure/check_structure.py` compares surfaces and reports drift |
