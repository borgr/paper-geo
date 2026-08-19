<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced via a forced tool call) + 2 repair rounds. Every claim, number
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

Then promote it:  python scripts/draft_sidecars.py --accept fusing-finetuned-models-for-better-pretraining

Stamp: spec=d57862840a90 checks=pass body=a962dcfc3b2e
-->
---
claims:
- id: fuse-beats-pretrain
  kind: result
  text: Averaging the weights of several finetuned T5v1.1-small models yields a better base
    model for finetuning than the pretrained model itself. Average accuracy across 3 target
    dataset families rises from 62.40 to 64.72 when the NLI models are fused.
  scope: T5v1.1-small, AdamW without weight decay, 30 English text-classification datasets
    in 3 families (GLUE/SuperGLUE, NLI, TweetEval); the target task is always excluded from
    the source tasks; averaged over 5 seeds.
  evidence: Table 1
- id: intertrain-still-better-when-chosen
  kind: result
  text: Fusing all available finetuned models does not beat carefully chosen intertraining
    on T5v1.1-small. Intertraining on the general dataset family averages 66.48 accuracy over
    3 target families, against 64.72 for the best fused set and 62.40 for the pretrained baseline.
  scope: Fusing all available models indiscriminately, with the intertraining baseline picking
    the model finetuned on the largest source dataset (MNLI for the general family, a known
    strong intertraining task); 5 seeds; no weight decay.
  evidence: Table 1
- id: fusing-target-insensitive
  kind: result
  text: Intertraining is sensitive to which target task it is applied to while fusing is not.
    The best intertraining source family is the one most similar to the target, whereas the
    NLI model set is the best set to fuse for all 3 target families.
  scope: 3 dataset families as both sources and targets (general GLUE/SuperGLUE, NLI, Twitter),
    T5v1.1-small, no weight decay, 5 seeds.
  evidence: Table 1
- id: pairs-beat-max-intertraining
  kind: result
  text: Fusing 2 finetuned models is often better than intertraining with the better of the
    two. In all but 1 of the GLUE model pairs, fusing beats intertraining with the worse of
    the two.
  scope: Pairs of models finetuned on GLUE datasets, evaluated as base models on GLUE targets,
    T5v1.1-small, no weight decay; improvement measured against the pretrained baseline.
  evidence: Figure 2
- id: best-pair-mnli-sst2
  kind: result
  text: Fusing the MNLI and SST2 finetuned models reaches the highest accuracy in the GLUE
    fusing experiment, and the models most useful for intertraining are also the best models
    to fuse.
  scope: GLUE target datasets, T5v1.1-small, no weight decay; MNLI and SST2 are the 2 largest
    general-family training sets and MNLI is a previously reported strong intertraining source.
  evidence: Figure 2
- id: weight-decay
  kind: result
  text: Weight decay of 0.01 in finetuning nullifies the benefit of intertraining but not
    of fusing. On general target datasets intertraining drops from 72.76 to 61.7, level with
    the pretrained baseline's 61.6, while fusing falls only from 68.12 to 65.1.
  scope: T5v1.1-small finetuned with AdamW, decay 0.01 versus none, general (GLUE/SuperGLUE)
    target datasets; absolute accuracies are lower with decay overall. Initial BERT trials,
    pretrained with decay, showed less of the adverse effect.
  evidence: Table 2
- id: stability
  kind: result
  text: 'Fusing gives more stable finetuning than starting from the pretrained model: the
    standard deviation of target accuracy averages 1.21 to 2.27 across fused source families
    against 3.64 for the pretrained base model.'
  scope: T5v1.1-small, 5 random seeds, 3 target dataset families; intertraining is comparably
    stable (1.61 to 2.24), so the stability gain is over the pretrained baseline and not over
    intertraining.
  evidence: Table 3
- id: source-data-size
  kind: result
  text: More source training data produces better fused base models, and fusing gains from
    smaller amounts of source data than intertraining while its improvement also plateaus
    earlier.
  scope: General target datasets, T5v1.1-small, source data amounts swept on a log scale;
    the earlier-plateau trend is described in the paper as noisier than the main monotone
    trend.
  evidence: Figure 3
- id: context-reverse-transfer
  kind: context
  text: Fusing finetuned models for better pretraining proposes reversing the transfer-learning
    pipeline. Rather than reusing a pretrained model to make finetuned models, it recycles
    existing finetuned models by weight averaging into a better base model for new target
    tasks.
  scope: As of the 2022 arXiv preprint; demonstrated only on T5v1.1-small and English text
    classification. Contemporaneous weight-averaging work (Model Soups, Fisher-weighted averaging)
    fuses models for direct use on a task rather than as an initialization for new tasks.
- id: context-generalizes-intertraining
  kind: context
  text: Fusing finetuned models for better pretraining frames intertraining as the special
    case of fusing a single model. Choosing a base model becomes a question of which set of
    finetuned models to average rather than which one to pick.
  scope: 3 dataset families and 30 English classification datasets; all fused models share
    one pretrained initialization, and no theory for why averaging helps is offered.
