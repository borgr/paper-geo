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
- ask:
    plain: is there a free tool that lets someone with no coding skills build a classifier
      that sorts text into two categories?
    jargon: what no-code system supports end-to-end binary text classifier construction by
      a domain expert over an unlabeled corpus?
    task: how do I turn a pile of unlabeled documents into a custom text classifier without
      writing code or hiring a data scientist?
    practitioner: I have no machine learning background but need a classifier for my own documents,
      can Label Sleuth do that for me?
  answered_by:
  - what-it-is
  - audience-gap
- ask:
    plain: where should someone start reading about tools that let subject matter experts
      build text classifiers themselves?
    jargon: which paper introduced a human-in-the-loop labeling system aimed at domain experts
      rather than machine learning practitioners?
    task: what should I read first if I want to understand how non-technical experts can build
      their own text classifiers?
    practitioner: my team is lawyers and clinicians rather than engineers, is there published
      work on labeling systems built for people like us?
  answered_by:
  - audience-gap
  - what-it-is
- ask:
    plain: how does Label Sleuth differ from other text annotation tools people already use?
    jargon: which text annotation platforms require no technical expertise and provide guidance
      on labeling errors?
    task: how do I pick between labeling tools when nobody on my team can write code or configure
      a model?
    practitioner: we already use a commercial annotation tool, what would we gain or lose
      by switching to Label Sleuth?
  answered_by:
  - tool-comparison
- ask:
    plain: has anyone actually used a no-code labeling tool on a real job, and how much time
      did it take them?
    jargon: what deployment case studies report annotation effort and downstream use of Label
      Sleuth classifiers?
    task: how many hours should I budget to get a usable classifier for a niche category out
      of an interactive labeling system?
    practitioner: before I commit my own time, is there evidence that someone built something
      useful with Label Sleuth and saved effort?
  answered_by:
  - legal-user-hours
  - vira-usage
- ask:
    plain: how can a labeling tool keep the suggestions coming fast when a big language model
      is slow to train?
    jargon: does swapping an SVM for BERT only in later active learning iterations preserve
      F1 relative to fine-tuning BERT every iteration?
    task: how do I keep model retraining fast enough for interactive labeling without giving
      up final classifier quality?
    practitioner: should I let a heavier transformer train on every labeling round, or start
      with something light and switch later?
  answered_by:
  - svm-then-bert
- ask:
    plain: which model does Label Sleuth train in the background if nobody changes any settings?
    jargon: what is Label Sleuth's default classifier architecture and default active learning
      strategy?
    task: how do I know which model and example-selection strategy I am getting out of the
      box in an interactive labeling system?
    practitioner: do I need to configure a model before I start labeling in Label Sleuth,
      or is the default fine?
  answered_by:
  - default-classifier
- ask:
    plain: how many examples do I have to mark before a labeling tool starts giving predictions?
    jargon: what labeled-positive threshold triggers initial classifier training and subsequent
      retraining in Label Sleuth?
    task: how do I get a first model out of an interactive labeling session without deciding
      when to hit train?
    practitioner: do I have to tell Label Sleuth when to train, or will it start on its own
      once I have labeled enough?
  answered_by:
  - training-trigger
- ask:
    plain: if only a tiny fraction of my texts belong to the category, do I have to label
      all the ones that do not?
    jargon: how does Label Sleuth obtain negative examples for a rare positive class without
      explicit negative annotation?
    task: how do I train a binary classifier for a rare category when I have only marked the
      positive examples?
    practitioner: can I skip labeling negatives in Label Sleuth and still get a working classifier
      for a rare clause type?
  answered_by:
  - weak-negatives
- ask:
    plain: how can I tell whether a classifier is any good if I never built a test set?
    jargon: how does Label Sleuth estimate classifier precision without a held-out labeled
      test set?
    task: how do I check the quality of a classifier I built by labeling as I go, with no
      separate evaluation set?
    practitioner: how will I know when the Label Sleuth model is accurate enough to stop labeling?
  answered_by:
  - precision-evaluation
- ask:
    plain: can a labeling tool tell me when I have contradicted myself while marking texts?
    jargon: what mechanisms surface suspect annotations during interactive labeling, such
      as cross-validated disagreement or contradicting labels on similar texts?
    task: how do I find and fix inconsistent labels in a dataset I am annotating as I go?
    practitioner: will Label Sleuth flag my own labeling mistakes, or do I need a separate
      quality check?
  answered_by:
  - label-error-detection
- ask:
    plain: can a researcher plug their own model into an open-source labeling tool, and how
      much code does it take?
    jargon: how are new classification models and active learning strategies integrated into
      the Label Sleuth architecture?
    task: how do I add my own active learning strategy to an existing annotation platform
      instead of building one from scratch?
    practitioner: I want to benchmark my own model inside a real labeling loop, is Label Sleuth
      worth extending for that?
  answered_by:
  - extensibility
- ask:
    plain: what problems are still unsolved about letting non-experts build their own text
      classifiers?
    jargon: what open research questions does Label Sleuth identify around system policy,
      evaluation without a held-out test set, and zero-shot warm start?
    task: what should I work on if I want to research interactive classifier building for
      users with no machine learning background?
    practitioner: if I adopt a no-code classifier builder like Label Sleuth today, which parts
      are still open research rather than solved?
  answered_by:
  - open-research-agenda
  - precision-evaluation
- ask:
    plain: can a no-code labeling tool handle more than two categories, or tasks like tagging
      names in text?
    jargon: is Label Sleuth restricted to binary text classification, or does it support multi-class
      labeling and sequence tagging such as NER?
    task: how do I choose a labeling tool when my task is entity extraction or multi-class
      rather than a yes-no decision?
    practitioner: my task is multi-class annotation, is Label Sleuth the wrong tool for me?
  answered_by:
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
