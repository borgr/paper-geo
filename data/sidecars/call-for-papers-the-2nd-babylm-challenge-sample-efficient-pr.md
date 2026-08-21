---
one_liner: 'The 2nd BabyLM Challenge (2024/2025) asks participants to pretrain language models
  on 100M or 10M words, and changes three rules: a paper-only track replaces the loose track,
  participants may build their own corpora, and a vision-language track ships a 50% text-only,
  50% image-text corpus.'
key: choshen2024babylm2
coined: BabyLM Challenge (2nd edition)
gloss: shared task on pretraining language models with a child-sized amount of language data
  (10M or 100M words)
claims:
- id: tracks
  kind: result
  text: 'The 2nd BabyLM Challenge runs four tracks: Strict (100M words or less), Strict-small
    (10M words or less), Vision (multimodal image-text models within a 100M word budget),
    and Paper (no model required).'
  scope: Rules as stated in the 2024/2025 call for papers; the Paper track replaces the loose
    track of the 2023 edition.
  evidence: Section 3
- id: own-data
  kind: result
  text: Unlike the first BabyLM Challenge, the 2024/2025 edition lets participants construct
    their own pretraining corpora, provided they stay within the 100M-word or 10M-word budget
    and submit a datasheet for any self-built dataset.
  scope: Strict, Strict-small and Vision tracks; the organizers still provide fixed language-only
    and multimodal corpora for participants who prefer them.
  evidence: Section 4
- id: budget-counting
  kind: result
  text: 'The BabyLM word budget counts every text seen by any component of a submission: tokenizers,
    parsers, rerankers, data-augmentation models and other ancillary models all draw on the
    same 100M or 10M words.'
  scope: Synthetic data and augmentation are allowed only as a closed system, where the augmenting
    model's own training text also counts; audio and other linguistic modalities count, non-linguistic
    ones do not.
  evidence: Section 7
- id: multimodal-corpus
  kind: result
  text: 'The Vision track''s suggested corpus totals 100M words: 50M words of text-only data
    downsampled from the 100M text corpus, plus 50M words of paired image-text data covering
    roughly 2.9M images. The paired half is 27M words from Localized Narratives and 23M from
    Conceptual Captions 3M.'
  scope: Word counts are approximate; the Localized Narratives portion uses the MS-COCO and
    Open Images subsets, and the CC3M portion uses only image-caption pairs whose images were
    still valid in January 2024.
  evidence: Table 1
- id: text-corpus
  kind: result
  text: 'The updated 100M-word text-only BabyLM corpus drops the QED portion of the 2023 dataset
    in favour of a larger CHILDES share of 29M words. The remaining sources keep their previous
    relative proportions: 26M words of children''s Project Gutenberg text, 20M of OpenSubtitles,
    15M of Simple English Wikipedia, 8M of BNC dialogue and 1M of Switchboard.'
  scope: Strict-track word counts, which are approximate; QED was replaced because on inspection
    its quality was poorer than hoped.
  evidence: Table 1
- id: baselines
  kind: result
  text: The 2nd BabyLM Challenge baselines are built from the previous year's winning submissions
    rather than trained naively. The Strict and Strict-small baselines are GPT-2, LTG-BERT
    and Contextualizer, and the Vision baselines are GIT and Flamingo.
  scope: Baselines as announced in the call for papers; final released checkpoints and their
    scores are not reported in the call.
  evidence: Section 5.1
- id: epochs
  kind: result
  text: The BabyLM Challenge places no limit on the number of training epochs or on hyperparameters.
    The organizers report that in their internal results over-training beyond a couple of
    epochs gives minor gains at most.
  scope: The internal-results statement is an unquantified organizer observation; the stated
    rationale also covers engineering practice at these data scales and human re-access to
    linguistic memories.
  evidence: Section 7
- id: eval-requirements
  kind: result
  text: Submissions to the BabyLM Challenge must be able to assign a (pseudo) log-likelihood
    to a string of text and to be fine-tuned for classification, but need not be able to generate
    sequences.
  scope: The 2024 evaluation pipeline is built on catwalk so that models outside the HuggingFace
    transformers library can be submitted; Vision-track models must score text conditioned
    on an image.
  evidence: Section 5
- id: review
  kind: result
  text: BabyLM runs its own review process with acceptance based on soundness alone, planning
    to reject only submissions that make incorrect or unjustified claims. Papers are archival
    and may be up to 8 pages, with dual submission allowed but not dual publication.
  scope: Review policy as stated for the 2024/2025 edition; the presentation venue and formatting
    requirements were not yet finalized at the time of the call.
  evidence: Section 6.3
