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
- ask:
    plain: is there a language identification test set made of real web pages and labelled
      by people who speak the languages?
    jargon: does an openly licensed, human-annotated LID evaluation corpus exist for the web
      domain, including long-tail varieties?
    task: where do I get evaluation data to test a language identifier on messy crawled web
      text rather than clean sentences?
    practitioner: I need to benchmark my language detector on low-resource web text with a
      permissive license, is there a dataset I can just download?
  answered_by:
  - web-lid-benchmark
  - dataset-size
- ask:
    plain: how many languages are covered by the new human-annotated benchmark for detecting
      which language a web page is written in?
    jargon: what is the size, mean line length and language-variety coverage of the CommonLID
      annotated Common Crawl sample?
    task: how many languages can I actually evaluate on if I use the CommonLID web benchmark,
      and how many have enough lines to be meaningful?
    practitioner: is CommonLID big enough per language for me to trust a per-language F1 I
      compute on it?
  answered_by:
  - dataset-size
- ask:
    plain: do language detectors get much worse on raw web pages than on clean translated
      sentences?
    jargon: how large is the macro-F1 gap for LID systems between web-domain lines and FLORES+,
      and how much of the older numbers reflect train-test overlap?
    task: how should I adjust my expectations of a language identifier's reported accuracy
      before running it over a web crawl?
    practitioner: can I trust the accuracy figure published for a language identifier when
      I plan to run it on Common Crawl?
  answered_by:
  - harder-than-clean-sets
  - overestimation
- ask:
    plain: when several language detectors are compared on the languages they all support,
      which one comes out ahead?
    jargon: on the shared label intersection, how do GlotLID, CLD2, CLD3 and OpenLID-v2 rank
      on F1 and false positive rate, and does any system clear 75% macro-F1?
    task: which off-the-shelf language identifier should I pick for a multilingual crawl if
      I care about false positives?
    practitioner: is GlotLID good enough for my pipeline, or is one of the older detectors
      still competitive on the languages I need?
  answered_by:
  - glotlid-best-shared-languages
  - no-model-above-75
- ask:
    plain: can a general-purpose chatbot tell you what language a piece of text is in as well
      as a purpose-built detector?
    jargon: how do zero-shot GPT-4o and GPT-5 variants compare with GlotLID on LID F1 across
      core and African language subsets?
    task: should I prompt an LLM to label the language of my documents, or run a dedicated
      classifier over them?
    practitioner: I already pay for GPT-5 API calls, is it worth using them for language identification
      on African languages?
  answered_by:
  - llms-lose
- ask:
    plain: how much throughput do you give up to get a more accurate language detector?
    jargon: which LID systems lie on the speed-accuracy Pareto frontier, and what are their
      samples-per-second rates?
    task: which language identifier can I afford to run over billions of web lines without
      the labelling step dominating my compute?
    practitioner: my crawl is huge, should I take the fast detector or pay the slowdown for
      the more accurate one?
  answered_by:
  - speed-tradeoff
- ask:
    plain: is telling what language a text is written in basically a solved problem?
    jargon: do any current LID systems reach high macro-F1 across all six evaluation sets,
      and can systems be ranked by a single aggregate score at all?
    task: how do I decide whether language identification is still a research problem worth
      working on for my languages?
    practitioner: can I just plug in an existing language detector and stop worrying about
      it?
  answered_by:
  - no-model-above-75
  - coverage-comparison-problem
- ask:
    plain: why is it unfair to compare two language detectors that recognise different lists
      of languages?
    jargon: how should LID systems with mismatched label sets be scored, given that whole-test-set
      macro-F1 rewards coverage and covered-language scoring rewards specialisation?
    task: how do I build a fair comparison table for language identifiers that each support
      a different number of languages?
    practitioner: should I prefer a language detector that claims 2000 languages over one
      that claims 100?
  answered_by:
  - coverage-comparison-problem
- ask:
    plain: how often do people who speak a language disagree about what language a line of
      web text is in?
    jargon: what is the inter-annotator disagreement rate on multiply-annotated CommonLID
      lines, and which macro/micro-language pairs drive it?
    task: how much label noise should I expect when I have native speakers annotate crawled
      lines for language?
    practitioner: if my annotators disagree on a few percent of lines, is that normal for
      web language labelling?
  answered_by:
  - annotator-disagreement
- ask:
    plain: what goes wrong when you build a language benchmark by filtering crawled pages
      with existing detectors first?
    jargon: how does pre-selecting candidate lines with fastText, OpenLID, GlotLID and MADLAD-400
      bias CommonLID's language and register coverage?
    task: how do I sample web text for language annotation without inheriting the blind spots
      of the detectors I used to find it?
    practitioner: should I worry that a benchmark's own results are flattering the detectors
      that were used to collect it?
  answered_by:
  - selection-bias-limit
- ask:
    plain: why do language detectors score so well on religious texts and human-rights declarations?
    jargon: to what extent do high macro-F1 scores on UDHR and Bible evaluation sets reflect
      overlap with LID training corpora?
    task: how do I tell whether a language identifier's long-tail scores come from genuine
      generalisation or from having trained on the same test text?
    practitioner: can I use a detector's Bible-based scores to predict how it will do on my
      own long-tail language data?
  answered_by:
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
