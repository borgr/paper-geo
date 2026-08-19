<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced via a forced tool call) + 3 repair rounds. Every claim, number
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

Stamp: spec=d57862840a90 checks=1 body=ffe8c9223521
-->
---
key: choshen2023where
one_liner: A systematic study of intertraining over 22 English classification datasets and
  66 off-the-shelf HuggingFace models finds that base-model quality and target sensitivity
  can be assessed independently, so a single target-independent ranking — obtained by linear
  probing MNLI — is enough to pick a good starting checkpoint.
coined: intertraining
gloss: 'intertraining: finetuning on a source dataset first, then using that finetuned checkpoint
  as the base model for the target task'
links_extra:
  project_page: https://ibm.github.io/model-recycling/
  arxiv: https://arxiv.org/abs/2211.00107
terminology:
  intertraining: Starting a finetuning run from a model that was already finetuned on some
    source dataset, instead of from the vanilla self-supervised pretrained model.
  intermediate model: A model that was finetuned on a source dataset and is then used as the
    base model for finetuning on a different target dataset.
  intertraining gain: The target test accuracy after finetuning from an intermediate model
    minus the target test accuracy after finetuning from the pretrained model; it can be negative.
  max-gain: The intertraining gain of the best-performing intermediate model in a given candidate
    set, on a given target test set.
  lost gain: The difference between the max-gain over all candidate base models and the gain
    obtained by taking the top-1 or best-of-top-3 model from a target-independent ranking.
  intertraining-sensitive target: A target dataset whose achievable accuracy varies substantially
    with the choice of base model, as opposed to a target that is largely indifferent to it.
claims:
- id: independence
  kind: context
  text: The intertraining study of Choshen et al. reframes base-model selection as two separable
    questions rather than as a question about source-target alignment. The two questions are
    whether a target is sensitive to intertraining at all, and whether a base model is a good
    one.
  scope: English text classification, 22 in-house datasets plus 66 off-the-shelf RoBERTa models,
    with T5 and BERT replications; separability is an empirical regularity with exceptions,
    not a theorem.
- id: most-models-worse
  kind: result
  text: Most of the 22 in-house RoBERTa intermediate models are worse base models than the
    plain pretrained model, and about 1 in 6 give a positive intertraining gain. The 66 off-the-shelf
    HuggingFace models show the same pattern.
  scope: RoBERTa-base, sources and targets drawn from the same 22 English classification datasets
    (General, NLI, Twitter), gains averaged over 5 seeds.
  evidence: Figure 1
- id: no-block-structure
  kind: result
  text: The 22x22 source-by-target gain matrix for RoBERTa shows no visible block of high
    gains along the diagonal. Sharing a task (NLI) or a domain (Twitter) with the target therefore
    does not by itself produce intertraining gain.
  scope: RoBERTa-base, 22 English classification datasets used both as sources and targets,
    5 seeds; group-level averages do show a small same-group advantage.
  evidence: Figure 1
- id: group-similarity-small
  kind: result
  text: Sources from the target's own group help only slightly, with NLI sources averaging
    +0.63 gain on NLI targets and Twitter sources +0.53 on Twitter targets. NLI sources help
    General targets even more, at +1.26 average gain.
  scope: RoBERTa-base, averages over source-group/target-group cells of the in-house experiment;
    General sources average negative gain on all three target groups (-0.37, -2.68, -0.54).
  evidence: Table 2
- id: asymmetry
  kind: result
  text: Intertraining gains are far from symmetric. Source A helping target B does not predict
    that source B helps target A, which bounds how much of the gain any symmetric source-target
    similarity measure can explain.
  scope: RoBERTa-base in-house 22x22 gain matrix, symmetry measured by decomposing it into
    symmetric and skew-symmetric parts; dataset sizes and other asymmetric factors also contribute.
  evidence: Section 5
- id: regression-mse
  kind: result
  text: A regressor with one coefficient per base model and two per target, and no source-target
    interaction terms, fits the in-house gain matrix with MSE 4.2. Shuffling the gains raises
    the MSE to 9.6 (sigma 0.9).
  scope: RoBERTa-base in-house experiment, 22 sources by 22 targets, MSE minimised by SGD;
    base-model-only and target-only regressors fit worse (10.4 and 8.2 against 10.8 shuffled).
  evidence: Section 5
