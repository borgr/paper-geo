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
    to prior RL-for-calibration work that optimizes calibration alone, and then reproduces
    at 0.00 accuracy in an appendix.'
  evidence: Theorem 1, Section 3, Appendix A, Appendix E, Appendix I, Section 5
- id: log-score-hacks-a-toy-task-and-not-qa
  text: 'The paper builds the log score''s failure mode and measures it. On a five-arm next-draw
    prediction task, an RLCR variant rewarded with the log score converges to answering with
    the invalid arm at confidence 0 -- 0% accuracy with a perfect 0.00 Brier and 0.00 calibration
    error -- while the Brier variant keeps predicting, at 34.4% accuracy and 0.02 calibration
    error. Trained on HotpotQA instead, the log-score variant does not collapse: 59.5% accuracy,
    0.22 Brier and 0.07 calibration error against Brier''s 62.1%, 0.21 and 0.03.'
  scope: 'So boundedness is a guarantee against a failure that does not always occur. The
    authors say so directly -- for many datasets hacking may not happen in practice, and they
    expect its emergence to depend on the data distribution and the model size. The toy task
    is engineered for the regime where the log score''s expected reward is non-monotonic in
    the true correctness probability: short observation sequences (zero to five draws), an
    arbitrary arm distribution, and an explicit abstain option, so aleatoric uncertainty is
    high by construction. The toy runs use no uncertainty analysis. Read the toy result as
    a demonstration that the theorem''s gap is reachable, and the HotpotQA result as evidence
    that Brier''s practical margin over log score is about a point, not a category.'
  evidence: Appendix E.1, Appendix E.2, Appendix E.3, Figure 5, Figure 6, Table 3
- id: calibration-only-rl-collapses
  text: 'Rewarding calibration alone collapses, and the paper measures the collapse rather
    than only predicting it: a Brier-only reward applied over the whole generation reaches
    0.00 accuracy with a perfect 0.00 Brier and 0.00 calibration error. Masking the loss off
    the thinking and answer spans prevents that -- 62.0% accuracy -- but calibration stays
    behind RLCR, 0.08 against 0.03 in domain and 0.25 against 0.21 out of it. Abstention-RL,
    which pays an intermediate reward for saying "I don''t know", lands at 62.1% accuracy
    with calibration error 0.31 in domain and 0.35 out of it.'
  scope: 'Every RL-for-calibration baseline beats plain RLVR on calibration (0.37 and 0.46)
    and loses to RLCR, so the comparison establishes ordering within a family rather than
    RLCR against nothing. It is not head-to-head on initialization: the two calibration-only
    variants start from the paper''s own RLVR model, which the authors say may be a poor starting
    point for further RL because of reduced entropy, while Abstention-RL starts from the base
    model since it optimizes accuracy too. Abstention-RL produces no confidence, so its calibration
    is measured by prompting it at test time never to abstain -- and its reward only ever
    teaches whether internal confidence clears the 0.5 threshold, not a graded confidence.
    The authors'' own two hypotheses for the masked variant''s remaining gap -- bad initialization,
    or a genuine complementarity between the accuracy and calibration gradients -- are labelled
    as hypotheses.'
  evidence: Appendix I, Table 6
