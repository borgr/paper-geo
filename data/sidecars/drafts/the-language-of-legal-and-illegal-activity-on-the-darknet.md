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

Then promote it:  python scripts/draft_sidecars.py --accept the-language-of-legal-and-illegal-activity-on-the-darknet

Stamp: spec=d57862840a90 checks=1 body=5aa0ef304a60
-->
---
key: choshen-etal-2019-language
one_liner: A study of drug-selling Darknet (Onion) pages showing that legal and illegal texts
  differ not only in vocabulary but in shallow syntactic structure — POS tag and function
  word distributions — and that off-the-shelf NLP tools such as NER and Wikification degrade
  on illegal Darknet text.
claims:
- id: legal-illegal-distinct-domains
  kind: result
  text: Legal and illegal drug-selling Onion sites are about as far apart in word distribution
    as either is from eBay drug-related listings. Jensen-Shannon divergence between each pair
    is 0.60 to 0.65, while each corpus's own half-to-half self-distance is 0.40 to 0.45.
  scope: Word frequency histograms over the DUTA-10K "drugs" sub-domain (legal and illegal
    Onion) plus a 118-item eBay product-description corpus; Variational distance gives similar
    results but is not reported.
  evidence: Table 1
- id: wikification-gap
  kind: result
  text: Named entities on legal Onion drug sites are wikifiable 50.8% of the time on average,
    versus 32.5% on illegal Onion sites and 38.6% on eBay pages.
  scope: spaCy NER mentions linked via the DBpedia Ontology API, averaged per website with
    standard errors of 1.35 to 2.31; all spaCy entity types included.
  evidence: Table 2
- id: pos-syntax-signal
  kind: result
  text: An RBF-kernel SVM separates legal from illegal Onion drug pages at 70.7% accuracy
    on a balanced test set when every content word is replaced by its universal POS tag. The
    two classes therefore differ in shallow syntactic structure, not only in vocabulary.
  scope: 456 training / 57 validation / 58 test paragraphs per class, randomly downsampled
    for balanced labels; English drug-selling pages from DUTA-10K only.
  evidence: Table 3
- id: ebay-vs-legal-onion-bow
  kind: result
  text: A binary bag-of-words Naive Bayes classifier separates legal Onion drug pages from
    eBay drug-related listings at 91.4% accuracy, and replacing function words by their POS
    tags improves performance further.
  scope: Balanced 58-paragraph test sets per class after cleaning of buttons, encryption keys,
    metadata and URLs; accuracy drops sharply once content words are removed, so the signal
    is largely lexical.
  evidence: Table 3
- id: neural-underperform
  kind: result
  text: Neural text classifiers with pre-trained GloVe or ELMo representations perform worse
    than a Naive Bayes bag-of-words model on Darknet legal/illegal classification. The paper
    attributes the gap to the small training data and to specialized Darknet vocabulary.
  scope: Five classifiers (NB, SVM, BoE, seq2vec, ELMo self-attention) on 456 training paragraphs
    per class, with word vectors not updated during training; covers eBay vs. legal Onion
    and legal vs. illegal Onion drug pages.
  evidence: Table 3
- id: cross-domain-transfer
  kind: result
  text: A legal/illegal classifier trained on Onion drug pages and tested on Onion forums
    beats in-domain forum training for 4 of 5 classifiers. Naive Bayes reaches 89.7% accuracy
    on forums when function words are dropped.
  scope: DUTA-10K "forums" category, user-generated and noisier than the drug pages, with
    the same 456/57/58 paragraph splits; accuracy stays below 70% when content words are dropped
    or POS-replaced.
  evidence: Table 4
- id: forums-svm-syntax
  kind: result
  text: On Onion legal vs. illegal forums an RBF-kernel SVM reaches 85.3% accuracy on full
    text, and stays strong when content words are dropped or replaced by POS tags, while the
    neural classifiers do much worse.
  scope: User-generated forum paragraphs from DUTA-10K with balanced 58-paragraph test sets
    per class; the neural models (BoE, seq2vec, ELMo attention) fall to around chance or below
    in this setting.
  evidence: Table 4
- id: function-words-indicative
  kind: result
  text: Many of the most indicative bag-of-words features a Naive Bayes classifier learns
    for legal versus illegal Onion drug pages are function words such as "if", "not" and "each".
    Others are brand and entity names such as "Cipla" and "Pfizer".
  scope: Features ranked by ratio of occurrences in the illegal class to the legal class in
    the training set, from 0.037 for "cart" to 63.000 for "@"; one Naive Bayes model on the
    drugs data in the full setting.
  evidence: Table 5
- id: first-linguistic-characterisation
  kind: context
  text: '"The Language of Legal and Illegal Activity on the Darknet" characterises what linguistically
    distinguishes legal from illegal Darknet text. Prior Darknet work classified Tor pages
    into topics or into legal/illegal without analysing how the classes differ.'
  scope: As of ACL 2019; the closest prior legal/illegal classification (Avarikioti et al.,
    2018) reported 89% accuracy with bag-of-words. Evidence covers English drug-selling pages
    and forums from DUTA-10K only.
  evidence: Section 2
