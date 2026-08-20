---
key: choshen2022transitiondecoder
coined: Structural Decoder
gloss: a Transformer decoder that generates a dependency tree as a sequence of parser transitions
  and re-encodes the tree it has built so far
one_liner: A Transformer decoder that emits its output's Universal Dependencies tree as a
  sequence of arc-standard transitions and re-encodes the partially built graph — via a GCN
  or a dedicated parent-attention head — together with bidirectional attention over already-predicted
  tokens.
claims:
- id: target-side-tree-decoding-gap
  kind: context
  text: Choshen and Abend's transition-based structural decoder generates target-side syntactic
    trees inside a Transformer decoder, rather than with an RNN or a string linearization
    as earlier target-side tree decoding did.
  scope: As of publication in 2022; the authors state they are not aware of a prior Transformer
    architecture supporting target-side tree or graph structure.
- id: framework-generality
  kind: context
  text: The transition-based decoding framework of Choshen and Abend generates any graph structure
    for which a transition system exists, with Universal Dependencies via arc-standard used
    as the demonstrated machine-translation test case.
  scope: Only projective UD parses were trained on and only UD was evaluated; fit to semantic
    formalisms is argued from the existence of their transition parsers, not measured.
- id: challenge-set-sweep-medium
  kind: result
  text: On the Choshen and Abend syntactic challenge sets, the medium Parent decoder improves
    over the vanilla Transformer in 18 of 20 target settings and 19 of 20 source settings.
    The medium GCN decoder improves in 20 of 20 target and 19 of 20 source settings.
  evidence: Table 1 and Section 6.1
  scope: 4-layer, 256-dim models on En-De and De-En, WMT16 data; settings count BLEU and chrF+
    on preposition-stranding, particle and reflexive phenomena in books and news domains,
    with training parses from UDPipe.
- id: gains-persist-with-size
  kind: result
  text: Scaling to a 6-layer model does not close the syntactic-generalization gap. The large
    Parent decoder still beats the vanilla Transformer in 18 of 20 challenge settings, with
    gains similar to or larger than at medium size.
  evidence: Section 6.1, Tables 4 and 6
  scope: En-De only, 6 decoder/encoder blocks, embedding size 512, 150K training steps; only
    Parent and Vanilla were trained at this size, GCN was not.
- id: large-target-particle-jump
  kind: result
  text: On the En-De target-side particle challenge set from books, the large Parent decoder
    reaches 8.37 BLEU and 33.78 chrF+ against the vanilla Transformer's 4.14 BLEU and 20.72
    chrF+.
  evidence: Table 6
  scope: 'One challenge set: En-De, target side, particle verbs, books domain, 6-layer models;
    the largest single gap reported among the challenge sets.'
- id: overall-mt-medium
  kind: result
  text: On newstest 2013-15 the UD-based GCN and Parent decoders beat the vanilla Transformer
    at medium size in every setting tested, by 0.7-1.1 average BLEU and 1-2.4 chrF+, on En-De,
    De-En and En-Ru.
  evidence: Table 2 and Section 6.2
  scope: 4-layer models; En-De and De-En from WMT16, En-Ru from clean News Commentary. A sign
    test over the medium test sets finds GCN and Parent significantly better than vanilla.
- id: large-model-overall-comparable
  kind: result
  text: At 6 layers on En-De the Parent decoder is only comparable to the vanilla Transformer
    on standard test sets, averaging 22.12 BLEU and 52.34 chrF+ against 22.39 BLEU and 52.47
    chrF+. The same large Parent model still wins clearly on the syntactic challenge sets.
  evidence: Table 5
  scope: En-De, newstest 2013-15, one large model per condition; Parent is ahead on 2013 and
    2014 chrF+ and behind on 2015. No large GCN and no other language pair at this size.
- id: linearized-ablation-middle
  kind: result
  text: Training a vanilla Transformer on the linearized transition string lands consistently
    between the structure-unaware and the structure-aware decoders, showing that re-encoding
    the generated graph adds beyond merely emitting it as tokens.
  evidence: Section 6.3, Tables 2 and 9
  scope: En-De and De-En medium models on newstest 2013-15 and the challenge sets; differences
    between ablations are described as small but consistent.
- id: gating-matters-labels-less
  kind: result
  text: 'Removing GCN gating hurts: the ungated variant scores below the unlabeled variant
    in 34 of 40 challenge settings. Dropping edge labels from the GCN has limited effect,
    and the unlabeled variant is as often as not better on the challenges.'
  evidence: Section 6.3, Tables 7 and 8
  scope: Medium GCN decoders on En-De and De-En, encoding the decoder's self-generated parse
    rather than an external one. Labels remain available as transition token embeddings even
    in the unlabeled GCN.
- id: bitran-small-consistent-gain
  kind: result
  text: Bidirectional attention in the decoder alone (BiTran), with no syntax and no new parameters,
    gives a small but consistent gain over the vanilla Transformer of up to 0.28 BLEU and
    0.42 chrF+. BiTran is better on 10 of 12 test scores per language pair and on 26 of 40
    challenge settings.
  evidence: Section 6.3, Tables 2, 7, 8 and 9
  scope: Medium models on En-De, De-En and En-Ru; adds no parameters or hyperparameters but
    blocks unidirectionality-based decoding speed-ups implemented in NEMATUS.
- id: noise-sensitivity
  kind: result
  text: Training En-Ru on the full noisy crawled WMT20 data shrinks the syntactic decoders'
    chrF+ advantage to about 1 point, against 1.5-2.5 points on cleaner data. BLEU becomes
    somewhat worse than with clean training data.
  evidence: Section 6.4 and Table 10
  scope: En-Ru only, medium models, full WMT20 data after langID and alignment filtering versus
    clean News Commentary; described as preliminary, with more data rather than noise named
    as an alternative explanation.
