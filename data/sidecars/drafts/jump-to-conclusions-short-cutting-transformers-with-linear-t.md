<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced via a forced tool call) + 3 repair rounds. Every claim, number
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

Then promote it:  python scripts/draft_sidecars.py --accept jump-to-conclusions-short-cutting-transformers-with-linear-t

Stamp: spec=74e012ff9654 checks=pass body=f4d950efbb9c
-->
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
- q:
  - How can I read a prediction out of a transformer's intermediate layer more accurately
    than the logit lens?
  - Is projecting hidden states straight onto the output embeddings the best way to inspect
    intermediate layers?
  - What improves on interpreting hidden representations in the final-layer space?
  answers:
  - context-logit-lens-alternative
  - mat-vs-id-r2
  - gpt2-precision-gain
- q:
  - Do language models decide their output in early layers?
  - How often does an early GPT-2 layer already contain the final next-token prediction?
  - At what depth does BERT's masked-token answer become readable?
  answers:
  - gpt2-early-layers
  - bert-precision-gain
- q:
  - Can linear layer-skipping make early exiting cheaper?
  - How many transformer layers can be skipped while keeping 95% accuracy?
  - Does replacing the identity read-out in an early-exit confidence rule save compute?
  answers:
  - early-exit-savings
- q:
  - Do learned layer-to-layer mappings still work on text from a different domain?
  - Do linear shortcut matrices fitted on Wikipedia transfer to news sentences?
  - Are the linear mappings for skipping transformer layers domain-specific?
  answers:
  - cross-distribution
- q:
  - Does the linear shortcut result hold for larger models?
  - Was linear layer-skipping tested on more than one model size and architecture?
  - Do linear cross-layer mappings work for both decoder-only and encoder-only models?
  answers:
  - scale-robustness
  - mat-vs-id-r2
- q:
  - Which part of a transformer block can be replaced by a linear map with the least damage?
  - Is attention or the feed-forward network easier to approximate linearly?
  - Can individual sub-modules of a transformer be linearised?
  answers:
  - attention-linearizable
- q:
  - Are the tokens read off intermediate layers actually plausible to a human?
  - Was there a human evaluation of predictions decoded from BERT's hidden layers?
  - How often are top-5 tokens from an intermediate layer grammatical in context?
  answers:
  - bert-plausibility
- q:
  - Is it better to jump straight to the last layer or to alternate real blocks with linear
    jumps?
  - Do partial layer skips beat a single mapping to the final layer?
  - How should a schedule of linear jumps through a transformer be chosen?
  answers:
  - alternation
- q:
  - What should I read about how much of transformer computation is linear?
  - Which paper argues transformer inference has more linear structure than the residual stream
    explains?
  - Where does the claim that transformer layers can be short-cut with a single matrix come
    from?
  answers:
  - context-linearity-finding
  - context-logit-lens-alternative
- q:
  - Does short-cutting layers with a matrix require retraining the language model?
  - How expensive is it to fit cross-layer linear mappings for a transformer?
  - What training is needed to skip transformer layers linearly?
  answers:
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
