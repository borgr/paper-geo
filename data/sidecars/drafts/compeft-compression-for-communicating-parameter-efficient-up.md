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

Stamp: spec=e47adcd7257c checks=2 body=587f58b58fb3
-->
---
key: yadav2023compeft
coined: ComPEFT
gloss: compressing a LoRA or (IA)^3 adapter into a sparse ternary sign vector plus one scalar,
  with no retraining
one_liner: ComPEFT compresses a PEFT module's fine-tuning residual into a sparse ternary sign
  vector plus a single tuned scalar (alpha times the task vector's standard deviation), giving
  8x-50x smaller experts with no retraining and often better accuracy than the original checkpoint.
claims:
- id: llama-mmlu-scale
  kind: result
  text: ComPEFT-compressed QLoRA adapters raise 5-shot MMLU test accuracy over the original
    QLoRA checkpoints by 0.54% on LLaMA-7B, 1.06% on 13B, 3.44% on 33B and 4.16% on 65B. Storage
    shrinks 16x, 20x, 16x and 26x respectively.
  evidence: Table 1
  scope: 8 instruction-tuning datasets using QLoRA checkpoints released by the QLoRA authors;
    alpha and density k tuned on a small held-out MMLU subset; storage assumes Golomb coding
    against 16-bit adapters.
- id: wins-28-of-32
  kind: result
  text: ComPEFT improves on the original QLoRA checkpoint in 28 of 32 model-size/dataset configurations
    on MMLU, with compression of 10x-50x in storage cost.
  evidence: Table 1
  scope: LLaMA 7B/13B/33B/65B crossed with 8 instruction-tuning datasets; the 4 losses fall
    at 7B and 13B; alpha and k selected on a held-out MMLU subset.
- id: 65b-size
  kind: result
  text: On LLaMA-65B, ComPEFT reduces the average QLoRA adapter from 1.49 GB to about 58 MB
    while improving average MMLU test accuracy from 59.29% to 63.45%.
  evidence: Table 1
  scope: Averages over 8 instruction-tuning datasets; sizes from the sparse ternary entropy
    with Golomb coding, versus 16-bit uncompressed adapters.
- id: llama2-70b
  kind: result
  text: On LLaMA2-70B QLoRA adapters, ComPEFT improves average MMLU accuracy by 1.69% (65.84%
    to 67.53%), including a 4.82% gain on Self-Instruct.
  evidence: Figure 3
  scope: 5 instruction-tuning datasets with rank-64 QLoRA; per-dataset gains range from +0.43%
    on Alpaca to +4.82% on Self-Instruct.
- id: small-models-peft
  kind: result
  text: On 7 GLUE tasks, ComPEFT compresses (IA)^3 and LoRA modules by 12x-25x with at most
    1.3 points of average test-set loss. LoRA on T5-Large gains 0.1 points and LoRA on T0-3B
    is unchanged.
  evidence: Figure 4
  scope: T5-Base, T5-Large and T0-3B base models on MNLI, RTE, QNLI, WNLI, SST2, MRPC and
    QQP; largest drop is (IA)^3 on T5-Base at -1.3 points. Alpha and k chosen on a validation
    set of the same tasks.
- id: full-finetuning
  kind: result
  text: ComPEFT also compresses fully fine-tuned residuals by 12x-19x on 7 GLUE tasks, improving
    average test accuracy by 1.7 points on T5v1.1-Base and 0.6 points on RoBERTa-Large, while
    losing 4.7 points on T5-Base.
  evidence: Figure 5
  scope: BERT, RoBERTa, T5-v1.1 and T5 at Base and Large sizes; 7 GLUE classification tasks;
    results are averages over tasks, and per-model outcomes range from +1.7 to -4.7 points.
- id: latency
  kind: result
  text: ComPEFT checkpoints download about 32x faster and load from CPU to GPU about 25x faster
    for LLaMA-65B. Download falls from 83.17 s to 2.59 s and CPU-to-GPU transfer from 475.26
    ms to 18.60 ms.
  evidence: Figure 6
  scope: Wall-clock means over 10 repetitions for LLaMA 7B-65B QLoRA adapters, with a simulated
    internet server for the download scenario; transmission and loading only, not inference
    compute.
- id: pareto
  kind: result
  text: ComPEFT applied to (IA)^3 and LoRA is Pareto-optimal in performance versus storage
    size against 10 PEFT methods including BitFit, Adapters, Compacter, Prompt Tuning, Prefix
    Tuning and Intrinsic SAID. Com(IA)^3 matches methods needing 1000x more storage.
  evidence: Figure 7
  scope: T0-3B averaged over the 11 held-out datasets of Sanh et al., first PromptSource template,
    200 validation examples per task; full fine-tuning still attains slightly higher peak
    accuracy.
- id: merging
  kind: result
  text: Merging ComPEFT-compressed checkpoints beats merging the uncompressed ones in 9 of
    12 settings, and on T0-3B improves merged-model accuracy by 2.4% on average while being
    about 15x smaller.
  evidence: Figure 9
  scope: 7 GLUE tasks merged with Task Arithmetic and TIES-Merging on T5-Base, T5-Large and
    T0-3B with (IA)^3 and LoRA; the exceptions are (IA)^3 on the T5 models.
- id: compositional
  kind: result
  text: ComPEFT-compressed LoRA experts retain few-shot compositional generalization under
    LoraHub, averaging 30.6 exact match on 27 Big-Bench Hard tasks versus 30.5 for uncompressed
    LoraHub.
  evidence: Figure 8
  scope: Flan-T5-Large with ~200 LoRA experts, N=20 composed per unseen task by the gradient-free
    Shiwa optimizer, over 5 seeds; best-of-run is 36.4 versus 37.3 uncompressed.
- id: ablation-stc
  kind: result
  text: ComPEFT beats Sparse Ternary Compression and a prune-only ablation at nearly all density
    levels, and unlike STC stays at or above the uncompressed LoRA checkpoint's accuracy on
    3B and 7B base models.
  evidence: Figure 10
  scope: Validation performance versus density k for LoRA on T0-3B and LLaMA 7B/13B/33B/65B;
    at 13B and above all variants, STC included, match or beat the original.
- id: alpha-tuning
  kind: result
  text: Tuning the scaling factor alpha becomes unnecessary at scale for ComPEFT. For base
    models of 13B parameters or more at density k of 20% or less, performance varies little
    with alpha and alpha = 1 is recommended.
  evidence: Figure 11
  scope: Sweeps of k in {5,10,20,30,50} and alpha in {0.5,1,2,3,4,5,6,8,10} on T0-3B and LLaMA
    7B-65B; 3B and 7B models still need alpha tuned, with optimal alpha 5-8 at k=5 versus
    2-3 at k=50 on T0-3B.
- id: baselines-70b
  kind: result
  text: On LLaMA2-70B, ComPEFT reaches 67.53 average MMLU at 56 MB, against 65.24 for STC
    at 56 MB and 64.73 for BitDelta without training at 99 MB. DAREx-qv reaches 64.68 at 95%
    sparsity and 45.86 at 99% sparsity.
  evidence: Table 3
  scope: Rank-64 QLoRA on LLaMA2-70B over 5 instruction-tuning datasets; BitDelta with a learned
    scale reaches 67.46 at 99 MB but needs backward passes, so it is not training-free.
- id: entropy
  kind: result
  text: At 95% sparsity ComPEFT's sparse ternary representation reduces the update from 16
    bits per parameter to about 0.34 bits per parameter. That is a 47x reduction in storage
    and communication cost.
  evidence: Section 2.2
  scope: Entropy bound at density k=0.05 assuming uniformly distributed signs on nonzero entries,
    plus a 16-bit scalar; the two-binary-mask alternative instead costs 2 bits per parameter.
- id: context-redundancy
  kind: context
  text: ComPEFT establishes that parameter-efficient fine-tuning modules are themselves highly
    redundant, and frames adapter size as a communication and serving bottleneck for systems
    that dynamically retrieve, swap, merge or route among many experts.
  scope: Argued for LoRA, QLoRA, DoRA and (IA)^3 residuals on T5, T0 and LLaMA-family models
    from 200M to 70B parameters as of the 2025 TMLR version; assumes access to both the initial
    and fine-tuned parameters.
- id: context-training-free
  kind: context
  text: ComPEFT is a training-free compression method for fine-tuning residuals. Only a small
    validation set is needed to pick the scaling factor alpha and density k, rather than the
    retraining that pruning pipelines typically need.
  scope: Contrasts with STC from federated learning and BitDelta's trained-scale variant;
    no custom sparse-ternary kernels are provided, so wall-clock inference speedups are not
    demonstrated.
qa:
- q:
  - How much can a LoRA adapter be compressed without losing accuracy?
  - Can you shrink QLoRA adapters and keep MMLU performance?
  - What compression ratio does ComPEFT get on LLaMA QLoRA modules?
  answers:
  - llama-mmlu-scale
  - 65b-size
  - wins-28-of-32
- q:
  - Does compressing an adapter ever help accuracy rather than hurt it?
  - Why does adapter compression improve performance for bigger base models?
  - Is adapter compressibility related to base model scale?
  answers:
  - llama-mmlu-scale
  - llama2-70b
  - ablation-stc
- q:
  - What should I read about the redundancy of parameter-efficient fine-tuning modules?
  - Where should I start reading about the storage and communication cost of serving many
    LoRA experts?
  - Which paper argues that PEFT adapters are still too big for multi-expert serving?
  answers:
  - context-redundancy
  - context-training-free
- q:
  - Does compressing adapters require retraining or fine-tuning afterwards?
  - Is there a compression method for fine-tuning residuals that needs no extra training?
  - How is the ComPEFT scaling factor chosen without retraining?
  answers:
  - context-training-free
  - alpha-tuning
- q:
  - How much faster is it to download and load a compressed adapter?
  - What latency savings come from shrinking a QLoRA expert module?
  - Does adapter compression reduce CPU-to-GPU transfer time?
  answers:
  - latency
- q:
  - Does ComPEFT work on small models like T5-Base, or only on very large ones?
  - How well does compression work for (IA)^3 and LoRA on GLUE tasks?
  - Is there a performance loss when compressing adapters on sub-billion-parameter models?
  answers:
  - small-models-peft
- q:
  - Can sparsification and ternary quantization compress a fully fine-tuned model's task vector?
  - Does the compression method extend beyond PEFT to full fine-tuning residuals?
  - What happens when full fine-tuning updates are ternarized on BERT and RoBERTa?
  answers:
  - full-finetuning
- q:
  - Do compressed checkpoints merge better or worse than uncompressed ones?
  - Does sparsifying task vectors help task arithmetic and TIES-Merging?
  - How does adapter compression interact with model merging?
  answers:
  - merging
- q:
  - Do compressed LoRA experts still compose for unseen tasks?
  - Does compression break LoraHub-style few-shot cross-task generalization?
  - What is the Big-Bench Hard performance of compressed experts under LoraHub?
  answers:
  - compositional
- q:
  - How does ComPEFT compare with Sparse Ternary Compression, BitDelta and DAREx?
  - Which delta-compression baselines were beaten and by how much?
  - Is a tuned scalar better than using the mean magnitude for ternary quantization?
  answers:
  - baselines-70b
  - ablation-stc
- q:
  - Is a compressed adapter competitive with other parameter-efficient fine-tuning methods
    on the storage-accuracy trade-off?
  - How does compressed (IA)^3 compare with BitFit, Adapters, Compacter and prompt tuning?
  - What does Pareto-optimal mean for PEFT storage versus performance in ComPEFT?
  answers:
  - pareto
- q:
  - How many bits per parameter does a sparse ternary task vector need?
  - What is the theoretical compression limit of ternarizing a 95% sparse update?
  - How is the storage size of a compressed task vector computed?
  answers:
  - entropy
- q:
  - Do I need to tune the density and scaling hyperparameters for every task?
  - When can I just set alpha to 1 in ComPEFT?
  - How do density k and scaling alpha interact?
  answers:
  - alpha-tuning
misreadings:
- 'ComPEFT''s accuracy gains are not universal: on LLaMA-7B and 13B it loses to the original
  QLoRA checkpoint on 4 of 32 configurations, and full fine-tuning compression on T5-Base
  drops 4.7 points.'
- Compressing (IA)^3 is not always safe. On base models with weak zero-shot performance such
  as BERT, RoBERTa and T5v1.1, ternarizing (IA)^3 residuals causes large accuracy drops, while
  LoRA compresses with minimal loss.
- The reported 32x download and 25x load speedups are transmission and memory-transfer times,
  not inference throughput; realizing wall-clock compute gains from sparse ternary vectors
  would require custom Triton/CUDA kernels that ComPEFT does not provide.
- ComPEFT is not the same as Sparse Ternary Compression. Applying STC directly to task vectors
  degrades performance on 3B and 7B base models, and the difference is the tuned scaling factor
  alpha times the task vector's standard deviation.
- ComPEFT does not quantize the base model. It compresses only the fine-tuning residual, so
  both the initial and fine-tuned parameters must be available and the base model is still
  served at its own precision.
- 'The gains are not an artifact of an over-parameterized rank-64 LoRA: compressing rank-32
  and rank-8 LoRA on LLaMA2-70B still yields over 25x compression and still beats the corresponding
  uncompressed checkpoint.'
terminology:
  task vector: the difference between a fine-tuned parameter vector and the initial pre-trained
    parameter vector, treated as the object to be compressed.
  density (k): the fraction of task-vector entries whose signs are kept after top-magnitude
    selection; sparsity is 1 minus density.
  ternary quantization in ComPEFT: replacing every kept task-vector magnitude by one shared
    scalar equal to a tuned coefficient alpha times the task vector's standard deviation,
    leaving entries in {-1, 0, +1} times that scalar.
  Com(IA)^3 / ComLoRA: the names for ComPEFT compression applied to (IA)^3 and to LoRA checkpoints
    respectively.
  Golomb coding: a near-entropy variable-length code for geometrically distributed gaps, used
    to store the positions and signs of nonzero entries in a sparse ternary task vector.
links_extra:
  code: https://github.com/prateeky2806/compeft
  arxiv_html: https://arxiv.org/html/2311.13171
---
