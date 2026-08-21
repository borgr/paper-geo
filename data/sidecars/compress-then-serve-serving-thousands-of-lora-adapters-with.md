---
key: gabrielsson2025compress
coined: JD-Full / JD-Diag (joint diagonalization of LoRAs)
gloss: compressing many LoRA adapters into one shared basis plus a small per-adapter matrix,
  so thousands can be served from one GPU
one_liner: Compress then Serve jointly compresses a collection of LoRA adapters into a shared
  basis U, V plus small LoRA-specific matrices, found by joint diagonalization and clustering,
  so that thousands of adapters fit in GPU memory and can be served with little throughput
  loss.
claims:
- id: throughput-1000
  kind: result
  text: Serving over 1000 jointly compressed LoRAs with vLLM increases throughput 1.6x over
    vLLM multi-LoRA at a matched GPU memory footprint. The compressed collection retains 80%
    of the throughput of serving the base LLM or a single merged LoRA.
  scope: Mistral-7B-Instruct-v0.2, rank-16 LoRAs, 25 clusters at compression rank 16, asynchronous
    requests generating 10 tokens each on a Shakespeare-sonnet input set, one H100 80GB GPU
    capped at 40% memory.
  evidence: Figure 1
- id: throughput-crossover
  kind: result
  text: Compression settings for LoRA serving must be matched to collection size. Rank-16
    JD-Full improves vLLM multi-LoRA throughput at 4 and 8 LoRAs but not beyond, while 25
    clusters at rank 15 helps only from well above 32 LoRAs, with large gains at 1000+.
  scope: vLLM multi-LoRA baseline given the same GPU memory footprint (max-gpu-lora set per
    collection size), Mistral-7B-Instruct, rank-16 LoRAs, collections between 4 and 1024.
  evidence: Figure 4
- id: recon-threshold
  kind: result
  text: LoRA compression settings whose mean relative reconstruction error stays below 0.6
    reliably preserve 99% or more of the uncompressed LoRAs' Rouge-L performance. Compression
    rank and cluster count can therefore be tuned on CPU without any LLM evaluation.
  scope: Frobenius reconstruction error of BA measured on one LoRA module from the middle
    of the network; 10 in-distribution natural-instruction tasks with Mistral-7B-Instruct;
    adapters normalized to unit Frobenius norm before compression.
  evidence: Section 6.5
- id: lossy-helps
  kind: result
  text: 'Minimizing reconstruction error does not maximize downstream performance for compressed
    LoRAs: moderate reconstruction error around 60% matches or slightly exceeds the zero-error
    setting on Rouge-L. At equal reconstruction error, clustering beats non-clustered joint
    diagonalization.'
  scope: Rouge-L relative to uncompressed LoRA on 10 in-distribution natural-instruction tasks,
    Mistral-7B-Instruct, rank-16 LoRAs, collections of 10 to 1000; at large reconstruction
    error performance falls off sharply.
  evidence: Figure 3
- id: clustering-needed
  kind: result
  text: Joint diagonalization of LoRAs alone suffices up to about 100 adapters, using a rank
    of roughly (number of LoRAs / 2) + 7. Clustering becomes essential at 500-1000 LoRAs,
    where JD-Full with clustering preserves performance.
  scope: Mistral-7B-Instruct with rank-16 LoRAs on natural-instruction tasks; JD-Full is preferred
    over JD-Diag, though below 100 LoRAs the difference between them is negligible.
  evidence: Section 6.5
- id: recon-bound
  kind: result
  text: For n LoRAs stacked as columns of a matrix L, JD-Full's reconstructed Frobenius energy
    is bounded above by the sum of L's top min(r^2, n) squared singular values. Reconstruction
    error is thus unavoidable unless L's spectrum concentrates in the top r^2 directions.
  scope: JD-Full with orthogonal U, V of r columns; the bound is on Frobenius reconstruction
    error, not on downstream LLM accuracy, and the proof notes the Von Neumann upper bound
    is generous because vec(BA) has Kronecker structure.
  evidence: Theorem 1, Section 4
- id: orthogonal-corollary
  kind: result
  text: When LoRAs are mutually orthogonal and normalized to unit Frobenius norm, JD-Full's
    relative reconstruction error is at least 1 - min(r^2/n, 1). For r^2 much smaller than
    n the reconstruction therefore retains little of the original adapters.
  scope: Idealized case of exactly orthogonal, unit-norm LoRAs; real trained LoRAs share structure
    and do considerably better, and clustering with k growing in n can keep error bounded
    at fixed r.
  evidence: Corollary 1, Section 4
