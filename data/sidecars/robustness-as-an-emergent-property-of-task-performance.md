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
    unsorted:
    - Does higher benchmark accuracy make an LLM more consistent under prompt variations?
    - How strongly is LLM robustness correlated with task performance?
    - Is prompt sensitivity just a symptom of low accuracy?
  answered_by:
  - perf-explains-robustness
  - imdb-saturated-robust
- ask:
    unsorted:
    - Is high consistency on an easy benchmark just an artifact of high accuracy?
    - How is trivial robustness from high success rates ruled out when comparing consistency
      to accuracy?
    - What random baseline is used for output consistency across prompt variations?
  answered_by:
  - beats-random-baseline
  - imdb-saturated-robust
- ask:
    unsorted:
    - Are some language models inherently more robust than others?
    - Does LLM output consistency depend on which model is used or on how well it performs
      the task?
    - Do bigger models in the same family show better prompt consistency at equal accuracy?
  answered_by:
  - model-factors-weak
  - reframing-robustness
- ask:
    practitioner: Where should I start reading on the relationship between benchmark saturation
      and LLM reliability?
    unsorted:
    - Should researchers keep building dedicated robustness benchmarks for LLMs?
    - What is a good paper arguing robustness will emerge as benchmarks saturate?
  answered_by:
  - reframing-robustness
  - perf-explains-robustness
- ask:
    practitioner: Can I use benchmark accuracy as a signal that a model is ready for deployment?
    unsorted:
    - Which tasks are LLMs actually reliable on for high-stakes use?
    - Does strong performance on a task predict stable behavior in production?
  answered_by:
  - deployment-signal
  - imdb-saturated-robust
- ask:
    unsorted:
    - How many models, datasets and prompt configurations were tested?
    - What is the experimental scale of the robustness-versus-performance analysis?
    - Which benchmarks and perturbations were used to measure output consistency?
  answered_by:
  - study-scale
  - config-choices-minor
- ask:
    unsorted:
    - Do the conclusions depend on which robustness metric is used?
    - Does performance drop rate show the same trend as strict output consistency?
    - Are score-based and output-based robustness measures consistent with each other?
  answered_by:
  - metrics-agree
  - long-tail-consistency
- ask:
    unsorted:
    - Do choices like number of few-shot demonstrations or temperature drive the reported
      results?
    - Was a statistical test run on whether configuration parameters affect accuracy?
    - How much does prompt variation change measured performance on MMLU or RewardBench?
  answered_by:
  - config-choices-minor
- ask:
    unsorted:
    - Are the accuracy numbers in this robustness study consistent with published leaderboards?
    - How were the measured MMLU-Pro and GPQA scores sanity-checked?
    - Do the reported model scores match HELM and model cards?
  answered_by:
  - external-validation
- ask:
    unsorted:
    - Could benchmark contamination explain the high consistency across prompt variants?
    - How is data contamination addressed in the performance-robustness analysis?
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