- id: grounding-negative
  kind: result
  text: The BabyLM organizers report that submissions to the first challenge did not gain
    from non-linguistic grounding, and invite the 2024/2025 vision-language track partly to
    revisit that question.
  scope: A summary statement about the 2023 edition's submissions, concerning non-linguistic
    grounding signals rather than multimodal training in general.
  evidence: Section 7
- id: context-shared-task
  kind: context
  text: The BabyLM Challenge is a recurring shared task that reorients pretraining research
    toward sample efficiency by capping training data at a developmentally plausible 10M or
    100M words. A stated goal is making pretraining research feasible on a university budget.
  scope: A shared-task call for papers, not an empirical study; the rationale is argued at
    greater length in the 2023 call and proceedings introduction by Warstadt et al. Second
    edition, run in 2024/2025.
  evidence: Section 1
- id: context-paper-track
  kind: context
  text: The 2nd BabyLM Challenge's paper-only track opens the shared task to non-model submissions,
    such as novel cognitively-inspired evaluation metrics and in-depth analyses of individual
    BabyLM models. Best-paper selection in that track is not driven by evaluation scores.
  scope: The paper track replaces the loose track used in the 2023 edition; papers may still
    include a model and report its scores.
  evidence: Section 3
qa:
- ask:
    plain: which competition asks people to train language models on only as much text as
      a child hears?
    jargon: what shared task evaluates pretraining sample efficiency under a developmentally
      plausible corpus cap?
    task: where do I start if I want to work on pretraining language models with very little
      text?
    practitioner: is there a benchmark I can enter if my lab cannot afford large-scale pretraining
      runs?
  answered_by:
  - context-shared-task
  - tracks
- ask:
    plain: what kinds of entries does the 2024/2025 sample-efficient language model pretraining
      competition accept?
    jargon: how are the 2nd BabyLM Challenge tracks split across word budgets and multimodal
      pretraining?
    task: which BabyLM track should I submit to if I want to train on images and text together?
    practitioner: can I enter a vision-language model in the 2024 BabyLM round, or is it text
      only?
  answered_by:
  - tracks
  - multimodal-corpus
- ask:
    plain: can entrants to the 2024 small-data language model competition pick their own training
      text?
    jargon: does the 2024/2025 BabyLM edition still fix the pretraining corpus, or permit
      participant-constructed corpora?
    task: how do I build my own 10M-word pretraining corpus and still be eligible for BabyLM?
    practitioner: if I curate my own child-scale training data, what documentation do I have
      to submit with it?
  answered_by:
  - own-data
- ask:
    plain: in the BabyLM competition, does text used to train a tokenizer or a data-augmentation
      model count toward the limit?
    jargon: how is the BabyLM word budget accounted across ancillary components such as tokenizers,
      parsers and rerankers?
    task: can I generate synthetic training text or use an off-the-shelf parser and still
      stay inside a 100M-word budget?
    practitioner: I want to augment my 10M words with a pretrained helper model — does that
      break the BabyLM rules?
  answered_by:
  - budget-counting
- ask:
    plain: what text and pictures make up the training data for the image-and-text part of
      the BabyLM competition?
    jargon: which caption corpora and what text/image-text split compose the BabyLM Vision
      track's 100M-word pretraining set?
    task: what should I train on if I want a multimodal model within a child-scale word budget?
    practitioner: how many images and captions do I actually get if I use the suggested BabyLM
      multimodal corpus?
  answered_by:
  - multimodal-corpus
- ask:
    plain: how did the rules about training text change for the 2024/2025 round of the small-data
      language model pretraining contest?
    jargon: what source-level composition does the updated 100M-word BabyLM text corpus use,
      and which 2023 source was dropped?
    task: how much child-directed speech do I get if I pretrain on the BabyLM strict-track
      corpus?
    practitioner: should I reuse the 2023 BabyLM corpus, or is the 2024 text mix different
      enough to matter?
  answered_by:
  - text-corpus
- ask:
    plain: what ready-made corpus is released as a starting point for entrants in the 2024/2025
      child-scale language model pretraining competition?
    jargon: which architectures serve as the 2nd BabyLM Challenge baselines for the strict
      and vision tracks?
    task: what do I need to beat to be competitive in the BabyLM strict-small track?
    practitioner: are the 2024 BabyLM baselines harder to beat than the naively trained ones
      from 2023?
  answered_by:
  - baselines
