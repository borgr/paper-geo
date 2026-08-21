---
key: batzner2026everyevalever
coined: Every Eval Ever
gloss: a shared JSON schema and crowdsourced database for AI evaluation results
one_liner: Every Eval Ever is a community-governed JSON schema plus converters and a Hugging
  Face datastore that records not just a benchmark score but who ran it, on which model, under
  what generation settings, and what the metric means — spanning 22,235 models, 2,273 benchmarks
  and 31 evaluation formats.
claims:
- id: datastore-scale
  kind: result
  text: The Every Eval Ever datastore holds more than 200K aggregated evaluation results covering
    22,235 models, 2,273 unique benchmarks and 31 distinct evaluation reporting formats, drawn
    from over a hundred community data contributions.
  scope: Counts as of the May 4th 2026 snapshot; coverage is biased toward the sources contributors
    ingested, and 71.23% of runs come from one organization, alphaXiv.
  evidence: Section 6 and Figure 2; Table 6
- id: context-standardization-gap
  kind: context
  text: Every Eval Ever is a shared schema and crowdsourced repository for AI evaluation results,
    filling the documentation gap left by dataset and model standards. Croissant, Datasheets
    for Datasets and Model Cards cover data and models but not the run-time context that determines
    whether two scores can be compared.
  scope: Positioned as the first standardization effort of its kind for evaluation results
    as of the 2026 publication; concurrent efforts collecting instance-level or Inspect-specific
    outputs exist and are being aggregated into it.
- id: context-entry-point
  kind: context
  text: Every Eval Ever offers a starting point for readers looking for work on why nominally
    identical benchmark scores are not comparable across evaluation frameworks. It also documents
    what metadata has to be recorded before such scores can be compared.
  scope: Coverage is strongest for text-based, single-model evaluations; multi-modal evaluations,
    human preference judgments such as Chatbot Arena Elo, and multi-agent settings are only
    partially supported as of publication.
- id: inference-platform-unreported
  kind: result
  text: The inference platform is marked unknown or omitted entirely in 98% of evaluation
    rows in the Every Eval Ever datastore. Weighting each of the 31 formats equally, the field
    is reported in only 27% of rows on average.
  scope: 98% is a micro-average over evaluation runs, 27% a macro-average over the 31 harnesses
    and formats in the datastore; measures the ingested sources, not the schema.
  evidence: Section 6 and Table 2; Table 4
- id: metadata-fill-rates
  kind: result
  text: Across the 31 formats in the Every Eval Ever datastore, model name is filled 100%
    of the time but model parameter count and model license are each filled only 3%. Temperature
    and max tokens are filled 23% of the time.
  scope: Macro-average fill rates over the 31 evaluation harnesses and formats ingested as
    of the paper's snapshot; measures what upstream sources report, and the schema records
    absence rather than defaulting missing values.
  evidence: Table 2
- id: perplexity-normalization
  kind: result
  text: The same summed cross-entropy on WikiText yields a token-level perplexity of 5.4687
    and a word-level perplexity of 8.7939 for Llama-2-7B, a gap of 3.3252 that comes only
    from the normalization denominator.
  scope: 'Two implementations compared: a GPTQ-style script reporting token-normalized perplexity,
    and vLLM plus lm-eval-harness reporting word_perplexity; shown for OPT-6.7B (gap 1.4301)
    and Llama-2-7B on WikiText.'
  evidence: Table 3
- id: helm-reproduction-agreement
  kind: result
  text: Reproducing official HELM records locally and comparing per-instance scores gives
    91% to 100% agreement for Pythia-6.9B and Vicuna-7B v1.3 across 13 comparable benchmarks,
    but drops to 78.8% for Falcon-7B on SyntheticReasoning-Natural.
  scope: 3 models on 14 single-turn HELM benchmarks, both sides converted to the Every Eval
    Ever schema; agreement counts aligned (instance, core metric) pairs with identical scores
    up to numerical tolerance.
  evidence: Figure 4
