---
key: charpentier-etal-2025-babylm-findings
one_liner: The third BabyLM Challenge capped pretraining at 100M words (10M in strict-small),
  added an interaction track where a student learns from a larger teacher model, capped total
  word exposure and required intermediate checkpoints; objective and architecture changes,
  not curriculum learning, produced the winners.
claims:
- id: what-it-is
  kind: context
  text: The Findings of the Third BabyLM Challenge report documents a shared task on data-efficient
    language model pretraining under a budget of at most 100M words. It is the reference point
    for the challenge's 2025 tracks, corpora, evaluation suite and winning systems.
  scope: Covers the third iteration only, with English data and evaluations; the first and
    second iterations are reported in separate findings papers (Warstadt et al. 2023; Hu et
    al. 2024).
- id: new-interaction-track
  kind: context
  text: The third BabyLM Challenge introduced an interaction track in which a student model
    learns from feedback produced by a larger teacher model, rather than only from passive
    exposure to human-written text. Teachers were restricted to a fixed list including Llama3.1-8B-Instruct
    and any LM below 1B parameters.
  scope: The student may see at most 100M external words and generate at most 100M of its
    own; the teacher's weights, hidden states and output distribution may not be exposed to
    the student.
- id: objective-arch-win
  text: The winning systems of the third BabyLM Challenge were a diffusion masked language
    model, an instruction-tuned model, a modular mixture-of-experts model and a reinforcement-learning
    interactive storytelling model. Curriculum learning was the most common approach among
    submissions but won nothing.
  evidence: Figure 1 and Section 6.1
  scope: 32 models submitted across the strict, strict-small, multimodal and interaction tracks;
    winners named separately for human-likeness and for NLP task scores.
- id: interaction-winner-numbers
  text: BLM, the interaction-track winner of the third BabyLM Challenge, scored 20.8 on human-likeness
    and 54.4 on the NLP metric, beating the track's SimPO baseline (20.4 human-likeness, 54.1
    NLP) and taking both awards.
  evidence: Table 3
  scope: Interaction track only; the challenge's own aggregate human-likeness and NLP task
    metrics on the final checkpoint, with the student limited to 100M external words.
- id: strict-winners-numbers
  text: In the strict track of the third BabyLM Challenge, CLASS-IT reached a human-likeness
    score of 20.4 against the best GPT-BERT baseline's 22.5. Simple-Diffusion reached an NLP
    score of 58.4 against the best baseline's 63.0.
  evidence: Table 3
  scope: Strict track (100M words), final-checkpoint full evaluation; the GPT-BERT baselines
    are last year's winning submission, trained on the 100M-word BabyLM corpus.
- id: strictsmall-beats-baseline
  text: In the strict-small track of the third BabyLM Challenge, MoEP reached a human-likeness
    score of 31.5 and a macro average of 42.3, above every baseline in that track. The best
    baseline human-likeness was 19.8 and the best baseline macro average 37.4.
  evidence: Table 3
  scope: Strict-small track (10M words) only; baselines are GPT-BERT variants and GPT-2 Small
    trained on the 10M-word BabyLM corpus. In the strict track the baselines were not beaten
    on the aggregate metrics.
- id: flops-not-predictive
  text: Across the third BabyLM Challenge submissions, macro average score shows no strong
    relationship with training FLOPs in the strict and strict-small tracks; a positive correlation
    appears only in the interaction track.
  evidence: Figure 6
  scope: 32 models under this year's exposure cap of 100M words for strict-small and 1B for
    other tracks; FLOPs self-reported by participants.
- id: cog-ling-correlation
  text: In the third BabyLM Challenge, linguistic task performance and cognitive modeling
    task performance were positively correlated across submitted models in every track except
    strict-small.
  evidence: Figure 3
  scope: Within-track correlations across submitted models, using the new human-likeness tasks
    against BLiMP/GLUE/EWoK; the multimodal track had only 1 submission.
- id: blimp-vs-llama70b
  text: Some strict-track and interaction-track models in the third BabyLM Challenge reach
    BLiMP scores comparable to a 70B-parameter Llama model. On GLUE, all submitted models
    remain below both the human score and the Llama 70B skyline.
  evidence: Figure 4
  scope: BLiMP and GLUE only; GLUE is evaluated after finetuning on subsampled (Super)GLUE
    tasks capped at 10,000 training examples. Does not extend to the cognitive human-likeness
    tasks.
- id: training-dynamics
  text: Across intermediate checkpoints in the third BabyLM Challenge, BLiMP and EWoK scores
    rise with words seen, while wug past-tense accuracy is flat for the first 10-50M words
    before a phase shift upward. Entity tracking shows U-shaped scaling in the strict track.
  evidence: Figure 5 and Section 7
  scope: Checkpoints requested every 1M words to 10M, every 10M to 100M, and every 100M to
    1B, evaluated on the fast (20% subsampled) task versions. Reading-time prediction and
    wug adjective nominalization show no strong relationship with words seen.
