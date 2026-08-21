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
    practitioner: Where should I start reading about sample-efficient pretraining on developmentally
      plausible data?
    unsorted:
    - What is the BabyLM Challenge about?
    - Which shared task limits language model pretraining to a child-sized amount of data?
  answered_by:
  - context-shared-task
  - tracks
- ask:
    practitioner: How many words am I allowed to pretrain on in the 2024 sample-efficient
      pretraining shared task?
    unsorted:
    - What tracks does the 2nd BabyLM Challenge have?
    - Is there a multimodal track in the second BabyLM Challenge?
  answered_by:
  - tracks
  - multimodal-corpus
- ask:
    practitioner: Can I use my own pretraining corpus in the 2024 BabyLM Challenge?
    unsorted:
    - Did the 2024 sample-efficient pretraining competition drop its fixed-dataset requirement?
    - Do I need a datasheet if I build my own BabyLM dataset?
  answered_by:
  - own-data
- ask:
    unsorted:
    - Does training a tokenizer count against the BabyLM word budget?
    - Is synthetic or augmented data allowed in the BabyLM Challenge?
    - How is a 100M word pretraining limit counted when ancillary models are used?
  answered_by:
  - budget-counting
- ask:
    unsorted:
    - What data is in the BabyLM multimodal corpus?
    - Which image-caption datasets are used by the 2024 vision-language track for child-scale
      pretraining?
    - How many images are in the BabyLM 2024 multimodal dataset?
  answered_by:
  - multimodal-corpus
- ask:
    unsorted:
    - What changed in the BabyLM 100M-word text corpus for 2024?
    - Why was QED removed from a child-scale pretraining dataset?
    - How much CHILDES data is in the BabyLM strict-track corpus?
  answered_by:
  - text-corpus
- ask:
    unsorted:
    - What baseline models does the 2nd BabyLM Challenge provide?
    - Which baselines are used for the BabyLM vision track?
    - Are the 2024 baselines for the child-scale pretraining competition stronger than the
      2023 ones?
  answered_by:
  - baselines
- ask:
    practitioner: Can I tune hyperparameters freely in the BabyLM Challenge?
    unsorted:
    - Is there a limit on epochs or hyperparameters when training a BabyLM?
    - Does training for many epochs help on 100M words?
  answered_by:
  - epochs
- ask:
    unsorted:
    - What must a model be able to do to be evaluated in the BabyLM Challenge?
    - Do submissions to the 2024 sample-efficient pretraining competition have to be HuggingFace
      models?
    - Does a BabyLM submission need to generate text?
  answered_by:
  - eval-requirements
- ask:
    practitioner: Can I dual-submit a BabyLM paper elsewhere?
    unsorted:
    - How are BabyLM Challenge papers reviewed?
    - What are the page limits and archival rules for a submission to the 2024 child-scale
      pretraining shared task?
  answered_by:
  - review
- ask:
    unsorted:
    - Did visual or non-linguistic grounding help models in the first BabyLM Challenge?
    - What did BabyLM 2023 find about multimodal grounding?
    - Is there evidence that image data improves low-resource language model pretraining?
  answered_by:
  - grounding-negative
  - multimodal-corpus
- ask:
    practitioner: Can I submit an analysis or benchmark paper instead of a model to BabyLM?
    unsorted:
    - What is the BabyLM paper track for?
    - Does a submission to the 2024 sample-efficient pretraining competition have to be a
      competition entry?
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
