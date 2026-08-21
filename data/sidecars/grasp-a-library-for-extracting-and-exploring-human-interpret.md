---
key: lertvittayakumjorn2022grasp
coined: GrASP library
gloss: an open-source Python tool that learns human-readable text patterns (sequences of linguistic
  attributes) separating two sets of texts, plus a web viewer for them
one_liner: GrASP is an open-source Python library and web exploration tool that learns human-interpretable
  textual patterns — sequences of conjoined linguistic attributes such as part-of-speech,
  hypernym and sentiment tags — distinguishing a positive from a negative set of texts.
claims:
- id: first-public-impl
  kind: context
  text: The GrASP library is the first publicly released implementation of the GrASP pattern-extraction
    algorithm, which was proposed by Shnarch et al. in 2017 without a public implementation.
  scope: As of the 2022 LREC publication, and about implementations of that specific algorithm;
    the authors report finding no public tools for other pattern-learning algorithms either.
- id: exploration-tool-context
  kind: context
  text: GrASP fills a gap in textual data exploration tooling, where most tools for text analyze
    data only at the word or n-gram level. GrASP instead learns and displays recurring generalizable
    patterns that match tokens by linguistic attributes rather than surface form.
  scope: Positioning as of 2022, per the authors' survey of exploration tools, pattern-based
    search engines (which require an expert to write the patterns) and rule-based extraction
    systems; built-in attributes are English-only.
- id: artifact-filtering-ood
  text: Removing 20Newsgroups training examples matched by GrASP-flagged artifact patterns
    raised out-of-distribution accuracy on the Religion test set from 0.674 to 0.725. Macro
    F1 rose from 0.682 to 0.739, versus a size-matched sample of the original data.
  kind: result
  evidence: Table 2
  scope: Christianity vs. Atheism+Religion(misc) with a 1D CNN over 300-dimensional GloVe
    embeddings, average of 5 runs with SD up to 0.06. The larger class was downsampled and
    patterns kept at precision ≥75% before a human flagged artifacts.
- id: artifact-filtering-indomain
  text: Filtering out examples matched by GrASP artifact patterns left in-domain 20Newsgroups
    performance essentially unchanged, at 0.800 accuracy and 0.804 macro F1 versus 0.810 and
    0.818 for the size-matched unfiltered sample.
  kind: result
  evidence: Table 2
  scope: Christianity vs. Atheism+Religion(misc) with a 1D CNN and GloVe embeddings, average
    of 5 repetitions with SD 0.01–0.03; the in-domain gap is within one SD.
- id: human-annotation-throughput
  text: In the 20Newsgroups artifact use case, GrASP produced 133 patterns at precision ≥75%.
    A human annotator using the web exploration tool flagged 40 of the 133 as semantically
    irrelevant to the task and therefore likely artifacts.
  kind: result
  evidence: Section 6
  scope: One annotator, Christianity vs. Atheism+Religion(misc), after downsampling the majority
    class; no inter-annotator agreement or annotation-time measurement is reported.
- id: snli-artifact-precision
  text: Applied to 10K SNLI entailment and 10K contradiction hypotheses, GrASP recovered known
    annotation artifacts with added structure. Examples include an entailment pattern of noun
    + 'be' + a hypernym of 'outside' at 97% precision, and negative-sentiment verbs correlating
    with contradiction at 75.7% precision.
  kind: result
  evidence: Section 6
  scope: Hypothesis-only subsets of SNLI entailment vs. contradiction, 200 patterns and alphabet
    size 200, information gain as selection criterion, patterns kept only at precision ≥75%;
    precisions are on the training subset, not a held-out split.
- id: mt-quality-patterns
  text: Using the top and bottom 25% of WMT19 English-German quality-estimation sentences
    as positive and negative sets, GrASP found 60 patterns with precision ≥80% for easy-to-translate
    inputs. Only 16 patterns above 60% precision were found for hard inputs, indicating challenging
    inputs are more diverse.
  kind: result
  evidence: Section 5
  scope: 13K automatically translated sentences from one MT model judged by human quality
    scores, default GrASP hyperparameters, 100 patterns output; recall of the high-precision
    positive patterns ranges from 5% to 35%, and the data mixes Reviews and IT domains.
- id: mt-known-hurdles
  text: GrASP patterns over WMT19 English-German quality-estimation data independently surfaced
    translation difficulties already documented in the literature. GrASP dedicated a pattern
    to the lemma 'be' and found an adjective-noun-noun pattern capturing structural ambiguity
    such as 'new blog entry'.
  kind: result
  evidence: Section 5
  scope: Qualitative agreement with prior MT analysis for a single MT model on WMT19 en-de
    quality-estimation data; the patterns were selected by the authors as illustrative, with
    no systematic recall over the set of known hurdles.
