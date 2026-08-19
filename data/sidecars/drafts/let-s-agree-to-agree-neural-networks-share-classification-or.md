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

Then promote it:  python scripts/draft_sidecars.py --accept let-s-agree-to-agree-neural-networks-share-classification-or

Stamp: spec=8f05813a4658 checks=pass body=05b28097470c
-->
---
claims:
- id: bimodal-tp-agreement
  text: Independently trained neural networks of the same architecture produce a bi-modal
    distribution of per-example TP-agreement throughout training on every natural benchmark
    tested, including ImageNet with 27 ResNet-50 models. Most examples are classified correctly
    by all the models or by none of them.
  kind: result
  evidence: Figure 4
  scope: 27 ResNet-50 models on ImageNet, train and validation sets, epochs 1 to 100; each
    epoch measured by training a fresh set of networks from scratch. Random classification
    vectors with matching accuracy give a uni-modal Gaussian instead.
- id: same-order-many-datasets
  text: The shared learning order of neural networks holds across MNIST, Fashion-MNIST, CIFAR-10,
    CIFAR-100, tiny ImageNet, VGGFace2, ImageNet and a 20-class Stack Overflow text classification
    task, for both train and test sets.
  kind: result
  evidence: Figure 5
  scope: Small handcrafted CNNs, st-VGG, VGG-19, AlexNet, DenseNet, ResNet-50 and an attention-based
    BiLSTM with GloVe embeddings; 20 to 100 models per setting. The text case is one dataset
    of 39K train and 1K test questions.
- id: hyperparameter-robustness
  text: The shared classification order of same-architecture networks survives changes to
    learning rate (10^-4 to 1), optimizer (SGD, Adam, AdaDelta), batch size (1 to 2500) and
    dropout (0 to 0.5). It also survives changes of initialization (Xavier, He normal, LeCun
    normal, truncated normal) and activation (ReLU, ELU, tanh, linear).
  kind: result
  evidence: Appendix D
  scope: Direct hyper-parameter sweeps were run on st-VGG trained on the small-mammals dataset
    with 100 instances each; other ranges came indirectly from varying architectures. Qualitative
    bi-modality is what is preserved, not exact accuracies.
- id: cross-architecture-correlation
  text: Accessibility scores on the ImageNet train set correlate at r=0.87 between ResNet-50
    and AlexNet collections and r=0.97 between ResNet-50 and DenseNet, against r=0.99 between
    two disjoint collections of ResNet-50.
  kind: result
  evidence: Figure 9
  scope: 27 ResNet-50, 22 AlexNet and 6 DenseNet models on ImageNet, all p ≤ 10^-50; Top-1
    error differs widely (AlexNet 0.45, ResNet-50 0.24, DenseNet 0.27).
- id: stronger-learns-superset
  text: ResNet-50 on ImageNet first learns the examples AlexNet gets right and only then learns
    examples AlexNet never learns. The count of examples that only one of the two architectures
    classifies correctly stays constant and low as accuracy improves.
  kind: result
  evidence: Figure 9
  scope: Majority-vote ensembles of 27 ResNet-50 and 22 AlexNet models on the ImageNet validation
    set, compared at epochs of matched accuracy (±1% tolerance); ResNet-50 reaches 80% and
    AlexNet 60%, so past 60% the comparison is against converged AlexNet.
- id: linear-nonlinear-nesting
  text: Linear st-VGG networks on the small-mammals dataset reach 0.43 average accuracy versus
    0.56 for non-linear st-VGG, yet still show bi-modal TP-agreement (maximum Pearson bi-modality
    0.06 versus 0.22). The non-linear networks first learn the examples the linear ones learn.
  kind: result
  evidence: Figure 10
  scope: 100 linear st-VGG models on the small-mammals dataset (2500 train, 500 test images,
    5 classes); linear networks converge in a few epochs, too fast for a meaningful accessibility
    score, so the nesting is read off matched-accuracy counts.
- id: synthetic-datasets-break-order
  text: The shared learning order disappears on synthetic data. 100 st-VGG models on a 12-class
    Gabor-patch dataset and 100 fully connected models on a 2-class overlapping-Gaussian task
    show approximately normal, not bi-modal, TP-agreement distributions.
  kind: result
  evidence: Figure 11
  scope: Both datasets are hand-crafted and are learned successfully by the networks; the
    Gabor case partially regains bi-modal character on the test set at convergence. Gaussian
    samples are 3072-dimensional, means 0 and 0.1, identity covariance.
- id: random-labels-break-order
  text: With randomly shuffled labels on the small-mammals dataset, 100 st-VGG models memorize
    the training set to 100% accuracy but do so in different orders. TP-agreement stays Gaussian,
    with minimum Pearson bi-modality 1.07 on train and 1.35 on test.
  kind: result
  evidence: Figure 11
  scope: 100 st-VGG instances with dropout layers removed to enable fitting random labels;
    test accuracy stays at chance. Shows association between bi-modality and generalization,
    not a causal mechanism.
