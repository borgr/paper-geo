<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced via a forced tool call). Every claim, number
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

Then promote it:  python scripts/draft_sidecars.py --accept dora-the-explorer-directed-outreaching-reinforcement-action

Stamp: spec=d57862840a90 checks=3 body=7cde4a1767d5
-->
---
key: DBLP:conf/iclr/FoxCL18
coined: E-values (DORA)
gloss: 'propagating exploration counters: a second value function, learned with zero reward
  and optimistic initialization, whose logarithm acts as a visit counter that spreads over
  trajectories'
one_liner: DORA learns a second, reward-free value function called E-values alongside Q, initialized
  to 1 and updated by SARSA, so that log of the E-value acts as a visit counter that propagates
  exploratory value along whole trajectories instead of one step ahead — giving model-free
  directed exploration.
claims:
- id: e-values-generalize-counters
  kind: context
  text: DORA introduces E-values, a model-free generalization of visit counters that propagates
    exploratory value along state-action trajectories, filling a gap where earlier propagating-exploration
    schemes were model-based.
  scope: As of ICLR 2018; earlier propagation of exploration values (Storck et al. 1995, Meuleau
    & Bourgine 1999, Little & Sommer 2014) required an estimated model of the MDP, and counter-based
    model-free bonuses evaluated novelty only one step ahead.
- id: log-e-is-a-counter
  kind: result
  text: With exploration discount gamma_E = 0, the E-value of a state-action pair visited
    n times equals (1-alpha)^n, so log base (1-alpha) of E is exactly the visit counter; with
    gamma_E > 0 it grows more slowly and each visit of an action with many possible outcomes
    contributes less than one generalized count.
  evidence: Section 2.3 and Figure 1
  scope: Tabular setting with learning rate alpha shared between Q and E; exact equality to
    n requires gamma_E = 0 or a terminal state with a single action. The tree-MDP simulation
    in Figure 1 varies the number of leaves k.
- id: bonus-beats-standard-counters
  kind: result
  text: 'Adding a 1/log_(1-alpha)E exploration bonus to the reward speeds up convergence of
    an epsilon-greedy agent on the bridge MDP, and larger exploration discounts help more:
    gamma_E = 0.9 learns faster than gamma_E = 0, which is equivalent to standard visit counters.'
  evidence: Figure 3
  scope: Short bridge environment with k = 5, tabular Q-learning, epsilon fitted per agent
    to optimize learning, stochastic agents averaged over 50 trials; convergence measured
    as MSE between Q and Q* weighted by state-action visitation under the optimal policy.
- id: lll-outperforms-counters-and-stochastic
  kind: result
  text: On the long bridge environment with k = 15, E-value LLL agents are the first to reach
    low MSE between Q and Q*, while stochastic and counter-based epsilon-greedy agents and
    the standard UCB-like agent fail to converge.
  evidence: Figure 4
  scope: Tabular bridge MDP, k = 15, gamma_E = 0.9 unless stated otherwise; epsilon and temperature
    fitted separately per agent, stochastic agents averaged over 50 trials. Comparators are
    epsilon-greedy, Softmax, their counter-based LLL determinizations, and a UCB-like rule
    with sqrt(log t / C) bonus.
- id: generalized-counters-track-missing-knowledge
  kind: result
  text: Convergence level |(Q-Q*)/Q*| is a single common function of the generalized counter
    log_(1-alpha)E across all state-action pairs, whereas against ordinary visit counters
    the same quantity depends on which state-action is being counted.
  evidence: Figure 5
  scope: E-value LLL Softmax agent on the short bridge environment with k = 5, recorded at
    the end of each episode; a qualitative pattern across state-action pairs rather than a
    fitted functional form.
- id: freeway-faster-convergence
  kind: result
  text: On the Freeway Atari 2600 game, a two-stream network predicting Q and E with an exploration
    bonus of beta/sqrt(-log E) and beta = 0.05 converges in roughly 2x10^6 steps, versus about
    10x10^6 steps reported for the density-model counters of Bellemare et al. (2016).
  evidence: Section 4.1 and Figure 6
  scope: Single game (Freeway) with epsilon-greedy action selection; the DQN baseline here
    lacks the Double DQN and Monte-Carlo return enhancements used in the density-model work,
    so the step-count comparison is across papers rather than a matched ablation.
