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

Then promote it:  python scripts/draft_sidecars.py --accept muler-detailed-and-scalable-reference-based-evaluation

Stamp: spec=8f05813a4658 checks=pass body=f9df0924a4e7
-->
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
- q:
  - How can I find out which linguistic phenomena a machine translation system gets wrong,
    instead of just its BLEU score?
  - Is there a way to break a single BLEU or ROUGE number down by error type?
  - What does MuLER do?
  answers:
  - what-muler-is
  - naturalistic-alternative
- q:
  - What should I read about fine-grained evaluation of text generation systems?
  - Which papers move beyond bottom-line metrics like BLEU toward per-phenomenon analysis?
  - Where does MuLER sit relative to challenge-set evaluation?
  answers:
  - naturalistic-alternative
  - what-muler-is
- q:
  - Which parts of speech are hardest for machine translation systems to get right?
  - Are frequent words like nouns and verbs easy for MT systems to translate?
  - What did analysing all WMT submissions from 2014 to 2020 reveal about POS tags?
  answers:
  - nouns-verbs-hard
- q:
  - Does a higher BLEU score mean better named-entity translation?
  - Do all linguistic phenomena improve as overall MT quality improves?
  - Which features track overall metric gains and which do not?
  answers:
  - ne-not-tracking-bleu
  - nouns-verbs-hard
- q:
  - Is there human validation that MuLER scores reflect real translation quality on a feature?
  - How well does a fine-grained metric decomposition agree with human judgement of feature
    translation quality?
  - Was MuLER checked manually against annotated WMT outputs?
  answers:
  - manual-agreement
- q:
  - Does a per-feature evaluation score get confounded by how often the feature occurs?
  - How do I know a fine-grained metric is not just measuring feature frequency?
  - Why does MuLER normalize by the oracle minus anti-oracle interval?
  answers:
  - frequency-robust
  - monotonic-range
- q:
  - Would a feature-masking evaluation score fire on arbitrary random word sets too?
  - How was MuLER shown to be specific to real linguistic phenomena?
  - What synthetic experiments validate MuLER?
  answers:
  - specificity
  - monotonic-range
- q:
  - Can BLEU detect whether a system translates gender correctly?
  - What do WinoGender pairs reveal about the blind spots of overlap metrics?
  - How does MuLER expose gender errors that BLEU misses?
  answers:
  - gender-blind-bleu
- q:
  - Does MuLER work for summarization as well as translation?
  - Can ROUGE be decomposed by feature to compare summarization models?
  - What did MuLER find when comparing T5 and DistilBART summarizers?
  answers:
  - summarization-concreteness
- q:
  - Does feature-level metric decomposition work with neural metrics like BERTScore?
  - Is MuLER limited to n-gram overlap metrics such as BLEU and ROUGE?
  - How is BERTScore adapted for oracle and anti-oracle masking?
  answers:
  - bertscore-extension
  - what-muler-is
- q:
  - Can a MuLER score come out negative, and what does that mean?
  - Why would masking a feature make the base metric worse instead of better?
  - What are the known failure cases of oracle masking in MuLER?
  answers:
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
