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

Then promote it:  python scripts/draft_sidecars.py --accept ties-merging-resolving-interference-when-merging-models
-->
---
key: DBLP:conf/nips/YadavTCRB23
coined: TIES-Merging
gloss: merging fine-tuned models by trimming small changes, electing a sign, and averaging
one_liner: TIES-Merging combines several independently fine-tuned checkpoints into one multitask
  model without retraining, by zeroing the smallest parameter changes, electing one sign per
  parameter by total magnitude, and averaging only the models that agree with it.
qa:
- q:
  - how do I combine multiple fine-tuned models into one?
  - can I merge fine-tuned models without retraining?
  - how do I build a multitask model from separate task-specific models?
  answers:
  - no-retraining
  - election-is-by-mass-not-by-vote
  - how-it-was-run
- q:
  - why does averaging fine-tuned weights hurt performance?
  - what causes interference when merging models?
  - why does task arithmetic degrade as I add more models?
  answers:
  - interference-sources
  - sign-conflict
  - sign-conflicts-start-at-two-models-and-survive-same-task
- q:
  - how exactly does TIES-Merging elect a sign?
  - is the sign election a majority vote across models?
  - how do I implement TIES-Merging correctly?
  answers:
  - election-is-by-mass-not-by-vote
  - no-retraining
- q:
  - how much of a task vector can I throw away?
  - why top 20 percent and not some other threshold?
  - what value of k should I use for trimming?
  answers:
  - top-20-percent-is-lossless-on-its-own-task
  - where-the-fixed-hyperparameters-came-from
- q:
  - how much does TIES-Merging actually gain over task arithmetic?
  - is model merging worth it compared to simpler baselines?
  - does TIES-Merging ever lose to the baselines?
  answers:
  - the-gains-are-one-to-four-points-and-one-cell-is-negative
  - sign-conflict
  - it-also-works-for-same-task-soups-and-as-an-initialisation
- q:
  - can a merged model replace multitask training?
  - how close does merging get to a jointly trained model?
  - will the merged model be as good as my individual fine-tuned models?
  answers:
  - merging-does-not-reach-multitask-training
  - an-oracle-sign-vector-nearly-closes-the-gap
- q:
  - what would it take to close the gap between merging and multitask training?
  - how much could better sign estimation buy?
  - can I estimate the multitask sign vector cheaply?
  answers:
  - an-oracle-sign-vector-nearly-closes-the-gap
  - merging-does-not-reach-multitask-training
- q:
  - which step of TIES-Merging matters most?
  - can I skip the trimming or the sign election?
  - what does the ablation say about the method's components?
  answers:
  - scaling-and-the-disjoint-mean-dominate-the-ablation
  - the-no-validation-recipe-drops-the-most-valuable-component
  - election-is-by-mass-not-by-vote
- q:
  - can I merge models without any validation data?
  - what hyperparameters should I use if I cannot tune them?
  - how well does the fixed k=20, lambda=1 recipe transfer?
  answers:
  - where-the-fixed-hyperparameters-came-from
  - the-no-validation-recipe-drops-the-most-valuable-component
  - the-gains-are-one-to-four-points-and-one-cell-is-negative
- q:
  - how sensitive is TIES-Merging to lambda?
  - what lambda should I pick if I do have a validation set?
  - why is lambda around 1 for TIES but 0.4 for task arithmetic?
  answers:
  - where-the-fixed-hyperparameters-came-from
  - the-no-validation-recipe-drops-the-most-valuable-component
- q:
  - does merging improve out-of-domain generalisation?
  - how do merged models do on held-out tasks?
  answers:
  - the-out-of-domain-gain-is-over-regmean-not-task-arithmetic
  - merging-does-not-reach-multitask-training
- q:
  - can I use TIES-Merging to merge checkpoints of the same task?
  - is a merged model a good initialisation for fine-tuning?
  - does TIES-Merging beat ensembling?
  answers:
  - it-also-works-for-same-task-soups-and-as-an-initialisation
  - sign-conflicts-start-at-two-models-and-survive-same-task
- q:
  - why do the signs of large parameters matter more?
  - what happens if I get parameter directions wrong?
  answers:
  - only-the-signs-of-large-parameters-matter
  - interference-sources
