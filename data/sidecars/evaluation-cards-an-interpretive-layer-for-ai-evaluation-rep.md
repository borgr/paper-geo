---
key: ghosh2026evaluationcards
coined: Evaluation Cards
gloss: a unified, machine-populated record that joins benchmark metadata, evaluation run data
  and model metadata so a reported score can be traced, compared and read for what it omits
one_liner: Evaluation Cards is a deployed reporting layer that joins benchmark metadata, evaluation
  run data and model metadata into one record, resolves every score to a family-composite-benchmark-split-metric
  path, and computes four interpretive signals (reproducibility, completeness, provenance,
  comparability) over it.
claims:
- id: repro-gap-corpus
  kind: result
  text: Across 50,461 (model, benchmark, metric-path) triples in the Evaluation Cards corpus,
    48,698 (96.5%) are missing at least one field of the minimal reproducibility sub-schema.
    Within that sub-schema, max_tokens is absent from 95.6% of triples and temperature from
    93.9%.
  scope: Public LLM evaluation reporting ingested as of June 4, 2026 from EEE converters (HELM,
    lm-eval-harness, Inspect AI), leaderboard scrapes and community contributions; the sub-schema
    checks only temperature and max_tokens, not seeds, hardware or determinism.
  evidence: Section 5, Finding 1
- id: first-vs-third-party-fields
  kind: result
  text: On 180 (model, benchmark) pairs reported by both first- and third-party evaluators,
    first-party rows populate 0.0% of the base reproducibility fields on average against 16.6%
    for third-party rows. The reproducibility gap is therefore widest in developer self-reporting.
  scope: 180 paired first/third-party cases in the ingested corpus; base fields are temperature
    and max_tokens only; evaluator relationship is self-declared in the EEE evaluator_relationship
    field.
  evidence: Section 5, Finding 1
- id: completeness-median
  kind: result
  text: Median per-benchmark documentation completeness against the 28-field operationalized
    Evaluation Cards schema is 10.7% across 635 benchmarks. Per-field population runs from
    100.0% for score and metric score_type down to 0.0% for preregistration_url and lifecycle_status.
  scope: 635 benchmarks with warehouse completeness rows, of which 211 carry matched Auto-BenchmarkCards
    records; completeness measures artifact-side documentation adequacy only, and partial
    fields score as the fraction of sub-items populated.
  evidence: Section 5, Finding 2
- id: single-party-reporting
  kind: result
  text: Of 49,865 (model, benchmark) pairs in the Evaluation Cards corpus, 98.2% are reported
    by only one party, and among the 181 multi-organization metric groups 94 (51.9%) exceed
    the 5% cross-party score-divergence threshold.
  scope: Ingested public reporting from 30 organizations as of June 4, 2026; the 5% threshold
    is applied uniformly on each metric's native scale and ignores sampling variance.
  evidence: Section 5, Finding 3
- id: first-party-only-by-category
  kind: result
  text: First-party-only reporting is most prevalent for agentic benchmarks (15.1%) and general
    benchmarks (12.5%), and least prevalent for safety benchmarks (0.8%). Independent reporting
    is thus scarcest in the categories where comparability problems would matter most.
  scope: Benchmark categories assigned by LLM-assisted labelling from benchmark name only
    into an 18-category taxonomy, with human review and manual corrections; the ingested corpus
    overrepresents English-language benchmarks and frontier-scale models.
  evidence: Section 5, Finding 3
- id: gpt5-walkthrough
  kind: result
  text: In the GPT-5 Evaluation Cards profile, 202 of 213 documented results (95%) lack temperature
    or max_tokens, and 13% of results are first-party. MATH-500 is reported by 3 organizations
    with scores from 84.7% (LLM Stats) to 98.9% (Artificial Analysis).
  scope: One model view rendered from the Evaluation Cards interface on June 4, 2026, covering
    118 benchmarks and 19 reporting organizations; a single frontier model rather than a corpus-wide
    statistic.
  evidence: Appendix A.3
- id: mmlu-pro-walkthrough
  kind: result
  text: Aggregating MMLU-Pro across 8 reporting organizations, 4,975 of 5,079 reported results
    (98%) lack a minimal reproducibility field. 6 model entries diverge across parties beyond
    the threshold, including Llama 3.2 at 20.9% from Hugging Face versus 61.8% from Arcadia
    Impact.
  scope: One benchmark view rendered on June 4, 2026 over 401 models and 8 organizations;
    MMLU-Pro's own Auto-BenchmarkCards record populates 26 of 28 fields, so it is a well-documented
    benchmark rather than a typical one.
  evidence: Appendix A.4