- id: rlvr-confidence-is-uninformative
  text: 'The confidence a standard reasoning-trained model states is close to worthless: its
    AUROC is 0.50 on in-domain HotpotQA and 0.47 on math -- chance -- against 0.54 and 0.56
    for the base model it was trained from. Ordinary RL does not merely make confidence badly
    scaled, it removes the signal that would let confidence separate correct from incorrect
    answers.'
  scope: 'Its expected calibration error is 0.37 in-domain on HotpotQA and 0.26 on math, and
    in all four of the paper''s RLVR cells that error is within a point or two of 1 minus
    its accuracy (0.37 against 63.0% accurate, 0.26 against 72.9%, 0.46 against 53.9%, 0.49
    against 52.5%) -- the arithmetic signature of a model that answers with near-certainty
    whatever it is asked. That arithmetic is a derivation from the paper''s own table, but
    the underlying behaviour is stated outright in the appendices: RLVR consistently predicts
    85-100% confidence across all questions and all datasets, its confidence histogram puts
    almost all mass in the 0.9-1.0 bin, and out of domain its answers stated at 0.8-0.9 confidence
    are right about 30% of the time. RLCR''s histogram instead spreads across the range with
    substantial mass at 0.4-0.8. The confidence has to be elicited from RLVR at test time
    by appending a fixed continuation to the reasoning chain, since it was never trained to
    produce one.'
  evidence: Table 1a, Table 1b, Appendix B.4, Appendix H.1, Appendix L, Figure 8, Figure 9
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
  scope: 'Both accuracy differences are slightly in RLVR''s favour, and the appendix''s per-dataset
    tables give the interval that settles it: 63.0% +/- 3.05 for RLVR against 62.1% +/- 3.05
    for RLCR on HotpotQA, as half-widths of 95% bootstrap confidence intervals over the evaluation
    set. The gap is an order of magnitude inside the interval, so this is parity, not RLCR
    being marginally behind. Those intervals are over evaluation examples rather than training
    seeds -- every cell is a single run -- and the calibration-error columns carry no interval
    at all. The 0.37 to 0.03 figure is in-domain HotpotQA and is the paper''s largest calibration
    improvement; the equivalent out-of-domain numbers are far larger in absolute terms. Accuracy
    on HotpotQA is exact string match against the gold answer, which will score some acceptable
    answers as wrong for every method equally.'
  evidence: Table 1a, Table 1b, Section 4.2, Section 4.3, Appendix L, Table 11
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
- id: the-out-of-domain-average-hides-a-reversal
  text: The out-of-domain average is an average over datasets that disagree. Against RLVR's
    calibration error, the HotpotQA-trained RLCR model wins on SimpleQA (0.34 against 0.88),
    TriviaQA (0.06 against 0.38), GPQA (0.16 against 0.60) and MATH-500 (0.19 against 0.61),
    ties on GSM8K (0.20 against 0.20), and loses on CommonsenseQA (0.30 against 0.09) -- where
    it is also worse than the untrained base model's 0.00.
  scope: 'The win-tie-loss tally is a derivation from the appendix''s per-dataset tables,
    not a count the paper reports; the paper does acknowledge considerable per-dataset variance
    and singles out CommonsenseQA. Its explanation is sound and worth keeping: RLVR states
    85-100% confidence on essentially every question of every dataset, and CommonsenseQA is
    a dataset where all methods score about 90%, so uniform overconfidence is accidentally
    well calibrated there. But the other half is that RLCR is genuinely off by 0.30 on that
    dataset while still ranking answers best on it (AUROC 0.73 against RLVR''s 0.50) -- the
    discrimination survives where the absolute numbers do not. Anyone deploying this should
    expect the calibration gain to be dataset-dependent even though its sign is usually right.'
  evidence: Appendix L, Table 8, Table 9, Table 10, Table 11
