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
- ask:
    plain: how can a reinforcement learning agent be pushed toward whole unexplored regions
      instead of just the next unseen step?
    jargon: can visit-count exploration bonuses be propagated along state-action trajectories
      in a model-free setting without learning the MDP transition model?
    task: how do I get my exploration bonus to look several steps ahead when I have no environment
      model to plan with?
    practitioner: my agent keeps re-exploring dead ends one step at a time -- is there a counter-style
      bonus that accounts for what lies beyond a state?
  answered_by:
  - e-values-generalize-counters
  - log-e-equals-counter
- ask:
    plain: which research introduced spreading exploration value backwards through states
      instead of counting single visits?
    jargon: what work proposed generalized visit counters propagated by a Bellman-style update
      for directed exploration in model-free RL?
    practitioner: if I want to read up on propagating exploration values for model-free agents,
      which paper should I start with?
  answered_by:
  - e-values-generalize-counters
  - lll-rule
- ask:
    plain: how does an exploration value that decays with each visit relate to simply counting
      how many times a state was tried?
    jargon: under what setting of the exploration discount does log_{1-alpha}(E) coincide
      exactly with the tabular state-action visit count?
    task: how do I check that a decaying exploration value I am learning really behaves like
      a visit count before trusting it?
    practitioner: if I replace my visit-count table with a learned exploration value, will
      the numbers still mean the same thing?
  answered_by:
  - log-e-equals-counter
  - missing-knowledge
- ask:
    plain: does a bonus built from a propagated exploration value beat plain visit counts
      on a small gridworld with a long corridor?
    jargon: how does the exploration discount gamma_E affect convergence speed of an epsilon-greedy
      agent with a 1/log_{1-alpha}(E) reward bonus on the bridge MDP?
    task: how do I pick the discount for a propagating exploration bonus so a corridor-style
      task is learned faster?
    practitioner: is it worth switching my count-based exploration bonus for a trajectory-propagated
      one on a hard corridor task?
  answered_by:
  - bonus-bridge
  - bridge-outperforms
- ask:
    plain: which exploration strategies fail on a gridworld where the agent must cross a long
      risky corridor to find reward?
    jargon: how do E-value-driven agents compare against stochastic epsilon-greedy, counter-based
      epsilon-greedy and UCB-like agents in Q-versus-Q* error on the long bridge environment?
    task: how do I get an agent through a long bridge gridworld when random and count-bonus
      exploration never converge?
    practitioner: my tabular agent with epsilon-greedy or UCB never solves a long-corridor
      task -- what else should I try?
  answered_by:
  - bridge-outperforms
  - bonus-bridge
- ask:
    plain: what number tells you how much an agent still has left to learn about a state,
      better than the number of times it visited it?
    jargon: is there evidence that generalized counters track missing knowledge, in the sense
      of predicting normalized |(Q-Q*)/Q*| uniformly across state-action pairs?
    task: how do I measure how far my agent's Q-values still are from optimal without knowing
      Q*?
    practitioner: can I use visit counts as a proxy for how well my agent knows a state, or
      is there something better?
  answered_by:
  - missing-knowledge
- ask:
    plain: does the propagated exploration bonus help on an Atari game where reward is rare,
      and how quickly does it learn?
    jargon: how does E-value exploration compare with a DQN baseline and density-model pseudo-counts
      in convergence steps on Freeway?
    task: how do I speed up convergence of a deep Q agent on a sparse-reward Atari game like
      Freeway?
    practitioner: should I use E-value bonuses instead of pseudo-count intrinsic rewards for
      my deep RL agent on hard-exploration games?
  answered_by:
  - freeway
  - training-speed
- ask:
    plain: how expensive is it to learn a decaying exploration value alongside the value function
      compared with fitting a density model over frames?
    jargon: what is the training-time overhead of a two-stream E-value network relative to
      density-model pseudo-counts on Atari?
    task: how do I add an intrinsic exploration signal to a deep Q agent without paying the
      training cost of a density model over pixels?
    practitioner: I cannot afford to train a pixel density model for pseudo-counts -- is a
      learned exploration value cheaper?
  answered_by:
  - training-speed
  - freeway
- ask:
    plain: can a randomized way of picking actions be replaced by a deterministic one that
      still tries actions at the same rates?
    jargon: is there a theorem that a deterministic action-selection rule can match the limiting
      action frequencies of a stochastic rule such as epsilon-greedy or Softmax?
    task: how do I make my agent's exploration reproducible and deterministic without changing
      how often each action gets tried?
    practitioner: can I drop the random number generator out of my Softmax exploration and
      still get the same coverage of actions?
  answered_by:
  - determinization-theorem
  - lll-rule
- ask:
    plain: how does an agent actually choose its action once it has a propagated exploration
      value instead of a visit count?
    jargon: how are generalized counters substituted into a counter-based action-selection
      rule to give a deterministic argmax over log f(s,a) minus log log_{1-alpha}(E(s,a))?
    task: how do I plug a learned exploration value into the exploration rule I already use
      in place of the visit count?
    practitioner: I already use a count-based action-selection rule -- can I swap in a propagated
      exploration value without redesigning it?
  answered_by:
  - lll-rule
  - determinization-theorem
- ask:
    plain: can you estimate how much a state has been explored in a continuous problem where
      the exact same state is never seen twice?
    jargon: do E-values learned by linear function approximation with tile coding on MountainCar
      correlate with empirical visit histograms, and at what parameter cost versus a state-action
      count table?
    task: how do I get count-like exploration signals in a continuous state space where tabular
      counters are useless?
    practitioner: my state space is continuous so visit counts are all zero or one -- can
      a learned exploration value give me something usable?
  answered_by:
  - function-approximation
  - mountaincar-sparse
- ask:
    plain: what exploration method gets a car up a hill when reward only arrives at the goal
      and nowhere else?
    jargon: how do LLL E-value agents with gamma_E = 0.99 compare with Softmax exploration
      on goal-reaching probability in sparse-reward MountainCar?
    task: how do I get an agent to solve a sparse-reward continuous control task where Boltzmann
      exploration stalls?
    practitioner: my agent never finds the goal in a sparse-reward continuous task with Softmax
      exploration -- would directed exploration fix it?
  answered_by:
  - mountaincar-sparse
  - function-approximation
- ask:
    plain: how does an exploration-value agent stack up against methods that come with formal
      sample-complexity guarantees?
    jargon: how does E-value LLL compare with Delayed Q-Learning on the normalized bridge
      environment, and what update threshold m did that comparison require?
    task: how do I choose between a PAC-MDP exploration algorithm and a generalized-counter
      agent for a hard tabular task?
    practitioner: should I use Delayed Q-Learning with its theoretical guarantees, or an exploration-value
      agent, on a long-corridor gridworld?
  answered_by:
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
