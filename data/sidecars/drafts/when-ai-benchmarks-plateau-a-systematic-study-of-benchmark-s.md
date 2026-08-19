<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced via a forced tool call). Every claim, number
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

Then promote it:  python scripts/draft_sidecars.py --accept when-ai-benchmarks-plateau-a-systematic-study-of-benchmark-s

Stamp: spec=e47adcd7257c checks=? body=052ac07dcb13
-->
---
claims: '[{"id": "saturation-index-definition", "kind": "context", "text": "\"When AI Benchmarks
  Plateau\" defines benchmark saturation as the loss of reliable discriminative power among
  top-performing models, and operationalizes it as an uncertainty-aware saturation index computed
  from leaderboard scores rather than from human baselines.", "scope": "Text-based LLM benchmarks
  with public leaderboard data; the standard-error estimate assumes accuracy-like metrics
  averaged over a fixed test set, so Elo, pass@k and judge-based metrics need tailored variance
  estimates."], "evidence": "Section 2.1"}, {"id": "prevalence", "kind": "result", "text":
  "Of 60 widely used text-based LLM benchmarks, 29 show high or very high saturation (saturation
  index at or above 0.7), and 14 of those fall in the very high band (index at or above 0.9).",
  "scope": "Static leaderboard snapshots for 60 benchmarks selected for sustained use and
  available leaderboard data, with k=5 top models and alpha=0.5; multimodal benchmarks excluded.",
  "evidence": "Section 4.1, Overall saturation patterns"}, {"id": "age-effect", "kind": "result",
  "text": "Saturation rises with benchmark age across 60 LLM benchmarks: 42.9% of benchmarks
  released within the past 24 months are saturated versus 54.5% of those older than 60 months,
  with mean saturation index 0.51, 0.52 and 0.60 across the age bins.", "scope": "Observational
  cross-benchmark comparison over benchmarks aged 1 to 114 months; the trend is directionally
  consistent but not statistically significant at conventional thresholds.", "evidence": "Figure
  3 and Section 4.1, Temporal and exposure effects"}, {"id": "private-test-sets", "kind":
  "result", "text": "Private, held-out test sets do not protect against saturation: public
  (N=56) and private (N=4) benchmarks show similar saturation distributions with no statistically
  meaningful difference in the saturation index, rejecting the hypothesis that public benchmarks
  saturate faster.", "scope": "Only 4 private benchmarks in the sample, so the null result
  rests on a small private group; benchmarks were all in sustained use by major developers.",
  "evidence": "Section 4.1, Accessibility and task design"}, {"id": "output-format", "kind":
  "result", "text": "Open-ended generation formats do not extend benchmark life relative to
  closed-ended ones: closed-ended (N=28) and open-ended (N=31) benchmarks show no meaningful
  difference in saturation, and the comparison is age-balanced (p=0.40).", "scope": "60 text-based
  LLM benchmarks annotated for output format; one benchmark falls outside the two format groups.
  Observational, not an intervention on format.", "evidence": "Section 5.2, Open-ended output
  formats"}, {"id": "templating", "kind": "result", "text": "Template diversity does not delay
  saturation: templated benchmarks (N=14) do not differ significantly from non-templated ones
  (N=46) in saturation behaviour (p=0.10).", "scope": "Annotation-based binary templated/non-templated
  split over 60 benchmarks; templating is one of the age-balanced comparisons, so age is not
  driving the null.", "evidence": "Section 4.1, Benchmark composition and construction"},
  {"id": "multilingual-confound", "kind": "result", "text": "The apparent saturation resistance
  of multilingual benchmarks is explained by recency, not linguistic scope: multilingual benchmarks
  (N=16) have lower raw saturation rates than English-only ones (N=44) but are substantially
  younger on average, 32.9 versus 48.9 months.", "scope": "60 text-based benchmarks; the age
  gap is a confound identified observationally, and the paper does not test multilinguality
  at matched age.", "evidence": "Section 5.2, Template diversity and multilinguality"}, {"id":
  "citations-not-predictive", "kind": "result", "text": "Adoption metrics do not predict benchmark
  saturation once age is controlled: citation counts (rho=0.22, p=0.12), citation growth rates
  (rho=0.13, p=0.37) and frequency of appearance in industry technical reports (rho=0.05,
  p=0.73) all show no significant association.", "scope": "Partial correlations across 60
  benchmarks after controlling for benchmark age; raw uncontrolled correlations do show higher
  saturation for more-cited benchmarks.", "evidence": "Section 4.1, Temporal and exposure
  effects, and Figure 4"}, {"id": "expert-curation", "kind": "result", "text": "Expert-curated
  benchmarks show lower saturation at comparable ages than crowdsourced ones, and several
  such benchmarks including ARC-AGI and BIG-Bench Hard remain unsaturated despite prolonged
  exposure.", "scope": "Curation categories differ significantly in age (p=0.0017), so age
  remains a confounder; fully synthetic benchmarks show low saturation but are recent, limiting
  causal reading.", "evidence": "Section 4.1, Benchmark composition and construction"}, {"id":
  "joint-regression", "kind": "result", "text": "In a Bayesian regression predicting the saturation
  index from 14 annotated benchmark properties, benchmark age and test set size are the only
  consistently predictive factors, while accessibility, output format and templating show
  no reliable association; the model reaches R-squared of 0.884 plus or minus 0.012.", "scope":
  "60 benchmarks, single static snapshot, so the fit describes association rather than causation;
  posterior AUROC for separating saturated from non-saturated benchmarks has a median of about
  0.98.", "evidence": "Section 4.2 and Figure 5"}, {"id": "test-set-scale", "kind": "result",
  "text": "Larger test sets are associated with lower saturation: benchmarks with more test
  items show less score compression among top models, and the relationship persists in the
  joint regression alongside benchmark age.", "scope": "Test set sizes span a few dozen to
  several hundred thousand items; the saturation index down-weights nominal size via effective
  size n to the power 0.5, so the effect is not an artifact of raw size dominating the uncertainty
  term.", "evidence": "Section 4.1, Overall saturation patterns, and Section 5.1"}, {"id":
  "livebench-case", "kind": "result", "text": "Dynamically refreshed benchmarks are not immune
  to saturation: LiveBench reaches a very high saturation index of 0.99 with a top-5 score
  range of 1.09 at moderate performance levels around 79%, and LiveCodeBench reaches 0.77
  with a range of 3.90.", "scope": "Case studies from single leaderboard snapshots with k=5;
  high saturation at moderate absolute scores indicates model-level stagnation rather than
  task mastery.", "evidence": "Table 7 and Appendix E"}, {"id": "index-stability", "kind":
  "result", "text": "The saturation index ranks benchmarks stably under parameter changes:
  Spearman correlation is 0.92 between k=3 and k=5 and between alpha=0.5 and alpha=1, and
  0.88 between alpha=0.5 and alpha=0, though only 18.3% to 48.3% of benchmarks stay in the
  same one of five saturation bins.", "scope": "Sensitivity analysis over k in {3,5} and alpha
  in {0,0.5,1} on the 60-benchmark set; most bin changes are between neighbouring bins, so
  absolute values shift more than ordering.", "evidence": "Table 1 and Section 2.3"}, {"id":
  "saturation-not-negative", "kind": "context", "text": "\"When AI Benchmarks Plateau\" argues
  benchmark saturation is a neutral phenomenon that signals genuine task mastery when the
  benchmark is valid, and is a problem only when score compression comes from evaluation noise
  exceeding real performance gaps.", "scope": "A conceptual position argued from the paper''s
  measurements, not itself tested; the paper''s index cannot by itself separate mastery from
  lost measurement resolution.", "evidence": "Section 5.4, When is saturation desirable?"}]'
one_liner: '"When AI Benchmarks Plateau" defines benchmark saturation as the loss of reliable
  discriminative power among top models, measures it with an uncertainty-aware saturation
  index over 60 LLM benchmarks, and finds age and test set size predict it while private test
  sets and open-ended formats do not.'
qa:
- q:
  - What work systematically studies why AI benchmarks saturate?
  - Where should I start reading about benchmark saturation in language model evaluation?
  - Is there a paper that gives a quantitative definition of benchmark saturation?
  answers:
  - saturation-index-definition
  - prevalence
- q:
  - How many popular LLM benchmarks have already saturated?
  - What fraction of language model benchmarks lose discriminative power?
  - How widespread is benchmark saturation across widely used LLM benchmarks?
  answers:
  - prevalence
  - age-effect
- q:
  - Do private or held-out test sets stop a benchmark from saturating?
  - Does keeping benchmark test data secret protect against score compression?
  - Is a hidden test set an effective defense against benchmark saturation?
  answers:
  - private-test-sets
- q:
  - Does switching from multiple-choice to open-ended generation make a benchmark last longer?
  - Do open-ended answer formats delay benchmark saturation?
  - Are closed-ended benchmarks more prone to saturation than free-form ones?
  answers:
  - output-format
- q:
  - Are multilingual benchmarks more resistant to saturation than English-only ones?
  - Does multilingual coverage protect a benchmark from saturating?
  - Why do multilingual benchmarks look less saturated?
  answers:
  - multilingual-confound
- q:
  - Which benchmark properties actually predict saturation?
  - What factors best explain why some benchmarks lose discriminative power?
  - Does benchmark age or design matter more for saturation?
  answers:
  - joint-regression
  - age-effect
  - test-set-scale
- q:
  - Does a benchmark saturate faster if it is heavily cited and widely used?
  - Is benchmark popularity associated with saturation after accounting for age?
  - Do citation counts predict which benchmarks saturate?
  answers:
  - citations-not-predictive
- q:
  - What kind of benchmark construction resists saturation?
  - Are expert-written benchmarks more durable than crowdsourced ones?
  - Which benchmarks stayed unsaturated despite years of exposure?
  answers:
  - expert-curation
- q:
  - Does making a benchmark bigger help it stay discriminative?
  - How does test set size affect benchmark saturation?
  - Why do small evaluation sets saturate sooner?
  answers:
  - test-set-scale
- q:
  - Can a continuously updated benchmark like LiveBench still saturate?
  - Do contamination-resistant refreshed benchmarks avoid score compression?
  - What are the saturation index values for LiveBench and LiveCodeBench?
  answers:
  - livebench-case
- q:
  - How sensitive is the saturation index to the number of top models used?
  - Does the choice of k and alpha change which benchmarks count as saturated?
  - Is the uncertainty-aware saturation index robust to its parameters?
  answers:
  - index-stability
- q:
  - Does template diversity in prompts prevent a benchmark from saturating?
  - Are templated benchmarks more likely to saturate than free-form ones?
  answers:
  - templating
- q:
  - Is benchmark saturation always a bad thing?
  - When does a saturated benchmark indicate real progress rather than a measurement failure?
  - Should a saturated benchmark be retired?
  answers:
  - saturation-not-negative
claims_note: n/a
coined: saturation index
gloss: a 0-to-1 score for how much top model results on a benchmark have collapsed into evaluation
  noise
key: akhtar2026saturation
misreadings:
- 'A high saturation index does not mean a benchmark''s task has been solved: strong clustering
  of top models can occur at moderate absolute scores, which indicates model-level stagnation
  rather than task mastery.'
- The finding that private test sets do not reduce saturation is not evidence that contamination
  is harmless; it says secrecy alone fails to prevent score compression once a benchmark is
  widely adopted, and only 4 private benchmarks were available for the comparison.
- The age-saturation relationship is an observational association across 60 benchmarks, not
  a demonstrated causal mechanism; the analysis does not identify what about exposure compresses
  scores.
- 'Saturation as defined by the loss of reliable discriminative power is not the same as stagnation:
  stagnation is statistical indistinguishability among top models alone, while saturation
  additionally requires performance near the empirically inferred ceiling.'
- The 60-benchmark set is not a random sample of AI benchmarks; it was filtered for sustained
  use in developer reports and for available up-to-date leaderboard data, and excludes multimodal
  benchmarks and benchmarks like BIG-Bench that lacked leaderboard coverage.
terminology:
  benchmark saturation: 'The loss of reliable discriminative power among top-performing models
    on a benchmark: top models cannot be statistically distinguished by their scores and performance
    approaches the benchmark''s empirically observed ceiling.'
  stagnation: Statistical indistinguishability among a benchmark's top-performing models without
    performance being near the benchmark's empirical ceiling; distinguished from saturation,
    which requires both conditions.
  saturation index: A continuous score in [0,1] equal to exp of minus the squared normalized
    top-model score range, which rises as the spread between the best and k-th best model
    falls inside expected evaluation uncertainty.
  normalized score range: The gap between the top model's score and the k-th model's score
    divided by the standard error of that difference, interpretable as a signal-to-noise ratio
    for a leaderboard's top.
  effective test set size: The nominal number of test items raised to the power alpha (default
    0.5), used in place of raw size when estimating score standard errors so that very large
    benchmarks do not dominate uncertainty estimates.
  model-level saturation: Tight clustering of top models at a low or moderate performance
    level, indicating that a benchmark no longer separates contemporary systems even though
    the task is not solved.
---
