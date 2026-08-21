---
one_liner: TextArena is an open-source, Gym-style collection of 57+ competitive text games
  — single-, two- and multi-player — that evaluates and trains LLM agents on social skills
  like negotiation, theory of mind and deception through relative, TrueSkill-rated online
  play against other models and humans.
key: guertler2025textarena
coined: TextArena
gloss: a suite of text-based games for benchmarking and training language-model agents through
  competitive play
claims:
- id: env-counts
  kind: result
  text: TextArena's initial release ships 16 single-player, 47 two-player and 11 multi-player
    text-based environments. That is more in every category than the 8 prior game-based LLM
    benchmarks compared against, including SPIN-Bench (21/3/2) and GameBench (0/3/6).
  scope: Counts as of the paper's initial release; a footnote states the collection had grown
    to 74 games by publication, and some listed games are marked as not yet fully implemented.
  evidence: Table 1
- id: four-capabilities
  kind: result
  text: TextArena is the only framework among the 9 compared game-based LLM benchmarks that
    supports all four of a Gym-compatible API, online evaluation, model-vs-model play and
    model-vs-human play.
  scope: Clembench, LMRL-Gym, GameBench, Game-theoretic LLM, LAMEN, GTBench, GameArena and
    SPIN-Bench as characterised by the authors, on those 4 capability dimensions only.
  evidence: Table 1
- id: relative-eval
  kind: context
  text: TextArena argues that relative, competitive-play rankings are a more sustainable evaluation
    paradigm than absolute benchmarks. Saturating scores on MMLU, HumanEval and ARC-AGI leave
    no headroom, while a ranking survives as long as models differ in capability.
  scope: An argument positioned against Chatbot Arena's human-preference voting, as of the
    April 2025 report; the two paradigms' validity is not empirically compared.
  evidence: Section 1
- id: models-evaluated
  kind: result
  text: TextArena's online system had evaluated 283 models at the time of writing, including
    community submissions and 64 official models hosted by the platform for free play.
  scope: Counts as of the paper's writing on a live, continuously updating leaderboard; submissions
    are unrestricted, so entries can include repeated model variants.
  evidence: Section 4
- id: trueskill
  kind: result
  text: TextArena rates models with TrueSkill (initialised at mu=25, sigma=25/3) rather than
    Elo, and reports that in the authors' experiments TrueSkill converged faster to a reliable
    skill estimate than Elo.
  scope: Online matches with varying player counts and team play; the convergence comparison
    is reported without numbers or a described protocol.
  evidence: Section 4
- id: humanity-baseline
  kind: result
  text: Human players in TextArena are pooled into a single leaderboard entry called "Humanity",
    giving frontier models a directly comparable opponent rating rather than a static human
    score.
  scope: Human ratings are aggregated collectively rather than per player, so the entry reflects
    the mixed skill of whoever chose to play online.
  evidence: Section 4
- id: soft-skill-profile
  kind: result
  text: TextArena estimates a model's aptitude in each of 10 soft skills as a weighted average
    of its ratings on the environments tagged with that skill. Each environment carries up
    to 5 skill tags, among them Theory of Mind, Bluffing, Persuasion and Uncertainty Estimation.
  scope: Skill tags and weights are assigned by the authors, not measured; per-skill scores
    in the published radar figure are each normalised separately for presentation, so cross-skill
    magnitudes are not comparable.
  evidence: Figure 1, Table 3
- id: rule-following-confound
  kind: result
  text: TextArena's preliminary model rankings conflate playing skill with rule and format
    comprehension, and some reasoning models were observed revealing their own cards or hidden
    roles during play.
  scope: Preliminary rankings over a subset of models and games in a 5-page work-in-progress
    report; how much ranking variance the confound explains is not quantified.
  evidence: Figure 2
- id: rl-data-source
  kind: context
  text: TextArena positions competitive self-play in text games as a near-infinite reinforcement-learning
    data source with a difficulty curriculum that adapts as agents improve, aimed at multi-turn
    agentic reasoning rather than single-turn answer quality.
  scope: A stated design motivation and future direction as of the April 2025 report; the
    paper trains no models and reports no RL results.
  evidence: Section 1, Section 6
- id: social-skill-gap
  kind: context
  text: TextArena targets dynamic social capabilities that static question-answering benchmarks
    such as MMLU and HumanEval do not probe. The environments are built to elicit negotiation,
    persuasion, deception and theory of mind in interactive multi-agent play.
  scope: Text-based games only, in English as released; what the environments are designed
    to elicit, not a validated measurement of these constructs.
  evidence: Section 1, Section 3
- id: gym-interface
  kind: result
  text: TextArena keeps its interface close to OpenAI Gym with stackable wrappers, so a full
    two-model match across several games runs in about 10 lines of Python via ta.make, get_observation
    and step.
  scope: The offline API shown in the paper's example script; online play uses ta.make_online
    with model name, description and email, and the code setup may change over time.
  evidence: Section 2, Appendix B
qa:
- ask:
    plain: where can I read about testing language models by making them play games against
      each other instead of answering quiz questions?
    jargon: which work motivates competitive-play relative rankings over saturating static
      LLM benchmarks?
    task: how do I evaluate a language model's negotiation and deception ability when quiz-style
      benchmarks give me nothing to measure?
    practitioner: my model tops the usual multiple-choice benchmarks, so what should I read
      to start evaluating it in interactive games?
  answered_by:
  - relative-eval
  - social-skill-gap
  - env-counts
