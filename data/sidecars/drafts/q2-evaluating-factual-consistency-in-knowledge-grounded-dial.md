<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from build/sidecar_tasks.json. Every claim, number
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
-->
---
coined: Q²
gloss: a reference-free metric that checks whether a dialogue response is consistent with
  the text it was supposed to be grounded in, by asking questions about the response and answering
  them from the knowledge
one_liner: 'Q² scores a dialogue response for consistency with the text it was grounded in,
  needing no reference answer: it generates questions from the response, answers them from
  the knowledge, and compares the two answers by NLI rather than token overlap -- 77.3% response-level
  accuracy on Wizard of Wikipedia.'
claims:
- id: nli-instead-of-token-matching
  text: Q² compares the response's answer span with the knowledge's answer span using a natural
    language inference model rather than token overlap, which is what distinguishes it from
    earlier question-generation/question-answering consistency metrics; dropping the NLI comparison
    lowers response-level classification accuracy on Wizard of Wikipedia from 77.3% to 73.1%
    and Spearman correlation on Topical-Chat from 0.4579 to 0.3933.
  scope: The NLI model is RoBERTa fine-tuned on SNLI, run only on span pairs that do not already
    match exactly at the token level, with the question prepended to each answer for context;
    entailment scores 1, contradiction or no-answer 0, and the neutral case falls back to
    token-level F1. So the metric is not NLI-only -- the token-F1 path still carries the neutral
    cases, and the ablated variant remains a working metric rather than a broken one.
  evidence: Section 2 (Answer Similarity and Final Scores), Section 5.1, Table 5
- id: pipeline
  text: 'Q² works in three steps: mark every named entity and noun phrase in the response
    as an informative span, generate a question for each span from the response with T5-base
    fine-tuned on SQuAD1.1, then answer that question from the grounding text with Albert-Xlarge
    fine-tuned on SQuAD2.0 and compare the two answer spans; per-question scores average into
    a response score and response scores into a system score.'
  scope: Two filters do a lot of the work and change what the metric measures. Each question
    is round-tripped -- the QA model must recover the original span from the response, or
    the question is discarded -- and questions whose subject is 'I' or 'you' or that contain
    'my' or 'your' are dropped, so opinions and personal statements are excluded by construction.
    SQuAD2.0 is chosen because it can answer 'no answer', which is how fully hallucinated
    content is caught. When no question survives filtering, the score comes from an end-to-end
    NLI fallback (1 entailment, 0 contradiction, 0.5 neutral). Questions come from beam search
    with n=5; the paper reports the variant that keeps only the top-ranked surviving question,
    having found sampling-based decoding worse.
  evidence: Section 2, Figure 2
- id: separates-consistent-from-inconsistent
  text: On the paper's annotated Wizard of Wikipedia responses, Q² scores factually consistent
    output far above inconsistent output -- 0.696 against 0.238 for dodecaDialogue and 0.756
    against 0.135 for MemNet, with randomly sampled responses in between at 0.496 and 0.448.
  scope: Absolute Q² values are not comparable across systems or datasets; only the ordering
    within a set is meaningful, and the random-sample scores sit in between because those
    responses are a mix. The consistent and inconsistent sets are curated rather than sampled
    -- inconsistent examples were deliberately chosen to be fluent and coherent, and consistent
    responses that were pure chit-chat were skipped -- so the gap is measured on the cases
    that matter, not on average output. Every baseline also orders the two sets correctly;
    what distinguishes Q² is that the baselines barely separate inconsistent responses from
    the random sample.
  evidence: Table 2, Section 4, Section 5.1 (Baselines)
