---
key: shnarch2020grasplite
coined: GrASP^lite
gloss: unsupervised discovery of human-readable text patterns by contrasting a new corpus
  against a background corpus
one_liner: GrASP^lite turns a supervised pattern-mining algorithm into an unsupervised one
  by contrasting the new corpus (foreground) with a background corpus — either general English
  news or an in-domain split — yielding human-readable rules that reveal a corpus's prominent
  categories with no labels and no list of categories.
claims:
- id: unsupervised-rules-beat-baselines
  kind: result
  text: GrASP^lite, given no labels and no list of categories, ranks first on 14 of the 26
    target categories evaluated across 10 datasets. The SIB clustering baseline ranks first
    on all 4 AG's news categories and 4 ISEAR categories, and no method beats the all-positive
    prior baseline on ISEAR disgust, Polarity or Essays premise.
  evidence: Section 4.3; Table 5
  scope: 10 English datasets and 26 categories; the GrASP^lite number per category is the
    best over an expert simulation that picks top-k rules by Information Gain on a 100–300-sentence
    annotated validation set.
- id: sms-spam-split
  kind: result
  text: On SMS spam, GrASP^lite with an in-domain split reaches 93% precision and 82 F1, against
    50 F1 for SIB, 30 for Naive Bayes and 23 for the all-positive prior baseline.
  evidence: Table 2 (SMS spam block)
  scope: SMS spam test set, 13% spam prior; the split uses SIB clustering, and the configuration
    was chosen on a 100-sentence validation set.
- id: wiki-attack-split-lifts-sib
  kind: result
  text: On Wiki attack, GrASP^lite with an in-domain split reaches 54% precision and 44 F1,
    more than doubling the 24% precision of the SIB clustering used to make the split. The
    general-English background version stays at the 21 F1 of the prior baseline.
  evidence: Table 2 (Wiki attack block)
  scope: Wiki attack test set, 12% attack prior; the general-English background is 50,000
    news sentences, stylistically unlike Wikipedia talk pages. Split favours precision over
    recall (38% vs 93% for the general-English version).
- id: background-choice-changes-rule-type
  kind: result
  text: A general-English background leads GrASP^lite to rules built on domain jargon words,
    such as the ToS rule matching "any" and the HOLJ rule matching "section" and "paragraph".
    An in-domain split instead yields rules relying on abstract syntax, WordNet generalizations
    and sentiment attributes.
  evidence: Section 5.2; Table 1 lines 10-15
  scope: Qualitative inspection of rules for the ToS and HOLJ legal corpora against a 50,000-sentence
    general-English news background; on HOLJ fact and framing the general-English background
    fails because those sentences are unusual within the corpus but not against general English.
- id: beats-domain-adaptation
  kind: result
  text: Both GrASP^lite variants outrank BlendNet on F1 for ASRD argument (56 and 55 vs 40)
    and Essays major claim (42 and 21 vs 17). BlendNet is a supervised domain-adaptation baseline
    trained on about 200K labeled news sentences.
  evidence: Table 2 (ASRD and Essays major claim blocks)
  scope: Two computational-argumentation datasets only; BlendNet predicts an argument if any
    argument type is detected, and GrASP^lite results are the best per category after the
    validation-set expert simulation.
- id: bert-still-better
  kind: result
  text: BERT fine-tuned on the same small validation set outperforms GrASP^lite on most datasets,
    reaching 97 F1 on SMS spam versus 82. On ToS unfair clause it fails entirely with 0 F1,
    after 9 trials without a meaningful classification.
  evidence: Table 5; Appendix D.1
  scope: BERT numbers are averages of 3 runs fine-tuned on the 100–300-sentence validation
    set, best model after 5 epochs; BERT is not interpretable and so does not serve the expert-assistance
    scenario.
- id: user-study-explainability
  kind: result
  text: Annotators preferred GrASP^lite rule explanations over Naive Bayes indicative-word
    explanations 53% of the time, abstained 29% of the time, and preferred Naive Bayes only
    18% of the time. The study used 20 SMS spam messages that both models classified correctly.
  evidence: Section 5.4; Table 4
  scope: 7 annotators, one outlier excluded; SMS spam only, and local explanations of individual
    predictions rather than judgments about which model predicts better.
- id: rules-recover-annotation-indicators
  kind: result
  text: GrASP^lite rules recover premise indicators listed in the Essays annotation guidelines,
    such as "for example" and "for instance", and generalize to unlisted ones such as "as
    a matter of fact". The rules come from a knowledgeable in-domain split taking first halves
    of sentences as foreground and second halves as background.
  evidence: Section 5.3; Table 1 lines 7-9
  scope: Essays corpus in the computational-argumentation domain; the sentence-halves heuristic
    assumes argumentative structure appears sentence-initially, and the comparison against
    the Stab and Gurevych guidelines is qualitative.
