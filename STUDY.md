# Machine visibility for research output: study + playbook

Two parts: (1) what is actually known about how machines find, retrieve and cite
content, including what transfers from commercial SEO/GEO and what does not;
(2) a concrete, mostly-automatable playbook for one researcher's corpus, grounded
in an audit of the real current state (122 papers).

Evidence grading used throughout: **[A]** controlled experiment or authoritative
platform documentation · **[B]** large observational study · **[C]** vendor-stated
or practitioner claim, directional only.

---

## Part 1 — Study

### 1.1 There is no single "index". There are three, and they behave differently.

Almost all confusion in this area comes from collapsing three separate pipelines
that have separate entry conditions. Every action below should be attributed to
one of them.

| | Pipeline | How your work enters | Latency | What wins |
|---|---|---|---|---|
| **P1** | **Web/crawl retrieval** — Google, Bing (→ ChatGPT), Brave (→ Claude), Perplexity's own crawler, Google AI Mode/Overviews | An HTML page a crawler can fetch and parse | days–weeks | crawlable HTML, topic match, freshness, structured data, being in the top-10 of the underlying index |
| **P2** | **Scholarly graph retrieval** — Google Scholar, Semantic Scholar/S2AG, OpenAlex, Crossref, DBLP, ACL Anthology. This is what Elicit, Consensus, SciSpace, Scholar's own AI features, Primo Research Assistant, and nearly every LLM literature agent call | Correctly-parsed bibliographic records + resolvable identifiers | weeks–months | metadata correctness, identifier linkage, author disambiguation, abstract presence |
| **P3** | **Model weights** — what the model "knows" with no retrieval | Being in the pretraining corpus, and being *talked about* enough that the association is learned | 6–24 months, one-way | volume and consistency of third-party mentions; presence in high-weight corpora (Wikipedia, GitHub, arXiv, Common Crawl) |

Practical consequences:

- **P1 fixes are fast and fully under your control.** P2 fixes are slow but
  compound and are the ones that matter for research audiences. P3 is not
  directly actionable per paper; it is a by-product of P1+P2 plus other people
  writing about the work.
- **Being invisible in one pipeline is invisible-shaped in all of them.** A paper
  that only exists as a PDF is retrievable in P2 (Scholar parses PDFs) but weak
  in P1 (no HTML page to cite) and contributes little to P3.
- ChatGPT's web search runs on Bing, Claude's on Brave, Perplexity on its own
  ~5B-URL index with Bing fallback, Gemini/AI Mode on Google's index **[C,
  consistent across several independent write-ups]**. Optimizing only for
  Google leaves three of four engines unaddressed — and note that arXiv, GitHub,
  Hugging Face and ACL Anthology are well-covered in *all* of these, whereas a
  personal Wix subdomain may not be.

### 1.2 What the GEO literature actually establishes

**Aggarwal et al., "GEO: Generative Engine Optimization", KDD '24
(arXiv:2311.09735)** — 10K queries, GEO-bench, validated on live Perplexity.
Tested nine content edits against a baseline. Ranked by measured lift **[A]**:

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

Three findings matter more than the ranking:

1. **The winning edits are exactly the ones good scientific writing already
   rewards**: quote your sources, give numbers, cite, write fluently. There is no
   tension between GEO and scholarly quality here.
2. **Keyword stuffing actively hurts.** Every "SEO trick" instinct is
   counterproductive against generative engines.
3. **GEO helps low-ranked sources far more than top-ranked ones.** When all five
   retrieved sources were optimized, the rank-5 source gained **+115%** while
   rank-1 *lost* 30%. Content optimization is a lever for the source that is
   retrieved-but-ignored, not for the one already winning.

**Vishwakarma et al., "What Gets Cited: Competitive GEO in AI Answer Engines",
SIGIR '26 (arXiv:2605.25517)** — 252,000 trials, 6 models, matched-pair design
with position counterbalancing and a logistic GLMM. The strongest causal evidence
in this area **[A]**, though its corpus is consumer product reviews, so transfer
to scholarly content is an assumption, not a result.

Its central structural claim is the useful one — factors are **not** additive:

