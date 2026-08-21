---
key: ashurytahan2026errormap
coined: ErrorMap
gloss: an LLM-based pipeline that turns a benchmark's wrong answers into a hierarchical taxonomy
  of why the model failed
one_liner: ErrorMap analyses each wrong prediction in a benchmark run with an analyst LLM
  and recursively groups the resulting error labels into a layered taxonomy, and applying
  it to 83 models on 35 datasets yields ErrorAtlas, a static taxonomy of 17 high-level LLM
  error categories.
links_extra:
  code: https://github.com/IBM/ErrorMap
terminology:
  ErrorAtlas: A static, reusable taxonomy of 17 high-level LLM error categories built by running
    ErrorMap over sampled wrong predictions from 83 models on 35 datasets, intended for replicable
    cross-model and cross-benchmark comparison.
  Failure signature: The distribution of a single model's errors over taxonomy categories,
    used to distinguish models that share the same benchmark score but fail in different ways.
  Informative Correct Predictions (ICPs): Correct answers produced by other models on the
    same benchmark instance, given to the analyst LLM as additional reference material when
    diagnosing a wrong prediction; up to 3 are included per prompt.
  Taxonomy coverage: The fraction of analysed wrong predictions that an automatic classifier
    maps into a real taxonomy category rather than into 'other', 'hard to analyze', or rare
    uninformative categories.
claims:
- id: erroratlas-17-categories
  kind: result
  text: ErrorAtlas is a taxonomy of 17 high-level LLM error categories, led by Missing Required
    Element at 15.56% of errors, Specification Misinterpretation at 11.5%, and Logical Reasoning
    Error at 9.09% of errors.
  scope: Sampled wrong predictions from 83 models on 35 datasets spanning HELM Capabilities,
    MedHELM, ToRR, BFCL-v4 and code benchmarks, with gpt-oss-120b as analyst and clustering
    LLM.
  evidence: Table 1 and Table 6
- id: understudied-errors
  kind: result
  text: Omissions of required detail are the single most prevalent LLM error category in ErrorAtlas,
    at 15.56% of errors, appearing in 31 of 35 datasets and for 82 of 83 models. Question
    or task misinterpretation is second at 11.5%, and both types receive little attention
    in LLM research.
  scope: Prevalence measured on the sampled errors of the 35 datasets studied; the judgement
    that these types are under-discussed comes from the authors' related-work survey of existing
    error taxonomies, not from a bibliometric count.
  evidence: Table 6 and Section 4
- id: reasoning-benchmarks-nonreasoning-errors
  kind: result
  text: About 44% of model errors on MMLU-Pro, GPQA and Omni-MATH have a weak reasoning orientation.
    Those failures are instead technical, such as computation errors, missing required elements
    or counting errors, even though the 3 benchmarks are positioned as reasoning tests.
  scope: Aggregated over the sampled failures of the models evaluated on these 3 datasets,
    with categories assigned by the ErrorAtlas classifier; failure is decided by each benchmark's
    primary metric and a threshold.
  evidence: Table 7 and Section 4
- id: coverage-95
  kind: result
  text: Automatically mapping the analysed wrong predictions back into ErrorAtlas gives a
    coverage score of 95.2%, with only 1 instance falling into "other" and 48 into "hard to
    analyze".
  scope: Wan et al. (2024) protocol applied to the same errors used to build the taxonomy;
    295 errors counted as uncovered, including rare or uninformative categories outside ErrorAtlas.
  evidence: Section 6, Coverage, and Table 6
- id: accuracy-92
  kind: result
  text: A meta-judge choosing between an error's assigned ErrorAtlas category and a random
    alternative agrees with the assigned label 92% of the time. The same meta-judge accepts
    the per-instance error analyses 91.1% of the time.
  scope: Qwen2.5-72B-Instruct as meta-judge over the 3 experiments (ErrorAtlas construction,
    Gemini comparison, MMLU-Pro taxonomy), in a forced binary choice against one random negative.
  evidence: Table 10 and Section 6
- id: robustness-sampling
  kind: result
  text: Rebuilding ErrorAtlas with a rephrased prompt, different examples and a 15% sample
    reproduces the original categories with 88% precision and 88% recall. A weaker configuration
    using qwen-30b-thinking on a 5% sample reaches 1.00 precision but 0.52 recall.
  scope: Manual comparison of high-level category descriptions and subcategories against the
    original gpt-oss-120b 10%-sample taxonomy; the lower-bound configuration still recovers
    8 of the top 10 categories, with losses in the long tail.
  evidence: Table 12 and Appendix E.2
