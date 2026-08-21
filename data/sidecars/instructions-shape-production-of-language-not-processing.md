---
claims:
- id: production-centered-mechanism
  kind: context
  text: '"Instructions shape Production of Language, not Processing" introduces a cognitively
    inspired processing–production lens for language models, operationalized by probing representations
    at sample-token versus output-token positions. The paper''s central argument is that instruction
    effects concentrate at output-token positions.'
  scope: Decoder-only LMs (Llama-3.1, OLMo-2, Qwen-2.5) on 5 binary judgment tasks with single-token
    outputs; token position is an approximation, not a claim of strict computational separation.
- id: sample-vs-output-spread
  kind: result
  text: Task-specific probing accuracy in sample tokens varies by at most ±0.7 percentage
    points across 3 prompting variations, versus ±2.2 pp for output tokens, over the same
    layers.
  evidence: Figure 2 (a) and (b)
  scope: Averaged across 5 binary judgment tasks and 3 model families; variations are instruction-first,
    sample-first, and 4-shot in-context learning without an explicit instruction.
- id: correlation-with-behavior
  kind: result
  text: Task-specific information in output tokens correlates strongly with exact-match behavior
    (Kendall τ=0.62), whereas information in sample tokens correlates weakly and negatively
    (τ=-0.15) and is essentially uncorrelated with output-token information (τ=0.02).
  evidence: Section 4
  scope: Kendall τ computed across 3 model families, 5 binary judgment tasks and 3 prompting
    variations; linear probes, so a lower bound on decodable information.
- id: full-intervention
  kind: result
  text: Blocking attention from instruction tokens to all subsequent tokens cuts exact-match
    accuracy by 58.0 pp while probing accuracy falls only 0.8 pp in sample tokens and 3.0
    pp in output tokens.
  evidence: Figure 3 (b)
  scope: Instruction-first prompting, averaged across 3 model families and 5 binary judgment
    tasks with single-token answers.
- id: prompt-only-intervention
  kind: result
  text: Blocking attention only from instruction tokens to sample tokens costs 4.0 pp exact-match
    accuracy and 0.8 pp probing accuracy in sample tokens, far less than blocking instruction
    flow to all subsequent tokens.
  evidence: Figure 3 (b)
  scope: Instruction-first prompting, averaged across models and tasks; per-model behavioral
    drops range from -2.0 to -4.0 pp.
- id: scaling-production
  kind: result
  text: From the smallest to the largest model, output-token task-specific information grows
    by 46% in Qwen-2.5 and 30% in OLMo-2, compared with 30% and 20% in sample tokens.
  evidence: Section 5.2 with Figure 5
  scope: 6 Qwen-2.5 sizes (0.5B–32B) and 4 OLMo-2 sizes (1B–32B), instruction-first prompting,
    relative layer positions.
- id: instruction-tuning
  kind: result
  text: Instruction-tuned models carry substantially more task-specific information at output-token
    positions than their base counterparts, while layer-wise sample-token profiles stay nearly
    identical and the information peak layer does not shift.
  evidence: Figure 6 (a)
  scope: Base/instruct pairs of Llama-3.1-8B, OLMo-2-7B and Qwen-2.5-7B under instruction-first
    prompting; the paper reports the gap qualitatively rather than as a single number.
- id: task-type-coupling
  kind: result
  text: Output-token probing predicts behavior better than sample-token probing on all 5 binary
    judgment tasks. The gap is largest for EWOK (τ=0.70 vs 0.29) and oLMpics (0.53 vs 0.21),
    and smallest for BLiMP (0.56 vs 0.37) and ToM (0.22 vs 0.15).
  evidence: Figure 7 (a)
  scope: Instance-level Kendall τ averaged across models and prompting variations; ToM is
    weak on both stages, so its small gap reflects weak coupling overall rather than tight
    coupling.
- id: tom-interference
  kind: result
  text: On the theory-of-mind task, cutting attention from instruction to sample tokens improves
    exact-match accuracy by 6.0 pp, while BLiMP loses 13.0 pp under the same intervention.
  evidence: Figure 14
  scope: Prompt-only intervention relative to instruction-first prompting, averaged across
    models; oLMpics and EWOK show minimal behavioral change in either direction.
