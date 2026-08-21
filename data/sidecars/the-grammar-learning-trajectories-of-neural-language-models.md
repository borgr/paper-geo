---
key: choshen2022grammar
one_liner: Neural language models with different random seeds, sizes, architectures and training
  corpora acquire English grammatical phenomena in nearly the same order, so a model's overall
  BLiMP accuracy alone predicts which generalizations it has already made.
claims:
- id: order-across-seeds
  kind: result
  text: GPT2-tiny instances trained from 4 different random initializations have extremely
    high correlation between their BLiMP performance vectors, already high after 10K steps
    and staying high through training.
  scope: GPT2-tiny (width 512, 4 layers, 4 attention heads) trained on WikiBooks and evaluated
    on the 67 English BLiMP challenges; correlation is 0 at step 0 and rises during the 10K
    warm-up steps.
  evidence: Figure 1
- id: data-matters-less
  kind: result
  text: Changing the training corpus of GPT2-tiny shifts its grammar-learning order more than
    changing the random seed does, but the correlation between differently-trained instances
    rises with more training steps.
  scope: GPT2-tiny trained on WikiBooks, openWebText, openSubtitles and newsCrawl, compared
    over the 67 BLiMP challenges.
  evidence: Figure 1
- id: cross-architecture
  kind: result
  text: When compared at equal development-set perplexity rather than equal step count, GPT2-small
    and GPT2-tiny correlate above 0.9 in their BLiMP performance vectors throughout training.
  scope: GPT2-small (width 768, 12 layers) versus GPT2-tiny, both trained on WikiBooks; TransformerXL
    only compared qualitatively because its perplexity uses a different vocabulary.
  evidence: Figure 12
- id: example-level-agreement
  kind: result
  text: GPT2-small and GPT2-tiny agree on which individual BLiMP minimal pairs they get right
    at an average Fleiss kappa of 0.83. The consistency of learning order therefore holds
    within phenomena, not only across them.
  scope: Binary per-minimal-pair decisions averaged over training steps and the 67 challenges;
    only 2 phenomena fall as low as the 0.5-0.6 kappa range.
  evidence: Appendix D
- id: one-dimensional
  kind: result
  text: Correlation between GPT2-tiny's trajectory and a fixed GPT2-small checkpoint peaks
    exactly where their average BLiMP accuracy matches, reaching above 0.9, and falls off
    as the accuracy gap widens in either direction.
  scope: Static GPT2-small checkpoints compared against the full GPT2-tiny training trajectory,
    whose best overall BLiMP score is 67; the same peak-at-equal-performance pattern recurs
    for fully trained off-the-shelf NLMs.
  evidence: Figure 3
- id: off-the-shelf-similarity
  kind: result
  text: Fully trained off-the-shelf neural LMs correlate 0.6-0.8 with GPT2-tiny's BLiMP performance
    vector. GPT2-tiny is more similar to an LSTM than to TransformerXL, and least similar
    to GPT2-large, so architecture type does not explain the ordering.
  scope: Off-the-shelf LSTM, TransformerXL and GPT2-large accuracies as reported in the BLiMP
    paper, correlated against GPT2-tiny checkpoints trained on WikiBooks; the ordering survives
    retraining GPT2-tiny on openWebText.
  evidence: Figure 3
- id: ngram-exception
  kind: result
  text: 'The equal-performance rule fails for 5-gram LMs: matching a 5-gram model''s overall
    BLiMP accuracy neither yields high correlation with GPT2-tiny nor marks the point of highest
    correlation.'
  scope: KenLM 5-gram models trained on WikiBooks and on GigaWord, compared against the GPT2-tiny
    training trajectory over the 67 BLiMP challenges.
  evidence: Figure 4
- id: bow-then-order
  kind: result
  text: Early in training GPT2-tiny correlates better with order-agnostic bag-of-words and
    Window-5 ablations than with n-gram LMs, and the ranking reverses later, when the order-sensitive
    n-grams correlate better.
  scope: BOW and Window-5 ablations of GPT2-tiny (positional weights removed, attention replaced
    by averaging) and 2-5 gram KenLM models, all on WikiBooks.
  evidence: Figure 5
