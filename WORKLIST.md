# What still needs a human

Regenerate with `python update.py`. Ordered by leverage.

## Once-only identity fixes

Run `python scripts/identity_tasks.py` first -- it writes the payload for each
of these into `tasks/` -- committed, so browsable on GitHub. Every one is
blocked on a logged-in account you own, not on knowing what to do.

### 1. Populate ORCID  — do this one first

`0000-0002-0085-6496` currently lists **0 works**. This is the highest-leverage
item on the page, because it is also the lever for the other three: Semantic
Scholar's disambiguation uses ORCID, and OpenAlex is actively running
ORCID-driven merges of split profiles. Fixing ORCID makes both of those more
likely to fix themselves, and keeps them fixed.

Order matters, and the docs are easy to misread:

1. **Turn on auto-update** for Crossref and DataCite — *Works → Search &
   link*, authorise both, grant standing permission. Covers only works whose
   deposited metadata already carries your iD, so this fixes the *future*.
   Published DOIs are Crossref; arXiv DOIs are DataCite — you want both.
2. **Link your arXiv account to ORCID** —
   <https://arxiv.org/user/confirm_orcid_id>. This is what puts your iD into
   arXiv's DataCite metadata, which is what makes step 1 work on future
   preprints.
3. **Fill the backlog.** *Add DOI* is the reliable route: it resolves
   server-side against Crossref/DataCite and creates a properly-sourced work.
   `tasks/orcid_dois.txt` has the 101 DOIs,
   citation-ordered, so stopping early still captures most of the value.
4. **Or bulk-import** `tasks/orcid_import.bib` via *Add works → Add BibTeX*.
   Less risky than it first appears: ORCID **groups works that share an
   identifier**, so a DOI-bearing entry merges with the registry copy when
   auto-update later finds it rather than showing as a duplicate. The file is
   split — DOI-bearing entries first, then the few without a DOI, which are
   the only ones with nothing to group on.

**If the wizards misbehave, that is expected, not you:** the *Crossref
Metadata Search* wizard is genuinely flaky and hangs. *Scopus* looks empty
because Scopus indexes little arXiv/ACL content and the wizard wants a Scopus
Author ID you may not have. **dblp has no connect button because dblp is not
an ORCID wizard** — it only ingests iDs harvested from publisher metadata and
the ORCID dump, and never pushes works out. Skip all three and use *Add DOI*
or the BibTeX import.

I cannot do this for you: writing to an ORCID record needs an OAuth token with
`/activities/update` scope, which only you can grant. The public API is
read-only.

### 2. Semantic Scholar — 46 papers on the wrong record

Claimed: <https://www.semanticscholar.org/author/41019330>  
Secondary: <https://www.semanticscholar.org/author/2283849613>

**Do we have to?** It is the single biggest retrieval loss on this page: every
Semantic-Scholar-backed tool — Elicit, Consensus, SciSpace, most literature
agents — resolves an author to one page, so each of them currently sees about
half your corpus and ranks both halves lower.

**Is there a way, given support ignored you?** Yes, and it does not need them.
There is no self-service *merge*, but a claimed page can pull papers across:

1. Open the claimed page → **Edit Author Page** → **Add Papers**.
2. Paste the paper's S2 URL, select it, choose *the author is correct, but the*
   *paper is missing from my author page*, Submit. ~24h to appear.
3. Repeat. `tasks/s2_merge.md` lists all of them citation-ordered with URLs,
   so stopping early still captures most of the loss.

Do **not** claim the second page as well — their docs prohibit holding two
claims, and it makes the split harder to undo later. If you want to chase
support again, the durable argument is the ORCID: quote it and ask them to
merge on that basis.

### 3. Create a Wikidata item

**Is this an acceptable use?** Yes. Wikidata's notability policy is not
Wikipedia's: criterion 2 admits any *clearly identifiable entity describable
with serious, publicly available references*, and criterion 3 admits items that
*fulfil a structural need* — which is exactly what an author item with an ORCID
and published papers is. Hundreds of thousands of researcher items exist,
mostly auto-created from ORCID and Crossref. Unlike Wikipedia there is no
prohibition on creating an item about yourself; the requirement is accuracy,
not distance. `tasks/wikidata.qs` therefore contains identifiers and
affiliations only — no claims about importance, nothing unsourced.

**What I need from you:** a logged-in Wikidata account. Then:

1. Log in at <https://www.wikidata.org>.
2. Open <https://quickstatements.toolforge.org/#/batch>, authorise it once.
3. Paste `tasks/wikidata.qs`, run it, and copy the new Q-number.
4. Put that Q-number in `config.yaml` → `ids.wikidata` and redeploy; it then
   appears in the site's `sameAs` array.

**Why it is not automatic:** Wikidata writes require an authenticated account,
and an unattended bot account needs community approval. Creating an item about
yourself should also be a decision you make knowingly rather than one a script
makes for you.

### 4. OpenAlex — 4 duplicate profiles

Lowest priority: the duplicates hold a handful of works between them against
140+ on the main profile, so this is tidying.

**Preferred route: do nothing here and fix ORCID.** OpenAlex disambiguation is
ORCID-driven and they are currently running ORCID-based merges of split
profiles, so this may resolve itself.

**If you want it now:** the *Fixing Author Profiles* form linked from
<https://help.openalex.org/hc/en-us/articles/27714298573719-Fix-errors-in-OpenAlex>
can merge profiles, set the display name, and remove wrong works.
`tasks/openalex_merge.md` has the exact profile IDs to paste.
`support@openalex.org` is the fallback.

## arXiv journal-ref missing (103 papers)

Scholar matches citations and merges preprint/published versions on exactly these fields. No write API -- one web form each, so do them by citation count.

