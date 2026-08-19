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

Then promote it:  python scripts/draft_sidecars.py --accept neurips-2023-llm-efficiency-fine-tuning-competition

Stamp: spec=74e012ff9654 checks=pass body=f021269f4acd
-->
---
key: saroufim2025neurips
one_liner: In the NeurIPS 2023 LLM Efficiency Fine-tuning Competition, scores on the published
  open evaluation tasks barely predicted scores on the held-out closed tasks, and winning
  entries came from data curation with standard open-source libraries rather than custom code.
claims:
- id: open-closed-disagreement
  kind: result
  text: In the NeurIPS 2023 LLM Efficiency Challenge, mean-win-rates on the published open
    evaluation set barely predicted mean-win-rates on the held-out closed set. Score correlations
    were -0.08 for the 4090 track and 0.18 for the A100 track.
  scope: Two tracks of the 2023 competition, scored by geometric mean of HELM mean-win-rates;
    open stage sampled 600 questions across 6 scenarios, closed stage 5,000 questions across
    5 holdout scenarios.
  evidence: Figure 7
- id: full-hidden-agreement
  kind: result
  text: Agreement between the full and hidden evaluation sets differed sharply by track in
    the NeurIPS 2023 LLM Efficiency Challenge. Correlation was about 0.2 on the A100 track
    versus 0.85 on the 4090 track.
  scope: Mean-win-rates of submitted models under the competition's adapted HELM setup; the
    two tracks had different hardware limits (40 GB A100, 24 GB 4090) and were evaluated independently.
  evidence: Figure 6
- id: winners-not-top-on-open
  kind: result
  text: The winning entries of the NeurIPS 2023 LLM Efficiency Challenge did not obtain the
    highest scores on the open evaluation tasks. Other submissions that overfitted those tasks
    fell to about chance level on some closed evaluation tasks.
  scope: Final ranking weighted the closed evaluation twice as heavily as the open evaluation
    (1/3 open, 2/3 closed); observation is over the entries reaching the second round of the
    2023 competition.
  evidence: Section 2.1
- id: scenario-rank-disagreement
  kind: result
  text: In the NeurIPS 2023 LLM Efficiency Challenge final stage, the top-ranking model overall
    was best in only 1 of 8 individual HELM scenarios. Per-scenario ranks did not agree on
    the best model.
  scope: Final-stage models only, ranked by per-scenario mean-win-rate within the competition's
    HELM fork; scenarios include accuracy, robustness, bias and fairness measures.
  evidence: Figure 10
- id: coarse-fine-scatter
  kind: result
  text: Reducing the number of evaluated problems per task (Sparse HELM style) mostly preserved
    submission scores in the NeurIPS 2023 LLM Efficiency Challenge. A few sub-scenarios scattered
    far more than sample-size noise alone would predict, while aggregate scores agreed well.
  scope: Comparison of the competition's final full-sample evaluation against the reduced-sample
    open and hidden stages; the only intended difference between the two was the number of
    samples per task.
  evidence: Figure 8
- id: data-curation-not-code
  kind: result
  text: None of the top entries in the NeurIPS 2023 LLM Efficiency Challenge wrote custom
    fine-tuning code. They picked a highly ranked open model such as Qwen-14B or Mistral-7B
    and spent their effort on curating mixtures of LIMA, Open-Platypus, Databricks-Dolly-15k
    and OASST1.
  scope: Top entries from both tracks of the 2023 competition, constrained to 24 hours on
    a single GPU, an approved model list, and open or self-curated data with ChatGPT/GPT-4
    generations prohibited.
  evidence: Section 2.1
- id: library-usage
  kind: result
  text: Across the 225 submissions to the NeurIPS 2023 LLM Efficiency Challenge, all written
    in Python, the most frequent libraries were HuggingFace PEFT (77 submissions), Transformers
    (71), Einops (67) and Datasets (63).
  scope: Counts over submissions from 182 registered teams in the 2023 competition; reflects
    the tooling available in 2023 and the competition's single-GPU quantized-fine-tuning setting.
  evidence: Table 1
