<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced via a forced tool call) + 3 repair rounds. Every claim, number
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

Then promote it:  python scripts/draft_sidecars.py --accept an-autonomous-debating-system

Stamp: spec=d57862840a90 checks=1 body=3ea5ad6ac31d
-->
---
key: slonim2021autonomous
coined: Project Debater
gloss: an autonomous system that prepares and delivers spoken argumentative speeches in a
  competitive debate against a human
one_liner: Project Debater is an autonomous debating system that, given an unseen debate motion,
  mines arguments from a 400-million-article news corpus, draws on a manually authored argument
  knowledge base, rebuts a human opponent's recorded speech and delivers multi-minute spoken
  speeches in a full competitive debate.
claims:
- id: system-context
  kind: context
  text: Project Debater is an autonomous debating system, described in Nature, that can hold
    a full competitive debate with an expert human debater. Its pipeline covers argument mining,
    an argument knowledge base, argument rebuttal and debate construction.
  scope: As of publication in 2021, the authors state they are unaware of any other automatic
    method able to participate in a full debate; the format is a simplified parliamentary
    style with English-language motions.
- id: composite-ai-framing
  kind: context
  text: Project Debater is presented as a case for treating debate as a 'composite AI' task,
    decomposed into narrow tangible subtasks rather than solved end-to-end. The paper contrasts
    it with game-playing grand challenges such as chess, Jeopardy! and Go.
  scope: 'A position advanced in the paper''s discussion, resting on four stated properties
    of games that competitive debate lacks: a clear winner, enumerable moves, tactics humans
    need not follow, and large structured training data.'
- id: task-formulation-legacy
  kind: context
  text: The tasks of context-dependent claim detection and context-dependent evidence detection
    were formulated in the course of building Project Debater and have since become an active
    line of research in computational argumentation.
  scope: Refers to the authors' own account of subtasks introduced in their 2014-2015 publications
    underlying the system; standing within the computational argumentation community is asserted,
    not measured.
- id: opening-speech-baselines
  text: On generating an opening speech over 78 motions, Project Debater scored higher than
    every baseline tested and below human expert debaters. Baselines included a multi-document
    summarizer, a fine-tuned GPT-2, ArgumenText retrieval and 2 human-curated argument concatenations.
  evidence: Figure 3a
  scope: Crowd annotators, 15 per speech, rating agreement with 'This speech is a good opening
    speech for supporting the topic' on a 1-5 scale; Arg-Human1 covers only 23 motions and
    Human Expert only 77; P < 0.05 for both directions.
- id: full-debate-decent
  text: In three-speech debates over 78 motions, the average annotator score for Project Debater
    reached at least 4 out of 5 on 50 motions. That means crowd annotators perceived 'decent
    performance' in at least 64% of motions.
  evidence: Figure 3b and the 'Evaluation of the final system' section
  scope: 20 annotators per debate set, judging only the system's opening speech S1 and third
    speech S3 read as text; the opposing speech S2 was recorded by a human expert replying
    to a different opening speech.
- id: above-neutral
  text: Project Debater's average annotator score exceeded the neutral value of 3 for all
    but 3 of the 78 evaluated debate motions.
  evidence: The 'Evaluation of the final system' section
  scope: Crowd annotation of read transcripts on a 1-5 agreement scale, not live audience
    voting, and against 2 simple controls.
- id: controls-beaten
  text: Project Debater scored significantly higher (P < 0.05) than both control conditions
    in the full-debate evaluation. The 'Mixed Debater Control' used a system third speech
    generated for a different motion, and the 'Baselines Control' used fully automatic baseline
    opening speeches.
  evidence: Figure 3b
  scope: 78 motions, 20 crowd annotators per three-speech set, 95% bootstrap confidence intervals;
    the controls were designed to validate the labelling task rather than as competitive debating
    systems.
- id: content-volume-quality
  text: 'Motions on which Project Debater scored well produced far more speech content: ''high'',
    ''medium'' and ''low'' motions averaged 1,496, 1,155 and 793 total words across the three
    speeches respectively.'
  evidence: The 'In-depth analysis' section
  scope: An independent set of 36 motions split by in-house annotator score into 12 'high'
    (above 3.5), 11 'medium' (3-3.5) and 11 'low' (below 3).
- id: mined-content-gap
  text: Across 5 content types covering the whole system output, 'low'-scoring motions had
    less content than 'high'-scoring ones for every type, with the largest gap in mined arguments.
  evidence: Figure 4a
  scope: Average word counts over the 11 'low' and 12 'high' motions of the second, 36-motion
    evaluation set.
- id: canned-text-share
  text: Conventional canned text accounted for less than 18% of Project Debater's speech content,
    with mined arguments contributing 41.8% and argument knowledge base content 27.0%.
  evidence: Figure 4b
  scope: All speeches for the 78 motions of the first evaluation set; the canned share is
    17.6%, rebuttal 11.3% and rebuttal leads 2.4%.
