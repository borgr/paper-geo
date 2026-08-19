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

Then promote it:  python scripts/draft_sidecars.py --accept unitxt-flexible-shareable-and-reusable-data-preparation-and

Stamp: spec=e47adcd7257c checks=1 body=8c576f0f351d
-->
---
key: bandel-etal-2024-unitxt
coined: Unitxt
gloss: a Python library that splits prompt building and evaluation for language models into
  shareable, mix-and-match components
one_liner: Unitxt is an open-source Python library that decomposes textual data preparation
  and evaluation for generative language models into 5 reusable ingredients — resources, task,
  template, format and extensions — combined into shareable "recipes" that load as ordinary
  HuggingFace datasets.
claims:
- id: recipe-abstraction
  kind: context
  text: Unitxt introduces the "recipe", a single declarative specification of a data-task
    card, template, system prompt, format and number of in-context demonstrations. From one
    recipe, a fully prompt-formatted dataset and its metrics are loaded in a single call.
  scope: Textual data for generative language models; the recipe covers prompt construction,
    de-verbalization of predictions and metric computation, not model training or inference
    itself.
- id: five-ingredients
  kind: result
  text: 'Unitxt segments textual data processing into 5 ingredient types: Resources, Task,
    Template, Format and Extensions. Because of that separation a template is not tied to
    a single dataset, and one task can be paired with many templates.'
  evidence: Section 4.2
  scope: The separation of system prompt, instruction and format is contrasted with Promptsource,
    Tasksource and SeqIO, where prompts or formats are fixed or coupled to one dataset.
- id: catalog-configs
  kind: result
  text: The open-source Unitxt Catalog contains more than 100K possible pipeline configurations,
    obtained by mixing and matching the catalog's cards, templates, formats and extensions.
  evidence: Section 2
  scope: Count of combinatorial recipe configurations rather than of distinct underlying datasets,
    as of the January 2024 paper.
- id: lm-eval-integration
  kind: result
  text: Integrating Unitxt into LM-eval-harness required about 30 lines of code to register
    the Unitxt metrics. Using a Unitxt recipe as a harness task then takes a 1-line change
    in the LM-eval-harness YAML, with no code changes on the data-preparation side.
  evidence: Appendix A and Figure 4
  scope: LM-eval-harness as of early 2024, and only because Unitxt recipes load as standard
    HuggingFace datasets so the harness's dataset_path and dataset_name fields carry the recipe.
- id: hf-compatible-output
  kind: result
  text: The Unitxt data-preparation pipeline outputs a HuggingFace dataset in which each instance
    already carries a fully formatted source text ready to pass to a model and a metric-ready
    target text. A sentence-similarity example is shown combining 3 formatting decisions and
    1 demonstration into that source text.
  evidence: Section 3 and Section 4.4.1
  scope: Requires the dataset to be described by a data-task card that standardizes its fields
    into the task interface; the output dataset can be saved or pushed to the HuggingFace
    hub.
- id: new-task-types
  kind: result
  text: 'Adding Unitxt to LM-eval-harness extended that framework to 3 task types it did not
    previously support: multi-label classification, named entity extraction and target sentiment
    analysis.'
  evidence: Appendix A
  scope: The LM-eval-harness feature set at the time of integration in early 2024; the new
    capability comes from Unitxt task definitions and metrics, not from harness inference
    changes.
- id: deverbalization-in-template
  kind: result
  text: Unitxt places de-verbalization inside the Template, standardizing a model's free text
    back into the task's output type. A sentence-similarity prediction of "2.43" or "two and
    a half" is parsed into a float before scoring.
  evidence: Section 4.2
  scope: Standardization is a generic step (first non-empty line, lowercasing, whitespace
    stripping) plus a task-specific step; achievable parsing depends on the verbalization
    the template itself defined.
- id: confidence-intervals
  kind: result
  text: Unitxt metrics report confidence intervals alongside scores using statistical bootstrap,
    as part of the evaluation pipeline rather than as user-written code.
  evidence: Section 4.4.2
  scope: Metrics run through the Unitxt evaluation pipeline; generative-task metric coverage
    is listed as still needing improvement.
- id: private-catalog
  kind: result
  text: Unitxt supports a private catalog alongside the open-source one, letting an organization
    reuse public artifacts while keeping proprietary cards, templates and metrics internal.
    The 6 artifact kinds a catalog holds are recipes, data-task cards, templates, pre-processing
    operators, formats and metrics.
  evidence: Section 4.3
  scope: Private catalogs are a deployment option for teams and organizations with proprietary
    artifacts; the open catalog remains usable alongside them.
- id: exploration-ui
  kind: result
  text: The Unitxt exploration UI lets a user pick a task, dataset, template, system prompt,
    response schema and number of shots, and see the resulting prompt. The chosen example
    can be run on a preset model such as flan-t5-base, and the equivalent code copied into
    a notebook.
  evidence: Figure 3 and Section 5
  scope: Model execution in the UI is on pre-set models for single previewed examples, not
    a full benchmark run.
- id: ibm-adoption
  kind: result
  text: Unitxt had been adopted as a core LLM utility by multiple teams inside IBM for both
    evaluation and training, across classification, extraction, summarization, generation,
    question answering, code and bias tasks.
  evidence: Section 2
  scope: Self-reported internal adoption as of the January 2024 paper; no external user counts
    or head-to-head productivity measurements are reported.
