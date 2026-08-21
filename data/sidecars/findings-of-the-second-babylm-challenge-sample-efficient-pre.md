---
key: hu2024babylm2
one_liner: The second BabyLM Challenge asked 31 teams to pretrain language models on 100M
  words or less (10M in Strict-Small, plus a new 100M-word image-text Multimodal track), and
  found that a hybrid causal-masked model, GPT-BERT, won both text tracks while no multimodal
  submission beat the organizers' baselines.
claims:
- id: gptbert-wins-both-text-tracks
  kind: result
  text: GPT-BERT, which combines masked and causal language modeling objectives, won both
    text tracks of the second BabyLM Challenge. It reached a 75.7 text average in the 100M-word
    Strict track against 64.8 for the best baseline, LTG-BERT, and 70.4 in the 10M-word Strict-Small
    track against 61.6 for BabyLlama.
  scope: Text average over BLiMP, BLiMP Supplement, (Super)GLUE and EWoK, on evaluation sets
    filtered to the BabyLM vocabulary; English only; word budgets of 100M and 10M with participant-chosen
    training data.
  evidence: Table 3
- id: multimodal-no-winner
  kind: result
  text: No submission to the BabyLM Multimodal track outperformed the organizers' baselines,
    so no winner was awarded. The best Flamingo baseline scored a 54.5 vision average and
    65.2 text average, above every one of the 8 submitted multimodal models.
  scope: 3 teams and 8 models only, all trained within a 100M-word text budget with unlimited
    images; vision average covers VQA, Winoground and DevBench.
  evidence: Table 3
- id: flops-effect
  kind: result
  text: Average text-evaluation score in the second BabyLM Challenge rose with training compute,
    with log training FLOPs a significant positive predictor (beta = 2.7). The mixed-effects
    regression also included backbone architecture and track as covariates.
  scope: 64 submitted models across the Strict, Strict-Small and Multimodal tracks, with random
    slopes per submitting group and no fixed-effect interactions; correlational over submissions,
    not a controlled compute sweep.
  evidence: Figure 3 and Section 6.1
- id: ewok-near-chance
  kind: result
  text: Models trained on 100M words or less do not acquire the world knowledge that EWoK
    tests. Most submissions to the second BabyLM Challenge scored near the 50% chance level,
    and the maximum score was 58.4%.
  scope: EWoK used as the hidden text-track evaluation, filtered to the BabyLM vocabulary;
    masked-LM scores required re-scoring with uniform tie-breaking, which lowered initially
    reported values of 60-70%.
  evidence: Section 5.1 and Table 3
- id: curriculum-learning-not-effective
  kind: result
  text: Curriculum learning was the most popular approach in the second BabyLM Challenge yet
    did not pay off. It showed a negative coefficient on average text score (beta = -3.6,
    p = 0.055) in a mixed-effects regression over submitted models.
  scope: Self-reported approach labels over 64 models, dummy-coded with random intercepts
    per submitting group; effect not significant at alpha = 0.05, and most curriculum submissions
    varied data order rather than training objective.
  evidence: Figure 5 and Section 6.3
- id: effective-approach-categories
  kind: result
  text: In the second BabyLM Challenge, training-objective innovations, dataset creation,
    hyperparameter tuning and architectural innovations gave the highest average text scores,
    with training-objective innovations significant at alpha = 0.05 (beta = 4.5).
  scope: Self-reported approach labels over 64 submitted models, mixed-effects regression
    with random intercepts per submitting group; architectural innovation also carried high
    variance across models.
  evidence: Figure 5 and Section 6.3
- id: backbone-no-significant-effect
  kind: result
  text: No backbone architecture had a statistically significant effect on average text score
    across the second BabyLM Challenge's submissions at alpha = 0.05. Coefficients were nonetheless
    large for DeBERTa (beta = 9.1, p = 0.06), GPT-2 and LTG-BERT (both beta = 8.5, p = 0.06
    and 0.07) and Llama (beta = 7.7, p = 0.07).
  scope: 64 models, so the analysis may lack power to detect architecture effects; the highest-scoring
    individual models were all LTG-BERT based, and LTG-BERT also had the highest variance
    of any backbone.
  evidence: Figure 4 and Section 6.2
- id: rnns-competitive
  kind: result
  text: Recurrent networks entered the BabyLM Challenge for the first time in 2024 and were
    competitive with Transformers. HGRN, an RNN with complex forget gates, was among the backbones
    with the highest average text scores, alongside DeBERTa.
  scope: Aggregated by backbone over 64 submitted models with no controlled matching of compute
    or data; architecture effects were not statistically significant.
  evidence: Figure 4 and Section 6.4
