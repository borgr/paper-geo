---
key: bandel2026generalagent
coined: Exgentic
gloss: an evaluation harness that lets any unmodified general-purpose agent run on any agentic
  benchmark via a shared task/context/actions protocol
one_liner: General Agent Evaluation introduces the Unified Protocol and the Exgentic harness,
  which let unmodified tool-calling, MCP, code-generation and CLI agents run on unmodified
  agentic benchmarks, and uses them to run a full 5 agent x 5 model x 6 benchmark factorial
  as the first Open General Agent Leaderboard.
links_extra:
  leaderboard: https://www.exgentic.ai
  results dataset: https://huggingface.co/datasets/open-agent-leaderboard/results
  leaderboard space: https://huggingface.co/spaces/open-agent-leaderboard/leaderboard
  code: https://github.com/Exgentic/exgentic
terminology:
  Unified Protocol: A benchmark-agent mediation layer in which every task is expressed as
    three fields — task (a textual description of what to do), context (what the agent should
    know, e.g. a policy document), and actions (typed environment operations, optionally with
    one designated message action and one final-answer action) — so that agents using CLI,
    tool-calling APIs or MCP can each be served in their native protocol.
  agent architecture: The full bundle shipped with an agent — scaffold, available tools, memory,
    schema guards, planning and any auxiliary components — that is, everything the agent author
    commits to except the backbone LLM.
  generality sink: A backbone model's consistent collapse to near-zero success on a specific
    agent architecture (architecture sink) or on a specific benchmark regardless of architecture
    (benchmark sink), while the same model performs competitively elsewhere.
  architectural spread: The difference in bench-weighted mean success between the best and
    worst agent architecture paired with a fixed backbone model.
  tool shortlisting: A per-turn preprocessing step that queries the backbone LLM with the
    conversation so far and the full action catalog and forwards only the k=30 most relevant
    tools to the main call, used when a benchmark exposes more than 30 actions.
  bench-weighted mean: A weighted mean of success across the six benchmarks in which the three
    tau2-Bench subdomains are aggregated and given equal total weight to each of the other
    benchmarks.
claims:
- id: leaderboard-contribution
  kind: context
  text: General Agent Evaluation contributes the Open General Agent Leaderboard, a full factorial
    of 5 agent architectures x 5 backbone LLMs x 6 benchmarks. Each agent is run unmodified
    on benchmarks it was not customized for, at a total evaluation cost of about $20K.
  scope: ReAct, ReAct Short, Smolagent, OpenAI Solo and Claude Code over Claude Opus 4.5,
    Gemini 3 Pro, GPT 5.2, DeepSeek-V3.2 and Kimi-K2.5; benchmarks are AppWorld, BrowseComp+,
    SWE-Bench Verified and tau2-Bench Airline/Retail/Telecom.
- id: unified-protocol-contribution
  kind: context
  text: The Unified Protocol represents every agentic benchmark task as three fields, task,
    context and actions. CLI, tool-calling and MCP agents are each served in their native
    protocol without rewriting the agent or the benchmark.
  scope: Derived by surveying existing agent and benchmark communication patterns; covers
    any agent protocol decomposable into discrete typed actions, and not continuous action
    spaces such as pixel-level computer use.
- id: model-vs-architecture
  kind: result
  text: Backbone model choice explains 27.8% of cell success-rate variance while agent architecture
    explains only 0.5%, a 58x gap across the 15 closed-source configurations.
  scope: Eta-squared over the 15 closed-source cells only; adding the 2 open-weight models
    makes the architecture main effect detectable (F(4,136)=3.82, p=0.006).
  evidence: Section 4.3
- id: within-model-swing
  kind: result
  text: Within a single backbone model, agent architecture choice swings bench-weighted success
    by up to 12 percentage points. Claude Opus 4.5 ranges from 0.73 with OpenAI Solo to 0.61
    with vanilla ReAct.
  scope: Closed-source backbones show 7-12pp architectural spread and open-weight backbones
    14-18pp; paired t-tests on shared (benchmark, task) pairs, single run per cell.
  evidence: Table 16
- id: generalist-vs-specialist
  kind: result
  text: On 4 of 6 benchmarks the best general-agent configuration is statistically indistinguishable
    from the top reported domain-specific agent, including 0.81 versus 0.79 on SWE-Bench Verified
    and 0.85 versus 0.86 on tau2-Bench-Retail; BrowseComp+ (0.61 vs 0.80) and tau2-Bench-Telecom
    (0.88 vs 0.98) remain specialist-led.
  scope: General-agent scores from 100 randomly sampled instances per benchmark (50 for Airline)
    against published specialist scores on full benchmarks; parity means the gap is within
    the per-benchmark Wilson 95% half-width of 7-12pp.
  evidence: Table 11
