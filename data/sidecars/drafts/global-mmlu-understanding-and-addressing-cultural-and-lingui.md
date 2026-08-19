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

Then promote it:  python scripts/draft_sidecars.py --accept global-mmlu-understanding-and-addressing-cultural-and-lingui

Stamp: spec=d57862840a90 checks=8 body=2c1b2ff28fe7
-->
---
key: singh2025globalmmlu
coined: Global-MMLU
gloss: a 42-language MMLU test set with human-verified translations and culturally-sensitive
  vs. culturally-agnostic question labels
one_liner: Global-MMLU is a 42-language MMLU test set built from professional, community and
  machine translations, with every question in a 2,850-sample annotated subset labelled by
  human annotators as culturally-sensitive or culturally-agnostic so multilingual results
  can be reported separately on each.
links_extra:
  dataset: https://hf.co/datasets/CohereForAI/Global-MMLU
terminology:
  Culturally-Agnostic (CA): An MMLU question that human annotators judged answerable without
    cultural, geographic or dialect-specific knowledge; 2,058 of 2,850 annotated English MMLU
    questions fall in this subset.
  Culturally-Sensitive (CS): An MMLU question that human annotators judged to require cultural,
    geographic or dialect-specific knowledge to answer correctly; 792 of 2,850 annotated English
    MMLU questions fall in this subset.
  MMLU Annotated (MA): A uniform sample of 50 questions from each of MMLU's 57 subjects, 2,850
    questions in total, annotated in English for cultural, geographic, dialect and temporal
    knowledge and used as the reference point for model rankings.
  transMMLU: Collective term for versions of MMLU produced by machine-translating the English
    questions into other languages without human verification or cultural re-annotation.
claims:
- id: cs-share
  kind: result
  text: 28% of MMLU questions require culturally-sensitive knowledge, meaning cultural, geographic
    or dialect-specific knowledge, to answer correctly. The share comes from majority vote
    of human annotators on a uniform 2,850-question sample of English MMLU.
  scope: 50 questions per each of MMLU's 57 subjects; each question reviewed by at least 3
    annotators, 96.4% by more than 3; a tag applies when half or more annotators use it.
  evidence: Section 2.2; Figure 3
- id: geo-western
  kind: result
  text: Among MMLU questions that require geographic knowledge, 64.5% concern North America
    and 20.4% Europe, so 84.9% target Western regions.
  scope: Region tags in the culturally-sensitive subset of the 2,850-question annotated English
    sample; questions with no or multiple region tags excluded.
  evidence: Section 2.2; Figure 4
- id: culture-western
  kind: result
  text: 86.5% of MMLU questions tagged as requiring cultural knowledge are tagged as requiring
    Western cultural knowledge, with the next largest category, South Asian culture, at 4%.
  scope: Culture tags from the annotated 2,850-question English sample; Latin American, African
    and Indigenous cultures account for 1.3%, 1.1% and 0.7% of tags.
  evidence: Section 2.2; Figure 4
- id: us-concentration
  kind: result
  text: 73.9% of MMLU questions tagged as requiring Western cultural knowledge require knowledge
    specific to the United States, followed by the United Kingdom at 8%.
  scope: Country-level tags within the culturally-sensitive subset of the annotated English
    sample; questions with no country tag or multiple country tags excluded.
  evidence: Section 2.2; Figure 5
- id: subject-skew
  kind: result
  text: Cultural sensitivity in MMLU concentrates in Humanities, where 68% of questions are
    culturally sensitive, while only 30 of 950 STEM questions (3.15%) are, and Clinical Knowledge,
    Computer Security and Econometrics contain none.
  scope: Majority-vote labels on the 2,850-question annotated English sample; above 80% of
    samples are culturally sensitive in Philosophy, Moral Scenarios and High School US History.
  evidence: Section 2.2; Figure 6; Table 1
- id: rank-volatility
  kind: result
  text: Model rankings shift far more on the culturally-sensitive MMLU subset than on the
    culturally-agnostic one. Averaged over languages, the CS subset shows 5.7 rank changes
    and 7.3 position changes against 3.4 and 3.7 for CA, relative to MMLU Annotated.
  scope: 14 models from 9 families evaluated 5-shot with lm-evaluation-harness (API generations
    for GPT-4o and Claude Sonnet 3.5); ranks measured relative to the uniform MMLU Annotated
    sample across the 42 languages.
  evidence: Section 4.2; Table 2; Tables 5 and 6
