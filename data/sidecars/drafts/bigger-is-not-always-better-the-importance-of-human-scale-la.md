<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced via a forced tool call) + 2 repair rounds. Every claim, number
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

Stamp: spec=d57862840a90 checks=2 body=c728d0d546db
-->
---
one_liner: Wilcox et al. argue that scaling language models to trillions of words undermines
  their use in psycholinguistics, and report that the first BabyLM Challenge -- 31 papers
  and 162 models trained on 100 million words or fewer -- came within a few percentage points
  of human BLiMP performance.
coined: BabyLM Challenge
gloss: shared task for pretraining a language model on 100 million words or fewer, the amount
  of language a child hears
claims:
- id: human-scale-generalizations
  kind: result
  text: Language models trained on 100 million words or fewer in the first BabyLM Challenge
    reached BLiMP scores within a few percentage points of human performance. The top Strict-track
    model ELC-BERT scored 0.85 on BLiMP, against 0.84 for Llama 2 trained on trillions of
    tokens.
  scope: English text only; BLiMP is a zero-shot minimal-pair grammaticality benchmark, and
    Llama 2 was evaluated on GLUE/SuperGLUE via in-context learning rather than fine-tuning.
  evidence: Table 1
- id: pos-relevant-no-gap
  kind: result
  text: BabyLM submissions performed virtually the same on BLiMP subtasks central to poverty-of-the-stimulus
    debates as on all other BLiMP subtasks. The POS-relevant subtasks target island constraints,
    filler-gap dependencies and subject-aux inversion.
  scope: Post hoc division of BLiMP subtasks into POS-relevant and non-POS-relevant, averaged
    across submissions within each track; English only; error bars are 95% CIs across model
    scores.
  evidence: Figure 4
- id: strict-small-close-to-strict
  kind: result
  text: Models trained on 10 million words in the BabyLM Strict-Small track came close to
    those trained on 100 million words in the Strict track. Only 2 Strict-track models achieved
    higher GLUE scores than the best-performing Strict-Small model.
  scope: Aggregate comparison across the 162 submitted models; the BabyLM corpus composition
    was held constant between tracks, with Strict-Small sampling 10% from each source.
  evidence: Table 1
- id: loose-track-worse
  kind: result
  text: Loose-track BabyLM models tended to score worse in the aggregate than Strict-Small
    models trained on 10 million words of text alone. The Loose track permitted extra non-linguistic
    data such as speech audio, code or visual input.
  scope: First BabyLM iteration only, with 2023-era architectures; the comparison is on BLiMP,
    GLUE/SuperGLUE and MSGS, which are text-based evaluations and may not reward multimodal
    grounding.
  evidence: Table 1 and Figure 3
- id: curriculum-learning-negative
  kind: result
  text: Curriculum learning was the most popular strategy among BabyLM submissions but produced
    only marginal gains over the baselines, while data preprocessing and architectural modifications
    were the most effective strategies.
  scope: Hand-coded meta-analysis of submissions into 9 approach categories; the CLIMB submission
    varied vocabulary size, difficulty metric and objective function and found no widespread
    improvement.
  evidence: Figure 5 and Figure 6
- id: epochs-not-architecture
  kind: result
  text: Retraining the BabyLM winner ELC-BERT and its backbone LTG-BERT for only 20 epochs
    on the 100-million-word Strict corpus dropped BLiMP and GLUE by about 2 points and the
    BLiMP supplement by about 10 points. At 20 epochs neither model was still a clear winner
    over the second-place McGill-BERT.
  scope: Reproduction with the authors' public code on 4 NVIDIA RTX8000 GPUs, with a smaller
    batch size than the original; the original submissions used over 450 epochs (Strict) and
    over 2000 epochs (Strict-Small).
  evidence: Table A.2
- id: skip-connections-not-needed
  kind: result
  text: 'LTG-BERT and ELC-BERT perform comparably on BabyLM''s language evaluations when both
    are trained for 20 epochs: tied on BLiMP, with LTG-BERT 1 percentage point higher on GLUE
    and on the BLiMP supplement. LTG-BERT is therefore the simpler recommendation for small-scale
    language modeling.'
  scope: Strict track (100M words), 20 epochs, 3 random seeds, controlled reproduction; ELC-BERT
    does score higher on MSGS.
  evidence: Table A.2
