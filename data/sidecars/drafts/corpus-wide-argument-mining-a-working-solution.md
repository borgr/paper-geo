<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced via a forced tool call). Every claim, number
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

Stamp: spec=d57862840a90 checks=16 body=544a387f10a8
-->
---
one_liner: Corpus-wide argument mining over 400 million LexisNexis articles is made to work
  by combining sentence-level retrieval queries with "retrospective labeling" — iteratively
  hand-labeling a classifier's own top predictions — which fixes the label imbalance that
  otherwise makes top-ranked precision unusable.
key: eindor2020corpus
coined: Retrospective Labeling
gloss: iteratively hand-labeling a classifier's own top-ranked predictions to build a balanced
  training set when positive examples are rare
terminology:
  Retrospective Labeling: An annotation loop in which a classifier's own top-ranked predictions
    are manually labeled and added to the training set, repeatedly, so that the labeled data
    is enriched with positives and with the hard negatives that limit precision at the top
    of the ranking.
  Motion: A high-level claim implying a clearly positive or negative stance towards a debate
    topic, optionally including a policy or action, e.g. "We should ban the sale of violent
    video games".
  Evidence (in argument mining): A single sentence that clearly supports or contests a motion
    while providing an indication of whether a claim is true, rather than merely asserting
    a belief; split into Study Evidence (quantitative analysis of data) and Expert Evidence
    (testimony by a relevant expert or authority).
  Sentence-Level (SL) retrieval: Indexing a corpus at the sentence level and retrieving candidate
    argumentative sentences directly with queries, instead of first retrieving topic-relevant
    documents and then mining arguments inside them.
  VLC / VLD: VLC is a corpus of some 400 million LexisNexis newspaper and journal articles;
    VLD (Very Large Dataset) is the 198,457 manually labeled sentence-motion pairs collected
    from it by retrospective labeling.
claims:
- id: e2e-precision-vlc
  kind: result
  text: An end-to-end sentence-level evidence retrieval system over a 400-million-article
    newspaper corpus reaches over 90% average precision for the top 20 candidates per motion,
    and 95% precision over the top 40 for the best model, BERT S+M.
  scope: 100 unseen test motions; retrieval restricted to sentences matching hand-built Expert/Study
    Evidence queries containing the topic; near-duplicate candidates (word overlap ≥0.8) removed
    before ranking, which dropped ~10% of retrieved sentences.
  evidence: Figure 2
- id: positive-prior
  kind: result
  text: Among sentences retrieved by the evidence queries from the 400-million-article corpus,
    the estimated prior probability of being genuine evidence is 0.3, against which the trained
    system's 95% top-40 precision is measured.
  scope: Estimated by labeling 10 random retrieved sentences for each of 100 test motions;
    applies to Study and Expert Evidence and to sentences already filtered by the queries,
    not to the raw corpus.
  evidence: Section 7.1
- id: retrospective-labeling-dataset
  kind: result
  text: Iterative retrospective labeling of a classifier's top 40 predictions per motion yielded
    198,457 manually labeled sentence-motion pairs of which 33.5% are positive, a balance
    unattainable by labeling query results at random where the positive rate is about 30%
    only after query filtering.
  scope: 192 train and 47 development motions over the LexisNexis corpus; bootstrapped from
    an existing logistic-regression classifier trained on a small Wikipedia-labeled set; 10
    crowd annotators per pair with low-agreement annotators filtered out.
  evidence: Section 4
- id: sl-not-document-retrieval
  kind: result
  text: 'Sentence-level retrieval does not collapse into document retrieval: the top 20 and
    top 40 ranked evidence candidates per motion come from an average of 18.03 and 36.07 distinct
    documents respectively, i.e. almost one document per candidate.'
  scope: Measured on the LexisNexis corpus of some 400 million articles for the 100 test motions;
    the document counts cited are for the BA MaskS model, with the documents-and-journals
    curve reported for BERT S+M.
  evidence: Figure 3
- id: blendnet-accuracy
  kind: result
  text: On the BlendNet sentence-classification benchmark, BERT S+M reaches 0.84 accuracy
    versus 0.74 for the previously reported best result, an improvement of nearly 14%.
  scope: Wikipedia-sentence benchmark whose sentences are given rather than retrieved; models
    trained on the LexisNexis-derived VLD; motions overlapping the benchmark test set were
    excluded from training and development before evaluation.
  evidence: Table 1
