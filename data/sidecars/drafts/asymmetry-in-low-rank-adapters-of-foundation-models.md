<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from build/sidecar_tasks.json. Every claim, number
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
-->
---
one_liner: 'LoRA''s two factors are not interchangeable: A only has to supply features while
  B has to produce the output, so freezing A at a random orthonormal matrix and training B
  alone matches standard LoRA on GLUE with half the trainable parameters -- and the freed
  budget buys twice the rank.'
claims:
- id: a-extracts-features-b-produces-output
  text: 'In a LoRA update written as a product BA, the two factors do not play symmetric roles:
    A projects the layer''s input down to r features, while B has to turn those r features
    into the output the fine-tuned layer needs. Which matrix you train therefore matters,
    and the paper''s claim is that B is the one that carries the adaptation.'
  scope: 'This is a claim about the roles the factorization forces on each matrix, not about
    anything specific to attention: it applies to any adapted matrix used multiplicatively
    on an input, feedforward or attention. Three kinds of evidence support it -- a similarity
    analysis of trained adapters, exact solutions in a linear least-squares model, and an
    inspection of the gradients in the nonlinear case. All three are consistent, and none
    is a proof about deep networks.'
  evidence: Abstract, Section 1, Section 4, Section 6
- id: freezing-b-loses-output-information
  text: The reason the asymmetry exists is that a frozen B throws away output dimensions while
    a frozen A only throws away input dimensions. With B fixed to a random r-column matrix,
    the best achievable A can only fit the target projected into that random r-dimensional
    output subspace; with A fixed, the fit is an ordinary regression on projected features
    and the output is untouched.
  scope: 'Proved for multivariate linear least squares against a target that is itself a linear
    map, with the frozen factor orthonormal, the bias set to the target''s and the input mean
    zero (Lemmas 4.1 and 4.2). Theorem 4.3 then says the B-tuning loss is no worse, with high
    probability, as the dimension-to-rank ratio grows -- an asymptotic statement whose gap
    is quantified only in a worked example where the input covariance is rank r and isotropic,
    and there it scales as 1 - r/d. For nonlinear losses the argument inspects the gradients
    rather than proving a bound: freezing B multiplies the output-fit term by a random projection,
    and the paper says it therefore expects an asymmetry.'
  evidence: Section 4.1.1, Lemma 4.1, Lemma 4.2, Theorem 4.3, Section 4.1.2, Appendix B
- id: random-frozen-a-nearly-matches-full-lora
  text: 'A random untrained A costs almost nothing: on GLUE with RoBERTa-large, freezing A
    at a random orthonormal matrix and training only B averages 87.4 at rank 8 with half of
    LoRA''s trainable parameters, and 87.5 at rank 16 with the same count as LoRA''s 87.2
    -- statistically level with AdaLoRA''s 87.9, which tunes about three times as many parameters.'
  scope: The margins are inside the run-to-run spread. At matched parameters the rank-16 B-only
    model beats LoRA on four of seven tasks, ties RTE, and loses MNLI and STS-B by 0.2 and
    0.3, with per-task standard errors from 0.1 to 2.6 across three seeds. "Half the parameters"
    is exact only for square matrices, where the saving is d_out/(d_out+d_in) = 0.5; all experiments
    adapt query/key/value matrices, which are square. Note also that the main table's parameter
    column carries percent signs (0.8%, 0.3%, 2.5%) while the appendix prints the same rows
    as 0.8M and 0.3M, and LoRA at rank 8 on a 355M-parameter RoBERTa-large is about 0.8M parameters
    -- roughly 0.2% -- so those figures are counts in millions.
  evidence: Section 5.1, Table 1, Table 7, Section 4.2.1
- id: glue-gap-between-b-only-and-a-only
  text: 'Reversing the roles costs real accuracy: training only A with B frozen averages 85.1
    at rank 8 and 85.9 at rank 16 on GLUE, against 87.4 and 87.5 for training only B at the
    same parameter count.'
  scope: 'The gap is not spread across the benchmark. At rank 8 five of the seven tasks differ
    by 0.4 or less -- A-only is even fractionally ahead on MNLI -- and the whole 2.3-point
    average difference comes from CoLA (67.5 against 58.7) and RTE (82.8 against 77.1), which
    are the two smallest training sets in GLUE; that connection is an observation from the
    table, not one the paper draws. One number to handle carefully: the main table prints
    84.2 as the rank-8 A-only average, but its own seven task scores average 85.1, and the
    appendix''s copy of the same row prints 85.1. Using 84.2 overstates the gap by about a
    point.'
  evidence: Table 1, Table 7, Section 5.1