- id: freeway-beats-density-counters
  kind: result
  text: E-value exploration bonuses outperform both a plain DQN baseline and density-model
    counter bonuses on Freeway, and training with density-model counters was an order of magnitude
    slower than training the two-streamed E-value network.
  evidence: Figure 6
  scope: Freeway only, all agents using epsilon-greedy action selection with the bonus added
    to the reward, beta = 0.05, built on the atari-rl DQN implementation; the runtime comparison
    is wall-clock for these implementations, not an asymptotic claim.
- id: determinization-theorem
  kind: result
  text: Any deterministic action-selection rule that never picks an action whose empirical
    frequency exceeds its target probability by more than a sub-linear b(t) has action frequencies
    converging to the stochastic rule f(a), which is what licenses replacing epsilon-greedy
    or Softmax by a counter-based deterministic equivalent.
  evidence: Theorem 3.1 in Section 3.2.1, proved in Appendix A
  scope: An in-the-limit equivalence of action frequencies at fixed Q-values and a fixed state,
    not a claim about finite-time behaviour or about learning speed; two concrete determinizations
    are given, argmin_a C(a)/C - f(a) and the LLL rule argmax_a f(a)/C(a).
- id: e-values-with-function-approximation
  kind: result
  text: With linear tile-coding function approximation on MountainCar, the summed generalized
    counter C_E(s) recovered from the learned E-value weights correlates strongly and positively
    with the empirical visit histogram throughout training, using far fewer parameters than
    a table of state-action counters at the same binning resolution.
  evidence: Appendix C, Figures 8-12
  scope: MountainCar with linear approximation, gamma_E = 0 for the correlation histogram
    in Figure 12; Q and E were learned in parallel with actions chosen epsilon-greedily and
    independently of E to dissociate the two. E-value weights initialized to 0 with a logistic
    output non-linearity to keep E in (0,1).
- id: mountaincar-sparse-reward
  kind: result
  text: On sparse-reward MountainCar, LLL Softmax agents using E-values with gamma_E = 0.99
    quickly reach high probability of reaching the goal, while Softmax exploration fails to
    solve the problem within 1000 episodes.
  evidence: Appendix D and Figure 13
  scope: Reward 0 everywhere except magnitude 1 at the goal, episodes capped at 1000 steps,
    linear approximation with tile coding, temperature and epsilon fitted separately per agent,
    probability averaged over 50 simulations per agent.
- id: optimism-without-reward-priors
  kind: result
  text: Because DORA keeps exploratory value in a separate E-value function, it can use optimistic
    initialization for exploration without assuming known reward bounds, and still reaches
    convergence competitive with Delayed Q-Learning on the normalized bridge environment.
  evidence: Appendix B and Figure 7
  scope: Normalized bridge environment with k = 15 and rewards in [0,1]; MSE normalized separately
    per agent to make the curves comparable, and Delayed Q-Learning needed m = 10, an order
    of magnitude below the value its PAC guarantees require, to perform this well.
- id: no-extra-complexity
  kind: result
  text: Learning E-values leaves the asymptotic time and space complexity of the learning
    algorithm unchanged, since it amounts to running the same value-update twice, once for
    Q and once for E.
  evidence: Section 2.2
  scope: Tabular case with one E-value per state-action pair and alpha_E = alpha; in the function-approximation
    case E is a second learned value function whose parameter count is set by the chosen architecture.
qa:
- q:
  - How can a reinforcement learning agent explore based on how much new knowledge a whole
    trajectory would give, not just the next step?
  - Is there a model-free way to propagate exploration bonuses over trajectories?
  - What does DORA the Explorer propose for directed exploration?
  answers:
  - e-values-generalize-counters
  - log-e-is-a-counter
- q:
  - What should I read about directed exploration in model-free reinforcement learning?
  - Which paper introduced E-values as a generalization of visit counters?
  - Where does the idea of propagating exploration counters without a world model come from?
  answers:
  - e-values-generalize-counters
- q:
  - Why is the logarithm of an E-value called a generalized counter?
  - How does an E-value relate to the number of times a state-action pair was visited?
  - What does the exploration discount gamma_E change about counting visits?
  answers:
  - log-e-is-a-counter
- q:
  - Do propagating exploration counters actually beat plain visit counters?
  - Does using gamma_E greater than 0 help compared with ordinary counting?
  - How much does an E-value exploration bonus improve convergence on a bridge gridworld?
  answers:
  - bonus-beats-standard-counters
  - lll-outperforms-counters-and-stochastic
