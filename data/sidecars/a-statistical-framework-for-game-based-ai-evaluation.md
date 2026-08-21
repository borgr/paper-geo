---
claims:
- id: reliability-vs-proficiency
  kind: context
  text: The statistical framework for game-based AI evaluation separates a model's reliability
    (avoiding timeouts and invalid moves) from its proficiency (winning games that reach a
    valid conclusion). Neither is folded into a single win rate or per-game rank.
  scope: Two-player text games with a win/draw/loss outcome and a two-strike invalid-move
    rule; demonstrated only on TextArena data as of the 2025 workshop version, which reports
    preliminary results.
- id: invalid-moves-as-signal
  kind: context
  text: Treating timeouts and repeated invalid moves as informative outcomes rather than discarded
    matches turns arena failure data into a measure of whether a model follows formats and
    instructions reliably.
  scope: Arenas that log why a match ended; the argument is about arena leaderboards summarising
    outcomes as raw win rates or independent per-game ranks.
- id: four-dimensions
  kind: result
  text: Validation loss on a small held-out subset of the roughly 38k TextArena matches indicated
    that d = 4 latent skill dimensions is the optimal choice for the game-outcome model.
  evidence: Section 4
  scope: TextArena traces after filtering to game modalities with at least 50 valid matches;
    a single held-out validation split, no dimension-selection sweep reported.
- id: dataset-scale
  kind: result
  text: The framework is fit to the public TextArena traces covering 57 language models, 30
    game types and roughly 38k recorded matches, including some matches against human players.
    Filtering to games with at least 50 valid matches leaves 22 game modalities.
  evidence: Section 4
  scope: One dataset, one snapshot of the TextArena HuggingFace release; games with fewer
    than 50 valid matches are excluded from the fit.
- id: skill-profile-similarity
  kind: result
  text: Cosine similarity between fitted 4-dimensional latent skill profiles, normalized so
    the highest similarity is 1 and the lowest 0, places deepseek-r1 closest to deepseek-r1-distill-llama-70b,
    deepseek-r1-distill-llama-8b and OpenAI's o1.
  evidence: Figure 1
  scope: Similarities are normalized across the 57 TextArena models so the highest is 1 and
    the lowest 0, so they are relative, not absolute; fit to the filtered TextArena matches.
- id: geomin-interpretable-axes
  kind: result
  text: After a geomin rotation of the fitted 4-dimensional skill space, "Skill 0" is strongly
    associated with avoiding timeouts and "Skill 1" with avoiding invalid moves, i.e. following
    complex instructions correctly.
  evidence: Figure 2
  scope: Rotation chosen on the premature-termination loadings averaged across the 22 retained
    TextArena games; the labels are the authors' post hoc reading of the loadings.
- id: rotation-invariance
  kind: result
  text: The latent skills in the game-outcome model are identifiable only up to a common orthogonal
    rotation of the 4-dimensional skill space. Choosing a rotation changes neither model fit
    nor predictive performance, only how interpretable the axes are.
  evidence: Section 3.3
  scope: After centering and whitening the skills across models, which removes the translation
    and scale indeterminacies; the residual rotational non-identifiability is the standard
    one in factor analysis and multidimensional IRT.
- id: math-vs-ifeval
  kind: result
  text: The TextArena complex instruction-following skill, estimated for 57 models, correlates
    more strongly (Pearson) with a one-dimensional IRT skill fit to MATH than with one fit
    to IFEval. The games-based skill therefore tracks mathematical reasoning more than narrow
    instruction following.
  evidence: Figure 3
  scope: The same 57 models on all three fits; correlation signs are not meaningful because
    the model is translation-invariant, so only relative alignment is interpretable. MATH
    and IFEval only.
- id: model-ranking
  kind: result
  text: The fitted framework ranks the 57 TextArena models by instruction-following skill,
    the rotated "Skill 1" axis, where a higher score means a stronger ability to avoid invalid
    moves and follow complex instructions.
  evidence: Figure 4
  scope: Ranking reflects reliability in games rather than overall win rate; based on the
    fit to the 22 retained TextArena game modalities.
- id: game-loadings
  kind: result
  text: Fitted per-game valid-play loadings show that the 22 retained TextArena games differ
    in which of the 4 latent skills govern win/draw/loss outcomes, so no single skill dimension
    explains performance across all games.
  evidence: Figure 5
  scope: TextArena traces only; the loadings are reported without a quantitative interpretation,
    which the paper flags as future work.
- id: position-bias
  kind: result
  text: The framework includes explicit first-mover position-bias terms in both the premature-termination
    component and the win/draw/loss component, plus a per-game draw margin, so first-move
    advantage is estimated rather than assumed away.
  evidence: Section 3.2
  scope: Two-player games with a defined first mover; these parameters are specified and fit
    by maximum likelihood, but their estimated magnitudes are not reported.
one_liner: A statistical framework for game-based LLM evaluation that splits each match into
  whether it ended prematurely (timeout or two invalid moves in a row) and, if valid, into
  win/draw/loss, with both parts sharing one low-dimensional latent skill space for models
  and games.
qa:
- ask:
    plain: is there research on scoring language models by how often they crash or break the
      rules of a game, not just who wins?
    jargon: what statistical framework separates reliability (timeouts, illegal moves) from
      proficiency (win/draw/loss) in LLM two-player game evaluation?
    task: how do I turn logged game matches with timeouts and rule violations into an evaluation
      signal instead of dropping those matches?
    practitioner: should I keep the forfeited and timed-out matches in my model-vs-model game
      evaluation?
  answered_by:
  - reliability-vs-proficiency
  - invalid-moves-as-signal
