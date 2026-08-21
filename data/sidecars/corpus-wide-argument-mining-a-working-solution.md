---
key: eindor2020corpuswide
coined: Retrospective Labeling
gloss: iteratively hand-labeling a classifier's own top-ranked predictions to build a balanced
  training set when relevant examples are rare
one_liner: Corpus-wide argument mining becomes practical by combining sentence-level queries
  over an index of ~400 million newspaper articles with Retrospective Labeling — repeatedly
  annotating the classifier's own top predictions — yielding 95% precision on the top 40 retrieved
  evidence sentences per motion.
claims:
- id: e2e-precision-vlc
  kind: result
  text: An end-to-end evidence retrieval system over a 400-million-article newspaper corpus
    reaches over 90% precision on the top 20 candidates per motion. The best model, BERT S+M,
    reaches 95% precision on the top 40.
  scope: 100 held-out motions; retrieval limited to sentences matching the Study/Expert Evidence
    queries and near-duplicate sentences removed; estimated positive prior among query-retrieved
    sentences is 0.3.
  evidence: Figure 2
- id: sentence-level-diversity
  kind: result
  text: Sentence-level retrieval over the newspaper corpus does not collapse into document
    retrieval. The top 20 and top 40 ranked candidates per motion come from an average of
    18.03 and 36.07 different documents respectively.
  scope: Measured on the very large newspaper corpus, where near-duplicates were filtered;
    the diversity figures come from the BA MaskS ranking, and Figure 3 reports document and
    journal counts for BERT S+M.
  evidence: Figure 3
- id: blendnet-accuracy
  kind: result
  text: On the BlendNet sentence-classification benchmark, retraining the same BiLSTM-plus-attention
    architecture on the newspaper-corpus dataset raises accuracy from 0.74 to 0.78, and BERT
    S+M reaches 0.84.
  scope: Wikipedia-sentence benchmark of a prior evidence-detection work; motions overlapping
    the training and development sets were excluded and models retrained for this evaluation.
  evidence: Table 1
- id: bert-masking
  kind: result
  text: 'Masking the topic token helps the BiLSTM architecture but hurts BERT: BERT MaskS+M
    reaches 0.82 accuracy on BlendNet while unmasked BERT S+M reaches 0.84.'
  scope: BlendNet accuracy at a 0.5 decision threshold; masking replaces Wikified topic mentions
    with a single token.
  evidence: Table 1
- id: dataset-vld
  kind: result
  text: Iterative retrospective labeling produced a dataset of 198,457 manually labeled sentence-motion
    pairs over the 400-million-article newspaper corpus, of which 33.5% are positive evidence
    examples.
  scope: 192 train and 47 development motions; top 40 predictions per motion and evidence
    type annotated per iteration by 10 crowd annotators, gold label by majority; Cohen's Kappa
    0.47.
  evidence: Section 4
- id: dataset-wiki
  kind: result
  text: A matching Wikipedia evidence dataset of 29,429 labeled sentences, 23% of them positive,
    was released at http://ibm.biz/debater-datasets.
  scope: Same train and development motions as the newspaper dataset; top 20 ranked predictions
    per motion annotated.
  evidence: Section 4
- id: train-on-large-corpus
  kind: result
  text: Models trained on the 154K-pair newspaper-corpus training set outperform models trained
    on the 22K-pair Wikipedia training set even when tested on the Wikipedia benchmark. Top-k
    precision on Wikipedia is nonetheless well below that on the newspaper corpus.
  scope: 100 test motions, precision of top k candidates; the model ranking order is identical
    across both benchmarks, and scores on Wikipedia top-k predictions are lower (t-test p=3.19e-9
    at k=20). Precisions are not comparable across the two benchmarks.
  evidence: Figure 4
- id: ukp-transfer
  kind: result
  text: An evidence-trained BERT S+M classifier on the UKP-TUDA argumentativeness benchmark
    gives precision 0.88 at recall 0.16 with a 0.5 threshold. At a threshold of 0.002 it gives
    precision 0.66 and recall 0.75 (F1 0.70), against 0.65/0.67/0.67 for a classifier trained
    directly for that task.
  scope: 'Zero-adaptation transfer: the model was trained only on query-retrieved Study and
    Expert Evidence, whereas UKP-TUDA labels any sentence with a clear stance as positive,
    which is why recall at the default threshold is low.'
  evidence: Figure 5
