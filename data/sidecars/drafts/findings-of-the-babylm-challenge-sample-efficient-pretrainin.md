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
  or 100M words), scored on one common evaluation pipeline
one_liner: The first BabyLM Challenge capped pretraining at 10M or 100M words -- roughly a
  child's input -- and its winner outscored both Llama 2 70B and a full-data RoBERTa on the
  challenge's own aggregate, but only by running over 450 epochs; curriculum learning, the
  most-tried approach of 31 submissions, mostly did not help.
claims:
- id: winner-beat-trillion-word-skylines
  text: In the first BabyLM Challenge, the winning 100M-word model (ELC-BERT, built on the
    LTG-BERT architecture) scored 0.74 on the challenge's aggregate metric against 0.71 for
    Llama 2 70B and 0.70 for a fully trained RoBERTa-base, both trained on orders of magnitude
    more text.
  scope: 'The aggregate is this challenge''s own weighted metric -- BLiMP plus the BLiMP supplement
    at 50%, (Super)GLUE at 30%, MSGS at 20% -- run through the challenge''s pipeline on filtered
    task data, not a measure of general capability. (Super)GLUE is the exception and the gap
    there is large: 0.78 for ELC-BERT against 0.84 for Llama 2. Llama 2 was evaluated in-context
    on (Super)GLUE but fully finetuned on MSGS, so the two are not compared under identical
    conditions. The margin leans on MSGS, worth 20%, where Llama 2 scores 0.26.'
  evidence: Table 2, Section 7.1, Section 7.2 (Strict track), Section 5.3
- id: epochs-bought-the-headline
  text: The winning submission reached its score by training for hundreds of epochs -- over
    450 on the 100M-word corpus and over 2000 on the 10M-word one -- so it saw about as many
    training samples as BERT did despite a training set only about 3% the size.
  scope: 'This is the organizers'' own accounting of the result they awarded, in the section
    on what to change next: they write that training for hundreds of epochs is not cognitively
    plausible and does not make it easier or more accessible to test new training approaches,
    so the win does little to help achieve the challenge''s goals. The challenge budgeted
    words, not compute, and rereading the same data across epochs explicitly did not count
    as seeing more text. Future iterations, they say, may reward compute efficiency.'
  evidence: Section 8, Section 7.2 (Strict track), Section 3 (Tracks)
- id: ten-times-the-data-bought-little
  text: 'Ten times more pretraining text bought surprisingly little in the BabyLM Challenge:
    submissions in the 100M-word Strict track did not outperform the 10M-word Strict-Small
    track by a large margin, and only two Strict submissions achieved a higher (Super)GLUE
    score than the best Strict-Small model.'
  scope: 'A comparison between two pools of independently designed submissions, not a controlled
    data-scaling experiment: the tracks differ in who entered them and what they tried, not
    only in corpus size. The same winning architecture (ELC-BERT) took both tracks, which
    is the closest thing here to a matched comparison, and it did score higher on Strict (0.74)
    than Strict-Small (0.66). Strict-Small also drew far more entries -- 118 models from 29
    teams, against 24 models from 11 teams -- so its best-of pool is deeper.'
  evidence: Section 7.1, Figure 4, Table 2, Table 3
- id: curriculum-learning-largely-failed
  text: Curriculum learning was the most popular approach in the first BabyLM Challenge --
    13 of the 31 teams (41.9%) tried some variant -- and the majority of those attempts produced
    no consistent improvement across the challenge's evaluation tasks, though some showed
    modest gains.
  scope: 'A finding about this data regime, this evaluation suite and these implementations,
    not a proof that ordering training data cannot help. The attempts covered a wide space
    -- ranking by surprisal, lexical frequency, length or syntactic complexity, ordering whole
    datasets by difficulty, growing the vocabulary, and increasing objective difficulty --
    and the award for compelling negative results went to a submission (CLIMB) that tested
    that space systematically across eight curricula and found no widespread improvement.
    Several teams report the sharper version: their curriculum lost to the same data in random
    order.'
  evidence: Section 7.4 (Curriculum learning), Figure 3, Section 7.3, Appendix F (CLIMB, Oba
    et al., Opper et al.)
