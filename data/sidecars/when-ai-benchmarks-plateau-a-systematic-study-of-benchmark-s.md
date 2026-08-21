---
claims:
- id: saturation-index-definition
  kind: context
  text: '"When AI Benchmarks Plateau" defines benchmark saturation as the loss of reliable
    discriminative power among top-performing models. Saturation is operationalized as an
    uncertainty-aware index computed from leaderboard scores, with no reliance on human baselines.'
  scope: The index uses the top k=5 leaderboard scores and an effective test set size n^0.5;
    it is designed for accuracy-like metrics averaged over a fixed test set, and other metrics
    such as Elo, pass@k or judge-based scores need their own variance estimates.
  evidence: Section 2.1 and Section 2.2
- id: prevalence
  text: Of 60 widely used text-based LLM benchmarks, 29 show high or very high saturation
    (saturation index at least 0.7), of which 14 are very high (at least 0.9).
  scope: Text-only benchmarks with usable leaderboard data, from developer reports (Jan 2022-Nov
    2025) and cited papers; static snapshots.
  evidence: Section 4.1, Overall saturation patterns
- id: age-effect
  text: The share of saturated benchmarks rises from 42.9% among benchmarks released within
    the past 24 months to 54.5% among those older than 60 months. Mean saturation indices
    across the age bins are 0.51, 0.52 and 0.60.
  scope: N=60 benchmarks aged 1 to 114 months; the trend is directionally consistent but modest
    and not statistically significant at conventional thresholds.
  evidence: Section 4.1 (Temporal and exposure effects) and Figure 3
- id: private-test-sets
  text: Public (N=56) and private (N=4) benchmarks show similar saturation distributions,
    with no statistically meaningful difference in saturation index. Private held-out test
    sets therefore do not protect against saturation, rejecting the hypothesis that public
    benchmarks saturate faster.
  scope: Only 4 private benchmarks in the sample, so the comparison has low power; based on
    annotated public availability of benchmark data and labels rather than on measured contamination.
  evidence: Section 4.1 (Accessibility and task design) and Section 5.2
- id: output-format
  text: Closed-ended benchmarks (N=28) and open-ended generation benchmarks (N=31) show no
    meaningful difference in saturation, and the comparison is age-balanced (p=0.40).
  scope: 60 text-only LLM benchmarks; output format annotated as MCQ versus free-form generation,
    so open-ended scoring protocols are not separated.
  evidence: Section 4.1 (Accessibility and task design) and Section 5.2
- id: templating
  text: Templated benchmarks (N=14) do not differ significantly from non-templated ones (N=46)
    in saturation behaviour (p=0.10), indicating that surface-level template diversity alone
    does not delay saturation.
  scope: Templating annotated as whether prompts use fixed patterns versus natural variation,
    on 60 text benchmarks; age-balanced comparison group.
  evidence: Section 4.1 (Benchmark composition and construction) and Section 5.2
- id: multilingual-confound
  text: Multilingual benchmarks (N=16) show lower raw saturation rates than English-only benchmarks
    (N=44). The advantage is explained by recency rather than intrinsic resistance, as the
    multilingual benchmarks are substantially younger on average (32.9 vs. 48.9 months).
  scope: Observational comparison across 60 benchmarks with age as a confounder; no causal
    test isolating language coverage from maturity.
  evidence: Section 4.1 (Benchmark composition and construction) and Section 5.2
- id: expert-curation
  text: Expert-curated benchmarks show lower saturation than crowdsourced ones at comparable
    ages, and several such benchmarks including ARC-AGI and BIG-Bench Hard remain unsaturated
    despite prolonged exposure.
  scope: Curation categories differ significantly in age (p=0.0017), and fully synthetic benchmarks
    are too recent for causal interpretation; the finding is associational, not a controlled
    comparison.
  evidence: Section 4.1 (Benchmark composition and construction) and Section 5.3
- id: adoption-not-predictive
  text: After controlling for benchmark age, citation counts are not significantly associated
    with saturation (rho=0.22, p=0.12), nor are citation growth rates (rho=0.13, p=0.37) or
    frequency of appearance in developer technical reports (rho=0.05, p=0.73).
  scope: Adoption measured only through citation counts, citation growth and inclusion in
    industry model release reports for 60 benchmarks; raw uncontrolled correlations do show
    higher saturation at higher citation counts.
  evidence: Section 4.1 (Temporal and exposure effects) and Figure 4
- id: joint-model
  text: A Bayesian regression predicting the saturation index of 60 benchmarks attains R-squared
    of 0.884 +/- 0.012, with benchmark age and test set size the most consistent predictors.
    Predictors also included adoption proxies, accessibility, output format, templating, language
    coverage, curation strategy and documented quality issues.
  scope: Fitted on 60 benchmarks with time-invariant annotations; accessibility, output format
    and templating show no reliable associations once confounders are included, and the fit
    is descriptive rather than causal.
  evidence: Section 4.2 and Figure 5
