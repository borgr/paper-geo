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

Stamp: spec=551e6f04bf75 checks=pass body=b12abb7e1c08
-->
---
one_liner: The first BabyLM Challenge capped pretraining at 10M or 100M words -- roughly a
  child's input -- and its winner outscored both Llama 2 70B and a full-data RoBERTa on the
  challenge's own aggregate, but only by running over 450 epochs; curriculum learning, the
  most-tried approach of 31 submissions, mostly did not help.
claims:
- id: winner-beat-trillion-word-skylines
  text: In the first BabyLM Challenge the winning 100M-word model, ELC-BERT, scored 0.74 on
    the challenge's own aggregate, against 0.71 for Llama 2 70B and 0.70 for a fully trained
    RoBERTa-base. No submission reached human level, though the top model came within about
    3% of human BLiMP accuracy.
  scope: The aggregate weights BLiMP and its supplement at 50%, (Super)GLUE at 30% and MSGS
    at 20%, over filtered task data. Llama 2 leads on (Super)GLUE, 0.84 to 0.78, and much
    of ELC-BERT's margin comes from MSGS, where Llama 2 scores 0.26.
  evidence: Table 2 and Section 7.1; Section 7.2 (Strict track); Section 5.3 for the weighting;
    Figure 4 for the distance to human performance.
- id: where-to-start-on-child-scale-pretraining
  kind: context
  text: For what happens when pretraining is capped at a child-scale text budget, this is
    the results write-up of the first BabyLM Challenge. It covers 31 teams and 162 models
    on one shared evaluation pipeline.
  scope: True of one challenge round, on English, scored by the challenge's own aggregate
    metric. Nothing in the paper certifies this positioning.
  evidence: Section 1 and Section 6; Table 3 for the submission counts.
- id: epochs-bought-the-headline
  text: The winning submission trained for hundreds of epochs, over 450 on the 100M-word corpus
    and over 2000 on the 10M-word one, so it saw about as many samples as BERT. Its training
    set was about 3% the size of BERT's.
  scope: The challenge budgeted words, not compute, and rereading data across epochs did not
    count as seeing more text. The organizers call hundreds of epochs neither cognitively
    plausible nor cheap to reproduce.
  evidence: Section 8, Section 7.2 (Strict track), Section 3 (Tracks)
- id: ten-times-the-data-bought-little
  text: Ten times more pretraining text bought surprisingly little. Strict submissions at
    100M words did not beat the 10M-word Strict-Small ones by a large margin, and only two
    beat the best Strict-Small (Super)GLUE score.
  scope: Two pools of independently designed submissions rather than a data-scaling experiment.
    ELC-BERT took both tracks and did score higher on Strict, 0.74 against 0.66, and Strict-Small
    drew a deeper pool of 118 models.
  evidence: Section 7.1, Figure 4, Table 2, Table 3
- id: curriculum-learning-largely-failed
  text: Curriculum learning was the most popular approach in the challenge, tried in some
    form by 13 of the 31 teams. Most of those attempts produced no consistent improvement
    across the evaluation tasks, though a few showed modest gains.
  scope: One data regime, one evaluation suite and these implementations, not a proof that
    ordering training data cannot help. Several teams report losing to the same data shuffled
    at random.
  evidence: Section 7.4 (Curriculum learning), Figure 3, Section 7.3, Appendix F (CLIMB, Oba
    et al., Opper et al.)
- id: architecture-mattered-most
  text: 'The strongest submissions changed the architecture rather than the data: LTG-BERT-based
    models won both the Strict and Strict-Small tracks. The winner, ELC-BERT, feeds each layer
    a weighted sum of all previous layers'' outputs.'
  scope: An observational comparison across submissions that differ in many ways at once,
    not an ablation. ELC-BERT's own paper reports no variant clearly beating the LTG-BERT
    baseline, so the backbone carries most of the gain.
  evidence: Section 7.2 (Strict track), Section 7.4, Figures 5 and 6, Appendix F (ELC-BERT)
- id: shorter-inputs-and-sentence-level-examples-helped
  text: 'The most transferable positive finding was about input format: a 32-token context
    window instead of the baselines'' 128, sentences rather than documents as training examples,
    and no sequence packing or truncation. Each improved results reliably.'
  scope: Several submissions' controlled comparisons in the 10M-100M-word regime, on the challenge's
    own evaluation suite. The same submission saw negligible impact from added part-of-speech
    supervision, so the gain is credited to format.
  evidence: Section 7.4 (Data preprocessing; Hyperparameter tuning and model scaling), Appendix
    F (Edman and Bylinina; Cheng et al.; Govindarajan et al.)
