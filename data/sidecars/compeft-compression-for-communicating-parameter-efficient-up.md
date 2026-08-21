---
key: yadav2023compeft
coined: ComPEFT
gloss: compressing a fine-tuned adapter's weight update into sparse signs plus one shared
  scalar, with no retraining
one_liner: ComPEFT compresses a PEFT module's fine-tuning residual by keeping only the signs
  of its top-k% largest-magnitude entries and replacing all magnitudes with one tuned multiple
  of the task vector's standard deviation, giving 8x-50x smaller experts with no retraining.
claims:
- id: llama-65b-mmlu
  kind: result
  text: ComPEFT-compressed QLoRA adapters on LLaMA-65B average 63.45% on the MMLU test set,
    against 59.29% for the original QLoRA adapters. The 4.16-point gain comes with 26x smaller
    storage, 1.49 GB down to about 0.058 GB.
  scope: 5-shot MMLU on the QLoRA authors' released checkpoints for 8 instruction-tuning datasets;
    density k and alpha selected on a small held-out MMLU subset; storage assumes Golomb coding.
  evidence: Table 1
- id: scaling-trend
  kind: result
  text: 'The gain from ComPEFT over uncompressed QLoRA grows with base-model size: +0.54 points
    on LLaMA-7B, +1.06 on 13B, +3.44 on 33B and +4.16 on 65B MMLU. Compression factors are
    16x, 20x, 16x and 26x respectively.'
  scope: LLaMA 7B/13B/33B/65B with QLoRA adapters averaged over 8 instruction-tuning datasets,
    5-shot MMLU; alpha and k tuned per configuration on a small held-out MMLU subset.
  evidence: Table 1
- id: config-win-rate
  kind: result
  text: ComPEFT improves on the original QLoRA checkpoint in 28 of 32 dataset-by-model-size
    configurations while compressing the LoRA module 10x-50x in storage.
  scope: 8 instruction-tuning datasets crossed with LLaMA 7B/13B/33B/65B, 5-shot MMLU test;
    the 4 losses sit at 7B and 13B.
  evidence: Table 1
- id: small-models-peft
  kind: result
  text: On T5-Base, T5-Large and T0-3B, ComPEFT compresses (IA)^3 and LoRA modules 12x-25x.
    Average performance over 7 GLUE tasks changes by at most 1.3 points, from -1.3 for (IA)^3
    on T5-Base to +0.1 for LoRA on T5-Large.
  scope: 7 GLUE classification tasks (MNLI, RTE, QNLI, WNLI, SST2, MRPC, QQP), test set; alpha
    and k chosen on a validation set per task.
  evidence: Figure 4
- id: full-finetuning
  kind: result
  text: ComPEFT also compresses full fine-tuning residuals, achieving 12x-19x compression
    on BERT, RoBERTa, T5-v1.1 and T5 with changes from +1.7 points (T5v1.1-Base) to -4.7 points
    (T5-Base) on 7 GLUE tasks.
  scope: Base and Large sizes of 4 architectures, average test performance over 7 GLUE tasks;
    the largest drops are T5-Base (-4.7) and RoBERTa-Base (-2.2).
  evidence: Figure 5
- id: latency
  kind: result
  text: Downloading a ComPEFT-compressed LLaMA-65B QLoRA checkpoint from a simulated internet
    server takes 2.59 s against 83.17 s uncompressed, about 32x faster. CPU-to-GPU loading
    takes 18.60 ms against 475.26 ms, about 25x faster.
  scope: Wall-clock means over 10 repetitions per configuration, LLaMA 7B-65B QLoRA checkpoints
    on a single 48GB A6000 host; ternary-vector compute speedups would need kernels the paper
    does not implement.
  evidence: Figure 6
- id: pareto
  kind: result
  text: ComPEFT applied to (IA)^3 and LoRA is Pareto-optimal in performance versus storage
    against 10 PEFT methods, among them BitFit, Adapters, Compacter, Prompt Tuning, Prefix
    Tuning and Intrinsic SAID. Com(IA)^3 matches methods that use 1000x more storage.
  scope: T0-3B base model, 11 held-out datasets from the T0 evaluation suite, first PromptSource
    template, 200 training examples used as validation per task.
  evidence: Figure 7
- id: merging
  kind: result
  text: Merging ComPEFT-compressed checkpoints beats merging the uncompressed ones in 9 of
    12 settings, and on T0-3B improves merged-model performance by 2.4% on average while being
    about 15x smaller; (IA)^3 on T5 models is the exception.
  scope: Task Arithmetic and TIES-Merging applied to (IA)^3 and LoRA modules for 7 GLUE tasks
    on T5-Base, T5-Large and T0-3B; average test performance of the merged multitask model.
  evidence: Figure 9
- id: compositional
  kind: result
  text: ComPEFT-compressed LoRA experts retain compositional generalization under LoraHub,
    averaging 30.6 exact match across 27 Big-Bench-Hard tasks versus 30.5 for uncompressed
    experts.
  scope: Flan-T5-Large, ~200 LoRA experts, N=20 modules composed per task with the gradient-free
    Shiwa optimizer, 5 seeds; best-seed results favour LoraHub.
  evidence: Table 8
