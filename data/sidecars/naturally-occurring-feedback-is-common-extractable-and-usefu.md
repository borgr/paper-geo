---
key: donyehiya2025naturallyoccurringfeedbackcommon
one_liner: Users spontaneously leave explicit feedback in about 30% of real chatbot conversations,
  an open LLM can extract it at 0.43 span precision and 0.58 recall, and finetuning on 173,859
  such extracted samples beats the pretrained model in up to 79% of pairwise comparisons.
claims:
- id: prevalence-30-percent
  kind: result
  text: Manual annotation of 223 English multi-turn conversations from LMSYS-Chat-1M found
    101 explicit feedback cases in 77 conversations, meaning roughly 30% of chats carry naturally
    occurring user feedback.
  scope: First 300 multi-turn LMSYS-Chat-1M conversations annotated by one author, 223 left
    after filtering non-English and offensive content; explicit text-anchored feedback only.
  evidence: Section 3.2, Figure 2
- id: annotator-agreement
  kind: result
  text: Two annotators reach a Cohen's kappa of 0.65 on the binary question of whether a user
    response contains naturally occurring feedback. On the cases both marked as feedback,
    they agree on the category in 0.79 of them.
  scope: 68 English LMSYS-Chat-1M conversations, out of the first 100, re-annotated by one
    in-house annotator; 5-category taxonomy.
  evidence: Section 3.2
