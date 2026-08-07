---
coined: KnOTS
gloss: 'Knowledge Orientation Through SVD: concatenate several LoRA models'' weight updates
  for a layer, take one SVD, and merge the task-specific factors in the shared basis the SVD
  produces'
one_liner: 'KnOTS concatenates several LoRA task-updates for one layer, takes a single SVD,
  and merges the aligned V matrices so that existing merging methods transfer to LoRA models:
  TIES gains 4.3 normalized-accuracy points on eight vision tasks and 2.9 on six NLI tasks,
  while KnOTS is provably a no-op on plain task arithmetic.'
claims:
- id: where-to-start-on-merging-lora-adapters
  kind: context
  text: 'If you have several LoRA adapters for different tasks and want one model that does
    all of them without retraining, this is the paper to read first: it says what goes wrong
    when you average LoRA weights, and gives a preprocessing step that makes the standard
    merging methods work on adapters.'
  scope: An entry-point judgement, which the paper verifies none of -- it is about where this
    work sits for a reader with that problem. It holds for gradient-free merging of adapters
    that share a pretrained base and a set of adapted layers. It is not the place to start
    on merging fully finetuned models, on distillation, or on mixture-of-experts routing,
    which answer the same user problem by other means and are not compared here. Everything
    measured is attention-projection LoRA on CLIP ViTs and on Llama3-8B.
- id: first-alignment-based-lora-merging
  kind: context
  text: 'The paper reframes LoRA merging as an alignment problem rather than an interference
    one: where the methods it compares against ask which parameters conflict, KnOTS asks whether
    the updates share a basis at all, and makes that shared basis something you construct
    with one SVD instead of something you hope the finetuning produced.'
  scope: 'A claim about framing, not a measured result: the paper contains no sentence certifying
    its own standing, and this is the reading of it that its own introduction argues for.
    What is demonstrated is narrower -- that a shared basis obtained by one SVD lets existing
    gradient-free merges do better on LoRA models than they do on the raw updates. Alignment-based
    merging of fully finetuned models predates this work, including RegMean and the activation-matching
    line it builds on, so what is new is the LoRA case and the SVD route to it, not alignment
    as an idea.'
- id: knots-aligns-lora-updates-with-a-joint-svd
  text: 'KnOTS concatenates the task-updates of n LoRA models at a given layer into one matrix
    and takes its SVD, which factors every update as U*Sigma*V(i)^T with U and Sigma shared:
    the task-specific V(i) matrices then all act on the same basis, so an existing merging
    method can be applied to them and the merged update rebuilt as U*Sigma*V(merged)^T.'
  scope: The alignment step itself needs no data, no gradients and no retraining, and adds
    no hyperparameter of its own. Two implementation details matter. Because scale lives in
    Sigma and every row of V(i) has magnitude at most 1, magnitude-based operations such as
    TIES pruning must be computed on Sigma*V(i)^T and then applied to the V(i)^T that get
    merged. And the updates are used in their full-matrix form (ΔW = BA) rather than as the
    LoRA factors A and B, because task-arithmetic on the factors separately produces cross
    terms that multiply one model's B by another's A.
  evidence: Section 4, Figure 1, Section 5.1.0.2, Appendix A
- id: stack-columnwise-and-merge-the-product
  text: 'Two representation choices decide whether the transform works: stack the updates
    column-wise so that U and Sigma are shared and each V(i) is task-specific -- row-wise
    stacking gives each task its own U(i) instead and costs 2.6 points, 65.4 against 68.0
    -- and merge the full product BA rather than the LoRA factors, since task arithmetic on
    A and B separately produces cross terms pairing one model''s B with another model''s A.'
  scope: The direction is one ablation on the eight ViT-B/32 models with KnOTS-TIES, and the
    row-wise variant at 65.4 still beats TIES's 63.7, so the choice tunes the method rather
    than deciding whether it works; the explanation -- that Sigma*V acting through distinct
    U(i) lowers alignment -- is argued from the shape of the decomposition, not measured with
    CKA. The factor argument is algebraic, in Appendix A, and the appendix as rendered gives
    no numerical comparison of the two options. Merging the product also means KnOTS operates
    on matrices of the pretrained layer's shape rather than on the small LoRA factors, so
    the SVD is taken on an O-by-nI matrix per layer -- cheap relative to training, but not
    free.
  evidence: Section 5.4.0.3, Appendix A, Section 3.0.0.3, Section 4
