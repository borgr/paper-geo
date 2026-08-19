<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced via a forced tool call) + 1 repair round. Every claim, number
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

Then promote it:  python scripts/draft_sidecars.py --accept sloth-scaling-laws-for-llm-skills-to-predict-multi-benchmark

Stamp: spec=d57862840a90 checks=5 body=1580d56a3647
-->
---
key: polo2024sloth
coined: Sloth
gloss: skills scaling laws — predicting a big model's benchmark scores from one small model
  in its family
one_liner: Sloth fits a scaling law on public leaderboard data by assuming benchmark scores
  are driven by 3 low-dimensional latent skills that families produce from parameters and
  tokens with family-specific efficiency, so predicting a large model needs only one small
  model from its family.
claims:
- id: prediction-accuracy
  kind: result
  text: Sloth predicts held-out LLM benchmark performance with mean absolute error similar
    to or lower than a FLOPs-based scaling law with shared intercept, a family-specific-intercept
    FLOPs law, and a PCA+FLOPs adaptation of observational scaling laws. Its errors are also
    similar to or lower than Sloth's own full-dimensional "Size and Tokens" variant.
  scope: 12 Open LLM Leaderboard v1/v2 benchmarks, leave-one-family-out cross-validation over
    30 model families, with only the smallest model of the test family in the training set;
    errors in percentage points, averaged across families.
  evidence: Figure 1
- id: mape-version
  kind: result
  text: Sloth produces the best benchmark-score predictions on both Open LLM Leaderboard v1
    and v2 when error is measured as mean absolute percentage error rather than mean absolute
    error.
  scope: Same leave-one-family-out setup over 30 families as the MAE results, with 1 model
    per test family observed at training time; 12 benchmarks; conclusions match the MAE version.
  evidence: Figure 10
- id: two-model-setting
  kind: result
  text: Sloth's prediction advantage persists when 2 models per test family are available
    at training time. That is the regime in which the fully family-dependent FLOPs law, with
    both family-specific intercept and slope, can also be fitted.
  scope: 12 Open LLM Leaderboard v1/v2 benchmarks, leave-one-family-out over 30 families;
    results reported as averages across families and per family.
  evidence: Figure 16
- id: three-skills
  kind: result
  text: 3 latent skills, labelled Reasoning, Knowledge and Instruction Following, account
    for performance across the 12 Open LLM Leaderboard benchmarks. GSM8K, MATH, GPQA, MMLU(-PRO),
    BBH and MuSR load on Reasoning, ARC, HellaSwag and Winogrande on Knowledge, and IFEval
    on Instruction Following.
  scope: d=3 fit on the 15 families in the intersection of Open LLM Leaderboard v1 and v2,
    using the "basic" Sloth with sigmoid link and fixed lower asymptotes; skill names are
    the authors' subjective reading of the rotated loadings.
  evidence: Figure 2
- id: reasoning-vs-knowledge-inputs
  kind: result
  text: Reasoning is primarily a function of parameter count, with only small dependence on
    the number of training tokens. Knowledge is strongly influenced by both parameter count
    and training tokens, and spans the widest range of skill levels across compute.
  scope: Level curves of the d=3 fit on the leaderboard v1/v2 intersection with family-specific
    intercepts subtracted; skills standardized to zero mean and unit standard deviation; robust
    across d=2, 3 and 4.
  evidence: Figure 4
- id: instruction-tuning-effects
  kind: result
  text: Instruction tuning has a large positive effect on the Instruction Following skill
    for every family examined, a moderate negative effect on Reasoning, and mixed effects
    on Knowledge.
  scope: Base versus instruction-tuned pairs from the families with the most models, d=3 fit
    on the leaderboard v1/v2 intersection; the effect is invisible at d=2.
  evidence: Figure 5
- id: downstream-humaneval
  kind: result
  text: 'Sloth recovers the code-completion score of a model excluded from its training set:
    LLaMa 3 70B base and instruct HumanEval performance is predicted from Sloth-estimated
    skills. Both 70B models are held out of the scaling-law fit.'
  scope: Two-stage pipeline — Sloth fitted on 12 leaderboard benchmarks without the 70B models,
    then a logistic-link regression from skills to HumanEval; a demonstration on 2 held-out
    models, not an error rate over many.
  evidence: Figure 6
