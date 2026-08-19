<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced via a forced tool call). Every claim, number
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

Then promote it:  python scripts/draft_sidecars.py --accept knowledge-is-a-region-in-weight-space-for-fine-tuned-languag

Stamp: spec=d57862840a90 checks=1 body=ae149295ed3e
-->
---
key: gueta2023knowledge
one_liner: Language models finetuned from the same pretrained checkpoint occupy bounded low-loss
  regions in weight space determined by dataset and task, and points sampled inside those
  regions — including the centroid — often outperform the finetuned models that define their
  edges.
terminology:
  generalized loss: 'A loss that is comparable across datasets: the encoder weights of a finetuned
    model are frozen, a fresh classification head is fit by linear probing on a target dataset''s
    training split, and the loss is reported on that dataset''s test split.'
  PB (probability of better): The probability that a model drawn from one group attains lower
    generalized loss than a model drawn from a comparison group, estimated over all pairs
    of models from the two groups.
  In, In', Ex: In is a set of models finetuned on datasets sharing a trait; In' is a set of
    models sampled from the convex hull (weighted averages) of In; Ex is a set of models not
    sharing that trait, or random perturbations of the pretrained model at matched distance.
  centroid model: The unweighted average of the weights of several models finetuned from the
    same pretrained checkpoint on different datasets, used as an initialization for further
    finetuning.
claims:
- id: dataset-clusters
  kind: result
  text: RoBERTa-base models finetuned on 12 GLUE/SuperGLUE datasets with 20 seeds each cluster
    by their finetuning dataset in weight space with 98% clustering accuracy, using cosine
    similarity between task vectors.
  scope: 280 RoBERTa-base models, 12 General (GLUE/SuperGLUE) datasets, spectral clustering
    into 12 clusters on pretrained-subtracted weights; all but 3 clusters perfectly matched.
    Euclidean distance on raw weights did not produce clear clusters.
  evidence: Figure 2(a), Section 4
- id: task-clusters
  kind: result
  text: Finetuned RoBERTa-base models group by task family — NLI, sentiment and topic classification
    — with 90% clustering accuracy in weight space, so a task and not only a single dataset
    corresponds to a region.
  scope: 5 seeds per dataset across 3 task families of English classification datasets, spectral
    clustering into 3 clusters; when a Twitter domain group is added as a fourth cluster,
    its F1 drops to 30 while NLI reaches 100.
  evidence: Figure 2(b), Table 1
- id: convex-hull-mnli
  kind: result
  text: Every weighted average of 5 MNLI-finetuned RoBERTa-base models beats every model finetuned
    on other General datasets on MNLI loss (PB = 100%), and beats the MNLI-finetuned models
    themselves 88% of the time.
  scope: RoBERTa-base, MNLI as the interior dataset, exterior models finetuned on the remaining
    General datasets, generalized loss with a freshly linear-probed head; interior region
    estimated by uniform sampling from the convex hull.
  evidence: Section 5.2, Figure 4(a)
- id: convex-hull-task-general
  kind: result
  text: Models sampled from the convex hull of NLI-finetuned models outperform models from
    outside that region in 100% of pairs and outperform the NLI-finetuned models themselves
    in 96.7%, versus PB = 75.3% for the finetuned NLI models over outsiders.
  scope: RoBERTa-base finetuned on NLI datasets, evaluated on all NLI test sets except ANLI;
    in the General granularity, with random weight perturbations at matched task-vector norm
    as the exterior, the hull reaches PB = 100% over exterior and 90% over the finetuned models.
  evidence: Section 5.2, Figure 4(b), Figure 4(c)
- id: interpolation
  kind: result
  text: Linearly interpolating between pairs of RoBERTa-base models finetuned on the same
    dataset, or on two different datasets of the same task, yields models whose average loss
    is comparable to or lower than the endpoint finetuned models, including on datasets the
    endpoints never saw.
  scope: 10 MNLI-MNLI pairs; 25 MNLI-ESNLI pairs evaluated on NLI test sets; 25 MNLI-SST2
    pairs evaluated on all 12 General datasets; losses are generalized losses averaged over
    seeds.
  evidence: Figure 3, Figure 10
