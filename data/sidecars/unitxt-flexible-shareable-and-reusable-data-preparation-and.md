---
claims:
- id: recipe-single-spec
  kind: result
  text: A Unitxt recipe specifies a dataset card, template, system prompt, format and number
    of in-context demonstrations in one declarative string, and the open catalog's ingredients
    combine into more than 100K such recipes. Loading it yields a dataset whose every instance
    already holds fully prepared model-input text and a metric-ready target.
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
    or pushed to the hub, so Unitxt drops into existing HuggingFace-based codebases without
    rewriting downstream code. Integrating it into LM-eval-harness took about 30 lines of
    code, with one line changed per recipe in a yaml.
  scope: The data-preparation pipeline output format; raw data and metrics arrive through
    Unitxt resource APIs covering HuggingFace Hub, local files and cloud storage.
  evidence: Section 4.4.1
- id: template-decoupling
  kind: result
  text: 'In Unitxt, templates, datasets and tasks are not exclusively tied: one task can use
    many templates and one template can serve many datasets. In PromptSource, by contrast,
    each prompt is bound to a single dataset.'
  scope: Unitxt tasks whose interface fixes input and output field names and types, so any
    metric accepting those fields applies; templates and datasets drawn from the open catalog.
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
- ask:
    plain: Is there a library that turns a dataset plus a prompt wording into ready-to-score
      model inputs?
    jargon: Which framework decomposes prompt-level data preparation into shareable cards,
      templates, formats and system prompts?
    task: How do I hand a colleague my entire prompt-building and scoring setup as one shareable
      specification?
    practitioner: Should I adopt Unitxt instead of maintaining my own prompt formatting and
      metric code?
  answered_by:
  - recipe-single-spec
  - context-modularity-gap
- ask:
    plain: What paper should I read first about making language-model evaluation pipelines
      reproducible?
    jargon: Which work introduced a modular, catalog-based library for prompt-level data processing
      and LLM evaluation?
    task: Where do I start reading if I want to build a reproducible LLM evaluation pipeline?
    practitioner: I need a citable reference for reproducible prompt-level evaluation tooling
      — which one covers the modular pipeline design?
  answered_by:
  - context-modularity-gap
  - context-standalone-vs-harness
- ask:
    plain: How do you write down which wording, instruction and number of examples a prompt
      should use?
    jargon: How is a Unitxt recipe declared, and are templates bound to a single dataset or
      reusable across tasks?
    task: How do I swap the template, system prompt and shot count without editing my data-processing
      code?
    practitioner: Can I change prompt wording and in-context example count from a config string
      rather than rewriting my loader?
  answered_by:
  - recipe-single-spec
  - template-decoupling
- ask:
    plain: How many different prompt setups can you build from the ready-made pieces in the
      Unitxt catalog?
    jargon: How many pipeline configurations does the Unitxt Catalog yield by combining cards,
      tasks, templates, formats and extensions?
    task: How many dataset, task and prompt-format combinations can I get without authoring
      anything myself?
    practitioner: Is the Unitxt catalog big enough that my task and prompt format are probably
      already in it?
  answered_by:
  - hundred-k-configs
- ask:
    plain: How much work is it to make an existing evaluation harness use Unitxt data and
      metrics?
    jargon: What integration cost does adding Unitxt recipes and metrics to LM-eval-harness
      incur in lines of code?
    task: How do I add a new task and a new metric to LM-eval-harness without rewriting its
      data loading?
    practitioner: I already run LM-eval-harness — how disruptive is wiring Unitxt into it?
  answered_by:
  - lm-eval-30-lines
  - hf-compatible-output
- ask:
    plain: Does the prepared prompt data come out in a format ordinary training code can read?
    jargon: Does the Unitxt preparation pipeline emit a HuggingFace dataset that can be serialized
      or pushed to the hub?
    task: How do I get verbalized prompts into my existing HuggingFace training loop without
      writing a converter?
    practitioner: Can I use Unitxt-prepared prompts in my current HuggingFace training and
      inference code as-is?
  answered_by:
  - hf-compatible-output
- ask:
    plain: Can the same prompt wording be reused across several different datasets?
    jargon: Are Unitxt templates decoupled from datasets and tasks, unlike PromptSource's
      per-dataset prompt binding?
    task: How do I write one prompt template once and apply it to every dataset of the same
      task?
    practitioner: If I author 20 prompt templates, will I have to duplicate them per dataset?
  answered_by:
  - template-decoupling
- ask:
    plain: How does free-text model output get turned back into something a metric can actually
      score?
    jargon: Where does de-verbalization and type casting of generative predictions happen
      in a Unitxt pipeline?
    task: How do I post-process a model's answer like "two and a half" into a number my similarity
      metric can use?
    practitioner: Do I have to write my own output parser for each task, or does Unitxt handle
      prediction post-processing?
  answered_by:
  - deverbalization-in-template
- ask:
    plain: Do the evaluation scores come with any measure of uncertainty?
    jargon: Does Unitxt report bootstrap confidence intervals alongside metric scores?
    task: How do I get error bars on a benchmark score so I know whether two models really
      differ?
    practitioner: Can I report confidence intervals with my Unitxt evaluation numbers without
      coding a bootstrap myself?
  answered_by:
  - bootstrap-ci
- ask:
    plain: Can I deliberately add noise or typos to prompts to test how sensitive a model
      is?
    jargon: Can Unitxt Extensions inject augmentations such as spelling noise, synonym replacement
      or demonstration label noising at arbitrary points in the pipeline?
    task: How do I perturb prompts and corrupt in-context example labels to probe model robustness?
    practitioner: Do I need custom code to augment or label-noise my prompt data, or is it
      built in?
  answered_by:
  - augmentation-extensions
- ask:
    plain: Is there a way to see what a prompt will look like before running a whole evaluation?
    jargon: Does Unitxt ship an exploration UI that previews verbalized prompts and exports
      the equivalent recipe code?
    task: How do I preview a prompt with a chosen template and shot count, and try it on a
      model, before writing code?
    practitioner: Can I browse and test prompt configurations in a UI first and only then
      copy out the code?
  answered_by:
  - explore-ui
- ask:
    plain: Is the shared library for preparing prompts and evaluating language models actually
      used by people, or just described in a paper?
    jargon: What evidence of production adoption exists for Unitxt across LLM evaluation and
      training workloads?
    task: How do I tell whether Unitxt is mature enough to depend on for both training and
      evaluation work?
    practitioner: Is Unitxt used in real industrial LLM pipelines, and for which kinds of
      tasks?
  answered_by:
  - context-ibm-adoption
- ask:
    plain: Does using Unitxt mean giving up the evaluation harness I already run?
    jargon: Is Unitxt positioned as a standalone data-preparation and evaluation layer rather
      than a replacement evaluation harness?
    task: How do I add modular prompt preparation to my existing evaluation framework instead
      of switching frameworks?
    practitioner: Should I replace my current LLM evaluation harness with Unitxt, or embed
      Unitxt inside it?
  answered_by:
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