- id: gpt-bert-backbone
  text: Grouping third BabyLM Challenge submissions by backbone architecture, GPT-BERT consistently
    yields the strongest cognitive, linguistic and macro average scores, with DeBERTa and
    LTG-BERT also performing strongly.
  evidence: Figure 7
  scope: Backbones compared include BERT, DeBERTa, Flamingo, GIT, GPT-2, GPT-BERT, Llama,
    LSTM, LTG-BERT, ModernBERT, Qwen2 and RoBERTa, aggregated over submissions without controlling
    training data or hyperparameters.
- id: zero-shot-glue-failed
  text: The third BabyLM Challenge organizers tested replacing the finetuning-based (Super)GLUE
    evaluations with zero-shot prompting. They concluded that models at these data budgets
    do not support robust in-context learning, so the finetuning tasks were kept.
  evidence: Section 4.2
  scope: Models trained on 10M-100M words; cost was instead reduced by subsampling tasks larger
    than 10,000 training examples down to 10,000 and dropping highly correlated tasks such
    as QNLI.
- id: multimodal-track-thin
  text: The multimodal track of the third BabyLM Challenge received only 1 submission, BitMar,
    which scored below both the Flamingo and GIT baselines on vision average (26.7 versus
    49.3 and 49.7).
  evidence: Table 2 and Table 3
  scope: Multimodal track only; the organizers attribute part of the difficulty to the provided
    vision embeddings and data download process and plan to move to a more openly licensed
    dataset.
qa:
- ask:
    plain: Where can I read about what happens when language models are trained on only as
      much text as a child hears?
    jargon: Which report documents the shared task on sample-efficient pretraining under a
      100M-word budget and its winning systems?
    task: What should I read first before entering a data-efficient language model pretraining
      competition?
    practitioner: I want a single reference for small-data pretraining results in 2025 --
      which write-up covers the tracks, corpora and winners?
  answered_by:
  - what-it-is
  - objective-arch-win
- ask:
    plain: Can a small language model be taught by a bigger model instead of just reading
      text, and did that work?
    jargon: How does the interaction track let a student model learn from teacher-model feedback,
      and which teachers are permitted?
    task: How do I train a small model using feedback from a larger instruct model within
      a fixed word budget?
    practitioner: If I train a small model with a larger teacher giving it feedback, will
      it actually beat passive text training on human-likeness?
  answered_by:
  - new-interaction-track
  - interaction-winner-numbers
- ask:
    plain: When you can only use a small amount of text, does feeding it in an easy-to-hard
      order actually help?
    jargon: Did curriculum learning submissions win any track of the 2025 data-efficient pretraining
      shared task, and which objectives and architectures did?
    task: Which training objective and architecture should I pick for pretraining on 100M
      words or less?
    practitioner: Should I spend my effort on curriculum ordering or on the model architecture
      and objective for a small-data pretraining run?
  answered_by:
  - objective-arch-win
  - gpt-bert-backbone
- ask:
    plain: Did anyone training on a tiny text budget in 2025 actually beat the organizers'
      own reference models?
    jargon: How did strict, strict-small and interaction track submissions score against the
      GPT-BERT and SimPO baselines on human-likeness and NLP metrics?
    task: How do I tell whether a small-data pretraining recipe genuinely improves on the
      published reference models?
    practitioner: Is any 2025 100M-word submission worth adopting over the provided baseline
      checkpoints?
  answered_by:
  - strictsmall-beats-baseline
  - strict-winners-numbers
  - interaction-winner-numbers
- ask:
    plain: If you spend more computing power training a small-data model, do the scores get
      better?
    jargon: Is macro average score correlated with training FLOPs across submissions in the
      strict, strict-small and interaction tracks?
    task: Should I buy more GPU hours to raise scores when my training corpus is capped at
      100M words?
    practitioner: My data budget is fixed -- is throwing more compute at the run likely to
      pay off?
  answered_by:
  - flops-not-predictive
- ask:
    plain: Do the models that behave most like humans also score best on grammar and language
      tests?
    jargon: Are cognitive modeling scores and linguistic benchmark scores positively correlated
      across 100M-word pretrained submissions?
    task: Can I use linguistic benchmark scores as a proxy for how well a small-data model
      predicts human reading behaviour?
    practitioner: If I optimize my small-data model for BLiMP-style linguistic scores, am
      I also improving its fit to human data?
  answered_by:
  - cog-ling-correlation
