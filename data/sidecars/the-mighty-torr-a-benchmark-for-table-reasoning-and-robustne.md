---
claims:
- id: best-score-050
  kind: result
  text: On ToRR, the best-performing LLMs (claude-3-5-sonnet, gpt-4o and deepseek-v3) reach
    an overall performance score of only 0.50. The weakest evaluated model, llama-3-1-8b-instruct,
    reaches 0.29.
  scope: 14 models across 7 families, 10 table datasets, 100 sampled examples per dataset,
    5-shot greedy decoding; scores averaged over 35 prompt configurations.
  evidence: Table 2
- id: narrow-gap
  kind: result
  text: Performance differences between models within the same family on ToRR average 0.07,
    and paired Cohen's d shows most model comparisons on ToRR have small, often non-significant
    practical differences.
  scope: 14 models on 10 table datasets over 35 prompt configurations; aggregated p-values
    still find all pairwise comparisons significant.
  evidence: Section 3.2 and Section 3.1
- id: brittleness
  kind: result
  text: 'Every model evaluated on ToRR is unrobust: across the 35 semantically equivalent
    prompt configurations of one example, the minimum and maximum scores give entirely different
    estimates of performance. Robustness scores run from 0.49 for mixtral-8x7b-instruct to
    0.70 for claude-3-5-sonnet.'
  scope: Robustness is 1 minus the mean per-example score range over 7 serializations x 4
    structural perturbations plus 7 unperturbed variants; tables embedded directly in the
    prompt, no tool use.
  evidence: Table 2 and Figure 3
- id: no-best-serializer
  kind: result
  text: 'No table serialization format consistently wins on ToRR: aggregated over all models
    and datasets no serializer outperforms the others, and per-model serializer preferences
    shift overall performance by at most 0.06.'
  scope: 7 serializations — HTML, CSV, JSON, Markdown, Indexed Row Major, DataFrame and Concatenation
    — measured by example-level win rate over 14 models and 10 datasets; individual model-dataset
    pairs still vary much more.
  evidence: Section 3.3 and Figure 9
- id: serializer-worst-case
  kind: result
  text: On ToRR the gap between a model's best and worst serializer on a single dataset averages
    about 0.05. It reaches 0.22 for llama-3-1-8b-instruct on TableBench FC, and 0.23 for llama-3-1-405b-instruct
    on the same dataset.
  scope: Largest max-minus-min score difference across the 7 serializations, computed per
    model-dataset pair over 14 models and 10 datasets.
  evidence: Table 7
- id: perturbations-no-effect
  kind: result
  text: Structural table perturbations in ToRR have no consistent direction of effect, changing
    model scores by an average of 0.03 relative to the unperturbed baseline. The 4 perturbations
    are row swapping, column swapping, transposition and adding empty rows.
  scope: 4 perturbations applied on top of each of 7 serializations, 14 models, 10 datasets;
    per-example absolute impact is larger, and more pronounced for smaller models and for
    Table QA and fact-checking datasets than for Table-to-Text.
  evidence: Figure 12 and Figure 15
- id: single-prompt-unreliable
  kind: result
  text: Model rankings derived from a single table prompt configuration agree poorly with
    one another on ToRR, so a benchmark that fixes one serialization format yields an unreliable
    ranking of models.
  scope: Kendall's W over 30 sampled prompt-configuration sets, 14 models, 100 examples per
    dataset; table serializations and structural perturbations only, not instruction wording.
  evidence: Figure 4
- id: ten-prompts-gain
  kind: result
  text: Increasing the number of table prompt configurations from 1 to 10 raises Kendall's
    W ranking agreement on ToRR by more than 0.35 on average. The largest gains fall between
    roughly 2 and 8 configurations.
  scope: Averaged over 30 sampled configuration sets and over ToRR's datasets; per-dataset
    gains differ sharply, FinQA rising from 0.35 to 0.93 with 11 prompts while NumericNLG
    rises only from 0.29 to 0.54.
  evidence: Figure 4
- id: prompts-substitute-examples
  kind: result
  text: 'Adding prompt configurations can substitute for test examples: on ToRR, 50 examples
    evaluated with 2 prompt configurations give about the same model-ranking reliability as
    100 examples with 1 configuration.'
  scope: Kendall's W over 30 randomly sampled example-and-configuration sets, averaged per
    dataset, on table reasoning tasks at these small sample sizes.
  evidence: Figure 5
