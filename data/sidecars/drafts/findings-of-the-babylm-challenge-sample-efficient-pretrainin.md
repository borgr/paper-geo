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

Then promote it:  python scripts/draft_sidecars.py --accept findings-of-the-babylm-challenge-sample-efficient-pretrainin
-->
---
coined: BabyLM Challenge
gloss: a shared task on pretraining language models from a child-sized amount of text (10M
  or 100M words)
one_liner: The first BabyLM Challenge capped pretraining at 100M words -- about what a child
  hears by adolescence -- and its winner beat Llama 2 70B on the challenge's own aggregate,
  while curriculum learning, the most-tried approach among 31 submissions, largely did not
  help.
claims:
- id: winner-beat-trillion-word-skylines
  text: In the first BabyLM Challenge, the winning 100M-word model (ELC-BERT, built on the
    LTG-BERT architecture) scored 0.74 on the challenge's aggregate metric against 0.71 for
    Llama 2 70B and 0.70 for a fully trained RoBERTa-base, both of which were trained on orders
    of magnitude more text.
  scope: 'The aggregate is this challenge''s own weighted metric -- BLiMP plus the BLiMP supplement
    at 50%, (Super)GLUE at 30%, MSGS at 20% -- run through the challenge''s pipeline, not
    a measure of general capability. (Super)GLUE is the exception and the gap there is large:
    0.78 for ELC-BERT against 0.84 for Llama 2. Llama 2 was evaluated in-context on (Super)GLUE
    but fully finetuned on MSGS, so the two are not compared under identical conditions.'
  evidence: Table 2, Section 7.1, Section 7.2 (Strict track), Section 5.3
- id: ten-times-the-data-bought-little
  text: 'Ten times more pretraining text bought surprisingly little in the BabyLM Challenge:
    submissions in the 100M-word Strict track did not outperform the 10M-word Strict-Small
    track by a large margin, and only two Strict submissions achieved a higher (Super)GLUE
    score than the best Strict-Small model.'
  evidence: Section 7.1, Figure 4, Table 2
  scope: 'A comparison between two pools of independently designed submissions, not a controlled
    data-scaling experiment: the tracks differ in who entered them and what they tried, not
    only in corpus size. The same winning architecture (ELC-BERT) took both tracks, which
    is the closest thing here to a matched comparison, and it did score higher on Strict (0.74)
    than Strict-Small (0.66).'
- id: curriculum-learning-largely-failed
  text: Curriculum learning was the most popular approach in the first BabyLM Challenge --
    13 of the 31 teams (41.9%) tried some variant -- and the majority of those attempts produced
    no consistent improvement across the challenge's evaluation tasks, though some showed
    modest gains.
  scope: A finding about this data regime, this evaluation suite and these implementations,
    not a proof that ordering training data cannot help. The attempts covered a wide space
    -- ranking by surprisal, lexical frequency, length or syntactic complexity, ordering whole
    datasets by difficulty, growing the vocabulary, and increasing objective difficulty --
    and the award for compelling negative results went to a submission (CLIMB) that tested
    that space systematically and found no widespread improvement.
  evidence: Section 7.4 (Curriculum learning), Figure 3, Section 7.3
- id: architecture-mattered-most
  text: 'The strongest BabyLM submissions were the ones that changed the architecture rather
    than the data: LTG-BERT-based models won both the Strict and Strict-Small tracks, with
    ELC-BERT feeding each layer a weighted sum of all previous layers'' outputs and training
    for over 450 epochs on 100M words and over 2000 epochs on 10M words.'
  scope: The organizers' own reading of the submissions, from hand-coding each one into a
    typology of nine approaches -- an observational comparison across submissions that differ
    in many ways at once, not an ablation. The submitting authors' baselines also suggest
    the LTG-BERT backbone, rather than their own incremental changes, carried most of the
    gain.
  evidence: Section 7.2 (Strict track), Section 7.4, Figures 5 and 6
- id: extra-modalities-did-not-help
  text: Submissions to the BabyLM Loose track, which could add unlimited non-linguistic data
    on top of the 100M-word text budget, tended to score worse in aggregate than Strict-Small
    submissions limited to 10M words of text and nothing else.
  scope: The organizers read this as evidence that learning from multiple modalities is a
    hard problem in its own right and that current architectures are not optimized to use
    several input types during training -- not as evidence that multimodal input cannot help
    sample efficiency. Only 8 participants entered the Loose track, and its winner used no
    extra modality at all, just text augmentation.
  evidence: Section 7.1, Table 2, Table 3
- id: context-recombination-won-loose
  text: 'The BabyLM Loose track was won by data augmentation rather than extra modalities:
    Contextualizer built extra training samples by combining chunks of text from different
    contexts, repeating this 40 times per chunk to get as many samples as a 4B-word dataset
    out of 100M words, and scored 0.73 aggregate with 0.58 on MSGS.'
  scope: Its 0.58 MSGS score -- the metric for preferring linguistic over surface generalizations
    -- is the highest of any model reported in Table 2, above Llama 2's 0.26. The comparison
    the paper makes is against training 40 epochs on the same samples, which the augmentation
    beat; it is not compared against a genuinely 4B-word corpus.
  evidence: Section 7.2 (Loose track), Table 2
