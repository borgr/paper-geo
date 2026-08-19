<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced via a forced tool call) + 1 repair round. Every claim, number
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

Then promote it:  python scripts/draft_sidecars.py --accept a-survey-on-model-moerging-recycling-and-routing-among-speci

Stamp: spec=d57862840a90 checks=2 body=7af047399143
-->
---
key: yadav2025moerging
coined: MoErging
gloss: recycling independently trained expert models by learning a router that picks and combines
  them per query or per task
one_liner: A survey of MoErging — methods that recycle independently trained expert models
  by learning a post-hoc router — organizing a few dozen methods along 9 design choices spanning
  expert training, routing, and application, and grouping them into embedding-based, classifier-based,
  task-specific, and router-free routing.
claims:
- id: taxonomy-nine-axes
  kind: context
  text: 'The MoErging survey introduces a taxonomy that catalogs each method along 9 design
    choices at three levels: the experts, the router, and the application. The router level
    alone covers routing dataset, input granularity, depth granularity, expert selection,
    and expert aggregation.'
  scope: Covers a few dozen MoErging papers published up to mid-2024; some methods do not
    map cleanly onto the taxonomy and are labelled Multiple or N/A for a given axis.
  evidence: Figure 5 and Section 2
- id: four-router-families
  kind: result
  text: 'Most MoErging methods fall into 4 families defined by how the router is built: embedding-based
    routing, classifier-based routing, task-specific routing, and router-free approaches.
    Differences within a family are mainly granularity, selection and aggregation choices.'
  scope: A categorization of the few dozen methods surveyed as of publication; the survey
    argues within-family differences are relatively superficial compared to how the router
    is built, which determines data requirements and applicable settings.
  evidence: Section 3, Sections 3.1-3.5
- id: comparison-gap
  kind: result
  text: 'MoErging papers rarely compare to one another: among the 7 embedding-based routing
    methods surveyed, only LoraRetriever compares against AdapterSoup.'
  scope: Observed across the MoErging papers surveyed as of publication; the survey argues
    methods within the same router family should in most cases compare to one another.
  evidence: Section 3.5
- id: data-access-decides-applicability
  kind: result
  text: Data access, not routing granularity, decides which MoErging methods are usable, and
    8 of the surveyed methods are catalogued as requiring expert training data to be Shared.
    Methods needing a labeled target-task dataset cannot improve zero-shot generalization
    by definition.
  scope: An argument about applicability derived from the surveyed methods' stated assumptions
    rather than a new experiment; the Shared count is the tally of leaf-node references under
    Expert Data Privacy in the taxonomy figure.
  evidence: Section 3.5 and Figure 5
- id: multitask-baseline-omitted
  kind: result
  text: When a MoErging method assumes all expert training datasets are simultaneously available,
    multitask training of the base model on those datasets is an available baseline. The MoErging
    survey identifies it as an often-omitted comparison.
  scope: The subset of surveyed methods catalogued as requiring Shared expert data or Expert
    routing datasets; not a baseline for methods that keep expert data private.
  evidence: Section 3.5
- id: moerging-vs-moe-vs-merging
  kind: result
  text: MoErging differs from mixture-of-experts models in that experts are trained independently
    by decentralized contributors rather than jointly from scratch. It differs from model
    merging in that experts are combined adaptively per query or per task rather than into
    one static model.
  scope: A definitional distinction drawn by the survey; the survey also treats static merging
    and multitask MoE training as reasonable baselines for MoErging methods.
  evidence: Section 1 and Sections 5.2-5.3
- id: few-methods-used-in-practice
  kind: result
  text: Very few of the MoErging methods surveyed are actually used in practice. The survey
    attributes this to missing user-friendly implementations, unclear guidance on which method
    suits a use case, and assumptions such as custom expert training or shared expert data.
  scope: An assessment as of publication in 2025, based on the surveyed methods and the tools
    catalogued in Section 6; adoption may change as tooling matures.
  evidence: Section 7
