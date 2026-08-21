---
claims:
- id: confound-shallow
  kind: result
  text: 'Strong neuron-level activation correlation between paraphrases in a Transformer encoder
    is largely reproduced by two shallow controls: a random token sequence of matched length,
    or the same sentence stripped of positional encoding. Active-to-passive paraphrasing changes
    sentence length by only 2.0±0.4 tokens, so positional encodings stay similar.'
  scope: fairseq Transformer trained on WMT19 en-de, embedding dimension 1024, sinusoidal
    positional encoding; neurons taken as the outputs of the 6 encoder layer blocks; active-passive
    minimal pairs from the WMT19 dev set, mean-pooled within sentences.
  evidence: Figure 1
- id: no-localized-structure
  kind: result
  text: No individual neuron in the Transformer en-de encoder shows strong activation correlation
    attributable to the active-passive distinction. Sentence structure is therefore not localized
    to a small neuron set, and controlling for shared syntactic construction alone leaves
    correlations between -0.17 and 0.20.
  scope: Pearson correlation on sentence-level mean-pooled activations, active-passive and
    clause/noun-phrase minimal pairs; effects present in all 6 encoder layer blocks but weaker
    off the diagonal and in higher layers.
  evidence: Section 4.3
- id: random-structure-controls
  kind: result
  text: Activations of two unrelated sentences sharing only the syntactic construction (e.g.
    two random active-voice sentences) correlate between -0.17 and 0.20. Correlating a sentence
    against random tokens with positional encoding also stripped gives between -0.27 and 0.31.
  scope: fairseq Transformer en-de encoder outputs, mean-pooled per sentence, WMT19 dev-set
    sentences; the second control rules out neurons with near-constant activations rather
    than testing structure.
  evidence: Section 4.3
- id: manipulation-works
  kind: result
  text: Shifting encoder neuron activations along the difference between average passive-voice
    and average active-voice activations makes the Transformer's German output more similar
    to active-voice references than to passive-voice ones. No retraining is involved and the
    normalized step uses alpha=1.
  scope: Passive-to-active direction on active-passive minimal pairs from the WMT19 dev set;
    BLEU against Google Translate outputs used as references for both forms; average activations
    per form estimated on that same dev set.
  evidence: Figure 2
- id: many-neurons-needed
  kind: result
  text: Controlling the syntactic form of the Transformer's translation by neuron manipulation
    requires modifying at least 50% of the encoder neurons for the maximal effect. The effect
    is not monotone in the number of neurons manipulated in every setting.
  scope: Active-passive and clause/noun-phrase minimal pairs, both manipulation directions;
    non-monotone behaviour appears in the active-to-passive, noun-phrase-to-clause and clause-to-noun-phrase
    settings.
  evidence: Figures 9, 12 and 13
- id: direction-matters-selection-does-not
  kind: result
  text: 'The direction of neuron manipulation matters: 100 random direction vectors are substantially
    worse than shifting along the average-activation difference. Randomly selecting which
    neurons to manipulate is no worse than selecting them by ParaCorr rank.'
  scope: Passive-to-active manipulation on active-passive minimal pairs, BLEU against Google
    Translate references; random selection also holds when constrained to match the controlled
    case's distribution over the 6 encoder layers.
  evidence: Figures 2b and 2c
- id: top-paracorr-better
  kind: result
  text: Manipulating the encoder neurons most correlated across paraphrases flips the translation's
    voice more effectively than manipulating the least correlated ones, by both BLEU against
    active-voice references and automatic passive detection. That is the opposite of the intuition
    that low-correlation, change-sensitive neurons should control the change.
  scope: Passive-to-active manipulation on active-passive minimal pairs from the WMT19 dev
    set; the same ordering appears on 552 held-out active-voice WMT19 test sentences manipulated
    toward passive.
  evidence: Figure 3
