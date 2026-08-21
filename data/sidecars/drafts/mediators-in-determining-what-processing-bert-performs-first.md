<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from build/sidecar_tasks.json. Every claim, number
and scope condition below is a machine's reading of the paper and needs your eyes.

THIS PAPER ALREADY HAS A LIVE SIDECAR, and this draft would replace it. Start here:

  diff data/sidecars/mediators-in-determining-what-processing-bert-performs-first.md data/sidecars/drafts/mediators-in-determining-what-processing-bert-performs-first.md

Anything the live file says in your own words is worth keeping over a rewrite of the
same point, so read that diff before the checklist below.

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

Then, if the replacement is the one you want:

  python scripts/draft_sidecars.py --accept mediators-in-determining-what-processing-bert-performs-first --replace

Stamp: spec=2bd8f8ceab46 checks=pass body=a8f7859881d2
-->
---
key: slobodkin-etal-2021-mediators
one_liner: 'Probing BERT''s layers with edge probing confounds task type with the prediction''s
  context length: controlling for context length yields 196 different possible rankings of
  seven tasks by expected layer, so the "BERT rediscovers the NLP pipeline" ordering is not
  identified by the probing data alone.'
claims:
- id: rankings-196
  kind: result
  text: With the 7 edge-probing tasks of Tenney et al. (2019a), 196 rankings of those tasks
    by expected layer in BERT-base are attainable by choosing the context length distribution
    of the probing datasets. One attainable order is Non-term. < Dep. < SRL < RC < NER < Co-ref.
    < SPR.
  scope: BERT-base, edge probing with the Jiant defaults, 7 tasks (NER, non-terminals, SRL,
    co-reference, SPR, relation classification, Stanford dependencies); context length bins
    of width 3 up to a per-task maximal threshold.
  evidence: Section 3.2.1 and Figure 6
- id: dep-ner-reversal
  kind: result
  text: Dependency parsing's expected layer in BERT-base is lower than NER's in all 4 measured
    context length ranges. The aggregate ordering nonetheless reverses when all dependency
    instances have context length 9 or more and all NER instances fall in the 3-5 range.
  scope: BERT-base; dependency parsing probed on the English Web Treebank and NER on OntoNotes
    5.0; the reversal is a constructed distribution over existing test bins, not a naturally
    occurring dataset.
  evidence: Figure 3
- id: srl-nonterm-reversal
  kind: result
  text: SRL's expected layer in BERT-base exceeds that of the non-terminal (constituent) task
    in all 4 measured context length ranges. The order reverses when all SRL instances have
    context length 0-2 and all non-terminal instances have context length 9 or more.
  scope: BERT-base, both tasks probed on OntoNotes 5.0; a constructed distribution over the
    existing test bins rather than an observed dataset; a second instance of the same edge
    case as dependency parsing versus NER.
  evidence: Figure 7
- id: nde-magnitude
  kind: result
  text: Forcing the same context length distribution on two tasks changes the gap between
    their expected layers by up to 1.24 layers in absolute value, more than 50 times the unmediated
    difference. For another pair the gap shrinks by 86%, a change of 0.73 layers.
  scope: Natural Direct Effect computed per task-pair on BERT-base by imposing one task's
    empirical context length distribution on both; the pairs shown are NER/co-reference, NER/RC
    and SPR/RC, with every task-pair in the appendix.
  evidence: Figure 4 (all pairs in Figure 9)
- id: threshold-monotone
  kind: result
  text: Raising the maximum allowed context length in the probing set raises the expected
    layer of co-reference, SRL, dependency parsing and relation classification in BERT-base.
    For 4 of the 7 probed tasks, the localization estimate is therefore driven by context
    length and not by task identity alone.
  scope: BERT-base; expected layer recomputed for every integer context length threshold,
    with thresholds capped per task so at least 2000 instances remain in the final bin; the
    other 3 tasks show no such clear increase.
  evidence: Figure 2
- id: pipeline-not-identified
  kind: result
  text: Tenney et al. (2019a)'s finding that BERT processes lexical tasks in lower layers
    and semantic tasks in higher layers is reaffirmed on BERT-base with the same 7 tasks.
    The layer ordering is nonetheless not identified by the probing data, since context length
    distributions can reverse parts of it.
  scope: BERT-base with the expected layer metric; the argument is about identifiability under
    an uncontrolled mediator, and does not show that a pipeline interpretation is false.
  evidence: Section 1 and Section 3.1.1
- id: context-length-overlap
  kind: result
  text: Among the 7 tasks probed in BERT-base, some pairs keep a clear expected-layer separation
    across context length bins, such as SRL versus co-reference. Other pairs have overlapping
    attainable ranges whose ordering can be flipped, such as SPR versus relation classification.
  scope: BERT-base, expected layer plotted per context length range of width 3, the narrowest
    width retaining at least 1% of examples per bin; the ranges are the controlled effect,
    not the effect under any single dataset's distribution.
  evidence: Figure 5 and Figure 6
