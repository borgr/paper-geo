<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from build/sidecar_tasks.json. Every claim, number
and scope condition below is a machine's reading of the paper and needs your eyes.

THIS PAPER ALREADY HAS A LIVE SIDECAR, and this draft would replace it. Start here:

  diff data/sidecars/asymmetry-in-low-rank-adapters-of-foundation-models.md data/sidecars/drafts/asymmetry-in-low-rank-adapters-of-foundation-models.md

Anything the live file says in your own words is worth keeping over a rewrite of the
same point, so read that diff before the checklist below.

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

Then, if the replacement is the one you want:

  python scripts/draft_sidecars.py --accept asymmetry-in-low-rank-adapters-of-foundation-models --replace

Stamp: spec=2bd8f8ceab46 checks=pass body=79b12047ad61
-->
---
claims:
- id: asymmetry-roles
  kind: context
  text: '"Asymmetry in Low-Rank Adapters of Foundation Models" gives a formal analysis of
    why LoRA''s two factors are not interchangeable. A projects the layer input to r features
    while B maps those features to the layer output, so tuning B matters more than tuning
    A.'
  scope: Analysis covers rank-r updates W0+BA applied multiplicatively to an input-dependent
    vector, covering feedforward and attention layers; earlier work such as VeRA and LoRA-FA
    froze A empirically without a formal account, as of publication in 2024.
- id: tune-b-beats-tune-a-theory
  kind: result
  text: For multivariate linear least squares, freezing A to a random orthonormal matrix and
    tuning B achieves loss at least as low as freezing B and tuning A. The guarantee holds
    with high probability as d/r grows.
  scope: A pre-trained linear model with zero-mean target inputs and b fixed to b_targ, with
    U and Q drawn uniformly from their Stiefel manifolds; asymptotic in d/r, with no guarantee
    at small d/r.
  evidence: Theorem 4.3 (Section 4.1.1), with proof in Appendix B.3
- id: asymmetry-gap-size
  kind: result
  text: The advantage of tuning B over tuning A in low-rank least squares scales as (1 - r/d)
    times Tr[U_X U_X^T Delta^T Delta]. The gap is therefore largest when the layer dimension
    far exceeds the rank, the typical regime in practice.
  scope: Derived in an intuition regime where the input covariance is exactly rank r with
    equal eigenvalues sigma^2, and as d becomes large; the general case is bounded only by
    the inequality behind Theorem 4.3.
  evidence: Section 4.1.1, 'Intuition on asymmetry gap'
- id: generalization-bound-sqrt2
  kind: result
  text: Information-theoretic generalization bounds for LoRA shrink by a factor of sqrt(2)
    when only one factor is tuned instead of both, for square parameter matrices. The rank
    of a B-only adapter can therefore be doubled while still matching standard LoRA's bound.
  scope: A sigma-sub-Gaussian loss, each tuned parameter quantized to q bits, and d_in = d_out
    for the sqrt(2) factor; upper bounds on generalization error rather than measured test
    gaps.
  evidence: Lemma 4.5 (Section 4.2.2), proof in Appendix C
- id: glue-b-vs-a
  kind: result
  text: On GLUE with RoBERTa-large, tuning only B with a frozen random A averages 87.4 at
    r=8 and 87.5 at r=16. Tuning only A with a frozen random B averages 84.2 and 85.9, with
    the largest gaps on CoLA and RTE.
  scope: RoBERTa-large (355M) with adapters on query/key/value matrices, at 0.3% and 0.8%
    trainable parameters, averaged over MNLI, SST-2, MRPC, CoLA, QNLI, RTE and STS-B.
  evidence: Table 1
- id: glue-b-only-matches-adalora
  kind: result
  text: Tuning only B at r=16 reaches a GLUE average of 87.5 with 0.8% trainable parameters,
    above conventional LoRA at r=8 (87.2 with 0.8%). It statistically matches AdaLoRA (87.9),
    which uses 2.5% of parameters.
  scope: RoBERTa-large on the 7 GLUE tasks reported, adapters on query/key/value matrices;
    the rank is doubled to keep the trainable-parameter count equal to LoRA's, and AdaLoRA
    is numerically higher.
  evidence: Table 1
- id: init-not-the-cause
  kind: result
  text: The A/B asymmetry is not an artifact of LoRA's zero-versus-random initialization.
    When both matrices are trained, GLUE averages with RoBERTa-large fall within 87.3 to 87.8
    across 4 initialization schemes, with differences tending to be smaller than the standard
    error.
  scope: RoBERTa-large at 0.8% trainable parameters, comparing B initialized to zero with
    A random or A set to right singular vectors, and A initialized to zero with B random or
    B set to left singular vectors; both factors are trained in all 4 rows.
  evidence: Table 2
