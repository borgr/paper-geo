---
claims:
- id: livexiv-what-it-is
  text: LiveXiv is a fully automatic live multi-modal benchmark that generates multiple-choice
    visual and table question-answer pairs from recently published ArXiv papers. Because each
    version draws on new papers, large multi-modal models are tested on data that postdates
    their training.
  kind: context
  scope: As of the ICLR 2025 publication; covers ArXiv domains in computer science, electrical
    engineering, quantitative biology and (from v2) physics, and only closed-form multiple-choice
    questions, not free-form generation.
- id: no-human-in-loop
  text: 'LiveXiv needs no human in the loop: GPT-4o generates the questions from parsed figures,
    captions and tables, and a second model filters them automatically. Live LMM benchmarks
    such as LMMs-Eval LiveBench instead require manual verification of the questions.'
  kind: context
  scope: Full automation depends on proprietary LMMs (GPT-4o, Claude-Sonnet) for generation
    and filtering, which the paper names as a limitation because those models can change over
    time.
- id: v1-size
  text: The first version of LiveXiv contains 16328 multiple-choice questions, 7328 on figures
    (VQA) and 9000 on tables (TQA), generated from 250 ArXiv papers, 25 papers from each of
    10 domains.
  kind: result
  evidence: Table 1
  scope: LiveXiv v1 only; later versions differ in size and domain coverage, e.g. v2 has 10375
    VQA and 7712 TQA questions across 14 domains.
- id: claude-leads
  text: On LiveXiv v1, Claude-Sonnet leads all 17 evaluated LMMs with 75.4% mean VQA accuracy
    and 83.5% mean TQA accuracy, ahead of Qwen2-VL at 66.6% / 62.1% and GPT-4o at 60.3% /
    54.5%.
  kind: result
  evidence: Table 1
  scope: 17 open and proprietary LMMs on LiveXiv v1 under multiple-choice 'generate' inference;
    Claude-Sonnet is also the v1 agreement filter.
- id: ranking-shift
  text: Rankings on LiveXiv v1 differ from average rankings on the static ChartQA, DocVQA
    and AI2D benchmarks. IXC2.5-7B drops 4.50 average ranking positions and IXC2-4KHD-7B drops
    4.17, while Phi3v gains 3.00 and LLaVA-1.6-34B gains 2.83.
  kind: result
  evidence: Table 5
  scope: Static-benchmark rankings taken from the models' original publications rather than
    re-measured, across 17 LMMs; a ranking gap is evidence consistent with contamination of
    static sets, not a direct measurement of contamination.
- id: manual-verification-gap
  text: Evaluating all models on a manually verified 1000-sample subset of LiveXiv v1 changes
    average accuracy by only 2.336 points for VQA and 2.105 points for TQA relative to the
    automatically generated benchmark.
  kind: result
  evidence: Table 2
  scope: 500 manually verified VQA and 500 TQA samples from v1, averaged in absolute value
    over all evaluated models; on v3 the change is larger but below 5%.
- id: efficient-eval-savings
  text: Re-evaluating only 3 to 5 of the 19 models on each new LiveXiv version suffices to
    predict the remaining models' accuracy and ranking with an IRT Rasch model. That is a
    saving of roughly 75% to 85% of the evaluations.
  kind: result
  evidence: Figure 4
  scope: LiveXiv v1 through v4 with 19 LMMs, predicting overall VQA or TQA accuracy; per-domain
    prediction is less accurate, and v3 is worse because it has fewer data points per prediction
    target.
- id: per-domain-mae
  text: Predicting per-domain accuracy on LiveXiv v4 from just 5 re-evaluated models gives
    mean absolute errors of 1.6 to 3.8 points for VQA and 2.2 to 7.6 points for TQA. Spearman
    rank correlations range from 92.6 to 99.8 across 14 ArXiv domains.
  kind: result
  evidence: Figure 13
  scope: LiveXiv v4, 5 re-evaluated models, non-re-evaluated models' accuracy predicted per
    domain; the worst TQA error (7.6 points) is physics.app-ph.