- id: one-factor-halves-the-parameters
  text: Tuning one factor instead of two reduces trainable parameters by a factor of d_out/(d_out+d_in),
    which is exactly one half when the adapted matrix is square -- so at a fixed budget the
    rank of a B-only adapter can be doubled relative to standard LoRA.
  scope: A counting argument, independent of any experiment. It bounds trainable parameters,
    hence optimizer state and the size of what has to be stored or communicated; it does not
    halve activation memory or forward cost, since the frozen A still participates in the
    forward and backward pass. The paper's recommendation to spend the saving on rank rests
    on the joint claim that A contributes little and that a larger r buys expressive power,
    which is where the empirical support is uneven.
  evidence: Section 4.2.1, Section 4.3, Section 5.1
- id: generalization-bound-is-smaller-by-root-two
  text: An information-theoretic bound on generalization error scales with the square root
    of the number of tuned parameters, so tuning one factor gives a bound smaller than tuning
    both by a factor of the square root of two when input and output dimensions match -- which
    is the paper's formal argument that the rank could be doubled without giving up the guarantee.
  scope: 'Two limits worth stating. First, it is an upper bound, and a smaller upper bound
    is not smaller error; the mechanism is parameter counting, following Xu and Raginsky''s
    framework, and it assumes each tuned parameter is quantized to q bits and the loss is
    sub-Gaussian. Second, the bound sums output dimensions when tuning B and input dimensions
    when tuning A, so for square matrices the two are identical: the bound argues for tuning
    one factor, not for which factor to tune. The preference for B comes entirely from the
    prediction analysis.'
  evidence: Section 4.2.2, Lemma 4.5, Definition 4.4, Appendix C
- id: asymmetry-at-seven-billion-parameters
  text: 'The pattern survives at LLaMA-2-7B scale: instruction-tuned on Alpaca and evaluated
    5-shot on MMLU, a B-only adapter at rank 64 scores 45.1 / 37.7 / 55.1 / 51.1 on humanities,
    STEM, social sciences and other, beating LoRA at rank 32 in all four categories at a comparable
    parameter budget.'
  scope: The rank-matched comparison in the same table is much weaker than the summary suggests.
    At rank 32 the A-only row is higher than the B-only row on humanities, social sciences
    and other, and lower only on STEM, so at equal rank the categories favour A-only; the
    B-only rank-32 row wins only on the reported average, and that average sits about 2.2
    points above what its four category scores imply, where every other row in the table is
    consistent within half a point. The clean result is the rank-64 row. The parameter column
    also lists 0.12% for both the rank-32 and rank-64 B-only rows, which cannot both be right,
    so read it as the intended matched-budget comparison rather than literally.
  evidence: Section 5.3, Table 4
- id: asymmetry-in-summarization
  text: 'The direction holds in generation too: BART-large adapters on XSum and CNN/DailyMail
    score 42.91 / 19.61 / 34.64 and 43.65 / 20.62 / 40.72 ROUGE-1/2/L when B is trained and
    A frozen, against 42.37 / 19.30 / 34.29 and 43.38 / 20.36 / 40.48 when the roles are reversed.'
  scope: Six comparisons, all in the same direction, with margins of 0.2 to 0.5 ROUGE -- consistent
    but small, and reported as single runs without variance, unlike the GLUE tables. The last
    two rows of the same table tune both matrices under different initializations, which the
    paper reads as evidence that the asymmetry is not an initialization artifact; those rows
    are also the strongest in the table, which is the reversal recorded separately.
  evidence: Section 5.2, Table 3, Appendix D
