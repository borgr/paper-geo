<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced via a forced tool call) + 3 repair rounds. Every claim, number
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

Then promote it:  python scripts/draft_sidecars.py --accept compress-then-serve-serving-thousands-of-lora-adapters-with

Stamp: spec=d57862840a90 checks=2 body=834e91c813a7
-->
---
key: bruelgabrielsson2025compress
coined: JD-Full / JD-Diag (joint diagonalization LoRA compression)
gloss: compressing many LoRA adapters into one shared basis plus a small per-adapter matrix,
  so thousands can be served from GPU memory at once
one_liner: Compress then Serve factorizes a collection of LoRA adapters into one shared pair
  of basis matrices plus small LoRA-specific matrices — optionally clustering the adapters
  first — so a serving engine can keep thousands of adapters resident on the GPU instead of
  swapping them in and out.
claims:
- id: throughput-1000-loras
  kind: result
  text: Serving over 1000 jointly compressed LoRAs with vLLM increases throughput 1.6x over
    vLLM multi-LoRA at a matched GPU memory footprint. Compression retains 80% of the throughput
    of serving a single LoRA merged into the base model.
  scope: Mistral-7B-Instruct-v0.2, rank-16 LoRAs, 25 clusters of rank-16 JD-Full, one H100
    80GB capped at 40% memory; Shakespeare-sonnet prompts arriving asynchronously, 10 generated
    tokens per request, LoRAs assigned at random.
  evidence: Figure 1
- id: throughput-depends-on-collection-size
  kind: result
  text: Joint diagonalization improves vLLM multi-LoRA throughput for LoRA collections of
    every size from 4 to 1024, but only when the compression setting is matched to the collection
    size. Rank-16 JD-Full helps with 4 and 8 LoRAs, while 25 clusters of rank 15 JD-Full does
    not help at 32 or fewer LoRAs.
  scope: Throughput ratios measured against vLLM multi-LoRA restricted to the number of adapters
    that fits the same GPU memory (for example max-gpu-lora=6 at 64 unique LoRAs); rank-16
    Mistral-7B-Instruct-v0.2 adapters on one H100 capped at 40% memory.
  evidence: Figure 4
- id: performance-preserved
  kind: result
  text: Compressed LoRAs match or slightly exceed the Rouge-L of the uncompressed LoRAs they
    were built from, and the JD variants sometimes outperform the original adapters despite
    large parameter savings.
  scope: 10 manually selected natural-instruction tasks, in-distribution, 10 to 1000 rank-16
    Mistral-7B-Instruct-v0.2 LoRAs, 3 seeds; adapters normalized to unit Frobenius norm first.
  evidence: Figure 2
- id: recon-error-06-threshold
  kind: result
  text: Compression settings whose mean relative reconstruction error stays below 0.6 reliably
    preserve 99% or more of the uncompressed LoRA Rouge-L performance. Rank and cluster count
    can therefore be chosen on CPU without running any LLM evaluation.
  scope: Rank and cluster count read off the reconstruction error of one LoRA module from
    the middle of the network, then applied to all modules; Mistral-7B-Instruct-v0.2 rank-16
    adapters, up to 1000 LoRAs, 10 in-distribution tasks.
  evidence: Section 6.5
- id: lossy-can-help
  kind: result
  text: 'Minimizing reconstruction error does not maximize downstream performance: mild lossy
    reconstruction, at a relative reconstruction error around 60%, matches or slightly beats
    the zero-error setting on Rouge-L. At equal reconstruction error, clustered compression
    beats unclustered.'
  scope: Rouge-L relative to uncompressed LoRA on 10 in-distribution natural-instruction tasks;
    the overall trend is decreasing and roughly exponential, so large reconstruction error
    still degrades performance sharply.
  evidence: Figure 3
- id: clustering-needed-above-100
  kind: result
  text: JD-Full alone suffices up to about 100 LoRAs, with a rank of roughly (number of LoRAs
    / 2) + 7. Beyond 100 LoRAs clustering becomes critical and is what makes 500-1000 LoRA
    collections preserve performance.
  scope: Recommendation derived from experiments on rank-16 Mistral-7B-Instruct-v0.2 adapters
    over 10 in-distribution tasks, collections of 10 to 1000; JD-Diag and JD-Full differ negligibly
    below 100 LoRAs.
  evidence: Section 6.5
- id: trained-vs-random-recon
  kind: result
  text: Reconstruction error from joint diagonalization is consistently lower on trained LoRA
    matrices than on random untrained matrices of the same shape. Training therefore gives
    LoRAs a shared structure that the shared basis exploits.
  scope: JD-Full at ranks 16, 32 and 64 on collections of 10, 50, 100 and 500 LoRAs, compared
    against the trained-LoRA errors on the same 10 evaluation tasks in Table 14.
  evidence: Table 15