- id: replicates-on-two-other-model-families
  text: The calibration result replicates on two other backbones. From OlMo-2-7B-Instruct,
    RLCR reaches 61.3% accuracy against RLVR's 61.7% with in-domain calibration error 0.09
    against 0.38, and 0.20 against 0.48 out of domain. From Qwen3-8B it reaches 61.8% against
    62.7% with 0.23 against 0.36 in domain and 0.17 against 0.29 out of it.
  scope: 'What replicates is the calibration gain at matched accuracy. The out-of-domain accuracy
    edge from the main table does not: on OlMo-2 RLCR is behind RLVR out of domain (49.3%
    against 50.8%) and on Qwen3 it is a tie (65.6% against 65.5%), so the 56.2%-against-53.9%
    edge on Qwen2.5-7B should be read as one backbone''s result rather than a property of
    the method. Qwen3 also weakens the paper''s premise rather than the method: its base model
    is already reasonably calibrated out of domain (0.28) and RLVR barely degrades that (0.29),
    so the "RL wrecks calibration" starting point is much milder on a newer instruction-tuned
    model -- while RLCR still improves on it. Both replications are HotpotQA-trained only,
    one run each, and reported in an appendix.'
  evidence: Appendix F.1, Appendix F.2, Table 4, Table 5
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
  text: 'Fixing the answer and resampling only the uncertainty analysis gives a narrower spread
    of confidences than resampling whole reasoning chains, so most of the variance in a stated
    confidence comes from which solution the model found rather than from indecision about
    a solution it has. Across distinct answers the confidences behave more like probabilities
    under RLCR than under RLVR: on in-domain HotpotQA they sum to about 1, as they should
    when only one answer can be right.'
  scope: The narrower distribution is explicitly not a collapse -- the appendix says the answer-conditioned
    spread still shows non-trivial variance rather than concentrating near zero -- so "the
    model is confident about its confidence" overstates it; averaging over 16 analyses improves
    the Brier score only modestly, which is the practical consequence. Out of domain both
    models still sum to more than 1, so assigning high confidence to contradictory answers
    survives training; RLCR is closer to the ideal, not at it. Both findings are read from
    distribution plots with no summary statistics in the text, so treat the direction as the
    result. The sum-to-one criterion applies only where answers are mutually exclusive, and
    is an equality only when the sampled answers are exhaustive.
  evidence: Section 4.4, Section 4.5, Appendix H.2, Figure 3b, Figure 4a, Figure 4b, Figure
    10
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
- id: analysis-text-helps-small-readers-only
  text: 'The uncertainty analysis does carry calibration-relevant information, but only for
    a reader that needs it: classifiers trained to predict correctness from RLCR''s reasoning
    chains (with the confidence tags stripped out) beat classifiers trained on RLVR''s chains
    at 0.5B and 1.5B, and the two perform similarly at 7B.'
  scope: 'The authors'' reading is that a sufficiently expressive classifier can infer confidence-relevant
    features from the solution alone, so the analysis text matters most when capacity is limited
    -- a bound on how much the explicit uncertainty reasoning is doing, from the paper itself.
    The test is a probe of what the chains contain, not of the RLCR policy: nothing here says
    a 7B RLCR model would do as well without writing the analysis, which is what the separate
    test-time ablation measures. The confidence tags are removed specifically so the classifier
    cannot copy the answer. Read from a figure with no numbers in the text, and the authors
    flag the capacity relationship as future work.'
  evidence: Appendix G, Figure 7
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
  text: 'Warm-starting the math run with supervised finetuning on uncertainty analyses written
    by a stronger model gives the best calibration in the paper -- AUROC 0.78, Brier 0.14,
    error 0.08 in domain and 0.66, 0.24, 0.18 out of it -- while its out-of-domain accuracy
    falls to 43.8%, below the untrained base model''s 47.8%. An appendix then shows most of
    that drop is not forgetting: the model names the right answer in its reasoning and writes
    an unrelated number in the answer tag, and one added prompt line telling it not to put
    arbitrary numbers there recovers 43.8% to 49.8%, against plain RLCR''s 50.9%.'
  scope: 'So the main table''s caption attributing the collapse to catastrophic forgetting
    is corrected by the paper''s own appendix, which says the degradation is not solely forgetting
    and that residual forgetting is much smaller than the authors first suspected -- a case
    where the sentence a reader is most likely to quote is the one the paper later walks back.
    The warmup is small and deliberately partial: 500 base-model solutions with analyses generated
    by DeepSeek-R1, which was never asked for confidence scores, so only the analysis style
    is distilled. The fix is a test-time prompt change with nothing retrained. The appendix''s
    table caption says the recovery is to 48% while its own text and table say 49.8%. The
    variant exists only for the math models, so there is no HotpotQA counterpart to check
    the pattern against.'
  evidence: Table 1b, Section 4.3, Appendix B.2, Appendix J, Table 7
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
    takes the distractor set''s ten paragraphs (two supporting, eight distractors) and removes
    both, one, or neither supporting paragraph for equal thirds of 20,000 questions, leaving
    exactly eight paragraphs in every case -- 2/6, 1/7 or 0/8 -- so a third are unanswerable
    from the context and the model cannot tell which third it is in. The math set is 15,000
    Big-Math problems filtered to numerical answers and to a 0-70% solve rate for a reference
    Llama-8B.'
  scope: 'Numerical answers only, because verifier noise on free-form answers caused training
    instability -- so the reward is clean at the cost of question variety. Every model is
    evaluated at temperature 0; correctness is exact match on HotpotQA, math-verify on the
    three math sets, and a Llama-3.1-8B-Instruct judge on TriviaQA, SimpleQA, CommonsenseQA
    and GPQA, with the reasoning trace withheld from the judge. Malformed outputs are re-queried
    with a fixed continuation appended before being scored, which the base model needs far
    more often than the RL-trained models -- a deliberate leniency that makes the base baseline
    stronger than a strict parse would. The RL recipe is GRPO with two modifications: the
    standard-deviation division is dropped from the advantage, following Turtel et al., which
    the authors suggest helps on extremely miscalibrated examples, and token losses are aggregated
    with BNPO over the active tokens in the local batch. 32 samples per prompt at temperature
    0.7, effective batch 2048, one epoch, constant learning rate 1e-6 for HotpotQA and 5e-6
    for math with a 0.1 warmup ratio, completion cap 1536 for HotpotQA and 4096 for math,
    on a mix of A100 and H100 hardware.'
  evidence: Section 4.2, Section 4.3, Appendix B.1, Appendix B.2, Appendix B.3, Appendix B.4