- **Four gatekeepers** (significant in all 6 models, odds ratios >100): **topic
  match**, **presence of the specific concrete fact the query asks for** (their
  domain: price), **recent timestamp**, **being first in the candidate list**.
  Failing any one of these can zero out citation odds no matter how good the rest is.
- **Seven differentiators** (OR ≈ 2–240): query-term coverage, specifications /
  concrete detail, comparisons against alternatives, evidence for claims,
  internal consistency, depth of coverage, strong social proof.
- **Seven factors with no consistent effect.** Notably **content structure
  (sectioned vs. dense prose) had no measurable effect** — the authors conclude
  models parse text regardless of visual organization, and they explicitly
  **deprioritize formatting work as low-return**. This directly contradicts most
  commercial AEO advice.

Two of its findings deserve explicit ethical flagging for scientific use:

- "Confident vs. hedged" language had ORs of 599 (Gemini) and 754 (Claude).
  Taken naively this says: strip your caveats. **Do not do this.** The defensible
  version is: state what you *did* find precisely and unhedgedly, and put scope
  conditions somewhere structured and machine-readable rather than dissolving
  them into the prose — which is what §1.5 is about. This is also the one place
  where the incentive gradient of AI retrieval points away from good science, and
  worth saying out loud in public.
- Recency bias is strong (recent vs. 2019 timestamp: OR >10,000 in 4 of 6
  models). For a paper this is largely fixed, but it argues for keeping a dated,
  updated landing page per line of work rather than relying on the original
  paper's date alone.

### 1.3 What commercial GEO/AEO practitioners do — and what transfers

Stripping the vendor material down to mechanisms:

| Practice | Transfers to papers? |
|---|---|
| Answer-first, self-contained 200–400 token passages **[C]** | **Yes, cheaply.** Not because of "chunking magic" (the SIGIR paper found structure ≈ no effect) but because a self-contained passage survives being retrieved *alone*, without its surrounding context. |
| Entity establishment: Wikidata item → `sameAs` → Knowledge Graph **[C]** | **Yes.** Wikidata needs no notability, is free, takes minutes, feeds Google's KG and is a high-weight corpus for P3. Reported correlation of brand mentions with AI-Overview visibility 0.664 vs. 0.218 for backlinks **[C, vendor-chained — directional only]**. |
| `llms.txt` as a *protocol* | **No.** Google confirmed (June 2026) it has zero effect on Search or AI Overviews; no major AI platform commits to parsing it. Treat protocol-`llms.txt` as dead. |
| `llms.txt` as a *content artifact* | **Yes** — see §1.5. The academic version is not a crawler directive, it is an author-written orientation document. Different thing wearing the same name. |
| Schema.org JSON-LD (`ScholarlyArticle`, `Person`, `Dataset`, `sameAs`) | **Yes.** Cheap, generated, and the `sameAs` array is the only place you can *assert* your own identity graph. |
| Being on high-citation-share domains | **Yes, and this is the big one.** Citation share in AI answers is hyper-concentrated: Wikipedia, Reddit, YouTube, LinkedIn, GitHub dominate; the top ~15 domains take ~68% of consolidated share **[B, multiple independent studies, ~150K–680M citations]**. |
| Robots/CDN not blocking `GPTBot`, `ClaudeBot`, `PerplexityBot`, `OAI-SearchBot` | **Yes** — pure downside risk, worth a one-time check. |
| Keyword density, backlink building, formatting churn | **No.** Measured null or negative. |
| Hidden text / prompt injection aimed at LLM reviewers or rankers | **Off-limits.** There have already been retraction-level scandals over hidden prompts in manuscripts. Anything that only works because a human can't see it is out of scope. |

The single most important transfer: **for a general-audience AI answer, the
paper's PDF is rarely the cited artifact — the GitHub README, the Wikipedia
paragraph, the HF model card, or someone's blog post is.** Optimizing the paper
alone optimizes the least-cited surface in the ecosystem.

### 1.4 The scholarly pipeline (P2): the mechanics that actually gate you

From Google Scholar's own inclusion guidelines **[A — authoritative]**, the
non-obvious parts:

