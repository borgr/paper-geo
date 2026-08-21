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
    unsorted:
    - Is sentence structure encoded in individual neurons of a translation model?
    - Do single neurons in an NMT encoder represent active versus passive voice?
    - Can you find neurons responsible for syntactic form in a Transformer translator?
  answered_by:
  - no-localized-structure
  - confound-shallow
- ask:
    unsorted:
    - Why do activations of paraphrases correlate so strongly?
    - What confounds inflate neuron correlation between paraphrase pairs?
    - Is high activation similarity between two paraphrases evidence of shared meaning?
  answered_by:
  - confound-shallow
  - random-structure-controls
  - context-confound-lesson
- ask:
    unsorted:
    - Can you make a machine translation system output passive voice by editing activations?
    - Is it possible to control the syntactic form of a translation without retraining?
    - How do you steer an NMT model toward active voice at inference time?
  answered_by:
  - manipulation-works
  - many-neurons-needed
- ask:
    unsorted:
    - How many neurons must be changed to control the output structure of a translation model?
    - Is voice control in NMT localized to a few neurons or distributed?
  answered_by:
  - many-neurons-needed
  - no-localized-structure
- ask:
    unsorted:
    - Does the direction of an activation edit matter, or is any perturbation enough?
    - Would random neuron edits also change the voice of a translation?
    - Is picking which neurons to edit more important than picking the shift vector?
  answered_by:
  - direction-matters-selection-does-not
- ask:
    unsorted:
    - 'Which neurons work best for steering syntactic form: the most or the least paraphrase-invariant
      ones?'
    - Are neurons invariant across paraphrases useless for controlling structure?
    - Do high-correlation neurons or low-correlation neurons give better intervention results?
  answered_by:
  - top-paracorr-better
  - role-overlap
- ask:
    unsorted:
    - Does correlation across paraphrases identify generally important neurons?
    - What happens to BLEU when you zero out the most paraphrase-correlated neurons?
  answered_by:
  - paracorr-ranks-importance
- ask:
    practitioner: Where can I get a dataset of active-passive minimal pair paraphrases with
      reference translations?
    unsorted:
    - Is there a corpus of meaning-preserving syntactic minimal pairs for English?
    - How large is the minimal-paraphrase corpus derived from WMT19 English-German?
  answered_by:
  - context-dataset
  - dataset-counts
- ask:
    practitioner: What should I read about interpreting individual neurons in neural machine
      translation?
    unsorted:
    - Which work analyses neuron activations under paraphrased input rather than across models?
    - Where should I start on probing-free analysis of syntax in NMT representations?
  answered_by:
  - context-methodology
  - context-confound-lesson
- ask:
    unsorted:
    - Did the neuron manipulation work for every syntactic construction tested?
    - Which structural manipulation failed in the neuron-editing experiments?
    - Can adverbial clauses be turned into noun phrases by editing encoder neurons?
  answered_by:
  - clause-to-np-fails
- ask:
    unsorted:
    - How is passive voice detected automatically in German output?
    - How reliable is the automatic passive-voice scorer used to evaluate voice manipulation?
  answered_by:
  - passive-score-baseline
- ask:
    unsorted:
    - How were automatically generated paraphrases filtered for fluency?
    - What was the annotator agreement on paraphrase fluency judgements?
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
