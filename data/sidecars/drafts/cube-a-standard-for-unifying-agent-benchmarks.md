<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced via a forced tool call) + 3 repair rounds. Every claim, number
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

Then promote it:  python scripts/draft_sidecars.py --accept cube-a-standard-for-unifying-agent-benchmarks

Stamp: spec=8f05813a4658 checks=pass body=912b476a9daa
-->
---
key: lacoste2026cube
coined: CUBE
gloss: Common Unified Benchmark Environments — a wrap-once protocol so any agent benchmark
  runs on any evaluation or RL platform
one_liner: CUBE is a proposed protocol standard fusing MCP tool calls with Gym-style reset/step/evaluate
  semantics, splitting task, benchmark, package and registry concerns into separate API layers
  so an agent benchmark is wrapped once and usable by any compliant evaluation or RL-training
  platform.
claims:
- id: integration-tax-position
  kind: context
  text: CUBE is a position paper naming the "integration tax" as the bottleneck that limits
    which labs can evaluate agents broadly. The tax is the per-benchmark custom wrapper work
    that N agents against M benchmarks demands, and CUBE's proposed fix is a single benchmark-side
    interface contract.
  scope: A position paper from March 2026 arguing for a standard; it reports no agent accuracy
    results and no measured reduction in engineering effort. Concurrent with AgentBeats' Agentified
    Agent Assessment paradigm, which shares the motivation but differs in scope and design.
- id: benchmark-count-forecast
  kind: result
  text: Over 300 agentic benchmarks exist, many of them innovative but largely unknown because
    they are too difficult to set up. CUBE's authors forecast that number to double by the
    end of 2026.
  evidence: Section 1
  scope: A community count and an authors' projection as of March 2026, not a systematic survey
    with an enumerated list; the doubling is attributed to coding-agent and RL post-training
    activity.
- id: four-layer-separation
  kind: context
  text: 'CUBE separates agent-benchmark integration into 4 distinct API layers: task-level
    interaction, benchmark-level discovery and spawning, package-level installation and parallelization,
    and a registry-level metadata catalog. A benchmark author implements Python classes once
    and CUBE generates the RPC layer automatically.'
  evidence: Section 3
  scope: Describes the proposed contract as of the v1 draft; the reference implementation
    is labelled alpha and interfaces may change. The layer split is argued on design grounds,
    not validated by a user study or an integration-effort measurement.
- id: mcp-gym-fusion
  kind: result
  text: CUBE's task-level API keeps MCP's tools/list, tools/call, resources/list and resources/read
    unchanged, and adds cube/evaluate, cube/reset, cube/step, cube/close and cube/privileged_info.
    The result is a superset from which both plain MCP and plain Gym can be recovered, plus
    a non-blocking async-Gym pattern.
  evidence: Table 2
  scope: MCP is chosen for actions because its non-blocking tools/call and tool-signature
    discovery suit benchmarks such as ARE and GAIA-2 that require agents to coordinate long-running
    operations; the traditional blocking Gym step function cannot express those patterns.
- id: shared-infrastructure-lifecycle
  kind: result
  text: CUBE's benchmark-level layer handles benchmarks whose infrastructure is shared across
    tasks, such as WebArena's persistent GitLab, e-commerce and forum micro-internet or OSWorld's
    full desktop OS. Those resources are initialized once in Benchmark.setup() and each spawned
    task receives a RuntimeContext.
  evidence: Section 3.2 and Section 3.3
  scope: OpenEnv requires the user to provision shared infrastructure externally via environment
    variables, and Harbor's per-task container model has no cross-task shared-infrastructure
    lifecycle, which is reflected in its adapter catalogue excluding WebArena and OSWorld.
- id: privileged-info
  kind: result
  text: CUBE standardizes an optional info field carrying privileged information at both task
    and step level, such as the evaluation function's source code, ground-truth answers, or
    summaries of internal environment state. Its stated purposes are better LLM-judge failure
    diagnosis and privileged policy distillation during training.
  evidence: Table 2 and Section 3.1
  scope: The field is curated by benchmark designers and optional, so its content varies by
    benchmark; the paper motivates it from documented LLM-judge limitations but reports no
    measurement of judge accuracy with versus without it.
- id: debug-agent-ci
  kind: result
  text: Every CUBE package must expose get_debug_task_configs() and make_debug_agent(task_id),
    a scripted agent guaranteed to solve a debug task. Any consumer can then run a full episode
    end-to-end and assert the reward reaches 1.0 without calling a live language model.
  evidence: Section 3.3
  scope: Makes benchmarks testable in standard CI pipelines; it checks that the harness plumbing
    and reward path work, not that the benchmark's task difficulty or evaluation logic is
    well designed.
