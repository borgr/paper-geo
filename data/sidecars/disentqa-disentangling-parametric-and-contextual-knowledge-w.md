---
key: neeman2023disentqa
coined: DisentQA
gloss: question answering that outputs two separate answers, one from the given passage and
  one from the model's memorized knowledge
one_liner: DisentQA trains a single generative QA model to emit two answers at once — one
  grounded in the given passage and one from its parametric memory — using counterfactual
  and unanswerable-context data augmentation on Natural Questions.
claims:
- id: paradigm
  kind: context
  text: DisentQA introduces a QA paradigm in which one generative model outputs two answers
    per question. One answer is grounded in the given passage and the other comes from the
    model's memorized knowledge, so a reader can tell which source an answer came from.
  scope: Natural Questions with fine-tuned T5-Large (770M) and T5-11B, gold passages only;
    the authors state it is the first work to combine multiple answers, counterfactual augmentation
    and answerability augmentation, with concurrent work by Li et al. (2022).
- id: robustness
  text: Combining counterfactual and answerability augmentation raises contextual-answer accuracy
    on counterfactual Natural Questions contexts to 84.98% for the single-answer T5-11B model,
    versus 66.81% for the vanilla factual-only model.
  evidence: Table 4
  scope: T5-11B fine-tuned on NQ examples that have both a gold passage and a short answer;
    counterfactual contexts built by entity substitution, so only named-entity answers are
    covered.
  kind: result
- id: no-cost
  text: Adding the second, parametric answer costs almost nothing on standard grounded QA.
    The multi-answer T5-11B model trained on all augmentations reaches 78.10% on the factual
    NQ test set, against 78.32% for its single-answer counterpart and 79.34% for the vanilla
    model.
  evidence: Table 4
  scope: T5-11B, gold-passage NQ, exact-match accuracy; the test set is restricted to the
    1,365 examples that induced the counterfactual set.
  kind: result
- id: answerability
  text: The T5-11B multi-answer model trained with both counterfactual and answerability data
    predicts "unanswerable" for 99.49% of random contexts. The same multi-answer model trained
    without counterfactual data reaches only 35.60%.
  evidence: Table 5
  scope: T5-11B; all models score 100% on empty contexts, so the difficulty is confined to
    randomly sampled contexts, which the authors call a simplistic proof-of-concept because
    the random passage is unrelated in topic and entities.
  kind: result
- id: separation
  text: The T5-11B model trained on factual, counterfactual and answerability examples gives
    identical contextual and parametric answers in only 18.46% of counterfactual cases, while
    models missing either augmentation stay above 92%.
  evidence: Table 6
  scope: T5-11B on the 1,365-example counterfactual NQ test set; on factual contexts the same
    model's two answers agree 93.55% of the time, which is the desired behaviour there.
  kind: result
- id: complementary
  text: 'Counterfactual augmentation and answerability augmentation are complementary rather
    than redundant in DisentQA: neither alone produces disentangled answers or reliable abstention,
    and only their combination achieves both.'
  evidence: Tables 4, 5 and 6
  scope: Shown for T5-11B and replicated in trend for T5-Large on NQ with gold passages; not
    tested on question types outside named-entity answers.
  kind: result
- id: parametric-quality
  text: The fully augmented multi-answer T5-11B model answers 31.14% of empty-context NQ questions
    correctly from parametric knowledge, 3.5 points above the 27.69% closed-book baseline
    trained only to answer from parameters.
  evidence: Table 7
  scope: T5-11B, exact match on the NQ dev-derived test set; the authors note it is not clear
    why a model trained on both knowledge sources should beat the closed-book model in this
    setting.
  kind: result
- id: context-leakage
  text: Parametric answers in DisentQA models are not context-independent. The fully augmented
    T5-11B model scores 44.69% parametric accuracy on counterfactual contexts, 31.14% on empty
    and 30.18% on random contexts.
  evidence: Table 7
  scope: T5-11B; the higher counterfactual number suggests the model picks up hints from the
    altered passage, and manual inspection finds leakage in both directions between contextual
    and parametric answers.
  kind: result
