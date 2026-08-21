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
- ask:
    plain: can several teams share the benefits of training on each other's tasks without
      ever sharing their training data?
    jargon: how can publicly shared finetuned checkpoints be recycled into an improved pretrained
      model without pooling the underlying datasets?
    task: how do I build a stronger starting checkpoint for my classification tasks by reusing
      other people's finetuned models instead of their data?
    practitioner: my data cannot leave my organization, so can I still get multitask gains
      by contributing only model weights?
  answered_by:
  - context-recycling
  - roberta-gain
- ask:
    plain: how much better does a base model get if you repeatedly average many finetuned
      copies of it back together?
    jargon: what average gain over pretrained RoBERTa-base does iterative weight averaging
      of finetuned models give after downstream finetuning?
    task: if I swap pretrained RoBERTa-base for a recycled fused checkpoint, how much accuracy
      do I gain on my classification datasets?
    practitioner: is starting from a ColD Fusion checkpoint worth it compared with just finetuning
      RoBERTa-base myself?
  answered_by:
  - roberta-gain
  - beats-multitask-and-fuse
- ask:
    plain: does repeatedly averaging separately trained models work as well as training one
      model on all the tasks at once?
    jargon: how does iterative model fusion compare with centralized multitask pretraining
      and with single-round weight averaging as a base model?
    task: should I train a multitask model on the combined datasets or iteratively fuse per-dataset
      finetuned checkpoints?
    practitioner: I already have a multitask baseline like MUPPET, would switching to iterative
      checkpoint fusing actually gain me anything?
  answered_by:
  - beats-multitask-and-fuse
  - consistency-vs-muppet
- ask:
    plain: can a base model that was trained on many tasks end up hurting accuracy on some
      individual datasets?
    jargon: how consistent are per-dataset gains from iteratively fused base models compared
      with a MUPPET-style multitask base model?
    task: how do I pick a multitask starting checkpoint that will not tank one of my datasets?
    practitioner: what is the worst-case downside per dataset if I adopt a fused multitask
      checkpoint instead of the plain pretrained one?
  answered_by:
  - consistency-vs-muppet
- ask:
    plain: does a model built by averaging other people's finetuned models help on tasks that
      were never part of that pool?
    jargon: how well does an iteratively fused base model transfer to datasets held out of
      the fusion pool, under full finetuning versus linear probing?
    task: my task was not in the fusion pool, will a recycled fused checkpoint still help
      me?
    practitioner: should I expect gains on my own dataset if it is nothing like the 35 classification
      datasets used to build the checkpoint?
  answered_by:
  - unseen-datasets
  - few-shot
- ask:
    plain: does a recycled starting model help most when you only have a hundred labelled
      examples?
    jargon: what few-shot gain does an iteratively fused base model give over pretrained RoBERTa-base
      on held-out datasets?
    task: how do I improve accuracy on a new task when I can only label about 100 examples?
    practitioner: I have almost no labelled data, is a fused base checkpoint the cheapest
      way to get better results?
  answered_by:
  - few-shot
- ask:
    plain: how many participants have to send in a model each round for shared weight averaging
      to work?
    jargon: how does the number of contributors fused per iteration affect base-model quality
      and convergence speed in ColD Fusion?
    task: how many partners do I need to recruit per round before collaborative checkpoint
      averaging pays off?
    practitioner: can I run collaborative model fusing with only a couple of participating
      groups?
  answered_by:
  - contributors-per-iteration
  - distributing-cost
- ask:
    plain: is it better for each participant to train on a lot of data or a little before
      their models are averaged?
    jargon: how does per-contributor training set size affect how closely the fused model
      approaches centralized full finetuning?
    task: how much MNLI data should each contributor train on before I average their weights?
    practitioner: will large local finetuning runs break the averaging step, or should I let
      each contributor train on as much data as they have?
  answered_by:
  - more-data-per-contributor
- ask:
    plain: can a shared model keep getting better as participants keep feeding in newly collected
      examples?
    jargon: does iterative weight fusion accumulate fresh examples sampled each round, or
      only coarse dataset identity?
    task: how do I keep improving a shared checkpoint as new labelled data arrives from each
      contributor over time?
    practitioner: in a federated setup where my contributors collect new data every round,
      will repeated fusing keep paying off?
  answered_by:
  - federated-streaming
- ask:
    plain: does throwing more tasks into a shared training pool always make the resulting
      model better?
    jargon: how does the size of the dataset pool affect fused base-model quality, and is
      the relationship monotonic?
    task: how many datasets should I put in the fusion pool to get the best shared checkpoint?
    practitioner: I can fuse over 4, 8 or 36 datasets, does adding more always help me?
  answered_by:
  - dataset-pool-nonmonotonic
- ask:
    plain: does the trick of repeatedly averaging finetuned models work on architectures other
      than a masked language model?
    jargon: does iterative model fusion replicate on an encoder-decoder model such as T5,
      for both finetuned and frozen evaluation?
    task: how do I know whether collaborative weight fusing will transfer to a T5-style seq2seq
      backbone?
    practitioner: my stack is T5, not RoBERTa, is iterative checkpoint fusing still going
      to work for me?
  answered_by:
  - t5-replication
- ask:
    plain: how much computing time and disk space does it take to rerun a large repeated model-averaging
      study?
    jargon: what GPU-hour and storage budget does reproducing the main ColD Fusion experiment
      over 30 iterations and 36 test sets require?
    task: how do I budget GPUs and storage before reproducing an iterative checkpoint-fusing
      experiment?
    practitioner: do I have enough compute to reproduce ColD Fusion, or should I just download
      the released checkpoint?
  answered_by:
  - compute-cost
- ask:
    plain: which paper should I read first about repeatedly recycling shared finetuned models
      into a better starting model?
    jargon: what work introduced collaborative multitask learning by iterative weight averaging
      with private contributor data?
    task: where do I start reading about merging community checkpoints into a continually
      improving pretrained model?
    practitioner: I am surveying model merging and federated learning for a continually improving
      base model, which paper is the reference point for weight-averaging collaboration?
  answered_by:
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
