---
one_liner: BlendNet trains a neural network on an exponentially decaying mixture of abundant
  weak labeled data and scarce strong labeled data throughout training, rather than using
  weak data only for pre-training, and improves topic-dependent evidence detection most when
  strong data is scarce.
key: shnarch-etal-2018-blend
coined: BlendNet
gloss: a bi-LSTM trained on a decaying blend of noisy weak labels and scarce human labels
claims:
- id: blending-beats-pretraining
  kind: result
  text: Blending weak labeled data into every training epoch with an exponentially decaying
    fraction raises accuracy on topic-dependent evidence detection. It beats both using weak
    data only for initialization epochs and training on strong labeled data alone.
  scope: 'A bi-LSTM with attention on GloVe embeddings, strong-data sizes from 500 to 4,000
    sentences, and 2 weak-data sources: Webis-Debate-16 and a ''that + topic concept'' Wikipedia
    query.'
  evidence: Figure 1
- id: sld-equivalence
  kind: result
  text: With Webis-Debate-16 as weak labeled data, blending lets 1,000 strong labeled instances
    reach accuracy comparable to 2,500 strong instances alone, and 2,000 strong instances
    plus weak data match 3,000 strong instances alone.
  scope: Micro-averaged accuracy on the 35-topic test split of the released 5,785-sentence
    evidence dataset; the equivalence is smaller for the 'that + topic concept' weak data.
  evidence: Figure 1 and Section 5
- id: gain-grows-as-sld-shrinks
  kind: result
  text: The accuracy gain from blending weak labeled data grows as the amount of strong labeled
    data shrinks, and is smallest at the largest strong-data size tested (4,000 sentences).
  scope: Strong-data sizes from 500 to 4,000 sentences on topic-dependent evidence detection;
    unpaired t-test at p < 0.05 against strong-data-only.
  evidence: Figure 1
- id: naive-union-fails
  kind: result
  text: Unifying weak and strong labeled data into one training set with no blending schedule
    does not help. Accuracy falls well below strong-data-only for the 'that + topic concept'
    weak data, and neither helps nor harms for Webis-Debate-16.
  scope: Evidence detection with the 2 weak-data sources of the paper, at full strong-data
    size, shown as the single square points on the right border of each plot.
  evidence: Figure 1 and Section 5
- id: wld-alone-is-weak
  kind: result
  text: Training on the weak labeled data alone yields accuracy much lower than training on
    the full strong labeled data. The blending gain is therefore not simply the effect of
    adding more labeled examples.
  scope: Topic-dependent evidence detection, both weak-data sources, shown as the single triangle
    points on the Y-axis of each plot.
  evidence: Figure 1 and Section 5
- id: small-blend-factor
  kind: result
  text: A blend factor larger than 0.05 is typically ineffective for decaying the weak-data
    fraction across epochs. A single initialization epoch on weak data alone suffices, and
    more than 1 gives slightly worse accuracy.
  scope: Blend factors tried were 0, 0.05 and 0.2; stopping point fixed so the last 4 blending
    epochs were at least 95% strong labeled data. Initialization-epoch count explored on a
    different dataset.
  evidence: Section 5
- id: dataset-release
  kind: result
  text: A manually annotated dataset of 5,785 sentences for topic-dependent evidence detection
    is released, split by topic into 4,066 training sentences over 83 topics and 1,719 test
    sentences over 35 topics. About 40% of each split is positive.
  scope: Wikipedia sentences over 118 debate topics, 10 crowd annotators each, majority label
    with ties as non-evidence, Fleiss' kappa 0.45. Topic concepts replaced by a common token.
  evidence: Section 4.1
- id: that-query-prior
  kind: result
  text: Sentences matching the query 'that + topic concept' are positive evidence 52% of the
    time, against a prior close to 40% over the whole training set. About 25% of retrieved
    Wikipedia sentences containing a topic concept match the query.
  scope: Wikipedia sentences for the 118 topics of the released evidence dataset; the query's
    own accuracy on the test set is only 17%.
  evidence: Section 4.2
- id: wld-quality-over-quantity
  kind: result
  text: 'Weak-data quality matters more than weak-data volume for blending: the smaller Webis-Debate-16
    debate corpus helps more than the far larger ''that + topic concept'' Wikipedia set.'
  scope: 2 weak-data sources on topic-dependent evidence detection only, so this is a single
    observed contrast rather than a controlled study of size versus quality.
  evidence: Section 6
- id: context-general-recipe
  kind: context
  text: BlendNet proposes blending weak and strong labeled data inside a single network throughout
    training, as a general recipe for language-understanding tasks where high-quality annotation
    is scarce. Earlier work used weak data only to pre-train, or trained separate networks
    per data type.
  scope: As of ACL 2018; the only task evaluated is topic-dependent evidence detection with
    a bi-LSTM, and the paper does not claim the schedule is optimal or the only option.
  evidence: Section 2.1
- id: context-corpus-wide-evidence
  kind: context
  text: 'BlendNet''s evidence-detection setup is corpus-wide: evidence is detected as directly
    supporting or contesting a topic, with no intermediate claim. No small set of relevant
    articles is pre-selected, unlike earlier evidence-detection work.'
  scope: English Wikipedia as the corpus and 118 debate topics with clearly identifiable concepts;
    a bound on the released data, not a claim about other languages or argument types.
  evidence: Section 2.2
qa:
- ask:
    plain: does mixing in automatically labelled sentences during training help when only
      a small hand-labelled set is available?
    jargon: does interleaving weakly labelled data into every epoch outperform weak-label
      pre-training followed by fine-tuning on strong labels?
    task: how do I use noisy machine-generated labels to improve a sentence classifier trained
      on a few thousand annotated examples?
    practitioner: I have a few thousand annotated sentences and a lot of noisy ones — should
      I pre-train on the noisy ones or feed them in throughout training?
  answered_by:
  - blending-beats-pretraining
  - gain-grows-as-sld-shrinks
