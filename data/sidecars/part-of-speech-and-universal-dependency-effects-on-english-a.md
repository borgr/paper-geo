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
    Universal Dependencies sentences. The divergence-based selection did not produce a harder-than-average
    challenge set.
  scope: English-to-Arabic Google Translate output scored with NLTK smoothed sentence_bleu
    against the corpus's professional Arabic translation as the single reference; 1000 PUD
    sentences from news and Wikipedia.
  evidence: Mid-level results, BLEU score table and the accompanying 0.7495161015312339 whole-corpus
    figure
- id: per-phenomenon-bleu
  kind: result
  text: The six divergence types tested give near-identical Google Translate BLEU means, from
    0.6938 for amod -> nmod (113 sentences) to 0.7036 for xcomp -> obl (74 sentences). Verb
    -> Noun is the largest set, at 307 sentences.
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
  text: 'Six English-to-Arabic divergences were selected as candidate challenge-set rules
    from the manual alignment: obl -> nmod, amod -> nmod, Aux -> verb, obj -> nmod, Verb ->
    Noun and xcomp -> obl. The threshold was over 8% of English words with a given tag taking
    the divergent Arabic tag, and over 50 occurrences.'
  scope: Thresholds applied to the POS percentage matrix and UD count matrix built from one
    annotator's content-word alignment of the English-Arabic PUD corpus; not validated against
    a second annotator.
  evidence: Table 1 (POS correlation matrix percentages) and Table 2 (UD correlation matrix
    counts), with the orange-cell criterion described under Table 1
- id: manual-alignment-coverage
  kind: result
  text: Manual content-word matching between English and Arabic covered all but 2 of the 1000
    Parallel Universal Dependencies sentences. Sentences 454 and 491 could not be fully tagged,
    because the Arabic rendering diverges in meaning from the English.
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
  text: Four Arabic constructions with no fixed English parallel, namely passive participle,
    dual form, maf'ul mutlaq and verb-preposition distance, each yield a hand-made Arabic
    sentence that Google Translate renders wrongly. One such example, ظفرت الجائزة بتصفيق,
    comes back as "The award won applause" instead of "The award was received with applause".
  scope: Single hand-constructed example per phenomenon, Arabic-to-English direction, Google
    Translate at time of writing in 2021; no BLEU scores or automatic extraction for these
    cases.
  evidence: Other ideas section, Passive Particle, Dual form, Maf'ul mutlaq and Verb and preposition
    distance subsections
- id: ud-extraction-blockers
  kind: result
  text: 'Two Arabic phenomena resist automatic extraction from Universal Dependencies: dual
    number is absent from the UD data, and maf''ul mutlaq needs word roots the Arabic UD parser
    leaves unfilled on the advmod. Off-the-shelf Arabic root extractors reach only around
    75% accuracy.'
  scope: UD v2 annotation of the Arabic PUD treebank and publicly available Arabic root-extraction
    tools as of 2021; the 75% figure is quoted from those tools' reported accuracy, not measured
    in this work.
  evidence: Other ideas section, Dual form and Maf'ul mutlaq subsections
- id: tag-presence-check-flawed
  kind: result
  text: Checking whether a translated Arabic sentence contains the expected divergent tag
    is an unreliable substitute for BLEU. The divergences occur well below 100% of the time,
    so such a check would penalise correct translations that keep the English construction.
  scope: Argument grounded in the divergence rates of the POS and UD correlation matrices
    for English-Arabic; the alternative check was reasoned about, not implemented or measured.
  evidence: Mid-level results, the two numbered objections following the BLEU discussion
- id: contribution-rule-not-set
  kind: context
  text: A reusable rule for automatically extracting English-Arabic challenge sets from a
    parallel treebank is the target, rather than a fixed challenge set. Others could then
    generate their own diverse test sentences with little human labour.
  scope: As stated by the author for the English-Arabic pair in 2021; the reported experiment
    tested the rule and did not confirm that it isolates hard sentences.
  evidence: Summary section
- id: context-syntactic-divergence-challenge-sets
  kind: context
  text: The work is an undergraduate-level case study in building syntax-divergence challenge
    sets for machine translation. It applies the challenge-set methodology of Choshen and
    Abend (2019) to English-Arabic, via manual annotation of the Parallel Universal Dependencies
    corpus.
  scope: One language pair, one 1000-sentence parallel corpus and one MT system (Google Translate)
    as of 2021; arXiv preprint, not peer-reviewed.
  evidence: Introduction and Syntactic pattern arise sections; Verb and preposition distance
    subsection citing Choshen and Abend (2019)
