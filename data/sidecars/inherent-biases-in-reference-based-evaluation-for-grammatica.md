---
one_liner: Because the valid corrections of a sentence follow a long-tailed distribution,
  reference-based GEC and simplification measures systematically under-score correct output,
  and this Low Coverage Bias rewards systems that under-correct rather than being fixable
  by re-scaling or by adding references.
coined: LCB (Low Coverage Bias)
gloss: the systematic under-scoring of valid text-to-text output caused by evaluating against
  too few reference corrections
key: choshen2018inherent
claims:
- id: long-tail-corrections
  kind: result
  text: Short learner-English sentences of 15 words or fewer have 1351.24 distinct valid corrections
    on average, with 74.34 corrections of frequency at least 0.001 accounting for 75% of the
    probability mass.
  scope: Estimated with UNSEENEST from crowdsourced corrections of 52 randomly sampled short
    sentences (15 words or less) from the NUCLE test set; longer sentences were excluded to
    keep the estimate reliable.
  evidence: Table 1
- id: rare-corrections-valid
  kind: result
  text: The rare corrections forming the long tail of valid GEC corrections are not annotation
    noise. Even the rarest crowdsourced corrections were judged valid 78% of the time, and
    frequency had little effect on judged validity.
  scope: A second crowdsourcing round with 3 validity annotators per correction, on the same
    52 short NUCLE sentences of 15 words or less.
  evidence: Section 2.1 and Appendix C
- id: perfect-system-f05
  kind: result
  text: A perfect GEC system scores only 0.42 F0.5 under the M2 scorer with 2 references,
    so reference-based scores drastically under-estimate correct output.
  scope: Accelerated bootstrap with 1000 iterations, N = 1312 and Ncor = 136 to match NUCLE
    test-set statistics.
  evidence: Figure 1b
- id: more-references-saturate
  kind: result
  text: Adding reference corrections gives sharply diminishing returns in GEC evaluation.
    The expected sentence-level accuracy of a perfect system is only about 0.5 even at 20
    references, with a slope of 0.004 per added reference at M = 20.
  scope: Sampling 1000 reference sets per sentence for M = 1..20 over the estimated correction
    distributions of 52 short NUCLE sentences; sampling without replacement gives a faster
    increase, above 0.47 at M = 10.
  evidence: Figure 1a
- id: gleu-same-saturation
  kind: result
  text: GLEU shows the same low-coverage saturation as M2 in GEC, scoring a perfect system
    only about 2% higher than M2 does across reference-set sizes.
  scope: Mean GLEU sentence score, bootstrapped on 52 short NUCLE sentences; I-measure untested,
    its runtime being prohibitive.
  evidence: Figure 1b
- id: systems-beat-humans
  kind: result
  text: The GEC systems RoRo and JMGR surpass the F0.5 score of a perfect system evaluated
    with 2 references on the NUCLE test set. Both also obtain comparable or superior scores
    to humans under GLEU.
  scope: CoNLL 2014 shared-task systems plus three stronger later systems, evaluated on the
    NUCLE test set with M = 2 as in their reported results; confidence intervals at p = .95.
  evidence: Figure 2 and Section 2.3
- id: rescaling-fails
  kind: result
  text: Re-scaling reference-based GEC scores by inter-annotator agreement cannot remove Low
    Coverage Bias, because the bias is not a constant factor. Systems that only correct closed-class
    errors can exceed the score of a perfect system.
  scope: Argument grounded in the NUCLE M = 2 comparison of CoNLL 2014 systems against a perfect
    system; directed at the Ratio Scoring proposal of Bryant and Ng (2015).
  evidence: Section 2.4
- id: systems-undercorrect
  kind: result
  text: GEC systems change the source far less than human annotators do, sometimes by an order
    of magnitude. 36 NUCLE reference sentences contain 6 word changes, while no system produces
    more than 5 sentences with 6 word changes.
  scope: CoNLL 2014 system outputs versus NUCLE references, non-alphanumeric characters excluded;
    measured by WORDCHANGE, word-order Spearman rho, and splits/concatenations.
  evidence: Figure 3
