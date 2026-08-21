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
    practitioner: What should I read first about training language models on small, child-scale
      amounts of data?
    unsorted:
    - Is there a shared task for sample-efficient language model pretraining?
    - Where did the BabyLM Challenge come from and what did it set up?
  answered_by:
  - shared-task-contribution
- ask:
    unsorted:
    - Can a language model trained on 100 million words beat one trained on trillions?
    - Did any BabyLM submission outperform Llama 2?
    - Which model won the BabyLM Strict track and what did it score?
  answered_by:
  - elc-bert-beats-skylines
  - ltg-bert-architecture-effective
- ask:
    unsorted:
    - Does curriculum learning help when pretraining data is limited?
    - How well did curriculum learning work in the BabyLM Challenge?
    - Is ordering training sentences from easy to hard worth trying for small-data language
      models?
  answered_by:
  - curriculum-learning-largely-unsuccessful
- ask:
    unsorted:
    - Which architecture works best for pretraining on 10M-100M words?
    - Was LTG-BERT effective on developmentally plausible data budgets?
    - What backbone did the winning BabyLM models use?
  answered_by:
  - ltg-bert-architecture-effective
  - elc-bert-beats-skylines
- ask:
    unsorted:
    - How much does going from 10 million to 100 million words of pretraining data actually
      buy you?
    - Did BabyLM Strict-track models beat Strict-Small models by much?
    - Is a 10x increase in pretraining data worth it at this scale?
  answered_by:
  - strict-small-close-to-strict
- ask:
    unsorted:
    - Did adding images or audio help language models trained on small data in BabyLM?
    - How did multimodal submissions to the BabyLM Loose track perform?
    - Does multimodal input improve sample efficiency for language modelling?
  answered_by:
  - loose-track-underperformed
- ask:
    unsorted:
    - How close are small-data language models to human grammar performance?
    - What BLiMP accuracy did the best BabyLM model reach relative to humans?
    - Can models trained on child-scale data pass minimal-pair grammar tests?
  answered_by:
  - blimp-near-human
- ask:
    unsorted:
    - Do language models trained on small corpora prefer syntactic or surface generalizations?
    - What did MSGS reveal about the inductive bias of BabyLM models?
    - Does linguistic inductive bias require billions of words of pretraining?
  answered_by:
  - msgs-negative-bias
- ask:
    unsorted:
    - Do language models understand hypernym and lexical entailment relations?
    - How did BabyLM models do on the Hypernym test suite?
    - Which BLiMP Supplement task defeated every model including the skylines?
  answered_by:
  - hypernym-at-chance
- ask:
    unsorted:
    - What new evaluation tasks did the BabyLM Challenge add beyond BLiMP and GLUE?
    - Which BLiMP Supplement suite best separates strong from weak small-data models?
    - Can language models track pronoun shifts across a change of speaker?
  answered_by:
  - turn-taking-discriminative
  - hypernym-at-chance
- ask:
    unsorted:
    - Can small language models predict the age at which children acquire words?
    - Did any BabyLM submission beat the baseline on age-of-acquisition prediction?
    - How well do BabyLM models align with children's word learning?
  answered_by:
  - aoa-no-submission-beats-baseline
- ask:
    unsorted:
    - What practical tricks improved sample efficiency in the BabyLM Challenge?
    - Does shortening context length or sentence-level batching help low-resource pretraining?
    - Did knowledge distillation help models trained on 10 million words?
  answered_by:
  - short-sequences-and-distillation-work
- ask:
    unsorted:
    - Did the BabyLM Challenge limit compute as well as data?
    - How many epochs did the winning BabyLM model train for?
    - Were data-limited pretraining winners actually cheap to train?
  answered_by:
  - compute-not-constrained
  - ltg-bert-architecture-effective
- ask:
    unsorted:
    - Do better BLiMP and GLUE scores mean a model is a better cognitive model of reading?
    - Does BabyLM benchmark performance correlate with predicting human reading times?
    - Which BabyLM paper won the award for outstanding evaluation and what did it find?
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
