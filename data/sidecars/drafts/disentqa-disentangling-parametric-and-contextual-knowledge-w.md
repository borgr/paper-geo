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

Then promote it:  python scripts/draft_sidecars.py --accept disentqa-disentangling-parametric-and-contextual-knowledge-w
-->
---
coined: DisentQA
gloss: a question answering setup where one model emits two answers at once -- one grounded
  in the passage it was given, one from its own weights -- so the source of an answer is visible
one_liner: 'DisentQA trains one QA model to emit a contextual answer and a parametric answer
  in a single output: counterfactual and answerability augmentation together lift accuracy
  under knowledge conflict from 66.81% to 84.98% and leave the two answers identical on only
  18.46% of counterfactual cases, while neither alone works.'
claims:
- id: two-answers-in-one-output
  text: 'DisentQA trains a single generative QA model to decode two answers to one question
    in one output sequence, formatted "contextual: <contextual answer>, parametric: <parametric
    answer>", so a reader can see whether an answer came from the supplied passage or from
    the weights, and whether the two agree.'
  scope: 'A property of the output format and the training data, not of the model''s internals
    -- nothing inspects the weights, and a footnote concedes that calling a token predictor''s
    stored regularities "knowledge" is anthropomorphic. The parametric answer is supervised
    to be the original dataset answer in every example type, so "parametric" means "the answer
    to give when the context is empty, irrelevant or altered", not a read-out of what the
    weights contain. Implemented by fine-tuning T5 (770M and 11B) with T5X: greedy decoding,
    50k steps, batch 32, constant learning rate 1e-4, best checkpoint chosen on the factual
    validation set.'
  evidence: Section 2.1, Section 3.4, Table 3, Appendix B, footnote 2
- id: augmentations-are-complementary
  text: 'The two augmentations are complementary rather than interchangeable: the model trained
    on both is the only one that both abstains on irrelevant context (99.34% and 99.49%, against
    27.69% and 35.60% for the answerability-only models) and keeps its two answers apart under
    conflict (identical on 18.46% of counterfactual examples, against 99.71% for answerability-only
    and 92.45% for counterfactual-only).'
  scope: '"Complementary" is the authors'' reading of a pattern across Tables 4-6, not a measured
    interaction term -- no ablation isolates why one augmentation makes the other work. The
    mechanism the error analysis points to is copying: when the answerability-only model fails
    to abstain it emits the same string as both answers, so it never learned two channels
    at all, and in 176 of its 879 failures that string came from the irrelevant context. Reported
    for T5-11B; the T5-Large models in Appendix C show the same ordering at lower absolute
    values.'
  evidence: Section 4.2, Section 4.3, Section 4.4, Tables 4-6, Section 5.3 (Error Analysis)
- id: robustness-to-knowledge-conflicts
  text: On counterfactual test examples, where the passage has been edited so that the grounded
    answer contradicts the original one, contextual answer accuracy rises from 66.81% for
    the vanilla single-answer model to 79.63% with counterfactual augmentation and 84.98%
    with counterfactual plus answerability augmentation -- a further 5.35 points from data
    that is not about knowledge conflict at all.
  scope: 'Exact Match on 1,365 altered Natural Questions dev examples, scored against the
    altered (expected) answer. The two-answer variant lands in the same place (84.91%), so
    the gain comes from the training data rather than from emitting a parametric answer. One
    configuration falls below the vanilla baseline: the two-answer answerability-only model
    scores 64.62%. The paper''s own limitations section notes that part of the high counterfactual
    accuracy may be the model detecting that substituted passages read unnaturally, rather
    than following the context on its merits.'
  evidence: Section 4.2, Table 4, Appendix A
- id: answerability-needs-counterfactual-data
  text: 'Abstaining on an empty context is trivial -- every model trained for it predicts
    "unanswerable" 100% of the time -- but abstaining on a randomly substituted context is
    not: the answerability-only models manage 27.69% and 35.60%, while adding counterfactual
    data to the same recipe raises this to 99.34% and 99.49%.'
  scope: Answerability here is accuracy at emitting the literal "unanswerable" token as the
    contextual answer, so it measures an output convention, not a calibrated confidence. The
    random contexts are sampled from elsewhere in the corpus and share neither topic nor entities
    with the question; the authors call this simplistic and a proof of concept, and leave
    plausible-looking distractors to future work. Section 4.3's prose says "more than 99%"
    for the empty case where Table 5 reports 100.00 -- prefer the table.
  evidence: Section 4.3, Table 5, Appendix A
