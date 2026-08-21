---
claims:
- id: human-llm-gap
  text: On EWoK-core-1.0, the best of 20 open-weights LLMs tested (falcon-40b-instruct) reaches
    0.801 mean LogProbs accuracy against 0.951 for humans, with chance at 0.5.
  kind: result
  evidence: Table 4
  scope: Open-weights models from 1.3B to 70B parameters, scored with LogProbs on English
    items; human norms from 1,262 US-resident native English speakers.
- id: social-vs-physical
  text: 'LLMs score highest on EWoK''s social domains and lowest on relational physical ones:
    average LLM accuracy is 0.859 on social interactions and 0.615 on spatial relations, where
    humans score 1.000 and 0.958.'
  kind: result
  evidence: Table 5
  scope: Averages across 20 open-weights LLMs on EWoK-core-1.0 with LogProbs scoring; physical
    dynamics is the one domain where humans (0.833) sit below the best LLM (0.920).
- id: domain-not-surface
  text: Domain remains a significant predictor of LLM accuracy on EWoK-core-1.0 after controlling
    for item length, word frequency, context type and contrast type. In the same mixed-effects
    logistic regression, word frequency (+0.07) and number of words (-0.04) are also significant.
  kind: result
  evidence: Table B.2 (mixed-effects results, Appendix B)
  scope: Item-level binary accuracy pooled over the 20 open-weights LLMs under LogProbs, with
    random intercepts for model and item.
- id: version-variance
  text: Swapping only the names, objects and locations that fill EWoK templates moves LLM
    accuracy by up to 0.07 across 5 dataset versions (phi-1.5 and phi-2), while human accuracy
    moves by 0.02.
  kind: result
  evidence: Table 4
  scope: 5 filler-sampled versions of EWoK-core-1.0 with fillers held constant within a version;
    ranges are per-model over whole-dataset means, and most models vary less than phi-1.5
    and phi-2.
- id: logprobs-beats-prompting
  text: LogProbs scoring beats 2-shot constrained prompting (Likert and Choice) for nearly
    all 20 open-weights LLMs on EWoK-core-1.0, with the gap larger for smaller models.
  kind: result
  evidence: Figure 5
  scope: One fixed prompt per task, outputs logit-masked to 1-5 or 1-2; no targeted prompt
    engineering or chain-of-thought was tried.
- id: likert-degenerate
  text: Under a strict-inequality Likert metric that removes the 0.5-point credit for tied
    ratings, Meta-Llama-3-70B falls to 0.588 and mpt-7b to 0.021 on EWoK-core-1.0. Prompted
    models frequently return the same plausibility rating for every item.
  kind: result
  evidence: Table B.2 (strict-inequality Likert table, Appendix B)
  scope: The 12 models evaluated with Likert prompting; the main paper's metric awards 0.5
    for a tie, which preserves a 50% floor for any context-insensitive responder.
- id: frontier-models-helm
  text: Frontier closed models evaluated on EWoK-core-1.0 via HELM in January 2025 top out
    near 0.912 (GPT-4 Turbo) and 0.911 (Claude 3.5 Sonnet) under Choice prompting, still below
    the human 0.951.
  kind: result
  evidence: Table 2
  scope: Choice prompting only, 2-shot, since log probabilities are unavailable for closed
    models; EWoK-core-1.0 was public from May 2024, so later models may have seen it.
- id: bow-baseline
  text: A bag-of-words baseline that picks the context with the highest word2vec cosine similarity
    to the target reaches only 0.542 on EWoK-core-1.0, against a 0.5 chance floor. Every LLM
    tested except phi-1 (0.522) scores above it.
  kind: result
  evidence: Table 4
  scope: Summed word2vec embeddings per context and per target, cosine-matched on English
    EWoK-core-1.0 items; speaks only to lexical-overlap shortcuts, not to other heuristics.
- id: dataset-scale
  text: EWoK-core-1.0 contains 4,374 items built from 880 expert-curated templates covering
    192 concepts across 11 domains, with each domain contributing between 75 and 1130 templates
    and testing between 12 and 22 concepts.
  kind: result
  evidence: Table 1
  scope: English-language items only, generated from over 500 fillers across 13 classes under
    28 type restrictions; domain and concept lists chosen by the author team.
- id: context-dependence-design
  text: EWoK holds each target sentence fixed and varies the context so that the identical
    sentence is plausible under one context and implausible under the other. This prevents
    a model from succeeding on target-sentence frequency alone.
  kind: context
  scope: The framework as released, extending the minimal-pair tradition of BLiMP and COMPS
    to minimal pairs of both contexts and targets; shortcut resistance is checked only via
    a bag-of-words baseline and surface-feature analyses.