- id: auroc
  text: The interaction model separating saturated from non-saturated benchmarks reaches a
    posterior AUROC tightly concentrated near a median of about 0.98.
  scope: In-sample discrimination on the same 60 annotated benchmarks used for fitting, with
    labels from the paper's own index.
  evidence: Figure 6
- id: test-set-scale
  text: Larger test sets are associated with lower saturation indices across the 60 benchmarks,
    and the relationship persists in the joint Bayesian regression, indicating that measurement
    resolution limits discriminative power.
  scope: Test set sizes span a few dozen to several hundred thousand samples; the index's
    uncertainty term uses n^0.5 rather than raw n, so the size dependence is deliberately
    down-weighted.
  evidence: Section 4.1 (Overall saturation patterns) and Section 5.1
- id: index-stability
  text: Saturation-index rankings are stable to parameter choices, with Spearman correlations
    of 0.92 for k=3 vs k=5, 0.88 for alpha=0.5 vs alpha=0 and 0.92 for alpha=0.5 vs alpha=1.
    Only 18.3-48.3% of benchmarks stay in the same one of the five saturation bins.
  scope: Sensitivity checked over k in {3,5} and alpha in {0,0.5,1} on the 60-benchmark set;
    most bin changes are between neighbouring bins, so absolute values shift more than ordering.
  evidence: Table 1 and Section 2.3
- id: saturation-at-low-scores
  text: 'Saturation can occur far below the score ceiling: LiveBench reaches a saturation
    index of 0.99 with top models clustered in a 1.09-point range at roughly 79% performance.
    Such clustering reflects model-level stagnation rather than task completion.'
  scope: Single-benchmark case study from a static leaderboard snapshot of n=1000 with SE_delta=0.1028;
    saturation as defined additionally requires nearness to the empirical ceiling.
  evidence: Table 7 and Appendix E
- id: lifecycle-recommendations
  kind: context
  text: '"When AI Benchmarks Plateau" argues benchmarks should be managed as ageing measurement
    instruments rather than fixed targets. Its recommendations are larger or stratified test
    sets, periodic or adversarial refreshes, uncertainty-aware leaderboard reporting, and
    explicit revision or retirement criteria.'
  scope: Recommendations are derived from associational analysis of 60 text-only LLM benchmarks
    and are not themselves experimentally validated; as of the 2026 publication.
  evidence: Section 5.4
qa:
- ask:
    plain: has anyone measured how many language model benchmarks no longer tell the best
      models apart?
    jargon: is there a quantitative operationalization of benchmark saturation across LLM
      leaderboards?
    task: where do I start reading about whether LLM benchmarks still separate frontier models?
    practitioner: I need a citable source on benchmark saturation for an evaluation report,
      what should I cite?
  answered_by:
  - saturation-index-definition
  - prevalence
- ask:
    plain: how many of the popular language model benchmarks have stopped separating the top
      models?
    jargon: what share of widely used text LLM benchmarks exhibit high saturation index values?
    task: how do I tell whether the benchmarks in my evaluation suite still have discriminative
      power?
    practitioner: are the standard benchmarks I report on still worth reporting?
  answered_by:
  - prevalence
  - age-effect
- ask:
    plain: do benchmarks get worse at separating models the longer they have been out?
    jargon: is time since benchmark release a predictor of saturation index?
    task: how do I use a benchmark's release date to judge whether it is still useful?
    practitioner: should I drop a benchmark from my evaluation suite once it is a few years
      old?
  answered_by:
  - age-effect
  - joint-model
- ask:
    plain: does hiding the test answers keep a benchmark from going stale?
    jargon: do private held-out test splits slow saturation relative to fully public benchmarks?
    task: if I want my new benchmark to last, is withholding the test set enough?
    practitioner: should I pay for a benchmark with a hidden test set instead of using a public
      one?
  answered_by:
  - private-test-sets
- ask:
    plain: does asking for written answers instead of multiple choice make a benchmark last
      longer?
    jargon: does open-ended generation versus closed-ended answer format affect saturation
      rates?
    task: when designing an eval, should I use free-form responses to keep it discriminative
      for longer?
    practitioner: is it worth rebuilding my multiple-choice eval as open-ended generation?
  answered_by:
  - output-format
- ask:
    plain: do benchmarks covering many languages stay useful longer than English-only ones?
    jargon: is the lower observed saturation of multilingual benchmarks intrinsic or confounded
      by release recency?
    task: can I extend an evaluation's shelf life by adding more languages to it?
    practitioner: should I invest in translating my benchmark into more languages to keep
      it hard?
  answered_by:
  - multilingual-confound
- ask:
    plain: what actually makes some evaluations keep separating the best models for years?
    jargon: which design factors, such as expert curation or templated item generation, are
      associated with slower saturation?
    task: how should I build a benchmark that stays discriminative as models improve?
    practitioner: is it worth paying domain experts to write my eval items instead of crowdsourcing
      them?
  answered_by:
  - expert-curation
  - templating