- id: trained-vs-random
  kind: result
  text: Reconstruction error of joint diagonalization is consistently higher on random untrained
    LoRA matrices than on trained ones, indicating that training gives LoRAs a shared component
    that joint diagonalization exploits.
  scope: JD-Full at ranks 16, 32 and 64 on collections of 10, 50, 100 and 500 rank-16 Mistral-7B-Instruct
    LoRAs, compared against the trained-LoRA errors in Table 14.
  evidence: Table 15, Appendix H.11
- id: ood-lorahub
  kind: result
  text: Under the LoRA-hub out-of-distribution protocol with 100 sampled adapters, JD-Full
    at rank 64 averages 47.66 versus 48.32 for uncompressed LoRAs and 32.28 for the base model.
    JD-Diag at rank 64 averages 47.43.
  scope: 100 LoRAs sampled independently of the evaluation task, averaged over 10 BIG-Bench-style
    tasks; these runs were done without the Frobenius normalization of adapters that the paper
    later found beneficial.
  evidence: Table 18
- id: lora-quality
  kind: result
  text: The 1000 released LoRAs for Mistral-7B-Instruct-v0.2 raise mean Rouge-L from 20.62
    to 67.80 over the base model. Mean exact match rises from 1.81 to 51.38 and mean test
    loss falls from 4.14 to 0.56.
  scope: Rank-16 LoRAs on q_proj, k_proj and v_proj of a 4-bit quantized base model, one adapter
    per task across 1000 English natural-instruction tasks, early stopping on validation loss.
  evidence: Table 1
- id: no-leakage
  kind: result
  text: Compressing an adapter for one task jointly with an adapter for a second task gave
    no performance gain on the second task. This is preliminary evidence that joint compression
    does not leak task information between adapters.
  scope: A single ablation on pairs of natural-instruction tasks with Mistral-7B-Instruct;
    a negative result at this scale, not a privacy guarantee, and the paper flags a fuller
    privacy study as future work.
  evidence: Appendix H.2
- id: context-problem
  kind: context
  text: Compress then Serve frames multi-LoRA serving as a compression problem rather than
    only a systems problem. Scheduling and memory-management optimizations such as S-LoRA
    and vLLM multi-LoRA still degrade when thousands of adapters must be swapped in and out
    of GPU memory.
  scope: Positioning as of the 2025 ICML publication, for LLM inference servers holding one
    base model plus many per-user LoRAs; complementary to rather than a replacement for kernel-level
    work, and the paper's own experiments use vLLM with the Punica kernel.
  evidence: Section 2
- id: context-artifact
  kind: context
  text: Compress then Serve releases a collection of over 1000 LoRA adapters trained on 1000
    natural-instruction tasks for Mistral-7B-Instruct-v0.2. The collection is intended as
    a testbed for work on serving, merging and compressing large adapter collections.
  scope: All tasks are English-language natural instructions with input and output in English;
    all adapters are rank 16 on q_proj, k_proj and v_proj of one base model, so the collection
    does not cover varied ranks, architectures or languages.
  evidence: Section 1, Table 3
qa:
- ask:
    plain: how can one GPU server answer requests for thousands of different fine-tuned versions
      of the same model at once?
    jargon: does joint compression of LoRA adapters raise multi-LoRA serving throughput at
      a fixed GPU memory budget?
    task: how do I keep serving throughput up when my inference server has to swap between
      1000 LoRA adapters?
    practitioner: I host hundreds of per-customer adapters on one base model, should I compress
      them together before serving?
  answered_by:
  - throughput-1000
  - throughput-crossover
- ask:
    plain: if many fine-tuned adapters are squeezed into a shared basis, how much task quality
      is given up?
    jargon: how does reconstruction error of jointly diagonalized LoRAs translate into Rouge-L
      on the adapters' own tasks?
    task: how do I compress a large adapter collection without losing accuracy on the tasks
      each adapter was trained for?
    practitioner: is lossy compression of my LoRA adapters safe, or will my users notice worse
      answers?
  answered_by:
  - lossy-helps
  - recon-threshold
- ask:
    plain: can the settings for squashing many adapters together be picked without running
      the big model at all?
    jargon: can compression rank and cluster count be selected from mean relative reconstruction
      error alone, with no downstream LLM eval?
    task: how do I choose a compression rank and number of clusters for my adapter collection
      cheaply?
    practitioner: do I have to benchmark every compression configuration on my tasks, or is
      a CPU-side error metric enough to decide?
  answered_by:
  - recon-threshold
  - clustering-needed
- ask:
    plain: at what collection size does grouping similar adapters start to matter instead
      of using one shared basis for all of them?
    jargon: when does clustering before joint diagonalization become necessary as the number
      of LoRAs scales from tens to 1000?
    task: I am compressing anywhere from 8 to 1000 adapters, how do I decide between one shared
      basis and clustered bases?
    practitioner: with only a few dozen adapters to serve, is clustering them worth the extra
      complexity?
  answered_by:
  - clustering-needed
  - throughput-crossover
