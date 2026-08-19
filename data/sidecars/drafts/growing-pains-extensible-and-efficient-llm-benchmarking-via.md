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

Then promote it:  python scripts/draft_sidecars.py --accept growing-pains-extensible-and-efficient-llm-benchmarking-via

Stamp: spec=8f05813a4658 checks=pass body=0e6464636226
-->
---
key: habba2026growingpainsextensibleefficient
coined: Sequential fixed parameter calibration
gloss: adding a new benchmark to an evaluation suite by fitting only the new items' parameters
  and locking the old ones, so old and new model scores stay comparable
one_liner: 'Growing Pains treats LLM evaluation under continuously released benchmarks as
  a psychometric scale-linking problem: a multidimensional IRT model calibrates each new dataset
  against fixed anchor items, so a growing suite stays score-comparable without re-running
  previously evaluated models.'
claims:
- id: anchor-100-mae
  kind: result
  text: Sequential fixed parameter calibration predicts a model's full-benchmark accuracy
    to within about 2-3 percentage points of mean absolute error. It needs only 100 anchor
    questions per dataset, on suites of more than 400 models.
  scope: Open LLM Leaderboard (6 datasets, 395 models) and full MMLU as 57 subject datasets
    (428 models), on binary item-level responses from Polo et al. (2024b); reference/test
    models split 75/25 at random.
  evidence: Abstract and Section 7 (Conclusion); MAE curves in Figure 3
- id: no-error-accumulation
  kind: result
  text: Mean absolute error of fixed parameter calibration stays flat rather than accumulating
    as datasets are added one at a time along a calibration chain, closely tracking concurrent
    re-calibration that refits every parameter.
  scope: 12 randomized dataset orderings on the Open LLM Leaderboard and 20 chains on MMLU,
    with means and 95% confidence intervals across chains; English knowledge and reasoning
    tasks with binary correctness only.
  evidence: Figure 3; discussed in Section 4.2 and Section 6
- id: constant-cost
  kind: result
  text: Fixed parameter calibration keeps per-step evaluation cost constant as the benchmark
    suite grows, because each model is evaluated only on the anchors of the newly added dataset.
    Concurrent calibration re-evaluates all accumulated anchors and grows linearly in cost
    with no accuracy gain.
  scope: Open LLM Leaderboard chains with 100 anchors per dataset; cost is counted as the
    number of model-item inferences, and the paper notes IRT calibration compute itself still
    grows slowly as anchor sets accumulate.
  evidence: Figure 2
- id: ranking-spearman
  kind: result
  text: With 100 anchors per dataset, predicted model orderings reach Spearman rho of 0.94
    on the Open LLM Leaderboard and 0.98 on MMLU, against 0.91 and 0.98 for random anchor
    sampling. At N=25 anchors on the Open LLM Leaderboard the gap is larger, 0.88 against
    0.82 for random sampling.
  scope: Held-out test models, 25% of each suite, ranked against their full-evaluation accuracy;
    at N=200 anchors all three methods reach 0.97.
  evidence: Table 3
- id: random-baseline-crossover
  kind: result
  text: Random anchor sampling is a viable substitute for IRT calibration once the anchor
    budget is large. IRT-based methods keep a clear advantage at small budgets such as N=10
    or N=25 anchors, which is where evaluation cost savings are largest.
  scope: Both suites, comparing MAE across anchor budgets; random sampling here means directly
    averaging accuracy on N randomly drawn questions from the new dataset with no IRT model.
  evidence: Figure 3; ranking numbers in Table 3
- id: reference-pool-size
  kind: result
  text: Reliable fixed parameter calibration on the Open LLM Leaderboard requires roughly
    100 or more reference models, while 25 reference models produce unstable error profiles
    there. On MMLU, 25 reference models already give robust prediction quality.
  scope: Reference-pool sweeps on both suites, with 95% confidence intervals across chains;
    MMLU's greater latent overlap is hypothesised, not tested.
  evidence: Figure 5
- id: clustering-beats-topk
  kind: result
  text: Selecting anchors by clustering IRT item representations gives substantially lower
    MAE than selecting the top-K items by discrimination parameter. Representative coverage
    of the item space, not high discrimination alone, is what accurate prediction needs.
  scope: Open LLM Leaderboard (Figure 4) and MMLU (Figure 7), with the rest of the calibration
    pipeline held identical; item maps show top-K anchors concentrate in a narrow high-discrimination
    region.
  evidence: Figure 4 for the Open LLM Leaderboard and Figure 7 for MMLU; item maps in Figures
    6 and 8
- id: anchor-coverage-fraction
  kind: result
  text: 100 anchor questions cover 0.7% of MMLU's 14,042 items and 1.0% of HellaSwag's 10,082
    items. On the smallest Open LLM Leaderboard dataset, TruthfulQA with 857 items, the same
    budget is 11.7% of the dataset.
  scope: Open LLM Leaderboard datasets at N=50 and N=100 anchors; on MMLU subjects the fraction
    at N=50 ranges from 3.3% of Professional Law to 50% of the 100-item Abstract Algebra subject.
  evidence: Table 2
- id: scale-linking-framing
  kind: context
  text: Growing Pains formulates LLM evaluation under evolving benchmark coverage as a psychometric
    scale-linking problem, where datasets arrive over time and models are only evaluated on
    the datasets available at their evaluation date.
  scope: As of the paper's 2026 arXiv posting; prior efficient-evaluation work such as tinyBenchmarks
    treated each benchmark as a closed static pool, and prior IRT work in NLP focused on ability
    estimation within a fixed item pool.
