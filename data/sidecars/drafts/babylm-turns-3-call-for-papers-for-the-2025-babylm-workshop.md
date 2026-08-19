<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced via a forced tool call) + 3 repair rounds. Every claim, number
and scope condition below is a machine's reading of the paper and needs your eyes.

What to check, in the order it pays:

1. Each claim's NUMBER and BASELINE. A magnitude attributed to the wrong baseline is
   the one error here that is worse than saying nothing, because it is quotable.
2. Each SCOPE. This is the field summarisers drop, so it is the field this file exists
   for. If a scope reads like a disclaimer, replace it with the condition that
   actually bounds the result.
3. The MISREADINGS. A drafted misreading is a guess about your readers; you know which
   one keeps happening.
4. `one_liner`: the sentence you will reuse verbatim in the README, the model card and
   the talk abstract. Make it yours.

Then promote it:  python scripts/draft_sidecars.py --accept babylm-turns-3-call-for-papers-for-the-2025-babylm-workshop

Stamp: spec=d57862840a90 checks=2 body=1ed0bf1c7b8f
-->
---
key: charpentier2025babylm
coined: BabyLM Interaction track
gloss: a data-efficient pretraining track where a student model learns from a teacher model's
  feedback within a 100M-word budget
one_liner: The 2025 BabyLM call for papers turns the data-efficient pretraining challenge
  into an EMNLP workshop, adds an Interaction track where a student model learns from an external
  teacher inside a 100M-word budget, and caps all competition entries at 10 epochs over their
  training data.
claims:
- id: workshop-turn
  kind: context
  text: BabyLM, previously run as a data-efficient pretraining competition, became a full
    EMNLP 2025 workshop in its third year. The workshop accepts papers at the intersection
    of cognitive science and language modeling with no requirement to enter any competition
    track.
  scope: The 2025 edition, held 5-9 November at EMNLP in Suzhou; earlier BabyLM editions in
    2023 and 2024 were competitions only.
- id: interaction-track
  kind: result
  text: The 2025 BabyLM Interaction track allows a pre-trained external teacher model in the
    training pipeline. The submitted student model may be exposed to no more than 100M word
    tokens and may itself generate no more than 100M words during training.
  scope: Interaction-track competition entries only; the external model must come from a predetermined
    list on the BabyLM website, and its weights, hidden states and output distribution may
    not be revealed to the submission model.
  evidence: Section 4.1
- id: epoch-cap
  kind: result
  text: The 2025 BabyLM competition caps data exposure at 100M words for Strict-small and
    1B words for all other tracks, counting repeated exposures. For the standard BabyLM corpora
    that amounts in most cases to at most 10 epochs.
  scope: Binds only leaderboard-eligible competition checkpoints; participants may train longer
    and report it in their paper, and workshop papers are exempt. Interaction-track word counts
    sum input words and generated tokens.
  evidence: Section 4.2
- id: compute-correlation-motivation
  kind: result
  text: One stated conclusion of the 2024 BabyLM Challenge is that more compute correlates
    with higher performance, which motivated the 2025 epoch limit on both developmental-plausibility
    and democratization grounds.
  scope: A motivation carried over from the 2024 challenge results rather than a new measurement
    in the 2025 call; the organizers declined to restrict FLOPs.
  evidence: Section 4.2
- id: checkpoints
  kind: result
  text: The 2025 BabyLM competition requires intermediate checkpoints on the HuggingFace Hub
    at increasing intervals. Checkpoints are due every 1M words up to 10M, every 10M words
    up to 100M, and every 100M words up to 1B for tracks other than Strict-small.
  scope: Required of competition submissions so the evaluation pipeline can measure learning
    efficiency and language-acquisition dynamics; precise evaluation details were deferred
    to the pipeline release.
  evidence: Section 4.2
- id: dataset-unchanged
  kind: result
  text: 'The BabyLM training corpus is unchanged from the 2nd BabyLM Challenge: 100M words
    for Strict and 10M for Strict-small. The Multimodal set is 100M words pairing 50% text-only
    with 50% image-text data across 2.9M images.'
  scope: Word counts in Table 1 are approximate and subject to slight changes; the corpus
    is suggested rather than mandatory, since Strict and Multimodal participants may substitute
    their own data within the same word budget.
  evidence: Table 1