- id: adaboost-different-order
  text: AdaBoost with up to 100 weak linear classifiers learns CIFAR-10 in an order only weakly
    related to that of neural networks. Accessibility scores correlate at r=0.35 on raw pixels
    and r=0.05 when AdaBoost uses Inception-V3 penultimate-layer features.
  kind: result
  evidence: Figure 12
  scope: AdaBoost versus 100 st-VGG models on CIFAR-10, both p ≤ 10^-20; replicated on small-mammals,
    fish, insect, cats-and-dogs and ImageNet-cats subsets. CIFAR-100 and full ImageNet excluded
    as AdaBoost accuracy is too low there.
- id: different-training-sets
  text: Neural networks trained on disjoint partitions of the same training distribution learn
    a common test set in nearly the same order, with almost perfect correlation between accessibility
    scores computed from different partitions.
  kind: result
  evidence: Figure 25
  scope: Fashion-MNIST train set split into 60 parts of 1000 images, 100 st-VGG instances
    per part, epochs 0 to 40; the shared order concerns the common unmodified test set.
- id: rarely-forgotten
  text: Once an example is classified correctly by most networks of a collection it is rarely
    misclassified later, with per-example TP-agreement staying pinned at 0 or 1 for most of
    training. The number of examples that rise near 1 and then fall to 0 is negligible.
  kind: result
  evidence: Figure 31
  scope: 5 tracked example images from st-VGG trained on the small-mammals dataset, with the
    pattern reported for the majority of examples in that setting; this property is what licenses
    defining a per-example learning epoch.
- id: class-order-hierarchy
  text: Classes, not just examples, are learned in a consistent order. Early in training only
    images from 2 of the 5 small-mammals classes reach TP-agreement 1, and further class labels
    emerge gradually as learning proceeds.
  kind: result
  evidence: Figure 30
  scope: 100 st-VGG instances on the 5-class small-mammals dataset, epochs 1, 2, 30 and 140;
    each image coloured by its most frequent predicted label across the collection.
- id: context-similarity-measure
  text: '"Let''s Agree to Agree" compares trained neural networks by their per-example predictions
    rather than by their internal representations. It offers an alternative to representation-similarity
    methods such as SVCCA for asking whether two networks are alike.'
  kind: context
  scope: As of the ICML 2020 publication; the comparison is behavioural and needs a labelled
    dataset and multiple trained instances, and it says nothing about which internal features
    a network uses.
- id: context-learning-order-line
  text: '"Let''s Agree to Agree" established shared example learning order as an empirical
    phenomenon of neural networks on natural datasets, a starting point for later work on
    example difficulty, learning-order and data-pruning scores.'
  kind: context
  scope: Evidence is empirical across image benchmarks and one text benchmark, with no theoretical
    account of why particular examples are easy; the paper reports that using the discovered
    order as a curriculum did not improve learning.
qa:
- q:
  - Do neural networks learn training examples in the same order across random seeds?
  - Does the order in which examples are learned depend on initialization and mini-batch sampling?
  - Do independently trained networks of the same architecture agree on which examples they
    classify correctly?
  answers:
  - bimodal-tp-agreement
  - hyperparameter-robustness
- q:
  - Which datasets show the shared classification order phenomenon?
  - Does shared learning order appear outside image classification, for example in text classification?
  - Was the learning-order effect tested on ImageNet and on NLP data?
  answers:
  - same-order-many-datasets
  - bimodal-tp-agreement
- q:
  - Do different architectures learn a dataset in the same order?
  - How similar is the learning order between ResNet-50, AlexNet and DenseNet on ImageNet?
  - Does a shared learning order survive across ResNet and AlexNet despite very different
    accuracies?
  answers:
  - cross-architecture-correlation
  - stronger-learns-superset
- q:
  - Does a more accurate network learn a superset of what a weaker network learns?
  - What is the relationship between the examples learned by a strong and a weak architecture?
  - Do stronger models learn easy examples first and then continue past what weak models manage?
  answers:
  - stronger-learns-superset
  - linear-nonlinear-nesting
- q:
  - Is the shared learning order just an artifact of SGD training?
  - Are there datasets where neural networks learn examples in different orders?
  - What happens to per-example agreement on synthetic datasets like Gabor patches or overlapping
    Gaussians?
  answers:
  - synthetic-datasets-break-order
  - random-labels-break-order
- q:
  - What happens to learning order when labels are randomly shuffled?
  - Do networks memorize random labels in a consistent order?
  - Is agreement on learning order tied to generalization rather than memorization?
  answers:
  - random-labels-break-order
