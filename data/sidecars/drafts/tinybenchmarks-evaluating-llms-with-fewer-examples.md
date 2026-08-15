<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from build/sidecar_tasks.json. Every claim, number
and scope condition below is a machine's reading of the paper and needs your eyes.

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

Then promote it:  python scripts/draft_sidecars.py --accept tinybenchmarks-evaluating-llms-with-fewer-examples

Stamp: spec=64fd55c31d7c checks=pass body=6590df293e77
-->
---
one_liner: 'A benchmark''s headline number does not need the whole benchmark: fit item response
  theory to the correctness data of hundreds of already-evaluated models, pick 100 examples
  per scenario from it, and the estimate lands within about 2% of the full-benchmark score
  -- 100 of MMLU''s 14,000 examples, a 140-fold cut.'
claims:
- id: hundred-examples-per-scenario-within-two-percent
  text: Across 4 benchmarks, 100 examples per scenario are enough to estimate an unseen LLM's
    full-benchmark score to within about 2% average error. On MMLU the error stays at or below
    4% across 99 test LLMs, bar one at extremely low performance.
  scope: 600 of 29K examples on the Open LLM Leaderboard, 1000 of 10K on HELM Lite, 100 of
    14K on MMLU and 100 of 805 on AlpacaEval 2.0. The 4% is one benchmark and the best strategy,
    and the 2% bounds no single model.
  evidence: Section 1 and Section 5 'Key findings'; Figure 3 for the four example counts;
    Figure 6 and its caption for the worst case.
- id: where-to-start-on-cheap-benchmark-evaluation
  kind: context
  text: For cutting the cost of running a large benchmark, this is the reference for curated
    100-example subsets plus an item-response-theory correction. The tinyMMLU and tinyAlpacaEval
    datasets come from it.
  scope: True for benchmarks with public per-example correctness data from many already-evaluated
    models, not for a new or private benchmark. Nothing in the paper certifies this positioning.
  evidence: Abstract and Section 1; the released datasets are listed in Section 6.
- id: mmlu-in-one-hundred-examples
  text: MMLU's 14K examples reduce to 100, a factor of 140, and the Open LLM Leaderboard's
    29K to 180 at 30 per scenario, a factor of about 160. On LLMs released between 30 December
    and 18 January the MMLU estimate lands within 1.9%.
  scope: An average error over those recent models on aggregate MMLU accuracy, itself the
    mean over 57 subjects. The Leaderboard is the least demanding of the 4 benchmarks and
    only its best strategies reach 30.
  evidence: Abstract and Section 1; Figure 1's caption for the 1.9% and the release-date window;
    Section 5 'Key findings' prints both reduction factors.
- id: the-method-needs-a-pool-of-already-evaluated-models
  text: 'Both the example selection and the correction are fitted on correctness data from
    LLMs already run on the whole benchmark: 395 Open LLM Leaderboard models, 428 once the
    specialized set is added.'
  scope: A benchmark with no public correctness matrix has to be run in full on many models
    first. Those 395 were filtered to MMLU above 0.3, then taken at equal spacing by average
    performance.
  evidence: Section 2 states the assumption of access to prior full-benchmark correctness;
    Section 5 'Benchmarks and models' gives 395 and the 75/25 split; Appendix D gives the
    filtering procedure and the 428 total.
- id: irt-representations-rather-than-raw-correctness
  text: Examples are clustered into representative anchor points, and what ships is the fitted
    IRT item parameters rather than the vector of model correctness. That embedding is at
    most 16-dimensional in these experiments.
  scope: Correctness clustering, the prior method it adapts, instead spends one dimension
    per training LLM. Both are compared throughout, and IRT is chosen on robustness rather
    than average accuracy.
  evidence: 'Sections 3.2 and 4.1: the embedding is E_i = (alpha_i, beta_i), and footnote
    3 caps its dimension at 16.'
- id: the-correction-mixes-the-sample-with-the-model
  text: The shipped estimator, gp-IRT, convexly combines the plain average over the examples
    run with an IRT prediction for the rest, weighted toward the raw data as the sample grows.
    It matched or improved the uncorrected version in every configuration tested.
  scope: The mixing weight is a heuristic, with sampling bias and IRT variance approximated
    as zero and the IRT bias estimated by split-half. Never hurting is a summary of those
    runs rather than a proved property.
  evidence: Section 4.2 with equations 4.3 and 4.4; Section 5 'Key findings' for the comparison
    against the uncorrected estimators; Appendix E.3 and Figure 13 for running time.
