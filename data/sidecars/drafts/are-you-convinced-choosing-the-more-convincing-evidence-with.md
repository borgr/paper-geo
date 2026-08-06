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

Then promote it:  python scripts/draft_sidecars.py --accept are-you-convinced-choosing-the-more-convincing-evidence-with
-->
---
key: DBLP:conf/acl/GleizeSCDMAS19
coined: IBM-EviConv
gloss: a dataset of evidence pairs labelled for which one is more convincing
one_liner: IBM-EviConv is a dataset of 5,697 pairs of Wikipedia evidence sentences labelled
  for which one is more convincing, built so that length, argument type and writing level
  cannot decide the answer, released with EviConvNet, a Siamese network that learns from pairs
  yet scores a single argument at inference.
claims:
- id: what-ibm-eviconv-contains
  text: IBM-EviConv contains 5,697 pairs of evidence sentences labelled for which of the two
    is more convincing, drawn from 1,884 unique Wikipedia sentences over 69 debatable topics
    and split 4,319 train / 1,378 test with no topic appearing in both halves.
  scope: More than 8,000 pairs were annotated and 5,697 survived cleaning. The evidence sentences
    come from the IBM Debater evidence-detection set of Shnarch et al. (2018), so the underlying
    sentences are already-confirmed evidence rather than arbitrary text, and the topic-disjoint
    split is inherited from that dataset.
  evidence: Section 4
- id: the-pairs-are-matched-so-shortcuts-cannot-decide-them
  text: 'IBM-EviConv pairs are deliberately homogeneous on three axes that would otherwise
    settle the comparison: both members are evidence rather than one evidence and one claim,
    both come from Wikipedia so writing level is comparable, and their lengths differ by at
    most 30% of the shorter one.'
  scope: This is the dataset's design contribution rather than a finding. It is a response
    to the earlier UKPConvArg mixing claims with evidence and free-text web-forum prose, where
    argument type and length are themselves informative. 3,075 pairs share a stance toward
    the topic and 2,622 are cross-stance.
  evidence: Sections 1 and 4
- id: the-length-baseline-collapses-on-the-new-dataset
  text: Preferring the longer evidence scores 0.53 accuracy on IBM-EviConv, below the 0.54
    of always picking the first candidate, whereas the same length heuristic reaches 0.77
    on UKPConvArgStrict -- above the 0.76 of the BiLSTM published with that dataset.
  scope: 'The evidence that the length control worked, and the strongest single argument for
    using IBM-EviConv: on the older dataset a one-line heuristic is competitive with a trained
    model, which means gains reported there may be gains at measuring length. The most frequent
    label covers 53% of IBM-EviConv, so 0.53-0.54 is chance.'
  evidence: Tables 1 and 3
- id: eviconvnet-ties-on-the-old-dataset-and-wins-on-the-new-one
  text: EviConvNet reaches 0.81 accuracy on UKPConvArgStrict, equal to the best prior system
    (GPC, 0.81) rather than above it, and 0.73 on IBM-EviConv against 0.67 for all three Gaussian-process
    methods and 0.59 for an evidence-detection model.
  scope: 'Two different comparisons: on UKPConvArgStrict the paper''s own wording is ''comparable
    to the best baseline'', with cross-topic validation over 32 folds (16 topics x 2 stances)
    and accuracy averaged across them; on IBM-EviConv the 0.73 is a significant improvement
    over every system tested (p much less than 0.01).'
  evidence: Tables 1 and 3
- id: the-ranking-gain-is-in-pearson-not-spearman
  text: On UKPConvArgRank, EviConvNet raises Pearson's r to 0.47 from the 0.44 of the best
    prior method, a statistically significant increase (p much less than 0.01, one-sample
    two-tailed t-test), while tying on Spearman's rho at 0.67.
  scope: Correlations are averaged across topics, following Simpson and Gurevych (2018), not
    computed on all arguments pooled as in the original UKPConvArg paper -- so these numbers
    are not comparable with the pooled ones. The rank ordering is unchanged; what improves
    is the linear fit of the scores.
  evidence: Table 2
- id: the-headroom-is-five-times-larger-on-the-matched-dataset
  text: 'Relative to the system each is compared against, the gains on IBM-EviConv are several
    times those on UKPConvArg: a Gaussian-process method improves 26% over the length baseline
    and EviConvNet a further 9% over it, against 5% and 1% for the same two steps on the older
    dataset.'
  scope: Percentages are relative to the referenced system's accuracy, which the authors chose
    deliberately so the two datasets can be compared at different absolute levels. It measures
    how much room a method has to show an effect, not how good the method is.
  evidence: Section 5.2, footnote 6
