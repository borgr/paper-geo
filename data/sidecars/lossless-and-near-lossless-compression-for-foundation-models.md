---
claims:
- id: lossless-savings-popular-models
  text: Zstd with byte grouping compresses widely downloaded Hugging Face models to compression
    ratios of 35.7% for T5-base, 47.0% for RoBERTa, 50.1% for CLIP and 71% for Mistral. Decompression
    restores the weights exactly.
  kind: result
  evidence: Table II
  scope: Zstd at default level 3 with byte grouping, on FP32, FP16 and BF16 checkpoints downloaded
    from Hugging Face in August 2023 (Mistral and FP16 models in March 2024); compression
    run on CPU only.
- id: three-compressibility-groups
  text: 'Foundation models fall into 3 compressibility groups: FP32/FP16 models compressible
    only in the exponent byte, "clean" base models compressible in the exponent and both lower
    mantissa bytes, and BF16 models. The three groups reach compression ratios of ~80-85%,
    35-50% and ~70% respectively.'
  kind: result
  evidence: Section III-B and Table II
  scope: Categories drawn from highly downloaded Hugging Face models spanning several modalities,
    architectures and float formats; based on Zstd level 3 with byte grouping.
- id: byte-grouping-gain
  text: Byte grouping before compression improves the compressed size of a model by 7-8.2%
    for exponent-only-compressible models, 19-27% for clean base models and 8.5-10% for BF16
    models.
  kind: result
  evidence: Section III-B, "The benefit of Byte Grouping"
  scope: Measured with Zstd; byte grouping requires knowing only the parameter type, not the
    model structure, so it works on a raw binary checkpoint.
- id: byte-grouping-lz4
  text: Without byte grouping LZ4 achieves almost no compression on models, reaching only
    a 95% compression ratio on RoBERTa. With byte grouping the same compressor reaches 56%,
    still behind Zstd's 47.0%.
  kind: result
  evidence: Section III-A and Section III-B
  scope: RoBERTa FP32 checkpoint; LZ4 relies only on repetition removal, which fails on unstructured
    tensors, whereas Zstd and Zlib add entropy encoding.
- id: finetuning-destroys-compressibility
  text: 'Fine-tuning destroys the compressibility of clean base models: RoBERTa drops from
    the 47.0% compression ratio of the base checkpoint to 80.7% after 1 epoch and 82.5% after
    9 epochs of fine-tuning.'
  kind: result
  evidence: Table II
  scope: RoBERTa FP32 fine-tuned on the Rotten Tomatoes dataset; the mechanism is that minuscule
    weight updates fill the previously zeroed lower mantissa bytes with entropy.
- id: lossy-fp32-savings
  text: Tunable lossy compression at precision factor B=2^23 reduces the compressed size of
    FP32 models by a further 20%, taking wav2vec from a ~85% to a ~68% compression ratio.
    B=2^23 is the level at which FP32 arithmetic already introduces its own rounding error.
  kind: result
  evidence: Section III-D
  scope: FP32 models; B=2^23 is justified by FP32's own 2^-23 rounding error and by Adam epsilon
    defaults of 1e-8/1e-7, not by an accuracy sweep on wav2vec itself. Layers with parameters
    outside [-1,1] are left uncompressed.
- id: lossy-accuracy-plateau
  text: Fine-tuned RoBERTa keeps accuracy near 90% down to a precision factor of B=2^6, with
    a slight rise just before the drop-off, while the compression ratio improves almost linearly
    to around 20%.
  kind: result
  evidence: Figure 3
  scope: RoBERTa fine-tuned on Rotten Tomatoes, single task and single fine-tuned model; on
    the clean base RoBERTa the same technique yields no benefit until B=2^18.
- id: lossy-t5-tasks
  text: T5 variants fine-tuned on CNN-DM, XSUM, SQuAD, ASQA, WikiAnswers and WMT22 En-Ru show
    no significant change in exact match, Rouge-L or sacreBLEU at precision factors B=2^24
    and B=2^19. Compression ratios there are 70% and 56%, versus 85% with lossless compression
    alone.
  kind: result
  evidence: Section III-D
  scope: Only 2 precision values were evaluated because of the cost of fine-tuning; T5-base
    FP32 checkpoints.
