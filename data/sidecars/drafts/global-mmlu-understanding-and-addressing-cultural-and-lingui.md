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
gloss: a 42-language version of the MMLU benchmark with human-verified translations for some
  languages and per-question labels marking which questions need culture-specific knowledge
one_liner: 'Global-MMLU re-annotates MMLU for cultural dependence and re-releases it in 42
  languages: 28% of questions need culture-specific knowledge, 86.5% of the culture-tagged
  ones need Western knowledge, and model rankings move about twice as much on that subset
  as on the culturally agnostic one.'
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
    and 1.5% all three. Note that the paper''s own contribution bullet in Section 1 renders
    this as ''28% of questions require specific knowledge of Western cultures'', which is
    not what Section 2.2 measures; 28% is the culturally sensitive share of any kind, and
    the Western share is 86.5% of the culture tags.'
  evidence: Section 2.2, Figure 3, Table 1; the conflicting phrasing is in the Section 1 contributions
    list
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
- id: culture-and-region-tags-collapse-onto-the-us
  text: 'The culture and region tags are not independent axes but two views of the same concentration:
    73.3% of Western-culture questions are also tagged North America and 25.5% Europe, 97.2%
    of Asian-culture questions are tagged Asia, the United States accounts for 89.6% of all
    North America tags (Canada and the UK 0.8% each), and every question in the residual ''Other''
    culture category is about Russia.'
  scope: 'Cross-tabulations over the culturally sensitive subset only, in the appendix, with
    multi-tagged samples excluded as in the main figures. Tag counts inside the small categories
    are tiny, so their internal splits are shape rather than statistics: Indigenous culture
    is two countries (USA 66.7%, Micronesia 33.3%), Latin American culture four (Bolivia and
    Mexico 33.3% each, Honduras and Peru 16.7% each). Europe is the more evenly spread region
    (UK 20.1%, France 10.1%) and Africa the most even (Egypt and South Africa 33.3% each).
    The region set is the six-region Pew taxonomy; the authors say in Limitations that they
    would now use the more granular World Bank taxonomy, which separates Central America and
    Sub-Saharan Africa.'
  evidence: Appendix B, Figures 14-17; Section 7 (Region Category Assignment)
- id: rankings-change
  text: 'Model rankings on MMLU depend on whether the questions are culturally loaded: across
    14 models, the culturally agnostic subset produces an average of 3.4 rank changes and
    3.7 position shifts relative to the uniform annotated sample, while the culturally sensitive
    subset produces 5.7 rank changes and 7.3 position shifts.'
  scope: 'Counted per language against each model''s rank on MMLU Annotated, so this measures
    how unstable a leaderboard is under a change of question subset -- not how much accuracy
    moved. The culturally agnostic baseline is not zero: even questions requiring no cultural
    knowledge reshuffle 3.4 of 14 models, so the cultural effect is the gap between the two
    numbers, not the whole of the second. High-resource languages show the largest culturally
    sensitive effect (6.8 rank changes, 9.1 position shifts) and mid-resource languages the
    smallest gap between the two subsets. The culturally sensitive subset is also the smaller
    of the two (792 English questions against 2,058), so some of the extra volatility is sample
    size. The families the paper singles out as trending upward on culturally sensitive data
    are Aya Expanse and Command R, both from the lab that led the dataset effort; the paper
    reports the trend without comment.'
  evidence: Table 2, Section 4.2 (Model Rank Changes), Section 1 contributions
- id: largest-shifts-in-lower-resource-languages
  text: 'The most violent reshuffles are in lower-resourced languages: rank shifts of up to
    5 positions on Malagasy and 13 of 14 models changing rank on Ukrainian, against a maximum
    shift of 3 positions for the large models anywhere.'
  scope: 'Table 3 collects the extremes across Greek, Ukrainian, Malagasy and Shona; per-language
    tables for all 42 are in Appendix A.2. Averaged rank changes are not monotone in resource
    level -- high-resource languages average 3.3 (agnostic) and 6.8 (sensitive), mid-resource
    3.7 and 4.7, low-resource 3.3 and 3.7 -- so it is the position shifts, not the count of
    models moving, that grow toward the low-resource end (5.7 and 7.9). The paper''s low-resource
    paragraph cites Ukrainian as its example, but its own language table classifies Ukrainian
    as mid-resource. Instability in these languages cannot be separated from translation quality:
    16 of the 42 languages are unreviewed machine translation.'
  evidence: Section 4.2 (Model Rank Changes), Tables 3-6, Table 4 for the resource classes
