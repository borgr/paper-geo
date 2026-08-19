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

Then promote it:  python scripts/draft_sidecars.py --accept are-you-convinced-choosing-the-more-convincing-evidence-with

Stamp: spec=d57862840a90 checks=1 body=692cf7986721
-->
---
key: gleize2019convinced
coined: IBM-EviConv
gloss: a dataset of Wikipedia evidence-sentence pairs labeled for which one is more convincing
one_liner: IBM-EviConv pairs Wikipedia evidence sentences of matched type, length and writing
  level and labels which is more convincing, and EviConvNet — a Siamese BiLSTM-with-attention
  trained on pairs but able to score a single argument — reaches 0.73 accuracy on it against
  0.67 for Gaussian-process baselines.
claims:
- id: eviconv-dataset
  kind: context
  text: IBM-EviConv is a dataset of 5,697 evidence-sentence pairs over roughly 70 debatable
    topics, each pair labeled for which evidence is more convincing, split 4,319 train / 1,378
    test with no topic shared across the split.
  scope: 1,884 unique Wikipedia evidence sentences drawn from the Shnarch et al. (2018) evidence
    set; pairs are within-topic and length-matched to within 30% of the shorter evidence;
    10 crowd labelers per pair with a 60% agreement threshold, indecisive pairs removed.
  evidence: Section 4
- id: first-evidence-convincingness
  kind: context
  text: Gleize et al. (2019) frame evidence convincingness — choosing the more convincing
    of two evidence sentences — as a task distinct from general argument convincingness, where
    prior pair-comparison work mixed claims and evidence.
  scope: Described by the authors as, to their knowledge, the first work on evidence convincingness
    as of ACL 2019; the closest prior dataset is UKPConvArg (Habernal and Gurevych, 2016a),
    on web-mined arguments of mixed type.
  evidence: Section 1
- id: length-baseline-ukp
  kind: result
  text: On UKPConvArgStrict, simply preferring the longer argument reaches 0.77 accuracy,
    above the 0.76 of the BiLSTM of Habernal and Gurevych (2016a) and just below their SVM
    at 0.78.
  scope: Cross-topic validation over 32 topic/stance splits of UKPConvArg, average accuracy
    across folds; UKPConvArg pairs mix claims and evidence and are not length-controlled.
  evidence: Table 1
- id: length-baseline-eviconv
  kind: result
  text: On IBM-EviConv, preferring the longer evidence gives only 0.53 accuracy, below the
    0.54 of always picking the most frequent label, confirming that length carries almost
    no signal once pairs are length-matched.
  scope: 1,378-pair IBM-EviConv test set of Wikipedia evidence sentences paired within 30%
    length difference; the same baseline reaches 0.77 on UKPConvArgStrict.
  evidence: Table 3
- id: eviconvnet-eviconv
  kind: result
  text: EviConvNet reaches 0.73 accuracy on IBM-EviConv, above the 0.67 of GPPL, GPPL opt.
    and GPC and the 0.59 of a single-leg argument-detection model (p ≪ 0.01).
  scope: IBM-EviConv test set; EviConvNet is a Siamese network of two weight-shared BiLSTMs
    (width 128, 100 attention heads) over non-trainable word2vec embeddings, trained 10 epochs
    with Adam at learning rate 0.001, with no task-specific linguistic features.
  evidence: Table 3
- id: eviconvnet-ukp
  kind: result
  text: On UKPConvArgStrict EviConvNet matches the best prior system at 0.81 accuracy (GPC
    0.81, GPPL opt. 0.80), and on UKPConvArgRank it raises Pearson's r to 0.47 from GPPL opt.'s
    0.44 while tying on Spearman's ρ at 0.67.
  scope: Cross-topic validation over 32 UKPConvArg topic/stance splits; ranking measures averaged
    across topics as in Simpson and Gurevych (2018); the Pearson gain is significant at p
    ≪ 0.01 by one-sample two-tailed t-test.
  evidence: Tables 1 and 2
