<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced via a forced tool call) + 2 repair rounds. Every claim, number
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

Stamp: spec=d57862840a90 checks=2 body=6d6fcabf3811
-->
---
claims:
- id: wow-annotated-dataset
  kind: result
  text: Q² releases a dataset of Wizard-of-Wikipedia dialogue responses from the MemNet and
    dodecaDialogue systems, hand-annotated for factual consistency. The release covers 544
    dialogue contexts and 1,088 annotated responses, with Fleiss' kappa of 0.853 on a 100-response
    agreement sample.
  scope: English Wizard-of-Wikipedia validation set only; annotated by 3 of the paper's authors,
    who deliberately skipped pure chit-chat responses and picked clear, coherent inconsistent
    examples rather than sampling uniformly.
  evidence: Section 4
- id: wow-separation
  kind: result
  text: On the annotated Wizard-of-Wikipedia data, Q² scores 0.238 for inconsistent versus
    0.696 for consistent dodecaDialogue responses, and 0.135 versus 0.756 for MemNet. The
    token-overlap baseline separates the same responses far less (0.299 vs 0.426 and 0.270
    vs 0.526).
  scope: 150 consistent and 150 inconsistent responses per system, plus 150 random responses
    per system; scores computed with T5-base QG, Albert-Xlarge QA and RoBERTa-SNLI answer
    comparison, with no reference response used.
  evidence: Table 2
- id: response-level-accuracy
  kind: result
  text: At an untuned decision threshold of 0.5 on Wizard-of-Wikipedia responses, Q² classifies
    consistent versus inconsistent responses with 77.3% accuracy. Q² without the NLI answer
    comparison reaches 73.1% and end-to-end NLI 65.3%.
  scope: Threshold of 0.5 chosen arbitrarily rather than tuned on a development split; measured
    on the paper's annotated dodecaDialogue and MemNet consistent/inconsistent responses.
  evidence: Section 5.1
- id: system-level-correlation
  kind: result
  text: In a bootstrapped system-level evaluation on Wizard-of-Wikipedia, Q² reaches an average
    Spearman correlation of 0.9798 with human consistency judgments, above end-to-end NLI
    (0.9216), knowledge overlap (0.878), BERTScore (0.8467) and BLEU (0.3051).
  scope: Simulated systems built by bootstrapping 350 contexts sampled with repetition from
    244 dialogue contexts, repeated 1000 times; confidence intervals are wide (Q² lower CI
    0.9, BLEU lower CI -0.7).
  evidence: Table 4
- id: topical-chat
  kind: result
  text: On Topical-Chat's "Uses Knowledge" human ratings, Q² attains Spearman 0.4579 and Pearson
    0.4698, above the best USR result (0.4468 Spearman, 0.3175 Pearson) and METEOR (0.3909
    Spearman, 0.3328 Pearson).
  scope: 52 knowledge-grounded dialogue contexts and 260 responses from the USR annotation
    collection; grounding text includes Washington Post articles and Reddit fun-facts, not
    only Wikipedia.
  evidence: Table 5
- id: dnli-accuracy
  kind: result
  text: On the Dialogue NLI Test Gold split, Q² reaches 74.49% accuracy in a zero-shot setting.
    The same NLI model applied end-to-end reaches 67.42%, InferSent hypothesis-only 51.52%
    and InferSent trained on SNLI 47.03%.
  scope: Binary entailment-versus-contradiction decision with a 0.1 threshold tuned on the
    DNLI development set, treating neutral pairs as inconsistent; pronoun-based question filtering
    is disabled for this persona task.
  evidence: Table 6
- id: nli-vs-token-matching
  kind: result
  text: Replacing token-level F1 answer matching with NLI-based answer comparison raises Q²'s
    consistent-response scores on Wizard-of-Wikipedia from 0.516 to 0.696 (dodecaDialogue)
    and 0.661 to 0.756 (MemNet), widening the gap from inconsistent responses.
  scope: 150 consistent and 150 inconsistent annotated WoW responses per system; RoBERTa fine-tuned
    on SNLI with the question prepended to both answer spans, applied only to span pairs that
    do not match exactly at the token level.
  evidence: Table 2
- id: small-model-robustness
  kind: result
  text: 'Swapping Q²''s question generator for T5-small or its QA model for Albert-base barely
    changes system-level correlation with human judgments: 0.9722 and 0.9797 versus 0.9798
    for the original. Question coverage stays above 88%.'
  scope: Measured on the WoW annotated data; absolute Q² scores do shift — lower with T5-small
    and higher with Albert-base — so thresholds are not transferable across component sizes.
  evidence: Table 7 and Table 8
