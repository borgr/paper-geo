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

Then promote it:  python scripts/draft_sidecars.py --accept global-piqa-evaluating-commonsense-reasoning-across-100-lang

Stamp: spec=8f05813a4658 checks=pass body=b716aac543bd
-->
---
key: chang2025globalpiqa
coined: Global PIQA
gloss: a hand-written commonsense reasoning benchmark for 141 language varieties, with culturally-specific
  and parallel splits
one_liner: Global PIQA is a commonsense reasoning benchmark for 141 language varieties, hand-written
  by over 350 researchers in over 65 countries, with a culturally-specific non-parallel split
  (100 examples per language) and a parallel split of 103 "culturally agnostic" questions
  translated into 131 language varieties.
claims:
- id: coverage
  kind: result
  text: Global PIQA covers 141 language varieties, spanning 118 unique ISO 639-3 language
    codes, 24 writing systems, and 19 top-level Glottolog language families. Of the languages,
    70 are Indo-European and 11 Atlantic-Congo.
  scope: 'Counts include dialect region codes; excluding them gives 129 ISO language-script
    combinations. Coverage is uneven: 36 South Asian languages against 1 Oceanian, and no
    indigenous American languages.'
  evidence: Table 2 and Appendix B
- id: participatory
  kind: context
  text: 'Global PIQA was built as a participatory benchmark: over 350 researchers from over
    65 countries and over 180 affiliations wrote and validated examples in their own languages.
    Contributors were offered co-authorship rather than paid as external annotators.'
  scope: Participation was voluntary, recruited through NLP community channels such as the
    EleutherAI Discord, LINGUIST List, Masakhane and social media, between the June 2025 announcement
    and the September 15, 2025 deadline.
  evidence: Section 3.1 and Appendix C
- id: cultural-specificity
  kind: result
  text: In the official non-parallel split of Global PIQA, 59.9% of examples are annotated
    as culturally-specific, referencing local foods, holidays, folklore, traditions or region-varying
    norms. Only 4.1% were written with any help from LLMs.
  scope: The official split up-samples culturally-specific and non-LLM examples, so the unsampled
    29.1K-example pool is only 40.8% culturally-specific and 9.6% LLM-assisted.
  evidence: Section 3.3 and Appendix D.2
- id: native-validation
  kind: result
  text: Every example in the Global PIQA non-parallel split was manually validated by at least
    one native speaker, 97.8% were validated multiple times by native speakers, and 92.6%
    carry human-corrected English translations.
  scope: Secondary review, covering source-language verification and translation correction,
    was completed for 126 of the 136 non-parallel language varieties; the rest are marked
    [machine_translated] in the release.
  evidence: Section 3.4
- id: manual-methods
  kind: result
  text: Of the 146 author groups contributing datasets to the Global PIQA non-parallel split,
    128 drafted their examples entirely manually without LLM help, and 141 reported making
    their datasets at least partially culturally-specific.
  scope: Self-reported per-group method descriptions, non-parallel split only; 16 groups used
    LLMs for initial generation, with two reporting that they kept only 14.6% and 22.0% of
    generated examples.
  evidence: Section 3.2
- id: parallel-split
  kind: result
  text: The parallel split of Global PIQA contains 103 four-choice "culturally agnostic" commonsense
    questions in 131 language varieties. All were machine translated from English and then
    corrected or verified by a native speaker of each target language.
  scope: Ekpeye has 101 examples because 2 cardinal-direction questions had no translatable
    terms; 6 of the original 109 English examples were dropped from all languages after correction
    revealed ambiguity.
  evidence: Section 4 and Section 4.1
- id: translation-edits
  kind: result
  text: Correcting the machine translations for the Global PIQA parallel split changed a mean
    of 24.9 characters per example, or 12.9% of characters. Per-language means reach 273.7
    characters for Ekpeye, 209.0 for Idoma and 131.6 for Urhobo.
  scope: Translations came from Gemini 2.5 Pro for the first 50 examples per language and
    Gemini 3.0 Flash for the rest, with prompts and candidate solutions translated separately.
  evidence: Section 4
- id: closed-model-aggregate
  kind: result
  text: Some closed systems among GPT-5.4, Claude Sonnet 4.6 and Gemini 3.1 exceed 90% accuracy
    averaged across languages on both the parallel and non-parallel splits of Global PIQA.
  scope: Generation-style prompting with thinking enabled (1024-token budget for Gemini and
    Claude, "medium" for GPT-5.4), 100 examples per language non-parallel and 103 parallel.
  evidence: Section 5.3 and Figure 2
