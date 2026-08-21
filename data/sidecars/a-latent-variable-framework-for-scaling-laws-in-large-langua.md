---
key: cai2025latent
one_liner: A latent variable scaling law in which each LLM family gets a random ability vector
  and each benchmark a loading vector, so benchmark performance is modelled as a small set
  of interpretable skills that scale with model size and training tokens, with consistency,
  asymptotic normality and prediction intervals.
claims:
- id: four-skills-suffice
  text: 4 latent skills suffice to describe LLM performance across 12 Open LLM Leaderboard
    benchmarks and hundreds of models. AIC over latent dimensions K from 1 to 12 drops sharply
    from K=1 to K=3 and flattens after K=4.
  kind: result
  evidence: Section 4.2, with the AIC curve in Figure S1 of Appendix D.2
  scope: 168 LLMs from 75 families on Open LLM Leaderboard v1 and 216 LLMs from 146 families
    on v2, combined; anchor benchmarks MATH, IFEval, HellaSwag and BBH chosen by domain knowledge;
    K=6 results also reported.
- id: skills-scale-differently
  text: Mathematical skill (anchored on MATH) loads more on training tokens than on parameters,
    with coefficients 0.774 (SE 0.101) for log tokens versus 0.432 (SE 0.065) for log parameters.
    Common-sense reasoning (HellaSwag) reverses this, at 0.840 (SE 0.055) for log parameters
    versus 0.384 (SE 0.085) for log tokens.
  kind: result
  evidence: Table 1
  scope: K=4 fit with covariates log(size), log(tokens) and their interaction, on combined
    Open LLM Leaderboard v1/v2 data; the interaction term is not consistently significant.
- id: ifeval-weak-scaling
  text: Instruction following, anchored on IFEval, scales only weakly with both pretraining
    inputs, at 0.190 (SE 0.054) for log parameters and 0.324 (SE 0.087) for log tokens. Those
    are the smallest scaling coefficients among the 4 skills.
  kind: result
  evidence: Table 1
  scope: K=4 fit on Open LLM Leaderboard v1/v2 benchmark averages; covariates are only model
    size, token count and their interaction, so post-training compute is not represented among
    the covariates.
- id: compute-optimal-differs-by-skill
  text: 'Compute-optimal allocation under a fixed FLOPs budget differs by skill: at 100.37E19
    FLOPs the MATH-optimal configuration is 0.07B parameters with 2.39T tokens. The HellaSwag-
    and BBH-optimal configuration at the same budget is 1.12B parameters with 0.15T tokens.'
  kind: result
  evidence: Table 2
  scope: Allocations are constrained to the range of sizes and token counts observed in the
    training data (up to 180B parameters and 15T tokens), so budgets at the extremes saturate
    at those bounds; derived from the fitted K=4 model.
- id: prediction-intervals-cover
  text: 95% prediction intervals from the latent variable scaling model contain nearly all
    observed benchmark scores for 6 held-out LLMs, including Qwen-2-72B, Yi-1.5-34B and Meta-Llama-3-70B-instruct.
    GPQA and MuSR give visibly wider intervals than the other benchmarks.
  kind: result
  evidence: Figure 4
  scope: Each test model has smaller variants of the same family present in the training data,
    which is what allows the family latent ability to be inferred; K=4 fit on combined Open
    LLM Leaderboard v1/v2 data.
- id: consistency-and-normality
  text: The marginal maximum likelihood estimator of the latent variable scaling law is consistent,
    and its free parameters are asymptotically normal at rate sqrt(N) in the number N of LLM
    families. That asymptotic distribution supplies the standard errors on the size and token
    coefficients.
  kind: result
  evidence: Theorems 1 and 2 in Section 2.3, with assumptions in Appendix A.1
  scope: Number of families N diverges while models per family and number of benchmarks J
    stay fixed; requires anchor-benchmark and unit-diagonal identifiability constraints, known
    guessing parameters, and standard M-estimation regularity conditions.