- id: ablation-stc
  kind: result
  text: ComPEFT beats Sparse Ternary Compression and a prune-only ablation at nearly all density
    levels from 3B to 65B base models, and STC falls far below the uncompressed model at 3B
    and 7B. The tuned scalar alpha is what recovers the performance lost to sparsification
    and ternarization.
  scope: Average validation performance versus density k for LoRA modules on T0-3B and LLaMA
    7B/13B/33B/65B; at base sizes of 13B and above all variants match or beat the original
    checkpoint at all densities tested.
  evidence: Figure 10
- id: alpha-tuning
  kind: result
  text: For base models with 13B or more parameters and density k of 20% or less, performance
    varies little with the scaling factor alpha. Setting alpha=1 is recommended rather than
    tuning it.
  scope: Sweeps over k in {5,10,20,30,50} and alpha in {0.5,1,2,3,4,5,6,8,10} on T0-3B and
    LLaMA 7B-65B; at 3B and 7B the optimal alpha shifts with k.
  evidence: Figure 11
- id: baselines-70b
  kind: result
  text: On LLaMA2-70B, ComPEFT averages 67.53% MMLU at 56 MB, above STC (65.24%, 56 MB), BitDelta
    without training (64.73%, 99 MB) and DAREx-q at 95% sparsity (64.68%, 395 MB). It matches
    BitDelta with a trained scale (67.46%), which requires backward passes.
  scope: Rank-64 QLoRA on LLaMA2-70B over 5 instruction-tuning datasets; storage uses Golomb
    coding for ComPEFT and STC, bitmask for BitDelta and COO sparse matrices for DAREx; DAREx
    at 99% sparsity collapses to 45.86%.
  evidence: Table 3
- id: entropy-bound
  kind: result
  text: At 95% sparsity the ternary ComPEFT update has entropy of about 0.34 bits per parameter
    plus a 16-bit scalar, down from 16 bits per parameter for a bfloat16 task vector. Under
    a perfect coding scheme that is a 47x reduction in communication and storage cost.
  scope: Analytical entropy assuming signs of nonzero entries are uniformly distributed; realised
    sizes in the experiments use Golomb coding, and a two-binary-mask alternative costs 2
    bits per parameter but is cheaper to compute with.
  evidence: Section 2.2
- id: context-motivation
  kind: context
  text: ComPEFT frames expert-adapter size as a communication and memory bottleneck for multi-expert
    serving rather than as a training-cost problem. A QLoRA adapter for LLaMA-65B is 3.2 GB
    and must be swapped between disk, CPU and GPU per query.
  scope: Framing stated for multi-expert serving of instruction-tuned LLaMA models in 2023;
    the paper measures storage and transfer, not end-to-end serving throughput under real
    query mixes.
  evidence: Section 1
- id: context-position
  kind: context
  text: ComPEFT adapts the sparsification-plus-ternary-quantization idea from federated-learning
    gradient compression (STC, TernGrad) to post-hoc compression of fine-tuning task vectors,
    removing the retraining that pruning methods usually need to recover accuracy.
  scope: Compression of the residual between a released fine-tuned checkpoint and its initialization;
    assumes access to both, and to a small validation set for choosing the single scaling
    hyperparameter alpha.
  evidence: Section 5
qa:
- ask:
    plain: how much smaller can a fine-tuned adapter file be made before its accuracy drops?
    jargon: how far can a LoRA or QLoRA task vector be sparsified and ternarized without accuracy
      loss?
    task: how do I shrink a QLoRA adapter checkpoint for storage without retraining it?
    practitioner: can I compress the LoRA adapters I already trained and still trust their
      scores?
  answered_by:
  - llama-65b-mmlu
  - small-models-peft
  - entropy-bound
- ask:
    plain: can throwing away most of an adapter's weights ever make the model score higher?
    jargon: why does sparsifying and ternarizing a fine-tuning task vector sometimes exceed
      the dense checkpoint on MMLU?
    task: how do I tell whether compressing my QLoRA checkpoint costs accuracy or gains it?
    practitioner: if I compress my fine-tuned expert, should I expect to lose accuracy?
  answered_by:
  - config-win-rate
  - scaling-trend
  - baselines-70b
- ask:
    plain: does shrinking adapters work better for bigger language models?
    jargon: does the accuracy gain from ternary task-vector compression scale with base-model
      parameter count from 7B to 65B?
    task: how do I predict the accuracy effect of adapter compression at 33B or 65B rather
      than 7B?
    practitioner: my base model is 65B rather than 7B, is adapter compression a better deal
      for me?
  answered_by:
  - scaling-trend
  - llama-65b-mmlu
- ask:
    plain: how much time does a smaller adapter file save when downloading and loading it?
    jargon: what wall-clock savings does a compressed QLoRA checkpoint give on network transfer
      and CPU-to-GPU load?
    task: how do I cut the swap-in latency of per-query expert modules in a multi-expert server?
    practitioner: is compressing my expert adapters worth it for serving latency, not just
      disk space?
  answered_by:
  - latency