- id: instance-level-agreement
  kind: result
  text: The two instruction-based prompting variations agree behaviorally on 77% of instances,
    agreement with the no-instruction 4-shot baseline drops to 60% and 58%, and all 3 variations
    agree on only 48%.
  evidence: Section 4 with Figure 2 (d)
  scope: Instance-level exact-match agreement across 5 binary judgment tasks and 3 model families,
    single-token yes/no answers.
- id: probing-validity
  kind: result
  text: The layer-wise information patterns hold under control-task selectivity checks, an
    information-theoretic (MDL-style) assessment and probes with 1 or 2 hidden layers, and
    emerge with as few as 100 to 200 training samples.
  evidence: Figure 8 and Figure 9
  scope: Validation across all model families, sizes and tasks; linear probes still only bound
    linearly accessible information, and non-linear probes shift information levels slightly
    without changing the layer-wise pattern.
- id: unrelated-instructions
  kind: result
  text: Replacing the task instruction with a semantically unrelated one (counting occurrences
    of the letter "a") costs 10.0 points of probing accuracy in output tokens but only 2.0
    in sample tokens.
  evidence: Figure 10, left
  scope: Sanity check relative to instruction-first prompting, averaged across 5 tasks and
    3 model families.
- id: evaluation-implication
  kind: context
  text: 'The processing–production decomposition separates two failure modes that behavioral
    scores conflate: task information never encoded from the input, versus information encoded
    but not selected during output production.'
  scope: Argued from binary judgment tasks with single-token answers; whether the same decomposition
    localizes failures in open-ended generation or multi-step reasoning is untested.
qa:
- ask:
    plain: when I reword a prompt, does the model understand the input differently or just
      answer differently?
    jargon: do instruction phrasing variants shift task-relevant information in sample-token
      representations, or only at output-token positions?
    task: how do I tell whether prompt sensitivity in a language model comes from input encoding
      or from answer generation?
    practitioner: my model's accuracy swings with prompt wording — is it worth rewriting my
      prompts to fix comprehension, or is the problem in how answers get produced?
  answered_by:
  - sample-vs-output-spread
  - correlation-with-behavior
  - production-centered-mechanism
- ask:
    plain: what happens to a model's answers if the instruction is prevented from influencing
      the rest of the prompt?
    jargon: what does attention masking from instruction tokens reveal about where instructions
      causally act, sample positions or output positions?
    task: how can I test causally whether an instruction affects input encoding or only answer
      selection?
    practitioner: if I block instruction attention to the examples but not to the answer position,
      how much accuracy do I lose?
  answered_by:
  - full-intervention
  - prompt-only-intervention
- ask:
    plain: as models get bigger, do they take in more from the input or mainly get better
      at saying the answer?
    jargon: how does task-specific decodable information at sample versus output token positions
      scale with parameter count in Qwen-2.5 and OLMo-2?
    task: how do I work out whether scaling up a model buys better input representations or
      better answer expression on judgment tasks?
    practitioner: should I expect a bigger model in the same family to encode more task information,
      or just verbalize it better?
  answered_by:
  - scaling-production
  - instruction-tuning
- ask:
    plain: what actually changes inside a model when it is trained to follow instructions?
    jargon: do instruction-tuned checkpoints differ from base checkpoints in layer-wise probing
      profiles at sample tokens or only at output tokens?
    task: how do I find out whether instruction tuning taught a model new task knowledge or
      just how to deliver an answer?
    practitioner: is switching from a base model to its instruction-tuned version going to
      change what it knows about my task, or only how it responds?
  answered_by:
  - instruction-tuning
  - scaling-production
- ask:
    plain: does the split between understanding and answering look the same on grammar judgments
      as on world-knowledge or mind-reading questions?
    jargon: how does the coupling between output-token probing accuracy and exact-match behavior
      vary across BLiMP, oLMpics, EWOK, StereoSet and theory-of-mind judgments?
    task: how do I know which judgment benchmarks have internal signals that actually predict
      what a model answers?
    practitioner: for the benchmark I care about, will probing internal representations tell
      me anything about the model's answers?
  answered_by:
  - task-type-coupling
  - tom-interference
- ask:
    plain: can a model get more questions right when the instruction is stopped from touching
      the examples?
    jargon: on which judgment task does masking instruction-to-sample attention raise exact-match
      accuracy rather than lower it?
    task: how do I check whether the instruction in my prompt is interfering with how the
      model reads the examples?
    practitioner: could dropping or isolating the instruction actually improve my model's
      accuracy on a theory-of-mind style task?
  answered_by:
  - tom-interference
