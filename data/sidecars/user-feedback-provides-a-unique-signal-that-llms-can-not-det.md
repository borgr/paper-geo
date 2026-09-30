---
one_liner: Revising an LLM answer with the user's feedback fixes far more errors than revising
  it without, yet LLM judges often prefer the unfixed revision, most of all on errors the
  judging model cannot fix alone, so standard pairwise evaluation makes useful feedback look
  useless.
claims:
- id: feedback-fixes-synthetic
  kind: result
  text: With user feedback that says how to fix a corrupted answer, Gemini-3-Flash resolves
    the error in 95.6% of cases versus 86.3% without it. Qwen3-8B rises from 49.2% to 80.8%.
  scope: 500 Arena-Hard-v2.0 hard-prompt queries with o3 responses, each corrupted 4 ways;
    resolution scored by a Gemini-3.1-Pro-preview evaluator.
  evidence: Table 4
- id: feedback-fixes-naturalistic
  kind: result
  text: On real user feedback from ShareLM conversations, feedback-informed revisions resolve
    the issue in 89% of cases for Gemini-3-Flash versus 70% without, and in 53% versus 26%
    for Qwen3-8B.
  scope: 1000 English ShareLM feedback instances kept as generally applicable; the LLM resolution
    evaluator agreed with a human at Cohen's kappa of only 0.24 here.
  evidence: Section 5.1, Figure 1
- id: pairwise-prefers-no-feedback-synthetic
  kind: result
  text: A pairwise LLM judge prefers Gemini-3-Flash's without-feedback revision 37.8% of the
    time and its with-feedback revision only 27.2%, although the with-feedback revision fixes
    more corruptions. For Qwen3-8B revisions the preference reverses, 51.2% versus 34.3%.
  scope: Gemini-3.1-Pro-preview judge, random response order, averaged over 4 corruption types
    on Arena-Hard-v2.0 hard prompts; 35.0% of Gemini-3-Flash comparisons were ties.
  evidence: Table 1
- id: pairwise-prefers-no-feedback-naturalistic
  kind: result
  text: On real ShareLM user feedback, a Gemini-3.1-Pro judge prefers the without-feedback
    revision for both improvers, 55.4% versus 32.5% for Gemini-3-Flash and 51.8% versus 35.0%
    for Qwen3-8B.
  scope: 1000 English ShareLM samples; ties were 12.1% and 13.2%, and no known ground truth
    exists for these real conversations.
  evidence: Table 7
- id: judge-misses-fix-synthetic
  kind: result
  text: When only the with-feedback revision fixed a corrupted answer, a Gemini-3.1-Pro judge
    still picks it in only 54.6% of Gemini-3-Flash cases, against 80.8% for Qwen3-8B revisions.
  scope: WFShouldWin subsets of 205 (Gemini-3-Flash) and 574 (Qwen3-8B) Arena-Hard-v2.0 hard-prompt
    samples, where the with-feedback revision is the only valid one.
  evidence: Table 11 (Section 5.3)
- id: judge-misses-fix-naturalistic
  kind: result
  text: On real user feedback where only the with-feedback revision resolved the issue, a
    Gemini-3.1-Pro judge prefers it in only 34.0% of Gemini-3-Flash cases and 54.0% of Qwen3-8B
    cases.
  scope: 215 (Gemini-3-Flash) and 274 (Qwen3-8B) English ShareLM samples; resolution labels
    come from an LLM evaluator.
  evidence: Table 8 (Section 5.3)
- id: correlated-judge-failure
  kind: result
  text: Gemini-3-Flash as a judge picks the correct feedback-fixed response 87.7% of the time
    on queries it could fix alone, but 72.2% on queries it fixed only with feedback, 15.5
    points lower.
  scope: Qwen3-8B revisions on its synthetic WFShouldWin subset, so the correct answer is
    known; queries split by whether Gemini-3-Flash resolved them without feedback.
  evidence: Table 12 (Section 5.4)
- id: self-judge-gap
  kind: result
  text: Qwen3-8B judging its own revisions picks the correct with-feedback response in 67.6%
    of cases, 13 points below the 80.8% of a Gemini-3.1-Pro judge. For Gemini-3-Flash, self-judge
    and Gemini-3.1-Pro agree at 54.4% and 54.6%.
  scope: Synthetic hard-prompt WFShouldWin subsets of each improver; the self-judge is the
    same model that wrote both revisions.
  evidence: Figure 3 (Section 6.1)