- id: corpus-composition
  kind: result
  text: The 100M-word Strict BabyLM corpus is built mostly from child-directed and simplified
    English, with CHILDES contributing 29M words, Project Gutenberg children's stories 26M,
    OpenSubtitles 20M and Simple English Wikipedia 15M.
  scope: Approximate word counts for the strict-track version of the corpus; the multimodal
    version halves these text portions and adds 27M words of Localized Narratives and 23M
    of Conceptual Captions captions.
  evidence: Table 1
- id: human-likeness-award
  kind: result
  text: The 2025 BabyLM evaluation adds psychometric fit to human language learners, including
    reading-time prediction, and scores human-likeness separately from NLP accuracy so that
    a system can win either award.
  scope: The pipeline was rewritten from scratch for 2025 with HuggingFace and plain-PyTorch
    paths; the full task list was deferred to the pipeline release.
  evidence: Section 4.4
- id: interaction-baselines
  kind: result
  text: The 2025 BabyLM Interaction track ships two feedback baselines. One is a PPO baseline
    rewarded by a deberta-v3-xsmall model predicting whether a child utterance would trigger
    a caregiver communicative response; the other is a GPT-2 Small student corrected by Llama-3.1
    Instruct 8B over 20 rounds with SimPO.
  scope: Illustrative examples of instantiating feedback rather than strong systems; the correction
    baseline uses nucleus sampling at p=0.8 for student completions and teacher corrections,
    AdamW at learning rate 0.00005, and SimPO with beta=2 and gamma=1.
  evidence: Section 4.5, Appendix A
- id: multimodal-baselines-unbeaten
  kind: result
  text: No submission to the 2024 BabyLM Multimodal track outperformed the GIT and Flamingo
    baselines, so both are re-released as baselines for 2025.
  scope: The previous year's multimodal submissions, which were few in number.
  evidence: Section 4.5
- id: grounding-negative
  kind: result
  text: BabyLM organizers report that the previous year's submissions did not gain from non-linguistic
    grounding, and require that any linguistic modality such as audio still counts its words
    toward the 100M-word budget.
  scope: Submissions to the 2024 BabyLM challenge, compared informally rather than in a controlled
    experiment; the organizers still encourage new attempts at non-linguistic grounding.
  evidence: Section 5
- id: closed-system-synthetic
  kind: result
  text: Synthetic data is permitted in the BabyLM competition only as a closed system. Any
    tokenizer, parser, augmenter or ancillary language model learned on text has its own training
    words counted against the same 100M-word budget.
  scope: All tracks, including Interaction, where the external model is the sole exception;
    off-the-shelf tools learned on language, such as a pre-existing POS tagger, are not allowed.
  evidence: Section 5
- id: field-entry-point
  kind: context
  text: The BabyLM challenge series frames sample-efficient pretraining as a shared task with
    a human-scale data budget of 100M words or less, bringing cognitive scientists and language-modeling
    researchers to the same leaderboard.
  scope: The series' framing as of the 2025 call; the human-scale budget is an approximation
    of childhood language input, not a validated model of it.
qa:
- q:
  - What is BabyLM and what problem does the challenge address?
  - Where should I start reading about sample-efficient language model pretraining on human-scale
    data?
  - What work brought cognitive science and language modeling together around a shared pretraining
    task?
  answers:
  - field-entry-point
  - workshop-turn
- q:
  - What changed in the 2025 BabyLM challenge compared to 2024?
  - Is BabyLM still a competition in 2025 or has it become a workshop?
  - Can I submit a paper to a data-efficient pretraining workshop without entering its competition?
  answers:
  - workshop-turn
  - interaction-track
  - epoch-cap
- q:
  - What is the BabyLM Interaction track?
  - Can I use a large pre-trained teacher model when training a small student model in a data-efficient
    pretraining competition?
  - How many words is a student model allowed to see and generate when learning from a teacher
    model?
  answers:
  - interaction-track
- q:
  - Is there an epoch limit in the 2025 BabyLM competition?
  - How much repeated exposure to the training data is allowed for BabyLM submissions?
  - Why would a pretraining shared task add a training duration limit?
  answers:
  - epoch-cap
  - compute-correlation-motivation