- id: hallucination-surfaces-as-unanswerable
  text: 'Hallucinated content shows up in Q² as questions the grounding text cannot answer:
    54.88% of the questions generated from inconsistent dodecaDialogue responses and 62.04%
    from inconsistent MemNet responses had no answer in the knowledge, against 15.25% and
    9.94% for consistent responses.'
  scope: 'This is why the QA model is fine-tuned on SQuAD2.0, which can abstain, rather than
    on SQuAD1.1: a question generated from invented content should have no answer. A no-answer
    result scores 0, the same as a contradiction, so the metric does not distinguish ''the
    knowledge says otherwise'' from ''the knowledge does not say''. The percentages are over
    questions that survived filtering, not over all generated questions.'
  evidence: Table 2, Section 2 (Question Answering)
- id: response-level-accuracy
  text: Used as a binary detector at a threshold of 0.5, Q² classifies individual Wizard of
    Wikipedia responses as consistent or inconsistent with 77.3% accuracy, against 73.1% for
    the same metric without the NLI comparison and 65.3% for end-to-end NLI applied to the
    whole response.
  scope: 'The 0.5 threshold was chosen arbitrarily to demonstrate separability, not tuned
    on a development split, and the paper says tuning it would likely improve the numbers
    -- so 77.3% is a floor for this use rather than a tuned operating point. Accuracy is on
    the curated consistent/inconsistent sets, which are balanced by construction. Precision
    and recall are asymmetric at this threshold: 73% precision at 86.7% recall for detecting
    inconsistency, 83.5% at 67.9% for detecting consistency. The precision-recall curves show
    Q² above every baseline across the whole threshold range, so the advantage is not an artefact
    of this cut point.'
  evidence: Section 5.1 (Response-Level Evaluation), Table 3, Figure 3
- id: system-level-correlation
  text: At the system level, Q² correlates with human factual-consistency judgements at an
    average Spearman of 0.9798, against 0.9216 for end-to-end NLI, 0.878 for token overlap
    with the knowledge, 0.8467 for BERTScore and 0.3051 for BLEU.
  scope: 'Systems here are simulated, following Graham and Liu''s bootstrap method for machine
    translation: 350 contexts are sampled with repetition from the 244 contexts that have
    both a consistent and an inconsistent response, at inconsistency rates of 5, 10, 15, 20
    and 25%, repeated 1000 times. So this measures whether the metric ranks systems that differ
    only in how often they hallucinate -- not whether it ranks real dialogue systems, which
    differ in many ways at once. All confidence intervals reach 1, and BLEU''s reaches -0.7.'
  evidence: Table 4, Section 5.1 (System-Level Evaluation)
- id: topical-chat-correlation
  text: On Topical-Chat's 'Uses Knowledge' human ratings, Q² correlates at 0.4579 Spearman
    and 0.4698 Pearson, above the best reported USR result (0.4468 and 0.3175) and METEOR
    (0.3909 and 0.3328), with the improvement over the baselines significant at p < 0.001.
  scope: 'Zero-shot: nothing in Q² was tuned for Topical-Chat, whose grounding includes Washington
    Post articles and Reddit fun-facts rather than only Wikipedia. The comparison is against
    numbers reported by Mehri and Eskenazi rather than re-run here, on the 52 of 60 dialogue
    contexts that used any knowledge and the 5 of 6 annotated responses per context they kept
    -- 260 responses. ''Uses Knowledge'' is a proxy: a response that uses knowledge properly
    is expected to use it consistently, but the two are not the same construct. This is the
    dataset where the NLI comparison helps most, which the paper reads as lexical variability
    mattering more when the grounding is not Wikipedia.'
  evidence: Table 5, Section 5.2
- id: dnli-accuracy
  text: 'Q² transfers to persona and self-consistency without retraining: on the Dialogue
    NLI Test Gold split it reaches 74.49% accuracy against 67.42% for the same NLI model applied
    end-to-end, 51.52% for a hypothesis-only InferSent model and 47.03% for InferSent trained
    on SNLI.'
  scope: 'The grounding text here is a persona description or an earlier utterance, not an
    external document. Two settings change for this dataset: the threshold is 0.1, tuned on
    the development split, and the pronoun filter is switched off, because personal statements
    are exactly what persona consistency is about. Neutral pairs are counted as inconsistent,
    which is a deliberate choice for dialogue rather than the standard NLI convention. All
    compared methods are zero-shot with respect to DNLI.'
  evidence: Table 6, Section 5.3, Section 3.3
