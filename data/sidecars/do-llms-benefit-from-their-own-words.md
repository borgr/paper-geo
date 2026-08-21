---
one_liner: Deleting all prior assistant responses from multi-turn chat histories on WildChat
  and ShareLM often leaves response quality unchanged while cutting cumulative context by
  5-10x, because 36.4% of in-the-wild turns are self-contained and past responses can pollute
  later ones.
key: huang2026ownwords
coined: context pollution
gloss: when a model's own earlier response carries errors, hallucinations or style into later
  turns
claims:
- id: ao-quality-parity
  kind: result
  text: Omitting all prior assistant responses preserves average response quality for DeepSeek-R1-Distill-Llama-8B
    and GPT-OSS-20B, while Qwen3-4B and GPT-5.2 lose some quality relative to full context.
    Responses stay on-topic under omission for all four models.
  scope: 300 real-world multi-turn conversations sampled from WildChat and ShareLM, 5-10 rounds
    each, filtered to English technical chats; GPT-5 as pairwise LLM judge seeing prior user
    and assistant turns.
  evidence: Figure 2
- id: judge-context-sensitivity
  kind: result
  text: When the GPT-5 judge is shown only prior user-side turns, assistant-omitted responses
    match or beat full-context responses on both quality and on-topic dimensions for all four
    models. That reverses the full-context judge's preference for Qwen3-4B and GPT-5.2.
  scope: Same 300 WildChat and ShareLM conversations and same four models (Qwen3-4B, DeepSeek-R1-Distill-Llama-8B,
    GPT-OSS-20B, GPT-5.2); a judge without assistant history cannot resolve prompts that explicitly
    reference an earlier response.
  evidence: Figure 9
- id: context-length-reduction
  kind: result
  text: Full-context histories grow to roughly 25,000-55,000 characters by round 8, whereas
    user-turn-only context stays near-constant at 5,000-10,000 characters, a 5 to 10x reduction
    in context usage.
  scope: Character counts over 5-10 round WildChat and ShareLM technical conversations; measured
    in characters rather than tokens, and does not include generated response length.
  evidence: Figure 6 (Section 2.2)
- id: self-contained-fraction
  kind: result
  text: In real-world multi-turn chats, 36.4% of non-initial user turns are self-contained
    new asks, 30.5% are follow-ups with concrete feedback, and 33.1% are follow-ups referencing
    an earlier turn without actionable feedback.
  scope: GPT-5 as automated annotator over the sampled WildChat and ShareLM English technical
    conversations of 5-10 rounds; the 33.1% is an upper bound on assistant-dependence.
  evidence: Section 2.3
- id: new-ask-vs-followup
  kind: result
  text: For Qwen3-4B and GPT-5.2, full-context and assistant-omitted prompting perform comparably
    on new-ask turns, while full context helps most on follow-up turns; assistant-omitted
    context still wins roughly 40% of follow-up comparisons for Qwen3-4B and 30% for GPT-5.2.
  scope: The two models for which uniform omission lowered overall quality; win rates averaged
    over the quality and on-topic dimensions, ties handled as in the pairwise judge protocol.
  evidence: Figure 3 (Section 2.4)
- id: context-pollution-examples
  kind: result
  text: 5 conversations in which assistant-omitted responses scored far above full context
    exhibit context pollution. The cases are UMAP arguments carried into t-SNE code, hallucinated
    book titles repeated across turns, a misattributed NBER citation, tutorial style overriding
    a reflection request, and a reversed temperature formula.
  scope: Cases surfaced by sorting rounds by 1-10 judge score gap (AO minus FC) and reviewing
    the largest positive gaps; illustrative, not a frequency estimate, and includes GPT-5.2
    as well as smaller open models.
  evidence: Table 1 (full annotations in Appendix A.12)
