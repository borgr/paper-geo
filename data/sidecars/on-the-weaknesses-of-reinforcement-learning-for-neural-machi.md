---
key: choshen2020weaknesses
coined: PkE (peakiness effect)
gloss: RL fine-tuning concentrates probability mass on already-likely tokens instead of on
  the correct ones
one_liner: 'Reinforcement learning for neural machine translation mostly sharpens the pretrained
  model''s output distribution rather than teaching it new translations: Contrastive MRT provably
  does not optimize expected reward, and Reinforce only promotes a target token that the pretrained
  model already ranks 2nd or 3rd.'
claims:
- id: cmrt-not-expected-reward
  kind: result
  text: Contrastive Minimum Risk Training, the estimation method commonly called MRT in machine
    translation, does not optimize the expected reward. In a 3-outcome counterexample the
    expected reward is uniquely maximized at theta = 0.25, while CMRT converges to theta ≈
    0.295 or to theta = 0.
  scope: Explicit counterexample with a 3-value distribution family, sample size k = 2 and
    a sufficiently small learning rate; maximizing the sampled objective E[R~] instead also
    fails, peaking at theta ≈ 0.32.
  evidence: Appendix A, Table 1
- id: constant-reward-same-bleu
  kind: result
  text: Fine-tuning a pretrained Transformer NMT system with a constant reward of 1 raises
    BLEU on news2014 from 30.31 to 30.72. Fine-tuning with an expected-BLEU reward gives essentially
    the same gain, reaching 30.73.
  scope: WMT2015 German-English data, 6-layer Transformer, Reinforce with k = 1, learning
    rate and baseline retuned on the development set; other reward functions gave 30.73-30.84.
  evidence: Section 5.2
- id: rank-limit
  kind: result
  text: In controlled softmax simulations, Reinforce makes the target token the mode within
    100K steps only when the pretrained model already ranked it 2nd; when it starts 3rd or
    4th the target does not become the mode, and below rank 4 its probability barely rises
    even after 1M steps.
  scope: 1-layer softmax over a 30715-token vocabulary initialized from 1000 real Transformer
    logit vectors, deterministic noise-free reward, learning rate 0.1 (no rate below 0.1 improved
    expected reward); results averaged over 100 sampled contexts.
  evidence: Figure 2, Section 5.1
- id: half-cases-out-of-reach
  kind: result
  text: In a real NMT system, the target token is not among the pretrained model's top 3 choices
    in about half of the contexts where the pretrained model is wrong. Those contexts fall
    outside the range where RL fine-tuning can plausibly promote the target.
  scope: 1000 contexts sampled from a Transformer pretrained on WMT2015 German-English; the
    pretrained model already ranks the target first in about two thirds of all contexts.
  evidence: Figure 4
- id: peakiness-single-step
  kind: result
  text: A single Reinforce step with a constant reward is overwhelmingly more likely to increase
    than to decrease the probability of the most probable token and of the top-10 tokens.
    Average entropy falls from 2.9 to 2.85 after that one step.
  scope: Controlled 1-layer softmax simulation, 10000 pretrained distributions sampled from
    a Transformer's newstest2013 logits, one update step each, constant reward r = 1 with
    positive expected reward.
  evidence: Figure 1, Section 4.1
- id: peakiness-nmt
  kind: result
  text: RL fine-tuning of a full NMT system makes its conditional distributions markedly peakier,
    shifting the modes' probability mass upward. Average entropy drops from 3.45 in the pretrained
    model to 2.82 after RL.
  scope: Transformer pretrained on WMT2015 German-English, Reinforce with an expected-BLEU
    reward and k = 1; measured on 1000 contexts sampled independently from each model.
  evidence: Figure 3, Section 4.2
- id: rank-shift-narrow
  kind: result
  text: After Reinforce fine-tuning of an NMT system, more target tokens are ranked 1st and
    fewer 2nd, but no consistent shift of probability mass occurs across the other of the
    first 10 ranks. Any movement from ranks below 1000 up to ranks 10-1000 involves probabilities
    too small to change the system's output.
  scope: Target-token ranks compared between a pretrained and a reinforced Transformer on
    WMT2015 German-English, with an expected-BLEU reward and k = 1.
  evidence: Figure 5