- id: answer-overlap
  text: Much of the apparent parametric knowledge in DisentQA models is answer overlap with
    fine-tuning data. On the No-Answer-Overlap dev subset the fully augmented T5-11B model's
    parametric accuracy drops by 23.74 points on empty contexts and 31.97 points on counterfactual
    contexts.
  evidence: Table 8
  scope: T5-11B, drops measured against the full dev set; NAO subsets defined following Lewis
    et al. (2021) as reference answers absent from the training data, and accuracy stays non-zero
    everywhere.
  kind: result
- id: unseen-answers
  text: Only 18% of the fully augmented T5-11B model's parametric answers on the counterfactual
    test set were never seen as answers during fine-tuning, indicating a strong tendency to
    reuse fine-tuning answers. Of those unseen answers, 85% differ from the contextual answer.
  evidence: Section 5.4
  scope: T5-11B on the counterfactual test set; comparable figures are 25% for the answerability-only
    multi-answer model, 26% for the counterfactual-only one and 23% for the closed-book baseline.
  kind: result
- id: model-size
  text: The disentanglement trends of DisentQA hold at 770M parameters but weaker. T5-Large's
    fully augmented multi-answer model reaches 81.03% contextual accuracy on counterfactual
    contexts and 22.34% parametric accuracy on empty contexts.
  evidence: Tables 10 and 12
  scope: T5-Large (770M) versus T5-11B on NQ, where T5-11B is better in all reported cases;
    no significance testing was run across random initializations because of model size.
  kind: result
qa:
- ask:
    plain: can a question answering system tell me whether its answer came from the document
      or from what it already knew?
    jargon: how can a generative reader disentangle contextual knowledge from parametric knowledge
      at inference time?
    task: how do I get a QA model to return both a passage-grounded answer and a memory-based
      answer for the same question?
    practitioner: if my retrieval QA system contradicts the retrieved passage, can I see which
      answer came from the model's own memory?
  answered_by:
  - paradigm
- ask:
    plain: what should I read first about question answering models trusting their own memory
      instead of the document they are given?
    jargon: which work introduced a framework for separating parametric and contextual knowledge
      in generative open-domain QA?
    task: where do I start reading about knowledge conflicts between a retrieved passage and
      a model's memorized facts?
    practitioner: is there a paper I can cite when I argue that a QA model should expose whether
      an answer came from the passage or from pretraining?
  answered_by:
  - paradigm
- ask:
    plain: does training on passages with edited facts make a QA model follow the document
      instead of its memory?
    jargon: how much does counterfactual augmentation on Natural Questions improve contextual
      answer accuracy under knowledge conflict?
    task: how do I make a reader model stick to the retrieved passage when the passage contradicts
      what the model memorized?
    practitioner: should I add counterfactually edited passages to my fine-tuning data to
      stop my QA model ignoring retrieved evidence?
  answered_by:
  - robustness
  - complementary
- ask:
    plain: does making a question answering model give two answers instead of one make it
      worse at normal questions?
    jargon: what is the accuracy penalty on the standard factual NQ test set for a multi-answer
      decoder versus a single-answer baseline?
    task: how do I add a memory-based answer to my QA output without losing accuracy on ordinary
      grounded questions?
    practitioner: if I switch my QA model to predict two answers, what do I give up on my
      regular benchmark numbers?
  answered_by:
  - no-cost
- ask:
    plain: can a question answering model recognise that the passage it was given has nothing
      to do with the question?
    jargon: what unanswerable-prediction rate is reached on random contexts, and does answerability
      augmentation alone suffice for abstention?
    task: how do I train a reader to abstain when the retrieved passage is irrelevant to the
      question?
    practitioner: if I only add unanswerable examples to my training data, will my QA model
      learn to say it cannot answer?
  answered_by:
  - answerability
  - complementary
- ask:
    plain: when training a QA model to separate document facts from remembered facts, is one
      kind of extra training data enough or are two needed?
    jargon: are counterfactual and answerability augmentations complementary or redundant
      for disentangling contextual and parametric answers?
    task: which training augmentations do I need to combine to get both source separation
      and reliable abstention from one reader model?
    practitioner: can I skip the counterfactual passages and just train on unanswerable examples,
      or do I need both?
  answered_by:
  - complementary
  - separation