- ask:
    plain: Can a model trained on a child-sized amount of text judge grammar as well as a
      huge model?
    jargon: How do 100M-word submissions compare with a 70B Llama skyline on BLiMP and on
      GLUE?
    task: Which evaluations should I expect a 100M-word model to be competitive on, and which
      will it lose?
    practitioner: If I pretrain on 100M words instead of using a 70B model, where will I actually
      lose accuracy?
  answered_by:
  - blimp-vs-llama70b
- ask:
    plain: As a language model reads more and more text, which abilities show up early and
      which appear suddenly?
    jargon: How do BLiMP, EWoK, wug past-tense and entity-tracking scores evolve across intermediate
      checkpoints as words seen increases?
    task: How many words of training do I need before morphological generalization starts
      working in a small model?
    practitioner: Should I keep checkpointing and evaluating throughout a small-data pretraining
      run, or will scores just rise smoothly?
  answered_by:
  - training-dynamics
- ask:
    plain: Can you test a small language model by just prompting it, instead of fine-tuning
      it on each task?
    jargon: Do 100M-word models support robust in-context learning well enough to replace
      finetuning-based (Super)GLUE evaluation with zero-shot prompting?
    task: How should I evaluate a 100M-word model on GLUE-style tasks -- prompt it or finetune
      it?
    practitioner: Can I skip the finetuning step and prompt my small pretrained model to get
      comparable task scores?
  answered_by:
  - zero-shot-glue-failed
- ask:
    plain: Did anyone submit an image-and-text model trained on a tiny data budget, and how
      did it do?
    jargon: How many multimodal-track submissions were received, and how did the vision average
      compare with the Flamingo and GIT baselines?
    task: Is it worth entering the vision-language part of a data-efficient pretraining challenge?
    practitioner: Should I expect a small-data vision-language model to reach the provided
      multimodal baselines?
  answered_by:
  - multimodal-track-thin
- ask:
    plain: Which kind of model works best when you only have 10 to 100 million words of training
      text?
    jargon: Which backbone architectures give the strongest cognitive, linguistic and macro
      average scores at 10M-100M word budgets?
    task: Which backbone should I start from for pretraining on 10M to 100M words?
    practitioner: Should I pick a GPT-BERT style hybrid backbone or a plain masked or causal
      transformer for my small-data run?
  answered_by:
  - gpt-bert-backbone
terminology:
  Strict and Strict-Small tracks: BabyLM Challenge tracks limiting training data to at most
    100M words and at most 10M words respectively, with no other restriction on model or training
    procedure; participants may use the provided BabyLM corpus or build their own within the
    word limit.
  Interaction track: A BabyLM Challenge track in which an external teacher model from a fixed
    list may be placed in the training pipeline, giving scalar or natural-language feedback
    or generating data conditioned on the student's outputs, but never exposing its weights,
    hidden states or output distribution to the student.
  human-likeness score: An aggregate BabyLM metric over tasks measuring psychometric and linguistic
    similarity to human learners — reading-time correlation, age-of-acquisition correlation,
    wug past-tense and adjective nominalization agreement with human preferences, entity tracking
    and COMPS — reported separately from NLP task accuracy.
  word exposure limit: A cap on total training tokens counted with repetition, set in the
    third BabyLM Challenge at 100M words for strict-small and 1B words for the other tracks,
    so that extra epochs over the same data cannot be used to buy performance.
  masked next token prediction (MNTP): A variant of masked language modeling used by GPT-BERT
    in which outputs are shifted as in autoregressive training, allowing one model to be trained
    and evaluated as both an encoder and a decoder.
misreadings:
- 'The third BabyLM Challenge did not show that submissions beat the baselines everywhere:
  in the strict track the GPT-BERT baselines still had the best human-likeness (22.5) and
  best NLP score (63.0), and in the multimodal track the sole submission scored below both
  baselines on vision.'
- 'The finding that FLOPs and performance are weakly related is not evidence that compute
  is irrelevant: a positive correlation still appears in the interaction track, this year''s
  exposure cap removed one of the main ways compute was previously converted into score, and
  hyperparameter tuning remains a compute-dependent advantage.'
- Curriculum learning being the most popular approach in the third BabyLM Challenge is not
  evidence that it was the most effective one; the best-performing entries modified the training
  objective or architecture instead.
- 'Matching a 70B Llama on BLiMP does not mean BabyLM-scale models match large models generally:
  on GLUE all submitted models remain below both the Llama 70B skyline and human scores.'
- The interaction track's teacher model is not distilled into the student in the usual sense
  — exposing the teacher's weights, hidden states or output distribution to the student was
  prohibited, and interaction had to run through text or scalar feedback.
links_extra:
  anthology: https://aclanthology.org/2025.babylm-main.28/
  evaluation pipeline: https://github.com/babylm/evaluation-pipeline-2025
  leaderboard: https://huggingface.co/spaces/BabyLM-community/babylm-leaderboard-2025-alltasks
supersedes:
- findings-of-the-second-babylm-challenge
---
