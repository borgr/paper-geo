---
key: ramesh2026ri
coined: RI (Resolving Interference)
gloss: a pre-merging adaptation step that uses unlabeled auxiliary images to make each expert
  model's update leave the other tasks' outputs unchanged
one_liner: Resolving Interference (RI) adapts each expert model before merging so that, on
  unlabeled auxiliary images, it reproduces its own task head's outputs while leaving every
  other task head's outputs at their pretrained values — raising the accuracy of existing
  merging methods without any task data.
claims:
- id: ri-context-framing
  kind: context
  text: Resolving Interference (RI) is an adaptation step applied to expert models before
    merging, not a merging method itself. RI therefore composes with existing techniques such
    as Task Arithmetic, TIES, KnOTS, WUDI, Iso-C, Iso-CTS and TSV-M.
  scope: Requires expert models that share a backbone architecture and pretrained initialization,
    plus each task's head; demonstrated on CLIP ViT vision classifiers as of the 2026 preprint.
- id: interference-definition
  kind: context
  text: Resolving Interference defines cross-task interference as the summed distance between
    each expert model's output representations and the merged model's output representations
    under that expert's own task head. An interference value of 0 is sufficient for the merged
    model to match every constituent expert.
  scope: Classification settings where the distance is KL-divergence between predicted distributions;
    computing the metric requires task data even though the RI method itself does not, and
    the sufficiency statement concerns representation equality under each task head.
- id: no-task-data
  kind: context
  text: Resolving Interference reduces merging interference using only unlabeled, task-agnostic
    auxiliary images, with no access to any constituent task's training or validation data.
    Gradient-based merging adaptations such as AdaMerging or Fisher-weighted averaging instead
    assume access to task data.
  scope: Positioning claim about the data-scarce setting; routing-based and task-data-based
    adaptation methods are excluded from comparison by design rather than shown to be worse.
- id: vision-benchmark-gains
  text: Adding RI before merging raises 20-task average accuracy on ViT-B/32 by 8.6 points
    for Task Arithmetic (56.1% to 64.7%) and 9.7 points for TIES (58.0% to 67.7%). The state-of-the-art
    TSV-M baseline gains 3.8 points, from 76.5% to 80.3%.
  evidence: Table 1
  scope: CLIP ViT-B/32 experts from Wang et al. (2024c) on the 20-task vision benchmark, using
    each baseline's recommended default merging hyperparameters and ImageNet as auxiliary
    data.
- id: averaging-exception
  text: 'RI improves every merging method tested on the 8/14/20-task vision benchmarks except
    plain weight averaging. Averaging changes by at most 1.0 point and is sometimes slightly
    worse with RI (ViT-B/16, 8 tasks: 72.3% without versus 71.3% with).'
  evidence: Table 1
  scope: ViT-B/32, ViT-B/16 and ViT-L/14 CLIP experts with default merging hyperparameters;
    averaging's shortfall is attributed to its very small effective scaling coefficient.
- id: averaging-scaling-diagnosis
  text: Averaging+RI in the 20-task ViT-B/32 setting rises from 61.4% at the default averaging
    coefficient of 0.05 to a peak of 64.7% at 0.15. Averaging therefore underuses RI's adapted
    task vectors rather than RI failing.
  evidence: Section B.2
  scope: One sweep of the scaling coefficient from 0.0 to 0.3, ViT-B/32, 20 tasks; accuracy
    degrades again beyond 0.15.
- id: scale-with-tasks
  text: 'Gains from RI grow with the number of merged tasks: TSV-M improves by 1.5, 2.8 and
    3.9 points on the 8-, 14- and 20-task ViT-B/32 settings. Iso-CTS improves by 0.2, 0.9
    and 1.6 points across the same three settings.'
  evidence: Table 1
  scope: CLIP ViT-B/32 experts, default merging hyperparameters; the trend is reported for
    these two merging methods across the three benchmark sizes.
- id: domainnet-ood
  text: On DomainNet, merging with RI beforehand improves mean accuracy over 5 unseen domains
    by 2.3 points for TIES and 2.0 points for weight averaging. The best RI-merged models
    reach up to 3.9 points above the split-specific expert models.
  evidence: Table 2
  scope: Two CLIP ViT-B/32 experts finetuned on the real domain over disjoint halves of DomainNet's
    345 classes; Iso-C and Iso-CTS show no mean gain from RI in this setting.
