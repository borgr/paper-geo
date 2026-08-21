---
key: waldis2024holmes
coined: Holmes
gloss: a probing benchmark that measures what language models internally encode about linguistic
  phenomena
one_liner: Holmes measures the linguistic competence of language models by training linear
  probes on the frozen last-layer representations of 208 datasets covering morphology, syntax,
  semantics, reasoning and discourse, isolating linguistic knowledge from instruction following.
links_extra:
  project page: https://holmes-benchmark.github.io
terminology:
  linguistic competence: Following Chomsky (1965), a language model's unconscious internal
    understanding of linguistic phenomena, assessed via its internal representations rather
    than via its textual responses.
  linguistic performance: A language model's use of language in textual responses to instructions,
    which is what prompting-based benchmarks measure and which conflates linguistic knowledge
    with abilities such as instruction following.
  formal vs. functional phenomena: Formal phenomena are morphology and syntax (grammatical
    rules and statistical patterns); functional phenomena are semantics, reasoning and discourse
    (practical abilities like interpreting sentiment or detecting speculation).
  selectivity: The macro-F1 of a probe trained on the true labels minus the macro-F1 of the
    same probe trained on randomly assigned control-task labels; higher values mean the probe
    found phenomenon-relevant structure rather than memorising.
  compression: The ratio of a uniform encoding of instances and labels to their minimum description
    length under the probe; higher values mean the linguistic phenomenon is more cleanly encoded
    in the representation.
  discriminability: The Kendall-tau alignment between the model ranking induced by a single
    probing dataset and the overall benchmark ranking; low values mean no single dataset dominates
    the aggregate ranking.
  rank resolution: The 95% confidence interval of the difference in a model's rank between
    a subsampled benchmark and the full benchmark; a resolution of 1 means a model keeps its
    rank or swaps with a neighbour.
  FlashHolmes: The streamlined variant of the Holmes benchmark that trains probes on 1/32
    of the training instances and excludes 18 licensed datasets.
claims:
- id: holmes-benchmark
  kind: context
  text: Holmes is a probing benchmark that assesses the English linguistic competence of language
    models with 208 datasets covering 66 phenomena. Its morphology, syntax, semantics, reasoning
    and discourse datasets consolidate resources found in a survey of 274 probing studies.
  scope: English only, and last-layer internal representations only. Classifier-based (linear)
    probing, so generation and instruction following are not measured; 18 of the 208 datasets
    rest on licensed resources.
  evidence: Section 4.1, Section 3.1
- id: probing-fragmented
  kind: result
  text: A meta-study of 274 probing papers finds the literature collectively covers 289 tasks
    and 161 language models, yet individual studies stay narrow. Part-of-speech tagging, the
    most probed task, was evaluated on only 23% of the models, and the top-10 most mentioned
    models account for 80% of all model mentions.
  scope: 28,063 papers from 2015 to August 2023 at ACL-family venues plus selected other venues,
    filtered by occurrences of 'probing'/'probe' and then manually reviewed; recent large
    models such as Pythia, UL2 and Llama-2 are almost absent from the surveyed work.
  evidence: Section 3.2 (iv), Figure 5, Figure 6
- id: classifier-probing-dominant
  kind: result
  text: Among 274 surveyed probing studies, 74% use classifier-based probing and 20% use mask-based
    probing, while roughly 3% rely on attention patterns or other approaches.
  scope: Categorisation of studies published 2015 to August 2023 at major NLP venues; each
    study assigned a single dominant probing method.
  evidence: Section 3.2 (iii), Figure 4
- id: probing-reliable
  kind: result
  text: Probing results on Holmes vary little across seeds, with an average standard deviation
    of 0.02 over 5 random seeds, against the 0.07 deviation reported for prompt paraphrasing
    in prompting-based evaluation. Average compression is 1.9 and average selectivity 0.31.
  scope: Averages over 208 probing datasets and the evaluated models, with fixed probe hyperparameters
    (20 epochs, batch size 64, learning rate 0.0005); selectivity computed only for base-sized
    models of 10M-200M parameters.
  evidence: Section 5 (i), Figure 8
- id: formal-vs-functional
  kind: result
  text: Across 59 evaluated language models, linguistic competence is markedly stronger for
    formal phenomena (morphology and syntax) than for functional ones (semantics, reasoning
    and discourse), which score lower on the probing task metric.
  scope: 59 models spanning sparse, static, encoder, decoder and encoder-decoder types, probed
    on last-layer representations of 208 English datasets.
  evidence: Section 5 (ii), Figure 9
- id: phenomena-correlations
  kind: result
  text: The five phenomenon types in Holmes correlate at 68.4±7.5 Kendall-tau with the overall
    model ranking but only 54.7±13.9 with each other. Discourse is the most distinct type,
    at 44.4±14.7 average correlation with the others.
  scope: Kendall-tau rank correlations over the models jointly evaluated within Holmes; semantics
    and reasoning correlate 73.9 and 75.6 with the overall ranking but only 58.4 with each
    other.
  evidence: Section 5 (ii), Figure 10 (left)
