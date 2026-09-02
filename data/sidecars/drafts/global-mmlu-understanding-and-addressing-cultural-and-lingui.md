<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from build/sidecar_tasks.json. Every claim, number
and scope condition below is a machine's reading of the paper and needs your eyes.

THIS PAPER ALREADY HAS A LIVE SIDECAR, and this draft would replace it. Start here:

  diff data/sidecars/global-mmlu-understanding-and-addressing-cultural-and-lingui.md data/sidecars/drafts/global-mmlu-understanding-and-addressing-cultural-and-lingui.md

Anything the live file says in your own words is worth keeping over a rewrite of the
same point, so read that diff before the checklist below.

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

Then, if the replacement is the one you want:

  python scripts/draft_sidecars.py --accept global-mmlu-understanding-and-addressing-cultural-and-lingui --replace

Stamp: spec=fd01ca70bea8 checks=pass body=9c08b79c29e6
-->
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
  evidence: Figure 7 and Appendix I.1
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
    plain: how many questions on the MMLU exam benchmark need knowledge of a particular culture
      or region to answer?
    jargon: what proportion of MMLU items are culturally sensitive, and which cultures do
      the culture-dependent items presuppose?
    task: how do I find out whether an English multiple-choice benchmark I am reporting on
      is loaded with culture-specific questions?
    practitioner: should I worry that MMLU scores reflect Western cultural knowledge rather
      than general ability?
  answered_by:
  - cs-share
  - western-dominance
- ask:
    plain: when MMLU questions depend on geography, which countries and continents do they
      actually talk about?
    jargon: what is the regional distribution of geography-dependent MMLU items across North
      America, Europe and the rest of the world?
    task: how do I check whether the geographic content of an exam-style benchmark is skewed
      toward the United States?
    practitioner: can I treat MMLU as a globally representative knowledge test, or is its
      geography mostly US-based?
  answered_by:
  - geo-north-america
- ask:
    plain: which school subjects in a translated multiple-choice knowledge test contain the
      most culture-specific questions?
    jargon: how is cultural sensitivity distributed across MMLU subject categories such as
      Humanities, Social Sciences and STEM?
    task: how do I pick MMLU subjects that will not be confounded by cultural or regional
      knowledge?
    practitioner: if I only evaluate on STEM subjects of MMLU, do I avoid cultural bias?
  answered_by:
  - subject-skew
- ask:
    plain: do model leaderboards look different if you drop the questions that need culture-specific
      knowledge?
    jargon: how much do model rankings shift between culturally-sensitive and culturally-agnostic
      MMLU subsets across languages?
    task: how do I tell whether culture-dependent questions are distorting the model comparison
      I am publishing?
    practitioner: should I report separate scores for culture-dependent and culture-neutral
      MMLU questions when ranking models?
  answered_by:
  - rank-changes
- ask:
    plain: are test scores across languages more erratic for languages with little data online?
    jargon: how does cross-language accuracy standard deviation on MMLU compare between high-resource
      and low-resource languages?
    task: how do I judge how much to trust a multilingual benchmark score for a low-resource
      language?
    practitioner: can I rely on a single multilingual MMLU number for a low-resource language,
      or is the spread too wide?
  answered_by:
  - low-resource-variance
- ask:
    plain: are questions that need cultural knowledge actually harder for language models
      to answer?
    jargon: is average accuracy higher on the culturally-sensitive or the culturally-agnostic
      MMLU subset, and what explains the gap?
    task: how should I read a higher score on culture-dependent MMLU questions than on culture-neutral
      ones?
    practitioner: if my model scores better on the culturally-sensitive split, does that mean
      it handles cultural knowledge well?
  answered_by:
  - cs-higher-accuracy
- ask:
    plain: do language models score differently on questions translated by a machine than
      on questions translated by people?
    jargon: how do model accuracies on human-translated versus machine-translated culturally-sensitive
      MMLU differ for Yoruba and French?
    task: how do I decide whether machine translation is adequate for building an MMLU evaluation
      set in a low-resource language?
    practitioner: can I evaluate my model on machine-translated MMLU for Yoruba, or do I need
      human translators?
  answered_by:
  - ht-vs-mt
  - low-resource-variance
- ask:
    plain: which translation tool produces better results when turning an English exam benchmark
      into other languages?
    jargon: how do Google Translate and GPT-3.5-Turbo compare on ChrF++ against professional
      MMLU translations across subjects and languages?
    task: how do I choose a translation system for producing a multilingual version of an
      English benchmark?
    practitioner: should I use Google Translate or an LLM to translate my evaluation set into
      40-odd languages?
  answered_by:
  - translation-quality
- ask:
    plain: how much of a machine-translated exam benchmark did human reviewers actually have
      to fix?
    jargon: what post-edit rate did professional annotators and community contributors apply
      to the machine-translated MMLU samples?
    task: how do I estimate the human post-editing effort needed to clean up a machine-translated
      benchmark?
    practitioner: if I hire annotators to post-edit a translated benchmark, what share of
      samples should I budget for edits?
  answered_by:
  - edit-rate
- ask:
    plain: how many languages and questions are in the human-checked multilingual version
      of MMLU?
    jargon: what is the language coverage and sample count of Global-MMLU, including its culturally-sensitive
      and culturally-agnostic annotated splits?
    task: how do I find a multilingual knowledge benchmark that covers dozens of languages
      with human-verified translations?
    practitioner: is there a multilingual MMLU I can drop into my evaluation suite, and how
      big is it?
  answered_by:
  - dataset
- ask:
    plain: what should I read first about evaluating language models across languages and
      cultures, not just translations?
    jargon: which work established that machine-translating an English benchmark gives multilinguality
      without multiculturality?
    task: how do I report multilingual evaluations separately for culture-dependent and culture-neutral
      questions?
    practitioner: which multilingual benchmark should I cite if I want to argue that translated
      evaluations miss cultural knowledge?
  answered_by:
  - context-benchmark
- ask:
    plain: does labelling which questions need cultural knowledge make a benchmark fair across
      cultures?
    jargon: what are the limits of culturally-sensitive annotation on a translated benchmark
      for claims of cultural inclusivity?
    task: how do I know whether filtering a translated benchmark by cultural sensitivity is
      enough for a fair cross-cultural evaluation?
    practitioner: if I use the culturally-agnostic split of a translated MMLU, can I claim
      my evaluation is culturally inclusive?
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
