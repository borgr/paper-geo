<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, low effort (schema-enforced via a forced tool call) + 1 repair round. Every claim, number
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

Stamp: spec=d57862840a90 checks=pass body=5c8874bf51ec
-->
---
key: slonim2021debater
coined: Project Debater
gloss: an autonomous system that prepares and delivers spoken argumentative speeches in a
  competitive debate with a human
one_liner: Project Debater is an autonomous debating system that mines arguments from a 400-million-article
  news corpus, combines them with a hand-authored argument knowledge base and a rebuttal module,
  and delivers 4-minute spoken speeches in a competitive debate against expert human debaters.
claims:
- id: opening-speech-vs-baselines
  kind: result
  text: Project Debater's opening speeches were rated higher than a multi-document summarization
    system (Summit), a fine-tuned GPT-2 speech generator, argument-concatenation baselines
    including ArgumenText, and two human-curated argument baselines. Their scores remained
    lower than those of human expert debaters.
  scope: 78 motions unseen in training; crowd annotators, 15 per speech, rating a 1-5 agreement
    statement; P < 0.05 for both comparisons.
  evidence: Figure 3a
- id: decent-performance-rate
  kind: result
  text: Crowd annotators judged Project Debater as showing 'decent performance' in a three-speech
    debate for at least 64% of motions. Its average score was at least 4 out of 5 in 50 of
    78 motions and above the neutral 3 in all but 3 motions.
  scope: Annotators read transcripts and judged only the system's 2 speeches (S1 and S3) against
    a human-recorded opposing speech; 20 annotators per set; 2 simple controls, not a full
    human debater.
  evidence: Figure 3b
- id: content-volume-drives-quality
  kind: result
  text: 'Speech quality tracked sheer content volume: motions scored ''high'' averaged 1,496
    words across the three speeches versus 1,155 for ''medium'' and 793 for ''low'' motions,
    with the largest gap in mined arguments.'
  scope: 12 high, 11 medium and 11 low motions from an independent 36-motion set, graded by
    in-house annotators; strict precision-oriented thresholds filter candidate content out.
  evidence: Figure 4a
- id: canned-text-share
  kind: result
  text: Less than 18% of Project Debater's speech content was conventional canned text; mined
    arguments contributed 41.8% and argument-knowledge-base arguments 27.0%, with rebuttal
    at 11.3% and rebuttal leads at 2.4%.
  scope: Relative distribution across all speeches in the 78-motion first evaluation set;
    shares are of words in system output, not a measure of quality.
  evidence: Figure 4b
- id: extensive-errors-only-low
  kind: result
  text: Extensive errors, in which the same mistake recurs through a whole speech such as
    entirely off-topic argument-knowledge-base framing, occurred only in the lowest-scoring
    motions. Local errors such as stance misclassification appeared in almost all motions,
    including the highest-scoring ones.
  scope: Qualitative error analysis over an independent set of 36 motions, split into 12 high,
    11 medium and 11 low motions by in-house annotator scores.
  evidence: Section 3.8
- id: debut-vote-imbalance
  kind: result
  text: In the February 2019 public debut on subsidizing preschool, 79% of the audience already
    favoured the motion and 13% opposed it. That left Project Debater only 21% of the audience
    available to win over, against 87% for its human opponent.
  scope: One live event against H. Natarajan, on a motion absent from the system's training
    data; vote figures come from the pre-debate audience poll.
  evidence: Section 2
- id: modular-not-end-to-end
  kind: result
  text: Project Debater produces debate-length speeches through 4 orchestrated modules rather
    than a single end-to-end neural model. The modules are argument mining over indexed news
    sentences, a manually authored argument knowledge base, argument rebuttal from opponent
    speech-to-text, and rule-based debate construction with clustering.
  scope: Architecture as deployed for the 2019 debut; the argument knowledge base and its
    counter-argument mappings are hand-authored or manually edited, and iDebate data is used
    only for the few motions it covers.
  evidence: Figure 2
- id: composite-ai-framing
  kind: context
  text: The Project Debater paper argues that debating with humans sits outside the 'comfort
    zone' of AI grand challenges such as chess, Jeopardy! and Go, because debate has no clear
    winner definition, no enumerable moves, no strategy the audience can be asked to ignore,
    and no large corpus of structured debate data for training.
  scope: A position argued in the paper's discussion, not an empirical result; contrasts competitive
    debate with game-playing challenges as of publication in 2021.
  evidence: Discussion
