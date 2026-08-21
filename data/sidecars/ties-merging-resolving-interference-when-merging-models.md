---
one_liner: TIES-Merging resolves the two kinds of interference between task vectors -- redundant
  values and sign disagreement -- by trimming, electing a sign, and merging only the parameters
  that agree.
qa:
- ask:
    plain: what does it mean for two fine-tuned models to interfere when their weights are
      combined?
    jargon: what interference between task vectors does TIES-Merging resolve?
    task: how do I combine several fine-tuned versions of one base model into a single model?
    practitioner: should I use TIES-Merging instead of averaging my fine-tuned checkpoints?
  answered_by:
  - context-claim
- ask:
    plain: what steps are involved in combining fine-tuned model weights without retraining?
    jargon: what are the three steps of TIES-Merging -- trim, elect sign, disjoint merge?
    task: how do I merge task vectors so that conflicting parameter updates do not cancel
      out?
    practitioner: do I have to implement trimming and sign election myself to merge my checkpoints?
  answered_by:
  - ties-merging-steps
- ask:
    plain: how much better is careful weight merging than simply averaging fine-tuned models?
    jargon: how much absolute accuracy does TIES-Merging add over task arithmetic in NLP and
      vision?
    task: how much accuracy would I gain switching from weight averaging to interference-aware
      merging?
    practitioner: is switching from averaging to TIES-Merging worth it for my multi-task model?
  answered_by:
  - ties-merging-performance
- ask:
    plain: why does a model built by combining fine-tuned models perform worse than each one
      alone?
    jargon: what are the sources of interference between task vectors during merging?
    task: how do I diagnose why merging two fine-tuned checkpoints lost accuracy?
  answered_by:
  - interference-sources
- ask:
    plain: what happens when two fine-tuned models change the same weight in opposite directions?
    jargon: why does resolving sign conflicts between task vectors matter for merged accuracy?
    task: how do I stop opposing parameter updates from cancelling when I merge models?
  answered_by:
  - sign-conflicts-importance
- ask:
    plain: does dropping most of the small weight changes hurt a merged model?
    jargon: what effect does trimming redundant task-vector values have on merged performance?
    task: how do I decide which parameter changes to keep when merging fine-tuned models?
  answered_by:
  - redundant-parameters-impact
- ask:
    plain: does a model built by merging others still work on tasks none of them were trained
      on?
    jargon: how does TIES-Merging compare with the strongest baseline on out-of-domain generalization
      for T5-Base and T5-Large?
    task: how do I merge fine-tuned models and keep performance on tasks outside their training
      sets?
    practitioner: will a merged model generalize to tasks I never fine-tuned on?
  answered_by:
  - out-of-domain-performance
- ask:
    plain: how many fine-tuned models can be combined before the result gets noticeably worse?
    jargon: how does merged accuracy degrade with the number of task vectors, for averaging
      versus task arithmetic versus TIES-Merging?
    task: how do I merge more than a handful of fine-tuned models without accuracy collapsing?
    practitioner: how many checkpoints can I merge at once before I should stop adding more?
  answered_by:
  - scaling-performance
- ask:
    plain: can several training runs of the same task be combined into one better model?
    jargon: how does TIES-Merging compare with averaging, Fisher merging and ensembling over
      ten same-task checkpoints?
    task: how do I combine multiple runs of one fine-tuning job instead of picking the best
      run?
    practitioner: I have ten fine-tuning runs of the same task -- should I merge them or ensemble
      them?
  answered_by:
  - same-task-checkpoints-performance
- ask:
    plain: is a combined model a good starting point for further training?
    jargon: does a TIES-merged checkpoint initialize downstream fine-tuning better than other
      merging methods?
    task: how do I build a better starting checkpoint for fine-tuning out of models I already
      have?
    practitioner: should I fine-tune from a merged checkpoint or from the original pretrained
      model?
  answered_by:
  - initialization-performance
