---
key: choshen2023where
one_liner: A systematic study of intertraining over 22 English classification datasets and
  66 off-the-shelf HuggingFace checkpoints, showing that base-model quality and target sensitivity
  can be assessed independently — so a single MNLI linear probe ranks base models without
  knowing the target task.
links_extra:
  project page: https://ibm.github.io/model-recycling/
terminology:
  intertraining: Finetuning a model on a source dataset and then using that finetuned model,
    rather than the vanilla pretrained model, as the starting point for finetuning on a target
    dataset.
  intermediate model: A model finetuned on some source dataset and then used as the base model
    (starting point) for finetuning on a different target dataset.
  intertraining gain: The target-test accuracy obtained by finetuning from an intermediate
    model minus the accuracy obtained by finetuning from the vanilla pretrained model on the
    same target; may be negative.
  max-gain: The largest intertraining gain achievable on a target by finetuning every available
    intermediate model and keeping the best, used as the ceiling that cheaper selection strategies
    are measured against.
  lost gain: The difference between the max-gain on a target and the gain obtained from the
    best of the n top-ranked base models, quantifying what a cheap target-independent ranking
    gives up.
  intertraining-sensitive target: A target dataset whose accuracy changes substantially depending
    on which base model is used as the finetuning starting point, as opposed to targets that
    are largely indifferent to base model choice.
  static ranking: An ordering of candidate base models computed once, independently of any
    target dataset, and reused for every new target.
misreadings:
- 'Intertraining is not a free win: most finetuned checkpoints degrade target performance
  relative to the plain pretrained model, so picking an arbitrary finetuned model is worse
  than doing nothing.'
- 'The finding that source-target similarity matters little does not mean interaction is absent:
  sources sharing the target''s task or domain do give somewhat higher average gain, the effect
  is just secondary to which base model is chosen.'
- A high score on the source dataset is not evidence that a checkpoint will be a good starting
  point; MNLI models with nearly identical source accuracy differ widely in the gain they
  give on new targets.
- Rankings of source datasets found for RoBERTa should not be reused for BERT or T5, since
  average source gains do not correlate across architectures; MNLI is the exception that does
  well in all three.
claims:
- id: independence
  text: Intertraining gain can be analyzed as a per-base-model effect plus a per-target effect,
    so a base model can be chosen without knowing the target dataset. This reverses the common
    assumption that source-target task alignment is the main determinant of intertraining
    success.
  scope: 22 English classification datasets used both as sources and targets with RoBERTa-base,
    replicated with BERT and T5; source-target interaction is secondary rather than zero.
  kind: context
  evidence: Figure 1 and Section 5
- id: regression-mse
  text: A regressor with one coefficient per base model and two per target predicts intertraining
    gain with MSE 4.2 on the 22-source-by-22-target in-house experiment, versus 9.6 (sigma
    0.9) with randomly shuffled gains. It has too few parameters to model any source-target
    interaction explicitly.
  scope: RoBERTa-base in-house sources and targets, gains averaged over 5 seeds, fit by SGD
    minimising MSE. Base-model-only and target-only regressors reach MSE 10.4 and 8.2 against
    a shuffled baseline of 10.8.
  kind: result
  evidence: Section 5
- id: most-models-hurt
  text: 'Most finetuned models are worse starting points than the vanilla pretrained model:
    only about 1 in 6 intermediate models yields a positive intertraining gain on a target
    dataset.'
  scope: RoBERTa-base models finetuned on 22 English classification sources, used as starting
    points on the same 22 targets, 5 seeds each.
  kind: result
  evidence: Section 4 and Figure 1
- id: linear-probe-rank
  text: Ranking base models by the gain of a linear probe trained on MNLI predicts their average
    finetuning gain over target datasets. Correlation is Spearman 0.46 and Pearson 0.78 in
    the in-house experiment, and Figure 2 shows the same relation for off-the-shelf models
    on 14 General targets.
  scope: RoBERTa-base in-house sources and 66 off-the-shelf HuggingFace models; only the classification
    head is trained during probing. MNLI is not unique as probing dataset.
  kind: result
  evidence: Figure 2 and Section 4.2
- id: top3-lost-gain
  text: Finetuning only the top 3 statically ranked base models instead of all 66 off-the-shelf
    models costs at most 1.62 accuracy points of the available max-gain. That worst case is
    over 14 General targets, where the average loss is 0.34 points.
  scope: 'RoBERTa-base off-the-shelf models ranked target-independently by MNLI linear probing;
    the single top-ranked model loses 2.33 points on average and 12.0 at worst. In-house:
    0.2 average, 1.15 max for top 3.'
  kind: result
  evidence: Table 1
- id: target-sensitivity-mnli
  text: Whether a target dataset can benefit from intertraining at all is predictable from
    the gain of a single MNLI-based intermediate model. That single gain correlates with the
    max-gain over all models at Spearman 0.90 and Pearson 0.94 on 14 General targets.
  scope: RoBERTa-base off-the-shelf models on 14 General targets; in-house models on 22 targets
    give Spearman 0.89 and Pearson 0.99. Requires finetuning one model on the target.
  kind: result
  evidence: Section 4.1
