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

Then promote it:  python scripts/draft_sidecars.py --accept a-hitchhiker-s-guide-to-scaling-law-estimation

Stamp: spec=8f05813a4658 checks=pass body=8ae296b180f6
-->
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
- q:
  - What is a good paper to read on how to estimate scaling laws for language models?
  - Where should I start if I want to learn how to fit a scaling law for a new model family?
  - Is there work studying scaling law estimation practice rather than proposing a new scaling
    law?
  answers:
  - guide-context
  - dataset
- q:
  - Is there a public dataset of pretraining loss curves across many model families?
  - Where can I get training losses and checkpoints for many published LLMs?
  - How much data was used to study scaling law estimation across families?
  answers:
  - dataset
- q:
  - Should scaling laws be fit only to final losses, or also to intermediate checkpoints?
  - Does using checkpoints from the middle of training improve scaling law accuracy?
  - Is it wasteful to throw away intermediate training losses when fitting a scaling law?
  answers:
  - intermediate-checkpoints
  - drop-early
- q:
  - Are early training checkpoints harmful when fitting a scaling law?
  - How many initial tokens of training should be discarded before fitting a scaling law?
  - Why do the first billions of training tokens hurt scaling law fits?
  answers:
  - drop-early
- q:
  - How accurate does a scaling law prediction need to be to be useful?
  - What error level makes a scaling law good enough to compare pretraining decisions?
  - How much loss difference do published pretraining A/B tests actually report?
  answers:
  - target-accuracy
- q:
  - Can I predict a large model's loss from just one smaller model?
  - Is it possible to reuse scaling parameters from another model family?
  - Do I need to train a whole ladder of models, or can a single run suffice?
  answers:
  - one-model
  - family-params-differ
- q:
  - Do different model families have different scaling law parameters?
  - Does architecture change the exponents in a scaling law?
  - Can a scaling law be transferred between architectures unchanged?
  answers:
  - family-params-differ
  - one-model
- q:
  - Is it better to train the target model partially instead of training many small models?
  - How much of the full training run of a target LLM is needed to extrapolate its final loss?
  - Can I stop a big pretraining run early and predict where the loss will land?
  answers:
  - partial-target
- q:
  - How much better is fitting a scaling law than just taking the best small model's loss?
  - Are naive baselines enough instead of fitting a scaling law?
  - What error do no-fit baselines get when predicting a large model's loss?
  answers:
  - baselines
- q:
  - Is it better to train more small models or one big model for a scaling law?
  - How many preliminary models are needed for a reliable scaling law?
  - Does adding more models help scaling law accuracy even if they are small?
  answers:
  - more-small-models
  - model-size
- q:
  - How large should the biggest preliminary model be when fitting a scaling law?
  - Does using models closer in size to the target improve extrapolation?
  - How far up in parameter count can a scaling law extrapolate reliably?
  answers:
  - model-size
  - more-small-models
- q:
  - Can I detect which preliminary models are bad to fit a scaling law on?
  - Does cross-validation help remove outlier models from a scaling law fit?
  - Why is scaling law estimation noisy when one model behaves badly?
  answers:
  - cv-fails
  - more-small-models
- q:
  - Does the Chinchilla scaling law form have redundant parameters?
  - How many independent degrees of freedom do fitted scaling law parameters actually have?
  - Are the parameter and token scaling coefficients correlated across model families?
  answers:
  - degrees-of-freedom
- q:
  - Can scaling laws extrapolate downward to smaller models?
  - Does predicting a small model's loss from larger models work?
  - How much training is needed to fit a scaling law that scales down?
  answers:
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
