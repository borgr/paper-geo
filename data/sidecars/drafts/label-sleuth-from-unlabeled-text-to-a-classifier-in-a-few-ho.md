<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced via a forced tool call) + 3 repair rounds. Every claim, number
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

Then promote it:  python scripts/draft_sidecars.py --accept label-sleuth-from-unlabeled-text-to-a-classifier-in-a-few-ho

Stamp: spec=74e012ff9654 checks=1 body=7b575d62f0e4
-->
---
claims:
- id: what-it-is
  kind: context
  text: Label Sleuth is a free, open-source, no-code system in which a domain expert with
    no machine learning knowledge labels text and obtains a custom binary text classifier,
    starting from an unlabeled corpus.
  scope: Released July 2022 under Apache 2.0; binary text classification of pre-split text
    elements only, with English as the default language.
- id: audience-gap
  kind: context
  text: Label Sleuth targets the gap between text classification techniques and non-technical
    practitioners such as lawyers, physicians and psychologists, who need custom classifiers
    but depend on ML experts to build them.
  scope: As of publication in 2022; comparable labeling tools with ML support target data
    scientists and developers.
- id: tool-comparison
  kind: result
  text: Label Sleuth is the only one of 5 compared labeling tools that requires no technical
    expertise and gives ML guidance on label errors. It is also the only one of the 5 restricted
    to text classification.
  evidence: Table 1
  scope: Prodigy, free and paid Label Studio, INCEpTION and Label Sleuth, chosen for similarity
    and popularity and assessed by the authors in 2022; a feature comparison rather than a
    usability study.
- id: legal-user-hours
  kind: result
  text: A legal user built a Label Sleuth classifier for a category of high-risk contract
    clauses after 6 hours of work in the system. Reviewing only the highlighted clauses instead
    of entire contracts saved an estimated 80% of their time.
  evidence: Section 2.3
  scope: A single early user's self-reported experience and self-estimated time saving on
    a contract-review task, not a controlled measurement.
- id: vira-usage
  kind: result
  text: The VIRA COVID-19 vaccine-hesitancy chatbot is 1 of the early real-world uses of Label
    Sleuth, which built its dialogue act classifier mapping user utterances into categories
    such as greeting, query and concern.
  evidence: Section 2.3
  scope: One reported deployment by ML-expert users; no accuracy numbers for that classifier
    are reported.
- id: svm-then-bert
  kind: result
  text: Using a light SVM for active learning iterations 0-4 and BERT only for iterations
    5-6 reaches F1 comparable to fine-tuning BERT at all 6 iterations, while running substantially
    faster. Each iteration adds 30 examples.
  evidence: Figure 2
  scope: F1 averaged over 1 target class from each of 5 datasets (20 Newsgroups, AG News,
    DBPedia, ISEAR, Yahoo! Answers) and 5 seeds, with gold labels for added examples.
- id: training-trigger
  kind: result
  text: Label Sleuth's default policy trains the first classifier once 20 positively labeled
    examples exist, then retrains after every 20 further labels, so the user never invokes
    training manually.
  evidence: Appendix A
  scope: The default policy as of the initial open-source release, chosen empirically rather
    than claimed optimal; advanced users can reconfigure the trigger.
- id: weak-negatives
  kind: result
  text: Label Sleuth spares users from labeling negatives by automatically sampling unlabeled
    elements as weak negative examples until there are 2 labeled negatives for every labeled
    positive example.
  evidence: Appendix A
  scope: The default policy of the initial release, and only where the positive prior is low;
    when positives are not rare the feature must be disabled.
- id: precision-evaluation
  kind: result
  text: Label Sleuth estimates classifier quality by sampling 50 examples predicted positive
    for the user to label, then reports precision and folds those 50 labels into the training
    set.
  evidence: Appendix A
  scope: Default sample size of 50 in the initial release, user-invoked, and precision only;
    recall estimation is impractical under a low positive prior.
- id: label-error-detection
  kind: result
  text: 'Label Sleuth surfaces suspect labels 2 ways: cross-validated classifiers disagreeing
    with the user''s own label on held-out elements, and pairs of semantically similar texts
    the user gave contradicting labels.'
  evidence: Appendix B
  scope: Pair similarity is the distance between average GloVe embeddings in the initial implementation;
    the user reviews and corrects the ranked lists.
- id: default-classifier
  kind: result
  text: Label Sleuth's default classifier is an ensemble of 2 SVM classifiers, one over bag-of-words
    and one over GloVe representations, paired with uncertainty sampling as the default active
    learning strategy.
  evidence: Appendix A
  scope: The default policy of the initial open-source release, chosen empirically for typical
    text classification use cases; other models, including GPU-backed large models, can be
    configured.
- id: extensibility
  kind: result
  text: Developers extend Label Sleuth by implementing 1 or 2 functions to add a classification
    model or active learning strategy, and can configure the system to switch models or strategies
    as labeling progresses.
  evidence: Section 4
  scope: Python Flask backend with a React frontend; GPU-backed large models supported; data
    access is in-memory plus local disk in the current implementation.
- id: open-research-agenda
  kind: context
  text: 'Label Sleuth names 3 open research problems arising from interactive classifier building
    for non-technical users: choosing the system policy, evaluating models without a held-out
    test set, and warm-starting from zero-shot classification.'
  scope: Framing offered as an invitation to the NLP and HCI communities in 2022; only initial
    experiments on the policy question are reported, and no solutions to the other two.