- id: separability
  kind: result
  text: Aggregated ToRR separates 79% of model pairs with non-overlapping confidence intervals,
    while individual datasets range from 38% for TableBench FC to over 71% for WikiTQ.
  scope: Bootstrapping 1K seeds over samples of 100 examples per dataset with the 14 evaluated
    models; separability depends on which models are compared.
  evidence: Section 4 and Figure 19
- id: closed-vs-open
  kind: result
  text: Closed proprietary models outperform open-weight models across most ToRR datasets,
    though the open qwen2-72b-instruct beats llama-3-1-405b-instruct on both performance and
    robustness.
  scope: 14 models released through late 2024 and early 2025, served via Together AI and vendor
    APIs; no reasoning-mode or tool-using configurations.
  evidence: Figure 8 and Table 2
- id: benchmark-contribution
  kind: context
  text: ToRR is a table reasoning benchmark that measures robustness as a first-class quantity,
    pairing 10 datasets over 6 tabular tasks with 35 semantically equivalent prompt configurations
    per example. Scores therefore reflect consistency across table formats rather than one
    chosen format.
  scope: Covers tables that fit directly in the prompt as text; excludes tool-using, agentic,
    retrieval, multi-table and image-based table settings, and hierarchical tables. Compared
    against TableBench, DataBench, TQA-Bench, InfiAgent-DABench and TableVQA-Bench.
  evidence: Table 8
- id: robust-eval-practice
  kind: context
  text: ToRR is a worked example for benchmark designers that evaluating over many semantically
    equivalent prompt variants, rather than one canonical prompt, is what makes a leaderboard's
    model ranking reproducible.
  scope: Shown for table serialization formats and structural table perturbations in English
    table tasks as of 2025; other prompt dimensions are argued by analogy to prior work, not
    measured.
qa:
- ask:
    plain: how good are today's chatbots at answering questions about spreadsheets and tables?
    jargon: what overall accuracy do frontier LLMs reach on tabular reasoning tasks, and how
      far apart are models within one family?
    task: how do I find out whether any available LLM is accurate enough to run question answering
      over my data tables?
    practitioner: if I need table question answering, does it matter much which top model
      I pick?
  answered_by:
  - best-score-050
  - narrow-gap
- ask:
    plain: does writing a table as CSV instead of HTML change how well a language model answers
      questions about it?
    jargon: how sensitive is LLM table reasoning accuracy to the serialization format of the
      input table?
    task: how do I tell whether my table formatting choice is costing me accuracy on a table
      QA pipeline?
    practitioner: should I worry that switching my tables from markdown to JSON will change
      my model's answers?
  answered_by:
  - brittleness
  - no-best-serializer
  - serializer-worst-case
- ask:
    plain: what is the best way to write a table into a prompt so a language model understands
      it?
    jargon: is there a serialization format for tabular input that dominates across models
      and table reasoning datasets?
    task: which table format should I use when I feed tables into an LLM prompt?
    practitioner: can I just pick one table format for all my models, or do I have to test
      each one?
  answered_by:
  - no-best-serializer
  - serializer-worst-case
- ask:
    plain: if I shuffle the rows of a table or flip it sideways, do language models get more
      answers wrong?
    jargon: what effect do structural table perturbations such as row and column swapping
      or transposition have on LLM task scores?
    task: do I need to normalize row order and orientation in my tables before sending them
      to an LLM?
    practitioner: is it worth cleaning up transposed tables and blank rows in my data before
      running a model on them?
  answered_by:
  - perturbations-no-effect
- ask:
    plain: can you trust a leaderboard that tested every model with the same single prompt?
    jargon: how many prompt configurations are needed before model rankings become stable
      in Kendall's W agreement?
    task: how many prompt variants should I evaluate over to get a model ranking that does
      not flip?
    practitioner: I ranked a few models with one prompt template, should I redo it with more?
  answered_by:
  - single-prompt-unreliable
  - ten-prompts-gain
- ask:
    plain: is it better to test a model on more examples or on more versions of the same prompt?
    jargon: can additional prompt configurations substitute for test-set size in achieving
      reliable model rankings?
    task: I have a limited evaluation budget for table tasks, how should I split it between
      examples and prompt variants?
    practitioner: should I spend my annotation budget labelling more test examples or writing
      more prompt formats?
  answered_by:
  - prompts-substitute-examples
  - ten-prompts-gain
- ask:
    plain: is there a benchmark that checks both whether models can read tables and whether
      their answers survive reformatting?
    jargon: which table reasoning benchmark treats robustness across semantically equivalent
      prompts as a reported metric rather than a fixed prompt leaderboard?
    task: where should I start reading about how table formatting affects language model evaluation?
    practitioner: which table benchmark should I cite if I want to argue single-prompt leaderboards
      are unreliable?
  answered_by:
  - benchmark-contribution
  - robust-eval-practice