- id: ukp-ranking-order
  kind: result
  text: Among UKP-TUDA sentences scored below the 0.5 threshold, argumentative sentences receive
    a mean score of 7.3e-2 versus 1.5e-2 for non-argumentative ones, showing that an evidence-trained
    ranker still prefers argumentative text.
  scope: UKP-TUDA benchmark sentences below the decision threshold, with the difference significant
    by t-test; a manual check of 20 sentences above and 20 below the threshold found 14 versus
    2 to be Study or Expert Evidence.
  evidence: Section 7.3
- id: context-first-e2e
  kind: context
  text: Corpus Wide Argument Mining - A Working Solution presents an end-to-end, high-precision
    argument retrieval system over a corpus of roughly 400 million newspaper and journal articles.
    That corpus is about 50 times larger than the Wikipedia corpora used by earlier sentence-level
    argument mining work.
  scope: As of AAAI 2020; retrieval targets Study Evidence and Expert Evidence for motions
    whose topic is a Wikipedia title, and precision is measured on top-ranked candidates rather
    than over the full corpus.
- id: context-retrospective-labeling
  kind: context
  text: Retrospective Labeling, introduced in Corpus Wide Argument Mining - A Working Solution,
    is a precision-oriented active-learning strategy for class-imbalanced retrieval. Repeatedly
    hand-labeling a classifier's top-ranked predictions both enriches positives and surfaces
    the hard negatives that limit top-k precision.
  scope: Demonstrated only for evidence retrieval from newspaper and Wikipedia corpora; intended
    for retrieval tasks where precision is the metric and positive examples are scarce, and
    it requires substantial ongoing annotation effort.
- id: context-supervised-vs-weak
  kind: context
  text: Corpus Wide Argument Mining - A Working Solution argues that sentence-level topic-relevant
    argument retrieval can be tackled with fully supervised learning rather than weak supervision.
    The large balanced labeled set this needs is bootstrapped from query-retrieved sentences.
  scope: The queries used to restrict the search space play a role similar to weak-supervision
    rules; arguments in sentences that do not match any query, or that do not mention the
    topic explicitly, are missed by design.
qa:
- ask:
    plain: how accurate are the top results when a computer searches a huge news archive for
      arguments about a debate topic?
    jargon: what top-k precision does an end-to-end evidence retrieval pipeline achieve over
      a 400-million-article newspaper corpus?
    task: how do I get a shortlist of usable supporting evidence sentences for a controversial
      motion out of a large news archive?
    practitioner: if I run corpus-wide argument retrieval for a motion, can I trust the first
      few dozen sentences it hands me without reading everything below them?
  answered_by:
  - e2e-precision-vlc
- ask:
    plain: when a system pulls single sentences about a topic out of millions of articles,
      do they all come from the same few articles?
    jargon: does sentence-level evidence retrieval over a newspaper corpus degenerate into
      document-level retrieval in the top-ranked candidates?
    task: how do I check that the evidence sentences I retrieve for one motion span many different
      source articles?
    practitioner: should I bother with sentence-level argument retrieval, or will document
      retrieval plus a sentence picker give me the same spread of sources?
  answered_by:
  - sentence-level-diversity
- ask:
    plain: how do you build a labeled training set when the sentences you actually want are
      a tiny fraction of a huge collection?
    jargon: how is retrospective labeling used as a precision-oriented active-learning strategy
      for class-imbalanced sentence retrieval?
    task: how do I collect enough positive examples to train an evidence detector when positives
      are rare in the corpus?
    practitioner: is it worth hand-labeling my current classifier's top-ranked predictions
      instead of labeling a random sample of sentences?
  answered_by:
  - context-retrospective-labeling
  - dataset-vld
- ask:
    plain: for finding evidence sentences, is a large training set from newspapers better
      than a smaller one from the same source as the test data?
    jargon: does a 154K-pair newspaper-corpus training set beat a smaller Wikipedia training
      set on a Wikipedia evidence benchmark?
    task: which labeled corpus should I train an evidence-detection classifier on if I plan
      to run it on Wikipedia sentences?
    practitioner: I already have a small in-domain evidence set for Wikipedia -- should I
      switch to a much larger newspaper-sourced one instead?
  answered_by:
  - train-on-large-corpus
  - blendnet-accuracy
