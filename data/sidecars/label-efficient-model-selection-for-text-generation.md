---
key: ashurytahan2024diffuse
coined: DiffUse
gloss: selecting which examples to have annotated by clustering the difference between two
  models' outputs, so fewer preference labels are needed to tell which model is better
one_liner: DiffUse picks which examples to send to a human or LLM judge by embedding both
  models' outputs, subtracting them, clustering the difference vectors and annotating one
  representative per cluster, so far fewer preference labels are needed to identify the better
  text generation model.
claims:
- id: iterative-annotation-savings
  kind: result
  text: With the iterative stopping rule at risk threshold p=0.2, DiffUse reaches a decision
    after 28.77 annotations on NarrativeQA versus 118.69 for random sampling, and 85.25 versus
    160.97 on open-book NaturalQuestions.
  scope: HELM v0.2.2 data, 666 model pairs per scenario, Algorithm 1 with n=5 and maximum
    budget N=200; reference-based metrics stand in for the preference oracle.
  evidence: Table 2
- id: iterative-success-rate
  kind: result
  text: At risk threshold p=0.2 the iterative DiffUse procedure returns the correct winner
    on 89.64% of NarrativeQA model pairs against 43.03% for random sampling, and on 86.50%
    versus 80.32% for CNN/DailyMail.
  scope: 666 HELM model pairs per scenario, Algorithm 1 with n=5, N=200; gains are much smaller
    on closed-book NaturalQuestions, where winning distances are tiny.
  evidence: Table 2
- id: hard-case-limit
  kind: result
  text: On closed-book NaturalQuestions, iterative DiffUse at p=0.2 annotates 189.05 examples
    and still returns an inconclusive verdict for 93.41% of model pairs, because the test
    winning distances in that scenario are very small.
  scope: HELM closed-book NaturalQuestions, 666 model pairs, Algorithm 1 with n=5 and maximum
    budget N=200; random sampling is no better, at 191.74 annotations and 95.53% inconclusive.
  evidence: Table 2
- id: failures-are-cheap
  kind: result
  text: When iterative DiffUse picks the wrong model at p=0.2, the pair's average winning
    distance is 0.06 on both CNN/DailyMail and NarrativeQA. Correctly decided pairs have far
    larger gaps, 0.30 and 0.34, so the cost of an error is limited.
  scope: 666 HELM model pairs per scenario, Algorithm 1 with p=0.2, n=5, N=200; winning distance
    is defined over reference-based metric scores, not human preferences.
  evidence: Table 2
- id: winner-bias
  kind: result
  text: DiffUse produces a winning-distance estimate biased in favour of the true test winner,
    largest at small annotation budgets and dissipating as more examples are labeled. Random
    selection, by contrast, deviates from the test winning distance by 0 on average.
  scope: Aggregated across all 666 model pairs on XSum, budgets from 5 to 200 examples; the
    bias means DiffUse should not be used to report the size of the performance gap.
  evidence: Figure 5
- id: high-norm-informative
  kind: result
  text: 'Output pairs whose difference vector has a larger norm are more likely to carry the
    preference label matching the overall test winner. Hierarchical clustering exploits this:
    often over half the vectors fall into a single low-norm cluster that contributes just
    1 annotated example.'
  scope: Difference vectors from Sentence-BERT all-MiniLM-L6-v2 embeddings, binned into 50
    equal-count bins per model pair, aggregated over NarrativeQA model pairs.
  evidence: Figure 10
- id: max-norm-fails
  kind: result
  text: Annotating the examples with the highest difference-vector norm, without clustering,
    is inconsistent across the 6 HELM generation scenarios and does not match DiffUse. Norm
    alone selects outliers that do not represent the space of output differences.
  scope: Max-norm baseline across the 6 HELM generation scenarios and 666 model pairs, budgets
    5-200; norm ranking still carries useful signal, it is the loss of diversity that hurts.
  evidence: Figure 16
- id: input-clustering-fails
  kind: result
  text: Clustering the embeddings of task inputs instead of output difference vectors does
    not consistently beat random sampling across the 6 HELM scenarios and 666 model pairs.
    The gains of DiffUse therefore come specifically from representing differences between
    model outputs.
  scope: 6 HELM generation scenarios, 666 model pairs, budgets 5-200; contrasts with active-learning
    style input-space selection.
  evidence: Figure 14
- id: robust-to-clustering-choice
  kind: result
  text: Swapping DiffUse's clustering algorithm among 3 options (hierarchical with Euclidean
    or cosine distance, or k-means) changes model-preference success rates only slightly,
    and all configurations beat random selection. The rule for picking a cluster representative
    matters as little.
  scope: 6 HELM generation scenarios, 666 model pairs, budgets 5-200; representative rules
    compared are random, nearest centroid by Euclidean or cosine distance, and maximum norm.
  evidence: Figure 12