- id: lora-updates-are-misaligned
  text: 'The diagnosis behind the method: on the same eight tasks, the pairwise centered kernel
    alignment between the task-updates of fully finetuned models is very high, while the LoRA-finetuned
    counterparts are dramatically lower -- the LoRA updates extract unrelated features from
    the same inputs -- and KnOTS''s transformed updates are much more aligned again.'
  scope: Reported as three heatmaps in Figure 2 with no numbers in the text, so the finding
    is a direction, not a magnitude; quote it qualitatively. CKA is measured on the activations
    produced by the update alone (a single ΔW), averaged over the attention layers being merged,
    not on the full models. The causal story -- that the low-rank constraint forces each model
    to pick a different subspace, so different LoRAs are unlikely to pick the same one --
    is the authors' speculation, flagged as such. That aligning updates raises mergeability
    is a hypothesis the rest of the paper tests indirectly, through merge accuracy, rather
    than a demonstrated mechanism.
  evidence: Section 3.1, Figure 2, Section 4
- id: orthogonality-is-not-enough
  text: 'Task-vector orthogonality, the standard proxy for whether two models can be merged,
    does not imply they can: the paper''s two-parameter counterexample has task-vectors [1,
    1] and [-1, 1], exactly orthogonal, yet the two models are opposite classifiers, so any
    scaled sum of their weights preserves one model''s predictions and flips the other''s.'
  scope: 'A constructed one-dimensional example, not a measurement -- it shows orthogonality
    is insufficient, not that it is uninformative or that real merges fail this way. The paper''s
    alternative is not a replacement metric but a second lens: activation alignment, measured
    by CKA, following results that models whose layers produce similar intermediate activations
    merge more easily. Neither quantity is validated as a predictor of merge quality here.'
  evidence: Section 3.1.0.1, Section 3.1.0.2
- id: gains-concentrate-on-ties
  text: 'The improvement is uneven across the methods KnOTS wraps: KnOTS-TIES beats TIES by
    4.3 points on eight ViT-B/32 vision tasks (68.0 against 63.7), 3.0 on eight ViT-L/14 models
    (78.2 against 75.2) and 2.9 on six Llama3-8B NLI models (92.9 against 90.0), while KnOTS-DARE-TIES
    beats DARE-TIES by only 0.2, 0.9 and 0.2.'
  scope: 'This is what "improves LoRA merging by up to 4.3%" means: the 4.3 is the best case
    of one pairing on one benchmark, and the DARE-TIES pairing is close to flat everywhere
    -- which is why every analysis experiment in the paper uses KnOTS-TIES. Across scale and
    modality it is the gap that holds rather than the method scaling something the baselines
    cannot: every merging method improves with the larger vision backbone, and the NLI setting
    is easier in normalized terms, every method above 90, so there is less headroom there.
    The six NLI datasets are SNLI, MNLI, SICK, QNLI, RTE and SciTail, and the last three use
    only two of the three labels. One printing inconsistency: the setup section names the
    large vision model ViT-L/16 while the results heading and table say ViT-L/14.'
  evidence: Table 1, Table 2, Table 3, Section 5.2, Section 5.4, Appendix D
