---
claims:
- id: elc-bert-beats-skylines
  text: ELC-BERT, trained on 100M words in the BabyLM Strict track, reached an aggregate score
    of 0.74. That is above the Llama 2 skyline at 0.71, trained on 2T tokens, and above RoBERTa-base
    at 0.70 trained on its full corpus.
  kind: result
  evidence: Table 2
  scope: (Super)GLUE was the one task where ELC-BERT did not beat the skylines, at 0.78 against
    Llama 2's 0.84; Llama 2 was evaluated on (Super)GLUE by in-context learning.
- id: curriculum-learning-largely-unsuccessful
  text: Curriculum learning was the most popular BabyLM 2023 approach, attempted by 13 of
    31 teams (41.9%), and the majority of those attempts produced no consistent improvement
    across the BabyLM evaluation tasks.
  kind: result
  evidence: Section 7.4
  scope: Curricula ranking by surprisal, lexical frequency, length, syntactic complexity,
    dataset difficulty, vocabulary size and objective difficulty, on the 10M-word and 100M-word
    English BabyLM corpora.
- id: ltg-bert-architecture-effective
  text: The two top BabyLM Strict-track systems, ELC-BERT at 0.74 aggregate and Boot-BERT
    at 0.70, both build on the LTG-BERT encoder architecture. The participants' own baselines
    indicate the backbone rather than their added modifications drove most of the gain.
  kind: result
  evidence: Table 2
  scope: Encoder-only masked language models on 100M-word and 10M-word English BabyLM corpora,
    trained for hundreds to thousands of epochs; ELC-BERT used over 450 epochs in Strict and
    over 2000 in Strict-Small.
- id: strict-small-close-to-strict
  text: BabyLM Strict-track models trained on 100M words did not outperform Strict-Small models
    trained on 10M words by a large margin. Only 2 Strict-track models achieved higher GLUE
    scores than the best Strict-Small model.
  kind: result
  evidence: Section 7.1
  scope: 162 submitted models across the three 2023 tracks, evaluated on the vocabulary-filtered
    BabyLM versions of BLiMP, BLiMP Supplement, (Super)GLUE and MSGS; the Strict corpus is
    98.04M words and Strict-Small 9.96M.
- id: loose-track-underperformed
  text: BabyLM Loose-track models, which could add unlimited non-linguistic data to a 100M-word
    text budget, tended to score lower in aggregate than Strict-Small models limited to 10M
    words of text.
  kind: result
  evidence: Section 7.1
  scope: 20 Loose-track models from 8 participants in 2023; few multimodal submissions were
    received, and one text-and-audio system (WhisBERT) was reported undertrained.
- id: blimp-near-human
  text: The best BabyLM 2023 submission came within about 3% of reported human performance
    on BLiMP, despite training on at most 100M words.
  kind: result
  evidence: Section 7.1
  scope: Zero-shot minimal-pair accuracy on the vocabulary-filtered BLiMP used in the challenge;
    human performance is the figure reported by Warstadt et al. (2020a).
- id: msgs-negative-bias
  text: MSGS Matthews correlations for BabyLM 2023 systems were largely negative, showing
    that models trained on 10M-100M words prefer surface features over linguistic ones in
    ambiguous contexts. ELC-BERT was the exception, at -0.01 in Strict-Small and -0.10 in
    Strict against Llama 2's -0.24.
  kind: result
  evidence: Table 8
  scope: Six ambiguous MSGS subtasks under finetuned evaluation; macro-average MCC for the
    top systems per track plus baselines and skylines. Llama 2 was fully finetuned on MSGS.
- id: hypernym-at-chance
  text: On the Hypernym test suite of the BLiMP Supplement, every BabyLM 2023 system and both
    skylines scored near chance, between 0.45 and 0.50 accuracy.
  kind: result
  evidence: Table 9
  scope: Zero-shot minimal-pair scoring on 860 semi-automatically templated lexical-entailment
    items phrased as logical statements.
- id: turn-taking-discriminative
  text: The Turn-Taking suite of the BLiMP Supplement separated BabyLM 2023 systems sharply,
    with ELC-BERT (Strict) reaching 0.92 against RoBERTa's 0.73 and Llama 2's 0.83, while
    some systems scored near chance.
  kind: result
  evidence: Table 9
  scope: 280 templated dialogue minimal pairs on indexical pronoun choice across a speaker
    change, scored zero-shot; transcribed dialogue is a large share of the BabyLM corpus.