- Scholar's parser is **fully automated with no human correction**. Misparsed
  bibliographic data doesn't just look bad — it means "(incorrect)
  bibliographic data would not match (correct) references to them from other
  papers", which **lowers ranking** and can drop the paper. A stated failure
  mode: if a repository or venue name gets extracted as the *title* across many
  papers, those papers can vanish entirely as presumed duplicates.
- The governing principle for metadata: present the article "**as it would
  normally be cited in the References section of another paper**" — venue name,
  volume/issue, first page. This is why an arXiv record with no journal-ref is a
  real (not cosmetic) problem: it starves the version-matching that merges your
  arXiv and proceedings versions into one ranked cluster.
- Highwire Press meta tags (`citation_title`, `citation_author`,
  `citation_publication_date`) are preferred; **all three are mandatory** or the
  page is processed as if it had no tags at all. Dublin Core is a "last resort".
- `citation_pdf_url` must be absolute and the PDF must live **in the same
  subdirectory** as the HTML abstract, or the PDF is indexed as a tagless
  standalone document.
- For a self-hosted PDF with no meta tags, layout *is* the metadata: title in
  ≥24pt at the top, authors 16–23pt directly beneath, a citation line in the
  first-page header/footer, a section literally headed "References" or
  "Bibliography", and **no Type 3 fonts**.
- Abstract or full text must be visible **with no interstitial, no login, no
  scroll, no click**.
- One paper per URL. Update latency for already-indexed papers: **6–9 months.**

The other graph nodes and what each one feeds:

- **ORCID** — the canonical author identity. Feeds OpenAlex name variants and
  most publisher pipelines. Auto-populates via Crossref/DataCite Search & Link
  wizards plus standing auto-update permissions. arXiv can be linked to it and
  says it will "use ORCID iDs in preference to internal arXiv author
  identifiers" **[A]**.
- **Semantic Scholar / S2AG** — feeds Elicit, Consensus, SciSpace, S2ORC, and
  most LLM lit-search agents. Author pages are generated by an automated
  disambiguation model (S2AND) and **split on similar-name/coauthor-cluster
  boundaries**. There is no self-service merge; claiming the page is the
  documented remedy, and you must **not** claim two pages **[A]**.
- **OpenAlex** — open, widely mirrored, ORCID-driven for name variants. Actively
  merges duplicates in bulk but accepts corrections.
- **DBLP / ACL Anthology** — hand-curated, high-precision, well-crawled. Strong
  in this field specifically.
- **Hugging Face Papers** — the successor to Papers with Code (shut down July
  2025). Any arXiv paper can be indexed by visiting `hf.co/papers/<arxiv-id>`;
  authorship can be **claimed** and verified; and any model/dataset/Space whose
  README links the arXiv URL is auto-tagged and cross-listed on the paper page
  **[A — HF docs]**. This is now the main paper↔artifact join surface in ML.
- **arXiv HTML** (LaTeXML, since Dec 2023) — gives every post-2023 paper a
  crawlable HTML page. Pre-2024 papers have **no** `arxiv.org/html/` version,
  but `ar5iv.labs.arxiv.org/html/<id>` covers them.
- **arXiv abstract-page hooks** — `Links to Code` (CatalyzeX), alphaXiv, Hugging
  Face, DagsHub, ScienceCast, Connected Papers, scite. Free surfaces you can
  populate.

### 1.5 The machine-readable-science movement (the interesting frontier)

Two 2026 proposals are the intellectually serious version of "GEO for papers",
and both converge on the same idea: **the missing artifact is author intent, not
better parsing.**

**Goldsmith-Pinkham, "LLM-Friendly Academic Papers" (Mar 2026)** proposes a
per-paper `llms.txt` plus a "paper bundle". The `llms.txt` is plain markdown,
author-curated, seven suggested sections: what the paper is about (*not* the
abstract), important context and misconceptions, data/methods fingerprint, key
results, **limitations and scope**, a navigation guide, publication status. The
bundle adds `paper.md` (via `pandoc paper.tex -o paper.md`), figures, **tables as
CSV/markdown never images**, code with `reproduce.sh` and pinned deps, and
`references.bib`.