- id: answer-separation-on-counterfactual
  text: 'The fully augmented model separates its two answers where it should and merges them
    where it should: on counterfactual examples the contextual and parametric answers are
    identical in only 18.46% of cases, on factual examples they are identical in 93.55%, and
    on empty or random contexts in 0% and 0.29%.'
  scope: Watch the direction. The metric is named Answer Separation and defined in Section
    3.3 as the percentage of cases where the two answers differ, but Table 6 reports the complement
    -- the percentage where they are identical -- so 18.46% means high separation, and lower
    is better in the counterfactual, empty and random columns. String identity is the test,
    so a paraphrase or a partial name counts as a difference. The 93.55% on factual data is
    lower than the 99.9% of the two ablations, which the paper reads as better disentanglement
    rather than worse agreement, since imitating the contextual answer is the easy path.
  evidence: Section 3.3, Section 4.4, Table 6
- id: parametric-answers-mostly-repeat-finetuning-answers
  text: 'Most of the apparent parametric knowledge is answer overlap with the fine-tuning
    data: restricted to dev examples whose answer never appears as an answer in training,
    the fully augmented model''s parametric accuracy falls from 44.69% to 12.72% on counterfactual
    contexts and from 31.14% to 7.40% on empty ones, while the closed-book baseline falls
    from 27.69% to 9.76%.'
  scope: 'The No Answer Overlap split follows Lewis et al. (2021) and is the harder half by
    construction; every number stays non-zero, so pretraining does contribute something. A
    second measurement agrees: on the counterfactual test set, 18% of the fully augmented
    model''s parametric answers were never seen as an answer during fine-tuning (against 23%
    for closed-book and 25% and 26% for the ablations), and 85% of that 18% differed from
    the contextual answer. The paper''s own conclusion is that the models do surface parametric
    answers from pretraining but have a strong tendency to repeat fine-tuning answers. Two
    qualifiers on those unseen-answer percentages: for the counterfactual-only model most
    of its 26% are identical to its own contextual answer, so the figure does not indicate
    a separate channel at all; and manual inspection of the fully augmented model''s unseen
    answers found some that are correct about the world while contradicting the supplied context,
    which is the clearest evidence in the paper that anything is being recalled from pretraining.'
  evidence: Section 5.1, Table 8, Section 5.4
- id: contextual-quality-is-preserved
  text: 'Adding a second answer costs almost nothing on the standard task: contextual answer
    accuracy on unaltered Natural Questions stays between 78.10% and 80.81% across all seven
    models, the single-to-multi answer change moves it by at most 0.6 points, and counterfactual
    augmentation slightly improves on the vanilla model (80.73% against 79.34%).'
  scope: 'Exact Match on the restricted test set of 1,365 examples, so not comparable to published
    NQ numbers. Answerability augmentation is where the small cost sits -- 78.32% and 78.10%
    for the two fully augmented models -- and the error analysis attributes 8 of 73 regressions
    to the model predicting "unanswerable" when the context did contain the answer. The seven
    models are single training runs: no repeated seeds, no hyperparameter search, with consistency
    across the two model sizes offered as the substitute for significance testing.'
  evidence: Section 4.1, Table 4, Section 5.3, Appendix A, Appendix B
- id: parametric-answer-leaks-from-context
  text: 'The parametric answer is not independent of the context it is supposed to ignore:
    for the fully augmented model its accuracy is 74.87% given the factual passage, 44.69%
    given a counterfactual one, 31.14% given an empty one and 30.18% given a random one, where
    a genuinely separate channel would score the same everywhere.'
  scope: 'Leakage runs both ways and the paper shows an example of each -- a substituted entity
    appearing verbatim in the parametric answer, and a parametric answer overriding a substituted
    context. The factual column is marked "?" rather than "up is better" in Table 7 because
    scoring high there mostly means imitating the contextual answer: the two ablations that
    copy score 80.37% and 80.22%, above the fully augmented model. Counterfactual contexts
    scoring above empty or random ones is read as the model taking hints from the altered
    passage.'
  evidence: Section 4.5, Table 7, Table 9, Section 5.3 (Disentanglement)
