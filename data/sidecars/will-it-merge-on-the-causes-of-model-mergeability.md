---
key: rahamim2026mergeability
one_liner: Mergeability is defined as how much of a model update's knowledge survives being
  merged with randomly sampled other updates, and across PopQA and Lots-of-LoRAs it tracks
  the base model's prior knowledge of the finetuning data far more than any weight-level property.
claims:
- id: mergeability-exists
  kind: result
  text: 'Mergeability is a non-trivial trait of individual model updates: the empirical distribution
    of mergeability scores for Llama-3.2-3B LoRA adapters on PopQA departs from a binomial
    baseline with a fixed per-merge success rate.'
  scope: PopQA example-level LoRA adapters on Llama-3.2-3B, merged with Knots; the binomial
    baseline uses the observed overall success rate. Also reproduced for Qwen2.5-3B and for
    full finetuning with mean and TIES merging.
  evidence: Figure 2
- id: base-knowledge-popqa
  kind: result
  text: On PopQA, the base model's probability gap between its top-ranked answer and the correct
    answer decreases as mergeability increases. Examples needing only a small decision-boundary
    adjustment are the ones whose LoRA updates survive merging.
  scope: Llama-3.2-3B on PopQA in 8-option multiple-choice format, k=4 shot, per-example LoRA
    adapters (rank 64, mlp.up_proj, single layer) merged with Knots; replicated on Qwen2.5-3B
    and at LoRA ranks 8 and 256, where the r=256 trend is weaker.
  evidence: Figure 3
- id: base-knowledge-lots-of-loras
  kind: result
  text: On the Lots-of-LoRAs collection, tasks with higher average base model accuracy have
    higher mergeability scores. Tasks the base model already handles well lose less performance
    when their adapters are merged with adapters from other tasks.
  scope: Mistral-7B-Instruct-v0.2, 81 Lots-of-LoRAs tasks whose finetuned adapter reaches
    at least 99% accuracy, exact-match scoring, Knots merging with M=10 and N=5; same trend
    at the 75%, 50%, 25% and 0% thresholds.
  evidence: Figure 4
- id: trained-gap-inversion
  kind: result
  text: High-mergeability PopQA examples show the largest post-training gain in the probability
    of the correct answer. Those are the examples the base model was already closest to getting
    right on its own.
  scope: Llama-3.2-3B, PopQA example-level adapters, comparing correct-answer probability
    before and after LoRA finetuning on the entity's Wikipedia passages; the 639 examples
    finetuning fixed.
  evidence: Figure 3
- id: weights-no-correlation
  kind: result
  text: 'Weight-level properties of LoRA updates barely predict mergeability: on PopQA the
    Frobenius norm and the largest singular value of the effective update correlate with the
    mergeability score at 0.10 and 0.09 Spearman.'
  scope: Llama-3.2-3B PopQA adapters trained on a single layer's mlp.up_proj; the Lots-of-LoRAs
    adapters (attention Q, K, V across layers) likewise show no monotone trend.
  evidence: Figure 3
- id: lowest-bin-weights
  kind: result
  text: In Lots-of-LoRAs, the extremely low mergeability bin (S in [0.0,0.2)) has an average
    weight norm of 1.15 and average largest singular value of 0.78. Every higher bin ranges
    0.57-0.73 and 0.40-0.52.
  scope: Mistral-7B-Instruct-v0.2 task-level adapters, 81 tasks at the 99% threshold, ΔW=BA
    over attention Q, K, V; the separation is lowest bin versus the rest, not a trend across
    bins.
  evidence: Table 1
- id: mergeability-is-local
  kind: result
  text: Mergeability is primarily a local property of a single model update rather than of
    the merge set. Updates fixed at mergeability score 1.0 keep near-constant accuracy whichever
    mergeability bin their merge partners come from.
  scope: PopQA example-level setting, Llama adapters, Knots merging; the partner updates themselves
    still improve with their own mergeability score, so the merge set matters for the partners
    and not for the highly mergeable update.
  evidence: Figure 5
