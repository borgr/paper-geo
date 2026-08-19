<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced via a forced tool call) + 1 repair round. Every claim, number
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

Then promote it:  python scripts/draft_sidecars.py --accept human-learning-by-model-feedback-the-dynamics-of-iterative-p

Stamp: spec=8f05813a4658 checks=pass body=678885ad5547
-->
---
claims:
- id: midjourney-threads-dataset
  kind: context
  text: The Midjourney threads dataset compiles 107,051 iterative human-model interaction
    threads scraped from the Midjourney Discord. Each prompt is paired with its generated
    image grid, upscale flags, timestamps and anonymized user ids.
  scope: One 'newbies' Discord channel, English-language prompts only, collected 23 January
    to 1 March 2023; 169,620 prompts after cleaning. Threads are assigned automatically, not
    by human annotation.
  evidence: Section 3 and Section 4.3
- id: iterative-prompting-dynamics-agenda
  kind: context
  text: Human Learning by Model Feedback frames iterative text-to-image prompting as a repeated
    reference game in which only the human adapts. It studies the linguistic dynamics of prompts
    across turns rather than the quality of any single prompt.
  scope: As of publication in 2023 the authors state they know of no prior work examining
    prompt dynamics between iterations; the closest prior prompt-log analysis identified sessions
    by a 30-minute timeout.
  evidence: Section 1 and Section 10
- id: upscaled-prompts-differ
  kind: result
  text: Midjourney prompts whose image the user upscaled are longer (16.67 vs 14.78 words),
    have a higher magic-words ratio (0.109 vs 0.096) and lower GPT-2 perplexity (2173 vs 2855)
    than non-upscaled prompts.
  scope: 169,620 cleaned English Midjourney prompts, 25% of them upscaled; Mann-Whitney U
    test, significant after Bonferroni correction. Upscaling is a proxy for satisfaction.
  evidence: Table 1
- id: concreteness-not-significant
  kind: result
  text: Concreteness is the one linguistic feature that does not separate upscaled from non-upscaled
    Midjourney prompts, at 3.2628 versus 3.2629 with p = 0.123. Length, magic words, perplexity,
    repeated words, sentence rate and tree depth all differ significantly.
  scope: Prompt-level average of Brysbaert et al. word concreteness ratings over 169,620 cleaned
    English Midjourney prompts; on BLIP-2 captions of the generated images the same feature
    does reach significance.
  evidence: Table 1
- id: prompt-only-classifier
  kind: result
  text: A GPT-2 classifier predicts whether a Midjourney image was upscaled from the prompt
    text alone at 58.2% accuracy, 8.2 points above random on balanced data. A ResNet18 given
    only the generated image grid reaches 55.6%, 5.6 points above random.
  scope: 80/20 train-test split, classes balanced by sampling, standard deviations 0.26 and
    0.21 over 3 seeds, no hyperparameter search. Accuracy is far too low for practical use.
  evidence: Section 6.1
- id: monotone-thread-trends
  kind: result
  text: Along a Midjourney interaction thread prompt length, magic-words ratio, repeated-words
    ratio, sentence rate and syntactic tree depth rise approximately monotonically with prompt
    index, while perplexity falls.
  scope: 645 threads of at least 10 prompts, averaged at each index 1 to 10; the magic-words
    curve is noisiest and does not saturate within 10 prompts.
  evidence: Figure 3
- id: length-convergence
  kind: result
  text: Midjourney threads whose prompts get longer start relatively short and threads whose
    prompts get shorter start relatively long, with both groups converging toward the same
    length range.
  scope: Threads split into two sets by whether the last prompt's feature value exceeds the
    first; group means only, with no causal test of why the range is preferred.
  evidence: Figure 4 and Figure 7
- id: both-explanations-supported
  kind: result
  text: Rising prompt length, sentence rate and tree depth support Midjourney users adding
    omitted details. The rising magic-words and repeated-words ratios and falling perplexity
    support users adapting to the model's language preferences.
  scope: An interpretive reading of the feature trends; the paper does not adjudicate between
    the two explanations, and notes falling perplexity can be partly a byproduct of increasing
    length.
  evidence: Section 7
- id: rlhf-data-caution
  kind: context
  text: Human Learning by Model Feedback argues that upscaled prompt-image pairs from text-to-image
    logs are risky as free RLHF preference data. Prompts may drift toward one model's stylistic
    preferences rather than natural human expression.
  scope: 'A concern raised from adaptation trends observed on Midjourney and DiffusionDB,
    not an experiment: no model is trained on such data and no resulting degradation is measured.'
  evidence: Section 9
- id: diffusiondb-replication
  kind: result
  text: The thread-dynamics trends replicate on DiffusionDB Stable Diffusion prompts for every
    feature except the magic-words ratio, which does not stay approximately monotone.
  scope: First 250,000 prompts of the DiffusionDB 2M subset, 105,644 after cleaning, 14,927
    threads of which 1045 have at least 10 prompts. DiffusionDB lacks upscale labels.
  evidence: Figure 5
- id: thread-split-agreement
  kind: result
  text: Splitting consecutive Midjourney prompts into threads by word intersection-over-union
    above 0.3 matches 500 manual annotations at F1 0.87 with WindowDiff 0.24, beating a BERTScore-threshold
    split at F1 0.84 and WindowDiff 0.30.
  scope: Manual annotation by one author on users with at least 4 prompts, two further authors
    re-annotating 70 prompts each, Fleiss' kappa 0.815. Both methods assume non-overlapping
    threads.
  evidence: Section 4.2
