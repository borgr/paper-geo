---
key: slobodkin2022semantics
coined: SASA / SACrA
gloss: 'scene-aware self-attention and scene-aware cross-attention: masking one Transformer
  attention head so it attends only within UCCA semantic scenes'
one_liner: SASA and SACrA inject semantics into NMT Transformers without adding parameters,
  by masking a single attention head so it attends only to tokens sharing a UCCA scene — in
  the encoder's self-attention (SASA) or the decoder's cross-attention (SACrA).
claims:
- id: sasa-beats-transformer
  kind: result
  text: Scene-Aware Self-Attention (SASA) raises average BLEU over the vanilla Transformer
    for all four language pairs tested. The averages move from 21.66 to 21.77 on En-De, 20.81
    to 21.14 on En-Ru, 11.49 to 11.67 on En-Fi, and 8.36 to 8.54 on En-Tr.
  scope: 4-layer Transformers of internal size 256 on WMT data for En-De, En-Ru, En-Fi and
    En-Tr, averaged over all newstests since 2012; UCCA parses from a pretrained BERT-based
    TUPA parser; layer and head count tuned on En-De and reused.
  evidence: Table 3
- id: sasa-beats-syntax
  kind: result
  text: SASA outperforms the syntax-infused PASCAL and UDISCAL masks on average BLEU for all
    four language pairs, and the sign-test over all test sets across all languages rejects
    both syntactic baselines at p<0.01.
  scope: PASCAL reimplemented post-softmax on 5 heads of encoder layer 1; UDISCAL is the authors'
    UD-distance-scaled adaptation on 1 head of layer 1; BLEU and chrF on WMT newstests for
    En-De, En-Ru, En-Fi, En-Tr.
  evidence: Table 3 and Table 5
- id: sasa-sign-test
  kind: result
  text: 'SASA''s gains over the vanilla Transformer are consistent rather than test-set-specific:
    a sign-test over all newstests across all four language pairs gives p<0.01, and the same
    trend holds under chrF.'
  scope: Sign-test pools test sets across En-De, En-Ru, En-Fi and En-Tr; the effect sizes
    per test set are small (often under 0.5 BLEU) and SASA does not win on every individual
    newstest.
  evidence: Table 5, with chrF in Table 7
- id: combination-distant-languages
  kind: result
  text: 'Combining the semantic SASA head with the syntactic UDISCAL head helps only the pairs
    typologically distant from English: En-Fi and En-Tr improve over each mask alone, while
    En-De and En-Ru hardly benefit. The sign-test on En-Fi and En-Tr gives p=0.02 versus SASA
    and p=0.0008 versus UDISCAL.'
  scope: Combination reuses the hyperparameters tuned for each mask separately; the sign-test
    for the combination is computed only on the En-Fi and En-Tr test sets, and the gains there
    are small.
  evidence: Table 3 and Section 4.3
- id: combination-margin
  kind: result
  text: At its best the combined SASA+UDISCAL model beats SASA alone by 0.52 BLEU and UDISCAL
    alone by 0.69 BLEU (0.46 and 0.43 chrF), rather than by a uniform margin across test sets.
  scope: Best-case margins on test sets of the typologically distant pairs En-Fi and En-Tr;
    average-level gains are smaller.
  evidence: Section 1, with per-test-set scores in Table 3 and Table 7
- id: sacra-decoder
  kind: result
  text: Scene-Aware Cross-Attention (SACrA) injects source-side scene structure through the
    decoder and improves average BLEU over the vanilla Transformer on 3 of 4 language pairs
    (sign-test p=0.047). On En-Fi it even beats SASA, 11.72 versus 11.67.
  scope: SACrA uses 1 head on decoder layers 2 and 3, tuned on the En-De development set;
    En-De is the pair where SACrA falls below the Transformer (21.36 versus 21.66 average
    BLEU), and SASA is better overall.
  evidence: Table 3 and Table 5
- id: binary-mask-best
  kind: result
  text: A hard binary scene mask works at least as well as softer alternatives for SASA. Neither
    a scaled mask that lets out-of-scene attention through at weight C nor a normally-distributed
    mask over scene-graph distance beats it on the WMT En-De newstests.
  scope: Grid searches over C in {0.05, 0.1, 0.15, 0.2, 0.3, 0.5} for the scaled mask and
    C in {0.1, 0.2, 0.5, sqrt(0.5)} for the normally-distributed mask, evaluated on En-De
    only; the best variant of each was compared to the binary mask.
  evidence: Table 1
- id: one-head-one-layer
  kind: result
  text: Masking a single attention head in a single mid-encoder layer is better for SASA than
    masking many. Layer 4 alone gives the best En-De validation BLEU, 20.37 against 20.1-20.33
    for the other single-layer and layer-pair settings, and adding heads beyond 1 gave no
    further benefit.
  scope: Tuning on the En-De newstest2013 development set with a 4-layer encoder, over single
    layers 1-4 and pairs (1,2), (2,3), (3,4); the resulting hyperparameters were transferred
    unchanged to En-Ru, En-Fi and En-Tr.
  evidence: Table 4
