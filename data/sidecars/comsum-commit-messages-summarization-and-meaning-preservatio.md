---
key: choshen2021comsum
coined: ComSum
gloss: a summarization dataset built from Git commit messages and their one-line subjects
one_liner: ComSum turns 7.5 million Git commits into a text summarization dataset by pairing
  each commit message with its one-line subject, and adds a meaning-preservation evaluation
  based on the corrective/adaptive/refactor commit taxonomy instead of Rouge alone.
claims:
- id: dataset-size
  kind: result
  text: ComSum contains 7,540,026 commit-message/subject pairs drawn from 19,720 GitHub projects
    and 317,423 authors. The average message has 494 characters, the average subject 53, an
    average compression ratio of 11.08.
  scope: Commits pushed to GitHub before 2021 and indexed in the BigQuery GitHub schema; projects
    required at least 50 commits during 2020, and each message must be at least 100 characters
    longer than its subject.
  evidence: Section 4
- id: abstractiveness
  kind: result
  text: ComSum is the most abstractive of the summarization datasets it is compared with,
    at a coverage of 0.27 and a density of 0.89. XSum scores 0.66 and 1.09, and BOOKSUM Paragraph
    0.5 and 0.92.
  scope: Coverage and density as defined by Grusky et al. (2018); comparison set is Arxiv/PubMed,
    BigPatent, CNN/DM, Newsroom, XSum and BOOKSUM Paragraph.
  evidence: Table 1
- id: vocabulary
  kind: result
  text: ComSum commit messages have a vocabulary of over 2M types in the validation set alone
    and 19M overall, against the 1.4M reported for the NYTimes dataset. The summary vocabulary
    is 0.5M and 3.9M against NYTimes' 0.3M.
  scope: Validation-set figures are size-matched for fairness against news datasets; vocabulary
    counted as unfiltered surface types, which in the commit domain includes identifiers,
    version numbers and hashes.
  evidence: Section 2
- id: bart-baseline
  kind: result
  text: Fine-tuned BART reaches RougeL 27.2 on the ComSum test set against 14.9 for zero-shot
    BART. The gain suggests the dataset is large enough to partly overcome the domain shift
    from BART's Wikipedia and Books pretraining.
  scope: BART fine-tuned with max source length 512, target length 128, learning rate 1e-4,
    batch size 256, trained for 1 week on 4 Nvidia M60 GPUs; heuristic baselines computed
    on 10k samples.
  evidence: Table 2
- id: still-challenging
  kind: result
  text: 'ComSum is harder for BART than news summarization benchmarks are: BART reaches RougeL
    44.2 on CNN/Daily Mail and 27.2 on XSum. On ComSum it reaches 33.2 on the train set and
    27.2 on the test set.'
  scope: Single BART configuration, no error bars because training was repeated only once;
    CNN/DM and XSum figures are the ones reported by Lewis et al. (2020) rather than re-run.
  evidence: Table 2
- id: copying-insufficient
  kind: result
  text: Copying the commit message instead of summarizing it scores only RougeL 12.0 on ComSum,
    and picking a random sentence from the message scores 13.6. Extraction from the input
    is far from a good commit summary.
  scope: Heuristic baselines on 10k training-set samples; the Subject-and-Message upper reference
    reaches 29.5 RougeL but is not usable for prediction because it includes the gold summary.
  evidence: Table 2
- id: related-commit
  kind: result
  text: A subject borrowed from a related commit by the same author in the same project within
    a week scores RougeL 14.6 on ComSum, rising to 15.5 when both commits are bug fixes. Topic
    and author style are therefore not substitutes for the summary.
  scope: Related-commit and Related-Fix baselines computed on the training split, 10k samples;
    pairing requires same author, same project and a one-week window.
  evidence: Table 2