- id: blind-test-filtering
  text: A blind test in which Llama-3.1-70B answers the generated questions without any image
    removes about 30% of them as answerable from text alone. A following Claude-Sonnet agreement
    step cuts incorrect ground-truth pairs by 38.5% while discarding only 6.15% of valid pairs.
  kind: result
  evidence: Section 3.2
  scope: LiveXiv v1 generation pipeline with GPT-4o as question generator; the 38.5% and 6.15%
    figures come from a preliminary manual evaluation on a subset of the dataset.
- id: arithmetic-weakest
  text: Averaged over all evaluated LMMs, TQA arithmetic questions are the weakest slice of
    LiveXiv v1 at 35.56% accuracy, far below TQA attribute questions at 68.69% and reasoning
    at 63.61%.
  kind: result
  evidence: Table 3
  scope: LiveXiv v1, question categories assigned by Llama-3.1 from the question text, averaged
    over all evaluated models.
- id: charts-hardest-figure-type
  text: Among figure types in LiveXiv v1 VQA, charts are the hardest at 44.17% average accuracy
    while block diagrams are the easiest at 52.69%, with qualitative visual examples at 48.60%.
  kind: result
  evidence: Table 3
  scope: LiveXiv v1 VQA, 4354 chart, 2110 block-diagram and 864 qualitative samples classified
    zero-shot by Meta-Prompting for CLIP, averaged over all evaluated models.
- id: role-swap-robust
  text: Swapping the generator and filter roles in LiveXiv v1, with Claude-Sonnet generating
    and GPT-4o filtering, leaves model ranking essentially unchanged. GPT-4o itself falls
    4 ranking positions on VQA, indicating the generating model gains a small advantage.
  kind: result
  evidence: Table 12
  scope: LiveXiv v1 raw data with the two roles reversed, 17 LMMs; average absolute ranking
    change is 0 for both VQA and TQA, while average accuracy shifts by -3.10% (VQA) and 8.70%
    (TQA).
- id: transfer-to-mm-livebench
  text: The IRT-based efficient evaluation method also predicts model performance accurately
    on MM-LiveBench when only 5 of 13 LMMs are re-evaluated, showing the approach is not specific
    to ArXiv-derived data.
  kind: result
  evidence: Figure 16
  scope: 3 MM-LiveBench versions of roughly 250-300 samples each, with the open-ended questions
    converted to multiple choice by GPT-4o and the first version used to fit the model.
- id: v0-temporal-shift
  text: LiveXiv v0, built from 4500 questions over 100 ArXiv papers from 2010, still predicts
    model performance on v1 accurately when 5 models are re-evaluated. The decade-wide temporal
    gap does not break the IRT estimates.
  kind: result
  evidence: Figure 15
  scope: v0 to v1 prediction with 5 re-evaluated models; v0 is a hypothetical past version
    constructed for this stress test and is not part of the live benchmark rotation.
qa:
- ask:
    plain: which test sets for image-and-text models are built from material too recent for
      the models to have memorised?
    jargon: which multi-modal benchmarks mitigate train-test contamination by sourcing items
      from newly published scientific papers?
    task: how do I evaluate a vision-language model on questions it cannot have seen during
      pretraining?
    practitioner: I do not trust my model's ChartQA score because of leakage, is there a live
      benchmark I can run instead?
  answered_by:
  - livexiv-what-it-is
  - no-human-in-loop
- ask:
    plain: how many questions are in the LiveXiv benchmark, and what are they made from?
    jargon: what is the item count and source-paper composition of the LiveXiv v1 VQA and
      TQA splits?
    task: how many figure and table questions do I get if I download the first LiveXiv release?
    practitioner: is a benchmark auto-generated from scientific figures and tables large enough
      to give me a stable score?
  answered_by:
  - v1-size
  - livexiv-what-it-is