- id: the-in-domain-cell-is-the-answerable-split
  text: The 0.03 calibration error everyone quotes is not measured on the training distribution.
    In-domain HotpotQA is 1,000 validation questions from the original distractor set trimmed
    to eight paragraphs with both supporting paragraphs present -- every question answerable.
    On the held-out HotpotQA-Modified split, where a third of questions have no supporting
    paragraph at all, RLCR scores 44.4% accuracy, AUROC 0.80 and calibration error 0.08, against
    RLVR's 46.0%, 0.50 and 0.54.
  scope: 'This mostly favours the paper rather than undercutting it: the gap over RLVR is
    far larger on the harder split (0.08 against 0.54) and RLCR''s ranking ability is its
    best anywhere (0.80). But it means the headline in-domain pair of numbers describes the
    easy condition, and the modified-split column appears only in the appendix. Both HotpotQA
    variants are scored by exact string match against the gold answer, which penalizes acceptable
    paraphrases equally for every method.'
  evidence: Appendix B.3, Appendix L, Table 11
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
- q:
  - Does RLCR work on models other than Qwen?
  - Has this been replicated on another model family?
  - Is the calibration gain specific to one backbone?
  answers:
  - replicates-on-two-other-model-families
  - calibration-gains-generalize
- q:
  - Why not just reward calibration and skip the correctness term?
  - What happens if you train only on a Brier reward?
  - How does RLCR compare to abstention training or teaching a model to say I don't know?
  answers:
  - calibration-only-rl-collapses
  - bounded-scoring-rules-only
  - log-score-hacks-a-toy-task-and-not-qa
- q:
  - Are there datasets where RLCR is worse calibrated than plain RL?
  - Does the calibration gain hold on every benchmark?
  - Why does RLVR look well calibrated on CommonsenseQA?
  answers:
  - the-out-of-domain-average-hides-a-reversal
  - calibration-is-still-poor-in-absolute-terms
- q:
  - Does the uncertainty analysis text actually contain useful information?
  - Is the uncertainty reasoning faithful, or just decoration?
  - Does model size change how much the uncertainty analysis helps?
  answers:
  - analysis-text-helps-small-readers-only
  - reward-beats-prompting
  - analysis-free-variant-is-nearly-free
