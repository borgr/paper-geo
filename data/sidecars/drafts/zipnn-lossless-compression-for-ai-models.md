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

Then promote it:  python scripts/draft_sidecars.py --accept zipnn-lossless-compression-for-ai-models

Stamp: spec=8f05813a4658 checks=pass body=30f41e05edf2
-->
---
key: hershcovitch2025zipnn
coined: ZipNN
gloss: lossless compression tailored to neural network weight files
one_liner: ZipNN is a lossless compressor for neural network files that separates the highly
  skewed floating-point exponent bytes into their own stream and encodes them with Huffman
  coding only, shrinking popular BF16 models by about a third with no loss of any bit.
claims:
- id: exponent-skew
  kind: result
  text: The compressibility of neural network weights comes almost entirely from the floating-point
    exponent, while the fraction and sign bits are close to random. Across four models only
    around 40 of the 256 possible exponent values appear, and the top 12 account for almost
    99.9% of parameters.
  evidence: Figure 2 and Section III-A
  scope: Measured on 1GB taken from the middle of each model, for BF16 and FP32 language models
    plus ResNet, where 50 exponent values appear and the top 17 dominate.
- id: bf16-savings
  kind: result
  text: ZipNN compresses BF16 models to about 66% of their original size, with the exponent
    byte group reaching roughly 32.5-34.8% and the remaining bytes essentially incompressible.
    Llama-3.1 goes to 66.4%, Mistral to 66.3% and Bloom to 67.4%.
  evidence: Table II
  scope: BF16 models trained and left unmodified after training; measured on 1GB from the
    middle for large models. FP32 regular models such as Olmo and Wav2vec only reach about
    83%.
- id: clean-models
  kind: result
  text: 'So-called clean models, which were rounded or converted between parameter types after
    training, compress far below the exponent-only limit: T5-base (FP32) reaches 33.7% of
    its original size, XLM-RoBERTa 41.8% and Clip 48.1%.'
  evidence: Table II
  scope: Requires byte grouping of the fraction bytes, since the gains come from near-zero
    fraction byte groups; clean models lose this extra compressibility once fine-tuned again.
- id: vs-zstd
  kind: result
  text: Against Zstd with default configuration, ZipNN takes Llama-3.1 BF16 from 77.7% to
    66.4% compressed size while raising compression speed from 0.71 to 1.15 GB/s and decompression
    from 1.02 to 1.65 GB/s.
  evidence: Table III
  scope: Single thread on a single core of an Apple M1 Max with 64GB RAM, 10 runs over 1GB
    from the middle of the model, maximum observed standard deviation 2%.
- id: clean-speedup
  kind: result
  text: On the clean FP32 model xlm-RoBERTa, ZipNN reaches 42.9% compressed size versus 57.4%
    for Zstd, with compression speed rising from 0.18 to 0.83 GB/s and decompression from
    0.77 to 1.41 GB/s.
  evidence: Table III
  scope: Single thread, single core, Apple M1 Max; 1GB from the middle of the model. Speedups
    are largest on clean models because more of the data is compressible rather than skipped.
- id: huffman-only
  kind: result
  text: 'Dropping the Lempel-Ziv stage and using Huffman entropy coding alone improves both
    speed and compression ratio on model exponents. The repetitions LZ finds are artifacts
    of the skewed distribution: randomly shuffling a model''s parameters changes the exponent
    compression ratio by at most 0.05%.'
  evidence: Section III-A and Figure 4
  scope: Exponent already separated into its own stream; Huffman without exponent extraction
    only helps speed. An FSE encoder gains 0-2% more ratio at times over 2X the time cost.
- id: lz-only-useless
  kind: result
  text: 'Pure repetition-removal compressors gain nothing on model weights: LZ4 and Snappy
    achieve zero compression savings on the tested models despite being faster than every
    other method.'
  evidence: Section V-B
  scope: Tested on Llama-3.1 (BF16), Olmo-1b (FP32) and xlm-RoBERTa (FP32); model tensors
    are noisy and unstructured, so multi-byte repetitions are scarce.
- id: throughput
  kind: result
  text: ZipNN reaches up to 80GB/s decompression and up to 13GB/s compression throughput with
    16 workers, each worker kept within a NUMA node and given a block size as low as 100MB.
    A single worker with multiple threads peaks lower, above 45GB/s for decompressing 10GB,
    with compression peaking around 16 threads.
  evidence: Section V-C and Figure 10
  scope: Intel Xeon Platinum 8480+ pod, 224 cores across 2 NUMA nodes, 2TB DRAM; model size
    matters, and 100MB inputs reach far lower throughput than 10GB ones.