- id: aoa-no-submission-beats-baseline
  text: On the optional age-of-acquisition prediction task, no BabyLM 2023 Strict-Small submission
    beat the OPT-125M baseline's mean average deviation of 2.03 months, with the best submissions
    at 2.05.
  kind: result
  evidence: Table 11
  scope: 7 of 31 teams (22.6%) evaluated on AoA prediction, almost all in Strict-Small; MAD
    in months across cross-validation folds.
- id: short-sequences-and-distillation-work
  text: Reducing context length or using single sentences as training examples, and distilling
    a student from a teacher trained on the same corpus, were the BabyLM 2023 modifications
    that most consistently improved scores.
  kind: result
  evidence: Section 7.4
  scope: Based on hand-coding 162 submitted models into 9 approach categories and on participants'
    own controlled comparisons, not on organizer-run ablations; English BabyLM corpora of
    10M and 100M words.
- id: shared-task-contribution
  text: The BabyLM Challenge established a shared task and public leaderboard for pretraining
    language models on developmentally plausible budgets of 10M or 100M words. It supplied
    a fixed corpus of child-directed speech, dialogue and children's literature plus a common
    evaluation pipeline.
  kind: context
  scope: First iteration, 2023, English only, 31 papers and 162 models across the Strict,
    Strict-Small and Loose tracks; earlier data-limited work existed (LTG-BERT, BabyBERTa,
    MiniPile) but not as a community shared task with a common corpus and leaderboard.
- id: compute-not-constrained
  text: The BabyLM 2023 rules capped training data but not compute, and the winning Strict
    submission consumed roughly as many training samples as BERT despite a training set only
    about 3% as large.
  kind: result
  evidence: Section 8
  scope: The 2023 iteration's rules, under which repeated epochs did not count against the
    word budget; the organizers flag compute efficiency as a target for future iterations.
- id: benchmark-vs-psycholinguistic
  text: A BabyLM 2023 submission awarded for outstanding evaluation found that models scoring
    better on the BabyLM benchmark tasks were not better at predicting human reading difficulty.
  kind: result
  evidence: Section 7.3
  scope: Decoder-only GPT-style models trained by Steuer et al. (2023) on BabyLM data; a single
    submission's finding, not an organizer-run meta-analysis across all 162 models.
qa:
- ask:
    plain: Is there an open competition for training language models on the amount of language
      a child hears?
    jargon: What shared task benchmarks sample-efficient pretraining on developmentally plausible
      corpora of 10M or 100M words?
    task: Where can I find a fixed small-scale pretraining corpus and evaluation pipeline
      to test my own language model?
    practitioner: If I want to compare my small-data pretraining run against others, is there
      an existing leaderboard I can enter?
  answered_by:
  - shared-task-contribution
- ask:
    plain: Can a language model trained on 100 million words of text score better than one
      trained on trillions?
    jargon: Did any BabyLM Strict-track submission exceed the Llama 2 and RoBERTa-base skylines
      on the aggregate evaluation score?
    task: How do I find out what the strongest 100M-word pretrained encoder achieved and what
      it was compared against?
    practitioner: Should I expect a model I pretrain on 100M words to be competitive with
      off-the-shelf large models on grammar and understanding benchmarks?
  answered_by:
  - elc-bert-beats-skylines
  - ltg-bert-architecture-effective
- ask:
    plain: Does feeding a language model simple text before hard text help when there is very
      little training data?
    jargon: Did curriculum learning yield consistent gains for BabyLM 2023 submissions across
      the evaluation suite?
    task: How do I decide whether to order my pretraining data from easy to hard when data
      is capped at 100M words?
    practitioner: I only have 10M words to pretrain on, is curriculum learning worth my engineering
      time?
  answered_by:
  - curriculum-learning-largely-unsuccessful
- ask:
    plain: Which model design worked best for training on only 10 to 100 million words of
      text?
    jargon: Was the LTG-BERT encoder backbone responsible for the top aggregate scores on
      developmentally plausible data budgets?
    task: Which architecture should I start from if I am pretraining on a 100M-word corpus?
    practitioner: Do I get more from picking a stronger encoder backbone or from adding my
      own training modifications at small data scale?
  answered_by:
  - ltg-bert-architecture-effective
  - elc-bert-beats-skylines
