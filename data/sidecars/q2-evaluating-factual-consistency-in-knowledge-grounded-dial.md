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
- ask:
    plain: how can you tell whether a chatbot's answer actually matches the article it was
      supposed to use, without a gold answer to compare against?
    jargon: is there a reference-free factual-consistency metric for knowledge-grounded dialogue
      that also separates consistent from hallucinated responses?
    task: how do I score a generated dialogue response for groundedness against its source
      passage and see which span went wrong?
    practitioner: should I use Q² to flag hallucinated responses from my knowledge-grounded
      chatbot when I have no reference replies?
  answered_by:
  - context-interpretable
  - wow-separation
- ask:
    plain: when checking if two answers to the same question agree, is entailment better than
      just counting shared words?
    jargon: does replacing token-level F1 answer-span matching with an NLI entailment check
      improve the separation and accuracy of Q²?
    task: how should I compare the answer extracted from a response with the answer from the
      source document — word overlap or an entailment model?
    practitioner: is the extra NLI model in the Q² pipeline worth running, or will token F1
      span matching do?
  answered_by:
  - nli-vs-token
  - response-level-accuracy
- ask:
    plain: which automatic score for chatbot groundedness agrees best with what human raters
      say?
    jargon: how does Q² compare with end-to-end NLI, knowledge overlap, BERTScore, BLEU, METEOR
      and USR on system-level correlation with human groundedness judgments?
    task: how do I rank knowledge-grounded dialogue systems for factual consistency the way
      human annotators would?
    practitioner: if I need one metric to compare my dialogue systems on faithfulness to knowledge,
      which one tracks human ratings closest?
  answered_by:
  - system-level-correlation
  - topical-chat
- ask:
    plain: can a groundedness score be turned into a yes-or-no verdict on a single chatbot
      reply?
    jargon: what response-level classification accuracy does a fixed 0.5 threshold on the
      Q² score reach on Wizard-of-Wikipedia?
    task: how do I get a binary consistent/inconsistent decision per response out of a continuous
      groundedness metric?
    practitioner: can I use Q² with a default cutoff to filter individual hallucinated responses,
      or is it only reliable for comparing systems?
  answered_by:
  - response-level-accuracy
- ask:
    plain: does a groundedness checker built for factual passages also catch a chatbot contradicting
      its own persona?
    jargon: how does the Q² question-generation and question-answering pipeline perform zero-shot
      on the Dialogue NLI Test Gold split against InferSent and end-to-end NLI baselines?
    task: how do I detect persona contradictions in Persona-Chat dialogue without training
      a dedicated NLI classifier on that data?
    practitioner: can I reuse Q² for persona-consistency checking, or do I need a model trained
      on Dialogue NLI?
  answered_by:
  - dnli
- ask:
    plain: does a groundedness score change much if the question-writing and question-answering
      models inside it are smaller?
    jargon: how sensitive is Q²'s system-level correlation with human judgments to swapping
      T5-base for T5-small and Albert-Xlarge for Albert-base?
    task: how do I cut the compute cost of a question-generation-based consistency metric
      without losing agreement with human ratings?
    practitioner: can I run Q² with smaller QG and QA checkpoints on my hardware and still
      trust the scores?
  answered_by:
  - robust-to-components
- ask:
    plain: is there a public set of chatbot replies labelled for whether they stick to the
      source text?
    jargon: what annotated Wizard-of-Wikipedia data with factual-consistency labels and inter-annotator
      agreement is released with Q²?
    task: where do I get labelled dialogue responses to benchmark my own hallucination detector
      for grounded dialogue?
    practitioner: is the Q² Wizard-of-Wikipedia annotation set big and reliable enough to
      validate my own groundedness metric?
  answered_by:
  - wow-dataset
- ask:
    plain: which paper should I read first on automatically checking whether chatbot answers
      stay faithful to the text they were given?
    jargon: what work carried question-generation/question-answering faithfulness evaluation
      from abstractive summarization over to knowledge-grounded dialogue?
    task: where do I start reading about explainable, reference-free groundedness evaluation
      for dialogue systems?
  answered_by:
  - context-first-qgqa-dialogue
  - context-interpretable
- ask:
    plain: what score does a groundedness checker give when the passage handed to it has nothing
      to do with the reply?
    jargon: how does Q² behave in adversarial controls where the grounding knowledge is swapped
      for another turn's or another dialogue's knowledge?
    task: how do I sanity-check that a factual-consistency metric is really reading the grounding
      document and not just the response?
    practitioner: will Q² give a near-zero score if I feed it the wrong knowledge passage,
      so I can trust it as a hallucination alarm?
  answered_by:
  - random-knowledge
- ask:
    plain: what happens to a groundedness checker when the reply is just small talk with no
      facts in it?
    jargon: how often does Q² produce no valid questions, and how does chit-chat coverage
      limit question-generation-based consistency evaluation?
    task: how do I handle dialogue responses that carry no verifiable content when scoring
      groundedness?
    practitioner: will Q² leave a chunk of my chatbot's responses unscored, and how would
      I know which ones?
  answered_by:
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