The argument for why parsing improvements can't substitute: even flawless text
extraction "cannot indicate which results are central, which caveats bind, or
what a term of art means in context." Motivating evidence: LLM summaries were
~5× likelier than human ones to overstate scientific conclusions (Peters &
Chin-Yee 2025); 74.9% of 20,000 scholarly PDFs met no accessibility criteria
(Kumar & Wang 2024). The minimum viable version is explicitly **"two paragraphs
on what the paper shows and doesn't, posted with the PDF — fifteen minutes."**

**Booeshaghi et al., "Science should be machine-readable" (bioRxiv, Feb 2026)**
goes further, representing papers as structured claim sets — their OpenEval
extracted ~112 claims per paper. Direction of travel: the unit of scientific
retrieval becomes the claim, not the paper. If that lands, papers that ship their
own claim list are the ones represented correctly.

**Why this matters more than ordinary GEO:** it targets *fidelity*, not just
visibility. The failure mode for a well-known paper isn't being unfindable — it's
being findable and then described wrongly (overstated, mis-scoped, credited to
the wrong sub-claim). Publishing your own claims + scope conditions is the only
lever on that, and it's a lever no index or publisher can pull for you.

---

## Part 2 — Audit of the actual current state

Measured, not assumed. Corpus assembled from both Semantic Scholar author
records; 122 unique papers; run `audit.py` in this directory to reproduce.

```
papers                             122
  split across S2 records A / B    72 / 50      ← two profiles, one person
  no abstract in S2                14/122 (11%)
  with arXiv id                    102/122 (84%)
  arXiv: NO journal-ref            96/102 (94%)
  arXiv: NO DOI field              97/102 (95%)
  arXiv: NO HTML rendering         41/102 (40%)
  HF paper page missing            47/102 (46%)
  HF page w/ 0 claimed authors      7/102  (7%)
```

Identity-graph state:

| Node | State | Consequence |
|---|---|---|
| **Semantic Scholar** | **Two author pages**: `41019330` (73 papers, 3,610 cites, h=31, homepage set → claimed) and `2283849613` (52 papers, 1,060 cites, h=14, unclaimed) | Every S2-backed tool (Elicit, Consensus, SciSpace, most lit-search agents) sees **either** the merging/BabyLM/NLP-eval half **or** the benchmarks/scaling-laws/LoRA half. Author-level retrieval is halved; both halves under-rank. Highest-leverage single fix in the audit. |
| **ORCID** `0000-0002-0085-6496` | Exists, **0 works** | The canonical identifier asserts nothing. Downstream disambiguation has nothing to anchor on. |
| **OpenAlex** | 1 main record (143 works) **+ 4 duplicate records** (8 works total) | Minor leakage; trivially fixable. |
| **Wikidata** | **No author item. No paper items** (checked TIES-Merging, BabyLM Findings, tinyBenchmarks) | No entity anchor in the KG, no `sameAs` target, absent from a high-weight P3 corpus. Zero notability requirement to fix. |
| **DBLP** | 166 hits, well-curated | Healthy. |
| **ACL Anthology** | Person page exists | Healthy. |
| **Google Scholar** | 5,829 cites, h=38, i10=74 (per `publications/profile_stats.json`) | Healthy; the public-facing number is fine. The problem is everything downstream of it. |

Web surfaces:

- **`ktilana.wixsite.com/leshem-choshen`** — the canonical homepage per S2, ORCID,
  LinkedIn and GitHub. robots.txt is permissive (fine), but: it's a
  `wixsite.com` subdomain (no domain authority of its own), `<html lang="he">`,
  **zero JSON-LD**, meta description is "NLP Publications, scientific interests
  and a surprise", and no per-paper pages. The one surface fully under your
  control is the least machine-readable one you own.
- **`borgr.github.io`** — live (200), contains `index.html` + a Google
  verification file, *already has* `Person` JSON-LD — but with
  `"email": "mailto:leshem@example.com"` (placeholder) and a Wix-hosted image.
  An unused, crawler-friendly, fully-controlled surface.
- **`github.com/borgr`** — 90 public repos, and **topics = 0 on every single
  one**. Several have `description: NONE`. **No `CITATION.cff` in any of 9
  flagship repos checked** (TextArena, ColPret, zipnn, DORA, USim, ewok-paper,
  every_eval_ever, paper-sharpener, publications). GitHub is a top-5 AI-cited
  domain and topics are its primary discovery facet.
