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

Stamp: spec=8f05813a4658 checks=pass body=90ef92278036
-->
---
one_liner: Project Debater is an autonomous debating system that decomposes competitive debate
  into modular tasks — argument mining over 400 million news articles, a curated argument
  knowledge base, speech-to-text rebuttal and rule-based speech construction — and delivers
  spoken speeches against expert human debaters.
key: slonim2021autonomous
coined: Project Debater
gloss: an autonomous system that prepares and delivers spoken debate speeches against human
  debaters
claims:
- id: opening-speech-vs-baselines
  kind: result
  text: Project Debater's opening speeches score higher than a multi-document summarization
    system (Summit), a fine-tuned GPT-2 speech generator, GPT-2-generated arguments, ArgumenText-retrieved
    arguments and two human-curated argument baselines. The same speeches score lower than
    human expert debaters' speeches, both gaps being significant at P < 0.05.
  scope: Crowd annotators rating agreement with 'This speech is a good opening speech for
    supporting the topic' on a 1-5 scale, 15 annotators per speech, over 78 motions unseen
    during development; the two human-argument baselines cover only 23 and 77 motions.
  evidence: Figure 3a
- id: decent-performance-rate
  kind: result
  text: Crowd annotators perceived Project Debater as demonstrating 'decent performance' in
    at least 64% of debate motions. The average score was 4 or higher for 50 of 78 motions,
    and above the neutral 3 for all but 3 motions.
  scope: 20 annotators per set reading 3 written speeches of unknown origin on a 1-5 agreement
    scale; only Project Debater's 2 speeches judged, against simple controls rather than a
    human debater.
  evidence: Figure 3b
- id: canned-text-share
  kind: result
  text: Less than 18% of Project Debater's generated speech content is conventional canned
    text; the rest comes from mined arguments (41.8%), the argument knowledge base (27.0%),
    rebuttal (11.3%) and rebuttal leads (2.4%).
  scope: Relative distribution of word content across all speeches for the 78 motions of the
    first evaluation set.
  evidence: Figure 4b
- id: content-quantity-drives-quality
  kind: result
  text: Speech quality in Project Debater tracks how much content the system managed to produce.
    Motions scored 'high' averaged 1,496 words across the three speeches, 'medium' 1,155 words
    and 'low' 793 words, with the largest gap in mined arguments.
  scope: Independent evaluation set of 36 motions split by in-house annotator score into high
    (12, above 3.5), medium (11, between 3 and 3.5) and low (11, below 3); strict precision-oriented
    confidence thresholds filter content out.
  evidence: Figure 4a
- id: error-taxonomy
  kind: result
  text: Project Debater's extensive errors, in which one mistake such as off-topic argument-knowledge-base
    content recurs through a whole speech, occurred only in the lowest-scoring group of motions.
    Local errors appear in almost all motions, including the highest-scoring ones.
  scope: Manual in-depth analysis of the independent set of 36 motions, grouped by in-house
    annotator scores; local errors counted are wrong argument stance, off-topic units and
    units incoherent without context.
  evidence: The 'In-depth analysis' section
- id: modular-not-end-to-end
  kind: result
  text: 'Project Debater engages in competitive debate with no end-to-end model. Four modules
    do the work: argument mining over an indexed corpus, a manually authored argument knowledge
    base, speech-to-text-driven rebuttal, and rule-based debate construction with clustering.'
  scope: Architecture as deployed for a debate format of 4-minute opening and second speeches
    and 2-minute closings, with 15 minutes of preparation after the motion is announced; argument
    knowledge base texts are hand-authored or manually edited.
  evidence: Figure 2 and the 'System architecture' section
- id: corpus-scale
  kind: result
  text: Project Debater's argument mining runs over a corpus of about 400 million newspaper
    articles from LexisNexis 2011-2018. The corpus is indexed offline by words, Wikipedia
    concepts, named entities and lexicon words, so claims and evidence for a new motion are
    retrieved at sentence level online.
  scope: The motion's topic must be discussed in this news corpus; motions whose topics are
    sparsely covered are the ones that yield low-scoring speeches.
  evidence: The 'Argument mining' section and Figure 2
- id: public-debut
  kind: result
  text: Project Debater's public debut on 11 February 2019 debated debate champion H. Natarajan
    on whether preschool should be subsidized, a motion never included in the system's training
    data. The pre-debate audience vote was 79% in favour of subsidizing preschool and 13%
    against.
  scope: A single live event; the unbalanced pre-debate vote left Project Debater at most
    21% of the audience to win over versus 87% for the human debater, which is why audience
    voting is not used as the system's evaluation metric.
  evidence: The introduction and the 'Evaluation and results' section
- id: debate-outside-comfort-zone
  kind: context
  text: Project Debater's authors argue that competitive debate lies outside the 'comfort
    zone' of classical AI grand challenges such as checkers, backgammon, chess, Jeopardy!,
    Go and StarCraft II. Debate has no clear winner, no enumerable moves, no room for strategies
    humans cannot follow, and no large body of structured training data.
  scope: A position argued in the paper's discussion rather than an experimental finding,
    contrasting debate with game competitions as of 2021; no claim is made that humans prevail
    on all real-world language tasks.
- id: composite-ai-framing
  kind: context
  text: 'Project Debater is presented as a case study in ''composite AI'': breaking a broad
    human cognitive activity into a collection of tangible narrow tasks. Solutions are built
    for each narrow task rather than seeking a single end-to-end model.'
  scope: One system built between 2012 and 2019 for one task, competitive debate; the paper
    offers no evidence about whether end-to-end models could eventually do the task.
  evidence: The Discussion section
