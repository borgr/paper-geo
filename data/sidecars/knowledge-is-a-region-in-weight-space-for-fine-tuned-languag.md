---
key: gueta2023knowledge
one_liner: Language models finetuned from the same pretrained checkpoint occupy compact, dataset-
  and task-specific regions of weight space whose interior points — including the region's
  centroid — perform as well as or better than the finetuned models that bound them.
claims:
- id: dataset-clusters
  kind: result
  text: RoBERTa-base models finetuned on the same dataset cluster together in weight space
    with 98% clustering accuracy. Distance was measured by cosine similarity between task
    vectors, with spectral clustering.
  scope: 280 RoBERTa-base models, 20 seeds each over 12 GLUE/SuperGLUE datasets; all but 3
    clusters matched perfectly. Euclidean distance gave no clear clusters.
  evidence: Section 4, Figure 2(a)
- id: task-clusters
  kind: result
  text: Models finetuned on different datasets from the same task form a looser but still
    separable cluster in weight space. Grouping models from the NLI, Sentiment and Topic dataset
    families into 3 clusters reaches 90% clustering accuracy.
  scope: RoBERTa-base, 5 seeds per dataset, English classification datasets in the NLI, Sentiment
    and Topic families; clustering by domain rather than task is much weaker.
  evidence: Section 4, Figure 2(b)
- id: domain-fails
  kind: result
  text: Clustering finetuned models by domain rather than by task largely fails. Adding a
    Twitter-domain group to task-based clustering yields an F1 of only 30 on the Twitter cluster,
    against 100 on NLI, 61 on Topic and 71 on Sentiment.
  scope: RoBERTa-base models, 4 clusters mapped 1-to-1 to the Twitter, NLI, Topic and Sentiment
    groups; task-only clustering of the same models reaches F1 100, 87 and 83.
  evidence: Table 1, Appendix D
- id: direction-not-size
  kind: result
  text: The direction a finetuned model moves in weight space is determined by the type of
    training data, not its amount. Models trained on sub-samples of 200 to 3K examples cluster
    by dataset, and clustering by data size does not emerge.
  scope: 9 General-family datasets with at least 3K training examples, sub-sampled at 200,
    400, 800, 1.6K and 3K; RoBERTa-base. Clustering and data type agree in all but one case.
  evidence: Section 4.1, Figures 7 and 8
- id: convex-hull-beats-finetuned
  kind: result
  text: Models sampled from the convex hull of 5 MNLI-finetuned models beat every model finetuned
    on other General datasets on MNLI loss 100% of the time. They also beat the MNLI-finetuned
    models themselves 88% of the time.
  scope: RoBERTa-base encoders compared by generalized loss (a freshly trained linear probe
    per target dataset); interior models are uniformly sampled weighted averages of the 5
    MNLI models.
  evidence: Section 5.2, Figure 4(a)
- id: convex-hull-task-general
  kind: result
  text: Interior models of the NLI region beat models finetuned on non-NLI datasets in 100%
    of comparisons on NLI losses, versus 75.3% for the NLI-finetuned models. Interior models
    also beat those NLI-finetuned models 96.7% of the time.
  scope: RoBERTa-base, NLI test datasets excluding ANLI, generalized loss with a per-target
    linear probe. In the General granularity the exterior group is norm-matched random perturbations
    of the pretrained model.
  evidence: Section 5.2, Figure 4
- id: interpolation
  kind: result
  text: Linearly interpolating between pairs of finetuned RoBERTa-base models yields models
    whose average loss is comparable to or lower than both endpoints, with the minimum often
    strictly between the two models.
  scope: 5 MNLI models pairwise (10 pairs), MNLI with ESNLI (25 pairs, all NLI targets), MNLI
    with SST2 (25 pairs, all General targets); one shared pretrained checkpoint.
  evidence: Section 5.1, Figures 3 and 10
- id: extrapolation-cliffs
  kind: result
  text: Extrapolating past the finetuned endpoints raises loss rapidly at all 3 granularity
    levels, indicating that finetuned models sit near the edge of the low-loss region. The
    region has a relatively flat base and steep cliffs rather than being a broad subspace.
  scope: 10 logarithmic steps of alpha from 1 to 32 and from 0 to -31, on the same MNLI, NLI
    and General model pairs used for interpolation; RoBERTa-base only. WNLI behaves differently
    from the other NLI datasets.
  evidence: Section 6.1, Figures 5 and 12