- id: framework-derivation
  kind: result
  text: The Evaluation Cards reporting framework is a five-part structure covering design,
    before execution, execution, lifecycle, and reporting and publication. It was derived
    from 730 recommendation items coded from 52 papers out of 748 screened candidates, plus
    12 stakeholder interviews.
  scope: Preregistered review of AI evaluation practice papers published 2020-2025; two independent
    coders reached Cohen's kappa in [0.865, 0.895] and Krippendorff's alpha in [0.916, 0.964];
    interviewees recruited through author networks, mostly North America-based.
  evidence: Section 3.1, Table 2
- id: entity-resolver-accuracy
  kind: result
  text: The Evaluation Cards entity resolver reaches 98.3% accuracy on models, 77.4% on benchmarks
    and 86.7% on metrics, over 200 randomly sampled entities per type. The resolver maps observed
    model, benchmark and metric strings to canonical identifiers.
  scope: In-domain EEE corpus data with manual labelling of each prediction, and matching
    rules were curated on the full dataset, so figures are not held-out; unresolved strings
    are retained rather than dropped.
  evidence: Appendix D.2.2
- id: rollout-hierarchy
  kind: result
  text: Evaluation Cards replaces the flat (model, benchmark, score) triple with a five-level
    rollout hierarchy of family, composite, benchmark, split and metric. A claim such as "GPT-5
    achieves 0.994 on MATH" resolves to MATH-family / artificial_analysis / MATH-500 / advanced-math
    / accuracy.
  scope: LLM benchmarks ingested into Evaluation Cards; the hierarchy lets integrity signals
    attach to a (model, metric-path) pair rather than to a benchmark label, and depends on
    the canonicalization layer resolving name variants correctly.
  evidence: Section 3.2, Figure 2
- id: reader-modes
  kind: result
  text: Evaluation Cards renders identical records through two reader modes, differing only
    in which fields are surfaced or compressed. Research mode lists the specific missing configuration
    fields, while the default summary mode states the same signal as "How this model was prompted
    during testing is not documented."
  scope: Two modes derived from 12 practitioner interviews across technical, developer and
    policy roles; systematic usability evaluation is planned post-deployment rather than completed.
  evidence: Section 4.3
- id: no-grades
  kind: result
  text: Evaluation Cards assigns no letter grades, pass/fail thresholds or completeness rankings,
    surfacing omitted fields to readers instead of penalizing developers for them.
  scope: All records in the interface; signal outputs are flags, missing-field lists and a
    completeness score in [0,1].
  evidence: Section 4.2
- id: context-composition
  kind: context
  text: 'Evaluation Cards composes three previously separate efforts into a single reader-facing
    record: Auto-BenchmarkCards for benchmark metadata, EEE for evaluation run data, and community
    model catalogs. It is an integration layer rather than another documentation standard
    for evaluators to fill in by hand.'
  scope: As of the June 2026 preprint, and by the comparison in Table 1 against Datasheets,
    Data Cards, Model Cards, BenchmarkCards, Audit Cards, Eval Factsheets, SPHERE, STREAM,
    HELM, Inspect, Open LLM Leaderboard, EEE and BetterBench; covers LLM evaluation only.
  evidence: Table 1
- id: context-monitoring-instrument
  kind: context
  text: Evaluation Cards is a deployed monitoring instrument for the state of public AI evaluation
    reporting, applied to 5,816 models, 635 benchmarks and 101,955 reported results from 30
    organizations. Its code is open and the interface is live and hosted.
  scope: LLM evaluation reporting as of June 4, 2026; the corpus is what EEE, leaderboard
    scrapes and community contributions supply rather than a census of public reporting.
  evidence: Section 5, Appendix A.2, Appendix N
qa:
- ask:
    plain: when a company publishes a benchmark score for a language model, do they usually
      say enough for someone else to get the same number?
    jargon: how prevalent are missing decoding-configuration fields such as temperature and
      max_tokens across publicly reported LLM benchmark results?
    task: how do I find out whether a published model score lists the generation settings
      I would need to re-run the evaluation?
    practitioner: can I trust a leaderboard score enough to reproduce it on my own infrastructure,
      or will the sampling settings be missing?
  answered_by:
  - repro-gap-corpus
