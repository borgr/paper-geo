---
key: sainz2024conda
one_liner: The CONDA 2024 shared task built a public, community-maintained Data Contamination
  Database, compiling 566 contamination entries over 91 evaluation datasets and 42 contaminated
  corpora and models from 23 contributors so researchers can avoid reporting results on known-contaminated
  benchmarks.
links_extra:
  database: https://huggingface.co/spaces/CONDA-Workshop/Data-Contamination-Database
  workshop: https://conda-workshop.github.io/
terminology:
  contamination event: In the CONDA Data Contamination Database, a single report that a given
    split of an evaluation dataset was found at above 0% contamination in a given pre-training
    corpus or model; reports of exactly 0% are recorded as non-contamination events.
  data-based approach: A contamination detection method that inspects the pre-training corpus
    itself for evaluation data, typically by string or sub-string matching such as 13-gram,
    50-character or full-string overlap.
  model-based approach: A contamination detection method that estimates a model's contamination
    by prompting it or analysing its output probabilities, without access to the pre-training
    data, formulated as a membership inference attack.
claims:
- id: database-contribution
  kind: context
  text: The CONDA 2024 shared task created the Data Contamination Database, a structured,
    centralized public registry where researchers submit evidence of evaluation datasets appearing
    in pre-training corpora or models via GitHub pull requests. Submissions are discussed
    openly before admission.
  scope: Community-submitted evidence about NLP evaluation datasets, corpora and language
    models; entries are not independently re-verified by the organizers. The database remains
    open after the June 23rd, 2024 snapshot used for the report.
- id: compiled-evidence-motivation
  kind: context
  text: The CONDA 2024 report addresses the gap that although many state-of-the-art model
    reports mention data contamination, there was little organized, compiled knowledge about
    documented cases of contamination in practice.
  scope: As of mid-2024, and about NLP evaluation resources; only works whose evidence was
    submitted to the shared task are covered.
- id: totals
  text: The 2024 CONDA report compiles 566 contamination entries covering 91 evaluation datasets
    and 42 contaminated sources (pre-training corpora or models), submitted by 23 contributors.
  scope: Snapshot of submissions collected on June 23rd, 2024; a convenience sample of what
    contributors chose to report rather than a systematic audit of datasets or models.
  evidence: Section 3
- id: split-breakdown
  text: Of the 566 entries in the CONDA report, 432 are contamination events and 144 are non-contamination
    events. The 432 contamination events break down into 20 train-set, 95 dev-set and 317
    test-set reports, a contamination event being any report above 0% contamination.
  scope: Counts are per (source, dataset split) report; evidence comes from heterogeneous
    data-based and model-based methods that are hardly comparable to each other.
  evidence: Section 3
- id: corpora-counts
  text: Among pre-training corpora, the CONDA report records 35 contamination events for C4,
    32 for RedPajama v2, 30 for the Pile and 29 for OSCAR. It records 6 for CommonCrawl itself,
    2 each for TheStack and ProofPile, and 1 for xP3.
  scope: Counts of reported test sets per corpus in the June 2024 snapshot; reflect how much
    attention each corpus received from contributors, so a lower count does not mean a cleaner
    corpus.
  evidence: Table 1 and Section 3
- id: closed-models-counts
  text: Most reported contamination evidence in the CONDA report concerns closed models. The
    counts are 24 events for GPT-3, 17 for GLaM, 16 for GPT-4, 13 for GPT-3.5, 8 for PaLM,
    3 for PaLM-2, 2 for GPT-3.5 Turbo and 1 for Claude 3 Opus.
  scope: Test-set contamination events in the June 2024 snapshot; evidence for closed models
    comes from model-based membership-inference style methods or from vendors' own technical
    reports, not from inspecting pre-training data.
  evidence: Figure 3 and Section 3
