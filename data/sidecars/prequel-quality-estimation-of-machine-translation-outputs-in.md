---
key: donyehiya2022prequel
coined: PreQuEL
gloss: predicting machine-translation quality from the source sentence alone, before translating
one_liner: PreQuEL predicts how well a sentence will be machine-translated from the source
  text alone, before any translation is produced, and a data-augmentation method that labels
  parallel corpora with automatic metric scores makes it work well enough to approach a full
  quality-estimation system.
links_extra:
  code: https://github.com/shachardon/PreQuEL
  arxiv: https://arxiv.org/abs/2205.09178
terminology:
  PreQuEL: 'Pre-(Quality-Estimation) Learning: predicting the quality that a machine-translation
    system will produce for a given source sentence, using only that source sentence and never
    the translation.'
  System-specific PreQuEL variant: Predicting translation quality for one named MT system
    whose outputs supplied the training labels, as opposed to predicting quality for state-of-the-art
    MT in general.
  Augmentation from parallel corpora: Re-translating an existing parallel corpus with the
    target MT system and using automatic metric scores (COMET, ChrF++, BERTScore) of those
    translations as free training labels for a quality predictor.
  Simple Aug: The baseline TransQuest-style PreQuEL regressor first intertrained on COMET-labelled
    augmented data and then fine-tuned on human direct-assessment scores.
  Multitask (PreQuEL): A PreQuEL model with one classifier head per automatic metric, trained
    to predict COMET, ChrF++ and BERTScore alongside the human direct-assessment score.
claims:
- id: task-context
  kind: context
  text: PreQuEL introduces the task of predicting machine-translation quality from the source
    sentence alone, before any translation exists, shifting quality estimation's focus from
    the output onto properties of the input text.
  scope: Introduced at EMNLP 2022; earlier quality-estimation work required the translation,
    and Sun et al. (2020) had treated source-only prediction as a dataset artifact rather
    than a task.
- id: why-read
  kind: context
  text: PreQuEL is a starting point for readers deciding between paid machine translation
    and human translation. A source-only quality predictor can be run before any translation
    cost is incurred.
  scope: Motivational framing for the sentence-level setting studied; no cost or deployment
    study is reported, and absolute correlations remain modest.
- id: main-endezh
  text: The best PreQuEL model reaches Pearson's r of 0.336 with human direct-assessment scores
    on English-German, against 0.135 for a negated-sentence-length baseline.
  scope: WMT 2020 sentence-level DA data, 7K training sentences, single fairseq MT system;
    Multitask model, RoBERTa-large, 3 seeds.
  evidence: Table 1
- id: gap-to-qe
  text: The best source-only PreQuEL model trails TransQuest, a quality-estimation system
    that sees the actual translation, by only 4.5 Pearson points on English-German (0.336
    vs 0.381).
  scope: 'WMT 2020 en-de DA data; TransQuest run with official code scored below its published
    numbers. On et-en the gap is far larger: 0.602 vs 0.767.'
  evidence: Table 1
- id: augmentation-gain
  text: Intertraining on parallel-corpus data automatically labelled with COMET raises PreQuEL's
    en-de correlation from 0.196 to 0.315, and the multi-task variant reaches 0.336.
  scope: en-de WMT 2020 DA; augmentation from WMT-News, bible-uedin, Tatoeba and GlobalVoices
    re-translated with OPUS-MT/Marian, 3 seeds.
  evidence: Table 1
- id: aug-helps-qe
  text: 'The same COMET-labelled augmentation also improves ordinary quality estimation: TransQuest
    on en-de rises from 0.381 (std 0.043) to 0.429 (std 0.008) Pearson''s r when intertrained
    on the augmented data.'
  scope: en-de WMT 2020 DA, TransQuest architecture, 3 seeds; the gain is in both correlation
    and seed-to-seed stability.
  evidence: Section 9.1
- id: cross-system
  text: A PreQuEL model supervised only with Marian outputs correlates 0.610 on Facebook FAIR
    outputs versus 0.652 on Marian's own, a drop of 4.2 points. That exceeds the 0.535 bound
    implied by inter-system label similarity.
  scope: COMET-labelled augmented data rather than human DA labels, en-de, two neural MT systems;
    the two systems' COMET labels correlate 0.60-0.82 across datasets.
  evidence: Section 7.1
- id: target-specific
  text: 'PreQuEL learns target-language-specific difficulty: an en-de model correlates 0.377
    with en-de gold scores but only 0.260 with en-zh, while the en-zh model scores 0.577 on
    en-zh and 0.140 on en-de.'
  scope: Simple Aug models, source sentences shared between the en-de and en-zh WMT 2020 development
    DA sets, augmentation from NewsTests and bible-uedin.
  evidence: Table 3
