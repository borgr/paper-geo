---
key: choshen2022some
one_liner: Native English speakers rated how much errors in 58K NUCLE sentences bothered them,
  and a linear regression from per-type error counts to those ratings gives an importance
  weight for every error type in the NUCLE, ERRANT and SErCl typologies.
claims:
- id: frequency-vs-importance
  kind: result
  text: Grammatical error types that human readers find most bothering are not the frequent
    ones. Determiner errors are extremely common in NUCLE yet rank low in human importance,
    while orthography errors are easy for systems to correct and rank among the most bothering.
  scope: Crowd ratings by US-based self-reported native English speakers on NUCLE sentences
    of at least 7 words; importance inferred by linear regression on error-type counts, assuming
    additive, context-independent contributions.
  evidence: Section 6, with rankings in Figures 2-4
- id: verb-orthography-top
  kind: result
  text: Verb inflection and verb errors in general rank among the most bothering error types
    to native English readers across the NUCLE, ERRANT and SErCl typologies. Orthography errors,
    unnecessarily added tokens and wrong determiners also rank high.
  scope: NUCLE sentences rated by crowd annotators; error bars in the rank figures overlap,
    so neighbouring types are not significantly separated and only the easy/medium/hard groupings
    are clear.
  evidence: Section 5, Figures 2, 3 and 4
- id: low-importance-types
  kind: result
  text: Missing tokens, inflection and morphology errors rank among the least bothering grammatical
    error types to native English readers, as do several determiner-related error types.
  scope: NUCLE sentences, crowd ratings from US native English speakers; rank differences
    between adjacent types are within the reported standard-deviation error bars.
  evidence: Section 5, Figures 2, 3 and 4
- id: metrics-mismatch
  kind: context
  text: Standard GEC metrics such as M^2 count corrected errors regardless of type, so systems
    and their training loss are implicitly weighted by error frequency rather than by what
    readers care about. The importance-weighting question this opens is what "Some Grammatical
    Errors are Frequent, Others are Important" measures.
  scope: Argument concerns English GEC evaluation as of 2022 and one NUCLE-based measurement;
    prior work had studied which error types are hardest to correct rather than which matter
    most to readers.
  evidence: Sections 1, 2 and 6
- id: method-transfers-typologies
  kind: context
  text: Annotating whole sentences for how much their errors bother readers, then regressing
    the ratings on per-type error counts, yields importance weights for any error typology
    without collecting new annotations for it.
  scope: Shown for the manual NUCLE typology and the automatic ERRANT and SErCl typologies
    on one corpus; the linear model assumes additive type contributions.
  evidence: Section 4
- id: annotation-scale
  kind: result
  text: 58K NUCLE sentences were sent for crowd annotation, roughly 2 ratings per erroneous
    sentence plus about 8.7K annotations of grammatical sentences. The whole corpus was annotated
    in under 2 days at 0.5$ per 100-sentence batch.
  scope: Amazon Mechanical Turk workers from the United States with above 95% acceptance rate
    who reported being English natives; NUCLE contains about 59K sentences before filtering
    ones under 7 words and non-English-looking ones.
  evidence: Sections 3 and 3.1
- id: bother-not-grammaticality
  kind: result
  text: Annotators moved a slider from 1 to 100 to say how much the English mistakes in a
    text bother them, rather than judging grammaticality. Grammatical knowledge in non-professionals
    is implicit and often judged unimportant.
  scope: Adapts the Direct Assessment fluency protocol; other wordings, such as framing the
    sentence in an academic or email context, could yield somewhat different importance rankings.
  evidence: Section 3
- id: filtering
  kind: result
  text: Quality filtering of the NUCLE bother ratings removed about 5% of annotators for spending
    under 350 seconds on 100 sentences. About 10% of annotators were removed overall, once
    per-annotator t-tests on error-free control sentences and negative correlation with other
    annotators were added.
  scope: 15 error-free, 70 erroneous and 15 repeated sentences per 100-sentence batch; correlations
    computed only on repeated sentences with at least 15 responses, dropping annotators below
    -0.4.
  evidence: Section 3.2, Figure 1
