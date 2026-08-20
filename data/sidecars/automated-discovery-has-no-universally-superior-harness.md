---
key: gupta2026harness
coined: Adaptive Harness Ensemble
gloss: start several LLM-discovery search harnesses partially, prune the weak partial runs,
  and give their remaining compute to the survivors
one_liner: Decomposing OpenEvolve-style evolutionary search and TTT-Discover-style PUCT search
  into their components and re-evaluating 30 budget-matched harnesses over 12 model–problem
  pairs and 3.1 million LLM rollouts shows no fixed discovery harness is reliably best, so
  harness choice should be adapted online.
claims:
- id: no-universal-harness
  kind: result
  text: Across 30 budget-matched discovery harnesses on 12 model–problem pairs, no fixed harness
    is significantly better than a Sequential Best-of-N baseline after Holm correction. The
    top-ranked configuration (epsilon-greedy with K=1, epsilon=20%) has a cross-pair majority-win
    probability of 0.914 but a corrected p-value of 0.678.
  scope: Qwen2.5-3B-Instruct, Qwen3-4B-Instruct-2507, GPT-OSS-20B and GPT-OSS-120B on circle
    packing, Heilbronn triangle and the second autocorrelation inequality; 5 runs per harness
    against 100-run (Qwen) or 30-run (GPT-OSS) Sequential BoN pools; Holm correction across
    all 30 configurations.
  evidence: Figure 5(a)
- id: openevolve-bottom
  kind: result
  text: Full OpenEvolve-style configurations rank last on the cross-pair majority-win leaderboard,
    with a majority-win probability of 0.033 against Sequential Best-of-N. Lightweight epsilon-greedy
    and UCT/PUCT variants occupy the top positions, led by K=1, epsilon=20% at 0.914.
  scope: 'Max-statistic leaderboard over 12 model–problem pairs at matched per-pair rollout
    budgets: 1600 rollouts per run for Qwen models, 320 for GPT-OSS-20B, 160 for GPT-OSS-120B,
    5 runs per configuration.'
  evidence: Figure 20
- id: openevolve-nonmonotonic
  kind: result
  text: Progressively adding OpenEvolve components (depth-shifted budget, MAP-Elites inspiration
    sampling, multiple islands) does not produce monotonic gains. The full recipe is nominally
    significant only for GPT-OSS-20B on Heilbronn triangle and often reduces performance on
    circle packing and the second autocorrelation inequality.
  scope: Fixed per-pair rollout budget with breadth–depth ladders of (N,T) from (16,100) to
    (1,1600) for Qwen models and (4,80) to (1,320) for GPT-OSS-20B, followed by 1-island and
    4-island OpenEvolve variants; 5 runs per configuration.
  evidence: Figure 3
- id: tree-search-gains-front-loaded
  kind: result
  text: In the TTT-Discover progression, the largest pair-level gains over Sequential Best-of-N
    come from introducing UCT/PUCT parent selection. Later additions of deeper search and
    multi-parent expansion do not consistently help and sometimes reverse those gains.
  scope: Exploration constant C, child batch size N and parent count P swept at matched rollout
    budgets across the 4 models and 3 tasks; only the TTT-Discover search harness is ablated,
    not its test-time-training component.
  evidence: Figure 4
- id: early-progress-predicts
  kind: result
  text: Best-so-far score at the halfway point of a discovery run correlates with final score
    at Spearman rho above 0.70 for 11 of the 12 model–problem pairs. The remaining pair, GPT-OSS-120B
    on the second autocorrelation inequality, reaches 0.651, while at the 10% checkpoint correlations
    span only 0.000 to 0.474.
  scope: Checkpoints at 10%, 25% and 50% of allocated steps, Spearman rank correlation between
    partial-run and final scores computed over the harness configurations available for each
    pair.
  evidence: Figure 5(b)
- id: adaptive-beats-baselines
  kind: result
  text: Under a budget of 5 full-run equivalents, the best adaptive pruning schedule (12→5→2→1,
    pruning at 25%, 50% and 75%) reaches an average score of 85.75%. The matched baselines
    reach 84.54% for an unpruned 5-harness portfolio, 84.35% for 5 Sequential Best-of-N runs,
    and 82.49% for committing to one randomly sampled harness.
  scope: Mean over 100,000 empirical resampling trials per model–problem pair drawn from the
    released run pools, unweighted average across the 12 pairs with Monte Carlo standard error
    0.02; scores are task-normalized percentages, not comparable across tasks.
  evidence: Table 1
