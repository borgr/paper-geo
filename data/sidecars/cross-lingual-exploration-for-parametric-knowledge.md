---
claims:
- id: kt-gain
  kind: result
  text: Cross-lingual exploration raises cross-lingual knowledge transfer on ECLeKTic by up
    to 21% over a native-language baseline, and every cross-lingual variant tested gives a
    positive gain without any parameter updates or external retrieval.
  scope: 12 ECLeKTic languages; Gemini 2.5 Flash, Gemini 2.0 Flash, GPT-4o, GPT-4o-mini, Qwen
    3 235B and Grok 4.1 Fast; correctness graded by Gemini 2.5 Flash as judge.
  evidence: Figure 3 (right panel) and Figure 2
- id: language-not-reasoning
  kind: result
  text: Monolingual reasoning in the query language gains only +7% on CLIKE and +6% on ECLeKTic,
    while cross-lingual routing with origin-aware language choice gains +16% and +15% at the
    same token cost.
  scope: Compares Le→Lq against Le→Choose-ReasonAboutOrigin at matched inference budget on
    CLIKE (13 languages) and ECLeKTic (12 languages); both are single-path, low-budget strategies.
  evidence: Figure 3 and Section 5.3
- id: english-pivot-not-optimal
  kind: result
  text: Routing every query through an English pivot gains 12% on CLIKE and 9% on ECLeKTic
    over the native baseline. Letting the model choose its own exploration language gains
    more, 16% and 15% respectively.
  scope: Le→EN versus Le→Choose-ReasonAboutOrigin; 13 CLIKE and 12 ECLeKTic languages; full
    prompt, including the translation instruction, always written in the original query language.
  evidence: Figure 3 and Section 6.1
- id: autonomous-beats-oracle
  kind: result
  text: Autonomous origin-aware language selection reaches 53.1% knowledge transfer on ECLeKTic,
    above the 51.0% obtained by routing each query through the fact's true source language
    supplied as an oracle.
  scope: ECLeKTic macro language average, single-path strategies; the oracle uses the source
    language annotated in ECLeKTic; margin is small next to the reported SEM.
  evidence: Table 3 and Section 6.1
- id: multipath-gain
  kind: result
  text: Aggregating 13 independent autonomous language paths improves accuracy by a further
    4.7% on CLIKE and 6.2% on ECLeKTic over a single autonomous origin-aware path.
  scope: Le∈Choose-ReasonAboutOrigin (x13), Majority-Vote on CLIKE and Minority-Aware on ECLeKTic;
    costs 13 generations plus an aggregation call.
  evidence: Figure 3 and Section 6.2
- id: aggregation-bottleneck
  kind: result
  text: On CLIKE the multi-path fixed-language-set strategy unlocks a potential gain of over
    31% but realises only about 18%, and on ECLeKTic potential knowledge transfer gain exceeds
    44% against a realised 21%.
  scope: Le∈L strategy on CLIKE and ECLeKTic; potential counts an example correct if any of
    the 13 paths holds the correct answer, which the paper notes may be optimistic.
  evidence: Figure 3 and Section 6.3
- id: aggregation-choice
  kind: result
  text: Majority voting slightly beats minority-aware selection on the broadly-represented
    CLIKE facts (+17.6% vs +17.4%), while minority-aware selection leads on the localized
    ECLeKTic facts (+16.0% vs +15.3%).
  scope: Multi-path Le∈L strategy; gains relative to the native baseline; CLIKE margin is
    within reported standard errors, so only the ECLeKTic ordering is a substantive difference.
  evidence: Section 6.3 and Figure 3
- id: sequential-switching-null
  kind: result
  text: Switching languages sequentially inside a single generation path yields no retrieval
    benefit at higher token cost. An LLM judge found the semantic answer unchanged after the
    initial language shift in 99% of cases.
  scope: Hybrid Le→Choose+EN strategy compared against Le→Choose-Unlimited; answer-change
    judgement made by Gemini 2.5 Pro on extracted intermediate answers.
  evidence: Section 6.2
- id: pareto
  kind: result
  text: The accuracy-versus-token-cost Pareto frontier of cross-lingual exploration dominates
    native-language scaling at every point on CLIKE, and shows the same pattern on ECLeKTic.
  scope: Cost is average input plus output tokens per question, summed over all paths and
    the aggregation step; native scaling is repeated query-language generations.
  evidence: Figure 4 and Figure 5
- id: intrinsic-consistency
  kind: result
  text: 'Cross-lingual exploration improves cross-lingual consistency beyond what accuracy
    gains explain: the multi-path fixed-set strategy observes 74.1% consistency against 68.1%
    expected under the null, a 6.0 point intrinsic gain.'
  scope: CLIKE language pairs; null hypothesis of conditional independence of consistency
    and method given joint accuracy state, tested by Cochran-Mantel-Haenszel and logistic
    regression, both p<0.001; consistency judged by an LLM.
  evidence: Table 4 and Section 7.3