- id: open-class-undercorrected
  kind: result
  text: Open-class GEC error types are the most under-corrected. Verb, noun, preposition and
    pronoun selection fall in the bottom quarter of correction ratios, while orthography,
    noun plurality, adjective inflection and determiner selection fall in the top quarter.
  scope: Automatic edit typing of all CoNLL 2014 system outputs on the NUCLE test set using
    the data of Bryant et al. (2017), counting attempted rather than valid corrections; punctuation
    selection is a closed-class exception in the bottom quarter.
  evidence: Section 3.4 and Appendix E
- id: more-refs-reduce-undercorrection
  kind: result
  text: Tuning against more references reduces under-correction in GEC. Oracle re-ranking
    of the RoRo system's 100-best lists on the NUCLE test set produces more word changes as
    the number of references grows, with no significant change in word order.
  scope: Oracle re-ranking with the M2 F-score over 1312 samples of M references drawn from
    the ten NUCLE references of Bryant and Ng (2015); a simulation of retraining, since no
    multi-reference corpus is large enough to retrain a system.
  evidence: Figure 4
- id: sari-coverage-flat
  kind: result
  text: SARI gives a perfect text-simplification system a coverage of about 0.45 that is largely
    independent of the number of references. The score of a system that outputs one of the
    given references drops as references are added.
  scope: 2500 crowdsourced simplifications for 47 sentences using the corpus and protocol
    of Xu et al. (2016), UNSEENEST-estimated distributions, and the same bootstrapping protocol
    as the GEC experiments.
  evidence: Figure 1c
- id: simplification-long-tail
  kind: result
  text: Valid simplifications are even more numerous than valid corrections. A sentence has
    2636.29 distinct valid simplifications on average, and the 111.19 simplifications of frequency
    at least 0.001 cover only 0.42 of the probability mass.
  scope: UNSEENEST estimates from 2500 crowdsourced simplifications of 47 sentences from the
    corpus of Xu et al. (2016).
  evidence: Table 4
- id: ts-oracle-reranking
  kind: result
  text: 'Under-prediction in text simplification also eases with more references: under MAX-SARI
    oracle re-ranking, a neural simplification model left 50 sentences unchanged with 1 reference
    but only 29 unchanged with 8 references.'
  scope: Oracle re-ranking on k-best lists from Moses (k = 100) and a neural model (Nisioi
    et al., 2017, k = 12); MAX-SARI only, since multi-reference SARI does not reward matching
    a single reference.
  evidence: Section 4 and Appendix G
- id: methodology-contribution
  kind: context
  text: 'Choshen and Abend (2018) contribute two reusable methodologies to monolingual translation
    evaluation: bootstrapping the score a hypothetical perfect system would receive, in order
    to audit an evaluation measure. The second estimates the distribution of valid outputs
    per source sentence from crowdsourced samples.'
  scope: Demonstrated for GEC and text simplification only; the authors suggest applicability
    to style conversion and automatic post-editing without testing those tasks.
  evidence: Section 5
- id: field-entry-point
  kind: context
  text: Inherent Biases in Reference-based Evaluation for Grammatical Error Correction and
    Text Simplification is a standard reference for the argument that reference-based GEC
    evaluation rewards under-correction and cannot be repaired by adding references.
  scope: As of its ACL 2018 publication; concerns English learner-essay GEC on NUCLE and English
    text simplification, and addresses M2, GLEU, sentence accuracy and SARI rather than reference-less
    or semantic measures.
qa:
- ask:
    plain: why do grammar correction tools leave so many mistakes in a sentence uncorrected?
    jargon: what drives the conservative edit behaviour of grammatical error correction systems
      relative to human annotators?
    task: how do I get a grammar correction model to attempt more edits instead of copying
      the input?
    practitioner: if my grammar correction model barely changes the input, should I blame
      my training objective or reference-based F-score evaluation with few references?
  answered_by:
  - systems-undercorrect
  - open-class-undercorrected
  - more-refs-reduce-undercorrection
