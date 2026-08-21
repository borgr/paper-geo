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
    practitioner: What benchmark should I read about first for evaluating what language models
      know about grammar and linguistics?
    unsorted:
    - Is there a benchmark that tests linguistic knowledge of LLMs without prompting?
    - Where can I find a large consolidated collection of probing datasets for language models?
    - What work consolidated the probing literature into an evaluation suite?
  answered_by:
  - holmes-benchmark
  - probing-fragmented
- ask:
    unsorted:
    - Does prompting a language model about syntax tell you the same thing as probing its
      representations?
    - Can prompting-based benchmarks replace probing for measuring linguistic knowledge?
    - How well do HELM's BLiMP prompting results agree with probing results?
  answered_by:
  - prompting-not-substitute
  - openllm-correlation
- ask:
    unsorted:
    - Do encoder models understand language better than decoder-only LLMs?
    - Does architecture matter for how well a model encodes part-of-speech and agreement?
    - Can a 70B decoder model match BERT on token-level linguistic probing?
  answered_by:
  - encoder-beats-decoder
- ask:
    unsorted:
    - Does instruction tuning improve a model's internal grasp of linguistic phenomena?
    - What effect does RLHF-style instruction tuning have on syntax and semantics probing
      scores?
    - Is instruction tuning only a superficial alignment when it comes to linguistic competence?
  answered_by:
  - instruction-tuning-mixed
- ask:
    unsorted:
    - Does linguistic competence in language models scale with parameter count?
    - At what model size do probing scores for morphology and syntax jump?
    - How do T5 and Pythia compare as they get bigger on linguistic probing?
  answered_by:
  - scaling
- ask:
    unsorted:
    - Which linguistic phenomena are language models good and bad at internally?
    - Are semantics and discourse harder for language models than syntax?
    - What is the difference between formal and functional linguistic phenomena in model probing
      results?
  answered_by:
  - formal-vs-functional
  - phenomena-correlations
- ask:
    unsorted:
    - Are classifier-probing results stable enough to build a benchmark on?
    - How much do probing scores vary across random seeds compared to prompt variation?
    - What reliability checks did the Holmes benchmark run on its probes?
  answered_by:
  - probing-reliable
- ask:
    unsorted:
    - How expensive is it to evaluate a new large language model on a full probing benchmark?
    - Is there a cheap version of Holmes for evaluating a new model?
    - How much compute does FlashHolmes save and at what cost in ranking accuracy?
  answered_by:
  - flashholmes
- ask:
    unsorted:
    - How fragmented is existing probing research on language models?
    - How many tasks and models does the probing literature actually cover jointly?
    - Which probing method dominates the published literature?
  answered_by:
  - probing-fragmented
  - classifier-probing-dominant
- ask:
    unsorted:
    - Is a probing benchmark affected by benchmark contamination in pretraining data?
    - Why would evaluating internal representations be more robust to data leakage?
    - Does Holmes control for the possibility that OntoNotes was in a model's pretraining
      corpus?
  answered_by:
  - contamination-robust
- ask:
    unsorted:
    - How many language models and datasets does a linguistic probing benchmark like Holmes
      cover?
    - What does the Holmes benchmark measure about language models?
    - Which linguistic phenomena are covered by a large probing benchmark for language models?
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