- id: knots-on-task-arithmetic-is-task-arithmetic
  text: 'KnOTS cannot help plain task arithmetic, and the paper proves it: since every update
    shares U and Sigma, a weighted sum of the V(i) rebuilt through U*Sigma is identical to
    the weighted sum of the original updates, so KnOTS-TA reduces exactly to TA. Its benefit
    exists only for methods that do something non-linear to the parameters, such as TIES''s
    magnitude pruning and sign resolution.'
  scope: 'An algebraic identity, stated in Section 5.1.0.2, not an empirical finding -- which
    is why no KnOTS-TA row appears in any table. The authors present it as KnOTS generalizing
    TA: the method reduces to the underlying merge when its alignment is not exploited. Read
    together with the previous claim, it says the mechanism is specifically that pruning and
    sign decisions become better posed in the shared basis, which the paper argues but does
    not isolate with an ablation.'
  evidence: Section 5.1.0.2
- id: normalized-accuracy-not-absolute
  text: Every merging number in this paper is a normalized accuracy -- the merged model's
    accuracy on a task divided by that of the model finetuned on it -- so the best eight-task
    vision result, 68.0, means the merged model recovers 68% of finetuned performance, against
    a finetuned average of 84.1% absolute, not that it is 68% accurate.
  scope: 'The convention follows Ilharco et al. (2023) and Yadav et al. (2023) and applies
    to Tables 1, 2 and 3 and to both analysis figures; the joint-task table reports Hits@k
    instead. The finetuned reference averages are 84.1% for ViT-B/32, 92.3% for ViT-L/14 and
    92.9% for the Llama3-8B NLI models. One collision to watch: KnOTS-TIES''s normalized score
    in the NLI setting is 92.9, the same figure as the finetuned models'' average absolute
    accuracy, and the two are unrelated quantities.'
  evidence: Section 5.1.0.3, Table 1, Table 2, Table 3
- id: existing-methods-tie-on-lora-models
  text: On eight ViT-B/32 LoRA models, the three merging methods that assume alignment land
    on the same average -- TA, TIES and DARE-TIES all at 63.7 normalized accuracy -- while
    RegMean, the one baseline that also aligns weights, does worst at 60.9; KnOTS-TIES reaches
    68.0.
  scope: 'Verified against the paper''s per-task columns: every row average recomputes to
    the printed figure. KnOTS-TIES''s gain is concentrated in the datasets the baselines handle
    worst -- MNIST 68.9 against TIES''s 56.8, SVHN 53.8 against 44.6, GTSRB 48.9 against 36.8
    -- and it is slightly behind TIES on SUN397 (95.5 against 96.9) and EuroSAT (49.3 against
    50.0). RegMean''s alignment is a closed-form per-layer regression that requires activations,
    so it is data-dependent in a way KnOTS is not; its poor average here is a result on this
    setting, not a general verdict on it.'
  evidence: Table 1, Section 5.2.0.1
- id: joint-task-benchmark
  text: 'The paper introduces a joint-task benchmark that asks whether a merged model is actually
    general: the eight vision datasets'' labels are pooled and deduplicated into 748 unique
    labels, and every image is classified against all of them with no indication of which
    dataset it came from. KnOTS-TIES leads at every cutoff -- 46.8 / 68.1 / 76.3 for Hits@1/3/5
    against TIES''s 43.6 / 65.3 / 73.9.'
  scope: 'Hits@k rather than accuracy because pooling creates near-synonyms and hyponyms across
    datasets (SUN397''s "islet" against RESISC45''s "island"), so Hits@1 is accuracy and the
    higher cutoffs absorb genuine label ambiguity rather than measuring a harder skill. The
    absolute numbers are not comparable to the per-task tables: these are raw Hits@k over
    the union, not normalized. An ensemble of all eight finetuned models is the worst entry
    here (40.7 at Hits@1), which the authors attribute to models making over-confident predictions
    on data from tasks they were not finetuned on.'
  evidence: Section 5.3, Table 4