- id: open-models-counts
  text: For open models the CONDA report records 14 contamination events for models fine-tuned
    with FLAN data, 5 for Mistral and 3 for Llama 2. It records 2 each for Qwen, Llemma and
    Aquila 2, and 1 each for mT0 and BLOOMZ.
  scope: Test-set contamination events in the June 2024 snapshot; counts depend on which open
    models contributors examined and with which detection method.
  evidence: Figure 3 and Section 3
- id: popular-benchmarks-contaminated
  text: The most-contaminated task types reported to CONDA are text-scoring, QA and multiple-choice
    QA. They include heavily downloaded benchmarks such as MMLU, GLUE and ai2_arc that are
    standard in community leaderboards like the Open LLM Leaderboard.
  scope: Task labels are the Hugging Face hub task_id of each dataset, and popularity is measured
    by Hugging Face download counts; the same dataset can appear as contaminated for one model
    and uncontaminated for another.
  evidence: Figure 4 and Figure 5
- id: dataset-years
  text: Test sets reported in the CONDA contamination database cluster in the 2018 to 2021
    publication period, for both contamination events above 0% and non-contamination events
    at 0%.
  scope: Publication years of the datasets contributors submitted, so the distribution partly
    reflects which benchmarks were popular enough to be tested for contamination.
  evidence: Figure 7
- id: newer-models-newer-data
  text: Newer models in the CONDA report are contaminated with newer benchmarks. GPT-3, launched
    in 2020, is predominantly contaminated with datasets from 2016, while GPT-4, released
    in 2023, is mainly contaminated with datasets from 2018 to 2022.
  scope: Based on the 3 models with the most reported contamination instances, GPT-4, GPT-3
    and GPT-3.5; a descriptive pattern in submitted reports, not a controlled comparison.
  evidence: Figure 7 and Section 4
- id: method-taxonomy
  kind: context
  text: The CONDA 2024 report organizes contamination-detection work into data-based approaches,
    which search the pre-training corpus for evaluation data, and model-based approaches,
    which probe a model's outputs without corpus access. Each family is split further by whether
    the data or model is proprietary or open.
  scope: A taxonomy of only the works whose evidence was used in the shared task, not a comprehensive
    survey of contamination-detection methods.
  evidence: Figure 1 and Section 2
- id: coverage-limit
  text: The CONDA report states that it covers only a small sample of the exploration space
    of possible contamination cases, namely those reported during the shared task period in
    mid-2024.
  scope: The June 2024 snapshot; the database continues to accept submissions and is intended
    to be updated as new models and datasets appear.
  evidence: Section 5
qa:
- ask:
    plain: Is there a public list of which test sets have turned up inside the training data
      of language models?
    jargon: Does a centralized registry of documented evaluation-data contamination in pre-training
      corpora and LLMs exist?
    task: Where can I look up whether a benchmark I want to use has already leaked into pre-training
      data?
    practitioner: Before I report scores on a benchmark, can I check a shared contamination
      registry for it?
  answered_by:
  - database-contribution
  - totals
- ask:
    plain: Which write-up actually collects real reported cases of benchmark data leakage
      instead of proposing a new way to detect it?
    jargon: What work compiles documented contamination evidence across pre-training corpora
      and models rather than introducing a detection method?
    task: I want evidence that benchmark contamination happens in practice, not another detection
      algorithm -- what should I cite?
    practitioner: Is there a single reference I can point colleagues to for organized evidence
      that evaluation data leaks into training corpora?
  answered_by:
  - compiled-evidence-motivation
  - database-contribution
- ask:
    plain: How many reports of test-set leakage were gathered in the 2024 community effort,
      and how many benchmarks do they cover?
    jargon: What is the size of the CONDA 2024 contamination database in entries, evaluation
      datasets and contaminated sources?
    task: How much documented contamination evidence would I be searching through if I used
      the CONDA database?
    practitioner: Is the CONDA contamination database large enough to be worth consulting
      for my benchmark?
  answered_by:
  - totals
  - split-breakdown