- id: open-weight-gap
  kind: result
  text: Gemma 4 31B, the best open-weight model evaluated on Global PIQA, reaches 82.4% mean
    accuracy on the parallel split and 84.9% on the non-parallel split, below the closed-system
    skyline. Open-weight accuracy plateaus around 30-40B parameters.
  scope: Open-weight models from 300M to 120B parameters with generation-style prompting,
    including models specialised for single languages or regions; the plateau is read against
    parameter count.
  evidence: Figure 2 and Section 5.3
- id: region-gap
  kind: result
  text: On the parallel split of Global PIQA, Gemma 4 31B averages 88.1% accuracy for European
    languages but only 60.5% for Sub-Saharan African languages, and 91.0% for high-resource
    against 75.0% for low-resource languages.
  scope: Parallel split only, so the gap is not attributable to cultural content; resource
    levels follow the Joshi et al. (2020) taxonomy and regions follow the paper's own grouping.
  evidence: Figure 3 and Section 5.3
- id: worst-languages
  kind: result
  text: Taking the best-performing LLM per language including closed systems, Global PIQA
    leaves 4 parallel-split and 8 non-parallel-split languages below 80% accuracy. Ekpeye
    sits at 33% parallel / 65% non-parallel and Idoma at 37% / 75%.
  scope: Best-of-all-models-per-language figures over 100-103 examples per language, so sampling
    error is non-trivial; other low scorers include Burushaski at 59% and Meitei Manipuri
    at 63% non-parallel.
  evidence: Section 5.3 and Table 1
- id: cultural-vs-linguistic
  kind: result
  text: Lingala and Plateau Malagasy show the largest parallel-to-non-parallel accuracy drops
    in Global PIQA for the best-performing models, at 20 and 19 points. The paper reads this
    as weaker cultural knowledge than linguistic ability.
  scope: Best-model-per-language comparison across the two splits; the non-parallel split
    varies qualitatively in difficulty across languages, so split-to-split drops are suggestive
    rather than controlled.
  evidence: Section 5.3
- id: everyday-knowledge-framing
  kind: context
  text: Global PIQA argues that everyday commonsense knowledge, not only complex reasoning
    and expert knowledge, remains an area for improvement in LLMs for many languages and cultures.
  scope: Based on 100 examples per language in one task format (prompt plus candidate solutions),
    for models evaluated in 2025-2026.
  evidence: Section 6
- id: non-translated-design
  kind: context
  text: Global PIQA departs from multilingual benchmarks such as XNLI, XCOPA, Belebele, MGSM
    and Global MMLU by writing its non-parallel split directly in each language instead of
    translating an English dataset. Examples translated from English PIQA are excluded from
    that split.
  scope: The non-parallel split, covering 136 language varieties; the parallel split is itself
    translated from English by design, and a few non-parallel datasets were translated between
    related languages within the project.
  evidence: Section 1 and Section 3.2
qa:
- q:
  - What benchmark should I use to test commonsense reasoning in low-resource languages?
  - Is there a multilingual commonsense reasoning dataset that is not translated from English?
  - Where should I start reading about culturally-specific LLM evaluation across many languages?
  answers:
  - non-translated-design
  - participatory
  - coverage
- q:
  - How many languages does Global PIQA cover?
  - Which language families and writing systems are represented in Global PIQA?
  - How broad is the language coverage of a hand-written multilingual commonsense benchmark?
  answers:
  - coverage
- q:
  - How was Global PIQA constructed?
  - Who wrote the examples in Global PIQA, and were they paid annotators?
  - How do you organise a benchmark written by hundreds of native speakers?
  answers:
  - participatory
  - manual-methods
- q:
  - How much of Global PIQA is actually culturally specific?
  - What fraction of examples reference local foods, customs or traditions?
  - Were LLMs used to write the Global PIQA examples?
  answers:
  - cultural-specificity
  - manual-methods
- q:
  - How was data quality verified in a benchmark built by hundreds of volunteers?
  - Were the Global PIQA examples checked by native speakers?
  - Do the Global PIQA examples come with English translations?
  answers:
  - native-validation
- q:
  - What is the difference between the parallel and non-parallel splits of Global PIQA?
  - How can I compare LLM accuracy directly across languages on commonsense reasoning?
  - How many examples are in the Global PIQA parallel split?
  answers:
  - parallel-split
  - non-translated-design
- q:
  - How much do machine translations of commonsense questions need correcting for low-resource
    languages?
  - Which languages required the heaviest edits to machine-translated benchmark examples?
  - Is machine translation good enough for building multilingual benchmarks?
  answers:
  - translation-edits
  - parallel-split