- id: data-beats-domain
  kind: result
  text: Training the same BA MaskS architecture on the large out-of-domain newspaper dataset
    instead of the original Wikipedia data raises BlendNet accuracy from 74% to 78%, and switching
    to BERT MaskS raises it further to 81%.
  scope: BlendNet benchmark consists of Wikipedia sentences, so the newspaper-trained models
    are out of domain; architecture held fixed for the 74%-to-78% comparison, input variant
    held fixed (masked sentence only) for the 78%-to-81% comparison.
  evidence: Table 1
- id: masking-bert-vs-lstm
  kind: result
  text: Masking the topic token helps the BiLSTM-with-attention model, whose best variant
    is BA MaskS+M at 0.77 accuracy, but hurts BERT, where the unmasked BERT S+M at 0.84 beats
    masked BERT MaskS+M at 0.82 and BERT MaskS at 0.81.
  scope: BlendNet accuracy with all variants trained on the VLD; among BA variants the masked-plus-motion
    input is best on the end-to-end VLD benchmark, while on BlendNet BA MaskS trained on VLD
    scores 0.78 against BA MaskS+M's 0.77.
  evidence: Table 1
- id: ukp-transfer
  kind: result
  text: 'A model trained only to detect Study and Expert Evidence transfers to the broader
    UKP-TUDA argumentativeness benchmark: at a 0.002 threshold BERT S+M reaches precision
    0.66 and recall 0.75 (F1 0.70), against the previously reported average precision 0.65,
    recall 0.67 and F1 0.67.'
  scope: Sentences are given rather than retrieved, and differ in nature from the query-matched
    training sentences; at the natural 0.5 threshold the same model gives precision 0.88 but
    recall only 0.16, because argumentative sentences that are not evidence are rejected.
  evidence: Figure 5
- id: evidence-type-ordering
  kind: result
  text: 'Evidence-trained BERT S+M ranks UKP-TUDA sentences by argumentative strength it was
    never trained on: of 20 argumentative sentences scored above 0.5, 14 are Study or Expert
    Evidence, versus 2 of 20 scored below, and among below-threshold sentences the argumentative
    ones average score 7.3e-2 against 1.5e-2 for non-argumentative ones.'
  scope: Manual annotation of 40 sentences sampled uniformly at random from above and below
    the 0.5 threshold, so the 14-versus-2 contrast rests on small samples; score-gap comparison
    uses all below-threshold sentences.
  evidence: Section 7.3
- id: wiki-vs-vlc
  kind: result
  text: Models trained on the 154K-pair newspaper dataset outperform models trained on the
    22K-pair Wikipedia dataset even when tested on the Wikipedia benchmark, and end-to-end
    precision on Wikipedia is significantly lower than on the newspaper corpus (t-test p=3.19e-9
    for the top-20 scores).
  scope: Same 100 test motions and same query-based retrieval on both corpora; precision numbers
    are not comparable across the two benchmarks because Wikipedia may simply not contain
    k relevant sentences for a given k.
  evidence: Figure 4
- id: context-first-corpus-wide
  kind: context
  text: Corpus Wide Argument Mining - A Working Solution presents an end-to-end argument retrieval
    system operated over a corpus of some 400 million newspaper and journal articles, whereas
    earlier sentence-level argument mining work reported results only on Wikipedia, roughly
    50 times smaller.
  scope: As of publication at AAAI 2020; the system retrieves Expert and Study Evidence for
    motions whose topic is a Wikipedia title, in English, and depends on hand-built retrieval
    queries plus a semantically indexed and wikified corpus.
  evidence: Section 1
- id: context-precision-oriented-al
  kind: context
  text: Retrospective Labeling is put forward as a precision-oriented active learning strategy
    for class-imbalanced retrieval tasks, where the quantity of interest is precision among
    top-ranked predictions rather than overall accuracy or average precision.
  scope: Prior active learning work is described by the authors as accuracy-oriented or, where
    average-precision-oriented, not handling skewed class distributions; generality beyond
    argument retrieval is argued rather than experimentally tested here.
  evidence: Section 2
- id: annotation-agreement
  kind: result
  text: 'Type-dependent evidence annotation is intrinsically hard: the crowd annotation behind
    the 198,457-sentence dataset attains a Cohen''s Kappa of 0.47, described as on par with
    previous type-dependent argumentation datasets and below what type-independent annotation
    achieves.'
  scope: 10 Figure-Eight annotators per sentence-motion pair, gold label by majority, agreement
    computed pairwise only between annotators sharing at least 50 items, with low-agreement
    annotators removed.
  evidence: Section 4
