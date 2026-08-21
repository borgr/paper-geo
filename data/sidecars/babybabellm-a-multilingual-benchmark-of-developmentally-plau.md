---
key: jumelet2026babybabellm
coined: BabyBabelLM
gloss: multilingual child-language-style pretraining corpora, evaluations and baseline models
  for 45 languages
one_liner: BabyBabelLM curates developmentally plausible pretraining corpora for 45 languages,
  sized into 100M/10M/1M English-equivalent-token tiers via byte premiums, and adds an evaluation
  suite plus monolingual, bilingual and multilingual baseline models.
links_extra:
  project page: https://babylm.github.io/babybabellm
  code: https://github.com/babylm-org/multilingual-babylm
terminology:
  Developmental plausibility: The criterion that pretraining data should approximate the linguistic
    input a child actually encounters, prioritising child-directed speech, educational material
    and child-oriented books, wikis and subtitles, and excluding synthetic corpora such as
    TinyStories.
  Byte premium: A per-language multiplier on UTF-8 encoded size that makes token budgets comparable
    across orthographies and morphologies, so that '100M English-equivalent tokens' means
    the same amount of content in each language.
  Language tier: A size class of a BabyBabelLM language dataset, where Tier 1 targets the
    equivalent of 100M English tokens, Tier 2 10M and Tier 3 1M.
  Padding: Filler data added to a language dataset to reach its target tier size, drawn mainly
    from child-appropriate OpenSubtitles and, where insufficient, FineWeb-C and Wikipedia.
  MonoBLiMP: The collection of language-specific minimal pair benchmarks used together in
    the BabyBabelLM evaluation suite, including Basque, Chinese, Japanese, German and Turkish
    resources plus CLAMS for English, French, German, Russian and Hebrew.
  Child-available speech: Speech children are exposed to without being the intended recipient,
    such as overheard adult-adult conversation, included alongside child-directed speech.
claims:
- id: coverage-45-languages
  kind: context
  text: BabyBabelLM is a coordinated multilingual collection of developmentally plausible
    pretraining corpora covering 45 languages, released together with an evaluation suite
    and baseline models for each language.
  scope: 45 languages spanning families primarily rooted in Europe, Asia and Africa, 22 of
    them Indo-European; as of the 2025 initial release.
- id: tier-distribution
  text: The 45 BabyBabelLM languages split into 9 Tier 1 languages at roughly 100M English-equivalent
    tokens, 15 Tier 2 languages at 10M and 21 Tier 3 languages at 1M.
  evidence: Section 3.2.2, Table 3
  scope: Thresholds calibrated with the byte premium approach of Arnett et al. (2024); tier
    size reached by padding when plausible data runs out.
- id: padding-share
  text: Most BabyBabelLM languages reach their tier size largely through padding rather than
    child-oriented data. Bulgarian's corpus contains 90,563,381 padding tokens and Indonesian's
    96,044,750, while English needs only 20,706,303.
  evidence: Table 3
  scope: Per-language token counts in the initial release; padding is child-appropriate OpenSubtitles
    where available, with FineWeb-C and Wikipedia as fallback. Some languages, such as Persian
    and Spanish, rely on padding far less.
- id: sixteen-multilingual-only
  text: 16 of the 45 BabyBabelLM languages, including Basque, Czech, Hebrew, Korean, Russian,
    Turkish and Welsh, are populated only from general-purpose multilingual sources (CHILDES,
    GlotStoryBooks, Ririro and child wikis) with no language-specific collection.
  evidence: Section 3.1.2, Appendix C.19
  scope: Initial release; the authors describe these entries as starting points and provide
    a pipeline for community expansion.
- id: multiblimp-tier1
  text: Monolingual 17.1M-parameter GPT-2 models trained on BabyBabelLM typically score above
    80% on MultiBLiMP subject-verb agreement minimal pairs for Tier 1 languages. French reaches
    94.1% and Bulgarian 90.8%, against a 50% chance baseline.
  evidence: Table 1, Section 5
  scope: GPT-2 with 4 layers, 8 heads, hidden size 512 and an 8,192-token BPE vocabulary,
    10 epochs per language; MultiBLiMP zero-shot. Tier 2 and 3 languages score lower, down
    to 58.5% for Russian.
