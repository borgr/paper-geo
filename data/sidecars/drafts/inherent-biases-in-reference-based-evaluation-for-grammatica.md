<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced via a forced tool call) + 2 repair rounds. Every claim, number
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

Stamp: spec=d57862840a90 checks=4 body=8bdb7673514c
-->
---
one_liner: Because the distribution of valid corrections for a sentence is long-tailed, reference-based
  GEC evaluation cannot be fixed by re-scaling or by adding references, and it rewards systems
  that under-correct.
key: choshen2018inherent
coined: LCB
gloss: low coverage bias — the systematic under-estimation of text-to-text system quality
  caused by evaluating against too few reference outputs
terminology:
  Low Coverage Bias (LCB): The gap between a text-to-text system's score against the full
    set of valid outputs and its score against a small reference set, arising because most
    valid corrections of a sentence are absent from the references.
  Coverage of a reference set: For an input sentence, the probability that a correction sampled
    from the human correction distribution for that sentence appears in the set of M references
    given for it.
  Under-correction: A system's tendency to leave a source substring unchanged even when it
    could generate a valid correction, because keeping the source is more likely to match
    a small reference set than any single valid correction is.
  Exact Index Match: A relaxed sentence-level accuracy for grammatical error correction that
    counts a system output as matching a reference when the two change the same source word
    positions, regardless of what those words were changed to.
  MAX-SARI: A variant of the SARI text-simplification metric defined as the maximum single-reference
    SARI score over the available references, equal to SARI when there is 1 reference.
  UNSEENEST: A non-parametric algorithm, originally built for estimating how many unseen variants
    a gene has, that fits a discrete distribution's histogram — including its unobserved atoms
    — by minimizing earthmover distance.
claims:
- id: long-tail-corrections
  kind: result
  text: Short English learner sentences of 15 words or fewer have on average 1351.24 distinct
    valid corrections. Just 74.34 corrections, each occurring at least 0.1% of the time, already
    account for 75% of the probability mass.
  scope: 52 short sentences (≤15 words) sampled from the NUCLE test set, with corrections
    crowdsourced under instructions to correct grammaticality only and not style; distributions
    estimated with UNSEENEST.
  evidence: Table 1
- id: rare-corrections-valid
  kind: result
  text: 'The many rare corrections of a learner sentence are not annotation noise: even the
    rarest crowdsourced corrections were judged valid 78% of the time. Correction frequency
    had little effect on judged validity.'
  scope: 3 annotators judging validity of corrections collected in the earlier crowdsourcing
    round, on the same 52 short NUCLE sentences; details in Appendix C.
  evidence: Section 2.1 (details in Appendix C)
- id: perfect-system-low-score
  kind: result
  text: A perfect grammatical error correction system, sampling its output from the human
    correction distribution, scores only about 0.42 F0.5 with 2 references. Its sentence-level
    accuracy is only around 0.5 even with 20 references.
  scope: Bootstrapped over NUCLE test statistics (N = 1312 sentences, 136 needing no correction),
    M = 1 to 20, M2 scorer with heuristically produced reference edits.
  evidence: Figure 1a and Figure 1b
- id: diminishing-returns-references
  kind: result
  text: 'Adding references to grammatical error correction evaluation shows sharply diminishing
    returns: the expected accuracy of a perfect system gains only 0.004 per extra reference
    at M = 20. GLEU saturates the same way, running about 2% above M2.'
  scope: Sampling references with replacement from UNSEENEST-estimated per-sentence correction
    distributions on 52 short NUCLE sentences; sampling without replacement gives faster growth,
    above 0.47 accuracy at M = 10.
  evidence: Figure 1a and Figure 1b
- id: systems-beat-perfect-system
  kind: result
  text: Two CoNLL-2014-era GEC systems, RoRo and JMGR, surpass the F0.5 score of a perfect
    system evaluated with 2 references on the NUCLE test set. Comparable or superior scores
    to humans also appear under GLEU.
  scope: NUCLE test set with M = 2, as in the systems' own reported results; confidence intervals
    from accelerated bootstrap with 1000 iterations.
  evidence: Figure 2 and Section 2.3
- id: systems-undercorrect
  kind: result
  text: GEC systems change the source far less than human annotators do, often by an order
    of magnitude. 36 NUCLE reference sentences contain 6 word changes, whereas the largest
    number of sentences with 6 word changes by any system is 5.
  scope: All CoNLL 2014 shared task systems plus RoRo, JMGR and Xie et al. on the NUCLE test
    references, with non-alphanumeric characters excluded; word changes measured by bipartite
    word alignment.
  evidence: Figure 3