- id: diminishing-epoch-returns
  kind: result
  text: Most of the benefit of repeated passes over the BabyLM corpora arrives in the first
    20 epochs, with BLiMP gains diminishing exponentially over further training. Strict-Small
    GLUE performance actually declines after 50 epochs.
  scope: LTG-BERT trained on the BabyLM Strict and Strict-Small corpora, losses and scores
    averaged over 3 random seeds; Pearson correlations between training loss and BLiMP are
    -0.99 (Strict) and -0.95 (Strict-Small).
  evidence: Figure A.8 and Figure A.9
- id: msgs-linguistic-preference
  kind: result
  text: All top BabyLM models except Strict-Small McGill-BERT scored positively on MSGS, showing
    a preference for structural over surface-level generalizations comparable to Llama 2 (0.26)
    and RoBERTa-base (0.24). That argues their BLiMP and GLUE scores are not memorized surface
    patterns.
  scope: MSGS score is the Matthews correlation with the linguistic generalization on the
    test set; MSGS has not been run with human subjects, so no human reference point exists.
  evidence: Table 1 and Figure 3
- id: babylm-corpus-composition
  kind: result
  text: The BabyLM Corpus of 100 million words drew roughly 56% of its text from transcribed
    or scripted speech and about 40% from sources intended or appropriate for children. Mainstream
    pretraining corpora are instead dominated by web-scraped text and code.
  scope: English text and transcriptions only, no audio or video; the remaining 60% comes
    from adult-directed material including Wikipedia and Project Gutenberg, a compromise forced
    by limited availability of child-directed data.
  evidence: Section 'Training corpus'
- id: scaling-hurts-psycholinguistics
  kind: context
  text: Wilcox et al. argue that scaling undermines two main uses of language models in psycholinguistics.
    Models trained on trillions of words can no longer serve as evidence against poverty-of-the-stimulus
    claims, and larger models predict human reading times worse than smaller ones.
  scope: A position argument, not a new measurement; the reading-time reversal is attributed
    to prior work by Oh and Schuler (2023) and Shain et al. (2024) rather than measured in
    this article.
- id: babylm-population-resource
  kind: context
  text: The BabyLM Challenge established a population of openly described data-efficient language
    models, drawing 31 papers and 162 models. It also produced the BabyLM Corpus and a public
    evaluation pipeline for small-scale pretraining research.
  scope: First iteration, English only, held at CoNLL in December 2023; the challenge did
    not itself yield cognitive insight, and most winning modifications are not cognitively
    motivated.
- id: not-cognitively-plausible
  kind: context
  text: Robust linguistic generalization at human data scale was achieved in the BabyLM Challenge
    by mechanisms that are not cognitively plausible. These include hundreds to thousands
    of training epochs, transformers that retain all context words, and large-scale data augmentation.
  scope: The first BabyLM iteration's submissions; whether multiple-epoch training is cognitively
    plausible is left as an open question, with memory replay noted as a partial analogue.
qa:
- q:
  - can a language model learn English grammar from only the amount of language a child hears?
  - how well do models trained on 100 million words do on grammaticality benchmarks?
  - do small-data language models reach human-level syntactic performance?
  - what did the BabyLM Challenge show about human-scale training data?
  answers:
  - human-scale-generalizations
  - pos-relevant-no-gap
- q:
  - does more training data always help language models on linguistic benchmarks?
  - how much worse is a 10-million-word model than a 100-million-word model?
  - is there a big gap between the BabyLM Strict and Strict-Small tracks?
  answers:
  - strict-small-close-to-strict
- q:
  - does adding images or audio help language models learn from less text?
  - did multimodal submissions to the BabyLM Challenge outperform text-only ones?
  - why did the BabyLM Loose track underperform?
  answers:
  - loose-track-worse
- q:
  - does curriculum learning improve sample-efficient language model pretraining?
  - is training on simple sentences first useful for small-scale language models?
  - what happened to the 'starting small' hypothesis in the BabyLM Challenge?
  answers:
  - curriculum-learning-negative
- q:
  - which architecture should I use for small-scale language model pretraining?
  - is ELC-BERT better than LTG-BERT for training on 100 million words?
  - do the ELC-BERT skip connections matter?
  answers:
  - skip-connections-not-needed
  - epochs-not-architecture
- q:
  - how many epochs should a language model be trained for on a small corpus?
  - do hundreds of passes over a 100-million-word corpus pay off?
  - why did the BabyLM winner train for over 450 epochs, and was it necessary?
  answers:
  - epochs-not-architecture
  - diminishing-epoch-returns
