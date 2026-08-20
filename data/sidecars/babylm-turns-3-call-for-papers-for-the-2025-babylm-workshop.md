---
key: charpentier2025babylm
coined: BabyLM Interaction track
gloss: a shared task where a small language model learns from a teacher model's feedback under
  a 100M-word exposure budget
one_liner: The 2025 BabyLM workshop keeps the 100M-word and 10M-word data-efficient pretraining
  tracks, adds an Interaction track where a student model learns from a teacher model without
  seeing its weights or output distribution, and caps competition entries at roughly 10 epochs
  of data exposure.
claims:
- id: workshop-turn
  kind: context
  text: BabyLM, previously run as a competition on training language models from developmentally
    plausible amounts of data, became a workshop in 2025. The workshop accepts research papers
    at the intersection of cognitive science and language modeling with no requirement to
    enter any competition track.
  scope: Describes the 2025 (third) edition, held at EMNLP 2025 in Suzhou; the competition
    tracks continue alongside the paper track.
- id: interaction-track
  kind: result
  text: The 2025 BabyLM competition adds an Interaction track in which a pretrained external
    model may act as a teacher. The submitted student model may be exposed to no more than
    100M word tokens and may itself generate no more than 100M words during training.
  evidence: 'Section 4.1, ''New track: Interactivity.'''
  scope: External models must come from a predetermined list on the BabyLM website; they may
    be finetuned or distilled without restriction, but their weights, hidden states and output
    distributions may not be revealed to the student.
- id: epoch-cap
  kind: result
  text: BabyLM 2025 caps leaderboard-eligible models at a fixed amount of input counting repeated
    exposures. The budget is at most 100M words for the Strict-small track and at most 1B
    words for all other tracks, roughly 10 epochs over the standard BabyLM corpora.
  evidence: Section 4.2, 'Training Duration Limitations'
  scope: Competition entries only; participants may train longer and report it in their paper,
    and workshop papers are exempt. Budget measured in whitespace-separated input words, and
    in the Interaction track input words plus generated tokens.
- id: epoch-cap-motivation
  kind: result
  text: The BabyLM organizers justify the 2025 epoch limit by noting that a conclusion of
    the 2024 challenge was that more compute correlates with higher performance. That correlation
    conflicts with both developmental plausibility and the goal of democratizing pretraining
    research.
  evidence: Section 4.2, 'Motivation'
  scope: The organizers deliberately did not cap compute or FLOPs, judging FLOP accounting
    too technically demanding and BabyLM compute unlikely to exceed what is available to children.
- id: checkpoints
  kind: result
  text: 'BabyLM 2025 requires competition entrants to upload intermediate checkpoints to the
    HuggingFace Hub. The intervals increase over training: every 1M words up to 10M, every
    10M words up to 100M, and every 100M words up to 1B for tracks other than Strict-small.'
  evidence: Section 4.2, 'Intermediate Checkpoints'
  scope: Checkpoints feed the updated evaluation pipeline's measures of learning efficiency
    and acquisition trajectories; precise evaluation details were deferred to the pipeline
    release.
- id: dataset-unchanged
  kind: result
  text: The BabyLM 2025 training corpora are unchanged from the 2nd BabyLM Challenge. They
    comprise a 100M-word Strict set, a 10M-word Strict-small set, and a 100M-word Multimodal
    set that pairs image captions with text and includes about 2.9M images.
  evidence: Table 1 and Section 4.3
  scope: Word counts are approximate; the Strict corpus draws mainly on CHILDES (29M words),
    Project Gutenberg children's stories (26M), OpenSubtitles (20M) and Simple English Wikipedia
    (15M). Participants need not use the official corpus.