- id: chat-family-comparison
  text: Posterior joint densities of family latent abilities show Yi-1.5-chat above base Yi-1.5
    on the instruction-following dimension, with differences on the mathematical and logical-reasoning
    dimensions small.
  kind: result
  evidence: Figure 3
  scope: Comparison of 2 families (Yi-1.5 and Yi-1.5-chat) treated as separate families in
    the fit; posterior samples drawn by Metropolis-Hastings with the estimated parameters
    plugged in for the true ones.
- id: correlated-skills
  text: Family-level latent abilities in the scaling model are correlated rather than orthogonal,
    with the BBH-anchored ability correlating above 0.5 with both the MATH- and HellaSwag-anchored
    abilities.
  kind: result
  evidence: Figure 2
  scope: Estimated correlation matrix of the K=4 family random effects on combined Open LLM
    Leaderboard v1/v2 data; the unit-diagonal constraint on the covariance is imposed for
    identifiability.
- id: context-framework
  text: A latent variable framework for LLM scaling laws models each family with a random
    ability vector and each benchmark with loadings. It replaces a single global power-law
    curve with family-specific, skill-specific scaling on downstream benchmarks.
  kind: context
  scope: Benchmark-level average scores rather than validation loss or item-level responses;
    demonstrated on 12 Open LLM Leaderboard v1/v2 benchmarks as of the 2025 preprint.
- id: context-guarantees-gap
  text: The latent variable scaling law of Cai et al. supplies identifiability constraints,
    estimation consistency and asymptotic normality for latent-skill scaling laws. Earlier
    latent-skill scaling formulations such as Ruan et al. (2024) and Maia Polo et al. (2024)
    did not establish these properties.
  kind: context
  scope: The guarantees are asymptotic in the number of LLM families and rest on anchor benchmarks
    whose loadings are assumed single-dimensional; as characterised in Sections 1 and 1.1
    of the 2025 preprint.
- id: context-intervals
  text: Prediction intervals for unevaluated LLMs are obtained by combining the estimator's
    asymptotic distribution with posterior draws of the family latent ability. Prior benchmark
    scaling-law work reported point predictions without such uncertainty quantification.
  kind: context
  scope: Intervals are valid under the fitted beta-likelihood scaling model and require observed
    data from other models in the same family; as of the 2025 preprint.
qa:
- ask:
    plain: does making a language model bigger help the same skills that feeding it more text
      helps?
    jargon: do benchmark-specific scaling coefficients on log parameters and log tokens differ
      across skill dimensions such as mathematics and common-sense reasoning?
    task: how do I work out whether adding parameters or adding training tokens will improve
      the particular capability I care about?
    practitioner: my model needs better math more than better common-sense answers, so should
      I spend my next run on more data or a bigger network?
  answered_by:
  - skills-scale-differently
  - compute-optimal-differs-by-skill
- ask:
    plain: how many underlying abilities are enough to explain how language models score across
      a dozen benchmarks?
    jargon: how is the latent dimension K selected in a factor model of LLM benchmark scores,
      and where does the AIC curve flatten?
    task: how do I decide how many latent factors to fit when summarising leaderboard scores
      for hundreds of models?
    practitioner: can I get away with tracking a few skill axes instead of all 12 leaderboard
      benchmarks?
  answered_by:
  - four-skills-suffice
- ask:
    plain: why does a model's ability to follow instructions barely improve when it is pretrained
      on more data or made bigger?
    jargon: what are the log-parameter and log-token scaling coefficients for the IFEval-anchored
      latent skill relative to the other dimensions?
    task: how do I improve instruction following if scaling pretraining size and tokens does
      not move it much?
    practitioner: should I expect a bigger pretraining run to fix my model's instruction-following
      scores?
  answered_by:
  - ifeval-weak-scaling
- ask:
    plain: can a scaling model say how uncertain its forecast of an untested model's benchmark
      score is, instead of giving a single number?
    jargon: do 95% prediction intervals from a latent variable scaling law cover held-out
      LLM benchmark scores, and which benchmarks show the widest intervals?
    task: how do I put error bars on a predicted benchmark score for a model that has not
      been evaluated yet?
    practitioner: can I trust a predicted leaderboard score for a 70B-scale model I have not
      run, and how wide is the range?
  answered_by:
  - prediction-intervals-cover
  - context-intervals