- id: registry-no-hosting
  kind: result
  text: The CUBE Registry indexes metadata only and hosts no benchmark code or data, pointing
    at PyPI via a package field. The recorded metadata covers runtime type (docker, apptainer,
    vm, docker-root, docker-in-docker, live), hardware needs, task count, separate package
    and benchmark licenses, and a content notice for cloned or copyrighted material.
  evidence: Table 4 and Section 3.4
  scope: Registration triggers a GitHub compliance-verification job; the design intent is
    that authors retain control of distribution and that researchers can filter out benchmarks
    incompatible with their infrastructure before installing anything.
- id: infrastructure-heterogeneity
  kind: result
  text: 'Four popular agent benchmarks disagree on nearly every infrastructure axis: SWE-bench
    uses per-task Docker containers, WebArena and OSWorld need benchmark-level VMs, and GAIA
    ships static files with no tools at all. OSWorld''s scaling bottleneck is 20 GB+ of RAM
    per agent plus heavy disk I/O for state resets.'
  evidence: Table 1
  scope: A 4-benchmark comparison (WebArena, SWE-bench, OSWorld, GAIA) chosen to illustrate
    heterogeneity in hosting format, action space, integration effort and scaling bottleneck;
    not an exhaustive benchmark survey.
- id: coverage-comparison
  kind: result
  text: CUBE had 9 wrapped CUBEs at the time of writing, an explicitly early-stage catalogue.
    The compared platforms list 40+ environments in NeMo Gym, 250+ benchmarks across 17 domains
    in AgentBeats, 30+ in OpenEnv and 46+ adapters in Harbor.
  evidence: Table 5
  scope: Counts as documented in March 2026, which move quickly. CUBE is the only entry in
    the comparison whose stated coverage includes shared-infrastructure and VM-based benchmarks.
- id: complementary-not-competing
  kind: context
  text: 'CUBE positions existing agent platforms as complementary rather than rivals, and
    targets the benchmark packaging and infrastructure lifecycle layer that none of them specifies.
    Each compared platform evolved from its own niche: NeMo Gym from RL training, AgentBeats
    from competition infrastructure, OpenEnv from the HuggingFace ecosystem, Harbor from SWE
    evaluation and HAL from academic benchmarking.'
  evidence: Section 4.3 and Table 5
  scope: Platform features and documentation available in March 2026. The paper states an
    AgentBeats judge agent could consume a CUBE benchmark through a thin connector, but reports
    no such connector as built.
- id: design-not-optimal
  kind: context
  text: CUBE's authors state explicitly that their design is not claimed to be optimal, only
    that some standard is necessary. Objections they list a critic might prefer include explicit
    async primitives, fewer abstraction layers, pure Gym without MCP, and message-passing
    over RPC.
  evidence: Section 5
  scope: A draft standard put forward for community feedback in March 2026; the listed alternative
    designs are not evaluated against CUBE's own.
- id: two-sided-adoption
  kind: result
  text: CUBE's adoption plan addresses a two-sided deadlock in which platforms wait for compliant
    benchmarks while benchmark authors wait for platform demand. The plan recruits early platform
    supporters to build reference connectors for NVIDIA NeMo Gym and OpenEnv, and targets
    critical mass by the end of 2026.
  evidence: Section 3.6
  scope: A plan and a target date stated in March 2026, not an achieved outcome; the initial
    corpus spans web navigation, software engineering and desktop environments, the reference
    implementation is alpha and the connectors are proposed deliverables.
qa:
- q:
  - How can I run one agent across many different agent benchmarks without writing a wrapper
    for each?
  - Is there a standard interface for agent benchmarks so they work on any evaluation platform?
  - What does CUBE propose for unifying agent benchmarks?
  answers:
  - integration-tax-position
  - four-layer-separation
  - mcp-gym-fusion
- q:
  - What should I read about fragmentation in agent benchmark infrastructure?
  - Which paper argues for a common standard for agent evaluation environments?
  - Where should I start reading about the integration burden of agentic benchmarks?
  answers:
  - integration-tax-position
  - complementary-not-competing
- q:
  - How many agentic benchmarks are there right now?
  - Is the number of agent benchmarks expected to grow?
  - How many agent benchmarks does the CUBE position paper count?
  answers:
  - benchmark-count-forecast
- q:
  - Why combine MCP with the Gym API instead of just using Gym?
  - How does CUBE handle asynchronous, non-blocking tool calls that a blocking step function
    cannot?
  - What methods does the CUBE task-level API define?
  answers:
  - mcp-gym-fusion
- q:
  - How do you support benchmarks like WebArena or OSWorld that need one shared server or
    VM across all tasks?
  - Which agent frameworks can manage shared infrastructure spanning multiple tasks?
  - Why do OpenEnv and Harbor struggle with WebArena and OSWorld?
  answers:
  - shared-infrastructure-lifecycle
  - infrastructure-heterogeneity