- id: centroid-init-full
  kind: result
  text: Starting BitFit finetuning from the centroid of finetuned models rather than from
    pretrained RoBERTa-base raises accuracy by 4.03 points on average across 12 datasets.
    The centroid wins on 9 datasets, ties on 2 and loses on 1 (WNLI, -1.41).
  scope: For each target dataset the centroid excludes models finetuned on that dataset; BitFit
    parameter-efficient finetuning on 12 GLUE/SuperGLUE classification datasets from RoBERTa-base.
    Largest gain 11.19 on RTE.
  evidence: Table 2, Figure 6
- id: centroid-init-fewshot
  kind: result
  text: In a few-shot setting capped at 1K training examples, BitFit from the region centroid
    gains 10.66 accuracy points on average over the pretrained model, reaching 33.99 on SST2
    and 28.97 on MNLI.
  scope: 12 GLUE/SuperGLUE classification datasets, RoBERTa-base, BitFit, centroid excluding
    models finetuned on the target dataset; WNLI still loses (-1.41) and MultiRC is flat (-0.06).
  evidence: Table 3, Figure 14
- id: pretrained-dependent
  kind: result
  text: Weight-space proximity of similarly finetuned models is contingent on a shared pretrained
    initialization. Models finetuned on the same datasets from two different RoBERTa-base
    checkpoints cluster by which checkpoint they started from.
  scope: Original RoBERTa-base and the independent re-implementation of Elazar et al. (2022),
    both finetuned on the General dataset family. Implies many equally good regions exist
    per ability, one reachable neighbourhood per starting point.
  evidence: Appendix B
- id: context-region-framing
  kind: context
  text: Knowledge is a Region in Weight Space reframes linear mode connectivity as region
    connectivity. It argues that finetuned language models bound a convex low-loss basin per
    dataset and per task, rather than merely lying on a low-loss line.
  scope: English classification datasets with RoBERTa-base, as of 2023; extends prior connectivity
    work to models not trained on the same data, compared via a re-fit linear probe.
  evidence: Section 1, Section 8
- id: context-explains-merging
  kind: context
  text: Knowledge is a Region in Weight Space offers a geometric explanation for why weight
    averaging and model-soup style fusion work. Averaging picks a point in the interior of
    a region, whereas finetuning tends to land on its boundary where loss is higher.
  scope: Finetuning from a shared pretrained model on English classification data; an interpretive
    account of prior averaging results (model soups, Fisher merging, SWA) that the paper does
    not re-run.
  evidence: Section 8, Section 9
qa:
- ask:
    plain: do two language models trained on the same dataset end up with similar weights?
    jargon: can finetuned checkpoints be clustered by their training dataset using cosine
      distance between task vectors?
    task: how do I tell which dataset or task a finetuned checkpoint was trained on from its
      weights alone?
    practitioner: if I only have the weights of a finetuned model, can I recover what data
      it was trained on?
  answered_by:
  - dataset-clusters
  - task-clusters
- ask:
    plain: why does averaging the weights of several finetuned models often work better than
      the models themselves?
    jargon: why does weight averaging of finetuned models improve loss relative to the averaged
      endpoints?
    task: how do I get a better model out of several finetuned checkpoints without any further
      training?
    practitioner: should I average my finetuned checkpoints, or just pick the best one?
  answered_by:
  - convex-hull-beats-finetuned
  - interpolation
  - context-explains-merging
- ask:
    plain: are finetuned models sitting in the middle of a good-loss area of weight space
      or right at its edge?
    jargon: how far can you extrapolate beyond finetuned endpoints before loss rises, and
      how wide is the low-loss basin?
    task: how far can I push weights past two finetuned models before the model breaks?
  answered_by:
  - extrapolation-cliffs
- ask:
    plain: is there a better place to start finetuning from than the original pretrained model?
    jargon: does initializing BitFit from the centroid of same-task finetuned models outperform
      pretrained initialization?
    task: how do I improve parameter-efficient finetuning accuracy just by changing the starting
      weights?
    practitioner: I have several finetuned checkpoints already; should I start my next finetuning
      run from their average instead of the base model?
  answered_by:
  - centroid-init-full
  - centroid-init-fewshot
