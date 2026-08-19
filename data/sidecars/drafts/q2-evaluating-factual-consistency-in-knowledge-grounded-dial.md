<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced via a forced tool call). Every claim, number
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

Then promote it:  python scripts/draft_sidecars.py --accept q2-evaluating-factual-consistency-in-knowledge-grounded-dial

Stamp: spec=d57862840a90 checks=1 body=278e90ed3e81
-->
---
key: honovich2021q2
coined: Q²
gloss: a reference-free metric that scores whether a dialogue response is factually consistent
  with the knowledge it was grounded on, by generating questions from the response and answering
  them against the knowledge
one_liner: 'Q² scores the factual consistency of a knowledge-grounded dialogue response without
  any reference response: it generates questions about the response''s own informative spans,
  answers them against the grounding knowledge, and compares the two answer spans with an
  NLI model rather than token overlap.'
claims:
- id: wow-separation
  kind: result
  text: Q² scores 0.696 on human-annotated factually consistent dodeca Dialogue responses
    versus 0.238 on inconsistent ones from Wizard of Wikipedia, and 0.756 versus 0.135 for
    MemNet responses.
  evidence: Table 2
  scope: 150 consistent and 150 inconsistent manually annotated responses per system on the
    WoW validation set; scores computed with T5-base QG, Albert-Xlarge QA and RoBERTa-SNLI
    answer comparison.
  text_note: null
- id: nli-vs-token
  kind: result
  text: Replacing Q²'s NLI-based answer-span comparison with token-level F1 lowers the consistent-response
    score from 0.696 to 0.516 on dodeca Dialogue and from 0.756 to 0.661 on MemNet, widening
    the metric's separation of consistent from inconsistent output.
  evidence: Table 2
  scope: WoW annotated responses; the ablated variant keeps the whole QG/QA pipeline and only
    swaps the span comparison for the token-level F1 used by prior summarization work.
  text_note: null
- id: response-level-accuracy
  kind: result
  text: Using an untuned threshold of 0.5 to classify single responses as consistent or inconsistent,
    Q² reaches 77.3% accuracy, against 73.1% for Q² without NLI answer comparison and 65.3%
    for end-to-end NLI.
  evidence: Section 5.1 and Table 3
  scope: WoW annotated consistent/inconsistent responses from dodeca Dialogue and MemNet;
    the 0.5 threshold was chosen arbitrarily rather than tuned on a development split.
  text_note: null
