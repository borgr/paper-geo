<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from build/sidecar_tasks.json. Every claim, number
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

Then promote it:  python scripts/draft_sidecars.py --accept beyond-binary-rewards-training-lms-to-reason-about-their-unc
-->
---
coined: RLCR
gloss: 'Reinforcement Learning with Calibration Rewards: reasoning training whose reward is
  binary correctness plus a Brier score on a confidence the model states itself, so accuracy
  and calibration are optimized by the same objective'
one_liner: 'RLCR adds a Brier score to the binary correctness reward of reasoning training,
  so a model states a confidence it is then scored on: expected calibration error falls from
  0.37 to 0.03 on HotpotQA and 0.26 to 0.10 on math at no cost in accuracy, and unlike ordinary
  RL the improvement survives out of domain.'
claims:
- id: calibration-reward-added-to-correctness
  text: 'RLCR changes one thing about standard reasoning training: the model emits an answer
    and a numerical confidence, and the reward is the usual binary correctness indicator minus
    the squared difference between that confidence and the indicator -- a Brier score. Being
    confidently wrong or unconfidently right is penalized; the answer is still rewarded for
    being right.'
  scope: 'It is a reward change, not an architecture or algorithm change: the same GRPO training,
    initialized from the base model with no KL regularization, and the confidence is generated
    as text inside a <confidence> tag rather than read off logits. The full prompt format
    asks for four blocks -- <think>, <answer>, <analysis>, <confidence> -- and a format reward,
    weighted equally with the calibration reward, enforces their presence and order. Because
    the confidence is verbalized, nothing constrains it to be a probability beyond the reward.'
  evidence: Section 3, Equation 8, Figure 1a, Section 4.1, Appendix B.2
- id: bounded-scoring-rules-only
  text: 'The paper proves the combined reward is maximized by exactly the behaviour wanted
    -- the answer with the highest probability of being correct, paired with a confidence
    equal to that probability -- and that this depends on the calibration term being bounded,
    not merely proper: log loss is a proper scoring rule but unbounded, and adding it to a
    correctness reward does not incentivize correctness.'
  scope: 'The theorem is about where the reward''s optimum lies, not about what the optimizer
    reaches, and it assumes each candidate answer''s correctness is Bernoulli with some probability
    p_y. The generalization is stated as a condition: an analogous result holds for any bounded
    proper scoring rule whose score gap S(p,1) - S(p,0) is below some threshold. The practical
    reading is that a naive log-likelihood calibration reward lets a model buy a perfect calibration
    score by answering wrongly with zero confidence -- the failure mode the paper attributes
    to prior RL-for-calibration work that optimizes calibration alone.'
  evidence: Theorem 1, Section 3, Appendix A, Section 5
- id: rlvr-confidence-is-uninformative
  text: 'The confidence a standard reasoning-trained model states is close to worthless: its
    AUROC is 0.50 on in-domain HotpotQA and 0.47 on math -- chance -- against 0.54 and 0.56
    for the base model it was trained from. Ordinary RL does not merely make confidence badly
    scaled, it removes the signal that would let confidence separate correct from incorrect
    answers.'
  scope: Its expected calibration error is 0.37 in-domain on HotpotQA and 0.26 on math, and
    in all four of the paper's RLVR cells that error is within a point or two of 1 minus its
    accuracy (0.37 against 63.0% accurate, 0.26 against 72.9%, 0.46 against 53.9%, 0.49 against
    52.5%) -- the arithmetic signature of a model that answers with near-certainty whatever
    it is asked. That last step is a derivation from the paper's own table, not a claim the
    paper makes. The confidence has to be elicited from RLVR at test time by appending a fixed
    continuation to the reasoning chain, since it was never trained to produce one.
  evidence: Table 1a, Table 1b, Appendix B.4