- q:
  - Do non-neural classifiers learn a dataset in the same order as neural networks?
  - How does AdaBoost's learning order on CIFAR-10 compare with that of a CNN?
  - Is example difficulty a property of a benchmark dataset alone, or of the learner too?
  answers:
  - adaboost-different-order
  - synthetic-datasets-break-order
- q:
  - Does the shared learning order depend on the exact training set used?
  - If two models are trained on disjoint samples from the same distribution, do they learn
    a common test set in the same order?
  - How was the effect of the specific training split on learning order tested?
  answers:
  - different-training-sets
- q:
  - Are examples ever forgotten after being learned by a network?
  - Once a CNN classifies an example correctly, does it keep classifying it correctly?
  - How stable is per-example correctness across training epochs?
  answers:
  - rarely-forgotten
- q:
  - Do linear convolutional networks show the same learning-order behaviour as non-linear
    ones?
  - Is the shared learning order caused by non-linearities in the network?
  - What did linear st-VGG reveal about learning order on the small-mammals dataset?
  answers:
  - linear-nonlinear-nesting
- q:
  - How can I measure whether two trained neural networks are similar without comparing their
    weights?
  - What is TP-agreement and what does it measure?
  - Is there a way to compare networks by their per-example predictions instead of their representations?
  answers:
  - context-similarity-measure
  - bimodal-tp-agreement
- q:
  - What paper should I read first about example difficulty and learning order in deep networks?
  - Which work established that neural networks learn examples in a consistent order?
  - Where does the idea of a per-example learning order in deep learning come from?
  - What is a good starting paper on how neural networks discover structure in benchmark datasets?
  answers:
  - context-learning-order-line
  - context-similarity-measure
- q:
  - Are whole classes learned in a consistent order, not just individual images?
  - Does classification order induce a hierarchy over classes?
  - Which classes does a CNN learn first on a 5-class CIFAR-100 super-class?
  answers:
  - class-order-hierarchy
- q:
  - Does knowing the order examples are learned help build a better curriculum?
  - Can learning order be used to speed up training?
  answers:
  - context-learning-order-line
coined: TP-agreement
gloss: 'true-positive agreement: the fraction of independently trained networks that classify
  a given example correctly'
key: hacohen2020agree
misreadings:
- A shared learning order does not mean the trained networks have similar weights or internal
  representations; the similarity reported in "Let's Agree to Agree" is behavioural, measured
  on per-example predictions.
- 'The shared learning order is not a universal property of neural networks: on hand-crafted
  Gabor-patch and overlapping-Gaussian datasets, and on data with shuffled labels, networks
  of the same architecture learn examples in different orders.'
- 'Example difficulty as measured by the accessibility score is not a property of the dataset
  alone: AdaBoost with linear weak learners orders CIFAR-10 examples very differently from
  CNNs (r=0.35 on pixels, r=0.05 on Inception-V3 features).'
- The consistent learning order did not translate into a useful curriculum; "Let's Agree to
  Agree" reports that using the discovered order with the curriculum method of Hacohen & Weinshall
  (2019) did not seem to benefit learning.
- 'TP-agreement is not accuracy: accuracy averages one model''s correctness over many examples,
  whereas TP-agreement averages many models'' correctness on one example, so models with identical
  accuracy can have completely different TP-agreement distributions.'
one_liner: '"Let''s Agree to Agree" shows that independently trained neural networks learn
  benchmark datasets in nearly the same example-by-example order — measured by TP-agreement,
  the fraction of models classifying an example correctly — and that this order breaks down
  on synthetic data, on shuffled labels, and for AdaBoost.'
terminology:
  TP-agreement: For a single labelled example, the fraction of a collection of independently
    trained networks that classify it correctly after the same number of training epochs;
    contrasted with accuracy, which averages over examples rather than over models.
  Agreement score: For a single example, the largest fraction of a collection of networks
    that predict the same label, whether or not that label is correct; complements TP-agreement
    by capturing consensus among mistakes.
  accessibility score: An example's TP-agreement averaged over all training epochs measured,
    used as a per-example measure of how early and how robustly a given architecture learns
    it.
  Pearson bi-modality: The score kurtosis(X) − skewness²(X) − 1 of a distribution, where lower
    values indicate a more bi-modal distribution; used to quantify how sharply per-example
    agreement splits between 0 and 1.
  st-VGG: A stripped 8-convolutional-layer version of VGG with 32 to 256 filters per layer,
    max-pooling and dropout, used as a fast stand-in for larger CNNs on CIFAR-scale data.
  small-mammals dataset: The 5-class small-mammals super-class of CIFAR-100, with 2500 train
    and 500 test images of size 32×32×3.
---