- id: fpc-first-in-llm-eval
  kind: context
  text: Growing Pains applies fixed parameter calibration, a long-established test-equating
    procedure from psychometrics, to LLM benchmarking, holding anchor item parameters constant
    so ability estimates from different evaluation periods stay comparable.
  scope: The procedure dates to Kim and Cohen (1996) in psychometrics and the paper states
    it had not previously been applied to LLM evaluation; the transfer is validated only on
    English knowledge and reasoning benchmarks with binary correctness.
  evidence: Section 2.3
- id: retroactive-estimation
  kind: context
  text: Growing Pains supports two evaluation workflows from one calibrated model. A brand-new
    model is scored from its anchor responses alone, and already-evaluated historical models
    are estimated retroactively on a newly added dataset.
  scope: Both workflows assume the new dataset's items can be calibrated against the existing
    latent space; the paper expects accuracy to degrade when a new benchmark tests a capability
    largely absent from the existing suite.
qa:
- q:
  - How many questions do I need to run to estimate a model's full benchmark score?
  - How accurate is IRT-based anchor-item prediction of full-evaluation accuracy?
  - Can 100 anchor questions per dataset replace running a model on the whole benchmark suite?
  answers:
  - anchor-100-mae
  - anchor-coverage-fraction
- q:
  - Does prediction error build up as more datasets are added to an evaluation suite?
  - Does IRT calibration degrade over long chains of benchmark additions?
  - Is fixed parameter calibration as accurate as refitting all IRT parameters from scratch?
  answers:
  - no-error-accumulation
- q:
  - How can I add a new benchmark to a leaderboard without re-evaluating every existing model?
  - What is the cost of extending an evaluation suite with a new dataset?
  - Why is joint re-calibration of all item parameters expensive when benchmarks keep arriving?
  answers:
  - constant-cost
  - retroactive-estimation
- q:
  - Are model rankings preserved when scores are predicted from a small item subset?
  - What Spearman correlation does anchor-based prediction achieve with full-evaluation rankings?
  - Does subsampling a benchmark change the leaderboard order?
  answers:
  - ranking-spearman
- q:
  - Is random subsampling of benchmark questions good enough, or do I need IRT?
  - When does IRT-based item selection beat just averaging a random sample of questions?
  - Does psychometric modelling of benchmark items still help at large sample sizes?
  answers:
  - random-baseline-crossover
- q:
  - How many models do I need to calibrate an IRT model for benchmark prediction?
  - How large must the reference model pool be for reliable anchor calibration?
  - Why does MMLU need fewer reference models than the Open LLM Leaderboard?
  answers:
  - reference-pool-size
- q:
  - Should anchor questions be the most discriminative items in a benchmark?
  - How should representative benchmark subsets be chosen for efficient evaluation?
  - Does picking high-discrimination items beat clustering-based anchor selection?
  answers:
  - clustering-beats-topk
- q:
  - What should I read about keeping LLM benchmark scores comparable as benchmarks change?
  - Which paper connects psychometric test equating to LLM evaluation?
  - Where can I start reading about efficient and extensible LLM benchmarking?
  - What work frames benchmark growth as a scale-linking problem?
  answers:
  - scale-linking-framing
  - fpc-first-in-llm-eval
- q:
  - Can I estimate how older models would have scored on a benchmark released after they were
    evaluated?
  - Is retroactive scoring of historical models on new datasets possible without re-inference?
  answers:
  - retroactive-estimation
- q:
  - What fraction of a benchmark do 100 anchor items actually represent?
  - How does anchor budget relate to dataset size in the Open LLM Leaderboard and MMLU?
  answers:
  - anchor-coverage-fraction
misreadings:
- The 2-3 percentage point prediction error is validated on English knowledge and reasoning
  benchmarks with binary correct/incorrect responses; the framework does not yet handle graded
  or open-ended evaluation formats, which would require changes to the IRT formulation.
- 'Fixed parameter calibration does not make evaluation free: models still have to be run
  on the anchors of each newly added dataset, and the calibration compute itself grows slowly
  as anchor sets accumulate.'
- The flat error profiles do not imply that any new benchmark can be linked in successfully.
  Prediction quality depends on overlap with the already-calibrated latent space, and a benchmark
  probing a capability absent from existing tasks is expected to be predicted worse.
- Fixed parameter calibration is not shown to be more accurate than concurrent re-calibration;
  it matches concurrent calibration's accuracy while keeping cost constant and keeping historical
  ability estimates comparable.
- The reference/test model split in Growing Pains is random rather than time-ordered, so the
  reported errors may understate the difficulty of generalising to future models that differ
  systematically from the reference population.
- 'Anchor items are assumed to keep stable statistical properties, which does not hold indefinitely:
  contaminated or saturated anchors would require recalibration.'
terminology:
  Fixed parameter calibration (FPC): A test-equating procedure in which the item parameters
    of previously calibrated anchor items are held constant while only the parameters of newly
    introduced items are estimated, so latent ability estimates keep a consistent meaning
    across calibration rounds.
  Concurrent calibration: The standard IRT alternative in which all item parameters and all
    model abilities are jointly re-estimated on the accumulated data every time a new benchmark
    is added, which shifts previously estimated parameters and makes historical ability estimates
    incomparable.
  Anchor items: A small fixed subset of a dataset's questions, selected by clustering IRT
    item representations, whose calibrated parameters serve as the common reference linking
    scores collected in different evaluation periods.
  Chain: A simulated sequence of dataset releases in which one dataset is added to the evaluation
    suite at each step and prediction quality is measured at every step, so error accumulation
    over long sequences can be tested.
  MIRT 2PL: The multidimensional 2-parameter logistic Item Response Theory model, in which
    each item has a discrimination vector over several latent skill dimensions plus an intercept
    related to difficulty, and each model's ability is a vector over those dimensions.
links_extra:
  project page: https://eliyahabba.github.io/growing-pains/
  code: https://github.com/eliyahabba/growing-pains
---