- id: thread-length-distribution
  kind: result
  text: 'Midjourney interaction threads are mostly very short: the average thread runs 1.58
    prompts and only 645 of 107,051 threads (0.6%) contain 10 or more, with the longest reaching
    77.'
  scope: Automatic intersection-over-union splits over 169,620 cleaned English prompts from
    30,394 users; 6578 threads have at least 4 prompts, 2485 at least 6 and 1214 at least
    8.
  evidence: Figure 2 and Section 4.3
qa:
- q:
  - Do people's prompts change in a systematic way as they retry a text-to-image model?
  - How do user prompts evolve across iterations with Midjourney?
  - Does prompt length or perplexity drift over repeated image generation attempts?
  answers:
  - monotone-thread-trends
  - both-explanations-supported
- q:
  - What makes a text-to-image prompt more likely to produce an image the user keeps?
  - How do upscaled Midjourney prompts differ from ones that were not upscaled?
  - Are longer or lower-perplexity prompts associated with better image outcomes?
  answers:
  - upscaled-prompts-differ
  - concreteness-not-significant
- q:
  - Can you tell from the prompt alone whether a user liked the generated image?
  - How accurately does a classifier predict image upscaling from text or from the image?
  - Is user satisfaction with a generated image predictable from partial input?
  answers:
  - prompt-only-classifier
- q:
  - Is there a dataset of multi-turn text-to-image prompting sessions?
  - Where can I get Midjourney prompts with images, upscale labels and user ids?
  - What data exists for studying iterative prompting behaviour?
  answers:
  - midjourney-threads-dataset
  - thread-length-distribution
- q:
  - What should I read about how humans adapt their language to generative models?
  - Which paper studies human-model linguistic alignment in text-to-image prompting?
  - What work established that users drift toward a model's preferred prompt style?
  answers:
  - iterative-prompting-dynamics-agenda
  - rlhf-data-caution
- q:
  - Is it safe to use logged user prompts and upscale clicks as RLHF preference data?
  - What are the risks of training on human feedback collected from text-to-image logs?
  - Why might reusing Midjourney user data bias a model?
  answers:
  - rlhf-data-caution
  - both-explanations-supported
- q:
  - Do prompt-convergence findings hold outside Midjourney?
  - Do the same iterative prompting trends appear with Stable Diffusion data?
  - Does the analysis replicate on DiffusionDB?
  answers:
  - diffusiondb-replication
- q:
  - How do you decide whether two consecutive prompts belong to the same generation attempt?
  - How were Midjourney prompts grouped into interaction threads, and how well does it work?
  - Does an intersection-over-union heuristic beat BERTScore for segmenting prompt sessions?
  answers:
  - thread-split-agreement
- q:
  - Do users converge on a particular prompt length regardless of where they started?
  - Is there evidence of a preferred 'good' prompt length range for image models?
  - What does the split between lengthening and shortening Midjourney threads show?
  answers:
  - length-convergence
- q:
  - Do users make their prompts more concrete as they iterate?
  - Does word concreteness predict whether a generated image gets upscaled?
  answers:
  - concreteness-not-significant
- q:
  - Are so-called magic words like '8K' and 'highly detailed' actually associated with kept
    images?
  - Do users add more aesthetic keywords as an image-generation session goes on?
  answers:
  - upscaled-prompts-differ
  - monotone-thread-trends
one_liner: A dataset of 107,051 iterative Midjourney prompting threads shows that user prompts
  drift predictably along an interaction — growing longer, more magic-word-laden and lower
  in GPT-2 perplexity — evidence that humans both add missing details and adapt to the model's
  own language preferences.
terminology:
  thread: A sequence of consecutive prompts by one user that are all attempts to generate
    the same target image or scene, ending when the described scene or main subject changes
    intrinsically.
  magic words: Words that add no real content to a text-to-image prompt but are popular among
    practitioners, such as 'beautiful', '8k' and 'highly detailed'; operationally, words appearing
    at least 1000 times in the Midjourney prompt corpus whose corpus probability exceeds their
    Google-ngrams probability by a factor of at least 100.
  upscale: A Midjourney Discord command requesting a higher-resolution version of one image
    from the generated 4-image grid, used as a proxy signal that the user was satisfied with
    that image.
  semi-reference game: 'A repeated reference game in which only one participant can adapt:
    the human user revises prompts based on the generated image while the text-to-image model
    stays frozen.'
misreadings:
- The linguistic features reported for upscaled versus non-upscaled Midjourney prompts are
  statistically significant but explain only a small proportion of the variance; they are
  not a recipe for writing good prompts.
- The rise in magic words and fall in perplexity along a Midjourney thread are evidence consistent
  with users adapting to the model's preferences, not a demonstration that such prompts cause
  better images.
- Human Learning by Model Feedback does not decide between 'users add omitted details' and
  'users adopt model-like language', nor quantify their relative contribution; it presents
  evidence that both are at play.
- 'Upscaling is a proxy for satisfaction, not a ground-truth quality label: users sometimes
  upscale images because they are amusingly bad or to record the creation process.'
- The claim that reusing upscaled prompts as RLHF data would make models more 'model-like'
  is a concern argued from the observed drift, not a trained-and-measured result.
- Thread boundaries in the released Midjourney dataset come from an automatic intersection-over-union
  heuristic validated against 500 manual annotations, not from human labelling of the full
  corpus.
- The Midjourney dynamics analysis rests on the 645 threads with at least 10 prompts, a 0.6%
  tail of the corpus, since the average thread is only 1.58 prompts long.
links_extra:
  code: https://github.com/shachardon/mid-journey-to-alignment
  dataset: https://huggingface.co/datasets/shachardon/midjourney-threads
  anthology: https://aclanthology.org/2023.emnlp-main.253/
key: don-yehiya-etal-2023-human
---