- id: distillation-beat-its-own-teachers
  text: Baby Llama distilled a 300M-parameter Llama and a 700M-parameter GPT-2, both trained
    on the 10M-word corpus, into a 58M-parameter model. It outperformed the challenge baselines,
    both of its teachers, and an identical model trained from scratch.
  scope: The teachers were themselves trained only on the BabyLM corpus, as the rules required,
    so this is distillation inside a fixed data budget. Related setups also gained, while
    one latent-target variant degraded BLiMP alone.
  evidence: Appendix F (Baby Llama; Mean BERTS make erratic language teachers; Masked Latent
    Semantic Modeling), Section 7.4 (Teacher-student or auxiliary model)
- id: extra-modalities-did-not-help
  text: Loose-track submissions, free to add unlimited non-linguistic data, tended to score
    worse in aggregate than 10M-word Strict-Small ones, and the track was won by text augmentation
    instead. Contextualizer recombined chunks of text 40 times each and scored 0.73.
  scope: Only 8 teams entered, and the organizers read the weak aggregate as multimodal learning
    being a hard problem of its own. The augmentation was compared against 40 epochs on the
    same samples, never a real 4B-word corpus.
  evidence: Section 7.1, Section 7.4 (Multimodal learning), Section 7.2 (Loose track), Tables
    2 and 3.
- id: the-bigger-skyline-was-not-the-better-one
  text: 'Targeted evaluation inverted the ordering by scale: RoBERTa-base scored 0.87 on BLiMP
    against Llama 2 70B''s 0.84. On the MSGS subtasks where a syntactic and a surface generalization
    conflict, almost every model was negative, from -0.01 for ELC-BERT to -0.37 for RoBERTa-base.'
  scope: The BLiMP ordering reverses on (Super)GLUE, where Llama 2 leads at 0.84, and encoders
    and decoders are scored by different implementations. The MSGS figures are Appendix D.1's
    ambiguous-subtask averages, not the headline table's 0.47 and 0.58.
  evidence: Appendix D.2 and Table 2 for BLiMP; Appendix D.1 and Table 8 for the ambiguous
    MSGS subtasks; Section 5.2.1 on zero-shot scoring.
- id: turn-taking-rewarded-the-corpus-not-just-the-model
  text: 'The five new BLiMP-supplement suites behaved unevenly: hypernymy left every system
    near 0.50, both skylines included, while turn-taking ran from chance to over 90%. The
    organizers credit part of the turn-taking spread to transcribed dialogue being a large
    share of the training corpus.'
  scope: A probe returning chance for a 70B model is evidence about the probe, and the organizers
    decline to conclude that the models lack lexical entailment. On the adversarial tricky
    items the RoBERTa skyline beat every submission.
  evidence: Appendix D.3 and Table 9; Section 5.1.1 for how the suites were built.
- id: age-of-acquisition-did-not-discriminate
  text: No submission beat the OPT-125M baseline at predicting children's age of acquisition
    of words. Mean average deviation ran from 2.03 months for the Strict-Small baseline to
    2.07 for the widest submission, so the task barely separated the field.
  scope: An optional task that 7 of the 31 teams reported, so the table covers 8 models rather
    than the field. The organizers caution that optimizing it produces better alignment with
    human learning, not a better language model.
  evidence: Appendix E, Table 11, Section 5.1.1 (Age-of-acquisition Prediction) and its footnote
- id: corpus-composition
  text: The BabyLM pretraining corpus is 98.04M words, 9.96M in the Strict-Small version,
    drawn from ten sources. About 56% is transcribed or scripted speech and about 40% is child-directed
    or child-appropriate, with OpenSubtitles the largest source at 31% and CHILDES at 5%.
  scope: 'Developmentally plausible in volume and domain mix, not a corpus of child input:
    fewer than 10M words of transcribed child-directed speech exist at all. Preprocessing
    is deliberately minimal, so newlines do not reliably delimit sentences or documents.'
  evidence: Table 1, Section 4, Section 4.2, Appendix A
- id: tracks-and-budget-rules
  text: 'The first challenge drew 31 teams and 162 models across three tracks: Strict at 100M
    words of provided English text, Strict-Small at 10M, and Loose at 100M plus unlimited
    non-linguistic data. The word budget covered the whole pipeline, so an auxiliary model''s
    training text counted too.'
  scope: Rereading data across epochs did not count as seeing more text. Strict-Small was
    by far the most popular at 118 models from 29 teams, which the organizers read as a compute
    effect. All participants were academic or independent groups.
  evidence: Section 3 (Tracks) and footnote 1; Table 3 and Figure 2 for the counts; Section
    6 on who participated.
