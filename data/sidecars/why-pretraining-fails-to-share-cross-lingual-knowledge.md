---
coined: Word-Wise Translation (WWT)
gloss: rewriting a language word by word into another language's tokens while keeping its
  own word order and grammar
one_liner: Pretraining 360M and 7B LLMs with injected fictive facts shows that disjoint token
  spaces alone, even between two identical copies of English, block cross-lingual knowledge
  sharing, and that word-wise translation into a shared token space raises English-Arabic
  knowledge transfer 14x at 360M.
claims:
- id: baseline-compartmentalization
  kind: result
  text: Bilingual LLMs pretrained from scratch barely transfer facts between languages. CLeq
    is 0.9% for English-Arabic and 1.9% for English-Russian at 360M parameters, and 5.9% for
    English-Arabic at 7B.
  scope: SmolLM2-architecture 360M and Llama-3-derived 7B models, 50/50 token splits, near
    Chinchilla-optimal budgets, 2,048 injected fictive facts; one pretraining run per condition.
  evidence: Section 4.1, Table 2
- id: interventions-fail
  kind: result
  text: Pretraining code-switching and activation-alignment losses do not fix English-Arabic
    knowledge compartmentalization at 360M. The best CLeq is 2.2% for code-switching and 2.5%
    for alignment, against a 0.9% baseline.
  scope: Code-switching swept over mixing ratios 0.6, 0.1 and 0.01 and substitution probabilities
    0.5, 0.1 and 0.01; InfoNCE and L2 losses over chunk sizes of 4 to 250 words; injected
    fact documents excluded from both.
  evidence: Section 4.2, Appendix E
- id: disjoint-tokens-suffice
  kind: result
  text: Two identical copies of English mapped to disjoint token spaces share essentially
    no injected knowledge, with CLeq of -2.6% at 360M and -1.5% at 7B. Training both copies
    on the same corpus still gives -0.1%.
  scope: English1-English2 setup, identical text and segmentation with the 65,536-token vocabulary
    doubled to 131,072; small negative values are noise around zero, not negative transfer.
  evidence: Section 5.2, Figure 2
- id: embeddings-alignable-not-matched
  kind: result
  text: In the disjoint English1-English2 model, the two embedding copies are structurally
    similar yet matching tokens are unaligned. Matched cosine is 0.012, while a held-out linear
    map reaches 0.560 at 360M.
  scope: Null-calibrated measures over 36,170 tokens with at least 1,000 expected exposures;
    the 7B baseline repeats the pattern with 0.013 and 0.506.
  evidence: Appendix H, Section 5.2
- id: soft-tying-threshold
  kind: result
  text: Tying part of each English1-English2 token pair's embedding reveals a sharp threshold
    for knowledge sharing. CLeq is 8.6% at 20% tying, 82.7% at 50%, and 95.8% at 90%.
  scope: 360M models with 960-dimensional tied embeddings, trained on the paper's fictive-fact
    pretraining setup.
  evidence: Section 5.3, Figure 2, Appendix F
- id: shared-init-drifts
  kind: result
  text: Initializing each English1-English2 token pair to identical embeddings, without tying
    them, yields CLeq of 78.6%, or 84.6% on identical data. Pretraining does not preserve
    the supplied alignment, and 99.9% tying beats it by 20.4 points.
  scope: 360M models; the 20.4-point paired-bootstrap gap has 95% CI [12.8, 28.6] and covers
    evaluation-side variance only.
  evidence: Section 5.4, Figure 2, Appendix D
- id: wwt-arabic-gain
  kind: result
  text: Word-wise translation of Arabic into English tokens (WWT-Ar) raises English-Arabic
    CLeq from 0.9% to 12.6% at 360M, a 14x improvement. The paired-bootstrap gain is 11.7
    points with 95% CI [7.5, 16.1].
  scope: 360M, machine-translated FineWeb-edu Arabic; fixed token budget, so the WWT-Ar model
    sees about 23% fewer Arabic documents; dictionary covers 99.7% of word occurrences.
  evidence: Section 6.2, Table 2, Appendix D