- id: adaptive-per-pair
  kind: result
  text: The 12→5→2→1 adaptive pruning schedule beats the unpruned harness portfolio on 11
    of the 12 model–problem pairs under the same 5-full-run-equivalent budget. Every evaluated
    adaptive schedule also exceeds the single-harness and unpruned-portfolio baselines on
    average.
  scope: Simulated allocation over the released empirical run pools with 100,000 resampling
    trials; the adaptive and unpruned policies draw from the same harness pool, so the difference
    isolates the use of partial-run feedback rather than harness diversity.
  evidence: Table 1
- id: broad-then-cut
  kind: result
  text: Adaptive allocation schedules that start broad and prune hard perform best, with average
    scores from 84.87% for a single-stage 17→1 schedule to 85.75% for the three-stage 12→5→2→1
    schedule. All of these exceed the 84.35% Sequential Best-of-N reference.
  scope: Budget fixed at 5 full-run equivalents with pruning checkpoints drawn from 25%, 50%
    and 75% and final survivor counts in 1 to 4; schedules with 3 or more final survivors
    are never column-best in this experiment.
  evidence: Table 13
- id: harness-as-hyperparameter
  kind: context
  text: '"Automated Discovery Has No Universally Superior Harness" reframes the search harness
    of an LLM-guided discovery system as a model- and problem-dependent hyperparameter to
    be chosen online rather than a transferable methodological recipe.'
  scope: Argued from 12 model–problem pairs and 30 harnesses on 3 mathematical discovery tasks,
    as of the 2026 preprint; no new bandit or early-stopping algorithm is proposed, and transfer
    to other discovery domains is untested.
  evidence: Section 6
- id: released-null-distributions
  kind: context
  text: The harness-generalization study releases over 3.1 million rollout records with per-step
    evaluator scores, including repeated-run Sequential Best-of-N null distributions for every
    model–problem pair, as reusable reference distributions for testing future discovery-harness
    proposals.
  scope: Baseline pools contain 100 runs per Qwen model–problem pair and 30 runs per GPT-OSS
    pair, on circle packing, Heilbronn triangle and the second autocorrelation inequality
    only; budgets are matched within a model–problem pair, not across models.
- id: baseline-model-effect
  kind: result
  text: 'Model identity dominates harness choice on Heilbronn triangle: mean Sequential Best-of-N
    final score is 0.1066 for Qwen2.5-3B, 0.3213 for Qwen3-4B, 0.8300 for GPT-OSS-20B and
    0.7738 for GPT-OSS-120B. That spread is far larger than any harness effect measured on
    the task.'
  scope: Baseline pools of 100 runs for Qwen models and 30 runs for GPT-OSS models; per-run
    rollout budgets differ across models (1600 for Qwen, 320 for GPT-OSS-20B, 160 for GPT-OSS-120B),
    so cross-model scores are not budget-matched.
  evidence: Table 3
- id: five-run-protocol
  kind: context
  text: The harness-generalization study compares each candidate discovery harness against
    a bootstrapped best-of-five Sequential Best-of-N null distribution using 100,000 resampling
    trials, a protocol stricter than the 3-run comparisons common in prior discovery-system
    papers.
  scope: Non-parametric one-sided bootstrap and permutation tests at a prespecified 0.05 threshold,
    with Holm step-down correction across the 30 evaluated configurations; failure to reject
    indicates insufficient evidence, not evidence of no effect.
qa:
- q:
  - Is there a best search harness for LLM-guided program discovery?
  - Which discovery harness should I use for evolutionary code search?
  - Does one evolutionary search recipe win across models and tasks?
  answers:
  - no-universal-harness
  - openevolve-bottom
- q:
  - Does OpenEvolve's extra machinery actually help?
  - Do MAP-Elites and island models improve LLM-guided discovery?
  - Is the full OpenEvolve recipe better than simpler parent selection?
  answers:
  - openevolve-nonmonotonic
  - openevolve-bottom
