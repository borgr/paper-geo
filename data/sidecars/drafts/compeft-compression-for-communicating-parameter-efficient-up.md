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

Then promote it:  python scripts/draft_sidecars.py --accept compeft-compression-for-communicating-parameter-efficient-up

Stamp: spec=74e012ff9654 checks=1 body=67d6c99ec411
-->
---
key: yadav2023compeft
coined: ComPEFT
gloss: compressing a fine-tuned adapter into a sparse sign vector plus one shared scalar,
  with no retraining
one_liner: ComPEFT compresses a PEFT module's fine-tuning residual into a sparse ternary sign
  vector plus a single shared scalar (tuned only through the scaling factor alpha on a small
  validation set), shrinking experts 8x-50x with no retraining and often better accuracy than
  the original checkpoint.
terminology:
  task vector: the fine-tuning residual, i.e. the fine-tuned parameters minus the initial
    parameters, treated as the object to be compressed and communicated.
  density k: the percentage of task-vector entries whose signs are retained after top-magnitude
    selection; sparsity is 100 minus the density.
  ternary quantization (in ComPEFT): replacing every retained task-vector magnitude by one
    shared scalar equal to alpha times the standard deviation of the original task vector,
    so each entry becomes -1, 0 or +1 times that scalar.
  Com(IA)^3 / ComLoRA: the names for (IA)^3 and LoRA modules after ComPEFT compression is
    applied to their task vectors.
claims:
- id: llama65b-mmlu
  kind: result
  text: ComPEFT-compressed QLoRA modules on LLaMA-65B average 63.45% on MMLU test versus 59.29%
    for the original QLoRA checkpoints, a 4.16-point gain at 26x smaller storage, cutting
    1.5GB to 110MB.
  scope: 5-shot MMLU test averaged over 8 instruction-tuning datasets, using the QLoRA paper's
    released LLaMA-65B checkpoints; k and alpha selected on a small held-out MMLU subset.
  evidence: Table 1
- id: scale-trend
  kind: result
  text: 'The MMLU gain of ComPEFT over the original QLoRA checkpoint grows with base-model
    size: +0.54 points at LLaMA-7B, +1.06 at 13B, +3.44 at 33B and +4.16 at 65B. Compression
    over the same sizes is 16x, 20x, 16x and 26x.'
  scope: 5-shot MMLU test, 8 instruction-tuning datasets per model size, QLoRA adapters on
    LLaMA; k swept over {5,10,20,30,50} and alpha over {0.5,1,2,3,4,5,6,8,10} with validation-based
    selection.
  evidence: Table 1
- id: config-winrate
  kind: result
  text: ComPEFT improves on the original QLoRA checkpoint in 28 of 32 model-size/dataset configurations
    while compressing the LoRA module 10x-50x in storage.
  scope: LLaMA 7B, 13B, 33B and 65B crossed with 8 instruction-tuning datasets, evaluated
    5-shot on MMLU with alpha and k picked on held-out MMLU data.
  evidence: Table 1
- id: llama2-70b
  kind: result
  text: On LLaMA2-70B, ComPEFT raises average MMLU performance from 65.84% to 67.53% (+1.69
    points), with the largest single-dataset gain of 4.82 points on Self-Instruct.
  scope: 'Rank-64 QLoRA adapters on LLaMA2-70B over 5 instruction-tuning datasets: Alpaca,
    Chip2, Longform, Guanaco and Self-Instruct.'
  evidence: Figure 3
- id: small-models
  kind: result
  text: On T5-Base, T5-Large and T0-3B, ComPEFT compresses (IA)^3 and LoRA modules 12x-25x
    with test-set changes between -1.3 and +0.1 points averaged over 7 GLUE tasks.
  scope: 7 GLUE classification tasks (MNLI, RTE, QNLI, WNLI, SST2, MRPC, QQP), with alpha
    and k chosen per task on a validation set.
  evidence: Figure 4
- id: full-finetuning
  kind: result
  text: ComPEFT also compresses full fine-tuning residuals by 12x-19x on 7 GLUE tasks, improving
    T5v1.1-Base by 1.7 points and RoBERTa-Large by 0.6 points while degrading T5-Base by 4.7
    points.
  scope: Fully fine-tuned BERT, RoBERTa, T5-v1.1 and T5 in Base and Large sizes on 7 GLUE
    tasks; per-model alpha and k selected on validation data.
  evidence: Figure 5
