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

Then promote it:  python scripts/draft_sidecars.py --accept a-statistical-framework-for-game-based-ai-evaluation

Stamp: spec=551e6f04bf75 checks=pass body=cd2eabcb12b9
-->
---
one_liner: 'A statistical framework for game-based AI evaluation models each match twice:
  whether it ended prematurely, by timeout or two invalid moves, and who won if it did not.
  One low-dimensional skill vector per model links both parts, so reliability and proficiency
  are estimated together.'
claims:
- id: where-to-start-on-modelling-arena-outcomes
  kind: context
  text: For turning head-to-head game logs into per-model skill estimates rather than win
    rates, a two-part latent-skill model treats forfeits and completed games as linked parts
    of one likelihood. It belongs to the multidimensional item-response-theory tradition rather
    than the Elo one.
  scope: Two-player, turn-taking text games whose logs record why a match ended, not single-player
    benchmarks and not pairwise preference votes without a game state. One dataset, no Bradley-Terry
    or Elo baseline, and no held-out predictive evaluation.
- id: forfeits-carry-skill-rather-than-noise
  kind: context
  text: Timeouts and invalid moves in game-based LLM evaluation are modelled as typed outcomes
    that carry skill information rather than being discarded or folded into a loss. A win-rate
    summary does the latter and loses that signal.
  scope: Arenas whose logs record why a match ended. Nothing measures what a leaderboard loses
    by discarding forfeits, so the standing of the choice is argument rather than evidence.
- id: two-part-model-with-a-shared-skill-space
  text: One per-model skill vector explains both how a match ended and who won it, so a forfeit
    and a loss are scored on the same scale instead of one being discarded. Coupling a model
    of termination to a paired-comparison model of the winner through that vector is what allows
    it.
  scope: 'TextArena''s termination types: either player timing out, either player making two
    invalid moves in a row, or a valid game as the reference class.'
  evidence: Sections 3.1 and 3.2
- id: skill-enters-both-parts-linearly
  kind: result
  text: A model can be reliable on one game and unreliable on another, because reliability
    is carried by per-game loading vectors rather than by one global trait. Skill enters the
    termination model and the win model linearly through those loadings.
  scope: Every fit of the model as specified. No per-game loading vector is reported, so this
    is what the parameterisation allows and not a measured difference between games.
  evidence: Sections 3.1 and 3.2
- id: four-latent-dimensions-on-textarena
  text: A 4-dimensional skill space was selected for the TextArena fit over 57 models and
    22 game types, chosen by validation loss on a held-out subset of the matches.
  scope: One dataset and one selection run; the held-out size, the grid of dimensionalities
    compared and the loss values are unreported.
  evidence: Data analysis
- id: rotation-turns-loadings-into-two-reliability-axes
  text: After a geomin rotation of the fitted skill space, one dimension aligns with avoiding
    timeouts and a second with avoiding invalid moves. Both readings come off loadings averaged
    over the 22 game types.
  scope: Mean loadings, with standard deviations across games and no test that the two axes
    separate. A different rotation criterion gives different axes over the same fit.
  evidence: Figure 2, Data analysis
- id: identifiable-only-up-to-a-rotation
  text: Centering and whitening the skills across models removes the translation and scale
    indeterminacies, but the likelihood is invariant to any common orthogonal rotation of
    the skill space. The parameters are therefore identifiable only up to a rotation.
  scope: Any fit of this model, as in factor analysis and multidimensional item-response theory.
    Fit and predictive performance are unchanged by the rotation, and quantities that depend
    only on inner products, such as profile similarities, are unaffected.
  evidence: Section 3.3
- id: skill-profiles-place-a-model-next-to-its-own-distillations
  text: Cosine similarity between fitted skill profiles puts deepseek-r1 closest to its own
    llama-70b and llama-8b distillations and to o1, out of the 57 models fitted. Profiles
    track lineage and reasoning style rather than raw strength.
  scope: One reference model, read off a figure of similarities normalised to a 0-to-1 range,
    so the values order the other models and carry no absolute meaning.
  evidence: Figure 1, Data analysis
