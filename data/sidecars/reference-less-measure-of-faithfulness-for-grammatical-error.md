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
    plain: is there a way to check whether a grammar correction changed the writer's meaning,
      without comparing to a human-written correction?
    jargon: what reference-less evaluation measures meaning preservation rather than grammaticality
      in grammatical error correction?
    task: how do I score a corrected sentence for faithfulness to the source when I have no
      gold correction to compare against?
    practitioner: I have no reference corrections for my GEC outputs — can I still measure
      whether they preserved the original meaning?
  answered_by:
  - context-faithfulness-gap
  - context-scheme-agnostic
- ask:
    plain: how can two sentences be compared for whether they still say the same thing after
      one has been edited for grammar?
    jargon: how does a semantic-graph similarity score quantify meaning preservation between
      a source sentence and its correction?
    task: how do I compute a faithfulness score between an ungrammatical sentence and its
      corrected version?
    practitioner: what would I actually be measuring if I adopted a semantic similarity score
      for grammar correction output?
  answered_by:
  - context-scheme-agnostic
  - context-faithfulness-gap
- ask:
    plain: do genuinely good grammar corrections score high on a meaning-preservation measure,
      or do legitimate edits get punished?
    jargon: what USim values do human NUCLE reference corrections receive against their source
      sentences, relative to the inter-annotator ceiling?
    task: how do I check that a faithfulness measure does not penalise valid corrections before
      I trust it on system output?
    practitioner: if I score my corrections for meaning preservation, will heavy but correct
      rewriting be marked down?
  answered_by:
  - valid-correction-usim
  - not-length-of-edit
- ask:
    plain: can people annotate the meaning of essays written by language learners consistently,
      even when the grammar is broken?
    jargon: what inter-annotator agreement does UCCA semantic annotation achieve on learner-language
      essays compared with standard English text?
    task: how do I get reliable semantic structure annotation over ungrammatical, non-native
      writing?
    practitioner: should I expect usable annotation quality if I have annotators mark semantic
      structure on learner essays?
  answered_by:
  - ucca-iaa-learner-language
  - context-semantic-annotation-of-ll
- ask:
    plain: can a parser stand in for human annotation when scoring whether a correction kept
      the meaning?
    jargon: how much does substituting TUPA parses for gold UCCA annotation degrade the USim
      faithfulness score?
    task: how do I run a semantic faithfulness metric for grammatical error correction fully
      automatically?
    practitioner: can I trust the parser-based version of a meaning-preservation score on
      my own correction outputs?
  answered_by:
  - automatic-usim-parser
  - error-type-failure-modes
- ask:
    plain: does a meaning-preservation score actually give low marks to bad grammar corrections?
    jargon: does automatic USim separate partially trained GEC systems from human references
      on JFLEG?
    task: how do I test whether a faithfulness measure discriminates unfaithful system output
      from human corrections?
    practitioner: will a semantic similarity score flag the corrections from my undertrained
      model as unfaithful?
  answered_by:
  - sensitivity-low-quality
  - not-length-of-edit
- ask:
    plain: which kinds of grammar mistakes trip up an automatic meaning-preservation score?
    jargon: which error types produce the largest USim shifts under parser-based semantic
      graph comparison?
    task: which correction types should I be careful about when interpreting an automatic
      faithfulness score?
    practitioner: my system mostly fixes word order and pronoun reference — is a parser-based
      faithfulness score reliable for that?
  answered_by:
  - error-type-failure-modes
- ask:
    plain: how much does the meaning structure of a sentence shift when someone fixes its
      grammar?
    jargon: how do UCCA category distributions differ between source and corrected sentences
      relative to translation pairs?
    task: how do I tell whether semantic structure is stable enough across error correction
      to build a faithfulness measure on it?
    practitioner: is semantic structure stable enough under grammar editing for me to rely
      on it as an evaluation signal?
  answered_by:
  - distsim-comparable-translation
  - ucca-iaa-learner-language
- ask:
    plain: is a meaning-preservation score enough on its own to rank grammar correction systems?
    jargon: can reference-less USim substitute for GLEU or M2 in ranking GEC systems, or only
      complement grammaticality measures?
    task: how should I combine a faithfulness score with a grammaticality score when evaluating
      correction systems?
    practitioner: should I report a semantic faithfulness score instead of GLEU for my grammar
      correction system?
  answered_by:
  - context-faithfulness-gap
  - sensitivity-low-quality
- ask:
    plain: does a meaning-comparison score have to use one particular way of representing
      sentence meaning?
    jargon: is USim tied to UCCA, or can it be instantiated over AMR or other semantic representations?
    task: how do I build a faithfulness measure over a semantic representation I already have
      parsers for?
    practitioner: I already work with AMR — can I use a semantic faithfulness measure for
      correction without switching to UCCA?
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
