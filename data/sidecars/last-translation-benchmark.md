---
key: zouhar2026translationbenchmark
coined: Last Translation Benchmark
gloss: a crowdsourced, peer-reviewed set of hard-to-translate texts, images, audio and video,
  each graded by pass/fail verification rules
one_liner: The Last Translation Benchmark is a live, crowdsourced collection of peer-reviewed
  examples that break leading machine translation models, each paired with handwritten pass/fail
  verification rules that an LLM checks, giving a reproducible, interpretable score instead
  of an opaque quality metric.
claims:
- id: ltb-contribution
  kind: context
  text: The Last Translation Benchmark (LTB) is a live machine translation challenge set of
    human-authored examples that most leading translation models fail on. Contributors keep
    adding examples, with tagged releases such as LTBv1.
  scope: As of LTBv1, the release of contributions accepted before September 1st 2026; one
    of several community-driven efforts to collect model-breaking examples, applied here to
    translation.
- id: verification-rules-approach
  kind: context
  text: The Last Translation Benchmark scores translations with example-specific verification
    rules, where a translation succeeds only if an LLM verifier finds it passes every rule.
    The rules give the evaluator privileged knowledge of the failure the generator lacks.
  scope: Rules are written by the contributor of each example and describe its targeted failure,
    not every aspect of translation quality; LTBv1 averages 1.8 rules per example.
- id: frontier-pass-rate
  kind: result
  text: On LTBv1-eval, the best model, Gemini 3.1 Pro, passes all verification rules on only
    37.4% to 43.8% of examples depending on the verifier LLM. GPT-5.6 Sol is second at 28.1%
    to 36.1%.
  scope: 911 text-only LTBv1-eval examples in blind mode, scored by 6 verifier LLMs; examples
    a model cannot translate for lack of language support are excluded.
  evidence: Section 3.2
- id: unseen-models-also-fail
  kind: result
  text: The difficulty of the Last Translation Benchmark is not limited to the models examples
    were filtered against. 19 of the 29 evaluated models were never shown to contributors,
    and GPT-5.6 Luna among them passes only 15.4% to 22.9% of LTBv1-eval.
  scope: Up to 10 models were shown on the contributor platform; the 29-model evaluation uses
    the same 6 verifiers on LTBv1-eval.
  evidence: Section 3.2
- id: judges-rate-failures-good
  kind: result
  text: Generic LLM judges score Gemini 3.1 Pro translations on LTBv1-eval at 72.1 to 95.4
    out of 100, the rubric's good or very good bands. Rule-based verifiers pass at most 43.8%
    of them.
  scope: Judges are the same 6 LLMs prompted with a cESA-style 0 to 100 rubric in which 65
    to 80 means good; the 95.4 comes from Gemini 3.1 Pro judging its own output.
  evidence: Section 3.2
- id: rules-in-prompt
  kind: result
  text: Showing LLM translators the human-written verification rules raises the verifier pass
    rate on the Last Translation Benchmark from 7.2% to 89.8%. Rules the LLMs generate for
    themselves raise it only to 12.9%.
  scope: Averaged over LLM translators on LTBv1-eval, in the oracle setting where the rules
    are privileged information not available to a real translation system.
  evidence: Table 3
- id: metrics-miss-rule-gains
  kind: result
  text: Standard translation metrics do not register the gain from giving LLM translators
    the verification rules. 2 of the 5 automatic metrics score the rule-informed translations
    lower, while the verifier pass rate rises from 7.2% to 89.8%.
  scope: MetricX 24, MetricX QE 24, Comet 22, Comet QE 22 and ChrF, averaged over LLM translators
    on LTBv1-eval with the human translation as reference where needed.
  evidence: Table 3
- id: verifier-ranking-stable
  kind: result
  text: Model rankings from verification rules are stable across the choice of verifier LLM,
    with an average Kendall tau of 86.9, against 72.0 for generic LLM judges and 35.1 for
    automatic metrics.
  scope: Pairwise ranking similarity within each evaluation approach over the models on LTBv1-eval,
    using the 6 verifier or judge LLMs and 5 metrics.
  evidence: Table 4
- id: verifier-agrees-with-humans
  kind: result
  text: Rankings of translation models by verifier pass rate agree with human judgments at
    an average Kendall tau of 90.5, versus 34.9 for generic LLM judges and 16.2 for automatic
    metrics.
  scope: Human rankings from the cESA study on a subset of models and examples; the same agreement
    values are reported whether annotators saw the rules or not.
  evidence: Table 4