- id: same-task-domain-gain
  text: Sources sharing the target's task or domain give higher average gain than unrelated
    sources, but the effect is small. Average gain is 0.63 for NLI sources on NLI targets
    and 0.53 for Twitter sources on Twitter targets, while NLI sources give a larger 1.26
    on the diverse General targets.
  scope: RoBERTa-base in-house intermediate models, averages over the General, NLI and Twitter
    dataset groups; General sources give negative average gain on all 3 target groups.
  kind: result
  evidence: Table 2
- id: asymmetry
  text: Intertraining gains are far from symmetric. A source A that helps target B does not
    imply source B helps target A, which bounds how much of the gain any symmetric source-target
    similarity measure can explain.
  scope: 22-by-22 in-house RoBERTa gain matrix, decomposed into symmetric and skew-symmetric
    parts; dataset sizes differ, so full symmetry would not be expected even under strong
    similarity effects.
  kind: result
  evidence: Section 5 and Appendix G
- id: source-size-amplifies
  text: 'More source training data amplifies whatever direction the source pushes in: gains
    grow with source size for good sources (ANLI, MNLI) and shrink for bad ones (MultiRC,
    QQP). Source size correlates with average source gain at Pearson 0.75.'
  scope: RoBERTa-base, 4 in-house sources with source training limited to 50-3200 samples,
    evaluated on the General targets; the 0.75 correlation is across the 22 in-house sources.
  kind: result
  evidence: Figure 3 and Section 6.1
- id: target-size
  text: Intertraining gain shrinks as the target's own training set grows, making intertraining
    most valuable in few-shot target settings; for 3 targets the gain follows a U-shape, turning
    negative before rising back toward zero.
  scope: RoBERTa-base, General sources and General targets subsampled to between 50 and 1600
    training examples. No significant correlation between target size and target average gain
    across the full in-house experiment.
  kind: result
  evidence: Figure 4 and Section 6.1
- id: source-score-no-signal
  text: Source-task accuracy does not predict intertraining quality. 20 RoBERTa models finetuned
    on MNLI with different seeds score between 86.5 and 87.5 on MNLI test yet range from 74.5
    to 79 in average General target score, with no correlation.
  scope: RoBERTa-base, MNLI as source, General datasets as targets, differences arising from
    random seeds alone; hyperparameter choices such as weight decay produce similar disconnects.
  kind: result
  evidence: Section 6.2 and Figure 11
- id: good-basin-models
  text: 'BERT models that generalize better out-of-domain also make better base models: 12
    ''good''-basin MNLI models give 3.65 average gain on General targets versus 2.16 for 12
    ''bad''-basin models.'
  scope: BERT models finetuned on MNLI taken from Juneja et al. (2022); good/bad labels come
    from that prior work's loss-basin analysis, not from new clustering.
  kind: result
  evidence: Section 6.2
- id: cross-architecture
  text: Which source dataset makes a good base model does not transfer across architectures,
    as average source gains do not correlate between RoBERTa, BERT and T5. Target sensitivity
    does transfer, with pairwise Pearson 0.6-0.94 across architectures.
  scope: In-house models/targets experiment repeated with RoBERTa, BERT-base-uncased and T5
    on English classification datasets; MNLI is the exception, giving the highest gain in
    all 3 architectures.
  kind: result
  evidence: Section 6.3
- id: model-recycling-site
  text: The model-recycling site at ibm.github.io/model-recycling publishes a continuously
    updated ranking of the best HuggingFace base models per architecture for intertraining,
    so practitioners can pick a starting point without rerunning the ranking.
  scope: Static target-independent rankings by average intertraining gain on English classification
    targets; RoBERTa-base and T5-small lists also appear in the paper, and site contents change
    over time.
  kind: context
  evidence: Section 8, Table 4 and Table 5
- id: new-best-sources
  text: 'Among off-the-shelf HuggingFace models, several outperform the well-known MNLI source:
    STS-B-based RoBERTa models and Quora-based T5 models rank at the top. A RoBERTa finetuned
    only on STS-B matches the massively multitask MUPPET model.'
  scope: 66 off-the-shelf RoBERTa-base models and 25 T5-small models as base models on the
    General targets; top RoBERTa gains are 2.8-3.0 points. No in-house source among the 22
    beat MNLI.
  kind: result
  evidence: Table 4, Table 5 and Appendix E
qa:
- ask:
    plain: does a fine-tuned model have to come from a related task to be a good starting
      point for training on my task?
    jargon: how much of intermediate-task transfer gain is explained by source-target task
      or domain similarity rather than by the source checkpoint itself?
    task: how do I pick an intermediate checkpoint to fine-tune from when nothing in the model
      zoo matches my task or domain?
    practitioner: my labelled data is in a niche domain, should I only consider checkpoints
      trained on similar data?
  answered_by:
  - independence
  - same-task-domain-gain
  - asymmetry
  - regression-mse
