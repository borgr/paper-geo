---
one_liner: Pretraining a battery of small BabyLlama-2 models on 10-million-word time slices
  of Project Gutenberg gives historically airtight language models that finetuned Llama3-8B
  adapters cannot match, because finetuned models leak future word senses across period boundaries.
key: fittschen2026diachronic
coined: Perspectival Language Models
gloss: small language models pretrained separately on each slice of a corpus, so each one
  only knows its own period or genre
claims:
- id: pretrain-period-specific-ppl
  kind: result
  text: BabyLlama-2 models pretrained on individual 1750-1940 time slices each reach their
    lowest perplexity on the test set from their own slice, with perplexity rising roughly
    linearly on both older and newer text. Llama3-8B DoRA models finetuned on the same slices
    show this preference only for the earlier slices.
  scope: 5 slices (1750-1820, 1820-1850, 1850-1880, 1880-1910, 1910-1940) of 10M training
    tokens each drawn from Project Gutenberg English prose, with 5M reserved test and 1M validation
    tokens.
  evidence: Figure 1
- id: leakage
  kind: result
  text: Llama3-8B DoRA models finetuned on early time slices recall word senses coined after
    their slice at consistently higher rates than the period-pretrained BabyLlama-2 models.
    The gap persists after correcting for each model's overall recall, and the cloze task
    is built from Oxford English Dictionary sense-first-attestation dates.
  scope: 14.6 thousand cloze examples remaining after filtering out words with fewer than
    2 occurrences in any training set, scored as success if the target appears in the top
    100 single-word completions.
  evidence: Figure 3 and Figure 7
- id: cholera-example
  kind: result
  text: For the 1837 hog-disease sense of "cholera", only the 1750-1820 pretrained model ranks
    the word inside the top-k completions, at rank 41. The DoRA-finetuned models rank it 11
    to 19 in every slice, and off-the-shelf Llama3-8B ranks it 8.
  scope: A single manually inspected cloze context; illustrative of the leakage pattern rather
    than an aggregate measurement.
  evidence: Table 7
- id: blimp-aggregate
  kind: result
  text: On maximally filtered BLiMP the period-pretrained BabyLlama-2 models score 0.67 to
    0.72 aggregate accuracy across the 5 slices. The DoRA-finetuned models reach 0.80 to 0.84,
    off-the-shelf BabyLlama-2 scores 0.74 and Llama3-8B scores 0.82.
  scope: '"Maximally filtered" BLiMP: only minimal pairs whose every word occurs at least
    twice in all 5 training sets, evaluated through the BabyLM 2024 evaluation pipeline.'
  evidence: Table 3
- id: npi-change
  kind: result
  text: On the BLiMP "only NPI licenser present" task the period-pretrained models rise monotonically
    from 0.00 accuracy in the 1750-1820 and 1820-1850 slices to 0.33, 0.82 and 0.91 in the
    later slices. The DoRA-finetuned models score 0.92 to 1.00 in every slice and register
    no diachronic change.
  scope: Maximally filtered BLiMP subset testing preference for "only...ever" over "even...ever";
    baseline BabyLlama-2 scores 0.76 and Llama3-8B 0.90. The corpus is Gutenberg English prose,
    so the trend may be corpus-specific rather than a fact about English.
  evidence: Table 4
- id: training-cost
  kind: result
  text: Training one period model with the BabyLlama-2 recipe takes about 32 minutes per teacher
    plus 3 hours 20 minutes for the distilled 345M-parameter student on a single A100. DoRA
    finetuning of Llama3-8B for 3 epochs on the same 10M-token slice takes around 8 hours.
  scope: Single A100 GPU; DoRA rank 16 on Q, K, V, Up and Down projections; BabyLlama-2 uses
    2 same-size teachers and 8 epochs with distillation alpha 0.5.
  evidence: Appendix A, Tables 8-10
- id: date-attribution
  kind: result
  text: Zero-shot work-date attribution by 4-bit quantized Llama3.3-70B matches hand-annotated
    dates at 0.63 within 1 year and 0.81 within 10 years. GPT-4o reaches 0.82 and 0.84 on
    the same set, which the authors judge close enough to justify the open-weight model for
    segmenting the corpus.
  scope: 1054 manually annotated known-author works published 1550-1850, dated by prompting
    for a single year; the +/-1 tolerance accommodates copyright-year publication dates.
  evidence: Table 11