- id: near-chance-functional
  text: The BabyBabelLM monolingual baselines stay close to random chance on functional-competence
    benchmarks including XCOPA, ARC, XCOMPS and HellaSwag, with HellaSwag accuracies clustered
    around 25–27% against 25% chance.
  evidence: Table 1
  scope: 17.1M-parameter GPT-2 models; ARC, TruthfulQA, BMLAMA, Belebele, INCLUDE, SIB-200,
    Global-MMLU, MultiNLI, XNLI and XCOPA scores are after finetuning on up to 8,000 items
    for 10 epochs, other tasks zero-shot.
- id: in-context-limit
  text: Zero-shot prompting on classification and question-answering benchmarks failed for
    the BabyBabelLM models, because corpora of 1M–100M tokens are too small for in-context
    learning to emerge. Those tasks are reported after finetuning instead.
  evidence: Section 4
  scope: ARC, TruthfulQA, BMLAMA, Belebele, INCLUDE, SIB-200, Global-MMLU, MultiNLI, XNLI
    and XCOPA with the 17.1M-parameter GPT-2 baselines; cited evidence puts induction heads
    at 2.5–5B tokens of exposure.
- id: mono-beats-multi
  text: On MultiBLiMP the monolingual BabyBabelLM models generally beat the 111M-parameter
    multilingual BabyBabelLM model, which improves only modestly on 4 Tier 3 languages.
  evidence: Figure 2
  scope: 'Multilingual model: 12 layers, hidden size 768, 32,768-token vocabulary, 1 epoch
    on roughly 1B tokens; only languages with MultiBLiMP coverage.'
- id: qwen-comparison
  text: Qwen3-0.6B outperforms the multilingual BabyBabelLM model on MultiBLiMP in most languages,
    while BabyBabelLM remains stronger in 8 languages with no clear trend by tier; on Belebele
    both BabyBabelLM models sit near chance while Qwen3-0.6B is substantially higher in every
    language.
  evidence: Figure 2, Table 5
  scope: Multilingual BabyBabelLM has 111M parameters trained on roughly 1B tokens for 1 epoch,
    against Qwen3-0.6B trained on ordinary web-scale data; Belebele scores for BabyBabelLM
    are post-finetuning.
- id: bilingual-gains
  text: Adding English as a second training language raises zero-shot accuracy across most
    Tier 1 languages on SIB-200, BMLAMA, XCOMPS and INCLUDE, with Dutch SIB-200 gaining 24.8
    points. MultiBLiMP performance is largely unchanged.
  evidence: Figure 3
  scope: Each Tier 1 language paired with the English BabyLM corpus, 200M tokens total, same
    GPT-2 configuration but 5 epochs; Dutch on INCLUDE slightly decreases.
- id: gpt-bert-underperforms
  text: GPT-BERT, the architecture that won the 2024 BabyLM Challenge, did not outperform
    the 17.1M-parameter GPT-2 baselines on BabyBabelLM data, scoring consistently lower on
    SIB-200 and MultiBLiMP.
  evidence: Figure 4, Appendix D
  scope: Tier 1 and Tier 2 languages only, 500 steps for Tier 1 and 250 for Tier 2, 12 layers,
    hidden size 768, 16,384-token vocabulary; no configuration search.
- id: evaluation-gap
  text: MultiBLiMP is the only benchmark in the BabyBabelLM evaluation suite that approaches
    coverage of all included languages, and many languages are evaluated only on monolingual
    datasets built specifically for them.
  evidence: Table 1, Limitations
  scope: Benchmarks surveyed for the initial release, covering formal competence (minimal
    pairs) and functional competence (knowledge and reasoning).
- id: living-resource
  kind: context
  text: BabyBabelLM ships an open-source pipeline and a unified document-level schema so that
    researchers can add new languages or extend existing ones through GitHub and Hugging Face
    pull requests.
  scope: Documents carry text, category, data source, script, language, age estimate, license
    and token count fields; all data permits academic research.
qa:
- ask:
    practitioner: Where can I find child-language-style pretraining data for languages other
      than English?
    unsorted:
    - Is there a multilingual version of the BabyLM training corpus?
    - What dataset provides developmentally plausible pretraining data across many languages?
    - What should I read first about multilingual developmentally plausible language modeling?
  answered_by:
  - coverage-45-languages
  - living-resource