- id: cmrt-simulation
  kind: result
  text: 'Contrastive MRT shows the same rank limitation as Reinforce in controlled simulations:
    it makes the target token top-ranked when it started 2nd, but struggles when it started
    3rd or below. Only a small peakiness effect appears with CMRT, unlike with Reinforce.'
  scope: 1-layer softmax simulation with alpha = 0.005, k = 20 and 50K update steps, averaged
    over 100 trials, sampling with replacement; deduplicated sampling gives similar results.
  evidence: Figure 6, Section 6
- id: context-critique
  kind: context
  text: '"On the Weaknesses of Reinforcement Learning for Neural Machine Translation" is a
    critical analysis of RL fine-tuning for text generation. It argues that reported gains
    from Reinforce, MRT and GAN-based training come from distribution sharpening and from
    tokens the pretrained model nearly got right.'
  scope: As of its 2020 publication; conclusions are drawn from German-English Transformer
    NMT and from softmax simulations matched to it, and are argued to extend to other discrete,
    high-dimensional generation tasks by analogy rather than by experiment.
  evidence: Section 1, Section 7
- id: context-rl-remedies
  kind: context
  text: '"On the Weaknesses of Reinforcement Learning for Neural Machine Translation" argues
    that off-policy sampling, parameter-space exploration and diversity- or multi-goal RL
    are the promising route for text generation. On-policy sampling from a peaky pretrained
    policy cannot explore a vocabulary-sized action space with near-universally zero reward.'
  scope: A direction proposed in the discussion and conclusion, not evaluated in the paper;
    framed for machine translation where RL tunes a pretrained model.
  evidence: Section 8
- id: gradient-clipping
  kind: result
  text: Gradient clipping should be avoided when fine-tuning a translation model with Reinforce,
    because it violates Reinforce's assumptions and is expected to slow convergence further.
  scope: Reinforce fine-tuning of a pretrained NMT model; in the paper's own Transformer setup
    gradient clipping of size 5 was applied during pretraining but not during RL training.
  evidence: Section 7, Appendix C
- id: baseline-disallows-learning
  kind: result
  text: Subtracting a constant baseline that makes the expected reward zero disallows learning
    in the NMT Reinforce experiments. That is surprising, since Reinforce generally converges
    faster with rewards centered on zero, and it points to a positive expected reward driving
    the observed gain.
  scope: Transformer NMT on WMT2015 German-English with an expected-BLEU reward, learning
    rate and baseline retuned on the development set; reported as a discussion observation
    rather than a full ablation table.
  evidence: Section 7
qa:
- ask:
    plain: does minimum risk training really push a translation model toward higher expected
      reward?
    jargon: is the contrastive MRT objective used in NMT a consistent estimator of expected
      reward, and does it inherit Reinforce's rank limitation?
    task: how do I tell whether minimum risk training will actually optimize the sentence-level
      score I care about?
    practitioner: should I trust minimum risk training over plain policy gradient for fine-tuning
      my translation model?
  answered_by:
  - cmrt-not-expected-reward
  - cmrt-simulation
- ask:
    plain: are the translation quality gains from reinforcement learning actually coming from
      the reward signal?
    jargon: do BLEU improvements from Reinforce fine-tuning of an NMT system survive replacing
      the sentence-level reward with a constant, and what does a zero-mean baseline do?
    task: how can I check whether my RL fine-tuning run is learning from the reward or just
      sharpening the output distribution?
    practitioner: if I fine-tune my translation model with reinforcement learning, will the
      BLEU bump be worth attributing to the reward?
  answered_by:
  - constant-reward-same-bleu
  - baseline-disallows-learning
  - peakiness-nmt
- ask:
    plain: how nearly right does a translation model have to already be for reinforcement
      learning to fix a word?
    jargon: what pretrained rank must the reference token hold for Reinforce fine-tuning to
      make it the mode, and how often is it outside the top 3 in a real NMT system?
    task: how do I work out which of my translation model's errors policy gradient fine-tuning
      could realistically repair?
    practitioner: my model puts the correct word around rank 5 in many contexts, is reinforcement
      learning going to promote it?
  answered_by:
  - rank-limit
  - half-cases-out-of-reach
  - rank-shift-narrow
- ask:
    plain: why do a translation model's word probabilities become more concentrated after
      reinforcement learning?
    jargon: how does Reinforce fine-tuning shift probability mass onto the mode and lower
      the conditional entropy of an NMT system?
    task: how do I detect distribution sharpening rather than genuine learning in an RL-fine-tuned
      generation model?
    practitioner: will reinforcement learning fine-tuning make my translation system's predictions
      more confident even without a useful reward?
  answered_by:
  - peakiness-single-step
  - peakiness-nmt