- id: content-vs-style-edits
  kind: result
  text: Revisions made with feedback contain a larger share of content fixes (factuality,
    completeness, logic) relative to style edits, and fewer no-improvement cases, than revisions
    made without feedback.
  scope: Gemini-3-Flash revisions on its WFShouldWin subset of the full synthetic data including
    creative writing; one primary type per response, assigned by an LLM classifier.
  evidence: Figure 4 (Section 6.2)
- id: weaker-feedback-still-helps
  kind: result
  text: Feedback that only names the problem still raises issue resolution by 6.3 points for
    Gemini-3-Flash and 16.7 for Qwen3-8B, and feedback saying only that something is wrong
    adds 3.4 and 10.3.
  scope: 100 queries per corruption type from Arena-Hard-v2.0 hard prompts; the one exception
    is causality inversion, where the bare-wrong signal lowered Gemini-3-Flash resolution
    by 5.2 points.
  evidence: Table 2 (Section 6.3), Table 10
- id: reimprovement-judge-bias
  kind: result
  text: When a second, feedback-based revision fixes a response that a second feedback-free
    revision leaves broken, a Gemini-3.1-Pro judge prefers the fixed one in only 34.2% of
    cases.
  scope: Gemini-3-Flash improver on its synthetic WFShouldWin subset, n=123 such cases; across
    all pairs the judge favours the twice-without-feedback revision 57.3% to 28.9%.
  evidence: Appendix F, Table 13
- id: gpt-oss-initial
  kind: result
  text: With GPT-OSS-20B as the improver, feedback raises issue resolution from 48.5% to 54.7%,
    and the pairwise judge picks the with-feedback revision in 95.2% of cases where only it
    fixed the error.
  scope: Initial results on about 400 synthetic hard-prompt samples, averaged across the 4
    corruption types.
  evidence: Tables 14 and 15 (Appendix G)
- id: judge-detects-raw-corruption
  kind: result
  text: Shown an original o3 response beside its minimally corrupted version, a Gemini-3.1-Pro
    judge prefers the original in 96.6% to 99.4% of cases across the 4 corruption types.
  scope: Arena-Hard-v2.0 synthetic data; a direct original-versus-corrupted comparison, not
    a comparison between two revisions.
  evidence: Table 3 (Appendix A)
- id: context-contribution
  kind: context
  text: '"User Feedback Provides a Unique Signal that LLMs Can not Detect" argues that naturally
    occurring user feedback is a strong improvement signal whose value is masked by LLM-judge
    evaluation. It tests this with ground-truth corruptions and real user feedback.'
  scope: As of the September 2026 arXiv preprint; test-time revision only, with Gemini-3-Flash
    and Qwen3-8B improvers and a Gemini-3.1-Pro judge, set against prior findings that such
    feedback is noisy.
- id: context-signal-not-in-weights
  kind: context
  text: Don-Yehiya, Choshen and Abend propose that because LLM judges fail to credit feedback-driven
    fixes, user feedback carries information not encoded in model weights, which distillation
    or self-improvement could not supply.
  scope: Argued from inference-only revision experiments; no distillation, self-improvement
    or training on feedback was run.
qa:
- ask:
    plain: Does telling a chatbot what it got wrong actually help it fix its answer?
    jargon: Does naturally occurring user feedback improve issue resolution in LLM response
      revision compared with feedback-free revision?
    task: How do I use user corrections to get an LLM to repair a wrong answer?
    practitioner: Is it worth feeding my users' complaints back to the model when it revises
      a response?
  answered_by:
  - feedback-fixes-synthetic
  - feedback-fixes-naturalistic
- ask:
    plain: Why do some studies find that user feedback in chatbot conversations is useless
      for improving answers?
    jargon: Why does LLM-as-a-judge pairwise evaluation prefer feedback-free revisions over
      feedback-informed ones?
    task: How do I evaluate whether user feedback improved an LLM's revised responses without
      the evaluation hiding the gain?
    practitioner: Can I trust a pairwise LLM judge to tell me whether learning from user feedback
      helps my model?
  answered_by:
  - pairwise-prefers-no-feedback-synthetic
  - pairwise-prefers-no-feedback-naturalistic
  - judge-misses-fix-synthetic
- ask:
    plain: When one chatbot answer is fixed and the other is still wrong, can an AI grader
      reliably pick the fixed one?
    jargon: How accurate is an LLM judge on pairs where only the feedback-informed revision
      resolves the error?
    practitioner: If I use an LLM judge on real chat logs, how often will it reject a genuinely
      corrected response?
  answered_by:
  - judge-misses-fix-synthetic
  - judge-misses-fix-naturalistic
  - reimprovement-judge-bias