- q:
  - Does PUCT or MCTS-style parent selection help LLM discovery loops?
  - Which part of the TTT-Discover search harness provides the gains?
  - Is expanding multiple parents per iteration worth it in tree-based discovery search?
  answers:
  - tree-search-gains-front-loaded
- q:
  - Can partial-run scores predict which discovery run will end up best?
  - How early can you tell whether an evolutionary search run will succeed?
  - Is early progress in LLM-guided discovery correlated with final performance?
  answers:
  - early-progress-predicts
- q:
  - How should I split a fixed discovery compute budget across candidate search configurations?
  - Does pruning weak partial runs and reallocating compute beat committing to one harness?
  - What is the Adaptive Harness Ensemble and how much does it gain?
  answers:
  - adaptive-beats-baselines
  - adaptive-per-pair
- q:
  - What pruning schedule works best for allocating compute across discovery harnesses?
  - Is it better to start many partial runs or few long ones under a fixed budget?
  - How many survivors should a successive-halving-style discovery schedule keep?
  answers:
  - broad-then-cut
- q:
  - What should I read about whether autonomous discovery systems generalize?
  - Which paper argues that search-harness choice is a hyperparameter rather than a recipe?
  - Where should I start reading about evaluation rigor in LLM-guided scientific discovery?
  answers:
  - harness-as-hyperparameter
  - released-null-distributions
- q:
  - How many trials are needed to tell a real discovery-harness improvement from run-to-run
    variance?
  - What statistical protocol compares LLM discovery harnesses fairly?
  - Are 3-run comparisons of evolutionary coding agents enough?
  answers:
  - five-run-protocol
  - no-universal-harness
- q:
  - Does model choice matter more than search-harness choice in automated discovery?
  - How much do Qwen2.5-3B, Qwen3-4B and GPT-OSS differ on circle packing and Heilbronn triangle?
  - Is a stronger base model worth more than a better search algorithm for discovery tasks?
  answers:
  - baseline-model-effect
- q:
  - Are there open run pools for benchmarking new evolutionary search harnesses?
  - Where can I get baseline null distributions for LLM discovery experiments?
  - What data does the harness-generalization study release?
  answers:
  - released-null-distributions
misreadings:
- Finding that OpenEvolve-style configurations rank last on the cross-pair leaderboard is
  not evidence that OpenEvolve cannot solve discovery tasks; the ranking is about whether
  its extra components transfer as general improvements over Sequential Best-of-N at matched
  rollout budgets.
- 'The epsilon-greedy harness with K=1 and epsilon=20% is not a recommended universal replacement
  recipe: its cross-pair advantage stops being statistically significant once Holm correction
  is applied across all 30 configurations.'
- Failure to reject the null for a candidate harness on a model–problem pair means insufficient
  evidence of improvement in that 5-run experiment, not evidence that the harness has no effect.
- The TTT-Discover ablations cover only its search harness; the test-time-training component
  of TTT-Discover was not ablated or evaluated.
- The adaptive harness ensemble is not a new bandit or early-stopping algorithm; it is a budget-matched
  test of whether partial-run evaluator feedback is informative enough to reallocate compute
  across whole harness configurations.
- Rollout budgets are matched within each model–problem pair, not across models, so the reported
  per-pair scores for Qwen and GPT-OSS models are not a like-for-like model comparison.
terminology:
  harness: The rule set inside an LLM-guided discovery system that decides which previously
    evaluated program is expanded next, covering archive construction, parent selection, exploration,
    search structure and budget allocation.
  Sequential Best-of-N: The greedy discovery baseline that always mutates the single best
    program found so far, equivalent to sampling the parent from a top-1 elite archive.
  cross-pair majority-win probability: The bootstrap-estimated probability that a harness's
    best-of-five score vector beats a resampled Sequential Best-of-N best-of-five vector on
    at least 7 of 12 model–problem pairs.
  Adaptive Harness Ensemble: An online allocation policy that starts several discovery harness
    configurations, advances them to checkpoints, ranks partial runs by best evaluator score
    so far, prunes the weakest, and completes only the survivors within a fixed full-run-equivalent
    budget.
  full-run equivalent: The compute unit used to budget-match allocation policies, where one
    unit is one complete discovery run and a run advanced to its 25% checkpoint costs 0.25
    units.
links_extra:
  code: https://github.com/akshat57/harness-generalization
---