- id: robust-to-filtering
  kind: result
  text: Harsher annotator-filtering thresholds on the NUCLE bother ratings produced similar
    error-type importance rankings with higher variance. Most annotators removed by the 350-second
    time or t-test filters also correlated negatively with other annotators.
  scope: Robustness checked by varying the time threshold and the t-test p-value on the same
    NUCLE annotation pass; noise remains in the retained annotations and adjacent type ranks
    stay statistically indistinguishable.
  evidence: Section 3.2, discussed with results in Section 5
- id: weighted-training
  kind: result
  text: Weighting training spans by the estimated importance of each error type improved a
    GEC network on the targeted error types more than on others or the baseline. The margin
    was not large.
  scope: Initial study reported without tables or figures; non-error tokens received a constant
    weight, and no full system comparison or metric numbers are given.
  evidence: Section 6
qa:
- q:
  - Are all grammatical error types equally important to correct?
  - Do readers care more about frequent grammatical errors?
  - Which grammatical errors bother native English speakers most?
  answers:
  - frequency-vs-importance
  - verb-orthography-top
  - low-importance-types
- q:
  - Which error types are least annoying to readers of learner English?
  - What grammatical errors can be deprioritised in error correction?
  answers:
  - low-importance-types
- q:
  - What should I read about weighting error types in grammatical error correction evaluation?
  - Is there work arguing GEC metrics like M^2 treat all errors equally and shouldn't?
  - What paper questions counting corrected errors as the GEC evaluation target?
  answers:
  - metrics-mismatch
  - frequency-vs-importance
- q:
  - How can importance weights be estimated for an error typology without new annotation?
  - Can sentence-level human ratings be turned into per-error-type importance scores?
  - How were importance weights computed for NUCLE, ERRANT and SErCl types?
  answers:
  - method-transfers-typologies
  - bother-not-grammaticality
- q:
  - How much crowd annotation was collected on NUCLE for error importance?
  - How many sentences and annotators went into rating how much errors bother readers?
  - What did the Mechanical Turk annotation of NUCLE cost and how long did it take?
  answers:
  - annotation-scale
  - bother-not-grammaticality
- q:
  - How were low-quality crowd annotators of grammatical error ratings filtered out?
  - What quality controls were used in the NUCLE bother-rating annotation?
  - How many crowdworkers were removed by the filtering procedure?
  answers:
  - filtering
  - robust-to-filtering
- q:
  - Are the error-importance rankings robust to how aggressively annotators are filtered?
  - Do stricter annotator filters change which grammatical errors rank as important?
  answers:
  - robust-to-filtering
  - verb-orthography-top
- q:
  - Does training a GEC model with error-importance weights help?
  - Has anyone tried weighting the GEC training loss by how much each error type bothers readers?
  answers:
  - weighted-training
- q:
  - Why ask annotators how much mistakes bother them instead of asking about grammaticality?
  - What question wording was used to elicit grammatical error importance judgements?
  answers:
  - bother-not-grammaticality
misreadings:
- 'Importance ranks of grammatical error types are not difficulty ranks: orthography errors
  are easy for systems to correct yet rank as highly bothering, and determiner errors are
  easy and frequent yet rank low.'
- The rank figures do not establish that every error type differs significantly from its neighbours;
  error bars overlap, and only the coarse split into easy, medium and hard types is clear.
- Importance weights are extrapolated from sentence-level ratings by linear regression on
  error-type counts, not obtained by asking annotators to judge error types directly.
- A negative regression weight for an error type does not mean annotators viewed that error
  positively, since the regression includes a baseline term and the type may simply be less
  severe than others.
- The results describe what bothers readers of erroneous text, not what writers or language
  learners most need corrected, and assume error importance is independent of sentence context.
terminology:
  bother score: A crowd annotator's response on a 1-100 slider to the statement that the English
    mistakes in a text bother them, normalized per annotator to a standard normal Z-score.
  importance weight: The coefficient assigned to an error type by a linear regression predicting
    a sentence's human bother score from the counts of each error type in that sentence.
  SErCl: A fine-grained, syntax-based typology of grammatical errors with automatic extraction
    for most languages, dependent only on a part-of-speech tagger.
  SERRANT: A grammatical error typology combining SErCl's broad coverage with ERRANT's interpretable
    rule-based categories.
links_extra:
  code: https://github.com/borgr/GEC_BOTHER
---