- id: long-dependency-challenge
  kind: result
  text: On challenge sets of sentences with long dependencies, SASA's BLEU gain over the Transformer
    is only slightly larger than on the full newstests, with gains of up to 1.41 BLEU points.
    The improvement therefore does not come specifically from resolving long-distance syntax.
  scope: Challenge sets extracted from each newstest by the Choshen and Abend (2019) methodology,
    plus Wikipedia, Mozilla, EUbookshop and bible corpora for En-Tr; BLEU only.
  evidence: Table 8 and Section 4.1
- id: semsplit-negative
  kind: result
  text: The SemSplit pipeline, which splits source sentences into UCCA scenes and translates
    each piece separately, falls well below the vanilla Transformer under automatic metrics.
    Average BLEU is 15.50 versus 21.66 on En-De and 7.35 versus 11.49 on En-Fi.
  scope: Reimplementation of the Sulem et al. (2020) pipeline evaluated with BLEU and chrF,
    which penalise sentence separation, in a normal- rather than low-resource NMT setting;
    the original work reported human evaluation in a pseudo-low-resource scenario.
  evidence: Table 6
- id: parameter-free
  kind: context
  text: SASA and SACrA add no parameters to the Transformer. They replace an existing attention
    head's scores with scene-masked scores computed from an off-the-shelf UCCA parse of the
    source, leaving model size and inference architecture unchanged.
  scope: Cost is not zero end-to-end — source sentences must be parsed in advance by a UCCA
    parser, and average training time rose from 21.8 to 26.5 hours for SASA in the paper's
    setup.
  evidence: Section 5 and Section 3
- id: first-semantic-transformer-nmt
  kind: context
  text: Semantics-aware Attention Improves Neural Machine Translation is, to its authors'
    knowledge, the first work to inject semantic graph structure into a Transformer NMT model,
    where prior structure-aware Transformer work used syntax instead.
  scope: Novelty as stated by the authors at *SEM 2022 publication. Earlier semantic-injection
    results targeted RNN-based NMT, and earlier structure-aware Transformer work used Universal
    Dependencies.
  evidence: Section 4.2
- id: semantics-higher-layers
  kind: context
  text: Semantic scene masks help most when injected into a higher encoder layer, while syntactic
    masks help most in the first layer. The authors read this contrast as evidence that semantics
    supports more complex generalisation than syntax in Transformer NMT.
  scope: Hyperparameter tuning of a 4-layer encoder on the En-De development set only — SASA
    best at layer 4, PASCAL and UDISCAL tuned to layer 1 — and an interpretation rather than
    a controlled probing study.
  evidence: Table 4 and Section 3
qa:
- ask:
    plain: how can meaning structure from a sentence analysis be built into a machine translation
      model?
    jargon: how is UCCA scene structure injected into Transformer NMT self-attention without
      extra parameters?
    task: how do I add semantic structure to my Transformer translation model without changing
      its size or inference code?
    practitioner: is there a way to use a semantic parser to improve my translation system
      without training extra parameters?
  answered_by:
  - parameter-free
  - sasa-beats-transformer
- ask:
    plain: does giving a translation model sentence-meaning structure actually produce better
      translations?
    jargon: what BLEU improvement does scene-masked self-attention give over a vanilla Transformer
      baseline across language pairs?
    task: how much translation quality can I expect to gain by masking one attention head
      with semantic scene structure?
    practitioner: are the BLEU gains from semantics-aware attention big and consistent enough
      to be worth adopting?
  answered_by:
  - sasa-beats-transformer
  - sasa-sign-test
- ask:
    plain: for translation models, is it better to feed in grammar structure or meaning structure?
    jargon: does UCCA scene masking outperform dependency-based attention masking such as
      PASCAL and UDISCAL in Transformer NMT?
    task: I already mask attention with parse trees for translation — would switching to semantic
      scenes help more?
    practitioner: should I use a semantic graph or a syntactic parse to guide attention in
      my translation model?
  answered_by:
  - sasa-beats-syntax
  - semantics-higher-layers
- ask:
    plain: does using both grammar structure and meaning structure together help a translation
      model more than either alone?
    jargon: does combining a UD-based syntactic attention mask with a UCCA scene mask improve
      BLEU over either mask alone, and for which typologies?
    task: how do I decide whether to stack a syntactic mask and a semantic mask in the same
      encoder for my language pair?
    practitioner: my target language is typologically far from English — would combining syntactic
      and semantic attention masks pay off?
  answered_by:
  - combination-distant-languages
  - combination-margin
