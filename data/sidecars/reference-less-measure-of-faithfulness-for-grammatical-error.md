---
claims:
- id: ucca-iaa-learner-language
  kind: result
  text: UCCA semantic annotation of learner-language essays reaches an inter-annotator DAG
    F-score of 0.845 (precision 0.834, recall 0.857), comparable to the agreement previously
    reported for standard English Wikipedia text.
  scope: 2 trained annotators after 6 training hours, on 4 doubly annotated essays of about
    500 tokens each plus 3 corrected NUCLE passages; English only, UCCA guidelines unmodified.
  evidence: Section 4.2
- id: valid-correction-usim
  kind: result
  text: Manually corrected NUCLE sentences score 0.84 average USim against their source when
    source and correction are annotated by different annotators, and 0.92 when annotated by
    the same annotator. The USim inter-annotator ceiling is 0.83.
  scope: Manual UCCA annotation of 6 essays, 3 of them doubly annotated, with NUCLE references
    treated as the valid correction; both alignment directions reported.
  evidence: Table 1 (left-hand side)
- id: distsim-comparable-translation
  kind: result
  text: Source and corrected sentences differ by DistSim 0.96 for Participants and Adverbials
    together and 0.93 for Scenes, close to the 0.95 and 0.96 Sulem et al. report for English-French
    translation pairs.
  scope: Different-annotator setting on the manually annotated essays; DistSim compares only
    per-label edge counts, not structure, so it is a weaker test than USim.
  evidence: Table 1 (right-hand side)
- id: automatic-usim-parser
  kind: result
  text: Replacing human UCCA annotation with the TUPA parser yields a USim of 0.7 between
    the parses of a NUCLE reference correction and its source. TUPA's own reported parsing
    accuracy is 0.73 in-domain and 0.68 out-of-domain.
  scope: TUPA biLSTM model trained on the UCCA English Wikipedia corpus with no domain adaptation
    to learner language; the source-correction similarity is therefore about as high as either
    parse's similarity to gold.
  evidence: Section 4.3
- id: sensitivity-low-quality
  kind: result
  text: 'Automatic USim separates poor corrections from valid ones on JFLEG: 5 partially trained
    correctors score 0.32-0.39, and 0.19 for the system with the lowest GLEU, while the 4
    human references score 0.72-0.78.'
  scope: 754 JFLEG source sentences, correctors trained and evaluated on JFLEG by Sakaguchi
    et al. (2017); the weak correctors delete phrases or change many words.
  evidence: Section 4.5
- id: not-length-of-edit
  kind: result
  text: USim rewards meaning preservation rather than conservatism. On one JFLEG sentence
    the reference scores 0.71 and a partially trained corrector only 0.33, even though the
    reference changes more words.
  scope: A single illustrative sentence pair from the JFLEG experiment with automatic (TUPA-parsed)
    USim.
  evidence: Section 4.5
- id: error-type-failure-modes
  kind: result
  text: Automatic USim is least neutral on edits that restructure the lower levels of the
    UCCA graph. Dangling modifier, pronoun reference, word tone, word-order, acronym, mechanical
    and missing-verb corrections produce the largest average USim changes.
  scope: MAEGE-based analysis over NUCLE sentences and edit sets with automatic TUPA parsing;
    several deviations are attributed to parser limitations (no character-level encoding,
    no implicit units) rather than to the measure.
  evidence: Section 4.4
- id: context-faithfulness-gap
  kind: context
  text: USim fills the meaning-preservation gap in reference-less evaluation of grammatical
    error correction. Earlier reference-less measures scored the output's grammaticality,
    and Asano et al. (2017) noted that a faithfulness measure for the task was lacking.
  scope: As of publication in 2018, for English grammatical error correction; USim is intended
    to be used alongside grammaticality-based reference-less measures and reference-based
    measures, not to replace them.
- id: context-semantic-annotation-of-ll
  kind: context
  text: The USim paper of Choshen and Abend reports the first attempt its authors are aware
    of to annotate learner language with a semantic scheme. Semantic structure is argued to
    sidestep the inconsistency of syntactic annotation of ungrammatical text.
  scope: Novelty claim is the authors' own as of 2018 and concerns semantic annotation of
    English learner language; prior learner-language schemes cited annotate syntax, either
    as used by or as intended by the learner.
- id: context-scheme-agnostic
  kind: context
  text: USim is defined over aligned semantic graphs rather than over UCCA specifically, so
    it can be adapted to other semantic schemes such as AMR. UCCA is the test case, chosen
    for its broad predicate coverage and stability across translation.
  scope: Only the UCCA instantiation is implemented and evaluated in the paper; portability
    to AMR or other schemes is a design argument, not a measured result.
qa:
- ask:
    practitioner: How can I evaluate a grammatical error correction system without reference
      corrections?
    unsorted:
    - Is there a reference-less metric for GEC?
    - What metric measures whether a correction preserved the original meaning?
  answered_by:
  - context-faithfulness-gap
  - context-scheme-agnostic
- ask:
    unsorted:
    - What is USim?
    - How does a semantic faithfulness score compare a correction with its source sentence?
    - What does the USim measure for grammatical error correction compute?
  answered_by:
  - context-scheme-agnostic
  - context-faithfulness-gap
