<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced) + a targeted repair. Every claim, number
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

Stamp: spec=8f05813a4658 checks=pass body=57be73a43b61
-->
---
key: DBLP:conf/iclr/FoxCL18
coined: DORA / E-values
gloss: exploration values that propagate "missing knowledge" along trajectories, so a model-free
  agent can prefer actions that lead toward unexplored regions rather than just unvisited
  single steps
one_liner: DORA learns a second value function, E-values, on a copy of the MDP with all rewards
  set to zero and values initialized to 1, so that the logarithm of E acts as a visit counter
  that propagates exploratory value along whole trajectories in model-free RL.
claims:
- id: e-values-generalize-counters
  kind: context
  text: DORA introduces E-values, a model-free generalization of visit counters that requires
    no learned model of the MDP. The generalized counter log_{1-alpha}(E) propagates exploratory
    value along state-action trajectories instead of scoring only the immediate next step.
  scope: Earlier propagating-exploration schemes (Storck et al. 1995, Meuleau & Bourgine 1999,
    Little & Sommer 2014) were model-based; as of ICLR 2018. Requires running a second value-learning
    process beside Q-learning.
- id: log-e-equals-counter
  kind: result
  text: With exploration discount gamma_E = 0, an E-value initialized to 1 becomes (1-alpha)^n
    after n visits, so log_{1-alpha}(E) equals the visit counter exactly; for gamma_E > 0
    it grows more slowly and behaves as a generalized counter.
  evidence: Section 2.3 and Figure 1
  scope: Exact equality holds for gamma_E = 0, and for any gamma_E at a terminal state with
    one action. On the tree MDP with k leaves, one full cycle of k visits of the start action
    contributes roughly 1 generalized visit.
- id: bonus-bridge
  kind: result
  text: Adding an exploration bonus of 1/log_{1-alpha}(E) to the reward speeds up convergence
    of an epsilon-greedy agent on the bridge MDP. Larger exploration discounts learn faster,
    with gamma_E = 0.9 beating gamma_E = 0, which is equivalent to standard visit counters.
  evidence: Figure 3
  scope: Short bridge environment with k = 5, tabular Q-learning, epsilon fitted separately
    per agent; convergence measured as MSE between Q and Q* averaged over the optimal-policy
    state-action distribution.
- id: bridge-outperforms
  kind: result
  text: On the long bridge environment with k = 15, E-value LLL agents are the first to reach
    low Q-versus-Q* error. Stochastic and counter-based epsilon-greedy agents and the standard
    UCB-like agent fail to converge at all.
  evidence: Figure 4
  scope: Tabular bridge MDP, k = 15, gamma_E = 0.9, epsilon and Softmax temperature fitted
    per agent, stochastic agents averaged over 50 trials. Cliff gridworld results reported
    but not shown.
- id: missing-knowledge
  kind: result
  text: Generalized counters track an agent's missing knowledge better than visit counters
    on the bridge MDP. The normalized distance |(Q-Q*)/Q*| is a single function of log_{1-alpha}(E)
    across all state-action pairs, whereas against the visit counter it depends on which state-action
    is counted.
  evidence: Figure 5
  scope: Measured for an E-value LLL Softmax agent on the short bridge environment with k
    = 5, recording C, log_{1-alpha}(E) and the normalized error at the end of each episode.
- id: freeway
  kind: result
  text: On the Freeway Atari 2600 game, E-value exploration bonuses beat both a DQN baseline
    and the density-model counters of Bellemare et al. (2016). Learning converges in approximately
    2*10^6 steps instead of approximately 10*10^6 steps.
  evidence: Section 4.1 and Figure 6
  scope: Single game (Freeway), beta = 0.05, epsilon-greedy action selection in all conditions.
    The DQN baseline lacks Double DQN and Monte-Carlo return, which the 10*10^6-step Bellemare
    et al. result did use.
- id: training-speed
  kind: result
  text: Training the two-stream network for E-values on Freeway was an order of magnitude
    faster than training with density-model counters.
  evidence: Section 4.1, footnote 2
  scope: Wall-clock comparison for one implementation pair on Freeway, using the atari-rl
    package for both DQN and density-model counters.
