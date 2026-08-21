---
key: choshen2020serclclassifying
coined: SErCl
gloss: syntactic error classification from Universal Dependencies parses of a learner sentence
  and its correction
one_liner: SErCl classifies a grammatical error by the pair of Universal Dependencies labels
  — POS tags, dependency edge labels or morphological features — that change between the learner's
  span and its correction, giving an error taxonomy that needs no hand-written categories
  and transfers across languages.
claims:
- id: complements-errant
  kind: result
  text: About 60% of the English learner errors that ERRANT dumps into its residual OTHER
    category receive a POS-based syntactic-error class from SErCl. Of 842 OTHER edits in W&I,
    504 (59.9%) change the POS tag between source and correction.
  scope: W&I learner English, using ERRANT's own edit spans and UDPipe parses; ERRANT sends
    about 25% of its predictions to OTHER in NUCLE and Lang8 and about 15% in W&I and TLE.
  evidence: Section 3.3
- id: auto-parse-reliable
  kind: result
  text: Replacing manual dependency annotation with a UDPipe parser barely changes the distribution
    of syntactic error types in the TLE learner corpus. Normalising by tokens per POS, class
    frequencies shift 0.4% on average, with Pearson r=0.998.
  scope: TLE learner English, the only corpus with manual UD; UDPipe parses; non-lexical tags
    X, INTJ and SYM are excluded because the parser inflates them.
  evidence: Section 3.1
- id: maps-to-nucle
  kind: result
  text: SErCl types sit largely inside single categories of NUCLE's hand-built taxonomy. On
    average 62% of a given syntactic-error type's instances fall in its maximally overlapping
    NUCLE category, and 82% in one of the top three.
  scope: NUCLE training set, relocation errors excluded because edits do not distinguish relocation
    from deletion; SErCl types with fewer than 30 occurrences omitted from the comparison
    matrix.
  evidence: Table 24 and Section 3.2
- id: ses-harder
  kind: result
  text: Syntactic errors are harder for grammatical error correction systems than other errors.
    The BEA2019 winner UEDIN-MS changes only 2686 of 4790 gold syntactic errors, a 56% recall
    upper bound, against its reported overall recall of 60%.
  scope: W&I development set, BEA2019 system outputs; the bound counts any change of the right
    type, correct or not; the ~40% SE recall estimate assumes SE precision equals the reported
    overall 72%.
  evidence: Table 6 and Section 5.1
- id: recall-uneven-by-type
  kind: result
  text: Recall upper bounds of UEDIN-MS vary widely across syntactic error types, from 38%
    on ADJ→ADV and 44% on ADJ→NOUN up to 61-63% on determiners, adjectives and pronouns as
    source POS.
  scope: W&I development set, UEDIN-MS output; upper bounds computed as predicted changes
    divided by gold changes per type, and the rare NUM→DET and PART→DET types are set aside.
  evidence: Table 5 and Table 6
- id: no-conservatism-rank-link
  kind: result
  text: The number of syntactic changes a BEA2019 grammatical error correction system makes
    is unrelated to its shared-task rank. The partial-order Kendall tau between rank and number
    of SE changes, overall and per source POS, is 0.
  scope: 5 BEA2019 systems (UEDIN-MS, KAKAO&BRAIN, SHUYAO, CAMB-CUED, AIP-TOHOKU) on the W&I
    development set; ranks 1, 2, 5, 8 and 9 only, so a small sample.
  evidence: Table 14 and Section 5.1
- id: grammarly-weak-on-ses
  kind: result
  text: Grammarly detects and validly corrects almost none of most syntactic error types,
    with 0% recall on 7 of the 15 examined types including missing adverbs, missing verbs
    and VERB→ADJ replacements. Its best cases are superfluous determiners (41%) and PART→DET
    (67%, from 6 instances).
  scope: TLE-derived selected SE types, manually annotated by whether Grammarly detected the
    edit at all and whether at least one offered correction was valid; product version as
    evaluated at the time of the 2020 study.
  evidence: Table 7
- id: proficiency-monotone
  kind: result
  text: In the W&I corpus, the share of words whose POS tag survives correction rises with
    learner proficiency from level A to level C for every POS tag. Native writers generally
    change fewer tags than advanced learners, but the trend is mixed.
  scope: W&I training set, proficiency levels A-C plus LOCNESS native text, automatic UD parses;
    native counts are smaller, so borderline native-vs-C differences should not be read as
    significant.
  evidence: Table 3
