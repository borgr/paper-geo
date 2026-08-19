<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced) + a targeted repair. Every claim, number
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

Then promote it:  python scripts/draft_sidecars.py --accept evaluation-cards-an-interpretive-layer-for-ai-evaluation-rep

Stamp: spec=8f05813a4658 checks=pass body=89d4f0838b5d
-->
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
- q:
  - How often do published AI evaluation results include the settings needed to re-run them?
  - What share of reported model scores are missing generation parameters like temperature
    and max_tokens?
  - Is public LLM benchmark reporting reproducible?
  answers:
  - repro-gap-corpus
- q:
  - Do model developers document their own evaluations less thoroughly than independent evaluators?
  - Are first-party reported benchmark scores less well documented than third-party ones?
  - Who reports more configuration detail, labs evaluating their own models or outside evaluators?
  answers:
  - first-vs-third-party-fields
- q:
  - How well documented are AI benchmarks themselves?
  - What fraction of benchmark documentation fields are actually populated in public reporting?
  - Which benchmark reporting fields are always present and which are always missing?
  answers:
  - completeness-median
- q:
  - How often is the same model and benchmark scored by more than one organization?
  - Do benchmark scores from different reporting organizations agree with each other?
  - How common is cross-party disagreement on LLM benchmark scores?
  answers:
  - single-party-reporting
- q:
  - Which kinds of benchmarks rely most on developer self-reported scores?
  - Are safety benchmarks or agentic benchmarks more likely to have only first-party results?
  - Where is independent evaluation reporting scarcest across benchmark categories?
  answers:
  - first-party-only-by-category
- q:
  - How much do GPT-5 benchmark scores differ between reporting sources?
  - What does an audit of reported GPT-5 evaluation results show about reproducibility?
  - Do different organizations report different MATH-500 scores for the same model?
  answers:
  - gpt5-walkthrough
- q:
  - What happens when MMLU-Pro results are aggregated across reporting organizations?
  - Do MMLU-Pro scores for the same model disagree across sources?
  - How complete is the reporting behind MMLU-Pro leaderboard scores?
  answers:
  - mmlu-pro-walkthrough
- q:
  - How was the Evaluation Cards reporting framework derived?
  - What evidence base underlies a reporting schema for AI evaluations?
  - How many papers and interviews went into the Evaluation Cards framework?
  answers:
  - framework-derivation
- q:
  - How accurately can model and benchmark names be resolved to canonical identifiers across
    evaluation sources?
  - Does entity matching across leaderboards and evaluation repositories work reliably?
  - How good is the Evaluation Cards canonicalization on models, benchmarks and metrics?
  answers:
  - entity-resolver-accuracy
- q:
  - Why is a flat (model, benchmark, score) triple not enough to describe an evaluation result?
  - How can an aggregate benchmark claim be traced to the specific subtask and metric behind
    it?
  - What is the Evaluation Cards rollout hierarchy for evaluation evidence?
  answers:
  - rollout-hierarchy
- q:
  - How can evaluation reporting serve both researchers and policymakers from the same record?
  - What are reader modes in Evaluation Cards?
  - Can the same evaluation record be rendered in plain language for non-technical readers?
  answers:
  - reader-modes
- q:
  - Does Evaluation Cards grade or rank model developers on their reporting?
  - Are benchmark documentation completeness scores turned into pass/fail judgements?
  - Is a documentation completeness score a measure of evaluation quality?
  answers:
  - no-grades
- q:
  - What should I read about standardizing how AI evaluation results are reported?
  - Is there a paper that unifies benchmark cards, evaluation run schemas and model metadata?
  - Where should I start reading about AI evaluation reporting infrastructure?
  answers:
  - context-composition
  - context-monitoring-instrument
- q:
  - Is there a tool that continuously monitors the state of public AI evaluation reporting?
  - What work measures reporting gaps across thousands of models and benchmarks at once?
  - Which paper audits public LLM evaluation reporting practice at scale?
  answers:
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
