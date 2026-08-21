---
claims:
- id: context-logit-lens-alternative
  kind: context
  text: '"Jump to Conclusions" introduces linear cross-layer mappings (mat) as an alternative
    to reading hidden representations directly in the final layer''s space. Each mapping is
    fitted by ordinary linear regression rather than by gradient training.'
  scope: Post-hoc analysis of frozen GPT-2 and BERT, with one matrix per ordered pair of layers
    fitted on 9,000 Wikipedia sentences at one random token position per sentence.
  evidence: Section 3.1
- id: context-linearity-finding
  kind: context
  text: '"Jump to Conclusions" argues that transformer inference contains more linear structure
    than the residual connection alone explains, since context-free, token-uniform matrices
    can stand in for whole blocks and even for individual sub-modules.'
  scope: GPT-2 and BERT, English text, post-hoc on frozen weights; the paper states it does
    not explain why this extra linear structure exists, and studies only linear (not affine
    or non-linear) maps.
- id: mat-vs-id-r2
  kind: result
  text: Least-squares cross-layer matrices (mat) reach higher coordinate-averaged r^2 scores
    than identity propagation for layer pairs across both GPT-2 and BERT. The gap is widest
    in BERT, where identity propagation fails to map representations between most layer pairs.
  evidence: Figures 2 and 3
  scope: 48-layer GPT-2 and 24-layer BERT; mappings fitted on 9,000 Wikipedia sentences and
    scored on a 3,000-sentence validation set at one random token position per sentence, with
    BERT representations taken at a [MASK] token.
- id: gpt2-precision-gain
  kind: result
  text: For GPT-2 next-token prediction, the linear cross-layer mapping mat beats identity
    propagation on Precision@k and Surprisal at every layer, with Precision@1 more than 20%
    higher than identity propagation up to layer 44.
  evidence: Figure 4
  scope: 48-layer GPT-2, Wikipedia validation sentences, one random position per sentence;
    Precision@1 measures agreement with the model's own final-layer top-1 token, not gold-label
    accuracy.
- id: gpt2-early-layers
  kind: result
  text: 'Reading GPT-2''s early layers through the linear mapping mat already recovers the
    model''s final next-token choice often: Precision@10 of 62%-82%, Precision@5 of 52%-74%
    and Precision@1 of 28%-45% in early layers.'
  evidence: Figure 4
  scope: 48-layer GPT-2 on Wikipedia validation sentences; scores are agreement with the full
    model's own final-layer prediction, and each mapping is fitted from the given source layer
    to the final layer.
- id: bert-precision-gain
  kind: result
  text: For BERT masked-token prediction, the linear mapping mat attains 8%-52% precision
    within the first ten layers, where identity propagation stays close to zero for all k.
    Across most layers mat improves Precision@1 over identity propagation by more than 17%.
  evidence: Figure 5
  scope: 24-layer BERT, Wikipedia validation sentences, representations taken at a [MASK]
    token; more than 25% of final predictions are already recovered from layer 3 onward.
- id: bert-plausibility
  kind: result
  text: In a manual annotation of 1,250 instances (50 Leipzig sentences x 25 representations),
    top-5 BERT masked-token predictions decoded through mat were contextually plausible 85.4%
    of the time versus 52.8% for identity propagation.
  evidence: Section 4.2, Analysis (examples in Table 1)
  scope: 24-layer BERT, 50 randomly selected news sentences from the Leipzig corpus, single
    human annotator judging grammatical plausibility; identity propagation yielded more plausible
    top-5 tokens than mat in under 4.3% of instances.
- id: early-exit-savings
  kind: result
  text: In a confidence-based early-exit rule targeting 95% average Precision@1, the linear
    mapping mat saves ~3.3 layers (13.8%) in 24-layer GPT-2 against ~1.4 layers (5.9%) for
    identity propagation. In 24-layer BERT it saves ~4.8 layers (20%) against ~3.5 layers
    (14.6%).
  evidence: Figure 9
  scope: Next-token prediction for GPT-2 and masked-token prediction for BERT, using the confidence
    criterion of Schuster et al. (2022) with varying lambda; efficiency is counted as average
    transformer layers processed, not wall-clock time.
- id: cross-distribution
  kind: result
  text: 'Linear cross-layer mappings transfer across data distributions: swapping Wikipedia-fitted
    for Leipzig-news-fitted mappings changes average Precision@1 by -0.1% and +1.1% for BERT
    and by -5.5% and -8% for GPT-2.'
  evidence: Section 5.2
  scope: 24-layer GPT-2 and 24-layer BERT, mappings fitted on 9,000 sentences from one corpus
    and evaluated on the other's validation set, averaged across layers.