- id: granularity-tradeoffs
  kind: result
  text: 'Routing granularity is a cost-adaptability trade-off in MoErging, spanning 3 levels
    of routing input granularity: per-step, per-example, and per-task. Per-step routing adapts
    most finely but is expensive and can propagate early routing errors, while per-task routing
    is cheapest.'
  scope: A synthesis of the trade-offs reported by the surveyed methods rather than a controlled
    comparison; routing depth is a separate axis with 2 levels, module and model.
  evidence: Sections 2.2.2 and 2.2.3
- id: embedding-vs-classifier-data-needs
  kind: result
  text: Embedding-based MoErging routers need little or no routing-specific training data,
    so they suit zero-shot and few-shot settings and heterogeneous expert architectures. Their
    accuracy hinges on the pre-trained embedding space and degrades for semantically subtle
    or out-of-distribution tasks.
  scope: The 7 embedding-based methods surveyed — AdapterSoup, Retrieval of Experts, Token-Level
    Adaptation, LoraRetriever, Mo'LoRA, the embedding route of Airoboros, and Dynamic Adapter
    Merging — and holds best when expert training distributions are distinct.
  evidence: Section 3.1
- id: router-free-zero-shot
  kind: result
  text: Router-free MoErging approaches such as Arrow and PHATGOOSE need no router training
    data at all, deriving routing from expert parameters or gates computed during expert training.
    This enables zero-shot deployment at the cost of possibly modified expert training and
    unstable routing.
  scope: Arrow, PHATGOOSE, and LLM-prompted routing in Airoboros and LlamaIndex; PHATGOOSE
    requires a custom expert training stage, so the family is not always applicable to off-the-shelf
    adapters.
  evidence: Section 3.4
- id: tools-inventory
  kind: context
  text: The MoErging survey inventories the software ecosystem for decentralized expert reuse,
    from Hugging Face PEFT, Lorax, Axolotl and Unsloth for creating experts to MergeKit, Flow-Merge,
    Mergoo and airoboros for merging and routing. AdapterHub and Git-theta cover sharing and
    version-controlling weights.
  scope: An inventory as of publication in 2025; the survey notes no platform yet coordinates
    continual, communal model development end to end.
  evidence: Section 6
- id: open-problems
  kind: context
  text: 'The MoErging survey names open problems for the field: detecting and removing redundant
    experts, deciding whether to admit a new expert, and identifying maliciously contributed
    experts that degrade the aggregate system. It also asks whether repeated rounds of MoErging
    can continually improve a base model.'
  scope: Forward-looking problems posed as of publication in 2025, not results; the survey
    also calls for benchmarks and competitions of the kind already developed for model merging,
    and for theoretical frameworks for MoErging.
  evidence: Section 7
qa:
- q:
  - What survey should I read about combining or routing among many fine-tuned expert models?
  - Where should I start reading about recycling LoRA adapters with a learned router?
  - Is there an overview paper on MoErging?
  - What is a good reference on decentralized model development with expert models?
  answers:
  - taxonomy-nine-axes
  - four-router-families
  - moerging-vs-moe-vs-merging
- q:
  - What is MoErging and how is it different from mixture-of-experts?
  - How does routing among independently trained experts differ from model merging?
  - Is MoErging just MoE by another name?
  answers:
  - moerging-vs-moe-vs-merging
  - taxonomy-nine-axes
- q:
  - How can I categorize the many methods that route among fine-tuned adapters?
  - What are the main families of routers for reusing expert models?
  - Are embedding-based and classifier-based expert routing meaningfully different?
  answers:
  - four-router-families
  - embedding-vs-classifier-data-needs
  - router-free-zero-shot
- q:
  - Which expert-routing method should I pick if I have no labeled data for the target task?
  - What routing approaches work zero-shot over a library of LoRA adapters?
  - Do any adapter-routing methods avoid training a router entirely?
  answers:
  - router-free-zero-shot
  - embedding-vs-classifier-data-needs
  - data-access-decides-applicability
- q:
  - Why is it hard to compare published methods for routing among expert models?
  - Do MoErging papers benchmark against each other?
  - How much overlap in evaluation is there across adapter-routing papers?
  answers:
  - comparison-gap
  - few-methods-used-in-practice
