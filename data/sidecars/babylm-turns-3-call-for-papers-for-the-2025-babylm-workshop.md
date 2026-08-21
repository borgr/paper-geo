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
- ask:
    plain: what is BabyLM and what question about learning language from limited input does
      it try to answer?
    jargon: which venue brings together child language acquisition research and sample-efficient
      language model pretraining?
    task: where do I submit work that sits between cognitive science and small-data language
      modeling?
    practitioner: should I send my paper to BabyLM if I do not want to enter a competition
      track?
  answered_by:
  - field-entry-point
  - workshop-turn
- ask:
    plain: what is new in the 2025 round of the small-data language model competition compared
      with the previous year?
    jargon: which rule changes did the 3rd BabyLM Challenge introduce over the 2nd, in tracks,
      data budget and checkpointing?
    task: I entered the earlier BabyLM challenge, what do I need to change to submit in 2025?
    practitioner: if I already have a BabyLM-style pretraining pipeline, is it still eligible
      under the 2025 rules?
  answered_by:
  - interaction-track
  - epoch-cap
  - checkpoints
  - dataset-unchanged
- ask:
    plain: can a small language model be trained by a bigger model giving it feedback in a
      limited-data competition?
    jargon: how does the BabyLM Interaction track constrain teacher-student setups and the
      student's own generated tokens?
    task: how do I use a large pretrained teacher to train a 100M-word budget model without
      breaking the entry rules?
    practitioner: am I allowed to distil from an off-the-shelf pretrained model in my BabyLM
      2025 entry?
  answered_by:
  - interaction-track
  - synthetic-data-accounting
- ask:
    plain: how many times can a model see the same training text in the small-data pretraining
      competition, and why is there a cap?
    jargon: what epoch or multiple-exposure budget applies to BabyLM 2025 leaderboard eligibility,
      and what motivated it?
    task: how long can I keep training on the 100M-word corpus before my run stops being eligible?
    practitioner: if more compute keeps improving my scores, can I just train for more epochs
      and still submit?
  answered_by:
  - epoch-cap
  - epoch-cap-motivation
- ask:
    plain: how big is the training text used for the small-data language model challenge and
      what is in it?
    jargon: what are the composition and sizes of the Strict, Strict-small and Multimodal
      BabyLM pretraining corpora?
    task: where do I get the pretraining data for a developmentally plausible language model,
      and how much of it is there?
    practitioner: do I need to build my own corpus for BabyLM 2025 or can I reuse the earlier
      release?
  answered_by:
  - dataset-unchanged
- ask:
    plain: do entrants to the small-data language model challenge have to save models partway
      through training?
    jargon: what intermediate checkpoint schedule does BabyLM 2025 require entrants to publish
      for learning-dynamics analysis?
    task: how often should I save and upload checkpoints during a 100M-word pretraining run
      to stay eligible?
    practitioner: how much extra storage and uploading am I committing to if I enter BabyLM
      2025?
  answered_by:
  - checkpoints
- ask:
    plain: is a model judged on how human-like it is, or only on how well it does language
      tasks, in the small-data challenge?
    jargon: does the BabyLM 2025 evaluation pipeline include psychometric measures such as
      reading-time prediction alongside NLP benchmarks?
    task: how do I get credit for a model that fits human reading behaviour rather than topping
      accuracy benchmarks?
    practitioner: my model is not the most accurate but fits human data well, is there a category
      I can win?
  answered_by:
  - human-likeness-award
- ask:
    plain: which starter models are provided for the 2025 small-data language model challenge?
    jargon: what pretrained and Interaction-track baselines does BabyLM 2025 release, including
      the winning 2024 submission and the multimodal ones?
    task: what should I compare my limited-data pretrained model against, and where do the
      teacher-feedback baselines come from?
    practitioner: is there a released baseline I can fork rather than training a BabyLM entry
      from scratch?
  answered_by:
  - strict-baselines
  - interaction-baselines
- ask:
    plain: if I use another model or an existing tagger to prepare training text, does that
      text count against the word limit?
    jargon: how does BabyLM's closed-system data accounting treat tokenizers, parsers and
      auxiliary LMs used for augmentation?
    task: can I augment my 100M-word corpus with synthetic text or off-the-shelf preprocessing
      tools and stay within budget?
    practitioner: is an external POS tagger or pretrained parser going to disqualify my BabyLM
      submission?
  answered_by:
  - synthetic-data-accounting
- ask:
    plain: how strict is reviewing for papers describing entries to the small-data language
      modeling challenge?
    jargon: what acceptance criteria apply to BabyLM competition-entry papers versus its archival
      research submissions?
    task: what do I need to include in a BabyLM entry paper so it is not rejected?
    practitioner: is it worth writing up a BabyLM submission if my results are not competitive?
  answered_by:
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
