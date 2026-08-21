---
claims:
- id: what-muler-is
  kind: context
  text: MuLER turns any reference-based text-generation metric, such as BLEU, ROUGE or BERTScore,
    into a per-phenomenon error analysis. By masking a feature such as nouns or location names
    in both reference and system output, it measures how much of the metric's achievable gain
    the system leaves on the table.
  scope: Requires a feature detectable automatically on the target side (tagger or lexicon
    scorer) and a reference-based metric; demonstrated for machine translation into English
    and for CNN/DailyMail summarization as of 2023.
- id: naturalistic-alternative
  kind: context
  text: MuLER offers a naturalistic alternative to challenge sets for fine-grained evaluation.
    Instead of constructing minimal-pair test items, it restricts an existing test set's evaluation
    to the examples that contain the feature of interest.
  scope: Positioned in the paper's related-work discussion against minimal-change evaluation
    and challenge-set methods; MuLER covers a closed but extendable set of automatically detectable
    traits rather than arbitrary linguistic phenomena.
- id: manual-agreement
  kind: result
  text: In a manual analysis of WMT system pairs with near-equal BLEU but differing MuLER,
    the system MuLER ranked better on a feature translated that feature better in 91.3% of
    sentences. That covers the 97 sentences of 201 where quality differed.
  scope: 5 system pairs from WMT 2018-2020 (fi-en, tr-en, ru-en, zh-en), features LOC, ORDINAL,
    AUX, PERSON and WORK_OF_ART; annotated by one of the authors on shuffled side-by-side
    outputs.
  evidence: Section 4.3 and Table 10
- id: nouns-verbs-hard
  kind: result
  text: Nouns and verbs are among the hardest POS tags to translate under MuLER even though
    they are among the most frequent POS tokens. On WMT 2019 German-English systems, 100%-masking
    MuLER runs 0.225-0.306 for nouns and 0.359-0.448 for verbs (lower is better).
  scope: WMT news-task submissions into English, POS features tagged automatically; MuLER
    computed with BLEU. The frequency figures are token frequencies in the evaluated data,
    not measured training-set counts.
  evidence: Figure 4 and Table 15
- id: ne-not-tracking-bleu
  kind: result
  text: 'Overall BLEU gains do not imply better named-entity translation: correlations between
    BLEU and negative MuLER are high for sentiment, concreteness, valence, arousal and dominance
    features but not for most named-entity types.'
  scope: Pearson correlations over all WMT 2014-2017 submissions with English as target, per
    source language; the features on which BLEU and MuLER agree change from language to language.
  evidence: Figure 3 and Section 4.2
- id: monotonic-range
  kind: result
  text: Masking a fixed fraction of a feature's occurrences with the oracle strategy and the
    rest with the anti-oracle strategy places MuLER proportionally inside the oracle-to-anti-oracle
    interval. On the WMT 2020 de-en submission OPPO.1360, the 50-50 hybrid noun score of 0.33
    sits between the anti-oracle 0.21 and the oracle 0.45.
  scope: 5 randomly chosen WMT submissions (de-en, ru-en, fi-en, 2015-2020) at 50-50, 40-60
    and 30-70 splits, nouns and verbs only, BLEU as the base metric; the split is synthetic,
    partitioning feature words by first letter.
  evidence: Table 4 and Tables 11-13
- id: specificity
  kind: result
  text: Synthetic features built to match the frequency of real POS tags give MuLER a variance
    near zero across 1000 draws, 4.09e-04 for the noun-matched synthetic feature. Their scores
    also differ from the matched real tag's MuLER score, so MuLER does not fire on arbitrary
    word groupings.
  scope: WMT 2019 German-English submission online-G.0, synthetic features formed by splitting
    the unique vocabulary into p equal groups for p in 2 to 6, 1000 sampled runs; real features
    compared are NOUN, VERB, PROPN, PRON and ADV.
  evidence: Table 2 and Table 14
- id: frequency-robust
  kind: result
  text: MuLER is far less sensitive to how frequently a feature occurs than its unnormalized
    numerator. On WMT 2019 de-en Facebook_FAIR.6750, masking 50% versus 100% of nouns moves
    abl-MuLER from 0.021 to 0.054 while MuLER moves only from 0.203 to 0.267.
  scope: WMT 2019 German-English submissions, nouns and verbs, BLEU as base metric, frequency
    varied by masking a first-letter-sorted subset of feature occurrences and ignoring the
    rest.
  evidence: Table 3 and Table 15
