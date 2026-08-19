<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced via a forced tool call) + 1 repair round. Every claim, number
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

Then promote it:  python scripts/draft_sidecars.py --accept cold-fusion-collaborative-descent-for-distributed-multitask

Stamp: spec=8f05813a4658 checks=pass body=92e6f45e445b
-->
---
key: donyehiya2023coldfusion
coined: ColD Fusion
gloss: 'collaborative descent: repeatedly averaging the weights of models that contributors
  finetuned separately, to keep improving a shared base model'
one_liner: 'ColD Fusion turns ordinary finetuning into distributed multitask learning: contributors
  finetune a shared base model on their own private data, a repository averages the returned
  weights, and the fused model becomes the next iteration''s starting point.'
links_extra:
  models: https://huggingface.co/ibm/ColD-Fusion
  arxiv: https://arxiv.org/abs/2212.01378
terminology:
  ColD multitask: A multitask learning setting in which contributors never share their datasets,
    the central repository performs no training, and communication happens only when a contributor
    finishes finetuning.
  ColD-Frozen: Evaluation of a fused base model by training only the classification head (linear
    probing) while all other weights stay frozen, measuring how much task knowledge the fused
    weights themselves carry.
  Fusing: Combining several finetuned models into one by taking the plain element-wise average
    of their parameters, with no alignment step and no per-model weighting.
  Recycling finetuned models: Reusing the compute and data already spent on published finetuned
    checkpoints to improve the pretrained model those checkpoints started from, instead of
    discarding them.
claims:
- id: roberta-gain
  kind: result
  text: A RoBERTa-base model built by ColD Fusion beats the original RoBERTa-base pretrained
    model by up to 2.33 points on average after finetuning on each of 35 diverse English classification
    datasets separately.
  scope: RoBERTa-base, 30 iterations with 8 contributors sampled per iteration from a pool
    of 36 datasets, 5 random seeds; STSB excluded as a regression task.
  evidence: Section 5.1 and Figure 2(b)
- id: beats-multitask-and-fuse
  kind: result
  text: ColD Fusion's base model improves on pretrained RoBERTa-base by up to 2.33 points,
    against 1.62 points for a standard multitask baseline and 0.92 points for single-round
    model fusing. It also outperforms the MUPPET multitask model.
  scope: Averages over 35 English classification datasets with RoBERTa-base; MUPPET was trained
    on more datasets than the 36-dataset pool and without the no-data-sharing constraint,
    so it is a favourable baseline rather than a matched one.
  evidence: Section 5.1
- id: consistency-vs-muppet
  kind: result
  text: ColD Fusion improves over pretrained RoBERTa-base on 75% of datasets and loses at
    most 1.73 points on its worst dataset. MUPPET, by contrast, helps as many datasets as
    it hurts and is worse by 40 points on some.
  scope: Per-dataset accuracies on the 35-dataset main experiment with RoBERTa-base; MUPPET's
    larger maximum gains on the datasets it does help are not captured by this consistency
    comparison.
  evidence: Section 5.1, Appendix C, Table 1 and Figure 7
- id: unseen-datasets
  kind: result
  text: A base model produced by ColD Fusion helps unseen datasets about as much as datasets
    it was fused on. Under linear probing, however, the advantage on seen datasets is much
    larger than on unseen ones.
  scope: 3-fold cross-validation with 24 seen datasets as contributors and 12 held-out unseen
    datasets per fold, RoBERTa-base; the unseen curve plateaus around iteration 10 and then
    declines slightly.
  evidence: Section 5.2 and Figure 3
- id: few-shot
  kind: result
  text: In a 100-example few-shot setting on unseen datasets, ColD Fusion improves over pretrained
    RoBERTa-base by 6.73 points after 20 iterations.
  scope: Training on 24 full datasets and testing on 12 unseen datasets with 100 labels each,
    averaged over 3 folds, RoBERTa-base.
  evidence: Section 5.3 and Figure 4
- id: contributors-per-iteration
  kind: result
  text: Beyond 2 contributors per iteration, base-model performance from ColD Fusion is hardly
    affected by how many contributors are fused in each round, though more contributors make
    the process more stable.
  scope: Total data fixed, with only the per-iteration sampling changed; 5 randomly sampled
    test datasets for compute reasons, RoBERTa-base. In practice more contributors bring more
    data, which does help.
  evidence: Section 5.4 and Figure 5