- id: architecture-mattered-most
  text: 'The strongest BabyLM submissions were the ones that changed the architecture rather
    than the data: LTG-BERT-based models won both the Strict and Strict-Small tracks, with
    ELC-BERT feeding each layer a weighted sum of all previous layers'' outputs.'
  scope: 'The organizers'' own reading of the submissions, from hand-coding each one into
    a typology of nine approaches -- an observational comparison across submissions that differ
    in many ways at once, not an ablation. The submitting authors'' baselines also suggest
    the LTG-BERT backbone, rather than their own incremental changes, carried most of the
    gain; ELC-BERT''s own paper reports no variant clearly beating the LTG-BERT baseline,
    only all of them beating the challenge''s RoBERTa baseline. LTG-BERT is itself a synthesis
    of four existing modifications: extra layer normalization, GEGLU feed-forward modules,
    DeBERTa-style disentangled attention, and scaled weight initialization.'
  evidence: Section 7.2 (Strict track), Section 7.4, Figures 5 and 6, Appendix F (ELC-BERT)
- id: shorter-inputs-and-sentence-level-examples-helped
  text: 'The most consistently transferable positive finding was about input format rather
    than modelling: shortening the context window (32 tokens instead of the baselines'' 128),
    using sentences rather than documents as training examples, and dropping sequence packing
    and truncation each improved results reliably.'
  scope: Assembled from several submissions' controlled comparisons rather than one experiment,
    all in the 10M-100M-word regime and on the challenge's own evaluation suite. The same
    submission that found sentence-level examples highly effective found that adding part-of-speech
    supervision and unsupervised syntactic induction had negligible impact, so the gain is
    attributed to the format, not to added linguistic signal. Whether it survives at ordinary
    pretraining scale is untested here.
  evidence: Section 7.4 (Data preprocessing; Hyperparameter tuning and model scaling), Appendix
    F (Edman and Bylinina; Cheng et al.; Govindarajan et al.)
- id: distillation-beat-its-own-teachers
  text: 'Knowledge distillation was one of the approaches that worked: Baby Llama distilled
    a 300M-parameter Llama and a 700M-parameter GPT-2, both trained on the 10M-word corpus,
    into a 58M-parameter model that outperformed the challenge baselines, both of its teachers,
    and an identical 58M model trained from scratch on the same data.'
  scope: The teachers were themselves trained only on the BabyLM corpus, as the rules required,
    so this is distillation inside a fixed data budget rather than distillation from a larger-data
    model. Other teams got gains from related setups -- an exponential-moving-average teacher,
    a latent semantic feature distribution -- while one variant of latent-target training
    degraded BLiMP on its own and only matched plain masked language modelling when combined
    with it.
  evidence: Appendix F (Baby Llama; Mean BERTS make erratic language teachers; Masked Latent
    Semantic Modeling), Section 7.4 (Teacher-student or auxiliary model)
- id: extra-modalities-did-not-help
  text: Submissions to the BabyLM Loose track, which could add unlimited non-linguistic data
    on top of the 100M-word text budget, tended to score worse in aggregate than Strict-Small
    submissions limited to 10M words of text and nothing else.
  scope: 'The organizers read this as evidence that learning from multiple modalities is a
    hard problem in its own right and that current architectures are not optimized to use
    several input types during training -- not as evidence that multimodal input cannot help
    sample efficiency. Only 8 participants entered the Loose track, and its winner used no
    extra modality at all, just text augmentation. Of the individual multimodal results: music
    pretraining gave minor gains on some subtasks, vision-and-language marginally beat the
    baselines at 10M words but not at 100M, a multiplex-network embedding cut parameters without
    gaining accuracy, and the text-and-audio submission was reported as undertrained and therefore
    hard to interpret.'
  evidence: Section 7.1, Section 7.4 (Multimodal learning), Table 2, Table 3
- id: context-recombination-won-loose
  text: 'The BabyLM Loose track was won by data augmentation rather than extra modalities:
    Contextualizer built extra training samples by combining chunks of text from different
    contexts, repeating this 40 times per chunk to get as many samples as a 4B-word dataset
    out of 100M words, and scored 0.73 aggregate.'
  scope: The comparison the paper makes is against training 40 epochs on the same samples,
    which the augmentation beat; it is not compared against a genuinely 4B-word corpus. Its
    0.58 in the MSGS column of Table 2 is the highest there, above Llama 2's 0.26, but on
    the six ambiguous MSGS subtasks reported in the appendix its macro average is -0.24 --
    the same as Llama 2's.
  evidence: Section 7.2 (Loose track), Table 2, Table 8
