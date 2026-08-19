<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced via a forced tool call) + 2 repair rounds. Every claim, number
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

Then promote it:  python scripts/draft_sidecars.py --accept stop-guessing-when-to-stop-testing-efficient-model-evaluatio

Stamp: spec=8f05813a4658 checks=pass body=d6d6dc0ca9f7
-->
---
key: arviv2026stopguessing
one_liner: Adaptive evaluation applies group sequential testing with the Pocock spending function
  to benchmark runs, so evaluation stops as soon as a user-defined criterion — a target confidence-interval
  width, an equivalence margin, a score threshold — is met, with the statistical guarantees
  preserved despite repeated peeking.
gloss: stopping a benchmark run as soon as the statistics justify it, instead of at a fixed
  sample size
coined: Adaptive evaluation
links_extra:
  code: https://github.com/OfirArviv/adaptive-eval
  data: https://huggingface.co/datasets/VLMEval/OpenVLMRecords
terminology:
  Diminishing returns stopping: A stopping rule that halts evaluation once the marginal gain
    in confidence-interval precision from an additional batch of examples falls below a user-specified
    threshold.
  Equivalence margin stopping: A stopping rule that halts a model comparison once the estimated
    performance difference is confidently confined within a user-specified margin, declaring
    the two models practically equivalent instead of waiting for strict significance.
  Group sequential testing (GST): A statistical design that analyses accumulating data in
    batches at pre-specified interim points and adjusts the per-stage significance threshold
    so the overall Type I error rate stays at the nominal level despite repeated looks.
  Mean-of-means benchmark score: A multi-dataset benchmark score computed as the unweighted
    average of per-dataset means, so every dataset contributes equally regardless of its size.
  Peeking: Repeatedly inspecting and acting on results while data is still being collected,
    which invalidates the standard interpretation of fixed-sample p-values and confidence
    intervals.
claims:
- id: ci-target-savings
  kind: result
  text: Stopping an Open VLM Leaderboard evaluation once the 95% confidence-interval half-width
    reaches ±2.5 points saves 80% of the evaluation cost relative to the full benchmark. Stopping
    instead at the diminishing-returns plateau saves 44% while giving up 0.132 points of precision.
  scope: 206 VLMs on the Open VLM Leaderboard, 31 multimodal benchmarks totalling 14,400 examples,
    averaged over 10 random seeds; unweighted mean-of-means scoring, and savings depend on
    that benchmark's dataset-size heterogeneity.
  evidence: Figure 1
- id: ci-vs-fraction
  kind: result
  text: On the Open VLM Leaderboard, a ±3-point confidence interval on a single model's score
    needs roughly 15% of the examples, ±2 points needs about 30%, and ±1.5 points needs about
    half.
  scope: 95% CIs for each of 206 VLMs over 10 random seeds, unweighted mean-of-means over
    31 datasets; the fractions are specific to this benchmark's variance structure.
  evidence: Section 7.1
- id: full-benchmark-waste
  kind: result
  text: Going from 8K examples (55% of the Open VLM Leaderboard) to the full 14,400 examples
    narrows the confidence interval only from 2.9 to 2.7 points. That 0.2-point gain costs
    nearly double the compute.
  scope: 206 VLMs, 95% CI half-width averaged over 10 seeds; precision improves as n^(-1/2)
    and small high-variance datasets dominate the unweighted mean-of-means, which caps overall
    uncertainty.
  evidence: Section 7.1
- id: small-subsets-uncertain
  kind: result
  text: The common heuristic of evaluating on 1K examples or fewer yields confidence intervals
    often exceeding ±5.5 points on the Open VLM Leaderboard, wide enough to be impractical
    for decision-making.
  scope: 206 VLMs, 31 multimodal datasets, mean-of-means score, 10 seeds; magnitude is benchmark-specific
    and reflects heterogeneous dataset sizes.
  evidence: Section 7.1
- id: pairwise-gap-savings
  kind: result
  text: For pairs of top-50 Open VLM Leaderboard models differing by more than 2 points, sequential
    stopping saved at least 60% of the evaluation effort. Pairs differing by less than 1.2
    points typically consumed the full benchmark without reaching significance.
  scope: 1K sampled pairs from the top 50 models, strict comparison at 95% confidence, initial
    sample 600 (100 per dataset) and batch size 100, Pocock spending function; roughly 24%
    of pairs fall in the sub-1.2-point regime.
  evidence: Figure 2
