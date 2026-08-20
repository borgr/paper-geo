---
claims:
- id: taxonomy-nine-axes
  kind: context
  text: The MoErging survey introduces a taxonomy that catalogues each surveyed method along
    9 design choices. The axes are expert training procedure and expert data privacy, then
    routing dataset, input granularity, depth granularity, expert selection and expert aggregation,
    then generalization target and user dataset requirement.
  scope: Covers methods surveyed as of the 2024 arXiv release and 2025 TMLR publication; some
    papers map onto an axis only as 'Multiple' or 'N/A', and the authors state the taxonomy
    may miss methods and design choices.
  evidence: Figure 5 and Sections 2.1-2.3
- id: four-categories
  kind: result
  text: 'MoErging methods fall into 4 families by how the router is built: embedding-based
    routing, classifier-based routing, task-specific routing, and router-free approaches.
    The remaining differences in granularity, selection and aggregation are comparatively
    superficial.'
  scope: A grouping the survey argues for over the few dozen methods it reviews in Section
    4; methods that mix strategies fit the grouping less cleanly.
  evidence: Sections 3.1-3.5
- id: no-mutual-comparison
  kind: result
  text: 'MoErging papers rarely compare to one another: among the 7 embedding-based routing
    methods the survey lists, only LoraRetriever compares against AdapterSoup. Most surveyed
    papers cite only a small fraction of the others.'
  scope: Based on the papers catalogued in Section 4 as of the survey's writing; the observation
    is about published comparisons, not about whether the methods are comparable in principle.
  evidence: Sections 3.1 and 3.5
- id: missing-baselines
  kind: result
  text: When a MoErging method assumes all expert training datasets are simultaneously available,
    multitask training of the base model on those expert datasets is an applicable baseline
    that is often omitted. Multitask mixture-of-experts methods likewise become valid baselines
    under shared expert data.
  scope: Methods whose taxonomy entry lists expert data as Shared; methods that keep expert
    data Private cannot be compared to a multitask baseline on the same terms.
  evidence: Sections 3.5 and 5.2
- id: data-access-gates-applicability
  kind: result
  text: 'Data-access assumptions decide which MoErging methods are usable at all: a method
    requiring a labeled target-task dataset cannot by definition improve zero-shot generalization.
    A method requiring shared expert training data cannot be applied to publicly shared adapters,
    which are seldom released with their training data.'
  scope: A logical consequence of the survey's taxonomy axes for routing dataset, expert data
    and user dataset, stated over the methods catalogued in Section 4.
  evidence: Section 3.5
- id: little-practical-use
  kind: result
  text: Very few of the MoErging methods catalogued in the survey are actually used in practice,
    despite many demonstrating improved performance or generalization. The survey attributes
    this to missing user-friendly implementations, unclear guidance on which method suits
    which use case, and assumptions such as custom expert training or shared expert data.
  scope: An assessment as of publication; the attributed causes are the authors' speculation
    rather than a measured result, and the tools inventory in Section 6 shows supporting infrastructure
    does exist.
  evidence: Section 7
- id: moerging-vs-moe-vs-merging
  kind: context
  text: MoErging learns post-hoc routing over independently trained, decentralized experts
    and combines them adaptively per query or per task. That separates it from mixture-of-experts
    models, which jointly train experts and router from scratch, and from model merging, which
    produces a static combination.
  scope: The survey's own delineation; the authors note that precisely delineating what is
    and is not MoErging is challenging because adjacent methods share the motivation while
    differing in framing.
  evidence: Section 1 and Sections 5.2-5.3
- id: granularity-tradeoff
  kind: result
  text: 'Routing granularity trades adaptability against cost and stability across the 3 levels
    the MoErging taxonomy defines: per-task, per-example and per-step. Per-step routing adapts
    most to the input but is expensive and risks early routing errors propagating, while per-task
    routing is cheapest and assumes constant expert needs within a task.'
  scope: A synthesis of trade-offs across the surveyed methods rather than a controlled experiment;
    the same error-propagation concern is raised for per-module routing depth.
  evidence: Sections 2.2.2 and 2.2.3