- id: beats-the-closed-book-baseline
  text: 'Trained with all the augmentations, the two-answer model recalls the original answer
    from an empty context better than a closed-book model trained for exactly that task: 31.14%
    against 27.69%, an improvement of about 3.5 points.'
  scope: 'The paper says plainly that it is not clear why a model trained to use both knowledge
    sources should beat a dedicated closed-book model here, and offers no mechanism. The margin
    is small and largely overlap-driven: on the No Answer Overlap split both drop sharply
    and the ordering reverses (7.40% against 9.76%). Both are T5-11B; the T5-Large closed-book
    baseline scores 10.26%, and excluding tabular contexts moves both down rather than up.'
  evidence: Section 4.5, Table 7, Table 8, Table 10, Table 15
- id: dataset-and-augmentation-construction
  text: 'The training data is four parallel derivations of the same Natural Questions examples:
    85,540 factual, 30,653 counterfactual, 85,540 empty-context and 85,540 random-context
    training examples, with 1,365 test examples of each type, always using the gold passage
    as the context.'
  scope: Only the 35% of NQ examples that have both a gold passage and a short answer are
    used, and an example qualifies if at least one of five annotators judged the passage suitable
    for answering. Counterfactuals follow Longpre et al. (2021)'s corpus-substitution policy
    -- every occurrence of the answer entity in the passage is replaced by another answer
    of the same entity type sampled from the same corpus -- which is why there are far fewer
    of them. No new questions are introduced; all four sets derive from questions already
    in the split, and the test set is cut down to the examples that admitted a counterfactual
    so the four conditions stay comparable. Always supplying the gold passage assumes an oracle
    retriever.
  evidence: Section 3.1, Section 3.2, Table 2, Appendix A
- id: what-is-new-and-what-is-borrowed
  text: 'The paper''s novelty claim is the combination, not any one part: it says it is the
    first to put multiple answers, counterfactual augmentation and answerability augmentation
    together to encourage and evaluate disentanglement, and to show those approaches are complementary.
    Counterfactual substitution is Longpre et al. (2021)''s, who defined knowledge conflicts
    and proposed substitution augmentation as the mitigation; the closed-book baseline is
    Roberts et al. (2020)''s setup and the answer-overlap split is Lewis et al. (2021)''s.'
  scope: Two pieces of the related work bear directly on the results rather than just crediting
    them. Yatskar (2019) found SQuAD 2.0's unanswerable questions to be mostly cases of extreme
    confusion and therefore easy to detect, and Sulem et al. (2021) built harder ones -- which
    is the same weakness the authors concede in their own topically unrelated random contexts,
    and they do not use the harder resource. Kim et al. (2021)'s unanswerable NQ subset, questions
    with failed presuppositions, is stated not to overlap with this data. Li et al. (2022)
    is named as concurrent work exploring similar ideas and is not compared against. The knowledge-editing
    line (Zhu et al. 2020, De Cao et al. 2021, Verga et al. 2021) and the fact-localisation
    line (Dai et al. 2022, Meng et al. 2022) attack the same problem from the other side,
    by changing or locating what the weights store rather than making both sources visible
    in the output; neither is a baseline here.
  evidence: Section 6, Appendix A
- id: named-entity-answers-only
  text: 'The method''s reach is bounded by its augmentation: counterfactual examples can only
    be generated for questions whose answer is a named entity, so knowledge conflicts in Boolean
    questions, or in any answer that is not a substitutable entity, fall outside the framework
    and would need a different augmentation.'
  scope: The authors' own first stated limitation. It bounds the augmentation rather than
    the two-answer output format, which needs no substitution and could in principle be trained
    on any QA data that supplies a parametric target. Extending it to other question types
    is named as required future work, not sketched.
  evidence: Appendix A, Section 3.2
- id: oracle-retrieval-and-easy-unanswerables
  text: 'Two setup choices make this a controlled study rather than a deployment result: the
    context is always the gold passage, so there is no retrieval error to survive, and the
    unanswerable examples are empty or topically unrelated passages, which the authors themselves
    call simplistic and a proof of concept.'
  scope: 'Named as limitations by the authors, not inferred. They add a third: the strong
    counterfactual results may partly reflect the model noticing that substituted passages
    read unnaturally, though they judge this minor given the small gap between factual and
    counterfactual accuracy. A fourth open question is what makes a case easy or hard to disentangle
    -- possibly how often the fact appears in pretraining data -- which they leave to future
    work.'
  evidence: Appendix A