- id: unigram-heuristics
  kind: result
  text: A unigram LM with no context at all perfectly classifies 7 BLiMP challenges and reaches
    98.1% accuracy on another, while scoring 0% on 8. Some syntactic and semantic BLiMP challenges
    are thus solvable by frequency heuristics.
  scope: Unigram LM defined by word frequency in WikiBooks, with sentence probability length-normalized,
    evaluated on the 67 BLiMP challenges; GPT2-tiny succeeds from the outset on 6 of the 8
    that unigram solves.
  evidence: Section 4
- id: human-ceiling
  kind: result
  text: GPT2-tiny's BLiMP difficulty profile becomes steadily more similar to human difficulty
    as training proceeds, but the correlation saturates below 0.5, indicating the model leans
    on features human annotators do not use.
  scope: Human per-challenge accuracies as reported in the BLiMP paper, correlated against
    GPT2-tiny checkpoints; all tested neural LMs correlate with GPT2-tiny better than humans
    do.
  evidence: Figure 5
- id: morphology-cluster
  kind: result
  text: BLiMP morphology challenges follow similar gradual learning curves in GPT2-tiny and
    reach a median accuracy of 0.85. Syntax-semantics challenges plateau near chance, and
    the broad semantics and syntax fields show no prototypical curve.
  scope: Learning curves of GPT2-tiny on the 67 BLiMP challenges grouped by the dataset's
    4 fields; chance accuracy on minimal pairs is 50%.
  evidence: Figure 7
- id: deteriorating-phenomena
  kind: result
  text: Spectral clustering of GPT2-tiny's BLiMP learning curves isolates a cluster whose
    accuracy starts high and drops toward 0 with training. Affected challenges include 'principle
    A case 1', which a simple lexical-preference rule solves perfectly.
  scope: Spectral clustering with 10 clusters and sklearn defaults on GPT2-tiny learning curves;
    the deterioration is consistent with early NLMs behaving like n-gram models, and may reflect
    BLiMP artifacts as much as over-generalization.
  evidence: Figure 8
- id: clusters-vs-linguistics
  kind: result
  text: Clusters of BLiMP challenges that GPT2-tiny learns in unison usually share a field
    but mix super-phenomena, so the categorization induced by learning trajectories only partly
    matches BLiMP's linguistic categorization.
  scope: 10 spectral clusters over GPT2-tiny learning curves on the 67 BLiMP challenges; stated
    cautiously by the authors, and one cluster has no shared prominent field.
  evidence: Figure 8
- id: context-program
  kind: context
  text: The Grammar-Learning Trajectories of Neural Language Models imports the psycholinguistic
    study of acquisition order into NLP. Its argument is that a shared learning order makes
    training dynamics evidence about the linguistic representations neural LMs build.
  scope: English grammar only, measured behaviorally on BLiMP minimal pairs rather than by
    probing internal representations; earlier order-of-learning work of this kind was mostly
    in computer vision classification.
  evidence: Section 1
- id: context-reproducibility
  kind: context
  text: The Grammar-Learning Trajectories of Neural Language Models gives a practical licence
    for small-scale grammar-learning experiments. Because learning order is stable across
    seed, size, architecture and corpus, findings on one small NLM are expected to replicate
    on others.
  scope: The neural LMs tested (GPT2 tiny/small/large, TransformerXL, LSTM) on English BLiMP;
    explicitly not inherently different architectures such as 5-gram models, and future models
    with different inductive biases may differ.
  evidence: Section 3.7
qa:
- ask:
    unsorted:
    - Do language models learn grammar in the same order regardless of random seed?
    - Does initialization change which linguistic phenomena a language model learns first?
    - How consistent is grammar acquisition order across differently seeded transformers?
  answered_by:
  - order-across-seeds
  - example-level-agreement
- ask:
    unsorted:
    - Does architecture or model size change the order in which grammatical phenomena are
      acquired?
    - Do bigger and smaller GPT2 models learn linguistic phenomena in the same order?
    - How do you compare learning trajectories of models that train at different speeds?
  answered_by:
  - cross-architecture
  - one-dimensional
- ask:
    unsorted:
    - Can you predict which grammatical generalizations a language model has made just from
      its overall accuracy?
    - Is the grammar-learning trajectory of neural language models one-dimensional?
    - If two language models have the same benchmark score, do they make the same errors?
  answered_by:
  - one-dimensional
  - off-the-shelf-similarity