- ask:
    plain: How much better does a language model get when its training text goes from 10 million
      to 100 million words?
    jargon: Did BabyLM Strict-track models trained on 100M words outperform Strict-Small models
      trained on 10M words on GLUE and aggregate scores?
    task: How do I decide whether collecting 10x more pretraining text will actually raise
      my scores at this scale?
    practitioner: Is it worth spending effort to get 100M words of clean text if I already
      have 10M?
  answered_by:
  - strict-small-close-to-strict
- ask:
    plain: Did giving language models images or other non-text input help when their text
      data was limited?
    jargon: How did BabyLM Loose-track submissions with unlimited non-linguistic data compare
      in aggregate to 10M-word Strict-Small models?
    task: Should I add visual or audio data to a small text corpus to improve my model's language
      scores?
    practitioner: I have image-caption data available on top of 100M words of text, will using
      it beat a text-only model trained on far less?
  answered_by:
  - loose-track-underperformed
- ask:
    plain: How close to human accuracy on grammar tests can a model trained on a child-sized
      amount of text get?
    jargon: What BLiMP minimal-pair accuracy did the best BabyLM 2023 submission reach relative
      to reported human performance?
    practitioner: If I pretrain on at most 100M words, how much grammatical acceptability
      performance am I giving up compared with humans?
  answered_by:
  - blimp-near-human
- ask:
    plain: When a sentence can be read two ways, do models trained on small amounts of text
      go by word patterns or by grammar?
    jargon: What did MSGS Matthews correlations reveal about linguistic versus surface inductive
      bias in models trained on 10M-100M words?
    task: How do I tell whether my small-data pretrained model generalizes on syntactic features
      rather than surface cues?
    practitioner: Do I need billions of words of pretraining before my model prefers linguistic
      generalizations over surface ones?
  answered_by:
  - msgs-negative-bias
- ask:
    plain: Can language models tell that a robin is a bird and not the other way round?
    jargon: How did BabyLM 2023 submissions and the skylines score on the Hypernym suite of
      the BLiMP Supplement?
    practitioner: Should I trust a small pretrained model to handle lexical entailment between
      general and specific words?
  answered_by:
  - hypernym-at-chance
- ask:
    plain: What extra language tests did the BabyLM Challenge add beyond standard grammar
      and understanding benchmarks?
    jargon: Which BLiMP Supplement suites, such as Turn-Taking and Hypernym, discriminate
      between BabyLM systems and which saturate at chance?
    task: Which evaluation suites should I use if I want to separate strong from weak models
      pretrained on 10M-100M words?
    practitioner: If I run the BabyLM Supplement suites on my model, which of them will actually
      tell me something about it?
  answered_by:
  - turn-taking-discriminative
  - hypernym-at-chance
- ask:
    plain: Can a language model predict the age at which children learn particular words?
    jargon: Did any BabyLM 2023 Strict-Small submission beat the OPT-125M baseline on age-of-acquisition
      prediction measured by mean average deviation?
    task: How do I check whether a small pretrained model's word learning lines up with children's
      acquisition order?
    practitioner: Is a BabyLM-style model a better fit than a plain 125M-parameter baseline
      if I want to model children's word acquisition?
  answered_by:
  - aoa-no-submission-beats-baseline
- ask:
    plain: Which training tweaks actually helped models learn more from a small amount of
      text?
    jargon: Which modifications, such as reduced context length, sentence-level examples or
      same-corpus distillation, consistently improved BabyLM scores?
    task: What changes should I make to my pretraining recipe to squeeze more out of a 10M-100M
      word corpus?
    practitioner: I am pretraining on 10 million words, should I shorten sequences or distill
      from a teacher trained on the same data?
  answered_by:
  - short-sequences-and-distillation-work
- ask:
    plain: Was the amount of computation limited in the child-scale language model competition,
      or only the amount of text?
    jargon: Did the BabyLM 2023 rules constrain compute alongside the data budget, and how
      many training samples did the winning Strict submission consume?
    task: How do I estimate the training cost of reproducing a winning 100M-word pretrained
      model?
    practitioner: If I train on only 100M words, can I expect the run to be cheap, or will
      I need as many training steps as BERT?
  answered_by:
  - compute-not-constrained
  - ltg-bert-architecture-effective
