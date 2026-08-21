---
key: choshen2025hitchhiker
one_liner: A meta-analysis of over 1,000 scaling laws fit to a released dataset of losses
  and evaluations from 485 published pretrained models, yielding concrete best practices for
  estimating a scaling law for a new model family.
claims:
- id: dataset
  kind: context
  text: A Hitchhiker's Guide to Scaling Law Estimation releases a public dataset of pretraining
    losses and downstream evaluations for 485 published pretrained models. The dataset covers
    more than 40 scaled model families and 1.9M recorded training steps.
  scope: Language models whose largest family member exceeds 3B parameters and whose data
    was public or privately shared; some losses were manually extracted from published figures.
  evidence: Section 3.1
- id: guide-context
  kind: context
  text: A Hitchhiker's Guide to Scaling Law Estimation is a practical guide to choosing the
    preliminary models used to fit a language-model scaling law. It asks how many, how large
    and how fully trained they should be, rather than proposing a law for one family.
  scope: Loss-based scaling laws in the Hoffmann et al. (2022) functional form, fit with square
    loss and replicated with Huber loss; as of publication in 2025.
  evidence: Section 1
- id: target-accuracy
  kind: result
  text: A scaling law needs about 4% absolute relative error to be useful for comparing pretraining
    decisions. No widely adopted pretraining change surveyed was motivated by less than a
    4% relative loss difference, and seed-to-seed variation alone reaches 3.5%.
  scope: Based on a survey of published A/B tests on pretraining decisions, where reported
    effects run from 4% up to 50%; errors up to 20% still separate many modeling choices.
  evidence: Section 4
- id: intermediate-checkpoints
  kind: result
  text: Fitting scaling laws to full training curves rather than to final losses alone substantially
    lowers prediction error, and relying only on the end of training produces significantly
    worse fits across model families.
  scope: OPT, GPT-3 and Pythia families, using checkpoint subsets defined by the fraction
    of training tokens retained; assumes the learning-rate schedule's effect on intermediate
    losses is negligible.
  evidence: Figure 4
- id: drop-early
  kind: result
  text: Discarding checkpoints from the first 10B training tokens cuts scaling-law error from
    above 15% to 4-10% for OPT and Pythia, because the earliest phase of training contains
    loss spikes and non-monotonic behaviour.
  scope: OPT and Pythia families; cutting fewer than 10B tokens gave noisier results and cutting
    more had negligible effect in preliminary experiments.
  evidence: Figure 5
- id: one-model
  kind: result
  text: With the model-size scaling parameters fixed to values from earlier published work,
    a single partially trained model in a new family can suffice. OLMo's 7B loss is predicted
    from 1B checkpoints with under 1% error.
  scope: Transformer families with model-size parameters borrowed from Muennighoff et al.
    (2024); fails for the encoder-decoder T5-Pile, and errors reach 37%, 25% and 15% for OPT
    predictions to 175B from 8.7B, 13B and 30B.
  evidence: Figure 6 (Appendix A)
- id: family-params-differ
  kind: result
  text: Estimated scaling-law parameters E, A, alpha, B and beta differ dramatically across
    model families, so the rate at which extra data or parameters help depends on architectural
    details.
  scope: The more than 40 scaled families in the released dataset, all fit with the Hoffmann
    et al. (2022) form; the differences are in fitted parameters, not the form.
  evidence: Figure 3
- id: partial-target
  kind: result
  text: Training the target model itself part-way is a viable substitute for training many
    small models, but reliable loss estimates require training it on roughly 30% of the full
    run.
  scope: Predicting within a single parameter-count family, so only the token term is extrapolated;
    shown on OPT, GPT-2, OLMo, Pythia variants and T5-Pile.
  evidence: Section 5.1
- id: baselines
  kind: result
  text: Simple no-fitting baselines that assume the target model is no better than the best
    small model incur more than 15% error and mostly above 10%. Across all scaled families
    studied they average 18% absolute relative error.
  scope: Two baselines, the best loss in the training set and the loss of the most-compute
    model, each given the full available family.
  evidence: Section 5.2
- id: more-small-models
  kind: result
  text: Increasing the number of preliminary models lowers scaling-law error even when the
    added models are not larger, and 5 models is a reasonable minimum for reliable predictions.
  scope: GPT-3, Gopher, OPT and Pythia families; the trend is not monotonic, since a single
    badly behaved model can dominate the fit.
  evidence: Figure 2(b), Figure 2(c)
