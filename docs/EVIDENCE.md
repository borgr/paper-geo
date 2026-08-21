# The evidence, and how to tell whether it worked

Why the rules in [RULES.md](RULES.md) are what they are, and what instruments exist
to check them. Read rarely, and never during a run — nothing here is a procedure.

Grading used throughout: **[A]** controlled experiment or authoritative platform
documentation · **[B]** large observational study · **[C]** vendor-stated or
practitioner claim, directional only.

---

## 1. Three pipelines, not one index

[RULES.md §1](RULES.md#1-which-pipeline-are-you-optimizing) states the rule. The
evidence for splitting them is that they have different entry conditions, different
latencies, and different things that win:

| | What wins |
|---|---|
| **P1** web/crawl | crawlable HTML, topic match, freshness, structured data, being in the top-10 of the underlying index |
| **P2** scholarly graph | metadata correctness, identifier linkage, author disambiguation, abstract presence |
| **P3** model weights | volume and consistency of third-party mentions; presence in high-weight corpora (Wikipedia, GitHub, arXiv, Common Crawl) |

Which engine reads which index: ChatGPT's web search runs on Bing, Claude's on
Brave, Perplexity on its own ~5B-URL index with Bing fallback, Gemini and AI Mode on
Google's **[C, consistent across several independent write-ups]**. Optimizing only
for Google leaves three of four unaddressed — and arXiv, GitHub, Hugging Face and
the ACL Anthology are well covered in *all* of them, where a personal Wix subdomain
may not be.

P1 fixes are fast and fully under your control. P2 fixes are slow, compound, and are
the ones that matter for research audiences. P3 is not directly actionable per paper
— it is a by-product of P1 + P2 plus other people writing about the work. And being
invisible in one pipeline is invisible-shaped in all of them: a paper that exists
only as a PDF is retrievable in P2 (Scholar parses PDFs), weak in P1, and
contributes little to P3.

## 2. What the GEO literature establishes

**Aggarwal et al., "GEO: Generative Engine Optimization", KDD '24
(arXiv:2311.09735)** — 10K queries, GEO-bench, validated on live Perplexity. Nine
content edits against a baseline **[A]**:

| Edit | Position-adjusted word-count share (baseline 19.3) |
|---|---|
| Add quotations | 27.2 (**+41%**) |
| Add statistics | 25.2 |
| Cite sources | 24.6 |
| Fluency optimization | 24.7 |
| Add technical terms | 22.7 |
| Make easy to understand | 22.0 |
| Authoritative tone | 21.3 (n.s.) |
| Unique words | 20.5 (n.s.) |
| **Keyword stuffing** | **17.7 — worse than doing nothing**; −10% on live Perplexity |

Three findings matter more than the ranking. The winning edits are exactly the ones
good scientific writing already rewards — quote your sources, give numbers, cite,
write fluently — so there is no tension between this and scholarly quality.
Keyword stuffing actively hurts, which kills the whole SEO-trick instinct. And
**GEO helps low-ranked sources far more than top-ranked ones**: when all five
retrieved sources were optimized, rank-5 gained **+115%** while rank-1 *lost* 30%.
Content optimization is a lever for the source that is retrieved-but-ignored.

**Vishwakarma et al., "What Gets Cited: Competitive GEO in AI Answer Engines",
SIGIR '26 (arXiv:2605.25517)** — 252,000 trials, 6 models, matched-pair design with
position counterbalancing and a logistic GLMM. The strongest causal evidence in the
area **[A]**, though its corpus is consumer product reviews, so transfer to
scholarly content is an assumption rather than a result. Its central structural
claim is the useful one — the factors are **not additive**:

- **Four gatekeepers** (significant in all 6 models, odds ratios >100): topic match,
  presence of the specific concrete fact the query asks for, a recent timestamp,
  being first in the candidate list. Failing any one can zero out citation odds no
  matter how good the rest is.
- **Seven differentiators** (OR ≈ 2–240): query-term coverage, specifications and
  concrete detail, comparisons against alternatives, evidence for claims, internal
  consistency, depth of coverage, strong social proof.
- **Seven factors with no consistent effect** — notably **content structure
  (sectioned vs dense prose) had no measurable effect.** The authors conclude models
  parse text regardless of visual organization and explicitly deprioritize
  formatting work, which contradicts most commercial AEO advice.

Two of its findings need ethical flagging for scientific use. "Confident vs hedged"
language had ORs of 599 (Gemini) and 754 (Claude); taken naively that says strip
your caveats. **Do not.** The defensible version is to state what you did find
precisely and unhedgedly, and put the scope conditions somewhere structured and
machine-readable rather than dissolving them into prose — which is what the sidecar
is. This is the one place where the incentive gradient of AI retrieval points away
from good science, and worth saying out loud in public. Separately, recency bias is
strong (recent vs 2019 timestamp: OR >10,000 in 4 of 6 models); a paper's date is
fixed, which argues for a dated, updated page per line of work rather than relying
on the paper's date alone.

## 3. What transfers from commercial practice

| Practice | Transfers to papers? |
|---|---|
| Answer-first, self-contained 200–400 token passages **[C]** | **Yes, cheaply.** Not because of chunking magic — the SIGIR paper found structure ≈ no effect — but because a self-contained passage survives being retrieved *alone* |
| Entity establishment: Wikidata item → `sameAs` → Knowledge Graph **[C]** | **Yes.** Wikidata needs no notability, is free, takes minutes, feeds Google's KG and is a high-weight P3 corpus. Brand mentions correlate with AI-Overview visibility at 0.664 vs 0.218 for backlinks **[C, vendor-chained — directional only]** |
| `llms.txt` as a *protocol* | **No.** Google confirmed (June 2026) zero effect on Search or AI Overviews, and no major platform commits to parsing it. Protocol-`llms.txt` is dead |
| `llms.txt` as a *content artifact* | **Yes** — see §5. The academic version is not a crawler directive but an author-written orientation document. Different thing, same name |
| Schema.org JSON-LD (`ScholarlyArticle`, `Person`, `Dataset`, `sameAs`) | **Yes.** Cheap, generated, and the `sameAs` array is the only place you can *assert* your own identity graph |
| Being on high-citation-share domains | **Yes, and this is the big one.** Citation share in AI answers is hyper-concentrated: Wikipedia, Reddit, YouTube, LinkedIn, GitHub dominate, and the top ~15 domains take ~68% of consolidated share **[B, multiple independent studies, ~150K–680M citations]** |
| Not blocking `GPTBot`, `ClaudeBot`, `PerplexityBot`, `OAI-SearchBot` | **Yes** — pure downside risk, worth a one-time check |
| Keyword density, backlink building, formatting churn | **No.** Measured null or negative |
| Hidden text / prompt injection aimed at automated readers | **Off-limits.** There have been retraction-level scandals over hidden prompts in manuscripts |

The single most important transfer: **for a general-audience AI answer the paper's
PDF is rarely the cited artifact** — the GitHub README, the Wikipedia paragraph, the
HF model card or someone's blog post is. Optimizing the paper alone optimizes the
least-cited surface in the ecosystem.

## 4. The scholarly pipeline: what actually gates you

From Google Scholar's own inclusion guidelines **[A — authoritative]**, the
non-obvious parts:

- The parser is **fully automated with no human correction.** Misparsed
  bibliographic data means "(incorrect) bibliographic data would not match
  (correct) references to them from other papers", which lowers ranking and can drop
  the paper. Stated failure mode: a repository or venue name extracted as the
  *title* across many papers makes them vanish as presumed duplicates.
- The governing principle: present the article "**as it would normally be cited in
  the References section of another paper**" — venue, volume/issue, first page.
  This is why an arXiv record with no journal-ref is a real problem: it starves the
  version-matching that merges the arXiv and proceedings versions into one cluster.
- Highwire Press meta tags are preferred and **all three mandatory ones**
  (`citation_title`, `citation_author`, `citation_publication_date`) must be present
  or the page is processed as if it had none. Dublin Core is a last resort.
- `citation_pdf_url` must be absolute, and the PDF must live **in the same
  subdirectory** as the HTML abstract, or it is indexed as a tagless standalone doc.
- For a self-hosted PDF with no meta tags, layout *is* the metadata: title ≥24pt at
  the top, authors 16–23pt directly beneath, a citation line in the first-page
  header/footer, a section literally headed "References" or "Bibliography", and no
  Type 3 fonts.
- Abstract or full text visible with **no interstitial, no login, no scroll, no
  click.** One paper per URL. Update latency for already-indexed papers: **6–9
  months.**

The other graph nodes, and what each feeds:

- **ORCID** — the canonical author identity. Feeds OpenAlex name variants and most
  publisher pipelines; auto-populates via the Crossref/DataCite Search & Link
  wizards plus standing auto-update permissions. arXiv can be linked to it and says
  it will "use ORCID iDs in preference to internal arXiv author identifiers" **[A]**.
- **Semantic Scholar / S2AG** — feeds Elicit, Consensus, SciSpace, S2ORC and most
  LLM lit-search agents. Author pages come from an automated disambiguation model
  (S2AND) that **splits on similar-name/coauthor-cluster boundaries**. No
  self-service merge exists; claiming the page is the documented remedy and you must
  **not** claim two **[A]**.
- **OpenAlex** — open, widely mirrored, ORCID-driven for name variants. Merges
  duplicates in bulk and accepts corrections.
- **DBLP / ACL Anthology** — hand-curated, high-precision, well-crawled, strong in
  this field specifically.
- **Hugging Face Papers** — successor to Papers with Code (shut down July 2025). Any
  arXiv paper is indexed by visiting `hf.co/papers/<arxiv-id>`; authorship can be
  claimed and verified; and any model, dataset or Space whose README links the arXiv
  URL is auto-tagged and cross-listed on the paper page **[A — HF docs]**. This is
  now the main paper↔artifact join surface in ML.
- **arXiv HTML** (LaTeXML, since Dec 2023) — a crawlable HTML page for every
  post-2023 paper. Pre-2024 papers have no `arxiv.org/html/`, but
  `ar5iv.labs.arxiv.org/html/<id>` covers them.
- **arXiv abstract-page hooks** — `Links to Code` (CatalyzeX), alphaXiv, Hugging
  Face, DagsHub, ScienceCast, Connected Papers, scite. Free surfaces you can
  populate.

## 5. Machine-readable science: the frontier this bets on

Two 2026 proposals are the serious version of "GEO for papers", and both converge on
the same idea: **the missing artifact is author intent, not better parsing.**

**Goldsmith-Pinkham, "LLM-Friendly Academic Papers" (Mar 2026)** proposes a
per-paper `llms.txt` plus a paper bundle. The `llms.txt` is plain markdown,
author-curated, in seven sections: what the paper is about (*not* the abstract),
important context and misconceptions, a data/methods fingerprint, key results,
**limitations and scope**, a navigation guide, publication status. The bundle adds
`paper.md`, figures, **tables as CSV or markdown, never images**, code with
`reproduce.sh` and pinned deps, and `references.bib`. The argument for why parsing
improvements cannot substitute: even flawless text extraction "cannot indicate which
results are central, which caveats bind, or what a term of art means in context."
Its minimum viable version is explicitly *"two paragraphs on what the paper shows
and doesn't, posted with the PDF — fifteen minutes."*

**Booeshaghi et al., "Science should be machine-readable" (bioRxiv, Feb 2026)** goes
further, representing papers as structured claim sets — their OpenEval extracted
~112 claims per paper. Direction of travel: the unit of scientific retrieval becomes
the claim, not the paper.

Motivating evidence for both: LLM summaries were ~5× likelier than human ones to
overstate scientific conclusions (Peters & Chin-Yee 2025), and 74.9% of 20,000
scholarly PDFs met no accessibility criteria (Kumar & Wang 2024).

**Why this matters more than ordinary GEO:** it targets *fidelity*, not visibility.
The failure mode for a well-known paper is not being unfindable, it is being
findable and then described wrongly — overstated, mis-scoped, credited to the wrong
sub-claim. Publishing your own claims and scope conditions is the only lever on
that, and it is one no index or publisher can pull for you. It is also the part of
this project with the least direct evidence, which is stated again in §7.

## 6. The baseline: what the corpus looked like before any of this

A dated snapshot, kept because it is the only "before" measurement that will ever
exist. Taken from both Semantic Scholar author records; 122 unique papers then, 112
after duplicate merging. The standalone script that produced it has been deleted --
`scripts/collect.py` superseded it, and a second copy of the same fetching was the
kind of dead code that reads as a live tool. The numbers below are the record.

```
papers                             122
  split across S2 records A / B    72 / 50      <- two profiles, one person
  no abstract in S2                14/122 (11%)
  with arXiv id                    102/122 (84%)
  arXiv: NO journal-ref            96/102 (94%)
  arXiv: NO DOI field              97/102 (95%)
  arXiv: NO HTML rendering         41/102 (40%)
  HF paper page missing            47/102 (46%)
  HF page w/ 0 claimed authors      7/102  (7%)
```

| Node | State then | Consequence |
|---|---|---|
| **Semantic Scholar** | **two author pages** — `41019330` (73 papers, 3,610 cites, h=31, claimed) and `2283849613` (52 papers, 1,060 cites, unclaimed) | every S2-backed tool saw *either* the merging/BabyLM/eval half *or* the benchmarks/scaling-laws half. Author-level retrieval halved, both halves under-ranking. The highest-leverage single fix in the audit |
| **ORCID** `0000-0002-0085-6496` | existed, **0 works** | the canonical identifier asserted nothing, so downstream disambiguation had nothing to anchor on |
| **OpenAlex** | 1 main record (143 works) + **4 duplicates** (8 works) | minor citation leakage |
| **Wikidata** | **no author item, no paper items** | no entity anchor in the KG, no `sameAs` target, absent from a high-weight P3 corpus — with a zero notability bar to fix |
| **DBLP** | 166 hits, well curated | healthy |
| **ACL Anthology** | person page exists | healthy |
| **Google Scholar** | 5,829 cites, h=38, i10=74 | healthy; the public-facing number was never the problem |

Web surfaces then: the canonical homepage per S2, ORCID, LinkedIn and GitHub was a
`wixsite.com` subdomain with `<html lang="he">`, zero JSON-LD, a meta description
reading "NLP Publications, scientific interests and a surprise", and no per-paper
pages — the one surface fully under his control was the least machine-readable one
he owned. `borgr.github.io` was live and unused, already carrying `Person` JSON-LD
with a placeholder email. `github.com/borgr` had 90 public repos with **zero topics
on every one**, several with no description, and no `CITATION.cff` in any of the 9
flagship repos checked. And `github.com/borgr/publications` already held the whole
bibliography pipeline — the Scholar scrape, the arXiv→published-BibTeX resolver, and
`enhanced.bib` with abstracts — so nothing here had to be built from scratch.

One sentence: **the scholarly-graph layer was in good shape wherever someone else
curates it (DBLP, ACL, Scholar) and broken wherever it depended on him asserting his
own identity (S2 split, empty ORCID, no Wikidata) — and the web layer was almost
entirely unbuilt despite the raw material sitting in a repo.**

## 7. What is deliberately not built, and the honest uncertainty

The tier of work with the *best* observational evidence is the least automatable,
and most of it is still undone:

- **Wikipedia.** Model merging, benchmark evaluation, sample-efficient pretraining
  and scaling laws are all topics where a well-sourced paragraph citing the primary
  literature is a legitimate encyclopedic contribution. Wikipedia is the #1 cited
  domain in ChatGPT (47.9% of top citations in one study **[B]**) and a high-weight
  P3 corpus. Norms caveat: WP:COI — do not cite yourself into articles; write the
  topic honestly, propose on talk pages, or let others write the coverage.
- **README-as-explainer** for each flagship repo, answering what this is, what it
  found, and how to use it, with the numbers in it. For method questions the README,
  not the PDF, is what gets cited.
- **One durable explainer post per line of work**, dated and updated. Recency is one
  of the four gatekeepers; a paper's date is frozen, a post's is not.
- **Reddit / HN / Bluesky / LinkedIn** — high-citation-share domains, and the
  third-party corroboration layer that P3 actually runs on.

And the uncertainty, stated plainly because it belongs in public: the identity and
metadata work rests on authoritative platform documentation and directly measured
gaps — that will work. The pages-and-sidecars layer rests on a plausible but
untested transfer of consumer-product GEO findings to scholarly retrieval, plus a
2026 proposal with no adoption data; its *fidelity* benefit is more defensible than
its *visibility* benefit. The third-party-mention layer has the best observational
evidence and the worst automatability. Nothing here has a controlled study on
academic content, because as far as this survey found nobody has run one — which is
itself a paper-shaped hole, and one this corpus is unusually well positioned to
fill.

---

# Can we tell whether it worked?

Three questions. Two are cheaply and reliably measurable. One — the causal one — is
close to unanswerable at 113 papers, and this section says so rather than dressing
up an underpowered design.

| | Question | Instrument | Verdict |
|---|---|---|---|
| **A** | Did the work get done, and is it still done? | counters + validator | **Build it.** Deterministic, free, runs every time |
| **C** | Is the work described *correctly* right now? | claim-fidelity scoring | **Build it.** Diagnostic, not causal — produces a worklist |
| **B** | Did our changes *cause* more citations? | a controlled comparison | **Probably don't.** One design survives scrutiny; even it is marginal |

**A is not evidence for B.** "103 papers now have a journal-ref" is a completed
task. Most published GEO case studies stop at A and present it as B.

## A. Structural checks — built, and unconditional

Cheap, deterministic, and they verify the work exists and *stays* existing, which is
a real class of failure: metadata gets reverted, pages 404, an index re-splits a
profile. Already printed by every `update.py` run: the coverage counters
(journal-ref, HTML surface, HF page, sidecar, verbatim BibTeX), `scripts/validate.py`
against `schema/*.json`, and the cross-checks JSON Schema cannot express.

**Regression policy: every bug that has shipped gets one check, and those checks run
*unconditionally*.** That last word is the lesson. The original design put them in a
branch that only executed when `jsonschema` was absent, so installing `jsonschema`
silently skipped them — which is how a duplicate slug reached production and quietly
cost one paper its page. A check behind a conditional is not a check.

| Shipped bug | Guard |
|---|---|
| Invalid JSON-LD from string-concatenated LaTeX | `check_structure.py`: all JSON-LD parses |
| Duplicate slug silently overwrote a page | `validate.py`: duplicate-slug check |
| S2-only records lacked authors → no highwire tags | `check_structure.py`: 3 mandatory tags on every page |
| LaTeX braces leaked into headings and `citation_title` | `validate.py`: no `{}$\\` in `*_display` fields |
| Private `pretitle` macro shipped in published BibTeX | `validate.py`: `pretitle` rejected |
| Topics call built comma-joined → 422 | `validate.py selftest()`: asserts the arg builder |
| Two parties claiming one paper | `validate.py` + `check_structure.py` |

`selftest()` covers the cases with no data footprint — a wrongly-built API call looks
fine in every data file, so it needs an assertion on the code path itself.

Worth adding, all mechanical:

| Check | Catches |
|---|---|
| Every URL in `links` returns 200 | link rot, ar5iv outages, moved publisher pages |
| Highwire tags present and complete on each generated page | Scholar silently ignoring a page for one missing mandatory tag |
| JSON-LD parses and validates as `ScholarlyArticle` | markup errors that make structured data worthless |
| `sameAs` on the site ⊇ `links` in the data | a surface we know about but never asserted |
| Abstract visible without JS on each page | the SPA failure mode — fine in Google, empty to Claude |
| Robots/CDN allow `GPTBot`, `OAI-SearchBot`, `ClaudeBot`, `PerplexityBot` | silent exclusion from three of four engines |
| One canonical page per paper, no duplicate titles across our own surfaces | Scholar's documented duplicate-title drop |
| Claim text identical across page, README and model card | corroboration fragmenting through drift |

That last one is the interesting structural test: it enforces "say it the same way"
mechanically instead of by discipline.

## C. Claim fidelity — a diagnostic, not an experiment

**C does not need to be an experiment to be useful.** Asked as "which of my papers
are currently described wrongly?", it produces a ranked worklist, actionable
regardless of attribution.

Method: for each paper with a sidecar, ask each engine *"What did <paper> find, and
under what conditions does it hold?"* and score against the sidecar's `claims` — 2 =
claim and scope correct, 1 = claim correct and scope dropped or overstated, 0 = claim
wrong or attributed to the wrong finding. **The 1s are the interesting cell.** That
is the documented failure mode and the thing the sidecar is actually for.

Grade with a model against the sidecar, then hand-check a stratified 20%: the grader
is the instrument and needs its own validation before its output means anything. Run
it on the top 20 papers, monthly. The output is a list of papers to fix, not a
p-value — a paper that scores 0 repeatedly is a concrete bug in how the work is
represented, worth chasing independent of any theory about why.

## B. The causal question, and why the arithmetic kills it

Randomising at the paper level — sidecar half the corpus, hold half back — does not
survive a power calculation. Suppose the base rate of "your paper is cited in the
answer" is 15% and the treatment lifts it to 25%, a large effect at +67% relative.
With 65 papers per arm:

```
pooled p = 0.20,  SE = sqrt(2 · 0.2 · 0.8 / 65) = 0.070
z = 0.10 / 0.070 = 1.43        ->  power ≈ 30%
n needed for 80% power         ≈  250 papers per arm
```

**Underpowered by about 4×, for an effect larger than anyone should expect.**

Counting (paper × question × engine) triples does not rescue it. Whether a paper gets
cited is overwhelmingly a *paper-level* property, so intra-cluster correlation is
high: at 16 observations per paper and ICC ≈ 0.5 the variance inflation is
`1 + 15(0.5) = 8.5`, and the effective sample size collapses back to roughly the
number of papers.

| Objection | Verdict |
|---|---|
| Can't compare to the past — AI search barely existed then | **Correct.** No usable historical baseline; only same-session comparisons work |
| Papers differ too much to compare to each other | **Correct in practice.** Randomisation handles it in expectation, but not at n=65 |
| Compare to other authors? | **Fatal.** Author prominence dwarfs any metadata effect. Do not attempt it |

### The one design where the confounds cancel

**Move the randomisation below the paper.** Write sidecars for *every* paper — you
want them regardless — but have each sidecar's Q&A block cover only a **random half
of that paper's questions**, then compare `cited` on covered vs uncovered questions
**within the same paper**.

Paper prominence, citation count, venue, topic, year and the whole "me factor" are
identical across arms, so they difference out instead of needing to be balanced. The
unit is a question: ~113 papers × 6 questions ≈ 678 questions, ~339 per arm, with the
contrast taken within cluster. Nothing is withheld permanently — you add the
uncovered questions afterwards. And **spillover biases toward null**, since an
uncovered question may still be helped by the page existing, which makes the estimate
conservative: the right direction for a bet you might want to believe.

Honest assessment: this is powered for something like a 7–10 percentage-point
within-paper difference, not for a subtle one. It is the only version worth
reporting, and it is nearly free because the sidecars are work you want anyway. If
that does not clear your bar, **skip B** — choosing not to run a study that would be
uninterpretable is a right call, not a gap.

### What the experiment costs, if the treatment works

The naive cost — "half the questions uncovered for the duration" — sounds like
forfeiting half the benefit, and is not, for four reasons. Only the marginal layer is
withheld: every paper still gets its page, JSON-LD, links map, abstract, canonical
claim sentence and misreadings, and the randomised element is only *which questions
get explicit Q&A coverage*. Spillover means the control arm is partial-treatment,
not zero. It is a delay rather than a forfeit — you add the rest afterwards, and
against papers with 5–20 year lifespans a one-quarter delay is a rounding error. And
it rides a rollout that is happening anyway: sidecars get written incrementally over
months regardless, so partial coverage exists whether or not you call it an
experiment.

Put a number on it: ~113 papers × ~4 months × half coverage ≈ 226 paper-months of
half-coverage against a corpus lifetime on the order of 14,000 paper-months. **Under
2% of lifetime coverage, and recoverable.**

The real costs are elsewhere:

| Cost | Size |
|---|---|
| Measurement labour | The dominant one. 2 rounds × ~678 questions × 4 engines, and two engines have no API for this — manual runs or a browser harness. Tens of hours, or a build |
| Discipline | Recording the assignment and not back-filling early. Cheap but easy to fumble |
| **Mis-reading a null** | The real hazard. At ~50% power a null is weak evidence, and it would be easy to conclude "sidecars don't work" when the honest statement is "no *large* effect detected" |

The payoff if it does not work: you stop writing sidecars for 113 papers (~19 hours)
and stop maintaining them indefinitely, and you redirect that effort to the
third-party-mention layer where the observational evidence is better. That asymmetry
is what makes a cheap version worth it.

**Recommendation.** Run a deliberately reduced version: randomise question coverage
on the **top ~40 papers only** — the ones you would sidecar first anyway — for two
rounds, and treat it as a go/no-go pilot rather than an estimate. Powered for roughly
a 12–15pp difference, so it detects "this clearly helps" and nothing subtler.
Pre-commit in writing to reading a null as *no large effect*, not *no effect*. If even
that feels like overhead, skip it; the cost of skipping is that the sidecar layer
stays an honest bet, which is a defensible position to hold in public.

**Free second contrast, no extra work:** sidecars roll out over time anyway, so
randomise the *order within each citation tier* instead of strictly by citation
count. You still do high-citation papers early, and you get contemporaneous
treated/untreated pairs matched on tier — a stepped-wedge design for the price of
shuffling a list.

### If you skip B

Then the honest framing of the whole project is: the identity and metadata work rests
on platform documentation and directly measured gaps and needs no experiment. The
pages, sidecars and Q&A are a **bet on a plausible mechanism**, held because it is
cheap and because its secondary payoff — fidelity, measured by C — is real and
separately checkable. Say that in public rather than implying a result nobody has.

## Cheap instruments worth adding regardless

- **Crawler hits.** Cloudflare in front of the site would show `GPTBot`,
  `ClaudeBot`, `PerplexityBot` and `OAI-SearchBot` by user-agent — the earliest
  possible signal that a page was noticed, weeks before any answer cites it. Highest
  value per unit of effort on this list; GitHub Pages gives no logs.
- **Referrer analytics** — **built**, off by default. Referrals from `chatgpt.com`,
  `perplexity.ai`, `claude.ai` are ground truth that an AI answer sent a human here.
  AI answers frequently are not clicked, so a rise is evidence and a flat line is
  uninformative. Set `site.analytics.provider` in `config.yaml` to one of `plausible`,
  `goatcounter`, `umami` or `ga4` and the snippet goes on every page; the first three
  set no cookies, `ga4` does.
- **Scholar / S2 / OpenAlex counters over time.** Already collected. Slow, heavily
  confounded, not attributable — useful as a tripwire that something broke, not as an
  outcome.
