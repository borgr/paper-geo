<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from hand fix: named the subject in 2 phrasings. Every claim, number
and scope condition below is a machine's reading of the paper and needs your eyes.

THIS PAPER ALREADY HAS A LIVE SIDECAR, and this draft would replace it. Start here:

  diff data/sidecars/tinybenchmarks-evaluating-llms-with-fewer-examples.md data/sidecars/drafts/tinybenchmarks-evaluating-llms-with-fewer-examples.md

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

  python scripts/draft_sidecars.py --accept tinybenchmarks-evaluating-llms-with-fewer-examples --replace

Stamp: spec=4b2236733458 checks=pass body=d878f5b5c579
-->
---
key: polo2024tinybenchmarks
coined: tinyBenchmarks
gloss: 100-example curated subsets of popular LLM benchmarks, plus an item-response-theory
  estimator that corrects the score
one_liner: tinyBenchmarks curates 100 examples per scenario by clustering item-response-theory
  embeddings of benchmark examples, and corrects the resulting score with an IRT-based estimator,
  reproducing full-benchmark LLM performance on MMLU, the Open LLM Leaderboard, HELM Lite
  and AlpacaEval 2.0 within about 2%.
claims:
- id: mmlu-100-examples
  kind: result
  text: Evaluating an LLM on 100 curated MMLU examples estimates its accuracy on all 14K MMLU
    examples to within 1.9% on average, for recent LLMs released between December 30th and
    January 18th.
  scope: MMLU accuracy for LLMs held out by release date, with the IRT++ (gp-IRT) strategy;
    needs correctness data from 395 previously evaluated Open LLM Leaderboard models.
  evidence: Figure 1
- id: two-percent-four-benchmarks
  kind: result
  text: 100 curated examples per scenario estimate LLM performance within about 2% average
    error on the Open LLM Leaderboard, MMLU, HELM Lite and AlpacaEval 2.0. That is 600 of
    29K, 100 of 14K, 1000 of 10K and 100 of 805 examples respectively.
  scope: Both random and by-date train-test splits of the evaluated LLMs, for the best strategies
    (IRT anchor points and gp-IRT); test LLMs are dominated by base and instruction-tuned
    models, with error averaged over 5 restarts.
  evidence: Figure 3
- id: cost-reduction-factor
  kind: result
  text: Curated subsets cut MMLU evaluation cost by a factor of 140, from 14K examples down
    to 100. On the Open LLM Leaderboard even 30 examples per scenario suffice, a factor of
    160 from 29K down to 180.
  scope: Cost counted as examples evaluated, with estimation error staying within 2%; the
    30-per-scenario figure is for the 6-scenario Leaderboard average, not a single scenario.
  evidence: Figure 3
- id: irt-anchors-robust-specialized
  kind: result
  text: On a hand-picked test set of 40 specialized LLMs fine-tuned for domains such as math
    or coding, MMLU estimates from correctness-clustered anchor points degrade markedly. IRT-embedding
    anchor points are only slightly affected.
  scope: MMLU only, with 40 specialized models tested against a train set of base and instruction-tuned
    LLMs drawn from the 428 collected Open LLM Leaderboard models.
  evidence: Figure 5
- id: worst-case-error
  kind: result
  text: Across 99 test LLMs on MMLU with 100 examples, the IRT++ estimation error never exceeds
    4%, except for one LLM with extremely low true accuracy. The error is slightly lower for
    more capable models.
  scope: Random train-test split of the 395 Open LLM Leaderboard models, MMLU accuracy, IRT++
    strategy with 100 examples; average error over these models is 2%.
  evidence: Figure 6
- id: gpirt-never-hurts
  kind: result
  text: The gp-IRT correction ("++") always improves or matches the vanilla estimate that
    just averages the selected examples, across all four benchmarks and both train-test splits.
    It adds only a few seconds of CPU time.
  scope: Vanilla random, correctness-anchor and IRT-anchor estimators on the Open LLM Leaderboard,
    MMLU, HELM Lite and AlpacaEval 2.0; needs a pre-fitted IRT model, whose fitting cost is
    excluded.
  evidence: Figure 3
- id: random-sampling-cost
  kind: result
  text: 'Stratified random sampling needs far more examples to match IRT++ at 100 examples:
    400 per task (2400 total) on the Open LLM Leaderboard and 200 on AlpacaEval 2.0. On MMLU
    it needs more than 400.'
  scope: Random train-test split of LLMs, so no distribution shift between train and test
    models; comparison made at equal estimation error.
  evidence: Figure 12
- id: longer-horizon
  kind: result
  text: IRT++ estimation error stays close to the main results when the test set is enlarged
    to the most recent 75% of models. That is about 3 months of future LLMs for the Open LLM
    Leaderboard and MMLU, and 6 months for AlpacaEval 2.0.
  scope: Ablation with 75% of models held out by date, versus roughly 3 weeks and 2 months
    of future models in the main experiments; measured as average estimation error and standard
    deviation across test LLMs.
  evidence: Figure 11