- q:
  - how many models can I merge before it breaks down?
  - do sign conflicts appear even with two models?
  answers:
  - sign-conflicts-start-at-two-models-and-survive-same-task
  - sign-conflict
  - merging-does-not-reach-multitask-training
- q:
  - how reliable are the reported merging numbers?
  - how was TIES-Merging evaluated?
  - were the merging results run over multiple seeds?
  answers:
  - how-it-was-run
  - the-gains-are-one-to-four-points-and-one-cell-is-negative
  - scaling-and-the-disjoint-mean-dominate-the-ablation
claims:
- id: no-retraining
  text: TIES-Merging produces a single multitask model from several task-specific fine-tuned
    checkpoints with no additional training and no access to the original training data. The
    whole procedure is elementwise arithmetic on the task vectors, and merging plus evaluation
    runs in minutes.
  scope: Checkpoints must share the same architecture and the same pre-trained initialisation
    -- the paper lists that requirement as a limitation of the whole merging literature, not
    a detail. Demonstrated on IA3 adapters over T0-3B, full fine-tuning of T5-base and T5-large,
    and CLIP visual encoders at ViT-B/32 and ViT-L/14. Two hyperparameters remain, k and lambda,
    and the no-validation recipe fixes them rather than removing them.
  evidence: Section 4.2, Algorithm 1, Appendix A, Appendix C.1
- id: interference-sources
  text: 'Two sources of interference degrade model merging: redundant parameter changes, whose
    small values pull the mean of the influential ones toward zero, and disagreement on a
    parameter''s sign across the models being merged.'
  scope: 'Demonstrated for parameter-space merging of models fine-tuned from a shared initialisation;
    not a claim about models trained from scratch. The demonstration is a magnitude analysis,
    not an ablation: parameters are bucketed by how many models find them influential, and
    by sign agreement, and the merged magnitudes compared before and after trimming or electing.
    The bucketed comparisons are run on the IA3 setting, with T5-base versions in the appendix.'
  evidence: Section 3, Section 7.1, Appendix B.5
- id: election-is-by-mass-not-by-vote
  text: The sign election is not a majority vote. For each parameter the trimmed values are
    summed across models and the sign of that sum is taken, so one model with a large change
    outvotes several models with small opposite ones. The merge that follows is a mean over
    only the models whose own sign matches the elected one, and it ignores the zeros left
    by trimming -- which is what keeps the surviving magnitudes from being diluted.
  scope: 'This is a description of the published algorithm, so it is as reliable as reading
    it. Worth stating because the paper''s own prose says the elected sign is the one with
    ''greater total movement'' while the phrase most readers carry away is sign conflict resolution,
    and a re-implementation as a count-based vote is a different method. The two design choices
    are separable and the ablation separates them: electing and the disjoint mean are removed
    independently.'
  evidence: Section 4.2 step 2, Section 4.2 step 3, Algorithm 1
- id: top-20-percent-is-lossless-on-its-own-task
  text: Trimming a task vector to its top 20% of values by magnitude and resetting the other
    80% to the pre-trained value leaves that task's performance essentially unchanged, which
    is what licenses discarding them before merging.
  scope: 'Measured as the average over the eleven IA3 task-specific models, each trimmed and
    evaluated on its own task -- so it is a statement about redundancy inside a single fine-tuning
    run, established before any merging happens, and the sweep over k is what picks 20%. The
    retention curve for merged models runs the other way: as k grows past 20 the merged performance
    falls and then flattens, and sign conflicts rise toward 80% of parameters, so 20% is not
    a universally safe density but the point where those two curves meet in this setting.
    The paper notes the curve depends on how parameter values are distributed in the task
    vector.'
  evidence: Section 3, Appendix B.2, Appendix B.3, Appendix C.3