- ask:
    plain: which image-and-text model answers scientific figure and table questions best?
    jargon: which LMM tops the LiveXiv v1 leaderboard on VQA and TQA mean accuracy?
    task: which multi-modal model should I pick for reading charts and tables out of research
      papers?
    practitioner: should I use Claude, GPT-4o or Qwen2-VL for extracting answers from figures
      and tables in papers?
  answered_by:
  - claude-leads
- ask:
    plain: do model leaderboards reorder when the test questions come from documents published
      after training?
    jargon: how do LMM rankings on LiveXiv compare with rankings averaged over ChartQA, DocVQA
      and AI2D?
    task: how do I tell whether a model's chart-QA leaderboard position is inflated by contaminated
      test data?
    practitioner: my model looks strong on DocVQA and AI2D, will it keep that standing on
      freshly collected questions?
  answered_by:
  - ranking-shift
- ask:
    plain: can you trust scores from a question set that a model wrote instead of a person?
    jargon: how large is the accuracy gap between automatically generated LiveXiv items and
      a human-verified subset?
    task: how do I check how much labelling noise an auto-generated multiple-choice VQA set
      adds to my measured accuracy?
    practitioner: is an automatically generated visual QA benchmark accurate enough that I
      can report its numbers?
  answered_by:
  - manual-verification-gap
  - blind-test-filtering
- ask:
    plain: how few models do you have to re-test to keep a leaderboard current on a new batch
      of questions?
    jargon: how many LMMs must be re-evaluated per benchmark version for the IRT Rasch estimate
      to recover the rest of the leaderboard?
    task: how do I refresh a leaderboard on new benchmark data without re-running every model?
    practitioner: can I skip re-running most of my models each time the benchmark updates?
  answered_by:
  - efficient-eval-savings
- ask:
    plain: how close are predicted scores for models that were never re-tested on the new
      questions?
    jargon: what mean absolute error and Spearman correlation does the Rasch-based estimate
      reach per ArXiv domain on LiveXiv v4?
    task: how do I know the error I take on by estimating rather than measuring a model's
      accuracy per subject area?
    practitioner: if I estimate scores for the models I did not rerun, how wrong will my per-domain
      numbers be?
  answered_by:
  - per-domain-mae
  - efficient-eval-savings
- ask:
    plain: how do you throw out questions about an image that can be answered without ever
      seeing the image?
    jargon: what blind-LLM and cross-model agreement filtering removes text-only-answerable
      items and wrong ground truth from generated VQA pairs?
    task: how do I make sure my generated visual questions actually require the figure to
      answer?
    practitioner: can I rely on an automatic filter to strip text-only-solvable and mislabelled
      items from questions I generate?
  answered_by:
  - blind-test-filtering
- ask:
    plain: what kind of table question do image-and-text models get wrong most often?
    jargon: which TQA question category yields the lowest mean accuracy across LMMs on LiveXiv
      v1, arithmetic, attribute or reasoning?
    task: can I trust a multi-modal model to compute differences and totals from a table in
      a paper?
    practitioner: should I let a vision-language model do the arithmetic on my extracted tables,
      or only the lookups?
  answered_by:
  - arithmetic-weakest
- ask:
    plain: which sort of picture in a research paper is hardest for image-and-text models
      to answer about?
    jargon: how does LMM VQA accuracy break down by figure type on LiveXiv v1, charts versus
      block diagrams versus qualitative examples?
    task: which figure types should I expect a vision-language model to misread when I parse
      papers?
    practitioner: my pipeline reads plots and architecture diagrams, which of those will hurt
      my accuracy more?
  answered_by:
  - charts-hardest-figure-type