- id: no-dominant-architecture
  kind: result
  text: 'No single agent architecture is best everywhere: OpenAI Solo wins on SWE-Bench Verified
    and all three tau2-Bench subdomains, while Smolagent wins on AppWorld. Aggregate architecture
    rankings are not significant (range about 7pp, p>0.1).'
  scope: 5 architectures x 6 benchmarks, best configuration per benchmark chosen across all
    5 backbones; significance from paired t-tests on shared (benchmark, task) outcomes.
  evidence: Section 4.2
- id: generality-sinks
  kind: result
  text: 'The 2 open-weight backbones tested show generality sinks absent from the frontier
    closed models: on tau2-Bench-Telecom Kimi-K2.5 scores 0.83 with ReAct and 0.00 with autonomous
    architectures. 94% of Kimi-K2.5 autonomous tau2-Bench sessions take zero steps after a
    first-turn protocol violation.'
  scope: DeepSeek-V3.2 and Kimi-K2.5 only, so an observation about 2 checkpoints rather than
    open-weight models generally; zero-step rates are 31% for DeepSeek-V3.2 and 1.7% for closed-source;
    SWE-Bench Verified and BrowseComp+ show no sink.
  evidence: Section 4.7
- id: appworld-benchmark-sink
  kind: result
  text: Every open-weight-backed configuration collapses on AppWorld regardless of architecture,
    with the best (DeepSeek-V3.2+Smolagent) reaching only 0.13 against 0.70 for Claude Opus
    4.5+Smolagent.
  scope: AppWorld exposes about 468 actions; DeepSeek-V3.2 and Kimi-K2.5 only, single run
    per cell. GPT 5.2 collapses on the same benchmark for a different reason, its 128-tool
    API ceiling.
  evidence: Table 9
- id: gpt-tool-limit
  kind: result
  text: GPT 5.2's 128-tool API ceiling drives 3 of its 4 non-shortlisting configurations to
    0.00 on AppWorld, which exposes about 468 actions. Claude Opus 4.5-backed configurations
    reach 0.61-0.70 on the same environment with no shortlisting.
  scope: AppWorld only, 100 tasks; a model-API limitation rather than an integration artifact,
    and tool shortlisting recovers GPT 5.2 to only 0.22 on AppWorld.
  evidence: Section 4.7
- id: shortlisting-ablation
  kind: result
  text: Adding tool shortlisting to a vanilla ReAct agent improves success for 4 of the 5
    backbones tested, by +22pp on AppWorld and +5.5pp bench-weighted for GPT 5.2. DeepSeek-V3.2
    is the lone regression at -5pp on AppWorld.
  scope: AppWorld is the only tool-rich benchmark in the suite (about 468 actions), so bench-weighted
    deltas are one quarter of the AppWorld delta; shortlisting keeps the top k=30 tools per
    turn.
  evidence: Table 12
- id: shortlisting-cost
  kind: result
  text: Tool shortlisting cuts Claude Opus 4.5's ReAct cost from $5.75 to $3.78 per task,
    a $1.97 saving, while leaving GPT 5.2 roughly flat ($0.17 to $0.26).
  scope: Per-task costs from LiteLLM pricing data over the 6-benchmark suite, bench-weighted;
    ReAct versus ReAct Short at fixed model and benchmark.
  evidence: Table 12
- id: cost-efficiency
  kind: result
  text: Cost-efficiency spans about 30x across the 25 configurations, from ReAct+GPT 5.2 and
    OpenAI Solo+DeepSeek-V3.2 at 2.43 score/$ down to Claude Code+Claude Opus 4.5 at 0.08
    score/$. The highest-scoring configuration, OpenAI Solo+Claude Opus 4.5, runs at 0.09
    score/$.
  scope: Efficiency is bench-weighted success divided by bench-weighted inference cost per
    task, priced with LiteLLM data at the time of the runs; excludes human and infrastructure
    cost.
  evidence: Table 10