- id: sign-conflicts-start-at-two-models-and-survive-same-task
  text: Sign conflicts are not a many-model phenomenon. After trimming to the top 20%, conflicts
    are already present when merging two models from different tasks, they increase monotonically
    as the count goes from 2 to 11, and they appear at a similar rate among ten differently
    fine-tuned checkpoints of the same task.
  scope: The cross-task measurements use the eleven IA3 models, with a T5-base version in
    the appendix; the same-task measurements use ten public BERT-base checkpoints each for
    RTE, MRPC and WNLI. These are counts of conflicting parameters, not performance, so they
    establish that the phenomenon exists at small counts rather than that it costs anything
    there -- and the scaling experiment shows two-model merges losing almost nothing. The
    paper's explanation, that overparameterised models have many equivalent subnetworks so
    different runs move the same parameter in opposite directions, is offered as a suspicion.
  evidence: Section 3, Appendix B.3, Appendix B.4, Appendix C.3
- id: only-the-signs-of-large-parameters-matter
  text: The directions of large parameter changes carry the task and the directions of small
    ones do not. Flipping the sign of each of the top 20% or 30% of a task vector's parameters
    with probability p degrades performance monotonically in p, while flipping the bottom
    80% or 70% the same way barely moves it.
  scope: 'Eleven IA3 task vectors, averaged over three runs, each perturbed model evaluated
    on its own task -- so this is about what a single task vector needs, and it motivates
    the election step rather than testing it. The asymmetry is partly definitional: the trimming
    experiment already showed the bottom 80% can be deleted outright, so flipping it is expected
    to be cheap.'
  evidence: Section 7.2
- id: sign-conflict
  text: Trimming low-magnitude parameter changes, electing a single sign per parameter, and
    averaging only the agreeing values beats plain weight averaging, Fisher merging, RegMean
    and task arithmetic in every setting reported, and the advantage over task arithmetic
    grows as more models are merged.
  scope: Up to 11 models in the PEFT setting and up to 8 in the others; same architecture
    and initialisation throughout. The grows-with-count result is a separate experiment on
    T5-large (T5-base in the appendix), plotting accuracy normalised by each task's own fine-tuned
    model, averaged over at most 10 random task subsets per count -- so it is a mean over
    subsets with no dispersion reported, and at two models both methods are already near-lossless
    while simple averaging drops about 10%.
  evidence: Section 6, Section 7.3, Appendix C.5
- id: the-gains-are-one-to-four-points-and-one-cell-is-negative
  text: 'The improvements over the strongest baseline are single-digit and uneven: with a
    validation set, +2.5 on IA3, +0.7 on T5-base, +3.6 on T5-large, +1.8 on ViT-B/32 and +1.5
    on ViT-L/14. The abstract''s 2.3% and 1.7% are the means of the language and vision columns.
    Without a validation set the fixed recipe scores +0.9, +6.6 and +2.7 on T5-large, ViT-B/32
    and ViT-L/14 and minus 3.2 on T5-base, where it reaches 69.7 against task arithmetic''s
    73.2.'
  scope: 'One negative cell out of nine, printed by the paper itself, and it is in the setting
    most people will try first: full fine-tuning of a small language model with no validation
    data. The deltas are against the best baseline per column, which is not the same method
    in every column, so they are not deltas against one competitor. Every number is a single
    reported figure with no seeds or error bars, and the IA3 column is a median over prompt
    templates while the others are plain accuracies. The 0.7 on T5-base with a validation
    set is smaller than the spread one would expect between reruns.'
  evidence: Section 6, Section 1
- id: merging-does-not-reach-multitask-training
  text: 'The merged model stays well short of both a jointly trained multitask model and the
    individual fine-tuned models it was built from: 73.6 against 88.9 and 90.5 on ViT-B/32,
    76.9 against 88.1 and 88.8 on T5-large, 73.9 against 83.6 and 82.8 on T5-base. IA3 is
    the one setting where merging clears the fine-tuned average, and it does not: 66.4 against
    73.1 multitask and 71.4 fine-tuned.'
  scope: 'These are the same table as the headline gains, read down the column instead of
    across the row, and the paper states the gap as a limitation rather than hiding it. What
    the comparison does not settle is whether the remaining gap is intrinsic to merging or
    an artefact of fixed hyperparameters, since the multitask rows are trained models with
    their own tuning. Merging still buys what multitask training cannot: no data, no gradients,
    and minutes of compute.'
  evidence: Section 6, Appendix A, Appendix C.1
