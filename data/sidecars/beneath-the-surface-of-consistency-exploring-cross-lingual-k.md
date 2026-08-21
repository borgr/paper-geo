---
key: ifergan2025beneath
coined: CLIKE
gloss: Cross-LIngual Knowledge Editing — a 13-language fill-in-the-blank factual probing and
  editing dataset
one_liner: Repurposing knowledge-editing methods (ROME, MEMIT, finetuning) as a probe, this
  work edits a fact in one language and measures whether the edit propagates to other languages,
  separating surface-level cross-lingual answer consistency from genuinely shared internal
  representations in 7B LLMs.
claims:
- id: consistency-not-sharing
  kind: result
  text: In four 7B LLMs, the expected number of languages in which a fact is answered consistently
    exceeds the number of languages an edit to that fact propagates to. Cross-lingual answer
    agreement therefore does not imply a shared internal representation.
  scope: BLOOM-7B, Qwen-7B, Llama-2-7B and Mistral-7B-v0.1 on CLIKE's 13 languages, with sharing
    measured via MEMIT edits on 500 known facts per language; the gap is largest for language
    pairs using different scripts.
  evidence: Figure 3
- id: low-resource-diff-script-gap
  kind: result
  text: Chinese, Japanese, Hebrew and Arabic show high cross-lingual answer consistency with
    each other in all models except Qwen. Edits made in one of them nevertheless show limited
    propagation to the others.
  scope: Pairwise MEMIT-based generalization scores on CLIKE; measured on base pretrained
    7B decoder-only models, not instruction-tuned ones.
  evidence: Figure 4
- id: cyrillic-latin-inversion
  kind: result
  text: Cyrillic languages (Russian, Ukrainian, Bulgarian) share more representation with
    each other than with Latin-script languages. Answer consistency runs the opposite way,
    being higher between Cyrillic and Latin than within Cyrillic.
  scope: CLIKE facts, pairwise C and SR matrices computed with MEMIT on the four base 7B models;
    a within-versus-across-script comparison, not a claim about any single language pair.
  evidence: Figure 4
- id: script-dominant
  kind: result
  text: Languages within the same script family exhibit the highest degree of cross-lingual
    knowledge representation sharing in every model examined, including Latin (English, French,
    Italian, Spanish) and Cyrillic (Russian, Ukrainian, Bulgarian) groups.
  scope: Multilingual BLOOM-7B, bilingual Qwen-7B and English monolingual Llama-2-7B and Mistral-7B-v0.1
    on CLIKE; Devanagari-script sharing (Hindi, Bengali) is high only for models that perform
    well on those languages (BLOOM, Mistral).
  evidence: Figure 4
- id: asymmetric-transfer
  kind: result
  text: Knowing a fact in a Cyrillic-script language implies roughly 40-60% probability of
    knowing it in a Latin-script language, while the reverse direction holds only about 10-20%
    of the time.
  scope: Pairwise consistency by exact match on CLIKE across the four base 7B models; the
    attribution to Latin-script pretraining dominance is a hypothesis, not a tested mechanism.
  evidence: Figure 4
- id: knowledge-variability-headroom
  kind: result
  text: Four 7B LLMs answer 42.5% of CLIKE facts correctly in at least one language, but only
    27.6% in their best-performing language and 11.8% averaged over all 13 languages. Fully
    shared knowledge would raise the best language by up to 53%.
  scope: Exact-match accuracy with 3-shot demonstrations and greedy decoding, counting a fact
    as known if any of 3 paraphrases is answered correctly; the headroom is an upper bound
    assuming perfect sharing, not an achieved improvement.
  evidence: Figure 2
- id: monolingual-latin-peak
  kind: result
  text: English monolingual Mistral-7B shows the highest within-script-family pairwise consistency
    (54.7%) and representation sharing (37.6%) of any model tested. Its facts peak anomalously
    at being known and represented in exactly 4 languages, the 4 Latin-script ones.
  scope: Mistral-7B-v0.1 and Llama-2-7B evaluated on CLIKE's 13 languages; within-script-family
    averages, which are not comparable to the cross-script averages reported for BLOOM.
  evidence: Figure 3
- id: bloom-cross-script
  kind: result
  text: Multilingual BLOOM-7B attains the highest cross-script pairwise averages of the models
    tested, at 36% consistency and 8.4% representation sharing, including 28% sharing from
    Italian to Hindi.
  scope: Averages over language pairs from different script families on CLIKE, compared against
    Qwen-7B, Llama-2-7B and Mistral-7B-v0.1; BLOOM's overall retrieval accuracy is low.
  evidence: Figure 4
- id: language-extension-tradeoff
  kind: result
  text: Chinese-Llama-2-7B and Hebrew-Mistral-7B gain large accuracy in their extended language,
    142% and 600% relative increases, while losing English accuracy by 29% and 32% relative.
    English-to-extended-language representation sharing stays in the single digits, at 4%
    and 6%.
  scope: Two language-extended 7B models compared to their Llama-2-7B and Mistral-7B-v0.1
    bases, with expanded tokenizer vocabularies and continued pretraining in English plus
    the extended language.
  evidence: Table 1
- id: editing-method-robustness
  kind: result
  text: Representation-sharing measurements agree across the three editing methods used as
    probes, with a 0.87 correlation between methods and locality scores averaging above 70%,
    indicating edits were specific rather than broadly destructive.
  scope: ROME, MEMIT and a finetuning baseline applied through EasyEdit to 500 known facts
    per language; custom hyperparameters were tuned for BLOOM, defaults used elsewhere. Main
    results are reported with MEMIT.
  evidence: Section 4
