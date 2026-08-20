---
one_liner: Manually aligning the content words of 1000 English-Arabic sentences in the Parallel
  Universal Dependencies corpus yields POS and dependency divergences for building translation
  challenge sets, but Google Translate scores higher on the extracted divergence sentences
  than on the corpus as a whole.
key: rafaeli2021pos
claims:
- id: negative-result-bleu
  kind: result
  text: Google Translate's mean sentence-level BLEU on English-Arabic sentences selected for
    POS/dependency divergences is about 0.70, below its 0.7495 mean over all 1000 Parallel
    Universal Dependencies sentences, so the divergence-based selection did not produce a
    harder-than-average challenge set.
  scope: English-to-Arabic Google Translate output scored with NLTK smoothed sentence_bleu
    against the corpus's professional Arabic translation as the single reference; 1000 PUD
    sentences from news and Wikipedia.
  evidence: Mid-level results, BLEU score table and the accompanying 0.7495161015312339 whole-corpus
    figure
- id: per-phenomenon-bleu
  kind: result
  text: The six divergence types tested give near-identical Google Translate BLEU means, from
    0.6938 for amod -> nmod (113 sentences) to 0.7036 for xcomp -> obl (74 sentences), with
    Verb -> Noun the largest set at 307 sentences.
  scope: One reference translation per sentence, BLEU-4 with uniform weights; sentence counts
    are subsets of the 1000-sentence PUD corpus and overlap where a sentence contains several
    divergences.
  evidence: Mid-level results, the phenomena/BLEU score mean/number of sentences table
- id: bleu-ngram-insensitive
  kind: result
  text: Recomputing the English-Arabic divergence-set BLEU scores with n = 3, 5 and 6 instead
    of the default BLEU-4 did not greatly alter the results under uniform weights.
  scope: Same 1000-sentence PUD material and single-reference smoothed NLTK sentence_bleu;
    no numeric table of the alternative-n scores is reported.
  evidence: Mid-level results, paragraph on default BLEU-4 and n=5, n=6, n=3
- id: divergences-selected
  kind: result
  text: Six English-to-Arabic divergences were selected as candidate challenge-set rules from
    the manual alignment — obl -> nmod, amod -> nmod, Aux -> verb, obj -> nmod, Verb -> Noun
    and xcomp -> obl — using a threshold of over 8% of English words with a tag taking the
    divergent Arabic tag and over 50 occurrences.
  scope: Thresholds applied to the POS percentage matrix and UD count matrix built from one
    annotator's content-word alignment of the English-Arabic PUD corpus; not validated against
    a second annotator.
  evidence: Table 1 (POS correlation matrix percentages) and Table 2 (UD correlation matrix
    counts), with the orange-cell criterion described under Table 1
- id: manual-alignment-coverage
  kind: result
  text: Manual content-word matching between English and Arabic covered all but 2 of the
    1000 Parallel Universal Dependencies sentences. Sentences 454 and 491 could not be fully
    tagged, because the Arabic rendering diverges in meaning from the English.
  scope: Single annotator at ILR R-1+ reading proficiency in Modern Standard Arabic, matching
    content words rather than translating; annotation reliability is not independently measured.
  evidence: Manual Tagging section, including the sentence 454 and sentence 491 examples
- id: aux-verb-lexical-pattern
  kind: result
  text: In the English-Arabic AUX -> VERB divergences, English inflections of "be" align with
    كان and its inflections, while English "can", "could" and "have" align with يمكن.
  scope: Word pairs aligned more than 3 times in the manually tagged PUD corpus; a lexical
    regularity in this corpus, not a claim about Arabic generally.
  evidence: Noteworthy divergent constructions, AUX -> VERB subsection
- id: arabic-only-phenomena-fail
  kind: result
  text: Four Arabic constructions with no fixed English parallel — passive participle, dual
    form, maf'ul mutlaq (cognate accusative) and verb-preposition distance — each yield a
    hand-made Arabic sentence that Google Translate renders wrongly, for example ‫ ظفرت الجائزة
    بتصفيق‬translated as "The award won applause" instead of "The award was received with
    applause".
  scope: Single hand-constructed example per phenomenon, Arabic-to-English direction, Google
    Translate at time of writing in 2021; no BLEU scores or automatic extraction for these
    cases.
  evidence: Other ideas section, Passive Particle, Dual form, Maf'ul mutlaq and Verb and preposition
    distance subsections
- id: ud-extraction-blockers
  kind: result
  text: 'Two Arabic phenomena resist automatic extraction from Universal Dependencies annotation:
    dual number is absent from the UD data examined, and maf''ul mutlaq needs word roots that
    the Arabic UD parser leaves unfilled on the advmod, with off-the-shelf Arabic root extractors
    reaching only around 75% accuracy.'
  scope: UD v2 annotation of the Arabic PUD treebank and publicly available Arabic root-extraction
    tools as of 2021; the 75% figure is quoted from those tools' reported accuracy, not measured
    in this work.
  evidence: Other ideas section, Dual form and Maf'ul mutlaq subsections
- id: tag-presence-check-flawed
  kind: result
  text: Checking whether a translated Arabic sentence contains the expected divergent tag
    is an unreliable substitute for BLEU, because the divergences occur well below 100% of
    the time and such a check would penalise correct translations that keep the English construction.
  scope: Argument grounded in the divergence rates of the POS and UD correlation matrices
    for English-Arabic; the alternative check was reasoned about, not implemented or measured.
  evidence: Mid-level results, the two numbered objections following the BLEU discussion