- id: reasoning-drives-coding
  kind: result
  text: Reasoning is by far the most important of the 3 latent skills for predicting HumanEval
    code-completion performance, whereas emotional intelligence on EQ-Bench needs a mixture
    of Reasoning and Knowledge.
  scope: Logistic-link regressions from d=3 Sloth skills to downstream scores; EQ-Bench data
    covers only the 15 chat models listed in Appendix G.
  evidence: Figure 6
- id: test-time-scaling
  kind: result
  text: Sloth combined with per-question logistic item response models predicts MATH pass@k
    curves under repeated sampling for 3 held-out models. The held-out models are the largest
    LLaMa 3 Instruct, Gemma and Pythia models, absent from the scaling-law training set.
  scope: 10 LLMs with repeated-sampling MATH data from Brown et al., of which 7 fit the per-question
    logistic regressions and 3 are held out; MATH only.
  evidence: Figure 7
- id: compute-optimal-skills
  kind: result
  text: 'Compute-optimal allocation differs sharply by skill: at 3.3e21 FLOPs the Reasoning-maximizing
    configuration is 30.98B parameters on 0.18T tokens, while the Knowledge-maximizing configuration
    is 0.37B parameters on 15.0T tokens.'
  scope: Derived under the 6st=c budget with parameter and token ranges clipped to training-support
    quantiles (up to 72B parameters, 15.0T tokens), from the d=3 fit; allocation is family-independent.
  evidence: Table 2
- id: parameter-efficiency
  kind: result
  text: With d=3 latent skills and 12 benchmarks, Sloth uses 69+3f parameters for f model
    families, against 36+12f for the FLOPs baseline and 50+12f for the "Size and Tokens" baseline.
    Sloth is the smaller model for 4 or more families.
  scope: Exact parameter counts for d=3 and J=12; compared against the 2 best-performing baselines,
    which use family-specific intercepts or a trained activation function.
  evidence: Appendix F
- id: identifiability
  kind: result
  text: Sloth's loadings and skill-production coefficients are identifiable up to an invertible
    d-by-d transformation. The transformation becomes an orthogonal rotation when the skill
    covariance is the identity, the same indeterminacy exploratory factor analysis has.
  scope: Proved for the "basic" Sloth with a fixed invertible link and fixed lower asymptotes,
    under standardized skills, full-rank loadings and full-rank design matrix; not proved
    for the trainable-link version.
  evidence: Theorem A.2
- id: context-positioning
  kind: context
  text: Sloth predicts a hypothetical larger model's benchmark scores using family information
    while requiring only 1 already-trained model from that family. That fills the gap between
    family-agnostic scaling laws and observational scaling laws that assume the target model
    already exists.
  scope: Positioning relative to Owen (2024), Ruan et al. (2024) and Gadre et al. (2024) as
    of publication in 2025; concerns benchmark-accuracy prediction from public leaderboard
    data, not pretraining-loss scaling laws.
  evidence: Section 2.2
- id: context-skills-scaling
  kind: context
  text: Sloth turns earlier factor-analytic findings that LLM benchmark scores reflect a few
    latent skills into an explicit scaling law. Each skill is modelled as a function of parameter
    count, training tokens and their interaction.
  scope: Prior latent-skill work cited includes Ilić (2023), Burnell et al. (2023), Kipnis
    et al. (2024) and Maia Polo et al. (2024), which report positive skill-size correlations
    without formal scaling laws. Open-weight LLMs with published parameter and token counts.
  evidence: Section 1.1
qa:
- q:
  - How can I predict how a 70B model will score on benchmarks before training it?
  - Is it possible to forecast a large LLM's leaderboard scores from smaller models in the
    same family?
  - How accurate is Sloth at predicting held-out LLM benchmark performance?
  answers:
  - prediction-accuracy
  - mape-version
- q:
  - How much data from a new model family does a skills scaling law need?
  - Can a scaling law be fitted with only one model per family?
  - What happens if two models per family are available instead of one?
  answers:
  - context-positioning
  - two-model-setting