- id: tabular-contexts-depress-every-number
  text: '27% of the test contexts are tables rather than prose, and they carry much of the
    residual contextual error: excluding them raises the fully augmented model''s contextual
    accuracy from 78.10% to 86.19% on factual examples and from 84.91% to 96.37% on counterfactual
    ones, while its parametric accuracy barely moves (44.69% to 44.86% on counterfactual contexts).'
  scope: 'The 27% is the complement of the table caption''s statement that 73% of the data
    did not include tables, and the split is by whether the context contains a table at all,
    not by whether the answer sits in it. The lift is not uniform: the closed-book baseline''s
    parametric accuracy on empty contexts falls from 27.69% to 25.40% and the fully augmented
    model''s from 31.14% to 28.53% when tables are excluded, so this is a re-scoring on an
    easier subset rather than a correction. The manual error analysis found that half of the
    33 genuinely wrong context-derived answers involved a table, a numeric answer, or an unclear
    question.'
  evidence: Table 14, Table 15, Section 5.3 (Error Analysis)
- id: bigger-model-more-parametric-knowledge
  text: 'Model size is treated as the lever on how much parametric knowledge is available
    at all: T5-11B beats T5-Large in every configuration with the same ordering between variants,
    and the closed-book baseline''s accuracy from an empty context is 27.69% at 11B against
    10.26% at 770M.'
  scope: Two sizes, one run each, so this is a direction rather than a scaling curve; the
    paper explicitly declines significance testing because of the model sizes involved and
    offers agreement of trends across the two sizes instead. The T5-Large results do show
    the augmentations mattering the same way -- 33.99% answer similarity on counterfactual
    examples for the fully augmented model against 99.71% for answerability-only. Each 11B
    run took 10 TPU hours, with no hyperparameter search.
  evidence: Section 3.4, Section 5.2, Appendix B, Tables 10-13
- id: error-analysis-of-the-factual-regression
  text: 'The fully augmented model''s 1-2 point drop on unaltered examples is mostly not a
    knowledge failure: of the 73 cases where it failed and the vanilla model succeeded, 14
    were correct answers scored zero by Exact Match (for instance "Napoleon" against the reference
    "Napoleon Bonaparte"), 8 were wrong abstentions, 6 had more than one valid answer, 12
    answers came from outside the context, and 33 were wrong answers taken from the context.'
  scope: 'A manual analysis of one model pair in one direction of disagreement, so it explains
    the regression rather than measuring either model''s overall error composition. What it
    does show is how much of the gap is a scoring artefact: about a third of these failures
    -- the 14 correct-but-zero plus the 6 alternative-valid-answer cases -- are not errors
    a reader would count. Half of the 33 context-derived wrong answers involve a tabular context,
    a numeric answer or an unclear question.'
  evidence: Section 5.3 (Error Analysis)
qa:
- q:
  - How can I tell whether a RAG answer came from the retrieved passage or from the model's
    memory?
  - How do I know if a generated answer is grounded in the context I supplied?
  - Can a QA model show which knowledge source its answer came from?
  - How do I make a QA model's answer attributable to its source?
  answers:
  - two-answers-in-one-output
  - answer-separation-on-counterfactual
  - parametric-answer-leaks-from-context
- q:
  - What is DisentQA?
  - What does it mean to disentangle parametric and contextual knowledge?
  - How does the DisentQA method work?
  answers:
  - two-answers-in-one-output
  - augmentations-are-complementary
  - dataset-and-augmentation-construction
- q:
  - How do I stop a QA model from ignoring the retrieved passage in favour of its memorized
    answer?
  - How do you handle knowledge conflicts between a model's memory and its context?
  - What fixes a model that answers from stale parametric knowledge instead of the given document?
  - Does counterfactual data augmentation make QA models follow the context?
  answers:
  - robustness-to-knowledge-conflicts
  - augmentations-are-complementary
  - contextual-quality-is-preserved
- q:
  - How do I train a model to abstain when the retrieved context is irrelevant?
  - How do you teach a QA model to say a question is unanswerable from the given passage?
  - Why does my model still answer when the retrieved passage has nothing to do with the question?
  answers:
  - answerability-needs-counterfactual-data
  - augmentations-are-complementary
  - oracle-retrieval-and-easy-unanswerables
- q:
  - Does adding counterfactual or answerability data hurt normal QA accuracy?
  - What is the cost of training a QA model to produce two answers?
  - Is there a tradeoff between robustness to knowledge conflict and standard accuracy?
  answers:
  - contextual-quality-is-preserved
  - error-analysis-of-the-factual-regression
  - robustness-to-knowledge-conflicts