- ask:
    plain: on table question answering tests, can you actually tell two models apart or do
      their scores overlap?
    jargon: what fraction of model pairs are separated by non-overlapping confidence intervals
      on aggregated versus individual table reasoning datasets?
    task: which table dataset should I evaluate on if I need to show a statistically distinguishable
      difference between two models?
    practitioner: is one table dataset enough to prove my model beats a competitor, or do
      I need to aggregate several?
  answered_by:
  - separability
- ask:
    plain: are open models catching up with the big commercial ones at reading tables?
    jargon: do open-weight LLMs match proprietary models on tabular reasoning performance
      and robustness, and does parameter count track accuracy?
    task: how do I decide between a self-hosted open model and a commercial API for reasoning
      over tables?
    practitioner: can I swap a paid API for an open-weight model on my table extraction workload
      without losing accuracy?
  answered_by:
  - closed-vs-open
  - narrow-gap
- ask:
    plain: what kinds of table questions and data sources go into a table reasoning test set?
    jargon: which tabular tasks, datasets and prompt configurations make up the ToRR benchmark
      suite?
    task: what table skills would I be covering if I evaluated on a multi-task table reasoning
      benchmark?
    practitioner: does a table benchmark I might adopt cover the task types my product actually
      does, like fact checking and table QA?
  answered_by:
  - benchmark-contribution
- ask:
    plain: how do you put a number on whether a model gives consistent answers when a table
      is rewritten?
    jargon: how is a per-example robustness score computed across semantically equivalent
      table prompt configurations?
    task: how do I measure the spread between a model's best-case and worst-case score across
      equivalent prompts?
    practitioner: how should I report my model's consistency across table formats rather than
      just its average accuracy?
  answered_by:
  - brittleness
one_liner: ToRR evaluates 14 LLMs on 10 table reasoning datasets under 35 semantically equivalent
  prompt configurations — 7 serializations crossed with 4 structural perturbations — and shows
  that table performance tops out around 0.50 while every model's score swings widely across
  formats that carry identical information.
coined: ToRR
gloss: 'a benchmark for Table Reasoning and Robustness: table tasks scored across many equivalent
  table formats'
key: ashurytahan2025torr
terminology:
  Prompt configuration: A pairing of one table serialization format with at most one structural
    table perturbation; ToRR uses 35 of them per example (7 serializations x 4 perturbations,
    plus the 7 unperturbed serializations).
  Serialization: A method for converting a table into a string that can be embedded in a prompt,
    such as HTML, CSV, JSON, Markdown, Indexed Row Major, DataFrame or Concatenation.
  Structural perturbation: 'A change to how a table''s content is laid out without changing
    its content or cell relations: row swapping, column swapping, transposition, or inserting
    empty rows.'
  Robustness score (R): One minus the average per-example range (maximum minus minimum) of
    a model's score across all prompt configurations of that example, so 1.0 means identical
    scores on every table format.
  Mean Absolute Impact: The mean of the absolute score change caused by a perturbation relative
    to its unperturbed baseline, used so that positive and negative effects do not cancel
    out in an average.
  Separability with Confidence: The percentage of model pairs whose bootstrapped score confidence
    intervals do not overlap, used as a measure of how well a benchmark distinguishes models.
misreadings:
- 'ToRR''s finding that no serializer wins on average does not mean table format is irrelevant
  in practice: individual model-dataset pairs vary by about 0.05 between their best and worst
  serializer and by up to 0.23 in the worst case, so a deployment still needs its format chosen
  by case-by-case tuning.'
- The low robustness scores in ToRR are not evidence that models prefer particular table formats.
  The variation is largely idiosyncratic per example, which the paper reads as general prompt
  sensitivity rather than a format preference.
- 'ToRR''s low absolute scores are not simply a small-model story: the strongest closed models
  reach only 0.50 overall, and the gap between the strongest and weakest large models is narrow.'
- The claim that prompt configurations can substitute for test examples is demonstrated for
  ranking reliability at small sample sizes — 50 examples with 2 configurations matching 100
  examples with 1 — and is not a claim that prompt variation replaces data collection in general.
- 'ToRR does not measure agentic or tool-using table capabilities: datasets requiring SQL,
  retrieval, code execution, multi-table joins or table images were deliberately excluded,
  so its scores are not an upper bound on what a table-using pipeline can do.'
links_extra:
  arxiv: https://arxiv.org/abs/2502.19412
---