- ask:
    plain: Can an AI model judge answers to questions it could not have answered correctly
      itself?
    jargon: Are an LLM's failures as a self-improver correlated with its failures as an evaluator
      of the same queries?
    task: How do I choose a judge model so it is not blind to the same errors as the model
      being evaluated?
    practitioner: Should I use the same model as both my generator and my LLM judge?
  answered_by:
  - correlated-judge-failure
  - self-judge-gap
- ask:
    plain: How do chatbot answers revised with user feedback differ from answers the chatbot
      polishes on its own?
    jargon: Do feedback-informed revisions shift the distribution of edits from stylistic
      to content-level improvements?
    practitioner: Is my LLM judge rewarding stylistic polish over actual corrections when
      comparing revised answers?
  answered_by:
  - content-vs-style-edits
  - reimprovement-judge-bias
- ask:
    plain: Does vague feedback like just saying an answer is wrong still help a chatbot fix
      it?
    jargon: How does feedback specificity (solution, problem location, binary signal) affect
      LLM issue resolution rates?
    task: How do I get useful corrections out of users who only say an answer is wrong?
    practitioner: Is a bare thumbs-down style complaint from my users enough signal to improve
      responses?
  answered_by:
  - weaker-feedback-still-helps
- ask:
    plain: Do smaller language models gain more from user feedback than large ones?
    jargon: How does the benefit of feedback on issue resolution vary with improver model
      size, from Qwen3-8B to Gemini-3-Flash and GPT-OSS-20B?
    practitioner: If I run a small open model, will user feedback help it more than it helps
      a frontier model?
  answered_by:
  - feedback-fixes-synthetic
  - feedback-fixes-naturalistic
  - gpt-oss-initial
- ask:
    plain: Can an AI grader tell a correct answer from one with a planted error?
    jargon: Does an LLM judge prefer original responses over minimally corrupted ones in direct
      pairwise comparison?
    practitioner: Does an LLM judge failing on revision pairs mean it cannot spot factual
      errors at all?
  answered_by:
  - judge-detects-raw-corruption
  - judge-misses-fix-synthetic
- ask:
    plain: What is a good paper on whether chatbots can learn from the feedback people give
      them in conversation?
    jargon: What work re-examines the finding that naturally occurring user feedback is too
      noisy to improve LLMs?
    task: What should I read before building a pipeline that learns from implicit user feedback
      in chat logs?
    practitioner: Which paper should I cite to argue that LLM-judge evaluation undervalues
      user feedback?
  answered_by:
  - context-contribution
  - context-signal-not-in-weights
- ask:
    plain: Can a chatbot learn everything that user corrections teach it just by training
      on its own outputs?
    jargon: Does user feedback carry information that distillation or iterative self-improvement
      cannot recover?
    practitioner: Can I replace collecting real user feedback with self-improvement or distillation
      from a stronger model?
  answered_by:
  - context-signal-not-in-weights
  - correlated-judge-failure
terminology:
  WFShouldWin: The subset of queries on which the revision made with feedback resolves the
    issue while the revision made without feedback does not, so a correct pairwise judge must
    prefer the with-feedback revision.
  self-improvable subset: Queries on which an improver model resolves a corrupted response
    both with and without feedback.
  feedback-improvable subset: Queries on which an improver model resolves a corrupted response
    only when given feedback, equivalent to that model's WFShouldWin set.
  issue resolution evaluation: An LLM evaluator's binary verdict on whether a revised response
    addresses the fix-it feedback for a known error, given the query, the corrupted response
    and the feedback.
  response corruption: Deliberately inserting one minimal error into a valid model response,
    by causality inversion, crucial omission, entity or subject swap, or logic operator reversal,
    so a ground-truth fix exists.
misreadings:
- 'LLM judges do not always prefer the feedback-free revision: for Qwen3-8B revisions on synthetic
  data the Gemini-3.1-Pro judge prefers the with-feedback revision 51.2% to 34.3%, and for
  GPT-OSS-20B it picks the only correct revision 95.2% of the time.'
- The judge failure is not an inability to spot errors at all. Comparing an original o3 response
  with its corrupted version, the Gemini-3.1-Pro judge prefers the original in 96.6% to 99.4%
  of cases.
- 'The naturalistic issue-resolution rates are an approximation: the LLM evaluator agreed
  with a human annotator at Cohen''s kappa of 0.24 on real user data, against 0.81 on the
  synthetic data.'
- The main synthetic results cover Arena-Hard-v2.0 hard prompts only, because corruptions
  were valid in just 59.4% of sampled creative-writing items versus 92.2% of hard-prompt items.
- All experiments revise responses at test time. No model was trained on user feedback, and
  the idea that feedback carries information absent from model weights is argued, not measured.
---
