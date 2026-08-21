---
one_liner: A linguistic study of drug-selling Darknet (.onion) pages showing that legal and
  illegal texts differ not only in their words but in POS-tag and function-word distributions,
  and that Wikification and neural classifiers work worse on illegal text than simple bag-of-words.
key: choshen-etal-2019-language
claims:
- id: context-first-linguistic-characterization
  kind: context
  text: Choshen et al.'s ACL 2019 study of legal versus illegal Darknet text characterizes
    what linguistically distinguishes the two classes. Earlier work built classifiers that
    separate them without analyzing the difference.
  scope: As of 2019; the closest prior work (Avarikioti et al., 2018) reported accuracy only.
    English drugs and forums categories of DUTA-10K, plus an eBay control.
- id: context-testbed
  kind: context
  text: Onion drug pages are argued to be an attractive testbed for studying legal/illegal
    text distinctions, because they break off-the-shelf NLP tools while remaining internally
    consistent enough to support linguistic analysis.
  scope: Argued from experiments on the DUTA-10K drugs and forums sub-domains with an eBay
    control condition of drug-related product descriptions.
- id: jsd-equilateral
  kind: result
  text: By Jensen-Shannon divergence over word distributions, eBay, Legal Onion and Illegal
    Onion drug texts each have a self-distance of 0.40 to 0.45 between random halves. The
    distance between each pair of corpora is 0.60 to 0.65, approximately an equilateral triangle.
  scope: Word-frequency histograms over the DUTA-10K drugs sub-domain and a 118-description
    eBay corpus, after removing markup, buttons, keys, URLs and duplicate paragraphs; Variational
    distance gives similar results but is not reported.
  evidence: Table 1
- id: distinct-domains
  kind: result
  text: Legal and illegal Onion drug texts are as far apart in vocabulary from each other
    as either is from eBay drug-related product descriptions. They are therefore better treated
    as distinct domains than as sub-domains of one Darknet drug domain.
  scope: Vocabulary-distribution evidence only (Jensen-Shannon divergence and Variational
    distance), on drug-related pages from DUTA-10K versus an eBay control corpus.
  evidence: Table 1
- id: wikification
  kind: result
  text: Named entities on legal Onion drug sites are wikifiable 50.8% of the time (standard
    error 2.31), versus only 32.5% (1.35) on illegal Onion sites and 38.6% (2.00) on eBay
    pages.
  scope: spaCy named entity recognition plus DBpedia Ontology API lookup, averaged per site
    within each domain, on drug-related pages.
  evidence: Table 2
- id: kb-adaptation
  kind: result
  text: Wikipedia and standard NER tools cover illegal Darknet drug text poorly, because its
    named entities are largely slang terms for illicit drugs and paraphernalia. Specialized
    knowledge bases and adapted tools are therefore needed for such text.
  scope: Based on Wikification rates and manual inspection of spaCy output for drug-related
    Onion and eBay pages; the diagnosis of why coverage is low is qualitative, and spaCy also
    produced false-positive entities such as "kush" and "GBL".
  evidence: Section 4.2
- id: nb-ebay-vs-legal
  kind: result
  text: A Naive Bayes bag-of-words classifier separates eBay pages from legal Onion drug pages
    at 91.4% test accuracy, and replacing function words by their POS tags improves performance
    further.
  scope: Balanced paragraph-level splits of 456 train / 57 validation / 58 test paragraphs
    per class, with larger categories randomly downsampled; BernoulliNB with alpha=1.
  evidence: Table 3
- id: pos-syntax-signal
  kind: result
  text: Legal and illegal Onion drug pages remain distinguishable at 70.7% accuracy by an
    RBF-kernel SVM when every content word is replaced by its universal POS tag. The two classes
    therefore differ in shallow syntactic structure, not only in vocabulary.
  scope: Balanced 58-paragraph test set per class from the DUTA-10K drugs sub-domain; POS
    tags from spaCy; accuracy on this pair is lower than on the eBay versus Legal Onion control
    pair.
  evidence: Table 3
- id: function-words
  kind: result
  text: Many of the most indicative Naive Bayes features for legal versus illegal Onion drug
    pages are function words rather than entities, indicating that the two classes differ
    in their function-word distribution. Indicative legal features include "if", "not" and
    "very".
  scope: Naive Bayes with binary bag-of-words features on balanced paragraph splits from the
    DUTA-10K drugs sub-domain; content words defined as spaCy ADJ, ADV, NOUN, PROPN, VERB,
    X and NUM.
  evidence: Table 5
- id: neural-underperform
  kind: result
  text: Pre-trained neural classifiers, including a bag-of-embeddings model, a BiLSTM and
    an ELMo self-attentive network, all score below the 91.4% that Naive Bayes bag-of-words
    reaches on eBay versus legal Onion drug pages.
  scope: Small training sets of 456 paragraphs per class; 100-dimensional GloVe embeddings
    held fixed, and ELMo contextualized representations. Neural models are also weakest on
    forums data.
  evidence: Table 3
- id: cross-domain-generalization
  kind: result
  text: A classifier trained on Onion legal versus illegal drug pages transfers directly to
    Onion legal versus illegal forums, with Naive Bayes reaching 89.7% accuracy when function
    words are dropped. Transfer beats in-domain forums training for 4 of 5 classifiers.
  scope: DUTA-10K forums sub-domain, user-generated and noisier than the drugs pages, with
    the same 456/57/58 paragraph splits. Accuracy falls below 70% when content words are dropped
    or replaced by POS tags, so part of the transferable signal is lexical.
  evidence: Table 4