- id: annotated-dataset
  text: 'The paper releases the first dataset of knowledge-grounded dialogue system outputs
    manually annotated for factual consistency: 1,088 responses over 544 Wizard of Wikipedia
    dialogue contexts, from MemNet and dodecaDialogue, annotated by three of the authors with
    Fleiss'' kappa 0.853 on a 100-response agreement sample.'
  scope: Built by annotating until 150 inconsistent and 150 consistent responses were collected
    per system (600 in total), then extending each context's annotation to both systems' outputs
    -- so it is a curated, balanced set, not a random sample of system output. Annotators
    skipped consistent responses that were pure chit-chat and preferred inconsistent responses
    that read as fluent and coherent, which makes the set harder than a random one on purpose.
    Both systems were decoded with beam size 10, beam block 3 and context block 3, so the
    outputs are specific to that decoding configuration.
  evidence: Section 4, Table 1, Appendix E
- id: annotation-asked-for-groundedness-not-truth
  text: The annotation guidelines told annotators to ignore their own background knowledge
    and judge only against the Wikipedia sentence the bot was given, to skip responses that
    were not clear and coherent, and to count as inconsistent both information the knowledge
    never mentioned and subtle changes to what it did say.
  scope: 'This is the operational definition behind every number in the paper, and it is narrower
    than ''factually wrong'': a response that is true about the world but unsupported by the
    given sentence is inconsistent by these instructions. It also explains the two ways the
    label is asymmetric -- incoherent responses were dropped rather than labelled, and ''not
    mentioned at all'' and ''subtly altered'' are collapsed into one class. The guidelines
    are adapted from Durmus et al.''s faithfulness annotation for summarisation.'
  evidence: Appendix E, Section 4
- id: reference-free-and-zero-shot
  text: 'Q² needs no gold reference response, no training on human consistency labels and
    no in-domain tuning: the same pipeline is applied zero-shot to Wizard of Wikipedia, Topical-Chat
    and Dialogue NLI, and beats the baselines on all three.'
  scope: Reference-free is the design requirement, not a convenience -- dialogue is open-ended,
    so a response can be perfectly consistent and share no words with any reference. What
    Q² does require is the grounding text the response was conditioned on, so it cannot be
    run on a dialogue whose knowledge source is unknown, and it evaluates the generator rather
    than the retrieval that chose that knowledge. Its QG and QA components are trained on
    SQuAD, which is Wikipedia text, yet transfer to the non-Wikipedia grounding in Topical-Chat
    and DNLI.
  evidence: Section 1, Section 5.4 (Analysis), Section 5.4 (Robustness to Underlying Model
    Quality)
- id: robust-to-component-size
  text: 'Q²''s correlation with human judgements barely moves when its components are made
    smaller: swapping T5-base for T5-small in question generation gives 0.9722 average system-level
    correlation and swapping Albert-Xlarge for Albert-base in question answering gives 0.9797,
    against 0.9798 for the original.'
  scope: 'Absolute scores do shift even though correlations do not, and not in one direction:
    the smaller QG model lowers Q² scores across every split, while the smaller QA model raises
    them. Question coverage drops a few points (for example 94% to 90.67% on consistent dodecaDialogue
    responses), so more responses fall through to the NLI fallback. The gap between consistent
    and inconsistent scores is what survives, which is the property a metric needs.'
  evidence: Table 7, Table 8, Section 5.4 (Robustness to Underlying Model Quality)
