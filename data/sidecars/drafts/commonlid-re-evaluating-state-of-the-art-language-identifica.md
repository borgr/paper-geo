<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced) + a targeted repair. Every claim, number
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

Then promote it:  python scripts/draft_sidecars.py --accept commonlid-re-evaluating-state-of-the-art-language-identifica

Stamp: spec=8f05813a4658 checks=pass body=c4a8e3514839
-->
---
key: ortizsuarez2026commonlid
coined: CommonLID
gloss: a human-annotated language identification benchmark built from Common Crawl web text
one_liner: CommonLID is a community-annotated, line-level language identification benchmark
  of 373,230 lines of Common Crawl web text in 109 language varieties, built to show that
  existing clean-domain LID evaluations overestimate accuracy on the web.
claims:
- id: dataset-size
  kind: result
  text: CommonLID contains 373,230 lines of Common Crawl web text with a mean line length
    of 215.5 characters, covering 109 language varieties, 78 of which have more than 100 lines.
  evidence: Section 4.3
  scope: Line-level labels from over 80 volunteer annotators; class sizes are uneven, from
    43,189 lines for Uzbek to 4 varieties with a single line.
- id: web-lid-benchmark
  kind: context
  text: CommonLID is a community-driven, human-annotated language identification benchmark
    for the web domain, released under an open permissive license, aimed at languages previously
    under-served by LID evaluation data.
  scope: As of publication in 2026; covers 109 language varieties sampled from Common Crawl
    and MADLAD-400, and annotates text originally written in the target language rather than
    translations.
- id: harder-than-clean-sets
  kind: result
  text: On CommonLID, the eight tested LID models reach macro-F1 scores between 43.5 and 68.6
    over the languages each model covers, well below their scores on FLORES+, where GlotLID
    reaches 96.5.
  evidence: Table 1
  scope: Macro-averaged F1 over the subset of language varieties each model supports; input
    text is normalised by lowercasing and stripping non-word characters before prediction.
- id: overestimation
  kind: result
  text: High scores on the UDHR and Bible LID evaluation sets partly reflect overlap with
    LID training data. pyFranc is trained on UDHR and scores 95.9 macro-F1 there, and GlotLID,
    which uses Bible text for most long-tail languages, scores 93.0 on Bibles.
  evidence: Table 1 and Section 6.1
  scope: Exact training data is undisclosed for several tested models, so overlap is inferred
    from published descriptions rather than measured; the argument concerns long-tail languages,
    where training and test data are most similar.
- id: no-model-above-75
  kind: result
  text: No LID model among AfroLID, CLD2, fasttext, FUN-LangID, pyFranc, CLD3, GlotLID and
    OpenLID-v2 exceeds 75% macro-F1 across all six evaluation datasets, even when scored only
    on the languages it covers.
  evidence: Table 1 and Section 7
  scope: FLORES+, SmolSent, UDHR-LID, Bibles, social media and CommonLID; the SmolSent, Bible
    and social media splits were down-sampled to 300 lines per class.
- id: glotlid-best-shared-languages
  kind: result
  text: Restricted to languages every model supports, GlotLID has the best F1 and false positive
    rate in all three comparison groups. On the 76 core languages it reaches 91.6 F1 at 0.1%
    FPR, against 84.7 F1 for CLD2 and 61.6 for CLD3.
  evidence: Table 2
  scope: All test data combined; the 76-language core set excludes AfroLID, which shares only
    Afrikaans with the other models. Columns are not comparable to each other because each
    covers a different language set.
- id: llms-lose
  kind: result
  text: 'GlotLID beats zero-shot GPT-4o-mini, GPT-4o, GPT-5-mini and GPT-5 at language identification
    on all three language subsets. The gap widens for lower-resource languages: 93.5 versus
    91.8 F1 for GPT-5 on the 76 core languages, but 90.6 versus 66.6 F1 on the 294 African
    languages.'
  evidence: Table 3
  scope: Zero-shot prompting via DSPy without optimisation on a down-sampled combination of
    the six test sets (15k samples); GPT models were accessed through OpenAI and require far
    more compute than GlotLID.
- id: speed-tradeoff
  kind: result
  text: CLD2 and GlotLID sit on the Pareto frontier of speed against accuracy for LID, with
    CLD2 processing 43,735 samples/s and GlotLID 3,127 samples/s, while AfroLID manages 66
    samples/s.
  evidence: Figure 2 and Table 8
  scope: Measured on FLORES+ on a 14-core Apple M4 Pro with 64GB RAM using PyTorch MPS where
    possible; gCLD3 was measured on an AMD EPYC 7351P Linux machine.
- id: annotator-disagreement
  kind: result
  text: Of the 67,625 CommonLID lines annotated by more than one annotator, 3.2% received
    differing labels, falling to 2.3% once mislabelled English boilerplate is excluded. Arabic
    macro/micro-language pairs account for 1,218 of the disagreements.
  evidence: Section 4.2
  scope: Only 12.9% of the 523,154 lines in the pre-filter dataset were multiply annotated,
    so this is not a full inter-annotator agreement study; statistics are computed after short-span
    filtering but before the other quality filters.