- ask:
    plain: If a model scores higher on grammar and language understanding tests, does it also
      match how hard humans find text to read?
    jargon: Does BabyLM aggregate benchmark performance correlate with predicting human reading
      times as a psycholinguistic measure?
    task: How do I choose a small pretrained model if what I need is a predictor of human
      reading difficulty?
    practitioner: Can I pick the top-scoring BabyLM model as my cognitive model of reading,
      or is benchmark rank the wrong signal?
  answered_by:
  - benchmark-vs-psycholinguistic
one_liner: The BabyLM Challenge is a shared task in which participants pretrain language models
  on a fixed 10M- or 100M-word developmentally plausible corpus, and in its 2023 first iteration
  the winning LTG-BERT-based submission outscored Llama 2 and RoBERTa-base in aggregate while
  most curriculum-learning attempts failed.
key: warstadt2023babylm
coined: BabyLM Challenge
gloss: shared task on pretraining language models with as little text as a child hears
terminology:
  Strict track: BabyLM Challenge track requiring models to train exclusively on the released
    100M-word English corpus of child-directed speech, dialogue and children's literature.
  Strict-Small track: BabyLM Challenge track requiring models to train exclusively on a 10M-word
    subsample of the released BabyLM corpus, roughly the linguistic input of a child's first
    two to five years.
  Loose track: BabyLM Challenge track allowing unlimited non-linguistic data (audio, images,
    code, music) and expert annotations alongside a 100M-word text budget that covers all
    language data used for any model in the pipeline.
  skyline: In the BabyLM Challenge, a reference model trained on its full unrestricted corpus
    — RoBERTa-base and Llama 2 70B — run through the same evaluation pipeline to bound what
    large-scale pretraining achieves.
  BLiMP Supplement: 'Five minimal-pair test suites released for the BabyLM Challenge covering
    phenomena BLiMP omits: hypernymy, subject-auxiliary inversion, turn-taking, and easy and
    tricky question-answer congruence.'
  MSGS: 'Mixed Signals Generalization Set: a finetuning benchmark whose training labels are
    ambiguous between a syntactic and a surface generalization, scored by Matthews correlation
    with the syntactic generalization, so 1 means systematic linguistic bias and -1 systematic
    surface bias.'
  age-of-acquisition prediction: Task converting a language model's average word surprisals
    into predicted ages at which children acquire those words, scored by mean average deviation
    in months from measured child acquisition ages.
misreadings:
- 'ELC-BERT beating the Llama 2 and RoBERTa-base skylines on the BabyLM aggregate score is
  not a win on every task: Llama 2 scored higher on (Super)GLUE (0.84 vs 0.78), and the aggregate
  weights zero-shot grammar and MSGS at 70% combined.'
- The BabyLM Challenge's data budget is not a compute budget. Repeated epochs cost nothing
  under the 2023 rules, and the winning Strict submission trained for over 450 epochs, so
  its results do not show that sample-efficient pretraining is cheap.
- Curriculum learning being largely unsuccessful in BabyLM 2023 is a finding about the specific
  curricula submitted — surprisal, frequency, length, syntactic complexity, vocabulary growth
  — not a proof that no data ordering can help; the Loose-track winner used dataset-level
  ordering and one linguistically motivated curriculum found improvements.
- 'Near-chance Hypernym scores in the BLiMP Supplement do not establish that language models
  lack knowledge of lexical entailment: the items are unnatural logical statements out of
  domain for the models, and there is no a priori reason logically invalid statements should
  be less probable.'
- BabyLM (Super)GLUE and MSGS numbers are not comparable to published GLUE or MSGS results,
  because evaluation examples containing words appearing fewer than twice in the Strict-Small
  corpus were filtered out.
- Loose-track models scoring below Strict-Small models is not evidence that multimodal training
  hurts language learning in general; few multimodal submissions were received, and one text-and-audio
  system was reported undertrained.
links_extra:
  anthology: http://aclanthology.org/2023.conll-babylm.1/
  leaderboard: https://dynabench.org/babylm
  data: https://github.com/babylm/babylm_data_preprocessing
  evaluation_pipeline: https://github.com/babylm/evaluation-pipeline
  submissions: https://github.com/babylm/submissions2023
---