- id: matches-manual-mmlu-pro
  kind: result
  text: Run on MMLU-Pro, ErrorMap produces 5 error categories whose GPT-4o distribution tracks
    the MMLU-Pro paper's manual annotation. ErrorMap reports 44% logical reasoning errors
    against 39% manual reasoning errors, and 5% prompt misinterpretation against 4% question
    understanding errors.
  scope: Single dataset (MMLU-Pro) and single model (GPT-4o); ErrorMap splits the manual "lack
    of specific knowledge" category (35%) across two of its own categories and has no "other"
    bucket, which is 10% of the manual labels, so the label sets do not map one-to-one.
  evidence: Table 3
- id: gemini-version-diff
  kind: result
  text: 'Gemini 1.5 Pro outscores Gemini 1.5 Flash by a mean 4.8% on the HELM Capabilities
    benchmark. ErrorMap localises that gap: the Pro version makes significantly fewer computation
    errors and fewer incomplete-reasoning errors.'
  scope: One model pair on HELM Capabilities, run with the fixed ErrorAtlas categories using
    only ErrorMap stages 1 and 2.b over all predictions of the 2 Gemini models.
  evidence: Figure 3 and Section 5.1
- id: per-model-signatures
  kind: result
  text: 'Models evaluated on HELM Capabilities show distinct failure signatures: Gemini 2.0
    Flash Lite has the highest rate of incomplete-content errors and the fewest formatting
    errors. Claude 3.5 Haiku skews toward logical reasoning errors and Mixtral 8x22B Instruct
    v0.1 toward computation errors.'
  scope: Models compared only within HELM Capabilities so the instances are shared; differences
    between best- and worst-performing models per category are usually significant under binomial
    tests, except prompt misinterpretation (p=.075).
  evidence: Figure 2, Figure 4 and Table 9
- id: domain-error-shifts
  kind: result
  text: 'Error distributions on MMLU-Pro shift by subject domain: mathematics and physics
    have near-identical profiles, while the health domain shows a disproportionately high
    share of factual errors, exceeding even history.'
  scope: MMLU-Pro only, with errors grouped by the dataset's own domain labels; reported as
    an observed pattern in the error distribution figure rather than a per-domain significance
    test.
  evidence: Figure 5
- id: context-diagnosis-gap
  kind: context
  text: ErrorMap addresses the gap between benchmark scores, which say when a model fails,
    and diagnosis, which says why. It analyses the model's actual output alongside the input
    rather than characterising difficulty by properties of the question alone.
  scope: Positioning as of the 2026 arXiv release; earlier diagnostic work the paper surveys
    either targets a single subdomain or model, or infers difficulty from inputs, and the
    authors report finding no prior general LLM error taxonomy.
  evidence: Section 1 and Section 7
- id: context-cheap-reuse
  kind: context
  text: ErrorAtlas is released as a static, publicly available taxonomy so error analyses
    of new models can be compared across time and papers. Applying it needs only per-instance
    analysis plus category assignment, skipping taxonomy generation.
  scope: Reuse is intended for tasks whose outputs contain interpretable content or chain-of-thought;
    classification-style tasks with no explanation cannot be analysed, and the authors plan
    periodic ErrorAtlas updates rather than freezing it.
  evidence: Section 3 and Appendix F
- id: sampling-cost
  kind: result
  text: Building ErrorAtlas took roughly 3 hours of largely parallel inference by sampling
    approximately 10% of each model-dataset pair's failures. Applying ErrorMap to a single
    dataset or model pair is cheaper still, since cost scales with the number of wrong predictions
    analysed.
  scope: gpt-oss-120b as the analyst LLM, with most inference calls run in parallel; the MMLU-Pro
    taxonomy and the Gemini 1.5 comparison each required fewer inferences than the ErrorAtlas
    build.
  evidence: Appendix B, Compute, and Section 3
qa:
- ask:
    practitioner: How can I find out the causes behind a model's wrong answers instead of
      its score?
    unsorted:
    - Why do language models fail on a benchmark, not just how often?
    - Is there a method that diagnoses why LLMs fail rather than where?
  answered_by:
  - context-diagnosis-gap
  - erroratlas-17-categories
- ask:
    practitioner: Where should I begin reading about going beyond benchmark scores to failure
      analysis?
    unsorted:
    - What is a good paper to start with on diagnostic LLM evaluation and error analysis?
    - Which work introduced a general taxonomy of LLM errors?
  answered_by:
  - context-diagnosis-gap
  - context-cheap-reuse