- id: context-no-source-data
  kind: context
  text: Fusing finetuned models for better pretraining assumes access only to finetuned model
    weights. Neither the source training data nor the compute for massively multitask pretraining
    is required, which is what makes averaging rather than retraining the mechanism.
  scope: As of the 2022 preprint; the assumption rules out data-dependent alternatives such
    as Fisher-information weighting. Relevance depends on finetuned models being shared, estimated
    only indirectly from HuggingFace hub counts and 20 sampled EMNLP 2021 papers.
qa:
- q:
  - Can averaging the weights of several finetuned models give a better starting point than
    the pretrained model?
  - Does weight averaging of finetuned checkpoints improve initialization for a new task?
  - Is a fused model a better base model than the original pretrained one?
  answers:
  - fuse-beats-pretrain
  - stability
- q:
  - Is fusing better than intermediate-task training?
  - Does averaging several finetuned models beat picking one good intermediate task?
  - How does fusing compare to intertraining on a well-chosen source task?
  answers:
  - intertrain-still-better-when-chosen
  - pairs-beat-max-intertraining
- q:
  - Which finetuned models should I average to get a good base model?
  - Does the choice of source models matter when fusing checkpoints?
  - Which pair of GLUE finetuned models makes the best fused initialization?
  answers:
  - best-pair-mnli-sst2
  - fusing-target-insensitive
- q:
  - Does the benefit of averaging finetuned models depend on the target task?
  - Do I need source tasks related to my target task for weight averaging to help?
  - Is intermediate-task transfer more target-dependent than model fusing?
  answers:
  - fusing-target-insensitive
- q:
  - Does weight decay during finetuning affect intermediate-task transfer?
  - Why does intertraining stop helping when AdamW weight decay is used?
  - Is model weight averaging robust to the finetuning optimizer's regularization?
  answers:
  - weight-decay
- q:
  - Does starting from an averaged model make finetuning more stable across seeds?
  - How much does seed variance drop when finetuning from a fused base model?
  - Is training variance lower when initializing from averaged finetuned weights?
  answers:
  - stability
- q:
  - How much source training data is needed for weight averaging to pay off?
  - Does the size of the source datasets change how good a fused base model is?
  - Is fusing more data-efficient than intertraining in the source task?
  answers:
  - source-data-size
- q:
  - What early work established that averaging finetuned model weights makes a better pretrained
    model?
  - What should I read first about model merging as a way to build base models?
  - Which paper proposed recycling existing finetuned checkpoints instead of pretraining from
    scratch?
  - What is a good paper on weight averaging for transfer learning?
  answers:
  - context-reverse-transfer
  - context-generalizes-intertraining
- q:
  - How does model merging for initialization differ from Model Soups and Fisher-weighted
    averaging?
  - Can I merge models without access to their training data?
  - What assumptions does recycling finetuned checkpoints as a base model require?
  answers:
  - context-no-source-data
  - context-reverse-transfer
- q:
  - Is intermediate-task training a special case of model merging?
  - How is picking one finetuned checkpoint related to averaging several of them?
  - What is the relationship between intertraining and fusing model weights?
  answers:
  - context-generalizes-intertraining
coined: Fusing
gloss: averaging the weights of several finetuned models to create a new base model for finetuning
  on a fresh task
one_liner: Fusing averages the weights of several existing finetuned models into a new base
  model that finetunes better and more stably than the pretrained model it came from, at almost
  no cost and without access to any source data.
terminology:
  Fusing: Combining several models finetuned from the same pretrained initialization into
    a single new base model by averaging each shared weight, and then finetuning that base
    model on a target task.
  Intertraining: Using a model already finetuned on some other source task as the initialization
    for finetuning on a target task, rather than starting from the pretrained model.
  Available finetuned models: The set of models assumed to already exist for reuse in an experiment,
    simulated by finetuning the pretrained model on each source task, always excluding the
    target task.
misreadings:
- 'Fusing all available finetuned models does not beat well-chosen intertraining: in the paper''s
  main table the best intertraining setting averages 66.48 against 64.72 for the best fused
  set, and fusing only wins over intertraining when the models to fuse are chosen carefully
  or when weight decay is used.'
- The fused model is not claimed to perform any of the source tasks. It is a meta-learning-style
  starting point, evaluated only after further finetuning on the target task, unlike Model
  Soups or Fisher-weighted averaging which use the merged model directly.
- The results are not evidence that weight averaging works between arbitrary networks. All
  fused models share the same pretrained initialization, and the paper states that in the
  general case averaging weights probably is not beneficial and offers no theory for why it
  helps.
- Fusing does not reduce seed variance relative to intertraining; both are more stable than
  finetuning from the pretrained model, whose average standard deviation is 3.64.
- 'The evidence base is one small model and one modality: T5v1.1-small on 30 English text-classification
  datasets, so the gains should not be read as established for large models or for generation
  tasks.'
---
