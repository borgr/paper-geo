<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from build/sidecar_tasks.json. Every claim, number
and scope condition below is a machine's reading of the paper and needs your eyes.

THIS PAPER ALREADY HAS A LIVE SIDECAR, and this draft would replace it. Start here:

  diff data/sidecars/robustness-as-an-emergent-property-of-task-performance.md data/sidecars/drafts/robustness-as-an-emergent-property-of-task-performance.md

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

  python scripts/draft_sidecars.py --accept robustness-as-an-emergent-property-of-task-performance --replace

Stamp: spec=c66468b7280b checks=pass body=5f2910ef6208
-->
---
key: ashurytahan2026robustness
one_liner: 'Robustness to meaning-preserving prompt changes is largely a by-product of task
  competence: across 9 open-weight LLMs and 6 benchmarks, performance explains 92.4% of output-consistency
  variance, so robustness emerges as tasks saturate.'
claims:
- id: perf-explains-robustness
  kind: result
  text: Across 9 open-weight LLMs and 6 classification benchmarks, task performance explains
    92.4% of the variance in output-consistency robustness. The fitted regression slope is
    1.05, so robustness rises slightly faster than performance.
  scope: 9 open-weight models on IMDB, BoolQ, MMLU, MMLU-Pro, RewardBench and GPQA; 100 examples
    per dataset under 24 inference configurations; exact-match classification.
  evidence: Figure 1
- id: imdb-saturated-robust
  kind: result
  text: On IMDB, where all 9 evaluated LLMs score between 95% and 97% accuracy, strict output
    consistency across 24 configurations ranges from 81% to 94%. A random baseline with the
    same success rate reaches only 33% to 54%.
  scope: IMDB sentiment classification, 100 sampled examples; robust means identical outputs
    across all 24 configurations; the baseline assumes independent per-configuration success
    at the model's accuracy.
  evidence: Section 4.1
- id: torr-correlation
  kind: result
  text: On the ToRR table-reasoning benchmark, robustness and aggregated performance correlate
    at Pearson 0.91 at the dataset level. ToRR uses its own score-range robustness metric,
    so the trend is not tied to output consistency.
  scope: Existing ToRR leaderboard results over 10 table-reasoning datasets, mostly generative;
    no new experiments were run on ToRR.
  evidence: Section 4.1
- id: torr-easy-vs-hard
  kind: result
  text: On ToRR, WikiTQ models mostly score 80% to 90% with robustness of roughly 75%, while
    FinQA models score around 40% with robustness around 50%. The easier table-reasoning dataset
    is the more robust one.
  scope: Two ToRR datasets read from its leaderboard (WikiTableQuestions F1, FinQA program
    accuracy) with ToRR's own robustness metric; typical values, not every model.
  evidence: Section 4.1
- id: model-factors-weak
  kind: result
  text: Model identity affects output consistency less than task performance does, but not
    negligibly. On BoolQ, gpt-oss-120b reaches 78% robustness against 56% for gpt-oss-20b
    at a 1-point performance difference.
  scope: Within the gpt-oss family; on MMLU a 6-point performance gap between the two corresponds
    to a 40% robustness difference. Only 9 open-weight models were compared.
  evidence: Section 4.2
- id: torr-cross-family
  kind: result
  text: On ToRR's FinQA, Claude-3.5-Sonnet and Gemini-1.5-Flash both score 43% and reach robustness
    of 56% and 57%. Models with comparable table-reasoning performance usually show similar
    robustness, across and within model families.
  scope: ToRR leaderboard results; within the Llama family, Llama-3.1-405B-Instruct and Llama-3.1-70B-Instruct
    score 36% and 37% with 49% robustness each on FinQA.
  evidence: Section 4.2
- id: beats-random-baseline
  kind: result
  text: Measured output consistency exceeds a matched random baseline on all 6 benchmarks,
    by 43.4% on IMDB and 62.9% on BoolQ on average. Llama-4-Scout-17B-Instruct exceeds the
    baseline on BoolQ by 70.4%.
  scope: Own experiments only, not ToRR; on MMLU, MMLU-Pro, RewardBench and GPQA the baseline
    is zero because performance is below 80%.
  evidence: Section 4.3
- id: config-choices-minor
  kind: result
  text: 'Configuration choices barely move accuracy: across 4 factors and 6 datasets, about
    70% of ANOVA p-values are non-significant. Where prompt variation and demonstration count
    are significant, effect sizes stay below 0.005.'
  scope: Type II and Type III ANOVA on performance, not on robustness, over demonstrations,
    prompt variation, template and temperature; significant effects appear on RewardBench,
    MMLU and MMLU-Pro.
  evidence: Appendix D.3