- id: matched-parameter-advantage-does-not-generalize
  text: The trade -- freeze A, spend the saving on rank -- pays off on GLUE but not everywhere.
    On summarization at an identical parameter budget, tuning both matrices at rank 8 beats
    the B-only rank-16 adapter on all six ROUGE numbers (43.78 / 20.47 / 35.53 against 42.91
    / 19.61 / 34.64 on XSum). On PACS, the B-only adapter's out-of-domain accuracy is 72.6
    against LoRA's 75.6, and on TerraIncognita low-rank adapters generally fit poorly and
    full fine-tuning wins.
  scope: The asymmetry between the two factors is the robust part of the paper and holds in
    every experiment; what varies is whether one factor at double rank beats two factors at
    single rank. The summarization comparison is read off the paper's own table -- it notes
    those rows only to rule out an initialization explanation and does not remark that they
    lead. On TerraIncognita, standard LoRA also beats both single-factor variants on two of
    four environments. Whether the rank-doubling recommendation is worth taking therefore
    depends on the task, and nothing here predicts which way it will go.
  evidence: Table 3, Table 5, Table 9, Appendix F
- id: vision-out-of-domain-gains
  text: 'In domain generalization with a ViT on DomainBed, freezing a random A and training
    B gives the best out-of-domain accuracy on two of three datasets: 75.8 on VLCS against
    56.4 for LoRA, 71.7 for linear probing and 64.9 for full fine-tuning, and 77.7 on OfficeHome
    against 74.5 for LoRA and 63.2 for full fine-tuning, at roughly two-thirds of LoRA''s
    trainable parameters.'
  scope: 'The 19-point VLCS margin is one environment''s doing: LoRA scores 44.6 on Caltech101,
    far below even linear probing''s 90.7, while the B-only adapter gets 93.2, and the other
    two held-out environments differ by about a point each. So the headline is as much about
    standard LoRA failing on that environment as about the method winning. PACS goes the other
    way (72.6 against 75.6), driven by the Sketch environment where LoRA leads 49.9 to 40.4.
    Each dataset trains on a single in-domain environment -- LabelMe, Cartoon, Clipart --
    with the standard 80/20 split, and the caption calls the columns test error although the
    numbers are accuracies.'
  evidence: Section 5.4, Table 5, Table 8