- id: paracorr-ranks-importance
  kind: result
  text: Erasing high-ParaCorr encoder neurons (setting activations to zero) degrades translation
    BLEU on 552 held-out WMT19 en-de test sentences more than erasing low-ParaCorr ones. Correlation
    across paraphrases therefore partly ranks neurons by general importance rather than by
    structural role.
  scope: 552 active-voice sentences extracted from the WMT19 en-de test set with their references;
    fairseq Transformer en-de; erasure applied cumulatively from the top or the bottom of
    the ParaCorr rank.
  evidence: Figure 4
- id: role-overlap
  kind: result
  text: For every top-x% cutoff of encoder neurons, the top ParaCorr neurons intersect with
    the top neurons under the token-identity and positional-encoding controls. That role overlap
    explains why they are the most effective neurons to manipulate for a word-order change
    like active-passive.
  scope: Active-passive set, fairseq Transformer en-de encoder; with unparalleled (non-paired)
    active and passive sets, whose per-neuron correlations average only -0.04 to 0.04 over
    100 splits, the top-over-bottom advantage does not reappear.
  evidence: Figure 5
- id: passive-score-baseline
  kind: result
  text: A dependency-and-POS-based German passive-voice detector labels only 37.38% of the
    unmanipulated translations of passive-voice inputs as passive. Its recall is therefore
    limited, making it a trend indicator rather than an absolute measure.
  scope: 'Spacy-based rule: root lemma ''werden'' with an ''oc'' clausal-object child in participle
    form; German outputs of the fairseq en-de Transformer on the active-passive minimal-pair
    set.'
  evidence: Section 5.3
- id: dataset-counts
  kind: result
  text: The minimal-paraphrase corpus derived from the WMT19 English-German dev set contains
    1,169 valid active-to-passive pairs (from 3,107 generated) and 114 valid adverbial-clause-to-noun-phrase
    pairs (from 376 generated) after manual fluency filtering.
  scope: Filtering by two in-house annotators making binary fluency judgements, with 75% observed
    agreement and Cohen's kappa 0.6; crowdsourced Direct Assessment and GPT2/SLOR probability
    thresholds were tried and did not work satisfactorily.
  evidence: Table 2
- id: clause-to-np-fails
  kind: result
  text: 'Manipulating neurons to turn an adverbial-clause input into a noun-phrase translation
    does not succeed: the output stays closer to the clause form. Only 114 clause/noun-phrase
    pairs passed filtering, against 1,169 active-passive pairs, which the authors offer as
    one possible cause.'
  scope: Clause/noun-phrase minimal pairs from the WMT19 dev set; both manipulation directions
    run with alpha=1; the reverse noun-phrase-to-clause direction does work.
  evidence: Figure 13
- id: context-methodology
  kind: context
  text: The minimal-paraphrase methodology of Patel, Choshen and Abend analyses sentence-structure
    encoding by feeding one translation model paraphrased input pairs and correlating neuron
    activations. It varies the input rather than comparing models or probing word-level representations.
  scope: Demonstrated on a single Transformer en-de translation model and two constructions
    (active-passive, adverbial clause vs. noun phrase); as of publication in 2022, prior neuron-correlation
    work varied the model or used probing rather than varying the input.
  evidence: Section 7
- id: context-confound-lesson
  kind: context
  text: Patel, Choshen and Abend argue that any neuron-level correlation analysis must control
    for token-identity and positional-encoding confounds, because these low-level input features
    can account for most of the apparent activation similarity.
  scope: Argued from a Transformer with sinusoidal positional encoding and residual connections,
    where positional information propagates through the layers; the size of the confound in
    models with learned or relative position encodings is untested.
  evidence: Section 4.3
- id: context-dataset
  kind: context
  text: Patel, Choshen and Abend release a semi-automatic engine and corpus of meaning-preserving
    minimal-pair paraphrases, covering active-to-passive voice and adverbial-clause-to-noun-phrase.
    The pairs are built to satisfy similar meaning, minimal change, controlled change and
    an available reference translation.
  scope: English source sentences with German reference translations from WMT19; two constructions
    only; generation is rule-based over dependency parses, semantic role labels, BERT word
    insertion and GPT2 sentence probability, and output requires manual fluency filtering.
  evidence: Section 2
