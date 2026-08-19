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

Then promote it:  python scripts/draft_sidecars.py --accept pretraining-language-models-for-diachronic-linguistic-change

Stamp: spec=8f05813a4658 checks=pass body=e523ab7f1818
-->
---
one_liner: Pretraining a battery of small BabyLlama-2 models on 10-million-word time slices
  of Project Gutenberg gives historically airtight language models that finetuned Llama3-8B
  adapters cannot match, because finetuned models leak future word senses across period boundaries.
key: fittschen2026diachronic
coined: Perspectival Language Models
gloss: small language models pretrained separately on each slice of a corpus, so each one
  only knows its own period or genre
claims:
- id: pretrain-period-specific-ppl
  kind: result
  text: BabyLlama-2 models pretrained on individual 1750-1940 time slices each reach their
    lowest perplexity on the test set from their own slice, with perplexity rising roughly
    linearly on both older and newer text. Llama3-8B DoRA models finetuned on the same slices
    show this preference only for the earlier slices.
  scope: 5 slices (1750-1820, 1820-1850, 1850-1880, 1880-1910, 1910-1940) of 10M training
    tokens each drawn from Project Gutenberg English prose, with 5M reserved test and 1M validation
    tokens.
  evidence: Figure 1
- id: leakage
  kind: result
  text: Llama3-8B DoRA models finetuned on early time slices recall word senses coined after
    their slice at consistently higher rates than the period-pretrained BabyLlama-2 models.
    The gap persists after correcting for each model's overall recall, and the cloze task
    is built from Oxford English Dictionary sense-first-attestation dates.
  scope: 14.6 thousand cloze examples remaining after filtering out words with fewer than
    2 occurrences in any training set, scored as success if the target appears in the top
    100 single-word completions.
  evidence: Figure 3 and Figure 7
- id: cholera-example
  kind: result
  text: For the 1837 hog-disease sense of "cholera", only the 1750-1820 pretrained model ranks
    the word inside the top-k completions, at rank 41. The DoRA-finetuned models rank it 11
    to 19 in every slice, and off-the-shelf Llama3-8B ranks it 8.
  scope: A single manually inspected cloze context; illustrative of the leakage pattern rather
    than an aggregate measurement.
  evidence: Table 7
- id: blimp-aggregate
  kind: result
  text: On maximally filtered BLiMP the period-pretrained BabyLlama-2 models score 0.67 to
    0.72 aggregate accuracy across the 5 slices. The DoRA-finetuned models reach 0.80 to 0.84,
    off-the-shelf BabyLlama-2 scores 0.74 and Llama3-8B scores 0.82.
  scope: '"Maximally filtered" BLiMP: only minimal pairs whose every word occurs at least
    twice in all 5 training sets, evaluated through the BabyLM 2024 evaluation pipeline.'
  evidence: Table 3
- id: npi-change
  kind: result
  text: On the BLiMP "only NPI licenser present" task the period-pretrained models rise monotonically
    from 0.00 accuracy in the 1750-1820 and 1820-1850 slices to 0.33, 0.82 and 0.91 in the
    later slices. The DoRA-finetuned models score 0.92 to 1.00 in every slice and register
    no diachronic change.
  scope: Maximally filtered BLiMP subset testing preference for "only...ever" over "even...ever";
    baseline BabyLlama-2 scores 0.76 and Llama3-8B 0.90. The corpus is Gutenberg English prose,
    so the trend may be corpus-specific rather than a fact about English.
  evidence: Table 4
- id: training-cost
  kind: result
  text: Training one period model with the BabyLlama-2 recipe takes about 32 minutes per teacher
    plus 3 hours 20 minutes for the distilled 345M-parameter student on a single A100. DoRA
    finetuning of Llama3-8B for 3 epochs on the same 10M-token slice takes around 8 hours.
  scope: Single A100 GPU; DoRA rank 16 on Q, K, V, Up and Down projections; BabyLlama-2 uses
    2 same-size teachers and 8 epochs with distillation alpha 0.5.
  evidence: Appendix A, Tables 8-10
