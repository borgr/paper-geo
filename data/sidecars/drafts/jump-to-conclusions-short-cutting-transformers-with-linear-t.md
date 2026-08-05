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

Then promote it:  python scripts/draft_sidecars.py --accept jump-to-conclusions-short-cutting-transformers-with-linear-t
-->
---
coined: linear shortcut
gloss: Fitting a least-squares linear map between two layers of a frozen transformer and using
  it to skip the computation in between, so a hidden representation can be read as if it were
  a final one. The paper writes the fitted map as mat and the usual practice of reading a
  layer unchanged as id.
one_liner: 'Rather than read a transformer''s hidden layer in the final layer''s space, fit
  a linear regression between the two: agreement with the model''s own next-token prediction
  rises by over 20 points across most of GPT-2''s depth, GPT-2 and BERT settle their answer
  early, and early exit skips 13.8% of layers rather than 5.9%.'
claims:
- id: linear-regression-between-layers
  text: 'For every ordered pair of layers in a frozen transformer, fit one square matrix by
    least squares to carry hidden representations from the earlier layer to the later one,
    then use it to skip the blocks in between. The model is not retrained and nothing is added
    to it: the mapping is fitted once from recorded activations and applied afterwards.'
  scope: 'The map is non-contextual and position-uniform -- a single matrix applied to one
    vector, with no access to the rest of the sequence and no dependence on which position
    or token it came from. That is what makes the result informative: whatever the mapping
    recovers is linear structure that survives being stripped of context. It is also what
    bounds it, since anything that depends on the surrounding tokens cannot be recovered.
    No bias term is used and no regularization is reported; the paper is explicit that affine
    and non-linear families are possible and were not tried.'
  evidence: Section 3.1, Equation 1, Figure 1, Section 10
- id: identity-baseline-fails-badly
  text: 'The prevailing practice -- reading a hidden representation directly in the final
    layer''s space, as if all layers shared one coordinate system -- is much worse than a
    fitted linear map at every layer pair in both models tested, and in BERT it fails almost
    completely: for most layer pairs the identity mapping has essentially no explanatory power
    over the target representations.'
  scope: 'Measured as a coordinate-averaged r-squared against the representations a full forward
    pass produces, shown as two heatmaps per model rather than a table, so the comparison
    is a direction with a visible margin rather than a pair of numbers. The asymmetry between
    the models matters: BERT''s blocks change their representations enough that same-space
    reading breaks down, while GPT-2''s residual stream tolerates it better -- which is roughly
    the assumption the logit-lens style of analysis rests on, holding partially for one architecture
    and not the other.'
  evidence: Section 3.3, Figure 2, Figure 3
- id: prediction-agreement-gains
  text: 'The better fit translates into better predictions: on GPT-2 next-token prediction
    the linear shortcut''s top-1 agreement with the model''s own final prediction exceeds
    the identity baseline''s by more than 20 percentage points at every layer up to the 44th
    of 48, and its surprisal is substantially lower throughout.'
  scope: Precision@k here means the shortcut's argmax appears in the full model's own top
    k, and surprisal is the full model's negative log likelihood of that argmax -- so both
    measure fidelity to the unmodified model, not correctness against a gold label. The reported
    early-layer levels are 28-45% for k=1, 52-74% for k=5 and 62-82% for k=10, read from a
    figure with 95% intervals shown for surprisal only. One random token position per validation
    sentence is scored, so these are per-position averages over 3,000 sentences, not full-sequence
    generation quality.
  evidence: Section 4, Section 4.1, Figure 4
- id: bert-masked-token-gains
  text: The gap is even wider for masked-token prediction in BERT, where the identity baseline's
    precision is near zero at every k for the first ten layers while the fitted map reaches
    8-52%, improves top-1 agreement by more than 17 points at most layers, and shows more
    than a quarter of the model's final predictions already recoverable from layer 3 onwards.
  scope: All BERT representations analyzed are those of the [MASK] position itself, since
    that is where masked-language-model predictions are read from -- so this characterizes
    the masked-token pathway, not BERT's representations in general. The 8-52% range spans
    the three k values and the first ten of 24 layers. As with GPT-2 the reference is the
    model's own final distribution. The layer at which the identity baseline starts working
    at all roughly coincides with a feature of the r-squared heatmap, an observation the paper
    notes without explaining.
  evidence: Section 4.2, Figure 5, Section 3.3
