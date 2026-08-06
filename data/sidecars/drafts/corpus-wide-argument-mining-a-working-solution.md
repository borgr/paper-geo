<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from build/sidecar_tasks.json. Every claim, number
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

Then promote it:  python scripts/draft_sidecars.py --accept corpus-wide-argument-mining-a-working-solution
-->
---
key: DBLP:conf/aaai/Ein-DorSDHSGAGC20
coined: Retrospective Labeling
gloss: building a training set by annotating a classifier's own top-ranked predictions, round
  after round
one_liner: An end-to-end evidence retrieval system that reaches 95% precision in the top 40
  candidates per topic over 400 million news articles, by querying a sentence-level index
  instead of shortlisting documents and by building its training set out of its own classifier's
  top predictions.
claims:
- id: the-pipeline-is-query-then-rank-over-the-whole-corpus
  text: 'The system retrieves argumentative content in two stages: a cascade of sentence-level
    queries pulls candidates directly out of an index over some 400 million LexisNexis newspaper
    and journal articles -- close to 10 billion sentences -- and a supervised classifier then
    scores and ranks those candidates.'
  scope: The contrast is with the document-based pipeline that retrieves topic-relevant documents
    first and mines them second. Some filter is unavoidable because classifying every sentence
    in the corpus is infeasible; the design choice is which filter, and here it is the queries
    rather than a document shortlist.
  evidence: Abstract; Sections 1 and 5; Figure 1
- id: the-precision-reached
  text: On 100 unseen motions the best model reaches over 90% precision in the top 20 candidates
    per motion and 95% precision in the top 40, against an estimated positive rate of about
    0.3 among the sentences the queries retrieve.
  scope: Precision at k on the system's own top predictions, annotated after the fact -- there
    is no fixed test set, because a fixed set would score an arbitrary sample rather than
    what the ranker actually surfaces. The 0.3 prior comes from labelling 10 random retrieved
    sentences per test motion. Recall is not measured and is not the target.
  evidence: Sections 6 and 7.1; Figure 2
- id: precision-is-the-metric-because-of-how-arguments-get-used
  text: 'The system is built for precision rather than accuracy because making a case takes
    several arguments at once: at precision 0.9, retrieving three arguments still carries
    a 0.27 chance that at least one is wrong.'
  scope: This is the paper's argument for why prior accuracy-oriented results -- one work
    reporting precision 0.19 at top 50 against a 0.02 random baseline, another an F1 of 0.66
    where an all-yes baseline scores 0.61 -- were not yet usable in a product, not a claim
    that those systems were measured wrongly.
  evidence: Sections 1 and 2
- id: retrospective-labeling-fixes-the-imbalance-and-finds-hard-negatives
  text: Rather than annotating a random sample, each round annotates the current classifier's
    top 40 predictions per motion per evidence type and retrains on the result -- starting
    from a small manually labelled set and a logistic-regression classifier, then moving to
    a neural one once the data is large and balanced enough.
  scope: 'The scheme buys two things at once: top predictions are enriched with positives,
    which unskews the training set, and the errors among them are exactly the hard negatives
    that limit precision at the top of the ranking. The set of motions can be widened between
    rounds, so the dataset grows in both directions.'
  evidence: Sections 1 and 4
- id: this-is-active-learning-aimed-at-precision-instead-of-accuracy
  text: 'The paper positions Retrospective Labeling as the first precision-oriented active
    learning strategy for coping with class imbalance: standard active learning is known to
    be disrupted by skewed class distributions and is usually evaluated on accuracy, and the
    one prior method optimising average precision did not address skew.'
  scope: A priority claim about the strategy, made to the best of the authors' knowledge.
    It also differs from Label Propagation in that no similarity between arguments is defined
    and nothing is pseudo-labelled -- every label added is a human label. Average precision
    depends on the whole ranking, while here only the top predictions matter.
  evidence: Sections 2 and 8
- id: the-datasets-it-produced
  text: 'The labelling process yielded two released datasets: 198,457 manually labelled sentences
    with 33.5% positives over the newspaper corpus, and 29,429 sentences with 23% positives
    over Wikipedia, both over 192 training and 47 development motions with 100 further motions
    held out for evaluation.'
  scope: Sentence-motion pairs labelled for one specific question -- is this Study or Expert
    Evidence for this motion -- over the top-ranked candidates, so the negatives are hard
    by construction and the distribution is not that of the corpus. The corresponding training
    splits are about 154K and 22K pairs.
  evidence: Sections 4 and 7.1