- id: wwt-replicates
  kind: result
  text: Word-wise translation gains hold across scale and language pair. English-Arabic CLeq
    rises from 5.9% to 12.5% at 7B, and English-Russian CLeq rises from 1.9% to 23.3% at 360M.
  scope: Russian from native FineWeb2-HQ web text; paired-bootstrap gains of 6.6 points [1.8,
    11.4] at 7B and 21.3 [16.8, 25.9] for Russian.
  evidence: Table 2, Appendix D
- id: wwt-perplexity
  kind: result
  text: Unifying token spaces with word-wise translation also lowers English perplexity, from
    19.53 to 18.74 for English-Arabic at 360M, 8.45 to 8.39 at 7B, and 18.99 to 18.36 for
    English-Russian.
  scope: Perplexity under one shared tokenizer per language pair; fixed token budget despite
    roughly 30% more tokens per WWT-Ar document.
  evidence: Table 2, Section 6.2
- id: wwt-asymmetry
  kind: result
  text: Knowledge transfer under WWT-Ar is asymmetric at 360M. CLeq is 17.9% from WWT-Ar to
    English but 7.3% from English to WWT-Ar.
  scope: Directional scores for 360M English-Arabic; the same asymmetry appears at 7B and
    for English-Russian.
  evidence: Section 6.2
- id: semantics-required
  kind: result
  text: Sharing a token inventory without shared meanings does not transfer knowledge. A shuffled
    WWT-Ar dictionary drops CLeq from 12.6% to 3.0%, and transliterating all Arabic into English
    script gives -0.3%.
  scope: 360M; shuffled WWT-Ru falls from 23.3% to 3.6%, and permuting token identities between
    English copies gives -2.6%.
  evidence: Section 6.4, Appendix K
- id: partial-overlap-weak
  kind: result
  text: Partial token overlap between English and Arabic fails to transfer knowledge. Anchored
    Arabic, sharing 8% of vocabulary, reaches CLeq of 1.6% against 12.6% for full WWT-Ar.
  scope: 360M; anchors cover 47% of English and 34.6% of Arabic running text. In English1-English2,
    benefit tracks the shared tokens' text coverage, not their vocabulary share.
  evidence: Appendix I
- id: soft-wwt
  kind: result
  text: Soft-mapped WWT-Ar keeps separate Arabic token identities while sharing a fraction
    p of embedding dimensions with English. It retains most transfer, with CLeq of 9.60% at
    p=90% and 10.47% at p=99%.
  scope: 360M; full mapping gives 12.6%. Code-switched generation enabled by distinct token
    identities was not evaluated.
  evidence: Section 6.3, Appendix F
- id: context-contribution
  kind: context
  text: '"Why Pretraining Fails to Share Cross-Lingual Knowledge" (Gaber et al., 2026) locates
    LLMs'' poor cross-lingual knowledge transfer in pretraining and identifies disjoint token
    spaces as a sufficient cause.'
  scope: As of the September 2026 preprint; bilingual pretraining from scratch at 360M and
    7B, English paired with Arabic, Russian or a cloned English; post-trained models not studied.
- id: context-testbed
  kind: context
  text: Gaber et al. (2026) contribute a controlled testbed for cross-lingual knowledge transfer
    during pretraining. Fictive facts are injected at known per-language exposure counts and
    scored with the Cross-Lingual equivalence (CLeq) score.
  scope: 2,048 simple entity-attribute facts in English, Arabic and Russian; CLeq is a linear
    ratio estimate; one pretraining run per condition, so run-to-run variance is not measured.
