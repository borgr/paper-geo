<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced via a forced tool call) + 3 repair rounds. Every claim, number
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

Then promote it:  python scripts/draft_sidecars.py --accept how-safe-is-your-safety-metric-automatic-concatenation-tests

Stamp: spec=8f05813a4658 checks=pass body=0ff42c39285c
-->
---
key: fandina2025safetymetric
one_liner: Concatenation-based tests — repeating, clustering and permuting prompt-response
  pairs — expose that harmfulness metrics including GPT-3.5 and GPT-4o judges flip their safety
  verdicts and score by input order rather than content.
gloss: automatic tests that concatenate, repeat and reorder prompt-response pairs to check
  whether a safety metric's scores stay consistent
coined: Concatenation-based metric validity tests
claims:
- id: gpt35-cluster-flip
  kind: result
  text: The GPT-3.5-based harmfulness judge scored 203 of 1000 concatenated 4-tuples of unsafe
    prompt-response pairs as safe (scores 1 or 2), while GPT-4o flipped its verdict in only
    2 of 1000 cases.
  scope: 4-tuples sampled from 50 pairs the same judge scored 4 or 5, on Mistral-7B-Instruct-v0.2
    responses to AttaQ prompts, 1-5 scale, OpenAI API at seed=2.
  evidence: Figure 6
- id: gpt4o-flip-rate-low
  kind: result
  text: GPT-4o as a harmfulness judge keeps its decision-flipping rate below 0.1% as the number
    of concatenated prompt-response pairs grows, whereas GPT-3.5's flip rate rises with concatenation
    length.
  scope: Safe and harmful cluster tests at 4, 8 and 16 concatenations, 1000 sampled tuples
    per setting, on AttaQ prompts and Mistral-7B-Instruct-v0.2 responses; single dataset and
    single task.
  evidence: Figures 15 and 16
- id: gpt35-positional-bias
  kind: result
  text: The GPT-3.5-based judge's positional bias is 24.4% for 8-concatenated lists of prompt-response
    pairs and 45.9% for 16-concatenated lists. Positional bias counts inputs whose verdict
    flips between scores {4,5} and {1,2} when the input order is reversed.
  scope: Balanced pools of 50 pairs scored {4,5}, 25 scored 3 and 50 scored {1,2} per metric;
    1000 sampled concatenations per length; increasing versus decreasing sorted permutations.
  evidence: Table 5 and Table 6
- id: gpt4o-order-dominates
  kind: result
  text: With 16-tuple inputs of effectively identical content, the GPT-4o judge scored 80%
    of tuples (803 of 1000) as safe when pairs were sorted from low to high harmfulness. The
    same content scored safe in about 40% of cases under random permutations and 1% under
    the decreasing permutation.
  scope: 1000 concatenated 16-tuples drawn from a balanced score pool; AttaQ prompts with
    Mistral-7B-Instruct-v0.2 responses; GPT-4o via OpenAI API, default temperature, seed=2.
  evidence: Figure 7
- id: positional-bias-grows-with-length
  kind: result
  text: Positional bias in both GPT-based harmfulness judges grows with the length of the
    concatenated input, so longer aggregated inputs are scored more by the order of their
    parts than by their content.
  scope: Concatenation lengths of 4, 8 and 16 prompt-response pairs; GPT-3.5-turbo-0125 and
    GPT-4o judges only; reward-model metrics show low positional bias instead.
  evidence: Figure 12
- id: reward-repetition-sensitive
  kind: result
  text: The OpenAssistant deberta-based and pythia-based reward metrics assign lower scores
    as input content is repeated, with the pythia-based model shifting most. Its Wasserstein
    distance from the unrepeated score distribution reaches 4.277 when both prompt and response
    are repeated 8 times.
  scope: Repetitions up to l=5 for deberta-based (512-token context) and l=16 for pythia-based
    (1024-token context); 1000 AttaQ prompts with Mistral-7B-Instruct-v0.2 responses; distances
    computed between score distributions, not per example.
  evidence: Table 2