- id: relation-type-effect
  kind: result
  text: Relations with few possible answer categories (countries, instruments, continents,
    company developers) and numerical relations such as birth year and death year show the
    higher cross-lingual representation sharing. Name-valued relations such as book authors,
    movie directors and discoverers transfer less.
  scope: CLIKE's relation types under MEMIT editing; sports type and religion are exceptions
    to the low-cardinality trend, and high-cardinality relations such as cities also transfer
    poorly.
  evidence: Figure 7
- id: method-contribution
  kind: context
  text: Editing-based probing measures cross-lingual knowledge representation sharing by editing
    a fact in one language and testing whether the false target propagates to the same fact
    queried in other languages. It gives a causal alternative to activation-similarity and
    neuron-overlap analyses.
  scope: Earlier cross-lingual representation work used passive analyses that indicate connection
    but do not quantify how much knowledge is shared; as of publication in 2025, and demonstrated
    only on 7B decoder-only models with middle-layer editing methods.
  evidence: Section 5
- id: clike-dataset
  kind: context
  text: CLIKE is a multilingual fill-in-the-blank factual probing and editing dataset of about
    35k facts in 13 languages spanning 7 scripts. Each (subject, relation, object) triplet
    has 3 paraphrased templates per language, verified by professional translators or native
    speakers.
  scope: English, French, Italian, Spanish, Russian, Ukrainian, Bulgarian, Hindi, Bengali,
    Chinese, Japanese, Hebrew and Arabic; Wikidata triplets from 14 SPARQL queries, keeping
    only triplets labelled in at least 8 of these languages.
  evidence: Section 3.1
qa:
- ask:
    unsorted:
    - Does a language model answering the same fact correctly in two languages mean it stores
      the fact once?
    - Is cross-lingual consistency evidence of shared knowledge representation in LLMs?
    - Do consistent answers across languages imply a shared internal fact representation?
  answered_by:
  - consistency-not-sharing
  - low-resource-diff-script-gap
  - cyrillic-latin-inversion
- ask:
    unsorted:
    - What determines whether an LLM shares a fact representation between two languages?
    - How much does writing script matter for cross-lingual knowledge sharing in LLMs?
    - Which language pairs share factual knowledge inside multilingual models?
  answered_by:
  - script-dominant
  - cyrillic-latin-inversion
- ask:
    unsorted:
    - How can you measure whether an LLM stores a fact once for many languages?
    - Can knowledge editing be used to test cross-lingual representation sharing?
    - What method probes shared multilingual knowledge causally rather than by activation
      similarity?
    - How does editing-based probing of cross-lingual knowledge work?
  answered_by:
  - method-contribution
  - editing-method-robustness
- ask:
    unsorted:
    - How much factual knowledge do 7B LLMs know in some language but not in their best language?
    - What is the accuracy gap between 'any language' and 'best language' factual retrieval?
    - How much could multilingual LLM factual accuracy improve if knowledge were fully shared
      across languages?
  answered_by:
  - knowledge-variability-headroom
- ask:
    unsorted:
    - Is knowledge transfer between scripts symmetric in multilingual LLMs?
    - Does knowing a fact in Russian predict knowing it in English more than the reverse?
    - Is cross-lingual factual consistency direction-dependent?
  answered_by:
  - asymmetric-transfer
- ask:
    unsorted:
    - Do English-only models like Mistral and Llama-2 share factual knowledge across languages
      at all?
    - Do monolingual English LLMs show cross-lingual knowledge sharing?
    - How do monolingual, bilingual and multilingual 7B models differ in cross-lingual knowledge
      sharing?
  answered_by:
  - monolingual-latin-peak
  - bloom-cross-script
- ask:
    unsorted:
    - Does continued pretraining on a new language fix cross-lingual knowledge sharing?
    - What happens to English knowledge when a model is extended to Chinese or Hebrew?
    - Do language-extended LLMs bridge knowledge across different writing systems?
  answered_by:
  - language-extension-tradeoff
- ask:
    unsorted:
    - Which kinds of facts transfer best across languages in LLMs?
    - Do relation types affect cross-lingual factual knowledge sharing?
    - Are dates shared across languages more than person names in LLM factual knowledge?
  answered_by:
  - relation-type-effect
- ask:
    practitioner: Where can I find a cross-lingual fill-in-the-blank factual knowledge dataset
      with several scripts?
    unsorted:
    - Is there a multilingual dataset for factual knowledge editing across languages?
    - What benchmark covers factual probing in 13 languages with multiple paraphrases?
  answered_by:
  - clike-dataset
- ask:
    practitioner: What should I read about how multilingual LLMs represent factual knowledge?
    unsorted:
    - What work established that cross-lingual consistency and representation sharing are
      distinct in LLMs?
    - Where should I start reading about multilingual factual knowledge in language models?
  answered_by:
  - method-contribution
  - consistency-not-sharing
  - clike-dataset
- ask:
    unsorted:
    - Do ROME, MEMIT and finetuning give the same picture of cross-lingual knowledge transfer?
    - Are editing-based measurements of multilingual knowledge sharing method-dependent?
    - Did the multilingual edits damage unrelated knowledge?
  answered_by:
  - editing-method-robustness
---