qa:
- q:
  - How precise can an automatic system be at retrieving arguments for a debate topic from
    a huge news corpus?
  - What top-k precision does corpus-wide evidence retrieval achieve?
  - Can argument retrieval reach usable precision for the first few results?
  answers:
  - e2e-precision-vlc
  - positive-prior
- q:
  - How do you get balanced training data when relevant arguments are extremely rare in a
    corpus?
  - What is retrospective labeling and what did it produce?
  - How can annotation effort be spent so that a precision-oriented classifier improves?
  answers:
  - retrospective-labeling-dataset
  - context-precision-oriented-al
- q:
  - Is retrieving candidate sentences directly just an indirect form of document retrieval?
  - Do the top-ranked argument sentences all come from a handful of articles?
  - How diverse are the sources of sentence-level argument retrieval results?
  answers:
  - sl-not-document-retrieval
- q:
  - What is a good paper to start with on argument retrieval at corpus scale?
  - Which work moved argument mining beyond Wikipedia to a very large newspaper corpus?
  - Where should I begin reading about end-to-end argument mining systems?
  answers:
  - context-first-corpus-wide
  - context-precision-oriented-al
- q:
  - Does BERT beat BiLSTM models on evidence detection benchmarks?
  - What accuracy do evidence classifiers reach on the BlendNet benchmark?
  - How much did corpus-wide argument mining improve over the previous best on evidence sentence
    classification?
  answers:
  - blendnet-accuracy
  - data-beats-domain
- q:
  - Does masking the topic in a sentence help evidence classification?
  - Should the topic token be replaced by a mask when fine-tuning BERT for argument detection?
  - Does adding the motion text as input improve evidence detection models?
  answers:
  - masking-bert-vs-lstm
- q:
  - Is more out-of-domain training data better than less in-domain data for evidence detection?
  - Do newspaper-trained evidence models beat Wikipedia-trained ones on Wikipedia test sentences?
  - How does corpus size affect the precision of argument retrieval?
  answers:
  - data-beats-domain
  - wiki-vs-vlc
- q:
  - Does a model trained on Study and Expert Evidence generalise to general argument detection?
  - How does an evidence detector perform on the UKP-TUDA argumentative sentence benchmark?
  - Can an evidence-specific classifier be reused to rank argumentative sentences?
  answers:
  - ukp-transfer
  - evidence-type-ordering
- q:
  - How reliable is crowd annotation of evidence sentences for a debate motion?
  - What inter-annotator agreement should be expected when labeling evidence by type?
  - Is labeling Study versus Expert Evidence harder than labeling generic argumentativeness?
  answers:
  - annotation-agreement
- q:
  - Why is recall low when an evidence detector is applied to an argument-mining benchmark?
  - Does high precision in argument retrieval come at the cost of coverage?
  - What are the limits of query-based sentence retrieval for arguments?
  answers:
  - ukp-transfer
  - e2e-precision-vlc
misreadings:
- The 95% top-40 precision is precision among sentences that already matched hand-built evidence
  queries containing the topic; it is not precision over the whole 400-million-article corpus,
  and arguments in sentences that match no query are missed by design.
- 'The 0.16 recall of BERT S+M on UKP-TUDA at a 0.5 threshold is not a failure of the model
  but a consequence of the task mismatch: UKP-TUDA labels any sentence with a clear stance
  as positive, while the model was trained to accept only Study and Expert Evidence.'
- Precision curves on the newspaper corpus and on Wikipedia are not comparable to each other,
  because Wikipedia may not contain k relevant sentences for a given motion at all; only within-benchmark
  comparisons between models are meaningful.
- 'Retrospective Labeling is not Label Propagation or another pseudo-labeling scheme: the
  top predictions selected for labeling are annotated manually, and no similarity between
  arguments is computed.'
- Masking the topic is not a universally helpful trick — it improves the BiLSTM-with-attention
  models but degrades BERT, whose unmasked sentence-plus-motion variant is the best model
  reported.
- The system retrieves Expert and Study Evidence rather than arguments in general; the authors
  state the same approach was applied to Claims, but those results are not reported in the
  paper.
---