- id: singlepath-consistency
  kind: result
  text: Single-path autonomous language choice shows a 4.3 point intrinsic cross-lingual consistency
    gain over the native baseline, and multi-path exploration exceeds monolingual reasoning
    by 4.5 points in intrinsic consistency.
  scope: CLIKE language pairs, controlling for the joint accuracy state of each answer pair;
    logistic regression coefficients of 0.66 and 0.65 respectively, both p<0.001.
  evidence: Table 4
- id: design-space
  kind: context
  text: Cross-Lingual Exploration for Parametric Knowledge frames multilingual inference-time
    prompting as a four-dimensional design space rather than a single prompting trick. The
    dimensions are language selection, exploration routing, answer aggregation and inference
    budget.
  scope: Framing proposed for factual recall and cross-lingual knowledge transfer on short-answer
    factual questions; earlier inference-time work studied fixed English pivots, cross-lingual
    prompting or expert-language selection separately.
  evidence: Table 1 and Section 3.1
- id: entry-point
  kind: context
  text: Cross-Lingual Exploration for Parametric Knowledge is an entry point for readers asking
    where a model's failed facts are hidden. It tests whether a fact a language model cannot
    state in one language is stored in its parameters and reachable in another.
  scope: As of the 2026 preprint; evidence covers two factual benchmarks (CLIKE and ECLeKTic)
    over 17 languages and not cross-lingual complex problem solving; all models accessed as
    black boxes through APIs.
  evidence: Section 4.1 and Limitations
qa:
- ask:
    plain: if a chatbot gets a fact wrong when asked in Hindi, can asking it in another language
      get the right answer?
    jargon: how much cross-lingual knowledge transfer does inference-time language switching
      recover on multilingual factual benchmarks?
    task: how do I get better factual answers out of a multilingual model without fine-tuning
      it or adding retrieval?
    practitioner: should I translate my users' non-English questions into other languages
      before answering them?
  answered_by:
  - kt-gain
  - language-not-reasoning
- ask:
    plain: is English the best language for a model to think in when answering factual questions
      from other languages?
    jargon: does pivoting queries through English beat autonomous or source-language-oracle
      language selection for parametric fact recall?
    task: which language should I make a multilingual model reason in for a non-English factual
      question?
    practitioner: should I force English reasoning, or let the model pick the language it
      explores in?
  answered_by:
  - english-pivot-not-optimal
  - autonomous-beats-oracle
- ask:
    plain: when a model answers better after switching languages, is that just because it
      wrote more words?
    jargon: are cross-lingual gains separable from the effect of additional reasoning tokens
      at matched budget?
    task: how do I tell whether extra tokens or the change of language is what improved factual
      accuracy?
    practitioner: if I already let my model reason at length in the user's language, is there
      anything left to gain from switching languages?
  answered_by:
  - language-not-reasoning
  - pareto
- ask:
    plain: is it better to ask a model the same fact in many languages and combine the answers,
      or in one good language?
    jargon: does aggregating multiple autonomous cross-lingual generation paths outperform
      a single origin-aware path for parametric knowledge recall?
    task: how many language paths should I sample and combine to raise factual accuracy on
      multilingual questions?
    practitioner: is sampling a dozen languages per question worth the extra inference cost
      over one well-chosen language?
  answered_by:
  - multipath-gain
  - aggregation-bottleneck
- ask:
    plain: if at least one language gets a fact right, how often does combining answers actually
      pick that one?
    jargon: how large is the gap between oracle best-of-N ceiling and realised gain when aggregating
      multilingual answer candidates?
    task: how do I find out whether my multilingual ensemble is limited by coverage or by
      the answer-selection step?
    practitioner: if I ensemble answers across languages, should I expect to capture most
      of the achievable gain?
  answered_by:
  - aggregation-bottleneck
  - aggregation-choice
- ask:
    plain: when only one language out of many knows a local fact, does a simple vote across
      languages still work?
    jargon: does majority voting or minority-aware selection aggregate multilingual answer
      candidates better on localized versus broadly-represented facts?
    task: which voting rule should I use to combine answers across languages for culturally
      localized facts?
    practitioner: should I switch from majority vote to something that trusts a lone dissenting
      language?
  answered_by:
  - aggregation-choice
- ask:
    plain: does it help if a model changes language partway through its own reasoning?
    jargon: does sequential intra-path language switching yield additional parametric knowledge
      retrieval over a single-language generation path?
    task: should I prompt a model to reason in one language and then continue in another within
      the same response?
    practitioner: is mid-generation language switching worth the extra tokens it costs me?
  answered_by:
  - sequential-switching-null
