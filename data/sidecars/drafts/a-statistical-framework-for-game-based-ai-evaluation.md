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

Then promote it:  python scripts/draft_sidecars.py --accept a-statistical-framework-for-game-based-ai-evaluation

Stamp: spec=74e012ff9654 checks=1 body=2dc9f05f3efa
-->
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
  text: Validation loss on a small held-out subset of the TextArena matches indicated that
    d = 4 latent skill dimensions is the optimal choice for the game-outcome model.
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
  text: Cosine similarity between fitted 4-dimensional latent skill profiles places deepseek-r1
    closest to deepseek-r1-distill-llama-70b, deepseek-r1-distill-llama-8b and OpenAI's o1,
    indicating these models behave most alike in play.
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
  text: The TextArena complex instruction-following skill correlates more strongly (Pearson)
    with a one-dimensional IRT skill fit to MATH than with one fit to IFEval. The games-based
    skill therefore tracks mathematical reasoning more than narrow instruction following.
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
- q:
  - What should I read about turning game or arena outcomes into interpretable model skills?
  - Is there work on statistical models of LLM performance in two-player games?
  - How can invalid moves and timeouts be used in LLM evaluation instead of being thrown away?
  answers:
  - reliability-vs-proficiency
  - invalid-moves-as-signal
- q:
  - How many latent dimensions are needed to model LLM game outcomes?
  - How was the number of skill dimensions chosen in the TextArena skill model?
  - What skill-space dimensionality did the game-based LLM evaluation framework select?
  answers:
  - four-dimensions
- q:
  - How much data does it take to fit a latent-skill model of arena outcomes?
  - How large is the TextArena dataset used for game-based LLM evaluation?
  - How many models, games and matches are in the TextArena traces?
  answers:
  - dataset-scale
- q:
  - Can I compare two LLMs by their skill profile?
  - Which models are most similar to deepseek-r1 in game-playing behaviour?
  - How do you measure similarity between LLMs' latent skills from match data?
  answers:
  - skill-profile-similarity
- q:
  - Do the latent skills learned from game outcomes mean anything interpretable?
  - What do rotated skill dimensions in the TextArena model correspond to?
  - Can a factor rotation separate avoiding timeouts from avoiding invalid moves?
  answers:
  - geomin-interpretable-axes
  - rotation-invariance
- q:
  - Are the latent skills in a multidimensional game model uniquely identified?
  - Does rotating the skill space change predictions or fit quality?
  - What identifiability problems affect latent skill models of match outcomes?
  answers:
  - rotation-invariance
- q:
  - Does instruction-following skill in games predict math benchmark performance?
  - How do TextArena-derived skills correlate with MATH and IFEval?
  - Can game-based evaluation predict performance on mathematical problem solving?
  answers:
  - math-vs-ifeval
- q:
  - Can a game-based evaluation framework rank LLMs by how well they follow complex instructions?
  - How do you rank models by reliability rather than win rate?
  - What does the instruction-following ranking from TextArena outcomes measure?
  answers:
  - model-ranking
  - geomin-interpretable-axes
- q:
  - Does one skill explain LLM performance across all text games?
  - Do different games depend on different latent skills?
  - What do the per-game loadings in the TextArena game-outcome model show?
  answers:
  - game-loadings
- q:
  - Does the TextArena game-outcome model account for first-mover advantage in two-player
    games?
  - How are draws and position bias handled when modelling LLM matches?
  - Is the advantage of moving first estimated in game-based LLM evaluation?
  answers:
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
