---
claims:
- id: dove-dataset
  kind: context
  text: DOVE (Dataset Of Variation Evaluation) is a publicly released dataset of more than
    250M LLM prompt perturbations and model outputs, built for studying prompt sensitivity
    and building more robust evaluation protocols.
  scope: English multiple-choice benchmarks only (MMLU, MMLU-Pro, ARC, HellaSwag, OpenBookQA,
    Social IQa, RACE); open-weight Llama 1B/3B/8B, OLMo 7B and Mistral 7B as of the 2025 release;
    no open-ended generation tasks.
  evidence: Section 1
- id: holistic-joint-perturbation
  kind: context
  text: DOVE varies 5 prompt dimensions jointly rather than one dimension at a time, giving
    over 6.5K perturbations per base instance. The dimensions are enumerator, separator, choices
    order, instruction phrasing and demonstrations, combined as a Cartesian product.
  scope: The 5 dimensions were chosen from a survey of prior sensitivity work and are not
    claimed exhaustive; 78 source datasets with 100 instances each, 7,800 base instances.
  evidence: Table 1
- id: scale-cost
  text: Building DOVE required roughly 5,000 GPU hours on NVIDIA A100 80GB GPUs, with Mistral-7B
    alone taking 1,189 GPU hours, and would cost upwards of $25K on cloud services such as
    AWS.
  scope: Generation with vLLM at approximately 60M instances per model for 5 open-weight models;
    closed API models were excluded partly for this reason.
  evidence: Section 4.1
- id: sensitivity-persists
  text: 'Prompt sensitivity does not wash out at scale: OLMo''s accuracy on HellaSwag ranges
    from 1% to 99% depending on which intent-preserving prompt is used.'
  scope: Accuracy computed over 100 instances per dataset per prompt; multiple-choice items
    scored by semantic similarity matching.
  evidence: Figure 3
- id: marginalized-dimensions
  text: 'Each individual prompt dimension moves accuracy even after averaging over all the
    others: for Mistral, different instruction paraphrases alone produce an 8% accuracy difference.'
  scope: Marginalized accuracy over the 5 DOVE dimensions, computed per domain for Llama 1B/3B/8B,
    OLMo 7B and Mistral 7B; 13 instruction phrasings.
  evidence: Figure 4
- id: model-specific-preferences
  text: 'Models have distinct prompt preferences rather than a shared best format: greek numerals
    are OLMoE''s best-performing enumerator of the 6 tested but only Mistral''s third best,
    behind capital and lateen numerals.'
  scope: 6 enumerator values, accuracy marginalized over all other dimensions and averaged
    across the dataset; established for the evaluated open-weight models only.
  evidence: Figure 4
- id: original-prompt-divergence
  text: A benchmark's original prompt is often not representative of average performance across
    intent-preserving prompts. Mistral's accuracy with original instructions exceeds its mean
    across prompts by more than 1 standard deviation on 35 of 57 MMLU domain tasks.
  scope: Divergence measured across few-shot prompts, with divergence defined as exceeding
    1 standard deviation; MMLU domains, Mistral-7B; full per-model results in Appendix B.3.
  evidence: Figure 5
- id: dimension-wise-selection
  text: Choosing the best value for each of the 5 prompt dimensions independently, marginalizing
    the others, matches linear regression on observed samples and beats picking the single
    best observed prompt.
  scope: Zero-shot selection simulated on DOVE against the best prompt over the full dataset,
    mean and standard deviation over 10 random seeds; 4 strategies including a random baseline.
  evidence: Figure 6
- id: best-observed-needs-data
  text: Selecting the best observed prompt only becomes a reliable strategy after tens of
    millions of observed samples, while dimension-wise selection works with relatively small
    sample sizes.
  scope: Zero-shot setting, gap from the best prompt in DOVE as a function of sample count,
    for Llama 1B/3B/8B, OLMo 7B and Mistral 7B; AUC comparison across models in Appendix B.4.
  evidence: Figure 7
- id: fewshot-reduces-variance
  text: 'Five-shot prompting consistently narrows the spread of accuracy across prompt perturbations
    compared to zero-shot, but does not eliminate it: the accuracy range still exceeds 20%
    on every dataset shown.'
  scope: Subset of DOVE domains, each point an accuracy over 100 instances; the effect is
    minimal for Social IQa and the MMLU-Pro legal domain.
  evidence: Figure 8