- id: russian-case-genitive
  kind: result
  text: 'Learners of Russian most often replace the genitive with accusative or nominative
    on nouns: 132 accusative-for-genitive and 163 nominative-for-genitive corrections, the
    two largest cells of the noun case confusion matrix.'
  scope: RULEC learner Russian, UDPipe morphological features on automatic parses; nouns only,
    adjective case agreement is more symmetric (27 accusative-for-genitive vs 19 converse).
  evidence: Table 4
- id: russian-verb-aspect-voice
  kind: result
  text: Aspect errors in learner Russian are near-symmetric while voice errors are not. Perfective
    was corrected to imperfective 210 times against 223 the other way, but active-for-middle
    voice occurs 108 times against 45 for the converse.
  scope: RULEC learner Russian, UD morphological features from UDPipe parses; verbal features
    only.
  evidence: Section 4.2.2
- id: pos-edge-correlated
  kind: result
  text: 'POS-based and dependency-edge-based syntactic error types carry largely the same
    information in learner English: Cramer''s V between them is 0.78 for additions and deletions
    and 0.76 for replacements in TLE.'
  scope: TLE with manual UD annotation, 4584 extracted syntactic errors (2042 additions, 1048
    deletions, 1495 replacements); English only, so the redundancy may not hold for morphologically
    richer languages.
  evidence: Section 4.1
- id: context-first-ud-taxonomy
  kind: context
  text: SErCl derives a learner-error taxonomy from an existing syntactic representation framework,
    Universal Dependencies, rather than from hand-designed error categories, which makes the
    same taxonomy usable across languages without per-language rules.
  scope: As of publication in 2020; demonstrated on learner English (TLE, NUCLE, Lang8, W&I)
    and learner Russian (RULEC) only, and the earlier automatic classifier ERRANT requires
    new rules per language.
  evidence: Section 1 and Section 6
- id: context-only-form-changes
  kind: context
  text: SErCl covers only errors whose correction changes a morphosyntactic label, leaving
    agreement errors and inappropriate determiners that keep the representative token's label
    outside the taxonomy unless UD morphological features are used.
  scope: 'By construction: an edit is a syntactic error only when the source and target representative
    tokens'' labels differ, so non-SEs fall on the diagonal of the confusion matrix; in TLE
    44.4% of errors are POS-based SEs.'
  evidence: Section 2 and Section 4.1
qa:
- ask:
    plain: is there a way to label grammar mistakes in learner writing that works for more
      than one language?
    jargon: can a learner-error taxonomy be derived from Universal Dependencies annotation
      instead of hand-designed error categories?
    task: how do I get error types for learner text in a language with no hand-built error
      taxonomy?
    practitioner: should I build my own error category list for my learner corpus, or reuse
      a syntax-based one?
  answered_by:
  - context-first-ud-taxonomy
  - complements-errant
- ask:
    plain: how many of the learner mistakes that automatic error taggers leave unclassified
      can actually be given a type?
    jargon: what share of ERRANT OTHER edits receive a syntactic error class from POS-change
      typing?
    task: how do I get informative labels for the edits ERRANT dumps into OTHER?
    practitioner: if I already tag my learner corpus with ERRANT, is a syntax-based taxonomy
      worth adding on top?
  answered_by:
  - complements-errant
- ask:
    plain: can you trust an automatic parser on sentences written by language learners, which
      are full of mistakes?
    jargon: does substituting UDPipe parses for gold treebank dependency annotation shift
      the distribution of extracted syntactic error types?
    task: how do I extract syntactic error types from a learner corpus that has no manual
      dependency annotation?
    practitioner: do I need gold-parsed learner data, or is running a parser over my own corpus
      good enough?
  answered_by:
  - auto-parse-reliable
- ask:
    plain: do error types built from grammar annotation line up with the categories human
      annotators use?
    jargon: how much do POS-change syntactic error types overlap with the NUCLE error taxonomy's
      manual categories?
    task: how do I tell whether a syntax-derived error type corresponds to a familiar hand-annotated
      error category?
    practitioner: can I interpret syntax-derived error types using the NUCLE categories my
      team already knows?
  answered_by:
  - maps-to-nucle
- ask:
    plain: are automatic grammar correction tools worse at mistakes that change a sentence's
      structure?
    jargon: what recall upper bound does the BEA2019 winning system UEDIN-MS reach on gold
      syntactic errors compared with its overall recall?
    task: how do I find out which part of my error correction system's recall gap comes from
      structural errors?
    practitioner: if my users mostly make structure-changing mistakes, can I expect a top
      shared-task system to fix them?
  answered_by:
  - ses-harder
  - recall-uneven-by-type