- id: cultural-bias-by-subject
  text: 'Cultural sensitivity in MMLU is concentrated in the humanities: 68% of Humanities
    questions were tagged culturally sensitive, over 80% for Philosophy, Moral Scenarios,
    High School US History and High School Government and Politics, against 30 of 950 STEM
    questions (3.15%), with Clinical Knowledge, Computer Security and Econometrics entirely
    culturally agnostic.'
  scope: Per-subject rates within the 50-question-per-subject annotated sample, so each subject's
    rate rests on 50 questions. Twelve of the 57 subjects contained no culturally sensitive
    questions at all and are omitted from Figure 3, while every sampled question in World
    Religions and Moral Scenarios contained at least one such reference. Moral Scenarios lands
    here because MMLU's own instruction specifies 'moral standards in the US', which is a
    property of the prompt rather than of morality.
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
    them. Released under a permissive licence for evaluation use.'
  evidence: Section 3, Section 3.1, Section 3.2, Section 6
- id: translation-provenance-by-language
  text: 'Which languages actually contain human translation is a per-language fact worth checking
    before use: 14 are fully human-translated (Arabic, Bengali, Chinese, French, German, Hindi,
    Indonesian, Italian, Japanese, Korean, Portuguese, Spanish, Swahili, Yoruba), 11 mix machine
    translation with community post-edits (Amharic, Czech, Malay, Persian, Romanian, Russian,
    Sinhala, Telugu, Turkish, Ukrainian, Vietnamese), and 16 are machine translation only
    (Dutch, Filipino, Greek, Hausa, Hebrew, Igbo, Kyrgyz, Lithuanian, Malagasy, Nepali, Nyanja,
    Polish, Serbian, Shona, Somali, Swedish).'
  scope: Read off the per-language table, which marks each language as fully machine-translated,
    fully human-translated, or both; English is the original and is marked as containing both.
    The fully-human 14 are the four Gold Set languages plus the ten taken from OpenAI's MMMLU,
    so their human coverage is the whole test set; the mixed 11 are machine translation with
    human post-editing over a sample, which can be as little as the 50-sample inclusion threshold.
    Being machine-translation-only does not make a language unusable -- it makes a low score
    unattributable between the model and the translation, which is the paper's own argument.
  evidence: Table 4, Section 3.1, Section 3.2, Section 1 contributions
- id: human-review-covered-a-slice
  text: 'The human verification behind Global-MMLU covers a slice of each language, not all
    of it: annotators fully reviewed 37% of the samples put in front of them and edited 12.3%
    of them overall, with 7,565 edits in total amounting to 36.9% of what was reviewed.'
  scope: 'Two different denominators, reported in two places, and easy to conflate: 36.9%
    is the share of reviewed samples that were edited (Section 3.1), 12.3% is the share of
    provided samples edited overall (Appendix C). Neither is a share of the 14,042-question
    test set. The per-language pool put up for review can be recovered from the reported pair
    -- professionals averaged 789 edits per language and that is given as 38.5% -- which puts
    the pool at roughly 2,050 samples per language, i.e. about 15% of the test set; that division
    is a derivation from the paper''s numbers, not a figure it states. So for a Gold Set language,
    ''human-verified'' means a professional looked at part of a ~2,050-question sample and
    changed some of it, on top of full machine translation.'
  evidence: Section 3.1, Figure 8, Appendix C (Schedule), Appendix D.2
- id: labels-are-english-only
  text: The culturally-sensitive and culturally-agnostic labels were assigned to 2,850 English
    questions and then copied onto the 41 other languages; no question was judged for cultural
    loading from the perspective of a reader of the target language.
  scope: 'This is a deliberate design choice and it bounds what the labels mean: a question
    tagged culturally agnostic is one that an English-reading annotator pool judged to need
    no cultural, geographic or dialect knowledge, which is not the same as being equally natural
    for a Telugu or Yoruba reader. The dialect judgements are explicitly about variation in
    English -- slang, idiom, regional vocabulary in the source -- and say nothing about dialect
    in the translations. What the labels do support is exactly what the paper uses them for:
    holding the question set fixed and comparing the same models across languages on the two
    subsets.'
  evidence: Section 2.1, Section 2.2 (Dialect Knowledge), Section 4.1 (subset definitions)