- **`github.com/borgr/publications`** — **the key asset.** Already contains
  `fetch_citations.py` (Scholar → `citations.csv` + `profile_stats.json`),
  `resolve_arxiv.py` (arXiv → DBLP/ACL/S2 published BibTeX — i.e. it *already
  knows how to find the journal-refs that arXiv is missing*), `build_bib.py`,
  `enhanced.bib` **with abstracts**, and an Overleaf submodule. A full
  bibliography pipeline already exists; nothing below needs to be built from
  scratch.

Reading the audit as one sentence: **the scholarly-graph layer is in good shape
where someone else curates it (DBLP, ACL, Scholar) and broken wherever it depends
on you asserting your own identity (S2 split, empty ORCID, no Wikidata) — and the
web layer is almost entirely unbuilt despite the raw material sitting in a repo.**

---

## Part 3 — Playbook

Ordered by (leverage ÷ effort). "Per-paper" work is marked; everything else is
once-only.

### Tier 0 — once-only identity fixes (hours, highest leverage)

| # | Action | Why | Automatable |
|---|---|---|---|
| 0.1 | **Merge the two Semantic Scholar author pages.** Claim `41019330`; email support to merge `2283849613` into it (do *not* claim both — S2 docs prohibit it). Then use *Add Papers* for strays. | Restores author-level retrieval across every S2-backed AI research tool. Single biggest fix found. | Manual (one email); verification automatable |
| 0.2 | **Populate ORCID** from `enhanced.bib` — Crossref + DataCite Search & Link wizards, enable standing auto-update, link the arXiv account. | Anchors disambiguation for everything downstream. Prevents the S2 split recurring. | Semi: wizards are clickthrough; ORCID has a public API for bulk work import |
| 0.3 | **Create a Wikidata item** (`instance of: human`, occupation, employer, ORCID P496, official website P856, and `sameAs`-style ID properties for S2/DBLP/GitHub/Google Scholar). | Free, no notability bar, feeds Google KG, high-weight P3 corpus, and gives every JSON-LD `sameAs` array a real target. | Yes — QuickStatements from the bibliography |
| 0.4 | **Pick one canonical URL and make it `borgr.github.io`** (or a custom domain pointed at it). Fix the placeholder email, add a real `sameAs` array, `Person` + `ProfilePage` JSON-LD. Update the URL in ORCID, S2, LinkedIn, GitHub, arXiv. | GitHub Pages is static, fast, crawlable, versioned and diffable; Wix is a JS SPA on a shared subdomain. Consistent URL across nodes is what lets engines fuse the identity. | Yes — generated from the bib |
| 0.5 | **Verify no AI crawler is blocked** on whatever domain you end up on (`GPTBot`, `OAI-SearchBot`, `ClaudeBot`, `PerplexityBot`, `Google-Extended`). | Pure downside risk; 30 seconds. | Yes |
| 0.6 | **Merge the 4 duplicate OpenAlex author records.** | Small, cheap, prevents citation leakage. | Yes — OpenAlex correction API/form |

### Tier 1 — bulk metadata repair (one script, then per-paper on submission)

| # | Action | Why | Automatable |
|---|---|---|---|
| 1.1 | **Add journal-ref + DOI to all 96 arXiv records missing them.** `resolve_arxiv.py` already resolves published BibTeX from DBLP/ACL/S2 — pipe its output into arXiv's journal-ref field. | Scholar's version-matching and citation-matching run on exactly these fields; missing them depresses ranking and splits arXiv/proceedings versions. This is 94% of the arXiv corpus. | **Mostly.** Generation is automatable; arXiv's journal-ref update is a per-paper web form (no write API) — a few minutes each, batched, prioritized by citation count |
| 1.2 | **Index the 47 missing Hugging Face paper pages** (`hf.co/papers/<id>`), then **claim authorship** on all of them (also fixes the 7 indexed-but-unclaimed). Currently the `leshem` HF account shows `numPapers: 0`. | HF Papers is the post-PwC paper↔code↔model join surface, heavily crawled, and the discovery path for ML practitioners. | Yes for indexing (URL visit); claiming is one clickthrough each |
| 1.3 | **Backfill arXiv abstract-page hooks**: `Links to Code` (CatalyzeX) for every paper with a repo. | Free surface on the highest-authority page each paper has. | Semi |
| 1.4 | **Add `CITATION.cff` to every repo** (0/9 flagship repos have one) — GitHub renders a "Cite this repository" widget from it and it's machine-readable. | Bidirectional repo↔paper link, in a format machines read. | **Fully** — generate from `enhanced.bib`, commit via `gh` |
| 1.5 | **Add GitHub topics + real descriptions + homepage URL to all 90 repos** (currently 0 topics everywhere). | Topics are GitHub's primary discovery facet; GitHub is a top-5 AI-cited domain. | **Fully** — `gh api -X PUT repos/{r}/topics` |
| 1.6 | **Fill the 14 missing S2 abstracts.** | An abstract-less record is near-unretrievable in embedding-based search. | Semi |