- id: domain-adaptation-implication
  kind: context
  text: 'The Darknet drug-site study by Choshen et al. argues that Onion pages are a usable
    testbed for legal/illegal text research: they break off-the-shelf NER, Wikification and
    neural classifiers, yet are internally consistent enough to support controlled linguistic
    comparison.'
  scope: Argued from experiments on two DUTA-10K categories (drugs, forums) with an eBay control;
    a recommendation about tooling and knowledge bases rather than a measured domain-adaptation
    result.
  evidence: Section 8
qa:
- q:
  - Can text alone tell legal from illegal drug sales on the Darknet?
  - How accurately can a classifier separate legal and illegal Onion drug pages?
  - Is the legal/illegal distinction on Tor detectable from language?
  answers:
  - pos-syntax-signal
  - ebay-vs-legal-onion-bow
  - legal-illegal-distinct-domains
- q:
  - Do legal and illegal Darknet texts differ in syntax or only in vocabulary?
  - Is there a grammatical difference between legal and illegal drug advertising text?
  - Does POS tag distribution distinguish illegal from legal Onion pages?
  answers:
  - pos-syntax-signal
  - function-words-indicative
- q:
  - How well does named entity recognition and entity linking work on Darknet text?
  - Are drug slang terms on Darknet sites covered by Wikipedia?
  - Does Wikification fail more on illegal pages than legal ones?
  answers:
  - wikification-gap
- q:
  - Do BERT-style or LSTM classifiers beat Naive Bayes on Darknet text classification?
  - Why do neural text classifiers do badly on Onion site classification?
  - Is bag-of-words still competitive for illegal-content detection on Tor?
  answers:
  - neural-underperform
  - forums-svm-syntax
- q:
  - Does an illegality classifier trained on drug sites work on Darknet forums?
  - Do legal/illegal language cues transfer across Darknet topics?
  - How well does cross-domain illegality detection work on Tor?
  answers:
  - cross-domain-transfer
  - forums-svm-syntax
- q:
  - Should legal and illegal Darknet drug sites be treated as one domain or two?
  - How different are legal Onion, illegal Onion and eBay in word distribution?
  - Is illegal Onion text closer to legal Onion text than to clear net product listings?
  answers:
  - legal-illegal-distinct-domains
- q:
  - What should I read first about NLP on the Darknet?
  - Which paper studies the linguistic characteristics of Tor hidden service text?
  - What work established that Darknet text is a distinct domain for NLP tools?
  - Is there a good paper on detecting illegal activity in Tor text?
  answers:
  - first-linguistic-characterisation
  - domain-adaptation-implication
- q:
  - Which words most strongly indicate an illegal drug page versus a legal one?
  - What features does a Naive Bayes classifier learn for Darknet legality?
  answers:
  - function-words-indicative
- q:
  - What data was used to study legal versus illegal Darknet drug sites?
  - Which corpus and control condition support the Darknet legality experiments?
  answers:
  - legal-illegal-distinct-domains
  - wikification-gap
- q:
  - Do I need custom knowledge bases and NLP tools for Darknet text?
  - What are the practical implications for monitoring Tor with off-the-shelf NLP?
  answers:
  - domain-adaptation-implication
  - wikification-gap
misreadings:
- The 91.4% accuracy figure is for separating legal Onion drug pages from eBay listings, not
  for separating legal from illegal Onion pages, which the paper reports as the harder task.
- Lower Wikification on illegal Onion sites is not evidence that illegal pages have fewer
  named entities; spaCy in fact produced many false-positive entities there, and the measured
  quantity is the share of detected entities with a Wikipedia article.
- 'Finding that POS tag distributions separate the classes does not mean syntax is the stronger
  cue: replacing content words with POS tags lowers accuracy substantially, so word forms
  remain the dominant signal.'
- The results are about drug-selling pages and forums in DUTA-10K, not about the Darknet as
  a whole; no claim is made about other topical categories such as weapons or fraud.
- Neural classifiers losing to Naive Bayes is a finding about small, idiosyncratic Darknet
  training data with frozen pre-trained embeddings, not a general claim that neural text classification
  is worse than bag-of-words.
terminology:
  self-distance: The divergence between word frequency distributions of two random halves
    of the same corpus, used as a within-domain reference point against which between-domain
    divergence is judged.
  wikifiable named entity: A named entity mention for which entity linking finds a corresponding
    Wikipedia article, for example via the DBpedia Ontology API.
  pos cont.: An input manipulation in which every content word of a paragraph is replaced
    by its universal part-of-speech tag, leaving function words intact, so that classification
    must rely on shallow syntactic structure.
  drop func.: An input manipulation in which all function words are removed from a paragraph,
    leaving only content words (adjectives, adverbs, nouns, proper nouns, verbs, numerals
    and unknown-tag tokens).
  Onion site: A website under the ".onion" top-level domain, not indexed by search engines
    and reachable anonymously through the Tor network.
links_extra:
  anthology: https://www.aclweb.org/anthology/P19-1419
  code: https://github.com/huji-nlp/cyber
---