- id: argument-mining-rediscovery
  text: On the topic-dependent argument mining corpus of 4,065 training and 1,720 test topic-sentence
    pairs, GrASP's most indicative pattern was the word 'that' in its preposition sense. That
    matches the known expert indicator of argumentative content.
  kind: result
  evidence: Section 4
  scope: Information gain as selection criterion, 100 patterns, up to 2 gaps allowed, built-in
    attributes plus a custom binary attribute for lexicon membership of argumentative words;
    no downstream classification accuracy is reported.
- id: pattern-generalization
  text: A single GrASP pattern groups 3 SMS spam messages that share almost no words, such
    as "awarded a SiPix Digital Camera" and "WIN a FREE Bluetooth Headset". That pattern is
    a positive-sentiment word followed closely by a determiner and then a proper noun.
  kind: result
  evidence: Table 1
  scope: Illustrative examples from the SMS spam dataset used throughout the paper; no coverage
    or precision figure is measured for this pattern.
- id: pattern2text
  text: The GrASP library translates each extracted pattern into an English sentence via templates,
    so readers without linguistic training can interpret patterns. It renders [[HYPERNYM:communication.n.02],
    [POS:NUM]] as "A type of communication (n), closely followed by a number".
  kind: result
  evidence: Section 2
  scope: Template-based translation of the built-in English attributes; custom attributes
    require the user to implement their own explanation function, and no user study of comprehension
    is reported.
- id: custom-attributes-extensions
  text: The GrASP library extends the original 2017 algorithm with user-pluggable pattern-selection
    criteria and domain-specific custom attributes added by implementing 2 functions. It also
    adds a limit on gaps between matched tokens that overrides the window size, and a minimum-coverage
    threshold.
  kind: result
  evidence: Section 2
  scope: The released library's API and hyperparameters; the original algorithm ranked patterns
    by information gain only, and no experiment isolates the benefit of each added parameter.
- id: four-report-views
  text: The GrASP web tool renders 4 linked report views, 2 pattern-centric and 2 example-centric.
    The pattern-centric views give a sortable table of all patterns with coverage, precision,
    recall and F1 plus the examples each pattern matches, while the example-centric views
    highlight matched words per example.
  kind: result
  evidence: Figures 1-4
  scope: Flask-based tool consuming the JSON exported by the GrASP library; it can also display
    output from other pattern-extraction algorithms if formatted into the required JSON schema.
qa:
- ask:
    plain: is there software that finds recurring word patterns in a labelled text dataset,
      beyond counting words?
    jargon: which open-source library extracts human-readable linguistic attribute patterns
      from labelled text corpora?
    task: how do I explore a labelled text collection at the pattern level instead of by word
      frequency?
    practitioner: I want to inspect what distinguishes my positive and negative examples —
      is there a ready-made pattern-mining tool I can install?
  answered_by:
  - exploration-tool-context
  - first-public-impl
- ask:
    plain: if you delete training examples that contain misleading shortcut phrases, does
      the model do better on data from elsewhere?
    jargon: does filtering artifact-matching training instances improve out-of-distribution
      accuracy and macro F1 on a 20Newsgroups-to-Religion transfer?
    task: how do I use pattern-flagged spurious cues to clean a training set for better generalization?
    practitioner: should I drop artifact-matched examples from my training data if I care
      about performance on a different distribution?
  answered_by:
  - artifact-filtering-ood
  - artifact-filtering-indomain
- ask:
    plain: does throwing away training examples with shortcut phrases cost accuracy on the
      original test set?
    jargon: what is the in-domain accuracy and macro F1 penalty from artifact-pattern-based
      training set filtering on 20Newsgroups?
    practitioner: if I remove artifact-matched examples, am I trading away in-domain accuracy
      to get it?
  answered_by:
  - artifact-filtering-indomain
- ask:
    plain: how much reading does a person have to do to decide which extracted phrase patterns
      are misleading shortcuts?
    jargon: how many candidate high-precision patterns does an annotator have to review to
      identify dataset artifacts in a 20Newsgroups topic task?
    task: how do I get a human to sort mined patterns into meaningful signal versus dataset
      artifact?
    practitioner: how many patterns should I budget for an annotator to label as artifacts
      before I start filtering?
  answered_by:
  - human-annotation-throughput
- ask:
    plain: do the giveaway phrases people found in the Stanford natural language inference
      data show up as automatically mined patterns?
    jargon: can pattern mining over SNLI entailment and contradiction hypotheses recover known
      hypothesis-only annotation artifacts, and at what precision?
    task: how do I check whether my crowdsourced inference hypotheses contain label-revealing
      cues?
    practitioner: would running pattern extraction on SNLI hypotheses tell me anything the
      artifact papers did not already report?
  answered_by:
  - snli-artifact-precision
- ask:
    plain: can you describe what makes a sentence easy or hard to translate using recurring
      patterns?
    jargon: what does pattern extraction over the top and bottom quartiles of WMT19 English-German
      quality-estimation data reveal about easy versus hard source inputs?
    task: how do I characterize which source sentences my translation system will struggle
      with?
    practitioner: if I mine patterns from quality-estimation scores, will I get a usable profile
      of hard-to-translate input or only of easy input?
  answered_by:
  - mt-quality-patterns
  - mt-known-hurdles
