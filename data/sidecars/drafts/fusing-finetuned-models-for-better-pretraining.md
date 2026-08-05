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

Then promote it:  python scripts/draft_sidecars.py --accept fusing-finetuned-models-for-better-pretraining
-->
---
coined: fusing
gloss: averaging the weights of several models finetuned from the same pretrained checkpoint,
  to get a better starting point for finetuning on a new task
one_liner: 'Fusing averages the weights of several models finetuned from the same pretrained
  checkpoint and uses the result as the base model for a new task: it beat the pretrained
  baseline on 6 of the 9 source-target combinations, and it survived the weight decay that
  wiped out intertraining''s advantage (65.1 against 61.7).'
claims:
- id: fusing-by-weight-averaging
  text: Fusing takes several models finetuned from the same pretrained checkpoint and averages
    their weights element-wise, then uses that average as the base model for finetuning on
    a new target task -- reversing the usual direction of transfer learning, in which a pretrained
    model is reused to make better finetuned models rather than finetuned models being reused
    to make a better pretrained one.
  scope: 'The paper deliberately proposes the simplest possible fusion function: a plain mean
    over each weight shared by all the models, with no weighting, no alignment and no training
    step. It requires that all the models were finetuned from one common initialization, which
    is what makes averaging meaningful at all, and it needs neither the source data of those
    models nor the target data -- so its cost is essentially the download. The fused model
    is a starting point, not a model: it need not perform any of the source tasks.'
  evidence: Section 2, Section 1, Figure 1
- id: fusing-generalizes-intertraining
  text: 'Fusing generalizes intertraining: intertraining picks one existing finetuned model
    as the initialization for the target task, which is the special case of fusing where only
    a single model is combined.'
  scope: A framing claim rather than a result -- it is what makes intertraining the natural
    baseline and what lets the same experiment answer 'is one model or several better'. The
    identification is exact for the averaging function used here, since the mean of one vector
    is that vector.
  evidence: Section 1, Figure 1
- id: beats-the-pretrained-baseline-except-on-twitter
  text: Fusing all available finetuned models beat starting from the pretrained model on the
    General and NLI target families -- 68.12, 68.96 and 64.17 accuracy against 63.81 on General,
    and 67.95, 70.65 and 66.74 against 67.66 on NLI -- but not on the Twitter target family,
    where all three fused models scored below the pretrained baseline (54.71, 54.54 and 52.86
    against 55.73).
  scope: 'The paper states this result more strongly than its own table supports: the abstract
    says ''the fused model results surpass the pretrained model ones'' and Section 4 says
    fusing is ''consistently better than pretraining'', while Table 1''s Twitter target column
    is an exception in all three source families. Read it as holding in 6 of the 9 source-target
    combinations, and as not yet shown for a target family of short social-media text. Rows
    are source families and columns target families; every figure is a mean over the datasets
    in the target family and over 5 random seeds, on T5v1.1-small, with the target task always
    excluded from the set of source models.'
  evidence: Table 1, Section 4, Abstract
- id: carefully-chosen-intertraining-still-wins
  text: 'Fusing everything available does not beat a well-chosen intertraining task: the best
    intertraining configuration averaged 66.48 across the three target families against 64.72
    for the best fusing configuration. The paper''s point is that this comparison flatters
    intertraining, because most choices of intermediate task are worse than not intertraining
    at all.'
  scope: The intertraining baseline here is not an average over arbitrary choices -- it uses
    the heuristic of taking the model finetuned on the largest training set, which for the
    General family selects MNLI, previously reported as the best intermediate task for that
    set. So the comparison is fusing-without-selection against intertraining-with-a-good-selection.
    Which intermediate task serves a given target is a separate open research question, and
    the paper does not measure how often the heuristic picks well.
  evidence: Table 1, Section 3.3, Section 4
- id: fusing-pairs-beats-intertraining
  text: 'Choosing which models to fuse changes the result dramatically, and fusing two models
    is often better than intertraining with either of them: across the pairs tested, fusing
    beat the worse of the two models in all but one pair, beat their mean in most cases, and
    frequently beat the better of the two. Fusing the models finetuned on MNLI and SST2 gave
    the highest accuracy in the whole experiment.'
  scope: Restricted to the GLUE datasets to keep the number of experiments manageable, and
    reported as a colour-coded matrix of pairwise comparisons rather than a table of numbers
    -- so the paper gives no aggregate figure for how much fusing two models beats intertraining
    by. The models that fuse best are the ones that also intertrain well, so this does not
    remove the need to choose source models; it changes what you get for choosing well.
  evidence: Figure 2, Section 4