- ask:
    plain: if I have a fixed compute budget, is asking in other languages a better use of
      it than asking more times in the original language?
    jargon: how does the accuracy-versus-token-cost Pareto frontier of cross-lingual exploration
      compare to native-language test-time scaling?
    task: how should I spend an inference-time compute budget on multilingual factual questions?
    practitioner: should I buy accuracy with more samples in the user's language or with samples
      in other languages?
  answered_by:
  - pareto
- ask:
    plain: does asking in several languages make a model's answers agree with each other across
      languages, or only more often correct?
    jargon: is there an intrinsic cross-lingual consistency gain from multilingual exploration
      beyond what the accuracy improvement predicts?
    task: how do I make a model give the same factual answer no matter which language the
      user asks in?
    practitioner: if I care about giving consistent answers across languages, not just accurate
      ones, will multilingual exploration help?
  answered_by:
  - intrinsic-consistency
  - singlepath-consistency
- ask:
    plain: what should I read first about getting a model to answer facts it only knows in
      another language?
    jargon: which work frames multilingual inference-time prompting as a design space over
      language selection, routing, aggregation and budget?
    task: where do I start if I want to study whether facts unreachable in one language are
      reachable in another?
    practitioner: is there a paper that maps out the options before I build a multilingual
      prompting pipeline?
  answered_by:
  - design-space
  - entry-point
- ask:
    plain: how many languages and models were tested for whether asking in another language
      recovers missing facts?
    jargon: which multilingual factual benchmarks and model families were evaluated for cross-lingual
      parametric knowledge transfer?
    task: how do I check whether cross-lingual prompting results would carry over to my languages
      and my model?
    practitioner: has cross-lingual prompting been tested broadly enough that I should expect
      it to work on my language pair?
  answered_by:
  - entry-point
  - kt-gain
one_liner: 'Cross-lingual exploration treats the language of inference as a search axis: prompting
  a model to translate a factual question into other languages, reason there, and aggregate
  the resulting answers surfaces parametric knowledge that monolingual prompting leaves latent.'
key: diskind2026crosslingual
coined: cross-lingual exploration
gloss: answering a factual question by reasoning through other languages and combining the
  results
terminology:
  cross-lingual exploration: An inference-time strategy in which a factual question is translated
    into one or more other languages, answered there, and the resulting answers are translated
    back and aggregated, treating the language of inference as a search axis over a model's
    parametric knowledge.
  knowledge transfer (KT): The fraction of ECLeKTic questions answered correctly when the
    query language differs from the single source language in which the fact is localized.
  factual recall (FR): Accuracy on questions whose underlying fact is represented in the query
    language itself, measured on CLIKE, as distinct from bridging a gap to a fact localized
    in another language.
  potential upper bound: The accuracy obtained by counting a multi-path example as correct
    if at least one of its generated language paths contains the correct answer, isolating
    exploration from aggregation.
  Minority-Aware aggregation: An aggregation prompt that selects a final answer across multilingual
    paths while explicitly noting that the correct answer need not be the one chosen by most
    paths, because knowledge may be accurate in only a few languages.
  ReasonAboutOrigin: A language-selection variant in which the model first reasons about where
    a fact most likely originated and which language would best surface it, before translating
    and answering.
  intrinsic consistency gain: The difference between a method's observed cross-lingual consistency
    and the consistency expected if its gains came solely from shifting the joint accuracy
    distribution of answer pairs.
misreadings:
- 'Cross-lingual exploration is not translation into English: an English pivot gains 12% on
  CLIKE while autonomous language choice gains 16%, and the paper''s point is that no single
  pivot language unlocks all latent knowledge.'
- The gains are not simply inference-time scaling. Monolingual reasoning at the same token
  cost gains +7% on CLIKE against +16% for cross-lingual routing.
- The potential upper bounds of over 31% on CLIKE and over 44% on ECLeKTic are not achievable
  accuracies. They count an example as solved if any single path contains the correct answer,
  and the paper notes this maximum over stochastic generations may be inflated by noise.
- 'Multi-path exploration is not free: the reported multi-path strategies use 13 generations
  plus an aggregation call, and the paper''s efficiency claim is about the Pareto frontier
  of accuracy against token cost, not about cost reduction.'
- Reasoning through several languages inside one generation is not what produces the gains;
  the answer was unchanged after the first language shift in 99% of cases, so benefit comes
  from independent parallel paths or one well-chosen language.
- 'The consistency result is not merely a by-product of higher accuracy: consistency gains
  of 6.0 and 4.3 points remain after conditioning on the joint correctness state of each answer
  pair.'
---