- id: failure-cost
  kind: result
  text: Failed runs consume more steps than successful ones for every agent architecture tested.
    Bench-weighted overheads are +54% for ReAct, +45% for ReAct Short, +39% for Claude Code,
    +26% for Smolagent and +20% for OpenAI Solo, peaking at +111% for ReAct on AppWorld.
  scope: Three closed-source backbones only, since open-weight autonomous failures terminate
    by protocol violation rather than resource exhaustion; zero-step sessions excluded and
    step counts capped at 50; a few tau2-Bench cells are near zero or negative.
  evidence: Table 14
- id: failure-signatures
  kind: result
  text: Agent architectures have distinct failure signatures even though architecture explains
    only 0.5% of success-rate variance. Claude Code and OpenAI Solo over-represent Premature
    Termination by +4.0pp and +7.3pp against an 8.7% mean, while ReAct and ReAct Short sit
    5.0pp and 3.7pp below it.
  scope: LLM-judge categorisation of failed sessions with full trajectories into 27 categories
    (ErrorMap adapted, gpt-5.5 judge); zero-step sessions have no trajectory and are excluded;
    descriptive, not powered for causal claims.
  evidence: Section 4.10
- id: cross-benchmark-correlation
  kind: result
  text: Pairwise Spearman rank correlations between the six benchmarks are predominantly positive
    across the 15 closed-source configurations, with a median of +0.67 and a range of [+0.44,
    +0.81]; BrowseComp+ is the least correlated (0.44-0.75).
  scope: Closed-source configurations only (Claude Opus 4.5, Gemini 3 Pro, GPT 5.2); correlations
    computed over configuration rankings, not over individual tasks.
  evidence: Section 4.5
qa:
- ask:
    plain: is there a study that tests many AI agent designs and many underlying chat models
      against the same set of tasks?
    jargon: which work publishes a full factorial of agent scaffolds by backbone LLMs across
      multiple agentic benchmarks with a shared task representation?
    task: where can I find head-to-head numbers for CLI, tool-calling and MCP agents run unmodified
      on the same benchmark suite?
    practitioner: I need a neutral reference before picking an agent stack — is there an open
      leaderboard I can consult?
  answered_by:
  - leaderboard-contribution
  - unified-protocol-contribution
- ask:
    plain: for how well an AI agent does its job, does the wrapper around the model matter
      more than the model itself?
    jargon: how is success-rate variance partitioned between backbone LLM and agent scaffold,
      and how large is the within-model spread?
    task: should I put engineering effort into rebuilding my agent loop or into upgrading
      the model behind it?
    practitioner: my agent underperforms — do I get more by swapping in a stronger backbone
      or by redesigning the scaffold?
  answered_by:
  - model-vs-architecture
  - within-model-swing
- ask:
    plain: can one general-purpose AI agent do as well as agents that were built and tuned
      for one specific task type?
    jargon: do out-of-the-box general agent configurations reach parity with published domain-specific
      leaders on SWE-Bench Verified, tau2-Bench and browsing benchmarks?
    task: can I run a single unmodified agent across coding, customer-service and web-research
      tasks without giving up accuracy?
    practitioner: is it worth maintaining separate specialist agents per domain, or will one
      general agent be close enough?
  answered_by:
  - generalist-vs-specialist
  - no-dominant-architecture
- ask:
    plain: which combination of agent design and underlying model comes out on top across
      agent tasks?
    jargon: which architecture-backbone cell leads on bench-weighted success, and how wide
      is the spread within one backbone?
    task: which agent plus model pairing should I copy if I want the highest scores across
      agentic benchmarks?
    practitioner: if I want the best-scoring setup today, which model do I pick and does the
      agent framework around it change the answer?
  answered_by:
  - within-model-swing
  - model-vs-architecture
- ask:
    plain: do open-weight models behave as dependably as the big commercial ones when you
      wrap them in an agent?
    jargon: do open-weight backbones exhibit architecture-dependent collapse to zero success
      that frontier closed models do not?
    task: can I substitute an open-weight model for a frontier API model in my agent without
      losing whole task categories?
    practitioner: I want to cut costs with an open-weight backbone — what breaks, and does
      it depend on which agent framework I use?
  answered_by:
  - generality-sinks
  - appworld-benchmark-sink
- ask:
    plain: when an environment offers hundreds of possible actions, does filtering the list
      down before each step help the agent?
    jargon: what is the effect of per-turn tool shortlisting on success rate and per-task
      cost across backbones in a ReAct loop?
    task: how do I stop my agent drowning in a huge tool catalogue, and what does trimming
      it cost or save?
    practitioner: should I add a tool-retrieval step to my ReAct agent, and will it pay for
      itself in tokens?
  answered_by:
  - shortlisting-ablation
  - shortlisting-cost