- id: error-types
  text: Extensive errors recurring through a whole speech, such as an entirely off-topic match
    of argument knowledge base classes, occurred only in Project Debater's lowest-scoring
    motion group. Local errors such as argument stance misclassification appeared in almost
    all motions, including the highest-scoring ones.
  evidence: The 'In-depth analysis' section
  scope: Qualitative error analysis over the independent 36-motion set graded by in-house
    annotators; local error categories were stance misclassification, off-topic elements and
    elements incoherent without additional context.
- id: debut-vote-imbalance
  text: In the February 2019 public debut on subsidizing preschool, 79% of the audience favoured
    the motion before the debate and 13% opposed it. That left Project Debater 21% of the
    audience to convince against 87% available to its human opponent.
  evidence: The 'Evaluation and results' section
  scope: A single live event against debate champion H. Natarajan, on a motion absent from
    the system's training data; separate from the 78-motion crowd-annotation evaluation that
    produced the paper's scores.
qa:
- q:
  - Can an AI system hold a real debate against a human?
  - What paper should I read on autonomous debating systems?
  - Where should I start reading about computational argumentation systems that debate humans?
  answers:
  - system-context
  - task-formulation-legacy
- q:
  - How well does Project Debater compare to GPT-2 or summarization baselines at writing an
    opening speech?
  - Does an argument-mining debating system beat a language model at generating a debate speech?
  - What baselines were used to evaluate automatic opening speech generation?
  answers:
  - opening-speech-baselines
- q:
  - How often was Project Debater judged to perform decently in a debate?
  - What fraction of debate motions did the autonomous debating system handle acceptably?
  - How were full debates by an automatic debater scored by annotators?
  answers:
  - full-debate-decent
  - above-neutral
- q:
  - Was the Project Debater evaluation checked against control conditions?
  - How did the debating system compare to mismatched-motion and baseline controls?
  answers:
  - controls-beaten
- q:
  - Why does an autonomous debating system do badly on some motions?
  - What distinguishes topics where Project Debater performs poorly from ones where it performs
    well?
  - Does the amount of content in a generated debate speech predict its quality?
  answers:
  - content-volume-quality
  - mined-content-gap
- q:
  - How much of Project Debater's speeches is pre-written boilerplate?
  - Is an autonomous debating system just reciting canned text?
  - What is the breakdown of content types in generated debate speeches?
  answers:
  - canned-text-share
- q:
  - What kinds of mistakes does an automatic debating system make?
  - What errors were found in Project Debater's generated speeches?
  answers:
  - error-types
- q:
  - Did Project Debater win its public debate against a human champion?
  - How did the audience vote in the 2019 Project Debater debut debate?
  - Why is audience voting a poor way to evaluate a debating system?
  answers:
  - debut-vote-imbalance
- q:
  - Why is debating harder for AI than chess or Go?
  - How does competitive debate differ from AI grand challenges based on games?
  - What is meant by composite AI as opposed to narrow AI?
  answers:
  - composite-ai-framing
- q:
  - Was Project Debater built as a single end-to-end neural model?
  - What is the architecture of an autonomous debating system?
  answers:
  - system-context
  - composite-ai-framing
misreadings:
- 'Project Debater was not shown to win debates against humans: in the systematic 78-motion
  evaluation its scores were significantly lower than those of human expert debaters, and
  the paper''s conclusion is that debating with humans remains a territory where humans prevail.'
- The 64% figure is not a win rate. It is the share of 78 motions for which crowd annotators,
  reading transcripts, gave an average score of at least 4 out of 5 to the statement that
  the first speaker performed decently.
- The main evaluation is not the televised February 2019 debate against H. Natarajan. That
  single event is described for context, while the paper's results come from crowd annotation
  over 78 motions and a further independent set of 36 motions.
- Project Debater is not an end-to-end neural language model. It is a modular pipeline of
  argument mining, a manually authored argument knowledge base, rebuttal and rule-based debate
  construction, and a fine-tuned GPT-2 was one of the baselines it was compared against.
- 'The argument knowledge base is not automatically learned content: its principled arguments,
  counter-arguments and examples are authored manually, or extracted automatically and then
  manually edited.'
terminology:
  motion: The resolution being debated, announced to both sides before a debate begins; in
    the Project Debater academic cloud services the same notion is called a 'topic'.
  argument knowledge base (AKB): A collection of manually authored or manually edited principled
    arguments, counter-arguments, quotes, analogies and framings, grouped into thematic classes
    that apply to whole families of debate motions rather than to a single motion.
  leads: Claims that a debating system predicts its opponent may raise, compiled in advance
    from argument mining, the argument knowledge base and iDebate, and then matched against
    the transcript of the opponent's actual speech to trigger a rebuttal.
  context-dependent claim detection: The task of finding, in a large corpus, concise statements
    that take a clear stance towards a specific given motion, as opposed to detecting claims
    independently of any topic.
  context-dependent evidence detection: The task of finding single sentences that support
    or contest a given motion by indicating whether a relevant claim is true, rather than
    merely expressing a belief or claim.
  extensive error: A speech-level failure of a debating system in which the same type of mistake
    recurs throughout the speech, for example an argument class match that makes a large amount
    of the content off-topic, as distinguished from a local error affecting one content unit.
---
