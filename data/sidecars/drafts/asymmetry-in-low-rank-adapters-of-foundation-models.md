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

Then promote it:  python scripts/draft_sidecars.py --accept asymmetry-in-low-rank-adapters-of-foundation-models

Stamp: spec=d57862840a90 checks=1 body=03fd2fc0aad7
-->
---
key: zhu2024asymmetry
one_liner: In LoRA's BA update, A extracts input features and B produces the output, so freezing
  A as a random orthonormal matrix and training only B halves the trainable parameters, tightens
  the information-theoretic generalization bound, and matches or beats standard LoRA.
terminology:
  asymmetry in low-rank adapters: The finding that in a LoRA update ΔW = BA the two factors
    play distinct roles — A projects the layer input to r features while B maps those features
    to the layer output — so freezing A and tuning B is not equivalent to freezing B and tuning
    A.
  A_rand: A LoRA configuration in which the down-projection matrix A is initialized as a random
    orthonormal matrix and kept frozen throughout fine-tuning, while only the up-projection
    matrix B is optimized.
  CCA goodness of fit for LoRA matrices: A similarity score ‖U_Y^T U_X‖_F^2 / min{r1, r2}
    between the orthonormal column bases of two learned adapter matrices, chosen because BA
    = (BC)(C^{-1}A) makes the factorization identifiable only up to an invertible r×r transform.
claims:
- id: b-learns-a-does-not
  kind: result
  text: In RoBERTa-large LoRA fine-tuning, the learned B matrices are similar across seeds
    on the same GLUE task and dissimilar across different tasks. The learned A matrices are
    similar whenever initialization is shared, even across different tasks, so B carries the
    task-specific learning.
  scope: RoBERTa-large on MRPC (5 seeds), RTE, STS-B and CoLA; similarity measured by canonical
    correlation analysis goodness of fit on the orthonormal bases of the learned factors.
  evidence: Figure 1
- id: tuning-b-beats-tuning-a-glue
  kind: result
  text: On GLUE with RoBERTa-large, training only B with a frozen random orthonormal A averages
    87.4 at rank 8 and 87.5 at rank 16. Training only A with a frozen random B averages 84.2
    and 85.9, a gap of about 3.2 and 1.6 points at matched parameter counts.
  scope: RoBERTa-large (355M), 7 GLUE tasks, ranks 8 and 16 at 0.3% and 0.8% trainable parameters;
    adapters on query/key/value matrices; largest gaps come from CoLA and RTE.
  evidence: Table 1
- id: matches-lora-and-adalora
  kind: result
  text: Training only B at rank 16 reaches a GLUE average of 87.5 against 87.2 for conventional
    LoRA at rank 8, at the same 0.8% trainable parameters. It statistically matches AdaLoRA's
    87.9, which uses 2.5% of parameters.
  scope: RoBERTa-large on 7 GLUE tasks; rank is doubled to spend the parameters saved by freezing
    A, so the comparison is at matched parameter count rather than matched rank.
  evidence: Table 1
- id: asymmetry-not-initialization
  kind: result
  text: Reversing which LoRA factor is zero-initialized changes GLUE averages by less than
    the standard error, from 87.3 to 87.8 across four initialization schemes with both factors
    trained. The B-over-A advantage is therefore not an artifact of the zero-initialization
    convention.
  scope: RoBERTa-large on 7 GLUE tasks at 0.8% trainable parameters, comparing B̂₀Â_V, B̂₀Â_rand,
    B̂_UÂ₀ and B̂_randÂ₀ where both factors are updated.
  evidence: Table 2
- id: llama2-mmlu
  kind: result
  text: Instruction-tuning Llama-2-7B on Alpaca with only B trained at rank 64 reaches 46.46
    average 5-shot MMLU accuracy using 0.12% of parameters. LoRA at rank 32 reaches 44.76
    with 0.24% of parameters, and the untuned Llama-2-7B reaches 43.14.
  scope: Llama-2-7B tuned on Alpaca, evaluated 5-shot on MMLU; the rank-64 B-only run beats
    standard LoRA on Humanities, STEM and Social Sciences and matches it on Other.
  evidence: Table 4
