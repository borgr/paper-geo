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
- q:
  - What is a good benchmark for testing multi-modal models on data they were not trained
    on?
  - Which benchmarks avoid test set contamination for vision-language models?
  - Where should I start reading about live, contamination-free evaluation of large multi-modal
    models?
  answers:
  - livexiv-what-it-is
  - no-human-in-loop
- q:
  - How big is LiveXiv and where do its questions come from?
  - How many questions does the first version of LiveXiv contain?
  - How large is a benchmark auto-generated from figures and tables in ArXiv papers?
  answers:
  - v1-size
  - livexiv-what-it-is
- q:
  - Which model performs best on LiveXiv?
  - How do GPT-4o and Claude compare on scientific figure and table question answering?
  - What are the top accuracies on LiveXiv v1?
  answers:
  - claude-leads
- q:
  - Do model rankings change when you evaluate on fresh data instead of static benchmarks?
  - Is there evidence that ChartQA, DocVQA and AI2D scores are inflated by contamination?
  - Which models drop in ranking on LiveXiv compared to established benchmarks?
  answers:
  - ranking-shift
- q:
  - Are automatically generated VQA benchmarks reliable, or do they contain too many wrong
    answers?
  - How much does LiveXiv accuracy differ from a human-verified subset?
  - What is the labeling error rate of automatically generated question-answer pairs in LiveXiv?
  answers:
  - manual-verification-gap
  - blind-test-filtering
- q:
  - How can I avoid re-evaluating every model each time a benchmark is updated?
  - How many models must be re-run to estimate the rest of a leaderboard on new data?
  - How much compute does the LiveXiv efficient evaluation method save?
  answers:
  - efficient-eval-savings
- q:
  - How accurate is Item Response Theory at predicting unseen model accuracy per domain?
  - What is the prediction error when estimating model scores without re-evaluating them?
  - How well does the LiveXiv efficient evaluation predict per-domain accuracy?
  answers:
  - per-domain-mae
  - efficient-eval-savings
- q:
  - How are questions that can be answered without looking at the image removed?
  - What filtering keeps an automatically generated VQA set truly multi-modal?
  - Does LiveXiv check for hallucinated ground-truth answers?
  answers:
  - blind-test-filtering
- q:
  - What kinds of questions do multi-modal models fail most on scientific tables?
  - Are arithmetic questions harder for LMMs than reading or attribute questions?
  - Which question category is the weakest for large multi-modal models on table QA?
  answers:
  - arithmetic-weakest
- q:
  - Which type of scientific figure is hardest for vision-language models?
  - Do LMMs do better on charts or on block diagrams?
  - How does LMM accuracy vary by figure type in LiveXiv?
  answers:
  - charts-hardest-figure-type
- q:
  - Does using one model to generate questions and another to filter them bias an auto-generated
    VQA benchmark?
  - Is a benchmark generated by GPT-4o unfair to GPT-4o or to Claude?
  - What happens to LiveXiv rankings when the generator and filter models swap roles?
  answers:
  - role-swap-robust
  - claude-leads
- q:
  - Does the IRT efficient evaluation approach work on benchmarks other than LiveXiv?
  - Can performance prediction from a few re-evaluated models transfer to another live benchmark?
  - Was the efficient evaluation method tested on MM-LiveBench?
  answers:
  - transfer-to-mm-livebench
- q:
  - Does performance prediction survive a large distribution shift between benchmark versions?
  - What happens to the IRT estimates when the source papers are 10 years apart?
  - Was LiveXiv efficient evaluation stress-tested on older ArXiv papers?
  answers:
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
