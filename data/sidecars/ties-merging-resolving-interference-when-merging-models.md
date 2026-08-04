---
key: DBLP:conf/nips/YadavTCRB23
coined: TIES-Merging
gloss: merging fine-tuned models by trimming small changes, electing a sign, and averaging
one_liner: >
  TIES-Merging combines several independently fine-tuned models into one without
  retraining, by discarding small parameter changes and resolving sign conflicts
  before averaging.

qa:
  - q:
      - how do I combine multiple fine-tuned models into one?
      - can I merge fine-tuned models without retraining?
      - how do I build a multitask model from separate task-specific models?
    answers: [no-retraining]
  - q:
      - why does averaging fine-tuned weights hurt performance?
      - what causes interference when merging models?
      - why does task arithmetic degrade as I add more models?
    answers: [interference-sources, sign-conflict]

claims:
  - id: no-retraining
    text: >
      TIES-Merging produces a single multitask model from several task-specific
      fine-tuned checkpoints with no additional training and no access to the
      original training data.
    scope: >
      Checkpoints must share the same architecture and the same pre-trained
      initialisation. Evaluated on T5-base, T5-large, ViT and IA3 adapters.
    evidence: Section 4
  - id: interference-sources
    text: >
      Two sources of interference degrade model merging: redundant parameter
      changes, and disagreement on a parameter's sign across the models being
      merged.
    scope: >
      Demonstrated for parameter-space merging of models fine-tuned from a shared
      initialisation; not a claim about models trained from scratch.
    evidence: Section 3
  - id: sign-conflict
    text: >
      Trimming low-magnitude parameter changes, electing a single sign per
      parameter, and averaging only the agreeing values outperforms plain weight
      averaging and task arithmetic, with the gap widening as more models are merged.
    scope: >
      Up to 7 models in the reported experiments; same architecture and
      initialisation throughout.
    evidence: Table 2, Figure 3

misreadings:
  - It is not a training method. No gradient steps and no training data are required.
  - It does not merge models with different architectures or different pre-trained initialisations.
  - The gain is not from trimming alone; resolving sign disagreement is the component that matters most as the number of models grows.

terminology:
  interference: >
    Used narrowly here for two specific effects during parameter merging --
    redundant parameter values, and sign disagreement across models -- not for
    task interference during multitask training.
  trim: >
    Resetting the parameters that changed least during fine-tuning back to their
    pre-trained values, before any averaging.

links_extra:
  code: https://github.com/prateeky2806/ties-merging
---
Worked example of a sidecar. The claims and scope conditions here are drafted from
the paper and should be checked by an author before this is treated as canonical.
