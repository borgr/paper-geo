<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from build/sidecar_tasks.json. Every claim, number
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
-->
---
coined: Global-MMLU
gloss: a 42-language version of the MMLU benchmark with human-verified translations and labels
  marking which questions need culture-specific knowledge
one_liner: 'Global-MMLU re-annotates MMLU for cultural dependence and re-translates it into
  42 languages: 28% of questions need culturally sensitive knowledge, 86.5% of the culture-dependent
  ones need specifically Western knowledge, and model rankings shift nearly twice as much
  on that subset as on the culturally agnostic one.'
claims:
- id: mmlu-is-culturally-sensitive
  text: 28% of MMLU questions require culturally sensitive knowledge -- geographic, cultural
    or dialect-specific -- to be answered correctly; geographic knowledge is the most common,
    at 54.7% of all culturally sensitive questions, followed by cultural knowledge at 32.7%
    and dialect knowledge at 0.5%.
  scope: 'Measured on MMLU Annotated: a uniform random sample of 50 questions from each of
    MMLU''s 57 subjects (2,850 questions, 20% of the test set), labelled in English by majority
    vote among at least three annotators. ''Culturally sensitive'' means answering requires
    prior cultural, geographic or dialect knowledge -- not that the question is offensive
    or badly written. The categories overlap: 10.6% require both cultural and geographic knowledge
    and 1.5% all three. The paper''s own denominators shift within this passage between ''all
    CS questions'' and ''all questions'', so treat the three shares as approximate.'
  evidence: Section 2.2, Figure 3, Table 1
- id: western-centric
  text: Among MMLU questions that require cultural knowledge, 86.5% require specifically Western
    cultural knowledge -- the next largest category, South Asian, is 4% -- and among those
    requiring geographic knowledge, 84.9% concern North America (64.5%) or Europe (20.4%).
  scope: Shares of the tagged culturally sensitive portion of MMLU Annotated, not of MMLU
    as a whole. Figures 4 and 5 exclude samples carrying no region or culture tag and samples
    carrying several, so these are shares of singly-tagged questions. Latin American, African
    and Indigenous cultures account for 1.3%, 1.1% and 0.7% of culture tags. The claim is
    about what the questions presuppose of the answerer, not about who wrote them.
  evidence: Section 2.2, Figure 4
- id: us-dominance
  text: Within the MMLU questions tagged as requiring Western cultural knowledge, 73.9% require
    knowledge about the United States and 8% about the United Kingdom; Middle Eastern culture,
    which is 2.7% of annotated questions overall, is largely represented by Iraq (37.5%) and
    Turkey (25%).
  scope: 'Country-level shares within each culture tag of the culturally sensitive subset,
    again excluding multi-tagged samples. The overall shares are small -- 4.0% of annotated
    questions concern South Asian and 3.1% East Asian culture -- so a large within-culture
    percentage can rest on very few questions. Part of the US concentration is structural
    rather than incidental: MMLU includes subjects that are US-specific by construction (US
    History, US Accounting, US Law).'
  evidence: Section 2.2, Figure 5, Appendix B
- id: rankings-change
  text: 'Model rankings on MMLU depend on whether the questions are culturally loaded: across
    14 models, the culturally agnostic subset produces an average of 3.4 rank changes and
    3.7 position shifts relative to the uniform annotated sample, while the culturally sensitive
    subset produces 5.7 rank changes and 7.3 position shifts.'
  scope: Counted per language against each model's rank on MMLU Annotated, so this measures
    how unstable a leaderboard is under a change of question subset -- not how much accuracy
    moved. High-resource languages show the largest culturally sensitive effect (6.8 rank
    changes, 9.1 position shifts) and mid-resource languages the smallest gap between the
    two subsets. The culturally sensitive subset is also the smaller of the two (792 English
    questions against 2,058), so some of the extra volatility is sample size.
  evidence: Table 2, Section 4.2 (Model Rank Changes)