- id: chitchat-no-questions
  kind: result
  text: Q² generates no valid question for roughly 6–8% of the annotated consistent and inconsistent
    Wizard-of-Wikipedia responses, but for about 20% of randomly sampled responses. Question
    generation therefore fails mainly on general chit-chat rather than on knowledge-bearing
    content.
  scope: WoW responses from MemNet and dodecaDialogue; such cases fall back to an end-to-end
    NLI score, and unresolved pronouns referring to the dialogue history are a further cause
    of discarded questions.
  evidence: Section 5.4
- id: random-knowledge
  kind: result
  text: When the grounding knowledge is replaced by a random passage, Q² collapses as intended,
    to 0.02 for knowledge taken from another turn of the same dialogue and 0 for knowledge
    from a different dialogue. Over 91% and 99.61% of generated questions respectively have
    no answer in that knowledge.
  scope: Adversarial check on the WoW annotated data only; measures sensitivity to mismatched
    knowledge, not correctness on genuinely grounded responses.
  evidence: Table 10
- id: length-not-a-cue
  kind: result
  text: 'Response length does not distinguish factually consistent from inconsistent dialogue
    responses in the annotated Wizard-of-Wikipedia data: inconsistent responses average 15.79
    tokens and consistent ones 15.13, with random samples at 15.86.'
  scope: dodecaDialogue outputs, with similar results reported for MemNet; the annotation
    protocol selected clear and coherent examples, which may itself flatten length differences.
  evidence: Table 11
- id: context-first-qgqa-dialogue
  kind: context
  text: Q² brought the question-generation/question-answering approach to factual-consistency
    evaluation for knowledge-grounded dialogue. Dialogue responses mix knowledge with opinions,
    questions to the user and chit-chat that should not be scored against the knowledge.
  scope: As of EMNLP 2021; QG/QA consistency metrics existed for abstractive summarization
    (Durmus et al. 2020, Wang et al. 2020, QuestEval), and the concurrent BEGIN benchmark
    framed grounded-dialogue evaluation as NLI instead.
  evidence: Section 6
- id: context-reference-free
  kind: context
  text: Q² is a reference-free metric for grounded dialogue, scoring a response against its
    grounding knowledge alone without a gold human response. That matters because dialogue
    is open-ended, and reference-based metrics such as BLEU correlate weakly with human judgments
    on it.
  scope: Requires an explicit textual knowledge source per turn, as in Wizard-of-Wikipedia
    or Topical-Chat; it does not check claims against the open world and so is not a fact-checking
    system.
  evidence: Section 1
- id: interpretability
  kind: context
  text: 'Q² is interpretable by construction: alongside the score it emits the generated questions,
    the answer spans taken from the response and the answers the QA model found in the knowledge.
    Those outputs can be used to highlight the potentially inconsistent spans.'
  scope: Explanations are as good as the underlying QG and QA models; the paper reports errors
    where questions are generated for chit-chat spans such as "purple is my favorite color".
  evidence: Section 5.4
qa:
- q:
  - How can I automatically tell whether a chatbot's answer contradicts the document it was
    given?
  - What metric detects hallucination in knowledge-grounded dialogue responses?
  - Is there an automatic way to measure factual consistency of dialogue systems without a
    gold reference?
  answers:
  - context-reference-free
  - wow-separation
  - response-level-accuracy
- q:
  - What should I read first about evaluating factual consistency in dialogue?
  - Which paper introduced QA-based consistency evaluation for grounded dialogue?
  - Where did the question-generation/question-answering evaluation idea move from summarization
    to dialogue?
  answers:
  - context-first-qgqa-dialogue
  - context-reference-free
- q:
  - Does comparing answer spans with NLI beat token overlap for consistency scoring?
  - How much does the NLI answer comparison in Q² actually help?
  - Why not just use token-level F1 to compare the response answer and the knowledge answer?
  answers:
  - nli-vs-token-matching
  - response-level-accuracy
- q:
  - How well does Q² correlate with human judgments compared with BLEU and BERTScore?
  - Which automatic metric correlates best with human factual-consistency ratings for dialogue
    systems?
  - Does BLEU work for ranking dialogue systems by faithfulness to knowledge?
  answers:
  - system-level-correlation
  - topical-chat