- ask:
    plain: does automatic pattern mining find the same cues in argumentative sentences that
      experts already knew about?
    jargon: on a topic-dependent argument mining corpus, which extracted pattern is most indicative
      of argumentative sentences?
    task: how do I check that a pattern-extraction run on argument mining data agrees with
      known expert indicators?
    practitioner: can I trust mined patterns as a sanity check by seeing whether they rediscover
      established argument indicators?
  answered_by:
  - argument-mining-rediscovery
- ask:
    plain: how can a single rule match two spam texts that have almost no words in common?
    jargon: what does an attribute-sequence pattern over sentiment, part-of-speech and gap
      constraints look like on an SMS spam corpus?
    task: how do I write or find a pattern that generalizes across differently-worded spam
      messages?
    practitioner: will mined patterns actually group paraphrased spam together, or just cluster
      shared keywords?
  answered_by:
  - pattern-generalization
- ask:
    plain: if a tool outputs patterns full of linguistic tags, how does a non-linguist read
      them?
    jargon: how are extracted attribute patterns with hypernym and POS constraints converted
      into natural-language descriptions?
    task: how do I present mined linguistic patterns to annotators or domain experts who do
      not know POS tags?
    practitioner: can I hand pattern-mining output to teammates without linguistics training
      and expect them to interpret it?
  answered_by:
  - pattern2text
- ask:
    plain: what extra features does the released pattern-mining library have compared with
      the algorithm first described in 2017?
    jargon: which extensions does the GrASP library add to the 2017 algorithm — custom attributes,
      selection criteria, gap limits, coverage thresholds?
    task: how do I plug in my own domain attributes or change how mined patterns are ranked?
    practitioner: can I adapt the library's pattern-selection criterion to my own dataset
      instead of using the default?
  answered_by:
  - custom-attributes-extensions
- ask:
    plain: what does the browser-based viewer for mined text patterns actually display?
    jargon: what report views does the GrASP web interface render, and how do pattern-centric
      and example-centric views differ?
    task: how do I browse mined patterns alongside the examples they match and the words they
      highlight?
    practitioner: if I have patterns and matched examples from my own extractor, can I use
      the web viewer to inspect them?
  answered_by:
  - four-report-views
misreadings:
- 'GrASP is not a new pattern-learning algorithm: the algorithm dates from Shnarch et al.
  2017, and the LREC 2022 contribution is the first public implementation, its extensions
  and a web exploration tool.'
- The 20Newsgroups filtering experiment shows that GrASP helps a human find artifacts, not
  that automatic pattern-based deletion is the best debiasing method; the authors chose to
  delete all matched examples for simplicity.
- 'GrASP patterns are not regular expressions over surface strings: tokens are matched by
  conjunctions of linguistic attributes such as part-of-speech, hypernym, dependency and sentiment
  tags, which is what lets one pattern cover very different word sequences.'
- The out-of-distribution improvement on the Religion test set is an average of 5 runs with
  standard deviations up to 0.06, so it should not be read as a tight or guaranteed 5-point
  gain.
- GrASP requires two labelled sets of texts, a positive and a negative one; the unsupervised
  single-list setting of GrASP lite is listed as future work, not implemented in the released
  library.
- The built-in attributes are English-specific even though the algorithm and viewer are language-agnostic;
  applying GrASP to another language requires the user to write custom attributes.
terminology:
  GrASP pattern: A sequence of slots, each a conjunction of linguistic attributes (e.g. [[SENTIMENT:pos],
    [POS:det], [POS:propn]]), matching tokens that appear in that order within a window and
    optionally with a bounded number of gaps between them.
  Alphabet (in GrASP): The set of token-level attributes retained after scoring, from which
    multi-slot patterns are greedily composed; its size is a hyperparameter of the GrASP library.
  Pattern-centric report: 'A view of extracted patterns organised by pattern: level 1 lists
    every pattern with its coverage, metric score, precision, recall and F1, and level 2 lists
    the positive and negative training examples one pattern matches.'
  Example-centric report: 'A view of extracted patterns organised by training example: level
    1 lists all examples with words matched by positive, negative or both kinds of patterns
    highlighted, and level 2 lists all patterns matching one example.'
  Dataset artifact: A token or phrase that is irrelevant to a classification task but frequently
    appears in examples of some classes, letting a trained model exploit a spurious correlation
    that does not generalise out of distribution.
  Custom attribute: A user-defined token annotation added to GrASP by subclassing CustomAttribute
    and implementing 2 functions, one extracting the attribute from an input text and one
    producing its natural-language explanation.
links_extra:
  code: https://github.com/plkumjorn/GrASP
  demo: https://plkumjorn.github.io/GrASP
---
