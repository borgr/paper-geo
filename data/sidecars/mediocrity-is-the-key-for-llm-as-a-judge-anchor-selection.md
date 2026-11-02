---
key: donyehiya2026mediocrity
one_liner: In anchor-based LLM-as-a-judge evaluation, where every model is compared only to
  one fixed anchor, mid-ranked ("mediocre") anchors give the most faithful rankings, while
  the strongest and weakest models, the usual choices, are the worst anchors because they
  decide most comparisons in advance.
terminology:
  Anchor-based evaluation: An LLM-as-a-judge protocol in which every evaluated model is compared
    only against one fixed reference model (the anchor), reducing the number of judgments
    from quadratic to linear in the number of models.
  Anchor informativeness: The fraction of (sample, model pair) cases in which two models receive
    different verdicts against the same anchor, so the sample can discriminate between them;
    cases where both models get the same verdict carry no ranking signal.
  Quadratic ranking: The ranking obtained by judging every pair of evaluated models on every
    benchmark instruction and aggregating the verdicts with Bradley-Terry, used as the gold
    standard that an anchor-based ranking approximates.
claims:
- id: inverted-u
  kind: result
  text: Anchor quality in pairwise LLM-as-a-judge evaluation follows an inverted U-shape in
    the anchor's own strength. Top-ranked and bottom-ranked anchors give the lowest Kendall's
    tau with the gold ranking, and mid-ranked anchors the highest.
  scope: Arena-Hard-v2.0, 750 instructions, 22 models each used as anchor and competitor,
    5 judges, against both the all-pairs and the human ranking. Replicated on AlpacaEval with
    11 models, where anchor tau ranges from .600 to .964.
  evidence: Figure 1; Figures 12-16; Figures 18-22; Figure 17; Table 8
- id: o3-worst
  kind: result
  text: o3, the top-performing model among 22 on Arena-Hard-v2.0, is the worst anchor under
    all 5 judges tested. With a Deepseek-V3 judge it reaches only .818 Kendall's tau with
    the all-pairs ranking and .324 with the human ranking.
  scope: Worst on both the all-pairs and the human ranking for every judge; with GPT-OSS 120B
    as judge its all-pairs tau falls to .662. Top-performing is relative to this 22-model
    pool.
  evidence: Table 1; Tables 4-7
- id: worst-anchor-drop
  kind: result
  text: A bad anchor instead of the best one costs up to .30 Kendall's tau in correlation
    with the human ranking on Arena-Hard-v2.0. The loss against the all-pairs ranking reaches
    .19.
  scope: 22 candidate anchors and 5 judges; best and worst are the anchors with the highest
    and lowest all-pairs correlation. The .305 human gap is the GPT-OSS 20B judge.
  evidence: Table 3
- id: anchor-vs-judge
  kind: result
  text: Choosing the anchor moves ranking accuracy as much as choosing the judge model. The
    best-to-worst anchor gap in human correlation is .181 to .305 per judge, while the judges'
    own human correlations span .333 to .514.
  scope: 5 open-weight judges (Deepseek-V3, GPT-OSS 120B, GPT-OSS 20B, Qwen3 235B A22B, Qwen3
    8B) on Arena-Hard-v2.0 with 22 models. Similar anchor effects appear at every judge quality
    level.
  evidence: Table 3
- id: wasted-budget
  kind: result
  text: A top-performing anchor wastes most of the judging budget. o3 beats every other model
    on about 500 of 750 Arena-Hard-v2.0 samples, and only 45.5% of its comparisons are informative,
    against 61.1% for o3 Mini.
  scope: Deepseek-V3 as judge, 22 models; informativeness is the share of model pairs that
    receive different verdicts against the anchor.
  evidence: Figure 2; Table 9
- id: informativeness-correlates
  kind: result
  text: An anchor's informativeness rate predicts how accurate its ranking is, with R^2 =
    0.5940 between informativeness and Kendall's tau with the all-pairs ranking across 22
    anchors.
  scope: Arena-Hard-v2.0 with Deepseek-V3 as judge; a single-judge fit over 22 points.
  evidence: Figure 3; Figure 6
- id: benchmark-too-small
  kind: result
  text: Arena-Hard-v2.0's 750 samples are too few to separate models with a +5% win-rate edge
    against an anchor. A sign test needs 617 discordant samples, which becomes 1,372 total
    at a 55% tie rate.
  scope: One-sided sign test, alpha = 0.05, power = 0.80, total inflated by 1/informativeness.
    Larger edges fit, as +10% needs 341 samples at 55% ties.
  evidence: Table 2
- id: wilcoxon-power
  kind: result
  text: Using the judge's win margins through a Wilcoxon signed-rank test cuts the samples
    needed for a +5% edge to 930, from 1143 under the sign test. That is still more than Arena-Hard-v2.0's
    750.
  scope: Simulation over the empirical verdict distributions at the mean informativeness of
    54%, alpha = 0.05, power = 0.80.
  evidence: Section 4.3; Appendix C