- id: narrower-train-test-gap
  text: 'The generalization story shows up directly as a smaller distance between training
    and test accuracy: tuning one factor narrows the train-minus-test gap relative to standard
    LoRA on most held-out environments, dramatically so on VLCS, where LoRA''s gap on Caltech101
    is 52.9 points against the B-only adapter''s -1.7.'
  scope: The paper describes this as consistent across all datasets; the per-environment table
    has exceptions. It holds on every VLCS and OfficeHome environment, but on PACS Sketch
    the B-only gap is larger (57.3 against LoRA's 49.7) and on TerraIncognita L100 it is larger
    too (64.2 against 47.5). A smaller train-test gap also does not by itself mean better
    test accuracy -- linear probing has the smallest gaps of any method and the worst accuracy
    on most environments. This is the empirical counterpart of the parameter-counting bound,
    not a test of it.
  evidence: Section 5.4, Table 10, Appendix F
- id: frozen-factor-initialization-can-break-training
  text: 'How the frozen matrix is drawn matters more than the paper''s summary implies: orthogonal
    initialization gives the best results throughout, and freezing B at LoRA''s original uniform
    initialization while training A can stop the model learning at all -- 34.5 on MNLI and
    0.0 Matthews correlation on CoLA, an average of 64.4 against 85.1 for the same configuration
    with an orthonormal B.'
  scope: 'This is the appendix table, and it cuts against the paper''s expectation that random
    orthonormal and random uniform initializations should be essentially equivalent for a
    tall random matrix -- an argument about column orthogonality that does not control the
    scale of the frozen factor. It affects the A-only configurations, which is to say the
    side of the comparison the paper argues against, so it does not threaten the main conclusion;
    it does mean the size of the reported gap depends on a choice the summary treats as immaterial.
    When both matrices are trained, initialization barely matters: four schemes land between
    87.3 and 87.8.'
  evidence: Table 7, Table 2, Section 5
- id: the-recipe-was-known-the-explanation-is-new
  text: Freezing A and training B was already in use before this paper -- as LoRA-FA, and
    in the same family as methods that rescale frozen random factors or learn combinations
    of fixed random bases. What is new here is the account of why it works, the generalization
    bound that follows, and the resulting advice to spend the saved parameters on a higher
    rank.
  scope: 'The paper is explicit that it confirms and builds on prior empirical observations,
    and its own appendix bears this out: the row that freezes A at LoRA''s uniform initialization
    and trains B reproduces the LoRA-FA baseline almost cell for cell. So a reader should
    not take the recipe as the contribution. The gap the paper identifies in prior work is
    that nearly all recent methods treat the two matrices asymmetrically in initialization
    or freezing without investigating the asymmetry formally, and that the one prior study
    of LoRA''s expressive power considers neither the fine-tuning data distribution nor generalization
    nor the differing roles of the factors.'
  evidence: Section 2, Section 1, Table 1, Table 7
- id: similarity-evidence-depends-on-initialization
  text: The motivating observation is that trained B matrices resemble each other when the
    task is shared and diverge when it changes, while trained A matrices resemble each other
    whenever the initialization is shared regardless of task -- measured across the layers
    of a RoBERTa model with a similarity score built to be invariant to LoRA's reparameterization
    ambiguity.
  scope: Reported as heatmaps with no numbers in the text, over four GLUE tasks and five seeds
    on MRPC. Under the standard initialization A starts random and B starts at zero, so the
    two matrices do not begin symmetrically. The appendix reverses that -- A at zero, B random
    -- and reports that the trend of differences reverses too, which it attributes to the
    known importance of initialization while arguing the conclusion about B still follows
    from comparing average similarity across panels. The figure is therefore motivation for
    the theory rather than independent evidence, and part of what it shows is an effect of
    which matrix starts at zero.
  evidence: Section 3, Figure 1, Appendix A, Appendix A.1, Figure 2
- id: how-it-was-run
  text: 'Four backbones, four settings: RoBERTa-large (355M) on GLUE, BART-large on XSum and
    CNN/DailyMail, LLaMA-2-7B instruction-tuned on Alpaca and evaluated 5-shot on MMLU''s
    57 tasks, and an ImageNet-pretrained ViT (86.4M) on DomainBed. Adapters are placed on
    every query/key/value matrix with the scaling coefficient fixed at twice the rank, and
    matrix names carry subscripts for random orthonormal, zero and LoRA''s original uniform
    initialization.'
  scope: GLUE numbers are means with standard errors over seeds; the summarization and MMLU
    tables report single runs. Summarization uses learning rate 5e-4 and batch size 48 with
    beam 8 for XSum and beam 4 for CNN/DailyMail, though the section says 15 epochs while
    the appendix table lists 25 for XSum and 15 for CNN/DailyMail. DomainBed trains on one
    environment per dataset with an 80/20 split and tests on the rest; TerraIncognita runs
    20,000 steps. Baselines are full fine-tuning, linear probing, IA3, LoRA, AdaLoRA and LoRA-FA,
    all implemented on HuggingFace Transformers.
  evidence: Section 5, Section 5.2, Section 5.4, Table 6, Table 9
qa:
- q:
  - Do I need to train both LoRA matrices?
  - Can I freeze one of the LoRA matrices?
  - Is it enough to train only the B matrix in LoRA?
  - Which LoRA matrix actually matters?
  answers:
  - a-extracts-features-b-produces-output
  - random-frozen-a-nearly-matches-full-lora
  - glue-gap-between-b-only-and-a-only
- q:
  - Why is B more important than A in LoRA?
  - What do the A and B matrices in a LoRA adapter do?
  - Is there a theoretical reason to prefer tuning B over A?
  answers:
  - a-extracts-features-b-produces-output
  - freezing-b-loses-output-information
  - generalization-bound-is-smaller-by-root-two
- q:
  - How much accuracy do I lose by freezing A at random?
  - Does a random untrained A hurt LoRA?
  - What happens if you freeze the wrong LoRA matrix?
  answers:
  - random-frozen-a-nearly-matches-full-lora
  - glue-gap-between-b-only-and-a-only
  - frozen-factor-initialization-can-break-training
- q:
  - How do I halve LoRA's trainable parameters?
  - Can I double the LoRA rank for free?
  - What is the cheapest way to keep LoRA quality at a smaller parameter budget?
  answers:
  - one-factor-halves-the-parameters
  - random-frozen-a-nearly-matches-full-lora
  - matched-parameter-advantage-does-not-generalize
- q:
  - Does freezing one LoRA matrix improve generalization?
  - Is there a generalization bound for low-rank adapters?
  - Does tuning fewer parameters give a better guarantee?
  answers:
  - generalization-bound-is-smaller-by-root-two
  - narrower-train-test-gap
  - one-factor-halves-the-parameters
- q:
  - Does LoRA overfit when fine-tuning out of distribution?
  - Which fine-tuning method generalizes best out of domain?
  - How does LoRA compare to linear probing and full fine-tuning on DomainBed?
  answers:
  - vision-out-of-domain-gains
  - narrower-train-test-gap
  - matched-parameter-advantage-does-not-generalize
- q:
  - Does the LoRA asymmetry hold for large language models?
  - Does freezing A work on LLaMA-2?
  - Has this been tested beyond small encoder models?
  answers:
  - asymmetry-at-seven-billion-parameters
  - asymmetry-in-summarization
  - how-it-was-run
- q:
  - Does the asymmetry hold for generation tasks?
  - Does freezing A work for summarization?
  - Which LoRA variant is best for BART fine-tuning?
  answers:
  - asymmetry-in-summarization
  - matched-parameter-advantage-does-not-generalize
  - how-it-was-run
- q:
  - When should I not freeze A and double the rank?
  - Are there tasks where standard LoRA beats training only B?
  - Does this trick always work?
  answers:
  - matched-parameter-advantage-does-not-generalize
  - vision-out-of-domain-gains
  - narrower-train-test-gap
- q:
  - How should I initialize a frozen LoRA matrix?
  - Does orthonormal initialization matter for LoRA adapters?
  - Why does my LoRA run fail to train when I freeze a matrix?
  answers:
  - frozen-factor-initialization-can-break-training
  - random-frozen-a-nearly-matches-full-lora
  - similarity-evidence-depends-on-initialization
- q:
  - How is this different from LoRA-FA or VeRA?
  - Was freezing A already known before this paper?
  - What is the actual contribution of the asymmetry paper?
  answers:
  - the-recipe-was-known-the-explanation-is-new
  - freezing-b-loses-output-information
  - generalization-bound-is-smaller-by-root-two
- q:
  - What evidence is there that B carries the task and A does not?
  - Do trained LoRA A matrices depend on the task?
  - How do you compare two LoRA adapters given that BA is not unique?
  answers:
  - similarity-evidence-depends-on-initialization
  - a-extracts-features-b-produces-output
  - frozen-factor-initialization-can-break-training
- q:
  - How strong is the theory behind LoRA asymmetry?
  - Is the asymmetry proved or just observed?
  - What assumptions does the asymmetry proof make?
  answers:
  - freezing-b-loses-output-information
  - generalization-bound-is-smaller-by-root-two
  - a-extracts-features-b-produces-output
- q:
  - Which models and benchmarks were used?
  - What hyperparameters were used for these LoRA experiments?
  - Where in the network are the adapters placed?
  answers:
  - how-it-was-run
  - random-frozen-a-nearly-matches-full-lora
  - vision-out-of-domain-gains
misreadings:
- '"A random untrained A performs nearly as well as a fine-tuned one" is about A specifically,
  not about randomness in general. Reversing the roles -- freezing B at random and training
  A -- costs 2.3 points of GLUE average at rank 8, and with an ill-scaled frozen B it can
  stop training entirely (0.0 Matthews correlation on CoLA).'
- The rank-8 A-only GLUE average is printed as 84.2 in the main table, but its own seven task
  scores average 85.1, which is also what the appendix prints for that row. Quoting 84.2 makes
  the asymmetry look about a point larger than the paper's own cells support.
- The GLUE gap is not a broad degradation. Five of the seven tasks are within 0.4 at rank
  8 -- A-only is even slightly ahead on MNLI -- and the entire difference comes from CoLA
  and RTE, the two smallest training sets in the benchmark.
- The generalization bound does not favour B over A. It sums output dimensions for B-only
  tuning and input dimensions for A-only, so for the square attention matrices used throughout,
  the two bounds are identical. The bound argues for tuning one factor rather than two; the
  case for choosing B rests entirely on the prediction analysis.
- A smaller bound is not smaller error. Lemma 4.5 is an information-theoretic upper bound
  that scales with the count of tuned parameters, assumes a sub-Gaussian loss and q-bit quantized
  parameters, and says nothing about which of two methods will actually generalize better.
- Theorem 4.3 is a statement about linear least squares against a linear target, holding with
  high probability in the limit of large dimension-to-rank ratio. For nonlinear losses the
  paper inspects gradients and says it expects an asymmetry -- it does not prove one.
- '"Doubling the rank of a B-only adapter beats standard LoRA at equal parameters" is a GLUE
  result. On summarization the paper''s own table has both matrices at rank 8 ahead of B-only
  at rank 16 on all six ROUGE numbers at the same budget, and on PACS the B-only adapter trails
  LoRA out of domain.'
- The 19-point out-of-domain margin on VLCS rests on one environment. Standard LoRA scores
  44.6 on Caltech101, below even linear probing's 90.7, while the B-only adapter reaches 93.2;
  on the other two held-out environments the two differ by about a point. The number describes
  a LoRA failure as much as a method win.
- '"Fine-tuning a single matrix consistently gives smaller train-test gaps" has exceptions
  in the per-environment table: PACS Sketch (57.3 against LoRA''s 49.7) and TerraIncognita
  L100 (64.2 against 47.5). And on TerraIncognita as a whole, low-rank adapters fit poorly
  and full fine-tuning is the strongest method.'
- Freezing A and training B is not this paper's invention -- it is LoRA-FA, and the appendix's
  version of that configuration reproduces the LoRA-FA baseline nearly cell for cell. The
  contribution is the explanation of why the roles differ, the bound that follows, and the
  rank-doubling consequence.
- The parameter column in the main GLUE table carries percent signs, but 0.8% of RoBERTa-large's
  355M parameters is not what LoRA at rank 8 tunes -- that is about 0.8M, or roughly 0.2%.
  The appendix prints the same rows as 0.8M and 0.3M, so read those figures as counts in millions.
- Halving trainable parameters is not halving memory or compute. The frozen A still runs in
  the forward and backward pass; what shrinks is the optimizer state and whatever has to be
  stored or shipped -- which is the point for serving many adapters, not for making a single
  fine-tune faster.
terminology:
  LoRA: 'Low-Rank Adaptation: fine-tune a frozen pretrained weight matrix by adding a low-rank
    product BA, training only the two small factors. A has r rows and as many columns as the
    layer''s input; B has r columns and as many rows as its output.'
  asymmetry (of LoRA factors): 'The observation that the two factors of a low-rank update
    play different roles and are not interchangeable: A projects the input to r features,
    B maps those features to the output. Consequently freezing A and training B is not the
    mirror image of freezing B and training A.'
  B-only tuning: Sampling A once as a random orthonormal matrix, freezing it, and training
    only B. Halves the trainable parameters for a square layer, and is the configuration this
    paper recommends -- optionally at double the rank to spend the saving.
  random orthonormal initialization: Drawing the frozen factor with orthonormal columns rather
    than from the uniform scheme LoRA uses by default. It gives the best results in every
    table here, and in the paper's notation is the rand subscript, distinct from km for LoRA's
    original uniform initialization.
  canonical correlation similarity: 'The score used to compare two trained adapters: project
    each matrix onto an orthonormal basis of its columns and measure the overlap. Chosen because
    BA equals (BC)(C-inverse A) for any invertible C, so any meaningful comparison of LoRA
    factors must be invariant to that reparameterization.'
  information-theoretic generalization bound: An upper bound on the gap between test and training
    risk that grows with the number of bits in the tuned parameters, following Xu and Raginsky.
    Here it grows with the rank times the summed dimensions of the adapted matrices, which
    is why tuning one factor bounds it more tightly than tuning two.
  Stiefel manifold: The set of matrices with orthonormal columns. The theorem draws the frozen
    factor uniformly from it, which is what makes "a random A" a precise statement rather
    than a choice of initializer.
  DomainBed: A domain-generalization testbed of image datasets, each split into environments
    that share classes but differ in style. Training on one environment and testing on the
    others separates in-domain accuracy from out-of-domain accuracy, which is what makes it
    the right place to test a generalization claim.
  AdaLoRA: A LoRA variant that reallocates rank across layers during training. It is the strongest
    GLUE baseline here at 87.9 average, using roughly three times the trainable parameters
    of the B-only adapter it statistically ties with.
  LoRA-FA: A prior method that freezes A and trains B for memory efficiency. It is both a
    baseline in this paper and, effectively, the configuration the paper analyzes -- which
    is why the contribution is the explanation and the rank-doubling consequence rather than
    the recipe.
---
