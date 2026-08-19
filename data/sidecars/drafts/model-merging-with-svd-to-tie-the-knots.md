<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from Qwen 2.5 72B via RITS, then hand-corrected: the enumerated contributions claim dropped as already covered, comparators named, scopes rewritten as conditions, one-liner separated from claim 1. Every claim, number
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

Stamp: spec=d57862840a90 checks=pass body=d53607f3b5c1
-->
---
one_liner: KnOTS takes a joint SVD over the LoRA updates of separately finetuned models so
  that existing mergers work in one shared basis, and tests the result on a joint-task benchmark
  that asks whether the merge is general.
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
  - knots-10
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
  scope: LoRA-finetuned models merged with TIES or DARE-TIES, where the 4.3% is KnOTS-TIES
    against TIES on the eight-task ViT-B/32 vision benchmark
  evidence: Table 1, Table 2, Table 3, Table 4
- id: knots-2
  kind: result
  text: KnOTS introduces a new benchmark that evaluates the generality of merged models by
    merging models on the union of all inputs and labels across multiple datasets.
  scope: the eight vision datasets pooled into one label space, so the merged model has to
    pick a label across all of them rather than within one
  evidence: Table 4, Figure 3
- id: knots-4
  kind: result
  text: KnOTS scales to larger vision models, improving TIES by 3% when the models being merged
    are eight ViT-L/14 LoRA finetunes rather than ViT-B/32.
  scope: eight ViT-L/14 CLIP models LoRA-finetuned on the same vision datasets as the ViT-B/32
    setting, scored as normalized per-task accuracy
  evidence: Table 2
- id: knots-5
  kind: result
  text: KnOTS-TIES outperforms task arithmetic, TIES and DARE-TIES by up to 2.9% normalized
    accuracy when merging six Llama3-8B models LoRA-finetuned on different NLI datasets.
  scope: normalized against the 92.9% average per-task accuracy of the six individual finetuned
    models, with the merge itself tuned on no held-out data
  evidence: Table 3
- id: knots-6
  kind: result
  text: KnOTS-TIES holds a gap of more than 4% over TIES and task arithmetic once more than
    two tasks are merged, and the gap does not close as the count grows.
  scope: ViT-B/32 models on the eight-task vision benchmark, sweeping the number of merged
    tasks and scoring average normalized accuracy
  evidence: Figure 3
- id: knots-7
  kind: result
  text: KnOTS-TIES outperforms TIES at every LoRA rank tried, from rank 4 up to the full-rank
    768 setting where rank equals the model's feature dimension.
  scope: ViT-B/32 models LoRA-finetuned at ranks 4, 16, 64, 256 and 768, merged on the eight-task
    per-task vision benchmark
  evidence: Figure 4
- id: knots-8
  kind: result
  text: 'Concatenating the task updates column-wise before the SVD is what makes KnOTS work:
    the row-wise variant performs 2.6% worse.'
  scope: ViT-B/32 models on the eight-task vision benchmark, with the concatenation order
    the only thing varied between the two runs
  evidence: Section 5.4.0.3
- id: knots-9
  kind: result
  text: KnOTS-TIES beats task arithmetic, TIES and DARE-TIES at every Hits@k level on the
    joint-task Union evaluation, by up to 3.2% on Hits@1.
  scope: eight ViT-B/32 LoRA models evaluated over the pooled label space of all eight datasets,
    which is the harder of the paper's two evaluations
  evidence: Table 4
- id: knots-10
  kind: context
  text: KnOTS is the reference point for merging LoRA adapters. It showed that different adapters'
    updates sit in different bases, and that one joint SVD is enough to bring them into a
    shared one.
  scope: as of its 2025 publication, and for LoRA adapters specifically rather than the fully
    finetuned models earlier merging work addressed
terminology:
  KnOTS: A method that uses SVD to align task updates from different LoRA models into a shared
    space, enabling effective merging.
supersedes: []
superseded_by: []
---