- id: model-size
  kind: result
  text: Preliminary models closer in parameter count to the target give better fits, but the
    effect is neither strong nor monotonic. The 4 smallest models available already reach
    under 10% error for GPT-3, Gopher and OPT.
  scope: Predicting the largest model in each family; Pythia's smallest models are not predictive,
    and extrapolating 34x up in Pythia is still reliable when other factors are accounted
    for.
  evidence: Figure 2(a), Figure 2(c)
- id: cv-fails
  kind: result
  text: Cross-validation does not identify which preliminary models will corrupt a scaling-law
    fit. In 58% of cases, removing the model flagged as hard to predict produced the worst
    possible error on the actual target.
  scope: Leave-one-out over parameter-count families within each scaled family, using the
    highest-token models as targets; tested on the paper's collected families only.
  evidence: Appendix D
- id: degrees-of-freedom
  kind: result
  text: Scaling laws appear to have fewer degrees of freedom than their 5 fitted parameters
    suggest, with 3 principal components explaining 99.49% of the variance across fitted parameters.
    A is linearly related to alpha, and B to beta.
  scope: Across the fitted families in the released dataset; exceptions are the encoder-decoder
    T5-Pile and 4 families trained with multiple passes over one training set, which show
    a different B-beta relationship.
  evidence: Section 9, Figure 3
- id: scale-down
  kind: result
  text: Scaling laws also predict downward, fitting the loss of the smallest model in a family
    from the largest models. Good fits need at least 30-40% of training and enough models
    in the fitting set.
  scope: OPT, Pythia variants and T5-Pile; the percentage of training used for the fitting
    models is not reversed.
  evidence: Figure 8 (Appendix C)
qa:
- ask:
    plain: which paper should I read to learn how to predict how a language model will improve
      with more size and data?
    jargon: is there a study of scaling law estimation methodology, rather than another proposed
      functional form for one model family?
    task: where do I start if I need to fit a scaling law for my own pretraining runs and
      do not know how to choose the small models?
    practitioner: I am planning a pretraining budget and want guidance on scaling-law fitting
      practice, what should I read first?
  answered_by:
  - guide-context
  - dataset
- ask:
    plain: is there an open collection of training loss curves from many published language
      models?
    jargon: is there a released corpus of pretraining losses and downstream evaluations spanning
      many scaled model families and training steps?
    task: where can I get loss curves across model families so I can test scaling-law fitting
      procedures without pretraining anything myself?
    practitioner: can I reuse someone else's published loss curves instead of training models
      to study scaling behaviour?
  answered_by:
  - dataset
- ask:
    plain: when predicting how a big model will do, is it better to use only each small model's
      final loss or its whole training curve?
    jargon: do intermediate checkpoint losses improve scaling law fits relative to fitting
      final-loss points only?
    task: I logged loss every few thousand steps for my small runs, should I feed all of those
      points into the scaling-law fit or just the last one?
    practitioner: is it worth keeping and using all my intermediate checkpoints when fitting
      a scaling law, or can I just use the end of training?
  answered_by:
  - intermediate-checkpoints
  - drop-early
- ask:
    plain: do the very first stages of training mess up predictions of how a model will improve
      at larger scale?
    jargon: should early-training checkpoints be filtered out of a scaling law fit, and above
      what token count do fits stabilise?
    task: how do I decide which early checkpoints to drop from my loss curves before fitting
      a scaling law?
    practitioner: my early loss curve has spikes and weird jumps, should I exclude that part
      before fitting a scaling law?
  answered_by:
  - drop-early
- ask:
    plain: how precise does a prediction of a large model's loss have to be before it is actually
      useful for making decisions?
    jargon: what absolute relative error threshold does a scaling law need to discriminate
      between pretraining interventions given seed noise?
    task: how do I know whether my scaling-law prediction is accurate enough to choose between
      two pretraining recipes?
    practitioner: my scaling law is off by several percent, is that good enough to trust for
      a pretraining decision?
  answered_by:
  - target-accuracy
- ask:
    plain: can I borrow numbers from someone else's published scaling study instead of training
      a whole ladder of small models?
    jargon: can model-size scaling parameters be fixed from prior published fits so a single
      partially trained run suffices for a new family?
    task: I can only afford one small training run, how do I still get a loss prediction for
      the larger model I want to train?
    practitioner: do I really need to train five or six models of different sizes, or can
      one run plus published parameters do?
  answered_by:
  - one-model
  - family-params-differ