- id: field-entry-point
  kind: context
  text: The Project Debater paper gives a full end-to-end account of a computational argumentation
    system. The project also originated task formulations including context-dependent claim
    detection and context-dependent evidence detection, which became active research areas.
  scope: Reflects the authors' account of work begun in 2012 at IBM Research; component details
    sit in Supplementary Information, and most capabilities are offered as cloud services
    for academic use rather than as open-source code.
  evidence: Section 2.0
qa:
- q:
  - How well does an automatic debating system compare with human debaters?
  - Did Project Debater beat human experts at writing an opening speech?
  - How good are machine-generated debate speeches compared with GPT-2 or summarization baselines?
  answers:
  - opening-speech-vs-baselines
  - decent-performance-rate
- q:
  - How was Project Debater evaluated without a live audience?
  - What fraction of debate topics did Project Debater handle decently?
  - How do you score a debating system when there is no agreed winner metric?
  answers:
  - decent-performance-rate
  - debut-vote-imbalance
- q:
  - What makes an automated debate speech turn out badly?
  - Why do some motions produce weak Project Debater speeches?
  - Is Project Debater's speech quality related to how much content it finds in the corpus?
  answers:
  - content-volume-drives-quality
  - extensive-errors-only-low
- q:
  - How much of Project Debater's output is pre-written boilerplate?
  - Is an autonomous debating system just templates and canned text?
  - Where does the content of the debate speeches actually come from?
  answers:
  - canned-text-share
  - modular-not-end-to-end
- q:
  - How is an autonomous debating system built?
  - Is Project Debater a single neural network?
  - What components does a system need to hold a full debate?
  answers:
  - modular-not-end-to-end
- q:
  - What should I read first about computational argumentation and debating technologies?
  - Which paper describes a complete AI debating system?
  - Where did context-dependent claim detection come from?
  answers:
  - field-entry-point
- q:
  - Why is debating harder for AI than chess or Go?
  - How does competitive debate differ from classical AI grand challenges?
  - Why can't reinforcement learning be applied to holding a debate?
  answers:
  - composite-ai-framing
- q:
  - Who won the 2019 IBM debate against a human champion?
  - What happened at the Project Debater public debut on subsidizing preschool?
  answers:
  - debut-vote-imbalance
  - decent-performance-rate
misreadings:
- 'Project Debater was not shown to beat expert human debaters: its opening-speech scores
  were significantly lower than those of human experts, and the paper''s own claim is that
  the system performs decently, not that it wins.'
- The main evaluation is not a live debate result. It rests on crowd annotators reading transcripts
  of 3 speeches over 78 motions, judging only the system's 2 speeches against simple controls
  rather than an experienced debater in a full debate.
- The audience vote at the 2019 debut is not a clean measure of who debated better; with 79%
  of the audience pre-committed in favour of the motion, the two sides had very unequal room
  to gain votes.
- Project Debater is not an end-to-end neural language model. It is a modular pipeline whose
  argument knowledge base content is manually authored or manually edited.
- '''Less than 18% canned text'' does not mean the rest was generated from scratch: the remaining
  content is largely sentences retrieved from a news corpus and texts selected from the argument
  knowledge base.'
terminology:
  motion: The resolution being debated, announced to both sides 15 min before the debate begins;
    in IBM's released cloud services the same notion is called 'topic'.
  argument knowledge base (AKB): A collection of manually authored or manually edited principled
    arguments, counter-arguments, analogies, quotes and framings grouped into thematic classes,
    matched to a new motion by a classifier so that content generalises across debates.
  claim (in argument mining): A concise statement with a clear stance towards the debate motion.
  evidence (in argument mining): A single sentence that supports or contests the motion by
    indicating whether a relevant claim or belief is true, rather than merely expressing a
    belief.
  rebuttal lead: A claim the opponent might plausibly state, compiled in advance from argument
    mining, the argument knowledge base or iDebate, and matched against the opponent's transcribed
    speech to trigger a prepared response.
  composite AI: A task associated with a broad human cognitive activity that requires several
    skills applied simultaneously, as opposed to a narrowly defined task amenable to an end-to-end
    model.
links_extra:
  project page: https://www.research.ibm.com/artificial-intelligence/project-debater/
  debut debate video: https://www.youtube.com/watch?v=m3u-1yttrVw
  datasets: https://www.research.ibm.com/haifa/dept/vst/debating_data.shtml
  academic cloud services: https://early-access-program.debater.res.ibm.com/academic_use
  doi: https://doi.org/10.1038/s41586-021-03215-w
---
