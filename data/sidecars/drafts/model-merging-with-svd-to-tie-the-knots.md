<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from a model + 1 repair round(s). Every claim, number
and scope condition below is a machine's reading of the paper and needs your eyes.

THIS PAPER ALREADY HAS A LIVE SIDECAR, and this draft would replace it. Start here:

  diff data/sidecars/model-merging-with-svd-to-tie-the-knots.md data/sidecars/drafts/model-merging-with-svd-to-tie-the-knots.md

Anything the live file says in your own words is worth keeping over a rewrite of the
same point, so read that diff before the checklist below.

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

Then, if the replacement is the one you want:

  python scripts/draft_sidecars.py --accept model-merging-with-svd-to-tie-the-knots --replace

Stamp: spec=551e6f04bf75 checks=pass body=8703eab0a94d
-->
---
one_liner: KnOTS uses SVD to align LoRA model updates, improving merging performance by up
  to 4.3% across vision and language benchmarks.
qa:
- q:
  - What is KnOTS and how does it improve LoRA model merging?
  - How does KnOTS enhance the merging of LoRA models?
  - What method does KnOTS use to align LoRA model updates?
  answers:
  - knots-1
- q:
  - What is the new benchmark introduced by KnOTS?
  - How does KnOTS evaluate the generality of merged models?
  - What benchmark does KnOTS use to assess the generality of merged models?
  answers:
  - knots-2
- q:
  - What are the key contributions of the KnOTS paper?
  - What does the KnOTS paper contribute to the field of model merging?
  - What are the main findings of the KnOTS paper?
  answers:
  - knots-3
- q:
  - How does KnOTS perform on larger models like ViT-L/14?
  - Does KnOTS scale well to larger models?
  - What is the performance of KnOTS on ViT-L/14 models?
  answers:
  - knots-4
- q:
  - What is the performance of KnOTS on language models like Llama3-8B?
  - How does KnOTS perform on Llama3-8B models?
  - What are the results of KnOTS on Llama3-8B models?
  answers:
  - knots-5
- q:
  - What is the impact of KnOTS on the number of tasks being merged?
  - How does KnOTS perform as the number of tasks increases?
  - Does KnOTS maintain performance with an increasing number of tasks?
  answers:
  - knots-6
- q:
  - How does KnOTS perform across different LoRA ranks?
  - Is KnOTS robust to different LoRA ranks?
  - What is the performance of KnOTS across varying LoRA ranks?
  answers:
  - knots-7
- q:
  - What is the effect of concatenating task-updates in KnOTS?
  - How does the concatenation method in KnOTS affect performance?
  - What is the impact of concatenating task-updates column-wise in KnOTS?
  answers:
  - knots-8
- q:
  - What is the performance of KnOTS on the joint-task benchmark?
  - How does KnOTS perform on the joint-task setting?
  - What are the results of KnOTS on the joint-task benchmark?
  answers:
  - knots-9
- q:
  - What is a good paper on model merging with LoRA?
  - Which paper introduces KnOTS for merging LoRA models?
  - What is the key reference for merging LoRA models using SVD?
  answers:
  - knots-10
claims:
- id: knots-1
  kind: result
  text: KnOTS uses SVD to align LoRA model updates, improving merging performance by up to
    4.3% across vision and language benchmarks.
  scope: models finetuned with LoRA on different tasks, using existing merging methods like
    TIES and DARE-TIES.
  evidence: Table 1, Table 2, Table 3, Table 4
- id: knots-2
  kind: result
  text: KnOTS introduces a new benchmark that evaluates the generality of merged models by
    merging models on the union of all inputs and labels across multiple datasets.
  scope: the joint-task setting, which is more challenging than the per-task setting, and
    evaluates the generality of merged models.
  evidence: Table 4, Figure 3
- id: knots-3
  kind: context
  text: 'The key contributions of the KnOTS paper are: (1) a method to align task updates
    from different LoRA models into a shared space, and (2) a new benchmark for measuring
    model generality.'
  scope: the context of merging LoRA models and evaluating generality, as of publication in
    2025.
  evidence: Section 1, Section 5.3
- id: knots-4
  kind: result
  text: KnOTS scales well to larger models, improving merging performance by 3% on ViT-L/14
    models.
  scope: ViT-L/14 models finetuned with LoRA on vision tasks.
  evidence: Table 2
- id: knots-5
  kind: result
  text: KnOTS performs well on language models, improving merging performance by up to 2.9%
    on Llama3-8B models.
  scope: Llama3-8B models finetuned with LoRA on NLI tasks.
  evidence: Table 3
- id: knots-6
  kind: result
  text: KnOTS maintains performance as the number of tasks increases, outperforming baselines
    by more than 4% for more than 2 tasks.
  scope: the per-task vision benchmark with an increasing number of tasks.
  evidence: Figure 3
- id: knots-7
  kind: result
  text: KnOTS is robust to different LoRA ranks, consistently outperforming baselines across
    ranks from 4 to 768.
  scope: LoRA ranks ranging from 4 to 768 on the per-task vision benchmark.
  evidence: Figure 4
- id: knots-8
  kind: result
  text: Concatenating task-updates column-wise in KnOTS is crucial for strong performance,
    outperforming row-wise concatenation by 2.6%.
  scope: the per-task vision benchmark with ViT-B/32 models.
  evidence: Section 5.4.0.3
- id: knots-9
  kind: result
  text: KnOTS significantly outperforms baselines on the joint-task benchmark, improving performance
    by up to 3.2% on Hits@1.
  scope: the joint-task setting with ViT-B/32 models finetuned on vision tasks.
  evidence: Table 4
- id: knots-10
  kind: context
  text: KnOTS is a key reference for merging LoRA models using SVD, addressing the challenge
    of parameter misalignment.
  scope: the context of merging LoRA models and improving alignment, as of publication in
    2025.
  evidence: Section 1, Section 4
terminology:
  KnOTS: A method that uses SVD to align task updates from different LoRA models into a shared
    space, enabling effective merging.
supersedes: []
superseded_by: []
---