- id: determinization-theorem
  kind: result
  text: For any stochastic action-selection rule f, a deterministic policy can match f's action
    frequencies in the limit. It suffices that the chosen action's empirical frequency C_T(a)/T
    exceed f(a) by at most a sub-linear b(t).
  evidence: Theorem 3.1, proved in Appendix A
  scope: An in-the-limit statement about action frequencies at fixed Q-values and fixed state,
    not a finite-time or regret bound. Two concrete determinizations are given, including
    the LLL rule argmax_a f(a)/C(a).
- id: lll-rule
  kind: context
  text: DORA turns any stochastic action-selection rule, such as epsilon-greedy or Softmax,
    into a deterministic rule by replacing visit counters with generalized counters, selecting
    argmax over log f(s,a) - log log_{1-alpha}(E(s,a)).
  scope: Rules whose target action frequencies can be written as a distribution over actions
    given the current Q-values; requires initializing E to 1 and 0 <= gamma_E < 1 so that
    E stays in (0,1).
- id: function-approximation
  kind: result
  text: E-values learned by linear function approximation with tile coding on MountainCar
    correlate strongly, per state, with empirical visit histograms throughout training. The
    E-value model uses far fewer parameters than a state-action count table at the same binning
    resolution.
  evidence: Appendix C, Figures 8-12
  scope: gamma_E = 0 for the correlation histogram, snapshots each 10 episodes; actions chosen
    by an epsilon-greedy agent independently of E-values to dissociate visits from the exploration
    bonus.
- id: mountaincar-sparse
  kind: result
  text: On sparse-reward MountainCar, LLL E-value agents with gamma_E = 0.99 quickly reach
    high goal-reaching probability, while Softmax exploration fails to solve the problem within
    1000 episodes.
  evidence: Appendix D and Figure 13
  scope: Reward 0 except 1 at the goal, episodes capped at 1000 steps, linear tile-coding
    approximation, probability averaged over 50 simulations per agent, temperature and epsilon
    fitted per agent.
- id: delayed-q
  kind: result
  text: E-value LLL is competitive with Delayed Q-Learning on the normalized bridge environment
    with k = 15. That comparison required hand-setting Delayed Q-Learning's update threshold
    to m = 10, an order of magnitude below the value its PAC guarantees require.
  evidence: Appendix B and Figure 7
  scope: MSE normalized separately per agent because Delayed Q-Learning initializes optimistically.
    Delayed Q-Learning also assumes all rewards lie between 0 and 1, which the normalized
    bridge environment provides.
qa:
- q:
  - How can a model-free RL agent explore toward unvisited regions rather than just unvisited
    single steps?
  - Is there a way to make visit counters propagate along trajectories without learning a
    model of the MDP?
  - What does DORA's E-value do that a visit counter does not?
  answers:
  - e-values-generalize-counters
  - log-e-equals-counter
- q:
  - What should I read first about directed exploration in reinforcement learning?
  - Which paper introduced propagating exploration values for model-free RL?
  - Where does the idea of generalized visit counters for exploration come from?
  answers:
  - e-values-generalize-counters
  - lll-rule
- q:
  - Why is the logarithm of the E-value called a generalized counter?
  - What is the relationship between E-values and the number of visits to a state-action pair?
  - Does log of E reduce to an ordinary visit count in any special case?
  answers:
  - log-e-equals-counter
  - missing-knowledge
- q:
  - Do E-values actually beat ordinary visit counters as an exploration bonus?
  - Does the exploration discount factor gamma_E matter for learning speed?
  - How much does adding an E-value bonus to the reward help on a bridge gridworld?
  answers:
  - bonus-bridge
  - bridge-outperforms
- q:
  - How does DORA compare with epsilon-greedy, Softmax and UCB on tabular gridworlds?
  - Which exploration methods fail to converge on the long bridge environment?
  - Are counter-based exploration bonuses enough on a hard tabular exploration task?
  answers:
  - bridge-outperforms
  - bonus-bridge
- q:
  - Is there evidence that generalized counters measure how much an agent still has to learn?
  - What quantity predicts convergence of Q to Q* better than visit counts?
  - Do visit counters capture missing knowledge in RL?
  answers:
  - missing-knowledge
- q:
  - How well does E-value exploration do on the Freeway Atari game?
  - Does DORA beat pseudo-count density models on hard-exploration Atari games?
  - How many steps does an E-value DQN agent need to converge on Freeway?
  answers:
  - freeway
  - training-speed