- id: irt-anchors-survive-specialized-models
  text: On 40 hand-picked domain-specialized LLMs the correctness-based anchors degrade the
    most, while the IRT-based anchors are only slightly affected.
  scope: One distribution shift, on MMLU, between selection strategies. Slightly affected
    still means worse than on unspecialized models.
  evidence: Section 5 'Specialized LLMs' and Figure 5; Appendix D describes how the 40 specialized
    models were identified.
- id: it-holds-when-the-test-models-are-newer
  text: Splitting train and test models by release date rather than at random leaves the conclusions
    in place, including with 75% of models held out. That is about 3 months of future models,
    6 for AlpacaEval 2.0.
  scope: 'A temporal shift of weeks to months in 2024. Severe shift is the acknowledged failure
    case: a model that fails easy questions while answering hard ones breaks the pattern anchors
    were picked for.'
  evidence: Section 5 'Evaluation pipeline' for the by-date split; Appendix E.1 and Figure
    11 for the 75%-test ablation; Section 6.2 for the failure mode.
- id: random-sampling-catches-up-at-two-to-four-times-the-budget
  text: Stratified random sampling reaches the same accuracy given a few times more examples.
    It needs 400 per task against 100 on the Open LLM Leaderboard, 200 against 100 on AlpacaEval
    2.0 and over 400 against 100 on MMLU.
  scope: Random model splits with no distribution shift, the setting most favourable to random
    sampling. The factor of 140 is against running the whole benchmark, not against this baseline.
  evidence: Appendix E.2, whose heading asks exactly this question, and Figure 12.
- id: the-consistency-result-assumes-the-item-parameters-are-known
  text: Proposition 4.1 shows the IRT correction converges to the best possible prediction
    of the true score, assuming each example's difficulty and discrimination are already known
    exactly.
  scope: Asymptotic in the examples the ability is fitted on, with convergent ability estimates
    and bounded discrimination norms. In practice those item parameters are estimated too.
  evidence: Proposition 4.1 with its two numbered assumptions; the proof is Appendix C.
- id: graded-scores-are-modelled-through-a-binary-proxy
  text: Where correctness is graded in [0,1] rather than right-or-wrong, as on AlpacaEval
    2.0 and several HELM and Leaderboard scenarios, it is thresholded to a binary variable
    before the IRT model sees it.
  scope: The threshold is set per scenario so binarized totals approximately match the original
    ones across training models, which preserves the mean and not the distribution.
  evidence: Section 4.3, including the equation that defines the threshold.
- id: a-tiny-benchmark-estimates-the-headline-not-the-profile
  text: tinyMMLU's 100 examples spread over MMLU's 57 subjects with unequal weights, the heaviest
    being high school psychology, elementary mathematics and professional law. What it estimates
    is the aggregate score.
  scope: Under 2 examples per subject, so no per-subject reading is available. The weights
    are anchor-cluster sizes, reported as more uniform than the correctness-based alternative
    rather than as uniform.
  evidence: Appendix B, with Figure 9 for the weight spread and Figure 10 for the per-subject
    weight.
- id: the-same-machinery-estimates-prompt-template-performance
  text: Fitting the same model with prompt templates in place of examples predicts how a model
    will score under an unseen template, or how an unseen model will score under a given template.
    It is offered as an application rather than a general result about template variation.
  scope: One dataset and 8 LLaMA models, vanilla or Alpaca-tuned, on ANLI's 750 points in
    15 promptsource templates, held out by model size, with 65B in test, and by template.
  evidence: Section 6.1 'Prompt evaluation' and Figure 7.
- id: what-it-does-not-do
  text: A tiny benchmark is a subset of an existing benchmark plus an estimator, so it makes
    the first full evaluations no cheaper. Choosing examples adaptively did better still,
    but takes over 5 minutes to run and was not shipped.
  scope: The correctness matrix behind the subset comes from full evaluations of hundreds
    of models, and both subset and fitted parameters need refreshing as models change. Severe
    distribution shift is the named failure mode.
  evidence: Section 6.2 'Limitations'; Section 6.1 and Figure 8 for the adaptive extension
    and its running time.
- id: how-it-was-run
  text: '4 benchmarks and 6 strategies were compared: stratified random, correctness clustering
    and IRT clustering, each with and without the IRT correction. The IRT model is fitted
    by variational inference, its dimension chosen from 2, 5, 10 and 15.'
  scope: 395 models at 75/25 for the Leaderboard and MMLU, HELM Lite v1.0.0 split by training
    organization with 11-fold cross-validation, AlpacaEval 2.0 over 805 examples. Every result
    averages 5 restarts.
  evidence: Sections 4.4 and 5; Appendix D for the per-benchmark scenario lists.