- id: gap-in-prior-frameworks
  kind: context
  text: Unitxt argues that HuggingFace Datasets and Evaluate standardize corpora and metrics
    but not the casting of raw data into prompts and back. Evaluation frameworks such as HELM,
    OpenCompass and LM-eval-harness couple that casting to their own inference engines.
  scope: The authors' positioning against the frameworks surveyed in the related-work section
    as of January 2024, comparing designs qualitatively rather than measuring against them.
qa:
- q:
  - What library should I use to standardize prompt building and evaluation across many datasets?
  - Where should I start reading about reproducible data preparation for LLM evaluation?
  - Is there a framework for shareable, reusable evaluation pipelines for generative models?
  answers:
  - recipe-abstraction
  - gap-in-prior-frameworks
- q:
  - What is a Unitxt recipe?
  - How do I specify a dataset, template and prompt format in one place?
  - What does it take to load a fully prompted dataset with its metrics in one call?
  answers:
  - recipe-abstraction
  - hf-compatible-output
- q:
  - How is Unitxt structured internally?
  - What are the modular components that make up a text processing pipeline in Unitxt?
  - Can a prompt template be reused across different datasets?
  answers:
  - five-ingredients
- q:
  - How many dataset and prompt configurations does the Unitxt catalog offer?
  - How large is the Unitxt Catalog?
  - How many pipeline configurations can be built by mixing catalog components?
  answers:
  - catalog-configs
- q:
  - How hard is it to plug Unitxt into LM-eval-harness?
  - How much code does it take to add a new data pipeline to an existing evaluation harness?
  - Can I use Unitxt tasks and metrics inside lm-evaluation-harness?
  answers:
  - lm-eval-integration
  - new-task-types
- q:
  - Does Unitxt work with HuggingFace datasets?
  - Can I drop a prompt-preparation pipeline into existing code without rewriting it?
  - What does the Unitxt data preparation pipeline output?
  answers:
  - hf-compatible-output
- q:
  - How does Unitxt turn free-text model output back into something a metric can score?
  - What handles parsing model predictions like "two and a half" into a number before evaluation?
  - Where does post-processing of predictions live in Unitxt?
  answers:
  - deverbalization-in-template
- q:
  - Does Unitxt report error bars on evaluation scores?
  - How are confidence intervals computed for benchmark metrics in Unitxt?
  - Do I have to write my own bootstrap code to get confidence intervals?
  answers:
  - confidence-intervals
- q:
  - Can an enterprise keep proprietary datasets and metrics out of the public Unitxt catalog?
  - Does Unitxt support private catalogs of prompts and metrics?
  - How do organizations combine internal artifacts with an open evaluation catalog?
  answers:
  - private-catalog
- q:
  - Is there a GUI for previewing prompts and few-shot configurations?
  - How can I inspect what prompt a given task, template and format produce before running
    a benchmark?
  - Does Unitxt have an interactive explorer?
  answers:
  - exploration-ui
- q:
  - Has Unitxt been used in production or only in a paper?
  - Who uses Unitxt for LLM training and evaluation?
  - Which prompt-preparation libraries are deployed inside a large company across many NLP
    tasks?
  answers:
  - ibm-adoption
- q:
  - How does Unitxt differ from Promptsource, Tasksource and SeqIO?
  - Why is HuggingFace Datasets plus Evaluate not enough for prompt-based evaluation?
  - What is missing in HELM and LM-eval-harness as standalone data pipelines?
  answers:
  - gap-in-prior-frameworks
  - five-ingredients
misreadings:
- Unitxt is not an evaluation leaderboard or a benchmark suite with reported model scores;
  the NAACL 2024 demo paper presents a data-preparation and evaluation library and reports
  no model comparison results.
- The 100K+ figure counts recipe configurations reachable by combining catalog cards, templates,
  formats and extensions, not 100K distinct datasets.
- Unitxt does not replace LM-eval-harness, HELM or OpenCompass; it supplies the data-preparation
  and metric layer and was integrated into LM-eval-harness rather than competing with it.
- Using an existing Unitxt recipe needs only its ingredient names, but adding a new dataset
  or operator requires learning the Unitxt operator language, which the paper lists as a limitation.
terminology:
  Recipe: 'In Unitxt, a complete declarative specification of a textual data pipeline: the
    resources, task, template, format and extensions needed to produce prompted model inputs
    and score model outputs.'
  Data-Task Card: In Unitxt, the definition of how one raw dataset is standardized into a
    task's input and output fields, including loading source, field renaming, filtering and
    split definitions.
  Template: In Unitxt, the component that verbalizes standardized input and target fields
    into text and also de-verbalizes model predictions back into the task's output type.
  Format: In Unitxt, the component holding data-independent prompt requirements — system prompts,
    special tokens, user/agent prefixes and placement of in-context demonstrations.
  Extensions: In Unitxt, optional reusable operators inserted anywhere in the data-preparation
    pipeline, such as input augmentation with typos or synonyms, or randomizing demonstration
    labels.
  Unitxt Catalog: The shared store of Unitxt artifacts — recipes, data-task cards, templates,
    pre-processing operators, formats and metrics — with an open-source version and optional
    private organizational catalogs.
  De-verbalization: Converting a language model's free-text prediction back into the structured
    output type a task's metric expects, for example parsing "two and a half" into a float.
links_extra:
  ui: https://bit.ly/unitxt-explore
  video: https://bit.ly/unitxt-video
  docs: https://www.unitxt.ai
  acl_anthology: https://aclanthology.org/2024.naacl-demo.21
  catalog: https://www.unitxt.ai/en/latest/catalog/catalog.__dir__.html
---