- q:
  - are small language models just memorizing surface patterns to pass grammar benchmarks?
  - what does MSGS tell us about whether BabyLMs generalize linguistically?
  - how do data-efficient models compare to Llama 2 on preference for structural generalizations?
  answers:
  - msgs-linguistic-preference
- q:
  - what is in the BabyLM pretraining corpus?
  - how was a developmentally plausible 100-million-word training corpus assembled?
  - how much of the BabyLM data is child-directed or transcribed speech?
  answers:
  - babylm-corpus-composition
- q:
  - what should I read about why scaling language models is a problem for cognitive science?
  - which paper argues that bigger language models are worse models of human language processing?
  - where should I start reading about human-scale language modeling for psycholinguistics?
  - what work established the case for data-efficient language models in psycholinguistics?
  answers:
  - scaling-hurts-psycholinguistics
  - babylm-population-resource
- q:
  - can large language models still bear on poverty-of-the-stimulus arguments?
  - why does training data scale matter for learnability arguments about syntax?
  - do LLMs trained on trillions of words count as evidence about what children can learn?
  answers:
  - scaling-hurts-psycholinguistics
  - pos-relevant-no-gap
- q:
  - did the BabyLM Challenge find cognitively plausible learning mechanisms?
  - are BabyLM models good models of child language acquisition?
  - what are the limits of treating data-efficient language models as models of children?
  answers:
  - not-cognitively-plausible
  - babylm-population-resource
- q:
  - how many teams and models took part in the first BabyLM Challenge?
  - what resources came out of the 2023 shared task on pretraining with 100 million words?
  - which shared task produced a corpus and evaluation pipeline for human-scale pretraining?
  answers:
  - babylm-population-resource
  - babylm-corpus-composition
terminology:
  Strict track: BabyLM Challenge track allowing 100 million English words of training text
    for all components of the pipeline, with unlimited epochs over that data.
  Strict-Small track: BabyLM Challenge track allowing 10 million English words of training
    text, sampled at 10% from each source of the 100-million-word BabyLM Corpus.
  Loose track: BabyLM Challenge track allowing 100 million English words plus additional non-linguistic
    data such as speech audio, code, music or visual input.
  BabyLM Corpus: A 100-million-word English pretraining corpus in which roughly 56% is transcribed
    or scripted speech and about 40% comes from child-directed or child-appropriate sources.
  POS-relevant BLiMP subtasks: 'The BLiMP grammaticality subtasks targeting phenomena raised
    in poverty-of-the-stimulus debates: island constraints, filler-gap dependencies and subject-aux
    inversion.'
  skyline: A large model trained on its full, unrestricted pretraining corpus, used as an
    upper reference point against which data-limited models are compared -- Llama 2 (70B)
    and RoBERTa-base in the BabyLM evaluation.
  MSGS: The Mixed Signals Generalization Set, which fine-tunes a model on labels consistent
    with both a linguistic and a surface generalization and then tests which one it adopted,
    scored as a Matthews correlation where 1 is systematic linguistic generalization and -1
    systematic surface generalization.
misreadings:
- 'Near-human BLiMP and GLUE scores from 100-million-word models do not mean these models
  match large LLMs in general: BabyLM models generate repetitive and sometimes nonsensical
  text, and are poor at instruction following and in-context learning.'
- 'The BabyLM Challenge''s success at human data scale is not a demonstration that the models
  learn like children: the winning submissions used hundreds to thousands of epochs over the
  corpus and large-scale data augmentation, neither of which is cognitively plausible.'
- 'ELC-BERT winning both the Strict and Strict-Small tracks does not mean its added layer-wise
  skip connections are what won: under a matched 20-epoch budget it performs comparably to
  plain LTG-BERT, and the large epoch count is what set the submission apart.'
- The negative curriculum-learning results concern sorting a small pretraining corpus by difficulty;
  they are not evidence that child-directed speech is useless for children, only grounds for
  skepticism that it is necessary for effective language learning.
- All BabyLM Challenge results are for English, so the findings about what is learnable at
  human data scale are not established for typologically diverse languages.
- 'Wilcox et al. do not argue that scaling is bad for language technology: scaling is described
  as largely beneficial for applications, and the objection is to relying on it exclusively
  when the goal is a cognitive model.'
---
