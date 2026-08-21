---
key: perlitz2024bat
coined: BenchBench
gloss: a Python package and meta-benchmark for testing whether one LLM benchmark agrees with
  others
one_liner: Benchmark Agreement Testing — validating a new LLM benchmark by correlating model
  rankings with established ones — gives unstable answers unless the reference benchmarks
  are aggregated, the threshold is data-driven and enough models are randomly sampled; BenchBench
  implements all three.
claims:
- id: combined-variance-reduction
  kind: result
  text: Applying aggregate reference benchmarks, metric-aware thresholds and randomly sampled
    model selection together cuts the standard deviation of Benchmark Agreement Testing results
    from 0.31 to 0.10, a 67% reduction.
  scope: Over 40 LLM benchmarks with results cut off at Jan 2024, spanning over 200 models;
    variance measured across repeated BAT instances using Kendall-tau; benchmark pairs need
    at least 5 intersecting models.
  evidence: Table 1
- id: aggregate-reference
  kind: result
  text: Replacing a single arbitrary reference benchmark with an aggregate reference reduces
    the standard deviation of BAT correlations from 0.31 to 0.23, a drop of more than 30%.
    The aggregate is built by averaging model win-rates across several benchmarks.
  scope: Requires access to model scores from multiple benchmarks measuring a similar construct,
    which BenchBench supplies; measured on the paper's set of over 40 benchmarks, results
    cutoff Jan 2024.
  evidence: Table 1
- id: model-selection
  kind: result
  text: Selecting the models for BAT randomly and in larger numbers, rather than picking a
    small arbitrary set, lowers the standard deviation of BAT results from 0.31 to 0.20, a
    35% reduction. The recommendation is at least 10 models, preferably more.
  scope: Kendall-tau agreement over the paper's collection of more than 40 benchmarks, cutoff
    Jan 2024; assumes the target benchmark already has scores across diverse model sizes and
    architectures.
  evidence: Table 1
- id: reference-choice-variability
  kind: result
  text: Alpaca v2 agrees with MT-Bench at Kendall-tau 0.57 but with LMSys Arena at 0.82, even
    though both references are taken to measure similar abilities. A single-reference BAT
    conclusion can therefore be an artifact of which reference was picked.
  scope: Each correlation computed over 20 randomly sampled models shared by the benchmark
    pair; benchmark results cut off Jan 2024.
  evidence: Figure 3
- id: few-models-variance
  kind: result
  text: With small model subsets the standard deviation of BAT results approaches 0.25. The
    Kendall-tau correlation between LMSys Arena and MT-Bench ranges from roughly 0.65 to 0.99
    depending only on how many models are included.
  scope: Randomly sampled subsets of models shared by the two benchmarks; variance shrinks
    as subset size grows, so the instability is a small-sample property, not a property of
    those two benchmarks.
  evidence: Figure 5
- id: granularity-top-models
  kind: result
  text: Two benchmarks can show high agreement over a wide range of models while agreeing
    poorly over the top-ranked ones. Kendall-tau between LMSys Arena and each of BBH, MMLU
    and Alpaca v2 changes substantially between the top 5, top 10 and top 15 Arena models.
  scope: Compares overlapping top-k model sets ranked by LMSys Arena; the effect is about
    closely ranked models generally, and the paper reports that the top 3 models are almost
    never in agreement across benchmarks.
  evidence: Figure 2
- id: adjacent-vs-random
  kind: result
  text: For a fixed number of models, BAT correlation over models adjacent in rank is lower
    than over randomly sampled models, and the gap widens as the subset gets smaller.
  scope: Adjacent sets sampled from the full rank range rather than a fixed tier; averaged
    over all benchmark pairs in the paper's collection using Kendall-tau.
  evidence: Figure 4