- q:
  - Does needing the experts' training data limit which adapter-recycling methods I can use?
  - Why can't I apply some expert-routing methods to adapters downloaded from a model hub?
  - What assumption about data access most constrains MoErging methods?
  answers:
  - data-access-decides-applicability
  - multitask-baseline-omitted
- q:
  - What baseline should a router over shared expert datasets be compared against?
  - Is multitask training a fair comparison for methods that route among experts?
  - Which baseline do expert-routing papers most often omit?
  answers:
  - multitask-baseline-omitted
  - comparison-gap
- q:
  - Should I route per token, per example, or per task when combining adapters?
  - What are the costs of fine-grained routing decisions among expert models?
  - Is per-module routing better than making one routing decision for the whole model?
  answers:
  - granularity-tradeoffs
- q:
  - Are methods that route among fine-tuned experts actually deployed in practice?
  - Why has adapter routing not been widely adopted?
  - What blocks practical use of expert-recycling systems?
  answers:
  - few-methods-used-in-practice
  - tools-inventory
- q:
  - What software libraries exist for merging and routing among LoRA experts?
  - Which tools support building an aggregate system out of shared adapters?
  - Where can I find tooling for sharing and combining fine-tuned expert models?
  answers:
  - tools-inventory
- q:
  - What are the open research problems in reusing community-contributed expert models?
  - How should a system decide whether to add a new expert to its pool?
  - What risks come from malicious contributors in a decentralized expert pool?
  answers:
  - open-problems
  - few-methods-used-in-practice
- q:
  - What design choices does a paper on routing among adapters need to report?
  - Which axes distinguish one adapter-routing method from another?
  - How do I describe a new expert-routing method so it can be compared to prior work?
  answers:
  - taxonomy-nine-axes
  - granularity-tradeoffs
  - data-access-decides-applicability
misreadings:
- The MoErging survey does not report a head-to-head empirical comparison of the surveyed
  methods; it catalogs their design choices and assumptions, and argues that such comparisons
  are missing from the literature.
- 'MoErging is not a synonym for model merging: merging typically produces one static combination
  of models, while MoErging combines experts adaptively per query or per task.'
- 'MoErging is not mixture-of-experts training: MoE trains experts and router jointly from
  scratch, whereas MoErging learns routing post-hoc over experts trained independently by
  separate contributors.'
- The four router families identified in the MoErging survey are not a ranking; the survey
  describes each family's data requirements and applicable settings rather than naming a best
  approach.
- 'Not every MoErging method can be applied to adapters downloaded from a model hub: some
  require a custom expert training procedure and others require the expert training datasets
  to be shared.'
- The MoErging survey's claim that few methods are used in practice is about adoption and
  tooling, not a finding that the methods fail to improve performance.
terminology:
  MoErging: A paradigm in which expert models fine-tuned independently by decentralized contributors
    are recycled into an aggregate system by learning a router that selects and combines them
    per query or per task.
  Routing dataset: The data used to build or train the router over expert models, categorized
    as the experts' own training data, a target-task dataset, a general multi-task dataset,
    or none for methods that train no router.
  Routing input granularity: 'How often a routing decision is made over experts: once per
    task, once per input example, or at every generation step or token.'
  Routing depth granularity: Whether a single routing decision selects experts for the whole
    model, or an independent decision is made at each layer or module where experts are inserted.
  Expert aggregation: How information from multiple selected experts is combined — mixing
    their outputs, merging their parameters into one model before processing the input, or
    no aggregation when a single expert is selected.
  Router-free approaches: Expert-routing methods that derive routing from precomputed gates,
    expert parameter prototypes, or a pre-trained LLM's knowledge of expert descriptions,
    instead of training a dedicated router post hoc.
  Expert data privacy (Shared vs Private): Whether a method requires contributors to release
    the datasets their experts were trained on, or works from expert parameters alone.
links_extra:
  paper list: https://github.com/pclucas14/awesome-moerging
---
