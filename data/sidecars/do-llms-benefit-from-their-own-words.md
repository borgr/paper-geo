---
one_liner: Replacing or dropping prior assistant responses in multi-turn chat histories from
  WildChat and ShareLM often matches full-context response quality while using roughly 8x
  less context, because 36.4% of in-the-wild turns are self-contained and past responses can
  pollute later ones.
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
  scope: 350 English multi-turn conversations, 200 from WildChat and 150 from ShareLM, 5-10
    rounds each, spanning creative-writing, science and coding keyword categories; GPT-5 as
    pairwise judge seeing prior user and assistant turns.
  evidence: Figure 2 (third row)
- id: judge-context-sensitivity
  kind: result
  text: When the GPT-5 judge is shown only prior user-side turns, assistant-omitted responses
    often perform comparably to full-context responses on both the quality and on-topic dimensions
    across the four models.
  scope: Same 350 WildChat and ShareLM conversations and same four models; a judge without
    assistant history cannot resolve prompts that explicitly reference an earlier response.
  evidence: Figure 10 (Section A.11)
- id: context-length-reduction
  kind: result
  text: Cumulative context length grows linearly with conversation length under full context.
    The summarized, last-turn-only and assistant-omitted configurations stay relatively constant,
    so a reduced configuration that matches full-context quality uses roughly 8x less context.
  scope: Cumulative context measured in characters over 5-10 round WildChat and ShareLM conversations,
    plotted from GPT-5.2 generations; does not include generated response length.
  evidence: Figure 4 (center)
- id: self-contained-fraction
  kind: result
  text: In real-world multi-turn chats, 36.4% of non-initial user turns are self-contained
    new asks, 30.5% are follow-ups with concrete feedback, and 33.1% are follow-ups referencing
    an earlier turn without actionable feedback.
  scope: GPT-5 as automated annotator over the sampled WildChat and ShareLM English conversations
    of 5-10 rounds; the 33.1% is an upper bound on assistant-dependence.
  evidence: Section A.7
- id: new-ask-vs-followup
  kind: result
  text: For Qwen3-4B and GPT-5.2, assistant-side history is most beneficial for follow-up
    turns, while full-context and assistant-omitted prompting perform comparably on new-ask
    turns.
  scope: The two models for which uniform omission lowered overall quality; win rates averaged
    over the quality and on-topic dimensions, with stars marking significant differences.
  evidence: Figure 8 (Section A.7)
- id: context-pollution-examples
  kind: result
  text: Retained assistant responses produce context pollution, with UMAP arguments carried
    into t-SNE code, a hallucinated fact about a novel repeated across turns, and a misattributed
    NBER citation. An earlier response's style also overrode a reflection request, and a temperature
    formula was reused incorrectly.
  scope: Select cases the authors reviewed among turns an LLM annotator flagged as polluted;
    illustrative rather than a frequency estimate, and includes GPT-5.2 as well as smaller
    open models.
  evidence: Table 1 (examples in Section A.22)
- id: adaptive-classifier
  kind: result
  text: A per-turn classifier choosing between full and assistant-omitted context retains
    over 99% of full-context-only performance while using an average of 87% of the total token
    cost. It beats a heuristic that omits assistant history on all new-ask turns.
  scope: GPT-5.2 with its own responses fed back into context; L1-regularized logistic regression
    over round number, context lengths, prompt category and PCA-reduced embeddings; the heuristic
    baseline uses a 20% held-out subset.
  evidence: Figure 6 (Section 5)
- id: prediction-is-weak
  kind: result
  text: 'Predicting whether the judge will prefer full context over assistant-omitted context
    is hard: the L1-regularized logistic regression reaches only a 5-fold cross-validated
    F1 of 0.6106 ± 0.0119. None of the top 20 features are significant at the 5% level.'
  scope: GPT-5.2 responses on the sampled WildChat and ShareLM conversations; features are
    round number, context lengths, prompt category, and 20 principal components each of the
    prompt and history embeddings.
  evidence: Table 5 (Section A.15)
- id: summarization-beats-full
  kind: result
  text: Replacing each assistant response with a one-sentence summary is the most effective
    of the reduced-context configurations, often exceeding full context across the four models.
    It also cuts median response length by roughly 25%.
  scope: Four models on the 350 WildChat and ShareLM conversations; the summary replaces each
    prior assistant turn in place, and the median-length reduction is measured over generated
    responses.
  evidence: Figure 2 (top row), Section 3
- id: judge-alignment
  kind: result
  text: The GPT-5 judge agreed with an author's manual verdict on 74 of 80 quality judgments
    (92.5%) and 75 of 80 on-topic judgments (93.75%).
  scope: 20 sampled judgments per model across the 4 models, annotated by one author; no multi-annotator
    human study was run.
  evidence: Section A.5
- id: context-contribution
  kind: context
  text: Huang et al.'s "Do LLMs Benefit From Their Own Words?" questions the default assumption
    of multi-turn chat and agentic context management that retaining a model's own past responses
    reliably helps. It tests that assumption on in-the-wild human-LLM logs rather than synthetic
    dialogues.
  scope: As of the August 2026 version of the preprint; prior turn-level context-editing work
    such as ERGO evaluated on synthetic conversations, and earlier conversational-QA findings
    about irrelevant turns concerned human-human histories.
- id: context-benchmark-implication
  kind: context
  text: '"Do LLMs Benefit From Their Own Words?" argues that in-the-wild multi-turn chat logs
    are weak benchmarks for long-context multi-turn reasoning, and calls for corpora curated
    for genuine multi-turn dependence. The reason is that a large share of turns in real chat
    logs do not depend on earlier assistant responses.'
  scope: Argued from English conversations of 5-10 rounds sampled from WildChat and ShareLM
    across creative-writing, science, coding and other keyword categories; agentic settings
    with tool outputs and scratchpads are discussed but not measured.
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
    plain: How much of the prompt do you save in a long chat by trimming the chatbot's own
      earlier replies?
    jargon: What context-length reduction do the reduced-context configurations yield over
      full dialogue history as a conversation grows?
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
    jargon: How does one-sentence summarization of assistant turns compare with full history
      and with full omission across four models on WildChat and ShareLM?
    task: How do I compress assistant turns in a chat history instead of deleting them outright?
    practitioner: Should I summarize my model's earlier replies rather than dropping them
      or keeping them verbatim?
  answered_by:
  - summarization-beats-full
- ask:
    plain: How much can you trust a big model's scoring of which chat answer is better, and
      does what it sees change its verdict?
    jargon: How well does the GPT-5 judge agree with manual annotation, and does restricting
      the judge to user-side turns change the preference between context conditions?
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
  a GPT-5 annotator on filtered English conversations from WildChat and ShareLM; it is not
  a claim about all chat traffic.
- The context-pollution cases are select examples the authors reviewed among annotator-flagged
  turns, so they establish that the failure mode exists and reaches GPT-5.2. The paper measures
  how often it occurs separately, in Table 1.
- 'The adaptive omission strategy is not a strong predictive model: its 5-fold cross-validated
  F1 is 0.6106 and no individual feature is significant, so its context savings come from
  a weak signal rather than a reliable per-turn prediction.'
- The roughly 8x reduction is in cumulative context characters over conversation rounds. No
  speedup or dollar cost saving was measured.
---
