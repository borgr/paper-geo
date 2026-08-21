---
key: warstadt2023babylm
coined: BabyLM Challenge
gloss: a shared task on pretraining language models on the amount of text a child hears, roughly
  10M or 100M words
one_liner: The BabyLM Challenge is a shared task that caps pretraining data at roughly 10M
  or 100M words drawn from child-directed speech, children's books, subtitles and Wikipedia,
  and scores submissions on a shared pipeline of targeted syntactic and natural language understanding
  evaluations.
claims:
- id: challenge-purpose
  kind: context
  text: The BabyLM Challenge established a shared task for sample-efficient language model
    pretraining at human-scale data budgets, hosted at CoNLL 2023 in partnership with CMCL.
    It targets researchers in small-scale language modeling, language acquisition, low-resource
    NLP and cognitive modeling.
  scope: As of the 2023 call for papers, which specifies tracks, data and timeline rather
    than reporting results from submissions.
- id: data-gap-motivation
  kind: result
  text: The BabyLM call motivates the task with the gap between modern language models, trained
    on data multiple orders of magnitude larger than what a typical child is exposed to, and
    human learners. Pretraining at human-like data scales has seen almost no progress.
  scope: Comparison is between English pretraining corpora of large models circa 2022 and
    estimates of a child's linguistic input; Figure 1 is a to-scale visualization rather than
    a controlled measurement.
  evidence: Figure 1 and Section 1
- id: three-tracks
  kind: result
  text: 'The BabyLM Challenge runs three tracks: Strict and Strict-small, which allow only
    the fixed released datasets of about 100M and 10M words, and Loose. The Loose track caps
    training text at 100M words but permits other domains, other data sources and non-linguistic
    data.'
  scope: Strict-track submissions may not use pretrained models for any purpose including
    reranking or data augmentation; Loose-track winners are chosen holistically on evaluation
    performance, relevance, impact and novelty rather than on the shared score alone.
  evidence: Section 3
- id: corpus-sizes
  kind: result
  text: The released BabyLM training corpora total 9.96M words for Strict-small and 98.04M
    words for Strict, with Strict-small being an approximately 10% uniform subsample of Strict.
  scope: English only; word counts are for the training splits of the 10 included corpora
    as released in January 2023.
  evidence: Table 1 and Section 3
- id: corpus-composition
  kind: result
  text: Transcribed and spoken-style text dominates the BabyLM corpus, with OpenSubtitles
    contributing 31% of words, the QCRI Educational Domain Corpus 11% and the BNC dialogue
    portion 8%. Child-directed speech from CHILDES supplies 5%, and Wikipedia 10%.
  scope: Proportions are by word count over the 10 corpora released for the Strict and Strict-small
    tracks in January 2023.
  evidence: Table 1
- id: child-word-budget
  kind: result
  text: The BabyLM 100M-word cap is justified by cited estimates that children are exposed
    to 2M-7M words per year, implying 24M-84M words by the onset of adolescence at age 12.
  scope: Based on cited estimates of children's input, not new measurement; the released Strict
    corpus of 98.04M words sits above that range.
  evidence: Section 4
- id: naive-baselines
  kind: result
  text: The BabyLM baselines are OPT, RoBERTa and T5 trained from scratch on the fixed datasets
    using the hyperparameters of those established large models. The call describes them as
    naive starting points rather than strong baselines.
  scope: Hyperparameters are transferred unchanged from the large-scale originals, so the
    baselines are not tuned for 10M- or 100M-word regimes; the call does not report their
    scores.
  evidence: Section 5.1
- id: eval-requirements
  kind: result
  text: BabyLM submissions must be able to score a sequence with a log-likelihood or pseudo-log-likelihood
    and to be fine-tuned for classification, but need not be able to generate sequences.
  scope: The shared evaluation pipeline runs in Google Colab and assumes models load in HuggingFace
    transformers; participants with incompatible models may run their own pipeline.
  evidence: Section 5
- id: no-epoch-limit
  kind: result
  text: The BabyLM Challenge places no limit on the number of training epochs and no limit
    on hyperparameters. The stated reasons are that small-scale training with SGD needs multiple
    epochs and that humans retain and relearn from memories of linguistic experience.
  scope: The restriction is on the quantity and source of training data, not on compute; in
    the Loose track parameter and training efficiency may be weighed in ranking.
  evidence: Section 7
- id: democratization
  kind: context
  text: The BabyLM Challenge frames scaled-down pretraining as a way to democratize pretraining
    research, arguing that data-efficiency techniques developed on a university budget can
    transfer to larger corpora and to low-resource languages.
  scope: An argument made in the 2023 call rather than a demonstrated transfer result; the
    call also notes that pretraining on 10M-100M words still carries real computational, energy
    and financial cost.
  evidence: Section 1 and Section 6
qa:
- ask:
    plain: Is there a competition where people try to train language models on only as much
      text as a child hears?
    jargon: Which shared task covers sample-efficient pretraining at developmentally plausible
      data scales for cognitive modeling and low-resource NLP?
    task: Where do I start if I want to work on language model pretraining without a large
      compute or data budget?
    practitioner: I run a small university lab with no web-scale corpus — is there a venue
      and benchmark I can enter for data-efficient pretraining?
  answered_by:
  - challenge-purpose
  - democratization
