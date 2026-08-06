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

Then promote it:  python scripts/draft_sidecars.py --accept on-the-weaknesses-of-reinforcement-learning-for-neural-machi
-->
---
coined: peakiness effect (PkE)
gloss: the tendency of RL fine-tuning to concentrate probability mass on the tokens a pretrained
  model already ranked highest, whether or not the reward carries any signal
one_liner: 'RL for machine translation reshapes the output distribution more than it teaches
  new tokens: a constant, uninformative reward reproduces the BLEU gain (30.72 against 30.73),
  Reinforce promotes a target token only if it already ranked second or third, and Contrastive
  MRT provably does not maximize expected reward.'
claims:
- id: constant-reward-reproduces-the-gain
  text: 'The BLEU improvement from RL fine-tuning was reproduced with a reward that carries
    no information at all: training the NMT system with an expected-BLEU reward raised BLEU
    from 30.31 to 30.73, and repeating the identical experiment with a constant reward of
    1 gave 30.72, along with a similar pattern of change in the target tokens'' ranks.'
  scope: One language pair (WMT2015 German-English, tested on news2014), one architecture
    (6-layer Transformer), k = 1, following Yang et al. (2018)'s setup with the learning rate
    and positive baseline retuned. The gain is small in absolute terms -- about 0.4 BLEU --
    but the paper reports it as very stable across metrics, trials and pretrained models,
    with several other reward functions landing at 30.73-30.84. The conclusion drawn is that
    there is 'room to suspect' the gain 'may partially result from' reward-independent factors,
    not that the reward never matters. Appendix D shows the constant-reward run's rank-shift
    pattern directly, and reports it as similar in trend to the informative-reward one.
  evidence: Section 5.2, footnote 4, Section 7, Appendix D (Figures 7 and 8)
- id: peakiness-effect
  text: 'The paper names and demonstrates the peakiness effect (PkE): early in RL fine-tuning,
    probability mass concentrates on the tokens the pretrained model already ranked highest,
    whether or not the reward carries signal. Under a constant reward, a single Reinforce
    step is overwhelmingly more likely to raise the mode''s probability and the top-10 mass
    than to lower it, with average entropy falling from 2.9 to 2.85 in that one step; in the
    full NMT run, entropy fell from 3.45 to 2.82.'
  scope: 'The mechanism is sampling, not the reward: Reinforce''s expected update is zero
    when the reward is constant with respect to the parameters, so with k typically between
    1 and 20 and few epochs it is unlikely that anything but the already-probable tokens gets
    sampled, and those are what get raised. PkE requires the expected reward to stay positive.
    The constant-reward simulation takes a single step from each of 10,000 sampled pretrained
    distributions rather than many steps from one, because the expected update is zero and
    any effect would only be accentuated at the next step. The 2.9-to-2.85 and 3.45-to-2.82
    figures come from the simulation and the NMT run respectively -- not the same quantity
    measured twice.'
  evidence: Section 3, Section 4.1, Figure 1, Section 4.2, Figure 3
- id: policy-collapses-to-determinism
  text: 'With an informative reward the simulated policy does not merely get peakier, it collapses:
    average entropy falls from 3 to about 0.001 over 100K steps, effectively a deterministic
    policy, and the peakiness appears within a few hundred steps -- before any effect attributable
    to the reward''s content becomes prominent.'
  scope: A simulation figure, not an NMT one, and the gap between the two is the point the
    paper draws on. The single-softmax simulation has a noise-free deterministic reward and
    a learning rate of 0.1; the real NMT run's entropy fell only from 3.45 to 2.82, which
    the paper reads as evidence that the procedure did not converge -- had it converged, entropy
    should have dropped either to 0 (overfitting) or to the entropy of the genuinely valid
    next tokens. The collapse is also stronger under the informative reward than under the
    constant one, so the reward does contribute to peakiness; what the constant-reward condition
    shows is that it is not required for it.
  evidence: Section 4.1 (Results), Section 4.2 (Results), Figure 2
