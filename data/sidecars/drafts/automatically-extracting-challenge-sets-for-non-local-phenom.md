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

Then promote it:  python scripts/draft_sidecars.py --accept automatically-extracting-challenge-sets-for-non-local-phenom

Stamp: spec=8f05813a4658 checks=pass body=9c0582d3bf07
-->
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
- q:
  - Is the Transformer biased toward monotonic word order?
  - Do self-attention translation models have a locality bias like LSTMs?
  - What happens to Transformer BLEU when you permute the source word order?
  answers:
  - learned-pe-no-locality-bias
  - sine-pe-residual-bias
- q:
  - Does learned or sinusoidal positional encoding matter for machine translation?
  - Should I use learned positional embeddings instead of sine ones?
  - Are sinusoidal position embeddings introducing an order bias?
  answers:
  - sine-pe-residual-bias
  - positional-embedding-design-implication
- q:
  - Are long-distance dependencies still a problem for neural machine translation?
  - Do modern MT systems handle discontinuous phrases like phrasal verbs?
  - How much worse is translation quality on long-distance dependency sentences?
  answers:
  - ldd-still-hard
  - difficulty-grows-with-distance
- q:
  - Does translation accuracy degrade as the distance between head and dependent grows?
  - Is syntactic distance still a determinant of MT quality?
  - Do human judgments confirm that longer dependencies are translated worse?
  answers:
  - difficulty-grows-with-distance
  - manual-accuracy-by-distance
- q:
  - How can I build a challenge set for machine translation without manual annotation?
  - Can challenge sets for MT evaluation be extracted automatically?
  - How large can automatically extracted MT challenge sets be?
  answers:
  - automatic-challenge-sets-contribution
  - challenge-set-sizes
- q:
  - How reliable is parser-based extraction of linguistic phenomena for evaluation sets?
  - What is the precision of automatically extracted reflexive verb and preposition stranding
    examples?
  - Do automatically extracted challenge sentences actually contain the target phenomenon?
  answers:
  - extraction-precision
- q:
  - Are challenge sets just harder because their sentences are longer?
  - How do you rule out sentence length as the reason a challenge set is difficult?
  - Is source length a confound in long-distance dependency evaluation?
  answers:
  - length-not-the-cause
- q:
  - What should I read about fine-grained evaluation of machine translation beyond BLEU?
  - Which paper established automatic construction of linguistic challenge sets for MT?
  - Where do I start reading on phenomenon-specific MT evaluation?
  answers:
  - automatic-challenge-sets-contribution
- q:
  - Does BLEU capture performance on rare syntactic phenomena?
  - Why does a reordering-focused metric matter for evaluating word order?
  - Do BLEU and RIBES agree on reordering challenge sets?
  answers:
  - ribes-reordering
  - ldd-still-hard
- q:
  - Which German and English constructions were used to build the long-distance dependency
    sets?
  - What phenomena are covered by the auto_challenge_sets corpora?
  - How many sentences are in the English-German preposition stranding challenge set?
  answers:
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
