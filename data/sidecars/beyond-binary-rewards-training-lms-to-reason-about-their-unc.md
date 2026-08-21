---
key: damani2026rlcr
coined: RLCR
gloss: reinforcement learning with calibration rewards — training a reasoning model to output
  a confidence score alongside its answer, rewarded by a Brier score
one_liner: RLCR adds a Brier-score term to the binary correctness reward of reasoning RL,
  so models learn to emit a calibrated confidence estimate alongside their answer without
  sacrificing task accuracy.
links_extra:
  project page: https://rl-calibration.github.io/
  arXiv: https://arxiv.org/abs/2507.16806
terminology:
  RLCR reward: The sum of a binary correctness indicator and a negative Brier score on the
    model's verbalized confidence, used as the RL reward for a reasoning model that outputs
    both an answer and a confidence in [0,1].
  RLVR: 'Reinforcement learning with verifiable rewards: RL on reasoning chains using only
    a binary indicator of whether the final answer matches the ground truth.'
  uncertainty analysis: A segment of the chain-of-thought, emitted in <analysis> tags after
    the answer, in which the model enumerates specific ways its own solution could be wrong
    before stating a numerical confidence.
  confidence-weighted majority vote: Test-time aggregation over N sampled responses in which
    each vote is weighted by the model's own verbalized confidence rather than by an external
    reward model.
  inter-solution consistency: The property that, when a model samples several answers to a
    mutually exclusive question, the mean confidences assigned to the distinct answers sum
    to at most 1.
claims:
- id: rlcr-context
  kind: context
  text: RLCR shows that RL for reasoning can optimize calibration alongside correctness by
    adding a proper-scoring-rule term to the binary correctness reward. Confidence is learned
    by the reasoning model itself rather than fitted post hoc by a separate model.
  scope: As of the 2026 publication; earlier RL-for-calibration work optimized calibration
    alone and was evaluated on non-reasoning tasks. Demonstrated on 7B-8B open models.
- id: theorem-bounded-proper
  kind: result
  text: A reward equal to a scaled correctness indicator minus a proper scoring rule provably
    incentivizes a calibrated confidence and the answer with the highest success probability.
    The guarantee requires the scoring rule's S(p,1)-S(p,0) to be bounded by the correctness
    weight lambda.
  scope: Assumes the correctness indicator for a fixed prediction is Bernoulli and that confidence
    can be chosen freely. Brier satisfies the bound at lambda=1; the log score does not, since
    S(p,1)-S(p,0) diverges as p approaches 0.
  evidence: Theorem 1 and Appendix A (Lemma 1, Lemma 2, Corollary 1)
- id: hotpot-ece
  kind: result
  text: On in-distribution HotpotQA, RLCR cuts expected calibration error from 0.37 to 0.03
    and Brier score from 0.37 to 0.21 relative to RLVR, at 62.1% versus 63.0% accuracy.
  scope: Qwen2.5-7B base, GRPO with no KL regularization, trained on 20,000 HotpotQA-Modified
    examples; evaluated at temperature 0 with exact-match correctness.
  evidence: Table 1(a)
- id: math-ece
  kind: result
  text: Trained on Big-Math, RLCR reduces in-domain expected calibration error from 0.26 to
    0.10 versus RLVR while matching accuracy (72.7% vs 72.9%) averaged over MATH-500, GSM8K
    and Big-Math.
  scope: Qwen2.5-7B base; Big-Math subset of 15,000 numerical-answer problems with LLaMA-8B
    solve rate between 0 and 70%; correctness scored by math-verify.
  evidence: Table 1(b)
- id: ood-calibration
  kind: result
  text: Averaged over 6 out-of-distribution datasets, RLVR training on HotpotQA worsens Brier
    score from the base model's 0.41 to 0.46, whereas RLCR improves it to 0.21 and raises
    AUROC from 0.50 to 0.68.
  scope: Qwen2.5-7B trained only on HotpotQA-Modified; OOD set is TriviaQA, SimpleQA, MATH-500,
    GSM8K, CommonsenseQA and GPQA. OOD accuracy is roughly flat for all RL methods.
  evidence: Table 1(a), O.O.D. Averaged columns