- q:
  - Which HotpotQA split are the in-domain numbers measured on?
  - Is the reported in-domain calibration measured on the training distribution?
  - What are the error bars on these results?
  answers:
  - the-in-domain-cell-is-the-answerable-split
  - calibration-comes-free-in-accuracy
  - how-the-tasks-and-numbers-were-built
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
- Every result in the main paper is one backbone, Qwen2.5-7B base, at one scale, and every
  cell is a single run. Appendix F does replicate the calibration gain on OlMo-2-7B-Instruct
  and Qwen3-8B at matched accuracy -- but the out-of-domain accuracy edge does not replicate
  (RLCR is behind RLVR on OlMo-2 and level on Qwen3), and nothing here says how the method
  behaves at 70B.
- SFT+RLCR is not a strict improvement over RLCR, and the reason given in the main table's
  caption is not the reason. It has the best calibration in the paper and the worst out-of-domain
  accuracy of any trained model, 43.8%; the caption calls that catastrophic forgetting, and
  Appendix J shows most of it is a formatting bias -- the model wrote arbitrary numbers into
  the answer tag on non-math questions -- which one added prompt line lifts to 49.8%.
- 'The extra uncertainty-reasoning text is what buys calibration, not accuracy: in the ablation
  the highest out-of-domain accuracy, 56.5%, belongs to the variant evaluated with that reasoning
  stripped out, at 113 completion tokens against full RLCR''s 249. If tokens matter more than
  the last 0.05 of calibration error, the cheap variant is the one to use.'
- '"No external reward model needed" compares confidence-weighted voting against other unsupervised
  selection rules -- plain majority vote, most-confident-sample, and two sequence-likelihood
  variants. It is not a comparison against a trained reward model or verifier, and the gaps
  are shown as curves rather than numbers.'
- 'On CommonsenseQA, RLCR is the worst-calibrated method in the table (error 0.30) and RLVR
  looks excellent (0.09), because RLVR states 85-100% confidence on everything and the dataset
  happens to sit at about 90% accuracy. RLCR still has the best AUROC there. The out-of-domain
  average is an average: it hides one reversal and one tie.'
- The 0.03 in-domain calibration error is measured on the answerable variant of HotpotQA --
  both supporting paragraphs present -- not on the HotpotQA-Modified distribution the model
  trained on. On that held-out split RLCR reads 0.08, against RLVR's 0.54.
- '"Log score would be hacked" is proven and then only half observed. A log-score reward does
  collapse to zero accuracy on a toy bandit task built for the regime where its expected reward
  is non-monotonic, but trained on HotpotQA it stays within about a point of the Brier version
  and never degenerates. The authors say hacking''s emergence probably depends on the data
  and the model size.'
- '"Just reward calibration" is not an untested alternative -- Appendix I runs it. Over the
  whole generation it converges to empty answers at confidence 0: perfect Brier, zero accuracy.
  Masking the loss off the answer and thinking spans fixes the accuracy and still leaves calibration
  behind RLCR.'
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
  Abstention-RL: 'The ternary-reward family this paper adapts as a baseline: +1 for correct,
    0 for incorrect, and an intermediate reward (0.5 here) for explicitly saying "I don''t
    know". It teaches only whether internal confidence clears that threshold, never a graded
    confidence, and can suppress exploration on hard questions once abstention is learned.'
  Calibration RL: A baseline that optimizes the Brier score alone with no correctness term.
    Applied over the whole generation it converges to empty answers at confidence 0 -- the
    degenerate optimum Theorem 1 warns about. Restricting the loss to the analysis and confidence
    spans preserves accuracy and still calibrates worse than RLCR.
  answer-conditioned vs answer-independent confidence: 'Two ways of resampling to measure
    how stable a stated confidence is: hold the reasoning and answer fixed and resample only
    the uncertainty analysis, or resample the whole chain so the answer may change. The second
    varies more, so most confidence variance tracks which solution was found rather than indecision
    about a fixed one.'
links_extra:
  project page: https://rl-calibration.github.io/
---