- q:
  - Do language models actually know facts, or are they repeating answers from fine-tuning?
  - How much of closed-book QA accuracy is answer overlap with the training data?
  - Is parametric knowledge in QA models real memorization from pretraining?
  answers:
  - parametric-answers-mostly-repeat-finetuning-answers
  - beats-the-closed-book-baseline
  - bigger-model-more-parametric-knowledge
- q:
  - How do you measure whether a model separated its knowledge sources?
  - What metric shows that two generated answers come from different sources?
  - How is answer separation computed and which direction is better?
  answers:
  - answer-separation-on-counterfactual
  - parametric-answer-leaks-from-context
  - parametric-answers-mostly-repeat-finetuning-answers
- q:
  - How do I build counterfactual QA training data?
  - How do you generate examples where the context contradicts the memorized answer?
  - What is entity substitution for knowledge conflict data?
  answers:
  - dataset-and-augmentation-construction
  - named-entity-answers-only
  - robustness-to-knowledge-conflicts
- q:
  - What are the limitations of DisentQA?
  - When does counterfactual augmentation for knowledge conflict not apply?
  - What does this approach not cover?
  answers:
  - named-entity-answers-only
  - oracle-retrieval-and-easy-unanswerables
  - parametric-answers-mostly-repeat-finetuning-answers
- q:
  - Does model size matter for parametric knowledge in QA?
  - Is an 11B model much better than a 770M one at closed-book QA?
  - How does scale affect knowledge disentanglement?
  answers:
  - bigger-model-more-parametric-knowledge
  - beats-the-closed-book-baseline
- q:
  - Why do QA models do worse when the context is a table?
  - How much of Natural Questions has tabular context?
  - Do tables in the passage hurt extractive or generative QA accuracy?
  answers:
  - tabular-contexts-depress-every-number
  - error-analysis-of-the-factual-regression
- q:
  - Is Exact Match a fair metric for generative QA?
  - How much of a QA accuracy gap is just string matching artefacts?
  - What kinds of errors does Exact Match miscount in question answering?
  answers:
  - error-analysis-of-the-factual-regression
  - contextual-quality-is-preserved
  - tabular-contexts-depress-every-number
- q:
  - Can one model give two different answers to the same question on purpose?
  - How do you train a model to output both a grounded answer and a memory-based answer?
  - What does a model that reports agreement or conflict between its sources look like?
  answers:
  - two-answers-in-one-output
  - answer-separation-on-counterfactual
  - augmentations-are-complementary
- q:
  - Has anyone else made a model output both a grounded and a memorized answer?
  - How is this different from knowledge editing or model editing?
  - Is counterfactual augmentation for knowledge conflict this paper's idea?
  - What prior work does DisentQA build on?
  answers:
  - what-is-new-and-what-is-borrowed
  - dataset-and-augmentation-construction
  - two-answers-in-one-output
misreadings:
- The 18.46% is a similarity, not a separation. Section 3.3 defines Answer Separation as the
  share of cases where the two answers differ, but Table 6 reports the share where they are
  identical -- so on counterfactual data lower is better, and 18.46% is the paper's best result
  rather than a weak one. The two ablations score 92.45% and 99.71% on the same cell.
- This is not a claim that the model has two knowledge stores. The parametric answer is supervised
  to be the original dataset answer, and it is measured against that answer -- not against
  the world, and not against anything read out of the weights. When the parametric answer
  changes with the context (74.87% factual, 44.69% counterfactual, 31.14% empty, 30.18% random),
  that is the channel leaking, which the paper reports rather than hides.
- The parametric answers are mostly remembered from fine-tuning, not from pretraining. On
  the No Answer Overlap dev split the fully augmented model's parametric accuracy falls from
  44.69% to 12.72% on counterfactual contexts and the closed-book baseline from 27.69% to
  9.76%. Independently, only 18% of its parametric answers were never seen as an answer in
  training. Non-zero, so pretraining contributes -- but the headline parametric numbers are
  not a measure of memorized world knowledge.
- Beating the closed-book baseline is a 3.5-point effect (31.14% against 27.69%), and the
  paper says it is unclear why it should happen at all. On the harder No Answer Overlap split
  the ordering reverses (7.40% against 9.76%), so this is not evidence that adding context
  training improves recall from the weights.