- id: rl-degrades-calibration-out-of-domain
  text: 'Reasoning training makes calibration worse than the model it started from, once you
    leave the training task: averaged over six out-of-distribution datasets, RLVR trained
    on HotpotQA reaches Brier 0.46 and calibration error 0.46 against the base model''s 0.41
    and 0.40, and trained on math it reaches 0.49 and 0.49 against 0.46 and 0.45.'
  scope: 'In-domain the same comparison flatters RLVR -- its HotpotQA calibration error, 0.37,
    is below the base model''s 0.53 -- but that is accuracy rising from 39.7% to 63.0% while
    confidence stays pinned high, not calibration improving. The out-of-domain accuracy numbers
    show why this matters: RL buys almost nothing there (53.3% base to 53.9% for RLVR on the
    HotpotQA-trained models), so the calibration loss is not paid for with capability. The
    out-of-distribution sets are TriviaQA, SimpleQA, MATH500, GSM8K, CommonsenseQA and GPQA
    for the HotpotQA-trained models, and TriviaQA, SimpleQA, CommonsenseQA, GPQA and HotpotQA
    for the math-trained ones.'
  evidence: Table 1a, Table 1b, Section 4.2, Section 1
- id: calibration-comes-free-in-accuracy
  text: 'The calibration term costs essentially no accuracy: 62.1% against RLVR''s 63.0% on
    HotpotQA and 72.7% against 72.9% on math, while in-domain calibration error falls from
    0.37 to 0.03 and from 0.26 to 0.10 -- so the worry that a model would deliberately answer
    badly to make its confidence easy to get right does not materialize.'
  scope: Both accuracy differences are slightly in RLVR's favour and neither is accompanied
    by error bars or repeated seeds, so read them as parity rather than as RLCR being marginally
    behind. The 0.37 to 0.03 figure is in-domain HotpotQA and is the paper's largest calibration
    improvement; the equivalent out-of-domain numbers are far larger in absolute terms. Accuracy
    on HotpotQA is exact string match against the gold answer, which will score some acceptable
    answers as wrong for every method equally.
  evidence: Table 1a, Table 1b, Section 4.2, Section 4.3