- id: fusing-is-less-target-dependent
  text: 'Intertraining is sensitive to which target task you are aiming at and fusing is much
    less so: for intertraining the best source family is always the one most similar to the
    target (72.76 for General source on General target, 71.11 for NLI on NLI, 57.18 for Twitter
    on Twitter, each the best in its column), whereas for fusing a single source set -- the
    NLI models -- was good across target families.'
  scope: 'Three source families and three target families, so ''consistently'' rests on three
    columns: the NLI source set was the best fusing source on the General and NLI targets
    and second-best on Twitter. This is the paper''s central practical argument -- fusing
    does not require a relation between source and target tasks while intertraining does --
    and it is an observed pattern across nine cells, not a controlled test of task similarity.'
  evidence: Table 1, Section 4, Section 5
- id: weight-decay-nullifies-intertraining-not-fusing
  text: 'Weight decay during finetuning erases intertraining''s advantage but not fusing''s:
    with AdamW at decay 0.01, intertraining scored 61.7 against 61.6 for the pretrained baseline
    -- no gain at all -- while fusing scored 65.1. Without decay the same three were 72.76,
    63.87 and 68.12.'
  scope: General target datasets only. Every score is lower with decay, so this is not an
    argument for using it -- it is an argument that a default many practitioners leave on
    (it is the default in HuggingFace's trainer) can silently remove the benefit intertraining
    is chosen for. Preliminary trials with BERT, which was pretrained with decay, showed less
    of the adverse effect, from which the paper infers that intertraining should match how
    pretraining was done; that inference rests on initial trials rather than a reported experiment.
    The pretrained baseline on General appears as 63.81 in Table 1 and 63.87 in Table 2.
  evidence: Section 4.1, Table 2, footnote 1
- id: both-are-more-stable-than-pretraining
  text: 'Fusing and intertraining are both markedly more stable across random seeds than finetuning
    from the pretrained model: the pretrained baseline''s standard deviation averaged 3.64
    (and reached 5.75 on the Twitter target family), against 1.21 to 2.27 for the fused base
    models and 1.61 to 2.24 for the intertrained ones.'
  scope: Standard deviation over 5 random seeds of finetuning on the target task, so it measures
    the stability the base model confers rather than any property of the base model itself.
    Every configuration of both methods was more stable than the pretrained baseline, which
    is the strongest form of this table's claim. The Twitter target family carries the largest
    deviations throughout -- and is also where fusing loses on accuracy. The rendering of
    the appendix table does not label its rows unambiguously, so the ranges are reliable where
    a deviation attached to one specific source family is not.
  evidence: Appendix C, Table 3, Section 3
- id: source-data-size
  text: More source training data produces better fused models. A second, noisier trend is
    that fusing benefits from smaller amounts of source data than intertraining does, but
    its improvement also plateaus sooner -- possibly because it draws on data from several
    models at once.
  scope: One figure, on a log scale, with the General datasets as targets; the paper labels
    the second trend noisy and offers the several-models explanation as a possibility rather
    than a test. No claim is made about how much source data is enough.
  evidence: Section 4.2, Figure 3
- id: no-theory-for-why-averaging-works
  text: 'The paper is explicit that there is little theory to support weight averaging and
    that in the general case it probably does not work: networks are non-linear in their weights,
    so the average of two models'' weights does not compute the average of their functions,
    and studies of model similarity do not find models similar weight-by-weight. Its best
    account is that the shared pretrained initialization is what makes averaging meaningful,
    and it leaves the mechanism to future work.'
  scope: 'A stated limitation, not a result. The supporting intuitions it does offer are drawn
    from other people''s work rather than tested here: monotonic linear interpolation (which
    weakens under adaptive optimizers, and which the paper notes does not describe what it
    actually does, since it starts from a pretrained rather than random initialization) and
    linear mode connectivity (which is not a general property of neural networks). Models
    are found to be similar in activations, classifications and generalizations even though
    they are not similar per weight.'
  evidence: Section 5, Appendix D
- id: meta-learning-framing
  text: 'Fusing moves initialization from transfer learning into meta-learning: where transfer
    learning starts from a model that performs one task well, the fused model may perform
    none of them, and is instead the point at roughly least Euclidean distance from each source
    model, which the paper argues needs less finetuning than the original initialization.
    In that sense it resembles a single step of REPTILE.'
  scope: An interpretation offered to explain why fusing might work and why errors introduced
    by averaging can be fixed later in training -- not a meta-learning algorithm, and not
    compared against one. The 'least distance' description follows from averaging rather than
    being optimized for. Iterating fusing and finetuning is named as future work; it is not
    done here.
  evidence: Section 5, Section 6
- id: finetuned-models-are-abundant
  text: 'The premise the method rests on is that finetuning is ubiquitous while pretraining
    is rare, so finetuned models are an unused resource: of 20 arbitrarily chosen EMNLP 2021
    papers, 14 finetuned a model and none pretrained one, which the paper extrapolates to
    roughly 560 of that conference''s 800-plus papers and 2,261 of ACL 2021''s 3,230, and
    T5-Small saw 3M downloads in a month against 30K for its most popular finetuned version.'
  scope: 'Counts from 2022, when the Hugging Face hub hosted about 27K models; the extrapolation
    is from a 20-paper sample and the download figures are proxies for finetuning runs rather
    than measurements of them. The same appendix cuts against convenience as much as for it:
    most finetuned models are never uploaded, and those that are get shared for reproducibility
    rather than as starting points -- which the paper reads as evidence that nobody currently
    treats them as reusable initializations.'
  evidence: Appendix A, Section 1
- id: experimental-design
  text: 'The experiments span 30 English text-classification datasets in three families chosen
    to separate different kinds of relatedness: a diverse benchmark family (GLUE and SuperGLUE
    classification tasks), a same-task family (natural language inference), and a same-domain
    family (the 11 TweetEval datasets), with every combination of source family and target
    family tested and the target task always excluded from the source models.'
  scope: Text classification only, chosen for ease of evaluation, with the assumption -- stated
    as an assumption -- that the tasks are diverse enough for the conclusions to extend elsewhere.
    One pretrained model (T5v1.1-small), picked partly because it was not trained on any task
    beyond its pretraining objective, which would otherwise contaminate the comparison. Because
    GLUE and SuperGLUE test sets are held out, test sets were carved from the training data
    (1K examples or 10%, whichever is smaller), so absolute accuracies are not comparable
    to published GLUE numbers.
  evidence: Section 3.1, Section 3.2, Section 3.4, Appendix B
- id: concurrent-merging-work
  text: Two concurrent papers proposed recycling finetuned models by combining weights --
    model soups (Wortsman et al., 2022) and Fisher-weighted merging (Matena and Raffel, 2021)
    -- but both use the merged model directly rather than as a base model to finetune further,
    soups average models finetuned on the same target task and mostly in vision, and Fisher
    merging weights each parameter by its estimated importance, which requires data this setting
    does not have.
  scope: 'Positioning, written in 2022 and describing those papers as parallel work rather
    than baselines -- no experimental comparison against either is reported. The Fisher point
    is the substantive distinction: choosing per-weight coefficients from data conflicts with
    wanting a base model that is general, when neither the source data of the fused models
    nor the target data is available.'
  evidence: Section 5
qa:
- q:
  - Can I average the weights of several finetuned models to get a better starting point?
  - Does merging finetuned model weights help before finetuning on a new task?
  - What is model fusing?
  - How do I reuse existing finetuned models instead of pretraining my own?
  answers:
  - fusing-by-weight-averaging
  - beats-the-pretrained-baseline-except-on-twitter
  - finetuned-models-are-abundant
- q:
  - Is intermediate-task finetuning better than merging several models?
  - Should I intertrain on one task or fuse several finetuned models?
  - How does fusing compare to intertraining?
  answers:
  - fusing-generalizes-intertraining
  - carefully-chosen-intertraining-still-wins
  - fusing-pairs-beats-intertraining
- q:
  - Does intermediate-task training require a source task related to my target task?
  - Do the models I merge have to be related to the task I care about?
  - Why does intertraining sometimes hurt performance?
  answers:
  - fusing-is-less-target-dependent
  - carefully-chosen-intertraining-still-wins
  - beats-the-pretrained-baseline-except-on-twitter
- q:
  - Does weight decay interact with intermediate-task finetuning?
  - Why did intertraining stop helping when I turned on weight decay?
  - Is weight merging robust to optimizer settings?
  answers:
  - weight-decay-nullifies-intertraining-not-fusing
  - both-are-more-stable-than-pretraining
- q:
  - How can I make finetuning less sensitive to the random seed?
  - Does the choice of base model affect training stability?
  - Why do my finetuning results vary so much between runs?
  answers:
  - both-are-more-stable-than-pretraining
  - beats-the-pretrained-baseline-except-on-twitter
- q:
  - Why would averaging neural network weights work at all?
  - Is there theory behind model merging?
  - When does weight averaging fail?
  answers:
  - no-theory-for-why-averaging-works
  - fusing-by-weight-averaging
  - meta-learning-framing
- q:
  - Which models should I pick to merge?
  - Does it matter which finetuned models go into a merge?
  - What is the best pair of models to average for a new task?
  answers:
  - fusing-pairs-beats-intertraining
  - fusing-is-less-target-dependent
  - source-data-size
- q:
  - How much source data do the models I merge need?
  - Does the size of the source task's training set matter for merging?
  - Do bigger intermediate tasks make better base models?
  answers:
  - source-data-size
  - carefully-chosen-intertraining-still-wins
- q:
  - How is fusing different from model soups or Fisher-weighted merging?
  - What is the difference between merging models and averaging a model soup?
  - Can I merge models without access to any training data?
  answers:
  - concurrent-merging-work
  - fusing-by-weight-averaging
  - meta-learning-framing
- q:
  - Is choosing a good initialization a meta-learning problem?
  - How does weight merging relate to meta-learning like REPTILE?
  - Can a base model be useful if it performs none of the tasks it came from?
  answers:
  - meta-learning-framing
  - fusing-by-weight-averaging
  - no-theory-for-why-averaging-works
- q:
  - How was model fusing evaluated?
  - Which datasets were used to test weight merging for pretraining?
  - Has fusing been tested outside text classification?
  answers:
  - experimental-design
  - beats-the-pretrained-baseline-except-on-twitter
  - fusing-is-less-target-dependent
- q:
  - Are there enough finetuned models around to make merging worthwhile?
  - How common is finetuning compared to pretraining?
  - Why are finetuned models an underused resource?
  answers:
  - finetuned-models-are-abundant
  - fusing-by-weight-averaging
misreadings:
- '''Fusing always beats pretraining'' is stronger than the results. The paper''s own Table
  1 has an exception: on the Twitter target family every fused base model scored below the
  pretrained one (54.71, 54.54, 52.86 against 55.73), while intertraining beat it there. The
  claim holds in 6 of the 9 source-target combinations tested, and the abstract''s phrasing
  is broader than that.'
- Fusing did not beat intertraining across the board. Fusing everything available lost to
  a well-chosen intermediate task (64.72 against 66.48 on average). What beat intertraining
  was fusing a carefully chosen pair -- and the pairs that fuse best are the ones that also
  intertrain well, so choosing source models still matters. The claim is that fusing is more
  forgiving, not that it removes the choice.
- This is not the same thing as model soups or Fisher merging, which appeared in parallel.
  Those merge models and use the result directly; here the merged model is a base model that
  is then finetuned on a new task, and it may perform none of the source tasks. Soups also
  average models finetuned on the same target task, mostly in vision, which is a different
  setting entirely.
- The weight-decay finding is not an argument for weight decay. Every score is lower with
  decay (61.6, 61.7 and 65.1 against 63.87, 72.76 and 68.12). The point is that a default
  many practitioners leave on can silently erase intertraining's benefit while leaving fusing's
  intact -- and the BERT observation that pretraining with decay reduces the effect comes
  from initial trials, not a reported experiment.
- Nothing here explains why averaging weights works. The paper says plainly that there is
  little theory for it, that averaging weights does not average the functions the networks
  compute, and that in the general case it probably is not beneficial -- offering only that
  the shared pretrained initialization is likely what makes it meaningful, and leaving the
  mechanism open.
- The results are one small model on English text classification. All the numbers come from
  T5v1.1-small over 30 classification datasets, with test sets carved out of training data
  because GLUE and SuperGLUE hold theirs back -- so absolute accuracies are not comparable
  to published GLUE scores, and the extension to other model sizes, languages and task types
  is an assumption the paper states rather than a result.
- The stability result is about the target-task finetuning, not about the merged model. Standard
  deviations of 1.21-2.27 for fusing against 3.64 for the pretrained baseline are across 5
  random seeds of finetuning on the target task; they say the base model makes training more
  reproducible, not that the fused weights are themselves better behaved.
terminology:
  fusing: 'This paper''s term: combining several models finetuned from a common pretrained
    checkpoint into a single new base model, here by averaging their weights. A base model
    to finetune from, not a model to use. Later work in this line calls the same operation
    model merging.'
  intertraining: Using a model already finetuned on some other task as the initialization
    for a target task -- also called intermediate-task finetuning. This paper treats it as
    fusing with n = 1, which is what makes it the natural baseline.
  base model: Whatever weights finetuning on the target task starts from -- the pretrained
    model, an intertrained model, or a fused one. The paper's whole subject is the choice
    of base model, so 'better model' throughout means better starting point, not better task
    performance.
  source task / target task: Source tasks are the ones the available finetuned models were
    trained on; the target task is the one being evaluated. In every experiment the target
    task is excluded from the source set, so no fused model has seen the task it is tested
    on.
  dataset family: A group of target tasks sharing something specific -- a benchmark (GLUE
    and SuperGLUE), a task (NLI), or a domain (TweetEval). The design uses these to ask whether
    relatedness of task or of domain is what makes a source model useful.
  monotonic linear interpolation / linear mode connectivity: 'Two prior findings the paper
    cites as motivation for averaging being meaningful at all: that loss can decrease monotonically
    along the line from an initialization to a trained model, and that linear combinations
    of two models trained on one task can have similar loss. Neither is a general property
    of neural networks, and the paper presents both as intuition rather than support.'
---
