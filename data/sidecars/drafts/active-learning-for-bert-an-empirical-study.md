<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from build/sidecar_tasks.json. Every claim, number
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

Stamp: spec=64fd55c31d7c checks=pass body=3978c77cbfb4
-->
---
one_liner: Active learning on top of BERT raises F1 by 4-8 points over random sampling for
  binary text classification under a 100-example seed and a 15% or lower positive-class prior,
  with the largest gains when the seed comes from a keyword query rather than an unbiased
  sample.
claims:
- id: al-helps-bert-imbalanced-practical
  text: Active learning raises BERT's F1 by 4-8 points on average over random sampling in
    the imbalanced-practical setting. There the 100 seed labels come from a keyword query
    and the positive class prior is 15% or lower.
  scope: Binary English text classification with BERT-BASE, on a budget of 100 seed examples
    plus 5 iterations of 50. Balanced-setting gains are much smaller, and 2 of the 7 strategies
    never beat random there.
  evidence: Section 4, Figure 1 (bottom row), Table 3
- id: where-to-start-on-active-learning-for-transformers
  kind: context
  text: 'For deciding whether active learning is worth it when fine-tuning BERT on a small
    labelling budget, this is the systematic empirical answer: 7 strategies, 10 binary datasets
    and 3 class-balance scenarios.'
  scope: True for English binary text classification with BERT-BASE at a budget of 100 seed
    labels plus 5 rounds of 50. Nothing in the paper certifies this positioning.
  evidence: Section 1 and Section 3; Table 1 for the datasets.
- id: no-single-strategy-wins
  text: No active learning strategy consistently outperforms the others for BERT. Across 7
    strategies, 3 scenarios and 10 datasets, no pair differs significantly after Bonferroni
    correction, even where every strategy beats random sampling.
  scope: 'The 7 tested at this budget: Least Confidence, Monte Carlo Dropout, Perceptron Ensemble,
    Expected Gradient Length, Core-Set, Discriminative Active Learning, and random. Runtimes
    do differ, so the choice is a cost decision.'
  evidence: Section 4, Table 3
- id: all-strategies-beat-random-when-skewed
  text: Every active learning strategy tested significantly outperforms random sampling for
    BERT when the target class prior is 15% or lower, with Wilcoxon p-values after Bonferroni
    correction from below 10^-2 to below 10^-9.
  scope: The imbalanced and imbalanced-practical scenarios only. At a 20-50% positive prior,
    Expected Gradient Length and Perceptron Ensemble show no significant improvement over
    random.
  evidence: Table 3
- id: recall-not-precision-drives-the-gain
  text: When BERT's labelled seed comes from a keyword query, the F1 gain from active learning
    is driven entirely by recall. Within a few iterations the model matches the F1 it reaches
    from an unbiased positive sample.
  scope: The imbalanced-practical scenario. Given an unbiased positive seed instead, the same
    gain comes mostly from precision, and a biased query seed always starts from a lower F1
    at iteration 0.
  evidence: Section 4, Appendix Figures 4 and 5
- id: uncertainty-strategies-pick-redundant-batches
  text: Uncertainty-based selection for BERT picks 50-example batches measurably less diverse
    and less representative than batch-aware selection does, out of the 7 strategies compared.
    Discriminative Active Learning scores highest on both.
  scope: The first batch after the initial model, with diversity as minimum-distance coverage
    and representativeness as inverse KNN-density over BERT [CLS] vectors. Greedy Core-Set
    is diverse but not representative.
  evidence: Section 5, Figure 2
- id: batch-overlap-under-15-percent
  text: Active learning strategies select largely different examples from one BERT model and
    pool. For every pair of the 7 strategies, expected overlap between their selected 50-example
    batches stays at or below 15%.
  scope: One batch per pair. Overlap is highest inside the uncertainty-based family and in
    the imbalanced scenarios, peaking between Expected Gradient Length and Least Confidence.
  evidence: Section 5
- id: batch-size-and-sequence-length-tradeoff
  text: 'BERT fine-tuning stability on 100-500 examples depends strongly on batch size. Under
    fixed GPU memory the best setting traded sequence length for it: batch size 50, a 100-WordPiece-token
    cap, 5 epochs at learning rate 5e-5, retrained from scratch each iteration.'
  scope: A single Tesla K80 and 10 binary datasets, so a starting point rather than a recipe.
    Random 100-example seeds on the skewed datasets were too unstable to use, which is why
    the imbalanced scenarios add 100 weakly-labelled negatives.
  evidence: Section 3.5, Section 3.2