- id: the-siamese-trick-is-scoring-one-argument-after-training-on-pairs
  text: EviConvNet's two identical legs share all parameters and each emits a convincingness
    score plus an untrained dummy output; training applies softmax across the two legs' scores
    with cross-entropy against the pair label, and inference on a single argument applies
    softmax across that argument's score and its own dummy output.
  scope: This is what makes it pointwise at inference while learning only from pairwise labels
    -- the SVM and BiLSTM of Habernal and Gurevych (2016a) can compare two arguments but cannot
    score one. Unlike RankNet, from which the training procedure is taken, the output is a
    probability; on held-out data the two performed comparably.
  evidence: Section 3
- id: no-feature-engineering-and-a-small-recipe
  text: Each leg is a BiLSTM of width 128 over non-trainable word2vec embeddings followed
    by 100 attention heads and a two-output fully connected layer, trained with Adam at learning
    rate 0.001, gradient clipping at norm 1, dropout 0.15 and 10 epochs.
  scope: 'The point of the comparison is the absence of the roughly 32,000 hand-built linguistic
    features that both prior systems depend on: that pipeline is slow and does not transfer
    to most languages. The leg architecture is taken from Shnarch et al. (2018) rather than
    designed here, and the paper says architecture tuning was not its focus.'
  evidence: Sections 2 and 3 (Implementation of a leg)
- id: how-convincingness-was-operationalised
  text: 'A label is a forced choice: ten crowd labelers were asked which of the two pieces
    of evidence they would rather use in a conversation about the topic, and an evidence counts
    as more convincing only if at least 60% chose it -- pairs preferred by a bare majority
    below that threshold were discarded as indecisive.'
  scope: 'This measures annotators'' stated preference between two candidate pieces of evidence,
    not measured persuasion of anyone''s opinion, and the 60% cut removes exactly the hardest
    pairs. Quality control: 92 pre-screened labelers, 20% hidden test questions, 23 labelers
    filtered out entirely, and pairs left with fewer than 7 valid annotations dropped.'
  evidence: Sections 4 and 4.1
- id: human-agreement-is-low-and-so-is-the-expert-ceiling
  text: Average pairwise agreement on IBM-EviConv is Cohen's kappa 0.33 among crowd labelers,
    against 0.38 among in-house experts on the same task, and crowd and expert groups agreed
    on 84% of the decisively labelled pairs of a 105-pair pilot.
  scope: 'The expert figure is what makes the crowd figure interpretable: 0.33 is low in absolute
    terms but close to a human ceiling of 0.38, which the authors treat as an upper bound
    and read as evidence that the task is hard for people rather than that the annotation
    is noisy. 21 of the pilot''s 105 pairs were indecisive for one group or the other and
    excluded.'
  evidence: Section 4.1
- id: the-labels-are-transitive
  text: Of the 1,899 evidence triplets whose three pairs were all annotated, 99% are transitive
    -- one member is consistently most convincing, one least and one in between.
  scope: A consistency check on the labels rather than a claim about convincingness itself,
    and it is what licenses deriving a ranking from pairwise preferences at all. Measured
    only on triplets that happen to be fully annotated, and after the 60%-threshold cleaning
    removed indecisive pairs.
  evidence: Section 4.1
- id: cross-stance-pairs-are-neither-harder-nor-need-matched-training
  text: 'Training and testing on every combination of same-stance, cross-stance and mixed-stance
    subsets gives accuracies between 0.69 and 0.72: cross-stance pairs are not harder than
    same-stance pairs, and training on cross-stance pairs does not help on them.'
  scope: The authors report this as a surprise, against the expectation that comparing a supporting
    to an opposing argument is a different task. Nine cells from equal-sized subsets -- 2,082
    training and 385 test pairs each -- so the whole grid sits within a 3-point band and the
    conclusion is an absence of an effect at this sample size.
  evidence: Table 5
- id: training-on-length-matched-pairs-still-generalises
  text: On 458 additional pairs whose lengths differ by more than 30%, EviConvNet scores 0.69
    against 0.73 on the length-matched test set -- lower, but still above every baseline measured.
  scope: Directly answers the objection that controlling length in training makes the model
    useless on real, unmatched pairs. These 458 pairs are the complement of the dataset's
    own length restriction and were annotated separately; they are not part of the released
    train/test split.
  evidence: Section 6.4
