---
key: bandel2026position
one_liner: Position paper arguing that agentic systems should be built as general-purpose,
  environment-agnostic designs rather than benchmark-specific ones, and that protocols and
  evaluation must describe environment affordances instead of assuming a particular agent
  interface.
claims:
- id: core-position
  kind: context
  text: '"Position: Agentic Systems Should be General" argues that domain-specific agents
    are a transitional stage and that agent developers should favor general-purpose designs
    that adapt across environments while minimizing per-deployment human effort.'
  scope: A position paper at the ICLR 2026 Workshop on Agents in the Wild, about research
    priorities rather than what practitioners should ship; specialized agents are held to
    remain valuable.
- id: generality-spectrum
  kind: context
  text: Generality of an agentic system is a spectrum measured by how little per-deployment
    human effort a design requires. It is not a binary property, and not how well one instantiation
    scores on a single task.
  scope: A definitional position stated in the paper's own terms, which declines to set a
    fixed requirement list and does not claim "Agentic General Interaction" is reachable.
- id: asta-react
  kind: result
  text: On ASTA Bench scientific tasks, a 358-line generalist ReAct agent using GPT-5 reaches
    a 44% ASTA score at $0.31 per task. The specialized ASTA-v0 system scores 53% at $3.40
    per task with subsystems exceeding 13,000 lines of code.
  evidence: Table 1
  scope: One benchmark, ASTA Bench, with ASTA-v0 using a mix of Claude 4 Sonnet, Gemini 2.5
    Flash, O3, GPT-4.1 and GPT-4o; single reported runs, treated as anecdotal rather than
    a controlled comparison.
- id: asta-literature
  kind: result
  text: On the ASTA Bench literature-understanding subtask, the general ReAct agent scores
    53%, below the specialized Asta agent's 62% but above the specialized ASTA Paper Finder's
    21% and OpenAI Deep Research's 19%.
  evidence: Section 5
  scope: One subtask of one scientific-research benchmark; the general agent still loses to
    the strongest specialized system on that subtask.
- id: swe-mini
  kind: result
  text: On SWE-Bench with Claude 4 Sonnet, the domain-agnostic 131-line Mini SWE-Agent scores
    65% versus 67% for the 4,161-line specialized SWE-Agent, at $0.37 per task versus about
    $2.50.
  evidence: Table 2
  scope: SWE-Bench only, both agents run with Claude 4 Sonnet; the minimal agent is described
    as roughly 30 times smaller and about 7 times cheaper per run.
- id: sparks-summary
  kind: result
  text: Across the scientific and software-engineering cases examined, small general agents
    of a few hundred lines reach 70% to 95% of the performance of specialized systems that
    run to thousands of lines.
  evidence: Section 5
  scope: Two settings only, ASTA Bench and SWE-Bench, which the paper itself calls currently
    rare and anecdotal; no claim that the ratio transfers to web or embodied environments.
- id: hal-conditionals
  kind: result
  text: The HAL Generalist Agent supports multiple environments yet contains more than 20
    instances of conditional logic keyed on the benchmark name. Those branches encode per-benchmark
    assumptions about dataset structure, available tools and task-relevant information.
  evidence: Section 4.2
  scope: A code inspection of the HAL Generalist Agent implementation as of the paper's writing,
    counting `if kwargs['benchmark_name'] == ...` style branches.
- id: cuga-config
  kind: result
  text: CUGA supports multiple benchmarks only through manual benchmark-specific setup, including
    an AppWorld-specific authentication module that logs into applications for the agent and
    a system prompt that assumes authenticated status. The HAL Generalist Agent shows the
    same pattern, with more than 20 instances of conditional logic branching on the benchmark
    name.
  evidence: Section 4.2
  scope: Code inspection of CUGA as of the paper's writing, on its AppWorld support; configurability
    of this kind still leaves the system constrained in novel domains it was not set up for.
- id: benchmark-interfaces-incompatible
  kind: result
  text: 'Tau-Bench, WebArena and TerminalBench each hard-code a mutually incompatible agent
    interface: user messaging, browser actions and command-line execution respectively. Evaluating
    one agent across all 3 is impossible without ad hoc engineering.'
  evidence: Section 8.3
  scope: Three interactive agent benchmarks inspected at their agent base-class level; BrowserGym
    and Harbor are cited as more general within the browser and terminal domains, but each
    still imposes one interaction mode.
- id: mcp-gaps
  kind: result
  text: MCP's 3 primitives of tools, resources and prompts represent neither benchmark task
    semantics nor evaluation workflows. Of 5 surveyed frameworks, all implement tools, only
    Claude Code implements resources, and only the OpenAI Agents SDK implements prompts.
  evidence: Table C.1
  scope: MCP as a candidate substrate for general-agent evaluation, surveyed over Smolagents,
    Llama Stack, OpenAI Agents SDK, Codex CLI and Claude Code at the time of writing; A2A
    is noted as having similar gaps.