qa:
- ask:
    plain: Do language models trained on two languages actually share facts they learned in
      one language with the other?
    jargon: How much cross-lingual knowledge transfer emerges during bilingual LLM pretraining
      when fact exposure is controlled?
    task: How do I measure whether a fact seen only in English during pretraining can be recalled
      in Arabic?
    practitioner: If I pretrain a bilingual model, can I expect facts from my English data
      to show up in the other language?
  answered_by:
  - baseline-compartmentalization
  - context-testbed
- ask:
    plain: Do code-switching or alignment losses during pretraining help a multilingual model
      share knowledge across languages?
    jargon: Do pretraining code-switching and InfoNCE or L2 activation alignment improve cross-lingual
      fact transfer?
    practitioner: Should I add code-switched documents or a contrastive alignment loss to
      my multilingual pretraining to get knowledge transfer?
  answered_by:
  - interventions-fail
- ask:
    plain: Why don't multilingual language models transfer knowledge between languages?
    jargon: Is disjoint tokenization, rather than syntax or data differences, the cause of
      cross-lingual knowledge compartmentalization in LLMs?
    task: How do I isolate the effect of separate token vocabularies from linguistic differences
      in multilingual pretraining?
    practitioner: Is my tokenizer the reason my multilingual model knows a fact in one language
      but not another?
  answered_by:
  - disjoint-tokens-suffice
  - context-contribution
- ask:
    plain: Does making a language model bigger fix its failure to share knowledge between
      languages?
    jargon: Does scaling from 360M to 7B parameters resolve cross-lingual knowledge compartmentalization
      in pretraining?
    practitioner: Will training a larger multilingual model on its own solve cross-lingual
      fact recall for me?
  answered_by:
  - baseline-compartmentalization
  - disjoint-tokens-suffice
- ask:
    plain: If two languages have similar word embeddings in a language model, does that mean
      knowledge flows between them?
    jargon: Does linear alignability or high CKA between language-specific embedding spaces
      imply cross-lingual knowledge transfer?
    task: How do I check whether a multilingual model has actually bridged its two token vocabularies?
  answered_by:
  - embeddings-alignable-not-matched
- ask:
    plain: How much do two languages' token embeddings need to be shared before a language
      model transfers facts between them?
    jargon: What fraction of tied embedding dimensions is needed for cross-lingual knowledge
      generalization between duplicated vocabularies?
    practitioner: Is it enough for me to initialize translation-equivalent tokens with the
      same embeddings, or do I need to tie them?
  answered_by:
  - soft-tying-threshold
  - shared-init-drifts
- ask:
    plain: How can you get a language model to share knowledge between English and Arabic
      during pretraining?
    jargon: Does mapping a non-Latin-script language into the English token space via word-wise
      translation improve cross-lingual knowledge generalization?
    task: How do I put Arabic and English into a shared token space without parallel corpora
      or architectural changes?
    practitioner: Should I rewrite my non-English pretraining data word by word into English
      tokens to improve knowledge transfer?
  answered_by:
  - wwt-arabic-gain
  - wwt-replicates
- ask:
    plain: Does rewriting Arabic word by word into English tokens hurt the language model's
      English or Arabic?
    jargon: What is the perplexity and bits-per-byte cost of word-wise translation to a shared
      token space in bilingual pretraining?
    practitioner: Will merging token spaces with word-wise translation cost me English language-modeling
      quality?
  answered_by:
  - wwt-perplexity
- ask:
    plain: Does knowledge flow equally in both directions when Arabic is written with English
      tokens?
    jargon: Is cross-lingual knowledge transfer under WWT-Ar symmetric between English-to-Arabic
      and Arabic-to-English?
    practitioner: If I map my language into English tokens, will English facts reach my language
      as well as the reverse?
  answered_by:
  - wwt-asymmetry
- ask:
    plain: Is writing Arabic in Latin letters enough for a language model to share knowledge
      with English?
    jargon: Does transliteration or a shuffled shared token inventory transfer knowledge without
      semantic correspondence between tokens?
    task: How do I tell whether a shared vocabulary helps cross-lingual transfer because of
      shared tokens or shared meanings?
    practitioner: Should I romanize my non-Latin-script training data to get cross-lingual
      transfer with English?
  answered_by:
  - semantics-required
