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

Then promote it:  python scripts/draft_sidecars.py --accept will-it-blend-blending-weak-and-strong-labeled-data-in-a-neu
-->
---
key: DBLP:conf/acl/ShnarchPDGHCAS18
coined: BlendNet
gloss: a network trained on a decaying mixture of noisy and clean labelled data
one_liner: 'Blending weak labelled data into every training epoch at an exponentially decaying
  rate -- rather than using it only to pre-train -- improves a neural argument-evidence detector,
  and the improvement grows as clean labelled data gets scarcer: 1,000 clean examples plus
  weak data match 2,500 clean examples alone.'
claims:
- id: the-contribution-is-a-schedule-not-an-architecture
  text: 'The proposed method keeps weak labelled data in the training set throughout training
    rather than only in a pre-training phase: after m initialisation epochs on weak data alone,
    each subsequent blending epoch k uses all of the strong data together with a fraction
    alpha^k of the weak data, shuffled together.'
  scope: 'The schedule is the contribution and the network is incidental -- the authors state
    explicitly that nothing in the blending method is restricted to their architecture. They
    also decline to claim it is the best schedule: ''the goal of this work is to suggest one
    method which works''.'
  evidence: Section 3.2
- id: the-decay-must-end-in-mostly-clean-data
  text: The number of blending epochs is chosen so that the final four epochs are at least
    95% strong labelled data, because the strong data is the better signal and is what the
    network should finish on.
  scope: 'This stopping rule, not the decay curve itself, is what the design rests on: the
    authors also tried *increasing* the weak-data fraction across epochs and got similar results,
    so the direction of the schedule matters less than ending on clean data.'
  evidence: Sections 3.2 and 5
- id: the-blend-factor-that-works-is-very-small
  text: Of the blend factors tried -- alpha in {0, 0.05, 0.2} -- anything above 0.05 was typically
    ineffective, and one initialisation epoch was enough (m greater than 1 gave slightly worse
    accuracy).
  scope: 'alpha = 0 is not ''no weak data'': it means weak data is used only in the initialisation
    epochs, which is the conventional pre-training setup and is the baseline the method is
    measured against. Since alpha sets how many epochs the weak data still matters in, a small
    value is expected for noisy data.'
  evidence: Section 5
- id: the-gain-is-worth-one-to-two-thousand-clean-examples
  text: With Webis-Debate-16 as the weak source, blending lets 1,000 strong labelled examples
    match the accuracy of 2,500 strong examples alone, and 2,000 match 3,000 -- the improvement
    is significant against both strong-data-only and initialisation-only training at p < 0.05.
  scope: Measured on one task (topic-dependent evidence detection) with strong-data sizes
    swept from 500 to 4,000; accuracies across the whole sweep sit between roughly 50% and
    76%. The equivalence is read off Figure 1 rather than tabulated, and the effect is smaller
    for the second weak source.
  evidence: Figure 1; Section 5
- id: the-benefit-shrinks-as-clean-data-grows
  text: The advantage of blending is largest when strong labelled data is scarcest and narrows
    as it accumulates, which is the condition the method is proposed for rather than a limitation
    discovered afterwards.
  scope: The sweep stops at 4,000 strong examples, so the paper does not show where the benefit
    disappears. Publicly available strong data for argument mining was then a couple of thousand
    instances at most, which is why the low end of the sweep is the operative regime.
  evidence: Figure 1; Sections 2.3 and 5
- id: weak-data-alone-is-much-worse-and-a-plain-union-does-not-help
  text: 'Two controls separate the schedule from the extra data: training on all the weak
    data alone is far below training on the strong data alone, and simply unioning weak and
    strong data with no schedule is well below strong-data-only for one weak source and neither
    helps nor harms for the other.'
  scope: This is the paper's answer to the obvious objection that blending is just more training
    data. It establishes that the gain comes from how the weak data is scheduled, not from
    its presence -- but it is two controls on two weak sources, not an ablation over schedules.
  evidence: Figure 1 (single triangles on the y-axis, single squares at the right border);
    Section 5
- id: how-weak-labels-were-manufactured
  text: 'Weak labels come from splitting a corpus into two sets where positives are merely
    more likely in one than the other: retrieving Wikipedia sentences matching ''that + topic
    concept'' yielded 253,352 candidate sentences of which 25% matched the query pattern and
    became the positive set, while Webis-Debate-16 contributed 16,402 instances split 66%
    positive by mapping idebate.org page structure onto argumentative versus not.'
  scope: The requirement is only a probability gap between the two sets, and the absolute
    rate in the positive set can still be low -- the query's own accuracy as a detector on
    the test set is 17%, and the Webis labels are for argumentativeness rather than evidence,
    assigned automatically from page layout.
  evidence: Sections 3.2 and 4.2
