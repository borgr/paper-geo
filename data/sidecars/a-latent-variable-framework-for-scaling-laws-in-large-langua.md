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
    unsorted:
    - Do different LLM skills scale differently with model size versus training data?
    - Is math ability more data-hungry than common-sense reasoning?
    - Which benchmarks improve with more parameters and which with more tokens?
  answered_by:
  - skills-scale-differently
  - compute-optimal-differs-by-skill
- ask:
    unsorted:
    - How many latent skills are needed to explain LLM benchmark scores?
    - How is the latent dimension chosen in a latent-skill scaling law?
    - Do a handful of factors explain performance across 12 leaderboard benchmarks?
  answered_by:
  - four-skills-suffice
- ask:
    unsorted:
    - Why doesn't instruction-following performance improve much with pretraining scale?
    - Does IFEval scale with parameters and tokens?
    - Which skill scales worst with compute in the Open LLM Leaderboard data?
  answered_by:
  - ifeval-weak-scaling
- ask:
    unsorted:
    - Can a scaling law give prediction intervals rather than point forecasts for an untrained
      model?
    - How accurate are forecasts for held-out large models like Llama-3-70B and Qwen-2-72B?
    - Which benchmarks are hardest to predict from compute?
  answered_by:
  - prediction-intervals-cover
  - context-intervals
- ask:
    unsorted:
    - Are there statistical guarantees for latent-skill scaling law estimators?
    - Is the maximum likelihood estimator of a latent variable scaling law consistent?
    - Where do standard errors on scaling-law coefficients come from?
  answered_by:
  - consistency-and-normality
  - context-guarantees-gap
- ask:
    practitioner: What should I read about scaling laws for downstream benchmarks rather than
      validation loss?
    unsorted:
    - Which work models heterogeneity across LLM families in a scaling law?
    - Where should I start reading about latent skills and LLM evaluation?
    - What is a good paper on statistical modelling of LLM benchmark performance?
  answered_by:
  - context-framework
  - context-guarantees-gap
- ask:
    practitioner: How can I compare two model families on a specific skill?
    unsorted:
    - Does instruction tuning hurt mathematical reasoning?
    - What does a chat variant change relative to its base family?
  answered_by:
  - chat-family-comparison
- ask:
    unsorted:
    - Are LLM latent skills independent of each other?
    - How correlated are family-level abilities across benchmarks?
    - Do factor-analytic LLM skills have to be orthogonal?
  answered_by:
  - correlated-skills
- ask:
    unsorted:
    - How should a fixed FLOPs budget be split between parameters and tokens for math versus
      reasoning?
    - Is Chinchilla-style allocation the same for every capability?
    - What is compute-optimal for a specific skill?
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