- id: headroom-gap
  kind: result
  text: 'Method choice matters far more on IBM-EviConv than on UKPConvArg: GPPL beats the
    sentence-length baseline by 26% relative and EviConvNet beats GPPL by 9% relative on IBM-EviConv,
    against 5% and 1% on UKPConvArg.'
  scope: Relative percentages computed against the accuracy of the system being compared to,
    on UKPConvArgStrict pair classification and the IBM-EviConv test set.
  evidence: Section 5.2
- id: no-features-needed
  kind: result
  text: A Siamese BiLSTM trained only on word2vec embeddings matches or beats methods built
    on 32,000 linguistic features on both UKPConvArg tasks, so the slow, language-specific
    feature-extraction step is not required for argument convincingness.
  scope: Compared against the SVM and BiLSTM of Habernal and Gurevych (2016a) and the Gaussian-process
    methods of Simpson and Gurevych (2018) on UKPConvArgStrict and UKPConvArgRank.
  evidence: Tables 1 and 2
- id: pointwise-inference
  kind: result
  text: EviConvNet is trained on labeled pairs yet scores a single argument at inference by
    taking a softmax over one leg's convincingness output and an untrained dummy output, giving
    a human-interpretable probability.
  scope: Pointwise scoring evaluated on UKPConvArgRank, where the model reaches Pearson's
    r 0.47 and Spearman's ρ 0.67; the dummy output is never trained and can be a constant.
  evidence: Section 3
- id: cross-stance
  kind: result
  text: 'Comparing evidence from opposite sides of a debate is no harder than comparing same-stance
    evidence: accuracy is 0.69–0.72 across every combination of training and testing on same-,
    cross- and mixed-stance pairs.'
  scope: Equal-size subsets of IBM-EviConv, 2,082 training pairs and 385 test pairs per stance
    condition; training on cross-stance pairs did not improve cross-stance test accuracy over
    training on same- or mixed-stance pairs.
  evidence: Table 5
- id: length-generalization
  kind: result
  text: EviConvNet trained on length-balanced pairs scores 0.69 accuracy on 458 held-out pairs
    whose length difference exceeds 30%, below its 0.73 on the balanced test set but above
    every other baseline.
  scope: 458 extra pairs annotated with the same protocol as IBM-EviConv but violating its
    30% length-difference restriction.
  evidence: Section 6.4
- id: annotation-difficulty
  kind: result
  text: 'Judging which of two evidence sentences is more convincing is hard for people: average
    pairwise Cohen''s Kappa is 0.33 among crowd labelers and 0.38 among in-house experts,
    while 99% of the 1,899 fully annotated evidence triplets satisfy transitivity.'
  scope: IBM-EviConv annotation by 92 selected crowd labelers, 23 of whom were filtered out;
    a 105-pair pilot found 84% label agreement between crowd and expert groups after removing
    indecisive pairs.
  evidence: Section 4.1
- id: reason-analysis
  kind: result
  text: EviConvNet cuts the length baseline's error rate most on pairs where annotators preferred
    the better-thought-out, better-presented or more on-topic argument, but has a 57% greater
    error rate than the baseline on pairs preferred for being balanced and objective.
  scope: UKPConvArg pairs restricted to those with a single annotator-given reason, using
    the reason categories of Habernal and Gurevych (2016b); the balanced/objective category
    covers only 3% of the dataset.
  evidence: Figure 1 and Section 6.1
qa:
- q:
  - How can I tell automatically which of two arguments is more convincing?
  - Is there a model that picks the more persuasive of two pieces of evidence?
  - What accuracy does EviConvNet get at choosing the more convincing evidence?
  answers:
  - eviconvnet-eviconv
  - eviconvnet-ukp
- q:
  - What is a good paper to start with on argument convincingness?
  - Where should I begin reading about ranking arguments by persuasiveness?
  - What work introduced evidence convincingness as a task?
  answers:
  - first-evidence-convincingness
  - eviconv-dataset
- q:
  - What dataset can I use to train a convincingness model on evidence sentences?
  - How big is IBM-EviConv and how was it labeled?
  - Is there a labeled corpus of evidence pairs for persuasiveness?
  answers:
  - eviconv-dataset