- id: scale-robustness
  kind: result
  text: The advantage of linear cross-layer mappings over identity propagation persists across
    gpt2 (12 layers), gpt2-medium (24), gpt2-large (36), gpt2-xl (48), bert-base-uncased (12)
    and bert-large-uncased (24), plotted against relative depth.
  evidence: Figures 7 and 8
  scope: English Wikipedia sentences, next-token prediction for GPT-2 models and masked-token
    prediction for BERT models; GPT-2 scores overlap closely across scales, while BERT scores
    of the two sizes do not overlap.
- id: alternation
  kind: result
  text: Interleaving genuine transformer blocks with linear jumps beats mapping once from
    a hidden layer to the final layer on Precision@1 for some schedules. Choosing the schedule
    by maximal product of r^2 scores works well only for the first half of layers.
  evidence: Figure 6
  scope: 24-layer GPT-2 next-token prediction on Wikipedia; schedules compared are the r^2-informed
    choice and weighted round-robin with a+b dividing the layer count, and the r^2-informed
    choice under-achieves other schemes in the second half of layers.
- id: attention-linearizable
  kind: result
  text: Replacing attention sub-modules by fitted linear maps costs less Precision@1 than
    linearly replacing FFN or layer-normalization sub-modules in 24-layer GPT-2. From about
    layer 7 onward all three sub-module replacements beat the full-block mapping mat.
  evidence: Figure 10
  scope: 24-layer GPT-2 next-token prediction on Wikipedia, with sub-module regressions fitted
    per block; layer-normalization scores rise sharply in layers 5-8 for reasons the paper
    does not explain.
qa:
- ask:
    plain: is reading a language model's hidden layers through the output vocabulary of the
      last layer a reliable way to see what it is computing?
    jargon: what alternative to logit-lens decoding maps hidden states from an intermediate
      layer into the final layer's representation space?
    task: how do I decode an intermediate transformer layer into vocabulary predictions more
      faithfully than by projecting it directly onto the output embeddings?
    practitioner: should I keep interpreting my model's intermediate activations in final-layer
      space, or fit a mapping between layers first?
  answered_by:
  - context-logit-lens-alternative
  - mat-vs-id-r2
  - gpt2-precision-gain
- ask:
    plain: does a language model already know which word it will output before it reaches
      its last layers?
    jargon: at what depth do GPT-2 next-token and BERT masked-token predictions become recoverable
      from hidden states?
    task: how do I check how early in a transformer the final prediction can already be read
      out?
    practitioner: can I read a usable answer out of my model's early layers instead of running
      it to the end?
  answered_by:
  - gpt2-early-layers
  - bert-precision-gain
- ask:
    plain: how much computation can be skipped if a model stops running layers as soon as
      it is confident about its answer?
    jargon: how many layers does a confidence-based early-exit rule save when the read-out
      uses a fitted cross-layer mapping instead of identity propagation?
    task: how do I cut transformer layers at inference time while holding top-1 agreement
      with the full model near 95%?
    practitioner: is early exiting with a fitted layer-to-layer mapping worth the extra machinery
      for my inference costs?
  answered_by:
  - early-exit-savings
- ask:
    plain: if a shortcut between layers is fitted on encyclopedia text, does it still work
      on news sentences?
    jargon: are least-squares cross-layer mappings sensitive to the fitting corpus, and how
      much does Precision@1 shift under a distribution swap?
    task: do I need to refit a cross-layer mapping on my own corpus, or can I reuse one fitted
      on Wikipedia?
    practitioner: my text is nothing like Wikipedia -- will a mapping fitted elsewhere still
      hold up for me?
  answered_by:
  - cross-distribution
- ask:
    plain: does skipping a language model's middle layers with a simple learned mapping work
      on bigger models and different designs, or only on one small model?
    jargon: does the advantage of fitted cross-layer mappings over identity propagation persist
      across GPT-2 sizes and encoder-only BERT models?
    task: how do I know whether linear layer-skipping will hold for the model size and architecture
      I actually use?
    practitioner: I run a large decoder-only model -- was linear cross-layer mapping tested
      at that scale and on encoders?
  answered_by:
  - scale-robustness
  - mat-vs-id-r2
- ask:
    plain: which piece of a transformer layer can be swapped for a plain matrix with the least
      loss in the model's answer?
    jargon: is the attention sub-module, the feed-forward network or layer normalization the
      most linearly approximable in a transformer block?
    task: how do I decide which sub-module to replace with a fitted linear map when cutting
      transformer compute?
    practitioner: if I linearise part of each block in my transformer, should I start with
      attention or the feed-forward network?
  answered_by:
  - attention-linearizable