- q:
  - Did the 2024 BabyLM challenge find that compute matters more than method?
  - What did BabyLM organizers conclude about compute and performance?
  - Why cap data exposure rather than FLOPs in a data-efficient pretraining challenge?
  answers:
  - compute-correlation-motivation
- q:
  - Do BabyLM submissions have to release intermediate checkpoints?
  - At what intervals must BabyLM competition checkpoints be saved?
  - How can a shared task evaluate learning dynamics over the course of pretraining?
  answers:
  - checkpoints
  - human-likeness-award
- q:
  - What data is in the BabyLM training corpus?
  - How many words of CHILDES and children's stories are in the 100M-word BabyLM dataset?
  - Did the BabyLM training data change for 2025?
  answers:
  - dataset-unchanged
  - corpus-composition
- q:
  - How is human-likeness measured in the 2025 BabyLM evaluation?
  - Can a small language model submission win on cognitive plausibility rather than benchmark
    accuracy?
  - Does the BabyLM evaluation suite include reading-time prediction?
  answers:
  - human-likeness-award
- q:
  - What baselines are provided for learning from teacher feedback in BabyLM 2025?
  - How is communicative feedback from a caregiver instantiated as a reward model for a small
    language model?
  - Which models are used as student and teacher in a natural-language correction training
    loop?
  answers:
  - interaction-baselines
- q:
  - Which baselines are used for the BabyLM multimodal track?
  - Did anyone beat GIT and Flamingo in the 2024 multimodal image-text pretraining competition?
  - What is the strongest published baseline for the strict BabyLM tracks?
  answers:
  - multimodal-baselines-unbeaten
- q:
  - Does adding images or other non-linguistic grounding help data-efficient language models?
  - Do audio or multimodal inputs count toward the BabyLM word budget?
  - What have BabyLM submissions found about non-linguistic grounding?
  answers:
  - grounding-negative
  - dataset-unchanged
- q:
  - Can I use synthetic or augmented data in the BabyLM competition?
  - Does a tokenizer or parser trained on text count toward a 100M-word pretraining budget?
  - Am I allowed to use an off-the-shelf POS tagger in a BabyLM pipeline?
  answers:
  - closed-system-synthetic
misreadings:
- 'The 100M-word cap in the BabyLM Interaction track applies to the student submission model,
  not to the external teacher: the teacher may be any pre-trained model from the organizers''
  list and may be fine-tuned or distilled without restriction.'
- 'The 10-epoch figure in the 2025 BabyLM rules is a consequence, not the rule: the actual
  limit is data exposure counted in whitespace-separated words, 100M for Strict-small and
  1B for other tracks, because what counts as an epoch differs across submissions.'
- BabyLM's training duration limit does not restrict compute or FLOPs; the organizers explicitly
  declined a compute cap and limited only the number of words a model sees.
- Submitting a paper to the BabyLM workshop does not require training a model under the competition
  rules, and workshop papers are exempt from the epoch limit.
- 'The BabyLM Strict track does not mandate the provided corpus: participants may train on
  their own data as long as it stays within the 100M-word budget.'
terminology:
  Strict track: A BabyLM competition track in which the submitted language model is trained
    on 100M words of text or less, evaluated on language-only tasks.
  Strict-small track: A BabyLM competition track in which the submitted language model is
    trained on 10M words of text or less.
  submission model: In the BabyLM Interaction track, the participant's own entry, which is
    subject to the 100M-word exposure limit.
  external model: In the BabyLM Interaction track, a secondary pre-trained model used in the
    training pipeline but not entered into the competition, whose weights, hidden states and
    output distribution must stay hidden from the submission model.
  communicative response (CR): A caregiver reply that indicates a child's utterance was understood;
    used in BabyLM's feedback baseline as the target of a binary reward model over child-caregiver
    conversations.
  hidden evaluations: BabyLM evaluation tasks withheld from participants until no less than
    two weeks before the model submission deadline, used to control for overfitting to the
    public task suite.
links_extra:
  website: https://babylm.github.io/
supersedes:
- babylm-2024-call-for-papers
---