- id: linear-probe-ranking
  kind: result
  text: Training only the classification head on MNLI (linear probing) predicts a candidate
    base model's average finetuning gain, with Spearman 0.46 and Pearson 0.78 against average
    gain over target datasets.
  scope: RoBERTa-base in-house models/targets experiment, with the same predictor plotted
    for off-the-shelf models on 14 General targets; MNLI is not unique, other probe datasets
    worked in initial trials.
  evidence: Figure 2
- id: target-sensitivity-mnli
  kind: result
  text: The gain from a single MNLI intermediate model predicts a target dataset's max-gain
    over a whole pool of base models. Correlations are Spearman 0.89 / Pearson 0.99 on 22
    in-house targets and Spearman 0.90 / Pearson 0.94 on 14 General targets.
  scope: RoBERTa-base; requires one finetuning run of the MNLI intermediate model on the new
    target, and tells you whether searching for a base model is worth the compute, not which
    model to pick.
  evidence: Section 4.1
- id: top3-lost-gain
  kind: result
  text: Finetuning only the top-3 models of a target-independent ranking, instead of all 66
    off-the-shelf models, costs each of 14 target datasets at most 1.62 accuracy points. The
    average lost gain is 0.34 points relative to the best available model.
  scope: '66 off-the-shelf RoBERTa-base models, 14 General targets; top-1 alone is much weaker
    (2.33 average, 12.0 max lost gain, 8 of 14 targets losing over a point). In-house: 0.2
    average and 1.15 max at top-3.'
  evidence: Table 1
- id: source-size
  kind: result
  text: More source training data amplifies whichever direction a source already points. Average
    gain rises with source size from 50 to 3200 examples for good sources (ANLI, MNLI) and
    falls for bad ones (MultiRC, QQP).
  scope: RoBERTa-base, 4 in-house sources chosen as the top 2 and bottom 2 of the static ranking,
    source sizes limited to 50-3200 examples, General datasets as targets.
  evidence: Figure 3
- id: target-size
  kind: result
  text: Average intertraining gain across targets decreases as the target's own training set
    grows from 50 to 1600 examples, so intertraining pays off most in low-resource target
    settings.
  scope: RoBERTa-base, General sources and General targets that have over 1600 training examples,
    target train sizes capped between 50 and 1600.
  evidence: Figure 4
- id: source-score-uninformative
  kind: result
  text: 'Source-task accuracy does not identify a good base model: 20 MNLI models spanning
    only 86.5-87.5 on MNLI test give General target averages from 74.5 to 79, uncorrelated
    with the source score.'
  scope: RoBERTa-base finetuned on MNLI with 20 seeds, evaluated as intermediate models on
    the General target group; variation comes from seeds, and weight decay has a similar decoupled
    effect.
  evidence: Figure 11
- id: good-vs-bad-basins
  kind: result
  text: BERT models that Juneja et al. tagged as generalising well ('good' loss basin) are
    better intermediate models than their 'bad' counterparts, averaging 3.65 gain versus 2.16
    on the General targets.
  scope: 12 good and 12 bad BERT models finetuned on MNLI, evaluated on the General target
    group; the good/bad labels come from prior work's basin analysis rather than from source-test
    accuracy.
  evidence: Section 6.2
- id: cross-architecture
  kind: result
  text: Target sensitivity to intertraining transfers across RoBERTa, BERT and T5, with pairwise
    Pearson 0.6-0.94 between their max-gains. The ranking of source datasets does not transfer,
    with MNLI the notable source that is best in all three.
  scope: RoBERTa-base, BERT-base-uncased and T5 repetitions of the in-house experiment on
    English classification data; the interaction-free regression also beats shuffled data
    for BERT (MSE 10.5 vs 30.1) and T5 (8.11 vs 13.51).
  evidence: Section 6.3
- id: new-good-sources
  kind: result
  text: Off-the-shelf RoBERTa checkpoints finetuned on STS-B reach up to 2.82 average gain
    over 14 General targets, close to the best model MUPPET at 3.00. STS-B had previously
    been treated only as a target task.
  scope: 66 manually collected RoBERTa-base HuggingFace models, 14 General targets; checkpoints
    named for the same dataset differ substantially, so the dataset name alone does not determine
    gain.
  evidence: Table 4