qa:
- ask:
    plain: can you point to particular neurons in a translation model that handle whether
      a sentence is active or passive?
    jargon: is the active-passive distinction localized to individual encoder neurons in a
      Transformer NMT model?
    task: how do I find the neurons that encode sentence structure in a translation encoder?
    practitioner: if I want to locate a small set of syntax neurons in my translation model,
      is that a realistic goal?
  answered_by:
  - no-localized-structure
  - confound-shallow
- ask:
    plain: if two ways of saying the same thing light up a network almost identically, does
      that mean it has captured the meaning?
    jargon: what token-identity and positional-encoding confounds inflate neuron activation
      correlation between paraphrase pairs?
    task: what controls do I need before reading a high activation correlation between paraphrases
      as evidence of shared structure?
    practitioner: my paraphrase pairs give near-identical activations, should I trust that
      as a representation finding?
  answered_by:
  - confound-shallow
  - random-structure-controls
  - context-confound-lesson
- ask:
    plain: can you push a translation system to say something in active voice instead of passive
      by nudging its internal numbers?
    jargon: can encoder activation shifts steer the syntactic form of NMT output without retraining?
    task: how do I change the voice of a translation model's output at inference time without
      fine-tuning it?
    practitioner: is editing encoder activations a workable way to control voice in my en-de
      translation system?
  answered_by:
  - manipulation-works
  - many-neurons-needed
- ask:
    plain: how many internal units do you have to change to alter the grammatical form of
      a translation?
    jargon: is control of output voice in an NMT encoder distributed across neurons or confined
      to a small subset?
    task: how many encoder neurons do I need to modify to reliably flip a translation's voice?
    practitioner: can I get away with editing a handful of neurons, or does voice control
      need most of the encoder?
  answered_by:
  - many-neurons-needed
  - no-localized-structure
- ask:
    plain: when you nudge a network's internal values, does the direction of the nudge matter
      or would any disturbance do?
    jargon: does the shift vector or the neuron selection criterion drive the effect of activation
      manipulation on output voice?
    task: how do I choose the shift vector and the neurons when editing activations to change
      a translation's syntax?
    practitioner: should I spend my effort picking the right neurons or the right direction
      to shift them in?
  answered_by:
  - direction-matters-selection-does-not
- ask:
    plain: to change a sentence's grammar by editing a network, are you better off touching
      the units that stay the same across rewordings or the ones that change?
    jargon: do high-ParaCorr or low-ParaCorr encoder neurons give stronger voice-flipping
      interventions?
    task: which neurons should I pick for an activation edit that changes the syntactic form
      of a translation?
    practitioner: my intuition says to edit the change-sensitive neurons, is that the right
      bet for controlling voice?
  answered_by:
  - top-paracorr-better
  - role-overlap
- ask:
    plain: do the units that behave the same way across reworded sentences turn out to be
      the generally important ones?
    jargon: does correlation across paraphrases rank encoder neurons by general importance,
      as measured by BLEU under ablation?
    task: how do I tell whether a neuron ranking reflects a structural role or just overall
      importance to translation quality?
    practitioner: can I use paraphrase-based correlation as a cheap importance score for pruning
      or analysis?
  answered_by:
  - paracorr-ranks-importance
- ask:
    plain: is there a ready-made collection of English sentence pairs that mean the same thing
      but differ in one grammatical way?
    jargon: is there a corpus of meaning-preserving syntactic minimal pairs with reference
      German translations, and how many pairs does it hold?
    task: where do I get active-passive and clause-to-noun-phrase minimal pairs with reference
      translations for analysing a translation model?
    practitioner: is the WMT19-derived minimal-paraphrase corpus large enough for my analysis?
  answered_by:
  - context-dataset
  - dataset-counts