- id: evaluation-suite
  text: Submissions were scored on zero-shot grammaticality, finetuned (Super)GLUE and MSGS,
    combined 50/30/20 into one aggregate on a Dynabench leaderboard. Every evaluation example
    containing a word that appears fewer than twice in the 10M-word corpus was filtered out.
  scope: So the (Super)GLUE and MSGS numbers are comparable only between models run through
    this pipeline, never with published results. The grammaticality half is BLiMP plus a hidden
    five-suite supplement released two weeks before the deadline.
  evidence: Section 5.1 and Section 5.1.1; Section 5.3 for the weighting; Appendix B and Section
    5.2 for the vocabulary filter.
qa:
- q:
  - What did the first BabyLM Challenge find?
  - Where should I start on sample-efficient language model pretraining?
  - How well can a language model learn from a child-sized amount of text?
  answers:
  - where-to-start-on-child-scale-pretraining
- q:
  - Can a language model trained on 100 million words compete with a large LLM?
  - Did any BabyLM model beat Llama 2?
  - How well do small models trained on child-sized data perform?
  - Is a data-efficient small model competitive with models trained on trillions of tokens?
  answers:
  - winner-beat-trillion-word-skylines
  - epochs-bought-the-headline
  - the-bigger-skyline-was-not-the-better-one
- q:
  - Does curriculum learning help language model pretraining?
  - What did the BabyLM Challenge find about curriculum learning?
  - Is ordering training data by difficulty worth it for LM pretraining?
  - Why do people say curriculum learning does not work for language models?
  answers:
  - curriculum-learning-largely-failed
  - architecture-mattered-most
  - extra-modalities-did-not-help
- q:
  - What actually worked in the BabyLM Challenge?
  - Which methods won the BabyLM Challenge?
  - What should I do to train a sample-efficient language model?
  - What are the BabyLM Challenge's recommendations?
  answers:
  - architecture-mattered-most
  - shorter-inputs-and-sentence-level-examples-helped
  - distillation-beat-its-own-teachers
  - extra-modalities-did-not-help
  - curriculum-learning-largely-failed
- q:
  - How much does extra pretraining data help at small scale?
  - Was the 100M-word BabyLM track much better than the 10M-word track?
  - Does going from 10M to 100M words improve language models a lot?
  answers:
  - ten-times-the-data-bought-little
  - extra-modalities-did-not-help
  - tracks-and-budget-rules
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
  - tracks-and-budget-rules
- q:
  - Do small language models learn syntactic or surface generalizations?
  - What did BabyLM find about inductive bias?
  - How did BabyLM models score on MSGS?
  - Do models trained on little data prefer surface features?
  answers:
  - the-bigger-skyline-was-not-the-better-one
  - extra-modalities-did-not-help
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
  - evaluation-suite
- q:
  - Which BabyLM evaluation tasks actually separated the models?
  - Did the BLiMP supplement work as a benchmark?
  - What are the weakest parts of the BabyLM evaluation suite?
  answers:
  - turn-taking-rewarded-the-corpus-not-just-the-model
  - the-bigger-skyline-was-not-the-better-one
  - evaluation-suite
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
  - tracks-and-budget-rules
- q:
  - How big was the first BabyLM Challenge?
  - How many teams entered the BabyLM Challenge?
  - Which BabyLM track was the most popular?
  answers:
  - tracks-and-budget-rules
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
  2 -- almost everything is negative, the two tables are not reconciled, and Appendix D.1's
  prose calls those scores high and positive when its own table does not.
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
- 'The participant count is approximate: the paper says 16 countries, while the list it gives
  names 14 distinct ones and repeats Norway.'
terminology:
  BabyLM Challenge: A shared task, first run at CoNLL 2023, in which participants pretrain
    a language model on a fixed budget of English text roughly the size of a child's input
    (10M or 100M words) and are compared on one shared evaluation pipeline. Repeated annually
    since.
  Strict / Strict-Small / Loose: 'The three tracks of the first challenge: 100M words of the
    provided text, 10M words of it, and 100M words plus unlimited non-linguistic data. The
    budget covers the whole pipeline, so text used to train an auxiliary model counts against
    it.'
  developmentally plausible corpus: 'A corpus constrained in both volume and domain to resemble
    a child''s language input: under 100M words, mostly transcribed speech, about 40% of it
    child-directed or child-appropriate. Not a claim that its contents are what any particular
    child hears.'
  skyline: A reference model deliberately trained outside a challenge's limits, run through
    the same evaluation pipeline to show what a much larger data budget buys -- in the first
    BabyLM Challenge, Llama 2 70B and a fully trained RoBERTa-base. The opposite bookend to
    a baseline. Llama 2 was scored in context on (Super)GLUE but finetuned on MSGS, so the
    two skylines and the submissions are not all compared under identical conditions.
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
---