- id: helm-mismatch-causes
  kind: result
  text: Instance-level comparison of official and reproduced HELM runs traces disagreements
    to concrete causes. Official Pythia completions on SyntheticReasoning-Natural are empty
    and score zero while local ones are non-empty, and Entity-Matching selects different Abt–Buy
    examples despite the same HELM recipe.
  scope: 3 models on 14 single-turn HELM benchmarks; the schema surfaces mismatched example
    sets, empty completions and stochastic disagreement, but when serving details are missing
    it cannot always determine the exact cause.
  evidence: Figure 4 and Section 7.3
- id: agentic-scaffold-cost
  kind: result
  text: On CocoaBench, the Codex and OpenClaw scaffolds with a GPT-5.4 backbone both reach
    45.1% accuracy, but Codex averages $0.7 and 377.8 s per task against OpenClaw's $1.0 and
    502.1 s.
  scope: Aggregate CocoaBench records for 6 scaffold–backbone pairs, re-represented in Every
    Eval Ever; source-reported accuracy, time and cost rather than reruns.
  evidence: Table 11 and Figure 3
- id: scaffold-backbone-interaction
  kind: result
  text: On CORE-Bench Hard from HAL, Claude Code beats CORE-Agent with a Claude Opus 4.5 backbone,
    77.8% versus 42.2%. With Claude Opus 4.1 the ranking flips, 42.2% for Claude Code against
    51.1% for CORE-Agent.
  scope: Representative HAL records for 6 scaffold–backbone pairs on CORE-Bench Hard re-represented
    in Every Eval Ever; source-reported accuracies and costs rather than reruns.
  evidence: Table 12 and Figure 3
- id: irt-instance-level
  kind: result
  text: A 1PL Item Response Theory model fit to instance-level Every Eval Ever records shows
    Wordle Arena items are harder on average and more variable in difficulty than GPQA Diamond
    or JudgeBench items. The response matrices cover 198 items from 69 models, 63 items from
    46 models, and 350 items from 55 models.
  scope: Unidimensional 1PL model fit with py-irt 0.7.1 via variational inference, using the
    is_correct field of each instance-level record; the difficulty comparison is descriptive,
    not a tested prediction about future saturation.
  evidence: Figure 5 and Appendix F.4
- id: reproduction-cost
  kind: result
  text: Re-running the roughly 230,000 model–benchmark evaluation pairs collected in Every
    Eval Ever is estimated to cost about $221K with a mid-tier model plus an LLM judge. A
    higher-end model raises that to about $368K, and a no-judge lower bound puts it at about
    $4.1K.
  scope: Assumes 1,000 examples per benchmark, 100 input and 20 output tokens per example,
    60% LLM-as-judge token overhead and list API prices; excludes agentic evaluations, reasoning
    models, repeated runs and human labeling.
  evidence: Appendix D, Sections D.6–D.8
- id: evaluation-concentration
  kind: result
  text: 'Evaluation activity in the Every Eval Ever datastore follows a long tail: the top
    25 models and top 25 benchmarks each account for barely 25% of all results. Excluding
    human baselines, 5 companies supply 23 of the 24 most frequently evaluated systems.'
  scope: Descriptive statistics over the ingested corpus as of the paper's snapshot; coverage
    is biased by which leaderboards and papers contributors converted, so the concentration
    describes reported evaluations rather than all evaluations run.
  evidence: Section 6 and Table 5, Table 7
- id: schema-design-partial-records
  kind: result
  text: The Every Eval Ever schema keeps required fields minimal and assigns each run a UUID
    rather than a canonical fingerprint. Partially specified, repeated and conflicting evaluation
    records are therefore all admitted and stay visible for later deduplication.
  scope: Design decision of schema version 0.2.2 with companion instance_level_eval_0.2.2;
    the cost is that deduplication shifts to the analysis layer, where reference implementations
    of equivalence criteria are planned rather than shipped.
  evidence: Table 1 and Section 8
- id: schema-community-process
  kind: result
  text: The Every Eval Ever schema was built from structured feedback from about 40 researchers
    and unstructured feedback from about 110. A field was admitted only if some existing framework
    or published result already reports it and a majority of contributors judged it necessary
    to interpret the score.
  scope: Contributors included benchmark creators, evaluation framework developers, governance
    experts, leaderboard operators and industry practitioners; disagreements were resolved
    by consensus among core maintainers, who retain final authority on contested changes.
  evidence: Section 3.1 and Appendix E.1
