<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API (schema-enforced via a forced tool call) + 1 repair round. Every claim, number
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

Stamp: spec=d57862840a90 checks=2 body=4b7b151f29f5
-->
---
claims:
- id: four-dims
  kind: result
  text: Validation loss on a held-out subset of the TextArena arena data selects 4 latent
    skill dimensions as sufficient to describe 57 language models across 22 filtered game
    modalities, out of 30 game types and roughly 38k matches.
  scope: TextArena matches only, filtered to games with at least 50 valid matches; some matches
    involve human players. Dimension chosen by held-out validation loss, not a formal selection
    test.
  evidence: Section 4
- id: reliability-axes
  kind: result
  text: After geomin rotation of the TextArena skill space, one of the 4 latent dimensions
    aligns with avoiding timeouts and a separate dimension aligns with avoiding invalid moves.
    Failure-avoidance is therefore two distinct model abilities, not one.
  scope: Rotated loadings averaged across the 22 retained TextArena games, with across-game
    standard deviations; the rotation is chosen for interpretability and leaves fit and predictions
    unchanged.
  evidence: Figure 2
- id: math-vs-ifeval
  kind: result
  text: The TextArena latent skill labelled complex instruction following correlates more
    strongly (Pearson) with a one-dimensional IRT skill fitted to MATH than with one fitted
    to IFEval, over the same 57 models.
  scope: MATH and IFEval scores for the 57 TextArena models; correlation signs are uninterpretable
    because the skill model is invariant to translation, and magnitudes are shown graphically.
  evidence: Figure 3
- id: skill-profile-similarity
  kind: result
  text: Cosine similarity between fitted skill vectors places deepseek-r1 closest to deepseek-r1-distill-llama-70b,
    deepseek-r1-distill-llama-8b and OpenAI's o1, so arena outcomes alone recover model-family
    and reasoning-style structure.
  scope: Similarities normalized across the 57 TextArena models so the highest is 1 and the
    lowest is 0, hence relative rather than absolute; preliminary fits to roughly 38k matches.
  evidence: Figure 1
- id: ranking-by-instruction-following
  kind: result
  text: The 57 TextArena models can be ranked on a single interpretable axis of ability to
    avoid invalid moves and follow complex instructions, separately from any win-rate ranking.
  scope: Rotated Skill 1 of the 4-dimensional fit; the axis interpretation depends on the
    geomin rotation, and the ordering appears as a figure.
  evidence: Figure 4
- id: game-loadings
  kind: result
  text: Fitted per-game valid-play loadings show that the 22 retained TextArena games load
    unequally on the 4 latent skills, so different games are informative about different abilities.
  scope: TextArena games retained after the 50-valid-match filter; the pattern is reported
    qualitatively, with more insightful interpretation of the loadings left as future work.
  evidence: Figure 5
- id: identifiability
  kind: result
  text: The game-based skill model is identifiable only up to a common orthogonal rotation
    of the latent skill space once skills are centered and whitened across models. All probabilities
    depend on the parameters through inner products alone.
  scope: The framework's own parameterization with d latent skills; centering and whitening
    remove translation and scale indeterminacy but not rotation, as in factor analysis and
    multidimensional IRT.
  evidence: Section 3.3
- id: two-part-model
  kind: context
  text: 'The statistical framework for game-based AI evaluation models a match in two linked
    parts: whether it ended prematurely by timeout or two consecutive invalid moves, and otherwise
    whether it was a win, draw or loss. Both parts share one low-dimensional skill space.'
  scope: Two-player text games with timeouts and a two-strike invalid-move rule, as instantiated
    on TextArena; fitted by maximum likelihood, with preliminary analyses rather than a broad
    benchmark study.
  evidence: Section 3
- id: failures-as-signal
  kind: context
  text: Treating timeouts and invalid moves as measurable reliability skills rather than as
    discarded noise is the framework's departure from win-rate and per-game leaderboard summaries
    of LLM arena play.
  scope: As of the 2025 NeurIPS LLM Evaluation Workshop paper; the comparison is to Bradley-Terry
    and latent-skill summaries of completed matches, not a head-to-head accuracy benchmark.
  evidence: Section 2