- q:
  - Is there an annotated dataset of dialogue responses labelled for factual consistency?
  - What data was released with the Q² paper for Wizard of Wikipedia?
  - How reliable were the factual-consistency annotations on Wizard-of-Wikipedia system outputs?
  answers:
  - wow-annotated-dataset
  - length-not-a-cue
- q:
  - Can a QG/QA consistency metric also measure persona consistency in Persona-Chat?
  - How does Q² do on the Dialogue NLI benchmark?
  - Does a QG/QA consistency metric work when the "knowledge" is a persona sentence or an
    earlier dialogue turn?
  answers:
  - dnli-accuracy
- q:
  - Do I need large question generation and question answering models to run Q²?
  - How sensitive is a QG/QA consistency metric to the size of its underlying QG and QA models?
  - Can I substitute T5-small and Albert-base in a QG/QA consistency pipeline?
  answers:
  - small-model-robustness
- q:
  - What happens when a dialogue response is pure chit-chat and no question can be generated?
  - How often does Q² fail to produce a valid question for a response?
  - What are the failure modes of QG/QA-based dialogue consistency evaluation?
  answers:
  - chitchat-no-questions
  - interpretability
- q:
  - Does a consistency metric behave correctly when given the wrong grounding passage?
  - How does Q² score responses against randomly selected knowledge?
  - Is a QG/QA faithfulness metric fooled by mismatched grounding knowledge?
  answers:
  - random-knowledge
- q:
  - Can an automatic faithfulness metric explain why it gave a low score?
  - Does Q² show which span of a dialogue response is unsupported?
  - Is QG/QA-based evaluation interpretable?
  answers:
  - interpretability
- q:
  - Are longer dialogue responses more likely to be factually inconsistent?
  - Do surface features like response length predict hallucination in grounded dialogue?
  answers:
  - length-not-a-cue
- q:
  - How does Q² compare with USR on Topical-Chat?
  - What correlation does a QA-based metric get on the "Uses Knowledge" human ratings?
  answers:
  - topical-chat
coined: Q²
gloss: a reference-free metric that scores a dialogue response's faithfulness to its grounding
  knowledge by generating questions from the response and answering them from the knowledge
one_liner: Q² scores the factual consistency of a knowledge-grounded dialogue response by
  generating questions from its informative spans, answering them against the grounding knowledge,
  and comparing the two answer spans with an NLI model instead of token overlap.
key: honovich2021q2
links_extra:
  code: https://github.com/orhonovich/q-squared
  arxiv: https://arxiv.org/abs/2104.08202
  data: https://github.com/orhonovich/q-squared/tree/main/third_party/data
misreadings:
- Q² does not check whether a dialogue response is true of the world; it checks only whether
  the response is consistent with the specific knowledge passage the model was conditioned
  on, so a response repeating a false grounding sentence scores high.
- The 0.5 response-level threshold that yields 77.3% accuracy on Wizard-of-Wikipedia was chosen
  arbitrarily for illustration, not tuned; treating 0.5 as a calibrated cut-off for other
  datasets or other QG/QA components is unwarranted, since absolute Q² scores shift when components
  are swapped.
- 'The annotated Wizard-of-Wikipedia dataset is not a random sample of system outputs: annotators
  skipped chit-chat-only consistent responses and selected clear, coherent inconsistent ones,
  so class proportions in it do not estimate how often the systems hallucinate.'
- Robustness to smaller QG and QA models means correlations with human judgments hold, not
  that scores are comparable across configurations — T5-small lowers and Albert-base raises
  absolute Q² scores.
- 'Low Q² on a response is not always evidence of hallucination: questions generated for chit-chat
  or opinion spans, and unresolved pronouns referring to earlier turns, produce spurious mismatches.'
terminology:
  Q² w/o NLI: An ablated variant of Q² in which the NLI-based answer-span comparison is dropped
    and answer spans are compared by token-level F1 only, as in earlier QG/QA summarization
    metrics.
  informative span: A named entity or noun phrase extracted from a generated dialogue response
    with spaCy, used as the target answer for automatic question generation.
  question coverage: The percentage of dialogue responses for which at least one generated
    question survives filtering, so the score is computed from question answering rather than
    from the end-to-end NLI fallback.
  question filtering: Discarding a generated question if the QA model, reading the response
    itself, does not return the exact span the question was generated from, or if the question
    is about personal statements (subject "I"/"you", possessive "my"/"your").
  end-to-end NLI fallback: 'The score assigned when no valid question survives filtering:
    an NLI model is run with the knowledge as premise and the response as hypothesis, giving
    1 for entailment, 0 for contradiction and 0.5 for neutral.'
---