- ask:
    unsorted:
    - What are the most common types of error large language models make?
    - Which failure categories are most prevalent across LLM benchmarks?
    - What does the ErrorAtlas taxonomy contain?
  answered_by:
  - erroratlas-17-categories
  - understudied-errors
- ask:
    unsorted:
    - Which LLM failure modes are neglected by current research?
    - Are incomplete answers and question misinterpretation common LLM errors?
    - What underexplored error types show up in large-scale LLM error analysis?
  answered_by:
  - understudied-errors
- ask:
    unsorted:
    - Do wrong answers on reasoning benchmarks actually reflect weak reasoning?
    - Are MMLU-Pro and GPQA errors really reasoning failures?
    - What fraction of errors on math and science benchmarks are technical rather than reasoning
      problems?
  answered_by:
  - reasoning-benchmarks-nonreasoning-errors
- ask:
    unsorted:
    - How well does the ErrorAtlas taxonomy cover the errors models actually make?
    - Was the LLM-built error taxonomy validated for coverage and accuracy?
    - How reliable are automatic LLM error category assignments?
  answered_by:
  - coverage-95
  - accuracy-92
- ask:
    unsorted:
    - Does an LLM-generated error taxonomy change if you use a different model or sample size?
    - How stable is the ErrorMap taxonomy construction under prompt and sample variation?
    - Is automatic error clustering robust to the choice of judge model?
  answered_by:
  - robustness-sampling
- ask:
    unsorted:
    - Does automatic error analysis agree with human annotation of model mistakes?
    - How does an LLM-produced error breakdown compare to MMLU-Pro's manual error study?
    - Can automated error categorisation replace manual error annotation?
  answered_by:
  - matches-manual-mmlu-pro
- ask:
    practitioner: How can I tell what changed between two versions of a model beyond its benchmark
      score?
    unsorted:
    - What is the difference between Gemini 1.5 Flash and Gemini 1.5 Pro in error types?
    - Can error analysis show which weaknesses a newer model version fixed?
  answered_by:
  - gemini-version-diff
  - per-model-signatures
- ask:
    practitioner: Can I compare models by their failure profile rather than their accuracy?
    unsorted:
    - Do different LLMs with similar scores fail in different ways?
    - Are per-model error distributions statistically distinguishable?
  answered_by:
  - per-model-signatures
- ask:
    unsorted:
    - Do error types vary by subject area within a benchmark?
    - Which MMLU-Pro domains produce the most factual errors?
    - How do failure patterns differ across domains like health, math and history?
  answered_by:
  - domain-error-shifts
- ask:
    unsorted:
    - How expensive is it to run LLM-based error analysis over a benchmark?
    - How long does building an error taxonomy across many models take?
    - Can error analysis be applied at scale without analysing every wrong prediction?
  answered_by:
  - sampling-cost
  - context-cheap-reuse
- ask:
    practitioner: Can I reuse an existing error taxonomy instead of generating my own?
    unsorted:
    - How do I apply ErrorAtlas categories to my own model's failures cheaply?
    - What kinds of tasks can automated error diagnosis not handle?
  answered_by:
  - context-cheap-reuse
misreadings:
- A 95.2% coverage score describes how well ErrorAtlas absorbs the errors it was built from,
  not a guarantee that it covers domains absent from the 35 datasets used; the authors note
  it may represent some specific domains poorly.
- 'ErrorMap does not inspect model internals: its diagnoses are inferred from inputs, references
  and generated outputs, so a model that cannot be run generatively or that emits no explanation
  cannot be analysed.'
- The 92% taxonomy accuracy comes from a meta-judge choosing between the assigned label and
  one random alternative, which is an easier task than free-form labelling and is not a human-annotation
  agreement rate.
- 'The 53% average cosine similarity between error labels under prompt variation is not a
  47% error rate: manual inspection of 100 examples found about 45% captured the same concept
  with partially overlapping phrasing and about 30% differed only in specificity, with about
  25% genuinely different errors.'
- ErrorAtlas category prevalences are shares of sampled wrong predictions, not absolute error
  rates of models; a category being 15.56% of errors says nothing about how often models fail
  overall.
- ErrorMap assigns each failure a single category based on its first major error, so the taxonomy
  does not claim that a mistake has exactly one cause — the authors state error categories
  are inherently soft.
---
