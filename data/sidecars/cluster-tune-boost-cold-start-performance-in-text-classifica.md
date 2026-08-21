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
- ask:
    plain: if I only have a few dozen labeled sentences, is there anything I can train a language
      model on first to make classification work better?
    jargon: how much does inter-training BERT on unsupervised cluster pseudo-labels improve
      accuracy in a cold-start text classification setup with 64 labeled examples?
    task: how do I get usable text classification accuracy when I can only afford to annotate
      a few dozen examples?
    practitioner: I have almost no annotated data for my classifier — should I add an unsupervised
      training phase before fine-tuning BERT?
  answered_by:
  - topical-gain-64
  - significance-budget
- ask:
    plain: is it better to keep training a language model on my own unlabeled text, or to
      train it to predict which group each document falls into?
    jargon: does clustering-based inter-training outperform continued masked language model
      pre-training on the target corpus as an intermediate task?
    task: I have a large unlabeled in-domain corpus — how do I use it best before fine-tuning
      on a tiny labeled set?
    practitioner: should I run domain-adaptive MLM pre-training, cluster-label inter-training,
      or both before fine-tuning?
  answered_by:
  - beats-mlm
  - complementary
- ask:
    plain: does grouping unlabeled documents before training help for spam or sentiment tasks,
      or only when the categories are about subject matter?
    jargon: on which target tasks does cluster-based inter-training fail to yield gains, and
      does normalized mutual information between clusters and labels predict that?
    task: how do I tell in advance whether an unsupervised clustering phase will help my particular
      classification task?
    practitioner: my labels are sentiment and subjectivity rather than topics — will a clustering
      pre-finetuning step do anything for me?
  answered_by:
  - nontopical-no-gain
  - nmi-predicts-gain
- ask:
    plain: does it matter which algorithm I use to group the unlabeled documents into pseudo-labels?
    jargon: does sequential Information Bottleneck over stemmed bag-of-words beat K-means
      or Hartigan's K-means over averaged GloVe embeddings as the source of inter-training
      pseudo-labels?
    task: which clustering method should I use to produce the pseudo-labels for an intermediate
      BERT training phase?
    practitioner: can I just use K-means over sentence embeddings for the clustering step,
      or do I need a bag-of-words method?
  answered_by:
  - sib-best-clustering
- ask:
    plain: with only a handful of labeled examples, could a simple word-count classifier or
      the document groups themselves do just as well as retraining BERT?
    jargon: do Naive Bayes and SVM baselines over BOW or GloVe, or nearest-cluster label propagation,
      match cluster-inter-trained BERT under small labeling budgets?
    task: how do I check whether a clustering-based BERT pipeline is worth it over a bag-of-words
      classifier on the same few labels?
    practitioner: should I bother fine-tuning BERT on cluster labels, or just label my clusters
      and classify by nearest cluster?
  answered_by:
  - not-just-bow
  - clusters-alone-insufficient
- ask:
    plain: what actually changes inside a language model's sentence representations after
      training it to predict document groups?
    jargon: how do BERT [CLS] embeddings change after cluster-label inter-training, measured
      by distance to class centroids?
    practitioner: is there evidence that cluster-label inter-training gives me a genuinely
      better starting point for fine-tuning, not just better numbers?
  answered_by:
  - embeddings-tighter
- ask:
    plain: how much extra compute and time does it cost to group unlabeled documents and train
      a model on those groups first?
    jargon: what is the runtime overhead of sIB clustering plus one inter-training epoch on
      a single GPU?
    task: how do I budget GPU time for adding a clustering-based intermediate training phase
      to a text classification pipeline?
    practitioner: I have one V100 and a 15K-document corpus — can I afford the clustering
      intermediate phase?
  answered_by:
  - cheap-to-run
- ask:
    plain: which work first used grouping of unlabeled text as a training step between language
      model pre-training and fine-tuning on few labels?
    jargon: which paper introduced unsupervised clustering pseudo-labels as an intermediate
      task for cold-start text classification in NLP?
    task: where do I start reading about training text classifiers when almost nothing is
      labeled yet?
    practitioner: what should I read first if I need a text classifier and have no annotation
      budget to speak of?
  answered_by:
  - context-cold-start
  - context-no-extra-labels
- ask:
    plain: once I can afford to label more examples, does an unsupervised pre-finetuning step
      stop being worth the trouble?
    jargon: up to what labeling budget is the gain from cluster-based inter-training over
      plain BERT fine-tuning statistically significant?
    task: how do I decide whether my annotation budget is small enough for a clustering intermediate
      phase to still pay off?
    practitioner: I can label about 1000 examples — is a cluster-based intermediate training
      phase still going to help me?
  answered_by:
  - significance-budget
  - topical-gain-64
- ask:
    plain: does training on document groups need any labeled data beyond the handful used
      for the final task?
    jargon: what supervision does cluster-based inter-training require beyond the target-task
      labels, compared with supervised intermediate tasks?
    task: how do I run an intermediate training phase when I have no labeled data from any
      other task to borrow?
    practitioner: I have no annotations at all and no related labeled dataset — can I still
      run the clustering intermediate phase, and what will it cost me?
  answered_by:
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
