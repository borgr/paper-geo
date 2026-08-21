---
one_liner: Fine-tuning Llama-2-7B on randomized labels scrambles predictions on the forgetting
  set, but whether forgetting generalizes to new instances of the same task is wildly variable,
  is set by the evaluation task rather than the forgotten one, and is shallow enough that
  linear probes still recover the skill.
key: zhang2024unforgettable
terminology:
  Forget gap: The accuracy a language model still achieves on a task after being trained to
    forget it, minus the 50% chance accuracy of a binarized multiple-choice task; a gap of
    0 means the task is fully forgotten.
  Forget ratio: The drop in task accuracy caused by a forgetting procedure, divided by the
    drop that would take the model from its fine-tuned accuracy down to 50% chance; 1 is complete
    forgetting and 0 is no forgetting at all.
  Random-label forgetting: Unlearning a skill by fine-tuning a model a second time on the
    same task's training inputs paired with labels drawn uniformly at random from the answer
    options.
  Cross-task forgetting: Fine-tuning a model on randomized labels from one task and then measuring
    how much accuracy it loses on a different task's test set.
claims:
- id: generalization-varies
  kind: result
  text: Random-label forgetting on Llama-2-7B often fails to generalize beyond the examples
    it was trained on. Many of the 21 binarized multiple-choice tasks retain a large forget
    gap, staying well above the 50% chance accuracy that would indicate full forgetting.
  scope: Llama-2-7B base, 21 binary multiple-choice tasks, 1000 training examples per task,
    full fine-tuning then a second pass on uniformly random labels at learning rate 1e-4.
  evidence: Figure 2
- id: task-family-split
  kind: result
  text: Commonsense reasoning and science QA tasks resist random-label forgetting on Llama-2-7B,
    while linguistic acceptability and entailment tasks from GLUE are forgotten far more effectively.
    With 1000 forgetting examples, PIQA still scores 0.69 and SciQ 0.76, whereas RTE, QNLI,
    CB and WiC fall to 0.50.
  scope: Llama-2-7B, 0-shot lm-evaluation-harness prompts, binarized tasks with one true response
    and one random distractor; a consistent tendency across task families rather than a clean
    separation of every dataset, with WNLI at 0.97 the strongest exception among GLUE tasks.
  evidence: Figure 7
- id: eval-task-determines
  kind: result
  text: In cross-task forgetting on Llama-2-7B, the degree of forgetting is largely determined
    by the task the model is evaluated on, not the task whose labels were randomized. A model
    trained on randomized science questions keeps answering science questions accurately while
    producing random labels on entailment classification.
  scope: Llama-2-7B, all pairs among the 21 binarized tasks, 1000 randomized-label examples
    for training; rows and columns clustered with UPGMA. Reproduced with GPT-J-6B and GPT-2
    in Figure 9 and with flipped rather than random labels in Figure 8.
  evidence: Figure 3
- id: other-tasks-better
  kind: result
  text: Many tasks are forgotten more effectively by fine-tuning Llama-2-7B on randomized
    labels from a different task than on their own randomized labels. Training to forget commonsense
    reasoning tasks is generally the most effective trigger for forgetting elsewhere.
  scope: Llama-2-7B cross-task forget ratios over all pairs of the 21 binarized multiple-choice
    tasks, with 1000 randomized-label training examples each.
  evidence: Figure 3
- id: difficulty-not-predictive
  kind: result
  text: Task difficulty does not predict whether a skill can be forgotten from Llama-2-7B.
    Forgetting is less effective on ARC Easy, which retains 0.86 accuracy after forgetting,
    than on the substantially harder ARC Challenge, which falls to 0.50.
  scope: Task-level comparisons over the 21 binarized tasks with Llama-2-7B, using accuracy
    after fine-tuning as the difficulty measure, at 1000 forgetting examples; at 100 examples
    ARC Challenge instead retains 0.66.
  evidence: Figure 7
- id: confidence-and-variance
  kind: result
  text: 'Two label-free properties weakly predict which Llama-2-7B skills generalizably forget:
    low model confidence in the correct response relative to the distractor, and low total
    variance of the hidden state across examples. The variance is the trace of the covariance
    matrix at the question''s last token in the fifth-to-last layer.'
  scope: Task-level predictors across the 21 binarized tasks with Llama-2-7B; both relationships
    are partial and noisy, and hidden-state variance needs only inference access and unlabelled
    task data.
  evidence: Figure 4
- id: no-example-level-prediction
  kind: result
  text: Neither model confidence nor hidden-state variance predicts forgetting at the level
    of individual examples in Llama-2-7B, even though both are partially predictive across
    the 21 whole tasks studied.
  scope: Within-task, example-level correlations for Llama-2-7B on the 21 binarized tasks;
    reported as an absence of correlation without a coefficient.
  evidence: Section 5