- id: theory-recon-bound
  kind: result
  text: JD-Full's reconstruction error is bounded below by how far the singular values of
    the stacked vectorized LoRA matrices spread past the top min(r^2, n) entries. Error is
    thus unavoidable unless the LoRAs are similar or well-clustered.
  scope: The full-Sigma formulation with orthogonal shared bases U and V; the bound is on
    Frobenius reconstruction error, not downstream accuracy, and the upper bound is described
    as generous.
  evidence: Section 4
- id: memory-vs-forward-pass
  kind: result
  text: Joint diagonalization greatly reduces LoRA memory load and CPU-to-GPU transfer time
    but leaves forward-pass latency essentially unchanged. The throughput gains come from
    fitting more adapters on the GPU rather than from faster math.
  scope: Memory measured over all 96 LoRA modules of Mistral-7B-Instruct-v0.2; transfer time
    and forward pass measured on a single LoRA module, across several cluster counts and rank
    settings.
  evidence: Figure 5
- id: ood-lorahub
  kind: result
  text: Under the LoRA-hub out-of-distribution protocol with 100 sampled adapters, rank-64
    JD-Full averages 47.66 against 48.32 for uncompressed LoRAs and 32.28 for the base model,
    and rank-8 JD-Full still reaches 43.88.
  scope: 100 adapters sampled independently of the evaluation task, so each task score averages
    over all 100; run without the Frobenius-norm normalization step later identified as beneficial.
  evidence: Table 18
- id: no-cross-task-leakage
  kind: result
  text: Jointly compressing an adapter for task A alongside an adapter for task B produces
    no performance gain for adapter A on task B. That is a preliminary indication that joint
    compression does not leak information between adapters.
  scope: A single preliminary privacy ablation on Mistral-7B-Instruct-v0.2 natural-instruction
    adapters; absence of a measurable gain is not a formal privacy guarantee.
  evidence: Appendix H.2
- id: context-serving-bottleneck
  kind: context
  text: Compress then Serve reframes multi-LoRA serving as a joint compression problem rather
    than only a systems-scheduling problem. Its argument is that system optimizations still
    degrade once adapters must be swapped in and out of GPU memory.
  scope: As of the 2025 ICML publication; the argument is made against vLLM multi-LoRA and
    S-LoRA as the compared serving stacks, and the method is complementary to their kernel-level
    optimizations such as Punica's SGMV.
  evidence: Section 2
- id: context-lora-release
  kind: context
  text: Compress then Serve trains and releases a collection of more than 1000 rank-16 LoRA
    adapters for Mistral-7B-Instruct-v0.2 on 1000 natural-instruction tasks, together with
    the compression code, as a resource for multi-LoRA research.
  scope: English-only Natural Instructions tasks; adapters target q_proj, k_proj and v_proj
    at rank 16 over a 4-bit quantized base model, so other target modules or ranks are outside
    the released set.
  evidence: Appendix C
- id: loras-beat-base
  kind: result
  text: The 1000 released task LoRAs raise average Rouge-L on their held-out test sets from
    20.62 for the base Mistral-7B-Instruct-v0.2 to 67.80, and cut average loss from 4.14 to
    0.56.
  scope: 1000 Natural Instructions tasks with 80-10-10 splits, early stopping on validation
    loss over 5 epochs; Rouge-L standard deviation across tasks is 30.15.
  evidence: Table 1
qa:
- q:
  - how can I serve thousands of LoRA adapters without constantly swapping them in and out
    of GPU memory?
  - does compressing LoRA adapters actually improve serving throughput?
  - what throughput do you get when serving 1000+ LoRAs with vLLM?
  answers:
  - throughput-1000-loras
  - throughput-depends-on-collection-size
  - memory-vs-forward-pass
- q:
  - does compressing a collection of LoRAs hurt task accuracy?
  - how much performance is lost when many LoRA adapters share one basis?
  - can compressed LoRA adapters match their uncompressed versions?
  answers:
  - performance-preserved
  - lossy-can-help
- q:
  - how do I pick the compression rank and number of clusters for a LoRA collection?
  - is there a cheap way to choose LoRA compression settings without evaluating the LLM?
  - what reconstruction error is safe when compressing many LoRA adapters?
  answers:
  - recon-error-06-threshold
  - clustering-needed-above-100