- ask:
    plain: can the weight changes from ordinary full fine-tuning be shrunk the same way as
      small adapters?
    jargon: does sign-plus-scalar compression of task vectors transfer from PEFT modules to
      full fine-tuning residuals on BERT, RoBERTa and T5?
    task: how do I compress a fully fine-tuned checkpoint rather than a LoRA module?
    practitioner: I fully fine-tuned my model instead of using LoRA, can I still compress
      the difference from the base weights?
  answered_by:
  - full-finetuning
- ask:
    plain: if several fine-tuned models are shrunk first, does combining them into one model
      still work?
    jargon: how does compressing task vectors before merging affect merged-model performance
      with task arithmetic and TIES-Merging?
    task: how do I combine several fine-tuned experts into one model while keeping each checkpoint
      small?
    practitioner: should I compress my checkpoints before or after merging them?
  answered_by:
  - merging
- ask:
    plain: can shrunken adapters still be mixed on the fly to handle a task none of them was
      trained on?
    jargon: is compositional generalization of LoRA experts under LoraHub preserved after
      sparsification and ternarization?
    task: how do I keep few-shot composition over a library of LoRA experts working once the
      experts are compressed?
    practitioner: I compose LoRA experts for unseen tasks, will compressing the library break
      that?
  answered_by:
  - compositional
- ask:
    plain: how does shrinking a fine-tuned model's weight changes compare with other ways
      of storing model deltas?
    jargon: how does post-hoc ternary task-vector compression compare with BitDelta and DAREx-q
      on LLaMA2-70B MMLU at matched storage?
    task: how do I pick a delta-compression method that needs no extra backward passes?
    practitioner: BitDelta needs a trained scale factor, is there a method I can apply without
      any training?
  answered_by:
  - baselines-70b
  - ablation-stc
- ask:
    plain: 'when shrinking a fine-tuned adapter, which step matters most: dropping the small
      weights, rounding the rest to plus or minus one, or rescaling them?'
    jargon: how much of the performance recovery after sparsification and ternarization comes
      from the tuned scalar rather than from the ternary quantization itself?
    task: how do I stop a sparse ternary compression of my task vector from losing accuracy?
    practitioner: if I just prune and ternarize my adapter myself, what am I missing?
  answered_by:
  - ablation-stc
- ask:
    plain: how carefully do I need to pick the number that rescales a compressed adapter?
    jargon: how sensitive is compressed task-vector performance to the scaling factor alpha
      across densities and base-model sizes?
    task: how do I choose the rescaling factor when compressing a 65B model's adapter?
    practitioner: do I have to tune the scaling factor for my compressed adapter, or can I
      just leave it at 1?
  answered_by:
  - alpha-tuning
- ask:
    plain: which way of cheaply adapting a large model gives the best accuracy for the least
      stored data?
    jargon: is compressed (IA)^3 Pareto-optimal in performance versus parameter storage against
      BitFit, Compacter, Prompt Tuning and Prefix Tuning?
    task: how do I choose a parameter-efficient fine-tuning setup when storage per task is
      the binding constraint?
    practitioner: I need hundreds of task-specific modules on disk, which fine-tuning method
      should I store them in?
  answered_by:
  - pareto
- ask:
    plain: what should I read first about making fine-tuned expert modules small enough to
      serve many of them?
    jargon: which work reframes PEFT module size as a communication and memory bottleneck
      for multi-expert serving?
    task: where do I start reading about post-hoc compression of fine-tuning task vectors?
    practitioner: I am building a multi-expert serving stack, which paper frames the adapter-size
      problem the way I have it?
  answered_by:
  - context-motivation
  - context-position
- ask:
    plain: how few bits per weight does a compressed fine-tuning update actually need?
    jargon: what is the per-parameter entropy of a 95%-sparse ternary task vector against
      a bfloat16 one?
    task: how do I work out the best-case storage for a sparse ternary fine-tuning update
      before implementing the encoding?
    practitioner: what compression factor should I expect from ternary adapter updates if
      I write an ideal encoder?
  answered_by:
  - entropy-bound
misreadings:
- ''
terminology:
  task vector: The difference between a fine-tuned model's parameters and the initialization
    they were fine-tuned from, treated as the object to be stored and communicated.
  density (k): The fraction of task-vector entries whose signs are kept after sparsification;
    the remaining 1-k fraction is set to zero, so sparsity equals 1-k.
  ternary quantization: Replacing every retained entry of a task vector by its sign in {-1,
    0, +1} and one shared 16-bit scalar, so no per-parameter magnitudes are stored.
  Com(IA)^3 / ComLoRA: The names for (IA)^3 and LoRA modules after ComPEFT compression, treated
    as PEFT methods in their own right on the storage-versus-performance frontier.
  alpha: The single tuned hyperparameter of ComPEFT, a multiplier on the original task vector's
    standard deviation that sets the magnitude of every retained ternary entry.
---
