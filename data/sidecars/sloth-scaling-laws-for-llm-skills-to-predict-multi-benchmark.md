---
key: polo2024sloth
coined: Sloth
gloss: skills scaling laws — predicting a large LLM's benchmark scores from low-dimensional
  latent skills fitted on public leaderboard data
one_liner: Sloth fits scaling laws on public leaderboard data by assuming benchmark scores
  are driven by a few latent skills that grow with model size and training tokens at a family-specific
  efficiency, so predicting a larger model in a new family needs as little as one observed
  model from that family.
claims:
- id: prediction-competitive
  kind: result
  text: Sloth predicts held-out LLM benchmark performance with mean absolute error similar
    to or lower than the "Size and Tokens" variant that models all 12 benchmarks separately.
    It also matches or beats the FLOPs-based scaling law of Owen (2024) and a PCA adaptation
    of Ruan et al. (2024).
  scope: Leave-one-out over LLM families on Open LLM Leaderboard v1 and v2 (12 benchmarks),
    with only the smallest model of the test family in the training set; base and instruct
    models treated as separate families.
  evidence: Figure 1
- id: mape-same-conclusion
  kind: result
  text: Sloth gives the best predictions on both Open LLM Leaderboards when error is measured
    as mean absolute percentage error rather than mean absolute error.
  scope: Same leave-one-out family split as the MAE experiment, one model of the test family
    observed; measured in percentage points.
  evidence: Figure 10
- id: one-model-per-family
  kind: result
  text: Sloth needs data from only 1 model of a new LLM family to estimate that family's efficiency
    intercepts and then predict a larger, untrained model in the same family. Fitting family-dependent
    slopes as in Ruan et al. (2024) instead requires at least 2 models.
  scope: The family's efficiency has to be captured by an intercept shared across sizes; the
    second experiment with 2 observed models per test family gives qualitatively similar errors.
  evidence: Section 4.2 and Figure 16
- id: three-skills
  kind: result
  text: Three latent skills, labelled Reasoning, Knowledge and Instruction Following, account
    for performance across the 12 Open LLM Leaderboard benchmarks. GSM8K, MATH, GPQA, MMLU(-PRO),
    BBH and MuSR load on Reasoning, ARC, HellaSwag and Winogrande on Knowledge, and IFEval
    on Instruction Following.
  scope: Loadings estimated on the 15 families in the intersection of Leaderboard v1 and v2
    with d=3, sigmoid link and fixed lower asymptotes, then Geomin-rotated; the skill names
    are the authors' subjective reading of the loadings, and the Instruction Following interpretation
    does not hold at d=4.
  evidence: Figure 2
- id: reasoning-size-driven
  kind: result
  text: Reasoning skill is primarily a function of parameter count, with only small dependence
    on the number of training tokens. Knowledge instead is strongly influenced by both parameter
    count and training tokens, and varies over a wider range of standard deviations.
  scope: Level curves of skills with the family-specific intercept removed, d=3, fitted on
    the intersection of Open LLM Leaderboard v1/v2; skills standardized to zero mean and unit
    standard deviation.
  evidence: Figure 4
- id: instruction-tuning-effects
  kind: result
  text: Instruction tuning raises the Instruction Following skill strongly and consistently
    across every family plotted, has a moderate negative effect on Reasoning, and mixed effects
    on Knowledge.
  scope: Base versus instruction-tuned pairs from the families with the most models in the
    dataset, d=3 fit on the leaderboard intersection; skill changes read in standard-deviation
    units.
  evidence: Figure 5
- id: instruction-tuning-dominates-compute
  kind: result
  text: Instruction tuning shifts the Instruction Following skill by much more, in standard-deviation
    units, than varying model size and training tokens does.
  scope: Comparison of base/instruct skill gaps against skill level curves over the observed
    ranges of parameter count and tokens, d=3, leaderboard intersection.
  evidence: Figure 5
- id: downstream-humaneval
  kind: result
  text: Skills that Sloth predicts for a held-out LLaMa 3 70B, base and instruct, support
    accurate prediction of its HumanEval code-completion score. Reasoning is by far the most
    important skill for coding in the second-stage logistic regression.
  scope: LLaMa 3 70B base and instruct excluded from the Sloth fit; second-stage logistic-link
    regression fitted on models with HumanEval data; the AgentBench case required Sloth without
    family-specific intercepts to avoid overfitting.
  evidence: Figure 6