- id: context-reproduction-requirements
  kind: context
  text: Replicating this style of manual cross-lingual content-word alignment requires reading
    a newspaper or Wikipedia sentence in the target language without a dictionary for more
    than half the words. Formal grammatical study of both languages is also needed.
  scope: The author's own recommendation based on the English-Arabic annotation experience;
    a suggested minimum, not an empirically validated annotator qualification.
  evidence: Comments on the work process section
qa:
- ask:
    plain: if you pick sentences where English and Arabic grammar disagree, does a translation
      system actually do worse on them?
    jargon: do POS and dependency-label divergences between English and Arabic select sentences
      with lower Google Translate BLEU than a random treebank sample?
    task: how do I tell whether a divergence-based test set is genuinely harder than the corpus
      it was drawn from?
    practitioner: should I build my English-Arabic MT test set by filtering for syntactic
      divergences, or will the scores come out the same?
  answered_by:
  - negative-result-bleu
  - per-phenomenon-bleu
- ask:
    plain: which bits of grammar change shape when English sentences are translated into Arabic?
    jargon: which English-to-Arabic dependency and POS divergences pass a frequency threshold
      in the Parallel Universal Dependencies treebank?
    task: how do I find recurring grammatical mismatches between English and Arabic to write
      test-set extraction rules from?
    practitioner: which English-Arabic construction mismatches are frequent enough to be worth
      targeting in my evaluation set?
  answered_by:
  - divergences-selected
  - aux-verb-lexical-pattern
- ask:
    plain: how were the English and Arabic versions of the same sentences matched up word
      by word, and did any sentences defeat it?
    jargon: how complete was the manual content-word alignment over the 1000-sentence English-Arabic
      PUD corpus, and what background does the annotation demand?
    task: how do I hand-align an English-Arabic parallel treebank at the content-word level,
      and what language skill does it take?
    practitioner: do I need to be fluent in Arabic to redo this kind of cross-lingual word
      alignment myself?
  answered_by:
  - manual-alignment-coverage
  - context-reproduction-requirements
- ask:
    plain: are there Arabic grammatical forms that machine translation into English simply
      gets wrong because English has no equivalent?
    jargon: do Arabic-specific constructions such as the passive participle, dual number and
      maf'ul mutlaq fail under Google Translate with no English structural parallel?
    task: how do I probe an Arabic-English translation system on constructions that English
      cannot express directly?
    practitioner: can I expect Google Translate to handle Arabic dual forms and cognate accusatives
      in my documents?
  answered_by:
  - arabic-only-phenomena-fail
- ask:
    plain: why can't Arabic dual forms and cognate accusatives be pulled out of a treebank
      automatically?
    jargon: what annotation gaps in the Arabic UD treebank block automatic extraction of dual
      number and maf'ul mutlaq, and how accurate are Arabic root extractors?
    task: how do I automate extraction of Arabic dual number or maf'ul mutlaq examples from
      Universal Dependencies annotation?
    practitioner: can I rely on Arabic Universal Dependencies annotation to mine these constructions,
      or do I need manual work?
  answered_by:
  - ud-extraction-blockers
- ask:
    plain: can you score a translation just by checking whether the expected grammatical form
      turned up in the output?
    jargon: is a target-side divergent-tag presence check a sound substitute for BLEU when
      scoring English-Arabic challenge sentences?
    task: how should I score an English-Arabic challenge set, by looking for the divergent
      dependency label or by an n-gram metric?
    practitioner: if I check my Arabic output for the expected divergent tag instead of computing
      BLEU, what goes wrong?
  answered_by:
  - tag-presence-check-flawed
- ask:
    plain: would using shorter or longer word sequences to score the translations change the
      comparison?
    jargon: are the English-Arabic divergence-set BLEU results sensitive to n-gram order,
      comparing BLEU-3, BLEU-5 and BLEU-6 against BLEU-4 under uniform weights?
    task: how do I check whether my BLEU comparison of English-Arabic divergence sentences
      survives a change of n-gram order?
    practitioner: do I need to report several n-gram orders when scoring Arabic translations,
      or is BLEU-4 enough?
  answered_by:
  - bleu-ngram-insensitive
- ask:
    plain: what should I read about using grammar differences between two languages to build
      translation test sentences?
    jargon: which work applies syntactic-divergence challenge-set methodology to English-Arabic
      machine translation using Universal Dependencies?
    task: where do I start if I want to build syntax-divergence challenge sets for a new language
      pair such as English-Arabic?
  answered_by:
  - context-syntactic-divergence-challenge-sets
  - contribution-rule-not-set
- ask:
    plain: was the aim to hand out a finished set of tricky English-Arabic sentences, or a
      recipe other people can run?
    jargon: is the English-Arabic contribution a fixed challenge set or a reusable extraction
      rule over a parallel treebank?
    practitioner: if I work on a different language pair, do I get a ready-made English-Arabic
      test set out of this or a procedure I can adapt?
  answered_by:
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
