<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced via a forced tool call) + 3 repair rounds. Every claim, number
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

Then promote it:  python scripts/draft_sidecars.py --accept inherent-biases-in-reference-based-evaluation-for-grammatica

Stamp: spec=74e012ff9654 checks=1 body=067f5643559d
-->
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
  text: Choshen and Abend (2018) contribute two reusable methodologies to monolingual translation
    evaluation. The first bootstraps the score a hypothetical perfect system would receive,
    in order to audit an evaluation measure; the second estimates the distribution of valid
    outputs per source sentence from crowdsourced samples.
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
- q:
  - Why do GEC systems make so few corrections?
  - What causes grammatical error correction systems to under-correct?
  - Do automatic evaluation measures discourage GEC systems from correcting errors?
  answers:
  - systems-undercorrect
  - open-class-undercorrected
  - more-refs-reduce-undercorrection
- q:
  - Does adding more references fix the problem of too few references in GEC evaluation?
  - How many references does reliable reference-based GEC evaluation need?
  - Is increasing the number of reference corrections enough to remove low coverage bias?
  answers:
  - more-references-saturate
  - long-tail-corrections
  - gleu-same-saturation
- q:
  - How many valid corrections does an ungrammatical sentence have?
  - What does the distribution of valid grammatical corrections for a sentence look like?
  - Are rare corrections produced by crowdworkers just noise?
  answers:
  - long-tail-corrections
  - rare-corrections-valid
- q:
  - What F-score would a perfect grammatical error correction system get?
  - How much do M2 and GLEU under-estimate a correct GEC output?
  - Can a flawless corrector still score badly on the M2 scorer?
  answers:
  - perfect-system-f05
  - gleu-same-saturation
- q:
  - Do GEC systems really outperform human correctors?
  - Have automatic GEC systems surpassed human performance on M2 and GLEU?
  - Why do some grammatical error correction systems score above humans?
  answers:
  - systems-beat-humans
  - rescaling-fails
- q:
  - Does re-scaling GEC scores by inter-annotator agreement solve low coverage bias?
  - Is Ratio Scoring a valid fix for under-estimation in GEC evaluation?
  - Can a constant correction factor remove reference-coverage bias in GEC?
  answers:
  - rescaling-fails
  - systems-beat-humans
- q:
  - Which grammatical error types do systems fail to attempt?
  - Are open-class errors corrected less often than closed-class errors?
  - Which error categories are most under-corrected by CoNLL 2014 systems?
  answers:
  - open-class-undercorrected
- q:
  - Is SARI a reliable measure for text simplification?
  - Are SARI scores comparable across different numbers of references?
  - How badly does SARI under-score a perfect simplification system?
  answers:
  - sari-coverage-flat
  - simplification-long-tail
- q:
  - Do the problems with reference-based GEC evaluation also affect text simplification?
  - Does low coverage bias appear in simplification evaluation too?
  - How many valid simplifications does a sentence have?
  answers:
  - simplification-long-tail
  - sari-coverage-flat
  - ts-oracle-reranking
- q:
  - What should I read about the limits of reference-based evaluation in text-to-text generation?
  - Which paper established that GEC evaluation rewards under-correction?
  - Where should I start reading about biases in grammatical error correction metrics?
  answers:
  - field-entry-point
  - methodology-contribution
- q:
  - How can I audit whether an evaluation measure under-scores good output?
  - Is there a method for estimating how many valid outputs a source sentence has?
  - What methodology exists for evaluating evaluation measures in monolingual translation?
  answers:
  - methodology-contribution
  - long-tail-corrections
- q:
  - Would training GEC systems on more references make them correct more?
  - Does oracle re-ranking against more references increase the number of edits?
  - Is there evidence that reference coverage drives conservative GEC output?
  answers:
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