- id: categories-found-by-hand
  kind: result
  text: Reading only GrASP^lite rules and their matched sentences for the Terms-of-Service
    corpus, an author identified an unannotated class of categories, "customer side part in
    the agreement". It covers what the customer agrees to, may do and must do, while the dataset
    itself carries only a single "unfair clause" label.
  evidence: Section 5.1
  scope: One assignee, one dataset of Terms of Service legal documents, self-reported and
    subjective; no inter-annotator measurement of the discovered categories.
- id: tos-weak-on-rare-target
  kind: result
  text: On ToS unfair clause, GrASP^lite reaches only 32 F1 with a general-English background
    and 25 with an in-domain split, against a 20 F1 prior baseline. The paper attributes this
    to unfair clauses being a small category next to more prominent ones the rules capture.
  evidence: Table 2 (ToS block)
  scope: ToS test set, 11% unfair-clause prior; unsupervised rules describe whatever is prominent
    in the foreground, so a low-prior target category is not favoured.
- id: unsupervised-eda-for-nlp
  kind: context
  text: GrASP^lite frames the first encounter with an unlabeled corpus as exploratory data
    analysis for NLP. Instead of a classifier it delivers human-readable patterns an expert
    can read, edit and merge to discover what categories the corpus contains.
  scope: Positioned as of 2020 against domain adaptation and per-dataset characterisation
    work; the paper does not propose using the rule list directly as a classifier.
- id: cheap-language-agnostic
  kind: context
  text: GrASP^lite requires no labeled data, no list of target categories and no special hardware,
    running on a normal laptop. It is applicable to any language for which basic text-processing
    tools exist.
  scope: All reported experiments are on English corpora; attribute extraction as run uses
    an English POS tagger, NER, WordNet and an English sentiment lexicon, so a new language
    needs equivalents.
qa:
- ask:
    plain: where can I start reading about finding interpretable patterns in a text collection
      that has no labels yet?
    jargon: what work frames unsupervised pattern discovery over unlabeled corpora as exploratory
      data analysis for NLP?
    task: how do I explore an unlabeled text corpus and work out what categories to annotate
      before writing a codebook?
    practitioner: I have a raw corpus and no annotation scheme yet — is there a method that
      gives me readable patterns instead of a black-box classifier?
  answered_by:
  - unsupervised-eda-for-nlp
  - cheap-language-agnostic
- ask:
    plain: can readable text patterns learned without any labels pick out the categories in
      a corpus better than clustering it?
    jargon: how do unsupervised linguistic pattern rules compare with bag-of-words clustering
      and Naive Bayes on target-category detection across corpora?
    task: how do I get precision and F1 on a target category such as SMS spam without labeling
      any training data?
    practitioner: if I have no labels, should I cluster my documents or mine pattern rules
      to surface the category I care about?
  answered_by:
  - unsupervised-rules-beat-baselines
  - sms-spam-split
- ask:
    plain: when mining patterns from text, does it matter whether the comparison corpus is
      generic text or another part of the same collection?
    jargon: how does the choice of background corpus, general English versus an in-domain
      split, affect the type and quality of discovered contrastive rules?
    task: what should I use as the contrast set when I mine patterns from a domain corpus
      like Wikipedia comments or terms of service?
    practitioner: should I contrast my documents against generic news text or split my own
      corpus in two?
  answered_by:
  - background-choice-changes-rule-type
  - wiki-attack-split-lifts-sib
- ask:
    plain: do people find a matched pattern easier to understand than a list of telling keywords
      when a classifier explains itself?
    jargon: in a human preference study, are rule-based pattern explanations preferred to
      Naive Bayes indicative-word explanations?
    task: how do I tell whether pattern explanations are actually more useful to annotators
      than keyword explanations?
    practitioner: if I want explanations my annotators will accept, are patterns worth the
      trouble over highlighted words?
  answered_by:
  - user-study-explainability
- ask:
    plain: can patterns mined with no labels at all compete with a model trained on hundreds
      of thousands of labeled sentences from another domain?
    jargon: do unsupervised pattern rules outrank a supervised domain-adaptation baseline
      on F1 for argument component detection?
    task: how do I detect claims and premises in essays or student writing without labeled
      data in my own domain?
    practitioner: I cannot label argument spans in my corpus — is transferring a supervised
      argument-mining model better than mining rules from scratch?
  answered_by:
  - beats-domain-adaptation
- ask:
    plain: if only a hundred or so labeled sentences exist, is fine-tuning a pretrained language
      model still the better option than unsupervised rules?
    jargon: how does BERT fine-tuned on a small validation split compare with unsupervised
      pattern rules, and where does it collapse?
    task: how do I decide between fine-tuning BERT and mining rules when my labeled set is
      a few hundred sentences?
    practitioner: I have about 200 labeled sentences and a large unlabeled corpus — should
      I just fine-tune BERT?
  answered_by:
  - bert-still-better
