<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from hand fix: named the subject in 2 phrasings. Every claim, number
and scope condition below is a machine's reading of the paper and needs your eyes.

THIS PAPER ALREADY HAS A LIVE SIDECAR, and this draft would replace it. Start here:

  diff data/sidecars/active-learning-for-bert-an-empirical-study.md data/sidecars/drafts/active-learning-for-bert-an-empirical-study.md

Anything the live file says in your own words is worth keeping over a rewrite of the
same point, so read that diff before the checklist below.

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

Then, if the replacement is the one you want:

  python scripts/draft_sidecars.py --accept active-learning-for-bert-an-empirical-study --replace

Stamp: spec=4b2236733458 checks=pass body=36f32a38825a
-->
---
key: eindor2020active
one_liner: A 2,520-run study of 7 active learning strategies on top of BERT for binary text
  classification with a 100-example seed and 50-example batches, showing the largest gains
  in the realistic case where the seed comes from a keyword query over a rare positive class.
claims:
- id: practical-gain
  kind: result
  text: Active learning strategies on top of BERT improve F1 over a random-selection baseline
    by 4-8% on average in the imbalanced-practical scenario. In that scenario the initial
    labeled seed of 100 examples is drawn from a keyword query.
  scope: Binary classification on 4 datasets with a queryable positive class (ISEAR fear,
    TREC location, Wiki attack, AG's News-imb world); BERT-base, 5 iterations of 50 labels,
    dev set used for model selection.
  evidence: Section 4
- id: significance-imbalanced
  kind: result
  text: All 6 non-random active learning strategies tested with BERT beat random selection
    significantly in both imbalanced scenarios, with Wilcoxon p < 10^-2 after Bonferroni correction.
    In the balanced scenario EGL and Perceptron Ensemble show no significant gain.
  scope: 10 binary datasets split across 14 dataset-scenario combinations, 5 seeds x 5 iterations
    per strategy; p-values computed over all (strategy, random) result pairs; accuracy used
    for balanced, F1 for imbalanced scenarios.
  evidence: Table 3
- id: no-winner
  kind: result
  text: 'No single active learning strategy consistently outperforms the others when paired
    with BERT: pairwise Wilcoxon tests across the 3 scenarios find no significant performance
    difference between any pair of the 7 strategies.'
  scope: Least Confidence, Monte Carlo Dropout, Perceptron Ensemble, EGL, Core-Set, DAL and
    Random on binary tasks, 100-example seed plus 5 batches of 50; larger budgets and multi-class
    tasks untested.
  evidence: Section 4
- id: recall-driven
  kind: result
  text: When BERT is seeded with a biased keyword-query sample of the minority class, the
    F1 gain from active learning is dominated entirely by rising recall. In the unbiased imbalanced
    seeding the gain comes mostly from precision.
  scope: The 4 imbalanced-practical datasets versus the 6 imbalanced datasets, BERT-base,
    F1 at the default 0.5 threshold; precision and recall curves are in Appendix Figures 4
    and 5.
  evidence: Section 4
- id: gap-bridged
  kind: result
  text: A keyword-query seed gives BERT a worse initial F1 than an unbiased sample of positives.
    After several active learning iterations of 50 labels each, the two seeding regimes converge
    to similar classification performance.
  scope: Compared at iteration 0 versus later iterations on the datasets run in both imbalanced
    and imbalanced-practical scenarios; simple string-match queries whose own recall is low.
  evidence: Figure 1
- id: unstable-random-seed
  kind: result
  text: For datasets whose positive class prior is at or below 15%, a random seed of 100 labeled
    instances led to unstable BERT fine-tuning runs. The study handled this by adding 100
    further instances weakly labeled as negative.
  scope: BERT-base fine-tuned for 5 epochs at learning rate 5e-5, batch size 50, maximum sequence
    length 100 tokens; observed on the 6 skewed datasets, with the instability data not shown
    in the paper.
  evidence: Section 3.2
- id: diversity-dal
  kind: result
  text: Discriminative Active Learning selects the most diverse and the most representative
    batches of the 7 strategies compared using BERT [CLS] representations. Greedy Core-Set
    scores low on representativeness except in the imbalanced-practical scenario.
  scope: Measured on the first 50-example batch after the initial BERT model, averaged over
    datasets and seeds per scenario; diversity per Zhdanov (2019) and representativeness from
    inverse KNN-density with K=10 on Euclidean [CLS] distances.
  evidence: Figure 2
- id: low-overlap
  kind: result
  text: 'Batches chosen by different active learning strategies over the same BERT model overlap
    little: expected pairwise batch overlap does not exceed 15%, with the highest overlap
    between EGL and Least Confidence.'
  scope: 50-example batches from the same unlabeled pool and the same trained BERT model,
    across 7 strategies and 14 dataset-scenario combinations; combining low-overlap strategies
    untested.
  evidence: Section 5
- id: runtime
  kind: result
  text: 'Per-iteration batch selection cost with BERT differs by orders of magnitude across
    strategies: assuming 7,000 unlabeled examples, random selection takes under 1 second and
    EGL 1,106 seconds. Dropout takes 840 seconds, Perceptron Ensemble 370, DAL 167, Core-Set
    98 and Least Confidence 84.'
  scope: Selection time only, excluding BERT fine-tuning; Intel Xeon E5-2699 v4 CPUs with
    a single Nvidia Tesla K80 GPU per run; dominated by BERT inference for every strategy
    except random.
  evidence: Table 2
- id: first-systematic-bert-al
  kind: context
  text: '"Active Learning for BERT: An Empirical Study" is a systematic empirical comparison
    of classical and deep active learning strategies on top of BERT for text classification.
    It covers 10 binary datasets and 2,520 fine-tuning runs.'
  scope: 'As of EMNLP 2020: earlier deep-AL work on text either used non-BERT models or applied
    a narrow set of strategies to one or two tasks with specific BERT variants; binary classification
    only, English datasets, BERT-base.'
  evidence: Section 2
- id: practical-scenario-framing
  kind: context
  text: 'The imbalanced-practical setting introduced in "Active Learning for BERT: An Empirical
    Study" is a low-resource evaluation protocol where the labeled seed comes from a simple
    keyword query. It replaces the usual assumption of an unbiased sample of the rare positive
    class.'
  scope: Applied to 4 datasets for which a simple string or sub-string match query with enough
    hits could be written; the queries are deliberately naive and better queries are likely
    to exist.
  evidence: Section 3.2
- id: framework-release
  kind: context
  text: '"Active Learning for BERT: An Empirical Study" releases an open-source low-resource
    text classification framework with the 10 datasets, implementations of the 7 active learning
    strategies and an automatic evaluation harness. New AL strategies can be plugged in.'
  scope: Framework as released at publication in 2020, built around BERT-base and binary classification
    tasks; released at github.com/IBM/low-resource-text-classification-framework.
  evidence: Section 3.6
qa:
- ask:
    plain: does choosing which examples to label help when there are only a few hundred labels?
    jargon: how much F1 does active learning gain over random selection when fine-tuning BERT
      on imbalanced text classification?
    task: how do I spend a tiny annotation budget on the examples that help a text classifier
      most?
    practitioner: I can label 500 examples -- should I choose them with active learning or
      at random?
  answered_by:
  - practical-gain
  - significance-imbalanced
- ask:
    plain: which way of choosing examples to label works best with a transformer classifier?
    jargon: is there a clear winner among uncertainty, core-set and discriminative active
      learning strategies for BERT?
    task: how do I pick an acquisition strategy for active learning with BERT?
    practitioner: which active learning strategy should I implement first?
  answered_by:
  - no-winner
  - runtime
- ask:
    plain: can a classifier recover if its first labeled examples all came from one keyword
      search?
    jargon: does a keyword-query seed permanently depress BERT classification quality relative
      to an unbiased positive sample?
    task: how do I bootstrap a rare-class classifier when the only way to find positives is
      a keyword query?
    practitioner: my seed set came from a keyword search -- is my classifier stuck with that
      bias?
  answered_by:
  - gap-bridged
  - recall-driven
  - practical-scenario-framing
- ask:
    plain: does choosing examples to label find more of the rare cases, or judge the found
      ones better?
    jargon: does the active learning F1 gain on skewed data come from precision or from recall?
    task: how do I tell whether active learning is improving coverage of a rare class or its
      precision?
  answered_by:
  - recall-driven
- ask:
    plain: how much computation does each way of choosing examples to label cost per round?
    jargon: what is the per-iteration selection runtime of EGL, Monte Carlo Dropout, DAL,
      Core-Set and Least Confidence over 7,000 unlabeled examples?
    task: how do I keep the selection step from costing more than the fine-tuning step?
    practitioner: which acquisition strategies are cheap enough for me to run every round?
  answered_by:
  - runtime
- ask:
    plain: why does fine-tuning go unstable when a rare class barely appears in the first
      labeled batch?
    jargon: what makes BERT fine-tuning unstable at a positive-class prior at or below 15%
      with a 100-instance random seed, and what stabilised it?
    task: how do I stabilise fine-tuning on a small, highly imbalanced seed without buying
      more labels?
    practitioner: my seed set has almost no positives and training keeps collapsing -- what
      do I do?
  answered_by:
  - unstable-random-seed
- ask:
    plain: do different ways of choosing examples to label end up picking the same ones?
    jargon: how much do batches selected by different acquisition functions over the same
      BERT model overlap?
    task: how do I tell whether combining two acquisition strategies could add anything?
  answered_by:
  - low-overlap
- ask:
    plain: which ways of choosing examples cover the data broadly rather than picking oddities?
    jargon: how do diversity and representativeness differ across acquisition strategies measured
      in BERT [CLS] space?
    task: how do I check whether an acquisition strategy is selecting outliers?
  answered_by:
  - diversity-dal
- ask:
    plain: what is a good study comparing ways of choosing which text examples to label?
    jargon: what work systematically compared classical and deep active learning strategies
      on top of BERT?
    task: where should I start reading about active learning for text classification with
      transformers?
    practitioner: which paper should I cite for whether active learning helps BERT?
  answered_by:
  - first-systematic-bert-al
  - framework-release
- ask:
    plain: is there code and data for trying out example-selection strategies on text classification?
    jargon: what open-source low-resource text classification framework, datasets and strategy
      implementations were released?
    task: how do I benchmark a new acquisition strategy against existing ones without rebuilding
      a text classification harness from scratch?
    practitioner: can I plug my own selection strategy into an existing harness?
  answered_by:
  - framework-release
- ask:
    plain: how many datasets and training runs went into comparing ways of choosing which
      text examples to label?
    jargon: how many binary datasets and BERT fine-tuning runs back the active learning comparison?
    practitioner: is the evidence broad enough for me to rely on these active learning conclusions?
  answered_by:
  - first-systematic-bert-al
  - significance-imbalanced
misreadings:
- The 4-8% F1 gain from active learning is an average over the imbalanced-practical scenario
  only; in the balanced scenario the gains are smaller and EGL and Perceptron Ensemble are
  not significantly better than random selection at all.
- 'The study does not identify a best acquisition function: pairwise significance tests find
  no strategy reliably better than any other, so citing it as evidence for Core-Set, DAL or
  least confidence specifically is a misreading.'
- Findings cover binary classification with BERT-base and a budget of a 100-example seed plus
  5 batches of 50 actively selected labels; multi-class tasks, regression, larger budgets
  and later BERT variants were not tested.
- The keyword queries used to build the biased seed are deliberately simple string matches
  with low recall, not tuned retrieval systems, so the reported initial F1 is not a bound
  on what query-based bootstrapping can achieve.
- Runtimes in the study are batch-selection times, not end-to-end iteration costs, and exclude
  BERT fine-tuning.
terminology:
  imbalanced-practical scenario: An active learning setup for a rare target class in which
    the initial labeled seed is drawn from the results of a simple keyword query, yielding
    a positive-enriched but biased sample, rather than from an unbiased sample of positives.
  imbalanced scenario: An active learning setup for a target class with prior at or below
    15% in which the initial seed's 100 fully labeled examples are drawn at random from the
    dataset's positives, assumed available via high-precision heuristics.
  Perceptron Ensemble (PE): An uncertainty-sampling strategy that averages the predictions
    of 10 perceptrons trained on the [CLS] vectors of a fine-tuned BERT model, used as a cheap
    substitute for an ensemble of full BERT models.
  Representativeness of a batch: One over the average KNN-density of the batch's instances,
    where density is the mean Euclidean distance from an instance to its K=10 nearest neighbours
    in the unlabeled pool in [CLS] representation space; low values indicate outlier selection.
  Diversity of a batch: The inverse of the average, over all unlabeled instances, of the minimum
    Euclidean distance from that instance to any member of the selected batch in [CLS] representation
    space.
---
