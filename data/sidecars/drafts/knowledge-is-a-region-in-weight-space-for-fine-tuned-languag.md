<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from build/sidecar_tasks.json. Every claim, number
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

Then promote it:  python scripts/draft_sidecars.py --accept knowledge-is-a-region-in-weight-space-for-fine-tuned-languag
-->
---
key: DBLP:conf/emnlp/GuetaVRSKC23
one_liner: Language models finetuned on the same data land in one tight bounded region of
  weight space, not at scattered minima, and every point inside it -- including points no
  gradient step would reach -- performs as well or better, which makes the region's centre
  a better place to start finetuning than the pretrained model.
claims:
- id: finetuning-lands-in-a-region-set-by-the-data
  text: 'Where a finetuning run ends up in weight space is determined by what it was trained
    on: clustering models by cosine distance between their task vectors recovers which of
    the 12 General datasets each was finetuned on with 98% accuracy over 20 seeds per dataset,
    and which of three task families with 90% accuracy over 5 seeds per dataset.'
  scope: 'Clustering accuracy is measured by labelling each cluster with its most common member,
    with the number of clusters fixed to the number of datasets or families -- so it says
    the groups are separable, not that the clusters were found without knowing how many to
    look for. All models start from RoBERTa-base. The set clustered at the dataset level is
    not quite the twelve datasets the rest of the paper evaluates: it is described as 20 seeds
    for each General dataset giving 280 models, which is 14 datasets and not 12, and Figure
    2(a)''s legend lists CoPA -- which Section 2.1 says was excluded for being too small --
    while omitting WiC, which Tables 2 and 3 both score.'
  evidence: Sections 2.3 and 4; Figure 2
- id: the-direction-is-set-by-data-type-not-data-size
  text: Finetuning on subsamples of 200, 400, 800, 1.6K and 3K examples from 9 datasets still
    clusters by which dataset the data came from and not by how much of it there was, and
    the direction in weight space is already fixed after relatively little data.
  scope: The control for the obvious confound -- that more data simply moves the weights further.
    Forcing the cluster count to the number of sample sizes instead of the number of datasets
    does not recover size either. Restricted to the 9 General datasets with at least 3K training
    examples.
  evidence: Section 4.1; Appendix C, Figures 7 and 8
- id: the-region-is-a-basin-not-just-a-line
  text: 'Models sampled from the whole convex hull of a group of similarly finetuned models
    -- not merely from the line between a pair -- outperform models outside it: sampled interior
    models beat exterior models 100% of the time in the dataset region, 100% in the task region
    and 100% in the general region.'
  scope: Connectivity in a bounded region, which is stronger than the linear connectivity
    previously reported. The hull is infinite so it is estimated by sampling as many models
    from it as there are models defining it, and each comparison is scored with PB, the probability
    that a random interior model beats a random exterior one.
  evidence: Section 5.2; Figure 4
- id: points-inside-the-region-beat-the-finetuned-models-that-define-it
  text: Weighted averages of finetuned models outperform the finetuned models themselves 88%
    of the time in the dataset region, 96.7% in the task region and 90% in the general region
    -- so the best model in the region is generally not one that finetuning produced.
  scope: 'Measured with the generalized loss averaged over the datasets the interior models
    were finetuned on, so ''better'' means better on the region''s own objective. Interpolation
    curves show the same shape: the minimum along the line usually sits between the two endpoints
    rather than at either one.'
  evidence: Sections 5.1 and 5.2; Figures 3 and 4
- id: finetuning-stops-at-the-edge-of-the-region
  text: Because the interior of the region is better than its vertices, and the vertices are
    the finetuned models, gradient-based finetuning typically stops at the boundary of the
    low-loss region rather than at its centre.
  scope: An inference the authors draw from the interior-versus-vertex comparison plus the
    extrapolation results, not a direct measurement of where in the basin an optimiser lands.
    They put it forward as an open question about the limits of gradient-based training.
  evidence: Sections 1, 6.1 and 9