- ask:
    plain: how many separate abilities do you need to explain who wins language-model games?
    jargon: how was the latent dimensionality d selected for the multidimensional TextArena
      game-outcome model?
    task: how do I pick the number of latent skill factors when fitting a game-outcome model
      to match records?
    practitioner: if I fit a latent skill model to my own match logs, how many dimensions
      should I start with?
  answered_by:
  - four-dimensions
- ask:
    plain: how many models and recorded games went into fitting the skill model of language-model
      matches?
    jargon: what is the scale of the TextArena trace corpus used to fit the multidimensional
      game-outcome model, and what match-count filter is applied per game?
    task: how much match data do I need before a latent skill model of LLM games can be fit?
    practitioner: can I rely on existing public TextArena traces instead of running thousands
      of my own matches?
  answered_by:
  - dataset-scale
- ask:
    plain: which language models play games in the most similar way to deepseek-r1?
    jargon: which models have the closest cosine similarity in fitted 4-dimensional latent
      skill space to deepseek-r1?
    task: how do I find which models are behavioural near-neighbours of a given model using
      only game match records?
    practitioner: can I use game-derived skill profiles to pick a cheaper stand-in for deepseek-r1?
  answered_by:
  - skill-profile-similarity
- ask:
    plain: do the hidden abilities found from game results correspond to anything a person
      can name?
    jargon: after geomin rotation, what do the axes of the 4-dimensional latent skill space
      correspond to, and does rotation affect model fit?
    task: how do I make latent factors from game outcomes interpretable as timeout-avoidance
      and rule-following?
    practitioner: if I fit factors to my match data, can I actually read off which axis means
      following instructions?
  answered_by:
  - geomin-interpretable-axes
  - rotation-invariance
- ask:
    plain: if a model of game results uses several hidden abilities, are those abilities pinned
      down uniquely?
    jargon: are latent skills in a multidimensional game-outcome model identified only up
      to an orthogonal rotation, and does the rotation change predictive performance?
    task: how should I handle rotational indeterminacy when reporting latent skill scores
      estimated from match outcomes?
  answered_by:
  - rotation-invariance
- ask:
    plain: does being good at following game rules go together with being good at math?
    jargon: how does the TextArena-derived complex instruction-following skill correlate with
      unidimensional IRT abilities fit to MATH versus IFEval?
    task: how do I check whether a skill estimated from game play tracks a math benchmark
      or an instruction-following benchmark?
    practitioner: can I use game-based scores as a proxy for math benchmark performance instead
      of running MATH?
  answered_by:
  - math-vs-ifeval
- ask:
    plain: can you rank language models by how reliably they follow complicated instructions,
      using only game results?
    jargon: what does the rotated Skill 1 axis rank the 57 TextArena models on, and how does
      it relate to invalid-move avoidance?
    task: how do I rank models by instruction-following reliability rather than by raw win
      rate?
    practitioner: which model should I pick if I care most about it not emitting malformed
      or illegal actions?
  answered_by:
  - model-ranking
  - geomin-interpretable-axes
- ask:
    plain: do different text games test different abilities, or is one general ability enough?
    jargon: what do the fitted per-game valid-play loadings show about which latent dimensions
      govern win/draw/loss outcomes across games?
    task: how do I tell which games in a suite probe which latent skill before choosing an
      evaluation set?
    practitioner: can I evaluate a model on one game and assume the ranking carries over to
      the rest?
  answered_by:
  - game-loadings
- ask:
    plain: does going first give an advantage in language-model games, and is that taken into
      account?
    jargon: are first-mover position-bias terms and a per-game draw margin estimated in the
      premature-termination and win/draw/loss components?
    task: how do I control for who moved first when estimating model skill from two-player
      match records?
    practitioner: do I need to alternate which model moves first, or can the model correct
      for it?
  answered_by:
  - position-bias
terminology:
  Two-strike rule: A match-ending condition in which a player forfeits after committing two
    invalid moves in a row.
  Premature ending: A game that never reaches a win, draw or loss because it ended by timeout
    or by a player's two consecutive invalid moves.
  Reliability (in game-based LLM evaluation): A model's ability to avoid premature endings
    — timeouts and repeated invalid moves — as distinct from its ability to win games that
    reach a valid conclusion.
  Proficiency (in game-based LLM evaluation): A model's ability to win games conditional on
    the match reaching a valid win/draw/loss conclusion.
  Draw margin: A per-game non-negative parameter in the paired-comparison outcome model whose
    size controls how often matches end in a draw.
  Geomin rotation: A factor-analysis criterion for choosing among the equivalent rotations
    of a latent skill space so that dimensions align with interpretable axes.
misreadings:
- 'The correlation between the TextArena instruction-following skill and MATH skill does not
  have a meaningful sign: the model is invariant to translations of the skills, so only the
  relative alignment between benchmarks is interpretable.'
- A high score on the rotated "Skill 1" axis means a model rarely makes invalid moves, not
  that it wins more games; winning valid games is governed by the separate valid-play component
  and its per-game loadings.
- Naming the rotated dimensions "avoiding timeouts" and "avoiding invalid moves" is a post
  hoc reading of the fitted loadings, not a constraint imposed on the model before fitting.
- 'The reported results are preliminary analyses on a single TextArena snapshot, not a validated
  leaderboard replacement: no out-of-sample ranking accuracy or predictive benchmark against
  Bradley-Terry baselines is reported.'
- The 22 game modalities analysed are a filtered subset of TextArena's 30 game types, since
  games with fewer than 50 valid matches were dropped.
key: maiapolo2025gamebased
links_extra:
  dataset: https://huggingface.co/datasets/the-acorn-ai/textarena-player-game-traces
---
