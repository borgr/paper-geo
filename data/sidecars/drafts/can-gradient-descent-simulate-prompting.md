<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced via a forced tool call) + 1 repair round. Every claim, number
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

Then promote it:  python scripts/draft_sidecars.py --accept can-gradient-descent-simulate-prompting

Stamp: spec=8f05813a4658 checks=pass body=f4e3adf122dc
-->
---
key: zhang2025gradientprompting
one_liner: Meta-training a language model with a MAML-style objective whose targets are the
  model's own prompted predictions makes a single gradient step on a passage behave partly
  like conditioning on it, recovering some of the gap between fine-tuning and prompting.
claims:
- id: label-free-targets
  kind: context
  text: '"Can Gradient Descent Simulate Prompting?" asks whether a language model can be meta-trained
    so that a gradient step on new text behaves like putting that text in the prompt. The
    meta-training targets are the model''s own prompted predictions, so no ground-truth labels
    are needed.'
  scope: 'Framed for single-context knowledge updates on Llama 3.2 1B, with four tasks: Character
    Description, Reversal Curse, SQuAD and WikiText. No claim that the objective scales to
    large diverse meta-training corpora.'
- id: inverse-of-icl-as-gd
  kind: context
  text: '"Can Gradient Descent Simulate Prompting?" takes up the inverse of the well-studied
    claim that in-context learning implements gradient descent. It asks instead whether gradient
    descent, given the right initialization, can reproduce the predictions that conditioning
    produces.'
  scope: As of the 2025 arXiv posting; cited prior work covers in-context learning as implicit
    gradient descent and context distillation separately, and no survey of contemporaneous
    work on the inverse direction is offered.
- id: lc-matches-gold
  text: Meta-learning from the model's own prompted (conditioning) predictions gives fine-tuning
    accuracies extremely close to oracle meta-learning from gold labels across the Character
    Description, Reversal Curse, SQuAD and WikiText tasks.
  evidence: Figure 2
  scope: Llama 3.2 1B, one meta-training epoch, inner learning rate 1e-3; standard error of
    all accuracies under ±2%. The gold-label variant is treated as an upper bound rather than
    a separately useful method.
- id: squad-recovery
  text: On SQuAD, meta-training recovers about a quarter of the prompted model's performance
    advantage over naive fine-tuning. On WikiText, it recovers about half of the prompting-versus-fine-tuning
    gap, which the paper attributes to the larger dataset.
  evidence: Section 5.1, Figure 2
  scope: Llama 3.2 1B, a single gradient step on one context, one meta-training epoch; 82031
    SQuAD and 343586 WikiText training records.
- id: reversal-improvement
  text: Meta-trained models improve substantially over base-model fine-tuning on the Reversal
    Curse task, but accuracy on Reversal Curse stays lower than on the Character Description
    task, where the description precedes the name.
  evidence: Figure 2, Section 5.1
  scope: Synthetic datasets of 5000 training and 500 test examples generated in the style
    of Berglund et al.'s reversal-curse data, evaluated on Llama 3.2 1B.
- id: rank-1-suffices
  text: Meta-training only a rank-1 update to the model parameters raises SQuAD fine-tuning
    accuracy from 47.3 to 59.4 and WikiText from 29.1 to 37.5, matching full-rank meta-training
    (58.6 and 37.2).
  evidence: Table 1
  scope: Llama 3.2 1B in the gold-label meta-learning setting, with a full-rank update in
    the inner step; standard error within ±2. Held-out data was used to tune the outer learning
    rate per task.
- id: lora-inner-outer
  text: Constraining both the meta-learned initialization and the inner adaptation step to
    a LoRA adapter reaches 72.0 accuracy on SQuAD fine-tuning, against 45.1 for an untrained
    LoRA adapter and 58.6 for full-rank meta-training. On WikiText the same configuration
    reaches 38.3 versus 32.2 untrained.
  evidence: Table 1
  scope: Llama 3.2 1B, gold-label meta-learning, SQuAD and WikiText only; Character Description
    and Reversal Curse were excluded as too easy. Standard error within ±2.