- id: one-target-token-assumption
  text: The analysis assumes exactly one valid target token per context, which the paper justifies
    on the grounds that MT systems are in practice trained against a single reference translation,
    and it treats a sparse sentence-level reward as equivalent to a uniform token-level one
    -- which is what licenses studying a single softmax layer in place of a sequence model.
  scope: Both assumptions are stated up front (citing Schulz et al. 2018 for the single reference)
    rather than tested, and they cut in two directions. They make the setting harder than
    reality -- where several high-ranked tokens may all be acceptable continuations, so a
    target token at rank 4 is not necessarily a translation error -- and they also make the
    paper's predictions optimistic in other respects, since the simulated reward is deterministic
    where a real one is approximated by Monte Carlo (20 sentence rolls per word here). The
    token-level reward in the NMT run is an expected-BLEU approximation, not a true token
    reward.
  evidence: Section 2.1, Section 4.1, Section 4.2, Appendix C
- id: improvement-only-near-the-top
  text: 'RL is likely to help only where the pretrained model is already nearly right: in
    controlled simulations Reinforce made the target token the mode within 100K steps only
    when it started as the second most probable token, and where it started below rank four
    its probability barely moved even after 1M steps.'
  scope: 'A single softmax layer over a 30,715-token vocabulary, initialized from 1,000 sets
    of real Transformer logits, with a deterministic reward (2 for the target, 1 for the ten
    initially highest-scoring tokens, 0 otherwise) -- easier than an approximated reward,
    so the predictions are optimistic. The learning rate had to be 0.1 for the expected reward
    to improve at all, three orders of magnitude above the 1e-4 typical in NMT, and the paper
    notes such a rate can hurt in practice: raising it by an order of magnitude in their NMT
    run made early stopping fire before any parameter update. The paper''s own reading of
    a gain confined to the top of the distribution is that it ''may be more easily achieved
    using reranking methods, and uses but little of the power of RL methods''.'
  evidence: Section 5.1, Figure 2, Section 4.1, Section 7
- id: half-the-targets-are-out-of-reach
  text: 'In the real NMT model, the tokens RL could fix are largely the ones it cannot reach:
    the pretrained model ranks the target token below its top three choices in about half
    the cases, and after RL more targets are ranked first and fewer second, with little consistent
    shift of probability mass anywhere else in the first ten ranks.'
  scope: The denominator matters and the paper is terse about it. Figure 4 plots the contexts
    where the pretrained model does not rank the target first, and the paper separately reports
    that it already ranks the target first in about two thirds of contexts -- so read 'about
    half ranked fourth or below' as about half of the model's errors, not half of all tokens.
    Measured on 1,000 contexts sampled from the pretrained model plus an independent sample
    from the reinforced one. RL may have moved some targets from very low ranks (below 1000)
    into the 10-1000 range, but probabilities there are too small to change any output.
  evidence: Section 5.2, Figure 4, Figure 5, footnote 3
- id: cmrt-does-not-optimize-reward
  text: 'Contrastive Minimum Risk Training -- the estimation method most MT work means by
    ''MRT'' -- provably does not maximize the expected reward, nor even the expected value
    of its own sampled objective: in the paper''s three-outcome counterexample the expected
    reward is uniquely maximized at 0.25, but CMRT with k = 2 converges to about 0.295 from
    any initialization in the interior (and to 0 if started there), while maximizing the expectation
    of its objective instead peaks at about 0.32.'
  scope: A counterexample, so it refutes the general guarantee rather than measuring how far
    off CMRT lands in a real system. The construction is a one-parameter family of distributions
    over three values with rewards 1, 0 and 0.5, and the size of the gap depends on the parameterization
    -- the paper notes that with a different reparameterization the convergence point can
    be pushed arbitrarily far from the optimum, which is a statement about the absence of
    a bound, not a stronger empirical result. This contradicts Sakaguchi et al. (2017), who
    described CMRT as a variant of Reinforce. The paper still studies CMRT rather than dismissing
    it, because it is widely used and has yielded strong results.
  evidence: Appendix A, Table 1 (Appendix A), Section 2.3, footnote 1
