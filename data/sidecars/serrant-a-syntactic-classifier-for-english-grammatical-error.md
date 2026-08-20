---
key: choshen2021serrant
coined: SERRANT
gloss: an automatic English grammatical-error-type classifier that falls back from ERRANT's
  readable labels to SErCl's "what changed into what" syntactic labels
one_liner: SERRANT is an automatic classifier of English grammatical error types that returns
  ERRANT's human-readable categories by default and substitutes SErCl's syntactic "source-tag
  → target-tag" types wherever ERRANT's label is uninformative, such as Other, Morph, or a
  POS-changing edit.
claims:
- id: what-serrant-is
  kind: context
  text: SERRANT is a released system and code library that unifies the two existing automatic
    English grammatical-error-type classifiers, ERRANT and SErCl, into a single taxonomy and
    a single output format.
  scope: English only, as of the 2021 release; the library exposes ERRANT-only, SErCl-only
    and combined annotators, and the SErCl component compares POS tags rather than full morphological
    features.
- id: default-errant
  kind: result
  text: SERRANT returns ERRANT's edit type in the default case, keeping ERRANT's R, M and
    U prefixes for replacement, missing and unnecessary edits. ERRANT's sub-classifications
    are preserved so users can group similar classes or ignore them.
  evidence: Section 2
  scope: Edits whose ERRANT type is judged informative; the 8 enumerated special cases of
    Section 2 override this default.
- id: other-fallback
  kind: result
  text: SERRANT replaces ERRANT's Other category, which signals failure to find an informative
    type, with SErCl's source-to-target syntactic type. Edits involving Intj, Num, Sym, X
    and Punct POS tags stay Other.
  evidence: Section 2, special case 1
  scope: Proper nouns are also treated as unreliable because the parser uses Propn as a fallback
    for misspelled words, so only the Propn → Propn type is kept.
- id: morph-replacement
  kind: result
  text: SERRANT replaces ERRANT's Morph type with SErCl types and re-exposes the lost information
    through a "WC" suffix. The suffix marks edits where the POS is unchanged but the lemma
    differs, so consume → eat becomes Verb:WC while eat → ate does not.
  evidence: Section 2, special case 2
  scope: Unreliable POS tags listed for the Other case are excluded, but Adj → Propn and Propn
    → Adj edits such as China → Chinese are kept.
- id: orth-propn
  kind: result
  text: For ERRANT's Orth type, SERRANT substitutes SErCl's X → Propn annotation when a non-sentence-initial
    word is corrected into a proper noun, as in "He founded apple" → "He founded Apple". Such
    capitalisation can change morphosyntax or meaning.
  evidence: Section 2, special case 4
  scope: Non-sentence-initial words changed into Propn only; other orthographic edits, such
    as a missing whitespace, keep ERRANT's Orth type.
- id: pos-change-types
  kind: result
  text: SERRANT gives POS-changing edits an explicit source-to-target type instead of ERRANT's
    misleading label. A noun corrected to a verb becomes Noun → Verb rather than Verb:Form,
    and pronoun/determiner swaps such as these → their become Pron → Det or Det → Pron.
  evidence: Section 2, special cases 6 and 7
  scope: English edits classified with a UD parser; correctness of the source and target tags
    depends on the parser's POS assignment.
- id: tense-modal-split
  kind: result
  text: SERRANT breaks up ERRANT's Verb:Tense category, which lumps tense, aspect and mood
    together. It keeps Verb:Tense only for be, have or "will" forms, adds a "Modal" suffix
    when both wordforms are modal verbs, and otherwise falls back to SErCl's type.
  evidence: Section 2, special case 8
  scope: 'The modal list has 9 members: can, could, may, might, shall, should, will, would
    and must; other tense, aspect and mood edits fall back to SErCl annotation.'
- id: aux-verb
  kind: result
  text: SERRANT separates auxiliaries from main verbs, marking edits as Aux where SErCl would,
    whereas ERRANT's Verb type covers both Aux and Verb edits.
  evidence: Section 2, special case 5
  scope: English edits; the distinction relies on the UD/spaCy analysis of the span.
- id: mw-suffix
  kind: result
  text: SERRANT adds an "MW" suffix to mark edits where either the source or the correction
    spans multiple words. The suffix is added only when the edit does not already carry a
    named type such as Verb:Tense.
  evidence: Section 2, special case 3
  scope: Multi-word edits after edit extraction; edits already assigned a named type are left
    without the suffix, and the Section 3 examples contain no multiword errors.
- id: cross-dataset-motivation
  kind: context
  text: SERRANT addresses the fact that grammatical-error taxonomies always differ across
    datasets of different languages and mostly differ even across datasets of the same language.
    Automatic edit-type classifiers are therefore the instrument of choice whenever more than
    one dataset is used.
  scope: The unification SERRANT provides is between the 2 English classifiers ERRANT and
    SErCl; cross-language taxonomy differences are stated as motivation and are not resolved
    by the released English-only system.