- q:
  - Which exploration methods were compared on the bridge MDP and which won?
  - Do epsilon-greedy and UCB converge on the long bridge environment?
  - What baselines does the E-value LLL agent beat in the tabular experiments?
  answers:
  - lll-outperforms-counters-and-stochastic
- q:
  - Is there evidence that generalized counters measure an agent's missing knowledge better
    than visit counts?
  - Why are visit counters a poor proxy for how well a state-action value has converged?
  - What does the relation between log E and |Q-Q*|/Q* look like?
  answers:
  - generalized-counters-track-missing-knowledge
- q:
  - How well do E-value exploration bonuses do on the Freeway Atari game?
  - Does DORA beat pseudo-count density models on hard-exploration Atari games?
  - How many steps does E-value exploration need to converge on Freeway?
  answers:
  - freeway-faster-convergence
  - freeway-beats-density-counters
- q:
  - Can a stochastic action-selection rule like epsilon-greedy be replaced by a deterministic
    counter-based rule?
  - What does the DORA determinization theorem guarantee about action frequencies?
  - Is the LLL action-selection rule equivalent to Softmax in the limit?
  answers:
  - determinization-theorem
- q:
  - Do E-values work with function approximation and continuous state spaces?
  - Can generalized visit counts be learned by a neural network or linear approximator instead
    of a lookup table?
  - How were E-values validated as visit counters on MountainCar?
  answers:
  - e-values-with-function-approximation
  - mountaincar-sparse-reward
- q:
  - Does DORA solve sparse-reward MountainCar where Softmax exploration fails?
  - What happens to Softmax exploration on sparse-reward MountainCar within 1000 episodes?
  answers:
  - mountaincar-sparse-reward
- q:
  - How does DORA compare to Delayed Q-Learning?
  - Can optimistic initialization be used for exploration without knowing the reward scale?
  - Why separate exploratory value from reward value instead of initializing Q optimistically?
  answers:
  - optimism-without-reward-priors
- q:
  - How expensive is it to learn E-values on top of Q-learning?
  - Does maintaining a second exploration value function double the asymptotic cost?
  answers:
  - no-extra-complexity
misreadings:
- 'E-values are not uncertainty estimates or a learned model of the environment: they are
  the action-values of a copy of the MDP in which all rewards are zero, so their only signal
  comes from optimistic initialization at 1 decaying with experience.'
- The E-value update deliberately uses SARSA rather than the max over next actions; taking
  the max would break the guarantee that exploration values decrease when the same trajectory
  is repeated.
- gamma_E = 0 does not disable exploration — it reduces the generalized counter to an ordinary
  visit counter, which is the baseline the propagating version is compared against.
- 'The Freeway comparison is not a matched ablation of the density-model counter method: the
  DQN baseline used lacks Double DQN and Monte-Carlo return, and the ~2x10^6 versus ~10x10^6
  step figure compares against numbers reported in the density-model paper.'
- The Atari result is a single hard-exploration game (Freeway), not a claim of state-of-the-art
  across the Atari suite.
- The determinization theorem guarantees only that action frequencies match the stochastic
  rule asymptotically; it does not by itself prove that the deterministic variant learns faster,
  which is an empirical finding.
terminology: '{"E-value", "The action-value learned in a copy of an MDP where every reward
  is identically zero, initialized to 1 and discounted by an exploration discount gamma_E,
  so its decay measures how much of a state-action''s potential outcome space has already
  been experienced.", "generalized counter", "The logarithm, base (1-alpha), of an E-value;
  it equals the ordinary visit count when the exploration discount is 0 and grows more slowly
  when exploratory value propagates from future states.", "LLL determinization", "A deterministic
  action-selection rule that picks argmax over actions of log f(s,a) minus log log_(1-alpha)E(s,a),
  the counter-based deterministic equivalent of a stochastic rule f with generalized counters
  substituted for visit counters.", "exploration discount (gamma_E)", "The discount factor
  of the reward-free parallel MDP, controlling how far exploratory value propagates backwards
  along trajectories; 0 recovers local visit counting.", "DORA", "Directed Outreaching Reinforcement
  Action-Selection: turning any stochastic or counter-based action-selection rule into a deterministic
  rule driven by generalized counters derived from E-values."}'
links_extra:
  OpenReview: https://openreview.net/forum?id=ry1arUgCW
  code: https://github.com/borgr/DORA
  replication study fork: https://github.com/borgr/deep_exploration_with_E_network/tree/2349bc9027fee67cf59914476e62f20398a43ddd
---