- id: cmrt-behaves-like-reinforce
  text: 'Contrastive MRT hits the same reachability limit as Reinforce while showing only
    a small peakiness effect: with the common settings alpha = 0.005 and k = 20 it promoted
    the target token to the top when that token started second, but struggled when it started
    third or below, and its contrastive term -- which keeps unsampled tokens from losing probability
    mass -- is why PkE stays small.'
  scope: The same single-softmax-layer simulation and Simulated Reward setting as the Reinforce
    experiments, averaged over 100 trials, sampling with replacement; deduplicated sampling
    gave similar results. No full NMT run with CMRT is reported, so the CMRT evidence here
    is simulation plus the Appendix A proof rather than an end-to-end translation experiment.
    One value of alpha was tested, not a sweep.
  evidence: Section 6, Figure 6
- id: constant-vs-informative-reward-diagnostic
  text: 'The paper''s method is a control condition rather than a new metric: running an identical
    RL setup twice, once with an informative reward and once with a constant one, separates
    improvements that come from the training signal from improvements that come from the update
    rule reshaping the distribution.'
  scope: A methodological contribution demonstrated here for Reinforce and CMRT in NMT, not
    validated as a general protocol. It works because Reinforce's expected update under a
    constant reward is provably zero, so whatever still moves is not the signal. Applying
    it requires the constant to keep the expected reward positive -- a zero-mean reward removes
    the effect being probed and, in their NMT run, stopped learning entirely.
  evidence: Section 1, Section 4.1, Section 5.2, Section 7
- id: sample-inefficiency
  text: The paper estimates that RL fine-tuning of NMT performs on the order of 1M update
    steps in practice -- roughly 30 epochs sampling about 100K tokens each -- and reports
    that wherever Reinforce was not close to converging after 50K simulated steps, it had
    still not converged after 1M.
  scope: The 1M figure is the authors' arithmetic over their own setup, assumed representative
    of other NMT systems; the paper's figures are plotted at 50K-100K steps for legibility.
    This is inefficiency in update steps needed to reorder a distribution, not a wall-clock
    claim -- their pretraining took about 7 days on 4 GPUs and RL training roughly as long
    again, with 20 Monte Carlo sentence rolls per word.
  evidence: Section 4.1, footnote 3, Appendix C
- id: zero-mean-baseline-disallows-learning
  text: Subtracting a constant baseline from the reward so that the expected reward becomes
    zero stopped the NMT system from learning altogether -- which is surprising, because Reinforce
    generally converges faster when the reward is centred on zero and a baseline shift does
    not change the optimal parameters.
  scope: A single observation from their NMT setup, offered as the first of four reasons to
    attribute the BLEU gain to PkE rather than to the reward. It is consistent with PkE needing
    a positive expected reward, since centring at zero removes the mechanism, but it is an
    argument by elimination rather than a measurement of how much of the gain PkE accounts
    for.
  evidence: Section 7, Section 2.2
- id: alpha-tradeoff
  text: 'CMRT''s smoothness parameter alpha faces a tradeoff the paper makes explicit from
    the gradient: below 1 it gives relatively more weight to improbable tokens, which can
    help the convergence rate, but as alpha approaches 0 the gradient of the objective vanishes
    -- which is why the literature reports alpha as needing careful tuning.'
  scope: 'Derived from the gradient of the sampled objective rather than swept empirically
    here; the simulations use a single value, alpha = 0.005. Whether deduplication is applied
    interacts with this: deduplicating shifts relative weight toward improbable tokens, not
    deduplicating shifts it toward high-probability ones and may hurt the convergence rate,
    and implementations differ (THUMT does not deduplicate). Off-policy sampling is offered
    later as a way to get the same smoothing while keeping convergence guarantees.'
  evidence: Section 2.3, Appendix B, footnote 2, Section 8
- id: avoid-gradient-clipping
  text: 'Gradient clipping, which is common in NMT, should not be used with Reinforce: it
    violates Reinforce''s assumptions and is expected to hinder convergence further.'
  scope: 'A theoretical recommendation, not an ablation -- no clipped-versus-unclipped comparison
    is reported. Their own setup follows it partially, clipping at 5 during pretraining and
    not during RL training. Two adjacent practical notes are reasoned the same way rather
    than measured: per-token sampling explores more than beam search, which additionally does
    not properly account for being off-policy in its updates; and adding the reference translation
    to the sampled set can address never sampling the target, but Edunov et al. (2018) report
    it may lower results by pushing the model toward outputs it cannot generalize over.'
  evidence: Section 7, Appendix C