- id: cs-accuracy-higher-but-variance-higher
  text: Models score higher on MMLU's culturally sensitive questions than on its culturally
    agnostic ones -- because the sensitive ones come disproportionately from Social Sciences
    and Humanities rather than STEM and Medical -- yet their accuracy varies more across languages
    on the sensitive subset, for every model tested.
  scope: 'A composition effect, not evidence that models handle culture well: the culturally
    sensitive subset is 26.3% Social Sciences and 2.9% STEM, against 21.1% and 33.3% in the
    uniform annotated sample, and the subject profile behind it is visible in the appendix
    (Aya Expanse 32B averages 66.4% with most STEM subjects below that line and most Social
    Sciences and Humanities subjects above it). The variance direction holds across all 14
    models and all three resource levels. The paper is explicit that its 14-model comparison
    is meant to expose subset behaviour, not to rank models against each other -- open and
    closed models were evaluated by different methods (log-probabilities against generated
    answers).'
  evidence: Section 4.2 (Performance on CS is higher but presents more variance), Figure 9,
    Appendix A.3 and Figure 12, Table 1
- id: low-resource-variance
  text: 'Cross-language variability in MMLU accuracy roughly doubles from high- to low-resource
    languages: the average standard deviation across languages is 3.21 (culturally agnostic)
    and 3.86 (culturally sensitive) for high-resource languages, 3.42 and 4.6 for mid-resource,
    and 6.37 and 6.78 for low-resource -- increases of 98% and 75% over high-resource.'
  scope: Standard deviation across the languages within each resource group, averaged over
    the 14 models; resource levels follow Joshi et al. (2019) as categorised by Singh et al.
    (2024), a three-way collapse of a five-class taxonomy that the authors note is imperfect
    and adopted for aggregation. Some of the low-resource spread is translation quality rather
    than model competence, which is exactly the paper's argument for needing human-translated
    or in-language evaluation data there -- without it, a low score cannot be attributed to
    the model.
  evidence: Section 4.2 (Evaluations Across High-, Mid-, and Low-Resource Languages), Figure
    10, Appendix A.1
- id: machine-translation-flatters-frontier-models
  text: On low-resource languages, GPT-4o and Claude 3.5 Sonnet score significantly better
    on machine-translated MMLU questions than on human-translated ones -- the paper's reading
    is that a machine-translated test set matches the machine-translated data these models
    were trained on -- while Aya Expanse 32B is the only model consistent across both.
  scope: Shown for the culturally sensitive subset in three example languages (French, Korean,
    Yoruba) in Figure 11, not across all 42, and read off a figure rather than a table. The
    training-data explanation is the authors' interpretation and is unverifiable for closed
    models. The direction reverses for high-resource languages, where models generally do
    better on human-translated data, and mid-resource languages sit in between with the gap
    narrowing for Claude 3.5 Sonnet and Qwen2.5 32B while Command R+ and Aya Expanse 32B still
    prefer human translation, which the paper attributes to their Korean support.
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
    at least three annotators and up to ten (96.4% by more than three) and labelled by majority
    vote.
  scope: Majority vote means a question counts as culturally sensitive when half or more of
    its annotators applied the tag -- a threshold, not a consensus. Krippendorff's alpha shows
    high agreement for most subjects, unanimity for Anatomy, and real disagreement for six,
    with Moral Scenarios and High School US History the worst. Annotators picked culture from
    a seven-option menu (Western, East Asian, Middle Eastern, South Asian, African, Latin
    American, Other) and region from a seven-option menu, so the taxonomy bounds what could
    be recorded. Annotation ran in 2-3 week sprints on Argilla with a shared Discord channel
    for calibration, and annotator proficiency was self-reported.
  evidence: Section 2.1, Section 2.2 (Inter-annotator agreement), Appendix C, Appendix C.1.1
