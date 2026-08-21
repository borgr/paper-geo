---
one_liner: TIES-Merging resolves the two kinds of interference between task vectors -- redundant
  values and sign disagreement -- by trimming, electing a sign, and merging only the parameters
  that agree.
qa:
- ask:
    unsorted:
    - What is TIES-Merging?
    - How does TIES-Merging resolve parameter interference?
  answered_by:
  - context-claim
- ask:
    unsorted:
    - What are the main steps in TIES-Merging?
    - What are the three steps of TIES-Merging?
    - What method does TIES-Merging use to merge models?
  answered_by:
  - ties-merging-steps
- ask:
    unsorted:
    - How does TIES-Merging perform compared to other methods?
    - What are the performance improvements of TIES-Merging over other merging methods?
  answered_by:
  - ties-merging-performance
- ask:
    unsorted:
    - What are the sources of interference in model merging?
    - What causes interference in merging models?
  answered_by:
  - interference-sources
- ask:
    unsorted:
    - What is the importance of resolving sign conflicts in TIES-Merging?
    - Why is resolving sign conflicts important in TIES-Merging?
  answered_by:
  - sign-conflicts-importance
- ask:
    unsorted:
    - What is the impact of redundant parameters in TIES-Merging?
    - How does TIES-Merging handle redundant parameters?
  answered_by:
  - redundant-parameters-impact
- ask:
    unsorted:
    - What is the performance of TIES-Merging on out-of-domain tasks?
    - How does TIES-Merging generalize to out-of-domain tasks?
  answered_by:
  - out-of-domain-performance
- ask:
    unsorted:
    - What is the performance of TIES-Merging when merging different numbers of tasks?
    - How does TIES-Merging scale with the number of tasks?
  answered_by:
  - scaling-performance
- ask:
    unsorted:
    - What is the performance of TIES-Merging when merging checkpoints of the same task?
    - How does TIES-Merging perform when merging multiple checkpoints of the same task?
  answered_by:
  - same-task-checkpoints-performance
- ask:
    unsorted:
    - What is the performance of TIES-Merging when used as an initialization for fine-tuning?
    - How does TIES-Merging perform as an initialization for fine-tuning?
  answered_by:
  - initialization-performance
- ask:
    unsorted:
    - What is the importance of the top-k% parameters in TIES-Merging?
    - How does TIES-Merging handle the top-k% parameters?
  answered_by:
  - top-k-parameters-importance
- ask:
    unsorted:
    - What is the impact of hyperparameters in TIES-Merging?
    - How sensitive is TIES-Merging to hyperparameters?
  answered_by:
  - hyperparameters-impact
- ask:
    unsorted:
    - What is the performance of TIES-Merging when merging PEFT models?
    - How does TIES-Merging perform with PEFT models?
  answered_by:
  - peft-performance
- ask:
    unsorted:
    - What is the performance of TIES-Merging when merging fully fine-tuned vision models?
    - How does TIES-Merging perform with fully fine-tuned vision models?
  answered_by:
  - vision-performance
- ask:
    unsorted:
    - What is the performance of TIES-Merging when merging fully fine-tuned NLP models?
    - How does TIES-Merging perform with fully fine-tuned NLP models?
  answered_by:
  - nlp-performance
- ask:
    unsorted:
    - What is a good paper on merging models?
    - What work established the importance of resolving interference in model merging?
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
