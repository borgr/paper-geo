---
key: ramesh2026ri
coined: RI (Resolving Interference)
gloss: a pre-merging step that fine-tunes each expert on unlabeled inputs to keep its own-task
  predictions while matching the pretrained model's predictions on every other task
one_liner: Resolving Interference (RI) adapts each fine-tuned expert before merging, distilling
  the original expert's predictions on its own task and the shared pretrained model's predictions
  on other tasks from unlabeled inputs, so any existing merging method combines experts that
  disrupt each other less.
claims:
- id: ri-context-framing
  kind: context
  text: Resolving Interference (RI) is an expert-adaptation step applied before merging, not
    a merging method. Its adapted experts feed into Task Arithmetic, TIES, TSV-M, Iso-CTS,
    AdaMerging, AdaRank or Representation Surgery unchanged, and RI adds no inference-time
    modules.
  scope: Experts fine-tuned from one shared pretrained initialization, with unlabeled inputs
    from each task; CLIP ViT classifiers and Llama-3.1-8B-Instruct and Gemma-2-9B-Instruct
    experts, as of the 2026 v2 preprint.
- id: ri-objective
  kind: context
  text: Resolving Interference (RI) treats merging interference as a fine-tuning problem,
    retraining each expert's task vector to keep its own-task predictions while matching the
    pretrained model's predictions on other tasks. Both targets are KL distillation on unlabeled
    inputs, so no labels and no other experts are needed as teachers.
  scope: Requires unlabeled inputs whose task membership is known; the objective is a surrogate,
    and nonlinear interactions can still arise after parameter merging.
- id: task-vectors-disrupt
  text: Adding the other 7 experts' original task vectors to a fixed SVHN expert drops its
    accuracy from 97.6% to 41.0%. Adding their RI-adapted task vectors instead keeps it at
    94.9%, cutting the loss from 56.6 to 2.7 points.
  evidence: Figure 2, Section 4.1
  scope: 8 CLIP ViT-B/32 vision experts, other-task vectors added at full scale; residual
    degradation remains on some tasks, notably between SVHN and MNIST.
  kind: result
- id: language-gains
  text: RI raises the average score of all 5 merging methods tested on Llama-3.1-8B-Instruct
    and Gemma-2-9B-Instruct experts. The best RI configurations, AdaMerging + RI on Llama
    (68.9) and TSV-M + RI on Gemma (72.1), beat the strongest baselines without RI by 2.9
    and 0.8 points.
  evidence: Table 1
  scope: 5 MergeBench experts per family (IFEval, MBPP+, GSM8K, XSTest, ARC-ml), RI adapted
    on unlabeled test inputs; merging hyperparameters tuned on 100 held-out examples per task.
  kind: result
- id: beats-own-experts
  text: Merged language models built from RI-adapted experts outperform their own constituent
    experts on average, with expert-normalized averages of 102.9 on Llama-3.1-8B-Instruct
    and 104.6 on Gemma-2-9B-Instruct. On Gemma, TSV-M + RI beats each individual expert in
    all 5 domains.
  evidence: Table 1
  scope: Normalized average divides each merged score by the matching expert's score; does
    not hold for the vision benchmarks, where merged models stay below the individual experts.
  kind: result
- id: adaptive-merging-recovery
  text: RI improves the entropy-minimizing merging methods AdaMerging and AdaRank by 10.5
    and 5.9 points on Llama-3.1-8B-Instruct and by 5.8 and 4.1 points on Gemma-2-9B-Instruct.
    AdaMerging's IFEval instruction-following score on Llama rises from 18.1 to 60.1.
  evidence: Table 1
  scope: Layer-wise AdaMerging and AdaRank-TA on the 5-benchmark MergeBench subset; without
    RI both methods fall furthest on instruction following and multilingual reasoning.
  kind: result