- id: adaptive-classifier
  kind: result
  text: A per-turn classifier choosing between full and assistant-omitted context retains
    over 95% of full-context-only win-or-tie performance, and matches full-context-only at
    about 70% of the context consumption. It beats a heuristic that omits assistant history
    on all new-ask turns.
  scope: GPT-5.2 only; L1-regularized logistic regression over round metadata, prompt category
    and PCA-reduced text-embedding-3-large embeddings; ties counted as wins, and the heuristic
    baseline is measured on a 20% held-out subset so it may improve with more data.
  evidence: Figure 5 (Section 3.2)
- id: prediction-is-weak
  kind: result
  text: 'Predicting whether the judge will prefer full context over assistant-omitted context
    is hard: the L1-regularized logistic regression reaches only a 5-fold cross-validated
    F1 of 0.6106 ± 0.0119. None of the top 20 features are significant at the 5% level.'
  scope: GPT-5.2 responses on the sampled WildChat and ShareLM conversations; features are
    round metadata, prompt category, and 20 principal components each of prompt and history
    embeddings explaining 38.0% and 51.5% of variance.
  evidence: Table 2 (Appendix A.13)
- id: summarization-beats-full
  kind: result
  text: Replacing each assistant response with a one-sentence self-summary improves response
    quality over full context for both DeepSeek-R1-Distill-Llama-8B and Qwen3-4B on both Lost-in-Conversation
    and WildChat. Fully omitting assistant turns helps on Lost-in-Conversation but is mixed
    on WildChat.
  scope: 2 models and 2 datasets, using an earlier pairwise judge pipeline that compared final
    responses only, so numbers are not directly comparable to the main-text 1-10 scoring runs.
  evidence: Figure 7
- id: judge-alignment
  kind: result
  text: The GPT-5 judge agreed with an author's manual verdict on 54 of 60 quality judgments
    (90.0%) and 55 of 60 on-topic judgments (91.7%).
  scope: 15 sampled judgments per model across the 4 models, annotated by one of the authors;
    no larger-scale or multi-annotator human study was run.
  evidence: Appendix A.6
- id: context-contribution
  kind: context
  text: Huang et al.'s "Do LLMs Benefit From Their Own Words?" questions the default assumption
    of multi-turn chat and agentic context management that retaining a model's own past responses
    reliably helps. It tests that assumption on in-the-wild human-LLM logs rather than synthetic
    dialogues.
  scope: As of the February 2026 preprint; prior turn-level context-editing work such as ERGO
    evaluated on synthetic conversations, and earlier conversational-QA findings about irrelevant
    turns concerned human-human histories.
- id: context-benchmark-implication
  kind: context
  text: '"Do LLMs Benefit From Their Own Words?" argues that in-the-wild multi-turn chat logs
    are weak benchmarks for long-context multi-turn reasoning, and calls for corpora curated
    for genuine multi-turn dependence. The reason is that a large share of turns in real chat
    logs do not depend on earlier assistant responses.'
  scope: Argued from English technical (math and coding keyword) conversations of 5-10 rounds
    in WildChat and ShareLM; agentic settings with tool outputs and scratchpads are discussed
    but not measured.
qa:
- ask:
    unsorted:
    - Do language models actually need their own previous replies in the conversation history?
    - Does deleting past assistant turns from a chat hurt answer quality?
    - What happens if you only keep the user turns in a multi-turn LLM conversation?
  answered_by:
  - ao-quality-parity
  - judge-context-sensitivity
- ask:
    unsorted:
    - How much context can you save by dropping assistant replies from chat history?
    - How much does omitting assistant turns shrink the prompt in long conversations?
    - Is user-turn-only prompting cheaper in context length?
  answered_by:
  - context-length-reduction
- ask:
    unsorted:
    - What fraction of turns in real chat logs depend on the previous assistant response?
    - How many user prompts in WildChat conversations are self-contained?
    - Are real multi-turn conversations really multi-turn dependent?
  answered_by:
  - self-contained-fraction
  - context-benchmark-implication