- id: an-oracle-sign-vector-nearly-closes-the-gap
  text: Almost all of the remaining gap is sign estimation. Substituting the sign vector of
    an actually trained multitask model for the elected one lifts IA3 merging from 66.4 to
    72.0, against 73.1 for that multitask model and above the 71.4 average of the individual
    fine-tuned models.
  scope: 'It is an oracle: obtaining that sign vector requires training the multitask model
    the merge was supposed to replace, so the 72.0 is a ceiling on what better sign estimation
    could buy, not a result anyone can use. The paper''s own attempt to reach it cheaply --
    training a multitask IA3 model on 32 validation examples per task and taking its signs
    -- gets 67.7 when initialised from the mean of the models being merged and 66.5 from scratch,
    so the practical version recovers about a fifth of the 5.6 points. Single runs, IA3 only.'
  evidence: Section 7.4, Appendix B.1
- id: scaling-and-the-disjoint-mean-dominate-the-ablation
  text: 'Removing one component at a time ranks them scaling first, disjoint mean second,
    then trimming and electing: minus 2.5 and minus 1.9 on T5-base and minus 5.2 and minus
    3.2 on IA3 for the first two, against minus 1.5 and minus 1.4 on T5-base and minus 0.1
    and minus 1.1 on IA3 for trimming and electing. The two steps the method is named after
    are the two that cost least to remove.'
  scope: 'Validation-set numbers, so the baselines here are 74.5 and 70.7 rather than the
    main table''s 73.9 and 66.4, and single runs. The ordering is not a claim that electing
    is dispensable: removing elect while keeping the disjoint mean still averages only nonzero
    values, so the ablated variants share most of the machinery and each row measures a marginal
    contribution on top of the others rather than a standalone method. Two settings, and they
    disagree about trimming -- it costs 1.5 points on T5-base and 0.1 on IA3.'
  evidence: Section 7.3
- id: the-no-validation-recipe-drops-the-most-valuable-component
  text: Removing scaling means setting lambda to 1 -- which is exactly what the recommended
    no-validation recipe does. So the ablation's largest drop and the price of the hyperparameter-free
    recipe are the same quantity, and on T5-base validation data it is 2.5 points.
  scope: 'That identification is a derivation from the ablation''s own definition of the row,
    not something the paper draws out, and the two experiments are reported in different sections
    on different splits, so the 2.5 should be read as an indication of the cost rather than
    a measurement of the recipe. It is consistent with the recipe''s one negative cell being
    on T5-base. The offsetting fact is that TIES is far less lambda-sensitive than task arithmetic:
    over the lambda values tried its accuracy spans roughly 68 to 75 where task arithmetic''s
    spans 55 to 75, so a fixed lambda hurts it much less than it would hurt the baseline.'
  evidence: Section 7.3, Section 5, Appendix B.2, Appendix C.4
- id: where-the-fixed-hyperparameters-came-from
  text: 'The k=20, lambda=1 recipe was tuned, just not on the settings it is reported for:
    the search ran over the eleven IA3 models with k in {10, 20, 30} and lambda from 0.8 to
    3.0, found k=20 best and 0.9, 1.0 and 1.1 equivalent, and 1 was picked for simplicity.
    It was then applied unchanged to the unseen T5 and ViT settings. Task arithmetic gets
    its own published default of lambda=0.4 in the same comparison.'
  scope: 'So the no-validation numbers are a genuine transfer test for T5 and ViT and not
    one for IA3, which is why the IA3 no-validation cells are blank. The tuning range for
    lambda was itself narrowed to 0.8-1.8 by preliminary PEFT experiments before the reported
    sweep. One caveat on treating lambda=1 as the right value in general: when a validation
    set is available and subsets of T5-large tasks are merged, the selected lambda for TIES
    runs from 1.1 to 3.0 with most values between 1.5 and 2.0, while task arithmetic''s selected
    lambda falls from 1.0 toward 0.5 as tasks are added. The two are on different scales --
    TIES averages task vectors where task arithmetic sums them -- so lambda=1 for TIES is
    comparable to 1/n for task arithmetic.'
  evidence: Appendix C.4, Section 5, Appendix B.2, Appendix C.5