- id: mt-is-a-hard-rl-setting
  text: 'The paper''s account of why RL underdelivers in MT is three properties of the setting
    holding at once: an action space the size of the target vocabulary, or its product over
    a sentence; a reward that is almost everywhere zero, because almost every possible sentence
    is wrong in a given context; and on-policy sampling from a pretrained model that is already
    peaky, which confines exploration to what the model already prefers.'
  scope: 'An argument for why techniques tuned on mainstream RL benchmarks -- small discrete
    action spaces such as video games, or low-dimensional continuous control -- do not transfer,
    rather than a measured decomposition of the failure. Note the internal tension the paper
    points out: pretraining is what makes the reward sparsity survivable, and pretraining
    is also what makes the policy peaky, so the third problem is a consequence of the usual
    fix for the second.'
  evidence: Section 8
- id: explains-the-temperature-result
  text: 'PkE supplies a mechanism for an earlier unexplained result: Caccia et al. (2018)
    found that the gains language GANs show can be matched by simply lowering the prediction
    softmax temperature -- that is, by making the distribution peakier -- without proposing
    an account of why. Because the output space of other generation tasks is likewise discrete,
    high-dimensional and concentrated, the paper expects its findings to carry beyond MT.'
  scope: 'The link is an interpretation the authors argue for, not a result they test on GANs:
    they show PkE occurs under Reinforce, and Caccia et al. separately show peakier distributions
    score better, so the joint reading is that reward-independent peakiness can produce apparent
    gains. The extension to other generation tasks is stated as reasonable to assume given
    those findings, not demonstrated here. It also runs the other way as a caution: a reinforced
    model that is peakier should be expected to score better on BLEU for that reason alone.'
  evidence: Section 4, Section 7
- id: off-policy-and-exploration
  text: 'The paper''s constructive proposal is to import RL machinery that NLP has not adopted:
    off-policy methods, which allow learning from a more exploratory policy and provide smoothing
    while keeping convergence guarantees, unlike CMRT''s alpha; directed exploration driven
    by the exploratory usefulness of states and actions, or by parameter-space rather than
    action-space noise; and diversity-based and multi-goal methods for reward spaces where
    almost nothing is rewarding.'
  scope: A discussion of directions, with no implementation or experiment in this paper. The
    works named are general RL results rather than MT systems built this way, and the argument
    for them is that even effective exploration may not suffice in MT, because the state-action
    space is too large to cover when almost all sentences carry no reward.
  evidence: Section 8
qa:
- q:
  - Does reinforcement learning actually improve neural machine translation?
  - Why does RL fine-tuning give only small BLEU gains in NMT?
  - Is the improvement from RL in machine translation real?
  - What do RL methods actually learn in machine translation?
  answers:
  - constant-reward-reproduces-the-gain
  - peakiness-effect
  - improvement-only-near-the-top
- q:
  - What is the peakiness effect in reinforcement learning for text generation?
  - Why does RL fine-tuning make a model's output distribution peakier?
  - What is PkE in RL for NMT?
  answers:
  - peakiness-effect
  - constant-vs-informative-reward-diagnostic
  - explains-the-temperature-result
- q:
  - Does Minimum Risk Training optimize the expected reward?
  - Is MRT for machine translation theoretically sound?
  - What is the difference between MRT and Reinforce?
  - Is Contrastive MRT just a variant of Reinforce?
  answers:
  - cmrt-does-not-optimize-reward
  - cmrt-behaves-like-reinforce
  - alpha-tradeoff
- q:
  - When is RL fine-tuning worth it for a pretrained sequence model?
  - Under what conditions does Reinforce help an NMT system?
  - Can RL fix translation errors the pretrained model gets badly wrong?
  answers:
  - improvement-only-near-the-top
  - half-the-targets-are-out-of-reach
  - sample-inefficiency
- q:
  - How many update steps does policy-gradient training need in NMT?
  - Why is Reinforce sample-inefficient for text generation?
  - What learning rate does Reinforce need for machine translation?
  answers:
  - sample-inefficiency
  - improvement-only-near-the-top
- q:
  - How do I tell whether my RL gains come from the reward or from something else?
  - How can I check that a reward function is doing any work?
  - What is a good control experiment for RL fine-tuning?
  answers:
  - constant-vs-informative-reward-diagnostic
  - constant-reward-reproduces-the-gain
  - zero-mean-baseline-disallows-learning
