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

Then promote it:  python scripts/draft_sidecars.py --accept are-you-convinced-choosing-the-more-convincing-evidence-with

Stamp: spec=d57862840a90 checks=2 body=054b1811bed1
-->
---
key: gleize2019convinced
coined: IBM-EviConv
gloss: a dataset of Wikipedia evidence-sentence pairs labeled for which one is more convincing
one_liner: IBM-EviConv is a dataset of 5,697 Wikipedia evidence-sentence pairs labeled for
  which evidence is more convincing, with pairs matched for type, length and writing level
  so that length shortcuts do not solve the task, plus EviConvNet, a Siamese BiLSTM trained
  on pairs that also scores single arguments.
terminology:
  EviConvNet: A Siamese network for argument convincingness whose two weight-sharing BiLSTM-with-attention
    legs each emit a convincingness output and a dummy output; training applies softmax over
    the two legs' convincingness outputs, and inference scores a single argument by softmax
    over its convincingness and dummy outputs.
  cross-stance pair: A pair of evidence sentences on the same debatable topic where one supports
    the topic and the other contests it, as opposed to a same-stance pair where both take
    the same side.
  IBM-EviConv: A dataset of 5,697 pairs of Wikipedia-sourced evidence sentences over roughly
    70 debatable topics, each pair labeled by crowd annotators for which evidence is more
    convincing, with pair members restricted to within 30% length difference.
  indecisive pair: An annotated evidence pair in which one side was preferred by more than
    half of the labelers but by fewer than 60%, and which is therefore excluded from the released
    dataset.
claims:
- id: eviconv-dataset
  kind: context
  text: IBM-EviConv is a dataset of 5,697 evidence-pair convincingness judgments over Wikipedia
    evidence sentences, with pair members matched to within 30% length difference.
  scope: Almost 70 English debatable topics, 1,884 unique evidence sentences derived from
    the Shnarch et al. (2018) evidence set. Split into 4,319 train and 1,378 test pairs with
    no topic shared across the split; evidence sentences only, no claims.
- id: length-baseline-ukp
  text: A baseline that simply prefers the longer argument reaches 0.77 accuracy on UKPConvArgStrict,
    above the 0.76 of the BiLSTM of Habernal and Gurevych (2016a) and just below the 0.78
    of their SVM.
  scope: Cross-topic validation over 32 topic-stance splits of UKPConvArg, whose pairs mix
    claims and evidence from web debate portals and are not length-controlled.
  evidence: Table 1
- id: length-baseline-eviconv
  text: On IBM-EviConv the length baseline collapses to 0.53 accuracy, essentially the 0.54
    of always picking the most frequent label, confirming that length-matched evidence pairs
    remove the length shortcut.
  scope: Full IBM-EviConv test set of length-matched Wikipedia evidence pairs; the same baseline
    reaches 0.77 on the non-length-controlled UKPConvArgStrict.
  evidence: Table 3
- id: eviconvnet-eviconv
  text: EviConvNet reaches 0.73 accuracy on IBM-EviConv, above the 0.67 of the GPPL, GPPL
    opt. and GPC methods of Simpson and Gurevych (2018), the 0.59 of a single-leg detection
    model and the 0.53 length baseline.
  scope: Full IBM-EviConv dataset with a cross-topic train/test split; BiLSTM of width 128
    with 100 attention heads over non-trainable word2vec embeddings, trained 10 epochs.
  evidence: Table 3
- id: eviconvnet-ukp-strict
  text: EviConvNet matches rather than beats the best prior systems on UKPConvArgStrict pair
    classification, reaching 0.81 accuracy, equal to GPC and above GPPL opt. at 0.80, the
    SVM at 0.78 and the BiLSTM at 0.76.
  scope: Cross-topic validation over 32 topic-stance splits, average accuracy across folds;
    EviConvNet uses no task-specific features, unlike the baselines' 32,000.
  evidence: Table 1
- id: eviconvnet-ukp-rank
  text: On UKPConvArgRank, EviConvNet scores Pearson's r of 0.47 against 0.44 for GPPL opt.,
    a statistically significant increase (p much less than 0.01), while tying GPPL opt. on
    Spearman's rho at 0.67.
  scope: Average of correlation measures across 32 topics, following the Simpson and Gurevych
    (2018) protocol; single-argument scores come from one leg of a network trained only on
    pairs.
  evidence: Table 2
- id: headroom-gap
  text: Better methods pay off far more on IBM-EviConv than on UKPConvArg. GPPL improves over
    the length baseline by 26% and EviConvNet over GPPL by 9% on IBM-EviConv, versus 5% and
    1% on UKPConvArg.
  scope: Relative improvements computed against the accuracy of the referenced system, comparing
    IBM-EviConv accuracies with UKPConvArgStrict accuracies.
  evidence: Section 5.2
- id: annotation-agreement
  text: 'Convincingness of evidence pairs is hard even for people: average pairwise Cohen''s
    Kappa is 0.33 among the crowd labelers of IBM-EviConv and 0.38 among in-house expert labelers
    on the same task.'
  scope: 92 pre-screened crowd labelers, 10 annotations per pair, after filtering 23 labelers
    on minimum-volume, Kappa and hidden-test-precision criteria.
  evidence: Section 4.1
- id: transitivity
  text: 'Convincingness judgments in IBM-EviConv are highly transitive: of the 1,899 evidence
    triplets whose three pairs were all annotated, 99% comply with transitivity.'
  scope: Triplets from the cleaned dataset, where pairs preferred by fewer than 60% of labelers
    were dropped as indecisive.
  evidence: Section 4.1