- id: framework-context
  text: EWoK is a cognition-inspired framework for evaluating world knowledge in language
    models. Its items are organised around concepts from domains known to recruit dedicated
    cognitive and neural machinery in humans, rather than around available text corpora.
  kind: context
  scope: Domains selected by an author team of cognitive scientists and neuroscientists from
    prior human literature; currently English only, and adapting the framework to other languages
    would require redesigning the concept inventory.
- id: generative-not-fixed-benchmark
  text: EWoK ships as a generative pipeline rather than a fixed test set. Users can regenerate
    datasets with new fillers such as non-Western names, nonwords or longer descriptors, and
    measure how much of a model's score depends on arbitrary item choices.
  kind: context
  scope: The released framework code and templates, gated behind terms of use requiring reporting
    of any training on EWoK-generated data; the paper exercises only the 5-version filler
    resampling, not the name or nonword substitutions.
- id: human-labels-imperfect
  text: Human raters on EWoK-core-1.0 average 0.951 accuracy against author gold labels and
    systematically err on absolute spatial reference frames, often judging cardinal-direction
    items as plausible when the gold label is implausible.
  kind: result
  evidence: Section 5, "Human ratings are usually, but not always, accurate"
  scope: 1,262 US-resident native English speakers, at least 5 ratings per item, 59 participants
    excluded for inter-subject correlation below 0.3; average inter-subject Pearson correlation
    was 0.744.
qa:
- ask:
    plain: do language models understand everyday facts about the physical and social world
      as well as people do?
    jargon: how large is the human-model accuracy gap on minimal-pair world-knowledge evaluation
      of open-weights and frontier LLMs?
    task: how do I find out whether a language model has the basic world knowledge a human
      rater would have?
    practitioner: if I need a model that reliably handles basic physical and social world
      knowledge, can I count on current LLMs to match human raters?
  answered_by:
  - human-llm-gap
  - frontier-models-helm
- ask:
    plain: which kinds of everyday knowledge do language models handle worst, social situations
      or physical space?
    jargon: do LLMs show a domain dissociation between social-interaction items and spatial-relation
      items in world-knowledge evaluation?
    task: how do I tell whether a model's weak spot is spatial reasoning or social reasoning
      before I build on it?
    practitioner: my application depends on spatial relations rather than social inference,
      should I expect a language model to be weaker there?
  answered_by:
  - social-vs-physical
- ask:
    plain: is it more reliable to compare sentence probabilities or to ask a model to rate
      how plausible a sentence is?
    jargon: does LogProbs minimal-pair scoring outperform few-shot constrained Likert and
      Choice prompting for world-knowledge items?
    task: how should I score a plausibility benchmark so that small models are not penalised
      by their inability to follow rating instructions?
    practitioner: should I evaluate my model with log-probability scoring or with a prompted
      plausibility rating?
  answered_by:
  - logprobs-beats-prompting
  - likert-degenerate
- ask:
    plain: if you swap the names and objects inside a template-generated test, how much do
      model scores move?
    jargon: how much variance in LLM accuracy comes from filler instantiation across regenerated
      versions of a templated world-knowledge dataset?
    task: how do I know whether a 1-point difference between two models on a synthetic benchmark
      is real or an artefact of the items?
    practitioner: can I trust a small score gap between two models on a template-generated
      benchmark, or should I regenerate the items first?
  answered_by:
  - version-variance
- ask:
    plain: could a model pass these plausibility questions just by matching words between
      the sentence and the context?
    jargon: is context-dependent plausibility discrimination solvable by lexical-overlap heuristics
      such as word2vec cosine similarity?
    task: how do I check that a world-knowledge benchmark is not solvable by shallow word-overlap
      shortcuts?
    practitioner: before I use a world-knowledge benchmark, how do I know it is testing knowledge
      rather than surface word similarity?
  answered_by:
  - bow-baseline
  - context-dependence-design
- ask:
    plain: are some world-knowledge topics really harder for language models, or is it just
      that those sentences are longer or use rarer words?
    jargon: does domain remain a significant predictor of LLM item accuracy after controlling
      for item length, word frequency, context type and contrast type in a mixed-effects logistic
      regression?
    task: how do I separate genuine domain difficulty from surface confounds when analysing
      per-item model accuracy?
  answered_by:
  - domain-not-surface
- ask:
    plain: what is a good benchmark for testing whether a language model has basic knowledge
      of how the world works?
    jargon: which evaluation framework organises world-model probing around human core-knowledge
      domains rather than around available corpora?
    task: where should I start reading if I want to evaluate world modeling in language models?
    practitioner: I need to assess world knowledge in my model rather than trivia recall,
      which benchmark should I pick?
  answered_by:
  - framework-context
  - context-dependence-design