- id: scale-of-the-study
  text: 'Comparing active learning strategies for BERT took 2,520 fine-tuning runs: 14 dataset-scenario
    combinations, 5 seeds each, one base model plus 7 strategies over 5 iterations, on 10
    binary text classification datasets.'
  scope: All English, all binary tasks made by picking one target class per dataset, all BERT-BASE.
    Iteration runtime spans 3 orders of magnitude, up to 1106 seconds for Expected Gradient
    Length at 7,000 unlabelled examples.
  evidence: Section 3.4, Table 1, Table 2
qa:
- q:
  - Where should I start on active learning for text classification with transformers?
  - What is the reference study on active learning for BERT?
  - How do I choose an active learning strategy for a small labelling budget?
  answers:
  - where-to-start-on-active-learning-for-transformers
- q:
  - Does active learning actually help when fine-tuning BERT?
  - Is active learning worth it for BERT text classification?
  - Do AL strategies beat random sampling for a pre-trained model like BERT?
  - Can active learning improve BERT with a small labelling budget?
  answers:
  - al-helps-bert-imbalanced-practical
  - all-strategies-beat-random-when-skewed
- q:
  - Which active learning strategy is best for BERT?
  - What is the state-of-the-art AL acquisition function for transformers?
  - Should I use least confidence or core-set with BERT?
  - Is there a winning active learning method for text classification?
  answers:
  - no-single-strategy-wins
  - uncertainty-strategies-pick-redundant-batches
  - batch-overlap-under-15-percent
- q:
  - What if my labelled examples come from a keyword search instead of a random sample?
  - Does active learning work when the seed set is biased?
  - Can a classifier recover from a biased initial training set?
  - How do I bootstrap a classifier for a rare class without annotating a random sample?
  answers:
  - al-helps-bert-imbalanced-practical
  - recall-not-precision-drives-the-gain
- q:
  - How do I fine-tune BERT stably on a few hundred examples?
  - What batch size and sequence length for low-resource BERT fine-tuning?
  - Why is my BERT fine-tuning unstable with a small imbalanced training set?
  answers:
  - batch-size-and-sequence-length-tradeoff
- q:
  - How large was the active learning for BERT study?
  - How many experiments does Active Learning for BERT run?
  - What datasets does the BERT active learning study cover?
  answers:
  - scale-of-the-study
misreadings:
- 'The paper is often cited as showing that active learning helps BERT, without its condition:
  the 4-8 point margin is for a skewed class (15% prior or lower) and a 100-example seed.
  In the balanced setting the gains are small, and two of the seven strategies do not beat
  random sampling at all.'
- It is not a ranking of acquisition functions. No pair of the seven strategies differs significantly,
  so citing this paper as evidence that one specific strategy is best inverts its finding
  -- the practical differences it does report are in runtime, which spans three orders of
  magnitude.
- '''Imbalanced-practical'' is not simply a lower class prior. It is the setting where the
  labelled seed itself is biased because it was retrieved by a keyword query, which is why
  it starts from a worse model and yet ends up with the largest improvement.'
- The results are for BERT-BASE with 110M parameters in 2020, on 10 binary English classification
  tasks. They say nothing about few-shot prompting, instruction-tuned models, or multi-class
  settings, none of which were tested.
terminology:
  imbalanced-practical: An active learning scenario in which the initial labelled set is retrieved
    by a keyword query rather than sampled, so it is enriched with positive examples but biased
    toward whatever the query matches. It is the situation a practitioner bootstrapping a
    rare-class classifier is actually in.
  imbalanced: An active learning scenario with a positive class prior of 15% or lower, where
    an unbiased sample of 100 positive examples can still be obtained. Distinct from imbalanced-practical,
    which drops that assumption.
  diversity: A batch-level measure, defined as the inverse of the mean over the unlabelled
    pool of each instance's minimum distance to the selected batch, computed on BERT [CLS]
    vectors -- not lexical or topical variety.
  representativeness: 'One over the average KNN-density (K=10) of the batch''s instances in
    [CLS] space: high values mean the batch avoids outliers, rather than that it covers the
    label distribution.'
---