- id: tasks-opened
  kind: context
  text: Context-dependent claim detection and context-dependent evidence detection were formulated
    in the course of Project Debater and have since become an active area of research in computational
    argumentation. Most of the system's underlying capabilities, including argument mining,
    are available as cloud services for academic research on request.
  scope: As stated by the authors in 2021; datasets built during development are released,
    the full system code is not, and academic access is by request through IBM's early-access
    programme.
qa:
- q:
  - Can an AI system hold a competitive debate against a human?
  - Has any computer program debated expert human debaters?
  - How well does Project Debater perform against human debaters?
  answers:
  - opening-speech-vs-baselines
  - decent-performance-rate
  - public-debut
- q:
  - How does Project Debater compare to GPT-2 or summarization systems at writing a debate
    speech?
  - What baselines were used to evaluate an automatically generated opening speech?
  - Does an argument-mining debate system beat a language model at speech generation?
  answers:
  - opening-speech-vs-baselines
- q:
  - How often does an autonomous debating system produce an acceptable speech?
  - What fraction of debate motions did Project Debater handle decently?
  - How was Project Debater's full-debate performance scored by annotators?
  answers:
  - decent-performance-rate
- q:
  - Are the speeches of Project Debater just canned templates?
  - How much of an automatically generated debate speech is boilerplate text?
  - Where does the content in Project Debater's speeches come from?
  answers:
  - canned-text-share
  - corpus-scale
- q:
  - Why do automatic debate speeches fail on some topics?
  - What makes an autonomous debating system perform badly on a motion?
  - What kinds of errors does Project Debater make?
  answers:
  - content-quantity-drives-quality
  - error-taxonomy
- q:
  - What is the architecture of Project Debater?
  - How is an autonomous debating system built without an end-to-end neural model?
  - What modules does a computational argumentation debate system need?
  answers:
  - modular-not-end-to-end
  - corpus-scale
- q:
  - What should I read first about computational argumentation and debate technologies?
  - Which paper established autonomous debating as an AI challenge?
  - Is there a good paper on why debating is harder for AI than board games?
  answers:
  - debate-outside-comfort-zone
  - composite-ai-framing
  - tasks-opened
- q:
  - Why is debate a harder AI grand challenge than chess or Go?
  - How does debating with humans differ from beating humans at games?
  - What does 'outside the AI comfort zone' mean for language tasks?
  answers:
  - debate-outside-comfort-zone
- q:
  - Are argument mining components from Project Debater available to researchers?
  - Which argumentation research tasks came out of the Project Debater effort?
  - Can I get access to IBM's debating technology datasets and services?
  answers:
  - tasks-opened
- q:
  - What motion did Project Debater debate in its 2019 public debut, and who won?
  - Was the audience vote a fair measure of the IBM debating system's performance?
  - Did the debut debate topic appear in Project Debater's training data?
  answers:
  - public-debut
misreadings:
- 'Project Debater is not reported as beating human debaters: its speeches score significantly
  lower than human expert speeches, and the paper''s conclusion is that debate is a territory
  where humans still prevail.'
- The 64% 'decent performance' figure comes from crowd annotators reading three written speeches,
  not from an audience vote in a live debate, and only two of the three speeches were assessed.
- The public debut against H. Natarajan is not the paper's evaluation; the systematic evaluation
  is over 78 motions plus an independent set of 36, and the paper explicitly declines to treat
  the live audience vote as a reliable metric.
- 'Project Debater is not an end-to-end neural model: it is a modular pipeline of separately
  trained components plus rule-based construction, and the argument knowledge base texts are
  manually authored or manually edited.'
- 'The argument knowledge base does not make the speeches formulaic: conventional canned text
  accounts for under 18% of speech content, with the majority mined from a news corpus.'
terminology:
  motion: The resolution being debated, announced at the start of a debate; in IBM's released
    cloud services the same thing is called a 'topic'.
  argument knowledge base (AKB): A manually authored or manually edited collection of principled
    arguments, counter-arguments, analogies, quotes and framings grouped into thematic classes,
    matched to a new debate resolution by a classifier so that content reusable across debates
    can be inserted into a speech.
  leads: Claims that a debating system predicts its opponent might make, compiled in advance
    from argument mining, an argument knowledge base and iDebate, and then detected in the
    opponent's transcribed speech to trigger a prepared rebuttal.
  context-dependent claim detection: The task of finding, in a large text corpus, concise
    statements that take a clear stance towards a given debate resolution, as opposed to detecting
    claims independently of any topic.
  context-dependent evidence detection: The task of finding single sentences that support
    or contest a given debate resolution by indicating whether a relevant claim is true, rather
    than merely expressing a belief or claim.
  composite AI: Tasks tied to broad human cognitive activities that require several skills
    applied simultaneously, contrasted with 'narrow AI' tasks that are individually well defined
    and amenable to end-to-end solutions.
  extensive error: A speech-generation error in which the same type of mistake recurs throughout
    a whole speech and propagates across multiple content units, as opposed to a local error
    affecting one unit.
links_extra:
  project page: https://www.research.ibm.com/artificial-intelligence/project-debater/
  debut debate video: https://www.youtube.com/watch?v=m3u-1yttrVw
  academic access to services: https://early-access-program.debater.res.ibm.com/academic_use
  datasets: https://www.research.ibm.com/haifa/dept/vst/debating_data.shtml
  doi: https://doi.org/10.1038/s41586-021-03215-w
---