- id: date-attribution
  kind: result
  text: Zero-shot work-date attribution by 4-bit quantized Llama3.3-70B matches hand-annotated
    dates at 0.63 within 1 year and 0.81 within 10 years. GPT-4o reaches 0.82 and 0.84 on
    the same set, which the authors judge close enough to justify the open-weight model for
    segmenting the corpus.
  scope: 1054 manually annotated known-author works published 1550-1850, dated by prompting
    for a single year; the +/-1 tolerance accommodates copyright-year publication dates.
  evidence: Table 11
- id: sense-trajectories
  kind: result
  text: Filtering words by a monotonic fall in normalized per-word perplexity across the 5
    period models separates two synchronically distinct senses of "station". The railway sense
    becomes sharply more acceptable in the 1820-1850 slice, while the camp/stopover sense
    rises smoothly from an already acceptable start.
  scope: Natural occurrences of "station" in the corpus, filtered for descending probability
    trajectory and then hand-labelled for sense; a demonstration of the discovery procedure,
    not a quantified detection rate.
  evidence: Figure 4
- id: prefiguration
  kind: result
  text: The 1750-1820 pretrained model ranks "line" 14th as the completion of "the end of
    the line", a sense first attested in 1948. A collocation search shows the construction
    never appears in that model's training data, and hereditary and military uses of "line"
    appear to prefigure it.
  scope: One hand-inspected cloze item; the finetuned model ranks the same completion 1st,
    which leakage from Llama3-8B pretraining can equally explain.
  evidence: Table 6
- id: context-pretraining-as-method
  kind: context
  text: '"Pretraining Language Models for Diachronic Linguistic Change Discovery" argues that
    domain-restricted pretraining, not finetuning or model editing, is the only way to guarantee
    a language model''s weights contain no out-of-domain information. The paper shows that
    argument is affordable at 10M tokens per model using BabyLM-community recipes.'
  scope: Argued and demonstrated for temporal division of an English literary corpus at academic
    compute scale; the paper does not test synchronic divisions such as genre, and lists that
    as future work.
  evidence: Section 1
- id: context-nonlexical-change
  kind: context
  text: Time-sliced perspectival pretraining extends computational study of language change
    beyond lexical semantic change to grammatical and morphological phenomena. Its authors
    report knowing of no prior work using language models to automate discovery of such non-lexical
    change.
  scope: As of publication in 2026; prior lexical semantic change work is surveyed as relying
    on non-causal embedding models and embedding alignment. The grammatical evidence is a
    single BLiMP phenomenon on one corpus.
  evidence: Section 2
- id: context-pipeline
  kind: context
  text: The historical-perspectival-lm codebase releases the full date-attribution, slicing,
    pretraining, finetuning and evaluation pipeline for time-sliced language models. It also
    releases a word-sense cloze evaluation set of 50.4 thousand OED-derived examples.
  scope: Reuse on new corpora requires supplying train/dev/test text per category; the released
    historical data covers English Project Gutenberg works dated 1750-1940. Cloze set filtering
    to 14.6 thousand examples is specific to the paper's vocabulary overlap.
  evidence: Appendix C
qa:
- q:
  - Does finetuning a large model on historical text keep it from knowing later language?
  - Can LoRA or DoRA finetuning restrict a model to one time period?
  - Do period-finetuned Llama models leak future word senses?
  answers:
  - leakage
  - cholera-example
  - context-pretraining-as-method
- q:
  - How well do small models pretrained on one time slice stay inside their period?
  - Do time-sliced pretrained language models show period-specific perplexity?
  - Which respects historical corpus boundaries better, pretraining or finetuning?
  answers:
  - pretrain-period-specific-ppl
  - leakage