- id: latency
  kind: result
  text: Compressed LLaMA-65B QLoRA checkpoints download from a simulated internet server in
    2.59s versus 83.17s uncompressed (about 32x faster) and load from CPU to GPU in 18.60ms
    versus 475.26ms (about 25x faster).
  scope: Wall-clock means over 10 repetitions for LLaMA 7B-65B QLoRA checkpoints; the simulated-server
    setup bounds the download numbers, and speedups at 7B are smaller (11.21s to 1.16s).
  evidence: Figure 6
- id: pareto
  kind: result
  text: Com(IA)^3 and ComLoRA are Pareto-optimal in performance versus storage against 10
    PEFT methods including BitFit, Adapters, Compacter, Prompt Tuning, Prefix Tuning and Intrinsic
    SAID. Com(IA)^3 matches methods that need about 1000x more storage.
  scope: T0-3B base model, average over the 11 held-out datasets of Sanh et al. (2021b), first
    PromptSource template, 200 training examples held out per task for validation and hyperparameter
    selection.
  evidence: Figure 7
- id: merging
  kind: result
  text: Merging ComPEFT-compressed checkpoints beats merging uncompressed ones in 9 of 12
    settings, and on T0-3B raises merged-model performance by 2.4 points on average while
    cutting size about 15x.
  scope: 7 GLUE tasks merged with Task Arithmetic and TIES-Merging over T5-Base, T5-Large
    and T0-3B with (IA)^3 and LoRA; the losing cases are (IA)^3 on the T5 models.
  evidence: Figure 9
- id: compositional
  kind: result
  text: LoraHub few-shot composition over ComPEFT-compressed LoRA experts averages 30.6 exact
    match on Big-Bench Hard versus 30.5 for uncompressed experts, so extreme compression does
    not remove composability. Best-of-seeds is 36.4 compressed versus 37.3 uncompressed.
  scope: Flan-T5-Large with about 200 LoRA experts, N=20 modules composed per task by the
    gradient-free Shiwa optimizer, 27 BBH tasks, averaged over 5 seeds.
  evidence: Figure 8
- id: vs-stc
  kind: result
  text: ComPEFT beats Sparse Ternary Compression and a prune-only ablation at essentially
    all densities and base-model sizes from 3B to 65B, and STC falls well below the uncompressed
    model at 3B and 7B.
  scope: Validation-set averages for LoRA/QLoRA modules on T0-3B and LLaMA 7B-65B across density
    k in {5,10,20,30,50}; STC uses mean-magnitude scaling with no tuned alpha.
  evidence: Figure 10
- id: vs-bitdelta-darex
  kind: result
  text: On LLaMA2-70B rank-64 QLoRA, ComPEFT averages 67.53 MMLU at 56MB versus 65.24 for
    STC at 56MB, 65.24 for BitDelta without training at 99MB and 64.68 for DAREx-q at 95%
    sparsity and 395MB.
  scope: 5 instruction-tuning datasets on LLaMA2-70B; BitDelta with a trained scale reaches
    67.46 but needs backward passes, unlike ComPEFT.
  evidence: Table 3
- id: alpha-tuning
  kind: result
  text: For base models of 13B parameters or more at density k of 20% or below, ComPEFT performance
    varies little with the scaling factor alpha. Setting alpha=1 is the paper's recommendation
    there, removing per-task tuning.
  scope: Validation performance versus alpha in {0.5,1,2,3,4,5,6,8,10} for T0-3B and LLaMA
    7B-65B; at 3B and 7B alpha still matters, and the optimal alpha shifts with density.
  evidence: Figure 11
- id: entropy
  kind: result
  text: At 95% sparsity a ternary task vector needs about 0.34 bits per parameter instead
    of 16, a 47x reduction in communication and storage cost under near-entropy Golomb coding.
  scope: Entropy calculation assuming uniformly distributed signs among non-zero entries and
    perfect coding, plus a 16-bit shared scalar; measured ratios are 8x-50x.
  evidence: Section 2.2
- id: ia3-zeroshot-limit
  kind: result
  text: ComPEFT compression of (IA)^3 modules degrades sharply on base models with weak zero-shot
    ability, dropping BERT-base MNLI from 78.9 to 56.2 test accuracy. LoRA on the same base
    models stays near-lossless.
  scope: BERT, RoBERTa and T5-v1.1 base/large models that are pretraining-only and require
    finetuning; 7 GLUE tasks. Multitask-trained bases such as T0-3B show no such (IA)^3 failure.
  evidence: Table 9