- id: self-bias
  kind: result
  text: LLMs used as generic translation judges favour their own translations far more than
    when they act as rule verifiers. Gemma 4 shows 27.6% self-bias as a judge but 8.9% as
    a verifier.
  scope: 6 LLMs, self-bias being self-ranking minus the average ranking by other models; Gemini
    3.1 Pro instead shows negative self-bias in both roles (-8.3% judge, -8.9% verifier).
  evidence: Table 5
- id: human-evaluation
  kind: result
  text: In a human evaluation, annotators rate the contributors' reference translations above
    every model they scored, 90.8 versus 68.1 for Gemini 3.1 Pro once shown the rules. Without
    the rules the gap is smaller, 81.4 versus 77.0.
  scope: 22 bilingual annotators, 317 examples across 19 language pairs, a subset of models;
    cESA protocol, rating each translation first without and then with the rules.
  evidence: Section 3.2
- id: dataset-size
  kind: result
  text: LTBv1 contains 3456 accepted examples spanning 109 languages, contributed by 260 people
    from 177 institutions. 94% of examples are text, and 13% involve neither English source
    nor English target.
  scope: Contributions collected May to September 1st 2026; 73% translate into English and
    14% out of English; the evaluation subset LTBv1-eval has 911 text-only examples.
  evidence: Section 3; Table 1
- id: difficulty-taxonomy
  kind: result
  text: The most frequent difficulty labels in LTBv1 are metaphor (1086 examples), cultural
    artifact (986) and polysemy (948). Less-benchmarked challenges also appear, including
    internet cultural artifacts (152) and meta-reasoning (83).
  scope: Multi-label tags on all LTBv1 examples, assigned by an LLM after 2 linguists built
    the taxonomy inductively on a subset; tags are not exhaustive.
  evidence: Table 6; Section 3.4
- id: cost-per-example
  kind: result
  text: Collecting one accepted Last Translation Benchmark example costs about $0.12 in model
    calls. A contributor makes on average 10 translation attempts before submitting a valid
    example.
  scope: Model-call costs only, for up to 10 platform translations plus Gemini 3.1 Pro verification
    of each rule; LTBv1 averages 1.8 rules per example.
  evidence: Section 2
qa:
- ask:
    plain: Is there a benchmark of sentences that today's best machine translation systems
      still get wrong?
    jargon: What challenge set targets failure modes of state-of-the-art MT now that standard
      test sets are saturating?
    task: How do I find hard, human-written test cases to stress-test a translation model?
    practitioner: Which benchmark should I use if WMT-style test sets no longer separate my
      strong translation models?
  answered_by:
  - ltb-contribution
  - frontier-pass-rate
- ask:
    plain: How good are the best AI translators on really hard translation examples?
    jargon: What verifier pass rate do frontier LLMs such as Gemini 3.1 Pro and GPT-5.6 reach
      on LTBv1-eval?
    practitioner: Can I trust Gemini or GPT to handle tricky idioms, puns and cultural references
      in translation?
  answered_by:
  - frontier-pass-rate
  - unseen-models-also-fail
- ask:
    plain: Is a translation benchmark built by breaking a few models only hard for those same
      models?
    jargon: Does adversarial filtering against the platform models inflate difficulty only
      for those models, or does it transfer to held-out systems?
    practitioner: If my translation model was never used to filter the Last Translation Benchmark,
      will it still find the examples hard?
  answered_by:
  - unseen-models-also-fail
- ask:
    plain: How can you score a translation without a vague quality number?
    jargon: How do example-specific pass/fail verification rules compare with reference-based
      metrics and rubric LLM judges for MT evaluation?
    task: How do I evaluate translations so that I know exactly which error a model made?
    practitioner: Should I replace COMET or LLM-as-a-judge scores with checklist-style verification
      rules for my translation evaluation?
  answered_by:
  - verification-rules-approach
  - judges-rate-failures-good
  - verifier-agrees-with-humans
- ask:
    plain: Do AI judges of translation quality miss obvious translation mistakes?
    jargon: How do generic LLM-as-a-judge scores compare with rule-based verifier pass rates
      on hard MT examples?
    practitioner: Is an LLM judge rating my translations as good enough evidence that they
      are correct?
  answered_by:
  - judges-rate-failures-good
  - metrics-miss-rule-gains
