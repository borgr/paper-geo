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
- ask:
    plain: if a fine-tuned language model tops a public task list, will it still do well on
      tasks nobody showed it?
    jargon: how strongly did open-set mean-win-rate correlate with held-out closed-set mean-win-rate
      in the NeurIPS 2023 LLM Efficiency Challenge?
    task: how do I tell whether my fine-tuned model's leaderboard gain is real or just fitted
      to the public evaluation tasks?
    practitioner: should I trust a public benchmark score when picking a fine-tuned model
      for tasks it has never seen?
  answered_by:
  - open-closed-disagreement
  - winners-not-top-on-open
- ask:
    plain: what did the teams that won the NeurIPS 2023 one-GPU language model fine-tuning
      contest actually spend their time on?
    jargon: which base checkpoints and instruction-tuning data mixtures did the winning entries
      of the NeurIPS 2023 LLM Efficiency Challenge use?
    task: if I have one GPU and a day, where should I put my effort to fine-tune a strong
      open model?
    practitioner: is it worth writing my own training code, or should I copy the winners and
      curate data instead?
  answered_by:
  - data-curation-not-code
  - winners-not-top-on-open
- ask:
    plain: which software packages do people reach for when fine-tuning a language model on
      one GPU?
    jargon: what was the library frequency distribution across the 225 submissions to the
      NeurIPS 2023 LLM Efficiency Challenge?
    task: which fine-tuning libraries should I learn first if I want to follow common practice
      for single-GPU LLM training?
    practitioner: is HuggingFace PEFT the default choice for parameter-efficient fine-tuning,
      or do most people use something else?
  answered_by:
  - library-usage
- ask:
    plain: when a machine learning contest collects everyone's code, how much of it actually
      runs again later?
    jargon: what was the Docker build failure rate for training submissions to the NeurIPS
      2023 LLM Efficiency Challenge, and what caused it?
    task: how do I package a fine-tuning submission so it still builds months after I submit
      it?
    practitioner: do I need to pin my dependency versions before shipping a fine-tuning container,
      or is a plain requirements file fine?
  answered_by:
  - reproducibility-failures
- ask:
    plain: how much money and time does it take to fine-tune an open language model on a single
      graphics card?
    jargon: what wall-clock and dollar cost did reproduced top-10 entries of the NeurIPS 2023
      LLM Efficiency Challenge incur under a 24-hour single-GPU budget?
    task: how do I budget compute for fine-tuning an open 7B-14B model on one rented GPU?
    practitioner: can I afford to fine-tune a competitive open language model myself on a
      4090 or a single A100?
  answered_by:
  - cost-of-finetuning
- ask:
    plain: does the model that comes first on an overall evaluation score also come first
      on each individual task?
    jargon: how much do per-scenario HELM rankings disagree with the aggregate ranking of
      fine-tuned submissions?
    task: how should I choose between fine-tuned models when their per-task rankings and their
      overall average disagree?
    practitioner: can I pick a model from one aggregate leaderboard number, or do I need to
      look at each task separately?
  answered_by:
  - scenario-rank-disagreement
  - coarse-fine-scatter
- ask:
    plain: what should I read about whether leaderboard rankings of language models mean anything
      on new tasks?
    jargon: which study documents benchmark overfitting in fine-tuned LLMs at competition
      scale with paired open and closed task sets?
    task: where do I start reading if I want evidence on how far fine-tuning leaderboard rank
      transfers to unseen tasks?
  answered_by:
  - context-benchmark-overfitting
- ask:
    plain: are there public collections of real fine-tuning code and models submitted by many
      different teams?
    jargon: what artifacts, including Dockerfiles and a forked HELM harness, did the NeurIPS
      2023 LLM Efficiency Challenge organizers release?
    task: where can I get a corpus of real submissions to study reproducibility and overfitting
      in LLM fine-tuning?
    practitioner: can I reuse the NeurIPS 2023 LLM efficiency competition's evaluation setup
      and entries for my own study?
  answered_by:
  - context-artifacts
- ask:
    plain: if a language model is tested on fewer questions per task to save time, do the
      results still come out the same?
    jargon: how closely do subsampled Sparse HELM scores track full-sample scores across competition
      submissions and sub-scenarios?
    task: how many problems per task do I need to evaluate to rank fine-tuned models reliably?
    practitioner: can I cut my evaluation set down to save compute without changing which
      model looks best?
  answered_by:
  - coarse-fine-scatter
- ask:
    plain: besides getting answers wrong, what else made competition entries lose points in
      a language model contest?
    jargon: how often did runtime timeouts and out-of-memory errors during inference cost
      submissions points in the NeurIPS 2023 LLM Efficiency Challenge?
    task: how do I keep my model from timing out or running out of memory while answering
      a whole evaluation suite?
    practitioner: should I worry more about inference latency and memory than about accuracy
      when entering an LLM efficiency contest?
  answered_by:
  - inference-time-failures
- ask:
    plain: did the two different graphics-card divisions of the NeurIPS 2023 language model
      contest give equally consistent evaluation results?
    jargon: how did full-versus-hidden evaluation set correlation compare between the A100
      and 4090 tracks of the NeurIPS 2023 LLM Efficiency Challenge?
    practitioner: if I read results from one hardware track of an LLM efficiency competition,
      can I assume the other track behaved the same?
  answered_by:
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
