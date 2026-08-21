---
key: gleize2019convinced
coined: IBM-EviConv
gloss: a dataset of Wikipedia evidence-sentence pairs labeled for which one is more convincing
one_liner: IBM-EviConv is a dataset of 5,697 Wikipedia evidence-sentence pairs labeled for
  convincingness, with pairs matched for type, length and writing level so length cannot be
  a shortcut, and EviConvNet is a Siamese BiLSTM trained on pairs that can also score a single
  argument.
terminology:
  EviConvNet: A Siamese network for argument convincingness whose two weight-sharing legs
    are BiLSTMs with attention over non-trainable word2vec embeddings; each leg emits a convincingness
    output and a dummy output, so training uses a softmax over the two legs' convincingness
    outputs while inference on a single argument uses a softmax over that argument's convincingness
    and dummy outputs.
  cross-stance pair: A pair of arguments about the same debate topic in which one argument
    supports the topic and the other contests it, as opposed to a same-stance pair where both
    take the same side.
  argument length baseline: A convincingness predictor that scores each argument by its character
    length, preferring the longer argument in a pair.
  reason unit: A coded category of the free-text justification an annotator gave for preferring
    one argument over another, from the taxonomy of Habernal and Gurevych (2016b), e.g. C8-1
    'more details, information, examples' or C8-4 'balanced, objective, several viewpoints'.
claims:
- id: eviconv-dataset
  kind: context
  text: IBM-EviConv is a released dataset of Wikipedia evidence-sentence pairs labeled for
    which sentence is more convincing. Argument type, length and writing level are held roughly
    constant within a pair, so they cannot substitute for a convincingness signal.
  scope: 1,884 evidence sentences over almost 70 topics, derived from Shnarch et al. (2018);
    both sentences in a pair share a topic and differ in length by at most 30% of the shorter
    one.
- id: eviconv-size
  kind: result
  text: IBM-EviConv contains 5,697 evidence pairs after cleaning, split 4,319 train and 1,378
    test with no topic shared between the splits, and comprising 3,075 same-stance and 2,622
    cross-stance pairs.
  evidence: Section 4
  scope: More than 8,000 pairs were annotated by 10 crowd labelers each; pairs where no evidence
    reached 60% preference, and pairs left with fewer than 7 valid annotations, were removed.
- id: length-baseline-ukp
  kind: result
  text: Ranking arguments by character length reaches 0.77 accuracy on UKPConvArgStrict, above
    the 0.76 of the BiLSTM of Habernal and Gurevych (2016a) and just below the 0.78 of their
    SVM. Length is therefore a confound in existing convincingness data.
  evidence: Table 1
  scope: Cross-topic validation over 32 topic-stance folds of UKPConvArgStrict, whose pairs
    mix claims and evidence; the most-frequent-label baseline scores 0.50.
- id: length-baseline-eviconv
  kind: result
  text: On IBM-EviConv the evidence-length baseline scores 0.53 accuracy, essentially the
    0.54 of always picking the first candidate, so the length shortcut that works on UKPConvArgStrict
    does not transfer.
  evidence: Table 3
  scope: Full IBM-EviConv test data, where pairs were built with a length difference of at
    most 30% of the shorter evidence.
- id: eviconvnet-ukp-strict
  kind: result
  text: EviConvNet reaches 0.81 accuracy on UKPConvArgStrict, matching the best prior system
    GPC at 0.81 and above GPPL opt. at 0.80, the SVM at 0.78 and the BiLSTM at 0.76, without
    using the 32,000 hand-built linguistic features those baselines rely on.
  evidence: Table 1
  scope: Cross-topic validation over 32 topic-stance folds, average accuracy across folds;
    EviConvNet uses non-trainable word2vec embeddings, a BiLSTM of width 128 and 100 attention
    heads.
- id: eviconvnet-ukp-rank
  kind: result
  text: On UKPConvArgRank EviConvNet attains Pearson's r of 0.47, a statistically significant
    increase over the best prior method GPPL opt. at 0.44 (p much less than 0.01, one-sample
    two-tailed t-test), and ties it on Spearman's rho at 0.67.
  evidence: Table 2
  scope: Averages of the correlation measures across topics, following Simpson and Gurevych
    (2018); the argument-length baseline scores 0.33 Pearson and 0.62 Spearman in the same
    setting.
- id: eviconvnet-eviconv
  kind: result
  text: EviConvNet reaches 0.73 accuracy on IBM-EviConv, significantly above the three Gaussian-process
    systems GPPL, GPPL opt. and GPC at 0.67 each, the single-leg detection model at 0.59 and
    the evidence-length baseline at 0.53 (p much less than 0.01).
  evidence: Table 3
  scope: Full IBM-EviConv train/test split with no shared topics; the Gaussian-process baselines
    are those of Simpson and Gurevych (2018) run with the authors' released code.