### Tier 2 — the per-paper machine-readable layer (the real work)

Build `borgr.github.io/papers/<key>/` — one page per paper, generated from
`enhanced.bib` + a small hand-written YAML sidecar. Each page carries:

1. **`ScholarlyArticle` JSON-LD** — authors (with ORCID `@id`s), venue, date,
   DOI, `sameAs` → arXiv/S2/ACL/HF/GitHub, `citation` → key refs, plus
   `codeRepository` / `dataset` where relevant.
2. **Highwire meta tags** — `citation_title`, `citation_author` (one per author),
   `citation_publication_date`, `citation_conference_title`, `citation_pdf_url`
   (absolute, same subdirectory). Get all three mandatory ones right or Scholar
   ignores the lot.
3. **Visible abstract**, no interstitial, plus a **rendered reference list under a
   literal `References` heading** — Scholar's PDF-layout fallback rules.
4. **A per-paper `llms.txt`** in the Goldsmith-Pinkham sense — this is the
   irreplaceable, non-automatable content, and the highest-value 15 minutes per
   paper:
   - **Claims**: 3–6 numbered, self-contained, quotable claim sentences. Each
     must survive being retrieved *alone* — name the object, the finding and the
     magnitude in one sentence, no anaphora, no "we show that this improves".
   - **Scope and limitations**: the specific conditions under which the claim
     does and doesn't hold. This is the antidote to the 5× overstatement rate,
     and the honest answer to the "confident vs. hedged" incentive — precise
     claims, explicit scope, no vague hedging in either direction.
   - **Terminology**: terms of art you use in a non-obvious sense (e.g. what
     exactly "merging", "efficient benchmarking" or "sample-efficient" denote in
     *this* paper).
   - **Common misreadings** — what people wrongly conclude from this paper.
   - **Artifacts**: repo, model, dataset, leaderboard, with URLs.
   - **How to cite** (BibTeX inline).
5. **A site-level `llms.txt`** indexing all of them + a `sitemap.xml`.

Also: **`ar5iv` fallback links** for the 41 pre-2024 papers with no arXiv HTML,
and **tables as CSV** alongside the paper for the flagship results.

Per-paper cost: ~15 min of genuine thought for the claims/scope, ~0 min for
everything else once the generator exists. Do it citation-weighted — the top 20
papers are most of the value.

### Tier 3 — the surfaces that actually get cited

The citation-concentration data says this tier probably beats Tiers 1–2 for
general-audience AI answers, but it is the least automatable.

- **Wikipedia.** Model merging, benchmark evaluation, BabyLM/sample-efficient
  pretraining, scaling laws are all topics where a well-sourced paragraph citing
  the primary literature is a legitimate encyclopedic contribution. Wikipedia is
  the #1 cited domain in ChatGPT (47.9% of top citations in one study **[B]**)
  and a high-weight P3 corpus. Norms caveat: WP:COI — don't cite yourself into
  articles; write the topic honestly, propose on talk pages, or get the coverage
  written by others.
- **README-as-canonical-explainer.** For each flagship repo, the README should
  independently answer "what is this, what did it find, how do I use it" with the
  numbers in it. In practice the README, not the PDF, is what gets cited for
  method questions.