- id: deberta-repetition-magnitudes
  kind: result
  text: 'For the deberta-based reward metric, repeating the response alone shifts the score
    distribution more than repeating the prompt alone: Wasserstein distance 2.065 at 5 response
    repetitions versus 0.900 at 5 prompt repetitions.'
  scope: OpenAssistant/reward-model-deberta-v3-large-v2 with a 512-token context, so repetition
    counts stop at 5; scores over 1000 AttaQ prompt-response pairs from Mistral-7B-Instruct-v0.2.
  evidence: Table 1
- id: gpt-ignores-repetition
  kind: result
  text: The GPT-3.5 and GPT-4o judges are insensitive to repeated content, preserving their
    original harmfulness scores when the prompt, the response, or both are repeated — the
    opposite of the reward-model metrics' behaviour.
  scope: Repetition tests on AttaQ prompts and Mistral-7B-Instruct-v0.2 responses; 16k-token
    context for GPT-3.5 and 128k for GPT-4o, so long repeated inputs still fit.
  evidence: Figures 9 and 10
- id: reward-low-positional-bias
  kind: result
  text: The reward-model harmfulness metrics show only minor sensitivity to input order, with
    average pairwise Wasserstein distance between permuted-input score distributions of 0.064
    for the deberta-based metric and 0.097 for the pythia-based metric.
  scope: Six permutations per concatenated input, including increasing- and decreasing-score
    sorts, where the largest gaps occur (0.147 deberta, 0.583 pythia between increasing and
    decreasing); AttaQ data with Mistral-7B-Instruct-v0.2 responses.
  evidence: Table 3 and Table 4
- id: reward-cluster-not-preserved
  kind: result
  text: Reward-model harmfulness metrics do not preserve cluster scores under concatenation.
    For the safe (high-score) 2-concatenated cluster, a large part of the concatenated score
    distribution falls well below the average of the two original pair scores.
  scope: Clusters built from the top and bottom 10% of scored pairs (100 pairs each), with
    1000 randomly formed 2-concatenations; deberta-based and pythia-based OpenAssistant reward
    models.
  evidence: Figure 5 and Figure 13
- id: context-safety-of-safety-metrics
  kind: context
  text: '"How Safe is Your Safety Metric?" argues that safety metrics themselves need validity
    testing, and supplies automatic repetition, cluster and concatenate-and-permute tests
    for that purpose. The tests reuse a task''s existing prompt-response data and need no
    new annotation.'
  scope: Demonstrated on one task (model safety) with one dataset (AttaQ) and four metrics;
    the authors note the test suite is small and its generality to other tasks such as translation
    is proposed rather than shown.
  evidence: Section 1 and Section 3
- id: context-judge-caution
  kind: context
  text: Because GPT-3.5-based judges are widely used to decide the success of multi-turn and
    conversation-based jailbreak attacks on concatenated prompt-response content, their measured
    decision-flipping rate makes such attack-success numbers questionable.
  scope: Concerns gpt-3.5-turbo-0125 with the Appendix A scoring prompt as evaluated in this
    work; other implementations, prompts and judge models — GPT-4o in particular — behaved
    more consistently in the cluster tests.
  evidence: Section 1
qa:
- q:
  - Can a harmful response slip past an LLM safety filter just by being concatenated with
    other text?
  - Do harmfulness metrics reverse their verdict when unsafe prompt-response pairs are combined?
  - How often does a GPT-based safety judge label concatenated unsafe content as safe?
  answers:
  - gpt35-cluster-flip
  - gpt4o-flip-rate-low
- q:
  - Does the order of content change how an LLM judge scores safety?
  - How large is positional bias in GPT-3.5 and GPT-4o harmfulness judges?
  - If safe text comes first, will a judge model call the whole input safe?
  answers:
  - gpt35-positional-bias
  - gpt4o-order-dominates