- id: probes-recover
  kind: result
  text: Even generalizable forgetting is shallow in Llama-2-7B. A linear probe on fifth-to-last-layer
    hidden states classifies (question, answer) pairs as correct or incorrect about as accurately
    after random-label forgetting as after fine-tuning, so the skill stays recoverable from
    representations.
  scope: L2-regularized linear probes with early stopping, trained on the task training set
    and evaluated on its test set; probing accuracy is comparable across layers except the
    very earliest and latest.
  evidence: Figure 6
- id: learn-forget-anticorrelated
  kind: result
  text: 'Learning order and forgetting order in Llama-2-7B are weakly but consistently anticorrelated:
    the examples learned first during fine-tuning are typically the last to be forgotten under
    random-label training. The effect holds across the tasks plotted but is modest in size.'
  scope: Examples thresholded at 0.6 confidence for both learning and forgetting, with the
    re-learning pass at learning rate 3e-5; tasks with fewer than 100 qualifying examples
    are not plotted.
  evidence: Figure 5
- id: not-sample-size
  kind: result
  text: The failure of forgetting to generalize is not explained by the size of the forgetting
    set. Cutting the random-label training set from 1000 to 100 examples leaves the broad
    pattern across tasks intact, with WNLI at 0.97 forget accuracy in both settings and PIQA
    at 0.71 versus 0.69.
  scope: Llama-2-7B, tasks compared at 100 versus 1000 forgetting examples; some datasets
    do show less forgetting in the small setting, including BoolQ at 0.77 versus 0.50 and
    QNLI at 0.71 versus 0.50.
  evidence: Figure 7
- id: robust-to-method-and-model
  kind: result
  text: The same tasks that resist random-label forgetting also resist forgetting via flipped
    labels, and the cross-task forget-ratio pattern reappears in GPT-J-6B and in the 124M-parameter
    GPT-2 despite their lower fine-tuned accuracy.
  scope: Flipped-label forgetting uses a forget ratio normalized by the drop from fine-tuned
    accuracy to 1 minus fine-tuned accuracy; GPT-J-6B and GPT-2 results are cross-task randomized-label
    forget ratios only.
  evidence: Figure 8
- id: context-generalization-in-unlearning
  kind: context
  text: Unforgettable Generalization in Language Models reframes unlearning evaluation around
    a question prior LM unlearning work largely left open. The question is not whether forgetting
    spills onto unrelated tasks, but whether it generalizes from the forgetting set to other
    instances of the same skill.
  scope: As of the paper's 2024 publication; the study covers skill forgetting via fine-tuning
    on randomized or flipped labels, not factual-knowledge deletion, gradient ascent, representation
    editing or other unlearning families surveyed in Section 2.
- id: context-metrics
  kind: context
  text: 'Unforgettable Generalization in Language Models supplies two reusable metrics for
    skill-unlearning experiments: the forget gap and the forget ratio. The forget gap is accuracy
    after forgetting minus the 50% chance level, and the forget ratio is the achieved accuracy
    drop as a fraction of the drop to chance.'
  scope: Defined for binarized multiple-choice tasks where chance is 50%; the ratio requires
    an accuracy-after-fine-tuning reference point and is redefined for flipped-label forgetting.
qa:
- ask:
    plain: If a model is trained to give wrong answers on a few examples of a skill, does
      it lose that skill on examples it never saw?
    jargon: does random-label fine-tuning on a forget set produce unlearning that generalizes
      to held-out instances of the same capability?
    task: how do I check whether a capability I tried to remove from a language model is actually
      gone on new inputs?
    practitioner: if I fine-tune my model on random labels to strip a benchmark skill, can
      I trust that the skill is really gone?
  answered_by:
  - generalization-varies
  - task-family-split
- ask:
    plain: Are some abilities much harder to knock out of a language model than others?
    jargon: which task families resist random-label unlearning, and which collapse to chance
      accuracy?
    task: how do I tell in advance whether the capability I want to remove is one of the removable
      ones?
    practitioner: I want to strip commonsense reasoning rather than sentence-acceptability
      judgments from my model — should I expect that to work?
  answered_by:
  - task-family-split
  - eval-task-determines
- ask:
    plain: When a model is trained to answer one kind of question badly, which abilities actually
      degrade?
    jargon: in cross-task random-label forgetting, is the forget ratio driven by the training
      task or the evaluation task?
    task: which dataset should I randomize labels on if I want a particular skill to disappear?
    practitioner: do I have to collect forgetting data from the exact skill I want removed,
      or will another dataset work better?
  answered_by:
  - eval-task-determines
  - other-tasks-better