- id: predictions-are-plausible-not-just-matching
  text: 'A manual check confirms the shortcut''s early-layer predictions are real words in
    context rather than artifacts of the metric: over 1,250 annotated instances, 85.4% of
    the mapped model''s top-5 tokens fit the sentence grammatically against 52.8% for the
    identity baseline, and in fewer than 4.3% of instances did the baseline offer more plausible
    tokens.'
  scope: Fifty sentences from the news corpus times 25 representations per sentence, judged
    by a single annotator on grammatical plausibility alone -- not on being the right answer,
    and with no second annotator or agreement statistic. Grammatical fit is a low bar that
    a fluent but wrong token clears. It is nonetheless the paper's only evaluation that does
    not use the model's own output as ground truth, which is why it carries weight disproportionate
    to its size.
  evidence: Section 4.2, Table 1, Section 5.2
- id: early-layers-already-encode-the-answer
  text: Read through a fitted linear map rather than directly, both models turn out to have
    largely settled their output well before the final layer -- the interpretability claim
    the paper draws from its numbers, and the reason it argues that inspecting layers in the
    final layer's space understates how early prediction is formed.
  scope: '"Already predicts the final output" means agrees with what the same model would
    have said after a full pass, so this is about when the computation converges, not about
    when it becomes correct. And the levels are partial: top-1 agreement in GPT-2''s early
    layers is 28-45%, so most early predictions still differ from the final one; the strong
    statement is about top-5 and top-10 agreement and about the contrast with the identity
    baseline. A mapping fitted to predict layer L''s representations will also import some
    of layer L''s behaviour, which is the standing objection to every learned lens and is
    not addressed here.'
  evidence: Section 1, Section 4.1, Section 4.2, Section 9
- id: alternating-mappings-can-beat-direct-mapping
  text: 'Jumping straight to the last layer is not the best use of the mappings: alternating
    real transformer blocks with linear jumps -- run a few blocks, skip a few, repeat -- beats
    mapping directly to the final layer for some schedules, at equal numbers of executed blocks.'
  scope: 'Measured on 24-layer GPT-2 with top-1 agreement only. The practical catch is that
    the paper has no reliable way to pick the schedule: choosing the schedule with the best
    product of per-jump r-squared scores works for the first half of the layers and underperforms
    other schedules in the second half, and the authors suggest depth-weighting as future
    work. So the finding is that better schedules exist, not that they can be selected in
    advance.'
  evidence: Section 4.3, Figure 6
- id: robust-across-scales
  text: 'The pattern holds across four GPT-2 sizes (12 to 48 layers, hidden width 768 to 1600)
    and two BERT sizes: at every scale the fitted map gives substantially better predictions
    from intermediate layers than reading them directly. Plotted against relative depth the
    GPT-2 curves largely coincide, while the two BERT curves do not.'
  scope: That GPT-2's curves overlap under relative depth suggests prediction formation occupies
    a similar fraction of the network regardless of size -- suggestive, from two figures,
    across one family spanning four sizes. Both families are pre-2020 models topping out at
    1.5B parameters; nothing here tests a modern decoder, a model trained with a different
    normalization placement, or an instruction-tuned one.
  evidence: Section 5.1, Figure 7, Figure 8
- id: mappings-transfer-across-corpora
  text: 'Mappings fitted on one corpus work on another: refitting on news sentences instead
    of Wikipedia changes average top-1 agreement by 0.3 points for GPT-2 and -1.4 for BERT,
    and applying a mapping fitted on one corpus to the other costs 5.5 and 8 points for GPT-2
    while BERT loses 0.1 in one direction and gains 1.1 in the other.'
  scope: The transfer is clean for BERT and only reasonable for GPT-2, where an 8-point drop
    is a real cost even if the method still beats the baseline; the paper's summary of "generalizes
    well" averages over that difference. One of the four swaps improving on its own in-domain
    mapping suggests a noise floor of about a point, which the 0.3 and -1.4 replication figures
    sit inside. Both corpora are single English sentences from encyclopedic or news text --
    a narrow notion of distribution shift.
  evidence: Section 5.2
- id: early-exit-saves-more-layers
  text: 'Dropped into a standard confidence-based early-exit rule as a replacement for reading
    representations directly, the fitted map raises how much computation can be skipped at
    a fixed quality target: holding 95% average top-1 agreement, it exits after saving 13.8%
    of layers in GPT-2 where the baseline saves 5.9%, and 20% against 14.6% in BERT.'
  scope: The abstract's "saves additional 7.9% layers for GPT-2 and 5.4% for BERT" is the
    difference between those pairs, not the total saving -- the totals are 13.8% and 20%,
    roughly 3.3 and 4.8 layers of 24. The savings count transformer blocks skipped, not wall-clock
    time, and do not charge for the matrix multiplication the mapping adds or for storing
    the matrices. The exit rule and its threshold schedule are taken from prior work, and
    dynamic exit beats fixed-depth exit under both mappings, as expected.
  evidence: Section 6, Figure 9, Section 1