- id: informativeness-ceiling
  kind: result
  text: Anchor-based evaluation limits informativeness to at most 0.5 under tie, win or loss
    verdicts, with equality only when the anchor is ranked exactly in the middle. Even the
    most informative anchor tested wastes roughly 39% of the evaluation budget.
  scope: The 0.5 bound assumes magnitude-free verdicts and transitivity. The 39% is o3 Mini
    under a Deepseek-V3 judge on Arena-Hard-v2.0.
  evidence: Section 4.3
- id: anchor-count
  kind: result
  text: Adding anchors helps less than choosing the first one well. A single random anchor
    already averages .92 Kendall's tau with the all-pairs ranking, against .82 for the strongest
    model as anchor.
  scope: Bradley-Terry over random anchor sets grown from 1 to 22 models, 40 shuffled permutations,
    Deepseek-V3 judge on Arena-Hard-v2.0. Tau reaches 1.0 by construction at 22 anchors.
  evidence: Figure 7
- id: cheap-estimation
  kind: result
  text: Anchor informativeness can be screened with only 10 benchmark samples. The estimate
    correlates with full-dataset informativeness at Pearson r above 0.86 for 3 or more models,
    and above 0.91 for 8 or more.
  scope: Arena-Hard-v2.0, pool sizes 3 to 22, 30 repetitions. The 10-sample screen always
    placed the best and worst models among the 3 least informative anchors.
  evidence: Section 5.3; Table 10
- id: sample-size-sensitivity
  kind: result
  text: Anchor-based rankings depend far more on benchmark size than all-pairs rankings. The
    mean anchor-based human correlation only approaches the all-pairs one at about 600 samples,
    and o3 as anchor stays far below at every size.
  scope: Sample sizes 50 to 750 on Arena-Hard-v2.0, 4 of 5 judges. With the Qwen3 8B judge
    the mean anchor-based correlation exceeds the all-pairs one from about 150 samples.
  evidence: Figure 4; Figures 8-11
- id: contribution
  kind: context
  text: '"Mediocrity is the key for LLM as a Judge Anchor Selection" (ACL 2026) is a systematic
    study of anchor choice in LLM-as-a-judge leaderboards. It treats the anchor, not the judge,
    as the overlooked design decision in Arena-Hard- and AlpacaEval-style evaluation.'
  scope: As of publication in 2026; it keeps the anchor protocol and gives practices for it,
    rather than proposing an alternative. Open-ended generation benchmarks in English.
  evidence: Section 7
- id: recommendations
  kind: context
  text: '"Mediocrity is the key for LLM as a Judge Anchor Selection" gives a decision procedure
    for pairwise evaluation. Avoid an external anchor if a natural baseline exists or 3 or
    fewer models are compared, else pick a mid-performing anchor and report its informativeness.'
  scope: Leaderboards needing a full ranking of 4 or more models; with 3 models all pairs
    cost the same 3N judgments. Mediocre is relative to the pool being ranked.
  evidence: Figure 5; Section 6
- id: released-judgments
  kind: context
  text: '"Mediocrity is the key for LLM as a Judge Anchor Selection" releases about 900K LLM
    judge verdicts. They cover all pairs of 22 models on 750 Arena-Hard-v2.0 instructions
    for each of 5 judges.'
  scope: 5 open-weight judges and no commercial judge; verdicts on a 5-level scale from clear
    loss to clear win. Hosted on Hugging Face as ibm-research/900K-Judgements.
  evidence: Section 3.2
qa:
- ask:
    plain: When every model is scored against one common opponent, should that opponent be
      the strongest model or an average one?
    jargon: How does Kendall's tau with the all-pairs ranking vary with the strength of the
      anchor model in pairwise LLM-as-a-judge evaluation?
    task: How do I choose which model to use as the fixed reference opponent in an Arena-Hard-style
      leaderboard?
    practitioner: Which reference model should I score all my models against in a pairwise
      judge leaderboard?
    adjacent: Is AlpacaEval-style win rate against a single reference model a reliable way
      to rank language models?
  answered_by:
  - inverted-u
  - recommendations
- ask:
    plain: Does comparing every model against the best available model make an automatic leaderboard
      less accurate?
    jargon: How much Kendall's tau with human and all-pairs rankings is lost when a frontier
      model such as o3 serves as the pairwise anchor?
    task: How do I avoid ranking errors from using a top-tier model as the fixed opponent
      in pairwise LLM evaluation?
    practitioner: Would benchmarking my models against o3 as the reference distort my leaderboard?
  answered_by:
  - o3-worst
  - worst-anchor-drop