- id: where-the-network-loses-to-the-length-heuristic
  text: Broken down by the reason annotators gave for their choice, EviConvNet's error rate
    is 57% higher than the length baseline's on pairs decided by an argument being balanced
    and objective across viewpoints, and it also loses on the two categories about sheer quantity
    of supporting information.
  scope: The balanced-and-objective category is 3% of the dataset, which the authors offer
    as the likely reason -- too few training examples of it. The analysis uses Habernal and
    Gurevych's (2016b) reason codes and is restricted to pairs where annotators gave a single
    reason, so it does not cover the dataset as a whole.
  evidence: Figure 1 and Table 4; Section 6.1
- id: what-expert-labelers-said-they-were-deciding-on
  text: Asked what made them prefer one piece of evidence, in-house expert labelers named
    source reliability first -- named authorities, level of expertise, type of evidence such
    as study, expert, opinion, example or precedent, and whether the source has an interest
    in the matter -- then completeness, specificity, significance and relevance to the present
    or future.
  scope: Self-reported factors from a small in-house group, released with the dataset, not
    a measured feature importance. The hard cases they described were pairs where both pieces
    of evidence were weak or where one factor could not be adjudicated between them.
  evidence: Section 6.2 ('We asked the experts')
- id: pretraining-a-leg-on-argument-detection-did-not-reproduce
  text: Initialising the Siamese network from weights learned on argument detection gave significant
    improvements in the authors' earlier experiments but could not be reproduced on IBM-EviConv,
    which they attribute to those earlier efforts having far fewer training pairs.
  scope: 'Reported as an unreproduced result, not a recommendation: the hypothesis is that
    detection pretraining helps most when convincingness training data is scarce. Argument
    detection is binary argument/non-argument classification, a different and less subjective
    task.'
  evidence: Section 7
- id: the-dataset-is-distributed-under-a-different-name
  text: 'IBM-EviConv is distributed under a different name from the one the paper gives it:
    IBM''s Project Debater datasets page publishes it as IBM Debater - Evidence Quality, with
    matching counts of 5,697 pairs, 69 topics and a 4,319 / 1,378 train-test split.'
  scope: 'Relevant to anyone trying to obtain the data: searching for the paper''s name for
    it does not find the distribution, and the distributed description credits its source
    dataset (IBM Debater - Evidence Sentences) rather than the paper''s name for that either.
    The dataset name in the paper is the one used in citations.'
  evidence: Section 4, footnote 2, against the distributing page's own record
qa:
- q:
  - What is IBM-EviConv?
  - What dataset does 'Are You Convinced?' release?
  - What is in the IBM evidence convincingness dataset?
  answers:
  - what-ibm-eviconv-contains
  - the-pairs-are-matched-so-shortcuts-cannot-decide-them
- q:
  - How do I download IBM-EviConv?
  - Where can I get the evidence convincingness data?
  - What is IBM-EviConv called on IBM's dataset page?
  answers:
  - the-dataset-is-distributed-under-a-different-name
  - what-ibm-eviconv-contains
- q:
  - Why build another argument convincingness dataset?
  - What is wrong with UKPConvArg?
  - How is IBM-EviConv harder than earlier convincingness data?
  answers:
  - the-length-baseline-collapses-on-the-new-dataset
  - the-pairs-are-matched-so-shortcuts-cannot-decide-them
  - the-headroom-is-five-times-larger-on-the-matched-dataset
- q:
  - Does argument length predict convincingness?
  - Is a longer argument more convincing?
  - How well does a length baseline do on convincingness?
  answers:
  - the-length-baseline-collapses-on-the-new-dataset
  - where-the-network-loses-to-the-length-heuristic
- q:
  - How accurate is EviConvNet?
  - What accuracy does the Siamese network reach on convincingness?
  - Does EviConvNet beat Gaussian process preference learning?
  answers:
  - eviconvnet-ties-on-the-old-dataset-and-wins-on-the-new-one
  - the-ranking-gain-is-in-pearson-not-spearman
- q:
  - How does the Siamese network work?
  - How can a model trained on pairs score a single argument?
  - What is the dummy output in EviConvNet for?
  answers:
  - the-siamese-trick-is-scoring-one-argument-after-training-on-pairs
  - no-feature-engineering-and-a-small-recipe
- q:
  - What architecture and hyperparameters does EviConvNet use?
  - Does EviConvNet need linguistic features?
  - How was the convincingness model trained?
  answers:
  - no-feature-engineering-and-a-small-recipe
  - the-siamese-trick-is-scoring-one-argument-after-training-on-pairs
- q:
  - How was convincingness annotated?
  - What question were the crowd labelers asked?
  - How many annotators labelled each pair?
  answers:
  - how-convincingness-was-operationalised
  - human-agreement-is-low-and-so-is-the-expert-ceiling