- ask:
    plain: which weight changes actually carry what a fine-tuned model learned?
    jargon: what happens to task performance when the signs of the top 20% highest-magnitude
      parameters are flipped?
    task: how do I tell which parameters matter before trimming a task vector?
  answered_by:
  - top-k-parameters-importance
- ask:
    plain: how much tuning does weight merging need before it works?
    jargon: how sensitive is TIES-Merging to its scaling coefficient compared with task arithmetic?
    task: how do I pick the scaling coefficient when merging fine-tuned models?
    practitioner: can I merge models without sweeping hyperparameters on a validation set?
  answered_by:
  - hyperparameters-impact
- ask:
    plain: can lightweight adapters trained separately be combined into one?
    jargon: how does TIES-Merging perform when merging PEFT modules across 11 tasks?
    task: how do I merge several LoRA adapters into a single adapter?
    practitioner: should I merge my LoRA adapters or keep loading them one at a time?
  answered_by:
  - peft-performance
- ask:
    plain: does combining fine-tuned image models work as well as combining language models?
    jargon: what accuracy gain does TIES-Merging give on fully fine-tuned ViT-B/32 and ViT-L/14?
    task: how do I merge several fine-tuned vision transformers into one multi-task model?
  answered_by:
  - vision-performance
- ask:
    plain: how much does careful merging help when combining fine-tuned text models?
    jargon: what improvement does TIES-Merging give over baselines on fully fine-tuned T5-Base
      and T5-Large?
    task: how do I merge fine-tuned T5 models across tasks?
  answered_by:
  - nlp-performance
- ask:
    plain: what is a good paper to read about combining fine-tuned models into one model?
    jargon: what work established interference between task vectors as the central problem
      in model merging?
    task: where should I start reading if I want to merge models for multi-task use?
    practitioner: which paper should I cite for interference-aware model merging?
  answered_by:
  - context-claim
claims:
- id: ties-merging-steps
  kind: result
  text: 'TIES-Merging consists of three steps: trimming redundant parameters, resolving sign
    conflicts, and merging only the parameters that align with the final agreed-upon sign.'
  scope: the algorithm as published, where trimming keeps the top 20% of parameters by magnitude
    and the elected sign is whichever carries the larger total magnitude
  evidence: Section 4.2, Figure 1
- id: ties-merging-performance
  kind: result
  text: TIES-Merging outperforms several existing methods in diverse settings, improving performance
    by 2.3% and 1.7% absolute in NLP and vision settings, respectively.
  scope: in-domain evaluation with a validation set available to tune the trimming threshold
    and the scaling coefficient, over the NLP and vision settings of Table 1
  evidence: Table 1
- id: interference-sources
  kind: result
  text: Interference in model merging can stem from redundant parameter values and sign disagreement
    between models.
  scope: task vectors from checkpoints that share one pre-trained initialization, with sign
    conflicts counted after trimming each vector to its top 20% of parameters
  evidence: Section 3, Figure 2
- id: sign-conflicts-importance
  kind: result
  text: Resolving sign conflicts is crucial for maintaining parameter magnitudes and avoiding
    performance drops in merged models.
  scope: (IA)3 models on eleven tasks, comparing merged parameter magnitudes when signs are
    elected against a plain mean over the same trimmed task vectors
  evidence: Figure 9, Figure 10
- id: redundant-parameters-impact
  kind: result
  text: Trimming redundant parameters prevents interference and maintains the performance
    of merged models.
  scope: eleven (IA)3 task vectors trimmed to the top 20% of parameters by magnitude, with
    the rest reset to zero
  evidence: Figure 3, Figure 9
- id: out-of-domain-performance
  kind: result
  text: TIES-Merging outperforms the strongest baseline by 1.0% and 4.4% absolute for T5-Base
    and T5-Large models, respectively, in out-of-domain generalization.
  scope: six tasks held out of the merge, for T5-base and T5-large checkpoints merged with
    a validation set available
  evidence: Table 8, Table 9, Figure 5