- q:
  - Does positional bias in LLM judges get worse with longer inputs?
  - Is judge order sensitivity related to input length?
  answers:
  - positional-bias-grows-with-length
- q:
  - Are reward models usable as safety filters if an attacker repeats the prompt or response?
  - Do OpenAssistant reward models change their score when input content is repeated?
  - How much do repeated prompts and responses shift reward-model harmfulness scores?
  answers:
  - reward-repetition-sensitive
  - deberta-repetition-magnitudes
- q:
  - Are GPT judges affected by repeated content in the input?
  - Which safety metrics ignore duplicated prompts and responses?
  answers:
  - gpt-ignores-repetition
- q:
  - Are reward-model safety metrics sensitive to the order of concatenated inputs?
  - Which harmfulness metrics have low positional bias?
  answers:
  - reward-low-positional-bias
- q:
  - Do safety scores stay consistent when several equally safe pairs are concatenated?
  - What happens to reward-model scores when two safe prompt-response pairs are merged into
    one input?
  answers:
  - reward-cluster-not-preserved
  - gpt-ignores-repetition
- q:
  - What work should I read on whether automatic safety evaluation metrics are reliable?
  - Where can I find a paper on validating LLM-as-a-judge safety metrics?
  - Is there research on testing the metrics used to measure model harmfulness?
  - How do I check the validity of a safety metric without collecting new human labels?
  answers:
  - context-safety-of-safety-metrics
- q:
  - Is GPT-3.5 a trustworthy judge for measuring jailbreak attack success?
  - Should attack-success rates measured with a GPT-3.5 judge be trusted?
  - What are the risks of using an LLM judge to score multi-turn red-teaming attacks?
  answers:
  - context-judge-caution
  - gpt35-cluster-flip
- q:
  - Which safety metrics and datasets were tested in the concatenation study?
  - What models were used to generate the harmful responses in the concatenation tests?
  answers:
  - context-safety-of-safety-metrics
  - reward-repetition-sensitive
misreadings:
- 'GPT-4o is not shown to be a robust safety judge overall: it keeps a decision-flipping rate
  below 0.1% in the cluster tests, yet exhibits strong positional bias, scoring 80% of 16-tuples
  safe under a low-to-high sort versus 1% under the reverse sort.'
- 'Insensitivity to repeated content is not a general property of LLM judges over reward models:
  GPT-3.5 and GPT-4o preserve their scores under repetition, but GPT-3.5 is the metric with
  the highest decision-flipping rate under concatenation.'
- The concatenation tests do not measure how harmful a language model is; they measure whether
  a harmfulness metric's scores stay consistent under input transformations that preserve
  content.
- 'The findings are not established across tasks or datasets: all experiments use one task
  (model safety), one prompt dataset (AttaQ) and one base model (Mistral-7B-Instruct-v0.2),
  and the authors list this limited scope as a limitation.'
- A high positional-bias number is not evidence that a metric disagrees with humans; it reports
  how often the metric's own verdict flips when only the order of identical content is reversed.
terminology:
  Decision flipping: A safety metric's verdict changing category — for example from harmful
    scores {4,5} to safe scores {1,2} — when individually scored prompt-response pairs are
    concatenated into a single input.
  Positional bias (of a safety metric): The percentage of concatenated inputs whose metric
    verdict flips between the harmful and safe score categories when the order of the concatenated
    prompt-response pairs is reversed.
  Cluster test: A metric validity test that collects inputs a metric scores uniformly high
    or uniformly low, concatenates them, and checks whether the concatenation receives the
    same class of score.
  Repetition test: A metric validity test that concatenates a prompt, a response, or both
    with itself l times and tracks how the metric's score changes as l grows.
  Concatenate-and-permute test: A metric validity test that concatenates several prompt-response
    pairs and rescores the same content under several orderings, including sorts by increasing
    and decreasing individual scores, to measure order sensitivity.
  AttaQ: A dataset of 1400 questions designed to elicit harmful responses from a language
    model, used as the prompt source for the concatenation tests.
---