- id: cultural-bias-by-subject
  text: 'Cultural sensitivity in MMLU is concentrated in the humanities: 68% of Humanities
    questions were tagged culturally sensitive, over 80% for Philosophy, Moral Scenarios,
    High School US History and High School Government and Politics, against 30 of 950 STEM
    questions (3.15%), with Clinical Knowledge, Computer Security and Econometrics entirely
    culturally agnostic.'
  scope: Per-subject rates within the 50-question-per-subject annotated sample, so each subject's
    rate rests on 50 questions. Twelve of the 57 subjects contained no culturally sensitive
    questions at all and are omitted from Figure 3, while all questions in World Religions
    and Moral Scenarios contained at least one such reference. Moral Scenarios lands here
    because MMLU's own instruction specifies 'moral standards in the US', which is a property
    of the prompt rather than of morality.
  evidence: Section 2.2, Figures 3 and 6, Table 1
- id: global-mmlu-dataset
  text: Global-MMLU covers MMLU's 14K-question test set in 42 languages including English
    -- 589,764 questions -- built from professional translations and post-edits for 14 languages,
    community translations for 11, and machine translation for the remaining 16, with the
    2,850-question annotated subset carrying culturally-sensitive and culturally-agnostic
    labels propagated to every language.
  scope: 'Translation provenance is uneven by design and recorded per language: four languages
    (Arabic, French, Hindi, Spanish) form the professionally post-edited Gold Set, ten more
    come from OpenAI''s human-translated MMMLU, eleven passed a threshold of at least 50 community-translated
    samples, and the rest are Google Translate output reviewed by nobody. Global-MMLU inherits
    MMLU''s questions and therefore its content biases -- the contribution is knowing which
    questions are culturally loaded and being able to report on them separately, not removing
    them.'
  evidence: Section 3, Section 3.1, Section 3.2
- id: cs-accuracy-higher-but-variance-higher
  text: Models score higher on MMLU's culturally sensitive questions than on its culturally
    agnostic ones -- because the sensitive ones come disproportionately from Social Sciences
    and Humanities rather than STEM and Medical -- yet their accuracy varies more across languages
    on the sensitive subset, for every model tested.
  scope: 'A composition effect, not evidence that models handle culture well: the culturally
    sensitive subset is 26.3% Social Sciences and 2.9% STEM, against 21.1% and 33.3% in the
    uniform annotated sample. The variance direction holds across all 14 models and all three
    resource levels. The paper is explicit that its 14-model comparison is meant to expose
    subset behaviour, not to rank models against each other -- open and closed models were
    evaluated by different methods (log-probabilities against generated answers).'
  evidence: Section 4.2 (Performance on CS is higher but presents more variance), Figure 9,
    Figure 12, Table 1
- id: low-resource-variance
  text: 'Cross-language variability in MMLU accuracy roughly doubles from high- to low-resource
    languages: the average standard deviation across languages is 3.21 (culturally agnostic)
    and 3.86 (culturally sensitive) for high-resource languages, 3.42 and 4.6 for mid-resource,
    and 6.37 and 6.78 for low-resource -- increases of 98% and 75% over high-resource.'
  scope: Standard deviation across the languages within each resource group, averaged over
    the 14 models; resource levels follow Joshi et al. (2019) as categorised by Singh et al.
    (2024). Some of the low-resource spread is translation quality rather than model competence,
    which is exactly the paper's argument for needing human-translated or in-language evaluation
    data there -- without it, a low score cannot be attributed to the model.
  evidence: Section 4.2 (Evaluations Across High-, Mid-, and Low-Resource Languages), Figure
    10
- id: machine-translation-flatters-frontier-models
  text: On low-resource languages, GPT-4o and Claude 3.5 Sonnet score significantly better
    on machine-translated MMLU questions than on human-translated ones -- the paper's reading
    is that a machine-translated test set matches the machine-translated data these models
    were trained on -- while Aya Expanse 32B is the only model consistent across both.
  scope: Shown for the culturally sensitive subset in three example languages (French, Korean,
    Yoruba) in Figure 11, not across all 42. The training-data explanation is the authors'
    interpretation and is unverifiable for closed models. The direction reverses for high-resource
    languages, where models generally do better on human-translated data, and mid-resource
    languages sit in between with the gap narrowing for Claude 3.5 Sonnet and Qwen2.5 32B.
  evidence: Section 4.2 (Human Translated vs. Machine Translated), Figure 11