- ask:
    plain: do the most cited and most reported benchmarks wear out faster?
    jargon: after adjusting for age, are citation counts or appearance in developer technical
      reports associated with saturation?
    task: can I use a benchmark's popularity to predict whether it is still discriminative?
    practitioner: should I avoid the most widely reported benchmarks on the assumption that
      heavy use burns them out?
  answered_by:
  - adoption-not-predictive
  - age-effect
- ask:
    plain: does having more test questions help tell the best models apart?
    jargon: how does test set size relate to saturation index and measurement resolution among
      top models?
    task: how many examples should my benchmark contain if I want it to distinguish frontier
      models?
    practitioner: is it worth expanding my 500-item eval to a few thousand items?
  answered_by:
  - test-set-scale
  - joint-model
- ask:
    plain: how do you put a number on benchmark staleness, and does the number move if you
      change the settings?
    jargon: how sensitive is a leaderboard saturation index to the number of top models k
      and the weighting parameter alpha?
    task: if I compute a saturation score for my own benchmarks, which parameter choices do
      I need to worry about?
    practitioner: can I trust a saturation ranking of benchmarks enough to act on it?
  answered_by:
  - index-stability
  - saturation-index-definition
- ask:
    plain: can a benchmark be exhausted even though the best scores are nowhere near 100%?
    jargon: does a high saturation index imply the task is solved, or can score clustering
      occur well below ceiling?
    task: how do I tell whether flat leaderboard scores mean my benchmark is used up or that
      models have stopped improving?
    practitioner: top models on my benchmark all sit around 79% and within a point of each
      other, is the benchmark still informative?
  answered_by:
  - saturation-at-low-scores
  - saturation-index-definition
- ask:
    plain: what should the people who build evaluations do once all the best models score
      the same?
    jargon: what lifecycle practices are recommended for benchmarks that have lost discriminative
      power among frontier models?
    task: how do I decide when to refresh, stratify or retire a benchmark I maintain?
    practitioner: my leaderboard's top entries are within noise of each other, should I retire
      it or refresh the test set?
  answered_by:
  - lifecycle-recommendations
- ask:
    plain: which properties of a benchmark best explain whether it still separates the top
      models?
    jargon: in a joint Bayesian regression over benchmark metadata, which covariates explain
      variance in the saturation index?
    task: can I predict from a benchmark's metadata alone whether it is saturated before running
      any models?
    practitioner: if I only know a benchmark's age, size and format, can I judge whether it
      is worth running?
  answered_by:
  - joint-model
  - auroc
one_liner: A study of 60 text-based LLM benchmarks that defines saturation as the loss of
  statistically reliable separation among top models, measures it with an uncertainty-aware
  saturation index from leaderboard scores, and finds age and test set scale predict it while
  private test sets and open-ended formats do not.
terminology:
  benchmark saturation: 'The loss of reliable discriminative power among top-performing models
    on a benchmark: top scores are statistically indistinguishable and also approach the benchmark''s
    empirically observed ceiling.'
  stagnation: Statistical indistinguishability among a benchmark's top models without performance
    being near the empirical ceiling, which may be overcome by future architectural, training
    or evaluation advances.
  saturation index: A continuous score in [0,1] equal to exp(-R_norm^2), where R_norm is the
    top-1-to-top-k score gap divided by the standard error of that difference; higher values
    mean stronger evidence of saturation.
  normalized score range (R_norm): The spread between the best and k-th best leaderboard score
    divided by the standard error of their difference, interpretable as a signal-to-noise
    ratio for model separability.
  effective test set size: The nominal test set size n raised to the power alpha (default
    0.5), used in the standard-error term so that very large benchmarks do not dominate uncertainty
    estimates.
  model-level saturation: Tight clustering of top models at a low absolute performance level,
    indicating that a benchmark no longer separates contemporary systems rather than that
    the task is solved.
misreadings:
- 'A high saturation index does not mean a benchmark''s task is solved: strong clustering
  of top models can occur at moderate absolute scores, which indicates lost discriminative
  power rather than task mastery.'
- 'Saturation is not treated as inherently bad in "When AI Benchmarks Plateau": if a benchmark
  is valid and measures a clearly defined capability, convergence near its ceiling can signal
  genuine progress.'
- The finding that public and private benchmarks saturate similarly is not a claim that contamination
  does not happen; it is a claim that secrecy alone does not prevent score compression, and
  only 4 private benchmarks were available for the comparison.
- The age effect reported across 60 benchmarks is directional and not statistically significant
  at conventional thresholds, so it should not be cited as a demonstrated causal mechanism
  of exposure-driven compression.
- 'Expert curation being associated with lower saturation is not a controlled result: curation
  categories differ significantly in age (p=0.0017), and age remains a confounder.'
- 'Dynamically updated benchmarks are not immune: LiveBench and LiveCodeBench, both designed
  with refresh mechanisms, register saturation indices of 0.99 and 0.77.'
links_extra:
  coalition: https://evalevalai.com/
---