- id: attention-is-the-most-linearizable-submodule
  text: 'Replacing individual sub-modules with linear approximations rather than skipping
    whole blocks, attention is the most tolerant: from about layer 7 onwards every sub-module
    approximation predicts better than the whole-block shortcut, and linearizing attention
    costs less precision than linearizing the feed-forward network or the layer normalizations.'
  scope: 'The striking part is what the attention substitution removes. The linear stand-in
    acts on each position independently, so it disables contextualization between the layers
    it replaces entirely -- and that costs less than linearizing components that are already
    per-position. The feed-forward and normalization substitutions keep real attention and
    stay contextual, which the paper offers as the reason they degrade more: a linear stand-in
    for those erodes the self-attention that runs after them. One 24-layer GPT-2, next-token
    prediction, read from a figure. The paper also flags a sharp unexplained rise in the normalization
    curve at layers 5-8.'
  evidence: Section 7, Figure 10, Appendix A
- id: contextualization-may-exhaust-itself-early
  text: Because attention can be replaced by a per-position linear map in the later layers
    at little cost, the paper suggests contextualization largely finishes early and late-layer
    attention matters only in more delicate cases -- and notes that non-contextual inference
    is parallelizable, so this points at a route to faster inference.
  scope: 'Labelled speculative by the authors, and it should stay that way: the evidence is
    aggregate agreement with the model''s own top prediction on single-sentence Wikipedia
    text, where long-range dependencies are scarce and the average case is easy. The parallelization
    is a consequence of the substitution''s structure, not something implemented or timed
    -- no throughput measurement appears anywhere in the paper.'
  evidence: Section 7, Section 1, Section 9
- id: cheaper-than-training-a-lens
  text: 'The mappings are fitted in closed form by linear regression, which the paper positions
    as much cheaper than the alternatives: concurrent work learning affine maps to the final
    layer trains them by gradient descent against a KL objective, and per-layer early-exit
    heads require a separate output softmax per layer, far more parameters than one square
    matrix.'
  scope: 'The comparison is on cost, not on quality: the paper states that comparing the accuracy
    of the two approaches would be valuable and does not do it. So the claim that this approach
    "far exceeds the prevailing practice" is measured against reading representations unchanged,
    not against the strongest available learned alternative. Cheap is also relative -- a full
    square matrix per ordered layer pair means on the order of a thousand matrices for a 48-layer
    model, of which the released collection is a subset.'
  evidence: Section 8, Section 3.1, Section 9
- id: how-the-mappings-were-fit
  text: Each mapping is fitted on 9,000 Wikipedia sentences with one randomly chosen token
    position taken from each, validated on 3,000 more, for every ordered pair of layers in
    the model; the news-corpus replication uses 9,000 training and 1,000 validation sentences.
    The fitted matrices and code are released.
  scope: One vector per sentence, so a square matrix of width up to 1,600 is fitted from 9,000
    examples -- comfortable per output coordinate but not lavish, and no regularization is
    mentioned. Sentences rather than documents, explicitly to simplify the analysis, which
    also means short contexts throughout. For BERT the chosen position is replaced by a mask
    token before recording, so its training and evaluation representations are mask representations
    by construction.
  evidence: Section 3.3, Section 5.2, Section 4.2
- id: what-this-does-not-explain
  text: 'The paper is explicit about what it leaves open: it finds more linear structure in
    transformer computation -- in whole layers and in individual sub-modules -- than residual
    connections alone would predict, and does not explain why; it restricts itself to linear
    rather than affine or non-linear maps; it only analyzes trained models without changing
    their weights; and every experiment is on English.'
  scope: The residual-stream argument is the standard justification for treating hidden states
    as approximations of final states, and the observation here is that linearity extends
    past what that argument covers -- including to sub-modules that sit inside the residual
    branch, where no such argument applies. Integrating these mappings into training is named
    as future work rather than attempted. The authors expect the findings to carry to other
    languages on the grounds that nothing in the method is language-specific, which is a reasonable
    expectation and not a result.
  evidence: Section 10, Section 1, Section 7
qa:
- q:
  - How do you read a transformer's intermediate layer as if it were the final one?
  - What is the linear shortcut method?
  - Can you skip transformer layers with a matrix multiplication?
  - How do I turn a hidden representation into a prediction?
  answers:
  - linear-regression-between-layers
  - identity-baseline-fails-badly
  - how-the-mappings-were-fit
