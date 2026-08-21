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
- ask:
    plain: can you tell whether a grammar-correction scoring measure is any good without paying
      people to rank outputs?
    jargon: how can GEC metrics be validated without correlation against human system rankings?
    task: how do I check that my grammatical error correction evaluation measure tracks real
      correction quality?
    practitioner: should I trust an automatic validation of my GEC metric instead of running
      a human ranking study?
  answered_by:
  - maege-context
  - chr-maege-divergence
- ask:
    plain: is the standard scorer used in grammar correction shared tasks a reliable way to
      rank systems?
    jargon: how well does M² correlate with corpus-level GEC quality, and how well does it
      order same-sentence corrections?
    task: can I use M² to decide which of my grammar correction systems is better overall?
    practitioner: my leaderboard uses the M² scorer -- is that enough to pick the best system?
  answered_by:
  - m2-corpus-level-poor
  - gleu-vs-m2-inverse
- ask:
    plain: which way of scoring grammar corrections lines up best with how good the corrections
      actually are?
    jargon: does a reference-less grammaticality metric such as LT correlate better with induced
      quality rankings than reference-based GEC metrics like GLEU and M²?
    task: which scorer should I report if I want corpus-level rankings of grammar correction
      systems to be trustworthy?
    practitioner: is it worth adding a grammaticality checker score alongside GLEU when I
      evaluate my corrector?
  answered_by:
  - lt-best-corpus
  - sentence-level-low
- ask:
    plain: do grammar-correction scores ever go down when a mistake is genuinely fixed?
    jargon: which NUCLE edit types receive negative average score changes under GEC metrics
      such as GLEU, M² and SARI?
    task: how do I find out whether my evaluation metric discourages fixing particular kinds
      of grammatical errors?
    practitioner: if my system fixes verb modality and possessive errors, will the usual GEC
      metrics reward me for it?
  answered_by:
  - edit-types-penalized
  - gleu-penalizes-most
- ask:
    plain: how much do people actually agree when they rank grammar correction output by quality?
    jargon: do the GJG15 and NSPT15 human judgment sets yield consistent metric correlations
      for GEC?
    task: which set of human rankings should I correlate my grammar correction metric against?
    practitioner: can I rely on a published human-ranking correlation to justify the metric
      I picked for grammar correction?
  answered_by:
  - human-ranking-disagreement
  - chr-protocol-proposal
- ask:
    plain: does judging scorers on systems that barely change the input make a different scorer
      look best?
    jargon: how do corpus-level correlations for SARI, MAX-SARI and M² change when the source
      is the uncorrected original sentence rather than a partially corrected one?
    task: how should I evaluate metrics if the grammar correction systems I compare are conservative
      and under-correct?
    practitioner: my corrector changes very little of the input -- which metric ranks systems
      like mine sensibly?
  answered_by:
  - precision-oriented-source
  - chr-maege-divergence
- ask:
    plain: is there a grammar-correction score that becomes impossible to compute on a normal
      test set?
    jargon: is I-Measure tractable on NUCLE given the number of generated references per sentence?
    task: can I run I-Measure over a multi-reference grammatical error correction test set
      in reasonable compute time?
    practitioner: should I budget compute for I-Measure when scoring my grammar correction
      system on CoNLL data?
  answered_by:
  - imeasure-intractable
- ask:
    plain: what should I read first about how grammar correction systems are evaluated?
    jargon: which work questioned validating GEC metrics by correlation with human system
      rankings?
    task: where do I start if I need to choose or defend an evaluation methodology for grammatical
      error correction?
    practitioner: is there a paper I can cite when arguing that our grammar correction evaluation
      setup needs changing?
  answered_by:
  - maege-context
  - chr-protocol-proposal
- ask:
    plain: can automatic grammar-correction scores tell which of two corrections of the same
      sentence is better?
    jargon: what sentence-level Pearson r and Kendall tau do GEC metrics such as iBLEU and
      GLEU reach against induced quality orderings?
    task: can I use a GEC metric to score individual sentences rather than a whole corpus?
    practitioner: I want per-sentence quality scores from my grammar corrector -- will any
      existing metric give me that?
  answered_by:
  - sentence-level-low
  - gleu-vs-m2-inverse
- ask:
    plain: how should future studies report agreement between grammar-correction scores and
      human judgments?
    jargon: what protocol should GEC correlation-with-human-ranking studies follow regarding
      judgment sets and the sentence subset used for corpus-level ranking?
    task: how do I set up a human-ranking correlation study for a new grammar correction metric
      so the numbers mean something?
    practitioner: if I run a human evaluation to validate my GEC metric, which judgments and
      which sentences should I score on?
  answered_by:
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