- id: vision-gains
  text: On CLIP vision merging, RI improves accuracy in 29 of 30 paired comparisons and gives
    the best merged model in all 6 settings. The lone exception is Iso-CTS on 20-task ViT-B/32,
    which is unchanged.
  evidence: Table 2
  scope: ViT-B/32 and ViT-L/14 image encoders on the 8-, 14- and 20-task benchmarks with fixed
    per-task heads; RI adapted on unlabeled test inputs.
  kind: result
- id: vision-20-task
  text: At 20 vision tasks, Surgery + RI reaches 84.3% on ViT-B/32 and TSV-M + RI reaches
    91.3% on ViT-L/14, beating the strongest baselines without RI by 1.3 and 1.1 points. On
    8 tasks, Iso-CTS + RI on ViT-L/14 reaches 95.2%, within 0.6 of the individual-expert average.
  evidence: Table 2
  scope: CLIP ViT-B/32 and ViT-L/14 expert checkpoints from Wang et al. (2024b), mean top-1
    accuracy over the task suite.
  kind: result
- id: vision-extended
  text: Across 10 merging methods, 3 CLIP architectures and 3 task suites, RI improves accuracy
    in 88 of 89 available paired comparisons. The largest gain is 12.9 points, for WUDI on
    20-task ViT-B/32.
  evidence: Appendix C.1
  scope: ViT-B/32, ViT-B/16 and ViT-L/14 on 8, 14 and 20 tasks, including KnOTS-TIES, WUDI
    and TATR; Iso-CTS on 20-task ViT-B/32 is unchanged and one TA + RI entry is unavailable.
  kind: result
- id: expert-consistency
  text: RI makes merged language models keep more of what their experts got right, raising
    consistency in 20 of 25 method-domain comparisons on Llama-3.1-8B-Instruct. The largest
    gain is on IFEval, where AdaMerging's consistency rises from 25.7% to 78.7%.
  evidence: Figure 5, Appendix D.1
  scope: Consistency is the share of an expert's correctly answered examples the merged model
    also answers correctly; 1 tie and 4 decreases, on multilingual reasoning (TA), code (TIES,
    TSV-M) and safety (TSV-M).
  kind: result
- id: expert-completions
  text: For language models, distilling RI on expert-generated completions as well as prompts
    raises mean scores by 1.2, 0.6 and 2.3 points for Task Arithmetic, TIES and AdaMerging.
    TSV-M is the exception, dropping slightly by 0.2 points.
  evidence: Figure 6
  scope: Llama-3.1-8B-Instruct experts on the 5-benchmark MergeBench subset, compared against
    prompt-only distillation.
  kind: result
- id: data-efficiency
  text: Running RI on only 5% of the unlabeled task data raises merged accuracy by 2.0 points
    for TSV-M and 4.7 points for AdaMerging. More data gives diminishing returns, with TSV-M
    reaching 89.2% on the full set.
  evidence: Figure 8
  scope: 8-task CLIP ViT-B/32 benchmark, fractions of the unlabeled test split from 5% to
    100%; AdaMerging plateaus near 87% from 25% onward.
  kind: result
- id: auxiliary-fallback
  text: When no task inputs are available, RI on unrelated unlabeled images still improves
    merging, by 0.4 points with Gaussian noise up to 1.8 points with MSCOCO or OpenImages.
    Unlabeled task inputs remain best, giving gains of 2.6 to 3.6 points.
  evidence: Figure 7
  scope: 8-task ViT-B/32 with TSV-M at a fixed scaling coefficient of 1.0 over an 85.4% baseline;
    settings where task-specific heads stay separate and unmerged.
  kind: result
- id: compute-cost
  text: RI adaptation of one ViT-B/32 expert takes 6.2 minutes with 2.7 GB peak GPU memory
    at 8 tasks, rising to 9.4 minutes and 4.3 GB at 20 tasks. Experts are adapted independently,
    so the work parallelizes across devices.
  evidence: Table 3
  scope: Single NVIDIA A40, 2,500 steps per expert; one-time teacher-logit caching (3.5 to
    7.4 minutes) is reported separately.
  kind: result
