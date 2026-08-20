---
key: shnarch2022cluster
coined: BERT_IT:CLUST
gloss: BERT inter-trained to predict unsupervised cluster labels before fine-tuning on scarce
  labeled data
one_liner: 'Cluster & Tune inserts an unsupervised intermediate phase between pre-training
  and fine-tuning: cluster the unlabeled target-domain training data with sequential Information
  Bottleneck over bag-of-words, then train BERT to predict the cluster label before fine-tuning
  on the few available labels.'
claims:
- id: topical-gain-64
  kind: result
  text: Inter-training BERT to predict 50 sIB cluster labels raises average accuracy on 6
    topical datasets from 26.9% to 49.6% with only 64 labeled fine-tuning examples. That is
    a 110% relative accuracy gain and a 33% error reduction over plain BERT fine-tuning.
  scope: BERT-BASE (110M), 64 fine-tuning examples (128 for 20 newsgroups), 5 repetitions;
    no dev set, 50 clusters and 1 inter-training epoch fixed for all datasets.
  evidence: Table 2
- id: nontopical-no-gain
  kind: result
  text: On the 3 non-topical datasets (SMS spam, Subjectivity, Polarity) cluster-based inter-training
    raises average accuracy only from 82.6% to 85.4% at 64 labeled examples, a 3% relative
    gain. Polarity shows 0% gain, and results stay comparable to plain BERT rather than worse.
  scope: Sentiment, subjectivity and spam tasks whose distinction is stylistic rather than
    topical; BERT-BASE, 64 labeled examples, sIB clustering over stemmed bag-of-words with
    50 clusters.
  evidence: Table 2
- id: significance-budget
  kind: result
  text: The accuracy gain of cluster-based inter-training over plain BERT fine-tuning is statistically
    significant for labeling budgets up to 512 examples, and not significant beyond 512. Bonferroni-corrected
    paired-t-test p-values run from 1×10⁻⁶ at 64 samples to 9×10⁻³ at 512.
  scope: Paired t-tests pooling all 9 datasets and 5 repetitions per labeling budget; budgets
    tested from 64 to 1024 examples with BERT-BASE.
  evidence: Table 3
- id: beats-mlm
  kind: result
  text: Clustering as the intermediate task beats continued MLM pre-training on the same target
    corpus for labeling budgets of 64, 128 and 192 examples, with no significant difference
    at 256 or above. Bonferroni-corrected p-values are 8×10⁻⁵, 3×10⁻³ and 4×10⁻².
  scope: BERT_IT:MLM baseline trained 30 epochs with replication rate 5 on the same unlabeled
    train set; comparison pools all 9 datasets and 5 repetitions per budget.
  evidence: Table 3
- id: complementary
  kind: result
  text: Running MLM inter-training and then cluster-label inter-training in sequence outperforms
    either intermediate task alone on topical datasets, showing the two phases are complementary
    at the cost of added runtime.
  scope: Topical datasets, labeling budgets 64-1024, BERT-BASE, sIB clustering over bag-of-words;
    the paper reports no p-values for this specific pairwise comparison.
  evidence: Figure 2
- id: nmi-predicts-gain
  kind: result
  text: The benefit of cluster-based inter-training tracks the normalized mutual information
    between the 50-cluster partition and the target labels. Datasets with NMI near zero show
    no clear gain, and the 3 datasets with the lowest NMI are exactly those where inter-training
    did not help.
  scope: 9 datasets, NMI computed over the full train set between sIB cluster labels and gold
    labels, error reduction measured at 64 fine-tuning samples; a correlation across 9 datasets,
    not a per-dataset predictive rule.
  evidence: Figure 4
- id: sib-best-clustering
  kind: result
  text: sIB clustering over stemmed bag-of-words representations gives better downstream accuracy
    after inter-training than K-means or Hartigan's K-means over averaged GloVe embeddings
    on most of the datasets tested.
  scope: 50 clusters, 1 inter-training epoch, sIB with 10 restarts and 15 iterations and a
    10K-word vocabulary; "most cases" rather than all, and no significance test reported for
    this comparison.
  evidence: Figure 6, Appendix C