- id: test-time-scaling
  kind: result
  text: Sloth combined with per-question item response models predicts pass@k curves under
    repeated sampling on MATH for held-out LLaMa 3 Instruct, Gemma and Pythia models. The
    per-question logistic regressions are fitted on the skills of 7 training LLMs.
  scope: 10 LLMs with MATH repeated-sampling data from Brown et al. (2024), with the largest
    model of each of the 3 families held out of both the Sloth fit and the per-question regressions;
    pass@k predicted as the average of 1-(1-p)^k over questions.
  evidence: Figure 7
- id: compute-optimal-skills
  kind: result
  text: Compute-optimal allocation differs sharply by skill at a budget of 3346e19 FLOPs.
    Maximizing Reasoning calls for 30.98B parameters and 0.18T tokens, while maximizing Knowledge
    calls for 0.37B parameters and 15.0T tokens.
  scope: Derived from the fitted translog skill model under the constraint 6st=c, with parameter
    and token ranges clipped to quantiles of the training data support; the optimal allocation
    does not depend on the model family.
  evidence: Table 2
- id: parameter-efficiency
  kind: result
  text: With d=3 latent skills and 12 benchmarks, Sloth uses 69+3f parameters for f model
    families, against 36+12f for the FLOPs baseline and 50+12f for the "Size and Tokens" baseline.
    Sloth is therefore smaller than either for any f of 4 or more.
  scope: Parameter counts for the stated configuration (d=3, 12 benchmarks); the trainable-link
    version adds neural-network weights per benchmark beyond this count.
  evidence: Appendix F
- id: identifiability
  kind: result
  text: Sloth's loadings and skill-production coefficients are identifiable up to an invertible
    d-by-d transformation of the latent space, which becomes an orthogonal rotation when the
    skill covariance is the identity. That licenses factor rotation for interpretation.
  scope: Proved for the "basic" Sloth with fixed invertible link and fixed lower asymptotes,
    under standardized skills, rank(Lambda)=d and rank(X)=p; identifiability of the trainable-link
    version is not established.
  evidence: Theorem A.2
- id: context-position
  kind: context
  text: Sloth targets the gap between a single scaling law fitted across all LLMs, which ignores
    family differences, and family-specific scaling laws, which require training several models
    per family. It bridges them by tying benchmark scores to shared latent skills with family-specific
    efficiency intercepts.
  scope: Positioned against benchmark and observational scaling laws as of 2025, in particular
    Owen (2024), Ruan et al. (2024) and Gadre et al. (2024). Concerns benchmark and downstream-task
    accuracy rather than pretraining loss.
  evidence: Section 2.2
- id: context-dataset
  kind: context
  text: Sloth is fitted on an extension of Ruan et al. (2024)'s benchmark dataset covering
    30 LLM families, or 53 if base and instruct models are counted separately. Of these, 28
    appear on Open LLM Leaderboard v1, 17 on v2, and 15 on both.
  scope: Public leaderboard scores plus HumanEval, EQ-Bench and AgentBench data for subsets
    of the models; the authors describe the dataset as the most comprehensive among prior
    benchmark scaling-law work as of publication.
  evidence: Section 4.1
qa:
- q:
  - How can I predict how a bigger model in my LLM family will score on benchmarks without
    training it?
  - Can benchmark performance of an untrained larger LLM be forecast from leaderboard data?
  - What method predicts a 70B model's benchmark scores from smaller models in the same family?
  answers:
  - prediction-competitive
  - one-model-per-family
- q:
  - How many models per family do I need before a scaling law can extrapolate to a larger
    one?
  - Does fitting Sloth require training several model sizes in the new family?
  - What is the minimum data on a new LLM family needed to fit a skills scaling law?
  answers:
  - one-model-per-family
  - context-position
- q:
  - What latent skills explain LLM benchmark scores?
  - Which benchmarks measure reasoning versus knowledge versus instruction following?
  - How many dimensions are needed to summarize Open LLM Leaderboard results?
  answers:
  - three-skills
- q:
  - Does model size or training data matter more for reasoning ability?
  - How do parameters and tokens differently affect knowledge versus reasoning skills?
  - Is reasoning driven by parameter count or by number of training tokens?
  answers:
  - reasoning-size-driven
- q:
  - What does instruction tuning do to a model's reasoning ability?
  - Does instruction tuning help or hurt latent skills of LLMs?
  - How large is the effect of instruction tuning compared with scaling up compute?
  answers:
  - instruction-tuning-effects
  - instruction-tuning-dominates-compute