- id: metric-fragmentation
  kind: result
  text: 'Basic outcome metrics are incompatible across agent benchmarks: success appears as
    a Boolean `resolved` flag in SWE-Bench, a `success` field in AppWorld and an implicit
    reward of 1 in Tau-Bench. Of the 3, only Tau-Bench reports interaction cost.'
  evidence: Table C.2
  scope: Three representative benchmarks — Tau-Bench, AppWorld and SWE-Bench — compared across
    11 metric types including termination, duration, interaction counts, cost and aggregation
    conventions.
- id: eval-levels
  kind: result
  text: A 5-level classification of agent evaluation generality places BFCL and GSM8K at agentic
    skills, Tau-Bench and WebArena at interactive-model, HAL at cross-model harness, and BrowserGym
    and Harbor at protocol-centric. The top level, protocol-agnostic general evaluation, has
    no existing example.
  evidence: Table A.1
  scope: A classification by the axes of cross-model, interaction, cross-environment, cross-agent
    and protocol-agnostic coverage, over the benchmarks cited as of the paper's writing.
- id: env-agnostic-design
  kind: result
  text: mini-swe-agent drives everything through 1 generic command-execution interface and
    never branches on benchmark identifiers, running a 5-step loop of template rendering,
    model query, action parsing, execution and observation feedback. Supporting a new benchmark
    therefore requires only an Environment backend exposing execute() plus the necessary template
    variables.
  evidence: Section 4.3
  scope: One system, which does not itself claim generality; the extension mechanism holds
    only where the target environment provides a CLI or can be wrapped as one.
- id: alternative-views
  kind: context
  text: '"Position: Agentic Systems Should be General" concedes control, predictability, efficiency
    and evaluation rigor as genuine advantages of specialized agents. It argues separately
    that generality is a distinct property from autonomy.'
  scope: Opposing positions as engaged with in the paper, which acknowledges reduced insight
    into how a general agentic pattern interacts with the world and refers readers elsewhere
    on the autonomy-safety debate.
qa:
- ask:
    plain: is there a paper arguing that AI agents should be built to work anywhere instead
      of tuned for one task?
    jargon: which position paper argues for general-purpose agentic systems over benchmark-specific
      agent designs?
    task: where do I find the argument for building one agent that transfers across environments
      rather than one per domain?
    practitioner: should I read a position paper before committing my team to a domain-specific
      agent architecture?
  answered_by:
  - core-position
  - generality-spectrum
- ask:
    plain: what makes an AI agent count as general rather than built for one job?
    jargon: how is generality of an agentic system defined and measured, and is it binary
      or graded?
    task: how do I judge how general my agent actually is instead of just reporting its benchmark
      score?
    practitioner: can I call my agent general if it only tops one benchmark?
  answered_by:
  - generality-spectrum
- ask:
    plain: can a short, simple agent keep up with a purpose-built research assistant on science
      tasks, and what does each cost per task?
    jargon: how does a generalist ReAct scaffold compare with the specialized ASTA-v0 pipeline
      on ASTA Bench score and per-task cost?
    task: how do I decide between a small ReAct loop and a specialized scientific-research
      pipeline for literature and science tasks?
    practitioner: is a purpose-built scientific agent worth its per-task cost over a plain
      ReAct agent I can write myself?
  answered_by:
  - asta-react
  - asta-literature
- ask:
    plain: can a tiny coding agent of about a hundred lines fix real GitHub issues about as
      well as a much bigger one?
    jargon: what is the SWE-Bench resolve rate and per-task cost of mini-swe-agent versus
      the full SWE-Agent scaffold under Claude 4 Sonnet?
    task: how do I pick between a minimal command-line coding agent and a full software-engineering
      scaffold for issue fixing?
    practitioner: can I ship the minimal SWE agent instead of the heavier one without losing
      much accuracy?
  answered_by:
  - swe-mini
- ask:
    plain: how much accuracy do you give up by using a small general-purpose agent instead
      of a big purpose-built pipeline?
    jargon: what fraction of specialized-system performance do compact domain-agnostic scaffolds
      recover on scientific and software-engineering benchmarks?
    task: how do I estimate the accuracy penalty of replacing a thousands-of-lines specialized
      agent with a few-hundred-line general one?
    practitioner: is the engineering cost of a large specialized agent justified by the performance
      it buys over a small general one?
  answered_by:
  - sparks-summary
  - asta-react
  - swe-mini
- ask:
    plain: are agents advertised as generalist really general, or do they have code paths
      per benchmark?
    jargon: do the HAL Generalist Agent and CUGA achieve multi-benchmark support through genuine
      environment abstraction or benchmark-keyed conditionals and manual setup?
    task: how do I tell whether a multi-benchmark agent I am adopting has hidden per-benchmark
      branching and setup?
    practitioner: if I run the HAL Generalist Agent or CUGA on my own environment, how much
      benchmark-specific plumbing will I have to write?
  answered_by:
  - hal-conditionals
  - cuga-config