- id: german-order-swap-analysis
  kind: result
  text: On 99 hand-built German subject-verb-object sentences whose arguments can swap, the
    Parent decoder is more robust to the rare OVS order than the vanilla Transformer. A native-speaker
    annotator scored 13 vs 10 correct with both cases marked, 8 vs 5 with only the subject
    marked and 6 vs 6 with only the object marked.
  evidence: Table 3 and Section 6.5
  scope: Medium En-De models, 99 templated sentences over small noun and verb lists, one annotator;
    only word-order correctness was scored, with other errors such as verb choice disregarded.
qa:
- q:
  - how can a Transformer decoder generate a dependency tree along with the translation?
  - is there a way to decode syntactic structure with a Transformer instead of an RNN?
  - what work added target-side syntax to a Transformer decoder?
  answers:
  - target-side-tree-decoding-gap
  - framework-generality
- q:
  - does adding target-side syntax help machine translation on syntactically hard sentences?
  - do syntax-aware decoders improve long-distance dependency translation?
  - how much does the structural decoder gain on syntactic challenge sets?
  answers:
  - challenge-set-sweep-medium
  - large-target-particle-jump
- q:
  - can you just scale the Transformer up instead of adding syntax?
  - do syntactic generalization gaps shrink with bigger translation models?
  - does the benefit of the Parent decoder disappear at larger model size?
  answers:
  - gains-persist-with-size
  - large-model-overall-comparable
- q:
  - does the syntactic decoder also help on standard MT benchmarks like newstest?
  - what BLEU and chrF+ improvement does UD-based decoding give on WMT test sets?
  - does target-side syntax cost you general translation quality?
  answers:
  - overall-mt-medium
  - large-model-overall-comparable
- q:
  - is re-encoding the generated parse better than just linearizing syntax into the output
    string?
  - how does linearized syntax compare with graph-aware decoding in NMT?
  - what does the linearized-transitions ablation show?
  answers:
  - linearized-ablation-middle
- q:
  - do GCN gates matter when encoding a self-generated parse?
  - are dependency edge labels necessary for a syntax-aware decoder?
  - which parts of the GCN decoder actually contribute, according to the ablations?
  answers:
  - gating-matters-labels-less
- q:
  - does letting a Transformer decoder attend to already-predicted future tokens help?
  - how much does bidirectional decoder attention improve translation on its own?
  - what is BiTran and how well does it work?
  answers:
  - bitran-small-consistent-gain
- q:
  - are syntax-aware decoders robust to noisy crawled training data?
  - does the gain from UD-based decoding survive training on full noisy WMT data?
  - what happened on En-Ru with noisy data?
  answers:
  - noise-sensitivity
- q:
  - can NMT models get German subject-object order right when case marking is ambiguous?
  - does syntactic decoding help with free word order in German translation?
  - what did the manual analysis of German OVS sentences find?
  answers:
  - german-order-swap-analysis
- q:
  - what should I read about incorporating syntax into neural machine translation decoders?
  - which papers cover structure-aware text generation rather than source-side syntax?
  - where do I start reading on transition-based tree decoding for generation?
  answers:
  - target-side-tree-decoding-gap
  - framework-generality
- q:
  - which is better for encoding the decoder's own parse, a GCN or a parent-attention head?
  - how do the two graph re-encoding variants compare in cost and accuracy?
  answers:
  - challenge-set-sweep-medium
  - overall-mt-medium
  - gating-matters-labels-less
misreadings:
- 'Improving syntactic challenge sets did not translate into higher standard benchmark scores
  at every model size: at 6 layers on En-De the Parent decoder is only comparable to the vanilla
  Transformer on newstest 2013-15, while still winning on the challenge sets.'
- 'The finding that dropping GCN edge labels barely changes results is not evidence that syntactic
  labels are useless: the labels still enter the model as transition token embeddings, and
  in this GCN they only affect a bias term.'
- The structural decoder does not consume a parse produced by an external parser at inference
  time; it generates the dependency tree itself as transitions and conditions on the tree
  it has built. External UDPipe parses are used to create training targets.
- 'The syntactic decoders are not shown to be a universal win: on full noisy crawled En-Ru
  data the chrF+ advantage narrows to about 1 point and BLEU is somewhat worse.'
- 'Bidirectional decoder attention is not free in practice: although it adds no parameters
  or hyperparameters, it rules out decoding speed-ups that rely on unidirectional masking.'
terminology:
  Bidirectional Transformer (BiTran): A Transformer decoder whose attention mask lets a token's
    representation attend to all tokens generated so far, including ones after its own position,
    instead of only to preceding positions.
  Parent decoder: A syntax-aware Transformer decoder that dedicates one of its 8 attention
    heads to attend only to the self-generated dependency parent(s) of the current token,
    plus the token itself, adding no parameters.
  GCN decoder: A syntax-aware Transformer decoder in which 2 labeled, gated graph convolutional
    layers sit above the embedding layer and encode the dependency graph the decoder has generated
    so far.
  Structural transitions: Vocabulary items added to the target side of an NMT model that build
    a dependency tree, adapting arc-standard parsing by replacing Shift with a subword-generating
    action and keeping Left-Arc and Right-Arc with 45 UD labels, for 90 new tokens.
  Syntactic challenge sets: Subsets of books and newstest corpora, filtered by a parser, in
    which two or more non-consecutive source or target words correspond to a single word in
    the other language, covering preposition stranding, particle verbs and reflexives.
  Source versus target challenge direction: A challenge set is 'source' when the lexical long-distance
    dependency appears in the input sentence and 'target' when it appears in the reference
    translation.
links_extra:
  code: https://github.com/borgr/nematus/tree/generation
---