- id: summarization-bart
  kind: result
  text: 'On summarization with BART-large, tuning only B beats tuning only A at r=16 on both
    datasets: 42.91/19.61/34.64 versus 42.37/19.30/34.29 ROUGE-1/2/L on XSum, and 43.65/20.62/40.72
    versus 43.38/20.36/40.48 on CNN/DailyMail.'
  scope: BART-large with adapters on every query/key/value matrix, 0.44% trainable parameters,
    beam length 8 for XSum and 4 for CNN/DailyMail; tuning both matrices at r=8 scores higher
    than either single-factor variant.
  evidence: Table 3
- id: mmlu-llama2
  kind: result
  text: With Llama-2-7B instruction-tuned on Alpaca, tuning only B at r=64 reaches 46.46 average
    5-shot MMLU accuracy with 0.12% trainable parameters. LoRA at r=32 reaches 44.76 with
    0.24%, and tuning only A at r=32 reaches 44.51.
  scope: 5-shot MMLU averaged over Humanities, STEM, Social and Other; the B-only r=32 setting
    scores 45.36 average but is below LoRA on the Social subject, and the base Llama-2-7B
    scores 43.14.
  evidence: Table 4
- id: ood-vit
  kind: result
  text: On DomainBed, freezing a random A and tuning only B gives the best out-of-domain accuracy
    on VLCS (75.81% at r=8 versus 56.43% for LoRA) and OfficeHome (77.85% at r=16 versus 74.46%).
    LoRA stays ahead out-of-domain on PACS, at 75.58% versus 73.76%.
  scope: ImageNet-pretrained ViT fine-tuned on the LabelMe, Cartoon and Clipart environments
    of VLCS, PACS and Office-Home, original 80/20 split; out-of-domain numbers averaged across
    held-out environments. On TerraIncognita full fine-tuning is strongest.
  evidence: Table 5, with per-environment breakdown in Table 8 and TerraIncognita in Table
    9
- id: train-test-gap
  kind: result
  text: Tuning a single LoRA factor yields a smaller train-minus-test accuracy gap than standard
    LoRA across DomainBed datasets, for example 11.82% versus 24.03% on the in-domain VLCS
    LabelMe environment for B-only at r=8.
  scope: ViT on VLCS, PACS, OfficeHome and TerraIncognita environments; the trend holds generally
    across environments rather than uniformly in every column, and the comparison is against
    LoRA at r=8.
  evidence: Table 10
- id: b-similarity-task-dependent
  kind: result
  text: Across layers of a LoRA-fine-tuned RoBERTa, learned B matrices are similar when trained
    on the same task with different random seeds and dissimilar across different tasks. Learned
    A matrices are similar whenever initialization is shared, regardless of task.
  scope: 'RoBERTa-large on GLUE: mrpc with 5 random seeds for the same-task setting, and mrpc,
    rte, stsb, cola for the different-task settings, with similarity measured by canonical
    correlation analysis goodness of fit.'
  evidence: Figure 1, with the metric defined in Appendix A
- id: half-parameters
  kind: result
  text: Training only B instead of both LoRA factors reduces trainable parameters by a factor
    of d_out/(d_out+d_in), which is 0.5 for square weight matrices, at the same rank r.
  scope: Per adapted parameter matrix at fixed rank; the saving is on trainable parameters,
    memory, storage and communication, not on the frozen pre-trained model.
  evidence: Section 4.2.1
qa:
- q:
  - Which LoRA matrix matters more to fine-tune, the down-projection or the up-projection?
  - Is it better to train B or A in a low-rank adapter?
  - Can I freeze one of the two LoRA matrices without losing accuracy?
  answers:
  - asymmetry-roles
  - tune-b-beats-tune-a-theory
  - glue-b-vs-a
- q:
  - What do the A and B matrices in LoRA actually do?
  - Why are the two factors of a low-rank adapter not interchangeable?
  - What roles do the LoRA down- and up-projections play during fine-tuning?
  answers:
  - asymmetry-roles
  - b-similarity-task-dependent
- q:
  - Is there a proof that freezing the LoRA input projection is better than freezing the output
    projection?
  - What theory supports training only the up-projection of a low-rank adapter?
  - Does the LoRA asymmetry show up even in linear least-squares models?
  answers:
  - tune-b-beats-tune-a-theory
  - asymmetry-gap-size
- q:
  - Does freezing one LoRA matrix improve generalization bounds?
  - What generalization guarantee do you get from training half of a low-rank adapter?
  - Can the rank be increased for free when only one adapter factor is trained?
  answers:
  - generalization-bound-sqrt2
  - half-parameters