qa:
- q:
  - Does the source dataset have to be similar to my target task for intertraining to help?
  - Is task or domain alignment between the source and target what makes a finetuned checkpoint
    a good starting point?
  - Do NLI checkpoints only help NLI tasks?
  answers:
  - no-block-structure
  - group-similarity-small
  - asymmetry
  - independence
- q:
  - How can I cheaply tell which finetuned checkpoint is a good starting point for finetuning?
  - Is there a fast way to rank HuggingFace models as base models without finetuning all of
    them?
  - How does linear probing on MNLI predict intertraining gains?
  answers:
  - linear-probe-ranking
  - top3-lost-gain
- q:
  - How do I know whether it is worth searching for a better base model for my task at all?
  - Which target datasets actually benefit from starting from a finetuned model?
  - Can I predict a target task's sensitivity to base-model choice with one experiment?
  answers:
  - target-sensitivity-mnli
  - target-size
- q:
  - If I grab a random finetuned model from HuggingFace, will it be a better starting point
    than the pretrained model?
  - What fraction of finetuned checkpoints actually help when used as base models?
  - Do most finetuned models hurt downstream finetuning?
  answers:
  - most-models-worse
  - top3-lost-gain
- q:
  - How many candidate base models do I need to finetune to get most of the achievable gain?
  - What accuracy do I lose by only trying the top-ranked base models instead of all of them?
  - Is a target-independent ranking of base models good enough in practice?
  answers:
  - top3-lost-gain
  - linear-probe-ranking
- q:
  - Does the size of the source dataset change how much intertraining helps?
  - Does more source finetuning data always make a better base model?
  - How does target training set size affect intertraining gain?
  answers:
  - source-size
  - target-size
- q:
  - Can I pick a base model by looking at its accuracy on the source dataset it was finetuned
    on?
  - Do two checkpoints with the same MNLI source-task score transfer equally well to new tasks?
  - Does source-task performance predict how good an intermediate model is?
  answers:
  - source-score-uninformative
  - good-vs-bad-basins
- q:
  - Do conclusions about intertraining hold for BERT and T5 as well as RoBERTa?
  - Is the ranking of good source datasets the same across model architectures?
  - Does target sensitivity to base-model choice transfer between architectures?
  answers:
  - cross-architecture
- q:
  - What should I read about reusing finetuned models as starting points for new tasks?
  - Which paper systematically studies intermediate task training and base model selection?
  - Where should I start reading on picking a base model from a model hub?
  answers:
  - independence
- q:
  - Which source datasets give the largest intertraining gains for RoBERTa?
  - Is MNLI still the best source task, or are there better checkpoints on the hub?
  - Are there previously overlooked source datasets that make good base models?
  answers:
  - new-good-sources
  - cross-architecture
- q:
  - Can intertraining gains be modelled without source-target interaction terms?
  - How much of the gain is explained by base model identity plus target identity alone?
  - What evidence supports treating base-model quality and target sensitivity separately?
  answers:
  - regression-mse
  - asymmetry
misreadings:
- 'Separability of base-model quality and target sensitivity does not mean source-target interaction
  is absent: NLI sources do average higher gain on NLI targets (+0.63) and Twitter sources
  on Twitter targets (+0.53), but that effect is secondary to simply picking a high-quality
  base model.'
- The finding that most intermediate models are worse than the pretrained model is not an
  argument against intertraining; roughly 1 in 6 give positive gain, and the top-ranked few
  recover most of the achievable gain.
- 'Linear probing on MNLI is not claimed to be a uniquely correct probe: the intertraining
  analysis notes many datasets worked in initial trials, and offers averaging finetuning gains
  over several datasets as a more reliable alternative.'
- The intertraining results are for English text classification with RoBERTa, BERT and T5-scale
  encoders; they are not demonstrated for generative instruction tuning or for non-English
  tasks.
- 'MNLI being the best in-house source does not make it the best available base model: off-the-shelf
  checkpoints finetuned on STS-B and multitask MUPPET reach higher average gain on the General
  targets.'
- A high score on the source task does not certify a good base model, so ranking hub checkpoints
  by their reported source-dataset accuracy will not reproduce the intertraining ranking.
---