- id: the-games-instruction-skill-tracks-math-more-than-ifeval
  text: The TextArena complex-instruction-following skill correlates more strongly with a
    skill estimated from MATH than with one estimated from IFEval. Both benchmark skills come
    from one-dimensional item-response-theory fits over the same 57 models.
  scope: Pearson correlations shown in a figure, with no coefficients or intervals in the
    text, so the comparison is a direction and not a magnitude. Translation invariance leaves
    the sign of any one correlation uninterpretable.
  evidence: Figure 3, Data analysis
- id: position-bias-and-draws-are-separate-parameters
  text: 'Moving first is modelled twice and separately: one per-game, per-failure-type term
    shifts the odds of ending a match prematurely, another per-game term the odds of winning
    a valid game. A separate non-negative draw margin controls how often valid games end drawn.'
  scope: Every game in the fit carries its own bias terms, none of them reported as a fitted
    quantity, so what is shown is that the two effects are separable and not how large either
    is.
  evidence: Section 3.1, Section 3.2
- id: fitted-on-57-models-and-22-game-types
  text: 'The fit uses the public TextArena trace dataset: 57 language models, 30 game types
    and roughly 38k recorded matches. Dropping game types with fewer than 50 valid matches
    leaves 22 game modalities.'
  scope: Maximum-likelihood point estimates, with no error bars on the fitted skills. Some
    traces involve human players, and whether those entered the fit is not stated.
  evidence: Data analysis, Appendix A
qa:
- q:
  - What should I read about evaluating language models with games?
  - Is there a principled way to turn game or arena results into model skill estimates?
  - How do I go beyond win rates when comparing LLMs that play each other?
  answers:
  - where-to-start-on-modelling-arena-outcomes
  - forfeits-carry-skill-rather-than-noise
  - two-part-model-with-a-shared-skill-space
  - skill-enters-both-parts-linearly
- q:
  - How should a leaderboard handle timeouts and invalid moves?
  - What do I do with matches an LLM forfeited by producing an illegal move?
  - Should failed or malformed games be thrown out of an arena ranking?
  answers:
  - forfeits-carry-skill-rather-than-noise
  - two-part-model-with-a-shared-skill-space
  - fitted-on-57-models-and-22-game-types
- q:
  - How do I model wins, draws and losses in the same fit?
  - Is there a Bradley-Terry variant that handles draws and a first-move advantage?
  - How do I account for who moves first when comparing two models?
  answers:
  - position-bias-and-draws-are-separate-parameters
  - two-part-model-with-a-shared-skill-space
  - skill-enters-both-parts-linearly
- q:
  - Do language models share latent skills across different games?
  - How many dimensions does it take to explain arena performance?
  - Is performance across games correlated enough to be summarised by a few factors?
  answers:
  - four-latent-dimensions-on-textarena
  - rotation-turns-loadings-into-two-reliability-axes
- q:
  - Which language models behave most similarly when they play games?
  - Can I compare two models by their skill profile rather than their score?
  - Do distilled models keep the skill profile of the model they came from?
  answers:
  - skill-profiles-place-a-model-next-to-its-own-distillations
  - identifiable-only-up-to-a-rotation
- q:
  - Does how a model plays games tell you anything about its maths ability?
  - Do game-based skills correlate with standard benchmarks like MATH or IFEval?
  - Is instruction following in games the same thing IFEval measures?
  answers:
  - the-games-instruction-skill-tracks-math-more-than-ifeval
  - rotation-turns-loadings-into-two-reliability-axes
- q:
  - Can I interpret the individual dimensions of a latent skill model?
  - Why does a factor model need a rotation before its axes mean anything?
  - Are the skill dimensions estimated from game outcomes identified?
  answers:
  - identifiable-only-up-to-a-rotation
  - rotation-turns-loadings-into-two-reliability-axes