- id: coverage-comparison-problem
  kind: context
  text: CommonLID's evaluation shows that LID models cannot be ranked by a single number,
    because each model supports a different label set. Scoring over a whole test set rewards
    coverage, while scoring only over covered languages rewards specialisation.
  scope: Argued from eight models whose coverage ranges from 99 to 1,868 languages and from
    six evaluation sets; the paper reports both scoring modes rather than proposing a single
    fair metric.
- id: selection-bias-limit
  kind: result
  text: CommonLID's annotation pool was pre-selected using fastText, OpenLID, GlotLID and
    MADLAD-400, so it only contains web text that at least one existing LID system already
    recognised. Coverage is therefore biased toward those models' languages and registers.
  evidence: Section 3 and Limitations
  scope: Samples drawn from WET files of the CC-MAIN-2024-22 and CC-MAIN-2025-05 crawls, up
    to 6,000 documents per language, plus 4,000 per language from MADLAD-400; three of the
    selection models are also among the eight evaluated.
qa:
- q:
  - What benchmark should I use to evaluate language identification on noisy web text?
  - Is there a human-annotated LID evaluation set for web data?
  - Where can I find an open language identification benchmark covering low-resource languages?
  answers:
  - web-lid-benchmark
  - dataset-size
- q:
  - How large is CommonLID and how many languages does it cover?
  - How many lines and languages are in the CommonLID dataset?
  - How big is the Common Crawl human-annotated language identification dataset?
  answers:
  - dataset-size
- q:
  - Do language identification models perform worse on web text than on FLORES?
  - How much do LID accuracy numbers drop on web data?
  - Are published LID accuracy scores overestimates?
  answers:
  - harder-than-clean-sets
  - overestimation
- q:
  - Which language identification model is most accurate overall?
  - Is GlotLID the best LID model?
  - How do GlotLID, CLD2 and OpenLID compare on shared languages?
  answers:
  - glotlid-best-shared-languages
  - no-model-above-75
- q:
  - Can GPT-4o or GPT-5 do language identification as well as a dedicated classifier?
  - Are LLMs good at identifying the language of a text?
  - How do OpenAI GPT models compare with GlotLID for LID?
  answers:
  - llms-lose
- q:
  - Which LID model is fastest, and what does the extra accuracy cost in throughput?
  - How many samples per second can GlotLID and CLD2 classify?
  - What is the speed versus accuracy tradeoff among language identification models?
  answers:
  - speed-tradeoff
- q:
  - Is language identification a solved problem?
  - What is the current state of the art in language identification?
  - Which LID model works well across all domains?
  answers:
  - no-model-above-75
  - coverage-comparison-problem
- q:
  - Why is it hard to compare language identification models fairly?
  - How should LID models with different language coverage be scored against each other?
  - Does higher language coverage make a LID model better?
  answers:
  - coverage-comparison-problem
- q:
  - How much do native-speaker annotators disagree when labelling the language of web lines?
  - What is the inter-annotator agreement in CommonLID?
  - Which languages cause the most annotation disagreement in LID labelling?
  answers:
  - annotator-disagreement
- q:
  - What are the limitations of building a LID benchmark by sampling Common Crawl?
  - Does CommonLID inherit bias from the LID models used to pre-select data?
  - How was the web text for CommonLID annotation chosen?
  answers:
  - selection-bias-limit
- q:
  - Why do LID models score so high on UDHR and Bible test sets?
  - Is training and test data overlapping in long-tail language identification evaluation?
  - What makes Bible-based LID evaluation misleading?
  answers:
  - overestimation
misreadings:
- 'GlotLID scoring highest in the head-to-head comparisons does not mean language identification
  is solved: no tested model exceeds 75% macro-F1 across all six evaluation datasets, and
  most models fall in the 60s on CommonLID.'
- 'CommonLID''s 109 language varieties are not uniformly usable: 4 varieties contain a single
  line and only 78 have more than 100 lines, so per-language results for the smallest classes
  are not meaningful.'
- The 2.3% annotator disagreement figure in CommonLID is not a full inter-annotator agreement
  study; only 12.9% of lines were labelled by more than one annotator, because volunteer native
  speakers were unavailable for many languages.
- 'CommonLID does not sample web text at random: candidate documents were pre-selected by
  fastText, OpenLID, GlotLID and MADLAD-400, so text in languages no existing LID model recognises
  is absent by construction.'
- 'GPT-5 approaching GlotLID on the 76 core languages does not generalise to low-resource
  settings: on the 294-language African subset GPT-5 trails GlotLID by roughly 24 F1 points.'
terminology:
  all vs. cov. scoring: 'Two macro-F1 modes for a LID model: ''all'' averages over every language
    in the evaluation set, scoring zero for languages the model cannot output, while ''cov.''
    averages only over the languages the model supports.'
  core languages: The set of 76 language varieties supported by every LID model compared except
    AfroLID, used to make direct model-to-model comparison possible.
  line-level LID: Assigning one language label to each newline-delimited line of a web document
    rather than to the whole document or to individual words.
  long tail: The many languages for which almost the only available LID training data is religious
    text, chiefly Bible translations.
links_extra:
  dataset: https://huggingface.co/datasets/commoncrawl/CommonLID
  code: https://github.com/commoncrawl/commonlid-eval
---