- id: more-references-more-correction
  kind: result
  text: 'Tuning against more references reduces under-correction: oracle re-ranking of the
    RoRo system''s 100-best list makes more word changes as the number of references grows,
    while word order shows no significant difference.'
  scope: RoRo with k = 100 on the NUCLE test corpus, F-score as the re-ranking objective,
    averaging over 1312 samples of M references drawn from the 10 references of Bryant and
    Ng (2015).
  evidence: Figure 4
- id: open-class-undercorrected
  kind: result
  text: 'Open-class selection errors are the most under-corrected error types in GEC: verb,
    noun, particle/preposition and pronoun selection all fall in the bottom quarter of system-to-reference
    correction ratios.'
  scope: Automatic edit typing of all CoNLL 2014 system outputs on the NUCLE test set using
    Bryant et al. (2017); ratio of mean system corrections to mean reference corrections per
    type, ignoring whether a correction is valid. Closed-class punctuation selection is also
    in the bottom quarter.
  evidence: Section 3.4 (details in Appendix E)
- id: type-frequency-not-explanation
  kind: result
  text: The pattern of which GEC error types get corrected is not explained by how common
    the types are. Error type frequency correlates slightly negatively with the under-correction
    ratio (ρ = -0.29, p = 0.16).
  scope: Edit types automatically assigned to CoNLL 2014 system outputs on the NUCLE test
    set; the correlation is not statistically significant.
  evidence: Section 3.4
- id: simplification-long-tail
  kind: result
  text: 'Text simplification has an even heavier tail of valid outputs than GEC: sentences
    have on average 2636.29 distinct valid simplifications. Simplifications occurring at least
    0.1% of the time cover only 0.42 of the probability mass.'
  scope: 2500 crowdsourced reference simplifications for 47 sentences, using the corpus and
    annotation protocol of Xu et al. (2016), with distributions estimated by UNSEENEST.
  evidence: Table 4
- id: sari-flat-in-m
  kind: result
  text: SARI gives a perfect text simplification system a coverage of only about 0.45, largely
    independently of the number of references. A system that outputs one of the given references
    scores lower as references are added.
  scope: Bootstrapping on 47 sentences with crowdsourced simplification distributions; MAX-SARI
    reported alongside SARI because multi-reference SARI is not a maximum over single-reference
    scores.
  evidence: Figure 1c
- id: simplification-reranking
  kind: result
  text: 'Under-prediction in text simplification also decreases with more references: the
    least under-predicting model, a neural one, left 50 sentences unchanged with 1 reference
    but only 29 unchanged with 8 references.'
  scope: Oracle re-ranking against MAX-SARI on k-best lists from Moses (k = 100) and the neural
    model of Nisioi et al. (2017) (k = 12); details in Appendix G.
  evidence: Section 4 (details in Appendix G)
- id: context-lcb-argument
  kind: context
  text: Choshen and Abend (2018) established that low reference coverage in grammatical error
    correction and text simplification is not a constant-factor under-estimation but an incentive
    structure that rewards systems for not correcting.
  scope: Argued for GEC on NUCLE and for text simplification with SARI, as of ACL 2018; earlier
    work on low coverage (Bryant and Ng 2015; Sakaguchi et al. 2016) proposed re-scaling or
    more references as the remedy.
  evidence: Section 5
- id: context-methodology
  kind: context
  text: Choshen and Abend (2018) contribute two reusable methods to monolingual translation
    evaluation. The first scores a hypothetical perfect system by bootstrapping to expose
    a measure's bias; the second estimates per-sentence distributions of valid outputs.
  scope: Demonstrated on GEC (M2, GLEU, sentence accuracy) and text simplification (SARI);
    the distribution estimate relies on UNSEENEST and, in the paper's own experiments, on
    short sentences of at most 15 words to keep estimation reliable.
  evidence: Section 5
- id: context-correlation-blindspot
  kind: context
  text: Choshen and Abend (2018) argue that metric validation by correlation with human rankings
    of system outputs cannot detect a metric's tendency to reward under-correction, because
    all ranked systems under-correct similarly.
  scope: An argument about GEC metric validation studies of the Grundkiewicz et al. (2015)
    type, presented in discussion rather than tested by an experiment.
  evidence: Section 5
qa:
- q:
  - Why doesn't adding more reference corrections fix GEC evaluation?
  - Does increasing the number of references solve low coverage bias in grammatical error
    correction?
  - How many references would GEC evaluation need to be reliable?
  answers:
  - long-tail-corrections
  - diminishing-returns-references
  - perfect-system-low-score