- id: corpus-more-child-oriented
  kind: result
  text: The 2024 BabyLM pretraining corpus raised child-oriented data to 70% of the mix, up
    from 39% the previous year. Child-oriented discourse rose from 5% to 29% by using the
    full English CHILDES including child utterances.
  scope: English text-only corpus of 100M words (10M subsampled for Strict-Small); Wikipedia
    except Simple English Wikipedia and the QED portion were dropped and reliance on OpenSubtitles
    reduced.
  evidence: Table 1 and Section 3
- id: blimp-approaching-human
  kind: result
  text: The best Strict-track model in the second BabyLM Challenge came within 2.5 percentage
    points of the reported human score on BLiMP, and one Strict-Small model beat the Llama
    skyline on BLiMP.
  scope: BLiMP filtered to the BabyLM vocabulary, so not comparable to published full-BLiMP
    results; human reference is the individual-agreement score from the original BLiMP paper.
  evidence: Section 5.1
- id: own-data-allowed
  kind: context
  text: The second BabyLM Challenge changed the rules to let participants build their own
    pretraining corpora within the 10M- or 100M-word budget. The provided BabyLM corpus became
    a dataset baseline rather than a fixed requirement.
  scope: The 2024 iteration's Strict, Strict-Small and Multimodal tracks; the 2023 iteration
    required the fixed corpus in its strict tracks.
- id: shared-task-for-sample-efficiency
  kind: context
  text: The BabyLM Challenge is a recurring shared task on sample-efficient pretraining under
    a fixed data budget. It gives the developmentally-plausible language modeling community
    a shared corpus and a common evaluation pipeline over BLiMP, (Super)GLUE, EWoK and multimodal
    tasks.
  scope: 'As of the second iteration in 2024: English only, text and image-text modalities,
    with 31 papers and 64 models submitted from 16 countries.'
- id: multimodal-resources-released
  kind: context
  text: The second BabyLM Challenge released a 100M-word image-text pretraining corpus pairing
    50M words of BabyLM text with 50M words of captions from Localized Narratives and Conceptual
    Captions 3M over 2.9M images. It also released a multimodal evaluation pipeline covering
    VQA, Winoground and DevBench.
  scope: Suggested resource rather than a requirement, since participants could construct
    their own multimodal data with unlimited images; images must be downloaded via provided
    scripts and CC3M coverage is limited to URLs valid in January 2024.
qa:
- ask:
    plain: is there a competition for training language models on a small amount of text?
    jargon: which shared task benchmarks sample-efficient pretraining under a fixed word budget
      with a developmentally plausible corpus?
    task: where do I find a standard corpus and evaluation suite for pretraining a small language
      model on limited data?
    practitioner: if I want to compare my low-resource pretraining recipe against others,
      which shared task should I enter?
  answered_by:
  - shared-task-for-sample-efficiency
  - own-data-allowed
- ask:
    plain: which entry did best at learning language from a small amount of text in the 2024
      contest, and what did it do differently?
    jargon: which submission topped the BabyLM 2024 Strict and Strict-Small text tracks, and
      which category of approach scored highest overall?
    task: what kind of change should I make to get the best text scores when pretraining on
      10M or 100M words?
    practitioner: should I copy the winning 2024 BabyLM recipe, or is the general lesson about
      training objectives enough?
  answered_by:
  - gptbert-wins-both-text-tracks
  - effective-approach-categories
- ask:
    plain: does showing a small language model pictures alongside text make it better at language?
    jargon: did any BabyLM 2024 multimodal submission beat the Flamingo and GIT vision-language
      baselines on the vision and text evaluations?
    task: if I pair captions with text to pretrain a vision-language model on 100M words,
      what results can I expect against the released baselines?
    practitioner: is there an image-text corpus and evaluation pipeline I can use for data-limited
      multimodal pretraining, and did anyone beat the baselines with it?
  answered_by:
  - multimodal-no-winner
  - multimodal-resources-released
- ask:
    plain: if the amount of training text is fixed, does throwing more computing power at
      it still raise scores?
    jargon: is log training FLOPs a significant predictor of average text-evaluation score
      once backbone and track are controlled for?
    task: how much should I budget for training steps and model size when my pretraining data
      is capped at 100M words?
    practitioner: would training my small-data model for longer with a bigger compute budget
      actually buy me better benchmark scores?
  answered_by:
  - flops-effect
- ask:
    plain: does ordering training text from simple to complex help a language model learn
      from less data?
    jargon: did curriculum learning submissions to BabyLM 2024 show a positive coefficient
      on average text score relative to other approach categories?
    task: should I sort my pretraining data by difficulty or spend the effort on the training
      objective instead?
    practitioner: I have limited pretraining data and time for one idea, is a curriculum worth
      trying?
  answered_by:
  - curriculum-learning-not-effective
  - effective-approach-categories