- ask:
    plain: when words are read off a model's middle layers, do people judge them as sensible
      in context?
    jargon: was there a human plausibility annotation of top-5 masked-token predictions decoded
      from intermediate BERT representations?
    task: how do I tell whether tokens decoded from intermediate layers are contextually plausible
      and not just formally close to the final output?
    practitioner: can I trust the words I read out of a model's hidden layers enough to show
      them to a human?
  answered_by:
  - bert-plausibility
- ask:
    plain: is it better to jump from a middle layer straight to the end, or to keep some real
      layers and skip others?
    jargon: does interleaving genuine transformer blocks with fitted linear jumps beat a single
      mapping from a hidden layer to the final layer on Precision@1?
    task: how do I pick which transformer layers to actually run and which to replace with
      a linear jump?
    practitioner: if I skip layers in my transformer, should I skip a whole contiguous block
      at the end or alternate skipped and real layers?
  answered_by:
  - alternation
- ask:
    plain: which research argues that a transformer's computation is more linear than the
      skip connections alone would explain?
    jargon: what work establishes that context-free, token-uniform linear maps can substitute
      for whole transformer blocks and sub-modules?
    task: what should I read first about approximating transformer layers with a single fitted
      matrix?
  answered_by:
  - context-linearity-finding
  - context-logit-lens-alternative
- ask:
    plain: does adding shortcuts between a model's layers mean retraining the model?
    jargon: are cross-layer mappings obtained by ordinary least-squares regression, or do
      they require gradient-based training of the transformer?
    task: how do I fit a mapping between two layers of a pretrained transformer without touching
      its weights?
    practitioner: I cannot afford to fine-tune my model -- how cheaply can I get a matrix
      that maps one layer to another?
  answered_by:
  - context-logit-lens-alternative
  - mat-vs-id-r2
one_liner: Jump to Conclusions fits one least-squares matrix per pair of transformer layers,
  so a hidden representation can be cast into a later or final-layer representation directly
  — a far more faithful read-out than inspecting hidden states in the final layer's space,
  and a drop-in upgrade for early exiting.
key: din2023jump
terminology:
  mat: A single matrix, fitted by least-squares linear regression on hidden representations
    at one token position, that maps a representation from one transformer layer to the representation
    at a later layer, skipping the blocks in between.
  id: The baseline of propagating a hidden representation from one transformer layer to a
    later one unchanged, i.e. treating all layers as sharing the same linear space; the assumption
    behind reading intermediate representations directly through the output embeddings.
  Precision@k: The rate at which the top-1 token predicted from a substitute final representation
    appears among the top-k tokens predicted by the model's real final representation.
  Surprisal: The negative log likelihood, under the model's true final output distribution,
    of the highest-probability token obtained from a substitute final representation; lower
    means the substitute's choice looks unsurprising to the full model.
  alternation scheme: An inference mode that interleaves runs of genuine transformer blocks
    with linear jumps across other layers, instead of mapping once from a hidden layer to
    the final layer.
  fixed exit: Stopping inference after a pre-set number of layers for every input, as opposed
    to a dynamic confidence-based early exit decision.
misreadings:
- The reported layer savings are savings in layers processed under an early-exit rule, not
  measured wall-clock speedups or end-task accuracy gains; the accuracy target being retained
  is agreement with the model's own final-layer top-1 prediction.
- Precision@1 in Jump to Conclusions measures agreement with the full model's own prediction,
  not correctness against gold labels, so a high score means faithful approximation of the
  model rather than good language modeling.
- That attention tolerates linear replacement best does not mean attention is unnecessary;
  the finding is that its contextualisation is largely exhausted in early layers, and replacing
  it still costs precision.
- The linear maps are fitted per pair of layers on hidden states at a single token position
  and are context-free and token-uniform, so the method is not a learned per-layer output
  head like layer-wise softmax approaches.
- Concurrent work by Belrose et al. (2023) trained affine hidden-to-final maps with SGD; Jump
  to Conclusions fits linear maps across all layer pairs by regression and reports no empirical
  comparison between the two.
- All experiments in Jump to Conclusions are post-hoc on frozen GPT-2 and BERT with English
  text; the mappings are not integrated into training and other languages are not tested,
  though the findings are expected to carry over.
links_extra:
  trained mappings: https://huggingface.co/sashay/linear-shortcut
  code: https://github.com/sashayd/mat
---