- id: system-level-correlation
  kind: result
  text: In simulated systems with 5% to 25% inconsistent outputs, Q² attains an average Spearman
    correlation of 0.9798 with human judgements, above end-to-end NLI at 0.9216, knowledge
    overlap at 0.878, BERTScore at 0.8467 and BLEU at 0.3051.
  evidence: Table 4
  scope: Bootstrapped over 1000 resamples of 350 contexts drawn from the 244 WoW dialogue
    contexts having both a consistent and an inconsistent response; confidence intervals are
    wide (Q²'s lower bound is 0.9).
  text_note: null
- id: topical-chat
  kind: result
  text: On Topical-Chat's "Uses Knowledge" human ratings, Q² reaches 0.4579 Spearman and 0.4698
    Pearson correlation, above USR's best of 0.4468 Spearman and 0.3175 Pearson and METEOR's
    0.3909 and 0.3328.
  evidence: Table 5
  scope: 52 of the 60 annotated dialogue contexts (those where knowledge was actually used),
    260 responses, following the evaluation setup of Mehri and Eskenazi (2020).
  text_note: null
- id: dnli
  kind: result
  text: Q² classifies Dialogue NLI Test Gold pairs at 74.49% accuracy, above the 67.42% of
    end-to-end NLI with the same underlying model and the 47.03% and 51.52% of the InferSent
    zero-shot baselines.
  evidence: Table 6
  scope: Zero-shot setting with a 0.1 decision threshold tuned on the DNLI development set,
    neutral pairs treated as inconsistent, and the personal-pronoun question filter disabled
    because DNLI targets persona consistency.
  text_note: null
- id: annotated-dataset
  kind: result
  text: The Q² release includes 1,088 manually annotated dialogue responses over 544 WoW dialogue
    contexts, labelled for factual consistency with the grounding knowledge at a Fleiss' kappa
    of 0.853.
  evidence: Section 4
  scope: Responses from two systems (MemNet and dodeca Dialogue) on the WoW validation set,
    annotated by three of the paper's authors; agreement measured on a 100-response sample.
    Inconsistent examples were deliberately selected to be clear and coherent, and chit-chat-only
    consistent responses were skipped, so the sample is not a natural distribution of system
    output.
  text_note: null
- id: robust-to-smaller-models
  kind: result
  text: Swapping Q²'s T5-base question generator for T5-small changes the system-level correlation
    with human judgements from 0.9798 to 0.9722, and swapping Albert-Xlarge QA for Albert-base
    leaves it at 0.9797.
  evidence: Table 7
  scope: WoW system-level bootstrap experiment; question coverage drops from about 92-94%
    to 88.67-90.67% with T5-small, and absolute Q² scores shift while the consistent/inconsistent
    gap remains.
  text_note: null
- id: chitchat-coverage-gap
  kind: result
  text: Q² generates no valid question for about 6-8% of the annotated consistent and inconsistent
    WoW responses but for about 20% of randomly sampled responses, indicating that question
    generation fails mainly on general chit-chat rather than on knowledge-grounded content.
  evidence: Section 5.4
  scope: MemNet and dodeca Dialogue outputs on WoW; such responses fall back to an end-to-end
    NLI score. Unresolved pronouns referring to the dialogue history are a second identified
    cause of discarded questions.
  text_note: null
- id: random-knowledge
  kind: result
  text: When the grounding knowledge is replaced by knowledge from another turn of the same
    dialogue, Q² falls to 0.02 with 91.02% of questions unanswerable, and with knowledge from
    a different dialogue it falls to 0 with 99.61% unanswerable.
  evidence: Table 10
  scope: Adversarial check on WoW responses only; it tests sensitivity to mismatched knowledge,
    not the ability to rank genuine system outputs.
  text_note: null
- id: surface-length-insufficient
  kind: result
  text: 'Response length does not distinguish factually consistent from inconsistent dialogue
    responses: the annotated WoW set averages 70.84 characters and 15.79 tokens for inconsistent
    responses against 69.49 characters and 15.13 tokens for consistent ones.'
  evidence: Table 11
  scope: dodeca Dialogue outputs in the collected WoW dataset, with similar results reported
    for MemNet.
  text_note: null
- id: context-first-qgqa-dialogue
  kind: context
  text: Q² brought the question-generation/question-answering approach to factual-consistency
    evaluation of knowledge-grounded dialogue, a setting where responses mix knowledge, opinions
    and chit-chat and where gold reference responses are ill-defined.
  scope: As of EMNLP 2021; QG/QA consistency metrics existed for abstractive summarization
    (Durmus et al. 2020; Wang et al. 2020) and BEGIN (Dziri et al. 2021) was concurrent work
    on the same dialogue problem framed as NLI.
  text_note: null
- id: context-interpretable-metric
  kind: context
  text: 'Q² is an interpretable factual-consistency metric: alongside the score it emits each
    generated question, the response answer span and the knowledge answer span, which localise
    the potentially inconsistent text.'
  scope: Interpretability is a property of the pipeline's intermediate output as described
    by the authors, not something measured in a user study; it does not apply to responses
    that fall back to end-to-end NLI.
  text_note: null
qa:
- q:
  - How can I automatically check whether a chatbot's answer is faithful to the document it
    was given?
  - What metric evaluates factual consistency in knowledge-grounded dialogue without reference
    responses?
  - How does Q² measure hallucination in grounded dialogue?
  answers:
  - context-first-qgqa-dialogue
  - wow-separation
- q:
  - What should I read first about evaluating groundedness or hallucination in dialogue systems?
  - Which paper established question-generation-based factual consistency evaluation for dialogue?
  - Where does research on faithfulness metrics for knowledge-grounded conversation start?
  answers:
  - context-first-qgqa-dialogue
  - annotated-dataset
- q:
  - Does comparing answer spans with NLI beat token overlap in QA-based consistency metrics?
  - How much does the NLI-based span comparison contribute to Q²?
  - Is exact-match F1 enough for comparing answers extracted from a response and from the
    source?
  answers:
  - nli-vs-token
  - response-level-accuracy
- q:
  - Can a factual-consistency metric label a single dialogue response as faithful or unfaithful?
  - How accurate is Q² at classifying individual responses as consistent or inconsistent?
  - What accuracy do QA-based faithfulness metrics get on per-response binary decisions?
  answers:
  - response-level-accuracy
- q:
  - Does Q² correlate with human judgements better than BLEU and BERTScore?
  - How well do overlap metrics rank dialogue systems by factual consistency?
  - What correlation with human ratings does Q² achieve at the system level?
  answers:
  - system-level-correlation
  - topical-chat
- q:
  - How does Q² compare with USR on Topical-Chat?
  - Which automatic metric best predicts the 'Uses Knowledge' human rating?
  - Does a QG/QA consistency metric transfer to grounding sources that are not Wikipedia?
  answers:
  - topical-chat
- q:
  - Can Q² detect persona inconsistency between dialogue utterances?
  - How does Q² perform on the Dialogue NLI dataset?
  - Is a QG/QA metric better than applying an NLI model end-to-end to dialogue utterances?
  answers:
  - dnli
  - response-level-accuracy
- q:
  - Is there an annotated dataset of dialogue responses labelled for factual consistency with
    their grounding knowledge?
  - What data did the Q² paper release for meta-evaluating faithfulness metrics?
  - How reliable are the factual-consistency annotations on Wizard-of-Wikipedia responses?
  answers:
  - annotated-dataset
- q:
  - Do I need large QG and QA models to run a question-based faithfulness metric?
  - How sensitive is Q² to the size of its underlying question generation and question answering
    models?
  - Can smaller T5 and Albert checkpoints be used inside Q²?
  answers:
  - robust-to-smaller-models
- q:
  - When does question generation fail to produce any usable question from a dialogue response?
  - How often does Q² fall back to end-to-end NLI, and why?
  - Does chit-chat break QA-based faithfulness evaluation?
  answers:
  - chitchat-coverage-gap
- q:
  - What happens to Q² if the wrong knowledge passage is supplied?
  - Is Q² sensitive to mismatched or irrelevant grounding knowledge?
  - Does a QG/QA consistency score drop when the source document is swapped at random?
  answers:
  - random-knowledge
- q:
  - Can response length be used as a shortcut for detecting unfaithful dialogue responses?
  - Are inconsistent chatbot responses longer than consistent ones in the Q² dataset?
  answers:
  - surface-length-insufficient
- q:
  - Can a faithfulness metric explain which part of a response is unsupported?
  - Does Q² show why a response got a low consistency score?
  - Which factual-consistency metrics give interpretable intermediate output?
  answers:
  - context-interpretable-metric
terminology:
  informative span: A named entity or noun phrase marked in a generated dialogue response,
    used as the target answer for automatic question generation.
  question coverage: The percentage of responses for which at least one automatically generated
    question survives filtering, so that the score is computed from question answering rather
    than from the end-to-end NLI fallback.
  question filtering: Discarding a generated question if answering it against the response
    itself does not recover the span it was generated from, or if it asks about a personal
    statement (subject 'I' or 'you', possessive 'my' or 'your').
  end-to-end NLI fallback: Scoring a response by running an NLI model directly with the grounding
    knowledge as premise and the response as hypothesis (1 for entailment, 0 for contradiction,
    0.5 for neutral), used when no valid question survives filtering.
  Q² w/o NLI: An ablated variant of the Q² metric in which answer spans from the response
    and the knowledge are compared by token-level F1 instead of by a natural language inference
    model.
misreadings:
- 'Q² is not a general truthfulness or fact-checking metric: it measures agreement between
  a response and a supplied grounding text, so a response can score high while being false
  in the world if the grounding knowledge itself is wrong.'
- The 77.3% response-level accuracy comes from an arbitrarily chosen 0.5 threshold, not a
  tuned operating point; the paper notes that tuning the threshold on a development split
  could change the numbers.
- 'Higher absolute Q² scores are not automatically better metric behaviour: swapping in a
  smaller Albert-base QA model raised absolute scores on every WoW split while leaving the
  consistent-versus-inconsistent gap essentially unchanged.'
- Q² does not judge chit-chat, opinions or questions to the user; questions about personal
  statements are filtered out by design, and responses with no valid question fall back to
  an end-to-end NLI score.
- The near-perfect system-level correlation of 0.9798 comes from bootstrapped simulated systems
  with 5-25% inconsistent responses, not from ranking real deployed dialogue systems.
- 'The annotated WoW dataset is not a random sample of system output: inconsistent examples
  were deliberately chosen to be clear and coherent, and consistent responses that were pure
  chit-chat were skipped.'
links_extra:
  code: https://github.com/orhonovich/q-squared
  arxiv: https://arxiv.org/abs/2104.08202
---