- ask:
    plain: what should I read about the gap between what a language model knows internally
      and what it actually says?
    jargon: which work frames prompt sensitivity as a production-side rather than encoding-side
      phenomenon in transformer language models?
    task: where do I start reading if I want to separate a model's task knowledge from its
      answer generation?
  answered_by:
  - production-centered-mechanism
  - evaluation-implication
- ask:
    plain: how can I tell whether a model got a question wrong because it did not know the
      answer or because it failed to give it?
    jargon: why do exact-match benchmark scores conflate absent task encoding with failed
      output selection, and what does joint probing add?
    task: how do I diagnose the source of a model's benchmark failures beyond the accuracy
      number?
    practitioner: my model scores badly on a judgment benchmark — how do I find out whether
      to fix its knowledge or its answer format?
  answered_by:
  - evaluation-implication
  - correlation-with-behavior
  - instance-level-agreement
- ask:
    plain: how much can you trust a layer-by-layer probe that claims to find task information
      in a model?
    jargon: do control-task selectivity, MDL-style probing and non-linear probes preserve
      the reported layer-wise task-information patterns?
    task: how many labeled examples and what probe checks do I need before believing a layer-wise
      probing result?
    practitioner: if I run linear probes on my own model's layers, will the pattern survive
      switching to an MLP probe or shrinking the training set?
  answered_by:
  - probing-validity
- ask:
    plain: do a model's answers actually change if I put the instruction first, put the examples
      first, or give no instruction at all?
    jargon: what is instance-level agreement between instruction-based prompt orderings and
      a 4-shot no-instruction baseline on judgment tasks?
    task: how do I measure whether two prompt formats are really equivalent rather than just
      scoring the same?
    practitioner: can I treat few-shot examples without an instruction as interchangeable
      with an explicit instruction for my evaluation?
  answered_by:
  - instance-level-agreement
  - sample-vs-output-spread
- ask:
    plain: what happens inside a model if the instruction in the prompt has nothing to do
      with the question being asked?
    jargon: how much decodable task information is lost at sample versus output positions
      when the instruction is replaced with a semantically unrelated one?
    task: how do I test whether a wrong or off-task instruction corrupts a model's reading
      of the input?
    practitioner: if my prompt template carries a leftover irrelevant instruction, is the
      model's input representation damaged or just its answer?
  answered_by:
  - unrelated-instructions
- ask:
    plain: which models and which tasks were tested to see whether instructions change comprehension
      or only answers?
    jargon: across which model families, sizes and binary judgment benchmarks does the processing–production
      asymmetry replicate?
    practitioner: is the finding that instructions act at output positions backed by more
      than one model family, or should I retest on mine?
  answered_by:
  - production-centered-mechanism
  - sample-vs-output-spread
  - task-type-coupling
one_liner: Layer-wise probing at sample-token versus output-token positions across 5 binary
  judgment tasks shows instructions barely change how language models encode input and mostly
  change how they produce output, an asymmetry attention-blocking interventions confirm causally.
coined: production-centered mechanism
gloss: separating what a model encodes from its input (processing) from what it emits as output
  (production), by token position
misreadings:
- 'Stable sample-token representations do not mean instructions are unnecessary: blocking
  instruction flow to all subsequent tokens costs 58.0 pp exact-match accuracy, so instructions
  remain essential to behavior even though they barely alter input encoding.'
- The processing–production split is an analytical lens based on token positions, not a claim
  that decoder-only transformers contain two architecturally separate stages; upper-layer
  sample-token states already carry output-preparing transformations.
- The evidence covers binary judgment tasks with single-token "yes"/"no" answers; whether
  the production-centered mechanism holds for open-ended generation or multi-step reasoning
  is left open.
- 'The asymmetry is not uniform across tasks: knowledge and reasoning tasks (oLMpics, EWOK,
  ToM) show loose processing–production coupling, while surface-sensitive tasks (BLiMP, StereoSet)
  are more tightly coupled.'
- Linear probing accuracy is a lower bound on encoded information, so "stable processing"
  means stable linearly decodable task information, not proof that nothing about the input
  encoding changed.
- 'The 58.0 pp drop under the full intervention should not be read as purely a loss of task
  information: it also removes output-formatting cues, and the paper treats it as an upper
  bound.'
---