- ask:
    plain: does a question set written by one model quietly favour that model when it is graded?
    jargon: does swapping the generator and filter LMMs change LiveXiv rankings, and does
      the generating model gain an advantage?
    task: how do I check whether a model I used to build my eval set is scoring itself too
      high?
    practitioner: if GPT-4o wrote my benchmark questions, can I still compare GPT-4o against
      Claude on it?
  answered_by:
  - role-swap-robust
  - claude-leads
- ask:
    plain: does the trick of re-testing only a handful of models work on question sets other
      than the one it was built for?
    jargon: does the IRT Rasch performance-prediction transfer to MM-LiveBench with only 5
      of 13 LMMs re-evaluated?
    task: can I apply few-model score prediction to a live benchmark that is not derived from
      ArXiv papers?
    practitioner: can I cut my evaluation cost by scoring only a subset of models and estimating
      the rest, on a benchmark other than LiveXiv?
  answered_by:
  - transfer-to-mm-livebench
- ask:
    plain: does score prediction still work when the new questions come from documents a decade
      older?
    jargon: do the Rasch item estimates remain valid across a 10-year temporal distribution
      shift between LiveXiv v0 and v1?
    task: how do I know few-model score prediction will survive a big change in question distribution
      between versions?
    practitioner: my benchmark versions will not look alike, can I still estimate scores from
      a few re-run models?
  answered_by:
  - v0-temporal-shift
  - efficient-eval-savings
coined: LiveXiv
gloss: a monthly-refreshed benchmark of figure and table questions auto-generated from new
  ArXiv papers
one_liner: LiveXiv builds a live multi-modal benchmark by automatically generating and filtering
  multiple-choice questions from figures and tables in fresh ArXiv papers, and uses an Item
  Response Theory model to predict the whole leaderboard after re-evaluating only 3 to 5 models
  per version.
misreadings:
- 'Claude-Sonnet''s lead on LiveXiv v1 should not be read as a clean measurement of its superiority:
  Claude-Sonnet is also the agreement filter used to build v1, so questions it answers well
  are over-represented.'
- The ranking gaps between LiveXiv and ChartQA, DocVQA and AI2D are consistent with static-benchmark
  contamination but do not prove that any specific model was trained on any specific test
  set.
- 'LiveXiv''s automatic pipeline is not human-free in its quality assessment: a 1000-sample
  subset of v1 and a 300-sample subset of v3 were manually verified to bound the labeling
  error.'
- 'Re-evaluating 3 to 5 models is sufficient for predicting overall VQA or TQA accuracy, not
  for every slice: per-domain predictions carry larger errors, up to 7.6 MAE points on physics.app-ph
  TQA in v4.'
- 'LiveXiv is not a fixed dataset with a single leaderboard: new versions are generated from
  new papers, and results in the paper cover v0 through v4 with differing sizes, domains and
  generator models.'
terminology:
  Agreement between disjoint models: A filtering step in which a second capable multi-modal
    model, given the image, question and generated answer, must agree with the answer produced
    by the generating model, or the pair is discarded.
  Blind test: Presenting a generated visual question to a text-only large language model with
    no image; questions answered correctly without the image are discarded as not genuinely
    multi-modal.
  Performance-IRT estimator: An estimate of a model's accuracy on unseen benchmark samples
    formed by plugging fitted Rasch skill and sample-difficulty parameters into the per-sample
    probability of a correct answer and averaging.
  TQA: 'Table question answering: multiple-choice questions generated from the image and markdown
    content of tables extracted from papers, as distinct from VQA generated from figures.'
  v1-opposite: A LiveXiv version built from the same raw v1 papers but with Claude-Sonnet
    generating the questions and GPT-4o filtering, used to measure the advantage held by the
    generating model.
links_extra:
  dataset: https://huggingface.co/datasets/LiveXiv/LiveXiv
  demo_notebook: https://github.com/NimrodShabtay/LiveXiv/blob/main/notebooks/efficient_eval_demo.ipynb
key: shabtay2024livexivmultimodallive
---