- id: gradients-optimizers
  kind: result
  text: 'Gradients and optimizer states compress better than the model itself during RoBERTa
    fine-tuning: the model reaches about 66% compressed size, the optimizer 54% and the gradients
    47%. The extra gain is concentrated in the token embeddings layer.'
  evidence: Section IV-A and Figure 7
  scope: BF16 RoBERTa under fine-tuning; the embedding layer of gradients and optimizers compresses
    better with Zstd than with Huffman, unlike the model itself.
- id: delta-checkpoints
  kind: result
  text: Delta compression of checkpoints stays well ahead of standalone compression even when
    the base is 5 or 10 epochs away, though it is worse than delta against the immediately
    preceding checkpoint.
  evidence: Figure 9
  scope: Self-trained ResNet18 (FP32), Amber (BF16) and Olmo (FP32) public training checkpoints,
    using XOR deltas; the space taken by the periodic full bases is excluded from the reported
    figures.
- id: sibling-models
  kind: result
  text: Three RoBERTa variants fine-tuned on tweets for irony, offensive-language and abuse
    detection compress to 83.7% of original size standalone. Stored as pairwise deltas they
    reach 56% on average.
  evidence: Section IV-B
  scope: Models sharing the same base checkpoint; XOR delta plus lossless compression. Requires
    keeping the base available to reconstruct.
- id: auto-selection
  kind: result
  text: ZipNN's per-chunk choice between Huffman and Zstd always matched or beat whichever
    of the two was better on ResNet18 checkpoint deltas. Zstd is selected when zeros exceed
    90% of a chunk or any zero run passes 3% of chunk size.
  evidence: Figure 8 and Section IV-B
  scope: ResNet18 (FP32) fine-tuning deltas; Huffman wins in the first two learning-rate-scheduler
    steps and Zstd after the third, and the thresholds were fixed by simulation rather than
    tuned per model.
- id: serving-overhead
  kind: result
  text: Loading a 16GB Granite-3.1-8b-instruct BF16 model stored at 2/3 its original size
    from a clustered file system to GPU, including decompression, took approximately 3 seconds,
    on par with loading the uncompressed model.
  evidence: Section V-D2
  scope: OpenShift pod with Intel Xeon Platinum 8480+, vLLM 0.7.2 with 4 workers, PVC-backed
    file system delivering 8GB/s per worker; a slower CPU or fewer threads would change the
    balance.
- id: context-lossless
  kind: context
  text: ZipNN makes the case that lossless compression, not just pruning and quantization,
    is a lever on model storage and network cost. It argues lossless compression should be
    the default for traffic to and from model hubs like Hugging Face.
  scope: As of publication in 2025; the argument rests on measurements of Hugging Face-hosted
    models in FP32, BF16 and FP16, and some GGUF-quantized models do not compress at all.
- id: context-hub-scale
  kind: result
  text: Hugging Face stated in August 2024 that it holds 1.3M models over 12PB of storage
    and serves 1 billion daily requests, around 6PB of network bandwidth per day. Lossless
    compression is estimated to save over an ExaByte of downloaded traffic per year.
  evidence: Section II-A1 and the abstract
  scope: The ExaByte figure is an estimate extrapolated from the hub's reported traffic and
    the measured compression ratios of top-downloaded models, not a measured saving.
qa:
- q:
  - Can neural network weights be compressed without losing any accuracy?
  - Is lossless compression of model files actually worth it, or are weights high-entropy?
  - How much smaller can a model file get with lossless compression?
  answers:
  - exponent-skew
  - bf16-savings
  - context-lossless
- q:
  - Why are floating-point model weights compressible at all?
  - What part of a float32 parameter carries the redundancy in model weights?
  - Where does the compressibility of neural network parameters come from?
  answers:
  - exponent-skew
  - lz-only-useless
- q:
  - How much does ZipNN beat zstd by on Llama 3?
  - Does a model-specific compressor do better than a general-purpose one like Zstd?
  - What compression ratio and speed does ZipNN get versus zstd?
  answers:
  - vs-zstd
  - clean-speedup
