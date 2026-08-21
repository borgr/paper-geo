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
- ask:
    plain: can you estimate how a bigger model in a model family will score on benchmarks
      before it is trained?
    jargon: how accurately do observational scaling laws extrapolate held-out LLM benchmark
      scores to larger models in the same family?
    task: how do I forecast benchmark scores for a 70B model using public leaderboard results
      from smaller releases?
    practitioner: before I commit compute to a larger model in my family, can I predict its
      leaderboard scores from the ones I already have?
  answered_by:
  - prediction-competitive
  - one-model-per-family
- ask:
    plain: how many existing models from a new model family do you need before you can predict
      scores for a bigger one?
    jargon: what is the minimum number of models per family required to identify family-specific
      parameters in a latent-skill scaling law?
    task: how do I fit a scaling law for a family where only one released checkpoint exists?
    practitioner: I have released just one model size so far; can I still fit a scaling law
      for my family?
  answered_by:
  - one-model-per-family
  - context-position
- ask:
    plain: are LLM benchmark scores really measuring a few underlying abilities rather than
      12 separate things?
    jargon: how many latent skill dimensions explain the covariance of Open LLM Leaderboard
      benchmark scores, and how do benchmarks load on them?
    task: how do I group leaderboard benchmarks into a small number of ability axes for reporting?
    practitioner: which leaderboard benchmarks should I run if I want separate reads on reasoning,
      knowledge and instruction following?
  answered_by:
  - three-skills
- ask:
    plain: for better reasoning, does it help more to make a model bigger or to train it on
      more text?
    jargon: how do parameter count and training tokens differ in their contribution to latent
      reasoning versus knowledge skill?
    task: how do I decide between adding parameters and adding training tokens when reasoning
      is the ability I care about?
    practitioner: my target is reasoning, not trivia recall; should I spend my budget on size
      or on more tokens?
  answered_by:
  - reasoning-size-driven
- ask:
    plain: what does instruction tuning actually change about a model's abilities, and does
      anything get worse?
    jargon: what are the measured effects of instruction tuning on latent reasoning, knowledge
      and instruction-following skills relative to scaling parameters and tokens?
    task: how do I tell whether instruction tuning or a bigger pretrained model will improve
      instruction following more?
    practitioner: should I instruction-tune my model or scale it up if I want better instruction
      following?
  answered_by:
  - instruction-tuning-effects
  - instruction-tuning-dominates-compute
- ask:
    plain: can scores on public benchmarks tell you how good a model will be at writing code?
    jargon: can latent skills estimated from leaderboard benchmarks predict held-out HumanEval
      pass rates, and which skill dominates?
    task: how do I predict a not-yet-trained model's code-completion accuracy without running
      a coding benchmark on it?
    practitioner: I care about coding ability; can I get an estimate for a model size I have
      not trained yet?
  answered_by:
  - downstream-humaneval
- ask:
    plain: can you predict how much a model improves when you let it try a problem many times,
      before the model exists?
    jargon: can pass@k curves under repeated sampling on MATH be forecast for held-out models
      by combining a scaling law with per-question item response models?
    task: how do I forecast the payoff of repeated sampling at inference for a model I have
      not trained?
    practitioner: is it worth planning an inference-time sampling budget for a model size
      I have yet to train?
  answered_by:
  - test-time-scaling
- ask:
    plain: does the best trade-off between model size and training data change depending on
      which ability you want?
    jargon: is compute-optimal allocation of parameters and tokens skill-dependent at a fixed
      FLOP budget?
    task: how do I pick parameters and tokens for a fixed compute budget when my goal is one
      specific capability?
    practitioner: my compute budget is fixed and I mainly need knowledge recall; should I
      copy Chinchilla-style allocation or something else?
  answered_by:
  - compute-optimal-skills
- ask:
    plain: is it cheaper to fit one shared model of abilities than a separate curve for every
      benchmark?
    jargon: how does the parameter count of a latent-skill scaling law compare with per-benchmark
      FLOPs and size-and-tokens scaling laws as families grow?
    task: how do I keep the number of fitted parameters down when modelling 12 benchmarks
      across many model families?
    practitioner: with dozens of model families to cover, is a shared-skill scaling law worth
      it over one fit per benchmark?
  answered_by:
  - parameter-efficiency
- ask:
    plain: if a model of hidden abilities gives you labels like reasoning and knowledge, can
      those labels be trusted?
    jargon: are the loadings and skill-production coefficients of a factor-analytic scaling
      law identifiable, and does that justify factor rotation?
    task: how do I know whether I can rotate the loadings before naming latent skills of LLMs?
    practitioner: should I trust the skill names attached to a latent-skill scaling law, or
      are they arbitrary?
  answered_by:
  - identifiability
- ask:
    plain: why does one scaling curve not fit all language models, and what should I read
      about it?
    jargon: which work formalises the gap between pooled observational scaling laws and family-specific
      ones for LLM benchmarks?
    task: where do I start reading about predicting LLM benchmark scores from public leaderboard
      data?
    practitioner: I need a reference on scaling laws that account for differences between
      model families; which one should I read first?
  answered_by:
  - context-position
  - context-dataset
- ask:
    plain: how far off are predicted benchmark scores in percentage terms, not just absolute
      points?
    jargon: do the prediction advantages of a latent-skill scaling law hold under MAPE as
      well as MAE on both Open LLM Leaderboards?
    task: how do I check whether a scaling law's accuracy ranking survives a change of error
      metric?
    practitioner: is the reported prediction accuracy robust to the error metric, or only
      good on the one they chose?
  answered_by:
  - mape-same-conclusion
  - prediction-competitive
- ask:
    plain: how many model families are there in public leaderboard data you could fit a scaling
      law on?
    jargon: what is the coverage of the Open LLM Leaderboard v1 and v2 dataset used to fit
      latent-skill scaling laws, in families and benchmarks?
    task: where do I get benchmark data across enough model families to fit a scaling law?
    practitioner: is there enough public leaderboard data to fit a skills scaling law without
      running my own evaluations?
  answered_by:
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