- id: gap-holds-across-ranks-and-model-counts
  text: 'The gap is not an artifact of one configuration: KnOTS-TIES beats TIES at every LoRA
    rank tested -- 4, 16, 64, 256 and 768 -- with the largest gain at the lowest rank (64.6
    against 58.6) and around four points still remaining at rank 768, and it stays more than
    4 normalized-accuracy points above both TIES and TA for every number of merged tasks above
    two.'
  scope: 'Both halves are read from figures: Figure 4 for rank, with only the rank-4 pair
    given numerically in the text, and Figure 3 for the count, whose 95% confidence intervals
    are over 28 randomly chosen task combinations. Each merged model is evaluated only on
    the tasks included in its own merge, so the absolute level is not comparable across counts
    -- what the figure supports is the gap. It is one architecture throughout, ViT-B/32, with
    the count sweep at rank 16. The gain surviving at full rank complicates the paper''s own
    motivating story, which explains LoRA''s misalignment by the low-rank constraint: 768
    is full rank for these ViTs'' 768-dimensional features, yet alignment still helps. These
    are LoRA-parameterized models throughout, not the fully finetuned models of Figure 2a.'
  evidence: Section 5.4.0.1, Figure 3, Section 5.4.0.2, Figure 4
- id: data-free-alignment-tuned-merging
  text: 'KnOTS is data-free and gradient-free -- one SVD per layer, no new hyperparameter,
    and the paper''s whole experimental program fits on a single Nvidia A40 with 48GB of VRAM
    -- but the pipeline around it is not: the methods it wraps tune a scaling coefficient,
    TIES''s top-k threshold and DARE''s drop probability on held-out validation data, and
    DARE is run over five seeds with the best-scoring merge kept.'
  scope: 'So "training-free" is about gradients and finetuning, not about needing no labelled
    data at all -- and normalized accuracy also requires knowing each finetuned model''s accuracy.
    The cost argument is architectural rather than benchmarked: no runtime appears in the
    paper, the SVD uses torch.linalg.svd, and the LoRA finetuning of the eight vision and
    six language models is the expensive part and is not counted, because KnOTS assumes those
    models already exist. The paper restricts itself to gradient-free merging and names only
    four such methods (RegMean, TA, TIES, DARE). The grids are given: the scaling coefficient
    over [0.1 ... 1.0], TIES''s top-k over [10 ... 100] percent retained, DARE''s p over [0.99,
    0.9 ... 0.1], and a single coefficient tuned for all models rather than one per task.'
  evidence: Section 3.0.0.1, Section 5.1.0.2, Section 5.2.0.1, Appendix C, Appendix D
- id: gradient-based-fisher-comparison
  text: The one gradient-based method the paper measures, Fisher weight averaging, averages
    63.9 normalized accuracy over the eight ViT-B/32 LoRA models -- level with TIES at 63.7,
    and behind gradient-free KnOTS-TIES at 68.0.
  scope: 'The authors count Fisher as a finetuning method rather than a merging baseline because
    it adds learnable parameters optimized by gradient descent, which is why it sits in an
    appendix instead of the main table. The average conceals a split: Fisher is the strongest
    entry in that table on Cars (84.5) and on GTSRB (55.8, where KnOTS-TIES manages 48.9),
    and its overall deficit comes almost entirely from MNIST (47.8 against 68.9) and SVHN
    (39.2 against 53.8) -- a reading of that table''s own columns, not a gap the paper states.
    One gradient-based method is not a survey of gradient-based merging. The printed search
    grid for Fisher''s scaling term runs [0.1 ... 0.9], yet the configuration reported as
    best uses 1.0; the main grid does include 1.0, so the appendix range is most likely printed
    short.'
  evidence: Appendix E, Table A1, Section 5.2.0.1