- id: metric-bias
  kind: result
  text: Kendall-tau and Pearson agreement scores track each other closely across benchmark
    pairs (r²=0.85) but differ by a roughly constant bias of 0.21. Applying one fixed threshold
    such as 0.8 to both metrics is therefore unsound.
  scope: All benchmark pairs in the paper's collection with varying model subsets; the bias
    is the offset between rank and score correlation, and does not license converting one
    metric into the other for an individual pair.
  evidence: Figure 6
- id: data-driven-threshold
  kind: result
  text: Choosing the agreement metric and threshold in a data-driven way rather than by a
    fixed cutoff reduces the standard deviation of BAT results from 0.31 to 0.23. Agreement
    is declared when the target benchmark's Z-score against other benchmarks' agreement with
    the same reference exceeds -1σ.
  scope: Requires a population of benchmarks already scored against the chosen reference,
    which BenchBench maintains and updates as benchmarks are added; measured on the paper's
    over-40-benchmark collection.
  evidence: Table 1
- id: model-tier
  kind: result
  text: 'Benchmark agreement is not uniform across model tiers: bottom-tier models agree with
    Kendall coefficients just below 0.5, middle-tier models below 0.2, and top-tier models
    around 0.3.'
  scope: Tiers defined by rank position over models in the paper's benchmark collection, cutoff
    Jan 2024; bottom-ranked models also show the highest score standard deviation.
  evidence: Figure 8
- id: benchbench-contribution
  kind: context
  text: BenchBench is an open-source Python package and leaderboard that standardizes Benchmark
    Agreement Testing. It ships stored results for over 40 LLM benchmarks, so a benchmark
    builder can run agreement testing without evaluating models on the reference benchmarks.
  scope: As of the 2024 preprint; covers the benchmarks in the package's database with results
    cut off Jan 2024, and requires the user to supply target-benchmark scores for the models
    it recommends.
  evidence: Section 5
- id: bat-guidelines-context
  kind: context
  text: '"Benchmark Agreement Testing Done Right" proposes best practices for validating an
    LLM benchmark against established ones. The practices cover the choice of reference benchmarks,
    models, correlation metric and agreement threshold, for which no standard procedure existed.'
  scope: As of 2024, and about agreement testing between LLM benchmarks reporting model-level
    scores; the paper deliberately does not address when BAT should be used or how high or
    low agreement should be interpreted substantively.
  evidence: Section 3, Section 4
- id: survey-of-bat-practice
  kind: context
  text: A survey of prior work using benchmark agreement testing finds no shared methodology.
    Reported practice includes a 0.8 threshold applied to both rank and score correlation,
    a 0.7 rank-correlation threshold, and validation against a single reference using 6 models.
  scope: Based on the works reviewed in the paper's related-work discussion rather than an
    exhaustive systematic review of the literature.
  evidence: Section 6
qa:
- ask:
    practitioner: How do I check whether a new LLM benchmark is valid by comparing it to existing
      benchmarks?
    unsorted:
    - What are the recommended best practices for benchmark agreement testing?
    - How should I run correlations between my benchmark and established LLM leaderboards?
  answered_by:
  - bat-guidelines-context
  - combined-variance-reduction
- ask:
    unsorted:
    - How much does following the BAT best practices actually reduce variance?
    - Do the BenchBench recommendations make agreement results more stable, and by how much?
    - What is the measured effect of aggregating references, sampling models and using a data-driven
      threshold together?
  answered_by:
  - combined-variance-reduction
  - aggregate-reference
  - model-selection
  - data-driven-threshold
- ask:
    practitioner: How much do agreement scores change if I pick a different reference benchmark?
    unsorted:
    - Is it safe to validate a new benchmark against just one established benchmark?
    - Why use an aggregate of several reference benchmarks instead of one?
  answered_by:
  - reference-choice-variability
  - aggregate-reference
- ask:
    practitioner: How many models do I need for a reliable rank correlation between two benchmarks?
    unsorted:
    - Why is benchmark agreement unstable when only a few models are compared?
    - What happens to correlation variance with small model subsets?
  answered_by:
  - few-models-variance
  - model-selection