- id: corpus-composition
  text: The BabyLM pretraining corpus is 98.04M words (9.96M in the Strict-Small version)
    drawn from ten sources, about 56% of it transcribed or scripted speech and about 40% either
    intended for or suitable for children; its largest single source is OpenSubtitles at 31%,
    with child-directed speech from CHILDES making up 5%.
  scope: 'Developmentally plausible in volume and domain mix, not a corpus of child input:
    the organizers note that fewer than 10M words of transcribed child-directed speech exist
    at all, far below the 100M budget, and that estimates of a child''s input include overheard
    speech. The Strict-Small training set is a random sample of the Strict one, and preprocessing
    is deliberately minimal -- newlines do not reliably delimit sentences or documents.'
  evidence: Table 1, Section 4, Section 4.2
- id: tracks-and-budget-rules
  text: 'The first BabyLM Challenge had three tracks: Strict (100M words of the provided English
    text), Strict-Small (10M words), and Loose (100M words plus unlimited non-linguistic data),
    with the word budget covering every component of the pipeline, so an auxiliary model''s
    training text counted against it too.'
  scope: Re-reading the same data across epochs did not count as seeing more text. Text generated
    by a model trained only on a BabyLM corpus was also free. The Loose rules were relaxed
    in April 2023 to permit externally trained taggers, parsers and tokenizers, so Loose submissions
    before and after that announcement were held to different rules; work using external linguistic
    data could be published but could not win a track.
  evidence: Section 3 (Tracks), footnote 1
- id: evaluation-suite
  text: BabyLM submissions were scored on zero-shot grammaticality (BLiMP plus a five-suite
    hidden supplement covering hypernymy, subject-auxiliary inversion, turn-taking and question-answer
    congruence), finetuned (Super)GLUE, and MSGS for inductive bias, combined 50/30/20 into
    one aggregate on a Dynabench leaderboard.
  scope: The hidden suites were released two weeks before the deadline specifically to penalize
    overfitting to BLiMP and (Super)GLUE. (Super)GLUE examples containing any word appearing
    fewer than twice in the Strict-Small corpus were filtered out, so scores are not comparable
    to published (Super)GLUE numbers. The 50/30/20 weighting was chosen heuristically, though
    the organizers report the track winners were stable across a range of reasonable weightings.
    Age-of-acquisition prediction was optional and only 7 teams (22.6%) reported it.
  evidence: Section 5.1, Section 5.1.1, Section 5.2, Section 5.3
- id: human-level-not-reached
  text: No BabyLM submission reached human-level performance, but the top model came within
    about 3% of human accuracy on BLiMP, which led the organizers to predict human-level results
    on these benchmarks within the next few years.
  scope: About BLiMP specifically, against the human numbers reported in the original BLiMP
    paper; the (Super)GLUE comparison is confounded because models were finetuned with additional
    task data. The organizers explicitly acknowledge the alternative reading -- that BLiMP
    may not measure human-level linguistic competence -- and argue against it on the grounds
    that minimal-pair tests were designed to mimic linguists' own diagnostics.
  evidence: Section 7.1, Figure 4
- id: scale-of-the-challenge
  text: The first BabyLM Challenge drew 31 participating teams from 16 countries, who submitted
    31 papers and 162 models across the three tracks, with the 10M-word Strict-Small track
    by far the most popular (118 models from 29 teams).
  scope: Counts models submitted to the Dynabench leaderboard, of which at most one per team
    per track could compete. All participants were at universities or independent research
    institutions -- no industry submissions -- which was one of the challenge's stated goals.
  evidence: Table 3, Figure 2, Section 6
qa:
- q:
  - Can a language model trained on 100 million words compete with a large LLM?
  - Did any BabyLM model beat Llama 2?
  - How well do small models trained on child-sized data perform?
  - Is a data-efficient small model competitive with models trained on trillions of tokens?
  answers:
  - winner-beat-trillion-word-skylines
  - human-level-not-reached
  - evaluation-suite
- q:
  - Does curriculum learning help language model pretraining?
  - What did the BabyLM Challenge find about curriculum learning?
  - Is ordering training data by difficulty worth it for LM pretraining?
  - Why do people say curriculum learning does not work for language models?
  answers:
  - curriculum-learning-largely-failed
  - architecture-mattered-most
- q:
  - What actually worked in the BabyLM Challenge?
  - Which methods won the BabyLM Challenge?
  - What should I do to train a sample-efficient language model?
  - What are the BabyLM Challenge's recommendations?
  answers:
  - architecture-mattered-most
  - context-recombination-won-loose
  - winner-beat-trillion-word-skylines
  - curriculum-learning-largely-failed