- id: headroom-gap
  kind: result
  text: Method choice matters far more on IBM-EviConv than on UKPConvArg. GPPL improves over
    the length baseline by 26% and EviConvNet improves over GPPL by 9% on IBM-EviConv, against
    relative gains of only 5% and 1% on UKPConvArg.
  evidence: Section 5.2
  scope: Percentages are relative to the accuracy of the system or baseline being compared
    against, not absolute accuracy points.
- id: annotation-agreement
  kind: result
  text: 'Choosing the more convincing of two evidence sentences is hard for humans: average
    pairwise Cohen''s Kappa is 0.33 among IBM-EviConv crowd labelers and 0.38 among in-house
    expert labelers on the same task.'
  evidence: Section 4.1
  scope: 92 selected crowd labelers, 23 filtered out for low volume, low Kappa or below-0.55
    precision on hidden test questions; a 105-pair pilot had 84% crowd-expert agreement.
- id: transitivity
  kind: result
  text: 'Convincingness preferences in IBM-EviConv are almost perfectly transitive: of the
    1,899 fully annotated evidence triplets, 99% admit a consistent ordering from most to
    least convincing.'
  evidence: Section 4.1
  scope: Triplets whose three pairs were all annotated and all decisive, after labeler filtering
    and removal of indecisive pairs.
- id: stance-null-result
  kind: result
  text: Cross-stance argument pairs are no harder for EviConvNet than same-stance pairs, and
    training on cross-stance data does not help on cross-stance test data. Accuracy on cross-stance
    test pairs is 0.71 when trained on same- or mixed-stance pairs, versus 0.69 when trained
    on cross-stance pairs.
  evidence: Table 5
  scope: Balanced subsets of 2,082 training pairs and 385 test pairs for each of same, cross
    and mixed stance; all nine train/test combinations fall between 0.69 and 0.72 accuracy.
- id: length-generalization
  kind: result
  text: EviConvNet trained on length-balanced pairs still scores 0.69 accuracy on 458 newly
    annotated evidence pairs whose length difference exceeds 30%, down from 0.73 on the balanced
    data but above every baseline.
  evidence: Section 6.4
  scope: 458 pairs annotated specifically as the complement of the IBM-EviConv length restriction;
    the 0.73 comparison point is the full-dataset accuracy in Table 3.
- id: reason-analysis
  kind: result
  text: EviConvNet beats the length baseline on pairs where annotators cited complexity, presentation,
    off-topicness or non-argumenthood. It has a 57% greater error rate than the length baseline
    on pairs preferred for being balanced and objective across viewpoints.
  evidence: Figure 1
  scope: Pairs from UKPConvArg restricted to those with a single annotator reason, coded with
    the taxonomy of Habernal and Gurevych (2016b); the balanced-objective category (C8-4)
    is only 3% of the data set.
- id: pointwise-scoring
  kind: context
  text: EviConvNet is trained only on pairwise convincingness labels yet can score a single
    argument at inference. The score comes from a softmax over that argument's convincingness
    output and an untrained dummy output from one leg of the Siamese network.
  scope: Requires no task-specific linguistic feature extraction, unlike the SVM and Gaussian-process
    approaches it is compared with; performance is reported as comparable to RankNet-style
    training on held-out data, without numbers.
qa:
- ask:
    plain: is there a public collection of sentence pairs labeled for which one argues more
      convincingly?
    jargon: what corpus provides pairwise convincingness annotations over Wikipedia evidence
      sentences with argument type and length controlled?
    task: where do I get training data for a model that picks the more persuasive of two evidence
      sentences?
    practitioner: can I train a persuasiveness ranker on IBM-EviConv, and how many labeled
      pairs would I have?
  answered_by:
  - eviconv-dataset
  - eviconv-size
- ask:
    plain: can you predict which of two arguments is more persuasive just by picking the longer
      one?
    jargon: how much of UKPConvArgStrict accuracy is recoverable by a character-length heuristic,
      and does it transfer to evidence-sentence pairs?
    task: how do I check whether my argument convincingness data is confounded by length before
      I trust a model on it?
    practitioner: should I worry that my convincingness model is only learning to prefer longer
      arguments?
  answered_by:
  - length-baseline-ukp
  - length-baseline-eviconv
- ask:
    plain: how often can a neural network correctly pick the more convincing of two arguments?
    jargon: how does a Siamese BiLSTM convincingness ranker compare with Gaussian process
      preference learning on UKPConvArgStrict, UKPConvArgRank and evidence pairs?
    task: how do I rank arguments by convincingness without building thousands of hand-crafted
      linguistic features?
    practitioner: is a neural pairwise ranker accurate enough to use for argument convincingness,
      or should I stay with feature-based Gaussian process models?
  answered_by:
  - eviconvnet-eviconv
  - eviconvnet-ukp-strict
  - eviconvnet-ukp-rank
