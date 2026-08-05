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
key: DBLP:conf/icml/PoloWCSXY24
coined: tinyBenchmarks
gloss: 100-example versions of standard LLM benchmarks, with IRT-based error correction
one_liner: tinyBenchmarks shows that 100 curated examples per scenario estimate an LLM's accuracy
  on a full benchmark within about 2% error, and releases 100-example versions of the Open
  LLM Leaderboard, MMLU, HELM and AlpacaEval 2.0 with the item-response-theory tools that
  correct the estimate.
claims:
- id: hundred-examples-two-percent
  text: Evaluating a large language model on 100 curated examples per scenario estimates its
    accuracy on the full benchmark to within roughly 2% average error, across the Open LLM
    Leaderboard, MMLU, HELM and AlpacaEval 2.0.
  scope: 'The 100 is per scenario, not per benchmark: this is 600 of 29K examples for the
    Open LLM Leaderboard, 100 of 14K for MMLU, 1000 of 10K for HELM and 100 of 800 for AlpacaEval
    2.0. The ~2% is an average over evaluated LLMs, not a worst-case bound, so an individual
    model can be estimated worse.'
  evidence: Figure 3
- id: mmlu-hundred-of-14k
  text: IRT++, the best-performing strategy in tinyBenchmarks, predicts an LLM's MMLU accuracy
    to within 1.9% of its accuracy on all 14K MMLU examples while evaluating only 100 curated
    examples, under 1% of the benchmark.
  scope: Measured on LLMs released between 30 December and 18 January, i.e. after the example
    selection and the IRT model were fitted, so the number is not an in-sample fit. It is
    an accuracy-estimation error, not a guarantee about ranking two models whose accuracies
    differ by less than it.
  evidence: Figure 1
- id: irt-beats-random
  text: Stratified random sampling of evaluation examples, the standard efficient-benchmarking
    approach, carries a larger performance-estimation error than correctness-clustering or
    item-response-theory estimators at the same number of examples, with the gap widest at
    small sample sizes.
  scope: Holds across the four benchmarks measured and for both randomly chosen and recently
    released LLMs; the clustering approach in particular depends on having correctness data
    from previously evaluated models to cluster on, so it is not available for a genuinely
    new benchmark with no evaluated models.
  evidence: Figure 3, Section 3
- id: anchor-points-generalised
  text: tinyBenchmarks extends anchor-point selection, previously demonstrated on classification
    tasks, to generative and multiple-choice LLM benchmarks by clustering examples on model
    correctness rather than on model confidence in a correct class.
  scope: The generalisation is what makes the method applicable to AlpacaEval 2.0 and to all
    scenarios of the Open LLM Leaderboard and HELM, where there is no 'confidence in the correct
    class' to cluster on.
  evidence: Section 3.2
qa:
- q:
  - How many examples do you actually need to evaluate an LLM on a benchmark?
  - Can you benchmark a language model on far fewer examples?
  - How few examples are enough to estimate LLM benchmark accuracy?
  - Is it possible to cut the cost of LLM evaluation by subsampling?
  answers:
  - hundred-examples-two-percent
  - mmlu-hundred-of-14k
- q:
  - What is tinyMMLU?
  - How accurate is tinyMMLU compared to full MMLU?
  - What are the tinyBenchmarks versions of MMLU and the Open LLM Leaderboard?
  answers:
  - mmlu-hundred-of-14k
  - hundred-examples-two-percent
- q:
  - Is random sampling good enough for efficient LLM evaluation?
  - Does item response theory beat random subsampling for benchmarks?
  - Why not just evaluate on a random subset of the test set?
  answers:
  - irt-beats-random
- q:
  - What are anchor points in LLM evaluation?
  - How do you pick which benchmark examples to keep?
  - How are the tinyBenchmarks examples selected?
  answers:
  - anchor-points-generalised
  - irt-beats-random
terminology:
  scenario: One dataset-and-task unit inside a composite benchmark. The Open LLM Leaderboard
    has six and HELM has ten, which is why the per-scenario budget of 100 examples is 600
    and 1000 examples respectively.
  anchor point: A single example chosen so that models are correct on it if and only if they
    are correct on a large set of other examples, letting it stand in for that set.
  p-IRT / gp-IRT: 'The performance-IRT and generalized performance-IRT estimators: they correct
    a raw subset accuracy using a fitted item-response-theory model of example difficulty
    rather than treating the subset as a random sample.'
  IRT++: The best-performing combination of example selection and IRT correction.
misreadings:
- The result is 100 examples per scenario, not 100 examples per benchmark. Reproducing it
  on the Open LLM Leaderboard means 600 examples, and on HELM 1000.
- A ~2% average estimation error is not a licence to rank models that differ by less than
  2%. The claim is about estimating one model's accuracy, not about resolving a leaderboard's
  fine ordering.
- The curated subsets are not a hard or adversarial subset of the benchmark. They are chosen
  to be informative about the rest of it, and the IRT correction, not the examples alone,
  is what brings the error down.
- Clustering-based selection needs correctness data from already-evaluated models, so the
  method shrinks an existing benchmark rather than making a brand-new benchmark cheap to build.
---
