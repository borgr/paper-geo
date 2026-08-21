---
key: donyehiya2026mediocrity
one_liner: 'Across 866,250 pairwise LLM-as-a-judge comparisons on Arena-Hard-v2.0, anchor
  quality follows an inverted U-shape in model strength: mid-ranked ("mediocre") anchors give
  rankings closest to the all-pairs and human gold, while the strongest and weakest models
  — the usual choices — are the worst anchors.'
terminology:
  Anchor-based evaluation: An LLM-as-a-judge protocol in which every evaluated model is compared
    only against one fixed reference model (the anchor), reducing the number of judgments
    from quadratic to linear in the number of models.
  Anchor informativeness: The fraction of (sample, model pair) cases in which two models receive
    different verdicts against the same anchor, so the sample can discriminate between them;
    comparisons where both models tie or both win identically carry no ranking signal.
  Quadratic ranking: The ranking obtained by judging all possible pairs of evaluated models
    on every benchmark instruction and aggregating with Bradley-Terry, used as the gold standard
    that anchor-based ranking approximates.
claims:
- id: inverted-u
  kind: result
  text: Anchor quality in LLM-as-a-judge pairwise evaluation follows an inverted U-shape in
    the anchor's own strength. Top-ranked and bottom-ranked models yield the lowest Kendall's
    tau with the all-pairs gold ranking, and mid-ranked models the highest.
  scope: Arena-Hard-v2.0, 750 instructions, 22 models each used as anchor and competitor;
    Deepseek-V3 judge, replicated for GPT-OSS 120B, GPT-OSS 20B, Qwen3 235B A22B, Qwen3 8B,
    and on AlpacaEval with 11 models.
  evidence: Figure 1; Figures 12-16; Figure 17
- id: worst-anchor-drop
  kind: result
  text: Choosing a bad anchor instead of the best one costs up to .30 Kendall's tau in correlation
    with the human ranking on Arena-Hard-v2.0. The gap against the all-pairs quadratic ranking
    reaches .19.
  scope: 22 anchors, 5 judges, 750 Arena-Hard-v2.0 instructions; the .30 human gap is the
    GPT-OSS 20B judge, and per-judge human gaps span .181-.305.
  evidence: Table 3
- id: o3-worst
  kind: result
  text: o3, the top-performing model in the pool, is the worst anchor for every one of the
    5 judges tested. Under the Deepseek-V3 judge it reaches only .818 Kendall's tau with the
    quadratic ranking and .324 with the human ranking.
  scope: Arena-Hard-v2.0 with 22 evaluated models; "top-performing" is relative to this pool,
    and o3's failure as an anchor follows from its position at the top rather than from the
    model itself.
  evidence: Table 1; Tables 4-7
- id: anchor-vs-judge
  kind: result
  text: Anchor selection matters as much as judge selection in LLM-as-a-judge evaluation.
    The best-to-worst anchor gap in correlation with human ranking is .181-.305 depending
    on the judge, comparable to or larger than the spread across the 5 judges.
  scope: 5 judges (Deepseek-V3, GPT-OSS 120B, GPT-OSS 20B, Qwen3 235B A22B, Qwen3 8B) on Arena-Hard-v2.0
    with 22 models; anchor effects are similar at every judge quality level.
  evidence: Table 3
- id: wasted-budget
  kind: result
  text: 'A strong anchor throws away most of the evaluation budget: o3 beats every opposing
    model on roughly 500 of the 750 Arena-Hard-v2.0 samples. Only 45% of o3''s comparisons
    are informative, against 61% for the most informative anchor, o3 Mini.'
  scope: Deepseek-V3 as judge on Arena-Hard-v2.0 with 22 models; informativeness is the fraction
    of model pairs receiving different verdicts against the anchor, and the empirical range
    across the 22 anchors is 45.5% to 61.1%.
  evidence: Figure 2; Table 9
- id: informativeness-correlates
  kind: result
  text: Anchor informativeness predicts ranking accuracy, with R^2 = 0.5940 between an anchor's
    informativeness rate and the Kendall's tau of its induced ranking with the quadratic ranking.
  scope: 22 anchors on Arena-Hard-v2.0, Deepseek-V3 as judge; a single-judge regression over
    22 points, so the relation is directional evidence rather than a calibrated predictor.
  evidence: Figure 3
- id: benchmark-too-small
  kind: result
  text: Standard benchmark sizes are statistically insufficient for anchor-based pairwise
    evaluation. Detecting a +5% win-rate edge at 80% power needs 617 discordant samples, which
    becomes 1,372 total samples at o3's tie rate, far more than Arena-Hard-v2.0's 750.
  scope: One-sided sign test, alpha = 0.05, power = 0.80, with the total inflated by 1/informativeness;
    larger effects stay detectable, as +10% needs 341 total samples at a 55% tie rate.
  evidence: Table 2