- ask:
    plain: if a model only ever saw pairs of arguments during training, can it still give
      one argument a persuasiveness score on its own?
    jargon: how is a pointwise convincingness score derived at inference from a Siamese network
      trained on pairwise preference labels?
    task: how do I score a single piece of evidence for convincingness when my labels are
      only pairwise comparisons?
    practitioner: can I use a pairwise-trained convincingness model to rank a whole list of
      candidate evidence sentences one at a time?
  answered_by:
  - pointwise-scoring
- ask:
    plain: do people actually agree on which of two pieces of evidence is more convincing?
    jargon: what pairwise Cohen's Kappa do crowd and expert annotators reach on evidence convincingness,
      and are the resulting preferences transitive?
    task: how many annotators do I need before convincingness labels on evidence pairs are
      usable?
    practitioner: can I trust crowdsourced judgments of which argument is more convincing?
  answered_by:
  - annotation-agreement
  - transitivity
- ask:
    plain: is it harder to compare two arguments when they take opposite sides of the same
      topic?
    jargon: does cross-stance versus same-stance pairing affect convincingness prediction
      accuracy, and does cross-stance training data help?
    task: do I need to collect cross-stance argument pairs to train a convincingness model
      that compares opposing evidence?
    practitioner: should I bother annotating pro-versus-con evidence pairs, or will same-stance
      pairs train an equally good convincingness model?
  answered_by:
  - stance-null-result
- ask:
    plain: if a persuasiveness model was trained only on arguments of similar length, does
      it still work when one argument is much longer?
    jargon: how does a convincingness ranker trained on length-balanced evidence pairs perform
      on out-of-distribution pairs with over 30% length difference?
    task: how do I stop length-controlled training data from breaking my convincingness model
      on real pairs of unequal length?
    practitioner: will a model trained on length-matched evidence pairs hold up on my data,
      where lengths vary a lot?
  answered_by:
  - length-generalization
- ask:
    plain: which reasons for finding an argument more convincing can a neural model pick up,
      and which does it get wrong?
    jargon: on which annotator-cited convincingness reasons does a Siamese ranker beat a length
      baseline, and where is its error rate higher?
    task: how do I find out what aspects of argument quality my convincingness model is actually
      missing?
    practitioner: if I need a model that spots balanced, objective coverage of viewpoints,
      is a neural convincingness ranker the wrong tool?
  answered_by:
  - reason-analysis
- ask:
    plain: why build a new dataset of convincing arguments when one already exists?
    jargon: how much relative headroom over a length baseline separates IBM-EviConv from UKPConvArg
      for successive convincingness methods?
    task: which argument convincingness benchmark should I evaluate on if I want method improvements
      to show up?
    practitioner: is it worth switching my convincingness experiments to evidence-sentence
      pairs instead of the older UKPConvArg data?
  answered_by:
  - headroom-gap
  - eviconv-dataset
- ask:
    plain: what should I read first about judging how convincing an argument is?
    jargon: which work introduced evidence convincingness as a pairwise ranking task in computational
      argumentation?
    task: where do I start if I want to build a system that ranks evidence by persuasiveness?
  answered_by:
  - eviconv-dataset
  - pointwise-scoring
misreadings:
- 'EviConvNet''s 0.81 accuracy on UKPConvArgStrict is not an improvement over prior art: it
  ties GPC at 0.81, and the paper''s own tables describe the model as comparable to the best
  baseline on both UKPConvArg tasks. The clear gain is on IBM-EviConv, at 0.73 versus 0.67.'
- 'IBM-EviConv is not a general argument convincingness dataset: its pairs are exclusively
  Wikipedia evidence sentences, deliberately excluding claims, so results on it do not speak
  to claim-versus-evidence comparisons.'
- The 0.33 average pairwise Cohen's Kappa on IBM-EviConv is not evidence of careless crowd
  annotation; in-house expert labelers reached only 0.38 on the same task, and 99% of annotated
  triplets are transitively consistent.
- Controlling within-pair length difference to 30% does not mean the dataset avoids all length
  effects by construction alone; the length baseline still scores 0.53 on IBM-EviConv, and
  a separately annotated set of pairs with larger length differences was needed to test generalization.
- The finding that cross-stance pairs are no harder than same-stance pairs is a negative result
  on one dataset and one architecture, not a general claim that debate side is irrelevant
  to persuasion.
- 'Pre-training a Siamese leg on argument detection is not reported as a working improvement
  in this work: earlier experiments with far fewer training pairs showed gains that could
  not be reproduced on IBM-EviConv.'
---