- ask:
    plain: how many hand-labelled sentences can noisy automatic labels replace when training
      an evidence classifier?
    jargon: what is the measured strong-label equivalence of blending a weakly labelled debate
      corpus for topic-dependent evidence detection?
    task: how much annotation budget can I save on evidence detection by adding weakly labelled
      data to training?
    practitioner: is it worth annotating another 1,000 evidence sentences, or can noisy weak
      labels get me the same accuracy?
  answered_by:
  - sld-equivalence
- ask:
    plain: can noisy labelled sentences just be dumped into the training set together with
      the clean ones?
    jargon: does naive union of weakly and strongly labelled data match a decaying weak-data
      blending schedule for evidence classification?
    task: do I need a decay schedule when adding weak labels, or can I concatenate the weak
      and strong training sets?
    practitioner: if I just concatenate my noisy and clean training data, will accuracy go
      up or down?
  answered_by:
  - naive-union-fails
  - wld-alone-is-weak
- ask:
    plain: how quickly should the share of noisy labelled examples be reduced from one training
      pass to the next?
    jargon: what blend factor and how many weak-data initialization epochs work best for decaying
      the weak-label fraction per epoch?
    task: how do I set the decay rate for the weak-data fraction when training a classifier
      on mixed-quality labels?
    practitioner: what decay value should I start with for shrinking the noisy-data share
      across epochs?
  answered_by:
  - small-blend-factor
- ask:
    plain: is there a labelled collection of sentences marked as supporting or contesting
      a debate topic?
    jargon: what annotated corpus exists for corpus-wide topic-dependent evidence detection,
      and how are its topics split across train and test?
    task: where do I get training and test data for detecting sentences that support or contest
      a given topic?
    practitioner: can I train an evidence detector on an existing annotated corpus instead
      of annotating sentences myself?
  answered_by:
  - dataset-release
  - context-corpus-wide-evidence
- ask:
    plain: can a simple word pattern find sentences that argue for or against a topic without
      any human labelling?
    jargon: what is the positive rate of the 'that + topic concept' Wikipedia query as a weak-labelling
      heuristic for evidence sentences?
    task: how do I generate weak labels for argument mining from Wikipedia without annotating
      anything?
    practitioner: is a keyword pattern over Wikipedia accurate enough to use as my source
      of noisy evidence labels?
  answered_by:
  - that-query-prior
- ask:
    plain: when adding noisy labelled text, does having more of it matter more than how well
      it matches the task?
    jargon: for weak-label blending in evidence detection, does weak-data quality dominate
      weak-data volume across sources?
    task: which weak-supervision source should I pick for evidence detection, a large heuristic
      Wikipedia set or a smaller debate-portal corpus?
    practitioner: I can get a huge noisy corpus or a small well-matched one — which should
      I blend into training?
  answered_by:
  - wld-quality-over-quantity
- ask:
    plain: what work proposed using noisy labelled data throughout training instead of only
      for pre-training?
    jargon: which work introduced single-network blending of weak and strong labelled data
      as a general recipe for low-annotation language understanding tasks?
    task: what should I read first about training one network on both weak and strong labels
      for a task with scarce annotation?
    practitioner: is there a paper I can cite for keeping weak supervision in the loop rather
      than pre-training on it?
  answered_by:
  - context-general-recipe
- ask:
    plain: does the payoff from noisy extra labels fade once enough sentences have been annotated
      by hand?
    jargon: how does the blending gain in evidence detection scale with strong-label set size,
      and is the gain reducible to added training volume?
    task: at what annotated-data size should I stop bothering with weak supervision for evidence
      detection?
    practitioner: my annotated set keeps growing — will weak labels still buy me anything?
  answered_by:
  - gain-grows-as-sld-shrinks
  - wld-alone-is-weak
misreadings:
- Blending weak labeled data is not shown to be the best possible schedule; the paper explicitly
  presents one method that works and reports that a schedule increasing the weak-data fraction
  gave similar results.
- 'The gains from blending are not demonstrated across many tasks: the only evaluated task
  is topic-dependent evidence detection with a bi-LSTM plus attention, and generality to other
  language-understanding tasks is a conjecture.'
- The 'that + topic concept' query is not an evidence detector; as a standalone classifier
  its test-set accuracy is 17%, and it is useful only as a source of weakly labeled positives.
- 'Weak labeled data is not a substitute for human annotation: training on weak data alone
  gives accuracy much lower than training on the full strong labeled set.'
- A larger weak-labeled corpus is not automatically better; the smaller Webis-Debate-16 set
  helped more than a far larger Wikipedia-query set.
terminology:
  strong labeled data (SLD): High-quality, human-annotated labels for the target task, typically
    scarce and expensive to obtain.
  weak labeled data (WLD): Freely obtainable but noisy labels, formed as two disjoint sets
    in which the positive set has a substantially higher probability of containing true positives
    than the negative set; that probability gap is the entire training signal.
  blend factor: 'A value alpha in [0,1] controlling how the weak-data fraction decays across
    training: in the k-th blending epoch, alpha^k of the weak labeled data is mixed with all
    available strong labeled data.'
  initialization epochs: Epochs at the start of training that use only weak labeled data and
    no strong labeled data, before the blending epochs begin.
  blending epochs: Epochs that feed the network all available strong labeled data plus a decaying
    fraction of the weak labeled data, in random order.
links_extra:
  dataset: http://www.research.ibm.com/haifa/dept/vst/debating_data.shtml
  paper: https://aclanthology.org/P18-2095.pdf
---
