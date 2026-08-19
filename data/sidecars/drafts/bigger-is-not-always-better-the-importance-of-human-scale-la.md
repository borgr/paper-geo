<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced) + a targeted repair. Every claim, number
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

Then promote it:  python scripts/draft_sidecars.py --accept bigger-is-not-always-better-the-importance-of-human-scale-la

Stamp: spec=8f05813a4658 checks=pass body=f5635532eaa1
-->
---
claims:
- id: babylm-corpus-scale
  kind: context
  text: The BabyLM Challenge, a CoNLL 2023 shared task, asked participants to pretrain language
    models on 100 million words of English or fewer. That budget is roughly the linguistic
    input available to a child in the United States by age 12.
  scope: English only, text and transcribed speech only, with no limit on compute or number
    of training epochs; the 3 tracks were Strict (100M words), Strict-Small (10M words) and
    Loose (100M words plus non-linguistic data).
- id: human-scale-argument
  kind: context
  text: Scaling training corpora to trillions of words undermines two scientific uses of language
    models in psycholinguistics, Wilcox et al. argue. Those uses are assessing poverty-of-the-stimulus
    claims and estimating word probabilities for testing surprisal theory.
  scope: An argument about neural language models used as cognitive models of language learning
    and processing, not about their engineering utility, which the paper grants is improved
    by scaling.
- id: near-human-blimp
  kind: result
  text: The best BabyLM submissions reached 0.85-0.86 on BLiMP while trained on 100 million
    words, above the Llama 2 70B skyline score of 0.84. The top model was a few percentage
    points shy of human performance on BLiMP.
  evidence: Table 1; Figure 3
  scope: BLiMP minimal-pair accuracy on English syntax; Llama 2 was evaluated on GLUE and
    SuperGLUE with in-context learning rather than fine-tuning.
- id: strict-vs-strict-small
  kind: result
  text: Cutting the BabyLM training budget from 100 million to 10 million words cost the best
    submissions about 5 points of BLiMP, 0.85 down to 0.80. The corresponding GLUE drop was
    4 points, 0.78 down to 0.74.
  evidence: Table 1
  scope: Top-3 submissions in the Strict and Strict-Small tracks; both corpora used the same
    source composition, with Strict-Small sampled at 10% from each source.
- id: loose-track-worse
  kind: result
  text: Loose-track BabyLM models, permitted extra non-linguistic data such as audio, code
    or images, tended to score lower in the aggregate than Strict-Small models trained on
    10 million words of text alone.
  evidence: Table 1; Figure 3
  scope: First BabyLM iteration only, with 2023-era architectures not designed for multimodal
    pretraining; the extra modality data was not counted against the 100M-word budget.
- id: pos-relevant-tasks
  kind: result
  text: BabyLM submissions performed about the same on BLiMP subtasks central to poverty-of-the-stimulus
    debates as on the remaining BLiMP subtasks. The POS-relevant subtasks covered island constraints,
    filler-gap dependencies and subject-aux inversion.
  evidence: Figure 4
  scope: Post-hoc partition of BLiMP subtasks by the paper's authors, averaged across submissions
    within each track, with 95% CIs across model scores; English syntax only.
- id: msgs-linguistic-preference
  kind: result
  text: All top BabyLM models except Strict-Small McGill-BERT scored positively on MSGS, indicating
    a preference for linguistic over surface generalizations comparable to Llama 2 (0.26)
    and RoBERTa-base (0.24).
  evidence: Table 1
  scope: MSGS Matthews correlation after fine-tuning on ambiguous training sets; MSGS has
    not been run with human subjects, so no human reference point exists, and Loose-track
    McGill-BERT scored -0.02.
- id: curriculum-learning-negative
  kind: result
  text: Curriculum learning was the most popular strategy among BabyLM submissions yet produced
    only marginal gains over the baselines, while data preprocessing and architectural modifications
    were the most effective strategies.
  evidence: Figure 5; Figure 6
  scope: Meta-analysis by hand-coding each submission into 9 approach categories, counting
    at most one model per participant per track; curricula tested were those participants
    chose, sorted mostly by simplicity metrics.