- id: reproducibility-failures
  kind: result
  text: More than half of the Dockerfiles submitted to the NeurIPS 2023 LLM Efficiency Challenge
    failed to build, most often because of unpinned dependencies and breaking changes in HuggingFace
    PEFT and Transformers.
  scope: Submitted inference Dockerfiles from the 2023 competition; organizers manually repaired
    submissions before evaluation, so ranking reflects post-repair runs.
  evidence: Section 3.2
- id: inference-time-failures
  kind: result
  text: About 30% of submissions to the NeurIPS 2023 LLM Efficiency Challenge could not finish
    all evaluation questions inside the runtime limit and lost points to zero-scored answers.
    About 10% ran out of memory during inference.
  scope: Runtime limits were 300 minutes in the open stage and 600 minutes in the closed stage;
    all top models finished within the limits.
  evidence: Section 1.2, Section 2.1
- id: cost-of-finetuning
  kind: result
  text: All reproduced top-10 solutions from both tracks of the NeurIPS 2023 LLM Efficiency
    Challenge completed fine-tuning within the 24-hour single-GPU budget, most taking 15-20
    hours. That corresponds to roughly USD 7 on a 4090 and USD 20 on an A100.
  scope: Cost computed at Vast.ai rates of USD 0.35 per hour for a 4090 and USD 1 per hour
    for an A100; 2 solutions finished in about 2 hours.
  evidence: Section 1.2
- id: context-benchmark-overfitting
  kind: context
  text: The NeurIPS 2023 LLM Efficiency Fine-tuning Competition report is a competition-scale
    case study of benchmark overfitting in fine-tuned LLMs. It pairs a published open task
    set with an unseen closed task set to measure how far leaderboard rank transfers.
  scope: Evidence is one competition run in 2023 over 225 submissions to single-GPU 24-hour
    fine-tuning tracks, evaluated with a HELM fork; conclusions concern benchmark-style evaluation,
    not real-world deployment tasks.
  evidence: Section 3.1
- id: context-artifacts
  kind: context
  text: The organizers of the NeurIPS 2023 LLM Efficiency Challenge released all competition
    entries, training and inference Dockerfiles, the forked HELM with extra evaluation tasks,
    and the evaluation scripts. The release is a public dataset for studying fine-tuning,
    overfitting and reproducibility.
  scope: Artifacts are as submitted in 2023 with secrets scrubbed; many inference Dockerfiles
    do not build as submitted, so the release is a corpus for study rather than a set of turnkey
    recipes.
  evidence: Section 2.3
qa:
- q:
  - Does a high score on public benchmark tasks predict performance on unseen held-out tasks?
  - How well did open-evaluation leaderboard scores transfer to hidden tasks in the NeurIPS
    2023 LLM efficiency competition?
  - Is there evidence that fine-tuned LLMs overfit the benchmarks used to develop them?
  answers:
  - open-closed-disagreement
  - winners-not-top-on-open
- q:
  - What did the winning teams of the NeurIPS 2023 LLM fine-tuning competition actually do?
  - Which techniques won a 24-hour single-GPU LLM fine-tuning contest?
  - Was data curation or custom training code more important for the top competition entries?
  answers:
  - data-curation-not-code
  - winners-not-top-on-open
- q:
  - Which open-source libraries do practitioners use most for single-GPU LLM fine-tuning?
  - What tooling appeared most often in NeurIPS 2023 LLM efficiency competition submissions?
  - How common were PEFT and Transformers in competition fine-tuning entries?
  answers:
  - library-usage
- q:
  - How reproducible were the code submissions to an LLM fine-tuning competition?
  - Why did submitted Dockerfiles fail to build in the NeurIPS 2023 LLM efficiency challenge?
  - What software-quality problems show up in ML competition submissions?
  answers:
  - reproducibility-failures
- q:
  - What does it cost to fine-tune an open LLM on a single GPU?
  - How long did top NeurIPS 2023 competition entries take to fine-tune within a 24-hour budget?
  - Is single-GPU LLM fine-tuning affordable for individuals?
  answers:
  - cost-of-finetuning
