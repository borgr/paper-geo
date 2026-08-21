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
- ask:
    plain: When fine-tuning with a low-rank adapter, which of its two weight matrices is worth
      training?
    jargon: In LoRA, does tuning the up-projection B with a frozen random down-projection
      A beat tuning A with B frozen?
    task: How do I decide which LoRA factor to train when I can only afford to update one
      of them?
    practitioner: If I freeze half my adapter to save memory, should I keep training the input-side
      or the output-side matrix?
  answered_by:
  - asymmetry-roles
  - tune-b-beats-tune-a-theory
  - glue-b-vs-a
- ask:
    plain: What do the two matrices inside a low-rank adapter each learn during fine-tuning?
    jargon: What functional roles do the LoRA down-projection and up-projection play, and
      which one carries task-specific information?
    task: How do I reason about which part of a LoRA adapter encodes the task I fine-tuned
      on?
    practitioner: Should I expect the two halves of my LoRA adapter to be interchangeable
      when I swap or reuse them?
  answered_by:
  - asymmetry-roles
  - b-similarity-task-dependent
- ask:
    plain: Is there any mathematical argument that freezing one half of a low-rank adapter
      is the better choice?
    jargon: Does a least-squares analysis prove that freezing a random orthonormal down-projection
      and optimizing the up-projection attains lower loss than the reverse?
    task: How do I justify training only the output-side factor of a low-rank update beyond
      just benchmark numbers?
    practitioner: Do I have a theoretical reason to trust one-sided LoRA training, or is it
      only an empirical trick?
  answered_by:
  - tune-b-beats-tune-a-theory
  - asymmetry-gap-size
- ask:
    plain: Does training only one of a low-rank adapter's two matrices help the model generalize?
    jargon: How do information-theoretic generalization bounds for LoRA change when a single
      factor is trained instead of both, and can rank be traded against that?
    task: How do I raise the rank of my adapter without weakening its generalization guarantee?
    practitioner: If I train only one adapter factor, can I spend the saved parameters on
      a higher rank?
  answered_by:
  - generalization-bound-sqrt2
  - half-parameters
- ask:
    plain: How well does a language model do on standard sentence-understanding tasks when
      half its adapter stays random and frozen?
    jargon: What GLUE averages does RoBERTa-large reach with B-only versus A-only LoRA training,
      and how do they compare to AdaLoRA?
    task: How do I hit competitive GLUE accuracy while training as few adapter parameters
      as possible?
    practitioner: Can I drop to a frozen random projection on GLUE without losing accuracy
      against fancier adaptive-rank methods?
  answered_by:
  - glue-b-vs-a
  - glue-b-only-matches-adalora
- ask:
    plain: Is the difference between the two adapter matrices just an accident of how each
      one is initialized at the start of training?
    jargon: Does swapping the zero and random initializations of the LoRA factors account
      for the observed A/B asymmetry on GLUE?
    task: How do I rule out initialization as the explanation for one adapter factor mattering
      more than the other?
    practitioner: Should I try a different adapter initialization scheme to get rid of the
      imbalance between the two factors?
  answered_by:
  - init-not-the-cause
- ask:
    plain: Does the advantage of training only one adapter matrix carry over to models that
      generate text, like summarizers?
    jargon: What ROUGE-1/2/L does BART-large reach on XSum and CNN/DailyMail with B-only versus
      A-only LoRA at rank 16?
    task: How do I fine-tune a summarization model with a frozen random adapter projection
      and still keep ROUGE up?
    practitioner: Should I use one-sided adapter training for my abstractive summarization
      fine-tune?
  answered_by:
  - summarization-bart
- ask:
    plain: Does training only one adapter matrix still work when the model has billions of
      parameters?
    jargon: What 5-shot MMLU accuracy does Llama-2-7B instruction-tuned on Alpaca reach with
      B-only LoRA versus standard LoRA?
    task: How do I instruction-tune a 7B model on knowledge benchmarks with roughly half the
      usual adapter parameters?
    practitioner: For a 7B instruction tune, is it safe to train only the output-side adapter
      factor?
  answered_by:
  - mmlu-llama2
- ask:
    plain: Does freezing half of an adapter help an image model hold up on data from a new
      domain?
    jargon: What out-of-domain accuracy does B-only LoRA on a ViT reach on DomainBed, and
      how does the train-test gap compare to standard LoRA?
    task: How do I fine-tune a vision transformer so it transfers to unseen domains rather
      than overfitting the training ones?
    practitioner: For domain shift in my vision model, should I train one adapter factor or
      both?
  answered_by:
  - ood-vit
  - train-test-gap
- ask:
    plain: How much memory or parameter count do you actually save by training only one of
      an adapter's two matrices?
    jargon: What is the reduction in LoRA trainable parameters from updating only the up-projection
      at fixed rank r?
    task: How do I calculate the parameter savings from freezing the down-projection of my
      adapter at a given rank?
    practitioner: Is training a single adapter factor really half the trainable parameters
      for my square weight matrices?
  answered_by:
  - half-parameters
- ask:
    plain: Which paper should I read to understand why some fine-tuning methods leave one
      adapter matrix frozen and random?
    jargon: What work gives the formal analysis of asymmetry between the two low-rank adapter
      factors that frozen-projection LoRA variants rely on?
    task: Where do I start reading on why one half of a low-rank adapter can be left untrained?
    practitioner: Is there a reference I can cite for why frozen random projections in low-rank
      adapters are justified?
  answered_by:
  - asymmetry-roles
- ask:
    plain: Do the learned halves of an adapter look alike when you retrain on the same task
      versus a different task?
    jargon: How similar are learned LoRA B matrices across random seeds on one GLUE task compared
      to across tasks, and what about the A matrices?
    task: How do I tell whether the task information in my fine-tuned adapter sits in the
      down-projection or the up-projection?
    practitioner: Can I reuse one factor of an adapter I trained on another task, or does
      that half depend on the task?
  answered_by:
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