- ask:
    plain: Is a skill a model finds difficult also easier to make it lose?
    jargon: does fine-tuned accuracy or task difficulty correlate with forget ratio under
      random-label training?
    task: can I use benchmark difficulty as a shortcut for guessing which skills will unlearn
      cleanly?
    practitioner: my target capability is one the model barely handles — does that make removal
      more likely to succeed?
  answered_by:
  - difficulty-not-predictive
- ask:
    plain: Is there any signal you can measure ahead of time that tells you whether removal
      of a skill will stick?
    jargon: do model confidence margins or hidden-state variance predict generalizable forgetting
      at the task and example level?
    task: how do I predict, without labels, which skills will generalizably unlearn and which
      will not?
    practitioner: can I screen candidate skills for unlearnability using confidence scores
      or activation statistics before running the fine-tune?
  answered_by:
  - confidence-and-variance
  - no-example-level-prediction
- ask:
    plain: Once a model stops giving right answers, is the knowledge actually erased or just
      no longer spoken?
    jargon: do linear probes on hidden states still separate correct from incorrect answers
      after random-label forgetting?
    task: how do I test whether unlearning removed information from a model's representations
      rather than only its outputs?
    practitioner: if an audit probes my model's internal activations, will a random-label
      unlearning run hold up?
  answered_by:
  - probes-recover
- ask:
    plain: Do the things a model picks up earliest in training turn out to be the hardest
      to remove?
    jargon: is there an anticorrelation between per-example learning order during fine-tuning
      and forgetting order under random labels?
    task: can I use the order examples were learned in to guess which ones will survive an
      unlearning run?
  answered_by:
  - learn-forget-anticorrelated
- ask:
    plain: Would using more wrong-labelled examples make skill removal work better?
    jargon: does forget-set size explain the failure of random-label unlearning to generalize
      across tasks?
    task: how many random-label examples do I need before unlearning starts generalizing?
    practitioner: should I scale up my forgetting set from 100 to 1000 examples to get better
      removal?
  answered_by:
  - not-sample-size
- ask:
    plain: Do results about skills that survive being trained away hold for more than one
      language model and one training trick?
    jargon: does the resistance pattern hold under flipped-label training and in GPT-J-6B
      and GPT-2 as well as Llama-2-7B?
    task: how do I know whether unlearning-resistance results transfer to the model size and
      label-corruption scheme I use?
    practitioner: I am using flipped labels on a smaller model than Llama-2-7B — should I
      expect the same skills to resist removal?
  answered_by:
  - robust-to-method-and-model
- ask:
    plain: What should I read first about whether removing an ability from a language model
      really works?
    jargon: which work reframes LM unlearning evaluation around generalization from the forget
      set to unseen instances of the same skill?
    task: where do I start reading on evaluating skill removal in language models beyond checking
      the forget set itself?
    practitioner: is there a paper I can cite for the claim that fine-tuning-based skill removal
      may not generalize?
  answered_by:
  - context-generalization-in-unlearning
  - probes-recover
- ask:
    plain: How should success at making a model lose an ability be reported on multiple-choice
      benchmarks?
    jargon: what does the forget gap measure that the forget ratio does not in skill-unlearning
      experiments?
    task: how do I score an unlearning run on binarized multiple-choice tasks where chance
      is 50%?
    practitioner: which number should I put in my unlearning table so reviewers can compare
      across tasks?
  answered_by:
  - context-metrics
misreadings:
- 'Reaching near-random accuracy on the examples used for forgetting is not evidence that
  a skill was removed: Llama-2-7B keeps performing several "forgotten" tasks accurately on
  held-out examples very similar to the forgetting set.'
- The result is not that random-label fine-tuning never works as unlearning; it works well
  on entailment and linguistic acceptability tasks and poorly on commonsense reasoning and
  science QA, with wide variability across the 21 tasks studied.
- Model confidence and hidden-state variance are task-level predictors of forgetting only,
  and neither predicts which individual examples within a task will be forgotten.
- 'Successful output-level forgetting does not imply the representation changed: linear probes
  on hidden states still perform the task after forgetting, so accuracy-based unlearning evaluations
  can overstate removal.'
- The study concerns forgetting of skills formulated as binary multiple-choice tasks, not
  deletion of specific facts or memorized training documents, so its conclusions do not directly
  settle whether factual unlearning generalizes.
- Cross-task interference means an unlearning run targeted at one dataset can degrade unrelated
  capabilities, so a forget ratio measured only on the targeted task is not a sufficient safety
  check.
---