- id: prompt-selection
  kind: result
  text: DiffUse also identifies the better of two few-shot prompt variants for a single fixed
    model using far fewer annotations than random selection, consistently across 111 unique
    prompt pairs per scenario.
  scope: 3 prompt variants for each of 37 HELM models, over the 6 generation scenarios with
    3 reference-based metrics each; variants differ only in the few-shot exemplars before
    the input.
  evidence: Figure 17
- id: problem-context
  kind: context
  text: 'DiffUse addresses label-efficient model selection for text generation: choosing between
    two generation models or prompts under a fixed preference-annotation budget. Earlier example-selection
    work had treated classification and question answering rather than generation.'
  scope: Pairwise comparison only, with no theoretical guarantee for a single comparison;
    picking from more than 2 candidates is left to future work. As of the ACL 2024 publication.
  evidence: Section 8
- id: no-annotations-needed
  kind: context
  text: DiffUse requires no existing annotations and no assumptions about the models, tasks,
    prompts or hyper-parameters, needing only the two models' generated outputs on unlabeled
    test inputs. Item-response-theory selection methods instead need fully annotated data
    for a set of existing models.
  scope: Requires running inference with both models over the pool of examples to be clustered,
    in the range of hundreds; only worthwhile when the oracle's cost far exceeds that inference
    cost, as with paid APIs or human annotators.
  evidence: Section 8
- id: simulated-oracle
  kind: result
  text: All DiffUse results use HELM reference-based automatic metrics as the preference oracle,
    with 3 metrics per each of 6 scenarios simulating different oracle types. The method is
    therefore not demonstrated on real human or LLM preference judgments.
  scope: HELM v0.2.2 core scenarios, 6 generation tasks, 37 models, 666 model pairs, 800 of
    1000 examples sampled per run, 10 seeds, budgets 5-200; a stated limitation of the work.
  evidence: Section 5.1
qa:
- ask:
    plain: how can I tell which of two text generators is better without paying someone to
      read every test output?
    jargon: what approach gives label-efficient pairwise model selection for generation tasks
      under a fixed preference-annotation budget?
    task: how do I pick between two summarization or QA systems while annotating only a small
      subset of the test set?
    practitioner: I have two candidate generation models and a small annotation budget — can
      I still trust which one I pick?
  answered_by:
  - problem-context
  - iterative-annotation-savings
  - no-annotations-needed
- ask:
    plain: how many judged examples does difference-based selection save compared with picking
      test examples at random?
    jargon: what annotation-budget reduction does DiffUse achieve over random sampling at
      matched model-preference success rates?
    task: how few preference judgments do I need to reliably rank two generation models against
      each other?
    practitioner: is selecting examples by output-difference clustering actually cheaper than
      random sampling for my comparison?
  answered_by:
  - iterative-annotation-savings
  - iterative-success-rate
- ask:
    plain: how do I know when I have annotated enough examples to call a winner between two
      models?
    jargon: how does the iterative DiffUse stopping rule at risk threshold p=0.2 trade off
      annotation count, decision accuracy and inconclusive verdicts?
    task: how do I decide when to stop labeling and declare one of two generation models the
      winner?
    practitioner: if I use a 0.2 risk threshold stopping rule for a two-model comparison,
      how often will the verdict be wrong or inconclusive?
  answered_by:
  - iterative-success-rate
  - failures-are-cheap
  - hard-case-limit
- ask:
    plain: can a small hand-picked sample tell me how much better one model is, not just which
      one is better?
    jargon: is the winning-distance estimate from difference-vector clustering unbiased, and
      why does the selection favour the test winner?
    task: how do I estimate the size of the quality gap between two generation models from
      a small annotated subset?
    practitioner: should I report the performance gap between two models from a DiffUse-selected
      sample, or only the winner?
  answered_by:
  - winner-bias
  - high-norm-informative
- ask:
    plain: which test examples tell you the most when comparing two models that write different
      answers?
    jargon: does the norm of the output difference vector predict agreement with the overall
      test-set preference?
    task: how do I find the handful of examples worth annotating when comparing two generation
      models?
    practitioner: should I spend my annotation budget on the examples where two models' outputs
      diverge most?
  answered_by:
  - high-norm-informative
  - max-norm-fails
