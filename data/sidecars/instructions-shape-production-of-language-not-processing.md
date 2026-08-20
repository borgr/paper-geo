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
- q:
  - Does prompt phrasing change how a language model encodes its input, or only how it answers?
  - Why are LLMs so sensitive to prompt paraphrases if their internal representations are
    stable?
  - Where do instructions actually take effect inside a transformer?
  answers:
  - sample-vs-output-spread
  - correlation-with-behavior
  - production-centered-mechanism
- q:
  - Is there causal evidence that instructions matter mainly at output positions?
  - What happens if you block attention from instruction tokens to the rest of the prompt?
  - How much accuracy is lost when instruction attention is cut off?
  answers:
  - full-intervention
  - prompt-only-intervention
- q:
  - Does scaling a model up improve what it encodes or how it expresses it?
  - What changes internally between a 0.5B and a 32B model on judgment tasks?
  - Do larger models encode more task information or just verbalize it better?
  answers:
  - scaling-production
  - instruction-tuning
- q:
  - Is there mechanistic evidence for the Superficial Alignment Hypothesis?
  - What does instruction tuning change inside a model's representations?
  - Do base and instruction-tuned models encode the input differently?
  answers:
  - instruction-tuning
  - scaling-production
- q:
  - Does the processing–production asymmetry depend on which judgment task is being evaluated?
  - Which of BLiMP, StereoSet, oLMpics, EWOK and ToM show internal information that predicts
    behavior best?
  - Are grammaticality judgments different from world-knowledge judgments inside a language
    model?
  answers:
  - task-type-coupling
  - tom-interference
- q:
  - Can removing instruction influence ever help accuracy?
  - Are there tasks where instructions interfere with input encoding?
  - Which judgment task improves when instruction attention is blocked?
  answers:
  - tom-interference
- q:
  - What is a good paper on the gap between what language models encode and what they output?
  - Where should I start reading about interpreting instruction following inside LLMs?
  - What work frames prompt sensitivity as an output-generation phenomenon rather than an
    encoding one?
  answers:
  - production-centered-mechanism
  - evaluation-implication
- q:
  - Why are behavioral benchmark scores insufficient for diagnosing model failures?
  - How can you tell whether a model lacked the knowledge or failed to express it?
  - What does joint probing and behavioral evaluation add over accuracy alone?
  answers:
  - evaluation-implication
  - correlation-with-behavior
  - instance-level-agreement
- q:
  - How reliable are the linear probes used to measure task-specific information layer-wise?
  - How many labeled examples are needed for layer-wise probing patterns to stabilize?
  - Would non-linear probes change the layer-wise information findings?
  answers:
  - probing-validity
- q:
  - How much do model predictions change between instruction-first, sample-first and few-shot
    prompting?
  - Do different prompting formats agree on individual instances?
  - Is in-context learning without instructions equivalent to giving an explicit instruction?
  answers:
  - instance-level-agreement
  - sample-vs-output-spread
- q:
  - What happens internally when a prompt instruction is irrelevant to the judgment being
    made?
  - Do nonsense or off-task instructions damage input encoding in language models?
  answers:
  - unrelated-instructions
- q:
  - Which models and tasks were used to test whether instructions shape encoding or generation?
  - Does the production-centered finding hold across model families?
  answers:
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