- id: the-basin-has-a-flat-floor-and-steep-cliffs
  text: Extrapolating past either endpoint of the line between two finetuned models -- 10
    logarithmic steps out to alpha = 32 and to alpha = -31 -- degrades performance rapidly
    at every granularity, so the region is a small basin with a relatively flat base and steep
    sides rather than a broad low-loss subspace.
  scope: '''Rapidly'' is relative to the distance between the two models: the finetuned models
    sit close to where loss starts rising. The shape claim is read off one-dimensional slices
    through the space, and the conclusion that it is a basin rather than a subspace follows
    from the cliffs appearing in every direction tested.'
  evidence: Section 6.1; Figure 5; Appendix G, Figure 12
- id: moving-toward-the-origin-does-not-leave-the-region
  text: Starting from a region's centroid and moving in random directions degrades performance
    once the distance exceeds that of the finetuned models, but moving the same distance and
    further toward the origin of the weight axes does not -- an effect the authors report
    without an explanation.
  scope: Flagged in the paper as unexpected and left as future work, so it is an observation
    rather than a result the paper builds on. Within the finetuned models' own radius, random
    directions are fine too, which is the paper's evidence that the directions finetuning
    happens to move in are not special.
  evidence: Appendix F; Figure 11
- id: the-centroid-beats-the-pretrained-model-as-a-starting-point
  text: Efficiently finetuning with BitFit from the average of a region's models instead of
    from the pretrained model improves accuracy by 4.03 points on average across 12 target
    datasets, winning on 9, tying on 2 and losing on 1.
  scope: 'Read from v3, the Findings of EMNLP 2023 camera-ready; v1 carries the same figures,
    so none of what follows is a version artefact. Two magnitudes circulate and only one of
    them is supported: 4.04 is Section 7''s wording, 4.03 is the printed mean of Table 2''s
    gain row and recomputing that row''s twelve entries gives 4.026, while the abstract''s
    3.06 appears nowhere else in the paper. The counts do reconcile -- the abstract''s ''as
    effective, if not more, in 11 out of 12 datasets'' is Section 7''s 9 wins plus 2 ties.
    For each target dataset the centroid is computed over models excluding any finetuned on
    that dataset, so the comparison is not leaking the target, and only BitFit''s small subset
    of weights is trained.'
  evidence: Section 7; Table 2; Figure 6; abstract
- id: the-gain-is-larger-when-target-data-is-scarce
  text: Restricting the subsequent finetuning to 1K examples raises the centroid's average
    gain over the pretrained model to 10.66 points, with the largest single-dataset gain reaching
    about 34 points.
  scope: 'All of the extra gain is the baseline falling rather than the centroid rising. Between
    Tables 2 and 3 as printed the centroid row is identical on all twelve datasets to two decimals,
    mean 65.54 in both, while the pretrained row is identical on six of them and lower on the
    other six -- MNLI 53.17 to 34.04, QNLI 64.88 to 50.72, QQP 74.49 to 63.18, RTE 50.40 to
    48.52, SST2 78.78 to 50.92, WiC 55.14 to 49.91 -- which moves its mean from 61.51 to 54.88.
    Why a run limited to 1K examples reproduces the full-data centroid numbers exactly is not
    addressed in the paper. The two datasets the centroid loses on, MultiRC at -0.06 and WNLI
    at -1.41, are the same in both settings and by the same margins.'
  evidence: Section 7; Table 3; Appendix H, Figure 14
- id: regions-are-relative-to-the-pretrained-model-you-started-from
  text: Finetuned models cluster by which pretrained checkpoint they started from rather than
    by which dataset they were finetuned on when two different RoBERTa-base checkpoints are
    mixed, because pretraining moves the weights far more than finetuning does.
  scope: The two checkpoints are the original RoBERTa-base and an independent reimplementation,
    and results are comparable within each. The conclusion the authors draw is that there
    is no single region per ability but many -- one neighbourhood of each starting point --
    so 'the MNLI region' is always relative to a base model.
  evidence: Appendix B; Section 4
- id: the-generalized-loss-is-what-makes-the-comparison-possible
  text: To compare models finetuned on different datasets the paper discards each model's
    head, attaches a fresh randomly initialised classifier, trains only that classifier on
    the target data and reports the test loss -- a generalized loss that reduces to the ordinary
    finetuning loss when the target is the model's own source dataset.
  scope: Linear probing on a frozen encoder is a convex problem, which is why the measurement
    is stable across runs -- but it also means every number in the paper is a frozen-representation
    score, not the accuracy a fully finetuned model would reach. Prior work comparing models
    across tasks without it reported chance performance.
  evidence: Section 3; Section 8
- id: cosine-distance-on-task-vectors-is-the-metric-that-works
  text: Subtracting pretrained weights from finetuned weights and taking cosine similarity
    produces clean clusters, while Euclidean distance on the same models does not -- most
    likely because weight norms grow during training for reasons unrelated to the data.
  scope: Chosen for being simple and cheap after trying more sophisticated representational-similarity
    measures, so it is a working choice rather than a claim that cosine is the right geometry.
    Clustering is Spectral Clustering, and the 2-D pictures are t-SNE projections of 120M-dimensional
    vectors -- illustrations, not the evidence.
  evidence: Section 2.3
- id: the-exterior-baseline-for-the-general-region-is-constructed
  text: At the broadest granularity there is nothing natural to compare against, so the exterior
    group is built by perturbing the pretrained model in a random direction whose norm equals
    the average task-vector norm of the interior models, with the direction drawn from a Xavier-initialisation
    prior.
  scope: The Xavier prior is there so the baseline is a plausible network rather than one
    with exploding or vanishing activations -- i.e. to avoid winning against a straw man.
    At the dataset and task granularities the exterior group is real finetuned models instead.
  evidence: Section 3.1, 'General'
- id: task-separates-cleanly-but-domain-does-not
  text: 'Adding a domain-defined group (Twitter datasets) to the task-defined ones breaks
    the clustering: Twitter reaches an F1 of 30 against 100 for NLI, and the presence of the
    domain group also drags Topic from 87 to 61 and Sentiment from 83 to 71, taking the average
    from 90 to 65.'
  scope: 'The paper offers two competing explanations and settles neither: domain regions
    may overlap task regions -- some datasets belong to both, such as TweetEval Sentiment
    -- or domains may not form regions at all. Listed in the limitations as the aspect where
    the results are mixed, with only one domain group available to test. The same appendix
    reports an alternative scoring -- a 1-to-1 cluster-to-group assignment chosen to maximise
    accuracy -- under which NLI scores 1 rather than 100, so the headline F1s depend on majority
    labelling, which permits several clusters to carry the same label.'
  evidence: Appendix D, Table 1 and Figure 9; Section 10
- id: wnli-does-not-behave-like-the-rest-of-nli
  text: Among the six NLI datasets, WNLI behaves differently under extrapolation and may not
    belong to the NLI region at all, which the authors suggest also explains a long tail in
    the task region's loss distribution.
  scope: 'A dataset-level caveat on the task-region result: ''same task'' is a label on a
    dataset, and the geometry does not always agree with it. ANLI is separately excluded from
    the task-level evaluation because its adversarial examples are built to break NLI-trained
    models.'
  evidence: Appendix G, Figure 13(b); Section 3.1, 'Same-Task'
- id: it-gives-model-averaging-a-reason-to-work
  text: 'The region picture retroactively explains a set of empirical results: averaging models
    finetuned on one dataset (model soups) picks a point inside that dataset''s region, averaging
    models from different datasets picks a point in the task or language region, and starting
    a finetuning run from another finetuned model works because that run begins inside the
    region instead of outside it.'
  scope: Offered as a preliminary explanation of others' findings, not as a test of it --
    the paper's own experiments are on RoBERTa-base classification. It also suggests why Stochastic
    Weight Averaging helps, namely that it lands inside a region rather than on its boundary,
    and notes a disagreement with work reporting several basins per dataset rather than one.
  evidence: Section 8
- id: what-was-actually-trained
  text: The study finetunes RoBERTa-base on 36 classification datasets -- thousands of models
    in total, 5 seeds for most experiments and 20 for the same-dataset clustering -- using
    standard hyperparameters with batch size 256 and learning rate 5e-5, and evaluates on
    the same 36 datasets.
  scope: 'The stated limits of that scope: English classification data only, always starting
    from a pretrained model rather than a random initialisation, and essentially one pretrained
    model family. Seeds control both classifier-head initialisation and data order.'
  evidence: Sections 2.1, 2.2 and 10; Appendix A
qa:
- q:
  - What does 'knowledge is a region in weight space' mean?
  - What is the main finding of Gueta et al. 2023?
  - How are finetuned models related in weight space?
  answers:
  - finetuning-lands-in-a-region-set-by-the-data
  - the-region-is-a-basin-not-just-a-line
  - points-inside-the-region-beat-the-finetuned-models-that-define-it
- q:
  - Do models finetuned on the same dataset end up close together?
  - Can you tell what a model was finetuned on from its weights?
  - Do finetuned models cluster by task?
  answers:
  - finetuning-lands-in-a-region-set-by-the-data
  - cosine-distance-on-task-vectors-is-the-metric-that-works
- q:
  - Is the clustering just an artefact of dataset size?
  - Does more finetuning data move the weights further?
  - What determines the direction a model moves during finetuning?
  answers:
  - the-direction-is-set-by-data-type-not-data-size
- q:
  - Is this just linear mode connectivity?
  - What is stronger than linear connectivity here?
  - Do all points in the convex hull of finetuned models work?
  answers:
  - the-region-is-a-basin-not-just-a-line
  - the-basin-has-a-flat-floor-and-steep-cliffs
- q:
  - Can an averaged model beat the models it was averaged from?
  - Is the best model in a region one that finetuning found?
  - Why does model averaging improve performance?
  answers:
  - points-inside-the-region-beat-the-finetuned-models-that-define-it
  - finetuning-stops-at-the-edge-of-the-region
  - it-gives-model-averaging-a-reason-to-work
- q:
  - Does finetuning find the best point in the region?
  - Where in the loss basin does gradient descent stop?
  - Is finetuning suboptimal?
  answers:
  - finetuning-stops-at-the-edge-of-the-region
  - the-basin-has-a-flat-floor-and-steep-cliffs
- q:
  - How big is the low-loss region?
  - What happens if you extrapolate past two finetuned models?
  - Is the region a subspace or a basin?
  answers:
  - the-basin-has-a-flat-floor-and-steep-cliffs
  - moving-toward-the-origin-does-not-leave-the-region
- q:
  - Should I start finetuning from an averaged model?
  - Is the centroid of finetuned models a better initialisation than the pretrained model?
  - How much does starting from a model average help?
  answers:
  - the-centroid-beats-the-pretrained-model-as-a-starting-point
  - the-gain-is-larger-when-target-data-is-scarce
- q:
  - Does this help in the few-shot setting?
  - Is the averaged initialisation better with little target data?
  - How large is the low-data gain?
  answers:
  - the-gain-is-larger-when-target-data-is-scarce
  - the-centroid-beats-the-pretrained-model-as-a-starting-point
- q:
  - Is there one region per task across all models?
  - Do models from different pretrained checkpoints share a region?
  - How many basins are there per ability?
  answers:
  - regions-are-relative-to-the-pretrained-model-you-started-from
- q:
  - How do you compare models finetuned on different datasets?
  - What is the generalized loss in this paper?
  - Why use linear probing to evaluate the models?
  answers:
  - the-generalized-loss-is-what-makes-the-comparison-possible
  - the-exterior-baseline-for-the-general-region-is-constructed
- q:
  - What distance metric should I use to compare finetuned models?
  - Why cosine similarity on task vectors instead of Euclidean distance?
  - How were the weight-space clusters computed?
  answers:
  - cosine-distance-on-task-vectors-is-the-metric-that-works
  - finetuning-lands-in-a-region-set-by-the-data
- q:
  - Do domains form regions in weight space like tasks do?
  - Does the clustering work for Twitter datasets?
  - What are the limits of the region finding?
  answers:
  - task-separates-cleanly-but-domain-does-not
  - wnli-does-not-behave-like-the-rest-of-nli
  - what-was-actually-trained
- q:
  - What models and datasets were used?
  - How many models were finetuned in this study?
  - Does this hold beyond English classification with RoBERTa?
  answers:
  - what-was-actually-trained
  - regions-are-relative-to-the-pretrained-model-you-started-from
- q:
  - What does this explain about model merging and soups?
  - Why does starting from a finetuned model help on a new task?
  - Why does Stochastic Weight Averaging work?
  answers:
  - it-gives-model-averaging-a-reason-to-work
  - points-inside-the-region-beat-the-finetuned-models-that-define-it
misreadings:
- 'The claim is two-directional and the second half is the harder one: not only do well-performing
  finetuned models fall in a region, but arbitrary points in that region also perform well
  -- including points no gradient step would ever reach. Citing only the clustering result
  drops the part that carries the paper.'
- '''Region'' means a bounded basin, not a subspace. Extrapolating slightly past the finetuned
  models degrades performance quickly; the floor is flat and the sides are steep.'