- q:
  - Do people agree about which argument is more convincing?
  - What is inter-annotator agreement on argument convincingness?
  - Is convincingness annotation reliable?
  answers:
  - human-agreement-is-low-and-so-is-the-expert-ceiling
  - the-labels-are-transitive
- q:
  - Are convincingness preferences transitive?
  - Can you rank arguments from pairwise convincingness labels?
  answers:
  - the-labels-are-transitive
  - the-siamese-trick-is-scoring-one-argument-after-training-on-pairs
- q:
  - Is it harder to compare arguments on opposite sides of a debate?
  - Does cross-stance comparison need cross-stance training data?
  - What happens when you compare a supporting and an opposing argument?
  answers:
  - cross-stance-pairs-are-neither-harder-nor-need-matched-training
- q:
  - Does length-controlled training hurt on real unmatched pairs?
  - How does EviConvNet do on pairs of very different length?
  answers:
  - training-on-length-matched-pairs-still-generalises
  - the-length-baseline-collapses-on-the-new-dataset
- q:
  - What makes a piece of evidence convincing?
  - Which factors do expert annotators use to judge evidence?
  - What signals does the model pick up on for convincingness?
  answers:
  - what-expert-labelers-said-they-were-deciding-on
  - where-the-network-loses-to-the-length-heuristic
- q:
  - Does pretraining on argument detection help convincingness?
  - Can you initialise a convincingness model from an argument detector?
  answers:
  - pretraining-a-leg-on-argument-detection-did-not-reproduce
misreadings:
- EviConvNet does not beat prior art on the older UKPConvArg data. It reaches 0.81 on UKPConvArgStrict,
  the same as GPC, and ties on Spearman's rho at 0.67; the paper's own wording there is 'comparable
  to the best baseline'. The improvements are on IBM-EviConv (0.73 against 0.67) and in Pearson's
  r (0.47 against 0.44).
- 'The length baseline scoring 0.53 on IBM-EviConv is the dataset design succeeding, not the
  baseline failing. That same heuristic gets 0.77 on UKPConvArgStrict, which is the problem
  being fixed: on the older data a model can look good by measuring length.'
- Low agreement here is not weak annotation. Crowd kappa is 0.33 against an in-house expert
  kappa of 0.38 on the same pairs, the two groups agreed on 84% of decisively labelled pilot
  pairs, and 99% of fully annotated triplets are transitive. The number reflects a task humans
  find hard.
- The labels are annotators' forced choice between two candidate pieces of evidence -- which
  one they would rather use -- with a 60% agreement threshold. They are not measurements of
  anyone's opinion changing, so results here do not transfer directly to persuasion outcomes.
- This is about evidence sentences, not arguments in general. Every item is a Wikipedia sentence
  already confirmed as evidence, over 69 debatable topics, with claims deliberately excluded
  -- which is precisely what distinguishes it from UKPConvArg's mix of claims and evidence
  from web debate portals.
- 'Cross-stance comparison turned out not to be a distinct harder task, and training on cross-stance
  pairs did not help on them: all nine train/test stance combinations land between 0.69 and
  0.72.'
- The Siamese architecture's contribution is not pairwise accuracy alone but pointwise inference
  -- a convincingness score for a single argument, learned from pairwise labels only. The
  earlier SVM and BiLSTM systems could only compare two arguments.
- Argument-detection pretraining is reported as not reproduced here, not as a recommended
  step. It helped in earlier experiments that had far fewer training pairs, which is the authors'
  proposed explanation.
terminology:
  IBM-EviConv: 'The dataset released here: 5,697 pairs of Wikipedia evidence sentences over
    69 topics, labelled for which is more convincing. Distributed as IBM Debater - Evidence
    Quality.'
  EviConvNet: The paper's Siamese network for the task -- two parameter-sharing BiLSTM-with-attention
    legs joined by a softmax.
  evidence convincingness: Choosing the more convincing of two pieces of *evidence* for a
    debatable topic, as distinct from comparing whole arguments or documents.
  evidence: A sentence supporting or contesting a topic, taken from the IBM Debater evidence-detection
    dataset -- so already verified to be evidence, unlike a claim, which is the concise assertion
    it supports.
  dummy output: The second, untrained head of each leg. Its only job is to give the softmax
    something to compare a single argument's score against at inference time, turning a pairwise-trained
    model into a pointwise scorer.
  same-stance / cross-stance pair: Whether the two pieces of evidence in a pair argue the
    same side of the topic or opposite sides; UKPConvArg has only the former.
  pointwise vs pairwise: Whether a ranking method scores one item at a time or only compares
    two. Pointwise inference is cheaper and needs no transitivity assumption to produce a
    ranking.
---