- id: what-actually-gets-merged
  text: 'Merging only ever touches LoRA-adapted attention weights -- query, key, value and
    output projections are the only learnable layers in every experiment -- and in the Llama3-8B
    setting only the backbone is merged: each dataset keeps its own task-specific classification
    head, including when the merged model is evaluated.'
  scope: 'So the six-task language result is one shared backbone plus six retained heads,
    not a single end-to-end network, and a reader comparing it to true single-model multitask
    learning is comparing different objects. The vision setting has no equivalent gap for
    the opposite reason: CLIP''s text encoder is frozen throughout and class scores come from
    passing the label strings through it, so there is no per-task head to keep -- which is
    also what makes the pooled 748-label evaluation possible at all. The Llama heads share
    a shape (three classes) but not weights.'
  evidence: Appendix D, Section 5.1.0.1
qa:
- q:
  - What should I read about merging LoRA adapters?
  - Is there a good paper on combining several LoRA models into one?
  - What work established how to merge low-rank adapters without retraining?
  - Where do I start if I want to merge task-specific adapters?
  answers:
  - where-to-start-on-merging-lora-adapters
  - first-alignment-based-lora-merging
  - knots-aligns-lora-updates-with-a-joint-svd
- q:
  - Why does merging LoRA adapters work worse than merging fully finetuned models?
  - Can I merge two LoRA adapters trained on different tasks?
  - Why does task arithmetic fail on LoRA models?
  - What goes wrong when you average LoRA weights from different tasks?
  answers:
  - lora-updates-are-misaligned
  - knots-aligns-lora-updates-with-a-joint-svd
  - existing-methods-tie-on-lora-models
- q:
  - What is KnOTS?
  - How do you use SVD to merge models?
  - How does KnOTS align LoRA models before merging?
  answers:
  - knots-aligns-lora-updates-with-a-joint-svd
  - stack-columnwise-and-merge-the-product
- q:
  - Which model merging method should I use for LoRA adapters?
  - Does KnOTS help every merging method?
  - How much does KnOTS improve TIES merging?
  - Is it worth adding SVD alignment to DARE-TIES?
  answers:
  - gains-concentrate-on-ties
  - knots-on-task-arithmetic-is-task-arithmetic
  - existing-methods-tie-on-lora-models
- q:
  - Does this only work on small vision models, or on LLMs too?
  - Can I merge Llama LoRA adapters with KnOTS?
  - Does SVD-based merging scale to 8B parameter language models?
  - Has this been tested on anything larger than ViT-B/32?
  answers:
  - gains-concentrate-on-ties
  - normalized-accuracy-not-absolute
- q:
  - Does SVD alignment help plain task arithmetic?
  - Why is there no KnOTS-TA result?
  - When does aligning weights before merging make no difference?
  answers:
  - knots-on-task-arithmetic-is-task-arithmetic
  - knots-aligns-lora-updates-with-a-joint-svd
- q:
  - How close does a merged model get to the individual finetuned models?
  - What does normalized accuracy mean in model merging papers?
  - Is a merging score of 68 the same as 68% accuracy?
  answers:
  - normalized-accuracy-not-absolute
  - existing-methods-tie-on-lora-models
  - gains-concentrate-on-ties
- q:
  - Is task vector orthogonality a good predictor of whether models can be merged?
  - Why do orthogonal task vectors still conflict when merged?
  - How do you tell in advance whether two models will merge well?
  answers:
  - orthogonality-is-not-enough
  - lora-updates-are-misaligned
- q:
  - How do you test whether a merged model is actually a general model?
  - What is the joint-task or union evaluation for merged models?
  - Why is per-task evaluation of merged models too easy?
  answers:
  - joint-task-benchmark
  - normalized-accuracy-not-absolute
- q:
  - Does model merging get worse as you add more models?
  - How many LoRA models can I merge into one?
  - Does the benefit of alignment shrink when merging many tasks?
  answers:
  - gap-holds-across-ranks-and-model-counts
  - gains-concentrate-on-ties