- id: over-weights-features
  text: PreQuEL predictions correlate more strongly with standard NLP features than the human
    gold scores do, for example -0.2894 versus -0.1305 with sentence length. The model therefore
    over-estimates those features' importance.
  scope: Simple Aug on the en-de DA development set; only statistically significant features
    reported, including UD parse depth, verb count, advcl and case edge counts and n-gram
    probabilities.
  evidence: Table 4
- id: syntax-parser
  text: Concatenating a UD parser to the PreQuEL encoder raises en-de correlation to 0.326
    against 0.265 for a same-size two-encoder control without a parser. The smaller Multitask
    model still beats both at 0.336.
  scope: en-de WMT 2020 DA; Combined+ and Combined- both use augmentation intertraining and
    double the parameter count of the Simple model (355M x 3 x 2).
  evidence: Table 1
- id: meaning-over-order
  text: On a German word-ordering challenge set, PreQuEL predictions correlate more highly
    between sentence pairs that share meaning (0.901 and 0.936) than between pairs that share
    syntax (0.687 and 0.641). Meaning matters more to the model than word order.
  scope: Second German word-ordering challenge set of Choshen and Abend (2021), de-en Simple
    model trained on COMET-labelled augmented data rather than human DA labels.
  evidence: Table 7
- id: transformation-probe
  text: Used as an analytic probe, PreQuEL scores are almost unchanged by swapping person
    names (-0.03) or numerical values (-0.03), but drop for Yoda-style reordering (-0.85)
    and random word deletion (-0.62). Back-translated English sentences score higher (+0.11).
  scope: en-de Simple Aug on NL-Augmenter transformations of DA source sentences; means over
    the 127-996 sentences each transformation actually changed, and the automatic transformations
    add noise.
  evidence: Table 2
- id: hter-vs-da
  text: 'Predicting translation quality from the source alone is harder for direct-assessment
    labels than for HTER: an en-de source-only model reaches 0.196 on DA versus 0.322 on HTER.'
  scope: en-de WMT 2020 DA and HTER data, Simple architecture, 3 seeds each; supports that
    switching the metric to DA does not remove source-only predictability.
  evidence: Section 9.2
- id: domain-matters
  text: PreQuEL correlations vary widely by domain and degrade out of domain, from 0.72 in-domain
    and 0.36 out-of-domain on bible-uedin to 0.36 and 0.25 on Tatoeba.
  scope: Single Simple instances without ensembling, trained on ChrF++ augmentations, evaluated
    on development sets of NewsTests, bible-uedin, GlobalVoices and Tatoeba.
  evidence: Table 5
qa:
- ask:
    plain: can you tell how badly a sentence will be translated before you translate it?
    jargon: can machine-translation quality be predicted from the source segment alone, with
      no hypothesis translation available?
    task: how do I score which source sentences will translate poorly before running them
      through an MT engine?
    practitioner: should I trust a source-only translation difficulty score to flag risky
      sentences in my input file?
  answered_by:
  - task-context
  - main-endezh
- ask:
    plain: which research first framed predicting translation quality from the source sentence
      only?
    jargon: what work introduced source-only quality prediction as a task distinct from quality
      estimation of MT output?
    task: where do I start reading if I need to decide up front whether to machine translate
      a document or pay a human translator?
    practitioner: is there a paper I can cite for choosing between paid MT and human translation
      before any translation exists?
  answered_by:
  - task-context
  - why-read
- ask:
    plain: how much accuracy do you lose by predicting translation quality without seeing
      the translation?
    jargon: what is the Pearson gap between source-only quality prediction and a quality-estimation
      model that conditions on the MT hypothesis?
    task: how do I know whether it is worth generating the translation first before estimating
      its quality?
    practitioner: if I skip running the MT system, how much worse will my quality estimate
      be?
  answered_by:
  - gap-to-qe
  - main-endezh
- ask:
    plain: does labelling a parallel corpus with an automatic translation metric give useful
      extra training data for quality prediction?
    jargon: does intertraining on COMET-scored parallel data improve source-only quality prediction
      and quality estimation?
    task: how do I get more training data for a translation quality predictor when human quality
      scores are scarce?
    practitioner: should I build a synthetic training set with an automatic MT metric instead
      of paying for more human quality judgements?
  answered_by:
  - augmentation-gain
  - aug-helps-qe
- ask:
    plain: can training data labelled by an automatic translation metric make an existing
      quality-scoring model better?
    jargon: does COMET-labelled intertraining raise TransQuest's Pearson correlation on WMT
      2020 English-German?
    task: how do I improve an off-the-shelf quality estimation model without collecting new
      human annotations?
    practitioner: is it worth intertraining my quality estimation system on automatically
      scored parallel data?
  answered_by:
  - aug-helps-qe
