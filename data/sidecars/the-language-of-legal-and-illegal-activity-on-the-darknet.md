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
    plain: which research studies how the language of illegal drug-selling websites differs
      from legal ones?
    jargon: which work gives a linguistic characterization of legal versus illegal Darknet
      text rather than just a classifier?
    task: where do I start reading if I want to do NLP on Tor hidden-service drug pages?
    practitioner: I need background before working on Darknet text analysis, what should I
      read first?
  answered_by:
  - context-first-linguistic-characterization
  - context-testbed
- ask:
    plain: can software tell a legal drug shop from an illegal one just from the words on
      the page?
    jargon: which features drive legal versus illegal classification of Onion drug pages,
      function words or content words?
    task: how do I build a text classifier that flags illegal drug listings on hidden services?
    practitioner: if I strip out drug names and slang, can I still separate legal from illegal
      onion drug pages?
  answered_by:
  - function-words
  - pos-syntax-signal
- ask:
    plain: do illegal drug websites write differently in grammar, or do they just use different
      words?
    jargon: is there a shallow syntactic signal, visible in POS-tag sequences, separating
      legal from illegal Onion drug text?
    task: how do I test whether legal/illegal separation survives replacing every content
      word with its part-of-speech tag?
    practitioner: can I rely on syntax and function words rather than a drug lexicon to detect
      illegal listings?
  answered_by:
  - pos-syntax-signal
  - function-words
- ask:
    plain: can Wikipedia be used to look up the product names found on Darknet drug sites?
    jargon: how do wikification rates on illegal Onion drug pages compare with legal Onion
      pages and clearnet marketplace listings?
    task: how do I do entity linking over Darknet drug text when the entity names are street
      slang?
    practitioner: will an off-the-shelf entity linker cover the drug names on illegal onion
      sites, or do I need my own knowledge base?
  answered_by:
  - wikification
  - kb-adaptation
- ask:
    plain: do modern neural text classifiers beat a simple word-counting classifier on Darknet
      drug pages?
    jargon: how do bag-of-embeddings, BiLSTM and ELMo self-attentive classifiers compare with
      Naive Bayes bag-of-words on Onion drug text?
    task: which classifier should I train to separate clearnet marketplace listings from legal
      onion drug pages?
    practitioner: is it worth using pre-trained embeddings and an LSTM for onion-site classification,
      or will Naive Bayes do better?
  answered_by:
  - neural-underperform
- ask:
    plain: are legal and illegal drug pages on hidden services really the same kind of writing?
    jargon: what is the Jensen-Shannon divergence between word distributions of legal Onion,
      illegal Onion and clearnet drug corpora?
    task: how do I decide whether to pool legal and illegal onion drug pages into one training
      domain or keep them separate?
    practitioner: can I train one model on all my onion drug data, or should I treat legal
      and illegal pages as separate domains?
  answered_by:
  - jsd-equilateral
  - distinct-domains
- ask:
    plain: does a detector trained on illegal drug shops still work on hidden-service discussion
      forums?
    jargon: does legal versus illegal classification of Onion drug pages transfer to Onion
      forums without in-domain training?
    task: how do I get an illegality classifier working on Darknet forums when I only have
      labelled drug-shop pages?
    practitioner: I have labelled onion drug listings but no labelled forum data, will a model
      trained on the listings transfer?
  answered_by:
  - cross-domain-generalization
  - forums-svm
- ask:
    plain: how accurately can forum posts on hidden services be sorted into legal and illegal?
    jargon: what accuracy does an RBF-kernel SVM reach on legal versus illegal Onion forum
      classification, and does it survive POS replacement?
    task: how do I classify noisy user-generated Tor forum text as legal or illegal?
    practitioner: my Darknet data is messy forum posts rather than clean product pages, what
      accuracy should I expect?
  answered_by:
  - forums-svm
- ask:
    plain: why do ordinary language tools struggle with the text on Darknet drug sites?
    jargon: which components of a standard NLP pipeline degrade on Onion drug text, and why
      do slang entities break knowledge-base coverage?
    task: what do I have to adapt before running an off-the-shelf NLP pipeline over hidden-service
      drug pages?
    practitioner: can I just point spaCy and a pre-trained model at my scraped onion drug
      corpus, or do I need to adapt them?
  answered_by:
  - kb-adaptation
  - neural-underperform
  - context-testbed
- ask:
    plain: how different is the writing on eBay listings from that on legal drug pages hosted
      on hidden services?
    jargon: how separable are clearnet marketplace product descriptions from legal Onion drug
      pages under a bag-of-words classifier?
    task: how do I check whether I can use eBay product descriptions as training data for
      legal onion drug pages?
    practitioner: can I substitute clearnet marketplace listings for legal onion drug pages
      when I lack Darknet training data?
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