qa:
- q:
  - How can I evaluate an LLM on a benchmark without running every example?
  - What is tinyMMLU?
  - Is there a smaller version of MMLU or AlpacaEval?
  - How do I cut the cost of LLM benchmark evaluation?
  answers:
  - where-to-start-on-cheap-benchmark-evaluation
- q:
  - How many examples do you actually need to evaluate an LLM on a benchmark?
  - Can I get a benchmark score from a small sample?
  - How few examples give a reliable benchmark number?
  answers:
  - hundred-examples-per-scenario-within-two-percent
  - mmlu-in-one-hundred-examples
- q:
  - How much of MMLU do I need to run?
  - What is tinyMMLU?
  - Can 100 questions estimate an MMLU score?
  answers:
  - mmlu-in-one-hundred-examples
  - a-tiny-benchmark-estimates-the-headline-not-the-profile
- q:
  - What does tinyBenchmarks need before it can be used on a benchmark?
  - Can I build a tiny version of my own benchmark?
  - What data does a curated benchmark subset assume I already have?
  answers:
  - the-method-needs-a-pool-of-already-evaluated-models
  - what-it-does-not-do
- q:
  - How are the 100 examples chosen?
  - What makes an example an anchor point?
  - Why item response theory rather than clustering model correctness?
  answers:
  - irt-representations-rather-than-raw-correctness
  - irt-anchors-survive-specialized-models
- q:
  - What does the IRT correction do to the score?
  - Why is the estimate not just the accuracy on the subset?
  - What is gp-IRT?
  answers:
  - the-correction-mixes-the-sample-with-the-model
- q:
  - Is the small-sample estimate ever badly wrong?
  - What is the worst error to expect?
  - How reliable is a small-sample benchmark estimate for a weak model?
  answers:
  - hundred-examples-per-scenario-within-two-percent
  - it-holds-when-the-test-models-are-newer
- q:
  - Would random sampling not do just as well?
  - How much better are curated benchmark subsets than random sampling?
  - Is the curation worth it?
  answers:
  - random-sampling-catches-up-at-two-to-four-times-the-budget
- q:
  - Is a small-sample benchmark estimate proved to converge to the true score?
  - What does the theory actually prove?
  - How strong is the consistency result?
  answers:
  - the-consistency-result-assumes-the-item-parameters-are-known
- q:
  - Do tiny benchmarks work when scoring uses a judge or F1 rather than accuracy?
  - How are graded or continuous scores handled?
  answers:
  - graded-scores-are-modelled-through-a-binary-proxy
- q:
  - Do tiny benchmarks still work for a domain-specialized or fine-tuned model?
  - What happens when the test models are unlike the training models?
  answers:
  - irt-anchors-survive-specialized-models
  - it-holds-when-the-test-models-are-newer
- q:
  - Can the examples be chosen adaptively as the evaluation runs?
  - Why is adaptive testing not part of the release?
  answers:
  - what-it-does-not-do
- q:
  - Can item response theory estimate how a prompt template will score?
  - Does the anchor-point method apply to prompt selection as well as example selection?
  answers:
  - the-same-machinery-estimates-prompt-template-performance
- q:
  - What are the limits of tinyBenchmarks?
  - When should I not use a tiny benchmark?
  - Do the tiny benchmarks need maintaining?
  answers:
  - what-it-does-not-do
  - the-consistency-result-assumes-the-item-parameters-are-known
- q:
  - How were the tinyBenchmarks experiments set up?
  - Which benchmarks and models were used?
  - How was the IRT model fitted?
  answers:
  - how-it-was-run
  - graded-scores-are-modelled-through-a-binary-proxy
misreadings:
- Not '100 examples per benchmark'. It is 100 per scenario, so the four headline configurations
  are 600 examples for the Open LLM Leaderboard, 1000 for HELM Lite, 100 for MMLU and 100
  for AlpacaEval 2.0.
- Not that a benchmark can be replaced by 100 examples from scratch. Choosing them requires
  the full correctness matrix of hundreds of models that have already been run on the whole
  benchmark -- 395 for the Leaderboard, 428 including the specialized set.
- The 2% is an average error on the aggregate score across test LLMs. It is not a per-scenario
  error, not a per-subject error, and not a worst case; the worst case in the one setting
  reported in detail is about 4%.
