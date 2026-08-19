<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced via a forced tool call) + 2 repair rounds. Every claim, number
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

Then promote it:  python scripts/draft_sidecars.py --accept general-agent-evaluation

Stamp: spec=8f05813a4658 checks=pass body=b0e9110d9db5
-->
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
- q:
  - What should I read about evaluating general-purpose AI agents across many benchmarks?
  - Is there a systematic comparison of tool-calling, MCP, code-generation and CLI agents
    on the same benchmarks?
  - Which paper introduces an open leaderboard of agent architecture and backbone model combinations?
  answers:
  - leaderboard-contribution
  - unified-protocol-contribution
- q:
  - Does the agent scaffold or the underlying LLM matter more for agent performance?
  - How much of agent success variance comes from the backbone model versus the agent architecture?
  - Is optimizing agent architecture worth it compared with switching to a stronger backbone
    LLM?
  answers:
  - model-vs-architecture
  - within-model-swing
- q:
  - Can general-purpose agents match agents that were hand-tuned for a specific benchmark?
  - How do generalist agents compare to domain-specific SWE-Bench or tau2-Bench leaders?
  - Do you lose accuracy by using one unmodified agent across software engineering, customer
    service and deep research tasks?
  answers:
  - generalist-vs-specialist
  - no-dominant-architecture
- q:
  - Which agent and model combination scores highest across agentic benchmarks?
  - What is the top configuration on the Open General Agent Leaderboard?
  - Which backbone LLM leads for agentic tasks in a full agent-by-model factorial study?
  answers:
  - within-model-swing
  - model-vs-architecture
- q:
  - Do open-weight models work as reliably as closed frontier models inside agent scaffolds?
  - Why does the same open-weight model score 0.83 with one agent and 0.00 with another?
  - What are generality sinks in agent evaluation?
  answers:
  - generality-sinks
  - appworld-benchmark-sink
- q:
  - Does tool shortlisting help agents in environments with hundreds of tools?
  - Is filtering the tool list per turn worth it for a ReAct agent?
  - How much does tool shortlisting improve success and reduce cost?
  answers:
  - shortlisting-ablation
  - shortlisting-cost
- q:
  - What happens when a benchmark exposes more tools than the model's API allows?
  - Why do GPT 5.2 agents score zero on AppWorld?
  - Does a 128-tool API limit break agent evaluation on tool-rich environments?
  answers:
  - gpt-tool-limit
  - appworld-benchmark-sink
- q:
  - How much does it cost per task to run frontier agents on agentic benchmarks?
  - Which agent configurations give the best success per dollar?
  - Is the highest-scoring agent configuration also the most cost-efficient?
  answers:
  - cost-efficiency
- q:
  - Do failing agent runs burn more steps than successful ones?
  - How much extra compute do failed agent trajectories consume?
  - Do different agent architectures fail in different ways?
  answers:
  - failure-cost
  - failure-signatures
- q:
  - What kinds of errors do agents actually make on long-horizon tasks?
  - Can failure-mode analysis distinguish agent architectures that success rates cannot?
  - What is Premature Termination in agent failure taxonomies?
  answers:
  - failure-signatures
- q:
  - How does the Unified Protocol let an unmodified agent run on an unmodified benchmark?
  - What is the task/context/actions representation used by Exgentic?
  - How can I evaluate my own agent on SWE-Bench, AppWorld and tau2-Bench without per-benchmark
    wiring?
  answers:
  - unified-protocol-contribution
  - leaderboard-contribution
- q:
  - Do agentic benchmarks measure the same underlying capability?
  - How correlated are AppWorld, BrowseComp+, SWE-Bench and tau2-Bench scores across configurations?
  - Which agentic benchmark captures the most distinct skills?
  answers:
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