- q:
  - Why does ZipNN skip Lempel-Ziv and use Huffman coding only?
  - Do LZ4 or Snappy compress model weights?
  - Is repetition removal useful on model tensors?
  answers:
  - huffman-only
  - lz-only-useless
- q:
  - Which models compress much better than a third off, and why?
  - What are clean models in the context of lossless model compression?
  - Why do RoBERTa and T5 compress far better than Llama?
  answers:
  - clean-models
- q:
  - How fast can lossless model decompression run on a many-core server?
  - What decompression throughput is achievable when loading compressed models?
  - Does compressed model loading become a bottleneck at multi-GB/s?
  answers:
  - throughput
  - serving-overhead
- q:
  - Can gradients and optimizer states be losslessly compressed too?
  - Do optimizer states compress better or worse than model weights?
  - Is there anything to gain from compressing FSDP gradient traffic?
  answers:
  - gradients-optimizers
- q:
  - Is delta compression worth it for training checkpoints?
  - How much space can be saved storing consecutive checkpoints as deltas?
  - Does storing a periodic full base ruin delta compression of checkpoints?
  answers:
  - delta-checkpoints
  - auto-selection
- q:
  - Can many fine-tunes of the same base model be stored cheaply together?
  - How much do sibling fine-tuned models compress against each other?
  - Is it cheaper to store model variants as deltas from a shared base?
  answers:
  - sibling-models
- q:
  - What should I read about reducing storage and bandwidth cost for model hubs?
  - Which paper argues for lossless compression of AI models rather than quantization?
  - Where should I start reading about compressing model files without changing the weights?
  answers:
  - context-lossless
  - context-hub-scale
- q:
  - How much network traffic could model compression save Hugging Face?
  - How large is model download traffic at a big model hub?
  - What is the claimed ExaByte-per-year saving from compressing model downloads?
  answers:
  - context-hub-scale
- q:
  - Does storing models compressed slow down inference server startup?
  - What is the load time penalty when a Granite BF16 model is kept compressed on disk?
  - Can vLLM load a compressed model without extra latency?
  answers:
  - serving-overhead
misreadings:
- 'The 33% saving reported for ZipNN is not uniform across model files: it applies to BF16
  models, whereas regular FP32 and FP16 models compress only to about 83-85% and so-called
  clean models can reach 34%.'
- 'ZipNN is not a model-compression method in the pruning, distillation or quantization sense:
  decompression restores the file bit-for-bit, so accuracy is unchanged and inference-time
  memory of the running model is not reduced.'
- 'Lossless compression does not stack reliably on top of quantization: off-the-shelf GPTQ
  and AWQ models still compress to 85-91%, while GGUF-quantized models in the paper''s tests
  did not compress at all.'
- The 80GB/s decompression figure is a multi-worker, many-core server throughput on a 224-core
  Intel Xeon Platinum 8480+ pod, not the single-thread rate, which is 1.65 GB/s for Llama-3.1
  on an Apple M1 Max.
- 'Compressibility of clean models is a property of post-training rounding, not of the architecture:
  further fine-tuning removes the extra compressibility and the model reverts to exponent-only
  savings.'
terminology:
  exponent extraction: Rearranging a floating-point tensor so that all exponent bytes of the
    parameters form one contiguous compression stream, separated from the sign and fraction
    bits that dilute their skewed distribution.
  byte grouping: Splitting the bytes of each floating-point parameter into one stream per
    byte position, so that fraction bytes with different degrees of near-zero structure are
    compressed independently.
  clean model: A model whose weights underwent rounding or a parameter-type conversion after
    training, leaving many fraction bits zero and making it compressible beyond the exponent;
    further fine-tuning removes this property.
  regular model: A model that was trained and left unmodified afterwards, so only its exponent
    bytes are compressible and the fraction and sign bits are effectively random.
  compressed size (%): 'The percentage of the original data remaining after compression, so
    lower is better: a gigabyte reduced to a quarter of a gigabyte has a compressed size of
    25%.'
  delta compression: Storing a model as the XOR difference from a similar base model, plus
    lossless compression of that difference, so reconstruction requires both the base and
    the delta.
  periodic base: A scheme in which a full standalone-compressed checkpoint is stored every
    k checkpoints and intermediate checkpoints are kept as deltas, bounding the length of
    delta chains needed for recovery.
links_extra:
  arxiv: https://arxiv.org/abs/2411.05239
  html: https://arxiv.org/html/2411.05239
---