- ask:
    plain: can meaning structure from the input sentence be fed into the part of a translation
      model that writes the output?
    jargon: does injecting source-side UCCA scene structure through decoder cross-attention
      improve BLEU compared with encoder self-attention masking?
    task: where do I attach a source semantic mask, encoder self-attention or decoder cross-attention?
    practitioner: should I put the scene mask on the encoder or the decoder side of my translation
      model?
  answered_by:
  - sacra-decoder
  - sasa-beats-transformer
- ask:
    plain: when you restrict what a translation model can look at, is a strict on-off restriction
      better than a gentle one?
    jargon: for scene-based attention masking, does a hard binary mask beat a scaled mask
      or a Gaussian over graph distance?
    task: how do I choose the mask shape when constraining an attention head with semantic
      scene boundaries?
    practitioner: should I let some out-of-scene attention leak through my mask, or zero it
      out completely?
  answered_by:
  - binary-mask-best
- ask:
    plain: how much of a translation model should be changed to feed in sentence structure,
      and which part of it?
    jargon: how many attention heads and which encoder layer should carry a UCCA scene mask
      in Transformer NMT?
    task: how do I pick the layer and number of heads to apply a linguistic attention mask
      to?
    practitioner: do I need to mask every encoder layer, or is one head in one layer enough?
  answered_by:
  - one-head-one-layer
  - semantics-higher-layers
- ask:
    plain: do meaning-based translation improvements come mainly from handling very long sentences
      with far-apart words?
    jargon: are scene-masked attention gains concentrated on challenge sets with long-distance
      dependencies?
    task: how do I check whether a semantics-aware translation gain comes from long-distance
      dependency resolution?
    practitioner: my inputs have lots of long-range dependencies — is that where semantic
      attention masking pays off most?
  answered_by:
  - long-dependency-challenge
- ask:
    plain: is it a good idea to break a sentence into smaller meaning units and translate
      each one separately?
    jargon: how does a UCCA-based scene-splitting inference pipeline compare with a vanilla
      Transformer on BLEU?
    task: how do I translate long sentences — split them into semantic clauses first, or feed
      them whole?
    practitioner: should I preprocess my source sentences by splitting them into semantic
      scenes before translating?
  answered_by:
  - semsplit-negative
- ask:
    plain: what should I read first about using sentence-meaning structure in machine translation?
    jargon: which work first injected semantic graph structure, rather than syntax, into a
      Transformer NMT model?
    task: where do I start reading if I want to bring semantic representations into neural
      translation?
  answered_by:
  - first-semantic-transformer-nmt
  - parameter-free
- ask:
    plain: what kinds of translation mistakes get fixed when a model is given the meaning
      structure of the sentence?
    jargon: which error types account for the BLEU gains from UCCA scene-masked attention
      in Transformer NMT?
    practitioner: will semantics-aware attention fix the specific errors I see, or just move
      average BLEU?
  answered_by:
  - long-dependency-challenge
  - sasa-beats-transformer
terminology:
  UCCA scene: 'A unit of the Universal Cognitive Conceptual Annotation graph corresponding
    to an event: one main relation, either a Process (action) or a State, together with at
    least one Participant.'
  Scene-aware mask: A binary matrix over source tokens whose entry is 1 when the two tokens
    share a UCCA scene and 0 otherwise, multiplied element-wise into an attention head's post-softmax
    scores; a token in several scenes may attend to all of them.
  SASA: 'Scene-Aware Self-Attention: one encoder self-attention head whose post-softmax scores
    are multiplied by a binary UCCA scene mask of the source sentence.'
  SACrA: 'Scene-Aware Cross-Attention: a decoder cross-attention head whose keys are the encoder
    output projected through the source''s binary scene mask, so tokens sharing a set of scenes
    receive identical keys.'
  UDISCAL: 'UD-Distance-Scaled mask: a syntactic attention mask whose value decays as a normal
    density in the undirected Universal Dependencies graph distance between two tokens, generalising
    PASCAL''s parent-only mask.'
  SemSplit: A pipeline that, at inference time, splits a source sentence into separate sentences
    by Direct Semantic Splitting, translates each independently, and concatenates the outputs
    with periods.
misreadings:
- The gains from scene-aware attention are consistent across test sets but small — typically
  a few tenths of a BLEU point on average — not the multi-point improvements a "consistent
  improvement over syntax-aware models" phrasing might suggest.
- 'Combining semantic and syntactic masks is not generally better: it helps En-Fi and En-Tr,
  barely changes En-De and En-Ru, and combining SACrA with UDISCAL is often worse than the
  plain Transformer.'
- 'Scene-aware self-attention was not shown to work by solving long-distance dependencies:
  the gain on long-dependency challenge sets is only slightly larger than on ordinary test
  sets.'
- The negative result for the SemSplit sentence-splitting pipeline is a BLEU/chrF result in
  a normal-resource setting, and does not refute the original human-evaluation findings for
  that pipeline in a pseudo-low-resource setting.
- 'SASA is not a claim that more attention masking is better: masking 1 head in 1 encoder
  layer was optimal, and using more heads gave no additional benefit.'
---