- q:
  - Is argument length just a shortcut for predicting convincingness?
  - Does preferring the longer argument work as a convincingness baseline?
  - Why is UKPConvArg considered easy to game?
  answers:
  - length-baseline-ukp
  - length-baseline-eviconv
- q:
  - Why build a new convincingness dataset instead of using UKPConvArg?
  - Does the choice of model matter more on length-controlled evidence pairs?
  - How much headroom is there between baselines and neural models on evidence convincingness?
  answers:
  - headroom-gap
  - length-baseline-eviconv
- q:
  - Do I need thousands of hand-crafted linguistic features to rank arguments by persuasiveness?
  - Can word embeddings alone match feature-engineered convincingness models?
  - How does a Siamese BiLSTM compare to Gaussian process preference learning on UKPConvArg?
  answers:
  - no-features-needed
  - eviconvnet-ukp
- q:
  - Can a model trained on pairwise preferences score a single argument?
  - How does a Siamese convincingness network do pointwise inference?
  - Does training on argument pairs prevent assigning a convincingness score to one argument?
  answers:
  - pointwise-inference
- q:
  - Is it harder to compare arguments from opposite sides of a debate?
  - Does training on cross-stance argument pairs help on cross-stance test pairs?
  - How does stance affect convincingness prediction accuracy?
  answers:
  - cross-stance
- q:
  - Does a convincingness model trained on length-matched pairs still work when lengths differ?
  - What happens to EviConvNet accuracy on evidence pairs with big length gaps?
  answers:
  - length-generalization
- q:
  - How well do humans agree on which argument is more convincing?
  - What is the inter-annotator agreement for evidence convincingness labeling?
  - Does transitivity hold among convincingness judgments of evidence triplets?
  answers:
  - annotation-difficulty
- q:
  - What kinds of argument quality does a neural convincingness model detect that length does
    not?
  - Where does a convincingness model fail relative to the length baseline?
  - Which annotator-given reasons for preferring an argument are hardest to model?
  answers:
  - reason-analysis
misreadings:
- text: The 0.77 accuracy of the argument-length baseline on UKPConvArgStrict is not evidence
    that length predicts convincingness in general; on the length-matched IBM-EviConv pairs
    the same baseline drops to 0.53, at chance level.
- text: EviConvNet's 0.81 on UKPConvArgStrict is a tie with the best prior Gaussian-process
    system, not a win over it; the clear margin over prior art appears on IBM-EviConv, where
    it scores 0.73 against 0.67.
- text: 'A Cohen''s Kappa of 0.33 among IBM-EviConv crowd labelers is not a sign of careless
    annotation: in-house experts reached only 0.38 on the same task, and 99% of annotated
    evidence triplets are transitively consistent.'
- text: 'Restricting IBM-EviConv pairs to within 30% length difference does not make the resulting
    model unusable on real, unbalanced pairs: EviConvNet still scores 0.69 on pairs with larger
    length gaps.'
- text: Including cross-stance pairs in IBM-EviConv did not turn out to be necessary for cross-stance
    performance; training on same-stance pairs gives the same 0.72 cross-stance test accuracy.
terminology:
  EviConvNet: A Siamese network for argument convincingness whose two weight-shared legs are
    BiLSTMs with attention over word2vec embeddings, trained on labeled argument pairs via
    a softmax over the two legs' convincingness outputs.
  dummy output: A second, never-trained output of each Siamese leg, used at inference time
    in a softmax alongside the convincingness output so that a single argument can be scored
    without a partner to compare against.
  cross-stance pair: A pair of evidence sentences on the same debate topic where one supports
    the topic and the other contests it, as opposed to a same-stance pair in which both take
    the same side.
  indecisive pair: An annotated argument pair discarded from IBM-EviConv because the preferred
    evidence was chosen by more than half but fewer than 60% of the labelers.
  hidden test question: A quality-control item inserted among real annotation pairs, built
    automatically by pairing a confirmed evidence sentence with a rejected evidence candidate
    so that the correct answer is known in advance.
links_extra:
  dataset: http://www.research.ibm.com/haifa/dept/vst/debating_data.shtml
---