- Emitting a parametric answer is not what improves robustness. Going from one answer to two
  barely moves any contextual number (80.73 to 80.37, 80.81 to 80.22, 78.32 to 78.10 on factual
  data; 84.98 to 84.91 on counterfactual). The gains under knowledge conflict come from the
  augmented training data; the second answer is what makes the source visible, not what makes
  the answer better.
- Answerability augmentation alone is not a partial version of the method -- in one configuration
  it is worse than doing nothing. The two-answer answerability-only model scores 64.62% on
  counterfactual data, below the 66.81% vanilla baseline, and it fails to abstain on 64.4%
  of random contexts, emitting the same string as both answers when it does.
- 'The value 27.69 appears in this paper as two unrelated quantities: the answerability-only
  single-answer model''s accuracy at abstaining on random contexts (Table 5) and the closed-book
  baseline''s parametric accuracy from an empty context (Table 7). Check which table a quoted
  27.69 came from before comparing it to anything.'
- The near-perfect abstention numbers (99.34% and 99.49%) are on easy negatives. The unanswerable
  examples are either an empty context or a passage sampled from elsewhere that shares no
  topic or entity with the question; the authors call the approach simplistic and a proof
  of concept, and name distractors that look relevant but lack the answer as future work.
- 'None of these accuracies are comparable to published Natural Questions numbers. Only the
  35% of NQ with both a gold passage and a short answer is used, the gold passage is always
  supplied (an oracle retriever), the test set is cut to the 1,365 examples that admitted
  a counterfactual, and Exact Match miscounts: of 73 analysed regressions, 14 were correct
  answers scored zero and 6 had a second valid answer.'
- Counterfactual augmentation is not this paper's invention -- it is Longpre et al. (2021)'s
  entity substitution, adopted unchanged, and they had already shown it mitigates over-reliance
  on memorized answers. What is new here is the two-answer output format, the answerability
  augmentation, and the finding that the two augmentations only work together. Attribute the
  substitution procedure accordingly.
- This is not knowledge editing. Methods that modify or locate the facts stored in the weights
  (Zhu et al., De Cao et al., Verga et al., Dai et al., Meng et al.) are cited as related
  work, not as baselines, and nothing here changes what the model has memorized. DisentQA
  leaves the parametric answer intact and makes it visible alongside the grounded one, so
  a reader can see the conflict rather than have it resolved for them.
terminology:
  DisentQA: 'The paradigm introduced here, and the name of the resulting model family: one
    generative QA model fine-tuned to emit a contextual answer and a parametric answer as
    a single decoded string, trained on factual, counterfactual and unanswerable versions
    of the same examples.'
  parametric knowledge: Knowledge encoded in the model's weights during pretraining. Operationally
    in this paper it is whatever the model produces as the second answer, supervised to be
    the original dataset answer -- so the term names an intent, not a verified source. A footnote
    acknowledges the word "knowledge" is anthropomorphic for a token predictor.
  contextual knowledge: The passage handed to the model at inference time, here always the
    Natural Questions gold passage. The contextual answer is the one the model should ground
    in that passage, including "unanswerable" when the passage does not support any.
  counterfactual data augmentation: 'Longpre et al. (2021)''s corpus-substitution procedure,
    adopted unchanged: every occurrence of the answer entity in a passage is replaced by another
    answer of the same entity type drawn from the same corpus, so the grounded answer now
    contradicts the original one. Works only for named-entity answers.'
  answerability augmentation: 'This paper''s addition: training examples whose context is
    empty or randomly substituted, where the contextual answer must be the literal token "unanswerable"
    while the parametric answer stays the original one. Its purpose is to stop the model from
    hallucinating a contextual answer out of its weights.'
  Answer Separation: The disentanglement metric. Defined in the text as the share of cases
    where the two answers differ, but tabulated as the share where they are identical -- so
    read Table 6 as similarity and remember that the counterfactual, empty and random columns
    want low numbers and the factual column wants a high one.
  answer overlap (AO / NAO): Lewis et al. (2021)'s split of a QA test set by whether the reference
    answer also appears as an answer somewhere in training. The No Answer Overlap half is
    where this paper's parametric-knowledge numbers collapse, which is why it is the honest
    denominator for any claim about memorization.
  (s) / (m) and f / cf / a: 'The model naming scheme: (s) emits one answer, (m) emits two;
    f, cf and a name the example types in training (factual, counterfactual, answerability).
    So "(m) f+cf+a" is the fully augmented two-answer model and "(s) f" is the vanilla baseline.'
links_extra:
  code: https://github.com/ellaneeman/disent_qa
---