- id: aux-loss-transfers
  text: Reducing the RI loss on unlabeled auxiliary images produces a corresponding drop in
    cross-task interference measured on the actual task data, with most of the decrease within
    the first 1000 optimization steps. Running RI for 25,000 steps instead of the default
    2500 gains TSV-M a further 1.8 points, reaching 82.1%.
  evidence: Figure 3
  scope: 20-task ViT-B/32 setting with ImageNet auxiliary images, optimized for up to 25,000
    steps; the correspondence is empirical, since auxiliary-data constraints do not guarantee
    the task-data solution.
- id: compute-cost
  text: Adapting one ViT-B/32 expert with RI takes 7m07s in the 8-task setting and 8m50s in
    the 20-task setting at 2500 steps. Peak GPU memory stays constant at 4.8 GB on an NVIDIA
    A40.
  evidence: Table 6
  scope: ViT-B/32 backbone, batch size 128, 2500 steps per expert, experts adapted independently
    and in parallel; ViT-L/14 needs a reduced batch size of 32.
- id: kl-best-metric
  text: KL-divergence is the most effective distance for the RI loss, lifting the average
    of TSV-M, Iso-C and Iso-CTS from 76.4% to 79.0%, versus 78.2% for cross-entropy and 77.7%
    for MSE.
  evidence: Table 3
  scope: 20-task ViT-B/32 setting; all three distances improve on no adaptation, so the choice
    shifts the size of the gain rather than its sign.
- id: aux-source-robustness
  text: RI helps with auxiliary sources ranging from Gaussian noise (+0.4 points) through
    Shapes21k (+1.1) to ImageNet (+1.5), MSCOCO (+1.8) and OpenImages (+1.8), with in-task
    data as an oracle giving +3.3.
  evidence: Figure 4
  scope: 8-task vision setting with TSV-M as the merging method on ViT-B/32; visually diverse
    sources with edges and curves work better, and closer-to-task distributions work best.
- id: hyperparameter-insensitivity
  text: 'Experts adapted with RI are far less sensitive to merging-hyperparameter tuning:
    across 6 merging methods the mean gap between default and task-data-tuned hyperparameters
    is 0.4 points with RI versus 1.8 points without.'
  evidence: Table 5
  scope: 20-task ViT-B/32 setting, hyperparameters tuned on privileged labeled task validation
    data over the sweeps in Section A.2.2.
- id: aux-tuning-fails
  text: Tuning merging hyperparameters with the cross-task interference objective on unlabeled
    auxiliary data is worse than using defaults. The 6-method mean drops from 68.3% to 63.8%
    without RI and from 73.1% to 71.1% with RI.
  evidence: Table 5
  scope: 20-task ViT-B/32 setting with ImageNet auxiliary data; a negative result for hyperparameter
    selection only, not for the RI adaptation objective itself.
- id: pre-merge-beats-post-merge
  text: Adapting each expert before merging beats distilling the already-merged model on the
    same auxiliary data. Merge+Distill_Aux reaches 75.0% for Iso-C and 77.1% for TSV-M on
    20 tasks, against 77.5% and 80.3% for RI.
  evidence: Table 4
  scope: ViT-B/32, 20 tasks, ImageNet auxiliary data; Merge+Distill_Aux is at or near the
    unadapted baselines of 75.1% and 76.5%.
qa:
- q:
  - How can I reduce interference when merging fine-tuned models without access to the training
    data?
  - Is there a way to improve model merging when task data is unavailable?
  - What method fixes merging conflicts using only unlabeled auxiliary images?
  answers:
  - no-task-data
  - ri-context-framing
- q:
  - What should I read about cross-task interference in model merging?
  - Which paper gives a formal definition of interference between merged models?
  - How is cross-task interference defined and measured?
  answers:
  - interference-definition
  - ri-context-framing
- q:
  - How much accuracy does RI add on top of TIES and Task Arithmetic?
  - What are the accuracy gains from Resolving Interference on the 20-task vision benchmark?
  - Does pre-merge adaptation actually improve state-of-the-art merging methods?
  answers:
  - vision-benchmark-gains
  - scale-with-tasks