- q:
  - Is E-value exploration cheaper to train than density-model pseudo-counts?
  - What is the computational overhead of learning E-values alongside Q-values?
  answers:
  - training-speed
  - freeway
- q:
  - Can a stochastic exploration rule like Softmax be replaced by a deterministic one with
    the same action frequencies?
  - Is there a theorem about determinizing epsilon-greedy or Boltzmann action selection?
  - What guarantee does the LLL determinization of a stochastic policy come with?
  answers:
  - determinization-theorem
  - lll-rule
- q:
  - How do I convert an existing exploration rule into an E-value based one?
  - What action-selection rule does DORA use in practice?
  - Can generalized counters be dropped into a counter-based action-selection rule?
  answers:
  - lll-rule
  - determinization-theorem
- q:
  - Do E-values work with function approximation and continuous state spaces?
  - Can generalized counters be estimated in a continuous MDP where states are never revisited?
  - How were E-values validated against real visit histograms on MountainCar?
  answers:
  - function-approximation
  - mountaincar-sparse
- q:
  - Does directed exploration help on sparse-reward MountainCar?
  - Which exploration method solves MountainCar when the reward is only given at the goal?
  - How does Softmax exploration do on sparse-reward MountainCar?
  answers:
  - mountaincar-sparse
  - function-approximation
- q:
  - How does DORA compare with Delayed Q-Learning and other PAC-MDP methods?
  - Is a PAC-MDP exploration algorithm better than E-value exploration on the bridge task?
  - Does E-value exploration need optimistic initialization of the reward values?
  answers:
  - delayed-q
  - e-values-generalize-counters
misreadings:
- 'E-values are not uncertainty estimates or a Bayesian posterior: they are the action-values
  of a copy of the MDP whose rewards are identically zero, initialized to 1, so their decay
  measures how thoroughly trajectories have been exhausted rather than variance in the reward.'
- 'The Freeway comparison is not a like-for-like ablation of Bellemare et al. (2016): the
  DQN baseline in the paper omits Double DQN and Monte-Carlo return, and the roughly 2*10^6
  versus 10*10^6 step figure compares against that published result rather than a matched
  re-run.'
- gamma_E is not the ordinary discount factor gamma of the task. Setting gamma_E = 0 removes
  propagation entirely and recovers standard visit counters, which is the baseline DORA is
  compared against.
- E-values are learned by SARSA rather than by max-based Q-learning updates; using max over
  next actions would break the guarantee that exploration values decrease when a trajectory
  is repeated.
- The determinization result is an asymptotic statement about matching action frequencies
  in the limit, not a sample-complexity or PAC-MDP guarantee for DORA.
- DORA's tabular results are on small gridworlds -- bridge environments with k = 5 and k =
  15 and the Cliff problem -- so they demonstrate faster convergence in these settings, not
  across a broad benchmark suite.
terminology:
  E-values: action-values learned on a copy of the MDP in which all rewards are identically
    zero and the discount is gamma_E, initialized to 1 so that positive initial conditions
    create an optimistic bias; they decay toward 0 as trajectories are repeated
  generalized counter: log_{1-alpha}(E(s,a)), which equals the number of visits when the exploration
    discount is 0 and grows more slowly when it is positive, so state-actions leading to many
    potential outcomes accumulate less credit per visit
  LLL determinization: a deterministic action-selection rule that reproduces a stochastic
    rule f in the limit by choosing argmax over log f(s,a) minus log log_{1-alpha}(E(s,a)),
    the counter-based version being argmax of f(a)/C(a)
  exploration discount factor gamma_E: the discount used when learning exploration values,
    separate from the task's reward discount; 0 gives no propagation between states and values
    approaching 1 give long-range propagation of exploratory value
  bridge MDP: a gridworld of length k in which the optimal policy requires crossing a bridge
    whose off-bridge actions are penalized, used as a hard directed-exploration test for tabular
    agents
links_extra:
  code: https://github.com/borgr/DORA
  openreview: https://openreview.net/forum?id=ry1arUgCW
  replication_study_fork: https://github.com/borgr/deep_exploration_with_E_network/tree/2349bc9027fee67cf59914476e62f20398a43ddd
  atari_implementation_fork: https://github.com/borgr/atari-rl/tree/53f0d898585de042e38d6eead81ea10ad0677750
---