- q:
  - How many valid ways are there to correct an ungrammatical English sentence?
  - What does the distribution of valid grammatical corrections per sentence look like?
  - Are rare crowdsourced corrections of learner sentences just noise?
  answers:
  - long-tail-corrections
  - rare-corrections-valid
- q:
  - What score does a perfect grammatical error correction system get under M2 with 2 references?
  - How much does M2 or GLEU under-estimate a system that always produces a valid correction?
  - Can a GEC system score higher than a human corrector on standard metrics?
  answers:
  - perfect-system-low-score
  - systems-beat-perfect-system
- q:
  - Can low coverage bias be removed by re-scaling scores by inter-annotator agreement?
  - Is Ratio Scoring enough to correct for too few GEC references?
  - Why is rescaling GEC scores by a human upper bound not a valid fix?
  answers:
  - systems-beat-perfect-system
  - context-lcb-argument
- q:
  - Why do grammatical error correction systems make so few edits?
  - Do GEC systems change the input less than human annotators do?
  - What evidence is there that GEC systems under-correct?
  answers:
  - systems-undercorrect
  - more-references-more-correction
- q:
  - Which kinds of grammatical errors do automatic correction systems tend to skip?
  - Are open-class errors corrected less often than closed-class errors by GEC systems?
  - Do systems avoid verb and preposition selection errors because they are rare?
  answers:
  - open-class-undercorrected
  - type-frequency-not-explanation
- q:
  - Does the low coverage problem also affect text simplification evaluation?
  - How many valid simplifications does a sentence have?
  - Is SARI biased by having too few reference simplifications?
  answers:
  - simplification-long-tail
  - sari-flat-in-m
  - simplification-reranking
- q:
  - Are SARI scores comparable across datasets with different numbers of references?
  - Does SARI improve when more reference simplifications are added?
  - Why is MAX-SARI reported instead of SARI in multi-reference experiments?
  answers:
  - sari-flat-in-m
- q:
  - What should I read about the limits of reference-based evaluation in grammatical error
    correction?
  - Which paper showed that GEC metrics reward systems for not correcting?
  - Where should I start reading about low coverage bias in text-to-text evaluation?
  - What work established that too few references biases monolingual translation evaluation?
  answers:
  - context-lcb-argument
  - context-methodology
- q:
  - How can I measure whether an evaluation metric is biased by its reference set?
  - Is there a method for estimating how many valid outputs a source sentence has?
  - What methodology exists for evaluating GEC evaluation measures themselves?
  answers:
  - context-methodology
  - long-tail-corrections
- q:
  - Is correlation with human judgments enough to validate a GEC metric?
  - Why can metric validation studies miss a metric's bias toward under-correction?
  - Do human-correlation experiments detect that a GEC measure rewards leaving the source
    unchanged?
  answers:
  - context-correlation-blindspot
- q:
  - Does training or tuning against more references make a corrector edit more?
  - What happens to under-correction when oracle re-ranking uses more references?
  - Is there experimental evidence that low reference coverage causes under-correction?
  answers:
  - more-references-more-correction
  - simplification-reranking
misreadings:
- Reporting that some systems outperform a perfect system with 2 references is not a claim
  that those systems are better than human correctors; it is evidence that the metric is broken,
  since a perfect system by construction always produces a valid correction.
- The finding is not that GEC references are noisy or badly annotated. Even the rarest crowdsourced
  corrections were judged valid 78% of the time, so the long tail is genuine variation among
  valid corrections, not annotation error.
- 'Showing that more references reduce under-correction is not an endorsement of collecting
  more references as the remedy: expected accuracy gains only 0.004 per extra reference at
  M = 20, so no feasible number of references removes the bias.'
- The result does not say GLEU is immune to low coverage bias. GLEU runs only about 2% above
  M2 and saturates with the number of references in the same way.
- Choshen and Abend (2018) propose no replacement metric for M2, GLEU or SARI; the contribution
  is a diagnosis, a bootstrapping methodology for scoring perfect systems, and a method for
  estimating the distribution of valid outputs.
- Preferring fluency-oriented references does not mitigate the problem — emphasising fluency
  over grammaticality enlarges the set of valid corrections and so compounds low coverage.
links_extra:
  code: https://github.com/borgr/IBGEC
  anthology: https://aclanthology.org/P18-1059/
  pdf: https://aclanthology.org/P18-1059.pdf
---
