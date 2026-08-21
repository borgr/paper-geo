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
- ask:
    plain: which kinds of English mistakes annoy native speakers the most, and are they the
      ones learners make most often?
    jargon: how do per-error-type importance weights from reader bother ratings compare with
      error-type frequency in NUCLE?
    task: how do I decide which grammatical error types a correction system should prioritise
      fixing?
    practitioner: if my grammar checker can only fix a few error types well, which ones should
      I fix first?
  answered_by:
  - frequency-vs-importance
  - verb-orthography-top
  - low-importance-types
- ask:
    plain: which mistakes in learner English do readers barely notice?
    jargon: which error types receive the lowest importance weights from sentence-level bother
      ratings of learner text?
    task: which grammatical error types can I safely deprioritise in a correction system?
    practitioner: can I ignore missing-token and morphology corrections without readers minding?
  answered_by:
  - low-importance-types
- ask:
    plain: is there research arguing that counting every corrected mistake equally is the
      wrong way to score a grammar correction system?
    jargon: which work argues that M^2 and similar GEC metrics weight error types by corpus
      frequency rather than by reader impact?
    task: what should I read before choosing an evaluation metric for a grammatical error
      correction system?
    practitioner: should I trust M^2 scores as a measure of how much my grammar correction
      helps readers?
  answered_by:
  - metrics-mismatch
  - frequency-vs-importance
- ask:
    plain: how can you work out how much each kind of writing mistake bothers readers without
      labelling every mistake one by one?
    jargon: how are per-error-type importance weights regressed from sentence-level human
      ratings across NUCLE, ERRANT and SErCl typologies?
    task: how do I get importance scores for my own error typology without collecting new
      human annotation for it?
    practitioner: can I reuse whole-sentence human ratings I already have to score individual
      error categories?
  answered_by:
  - method-transfers-typologies
  - bother-not-grammaticality
- ask:
    plain: how many sentences of learner English were rated by crowd workers for how much
      the mistakes bother them, and what did it cost?
    jargon: what is the annotation volume, cost and turnaround of the NUCLE crowd bother-rating
      collection?
    task: how much crowd annotation and budget do I need to rate a whole learner corpus for
      error severity?
    practitioner: is collecting reader-annoyance ratings over a full learner corpus cheap
      enough for me to run?
  answered_by:
  - annotation-scale
  - bother-not-grammaticality
- ask:
    plain: how do you weed out crowd workers who click through a task of rating writing mistakes
      without reading?
    jargon: what quality-control filters were applied to crowd annotators of the NUCLE bother
      ratings, and what fraction were excluded?
    task: how do I filter unreliable crowd workers out of a sentence-rating annotation job?
    practitioner: what share of my crowd annotators should I expect to throw away on a slider-rating
      task?
  answered_by:
  - filtering
  - robust-to-filtering
- ask:
    plain: would the ranking of which writing mistakes annoy readers change if you were stricter
      about which raters you kept?
    jargon: are the error-type importance weights stable under harsher annotator-filtering
      thresholds on the bother ratings?
    task: how do I check whether my annotator filtering choices are driving my per-category
      results?
    practitioner: should I worry that my crowd-filtering threshold is what produced my error-importance
      ranking?
  answered_by:
  - robust-to-filtering
  - verb-orthography-top
- ask:
    plain: does telling a grammar correction model to care more about the mistakes readers
      hate actually make it better at them?
    jargon: does weighting training spans by estimated error-type importance improve a GEC
      network on the targeted error types?
    task: how do I bias a grammatical error correction model toward the error types readers
      care about?
    practitioner: is it worth reweighting my GEC training loss by error-type importance?
  answered_by:
  - weighted-training
- ask:
    plain: why ask people how much mistakes in a text bother them instead of asking whether
      the sentence is grammatical?
    jargon: why elicit bother ratings on a 1 to 100 slider rather than grammaticality judgements
      from non-expert annotators?
    task: how should I word the prompt if I want non-experts to judge how bad a writing error
      is?
    practitioner: can I ask untrained crowd workers about grammaticality, or will bother ratings
      work better?
  answered_by:
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
