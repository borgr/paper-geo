# The papers track

135 papers. Read [SHARED.md](SHARED.md) first — this file only covers what is
specific to papers.

## What makes this track different

| | Papers | Repos |
|---|---|---|
| Retrievable unit | a **claim** | a **how-to** |
| Query shape | citation-shaped: "what's the method for X" | question-shaped: "how do I X" |
| Who owns the surface | arXiv, the publisher, the indexes — **not you** | you, entirely |
| What "correct" means | faithful to what the paper actually showed | the instructions work |
| Cadence | once per paper, at publication, then frozen | continuous |
| Automatable share | metadata: high. Claims: zero | high |

The consequence that shapes everything: **you don't control the surfaces that
matter most.** arXiv, ACL Anthology, and Scholar hold the canonical records, and
your only levers there are (a) getting their metadata right and (b) publishing a
page you *do* control that they can link to.

## Rule 1: metadata correctness is not cosmetic

Scholar's parser is fully automated with no human correction. Its own docs are
explicit that wrong bibliographic data means "(incorrect) bibliographic data
would not match (correct) references to them from other papers" — which lowers
ranking and can drop the paper. One documented failure mode: a venue name
extracted as a title makes papers vanish as presumed duplicates. We have a live
instance of that (`"Journal of Memory and Language"` as a paper title, now in
`overrides.yaml` → `drop`).

The governing principle, from those docs: present the article **as it would
normally be cited in the References section of another paper.**

**103 of 109 arXiv records have no journal-ref.** That is this track's largest
single gap. arXiv has no write API, so it's one web form each — do them by
citation count, from [`WORKLIST.md`](../WORKLIST.md).

## Rule 2: every paper needs an HTML surface

A PDF-only paper is retrievable in P2 (Scholar parses PDFs) and near-invisible in
P1. Current state: **109/135 have one, 46 of those only via ar5iv** (pre-2024
papers have no `arxiv.org/html/`). 26 papers have no arXiv id at all and so no
HTML surface — those are the ones your own site page matters most for.

`links.html` in [`papers.yaml`](../data/papers.yaml) resolves to the arXiv
rendering when it exists and the ar5iv fallback when it doesn't.

## Rule 3: the `links` map is the identity of the work

One paper is five to twelve URLs. An engine either treats them as one work with
many locations or as many unrelated pages; a `sameAs` array is what decides.

Derived on every run from identifiers (never stored by hand): `arxiv`,
`arxiv_pdf`, `html` (+ `html_source`), `huggingface`, `alphaxiv`, `doi`,
`acl_anthology`, `semantic_scholar`, `publisher`, `code`.

Hand-supplied, via the sidecar's `links_extra`: project page, talk video, slides,
poster, leaderboard, blog post, dataset, demo. These can't be derived and are
often the highest-value ones.

## Rule 4: publish the citation verbatim

`papers.yaml` carries `bibtex` copied byte-for-byte from `enhanced.bib` rather
than regenerated from parsed fields. A regenerated key would differ from the one
people have already cited, and §5 of SHARED.md applies to citation strings too:
one canonical form everywhere beats a tidier one. 118/135 captured; the rest are
S2-only records with no bib entry yet.

## Rule 5: the sidecar is the only thing no tool can write

One file per paper, `data/sidecars/<slug>.md`. ~10 minutes. This is the part that
targets **fidelity** rather than visibility — and fidelity is the real problem for
work that is already well known. LLM summaries overstate scientific conclusions
about 5× more often than human ones; a paper that ships its own claims and scope
is the only paper that gets represented correctly.

```yaml
---
key: yadav2023ties
coined: TIES-Merging
gloss: merging fine-tuned models by trimming, electing signs, and averaging
one_liner: >
  TIES-Merging combines independently fine-tuned models into one by resolving
  parameter-sign conflicts, outperforming task arithmetic across 11 tasks.

# Question/answer pairs. See "On questions vs answers" below -- the answer is a
# claim id, never a paraphrase.
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

### On questions vs answers

**Questions alone would be actively harmful.** A retrieved passage containing a
question with no answer matches the query and then fails the selection stage —
the study's gatekeeper is that the concrete answer is *present in the chunk*. You
would win retrieval and lose the citation, which is the worst of the two.

So: **question and answer adjacent, always.** But the two get opposite treatment:

| | Paraphrase? | Why |
|---|---|---|
| **Questions** | **Yes, deliberately — 2–4 phrasings** | Engines fan a query out into many synthetic sub-queries. Lexical retrieval needs the words people actually use, and you can't guess which phrasing wins. This is the cheapest real lever in the whole track. |
| **Answers / claims** | **No, never** | A paraphrase creates a second slightly-different version of your own claim. That fragments corroboration (SHARED.md §5) and lets the two drift apart over time. |

Hence the schema: `q` is a list of phrasings; `answers` is a list of claim **ids**.
The renderer emits each claim's text verbatim under each of its questions. The
same claim appears under several questions — that's intended, and it is
repetition of one canonical string, not paraphrase.

Is any of this in the "confusing / measured null" domain? Partly, and worth being
precise: the *FAQ markup* is cosmetic (formatting was measured null). The *Q&A
adjacency* and the *multiple question phrasings* are topic-match and
query-term-coverage, which are among the strongest measured effects. Same block
of text, two different claims about it — one weak, one strong.

### Drafting a sidecar

- Claims must survive isolation. Name the object, the finding, and the magnitude
  in one sentence. No pronouns pointing outside the sentence.
- Scope is the content, not a disclaimer. Name the populations, models, and
  conditions the claim does and doesn't reach. Boilerplate ("further research is
  needed") is worthless.
- A model can draft; only the author can rank which limitation actually binds.
  Draft `claims` and `misreadings`, then hand back for correction.
- Do **not** strip legitimate caveats to sound confident. The measured preference
  for confident language over hedged is the one place the incentive gradient
  points away from good science. The honest version is precise claims plus
  explicit scope — not vague hedging, and not false certainty.

## Rule 6: pages, once the generator lands

Per paper at `borgr.github.io/papers/<slug>/`, generated from `papers.yaml` +
sidecar:

1. `ScholarlyArticle` JSON-LD — authors with ORCID `@id`s, venue, date, DOI, the
   full `links` map as `sameAs`, `codeRepository`, `dataset`.
2. Highwire meta tags — `citation_title`, one `citation_author` per author,
   `citation_publication_date`, `citation_conference_title`, absolute
   `citation_pdf_url` in the same subdirectory. All three mandatory ones or
   Scholar ignores the lot.
3. Visible abstract, no gate, plus a reference list under a literal `References`
   heading (Scholar's PDF-layout fallback rules).
4. The Q&A block, the claims with scope, terminology, misreadings.
5. `rel=canonical` to itself; the sidecar in the repo is source, not a competitor.
6. Flagship results as CSV next to the figure — an LLM handed a PNG of a
   regression table sees pixels.

## Priority order

1. Identity fixes (SHARED.md §2) — once, hours, largest effect
2. arXiv journal-refs by citation count — 103 forms, mechanical
3. HF paper pages: index the 50 missing, claim the 24 unclaimed
4. Site generator + thin pages for all 135
5. Sidecars for the top 20 by citation, then onward