- id: scaling-performance
  kind: result
  text: TIES-Merging degrades more slowly than task arithmetic as the number of merged tasks
    grows. At two tasks simple averaging already loses 10% normalized accuracy, where both
    of the others lose almost none.
  scope: T5-Large checkpoints merged over the seven in-domain tasks of Table 1, sampling at
    most 10 subsets for each task count, with accuracy normalized by each task's own fine-tuned
    model
  evidence: Figure 6, Figure 18
- id: same-task-checkpoints-performance
  kind: result
  text: When the merged checkpoints are ten fine-tunings of the same task, TIES-Merging beats
    averaging, Fisher merging and ensembling on all three tasks, and beats task vectors on
    two of the three.
  scope: ten BERT-base checkpoints per task taken from the Hugging Face hub for RTE, MRPC
    and WNLI, each evaluated on the one task it was trained on
  evidence: Figure 7
- id: initialization-performance
  kind: result
  text: A TIES-merged model is a better initialization for fine-tuning than the models other
    merging methods produce, on two of the three downstream tasks tried; averaging wins on
    the third.
  scope: BERT-base checkpoints for the seven GLUE tasks other than the target, merged before
    fine-tuning, with RTE, MRPC and WNLI each taken as the target in turn
  evidence: Figure 8
- id: top-k-parameters-importance
  kind: result
  text: 'The direction of the highest-magnitude parameters is what carries task performance:
    flipping the signs of the top 20% degrades it monotonically, while flipping the bottom
    80% barely moves it.'
  scope: (IA)3 models on eleven tasks, flipping each selected parameter with probability from
    0 to 1 and averaging over three independent runs
  evidence: Figure 10, Figure 11
- id: hyperparameters-impact
  kind: result
  text: TIES-Merging is less sensitive to its scaling coefficient than task arithmetic, holding
    accuracy in a 68-75% band across the values swept against 55-75% for task arithmetic.
  scope: T5-base and T5-large models merged on GLUE, sweeping the scaling coefficient over
    0.8-1.8 and incrementing the trimming threshold in steps of 10
  evidence: Figure 13
- id: peft-performance
  kind: result
  text: TIES-Merging outperforms other methods when merging PEFT models, achieving an average
    enhancement of 2.5% across 11 tasks.
  scope: (IA)3 modules on T0-3B merged over eleven tasks, with a validation set available
    to pick the trimming threshold and the scaling coefficient
  evidence: Table 3
- id: vision-performance
  kind: result
  text: TIES-Merging outperforms other methods when merging fully fine-tuned vision models,
    improving performance by 1.8% and 1.5% for ViT-B/32 and ViT-L/14, respectively.
  scope: ViT-B/32 and ViT-L/14 image encoders fully fine-tuned on eight tasks, merged with
    a validation set available for tuning
  evidence: Table 6, Table 7
- id: nlp-performance
  kind: result
  text: TIES-Merging outperforms other methods when merging fully fine-tuned NLP models, achieving
    an improvement of 0.7% and 3.6% for T5-Base and T5-Large, respectively.
  scope: T5-base and T5-large models fully fine-tuned on seven tasks, merged with a validation
    set available for tuning
  evidence: Table 4, Table 5
- id: context-claim
  kind: context
  text: TIES-Merging introduced interference between task vectors as the thing model merging
    has to resolve, and named trimming, sign election and disjoint merging as the way to resolve
    it.
  scope: as of its 2023 publication, and before the later merging work that decomposes task
    vectors into subspaces rather than trimming them by magnitude
terminology:
  TIES-Merging: 'A method for merging models by addressing interference between parameters,
    consisting of three steps: trimming redundant parameters, resolving sign conflicts, and
    merging only the parameters that align with the final agreed-upon sign.'
superseded_by: []
---