- ask:
    plain: is there a mathematical limit on how much can be recovered when many small adapter
      updates share one basis?
    jargon: what upper bound on reconstructed Frobenius energy applies to joint diagonalization
      of n LoRA update matrices at rank r?
    task: how do I tell in advance whether a set of adapters can be jointly compressed without
      large reconstruction error?
    practitioner: if my adapters were trained on very unrelated tasks, should I expect joint
      compression to be provably lossy?
  answered_by:
  - recon-bound
  - orthogonal-corollary
- ask:
    plain: do separately fine-tuned adapters for different tasks end up sharing structure
      with each other?
    jargon: is the compressibility of trained LoRA updates due to a shared subspace, or would
      random low-rank matrices compress equally well?
    task: how do I check whether the adapters I want to compress together actually share directions
      rather than just being low rank?
    practitioner: does joint compression only pay off because my adapters were trained, or
      would it work on any low-rank matrices?
  answered_by:
  - trained-vs-random
  - orthogonal-corollary
- ask:
    plain: after adapters are compressed together, do they still help on tasks none of them
      was trained for?
    jargon: how do jointly diagonalized LoRAs perform under the LoRA-hub out-of-distribution
      evaluation protocol against uncompressed adapters and the base model?
    task: how do I keep out-of-domain generalization when I compress a pool of 100 adapters
      into a shared basis?
    practitioner: my users send prompts that do not match any single adapter, will compressed
      adapters still beat the plain base model?
  answered_by:
  - ood-lorahub
- ask:
    plain: how good are the 1000 released task-specific adapters for Mistral-7B compared with
      the plain model?
    jargon: what Rouge-L, exact match and test loss do the 1000 released natural-instructions
      LoRAs reach on Mistral-7B-Instruct-v0.2?
    task: where do I get a large collection of trained LoRA adapters to test my own merging
      or serving method on?
    practitioner: can I use the released 1000-adapter Mistral collection as a benchmark, or
      are the adapters too weak to be meaningful?
  answered_by:
  - context-artifact
  - lora-quality
- ask:
    plain: if one customer's fine-tuned adapter is compressed together with another's, can
      ability or information cross between them?
    jargon: does joint compression of LoRAs cause cross-task information leakage between the
      compressed adapters?
    task: how do I check that compressing per-user adapters into a shared basis does not transfer
      one user's task ability to another?
    practitioner: I serve per-tenant LoRAs, is it safe to compress them jointly from a data-isolation
      standpoint?
  answered_by:
  - no-leakage
- ask:
    plain: which work treats hosting thousands of fine-tuned adapters as a compression problem
      rather than a scheduling one?
    jargon: what should I read on the GPU memory bottleneck in multi-LoRA inference beyond
      serving-system optimizations?
    task: where do I start reading if I need to serve far more LoRA adapters than fit in GPU
      memory?
    practitioner: is there a paper and adapter collection I can build on for large-scale multi-LoRA
      serving research?
  answered_by:
  - context-problem
  - context-artifact
terminology:
  JD-Full: Joint diagonalization of a collection of LoRA products BA into a shared orthogonal
    basis U, V of r columns plus an unconstrained r-by-r matrix per adapter.
  JD-Diag: Joint diagonalization of a collection of LoRA products BA into a shared basis U,
    V plus a diagonal r-parameter scaling per adapter, cheaper per adapter than a full r-by-r
    matrix.
  Agreement: The fraction of generations on which a compressed adapter's output exactly matches
    the uncompressed adapter's output, compared model-to-model rather than against ground
    truth.
  Performance relative to LoRA: A method's task metric divided by the uncompressed LoRA's
    metric on the same task, so 1.0 means parity with the original adapter.
  Total Parameter Saved Ratio: One minus the number of parameters after compression divided
    by the number before, computed for a system serving a large number of distinct adapters.
misreadings:
- 'Joint diagonalization is not model merging: it shares only the subspaces U and V across
  adapters while each adapter keeps its own Sigma, so the result is a set of per-task models
  rather than one general model.'
- Reducing the parameter count of LoRA adapters does not by itself speed up inference; compression
  reduces memory load and CPU-to-GPU transfer time but leaves forward-pass latency unchanged,
  and the throughput gains come from fitting more adapters on the GPU.
- 'Lower reconstruction error is not the goal in itself: settings with near-zero Frobenius
  error do not give the best Rouge-L, and moderately lossy reconstruction can match or slightly
  beat them.'
- The 1.6x throughput gain is not universal across collection sizes; an aggressive setting
  such as 25 clusters at rank 15 underperforms the vLLM multi-LoRA baseline when only 32 or
  fewer adapters are served.
- The privacy ablation showing no gain on a co-compressed adapter's task is a single preliminary
  experiment, not a proof that joint compression is leakage-free.
links_extra:
  arxiv: https://arxiv.org/abs/2407.00066
---