- **Model/dataset cards on HF** with the arXiv link in the README (auto-tags the
  paper page and cross-lists it).
- **One durable explainer post per line of work**, dated and updated. Recency
  bias is one of the four gatekeepers; a paper's date is frozen, a post's isn't.
- **Reddit/HN/Bluesky/LinkedIn** — high-citation-share domains. This is the
  "third-party corroboration" layer; the existing `social-follow` and
  `ATProto-links-bot` repos suggest the plumbing interest is already there.

### Explicitly not worth doing

- Protocol-level `llms.txt` expecting crawler behavior change (measured null).
- Keyword-density work in abstracts (measured *negative* in GEO-bench).
- Formatting/structure churn on pages (measured null in the SIGIR study; the
  authors deprioritize it by name).
- Backlink building (0.218 correlation vs 0.664 for mentions **[C]**).
- Any hidden text, prompt injection, or citation-bait. Norm-violating,
  retraction-adjacent, and not what this is for.

---

## Part 4 — Tooling design

Everything below extends `github.com/borgr/publications`, which already owns the
bibliography, the Scholar scrape, and the arXiv→published resolution.

```
publications/
  fetch_citations.py      # exists — Scholar → citations.csv, profile_stats.json
  resolve_arxiv.py        # exists — arXiv → DBLP/ACL/S2 published BibTeX
  enhanced.bib            # exists — with abstracts
  update.py               # exists — orchestrator
+ geo/
+   audit.py              # DONE (this dir): per-paper machine-visibility audit → audit.json
+   fix_github.py         # topics + descriptions + homepage + CITATION.cff for all 90 repos
+   arxiv_journalrefs.py  # emits a prioritized worklist of the 96 missing journal-refs,
+                         #   pre-filled from resolve_arxiv.py output, with the arXiv form URL
+   hf_papers.py          # index missing hf.co/papers pages; report unclaimed ones
+   orcid_push.py         # bulk-load works into ORCID via the public API
+   wikidata_qs.py        # emit QuickStatements for the author item + paper items
+   sidecars/<key>.yaml   # THE HAND-WRITTEN PART: claims, scope, terminology, misreadings
+   build_site.py         # enhanced.bib + sidecars → borgr.github.io/papers/**
+                         #   (JSON-LD, highwire tags, visible abstract+refs, llms.txt,
+                         #    sitemap.xml, ar5iv fallbacks)
```

**Two agentic skills** (natural home: the existing `paper-sharpener` repo, which
is already "code and skills for academic writing"):

1. **`/paper-geo <arxiv-id|bibkey>`** — for one paper: read the source (arXiv
   `/src/` tarball or the PDF), draft the sidecar YAML (claims, scope,
   terminology, misreadings) for human revision, generate the page + `llms.txt`,
   check the arXiv journal-ref, ensure the HF paper page exists, check the repo's
   topics and `CITATION.cff`, and report what still needs a human. Two-pass, as
   Goldsmith-Pinkham suggests: model drafts, author fixes the judgment calls —
   a model can report what a paper *says* about its limits but cannot rank which
   limit actually binds.
2. **`/paper-geo-audit`** — re-run `audit.py` monthly, diff against the last
   `audit.json`, and open issues only for regressions and for newly-posted papers
   (new paper → sidecar + HF page + journal-ref reminder once the venue is known).

**Suggested order of execution:** 0.1 → 0.2 → 0.5 → 1.4/1.5 (fully automatable,
one afternoon, visible immediately) → 0.3/0.4 → 1.2 → Tier 2 generator + top-20
sidecars → 1.1 batched by citation count → Tier 3 ongoing.

**Honest uncertainty.** Tier 0 and Tier 1 rest on authoritative platform
documentation and directly measured gaps — those will work. Tier 2 rests on a
plausible but untested transfer of consumer-product GEO findings to scholarly
retrieval, plus a 2026 proposal with no adoption data yet; its fidelity benefit
(being described *correctly* by models) is more defensible than its visibility
benefit. Tier 3 has the best observational evidence and the worst automatability.
Nothing here has a controlled study on *academic* content, because as far as this
survey found, nobody has run one — which is itself a paper-shaped hole, and one
this corpus is unusually well-positioned to fill.