- q:
  - Why is machine translation a hard reinforcement learning problem?
  - What makes text generation different from other RL settings?
  - Why does exploration fail in RL for NLP?
  answers:
  - mt-is-a-hard-rl-setting
  - off-policy-and-exploration
  - peakiness-effect
- q:
  - Should I use gradient clipping with Reinforce?
  - Which RL practices should be avoided in NMT?
  - Is it a good idea to add the reference translation to the sampled set?
  answers:
  - avoid-gradient-clipping
  - alpha-tradeoff
- q:
  - How could RL for text generation be made to work better?
  - What alternatives are there to on-policy Reinforce for NLP?
  - Would off-policy RL help machine translation?
  answers:
  - off-policy-and-exploration
  - mt-is-a-hard-rl-setting
  - cmrt-does-not-optimize-reward
- q:
  - Does a baseline help Reinforce in machine translation?
  - Why would centering the reward at zero stop a model from learning?
  answers:
  - zero-mean-baseline-disallows-learning
  - peakiness-effect
- q:
  - Do the gains from language GANs come from the adversarial signal?
  - Why does simply lowering the softmax temperature match GAN improvements?
  - Do these RL findings apply beyond machine translation?
  answers:
  - explains-the-temperature-result
  - peakiness-effect
  - mt-is-a-hard-rl-setting
- q:
  - Does RL fine-tuning reduce a model's output diversity?
  - Why does entropy collapse when you fine-tune a language model with RL?
  - Did the RL run in this paper actually converge?
  answers:
  - policy-collapses-to-determinism
  - peakiness-effect
  - sample-inefficiency
- q:
  - Does this critique of RL apply when a sentence has many valid translations?
  - What does the paper assume about the reference translation?
  - Does the analysis hold for sentence-level BLEU rewards rather than token-level ones?
  answers:
  - one-target-token-assumption
  - mt-is-a-hard-rl-setting
  - improvement-only-near-the-top
misreadings:
- 'This is not a finding that RL does not work for MT. The paper''s own RL run improved BLEU
  from 30.31 to 30.73, and reports that improvement as very stable across metrics, trials
  and pretrained models. The finding is about what produced it: the same gain appears with
  a constant, uninformative reward, and the simulations show the target token becomes the
  mode only when it already ranked second or third. Current practice buys distribution reshaping
  and fine-tuning of near-correct predictions, not a fix for the errors RL was meant to reach.'
- '''MRT'' is ambiguous and the proof applies to one reading of it. Applying Reinforce to
  minimize risk is not what is refuted -- Reinforce''s update is an unbiased estimator of
  the gradient of the expected reward and carries the usual stochastic-gradient guarantees.
  What Appendix A refutes is Contrastive MRT (Och 2003, adapted by Shen et al. 2016), which
  samples k tokens and optimizes a renormalized objective supported only on that sample.'
- PkE is not the softmax temperature, and not a claim that RL only ever makes distributions
  peakier. It is a name for early concentration of mass on already-probable tokens, caused
  by sampling few tokens on-policy from a model that is already peaky. With enough iterations
  the more rewarding tokens do eventually get sampled and gain mass -- the paper's objection
  is the rate at which that happens, not the direction.
- The 30.72 BLEU under a constant reward does not show that reward functions are irrelevant
  in general. It is one language pair, one architecture, k = 1, and one family of rewards,
  and the paper's own wording is that there is 'room to suspect' the gain 'may partially result
  from' reward-independent factors such as PkE.
- 'The simulation numbers are not NMT numbers. Entropy falling from 3 to about 0.001, the
  learning rate of 0.1, and ''the mode within 100K steps'' all come from a single-softmax-layer
  simulation over a 30,715-token vocabulary initialized from real logits. The NMT run has
  its own figures -- entropy 3.45 to 2.82, BLEU 30.31 to 30.73 -- and its own complications
  the simulation lacks: parameters shared across contexts, and rarely sampling the same conditional
  distribution more than a handful of times.'
- '''About half the target tokens are not in the top three'' is a conditional statement. The
  pretrained model already ranks the target first in about two thirds of contexts, and Figure
  4 plots the contexts where it does not, so that half is best read as about half of the model''s
  errors rather than half of all tokens.'
