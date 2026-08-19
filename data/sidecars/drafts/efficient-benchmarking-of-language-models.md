<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced via a forced tool call) + 3 repair rounds. Every claim, number
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

Then promote it:  python scripts/draft_sidecars.py --accept efficient-benchmarking-of-language-models

Stamp: spec=74e012ff9654 checks=pass body=980980a90761
-->
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
- q:
  - How can I make language model benchmark evaluation cheaper without making it unreliable?
  - What is efficient benchmarking of language models?
  - Is there research on the compute cost of running LM benchmarks?
  answers:
  - efficient-benchmarking-problem
  - cost-of-full-benchmarks
- q:
  - Should I cut compute on a benchmark by using fewer datasets or fewer examples?
  - Is dropping tasks a good way to shrink an evaluation suite?
  - Which is safer to reduce in HELM, scenarios or examples?
  answers:
  - examples-reliable-scenarios-not
  - rank-stability-under-compute-cuts
- q:
  - How many evaluation examples do I actually need to rank language models?
  - Do HELM model rankings change if only a small sample of evaluation examples is used?
  - How much can HELM compute be reduced before ranks move?
  answers:
  - rank-stability-under-compute-cuts
  - cluster-error-rate
  - equivalence-classes
- q:
  - Can a benchmark reliably tell which language model is best?
  - Is the top of the HELM leaderboard trustworthy?
  - Are small rank differences between LMs on a benchmark meaningful?
  answers:
  - top-model-unreliable
  - equivalence-classes
- q:
  - How do you measure whether a benchmark design decision is reliable?
  - What does DIoR measure and how is it computed?
  - Is there a statistic for benchmark reliability like p-values are for significance?
  answers:
  - dior-measure
- q:
  - Is it bad to group datasets into task categories when aggregating benchmark scores?
  - Does aggregating subscenarios into scenarios hurt reliability?
  - Should benchmark scores be averaged over task groups or over individual datasets?
  answers:
  - no-aggregation
- q:
  - What is the best way to spend a fixed inference budget across few-shot prompts and examples?
  - Should each example be run with every prompt, or should prompts be sampled per example?
  - How should prompt variation be sampled in a benchmark?
  answers:
  - uniform-prompt-sampling
- q:
  - Can mean win rate leaderboards be gamed by submitting extra weak models?
  - Does adding a low-ranked model change who leads a benchmark?
  - What are the problems with win-rate aggregation in LM benchmarks?
  answers:
  - mwr-gameable
- q:
  - What is Flash-HELM and how much compute does it save?
  - Is there a cheap version of HELM that still gives correct ranks?
  - How can a new model be ranked against a leaderboard without running the full benchmark?
  answers:
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