- id: inherently-hard-instances
  text: Success-rate distributions over the more than 6.5K perturbations per instance identify
    instances a model answers wrongly under every perturbation. Such instances give an operational
    definition of inherently hard items that no prompt selection can fix.
  scope: Success rate is the percentage of a sample's perturbations answered correctly; measured
    per model on DOVE's multiple-choice instances; at both extremes models are also least
    prompt-sensitive.
  evidence: Figure 9
- id: living-benchmark
  kind: context
  text: DOVE is maintained as an extensible community resource with a standardized schema
    for multi-dimensional evaluation data, so that model predictions from other groups can
    be converted in rather than re-run.
  scope: As of the 2025 Findings of ACL release; contributions arrive via HuggingFace pull
    requests or email; coverage at release is English-centric and limited in model diversity.
  evidence: Section 6
qa:
- ask:
    plain: is there a big public collection of language model answers to the same questions
      written many different ways?
    jargon: what does the DOVE corpus of multi-dimensional prompt perturbations and model
      outputs cover?
    task: where can I get pre-computed model predictions across thousands of prompt variants
      instead of generating them myself?
    practitioner: can I download an existing prompt-variation evaluation dataset rather than
      running my own sweep?
  answered_by:
  - dove-dataset
  - holistic-joint-perturbation
- ask:
    plain: which research showed that scoring a model with one fixed prompt gives a misleading
      benchmark number?
    jargon: what work should I read first on prompt sensitivity undermining single-prompt
      benchmark evaluation?
    task: how do I justify to reviewers that a single-template benchmark score is not enough?
    practitioner: should I stop trusting leaderboard numbers that come from one prompt template
      per benchmark?
  answered_by:
  - dove-dataset
  - sensitivity-persists
  - original-prompt-divergence
- ask:
    plain: how much can a model's score move if you only reword the question or shuffle the
      answer options?
    jargon: what is the magnitude of accuracy variance across intent-preserving prompt perturbations
      on multiple-choice benchmarks?
    task: how do I find out how wide the accuracy range for my model is across formatting
      variants of the same task?
    practitioner: if I evaluate at a much larger scale, will prompt sensitivity average out?
  answered_by:
  - sensitivity-persists
  - marginalized-dimensions
- ask:
    plain: do different language models do best with different answer labels like A/B/C, roman
      numerals or greek letters?
    jargon: are optimal enumerator choices model-specific or is there a universally best multiple-choice
      format?
    task: how do I pick answer-option labels for a multiple-choice task across several models
      at once?
    practitioner: can I reuse the prompt format that worked well for one model on a different
      model?
  answered_by:
  - model-specific-preferences
- ask:
    plain: is it better to pick the single best prompt you tried, or to choose each formatting
      choice separately?
    jargon: does dimension-wise marginal selection beat argmax over observed prompts for prompt-format
      optimization?
    task: how do I choose a prompt format for a multiple-choice task with as few trial runs
      as possible?
    practitioner: I can only afford a few hundred prompt trials, how should I use them to
      settle on a format?
  answered_by:
  - dimension-wise-selection
  - best-observed-needs-data
- ask:
    plain: does showing a few worked examples in the prompt make a model's score less dependent
      on wording?
    jargon: does 5-shot prompting reduce accuracy variance across prompt perturbations relative
      to 0-shot?
    task: how do I make benchmark scores more stable across formatting changes?
    practitioner: if I switch to few-shot prompting, do I still need to worry about prompt
      sensitivity?
  answered_by:
  - fewshot-reduces-variance
- ask:
    plain: how can you tell which test questions a model gets wrong no matter how you ask
      them?
    jargon: how are success-rate distributions over prompt perturbations used to identify
      inherently hard instances?
    task: how do I separate genuinely difficult benchmark items from ones my model fails only
      for formatting reasons?
    practitioner: should I spend effort on prompt engineering for the items my model keeps
      failing, or are they hopeless?
  answered_by:
  - inherently-hard-instances
- ask:
    plain: is the prompt that ships with a benchmark like MMLU typical of how a model does
      on average?
    jargon: how far does accuracy under a benchmark's original template diverge from the mean
      over intent-preserving prompts?
    task: how do I check whether the default template I am evaluating with is flattering my
      model?
    practitioner: should I report the default MMLU prompt score or an average over prompt
      variants?
  answered_by:
  - original-prompt-divergence