- id: beats-fixed-1200
  kind: result
  text: Adaptive sequential evaluation reliably separated 76% of 1K top-50 Open VLM Leaderboard
    model pairs at 95% confidence. A fixed 1.2K-sample heuristic of 200 examples per dataset,
    evaluated with bootstrap confidence intervals, separated only 55%.
  scope: 1K sampled pairs from the top 50 models; the fixed-size baseline was given bootstrap
    inference, which is more powerful per sample than the sequential test.
  evidence: Section 7.2
- id: fixed-size-failures-invisible
  kind: result
  text: With a fixed 1.2K-sample budget on the Open VLM Leaderboard, the model pairs that
    cannot be reliably separated look no different to the user from the ones that can. Sequential
    testing instead reports when a comparison never reached significance.
  scope: 1K sampled pairs from the top 50 models at 95% confidence, where the fixed budget
    separated 55% of pairs and the sequential procedure 76%.
  evidence: Section 7.2
- id: ranking-case-study
  kind: result
  text: Ranking 5 Open VLM Leaderboard models drawn from the top 15 with a ±2-point equivalence
    margin at α=0.05 used only 60% of the examples. On average 2.4 of the 20 pairwise comparisons
    per run stayed indistinguishable and consumed the full benchmark.
  scope: 5 models sampled from the top 15 across 10 seeds, pairwise comparisons without multiple-testing
    correction, best-to-worst gap at most 5 points.
  evidence: Section 7.3.1
- id: deployment-case-study
  kind: result
  text: Testing whether a candidate model beats a deployed baseline by at least 2 points at
    95% confidence used 63% of the examples of a fixed-sample evaluation. The average is over
    100 sampled Open VLM Leaderboard pairs from the top 15.
  scope: One-sided test with stopping on either a confirmed ≥2-point improvement or on futility;
    100 random pairs from the top 15 models, so gaps between the compared models are small.
  evidence: Section 7.3.2
- id: model-selection-case-study
  kind: result
  text: Screening Open VLM Leaderboard models by discarding those below 60 points and otherwise
    stopping at a ±2-point CI used 30% of the total sample budget, against 50% without the
    discard rule. 86 models were filtered out early.
  scope: 206 VLMs over 10 seeds, two combined stopping rules (threshold crossing plus precision-based);
    the saving depends on how many candidates are genuinely weak.
  evidence: Section 7.3.3
- id: context-call-to-adopt
  kind: context
  text: The adaptive evaluation framework of "Stop Guessing When to Stop Testing" argues that
    NLP and vision-language benchmarking should replace fixed-size test sets with sequential
    testing. It imports group sequential designs from clinical trials into model evaluation.
  scope: A position and framework paper whose experiments cover one leaderboard, the Open
    VLM Leaderboard with 206 models; sequential testing itself is long established in clinical
    trials and quality control.
  evidence: Section 1
- id: context-no-past-statistics
  kind: context
  text: The adaptive evaluation framework obtains its statistical guarantees from the evaluation
    run in progress alone, needing no prior scores for other models. Efficient-evaluation
    methods that select benchmark subsets instead rely on statistics from full benchmark runs.
  scope: Contrast is with subset-selection and score-prediction approaches; the sequential
    framework instead assumes per-example scores behave close to i.i.d. and pays a modest
    power reduction for the interim looks.
  evidence: Section 3
- id: stopping-rule-menu
  kind: context
  text: 'The adaptive evaluation framework supplies 6 stopping rules that users can mix to
    match an evaluation objective: efficacy, equivalence margin, precision-based (minimum
    detectable effect size), threshold crossing, futility and diminishing returns.'
  scope: Multi-dataset benchmarks with per-example scores in [0,1]; the experiments demonstrate
    the precision-based, equivalence-margin, threshold-crossing and futility rules, and margins
    or thresholds must be user-specified.
  evidence: Section 5.3
