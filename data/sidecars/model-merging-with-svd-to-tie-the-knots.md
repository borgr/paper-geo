---
one_liner: KnOTS takes a joint SVD over the LoRA updates of separately finetuned models so
  that existing mergers work in one shared basis, and tests the result on a joint-task benchmark
  that asks whether the merge is general.
qa:
- ask:
    plain: why do separately fine-tuned adapters get worse when you average them together,
      and what fixes it?
    jargon: how does a joint SVD of LoRA task updates improve multi-task merging accuracy
      over merging in each adapter's own basis?
    task: how do I combine several LoRA adapters into one model so the combined model keeps
      their accuracy?
    practitioner: I have several LoRA fine-tunes of the same base model — will aligning their
      updates before merging actually buy me accuracy?
  answered_by:
  - knots-1
- ask:
    plain: how do you test whether a single merged model is any good when you do not know
      which task an input came from?
    jargon: what evaluation setting measures merged-model generality over the union of label
      spaces from all constituent datasets?
    task: how do I evaluate a merged multi-task model without telling it which dataset each
      test input belongs to?
    practitioner: should I be benchmarking my merged checkpoint on each dataset separately,
      or on all of the labels at once?
  answered_by:
  - knots-2
- ask:
    plain: what did the KnOTS work establish about combining low-rank fine-tunes of one base
      model?
    jargon: what is the KnOTS contribution to LoRA merging, and what did it show about the
      bases of different adapters' updates?
    practitioner: if I only read one thing before merging LoRA adapters, what does KnOTS tell
      me that I need to know?
  answered_by:
  - knots-10
- ask:
    plain: does the trick for merging low-rank fine-tunes still help when the vision backbone
      gets bigger?
    jargon: how does KnOTS-TIES scale from ViT-B/32 to ViT-L/14 LoRA finetunes on 8-task merging?
    task: how do I merge eight LoRA-finetuned vision transformers when the backbone is a large
      CLIP model?
    practitioner: I am merging adapters on a large ViT rather than a small one — will the
      gain hold at that scale?
  answered_by:
  - knots-4
- ask:
    plain: does aligning adapter updates before merging work on large language models, not
      just image models?
    jargon: how does KnOTS-TIES compare with task arithmetic, TIES and DARE-TIES when merging
      Llama3-8B LoRA finetunes on NLI datasets?
    task: how do I merge several 8B-parameter LoRA fine-tunes trained on different natural
      language inference datasets?
    practitioner: I have six LoRA fine-tunes of Llama3-8B on different NLI data — which merging
      method should I pick?
  answered_by:
  - knots-5
- ask:
    plain: does merging more fine-tuned models at once wipe out the advantage of aligning
      their updates first?
    jargon: how does the KnOTS-TIES margin over TIES and task arithmetic behave as the number
      of merged tasks increases?
    task: how many LoRA adapters can I merge into one model before the alignment step stops
      paying off?
    practitioner: I want one model covering many tasks, not two or three — does the gap hold
      as I add more adapters?
  answered_by:
  - knots-6
- ask:
    plain: does the rank you fine-tuned at change whether aligning updates before merging
      helps?
    jargon: is the KnOTS-TIES advantage over TIES stable across LoRA ranks from 4 up to the
      full feature dimension?
    task: how do I choose a LoRA rank for adapters I plan to merge later?
    practitioner: my adapters were trained at a low rank — do I need to retrain at higher
      rank to get the merging benefit?
  answered_by:
  - knots-7
- ask:
    plain: when you stack the weight changes from several fine-tunes before factorizing them,
      does the direction you stack them in matter?
    jargon: why does column-wise concatenation of LoRA task updates before the SVD outperform
      the row-wise variant in KnOTS?
    task: which way should I concatenate task updates before running an SVD to align them
      for merging?
  answered_by:
  - knots-8
- ask:
    plain: can one merged model handle inputs from all of its source tasks at once without
      being told which task an input came from?
    jargon: how does KnOTS-TIES compare with task arithmetic, TIES and DARE-TIES on Hits@k
      in the joint-task Union evaluation?
    task: how do I get a single merged model that answers correctly across the combined label
      space of all its source datasets?
    practitioner: I need one adapter-merged model serving mixed traffic from several tasks
      — which merging method holds up there?
  answered_by:
  - knots-9
- ask:
    plain: what should I read first about combining low-rank fine-tunes of a shared base model?
    jargon: which paper is the standard reference for SVD-based alignment of LoRA task updates
      prior to merging?
    task: where do I start reading if I need to merge LoRA adapters rather than full fine-tunes?
    practitioner: my team is about to merge LoRA adapters — which paper should I hand them?
  answered_by:
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