- ask:
    plain: is it enough to label only the examples where two models' answers differ the most?
    jargon: does a max-norm difference-vector baseline match clustering-based selection across
      HELM generation scenarios?
    task: can I skip clustering and just rank test examples by how far apart the two models'
      outputs are?
    practitioner: should I use a simple largest-difference heuristic instead of clustering
      output differences?
  answered_by:
  - max-norm-fails
- ask:
    plain: would grouping the questions themselves work as well as grouping the ways two models'
      answers differ?
    jargon: does clustering task-input embeddings match clustering output difference vectors
      for pairwise generation model selection?
    task: should I select evaluation examples from input-space embeddings or from differences
      between the two models' outputs?
    practitioner: I already have input embeddings for my test set — can I just cluster those
      to choose which examples to annotate?
  answered_by:
  - input-clustering-fails
  - high-norm-informative
- ask:
    plain: does the choice of clustering algorithm change how well the example selection works?
    jargon: how sensitive is DiffUse's model-preference success rate to hierarchical Euclidean,
      hierarchical cosine and k-means clustering, and to representative selection?
    task: which parts of a difference-vector selection pipeline do I have to tune before comparing
      two models?
    practitioner: do I need to tune the clustering algorithm and representative rule, or will
      any reasonable choice do?
  answered_by:
  - robust-to-clustering-choice
  - input-clustering-fails
- ask:
    plain: can the same cheap-labeling trick pick the better of two prompts for one model?
    jargon: does difference-vector selection extend from model pairs to few-shot prompt variants
      of a fixed model?
    task: how do I choose between two few-shot prompt templates with as few preference annotations
      as possible?
    practitioner: I am comparing two prompt variants of one model — can I use DiffUse instead
      of annotating a full test set?
  answered_by:
  - prompt-selection
- ask:
    plain: were the reported savings measured with real human judgments or with automatic
      scores?
    jargon: what preference oracle backed the DiffUse experiments, and does it cover LLM-as-judge
      or human annotation?
    practitioner: before I rely on DiffUse for human-annotated preference comparisons, what
      was it actually validated against?
  answered_by:
  - simulated-oracle
  - problem-context
- ask:
    plain: when is it not worth trying to cut annotation costs for comparing two models?
    jargon: what does DiffUse assume about the compared models and available labels, and in
      which scenarios does it fail to reach a verdict?
    task: how do I know whether cheap difference-based selection will work for the two models
      I want to compare?
    practitioner: do I need any existing labeled evaluation data or model assumptions to use
      DiffUse, and when will it not pay off?
  answered_by:
  - no-annotations-needed
  - hard-case-limit
- ask:
    plain: what should I read first about cutting the cost of comparing two language models?
    jargon: which work introduced label-efficient example selection for pairwise evaluation
      of text generation rather than classification?
    task: where do I start if I want to reduce the annotation cost of my LLM comparisons?
    practitioner: is there a paper I can point my team to on cheap pairwise evaluation of
      generation models?
  answered_by:
  - problem-context
  - no-annotations-needed
misreadings:
- The 75% reduction in annotations is a reduction relative to random sampling of the examples
  needed to reach the same reliability, not an absolute guarantee that 25% of a test set suffices
  for any model pair; on closed-book NaturalQuestions the full budget of 200 examples still
  leaves most comparisons inconclusive.
- 'DiffUse is a deliberately biased selector, not a better estimator of model quality: its
  winning-distance estimate leans toward the true winner at small budgets, so it should not
  be used to report how much better one model is.'
- The hypergeometric stopping threshold is a heuristic proxy for risk, not a statistical guarantee
  — the distribution's assumptions are violated because DiffUse selects non-randomly, though
  the measured error rate stayed below the chosen threshold on every dataset tested.
- The reported preference labels come from HELM reference-based automatic metrics simulating
  oracles, so the DiffUse results do not directly establish behavior with human annotators
  or an LLM judge.
- DiffUse compares 2 candidates at a time; it is not evaluated on ranking a larger pool of
  models, which the paper leaves to future work.
terminology:
  difference vector: The elementwise subtraction of the sentence embedding of one model's
    output from the other model's output on the same input, used as a representation of how
    the two models disagree on that example.
  test winning model: The model whose outputs are preferred by the oracle on more examples
    of the full test set — the ground truth an annotation-budgeted comparison is trying to
    recover.
  test winning distance: The absolute difference between the two models' win probabilities
    over the full test set, i.e. the size of the performance gap.
  success rate: The fraction of selection runs in which the winner computed from the annotated
    subset equals the test winning model, aggregated over model pairs and random seeds.
  oracle: Whatever judges which of two generated outputs is better — a human annotator, an
    LLM judge, or a reference-based automatic metric standing in for one.
---
