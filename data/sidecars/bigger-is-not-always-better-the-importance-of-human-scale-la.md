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
- ask:
    plain: why would researchers deliberately train a language model on only as much text
      as a child hears?
    jargon: how does training on trillions of tokens compromise the use of language models
      as psycholinguistic models of acquisition and as surprisal estimators?
    task: how do I justify a small-corpus pretraining setup to reviewers who expect web-scale
      data?
    practitioner: if I care about cognitive modelling rather than benchmark scores, should
      I be worried that my model saw far more text than a person ever could?
  answered_by:
  - human-scale-argument
  - not-cognitively-plausible
- ask:
    plain: what was the competition where teams trained language models on a child-sized amount
      of text, and how many took part?
    jargon: what were the data budget and participation figures for the first BabyLM shared
      task at CoNLL 2023?
    task: where do I find a set of openly released English language models pretrained on 100
      million words or fewer?
    practitioner: is there an existing shared task and model pool I can build on instead of
      designing my own small-data pretraining benchmark?
  answered_by:
  - babylm-corpus-scale
  - participation
- ask:
    plain: how well can a language model do on English grammar tests if it only ever reads
      100 million words?
    jargon: what BLiMP accuracy do 100M-word and 10M-word pretrained models reach relative
      to a Llama 2 70B skyline?
    task: how do I find out what grammatical accuracy is achievable at my training budget
      before I commit compute?
    practitioner: if I can only afford a small pretraining corpus, how much grammatical ability
      am I giving up compared with a huge model?
  answered_by:
  - near-human-blimp
  - strict-vs-strict-small
- ask:
    plain: does feeding a model easy text before hard text actually help when there is little
      data?
    jargon: did curriculum learning yield measurable gains over the BabyLM baselines, and
      which intervention classes did?
    task: which pretraining interventions should I spend my effort on when my corpus is only
      10 to 100 million words?
    practitioner: should I bother building a difficulty-ordered curriculum for my small-data
      pretraining run?
  answered_by:
  - curriculum-learning-negative
- ask:
    plain: which encoder architecture is a good default for pretraining on a small English
      corpus?
    jargon: do ELC-BERT's layer-wise skip connections beat LTG-BERT when both are pretrained
      on the 100M-word corpus?
    task: which architecture should I start from for a data-efficient masked language model?
    practitioner: is it worth adopting ELC-BERT over LTG-BERT for my 100-million-word pretraining
      run?
  answered_by:
  - ltg-bert-recommendation
- ask:
    plain: how many passes over a small text corpus are worth doing before the returns dry
      up?
    jargon: how much of the winning BabyLM result is attributable to hundreds of epochs rather
      than to architecture, and where do BLiMP and GLUE gains saturate?
    task: how do I set the number of training epochs for a 100-million-word pretraining corpus?
    practitioner: can I get most of the benefit in 20 epochs, or do I need to budget for hundreds
      of passes over my data?
  answered_by:
  - epochs-explain-win
  - diminishing-returns-epochs
- ask:
    plain: can a model pick up hard grammar rules like which questions you cannot ask, from
      a child-sized amount of text?
    jargon: do models pretrained on 100M words perform worse on island constraints, filler-gap
      dependencies and subject-aux inversion than on other BLiMP paradigms?
    task: how do I check whether phenomena at the centre of nativist arguments are learnable
      at human-scale data volumes?
    practitioner: can I cite small-corpus model results when arguing about whether syntax
      has to be innate?
  answered_by:
  - pos-relevant-tasks
  - near-human-blimp
- ask:
    plain: did giving language models pictures or speech alongside text make them learn more
      from less?
    jargon: did BabyLM Loose-track submissions with non-linguistic supervision outperform
      text-only Strict-Small models in aggregate?
    task: how do I decide whether to add images, audio or code to a small pretraining corpus?
    practitioner: should I add multimodal data to squeeze more out of my 10 million words
      of text?
  answered_by:
  - loose-track-worse
- ask:
    plain: do models trained on small corpora learn real grammar rules or just shallow word
      cues?
    jargon: what do MSGS scores indicate about linguistic versus surface generalization preference
      in the top BabyLM models?
    task: how do I test whether a small pretrained model prefers linguistic over surface features?
    practitioner: can I trust that my small-data model's grammar score reflects genuine generalization
      rather than shortcut features?
  answered_by:
  - msgs-linguistic-preference
- ask:
    plain: what should I read first about training language models on the amount of language
      a child actually hears?
    jargon: which paper is the entry point for developmentally plausible, data-efficient pretraining
      and its bearing on cognitive modelling?
    task: where do I start a literature review on human-scale language model pretraining?
    practitioner: which single paper should I hand a student who wants to work on child-scale
      language model training?
  answered_by:
  - human-scale-argument
  - babylm-corpus-scale
  - not-cognitively-plausible
- ask:
    plain: do the models that won the child-scale training competition learn anything like
      the way children do?
    jargon: can BabyLM winning systems be treated as cognitively plausible accounts of child
      language acquisition?
    task: how do I tell whether a data-efficient pretrained model is usable as a model of
      human acquisition?
    practitioner: can I present a small-corpus language model as a simulation of how a child
      learns language?
  answered_by:
  - not-cognitively-plausible
- ask:
    plain: how much grammar and language understanding do you lose going from 100 million
      training words down to 10 million?
    jargon: what is the BLiMP and GLUE penalty for the Strict-Small 10M budget relative to
      the 100M Strict budget?
    task: how do I estimate the cost of shrinking my pretraining corpus by a factor of 10?
    practitioner: if I can only collect 10 million words instead of 100 million, how much
      performance should I expect to sacrifice?
  answered_by:
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
