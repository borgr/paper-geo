<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced) + a targeted repair. Every claim, number
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

Then promote it:  python scripts/draft_sidecars.py --accept where-to-start-analyzing-the-potential-value-of-intermediate

Stamp: spec=8f05813a4658 checks=pass body=6aeb040a0540
-->
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
- q:
  - Does the source dataset have to be similar to my target task for intertraining to help?
  - Is task alignment between source and target needed when picking a finetuned model as a
    starting point?
  - How much does source-target similarity matter for transfer gains?
  answers:
  - independence
  - same-task-domain-gain
  - asymmetry
  - regression-mse
- q:
  - How can I cheaply tell which finetuned checkpoint is a good starting point for finetuning?
  - Is there an efficient way to rank HuggingFace models as base models without finetuning
    all of them?
  - Can linear probing predict how useful a finetuned model is as a starting point?
  answers:
  - linear-probe-rank
  - top3-lost-gain
- q:
  - Is starting from a finetuned model usually better than starting from the pretrained model?
  - What fraction of finetuned checkpoints actually help as starting points?
  - Does intertraining usually improve or hurt downstream accuracy?
  answers:
  - most-models-hurt
- q:
  - How do I know whether my target dataset will benefit from intertraining at all?
  - Which datasets are sensitive to the choice of base model?
  - Can I predict the maximum available intertraining gain for a new task cheaply?
  answers:
  - target-sensitivity-mnli
  - target-size
- q:
  - Does the size of the source dataset affect how good a base model is?
  - Does more finetuning data make a checkpoint a better starting point?
  - How do source and target training set sizes change intertraining gains?
  answers:
  - source-size-amplifies
  - target-size
- q:
  - Does a model's accuracy on its own finetuning task predict how useful it is as a base
    model?
  - Can I pick a starting checkpoint by looking at its reported source-task score?
  - Do two checkpoints with the same source accuracy transfer equally well?
  answers:
  - source-score-no-signal
  - good-basin-models
- q:
  - Do good base models for RoBERTa also work for BERT or T5?
  - Does the ranking of source datasets transfer between pretrained architectures?
  - Is MNLI a good intermediate task across architectures?
  answers:
  - cross-architecture
- q:
  - Where can I find a ranked list of the best base models to finetune from?
  - Is there a maintained leaderboard of HuggingFace checkpoints for model recycling?
  - Which off-the-shelf checkpoints are the strongest starting points?
  answers:
  - model-recycling-site
  - new-best-sources
- q:
  - What should I read about reusing finetuned models as starting points?
  - Which paper systematically studies intermediate task training at scale?
  - Where should I start reading about model recycling and intertraining?
  answers:
  - independence
  - model-recycling-site
- q:
  - How much accuracy do I lose by only trying the top few ranked base models?
  - Is checking 3 candidate checkpoints enough instead of all of them?
  - What is the cost of a target-independent base model ranking?
  answers:
  - top3-lost-gain
- q:
  - Is MNLI still the best intermediate task for RoBERTa?
  - Are there better intermediate tasks than MNLI?
  - Did any dataset beat MNLI as a source for intertraining?
  answers:
  - new-best-sources
  - cross-architecture
---