- ask:
    plain: 'In head-to-head model comparisons scored by a language model, which matters more:
      the judging model or the model everyone is compared against?'
    jargon: Is the best-to-worst anchor spread in human correlation comparable to the spread
      across judge models in LLM-as-a-judge evaluation?
    task: How do I decide whether to spend effort on picking the judge or on picking the reference
      opponent for a pairwise leaderboard?
    practitioner: Should I upgrade my judge model or rethink the baseline model I compare
      everything against?
    adjacent: Beyond benchmarking LLM judges for system ranking, does the choice of reference
      system change the ranking as much as the judge does?
  answered_by:
  - anchor-vs-judge
- ask:
    plain: When every model is compared with one fixed opponent by an automatic judge, how
      many comparisons tell you nothing about the ranking?
    jargon: What is the informativeness rate of an anchor in pairwise LLM-as-a-judge evaluation,
      and what caps it under win/tie/loss verdicts?
    task: How do I stop wasting LLM judge calls on pairwise comparisons whose outcome is decided
      before they run?
    practitioner: How much of my pairwise LLM judging budget is actually buying ranking signal?
  answered_by:
  - wasted-budget
  - informativeness-ceiling
- ask:
    plain: Do opponent models that produce more decisive comparisons give more accurate LLM
      leaderboards?
    jargon: Does an anchor's informativeness rate predict the Kendall's tau between its induced
      ranking and the all-pairs ranking?
    task: What should I measure about a candidate reference model to predict how accurate
      its pairwise LLM ranking will be?
  answered_by:
  - informativeness-correlates
- ask:
    plain: Is a 750-prompt benchmark big enough to tell apart two language models with slightly
      different win rates?
    jargon: How many samples are needed to detect a 5% win-rate edge at 80% power in anchor-based
      pairwise evaluation, given anchor tie rates?
    task: How many prompts do I need so a pairwise win-rate difference between two LLMs is
      statistically significant?
    practitioner: Can I trust a small win-rate lead my model shows on Arena-Hard-v2.0?
  answered_by:
  - benchmark-too-small
  - wilcoxon-power
- ask:
    plain: Does an automatic leaderboard built by comparing against one opponent need more
      test prompts than one comparing all pairs?
    jargon: How does Kendall's tau of anchor-based versus all-pairs Bradley-Terry rankings
      change with the number of benchmark instructions?
    task: How do I tell whether my benchmark is large enough for an anchor-based LLM-as-a-judge
      ranking?
  answered_by:
  - sample-size-sensitivity
- ask:
    plain: Can a handful of prompts tell you in advance whether a candidate opponent model
      will produce decisive comparisons?
    jargon: How well does anchor informativeness measured on 10 samples correlate with full-dataset
      informativeness?
    task: How do I screen candidate reference models cheaply before running the full pairwise
      LLM evaluation?
    practitioner: Can I run a small pilot to pick my baseline model instead of judging the
      whole benchmark for each candidate?
  answered_by:
  - cheap-estimation
- ask:
    plain: If several opponent models are used instead of one, does that remove the risk of
      picking a bad opponent?
    jargon: Does aggregating rankings over multiple random anchors recover all-pairs Kendall's
      tau better than one well-chosen anchor?
    task: 'How do I get a reliable pairwise LLM ranking: add more reference models, or spend
      the effort choosing one?'
    practitioner: Is it worth paying for LLM judgments against several reference models instead
      of one mid-ranked one?
  answered_by:
  - anchor-count
- ask:
    plain: What should I read about how reliable leaderboards built from automatic head-to-head
      model comparisons are?
    jargon: Which study examines anchor selection, rather than judge selection, in Arena-Hard-
      and AlpacaEval-style LLM-as-a-judge leaderboards?
    task: Where should I start reading before designing a pairwise LLM-as-a-judge evaluation
      of my models?
  answered_by:
  - contribution
  - inverted-u
- ask:
    plain: Is there a public collection of automatic judge decisions covering many pairs of
      language models on the same prompts?
    jargon: Are there released pairwise LLM judge verdicts over all model pairs on Arena-Hard-v2.0
      for multiple judges?
    task: Where can I get existing pairwise LLM judge verdicts to test ranking methods without
      paying for inference?
    practitioner: Can I reuse existing LLM judge verdicts instead of running all the pairwise
      comparisons myself?
  answered_by:
  - released-judgments
misreadings:
- '"Mediocre" anchors are not weak models: mediocrity is relative to the pool being ranked,
  so a pool of frontier models needs a frontier-level mid-ranked anchor.'
- o3 being the worst anchor does not mean o3 is a bad model; it fails as an anchor because
  it sits at the top of the evaluated pool and beats most opponents on most samples.
- 'Using several anchors does not remove the need to choose well: a single random anchor averages
  .92 Kendall''s tau with the all-pairs ranking, while the strongest model as anchor reaches
  .82.'
- The anchor-selection study does not replace anchor-based evaluation with an alternative
  protocol; it keeps the protocol and gives practices for using it reliably.
links_extra:
  code: https://github.com/IBM/Anchor-Selection
  dataset: https://huggingface.co/datasets/ibm-research/900K-Judgements
---
