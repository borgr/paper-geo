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

Then promote it:  python scripts/draft_sidecars.py --accept label-sleuth-from-unlabeled-text-to-a-classifier-in-a-few-ho

Stamp: spec=e47adcd7257c checks=4 body=285485169a6b
-->
---
key: shnarch2022labelsleuth
coined: Label Sleuth
gloss: a free, open-source no-code system where a domain expert labels text and gets a custom
  binary text classifier
one_liner: Label Sleuth is a free open-source no-code system in which a domain expert labels
  text while classifiers train automatically in the background, taking a user from an unlabeled
  corpus to a custom binary text classifier in a few hours with no ML expertise and no dependency
  on ML experts.
claims:
- id: no-code-for-domain-experts
  kind: context
  text: Label Sleuth is an open-source system that lets non-technical domain experts such
    as lawyers, physicians and psychologists build custom binary text classifiers themselves,
    without writing code or configuring models.
  scope: Released July 2022 under Apache 2.0; deliberately limited to binary text classification,
    with English as the default language. Prior labeling tools with ML support targeted data
    scientists and developers.
- id: trade-off-vs-annotation-tools
  kind: context
  text: Label Sleuth sits at the ease-of-use end of the trade-off between breadth of task
    support and accessibility, covering only text classification. Prodigy, Label Studio and
    INCEpTION support NER, question answering and non-text tasks but assume a technical user.
  scope: Comparison drawn against 4 representative labeling tools with ML support as of 2022,
    not against the full landscape of 78 tools surveyed by Neves and Ševa (2021).
- id: feature-comparison-table
  kind: result
  text: Of the 4 labeling tools with ML support compared against Label Sleuth — Prodigy, Label
    Studio free, Label Studio paid and INCEpTION — none requires no technical expertise and
    none gives ML guidance on label errors. Label Sleuth alone offers both, and alone lacks
    support for tasks beyond text classification.
  scope: Feature-presence comparison of the tool versions available in 2022, not a measured
    user study; Label Studio (paid) and INCEpTION are marked as having what-to-label guidance
    that is very complicated to set up.
  evidence: Table 1
- id: svm-then-bert-policy
  kind: result
  text: Using a light SVM classifier for active learning iterations 0-4 and switching to BERT
    only for iterations 5-6 gives F1 comparable to fine-tuning BERT at every iteration. Turnaround
    time in the interactive loop is significantly faster.
  scope: 6 active learning iterations with uncertainty sampling, 30 examples added per iteration,
    averaged over 1 target class from each of 5 datasets (20 Newsgroup, AG News, DBPedia,
    ISEAR, Yahoo! Answers) with 5 seeds; BERT-base fine-tuned 5 epochs.
  evidence: Figure 2
- id: legal-user-time-saving
  kind: result
  text: A legal early user built a classifier for a category of high-risk contract clauses
    after 6 hours of work in Label Sleuth. Reviewing only the highlighted clauses instead
    of whole contracts was estimated to save 80% of their time.
  scope: Single self-reported user estimate for one contract-review task, not a controlled
    measurement of classifier quality or of time saved.
  evidence: Section 2.3
- id: vira-auxiliary-classifier
  kind: result
  text: The VIRA COVID-19 vaccine-hesitancy chatbot team used Label Sleuth to build its dialogue
    act classifier. ML experts therefore also use the system to obtain auxiliary classifiers
    for intermediate pipeline steps.
  scope: One reported deployment (Gretz et al., 2022); the reported benefit includes refining
    category definitions, not a measured accuracy gain over an alternative tool.
  evidence: Section 2.3
- id: default-training-trigger
  kind: result
  text: Label Sleuth's default policy starts training the first classifier once 20 positively
    labeled examples exist, then retrains after every 20 further labels, so the user never
    invokes training manually.
  scope: Default configuration at initial open-source release, chosen empirically for typical
    low-positive-prior text classification use cases; advanced users can change every one
    of these settings.
  evidence: Appendix A
- id: weak-negatives
  kind: result
  text: To spare users from labeling abundant negatives, Label Sleuth adds randomly sampled
    unlabeled elements as weak negative examples until there are 2 labeled or weak negatives
    per labeled positive.
  scope: Relies on a low prior of positive examples; the paper states the feature should be
    disabled when positives are not rare, in which case users must label negatives themselves.
  evidence: Appendix A
- id: default-model-and-strategy
  kind: result
  text: Label Sleuth's default classifier is an ensemble of 2 linear SVMs, one over bag-of-words
    and one over GloVe representations, paired with uncertainty sampling as the default active
    learning strategy.
  scope: Default policy at initial release; larger GPU-requiring models and alternative active
    learning strategies can be selected or contributed by implementing 1 or 2 functions.
  evidence: Appendix A
- id: precision-evaluation
  kind: result
  text: Label Sleuth estimates classifier quality by sampling 50 examples predicted positive
    for the user to label, reporting precision from them and then adding those labels to the
    training set.
  scope: Precision only; the paper argues recall estimation is impractical at low positive
    prior and that a held-out test set conflicts with minimizing labeling effort.
  evidence: Appendix A