- id: summarization-bart
  kind: result
  text: With BART-large at rank 16 and 0.44% trainable parameters, tuning only B scores 42.91/19.61/34.64
    ROUGE-1/2/L on XSum versus 42.37/19.30/34.29 for tuning only A, and 43.65/20.62/40.72
    versus 43.38/20.36/40.48 on CNN/DailyMail.
  scope: BART-large, adapters on every query/key/value matrix, 15 epochs, beam length 8 for
    XSum and 4 for CNN/DailyMail; the margins are under 0.6 ROUGE points.
  evidence: Table 3
- id: ood-vit
  kind: result
  text: A ViT fine-tuned with frozen random A and trained B at rank 8 reaches out-of-domain
    DomainBed accuracy of 75.81% on VLCS and 77.72% on OfficeHome. LoRA at rank 8 reaches
    56.43% and 74.46%, and full fine-tuning 64.87% and 63.23%.
  scope: ImageNet-pretrained ViT trained on the LabelMe, Cartoon and Clipart environments
    of VLCS, PACS and Office-Home, 80/20 splits, OOD averaged over held-out environments;
    on PACS, LoRA's 75.58% OOD exceeds the B-only 72.55%.
  evidence: Table 5
- id: generalization-gap
  kind: result
  text: Tuning a single adapter matrix narrows the train-minus-test accuracy gap relative
    to standard LoRA on DomainBed. On VLCS LabelMe the gap is 11.82% for B-only at rank 8
    versus 24.03% for LoRA, and on OfficeHome Product 11.51% versus 22.53%.
  scope: ViT on DomainBed (VLCS, PACS, OfficeHome, TerraIncognita); the trend holds across
    datasets but the gap remains large in absolute terms on hard OOD environments such as
    PACS Sketch and TerraIncognita.
  evidence: Table 10
- id: least-squares-theorem
  kind: result
  text: For multivariate least-squares regression with a rank-r update, freezing A at a random
    orthonormal matrix and solving for B gives loss at most that of freezing B and solving
    for A. The inequality holds with high probability as d/r grows.
  scope: Multivariate linear least squares with zero-mean inputs, U and Q drawn uniformly
    from their Stiefel manifolds, asymptotic in d/r; the advantage of tuning B is large when
    d ≫ r and shrinks as r approaches d.
  evidence: Theorem 4.3 in Section 4.1.1
- id: generalization-bound
  kind: result
  text: An information-theoretic bound on LoRA's generalization error scales with the number
    of tuned parameters. When d_in = d_out the bound for tuning only B is smaller by a factor
    of √2 than for tuning both factors, so a B-only adapter can double its rank at the same
    bound.
  scope: Assumes the loss is σ-sub-Gaussian and each tuned parameter is quantized to q bits,
    following the mutual-information framework of Xu & Raginsky (2017); bounds generalization
    error rather than test accuracy.
  evidence: Lemma 4.5 in Section 4.2.2
- id: half-the-parameters
  kind: result
  text: Fine-tuning only B rather than both LoRA factors reduces trainable parameters by a
    factor d_out/(d_out + d_in), which is exactly 0.5 for square weight matrices such as attention
    query/key/value projections.
  scope: Per adapted parameter matrix at fixed rank r, with A drawn at random and frozen;
    the 50% saving requires d_in = d_out.
  evidence: Section 4.2.1
- id: context-formal-account
  kind: context
  text: Asymmetry in Low-Rank Adapters of Foundation Models gives a theoretical account of
    why LoRA's two factors are not interchangeable. It formalizes an asymmetry that earlier
    methods such as LoRA-FA and VeRA had exploited empirically by freezing or randomizing
    one factor.
  scope: As of the ICML 2024 publication; prior work analyzing LoRA's expressive power addressed
    linearized networks without treating the differing roles of the two factors, the target
    data distribution, or generalization.