- [ ] `2306.01708` (855 cites) -> Advances in Neural Information Processing Systems 36  <https://arxiv.org/abs/2306.01708>
- [ ] `2402.14992` (279 cites) -> Forty-first International Conference on Machine Lear  <https://arxiv.org/abs/2402.14992>
- [ ] `2412.03304` (181 cites) -> Proceedings of the 63rd Annual Meeting of the Associ  <https://arxiv.org/abs/2412.03304>
- [ ] `2104.08202` (167 cites) -> CoRR  <https://arxiv.org/abs/2104.08202>
- [ ] `1907.01752` (127 cites) -> 8th International Conference on Learning Representat  <https://arxiv.org/abs/1907.01752>
- [ ] `2204.03044` (120 cites) -> ArXiv  <https://arxiv.org/abs/2204.03044>
- [ ] `2211.05655` (119 cites) -> Proceedings of the 61st Annual Meeting of the Associ  <https://arxiv.org/abs/2211.05655>
- [ ] `2410.19735` (111 cites) -> International Conference on Learning Representations  <https://arxiv.org/abs/2410.19735>
- [ ] `2507.16806` (98 cites) -> The Fourteenth International Conference on Learning   <https://arxiv.org/abs/2507.16806>
- [ ] `2402.16842` (90 cites) -> Forty-first International Conference on Machine Lear  <https://arxiv.org/abs/2402.16842>
- [ ] `2405.17202` (83 cites) -> The Thirty-eighth Annual Conference on Neural Inform  <https://arxiv.org/abs/2405.17202>
- [ ] `2301.11796` (82 cites) -> CoRR  <https://arxiv.org/abs/2301.11796>

## Hugging Face paper page missing (47)

Reflects the last `collect.py` run -- re-run it before working this
list or you will redo what you already did.

`python scripts/hf_papers.py` writes a clickable list to
`build/hf_worklist.html`. An unauthenticated visit creates nothing
(verified: 0 of 50), so log in to Hugging Face first, then click
through. Afterwards: `python scripts/hf_papers.py --verify`.

- [ ] <https://hf.co/papers/2410.19735>  (111 cites)
- [ ] <https://hf.co/papers/1907.08971>  (77 cites)
- [ ] <https://hf.co/papers/2302.04863>  (71 cites)
- [ ] <https://hf.co/papers/1911.10763>  (70 cites)
- [ ] <https://hf.co/papers/1804.04012>  (70 cites)
- [ ] <https://hf.co/papers/2109.06096>  (41 cites)
- [ ] <https://hf.co/papers/1903.02953>  (38 cites)
- [ ] <https://hf.co/papers/1804.11254>  (38 cites)
- [ ] <https://hf.co/papers/1804.03824>  (36 cites)
- [ ] <https://hf.co/papers/1804.11225>  (35 cites)

## Hugging Face page indexed but not claimed by you (27)

Claims need admin approval, so a request you have already submitted
still shows here until it is validated -- your name will have no
linked user until then. Re-run `collect.py` before assuming one
failed.

- [ ] <https://hf.co/papers/2504.08165>  (232 cites)
- [ ] <https://hf.co/papers/1907.01752>  (127 cites)
- [ ] <https://hf.co/papers/2211.05655>  (119 cites)
- [ ] <https://hf.co/papers/2507.16806>  (98 cites)
- [ ] <https://hf.co/papers/2412.05149>  (62 cites)
- [ ] <https://hf.co/papers/2404.00459>  (46 cites)
- [ ] <https://hf.co/papers/2502.10645>  (33 cites)
- [ ] <https://hf.co/papers/2412.06540>  (26 cites)
- [ ] <https://hf.co/papers/2410.11840>  (22 cites)
- [ ] <https://hf.co/papers/2503.01622>  (21 cites)

## Sidecars not written (134/135)

The one input no tool can supply: claims, scope conditions, terminology, common misreadings. ~10 min each; do them by citation count.

- [ ] `data/sidecars/tinybenchmarks-evaluating-llms-with-fewer-examples.md`  (279 cites) tinyBenchmarks: evaluating LLMs with fewer examples
- [ ] `data/sidecars/active-learning-for-bert-an-empirical-study.md`  (244 cites) Active Learning for {BERT:} An Empirical Study
- [ ] `data/sidecars/findings-of-the-b-aby-lm-challenge-sample-efficient-pretrain.md`  (232 cites) Findings of the {B}aby{LM} Challenge: Sample-Efficient P
- [ ] `data/sidecars/global-mmlu-understanding-and-addressing-cultural-and-lingui.md`  (181 cites) Global {MMLU}: Understanding and Addressing Cultural and
- [ ] `data/sidecars/an-autonomous-debating-system.md`  (172 cites) An autonomous debating system
- [ ] `data/sidecars/q-2-evaluating-factual-consistency-in-knowledge-grounded-dia.md`  (167 cites) Q\({}^{\mbox{2}}\): Evaluating Factual Consistency in Kn
- [ ] `data/sidecars/on-the-weaknesses-of-reinforcement-learning-for-neural-machi.md`  (127 cites) On the Weaknesses of Reinforcement Learning for Neural M
- [ ] `data/sidecars/fusing-finetuned-models-for-better-pretraining.md`  (120 cites) Fusing finetuned models for better pretraining
- [ ] `data/sidecars/disentqa-disentangling-parametric-and-contextual-knowledge-w.md`  (119 cites) DisentQA: Disentangling Parametric and Contextual Knowle
- [ ] `data/sidecars/model-merging-with-svd-to-tie-the-knots.md`  (111 cites) Model merging with SVD to tie the Knots

## Repo labels awaiting your review (30/31)

Check `data/repos.yaml`, fix anything wrong, set `reviewed: true` to freeze it, then `python scripts/sweep_github.py diff`.