- ask:
    plain: can a language model pick up everyday knowledge about how the world works from
      only 100 million words?
    jargon: how did BabyLM 2024 submissions score on EWoK relative to the 50% chance baseline?
    task: should I expect a model pretrained on 10M-100M words to handle world-knowledge probes,
      or will it sit at chance?
    practitioner: if I need world knowledge from a small-data model, is a 100M-word budget
      going to be enough?
  answered_by:
  - ewok-near-chance
- ask:
    plain: does it matter which kind of neural network you pick when training on a small amount
      of text?
    jargon: does backbone architecture have a statistically significant effect on average
      text score across BabyLM 2024 submissions, and how did HGRN compare with Transformers?
    task: which architecture should I pick for pretraining under a 10M or 100M word budget?
    practitioner: is it worth switching from a Transformer to a recurrent model for my data-limited
      pretraining run?
  answered_by:
  - backbone-no-significant-effect
  - rnns-competitive
- ask:
    plain: what kind of text is in the 2024 small-data pretraining corpus for language models,
      and how did it change from the year before?
    jargon: what is the composition of the 2024 BabyLM pretraining corpus, and how much of
      the mix is child-oriented discourse compared with 2023?
    task: if I assemble my own 10M or 100M word pretraining set, how much child-directed speech
      should it contain?
    practitioner: should I train on the provided BabyLM corpus or build my own within the
      same word budget?
  answered_by:
  - corpus-more-child-oriented
  - own-data-allowed
- ask:
    plain: how close can a language model trained on 100 million words get to human judgments
      of grammar?
    jargon: what BLiMP scores do the top Strict and Strict-Small BabyLM 2024 models reach
      relative to the reported human score and the Llama skyline?
    task: what grammatical acceptability performance can I expect if I pretrain on only 10M
      or 100M words?
    practitioner: is a small-data pretrained model good enough on grammar benchmarks for me
      to use instead of a large one?
  answered_by:
  - blimp-approaching-human
  - gptbert-wins-both-text-tracks
- ask:
    plain: which tests are used to check whether a small image-and-text model understood both
      pictures and words?
    jargon: what does the BabyLM multimodal evaluation pipeline cover beyond the text tasks?
    task: how do I evaluate a vision-language model pretrained on a limited image-text corpus?
  answered_by:
  - multimodal-resources-released
misreadings:
- 'The 2.5-percentage-point gap to human BLiMP performance is not measured on the full BLiMP
  benchmark: BabyLM filters evaluation examples containing words that appear fewer than twice
  in the pretraining corpora, so scores are not comparable to published full-dataset results
  or to the 2023 challenge.'
- The strong FLOPs-score relationship is correlational across heterogeneous submissions, not
  evidence that scaling compute alone closes the human-model data-efficiency gap.
- The negative result in the Multimodal track reflects only 8 models from 3 teams, so it bounds
  what the 2024 submissions achieved rather than showing that visual grounding cannot help
  sample-efficient language learning.
- 'Finding no significant effect of backbone architecture does not mean architecture is irrelevant:
  with 64 models the analysis had limited power, and several backbones showed large coefficients
  with p values near 0.06.'
- Near-chance EWoK scores are not purely an evaluation artifact; initial masked-LM scores
  of 60-70% came from a tie-breaking default in the LM evaluation harness, and after uniform
  tie-breaking the scores were confirmed with an independent scoring script.
- Winning both text tracks does not mean GPT-BERT was trained on the organizers' provided
  corpus alone; participants in 2024 were allowed to construct their own data within the word
  budget, and the winning submission adjusted its training corpus.
terminology:
  Strict track: The BabyLM competition track limiting pretraining to 100 million words or
    fewer of text, with participants free to choose the data sources.
  Strict-Small track: The BabyLM competition track limiting pretraining to 10 million words
    or fewer of text.
  Multimodal track: The BabyLM competition track for image-text models, capped at 100 million
    words of text but allowing unlimited visual input, evaluated on both text-only and multimodal
    tasks.
  Skyline: A non-competition reference model trained without the BabyLM data budget (such
    as Llama or RoBERTa), plotted alongside submissions as an upper reference point rather
    than as a competitor.
  Variation sets: Consecutive rephrasings of the same sentence, common in child-directed speech,
    which one BabyLM submission synthesized with GPT-4 as training data.
  BLiMP Supplement: A set of minimal-pair test suites built for the BabyLM Challenge covering
    linguistic knowledge absent from BLiMP, including hypernymy, question-answer congruence,
    subject-auxiliary inversion and turn-taking.
links_extra:
  data: https://osf.io/ad7qg/
  evaluation pipeline: https://github.com/babylm/evaluation-pipeline-2024
  preprocessing code: https://github.com/babylm/babylm_data_preprocessing
---
