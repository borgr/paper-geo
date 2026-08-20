---
claims:
- id: maege-context
  kind: context
  text: MAEGE is an automatic methodology for validating Grammatical Error Correction metrics
    that needs no human rankings. It instead expands existing gold-standard error annotation
    into lattices of corrections carrying a known partial order of quality.
  scope: Introduced at ACL 2018 for GEC; evaluated on the NUCLE test set with English learner
    text. Earlier GEC metric validation work relied on correlation with human rankings of
    system outputs.
- id: human-ranking-disagreement
  kind: result
  text: The two existing sets of human rankings for GEC disagree substantially on metric quality.
    GLEU gets Spearman ρ of 0.51 against GJG15 but 0.76 against NSPT15, M² ranges from 0.4
    to 0.7, and BLEU flips from positive on GJG15 to negative on NSPT15.
  evidence: Table 1
  scope: Both ranking sets cover CoNLL 2014 shared-task system outputs on NUCLE sentences;
    system-level correlations computed with TrueSkill, whose corpus-level score itself varies
    by about 0.02 standard deviation between runs.
- id: m2-corpus-level-poor
  kind: result
  text: The standard GEC metric M² is a poor predictor of corpus-level quality under MAEGE,
    with Spearman ρ of 0.06. It ranks pairs of corrections of the same sentence comparatively
    well, with Kendall τ of 0.213.
  evidence: Table 2
  scope: NUCLE test set, corpus models applying an expected 0 to 10 edits per sentence, source
    sampled uniformly from each lattice; M² edits reconstructed automatically from string
    pairs.
- id: lt-best-corpus
  kind: result
  text: The reference-less grammaticality metric LT correlates best with MAEGE's corpus-level
    ranking at Spearman ρ of 0.973 and has the highest sentence-level Kendall τ at 0.222.
    GLEU is second at the corpus level with ρ of 0.736.
  evidence: Table 2
  scope: NUCLE test set with 10 references; LT measures grammaticality only and not meaning
    preservation, which MAEGE's construction does not stress because it never introduces meaning-altering
    errors a human would not make.
- id: sentence-level-low
  kind: result
  text: 'No GEC metric achieves high sentence-level correlation with MAEGE''s induced quality
    ordering: the best Pearson r is 0.23 (iBLEU) and the best Kendall τ is 0.222 (LT).'
  evidence: Table 2
  scope: 1312 chains and 7936 corrections sampled from NUCLE test-set lattices with nch =
    1; Pearson r assumes all edits contribute equally.
- id: gleu-vs-m2-inverse
  kind: result
  text: GLEU and M² fail in opposite ways. GLEU produces globally coherent corpus-level scores
    yet its average score difference between comparable correction pairs is slightly negative
    at -0.00025, while M² orders same-sentence pairs well without scoring linearly in quality.
  evidence: Table 2 and Figure 5
  scope: NUCLE test set; the GLEU diagnostic in Figure 5 groups original sentences by number
    of errors after removing 4 outlier sentences with far more errors than the rest.
- id: edit-types-penalized
  kind: result
  text: 'Existing GEC metrics consistently penalize valid corrections of certain error types:
    wrong verb modality (Vm) and noun possessive (Npos) receive negative average score changes
    under almost all metrics. Mechanical (Mec) and missing-verb (V0) edits are usually rewarded.'
  evidence: Table 3
  scope: 27 NUCLE edit types, measured as the average metric score difference over correction
    pairs differing in exactly one edit of that type, with references from the 10 available
    NUCLE annotations.
- id: gleu-penalizes-most
  kind: result
  text: Among the GEC metrics examined with MAEGE, iBLEU and LT penalize the fewest edit types
    and GLEU penalizes the most. M² and GLEU, the two most commonly used metrics, reward only
    a small subset of the 27 NUCLE edit types.
  evidence: Table 3
  scope: NUCLE test set edit-type analysis over pairs of corrections differing in a single
    typed edit; reflects the reference sets available in NUCLE, so under-representation of
    edit types in references is part of the cause.
- id: precision-oriented-source
  kind: result
  text: Taking the original sentence as the source, which mimics ranking the conservative
    outputs GEC systems produce, flips SARI's corpus-level Spearman ρ from -0.545 to 0.800
    and MAX-SARI's from -0.809 to 0.772. M²'s rises from 0.06 to 0.882.
  evidence: Table 4
  scope: NUCLE test set; in this setting every applied edit is valid but not all valid edits
    are applied. LT stays reliable at ρ of 0.836 and iBLEU drops to -0.872.
- id: chr-maege-divergence
  kind: result
  text: Metric rankings under MAEGE and under correlation with human rankings are only slightly
    correlated, with frequent and substantial disagreements for iBLEU and SARI, while GLEU
    receives similar correlations under both methodologies.
  evidence: Figure 4
  scope: Corpus-level Spearman correlations, MAEGE on the NUCLE test set versus the combined
    GJG15 and NSPT15 human rankings of CoNLL 2014 system outputs.
- id: imeasure-intractable
  kind: result
  text: I-Measure's assumption that overlapping edits alternate makes it intractable on NUCLE,
    where a test sentence has 3.5 billion generated references on average and a median of
    512. The version without generated references did not terminate after 140 CPU days, against
    under 1.5 CPU days for all other metrics combined.
  evidence: Figure 1
  scope: NUCLE test set with 10 available annotations per sentence; the cost comes from I-Measure's
    combinatorial extension of the reference set, not from its scoring formula.