- ask:
    plain: do models with different architectures improve at different rates as you add data
      or parameters?
    jargon: do fitted scaling coefficients such as the data and parameter exponents vary across
      model families, or can a law be transferred unchanged?
    task: can I take a published scaling law from one model family and apply it to my own
      architecture without refitting?
    practitioner: my architecture differs from the one a published scaling law was fit on,
      should I refit it?
  answered_by:
  - family-params-differ
  - one-model
- ask:
    plain: can I just train the model I actually care about part of the way and guess where
      its loss ends up?
    jargon: how much of a target model's token budget must be completed before extrapolating
      its final pretraining loss is reliable?
    task: instead of a ladder of small models, how far into the target run do I need to go
      to predict its final loss?
    practitioner: should I spend my compute on several small models or on partially training
      the big model I want?
  answered_by:
  - partial-target
- ask:
    plain: how much worse is simply using the best small model's loss as a guess for a bigger
      model?
    jargon: what absolute relative error do no-fit baselines that assume the target is no
      better than the largest preliminary model incur?
    task: do I need to fit a curve at all, or can I just report the smallest-loss small model
      as an estimate for the large one?
    practitioner: is fitting a scaling law worth the effort compared with eyeballing my best
      small run?
  answered_by:
  - baselines
- ask:
    plain: is it better to train more small models or a few bigger ones when trying to predict
      a large model's loss?
    jargon: how many preliminary models does a reliable scaling law fit need, and does adding
      models help without increasing maximum size?
    task: I have a fixed compute budget for preliminary runs, how many models should I train
      before fitting a scaling law?
    practitioner: I have trained 3 small models so far, should I train more before trusting
      the extrapolation?
  answered_by:
  - more-small-models
  - model-size
- ask:
    plain: how big do the practice models need to be compared with the large model whose loss
      I want to predict?
    jargon: how much does the parameter-count gap between preliminary models and the target
      affect extrapolation error in a scaling law fit?
    task: how do I pick the sizes of the small models I train so the extrapolation to my target
      size holds up?
    practitioner: can I get away with only very small preliminary runs, or does my largest
      one need to be near the target size?
  answered_by:
  - model-size
  - more-small-models
- ask:
    plain: if one of my practice runs behaved strangely, can I find and remove it by holding
      models out one at a time?
    jargon: does leave-one-out cross-validation identify which preliminary models corrupt
      a scaling law fit?
    task: how do I detect which preliminary model is poisoning my scaling-law fit before I
      extrapolate?
    practitioner: one of my small models looks like an outlier, should I trust cross-validation
      to tell me whether to drop it?
  answered_by:
  - cv-fails
  - more-small-models
- ask:
    plain: are the numbers fitted in a scaling formula actually independent, or do some of
      them move together?
    jargon: how many effective degrees of freedom do the 5 fitted parameters of a Chinchilla-style
      scaling law have across families?
    task: can I reduce the number of free parameters I fit in a scaling law by exploiting
      relationships between them?
    practitioner: should I fit all 5 scaling-law parameters for my family, or constrain some
      of them?
  answered_by:
  - degrees-of-freedom
- ask:
    plain: can the same curve that predicts big models also predict a small one from the large
      ones?
    jargon: can a scaling law extrapolate downward, fitting the smallest model's loss in a
      family from the largest models?
    task: how do I estimate what a tiny version of my model would score without training it,
      given results from my larger runs?
    practitioner: I already trained large models, can I predict a small one's loss instead
      of running it?
  answered_by:
  - scale-down
terminology:
  scaled model family: A set of language models differing only in parameter count and number
    of training tokens, sharing architecture and training distribution; different checkpoints
    of one run and different seeds count as different models.
  absolute relative error (ARE): The mean over target models of the absolute difference between
    the true loss and the scaling-law-predicted loss, divided by the true loss.
  q-maximal token family: The subset of a scaled model family containing all models trained
    on at least a q fraction of the largest training run's tokens.
  scale-up factor: The ratio between the parameter count of the target model and that of the
    largest model used to fit the scaling law.
misreadings:
- 'Intermediate checkpoints improving scaling-law fits does not mean every checkpoint helps:
  checkpoints from the first 10B tokens are sometimes harmful and should be dropped.'
- Predicting a new family's target model from a single run works only because the model-size
  scaling parameters are borrowed from another family's published fit, not because one run
  identifies a full scaling law.
- 'Training a larger preliminary model does not reliably improve a scaling law: added large
  models can increase variance, and error across model sizes is not monotonic.'
- The recommendation of about 4% absolute relative error is a target set by what pretraining
  A/B tests report, not an accuracy the surveyed scaling laws routinely achieve.
---