- id: the-out-of-domain-gain-is-over-regmean-not-task-arithmetic
  text: On six held-out T0 tasks the merged models score 35.3 and 40.4 for T5-base and T5-large.
    The baseline being beaten by 1.0 and 4.4 is RegMean at 34.3 and 36.0; task arithmetic,
    the strongest in-domain competitor, manages 31.9 and 32.3 -- for T5-base that is within
    a point of the 31.1 zero-shot model.
  scope: The merged models are the in-domain ones, evaluated without adaptation on question
    answering, word sense disambiguation and sentence completion tasks held out of the merge.
    Absolute accuracies of 27 to 40 mean every method here is weak and the comparison is among
    weak models, so a 4.4-point gap is large relative to the spread and small relative to
    what any fine-tuned model would score. Which baseline is strongest changes between the
    in-domain and out-of-domain tables, so 'outperforms the strongest baseline' names a different
    method in each. Single runs.
  evidence: Section 6, Appendix B.6
- id: it-also-works-for-same-task-soups-and-as-an-initialisation
  text: 'Two applications beyond multitask merging. Merging ten public same-task BERT checkpoints
    beats averaging, Fisher merging and ensembling: 72.2 on RTE and 86.8 on MRPC. And merging
    the seven other GLUE tasks to initialise fine-tuning beats every other initialisation
    including the pre-trained model: 80.1 on RTE and 88.0 on MRPC against 66.4 and 81.8.'
  scope: Three downstream tasks, one model family, single runs, and the third task undercuts
    both tables -- WNLI, where merging loses to task arithmetic in the soup setting (58.8
    against 59.2) and to plain averaging as an initialisation (54.9 against 56.3). WNLI is
    also where three separate configurations land on exactly 56.3, the level a constant predictor
    reaches on its dev set, so that column is mostly sorting methods by noise around a degenerate
    baseline and should not carry weight either way. The soup comparison uses another paper's
    code and checkpoint selection.
  evidence: Section 6, Appendix B.4
- id: how-it-was-run
  text: 'The evaluation spans five settings: IA3 adapters on T0-3B over 11 tasks, full fine-tuning
    of T5-base and T5-large over 7 GLUE-style tasks, and CLIP ViT-B/32 and ViT-L/14 visual
    encoders over 8 image classification tasks, against simple averaging, Fisher merging,
    RegMean and task arithmetic, with fine-tuned and jointly trained multitask models as reference
    points.'
  scope: Language results use rank classification -- the model's log probabilities for each
    label string are ranked and the top one taken as the prediction -- and IA3 numbers are
    medians over the prompt templates of each dataset, which is a different statistic from
    the means reported elsewhere. Vision checkpoints are taken from the task-arithmetic release
    rather than trained here. T5 models were trained up to 75,000 steps at batch size 1024
    and learning rate 1e-4 with early stopping, bfloat16 and a 128-token limit; the IA3 models
    used batch size 16 and patience 10; no scheduler and no weight decay anywhere. Everything
    ran on 48GB A6000 GPUs, single task models taking 15 minutes to 2 hours and the multitask
    reference up to 24 hours on four GPUs, while a merge plus evaluation takes under 2 minutes
    outside the template-heavy IA3 protocol. Dataset licences are enumerated, and a few could
    not be found.
  evidence: Section 5, Section 6, Appendix C.1, Appendix C.2, Appendix C.6
misreadings:
- It is not a training method. No gradient steps and no training data are required.
- It does not merge models with different architectures or different pre-trained initialisations.
- 'The sign is elected by total magnitude, not by majority vote: the trimmed values are summed
  across models and the sign of the sum is taken, so one model with a large change outweighs
  several with small opposite ones. A count-based reimplementation is a different method.'
- '"Resolving sign disagreement is the component that matters most" is not what the ablation
  says. Removing the scaling factor and the disjoint mean cost the most (2.5 and 1.9 points
  on T5-base, 5.2 and 3.2 on IA3); removing electing costs 1.4 and 1.1 and removing trimming
  1.5 and 0.1. Signs matter most in the analysis -- the oracle-sign experiment and the sign-flipping
  experiment -- not in the ablation of the method''s own steps.'