- ask:
    unsorted:
    - How many languages does BabyBabelLM cover and how much data does each have?
    - What are the data tiers in BabyBabelLM?
    - How are token budgets made comparable across languages with different scripts?
  answered_by:
  - tier-distribution
  - padding-share
- ask:
    unsorted:
    - How much of a multilingual child-language corpus is actually child-directed data rather
      than filler?
    - Do all 45 BabyBabelLM languages have genuinely child-oriented sources?
    - Which languages in BabyBabelLM rely only on generic multilingual resources?
  answered_by:
  - padding-share
  - sixteen-multilingual-only
- ask:
    unsorted:
    - How well do small language models trained on ~100M words of child-language data do on
      grammar tests?
    - What accuracy do BabyBabelLM baselines reach on MultiBLiMP?
    - Does data size affect subject-verb agreement performance in tiny multilingual LMs?
  answered_by:
  - multiblimp-tier1
- ask:
    unsorted:
    - Can models trained on 1M-100M tokens do reasoning or knowledge benchmarks?
    - Why are the BabyBabelLM baselines near chance on commonsense and knowledge tasks?
    - Do tiny developmentally plausible language models learn in-context learning?
  answered_by:
  - near-chance-functional
  - in-context-limit
- ask:
    unsorted:
    - Is one multilingual model better than separate per-language models at this data scale?
    - Does a multilingual BabyLM beat monolingual BabyLMs on grammar minimal pairs?
    - How does BabyBabelLM's multilingual model compare to the monolingual ones?
  answered_by:
  - mono-beats-multi
- ask:
    unsorted:
    - How do tiny developmentally plausible models compare to an off-the-shelf small multilingual
      LLM?
    - Does Qwen3-0.6B beat BabyBabelLM models?
    - Are BabyBabelLM baselines competitive with web-scale-trained small models?
  answered_by:
  - qwen-comparison
- ask:
    unsorted:
    - Does adding English to a low-resource pretraining corpus help downstream performance?
    - What happens when a BabyLM is trained bilingually with English?
    - Does bilingual training change syntactic competence in small language models?
  answered_by:
  - bilingual-gains
- ask:
    unsorted:
    - Does the BabyLM 2024 winning architecture transfer to other languages?
    - How does GPT-BERT compare to GPT-2 on multilingual developmentally plausible data?
    - Which architecture works best on BabyBabelLM corpora?
  answered_by:
  - gpt-bert-underperforms
- ask:
    unsorted:
    - What evaluation benchmarks exist for developmentally plausible models across many languages?
    - Which benchmark covers the most languages in the BabyBabelLM suite?
    - What are the limits of multilingual evaluation for small child-language models?
  answered_by:
  - evaluation-gap
- ask:
    practitioner: How can I contribute a new language to BabyBabelLM?
    unsorted:
    - Is the multilingual BabyLM dataset extensible by the community?
    - What metadata do BabyBabelLM documents carry?
  answered_by:
  - living-resource
misreadings:
- 'BabyBabelLM does not give every language 100M English-equivalent tokens: only 9 languages
  reach Tier 1, while 21 languages sit at roughly 1M tokens.'
- The BabyBabelLM per-language token totals are not all developmentally plausible content
  — several languages, such as Bulgarian and Indonesian, are padded to their tier size with
  subtitles, FineWeb-C or Wikipedia, so cross-linguistic comparisons must account for differing
  corpus composition.
- 'The 45 BabyBabelLM baseline models are not usable general-purpose LMs: at 17.1M parameters
  they sit near random chance on reasoning and knowledge benchmarks and are offered as starting
  points for further experimentation.'
- That GPT-BERT underperformed GPT-2 on BabyBabelLM is not evidence that GPT-BERT is a worse
  architecture in general; only a single configuration with 500 or 250 training steps was
  tried and no configuration search was carried out.
- BabyBabelLM does not claim to reproduce the actual input any individual native speaker receives;
  the distribution of topics and formats is a coarse approximation of a child's linguistic
  environment, better than Wikipedia dumps but not equivalent to real acquisition input.
- Excluding synthetic corpora such as TinyStories from BabyBabelLM was a deliberate design
  choice motivated by reduced linguistic long tails and more uniform syntax in synthetic text,
  not an oversight.
---