- id: decoding-and-filter-ablations
  text: 'The two design choices inside question generation trade coverage against sharpness:
    replacing beam search plus top-n selection with a single greedy question raises the raw
    scores on three of four splits but costs 5 to 10 points of question coverage, and additionally
    dropping the personal-pronoun filter lowers scores on every split while raising coverage
    again.'
  scope: 'The two ablations are cumulative -- the no-filter row is greedy decoding and no
    filter, so it must be read against the greedy row, not against full Q². Read that way,
    both ablations narrow the consistent/inconsistent gap: on dodecaDialogue it is 0.458 for
    full Q² against 0.435 for greedy, and on MemNet 0.621 against 0.576 (a subtraction of
    the paper''s own reported scores, not a figure it states). Coverage moves the other way,
    from 92.67% and 94% under full Q² to 87.33% and 85.33% under greedy. So the filters and
    the beam search buy separation at the cost of sending more responses to the end-to-end
    NLI fallback.'
  evidence: Appendix A, Table 9
- id: random-knowledge-sanity-check
  text: 'Given deliberately wrong grounding, Q² collapses to near zero: swapping in knowledge
    from a different turn of the same dialogue gives an average score of 0.02 with 91.02%
    of questions unanswerable, and knowledge from a different dialogue gives exactly 0 with
    99.61% unanswerable.'
  scope: An adversarial sanity check on the metric's floor, not a measurement of dialogue
    systems. It shows the score is driven by the grounding text rather than by generic response
    plausibility -- the same-dialogue variant is the harder one because the topic is shared,
    and it still scores 0.02. What it does not show is sensitivity at the top of the range,
    where the interesting errors are subtle rewrites of the correct knowledge.
  evidence: Appendix C (Random Knowledge), Table 10
- id: length-is-not-the-signal
  text: 'Inconsistent responses in the released dataset are not detectable from surface length:
    they average 70.84 characters and 15.79 tokens against 69.49 and 15.13 for consistent
    responses and 69.44 and 15.86 for random ones.'
  scope: Reported for the dodecaDialogue outputs with MemNet stated to be similar. It rules
    out one trivial shortcut on this dataset rather than establishing that no shortcut exists,
    and it is a property of the curated set -- inconsistent examples were chosen for being
    fluent and coherent, which is exactly what removes the easy surface cues.
  evidence: Appendix C (Response Length), Table 11
- id: chit-chat-is-the-failure-mode
  text: 'Q²''s known failure mode is chit-chat and opinion rather than factual error: no valid
    question could be generated for around 20% of randomly sampled responses against 6-8%
    of the annotated consistent and inconsistent ones, and a faithful response can be penalised
    when a question is generated from its non-factual part.'
  scope: The worked example is a response that used the knowledge correctly -- 'purple is
    my favorite color. it's between red and blue.' -- where one of two valid questions was
    'What is purple?', answered 'my favorite color' from the response and something else from
    the knowledge. The pronoun filter removes the clearest opinion cases but not this one.
    Unresolved pronouns referring to the dialogue history are the other cause of lost questions,
    and the authors report that a preliminary coreference step raised coverage. Separating
    chit-chat from knowledgeable content is named as future work, not solved here.
  evidence: Section 5.4 (Lack of Valid Questions), Section 5.4 (Qualitative Analysis), Section
    7
- id: interpretable-by-construction
  text: 'Q² returns more than a score: it emits each generated question, the answer span taken
    from the response and the answer the QA model found in the knowledge, so a low score can
    be traced to the specific span of the response that the grounding text does not support.'
  scope: A property of the pipeline rather than a measured result -- the paper demonstrates
    it with examples rather than evaluating the explanations. The localisation is only as
    good as the question generation, so a response whose questions were all filtered out gets
    a score from the end-to-end NLI fallback with no explanation attached.
  evidence: Section 5.4 (Qualitative Analysis)