- ask:
    plain: what should I read first about studying how a translation network handles sentence
      structure by changing its input rather than its weights?
    jargon: which work analyses syntax in NMT representations by correlating neuron activations
      across paraphrased input instead of probing or cross-model comparison?
    task: where do I start if I want to study syntax encoding in a translation model without
      training a probe?
  answered_by:
  - context-methodology
  - context-confound-lesson
- ask:
    plain: did editing internal units change every kind of grammatical rewrite that was tried,
      or did some fail?
    jargon: does encoder activation manipulation transfer from active-passive voice to the
      adverbial-clause to noun-phrase construction?
    task: can I use activation editing to turn an adverbial clause into a noun phrase in a
      German translation?
    practitioner: before I try activation editing on my own construction, is there a construction
      where it did not work?
  answered_by:
  - clause-to-np-fails
- ask:
    plain: how do you automatically check whether a German sentence came out in passive voice,
      and how well does that check work?
    jargon: how reliable is the dependency-and-POS-based German passive-voice detector used
      to score voice manipulation?
    task: how do I measure whether my model's German output is passive, and how much should
      I trust the score?
    practitioner: can I rely on an automatic German passive detector as an absolute metric
      for my voice experiments?
  answered_by:
  - passive-score-baseline
- ask:
    plain: how were the automatically generated sentence pairs checked before being kept?
    jargon: what manual fluency filtering was applied to the generated active-passive and
      clause-to-noun-phrase paraphrase pairs, and how many survived?
    task: how do I filter automatically generated minimal-pair paraphrases down to usable
      ones?
  answered_by:
  - dataset-counts
key: patel2022neurons
coined: ParaCorr
gloss: neuron-level activation correlation between a sentence and its paraphrase in the same
  model
one_liner: Correlating individual neuron activations between minimal-pair paraphrases in a
  Transformer English-German translation model shows the similarity is mostly explained by
  shared tokens and positional encodings, yet shifting a large fraction of encoder neurons
  still flips the output's voice.
misreadings:
- 'Finding no neuron-level signal for the active-passive distinction is not evidence that
  the Transformer fails to encode voice: the manipulation experiments show the distinction
  is encoded and used, apparently in a distributed manner.'
- 'Successful voice manipulation does not mean a small set of interpretable voice neurons
  was found: at least 50% of encoder neurons had to be shifted, and random neuron subsets
  worked as well as ParaCorr-selected ones.'
- ParaCorr is not a measure of a neuron's structural role; erasure experiments show high-ParaCorr
  neurons are the ones most important for overall translation quality, so the ranking partly
  tracks general importance.
- 'The negative correlation results should not be read as proof of absence: the manipulation
  is linear in a non-linear model, so positive results indicate a causal effect while negative
  ones are weaker evidence.'
- BLEU against Google Translate outputs is a proxy reference, not a gold measure of syntactic
  form, which is why an automatic passive-voice detector and a native-speaker qualitative
  analysis are added.
terminology:
  ParaCorr: Pearson correlation between a neuron's activations over a set of source sentences
    and its activations over the matched paraphrased sentences, in the same model.
  ModelCorr: Pearson correlation between neuron activations of two models trained with different
    random seeds on the same input sentences.
  PosCorr: Pearson correlation between neuron activations on a sentence set and on random
    token sequences of the same lengths, isolating the effect of shared positional encodings.
  TokenCorr: Pearson correlation between neuron activations on a sentence set and on the same
    sentences with positional encoding removed, isolating the effect of token identity.
  Minimal paraphrase pair: A pair of sentences with the same meaning differing by a single,
    consistently applied structural change (active vs. passive voice, or adverbial clause
    vs. noun phrase), with a reference translation available.
  Passive score: 'The percentage of German translations automatically labelled passive by
    a rule over dependency parse and POS tags: root lemma ''werden'' with a participle clausal-object
    child.'
  Intra-sentence aggregation: Pooling a sentence's per-token neuron activations into one value
    per sentence so that activation samples from sentence sets of different token counts can
    be correlated.
links_extra:
  code: https://github.com/galpatel/minimal-paraphrases
  arxiv: https://arxiv.org/abs/2110.03067
---
