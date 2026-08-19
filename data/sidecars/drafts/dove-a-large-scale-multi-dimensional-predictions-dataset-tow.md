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

Then promote it:  python scripts/draft_sidecars.py --accept dove-a-large-scale-multi-dimensional-predictions-dataset-tow

Stamp: spec=74e012ff9654 checks=pass body=52b81eac5f3d
-->
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
- q:
  - What is DOVE?
  - What does the DOVE prompt perturbation dataset contain?
  - Is there a large public dataset of LLM predictions across many prompt variants?
  answers:
  - dove-dataset
  - holistic-joint-perturbation
- q:
  - What should I read about prompt sensitivity in LLM evaluation?
  - Which paper shows that single-prompt benchmark scores are unreliable?
  - Where can I start reading about how arbitrary prompt formatting affects benchmark results?
  answers:
  - dove-dataset
  - sensitivity-persists
  - original-prompt-divergence
- q:
  - How much can accuracy change just from changing the prompt format?
  - How big is prompt sensitivity on multiple-choice benchmarks?
  - Does prompt sensitivity disappear when you evaluate at a very large scale?
  answers:
  - sensitivity-persists
  - marginalized-dimensions
- q:
  - Do different LLMs prefer different answer enumerators?
  - Is there one prompt format that is best for all models?
  - Do roman numerals or letters work better as multiple-choice labels?
  answers:
  - model-specific-preferences
- q:
  - How do I pick a good prompt on a limited inference budget?
  - Is it better to tune each prompt dimension separately or search whole prompts?
  - What is the most sample-efficient way to choose a prompt format for a multiple-choice
    task?
  answers:
  - dimension-wise-selection
  - best-observed-needs-data
- q:
  - Do few-shot examples reduce prompt sensitivity?
  - Does five-shot prompting make benchmark scores more stable than zero-shot?
  - Can adding demonstrations solve the prompt sensitivity problem?
  answers:
  - fewshot-reduces-variance
- q:
  - How can you tell which benchmark questions are genuinely hard for a model?
  - What is an inherently hard instance in prompt-perturbation analysis?
  - Are there examples that models get wrong no matter how the prompt is phrased?
  answers:
  - inherently-hard-instances
- q:
  - Is the original prompt shipped with a benchmark representative of average model performance?
  - How far off is the default MMLU prompt from the average across prompt variations?
  answers:
  - original-prompt-divergence
- q:
  - How expensive is it to run a large multi-prompt evaluation?
  - How many GPU hours did building the DOVE dataset take?
  - What does it cost to evaluate thousands of prompt perturbations per instance?
  answers:
  - scale-cost
- q:
  - Which prompt dimensions does DOVE vary?
  - How many prompt perturbations are there per benchmark instance in DOVE?
  - What kinds of intent-preserving prompt changes are covered in this perturbation dataset?
  answers:
  - holistic-joint-perturbation
- q:
  - Can I contribute my own model's predictions to DOVE?
  - Is the DOVE dataset being extended to more models and languages?
  - How do research groups add evaluation data to a shared prompt-sensitivity repository?
  answers:
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
