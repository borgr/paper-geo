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
    plain: How often do people spontaneously tell a chatbot it was wrong or right during a
      conversation?
    jargon: What is the prevalence of naturally occurring user feedback in multi-turn LMSYS-Chat-1M
      dialogues, and how reliably can annotators label it?
    task: How do I estimate how much usable feedback signal is sitting in my product's chat
      logs?
    practitioner: Are there enough spontaneous user reactions in my chat logs to be worth
      mining?
  answered_by:
  - prevalence-30-percent
  - annotator-agreement
- ask:
    plain: Do newer chatbot conversation logs contain more spontaneous user reactions than
      older ones?
    jargon: Does the rate of naturally occurring feedback per human-model conversation differ
      between the 2019 Self-Feeding Chatbot corpus and LMSYS-Chat-1M?
    task: Which vintage of human-model chat logs should I mine if I want the most user feedback
      per conversation?
    practitioner: Should I bother mining older dialogue corpora for user feedback, or stick
      to recent chat logs?
  answered_by:
  - newer-data-more-feedback
- ask:
    plain: How well can a language model pick out the places where a user reacted to a chatbot's
      answer?
    jargon: What span precision and recall does Mixtral-8x7B-Instruct achieve at extracting
      and categorising naturally occurring feedback?
    task: How do I automatically locate user feedback spans in a million chat transcripts
      without hand-annotating them?
    practitioner: Is prompting an open model to find user feedback in my logs accurate enough
      to trust?
  answered_by:
  - extraction-precision-recall
- ask:
    plain: How many examples of spontaneous user feedback can be pulled out of a million chat
      conversations?
    jargon: What is the yield and positive-to-negative balance of feedback samples extracted
      from the full LMSYS-Chat-1M corpus?
    task: How much training data would I get by mining a million chat logs for user feedback?
    practitioner: Is the released naturally occurring feedback dataset big and balanced enough
      for my finetuning run?
  answered_by:
  - dataset-size
- ask:
    plain: Does training a chatbot on the approving remarks users already wrote actually make
      it better?
    jargon: Do supervised finetuning and KTO on automatically extracted naturally occurring
      feedback improve win rates over the pretrained checkpoints?
    task: How do I use mined user feedback from chat logs as training data to improve my model's
      responses?
    practitioner: If I mine feedback out of my chat logs instead of paying for preference
      annotation, will my model actually improve?
  answered_by:
  - finetune-win-rates
  - kto-preference-gain
- ask:
    plain: Is mined user feedback better training data than just any chat transcripts from
      the same source?
    jargon: Does finetuning on extracted positive feedback outperform finetuning on a size-matched
      random sample of LMSYS-Chat-1M conversations?
    task: How do I check whether gains come from the feedback signal rather than from training
      on chat-formatted text at all?
    practitioner: Should I filter my chat logs for user feedback, or just finetune on a random
      slice of them?
  answered_by:
  - beats-random-chats
- ask:
    plain: Are the complaints and corrections users write useful for training, or only their
      compliments?
    jargon: Does KTO on extracted negative feedback add anything on top of supervised finetuning
      on positive feedback?
    task: How do I get value out of the negative user reactions I mined, given they have no
      paired preferred response?
    practitioner: Is it worth running preference training on mined user complaints after I
      have already finetuned on the praise?
  answered_by:
  - kto-preference-gain
- ask:
    plain: Does a language model need a detailed list of feedback types to find user reactions
      in chat logs, or is a general instruction enough?
    jargon: How does extraction accuracy respond to dropping the feedback taxonomy from the
      prompt, or restricting it to fewer categories?
    task: How should I write the prompt that pulls user feedback out of chat logs, with or
      without category definitions?
    practitioner: Can I skip the feedback taxonomy and just ask a model for user satisfaction
      cues in my logs?
  answered_by:
  - taxonomy-needed
  - fewer-categories-not-easier
- ask:
    plain: Can you trust a language model's own confidence rating to filter which extracted
      user reactions are real?
    jargon: Is a self-reported 1-5 confidence score a usable filter for automatically extracted
      naturally occurring feedback?
    task: How do I filter out false positives from automatically extracted chat feedback?
    practitioner: Should I ask the extraction model for a confidence score and threshold on
      it?
  answered_by:
  - confidence-useless
- ask:
    plain: Can automatic scoring models be trusted to judge which of two small chatbots gave
      the better answer?
    jargon: Do top RewardBench reward models agree with human pairwise judgments for Pythia-1.4B
      and Pythia-2.8B outputs?
    task: How do I evaluate finetuned billion-parameter models without paying for human pairwise
      comparisons?
    practitioner: Can I use Eurus-RM-7b or FsfairX-LLaMA3-RM as my judge when the models I
      compare are only 1-3B parameters?
  answered_by:
  - reward-models-fail-small
- ask:
    plain: Which research showed that ordinary chat logs already contain free human feedback
      you can train on?
    jargon: What work introduced naturally occurring feedback as a scalable substitute for
      solicited preference annotation?
    task: Where do I start reading about mining preference or feedback data from real user
      conversations?
    practitioner: Is there a paper I should read before deciding to mine feedback from my
      own chat logs instead of collecting annotations?
  answered_by:
  - context-natural-feedback
  - context-taxonomy
- ask:
    plain: What kinds of reactions do people give a chatbot when its answer was wrong or right?
    jargon: How is naturally occurring user feedback categorised, and how were the user-response
      patterns adapted into the taxonomy?
    task: What categories should I use to label the user reactions I find in chat logs?
    practitioner: Which feedback types should I expect to find in my own chat logs if I adopt
      this taxonomy?
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