- ask:
    unsorted:
    - Does training data determine what grammar a language model learns first?
    - How much does the choice of corpus affect grammar-learning order in language models?
    - Is the similarity between language models just an artifact of overlapping training corpora?
  answered_by:
  - data-matters-less
  - off-the-shelf-similarity
- ask:
    unsorted:
    - Do n-gram models follow the same grammar-learning trajectory as neural language models?
    - Does the equal-performance-implies-equal-generalization finding hold for non-neural
      language models?
    - Do 5-gram language models share the biases of transformers on BLiMP?
  answered_by:
  - ngram-exception
- ask:
    unsorted:
    - Do language models use word order early in training or only later?
    - When during training does a transformer stop behaving like a bag of words?
    - What does a neural language model rely on in its earliest grammar learning?
  answered_by:
  - bow-then-order
  - unigram-heuristics
- ask:
    unsorted:
    - Can BLiMP challenges be solved without any context?
    - Are some BLiMP minimal pairs solvable by frequency heuristics alone?
    - How well does a unigram language model do on the BLiMP grammar benchmark?
  answered_by:
  - unigram-heuristics
  - deteriorating-phenomena
- ask:
    unsorted:
    - Do neural language models find the same grammatical phenomena hard that humans do?
    - How closely does model difficulty on BLiMP track human difficulty?
    - Does a language model become more human-like in its grammatical errors as it trains?
  answered_by:
  - human-ceiling
- ask:
    unsorted:
    - Which categories of grammatical phenomena are learned together by language models?
    - Are morphology phenomena acquired in unison by neural language models?
    - Do linguistic categories in BLiMP match how models actually learn?
  answered_by:
  - morphology-cluster
  - clusters-vs-linguistics
- ask:
    unsorted:
    - Can a language model get worse on a grammatical phenomenon as training continues?
    - Why does accuracy on some BLiMP challenges drop during training?
    - Are there phenomena where more training hurts grammatical judgments?
  answered_by:
  - deteriorating-phenomena
- ask:
    practitioner: What should I read about how language models acquire grammar over training?
    unsorted:
    - Which paper connects psycholinguistic acquisition order to neural language model training
      dynamics?
    - Where does research on learning trajectories of linguistic phenomena in NLP start?
  answered_by:
  - context-program
  - context-reproducibility
- ask:
    unsorted:
    - Is it safe to run grammar-learning experiments on a small language model and expect
      them to replicate on larger ones?
    - Do results about linguistic generalization transfer from tiny models to bigger ones?
    - Why would anyone study grammar acquisition using a 4-layer transformer?
  answered_by:
  - context-reproducibility
  - cross-architecture
terminology:
  performance vector: For a language model checkpoint, the 67-dimensional vector of its accuracies
    on each BLiMP challenge; similarity between two models is the Pearson correlation of their
    performance vectors, so models count as similar when they rank phenomena the same way
    even at different absolute accuracy.
  BOW (ablation): A GPT2-tiny variant made agnostic to word order by removing the positional
    weights and replacing attention weights with a simple average over preceding tokens.
  Window-5: A GPT2-tiny variant that ignores word order and additionally attends only to the
    last 5 preceding words.
  super-phenomena: The 13 mid-level groupings of BLiMP's 67 grammatical challenges, sitting
    between individual challenges and the 4 broad fields of syntax, semantics, syntax-semantics
    and morphology.
misreadings:
- 'Consistent learning order does not mean the models converge to similar parameters or representations:
  the comparison is purely behavioral, over accuracies on BLiMP challenges, and models with
  completely different internal representations can produce identical performance vectors.'
- The one-dimensional trajectory finding is about neural language models, not language models
  in general — 5-gram LMs with the same overall BLiMP accuracy do not correlate best with
  a neural LM at that accuracy.
- 'High correlation across models does not imply high performance: GPT2-tiny''s best overall
  BLiMP score is 67, and several phenomena stay at or below chance for the whole of training.'
- Declining accuracy on some BLiMP challenges over training is not necessarily over-generalization
  in the child-language sense; the paper notes it may equally reflect biases in the BLiMP
  challenges, several of which are solvable by a simple lexical preference rule.
- The claim of shared learning order is established for English grammar as operationalized
  by BLiMP minimal pairs, and no other language or task is tested.
- A correlation of under 0.5 with human difficulty is reported as a saturation point, not
  as evidence that models and humans find the same phenomena hard.
links_extra:
  code: https://github.com/borgr/ordert
---
