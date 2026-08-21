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
    practitioner: Where should I start reading about evaluating language-model agents through
      competitive gameplay?
    unsorted:
    - What benchmarks exist for evaluating LLMs by having them play games against each other?
    - What work argues that relative rankings beat static benchmarks for LLM evaluation?
  answered_by:
  - relative-eval
  - social-skill-gap
  - env-counts
- ask:
    unsorted:
    - How many game environments does TextArena include?
    - How many single-, two- and multi-player text games are in TextArena?
    - Does a game benchmark for LLMs cover more environments than GTBench or SPIN-Bench?
  answered_by:
  - env-counts
  - four-capabilities
- ask:
    unsorted:
    - How are models ranked in TextArena?
    - Why use TrueSkill instead of Elo for rating language models in games?
    - What rating system tracks LLM performance in competitive text games?
  answered_by:
  - trueskill
  - models-evaluated
- ask:
    practitioner: Can I compare an LLM's game performance against human players?
    unsorted:
    - How does TextArena benchmark models against humans?
    - What does the "Humanity" entry on the TextArena leaderboard mean?
  answered_by:
  - humanity-baseline
  - four-capabilities
- ask:
    practitioner: How can I measure whether a model is good at bluffing or theory of mind?
    unsorted:
    - How does TextArena break down a model's score into soft skills?
    - What skill categories do text-game environments get tagged with?
  answered_by:
  - soft-skill-profile
- ask:
    unsorted:
    - Is a model's ranking in text games confounded by whether it understands the rules?
    - What are the limitations of the preliminary TextArena model rankings?
    - Do reasoning models leak their hidden roles when playing social deduction games?
  answered_by:
  - rule-following-confound
- ask:
    practitioner: Where do I get a difficulty curriculum for multi-turn agentic RL?
    unsorted:
    - Can competitive text games be used as reinforcement-learning training data for LLMs?
    - Does TextArena support RL training with self-play?
  answered_by:
  - rl-data-source
  - gym-interface
- ask:
    practitioner: How do I plug my own model into a text-game environment?
    unsorted:
    - How hard is it to run an LLM-vs-LLM match in TextArena?
    - Does TextArena use an OpenAI Gym-style API?
  answered_by:
  - gym-interface
  - four-capabilities
- ask:
    practitioner: How many models can I play games against for free online?
    unsorted:
    - How many models have been evaluated on the TextArena leaderboard?
    - How many language models have been rated on a competitive text-game leaderboard?
  answered_by:
  - models-evaluated
- ask:
    unsorted:
    - Which social skills do static LLM benchmarks like MMLU fail to measure?
    - Why build game environments instead of harder question-answering benchmarks?
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