- q:
  - How much does a random frozen A cost on the GLUE benchmark with RoBERTa?
  - What are the GLUE numbers for tuning only B versus only A?
  - Does a LoRA variant with a frozen random projection match AdaLoRA on GLUE?
  answers:
  - glue-b-vs-a
  - glue-b-only-matches-adalora
- q:
  - Is LoRA's asymmetry just a consequence of initializing B to zero and A randomly?
  - Does changing the initialization of the adapter matrices explain the asymmetry?
  - What happens on GLUE when the zero and random initializations of A and B are swapped?
  answers:
  - init-not-the-cause
- q:
  - Does the asymmetry between adapter matrices hold for summarization with BART?
  - What ROUGE scores does tuning only B get on XSum and CNN/DailyMail?
  - Does freezing the LoRA input projection work for text generation?
  answers:
  - summarization-bart
- q:
  - Does the LoRA asymmetry hold for a 7B language model?
  - What MMLU accuracy does Llama-2-7B get when only the B matrices are trained?
  - Can halving LoRA's trainable parameters beat standard LoRA on MMLU?
  answers:
  - mmlu-llama2
- q:
  - Does freezing one LoRA factor help out-of-distribution accuracy on vision transformers?
  - What are the DomainBed results for tuning only the B matrix of a ViT adapter?
  - Which parameter-efficient fine-tuning choice generalizes best across domains for ViTs?
  answers:
  - ood-vit
  - train-test-gap
- q:
  - How many fewer parameters does training only the up-projection of LoRA use?
  - What is the parameter saving from freezing the LoRA down-projection?
  answers:
  - half-parameters
- q:
  - What should I read to understand how LoRA fine-tuning actually works?
  - Which paper explains why methods like VeRA and LoRA-FA can freeze one adapter matrix?
  - What work established the asymmetry between low-rank adapter matrices?
  answers:
  - asymmetry-roles
- q:
  - How were the learned LoRA adapter matrices compared across seeds and GLUE tasks in the
    RoBERTa experiment?
  - What evidence shows the LoRA B matrix encodes the fine-tuning task while A reflects only
    its initialization?
  - Are learned LoRA B matrices similar across random seeds on the same task?
  answers:
  - b-similarity-task-dependent
one_liner: LoRA's two factors have different jobs — A extracts features from the layer input,
  B maps them to the output — so freezing A to a random orthonormal matrix and tuning only
  B halves trainable parameters, tightens generalization bounds by sqrt(2), and matches or
  beats LoRA on RoBERTa, BART, Llama-2 and ViTs.
key: zhu2024asymmetry
links_extra:
  code: https://github.com/Jiacheng-Zhu-AIML/AsymmetryLoRA
  arxiv: https://arxiv.org/abs/2402.16842
misreadings:
- 'The claim is not that the A matrix is useless: A must still project the layer input to
  r features, and it is the tuning of A, not its presence, that the analysis shows to be dispensable.'
- Freezing A does not always beat tuning both factors at the same rank. On BART-large summarization
  at 0.44% parameters, tuning both matrices at r=8 scores higher than either single-factor
  variant at r=16; the gains come from spending the saved parameters on a larger rank.
- The generalization result is a bound on generalization error under a sub-Gaussian loss assumption,
  not a proof that B-only tuning has better test accuracy.
- 'Out-of-domain gains from tuning only B are not universal across DomainBed: LoRA remains
  ahead out-of-domain on PACS, and on TerraIncognita low-rank adapters fit poorly and full
  fine-tuning is the strongest method.'
- Theorem 4.3 is an asymptotic statement holding with high probability as the ratio of layer
  dimension to rank grows; it is not a per-instance guarantee that tuning B beats tuning A
  for any particular layer.
terminology:
  A matrix (LoRA): The r-by-d_in factor of a low-rank weight update BA, which projects a layer's
    input down to r features.
  B matrix (LoRA): The d_out-by-r factor of a low-rank weight update BA, which maps the r
    projected features to the layer's output space.
  A_rand: An initialization scheme in which the LoRA down-projection is set to a random orthonormal
    matrix and kept frozen throughout fine-tuning.
  hat notation (B-hat, A-hat): A hat over a LoRA factor marks that matrix as being updated
    during fine-tuning; a factor without a hat is frozen at its initialization.
  CCA goodness of fit: A similarity score between two matrices computed from the squared Frobenius
    norm of the product of their orthonormal column bases, divided by the smaller rank, making
    it invariant to the invertible reparameterization BA = (BC)(C^{-1}A) of a low-rank adapter.
---
