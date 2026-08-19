<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced via a forced tool call) + 2 repair rounds. Every claim, number
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

Then promote it:  python scripts/draft_sidecars.py --accept prequel-quality-estimation-of-machine-translation-outputs-in

Stamp: spec=8f05813a4658 checks=pass body=e4600361684f
-->
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
- q:
  - Can you predict machine translation quality before translating a sentence?
  - Is it possible to estimate translation quality from the source sentence only?
  - What is PreQuEL?
  answers:
  - task-context
  - main-endezh
- q:
  - What should I read about quality estimation without access to the translation?
  - Which paper introduced source-only translation quality prediction?
  - Where should I start reading about deciding whether to machine translate or hire human
    translators?
  answers:
  - task-context
  - why-read
- q:
  - How much worse is source-only prediction than a real quality estimation system?
  - Does seeing the translation help quality estimation much?
  - How close does PreQuEL get to TransQuest?
  answers:
  - gap-to-qe
  - main-endezh
- q:
  - How can I get more training data for translation quality prediction without human annotation?
  - Does labelling parallel corpora with COMET scores help train a quality predictor?
  - What does the PreQuEL augmentation method contribute?
  answers:
  - augmentation-gain
  - aug-helps-qe
- q:
  - Can automatic-metric augmentation improve a normal quality estimation model?
  - Does COMET-based intertraining help TransQuest on WMT 2020 en-de?
  answers:
  - aug-helps-qe
- q:
  - Does a source-only quality predictor trained on one MT system transfer to another system?
  - Is translation difficulty shared across state-of-the-art MT systems?
  - How much correlation is lost when testing PreQuEL on a different translation system?
  answers:
  - cross-system
- q:
  - Does source-only difficulty prediction depend on the target language?
  - Is a sentence that is hard to translate into German also hard to translate into Chinese?
  - Do en-de and en-zh PreQuEL models transfer to each other?
  answers:
  - target-specific
- q:
  - Which features of a source sentence make it hard to machine translate?
  - Do sentence length and n-gram probability predict translation difficulty?
  - Does a source-only quality model rely too much on surface features?
  answers:
  - over-weights-features
  - transformation-probe
- q:
  - Does adding a dependency parser improve source-only translation quality prediction?
  - How much does explicit syntactic knowledge help predicting MT difficulty?
  answers:
  - syntax-parser
  - meaning-over-order
- q:
  - Is a source-only quality model sensitive to meaning or just to word order?
  - What do German word-ordering challenge sets reveal about PreQuEL predictions?
  answers:
  - meaning-over-order
- q:
  - Can a translation-difficulty model be used to study which linguistic phenomena hurt MT?
  - What happens to predicted translation quality when person names or numbers are swapped
    in the source?
  - Which source-sentence perturbations change predicted MT quality most?
  answers:
  - transformation-probe
- q:
  - Is source-only quality estimation just an artifact of HTER labels?
  - Does using direct-assessment scores instead of HTER stop models from cheating with the
    source alone?
  answers:
  - hter-vs-da
- q:
  - How well does source-only translation quality prediction hold up on a new domain?
  - Does the domain of the training corpus matter for predicting MT difficulty?
  answers:
  - domain-matters
- q:
  - What accuracy does the best en-de PreQuEL model reach?
  - What Pearson correlation does source-only MT quality prediction achieve on English-German?
  answers:
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