- id: embedding-router-strength
  kind: result
  text: Embedding-based routers, the 7 of which the survey lists include AdapterSoup, Retrieval
    of Experts, LoraRetriever and Dynamic Adapter Merging, need little or no routing-specific
    training data and tolerate experts with different architectures. Their quality is bounded
    by the pre-trained embedding space and degrades on semantically subtle, highly specialized,
    or out-of-distribution tasks.
  scope: The embedding-based family as characterised in the survey's grouping; assumes expert
    training distributions are distinct enough to separate in embedding space.
  evidence: Section 3.1
- id: classifier-router-tradeoff
  kind: result
  text: Classifier-based routers, the 5 of which the survey lists are Zooter, RouteLLM, Routoo,
    Branch-Train-Mix and Routing with Benchmark Datasets, can learn routing functions more
    complex than embedding similarity. They depend on labeled routing data and therefore lose
    applicability in zero-shot and few-shot settings.
  scope: The classifier-based family; the labeled data may come from expert data, a general
    dataset, or the target task, and the constraint is data availability rather than accuracy.
  evidence: Section 3.2
- id: router-free-zero-shot
  kind: result
  text: Router-free approaches such as Arrow, PHATGOOSE, Airoboros and LlamaIndex avoid post-hoc
    router training entirely, using precomputed gates, LoRA prototypes or a pre-trained LLM's
    own knowledge. That gives zero-shot deployment with no routing data, at the cost of possibly
    modified expert training and less stable routing.
  scope: The router-free family in the survey's grouping; PHATGOOSE and Arrow require expert-side
    changes or precomputation, so 'no training' refers to the router, not the experts.
  evidence: Section 3.4
- id: tools-inventory
  kind: context
  text: The MoErging survey inventories the software ecosystem for decentralized expert reuse,
    including Hugging Face PEFT, AdapterHub, Git-theta, MergeKit, Predibase's Lorax, Mergoo,
    Flow-Merge, Axolotl, Unsloth, airoboros and ComfyUI. It notes that no existing platform
    coordinates continual communal model development.
  scope: An inventory as of publication; the tool landscape changes quickly and the survey
    does not benchmark the tools against one another.
  evidence: Section 6
- id: open-problems
  kind: context
  text: The MoErging survey names as open problems identifying and removing redundant experts,
    deciding whether to admit a new expert to the pool, and detecting maliciously contributed
    experts. It also asks whether repeated rounds of MoErging can continually improve a base
    model rather than giving one-off gains.
  scope: Directions the authors identify as of publication, alongside a call for theoretical
    frameworks and for merging-style benchmarks and competitions; none are addressed experimentally
    in the survey.
  evidence: Section 7
qa:
- q:
  - What should I read first about routing among fine-tuned expert models?
  - Is there a survey on reusing LoRA adapters and expert models with a learned router?
  - Where can I find an overview of MoErging methods?
  - What paper organizes the literature on recycling specialized expert models?
  answers:
  - taxonomy-nine-axes
  - four-categories
  - moerging-vs-moe-vs-merging
- q:
  - How is MoErging different from mixture-of-experts?
  - What distinguishes routing among independently trained experts from model merging?
  - Is combining fine-tuned adapters with a router the same thing as a sparse MoE model?
  answers:
  - moerging-vs-moe-vs-merging
- q:
  - What are the main ways of building a router over pre-trained experts?
  - How can methods for selecting among fine-tuned experts be categorized?
  - What families of expert-routing methods exist?
  answers:
  - four-categories
  - embedding-router-strength
  - classifier-router-tradeoff
  - router-free-zero-shot
- q:
  - Which expert-routing approach works without any labeled routing data?
  - What method should I use for zero-shot routing among adapters?
  - Can I route among LoRA experts without training a router?
  answers:
  - router-free-zero-shot
  - embedding-router-strength
- q:
  - When does a learned classifier router beat embedding similarity for expert selection?
  - What are the drawbacks of training a dedicated router to pick among LLMs?
  - Do classifier-based LLM routers like RouteLLM need labeled data?
  answers:
  - classifier-router-tradeoff
  - embedding-router-strength
- q:
  - Should routing among experts happen per token, per example, or per task?
  - What is the cost of fine-grained routing decisions in adapter mixtures?
  - How does routing granularity affect adaptability and compute?
  answers:
  - granularity-tradeoff
- q:
  - Why is it so hard to compare methods that route among fine-tuned experts?
  - Do MoErging papers evaluate against each other?
  - Are expert-routing methods benchmarked in a consistent setup?
  answers:
  - no-mutual-comparison
  - data-access-gates-applicability