- ask:
    plain: is there any cap on how long or with what settings a BabyLM entry can be trained?
    jargon: does the BabyLM Challenge constrain epoch count or hyperparameter search, and
      what do repeated passes over 100M words buy?
    task: should I keep training more epochs on my 100M-word corpus, or is compute better
      spent elsewhere?
    practitioner: if I train 20 epochs on 10M words, am I breaking a BabyLM rule or wasting
      my time?
  answered_by:
  - epochs
- ask:
    plain: what does a model have to be able to do before the small-data pretraining competition
      can evaluate it?
    jargon: what interface must a BabyLM submission expose — pseudo-log-likelihood scoring,
      fine-tuning, generation?
    task: how do I make sure my masked language model can be scored by the BabyLM evaluation
      pipeline?
    practitioner: my model cannot generate text and is not a standard HuggingFace class —
      can I still submit it to BabyLM?
  answered_by:
  - eval-requirements
- ask:
    plain: how are write-ups submitted to the 2024/2025 sample-efficient pretraining competition
      judged, and do they count as publications?
    jargon: what are the BabyLM Challenge's reviewing criteria, page limit and archival and
      dual-submission policy?
    task: how long can I make my BabyLM write-up, and can I send the same work to another
      venue?
    practitioner: if my BabyLM model scores badly, will the write-up still be accepted?
  answered_by:
  - review
- ask:
    plain: did adding pictures help the models entered in the first round of the BabyLM competition?
    jargon: what did the first BabyLM Challenge find about non-linguistic grounding for sample-efficient
      pretraining?
    task: is it worth adding paired image-text data to a low-resource pretraining run?
    practitioner: should I bother with a multimodal setup for my 100M-word model, given what
      happened in the 2023 round?
  answered_by:
  - grounding-negative
  - multimodal-corpus
- ask:
    plain: can I enter the 2024/2025 sample-efficient pretraining competition without training
      a model at all?
    jargon: what does the 2nd BabyLM Challenge's paper-only track admit, and how is best paper
      chosen there?
    task: where can I submit a new cognitively-inspired evaluation metric or an analysis of
      an existing BabyLM model?
    practitioner: I have an analysis rather than a model — is a BabyLM submission still archival
      and reviewed?
  answered_by:
  - context-paper-track
  - review
misreadings:
- 'The 2nd BabyLM Challenge does not require using the organizers'' corpus: participants may
  build any dataset they like as long as it stays within the 100M-word or 10M-word budget
  and comes with a datasheet.'
- The 100M-word cap in the BabyLM Challenge is not a cap on tokens seen during training. Multiple
  epochs and augmentation are allowed; what is capped is the total amount of distinct text
  any component of the system learned from.
- The Vision track of the 2nd BabyLM Challenge is not evaluated on multimodal tasks alone
  — its submissions are also run on the language-only evaluation suite.
- The organizers' remark that the first challenge's submissions did not benefit from non-linguistic
  grounding is not a conclusion that grounding cannot help; the vision-language track exists
  to encourage further work on exactly that question.
- The Strict-small track's 10M-word budget is a separate track, not a smaller warm-up for
  Strict; a paper may enter several tracks with different models.
terminology:
  Strict track: BabyLM Challenge track for language models pretrained on 100M words of text
    or less, evaluated on language-only tasks.
  Strict-small track: BabyLM Challenge track for language models pretrained on 10M words of
    text or less, evaluated on language-only tasks.
  Vision track: BabyLM Challenge track for multimodal image-text models trained within a 100M
    word budget, which must be able to assign (pseudo) log-likelihoods to text conditioned
    on an image and are evaluated on both language-only and multimodal tasks.
  Paper track: BabyLM Challenge track for submissions that need not include a competition
    model, such as new cognitively-inspired evaluation metrics or analyses of an existing
    BabyLM model.
  Developmentally plausible corpus: a pretraining corpus whose size and composition approximate
    the language input a human child receives, on the order of 10M to 100M words drawn from
    sources such as child-directed speech, dialogue, subtitles and children's books.
links_extra:
  website: https://babylm.github.io/
  data: https://osf.io/ad7qg/
  submissions spreadsheet: https://docs.google.com/spreadsheets/d/182IjCUiaVYSuJq9GAwZeeb-50bxBlY4qEMOdiCh6i-g/edit?usp=sharing
---
