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
- q:
  - What is a good starting point for research on training language models with as little
    data as a child hears?
  - Where should I start reading about sample-efficient or human-scale language model pretraining?
  - What shared task exists for small-scale language modeling and cognitive modeling?
  answers:
  - challenge-purpose
  - democratization
- q:
  - How much training data does the BabyLM Challenge allow?
  - How many words are in the 10M and 100M word pretraining corpora for the BabyLM shared
    task?
  - What is the size of the developmentally plausible pretraining dataset released for small-scale
    language modeling?
  answers:
  - corpus-sizes
  - child-word-budget
- q:
  - What text sources make up the BabyLM pretraining corpus?
  - Which corpora and domains are in the child-inspired 100M-word pretraining dataset?
  - How much of the developmentally plausible pretraining data is transcribed speech versus
    Wikipedia?
  answers:
  - corpus-composition
- q:
  - What are the tracks of the BabyLM Challenge and how do they differ?
  - Can I use my own data or multimodal data in the sample-efficient pretraining shared task?
  - What is the difference between the Strict, Strict-small and Loose tracks?
  answers:
  - three-tracks
- q:
  - Why did anyone set up a challenge about pretraining on child-sized amounts of text?
  - How much more data do large language models see than a child does?
  - What motivates studying language model pretraining at human data scales?
  answers:
  - data-gap-motivation
  - challenge-purpose
- q:
  - What baseline models does the BabyLM Challenge provide?
  - Are the OPT, RoBERTa and T5 baselines for the 10M-word pretraining task tuned?
  - What should a submission to the sample-efficient pretraining challenge be compared against?
  answers:
  - naive-baselines
- q:
  - What must a model be able to do to be evaluated in the BabyLM Challenge?
  - Do submissions to the child-scale pretraining shared task have to be generative language
    models?
  - What interface does the shared evaluation pipeline for small-scale language models require?
  answers:
  - eval-requirements
- q:
  - Does the BabyLM Challenge limit training compute or epochs?
  - Can I train for many epochs on the 10M-word BabyLM corpus?
  - Are there hyperparameter restrictions in the sample-efficient pretraining shared task?
  answers:
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
