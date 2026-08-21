---
key: choshen-abend-2019-automatically
one_liner: The Transformer with learned positional embeddings shows no locality bias, yet
  long-distance dependencies still hurt it — so Choshen and Abend extract MT challenge sets
  automatically from dependency parses and word alignments, producing sets thousands of sentences
  large for German-English and English-German.
claims:
- id: learned-pe-no-locality-bias
  kind: result
  text: A Transformer with learned positional embeddings scores 24.81 BLEU on regular German-English
    data and 24.87 BLEU when the same fixed permutation is applied to every source sentence,
    showing no locality bias.
  scope: German-English WMT2015 sentences of length 18 only (130,983 sentences, 1,000 held
    out), one fixed permutation sigma, 5 runs in the Regular setting and 5 in Permuted; highest
    test BLEU over epochs reported.
  evidence: Table 1
- id: sine-pe-residual-bias
  kind: result
  text: 'Sine positional embeddings leave the Transformer with a residual locality bias: BLEU
    drops 1.18 points, from 25.08 to 23.90, when source tokens are permuted. A BiLSTM (Nematus)
    drops far more, 2.65 points from 22.32 to 19.67.'
  scope: German-English, fixed-length-18 sentences from WMT2015 (130,983 sentences, comparable
    to a low-resource setting), single training run each for SinePE and Nematus in both the
    Regular and Permuted conditions.
  evidence: Table 1
- id: ldd-still-hard
  kind: result
  text: Long-distance dependencies remain hard for the Transformer even though it shows no
    locality bias. On German-English News, BLEU drops from 28.23 on the full test set to 22.68
    on the reordering challenge set and 27.46 on the verb-particle set.
  scope: Transformer trained on WMT2015, evaluated on challenge sets extracted from newstest2013
    and the Books corpus with minimum head-dependent distance d>=1; the same drop pattern
    appears for Nematus and for English-German.
  evidence: Table 4
- id: difficulty-grows-with-distance
  kind: result
  text: Translation quality falls as the head-dependent distance grows. Across 10 phenomenon-model-language
    combinations, 9 show a negative Spearman correlation between minimum distance and BLEU,
    including -1 for German reflexive verbs with the Transformer.
  scope: Books challenge sets, minimum distances of 1, 2 and 3 against an unrestricted control;
    Transformer and Nematus; English verb-particle constructions with the Transformer are
    the single positive correlation (0.73).
  evidence: Table 5
- id: manual-accuracy-by-distance
  kind: result
  text: 'Manual annotation of German-English Transformer output confirms the distance effect:
    60% of lexical long-distance dependencies are translated correctly at distance 1, 54%
    at distance 2 and 38% at distance 5.'
  scope: 180 German source sentences from Books, distances of exactly 1, 2 and 5, judged by
    2 annotators at kappa=0.79, after removing extraction errors.
  evidence: Table 8