- id: informativeness-ceiling
  kind: result
  text: Anchor-based evaluation caps its own informativeness at 0.5 with magnitude-free tie/win/loss
    verdicts, maximised when the anchor sits exactly in the middle of the ranking. Even the
    best empirical anchor leaves 39% of Arena-Hard-v2.0 samples uninformative.
  scope: The 0.5 bound assumes verdicts in {-1,0,1} and that transitivity holds; empirical
    rates above 0.5 arise because the judge's 5-level verdicts carry magnitude. Arena-Hard-v2.0,
    22 models.
  evidence: Section 4.3
- id: anchor-count
  kind: result
  text: Adding more anchors helps less than picking the right one. Averaging over random anchor
    sets raises Kendall's tau with the quadratic ranking, but a single random anchor already
    reaches .92 versus .82 for the strongest model as anchor.
  scope: Iterative Bradley-Terry aggregation over anchor sets growing from 1 to 22 models,
    40 shuffled permutations, Deepseek-V3 judge on Arena-Hard-v2.0; converges to tau = 1.0
    by construction when all 22 models are anchors.
  evidence: Figure 7
- id: cheap-estimation
  kind: result
  text: An anchor's informativeness can be screened with only 10 benchmark samples, correlating
    with full-dataset informativeness at Pearson r above 0.86 for 3 or more evaluated models.
    For 8 or more models the correlation is above 0.91.
  scope: Arena-Hard-v2.0, pool sizes swept over 3-22 models, 30 repetitions, informativeness
    estimated from 10 random samples; rates span 0.42-0.65 versus 0.44-0.61 on the full data.
  evidence: Table 10; Section 5.3
- id: sample-size-sensitivity
  kind: result
  text: Anchor-based rankings are far more sensitive to benchmark size than all-pairs rankings.
    Averaged over anchors, anchor-based correlation with human ranking converges to the quadratic
    correlation only at around 600 samples, while o3 as anchor stays well below at every size.
  scope: Sample sizes swept from 50 to 750 on Arena-Hard-v2.0, 30 repetitions, Deepseek-V3
    judge; the same trend holds for GPT-OSS 120B, GPT-OSS 20B and Qwen3 235B A22B, but with
    the Qwen3 8B judge the mean anchor-based correlation exceeds the quadratic one from about
    150 samples.
  evidence: Figure 4; Figures 8-11
- id: contribution
  kind: context
  text: '"Mediocrity is the key for LLM as a Judge Anchor Selection" is a systematic study
    of anchor choice in LLM-as-a-judge leaderboards. It treats the anchor, rather than the
    judge, as the neglected design decision in Arena-Hard- and AlpacaEval-style evaluation.'
  scope: As of publication in 2026; earlier work on anchor-based evaluation focused on transitivity
    violations and proposed alternative protocols, while this study keeps the anchor protocol.
    English-language open-ended generation benchmarks only.
  evidence: Section 7
- id: recommendations
  kind: context
  text: '"Mediocrity is the key for LLM as a Judge Anchor Selection" offers a decision procedure
    for pairwise evaluation. Avoid an external anchor when a natural baseline exists or when
    3 or fewer models are compared, otherwise pick a mid-performing anchor and report its
    informativeness.'
  scope: Leaderboard settings where a full ranking of 4 or more models is needed; with 3 models
    all-pairs comparison costs the same 3N judgments as an external anchor. "Mediocre" is
    relative to the pool being ranked, so the choice must be recalibrated per model set.
  evidence: Figure 5
- id: released-judgments
  kind: context
  text: '"Mediocrity is the key for LLM as a Judge Anchor Selection" releases about 900K LLM
    judge verdicts, covering all 22-choose-2 model pairs on 750 Arena-Hard-v2.0 instructions
    for 5 judges.'
  scope: Arena-Hard-v2.0 and AlpacaEval instructions, 5 open-weight judges (no commercial
    judge models); verdicts are on a 5-level scale from clear loss to clear win.
  evidence: Section 3.2
qa:
- ask:
    plain: When one model is used as the common opponent for scoring every other model, should
      that opponent be the strongest one or an average one?
    jargon: How does Kendall's tau with the all-pairs gold ranking vary with the strength
      of the baseline model in pairwise LLM-as-a-judge evaluation?
    task: How do I choose which model to use as the fixed reference opponent in an Arena-Hard-style
      leaderboard?
    practitioner: I am setting up a pairwise judge leaderboard for my models — which reference
      model should I score everyone against?
  answered_by:
  - inverted-u
  - recommendations
- ask:
    plain: Does scoring every model against the strongest available model make the resulting
      ranking worse?
    jargon: How much Kendall's tau with human and all-pairs rankings is lost when a frontier
      model such as o3 serves as the pairwise baseline?
    task: How do I avoid ranking errors caused by picking a top-tier model as the fixed opponent
      in pairwise evaluation?
    practitioner: I was planning to benchmark my models against o3 as the reference — how
      much accuracy would that cost me?
  answered_by:
  - o3-worst
  - worst-anchor-drop
