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
- ask:
    plain: Can results about which BERT layer handles which linguistic task be an artifact
      of the probing dataset?
    jargon: Is the layer-wise localization of edge-probing tasks in BERT identified by the
      probing data, or confounded by properties of the probed examples?
    task: How do I check whether my layer-attribution probing result for a BERT task would
      survive a different probing set?
    practitioner: Should I trust a published per-layer ranking of BERT tasks when choosing
      which layer to read features from?
  answered_by:
  - rankings-196
  - threshold-monotone
  - pipeline-not-identified
- ask:
    plain: Does BERT really handle word-level things before grammar and grammar before meaning?
    jargon: Is the claim that BERT's layers rediscover the classical NLP pipeline supported
      once probing-set confounds are accounted for?
    task: How much can I rely on the lexical-to-syntactic-to-semantic layer story when picking
      BERT layers for a task?
    practitioner: Should I still cite the NLP-pipeline account of BERT layers, or has the
      layer ordering been shown to be unstable?
  answered_by:
  - pipeline-not-identified
  - dep-ner-reversal
- ask:
    plain: How many different orderings of seven linguistic tasks by BERT layer can the same
      probing setup produce?
    jargon: How many task orderings by expected layer over the 7 edge-probing tasks are attainable
      by varying the probing sets' span-length distributions?
    task: How do I tell which pairs of probing tasks have a stable layer ordering in BERT
      and which can be swapped?
    practitioner: If I report a layer ranking over seven probing tasks in BERT, how much of
      it could a reviewer flip by rebuilding the datasets?
  answered_by:
  - rankings-196
  - context-length-overlap
- ask:
    plain: Can one task look like BERT computes it in a higher layer than another even when
      it does not for any individual example?
    jargon: Can aggregate expected layers of two edge-probing tasks reverse the per-bin ordering,
      i.e. a Simpson's paradox in layer attribution?
    task: How do I avoid an aggregation artifact when I compare the average layer of dependency
      parsing and NER probes in BERT?
    practitioner: Is an aggregate expected-layer comparison between two probing tasks safe
      to report, or should I break it out by span length?
  answered_by:
  - dep-ner-reversal
  - srl-nonterm-reversal
- ask:
    plain: How much does the layer gap between two linguistic tasks in BERT shrink once the
      probing examples are matched for span length?
    jargon: What magnitude of natural direct effect on the expected-layer difference remains
      once span-length distributions are equalized across two probing tasks?
    task: How do I quantify how much of the layer difference between two BERT probing tasks
      comes from span length rather than the task?
    practitioner: Is it worth matching span-length distributions across my probing datasets,
      or is the effect on expected layer too small to bother?
  answered_by:
  - nde-magnitude
- ask:
    plain: Do BERT probes move to higher layers when the two words being related are farther
      apart?
    jargon: Does raising the maximum span distance in an edge-probing set monotonically raise
      the expected layer for co-reference, SRL, dependency and relation classification in
      BERT?
    task: How do I set the maximum span distance in a probing dataset if I do not want the
      layer estimate to move?
    practitioner: If I cap span distance in my co-reference or SRL probing set, will my layer
      estimate change?
  answered_by:
  - threshold-monotone
- ask:
    plain: What paper should I read first about hidden confounds in studies of which BERT
      layer does what?
    jargon: Which work brings causal mediation analysis to layer-wise probing of transformer
      representations?
    task: Where do I start reading if I want to design a probing study of BERT layers that
      controls for example properties?
    practitioner: Is there a paper I can cite for why my reviewers should distrust a raw layer
      ranking from probing?
  answered_by:
  - mediation-framing
  - best-practices
- ask:
    plain: What is the right way to compare which BERT layer handles each task without being
      fooled by dataset differences?
    jargon: What reporting practice is recommended for comparing expected layers across edge-probing
      tasks in the presence of a mediator such as span distance?
    task: How do I control for span distance when I compare probes across BERT layers?
    practitioner: Should I report per-bin expected layers or a direct effect when I compare
      probing tasks across layers?
  answered_by:
  - best-practices
  - context-length-overlap
- ask:
    plain: What does the distance between the two words in a probing example mean, and why
      does it matter for BERT layers?
    jargon: How is context length defined for an edge-probing instance, and how does it act
      as a mediator on expected layer?
    task: How do I measure span distance in my edge-probing examples so I can bin results
      by it?
  answered_by:
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