- id: more-data-per-contributor
  kind: result
  text: 'Giving each contributor more data brings the fused model closer to centralized full
    finetuning: with 10 contributors on MNLI splits of 1.25K, 2.5K, 5K and 10K examples, the
    largest splits fuse best.'
  scope: Single-dataset MNLI setup with disjoint fixed sub-datasets, evaluated as ColD-Frozen
    with the classification head trained on the first contributor's data only.
  evidence: Section 6 and Figure 6(b)
- id: federated-streaming
  kind: result
  text: ColD Fusion keeps improving when each of 5 contributors samples 5K fresh MNLI examples
    every iteration, showing the scheme accumulates newly added examples rather than only
    coarse dataset identity.
  scope: Single-dataset federated-style simulation on MNLI (392K examples) with RoBERTa-base;
    ColD-Frozen outperforms finetuned ColD in this setup.
  evidence: Section 6 and Figure 6(a)
- id: distributing-cost
  kind: result
  text: Splitting a fixed 50K MNLI training set across more contributors barely changes final
    ColD Fusion performance but slows convergence. Doubling the contributor count while halving
    per-contributor data costs roughly 2 extra iterations.
  scope: Single-dataset MNLI experiment with total data held at 50K and split evenly between
    contributors, RoBERTa-base.
  evidence: Section 6 and Figure 6(d)
- id: dataset-pool-nonmonotonic
  kind: result
  text: 'The number of datasets in the ColD Fusion pool helps non-monotonically: fusing over
    8 datasets is worse than over 4, while 16 and 36 datasets are much better than either.'
  scope: Random permutation of the 36-dataset pool, prefixes of 4, 8, 16 and 36 datasets,
    RoBERTa-base evaluated as a base model.
  evidence: Appendix E and Figure 9
- id: t5-replication
  kind: result
  text: The ColD Fusion trend replicates on T5, where both the finetuned and frozen fused
    models keep improving across iterations as they do on RoBERTa.
  scope: T5 with batch size 256, learning rate 0.0004, a single seed and 5 iterations, language
    model head trained for the frozen variant.
  evidence: Appendix D and Figure 8
- id: context-recycling
  kind: context
  text: ColD Fusion frames the many publicly shared finetuned checkpoints as a resource that
    can be recycled into a continually improving pretrained model, obtaining multitask benefits
    by mixing models instead of mixing datasets.
  scope: English text classification with RoBERTa-base and, at small scale, T5; a method rather
    than a deployed platform, leaving hosting and asynchronous updates to future work.
  evidence: Section 1 and Section 8
- id: context-collaborative-multitask
  kind: context
  text: ColD Fusion defines collaborative multitask learning as a setting where contributors
    keep their data private, the repository only averages weights, and communication happens
    once per finetuning run. It is presented as the first method targeting that setting.
  scope: As stated in the paper's own limitations section at publication in 2023, scaled to
    35 datasets; related low-communication work corresponds to a single ColD Fusion iteration
    on one shared dataset.
  evidence: Section 2.3 and Section 9
- id: compute-cost
  kind: result
  text: Reproducing the main ColD Fusion experiment cost roughly 4,800 A100 GPU hours and
    3.2 TB of storage if every model is saved once. That covers 30 iterations, 8 contributors,
    36 test sets and 5 seeds.
  scope: RoBERTa-base with learning rate 5e-5, batch size 256 and early stopping; contributor
    and test finetunings run in parallel and fusing time is negligible.
  evidence: Appendix B
qa:
- q:
  - How can I combine many separately finetuned models into a better starting point for new
    tasks?
  - Is there a way to get multitask learning benefits without pooling everyone's training
    data?
  - What does ColD Fusion do?
  answers:
  - context-recycling
  - roberta-gain
- q:
  - How much does iterative weight averaging of finetuned models improve over the pretrained
    model?
  - What accuracy gain does ColD Fusion get over RoBERTa-base?
  - Does averaging finetuned checkpoints actually beat plain finetuning of the pretrained
    model?
  answers:
  - roberta-gain
  - beats-multitask-and-fuse