- id: prompt-evaluation
  kind: result
  text: The same IRT-based estimators predict how an LLM performs under unseen prompt templates,
    tested on 8 LLaMA models evaluated on 750 ANLI examples wrapped in 15 promptsource instruction
    templates.
  scope: ANLI only, with vanilla and Alpaca-instruction-tuned LLaMA at 7B, 13B, 30B and 65B;
    splits hold out the 65B models and rotate templates in 2-fold cross-validation.
  evidence: Figure 7
- id: adaptive-testing-cost
  kind: result
  text: Selecting MMLU examples adaptively with an IRT variant improves estimation over a
    pre-selected fixed subset, but the implementation takes over 5 minutes to run, versus
    seconds for the fixed tiny subsets.
  scope: Preliminary results on MMLU, with additional benchmarks in Figure 16; the runtime
    is for the paper's own implementation, not a lower bound on adaptive testing generally.
  evidence: Figure 8
- id: tinymmlu-weights
  kind: result
  text: tinyMMLU's 100 example weights are much more uniform than those of correctness-based
    anchor points, as measured by effective sample size, which is what makes it robust to
    LLMs with unusual correctness patterns.
  scope: Comparison of the two anchor-selection methods on MMLU with 100 anchor points; the
    highest-weighted subjects in tinyMMLU are high school psychology, elementary mathematics
    and professional law.
  evidence: Figure 9
- id: irt-for-performance-estimation
  kind: context
  text: tinyBenchmarks introduces item response theory as a performance estimator for efficient
    LLM benchmarking, rather than only as a tool for ranking models or characterising item
    difficulty.
  scope: As of ICML 2024 publication; earlier IRT work on language models covered ability
    measurement, benchmark saturation and adaptive testing without a full-benchmark score
    estimator.
- id: released-artifacts
  kind: context
  text: tinyBenchmarks releases 100-example versions of MMLU, the six Open LLM Leaderboard
    scenarios, AlpacaEval 2.0 and HELM Lite, plus a pip-installable package with pre-trained
    IRT parameters. A new LLM's full-benchmark score can then be estimated on CPU in seconds.
  scope: Tiny datasets built from correctness data collected in January 2024 from 395 Open
    LLM Leaderboard models, 37 HELM Lite models and 100 AlpacaEval 2.0 models; the authors
    recommend periodically refreshing the curated examples and IRT parameters as LLMs change.
- id: pirt-consistency
  kind: result
  text: The p-IRT estimator is proved to converge in probability to the best mean-squared-error
    approximation of an LLM's full-scenario score as the number of observed examples grows.
  scope: Assumes a consistent ability estimate, known true example parameters, and uniformly
    norm-bounded example discrimination vectors; asymptotic in the number of observed examples.
  evidence: Section 4.2
qa:
- ask:
    plain: how many questions does it take to score a language model on MMLU accurately?
    jargon: how closely does a 100-example tinyMMLU subset reproduce full 14K-example MMLU
      accuracy?
    task: how do I evaluate a model on MMLU without running all 14K questions?
    practitioner: can I trust a 100-question MMLU score for my own model?
  answered_by:
  - mmlu-100-examples
  - cost-reduction-factor
- ask:
    plain: how accurate is a score measured on a hundred benchmark questions instead of thousands?
    jargon: what is the estimation error of 100-example curated subsets on the Open LLM Leaderboard,
      MMLU, HELM Lite and AlpacaEval 2.0?
    task: how do I know how much error I take on by evaluating a model on a subset?
    practitioner: is a two-percent error small enough for me to report a subset score?
  answered_by:
  - two-percent-four-benchmarks
  - worst-case-error
- ask:
    plain: why not just pick benchmark questions at random instead of curating them?
    jargon: how many stratified randomly sampled examples are needed to match IRT++ at 100
      examples?
    task: how do I subsample a benchmark -- randomly, or with curated anchor examples?
    practitioner: should I bother with curated subsets when random sampling is easier?
  answered_by:
  - random-sampling-cost
- ask:
    plain: do small evaluation sets still work for a model specialised in one domain like
      maths or code?
    jargon: how do IRT-embedding anchor points compare with correctness-clustered anchors
      on domain-specialised LLMs?
    task: how do I evaluate a fine-tuned domain model cheaply without the subset misjudging
      it?
    practitioner: my model is fine-tuned for one domain -- will a tiny benchmark misjudge
      it?
  answered_by:
  - irt-anchors-robust-specialized
  - tinymmlu-weights
- ask:
    plain: do small curated evaluation sets go stale as new models come out?
    jargon: how far into the future do IRT++ error rates hold as the LLM test set is extended?
    task: how do I know whether a curated benchmark subset still applies to a model released
      after it?
    practitioner: tinyMMLU was built before my model existed -- is a tinyMMLU estimate still
      valid for a model released later?
  answered_by:
  - longer-horizon
  - two-percent-four-benchmarks
- ask:
    plain: how does a technique from educational testing make model evaluation cheaper?
    jargon: what does item response theory contribute to LLM performance estimation, and what
      does the gp-IRT correction add over averaging the selected examples?
    task: how do I turn per-question correctness into an estimate of a full benchmark score?
  answered_by:
  - irt-for-performance-estimation
  - gpirt-never-hurts