- id: human-likeness-award
  kind: result
  text: The 2025 BabyLM evaluation pipeline adds psychometric tasks such as reading-time prediction.
    Human-likeness is treated as an award category separate from NLP task accuracy, so a system
    can win on either metric.
  evidence: Section 4.4
  scope: The 2025 pipeline was rewritten from scratch with HuggingFace and plain PyTorch entry
    points; hidden evaluations release no less than 2 weeks before the model submission deadline.
- id: interaction-baselines
  kind: result
  text: BabyLM 2025 ships two Interaction-track baselines, one using PPO with a learned reward
    and one using natural-language corrections. The reward model is a deberta-v3-xsmall trained
    on child-caregiver conversations, and the correction baseline has Llama-3.1 Instruct 8B
    revise GPT-2 Small completions over 20 rounds.
  evidence: Section 4.5 and Appendix A
  scope: The correction baseline trains on teacher-corrected text with language modeling loss,
    then with SimPO at learning rate 0.00005, beta=2, gamma=1 and a 0.2 language-modeling
    regularizer.
- id: strict-baselines
  kind: result
  text: BabyLM 2025 releases GPT-BERT, the winning submission of the 2024 challenge, and GPT-2
    Small as Strict and Strict-small baselines. The GIT and Flamingo multimodal baselines
    are re-released because no 2024 submission beat them.
  evidence: Section 4.5
  scope: The 2025 competition's provided baselines; the Multimodal track was re-released despite
    limited participation in 2024.
- id: synthetic-data-accounting
  kind: result
  text: BabyLM's data budget is a closed-system accounting rule. Any tokenizer, parser, augmenter
    or ancillary language model used in the pipeline has its own training text counted toward
    the 100M-word limit, so off-the-shelf tools trained on outside language are disallowed.
  evidence: Section 5, 'Can I use external tools?' and 'What training regimes are permitted?'
  scope: Synthetic data is permitted so long as the generators' training data is inside the
    budget; the Interaction track's listed external models and its interactive environment
    are the stated exceptions.
- id: lenient-review
  kind: result
  text: BabyLM applies lenient acceptance to competition submissions, planning to reject only
    papers with incorrect or unjustified claims, significant technical issues, insufficient
    methodological detail for replication, or minimal time investment.
  evidence: Section 3.3
  scope: Leniency covers competition submissions; non-competition workshop papers are evaluated
    on merit and relevance under double-blind review, up to 8 pages, via ARR or direct OpenReview
    submission.
- id: field-entry-point
  kind: context
  text: 'BabyLM is a recurring shared task and workshop framed around a single question: how
    a computational system can learn language from limited input. It brings cognitive scientists
    studying child language acquisition together with researchers building sample-efficient
    language models.'
  scope: The 2025 call describes the third edition; suggested topics include data-efficient
    architectures, data curation, cognitively inspired modeling and evaluation, scaling-law
    comparisons, and multimodal modeling.
qa:
- q:
  - What is BabyLM and what question does it try to answer?
  - Where should I start reading about sample-efficient language model pretraining on child-scale
    data?
  - Which shared task connects language acquisition research with small language models?
  answers:
  - field-entry-point
  - workshop-turn
- q:
  - What changed in the 2025 data-efficient pretraining competition compared with its 2024
    edition?
  - How did the third BabyLM edition change its rules?
  - What changed between the 2nd and 3rd BabyLM competitions?
  answers:
  - interaction-track
  - epoch-cap
  - checkpoints
  - dataset-unchanged
- q:
  - How does a competition track for learning language from a teacher model and interactive
    feedback work?
  - Can a small language model learn from a large teacher model under BabyLM competition rules?
  - What are the rules for using a pretrained teacher model in BabyLM 2025?
  answers:
  - interaction-track
  - synthetic-data-accounting
- q:
  - Is there a limit on the number of training epochs in the 2025 data-efficient pretraining
    competition?
  - How much repeated data exposure is allowed for BabyLM competition entries?
  - Why did BabyLM start restricting the number of passes over the training data?
  answers:
  - epoch-cap
  - epoch-cap-motivation