- id: calibration-gains-generalize
  text: 'The result that distinguishes RLCR is out of domain: trained on HotpotQA and evaluated
    on six unrelated datasets it reaches AUROC 0.68, Brier 0.21 and calibration error 0.21,
    against RLVR''s 0.50, 0.46 and 0.46 and the base model''s 0.54, 0.41 and 0.40 -- and it
    is also the most accurate of the seven methods there, at 56.2%.'
  scope: Where RLVR makes calibration worse than the base model out of domain, RLCR makes
    it better; the math-trained models show the same pattern more weakly (AUROC 0.60, Brier
    0.28, error 0.25 against RLVR's 0.52, 0.49, 0.49). The accuracy edge is small -- 56.2%
    against 53.9% -- and the paper does not claim RL improves out-of-domain accuracy in general;
    it notes the base model is competitive with all RL-trained models there. Three explanations
    are offered for why calibration generalizes -- reasoning about uncertainty explicitly,
    the non-stationarity of a target that moves as the policy improves, and one model sharing
    representations between answering and self-assessment -- and all three are labelled hypotheses.
  evidence: Table 1a, Table 1b, Section 4.2
- id: compared-with-post-hoc-classifiers
  text: The natural alternative -- keep the reasoning model and train a second model to predict
    when it is right -- is competitive in domain and clearly behind out of domain. On in-domain
    math a binary cross-entropy classifier beats RLCR on AUROC (0.78 against 0.67) and Brier
    (0.15 against 0.17) and ties on calibration error at 0.10; averaged over the out-of-distribution
    sets RLCR wins (0.60, 0.28, 0.25 against 0.55, 0.34, 0.33).
  scope: 'So "outperforming classifiers" is an out-of-domain statement plus an in-domain win
    on HotpotQA (0.69, 0.21, 0.03 against 0.66, 0.22, 0.07), not a clean sweep. The classifier
    is initialized from the same Qwen2.5-7B base, so it is as expressive as the policy and
    doubles training and inference cost; a linear probe on the RLVR model''s final-layer embedding
    is much cheaper and much worse (in-domain HotpotQA AUROC 0.55). None of the classifier
    rows have their own accuracy: they score answers RLVR produced, so their accuracy is RLVR''s
    by construction, and the empty accuracy cells in the table are not missing data.'
  evidence: Table 1a, Table 1b, Section 4.1, Section 4.2
- id: answer-probability-ranks-without-calibrating
  text: The cheapest baseline -- average token probability of the answer span -- has the best
    in-domain HotpotQA AUROC of any method, 0.72, above RLCR's 0.69, yet its Brier score and
    calibration error are 0.36 and 0.36. It ranks answers well while being systematically
    overconfident about all of them, because the model commits to its answer during the reasoning
    chain and the answer tokens are then nearly deterministic.
  scope: 'This is the clearest illustration in the paper that the two families of metric measure
    different things: AUROC only cares about the ordering of confidences, Brier and calibration
    error care about their absolute values. The paper describes this baseline as performing
    poorly, which is true of its calibration and false of its in-domain discrimination --
    and out of domain it is poor at both (0.60 AUROC, 0.42 Brier, 0.42 error), as it is on
    math (0.52 AUROC). It also requires token probabilities, so it is unavailable for closed
    models.'
  evidence: Table 1a, Table 1b, Section 4.2
- id: confidence-weighted-test-time-scaling
  text: 'A confidence the model states can be used as its own reward model at test time: weighting
    a majority vote by the verbalized confidence beats plain majority voting, beats picking
    the single most-confident sample, and beats the two sequence-likelihood analogues of both,
    averaged over seven datasets and improving as the sample count grows.'
  scope: 'Measured with the HotpotQA-trained RLCR model over the seven datasets of the main
    table, read from a curve rather than a table, so the gap between the aggregation methods
    is not given numerically. The point of the comparison is that no external reward model,
    verifier or extra supervision is needed -- but it is a comparison against unsupervised
    selection rules, not against a trained reward model or verifier. Weighting by confidence
    and selecting the most confident sample behave differently: only the first consistently
    helps, which is what you would expect if the confidences are informative but noisy.'
  evidence: Section 4.4, Figure 3a
- id: confidences-are-self-consistent
  text: 'Resampling the uncertainty analysis for a fixed answer yields confidences with low
    standard deviation, so the model has little "uncertainty about uncertainty", and averaging
    over analyses improves the Brier score only modestly for that reason. Across distinct
    answers the confidences behave more like probabilities under RLCR than under RLVR: on
    in-domain HotpotQA they sum to about 1, as they should when only one answer can be right.'
  scope: Out of domain both models still sum to more than 1, so overconfidence in the form
    of assigning high confidence to contradictory answers survives training -- RLCR is closer
    to the ideal, not at it. Both findings are read from distribution plots (a standard-deviation
    histogram over seven datasets and a swarm plot over three) with no summary statistics
    in the text, so treat the direction as the result. The sum-to-one criterion only applies
    where answers are mutually exclusive and is an equality only when the sampled answers
    are exhaustive.
  evidence: Section 4.4, Section 4.5, Figure 3b, Figure 4a, Figure 4b
- id: reward-beats-prompting
  text: 'Prompting a reasoning model to reason about its uncertainty does help, and helps
    far less than training it to: adding the identical analysis prompt to RLVR at test time
    moves its in-domain Brier and calibration error from 0.37 and 0.37 to 0.35 and 0.34, while
    RLCR evaluated with that reasoning stripped out reaches 0.23 and 0.09 -- better than the
    prompted RLVR model by a wide margin.'
  scope: 'A test-time ablation on the HotpotQA-trained models: nothing is retrained, the prompt
    is what changes, so it separates "the model was rewarded for calibration" from "the model
    was asked to think about calibration". Both components contribute in the same direction
    -- adding analysis helps RLVR and RLCR alike, and RLCR is best with it -- but the reward
    accounts for most of the effect. This does not test a model trained with the analysis
    prompt but without the calibration reward.'
  evidence: Table 2, Section 4.6
- id: analysis-free-variant-is-nearly-free
  text: 'The cheap version is most of the win: RLCR evaluated without its uncertainty analysis
    spends 113 completion tokens against RLVR''s 92 -- rather than full RLCR''s 249 -- scores
    61.7% against 63.0% accuracy, and cuts in-domain calibration error from 0.37 to 0.09.
    Out of domain it is the most accurate entry in the ablation at 56.5%, though its calibration
    (0.26) is worse than full RLCR''s (0.21).'
  scope: So the extra reasoning text buys calibration, not accuracy -- the highest out-of-domain
    accuracy in the table belongs to the variant that does not write it. Token counts are
    averages on the HotpotQA-trained models; out of domain the same three variants cost 179,
    300 and 142 tokens. This is one model at one scale, and the calibration ordering out of
    domain (0.21 with analysis, 0.26 without) means the trade is real rather than free.
  evidence: Table 2, Section 4.6
- id: sft-warmup-trades-accuracy-for-calibration
  text: Warm-starting the math run with supervised finetuning on uncertainty analyses written
    by a stronger model gives the best calibration in the paper -- AUROC 0.78, Brier 0.14,
    error 0.08 in domain and 0.66, 0.24, 0.18 out of it -- but its out-of-domain accuracy
    falls to 43.8%, below the untrained base model's 47.8% and seven points below plain RLCR.
  scope: 'The warmup is small and deliberately partial: 500 base-model solutions with uncertainty
    analyses generated by DeepSeek-R1, which was not asked to produce confidence scores, so
    only the analysis style is distilled. The authors attribute the accuracy collapse to catastrophic
    forgetting induced by the SFT phase and say so in the caption, presenting RLCR as the
    better trade-off out of domain. The variant exists only for the math models, so there
    is no HotpotQA counterpart to check the pattern against.'
  evidence: Table 1b, Section 4.3, Appendix B.2
- id: calibration-is-still-poor-in-absolute-terms
  text: 'The paper''s own conclusion is that the problem is not solved: out-of-domain calibration
    error remains 0.21 for the HotpotQA-trained model and 0.25 for the math-trained one --
    seven and two and a half times the in-domain figures the abstract quotes -- and models
    still assign high confidence to mutually contradictory answers.'
  scope: 'Reported as a limitation, not extracted against the authors'' framing. The relative
    claim is what holds up robustly: RLCR is better calibrated than every baseline out of
    domain, and better than the base model it started from, which RLVR is not. Anyone quoting
    0.03 as the calibration achieved by this method is quoting a single in-domain cell.'
  evidence: Section 6, Table 1a, Table 1b, Section 4.5
- id: how-the-tasks-and-numbers-were-built
  text: 'The training task is engineered so that uncertainty is warranted: HotpotQA-Modified
    splits 20,000 multi-hop questions into equal thirds where two, one or none of the supporting
    paragraphs are present, always padding to eight paragraphs, so a third of questions are
    unanswerable from the context and the model cannot tell which third it is in. The math
    set is 15,000 Big-Math problems filtered to numerical answers and to a 0-70% solve rate
    for a reference 8B model.'
  scope: Numerical answers only, because verifier noise on free-form answers caused training
    instability -- so the reward is clean at the cost of question variety. Every model is
    evaluated at temperature 0; correctness is exact match on HotpotQA, math-verify on the
    three math sets, and a Llama-3.1-8B-Instruct judge on TriviaQA, SimpleQA, CommonsenseQA
    and GPQA, with the reasoning trace withheld from the judge. Malformed outputs are re-queried
    with a fixed continuation appended before being scored, which the base model needs far
    more often than the RL-trained models -- a deliberate leniency that makes the base baseline
    stronger than a strict parse would.
  evidence: Section 4.2, Section 4.3, Appendix B.1, Appendix B.3, Appendix B.4
qa:
- q:
  - Does RL training make language models overconfident?
  - Why do reasoning models hallucinate more after RL?
  - What does reinforcement learning with verifiable rewards do to calibration?
  - Is a binary correctness reward bad for uncertainty estimation?
  answers:
  - rl-degrades-calibration-out-of-domain
  - rlvr-confidence-is-uninformative
  - calibration-reward-added-to-correctness
- q:
  - How do you train a model to know when it is wrong?
  - What is RLCR?
  - How do you add calibration to RLVR?
  - Can a reward function optimize accuracy and calibration at the same time?
  answers:
  - calibration-reward-added-to-correctness
  - calibration-comes-free-in-accuracy
  - bounded-scoring-rules-only
- q:
  - Does optimizing for calibration hurt accuracy?
  - Will a model answer badly on purpose to get an easy calibration reward?
  - What is the accuracy cost of adding a confidence reward?
  answers:
  - calibration-comes-free-in-accuracy
  - bounded-scoring-rules-only
  - rl-degrades-calibration-out-of-domain
- q:
  - Why use the Brier score instead of log loss as a reward?
  - Which scoring rules can you safely use as an RL reward?
  - Is a proper scoring rule enough to guarantee correctness?
  answers:
  - bounded-scoring-rules-only
  - calibration-reward-added-to-correctness
- q:
  - Does better calibration transfer to tasks the model was not trained on?
  - How well does calibration training generalize out of domain?
  - If I train for calibration on QA, do I get it on math?
  answers:
  - calibration-gains-generalize
  - rl-degrades-calibration-out-of-domain
  - calibration-is-still-poor-in-absolute-terms
- q:
  - Should I train a separate model to predict whether my LM is right?
  - Is a post-hoc confidence classifier better than training the model to verbalize confidence?
  - Does a linear probe work for confidence estimation?
  - What are the trade-offs of a verifier model versus self-reported confidence?
  answers:
  - compared-with-post-hoc-classifiers
  - calibration-gains-generalize
  - answer-probability-ranks-without-calibrating
- q:
  - Can I just use token probabilities as a confidence score?
  - Why is answer log-probability a bad confidence estimate for reasoning models?
  - Is sequence likelihood good enough for uncertainty estimation?
  answers:
  - answer-probability-ranks-without-calibrating
  - rlvr-confidence-is-uninformative
- q:
  - What is the difference between AUROC and expected calibration error?
  - Which metric should I use to evaluate confidence estimates?
  - Can a model rank its answers well and still be badly calibrated?
  answers:
  - answer-probability-ranks-without-calibrating
  - rlvr-confidence-is-uninformative
  - calibration-is-still-poor-in-absolute-terms
- q:
  - Can verbalized confidence be used for best-of-N or majority voting?
  - How do you do test-time scaling without a reward model?
  - Does confidence-weighted majority vote beat plain majority vote?
  answers:
  - confidence-weighted-test-time-scaling
  - confidences-are-self-consistent
- q:
  - Are a model's stated confidences stable across samples?
  - Do confidences over different answers sum to one?
  - Does averaging several confidence estimates help?
  answers:
  - confidences-are-self-consistent
  - calibration-is-still-poor-in-absolute-terms
- q:
  - Is it enough to prompt a model to reason about its uncertainty?
  - Does asking the model to think about confidence improve calibration?
  - Prompting versus training for calibration -- which matters more?
  answers:
  - reward-beats-prompting
  - analysis-free-variant-is-nearly-free
  - calibration-reward-added-to-correctness
- q:
  - How many extra tokens does uncertainty reasoning cost?
  - Is there a cheap version of calibration training?
  - Can I get calibrated confidence without a long uncertainty analysis?
  answers:
  - analysis-free-variant-is-nearly-free
  - reward-beats-prompting
- q:
  - Does an SFT warmup before RL help calibration?
  - Why does supervised finetuning before RL hurt out-of-domain accuracy?
  - Should I distil uncertainty analyses from a stronger model?
  answers:
  - sft-warmup-trades-accuracy-for-calibration
  - calibration-comes-free-in-accuracy
- q:
  - How was RLCR actually evaluated?
  - How do you build a QA task where the model should be uncertain?
  - What datasets and judges were used to measure calibration here?
  - How do you score a model that answers in the wrong format?
  answers:
  - how-the-tasks-and-numbers-were-built
  - compared-with-post-hoc-classifiers
  - calibration-comes-free-in-accuracy
misreadings:
- 'The headline 0.37 to 0.03 calibration improvement is in-domain HotpotQA and is the paper''s
  best cell. Out of domain the same model sits at 0.21, and the math-trained model at 0.25.
  The paper''s conclusion says so explicitly: out-of-domain calibration error remains high
  in absolute terms. Quote 0.03 as the in-domain figure, not as what the method achieves.'
- RLVR's problem is not that its confidence is badly scaled -- it is that the confidence carries
  no information. AUROC 0.50 in-domain on HotpotQA and 0.47 on math are chance, and in every
  RLVR cell the calibration error is within a point or two of 1 minus accuracy, which is what
  a model that always answers with near-certainty produces. That last step is arithmetic on
  the paper's table, not a claim it makes.
- '"Outperforming classifiers trained to assign post-hoc confidence scores" holds out of domain
  and on in-domain HotpotQA, not everywhere. On in-domain math the binary cross-entropy classifier
  beats RLCR on AUROC (0.78 against 0.67) and Brier (0.15 against 0.17) and ties on calibration
  error. What the classifier does not do is generalize, and it costs a second 7B model.'
- The empty accuracy cells for the classifier and probe rows are not missing data. Those methods
  score answers the RLVR model produced, so their accuracy is RLVR's by construction. Only
  the base model, RLVR, RLCR and SFT+RLCR have accuracies of their own.
- 'The Answer Probability baseline has the best in-domain HotpotQA AUROC in the table, 0.72,
  above RLCR''s 0.69, even though the text calls it poor. Both are right about different things:
  it ranks answers well and is uniformly overconfident, so it wins on AUROC and loses badly
  on Brier and calibration error. It is a good illustration that the two metric families are
  not interchangeable.'
- Theorem 1 says where the reward's optimum lies, not that training reaches it, and it assumes
  each answer's correctness is Bernoulli with a fixed probability. It also does not hold for
  every proper scoring rule -- boundedness is the operative condition, and log loss, though
  proper, fails it.
- Every result in the main paper is one backbone, Qwen2.5-7B base, at one scale. Appendices
  claim generalization to other model families, but those numbers are not present in the retrievable
  text, so nothing here establishes how the method behaves at 70B or on an instruction-tuned
  start.
- SFT+RLCR is not a strict improvement over RLCR. It has the best calibration in the paper
  and the worst out-of-domain accuracy of any trained model -- 43.8%, below the untrained
  base model's 47.8% -- which the authors attribute to catastrophic forgetting from the warmup.
- 'The extra uncertainty-reasoning text is what buys calibration, not accuracy: in the ablation
  the highest out-of-domain accuracy, 56.5%, belongs to the variant evaluated with that reasoning
  stripped out, at 113 completion tokens against full RLCR''s 249. If tokens matter more than
  the last 0.05 of calibration error, the cheap variant is the one to use.'
- '"No external reward model needed" compares confidence-weighted voting against other unsupervised
  selection rules -- plain majority vote, most-confident-sample, and two sequence-likelihood
  variants. It is not a comparison against a trained reward model or verifier, and the gaps
  are shown as curves rather than numbers.'
terminology:
  RLCR: 'Reinforcement Learning with Calibration Rewards. Reasoning training whose reward
    is binary correctness plus a Brier score on a confidence the model itself writes out,
    so one objective covers being right and knowing how likely it is to be right. Not a new
    algorithm: the same GRPO, a different reward.'
  RLVR: Reinforcement learning with verifiable rewards -- the standard recipe behind reasoning
    models, where the reward is 1 if the final answer matches the gold answer and 0 otherwise.
    Cheap to check and impossible to game with fluent text, but it pays the same for a confident
    answer and a guess, which is the gap this paper addresses.
  proper scoring rule: A way of scoring a stated probability against an observed outcome whose
    expected value is optimized by stating the true probability -- so an honest forecaster
    cannot do better by shading its estimate. The Brier score, log loss and spherical score
    are all proper; this paper's point is that properness alone is not enough when the rule
    is added to a correctness reward.
  Brier score: The squared difference between a stated confidence and whether the answer turned
    out to be correct, averaged over examples. Lower is better, it is bounded in [0, 1] for
    confidences in [0, 1], and here it does double duty as both the calibration term in the
    reward and a reported evaluation metric.
  ECE (expected calibration error): Bin the predictions by stated confidence, take the gap
    between average confidence and average correctness within each bin, and average those
    gaps weighted by bin size -- ten bins here. It measures whether the numbers mean what
    they say, and is insensitive to whether they rank answers correctly.
  AUROC: The probability that a randomly chosen correct answer gets a higher confidence than
    a randomly chosen incorrect one. Purely about ordering, so 0.5 is chance and a uniformly
    overconfident model can still score well. Reported alongside Brier and ECE precisely because
    it can disagree with them.
  verbalized confidence: A confidence the model writes out as text, here inside a <confidence>
    tag, rather than one read from token probabilities or a separate head. It works for closed
    models and survives long reasoning chains, but nothing forces it to behave like a probability
    except the reward that trains it.
  uncertainty analysis: The <analysis> block RLCR models write between their answer and their
    confidence, reviewing what could be wrong with the answer they just gave. The paper ablates
    it at test time to separate reasoning about uncertainty from being rewarded for calibration,
    and finds the reward does most of the work.
  confidence-weighted majority vote: Sample several reasoning chains, group them by final
    answer, and weight each vote by the confidence the model stated for it -- the verbalized-confidence
    analogue of reward-weighted voting, needing no reward model. The paper's variant that
    picks the single most-confident sample instead is the analogue of best-of-N and works
    less well.
  HotpotQA-Modified: 'This paper''s training and evaluation variant of the HotpotQA distractor
    set: for a third of questions both supporting paragraphs are present, for a third one
    is removed, for a third both are, always padded back to eight paragraphs. It makes a third
    of questions unanswerable from the context without telling the model which third it is
    looking at.'
links_extra:
  project page: https://rl-calibration.github.io/
---