- id: not-just-bow
  kind: result
  text: The gains of cluster-based inter-training do not come merely from bag-of-words information.
    Multinomial Naive Bayes and SVM classifiers over BOW or GloVe representations, trained
    on the same labeled samples, were all inferior to the cluster-inter-trained BERT.
  scope: 4 reference settings (NB_BOW, NB_GloVe, SVM_BOW, SVM_GloVe) on the same 9 datasets
    and the same 5 label samplings per budget.
  evidence: Figure 5, Appendix B
- id: clusters-alone-insufficient
  kind: result
  text: Using the 50 sIB clusters directly as a classifier is generally not on par with cluster-based
    BERT inter-training, though it is surprisingly effective where NMI is high and the budget
    small. Each cluster is labeled from a budget-proportional sample and each test example
    takes its nearest cluster's dominant label.
  scope: Heuristic guarantees at least 1 labeled instance per cluster; evaluated on the same
    9 datasets and budgets from 64 to 1024.
  evidence: Figure 5, Appendix B
- id: embeddings-tighter
  kind: result
  text: After cluster-label inter-training, BERT's [CLS] embeddings place same-class examples
    closer together in every dataset tested, measured by a permutation-normalized Euclidean
    distance to class centroids. t-SNE plots of topical datasets show visibly cleaner class
    separation.
  scope: Embeddings over the full train set, gold labels used only for measurement; normalization
    uses a permutation test with 1000 repetitions. The visual separation is qualitative and
    clearest on topical data such as DBpedia, unlike Polarity.
  evidence: Figure 3, Section 5.3
- id: cheap-to-run
  kind: result
  text: The clustering step for the intermediate task takes only a few seconds. The single
    inter-training epoch takes five and a half minutes for the largest 15K-instance train
    set on one Tesla V100-PCIE-16GB GPU.
  scope: BERT-BASE, batch size 64, max sequence length 128, learning rate 3×10⁻⁵; datasets
    of 3.9K to 15K training instances.
  evidence: Section 3.2
- id: context-cold-start
  kind: context
  text: Cluster & Tune introduces unsupervised text clustering as an intermediate training
    task for cold-start text classification, transferring to NLP the computer-vision practice
    of using cluster assignments as pseudo-labels for representation learning.
  scope: As of publication at ACL 2022; earlier NLP work used clustering mainly for non-transfer
    purposes. Demonstrated for English single-label text classification with BERT-BASE only.
  evidence: Section 6
- id: context-no-extra-labels
  kind: context
  text: Cluster & Tune requires no additional labeled data and no per-task design, since the
    pseudo-labels come from clustering the unlabeled target-domain corpus. It is therefore
    an alternative to supervised intermediate tasks that need labeled data from another task.
  scope: Requires an unlabeled corpus of the target domain on the order of several thousand
    examples; hyperparameters (50 clusters, 1 epoch) were fixed a priori rather than tuned
    per dataset, and no dev set is assumed.
  evidence: Section 2
qa:
- q:
  - How can I improve text classification accuracy when I only have a few dozen labeled examples?
  - What helps BERT fine-tuning in a cold-start setting with scarce labels?
  - How much does clustering-based inter-training help with 64 labeled examples?
  answers:
  - topical-gain-64
  - significance-budget
- q:
  - Is clustering better than continued MLM pre-training on domain data as an intermediate
    task?
  - Does further pre-training with masked language modeling beat training on cluster labels?
  - Should I do domain-adaptive MLM or cluster prediction before fine-tuning BERT?
  answers:
  - beats-mlm
  - complementary
- q:
  - When does cluster-based inter-training fail to help text classification?
  - Does Cluster & Tune work for sentiment analysis or spam detection?
  - Why does clustering-based pre-finetuning help topical tasks but not stylistic ones?
  answers:
  - nontopical-no-gain
  - nmi-predicts-gain
- q:
  - Which clustering algorithm should be used to generate pseudo-labels for intermediate training?
  - Is sequential Information Bottleneck over bag-of-words better than K-means over GloVe
    for inter-training?
  - Does the choice of clustering method matter for BERT_IT:CLUST?
  answers:
  - sib-best-clustering