- id: model-size-and-sensitivity
  text: 'Larger models are more stable under a change of MMLU subset: average rank changes
    are 0.21 (culturally agnostic) and 0.67 (culturally sensitive) for large open models,
    0.33 and 1.97 for mid-size, and 0.35 and 0.45 for small models -- but the small models''
    apparent stability comes from being weaker on both, at 51.3% and 54.8% accuracy against
    61.6% and 66.8% for large models.'
  scope: Open-weight models only; GPT-4o and Claude 3.5 Sonnet are excluded because their
    sizes are undisclosed. The groups are small -- two large models (Llama 3.1 70B, Command
    R+), four mid-size, six small -- so each average is over few models. Maximum position
    shift is 3 for large models against 5 for small ones.
  evidence: Section 4.2 (Model size influences performance variations), Section 4.1
- id: annotation-protocol
  text: The cultural-sensitivity labels in Global-MMLU come from 200 compensated professional
    and community annotators reviewing 2,850 English MMLU questions, each question seen by
    at least three annotators (96.4% by more than three) and labelled by majority vote; only
    2.4% of questions were judged to depend on temporal knowledge.
  scope: Majority vote means a question counts as culturally sensitive when half or more of
    its annotators applied the tag -- a threshold, not a consensus. Krippendorff's alpha shows
    high agreement for most subjects, unanimity for Anatomy, and real disagreement for six,
    with Moral Scenarios and High School US History the worst. Dialect judgements were made
    on the original English sentences, so they describe English regional variation rather
    than anything introduced by translation.
  evidence: Section 2.1, Section 2.2 (Inter-annotator agreement), Appendix C.1.1
- id: human-edit-rates
  text: 'Human review changed a substantial share of Global-MMLU''s machine translations:
    annotators made 7,565 edits, 36.9% of the samples they reviewed, with professional annotators
    editing 789 samples per language on average (38.5%) and community annotators 362 (17.7%).'
  scope: Edit rate measures annotator time and resources, not translation quality per language
    -- the paper states explicitly that the professional/community gap cannot be read as a
    quality difference between their languages. An edit is any change made where the translation
    did not capture the original's intent; it is unweighted by size, and per-subject edit
    distances are in the appendix. Annotation ran on Argilla, with the original and the machine
    translation shown side by side.
  evidence: Section 3.1, Figure 8, Appendix D
- id: google-translate-choice
  text: Global-MMLU's machine-translation baseline is Google Translate rather than an LLM,
    chosen deliberately so that no evaluated model would be scored on text produced by a model
    that might favour its own generations; it also scored higher ChrF++ than GPT-3.5-turbo
    across all subjects, with lower deviation across languages.
  scope: The self-preference concern is a validity argument backed by prior work on models
    preferring their own outputs, not a measured effect in this paper. The ChrF++ comparison
    is against GPT-3.5-turbo specifically -- the system behind the widely used 26-language
    translated MMLU -- not against current frontier translation models, and the paper notes
    that recent work already finds LLMs surpassing Google Translate on some high-resource
    languages.
  evidence: Section 3.1, Figure 7
qa:
- q:
  - Is MMLU culturally biased?
  - How much of MMLU requires Western knowledge?
  - Is the MMLU benchmark US-centric?
  - What cultural biases are in the MMLU benchmark?
  answers:
  - mmlu-is-culturally-sensitive
  - western-centric
  - us-dominance
- q:
  - Can I just machine-translate an English benchmark to evaluate multilingual models?
  - What is wrong with using translated MMLU?
  - Is machine translation good enough for multilingual evaluation?
  - Why is translating a benchmark not enough for multilingual evaluation?
  answers:
  - global-mmlu-dataset
  - machine-translation-flatters-frontier-models
  - rankings-change
  - google-translate-choice
- q:
  - Do model rankings change on culturally sensitive questions?
  - Are LLM leaderboards stable across benchmark subsets?
  - How much do MMLU rankings shift between culturally sensitive and agnostic questions?
  answers:
  - rankings-change
  - model-size-and-sensitivity
  - cs-accuracy-higher-but-variance-higher
- q:
  - What is Global-MMLU?
  - How many languages does Global-MMLU cover?
  - What is the difference between Global-MMLU and translated MMLU?
  - Where can I get a multilingual version of MMLU?
  answers:
  - global-mmlu-dataset
  - annotation-protocol
  - human-edit-rates
- q:
  - How should I evaluate LLMs on low-resource languages?
  - Are machine-translated benchmarks reliable for low-resource languages?
  - Why do evaluation scores vary so much across low-resource languages?
  answers:
  - low-resource-variance
  - machine-translation-flatters-frontier-models
  - global-mmlu-dataset