- id: msgs-ambiguous-subtasks-stayed-negative
  text: On the MSGS subtasks that actually pit a syntactic against a surface generalization,
    almost every model scored negative -- including both skylines -- meaning models at this
    scale prefer surface features; macro averages run from -0.01 (ELC-BERT, Strict-Small)
    and -0.10 (ELC-BERT, Strict) through -0.24 for Llama 2 to -0.37 for a fully trained RoBERTa-base.
  scope: These are Appendix D.1's macro averages over the six ambiguous subtasks, which are
    not the same numbers as the MSGS column of the headline table (0.47 for ELC-BERT Strict,
    0.58 for Contextualizer); the paper reports both without reconciling them, and the ambiguous
    subtasks are the ones that measure inductive bias. Appendix D.1's prose also says ELC-BERT
    and Contextualizer showed high positive scores on average, which its own table does not
    support -- they are the least negative, not positive. Prior work found that linguistic
    bias needs more than a billion words of pretraining, so a negative score here is the expected
    result rather than a failure of these submissions.
  evidence: Appendix D.1, Table 8, Table 2, Section 5.1.1
- id: the-bigger-skyline-was-not-the-better-one
  text: 'On targeted grammatical evaluation the smaller skyline won: RoBERTa-base scored 0.87
    on BLiMP against Llama 2 70B''s 0.84, despite Llama 2 having orders of magnitude more
    parameters and training data, and the best BabyLM submissions beat Llama 2 by a wide margin
    on island effects.'
  scope: About BLiMP and its minimal-pair scoring, not about capability in general -- the
    ordering reverses on (Super)GLUE, where Llama 2 leads at 0.84. Masked and autoregressive
    models are scored by different implementations (masked-language-model scoring for encoders),
    which is a confound in any comparison across architecture families here. Quantifiers is
    the one BLiMP suite where Llama 2 is the stronger model; most submissions cluster at mediocre
    scores on it.
  evidence: Appendix D.2, Table 2, Section 5.2.1 (Zero-shot evaluation)
- id: the-hypernym-suite-was-at-chance
  text: 'One of the five new BLiMP-supplement suites failed to separate any model from chance:
    on hypernymy, every system including both skylines scored near 0.50 (Llama 2 0.50, RoBERTa
    0.48).'
  scope: 'The organizers decline to conclude that the models lack knowledge of lexical entailment,
    for two reasons they state: the test items are somewhat unnatural logical statements that
    are out of domain for the models, and there is no strong prior reason a logically invalid
    statement should get lower probability than a valid one. A minimal-pair probe that returns
    chance for a 70B model is evidence about the probe.'
  evidence: Appendix D.3, Table 9
- id: turn-taking-rewarded-the-corpus-not-just-the-model
  text: Two of the new suites did separate models sharply -- turn-taking ran from chance to
    over 90%, and the adversarial tricky question-answer congruence items left only the top
    Strict models above chance -- and the organizers attribute part of the turn-taking result
    to transcribed dialogue being a large share of the BabyLM corpus.
  scope: 'That attribution is the important half: ELC-BERT beat the skylines on turn-taking
    at least partly because its training data matched the suite''s domain, which is a fact
    about corpus-benchmark alignment rather than about sample efficiency. On the tricky question-answer
    items the RoBERTa skyline outperformed every submission by a wide margin, so the two suites
    do not point the same way.'
  evidence: Appendix D.3, Table 9, Section 5.1.1
- id: age-of-acquisition-did-not-discriminate
  text: 'No submission beat the OPT-125M baseline at predicting children''s age of acquisition
    of words, and the whole field sat inside 0.04 months of each other: mean average deviation
    ran from 2.03 months for the Strict-Small baseline to 2.07 for the widest submission.'
  scope: An optional task that 7 of the 31 teams (22.6%) reported, so the table covers 8 submitted
    models rather than the full field. Individual sub-scores occasionally edge the baseline
    -- one Strict-Small submission on nouns, one Strict submission on predicates -- but no
    overall score does. The organizers themselves caution in a footnote that optimizing this
    task does not necessarily produce a better language model, and that it should be read
    as a measure of alignment with human learning rather than of quality.
  evidence: Appendix E, Table 11, Section 5.1.1 (Age-of-acquisition Prediction) and its footnote