- q:
  - Does repeated model averaging beat conventional multitask training?
  - How does ColD Fusion compare with MUPPET and with one-shot model fusing?
  - Is distributed weight averaging competitive with a centralized multitask baseline?
  answers:
  - beats-multitask-and-fuse
  - consistency-vs-muppet
- q:
  - Which multitask base model is more reliable across individual datasets, MUPPET or ColD
    Fusion?
  - Can a multitask base model hurt performance on some downstream datasets?
  - How consistent are the per-dataset gains from iterative model fusion?
  answers:
  - consistency-vs-muppet
- q:
  - Does a fused multitask base model help on tasks it never saw during training?
  - How well does ColD Fusion transfer to unseen datasets?
  - Are gains from collaborative model averaging limited to the datasets used to build the
    fused base model?
  answers:
  - unseen-datasets
  - few-shot
- q:
  - Does iterative model fusion help in low-resource or few-shot finetuning?
  - How much does ColD Fusion gain with only 100 labelled examples per task?
  - Is a recycled base model especially useful when there is little labelled data?
  answers:
  - few-shot
- q:
  - How many contributors per round are needed for collaborative model averaging to work?
  - Does the number of fused models per iteration matter in ColD Fusion?
  - Is a small number of participants enough for distributed multitask fusing?
  answers:
  - contributors-per-iteration
  - distributing-cost
- q:
  - Does giving each participant more training data help or hurt weight averaging?
  - How does per-contributor dataset size affect how close the fused model gets to centralized
    finetuning?
  - Do large local updates break parameter averaging in ColD Fusion?
  answers:
  - more-data-per-contributor
- q:
  - Can a shared model keep improving as new data keeps arriving from participants?
  - Does ColD Fusion work in a federated-learning-style setting on a single dataset?
  - Does iterative fusing accumulate new examples or just dataset identity?
  answers:
  - federated-streaming
- q:
  - Does adding more tasks always improve a multitask base model?
  - How does the number of datasets in the fusing pool affect ColD Fusion results?
  - Why might multitask training on 8 datasets be worse than on 4?
  answers:
  - dataset-pool-nonmonotonic
- q:
  - Does collaborative weight averaging work on encoder-decoder models like T5?
  - Has ColD Fusion been tested beyond RoBERTa?
  - Is iterative model fusion architecture-specific?
  answers:
  - t5-replication
- q:
  - How expensive is it to reproduce the ColD Fusion experiments?
  - What GPU budget and storage does iterative collaborative finetuning need?
  - Is repeated multitask fusing cheaper or more expensive than ordinary multitask training?
  answers:
  - compute-cost
- q:
  - What should I read first about recycling finetuned models to improve a pretrained model?
  - Which paper established collaborative, data-private multitask learning by weight averaging?
  - What is a good paper on model merging for continually improving base models?
  - Where does ColD Fusion sit relative to model soups and federated learning?
  answers:
  - context-collaborative-multitask
  - context-recycling
misreadings:
- 'ColD Fusion is a training method, not a deployed platform: hosting the models, verifying
  that no malicious or erroneous update was submitted, and asynchronous repository updates
  are all left to future work.'
- ColD Fusion is not cheaper than centralized multitask learning; with many iterations and
  many models it can require more total compute for a given amount of data, and its appeal
  is the collaboration constraints it satisfies rather than efficiency.
- 'The near-identical performance on seen and unseen datasets is not evidence that seen-task
  training was useless: seen datasets are trained on twice, once during fusing iterations
  and again during base-model evaluation, so the parity is expected in this setup.'
- The finding that the number of contributors per iteration barely matters holds only when
  total data is held fixed; adding contributors who bring new data does improve performance.
- ColD Fusion averages model weights only, without any weight alignment, permutation matching
  or per-contributor weighting, so results should not be attributed to a sophisticated merging
  operator.
- 'MUPPET is not shown to be a weak model: it attains larger maximum gains than ColD Fusion
  on the datasets it helps, and the reported advantage of ColD Fusion is in average score
  and consistency.'
---
