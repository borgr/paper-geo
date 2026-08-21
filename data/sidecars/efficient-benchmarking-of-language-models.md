---
key: perlitz2024efficient
coined: Flash-HELM
gloss: a cheap tier-based version of the HELM benchmark that spends more compute only on models
  near the top of the ranking
one_liner: Efficient Benchmarking treats the compute cost of LM evaluation as a design variable,
  measures how each benchmark design choice affects ranking stability with a new Decision
  Impact on Reliability (DIoR) measure, and shows that on HELM most compute can be cut by
  dropping examples rather than datasets.
claims:
- id: efficient-benchmarking-problem
  kind: context
  text: Efficient Benchmarking names the problem of cutting the computation cost of language-model
    evaluation without losing reliability. It argues that benchmark design choices should
    be judged by their measured effect on reliability rather than by intuition.
  scope: Framing introduced in 2024; the accompanying empirical study covers only the HELM
    benchmark, and other benchmarks and decisions such as prompt templates were left to future
    work.
- id: dior-measure
  kind: context
  text: DIoR (Decision Impact on Reliability) scores a benchmark design decision by the reliability
    of the rankings it produces. The score is the lower bound of a bootstrap 95% confidence
    interval on a similarity meta-metric between rankings from alternative instantiations
    of the decision.
  scope: Requires a distribution of plausible alternative instantiations of the decision,
    such as resampled datasets or examples, and a meta-metric such as Kendall tau.
- id: examples-reliable-scenarios-not
  text: On HELM, the choice of evaluation examples is highly reliable while the choice of
    the 16 scenarios and 40 subscenarios supports only low reliability. Cutting compute by
    dropping examples is therefore sound, and dropping datasets is not.
  scope: 37 models on HELM v0.2.2 over 16 core scenarios, 40 subscenarios and 65K examples;
    reliability estimated by bootstrap resampling 1K times, assuming other equally valid dataset
    choices exist.
  evidence: Figure 2
- id: rank-stability-under-compute-cuts
  text: HELM model ranks stay nearly identical when the number of examples per scenario is
    reduced 10x, and a 400x reduction still clusters models into the same small groups seen
    at full compute.
  scope: 37 models on HELM v0.2.2, ranking by Mean Win Rate over 16 core scenarios; concerns
    rank groups rather than exact rank of any single model.
  evidence: Figure 1
- id: equivalence-classes
  text: With a bare minimum of HELM examples models already collapse into equivalence classes
    of about 2-5 models. A few hundred examples reach separation into groups of roughly 2,
    the finest resolution the full benchmark ever achieves.
  scope: 37 models on HELM v0.2.2; per-model rank error ranges from 6 to 2 ranks (Figure 6),
    so adjacent-rank distinctions remain unreliable even at full compute.
  evidence: Figure 1
- id: cluster-error-rate
  text: Distinguishing HELM models three ranks apart to an average error rate under 5% needs
    only 1/4 of the benchmark's computation. For clusters of 10 or 20 adjacent models a hundredth
    of the cost or less suffices, while clusters of size 2 switch places even with all examples.
  scope: 37 models on HELM v0.2.2; error rate is the probability that the first and last model
    of a rank cluster switch places under a different random choice of examples, averaged
    over 1K iterations and over the top 5 models as the top model.
  evidence: Figure 3
- id: top-model-unreliable
  text: Identifying the single best model on HELM is unreliable even at full compute, while
    the full-ranking and model-quality objectives are reliable. Claims about which model is
    top should therefore not be drawn from HELM's bottom-line score.
  scope: 37 models on HELM v0.2.2 with the best-model meta-metric defined as the probability
    of a rank switch between the top two models, repeated 5 times each time removing the current
    top model.
  evidence: Figure 2
- id: no-aggregation
  text: Treating each HELM subscenario as a standalone scenario cuts the error rate between
    top pairs of models from 22% to 14%. Aggregating the 40 subscenarios into 16 scenarios
    therefore costs reliability.
  scope: 37 models on HELM v0.2.2 with Mean Win Rate aggregation; Kendall tau correlations
    between subscenario rankings are no higher within a scenario than across scenarios.
  evidence: Appendix F