- id: ltg-bert-recommendation
  kind: result
  text: LTG-BERT is the architecture Wilcox et al. recommend as a starting point for small-scale
    language modeling. ELC-BERT's added layer-wise skip connections gave no advantage over
    it when both were trained for 20 epochs on the 100-million-word Strict corpus.
  evidence: Table A.2; Appendix A
  scope: Reproduction runs averaged over 3 seeds on 4 NVIDIA RTX8000 GPUs, with smaller batch
    size and shorter sequence length than the original LTG-BERT paper; the 2 models tie on
    BLiMP at 0.83.
- id: epochs-explain-win
  kind: result
  text: Training ELC-BERT and LTG-BERT for 20 epochs instead of the 450 or more used in the
    winning submission cost about 2 points on BLiMP and GLUE. It also cost about 10 points
    on the BLiMP Supplement, leaving the 20-epoch models ahead of McGill-BERT on GLUE but
    behind it on BLiMP.
  evidence: Table A.2
  scope: Reproductions on the 100-million-word Strict corpus, 3 seeds, with batch size and
    sequence length differing from the original submissions.
- id: diminishing-returns-epochs
  kind: result
  text: BLiMP gains from additional training epochs on the BabyLM corpora diminish roughly
    exponentially, so most benefit of repeated exposure arrives within the first 20 epochs.
    Strict-Small GLUE performance declines after 50 epochs.
  evidence: Figure A.8; Figure A.9
  scope: LTG-BERT on the Strict and Strict-Small corpora, losses and scores averaged over
    3 seeds; training loss correlates with BLiMP at -0.99 (Strict) and -0.95 (Strict-Small),
    but with GLUE at only 0.61 for Strict-Small.
- id: not-cognitively-plausible
  kind: context
  text: The BabyLM Challenge showed that robust linguistic generalizations are learnable from
    human-scale data, but not through cognitively plausible mechanisms. Winning systems relied
    on transformer optimization tricks, hundreds of training epochs, and large-scale data
    augmentation.
  scope: The first (2023) iteration's submissions; only 7 teams ran the optional age-of-acquisition
    evaluation, and no submission was evaluated against incremental reading-time data.
- id: participation
  kind: result
  text: The first BabyLM Challenge received 31 papers and 162 submitted models, establishing
    a population of openly released models that are all effective data-efficient learners
    of English.
  evidence: Section 'Submitted systems and results'; Figure 2
  scope: CoNLL 2023 iteration; participants could enter multiple tracks, so unique-participant
    counts per track are lower than the model count.
qa:
- q:
  - Why is training language models on trillions of words a problem for cognitive science?
  - What are the downsides of scaling for psycholinguistics?
  - Why would anyone want a language model trained on less data?
  answers:
  - human-scale-argument
  - not-cognitively-plausible
- q:
  - What is the BabyLM Challenge?
  - What was the data budget in the BabyLM shared task?
  - Which shared task asked people to train language models on child-scale data?
  answers:
  - babylm-corpus-scale
  - participation
- q:
  - How good can a language model get on grammar tests with only 100 million words of training
    data?
  - Can small language models match large ones on BLiMP?
  - Do human-scale language models come close to human grammatical performance?
  answers:
  - near-human-blimp
  - strict-vs-strict-small
- q:
  - Does curriculum learning help when pretraining data is scarce?
  - Did sorting training data from simple to complex improve BabyLM models?
  - What training strategies actually worked in the BabyLM Challenge?
  answers:
  - curriculum-learning-negative
- q:
  - Which architecture should I use for small-scale language model pretraining?
  - Is ELC-BERT better than LTG-BERT for 100M-word pretraining?
  - What model do the BabyLM organizers recommend as a starting point?
  answers:
  - ltg-bert-recommendation
- q:
  - How many epochs should a language model be trained for on a 100-million-word corpus?
  - Did the winning BabyLM model win because of its architecture or because it trained longer?
  - Do hundreds of training epochs help on small corpora?
  answers:
  - epochs-explain-win
  - diminishing-returns-epochs
- q:
  - Can neural networks learn island constraints and filler-gap dependencies from child-scale
    data?
  - What do BabyLM results say about poverty-of-the-stimulus arguments?
  - Are hard-to-learn syntactic phenomena harder for models trained on 100 million words?
  answers:
  - pos-relevant-tasks
  - near-human-blimp
