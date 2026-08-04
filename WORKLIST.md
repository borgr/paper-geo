# What still needs a human

Regenerate with `python update.py`. Ordered by leverage.

## Once-only identity fixes
- [ ] **Merge the 2 Semantic Scholar author records** into 41019330. Claim the primary, then email support to merge the others; do not claim two pages. Splits author-level retrieval across every S2-backed tool.
- [ ] **Create a Wikidata item** (no notability bar) and put the QID in `config.yaml` -> `ids.wikidata`. Feeds Google's Knowledge Graph and gives every JSON-LD `sameAs` a real target.
- [ ] **Populate ORCID 0000-0002-0085-6496** via the Crossref + DataCite Search & Link wizards and enable standing auto-update.
- [ ] **Merge 4 duplicate OpenAlex author records** into A5040286212.

## arXiv journal-ref missing (103 papers)

Scholar matches citations and merges preprint/published versions on exactly these fields. No write API -- one web form each, so do them by citation count.

- [ ] `2306.01708` (855 cites) -> Advances in Neural Information Processing Systems 36  <https://arxiv.org/abs/2306.01708>
- [ ] `2402.14992` (276 cites) -> Forty-first International Conference on Machine Lear  <https://arxiv.org/abs/2402.14992>
- [ ] `2412.03304` (181 cites) -> Proceedings of the 63rd Annual Meeting of the Associ  <https://arxiv.org/abs/2412.03304>
- [ ] `2104.08202` (167 cites) -> CoRR  <https://arxiv.org/abs/2104.08202>
- [ ] `1907.01752` (127 cites) -> 8th International Conference on Learning Representat  <https://arxiv.org/abs/1907.01752>
- [ ] `2204.03044` (120 cites) -> ArXiv  <https://arxiv.org/abs/2204.03044>
- [ ] `2211.05655` (119 cites) -> Proceedings of the 61st Annual Meeting of the Associ  <https://arxiv.org/abs/2211.05655>
- [ ] `2410.19735` (111 cites) -> International Conference on Learning Representations  <https://arxiv.org/abs/2410.19735>
- [ ] `2507.16806` (97 cites) -> The Fourteenth International Conference on Learning   <https://arxiv.org/abs/2507.16806>
- [ ] `2402.16842` (90 cites) -> Forty-first International Conference on Machine Lear  <https://arxiv.org/abs/2402.16842>
- [ ] `2405.17202` (83 cites) -> The Thirty-eighth Annual Conference on Neural Inform  <https://arxiv.org/abs/2405.17202>
- [ ] `2301.11796` (82 cites) -> CoRR  <https://arxiv.org/abs/2301.11796>

## Hugging Face paper page missing (50)

Visit the URL once to index it, then claim authorship.

- [ ] <https://hf.co/papers/2504.08165>  (232 cites)
- [ ] <https://hf.co/papers/1907.01752>  (127 cites)
- [ ] <https://hf.co/papers/2211.05655>  (119 cites)
- [ ] <https://hf.co/papers/2410.19735>  (111 cites)
- [ ] <https://hf.co/papers/1907.08971>  (77 cites)
- [ ] <https://hf.co/papers/2302.04863>  (71 cites)
- [ ] <https://hf.co/papers/1911.10763>  (70 cites)
- [ ] <https://hf.co/papers/1804.04012>  (70 cites)
- [ ] <https://hf.co/papers/2109.06096>  (41 cites)
- [ ] <https://hf.co/papers/1903.02953>  (38 cites)

## Hugging Face page indexed but not claimed by you (24)

- [ ] <https://hf.co/papers/2507.16806>  (97 cites)
- [ ] <https://hf.co/papers/2412.05149>  (62 cites)
- [ ] <https://hf.co/papers/2404.00459>  (46 cites)
- [ ] <https://hf.co/papers/2502.10645>  (33 cites)
- [ ] <https://hf.co/papers/2412.06540>  (26 cites)
- [ ] <https://hf.co/papers/2410.11840>  (22 cites)
- [ ] <https://hf.co/papers/2503.01622>  (21 cites)
- [ ] <https://hf.co/papers/2410.10783>  (18 cites)
- [ ] <https://hf.co/papers/2010.09459>  (15 cites)
- [ ] <https://hf.co/papers/2510.24081>  (10 cites)

## Sidecars not written (134/135)

The one input no tool can supply: claims, scope conditions, terminology, common misreadings. ~10 min each; do them by citation count.

- [ ] `data/sidecars/tinybenchmarks-evaluating-llms-with-fewer-examples.md`  (276 cites) tinyBenchmarks: evaluating LLMs with fewer examples
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