- id: sense-trajectories
  kind: result
  text: Filtering words by a monotonic fall in normalized per-word perplexity across the 5
    period models separates two synchronically distinct senses of "station". The railway sense
    becomes sharply more acceptable in the 1820-1850 slice, while the camp/stopover sense
    rises smoothly from an already acceptable start.
  scope: Natural occurrences of "station" in the corpus, filtered for descending probability
    trajectory and then hand-labelled for sense; a demonstration of the discovery procedure,
    not a quantified detection rate.
  evidence: Figure 4
- id: prefiguration
  kind: result
  text: The 1750-1820 pretrained model ranks "line" 14th as the completion of "the end of
    the line", a sense first attested in 1948. A collocation search shows the construction
    never appears in that model's training data, and hereditary and military uses of "line"
    appear to prefigure it.
  scope: One hand-inspected cloze item; the finetuned model ranks the same completion 1st,
    which leakage from Llama3-8B pretraining can equally explain.
  evidence: Table 6
- id: context-pretraining-as-method
  kind: context
  text: '"Pretraining Language Models for Diachronic Linguistic Change Discovery" argues that
    domain-restricted pretraining, not finetuning or model editing, is the only way to guarantee
    a language model''s weights contain no out-of-domain information. The paper shows that
    argument is affordable at 10M tokens per model using BabyLM-community recipes.'
  scope: Argued and demonstrated for temporal division of an English literary corpus at academic
    compute scale; the paper does not test synchronic divisions such as genre, and lists that
    as future work.
  evidence: Section 1
- id: context-nonlexical-change
  kind: context
  text: Time-sliced perspectival pretraining extends computational study of language change
    beyond lexical semantic change to grammatical and morphological phenomena. Its authors
    report knowing of no prior work using language models to automate discovery of such non-lexical
    change.
  scope: As of publication in 2026; prior lexical semantic change work is surveyed as relying
    on non-causal embedding models and embedding alignment. The grammatical evidence is a
    single BLiMP phenomenon on one corpus.
  evidence: Section 2
- id: context-pipeline
  kind: context
  text: The historical-perspectival-lm codebase releases the full date-attribution, slicing,
    pretraining, finetuning and evaluation pipeline for time-sliced language models. It also
    releases a word-sense cloze evaluation set of 50.4 thousand OED-derived examples.
  scope: Reuse on new corpora requires supplying train/dev/test text per category; the released
    historical data covers English Project Gutenberg works dated 1750-1940. Cloze set filtering
    to 14.6 thousand examples is specific to the paper's vocabulary overlap.
  evidence: Appendix C
qa:
- ask:
    plain: if a big language model is trained further on writing from one century, will it
      forget words invented after that century?
    jargon: does parameter-efficient finetuning of Llama3-8B on a period corpus prevent recall
      of post-period word senses?
    task: how do I keep a language model from using vocabulary that did not exist in the period
      I am studying?
    practitioner: can I just DoRA-finetune Llama3-8B on my historical corpus, or do I need
      to pretrain from scratch to keep later language out?
  answered_by:
  - leakage
  - cholera-example
  - context-pretraining-as-method
- ask:
    plain: do small models trained only on books from one era actually prefer text from that
      era?
    jargon: do time-sliced pretrained models show period-specific perplexity minima, and does
      finetuning reproduce them?
    task: how do I check whether a model I trained on one historical period really stays inside
      its period boundaries?
    practitioner: for period-restricted language modelling, should I pretrain a small model
      per era or finetune one large model?
  answered_by:
  - pretrain-period-specific-ppl
  - leakage
- ask:
    plain: is a model trained on only 10 million words of old books still good enough at English
      grammar to trust?
    jargon: what BLiMP aggregate accuracy do 345M-parameter BabyLlama-2 models trained on
      10M-token period slices reach against a DoRA-finetuned Llama3-8B?
    task: how do I tell whether my tiny period-specific pretrained model has learned enough
      syntax to use for linguistic analysis?
    practitioner: is a 10M-token period model grammatical enough for my study, or will I lose
      too much against a finetuned 8B model?
  answered_by:
  - blimp-aggregate
- ask:
    plain: can models trained on different centuries reveal changes in grammar rather than
      just changes in word meaning?
    jargon: can minimal-pair acceptability judgements across period models detect diachronic
      change in NPI licensing?
    task: how do I use language models to find grammatical or morphological change over time
      instead of lexical semantic change?
    practitioner: if I want to study syntactic change, will a battery of period-pretrained
      models show me anything a word-sense method cannot?
  answered_by:
  - npi-change
  - context-nonlexical-change