- id: distance-metric
  text: KL-divergence gives the highest average merged accuracy as the RI distance, 84.2%,
    narrowly ahead of MSE (84.1%) and total variation (84.0%), with cross-entropy last at
    83.2%. MSE is best for Iso-CTS and TSV-M, so no metric wins uniformly.
  evidence: Appendix C.2
  scope: Vision setting, averaged over Task Arithmetic, TIES, Iso-CTS and TSV-M.
  kind: result
qa:
- ask:
    plain: can fine-tuned models be prepared before combining them so they conflict less?
    jargon: is there a pre-merge adaptation of task vectors that reduces cross-task interference
      and composes with existing merging operators?
    task: how do I make expert checkpoints more compatible before merging them into one multitask
      model?
    practitioner: can I keep my current merging method and just adapt my experts first?
    adjacent: is there something to run before TIES-Merging that resolves interference at
      the experts themselves rather than in the merge?
  answered_by:
  - ri-context-framing
  - ri-objective
- ask:
    plain: what is a good recent paper on why merged models lose what each fine-tuned model
      learned?
    jargon: which work localizes each task vector's functional influence to its own task distribution
      to reduce merging interference?
    practitioner: where should I start reading if my merged model forgets skills the separate
      experts had?
    adjacent: is there merging work that applies weight disentanglement by distilling each
      expert rather than by tangent-space fine-tuning?
  answered_by:
  - ri-objective
  - task-vectors-disrupt
- ask:
    plain: how badly does adding other models' fine-tuning changes hurt a model that already
      does its task well?
    jargon: how much does a fixed expert's accuracy degrade when other experts' task vectors
      are added, and does adapting those vectors prevent it?
    task: how do I check whether other experts' updates are what is breaking one task in my
      merge?
  answered_by:
  - task-vectors-disrupt
- ask:
    plain: does adapting experts before combining them help when merging large language models?
    jargon: how much does RI improve Task Arithmetic, TIES, TSV-M, AdaMerging and AdaRank
      on Llama-3.1-8B and Gemma-2-9B MergeBench experts?
    task: how do I merge instruction-following, code, math, safety and multilingual LLM experts
      without losing performance?
    practitioner: is a pre-merge adaptation step worth adding when I merge Llama or Gemma
      fine-tunes?
    adjacent: what results does pre-merge expert adaptation get on MergeBench?
  answered_by:
  - language-gains
  - beats-own-experts
- ask:
    plain: can a merged language model actually do better than the separate fine-tuned models
      it was built from?
    jargon: does merging RI-adapted experts exceed the individual experts' normalized average
      score?
    practitioner: could I get one merged model that beats each of my specialist fine-tunes
      on its own task?
  answered_by:
  - beats-own-experts
- ask:
    plain: why does entropy-based adaptive merging wreck instruction following, and can that
      be fixed?
    jargon: does reducing cross-task interference before AdaMerging or AdaRank recover their
      IFEval and multilingual losses?
    task: how do I stop test-time adaptive merging from losing instruction-following ability?
    practitioner: I use AdaMerging on my LLM experts and instruction following collapses --
      will adapting the experts first help?
    adjacent: can pre-merge expert adaptation complement test-time adaptation methods for
      model merging?
  answered_by:
  - adaptive-merging-recovery
  - expert-consistency
- ask:
    plain: how much does adapting experts first improve merging of image classifiers?
    jargon: how does RI change merged accuracy for CLIP ViT-B/32, ViT-B/16 and ViT-L/14 on
      the 8-, 14- and 20-task benchmarks?
    task: how do I get higher accuracy when merging 20 CLIP vision experts?
    practitioner: does pre-merge adaptation still help if I already use TSV-M, Iso-CTS or
      Surgery for my vision models?
  answered_by:
  - vision-gains
  - vision-20-task
  - vision-extended
- ask:
    plain: does merging still keep the right answers each specialist model was getting?
    jargon: what fraction of expert-correct examples does a merged LLM retain with and without
      RI?
    task: how do I measure whether my merged model still solves what each expert solved?
  answered_by:
  - expert-consistency