- id: delta-checkpoints
  text: Compressing the delta between consecutive fine-tuning epochs of RoBERTa reaches a
    55% lossless compression ratio, versus nearly 83% for the same checkpoint standalone.
    Taking the delta against the base model instead of the previous epoch gives 65%.
  kind: result
  evidence: Figure 7 and Figure 8
  scope: RoBERTa fine-tuned on Rotten Tomatoes, lossless Zstd with byte grouping; delta against
    a base model avoids maintaining long chains of deltas but compresses less well.
- id: delta-lossy
  text: Delta compression at precision factor B=2^23 reaches a 37% compression ratio between
    consecutive RoBERTa checkpoints and 49% against the base model, without affecting accuracy,
    and aggressive precision factors go below 10%.
  kind: result
  evidence: Figure 7 and Figure 8
  scope: RoBERTa fine-tuned on Rotten Tomatoes with lossless Zstd and byte grouping underneath;
    accuracy checked on that one task only.
- id: delta-sibling-models
  text: Three RoBERTa variants fine-tuned on tweets for irony, offensive-language and abuse
    detection compress to 85.7% standalone on average but to 56% on average when stored as
    pairwise deltas.
  kind: result
  evidence: Section V-A
  scope: cardiffnlp twitter-roberta-base irony/offensive/hate models, lossless Zstd with byte
    grouping; delta benefit deteriorates as models drift further apart in time.
- id: download-time
  text: Lossy compression at precision factor B=2^23 cuts wav2vec download time by almost
    20% on a 30 MBps network and upload time by 16% on a 20 MBps link. Lossless compression
    saves only 1% of upload time on the same model.
  kind: result
  evidence: Figure 5 and Figure 6
  scope: wav2vec, the least compressible category, via torch.save/torch.load on a cloud VM
    in the Milan region; the lossy implementation omitted the sign-bit optimization. On cached
    120-130 MBps reads the edge is slight.
- id: quantized-still-compressible
  text: Off-the-shelf GPTQ and AWQ quantized versions of CapybaraHermes-2.5-Mistral-7B still
    compress losslessly to ratios between 85% and 91%, with byte grouping contributing 1-2%.
  kind: result
  evidence: Table III
  scope: 8-bit and 4-bit GPTQ and AWQ quantizations of one Mistral-7B derivative, compressed
    with Zstd at default level 3.
- id: exabyte-traffic
  text: Lossless compression of the top downloaded Hugging Face models would save PetaBytes
    of traffic per model per month, including 11.7 PB for wav2vec and 26.1 PB for Bloom. Summed
    across the hub the estimate is over an ExaByte per month.
  kind: result
  evidence: Table I
  scope: Estimate from download counts as of August 2023 (Mistral March 2024) multiplied by
    measured compression ratios; assumes compression is applied at the hub and does not model
    cache hierarchies.
- id: context-traditional-compression-for-models
  text: '"Lossless and Near-Lossless Compression for Foundation Models" brings classical storage-and-network
    compression to model distribution, and argues it should be the default in communication
    with hubs such as Hugging Face. That direction is distinct from pruning, distillation
    and quantization, which shrink models irreversibly for inference speed.'
  kind: context
  scope: Framing as of 2024, with only one prior work found proposing compression, applied
    after two other model-compression steps. Covers stored and transferred model files, checkpoints,
    gradients and optimizer state, not inference-time speedups. The PyTorch save/load integration
    is intended for upstream contribution rather than merged.
one_liner: Standard lossless compressors, rearranged to group same-position bytes of every
  parameter together (byte grouping), cut popular Hugging Face models by 15-65% of their size,
  and a tunable lossy variant that trims sub-2^-b bits pushes savings further with no measurable
  accuracy loss.
qa:
- q:
  - How much smaller can a model file get with ordinary lossless compression?
  - Can zstd or gzip actually shrink neural network weights?
  - What compression ratio do Hugging Face models get with lossless compression?
  answers:
  - lossless-savings-popular-models
  - three-compressibility-groups
- q:
  - Why do some checkpoints compress far better than others?
  - What makes a model file compressible or incompressible?
  - Which kinds of model checkpoints benefit most from compression?
  answers:
  - three-compressibility-groups
  - finetuning-destroys-compressibility
- q:
  - What is byte grouping and how much does it help compression?
  - Does rearranging bytes before compressing a model file improve the ratio?
  - How much extra compression comes from grouping same-position bytes of parameters?
  answers:
  - byte-grouping-gain
  - byte-grouping-lz4