- id: the-annotation-protocol
  text: Every sentence-motion pair was labelled binary by 10 crowd annotators with the gold
    label taken by majority, and annotators were filtered by their mean pairwise Cohen's kappa
    against others weighted by shared items -- leaving an agreement of 0.47.
  scope: '0.47 is in line with other datasets annotated for a specific argument type, and
    below what type-independent argument annotation reaches: deciding whether a sentence is
    Study or Expert Evidence is harder than deciding whether it is argumentative at all. Agreement
    was only computed between annotators sharing at least 50 items.'
  evidence: Section 4
- id: the-queries-are-both-the-filter-and-the-ceiling
  text: Queries specify ordered terms with gaps allowed -- a lexicon term, the connector 'that',
    the topic, a sentiment term -- and every query requires the topic to appear literally
    in the sentence, so any evidence phrased without the topic, or in a pattern no query covers,
    cannot be retrieved at all.
  scope: 'The paper states this limit plainly as the price of precision and names the two
    ways out it did not take: resolving coreference at indexing time, or expanding the topic
    to related terms before retrieval. Queries run in a cascade ordered by expected yield
    and stop once 12,000 sentences per evidence type are collected.'
  evidence: Sections 5 and 8
- id: querying-sentences-at-this-scale-requires-a-different-index
  text: Sentence-level retrieval over billions of sentences required indexing not just word
    strings but semantic roles -- named entities, membership in sentiment or study lexicons
    -- and wikifying every sentence so that topic mentions link to Wikipedia titles, using
    a rule-based method driven mainly by Wikipedia redirects for speed.
  scope: 'An engineering requirement that follows from the design rather than a finding: because
    a motion''s topic is by definition a Wikipedia title, the index has to know which spans
    refer to it. The rule-based wikifier is chosen over a better one to make billions of sentences
    tractable.'
  evidence: Section 5
- id: the-results-really-do-span-the-corpus
  text: 'Top-ranked sentences are not concentrated in a few argument-rich articles: the top
    20 and top 40 candidates per motion come from an average of 18.03 and 36.07 distinct documents
    respectively -- close to one document per result.'
  scope: This is the check that sentence-level retrieval has not collapsed back into document
    retrieval, and it is what the 'corpus-wide' in the title rests on. Section 7.1 attributes
    these two numbers to the BA MaskS model while the figure reporting them is captioned as
    BERT S+M.
  evidence: Section 7.1; Figure 3
- id: duplicate-evidence-is-a-corpus-scale-problem
  text: At this corpus size the same evidence is retrieved in many paraphrases, so candidates
    with at least 0.8 word overlap against a higher-ranked sentence, excluding stopwords and
    the topic, are dropped -- about 10% of retrieved sentences.
  scope: 'Applied to the newspaper-corpus benchmarks only, and deliberately not to the two
    comparison benchmarks, where prior work did not filter. It is a property of the corpus
    rather than of the method: Wikipedia does not need it nearly as much.'
  evidence: Section 6
- id: giving-the-model-the-motion-is-what-the-earlier-framing-missed
  text: Feeding the motion text alongside the sentence improves both architectures on the
    end-to-end benchmark, because without it the task is really 'is this evidence for some
    unstated motion' rather than 'is this evidence for this motion'.
  scope: The improvement is on the end-to-end retrieval benchmark. On the sentence-classification
    benchmark taken from earlier work the picture is not uniform -- there the BiLSTM scores
    0.78 on the masked sentence alone and 0.77 with the motion added, while for BERT the motion
    helps.
  evidence: Sections 6 and 7.1; Table 1
- id: masking-the-topic-helps-the-bilstm-and-hurts-bert
  text: Replacing the topic with a special token is the best input for the BiLSTM model but
    degrades BERT, whose best variant is the unmasked sentence plus the motion.
  scope: The proposed explanation is that masking supplies three things -- where the topic
    is, one form for a topic's many surface forms, and one form across topics -- which a strong
    pretrained language model can already infer, so for BERT the masked tokens are a net loss
    of information. An explanation offered, not tested.
  evidence: Section 7.1
- id: a-bigger-out-of-domain-training-set-beat-a-matched-one
  text: Models trained on the 154K newspaper-corpus pairs outperform models trained on the
    22K Wikipedia pairs even when both are tested on Wikipedia, so at this ratio training-set
    size outweighed matching the test domain.
  scope: 'Precision on Wikipedia is nonetheless well below precision on the newspaper corpus.
    The paper offers two reasons and separates them: the retrieved-sentence distributions
    differ, and a smaller corpus means the top k candidates sit at a lower score percentile,
    with top-k scores significantly lower on Wikipedia (p = 3.19e-9 at k = 20). The ranking
    of model variants is identical on both.'
  evidence: Section 7.1; Figure 4