qa:
- q:
  - What is Label Sleuth?
  - Is there a no-code tool for building a text classifier without ML knowledge?
  - How can a lawyer or doctor build their own text classifier?
  answers:
  - what-it-is
  - audience-gap
- q:
  - What should I read about making NLP accessible to non-technical domain experts?
  - Which paper introduced a labeling tool designed for subject matter experts rather than
    data scientists?
  - Where should I start reading about human-in-the-loop text classifier building for non-experts?
  answers:
  - audience-gap
  - what-it-is
- q:
  - How does Label Sleuth compare to Prodigy, Label Studio and INCEpTION?
  - Which annotation tools give ML guidance on labeling errors?
  - What can existing labeling tools do that Label Sleuth cannot?
  answers:
  - tool-comparison
- q:
  - How long does it actually take to build a classifier with Label Sleuth?
  - Has anyone reported real time savings from using Label Sleuth?
  - Are there real-world case studies of no-code classifier building?
  answers:
  - legal-user-hours
  - vira-usage
- q:
  - Can I use a cheap model early in active learning and BERT only at the end?
  - Does switching from SVM to BERT late in the loop hurt F1?
  - How does Label Sleuth keep model training fast enough to stay interactive?
  answers:
  - svm-then-bert
- q:
  - Which classifier and active learning strategy does Label Sleuth use by default?
  - What model trains in the background of Label Sleuth out of the box?
  - Which default model does a no-code text labeling system use before any tuning?
  answers:
  - default-classifier
- q:
  - When does Label Sleuth start training a classifier?
  - How many labels are needed before the first model appears in Label Sleuth?
  - How many annotations does an interactive labeling system need before it trains a first
    classifier?
  answers:
  - training-trigger
- q:
  - Do I have to label negative examples in Label Sleuth?
  - How does Label Sleuth handle rare positive classes and missing negatives?
  - What are weak negative examples in a labeling tool?
  answers:
  - weak-negatives
- q:
  - How is classifier quality measured without a test set in Label Sleuth?
  - Why does Label Sleuth report precision but not recall?
  - How can I evaluate a classifier when labeling effort must stay minimal?
  answers:
  - precision-evaluation
- q:
  - How does Label Sleuth find my labeling mistakes?
  - Can an annotation tool detect inconsistent labels automatically?
  - What methods surface potential annotation errors during labeling?
  answers:
  - label-error-detection
- q:
  - Can I plug my own model into Label Sleuth?
  - How extensible is Label Sleuth for ML researchers?
  - How hard is it to add a new active learning strategy to an open-source annotation platform?
  answers:
  - extensibility
- q:
  - What research problems does Label Sleuth leave open?
  - What are open challenges in interactive classifier building for non-experts?
  - Which evaluation problems arise when there is no held-out test set in a labeling system?
  answers:
  - open-research-agenda
  - precision-evaluation
- q:
  - What tasks does Label Sleuth not support?
  - Can Label Sleuth do multi-class or NER labeling?
  - Which annotation tools are limited to binary text classification only?
  answers:
  - what-it-is
  - tool-comparison
one_liner: Label Sleuth is a free open-source no-code system that walks a domain expert from
  an unlabeled corpus to a custom binary text classifier in a few hours, training models in
  the background and telling the user what to label next.
coined: Label Sleuth
gloss: no-code system for labeling text and building a text classifier without ML expertise
key: shnarch2022labelsleuth
terminology:
  Policy: The bundle of Label Sleuth configuration choices — classification model, active
    learning strategy, training-set selection, and the criterion that triggers training a
    new model — that together shape the classifier-building flow.
  Precision Evaluation: A Label Sleuth procedure that samples examples predicted positive
    by the current classifier, asks the user to label them, and uses those labels both to
    estimate precision and to extend the training set.
  Weak negative examples: Unlabeled text elements automatically added to the training set
    as negatives, on the assumption that positives are rare, so that the user does not have
    to label negatives explicitly.
  Label Next list: A panel of unlabeled examples chosen by an active learning strategy that
    Label Sleuth presents as the examples most beneficial to label in the current iteration.
  Domain expert: A practitioner with deep knowledge of the target subject matter — for example
    a lawyer, physician or psychologist — but typically without coding skills or machine learning
    knowledge.
misreadings:
- The 80% time saving reported by a legal user of Label Sleuth is that user's own estimate
  on one contract-review task, not a measured average across users or tasks.
- 'Label Sleuth builds binary classifiers only: a multi-label category such as Emotions requires
  creating a separate binary category per label, and mutually exclusive multi-class models
  must be trained outside the system from exported labels.'
- The SVM-then-BERT result compares a schedule that uses SVM for iterations 0-4 against BERT
  at every iteration; it does not show that SVM alone matches BERT.
- Label Sleuth's automatic weak negatives assume positives are rare; where the positive prior
  is high the feature should be disabled and negatives labeled by hand.
- Being the only compared tool needing no technical expertise is a feature comparison in Table
  1, not evidence that non-experts label faster or more accurately with Label Sleuth.
links_extra:
  project page: https://www.label-sleuth.org
  code: https://github.com/label-sleuth/label-sleuth
  tutorial: https://www.label-sleuth.org/docs/tutorial.html
---