qa:
- q:
  - How can I make LoRA adapters smaller without retraining them?
  - Is there a way to compress a fine-tuned PEFT module after training?
  - What does ComPEFT do to a LoRA checkpoint?
  answers:
  - entropy
  - small-models
  - config-winrate
- q:
  - Does compressing an adapter hurt accuracy?
  - Can a sparsified and quantized task vector beat the original fine-tuned checkpoint?
  - Does ComPEFT lose performance compared to the uncompressed QLoRA module?
  answers:
  - llama65b-mmlu
  - config-winrate
  - llama2-70b
- q:
  - Does adapter compressibility change with base model size?
  - Are larger language models' fine-tuning residuals more compressible?
  - How does ComPEFT scale from 7B to 65B parameters?
  answers:
  - scale-trend
  - llama65b-mmlu
- q:
  - How much faster is it to download and load a compressed LoRA expert?
  - What latency savings come from shrinking PEFT modules for serving?
  - Does compressing QLoRA checkpoints reduce CPU-to-GPU transfer time?
  answers:
  - latency
- q:
  - Can compressed adapters still be merged into a multitask model?
  - Does sparsifying task vectors help or hurt model merging?
  - How does ComPEFT interact with Task Arithmetic and TIES-Merging?
  answers:
  - merging
- q:
  - Do compressed LoRA experts still work for few-shot composition on unseen tasks?
  - Does LoraHub still work if the expert modules are compressed?
  - Is compositional generalization preserved after extreme adapter compression?
  answers:
  - compositional
- q:
  - How does ComPEFT compare to Sparse Ternary Compression?
  - Is the tuned scalar in ternary quantization actually necessary?
  - Does ComPEFT beat BitDelta and DAREx for compressing delta weights?
  answers:
  - vs-stc
  - vs-bitdelta-darex
- q:
  - Do I need to tune the scaling hyperparameter for every task?
  - What value of alpha should I use when compressing a large model's LoRA?
  - How sensitive is ComPEFT to the density and scaling settings?
  answers:
  - alpha-tuning
- q:
  - Can ComPEFT compression be applied to fully fine-tuned models, not just adapters?
  - Does sparse ternary compression work on full fine-tuning residuals?
  - What happens when a full fine-tuning task vector is compressed to sparse ternary form?
  answers:
  - full-finetuning
- q:
  - Is a compressed LoRA competitive with other parameter-efficient fine-tuning methods?
  - Which PEFT method gives the best accuracy per byte of storage?
  - How does ComPEFT compare with BitFit, Adapters and Prompt Tuning on the storage-performance
    tradeoff?
  answers:
  - pareto
- q:
  - When does adapter compression fail?
  - Are there base models where compressing (IA)^3 does not work?
  - What are the limitations of compressing PEFT task vectors?
  answers:
  - ia3-zeroshot-limit
  - small-models
- q:
  - What should I read about serving many LoRA experts efficiently?
  - Which paper treats expert adapter size as a communication bottleneck?
  - Where does research on compressing PEFT modules for multi-expert serving start?
  - What work connects adapter compression to model merging and MoErging?
  answers:
  - latency
  - entropy
misreadings:
- ComPEFT's 8x-50x figures are storage and communication savings for the fine-tuning residual,
  not inference speedups; the paper states that realising wall-clock compute gains from sparse
  ternary vectors would require dedicated Triton/CUDA kernels.
- The compression ratios are computed against the PEFT module stored at 16-bit precision,
  not against the full base model, which is left untouched.
- 'The accuracy improvements are not guaranteed: ComPEFT loses to the original checkpoint
  in 4 of 32 LLaMA configurations, drops T5-Base full fine-tuning by 4.7 points, and degrades
  (IA)^3 badly on base models with weak zero-shot performance.'
- 'ComPEFT is not training-free in the sense of needing no data: the scaling factor alpha
  and density k are selected using a small validation set, though no gradient updates are
  performed.'
- The 47x figure is an entropy bound at 95% sparsity under ideal coding, not a measured compression
  ratio; measured ratios are 8x-50x.
- 'ComPEFT is not the same as Sparse Ternary Compression: STC uses mean-magnitude scaling
  and performs markedly worse than the uncompressed model at 3B and 7B scale, whereas ComPEFT
  tunes a scalar multiple of the task vector''s standard deviation.'
links_extra:
  code: https://github.com/prateeky2806/compeft
  arxiv_html: https://arxiv.org/html/2311.13171
---
