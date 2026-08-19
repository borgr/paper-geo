<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced via a forced tool call) + 2 repair rounds. Every claim, number
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

Then promote it:  python scripts/draft_sidecars.py --accept active-learning-for-bert-an-empirical-study

Stamp: spec=8f05813a4658 checks=pass body=1519ca57231e
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
- q:
  - Does active learning actually help BERT, or is BERT already good enough with few labels?
  - Can active learning improve BERT text classification under a tiny annotation budget?
  - How much does active learning gain over random sampling when fine-tuning BERT?
  answers:
  - practical-gain
  - significance-imbalanced
- q:
  - Which active learning strategy works best with BERT?
  - Is there a clear winner among uncertainty, core-set and discriminative active learning
    for BERT?
  - Should I pick least confidence or Core-Set for active learning with a transformer classifier?
  answers:
  - no-winner
  - runtime
- q:
  - What happens if I bootstrap a classifier from keyword search results instead of random
    labeling?
  - Can active learning recover from a biased seed collected with keyword queries?
  - Does starting from a keyword-query seed permanently hurt classifier quality?
  answers:
  - gap-bridged
  - recall-driven
  - practical-scenario-framing
- q:
  - Does active learning improve precision or recall for rare-class text classification?
  - Where does the F1 improvement come from when using active learning on skewed data?
  answers:
  - recall-driven
- q:
  - How expensive is each active learning strategy to run per iteration with BERT?
  - Which active learning selection methods are computationally cheap enough for a transformer?
  - What is the runtime cost of EGL and Monte Carlo Dropout selection compared to random?
  answers:
  - runtime
- q:
  - Is BERT fine-tuning stable when trained on 100 randomly labeled examples of a rare class?
  - What goes wrong when fine-tuning BERT on a small, highly imbalanced labeled seed?
  - How can a small imbalanced seed set be stabilised without more annotation budget?
  answers:
  - unstable-random-seed
- q:
  - Do different active learning strategies pick the same examples?
  - How much do batches selected by different acquisition functions overlap?
  - Is there room to combine complementary active learning strategies?
  answers:
  - low-overlap
- q:
  - Which acquisition strategies select diverse and representative batches?
  - Does Core-Set pick outliers when used with BERT representations?
  - How do diversity and representativeness differ across active learning strategies for BERT?
  answers:
  - diversity-dal
- q:
  - What should I read first about active learning with pre-trained language models?
  - Is there a good empirical study comparing active learning strategies for text classification?
  - Which paper established whether active learning helps BERT?
  answers:
  - first-systematic-bert-al
  - framework-release
- q:
  - Is there code and data available for benchmarking active learning strategies on text classification?
  - Where can I find an open-source framework for low-resource text classification experiments?
  answers:
  - framework-release
- q:
  - How many datasets and runs does the BERT active learning study cover?
  - What experimental scale backs the claims about active learning with BERT?
  answers:
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
