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
-->
---
one_liner: Active learning on top of BERT raises F1 by 4-8 points over random sampling for
  binary text classification under a 100-example seed and a 15% or lower positive-class prior,
  with the largest gains when the seed comes from a keyword query rather than an unbiased
  sample.
claims:
- id: al-helps-bert-imbalanced-practical
  text: Active learning strategies raise BERT's F1 by 4-8 points on average over a random-sampling
    baseline in the imbalanced-practical setting, where the initial 100 labelled examples
    are drawn from a keyword query and the positive class prior is 15% or lower.
  scope: Binary text classification, BERT-BASE, an annotation budget of 100 seed examples
    plus 5 iterations of 50; the 4-8 point margin is specific to the imbalanced-practical
    scenario. Gains in the balanced setting exist but are much smaller, and two strategies
    (Expected Gradient Length, Perceptron Ensemble) do not beat random there at all.
  evidence: Section 4, Figure 1 (bottom row), Table 3
- id: no-single-strategy-wins
  text: 'No one active learning strategy consistently outperforms the others for BERT: across
    seven strategies, three scenarios and ten datasets, no pair of strategies differs significantly
    after Bonferroni correction, even though every strategy beats random sampling on skewed
    data.'
  scope: Holds across the seven strategies tested (Least Confidence, Monte Carlo Dropout,
    Perceptron Ensemble, Expected Gradient Length, Core-Set, Discriminative Active Learning,
    and Random as baseline) at this budget; strategies do differ substantially in runtime,
    so the choice is a cost decision rather than an accuracy one.
  evidence: Section 4, Table 3
- id: all-strategies-beat-random-when-skewed
  text: Every active learning strategy tested significantly outperforms random sampling for
    BERT when the target class prior is 15% or lower, with Wilcoxon p-values after Bonferroni
    correction from below 10^-2 to below 10^-9.
  scope: The imbalanced and imbalanced-practical scenarios only. In the balanced setting (20-50%
    positive prior) Expected Gradient Length and Perceptron Ensemble show no significant improvement
    over random.
  evidence: Table 3
- id: recall-not-precision-drives-the-gain
  text: When the labelled seed comes from a keyword query, active learning's F1 gain for BERT
    is driven entirely by recall rather than precision, and the model recovers from the query's
    bias to match the F1 it reaches from an unbiased positive sample after a few iterations.
  scope: Imbalanced-practical scenario; in the imbalanced scenario with an unbiased positive
    seed the same F1 gain is driven mostly by precision instead. The starting model from a
    biased query seed has lower F1 at iteration 0 in every case.
  evidence: Section 4, Appendix Figures 4 and 5
- id: uncertainty-strategies-pick-redundant-batches
  text: Uncertainty-based selection for BERT (Least Confidence, Monte Carlo Dropout, Perceptron
    Ensemble, Expected Gradient Length) produces batches that are measurably less diverse
    and less representative than those from the batch-aware strategies, with Discriminative
    Active Learning scoring highest on both diversity and representativeness.
  scope: Measured on the first 50-example batch after the initial model, with diversity as
    minimum-distance coverage and representativeness as inverse KNN-density over BERT [CLS]
    vectors; greedy Core-Set is diverse but scores low on representativeness except in the
    imbalanced-practical scenario.
  evidence: Section 5, Figure 2
- id: batch-overlap-under-15-percent
  text: 'Different active learning strategies select largely different examples: for every
    pair of the strategies tested, expected overlap between the selected 50-example batches
    does not exceed 15%.'
  scope: One batch, measured from the same BERT model and the same unlabelled pool. Overlap
    is higher within the uncertainty-based family and in the imbalanced scenarios; the single
    highest overlap is between Expected Gradient Length and Least Confidence. The paper does
    not test whether combining low-overlap strategies helps.
  evidence: Section 5
- id: batch-size-and-sequence-length-tradeoff
  text: 'BERT fine-tuning stability under a 100-500 example budget depends strongly on batch
    size, and with fixed GPU memory the best setting traded sequence length for it: batch
    size 50 with a 100-WordPiece-token maximum, BERT-BASE, 5 epochs, learning rate 5e-5, retrained
    from scratch at every iteration.'
  scope: An empirical finding on this hardware (single Tesla K80) and these ten datasets,
    not a general recipe. Random 100-example seeds on the skewed datasets were unstable enough
    to be unusable, which is why the imbalanced scenarios add 100 weakly-labelled negatives.
  evidence: Section 3.5, Section 3.2
- id: scale-of-the-study
  text: 'The study covers 2,520 BERT fine-tuning runs: 14 dataset-scenario combinations, 5
    initial seeds each, one base model plus 7 selection strategies over 5 iterations, across
    10 binary text classification datasets.'
  scope: All English, all binary tasks derived by selecting one target class per dataset,
    all BERT-BASE. Iteration runtimes differ by three orders of magnitude between strategies
    (under 1 second for random, 1106 for Expected Gradient Length at 7,000 unlabelled examples).
  evidence: Section 3.4, Table 1, Table 2
qa:
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
  imbalanced-practical: 'This paper''s third scenario, and its main contribution: the initial
    labelled set is obtained by a keyword query rather than sampled, so it is enriched with
    positive examples but biased towards whatever the query matches -- the situation a practitioner
    is actually in.'
  imbalanced: Used here for a positive class prior of 15% or lower, with the assumption that
    an unbiased sample of 100 positive examples can still be obtained. Distinct from imbalanced-practical,
    which drops that assumption.
  diversity: A batch-level measure, defined as the inverse of the mean over the unlabelled
    pool of each instance's minimum distance to the selected batch, computed on BERT [CLS]
    vectors -- not lexical or topical variety.
  representativeness: 'One over the average KNN-density (K=10) of the batch''s instances in
    [CLS] space: high values mean the batch avoids outliers, rather than that it covers the
    label distribution.'
links_extra:
  code: https://github.com/IBM/low-resource-text-classification-framework
---
