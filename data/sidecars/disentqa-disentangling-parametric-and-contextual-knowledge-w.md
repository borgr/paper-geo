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
    practitioner: How can a QA model tell me whether its answer came from the retrieved passage
      or from what it memorized?
    unsorted:
    - Is there a way to separate a language model's memorized facts from the passage it was
      given at inference time?
    - What is DisentQA?
  answered_by:
  - paradigm
- ask:
    practitioner: What should I read about knowledge conflicts between a retrieved document
      and a model's memory?
    unsorted:
    - Which paper established a way to evaluate whether QA answers are grounded in context
      or in parameters?
    - Where should I start reading about parametric versus contextual knowledge in question
      answering?
  answered_by:
  - paradigm
- ask:
    unsorted:
    - Does counterfactual data augmentation make QA models follow the passage instead of their
      memory?
    - How much does robustness to knowledge conflicts improve with counterfactual training
      on Natural Questions?
    - What accuracy do DisentQA models get on counterfactual contexts?
  answered_by:
  - robustness
  - complementary
- ask:
    unsorted:
    - Does asking a QA model for two answers hurt its normal accuracy?
    - Is there a cost on standard grounded QA to also predicting a parametric answer?
    - How does the multi-answer model compare to a vanilla T5 QA model on factual Natural
      Questions?
  answered_by:
  - no-cost
- ask:
    unsorted:
    - How well can a QA model say 'unanswerable' when the passage is irrelevant?
    - Does training on unanswerable examples alone teach a model to abstain?
    - What abstention accuracy does DisentQA reach on random contexts?
  answered_by:
  - answerability
  - complementary
- ask:
    unsorted:
    - Do the two augmentations in DisentQA each work on their own, or are both needed?
    - Is counterfactual augmentation enough for disentanglement without answerability examples?
    - Why does DisentQA use both counterfactual and unanswerable training examples?
  answered_by:
  - complementary
  - separation
- ask:
    unsorted:
    - How often do the contextual and parametric answers actually differ when the passage
      is altered?
    - How is disentanglement measured in DisentQA, and what score does the best model get?
    - What is answer separation on counterfactual Natural Questions examples?
  answered_by:
  - separation
- ask:
    unsorted:
    - Is the parametric answer any good compared with a closed-book QA model?
    - How accurate are memory-based answers from a model trained to output two answers?
    - Does DisentQA's parametric answer beat a closed-book T5 baseline on Natural Questions?
  answered_by:
  - parametric-quality
- ask:
    unsorted:
    - Does the parametric answer stay the same regardless of the passage given?
    - Can the provided context leak into a model's supposedly memory-based answer?
    - Why do DisentQA parametric answers change across empty, random and counterfactual contexts?
  answered_by:
  - context-leakage
- ask:
    unsorted:
    - How much of a QA model's parametric accuracy is just answers repeated from fine-tuning
      data?
    - What happens to parametric answer accuracy on questions whose answers never appear in
      training?
    - Does answer overlap inflate closed-book QA results on Natural Questions?
  answered_by:
  - answer-overlap
  - unseen-answers
- ask:
    unsorted:
    - Does model size matter for disentangling contextual and parametric knowledge?
    - How do T5-Large and T5-11B compare on DisentQA's disentanglement metrics?
    - Is 770M parameters enough to learn to output separate contextual and parametric answers?
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
