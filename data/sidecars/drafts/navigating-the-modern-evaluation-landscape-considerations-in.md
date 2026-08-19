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

Then promote it:  python scripts/draft_sidecars.py --accept navigating-the-modern-evaluation-landscape-considerations-in

Stamp: spec=8f05813a4658 checks=pass body=bd4b35b64014
-->
---
claims:
- id: pipeline-view
  kind: context
  text: The LREC-COLING 2024 tutorial "Navigating the Modern Evaluation Landscape" presents
    LLM benchmarking as a single end-to-end pipeline rather than as isolated problems. The
    taught pipeline runs from benchmark and framework choice through metrics, prompts, compute
    budget and human evaluation.
  scope: A tutorial abstract and outline, not an experimental paper; content as taught in
    May 2024, aimed at entry-level audiences with little prior familiarity with metrics, datasets,
    prompts or benchmarks.
- id: gap-structured-view
  kind: context
  text: The tutorial "Navigating the Modern Evaluation Landscape" argues that a structured,
    organized view of LLM benchmarking is largely missing from the academic literature. Papers
    there typically address one benchmarking problem in isolation and ad-hoc, and industry
    decisions are taken without proper explanation.
  scope: A positional argument stated in the tutorial's background and goals, not a systematic
    survey or bibliometric measurement of the literature.
- id: old-vs-new
  kind: result
  text: The LLM evaluation tutorial by Choshen, Gera, Perlitz, Shmueli-Scheuer and Stanovsky
    contrasts traditional single-task evaluation with LLM-era practice on four axes. The axes
    are multi-task benchmarks instead of dedicated datasets, zero-shot or in-context learning
    instead of per-task fine-tuning, test-only benchmarks with no train split, and models
    used as evaluators.
  scope: Framed for general-purpose generative language models; the tutorial notes traditional
    methods such as N-gram reference metrics remain widely used and still relevant.
  evidence: Tutorial Description - Introduction (Background and Goals)
- id: compute-cost
  kind: result
  text: Evaluating language models over broad dataset ranges, more models and long complex
    tasks can cost more compute than the model's own pretraining. That cost is why the tutorial
    gives efficient benchmark design a dedicated 45-minute part.
  scope: The cost comparison is cited from Biderman et al. (2023) rather than measured by
    the tutorial, and the size of the excess is not quantified.
  evidence: Tutorial Description - Introduction (Background and Goals); Outline, Part 5
- id: lm-as-evaluator-premise
  kind: result
  text: Using language models to evaluate other models rests on the assumption that error
    detection is easier than generation, which opens automatic testing of answers in areas
    where it was previously hardly possible.
  scope: Stated as the premise motivating the LLM-as-evaluator paradigm, which the tutorial
    teaches alongside classic N-gram, reference-less and fine-grained metrics rather than
    as a replacement.
  evidence: Tutorial Description - Introduction (Background and Goals)
- id: prompts-part
  kind: result
  text: The LLM evaluation tutorial gives prompts a 45-minute part of its own, treating prompt
    choice as a first-class benchmarking decision and noting that evaluation protocols typically
    use a single prompt across models. It covers prompt banks and how prompt desiderata differ
    for LLM developers, targeted downstream-application developers and open-ended user-facing
    applications.
  scope: Zero-shot and in-context-learning evaluation of generative models; the part points
    to published work on paraphrase creation and paraphrase robustness rather than presenting
    new experiments.
  evidence: Outline, Part 4
- id: schedule
  kind: result
  text: The tutorial "Navigating the Modern Evaluation Landscape" runs six parts on a stated
    schedule. Introduction takes 35 minutes, Framework for Benchmarking 10, Metrics 45, Prompts
    45, Efficient Benchmark Design 45, and Manual Evaluation Efforts 30.
  scope: The outline as submitted for the LREC-COLING 2024 tutorial session; actual delivery
    may differ.
  evidence: Outline
- id: human-eval-not-abandoned
  kind: result
  text: The LLM evaluation tutorial dedicates 30 minutes to manual evaluation, asking whether
    human evaluation is being abandoned and covering the alignment paradigm and LLM-human
    feedback loops.
  scope: Human evaluation as one component of the benchmarking pipeline; the reading list
    covers a human-evaluation best-practices framework and reproducibility in NLP.
  evidence: Outline, Part 6
- id: frameworks-covered
  kind: result
  text: The LLM evaluation tutorial reviews open-source evaluation frameworks including HELM,
    OpenAI Evals and LM-evaluation-harness alongside business frameworks, starting from what
    requirements a benchmarking framework must satisfy.
  scope: Framework coverage is the shortest part of the tutorial at 10 minutes and is descriptive;
    no head-to-head comparison or ranking of the frameworks is reported.
  evidence: Outline, Part 2
