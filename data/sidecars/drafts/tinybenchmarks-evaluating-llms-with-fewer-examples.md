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
-->
---
one_liner: 'A benchmark''s headline number does not need the whole benchmark: fit item response
  theory to the correctness data of hundreds of already-evaluated models, pick 100 examples
  per scenario from it, and the estimate lands within about 2% of the full-benchmark score
  -- 100 of MMLU''s 14,000 examples, a 140-fold cut.'
coined: tinyBenchmarks
gloss: Released 100-example-per-scenario subsets of the Open LLM Leaderboard, MMLU (tinyMMLU),
  HELM Lite and AlpacaEval 2.0, chosen by clustering item response theory representations
  of examples, shipped with the fitted IRT parameters and a CPU-only estimator that corrects
  the small-sample score.
claims:
- id: hundred-examples-per-scenario-within-two-percent
  text: Across four benchmarks, 100 examples per scenario are enough to estimate an unseen
    LLM's full-benchmark performance to within about 2% average error.
  scope: 'Per scenario, not per benchmark: the same claim is 600 of 29K examples on the six-scenario
    Open LLM Leaderboard, 1000 of 10K on HELM Lite''s ten, 100 of 14K on MMLU and 100 of 805
    on AlpacaEval 2.0. The 2% is an average over test LLMs of the error in the aggregate score,
    not a bound on any single model and not an error on any component scenario. Results are
    averaged over 5 restarts.'
  evidence: Section 1 and Section 5 'Key findings'; Figure 3 and its caption give the four
    example counts.
- id: mmlu-in-one-hundred-examples
  text: MMLU's roughly 14,000 examples reduce to 100, a factor of 140, and on LLMs released
    between 30 December and 18 January the estimate is within 1.9% of the true full-MMLU accuracy.
  evidence: Abstract and Section 1; the 1.9% and the release-date window are Figure 1's caption.
    14000/100 = 140 as printed.
  scope: The 1.9% is the average error over that set of recent models on the aggregate MMLU
    accuracy. MMLU is treated as one scenario whose score is the average over its 57 subjects,
    so 100 examples is under two per subject.
- id: thirty-examples-suffice-on-the-leaderboard
  text: On the Open LLM Leaderboard 30 examples per scenario are already enough -- 180 of
    29,000 examples, a factor of about 160.
  scope: 'One benchmark, and the least demanding of the four: MMLU on its own still wants
    100. Stated for the best-performing strategies, and the aggregate Leaderboard score is
    an average of six scenario accuracies, which averages six independent errors down.'
  evidence: Section 5 'Key findings', which prints both the factor and the 29K-to-180 reduction.
- id: the-method-needs-a-pool-of-already-evaluated-models
  text: 'The example selection and the correction both come from correctness data for LLMs
    already evaluated on the entire benchmark: 395 models from the Open LLM Leaderboard, 428
    in total once the specialized set is added.'
  scope: This is the precondition, and it is what the paper's savings are measured against
    rather than included in. A benchmark with no such public correctness matrix has to be
    run in full on many models before any of this applies. 395 + 40 specialized = 435 against
    a stated total of 428, so 7 models are in both sets (my arithmetic on their two counts).
    Leaderboard data was downloaded in January 2024 and models were selected by filtering
    to MMLU above 0.3, ordering by average performance and taking equally spaced models --
    not a random sample of the leaderboard.
  evidence: Section 2 states the assumption of access to prior full-benchmark correctness;
    Section 5 'Benchmarks and models' gives 395 and the 75/25 split; Appendix D gives the
    filtering procedure and the 428 total.
