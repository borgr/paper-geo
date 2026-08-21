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
- ask:
    plain: is there a big collection of software commit messages paired with their one-line
      subjects for training summarizers?
    jargon: what scale and provenance does the ComSum commit-message summarization corpus
      have across GitHub projects and authors?
    task: where do I get a large-scale training set for generating commit subject lines from
      commit message bodies?
    practitioner: is there enough commit-message data out there for me to train a summarization
      model on, or do I need to scrape GitHub myself?
  answered_by:
  - dataset-size
  - context-domain
- ask:
    plain: do commit message summaries reuse the words of the original text less than news
      headlines do?
    jargon: how does ComSum compare with XSum and BOOKSUM on extractive coverage, density
      and vocabulary size?
    task: which summarization corpus should I pick if I need genuinely abstractive reference
      summaries and a large vocabulary?
    practitioner: if my model keeps copying spans instead of abstracting, would commit-message
      data push it harder than news data?
  answered_by:
  - abstractiveness
  - vocabulary
- ask:
    plain: how well does an off-the-shelf summarization model do at writing commit subject
      lines?
    jargon: what RougeL does BART reach on ComSum zero-shot versus fine-tuned, and how does
      that compare to CNN/Daily Mail and XSum?
    task: do I need to fine-tune a pretrained summarizer on commit messages, or will it work
      out of the box?
    practitioner: is commit-message summarization already solved by fine-tuning BART, or is
      there headroom left for my model?
  answered_by:
  - bart-baseline
  - still-challenging
- ask:
    plain: can you get a decent commit subject line just by copying part of the message?
    jargon: how do lead/random-sentence extraction and same-author related-commit subjects
      score in RougeL on ComSum?
    task: what trivial baselines should I beat before claiming a commit summarizer works?
    practitioner: would a simple copy-the-first-sentence heuristic be good enough for generating
      commit subjects in my tooling?
  answered_by:
  - copying-insufficient
  - related-commit
- ask:
    plain: does it matter whether a commit dataset is split by project or just shuffled by
      commit?
    jargon: how much RougeL does a repository-level split of ComSum cost fine-tuned BART relative
      to a commit-level split?
    task: how should I split a commit-message dataset so the test set actually measures generalization
      to new projects?
    practitioner: if I train a commit summarizer on my own repos, should I expect the score
      to drop on a codebase it has never seen?
  answered_by:
  - repo-split-gap
- ask:
    plain: how often does a summarization model quietly change what the original text was
      saying?
    jargon: what is BART's meaning-preservation precision on ComSum for corrective, refactor
      and adaptive commit categories with distractor terms?
    task: how do I test whether my summarizer keeps the intent of the input rather than just
      matching words?
    practitioner: can I trust a fine-tuned summarizer to keep a bug fix labeled as a bug fix
      rather than as a refactor?
  answered_by:
  - meaning-not-preserved
  - bart-precision
- ask:
    plain: which research suggests judging a summarizer by whether it keeps the original meaning
      rather than by word overlap?
    jargon: what work proposes domain-grounded meaning-preservation evaluation for summarization
      as an alternative to Rouge?
    task: where do I start reading if I want an evaluation for my summarizer that goes beyond
      Rouge?
    practitioner: my Rouge scores look fine, so what should I read to find out whether my
      summaries actually preserve meaning?
  answered_by:
  - context-meaning-eval
  - bart-precision
- ask:
    plain: is the short first line of a git commit really a summary of the rest of the message?
    jargon: what proportion of commit subjects in ComSum were manually validated as faithful
      summaries of the message body, and how does filtering merge and administrative commits
      change it?
    task: can I use commit subject lines as reference summaries without hand-annotating them?
    practitioner: how much label noise am I accepting if I treat the commit subject as ground-truth
      summary in my training data?
  answered_by:
  - subject-is-summary
- ask:
    plain: are the results the same for bug-fix commits as for cleanup or feature-adaptation
      commits?
    jargon: do RougeL trends on the corrective, refactor and adaptive ComSum test subsets
      track the full test set for zero-shot and fine-tuned BART?
    task: do I need separate models or separate evaluations for different kinds of commits?
    practitioner: if most of my commits are bug fixes, will a commit summarizer behave differently
      on them than the headline numbers suggest?
  answered_by:
  - typed-trends
- ask:
    plain: can a commit-message dataset be rebuilt from newer commits as projects keep growing?
    jargon: does ComSum release the extraction pipeline and SQL queries alongside a frozen
      static split so the corpus can be regenerated?
    task: how do I regenerate a larger commit-summarization dataset with my own filtering
      rules?
    practitioner: if I need more data or different filters than the released commit-summarization
      split gives me, can I rebuild it myself?
  answered_by:
  - context-growable
- ask:
    plain: which paper first treated software commit messages as a text summarization task?
    jargon: what work introduced commit-message-to-subject pairs as a summarization domain
      with a software-grounded evaluation?
    task: what should I read to find NLP datasets and tasks drawn from software engineering
      artifacts?
    practitioner: I work on developer tools and want a summarization benchmark from real code
      history, so which paper should I cite as the starting point?
  answered_by:
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