- id: cost-of-running-it
  text: 'Q² is a pipeline of three neural models per response, and the paper reports it as
    slow: on 4 CPUs, scoring one 150-response split took roughly 1.5 to 2 hours, with a more
    efficient version named as future work.'
  scope: Per-response cost, not per-dataset, so it scales linearly and the figure is CPU-only
    2021 hardware -- a GPU or a batched reimplementation changes it entirely. The practical
    constraint on reuse is less the runtime than the pinned stack the released code was written
    against (transformers 3.2.0, allennlp 1.0.0, spaCy 2.3.2, torch 1.6.0, Python 3.7), since
    the NLI component depends on an AllenNLP model class.
  evidence: Appendix B, the released repository's prerequisites
- id: released-artifacts
  text: The released repository contains the annotated data as four CSV files of 150 responses
    each -- consistent and inconsistent, for MemNet and dodecaDialogue -- plus the cross-annotation
    file used for the agreement check, with the Wizard of Wikipedia episode index, turn, response,
    grounding knowledge and gold human response per row, alongside the pipeline scripts and
    the meta-evaluation code.
  scope: 'Provenance for anyone reusing the labels: rows point back into the WoW validation
    set by episode and turn, so the dataset is a labelling of existing dialogues rather than
    new dialogue collection. The 600 rows across the four files are the annotation targets;
    the 1,088 figure in the paper comes from extending each context''s annotation to both
    systems'' outputs. The scripts expect metric scores normalised to [0,1] when comparing
    a new metric against Q².'
  evidence: The released repository (README, third_party/data), Section 4
- id: position-among-metrics
  text: 'Q² is the first application of question-generation/question-answering evaluation
    to dialogue rather than summarisation, and its specific move against the closest prior
    metric is where lexical variability is tolerated: QuestEval handles it with the QA model''s
    answerability confidence and can only do so on its recall-oriented side, while Q²''s NLI
    comparison allows it on the precision-oriented side too.'
  scope: Positioning as the paper states it, with the summarisation lineage explicit -- recall-oriented
    QA evaluation from Eyal et al., precision-oriented consistency checking from Durmus et
    al. and Wang et al., both combined in QuestEval. Answerability confidence is insensitive
    to how an answer is worded but also blind to whether the QA model hallucinated it, which
    is the gap NLI comparison fills. BEGIN, a WoW-based groundedness benchmark with five labels
    that models the task as NLI, is concurrent work rather than a baseline here.
  evidence: Section 6 (Evaluation via Question Answering and Question Generation, Factual
    Consistency and Hallucinations), Section 1
qa:
- q:
  - How do I measure whether a chatbot's answer is faithful to its retrieved source?
  - How can I detect hallucination in a knowledge-grounded dialogue system?
  - What metric checks that a generated response matches the knowledge it was given?
  - How do you evaluate factual consistency in dialogue without reference responses?
  answers:
  - pipeline
  - reference-free-and-zero-shot
  - response-level-accuracy
- q:
  - What is Q squared, the dialogue evaluation metric?
  - How does the Q2 metric work?
  - What does Q² measure?
  answers:
  - pipeline
  - nli-instead-of-token-matching
  - interpretable-by-construction
- q:
  - Why compare answer spans with NLI instead of token overlap?
  - What does the NLI component add to a QG/QA consistency metric?
  - How much does NLI-based answer comparison help over exact match?
  answers:
  - nli-instead-of-token-matching
  - response-level-accuracy
  - topical-chat-correlation
- q:
  - Do factual consistency metrics agree with human judgement?
  - How well does Q² correlate with human ratings?
  - Is BLEU or BERTScore any good for measuring factual consistency?
  answers:
  - system-level-correlation
  - topical-chat-correlation
  - response-level-accuracy
- q:
  - Is there a dataset of dialogue responses labelled for factual consistency?
  - Where can I get human annotations of hallucination in Wizard of Wikipedia?
  - How was the Q² evaluation dataset built?
  answers:
  - annotated-dataset
  - released-artifacts
  - annotation-asked-for-groundedness-not-truth
- q:
  - How often do knowledge-grounded dialogue models contradict their knowledge?
  - What does hallucination look like in a QA-based consistency metric?
  - How do you tell invented content from contradicted content?
  answers:
  - hallucination-surfaces-as-unanswerable
  - separates-consistent-from-inconsistent
  - annotated-dataset
