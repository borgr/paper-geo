---
key: singh2025globalmmlu
coined: Global-MMLU
gloss: a 42-language MMLU test set with human-verified translations and questions labelled
  as culturally sensitive or culturally agnostic
one_liner: Global-MMLU re-annotates MMLU for the cultural, geographic and dialect knowledge
  its questions require and releases a 42-language test set with human-verified translations,
  so multilingual results can be reported separately on culturally-sensitive and culturally-agnostic
  subsets.
claims:
- id: cs-share
  kind: result
  text: 28% of MMLU questions require culturally sensitive knowledge, meaning cultural, geographic
    or dialect-specific knowledge, to be answered correctly. Geographic knowledge accounts
    for 54.7% of those questions and cultural knowledge for 32.7%.
  scope: Based on a uniform sample of 2,850 English MMLU questions (50 per each of 57 subjects),
    labelled by majority vote among at least 3 of 200 professional and community annotators.
  evidence: Section 2.2
- id: western-dominance
  kind: result
  text: Among MMLU questions tagged as needing cultural knowledge, 86.5% require Western cultural
    knowledge, while the next largest category, South Asian culture, accounts for only 4%.
  scope: English MMLU sample of 2,850 questions; percentages are over samples with a single
    culture tag, excluding untagged and multi-tag samples.
  evidence: Figure 4 and Section 2.2
- id: geo-north-america
  kind: result
  text: For MMLU questions requiring geographic knowledge, 84.9% concern North America or
    Europe, split as 64.5% North America and 20.4% Europe. Of the Western-culture questions,
    73.9% specifically require knowledge about the United States.
  scope: English MMLU sample of 2,850 questions; region and country shares computed over samples
    with a single region or country tag.
  evidence: Figure 4, Figure 5 and Section 2.2
- id: subject-skew
  kind: result
  text: 'Cultural sensitivity in MMLU is concentrated in the humanities: 68% of Humanities
    questions are culturally sensitive, versus 30 of 950 STEM samples (3.15%). All World Religions
    and Moral Scenarios samples contain at least one cultural, regional or dialect reference.'
  scope: English MMLU annotated sample of 2,850 questions, 50 per subject, with subject categories
    following Hendrycks et al. and Medical and Business split out of 'Other'. 12 of the 57
    subjects contained no culturally sensitive samples.
  evidence: Figure 3, Figure 6 and Section 2.2
- id: rank-changes
  kind: result
  text: Model rankings shift far more on the culturally-sensitive MMLU subset than on the
    culturally-agnostic one. Averaged across languages and 14 models, CA rankings show 3.4
    rank changes and 3.7 position shifts against the annotated MMLU sample, CS rankings 5.7
    and 7.3.
  scope: 14 models from 9 families (including GPT-4o and Claude 3.5 Sonnet) evaluated 5-shot
    with lm-evaluation-harness; ranks measured against the uniform MMLU Annotated subsample,
    across the 42 Global-MMLU languages.
  evidence: Section 4.2 and Table 2
- id: low-resource-variance
  kind: result
  text: Accuracy variability across languages grows sharply for lower-resource languages.
    The average standard deviation rises from 3.21 (CA) and 3.86 (CS) on high-resource languages
    to 6.37 and 6.78 on low-resource languages, increases of 98% and 75%.
  scope: 14 evaluated models, 5-shot; low-resource languages include machine-translated data,
    so part of the variance may reflect translation quality rather than model capability.
  evidence: Section 4.2 and Figure 10
- id: cs-higher-accuracy
  kind: result
  text: 'Average model accuracy is higher on the culturally-sensitive MMLU subset than on
    the culturally-agnostic one: 54.8% versus 51.3% for small models and 66.8% versus 61.6%
    for large models. CS questions come mostly from Social Sciences and Humanities, while
    CA retains the harder STEM and Medical subjects.'
  scope: 14 models, 5-shot, averaged across languages; small models are Aya Expanse 8B, Gemma2
    9B, SEA-LION v3 9B, Llama 3.1 8B, Mistral Nemo 12B, Qwen2.5 7B and large models are Llama
    3.1 70B and Command R+.
  evidence: Section 4.2 and Figure 9
