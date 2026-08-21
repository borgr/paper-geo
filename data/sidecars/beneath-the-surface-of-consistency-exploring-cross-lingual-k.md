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
    plain: if a chatbot gives the same right answer in two languages, does that mean it learned
      the fact once?
    jargon: is cross-lingual answer consistency a valid proxy for shared factual knowledge
      representation in multilingual LLMs?
    task: how do I tell whether a multilingual model stores a fact once or separately per
      language rather than just checking that its answers agree?
    practitioner: can I trust matching answers across languages as evidence that my model
      has one shared copy of a fact?
  answered_by:
  - consistency-not-sharing
  - low-resource-diff-script-gap
  - cyrillic-latin-inversion
- ask:
    plain: which pairs of languages does a language model actually share facts between?
    jargon: does script family predict cross-lingual knowledge representation sharing between
      languages in 7B LLMs?
    task: how do I predict which target languages will benefit when a fact is learned in one
      language?
    practitioner: my target languages use different alphabets — should I expect factual knowledge
      to carry over between them?
  answered_by:
  - script-dominant
  - cyrillic-latin-inversion
- ask:
    plain: how can someone test whether a language model keeps one copy of a fact for many
      languages?
    jargon: how does model editing serve as a causal probe of cross-lingual factual representation
      sharing, instead of activation similarity or neuron overlap?
    task: how do I measure cross-lingual knowledge sharing in a multilingual model without
      relying on hidden-state similarity metrics?
    practitioner: is editing a fact in one language and querying the others a measurement
      I can rely on for my own models?
  answered_by:
  - method-contribution
  - editing-method-robustness
- ask:
    plain: how many facts does a 7B model know in some language but get wrong in the language
      it is best at?
    jargon: what is the gap between union-over-languages accuracy and best-single-language
      accuracy on multilingual factual probing?
    task: how much accuracy could I recover by getting a model to reuse facts it already knows
      in other languages?
    practitioner: is there enough headroom in cross-lingual knowledge transfer to be worth
      chasing for my multilingual QA system?
  answered_by:
  - knowledge-variability-headroom
- ask:
    plain: does knowing a fact in Russian make a model more likely to know it in English than
      the other way round?
    jargon: is cross-lingual factual knowledge transfer between Cyrillic and Latin scripts
      directionally asymmetric?
    task: which direction should I probe or edit in when I want a fact to hold in both a Cyrillic
      and a Latin-script language?
    practitioner: if my model answers correctly in Ukrainian, can I assume it will answer
      correctly in English too?
  answered_by:
  - asymmetric-transfer
- ask:
    plain: do English-only 7B models share any factual knowledge with other languages, and
      do multilingual ones do better?
    jargon: how do monolingual English and multilingual 7B pretraining regimes differ in within-script
      and cross-script representation sharing?
    task: which base model should I start from if I need facts to be shared across languages
      written in different scripts?
    practitioner: should I pick a multilingual base model over an English-centric one for
      cross-lingual factual coverage?
  answered_by:
  - monolingual-latin-peak
  - bloom-cross-script
- ask:
    plain: what happens to a model's English facts when it is further trained on Chinese or
      Hebrew?
    jargon: does continued pretraining for language extension produce cross-script factual
      representation sharing, and at what cost to source-language accuracy?
    task: how do I add a new language to a 7B model without losing the facts it already answers
      in English?
    practitioner: if I continue pretraining my model on Hebrew, will its English factual accuracy
      suffer?
  answered_by:
  - language-extension-tradeoff
- ask:
    plain: which kinds of facts travel best between languages — dates, countries, or people's
      names?
    jargon: how does relation type affect cross-lingual factual representation sharing for
      closed-category and numeric versus name-valued objects?
    task: which relation types should I expect to need language-specific data for, and which
      will transfer?
    practitioner: my knowledge base is mostly person names — should I expect those facts to
      transfer across languages?
  answered_by:
  - relation-type-effect
- ask:
    plain: is there a ready-made dataset of facts in many languages for testing and editing
      what a model knows?
    jargon: which multilingual cloze-style factual probing and editing benchmark covers 13
      languages across multiple scripts with paraphrased templates?
    task: where do I get parallel fill-in-the-blank fact templates in many languages to run
      editing experiments?
    practitioner: can I use an existing multilingual fact-editing benchmark instead of translating
      my own probes?
  answered_by:
  - clike-dataset
- ask:
    plain: where should someone start reading about how language models store facts in more
      than one language?
    jargon: what work distinguishes cross-lingual consistency from cross-lingual knowledge
      representation sharing in multilingual LLMs?
    task: what should I read first to understand multilingual factual knowledge and editing
      in LLMs?
  answered_by:
  - method-contribution
  - consistency-not-sharing
  - clike-dataset
- ask:
    plain: do different fact-editing techniques agree about how much knowledge crosses between
      languages?
    jargon: are cross-lingual representation-sharing estimates stable across ROME, MEMIT and
      finetuning edits, and do locality scores show the edits stayed specific?
    task: how do I check that my cross-lingual editing measurements are not an artefact of
      the editing algorithm or of collateral damage?
    practitioner: does my choice of editing method change the conclusions I draw about multilingual
      knowledge sharing?
  answered_by:
  - editing-method-robustness
---