- q:
  - Is the logit lens reliable?
  - Can you project hidden layers directly to the vocabulary?
  - Do all transformer layers live in the same space?
  - Why does reading early layers in the output space give garbage?
  answers:
  - identity-baseline-fails-badly
  - prediction-agreement-gains
  - bert-masked-token-gains
- q:
  - Do transformers decide their output in early layers?
  - At what layer does a language model know what it will say?
  - How much of the final prediction is present halfway through the network?
  answers:
  - early-layers-already-encode-the-answer
  - prediction-agreement-gains
  - bert-masked-token-gains
- q:
  - How much does a linear lens improve over reading representations directly?
  - What accuracy do you get predicting from intermediate layers?
  - Does the improvement hold for masked language models like BERT?
  answers:
  - prediction-agreement-gains
  - bert-masked-token-gains
  - predictions-are-plausible-not-just-matching
- q:
  - Are early-layer predictions actually sensible words, or just metric artifacts?
  - Did anyone check the intermediate-layer predictions by hand?
  - Does agreement with the final layer mean the prediction is any good?
  answers:
  - predictions-are-plausible-not-just-matching
  - early-layers-already-encode-the-answer
  - prediction-agreement-gains
- q:
  - How much computation can early exiting save?
  - Can a better lens improve early exit?
  - How many transformer layers can I skip while keeping 95% of the quality?
  answers:
  - early-exit-saves-more-layers
  - alternating-mappings-can-beat-direct-mapping
  - prediction-agreement-gains
- q:
  - Is it better to skip straight to the last layer or alternate skips with real layers?
  - How do you choose which layers to skip?
  - Can you interleave linear shortcuts with transformer blocks?
  answers:
  - alternating-mappings-can-beat-direct-mapping
  - early-exit-saves-more-layers
- q:
  - Which part of a transformer block is most linear?
  - Can attention be replaced by a linear map?
  - Is the feed-forward network or attention easier to approximate?
  - What happens if you remove contextualization from the later layers?
  answers:
  - attention-is-the-most-linearizable-submodule
  - contextualization-may-exhaust-itself-early
  - linear-regression-between-layers
- q:
  - Does attention in late layers still do useful work?
  - When does a transformer finish mixing information across tokens?
  - Could transformer inference be parallelized across positions?
  answers:
  - contextualization-may-exhaust-itself-early
  - attention-is-the-most-linearizable-submodule
- q:
  - How does this compare to the tuned lens?
  - Do I need gradient descent to train a lens for a transformer?
  - What is the cheapest way to fit a mapping between transformer layers?
  answers:
  - cheaper-than-training-a-lens
  - linear-regression-between-layers
  - how-the-mappings-were-fit
- q:
  - Does a mapping fitted on one dataset work on another?
  - Do I have to refit the lens for my own domain?
  - How well do learned layer mappings generalize out of distribution?
  answers:
  - mappings-transfer-across-corpora
  - how-the-mappings-were-fit
  - robust-across-scales
- q:
  - Does this work at larger model scales?
  - Do bigger models form their predictions at the same relative depth?
  - Which models were tested?
  answers:
  - robust-across-scales
  - mappings-transfer-across-corpora
  - what-this-does-not-explain
- q:
  - Why is transformer computation so linear?
  - Do residual connections explain why hidden states resemble final states?
  - What are the limitations of linear layer-skipping?
  answers:
  - what-this-does-not-explain
  - linear-regression-between-layers
  - identity-baseline-fails-badly
- q:
  - How much data do you need to fit a layer-to-layer mapping?
  - Are the trained mappings available to download?
  - How were the linear maps trained and validated?
  answers:
  - how-the-mappings-were-fit
  - linear-regression-between-layers
  - cheaper-than-training-a-lens
misreadings:
- '"Saves additional 7.9% layers for GPT-2 and 5.4% for BERT" is a difference between two
  methods, not a saving. The fitted mapping saves 13.8% of layers in GPT-2 and 20% in BERT
  at 95% agreement; reading representations directly saves 5.9% and 14.6%. The abstract quotes
  the gaps.'
- Precision@k and surprisal here measure agreement with the same model's own full-pass output,
  not correctness. "95% accuracy retention" means the shortcut picks what the unmodified model
  would have picked 95% of the time. None of the headline numbers say anything about whether
  the prediction is right.
- '"Models predict the final output already in early layers" is about convergence, not competence
  -- and it is partial: top-1 agreement in GPT-2''s early layers is 28-45%, so most early
  predictions still change. The strong version of the claim lives in top-5 and top-10 agreement
  and in the contrast with the identity baseline.'