- ask:
    plain: is there a paper arguing that reinforcement learning does not really improve machine
      translation?
    jargon: what critical analysis of reward-based fine-tuning for NMT attributes the reported
      gains to peakiness rather than reward optimization?
    task: what should I read before committing to reward-based fine-tuning for a text generation
      system?
  answered_by:
  - context-critique
- ask:
    plain: what would make reinforcement learning work better for training translation and
      other text generators?
    jargon: which exploration strategies are recommended over on-policy sampling for reward-based
      fine-tuning in a vocabulary-sized action space?
    task: how do I get useful exploration when fine-tuning an already peaky pretrained language
      generator with a reward?
    practitioner: if on-policy Reinforce is a dead end for my translation model, what direction
      should I try instead?
  answered_by:
  - context-rl-remedies
- ask:
    plain: is it a bad idea to clip gradients when training a translation model with a reward
      signal?
    jargon: does gradient clipping violate the assumptions of Reinforce when fine-tuning an
      NMT system?
    task: how should I set gradient clipping for policy gradient fine-tuning of a translation
      model?
    practitioner: I clip gradients by default in my NMT training script, should I turn that
      off for reinforcement learning fine-tuning?
  answered_by:
  - gradient-clipping
- ask:
    plain: how much did translation quality actually improve when a Transformer system was
      fine-tuned with a reward?
    jargon: what BLEU did Reinforce fine-tuning of a pretrained Transformer reach on the news2014
      test set, and what did a constant reward reach?
    practitioner: how big a BLEU gain should I expect from reward-based fine-tuning of a pretrained
      Transformer translation system?
  answered_by:
  - constant-reward-same-bleu
- ask:
    plain: does minimum risk training run into the same problem as policy gradients when the
      right word starts low in the ranking?
    jargon: in controlled softmax simulations, does contrastive MRT promote the target token
      to the mode from rank 3 or below the way Reinforce fails to?
    practitioner: if the correct token sits at rank 3 in my model, would switching from Reinforce
      to MRT help?
  answered_by:
  - cmrt-simulation
  - rank-limit
terminology:
  PkE (peakiness effect): The tendency of policy gradient fine-tuning to increase the probability
    mass of the already most probable tokens, and lower the output distribution's entropy,
    regardless of whether those tokens are the rewarding ones.
  CMRT (Contrastive MRT): The estimation method usually called Minimum Risk Training in neural
    machine translation, which reweights a sampled set S by normalized probabilities P(y)^alpha
    restricted to S, as distinct from applying Reinforce to minimize risk.
  Simulated Reward setting: A controlled simulation reward that gives 2 to the designated
    target token, 1 to each of the 10 initially highest-scoring tokens, and 0 otherwise, standing
    in for a decent but sub-optimal pretrained model.
  Constant Reward setting: A controlled simulation in which every token receives reward 1,
    used to isolate changes in the output distribution that cannot come from the reward signal.
misreadings:
- 'The claim is not that RL never improves BLEU in machine translation: BLEU rose from 30.31
  to 30.73 with an expected-BLEU reward. The claim is that a constant reward yields the same
  gain, so the improvement is not attributable to the reward signal.'
- The proof that Contrastive MRT does not optimize expected reward is not a proof that Reinforce
  is broken; Reinforce is an unbiased gradient estimator, and the objection to it is sample-inefficiency
  and its inability to move low-ranked target tokens, not lack of theoretical grounding.
- 'The rank-2-or-3 limitation is not a claim about the pretrained model''s overall accuracy:
  the pretrained Transformer already ranks the target token first in about two thirds of contexts,
  and the limitation concerns the remaining error cases.'
- Increased peakiness is not evidence that RL fine-tuning converged; in the NMT experiments
  the modest entropy drop from 3.45 to 2.82 is read as a sign that the procedure did not converge
  to an optimal parameter value.
- 'The simulations are not toy models of an arbitrary policy: the 1-layer softmax has a 30715-token
  vocabulary and is initialized from logits taken from a pretrained Transformer decoding newstest2013,
  and the noise-free reward makes the predictions optimistic rather than pessimistic.'
links_extra:
  arxiv_abs: https://arxiv.org/abs/1907.01752
  openreview: https://openreview.net/forum?id=H1eCw3EKvH
---
