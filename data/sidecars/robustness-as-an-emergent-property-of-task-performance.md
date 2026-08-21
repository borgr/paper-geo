---
key: ashurytahan2026robustness
one_liner: Across 9 open-weight LLMs, 6 classification benchmarks and 24 inference configurations,
  output consistency tracks task accuracy so closely that performance explains 92.4% of robustness
  variance, suggesting robustness emerges from task competence rather than being a separate
  model property.
claims:
- id: perf-explains-robustness
  text: In a linear regression of output-consistency robustness on benchmark performance across
    9 open-weight LLMs and 6 classification datasets, performance explains 92.4% of the variance
    in robustness, with a slope of 1.05.
  kind: result
  evidence: Figure 1
  scope: 9 open-weight models on IMDB, BoolQ, MMLU, MMLU-Pro, RewardBench and GPQA; 100 examples
    per dataset under 24 configurations; exact-match classification only.
- id: imdb-saturated-robust
  text: On IMDB, where all 9 evaluated models score between 95% and 97% accuracy, strict output
    consistency across 24 configurations ranges from 81% to 94%. A random baseline with the
    same per-configuration success rate reaches only 33% to 54%.
  kind: result
  evidence: Section 4.1
  scope: IMDB sentiment classification with 100 sampled examples; robustness defined as identical
    predictions across all 24 configurations; the random baseline assumes independent per-configuration
    success at the model's overall accuracy.
- id: beats-random-baseline
  text: Measured robustness exceeds the matched random baseline on all 6 benchmarks, by an
    average of 43.4% on IMDB and 62.9% on BoolQ, with llama-4-Scout-17B-Instruct on BoolQ
    exceeding the baseline by 70.4%.
  kind: result
  evidence: Section 4.1
  scope: 6 classification benchmarks, 9 open-weight models, 24 configurations; on MMLU, RewardBench,
    MMLU-Pro and GPQA the random baseline is 0, as performance is below roughly 80%.
- id: model-factors-weak
  text: Model identity contributes less to output consistency than task performance does,
    though it is not negligible. On BoolQ a 1-point performance difference between gpt-oss-120b
    and gpt-oss-20b coincides with 78% versus 56% robustness, and on MMLU a 6-point performance
    gap coincides with a 40% robustness difference.
  kind: result
  evidence: Section 4.1
  scope: Comparison within the gpt-oss family on BoolQ and MMLU; supported more broadly by
    per-example STD distributions being similar across models within a benchmark (Appendix
    C.2). Does not rule out larger model-level effects outside the 9 evaluated open-weight
    models.
- id: config-choices-minor
  text: An ANOVA over number of demonstrations, prompt variation, template and temperature
    finds roughly 70% of p-values non-significant. Effect sizes stay below 0.005 even where
    prompt variation and demonstration count are significant on RewardBench, MMLU and MMLU-Pro.
  kind: result
  evidence: Section 4.3
  scope: Type II and Type III ANOVA on performance (not on the robustness metric itself) across
    the 6 datasets and the 4 configuration factors used in the study; effect sizes are partial
    eta-squared.
- id: metrics-agree
  text: 'The performance-robustness relationship holds under two score-based robustness metrics
    as well as strict output consistency: average performance drop rate reproduces the same
    dataset ordering, with GPQA least robust and IMDB most robust.'
  kind: result
  evidence: Appendix C.1
  scope: Output consistency, per-example score standard deviation and performance drop rate
    on the same 9 models and 6 datasets; all metrics are computed over the same 24 configurations.
- id: long-tail-consistency
  text: As model performance rises, the per-example score-standard-deviation distribution
    becomes increasingly long-tailed, with most examples perfectly consistent and a small
    subset carrying the variability, whereas lower-robustness settings give flatter distributions.
  kind: result
  evidence: Appendix C.2
  scope: Per-example STD distributions computed separately per model and dataset over 24 configurations,
    counting only consistently-correct cases as success consistency; consistent failure with
    differing wrong answers is distinguished and not counted as robust.