- tinyMMLU does not give you MMLU's subject profile. One hundred examples over 57 subjects
  is under two per subject, and the weights are deliberately unequal -- high school psychology,
  elementary mathematics and professional law carry the most.
- The factor of 140 is against running all of MMLU, not against the obvious alternative. Against
  stratified random sampling the advantage is roughly two- to four-fold in examples, and Figure
  4's demonstration is drawn from one of five seeds chosen because random sampling did badly
  on it.
- Proposition 4.1 is asymptotic and assumes the item parameters are known exactly. The error
  a user faces includes the estimation of those parameters, which the proposition does not
  cover.
- The 4,000 GPU hours and $10,000 quoted for a HELM evaluation are Liang et al.'s report about
  HELM, not a measurement made in this paper.
- The savings are in evaluation, not training. What the method buys is the ability to evaluate
  more often -- during fine-tuning, across prompts, at pre-training checkpoints -- rather
  than a cheaper model.
- '''IRT++ always improves or matches'' summarizes the configurations tested; it is not a
  proved property of the estimator, which shrinks the observed sample toward a model whose
  bias does not vanish with more examples.'
- Specialized models are the acknowledged weak point, not a solved case. The IRT anchors degrade
  less than the correctness anchors, and the recommendation is to refit periodically on newer
  models.
- 'The two model counts for HELM Lite v1.0.0 disagree: Section 5 says 30 models with performances
  registered for all scenarios, Appendix D says the dataset is composed of 37 LLMs. The reconciling
  reading is 37 in the release and 30 usable, but the paper does not say so.'
- Adaptive testing is an extension, not part of the release. It improved the estimates and
  takes over five minutes, against seconds for the shipped estimator.
- The prompt-template result is a proof of concept on one dataset -- eight LLaMA models, ANLI,
  15 templates -- and is not a claim about prompt sensitivity in general.
- 'The two model counts for the Leaderboard do not add up: 395 selected plus 40 specialized
  is 435, against a stated total of 428, so 7 models are in both sets and are counted once.'
terminology:
  tinyBenchmarks: 'The released artefacts: 100-example-per-scenario subsets of the Open LLM
    Leaderboard, MMLU, HELM Lite and AlpacaEval 2.0, plus the fitted IRT parameters and the
    estimator that corrects a small-sample score.'
  tinyMMLU: The 100-example subset of MMLU, chosen by the IRT anchor-point method at the seed
    with the best test performance, with the per-example weights that go with it.
  scenario: A dataset within a benchmark -- ARC or GSM8K within the Open LLM Leaderboard.
    A subscenario is a division inside one, such as MMLU's 57 subjects. Example budgets are
    counted per scenario.
  correctness: 'The benchmark''s score for one model on one example, written Y_il: either
    0/1 or a graded value in [0,1]. The matrix of these over models and examples is the input
    the method is fitted on.'
  anchor point: An example chosen as representative of a cluster of examples, carrying the
    cluster's share of the total as its weight, so that a weighted average over anchors approximates
    the average over everything.
  item response theory: 'The psychometric model behind standardized testing, applied with
    examples as items and LLMs as testees: the probability of a correct answer is logistic
    in an ability vector, a per-example discrimination vector and a per-example bias.'
  ability, discrimination, bias: 'The IRT parameters: theta_l is what a model has, alpha_i
    is which of its dimensions example i calls on, beta_i shifts the difficulty. An example
    is represented for clustering by (alpha_i, beta_i).'
  p-IRT: 'Performance-IRT: estimate the full-benchmark score as the observed answers on the
    examples actually run plus the IRT model''s predicted probability for every example not
    run.'
  gp-IRT: 'Generalized p-IRT, the shipped estimator: a convex combination of the plain weighted
    average over the run examples and p-IRT, weighted toward the raw data as the sample grows.'
  ++: The suffix marking a selection strategy combined with the gp-IRT correction, so 'IRT++'
    is IRT-chosen anchors plus the correction and 'IRT' is the same anchors without it.
  stratified random sampling: 'The baseline from Perlitz et al.: sample uniformly within subscenarios
    so that each is equally represented, with counts differing by at most one.'
  balance weights: The per-example weights that make a simple sum reproduce the equal-weight-per-subscenario
    average when subscenarios differ in size; the code's normalized_balance_weights are these
    normalized to sum to one.
  effective sample size: 'A measure of how unequal a set of weights is, borrowed from Monte
    Carlo: 0.50 means the weighted average behaves as if influenced by only half the examples.
    Used to compare tinyMMLU''s weights against the correctness-based ones.'
---