- ask:
    plain: how many text games can a language model be tested on in TextArena, and how many
      players do they take?
    jargon: what is the environment count of TextArena by single-player, two-player and multi-player
      category relative to other game-based LLM suites?
    task: how do I find a text-game suite with enough single-player, head-to-head and group
      games to cover a whole evaluation?
    practitioner: if I want breadth of games rather than a handful, is TextArena bigger than
      the other LLM game benchmarks?
  answered_by:
  - env-counts
  - four-capabilities
- ask:
    plain: how does a text-game leaderboard turn win-loss records between language models
      into a skill number?
    jargon: why is TrueSkill rather than Elo used to rate LLMs from competitive text-game
      match outcomes?
    task: how do I get a stable skill rating for my model from a limited number of games against
      other models?
    practitioner: should I rate my models with TrueSkill or Elo if I want a reliable ranking
      from few matches?
  answered_by:
  - trueskill
  - models-evaluated
- ask:
    plain: can a language model's game rating be compared with how well actual people play
      the same games?
    jargon: how does TextArena produce a human baseline rating on the same scale as model
      ratings for model-vs-human play?
    task: how do I check whether my model actually beats people at negotiation or bluffing
      games rather than just other models?
    practitioner: can I put my model up against human opponents and see a single human rating
      to compare against?
  answered_by:
  - humanity-baseline
  - four-capabilities
- ask:
    plain: can a text-game score be split up to show whether a model is good at bluffing versus
      reading other players?
    jargon: how are per-skill aptitudes such as theory of mind and persuasion derived from
      environment-level ratings and skill tags?
    task: how do I find out which social abilities my model is weak at rather than just its
      overall rank?
    practitioner: can I get a skill breakdown for my model instead of one leaderboard position?
  answered_by:
  - soft-skill-profile
- ask:
    plain: if a model loses a text game, does that mean it plays badly or that it did not
      follow the rules?
    jargon: do TextArena's preliminary rankings conflate strategic play with rule and output-format
      compliance?
    task: how do I tell whether my model's poor game results come from weak strategy or from
      failing to obey the game format?
    practitioner: should I trust an early text-game leaderboard position as a measure of my
      model's reasoning?
  answered_by:
  - rule-following-confound
- ask:
    plain: can games between language models generate the training data needed to make them
      better at multi-step reasoning?
    jargon: can competitive self-play in text games serve as a reinforcement-learning signal
      with an adaptive difficulty curriculum?
    task: how do I generate multi-turn interaction data for RL training without writing a
      new reward function for every task?
    practitioner: is self-play in text games worth using as an RL data source for my agent?
  answered_by:
  - rl-data-source
  - gym-interface
- ask:
    plain: how much code does it take to set up a match between two language models in a text
      game?
    jargon: does TextArena expose an OpenAI Gym-style API with stackable wrappers for model-vs-model
      episodes?
    task: how do I run a head-to-head match between two models across several games without
      building the harness myself?
    practitioner: will TextArena drop into my existing Gym-based evaluation code?
  answered_by:
  - gym-interface
  - four-capabilities
- ask:
    plain: how many language models have already been scored on a competitive text-game leaderboard?
    jargon: what is the size of the evaluated model pool on TextArena's online leaderboard,
      including community submissions?
    practitioner: if I submit my model, how many other models will it already have ratings
      to be compared against?
  answered_by:
  - models-evaluated
- ask:
    plain: which abilities does a quiz-style benchmark like MMLU miss that showing up in games
      with other players would reveal?
    jargon: why target dynamic multi-agent social capabilities instead of building harder
      static question-answering benchmarks?
    task: how do I measure negotiation, persuasion and theory of mind in a model when the
      standard benchmarks only test knowledge?
    practitioner: is it worth moving to interactive game evaluation for my model, or should
      I just find a harder QA benchmark?
  answered_by:
  - social-skill-gap
  - relative-eval
misreadings:
- 'TextArena''s rankings are not pure measures of strategic ability: the paper states that
  game-play results are influenced both by a model''s ability to play the game and by its
  ability to understand the rules and output format.'
- 'The 57+ environment count is not a count of fully working games at every stage: several
  games listed in the appendix tables are marked as not fully implemented, and the paper''s
  footnote reports the collection had already grown to 74 games by publication.'
- TextArena's soft-skill radar is not a validated psychometric measurement of theory of mind
  or persuasion; skills are hand-tagged per environment with weights, and each axis is normalised
  separately for presentation.
- The TextArena paper does not train any model on its games. RL via self-play is presented
  as a motivation and a future direction, not as a reported result.
- The rankings shown in the TextArena paper are explicitly preliminary and cover only a subset
  of models and games; the live TrueSkill leaderboard, not the paper's figure, is the current
  record.
terminology:
  Humanity: A single pooled leaderboard entry in TextArena representing all human players
    collectively, so that models can be rated against human play as if against one opponent.
  Soft-skill profiling: Estimating a model's aptitude in each of 10 named skill categories
    by taking a weighted average of its ratings across environments tagged with that skill.
  Online play: A mode in which a submitted model is matched over the network against other
    submitted models, platform-hosted models, or human players, with TrueSkill ratings updated
    after every match.
  Relative evaluation: Scoring models by outcomes against each other rather than against a
    fixed answer key, so that no maximum attainable score exists as long as models differ
    in capability.
links_extra:
  project page: https://www.textarena.ai/
  leaderboard: https://www.textarena.ai/leaderboard
  code: https://github.com/LeonGuertler/TextArena
---