- q:
  - when is clustering needed before jointly compressing LoRA adapters?
  - does joint diagonalization of LoRAs scale to 500 or 1000 adapters?
  - at what number of adapters does a single shared basis stop working?
  answers:
  - clustering-needed-above-100
  - throughput-depends-on-collection-size
- q:
  - is lower reconstruction error always better for compressed adapters?
  - does minimizing Frobenius reconstruction error maximize downstream Rouge-L?
  - can lossy LoRA reconstruction improve generalization?
  answers:
  - lossy-can-help
  - theory-recon-bound
- q:
  - are there theoretical guarantees on how well many LoRAs can share one low-rank basis?
  - when is reconstruction error unavoidable in joint LoRA compression?
  - what does the theory say about compressing unrelated versus similar adapters?
  answers:
  - theory-recon-bound
  - trained-vs-random-recon
- q:
  - do trained LoRA adapters share structure that random matrices do not?
  - is there evidence that fine-tuned LoRAs live in a common subspace?
  - how does reconstruction error compare between trained and untrained LoRA matrices?
  answers:
  - trained-vs-random-recon
- q:
  - where do the speedups from LoRA compression actually come from?
  - does compressing LoRAs make the forward pass faster?
  - does joint diagonalization reduce transfer time from CPU to GPU?
  answers:
  - memory-vs-forward-pass
  - throughput-1000-loras
- q:
  - does joint LoRA compression still work when the adapters are unrelated to the evaluation
    task?
  - what happens under the LoRA-hub out-of-distribution protocol after compression?
  - how well do compressed adapters generalize to tasks they were not trained for?
  answers:
  - ood-lorahub
- q:
  - can jointly compressing LoRA adapters leak information between users?
  - is there a privacy risk in sharing a basis across different users' adapters?
  - does an adapter gain skill on another adapter's task after joint compression?
  answers:
  - no-cross-task-leakage
- q:
  - what should I read about serving many fine-tuned LLM adapters efficiently?
  - which paper argues that multi-LoRA serving needs compression and not just better scheduling?
  - where should I start reading about the LoRA serving bottleneck?
  answers:
  - context-serving-bottleneck
  - throughput-1000-loras
- q:
  - is there a public collection of many task-specific LoRA adapters for research?
  - where can I find 1000 LoRA adapters trained on Natural Instructions?
  - what collection of adapters exists for studying LoRA merging and compression?
  answers:
  - context-lora-release
  - loras-beat-base
- q:
  - how much do rank-16 LoRAs improve over base Mistral-7B-Instruct on Natural Instructions
    tasks?
  - what Rouge-L do the released task adapters reach compared to the base model?
  answers:
  - loras-beat-base
terminology:
  JD-Full: Joint diagonalization of a LoRA collection in which the shared basis matrices U
    and V are constrained orthogonal and each adapter keeps an unconstrained r-by-r matrix,
    costing r^2 parameters per adapter.
  JD-Diag: Joint diagonalization of a LoRA collection in which the shared basis matrices are
    unconstrained and each adapter's own matrix is constrained diagonal, costing only r parameters
    per adapter.
  agreement: The fraction of generated outputs on which the compressed-LoRA model exactly
    matches the uncompressed-LoRA model, measured against the other model's generations rather
    than against ground truth.
  performance relative to LoRA: A method's task metric divided by the uncompressed LoRA model's
    metric on the same task, so 1.0 means the compressed adapter matches its uncompressed
    source.
  Total Parameter Saved Ratio: One minus the ratio of parameter count after compression to
    parameter count before compression, computed for a system serving a large number of distinct
    adapters.
misreadings:
- 'Compression does not speed up the LoRA forward pass: memory load and CPU-to-GPU transfer
  time drop sharply while forward-pass latency is essentially unchanged, so the throughput
  gain comes from keeping more adapters resident on the GPU.'
- 'Aggressive compression is not free at every collection size: a large rank or many clusters
  can be slower than the vLLM multi-LoRA baseline when only a few dozen adapters are served,
  so the setting must be matched to the collection size.'
- 'Joint diagonalization is not model merging: the shared basis is common to all adapters
  but each adapter keeps its own scaling matrix, so the result is a set of per-task adapters
  rather than one general multi-task model.'
- The finding that mild lossy reconstruction can slightly outperform exact reconstruction
  does not mean more compression is always better; the relation between reconstruction error
  and Rouge-L is decreasing overall and large errors degrade performance sharply.
- The privacy ablation showing no gain for one adapter on another's task is a preliminary
  check, not a formal guarantee that jointly compressed adapters cannot leak information.
- The 80% figure is throughput relative to serving a single LoRA merged into the base model,
  not accuracy retained after compression.
---