- id: encoder-beats-decoder
  kind: result
  text: Encoder language models reach a mean winning rate of 52% on Holmes against 21% for
    decoder models of comparable size. Decoder models do not match encoder stability on frequent
    part-of-speech tokens even at 700 times the parameter count.
  scope: 5 encoder and 6 decoder models up to 220M parameters for the mean-winning-rate comparison;
    token stability covers BERT, RoBERTa, GPT2, Pythia-12B and Llama-2-70B on the top-20 most
    common tokens of the pos, xpos and upos datasets.
  evidence: Section 5 (iii), Figure 11
- id: scaling
  kind: result
  text: Linguistic competence on Holmes scales with parameter count within the Pythia and
    T5 families. The jump is pronounced beyond 0.5B parameters for Pythia and 1.0B for T5,
    and is concentrated in morphology and syntax.
  scope: 8 T5 sizes and 5 Pythia sizes only; T5 (encoder-decoder) reaches a mean winning rate
    of 40-70% versus 20-60% for Pythia (decoder-only), so architecture and scale are not separated
    in this comparison.
  evidence: Section 5 (iv), Figure 12
- id: instruction-tuning-mixed
  kind: result
  text: Instruction tuning raises mean winning rate on Holmes by an average of +10% for morphology,
    +5% for syntax and +4% for reasoning. It lowers it by -3% for semantics and -1% for discourse,
    for an overall average of +2%, with per-model effects from +41% to -13%.
  scope: 11 instruction-tuned models each compared against its own pre-trained base (Llama-2-Chat,
    FLAN-T5, Dolly-v2, Tülu-2, Orca-2, Vicuna-v1.5, FLAN-UL2, Mixtral-Instruct) at 7B to 70B
    parameters.
  evidence: Table 2
- id: openllm-correlation
  kind: result
  text: Holmes probing rankings correlate only moderately with the prompting-based OpenLLM
    leaderboard, at 54.7 to 58.0 Kendall-tau for syntax, semantics and discourse, rising to
    65.3 for morphology and 77.5 for reasoning.
  scope: Models evaluated by both Holmes and OpenLLM (Beeching et al., 2023); correlation
    patterns hold across MMLU, TruthfulQA and GSM8K, with TruthfulQA the weakest correlate.
  evidence: Section 5 (vi), Figure 10 (right)
- id: prompting-not-substitute
  kind: result
  text: On the BLiMP datasets evaluated by both Holmes and HELM, probing-based and prompting-based
    model rankings barely agree, at a rank correlation of tau=0.05. Most HELM prompting results
    fall below the random baseline.
  scope: 40 open decoder models and 22 BLiMP datasets covering quantifier, island effects,
    irregular forms and binding phenomena, using HELM's own evaluation code with its multiple-choice-joined
    prompting adaptation.
  evidence: Figure 15
- id: flashholmes
  kind: result
  text: FlashHolmes reproduces Holmes model rankings at a rank resolution of about 1.5 while
    requiring roughly 3% of the computation. It trains probes on 1/32 of the training instances
    and drops the 18 licensed datasets, versus about 6 GPU days of encoding for a 70B model
    on full Holmes.
  scope: Rank resolution is the 95% CI of rank difference against full Holmes, where 1/2 of
    the training data gives about 0.9 and 1/512 about 2.6; English datasets, last-layer representations.
  evidence: Section 6, Figure 13
- id: contamination-robust
  kind: context
  text: Holmes argues that probing-based evaluation retains validity under dataset contamination,
    because instruction tuning aligns a model's textual responses rather than explicitly aligning
    the internal representations that the probes read.
  scope: An argument rather than a measurement; training data is unknown for several evaluated
    models, including Llama-2, Mixtral and Wizard.
  evidence: Ethical Considerations and Limitations, Dataset Contamination
qa:
- ask:
    plain: is there a way to test how much grammar a language model actually knows without
      asking it questions in a prompt?
    jargon: which benchmark consolidates the probing literature into a single linguistic competence
      suite for English language models?
    task: where do I get a large collection of ready-made probing datasets covering morphology,
      syntax, semantics, reasoning and discourse?
    practitioner: should I use a consolidated probing benchmark instead of assembling probing
      datasets from individual papers myself?
  answered_by:
  - holmes-benchmark
  - probing-fragmented
- ask:
    plain: if a language model answers grammar questions correctly, does that mean its internal
      representations really encode grammar?
    jargon: how closely do probing-based rankings on BLiMP agree with prompting-based rankings
      from HELM and the OpenLLM leaderboard?
    task: can I skip probing and just prompt models on linguistic minimal pairs to rank their
      linguistic ability?
    practitioner: I already have leaderboard scores for my models -- do I still need probing
      to know their linguistic competence?
  answered_by:
  - prompting-not-substitute
  - openllm-correlation
