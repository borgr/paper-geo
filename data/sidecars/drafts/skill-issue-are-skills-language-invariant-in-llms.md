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

Then promote it:  python scripts/draft_sidecars.py --accept skill-issue-are-skills-language-invariant-in-llms

Stamp: spec=fd01ca70bea8 checks=pass body=1b3e9cef6b81
-->
---
one_liner: Two instances of the same LLM playing each other through different language interfaces
  win at markedly different rates, so the skills a model has in one language are not the skills
  it applies in another.
coined: Multilingual TextArena
gloss: a version of the TextArena game suite where each player's instructions and board are
  rendered in a different language while the rules stay fixed
claims:
- id: multilingual-textarena
  kind: context
  text: Multilingual TextArena covers 65 TextArena games in 193 languages, rendering each
    player's instructions and board in a different language. The rules, legal actions, rewards
    and transition dynamics are unchanged across languages.
  scope: Verification is tiered. 8 Tier-A languages were checked by native speakers, 42 Tier-B
    by closed-model back-translation judging, and 142 more by NLLB-200 round-trip agreement.
- id: skill-not-knowledge
  kind: context
  text: Multilingual self-play measures whether an LLM's skills, as distinct from its stored
    knowledge, transfer across languages by having 2 instances of one model compete through
    different language interfaces.
  scope: As of the 2026 preprint, framed against earlier cross-lingual work on knowledge retrieval
    and on static benchmarks. Evidence comes from 3 models of 3B to 4B parameters, 8 languages
    and 6 games.
- id: english-strongest-hebrew-weakest
  kind: result
  evidence: Figure 2
  text: English is the strongest interface language and Hebrew among the weakest for all 3
    models tested, aggregated over 6 games of self-play. Qwen3-4B shows the sharpest language
    hierarchy and Gemma-4-E4B-it the flattest.
  scope: Self-play between 2 instances of one model, so margins compare languages within a
    model and never across models. Gemma-4-E4B-it, Qwen3-4B and Ministral3-3B-Instruct on
    8 languages.
- id: blotto-most-language-sensitive
  kind: result
  evidence: Table 2
  text: Colonel Blotto is the most language-sensitive of the 6 games for all 3 models, with
    a mean gap of 1.07 between a model's strongest and weakest language. Kuhn Poker is the
    least sensitive at 0.13.
  scope: Gap is the spread of mean language margins within one model and game, averaged over
    the 3 models. 8 languages, 400 self-play games per direction.
- id: reasoning-language-recovery
  kind: result
  evidence: Table 3
  text: Switching only Gemma-4-E4B-it's reasoning language to English, with the TicTacToe
    interface still in German, moves the mean language margin from -0.22 to +0.20. That recovers
    89.4% of the gap to the English-interface ceiling of +0.25.
  scope: Gemma-4-E4B-it only, with German as the weak interface. SimpleTak recovers 60.5%
    the same way, and Kuhn Poker recovery is small and non-monotonic across reasoning languages.
- id: spatial-axis-failure
  kind: result
  evidence: Appendix G
  text: Gemma-4-E4B-it's TicTacToe losses split fairly evenly in English across rows at 28.5%,
    columns at 34.8% and diagonals at 36.7%. Under an Arabic interface the same model loses
    to rows only 20.3% of the time and to diagonals 45.3%.
  scope: Gemma-4-E4B-it in TicTacToe. Hebrew skews the same way as Arabic, while Qwen3-4B's
    defeat distribution stays stable across languages apart from Hebrew.
- id: simpletak-column-losses
  kind: result
  evidence: Appendix G
  text: In SimpleTak, Gemma-4-E4B-it loses to a completed column in 46.8% of English-interface
    defeats but 57.2% of Arabic and Hebrew ones, against 53.2% row losses in English.
  scope: Gemma-4-E4B-it in SimpleTak, where over 90% of its wins come from straight lines,
    which is what lets row and column losses stand for separate spatial axes.
- id: nim-knowledge-not-executable
  kind: result
  evidence: Appendix G
  text: Qwen3-4B plays Nim's optimal first move 80.8% of the time under an English interface
    but only 24.6% under French. Both languages produce a similar number of optimal-strategy
    mentions in the game logs.
  scope: Qwen3-4B in Nim with a board where the first player has exactly 1 optimal move. Hebrew
    and Arabic fall to 4.0% and 10.5%, while Gemma-4-E4B-it stays at 99.2% or above in every
    language.