- id: extraction-precision
  kind: result
  text: 'Automatic parser-based extraction of long-distance-dependency sentences is accurate
    enough for evaluation: 85% of extracted German sentences, 87% of English News sentences
    and 86% of English Books sentences genuinely contain the target phenomenon.'
  scope: Manual check of 180 German and 81 English sentences by 2 proficient annotators (the
    paper's authors); per-type precision in English ranges from 1.00 for particles on Books
    down to 0.60 for preposition stranding on Books.
  evidence: Table 7
- id: challenge-set-sizes
  kind: result
  text: Automatic extraction yields German-English challenge sets of 7,584 verb-particle and
    8,122 reflexive-verb sentences at minimum distance 1. Previously released MT challenge
    sets were compiled by hand at about 10 examples per phenomenon.
  scope: Extracted from the Books corpus (51K sentence pairs) and newstest2013 (3K) for German-English
    and English-German; English-German sets are much smaller, e.g. 191 preposition-stranding
    sentences at distance 1.
  evidence: Table 3
- id: ribes-reordering
  kind: result
  text: 'RIBES, a reordering-sensitive metric, confirms the BLEU trend on the reordering challenge
    sets: the Transformer scores 0.79 versus 0.82 baseline on German News and 0.54 versus
    0.57 on German Books.'
  scope: Reordering challenge sets extracted with FastAlign at alignment index difference
    d>=5, Transformer only, News and Books domains with German and English as source.
  evidence: Table 6
- id: length-not-the-cause
  kind: result
  text: Transformer BLEU on every German-English challenge set is lower than on any of the
    100 length-matched Books corpora sampled per set and per d. Correlations between a sampled
    corpus's average sentence length and Transformer BLEU are only 0.06, 0.09 and 0.03.
  scope: Books corpus, Transformer, d values 0-3, length-matched samples drawn within 1 token
    per sentence; the three correlations are for samples of 1,000, 100 and 10 sentences; English-German
    trends are similar but less pronounced.
  evidence: Section 4.3
- id: automatic-challenge-sets-contribution
  kind: context
  text: Choshen and Abend's CoNLL 2019 work introduces automatic extraction of MT challenge
    sets from dependency parses and word alignments. The extracted sets are large enough that
    phenomenon-specific evaluation can use standard automatic metrics such as BLEU and RIBES
    instead of manual inspection.
  scope: As of 2019, when earlier MT challenge sets for French-English and English-Swedish
    were hand-compiled and manually scored; demonstrated only for German-English and English-German,
    and requires a Universal Dependencies parser for the source language.
  evidence: Section 2.2
- id: positional-embedding-design-implication
  kind: context
  text: Choshen and Abend argue that the choice between learned and sine positional embeddings
    is not neutral. Learned embeddings are preferable when a locality bias is undesirable,
    such as for highly divergent language pairs.
  scope: Based on permutation experiments on one German-English setting with 18-token sentences;
    the two embedding types are comparable in BLEU under normal, unpermuted training.
  evidence: Section 3.2
qa:
- ask:
    plain: do machine translation models care whether nearby words stay near each other?
    jargon: does a self-attention encoder exhibit a locality bias when source token order
      is permuted?
    task: how do I test whether a translation model relies on source word order being monotonic?
    practitioner: if my language pair has very different word order, will a Transformer or
      an LSTM encoder suffer more?
  answered_by:
  - learned-pe-no-locality-bias
  - sine-pe-residual-bias
- ask:
    plain: does it matter whether a translation model learns its position information or uses
      a fixed formula?
    jargon: do sinusoidal versus learned positional embeddings differ in the locality bias
      they induce in NMT?
    task: which positional embedding should I pick when training translation for a language
      pair with heavy reordering?
    practitioner: should I switch my Transformer from sinusoidal to learned position embeddings?
  answered_by:
  - sine-pe-residual-bias
  - positional-embedding-design-implication
- ask:
    plain: do today's translation systems still get sentences wrong when related words are
      far apart?
    jargon: are long-distance dependencies still a bottleneck for Transformer NMT quality?
    task: how do I find out whether my translation model breaks on separable verbs and other
      split constructions?
    practitioner: can I trust a Transformer to translate sentences where a verb and its particle
      are separated?
  answered_by:
  - ldd-still-hard
  - difficulty-grows-with-distance
- ask:
    plain: does translation get worse the further apart the connected words in a sentence
      are?
    jargon: how does head-dependent distance correlate with translation quality for reflexive
      verbs and verb particles?
    task: how do I measure the effect of dependency length on my model's translation quality?
    practitioner: should I expect more translation errors in my data as the gap between a
      verb and its dependent grows?
  answered_by:
  - difficulty-grows-with-distance
  - manual-accuracy-by-distance
- ask:
    plain: can test sets that target a specific grammar construction be built without hand-writing
      examples?
    jargon: can MT challenge sets be extracted automatically from dependency parses and word
      alignments?
    task: how do I build a large phenomenon-specific evaluation set for translation without
      manual annotation?
    practitioner: is automatic extraction going to give me enough examples to evaluate one
      construction with BLEU?
  answered_by:
  - automatic-challenge-sets-contribution
  - challenge-set-sizes
- ask:
    plain: if examples are pulled out of a corpus by a parser, how often do they really contain
      the construction you wanted?
    jargon: what is the precision of parser-and-alignment-based extraction of reflexive verb
      and preposition-stranding sentences?
    task: how do I check that an automatically built challenge set is clean enough to report
      scores on?
    practitioner: can I rely on parser-extracted long-distance-dependency sentences without
      checking them by hand?
  answered_by:
  - extraction-precision
- ask:
    plain: are sentences with far-apart words harder just because they are longer sentences?
    jargon: is source sentence length a confound in long-distance-dependency challenge set
      evaluation?
    task: how do I separate the effect of dependency distance from the effect of sentence
      length on BLEU?
    practitioner: before I blame my model on long-distance dependencies, how do I rule out
      that it is just long sentences?
  answered_by:
  - length-not-the-cause
- ask:
    plain: which study first showed how to build grammar-targeted translation test sets from
      a corpus automatically?
    jargon: what work established automatic construction of phenomenon-specific challenge
      sets for MT evaluation?
    task: where should I start reading if I want to evaluate translation on specific syntactic
      phenomena?
  answered_by:
  - automatic-challenge-sets-contribution
- ask:
    plain: does a word-overlap score like BLEU really show whether word order was translated
      right?
    jargon: do BLEU and RIBES agree on reordering-focused challenge sets for German-English?
    task: which metric should I report when I am evaluating reordering rather than lexical
      choice?
    practitioner: should I add a reordering-sensitive metric alongside BLEU for my word-order
      experiments?
  answered_by:
  - ribes-reordering
  - ldd-still-hard
- ask:
    plain: which German and English grammar constructions were collected into the long-distance
      dependency test sets, and how many sentences each?
    jargon: what phenomena and set sizes do the automatically extracted German-English verb-particle
      and reflexive-verb challenge sets cover?
    task: where can I get a ready-made large test set for separable verbs or reflexive verbs
      in German-English translation?
    practitioner: are the released challenge sets big enough for me to compare two systems
      on one construction?
  answered_by:
  - challenge-set-sizes
terminology:
  locality bias: The inductive assumption in a translation model that source words close together
    correspond to target words close together, so that arbitrarily distant alignments are
    dispreferred.
  reordering LDD: A long-distance dependency in which source and target words largely correspond
    one-to-one but are ordered very differently, detected by word alignments whose source
    and target indices differ by at least d.
  lexical LDD: A long-distance dependency in which how a word or contiguous expression is
    translated depends on non-adjacent source words, such as a reflexive verb, a verb-particle
    construction or a stranded preposition.
  PerPosEmb: A control setting in which the source tokens stay in order but their positional
    embeddings are permuted, so token identity and position information are decoupled.
misreadings:
- 'The absence of a locality bias in the Transformer does not mean it handles long-distance
  dependencies well: BLEU still drops consistently on the extracted challenge sets, and quality
  falls further as dependency distance grows.'
- The Transformer's lower BLEU than Nematus on the Books corpus is not evidence that self-attention
  generalises worse out of domain; the two models were trained on different data and the experiments
  were not designed to compare architectures.
- Extracting challenge sets from dependency parses does not presuppose that MT systems internally
  build syntactic representations; parses are used only as a way to find sentences likely
  to be hard to translate.
- 'The difficulty of the challenge sets is not an artefact of longer sentences: length-matched
  control corpora sampled from Books all score higher in BLEU than the German-English challenge
  sets.'
- Automatic extraction is not perfectly precise; about 14-15% of extracted sentences lack
  the target phenomenon, and preposition-stranding precision is the lowest at 0.60 on Books.
links_extra:
  code: https://github.com/borgr/auto_challenge_sets
  anthology: https://www.aclweb.org/anthology/K19-1028
  doi: https://doi.org/10.18653/v1/K19-1028
---