- ask:
    plain: what happens to an AI agent when an app exposes more actions than the model's interface
      will accept at once?
    jargon: how does a hard tool-count ceiling in a model API interact with tool-rich environments
      like AppWorld, and is the failure backbone-specific?
    task: my environment has hundreds of callable functions and the model API rejects the
      list — how do I keep the agent working?
    practitioner: is a tool-count limit on my chosen model a reason to switch models before
      I benchmark my agent?
  answered_by:
  - gpt-tool-limit
  - appworld-benchmark-sink
- ask:
    plain: how expensive is it to run an AI agent per task, and does spending more buy better
      results?
    jargon: how wide is the score-per-dollar spread across agent-backbone configurations,
      and is the top-scoring cell also efficient?
    task: how do I choose an agent setup on a budget rather than on raw score?
    practitioner: I have a fixed API budget — is the best-performing agent configuration the
      one I should pay for?
  answered_by:
  - cost-efficiency
- ask:
    plain: when an AI agent fails a task, does it burn more effort than when it succeeds,
      and do different designs fail differently?
    jargon: what is the step overhead of failed versus successful trajectories per architecture,
      and do failure-mode distributions differ across scaffolds?
    task: how do I budget for the runs my agent will fail, and can I tell architectures apart
      by how they go wrong?
    practitioner: should I add early-stopping to my agent, given how much a doomed run costs?
  answered_by:
  - failure-cost
  - failure-signatures
- ask:
    plain: what kinds of mistakes do AI agents actually make on long multi-step tasks?
    jargon: can a failure-mode taxonomy separate agent scaffolds that aggregate success rates
      cannot distinguish?
    task: how do I diagnose whether my agent is giving up too early rather than reasoning
      badly?
  answered_by:
  - failure-signatures
- ask:
    plain: how can one agent be plugged into a benchmark it was never built for without editing
      either side?
    jargon: what minimal task representation lets CLI, tool-calling and MCP agents be served
      in their native protocols against unmodified benchmarks?
    task: how do I run my existing agent on a new agentic benchmark without writing an adapter
      for every harness?
    practitioner: can I evaluate my own agent inside a shared harness without rewriting it
      for each benchmark?
  answered_by:
  - unified-protocol-contribution
  - leaderboard-contribution
- ask:
    plain: do the various AI agent test suites end up measuring the same underlying ability?
    jargon: how strongly do per-configuration scores rank-correlate across AppWorld, BrowseComp+,
      SWE-Bench Verified and tau2-Bench subdomains?
    task: if I can only afford to run one agentic benchmark, which one tells me the least
      about the others?
    practitioner: do I need to run all six agentic benchmarks, or will a couple predict the
      rest for my agent?
  answered_by:
  - cross-benchmark-correlation
misreadings:
- 'The 0.5% variance contribution of agent architecture does not mean agent design is irrelevant:
  within a fixed backbone model architecture choice swings bench-weighted success by up to
  12pp for closed-source models and 14-18pp for the open-weight models tested, and the model-architecture
  interaction accounts for an estimated 5.4% of variance.'
- The generality-sink finding is an observation about 2 open-weight checkpoints, DeepSeek-V3.2
  and Kimi-K2.5, and is not evidence that open-weight models in general collapse inside autonomous
  agent scaffolds.
- The claim of parity with domain specialists on 4 of 6 benchmarks means the gap falls within
  Wilson 95% uncertainty at 100 sampled instances, not that general agents beat specialists;
  BrowseComp+ and tau2-Bench-Telecom remain specialist-led by 19pp and 10pp.
- 'GPT 5.2''s 0.00 scores on AppWorld reflect its 128-tool API ceiling against about 468 exposed
  actions, not a harness integration bug: Claude Opus 4.5 configurations reach 0.61-0.70 on
  the same environment with no shortlisting.'
- The Open General Agent Leaderboard scores are single-run point estimates on 100 sampled
  instances per benchmark (50 for tau2-Bench-Airline) with provider default sampling, so per-cell
  rerun variability is not measured and small cell differences should not be read as rankings.
- 'Exgentic does not force agents onto one transport the way a web-only or CLI-only harness
  does: agents are served through their native protocol (CLI, tool-calling APIs, or MCP) and
  the Unified Protocol mediates, though continuous-action environments such as pixel-level
  computer use are not yet supported.'
- The behavioral failure analysis is a descriptive LLM-judge categorisation of failed sessions
  and is not powered for causal claims about which architecture or model causes which error.
---