- id: improvement-needs-gradient
  text: On the SQuAD validation split, 12.8% of items are answered correctly by the meta-trained
    model only after the gradient step on the relevant context, against 3.6% that become correct
    without any context. Most of the gain therefore requires the inner update rather than
    better guessing.
  evidence: Table 4
  scope: Llama 3.2 1B meta-trained on SQuAD; the corresponding training-split figures are
    34.7% and 5.8%, and 55.6% of validation items are answered incorrectly in every condition.
- id: irrelevant-context-hurts
  text: Fine-tuning the meta-trained model on an irrelevant context drawn from the same dataset
    drops SQuAD accuracy to 29.7 from 58.6 with the correct context, below the 35.2 no-context
    baseline. On WikiText the same substitution collapses accuracy to 0.010 from 37.2.
  evidence: Table 5
  scope: Llama 3.2 1B meta-trained models, contexts randomly sampled from the same dataset
    distribution; standard error within ±2.
- id: multi-context-degrades
  text: Meta-training explicitly for batched multi-context inner updates keeps SQuAD accuracy
    above the base model at 4 and 16 sequential updates (51.5 and 46.6 versus 43.6 and 42.6).
    Every multi-update setting still falls well short of the 57.2 reached with a single context.
  evidence: Table 2
  scope: SQuAD only, chosen because its contexts are non-contradictory; Llama 3.2 1B, gold-label
    setting, standard error under ±3 over resampled random groups of updates.
- id: no-cross-dataset-transfer
  text: 'A WikiText meta-trained model transfers almost nothing to SQuAD: SQuAD fine-tuning
    accuracy reaches 47.8 sequentially and 48.0 jointly, against 47.3 with no meta-learning
    and 58.6 for in-domain SQuAD meta-training.'
  evidence: Table 3
  scope: Llama 3.2 1B, WikiText-to-SQuAD direction only, reusing the same SQuAD subset the
    model was originally fine-tuned on; standard error within ±2.
- id: meta-learning-forgetting
  text: WikiText meta-learning accuracy falls from 37.2 to 34.8 after sequential fine-tuning
    on SQuAD, and to the same 34.8 under joint SQuAD-plus-WikiText training. Joint optimization
    therefore costs about as much as forgetting from sequential fine-tuning.
  evidence: Table 3
  scope: Llama 3.2 1B, WikiText meta-learning task with SQuAD as the fine-tuning task; standard
    error within ±2. Only this one task pair was tested.
qa:
- q:
  - Can fine-tuning be made to behave like putting information in the prompt?
  - Is there a way to get a single gradient update to have the same effect as conditioning
    on a passage?
  - What work studies whether gradient descent can simulate prompting?
  answers:
  - label-free-targets
  - inverse-of-icl-as-gd
  - squad-recovery
- q:
  - What should I read on the relationship between in-context learning and gradient descent?
  - Which paper looks at the reverse of 'in-context learning is gradient descent'?
  - Where should I start reading about turning prompts into weight updates?
  answers:
  - inverse-of-icl-as-gd
  - label-free-targets
- q:
  - Do you need labelled answers to distil prompting into weight updates?
  - How well does meta-learning from a model's own prompted outputs compare to using gold
    labels?
  - Is label-free context distillation via MAML as good as supervised meta-learning?
  answers:
  - lc-matches-gold
  - label-free-targets
- q:
  - How much of the prompting-versus-fine-tuning gap does meta-training close on question
    answering?
  - Does a single gradient step on a passage let a model answer questions about it?
  - What fraction of prompted performance is recovered on SQuAD and WikiText?
  answers:
  - squad-recovery
  - lc-matches-gold