- 'The hyperparameter-free recipe is not free. Fixing lambda=1 is exactly the ablation''s
  ''remove scaling'' condition, whose cost is the largest of the four, and the recipe produces
  the paper''s one negative cell: 69.7 on T5-base against task arithmetic''s 73.2. With a
  validation set that setting becomes 73.9.'
- Merging does not reach multitask training. The merged models score 73.6 against 88.9 on
  ViT-B/32 and 76.9 against 88.1 on T5-large, and in four of five settings they also fall
  below the average of the individual fine-tuned models. The paper lists this as a limitation.
- The near-multitask result of 72.0 uses the sign vector of an already trained multitask model.
  It is an upper bound on better sign estimation, not an available method; estimating those
  signs from 32 examples per task gets 67.7.
- The out-of-domain result is over RegMean, not over task arithmetic -- and on T5-base task
  arithmetic is within a point of the unmerged zero-shot model. All the absolute numbers there
  are between 27 and 40.
- The claim that gains widen with more models is about the comparison with task arithmetic
  on normalised accuracy averaged over task subsets. At two models both methods lose almost
  nothing; it is simple averaging that already drops about 10%.
- '"Keeping the top 20% is lossless" is measured on each task vector against its own task
  before any merging. For merged models, performance falls as more parameters are kept, and
  the paper notes the curve depends on how the task vector''s values are distributed.'
- Sign conflicts are not evidence that a merge will fail. They already occur with two models
  and among checkpoints of the same task, while two-model merges are near-lossless -- the
  counts show the phenomenon is ubiquitous, not that it is costly at small scale.
- The reported deltas are against the strongest baseline in each column, and that is not the
  same baseline in every column or between the in-domain and out-of-domain tables. They are
  not head-to-head margins over one competitor.
- The WNLI column of the two auxiliary tables should not be read as a result. TIES loses there
  in both, and three configurations land on exactly 56.3 -- the majority-class level -- so
  the column separates methods by noise around a degenerate baseline.
- Numbers in the main tables are single runs. Only the sign-flipping experiment reports an
  average over repeats, and no table carries error bars, so single-digit differences should
  be treated as indications rather than measurements.
terminology:
  interference: Used narrowly here for two specific effects during parameter merging -- redundant
    parameter values, and sign disagreement across models -- not for task interference during
    multitask training.
  trim: Resetting the parameters that changed least during fine-tuning back to their pre-trained
    values, before any averaging. Controlled by k, the percentage kept; k=20 in the recommended
    recipe.
  elect: Choosing one sign per parameter for the merged model by summing the trimmed changes
    across models and taking the sign of that sum -- the direction with the greater total
    magnitude, not the one held by more models.
  disjoint mean: Averaging a parameter over only those models whose own sign matches the elected
    sign, ignoring the zeros left by trimming. The denominator therefore varies per parameter,
    which is what stops the surviving magnitudes from being diluted.
  task vector: The difference between a fine-tuned checkpoint and the shared initialisation
    it started from. Every method compared here operates on these differences rather than
    on the weights themselves.
  sign vector: The elementwise sign of a task vector, the direction along each parameter axis
    that reduces that task's loss. Paired with the magnitude vector, it factorises the task
    vector exactly.
  sign conflict: A parameter for which the models being merged do not agree on the sign of
    their changes. Reported as the fraction of parameters affected, and measured after trimming.
  sign agreement: 'A per-parameter score used to bucket parameters in the analysis: 1 when
    all models share a sign, 0.5 when they split evenly. Distinct from sign conflict, which
    is a yes-or-no count.'
  multitask vector: The task vector of a model trained jointly on all the tasks. Its sign
    vector is the oracle used to bound how much better sign estimation could be, and obtaining
    it requires the training that merging is meant to avoid.
  lambda: The factor the merged task vector is scaled by before it is added back to the initialisation.
    Because TIES averages task vectors where task arithmetic sums them, lambda=1 for TIES
    corresponds roughly to 1/n for task arithmetic.
  model soup: Merging several checkpoints trained on the same task to improve that one task,
    as opposed to merging different tasks into a multitask model. Used here as a second application,
    with ten public checkpoints per task.
  rank classification: 'The evaluation protocol for the language settings: score every candidate
    label string under the model and count the prediction correct if the gold string ranks
    first. It covers both classification and multiple choice without generation.'
---