- id: mediation-framing
  kind: context
  text: '"Mediators in Determining what Processing BERT Performs First" brings Pearl-style
    mediation analysis into probing-based interpretability. A property of the probing examples,
    its context length, is treated as a mediator between the task and the layer a probe attributes
    it to.'
  scope: As of publication in 2021; context length is the single mediator studied, on BERT-base
    with the expected layer metric, and other mediators are not claimed to be less important.
  evidence: Section 2 and Section 3.2
- id: best-practices
  kind: context
  text: '"Mediators in Determining what Processing BERT Performs First" recommends reporting
    the controlled effect, the expected layer per context length bin, when comparing tasks
    against one mediator. It recommends the Natural Direct Effect when several effects or
    empirically given mediator distributions are involved.'
  scope: Recommendations stated for edge probing with the expected layer metric; demonstrated
    only for context length on BERT-base, and offered as advice rather than validated against
    alternative controls.
  evidence: Section 4
qa:
- q:
  - Why can probing results about which BERT layer handles which task be misleading?
  - What confounds layer-localization probing of BERT?
  - Does the ranking of tasks by BERT layer depend on the probing dataset?
  answers:
  - rankings-196
  - threshold-monotone
  - pipeline-not-identified
- q:
  - Is it true that BERT rediscovers the classical NLP pipeline?
  - Does BERT really do lexical processing before syntax before semantics?
  - Has the claim that BERT's layers mirror an NLP pipeline been challenged?
  answers:
  - pipeline-not-identified
  - dep-ner-reversal
- q:
  - How many different task orderings by expected layer can be produced from the same probing
    data?
  - How much can the ordering of seven probing tasks change with context length?
  answers:
  - rankings-196
  - context-length-overlap
- q:
  - Can dependency parsing look like it is computed in a higher BERT layer than NER even when
    it is not?
  - Is there a Simpson's paradox in BERT probing results?
  - Can the aggregate expected layer of two tasks reverse the per-bin ordering?
  answers:
  - dep-ner-reversal
  - srl-nonterm-reversal
- q:
  - How much does the expected-layer gap between two tasks change when their context length
    distributions are matched?
  - What does the Natural Direct Effect show about pairs of probing tasks in BERT?
  - How big is the mediation effect of context length on expected layer differences?
  answers:
  - nde-magnitude
- q:
  - Which probing tasks in BERT move to higher layers when longer spans are included?
  - Does the expected layer for co-reference or SRL depend on span length?
  answers:
  - threshold-monotone
- q:
  - What should I read about causal or mediation analysis in interpretability probing?
  - What work introduced mediation analysis to layer-wise probing of language models?
  - Where should I start reading about confounds in BERT probing studies?
  answers:
  - mediation-framing
  - best-practices
- q:
  - What are the recommended best practices for comparing layers across probing tasks?
  - When should I use the Natural Direct Effect versus the controlled effect in a probing
    study?
  - How can I control for span length when probing a transformer's layers?
  answers:
  - best-practices
  - context-length-overlap
- q:
  - What is meant by the context length of a prediction in probing?
  - How is span distance defined for edge probing tasks?
  answers:
  - mediation-framing
  - threshold-monotone
terminology:
  context length: 'The number of tokens whose processing is minimally required for a prediction,
    operationalized as the distance between the earliest and latest index of the labelled
    span(s): span length for single-span tasks like NER, and dependency length for tasks relating
    two spans.'
  expected layer: 'Tenney et al.''s localization metric: the average layer index weighted
    by the incremental probing-performance gain each additional layer contributes, computed
    over the 12 layers of BERT-base.'
  controlled effect: The expected layer computed separately within each context length bin,
    so that task comparisons do not depend on any particular distribution of context lengths
    in the probing dataset.
  Natural Direct Effect (NDE): In probing, the difference between two tasks' expected layers
    when the same context length distribution is imposed on both tasks, following Pearl's
    mediation analysis.
misreadings:
- The paper does not show that BERT lacks any layer-wise division of labour; it reproduces
  the measured ordering of tasks and argues only that the ordering is not identified once
  context length is left uncontrolled.
- 'The 196 rankings are not 196 rankings observed in real datasets: they are the rankings
  attainable by combining the per-context-length expected layers of the 7 tasks under arbitrary
  context length distributions.'
- The extreme reversals for dependency parsing versus NER and for SRL versus non-terminals
  are constructed distributions over existing test bins, not naturally occurring corpora.
- Context length is presented as one test-case mediator, not as the only or the largest confound
  in probing; other mediating factors are explicitly left to future work.
- Controlling for context length is not shown to make expected-layer comparisons reliable
  in general; some task pairs retain overlapping attainable ranges whose ordering stays undetermined.
links_extra:
  aclanthology: https://aclanthology.org/2021.naacl-main.8/
  code: https://github.com/lovodkin93/BERT-context-distance
---