- id: irt-representations-rather-than-raw-correctness
  text: Examples are clustered to find representative 'anchor points', and the embedding that
    gets shipped is the fitted IRT item parameters rather than the vector of model correctness.
  scope: Correctness clustering is the adapted prior method (Vivek et al.'s anchor points);
    its embedding has one dimension per training LLM, where the IRT embedding is at most 16-dimensional
    in these experiments. Both are compared throughout; IRT is chosen for the release on the
    robustness evidence, not on average accuracy alone.
  evidence: 'Sections 3.2 and 4.1: the embedding is E_i = (alpha_i, beta_i), and footnote
    3 caps its dimension at 16.'
- id: the-correction-mixes-the-sample-with-the-model
  text: The shipped estimator, gp-IRT, is a convex combination of the plain weighted average
    over the chosen examples and an IRT-model prediction for every example not run, with the
    weight moving toward the raw data as the sample grows.
  scope: 'The mixing weight comes from a heuristic, not an optimization: it applies a corollary
    of Song (1988) for the optimal linear combination of two estimators while approximating
    the sampling estimator''s bias and the IRT estimator''s variance as zero, with the IRT
    bias estimated by a split-half procedure on the training models. With anchor points rather
    than random sampling the variance constant is divided by 4 by default, which is a stipulated
    halving of the standard deviation.'
  evidence: Section 4.2, equations 4.3 and 4.4, and the seven-step bias estimate that follows;
    the 'divide by 4' default is stated at the end of Section 4.2.
- id: the-correction-never-hurt
  text: The '++' correction matched or improved its uncorrected counterpart in every configuration
    tested, and adds only seconds of CPU time.
  scope: '''Always improves or matches'' is the paper''s summary of its own experiments across
    four benchmarks and two split types, not a proved property; the estimator is a shrinkage
    of the sample toward a model that can be misspecified. The running-time claim is IRT ability-fitting
    time, reported as negligible in a figure.'
  evidence: Section 5 'Key findings'; Appendix E.3 and Figure 13 for the running time.
- id: irt-anchors-survive-specialized-models
  text: On 40 hand-picked domain-specialized LLMs the correctness-based anchors degrade the
    most, while the IRT-based anchors are only slightly affected.
  scope: The comparison is between selection strategies under one distribution shift on MMLU,
    and 'only slightly affected' still means worse than on random models. This is the paper's
    stated reason for shipping IRT anchors, and its limitations section recommends periodically
    refitting rather than treating the robustness as settled.
  evidence: Section 5 'Specialized LLMs' and Figure 5; Appendix D describes how the 40 specialized
    models were identified.
- id: worst-case-error-around-four-percent
  text: For the best strategy on MMLU with 100 examples, estimation error across 99 test LLMs
    never exceeds 4% -- with one exception, an LLM of extremely low performance -- and is
    slightly smaller for more capable models.
  scope: One benchmark, one split, one strategy, and stated with its exception in the paper's
    own sentence. The average for the same setting is 2%, so 4% is the spread rather than
    a guarantee; the capability trend is described as having no strong dependency.
  evidence: Section 5 'Estimation error analysis' and Figure 6, whose caption says the worst
    case is at most 4% across almost all models.
- id: it-holds-when-the-test-models-are-newer
  text: Splitting train and test models by date rather than at random leaves the conclusions
    in place, including when three quarters of the data is held out for testing -- about three
    months of future models for the Leaderboard and MMLU, six for AlpacaEval 2.0.
  scope: 'A temporal shift over weeks to months in 2024, which is the shift the method is
    meant to absorb. Severe shifts are the acknowledged failure case: a model that fails simple
    questions while answering hard ones changes the correctness pattern the anchors were chosen
    for.'
  evidence: Section 5 'Evaluation pipeline' for the by-date split; Appendix E.1 and Figure
    11 for the 75%-test ablation; Section 6.2 for the failure mode.
- id: random-sampling-catches-up-at-two-to-four-times-the-budget
  text: 'Plain stratified random sampling reaches the same accuracy as the IRT method given
    a few times more examples: 400 per task against 100 on the Open LLM Leaderboard, 200 against
    100 on AlpacaEval 2.0, more than 400 against 100 on MMLU.'
  scope: So the curated subsets buy a factor of two to four over the simplest possible baseline,
    not the factor of 140 -- that larger factor is against running the whole benchmark. Measured
    on random model splits with no distribution shift, which is the setting most favourable
    to random sampling. Where examples are cheap but few, as on AlpacaEval 2.0's 805 GPT-4-judged
    examples, the two-fold difference is still money.
  evidence: Appendix E.2, whose heading asks exactly this question, and Figure 12.
- id: the-consistency-result-assumes-the-item-parameters-are-known
  text: The proposition behind the estimator says the IRT correction converges to the best
    possible prediction of the true score, assuming the item difficulty and discrimination
    parameters are already known exactly.
  scope: 'Asymptotic in the total number of examples the ability parameter is fitted on, and
    conditional on two assumptions: that the fitted ability converges, and that the true item
    parameters are known with uniformly bounded discrimination norms. In practice those parameters
    are themselves estimated from the training models, so the error the proposition brackets
    is not the error the user faces. The proof is four inequalities using that the logistic
    function is 1/4-Lipschitz plus Cauchy-Schwarz.'
  evidence: Proposition 4.1 with its two numbered assumptions; the proof is Appendix C.
- id: graded-scores-are-modelled-through-a-binary-proxy
  text: Where correctness is a number in [0,1] rather than right-or-wrong -- AlpacaEval 2.0,
    several HELM and Leaderboard scenarios -- it is thresholded into a binary variable before
    the IRT model sees it.
  scope: The threshold is chosen per scenario so that the total of the binarized scores approximately
    matches the total of the original ones across training models and examples, which preserves
    the mean but not the distribution. Stated as a simple and effective fix rather than as
    a modelling result.
  evidence: Section 4.3, including the equation that defines the threshold.
- id: a-tiny-benchmark-estimates-the-headline-not-the-profile
  text: tinyMMLU's 100 examples are spread over MMLU's 57 subjects with unequal weights --
    the heaviest are high school psychology, elementary mathematics and professional law --
    so what it estimates is the aggregate score.
  scope: Under two examples per subject on average, so a per-subject reading is not available
    from it at all; the weights are the anchor-cluster sizes and are reported as more uniform
    than the correctness-based alternative, measured by effective sample size, not as uniform.
  evidence: Appendix B, with Figure 9 for the weight spread and Figure 10 for the per-subject
    weight.
- id: adaptive-testing-was-tried-and-left-out
  text: Choosing each next example adaptively during evaluation improved the estimates further,
    but the implementation takes over five minutes to run and was not shipped.
  scope: 'Preliminary, presented as an extension: MMLU in the main text and other benchmarks
    in the appendix. The five minutes is against seconds for the released estimator, which
    is the reason given for leaving it out.'
  evidence: Section 6.1 'Adaptive testing' with Figure 8; Appendix E.5 and Figure 16 for the
    other benchmarks.
- id: the-same-machinery-estimates-prompt-template-performance
  text: Fitting the same model with prompt templates in place of examples predicts how a model
    will score under an unseen template, or how an unseen model will score under a given template.
  scope: One dataset and one small model family -- eight LLaMA models, vanilla or Alpaca-tuned,
    on ANLI's 750 points wrapped in 15 promptsource templates -- held out by model size (65B
    in test) and by template. Offered as a promising application, not a result about template
    variation in general.
  evidence: Section 6.1 'Prompt evaluation' and Figure 7.
- id: what-it-does-not-do
  text: 'It does not make the first evaluations cheaper, does not remove the need to keep
    re-running them, and is not a new benchmark: it is a subset of an existing one plus an
    estimator, and the paper asks for both to be refreshed periodically as models change.'
  scope: The correctness matrix that the anchors and IRT parameters are fitted on comes from
    full evaluations of hundreds of models. The limitations section names severe distribution
    shift as the failure mode and refitting on more modern LLMs as the mitigation, which makes
    a tiny benchmark a maintained artefact rather than a fixed dataset.
  evidence: Section 2 for the data assumption; Section 6.2 'Limitations' for the refresh recommendation.
- id: how-it-was-run
  text: Four benchmarks, six strategies -- stratified random, correctness clustering and IRT
    clustering, each with and without the IRT correction -- with models split into train and
    test either at random or by date, and the estimate compared against each test model's
    true full-benchmark score.
  scope: Open LLM Leaderboard and MMLU use 395 models at 75/25; HELM Lite v1.0.0 splits by
    training organization and uses 11-fold cross-validation for the random split; AlpacaEval
    2.0 has 100 models over 805 examples with 4-fold cross-validation. The IRT model is fitted
    by variational inference with normal priors and Gamma hyperpriors, point estimates taken
    as variational means, and its dimension chosen from {2, 5, 10, 15} on a validation split.
    Results averaged over 5 restarts.
  evidence: Sections 4.4 and 5; Appendix D for the per-benchmark scenario lists.
qa:
- q:
  - How many examples do you actually need to evaluate an LLM on a benchmark?
  - Can I get a benchmark score from a small sample?
  - How few examples give a reliable benchmark number?
  answers:
  - hundred-examples-per-scenario-within-two-percent
  - thirty-examples-suffice-on-the-leaderboard
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
  - What data does the method assume I already have?
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
  - the-correction-never-hurt
- q:
  - Is the small-sample estimate ever badly wrong?
  - What is the worst error to expect?
  - How reliable is this for a weak model?
  answers:
  - worst-case-error-around-four-percent
  - it-holds-when-the-test-models-are-newer
- q:
  - Would random sampling not do just as well?
  - How much better is this than sampling examples at random?
  - Is the curation worth it?
  answers:
  - random-sampling-catches-up-at-two-to-four-times-the-budget
- q:
  - Is there a guarantee that the estimator is correct?
  - What does the theory actually prove?
  - How strong is the consistency result?
  answers:
  - the-consistency-result-assumes-the-item-parameters-are-known
- q:
  - Does this work for benchmarks scored by a judge or by F1 rather than accuracy?
  - How are graded or continuous scores handled?
  answers:
  - graded-scores-are-modelled-through-a-binary-proxy
- q:
  - Does it still work for a domain-specialized or fine-tuned model?
  - What happens when the test models are unlike the training models?
  answers:
  - irt-anchors-survive-specialized-models
  - it-holds-when-the-test-models-are-newer
- q:
  - Can the examples be chosen adaptively as the evaluation runs?
  - Why is adaptive testing not part of the release?
  answers:
  - adaptive-testing-was-tried-and-left-out
- q:
  - Can this estimate how a prompt template will score?
  - Does it apply to prompt selection as well as example selection?
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
  - How were the experiments set up?
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
terminology:
  tinyBenchmarks: 'The released artefacts: 100-example-per-scenario subsets of the Open LLM
    Leaderboard, MMLU, HELM Lite and AlpacaEval 2.0, plus the fitted IRT parameters and the
    estimator that corrects a small-sample score.'
  tinyMMLU: The 100-example subset of MMLU, chosen by the IRT anchor-point method at the seed
    with the best test performance, with the per-example weights that go with it.
  scenario: A dataset within a benchmark -- ARC or GSM8K within the Open LLM Leaderboard.
    A subscenario is a division inside one, such as MMLU's 57 subjects. Budgets in this paper
    are per scenario.
  correctness: 'The benchmark''s score for one model on one example, written Y_il: either
    0/1 or a graded value in [0,1]. The matrix of these over models and examples is the input
    the method is fitted on.'
  anchor point: An example chosen as representative of a cluster of examples, carrying the
    cluster's share of the total as its weight, so that a weighted average over anchors approximates
    the average over everything.
  item response theory: 'The psychometric model behind standardized testing, here with examples
    as items and LLMs as testees: the probability of a correct answer is logistic in an ability
    vector, a per-example discrimination vector and a per-example bias.'
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
links_extra:
  code: https://github.com/felipemaiapolo/tinyBenchmarks
  the tiny datasets: https://huggingface.co/tinyBenchmarks
  HELM Lite, the benchmark version used: https://crfm.stanford.edu/helm/lite
---