- q:
  - How much data does it take to fit a latent-skill model of game outcomes?
  - Which games and how many matches were used?
  - Was the latent-skill framework validated on more than one arena dataset?
  answers:
  - fitted-on-57-models-and-22-game-types
  - four-latent-dimensions-on-textarena
- q:
  - How are latent skill vectors estimated from game outcomes?
  - Are latent-skill models of arena outcomes fit by maximum likelihood or Bayesian inference?
  answers:
  - two-part-model-with-a-shared-skill-space
  - fitted-on-57-models-and-22-game-types
- q:
  - Can I rank models by how reliably they follow instructions in games?
  - Is there a measure of model reliability separate from how often it wins?
  answers:
  - rotation-turns-loadings-into-two-reliability-axes
  - forfeits-carry-skill-rather-than-noise
  - identifiable-only-up-to-a-rotation
misreadings:
- The named skills are labels attached to axes after a rotation, not measured constructs.
  The likelihood is invariant to a common rotation of the skill space, so "Skill 1 is instruction
  following" is a statement about the geomin rotation the authors chose; a different criterion
  relabels the same fit.
- 'The correlation result does not say that game-based instruction following matches IFEval.
  It says the opposite ordering: the games-derived skill correlates more strongly with a MATH-derived
  skill than with an IFEval-derived one.'
- Only 2 of the 4 fitted dimensions are given interpretations. The other 2 are estimated but
  unlabelled, so a 4-dimensional skill space is not the same thing as 4 named skills.
- No coefficients, confidence intervals or significance tests are reported for the similarity
  and correlation results -- they are figures in a preliminary workshop paper, and the similarity
  figure is normalised so its maximum is 1 and its minimum 0, which makes the values an ordering
  rather than a measurement.
- The model is not compared against Bradley-Terry, Elo or per-game win rates. No baseline
  comparison and no held-out predictive evaluation is reported, so the claim being supported
  is that the framework yields interpretable skills, not that it predicts outcomes better.
- Filtering to game types with at least 50 valid matches drops game types where most matches
  ended prematurely -- exactly the outcomes the framework is built to model. The 22 modalities
  analysed are the ones that survived that filter, not the 30 the dataset contains.
- The dataset contains matches involving human players, and the paper does not state whether
  they were used in the fit. Nothing in the fitted skills should be read as a human-versus-model
  comparison.
- Two invalid moves in a row end the match under the dataset's two-strike rule; a single invalid
  move does not. The reliability dimension is estimated from those terminations, not from
  a count of every malformed output.
terminology:
  premature termination: A match that ended before a win, draw or loss -- by a player timing
    out or by committing two invalid moves in a row. The framework models it as a typed outcome
    of its own rather than as a loss or a discarded record.
  two-strike rule: The dataset's convention that two consecutive invalid moves by the same
    player end the match. It is the event the reliability side of the model is fitted to.
  draw margin: A non-negative per-game parameter controlling how much of the skill-difference
    scale is absorbed by draws; larger values make draws more likely in that game.
  skill profile: The full vector of a model's latent skills, as opposed to a single score.
    Similarity between profiles is compared by cosine, which depends only on inner products
    and so survives the model's rotational non-identifiability.
  geomin rotation: A post-fitting rotation criterion borrowed from factor analysis, applied
    to make individual skill dimensions describable. It changes neither the fit nor the predictions.
  loadings: The per-game vectors that say which skills a game draws on -- one set for the
    valid-play outcome and one per failure type for premature endings. A game's loadings are
    what let one shared skill vector behave differently across games.
  reliability: In game-based evaluation, the ability to avoid timeouts and invalid moves and
    so keep a match valid. Kept separate from proficiency, the ability to win matches that
    stay valid.
---
