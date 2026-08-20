---
key: honovich2021q2
coined: Q²
gloss: a reference-free metric that scores whether a dialogue response is factually consistent
  with its grounding knowledge, by generating questions from the response and answering them
  against the knowledge
one_liner: 'Q² scores factual consistency in knowledge-grounded dialogue without reference
  responses: it generates questions from the model''s response, answers them against the grounding
  knowledge, and compares the two answer spans with an NLI model instead of token overlap.'
claims:
- id: wow-separation
  kind: result
  text: On manually annotated Wizard-of-Wikipedia responses, Q² averages 0.696 on consistent
    and 0.238 on inconsistent dodeca Dialogue outputs, and 0.756 versus 0.135 on MemNet outputs.
    Random samples fall in between, at 0.496 and 0.448.
  scope: 150 consistent and 150 inconsistent responses per system, annotated by 3 of the paper's
    authors on the WoW validation set; inconsistent examples were deliberately chosen to be
    clear and coherent.
  evidence: Table 2
- id: nli-vs-token
  kind: result
  text: An NLI-based answer-span comparison widens Q²'s gap between consistent and inconsistent
    Wizard-of-Wikipedia responses. For dodeca Dialogue outputs the scores are 0.696 versus
    0.238 with NLI, against 0.516 versus 0.159 with token-level F1 matching.
  scope: WoW annotated responses; the NLI model is RoBERTa fine-tuned on SNLI, applied only
    to answer pairs that do not match exactly at the token level, with the question prepended
    to both premise and hypothesis.
  evidence: Table 2
- id: response-level-accuracy
  kind: result
  text: Using an untuned response-level threshold of 0.5, Q² classifies Wizard-of-Wikipedia
    responses as consistent or inconsistent with 77.3% accuracy, against 73.1% for Q² without
    the NLI comparison and 65.3% for end-to-end NLI.
  scope: The 0.5 threshold was selected arbitrarily rather than tuned on a development split;
    measured on the annotated dodeca Dialogue and MemNet consistent/inconsistent examples.
  evidence: Section 5.1 and Table 3
- id: system-level-correlation
  kind: result
  text: In a bootstrapped system-level meta-evaluation on WoW, Q² reaches an average Spearman
    correlation of 0.9798 with human judgments, above end-to-end NLI (0.9216), knowledge overlap
    (0.878), BERTScore (0.8467) and BLEU (0.3051).
  scope: Simulated systems built by sampling 350 contexts with repetition from 244 dialogue
    contexts having both a consistent and an inconsistent response, with inconsistent proportions
    of 0.05 to 0.25, repeated 1000 times.
  evidence: Table 4
- id: topical-chat
  kind: result
  text: On Topical-Chat's "Uses Knowledge" human judgments, Q² obtains 0.4579 Spearman and
    0.4698 Pearson correlation, above the best USR result (0.4468 Spearman, 0.3175 Pearson)
    and METEOR (0.3909, 0.3328).
  scope: 52 of the 60 annotated dialogue contexts, excluding the 8 where no knowledge was
    used, and 260 responses following the USR setting that drops the original human response.
  evidence: Table 5
- id: dnli
  kind: result
  text: Q² reaches 74.49% accuracy on the Dialogue NLI Test Gold split, above the end-to-end
    NLI baseline (67.42%) and the zero-shot InferSent baselines (47.03% for InferSent SNLI,
    51.52% for hypothesis-only).
  scope: Zero-shot use of Q² with a 0.1 decision threshold tuned on the DNLI development set,
    neutral pairs treated as inconsistent, and no filtering of questions containing personal
    or possessive pronouns.
  evidence: Table 6
- id: robust-to-components
  kind: result
  text: 'Swapping Q²''s T5-base question generator for T5-small, or its Albert-Xlarge QA model
    for Albert-base, barely changes the system-level correlation with human judgments: 0.9722
    and 0.9797 respectively, against 0.9798 for the original pipeline.'
  scope: WoW system-level bootstrap setting; question coverage drops slightly with smaller
    models (from about 92-95% to 88.67-92.67%), and the smaller QG model lowers absolute Q²
    scores while the smaller QA model raises them.
  evidence: Table 7 and Table 8