- ask:
    plain: when a model looks for sentences relevant to a debate topic, does hiding the topic
      word from the input help or hurt?
    jargon: does masking the topic token improve BERT-based evidence classification, or only
      BiLSTM-with-attention architectures?
    task: should I replace the motion's topic term with a mask token when feeding sentence-motion
      pairs to an evidence classifier?
    practitioner: I am fine-tuning BERT on sentence-plus-motion input for evidence detection
      -- do I mask the topic or leave it in?
  answered_by:
  - bert-masking
  - blendnet-accuracy
- ask:
    plain: where can I find labeled sentences marked as evidence for and against debate topics?
    jargon: which annotated context-dependent evidence datasets are released for sentence-level
      argument mining, and at what scale?
    task: how do I get labeled sentence-motion pairs to train and evaluate an evidence detector
      without annotating my own?
    practitioner: are the labeled evidence sets from corpus-wide argument mining big enough
      and balanced enough to train on?
  answered_by:
  - dataset-vld
  - dataset-wiki
- ask:
    plain: does a model trained to spot study and expert evidence also recognise argumentative
      sentences in general?
    jargon: how does an evidence-trained BERT S+M classifier transfer to the UKP-TUDA argumentativeness
      benchmark across decision thresholds?
    task: can I reuse an evidence-detection classifier to score general argumentativeness
      instead of training a new one for that label?
    practitioner: my task is finding argumentative sentences, not just study or expert evidence
      -- will an evidence-trained classifier be enough, and what threshold do I set?
  answered_by:
  - ukp-transfer
  - ukp-ranking-order
- ask:
    plain: which paper should I read first about automatically finding arguments on a topic
      across a massive text collection?
    jargon: what work established end-to-end corpus-wide sentence-level argument retrieval
      beyond Wikipedia-scale corpora?
    practitioner: I need a starting reference for building topic-relevant argument retrieval
      at scale -- which paper covers it end to end?
  answered_by:
  - context-first-e2e
  - context-supervised-vs-weak
- ask:
    plain: is keyword search enough to find arguments about a topic, or do you need a trained
      classifier on top?
    jargon: for topic-relevant sentence-level argument mining, is fully supervised learning
      preferable to weak supervision over query-retrieved candidates?
    task: how do I go beyond query-based sentence retrieval when collecting arguments for
      a controversial motion?
    practitioner: should I train a fully supervised evidence classifier, or rely on weak supervision
      and query heuristics for argument retrieval?
  answered_by:
  - context-supervised-vs-weak
misreadings:
- The 95% precision figure is precision among the top 40 ranked candidates per motion, not
  precision over all evidence sentences in the corpus, and it says nothing about recall.
- 'Retrospective Labeling is not label propagation or pseudo-labeling: the top predictions
  selected for labeling are annotated manually, and no automatic similarity between arguments
  is computed.'
- 'The low 0.16 recall on the UKP-TUDA benchmark is not a failure of the model but a definitional
  mismatch: the model is trained to find Study and Expert Evidence, while the benchmark labels
  any sentence with a clear stance as positive.'
- Precision numbers on the newspaper-corpus benchmark and the Wikipedia benchmark are not
  comparable, because Wikipedia may simply not contain k relevant sentences for a given motion.
- 'Masking the topic is not universally helpful: it improves the BiLSTM-with-attention models
  but degrades BERT, whose best configuration uses unmasked sentences plus the motion.'
terminology:
  Motion: A high-level claim implying a clearly positive or negative stance towards a debate
    topic, optionally naming a policy or action to be taken, such as 'ban the sale of violent
    video games'.
  Evidence: A single sentence that clearly supports or contests a motion while providing an
    indication of whether a belief or claim is true, rather than merely asserting a belief
    or claim.
  Study Evidence: Evidence that presents a quantitative analysis of data in support of or
    against a motion.
  Expert Evidence: Evidence consisting of testimony by a relevant expert or authority on the
    motion's topic.
  Sentence-Level (SL) approach: Argument retrieval that indexes and queries individual sentences
    of a corpus directly, instead of first retrieving topic-relevant documents and then mining
    arguments inside them.
  Retrospective Labeling: An iterative annotation scheme in which a classifier's highest-scoring
    predictions are manually labeled and added to the training set, enriching the data with
    positives and with hard negatives near the decision region that matters for top-k precision.
  MaskS: An input variant in which the topic mention inside a candidate sentence is replaced
    by a single special token, giving a uniform representation across surface forms and across
    topics.
  S+M: An input variant in which the classifier receives both the unmasked candidate sentence
    and the motion text, so the model judges evidence for an explicit motion rather than an
    implicit one.
---