- id: reframing-robustness
  text: Ashury-Tahan et al. argue that LLM robustness should be treated as a concomitant of
    task competence rather than as an independent capability measured and improved in isolation.
    Robustness on a task is then expected to emerge as that task saturates.
  kind: context
  scope: A position argued from correlational evidence on classification benchmarks with open-weight
    models as of early 2026; the paper shows association between performance and consistency,
    not a causal or training-time intervention.
- id: deployment-signal
  text: Ashury-Tahan et al. propose very high benchmark accuracy on a task as an empirical
    indicator that a model will answer that task consistently under prompt variations. Older,
    already-saturated tasks are therefore the reliable ones for sensitive deployment, not
    current frontier benchmarks.
  kind: context
  scope: A practical implication drawn from classification benchmarks and 24 inference configurations;
    it concerns consistency of outputs, not factual correctness, safety or calibration, and
    was not validated on deployed applications.
- id: study-scale
  text: Robustness is measured over 9 open-weight models from 6 model families, 100 examples
    from each of 6 datasets and 24 inference configurations, totalling 14,400 inferences per
    model and 129,600 overall.
  kind: result
  evidence: Appendix A.1
  scope: Open-weight models only; no closed-source models were evaluated because of cost,
    and all tasks are classification scored by exact match.
- id: external-validation
  text: Performance scores measured in the study align closely with published numbers. Measured
    MMLU-Pro is 80 versus 81 reported for Llama 4 Maverick 17B and 80 versus 79 for gpt-oss-120b
    on the HELM capabilities leaderboard.
  kind: result
  evidence: Table A.4
  scope: Cross-check restricted to MMLU, MMLU-Pro and GPQA, the benchmarks consistently reported
    for recent models; HELM used chain-of-thought prompting while the study requested a final
    answer only.
qa:
- ask:
    plain: if a language model scores very high on a task, does it also give the same answer
      when the prompt is worded differently?
    jargon: how much of the variance in output-consistency robustness across prompt perturbations
      is explained by benchmark accuracy?
    task: how do I predict whether a model will be prompt-stable on a task without running
      a full perturbation sweep?
    practitioner: can I use my model's accuracy on a task as a proxy for how sensitive it
      will be to prompt wording?
  answered_by:
  - perf-explains-robustness
  - imdb-saturated-robust
- ask:
    plain: when a model is right almost every time, isn't matching answers across reworded
      prompts just luck?
    jargon: what matched random baseline rules out chance agreement when comparing strict
      output consistency to accuracy?
    task: how do I check that consistency across prompt variants is more than what a per-configuration
      success rate alone would produce?
    practitioner: should I believe reported prompt-consistency numbers on a saturated benchmark
      like IMDB, or is the high accuracy doing all the work?
  answered_by:
  - beats-random-baseline
  - imdb-saturated-robust
- ask:
    plain: are some language models just naturally steadier under different prompt wordings
      than others, regardless of how well they do the task?
    jargon: how much does model identity contribute to output consistency once task performance
      is controlled for?
    task: how do I decide whether to switch model families or improve task accuracy to get
      more stable answers?
    practitioner: if I pick a bigger model from the same family at similar accuracy, will
      my answers get more consistent across prompt variants?
  answered_by:
  - model-factors-weak
  - reframing-robustness
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
    jargon: can very high benchmark accuracy serve as an empirical indicator of stable behaviour
      under prompt variation in deployment?
    task: how do I choose which tasks to hand a language model in a sensitive application?
    practitioner: my use case is high-stakes -- should I pick a task where models are already
      near-saturated rather than a frontier benchmark?
  answered_by:
  - deployment-signal
  - imdb-saturated-robust