- ask:
    plain: if a difficulty predictor is trained on one translation engine's output, does it
      still work for a different engine?
    jargon: how well does a source-only quality predictor supervised on one MT system's scores
      transfer to another system's outputs?
    task: how do I reuse a translation difficulty model when I switch MT providers?
    practitioner: can I apply a difficulty predictor trained on one MT engine to the engine
      I actually use in production?
  answered_by:
  - cross-system
- ask:
    plain: is a sentence that is hard to translate into German also hard to translate into
      Chinese?
    jargon: is source-side translation difficulty target-language-specific, or does it transfer
      across language pairs?
    task: how do I predict translation difficulty for a new target language without training
      a separate model?
    practitioner: do I need a separate difficulty model per target language, or will one English-side
      model cover them all?
  answered_by:
  - target-specific
- ask:
    plain: what makes a sentence hard for a machine to translate, and do simple things like
      length explain it?
    jargon: do source-only quality predictions over-weight surface features such as sentence
      length and n-gram probability relative to human DA scores?
    task: how do I tell whether my translation difficulty scores are just tracking sentence
      length?
    practitioner: should I worry that a source-only difficulty score is really just a length
      heuristic in disguise?
  answered_by:
  - over-weights-features
  - transformation-probe
- ask:
    plain: does giving a translation difficulty model an explicit grammar analysis of the
      sentence help?
    jargon: does concatenating a UD dependency parser to the encoder improve source-only quality
      prediction over a same-size two-encoder control?
    task: how do I add syntactic structure to a translation difficulty predictor, and does
      it pay off?
    practitioner: is it worth wiring a dependency parser into my source-side quality model?
  answered_by:
  - syntax-parser
  - meaning-over-order
- ask:
    plain: does a translation difficulty score react to what a sentence means or just to the
      order of its words?
    jargon: on German word-ordering challenge sets, do source-only quality predictions track
      meaning-preserving pairs or syntax-preserving pairs more closely?
    task: how do I test whether my source-side difficulty model responds to meaning rather
      than surface word order?
  answered_by:
  - meaning-over-order
- ask:
    plain: what changes to a sentence make a translation difficulty score go up or down?
    jargon: which controlled source-side transformations shift source-only quality predictions,
      and by how much?
    task: how do I use a translation difficulty predictor to find out which linguistic phenomena
      hurt machine translation?
    practitioner: can I probe my MT pipeline's weaknesses by perturbing source sentences and
      watching a difficulty score?
  answered_by:
  - transformation-probe
- ask:
    plain: is predicting translation quality from the source only an artefact of how post-editing
      effort is measured?
    jargon: does source-only quality prediction hold for direct-assessment labels as well
      as for HTER?
    task: which quality label should I train a source-only predictor on if I want human judgements
      rather than post-editing edits?
    practitioner: if I switch my target labels from HTER to human direct assessment, will
      a source-only model still work?
  answered_by:
  - hter-vs-da
- ask:
    plain: does a translation difficulty predictor still work on text from a different subject
      area than it was trained on?
    jargon: how much does source-only quality prediction degrade out of domain across corpora
      such as bible-uedin and Tatoeba?
    task: how do I know whether a translation difficulty model trained on one corpus will
      hold up on my own text?
    practitioner: can I apply a published source-only quality predictor to my domain, or do
      I need in-domain training data?
  answered_by:
  - domain-matters
- ask:
    plain: how well does predicting translation quality from the source sentence actually
      correlate with human judgements for English to German?
    jargon: what Pearson correlation with human DA scores does the best English-German source-only
      quality predictor reach?
    task: how do I know whether source-only quality prediction is accurate enough to act on
      for English-German?
    practitioner: is source-only English-German quality prediction accurate enough for me
      to route sentences on it?
  answered_by:
  - main-endezh
  - augmentation-gain
misreadings:
- 'PreQuEL does not tell a user why a sentence is hard to translate: the models are trained
  end to end and cannot point to the responsible linguistic features, only correlate with
  them.'
- An en-de correlation of 0.336 is not a high correlation in absolute terms, and the paper
  states its predictions should be used with care rather than as a reliable per-sentence filter.
- The finding that quality can be predicted from the source alone is not evidence that the
  WMT quality-estimation datasets are cheatable; an oracle source-only model could in principle
  simulate the MT system, so source-only predictability is expected rather than an artifact.
- The claim that PreQuEL generalises across MT systems rests on COMET-labelled augmented data
  comparing Marian and Facebook FAIR outputs, not on human direct-assessment labels for multiple
  systems.
- 'The augmentation method does not replace human direct-assessment data: it is used as intertraining
  or an auxiliary task before fine-tuning on DA scores, and a model trained on COMET data
  alone at matched 7K size reaches only 0.219 en-de.'
- Adding a UD parser is not the paper's winning design; the parser-augmented model doubles
  parameters and is still beaten by the much smaller multi-task model.
---