qa:
- ask:
    plain: is there an agreed way to write down the details of a benchmark run so other people
      can reuse the score?
    jargon: what schema unifies evaluation result records across harnesses, leaderboards and
      reporting formats?
    task: how do I publish my benchmark results in a format other people can aggregate with
      theirs?
    practitioner: should I log my eval runs into a shared schema instead of my own CSV columns?
  answered_by:
  - context-standardization-gap
  - schema-design-partial-records
- ask:
    plain: what should I read first about why the same benchmark score means different things
      in different tools?
    jargon: which work covers cross-framework comparability and metadata provenance for LLM
      evaluation results?
    task: where do I start reading if I need to compare scores reported by different evaluation
      pipelines?
    practitioner: I keep getting different numbers than a published leaderboard, is there
      a paper that explains what to check?
  answered_by:
  - context-entry-point
  - context-standardization-gap
- ask:
    plain: how many models and tests are covered by the big crowdsourced collection of AI
      evaluation results?
    jargon: what is the scale of the Every Eval Ever datastore in models, benchmarks and reporting
      formats?
    task: where can I find already-collected benchmark scores for thousands of models instead
      of running them?
    practitioner: is the collection large enough that my model or my benchmark is likely already
      in it?
  answered_by:
  - datastore-scale
- ask:
    plain: when people publish benchmark scores, which run details do they usually leave out?
    jargon: what are the field fill rates for inference platform, decoding temperature and
      parameter count across evaluation reporting formats?
    task: which metadata do I need to chase down myself before I can trust a reported score?
    practitioner: can I tell from a published leaderboard entry what serving stack and sampling
      settings produced the number?
  answered_by:
  - inference-platform-unreported
  - metadata-fill-rates
- ask:
    plain: why do two papers report different perplexity numbers on the same WikiText text
      and the same model?
    jargon: how much does token-level versus word-level normalization shift WikiText perplexity
      for Llama-2-7B?
    task: how do I make my perplexity number comparable to one reported by a different codebase?
    practitioner: my perplexity is higher than the published one for the same model, is the
      normalization denominator the reason?
  answered_by:
  - perplexity-normalization
- ask:
    plain: if I rerun a published evaluation myself, how close do the per-example results
      come out?
    jargon: what per-instance agreement do local reruns of official HELM records achieve across
      comparable scenarios?
    task: how do I check whether my local rerun of a public benchmark actually matches the
      official record?
    practitioner: can I trust the official numbers for a model, or should I rerun the benchmark
      myself?
  answered_by:
  - helm-reproduction-agreement
  - helm-mismatch-causes
- ask:
    plain: when two runs of the same benchmark disagree, what is usually going wrong?
    jargon: what concrete failure modes explain instance-level disagreement between official
      and reproduced HELM runs?
    task: how do I debug why my rerun of a public benchmark gives different scores from the
      released ones?
    practitioner: my rerun disagrees with the official record on a handful of items, is that
      a real difference or a pipeline bug?
  answered_by:
  - helm-mismatch-causes
- ask:
    plain: do two coding agents that solve the same fraction of tasks cost the same money
      and time?
    jargon: how do agentic scaffolds with an identical backbone differ in cost and wall-clock
      latency at matched accuracy on CocoaBench?
    task: how do I choose between two coding agent harnesses when their accuracy is the same?
    practitioner: is accuracy enough for me to pick a coding agent, or do I need the dollars-per-task
      numbers too?
  answered_by:
  - agentic-scaffold-cost
  - scaffold-backbone-interaction
- ask:
    plain: does the best agent wrapper change depending on which underlying model you plug
      into it?
    jargon: do scaffold rankings on CORE-Bench Hard invert across Claude Opus backbone versions?
    task: how do I pick an agent scaffold when I plan to swap the backbone model later?
    practitioner: if I upgrade my backbone model, will the agent framework I already chose
      still be the better one?
  answered_by:
  - scaffold-backbone-interaction
- ask:
    plain: can you tell which benchmark has harder individual questions rather than just lower
      average scores?
    jargon: what does a 1PL IRT fit to instance-level records show about item difficulty and
      its spread across GPQA Diamond, JudgeBench and Wordle Arena?
    task: how do I compare benchmarks at the item level instead of comparing their headline
      accuracies?
    practitioner: do I have enough per-item results across models to fit an item-difficulty
      model on my benchmark?
  answered_by:
  - irt-instance-level