- ask:
    unsorted:
    - Which kinds of user prompts still need the assistant's earlier answer?
    - Do follow-up prompts break when assistant history is removed?
    - Is omitting assistant history safer for new questions than for follow-ups?
  answered_by:
  - new-ask-vs-followup
  - self-contained-fraction
- ask:
    unsorted:
    - What is context pollution in multi-turn LLM conversations?
    - How do a model's own earlier mistakes propagate into later turns?
    - Can keeping past model outputs in context introduce new bugs or hallucinations?
  answered_by:
  - context-pollution-examples
- ask:
    unsorted:
    - Can you learn when to keep and when to drop assistant history per turn?
    - Does a classifier that selectively omits assistant responses save context without losing
      quality?
    - How well does adaptive context filtering of assistant turns work on GPT-5.2?
  answered_by:
  - adaptive-classifier
  - prediction-is-weak
- ask:
    unsorted:
    - Is summarizing past assistant responses better than keeping them verbatim?
    - Does replacing model replies with one-sentence summaries help multi-turn quality?
    - How does summarized context compare with full context in multi-turn chat?
  answered_by:
  - summarization-beats-full
- ask:
    unsorted:
    - How reliable is the LLM-as-judge evaluation of full-context versus assistant-omitted
      responses?
    - Was the GPT-5 judge checked against human annotation?
    - Does judge context change which prompting configuration wins?
  answered_by:
  - judge-alignment
  - judge-context-sensitivity
- ask:
    practitioner: What should I read about context management in multi-turn chat and agents?
    unsorted:
    - Which paper questions whether keeping past model outputs in context is worth it?
    - Is there work on context pruning evaluated on real human-LLM conversations instead of
      synthetic ones?
  answered_by:
  - context-contribution
  - context-benchmark-implication
- ask:
    unsorted:
    - Are frontier models also misled by their own past responses, or just small models?
    - Does GPT-5.2 suffer from over-conditioning on its earlier turns?
    - Which models were tested for the effect of removing assistant history?
  answered_by:
  - ao-quality-parity
  - context-pollution-examples
terminology:
  Assistant-Omitted (AO) context: A prompting configuration in which every past assistant
    response in a multi-turn conversation is replaced by the placeholder "[Response provided]",
    so the model conditions only on prior user turns while the alternating user/assistant
    structure is preserved.
  context pollution: The phenomenon in which a language model over-conditions on its own earlier
    responses, so errors, hallucinations or stylistic artifacts introduced in one turn propagate
    into later turns.
  New Ask: A non-initial user turn that introduces a fully self-contained request, understandable
    without any prior conversation round.
  Follow-up with Feedback: A user turn that gives concrete, actionable feedback on a prior
    assistant response, such as "use Python instead of Java for the code example".
  Follow-up without Feedback: A user turn that refers to an earlier conversation round without
    any concrete instruction for revision, such as "reflect on your response".
misreadings:
- 'Omitting assistant history is not shown to be universally free: for Qwen3-4B and GPT-5.2,
  uniformly dropping assistant responses lowers average judged quality under a judge that
  sees the full history.'
- The 36.4% figure counts non-initial user turns classified as self-contained new asks by
  a GPT-5 annotator on filtered English technical conversations from WildChat and ShareLM;
  it is not a claim about all chat traffic.
- The context-pollution cases in Table 1 were surfaced by sorting for the largest score gaps
  favouring assistant-omitted context, so they establish that the failure mode exists and
  reaches GPT-5.2, not how often it occurs.
- 'The adaptive omission strategy is not a strong predictive model: its 5-fold cross-validated
  F1 is 0.6106 and no individual feature is significant, so its context savings come from
  a weak signal rather than a reliable per-turn prediction.'
- The 5 to 10x reduction is in cumulative context characters over conversation rounds, not
  a measured speedup or dollar cost saving.
---