- q:
  - Did adding images or audio help language models trained on limited data?
  - Does multimodal input improve sample efficiency in BabyLM submissions?
  - Were Loose-track BabyLM models better than text-only ones?
  answers:
  - loose-track-worse
- q:
  - Do small language models generalize linguistically or just memorize surface cues?
  - What did MSGS scores show about BabyLM models?
  - How can you tell whether a model's benchmark score reflects real linguistic generalization?
  answers:
  - msgs-linguistic-preference
- q:
  - What should I read about human-scale or data-efficient language modeling for psycholinguistics?
  - Which paper argues that bigger language models are not better for cognitive modeling?
  - Where should I start reading about developmentally plausible language model pretraining?
  answers:
  - human-scale-argument
  - babylm-corpus-scale
  - not-cognitively-plausible
- q:
  - Are BabyLM models cognitively plausible models of child language acquisition?
  - Did the BabyLM Challenge identify how children learn language so efficiently?
  - Do the winning small-scale models resemble human learners?
  answers:
  - not-cognitively-plausible
- q:
  - How much worse is a 10-million-word language model than a 100-million-word one?
  - Does going from 10M to 100M training words matter much for grammar benchmarks?
  answers:
  - strict-vs-strict-small
one_liner: 'Bigger is not always better: scaling language models to trillions of words weakens
  their value as cognitive models, and the first BabyLM Challenge shows that models trained
  on 100 million words or fewer reach near-human BLiMP performance -- though not by cognitively
  plausible means.'
coined: BabyLM
gloss: a language model pretrained on roughly the amount of language a child hears, 100 million
  words or less
terminology:
  BabyLM Corpus: The 100-million-word English pretraining corpus released for the BabyLM Challenge,
    in which about 56% is transcribed or scripted speech and about 40% comes from sources
    intended or suitable for children, with the rest from adult writing such as Wikipedia
    and Project Gutenberg.
  Strict, Strict-Small and Loose tracks: 'The three BabyLM Challenge entry conditions: 100
    million English training tokens (Strict), 10 million (Strict-Small), and 100 million tokens
    plus optional non-linguistic data such as audio, code or images (Loose).'
  skyline model: A large, fully-scaled reference model included for comparison rather than
    as a competitor, such as the 70-billion-parameter Llama 2 evaluated alongside 100-million-word
    models.
  POS-relevant BLiMP subtasks: 'The BLiMP minimal-pair subtasks whose phenomena have figured
    in poverty-of-the-stimulus learnability debates: island constraints, filler-gap dependencies
    and subject-aux inversion.'
  MSGS: The Mixed Signals Generalization Set, a fine-tuning benchmark that trains a model
    on labels consistent with both a linguistic and a surface generalization and then tests
    which one the model adopted, scored as a Matthews correlation where 1 is systematic linguistic
    generalization and -1 systematic surface generalization.
misreadings:
- 'A BabyLM model scoring near Llama 2 on BLiMP and GLUE is not equivalent to a large language
  model: BabyLMs generate repetitive and sometimes nonsensical text and are poor at following
  instructions or learning from in-context examples.'
- The BabyLM Challenge did not establish that models learn language the way children do --
  the winning systems used hundreds of epochs over the same corpus, low-level transformer
  optimization tricks, and data augmentation, none of which is cognitively plausible.
- The negative result for curriculum learning bears on model training regimes; it is not evidence
  that child-directed speech is useless for children, though the paper reads it as supporting
  skepticism that child-directed speech is necessary for effective learning.
- All BabyLM Challenge results are for English, so whether the same architectures and data
  efficiencies hold for typologically different languages is untested.
- 'ELC-BERT winning both Strict and Strict-Small tracks does not mean its layer-wise skip
  connections were what made it win: under a controlled 20-epoch budget it performs comparably
  to the plain LTG-BERT backbone.'
- The claim is not that scaling harms language technology performance -- the paper grants
  that scaling largely benefits applications, and locates the harm in scientific uses such
  as poverty-of-the-stimulus arguments and reading-time prediction.
---
