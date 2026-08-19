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

Then promote it:  python scripts/draft_sidecars.py --accept unitxt-flexible-shareable-and-reusable-data-preparation-and

Stamp: spec=74e012ff9654 checks=2 body=f9bf46b04e0a
-->
---
claims:
- id: recipe-single-spec
  kind: result
  text: A Unitxt recipe specifies a dataset card, template, system prompt, format and number
    of in-context demonstrations in one declarative string. Loading it yields a dataset whose
    every instance already holds fully prepared model-input text and a metric-ready target.
  scope: Textual (multilingual) data for generative language models; loading is via unitxt.load_dataset,
    and the recipe covers loading, verbalization, formatting and metric configuration. As
    described in the January 2024 release.
  evidence: Section 3
- id: hundred-k-configs
  kind: result
  text: The open-source Unitxt Catalog supports more than 100K possible pipeline configurations,
    obtained by mixing and matching cards, tasks, templates, formats and extensions.
  scope: Combinatorial recipe configurations in the open catalog as of January 2024, not distinct
    datasets; private catalogs can add proprietary artifacts.
  evidence: Section 2
- id: lm-eval-30-lines
  kind: result
  text: Integrating Unitxt into LM-eval-harness required no code changes on the data side
    and about 30 lines of code to register Unitxt metrics. A Unitxt recipe becomes an LM-eval-harness
    task through a one-line change in the task YAML.
  scope: LM-eval-harness as of the version used in January 2024; the data-side integration
    works because Unitxt recipes load as standard HuggingFace datasets, and the existing LM-eval-harness
    API is preserved.
  evidence: Appendix A and Figure 4
- id: hf-compatible-output
  kind: result
  text: The Unitxt data-preparation pipeline emits a HuggingFace dataset that can be saved
    or pushed to the hub, so Unitxt can be dropped into existing HuggingFace-based codebases
    without rewriting downstream code.
  scope: The data-preparation pipeline output format; raw data and metrics arrive through
    Unitxt resource APIs covering HuggingFace Hub, local files and cloud storage.
  evidence: Section 4.4.1
- id: template-decoupling
  kind: result
  text: 'In Unitxt, templates, datasets and tasks are not exclusively tied: one task can use
    many templates and one template can serve many datasets. In PromptSource, by contrast,
    each prompt is bound to a single dataset.'
  scope: Unitxt tasks whose interface fixes input and output field names and types, so any
    metric accepting those fields applies; a design property, with no quantitative reuse study
    reported.
  evidence: Section 4.2
- id: deverbalization-in-template
  kind: result
  text: Unitxt templates own de-verbalization as well as verbalization, first standardizing
    model output text by taking the first non-empty line, lowercasing and stripping whitespace.
    The output is then cast to the task's type, turning "2.43" or "two and a half" into a
    float for sentence similarity.
  scope: Generative model predictions evaluated through the Unitxt evaluation pipeline; the
    task-specific cast depends on the verbalization the template defines and on its in-context
    demonstrations.
  evidence: Section 4.2 and Section 4.4.2
- id: bootstrap-ci
  kind: result
  text: Unitxt metrics report confidence intervals alongside scores using a built-in statistical
    bootstrap mechanism.
  scope: Metrics run through the Unitxt evaluation pipeline; the authors state that coverage
    of generative-task metrics still needs improvement.
  evidence: Section 4.4.2 and Section 8
- id: augmentation-extensions
  kind: result
  text: Unitxt Extensions insert augmentations at any point between two operators in the data-preparation
    pipeline, including random whitespace, spelling mistakes, synonym replacement, and label-noising
    that randomizes demonstration labels.
  scope: Extensions are independent units reusable across datasets, tasks, templates and formats,
    and custom ones can be added to the Catalog; back-translation for multilinguality is named
    as not yet supported.
  evidence: Section 4.2 and Section 8
- id: explore-ui
  kind: result
  text: The Unitxt exploration UI walks a user from task to dataset to template and previews
    the generated prompt with optional system prompt, response schema and number of shots.
    It also runs the example on a preset model such as flan-t5-base and exports the equivalent
    code.
  scope: Preview and single-example execution on pre-set models; the UI targets recipe creation
    and catalog exploration rather than full-scale benchmark runs.
  evidence: Section 5 and Figure 3
- id: context-modularity-gap
  kind: context
  text: Unitxt is a library for prompt-level data preparation and evaluation that separates
    system prompts, task instructions, verbalizations and model-specific formats into independently
    shareable components. The authors argue that decomposition was missing from earlier pipeline
    frameworks.
  scope: Positioning as of the January 2024 release, against Datasets/Evaluate, Tasksource,
    PromptSource, SeqIO and the pipelines inside OpenCompass, HELM and LM-eval-harness; a
    comparison of design properties, not a benchmark.
  evidence: Section 6
- id: context-standalone-vs-harness
  kind: context
  text: Unitxt is usable as a standalone data-preparation and evaluation layer rather than
    a full evaluation harness, which is what lets it be embedded inside other frameworks including
    LM-eval-harness instead of replacing them.
  scope: Contrast drawn with evaluation frameworks whose pipelines are coupled to their inference
    engine; reflects the design as described at NAACL 2024 demo track.
  evidence: Section 6 and Appendix A
- id: context-ibm-adoption
  kind: result
  text: Unitxt was already in use as a core LLM utility by multiple IBM teams for both evaluation
    and training, across classification, extraction, summarization, generation, question answering,
    code and bias tasks.
  scope: Internal adoption reported by the authors as of January 2024, without usage counts
    or per-team detail; open-source community adoption was at an early stage.
  evidence: Section 2