- id: repo-split-gap
  kind: result
  text: Splitting ComSum by repository rather than by commit costs fine-tuned BART about 6
    RougeL points, while the split-by-commit drop is about 1 point. The gap is therefore domain
    shift between repositories rather than memorization.
  scope: Comparison between the main repository-level split and the minor commit-level split;
    the test set is also more abstractive, with coverage 0.25 versus 0.31 and density 0.86
    versus 0.99.
  evidence: Section 5
- id: meaning-not-preserved
  kind: result
  text: BART changes a ComSum commit's meaning in 10% of corrective cases, 16% of refactor
    cases and 35% of adaptive cases. Those rates are measured on messages that carry a distractor
    core term but are not of the matching commit type.
  scope: Meaning judged by the commit classifiers of Amit and Feitelson (93% accuracy for
    corrective and refactoring, 65% for adaptive), applied to both message and summary.
  evidence: Table 4
- id: bart-precision
  kind: result
  text: BART's highest meaning-preservation precision on any commit concept tested on ComSum
    is 75%. A quarter or more of summaries therefore drop the concept expressed in the message
    even when Rouge scores are high.
  scope: Precision-like metric P(concept(model(message))) given P(concept(message)) over corrective,
    adaptive and refactor concepts, estimated with automatic commit classifiers rather than
    human labels.
  evidence: Section 6
- id: subject-is-summary
  kind: result
  text: In manual labeling of 100 ComSum samples, 80% of commit subjects were proper summaries
    of their message. Filtering merge commits and administrative messages raises that to about
    90% on the labeled sample.
  scope: Two authors labeled independently with 82% initial agreement, rising to 99% after
    protocol tuning; the administrative-message heuristic has 98.9% precision and about 75%
    recall.
  evidence: Section 3.2
- id: typed-trends
  kind: result
  text: Rouge trends on the corrective, refactor and adaptive ComSum test subsets match the
    general test set, with fine-tuned BART at RougeL 26.2 to 26.9 against 14.3 to 16.0 for
    zero-shot BART.
  scope: Typed test subsets built from the commit-type classifiers; results are for BART,
    zero-shot BART and the Random Message Sentence heuristic only.
  evidence: Table 3
- id: context-domain
  kind: context
  text: ComSum introduces software commit messages as a summarization domain and argues the
    pairing is natural because Git and GitHub already present the one-line subject as a summary
    of the longer message.
  scope: English-language commits, which are about 99% of the sampled commits; the domain
    is specific to software development, so gains on ComSum need not transfer to news or literary
    summarization.
  evidence: Appendix B
- id: context-meaning-eval
  kind: context
  text: ComSum proposes evaluating summarizers by whether the output preserves the commit's
    type in Swanson's corrective/adaptive/perfective taxonomy, a domain-grounded alternative
    to word-overlap scores like Rouge.
  scope: Applicable where an automatic, high-agreement classifier for the meaning aspect exists;
    for commits, human agreement on bug classification is 95%.
  evidence: Section 6
- id: context-growable
  kind: context
  text: ComSum ships both a frozen static release and the extraction code and SQL queries,
    so the same pipeline can rebuild a larger dataset from later commits or with different
    filtering choices.
  scope: As of the 2021 release; regeneration depends on the BigQuery GitHub schema, from
    which projects can disappear, so a regenerated dataset will not match the frozen one.
qa:
- q:
  - Is there a large dataset for summarizing software commit messages?
  - What data can I train a summarizer on for git commits?
  - How big is ComSum and where does the data come from?
  answers:
  - dataset-size
  - context-domain
- q:
  - Which summarization datasets are the most abstractive?
  - Is commit message summarization more abstractive than news summarization?
  - How does ComSum compare to XSum and CNN/DM on coverage and density?
  answers:
  - abstractiveness
  - vocabulary
- q:
  - How well do pretrained summarizers do on commit messages?
  - What Rouge score does BART get on ComSum?
  - Does fine-tuning help on commit message summarization?
  answers:
  - bart-baseline
  - still-challenging