- id: extrapolation-cliff
  kind: result
  text: Extrapolating past the endpoints of the line between two similarly finetuned RoBERTa-base
    models raises loss rapidly, indicating the low-loss regions have flat bases and steep
    edges and that finetuning lands near the region boundary.
  scope: Extrapolation with 10 logarithmic steps from alpha = 1 to 32 and from 0 to -31, tested
    at all 3 granularities (same dataset, same task, General); WNLI behaves differently from
    the other NLI datasets and may not belong to the NLI region.
  evidence: Figure 5, Figure 12, Figure 13(b)
- id: centroid-init
  kind: result
  text: Initializing BitFit finetuning from the centroid of models finetuned on other datasets
    beats initializing from pretrained RoBERTa-base by 4.03 accuracy points on average across
    12 datasets, winning on 9, tying on 2 and losing on 1 (WNLI).
  scope: RoBERTa-base, BitFit parameter-efficient finetuning on 12 GLUE/SuperGLUE datasets;
    for each target dataset the centroid excludes models finetuned on that target, so no target-specific
    finetuned model is used.
  evidence: Table 2, Figure 6
- id: centroid-fewshot
  kind: result
  text: With training data capped at 1K examples, BitFit finetuning from the centroid of other
    datasets' finetuned models gains 10.66 accuracy points on average over starting from pretrained
    RoBERTa-base, up to 33.99 points on SST2.
  scope: RoBERTa-base, BitFit, 12 GLUE/SuperGLUE targets with at most 1K training examples,
    centroid excluding target-dataset models; WNLI still loses 1.41 points and MultiRC 0.06.
  evidence: Table 3, Figure 14
- id: data-type-not-size
  kind: result
  text: 'The direction a finetuned model moves in weight space is set by the type of training
    data, not its quantity: models trained on 200 to 3K examples cluster by dataset and show
    no clustering by training-set size.'
  scope: 9 General datasets with at least 3K training examples, sub-sampled to 200, 400, 800,
    1.6K and 3K examples, clustered with k equal to either the number of datasets or the number
    of sizes; clustering agrees with data type in all but 1 case.
  evidence: Appendix C, Figure 7, Figure 8
