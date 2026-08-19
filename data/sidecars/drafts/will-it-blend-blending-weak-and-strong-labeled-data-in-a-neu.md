<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced via a forced tool call) + 1 repair round. Every claim, number
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

Then promote it:  python scripts/draft_sidecars.py --accept will-it-blend-blending-weak-and-strong-labeled-data-in-a-neu

Stamp: spec=74e012ff9654 checks=pass body=05e80a509fdb
-->
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
- q:
  - How can I train a neural network when I only have a few thousand hand-labeled examples?
  - Does adding noisy automatically-labeled data during training help a small supervised dataset?
  - What does BlendNet's blending schedule buy over pre-training on weak labels?
  answers:
  - blending-beats-pretraining
  - gain-grows-as-sld-shrinks
- q:
  - How much hand-labeled data does blending weak labels save?
  - Is there a measured equivalence between blended weak data and extra human annotation?
  - How many strong labeled sentences is weak labeled data worth in evidence detection?
  answers:
  - sld-equivalence
- q:
  - Can I just concatenate noisy weak labels with my clean training set?
  - Does mixing weak and strong labeled data in one pile work without a schedule?
  - Why is a decay schedule needed instead of simply adding weak labels to training data?
  answers:
  - naive-union-fails
  - wld-alone-is-weak
- q:
  - What blend factor and how many initialization epochs should I use for weak-data blending?
  - How were the BlendNet hyperparameters for weak-data decay chosen?
  - How fast should the weak-data fraction decay across epochs?
  answers:
  - small-blend-factor
- q:
  - Is there a labeled dataset for topic-dependent evidence detection?
  - Where can I find crowd-annotated sentences labeled as evidence for or against a topic?
  - What does the IBM Debater evidence detection release contain, and how was it annotated?
  answers:
  - dataset-release
  - context-corpus-wide-evidence
- q:
  - How can weak labels for argument mining be generated for free?
  - Does the 'that + topic concept' Wikipedia query find argumentative sentences?
  - What is the precision of retrieving evidence sentences with a 'that + topic' pattern?
  answers:
  - that-query-prior
- q:
  - Does more weak labeled data always help, or does its quality matter more?
  - Which weak-data source worked better for evidence detection, debate portal structure or
    a Wikipedia query?
  - Is a larger noisy corpus better than a smaller, better-matched noisy corpus?
  answers:
  - wld-quality-over-quantity
- q:
  - What should I read about combining weak supervision with a small clean training set?
  - Which papers introduced blending weak and strong labels inside one network?
  - Where does the idea of using weak labels throughout training rather than just for pre-training
    come from?
  answers:
  - context-general-recipe
- q:
  - When is weak supervision most useful in argument mining?
  - Does the benefit of weak labels shrink as human annotation grows?
  - At what training-set size does blending weak data stop paying off?
  answers:
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
