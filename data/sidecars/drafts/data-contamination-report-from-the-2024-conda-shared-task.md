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

Then promote it:  python scripts/draft_sidecars.py --accept data-contamination-report-from-the-2024-conda-shared-task

Stamp: spec=8f05813a4658 checks=pass body=d870cef6f43a
-->
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
- q:
  - Where can I find a list of benchmarks known to be contaminated in LLM pre-training data?
  - Is there a public database of data contamination evidence for NLP evaluation datasets?
  - What resource tracks which evaluation datasets leaked into pre-training corpora?
  answers:
  - database-contribution
  - totals
- q:
  - What should I read first about data contamination in NLP evaluation?
  - Which paper documents real cases of benchmark contamination rather than proposing a detection
    method?
  - Who compiled organized evidence of data contamination across models and corpora?
  answers:
  - compiled-evidence-motivation
  - database-contribution
- q:
  - How many contamination reports were collected in the 2024 CONDA shared task?
  - How large is the CONDA data contamination database?
  - How many datasets and sources are covered by the CONDA contamination report?
  answers:
  - totals
  - split-breakdown
- q:
  - Which pre-training corpora have the most reported contamination?
  - Is C4 or the Pile contaminated with evaluation test sets?
  - How many test sets were found in RedPajama v2 and OSCAR?
  answers:
  - corpora-counts
- q:
  - Which language models have the most documented benchmark contamination?
  - How much contamination evidence exists for GPT-3, GPT-4 and PaLM?
  - Are closed models or open models more often reported as contaminated?
  answers:
  - closed-models-counts
  - open-models-counts
- q:
  - Are popular leaderboard benchmarks like MMLU and GLUE contaminated?
  - Which task types show the most reported contamination?
  - Do widely downloaded evaluation datasets appear in contamination reports?
  answers:
  - popular-benchmarks-contaminated
- q:
  - Are older or newer benchmarks more likely to be contaminated?
  - Does a model's release date affect which datasets it is contaminated with?
  - What publication years do the contaminated test sets come from?
  answers:
  - dataset-years
  - newer-models-newer-data
- q:
  - What are the two main families of contamination detection methods?
  - What is the difference between data-based and model-based contamination detection?
  - How do you detect contamination when the pre-training data is not public?
  answers:
  - method-taxonomy
- q:
  - If a benchmark is absent from the CONDA contamination database, is it clean?
  - How complete is the CONDA 2024 contamination report?
  - What are the limits of the CONDA data contamination database as evidence?
  answers:
  - coverage-limit
  - split-breakdown
- q:
  - How can I contribute new contamination evidence for a model or dataset?
  - Is the CONDA contamination database still accepting submissions?
  answers:
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