- ask:
    plain: how much would it cost in API bills to rerun every collected model-and-benchmark
      evaluation from scratch?
    jargon: what is the estimated inference spend to reproduce roughly 230,000 model-benchmark
      evaluation pairs, with and without an LLM judge?
    task: how do I justify reusing published evaluation results instead of budgeting to rerun
      them?
    practitioner: is it cheaper for me to reuse aggregated published eval results than to
      rerun the benchmarks myself?
  answered_by:
  - reproduction-cost
- ask:
    plain: are reported AI benchmark results spread across many systems, or piled onto a few
      popular ones?
    jargon: how concentrated is evaluation activity across models and benchmarks in aggregated
      evaluation records?
    task: how do I find out whether the model or benchmark I care about has any reported results
      at all?
    practitioner: if my model is not from a big lab, should I expect to find published evaluations
      of it?
  answered_by:
  - evaluation-concentration
- ask:
    plain: can a shared collection of benchmark results accept a run that is missing some
      of its settings?
    jargon: how does a minimal-required-field schema with per-run UUIDs handle partial, duplicate
      and conflicting evaluation records?
    task: how do I contribute an old evaluation run when I no longer know the temperature
      or the serving platform?
    practitioner: my logs are incomplete, will my results be rejected from a shared evaluation
      repository?
  answered_by:
  - schema-design-partial-records
  - schema-community-process
- ask:
    plain: who decided which run details a shared benchmark-reporting format should ask for?
    jargon: what inclusion criteria and community feedback process determined the fields of
      the Every Eval Ever schema?
    task: how do I decide which metadata fields to require when designing an evaluation reporting
      format?
    practitioner: can I trust that a shared evaluation schema asks for fields my group actually
      needs, and can I get one added?
  answered_by:
  - schema-community-process
misreadings:
- Every Eval Ever is not a new evaluation harness and does not run evaluations; it is a translation
  layer and repository that stores results produced by harnesses, leaderboards and papers.
- High per-instance agreement between official HELM records and local reproductions does not
  mean evaluation frameworks guarantee exact reproducibility; the schema surfaces mismatched
  example sets, empty completions and stochastic disagreement without always identifying the
  cause.
- The 22,235 models and 2,273 benchmarks in the datastore are not a representative census
  of AI evaluation; coverage is biased by which sources contributors converted, with 71.23%
  of runs from one organization.
- The $221K mid-tier reproduction estimate is a deliberately conservative lower-side figure
  under fixed token assumptions, not a measured expenditure, and it excludes agentic evaluations,
  reasoning models, repeated runs and human labeling.
- 'Validation in Every Eval Ever checks schema compliance, not correctness of scores: records
  that pass validation can still be disputed, and the project explicitly does not arbitrate
  which of two methodologically valid runs is correct.'
- Recording metadata does not make all scores comparable; the schema makes normalization conventions,
  harness versions and access modes visible so that incomparable scores can be told apart.
terminology:
  aggregate evaluation record: A single JSON document describing one evaluation run of one
    model, holding source provenance, model identity and access mode, evaluation framework,
    generation configuration, and one or more metric results.
  instance-level companion file: An optional JSONL sidecar, one object per benchmark sample,
    storing prompts, model outputs, references, per-sample scores, token usage and latency,
    linked to an aggregate record by evaluation_id.
  evaluator_relationship: A metadata field recording whether an evaluation was run by the
    model developer (first_party), an independent party (third_party), or the metadata contributor
    themselves (self).
  source_type: A metadata field distinguishing results scraped from a leaderboard or paper
    (documentation) from results produced by a local evaluation run (evaluation_run).
  interaction_type: The interaction regime of an instance-level record, one of single_turn,
    multi_turn, or agentic, which determines whether the record uses an output object or a
    messages array with tool calls.
  metric_config: A per-result object capturing metric semantics — whether lower values are
    better, the score type (continuous, binary, ordinal), the score range, and level names
    for ordinal metrics — so that a bare number is not misread.
  macro-average fill rate: The share of records in which a metadata field is populated, averaged
    with each source format weighted equally rather than by its number of records.
---