- id: resource-variability
  kind: result
  text: Across-language standard deviation of model accuracy on low-resource languages reaches
    6.37 on culturally-agnostic and 6.78 on culturally-sensitive MMLU data, increases of 98%
    and 75% over the 3.21 and 3.86 measured on high-resource languages.
  scope: Averaged over 14 models evaluated 5-shot; resource tiers follow the Joshi et al.
    (2020) classes as grouped in Singh et al. (2024), and the low-resource languages are largely
    machine-translated.
  evidence: Section 4.2; Figure 10
- id: cs-easier
  kind: result
  text: Average model accuracy on MMLU is higher on the culturally-sensitive subset than on
    the culturally-agnostic one. CS questions come mostly from Social Sciences and Humanities,
    while CA retains the harder STEM and Medical questions.
  scope: Aggregated over 14 models on the 14 human-translated languages; the standard deviation
    across languages is nevertheless higher on CS than CA for every model.
  evidence: Section 4.2; Figure 9; Figure 12
- id: ht-vs-mt
  kind: result
  text: Claude Sonnet 3.5 and GPT-4o score significantly better on machine-translated than
    human-translated culturally-sensitive Yoruba questions, while models generally score better
    on human-translated data in French; Aya Expanse 32B is the only model consistent across
    both.
  scope: Run on the culturally-sensitive subset in three languages only — French (high-resource),
    Korean (mid) and Yoruba (low); human translations from professional or MMMLU sources,
    machine translations from Google Translate.
  evidence: Section 4.2; Figure 11
- id: translation-choice
  kind: result
  text: Google Translate achieves higher ChrF++ scores than GPT-3.5-Turbo across all MMLU
    subject categories and shows lower deviation across languages, measured against professional
    human translations from MMMLU.
  scope: Restricted to languages present in both machine-translated sets and in human-translated
    MMMLU, which serves as the reference; GPT-3.5-Turbo is the system behind the earlier multilingual
    MMLU.
  evidence: Section 3.1; Figure 7; Appendix D.1
- id: edit-rate
  kind: result
  text: Human reviewers edited 7,565 of the reviewed machine-translated MMLU samples, 36.9%
    of them, with professional annotators editing 789 samples per language on average (38.5%)
    and community contributors 362 per language (17.7%).
  scope: Edits to Google Translate output; professionals covered the gold-set languages Arabic,
    French, Hindi and Spanish, community annotators 11 further languages.
  evidence: Section 3.1; Figure 8
- id: dataset-context
  kind: context
  text: Global-MMLU is a 42-language MMLU test set of 589,764 samples that ships cultural-sensitivity
    metadata alongside the questions. It combines professional translations with post-edits
    (14 languages), crowdsourced translations (11 languages) and machine translations (16
    languages).
  scope: Released under a permissive license for evaluation; the cultural-sensitivity labels
    cover only the 2,850 annotated questions extended to all 42 languages, not all 14K MMLU
    questions, and dialect labels were assigned on the English source only.
  evidence: Section 3.2; Table 4
- id: practice-context
  kind: context
  text: Global-MMLU argues that multilingual LLM evaluation should be reported on culturally-sensitive
    and culturally-agnostic subsets separately rather than on a single machine-translated
    MMLU score, because translation alone delivers multilinguality without multiculturality.
  scope: A benchmark-practice recommendation advanced as of 2025 publication, grounded in
    the paper's own annotations of English MMLU and a 14-model rank-change analysis; whether
    it transfers to non-MMLU benchmarks is not evaluated.
  evidence: Section 1; Section 6
- id: participatory-context
  kind: context
  text: Global-MMLU was built with roughly 200 compensated professional and community annotators.
    They both labelled MMLU questions for cultural sensitivity and post-edited translations,
    making it a participatory-research benchmark across 42 languages.
  scope: 'Contributions were unevenly distributed: beyond four compensated gold-standard languages,
    community participation had a long tail of annotators submitting one or two annotations,
    so per-language annotator diversity varies.'
  evidence: Section 2.1; Section 7