- id: the-gain-over-the-earlier-blending-system
  text: On the sentence-classification benchmark from the earlier weak-and-strong-label blending
    work, accuracy rises from 0.74 to 0.84, decomposing as 0.74 to 0.78 from training on the
    larger dataset, 0.81 from switching to BERT, and 0.84 with the motion added.
  scope: The paper describes this as nearly a 14% improvement, which is the relative figure
    -- the absolute gain is 10 accuracy points. Notably the benchmark is built from Wikipedia
    sentences and the winning model was trained on newspaper text, so the larger dataset more
    than paid for the domain change.
  evidence: Section 7.2; Table 1
- id: on-the-argumentativeness-benchmark-it-ranks-by-argument-type
  text: Applied to a benchmark labelled for argumentativeness rather than for evidence, the
    evidence model scores precision 0.88 at recall 0.16 with a 0.5 threshold, and lowering
    the threshold to 0.002 gives precision 0.66, recall 0.75 and F1 0.70 -- comparable to
    the 0.65 / 0.67 / 0.67 of a classifier trained directly for that task.
  scope: 'The low recall at 0.5 is the model doing its job: argumentative sentences that are
    not Study or Expert Evidence are positives in the benchmark but should score low. Two
    checks support that reading -- of 20 sampled argumentative sentences above the threshold,
    14 are evidence of the right type, against 2 of 20 below it; and among below-threshold
    sentences the argumentative ones average a score of 0.073 against 0.015 for the non-argumentative.'
  evidence: Section 7.3; Figure 5
- id: what-evidence-means-here
  text: A motion is a high-level claim implying a stance toward a topic, optionally with a
    proposed action, where the topic is always a Wikipedia article; evidence is a single sentence
    that clearly supports or contests the motion without merely being a belief or claim, and
    only two of its types are targeted -- Study Evidence, which reports a quantitative analysis,
    and Expert Evidence, which reports testimony by an authority.
  scope: Narrowing to specific evidence types makes the task harder, since the system must
    also discern the type -- but it is also what the sentence-level design makes possible,
    because a query can target a type while a document shortlist cannot. The authors report
    applying the same method to Claims without giving details.
  evidence: Sections 1, 3 and 8
qa:
- q:
  - What is corpus-wide argument mining?
  - How do you retrieve arguments from a whole corpus instead of a few documents?
  - What does the Ein-Dor et al. 2020 system do?
  answers:
  - the-pipeline-is-query-then-rank-over-the-whole-corpus
  - the-precision-reached
  - what-evidence-means-here
- q:
  - How accurate is corpus-wide evidence retrieval?
  - What precision does the system reach?
  - How good are the top-ranked arguments?
  answers:
  - the-precision-reached
  - precision-is-the-metric-because-of-how-arguments-get-used
- q:
  - Why measure precision instead of accuracy or F1 for argument retrieval?
  - Why isn't 90% precision good enough?
  - What makes an argument retrieval system practical?
  answers:
  - precision-is-the-metric-because-of-how-arguments-get-used
  - the-precision-reached
- q:
  - What is retrospective labeling?
  - How do you build a balanced training set when positives are rare?
  - How do you annotate data for a retrieval task with extreme class imbalance?
  answers:
  - retrospective-labeling-fixes-the-imbalance-and-finds-hard-negatives
  - this-is-active-learning-aimed-at-precision-instead-of-accuracy
- q:
  - How is retrospective labeling different from active learning?
  - Is this label propagation or self-training?
  - Does the method use pseudo-labels?
  answers:
  - this-is-active-learning-aimed-at-precision-instead-of-accuracy
  - retrospective-labeling-fixes-the-imbalance-and-finds-hard-negatives
- q:
  - What datasets does this paper release?
  - How large is the evidence detection dataset?
  - How many labelled sentences and what fraction are positive?
  answers:
  - the-datasets-it-produced
  - the-annotation-protocol
- q:
  - How was the evidence data annotated?
  - What was the inter-annotator agreement?
  - Why is agreement low on argument type annotation?
  answers:
  - the-annotation-protocol
  - what-evidence-means-here
- q:
  - What are the queries used to retrieve candidate sentences?
  - What does the system miss?
  - Why must the topic appear in the sentence?
  answers:
  - the-queries-are-both-the-filter-and-the-ceiling
  - querying-sentences-at-this-scale-requires-a-different-index
