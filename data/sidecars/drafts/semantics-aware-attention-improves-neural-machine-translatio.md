<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced) + a targeted repair. Every claim, number
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

Then promote it:  python scripts/draft_sidecars.py --accept semantics-aware-attention-improves-neural-machine-translatio

Stamp: spec=8f05813a4658 checks=pass body=2287e4596d25
-->
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
- q:
  - How can semantic structure be added to a Transformer machine translation model?
  - Is there a way to inject semantics into NMT attention without adding parameters?
  - What does scene-aware attention do in a translation Transformer?
  answers:
  - parameter-free
  - sasa-beats-transformer
- q:
  - Does adding semantics actually improve BLEU in neural machine translation?
  - How much does scene-aware self-attention improve translation quality?
  - What BLEU gains does SASA get over a vanilla Transformer?
  answers:
  - sasa-beats-transformer
  - sasa-sign-test
- q:
  - Is semantic structure more useful than syntactic structure for Transformer MT?
  - Does UCCA-based masking beat dependency-based masking like PASCAL?
  - 'Semantics versus syntax for structure-aware neural machine translation: which wins?'
  answers:
  - sasa-beats-syntax
  - semantics-higher-layers
- q:
  - Does combining syntax and semantics in the same translation model help?
  - When is it worth using both a UD mask and a UCCA scene mask?
  - Do typologically distant language pairs benefit more from combined syntactic and semantic
    masks?
  answers:
  - combination-distant-languages
  - combination-margin
- q:
  - Can source-side semantics be injected through the decoder rather than the encoder?
  - What is scene-aware cross-attention and does it help translation?
  - Is encoder or decoder injection better for semantic structure in NMT?
  answers:
  - sacra-decoder
  - sasa-beats-transformer
- q:
  - Should an attention mask be hard binary or softly scaled by graph distance?
  - Does allowing some out-of-scene attention through help scene-aware masking?
  - Which mask shape works best for UCCA scene masking in a Transformer?
  answers:
  - binary-mask-best
- q:
  - How many attention heads and which layer should a linguistic mask be applied to?
  - Does masking all encoder layers work better than masking one for scene-aware attention?
  - Where in the encoder should UCCA scene information be injected?
  answers:
  - one-head-one-layer
  - semantics-higher-layers
- q:
  - Does scene-aware attention specifically fix long-distance dependency errors in translation?
  - How does SASA perform on challenge sets with long dependencies?
  - Are the gains from semantic masking concentrated on syntactically hard sentences?
  answers:
  - long-dependency-challenge
- q:
  - Does splitting sentences into semantic scenes before translating help BLEU?
  - How does the SemSplit sentence-splitting pipeline compare to a plain Transformer?
  - Is UCCA-based preprocessing at inference time a good idea for NMT?
  answers:
  - semsplit-negative
- q:
  - What work should I read on incorporating linguistic structure into neural machine translation?
  - Which paper first put semantic graphs into a Transformer MT model?
  - Where should I start reading about semantics-aware neural machine translation?
  answers:
  - first-semantic-transformer-nmt
  - parameter-free
- q:
  - What kind of translation errors does scene-aware attention fix?
  - Does semantic scene information help word-sense disambiguation in translation?
  answers:
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