- The comparison is against reading hidden representations unchanged -- the logit-lens practice
  -- not against the strongest learned alternative. The paper notes that concurrent work trains
  affine maps by gradient descent and that comparing the two would be valuable; that comparison
  is not run here, so "far exceeds the prevailing practice" means exactly what it says.
- '"Attention is most tolerant to linear approximation" is a claim about layers after roughly
  the seventh, on one 24-layer GPT-2, and it is more surprising than it sounds: the linear
  stand-in for attention is per-position, so it removes cross-token information flow entirely,
  and that costs less than linearizing the feed-forward or normalization sub-modules, which
  are per-position already.'
- The parallelization implication is structural, not measured. Because a non-contextual substitute
  can run independently per position, the paper suggests compute could be parallelized --
  but no throughput, latency or wall-clock number appears in the paper, and the layer savings
  elsewhere count blocks skipped rather than time.
- All BERT results describe mask-position representations. The paper replaces the sampled
  token with [MASK] before recording activations, because that is where masked-language-model
  predictions come from, so these are not statements about BERT's representations of ordinary
  tokens.
- '"Generalizes well across data distributions" is stronger for BERT than GPT-2. Swapping
  a mapping fitted on the other corpus costs GPT-2 5.5 and 8 points of top-1 agreement, while
  BERT loses 0.1 in one direction and gains 1.1 in the other. Both corpora are single English
  sentences, which is a mild notion of shift.'
- The alternation result does not come with a recipe. Some interleavings of real blocks and
  linear jumps beat mapping straight to the last layer, but the paper's rule for choosing
  one -- maximize the product of per-jump r-squared -- works only in the first half of the
  network and underperforms in the second.
- The mapping is fitted per ordered pair of layers, so a 48-layer model implies on the order
  of a thousand square matrices of width 1,600. Fitting each is cheap and closed-form, and
  the released collection is a subset -- but "one matrix" describes a single jump, not the
  artifact as a whole.
terminology:
  linear shortcut: Replacing the transformer computation between two layers with a single
    fitted matrix multiplication, so a representation from the earlier layer is cast into
    the later layer's space directly. The paper's term for the fitted map is mat; it contrasts
    throughout with id, the practice of passing a representation forward unchanged.
  mat / id: The two mappings compared in every experiment. mat is the least-squares matrix
    fitted between a given pair of layers; id is the identity, which is what inspecting a
    hidden layer in the output space implicitly assumes. Also the name of the code repository,
    mat.
  logit lens: The practice of multiplying a hidden representation by the output embedding
    matrix to read a distribution over the vocabulary from an intermediate layer. It presumes
    every layer shares the final layer's coordinate system, which is exactly the assumption
    the identity baseline encodes and this paper measures.
  Precision@k: Whether the token the shortcut ranks first appears among the full model's own
    top k tokens, averaged over positions. A fidelity measure with respect to the unmodified
    model rather than an accuracy against gold labels -- k of 1, 5 and 10 are reported.
  surprisal: The full model's negative log likelihood of whatever token the shortcut predicts.
    Low surprisal means the real model also considered that token likely, so it captures near-misses
    that Precision@k scores as failures.
  early exiting: Stopping a forward pass at an intermediate layer once some confidence criterion
    is met, and reading the prediction from there. It needs a way to turn an intermediate
    representation into an output distribution, which is the slot this paper's mapping drops
    into.
  alternation scheme: A schedule that interleaves real transformer blocks with linear jumps
    -- run a blocks, skip b layers, repeat -- rather than running a prefix of the network
    and then jumping once to the end. Some schedules beat the single jump at equal cost.
  sub-module approximation: Fitting a linear map for one component inside a block -- attention,
    the feed-forward network, or a layer normalization -- and substituting it while leaving
    the rest of the block intact. It localizes which parts of the computation the linear structure
    lives in, rather than treating a block as a unit.
  contextualization: The mixing of information across token positions, which in a transformer
    happens only in attention. It is the property the attention substitution destroys, since
    a per-position linear map cannot move information between positions -- which is why that
    substitution costing so little is the paper's most surprising result.
  r-squared score: The fraction of variance in the target layer's representations that a mapping
    explains, averaged uniformly over coordinates and computed on held-out sentences. Used
    to compare the fitted map against the identity across all layer pairs, and to score candidate
    alternation schedules by multiplying the scores of their jumps.
links_extra:
  trained mappings: https://huggingface.co/sashay/linear-shortcut
---