- id: newer-data-more-feedback
  kind: result
  text: The 2019 Self-Feeding Chatbot corpus yields only 11 feedback instances per 100 human-model
    conversations, less than half the rate found in the newer LMSYS-Chat-1M data. 48 model
    errors were annotated in that same 100-conversation sample, so a lack of errors does not
    explain the gap.
  scope: One 2019 open-domain human-model dataset compared against LMSYS-Chat-1M, omitting
    the Positive Feedback category added by this taxonomy; annotation sources differ (Petrak
    et al. 2023 versus this work's annotator).
  evidence: Section 3.3
- id: extraction-precision-recall
  kind: result
  text: Prompting Mixtral-8x7B-Instruct to mark feedback spans recovers naturally occurring
    feedback with 0.43±0.05 span precision and 0.58±0.06 span recall. Requiring the feedback
    category to be correct too drops this to 0.28±0.04 precision and 0.38±0.06 recall.
  scope: 300 manually annotated LMSYS-Chat-1M conversations; 4-bit quantized Mixtral-8x7B-Instruct-v0.1,
    zero-shot JSON prompt, bootstrap with 1000 repetitions; a span counts as correct if it
    is a substring of the annotated span and at least half as long.
  evidence: Section 4.2, Figure 4
- id: dataset-size
  kind: result
  text: Running the extraction method over all 1M LMSYS-Chat-1M conversations yields 173,859
    feedback examples from 115,312 distinct conversations, with about 15 times more negative
    than positive examples.
  scope: 334,319 multi-turn conversations remain after filtering; 4-bit Mixtral-8x7B-Instruct-v0.1
    at roughly 1 conversation per 10 seconds on an NVIDIA A40 GPU.
  evidence: Section 4.3
- id: finetune-win-rates
  kind: result
  text: Finetuning on 8,448 automatically extracted positive-feedback examples wins 69% /
    81.5% / 77% of blind human pairwise comparisons against the corresponding pretrained Pythia-1.4B,
    Pythia-2.8B and Mistral-7B models.
  scope: 100 response pairs per model rated by one in-house annotator on the OpenAssistant
    validation split, order not consistent and model identity hidden; GPT-4 as a judge gives
    65% / 74% / 78% on the same comparison.
  evidence: Table 1, Section 5.2
- id: beats-random-chats
  kind: result
  text: Finetuning Mistral-7B on extracted positive feedback beats finetuning it on an equally
    sized random sample of LMSYS-Chat-1M chats. Win rates over the pretrained model are 70%
    versus 64% under Eurus-RM-7b, 72% versus 68% under FsfairX-LLaMA3-RM-v0.1 and 78% versus
    75% under GPT-4.
  scope: 7B model only; both settings compared against the same pretrained Mistral-7B reference
    on the OpenAssistant validation split; win rates from reward models and GPT-4, not human
    raters.
  evidence: Table 1, Section 5.3
- id: kto-preference-gain
  kind: result
  text: KTO preference training on the extracted negative feedback, applied on top of finetuning,
    raises Mistral-7B win rates over the pretrained model to 74% (Eurus-RM-7b), 75% (FsfairX-LLaMA3-RM-v0.1)
    and 79% (GPT-4). That is 1 to 3 points above finetuning alone.
  scope: 7B model only, started from the already finetuned checkpoint; negatives restricted
    to Make Aware with Correction and Make Aware without Correction and down-sampled to balance
    positives; no human evaluation.
  evidence: Table 1, Section 5.4
- id: taxonomy-needed
  kind: result
  text: Dropping the feedback taxonomy from the extraction prompt and asking only for spans
    informative about user satisfaction produced 693 spans, none of which matched any manually
    annotated feedback case. The general prompt often marked the user's original request as
    a satisfaction signal.
  scope: 4-bit Mixtral-8x7B-Instruct-v0.1 on the 300 manually annotated LMSYS-Chat-1M conversations,
    with spans rated 1-5 instead of categorised.
  evidence: Section 6.1.1, Figure 6
- id: fewer-categories-not-easier
  kind: result
  text: Restricting extraction to just Repeat or Rephrase and Positive Feedback does not improve
    accuracy. Positive Feedback reaches 0.5 span and category precision, while Repeat or Rephrase
    reaches 0.43 span precision but only 0.17 category precision.
  scope: 4-bit Mixtral-8x7B-Instruct-v0.1 on the 300 manually annotated LMSYS-Chat-1M conversations;
    the model invented categories outside the 2 it was given, such as "Asking for Assistance".
  evidence: Section 6.1.2, Figure 7
- id: confidence-useless
  kind: result
  text: A self-reported 1-5 confidence level is useless for filtering automatically extracted
    feedback, because over 96% of extracted cases receive the top score of 5. The remaining
    4% are mostly non-feedback or hallucinations that parsing already discards.
  scope: 4-bit Mixtral-8x7B-Instruct-v0.1 on LMSYS-Chat-1M with the confidence-level variant
    of the extraction prompt; no other confidence-elicitation format tried.
  evidence: Section 6.2, Figure 8
- id: reward-models-fail-small
  kind: result
  text: 'Top RewardBench reward models misjudge small models: Eurus-RM-7b and FsfairX-LLaMA3-RM-v0.1
    report only 31%/48% and 38%/60% wins for finetuned Pythia-1.4B and Pythia-2.8B, while
    human raters report 69% and 81.5% for the same pairs.'
  scope: Open reward models judging OpenAssistant validation responses; the same reward models
    agree with human and GPT-4 evaluation at 7B, so the gap is attributed to their training
    distribution.
  evidence: Table 1, Section 5.2
- id: context-natural-feedback
  kind: context
  text: Naturally occurring feedback, meaning spontaneous unsolicited user reactions already
    present in chat logs, is proposed as a scalable alternative to solicited preference annotation.
    An extraction method and a released dataset of 173,859 samples accompany the proposal.
  scope: Positioned against elicited free-text feedback and model-as-judge labelling as of
    2025; covers explicit English-language textual cues in human-model chat only, not implicit
    signals such as a user silently moving on.
  evidence: Section 1, Section 7
- id: context-taxonomy
  kind: context
  text: The naturally occurring feedback taxonomy adapts Petrak et al. (2023)'s user-response
    patterns into 4 negative categories plus a new Positive Feedback category. The negative
    categories are Repeat or Rephrase, Make Aware with Correction, Make Aware without Correction
    and Ask for Clarification, and "Ignore and Continue" is dropped.
  scope: Designed for simplicity and text-anchoredness in human-model open-domain chat; "Ignore
    and Continue" is excluded because it requires annotated errors in the preceding model
    response, which this setting lacks.
  evidence: Section 3.1
qa:
- ask:
    unsorted:
    - How much feedback do users spontaneously give in chatbot conversations?
    - What fraction of chat logs contain explicit user feedback?
    - Do real chat users actually correct or praise a chatbot without being asked?
  answered_by:
  - prevalence-30-percent
  - annotator-agreement
- ask:
    unsorted:
    - Is feedback more common in newer chat datasets than older ones?
    - Has spontaneous user feedback in human-model conversations increased over time?
    - How does 2019 chatbot conversation data compare to LMSYS-Chat-1M in feedback rate?
  answered_by:
  - newer-data-more-feedback
- ask:
    unsorted:
    - How accurately can an open LLM extract user feedback spans from chat logs?
    - What precision and recall does automatic naturally occurring feedback extraction achieve?
    - Can Mixtral find spontaneous feedback in conversations reliably?
  answered_by:
  - extraction-precision-recall
- ask:
    unsorted:
    - How large is the released naturally occurring feedback dataset?
    - How many feedback samples were extracted from LMSYS-Chat-1M?
    - What is the ratio of negative to positive samples in the extracted natural feedback
      data?
  answered_by:
  - dataset-size
- ask:
    unsorted:
    - Does training on automatically extracted user feedback actually improve a language model?
    - What win rates does finetuning on extracted positive feedback achieve over the pretrained
      model?
    - Is spontaneous chat feedback useful as training data for alignment?
  answered_by:
  - finetune-win-rates
  - kto-preference-gain
- ask:
    unsorted:
    - Is extracted feedback better training data than just random chat transcripts?
    - Does the improvement come from the feedback signal or merely from finetuning on chat-formatted
      data?
    - What baseline rules out distillation as the explanation for the gains of training on
      extracted chat feedback?
  answered_by:
  - beats-random-chats
- ask:
    unsorted:
    - Do the negative feedback examples help, or only the positive ones?
    - Does KTO preference training on extracted corrections beat plain finetuning?
    - How were unpaired positive and negative feedback samples used for preference training?
  answered_by:
  - kto-preference-gain
- ask:
    unsorted:
    - Is a detailed feedback taxonomy necessary for prompting an LLM to find feedback?
    - What happens if a feedback extraction prompt asks for user satisfaction cues without
      categories?
    - Would fewer feedback categories make extraction more precise?
  answered_by:
  - taxonomy-needed
  - fewer-categories-not-easier
- ask:
    unsorted:
    - Does asking an LLM for a confidence score help filter extracted feedback?
    - Can self-reported confidence levels improve feedback extraction precision?
  answered_by:
  - confidence-useless
- ask:
    unsorted:
    - Are open reward models reliable judges for small language models?
    - Why do reward-model win rates disagree with human evaluation for 1.4B and 2.8B models?
    - Can RewardBench leaders be used to evaluate Pythia-scale outputs?
  answered_by:
  - reward-models-fail-small
- ask:
    practitioner: What should I read about getting human feedback for LLM alignment without
      paying annotators?
    unsorted:
    - Which work established that chat logs contain usable free human feedback?
    - Where do I start reading about mining preference data from real user conversations?
    - What is a good paper on scalable alternatives to human preference annotation?
  answered_by:
  - context-natural-feedback
  - context-taxonomy
- ask:
    unsorted:
    - What categories of spontaneous user feedback appear in chat conversations?
    - How is naturally occurring feedback classified into types?
    - What kinds of corrections do users give chatbots?
  answered_by:
  - context-taxonomy
  - prevalence-30-percent
terminology:
  naturally occurring feedback: Spontaneous, unsolicited feedback that a user includes in
    a chat message about the model's previous response -- a correction, a rephrased request,
    a clarification question or a thank-you -- as opposed to feedback elicited by an explicit
    request or rating interface.
  Repeat or Rephrase: A feedback category in which the user ignores the model's previous response
    and repeats or rephrases their earlier request, so the two one-turn exchanges can be used
    as a preference pair.
  Make Aware with Correction: A feedback category in which the user tells the model it was
    wrong and supplies the information needed to fix the error, e.g. "No, I wanted...".
  Make Aware without Correction: A feedback category in which the user tells the model it
    was wrong without supplying any corrective information, e.g. "That's incorrect", usable
    only as a strictly negative example.
  Ask for Clarification: A feedback category in which the user requests resolution that was
    expected in the previous model response but missing, indicating the response was partially
    but not entirely wrong.
  span precision: The percentage of automatically identified feedback spans that are correct,
    where correct means being a substring of a manually annotated feedback span and at least
    half as long as it.
misreadings:
- The reported ~30% prevalence is the share of multi-turn English LMSYS-Chat-1M conversations
  containing explicit feedback, not the share of all chat conversations or of individual user
  turns.
- The extraction method's 0.43 span precision means most extracted samples are not verified
  feedback; the training results show such noisy data is still useful, not that the extraction
  is accurate.
- Naturally occurring feedback as defined covers only explicit textual cues; a user silently
  moving on to another question is an implicit signal that the method does not attempt to
  capture.
- The 31%-60% win rates reported by Eurus-RM-7b and FsfairX-LLaMA3-RM-v0.1 for the 1.4B and
  2.8B models are evidence that those reward models judge small models poorly, not that finetuning
  on extracted feedback failed at those sizes.
- Asking the extraction model for a confidence level was tested and found ineffective, so
  confidence filtering is not part of the released extraction pipeline.
links_extra:
  dataset: https://huggingface.co/datasets/shachardon/naturally_occurring_feedback
  code: https://github.com/shachardon/naturally_occurring_feedback
---