- id: annotator-participation-was-uneven
  text: 'Community participation was heavily skewed across languages: a long tail of annotators
    contributed only one or two annotations, some languages are dominated by one or two frequent
    contributors, and the gap between the best- and worst-covered languages is large -- which
    the authors flag as unevenness in the dataset itself, not just in the effort.'
  scope: The authors' own limitation, and the reason the eleven community languages should
    not be treated as interchangeable with the four professionally post-edited ones or the
    ten from MMMLU. The inclusion bar was 50 human-translated samples per language, so a language
    can carry the 'community translated' label on very thin coverage. The annotation interface
    had no flag for toxic or offensive content and none was tracked, which the authors judge
    low-risk given MMLU's examination material but do not rule out.
  evidence: Section 7 (Uneven distribution of contributions, Toxic or offensive speech), Section
    3.2
- id: temporal-knowledge-is-rare
  text: Only 2.4% of annotated MMLU questions have answers that change over time, and no STEM
    question does; the time-sensitive ones sit in Social Sciences, Humanities, Medical and
    Other.
  scope: Same annotation pass and same 2,850-question sample as the cultural labels, with
    temporal sensitivity offered as a separate tag -- defined as a correct answer that may
    change with, for instance, who holds office or what an economic statistic is. Agreement
    on this tag was higher than on cultural sensitivity, with twelve subjects unanimous, and
    Moral Scenarios the notable disagreement. The finding bounds how fast MMLU goes stale
    from answer drift; it says nothing about contamination, which is the other way a static
    benchmark decays.
  evidence: Section 2.1, Section 2.2, Appendix A.4 and Figure 13, Appendix C.1.1 and Figure
    22
- id: human-edit-rates
  text: 'Human review changed a substantial share of Global-MMLU''s machine translations:
    annotators made 7,565 edits, 36.9% of the samples they reviewed, with professional annotators
    editing 789 samples per language on average (38.5%) and community annotators 362 (17.7%).'
  scope: Edit rate measures annotator time and resources, not translation quality per language
    -- the paper states explicitly that the professional/community gap cannot be read as a
    quality difference between their languages. An edit is any change made where the translation
    did not capture the original's intent; it is unweighted by size. Annotation ran on Argilla,
    with the original English and the machine translation shown side by side, so annotators
    were post-editing rather than translating from scratch.
  evidence: Section 3.1, Figure 8, Appendix D
- id: edit-effort-concentrates-in-humanities
  text: 'Where the machine translations needed the most repair was the Humanities: they carry
    the largest raw edit distances, larger for questions than for answers -- but once edit
    distance is normalised by text length, Humanities questions turn out to be simply the
    longest, and it is STEM answers that show the highest normalised edit distance.'
  scope: 'Levenshtein distance between each machine translation and its edited version, averaged
    within subject category, over the samples that were edited at all. Raw and normalised
    distances rank the categories differently, which is the point of reporting both: the raw
    ordering is partly a length artefact. This measures how much text moved, not whether the
    edit fixed a meaning error or a fluency one -- the interface asked only for acceptable-or-edit,
    with no error typology.'
  evidence: Appendix D.2, Figures 23 and 24, Appendix D and Figure 19
- id: google-translate-choice
  text: Global-MMLU's machine-translation baseline is Google Translate rather than an LLM,
    chosen deliberately so that no evaluated model would be scored on text produced by a model
    that might favour its own generations; it also scored higher ChrF++ than GPT-3.5-turbo
    across all subjects, with lower deviation across languages.
  scope: The self-preference concern is a validity argument backed by prior work on models
    preferring their own outputs, not a measured effect in this paper. The ChrF++ comparison
    uses MMMLU's human translations as the reference and only the languages common to both
    machine-translated sets, and it is against GPT-3.5-turbo specifically -- the system behind
    the widely used 26-language translated MMLU -- not against current frontier translation
    models; the paper notes that recent work already finds LLMs surpassing Google Translate
    on some high-resource languages.
  evidence: Section 3.1, Figure 7, Appendix D.1
- id: what-the-paper-asks-you-to-do
  text: The paper's two operational recommendations are to report Global-MMLU rather than
    a machine-translated MMLU, and to report the culturally sensitive and culturally agnostic
    subsets separately rather than as one aggregate number.
  scope: 'Recommendations, not results -- their force comes from the rank-change measurements
    rather than from any experiment on reporting practice. The second one is the load-bearing
    half: a single Global-MMLU number reintroduces exactly the mixing the labels exist to
    undo, and the argument for separating is strongest where the paper found the most instability,
    in lower-resourced languages and smaller models. Identifying culturally sensitive questions
    is also not the same as fixing the imbalance; the authors say so directly, and Global-MMLU
    still contains MMLU''s Western-centric question set.'
  evidence: Section 1 (recommendations), Section 6, Section 7 (Identifying cultural sensitivity
    does not guarantee cultural inclusion)
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
  - culture-and-region-tags-collapse-onto-the-us
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
  - largest-shifts-in-lower-resource-languages
  - model-size-and-sensitivity
  - cs-accuracy-higher-but-variance-higher