- ask:
    plain: which kinds of learner mistakes do automatic correction tools handle worst?
    jargon: how do recall upper bounds for UEDIN-MS and Grammarly vary across individual syntactic
      error types?
    task: how do I work out which error types to target when improving a grammar correction
      system?
    practitioner: which learner error types should I not rely on existing correction systems
      for?
  answered_by:
  - recall-uneven-by-type
  - grammarly-weak-on-ses
- ask:
    plain: do grammar correction systems that make more changes score better in competitions?
    jargon: is the number of syntactic-error edits a BEA2019 system makes correlated with
      its shared-task ranking?
    task: should I make my grammar correction system less conservative to move up the leaderboard?
    practitioner: if I tune my system to edit more aggressively, will its shared-task rank
      improve?
  answered_by:
  - no-conservatism-rank-link
- ask:
    plain: does a commercial writing assistant catch mistakes where the wrong kind of word
      was used?
    jargon: what is Grammarly's recall on syntactic error types where correction changes the
      token's POS tag?
    task: how do I know which learner error types a commercial proofreader will leave uncorrected?
    practitioner: can I hand my students Grammarly and expect it to fix missing verbs and
      adverbs?
  answered_by:
  - grammarly-weak-on-ses
- ask:
    plain: do stronger language learners make fewer mistakes where a word of the wrong type
      is used?
    jargon: does the share of POS-preserving corrections increase monotonically with CEFR
      proficiency level in W&I, and how do native writers compare?
    task: how do I check whether my learners' error profiles shift as their proficiency rises?
    practitioner: can I use POS-changing error rates as a proficiency signal for my learners?
  answered_by:
  - proficiency-monotone
- ask:
    plain: which noun endings do people learning Russian get wrong most often?
    jargon: which noun case substitutions dominate the case confusion matrix in learner Russian
      corrections?
    task: how do I find out which Russian case contrasts to drill with my students?
    practitioner: should my Russian learner-error tooling prioritise genitive case confusions?
  answered_by:
  - russian-case-genitive
- ask:
    plain: what kinds of verb mistakes do learners of Russian make, and do the mix-ups go
      both ways?
    jargon: are aspect substitutions in learner Russian symmetric, and how does that compare
      with voice substitutions?
    task: how do I tell whether a Russian verb error type needs direction-specific handling?
    practitioner: for Russian learner verb errors, do I need to model both directions of the
      confusion separately?
  answered_by:
  - russian-verb-aspect-voice
- ask:
    plain: when labelling learner mistakes, do grammatical relations tell you anything that
      word categories do not?
    jargon: how strongly associated are POS-based and dependency-edge-label-based syntactic
      error types in learner English?
    task: should I type learner errors by dependency relation labels or by POS tags?
    practitioner: is it worth the extra work to build a dependency-edge error taxonomy for
      my learner corpus?
  answered_by:
  - pos-edge-correlated
- ask:
    plain: which learner mistakes are missed by an approach that defines errors as changes
      to a word's grammatical label?
    jargon: which error classes fall outside a taxonomy keyed on morphosyntactic label change,
      and are agreement errors covered?
    task: how do I know whether agreement and determiner-choice errors will show up in a label-change
      error taxonomy?
    practitioner: if my main concern is agreement errors, will a POS-change-based taxonomy
      cover them?
  answered_by:
  - context-only-form-changes
terminology:
  syntactic error (SE): A grammatical error whose correction changes a morphological feature,
    a POS tag or a dependency label of the edited span's representative token; errors that
    leave those labels intact are non-syntactic errors.
  representative token: In an edit span analysed against a dependency parse, the node of the
    span's sub-forest closest to the tree root, with the leftmost token used to break ties;
    its labels before and after correction define the error type.
  recall upper bound: For a grammatical error correction system and an error type, the number
    of edits of that type the system makes divided by the number in the gold standard, counting
    changes whether or not they are correct.
misreadings:
- 'The 56% figure for UEDIN-MS is an upper bound on recall, not measured recall: it counts
  every change the system made of the right type regardless of whether the correction was
  valid.'
- SErCl does not aim to reproduce human error annotation; the comparison with NUCLE checks
  that the automatic types carry the manual taxonomy's information, not that the two agree
  label for label.
- Finding that 60% of ERRANT's OTHER edits get a SErCl class is not a claim that SErCl is
  better than ERRANT overall — ERRANT remains the more informative source for spelling and
  word-order errors, which the parser handles poorly.
- The claim of cross-linguistic applicability rests on demonstrations in learner English and
  learner Russian; no result is reported for any other language.
- Advanced learners scoring above natives on the least error-prone POS tags is a mixed trend
  on small native data, not evidence that natives are worse writers.
links_extra:
  code: https://github.com/borgr/GEC_UD_divergences
---
