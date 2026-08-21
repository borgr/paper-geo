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
    unsorted:
    - Does prompting a model in a different language help it recall facts it gets wrong in
      the original language?
    - Can translating a question into another language improve factual accuracy of an LLM?
    - How much does cross-lingual prompting improve knowledge transfer?
  answered_by:
  - kt-gain
  - language-not-reasoning
- ask:
    practitioner: Should I always translate non-English queries into English before asking
      an LLM?
    unsorted:
    - Is English always the best language to reason in for factual questions?
    - Does an English pivot beat letting the model pick its own language?
  answered_by:
  - english-pivot-not-optimal
  - autonomous-beats-oracle
- ask:
    unsorted:
    - Are the gains from multilingual prompting just the effect of extra reasoning tokens?
    - How do you separate chain-of-thought benefits from language-switching benefits?
    - Is the improvement due to the language shift or to thinking longer?
  answered_by:
  - language-not-reasoning
  - pareto
- ask:
    unsorted:
    - Does sampling several languages and voting beat a single well-chosen language?
    - Is multi-path multilingual answering worth the extra compute?
    - How much does aggregating 13 language paths add over one path?
  answered_by:
  - multipath-gain
  - aggregation-bottleneck
- ask:
    unsorted:
    - What limits multilingual ensembling of factual answers?
    - Why does the realized accuracy fall far below the best-of-N ceiling in multilingual
      prompting?
    - How large is the gap between potential and realized gains in cross-lingual exploration?
  answered_by:
  - aggregation-bottleneck
  - aggregation-choice
- ask:
    practitioner: Should I use majority voting or something else to combine answers from different
      languages?
    unsorted:
    - Which aggregation rule works best for localized cultural facts across languages?
    - Is majority vote the right choice when only one language knows the answer?
  answered_by:
  - aggregation-choice
- ask:
    unsorted:
    - Does switching languages several times within one chain of thought help?
    - Is it useful to reason in English and then in another language in the same response?
    - Does sequential language switching inside a single path add anything?
  answered_by:
  - sequential-switching-null
- ask:
    unsorted:
    - Is multilingual prompting a cost-effective way to spend inference compute?
    - How does cross-lingual exploration compare to just sampling more answers in the query
      language?
    - What is the accuracy-versus-token-cost tradeoff of multilingual exploration?
  answered_by:
  - pareto
- ask:
    unsorted:
    - Does multilingual prompting make a model's answers more consistent across languages,
      or just more accurate?
    - How can consistency gains be separated from accuracy gains in cross-lingual evaluation?
    - Is there an intrinsic cross-lingual consistency improvement from exploring multiple
      languages?
  answered_by:
  - intrinsic-consistency
  - singlepath-consistency
- ask:
    practitioner: What should I read about accessing hidden factual knowledge in multilingual
      language models?
    unsorted:
    - Which paper frames multilingual inference-time prompting as a design space?
    - Where should I start reading about cross-lingual knowledge transfer at inference time?
    - What work studies whether facts unreachable in one language are reachable in another?
  answered_by:
  - design-space
  - entry-point
- ask:
    unsorted:
    - Which models and languages were tested for cross-lingual factual recall?
    - What benchmarks measure cross-lingual knowledge transfer for parametric facts?
    - How broad is the evaluation of cross-lingual exploration?
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
