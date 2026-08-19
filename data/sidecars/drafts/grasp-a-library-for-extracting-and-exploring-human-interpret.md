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

Then promote it:  python scripts/draft_sidecars.py --accept grasp-a-library-for-extracting-and-exploring-human-interpret

Stamp: spec=8f05813a4658 checks=pass body=29c2501c81e5
-->
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
- q:
  - What tools exist for exploring a text dataset beyond word clouds and n-gram counts?
  - Where should I start reading about learning interpretable patterns from text?
  - Is there a library that extracts human-readable linguistic patterns from labelled text?
  answers:
  - exploration-tool-context
  - first-public-impl
- q:
  - Does removing dataset artifacts actually improve out-of-distribution accuracy?
  - How much does filtering artifact-matching training examples help generalization on 20Newsgroups?
  - What was the out-of-distribution gain from GrASP-based artifact removal?
  answers:
  - artifact-filtering-ood
  - artifact-filtering-indomain
- q:
  - Does deleting artifact-matched training examples hurt in-domain accuracy?
  - What is the in-domain cost of filtering a training set with GrASP patterns?
  answers:
  - artifact-filtering-indomain
- q:
  - How much human effort does it take to label patterns as dataset artifacts?
  - How many GrASP patterns did an annotator flag as artifacts in 20Newsgroups?
  answers:
  - human-annotation-throughput
- q:
  - Can pattern mining find annotation artifacts in SNLI?
  - What artifacts does GrASP find in SNLI hypotheses, and with what precision?
  - Do hypothesis-only artifacts in natural language inference show up as linguistic patterns?
  answers:
  - snli-artifact-precision
- q:
  - Can pattern extraction tell me which inputs a machine translation model handles well?
  - How were easy and hard MT inputs characterized with GrASP on WMT19 English-German?
  - Are hard-to-translate sentences harder to characterize with patterns than easy ones?
  answers:
  - mt-quality-patterns
  - mt-known-hurdles
- q:
  - Does GrASP rediscover things experts already know about argumentative text?
  - What did pattern mining reveal on the topic-dependent argument mining corpus?
  - Which single feature was most indicative of evidence sentences in argument mining?
  answers:
  - argument-mining-rediscovery
- q:
  - What does a GrASP pattern actually look like?
  - How can one pattern match spam messages that share no words?
  - What is an example of an attribute-sequence pattern for SMS spam?
  answers:
  - pattern-generalization
- q:
  - How are extracted linguistic patterns made readable for non-experts?
  - Can attribute patterns be translated into plain English?
  answers:
  - pattern2text
- q:
  - How do I add my own domain-specific attributes to GrASP pattern extraction?
  - What does the GrASP library add over the original 2017 algorithm?
  - Can I change the criterion used to rank extracted patterns?
  answers:
  - custom-attributes-extensions
- q:
  - What does the GrASP web interface show?
  - Can I browse extracted patterns and their matches in a dataset visually?
  - Can the web viewer display patterns from a different pattern-extraction algorithm?
  answers:
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
