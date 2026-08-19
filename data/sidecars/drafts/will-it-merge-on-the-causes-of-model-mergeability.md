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

Then promote it:  python scripts/draft_sidecars.py --accept will-it-merge-on-the-causes-of-model-mergeability

Stamp: spec=74e012ff9654 checks=1 body=11506082e3d2
-->
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
    notion of mergeability and identifies base model knowledge of the finetuning data as the
    dominant correlate, shifting the question from which algorithm merges best to which updates
    merge at all.'
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
- q:
  - Why do some finetuned models merge well and others badly?
  - What determines whether model merging succeeds or fails?
  - What predicts which LoRA adapters survive merging?
  answers:
  - base-knowledge-popqa
  - base-knowledge-lots-of-loras
  - context-first-causes
- q:
  - Is mergeability a real property of a model update or just noise?
  - How can you tell mergeability is not random variation across merges?
  - What evidence is there that individual updates differ systematically in how well they
    merge?
  answers:
  - mergeability-exists
  - score-stability
- q:
  - Does the size or norm of a LoRA update predict how well it merges?
  - Do weight-level properties like Frobenius norm and top singular value correlate with merging
    success?
  - Can I look at adapter weights to guess whether merging will work?
  answers:
  - weights-no-correlation
  - lowest-bin-weights
- q:
  - Does mergeability depend on which other adapters you merge with?
  - Is merging success a property of the merge set or of the individual update?
  - If I merge a good adapter with bad ones, does the good one degrade?
  answers:
  - mergeability-is-local
- q:
  - How does the choice of merging algorithm change measured mergeability?
  - Do Knots, TIES and simple weight averaging give different mergeability distributions?
  - Does a stronger LoRA merging method produce more perfectly mergeable examples?
  answers:
  - algorithm-tradeoff
- q:
  - How can I stop merging from wiping out tasks the base model is weak on?
  - Does weighting adapters by base model accuracy improve merging?
  - Is there a simple fix that preserves low-accuracy tasks when merging adapters?
  answers:
  - weighted-merging
- q:
  - What should I read about why model merging works or fails?
  - Which paper studies the causes of merging success rather than proposing a new merging
    algorithm?
  - Where does research link a base model's pre-training knowledge to merging outcomes?
  answers:
  - context-first-causes
  - context-two-granularities
- q:
  - Does training data difficulty affect how mergeable an adapter is?
  - Do perplexity and context length of the finetuning data predict mergeability?
  - Are harder finetuning examples less mergeable?
  answers:
  - weights-no-correlation
  - context-two-granularities
- q:
  - Are the examples that are easiest to fix by finetuning also the most stable under merging?
  - What is the relationship between how much finetuning improves an example and how well
    it merges?
  answers:
  - trained-gap-inversion
  - base-knowledge-popqa
- q:
  - How many trials and merge partners are needed to estimate a mergeability score reliably?
  - Do mergeability scores change if you vary the number of merged adapters?
  answers:
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