- id: gender-blind-bleu
  kind: result
  text: On WinoGender sentence pairs differing only in one pronoun's gender, BLEU scores the
    pair at 0.8 while MuLER's gender feature is 1.0, the maximum penalty. A bottom-line metric
    can therefore look near-perfect on a dimension it entirely fails.
  scope: WinoGender female-male pairs treated as reference-output pairs rather than as real
    system output; a diagnostic demonstration of the score's sensitivity, not an evaluation
    of a deployed MT system.
  evidence: Section 4.6
- id: summarization-concreteness
  kind: result
  text: Applied with ROUGE to T5-small, T5-base and DistilBART summarizers, MuLER shows the
    concreteness score consistently lower than valence, dominance, arousal and sentiment.
    That matches the expectation that summaries compress text by making it more concrete.
  scope: CNN/DailyMail summarization, 3 HuggingFace models, lexicon-based sentence scorers;
    described by the paper as preliminary summarization experiments.
  evidence: Figure 7 and Section 4.4
- id: bertscore-extension
  kind: result
  text: MuLER extends to embedding-based metrics by editing BERTScore's reference-candidate
    similarity matrix, and on 5 randomly sampled WMT 2020 Chinese-English submissions produces
    trends similar to MuLER with BLEU.
  scope: bert-base-uncased BERTScore, 5 zh-en WMT 2020 submissions; the paper labels these
    preliminary experiments, with the ordering max > min verified on 1000 randomly sampled
    sentences.
  evidence: Figure 9 and Appendix C
- id: negative-muler-edge
  kind: result
  text: MuLER can come out negative when oracle masking lowers rather than raises the base
    metric. The documented causes are tagger errors and cases where a word is a noun in the
    reference and a verb in the output.
  scope: Documented as edge cases with worked WMT examples; MuLER is otherwise computed only
    on sentences where both reference and output contain the feature, which prevents division
    by zero.
  evidence: Table 7 and Appendix G
qa:
- ask:
    plain: is there a way to find out which kinds of words a translation system gets wrong,
      instead of just one overall score?
    jargon: can a reference-based generation metric such as BLEU or BERTScore be decomposed
      into per-phenomenon error scores?
    task: how do I break a single BLEU or ROUGE number down by error type without building
      a new test set?
    practitioner: my system's BLEU went up but I need to know what it actually improved at,
      can MuLER tell me?
  answered_by:
  - what-muler-is
  - naturalistic-alternative
- ask:
    plain: what should I read about going beyond a single translation quality score to see
      specific error types?
    jargon: what work offers an alternative to challenge sets for fine-grained evaluation
      of generation systems?
    task: how do I get phenomenon-level evaluation from a test set I already have rather than
      writing minimal pairs?
    practitioner: should I build a challenge set for the phenomena I care about, or can I
      reuse my existing test set for fine-grained analysis?
  answered_by:
  - naturalistic-alternative
  - what-muler-is
- ask:
    plain: which kinds of words do machine translation systems get wrong most often, and are
      common words like nouns easier?
    jargon: which POS tags show the largest per-phenomenon error rates in WMT news-translation
      submissions?
    task: which word classes should I look at first when diagnosing a translation model's
      errors?
    practitioner: should I assume my MT system handles frequent nouns and verbs well because
      they are common in the training data?
  answered_by:
  - nouns-verbs-hard
- ask:
    plain: if a translation system's overall score goes up, does that mean it also got better
      at names of people and places?
    jargon: do per-feature MuLER scores correlate with BLEU uniformly across named-entity
      types and lexical features such as concreteness and valence?
    task: can I use overall BLEU improvements as evidence that named-entity translation improved?
    practitioner: my BLEU is 2 points higher than last quarter, can I tell my users that entity
      translation got better too?
  answered_by:
  - ne-not-tracking-bleu
  - nouns-verbs-hard
- ask:
    plain: has anyone checked with human readers that a per-word-type error score really reflects
      worse translation of those words?
    jargon: what is the human agreement rate for MuLER's per-feature ranking on WMT system
      pairs with near-equal BLEU?
    task: how do I know a fine-grained metric decomposition agrees with human judgement before
      I trust it to rank systems?
    practitioner: should I trust MuLER's per-feature ranking of two systems whose overall
      BLEU is basically tied?
  answered_by:
  - manual-agreement
- ask:
    plain: if a word type shows up rarely in a test set, does that distort a score measuring
      how well it is translated?
    jargon: how does normalizing by the oracle-to-anti-oracle interval control MuLER's sensitivity
      to feature frequency?
    task: how do I compare error rates across features that occur at very different frequencies
      in the same test set?
    practitioner: can I compare a MuLER score for rare location names against one for nouns,
      or is the frequency gap going to fool me?
  answered_by:
  - frequency-robust
  - monotonic-range