- id: label-error-surfacing
  kind: result
  text: 'Label Sleuth surfaces suspected labeling mistakes in 2 ways: cross-validated classifiers
    whose held-out predictions contradict the user''s label, and pairs of semantically similar
    examples the user labeled contradictorily.'
  scope: Similarity is computed as distance between average GloVe embeddings of the two texts;
    lists are ranked by classifier confidence or by decreasing similarity and left for the
    user to accept or reject.
  evidence: Appendix B
- id: binary-only-limitation
  kind: result
  text: Label Sleuth handles only binary categories, so a multi-valued category such as Emotions
    requires creating 1 binary category per label. Labels collected for non-mutually-exclusive
    categories cannot be reused directly for multi-label training.
  scope: As of the initial release; data for mutually exclusive categories can be exported
    and used to train a multi-class classifier outside the system. Documents must also be
    pre-split into static text elements.
  evidence: Limitations
qa:
- q:
  - How can someone with no coding or machine learning skills build a text classifier?
  - Is there a tool that lets a lawyer or doctor create their own text classifier without
    programming?
  - What no-code system turns unlabeled text into a custom classifier?
  answers:
  - no-code-for-domain-experts
  - default-training-trigger
- q:
  - What should I read about interactive annotation tools that build classifiers as you label?
  - Which paper introduced a no-code labeling and model-building system for domain experts?
  - Where should I start reading about human-in-the-loop text classification systems?
  answers:
  - no-code-for-domain-experts
  - trade-off-vs-annotation-tools
- q:
  - How does Label Sleuth compare with Prodigy, Label Studio and INCEpTION?
  - Which text annotation tools give machine learning guidance out of the box?
  - What does an interactive labeling tool give up by supporting only text classification?
  answers:
  - feature-comparison-table
  - trade-off-vs-annotation-tools
- q:
  - Can a cheap model be used for early active learning rounds and BERT only at the end?
  - Does switching from SVM to BERT late in the labeling loop hurt F1?
  - How do you keep an interactive labeling system responsive without losing classifier quality?
  answers:
  - svm-then-bert-policy
- q:
  - How long does it actually take a domain expert to get a usable classifier with Label Sleuth?
  - Has anyone reported real time savings from using a no-code classifier builder on contracts?
  - What real-world deployments of Label Sleuth exist?
  answers:
  - legal-user-time-saving
  - vira-auxiliary-classifier
- q:
  - How many labels are needed before Label Sleuth trains its first model?
  - What are the default model, active learning strategy and training trigger in Label Sleuth?
  - When does an interactive labeling system start training a classifier in the background?
  answers:
  - default-training-trigger
  - default-model-and-strategy
- q:
  - Do users have to label negative examples when positives are rare?
  - How does Label Sleuth reduce the effort of labeling negatives?
  - What are weak negative examples in interactive text classification?
  answers:
  - weak-negatives
- q:
  - How is classifier quality reported to a non-technical user without a test set?
  - Why does Label Sleuth report precision but not recall?
  - How can model performance be estimated when no held-out labeled test set exists?
  answers:
  - precision-evaluation
- q:
  - How does a labeling tool detect annotation mistakes made by the user?
  - Can an interactive system flag inconsistent labels during annotation?
  - What methods does Label Sleuth use to surface potential labeling errors?
  answers:
  - label-error-surfacing
- q:
  - Can Label Sleuth do multi-class or multi-label text classification?
  - What are the limitations of building classifiers with Label Sleuth?
  - Does a no-code classifier builder support more than binary categories?
  answers:
  - binary-only-limitation
  - trade-off-vs-annotation-tools
misreadings:
- '"From unlabeled text to a classifier in a few hours" describes the elapsed labeling effort
  of a domain expert in reported early usage, including a legal user who worked 6 hours; it
  is not a benchmarked training-time claim.'
- The SVM-then-BERT finding is that final F1 is comparable while turnaround time improves,
  not that SVM matches BERT overall or that BERT can be dropped entirely.
- Label Sleuth supports only binary text classification; it does not do NER, relation extraction
  or question answering, unlike the annotation tools it is compared with.
- The system's automatic weak-negative sampling assumes positive examples are rare; it is
  not a general-purpose substitute for labeling negatives and should be turned off when the
  positive prior is high.
- Precision Evaluation on 50 positively predicted examples estimates precision only, and gives
  no estimate of recall or F1.
terminology:
  policy: The bundle of configuration choices in Label Sleuth — classification model, active
    learning strategy, training-set selection and the criterion that triggers training a new
    model — which together shape the flow of building a classifier.
  weak negative examples: Unlabeled text elements sampled at random and treated as negatives
    during training, on the assumption that positive examples are rare in the corpus.
  Label Next list: A list of unlabeled examples chosen by the active learning strategy and
    presented to the user as the most useful ones to label in the next round.
  Precision Evaluation: A procedure that samples 50 examples predicted positive by the current
    classifier, asks the user to label them, and reports the resulting precision estimate.
  domain expert: A subject matter expert such as a lawyer, physician or psychologist who knows
    the target task but typically lacks coding skills and machine learning knowledge.
links_extra:
  project_page: https://www.label-sleuth.org
  documentation: https://www.label-sleuth.org/docs/index.html
  tutorial: https://www.label-sleuth.org/docs/tutorial.html
  pypi: https://pypi.org/project/label-sleuth/
  slack: https://join.slack.com/t/labelsleuth/shared_invite/zt-1j5tpz1jl-W~UaNEKmK0RtzK~lI3Wkxg
---