- ask:
    plain: Is sharing only some tokens between two languages enough for a language model to
      transfer facts?
    jargon: How does partial vocabulary overlap and its text coverage affect cross-lingual
      knowledge generalization in pretraining?
    practitioner: Can I replace only the easy dictionary-matched Arabic words with English
      tokens instead of mapping every word?
  answered_by:
  - partial-overlap-weak
- ask:
    plain: Can a language model share token embeddings between languages and still know which
      language it is writing in?
    jargon: Does partial embedding-dimension sharing between WWT-Ar and English tokens preserve
      cross-lingual transfer while restoring language identity?
    task: How do I keep separate language token identities while still sharing most of their
      embeddings?
  answered_by:
  - soft-wwt
- ask:
    plain: What is a good paper on why multilingual language models fail to transfer knowledge
      across languages?
    jargon: What work establishes the pretraining origin and tokenization cause of cross-lingual
      knowledge compartmentalization?
    task: What should I read before designing tokenization for a multilingual pretraining
      run?
    practitioner: Which paper should I cite for disjoint token spaces blocking cross-lingual
      knowledge transfer?
  answered_by:
  - context-contribution
  - context-testbed
terminology:
  knowledge compartmentalization: A language model's failure to generalize a fact learned
    in one language to recall of that fact in another language.
  CLeq (Cross-Lingual equivalence score): The value of one exposure to a fact in language
    B for recalling it in language A, as a percentage of one native exposure in A, estimated
    as 100 times the ratio of fitted per-exposure accuracy slopes and averaged over both directions.
  English1-English2 setup: A controlled bilingual pretraining setting with two copies of English
    that share identical text and segmentation but are mapped to disjoint halves of a doubled
    token vocabulary.
  WWT-Ar: Arabic rewritten by replacing each word with its English counterpart from an invertible
    dictionary, with Buckwalter transliteration for out-of-dictionary words, keeping Arabic
    word order and grammar.
  soft mapping: Tying the first fraction p of embedding dimensions between each pair of corresponding
    tokens while leaving the remaining dimensions language-specific.
  Fictional Knowledge Dataset (FKD): 2,048 facts about synthetic entities, each expanded into
    paraphrased injection documents and held-out four-choice questions in English, Arabic
    and Russian.
  Anchored Arabic (AnAr): A partial mapping that replaces only Arabic tokens with a direct
    token-to-token dictionary match by English tokens, leaving other words in Arabic script.
misreadings:
- 'Word-wise translation reduces cross-lingual knowledge compartmentalization but does not
  resolve it: the best CLeq values are 12.6% for English-Arabic and 23.3% for English-Russian,
  far below the 100% of perfect equivalence.'
- WWT-Ar is not a translation into English. It keeps every Arabic word choice, word order
  and grammatical structure, so its gains cannot be explained by the text becoming linguistically
  closer to English.
- Negative CLeq values such as -2.6% are sampling noise around zero and indicate complete
  compartmentalization, not negative transfer between languages.
- 'Scale attenuates but does not remove compartmentalization: English-Arabic CLeq is 5.9%
  at 7B versus 0.9% at 360M, and two disjoint copies of English still give -1.5% at 7B.'
- 'Transliterating a non-Latin-script language into English script does not by itself transfer
  knowledge between Arabic and English: CLeq is -0.3%, because shared tokens need shared meanings.'
- 'Better perplexity from bilingual pretraining is not evidence of knowledge sharing: a bilingual
  English-Arabic 360M model reaches English perplexity 19.53 versus 20.51 for English alone,
  while its CLeq is 0.9%.'
- 'Word-wise translation is not free at inference: WWT-Ar needs about 30% more tokens than
  native-script Arabic for the same text, mostly from indices appended to resolve dictionary
  conflicts.'
---