- id: algorithm-tradeoff
  kind: result
  text: Weaker merging algorithms push more examples into the top mergeability bins. TIES
    yields more PopQA examples with score at least 0.8 than Knots, and simple mean averaging
    produces the most examples at score 1.0.
  scope: Qwen2.5-3B on PopQA, example-level LoRA adapters of rank 64, comparing Knots, TIES
    and mean averaging at M=50, N=5.
  evidence: Figure 6
- id: weighted-merging
  kind: result
  text: Weighting each adapter inversely to the base model's accuracy on its task lets the
    2 low-base-accuracy tasks retain more of their finetuned performance. The 2 high-base-accuracy
    tasks show minimal degradation on one and none on the other.
  scope: Lots-of-LoRAs with Mistral-7B-Instruct-v0.2, 4 sampled tasks, softmax weights over
    1-Acc with temperature τ, against simple mean merging; base accuracies must be measurable
    in advance.
  evidence: Figure 7
- id: score-stability
  kind: result
  text: 'Mergeability scores are stable under the estimator''s sampling parameters: PopQA
    scores computed with M=50 and N=5 increase monotonically with scores computed at other
    numbers of trials N and other merge-set sizes M.'
  scope: Qwen2.5-3B on PopQA with Knots; the M-sweep is near-perfectly increasing and the
    N-sweep increasing.
  evidence: Figure A.13
- id: context-first-causes
  kind: context
  text: '"Will it Merge? On The Causes of Model Mergeability" gives model merging a per-update
    notion of mergeability, and names base model knowledge of the finetuning data as the dominant
    correlate. The question shifts from which algorithm merges best to which updates merge
    at all.'
  scope: To the authors' knowledge the first study to directly link pre-training knowledge
    with mergeability; earlier work related merging success to base model size and strength,
    to shared knowledge between tasks, and to update norms.
  evidence: Section 7
- id: context-two-granularities
  kind: context
  text: 'The mergeability study evaluates merging at two granularities that most merging papers
    do not separate: example-level adapters, each fixing one PopQA factual error, and task-level
    adapters from the Lots-of-LoRAs collection.'
  scope: Both setups use LoRA adapters on 3B-7B base and instruction models; training-data
    effects such as perplexity and context length appear only in Lots-of-LoRAs, where training
    data shares the evaluation format.
  evidence: Section 3
qa:
- ask:
    plain: why do some fine-tuned models combine cleanly with others while some lose their
      new skill?
    jargon: what property of a LoRA update predicts whether its task performance survives
      merging with other adapters?
    task: how do I predict in advance which of my LoRA adapters will keep working after being
      merged?
    practitioner: before I merge a batch of adapters, can I tell which ones will break?
  answered_by:
  - base-knowledge-popqa
  - base-knowledge-lots-of-loras
  - context-first-causes
- ask:
    plain: is how well a fine-tuned update combines with others a stable trait of that update,
      or just luck of the draw?
    jargon: do per-update mergeability scores for LoRA adapters deviate from a binomial null
      with a constant success rate?
    task: how do I check that the merge success rate I measured for an adapter is not sampling
      noise?
    practitioner: if one adapter of mine survived 8 out of 10 merges, should I trust that
      as a property of the adapter?
  answered_by:
  - mergeability-exists
  - score-stability
- ask:
    plain: does how big a fine-tuning update is tell you anything about whether it will merge
      well?
    jargon: do Frobenius norm and top singular value of the effective LoRA update correlate
      with merge survival?
    task: can I screen adapters for merge readiness just by inspecting their weight matrices?
    practitioner: is it enough to look at my adapters' weight norms to decide which to merge?
  answered_by:
  - weights-no-correlation
  - lowest-bin-weights
- ask:
    plain: does whether a fine-tuned update survives merging depend on which other updates
      it is mixed with?
    jargon: is mergeability a local property of a single update or a property of the merge
      set?
    task: do I need to re-measure merge success for every new combination of adapters I try?
    practitioner: if I swap out my merge partners, will my good adapter suddenly stop working?
  answered_by:
  - mergeability-is-local
- ask:
    plain: if a merging recipe is worse at preserving skills, does it look like more updates
      merged perfectly?
    jargon: how do TIES, KnOTS and simple mean averaging differ in the distribution of per-example
      merge success they induce?
    task: how do I compare merging algorithms without the weaker one looking better on a per-example
      success count?
    practitioner: should I pick the merging algorithm that gives me the most perfectly preserved
      examples?
  answered_by:
  - algorithm-tradeoff