- ask:
    unsorted:
    - Does a valid human correction get a high semantic similarity score to the ungrammatical
      source?
    - What USim score do NUCLE reference corrections get against their sources?
    - Does a meaning-preservation metric unfairly penalise correct edits?
  answered_by:
  - valid-correction-usim
  - not-length-of-edit
- ask:
    unsorted:
    - Can semantic annotation be applied consistently to ungrammatical learner text?
    - What is inter-annotator agreement for UCCA on learner language?
    - Is UCCA annotation reliable on text written by language learners?
  answered_by:
  - ucca-iaa-learner-language
  - context-semantic-annotation-of-ll
- ask:
    unsorted:
    - Does a semantic faithfulness metric for GEC need human annotation, or can a parser do
      it?
    - How well does automatic UCCA parsing work inside USim?
    - Is a fully automatic version of USim reliable?
  answered_by:
  - automatic-usim-parser
  - error-type-failure-modes
- ask:
    unsorted:
    - Does USim actually give low scores to bad corrections?
    - How were low-quality GEC outputs scored by USim on JFLEG?
    - Can a faithfulness metric distinguish unfaithful corrections from references?
  answered_by:
  - sensitivity-low-quality
  - not-length-of-edit
- ask:
    unsorted:
    - Which grammatical error types does an automatic UCCA-based faithfulness score handle
      badly?
    - Where does the USim faithfulness measure fail?
    - What are the known failure modes of parser-based USim?
  answered_by:
  - error-type-failure-modes
- ask:
    unsorted:
    - Are UCCA structures stable under grammatical error correction?
    - How much do UCCA category counts change between a source sentence and its correction?
    - Is semantic structure as robust to error correction as it is to translation?
  answered_by:
  - distsim-comparable-translation
  - ucca-iaa-learner-language
- ask:
    unsorted:
    - Can USim replace GLEU or M2 for ranking GEC systems?
    - Does USim discriminate between current state-of-the-art GEC systems?
    - Should a faithfulness measure be used on its own to evaluate correction quality?
  answered_by:
  - context-faithfulness-gap
  - sensitivity-low-quality
- ask:
    unsorted:
    - Does USim only work with UCCA?
    - Could a faithfulness measure like USim be built on AMR instead?
    - Why was UCCA chosen as the semantic scheme for measuring faithfulness?
  answered_by:
  - context-scheme-agnostic
key: choshen2018reference
coined: USim
gloss: reference-less semantic similarity score between a source sentence and its correction
one_liner: USim scores a grammatical error correction system without references by aligning
  the UCCA semantic graphs of the source sentence and the output and taking the F-score over
  matched labelled edges, giving a measure of semantic faithfulness that complements grammaticality-based
  reference-less measures.
misreadings:
- USim measures faithfulness to the source, not grammaticality or overall correction quality;
  a system that copies the source unchanged scores perfectly on USim, which is why the paper
  advocates using it alongside a grammaticality measure and reference-based measures.
- The JFLEG experiment does not show that USim can rank current state-of-the-art GEC systems;
  the paper deliberately uses 5 partially trained correctors precisely because state-of-the-art
  systems rarely change the source enough to be semantically unfaithful.
- 'A high USim score is not a reward for conservative editing: the reference in the paper''s
  example makes more word changes than the system output and still scores higher (0.71 versus
  0.33).'
- The automatic USim score of 0.7 between a reference correction and its source is not a measurement
  of the source and correction being 30% different in meaning; it is in the range of the TUPA
  parser's own accuracy, so parser error accounts for much of the gap.
- The error-type analysis showing large USim shifts for word order, acronym and missing-verb
  corrections reflects TUPA parser limitations rather than a property of UCCA structures,
  which are themselves unaffected by word order.
terminology:
  DAG F-score: A similarity measure between two UCCA annotations over the same tokens, in
    which two edges match if their lower nodes have identical leaf yields and identical labels,
    and precision and recall are their harmonic mean; it reduces to standard parsing F-score
    when both graphs are trees.
  DistSim: A coarse-grained comparison of two sets of UCCA annotations that averages, over
    sentence pairs, the absolute difference in the number of edges bearing a given UCCA label,
    ignoring structure.
  Faithfulness: The degree to which a system output preserves the meaning of its input sentence,
    as opposed to grammaticality or fluency, which concern only the well-formedness of the
    output.
  Learner language (LL): Text written by learners of a language, whose syntax may conform
    neither to the target language nor to any other known language, making syntactic annotation
    of it inconsistent across learners.
  RLM (reference-less measure): An evaluation measure for monolingual translation tasks such
    as grammatical error correction that compares system output to the source sentence alone,
    using no manually curated reference corrections.
  UCCA unit: 'A node in a UCCA graph: either a single word or several elements viewed jointly
    as one entity on semantic or cognitive grounds, with incoming edges labelled by the role
    the sub-unit plays in its parent relation.'
  USim: A reference-less similarity score between a source sentence and a proposed correction,
    computed as the F-score over labelled UCCA edges that match under an alignment induced
    from token-level edit-distance matching.
links_extra:
  anthology: https://aclanthology.org/N18-2020/
  code: https://github.com/borgr/USim
  ucca_guidelines: http://www.cs.huji.ac.il/~oabend/ucca.html
---