- id: ht-vs-mt
  kind: result
  text: Claude 3.5 Sonnet and GPT-4o score significantly higher on machine-translated than
    on human-translated culturally-sensitive Yoruba data, while models generally do better
    on human-translated data for high-resource French; Aya Expanse 32B is the only model consistent
    across both.
  scope: Compares human- versus machine-translated CS subsets for exactly 3 languages -- French
    (high), Korean (mid), Yoruba (low resource).
  evidence: Figure 11
- id: translation-quality
  kind: result
  text: Google Translate achieves higher ChrF++ scores than GPT-3.5-Turbo across all MMLU
    subject categories and with lower deviation across languages, measured against professional
    human translations from MMMLU.
  scope: Restricted to languages overlapping between the two machine-translated sets and human-translated
    MMMLU; GPT-3.5-Turbo is the system used for the widely adopted 26-language translated
    MMLU.
  evidence: Figure 7 and Appendix D.1
- id: edit-rate
  kind: result
  text: 'Human review changed a substantial share of the machine-translated MMLU: 7,565 edits
    were made, 36.9% of reviewed samples. Professional annotators edited 789 samples per language
    (38.5%) and community contributors 362 per language (17.7%).'
  scope: Edits cover 4 professionally annotated gold languages (Arabic, French, Hindi, Spanish)
    and 11 community-translated languages; differing edit rates reflect annotator time and
    resources, not translation quality across languages.
  evidence: Figure 8 and Section 3.1
- id: dataset
  kind: result
  text: Global-MMLU covers all 14K MMLU samples in 42 languages, 589,764 samples in total,
    combining professional translations with post-edits, community translations and machine
    translation. It ships 792 English culturally-sensitive and 2,058 culturally-agnostic annotated
    questions, extended to the other 41 languages.
  scope: Cultural sensitivity labels were assigned on the English source and propagated to
    translations, so they capture bias in the original questions rather than artefacts of
    any particular translation. Released under a permissive license.
  evidence: Section 3.2 and Table 4
- id: context-benchmark
  kind: context
  text: Global-MMLU is a reference point for the argument that machine-translating an English
    benchmark yields multilinguality without multiculturality, and provides the culturally-sensitive
    and culturally-agnostic subsets needed to report multilingual LLM evaluations separately.
  scope: As of publication in 2025; concerns knowledge-style multiple-choice evaluation derived
    from English MMLU, covering 42 of the world's roughly 7,000 languages and no dialect variation.
- id: context-not-inclusion
  kind: context
  text: Identifying whether benchmark questions are culturally sensitive does not make a dataset
    culturally inclusive. Global-MMLU flags gaps in non-Western representation but still derives
    all its questions from English MMLU rather than from locally authored material.
  scope: Stated as a limitation of the Global-MMLU release; achieving inclusion would require
    integrating culturally grounded knowledge sourced in-language, which the dataset does
    not do.
  evidence: Section 7
qa:
- ask:
    unsorted:
    - What fraction of questions in a widely used English multiple-choice knowledge benchmark
      require culture-specific knowledge?
    - What fraction of MMLU questions need cultural or regional knowledge to answer?
    - Is MMLU culturally biased?
  answered_by:
  - cs-share
  - western-dominance
- ask:
    unsorted:
    - Which regions and countries does the geographic knowledge in English exam-style benchmark
      questions actually cover?
    - Is MMLU US-centric?
    - Which geographies do MMLU geography-dependent questions refer to?
  answered_by:
  - geo-north-america
- ask:
    unsorted:
    - Which exam subjects in a multiple-choice knowledge benchmark carry the most cultural
      and regional bias?
    - Do STEM questions in MMLU require cultural knowledge?
    - Where in MMLU is cultural sensitivity concentrated by subject?
  answered_by:
  - subject-skew
- ask:
    unsorted:
    - Do model leaderboard rankings change if you remove culturally biased questions?
    - How much do LLM rankings shift between culturally sensitive and culturally agnostic
      MMLU questions?
    - Does cultural bias in MMLU distort model comparisons?
  answered_by:
  - rank-changes
