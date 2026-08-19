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

Then promote it:  python scripts/draft_sidecars.py --accept position-agentic-systems-should-be-general

Stamp: spec=74e012ff9654 checks=1 body=5b0902575b91
-->
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
    a system prompt that assumes authenticated status.
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
- q:
  - What should I read about building agents that work across many environments?
  - Is there a position paper arguing for general-purpose AI agents instead of task-specific
    ones?
  - What work argues that agentic systems should be general rather than benchmark-specific?
  answers:
  - core-position
  - generality-spectrum
- q:
  - What does it mean for an agent to be general?
  - How is agent generality defined and measured?
  - Is generality of an agentic system a yes-or-no property?
  answers:
  - generality-spectrum
- q:
  - Can a simple general agent match a specialized scientific research agent?
  - How does a ReAct agent compare to ASTA-v0 on ASTA Bench?
  - What is the cost difference between a generalist agent and a specialized agent on scientific
    tasks?
  answers:
  - asta-react
  - asta-literature
- q:
  - Does a minimal agent do as well as SWE-Agent on SWE-Bench?
  - How much worse is Mini SWE-Agent than SWE-Agent?
  - Is a 131-line coding agent competitive on SWE-Bench?
  answers:
  - swe-mini
- q:
  - How much performance do you lose by using a small general agent instead of a specialized
    pipeline?
  - Is there evidence that general agents are nearly as good as specialized ones?
  - What is the performance gap between a few-hundred-line general agent and a thousands-of-lines
    specialized system?
  answers:
  - sparks-summary
  - asta-react
  - swe-mini
- q:
  - Are current 'generalist' agents actually general?
  - Does the HAL Generalist Agent contain benchmark-specific code?
  - Why is CUGA still constrained despite being configurable?
  answers:
  - hal-conditionals
  - cuga-config
- q:
  - What does an environment-agnostic agent architecture look like?
  - How can an agent support a new benchmark without changing its control flow?
  - Why is mini-swe-agent held up as an example of good agent design?
  answers:
  - env-agnostic-design
- q:
  - Why can't the same agent be evaluated on Tau-Bench, WebArena and TerminalBench?
  - Do agent benchmarks assume a specific agent interface?
  - What makes cross-environment agent evaluation so hard?
  answers:
  - benchmark-interfaces-incompatible
  - eval-levels
- q:
  - Is MCP enough to standardize agent evaluation?
  - What is missing from the Model Context Protocol for general agents?
  - How consistently do agent frameworks implement MCP tools, resources and prompts?
  answers:
  - mcp-gaps
- q:
  - Do agent benchmarks report success and cost in comparable ways?
  - How do metric definitions differ between SWE-Bench, AppWorld and Tau-Bench?
  - Why is aggregating results across agent benchmarks unreliable?
  answers:
  - metric-fragmentation
- q:
  - What levels of generality exist in agent evaluation setups?
  - Which agent benchmarks are protocol-agnostic?
  - Where do BrowserGym and Harbor sit relative to HAL in evaluation generality?
  answers:
  - eval-levels
- q:
  - What is the case for specialized agents over general ones?
  - Does arguing for general agents mean arguing for more autonomous agents?
  - Are there safety or control arguments against general-purpose agentic systems?
  answers:
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