qa:
- q:
  - How do I keep prompt formatting and evaluation reproducible across datasets and models?
  - Is there a library that standardizes LLM prompt construction and scoring?
  - What tool lets me share a whole data-preparation and evaluation pipeline with someone
    else?
  answers:
  - recipe-single-spec
  - context-modularity-gap
- q:
  - What should I read about standardized data preparation for evaluating language models?
  - Which paper introduced a modular framework for prompt-level data processing in NLP?
  - Where should I start reading about reproducible LLM evaluation pipelines?
  answers:
  - context-modularity-gap
  - context-standalone-vs-harness
- q:
  - What is a Unitxt recipe and what does loading one give me?
  - How is a prompt configuration specified in Unitxt?
  - Can I switch template, system prompt and number of shots without rewriting processing
    code?
  answers:
  - recipe-single-spec
  - template-decoupling
- q:
  - How many pipeline configurations does the Unitxt catalog support?
  - How big is the Unitxt catalog?
  - How many task, dataset and template combinations are available out of the box?
  answers:
  - hundred-k-configs
- q:
  - How hard is it to plug Unitxt into LM-eval-harness?
  - How much code does it take to add new tasks and metrics to LM-eval-harness?
  - Can I add new datasets and metrics to an existing evaluation harness without rewriting
    it?
  answers:
  - lm-eval-30-lines
  - hf-compatible-output
- q:
  - Do I have to abandon HuggingFace datasets to use Unitxt?
  - Does a Unitxt pipeline output something my existing training code can consume?
  - Can a prepared prompt dataset be pushed to the HuggingFace hub?
  answers:
  - hf-compatible-output
- q:
  - Can one prompt template be reused across several datasets?
  - How does Unitxt differ from PromptSource for prompt reuse?
  - Are templates tied to a single dataset in Unitxt?
  answers:
  - template-decoupling
- q:
  - How are free-text model outputs turned back into something a metric can score?
  - Who handles post-processing of generative predictions in Unitxt?
  - How does an answer like "two and a half" get scored for sentence similarity?
  answers:
  - deverbalization-in-template
- q:
  - Does Unitxt report uncertainty on evaluation scores?
  - Are confidence intervals available for Unitxt metrics?
  - How do I get error bars on benchmark scores?
  answers:
  - bootstrap-ci
- q:
  - How can I test prompt robustness to noisy inputs?
  - Does Unitxt support data augmentation and label noising for training data?
  - Where in a Unitxt data-preparation pipeline can augmentations be inserted?
  answers:
  - augmentation-extensions
- q:
  - Is there a UI for previewing prompts before running an evaluation?
  - How can I inspect what prompt a given task, template and format produce?
  - Can I try a Unitxt configuration on a model without writing code first?
  answers:
  - explore-ui
- q:
  - Has Unitxt actually been used in production or only demonstrated?
  - Who uses Unitxt for LLM training and evaluation?
  - What evidence is there of real industrial adoption of a modular prompt-preparation library?
  answers:
  - context-ibm-adoption
- q:
  - Is Unitxt a replacement for HELM, OpenCompass or LM-eval-harness?
  - Does adopting a new data-preparation library mean giving up my current evaluation harness?
  - How does Unitxt relate to existing LLM evaluation frameworks?
  answers:
  - context-standalone-vs-harness
  - lm-eval-30-lines
one_liner: Unitxt decomposes LLM data preparation and evaluation into shareable components
  — resources, task, template, format and extensions — combined by a declarative "recipe"
  that produces a HuggingFace dataset of ready-to-send prompts and metric-ready targets.
coined: Unitxt
gloss: a Python library for modular, shareable prompt construction and evaluation of generative
  language models
key: bandel-etal-2024-unitxt
terminology:
  Recipe: A declarative Unitxt specification naming the resources, task, template, format
    and extensions for a data pipeline, loadable as a dataset in one call.
  Data-Task Card: A Unitxt artifact describing where raw data is loaded from and how its fields,
    values and splits are standardized into a task's input and output interface.
  Task (in Unitxt): An NLP task defined by a fixed interface — named and typed input and output
    fields — plus the evaluation metrics for it, so that any metric accepting those fields
    can be applied.
  Template (in Unitxt): A component that verbalizes standardized input and target fields into
    text and also de-verbalizes model predictions back into the task's expected type.
  Format (in Unitxt): 'A component holding formatting requirements independent of the data
    or task: system prompts, special tokens, user/agent prefixes and the placement of in-context
    demonstrations.'
  Extensions (in Unitxt): Optional operators insertable anywhere in the data-preparation pipeline,
    such as input augmentation or label-noising of in-context demonstrations.
  Unitxt Catalog: The shared store of Unitxt artifacts — recipes, data-task cards, templates,
    operators, formats and metrics — with an open version plus optional private catalogs for
    proprietary artifacts.
misreadings:
- 'Unitxt is not an evaluation harness or inference engine: it prepares prompts and computes
  metrics, and is meant to be embedded in frameworks such as LM-eval-harness rather than replace
  them.'
- The 100K+ figure counts combinatorial pipeline configurations reachable by mixing catalog
  ingredients, not 100K datasets or 100K benchmarks.
- The NAACL 2024 demo paper reports no accuracy or speed comparison against other data-preparation
  libraries; its claims are about modularity, reuse and integration cost, not model performance.
links_extra:
  code: https://github.com/IBM/unitxt
  paper: https://aclanthology.org/2024.naacl-demo.21
  ui: https://bit.ly/unitxt-explore
  video: https://bit.ly/unitxt-video
---