- id: perturbations-as-noise
  kind: result
  text: No single perturbation type is systematically harder for LLMs, in either the dedicated
    experiments or the ToRR benchmark. Paraphrases, demonstration changes, temperature and
    random noise act as interchangeable sources of noise.
  scope: Lightweight meaning-preserving perturbations (paraphrase, 2 or 4 demonstrations,
    TAB or random-string noise, temperature 0.2 or 0.6); not adversarial attacks.
  evidence: Section 4.4
- id: metrics-agree
  kind: result
  text: Average performance drop rate reproduces the dataset ordering found with strict output
    consistency, with GPQA the least robust and IMDB the most robust. The performance-robustness
    link does not depend on the choice of robustness metric.
  scope: Same 9 models, 6 datasets and 24 configurations; performance drop rate and per-example
    score standard deviation, both score-based, alongside the string-based output consistency.
  evidence: Appendix D.1
- id: long-tail-consistency
  kind: result
  text: As performance rises, per-example score standard deviation becomes long-tailed, with
    most examples perfectly consistent and a few carrying the variation. Less robust settings
    give flatter distributions, similar across models within a benchmark.
  scope: Per-example STD over 24 configurations, per model and dataset; only consistently
    correct examples count as success consistency, and consistent failure is separated out.
  evidence: Appendix D.2
- id: external-validation
  kind: result
  text: Benchmark scores re-measured for the robustness study track published numbers with
    minor differences. Llama 4 Maverick scores 62 on MMLU-Pro against 62 published and 80
    on MMLU against 85 published.
  scope: Cross-check limited to MMLU, MMLU-Pro and GPQA against model cards and the HELM capabilities
    leaderboard; HELM used chain-of-thought, the study asked for a final answer only.
  evidence: Appendix A.2
- id: reframing-robustness
  kind: context
  text: Robustness as an Emergent Property of Task Performance argues that LLM robustness
    to meaning-preserving input changes follows task competence rather than being an independent
    model capability. Robustness on a task is expected to emerge as that task saturates.
  scope: A position argued from correlational evidence on 9 open-weight models and existing
    ToRR results, as of 2026; no training-time intervention was tested, and adversarial robustness
    is out of scope.
- id: deployment-signal
  kind: context
  text: Ashury-Tahan et al. propose very high task accuracy as an empirical indicator that
    an LLM will answer that task consistently under prompt variation. Older saturated tasks,
    not current frontier benchmarks, are then the candidates for sensitive deployment.
  scope: An implication drawn from benchmark experiments; it concerns output consistency,
    not factual correctness, safety or calibration, and was not validated on deployed applications.
qa:
- ask:
    plain: if a language model scores very high on a task, does it also give the same answer
      when the prompt is worded differently?
    jargon: how much of the variance in output-consistency robustness across prompt perturbations
      is explained by benchmark accuracy?
    task: how do I predict whether an LLM will be prompt-stable on a task without running
      a full perturbation sweep?
    practitioner: can I use my model's accuracy on a task as a proxy for how sensitive it
      will be to prompt wording?
    adjacent: is robustness at odds with accuracy for LLMs under prompt paraphrases, or do
      the two rise together?
  answered_by:
  - perf-explains-robustness
  - imdb-saturated-robust
- ask:
    plain: when a model is right almost every time, isn't giving the same answer to reworded
      prompts just luck?
    jargon: does strict output consistency exceed a random baseline matched to per-configuration
      accuracy?
    practitioner: should I believe prompt-consistency numbers on a saturated benchmark like
      IMDB, or is high accuracy doing all the work?
  answered_by:
  - beats-random-baseline
  - imdb-saturated-robust
- ask:
    plain: does the link between accuracy and answer consistency also hold for generative
      tasks like table question answering?
    jargon: does performance correlate with robustness on the ToRR table-reasoning leaderboard?
    task: how do I check whether prompt robustness tracks accuracy on generative table reasoning
      such as WikiTQ or FinQA?
  answered_by:
  - torr-correlation
  - torr-easy-vs-hard
- ask:
    plain: are some language models just naturally steadier under different prompt wordings,
      regardless of how well they do the task?
    jargon: how much does model identity contribute to output consistency once task performance
      is controlled for?
    task: how do I decide whether to switch model families or improve task accuracy to get
      more stable LLM answers?
    practitioner: if two models have the same accuracy on my task, will they be equally consistent
      across prompt variants?
  answered_by:
  - model-factors-weak
  - torr-cross-family