- q:
  - Does meta-training help with the reversal curse?
  - Can a model learn 'A is B' from a gradient update and answer 'B is A'?
  - How does the Reversal Curse task compare to the easier description-first task after meta-training?
  answers:
  - reversal-improvement
- q:
  - What rank of parameter update is needed to make a model fine-tune better?
  - Is a low-rank change to the initialization enough to improve gradient-based knowledge
    injection?
  - Does rank-1 meta-training match full-rank meta-training?
  answers:
  - rank-1-suffices
- q:
  - Can LoRA be used for both the meta-learned initialization and the adaptation step?
  - Does restricting the inner fine-tuning step to a low-rank adapter help or hurt?
  - What is the best SQuAD accuracy reported for meta-learned LoRA initializations?
  answers:
  - lora-inner-outer
  - rank-1-suffices
- q:
  - Is a meta-trained language model actually using the context, or just guessing better?
  - How can you tell whether the gradient step on a passage is what produces the correct SQuAD
    answer?
  - What happens if a meta-trained model is fine-tuned on an irrelevant passage?
  answers:
  - improvement-needs-gradient
  - irrelevant-context-hurts
- q:
  - Can a meta-trained model absorb several passages at once?
  - Does accuracy hold up over 4 or 16 successive gradient updates on different contexts?
  - How badly does multi-context updating degrade compared with a single update?
  answers:
  - multi-context-degrades
- q:
  - Does a model meta-trained on one dataset transfer to another?
  - Does WikiText meta-training help on SQuAD question answering?
  - Is meta-learning ability forgotten when a WikiText meta-trained model is later fine-tuned
    on SQuAD?
  answers:
  - no-cross-dataset-transfer
  - meta-learning-forgetting
- q:
  - What model and compute were used in the gradient-descent-simulates-prompting experiments?
  - Which language model was meta-trained to emulate conditioning via fine-tuning?
  answers:
  - label-free-targets
  - lc-matches-gold
misreadings:
- 'Meta-training does not make fine-tuning fully equivalent to prompting: on SQuAD only about
  a quarter of the prompting advantage is recovered, and prompted accuracy (87.7) remains
  far above the best meta-trained fine-tuning accuracy.'
- The finding that a rank-1 update suffices concerns the meta-learned change to the initialization,
  not the amount of capacity needed to store new knowledge at fine-tuning time.
- 'Meta-learning from the model''s own prompted predictions is not ordinary context distillation:
  the targets are used inside a bi-level MAML objective so that a later gradient step on the
  raw context reproduces conditioning, rather than training the model to answer directly.'
- The near-equality between learning from conditioning and learning from gold labels does
  not mean labels are useless in general; the gold-label variant is used as an oracle upper
  bound and is reported as slightly less noisy.
- 'Meta-training is not a drop-in continual-learning method: accuracy degrades substantially
  over 4 and 16 successive context updates, and meta-learning ability partly disappears after
  later fine-tuning on another task.'
- Results are from Llama 3.2 1B with a batch size of 16 on a single 80GB H100 and one meta-training
  epoch, so they are not evidence about what happens at larger model or data scale.
terminology:
  Meta-learning from conditioning: A MAML-style objective that minimizes the KL divergence
    between a frozen teacher model's predictions when conditioned on a context and the student's
    predictions after one gradient step on that same context, requiring no ground-truth answers.
  Inner step: The single gradient update on a context's next-token prediction loss whose effect
    the meta-training objective is trying to make equivalent to placing that context in the
    prompt.
  No Context (NC) evaluation: Scoring a response given only the query, with the context discarded,
    used as the lower bound on how well a gradient-based context update can do.
  Character Description task: A synthetic reversal-curse-style dataset in which the description
    precedes the name in the learned sentence, so that the model must complete a paraphrased
    description with the same name.
  LoRA inner + outer: A configuration in which both the meta-learned initialization and the
    adaptation step are restricted to the same low-rank adapter, rather than adapting all
    model parameters at fine-tuning time.
---