- id: random-knowledge
  kind: result
  text: Replacing the grounding knowledge with knowledge from another turn of the same dialogue
    drops Q² to 0.02, with 91.02% of generated questions unanswerable. With knowledge from
    a different dialogue Q² drops to 0, with 99.61% unanswerable.
  scope: Adversarial check on WoW responses only, using randomly selected knowledge passages
    rather than model-generated hallucinations.
  evidence: Table 10
- id: wow-dataset
  kind: result
  text: The Q² paper releases 1,088 Wizard-of-Wikipedia dialogue responses over 544 contexts,
    annotated for factual consistency against the grounding sentence, with Fleiss' kappa of
    0.853 on a 100-response agreement sample.
  scope: Outputs of 2 systems (MemNet and dodeca Dialogue) on the WoW validation set, generated
    with beam size 10; the sample is not a random draw, and 34.2% of contexts were inconsistent
    for dodeca and 50.36% for MemNet.
  evidence: Section 4
- id: chit-chat-coverage
  kind: result
  text: Q² produces no valid questions for about 20% of randomly sampled Wizard-of-Wikipedia
    responses, versus around 6-8% of the annotated consistent and inconsistent responses,
    because general chit-chat yields fewer answerable factual questions.
  scope: WoW responses from MemNet and dodeca Dialogue; such cases fall back to an end-to-end
    NLI prediction, and unresolved pronouns referring to the dialogue history are a further
    cause of discarded questions.
  evidence: Section 5.4
- id: context-first-qgqa-dialogue
  kind: context
  text: Q² carries the question-generation/question-answering approach to factual-consistency
    evaluation over from abstractive summarization to knowledge-grounded dialogue. Dialogue
    responses mix grounded knowledge with chit-chat, opinions and questions to the user, which
    the summarization metrics of Durmus et al. and Wang et al. did not have to handle.
  scope: As of publication at EMNLP 2021, and to the authors' knowledge the first QG-QA metric
    applied to dialogue generation; concurrent work on grounded-dialogue evaluation includes
    the BEGIN benchmark of Dziri et al. (2021), which frames groundedness as NLI.
  evidence: Section 6
- id: context-interpretable
  kind: context
  text: Q² is a reference-free dialogue metric whose intermediate output is itself the explanation.
    Alongside the score it emits the generated questions, the response answer spans and the
    knowledge-based answers, which can highlight potentially inconsistent spans.
  scope: Interpretability is argued from qualitative examples rather than a human study of
    explanation quality; the pipeline is slow, at roughly 1.5-2 hours on 4 CPUs per 150-response
    split.
  evidence: Section 5.4 and Appendix B
qa:
- q:
  - How can I automatically tell whether a chatbot's answer contradicts the document it was
    given?
  - Is there a metric for hallucination in knowledge-grounded dialogue that does not need
    a gold reference response?
  - How does Q² score factual consistency of a dialogue response?
  answers:
  - context-interpretable
  - wow-separation
- q:
  - Does using NLI instead of token overlap to compare answer spans actually help?
  - How much does the NLI-based span comparison add over token-level F1 matching?
  - What is the difference between Q² and Q² without NLI?
  answers:
  - nli-vs-token
  - response-level-accuracy
- q:
  - How well do automatic consistency metrics correlate with human judgments on Wizard of
    Wikipedia?
  - Does Q² correlate better with human ratings than BLEU, BERTScore or knowledge overlap?
  - Which factual-consistency metric ranks dialogue systems most like humans do?
  answers:
  - system-level-correlation
  - topical-chat