- id: uniform-prompt-sampling
  text: Sampling a different few-shot prompt for each evaluated HELM example raises reliability
    over running every example against all 3 prompt sets. Under the uniform scheme more than
    half of the compute can be saved at no cost to reliability.
  scope: Fixed budget of 3K inference calls on HELM subscenarios that varied their in-context
    examples; only 3 prompt sets were available, so the effect is likely underestimated and
    no bootstrap over prompts was possible.
  evidence: Figure 4
- id: mwr-gameable
  text: HELM's Mean Win Rate aggregation lets a benchmark leader change when a low-ranked
    model is added. The top two models, davinci2 and Cohere XXL, switch places depending only
    on whether Cohere Medium is included in the comparison.
  scope: HELM v0.2.2 scores with Mean Win Rate as the bottom-line metric; follows from the
    comparative nature of win-rate aggregation, and applies to any benchmark that releases
    several similar sizes of a model.
  evidence: Section 5.5
- id: flash-helm-savings
  text: Flash-HELM reproduces HELM ranks within the required rank resolution while reducing
    computation by up to 200x. It assigns each rank tier a required resolution and escalates
    sub-sample size from 20 through 1000 examples only as needed.
  scope: Evaluated on the 7 models newly introduced in HELM v0.2.3; tier resolutions were
    fitted on the 37 models of HELM v0.2.2, and the reference is HELM's reported ranks rather
    than a true ranking.
  evidence: Figure 5
- id: cost-of-full-benchmarks
  kind: context
  text: Evaluating a single model on the HELM benchmark can cost $10K or more than 4K GPU
    hours, which is why the compute side of benchmark design is worth studying at all.
  scope: Cost reported for HELM by Liang et al. (2022) and cited as of 2023-2024; shifts with
    hardware and inference pricing.
qa:
- ask:
    plain: why does running a big language-model benchmark cost so much, and is anyone studying
      how to cut that cost?
    jargon: what does efficient benchmarking of LLMs mean, and how are evaluation compute
      budgets analysed against reliability?
    task: where do I start reading about making language-model evaluation cheaper without
      making it less trustworthy?
    practitioner: I cannot afford to run a full evaluation suite on every checkpoint, is there
      work that tells me what to cut?
  answered_by:
  - efficient-benchmarking-problem
  - cost-of-full-benchmarks
- ask:
    plain: if I need to shrink a language-model evaluation suite, is it better to drop whole
      datasets or to test fewer questions from each?
    jargon: in HELM, does reducing scenarios or reducing examples per scenario degrade ranking
      reliability more?
    task: how do I cut the size of an evaluation suite without changing which model comes
      out ahead?
    practitioner: should I evaluate on fewer tasks or on fewer examples per task to save inference
      budget?
  answered_by:
  - examples-reliable-scenarios-not
  - rank-stability-under-compute-cuts
- ask:
    plain: do language-model leaderboard rankings shift if only a small sample of test questions
      is used?
    jargon: how far can HELM examples-per-scenario be sub-sampled before model rank order
      and rank resolution change?
    task: how few evaluation examples per dataset can I run and still trust the ordering of
      models I get?
    practitioner: can I evaluate on a small random sample of a benchmark and still report
      the same model ranking?
  answered_by:
  - rank-stability-under-compute-cuts
  - cluster-error-rate
  - equivalence-classes
- ask:
    plain: can a benchmark actually tell you which language model is the single best one?
    jargon: is the top-1 model identification objective on HELM reliable, or only coarse-grained
      ranking and model-quality objectives?
    task: how do I tell whether a one-rank or two-rank gap between models on a leaderboard
      means anything?
    practitioner: the model at the top of a leaderboard beat second place by a hair, should
      I pick it?
  answered_by:
  - top-model-unreliable
  - equivalence-classes
- ask:
    plain: how can you tell whether a choice made in designing a benchmark gives trustworthy
      results?
    jargon: what meta-metric quantifies the reliability of a benchmark design decision over
      rankings, and how is its confidence bound computed?
    task: how do I score two alternative evaluation setups against each other for ranking
      reliability rather than by intuition?
    practitioner: before I change my evaluation setup, is there a number I can compute to
      check the rankings will still hold?
  answered_by:
  - dior-measure