- id: same-pretrained-required
  kind: result
  text: 'Proximity in weight space depends on sharing a pretrained starting point: RoBERTa-base
    models and a RoBERTa-base re-implementation, finetuned on the same datasets, cluster by
    which pretrained model they came from rather than by finetuning dataset.'
  scope: Two pretrained RoBERTa-base checkpoints (the original and Elazar et al.'s re-implementation),
    finetuned on the General dataset family; results are comparable on both, so each starting
    point has its own set of regions.
  evidence: Appendix B
- id: context-region-view
  kind: context
  text: '"Knowledge is a Region in Weight Space for Finetuned Language Models" extends linear
    mode connectivity into a claim about bounded convex regions, showing that whole neighbourhoods
    of weight space — not just paths between checkpoints — encode a dataset''s or task''s
    abilities.'
  scope: Argued for encoder-only English classification finetuning from a shared pretrained
    checkpoint (mainly RoBERTa-base, 36 datasets), as of publication in 2023; earlier connectivity
    work studied paths between models trained on the same data rather than regions spanning
    different datasets.
  evidence: Section 8, Section 9
- id: context-explains-merging
  kind: context
  text: '"Knowledge is a Region in Weight Space for Finetuned Language Models" offers a geometric
    explanation for why weight averaging methods such as model soups, Fisher merging and stochastic
    weight averaging work: averaging picks an interior point of a low-loss region while finetuning
    lands on its border.'
  scope: An interpretation the paper offers of prior results, supported by its own interpolation,
    convex-hull and extrapolation experiments on RoBERTa-base classifiers, not by re-running
    those merging methods.
  evidence: Section 7, Section 8
qa:
- q:
  - Do models finetuned on the same dataset end up close together in weight space?
  - Can you tell which dataset a finetuned model was trained on from its weights?
  - Does weight-space distance between finetuned checkpoints reflect their training data?
  answers:
  - dataset-clusters
  - task-clusters
- q:
  - Is averaging finetuned model weights better than the finetuned models themselves?
  - Do points inside the convex hull of finetuned checkpoints outperform the checkpoints?
  - How often does a weighted average of MNLI models beat an actual MNLI-finetuned model?
  answers:
  - convex-hull-mnli
  - convex-hull-task-general
- q:
  - What happens to loss when you interpolate between two finetuned language models?
  - Does linear interpolation between checkpoints finetuned on different datasets produce
    good models?
  - Is the best model on the line between two finetuned models, or at its ends?
  answers:
  - interpolation
  - extrapolation-cliff
- q:
  - Is averaging finetuned checkpoints a better starting point than the pretrained model?
  - Does initializing from a merged model help parameter-efficient finetuning?
  - How much accuracy does starting BitFit from a centroid of finetuned models gain over RoBERTa-base?
  answers:
  - centroid-init
  - centroid-fewshot
- q:
  - Does starting from merged weights help most when training data is scarce?
  - How large are the gains from a centroid initialization in a few-shot setting?
  answers:
  - centroid-fewshot
- q:
  - Is the weight-space movement during finetuning driven by how much data was used?
  - Does dataset size or dataset type determine where finetuning lands in weight space?
  - Do models trained on similar amounts of data look similar in weight space?
  answers:
  - data-type-not-size
- q:
  - Can I merge or interpolate models that came from different pretrained checkpoints?
  - Does weight-space clustering of finetuned models require a shared initialization?
  - Do two different RoBERTa pretraining runs share the same low-loss regions?
  answers:
  - same-pretrained-required
- q:
  - What paper should I read to understand why model merging and weight averaging work?
  - Where should I start reading about the geometry of finetuned model weights?
  - What work established that a task corresponds to a region in weight space rather than
    a single point?
  - Is there research explaining model soups and Fisher merging geometrically?
  answers:
  - context-region-view
  - context-explains-merging
- q:
  - How can losses of models finetuned on different datasets be compared at all?
  - How do you evaluate a finetuned encoder on a dataset it was never trained on?
  answers:
  - convex-hull-mnli
  - interpolation
- q:
  - Do task families like NLI and sentiment analysis occupy their own weight-space regions?
  - Does domain, like Twitter, cluster in weight space the way task does?
  answers:
  - task-clusters
- q:
  - How far can you move away from a finetuned model before performance collapses?
  - Are the low-loss basins around finetuned language models large or tight?
  answers:
  - extrapolation-cliff
misreadings:
- '0': T
  '1': h
  '2': e
  '3': ' '
  '4': r
  '5': e
  '6': s
  '7': u
  '8': l
  '9': t
  '10': s
  '11': ' '
  '12': d
  '13': o
  '14': ' '
  '15': n
  '16': o
  '17': t
  '18': ' '
  '19': s
  '20': h
  '21': o
  '22': w
  '23': ' '
  '24': t
  '25': h
  '26': a
  '27': t
  '28': ' '
  '29': a
  '30': n
  '31': y
  '32': ' '
  '33': t
  '34': w
  '35': o
  '36': ' '
  '37': f
  '38': i
  '39': n
  '40': e
  '41': t
  '42': u
  '43': n
  '44': e
  '45': d
  '46': ' '
  '47': l
  '48': a
  '49': n
  '50': g
  '51': u
  '52': a
  '53': g
  '54': e
  '55': ' '
  '56': m
  '57': o
  '58': d
  '59': e
  '60': l
  '61': s
  '62': ' '
  '63': c
  '64': a
  '65': n
  '66': ' '
  '67': b
  '68': e
  '69': ' '
  '70': a
  '71': v
  '72': e
  '73': r
  '74': a
  '75': g
  '76': e
  '77': d
  '78': ':'
  '79': ' '
  '80': p
  '81': r
  '82': o
  '83': x
  '84': i
  '85': m
  '86': i
  '87': t
  '88': y
  '89': ' '
  '90': a
  '91': n
  '92': d
  '93': ' '
  '94': l
  '95': o
  '96': w
  '97': '-'
  '98': l
  '99': o
  '100': s
  '101': s
  '102': ' '
  '103': i
  '104': n
  '105': t
  '106': e
  '107': r
  '108': p
  '109': o
  '110': l
  '111': a
  '112': t
  '113': i
  '114': o
  '115': n
  '116': ' '
  '117': h
  '118': o
  '119': l
  '120': d
  '121': ' '
  '122': o
  '123': n
  '124': l
  '125': y
  '126': ' '
  '127': f
  '128': o
  '129': r
  '130': ' '
  '131': m
  '132': o
  '133': d
  '134': e
  '135': l
  '136': s
  '137': ' '
  '138': f
  '139': i
  '140': n
  '141': e
  '142': t
  '143': u
  '144': n
  '145': e
  '146': d
  '147': ' '
  '148': f
  '149': r
  '150': o
  '151': m
  '152': ' '
  '153': t
  '154': h
  '155': e
  '156': ' '
  '157': s
  '158': a
  '159': m
  '160': e
  '161': ' '
  '162': p
  '163': r
  '164': e
  '165': t
  '166': r
  '167': a
  '168': i
  '169': n
  '170': e
  '171': d
  '172': ' '
  '173': c
  '174': h
  '175': e
  '176': c
  '177': k
  '178': p
  '179': o
  '180': i
  '181': n
  '182': t
  '183': .
  '184': ' '
  '185': M
  '186': o
  '187': d
  '188': e
  '189': l
  '190': s
  '191': ' '
  '192': f
  '193': r
  '194': o
  '195': m
  '196': ' '
  '197': t
  '198': w
  '199': o
  '200': ' '
  '201': d
  '202': i
  '203': f
  '204': f
  '205': e
  '206': r
  '207': e
  '208': n
  '209': t
  '210': ' '
  '211': R
  '212': o
  '213': B
  '214': E
  '215': R
  '216': T
  '217': a
  '218': '-'
  '219': b
  '220': a
  '221': s
  '222': e
  '223': ' '
  '224': p
  '225': r
  '226': e
  '227': t
  '228': r
  '229': a
  '230': i
  '231': n
  '232': i
  '233': n
  '234': g
  '235': ' '
  '236': r
  '237': u
  '238': n
  '239': s
  '240': ' '
  '241': c
  '242': l
  '243': u
  '244': s
  '245': t
  '246': e
  '247': r
  '248': ' '
  '249': b
  '250': y
  '251': ' '
  '252': p
  '253': r
  '254': e
  '255': t
  '256': r
  '257': a
  '258': i
  '259': n
  '260': e
  '261': d
  '262': ' '
  '263': o
  '264': r
  '265': i
  '266': g
  '267': i
  '268': n
  '269': ','
  '270': ' '
  '271': n
  '272': o
  '273': t
  '274': ' '
  '275': b
  '276': y
  '277': ' '
  '278': t
  '279': a
  '280': s
  '281': k
  '282': .
- '0': '"'
  '1': K
  '2': n
  '3': o
  '4': w
  '5': l
  '6': e
  '7': d
  '8': g
  '9': e
  '10': ' '
  '11': i
  '12': s
  '13': ' '
  '14': a
  '15': ' '
  '16': r
  '17': e
  '18': g
  '19': i
  '20': o
  '21': n
  '22': '"'
  '23': ' '
  '24': d
  '25': o
  '26': e
  '27': s
  '28': ' '
  '29': n
  '30': o
  '31': t
  '32': ' '
  '33': m
  '34': e
  '35': a
  '36': n
  '37': ' '
  '38': t
  '39': h
  '40': e
  '41': ' '
  '42': r
  '43': e
  '44': g
  '45': i
  '46': o
  '47': n
  '48': ' '
  '49': i
  '50': s
  '51': ' '
  '52': l
  '53': a
  '54': r
  '55': g
  '56': e
  '57': ' '
  '58': o
  '59': r
  '60': ' '
  '61': u
  '62': n
  '63': b
  '64': o
  '65': u
  '66': n
  '67': d
  '68': e
  '69': d
  '70': .
  '71': ' '
  '72': E
  '73': x
  '74': t
  '75': r
  '76': a
  '77': p
  '78': o
  '79': l
  '80': a
  '81': t
  '82': i
  '83': o
  '84': n
  '85': ' '
  '86': b
  '87': e
  '88': y
  '89': o
  '90': n
  '91': d
  '92': ' '
  '93': t
  '94': h
  '95': e
  '96': ' '
  '97': f
  '98': i
  '99': n
  '100': e
  '101': t
  '102': u
  '103': n
  '104': e
  '105': d
  '106': ' '
  '107': m
  '108': o
  '109': d
  '110': e
  '111': l
  '112': s
  '113': ' '
  '114': d
  '115': e
  '116': g
  '117': r
  '118': a
  '119': d
  '120': e
  '121': s
  '122': ' '
  '123': l
  '124': o
  '125': s
  '126': s
  '127': ' '
  '128': q
  '129': u
  '130': i
  '131': c
  '132': k
  '133': l
  '134': y
  '135': ;
  '136': ' '
  '137': t
  '138': h
  '139': e
  '140': ' '
  '141': r
  '142': e
  '143': g
  '144': i
  '145': o
  '146': n
  '147': s
  '148': ' '
  '149': a
  '150': r
  '151': e
  '152': ' '
  '153': s
  '154': m
  '155': a
  '156': l
  '157': l
  '158': ' '
  '159': b
  '160': a
  '161': s
  '162': i
  '163': n
  '164': s
  '165': ' '
  '166': w
  '167': i
  '168': t
  '169': h
  '170': ' '
  '171': s
  '172': t
  '173': e
  '174': e
  '175': p
  '176': ' '
  '177': c
  '178': l
  '179': i
  '180': f
  '181': f
  '182': s
  '183': ','
  '184': ' '
  '185': n
  '186': o
  '187': t
  '188': ' '
  '189': a
  '190': ' '
  '191': b
  '192': r
  '193': o
  '194': a
  '195': d
  '196': ' '
  '197': l
  '198': o
  '199': w
  '200': '-'
  '201': l
  '202': o
  '203': s
  '204': s
  '205': ' '
  '206': s
  '207': u
  '208': b
  '209': s
  '210': p
  '211': a
  '212': c
  '213': e
  '214': .
- '0': T
  '1': h
  '2': e
  '3': ' '
  '4': c
  '5': e
  '6': n
  '7': t
  '8': r
  '9': o
  '10': i
  '11': d
  '12': ' '
  '13': i
  '14': n
  '15': i
  '16': t
  '17': i
  '18': a
  '19': l
  '20': i
  '21': z
  '22': a
  '23': t
  '24': i
  '25': o
  '26': n
  '27': ' '
  '28': r
  '29': e
  '30': s
  '31': u
  '32': l
  '33': t
  '34': ' '
  '35': i
  '36': s
  '37': ' '
  '38': n
  '39': o
  '40': t
  '41': ' '
  '42': l
  '43': e
  '44': a
  '45': k
  '46': a
  '47': g
  '48': e
  '49': ' '
  '50': f
  '51': r
  '52': o
  '53': m
  '54': ' '
  '55': t
  '56': h
  '57': e
  '58': ' '
  '59': t
  '60': a
  '61': r
  '62': g
  '63': e
  '64': t
  '65': ' '
  '66': t
  '67': a
  '68': s
  '69': k
  '70': ':'
  '71': ' '
  '72': f
  '73': o
  '74': r
  '75': ' '
  '76': e
  '77': a
  '78': c
  '79': h
  '80': ' '
  '81': t
  '82': a
  '83': r
  '84': g
  '85': e
  '86': t
  '87': ' '
  '88': d
  '89': a
  '90': t
  '91': a
  '92': s
  '93': e
  '94': t
  '95': ' '
  '96': t
  '97': h
  '98': e
  '99': ' '
  '100': c
  '101': e
  '102': n
  '103': t
  '104': r
  '105': o
  '106': i
  '107': d
  '108': ' '
  '109': i
  '110': s
  '111': ' '
  '112': c
  '113': o
  '114': m
  '115': p
  '116': u
  '117': t
  '118': e
  '119': d
  '120': ' '
  '121': f
  '122': r
  '123': o
  '124': m
  '125': ' '
  '126': m
  '127': o
  '128': d
  '129': e
  '130': l
  '131': s
  '132': ' '
  '133': f
  '134': i
  '135': n
  '136': e
  '137': t
  '138': u
  '139': n
  '140': e
  '141': d
  '142': ' '
  '143': o
  '144': n
  '145': ' '
  '146': o
  '147': t
  '148': h
  '149': e
  '150': r
  '151': ' '
  '152': d
  '153': a
  '154': t
  '155': a
  '156': s
  '157': e
  '158': t
  '159': s
  '160': ' '
  '161': o
  '162': n
  '163': l
  '164': y
  '165': .
- '0': T
  '1': h
  '2': e
  '3': ' '
  '4': '3'
  '5': .
  '6': '0'
  '7': '6'
  '8': ' '
  '9': a
  '10': n
  '11': d
  '12': ' '
  '13': '4'
  '14': .
  '15': '0'
  '16': '3'
  '17': ' '
  '18': p
  '19': o
  '20': i
  '21': n
  '22': t
  '23': ' '
  '24': g
  '25': a
  '26': i
  '27': n
  '28': s
  '29': ' '
  '30': a
  '31': r
  '32': e
  '33': ' '
  '34': f
  '35': o
  '36': r
  '37': ' '
  '38': B
  '39': i
  '40': t
  '41': F
  '42': i
  '43': t
  '44': ' '
  '45': p
  '46': a
  '47': r
  '48': a
  '49': m
  '50': e
  '51': t
  '52': e
  '53': r
  '54': '-'
  '55': e
  '56': f
  '57': f
  '58': i
  '59': c
  '60': i
  '61': e
  '62': n
  '63': t
  '64': ' '
  '65': f
  '66': i
  '67': n
  '68': e
  '69': t
  '70': u
  '71': n
  '72': i
  '73': n
  '74': g
  '75': ','
  '76': ' '
  '77': n
  '78': o
  '79': t
  '80': ' '
  '81': f
  '82': o
  '83': r
  '84': ' '
  '85': f
  '86': u
  '87': l
  '88': l
  '89': ' '
  '90': f
  '91': i
  '92': n
  '93': e
  '94': t
  '95': u
  '96': n
  '97': i
  '98': n
  '99': g
  '100': ','
  '101': ' '
  '102': w
  '103': h
  '104': i
  '105': c
  '106': h
  '107': ' '
  '108': t
  '109': h
  '110': e
  '111': ' '
  '112': p
  '113': a
  '114': p
  '115': e
  '116': r
  '117': ' '
  '118': d
  '119': o
  '120': e
  '121': s
  '122': ' '
  '123': n
  '124': o
  '125': t
  '126': ' '
  '127': t
  '128': e
  '129': s
  '130': t
  '131': ' '
  '132': i
  '133': n
  '134': ' '
  '135': t
  '136': h
  '137': i
  '138': s
  '139': ' '
  '140': s
  '141': e
  '142': t
  '143': t
  '144': i
  '145': n
  '146': g
  '147': .
- '0': C
  '1': l
  '2': u
  '3': s
  '4': t
  '5': e
  '6': r
  '7': i
  '8': n
  '9': g
  '10': ' '
  '11': b
  '12': y
  '13': ' '
  '14': t
  '15': a
  '16': s
  '17': k
  '18': ' '
  '19': d
  '20': o
  '21': e
  '22': s
  '23': ' '
  '24': n
  '25': o
  '26': t
  '27': ' '
  '28': e
  '29': x
  '30': t
  '31': e
  '32': n
  '33': d
  '34': ' '
  '35': c
  '36': l
  '37': e
  '38': a
  '39': n
  '40': l
  '41': y
  '42': ' '
  '43': t
  '44': o
  '45': ' '
  '46': d
  '47': o
  '48': m
  '49': a
  '50': i
  '51': n
  '52': ':'
  '53': ' '
  '54': T
  '55': w
  '56': i
  '57': t
  '58': t
  '59': e
  '60': r
  '61': '-'
  '62': d
  '63': o
  '64': m
  '65': a
  '66': i
  '67': n
  '68': ' '
  '69': m
  '70': o
  '71': d
  '72': e
  '73': l
  '74': s
  '75': ' '
  '76': r
  '77': e
  '78': a
  '79': c
  '80': h
  '81': ' '
  '82': o
  '83': n
  '84': l
  '85': y
  '86': ' '
  '87': '3'
  '88': '0'
  '89': ' '
  '90': F
  '91': '1'
  '92': ' '
  '93': w
  '94': h
  '95': e
  '96': n
  '97': ' '
  '98': a
  '99': d
  '100': d
  '101': e
  '102': d
  '103': ' '
  '104': a
  '105': s
  '106': ' '
  '107': a
  '108': ' '
  '109': f
  '110': o
  '111': u
  '112': r
  '113': t
  '114': h
  '115': ' '
  '116': g
  '117': r
  '118': o
  '119': u
  '120': p
  '121': ','
  '122': ' '
  '123': a
  '124': n
  '125': d
  '126': ' '
  '127': t
  '128': h
  '129': e
  '130': ' '
  '131': p
  '132': a
  '133': p
  '134': e
  '135': r
  '136': ' '
  '137': l
  '138': e
  '139': a
  '140': v
  '141': e
  '142': s
  '143': ' '
  '144': o
  '145': p
  '146': e
  '147': n
  '148': ' '
  '149': w
  '150': h
  '151': e
  '152': t
  '153': h
  '154': e
  '155': r
  '156': ' '
  '157': d
  '158': o
  '159': m
  '160': a
  '161': i
  '162': n
  '163': s
  '164': ' '
  '165': f
  '166': o
  '167': r
  '168': m
  '169': ' '
  '170': r
  '171': e
  '172': g
  '173': i
  '174': o
  '175': n
  '176': s
  '177': ' '
  '178': a
  '179': t
  '180': ' '
  '181': a
  '182': l
  '183': l
  '184': .
- '0': T
  '1': h
  '2': e
  '3': ' '
  '4': f
  '5': i
  '6': n
  '7': d
  '8': i
  '9': n
  '10': g
  '11': s
  '12': ' '
  '13': a
  '14': r
  '15': e
  '16': ' '
  '17': a
  '18': b
  '19': o
  '20': u
  '21': t
  '22': ' '
  '23': f
  '24': i
  '25': n
  '26': e
  '27': t
  '28': u
  '29': n
  '30': i
  '31': n
  '32': g
  '33': ' '
  '34': f
  '35': r
  '36': o
  '37': m
  '38': ' '
  '39': a
  '40': ' '
  '41': p
  '42': r
  '43': e
  '44': t
  '45': r
  '46': a
  '47': i
  '48': n
  '49': e
  '50': d
  '51': ' '
  '52': e
  '53': n
  '54': c
  '55': o
  '56': d
  '57': e
  '58': r
  '59': ' '
  '60': o
  '61': n
  '62': ' '
  '63': E
  '64': n
  '65': g
  '66': l
  '67': i
  '68': s
  '69': h
  '70': ' '
  '71': c
  '72': l
  '73': a
  '74': s
  '75': s
  '76': i
  '77': f
  '78': i
  '79': c
  '80': a
  '81': t
  '82': i
  '83': o
  '84': n
  '85': ' '
  '86': d
  '87': a
  '88': t
  '89': a
  '90': ','
  '91': ' '
  '92': a
  '93': n
  '94': d
  '95': ' '
  '96': a
  '97': r
  '98': e
  '99': ' '
  '100': n
  '101': o
  '102': t
  '103': ' '
  '104': s
  '105': h
  '106': o
  '107': w
  '108': n
  '109': ' '
  '110': t
  '111': o
  '112': ' '
  '113': h
  '114': o
  '115': l
  '116': d
  '117': ' '
  '118': f
  '119': o
  '120': r
  '121': ' '
  '122': m
  '123': o
  '124': d
  '125': e
  '126': l
  '127': s
  '128': ' '
  '129': t
  '130': r
  '131': a
  '132': i
  '133': n
  '134': e
  '135': d
  '136': ' '
  '137': f
  '138': r
  '139': o
  '140': m
  '141': ' '
  '142': r
  '143': a
  '144': n
  '145': d
  '146': o
  '147': m
  '148': ' '
  '149': i
  '150': n
  '151': i
  '152': t
  '153': i
  '154': a
  '155': l
  '156': i
  '157': z
  '158': a
  '159': t
  '160': i
  '161': o
  '162': n
  '163': .
links_extra:
  arxiv: https://arxiv.org/abs/2302.04863
---