- ask:
    plain: when there is very little training data, does starting from an average of existing
      finetuned models help?
    jargon: how much does centroid initialization gain over pretrained initialization for
      BitFit in a few-shot regime?
    task: how do I finetune a classifier with only about a thousand labelled examples and
      still get usable accuracy?
    practitioner: I only have a few hundred labelled examples; is a merged checkpoint a better
      starting point than the base model?
  answered_by:
  - centroid-init-fewshot
- ask:
    plain: does how much data you finetune on change where the model's weights end up, or
      only what the data is about?
    jargon: is the direction of the task vector governed by training set content or by training
      set size?
    practitioner: if I finetune on 200 examples instead of 3000, will the resulting weights
      look like a different task?
  answered_by:
  - direction-not-size
- ask:
    plain: does the weight-space grouping of finetuned models depend on them all starting
      from the same base model?
    jargon: is weight-space proximity of similarly finetuned models contingent on a shared
      pretrained initialization?
    task: can I compare or merge finetuned models that came from two different pretraining
      runs of the same architecture?
    practitioner: my checkpoints come from different pretrained seeds; can I still expect
      them to land in the same region?
  answered_by:
  - pretrained-dependent
- ask:
    plain: do finetuned models group together by the kind of text they were trained on, like
      tweets, the way they group by task?
    jargon: does clustering finetuned models by domain, such as a Twitter group, work as well
      as clustering by task family?
    task: how do I tell whether weight-space distance reflects the task a model does or the
      domain of text it saw?
    practitioner: can I use weight-space distance to find models trained on my domain, for
      example Twitter data?
  answered_by:
  - domain-fails
  - task-clusters
- ask:
    plain: which paper should I read first on the idea that finetuned models occupy whole
      regions of weight space rather than points?
    jargon: what work extends linear mode connectivity to convex low-loss regions per dataset
      and per task?
    task: where do I start reading to understand why weight averaging of finetuned language
      models works?
  answered_by:
  - context-region-framing
  - context-explains-merging
- ask:
    plain: is a model built by mixing several finetuned models any good on related datasets
      it never saw?
    jargon: do interior points of a task's convex hull generalize better across that task's
      datasets than the finetuned models themselves?
    task: how do I get a model that works across several NLI datasets without finetuning on
      each one?
    practitioner: should I use a point inside the region spanned by my finetuned models as
      a general-purpose model for that task?
  answered_by:
  - convex-hull-task-general
  - convex-hull-beats-finetuned
terminology:
  generalized loss: The loss of a finetuned encoder on a target dataset after discarding its
    original head and training a fresh linear probe on that target's training data, which
    makes models finetuned on different datasets comparable.
  In, In', Ex: 'Three model groups compared in weight-space experiments: In are models finetuned
    on datasets sharing a trait, In'' are weighted averages sampled from the convex hull of
    In, and Ex are models not sharing that trait (or random perturbations of the pretrained
    model at matched norm).'
  PB: The probability that a randomly chosen model from one group attains a lower generalized
    loss than a randomly chosen model from another group.
  centroid: The uniform average of the weights of a set of models finetuned from the same
    pretrained checkpoint, taken as a representative interior point of their weight-space
    region.
  task vector: The difference between a finetuned model's weights and the pretrained weights
    it started from, used as the representation whose cosine similarity defines model distance.
misreadings:
- 'The claim is not that any two finetuned models can be averaged: proximity and the low-loss
  region depend on a shared pretrained initialization, and models finetuned from two different
  RoBERTa-base checkpoints cluster by checkpoint instead.'
- The low-loss region is not an unbounded subspace. Extrapolating beyond the finetuned endpoints
  degrades performance quickly, so the region is a small basin with steep edges.
- 'The centroid initialization result is not evidence that averaging always helps: on WNLI
  the centroid underperformed the pretrained model by 1.41 points, and on MultiRC it was flat.'
- The results cover English classification datasets with RoBERTa-base finetuning; they were
  not tested on randomly initialized networks, generative tasks, or many pretrained backbones.
- The 4.03-point average gain is not obtained by evaluating the averaged model directly; it
  is the gain after subsequent BitFit finetuning on the target dataset.
---