- ask:
    plain: how big is the world-knowledge test set and what topics does it cover?
    jargon: how many items, templates, concepts and domains does EWoK-core-1.0 contain?
    task: how do I check whether a world-knowledge benchmark has enough items per concept
      for my analysis?
    practitioner: is the EWoK-core dataset large enough and broad enough to report as a headline
      evaluation?
  answered_by:
  - dataset-scale
- ask:
    plain: what happens to a world-knowledge benchmark once the strongest models score near
      the top of it?
    jargon: how does a generative item-construction pipeline extend the useful life of a world-modeling
      evaluation as frontier models approach human accuracy?
    task: how do I keep an evaluation of world knowledge informative when new models start
      saturating the released version?
    practitioner: should I treat EWoK as a fixed leaderboard set or generate my own version
      with different fillers?
  answered_by:
  - generative-not-fixed-benchmark
  - frontier-models-helm
- ask:
    plain: how often do human raters themselves get everyday plausibility judgments wrong?
    jargon: what is human agreement with gold labels on EWoK-core-1.0 items, and which domain
      shows systematic annotator error?
    task: how do I set a human ceiling for a plausibility benchmark and know which items humans
      get wrong?
    practitioner: if I compare my model against the human ceiling on world-knowledge items,
      how solid is that ceiling?
  answered_by:
  - human-labels-imperfect
- ask:
    plain: how do the strongest commercial chatbots score on basic world knowledge compared
      with people?
    jargon: what accuracy do frontier closed models such as GPT-4 Turbo and Claude 3.5 Sonnet
      reach on EWoK-core-1.0 under Choice prompting?
    task: how do I find out whether closed API models have been evaluated on world-modeling
      items and how they did?
    practitioner: is a frontier API model good enough on everyday world knowledge for me to
      skip my own evaluation?
  answered_by:
  - frontier-models-helm
coined: EWoK
gloss: Elements of World Knowledge — a template-based framework for testing whether language
  models can tell plausible from implausible scenarios in physical, spatial and social domains
key: ivanova2024elements
one_liner: 'EWoK evaluates language models'' basic world knowledge with minimal pairs of pairs:
  the same target sentence is plausible under one context and implausible under another, so
  success requires contextual reasoning rather than memorised sentence frequency.'
misreadings:
- EWoK-core-1.0 was not designed to be a difficult challenge benchmark; it is a broad-coverage
  inventory of core human knowledge, so high frontier-model scores are expected rather than
  evidence the benchmark failed.
- 'The low LLM accuracy on spatial and physical relations is not attributable to longer or
  rarer wording: domain stays a significant predictor of accuracy after item length and word
  frequency are entered into the same regression.'
- Human accuracy of 0.951 on EWoK-core-1.0 is not a ceiling that validates every item — human
  raters make systematic errors on absolute spatial reference frames, and human data supplements
  rather than replaces author gold labels.
- The finding that LogProbs beats prompting is specific to one fixed 2-shot constrained prompt
  used identically for humans and models; it is not a claim that no prompting strategy can
  do better.
- Llama 3 Instruct 8B's 0.171 in the HELM Choice evaluation reflects failure to produce the
  required response format, not knowledge worse than chance.
- EWoK is a generation pipeline, not only the 4,374-item EWoK-core-1.0 release, so results
  on one version are results on one sample of fillers.
terminology:
  Choice: A prompt-based evaluation in which both contexts are shown with a single target
    sentence and the respondent selects which context better matches it.
  Likert: A prompt-based evaluation in which each context-target concatenation is rated for
    plausibility on a 1-5 scale, with correctness scored by comparing ratings across the pair.
  LogProbs: Scoring a context-target pair by the sum of the model's conditional log probabilities
    of the target tokens given the context, then checking whether each target is more probable
    under its matching context.
  domain distinguishability: The property of a benchmark that some knowledge domains are much
    easier than others, in contrast to model distinguishability, where different models separate
    from one another.
  indirect template: A template in which the target does not have to be true given the matching
    context, only more likely than under the contrasting context.
  minimal pairs of pairs: An item design in which both the two contexts and the two target
    sentences differ by a single targeted change, so that each target matches exactly one
    of the two contexts.
  version: One full instantiation of a template set with a particular random sample of fillers;
    several versions of the same templates measure how much accuracy depends on arbitrary
    name and object choices.
links_extra:
  dataset: https://huggingface.co/datasets/ewok-core/EWoK-core-1.0
  framework code: https://github.com/ewok-core/ewok
  project page: http://ewok-core.github.io
---