- q:
  - Which MMLU subjects are culturally biased?
  - Is the STEM part of MMLU culturally neutral?
  - Which parts of MMLU can I use for cross-cultural comparison?
  answers:
  - cultural-bias-by-subject
  - mmlu-is-culturally-sensitive
- q:
  - Do models do worse on culturally sensitive questions?
  - Are LLMs weaker at culture-specific knowledge?
  - Why is accuracy higher on the culturally sensitive MMLU subset?
  answers:
  - cs-accuracy-higher-but-variance-higher
  - cultural-bias-by-subject
  - low-resource-variance
- q:
  - How were the cultural sensitivity labels in Global-MMLU made?
  - Who annotated Global-MMLU, and how reliable are the labels?
  - What counts as a culturally sensitive question?
  answers:
  - annotation-protocol
  - mmlu-is-culturally-sensitive
  - human-edit-rates
misreadings:
- '''Culturally sensitive'' here does not mean offensive, ill-posed or in need of removal.
  It means answering the question correctly requires prior cultural, geographic or dialect-specific
  knowledge. The recommendation is to report the culturally sensitive and culturally agnostic
  subsets separately, not to delete either.'
- The percentages have different denominators and are easy to merge into a wrong number. 28%
  of MMLU requires culturally sensitive knowledge of any kind; 86.5% is the Western share
  of the culture-tagged questions; 84.9% is the North-America-plus-Europe share of the geography-tagged
  ones. It is not the case that 86.5% of MMLU is Western.
- Models are not worse on culturally sensitive questions -- average accuracy is higher there,
  because that subset skews to Social Sciences and Humanities while the agnostic one carries
  more STEM and Medical. What the cultural questions destabilise is consistency across languages
  and the ranking between models, not the score level.
- Global-MMLU is not a de-biased MMLU, and it is not fully human-translated. It keeps MMLU's
  questions and adds labels for which ones are culturally loaded; 16 of its 42 languages are
  machine translation with no human review, and the four professionally post-edited languages
  are Arabic, French, Hindi and Spanish.
- '''Human-translated test data gives more accurate scores'' is backwards for low-resource
  languages. GPT-4o and Claude 3.5 Sonnet scored significantly better on machine-translated
  data than on human-translated data there, most plausibly because machine-translated text
  resembles what they were trained on. A machine-translated test set can flatter a model rather
  than penalise it.'
- The rank-change figures are not accuracy differences. 5.7 rank changes on the culturally
  sensitive subset against 3.4 on the agnostic one describes leaderboard instability when
  the question subset changes; it says nothing about how far accuracy moved, and the sensitive
  subset is the smaller of the two (792 English questions against 2,058).
- The professional-versus-community edit rates (38.5% against 17.7%) are not a quality comparison
  between the languages involved. The paper attributes the gap to differences in annotator
  time and resources and says explicitly that it cannot be read as translation quality.
terminology:
  Global-MMLU: 'The released dataset: MMLU''s 14K-question test set in 42 languages, with
    human-verified translations where available and per-question metadata marking whether
    answering needs cultural, geographic or dialect knowledge.'
  transMMLU: This paper's collective term for the machine-translated MMLU variants in common
    use as multilingual benchmarks -- not one dataset, and not something anyone releases under
    that name. Used to name the practice the paper is arguing against.
  Culturally-Sensitive (CS) / Culturally-Agnostic (CA): A question is CS if a majority of
    annotators judged that answering it correctly requires cultural, geographic or dialect
    knowledge, and CA if none of the three applies. A property of what the question presupposes,
    not of its quality or its subject matter.
  MMLU Annotated (MA): The 2,850-question uniform sample the annotation was performed on --
    50 questions from each of MMLU's 57 subjects, 20% of the test set. It is also the reference
    point every reported rank change is measured against.
  Gold Set: 'The four languages whose machine translations were reviewed and post-edited by
    compensated professional annotators: Arabic, French, Hindi and Spanish. Distinct from
    the ten languages taken from OpenAI''s human-translated MMMLU and the eleven community-translated
    ones.'
  rank changes / position changes: Reported as a pair throughout. Read the first as how many
    models changed rank between two subsets and the second as the total number of positions
    those models moved; the paper does not define them explicitly, so the pair matters more
    than either number alone.
links_extra:
  data: https://hf.co/datasets/CohereForAI/Global-MMLU
---