- q:
  - How well do frontier LLMs do on multilingual commonsense reasoning?
  - What accuracy do GPT-5.4, Claude and Gemini get on Global PIQA?
  - Is Global PIQA already saturated by closed models?
  answers:
  - closed-model-aggregate
  - worst-languages
- q:
  - What is the best open-weight model on multilingual commonsense reasoning?
  - How big is the gap between open-weight models and proprietary systems on Global PIQA?
  - Does scaling open-weight model size keep improving multilingual commonsense accuracy?
  answers:
  - open-weight-gap
- q:
  - How large is the accuracy gap between high- and low-resource languages on commonsense
    reasoning?
  - Do LLMs perform worse on Sub-Saharan African languages than European ones?
  - What accuracy disparity across regions does Global PIQA reveal?
  answers:
  - region-gap
  - worst-languages
- q:
  - Which languages do LLMs handle worst on Global PIQA?
  - Are there languages where even the best model scores under 80% on commonsense questions?
  - How badly do models do on Ekpeye and Idoma?
  answers:
  - worst-languages
- q:
  - Can a benchmark separate a model's cultural knowledge from its linguistic ability in a
    language?
  - Which languages show weaker cultural knowledge than linguistic competence in LLMs?
  - What does the drop from the parallel to the non-parallel split of Global PIQA mean?
  answers:
  - cultural-vs-linguistic
  - parallel-split
- q:
  - Is everyday commonsense still a weakness of LLMs, or only expert reasoning?
  - What does Global PIQA claim about where multilingual LLMs still fail?
  - Why evaluate commonsense knowledge rather than complex reasoning across languages?
  answers:
  - everyday-knowledge-framing
  - region-gap
terminology:
  non-parallel split: The portion of Global PIQA whose examples are written directly in each
    language by native speakers rather than translated, so examples differ across languages
    and can be culturally specific; 100 examples per language for 136 language varieties.
  parallel split: The portion of Global PIQA consisting of the same 103 four-choice commonsense
    questions translated from English into 131 language varieties, enabling direct cross-lingual
    accuracy comparisons.
  culturally-specific example: In Global PIQA, an example that uses words that do not translate
    well into English (e.g. local dishes or brands), describes specific holidays, folklore,
    traditions or sayings, or whose correct solution likely varies by region.
  culturally agnostic: Written so as to minimise references to local foods, customs or traditions,
    so that the same question can be translated into a large number of languages and remain
    valid.
  cloze evaluation: Scoring a candidate solution by the language model's log-probability of
    the solution given the prompt, normalised by the solution's length in bytes, used for
    pretrained-only models.
  generation evaluation: Prompting an instruction-tuned model with the question and candidate
    solutions, sampling up to 2048 tokens, and scoring the response by string matching.
  English byte equivalents: Text length in UTF-8 bytes divided by the language's byte premium,
    i.e. the estimated extra bytes that language needs relative to content-matched English,
    used to compare solution lengths across languages fairly.
misreadings:
- 'Top closed systems exceeding 90% average accuracy does not mean Global PIQA is saturated:
  the benchmark still separates closed systems from open models, separates open models from
  each other, and leaves 8 non-parallel-split languages below 80% for the best model available.'
- Global PIQA is not a translation of English PIQA. Examples in the non-parallel split were
  written directly in each language, and translated English PIQA examples were explicitly
  excluded from that split.
- 'The 141 language varieties are not 141 distinct ISO 639-3 languages: the count includes
  script variants and dialect region codes, and reduces to 129 language-script combinations
  and 118 ISO 639-3 codes.'
- An example annotated as culturally-specific in Global PIQA does not always require the referenced
  cultural knowledge to answer; in many cases the culturally-specific element is only mentioned
  and the correct answer can be inferred from the rest of the context.
- The low accuracies for languages such as Ekpeye and Idoma on the parallel split are not
  explained by culturally unfamiliar content, because the parallel split was written to be
  culturally agnostic and translated from the same English source.
- Global PIQA's culturally-specific examples are snapshots from its individual authors and
  are not claimed to be representative of entire cultures; cultural stereotypes may still
  be present.
- '"More languages is better" is not the Global PIQA authors'' position: the paper states
  that researchers should work with communities to decide if and how their languages are included.'
links_extra:
  dataset (non-parallel): https://huggingface.co/datasets/mrlbenchmarks/global-piqa-nonparallel
  huggingface org: https://huggingface.co/mrlbenchmarks
---