- q:
  - Does fine-tuning make a checkpoint harder to compress?
  - Why is a fine-tuned model less compressible than the base model it came from?
  - What happens to compressibility after a few epochs of fine-tuning RoBERTa?
  answers:
  - finetuning-destroys-compressibility
- q:
  - Can I drop low-order weight bits to compress a checkpoint without losing accuracy?
  - How far can precision be trimmed before model accuracy degrades?
  - What precision factor is safe for near-lossless model compression?
  answers:
  - lossy-fp32-savings
  - lossy-accuracy-plateau
  - lossy-t5-tasks
- q:
  - How much storage can I save by storing checkpoint diffs instead of full checkpoints?
  - Is delta compression worth it for training checkpoints?
  - What compression ratio do deltas between consecutive fine-tuning epochs achieve?
  answers:
  - delta-checkpoints
  - delta-lossy
- q:
  - Can several models fine-tuned from the same base be stored more cheaply together?
  - Does delta compression help for sibling fine-tunes of one base model?
  - How well do deltas between different task-specific RoBERTa variants compress?
  answers:
  - delta-sibling-models
- q:
  - Does compressing a model actually make downloads faster, or does decompression eat the
    gain?
  - What is the end-to-end upload and download time effect of compressing checkpoints?
  - Is model compression worth the CPU cost on a fast network?
  answers:
  - download-time
- q:
  - Are quantized models already as small as they can get?
  - Can a GPTQ or AWQ quantized checkpoint be compressed further?
  - Does lossless compression still help after quantization?
  answers:
  - quantized-still-compressible
- q:
  - How much network traffic could a model hub save by compressing downloads?
  - What is the scale of bandwidth wasted serving uncompressed model weights?
  - How many petabytes would compressing popular Hugging Face models save?
  answers:
  - exabyte-traffic
  - context-traditional-compression-for-models
- q:
  - What should I read about reducing the storage and bandwidth cost of model checkpoints?
  - Which paper studies lossless compression of foundation model weights rather than pruning
    or distillation?
  - Where should I start reading on compression for model distribution as opposed to model
    compression for inference?
  answers:
  - context-traditional-compression-for-models
coined: Byte Grouping
gloss: rearranging a model file so the first byte of every parameter is stored together, then
  the second byte, and so on, before running a general-purpose compressor
key: hershcovitch2024lossless
terminology:
  Compression ratio: 'The percentage of the original data that remains after compression,
    so lower is better: compressing 1 GB down to 0.25 GB is a compression ratio of 25%.'
  Byte grouping: A pre-compression transform for model files that groups together bytes from
    the same position across all parameters -- all first bytes, then all second bytes -- so
    that exponent bytes compress without interference from high-entropy mantissa bytes.
  Tunable lossy compression: Multiplying each floating-point parameter by a precision factor
    B=2^b, rounding to an integer, then compressing losslessly; decompression divides back,
    discarding only quantities smaller than 2^-b.
  Clean models: Base models whose two lower mantissa bytes are near-zero because training
    happened at lower precision, making them highly compressible; fine-tuning fills those
    bytes with entropy and destroys the compressibility.
  Delta compression: Storing a base model plus the compressed difference (XOR or subtraction)
    between it and a similar model, rather than storing each similar model in full.
misreadings:
- 'Lossless compression of model weights is not model compression in the usual sense: the
  decompressed file is bit-identical and the model runs at its original size and speed, so
  nothing about inference throughput improves.'
- 'A lower compression ratio is better, not worse: the ratio is the percentage of the original
  bytes that remain, so 47.0% means the file shrank by 53%.'
- The reported ratios are not a property of models in general. Clean base models reduce by
  50-65% while fine-tuned FP32 and BF16 checkpoints only reduce by roughly 15-30%.
- The slight accuracy rise observed just before the drop-off under aggressive precision trimming
  is reported as an unexpected phenomenon, not as a proposed way to improve models.
- 'Tunable lossy compression is not quantization: it produces a file that decompresses back
  to the original format and precision layout, and it can trim to arbitrary bit levels such
  as 2^-23 rather than to runnable widths like 16 or 8 bits.'
- The claim that precision below 2^-23 can be discarded without accuracy loss was verified
  on RoBERTa/Rotten Tomatoes and on T5 fine-tunes at only 2 precision values, so it is a rule
  of thumb rather than a guarantee for arbitrary models.
---