- ask:
    plain: do the companies that build AI models write down less about how they tested them
      than outside testers do?
    jargon: does first-party evaluation reporting populate fewer reproducibility fields than
      third-party reporting on the same model-benchmark pairs?
    task: how do I tell whether a developer-reported score or an independent evaluator's score
      comes with more usable configuration detail?
    practitioner: if I need documented evaluation settings, should I take the number from
      the model developer or from an independent evaluator?
  answered_by:
  - first-vs-third-party-fields
- ask:
    plain: how much of the basic information about a benchmark is actually written down where
      people report scores from it?
    jargon: what is the per-benchmark field population rate against an operationalized evaluation
      documentation schema, and which fields saturate at 100% or 0%?
    task: how do I check which parts of a benchmark's documentation, like preregistration
      or lifecycle status, I can expect to find at all?
    practitioner: if I want benchmark metadata beyond the score itself, which fields will
      I realistically get and which will I have to chase down?
  answered_by:
  - completeness-median
- ask:
    plain: is the same AI model usually tested on the same benchmark by more than one organization,
      and do their numbers match?
    jargon: what fraction of (model, benchmark) pairs have multi-organization coverage, and
      how many metric groups exceed a cross-party score-divergence threshold?
    task: how do I check whether a reported model score has been independently corroborated
      by another organization?
    practitioner: should I treat a single reported benchmark number as corroborated, or look
      for a second organization's run of the same evaluation?
  answered_by:
  - single-party-reporting
- ask:
    plain: which types of AI tests are mostly scored by the companies that built the models,
      rather than by outsiders?
    jargon: how does the rate of first-party-only reporting vary across benchmark categories
      such as agentic, general and safety?
    task: how do I find out whether agentic or safety scores for a model have any independent
      reporting behind them?
    practitioner: for agentic capability claims, can I expect an independent evaluation to
      compare against, or only the developer's own numbers?
  answered_by:
  - first-party-only-by-category
- ask:
    plain: do different websites report different benchmark scores for GPT-5, and by how much?
    jargon: how do reported GPT-5 results vary across reporting organizations on MATH-500,
      and how many lack decoding configuration fields?
    task: how do I reconcile conflicting MATH-500 numbers reported for GPT-5 by different
      evaluation organizations?
    practitioner: which GPT-5 math benchmark number should I cite when several organizations
      report different ones?
  answered_by:
  - gpt5-walkthrough
- ask:
    plain: do scores reported for the MMLU-Pro test disagree depending on who ran it?
    jargon: what cross-party score divergence and missing-field rates appear when MMLU-Pro
      results are aggregated across reporting organizations?
    task: how do I check whether an MMLU-Pro number for a model like Llama 3.2 is consistent
      across the sources that report it?
    practitioner: if I am comparing models on MMLU-Pro, can I mix numbers from different leaderboards?
  answered_by:
  - mmlu-pro-walkthrough
- ask:
    plain: where do the rules for what an AI evaluation report should contain actually come
      from?
    jargon: what corpus of recommendation items and stakeholder input was coded to derive
      the Evaluation Cards five-part reporting structure?
    task: how do I justify the set of fields I ask evaluators to report, rather than inventing
      a checklist?
    practitioner: is the evaluation reporting structure grounded in prior recommendations,
      or is it one team's opinion about what to record?
  answered_by:
  - framework-derivation
- ask:
    plain: can model and test names collected from many different websites be matched up reliably
      to one canonical name?
    jargon: what accuracy does the Evaluation Cards entity resolver achieve when canonicalizing
      model, benchmark and metric strings?
    task: how do I merge evaluation results from several leaderboards when each one spells
      the model and benchmark names differently?
    practitioner: if I build on this aggregated evaluation corpus, how much name-matching
      error should I expect on benchmarks versus models?
  answered_by:
  - entity-resolver-accuracy
- ask:
    plain: why is saying "model X scores 0.99 on MATH" not enough to know what was actually
      measured?
    jargon: how does a five-level rollout hierarchy of family, composite, benchmark, split
      and metric resolve an aggregate benchmark claim to its underlying metric?
    task: how do I trace a headline benchmark number back to the specific split and metric
      it came from?
    practitioner: if I record evaluation results in my own database, is a flat model-benchmark-score
      row going to be enough?
  answered_by:
  - rollout-hierarchy