- Appendix A's convergence point of about 0.295 against an optimum of 0.25 is not a measurement
  of how wrong CMRT gets in practice. It is a constructed three-outcome example whose only
  job is to break the guarantee, and the remark that the gap can be made arbitrarily large
  by reparameterizing is a statement about the absence of a bound, not a stronger empirical
  claim.
- The recommendations in the discussion -- avoid gradient clipping with Reinforce, prefer
  off-policy methods, be wary of adding the reference to the sample -- are reasoned from the
  theory and from other people's results, not ablated here. The paper reports no experiment
  isolating any of them.
- The 'rank 2 or 3 or nothing' result is about the rank of a single reference token, under
  the paper's stated assumption that exactly one target token is valid per context. Where
  several continuations are acceptable, a reference token at rank 4 need not mean the model
  is wrong there -- so the assumption makes the setting harder than translation really is,
  at the same time as the noise-free simulated reward makes the paper's convergence predictions
  optimistic. The paper states both, and neither is tested here.
- That the constant-reward NMT run matched the BLEU gain does not mean nothing differed between
  the two runs. What the paper reports as matching is BLEU (30.72 against 30.73) and the trend
  of the target tokens' rank shifts (Appendix D). The informative reward does produce a stronger
  peakiness effect than the constant one in simulation -- the argument is that the reward
  is not necessary for the gain, not that it does nothing.
terminology:
  peakiness effect (PkE): 'This paper''s coined term: the increase in probability mass on
    the most probable tokens during early RL fine-tuning, which occurs even when the reward
    is constant, and which therefore cannot be credited to the training signal. Measured as
    the mode''s probability, the total probability of the top ten tokens, and entropy.'
  Contrastive MRT (CMRT): 'This paper''s name for the estimation method usually called Minimum
    Risk Training in MT: sample k tokens, then optimize an objective renormalized over just
    that sample. The rename exists because the method is distinct from applying Reinforce
    to minimize risk, and because Appendix A shows it does not maximize the expected reward.'
  Minimum Risk Training (MRT): Used in the MT literature for two different things -- applying
    Reinforce to maximize expected reward, or the contrastive sampled objective of Och (2003)
    and Shen et al. (2016). The paper separates them because only the first has convergence
    guarantees. Read any 'MRT' result with this ambiguity in mind.
  Simulated Reward / Constant Reward: The two settings of the controlled simulation, and the
    paper's central experimental device. Simulated Reward gives 2 for the target token, 1
    for the ten initially highest-scoring tokens and 0 otherwise; Constant Reward gives 1
    to everything, so any effect it produces is by construction not attributable to the reward.
  peakiness: The probability mass a distribution allocates to its most probable tokens. Not
    a property of the reward or the task -- a property of the output distribution's shape,
    which is why a change in it can raise BLEU without the model having learned anything new.
  y_best: 'The single target token in a given context, i.e. the one the reference translation
    supplies. The paper''s central quantity is where the pretrained model ranks it, because
    that rank predicts whether RL can promote it: rank 2 or 3 yes, rank 4 or below effectively
    no.'
  exposure bias: 'One of the two standard motivations for RL in MT, alongside optimizing non-differentiable
    metrics: a model trained on gold prefixes never sees its own mistakes during training,
    so it cannot recover from them at test time. Worth keeping in view because this paper
    argues against how well current RL practice delivers on that motivation, not against the
    motivation.'
  expected BLEU reward: 'The reward in the NMT experiments, following Yang et al. (2018):
    sample suffixes for the sentence and average their BLEU against the reference, giving
    a Monte-Carlo token-level approximation (20 sentence rolls per word here). So the ''token-level
    reward'' being optimized is itself an estimate, which is why the paper calls its deterministic
    simulated reward the optimistic case.'
  contrastive effect: 'The extra term in CMRT''s gradient, proportional to the gradient of
    log Z(S): because Q is supported only on the k sampled tokens, raising one token''s weight
    costs another sampled token rather than the whole vocabulary, so unsampled tokens do not
    lose mass. It is why CMRT shows only a small peakiness effect, and it may improve the
    convergence rate.'
---