- ask:
    plain: can giving more weight to the tasks a model is worst at rescue them when combining
      fine-tuned updates?
    jargon: does weighting adapters inversely to base model task accuracy improve retained
      finetuned performance for low-base-accuracy tasks?
    task: how do I stop my hardest task from being wiped out when I merge its adapter with
      others?
    practitioner: my adapters cover tasks of very different difficulty — should I weight them
      unequally when merging?
  answered_by:
  - weighted-merging
- ask:
    plain: what research asks why merging fine-tuned models works instead of proposing yet
      another merging recipe?
    jargon: which study links base model knowledge of the finetuning data to merge outcomes
      at both example and task granularity?
    task: where do I start reading if I want to understand the causes of merge failure rather
      than more merging algorithms?
    practitioner: which paper should I read to diagnose why my model merges keep failing?
  answered_by:
  - context-first-causes
  - context-two-granularities
- ask:
    plain: are harder or longer fine-tuning examples less likely to survive being merged with
      others?
    jargon: do finetuning-data properties such as perplexity and context length predict per-update
      mergeability?
    task: can I use difficulty statistics of my training data to pick which adapters to merge?
    practitioner: should I expect my adapters trained on hard examples to merge worse?
  answered_by:
  - weights-no-correlation
  - context-two-granularities
- ask:
    plain: are the cases fine-tuning fixes most easily also the ones that hold up best after
      models are combined?
    jargon: how does post-finetuning gain in correct-answer probability relate to per-example
      mergeability on PopQA?
    task: how do I tell which of the factual errors I fixed by finetuning will still be fixed
      after merging?
    practitioner: if finetuning gave a big improvement on an example, is that example safe
      to merge?
  answered_by:
  - trained-gap-inversion
  - base-knowledge-popqa
- ask:
    plain: how many repeat merges do you need to run before a per-update merge success rate
      settles down?
    jargon: how sensitive is the mergeability score to the number of trials N and the merge-set
      size M?
    task: how do I set the number of trials and merge partners when measuring merge success
      for an adapter?
    practitioner: can I get away with fewer merge trials and smaller merge sets to score my
      adapters?
  answered_by:
  - score-stability
terminology:
  mergeability: A property of a model update describing how much of the knowledge it encodes
    is preserved when it is merged with other model updates.
  mergeability score: The expected performance on an update's own task after that update is
    merged with M randomly sampled other updates, averaged over N such trials.
  example-level mergeability: Mergeability measured for LoRA adapters each trained to fix
    a single data point, such as one PopQA question about one entity.
  task-level mergeability: Mergeability measured for LoRA adapters each trained on a whole
    NLP task, scored by post-merge task accuracy.
  Δ_base: The gap between the probability the base model assigns to its top-ranked answer
    and the probability it assigns to the correct answer.
  Δ_trained: The increase in the probability of the correct answer from the base model to
    the finetuned model.
misreadings:
- 'Higher mergeability does not mean the merge is more useful: the most mergeable updates
  are those correcting knowledge the base model nearly had already, so the easiest updates
  to preserve are also the ones adding least.'
- Mean averaging placing more examples in the top mergeability bins does not make it the better
  merging algorithm; the mergeability score measures retention of one update's own knowledge,
  and mean averaging performs no interference mitigation at all.
- The finding that weight norm and top singular value do not correlate with mergeability is
  not a claim that no weight statistic can; the extremely low mergeability bin in Lots-of-LoRAs
  does show markedly higher norms and singular values.
- Mergeability being a local trait of the update does not mean the merge set is irrelevant
  to merged-model quality; partner updates with low mergeability still lose their own knowledge.
- The base-knowledge correlation is not evidence that the base model's general domain knowledge
  or the difficulty of the training data drives merging; in PopQA, perplexity and context
  length showed no clear trend.
- The weighted merging technique is a proof-of-concept on 4 Lots-of-LoRAs tasks, not a benchmarked
  merging method claimed to beat Knots or TIES.
---