- id: scores-are-not-comparable-to-published-benchmarks
  text: 'BabyLM''s (Super)GLUE and MSGS numbers cannot be compared to published results on
    those benchmarks: every evaluation example containing a word that appears fewer than twice
    in the 10M-word corpus was filtered out, so models were scored on a reduced version of
    each task.'
  scope: The paper states this limit itself -- results can only be compared between models
    evaluated on the challenge's version of these tasks. The filter controls lexical content
    only; sentence length, syntactic complexity and overall style still differ between the
    challenge corpus and standard NLP task data. (Super)GLUE was also evaluated by finetuning,
    after the organizers found zero-shot and few-shot performance at or below chance for their
    baselines.
  evidence: Appendix B, Section 5.2 (Data preprocessing), Section 5.2.1 (Finetuning), Section
    7.1
- id: corpus-composition
  text: The BabyLM pretraining corpus is 98.04M words (9.96M in the Strict-Small version)
    drawn from ten sources, about 56% of it transcribed or scripted speech and about 40% either
    intended for or suitable for children; its largest single source is OpenSubtitles at 31%,
    with child-directed speech from CHILDES making up 5%.
  scope: 'Developmentally plausible in volume and domain mix, not a corpus of child input:
    the organizers note that fewer than 10M words of transcribed child-directed speech exist
    at all, far below the 100M budget, and that the estimate the budget rests on counts all
    speech in a child''s environment including overheard speech. The Strict-Small training
    set is a random sample of the Strict one, and preprocessing is deliberately minimal --
    newlines do not reliably delimit sentences or documents.'
  evidence: Table 1, Section 4, Section 4.2, Appendix A