- ask:
    unsorted:
    - Why do benchmarks agree overall but disagree on the strongest models?
    - Does benchmark agreement hold for top-ranked LLMs?
    - Is high rank correlation between leaderboards meaningful for frontier models?
  answered_by:
  - granularity-top-models
  - adjacent-vs-random
- ask:
    practitioner: Can I use the same 0.8 correlation threshold for Kendall-tau and Pearson?
    unsorted:
    - How do rank and score correlations differ when comparing LLM benchmarks?
    - Is there a bias between Kendall-tau and Pearson agreement scores?
  answered_by:
  - metric-bias
  - data-driven-threshold
- ask:
    unsorted:
    - Does benchmark agreement depend on whether the compared LLMs are weak, mid-range or
      state of the art?
    - How does model tier affect correlations between LLM benchmarks?
    - Do older or lower-ranked models inflate benchmark agreement?
  answered_by:
  - model-tier
  - adjacent-vs-random
- ask:
    practitioner: Where can I get pooled results for many LLM benchmarks to correlate my own
      against?
    unsorted:
    - Is there a software package for running benchmark agreement testing?
    - What does the BenchBench leaderboard rank?
  answered_by:
  - benchbench-contribution
- ask:
    practitioner: What should I read about the validity of LLM benchmarks and leaderboards?
    unsorted:
    - Which paper established standards for evaluating benchmarks against each other?
    - Where should I start reading on meta-evaluation of LLM benchmarks?
  answered_by:
  - bat-guidelines-context
  - survey-of-bat-practice
- ask:
    unsorted:
    - How inconsistent is existing practice when papers report agreement with established
      benchmarks?
    - What thresholds have prior LLM benchmark papers used to call agreement high?
    - Do published benchmark validation studies use a common methodology?
  answered_by:
  - survey-of-bat-practice
  - bat-guidelines-context
misreadings:
- High agreement between two LLM benchmarks does not mean they measure the same qualities;
  it can also reflect that strong models are strong at many tasks, and it does not license
  the conclusion that new benchmarks are unnecessary.
- 'Low agreement is not automatically evidence that a benchmark is invalid: an unreliable
  benchmark whose ranking has not converged will disagree even with itself under different
  subsets or seeds, so reliability bounds the achievable agreement.'
- The 0.21 offset between Kendall-tau and Pearson is a population-level bias across benchmark
  pairs, not a conversion factor to apply to an individual pair's score.
- 'BenchBench''s best practices do not require running more evaluations: the package ships
  stored reference-benchmark results, so the variance reduction comes at no additional compute
  cost.'
- The finding that bottom-tier models agree more is not a reason to drop old models, switch
  benchmarks frequently or restrict BAT to recent models; the paper concludes no strong action
  follows from the tier trend.
terminology:
  Benchmark Agreement Testing (BAT): Validating a benchmark by measuring the statistical agreement
    — typically Kendall-tau over ranks or Pearson over scores — between its model scores and
    those of an established reference benchmark.
  Aggregate reference benchmark: A synthetic reference formed by averaging model win-rates
    across several benchmarks that measure a similar construct, used in place of a single
    arbitrarily chosen reference.
  Granularity (in benchmark agreement): The spread of model quality inside the compared model
    subset; agreement measured over models adjacent in rank is fine-grained, agreement over
    models of widely varying quality is coarse.
  Data-driven threshold: Deciding whether a target benchmark agrees with a reference by its
    Z-score against the distribution of other benchmarks' agreement with that same reference,
    with agreement declared above -1σ, rather than by a fixed correlation cutoff.
  Model tier: The rank band a model occupies within a benchmark's leaderboard — bottom, middle
    or top — treated as a variable that changes measured benchmark agreement.
links_extra:
  leaderboard: https://hf.co/spaces/ibm/benchbench
  code: https://github.com/IBM/benchbench
---