- ask:
    plain: would collecting more corrected versions of each sentence make grammar correction
      scores trustworthy?
    jargon: do additional reference corrections mitigate low coverage bias in M2 and GLEU
      evaluation?
    task: how many reference corrections should I annotate per sentence to evaluate a grammar
      correction system fairly?
    practitioner: is it worth paying annotators for extra reference corrections in my GEC
      test set?
  answered_by:
  - more-references-saturate
  - long-tail-corrections
  - gleu-same-saturation
- ask:
    plain: how many different ways can one badly written sentence be fixed, and are the unusual
      fixes real?
    jargon: what is the distribution of valid corrections per source sentence in grammatical
      error correction, and are low-frequency crowdsourced corrections valid?
    task: how do I tell whether an unusual correction produced by my grammar tool is a genuine
      alternative or an error?
    practitioner: should I discard rare crowdsourced corrections as annotation noise when
      building a GEC reference set?
  answered_by:
  - long-tail-corrections
  - rare-corrections-valid
- ask:
    plain: if a grammar correction were completely right, what score would an automatic metric
      give it?
    jargon: what F0.5 does an oracle-correct system obtain under the M2 scorer with 2 references,
      and how does GLEU compare?
    task: how do I interpret an F0.5 number from the M2 scorer when judging my grammar correction
      output?
    practitioner: my GEC system scores in the 0.4 range on M2 — does that mean the output
      is bad?
  answered_by:
  - perfect-system-f05
  - gleu-same-saturation
- ask:
    plain: have automatic grammar correction programs really become better than people at
      fixing sentences?
    jargon: do CoNLL-era GEC systems exceed human F0.5 and GLEU scores on the NUCLE test set,
      and what explains it?
    task: how do I check whether a reported above-human GEC score reflects real quality?
    practitioner: a grammar correction system reports scores above human annotators — should
      I believe it?
  answered_by:
  - systems-beat-humans
  - rescaling-fails
- ask:
    plain: can you correct grammar-correction scores by dividing out how often annotators
      agree with each other?
    jargon: does re-scaling reference-based GEC scores by inter-annotator agreement remove
      low coverage bias?
    task: how do I adjust GEC metric scores for the fact that references cover only some valid
      corrections?
    practitioner: should I normalise my GEC scores by an annotator-agreement factor before
      reporting them?
  answered_by:
  - rescaling-fails
  - systems-beat-humans
- ask:
    plain: which kinds of writing mistakes do grammar correction programs usually not even
      try to fix?
    jargon: which GEC error types have the lowest correction ratios, and how do open-class
      and closed-class errors differ?
    task: which error categories should I expect to fix myself after running an automatic
      grammar corrector?
    practitioner: can I rely on a grammar correction system for verb, noun and preposition
      choice errors in my text?
  answered_by:
  - open-class-undercorrected
- ask:
    plain: can you trust the standard automatic score used to judge sentence simplification?
    jargon: how does SARI behave for an oracle-correct simplification system as the number
      of references varies?
    task: how do I compare SARI numbers reported with different numbers of reference simplifications?
    practitioner: should I report SARI as the main metric for my text simplification model?
  answered_by:
  - sari-coverage-flat
  - simplification-long-tail
- ask:
    plain: does the trouble with judging grammar correction against reference sentences show
      up in sentence simplification too?
    jargon: does low coverage bias extend from GEC to text simplification, given the number
      of valid simplifications per sentence?
    task: how do I evaluate a sentence simplification model given how many different valid
      simplifications exist?
    practitioner: if reference-based scoring misleads for grammar correction, should I distrust
      it for my simplification system as well?
  answered_by:
  - simplification-long-tail
  - sari-coverage-flat
  - ts-oracle-reranking