- ask:
    plain: is there any mathematical proof that fitting a skill-based scaling model recovers
      the right numbers as more model families are added?
    jargon: is the marginal maximum likelihood estimator of a latent variable scaling law
      consistent and asymptotically normal in the number of LLM families?
    task: how do I get standard errors for the size and token coefficients in a latent-skill
      scaling law fit?
    practitioner: should I report confidence intervals from a latent-skill scaling fit, or
      are the estimates only descriptive?
  answered_by:
  - consistency-and-normality
  - context-guarantees-gap
- ask:
    plain: what should I read first about using statistics to model how language model benchmark
      scores grow with scale?
    jargon: which work formulates a latent variable scaling law with family-level random abilities
      and benchmark loadings, with identifiability constraints established?
    task: where do I start if I want to model differences between LLM families rather than
      fit one global scaling curve?
    practitioner: is there a paper I can cite for family-specific, skill-specific scaling
      laws on downstream benchmarks?
  answered_by:
  - context-framework
  - context-guarantees-gap
- ask:
    plain: does turning a base language model into a chat model trade away its maths ability?
    jargon: how do posterior family latent ability densities differ between a chat-tuned variant
      and its base family across instruction-following and reasoning dimensions?
    task: how do I tell which skill dimensions instruction tuning actually moved in a model
      family?
    practitioner: if I switch from a base checkpoint to its chat version, what will I gain
      and what might I lose?
  answered_by:
  - chat-family-comparison
- ask:
    plain: are the different abilities of language models separate from each other, or do
      they rise and fall together?
    jargon: are family-level latent abilities in a factor-analytic scaling model orthogonal,
      or correlated across benchmark-anchored dimensions?
    task: how do I interpret skill dimensions if they are not independent of one another?
    practitioner: can I treat reasoning, maths and common-sense scores as separate axes when
      comparing model families?
  answered_by:
  - correlated-skills
- ask:
    plain: if I have a fixed compute budget, is the best split between model size and training
      data the same for every ability?
    jargon: does the compute-optimal parameter-token allocation under a fixed FLOPs budget
      vary by skill dimension rather than following one Chinchilla frontier?
    task: how do I allocate a fixed FLOPs budget between parameters and tokens when I care
      mainly about mathematical performance?
    practitioner: should I follow the standard compute-optimal ratio, or change it because
      my target capability is maths?
  answered_by:
  - compute-optimal-differs-by-skill
terminology:
  scaling model: The statistical latent variable model for how LLM benchmark performance depends
    on model size, training tokens and family membership, named to distinguish it from the
    large language models being evaluated.
  family-wise common latent ability: A K-dimensional random vector attached to an LLM family,
    capturing the architecture and training-pipeline advantage shared by all models in that
    family, analogous to efficiency in stochastic frontier analysis.
  anchor benchmark: A benchmark assumed to load on exactly one latent skill dimension, imposed
    to make the latent skills identifiable and interpretable; MATH, IFEval, HellaSwag and
    BBH are used as anchors for the 4-dimensional fit.
  guessing parameter: A fixed, known lower bound on a benchmark's expected score reflecting
    random-chance success, set to 0.25 for 4-option multiple-choice benchmarks such as MMLU
    and 0 for open-ended ones.
misreadings:
- 'The 4 latent skills are not claimed to be the true cognitive dimensions of language models:
  the dimension 4 is chosen by AIC over K from 1 to 12, and the labels come from the anchor
  benchmarks MATH, IFEval, HellaSwag and BBH selected for interpretability.'
- Consistency and asymptotic normality hold as the number of LLM families grows, not as the
  number of models inside a family or the number of benchmarks grows, so results from a handful
  of families carry no such guarantee.
- The compute-optimal allocations are constrained to sizes and token counts seen in the training
  data, so entries pinned at 180B parameters or 15T tokens are boundary solutions rather than
  extrapolated optima.
- Fine-tuned models are treated as families distinct from their base models, so a comparison
  of Yi-1.5 with Yi-1.5-chat is a comparison between two families rather than a within-family
  scaling effect.
- The framework models benchmark-level average scores, not item-level responses; item-level
  modelling is named as future work rather than something demonstrated.
links_extra:
  code: https://github.com/felipemaiapolo/statistical-scaling-law
---