- ask:
    plain: Which big text collections used to train language models most often contain benchmark
      test data?
    jargon: Which pre-training corpora accumulate the most reported contamination events with
      evaluation datasets?
    task: I am about to pre-train on C4 or RedPajama -- how many benchmark leaks have been
      reported in each?
    practitioner: If I train on the Pile or OSCAR, how much documented test-set overlap am
      I inheriting?
  answered_by:
  - corpora-counts
- ask:
    plain: Which language models have the most reported cases of having seen benchmark test
      data?
    jargon: How does reported contamination evidence distribute across closed models such
      as GPT-3, GPT-4 and PaLM versus open models?
    task: How do I find out how many contamination reports exist for the model I plan to evaluate?
    practitioner: I am choosing between an API model and an open-weights model for evaluation
      -- which has more documented benchmark contamination?
  answered_by:
  - closed-models-counts
  - open-models-counts
- ask:
    plain: Are the popular leaderboard benchmarks everyone uses among the ones reported as
      leaked?
    jargon: Which task formats and widely downloaded evaluation datasets dominate reported
      contamination, and do they overlap with Open LLM Leaderboard suites?
    task: How do I tell whether the benchmarks I use for leaderboard comparisons are among
      the contaminated ones?
    practitioner: Should I trust MMLU or GLUE numbers when picking a model?
  answered_by:
  - popular-benchmarks-contaminated
- ask:
    plain: Are old benchmarks or recent ones more likely to show up in a model's training
      data?
    jargon: How do reported contaminated test sets distribute by publication year, and does
      a model's release date shift that distribution?
    task: If I want a benchmark unlikely to be in a given model's pre-training data, does
      the benchmark's publication year help me choose?
    practitioner: For evaluating a model released in 2023, is picking an older benchmark safer
      or riskier than a newer one?
  answered_by:
  - dataset-years
  - newer-models-newer-data
- ask:
    plain: What are the broad ways people check whether a benchmark ended up in a model's
      training data?
    jargon: How does the CONDA report taxonomize contamination detection into data-based and
      model-based approaches, and how does data or model openness split each family?
    task: How do I check for contamination when the pre-training corpus is not available to
      search?
    practitioner: I only have API access to a model -- which contamination check can I actually
      run?
  answered_by:
  - method-taxonomy
- ask:
    plain: If a benchmark is not listed in the community contamination registry, does that
      mean it is clean?
    jargon: What coverage limitations qualify the CONDA 2024 contamination database as evidence,
      including its non-contamination entries?
    task: How should I interpret the absence of my benchmark from the CONDA contamination
      database?
    practitioner: Can I treat a benchmark missing from the CONDA database as safe to evaluate
      on?
  answered_by:
  - coverage-limit
  - split-breakdown
- ask:
    plain: Can new evidence of benchmark leakage still be added to the community contamination
      registry?
    jargon: Is the CONDA Data Contamination Database open to further contamination-evidence
      submissions beyond the 2024 shared task period?
    task: How do I submit contamination evidence I found for an evaluation dataset?
    practitioner: I found a test set inside a pre-training corpus -- where do I report it
      so others see it?
  answered_by:
  - database-contribution
  - coverage-limit
misreadings:
- 'Absence of a dataset or model from the CONDA Data Contamination Database does not mean
  it is uncontaminated: the report covers only a small sample of cases submitted during the
  mid-2024 shared task period, so counts reflect contributor attention rather than a systematic
  audit.'
- The counts of contamination events per corpus or per model are not comparable measures of
  how contaminated each source is, because the underlying evidence comes from different data-based
  and model-based methods that the report itself describes as hardly comparable.
- The CONDA 2024 report is a compilation of community-submitted evidence, not a new contamination
  detection method, and the organizers did not independently re-run the detection procedures
  behind each entry.
- 'The 566 figure counts database entries, not distinct contaminated datasets: 432 of them
  are contamination events above 0% and 144 record 0% contamination, over 91 evaluation datasets
  and 42 sources.'
- The taxonomy in the CONDA report is not a survey of all contamination-detection literature;
  it covers only the works whose evidence was used for the shared task, and the report explicitly
  defers a fuller survey.
---