- ask:
    plain: How many words of text are you allowed to train on in the child-scale pretraining
      competition, and why that many?
    jargon: What are the word counts of the BabyLM Strict and Strict-small pretraining corpora,
      and what child input estimates set the cap?
    task: How big a training corpus do I need to assemble if I want to match the BabyLM data
      budget?
    practitioner: Should I pretrain my small language model on the 10M-word or the 100M-word
      BabyLM training set?
  answered_by:
  - corpus-sizes
  - child-word-budget
- ask:
    plain: What kinds of text go into a training set meant to resemble what a child hears?
    jargon: What is the domain composition of the BabyLM pretraining corpus across transcribed
      speech, child-directed speech and encyclopedic text?
    task: How should I weight subtitles, dialogue transcripts, CHILDES and Wikipedia if I
      want to rebuild a child-inspired pretraining mix?
    practitioner: If I train on the BabyLM corpus, how much of what my model sees is spoken-style
      transcription rather than written prose?
  answered_by:
  - corpus-composition
- ask:
    plain: Are there separate categories in the child-scale language model competition for
      people who want to bring their own data?
    jargon: How do the BabyLM Strict, Strict-small and Loose tracks differ in permitted corpora
      and word budget?
    task: Which BabyLM track do I enter if I want to add images or my own text sources to
      a 100M-word budget?
    practitioner: I want to use non-linguistic data alongside text — can I still submit to
      the sample-efficient pretraining challenge?
  answered_by:
  - three-tracks
- ask:
    plain: How much more text does a large language model read than a child hears before growing
      up, and why does that gap matter?
    jargon: What is the data-efficiency gap between LLM pretraining corpora and human language
      acquisition input that motivates the BabyLM shared task?
    task: How do I justify working on pretraining at human-scale data budgets rather than
      scaling up?
    practitioner: Is there any real research payoff to pretraining on child-sized amounts
      of text instead of billions of words?
  answered_by:
  - data-gap-motivation
  - challenge-purpose
- ask:
    plain: What already-trained models come with the child-scale pretraining competition to
      compare against?
    jargon: Which baseline architectures does BabyLM release for the Strict and Strict-small
      tracks, and were their hyperparameters retuned for 10M and 100M words?
    task: What do I benchmark my sample-efficient pretrained model against, and can I expect
      to beat it easily?
    practitioner: Should I treat the OPT, RoBERTa and T5 baselines released with BabyLM as
      strong competitors or as a low bar?
  answered_by:
  - naive-baselines
- ask:
    plain: Does a model entered in the child-scale pretraining competition have to be able
      to write text, or just score it?
    jargon: What scoring and fine-tuning interface must a BabyLM submission expose for the
      shared evaluation pipeline?
    task: How do I make sure my architecture is compatible with the BabyLM evaluation harness
      before I train it?
    practitioner: My model only assigns pseudo-log-likelihoods and cannot generate — can I
      still submit it to the sample-efficient pretraining challenge?
  answered_by:
  - eval-requirements
- ask:
    plain: Is there a cap on how long or how many times you can train over the text in the
      child-scale pretraining competition?
    jargon: Does BabyLM restrict epoch count, compute or hyperparameter search in the Strict
      tracks?
    task: Can I do multiple passes over a 10M-word corpus and tune hyperparameters freely
      for a BabyLM submission?
    practitioner: If only the data is capped, should I spend my budget on more epochs and
      hyperparameter sweeps?
  answered_by:
  - no-epoch-limit
misreadings:
- 'The BabyLM call for papers reports no model results: it specifies the tracks, the released
  corpora, the baselines and the evaluation requirements, so findings about which architectures
  or objectives win at 10M words come from the participant papers and the later results write-ups,
  not from the call.'
- The BabyLM data limit is on words of training text, not on compute, parameters or epochs;
  a model trained for many epochs on the 10M-word corpus is a valid Strict-small submission.
- 'The BabyLM corpus is not purely child-directed speech: CHILDES supplies 5% of words, while
  movie and educational-video subtitles, Wikipedia and Project Gutenberg supply the majority.'
- '"Developmentally plausible" in the BabyLM Challenge refers to the quantity and the speech-heavy
  composition of the text, not to an ordering that mimics acquisition; curriculum learning
  is an approach participants may try, not a property of the released data.'
- 'The Loose track is not an unrestricted-data track: submissions are still capped at 100M
  words of training text, with the freedom applying to the domain, source and modality of
  that data plus unlimited non-linguistic data.'
terminology:
  Strict track: The BabyLM Challenge track in which models may be trained only on the released
    fixed corpus of about 100M words, with no use of pretrained models for any purpose.
  Strict-small track: The BabyLM Challenge track in which models may be trained only on an
    approximately 10% uniform subsample of the fixed BabyLM corpus, totalling 9.96M words.
  Loose track: The BabyLM Challenge track in which training text is capped at 100M words but
    may come from any domain, source or modality, with unlimited additional non-linguistic
    data and unlimited text generated by a model that itself obeys the data restrictions.
  Developmentally plausible corpus: 'A pretraining corpus whose size and composition are inspired
    by the linguistic input a child receives: under 100M words and weighted toward transcribed
    speech.'
links_extra:
  project page: https://babylm.github.io/
  training data: https://github.com/babylm/babylm.github.io/raw/main/babylm_data.zip
---