- ask:
    plain: would a score that measures errors on nouns give the same answer for a random group
      of words?
    jargon: what synthetic control experiments establish MuLER's specificity to genuine linguistic
      features rather than frequency-matched word sets?
    task: how do I rule out that my per-feature error scores are an artefact of feature frequency
      rather than the linguistic phenomenon?
    practitioner: before I read anything into MuLER's noun score, is there evidence the score
      is not just noise from picking words at that rate?
  answered_by:
  - specificity
  - monotonic-range
- ask:
    plain: can an overlap score like BLEU tell whether a translation used the right gender
      for a pronoun?
    jargon: what do WinoGender minimal pairs show about BLEU's sensitivity to gender errors
      compared with a gender-feature MuLER score?
    task: how do I detect gender translation errors that leave my overall BLEU almost unchanged?
    practitioner: my model scores well on BLEU, is that any evidence it is not making gender
      errors?
  answered_by:
  - gender-blind-bleu
- ask:
    plain: does the per-error-type analysis work for summarization, not just translation?
    jargon: can ROUGE be decomposed per feature to compare abstractive summarizers such as
      T5 and DistilBART?
    task: how do I compare two summarization models on specific lexical properties like concreteness
      rather than a single ROUGE number?
    practitioner: I evaluate summarizers with ROUGE, can I get feature-level error analysis
      out of it with MuLER?
  answered_by:
  - summarization-concreteness
- ask:
    plain: does the per-error-type breakdown only work with word-overlap scores, or also with
      embedding-based ones?
    jargon: can MuLER's oracle and anti-oracle masking be applied to BERTScore's reference-candidate
      similarity matrix?
    task: how do I get feature-level error analysis when my evaluation pipeline uses BERTScore
      rather than BLEU?
    practitioner: we switched from BLEU to BERTScore, can I still get per-phenomenon error
      scores?
  answered_by:
  - bertscore-extension
  - what-muler-is
- ask:
    plain: why would a per-word-type error score come out negative, and what does that tell
      me?
    jargon: under what conditions does oracle masking lower rather than raise the base metric,
      producing a negative MuLER score?
    task: what do I do when a feature's MuLER score comes out below zero?
    practitioner: I got a negative MuLER value for one feature, is my setup broken or is the
      tagger to blame?
  answered_by:
  - negative-muler-edge
one_liner: MuLER decomposes any reference-based metric, such as BLEU, ROUGE or BERTScore,
  into per-feature scores by masking a phenomenon (nouns, location names, gender) in both
  reference and output and measuring how much of the metric's achievable gain the system fails
  to realize.
coined: MuLER
gloss: 'Multi-Level Evaluation with Reference: a way to split a single BLEU or ROUGE score
  into per-phenomenon error scores'
terminology:
  oracle masking: Replacing every span carrying a feature with the same mask token in both
    the reference and the system output, so the metric behaves as if the system had translated
    that feature perfectly.
  anti-oracle masking: Replacing spans carrying a feature with different mask tokens in the
    reference and in the output, destroying the correspondence and so simulating a system
    that gets the feature entirely wrong.
  MuLER score: The oracle-masked metric score minus the unmasked score, divided by the oracle
    minus anti-oracle difference; a unitless number where lower means better performance on
    the feature.
  abl-MuLER: An ablated version of the MuLER score consisting of its numerator only, without
    the oracle-minus-anti-oracle normalization.
  discrepancy breakdown: A triple of add, hit and miss counts recording how often a feature
    appears more, equally or fewer times in the output than in the reference, covering over-
    and under-generation that the MuLER score itself ignores.
  indices-BLEU: BLEU computed only over the sentences in which the feature of interest appears
    in both the reference and the system output.
misreadings:
- 'A lower MuLER score is better, not worse: MuLER measures the gain the system still leaves
  available on a feature, so 0 means nothing to improve and 1 means total failure on that
  feature.'
- 'MuLER is not an independent measure of feature accuracy: it inherits the base metric''s
  blind spots, so where BLEU or ROUGE is invariant to a trait MuLER will be too, and it is
  only as reliable as the tagger or lexicon used to detect the feature.'
- A low MuLER score does not mean the masked span itself was translated correctly. The manual
  analysis found many cases where the feature span matched the reference in both systems and
  the difference lay in the surrounding context.
- MuLER is not meant for comparing systems of wildly different overall quality; the paper
  argues the comparison is informative mainly for systems of roughly similar overall performance.
- The finding that nouns and verbs are hard to translate is about relative MuLER penalties
  on WMT submissions into English, not a claim that MT systems mistranslate most nouns and
  verbs.
- 'The summarization and BERTScore results are explicitly preliminary in the paper: 3 CNN/DailyMail
  models and 5 zh-en WMT 2020 submissions respectively, not a broad evaluation of either setting.'
links_extra:
  code: https://github.com/tai314159/MuLER
key: karidi2023muler
---