- q:
  - What is Global-MMLU?
  - How many languages does Global-MMLU cover?
  - What is the difference between Global-MMLU and translated MMLU?
  - Where can I get a multilingual version of MMLU?
  answers:
  - global-mmlu-dataset
  - translation-provenance-by-language
  - annotation-protocol
- q:
  - Which Global-MMLU languages are actually human-translated?
  - Is Global-MMLU human-translated or machine-translated?
  - How much of Global-MMLU did humans check?
  - Can I trust the Swahili or Polish split of Global-MMLU?
  answers:
  - translation-provenance-by-language
  - human-review-covered-a-slice
  - human-edit-rates
  - annotator-participation-was-uneven
- q:
  - How should I evaluate LLMs on low-resource languages?
  - Are machine-translated benchmarks reliable for low-resource languages?
  - Why do evaluation scores vary so much across low-resource languages?
  answers:
  - low-resource-variance
  - machine-translation-flatters-frontier-models
  - largest-shifts-in-lower-resource-languages
  - translation-provenance-by-language
- q:
  - Which MMLU subjects are culturally biased?
  - Is the STEM part of MMLU culturally neutral?
  - Which parts of MMLU can I use for cross-cultural comparison?
  answers:
  - cultural-bias-by-subject
  - mmlu-is-culturally-sensitive
  - labels-are-english-only
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
  - labels-are-english-only
  - mmlu-is-culturally-sensitive
- q:
  - Does the culturally-agnostic subset mean the questions are culturally neutral for everyone?
  - Were Global-MMLU's cultural labels made per language?
  - Do the CS/CA labels account for the target culture?
  answers:
  - labels-are-english-only
  - annotation-protocol
  - what-the-paper-asks-you-to-do
- q:
  - Does MMLU go out of date?
  - How many MMLU answers change over time?
  - Is MMLU time-sensitive?
  answers:
  - temporal-knowledge-is-rare
  - annotation-protocol
- q:
  - How should I report Global-MMLU results?
  - Should I report one Global-MMLU number or two?
  - What do the authors of Global-MMLU recommend?
  answers:
  - what-the-paper-asks-you-to-do
  - rankings-change
  - global-mmlu-dataset
- q:
  - How do you post-edit machine-translated benchmark data at scale?
  - What kind of translation errors did annotators fix in Global-MMLU?
  - Which subjects were hardest to translate?
  answers:
  - edit-effort-concentrates-in-humanities
  - human-edit-rates
  - human-review-covered-a-slice
  - google-translate-choice
- q:
  - Why use Google Translate instead of an LLM for building a benchmark?
  - Does translating a benchmark with an LLM bias the evaluation?
  - Is self-preference a problem when models translate their own test sets?
  answers:
  - google-translate-choice
  - machine-translation-flatters-frontier-models
misreadings:
- '''Culturally sensitive'' here does not mean offensive, ill-posed or in need of removal.
  It means answering the question correctly requires prior cultural, geographic or dialect-specific
  knowledge. The recommendation is to report the culturally sensitive and culturally agnostic
  subsets separately, not to delete either.'
- The percentages have different denominators and are easy to merge into a wrong number. 28%
  of MMLU requires culturally sensitive knowledge of any kind; 86.5% is the Western share
  of the culture-tagged questions; 84.9% is the North-America-plus-Europe share of the geography-tagged
  ones. It is not the case that 86.5% of MMLU is Western.
- 'The ''28% is Western'' version of that error is in the paper itself: the Section 1 contributions
  list says ''28% of questions require specific knowledge of Western cultures'', while Section
  2.2 -- where the number is actually measured -- says 28% require cultural, geographic or
  dialect knowledge of any kind. Cite Section 2.2.'
- Models are not worse on culturally sensitive questions -- average accuracy is higher there,
  because that subset skews to Social Sciences and Humanities while the agnostic one carries
  more STEM and Medical. What the cultural questions destabilise is consistency across languages
  and the ranking between models, not the score level.
- Global-MMLU is not a de-biased MMLU, and it is not fully human-translated. It keeps MMLU's
  questions and adds labels for which ones are culturally loaded; 16 of its 42 languages are
  machine translation with no human review, and the four professionally post-edited languages
  are Arabic, French, Hindi and Spanish.
- '''Human-verified'' does not mean every question was checked. Reviewers were shown a pool
  of roughly 2,050 questions per language -- about 15% of the 14,042-question test set --
  fully reviewed 37% of what they were given, and edited 12.3% of it. The 36.9% figure is
  the edited share of reviewed samples, not of the dataset.'
