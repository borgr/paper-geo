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
- ask:
    plain: if I average together the weights of several models that were each fine-tuned on
      a different task, is the result a better starting point for training on a new task than
      the original pretrained model?
    jargon: does weight averaging of multiple finetuned checkpoints yield a stronger initialization
      for downstream finetuning than the pretrained backbone?
    task: how do I build a better base checkpoint for a new task out of finetuned models I
      already have lying around?
    practitioner: should I start my next finetuning run from an average of my old finetuned
      checkpoints instead of the pretrained release?
  answered_by:
  - fuse-beats-pretrain
  - stability
- ask:
    plain: is averaging a bunch of models trained on other tasks as good as first training
      on one carefully picked helper task?
    jargon: does fusing all available finetuned checkpoints outperform intermediate-task training
      on a well-selected source task?
    task: how do I choose between averaging many source checkpoints and running a single intermediate-task
      training stage before my target task?
    practitioner: I already know which helper task transfers well to my target task, so is
      averaging models worth doing instead?
  answered_by:
  - intertrain-still-better-when-chosen
  - pairs-beat-max-intertraining
- ask:
    plain: when averaging fine-tuned models to make a starting point, does it matter which
      models go into the average?
    jargon: which source checkpoints should be selected for weight fusion, and are the best
      fusion candidates the same as the best intermediate-task donors?
    task: how do I pick which finetuned GLUE checkpoints to average into a base model for
      a new task?
    practitioner: can I just throw every finetuned checkpoint I have into the average, or
      do I need to select the pair?
  answered_by:
  - best-pair-mnli-sst2
  - fusing-target-insensitive
- ask:
    plain: does averaging finetuned models help every new task equally, or do I have to redo
      the choice of models for each new task?
    jargon: is fused-checkpoint initialization less target-task sensitive than intermediate-task
      transfer?
    task: how do I avoid re-selecting a source task every time I move to a new target task?
    practitioner: can one averaged base model serve all my target tasks, or must I tune source
      selection per task?
  answered_by:
  - fusing-target-insensitive
- ask:
    plain: does using weight decay while finetuning wipe out the gains from training on a
      helper task first?
    jargon: how does AdamW weight decay during finetuning interact with the benefit of intermediate-task
      training versus checkpoint fusion?
    task: how do I keep the advantage of a better starting checkpoint when my finetuning recipe
      uses weight decay?
    practitioner: my finetuning recipe uses weight decay of 0.01, so will a fused starting
      point still help me?
  answered_by:
  - weight-decay
- ask:
    plain: does starting from an averaged model make training results vary less from one random
      seed to another?
    jargon: does initializing from fused finetuned weights reduce across-seed standard deviation
      of target-task accuracy?
    task: how do I cut the seed-to-seed variance in my finetuning runs?
    practitioner: my finetuning results swing a lot between seeds, would starting from averaged
      checkpoints steady them?
  answered_by:
  - stability
- ask:
    plain: how much training data do the donor models need before averaging them makes a useful
      starting point?
    jargon: how does source-task training set size affect the quality of a fused base model
      relative to intermediate-task training?
    task: how do I tell whether my source checkpoints were trained on enough data to be worth
      averaging?
    practitioner: my source tasks only have small datasets, is averaging their checkpoints
      still worth it?
  answered_by:
  - source-data-size
- ask:
    plain: what research first suggested making a better starting model by averaging models
      people had already fine-tuned?
    jargon: which work proposed recycling finetuned checkpoints via weight averaging as a
      replacement for the pretrained initialization in transfer learning?
    task: where should I start reading about reusing existing finetuned checkpoints instead
      of pretraining a new base model?
    practitioner: what should I read first if I want to build base models out of finetuned
      checkpoints I already have?
  answered_by:
  - context-reverse-transfer
  - context-generalizes-intertraining
- ask:
    plain: what do you actually need to have on hand to turn a pile of fine-tuned models into
      a better starting model?
    jargon: what assumptions does fusing finetuned checkpoints into a base model make about
      access to source training data and multitask pretraining compute?
    task: how do I improve a base model when the source datasets are unavailable and I cannot
      afford multitask pretraining?
    practitioner: I only have the finetuned weights and no source data or pretraining budget,
      can I still get a better base model?
  answered_by:
  - context-no-source-data
  - context-reverse-transfer
- ask:
    plain: how does picking one fine-tuned model to start from relate to averaging several
      of them?
    jargon: is intermediate-task training the single-model special case of weight fusion for
      initialization?
    task: how should I frame the choice of a starting checkpoint if averaging several sources
      is on the table?
    practitioner: should I think of choosing a helper task and averaging several helper models
      as the same decision?
  answered_by:
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