- ask:
    plain: do older BERT-style models capture grammar better inside than much bigger chat-style
      models?
    jargon: how do encoder and decoder architectures compare on classifier probing for part-of-speech
      and agreement phenomena at matched parameter counts?
    task: which architecture should I pick to extract reliable part-of-speech and syntactic
      features from hidden states?
    practitioner: if I need strong token-level linguistic representations, is a 70B decoder
      model worth it over a small encoder?
  answered_by:
  - encoder-beats-decoder
- ask:
    plain: does teaching a model to follow instructions change how much grammar and meaning
      it encodes internally?
    jargon: what is the effect of instruction tuning on probing scores across morphology,
      syntax, semantics, reasoning and discourse?
    task: should I probe the base checkpoint or the instruction-tuned checkpoint if I care
      about linguistic phenomena?
    practitioner: will switching to the instruction-tuned version of my model improve its
      internal handling of syntax and semantics?
  answered_by:
  - instruction-tuning-mixed
- ask:
    plain: do bigger language models really encode more grammar than smaller ones from the
      same family?
    jargon: how does probing performance on morphological and syntactic phenomena scale with
      parameter count within the Pythia and T5 families?
    task: how big a model do I need before probing scores on syntax and morphology start to
      improve noticeably?
    practitioner: is it worth moving up to a larger checkpoint in the same family if I want
      better linguistic representations?
  answered_by:
  - scaling
- ask:
    plain: which parts of language are models good at internally, and which parts do they
      handle poorly?
    jargon: how do probing scores differ between formal phenomena such as morphology and syntax
      and functional ones such as semantics, reasoning and discourse?
    task: which linguistic phenomena should I test if I want to find where a language model's
      representations are weakest?
    practitioner: can I assume a model that scores well on syntax probing will also handle
      discourse and semantics well?
  answered_by:
  - formal-vs-functional
  - phenomena-correlations
- ask:
    plain: are probing scores stable enough to trust, or do they bounce around depending on
      how you run them?
    jargon: how much do classifier probing results vary across random seeds compared with
      the variance from prompt paraphrasing?
    task: how many seeds do I need to run before probing numbers are reliable enough to compare
      models?
    practitioner: should I trust a probing-based ranking of my models, or will it change if
      I rerun it?
  answered_by:
  - probing-reliable
- ask:
    plain: how much computing time does it take to run a full battery of internal linguistic
      tests on a large language model?
    jargon: what is the compute cost of encoding 208 probing datasets for a 70B model, and
      how much does a subsampled variant save?
    task: how do I evaluate a newly released model on a large probing suite without spending
      GPU days on encoding?
    practitioner: on a small compute budget, can I use a cheap subsampled probing run and
      still get the same model ordering?
  answered_by:
  - flashholmes
- ask:
    plain: how much do published studies of what language models know about language actually
      overlap in the tasks and models they test?
    jargon: how many probing tasks and language models does the probing literature jointly
      cover, and what share uses classifier-based versus mask-based probing?
    task: how do I find out whether the probing task I care about has already been evaluated
      on the models I use?
    practitioner: can I rely on published probing papers to tell me about my model, or do
      they each cover too few models?
  answered_by:
  - probing-fragmented
  - classifier-probing-dominant
- ask:
    plain: if a test set ended up in a model's training data, does that ruin an evaluation
      of its internal linguistic knowledge?
    jargon: why is probing internal representations argued to remain valid under benchmark
      contamination in pretraining corpora?
    task: how do I evaluate linguistic competence when I cannot rule out that the evaluation
      datasets were seen during pretraining?
    practitioner: should I worry about data leakage if I evaluate my model with probing classifiers
      rather than prompts?
  answered_by:
  - contamination-robust
- ask:
    plain: what exactly does a large linguistic probing benchmark measure about a language
      model, and how much does it cover?
    jargon: which linguistic phenomena and dataset counts make up the Holmes probing suite,
      and what does it find about formal versus functional competence?
    task: what will I learn about my model's linguistic abilities if I run it through a broad
      probing benchmark?
    practitioner: is a broad linguistic probing benchmark measuring the phenomena I care about
      before I commit to running it?
  answered_by:
  - holmes-benchmark
  - formal-vs-functional
misreadings:
- Holmes does not test whether a language model can answer grammar questions; it trains linear
  probes on frozen last-layer representations, so a high Holmes score says nothing directly
  about a model's generated output.
- The finding that encoders beat decoders holds for models up to 220M parameters in the mean-winning-rate
  comparison, because no large encoder-only models were available; it is not a measured comparison
  of a 70B encoder against a 70B decoder.
- 'Instruction tuning is not uniformly harmful or uniformly helpful for linguistic competence:
  it averages +10% mean winning rate on morphology but -3% on semantics, and individual models
  range from -13% to +41% depending on phenomenon type.'
- A moderate Holmes-OpenLLM rank correlation does not mean probing and prompting measure the
  same thing; on jointly evaluated BLiMP datasets the two rankings agree at only tau=0.05.
- 'FlashHolmes is not merely a random subsample of Holmes: besides training on 1/32 of the
  instances it also excludes the 18 datasets built from licensed resources.'
- Holmes covers English only, so its rankings should not be read as claims about multilingual
  linguistic competence.
---