- q:
  - What LoRA rank should I use if I plan to merge the adapters later?
  - Does LoRA rank affect mergeability?
  - Is merging harder at very low LoRA rank?
  answers:
  - gap-holds-across-ranks-and-model-counts
  - lora-updates-are-misaligned
- q:
  - Should I merge the LoRA A and B matrices separately or the product?
  - How do you merge LoRA adapters without mixing up their factorizations?
  - Why merge BA instead of A and B?
  answers:
  - stack-columnwise-and-merge-the-product
  - knots-aligns-lora-updates-with-a-joint-svd
- q:
  - Can I merge models without any training data or gradients?
  - Is model merging really training-free?
  - What data do I need to tune a model merge?
  answers:
  - data-free-alignment-tuned-merging
  - gains-concentrate-on-ties
  - normalized-accuracy-not-absolute
- q:
  - Is an ensemble better than a merged model?
  - Why does an ensemble of finetuned models do badly on pooled labels?
  - Should I ensemble my task-specific models instead of merging them?
  answers:
  - joint-task-benchmark
  - orthogonality-is-not-enough
- q:
  - Does the direction of concatenation matter when taking an SVD over several models?
  - What is the right way to stack task updates before decomposing them?
  - How sensitive is SVD-based merging to implementation choices?
  answers:
  - stack-columnwise-and-merge-the-product
  - knots-aligns-lora-updates-with-a-joint-svd
- q:
  - How does KnOTS compare to gradient-based merging methods?
  - Is Fisher weight averaging better than KnOTS?
  - Did they compare against methods that use gradients?
  answers:
  - gradient-based-fisher-comparison
  - data-free-alignment-tuned-merging
- q:
  - Which parameters does KnOTS actually merge?
  - Is the merged model a single network, or does it keep task-specific parts?
  - What does it cost to run KnOTS?
  answers:
  - what-actually-gets-merged
  - data-free-alignment-tuned-merging
  - gains-concentrate-on-ties
misreadings:
- None of the headline numbers are accuracies. They are normalized accuracies -- merged accuracy
  divided by the accuracy of the model finetuned on that task. The best eight-task vision
  result, 68.0, means the merged model recovers 68% of finetuned performance against a finetuned
  average of 84.1% absolute. Merged models here are still well short of the models they were
  built from.
- '"Improves LoRA merging by up to 4.3%" is one pairing on one benchmark. The 4.3 is KnOTS-TIES
  against TIES on eight ViT-B/32 models; the same wrapper applied to DARE-TIES gains 0.2,
  0.9 and 0.2 on the three per-task settings. The method''s value is concentrated in TIES,
  which is why every analysis experiment in the paper uses KnOTS-TIES.'
- 'KnOTS does not improve task arithmetic, and this is proved rather than measured. Because
  all updates share U and Sigma, a weighted sum of the aligned factors rebuilds exactly the
  weighted sum of the original updates, so KnOTS-TA is TA. Any story in which SVD alignment
  helps by itself is wrong: the benefit exists only for merges that prune or resolve signs.'
- The CKA evidence is a figure, not a table. The paper shows that fully finetuned updates
  are highly aligned, LoRA updates dramatically less so, and KnOTS-transformed updates much
  more aligned again -- but prints no CKA values in the text, and the explanation by way of
  the low-rank constraint is explicitly labelled speculation. Quote the direction, not a number.
- 'In the NLI setting KnOTS-TIES scores 92.9 and the six finetuned models average 92.9% absolute
  accuracy. These are unrelated quantities that happen to coincide: the first is a normalized
  score, so the merged model reaches about 92.9% of finetuned performance rather than matching
  it.'
- The joint-task numbers are not comparable to the per-task ones. Hits@1/3/5 over 748 pooled
  labels are raw, not normalized, and Hits@3 and Hits@5 exist because pooling eight label
  sets creates synonyms and hyponyms across datasets -- so the higher cutoffs absorb label
  ambiguity rather than measuring a looser skill.