- ask:
    plain: how much compute and money does it take to test one model on thousands of reworded
      versions of every question?
    jargon: what GPU-hour and cloud budget was needed to generate over 250M prompt perturbation
      outputs?
    task: how do I budget for an evaluation that sweeps thousands of prompt variants per instance?
    practitioner: can I afford to run a full multi-prompt sensitivity evaluation on my own
      hardware?
  answered_by:
  - scale-cost
- ask:
    plain: which parts of a prompt get changed in a large prompt-variation dataset, and how
      many versions of each question are there?
    jargon: which perturbation dimensions does DOVE vary, and what is the per-instance perturbation
      count from their Cartesian product?
    task: how do I build a prompt sweep that varies separators, option order and instruction
      phrasing together instead of one at a time?
    practitioner: does a prompt-variation dataset cover the formatting axes I actually care
      about, like demonstrations and option order?
  answered_by:
  - holistic-joint-perturbation
- ask:
    plain: can other research groups contribute their own model outputs to a shared prompt-variation
      dataset?
    jargon: is the DOVE resource maintained as a living benchmark with a standardized schema
      for contributed evaluation data?
    task: how do I add predictions from my own model to a shared prompt-sensitivity dataset
      without re-running everything?
    practitioner: if I contribute my evaluation runs, will they be usable alongside the existing
      prompt perturbation data?
  answered_by:
  - living-benchmark
one_liner: DOVE (Dataset Of Variation Evaluation) is a public dataset of over 250M LLM predictions
  in which every benchmark instance is perturbed jointly along 5 intent-preserving prompt
  dimensions, so prompt sensitivity can be measured and mitigated at scale.
coined: DOVE
gloss: Dataset Of Variation Evaluation — a large collection of LLM answers to the same benchmark
  questions asked in thousands of slightly different prompt formats
terminology:
  Intent-preserving prompts: Two prompts designed to convey the same underlying meaning to
    a model despite differences in phrasing or structure, e.g. adding "Answer the following
    question:" before the same multiple-choice item.
  Prompt dimension: A set of interchangeable prompt choices whose values all preserve the
    prompt's intent, such as the answer enumerator (capitals, lowercase, numbers, roman numerals,
    keyboard symbols, greek letters).
  Prompt linearization: The deterministic function that maps an underlying question plus one
    chosen value per prompt dimension into a single concrete prompt string given to an LLM.
  Marginalized accuracy: The accuracy of a model for one fixed value of a single prompt dimension,
    averaged over all combinations of values of the remaining dimensions.
  Divergence score: The number of standard deviations by which a model's accuracy using a
    benchmark's original prompt deviates from its mean accuracy across all prompt perturbations,
    with divergence counted when it exceeds 1.
  Success rate: For one benchmark instance and one model, the percentage of that instance's
    prompt perturbations for which the model outputs the correct answer.
  Inherently hard instance: A benchmark instance a model answers incorrectly under every prompt
    perturbation tested, so no prompt selection can recover it.
misreadings:
- 'DOVE is not a new benchmark of questions: it is a dataset of model predictions, log probabilities
  and scores built on top of existing benchmarks such as MMLU, ARC and RACE.'
- 'The finding that few-shot demonstrations reduce sensitivity does not mean five-shot evaluation
  is stable: the accuracy range across perturbations remains above 20% on every dataset measured,
  and the effect is minimal for Social IQa and the MMLU-Pro legal domain.'
- The 1%-to-99% HellaSwag range is a range across individual intent-preserving prompts, not
  a confidence interval on a single score; each endpoint is an accuracy obtained with some
  legitimate prompt format.
- DOVE does not show that prompt sensitivity is confined to small open-weight models; only
  open-weight models up to 8B were run, because API models alter prompts in undisclosed ways
  and costs were infeasible.
- '"Independent dimension-wise selection works best" is a statement about sample efficiency
  under a fixed budget, not a claim that prompt dimensions do not interact; with tens of millions
  of samples the best-observed-prompt strategy becomes reliable too.'
links_extra:
  project page: https://slab-nlp.github.io/DOVE
  dataset (full, 2TB): https://huggingface.co/datasets/nlphuji/DOVE
  dataset (lite, 100GB): https://huggingface.co/datasets/nlphuji/DOVE_Lite
key: habba2025dove
---