- id: the-smaller-weak-source-worked-better
  text: Webis-Debate-16, with 16,402 instances, gave larger gains than the 253,352-candidate
    Wikipedia query set -- so the amount of weak data was not the deciding factor.
  scope: 'The authors'' proposed explanation is domain fit rather than quantity: Webis sentences
    come from debates, while Wikipedia query matches span many forms and domains. Offered
    as an observation on two sources with a call for future work on what makes weak data fit
    a task, not as a tested mechanism.'
  evidence: Sections 4.2 and 6
- id: the-query-signal-is-a-probability-shift-not-a-label
  text: Sentences matching 'that + topic concept' are 52% positive against a roughly 40% positive
    rate in the training set overall -- a 12-point shift, which is the entire signal that
    weak source provides.
  scope: Adapted from Levy et al. (2017), who showed the query doubles the likelihood of a
    *claim*; this paper's premise is that the pattern marks argumentative content generally,
    which is why it transfers to evidence detection at a much weaker rate.
  evidence: Section 4.2
- id: the-released-dataset
  text: The paper releases 5,785 Wikipedia sentences manually annotated for topic-dependent
    evidence detection over 118 topics, split by topic into 83 training topics (4,066 sentences)
    and 35 test topics (1,719 sentences), with a positive rate of about 40% in both halves.
  scope: 'Sentence-level counts, not evidence counts: at a 40% positive rate the dataset holds
    roughly 2,300 positive evidence sentences, which is why later work describes it as ''more
    than 2,000 evidence sentences over 118 topics''. Topics come from sources such as Debatepedia
    and no topic appears in both splits.'
  evidence: Section 4.1
- id: what-counts-as-evidence-in-the-annotation
  text: 'A sentence was labelled positive only if it met three criteria at once: it clearly
    supports or contests the topic rather than being neutral, it is coherent and stands mostly
    on its own, and it is convincing enough to sway someone -- a claim alone does not qualify,
    it has to be backed up.'
  scope: Ten annotators per topic-sentence pair, combined by majority with ties resolved as
    non-evidence, so the label is conservative by construction. Fleiss' kappa is 0.45, and
    for 85% of instances the majority included at least 70% of annotators.
  evidence: Section 4.1
- id: the-topic-is-masked-during-training
  text: Every occurrence of the topic concept in a candidate sentence is replaced with a common
    token, so the model is trained to detect evidence topic-independently rather than to recognise
    the topics it was trained on.
  scope: The topic concept is located by an in-house wikification tool similar to TagMe, which
    makes this preprocessing step a dependency of reproducing the setup. Combined with the
    topic-disjoint split, it is what makes the test set a test of transfer to unseen topics.
  evidence: Section 4.1
- id: the-task-skips-the-intermediate-claim-and-the-article-shortlist
  text: Evidence is detected as directly supporting or contesting the topic, with no intermediate
    claim to attach to, and searched across the whole corpus rather than within a pre-selected
    set of articles where evidence is already known to be dense.
  scope: 'Both differences are against Rinott et al. (2015) and both make the task harder,
    which is the point: the setting is corpus-wide topic-dependent argument mining, so the
    positive rate in the wild is far below the 40% of the curated dataset.'
  evidence: Section 2.2
- id: the-network-and-its-recipe
  text: BlendNet is a bidirectional LSTM with an attention layer -- cell size 128, attention
    size 100 -- over frozen 300-dimensional GloVe embeddings trained on 840B Common Crawl
    tokens, using Adam at learning rate 0.001, gradient clipping at global norm 1.0 and dropout
    0.85 with a single mask shared across timesteps.
  scope: 'Reported so the result is reproducible, not as a design claim: the paper says blending
    can be applied to other networks and that the architecture choice is not the contribution.
    The shared-mask dropout follows Gal and Ghahramani (2016).'
  evidence: Section 3.1
- id: how-the-accuracies-were-obtained
  text: Each configuration was run five times on different slices of the strong labelled data,
    the best epoch's accuracy was recorded per run, and the reported figure is the micro-average
    of those five best accuracies.
  scope: Averaging over slices is there to control variance at small data sizes, but taking
    the best epoch per run means the reported number is not a clean held-out estimate -- it
    is an upper envelope, and the comparison between conditions is what carries the result.
    Significance is by unpaired Student t-test at p < 0.05.
  evidence: Section 5; Figure 1 caption
qa:
- q:
  - What does blending weak and strong labeled data mean?
  - How do you combine noisy and clean labels when training a network?
  - What is the blending method in 'Will it Blend?'
  answers:
  - the-contribution-is-a-schedule-not-an-architecture
  - the-decay-must-end-in-mostly-clean-data
  - the-blend-factor-that-works-is-very-small
- q:
  - Is blending better than pre-training on weak data?
  - Why not just pre-train on the noisy data and fine-tune?
  - What does blending add over standard weak-supervision pre-training?
  answers:
  - the-contribution-is-a-schedule-not-an-architecture
  - the-blend-factor-that-works-is-very-small
  - the-gain-is-worth-one-to-two-thousand-clean-examples
- q:
  - How much does blending help?
  - How many labelled examples is weak data worth?
  - What accuracy gain does blending give on evidence detection?
  answers:
  - the-gain-is-worth-one-to-two-thousand-clean-examples
  - the-benefit-shrinks-as-clean-data-grows