qa:
- q:
  - How much compute can I save by stopping a benchmark evaluation early instead of running
    all the examples?
  - What fraction of a benchmark do I actually need for a reliable model score?
  - Does adaptive stopping really cut evaluation cost by 80%?
  answers:
  - ci-target-savings
  - ci-vs-fraction
  - full-benchmark-waste
- q:
  - Is it safe to evaluate a language or vision model on only 1K examples?
  - How wide are confidence intervals when people sub-sample a benchmark to a thousand examples?
  - What is wrong with heuristically picking a small evaluation subset?
  answers:
  - small-subsets-uncertain
  - fixed-size-failures-invisible
- q:
  - How many examples do I need to tell two close models apart?
  - Can sequential testing decide which of two similar models is better with less data?
  - What happens when two models differ by less than a point on a benchmark?
  answers:
  - pairwise-gap-savings
  - beats-fixed-1200
- q:
  - Does sequential testing beat just picking a fixed sample size like 200 examples per dataset?
  - How does adaptive evaluation compare against a fixed-size bootstrap evaluation on model
    comparisons?
  - Which resolves more model pairs, a fixed 1.2K-sample budget or adaptive stopping?
  answers:
  - beats-fixed-1200
  - fixed-size-failures-invisible
- q:
  - How can I check whether a new model improves on the deployed one by a practically meaningful
    margin?
  - Can evaluation stop as soon as a 2-point improvement is confirmed?
  - How much data does a deployment go/no-go comparison need?
  answers:
  - deployment-case-study
  - stopping-rule-menu
- q:
  - How do I cheaply screen hundreds of training checkpoints or candidate models?
  - Can weak candidate models be discarded early during evaluation?
  - What savings come from filtering out underperforming checkpoints during benchmarking?
  answers:
  - model-selection-case-study
- q:
  - How much of a benchmark is needed to rank a handful of closely matched models?
  - Can adaptive evaluation produce a full ranking of several models cheaply?
  answers:
  - ranking-case-study
- q:
  - What should I read about making language model evaluation cheaper without losing statistical
    guarantees?
  - Which paper proposes sequential testing for benchmark evaluation?
  - Where does the idea of adaptive stopping in NLP benchmarking come from?
  - Is there work arguing against fixed-size benchmarks?
  answers:
  - context-call-to-adopt
  - context-no-past-statistics
- q:
  - What stopping criteria are available for adaptive model evaluation?
  - How do I express an evaluation goal like 'stop when the CI is ±2 points' or 'stop when
    the models are equivalent'?
  - What is equivalence margin stopping versus futility stopping in benchmark evaluation?
  answers:
  - stopping-rule-menu
  - ranking-case-study
- q:
  - How does adaptive evaluation differ from methods that pick benchmark subsets using earlier
    models' scores?
  - Do I need to run the full benchmark on other models first to use sequential evaluation?
  answers:
  - context-no-past-statistics
- q:
  - Should benchmark builders keep their datasets small to limit evaluation cost?
  - Is a bigger benchmark wasteful if most examples add little precision?
  answers:
  - full-benchmark-waste
  - small-subsets-uncertain
misreadings:
- 'The 80% cost reduction is not free precision: it is the saving obtained when the user accepts
  a ±2.5-point confidence interval on the Open VLM Leaderboard score, and tighter targets
  cost more samples.'
- 'Adaptive evaluation does not make close model comparisons resolvable: pairs differing by
  under 1.2 points still consumed the full Open VLM Leaderboard without reaching significance,
  and the framework''s contribution is reporting that failure rather than hiding it.'
- Sequential testing is not statistically free — repeated interim looks force a stricter per-stage
  threshold and cost a modest amount of power relative to a fixed-size bootstrap test of the
  same sample size.
- The reported percentage savings are measurements on the Open VLM Leaderboard's 31 heterogeneous
  multimodal datasets, not general constants; a benchmark whose datasets are uniformly large
  will show a different diminishing-returns point.
- 'Adaptive stopping does not remove the need for user judgement: equivalence margins, score
  thresholds and acceptable CI widths must be specified in advance, which the paper''s limitations
  note demands statistical or domain expertise.'
- Because stopping points depend on observed performance, results can vary between runs, so
  adaptive evaluation is not automatically more reproducible than fixed-size evaluation unless
  randomness is controlled.
---