- The regions are defined relative to a pretrained checkpoint, not absolutely. Mix in a second
  RoBERTa-base reimplementation and the models cluster by which checkpoint they came from,
  so there is a neighbourhood of each starting point rather than one canonical region per
  ability.
- Every loss in the paper is a linear-probe loss on a frozen encoder with a fresh head. That
  is what makes models trained on different datasets comparable at all; it is not the accuracy
  those models would reach if fully finetuned.
- Two different numbers exist for the headline practical result, and the abstract holds the
  unsupported one. Section 7, Table 2 and Figure 6 all give the centroid a 4.03-4.04 point
  average gain with 9 wins, 2 ties and 1 loss; the abstract's 3.06 occurs once and is not
  derivable from any table in the paper. Quote 4.03 with Table 2 behind it. The abstract's
  '11 out of 12' is fine -- it is the 9 wins plus the 2 ties.
- The clustering accuracies are computed with the number of clusters set to the number of
  datasets or families and each cluster labelled by majority. They show the groups are separable
  in weight space, not that the structure was discovered without being told how many groups
  to expect. Majority labelling also lets two clusters carry one label, and the paper's own
  1-to-1 alternative in Appendix D shows how much that matters -- NLI's F1 goes from 100 to
  1 under it.
- The t-SNE pictures are illustrations. The measurements are cosine distances between 120M-dimensional
  task vectors and the PB probabilities; nothing rests on the 2-D layout.