- q:
  - Could a simple bag-of-words classifier match cluster-based BERT inter-training in low-label
    settings?
  - Do Naive Bayes and SVM baselines explain the gains from clustering-based inter-training?
  - Is a nearest-cluster label-propagation classifier as good as inter-trained BERT?
  answers:
  - not-just-bow
  - clusters-alone-insufficient
- q:
  - What changes in BERT's sentence embeddings after training on cluster labels?
  - Does inter-training on clusters make same-class representations closer together?
  - Is there evidence that cluster inter-training gives a better starting point for fine-tuning?
  answers:
  - embeddings-tighter
- q:
  - How expensive is it to add a clustering-based intermediate training phase?
  - What is the runtime cost of Cluster & Tune?
  - How long does one inter-training epoch over cluster labels take on a single GPU?
  answers:
  - cheap-to-run
- q:
  - What should I read about using unsupervised clustering as pseudo-labels for NLP transfer
    learning?
  - Which paper introduced clustering as an intermediate task between pre-training and fine-tuning
    for text classification?
  - Where should I start reading about cold-start text classification with pre-trained language
    models?
  answers:
  - context-cold-start
  - context-no-extra-labels
- q:
  - Up to what labeling budget does the clustering intermediate phase still pay off?
  - Does the benefit of cluster-based inter-training disappear with more labeled data?
  - At how many labeled examples do the gains from cluster pseudo-labels become insignificant?
  answers:
  - significance-budget
  - topical-gain-64
- q:
  - Do I need extra labeled data from another task to use clustering as an intermediate task?
  - What data does Cluster & Tune require beyond the few target-task labels?
  - Can the intermediate phase be run without any annotation at all?
  answers:
  - context-no-extra-labels
  - cheap-to-run
misreadings:
- 'Cluster-based inter-training is not a general accuracy boost for text classification: on
  non-topical tasks such as Polarity, Subjectivity and SMS spam the average relative gain
  at 64 labels is 3%, and the advantage over plain BERT fine-tuning is not statistically significant
  above 512 labeled examples.'
- 'The number of clusters is not meant to match the number of target classes: setting it equal
  to the number of classes gave inferior accuracy, and 50 clusters was used for all 9 datasets
  regardless of their 2 to 20 classes.'
- Cluster & Tune is not a label-free classifier. The clustering phase produces pseudo-labels
  for inter-training only, and a final supervised fine-tuning phase on real target-task labels
  is still required.
- The method does not replace continued MLM pre-training. Running MLM inter-training first
  and cluster inter-training second outperformed either one alone on topical datasets.
- The clustering pseudo-labels are not tailored to the target task; they are generated independently
  of it, so no knowledge of the target label set is assumed when producing them.
terminology:
  inter-training: An intermediate training phase inserted between a model's general pre-training
    and its supervised fine-tuning, which sees the target-task corpus or domain but none of
    its labeled instances.
  BERT_IT:CLUST: BERT inter-trained as a 50-way classifier predicting sequential-Information-Bottleneck
    cluster assignments of the unlabeled target-domain train set, with the cluster-prediction
    head discarded before fine-tuning.
  BERT_IT:MLM: BERT further pre-trained with masked language modeling on the unlabeled target-domain
    corpus before fine-tuning, also known as adaptive or further pre-training.
  topical dataset: A classification dataset whose classes reflect a high-level distinction
    about what a text is about, such as sports versus economics, as opposed to non-topical
    datasets whose classes turn on style, fine details or negation.
  Normalized Embeddings' Distance (NED): The average Euclidean distance of instance embeddings
    from their own class centroid, divided by the expected value of that distance under random
    permutations of the class labels.
  cold start: The situation at the beginning of a text classification project in which unlabeled
    data from the target domain is available but labeled examples number only a couple of
    dozen to a few hundred.
links_extra:
  code: https://github.com/IBM/intermediate-training-using-clustering
  sib_implementation: https://github.com/IBM/sib
---