- q:
  - Do I need large models to run a QG/QA evaluation metric?
  - Can I use smaller question generation and question answering models in Q²?
  - Is Q² sensitive to the quality of its components?
  answers:
  - robust-to-component-size
  - decoding-and-filter-ablations
  - pipeline
- q:
  - When does Q² fail?
  - What are the limitations of QG/QA factual consistency metrics?
  - Does Q² penalise chit-chat or opinions?
  answers:
  - chit-chat-is-the-failure-mode
  - hallucination-surfaces-as-unanswerable
  - interpretable-by-construction
- q:
  - Can a factual consistency metric check persona consistency?
  - Does Q² work for Dialogue NLI or self-consistency?
  - How do you check that a chatbot stays consistent with its persona?
  answers:
  - dnli-accuracy
  - reference-free-and-zero-shot
- q:
  - Does Q² notice when the grounding document is completely wrong?
  - What score does Q² give for unrelated knowledge?
  - Can a consistency metric be fooled by plausible-sounding text?
  answers:
  - random-knowledge-sanity-check
  - length-is-not-the-signal
  - hallucination-surfaces-as-unanswerable
- q:
  - How expensive is it to run Q²?
  - Can I still run the Q² code today?
  - What does a QG/QA metric cost per response?
  answers:
  - cost-of-running-it
  - released-artifacts
  - robust-to-component-size
- q:
  - How is Q² different from QuestEval or FEQA?
  - What is the difference between Q² and BEGIN?
  - Which QA-based consistency metric should I use?
  answers:
  - position-among-metrics
  - nli-instead-of-token-matching
  - reference-free-and-zero-shot
- q:
  - What counts as an inconsistent dialogue response?
  - Does factual consistency mean the response is true?
  - How were annotators told to judge groundedness?
  answers:
  - annotation-asked-for-groundedness-not-truth
  - annotated-dataset
  - separates-consistent-from-inconsistent
- q:
  - Should I use beam search or greedy decoding for question generation in an evaluation metric?
  - Does filtering out opinion questions help a consistency metric?
  - What do the Q² ablations show?
  answers:
  - decoding-and-filter-ablations
  - chit-chat-is-the-failure-mode
  - pipeline
misreadings:
- 'Q² does not measure truth. It measures whether a response is consistent with the grounding
  text it was given, so a response can be factually correct about the world and still score
  0 because the knowledge does not support it -- and consistent with a false grounding passage
  and score 1. It is a groundedness metric, not a fact-checker, and the annotation guidelines
  say so explicitly: annotators were told to ignore their background knowledge.'
- The inconsistency rates in the released dataset -- 34.2% of contexts for dodecaDialogue
  and 50.36% for MemNet -- are not estimates of how often those systems hallucinate. The dataset
  was built by annotating until 150 consistent and 150 inconsistent responses had been collected
  per system and then extending each context to both systems, so it is balanced by construction
  and deliberately weighted toward hard cases.
- The 0.5 threshold and the 77.3% accuracy that goes with it are not a tuned operating point.
  The paper picked 0.5 arbitrarily to show that the score separates the two classes, and says
  explicitly that tuning it on a development split would likely do better. Absolute Q² values
  are also not comparable across systems or datasets -- only the ordering within one set is
  meaningful.
- The NLI comparison is an improvement, not the whole metric. Without it Q² still separates
  consistent from inconsistent responses (73.1% against 77.3% accuracy, 0.9711 against 0.9798
  system-level correlation); the NLI gain is clearest where the response and the knowledge
  say the same thing in different words, which is why it is larger on Topical-Chat than on
  Wizard of Wikipedia.
- The system-level result -- 0.9798 against BLEU's 0.3051 -- comes from simulated systems
  that differ only in what fraction of their responses are inconsistent, bootstrapped 1000
  times from 244 dialogue contexts. It shows the metric tracks hallucination rate; it is not
  a measured ranking of real dialogue systems, and every confidence interval reaches 1.