- q:
  - How much does extra pretraining data help at small scale?
  - Was the 100M-word BabyLM track much better than the 10M-word track?
  - Does going from 10M to 100M words improve language models a lot?
  answers:
  - ten-times-the-data-bought-little
  - extra-modalities-did-not-help
- q:
  - Does multimodal input make language models more data-efficient?
  - Did the BabyLM Loose track show that images and audio help?
  - What happened to the multimodal BabyLM submissions?
  answers:
  - extra-modalities-did-not-help
  - context-recombination-won-loose
  - tracks-and-budget-rules
- q:
  - What data is in the BabyLM pretraining corpus?
  - Is the BabyLM dataset child-directed speech?
  - Where does the BabyLM 100M-word corpus come from?
  - What makes a corpus developmentally plausible?
  answers:
  - corpus-composition
  - tracks-and-budget-rules
- q:
  - What are the rules of the BabyLM Challenge?
  - What is the difference between the Strict, Strict-Small and Loose tracks?
  - How many words are BabyLM submissions allowed to train on?
  answers:
  - tracks-and-budget-rules
  - evaluation-suite
- q:
  - How are BabyLM models evaluated?
  - What benchmarks does the BabyLM Challenge use?
  - How is the BabyLM aggregate score computed?
  answers:
  - evaluation-suite
  - scale-of-the-challenge
misreadings:
- It is not a claim that a 100M-word model is as good as Llama 2. The winning model beat the
  Llama 2 70B and RoBERTa-base skylines on this challenge's weighted aggregate of BLiMP, (Super)GLUE
  and MSGS, and lost clearly on (Super)GLUE (0.78 against 0.84). MSGS -- an inductive-bias
  probe worth 20% of the aggregate, where Llama 2 scores 0.26 -- is a large part of the margin.
- It is not a general refutation of curriculum learning. The finding is that 13 of 31 teams
  tried it in this data regime and most saw no consistent improvement on this evaluation suite,
  with some modest gains; and the Loose track was won by a submission that reorders and recombines
  training data, which is adjacent to the same idea.
- 'The tracks are easy to invert: Strict is the 100M-word track and Strict-Small the 10M-word
  one. Loose is not a larger text budget -- it is the same 100M words plus non-linguistic
  data, and its rules changed mid-challenge to permit externally trained taggers and parsers.'
- The corpus is not child-directed speech. Around 56% is transcribed or scripted speech and
  around 40% is child-directed or child-appropriate, but the largest single source is OpenSubtitles
  (31%) and CHILDES is 5%. The organizers say plainly that fewer than 10M words of transcribed
  child-directed speech exist, far below the budget.
- The Loose track's weak aggregate is not evidence that multimodality does not help sample
  efficiency. The paper's reading is that using several input types is a hard problem of its
  own and current architectures are not built for it; only 8 teams entered, and the track's
  winner used no non-text modality.
- '''Within about 3% of human performance'' is about BLiMP alone, and no submission reached
  human level overall. The (Super)GLUE comparison is confounded by finetuning, and scores
  are not comparable to published (Super)GLUE numbers because examples with rare words were
  filtered out.'
terminology:
  BabyLM Challenge: A shared task, first run at CoNLL 2023, in which participants pretrain
    a language model on a fixed budget of English text roughly the size of a child's input
    (10M or 100M words) and are compared on one shared evaluation pipeline. Repeated annually
    since.
  Strict / Strict-Small / Loose: 'The three tracks of the first challenge: 100M words of the
    provided text, 10M words of it, and 100M words plus unlimited non-linguistic data. The
    budget covers the whole pipeline, so text used to train an auxiliary model counts against
    it.'
  developmentally plausible corpus: Here, a corpus constrained in both volume and domain to
    resemble a child's language input -- under 100M words, mostly transcribed speech, about
    40% child-directed or child-appropriate. Not a claim that its contents are what any particular
    child hears.
  skyline: This paper's term for a reference model deliberately trained outside the challenge's
    limits -- Llama 2 70B and a fully trained RoBERTa-base -- run through the same evaluation
    pipeline to show what much larger data budgets buy. The opposite bookend to a baseline.
  BLiMP supplement: 'Five minimal-pair test suites written for this challenge and released
    two weeks before the deadline, covering dialogue and question phenomena BLiMP does not:
    hypernymy, subject-auxiliary inversion, turn-taking, question-answer congruence, plus
    the tricky-distractor cases.'
  MSGS: 'The Mixed Signals Generalization Set, a finetuning probe of inductive bias: a model
    is trained where a syntactic and a surface generalization are perfectly correlated, then
    tested where they conflict. Scored by Matthews correlation, +1 for systematic linguistic
    generalization and -1 for surface.'
links_extra:
  code: https://github.com/babylm/evaluation-pipeline
  data: https://github.com/babylm/babylm.github.io/raw/main/babylm_data.zip
  project: https://babylm.github.io/
  leaderboard: https://dynabench.org/babylm
  submissions: https://github.com/babylm/submissions2023
---