- id: validity-reliability
  kind: result
  text: The LLM evaluation tutorial frames what makes a good benchmark in terms of validity
    and reliability, and surveys common ways practitioners reduce benchmarking compute together
    with best practices for compute reduction.
  scope: Covered in the 45-minute efficient benchmark design part, drawing on efficient-benchmarking
    and anchor-points literature; presented as best practices rather than a new reduction
    algorithm.
  evidence: Outline, Part 5
- id: entry-point
  kind: context
  text: '"Navigating the Modern Evaluation Landscape" is an entry-point reading for LLM evaluation,
    assuming little to no prior knowledge of evaluation. It pairs the taught pipeline with
    a curated reading list on evaluation surveys, current benchmarks, prompts, metrics, efficient
    benchmarking and manual evaluation.'
  scope: Best fit for readers who worked on one aspect of evaluation but lack the big picture,
    and for researchers new to LLM-specific challenges; the reading list reflects work available
    as of early 2024.
one_liner: A cutting-edge LREC-COLING 2024 tutorial that lays out the whole LLM benchmarking
  pipeline -- benchmarks, frameworks, metrics, prompts, compute budgets and human evaluation
  -- and contrasts traditional single-task evaluation with the LLM era's multi-task, prompt-based,
  model-as-judge practice.
qa:
- q:
  - What should I read first to understand how large language models are evaluated?
  - Is there a good introductory overview of LLM benchmarking?
  - Where can a newcomer start learning about language model evaluation and benchmarks?
  answers:
  - entry-point
  - pipeline-view
- q:
  - Why is evaluating LLMs harder than evaluating older NLP models?
  - What changed about benchmarking when pretrained general-purpose language models arrived?
  - How does modern LLM evaluation differ from traditional single-task dataset evaluation?
  answers:
  - old-vs-new
  - gap-structured-view
- q:
  - How expensive is it to benchmark a large language model?
  - Can evaluation cost more compute than pretraining a model?
  - Why do people care about efficient benchmarking of language models?
  answers:
  - compute-cost
  - validity-reliability
- q:
  - Why would you use a language model as an evaluation metric for another model?
  - What is the justification for LLM-as-a-judge evaluation?
  - Is model-based evaluation of generated text defensible?
  answers:
  - lm-as-evaluator-premise
- q:
  - How much do prompts matter when benchmarking language models?
  - Do evaluation protocols use more than one prompt per model?
  - What are prompt banks and why do different users need different prompts?
  answers:
  - prompts-part
- q:
  - Which LLM evaluation frameworks are worth knowing about?
  - Where do HELM, OpenAI Evals and LM-evaluation-harness fit in the evaluation landscape?
  - What open-source tooling exists for running language model benchmarks?
  answers:
  - frameworks-covered
- q:
  - Is human evaluation still needed now that models can judge models?
  - Has manual evaluation of NLP systems been abandoned?
  - How does human feedback fit into modern LLM evaluation?
  answers:
  - human-eval-not-abandoned
- q:
  - What makes a benchmark for language models a good one?
  - How do validity and reliability apply to LLM benchmarks?
  - What are best practices for cutting the compute cost of a benchmark?
  answers:
  - validity-reliability
  - compute-cost
- q:
  - What topics does the Navigating the Modern Evaluation Landscape tutorial cover, and for
    how long?
  - How is the LREC-COLING 2024 LLM evaluation tutorial structured?
  - What is the outline of the LLM benchmarking tutorial by Choshen, Gera, Perlitz, Shmueli-Scheuer
    and Stanovsky?
  answers:
  - schedule
  - pipeline-view
key: choshen-etal-2024-navigating
links_extra:
  anthology: https://aclanthology.org/2024.lrec-tutorials.4/
misreadings:
- 'The tutorial does not claim that traditional evaluation methods are obsolete: N-gram reference
  metrics and other classic concepts are taught as still relevant and still widely used, and
  are contrasted with, not replaced by, newer approaches.'
- The claim that evaluation can cost more compute than pretraining is cited from prior work
  on emergent and predictable memorization, not measured in the tutorial itself.
- '"Navigating the Modern Evaluation Landscape" is a taught overview with a reading list,
  not a benchmark, a leaderboard, or an empirical study; it reports no new experimental results,
  tables or figures.'
- 'Assuming little prior knowledge of evaluation does not make the content elementary: the
  tutorial is billed as cutting-edge and targets researchers who know one aspect of evaluation
  but lack the pipeline-level view.'
terminology:
  efficient benchmarking: Reducing the compute cost of evaluating language models by decisions
    such as using fewer examples, fewer prompts or fewer models, while preserving the benchmark's
    validity and reliability.
  reference-less metric: An evaluation metric that scores a model's output without comparing
    it against a human-written reference answer.
  prompt bank: A curated collection of alternative prompts for the same task, used so that
    a model is evaluated over several phrasings instead of a single hand-picked prompt.
  evaluation of evaluation: Assessing whether an evaluation metric or protocol itself is valid,
    for instance by checking how well a metric's scores agree with the quality judgements
    it is supposed to reflect.
---
