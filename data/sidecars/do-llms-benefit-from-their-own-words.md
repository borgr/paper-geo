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
    plain: If you delete a chatbot's own earlier replies from the conversation history, do
      its later answers get worse?
    jargon: How does assistant-turn omission in the dialogue history affect judged response
      quality and on-topic rate across instruction-tuned LLMs?
    task: How do I trim assistant turns out of a multi-turn prompt without degrading the next
      response?
    practitioner: Should I keep past model replies in my chat history, or send only the user
      turns?
  answered_by:
  - ao-quality-parity
  - judge-context-sensitivity
- ask:
    plain: How many characters of prompt do you save in a long chat by keeping only what the
      user wrote?
    jargon: What context-length reduction does user-turn-only prompting yield over full dialogue
      history by round 8?
    task: How do I cut token spend on a growing chat history without truncating or summarizing?
    practitioner: Will dropping assistant turns actually make my multi-turn requests meaningfully
      cheaper?
  answered_by:
  - context-length-reduction
- ask:
    plain: In real conversations with a chatbot, how often is a person's next message a brand-new
      request rather than a follow-up?
    jargon: What proportion of non-initial user turns in in-the-wild human-LLM logs are self-contained
      versus dependent on prior assistant output?
    task: How do I tell whether a multi-turn chat corpus really tests long-context multi-turn
      reasoning?
    practitioner: Can I trust WildChat-style logs as a benchmark for multi-turn context dependence?
  answered_by:
  - self-contained-fraction
  - context-benchmark-implication
- ask:
    plain: Which kinds of user messages still need the chatbot's earlier answer in the history,
      and which do not?
    jargon: Does the benefit of retaining assistant history differ between new-ask turns and
      follow-up turns?
    task: How do I decide per turn whether a user message needs the assistant's prior response?
    practitioner: If most of my users ask follow-up questions, is stripping assistant history
      still safe for me?
  answered_by:
  - new-ask-vs-followup
  - self-contained-fraction
- ask:
    plain: Can a chatbot's own earlier mistakes in the conversation get repeated into later
      answers?
    jargon: What does context pollution from retained assistant turns look like in multi-turn
      LLM conversations?
    task: How do I stop a wrong assumption or hallucination from an earlier reply carrying
      into later turns?
    practitioner: Is keeping my model's previous outputs in the prompt risking repeated hallucinations
      and stale code?
  answered_by:
  - context-pollution-examples
- ask:
    plain: Can a small model learn when to keep the chatbot's earlier replies and when to
      throw them away?
    jargon: Can a per-turn classifier select between full and assistant-omitted context, and
      is judge preference predictable from turn features?
    task: How do I build a per-turn policy that drops assistant history only when it is safe?
    practitioner: Is adaptive per-turn context filtering worth implementing, or will I lose
      quality against always sending full history?
  answered_by:
  - adaptive-classifier
  - prediction-is-weak
- ask:
    plain: Is it better to replace a chatbot's past answers with one-sentence summaries than
      to keep them in full?
    jargon: How does one-sentence self-summarization of assistant turns compare with full
      history and with full omission on Lost-in-Conversation and WildChat?
    task: How do I compress assistant turns in a chat history instead of deleting them outright?
    practitioner: Should I summarize my model's earlier replies rather than dropping them
      or keeping them verbatim?
  answered_by:
  - summarization-beats-full
- ask:
    plain: How much can you trust a big model's scoring of which chat answer is better, and
      does what it sees change its verdict?
    jargon: How well does the GPT-5 judge agree with manual annotation, and does restricting
      the judge to user-side turns flip the preference between context conditions?
    task: How do I set up an LLM judge for comparing responses under different context conditions
      without biasing it toward the longer history?
    practitioner: Can I rely on LLM-as-judge results comparing full-context and assistant-omitted
      responses?
  answered_by:
  - judge-alignment
  - judge-context-sensitivity
- ask:
    plain: Is there a study that asks whether keeping a chatbot's own past replies in the
      prompt is actually worth it?
    jargon: What work evaluates assistant-history retention on in-the-wild human-LLM logs
      rather than synthetic multi-turn dialogues?
    task: What should I read before designing context management for a multi-turn chat or
      agent system?
    practitioner: Which paper should I cite if I want to argue that real chat logs are weak
      multi-turn benchmarks?
  answered_by:
  - context-contribution
  - context-benchmark-implication
- ask:
    plain: Do big commercial chatbots get thrown off by their own earlier replies, or is that
      only a small-model problem?
    jargon: Which models were evaluated for assistant-turn omission, and does over-conditioning
      on prior assistant output appear in frontier models too?
    task: How do I check whether the model I use is being misled by its own earlier turns?
    practitioner: I run a frontier model in production, is over-conditioning on its own past
      answers something I have to worry about?
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