- ask:
    plain: what does an agent design look like when it does not need changing for each new
      environment?
    jargon: how does mini-swe-agent stay environment-agnostic through a single command-execution
      interface without benchmark-keyed control flow?
    task: how do I add a new environment to my agent without touching its control loop?
    practitioner: what interface should I expose so my agent supports a new benchmark by adding
      a backend rather than a code branch?
  answered_by:
  - env-agnostic-design
- ask:
    plain: why is it so hard to run the same AI agent on several different benchmarks?
    jargon: why do Tau-Bench, WebArena and TerminalBench hard-code mutually incompatible agent
      interfaces, and what levels of evaluation generality exist above them?
    task: how do I evaluate one agent across a messaging benchmark, a browser benchmark and
      a terminal benchmark without ad hoc glue code?
    practitioner: should I expect to write custom adapters for every agent benchmark I want
      to test my agent on?
  answered_by:
  - benchmark-interfaces-incompatible
  - eval-levels
- ask:
    plain: is the Model Context Protocol enough to let one agent be evaluated everywhere?
    jargon: do MCP's tools, resources and prompts primitives cover benchmark task semantics
      and evaluation workflows, and how uniformly are they implemented across agent frameworks?
    task: can I rely on MCP as the single integration layer for running my agent against many
      benchmarks?
    practitioner: if I build on MCP, which of its primitives will actually be supported by
      the agent frameworks I use?
  answered_by:
  - mcp-gaps
- ask:
    plain: do different AI agent benchmarks report success and cost in ways you can compare?
    jargon: how do outcome and cost metric definitions differ across SWE-Bench, AppWorld and
      Tau-Bench?
    task: how do I aggregate success rates and costs from several agent benchmarks into one
      comparable table?
    practitioner: can I trust a leaderboard that averages agent success rates across benchmarks
      with different metric definitions?
  answered_by:
  - metric-fragmentation
- ask:
    plain: are there degrees of generality in how AI agents get evaluated, and where do current
      benchmarks fall?
    jargon: what 5-level classification places BFCL, Tau-Bench, WebArena, HAL, BrowserGym
      and Harbor on a spectrum of evaluation generality?
    task: how do I work out which rung of evaluation generality my agent harness currently
      sits on?
    practitioner: is there any existing agent evaluation setup that is protocol-agnostic,
      or do I have to build one?
  answered_by:
  - eval-levels
- ask:
    plain: what are the good arguments for building a narrow, task-specific AI agent instead
      of a general one?
    jargon: which advantages of specialized agents, such as control, predictability, efficiency
      and evaluation rigor, are conceded, and is generality the same property as autonomy?
    task: how do I weigh control and predictability against generality when choosing an agent
      design?
    practitioner: if I make my agent more general, am I also making it more autonomous and
      harder to control?
  answered_by:
  - alternative-views
terminology:
  Agentic pattern: The core orchestration algorithm of an agentic system, governing how components
    such as foundation models, memory, context compression and tool execution interact and
    react to one another given an initial input.
  General-purpose agent: An agentic system able to perform different types of agentic tasks
    across unfamiliar environments, where generality is measured by how little manual effort
    each new deployment requires.
  Benchmark-conditioned general agent: An agent that nominally supports several environments
    but encodes environment- or benchmark-specific assumptions inside its own logic, for example
    by branching on a benchmark identifier.
  Agent-agnostic evaluation: Benchmark design that specifies the task, observations and action
    effects without assuming a particular agent interface, so agents built on different protocols
    can be evaluated natively.
  General performance: The distinction between an agent being capable in principle, analogous
    to Turing-completeness, and being practically efficient and reliable in a new environment.
  Narrow waist: A stable, minimal interface layer — by analogy with the Internet protocol
    stack — that decouples development of tools, models and agentic patterns while preserving
    interoperability.
  Environment affordances: 'What an unseen environment offers an agent: what to expect, what
    can be used, and how the agent is expected to act, which a general agent must receive
    or collect rather than have hard-coded.'
misreadings:
- '"Position: Agentic Systems Should be General" does not claim specialized agents are useless:
  it holds that specialization is a transitional research stage and that general systems give
  better starting points for the specialized agents practitioners still need.'
- The ASTA Bench and SWE-Bench comparisons are presented as anecdotal sparks of promise, not
  as a controlled demonstration that general agents beat specialized ones — in both cases
  the specialized system still scores higher.
- Arguing for general agents is not arguing for more autonomous agents; generality and autonomy
  are treated as distinct properties, and no position is taken on how much autonomy agents
  should have.
- Naming HAL and CUGA as benchmark-conditioned is a critique of where environment assumptions
  live in the code, not a claim that those systems perform poorly on the benchmarks they target.
- 'Criticism of MCP is not a claim that MCP should be abandoned: it is identified as promising
  groundwork that lacks task semantics and evaluation-workflow support needed for general-agent
  evaluation.'
---