- ask:
    plain: how long does it take on one GPU to train a small language model for a single historical
      period?
    jargon: what is the wall-clock cost of the BabyLlama-2 distillation recipe on a 10M-token
      slice versus DoRA finetuning of Llama3-8B?
    task: how do I budget GPU time for training one language model per time period in my corpus?
    practitioner: with a single A100, is pretraining a small period model cheaper for me than
      parameter-efficient finetuning of an 8B model?
  answered_by:
  - training-cost
- ask:
    plain: how accurate is a large language model at guessing the year a book was written?
    jargon: what within-1-year and within-10-year agreement does zero-shot work-date attribution
      by a 4-bit quantized Llama3.3-70B reach against hand-annotated dates?
    task: how do I assign composition dates to thousands of Project Gutenberg texts so I can
      split them into periods?
    practitioner: can I use an open-weight 70B model instead of GPT-4o to date the works in
      my corpus?
  answered_by:
  - date-attribution
- ask:
    plain: can models trained on different eras show when a word picked up a new meaning,
      like railway "station"?
    jargon: can normalized per-word perplexity trajectories across period models separate
      synchronically distinct senses of a single word?
    task: how do I find candidate words whose senses shifted, and then tell the senses apart
      across periods?
    practitioner: if I want to date a specific sense of a word, will period-model perplexity
      curves give me a usable trajectory?
  answered_by:
  - sense-trajectories
- ask:
    plain: can a model trained only on old books still rank a phrase that was not coined until
      much later?
    jargon: do period-pretrained models assign high completion probability to constructions
      first attested after their slice, absent from their training data?
    task: how do I tell whether an early model's high ranking of a later idiom is data leakage
      or genuine prefiguration?
    practitioner: should I treat a period model's preference for a later-attested phrase as
      contamination or as evidence about earlier usage?
  answered_by:
  - prefiguration
- ask:
    plain: what should I read about training separate language models on different historical
      periods for humanities research?
    jargon: which work argues for domain-restricted pretraining over finetuning or model editing
      to guarantee corpus-bounded weights?
    task: where do I start if I want to build language models that only know one era of text
      for discovering language change?
    practitioner: is there a paper I can cite for using per-period pretrained models rather
      than a finetuned large model in a diachronic study?
  answered_by:
  - context-pretraining-as-method
  - context-nonlexical-change
- ask:
    plain: where can I download the code and the word-meaning fill-in-the-blank test set for
      models trained on separate eras?
    jargon: is the date-attribution, slicing, pretraining and OED-derived sense cloze evaluation
      pipeline released?
    task: how do I reuse an existing diachronic pretraining pipeline on my own corpus split
      into different periods?
    practitioner: can I take the historical-perspectival-lm release and run it on my own period
      divisions?
  answered_by:
  - context-pipeline
misreadings:
- 'The period-pretrained models are not better language models than the finetuned baselines:
  they score lower on aggregate filtered BLiMP and complete fewer cloze tasks correctly. Their
  advantage is that their knowledge is bounded by their slice.'
- The monotonic rise in "only NPI licenser present" accuracy is evidence about the 1750-1940
  Project Gutenberg slices, not an established claim about the history of English NPI licensing;
  the authors note that extending it to the whole language would be fraught.
- The "end of the line" and "cholera" results are single hand-inspected cloze items offered
  as illustrations of hypothesis discovery, not aggregate detection scores for sense change.
- Higher cloze success by the finetuned models is not better diachronic performance, since
  part of it comes from recalling senses coined after the model's training slice.
- The 10-million-token slice size is a consequence of wanting 5 equal subcorpora from dated
  Project Gutenberg text, not a claim that 10M tokens is sufficient for knowledge-level historical
  inquiry; the paper suggests larger corpora for that.
terminology:
  leakage: Recall by a period-restricted language model of word senses first attested after
    the end of its training period, measured as top-100 cloze completion success on post-cutoff
    senses.
  maximally filtered BLiMP: The subset of BLiMP minimal pairs in which every word occurs at
    least twice in each of the training corpora being compared, so that all models under comparison
    have in-vocabulary coverage.
  perspectival language model: A language model pretrained only on one delineated slice of
    a corpus, such as a single time period or genre, so that its weights are guaranteed to
    contain no information from outside that slice.
  sense trajectory: The sequence of a word sense's acceptability, measured as normalized per-word
    perplexity, across a battery of models each pretrained on a consecutive period of the
    same corpus.
links_extra:
  code: https://github.com/comp-int-hum/historical-perspectival-lm
  evaluation_harness: https://github.com/sabrinaxinli/evaluation-pipeline-2024
---