- ask:
    plain: what is a good paper on cutting the cost of evaluating language models?
    jargon: what work established item response theory as a performance estimator for LLM
      benchmarking?
    task: where should I start reading if I want to evaluate models on fewer examples?
    practitioner: which paper should I cite for evaluating language models on a hundred examples?
  answered_by:
  - irt-for-performance-estimation
  - released-artifacts
- ask:
    plain: are there ready-made small versions of the popular language model benchmarks?
    jargon: which tiny benchmark datasets and pre-trained IRT parameters does tinyBenchmarks
      release?
    task: how do I install something that estimates a full benchmark score from 100 examples?
    practitioner: can I get a full-benchmark estimate for my model on CPU in seconds?
  answered_by:
  - released-artifacts
  - gpirt-never-hurts
- ask:
    plain: can a small set of examples predict how a model behaves under a different prompt
      wording?
    jargon: do IRT-based estimators predict LLM performance under unseen promptsource instruction
      templates?
    task: how do I compare prompt templates without running the full evaluation for each one?
    practitioner: should I use a tiny benchmark to choose between my prompt templates?
  answered_by:
  - prompt-evaluation
- ask:
    plain: is it better to choose evaluation questions adaptively as a language model answers
      them?
    jargon: does adaptive IRT item selection beat a fixed pre-selected subset on MMLU, and
      at what runtime?
    task: how do I decide between adaptive item selection and a fixed curated subset?
    practitioner: is adaptive testing worth five minutes per model over a subset that runs
      in seconds?
  answered_by:
  - adaptive-testing-cost
- ask:
    plain: is there any mathematical guarantee behind estimating a benchmark score from a
      sample?
    jargon: what consistency result is proved for the p-IRT performance estimator?
    practitioner: do I have a theoretical reason to trust a p-IRT estimate, or only empirical
      ones?
  answered_by:
  - pirt-consistency
- ask:
    plain: how much cheaper is scoring a model on a curated subset than on a whole benchmark?
    jargon: what cost reduction factor do tinyBenchmarks subsets achieve on MMLU and the Open
      LLM Leaderboard?
    task: how do I cut my evaluation compute bill by two orders of magnitude?
    practitioner: how much evaluation compute would I actually save by switching to a tiny
      benchmark?
  answered_by:
  - cost-reduction-factor
  - random-sampling-cost
misreadings:
- 'The roughly 2% figure is an average estimation error across evaluated LLMs, not a guarantee
  for any single model: on MMLU with 100 examples, errors up to 4% occur, and a model with
  extremely low accuracy exceeded that.'
- 'tinyBenchmarks does not work from scratch on an arbitrary new benchmark: the anchor points
  and IRT parameters are fitted from publicly available correctness data for hundreds of LLMs
  already evaluated on the full benchmark.'
- The 100 curated examples are not simply the hardest or most discriminative questions; they
  are examples closest to K-Means centroids of IRT example embeddings, each carrying a weight
  equal to its cluster's share of the scenario.
- 'IRT-based estimation is not claimed to survive severe distribution shift: models that fail
  simple questions while answering complicated ones correctly break the correctness patterns,
  and the authors recommend periodically refitting on data from newer LLMs.'
- The gp-IRT tool is not a replacement for evaluating a model; it corrects the score obtained
  from the small evaluated subset, and its improvement over the raw weighted average depends
  on having a pre-fitted IRT model for that benchmark.
terminology:
  anchor points: Examples selected as cluster centroids of an embedding of benchmark items,
    each weighted by the fraction of the scenario's items assigned to its cluster, so that
    a weighted average over the anchors approximates the full-scenario score.
  p-IRT: An estimator of an LLM's full-scenario benchmark score that sums the observed correctness
    on the evaluated examples and the item-response-theory predicted probabilities of correctness
    on the unevaluated ones.
  gp-IRT: An estimator of an LLM's benchmark score formed as a convex combination of the raw
    weighted average over evaluated examples and the p-IRT estimate, with the weight set from
    an estimate of IRT bias and of sampling variance so that more examples shift weight toward
    the raw data.
  correctness: The per-example score a benchmark's harness assigns an LLM, either binary (incorrect/correct)
    or a bounded degree of correctness in [0,1]; item response theory is applied after thresholding
    the bounded case into a binary variable.
  IRT++: The variant of an example-selection strategy in which the score computed on the selected
    examples is further adjusted by the gp-IRT estimator, as opposed to the "vanilla" variant
    that reports the weighted average of selected examples directly.
  effective sample size (ESS): A measure of inequality among example weights, where an ESS
    of 0.50 informally means the weighted average is influenced by only 50% of uniformly weighted
    examples.
links_extra:
  huggingface: https://huggingface.co/tinyBenchmarks
  demo: https://github.com/felipemaiapolo/tinyBenchmarks/blob/main/tinyBenchmarks_MMLU_demo.ipynb
---