- q:
  - Can you just copy the commit message as its summary?
  - Do extractive heuristics work for commit summarization?
  - How strong are trivial baselines on commit message summarization?
  answers:
  - copying-insufficient
  - related-commit
- q:
  - Does splitting a summarization dataset by repository change results?
  - Why is the ComSum test set harder than its train set?
  - Is the train-test gap on ComSum memorization or domain shift?
  answers:
  - repo-split-gap
- q:
  - How often do neural summarizers change the meaning of what they summarize?
  - Do summarization models preserve whether a commit is a bug fix or a refactor?
  - How much does BART alter commit meaning on distractor cases?
  answers:
  - meaning-not-preserved
  - bart-precision
- q:
  - How can I evaluate summaries beyond Rouge?
  - What work proposes meaning preservation as a summarization metric?
  - Where should I start reading about domain-grounded summarization evaluation?
  answers:
  - context-meaning-eval
  - bart-precision
- q:
  - Are git commit subjects actually summaries of their messages?
  - How reliable is using the commit subject line as a reference summary?
  - What fraction of commit subjects are genuine summaries?
  answers:
  - subject-is-summary
- q:
  - Do results on ComSum hold across commit types?
  - Does summarization quality differ for bug fixes versus refactoring commits?
  - What are the Rouge scores on the corrective and refactor subsets of ComSum?
  answers:
  - typed-trends
- q:
  - Can a commit summarization dataset be regenerated with more recent data?
  - Is ComSum reproducible and extensible?
  - How do I build my own version of a commit summarization dataset?
  answers:
  - context-growable
- q:
  - What are good NLP datasets in the software engineering domain?
  - Which paper introduced commit messages as a summarization task?
  - Where should I start reading about NLP for programming artifacts?
  answers:
  - context-domain
  - context-meaning-eval
misreadings:
- 'ComSum''s high Rouge numbers for fine-tuned BART do not mean the summaries are factually
  correct: manual inspection found hallucinated terms, names and version numbers, such as
  "Merge pull request #14" for #1110.'
- The meaning-preservation figures in ComSum are estimated with automatic commit classifiers,
  not human judgments, so cross-concept comparisons must account for classifier accuracy —
  93% for corrective and refactoring but 65% for adaptive.
- 'ComSum is not a filtered-clean corpus: merge commits, administrative messages and generic
  subjects are deliberately left in, with 429K merge commits listed and filtering code provided,
  so users must apply the optional filters themselves.'
- 'ComSum''s release is not a moving target by accident: a static frozen version limited to
  pre-2021 commits is published for reproducibility alongside the extraction code, and a regenerated
  version will differ because projects can be deleted from the index.'
- Improvements on ComSum should not be assumed to transfer to other summarization domains,
  since bugs and refactoring have no analogue outside software development.
terminology:
  Core term: A word whose appearance in a commit message is indicative of a commit concept,
    such as 'bug', 'bugfix', 'error', 'fail' or 'fix' for the corrective concept.
  Meaning preservation (commit summarization): The requirement that a generated commit summary
    carry the same commit type as the source message, measured as the probability that the
    summary is classified into a concept given that the message is.
  Corrective / adaptive / perfective: Swanson's 1976 commit taxonomy, in which a change is
    a bug fix (corrective), an added feature (adaptive), or refactoring and documentation
    improvement (perfective).
  Corrective Commit Probability (CCP): The estimated share of a project's commits that fix
    bugs; a negative estimate is treated as a sign that a repository is not a software project.
  Not Preserved: The share of generated summaries whose commit meaning changed, computed as
    the sum of the Core-and-Concept and Not-Core-and-Concept cases on messages that carry
    a distractor core term without belonging to that concept.
links_extra:
  code: https://github.com/evidencebp/comsum
  dataset: https://figshare.com/articles/dataset/CumSum_data_set/14711370
  zenodo: https://zenodo.org/badge/latestdoi/384742703
---