- The result is not uniform across ways of grouping datasets. Task groups separate cleanly,
  a domain group (Twitter) does not, and WNLI may not sit inside the NLI region at all despite
  the name.
- The averaging done here is uniform weight averaging of models sharing an initialisation
  -- the geometric content is about that setting, not about merging arbitrary checkpoints
  or architectures.
terminology:
  weight space: The space in which each point is a full weight vector and so is a model; here
    120M-dimensional for RoBERTa-base.
  task vector: A finetuned model minus the pretrained model it started from -- the displacement
    finetuning produced, which is what the clustering measures.
  region: A bounded, convex-ish basin of low loss containing the finetuned models for a dataset,
    a task, or language tasks in general -- nested, in that order.
  generalized loss: The loss of a model on a target dataset after replacing its head and training
    only that head, so that models finetuned on different datasets can be scored on the same
    data.
  In / In' / Ex: The interior group of similarly finetuned models, points sampled from their
    convex hull, and an exterior group -- either models finetuned on other data or, at the
    broadest level, random perturbations of the pretrained model at matched norm.
  PB: The probability that a randomly chosen model from one group has lower generalized loss
    than a randomly chosen model from another -- the paper's single-number comparison between
    two groups of models.
  centroid: The uniform average of a region's models, used as the practical stand-in for 'inside
    the region' because no interior point is otherwise preferred.
---