- id: forums-svm
  kind: result
  text: An RBF-kernel SVM trained and tested on Onion legal versus illegal forums reaches
    85.3% accuracy in the full setting. It stays strong when content words are dropped or
    replaced by POS tags, while the neural classifiers perform far worse on this noisy data.
  scope: DUTA-10K forums sub-domain with balanced paragraph splits of 456 train / 57 validation
    / 58 test paragraphs per class; forums text is user-generated and varied.
  evidence: Table 4
qa:
- ask:
    practitioner: What research should I read on how language differs between legal and illegal
      activity online?
    unsorted:
    - Is there a paper analysing the linguistic characteristics of Darknet text?
    - Where should I start reading about NLP on Tor / .onion sites?
  answered_by:
  - context-first-linguistic-characterization
  - context-testbed
- ask:
    unsorted:
    - Can legal and illegal drug-selling websites be told apart automatically from their text?
    - How accurately can a classifier separate legal from illegal Darknet drug pages?
    - What accuracy do bag-of-words classifiers get on legal vs illegal onion drug sites?
  answered_by:
  - function-words
  - pos-syntax-signal
- ask:
    unsorted:
    - Do legal and illegal Darknet texts differ in syntax, or only in vocabulary?
    - Is part-of-speech distribution a useful signal for detecting illegal web content?
    - Can illegal text be identified after removing all content words?
  answered_by:
  - pos-syntax-signal
  - function-words
- ask:
    unsorted:
    - How well does entity linking to Wikipedia work on Darknet text?
    - Are named entities on illegal drug sites covered by Wikipedia?
    - Does Wikification work worse on illegal onion sites than legal ones?
  answered_by:
  - wikification
  - kb-adaptation
- ask:
    unsorted:
    - Do deep learning text classifiers beat Naive Bayes on Darknet pages?
    - Why do neural models with pre-trained embeddings do badly on onion site text?
    - Are ELMo and LSTM classifiers better than bag-of-words for illegal content detection?
  answered_by:
  - neural-underperform
- ask:
    unsorted:
    - Should legal and illegal Darknet drug pages be treated as one domain or two?
    - How far apart are legal and illegal onion drug texts in word distribution?
    - Are illegal onion pages closer to legal onion pages or to eBay listings?
  answered_by:
  - jsd-equilateral
  - distinct-domains
- ask:
    unsorted:
    - Does an illegality classifier trained on drug sites work on Darknet forums?
    - How well does legal/illegal text classification transfer across Darknet topics?
    - Is there a shared signal for illegal content across different Tor categories?
  answered_by:
  - cross-domain-generalization
  - forums-svm
- ask:
    unsorted:
    - How well can legal and illegal Tor forum posts be classified?
    - What accuracy is achievable on user-generated illegal Darknet forum text?
  answered_by:
  - forums-svm
- ask:
    unsorted:
    - Do off-the-shelf NLP tools need adaptation for Darknet text?
    - What do Darknet drug pages break in standard NLP pipelines?
  answered_by:
  - kb-adaptation
  - neural-underperform
  - context-testbed
- ask:
    unsorted:
    - How different is a clear net marketplace like eBay from a legal Darknet drug shop?
    - Can eBay product descriptions be separated from legal onion drug pages?
  answered_by:
  - nb-ebay-vs-legal
  - distinct-domains
terminology:
  self-distance: The Jensen-Shannon divergence (or Variational distance) between word-frequency
    distributions of two random halves of the same corpus, used as a within-corpus reference
    point against which between-corpus distances are judged.
  wikifiable named entity: A named entity mention that can be linked to a corresponding Wikipedia
    article, for example via the DBpedia Ontology API.
  pos cont.: An input manipulation in which every content word of a document is replaced by
    its universal part-of-speech tag, leaving function words intact, so that classification
    must rely on shallow syntactic structure.
  drop func.: An input manipulation in which all function words are deleted from a document,
    leaving only content words (spaCy ADJ, ADV, NOUN, PROPN, VERB, X, NUM).
  Legal Onion / Illegal Onion: The legal and illegal sub-categories of a DUTA-10K topical
    category (drugs or forums) of Tor hidden-service pages, used as the two classes to be
    distinguished.
  control condition: A corpus of 118 eBay product descriptions retrieved with drug-related
    search terms, legal and on the clear net, used for comparison against Darknet drug pages.
misreadings:
- 'Measuring that legal and illegal Darknet texts are distinguishable is not a deployable
  illegality detector: accuracies are reported on artificially balanced 58-paragraph test
  sets per class, not on the natural distribution of Tor content.'
- 'The low Wikification rate on illegal Onion sites is not a Darknet effect alone: eBay drug-related
  pages are also low (38.6%), while legal Onion pharmaceutical sites are the outlier at 50.8%.'
- The finding that neural classifiers lose to Naive Bayes is not evidence that neural models
  are unsuited to Darknet text in principle; training sets were only 456 paragraphs per class
  and the pre-trained embeddings cover this vocabulary poorly.
- '"Illegal" and "legal" labels are inherited from the DUTA-10K corpus''s existing sub-categories,
  not from a new legal judgment made by the study''s authors.'
- 'Transfer from drug pages to forums does not mean the transferable signal is purely syntactic:
  cross-domain accuracy falls below 70% when content words are removed, versus 89.7% when
  function words are.'
links_extra:
  acl_anthology: https://www.aclweb.org/anthology/P19-1419
  pdf: https://www.aclweb.org/anthology/P19-1419.pdf
  code: https://github.com/huji-nlp/cyber
---