- ask:
    plain: is there a cheap way to find which of many fine-tuned checkpoints is the best starting
      point, short of training with all of them?
    jargon: can a linear probe on a fixed dataset rank candidate base models for intermediate-task
      transfer without full finetuning of each?
    task: how do I shortlist base models from HuggingFace without finetuning all of them on
      my target task?
    practitioner: I have a small compute budget, can I rank candidate starting checkpoints
      before committing to full finetuning runs?
  answered_by:
  - linear-probe-rank
  - top3-lost-gain
- ask:
    plain: is starting from someone else's fine-tuned model usually better than starting from
      the plain pretrained one?
    jargon: what share of intermediate checkpoints yield positive intertraining gain over
      the vanilla pretrained model on a target dataset?
    task: how likely is picking an arbitrary finetuned checkpoint as my starting point to
      hurt my target accuracy?
    practitioner: should I grab a random finetuned checkpoint off HuggingFace or just start
      from the base pretrained weights?
  answered_by:
  - most-models-hurt
- ask:
    plain: how can I tell in advance whether my task will gain anything at all from starting
      on a fine-tuned model?
    jargon: is a target dataset's sensitivity to the choice of base model predictable from
      the gain of a single MNLI intermediate model, and how does target train size affect
      it?
    task: how do I decide whether intertraining is worth trying on a new target dataset before
      running many candidate sources?
    practitioner: I have a new dataset and limited budget, is one trial run enough to know
      if a better starting checkpoint will help me?
  answered_by:
  - target-sensitivity-mnli
  - target-size
- ask:
    plain: does the amount of data a checkpoint was trained on change how good a starting
      point it is?
    jargon: how do source training set size and target training set size each modulate intertraining
      gain?
    task: when choosing between candidate source checkpoints, how should I weigh how much
      data each was finetuned on and how much data I have?
    practitioner: I only have a few hundred labelled examples, does that make a large-source
      checkpoint more or less attractive as a starting point?
  answered_by:
  - source-size-amplifies
  - target-size
- ask:
    plain: if a fine-tuned model scores well on the task it was trained on, does that make
      it a better starting point for another task?
    jargon: does source-task test accuracy correlate with a checkpoint's average intertraining
      gain, and do out-of-domain generalization basins separate good from bad base models?
    task: what signal should I use to choose between several checkpoints finetuned on the
      same source dataset?
    practitioner: two MNLI checkpoints have almost identical MNLI scores, does it matter which
      one I finetune from?
  answered_by:
  - source-score-no-signal
  - good-basin-models
- ask:
    plain: if a fine-tuned model works well as a starting point for one pretrained model family,
      will it work for another?
    jargon: do average source gains and target sensitivity correlate across RoBERTa, BERT
      and T5 backbones?
    task: can I reuse a source-dataset ranking found on RoBERTa when I switch to T5 or BERT?
    practitioner: I read that MNLI checkpoints make good starting points, does that carry
      over to the architecture I actually use?
  answered_by:
  - cross-architecture
- ask:
    plain: where can I find an up-to-date list of the best fine-tuned checkpoints to start
      training from?
    jargon: is there a maintained per-architecture ranking of HuggingFace base models by intertraining
      gain, and which source datasets top it?
    task: how do I choose a strong starting checkpoint for my architecture without running
      the ranking experiments myself?
    practitioner: should I trust a published leaderboard of starting checkpoints instead of
      benchmarking candidates on my own task?
  answered_by:
  - model-recycling-site
  - new-best-sources
- ask:
    plain: what should I read to understand how reusing other people's fine-tuned models as
      starting points actually works?
    jargon: which work systematically studies intermediate-task training and model recycling
      across many source-target pairs?
    task: where do I start reading about choosing a finetuned checkpoint to continue training
      from?
  answered_by:
  - independence
  - model-recycling-site
- ask:
    plain: is trying just the top few candidate checkpoints good enough, or do I lose much
      by not trying them all?
    jargon: how much max-gain is forfeited by finetuning only the top 3 statically ranked
      base models instead of the full candidate pool?
    task: how many candidate base models do I need to actually finetune before I can stop
      searching?
    practitioner: I can afford 3 finetuning runs rather than 66, how much accuracy am I giving
      up?
  answered_by:
  - top3-lost-gain
- ask:
    plain: is there a better dataset than MNLI to train on first before training on my own
      task?
    jargon: do any off-the-shelf source datasets outperform MNLI as an intermediate task,
      and does the best source differ by architecture?
    task: which source datasets should I look for in a checkpoint name when picking a starting
      point for RoBERTa or T5?
    practitioner: everyone recommends starting from an MNLI model, should I be using something
      else?
  answered_by:
  - new-best-sources
  - cross-architecture
---