- ask:
    plain: when the passage has been edited to say something false, how often does a two-answer
      QA model give the same answer twice?
    jargon: how is answer disentanglement quantified on counterfactual NQ, and what identical-answer
      rate does the best T5-11B configuration reach?
    task: how do I check whether a model's two answers are genuinely coming from different
      knowledge sources rather than being copies?
    practitioner: how do I know the memory-based answer my model outputs is not just a duplicate
      of the passage-grounded one?
  answered_by:
  - separation
- ask:
    plain: is the answer a model gives from memory as good as one from a model trained only
      to answer without any document?
    jargon: how does empty-context parametric accuracy on NQ compare with a closed-book fine-tuned
      T5 baseline?
    task: how do I get usable closed-book answers out of the same model I use for reading
      passages?
    practitioner: if I want closed-book answers too, can one two-answer model replace a separate
      closed-book QA model?
  answered_by:
  - parametric-quality
- ask:
    plain: does the answer a model gives from memory stay the same no matter which passage
      you show it?
    jargon: is the parametric prediction of a disentangled reader actually independent of
      the input context?
    task: how do I test whether the passage I supply is leaking into the answer that is supposed
      to come from the model's memory?
    practitioner: can I treat the memory-based answer from my two-answer QA model as a context-independent
      probe of what the model knows?
  answered_by:
  - context-leakage
- ask:
    plain: how much of a QA model's memory-based accuracy is just repeating answers it saw
      during training?
    jargon: how much parametric accuracy on NQ survives on a no-answer-overlap subset, and
      what fraction of parametric predictions are unseen answers?
    task: how do I tell real memorized knowledge from answer-string overlap when I evaluate
      closed-book accuracy?
    practitioner: should I trust my closed-book Natural Questions numbers, or check for answer
      overlap with fine-tuning data first?
  answered_by:
  - answer-overlap
  - unseen-answers
- ask:
    plain: do you need a very large model to keep the document-based and memory-based answers
      apart?
    jargon: do the disentanglement trends hold at 770M parameters, or do contextual and parametric
      accuracies degrade with model scale?
    task: how small a T5 can I fine-tune and still get separate passage-grounded and memory-based
      answers?
    practitioner: I can only afford a 770M-parameter model, will it still learn to output
      two distinct answers?
  answered_by:
  - model-size
misreadings:
- 'A high parametric-answer accuracy in DisentQA is not evidence of recalled pretraining knowledge:
  only 18% of the fully augmented T5-11B model''s parametric answers on the counterfactual
  test set were unseen during fine-tuning, and No-Answer-Overlap accuracy is far lower.'
- 'DisentQA''s parametric answer is not independent of the input passage: the fully augmented
  T5-11B model''s parametric accuracy varies from 30.18% on random contexts to 44.69% on counterfactual
  ones.'
- 'Answerability augmentation alone does not teach abstention on irrelevant passages: the
  multi-answer T5-11B model trained on empty and random contexts without counterfactual data
  predicts "unanswerable" for only 35.60% of random contexts.'
- The counterfactual data augmentation in DisentQA applies only to questions whose answers
  are named entities, so knowledge conflicts on other question types, such as Boolean questions,
  are outside the method as evaluated.
- DisentQA's results assume an oracle retriever, since the factual contexts are the NQ gold
  passages rather than retrieved ones.
terminology:
  parametric knowledge: factual knowledge encoded in a language model's weights during pretraining,
    as opposed to knowledge supplied in the input at inference time.
  contextual knowledge: knowledge supplied to a QA model at inference time in the question's
    context passage, such as a retrieved Wikipedia paragraph.
  answer separation: the percentage of test cases in which a model's contextual and parametric
    answers are identical, used as a measure of how far the two knowledge sources have been
    disentangled; lower is better on counterfactual data and higher on factual data.
  counterfactual example: a QA example whose context has had every occurrence of the answer
    entity replaced by a different entity of the same type, so that the correct context-grounded
    answer contradicts the original memorized answer.
  answerability augmentation: training examples in which the context is replaced by an empty
    or randomly sampled passage and the target contextual answer is the special token "unanswerable".
  No Answer Overlap (NAO): the subset of a test set whose reference answers never appear as
    answers in the training data, used to control for artifacts from repeated answers.
links_extra:
  code: https://github.com/ellaneeman/disent_qa
---