- id: tracks-and-budget-rules
  text: 'The first BabyLM Challenge had three tracks: Strict (100M words of the provided English
    text), Strict-Small (10M words), and Loose (100M words plus unlimited non-linguistic data),
    with the word budget covering every component of the pipeline, so an auxiliary model''s
    training text counted against it too.'
  scope: Re-reading the same data across epochs did not count as seeing more text. Text generated
    by a model trained only on a BabyLM corpus was also free. The Loose rules were relaxed
    in April 2023 to permit externally trained taggers, parsers and tokenizers, so Loose submissions
    before and after that announcement were held to different rules; work using external linguistic
    data could be published but could not win a track -- one submission that used GPT-3.5-Turbo
    to reformat the corpus is discussed in the findings while technically qualifying for no
    track.
  evidence: Section 3 (Tracks), footnote 1, Appendix F (Baby's CoThought)
- id: evaluation-suite
  text: BabyLM submissions were scored on zero-shot grammaticality (BLiMP plus a five-suite
    hidden supplement covering hypernymy, subject-auxiliary inversion, turn-taking and question-answer
    congruence), finetuned (Super)GLUE, and MSGS for inductive bias, combined 50/30/20 into
    one aggregate on a Dynabench leaderboard.
  scope: The hidden suites were released two weeks before the deadline specifically to penalize
    overfitting to BLiMP and (Super)GLUE. The 50/30/20 weighting was chosen heuristically,
    though the organizers report the track winners were stable across a range of reasonable
    weightings, and the leaderboard lets a reader reweight. Age-of-acquisition prediction
    was optional and only 7 teams (22.6%) reported it. The leaderboard remains open to submissions
    after the challenge, so its contents are not the same set as the paper's.
  evidence: Section 5.1, Section 5.1.1, Section 5.3
- id: human-level-not-reached
  text: No BabyLM submission reached human-level performance, but the top model came within
    about 3% of human accuracy on BLiMP, which led the organizers to predict human-level results
    on these benchmarks within the next few years.
  scope: 'About BLiMP specifically, against the human numbers reported in the original BLiMP
    paper; the (Super)GLUE comparison is confounded because models were finetuned with additional
    task data. The organizers state the alternative reading -- that BLiMP may not measure
    human-level linguistic competence -- and argue against it on the grounds that minimal-pair
    tests were designed to mimic linguists'' own diagnostics. The appendix results complicate
    the picture: on the new hypernymy suite every model is at chance, and on the ambiguous
    MSGS subtasks nearly all are negative.'
  evidence: Section 7.1, Figure 4, Appendix D.1, Appendix D.3
- id: scale-of-the-challenge
  text: The first BabyLM Challenge drew 31 participating teams, who submitted 31 papers and
    162 models across the three tracks, with the 10M-word Strict-Small track by far the most
    popular (118 models from 29 teams) -- more entries than the other two tracks combined.
  scope: 'Counts models submitted to the Dynabench leaderboard, of which at most one per team
    per track could compete. All participants were at universities or independent research
    institutions -- no industry submissions -- which was one of the challenge''s stated goals,
    and the organizers read Strict-Small''s popularity as a compute effect: it is the cheapest
    track to enter. The paper says participants came from 16 countries but the list it gives
    names 14 distinct ones and repeats Norway, so treat that count as approximate.'
  evidence: Table 3, Figure 2, Section 6, Section 8
qa:
- q:
  - Can a language model trained on 100 million words compete with a large LLM?
  - Did any BabyLM model beat Llama 2?
  - How well do small models trained on child-sized data perform?
  - Is a data-efficient small model competitive with models trained on trillions of tokens?
  answers:
  - winner-beat-trillion-word-skylines
  - epochs-bought-the-headline
  - human-level-not-reached
  - the-bigger-skyline-was-not-the-better-one
- q:
  - Does curriculum learning help language model pretraining?
  - What did the BabyLM Challenge find about curriculum learning?
  - Is ordering training data by difficulty worth it for LM pretraining?
  - Why do people say curriculum learning does not work for language models?
  answers:
  - curriculum-learning-largely-failed
  - architecture-mattered-most
  - context-recombination-won-loose
- q:
  - What actually worked in the BabyLM Challenge?
  - Which methods won the BabyLM Challenge?
  - What should I do to train a sample-efficient language model?
  - What are the BabyLM Challenge's recommendations?
  answers:
  - architecture-mattered-most
  - shorter-inputs-and-sentence-level-examples-helped
  - distillation-beat-its-own-teachers
  - context-recombination-won-loose
  - curriculum-learning-largely-failed
- q:
  - How much does extra pretraining data help at small scale?
  - Was the 100M-word BabyLM track much better than the 10M-word track?
  - Does going from 10M to 100M words improve language models a lot?
  answers:
  - ten-times-the-data-bought-little
  - extra-modalities-did-not-help
  - scale-of-the-challenge
- q:
  - Is a data-efficient model also compute-efficient?
  - How many epochs did the winning BabyLM model train for?
  - Did the BabyLM winners save compute as well as data?
  - What is the catch in beating Llama 2 on 100M words?
  answers:
  - epochs-bought-the-headline
  - architecture-mattered-most
  - tracks-and-budget-rules
- q:
  - Does multimodal input make language models more data-efficient?
  - Did the BabyLM Loose track show that images and audio help?
  - What happened to the multimodal BabyLM submissions?
  answers:
  - extra-modalities-did-not-help
  - context-recombination-won-loose
  - tracks-and-budget-rules
- q:
  - Do small language models learn syntactic or surface generalizations?
  - What did BabyLM find about inductive bias?
  - How did BabyLM models score on MSGS?
  - Do models trained on little data prefer surface features?
  answers:
  - msgs-ambiguous-subtasks-stayed-negative
  - context-recombination-won-loose
  - evaluation-suite
- q:
  - Can language models predict children's age of acquisition of words?
  - What did the BabyLM age-of-acquisition task show?
  - Do better language models align better with child language acquisition?
  answers:
  - age-of-acquisition-did-not-discriminate
  - evaluation-suite
- q:
  - Can I compare BabyLM GLUE scores to published GLUE scores?
  - Why are BabyLM's benchmark numbers different from the originals?
  - How was the BabyLM evaluation data filtered?
  answers:
  - scores-are-not-comparable-to-published-benchmarks
  - evaluation-suite
- q:
  - Which BabyLM evaluation tasks actually separated the models?
  - Did the BLiMP supplement work as a benchmark?
  - What are the weakest parts of the BabyLM evaluation suite?
  answers:
  - the-hypernym-suite-was-at-chance
  - turn-taking-rewarded-the-corpus-not-just-the-model
  - msgs-ambiguous-subtasks-stayed-negative
  - scores-are-not-comparable-to-published-benchmarks
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
  - epochs-bought-the-headline
- q:
  - How are BabyLM models evaluated?
  - What benchmarks does the BabyLM Challenge use?
  - How is the BabyLM aggregate score computed?
  answers:
  - evaluation-suite
  - scale-of-the-challenge
  - scores-are-not-comparable-to-published-benchmarks
- q:
  - How big was the first BabyLM Challenge?
  - How many teams entered the BabyLM Challenge?
  - Which BabyLM track was the most popular?
  answers:
  - scale-of-the-challenge
  - ten-times-the-data-bought-little
misreadings:
- It is not a claim that a 100M-word model is as good as Llama 2. The winning model beat the
  Llama 2 70B and RoBERTa-base skylines on this challenge's weighted aggregate of BLiMP, (Super)GLUE
  and MSGS, and lost clearly on (Super)GLUE (0.78 against 0.84). MSGS -- an inductive-bias
  probe worth 20% of the aggregate, where Llama 2 scores 0.26 -- is a large part of the margin.
- It is not a claim that the winner was cheap to train. It ran over 450 epochs on 100M words,
  seeing about as many samples as BERT did on roughly thirty times more text. The challenge
  capped words, not compute, and the organizers say plainly that this undercuts two of their
  three goals -- cognitive plausibility and affordability.
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
  human level overall. The (Super)GLUE comparison is confounded by finetuning, and the numbers
  are not comparable to published (Super)GLUE results at all, because every example containing
  a word that occurs fewer than twice in the 10M-word corpus was removed.'
- A positive MSGS number in the results table does not mean the model preferred the syntactic
  generalization. On the six subtasks where a syntactic and a surface generalization actually
  conflict, the appendix reports macro averages of -0.10 for the winner and -0.24 for Llama
  2 -- almost everything is negative, and the two tables are not reconciled in the paper.
- The BLiMP supplement is not a uniformly working benchmark. Its hypernymy suite leaves every
  model, including a 70B skyline, at chance, which the organizers read as a problem with the
  items rather than with the models. Turn-taking discriminates well, but partly because transcribed
  dialogue is a large share of the training corpus.
- The age-of-acquisition task did not show that small models model children well or badly.
  No submission beat the OPT-125M baseline, and every reported system falls inside 0.04 months
  of every other, so the task did not separate them. The organizers add that doing better
  on it is not the same as being a better language model.
- Not every model in the findings qualified for a track. One submission used GPT-3.5-Turbo
  to reformat the training corpus, which no track's word budget allows; the organizers discuss
  it because it is informative, not because it competed.
- '''Beat the skylines'' does not mean ''beat the bigger model everywhere''. The smaller skyline,
  RoBERTa-base, is the stronger of the two on BLiMP (0.87 to 0.84), so on grammatical minimal
  pairs the ordering by scale was already inverted before any submission was scored.'
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
    generalization and -1 for surface. Only its ambiguous subtasks measure that bias, and
    the challenge''s headline MSGS column and the appendix''s ambiguous-subtask averages are
    different numbers.'
  LTG-BERT: 'The encoder architecture, from Samuel et al. 2023, behind both top Strict-track
    submissions: a synthesis of extra layer normalization, GEGLU feed-forward modules, DeBERTa-style
    disentangled attention and scaled weight initialization. Models built on it are also characteristically
    trained for very many epochs.'
  age-of-acquisition prediction: An optional BabyLM task that converts a model's average word
    surprisals into a predicted age at which children acquire each word, scored by mean average
    deviation in months against measured ages. A measure of alignment with human acquisition,
    not of model quality.
  sample efficiency: In this challenge, performance per word of training text -- the budgeted
    quantity. It says nothing about performance per unit of compute, which is why a model
    can be extremely sample-efficient and still expensive to train, as the winner was.
links_extra:
  project: https://babylm.github.io/
  the published version (cite this): https://aclanthology.org/2023.conll-babylm.1/
  evaluation pipeline: https://github.com/babylm/evaluation-pipeline
  the pretraining corpus (240MB zip): https://github.com/babylm/babylm.github.io/raw/main/babylm_data.zip
  leaderboard: https://dynabench.org/babylm
  all submissions, predictions and scores: https://github.com/babylm/submissions2023
---