- q:
  - What latent skills explain scores across LLM benchmarks?
  - How many dimensions are needed to explain Open LLM Leaderboard results?
  - Which benchmarks measure reasoning versus knowledge?
  answers:
  - three-skills
- q:
  - Does model size or training data matter more for reasoning ability?
  - Should I add parameters or tokens if I care about knowledge benchmarks?
  - How do parameter count and token count differently affect LLM skills?
  answers:
  - reasoning-vs-knowledge-inputs
- q:
  - What does instruction tuning do to a model's reasoning ability?
  - Does instruction tuning trade off reasoning for instruction following?
  - How do base and instruction-tuned models differ in latent skills?
  answers:
  - instruction-tuning-effects
- q:
  - Can leaderboard scores predict coding ability on HumanEval?
  - How do I forecast downstream task performance like code completion for an untrained model
    size?
  - Which latent skill predicts code-completion performance?
  answers:
  - downstream-humaneval
  - reasoning-drives-coding
- q:
  - Can scaling laws predict pass@k gains from repeated sampling?
  - How do I forecast test-time compute scaling for a model that does not exist yet?
  - Does Sloth predict MATH performance under repeated sampling?
  answers:
  - test-time-scaling
- q:
  - Given a FLOPs budget, how should parameters and tokens be split to maximize reasoning?
  - Is compute-optimal allocation the same for every skill?
  - What is the Chinchilla-style optimal allocation for knowledge versus reasoning skills?
  answers:
  - compute-optimal-skills
- q:
  - Are the latent skills recovered by a skills scaling law uniquely determined?
  - Is there an identifiability guarantee for Sloth's loadings and coefficients?
  - Can factor rotation change the interpretation of estimated LLM skills?
  answers:
  - identifiability
- q:
  - Does assuming a low-dimensional skill structure cost prediction accuracy or save parameters?
  - How many parameters does a skills scaling law use compared to per-benchmark scaling laws?
  answers:
  - parameter-efficiency
  - prediction-accuracy
- q:
  - What should I read about scaling laws that predict benchmark accuracy rather than loss?
  - Which work established scaling laws across LLM families using public leaderboard data?
  - Where do I start reading about latent skills of language models and scaling?
  answers:
  - context-positioning
  - context-skills-scaling
misreadings:
- 'Sloth does not eliminate the need for data from the target model family: the reported results
  assume at least one already-evaluated model from that family, and predictions for a family
  with no observed models are not demonstrated.'
- The named skills Reasoning, Knowledge and Instruction Following are subjective labels assigned
  to rotated factor loadings, not validated psychometric constructs, and the Instruction Following
  interpretation does not hold at 4 latent dimensions.
- The identifiability theorem covers only the basic Sloth with a fixed sigmoid link and fixed
  lower asymptotes; the best-predicting version with a trainable monotone neural-network link
  has no such guarantee.
- The compute-optimal allocations are clipped to the parameter and token ranges observed in
  the training data, up to 72B parameters and 15.0T tokens, so the tables should not be read
  as extrapolated optima beyond that support.
- Sloth is not evaluated as a replacement for pretraining-loss scaling laws such as Chinchilla;
  it models benchmark and downstream scores of already-released models rather than training
  runs the authors control.
terminology:
  Latent skills: Low-dimensional unobserved abilities of a language model, such as reasoning
    or instruction following, whose linear combination determines the model's scores across
    many benchmarks.
  Family efficiency intercept: A model-family-specific additive term in the skill equation,
    interpreted as how efficiently that family converts compute into a given skill, absorbing
    hidden factors like data quality and post-training.
  Translog skill production function: The functional form taken from stochastic frontier analysis
    in economics, in which a skill is linear in log parameter count, log training tokens and
    their product.
  Size and Tokens variant: An ablation of Sloth in which the loading matrix is the identity,
    so every benchmark gets its own scaling equation in log parameters and log tokens with
    no shared latent-skill structure.
  Trainable link function: A monotone increasing neural network with non-negative weights
    and a sigmoid output, fitted per benchmark in place of a fixed logistic curve mapping
    skills to scores.
links_extra:
  code: https://github.com/felipemaiapolo/sloth
  arxiv_html: https://arxiv.org/html/2412.06540
---