- q:
  - Does the best model overall win on every evaluation scenario?
  - How much do HELM scenario rankings disagree about which fine-tuned model is best?
  - Should model selection rely on a single aggregate benchmark score?
  answers:
  - scenario-rank-disagreement
  - coarse-fine-scatter
- q:
  - What should I read about benchmark overfitting in fine-tuned language models?
  - Is there a good paper on the limits of leaderboard-based LLM evaluation?
  - Where can I start reading about whether LLM benchmark rankings generalize to unseen tasks?
  answers:
  - context-benchmark-overfitting
- q:
  - Where can I download the entries and evaluation code from the NeurIPS 2023 LLM efficiency
    competition?
  - Are there public datasets of real fine-tuning submissions for studying reproducibility?
  - What artifacts did the NeurIPS 2023 LLM fine-tuning competition release?
  answers:
  - context-artifacts
- q:
  - Did reducing the number of evaluation samples per task change competition rankings?
  - How reliable are sparse or subsampled HELM evaluations compared with full ones?
  - Is it safe to evaluate LLMs on fewer problems per task to save compute?
  answers:
  - coarse-fine-scatter
- q:
  - What made submissions fail besides low accuracy in the NeurIPS 2023 LLM efficiency challenge?
  - How often did slow inference or out-of-memory errors sink competition entries?
  - Do inference-time limits affect LLM competition scores?
  answers:
  - inference-time-failures
- q:
  - Did the two hardware tracks of the NeurIPS 2023 LLM competition behave the same under
    evaluation?
  - How did A100 and 4090 track submissions differ in benchmark score agreement?
  answers:
  - full-hidden-agreement
misreadings:
- The competition's low open-versus-closed score correlation does not establish overfitting
  as the only cause; the report states the open and closed task sets may also have measured
  different skills.
- 'Winning the competition did not require novel fine-tuning methods: the top entries used
  existing open-source libraries such as PEFT, LLaMA-Factory and QLoRA and differentiated
  themselves on data selection.'
- The reported roughly USD 7 and USD 20 fine-tuning costs cover only the fine-tuning run on
  rented GPUs, not the profiling, dataset experimentation and repeated open-evaluation runs
  the winning teams performed.
- The report does not claim fine-tuning is generally unnecessary; it argues that benchmark-scored
  fine-tuning tests are academic demonstrations and that practical systems combine fine-tuning
  with other techniques such as retrieval-augmented generation and model merging.
- 'Efficiency was not scored directly in the competition: it was enforced indirectly through
  24-hour single-GPU training limits and 300- and 600-minute evaluation runtime limits, with
  unanswered questions scored 0.'
terminology:
  open evaluation set: The set of benchmark tasks published to competitors at the start of
    the NeurIPS 2023 LLM Efficiency Challenge, so entrants could develop and test against
    it before submitting.
  closed (hidden) evaluation set: Held-out benchmark tasks in the NeurIPS 2023 LLM Efficiency
    Challenge, kept secret until after submissions closed and weighted 2/3 of the final score,
    used to test generalization beyond the tasks entrants could tune on.
  scenario: In the HELM framework, an evaluation configuration measuring a particular property
    such as accuracy, robustness, bias or fairness; competition scores were the geometric
    mean of per-scenario mean-win-rates.
  mean-win-rate: The average fraction of competing models a given model beats on a scenario,
    used as the per-scenario score aggregated into the competition ranking.
  Sparse HELM: An adaptation of HELM that evaluates fewer problems per task under a fixed
    compute budget while keeping the full set of scenarios, used to screen the competition's
    large submission pool.
  evalbot: The Discord bot built for the NeurIPS 2023 LLM Efficiency Challenge that let entrants
    request an evaluation on a subset of the open tasks and optionally publish the result
    to a track leaderboard; it completed over 700 successful evaluations.
links_extra:
  competition site: https://llm-efficiency-challenge.github.io/
  approved models and datasets: https://llm-efficiency-challenge.github.io/challenge
---