- q:
  - What indexing is needed for sentence-level argument retrieval?
  - How do you run these queries over billions of sentences?
  - How is wikification done at scale?
  answers:
  - querying-sentences-at-this-scale-requires-a-different-index
  - the-queries-are-both-the-filter-and-the-ceiling
- q:
  - Is sentence-level retrieval really different from document retrieval?
  - Do the top results come from many documents or a few?
  - How diverse are the retrieved arguments?
  answers:
  - the-results-really-do-span-the-corpus
  - duplicate-evidence-is-a-corpus-scale-problem
- q:
  - Should the topic be masked in the input?
  - Does masking the topic help BERT?
  - Does giving the model the motion text help?
  answers:
  - masking-the-topic-helps-the-bilstm-and-hurts-bert
  - giving-the-model-the-motion-is-what-the-earlier-framing-missed
- q:
  - Is a larger out-of-domain training set better than a smaller in-domain one?
  - Why is precision lower on Wikipedia than on the news corpus?
  - Does corpus size affect precision at k?
  answers:
  - a-bigger-out-of-domain-training-set-beat-a-matched-one
  - the-precision-reached
- q:
  - How much better is this than earlier evidence detection work?
  - What did switching to BERT contribute?
  - Where does the improvement over the blending method come from?
  answers:
  - the-gain-over-the-earlier-blending-system
  - giving-the-model-the-motion-is-what-the-earlier-framing-missed
- q:
  - Does an evidence detector work for general argument detection?
  - Why is recall low on the argumentativeness benchmark?
  - Does the model transfer to other argument types?
  answers:
  - on-the-argumentativeness-benchmark-it-ranks-by-argument-type
  - what-evidence-means-here
- q:
  - What counts as evidence for a motion?
  - What are Study Evidence and Expert Evidence?
  - What is a motion in argument mining?
  answers:
  - what-evidence-means-here
misreadings:
- 'The reported numbers are precision at k on the system''s own top predictions, annotated
  afterwards. Recall is not measured, and by design cannot be: the queries cannot reach evidence
  that does not mention the topic or fit a pattern, and the paper says so.'
- Precision at k is not comparable across corpora. A smaller corpus may not contain k relevant
  sentences at all, so the drop from the news corpus to Wikipedia is partly a property of
  the corpus rather than of the model. Within one benchmark all variants rank the same candidate
  set and are comparable.
- There is no fixed held-out test set, and that is deliberate. A fixed set would score an
  arbitrary sample accumulated during data collection instead of what the ranker actually
  puts in front of a user.
- Retrospective labeling adds no automatic labels. Every label is a human label; what the
  classifier chooses is which sentences get shown to annotators. It is closer to active learning
  than to self-training or label propagation.
- The 33.5% positive rate is a property of the annotated top predictions, not of the corpus
  or even of the query output -- the estimated positive rate among retrieved sentences is
  about 0.3, and in the corpus at large it is far lower.
- '''Nearly 14% improvement'' on the earlier benchmark is relative. In absolute terms accuracy
  goes from 0.74 to 0.84, and roughly half of that comes from the bigger training set rather
  than from BERT.'
- Masking the topic is not a general improvement. It is the best input for the BiLSTM and
  the worst for BERT, so a result about masking from one architecture does not carry to the
  other.
- The low recall on the argumentativeness benchmark is not a failure of the model. That benchmark
  counts any argumentative sentence as positive, while the model was trained to find two specific
  evidence types, and sampled inspection confirms that is what it accepts.
- The task is Study and Expert Evidence specifically, not arguments in general. The authors
  say the method carries over to Claims and other types, but the results here are for those
  two types.
terminology:
  motion: A high-level claim implying a clear stance toward a topic, optionally with a proposed
    action -- and here the topic is always a Wikipedia article title.
  evidence: A single sentence that clearly supports or contests a motion and gives an indication
    of whether a claim is true, rather than merely asserting a belief.
  Study Evidence / Expert Evidence: 'The two evidence types the system targets: a reported
    quantitative analysis of data, and reported testimony by a relevant expert or authority.'
  sentence-level (SL) retrieval: Indexing and retrieving individual sentences across a whole
    corpus, instead of shortlisting topic-relevant documents and mining inside them.
  Retrospective Labeling: Annotating the current model's top-ranked predictions and retraining
    on them, repeatedly -- which both unskews the training set and concentrates it on hard
    negatives near the top of the ranking.
  VLC / VLD: The Very Large Corpus of some 400 million LexisNexis articles, and the Very Large
    Dataset of 198,457 labelled sentence-motion pairs collected from it.
  masking: Replacing the topic mention in a sentence with a single special token, which marks
    its position and collapses both a topic's surface forms and different topics into one
    representation.
---