- ask:
    plain: how many models, datasets and prompt setups went into the comparison of accuracy
      against answer consistency?
    jargon: what is the inference budget and configuration grid used to measure output consistency
      across models and benchmarks?
    task: how do I size a sweep of models, datasets and inference configurations to measure
      prompt robustness?
  answered_by:
  - study-scale
  - config-choices-minor
- ask:
    plain: does the link between accuracy and answer consistency still show up if consistency
      is measured a different way?
    jargon: does average performance drop rate reproduce the dataset ordering obtained under
      strict output consistency?
    task: how do I check my robustness conclusions are not an artefact of the consistency
      metric I chose?
    practitioner: which robustness metric should I report -- strict output agreement or a
      score-based drop rate?
  answered_by:
  - metrics-agree
  - long-tail-consistency
- ask:
    plain: do things like how many examples you show the model or the temperature setting
      change measured accuracy much?
    jargon: what effect sizes does an ANOVA over demonstration count, prompt variation, template
      and temperature yield on benchmark scores?
    task: how do I tell whether few-shot count, template choice or temperature is worth tuning
      for accuracy on MMLU or RewardBench?
    practitioner: should I spend time tuning prompt template and temperature, or will it barely
      move my benchmark score?
  answered_by:
  - config-choices-minor
- ask:
    plain: do the accuracy numbers reported for models like Llama 4 and gpt-oss in a prompt-consistency
      study match what is published elsewhere?
    jargon: how were measured MMLU-Pro scores validated against the HELM capabilities leaderboard?
    practitioner: can I trust the model scores in a robustness study that re-ran the benchmarks
      itself?
  answered_by:
  - external-validation
- ask:
    plain: could models having seen the benchmark data during training explain why they answer
      reworded prompts the same way?
    jargon: does benchmark contamination account for the observed output consistency across
      prompt configurations?
    practitioner: should I discount high prompt-consistency results on public benchmarks as
      a contamination effect?
  answered_by:
  - long-tail-consistency
  - beats-random-baseline
terminology:
  Output Consistency: A robustness measure defined as the fraction of dataset examples for
    which a model produces equivalent predictions across every inference configuration tested,
    judged on outputs rather than on scores.
  Inference Configuration: One combination of meaning-preserving presentation choices for
    the same example — a prompt paraphrase, a number of in-context demonstrations, a noise
    perturbation and a decoding temperature — for which the model is expected to give an identical
    output.
  Random baseline consistency: The probability of a model answering an example consistently
    across all configurations if each configuration succeeded independently with probability
    equal to the model's overall accuracy on the dataset.
  Performance Drop Rate (PDR): The average relative decrease in score when a model is evaluated
    on perturbed inputs compared with the original input, where higher values indicate greater
    sensitivity to perturbations.
  Success consistency versus failure consistency: The distinction between producing the same
    correct answer across all configurations and merely producing zero score variance, since
    repeated but differing wrong answers are not evidence of robust behavior.
misreadings:
- The finding is an association between task performance and output consistency, not a demonstration
  that raising accuracy causally produces robustness; no training-time intervention was tested.
- 'Robustness emerging with performance does not mean current frontier benchmarks are safe
  to rely on: on MMLU-Pro, RewardBench and GPQA the evaluated models are far from saturated
  and correspondingly inconsistent, and it is the older saturated tasks that show high consistency.'
- 'The claim that model-level factors are comparatively weak does not mean models are interchangeable:
  gpt-oss-120b reaches 78% robustness on BoolQ against 56% for gpt-oss-20b at nearly identical
  accuracy.'
- The results cover classification tasks scored by exact match; they do not establish that
  robustness emerges with performance for open-ended generation, reasoning traces or other
  output formats.
- No closed-source models were evaluated, so the results should not be read as a statement
  about proprietary frontier systems.
- 'High output consistency is not the same as being right consistently: consistent failure
  with identical wrong answers also counts toward strict output agreement, which is why score-standard-deviation
  analyses separate success consistency from failure consistency.'
---