- q:
  - How much worse are 10M-token period models than a finetuned Llama3-8B on grammar benchmarks?
  - What BLiMP accuracy do BabyLlama-2 models trained on 10 million tokens reach?
  - Are tiny domain-pretrained models still usable models of language?
  answers:
  - blimp-aggregate
- q:
  - Can a language model detect grammatical change over time, not just lexical change?
  - How was diachronic change in negative polarity item licensing measured with language models?
  - Do period models show a shift in preference for "only...ever" over "even...ever"?
  answers:
  - npi-change
  - context-nonlexical-change
- q:
  - Is pretraining a small model cheaper than parameter-efficient finetuning of an 8B model?
  - How long does it take to train one BabyLlama-2 period model on an A100?
  - What is the compute cost of the diachronic model battery?
  answers:
  - training-cost
- q:
  - How can publication dates be assigned to Project Gutenberg works at scale?
  - How accurate is an open-weight LLM at guessing when a book was written?
  - Can Llama3.3-70B replace GPT-4o for work-date attribution?
  answers:
  - date-attribution
- q:
  - How do you find candidate words for sense change using perplexity across periods?
  - Can a battery of period language models separate two senses of the same word?
  - What does the "station" example show about tracking sense trajectories?
  answers:
  - sense-trajectories
- q:
  - Can a model trained only on old text anticipate a sense that appears later?
  - What is the "end of the line" example evidence for?
  - Do earlier usages of a word prefigure later constructions?
  answers:
  - prefiguration
- q:
  - What should I read about using language models for historical linguistics?
  - Which paper argues for domain-restricted pretraining instead of finetuning in the digital
    humanities?
  - Where do I start on language models for diachronic change discovery?
  - Is there work on training separate LMs per time period for humanities research?
  answers:
  - context-pretraining-as-method
  - context-nonlexical-change
- q:
  - Is there released code for training time-sliced language models on my own corpus?
  - Where can I get the OED-based word sense cloze evaluation set?
  - How do I reuse the diachronic pretraining pipeline on a different corpus division?
  answers:
  - context-pipeline
misreadings:
- 'The period-pretrained models are not better language models than the finetuned baselines:
  they score lower on aggregate filtered BLiMP and complete fewer cloze tasks correctly. Their
  advantage is that their knowledge is bounded by their slice.'
- The monotonic rise in "only NPI licenser present" accuracy is evidence about the 1750-1940
  Project Gutenberg slices, not an established claim about the history of English NPI licensing;
  the authors note that extending it to the whole language would be fraught.
- The "end of the line" and "cholera" results are single hand-inspected cloze items offered
  as illustrations of hypothesis discovery, not aggregate detection scores for sense change.
- Higher cloze success by the finetuned models is not better diachronic performance, since
  part of it comes from recalling senses coined after the model's training slice.
- The 10-million-token slice size is a consequence of wanting 5 equal subcorpora from dated
  Project Gutenberg text, not a claim that 10M tokens is sufficient for knowledge-level historical
  inquiry; the paper suggests larger corpora for that.
terminology:
  leakage: Recall by a period-restricted language model of word senses first attested after
    the end of its training period, measured as top-100 cloze completion success on post-cutoff
    senses.
  maximally filtered BLiMP: The subset of BLiMP minimal pairs in which every word occurs at
    least twice in each of the training corpora being compared, so that all models under comparison
    have in-vocabulary coverage.
  perspectival language model: A language model pretrained only on one delineated slice of
    a corpus, such as a single time period or genre, so that its weights are guaranteed to
    contain no information from outside that slice.
  sense trajectory: The sequence of a word sense's acceptability, measured as normalized per-word
    perplexity, across a battery of models each pretrained on a consecutive period of the
    same corpus.
links_extra:
  code: https://github.com/comp-int-hum/historical-perspectival-lm
  evaluation_harness: https://github.com/sabrinaxinli/evaluation-pipeline-2024
---