- Q² is not a chit-chat detector, and chit-chat is where it goes wrong. Around 20% of randomly
  sampled responses yield no valid question at all and fall back to end-to-end NLI, against
  6-8% of the annotated ones, and a response that used its knowledge faithfully can still
  be penalised for a question generated from its opinion clause. The pronoun filter mitigates
  this rather than solving it.
- Scoring 74.49% on Dialogue NLI does not make Q² an NLI system. It is applied zero-shot with
  a threshold tuned on the development split, with the pronoun filter switched off, and with
  neutral pairs deliberately counted as inconsistent because an ungrounded persona utterance
  is a dialogue failure even when it is not a logical contradiction.
- The near-zero scores on randomly swapped knowledge (0.02 and 0) are a floor check, not evidence
  of fine-grained sensitivity. They show the score comes from the grounding text rather than
  from generic fluency; the errors the metric is actually for are subtle alterations of correct
  knowledge, which sit far above that floor.
- The ablation table is cumulative, not one-factor-at-a-time. The row without the personal-pronoun
  filter also uses greedy decoding, so comparing it with full Q² attributes both changes to
  the filter. Read against the greedy row, dropping the filter lowers the score on every split.
terminology:
  Q²: 'The metric introduced here: question generation plus question answering plus NLI-based
    answer comparison, scoring how consistent a dialogue response is with its grounding text.
    Both Qs are the two stages -- questions asked of the response, then of the knowledge.'
  factual consistency: Used throughout in the narrow sense of agreement with the specific
    grounding text supplied to the model, not correctness about the world. The paper's failures
    of consistency include contradiction and invention alike, both scored 0.
  informative span: A named entity or noun phrase in the response, found with spaCy, used
    as the target answer for question generation. Choosing these spans is what decides which
    parts of a response get checked -- and what makes opinion clauses a failure mode.
  question coverage: The percentage of responses for which at least one generated question
    survived filtering, so the score came from the QG/QA pipeline rather than from the end-to-end
    NLI fallback. Reported because it is what degrades when components get smaller or when
    questions are generated greedily.
  Q² w/o NLI: 'The ablation, not a separate metric: answer spans are compared by token-level
    F1 instead of NLI, which is what earlier question-based summarisation metrics did. Used
    throughout as the baseline that isolates the paper''s contribution.'
  E2E NLI: The strongest non-question baseline -- the same RoBERTa-SNLI model run once over
    the whole response against the whole knowledge passage, with the response as hypothesis.
    Also Q²'s own fallback when no question survives filtering.
  MemNet / dodecaDialogue: 'The two Wizard of Wikipedia systems whose outputs were annotated:
    the memory-network model released with the dataset, and the multi-task model from the
    dodecaDialogue benchmark, both decoded with beam size 10 in ParlAI. They are the source
    of the annotated responses, not systems the paper proposes.'
  QuestEval: The closest prior QG/QA metric, for summarisation, which combines recall- and
    precision-oriented question checking and handles wording differences using the QA model's
    answerability confidence. Q²'s contrast with it is that NLI-based span comparison extends
    that tolerance to the precision side.
  BEGIN: A concurrent WoW-based benchmark for groundedness that frames the task as NLI with
    five labels (entailment, contradiction, hallucination, off-topic, generic). Concurrent
    work in this paper's related-work section, not a baseline it is compared against.
links_extra:
  code and the annotated dataset: https://github.com/orhonovich/q-squared
  the four annotated CSV files: https://github.com/orhonovich/q-squared/tree/main/third_party/data
  the published version (cite this): https://aclanthology.org/2021.emnlp-main.619/
  preprint: https://arxiv.org/abs/2104.08202
  Wizard of Wikipedia, the dialogues the labels point into: https://parl.ai/projects/wizard_of_wikipedia/
---