- q:
  - When is blending worth doing?
  - Does blending still help when I have plenty of labelled data?
  - Which data regime does blending target?
  answers:
  - the-benefit-shrinks-as-clean-data-grows
  - the-gain-is-worth-one-to-two-thousand-clean-examples
- q:
  - Is the improvement just from having more training data?
  - What happens if you simply concatenate weak and strong data?
  - How good is a model trained on weak data alone?
  answers:
  - weak-data-alone-is-much-worse-and-a-plain-union-does-not-help
  - the-contribution-is-a-schedule-not-an-architecture
- q:
  - Where did the weak labels come from?
  - How do you generate weak labeled data for argument mining?
  - What is the 'that + topic concept' query?
  answers:
  - how-weak-labels-were-manufactured
  - the-query-signal-is-a-probability-shift-not-a-label
- q:
  - Does more weak data help more?
  - Which weak data source worked better and why?
  - Is the quality or the quantity of weak data what matters?
  answers:
  - the-smaller-weak-source-worked-better
  - how-weak-labels-were-manufactured
- q:
  - What blend factor should I use?
  - How fast should the weak data fraction decay?
  - How many initialisation epochs does blending need?
  answers:
  - the-blend-factor-that-works-is-very-small
  - the-decay-must-end-in-mostly-clean-data
- q:
  - What dataset does this paper release?
  - Where can I get topic-dependent evidence detection data?
  - How big is the IBM evidence sentences dataset?
  answers:
  - the-released-dataset
  - what-counts-as-evidence-in-the-annotation
- q:
  - What counts as evidence for a topic?
  - How was the evidence detection data annotated?
  - What were the annotation guidelines for evidence?
  answers:
  - what-counts-as-evidence-in-the-annotation
  - the-task-skips-the-intermediate-claim-and-the-article-shortlist
- q:
  - How is topic-dependent evidence detection set up?
  - Does the model see the topic during training?
  - How do you keep an evidence detector topic-independent?
  answers:
  - the-topic-is-masked-during-training
  - the-task-skips-the-intermediate-claim-and-the-article-shortlist
- q:
  - What network is BlendNet?
  - What architecture and hyperparameters were used?
  - Does blending require a specific model?
  answers:
  - the-network-and-its-recipe
  - the-contribution-is-a-schedule-not-an-architecture
- q:
  - How were the reported accuracies computed?
  - How many runs per configuration?
  - Are the numbers a clean held-out estimate?
  answers:
  - how-the-accuracies-were-obtained
misreadings:
- The contribution is the training schedule, not the network. The authors say outright that
  nothing in the blending method is tied to their BiLSTM, and that they do not claim their
  schedule is the best one -- only that it works.
- Blending is not 'more data helps'. Weak data alone trains a far worse model than strong
  data alone, and unioning the two with no schedule is well below strong-only for one weak
  source and neutral for the other. The scheduling is doing the work.
- The baseline being beaten is weak-data pre-training, which is what alpha = 0 means here,
  not the absence of weak data. Two different comparisons are reported and the method is significant
  against both.
- The improvement is not uniform. It is largest at 500-2,000 strong examples and narrows as
  strong data grows; the sweep stops at 4,000, so the paper does not show where it vanishes.
- More weak data is not better. The 16,402-instance Webis corpus outperformed the 253,352-candidate
  Wikipedia query set, which the authors attribute to domain fit rather than size.
- The exponential decay direction is not the essential ingredient -- increasing the weak-data
  fraction across epochs performed similarly. What the design requires is that the last epochs
  be almost entirely strong data.
- Fleiss' kappa 0.45 is inter-annotator agreement on the evidence-detection annotation, not
  a model score, and the 40% positive rate is a property of the curated candidate set, not
  of Wikipedia.
- Reported accuracies are the best epoch of each of five runs, micro-averaged. That makes
  them an upper envelope rather than a clean held-out estimate; the between-condition comparison
  is what the result rests on.
terminology:
  BlendNet: The paper's name for a network trained on a blend of weak and strong labelled
    data -- here a BiLSTM with attention, though the method is architecture-agnostic.
  weak labeled data (WLD): Labels obtained free from a heuristic or from document structure,
    where all that is required is that positives be *more likely* in one set than the other;
    the absolute rate in the positive set can still be low.
  strong labeled data (SLD): Manually annotated data for the target task -- high quality,
    and in argument mining typically only a couple of thousand instances.
  blend factor (alpha): 'The per-epoch decay applied to the weak data: blending epoch k uses
    alpha^k of it. Values above 0.05 were typically ineffective; alpha = 0 reduces the method
    to conventional pre-training.'
  initialisation epochs (m): Epochs at the start that use weak data only. One was enough;
    more was slightly worse.
  topic-dependent evidence detection: Deciding whether a sentence is evidence for or against
    a given topic -- with no intermediate claim, and searched corpus-wide rather than inside
    a shortlist of articles.
---