- ask:
    plain: is it worth building separate tests just for how sensitive language models are
      to prompt wording?
    jargon: what work argues that LLM robustness is a concomitant of task competence rather
      than a separate capability to benchmark?
    task: where should I start reading before designing a robustness evaluation for language
      models?
    practitioner: should I invest in a dedicated prompt-robustness benchmark, or expect robustness
      to arrive as accuracy climbs?
  answered_by:
  - reframing-robustness
  - perf-explains-robustness
- ask:
    plain: which kinds of tasks can a language model actually be trusted on for important
      decisions?
    jargon: can very high benchmark accuracy serve as an empirical indicator of stable LLM
      behaviour under prompt variation?
    task: how do I choose which tasks to hand a language model in a sensitive application?
    practitioner: my use case is high-stakes, so should I pick a task where models are already
      near-saturated rather than a frontier benchmark?
  answered_by:
  - deployment-signal
  - imdb-saturated-robust
- ask:
    plain: does the link between accuracy and answer consistency still show up if consistency
      is measured a different way?
    jargon: does performance drop rate or per-example score standard deviation reproduce the
      trend found with strict output consistency?
    task: how do I check that LLM robustness conclusions are not an artefact of the consistency
      metric I chose?
    practitioner: which robustness metric should I report for my LLM, strict output agreement
      or a score-based drop rate?
  answered_by:
  - metrics-agree
  - long-tail-consistency
  - torr-correlation
- ask:
    plain: do the number of examples shown to a language model or its temperature setting
      change measured accuracy much?
    jargon: what effect sizes does an ANOVA over demonstration count, prompt variation, template
      and temperature yield on LLM benchmark scores?
    practitioner: should I spend time tuning prompt template and temperature, or will it barely
      move my benchmark score?
  answered_by:
  - config-choices-minor
- ask:
    plain: is any one kind of prompt change, like paraphrasing or adding random characters,
      especially hard for language models?
    jargon: is there a dominant perturbation type in LLM prompt-sensitivity evaluations, or
      do perturbations act as generic noise?
    task: how do I pick which prompt perturbations to include in an LLM robustness test?
  answered_by:
  - perturbations-as-noise
  - config-choices-minor
- ask:
    plain: could language models having seen benchmark data in training explain why they answer
      reworded prompts the same way?
    jargon: does benchmark contamination account for observed output consistency across prompt
      configurations?
    practitioner: should I discount high prompt-consistency results on public benchmarks as
      a contamination effect?
  answered_by:
  - perturbations-as-noise
  - beats-random-baseline
- ask:
    plain: do accuracy numbers re-measured for Llama 4 and gpt-oss in a prompt-consistency
      study match published scores?
    jargon: how were re-measured MMLU and MMLU-Pro scores validated against model cards and
      the HELM capabilities leaderboard?
    practitioner: can I trust model scores in a robustness study that re-ran the benchmarks
      itself?
  answered_by:
  - external-validation
terminology:
  Output Consistency: 'A robustness measure: the fraction of dataset examples for which a
    model produces equivalent predictions under every inference configuration tested, computed
    from outputs rather than scores.'
  Inference Configuration: One meaning-preserving way of presenting the same example to a
    model, combining a prompt paraphrase, a number of in-context demonstrations, a noise perturbation
    and a decoding temperature, under which an identical output is expected.
  Random baseline consistency: The probability that a model answers an example consistently
    across all configurations if each configuration succeeded independently with probability
    equal to the model's overall accuracy on the dataset.
  Performance Drop Rate (PDR): The average relative decrease in score when a model is evaluated
    on perturbed inputs compared with the original input; higher values indicate greater sensitivity
    to perturbations.
  Success consistency versus failure consistency: The distinction between producing the same
    correct answer across all configurations and merely having zero score variance, since
    consistent failure can come from differing wrong answers and is not evidence of robust
    behaviour.
misreadings:
- The finding is an association between task performance and output consistency, not a demonstration
  that raising accuracy causally produces robustness; no training-time intervention was tested.
- 'Robustness emerging with performance does not mean current frontier benchmarks are safe
  to rely on: on MMLU-Pro, RewardBench and GPQA the evaluated models are far from saturated
  and correspondingly inconsistent.'
- 'Model-level factors being comparatively weak does not make models interchangeable: gpt-oss-120b
  reaches 78% robustness on BoolQ against 56% for gpt-oss-20b at nearly identical accuracy.'
- The dedicated experiments are classification tasks scored by exact match; evidence for generative
  tasks comes only from existing ToRR table-reasoning leaderboard results, not from new experiments.
- No closed-source models were run in the dedicated experiments, so those results are not
  a statement about proprietary frontier systems.
- The robustness studied is to lightweight meaning-preserving prompt perturbations; it does
  not extend to strong adversarial attacks, non-meaning-preserving shifts or tool use.
---