- id: cross-stance
  text: 'Comparing evidence from opposite sides of a debate is no harder than comparing same-side
    evidence: EviConvNet scores 0.69 to 0.71 on cross-stance test pairs and 0.72 on same-stance
    ones. Training on cross-stance pairs does not help cross-stance testing.'
  scope: Nine train/test combinations of same-, cross- and mixed-stance subsets of IBM-EviConv,
    each training subset 2,082 pairs and each test subset 385 pairs, so differences of a point
    or two are within noise.
  evidence: Table 5
- id: length-generalization
  text: EviConvNet trained on length-matched pairs still reaches 0.69 accuracy on 458 newly
    annotated evidence pairs whose length difference exceeds 30%. That is below its 0.73 on
    the balanced test set but above every other baseline.
  scope: 458 pairs annotated specifically as the complement of the IBM-EviConv 30% length
    restriction; a single held-out evaluation, not cross-validated.
  evidence: Section 6.4
- id: balanced-viewpoint-weakness
  text: EviConvNet is worse than the length baseline on argument pairs preferred for being
    balanced and objective across several viewpoints, with a 57% greater error rate on that
    reason category.
  scope: UKPConvArg pairs restricted to those given a single reason, under the Habernal and
    Gurevych (2016b) taxonomy; that category covers only 3% of the dataset.
  evidence: Figure 1
- id: siamese-pointwise
  kind: context
  text: EviConvNet shows that a Siamese neural network trained only on pairwise convincingness
    labels can also score a single argument on its own. It needs none of the roughly 32,000
    hand-built linguistic features used by prior SVM and Gaussian process approaches.
  scope: Demonstrated on argument and evidence convincingness in English, on datasets of a
    few thousand pairs; single-argument scoring uses softmax over one leg's convincingness
    output and an untrained dummy output. As of the 2019 publication.
qa:
- q:
  - What dataset should I use to study which argument is more convincing?
  - Is there a benchmark for comparing the persuasiveness of two pieces of evidence?
  - Where can I find labeled pairs of arguments with a convincingness preference?
  - What should I read first about assessing argument convincingness?
  answers:
  - eviconv-dataset
  - siamese-pointwise
- q:
  - Can you predict which argument is more convincing just from its length?
  - How strong is a length baseline on argument convincingness datasets?
  - Does preferring the longer argument solve convincingness prediction?
  answers:
  - length-baseline-ukp
  - length-baseline-eviconv
- q:
  - How accurate is EviConvNet on IBM-EviConv?
  - What accuracy do models get at picking the more convincing evidence sentence?
  - Does a Siamese network beat Gaussian process preference learning on evidence convincingness?
  answers:
  - eviconvnet-eviconv
- q:
  - How does the Siamese network compare to prior methods on UKPConvArg?
  - Does a neural model beat the SVM and Gaussian process baselines on UKPConvArgStrict?
  - What are the results on UKPConvArgRank ranking correlations?
  answers:
  - eviconvnet-ukp-strict
  - eviconvnet-ukp-rank
- q:
  - Why build a new convincingness dataset when UKPConvArg already exists?
  - Is UKPConvArg too easy for measuring progress on argument convincingness?
  - How much room for improvement is there on length-controlled evidence pairs?
  answers:
  - headroom-gap
  - length-baseline-eviconv
  - eviconv-dataset
- q:
  - How well do human annotators agree on which argument is more convincing?
  - What is the inter-annotator agreement for convincingness labeling?
  - Do experts agree more than crowd workers about persuasiveness?
  answers:
  - annotation-agreement
- q:
  - Are convincingness preferences between arguments transitive?
  - Do pairwise persuasiveness judgments form a consistent ordering?
  - Can pairwise convincingness labels be turned into a ranking?
  answers:
  - transitivity
  - siamese-pointwise
- q:
  - Is it harder to compare arguments from opposite sides of a debate?
  - Does training on cross-stance argument pairs help?
  - Does stance matter when choosing the more convincing evidence?
  answers:
  - cross-stance
- q:
  - Does training on length-matched pairs hurt performance on real-world pairs of different
    lengths?
  - How does EviConvNet do when the two evidence sentences differ a lot in length?
  answers:
  - length-generalization
- q:
  - Where does a neural convincingness model fail?
  - Which reasons for preferring an argument are hardest to predict?
  - What kinds of argument quality does the Siamese network miss?
  answers:
  - balanced-viewpoint-weakness
- q:
  - Can a model trained on pairwise preferences score a single argument?
  - How do you get a pointwise convincingness score without hand-crafted linguistic features?
  - Is it possible to avoid 32,000 linguistic features for convincingness prediction?
  answers:
  - siamese-pointwise
  - eviconvnet-ukp-rank
misreadings:
- 'EviConvNet does not beat prior art on UKPConvArg pair classification: at 0.81 accuracy
  it ties GPC and is comparable to the best baseline. The clear margin over Gaussian process
  methods appears only on the length-controlled IBM-EviConv, at 0.73 versus 0.67.'
- IBM-EviConv is not a larger version of UKPConvArg. It contains only evidence sentences from
  Wikipedia, matched in length and writing level, which removes the length and argument-type
  shortcuts that make UKPConvArg partly solvable by a length baseline.
- 'A Cohen''s Kappa of 0.33 among crowd labelers is not evidence of careless annotation: in-house
  experts reached 0.38 on the same task, and crowd and expert groups agreed on 84% of decisive
  pilot pairs.'
- The finding that cross-stance pairs are not harder than same-stance pairs comes from subsets
  of 2,082 training and 385 test pairs, so it bounds the size of any effect rather than proving
  stance is irrelevant.
- Pre-training one leg of the Siamese network on argument detection is not reported as a working
  improvement; earlier gains from that initialization could not be reproduced in this setup
  with more training pairs.
---