- ask:
    unsorted:
    - Are multilingual evaluation results less reliable for low-resource languages?
    - How much does accuracy vary across low-resource languages on MMLU?
    - Does evaluation variance grow for lower-resource languages?
  answered_by:
  - low-resource-variance
- ask:
    unsorted:
    - Do models score worse on culturally sensitive questions?
    - Is accuracy higher or lower on the culturally-sensitive MMLU subset?
    - Why do CS questions look easier than CA questions for LLMs?
  answered_by:
  - cs-higher-accuracy
- ask:
    unsorted:
    - Is machine translation good enough for evaluating LLMs in low-resource languages?
    - Do models do better on machine-translated or human-translated test sets?
    - Does using machine-translated benchmarks overstate low-resource language ability?
  answered_by:
  - ht-vs-mt
  - low-resource-variance
- ask:
    unsorted:
    - Which machine translation system is best for building a translated benchmark?
    - Is Google Translate or GPT-3.5 better for translating MMLU?
    - How was translation quality validated for the 42-language MMLU?
  answered_by:
  - translation-quality
- ask:
    unsorted:
    - How many machine-translated benchmark samples did professional and community annotators
      edit?
    - What share of translated MMLU samples needed post-editing?
    - How many translation edits went into a 42-language MMLU release?
  answered_by:
  - edit-rate
- ask:
    unsorted:
    - How many languages and samples does a human-verified multilingual knowledge benchmark
      cover?
    - How many languages and samples does the 42-language multilingual MMLU contain?
    - What is in the culturally-sensitive versus culturally-agnostic split of translated MMLU?
  answered_by:
  - dataset
- ask:
    practitioner: What should I read about cultural bias in multilingual LLM benchmarks?
    unsorted:
    - Which paper established that translating English benchmarks does not make them multicultural?
    - Where should I start reading about culturally aware multilingual evaluation?
    - What is a good benchmark for evaluating LLMs across languages and cultures?
  answered_by:
  - context-benchmark
- ask:
    unsorted:
    - Does labelling questions as culturally sensitive make a benchmark culturally inclusive?
    - What are the limits of flagging culturally sensitive questions in a translated benchmark?
    - Is a filtered translated benchmark enough for fair evaluation across cultures?
  answered_by:
  - context-not-inclusion
terminology:
  Culturally-Sensitive (CS): An MMLU question whose correct answer depends on cultural, geographic
    or dialect-specific knowledge, assigned by majority vote of annotators labelling the original
    English question.
  Culturally-Agnostic (CA): An MMLU question that requires none of cultural, geographic or
    dialect-specific knowledge to answer correctly, serving as a baseline subset for cross-language
    comparison.
  MMLU Annotated (MA): A uniform random subsample of 2,850 MMLU questions, 50 from each of
    the 57 subjects, annotated in English for cultural, geographic, dialect and temporal knowledge
    and used as the reference for model rankings.
  transMMLU: Collective term for versions of MMLU produced by machine-translating the English
    dataset into other languages and used as-is for multilingual evaluation.
  Gold Set: The 4 languages -- Arabic, French, Hindi and Spanish -- whose machine translations
    were reviewed and post-edited by compensated professional annotators.
misreadings:
- 'Higher accuracy on the culturally-sensitive subset does not mean models handle cultural
  knowledge well: CS questions come disproportionately from Social Sciences and Humanities,
  where models score higher, while the culturally-agnostic subset keeps the harder STEM and
  Medical subjects.'
- The culturally-sensitive labels describe bias in the original English MMLU questions, not
  translation errors; dialect annotation was performed on the English source and does not
  measure artefacts introduced during translation.
- 'Global-MMLU is not a culturally inclusive benchmark: it flags which questions assume Western
  knowledge but its questions are still translations of English MMLU rather than locally authored
  exam material.'
- Differences in edit rates between professional (38.5%) and community (17.7%) annotators
  reflect available time and resources, not the translation quality of the languages involved.
- Models scoring higher on machine-translated than human-translated low-resource data is not
  evidence that machine translation is a better test set; it indicates the machine-translated
  distribution resembles those models' own training data.
links_extra:
  dataset: https://hf.co/datasets/CohereForAI/Global-MMLU
---
