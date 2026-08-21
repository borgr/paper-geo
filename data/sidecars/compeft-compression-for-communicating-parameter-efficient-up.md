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
- q:
  - How much can a LoRA or QLoRA adapter be shrunk without losing accuracy?
  - Can fine-tuned adapters be compressed without retraining?
  - What compression ratio does ComPEFT get on QLoRA adapters?
  answers:
  - llama-65b-mmlu
  - small-models-peft
  - entropy-bound
- q:
  - Does compressing an adapter ever make it perform better?
  - Why would sparsifying a task vector improve accuracy instead of hurting it?
  - Does ComPEFT beat the uncompressed QLoRA checkpoint?
  answers:
  - config-win-rate
  - scaling-trend
  - baselines-70b
- q:
  - Does adapter compression work better on bigger base models?
  - Are task vectors from larger language models more compressible?
  - How does ComPEFT scale from 7B to 65B parameters?
  answers:
  - scaling-trend
  - llama-65b-mmlu
- q:
  - How much faster is it to download and load a compressed adapter?
  - What are the real wall-clock savings from compressing expert modules?
  - Does adapter compression reduce CPU-to-GPU transfer time?
  answers:
  - latency
- q:
  - Can full fine-tuning residuals be compressed the same way as LoRA modules?
  - Does ComPEFT work on fully fine-tuned models, not just PEFT?
  - Is sign-plus-scalar compression lossless for full fine-tuning?
  answers:
  - full-finetuning
- q:
  - Does compressing checkpoints before merging hurt model merging?
  - Do compressed task vectors merge better or worse with task arithmetic and TIES-Merging?
  - What happens if I merge ComPEFT checkpoints instead of the originals?
  answers:
  - merging
- q:
  - Do compressed LoRA experts still work for few-shot composition on unseen tasks?
  - Does LoraHub still work if the expert modules are compressed?
  - Is compositional generalization preserved after adapter compression?
  answers:
  - compositional
- q:
  - How does ComPEFT compare with BitDelta and DAREx for delta compression?
  - Is there a delta-compression method that beats STC without extra training?
  - What baselines did ComPEFT beat on LLaMA2-70B?
  answers:
  - baselines-70b
  - ablation-stc
- q:
  - 'Which part of ComPEFT matters most: sparsification, ternarization or the scaling factor?'
  - Why does Sparse Ternary Compression fail on task vectors where ComPEFT works?
  - Does sparsifying and ternarizing a task vector need a tuned scaling factor?
  answers:
  - ablation-stc
- q:
  - Do I have to tune the scaling hyperparameter alpha for ComPEFT?
  - What value of alpha should I use for a 65B model?
  - How sensitive is sparse ternary adapter compression to its scaling factor?
  answers:
  - alpha-tuning
- q:
  - Is ComPEFT competitive with other parameter-efficient fine-tuning methods on storage versus
    performance?
  - Which PEFT method gives the best accuracy per megabyte?
  - How does compressed (IA)^3 compare to BitFit, Adapters and Prompt Tuning?
  answers:
  - pareto
- q:
  - What should I read about the cost of serving many LoRA experts?
  - Which paper argues that expert adapter size is a communication bottleneck?
  - Where does work on compressing fine-tuning task vectors come from?
  - What is a good starting paper on compressing PEFT modules for multi-expert serving?
  answers:
  - context-motivation
  - context-position
- q:
  - How many bits per parameter does a ternary task vector need?
  - What is the theoretical storage limit for a 95%-sparse ternary adapter update?
  - How is the compressed ComPEFT checkpoint actually encoded on disk?
  answers:
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