- A question labelled culturally agnostic is one that English-reading annotators judged to
  need no cultural, geographic or dialect knowledge. The labels were assigned once, in English,
  and copied to the other 41 languages, so they do not certify that a question reads naturally
  or fairly to a speaker of the target language.
- '''Human-translated test data gives more accurate scores'' is backwards for low-resource
  languages. GPT-4o and Claude 3.5 Sonnet scored significantly better on machine-translated
  data than on human-translated data there, most plausibly because machine-translated text
  resembles what they were trained on. A machine-translated test set can flatter a model rather
  than penalise it.'
- The rank-change figures are not accuracy differences. 5.7 rank changes on the culturally
  sensitive subset against 3.4 on the agnostic one describes leaderboard instability when
  the question subset changes; it says nothing about how far accuracy moved, and the sensitive
  subset is the smaller of the two (792 English questions against 2,058). Note also that the
  agnostic baseline is not zero, so the cultural effect is the difference between the two,
  not the second number alone.
- The professional-versus-community edit rates (38.5% against 17.7%) are not a quality comparison
  between the languages involved. The paper attributes the gap to differences in annotator
  time and resources and says explicitly that it cannot be read as translation quality.
- Rank instability is not simply worse in low-resource languages. High-resource languages
  show the highest average number of models changing rank on the culturally sensitive subset
  (6.8); what grows toward the low-resource end is the size of the moves (7.9 position shifts
  against 9.1 for high-resource, but from a much lower agnostic baseline), and the single
  largest extremes -- 5 positions on Malagasy, 13 models reshuffled on Ukrainian -- are in
  the lower-resourced groups.
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
    not of its quality or its subject matter -- and judged once in English for all 42 languages.
  MMLU Annotated (MA): The 2,850-question uniform sample the annotation was performed on --
    50 questions from each of MMLU's 57 subjects, 20% of the test set. It is also the reference
    point every reported rank change is measured against.
  Gold Set: 'The four languages whose machine translations were reviewed and post-edited by
    compensated professional annotators: Arabic, French, Hindi and Spanish. Distinct from
    the ten languages taken from OpenAI''s human-translated MMMLU and the eleven community-translated
    ones.'
  MMMLU: OpenAI's professionally human-translated MMLU in 14 languages, released with the
    o1 system card. Global-MMLU absorbs the ten of those languages that are not already in
    its Gold Set, and also uses MMMLU as the human reference when scoring machine translation
    quality.
  post-edit: A human correcting a machine translation shown next to the English original,
    rather than translating from scratch. Most of Global-MMLU's 'human' languages are post-edited
    over a sample, not human-translated end to end; the exceptions are the fourteen fully
    human-translated languages.
  rank changes / position changes: Reported as a pair throughout. Read the first as how many
    models changed rank between two subsets and the second as the total number of positions
    those models moved; the paper does not define them explicitly, so the pair matters more
    than either number alone.
  high-/mid-/low-resource: A three-way grouping of the 42 languages collapsed from the five
    classes of Joshi et al. (2019). The authors note it is imperfect and adopted for aggregation,
    and their own low-resource discussion cites Ukrainian, which their language table lists
    as mid-resource.
links_extra:
  the dataset: https://hf.co/datasets/CohereForAI/Global-MMLU
  the published version (cite this): https://aclanthology.org/2025.acl-long.919/
  preprint: https://arxiv.org/abs/2412.03304
  MMMLU, the human translations it builds on: https://hf.co/datasets/openai/MMMLU
  ? 'Global-MMLU-Lite: 23 languages, 400 test + 215 dev items each, same CS/CA labels (companion
    release, not described in the paper)'
  : https://huggingface.co/datasets/CohereForAI/Global-MMLU-Lite
---