- id: beats-classifiers
  kind: result
  text: RLCR reaches out-of-distribution Brier score 0.21 with a single model, against 0.27
    for a same-size BCE confidence classifier and 0.32 for a Brier-loss classifier. A linear
    probe on RLVR embeddings reaches 0.38 and answer-token probability 0.42.
  scope: Classifiers and probe are trained on RLVR outputs from Qwen2.5-7B on HotpotQA-Modified
    and share the RLVR generator, so their accuracies equal RLVR's. In-distribution the BCE
    classifier is close (ECE 0.07 versus RLCR's 0.03).
  evidence: Table 1(a)
- id: log-score-collapse
  kind: result
  text: 'Replacing the Brier term with the unbounded log score collapses training on a 5-arm
    next-draw prediction task: RLCR-Log outputs the invalid arm at confidence 0 and reaches
    0 accuracy. RLCR-Brier on the same task reaches 34.4% accuracy at ECE 0.02.'
  scope: 'Qwen2.5-7B trained on 10,000 synthetic toy-arm examples with high aleatoric uncertainty
    and no uncertainty reasoning. On HotpotQA the same substitution does not collapse: RLCR-Log
    reaches 59.5% accuracy and ECE 0.07 (Table 3).'
  evidence: Figure 6 (Toy Arm Task table)
- id: confidence-weighted-scaling
  kind: result
  text: Weighting majority votes by an RLCR model's own verbalized confidence yields higher
    accuracy than plain majority vote, max-confidence selection, and two generation-likelihood
    baselines as the number of samples grows.
  scope: RLCR trained on HotpotQA, accuracy averaged over the 7 evaluation datasets of Table
    1; needs no external reward model or extra supervision.
  evidence: Figure 3
- id: reward-beats-prompting
  kind: result
  text: Prompting an RLVR model to reason about uncertainty at test time lowers HotpotQA ECE
    only from 0.37 to 0.34, whereas training with the calibration reward reaches 0.03. Calibration-aware
    reward matters far more than the uncertainty-reasoning prompt.
  scope: 'HotpotQA-trained Qwen2.5-7B models; RLVR w/ Analysis uses the identical analysis
    prompt RLCR was trained with. Both components help: OOD Brier is 0.41 for RLVR w/ Analysis
    versus 0.46 for plain RLVR.'
  evidence: Table 2
- id: no-analysis-variant
  kind: result
  text: RLCR without any uncertainty analysis in the chain-of-thought matches RLVR's accuracy
    (61.7% vs 63.0%) and token cost (113 vs 92 tokens) on HotpotQA while cutting ECE from
    0.37 to 0.09.
  scope: Qwen2.5-7B trained on HotpotQA-Modified, evaluated with the analysis section removed
    at inference. Full RLCR with analysis is still better calibrated (ECE 0.03) at 249 tokens.
  evidence: Table 2
- id: self-consistency
  kind: result
  text: Resampling multiple uncertainty-reasoning chains for the same answer from an RLCR
    model gives confidence scores with mostly low standard deviation, so the model has little
    'uncertainty about its uncertainty'.
  scope: RLCR trained on HotpotQA, standard deviations over analysis chains for a fixed solution
    across 7 datasets. Variability is higher when full chains, and hence answers, are resampled.
  evidence: Figure 4
- id: confidence-sums
  kind: result
  text: RLCR's mean confidences over distinct sampled answers sum to close to the ideal 1
    on in-distribution HotpotQA, but exceed 1 out of distribution, so overconfidence on contradictory
    answers persists.
  scope: Three representative datasets, HotpotQA-trained Qwen2.5-7B; questions with mutually
    exclusive answers only. RLCR's sums are closer to 1 than RLVR's in every case shown.
  evidence: Figure 4
- id: model-generality
  kind: result
  text: The accuracy-neutral calibration gain of RLCR reproduces on OlMo-2-7B-Instruct (HotpotQA
    ECE 0.38 for RLVR versus 0.09 for RLCR) and on Qwen-3-8B (OOD Brier 0.28 versus 0.17).
  scope: Both trained on HotpotQA-Modified with the main GRPO setup; accuracy within about
    1 point of RLVR in each case.
  evidence: Table 4 and Table 5
- id: calibration-only-rl-collapses
  kind: result
  text: Optimizing a Brier reward alone over the whole generation collapses a HotpotQA reasoning
    model to 0.00 accuracy, with empty or trivial answers at confidence 0. Restricting that
    reward to the analysis and confidence spans preserves 62.0% accuracy but leaves OOD Brier
    at 0.27 versus RLCR's 0.21.
  scope: Calibration-only baselines are initialized from the RLVR model, not the base model,
    and use no KL regularization. An abstention-RL baseline with reward 0.5 for abstaining
    reaches OOD Brier 0.35.
  evidence: Table 6
qa:
- ask:
    plain: if a model is trained to say how sure it is, does it get worse at getting answers
      right?
    jargon: does adding a proper-scoring-rule calibration term to a binary correctness reward
      trade off task accuracy against calibration error?
    task: how do I train a reasoning model to output a confidence score without losing accuracy
      on the task itself?
    practitioner: should I worry about losing accuracy if I add a confidence reward to my
      RL fine-tuning run?
  answered_by:
  - theorem-bounded-proper
  - hotpot-ece
  - math-ece
- ask:
    plain: which formula for scoring a stated confidence is safe to use as a training reward,
      and which one breaks?
    jargon: why is a bounded Brier term preferred over the logarithmic scoring rule when combined
      with a correctness reward in RL?
    task: which scoring rule should I pick for the confidence part of my reward so training
      does not degenerate?
    practitioner: can I just use log loss on the verbalized confidence as my calibration reward,
      or will that blow up?
  answered_by:
  - theorem-bounded-proper
  - log-score-collapse
- ask:
    plain: does reinforcement learning on right-or-wrong answers make a model more overconfident?
    jargon: how does RLVR with binary verifiable rewards affect Brier score and AUROC, including
      on datasets outside the training distribution?
    task: how do I tell whether my RL-tuned reasoning model became less reliable at judging
      its own answers on new tasks?
    practitioner: my model was RL-trained on correctness only, should I expect its confidence
      estimates to be trustworthy off-distribution?
  answered_by:
  - ood-calibration
  - reward-beats-prompting
- ask:
    plain: is it better to have the model itself state how sure it is, or to bolt a separate
      confidence predictor on top?
    jargon: how does verbalized confidence trained with a calibration-augmented RL reward
      compare with post-hoc confidence heads, linear probes on hidden states, and answer-token
      likelihood?
    task: how do I get calibrated uncertainty for a reasoning model without training and serving
      a second scoring model?
    practitioner: should I train a separate confidence classifier for my reasoning model or
      train the model to report confidence itself?
  answered_by:
  - beats-classifiers
  - calibration-only-rl-collapses
- ask:
    plain: can a model's own stated confidence be used to pick among several sampled answers?
    jargon: does weighting majority voting by verbalized confidence outperform unweighted
      self-consistency and generation-likelihood weighting as sample count grows?
    task: how do I aggregate multiple sampled answers at inference time without running a
      reward model or verifier?
    practitioner: is my model's stated confidence good enough to weight best-of-N or voting
      at test time?
  answered_by:
  - confidence-weighted-scaling
- ask:
    plain: is asking a model to think about how unsure it is enough, or does the training
      reward have to change?
    jargon: is the calibration improvement attributable to the calibration-augmented reward
      or to uncertainty reasoning in the chain of thought?
    task: how do I improve my model's confidence estimates - change the prompt to reason about
      uncertainty, or change the training objective?
    practitioner: can I skip retraining and just prompt my reasoning model to assess its own
      uncertainty?
  answered_by:
  - reward-beats-prompting
  - no-analysis-variant
- ask:
    plain: does making a model report calibrated confidence make its answers much longer?
    jargon: what is the token overhead of calibration-trained verbalized confidence relative
      to a correctness-only RL baseline, and does dropping the uncertainty analysis retain
      the calibration gain?
    task: how do I add calibrated confidence output without increasing inference cost per
      response?
    practitioner: will adding confidence training blow up my generation length and serving
      cost?
  answered_by:
  - no-analysis-variant
- ask:
    plain: if you ask a model the same question twice, does it give the same confidence number?
    jargon: how stable are verbalized confidence scores across resampled uncertainty-reasoning
      chains, and do mean confidences over distinct sampled answers sum to 1?
    task: how do I check whether the confidence numbers my model emits are reproducible enough
      to threshold on?
    practitioner: can I rely on a single sampled confidence score from my model, or do I need
      to average several?
  answered_by:
  - self-consistency
  - confidence-sums
- ask:
    plain: do the confidence gains show up on more than one base model, or just the one it
      was developed on?
    jargon: does the accuracy-neutral calibration improvement from a Brier-augmented RL reward
      replicate across base model families such as OlMo-2-7B-Instruct and Qwen-3-8B?
    task: how do I know whether calibration-augmented RL will work on the base model I actually
      use?
    practitioner: my base model is not Qwen2.5, will calibration training still help me?
  answered_by:
  - model-generality
- ask:
    plain: what should I read first about getting reinforcement-learned reasoning models to
      know when they are wrong?
    jargon: what work established that calibration can be optimized jointly with correctness
      in RL with verifiable rewards using a proper scoring rule?
    task: where do I start reading about training reasoning models to report reliable confidence
      instead of fitting confidence after the fact?
  answered_by:
  - rlcr-context
- ask:
    plain: what happens if a model is rewarded only for accurate confidence and not for being
      right?
    jargon: does optimizing a calibration reward alone over the whole generation induce reward
      hacking such as degenerate answers at confidence 0?
    task: how do I set up a confidence reward so the model cannot game it by giving up on
      the answer?
    practitioner: can I drop the correctness term and train on the calibration reward alone?
  answered_by:
  - calibration-only-rl-collapses
  - log-score-collapse
- ask:
    plain: after training a model to report confidence, how much overconfidence is left on
      tasks it never saw?
    jargon: how much residual calibration error and cross-answer confidence mass remains out
      of distribution after Brier-augmented RL training?
    task: how do I estimate how far I can trust confidence scores on domains outside the training
      distribution?
    practitioner: is out-of-domain calibration good enough after this kind of training that
      I can act on the confidence numbers?
  answered_by:
  - ood-calibration
  - confidence-sums
misreadings:
- 'RLCR does not improve out-of-domain accuracy in the HotpotQA experiments: the base model,
  RLVR and RLCR all sit near 53-56% OOD accuracy, and the contribution is calibration at unchanged
  accuracy rather than a better task solver.'
- The proof does not license any proper scoring rule as a calibration reward. Only bounded
  ones satisfy the correctness condition; the logarithmic score is proper but unbounded and
  can make an incorrect answer with confidence 0 the reward-maximizing output.
- The log-score collapse is not a claim that log-score RL always fails in practice. On HotpotQA
  an RLCR-Log model reaches 59.5% accuracy and ECE 0.07 with no sign of degenerate behaviour;
  the collapse was observed on a synthetic high-aleatoric-uncertainty toy task.
- 'Out-of-domain calibration is not solved: RLCR''s OOD ECE stays around 0.21 on the HotpotQA-trained
  model, and confidences assigned to mutually exclusive answers still sum to more than 1 outside
  the training distribution.'
- Strong calibration numbers on CommonsenseQA for RLVR are not evidence that RLVR is calibrated
  there. RLVR predicts 85-100% confidence on nearly every question, which coincidentally matches
  that dataset's roughly 90% accuracy.
- The SFT warmup variant is not a strict improvement. SFT+RLCR gives the best calibration
  on the math setting but drops out-of-domain accuracy from 50.9% to 43.8%, and most of that
  loss is a formatting bias recoverable by one extra prompt line (49.8%).
---