qa:
- q:
  - Do the two matrices in a LoRA adapter play different roles?
  - Is the down-projection or the up-projection matrix doing the learning in LoRA?
  - Why is LoRA's B matrix more important than its A matrix?
  answers:
  - b-learns-a-does-not
  - least-squares-theorem
- q:
  - Can I freeze one of the LoRA matrices and still get good accuracy?
  - What happens if I train only the up-projection matrix in LoRA?
  - Is it enough to train just B in a low-rank adapter?
  answers:
  - tuning-b-beats-tuning-a-glue
  - matches-lora-and-adalora
- q:
  - How do I halve the number of trainable parameters in LoRA without losing accuracy?
  - Can freezing a random LoRA factor cut parameter count in half?
  - What is the parameter saving from training only one LoRA factor?
  answers:
  - half-the-parameters
  - matches-lora-and-adalora
- q:
  - Does freezing A in LoRA help out-of-distribution generalization?
  - Which fine-tuning method generalizes better on DomainBed, LoRA or full fine-tuning?
  - Does training a single adapter matrix reduce overfitting in vision transformers?
  answers:
  - ood-vit
  - generalization-gap
- q:
  - Is there a generalization bound for low-rank adaptation?
  - What does information theory say about LoRA's generalization error?
  - Can I double the LoRA rank without hurting the generalization bound?
  answers:
  - generalization-bound
  - half-the-parameters
- q:
  - Does the asymmetry between LoRA matrices come from the zero initialization?
  - Is LoRA's A/B asymmetry just an artifact of initializing B to zero?
  - How much does LoRA initialization choice change GLUE accuracy?
  answers:
  - asymmetry-not-initialization
- q:
  - Does the B-only adapter trick work on 7B-scale language models?
  - What is the MMLU accuracy of Llama-2-7B fine-tuned with a frozen random LoRA down-projection?
  - Does training only one adapter factor scale to Llama-2?
  answers:
  - llama2-mmlu
- q:
  - How does freezing one LoRA factor affect summarization quality?
  - What are the ROUGE scores for BART-large with only one adapter matrix trained?
  - Does the LoRA asymmetry show up in text generation tasks?
  answers:
  - summarization-bart
- q:
  - What should I read to understand why LoRA's two factors are treated differently?
  - Which paper explains theoretically why methods like VeRA and LoRA-FA freeze one adapter
    matrix?
  - Is there a paper on the theory of parameter-efficient fine-tuning asymmetry?
  answers:
  - context-formal-account
  - least-squares-theorem
- q:
  - Which LoRA initialization works best on GLUE?
  - Does orthonormal initialization of the adapter matrices help?
  - Should I use SVD-based or random orthonormal initialization for LoRA factors?
  answers:
  - asymmetry-not-initialization
  - tuning-b-beats-tuning-a-glue
misreadings:
- 'The asymmetry result does not say the A matrix is useless: A still projects the layer input
  to r features, and the claim is that a random orthonormal A works about as well as a tuned
  one, not that A can be removed.'
- Training only B is not uniformly better than standard LoRA at the same rank; the reported
  wins come from spending the halved parameter budget on a doubled rank, and on PACS out-of-domain
  accuracy LoRA at rank 8 still beats the B-only adapter.
- The √2 improvement is in an information-theoretic upper bound on generalization error, not
  a measured reduction in test error, and the bound holds under a sub-Gaussian loss assumption
  with quantized parameters.
- 'Freezing an adapter matrix does not rescue low-rank adaptation on every distribution shift:
  on TerraIncognita all low-rank adapters fit poorly and full fine-tuning is the strongest
  method reported.'
- Reversing the roles of the matrices — initializing A to zero and randomizing B — reverses
  the observed similarity trends, so the asymmetry claim is about the standard LoRA setup
  where A is random and B starts at zero rather than about the letters A and B themselves.
links_extra:
  code: https://github.com/Jiacheng-Zhu-AIML/AsymmetryLoRA
  arxiv: https://arxiv.org/abs/2402.16842
---