- id: informativeness-goal
  kind: context
  text: SERRANT's design rule is informativeness rather than fidelity to either source taxonomy.
    ERRANT is the default because it is more human-readable when accurate, and SErCl is used
    exactly where ERRANT's categories were shown to be uninformative or inconsistent.
  scope: The judgement that specific ERRANT categories are uninformative or inconsistent comes
    from the earlier SErCl study (Choshen et al., 2020); SERRANT itself reports no quantitative
    comparison of the two taxonomies.
- id: worked-examples
  kind: result
  text: SERRANT's output is illustrated on made-up sentences and on level-A learner sentences
    from the W&I corpus, for example "my cook → cooking" annotated R:Morph:Noun and "it →
    that" annotated R:Pron → Det.
  evidence: Section 3
  scope: Qualitative examples only, with no multiword errors and no accuracy or agreement
    measurements; the model outputs the M2 format, rendered visually in the examples.
qa:
- q:
  - How can I automatically label the error types of grammatical corrections in English text?
  - Is there a tool that assigns error type categories to GEC edits?
  - What does SERRANT do?
  answers:
  - what-serrant-is
  - default-errant
- q:
  - What is a good paper to read about grammatical error type taxonomies?
  - Where should I start reading about classifying grammatical error types across datasets?
  - What work combines the ERRANT and SErCl error taxonomies?
  answers:
  - what-serrant-is
  - cross-dataset-motivation
- q:
  - Why not just use ERRANT for error type classification?
  - What problems with ERRANT's categories motivated a new classifier?
  - When does SERRANT depart from ERRANT's annotation?
  answers:
  - informativeness-goal
  - other-fallback
  - morph-replacement
- q:
  - How are edits handled when the part of speech changes between a learner sentence and its
    corrected version?
  - What type does a noun-to-verb correction get in SERRANT?
  - Which classifier gives an explicit source-to-target tag for POS-changing grammatical errors?
  answers:
  - pos-change-types
  - aux-verb
- q:
  - How are tense, aspect and mood errors distinguished in English error annotation?
  - Does any error type classifier separate modal verb errors from tense errors?
  - What replaces ERRANT's Verb:Tense category in SERRANT?
  answers:
  - tense-modal-split
- q:
  - How is ERRANT's Morph error category refined?
  - What does a WC suffix mean in an English grammatical error type label?
  - How is word-choice distinguished from morphosyntactic error in edit annotation?
  answers:
  - morph-replacement
- q:
  - How are capitalisation errors involving proper nouns annotated?
  - Does SERRANT treat "apple → Apple" as an orthography error?
  - What happens to ERRANT's Orth type in SERRANT?
  answers:
  - orth-propn
- q:
  - How are multi-word edits marked in SERRANT's error types?
  - What does the MW suffix mean in an English grammatical error type label?
  answers:
  - mw-suffix
- q:
  - Does the SERRANT paper report accuracy numbers for its error type classifier?
  - Was SERRANT evaluated quantitatively against ERRANT or SErCl?
  - Is there any measured comparison between English grammatical error type classifiers, or
    only worked examples?
  answers:
  - worked-examples
  - informativeness-goal
- q:
  - Can SERRANT be used on languages other than English?
  - Which languages does SERRANT support?
  - Is the SErCl-based syntactic error taxonomy cross-lingual in the released tool?
  answers:
  - what-serrant-is
  - cross-dataset-motivation
misreadings:
- SERRANT is not a grammatical error correction system; it classifies the type of an already-given
  edit, or of an edit extracted automatically from a sentence and its correction.
- 'SERRANT is not cross-lingual despite building on SErCl''s cross-lingual syntactic taxonomy:
  the released library accepts English only.'
- 'SERRANT does not discard ERRANT: ERRANT''s types are the default output and its sub-classifications
  are preserved, with SErCl used only for the enumerated uninformative cases.'
- The SERRANT paper reports no accuracy, agreement or F-score comparison against ERRANT or
  SErCl; it describes the combination rules and gives qualitative examples.
- The SErCl component in the released library compares POS tags only, so an edit like book
  → books is typed Noun rather than Noun:Singular → Noun:Plural, even though the SErCl taxonomy
  as defined allows morphological features.
terminology:
  edit: In grammatical error correction, an erroneous part of a sentence paired with its correction.
  taxonomy: A set of grammatical error edit types used to categorise corrections.
  SErCl type: An error type written as the morphosyntactic annotation of the learner span
    followed by that of the corrected span, e.g. Noun → Verb, with None on either side for
    insertions and deletions, and abbreviated to a single tag when the two sides are identical.
  WC suffix: A marker in a SERRANT error type indicating that the part of speech did not change
    but the lemma did, so the error is one of word choice rather than of morphosyntax (consume
    → eat is Verb:WC).
  MW suffix: A marker in a SERRANT error type indicating that the source or the correction
    spans more than one word, added only when the edit has no already-named type.
  Modal suffix: A marker in a SERRANT error type indicating that both the original and the
    corrected wordform are modal verbs, separating modality errors from tense errors.
  Other type: In ERRANT, the category assigned when no informative error type can be found
    for an edit.
links_extra:
  code: https://github.com/matanel-oren/serrant
  arxiv: https://arxiv.org/abs/2104.02310
---