- ask:
    plain: Do AI translators do better if you tell them what mistake to avoid?
    jargon: How much does conditioning an LLM translator on gold versus self-generated verification
      rules improve verifier pass rate?
    task: How do I get an LLM to avoid a known pitfall when translating a tricky sentence?
    practitioner: Should I have my LLM write its own checklist of translation pitfalls before
      translating?
  answered_by:
  - rules-in-prompt
- ask:
    plain: Do scores like COMET and chrF notice when a translation fixes the hard part?
    jargon: Are MetricX, COMET and chrF sensitive to translations that satisfy targeted verification
      rules?
    practitioner: Can I rely on COMET or MetricX to tell me my translation model fixed a specific
      error?
  answered_by:
  - metrics-miss-rule-gains
- ask:
    plain: Does it matter which AI model you use to grade translations?
    jargon: How stable are MT system rankings across evaluator LLMs for rule verification,
      LLM judges and neural metrics, measured by Kendall tau?
    practitioner: If I switch my evaluator LLM, will my translation model rankings change?
  answered_by:
  - verifier-ranking-stable
  - verifier-agrees-with-humans
- ask:
    plain: Do AI models grade their own translations too kindly?
    jargon: How large is self-preference bias of LLM evaluators in MT, as a judge versus as
      a rule verifier?
    practitioner: Is it a problem if I use the same LLM to translate and to evaluate the translations?
  answered_by:
  - self-bias
- ask:
    plain: Do human translators still beat AI on hard translation examples according to human
      raters?
    jargon: How do cESA human scores of reference translations compare with frontier MT output
      on LTBv1, with and without verification rules?
    practitioner: Are human translations still clearly better than Gemini 3.1 Pro on tricky
      inputs?
  answered_by:
  - human-evaluation
- ask:
    plain: How big is the Last Translation Benchmark and which languages does it cover?
    jargon: What are the size, language coverage, modality mix and English-centricity of LTBv1?
    practitioner: Does the Last Translation Benchmark have enough examples in my language
      pair to be useful to me?
  answered_by:
  - dataset-size
- ask:
    plain: What kinds of text are hardest for machine translation today?
    jargon: Which sources of translation difficulty, such as metaphor, polysemy and cultural
      knowledge, dominate a crowdsourced MT challenge set?
    task: How do I find which linguistic phenomena my translation model is weakest on?
  answered_by:
  - difficulty-taxonomy
- ask:
    plain: How cheap is it to crowdsource hard translation test examples with AI checking?
    jargon: What is the model-call cost per accepted example in a crowdsourced MT challenge
      set with LLM verification?
    practitioner: Can I afford to build a similar hard translation test set for my own domain?
  answered_by:
  - cost-per-example
misreadings:
- 'A low pass rate on the Last Translation Benchmark does not estimate typical translation
  quality: examples are selected to break leading models and rules target one failure each,
  so the benchmark is a stress test, not a measure of average user experience.'
- The verifier pass rate is an LLM checking human-written rules, not a human judgment of every
  translation; its agreement with humans is shown on a 317-example human study, not on the
  full benchmark.
- The human reference translations pass the verification rules by construction, because a
  submission is accepted only if its reference passes; the separate human evaluation is what
  supports their superiority.
- The 89.8% pass rate with human rules in the prompt is an oracle result using privileged
  information, not a translation setup a deployed system can use; realistic comparisons use
  the blind mode.
- The name "Last Translation Benchmark" is hyperbole, according to its own contributor FAQ,
  and not a claim that machine translation evaluation is finished; the benchmark is live and
  gets new releases.
- The Last Translation Benchmark is intended for evaluation, not training, except for controlled
  research studies.
terminology:
  verification rule: A short, English, pass/fail criterion written for one translation example
    that states the specific failure a correct translation must avoid, such as a required
    word sense or gender.
  verifier pass rate: The percentage of examples for which a translation passes all of that
    example's verification rules, as judged by an LLM verifier.
  LTBv1: The first tagged release of the Last Translation Benchmark, containing the 3456 examples
    accepted before September 1st 2026.
  LTBv1-eval: A 911-example, text-only subset of LTBv1 selected for evaluation by difficulty,
    output diversity and balance across language pairs.
  blind mode: A Last Translation Benchmark leaderboard setting in which the translation model
    sees only the input, used to compare realistic translation systems.
  oracle mode: A Last Translation Benchmark leaderboard setting in which the translation model
    also sees privileged information such as the verification rules or the human translation.
  model blockers: Taxonomy labels for target-side failures, such as refusals, irrelevant output,
    incomplete output, instruction injection and tokenization errors, that hide the source-side
    difficulty of an example.
---