- ask:
    plain: what should I read first about how automatic scores for grammar correction go wrong?
    jargon: which work established that reference-based GEC evaluation rewards under-correction
      and cannot be fixed by adding references?
    task: where do I start reading before choosing an evaluation setup for grammatical error
      correction?
  answered_by:
  - field-entry-point
  - methodology-contribution
- ask:
    plain: is there a way to estimate how many acceptable rewrites a single sentence actually
      has?
    jargon: what methodology exists for auditing an evaluation measure in monolingual translation
      by bootstrapping a perfect system's score?
    task: how do I test whether an automatic metric for a rewriting task is biased before
      I adopt it?
    practitioner: can I reuse an existing methodology to audit the metric I plan to use for
      my rewriting task?
  answered_by:
  - methodology-contribution
  - long-tail-corrections
- ask:
    plain: if a system is tuned against more corrected versions of each sentence, does it
      start making more changes?
    jargon: does oracle re-ranking of n-best lists against larger reference sets increase
      edit counts in GEC and simplification?
    task: how do I reduce under-correction when tuning or re-ranking my grammar correction
      system?
    practitioner: should I invest in more reference corrections to stop my model from being
      too conservative?
  answered_by:
  - more-refs-reduce-undercorrection
  - ts-oracle-reranking
misreadings:
- 'Low Coverage Bias is not a uniform scaling of scores that can be divided out: some correction
  policies, in particular correcting only closed-class errors, are penalised much less than
  others, which is why re-scaling by human agreement does not fix it.'
- Systems scoring above the F0.5 of a perfect system on NUCLE does not mean those systems
  correct better than humans; it means the 2-reference measure rewards making few but targeted
  changes.
- 'The finding that more references reduce under-correction is not an endorsement of collecting
  more references as the solution: the returns diminish sharply and the number needed for
  reliable evaluation remains infeasible.'
- The 1351.24 corrections per sentence figure applies to sentences of 15 words or fewer; longer
  sentences with multiple independent errors were deliberately excluded and would have more
  variants, not fewer.
- 'The long tail of rare corrections is not an artefact of sloppy crowdsourcing: even the
  rarest corrections were judged valid 78% of the time.'
- Correlation studies between human judgments and reference-based measures do not certify
  those measures against Low Coverage Bias, because if all evaluated outputs under-correct
  similarly, the correlation cannot detect insensitivity to under-correction.
terminology:
  Low Coverage Bias (LCB): The under-estimation of text-to-text system quality that arises
    when a reference set covers only a small share of the valid outputs for a source sentence.
  Coverage: For a source sentence and a reference set of size M, the probability that a correction
    sampled from the human correction distribution for that sentence appears in the reference
    set.
  True measure: The value an evaluation measure would return if the reference set for each
    source sentence contained every valid output rather than a small sample.
  WORDCHANGE: The number of words altered, deleted or added between a source sentence and
    a correction, counted after word-aligning the two as a weighted bipartite matching with
    token edit distances as edge weights.
  Exact Index Match: A relaxed sentence-level accuracy for grammatical error correction that
    requires the corrected output to change exactly the same source word positions as a reference,
    without requiring the replacements themselves to match.
  MAX-SARI: The maximum single-reference SARI score over a reference set, used because multi-reference
    SARI is a combination of references rather than a maximum and therefore does not award
    a perfect score to output identical to one reference.
  Lucky perfect system: A hypothetical simplification system whose output is one of the references
    actually given to the evaluation measure, used to test whether a measure rewards exactly
    matching a reference.
  UNSEENEST: A non-parametric algorithm, originally developed for estimating the histogram
    of gene variants including undiscovered ones, that estimates the histogram of a discrete
    distribution by minimising earthmover distance and can therefore estimate how many valid
    corrections a sentence has.
links_extra:
  code: https://github.com/borgr/IBGEC
  pdf: https://aclanthology.org/P18-1059.pdf
---