- q:
  - Does RI help when merging many tasks or only a few?
  - Do the benefits of resolving interference grow with the number of merged experts?
  - Is interference reduction more useful at 20 tasks than at 8?
  answers:
  - scale-with-tasks
- q:
  - Does RI ever fail to help a merging method?
  - Why doesn't Resolving Interference improve plain weight averaging?
  - Which merging baseline gets no benefit from pre-merge adaptation?
  answers:
  - averaging-exception
  - averaging-scaling-diagnosis
- q:
  - Does merging with interference reduction generalize to unseen domains?
  - What are the out-of-distribution results on DomainNet for RI?
  - Do merged models beat their own expert models on unseen image styles?
  answers:
  - domainnet-ood
- q:
  - Does optimizing on auxiliary data really reduce interference on the real tasks?
  - Why would unlabeled out-of-task images help a merged model on its own tasks?
  - How many steps does the RI loss take to converge?
  answers:
  - aux-loss-transfers
- q:
  - What kind of auxiliary data works best for resolving interference?
  - Can Gaussian noise or synthetic images be used instead of real data for pre-merge adaptation?
  - How much does the choice of auxiliary dataset matter for RI?
  answers:
  - aux-source-robustness
- q:
  - How expensive is RI to run per expert model?
  - What is the GPU time and memory cost of resolving interference before merging?
  - Does pre-merge adaptation scale to 20 experts computationally?
  answers:
  - compute-cost
- q:
  - Which distance function should be used for the interference-reduction loss?
  - Is KL-divergence better than MSE for distilling expert outputs during merging adaptation?
  - How much does the distance metric change RI's merging gains?
  answers:
  - kl-best-metric
- q:
  - Do I still need to tune merging hyperparameters after applying RI?
  - How sensitive is merging to the scaling coefficient once interference is resolved?
  - Can merging hyperparameters be tuned without labeled validation data?
  answers:
  - hyperparameter-insensitivity
  - aux-tuning-fails
- q:
  - Is it better to adapt experts before merging or distill the merged model afterwards?
  - Does multitask distillation on auxiliary data work as well as per-expert interference
    reduction?
  - Why adapt each expert instead of the single merged model?
  answers:
  - pre-merge-beats-post-merge
misreadings:
- Resolving Interference is not a merging algorithm and does not replace TIES, Iso-CTS or
  TSV-M; it adapts each expert first, after which a standard merging method is still applied.
- The reported "up to 3.8%" headline is the gain over state-of-the-art TSV-M on 20 ViT-B/32
  tasks; weaker baselines such as Task Arithmetic and TIES gain closer to 9 to 10 points,
  and plain weight averaging gains essentially nothing.
- RI does not eliminate cross-task interference, and the merged models remain well below their
  individual finetuned experts — 80.3% for TSV-M+RI versus 91.3% finetuned on 20 ViT-B/32
  tasks.
- 'Using the cross-task interference objective on auxiliary data as a substitute for validation-based
  hyperparameter tuning does not work: it performs worse than simply keeping the recommended
  defaults.'
- '"No task data needed" applies to the RI adaptation itself, which still requires each task''s
  head and the shared pretrained initialization; the interference metric reported in the analysis
  figures is computed on task data.'
terminology:
  Cross-task interference (ξ): The summed expected distance between an expert model's output
    representations and a merged model's output representations, evaluated under that expert's
    own task head on that task's data.
  RI loss: The sum of a task-preservation term, matching an adapted task vector's outputs
    to the original expert's under its own head, and an interference-reduction term, matching
    its outputs under every other task's head to the pretrained model's, weighted by α/(N−1).
  Task-preservation objective: The requirement that an adapted task vector reproduce its original
    expert's outputs under its own task head.
  Interference-reduction objective: The requirement that an adapted task vector leave the
    outputs of all other tasks' heads equal to those of the pretrained backbone, making it
    functionally orthogonal to those tasks.
  Auxiliary data: Unlabeled, task-agnostic inputs — for example ImageNet, MSCOCO, Shapes21k
    or Gaussian noise — used in place of any constituent task's data during adaptation.
  Merge+Distill_Aux: The alternative baseline of merging first and then distilling the single
    merged model toward each expert on auxiliary data, rather than adapting each expert before
    merging.
links_extra:
  code: https://github.com/pramesh39/resolving_interference
---