- id: latin-script-switch-recovers-knowledge
  kind: result
  evidence: Appendix G
  text: 70% of Ministral3-3B-Instruct's Arabic and 50% of its Hebrew optimal-strategy mentions
    in Nim come from logs where the model switched into a Latin script mid-reasoning. Such
    switching occurs in only 3.7% of Arabic and 1% of Hebrew logs.
  scope: Ministral3-3B-Instruct in Nim only, counted over game-log mentions rather than over
    model internals, and the gap between languages may therefore be wider than the mention
    counts suggest.
- id: kuhn-risk-profile-shift
  kind: result
  evidence: Appendix G
  text: Gemma-4-E4B-it bets the middle card Q in Kuhn Poker 41.6% of the time under a Malay
    interface and 63.3% under Hebrew. Its play of clearly weak and clearly strong cards varies
    far less across languages.
  scope: Gemma-4-E4B-it in Kuhn Poker across 8 languages. Ministral3-3B-Instruct instead folds
    the strongest card K when facing a bet between 10.4% and 23.7% of the time.
- id: benchmarks-predict-level-not-spread
  kind: result
  evidence: Figure 4
  text: Mean language margin correlates with 5-shot Global MMLU accuracy at Pearson r between
    0.73 and 0.92 depending on the model, and with Belebele at 0.71 to 0.79. Static benchmark
    accuracy does not predict a model's spread across languages.
  scope: 8 languages per model, so each correlation has n=8. Gemma-4-E4B-it has the lowest
    Global MMLU mean at 49.9% yet the smallest cross-language spread, and Qwen3-4B the highest
    mean with the largest spread.
- id: web-text-explains-part
  kind: result
  evidence: Figure 4
  text: Language strength correlates with available web text at an average Pearson r of 0.79
    against log FineWeb-2 word counts, and the residuals are large. Malay beats Hebrew for
    every model despite the smaller FineWeb-2 corpus.
  scope: Web text is a proxy for training data, which is undisclosed for all 3 models. Chinese
    has roughly 20 times less web text than English yet reaches near-English margins for Qwen3-4B
    and Ministral3-3B-Instruct.
- id: evaluation-scale
  kind: result
  evidence: Section 3
  text: The multilingual self-play evaluation runs 518,400 games in total, 28,800 per model
    and game pair, with 400 games for every ordered language pair and player role assignment.
  scope: 3 models by 6 games by all 8 languages, inference only. Each primary run used 2 NVIDIA
    H200 GPUs and about 6 H200 GPU-hours, excluding Iterated Prisoner's Dilemma.
qa:
- ask:
    plain: is there research on whether a language model is better at playing games in some
      languages than in others?
    jargon: how is cross-lingual skill inconsistency measured separately from cross-lingual
      knowledge transfer?
    task: how do I test whether a model's reasoning skills survive being asked in a different
      language?
    practitioner: should I expect the same agent behaviour from one model across the languages
      my users write in?
  answered_by:
  - skill-not-knowledge
  - english-strongest-hebrew-weakest
- ask:
    plain: what should I read first about language models performing unequally across languages
      for reasons other than missing facts?
    jargon: what work established that an LLM's interactive skills, not just its factual recall,
      are language-dependent?
    practitioner: is there a paper I can cite for skill gaps across languages inside one model?
  answered_by:
  - skill-not-knowledge
  - multilingual-textarena
- ask:
    plain: is there a set of text games translated into many languages for testing language
      models?
    jargon: what multilingual extension of TextArena renders observations in a target language
      without changing rules or legal actions?
    task: where do I get game environments in many languages so I can run the same game in
      2 languages at once?
    practitioner: can I reuse an existing multilingual game suite instead of translating environments
      myself?
  answered_by:
  - multilingual-textarena
- ask:
    plain: which language is a language model strongest at when it plays games against itself?
    jargon: which interface language gives the highest role-pooled win-loss margin in multilingual
      self-play?
    practitioner: if I run an agent in Hebrew instead of English, how much playing strength
      am I giving up?
  answered_by:
  - english-strongest-hebrew-weakest