- q:
  - Can leaderboard scores be used to predict coding ability on HumanEval?
  - How do you forecast a hypothetical LLM's performance on a downstream task like code completion
    or emotional intelligence?
  - Which latent skill predicts code-completion performance?
  answers:
  - downstream-humaneval
- q:
  - Can pass@k behavior under repeated sampling be predicted before a model is trained?
  - How is test-time compute scaling on MATH forecast for a hypothetical LLM?
  - Does combining a scaling law with item response theory predict inference-time scaling?
  answers:
  - test-time-scaling
- q:
  - Given a FLOPs budget, how should I split it between parameters and tokens to maximize
    reasoning?
  - Does compute-optimal allocation depend on which capability you care about?
  - Is Chinchilla-style optimal allocation the same for knowledge and for reasoning skills?
  answers:
  - compute-optimal-skills
- q:
  - How many parameters does a skills-based scaling law need compared with per-benchmark scaling
    laws?
  - Is Sloth more parameter-efficient than fitting one curve per benchmark?
  answers:
  - parameter-efficiency
- q:
  - Are the latent skills recovered by a factor-analysis-style scaling law uniquely identified?
  - Is it valid to rotate the loadings before naming the latent skills of LLMs?
  - What theoretical guarantee does Sloth have about its parameters?
  answers:
  - identifiability
- q:
  - What should I read about scaling laws that predict benchmark performance rather than loss?
  - Which paper addresses why a single scaling law fails across LLM families?
  - Where should I start reading on observational scaling laws for LLM benchmarks?
  answers:
  - context-position
  - context-dataset
- q:
  - How accurate are skills-based scaling law predictions in percentage terms?
  - Do the prediction gains hold under MAPE as well as MAE?
  answers:
  - mape-same-conclusion
  - prediction-competitive
- q:
  - What leaderboard data are skills scaling laws for LLMs fitted on, and how many model families
    does it cover?
  - Which leaderboards and how many model families are in the Sloth dataset?
  - How many LLM families are available for fitting benchmark scaling laws from public leaderboards?
  answers:
  - context-dataset
terminology:
  Skills Scaling Laws (SSLaws): A scaling law in which benchmark scores are a linear combination
    of a few latent LLM skills, and each skill is produced from log parameter count, log training
    tokens and their interaction with a family-specific intercept.
  Efficiency intercept: The family-specific additive term in a latent skill's production function,
    interpreted as how efficiently that model family converts compute into skill, absorbing
    hidden factors such as data quality and post-training.
  Latent skill (in LLM benchmark scaling): An unobserved low-dimensional ability, such as
    reasoning, knowledge or instruction following, inferred from the correlation structure
    of benchmark scores via factor loadings.
  Translog production function: A functional form borrowed from stochastic frontier analysis
    in economics that regresses an output on log inputs plus their product, used to make a
    skill depend on log size, log tokens and their interaction rather than on total FLOPs
    alone.
  Compute-optimal scaling of skills: The parameter-and-token allocation maximizing one latent
    skill under a fixed FLOPs budget, as opposed to the classical version that minimizes validation
    loss.
misreadings:
- 'Sloth does not eliminate the need for any data from the target LLM family: its main stated
  limitation is that it usually requires benchmark scores for at least 1 model of that family.'
- The three skill names — Reasoning, Knowledge, Instruction Following — are the authors' subjective
  labels for rotated factor loadings, not validated psychometric constructs, and the Instruction
  Following interpretation does not survive at d=4 latent dimensions.
- Sloth's identifiability theorem covers only the 'basic' version with a fixed sigmoid link
  and fixed lower asymptotes; the best-predicting version with a trainable monotonic neural-network
  link has no such guarantee.
- The compute-optimal tables report allocations restricted to the parameter and token ranges
  observed in the training data, so they are not extrapolations to budgets far beyond existing
  models.
- 'Sloth is not evaluated in the same setting as observational scaling laws by default: Ruan
  et al. (2024) predict a benchmark for an already-trained model, while Sloth predicts a model
  that has not been trained, and the head-to-head comparison in their setting appears only
  in Appendix L.'
- A single latent-skill scaling law is not claimed to be family-independent in general; only
  for a subset of benchmarks does the shared-intercept version of Sloth match the family-specific
  ones.
links_extra:
  code: https://github.com/felipemaiapolo/sloth
  arxiv: https://arxiv.org/abs/2412.06540
  quickstart_notebook: https://github.com/felipemaiapolo/sloth/blob/main/notebooks/interpretability_plots.ipynb
---