- q:
  - Can Q² be used to classify a single dialogue response as consistent or inconsistent?
  - What accuracy does a 0.5 threshold on Q² give for detecting inconsistent responses?
  - How good is response-level inconsistency detection with a question-generation metric?
  answers:
  - response-level-accuracy
- q:
  - Does Q² transfer to persona consistency and Dialogue NLI?
  - How does a QG-QA consistency metric do on the DNLI benchmark zero-shot?
  - Can question-generation-based evaluation detect persona contradictions in Persona-Chat?
  answers:
  - dnli
- q:
  - Do I need large question generation and question answering models for QG-QA based dialogue
    evaluation?
  - Is the Q² metric sensitive to the size of its underlying QG and QA models?
  - What happens if I substitute T5-small or Albert-base into the Q² pipeline?
  answers:
  - robust-to-components
- q:
  - Is there an annotated dataset of dialogue responses labelled for factual consistency?
  - What data does the Q² paper release for evaluating groundedness in Wizard of Wikipedia?
  - How large is the Wizard-of-Wikipedia factual consistency annotation set, and how reliable
    are the labels?
  answers:
  - wow-dataset
- q:
  - Where should I start reading about evaluating factual consistency in grounded dialogue?
  - What work brought QA-based summarization faithfulness metrics to dialogue?
  - Which paper established question-generation-based groundedness evaluation for dialogue
    systems?
  answers:
  - context-first-qgqa-dialogue
  - context-interpretable
- q:
  - What happens to a question-generation consistency metric when the grounding knowledge
    is completely irrelevant to the dialogue response?
  - How does Q² behave on adversarial cases with mismatched knowledge passages?
  - Does swapping in knowledge from a different Wizard-of-Wikipedia dialogue drive the consistency
    score to zero?
  answers:
  - random-knowledge
- q:
  - Why does a question-generation consistency metric fail on chit-chat responses?
  - How often does Q² generate no valid questions for a dialogue response?
  - What are the known failure modes of question-generation-based dialogue evaluation?
  answers:
  - chit-chat-coverage
  - context-interpretable
misreadings:
- 'A low Q² score does not always mean the response is unfaithful: questions generated for
  chit-chat or opinion spans, such as "What is purple?" answered by "my favorite color", get
  penalised even when the knowledge was used correctly.'
- The 0.5 response-level threshold that gives 77.3% accuracy on Wizard of Wikipedia was picked
  arbitrarily for demonstration, not tuned, and is not a recommended operating point.
- 'The released Wizard-of-Wikipedia annotations are not an unbiased sample of system outputs:
  annotators kept collecting until 150 consistent and 150 inconsistent responses per system
  were found, skipped incoherent responses, and skipped consistent responses that were pure
  chit-chat.'
- Q² does not classify NLI-style entailment labels end-to-end; the NLI model is used only
  to compare short answer spans, with the question prepended for context, and end-to-end NLI
  serves solely as a fallback when no valid question survives filtering.
- Q²'s reported gains over end-to-end NLI, overlap, BLEU and BERTScore are measured against
  those specific reference-free baselines on WoW, Topical-Chat and DNLI, not against the full
  space of later groundedness metrics.
terminology:
  Question coverage: The percentage of dialogue responses for which at least one generated
    question survives filtering, so that the metric is computed from question answering rather
    than from the end-to-end NLI fallback.
  Informative span: A named entity or noun phrase inside a generated dialogue response, marked
    with spaCy, that serves as the target answer for automatic question generation.
  Question filtering: Discarding a generated question if answering it with the response as
    the input paragraph does not return the original answer span, or if it asks about personal
    statements via the pronouns "I", "you", "my" or "your".
  End-to-end NLI baseline: Scoring a dialogue response by running an NLI model directly with
    the whole grounding knowledge as premise and the whole response as hypothesis, scoring
    1 for entailment, 0 for contradiction and 0.5 for neutral.
links_extra:
  code: https://github.com/orhonovich/q-squared
  dataset: https://github.com/orhonovich/q-squared/tree/main/third_party/data
---
