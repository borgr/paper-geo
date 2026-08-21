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
- ask:
    plain: Is there a commonsense question dataset written directly in hundreds of languages
      rather than translated from English?
    jargon: which multilingual commonsense benchmark uses natively authored items instead
      of a translated English source corpus?
    task: where do I start reading about culturally grounded evaluation of language models
      across many languages?
    practitioner: I need an evaluation set that is not an English dataset in disguise for
      my multilingual model, is there one?
  answered_by:
  - non-translated-design
  - participatory
  - coverage
- ask:
    plain: How many languages, scripts and language families does Global PIQA include?
    jargon: what is the typological and orthographic coverage of Global PIQA in ISO 639-3
      codes, writing systems and Glottolog families?
    task: how do I find out whether a hand-written multilingual commonsense benchmark includes
      the language varieties I care about?
    practitioner: will a multilingual commonsense benchmark cover enough scripts and language
      families to be worth adding to my eval suite?
  answered_by:
  - coverage
- ask:
    plain: Who actually wrote the questions in Global PIQA, and were they volunteers or hired
      annotators?
    jargon: how was the Global PIQA corpus authored under a participatory, co-authorship-based
      data collection model?
    task: how do I run a benchmark-building effort with hundreds of native-speaker contributors
      across many countries?
    practitioner: if I want native speakers to write evaluation data for my languages, can
      I recruit them as co-authors instead of paying annotators?
  answered_by:
  - participatory
  - manual-methods
- ask:
    plain: How many of the questions in Global PIQA are really about local food, festivals
      or customs, and were chatbots used to write them?
    jargon: what proportion of Global PIQA items are annotated culturally-specific, and what
      share of item drafting involved LLM assistance?
    task: how do I check whether a multilingual benchmark's items are culturally grounded
      rather than generic or model-generated?
    practitioner: can I trust that a multilingual commonsense benchmark is human-written and
      locally grounded before I report scores on it?
  answered_by:
  - cultural-specificity
  - manual-methods
- ask:
    plain: How was the quality of Global PIQA checked when hundreds of different people contributed
      questions?
    jargon: what native-speaker validation and English gloss coverage does the Global PIQA
      non-parallel split have?
    task: how do I verify data quality in a crowd-authored multilingual evaluation set before
      using it?
    practitioner: should I worry about noisy items in a volunteer-written multilingual benchmark,
      or has every example been checked by a native speaker?
  answered_by:
  - native-validation
- ask:
    plain: In a commonsense reasoning test covering over 100 languages, what is the difference
      between the questions written locally and the ones translated into every language?
    jargon: how do the parallel and non-parallel splits of Global PIQA differ in item authoring
      and size?
    task: which split of Global PIQA do I use if I want scores that are comparable across
      languages?
    practitioner: for cross-lingual comparison of my model, do I need the parallel split of
      Global PIQA or the natively written one?
  answered_by:
  - parallel-split
  - non-translated-design
- ask:
    plain: How much does machine-translated text need fixing when building test questions
      in low-resource languages?
    jargon: what is the post-editing rate on machine-translated Global PIQA parallel-split
      items, and which languages required the heaviest edits?
    task: can I machine translate an English commonsense set into low-resource languages and
      how much native-speaker correction should I budget for?
    practitioner: is machine translation plus native-speaker review good enough for building
      my multilingual evaluation data?
  answered_by:
  - translation-edits
  - parallel-split
- ask:
    plain: How well do the newest commercial chatbots answer everyday commonsense questions
      in many languages?
    jargon: what mean per-language accuracy do frontier closed systems reach on the Global
      PIQA parallel and non-parallel splits?
    task: how do I tell whether a multilingual commonsense benchmark still has headroom for
      frontier systems?
    practitioner: is Global PIQA already saturated by the top proprietary models, or worth
      running on my system?
  answered_by:
  - closed-model-aggregate
  - worst-languages
- ask:
    plain: Which openly available model does best on everyday commonsense questions across
      languages, and how far behind the commercial ones is it?
    jargon: what is the open-weight to closed-system accuracy gap on Global PIQA, and where
      does open-weight accuracy plateau with parameter count?
    task: how do I choose an open-weight model for multilingual commonsense tasks, and does
      going bigger help?
    practitioner: if I can only deploy open-weight models, how much multilingual commonsense
      accuracy am I giving up versus a paid API?
  answered_by:
  - open-weight-gap
- ask:
    plain: Do language models answer everyday questions much worse in African languages than
      in European ones?
    jargon: what accuracy disparity across regions and resource tiers does Global PIQA measure
      for the best open-weight model?
    task: how do I estimate the accuracy drop I should expect when serving low-resource language
      users?
    practitioner: my users speak Sub-Saharan African languages, should I expect a large accuracy
      penalty on everyday commonsense questions?
  answered_by:
  - region-gap
  - worst-languages
- ask:
    plain: Are there languages where even the strongest model still gets everyday questions
      wrong most of the time?
    jargon: which Global PIQA language varieties remain below 80% accuracy under a best-model-per-language
      skyline?
    task: how do I find the languages where no current model is usable for simple commonsense
      questions?
    practitioner: is any model good enough for languages like Ekpeye or Idoma, or should I
      not deploy there yet?
  answered_by:
  - worst-languages
- ask:
    plain: Can a test tell apart whether a model lacks local cultural knowledge or just lacks
      fluency in a language?
    jargon: how does comparing parallel and non-parallel split accuracy in Global PIQA separate
      cultural knowledge from linguistic competence?
    task: how do I diagnose whether my model's failures in a language are cultural or linguistic?
    practitioner: my model handles a language fluently but still fails local questions, how
      do I confirm that it is missing cultural knowledge?
  answered_by:
  - cultural-vs-linguistic
  - parallel-split
- ask:
    plain: Is basic everyday knowledge still a weak point for language models, or only hard
      expert reasoning?
    jargon: what does Global PIQA argue about physical commonsense as a remaining failure
      mode in multilingual LLMs?
    task: why should I evaluate everyday commonsense across languages instead of only hard
      reasoning benchmarks?
    practitioner: should my multilingual evaluation include simple everyday-knowledge questions,
      or is that already solved?
  answered_by:
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