- id: contribution-rule-not-set
  kind: context
  text: The paper's aim is a reusable rule for automatically extracting English-Arabic challenge
    sets from a parallel treebank, rather than a fixed challenge set, so that others can generate
    their own diverse test sentences with little human labour.
  scope: As stated by the author for the English-Arabic pair in 2021; the reported experiment
    tested the rule and did not confirm that it isolates hard sentences.
  evidence: Summary section
- id: context-syntactic-divergence-challenge-sets
  kind: context
  text: The study is an undergraduate-level case study in building syntax-divergence challenge
    sets for machine translation, applying the challenge-set methodology of Choshen and Abend
    (2019) to the English-Arabic pair via manual annotation of the Parallel Universal Dependencies
    corpus.
  scope: One language pair, one 1000-sentence parallel corpus and one MT system (Google Translate)
    as of 2021; arXiv preprint, not peer-reviewed.
  evidence: Introduction and Syntactic pattern arise sections; Verb and preposition distance
    subsection citing Choshen and Abend (2019)
- id: context-reproduction-requirements
  kind: context
  text: Replicating this style of manual cross-lingual content-word alignment requires reading
    a newspaper or Wikipedia sentence in the target language without consulting a dictionary
    for more than half the words, plus formal grammatical study of both languages.
  scope: The author's own recommendation based on the English-Arabic annotation experience;
    a suggested minimum, not an empirically validated annotator qualification.
  evidence: Comments on the work process section
qa:
- q:
  - Does selecting sentences by English-Arabic syntactic divergence produce a hard machine
    translation challenge set?
  - Did the POS and dependency divergence method actually find sentences Google Translate
    struggles with?
  - What BLEU scores did Google Translate get on the English-Arabic divergence sentences?
  answers:
  - negative-result-bleu
  - per-phenomenon-bleu
- q:
  - Which English-to-Arabic syntactic divergences were identified as candidates for challenge
    sets?
  - What POS and dependency mismatches show up between English and Arabic in a parallel treebank?
  - Which dependency label changes were extracted from the English-Arabic PUD alignment?
  answers:
  - divergences-selected
  - aux-verb-lexical-pattern
- q:
  - How was the English-Arabic parallel corpus annotated for this divergence study?
  - How many PUD sentences were manually word-aligned between English and Arabic?
  - Who did the content-word matching and how reliable is it?
  answers:
  - manual-alignment-coverage
  - context-reproduction-requirements
- q:
  - Which Arabic grammatical constructions does Google Translate get wrong?
  - Are there Arabic-specific phenomena with no English parallel that break machine translation?
  - How does Google Translate handle Arabic dual forms and passive participles?
  answers:
  - arabic-only-phenomena-fail
- q:
  - Why is it hard to automatically extract Arabic dual forms or cognate accusatives from
    Universal Dependencies?
  - What limits automatic challenge-set extraction from Arabic UD treebanks?
  - Does UD annotation contain enough information for Arabic dual number and maf'ul mutlaq?
  answers:
  - ud-extraction-blockers
- q:
  - Can you evaluate a translation by checking whether the expected syntactic tag appears
    in the output?
  - Why was a tag-presence check rejected in favour of BLEU for English-Arabic evaluation?
  - Is checking for the divergent dependency label in the target sentence a good MT metric?
  answers:
  - tag-presence-check-flawed
- q:
  - Does the choice of n-gram order change the BLEU comparison in this English-Arabic study?
  - Was BLEU-4 versus BLEU-3, BLEU-5 or BLEU-6 consequential for the divergence sentences?
  answers:
  - bleu-ngram-insensitive
- q:
  - What should I read on building challenge sets for machine translation from syntactic divergences?
  - Where can I find work on English-Arabic machine translation evaluation using Universal
    Dependencies?
  - Which papers study cross-lingual syntactic divergence as a source of MT test sentences?
  answers:
  - context-syntactic-divergence-challenge-sets
  - contribution-rule-not-set
- q:
  - Was the goal to publish an English-Arabic challenge set or a method for making one?
  - What is the intended contribution of this English-Arabic syntax study?
  answers:
  - contribution-rule-not-set
misreadings:
- 'The study is a negative result: sentences containing the six selected English-Arabic divergences
  were not harder for Google Translate than average PUD sentences, so the extracted divergence
  rules should not be cited as a validated challenge-set recipe.'
- The reported BLEU differences between the six divergence types are tiny and were computed
  on overlapping subsets of a single 1000-sentence corpus; no divergence type is shown to
  be harder than another.
- The Arabic-specific phenomena (passive participle, dual, maf'ul mutlaq) are illustrated
  with individual hand-made sentences, not measured on a corpus, so they are hypotheses about
  Google Translate's weaknesses rather than quantified error rates.
- The POS and UD correlation matrices come from one non-native annotator's content-word alignment,
  so divergence percentages are estimates from a single annotation pass with no inter-annotator
  agreement reported.
terminology:
  Challenge set: A set of source-language sentences with gold target-language translations,
    chosen so that they are difficult enough that any competent machine translation engine
    must be able to translate them correctly.
  PUD (Parallel Universal Dependencies): A corpus of 1000 sentences parallel across languages,
    drawn from news and Wikipedia, with 750 originally English and the rest translated via
    English, annotated under Universal Dependencies v2 guidelines.
  Syntactic divergence: A case where a word's part-of-speech or dependency label in the source
    sentence maps to a different label in the professional translation, such as an English
    adjectival modifier (amod) rendered as an Arabic noun modifier (nmod).
  Maf'ul mutlaq (cognate accusative): An Arabic verbal noun placed after the verb, resembling
    it in form or meaning, used for emphasis or to state a type or number, as in ترتبط ارتباطاً
    وثيقاً ('is linked a strong link').
---