- ask:
    plain: can the same record of how a model was tested be shown both to a researcher and
      to someone without a technical background?
    jargon: how do the Evaluation Cards reader modes surface or compress the same underlying
      record for research versus policy audiences?
    task: how do I present missing evaluation configuration fields to a non-technical reader
      without dumbing down the underlying record?
    practitioner: do I need two separate documents for researchers and policy readers, or
      can one evaluation record serve both?
  answered_by:
  - reader-modes
- ask:
    plain: does a low documentation completeness number mean an AI model or its developer
      is bad?
    jargon: does Evaluation Cards convert documentation completeness into letter grades, pass/fail
      thresholds or developer rankings?
    task: how do I report gaps in evaluation documentation without turning them into a scorecard
      that penalizes developers?
    practitioner: if my model's card shows low completeness, is that a quality judgement I
      have to answer for?
  answered_by:
  - no-grades
- ask:
    plain: is there a project that pulls benchmark descriptions, evaluation run details and
      model metadata into one place?
    jargon: which work composes benchmark metadata schemas, evaluation run records and model
      catalogs into a single reader-facing evaluation record?
    task: where do I start reading if I want to build infrastructure for AI evaluation reporting
      rather than another documentation standard?
    practitioner: do I have to fill in yet another documentation template, or is there an
      integration layer that assembles evaluation records from what already exists?
  answered_by:
  - context-composition
  - context-monitoring-instrument
- ask:
    plain: is anyone actually keeping track of how well AI evaluation results are being reported
      across the whole field?
    jargon: what deployed instrument monitors reporting completeness and cross-party divergence
      across thousands of models, benchmarks and reported results?
    task: how do I get an at-scale picture of evaluation reporting gaps without auditing each
      leaderboard by hand?
    practitioner: is there a live, open tool I can point at to show how public AI evaluation
      reporting currently stands?
  answered_by:
  - context-monitoring-instrument
misreadings:
- A high Evaluation Cards completeness score means a benchmark is well documented, not that
  the underlying evaluation was rigorous; completeness measures artifact-side reporting adequacy
  only.
- 'Evaluation Cards is not a new checklist for evaluators to fill in by hand: fields are populated
  by extraction from Auto-BenchmarkCards, EEE and model catalogs, with only lifecycle_status
  reserved for voluntary disclosure.'
- 'The reproducibility figures describe the public reporting record, not the evaluations themselves:
  a result flagged as a reproducibility gap may have been run carefully but reported without
  temperature or max_tokens.'
- The corpus is not a census of public AI evaluation reporting; results not contributed to
  EEE or picked up by the scrapers are absent, and English-language benchmarks and frontier-scale
  models are overrepresented.
- Evaluation Cards covers LLM evaluation reporting only and does not currently support other
  AI systems or modalities.
- 'Cross-party score divergence flags are not proof that one reporter is wrong: the 5% threshold
  is applied uniformly across metrics and ignores sampling variance, and benchmark misresolution
  can inflate the flags.'
terminology:
  rollout hierarchy: A five-level structure — family, composite, benchmark, split, metric
    — through which every reported evaluation score resolves to an explicit traceable path
    instead of a flat (model, benchmark, score) triple.
  minimal reproducibility sub-schema: 'The small set of fields required to re-run a reported
    evaluation: temperature and max_tokens, extended with harness, eval_plan and eval_limits
    for agentic evaluations.'
  reporting completeness: The share of a 28-field operationalized reporting schema populated
    for a benchmark, where fields with sub-items score as the fraction of sub-items present.
  provenance signal: An annotation on a reported score stating whether the evaluator was first-party,
    third-party or collaborative, whether any other party reported the same score, and which
    risk categories the benchmark carries.
  comparability flag: A warning raised when reported scores for the same model, benchmark
    and metric differ by more than 5% of the metric's range, either across setup variants
    or across reporting parties.
  reader modes: Two renderings of one identical evaluation record — a research mode foregrounding
    methodology and configuration, and a summary mode foregrounding plain-language accountability
    — differing only in which fields are surfaced, compressed or reframed.
links_extra:
  demo: https://evalcards.evalevalai.com
  code: https://huggingface.co/spaces/evaleval/general-eval-card/tree/main
  project: https://evalevalai.com/
---