- id: entry-point
  kind: context
  text: A statistical framework for game-based AI evaluation connects multidimensional item
    response theory and Bradley-Terry paired comparison to interactive LLM evaluation. It
    is a starting point for readers moving from static benchmarks to arena-style multi-turn
    testing.
  scope: A workshop-length paper with preliminary results on one dataset (TextArena); positioned
    relative to Bradley-Terry extensions and latent-skill studies of LLM benchmarks, not to
    game-playing agent literature more broadly.
qa:
- q:
  - How can win rates, timeouts and invalid moves in an LLM game arena be modelled together?
  - Is there a statistical model that treats forfeits and wins separately in two-player LLM
    games?
  - How do you turn arena match records into interpretable model skills?
  answers:
  - two-part-model
  - failures-as-signal
- q:
  - How many latent skill dimensions are needed to explain LLM game outcomes?
  - What dimensionality was chosen for the TextArena skill space?
  - How many factors fit 57 models across 30 text games?
  answers:
  - four-dims
- q:
  - Are timeouts and invalid moves the same underlying model weakness?
  - Does avoiding timeouts require the same skill as avoiding illegal moves?
  - What do the rotated skill axes in TextArena mean?
  answers:
  - reliability-axes
- q:
  - Does game-playing instruction following predict math ability?
  - How do TextArena latent skills relate to MATH and IFEval scores?
  - Do arena skills correlate with established LLM benchmarks?
  answers:
  - math-vs-ifeval
- q:
  - Can I compare two LLMs by their skill profile instead of a single score?
  - Which models are most similar to deepseek-r1 in game-play behaviour?
  - How is similarity between LLM skill vectors measured in TextArena?
  answers:
  - skill-profile-similarity
- q:
  - Can models be ranked by how reliably they follow complex instructions in games?
  - Is there a leaderboard of LLMs by ability to avoid invalid moves?
  answers:
  - ranking-by-instruction-following
- q:
  - Do all text games measure the same LLM abilities?
  - Which games are informative about which latent skills?
  answers:
  - game-loadings
- q:
  - Are the latent skill parameters in a game-based IRT model uniquely determined?
  - Why is a rotation applied after fitting a multidimensional skill model of arena outcomes?
  - Does the choice of rotation change predictive accuracy of a latent skill game model?
  answers:
  - identifiability
- q:
  - What should I read first about statistical evaluation of LLMs in games or arenas?
  - Which work connects item response theory to interactive multi-turn LLM evaluation?
  - Where does research on latent skills of language models meet Bradley-Terry match modelling?
  answers:
  - entry-point
  - failures-as-signal
one_liner: A statistical framework for game-based AI evaluation splits each two-player match
  into premature ending (timeout or two invalid moves) and win/draw/loss, tying both to a
  shared low-dimensional skill space so LLM reliability and proficiency are estimated separately
  from arena data.
terminology:
  premature ending: A two-player game that stops before a valid conclusion, either because
    a player timed out or because a player made two invalid moves in a row under a two-strike
    rule.
  reliability (in game-based LLM evaluation): A model's ability to avoid timeouts and invalid
    moves, estimated separately from its ability to win games that reach a valid conclusion.
  proficiency (in game-based LLM evaluation): A model's ability to win rather than draw or
    lose in games that reach a valid conclusion, conditional on no premature ending.
  draw margin: A non-negative per-game parameter in the paired-comparison outcome model; larger
    values make draws more likely for a given skill difference between the two players.
  skill profile: The fitted latent skill vector of a language model in a multidimensional
    game-outcome model, comparable across models by cosine similarity.
misreadings:
- 'The latent skill dimensions are not fixed, canonical abilities: the model is identifiable
  only up to an orthogonal rotation of the skill space, so labels such as ''avoiding timeouts''
  or ''instruction following'' depend on the geomin rotation chosen after fitting.'
- The sign of the reported correlations between TextArena skills and MATH or IFEval skills
  carries no meaning, because the skill model is invariant to translation; only the relative
  strength of alignment should be read.
- The stronger correlation with MATH than with IFEval does not show that IFEval is a poor
  instruction-following benchmark; it indicates that the game-derived skill labelled complex
  instruction following also carries reasoning ability beyond what IFEval targets.
- The reported TextArena analysis is preliminary and covers 22 game modalities after filtering
  out games with fewer than 50 valid matches, so it is not an evaluation of all 30 TextArena
  game types.
- 'Ranking models by the rotated instruction-following skill is not a win-rate ranking: it
  measures avoidance of invalid moves, which the framework estimates separately from performance
  in games that conclude validly.'
---