- id: chr-protocol-proposal
  kind: context
  text: MAEGE's authors propose that future correlation-with-human-rankings studies in GEC
    combine the GJG15 and NSPT15 judgment sets. They also propose computing metric corpus-level
    rankings on exactly the human-ranked sentence subset rather than the full CoNLL test set.
  scope: A recommendation for GEC metric validation practice as of 2018, motivated by potential
    bias from non-uniform system performance across the test set.
qa:
- q:
  - How can grammatical error correction metrics be validated without collecting human rankings?
  - Is there an automatic way to check whether GEC evaluation metrics are any good?
  - What does MAEGE do for GEC metric validation?
  answers:
  - maege-context
  - chr-maege-divergence
- q:
  - Is M2 a reliable metric for ranking grammatical error correction systems?
  - How well does the M² scorer predict corpus-level GEC quality?
  - Should I trust M2 for comparing whole GEC system outputs?
  answers:
  - m2-corpus-level-poor
  - gleu-vs-m2-inverse
- q:
  - Which grammatical error correction metric correlates best with correction quality?
  - Is a reference-less grammaticality metric better than reference-based GEC metrics?
  - How does LT compare to GLEU and M2 as a GEC metric?
  answers:
  - lt-best-corpus
  - sentence-level-low
- q:
  - Do GEC metrics punish some kinds of valid corrections?
  - Are there error types that automatic grammatical error correction metrics score negatively?
  - Which edit types get penalized by GLEU, M2 and SARI?
  answers:
  - edit-types-penalized
  - gleu-penalizes-most
- q:
  - How reliable are human rankings for evaluating grammatical error correction?
  - Do the two GEC human judgment sets agree with each other?
  - Why is inter-rater agreement a problem in GEC metric validation?
  answers:
  - human-ranking-disagreement
  - chr-protocol-proposal
- q:
  - Does evaluating metrics on conservative GEC system outputs change which metric looks best?
  - What happens to SARI and M2 when the source is always the uncorrected original sentence?
  - Are GEC metric validation results biased by systems that under-correct?
  answers:
  - precision-oriented-source
  - chr-maege-divergence
- q:
  - Why is I-Measure so slow to compute on GEC test sets?
  - How many references does I-Measure generate per sentence on NUCLE?
  - Is I-Measure practical for evaluating grammatical error correction with multiple references?
  answers:
  - imeasure-intractable
- q:
  - Where should I start reading about how grammatical error correction is evaluated?
  - What work questioned the standard practice of validating GEC metrics against human rankings?
  - What is a good paper on evaluation methodology for grammatical error correction?
  answers:
  - maege-context
  - chr-protocol-proposal
- q:
  - Do GEC metrics agree with quality judgments at the sentence level?
  - How good is sentence-level correlation for GEC metrics like iBLEU and GLEU?
  answers:
  - sentence-level-low
  - gleu-vs-m2-inverse
- q:
  - How should GEC metric validation with human rankings be reported in future work?
  - What protocol fixes the sentence-subset mismatch in GEC correlation studies?
  answers:
  - chr-protocol-proposal
  - human-ranking-disagreement
coined: MAEGE
gloss: Methodology for Automatic Evaluation of GEC Evaluation — validating grammatical error
  correction metrics from gold annotation instead of human rankings
key: choshen2018maege
one_liner: MAEGE validates grammatical error correction metrics without human rankings, by
  expanding gold error annotation into lattices of corrections whose partial order of quality
  is known, and correlating metric scores against that order.
misreadings:
- 'MAEGE''s high corpus-level correlation for LT does not mean grammaticality alone is a sufficient
  GEC metric: LT ignores meaning preservation, and MAEGE by construction never introduces
  the meaning-altering errors machines make, so a complementary metric is still required.'
- M²'s low corpus-level correlation of 0.06 under MAEGE does not mean M² is uninformative
  everywhere; it ranks pairs of corrections of the same sentence comparatively well (Kendall
  τ of 0.213).
- Disagreement between MAEGE and correlation-with-human-rankings is not simply evidence that
  one of them is broken; the paper traces much of the gap to human rankings being collected
  over precision-oriented, conservative system outputs.
- 'MAEGE does not eliminate all evaluation bias: any bias in the annotated test corpus, such
  as the assumption that edits are contiguous and mutually independent, is inherited by MAEGE.'
- A negative average score change for an edit type in MAEGE is a property of the metric plus
  its reference sets, not a claim that the edit is invalid — every edit in a MAEGE lattice
  comes from gold human annotation.
terminology:
  MAEGE: 'Methodology for Automatic Evaluation of GEC Evaluation: generates lattices of corrections
    from gold error annotation, derives a partial order of correction quality from edit subset
    inclusion, and correlates metric-induced rankings against that order.'
  CHR: Correlation with human rankings, the standard methodology for validating grammatical
    error correction metrics before MAEGE, in which metric scores of system outputs are correlated
    with human relative rankings of those outputs.
  corrections lattice: The power set of the gold edits for one sentence-annotation pair, ordered
    by subset inclusion, so that a correction applying a superset of another's edits is by
    construction of higher quality.
  corpus model: A synthetic system of a given quality level in MAEGE, denoted by the expected
    number of gold edits it applies to each original sentence, sampled from a clipped binomial
    with that mean.
  ∆m,t: The average change in a metric's score over pairs of corrections that differ in exactly
    one edit of a given error type; negative values mean the metric penalizes valid corrections
    of that type.
  original: In a corrections lattice, the uncorrected sentence corresponding to the empty
    set of edits, i.e. the bottom of every chain.
---