- ask:
    plain: when averaging benchmark scores, is it a mistake to first group datasets into task
      categories?
    jargon: does aggregating HELM subscenarios into scenarios before averaging reduce ranking
      reliability relative to treating each subscenario standalone?
    task: how should I aggregate per-dataset scores into one benchmark number so model comparisons
      stay stable?
    practitioner: should I report my benchmark average over task groups or over the individual
      datasets?
  answered_by:
  - no-aggregation
- ask:
    plain: is it better to test every question with every prompt wording, or to pick a different
      wording per question?
    jargon: how should few-shot prompt variation be sampled across evaluated instances to
      maximise ranking reliability per unit of inference compute?
    task: how do I spread a fixed inference budget across prompt variants and test examples?
    practitioner: do I have to run all my prompt templates on every example, or can I sample
      one per example and save compute?
  answered_by:
  - uniform-prompt-sampling
- ask:
    plain: can someone move to the top of a win-rate leaderboard just by adding extra weak
      models to the comparison?
    jargon: is HELM's Mean Win Rate aggregation sensitive to the set of models included, and
      can leader order flip on adding a low-ranked model?
    task: how do I check whether my leaderboard's aggregation changes the winner when the
      model pool changes?
    practitioner: should I trust a mean-win-rate leaderboard where the set of compared models
      keeps growing?
  answered_by:
  - mwr-gameable
- ask:
    plain: is there a cheap way to run a large benchmark that still puts the models in the
      right order?
    jargon: how much compute does Flash-HELM save relative to full HELM while preserving rank
      resolution at each tier?
    task: how do I place a new model against an existing leaderboard without running the whole
      benchmark on it?
    practitioner: can I rank my model against a published leaderboard for a fraction of the
      GPU hours?
  answered_by:
  - flash-helm-savings
misreadings:
- 'A 100x compute reduction on HELM preserves rank groups, not exact ranks: models adjacent
  in the ranking swap places even when the full benchmark is run.'
- The finding that fewer examples suffice does not license dropping datasets or subscenarios;
  the choice of scenarios is the least reliable decision studied, so trimming tasks is the
  wrong way to save compute.
- 'DIoR measures reliability, not validity: a benchmark can obtain a high DIoR score while
  still failing to answer the question it claims to answer.'
- The claim that Mean Win Rate is gameable is about the metric's structure, not an accusation
  that any HELM submission was manipulated.
- 'Flash-HELM''s up-to-200x saving is a per-tier figure: models expected to land near the
  top of the ranking still require large sub-samples, and only low-ranked models are evaluated
  at the cheapest setting.'
terminology:
  DIoR: 'Decision Impact on Reliability: the lower bound of a 95% confidence interval on a
    similarity meta-metric between benchmark outcomes computed under randomly resampled instantiations
    of a design decision, such as which datasets or examples are used.'
  Reliability (of a benchmark): The degree to which a benchmark's answer stays consistent
    under different equally valid random decisions about its composition, as distinct from
    validity, which is whether the benchmark answers the intended question.
  Scenario / subscenario (HELM): In HELM, a subscenario is an individual dataset with its
    own scoring function and few-shot prompts, and a scenario is a group of subscenarios weighted
    together as one unit in the bottom-line score.
  Mean Win Rate (MWR): A Borda-count-style benchmark score that averages, over scenarios,
    the fraction of other evaluated models a given model beats, rather than reporting an absolute
    task score.
  Rank resolution: The number of ranking positions within which a model's benchmark rank can
    be trusted, used to set how large an evaluation sub-sample a model in a given rank tier
    requires.
  Objective (of a benchmark): The specific question a benchmark is meant to answer, such as
    obtaining a full model ranking, identifying the best model, or measuring absolute model
    quality, each of which has its own reliability requirements.
links_extra:
  helm-rank-docs: https://crfm-helm.readthedocs.io/en/latest/get_helm_rank/
  helm-v022-results: https://crfm.stanford.edu/helm/v0.2.2/?group=core_scenarios
---