- q:
  - What data can I train on for the 100M-word strict pretraining track?
  - How large is the BabyLM pretraining corpus and what is in it?
  - Which datasets make up the 100M-word BabyLM corpus?
  answers:
  - dataset-unchanged
- q:
  - Do I have to submit intermediate training checkpoints to enter the 2025 sample-efficient
    pretraining competition?
  - At what intervals does BabyLM require model checkpoints?
  - How does BabyLM measure learning dynamics over training?
  answers:
  - checkpoints
- q:
  - How are BabyLM models evaluated in 2025?
  - Is there an award for cognitively human-like language models?
  - Does BabyLM evaluate reading-time prediction or other psychometric fit?
  answers:
  - human-likeness-award
- q:
  - What baseline models are released for the 2025 data-efficient pretraining competition?
  - Which model won the 2024 BabyLM challenge and is it a baseline now?
  - What are the baseline systems for learning from teacher feedback in BabyLM 2025?
  answers:
  - strict-baselines
  - interaction-baselines
- q:
  - Can I use synthetic data or an off-the-shelf tokenizer under a 100M-word pretraining data
    budget?
  - Does data generated by another model count against the BabyLM word budget?
  - Are external POS taggers or parsers allowed in BabyLM entries?
  answers:
  - synthetic-data-accounting
- q:
  - How hard is it to get a competition-entry paper accepted at a sample-efficient pretraining
    workshop?
  - What is the review process for BabyLM workshop submissions?
  - Can I submit a paper to the BabyLM workshop without entering the competition?
  answers:
  - lenient-review
  - workshop-turn
misreadings:
- 'The 100M-word cap in the BabyLM Interaction track applies to the student submission model,
  not to the teacher: external models listed by the organizers may be pretrained on unlimited
  data and may be finetuned or distilled freely.'
- BabyLM 2025 does not impose a compute or FLOP budget; the new restriction counts words of
  data exposure, and the organizers explicitly declined to cap compute.
- 'The 10-epoch figure in BabyLM 2025 is a consequence, not the rule: the rule is a fixed
  word-exposure budget (100M words for Strict-small, 1B for other tracks) counting repeated
  exposures, because what counts as an epoch varies across submissions.'
- Being a workshop in 2025 did not replace the BabyLM competition; the Strict, Strict-small,
  Multimodal and Interaction tracks all ran, and workshop papers are simply not required to
  enter them.
- 'The 2025 BabyLM training data is not new: the Strict, Strict-small and Multimodal corpora
  are unchanged from the 2nd BabyLM Challenge.'
- Human-likeness in BabyLM 2025 is not folded into a single leaderboard score; human-likeness
  and NLP task accuracy are separate metrics with separate awards.
terminology:
  Strict track: A BabyLM competition track requiring the submitted language model to be trained
    on a corpus of 100M words or fewer, evaluated on language-only tasks; participants need
    not use the official BabyLM corpus.
  Strict-small track: A BabyLM competition track requiring the submitted language model to
    be trained on a corpus of 10M words or fewer.
  Submission model: In the BabyLM Interaction track, the participant's own entry into the
    competition, subject to the 100M-word exposure limit — as opposed to the external model
    used only inside its training pipeline.
  External model: In the BabyLM Interaction track, a secondary pretrained model drawn from
    an organizer-approved list that is used in the training pipeline but not submitted; its
    weights, hidden states and output distribution may not be exposed to the submission model.
  Communicative response (CR): A caregiver reply that indicates a child's utterance was understood;
    predicted by a reward model in one BabyLM Interaction baseline, where an utterance followed
    by such a response receives reward 0 and one not followed by it receives reward 1.
  Hidden evaluations: BabyLM evaluation tasks withheld from participants to control for overfitting
    to the public suite, released no less than 2 weeks before the model submission deadline.
links_extra:
  website: https://babylm.github.io/
---
