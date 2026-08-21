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
- ask:
    plain: what should I read first to understand how language models are benchmarked?
    jargon: is there a tutorial that surveys LLM evaluation end to end for someone with no
      evaluation background?
    task: how do I get up to speed on language model benchmarking from scratch?
    practitioner: I need to set up evaluation for our models and know nothing about benchmarks
      -- where do I start?
  answered_by:
  - entry-point
  - pipeline-view
- ask:
    plain: why is testing today's chat models harder than testing older language systems?
    jargon: how does LLM-era benchmarking depart from single-task supervised dataset evaluation
      with train and test splits?
    task: how do I adjust an evaluation setup built for task-specific models to work for general-purpose
      LLMs?
    practitioner: our old per-task test sets no longer tell us much about our LLM -- what
      actually changed?
  answered_by:
  - old-vs-new
  - gap-structured-view
- ask:
    plain: how much computing does it take to test a large language model properly?
    jargon: how does the compute cost of broad multi-task LLM benchmarking compare to pretraining,
      and why does efficient benchmarking matter?
    task: how do I keep the compute bill for evaluating language models under control?
    practitioner: is my evaluation run going to cost more GPU time than training the model
      itself?
  answered_by:
  - compute-cost
  - validity-reliability
- ask:
    plain: why would anyone trust one language model to grade another model's answers?
    jargon: what is the underlying assumption that licenses LLM-as-a-judge as an evaluation
      metric?
    task: how do I justify using a model-based judge instead of exact-match scoring for open-ended
      outputs?
    practitioner: should I let a language model score my system's generations, or is that
      circular?
  answered_by:
  - lm-as-evaluator-premise
- ask:
    plain: does the wording of a test prompt change how a language model scores?
    jargon: how do prompt selection and prompt banks affect LLM benchmark results, and how
      do prompt desiderata differ across use cases?
    task: how many prompts should I use per task when benchmarking a language model?
    practitioner: I am comparing two models on one fixed prompt -- is that enough to call
      a winner?
  answered_by:
  - prompts-part
- ask:
    plain: what existing tools can run a batch of tests on a language model?
    jargon: which open-source LLM evaluation harnesses and business frameworks are covered
      in a survey of benchmarking frameworks?
    task: how do I pick an evaluation framework for running language model benchmarks?
    practitioner: should I adopt an off-the-shelf evaluation harness or build our own benchmarking
      pipeline?
  answered_by:
  - frameworks-covered
- ask:
    plain: do people still need humans to rate model outputs now that models can rate each
      other?
    jargon: what role does manual evaluation retain alongside the alignment paradigm and LLM-human
      feedback loops?
    task: how do I decide when to spend money on human annotation for evaluating a language
      model?
    practitioner: can I drop human raters from our evaluation and rely on automatic judges?
  answered_by:
  - human-eval-not-abandoned
- ask:
    plain: what makes a language model benchmark a good one rather than a bad one?
    jargon: how do validity and reliability apply to LLM benchmarks, and which compute-reduction
      practices are considered best practice?
    task: how do I cut the cost of a language model benchmark without making the scores untrustworthy?
    practitioner: I want to subsample our benchmark to save compute -- will the numbers still
      be trustworthy?
  answered_by:
  - validity-reliability
  - compute-cost
- ask:
    plain: what is covered in the LREC-COLING 2024 tutorial on language model evaluation,
      and how long is each part?
    jargon: what is the part-by-part schedule of the Navigating the Modern Evaluation Landscape
      tutorial on LLM benchmarking?
    task: how do I find out whether an LLM evaluation tutorial covers metrics, prompts and
      human evaluation before I sit through it?
  answered_by:
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