misreadings:
- The 28% culturally-sensitive figure is a property of MMLU's English questions, not an artefact
  introduced by translating MMLU into other languages; the bias is inherited by every translated
  variant.
- 'Higher model accuracy on the culturally-sensitive subset does not mean those questions
  are easier to answer with cultural knowledge: CS questions are drawn mostly from Social
  Sciences and Humanities, where models score higher, while the culturally-agnostic subset
  keeps the harder STEM and Medical questions.'
- Labelling MMLU questions as culturally sensitive or agnostic does not make the benchmark
  culturally inclusive; Global-MMLU identifies gaps in non-Western representation but does
  not add culturally grounded non-Western knowledge.
- 'Global-MMLU is not fully human-translated: 16 of its 42 languages are machine-translated
  only, and human-verified content is concentrated in 4 professionally translated gold languages,
  11 community-translated languages and 10 languages taken from OpenAI''s MMMLU.'
- Models scoring better on machine-translated than human-translated low-resource data is not
  evidence that machine translation is better test data; the paper reads it as models' training
  distributions matching machine-translated text, which obscures true in-language capability.
qa:
- q:
  - How much of MMLU requires culture-specific knowledge?
  - What fraction of MMLU questions need cultural or regional knowledge to answer?
  - Is the MMLU benchmark culturally biased?
  answers:
  - cs-share
  - culture-western
  - geo-western
- q:
  - How US-centric is MMLU?
  - Which countries does MMLU's cultural knowledge come from?
  - Does MMLU mostly test knowledge about the United States?
  answers:
  - us-concentration
  - geo-western
- q:
  - Which MMLU subjects are the most culturally biased?
  - Do STEM questions in MMLU need cultural knowledge?
  - Where in MMLU is cultural sensitivity concentrated by subject?
  answers:
  - subject-skew
- q:
  - Do LLM leaderboard rankings change when culturally sensitive questions are removed?
  - How much do model rankings shift between culturally-sensitive and culturally-agnostic
    MMLU subsets?
  - Is a single translated MMLU score enough to rank multilingual models?
  answers:
  - rank-volatility
  - practice-context
- q:
  - Why do models score higher on culturally-sensitive MMLU questions?
  - Are culturally sensitive MMLU questions harder for language models?
  answers:
  - cs-easier
- q:
  - How stable is multilingual evaluation for low-resource languages?
  - Does variance in model accuracy grow for low-resource languages on MMLU?
  - How much more variable are LLM scores across low-resource than high-resource languages?
  answers:
  - resource-variability
- q:
  - Can machine translation replace human translation for evaluating low-resource languages?
  - Do models perform differently on human-translated versus machine-translated MMLU?
  - Is machine-translated test data safe for benchmarking Yoruba or Korean?
  answers:
  - ht-vs-mt
  - edit-rate
- q:
  - Which machine translation system was used to build a 42-language MMLU, and why?
  - Is Google Translate better than GPT-3.5 for translating MMLU?
  - How was translation quality for multilingual MMLU verified by humans?
  answers:
  - translation-choice
  - edit-rate
- q:
  - Is there a multilingual MMLU with human-verified translations?
  - How many languages and samples does Global-MMLU cover?
  - Which multilingual benchmark labels questions as culturally sensitive or agnostic?
  answers:
  - dataset-context
  - participatory-context
- q:
  - What should I read about cultural bias in multilingual LLM benchmarks?
  - Which paper established that translated English benchmarks carry Western-centric bias?
  - Where should I start reading about culturally aware multilingual evaluation?
  answers:
  - practice-context
  - cs-share
  - dataset-context
- q:
  - How were MMLU questions labelled as culturally sensitive, and by whom?
  - Who annotated the cultural sensitivity labels for multilingual MMLU?
  - How reliable is the culturally-sensitive labelling of MMLU questions?
  answers:
  - participatory-context
  - cs-share
- q:
  - Does labelling culturally sensitive questions make a benchmark culturally inclusive?
  - What are the limits of the Global-MMLU cultural-sensitivity subsets?
  answers:
  - practice-context
  - dataset-context
---
