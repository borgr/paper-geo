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
    practitioner: What should I read about cross-lingual learner error taxonomies?
    unsorted:
    - How can grammatical errors in learner text be classified in a way that works for more
      than one language?
    - Is there a language-independent error taxonomy for grammatical error correction?
  answered_by:
  - context-first-ud-taxonomy
  - complements-errant
- ask:
    unsorted:
    - Does SErCl replace ERRANT or complement it?
    - How much of what ERRANT labels OTHER can be classified another way?
    - What fraction of unclassified learner errors get a type from Universal Dependencies
      label changes?
  answered_by:
  - complements-errant
- ask:
    unsorted:
    - Can automatic dependency parsers be trusted on ungrammatical learner sentences?
    - Does using UDPipe instead of manual treebank annotation change the learner error distribution?
    - How reliable is syntactic error extraction from parsed learner text?
  answered_by:
  - auto-parse-reliable
- ask:
    unsorted:
    - Do UD-derived error types agree with hand-annotated taxonomies like NUCLE's?
    - How well do syntactic error classes map onto the NUCLE error categories?
  answered_by:
  - maps-to-nucle
- ask:
    unsorted:
    - Are grammatical error correction systems worse on syntactic errors than on other errors?
    - What is the recall of the BEA2019 winning system on errors that change syntactic structure?
    - How well does UEDIN-MS handle errors whose correction alters the parse?
  answered_by:
  - ses-harder
  - recall-uneven-by-type
- ask:
    unsorted:
    - Which learner error types do GEC systems handle worst?
    - Are some syntactic error types much harder for correction systems than others?
  answered_by:
  - recall-uneven-by-type
  - grammarly-weak-on-ses
- ask:
    unsorted:
    - Does making more edits make a grammatical error correction system rank higher?
    - Is system conservatism related to BEA2019 shared-task rank?
  answered_by:
  - no-conservatism-rank-link
- ask:
    unsorted:
    - How well does Grammarly correct errors that change part of speech?
    - Does a commercial proofreading tool catch syntactic learner errors?
    - Which error types does Grammarly miss almost entirely?
  answered_by:
  - grammarly-weak-on-ses
- ask:
    practitioner: How do syntactic error rates differ across CEFR proficiency levels in W&I?
    unsorted:
    - Do more advanced learners make fewer errors that change part of speech?
    - Do native writers make fewer POS-changing errors than advanced learners?
  answered_by:
  - proficiency-monotone
- ask:
    unsorted:
    - What case errors do learners of Russian make most often?
    - Which Russian noun case is hardest for learners?
    - What do learner Russian case confusion matrices show?
  answered_by:
  - russian-case-genitive
- ask:
    unsorted:
    - What aspect and voice errors appear in learner Russian?
    - Do learners of Russian confuse perfective and imperfective symmetrically?
  answered_by:
  - russian-verb-aspect-voice
- ask:
    unsorted:
    - Is a taxonomy of learner errors based on dependency edge labels worth building rather
      than one based on POS tags?
    - How correlated are POS-based and dependency-label-based learner error types?
    - Do dependency labels add information over POS tags when typing learner errors?
  answered_by:
  - pos-edge-correlated
- ask:
    unsorted:
    - Which learner errors does a UD-label-change taxonomy fail to cover?
    - Are agreement errors counted as syntactic errors by SErCl?
    - What are the limits of defining errors by changed morphosyntactic labels?
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