- ask:
    plain: can patterns found automatically in essays turn up the same phrases that human
      annotation guidelines list as cues?
    jargon: do mined pattern rules recover the premise indicators specified in argumentative
      essay annotation guidelines, and do they extend beyond them?
    task: how do I check whether automatically discovered rules agree with the discourse cues
      my annotation manual already names?
    practitioner: could mined patterns help me write or extend the indicator list in my own
      annotation guidelines?
  answered_by:
  - rules-recover-annotation-indicators
- ask:
    plain: what happens when the category you are hunting for shows up in only a small slice
      of the documents, like unfair clauses in terms of service?
    jargon: how does unsupervised contrastive rule mining perform on a low-prior target category
      in a legal corpus against an all-positive prior baseline?
    task: how do I find a rare category such as unfair contract clauses in a corpus dominated
      by other content?
    practitioner: my target class is rare in the corpus — should I expect unsupervised pattern
      mining to find it?
  answered_by:
  - tos-weak-on-rare-target
- ask:
    plain: can someone reading automatically found patterns name a category that nobody had
      annotated in the corpus?
    jargon: has manual inspection of mined rules and their matched sentences yielded an unannotated
      category in a terms-of-service corpus?
    task: how do I discover categories my dataset's existing label scheme is missing?
    practitioner: if I skim the rules and the sentences they match, will I actually learn
      something new about my own corpus?
  answered_by:
  - categories-found-by-hand
- ask:
    plain: what hardware and resources does it take to mine interpretable patterns from an
      unlabeled corpus, and does it only work for English?
    jargon: what are the compute, labeled-data and linguistic-resource requirements of unsupervised
      contrastive rule mining, and is it language-agnostic?
    task: how do I run pattern discovery on a corpus in a language other than English on a
      laptop?
    practitioner: can I run this pattern-mining pipeline on my laptop for a non-English corpus?
  answered_by:
  - cheap-language-agnostic
misreadings:
- 'GrASP^lite is not proposed as a classifier: the reported precision, recall and F1 numbers
  measure whether a subset of its rules captures a non-trivial part of a category, and the
  paper explicitly does not advocate using the rule list directly to classify sentences.'
- 'The reported results are not fully label-free end to end: the best rule subset per category
  was chosen using Information Gain against labels on a 100–300-sentence validation set, a
  stand-in for a human expert filtering rules.'
- GrASP^lite does not dominate every baseline; SIB clustering ranks first on all 4 AG's news
  categories and 4 ISEAR categories, and on ISEAR disgust, Polarity and Essays premise no
  system improves over the all-positive prior baseline.
- The user study shows annotators found rule explanations easier to understand than indicative
  words on 20 spam messages; it does not show that GrASP^lite predicts spam better, since
  only examples both models classified correctly were shown.
- 'In-domain splitting is not universally better than a general-English background: the general-English
  version wins on ToS unfair clause (32 vs 25 F1) and Essays major claim (42 vs 21 F1).'
terminology:
  foreground corpus: The new, unexplored corpus of interest, used as the positive set of a
    pattern-mining algorithm on the assumption that the categories one wants to find are more
    prominent in it than in a contrasting background corpus.
  background corpus: A contrasting set of texts in which the categories of interest are expected
    to be significantly less prominent, used as the negative set; obtained either by sampling
    50,000 general-English news sentences or by splitting the domain corpus itself.
  in-domain split: Forming both foreground and background from the same domain corpus — by
    unsupervised clustering, or by a knowledgeable heuristic such as first sentence halves
    versus second halves — so that discovered patterns cannot be mere stylistic differences
    between two domains.
  knowledgeable in-domain split: An in-domain split driven by domain intuition rather than
    clustering; for argumentation, first halves of sentences form the foreground and second
    halves the background, on the hypothesis that argumentative structure appears sentence-initially.
  rule: A pattern of term-level linguistic attributes — surface form, POS tag, named entity,
    WordNet hypernym or super class, sentiment-lexicon membership — matched within a 5-term
    window, readable as a sentence such as "an ordinal number followed by a term relating
    to human communication".
  expert simulation: 'A surrogate for a human filtering rules: for each category, the top
    k ∈ {100, 50, 25, 10} rules by Information Gain on a small annotated validation set are
    kept, and a sentence is called positive when at least x ∈ {10, 5, 2, 1} of them match.'
  prior baseline: Labelling every instance positive, so recall is trivially 100% and precision
    equals the target category's share of the data; the F1 it yields is the bar an unsupervised
    method must clear.
---