- '"Data-free and gradient-free" describes the alignment step. The merges themselves tune
  a scaling coefficient, a pruning threshold and DARE''s drop probability on held-out validation
  data, and DARE is run over five random seeds with the best kept -- so the full pipeline
  needs labelled data, just not backpropagation.'
- The orthogonality counterexample is a two-parameter construction showing that orthogonal
  task-vectors can still merge catastrophically. It establishes that orthogonality is insufficient;
  it does not establish that CKA or activation alignment is a validated predictor of merge
  quality, which this paper does not test directly either.
- The improvement is not confined to low rank. KnOTS-TIES beats TIES at every rank from 4
  to 768, and 768 is full rank for these ViTs -- which sits awkwardly with the paper's own
  low-rank explanation for why LoRA models misalign. These are still LoRA-parameterized models,
  so it is not a result about merging fully finetuned models.
- '"KnOTS beats gradient-based merging" holds on average and fails per-task: Fisher weight
  averaging leads the appendix table on Cars and GTSRB, and only loses overall, mostly on
  MNIST and SVHN.'
- '"One merged model does six NLI tasks" -- the backbone is merged, the classification heads
  are not. Each dataset keeps its own head at evaluation time, including for the merged model.'
terminology:
  KnOTS: 'Knowledge Orientation Through SVD. Not a merging method in itself but a transform
    applied before one: concatenate the task-updates of n LoRA models at a layer, take the
    SVD, hand the resulting task-specific V matrices to any existing merging method, and rebuild.
    Named variants are the wrapped method prefixed, as in KnOTS-TIES.'
  task-update / task-vector: The difference between a finetuned model's weights and the pretrained
    weights it started from. "Task-vector" is the flattened form used for cosine-similarity
    arguments; "task-update" is this paper's term for the same thing kept in matrix shape
    per layer, which is what KnOTS operates on.
  normalized accuracy: 'The metric for every merging table here: the merged model''s accuracy
    on a task divided by the accuracy of the model finetuned on that task, averaged over tasks.
    It measures how much of each specialist''s ability survived the merge, so 100 means no
    loss and the absolute number is unrecoverable without the finetuned reference.'
  CKA (centered kernel alignment): A similarity measure between two models' intermediate activations
    on the same inputs, used here on the activations of the task-updates alone rather than
    the full models. High CKA is read as the updates extracting the same kinds of information
    in the same order, which prior work associates with being easier to merge.
  TA / TIES / DARE: The gradient-free merges KnOTS wraps. Task Arithmetic sums the task-updates
    with a tuned scaling coefficient. TIES adds magnitude pruning and sign resolution to reduce
    interference. DARE randomly drops parameters and rescales the rest, usually followed by
    TIES's sign resolution (DARE-TIES).
  joint-task ("Union") evaluation: 'This paper''s new benchmark setting: pool and deduplicate
    the labels of all eight vision datasets into 748 labels, then classify every image against
    all of them with no dataset hint. Contrast with the standard per-task setting, where the
    merged model is shown only the labels of the dataset each image came from.'
  gradient-free merging: 'Merging that requires no backpropagation or retraining, so models
    can be combined on the fly. It is not the same as data-free: the methods here still tune
    scaling coefficients and pruning thresholds against a held-out validation set.'
  FFT (full-rank finetuning): This paper's shorthand for ordinary finetuning of all parameters
    at maximum rank, the setting where existing merging methods already work well. Used throughout
    as the contrast case that motivates the LoRA problem, not as a baseline being competed
    against.
  Fisher weight averaging: Matena & Raffel's merging method, which weights each model's parameters
    by its Fisher information. This paper classifies it as finetuning rather than merging,
    because obtaining those weights requires gradient descent.
  task-specific head: the final classification layer kept separately per dataset in the Llama
    experiments. Only the backbone and its LoRA layers are merged; the heads are not.
links_extra:
  code: https://github.com/gstoica27/KnOTS
---
