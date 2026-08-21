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
    plain: is there a version of the child-language training data collection that covers languages
      other than English?
    jargon: which resource provides developmentally plausible pretraining corpora and evaluation
      across many languages?
    task: where do I start if I want to pretrain a small language model on child-directed
      text in a language other than English?
    practitioner: I work on a non-English language and want child-language pretraining data
      plus a baseline model, is there something I can use off the shelf?
  answered_by:
  - coverage-45-languages
  - living-resource
- ask:
    plain: how many languages does BabyBabelLM cover, and how much text is there per language?
    jargon: how are the BabyBabelLM data tiers defined, and how are token budgets normalised
      to English-equivalent counts?
    task: how do I find out how much training data is available for my language in the multilingual
      BabyLM corpora?
    practitioner: will my language have enough tokens in BabyBabelLM to train on, or am I
      stuck at the smallest budget?
  answered_by:
  - tier-distribution
  - padding-share
- ask:
    plain: in a multilingual collection of child-language corpora, how much of the text is
      really speech and books for children rather than filler added to hit a size target?
    jargon: what share of each BabyBabelLM language's tier budget comes from padding data,
      and which languages have no language-specific child-oriented sources?
    task: how do I check whether the corpus for my language is genuinely child-directed before
      I train on it?
    practitioner: if I train on the corpus for Korean or Turkish, am I actually training on
      child-oriented text?
  answered_by:
  - padding-share
  - sixteen-multilingual-only
- ask:
    plain: how well do small models trained on roughly 100 million words of child-language
      text handle basic grammar tests?
    jargon: what MultiBLiMP subject-verb agreement accuracies do the 17.1M-parameter GPT-2
      baselines reach on Tier 1 languages?
    task: how do I tell whether a tiny model trained on limited child-language data has learned
      agreement in my language?
    practitioner: if I pretrain on the largest BabyBabelLM budget for my language, should
      I expect the model to get agreement right?
  answered_by:
  - multiblimp-tier1
- ask:
    plain: can models trained on 1 million to 100 million words answer commonsense or knowledge
      questions at all?
    jargon: do the BabyBabelLM monolingual baselines exceed chance on functional-competence
      benchmarks such as XCOPA, ARC and HellaSwag, and does zero-shot prompting work at that
      scale?
    task: how should I evaluate a model pretrained on under 100 million tokens if prompting
      gives nothing above chance?
    practitioner: is it worth running reasoning or QA benchmarks on my tiny child-language
      model, or do I need to finetune first?
  answered_by:
  - near-chance-functional
  - in-context-limit
- ask:
    plain: at very small data sizes, is it better to train one model on many languages or
      a separate model per language?
    jargon: does the 111M-parameter multilingual BabyBabelLM model beat the monolingual baselines
      on MultiBLiMP minimal pairs?
    task: how do I decide between pooling all my low-resource languages into one pretraining
      run and training each separately?
    practitioner: should I train one multilingual child-language model or per-language models
      if I care about grammatical competence?
  answered_by:
  - mono-beats-multi
- ask:
    plain: how do tiny models trained on child-directed text compare with a small off-the-shelf
      model trained on web data?
    jargon: how does Qwen3-0.6B compare with the BabyBabelLM multilingual baseline on MultiBLiMP
      and Belebele across languages?
    task: how do I set a realistic upper bound for a small child-language model by comparing
      it against a web-scale small LLM?
    practitioner: if a 0.6B web-trained multilingual model already exists, is there any reason
      to use a BabyBabelLM baseline instead?
  answered_by:
  - qwen-comparison
- ask:
    plain: does mixing in English text help a model trained on a smaller amount of data in
      another language?
    jargon: what happens to zero-shot benchmark and minimal-pair scores when a Tier 1 BabyBabelLM
      model is pretrained bilingually with English?
    task: how do I improve downstream accuracy for a low-resource pretraining run without
      collecting more data in that language?
    practitioner: should I add English to my pretraining mix for a low-resource language,
      or does it dilute the grammar my model learns?
  answered_by:
  - bilingual-gains
- ask:
    plain: does an architecture that won an English child-language modelling competition also
      work best in other languages?
    jargon: does GPT-BERT transfer its 2024 BabyLM Challenge advantage over GPT-2 to the multilingual
      BabyBabelLM corpora?
    task: which architecture should I pick for pretraining on a small non-English child-language
      corpus?
    practitioner: should I use GPT-BERT rather than a plain small GPT-2 for my non-English
      child-language pretraining run?
  answered_by:
  - gpt-bert-underperforms
- ask:
    plain: what tests exist for judging small models trained on child-language data in languages
      other than English?
    jargon: which benchmark in the BabyBabelLM evaluation suite approaches full language coverage,
      and how patchy is coverage elsewhere?
    task: how do I assemble an evaluation suite for a small pretrained model in a language
      with few benchmarks?
    practitioner: can I evaluate my language with the same benchmarks as the others, or will
      I need to build my own datasets?
  answered_by:
  - evaluation-gap
- ask:
    plain: can outside contributors add a new language or more text to the multilingual child-language
      data collection?
    jargon: what pipeline and document-level schema does BabyBabelLM expose for community
      contributions of new languages?
    task: how do I contribute a corpus for a language that BabyBabelLM does not yet include?
    practitioner: if my language is missing from BabyBabelLM, can I add it myself and how?
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