- ask:
    plain: when adapting a language model before merging, should the training use only prompts
      or also the model's own answers?
    jargon: does distilling on expert-generated completions improve RI over prompt-only distillation
      for autoregressive models?
    practitioner: should I generate completions from my LLM experts to use in pre-merge adaptation?
    adjacent: does sequence-level knowledge distillation on teacher outputs help when adapting
      experts for model merging?
  answered_by:
  - expert-completions
- ask:
    plain: how much unlabeled data do you need to adapt models before merging them?
    jargon: how does RI's merged accuracy scale with the fraction of unlabeled task data used
      for adaptation?
    practitioner: I only have a small slice of unlabeled task data -- is that enough for pre-merge
      adaptation?
  answered_by:
  - data-efficiency
- ask:
    plain: can you improve a model merge without any data from the original tasks?
    jargon: does pre-merge interference reduction work with task-agnostic auxiliary inputs
      such as ImageNet, MSCOCO, synthetic shapes or Gaussian noise?
    task: which unlabeled image source should I use for pre-merge adaptation if I have no
      task inputs?
    adjacent: can unrelated auxiliary images stand in for task data in data-free model merging?
  answered_by:
  - auxiliary-fallback
- ask:
    plain: how long does adapting each model before merging take, and how much GPU memory?
    jargon: what are RI's per-expert runtime and peak GPU memory for ViT-B/32 as the task
      count grows from 8 to 20?
    practitioner: can I afford pre-merge adaptation for 20 experts on a single GPU?
  answered_by:
  - compute-cost
- ask:
    plain: which way of comparing two models' output probabilities works best when adapting
      experts before merging?
    jargon: does KL-divergence beat MSE, total variation and cross-entropy as the RI discrepancy
      objective?
    practitioner: should I use KL or MSE as the distillation loss for pre-merge expert adaptation?
  answered_by:
  - distance-metric
misreadings:
- Resolving Interference (RI) is not a merging algorithm and does not replace TIES, TSV-M
  or AdaMerging; it adapts each expert, after which a standard merging method is still applied.
- RI uses no labels, but its main results do use unlabeled inputs from each task, taken from
  the test split in a test-time adaptation setting. Unrelated auxiliary images are a weaker
  fallback that applies only when task-specific heads stay separate, as in the vision benchmarks.
- 'RI reduces cross-task interference but does not eliminate it: residual degradation remains
  on some vision tasks, notably between SVHN and MNIST.'
- Merged models beating their own experts is a language-model result on the expert-normalized
  average; on the vision benchmarks RI-merged models remain below the individual-expert average,
  for example 82.1% for TSV-M + RI versus 91.3% on 20-task ViT-B/32.
- 'RI''s gains are not uniform: consistency with the experts falls in 4 of 25 method-domain
  comparisons on Llama-3.1-8B-Instruct, and expert completions slightly hurt TSV-M.'
terminology:
  Cross-task interference (ξ): The average, over tasks, of the expected discrepancy between
    an expert's predictive distribution and a merged model's predictive distribution on that
    expert's own task inputs.
  Task-preservation objective: A distillation loss that keeps an adapted expert's predictions
    on its own task's inputs equal to those of the original fine-tuned expert.
  Interference-reduction objective: A distillation loss that makes an adapted expert's predictions
    on other tasks' inputs match those of the shared pretrained model, averaged equally over
    the other tasks.
  RI objective: The task-preservation loss plus λ times the interference-reduction loss, optimized
    starting from the original task vector; λ = 1.0 by default.
  Expert completions: Responses generated by the original language-model expert on its own
    task prompts, used as additional distillation context during RI adaptation.
  Consistency: The percentage of examples an original expert answers correctly that a merged
    model also answers correctly.
  Normalized average: The mean over benchmarks of a merged model's score divided by the corresponding
    expert's score, times 100, so values above 100 exceed the experts on average.
links_extra:
  code: https://github.com/pramesh39/learning-not-to-interfere
---