- q:
  - What baseline is often missing from papers that route among expert adapters?
  - If all expert training datasets are available, what should a routing method be compared
    to?
  - When is plain multitask training a fair baseline for expert recycling methods?
  answers:
  - missing-baselines
- q:
  - Does needing the experts' training data limit which routing methods I can use?
  - Can a routing method that requires a labeled target-task set improve zero-shot performance?
  - What assumptions rule out applying an expert-routing method to adapters downloaded from
    a model hub?
  answers:
  - data-access-gates-applicability
- q:
  - Are methods for recycling fine-tuned experts actually used in production?
  - Why has adaptive routing among community adapters not been widely adopted?
  - What is holding back practical adoption of expert-recycling systems?
  answers:
  - little-practical-use
  - tools-inventory
- q:
  - What software exists for merging and routing among expert models?
  - Which libraries support building a mixture over LoRA adapters?
  - Are there tools for decentralized sharing and combination of fine-tuned models?
  answers:
  - tools-inventory
- q:
  - What are the open research problems in recycling and routing among expert models?
  - How do you handle redundant or malicious contributed experts in a shared expert pool?
  - What future work is needed for decentralized collaborative model development?
  answers:
  - open-problems
  - little-practical-use
- q:
  - What design choices should I document when proposing a new expert-routing method?
  - Which axes describe how a router over fine-tuned experts is built and applied?
  - How do I classify a MoErging method's assumptions about expert data and user data?
  answers:
  - taxonomy-nine-axes
  - data-access-gates-applicability
one_liner: A survey of model MoErging — recycling independently trained expert models via
  a learned router — that catalogues a few dozen methods along a 9-axis taxonomy of expert,
  routing and application design choices, and groups them into embedding-based, classifier-based,
  task-specific and router-free routing.
coined: MoErging
gloss: recycling independently fine-tuned expert models by learning a router that picks and
  combines them per query or per task
key: yadav2025moerging
terminology:
  MoErging: A paradigm in which expert models fine-tuned independently by distributed contributors
    are recycled into an aggregate system by learning a post-hoc router that adaptively selects
    and combines them per query or per task.
  Expert data (Shared vs Private): A taxonomy axis recording whether a routing method requires
    contributors to release the expert models' training datasets (Shared) or can operate on
    the expert parameters alone (Private).
  Routing dataset: The data used to learn the router, categorized as the experts' own training
    data, a target-task dataset, a general multi-task dataset, or none for methods that use
    heuristics or precomputed information instead of router training.
  Routing input granularity: Whether a routing decision is made once per task, once per input
    example, or at every generation step or token.
  Routing depth granularity: Whether one routing decision applies to the whole model or an
    independent decision is made at each layer or module where experts are inserted.
  Expert aggregation: 'How multiple selected experts are combined: mixing their outputs, merging
    their parameter values into a single model before processing the input, or no aggregation
    when a single expert is selected.'
  Router-free approaches: Expert-selection methods that determine expert choice from precomputed
    gates, LoRA prototypes or a pre-trained LLM's knowledge, without training a dedicated
    router after the experts exist.
misreadings:
- 'The MoErging survey is not a benchmark: it catalogues design choices and reports what each
  paper claims, and it does not run head-to-head experiments comparing the surveyed methods
  under a common setup.'
- MoErging is not a synonym for model merging. Merging produces a static combination of parameters,
  whereas MoErging routes adaptively per query or per task, and the survey treats merging
  as a non-adaptive baseline for MoErging methods.
- 'Not every MoErging method can be applied to adapters downloaded from a model hub: methods
  labelled Custom expert training require a modified training procedure, and methods labelled
  Shared expert data require the experts'' training datasets, which are rarely released.'
- The four-way grouping into embedding-based, classifier-based, task-specific and router-free
  routing is an organizing claim about how routers are built, not a ranking; the survey does
  not name a best family and argues suitability depends on data access and generalization
  goal.
- 'Zero-shot in the survey''s user-dataset axis is a slight misnomer: it also covers methods
  that need an unlabeled target-task training set, such as Weight-Ensembling MoE, which tunes
  its router by minimizing routing entropy on unlabeled test data.'
links_extra:
  paper list repo: https://github.com/pclucas14/awesome-moerging
---