- ask:
    plain: 'In head-to-head model comparisons scored by a language model, which choice changes
      the ranking more: the model doing the scoring, or the model everyone is compared against?'
    jargon: Is the best-to-worst baseline spread in correlation with human ranking comparable
      to the spread across judge models in LLM-as-a-judge evaluation?
    task: How do I decide whether to spend effort on selecting the judge or on selecting the
      reference opponent for a pairwise leaderboard?
    practitioner: Should I upgrade the judge model or rethink the baseline model I compare
      everything against?
  answered_by:
  - anchor-vs-judge
- ask:
    plain: When every model is compared against one fixed opponent by an automatic judge,
      how many of those comparisons tell you nothing about the ranking?
    jargon: What is the informativeness rate of a fixed baseline in pairwise LLM-as-a-judge
      evaluation, and what caps it under tie/win/loss verdicts?
    task: How do I stop wasting judge API calls on comparisons whose outcome is decided before
      they run?
    practitioner: How much of my evaluation spend on pairwise judging is actually buying ranking
      signal?
  answered_by:
  - wasted-budget
  - informativeness-ceiling
- ask:
    plain: Is a 750-prompt benchmark big enough to separate two language models whose win
      rates differ only slightly?
    jargon: How many discordant samples are needed to detect a 5% win-rate gap at 80% power,
      and how does that scale with the baseline's tie rate?
    task: How many prompts do I need to run so a pairwise win-rate difference between two
      models is statistically meaningful?
    practitioner: Can I trust a small win-rate lead measured on Arena-Hard-v2.0, or do I need
      more prompts?
  answered_by:
  - benchmark-too-small
  - sample-size-sensitivity
- ask:
    plain: Can you tell in advance, from a handful of prompts, whether a candidate opponent
      model will produce decisive comparisons?
    jargon: How well does informativeness measured on 10 benchmark samples correlate with
      full-dataset informativeness for a candidate baseline?
    task: How do I screen several candidate reference models cheaply before committing the
      full benchmark budget to one?
    practitioner: Can I run a tiny pilot to pick my baseline model instead of judging the
      whole benchmark for each candidate?
  answered_by:
  - cheap-estimation
- ask:
    plain: If several different opponent models are used instead of one, does that remove
      the problem of picking a bad opponent?
    jargon: Does averaging rankings over random baseline sets recover the all-pairs Kendall's
      tau better than a single well-chosen baseline?
    task: How do I get a reliable pairwise ranking — add more reference models, or spend the
      effort choosing one?
    practitioner: Is it worth paying for judgments against multiple reference models rather
      than one mid-ranked one?
  answered_by:
  - anchor-count
- ask:
    plain: What should I read about how reliable leaderboards built from automatic head-to-head
      model comparisons really are?
    jargon: Which study systematically examines baseline selection, rather than judge selection,
      in Arena-Hard- and AlpacaEval-style LLM-as-a-judge leaderboards?
    task: Where do I start reading before designing an automatic pairwise evaluation of my
      models?
  answered_by:
  - contribution
  - inverted-u
- ask:
    plain: Is there a public collection of automatic judge decisions covering many pairs of
      language models on the same prompts?
    jargon: Are there released pairwise LLM judge verdicts spanning all model pairs on Arena-Hard-v2.0
      instructions across multiple judges?
    task: Where can I get existing pairwise judge verdicts so I can test ranking methods without
      paying for inference?
    practitioner: Can I reuse someone else's judge verdicts instead of running all the pairwise
      comparisons myself?
  answered_by:
  - released-judgments
- ask:
    plain: Do opponent models that produce more decisive comparisons actually give more accurate
      model rankings?
    jargon: Is a baseline's informativeness rate predictive of the Kendall's tau between its
      induced ranking and the all-pairs quadratic ranking?
    task: What should I measure about a candidate reference model to predict how accurate
      the ranking it induces will be?
    practitioner: If I pick the reference model with the fewest lopsided comparisons, will
      my leaderboard actually be more accurate?
  answered_by:
  - informativeness-correlates
misreadings:
- '"Mediocre" anchors are not weak models: mediocrity is defined relative to the pool being
  ranked, so a pool of frontier models needs a frontier-level mid-ranked anchor.'
- The inverted U-shape is not a claim that o3 is a bad model; o3 fails as an anchor because
  it sits at the top of the evaluated pool, and any model in that position would fail the
  same way.
- 'Using several anchors instead of one does not remove the need to choose well: a single
  random anchor reaches .92 Kendall''s tau with the quadratic ranking while the strongest
  model reaches .82.'
- The study does not propose replacing anchor-based evaluation with an alternative protocol;
  it keeps the protocol and gives guidelines for using it reliably.
links_extra:
  code: https://github.com/IBM/Anchor-Selection
  dataset: https://huggingface.co/datasets/ibm-research/900K-Judgements
---