- q:
  - Why is integrating agent benchmarks so much work — what actually differs between them?
  - How much RAM does OSWorld need per agent?
  - What are the infrastructure differences between WebArena, SWE-bench, OSWorld and GAIA?
  answers:
  - infrastructure-heterogeneity
- q:
  - Can an evaluation harness get ground-truth answers or the grading code to help an LLM
    judge?
  - What is privileged information in the CUBE benchmark protocol?
  - How can judge-based failure analysis be made more accurate on agent benchmarks?
  answers:
  - privileged-info
- q:
  - How do I test that a wrapped agent benchmark actually works without paying for LLM calls?
  - Can agent benchmarks be checked in a CI pipeline?
  - What is a CUBE debug agent for?
  answers:
  - debug-agent-ci
- q:
  - How would I discover agent benchmarks that fit my available GPU, RAM and container runtime?
  - Does the CUBE registry host benchmark code or data?
  - What metadata does a registered CUBE benchmark have to publish?
  answers:
  - registry-no-hosting
- q:
  - How does CUBE compare with NeMo Gym, OpenEnv, Harbor, AgentBeats and HAL?
  - How many benchmarks does CUBE currently wrap compared with other agent platforms?
  - Which agent benchmark platform wraps the most environments — NeMo Gym, OpenEnv, Harbor
    or AgentBeats?
  answers:
  - coverage-comparison
  - complementary-not-competing
- q:
  - Do the CUBE authors claim their API design is the right one?
  - What objections to the CUBE design do its own authors acknowledge?
  - Is there an argument against adding a new agent benchmark standard at all?
  answers:
  - design-not-optimal
- q:
  - How does a new benchmark standard get adopted when platforms and benchmark authors each
    wait for the other?
  - What is the plan for getting CUBE adopted, and by when?
  - Which platforms are getting CUBE reference connectors?
  answers:
  - two-sided-adoption
misreadings:
- 'CUBE is a protocol specification plus a reference implementation, not a benchmark suite:
  the paper reports no agent scores and, at the time of writing, only 9 wrapped benchmarks.'
- The claim that CUBE reduces integration work is an argument from design, not a measurement
  — the paper reports no experiment quantifying engineering time saved versus writing per-benchmark
  wrappers.
- CUBE is not a replacement for NeMo Gym, OpenEnv, Harbor or AgentBeats; it targets the benchmark
  packaging and infrastructure-lifecycle layer and expects those platforms to consume CUBE
  benchmarks through thin connectors.
- 'Building on MCP does not mean CUBE is only for tool-calling LLM agents: cube/reset, cube/step
  and cube/evaluate keep Gym-compatible RL semantics, with in-process Python execution for
  low-latency training loops.'
- The CUBE Registry is not a hosting service — it indexes metadata and points at PyPI, so
  benchmark authors keep control of their own distribution.
- 'Requiring benchmark authors to ship default tools does not lock agents into those tools:
  a tool_config parameter at initialization lets researchers substitute alternative tool implementations
  without changing benchmark code.'
- The "over 300 benchmarks doubling by end of 2026" figure is the authors' forecast stated
  in a position paper, not an outcome measured from a benchmark census.
terminology:
  Integration Tax: The redundant engineering cost of writing a separate driver or wrapper
    for every agent-benchmark pair, so that evaluating one agent on five benchmarks means
    five unique wrappers, and switching evaluation frameworks means starting over.
  CUBE: 'Common Unified Benchmark Environments: a protocol standard defining task-, benchmark-,
    package- and registry-level interfaces that an agent benchmark implements once to become
    usable by any compliant evaluation or RL-training platform.'
  a CUBE: A single benchmark wrapped to comply with the CUBE standard, distributed as a Python
    package and indexed in the CUBE registry.
  async-Gym API: An interaction pattern obtained by fusing MCP's non-blocking tools/call with
    Gym-style reward and termination semantics, letting an agent issue multiple concurrent
    long-running tool calls instead of waiting inside a blocking step function.
  privileged information: Optional context exposed to the evaluation harness but not the agent
    — evaluation function source code, ground-truth answers, or summaries of internal environment
    state — used for judge-based failure diagnosis and privileged policy distillation.
  debug agent: A scripted, non-LLM agent shipped with a benchmark package that is guaranteed
    to solve a designated debug task, so a full episode can be run in CI and asserted to reach
    a reward of 1.0.
  compliance badge: A registry-visible marker earned by a benchmark that passes a stress suite
    verifying idempotent resets, isolation between concurrent task instances, and resource
    usage within declared bounds.
links_extra:
  code: https://github.com/The-AI-Alliance/cube-standard
  harness: https://github.com/The-AI-Alliance/cube-harness
  docs: https://the-ai-alliance.github.io/cube-standard/
  benchmark-contribution-form: https://docs.google.com/forms/d/e/1FAIpQLSddMFyRXZJPpD0I2K27OEmIPUpj57w--u2NuMscrjNlkqy8rQ/viewform
---