- ask:
    plain: does the choice of game change how much language matters?
    jargon: which game environments show the largest max-minus-min language gap in mean language
      margin?
    task: how do I pick a game that will expose language effects rather than hide them?
  answered_by:
  - blotto-most-language-sensitive
- ask:
    plain: can a model do better in a weak language if it thinks in a stronger one?
    jargon: does decoupling the reasoning language from the environment interface language
      recover the margin lost under a weak interface?
    task: how do I recover accuracy when my prompts have to stay in a low-performing language?
    practitioner: should I make my agent reason in English while keeping the user-facing language
      unchanged?
  answered_by:
  - reasoning-language-recovery
- ask:
    plain: do language models misread game boards differently depending on the language of
      the instructions?
    jargon: how does the distribution of TicTacToe defeats over rows, columns and diagonals
      shift with the interface language?
    practitioner: will an Arabic or Hebrew interface make my agent miss board threats that
      it catches in English?
  answered_by:
  - spatial-axis-failure
  - simpletak-column-losses
- ask:
    plain: can a model know the right strategy for a game and still fail to use it in one
      language?
    jargon: does optimal-move execution in Nim track optimal-strategy mention counts across
      interface languages?
    task: how do I tell whether a language gap is missing knowledge or failed execution?
  answered_by:
  - nim-knowledge-not-executable
- ask:
    plain: why does a model sometimes start writing in English in the middle of an Arabic
      answer?
    jargon: what share of optimal-strategy mentions under Arabic and Hebrew interfaces come
      from mid-reasoning script switching?
    practitioner: if my model switches script mid-answer, is that a bug or is it reaching
      knowledge it otherwise cannot?
  answered_by:
  - latin-script-switch-recovers-knowledge
- ask:
    plain: does a model take different risks when the same card game is presented in a different
      language?
    jargon: how do card-conditioned bet, call and fold probabilities in Kuhn Poker vary with
      interface language?
    practitioner: can I assume my model's decision policy is the same across the languages
      it is deployed in?
  answered_by:
  - kuhn-risk-profile-shift
- ask:
    plain: can multilingual benchmark scores tell me how a model will behave in each language?
    jargon: how strongly does mean language margin correlate with Global MMLU and Belebele
      accuracy, and does either predict cross-language spread?
    task: how do I predict which languages my agent will be weak in without running the agent?
    practitioner: is a high multilingual benchmark average enough to tell me a model is consistent
      across languages?
  answered_by:
  - benchmarks-predict-level-not-spread
- ask:
    plain: is a language weak in a model just because there is little text in it on the web?
    jargon: how much of the language hierarchy in self-play is explained by FineWeb-2 per-language
      word counts, and which languages deviate?
    practitioner: should I assume a low-resource language will be my model's weakest interface?
  answered_by:
  - web-text-explains-part
- ask:
    plain: how many games were played to measure the language differences?
    jargon: what is the self-play sample size per language pair, model and game environment?
    task: how many matches do I need per language pair before a win-loss margin is worth reading?
  answered_by:
  - evaluation-scale
misreadings:
- A 193-language release is not 193 verified languages. 8 languages were verified by native
  speakers and the rest by automatic back-translation judging, which is why the experiments
  use the 8.
- Reasoning in a stronger language is not a general repair. Recovery is large in TicTacToe
  and SimpleTak and small and non-monotonic in Kuhn Poker.
- The language a model wins with is not simply the language it has most training data in.
  Malay outperforms Hebrew for every model despite a smaller web corpus, and Chinese reaches
  near-English margins with far less web text.
- A high multilingual benchmark average does not mean uniform behaviour across languages.
  Benchmark level and cross-language spread move independently in these models.
- The results are measured on models of 3B to 4B parameters and do not establish that language
  effects hold at larger scale.
terminology:
  language interface: the language in which a game's instructions, board and observations
    are presented to a player, holding the rules, legal actions and rewards fixed.
  role-pooled win-loss margin: wins minus losses divided by total games for one language against
    another, pooled over both player-role assignments so first-move advantage cancels.
  mean language margin: one language's average role-pooled win-loss margin against every other
    language evaluated, for a fixed model and game.
  Tier A: the 8 languages whose game translations were verified by native speakers, as opposed
    to tiers verified by automatic back-translation judging.
---
