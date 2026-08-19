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

Then promote it:  python scripts/draft_sidecars.py --accept disentqa-disentangling-parametric-and-contextual-knowledge-w

Stamp: spec=d57862840a90 checks=1 body=c913a7a959ba
-->
---
key: neeman2023disentqa
coined: DisentQA
gloss: a QA model trained to output two separate answers, one from the given passage and one
  from what the model memorized
one_liner: DisentQA trains a single generative QA model to emit two answers at once — a contextual
  answer grounded in the given passage and a parametric answer from its own memorized knowledge
  — using counterfactual and unanswerable-context data augmentation on Natural Questions.
claims:
- id: disentangled-output-paradigm
  kind: context
  text: DisentQA introduces a QA training paradigm in which one model outputs two answers
    per question, a contextual answer grounded in the supplied passage and a parametric answer
    from memorized pretraining knowledge, so that knowledge conflicts become visible instead
    of silently resolved.
  scope: Demonstrated on Natural Questions with T5-Large (770M) and T5-11B fine-tuned on gold
    passages (oracle retrieval); counterfactual augmentation only applies to questions whose
    answers are named entities.
- id: robustness-counterfactual
  text: On counterfactual Natural Questions contexts, the fully augmented DisentQA model reaches
    84.91% contextual-answer accuracy versus 66.81% for the vanilla single-answer model trained
    only on factual examples.
  evidence: Table 4
  scope: T5-11B, NQ dev-derived counterfactual test set of 1,365 examples, gold passages substituted
    by corpus-substitution; exact-match accuracy.
- id: augmentations-complementary
  text: 'Combining counterfactual and answerability augmentation is complementary for robustness:
    adding answerability on top of counterfactual data raises contextual accuracy on counterfactual
    examples by 5.35 points to 84.98% for the single-answer model.'
  evidence: Table 4
  scope: T5-11B single-answer models on the 1,365-example counterfactual test set; the same
    complementarity appears in the multi-answer models.
- id: factual-accuracy-preserved
  text: 'Adding a second, parametric answer costs little on standard Natural Questions: contextual-answer
    accuracy on the factual test set stays between 78.10% and 80.81% across all DisentQA variants
    and baselines, against 79.34% for the vanilla model.'
  evidence: Table 4
  scope: T5-11B, factual NQ test set with gold passages; the lowest values (78.10-78.32%)
    belong to the variants trained with answerability augmentation.
- id: answer-separation
  text: 'Only the model trained with both counterfactual and answerability augmentation separates
    its two answers: on counterfactual contexts its contextual and parametric answers are
    identical in just 18.46% of cases, versus 92.45% for counterfactual-only and 99.71% for
    answerability-only training.'
  evidence: Table 6
  scope: T5-11B multi-answer models on the counterfactual test set; on factual contexts the
    same model keeps the two answers identical 93.55% of the time, which is the desired behaviour
    there.
- id: answerability-random-context
  text: 'Detecting an irrelevant context requires counterfactual data too: with a randomly
    sampled passage, the fully augmented models predict "unanswerable" 99.34% (single-answer)
    and 99.49% (multi-answer) of the time, while answerability-only training reaches 27.69%
    and 35.60%.'
  evidence: Table 5
  scope: T5-11B on the 1,365-example random-context test set; with an empty context all four
    models score 100%, so only random contexts discriminate between them.
- id: parametric-answer-quality
  text: The fully augmented DisentQA model's parametric answer with an empty context is 31.14%
    exact match, 3.5 points above the 27.69% closed-book T5-11B baseline trained only to answer
    from parameters.
  evidence: Table 7
  scope: T5-11B, parametric answers compared against the original NQ answers; accuracy drifts
    with the supplied context (30.18% with random, 44.69% with counterfactual contexts), so
    the parametric answer is not fully context-independent.
- id: answer-overlap-inflation
  text: 'Much of the apparent parametric knowledge is fine-tuning memorization: on the No-Answer-Overlap
    subset the fully augmented model''s parametric accuracy drops to 7.40% with empty context
    and 7.10% with random context, 23.74 and 23.08 points below its accuracy on the full dev
    set.'
  evidence: Table 8
  scope: T5-11B; NAO subsets contain only reference answers absent from the training data,
    following Lewis et al. (2021); contextual-answer quality and robustness show much smaller
    NAO gaps.
- id: unseen-parametric-answers
  text: 'DisentQA''s parametric answers mostly repeat answers seen during fine-tuning: for
    the fully augmented model 18% of parametric answers on the counterfactual test set were
    never seen as an answer in fine-tuning, and 85% of those are disentangled from the contextual
    answer.'
  evidence: Section 5.4
  scope: T5-11B on the counterfactual test set; comparable unseen-answer rates are 25% for
    the answerability-only model, 26% for the counterfactual-only model and 23% for the closed-book
    baseline.
- id: leakage-failure-mode
  text: When the answerability-only multi-answer model fails to output "unanswerable" on a
    random context, it invariably emits the same string as both contextual and parametric
    answer, and in 176 of 879 error cases that string is copied from the unrelated random
    passage.
  evidence: Section 5.3
  scope: T5-11B "(m) f+a" model, random-context test set, where it fails on 64.4% of cases;
    the model trained with counterfactual data as well does not show this failure.
- id: model-size-trend
  text: 'DisentQA''s disentanglement behaviour holds at 770M parameters but is weaker: T5-Large''s
    fully augmented model reaches 81.03% contextual accuracy on counterfactual data and 33.99%
    answer similarity, against 84.91% and 18.46% for T5-11B.'
  evidence: Tables 10-13
  scope: T5-Large (770M) versus T5-11B on the same NQ-derived splits; T5-11B is better in
    all reported cases, and the ordering of model variants is preserved across the two sizes.
qa:
- q:
  - How can a QA model tell me whether its answer came from the retrieved passage or from
    memory?
  - Is there a way to separate what a language model memorized from what it read in the provided
    context?
  - What work proposes outputting two answers, one grounded in the passage and one from the
    model's own knowledge?
  answers:
  - disentangled-output-paradigm
  - answer-separation
- q:
  - What should I read about knowledge conflicts between retrieved context and model memory
    in question answering?
  - Where should I start reading about grounding generative QA answers in the provided passage
    versus parametric knowledge?
  - Which paper established the parametric-versus-contextual knowledge disentanglement framing
    for QA?
  answers:
  - disentangled-output-paradigm
- q:
  - Does counterfactual data augmentation make QA models follow the passage instead of their
    memorized fact?
  - How much does training on entity-substituted contexts improve robustness to knowledge
    conflicts?
  - What accuracy does DisentQA get on counterfactual Natural Questions contexts?
  answers:
  - robustness-counterfactual
  - augmentations-complementary
- q:
  - Does adding a second parametric answer hurt normal Natural Questions accuracy?
  - What is the cost on standard QA accuracy of training a model to emit two answers?
  - Does DisentQA lose exact-match performance on factual Natural Questions?
  answers:
  - factual-accuracy-preserved
- q:
  - Can a QA model learn to say "unanswerable" when the passage is irrelevant?
  - How well does abstention training work when the given context is a random unrelated passage?
  - Why is answerability training alone not enough to detect irrelevant contexts?
  answers:
  - answerability-random-context
  - leakage-failure-mode
- q:
  - Are counterfactual augmentation and answerability augmentation complementary or redundant?
  - Do you need both entity substitution and unanswerable examples to get disentanglement?
  - Which training augmentations are essential for a QA model to separate its two answers?
  answers:
  - augmentations-complementary
  - answer-separation
  - answerability-random-context
- q:
  - How good is the memorized answer that a disentangled QA model reports?
  - Does a model trained with context beat a closed-book model at answering from parameters
    alone?
  - What is DisentQA's parametric answer accuracy on Natural Questions with an empty context?
  answers:
  - parametric-answer-quality
- q:
  - Is the parametric answer really pretraining knowledge or just memorized fine-tuning answers?
  - How much does train-test answer overlap inflate closed-book style accuracy on Natural
    Questions?
  - What happens to parametric-answer accuracy on questions whose answers never appear in
    the training data?
  answers:
  - answer-overlap-inflation
  - unseen-parametric-answers
- q:
  - Does disentangling parametric and contextual knowledge need an 11B model?
  - How does model size affect a QA model's ability to separate memorized and contextual answers?
  - Do the DisentQA results replicate at T5-Large scale?
  answers:
  - model-size-trend
- q:
  - What are the limits of entity-substitution counterfactual training data for QA?
  - Which question types can this counterfactual augmentation not cover?
  - Does the disentanglement setup assume a perfect retriever?
  answers:
  - disentangled-output-paradigm
  - answer-overlap-inflation
terminology:
  parametric knowledge: Factual knowledge encoded in a language model's weights during pretraining
    and fine-tuning, available without any external passage.
  contextual knowledge: Factual knowledge supplied to a QA model at inference time as the
    context of the question, such as a retrieved Wikipedia passage.
  answer separation: The percentage of test cases in which a two-answer QA model's contextual
    and parametric answers are identical; low values are desired on counterfactual contexts
    and high values on factual ones.
  counterfactual example: A QA example whose context has had every occurrence of the answer
    entity replaced with a different entity of the same type, so the passage-grounded answer
    contradicts the memorized one.
  answerability augmentation: Training examples in which the context is empty or a randomly
    sampled unrelated passage and the required contextual answer is the special token "unanswerable".
  No Answer Overlap (NAO): The subset of a QA test set whose reference answers never appear
    as answers anywhere in the training data, used to remove train-test answer memorization
    artifacts.
misreadings:
- '0': D
  '1': i
  '2': s
  '3': e
  '4': n
  '5': t
  '6': Q
  '7': A
  '8': ''''
  '9': s
  '10': ' '
  '11': p
  '12': a
  '13': r
  '14': a
  '15': m
  '16': e
  '17': t
  '18': r
  '19': i
  '20': c
  '21': ' '
  '22': a
  '23': n
  '24': s
  '25': w
  '26': e
  '27': r
  '28': ' '
  '29': i
  '30': s
  '31': ' '
  '32': n
  '33': o
  '34': t
  '35': ' '
  '36': a
  '37': ' '
  '38': c
  '39': l
  '40': e
  '41': a
  '42': n
  '43': ' '
  '44': r
  '45': e
  '46': a
  '47': d
  '48': o
  '49': u
  '50': t
  '51': ' '
  '52': o
  '53': f
  '54': ' '
  '55': p
  '56': r
  '57': e
  '58': t
  '59': r
  '60': a
  '61': i
  '62': n
  '63': i
  '64': n
  '65': g
  '66': ' '
  '67': m
  '68': e
  '69': m
  '70': o
  '71': r
  '72': y
  '73': ':'
  '74': ' '
  '75': i
  '76': t
  '77': ' '
  '78': c
  '79': h
  '80': a
  '81': n
  '82': g
  '83': e
  '84': s
  '85': ' '
  '86': w
  '87': i
  '88': t
  '89': h
  '90': ' '
  '91': t
  '92': h
  '93': e
  '94': ' '
  '95': s
  '96': u
  '97': p
  '98': p
  '99': l
  '100': i
  '101': e
  '102': d
  '103': ' '
  '104': c
  '105': o
  '106': n
  '107': t
  '108': e
  '109': x
  '110': t
  '111': ','
  '112': ' '
  '113': a
  '114': n
  '115': d
  '116': ' '
  '117': '8'
  '118': '2'
  '119': '%'
  '120': ' '
  '121': o
  '122': f
  '123': ' '
  '124': p
  '125': a
  '126': r
  '127': a
  '128': m
  '129': e
  '130': t
  '131': r
  '132': i
  '133': c
  '134': ' '
  '135': a
  '136': n
  '137': s
  '138': w
  '139': e
  '140': r
  '141': s
  '142': ' '
  '143': o
  '144': n
  '145': ' '
  '146': t
  '147': h
  '148': e
  '149': ' '
  '150': c
  '151': o
  '152': u
  '153': n
  '154': t
  '155': e
  '156': r
  '157': f
  '158': a
  '159': c
  '160': t
  '161': u
  '162': a
  '163': l
  '164': ' '
  '165': t
  '166': e
  '167': s
  '168': t
  '169': ' '
  '170': s
  '171': e
  '172': t
  '173': ' '
  '174': w
  '175': e
  '176': r
  '177': e
  '178': ' '
  '179': a
  '180': l
  '181': r
  '182': e
  '183': a
  '184': d
  '185': y
  '186': ' '
  '187': s
  '188': e
  '189': e
  '190': n
  '191': ' '
  '192': a
  '193': s
  '194': ' '
  '195': a
  '196': n
  '197': s
  '198': w
  '199': e
  '200': r
  '201': s
  '202': ' '
  '203': d
  '204': u
  '205': r
  '206': i
  '207': n
  '208': g
  '209': ' '
  '210': f
  '211': i
  '212': n
  '213': e
  '214': '-'
  '215': t
  '216': u
  '217': n
  '218': i
  '219': n
  '220': g
  '221': .
- '0': H
  '1': i
  '2': g
  '3': h
  '4': ' '
  '5': a
  '6': c
  '7': c
  '8': u
  '9': r
  '10': a
  '11': c
  '12': y
  '13': ' '
  '14': o
  '15': n
  '16': ' '
  '17': c
  '18': o
  '19': u
  '20': n
  '21': t
  '22': e
  '23': r
  '24': f
  '25': a
  '26': c
  '27': t
  '28': u
  '29': a
  '30': l
  '31': ' '
  '32': c
  '33': o
  '34': n
  '35': t
  '36': e
  '37': x
  '38': t
  '39': s
  '40': ' '
  '41': d
  '42': o
  '43': e
  '44': s
  '45': ' '
  '46': n
  '47': o
  '48': t
  '49': ' '
  '50': m
  '51': e
  '52': a
  '53': n
  '54': ' '
  '55': p
  '56': e
  '57': r
  '58': f
  '59': e
  '60': c
  '61': t
  '62': ' '
  '63': g
  '64': r
  '65': o
  '66': u
  '67': n
  '68': d
  '69': i
  '70': n
  '71': g
  '72': ':'
  '73': ' '
  '74': e
  '75': n
  '76': t
  '77': i
  '78': t
  '79': y
  '80': '-'
  '81': s
  '82': u
  '83': b
  '84': s
  '85': t
  '86': i
  '87': t
  '88': u
  '89': t
  '90': e
  '91': d
  '92': ' '
  '93': p
  '94': a
  '95': s
  '96': s
  '97': a
  '98': g
  '99': e
  '100': s
  '101': ' '
  '102': r
  '103': e
  '104': a
  '105': d
  '106': ' '
  '107': a
  '108': s
  '109': ' '
  '110': s
  '111': o
  '112': m
  '113': e
  '114': w
  '115': h
  '116': a
  '117': t
  '118': ' '
  '119': u
  '120': n
  '121': n
  '122': a
  '123': t
  '124': u
  '125': r
  '126': a
  '127': l
  '128': ' '
  '129': t
  '130': e
  '131': x
  '132': t
  '133': ','
  '134': ' '
  '135': w
  '136': h
  '137': i
  '138': c
  '139': h
  '140': ' '
  '141': t
  '142': h
  '143': e
  '144': ' '
  '145': m
  '146': o
  '147': d
  '148': e
  '149': l
  '150': ' '
  '151': m
  '152': a
  '153': y
  '154': ' '
  '155': e
  '156': x
  '157': p
  '158': l
  '159': o
  '160': i
  '161': t
  '162': ' '
  '163': a
  '164': s
  '165': ' '
  '166': a
  '167': ' '
  '168': c
  '169': u
  '170': e
  '171': .
- '0': T
  '1': h
  '2': e
  '3': ' '
  '4': a
  '5': n
  '6': s
  '7': w
  '8': e
  '9': r
  '10': a
  '11': b
  '12': i
  '13': l
  '14': i
  '15': t
  '16': y
  '17': ' '
  '18': r
  '19': e
  '20': s
  '21': u
  '22': l
  '23': t
  '24': s
  '25': ' '
  '26': a
  '27': r
  '28': e
  '29': ' '
  '30': n
  '31': o
  '32': t
  '33': ' '
  '34': e
  '35': v
  '36': i
  '37': d
  '38': e
  '39': n
  '40': c
  '41': e
  '42': ' '
  '43': o
  '44': f
  '45': ' '
  '46': s
  '47': o
  '48': l
  '49': v
  '50': e
  '51': d
  '52': ' '
  '53': a
  '54': b
  '55': s
  '56': t
  '57': e
  '58': n
  '59': t
  '60': i
  '61': o
  '62': n
  '63': ':'
  '64': ' '
  '65': t
  '66': h
  '67': e
  '68': ' '
  '69': u
  '70': n
  '71': a
  '72': n
  '73': s
  '74': w
  '75': e
  '76': r
  '77': a
  '78': b
  '79': l
  '80': e
  '81': ' '
  '82': e
  '83': x
  '84': a
  '85': m
  '86': p
  '87': l
  '88': e
  '89': s
  '90': ' '
  '91': a
  '92': r
  '93': e
  '94': ' '
  '95': e
  '96': m
  '97': p
  '98': t
  '99': y
  '100': ' '
  '101': o
  '102': r
  '103': ' '
  '104': t
  '105': o
  '106': p
  '107': i
  '108': c
  '109': a
  '110': l
  '111': l
  '112': y
  '113': ' '
  '114': u
  '115': n
  '116': r
  '117': e
  '118': l
  '119': a
  '120': t
  '121': e
  '122': d
  '123': ' '
  '124': c
  '125': o
  '126': n
  '127': t
  '128': e
  '129': x
  '130': t
  '131': s
  '132': ','
  '133': ' '
  '134': a
  '135': ' '
  '136': p
  '137': r
  '138': o
  '139': o
  '140': f
  '141': '-'
  '142': o
  '143': f
  '144': '-'
  '145': c
  '146': o
  '147': n
  '148': c
  '149': e
  '150': p
  '151': t
  '152': ' '
  '153': s
  '154': e
  '155': t
  '156': u
  '157': p
  '158': ' '
  '159': r
  '160': a
  '161': t
  '162': h
  '163': e
  '164': r
  '165': ' '
  '166': t
  '167': h
  '168': a
  '169': n
  '170': ' '
  '171': d
  '172': i
  '173': s
  '174': t
  '175': r
  '176': a
  '177': c
  '178': t
  '179': i
  '180': n
  '181': g
  '182': ' '
  '183': n
  '184': e
  '185': a
  '186': r
  '187': '-'
  '188': m
  '189': i
  '190': s
  '191': s
  '192': ' '
  '193': p
  '194': a
  '195': s
  '196': s
  '197': a
  '198': g
  '199': e
  '200': s
  '201': .
- '0': D
  '1': i
  '2': s
  '3': e
  '4': n
  '5': t
  '6': Q
  '7': A
  '8': ' '
  '9': i
  '10': s
  '11': ' '
  '12': n
  '13': o
  '14': t
  '15': ' '
  '16': e
  '17': v
  '18': a
  '19': l
  '20': u
  '21': a
  '22': t
  '23': e
  '24': d
  '25': ' '
  '26': w
  '27': i
  '28': t
  '29': h
  '30': ' '
  '31': a
  '32': ' '
  '33': r
  '34': e
  '35': t
  '36': r
  '37': i
  '38': e
  '39': v
  '40': e
  '41': r
  '42': ':'
  '43': ' '
  '44': a
  '45': l
  '46': l
  '47': ' '
  '48': N
  '49': a
  '50': t
  '51': u
  '52': r
  '53': a
  '54': l
  '55': ' '
  '56': Q
  '57': u
  '58': e
  '59': s
  '60': t
  '61': i
  '62': o
  '63': n
  '64': s
  '65': ' '
  '66': e
  '67': x
  '68': p
  '69': e
  '70': r
  '71': i
  '72': m
  '73': e
  '74': n
  '75': t
  '76': s
  '77': ' '
  '78': u
  '79': s
  '80': e
  '81': ' '
  '82': t
  '83': h
  '84': e
  '85': ' '
  '86': g
  '87': o
  '88': l
  '89': d
  '90': ' '
  '91': p
  '92': a
  '93': s
  '94': s
  '95': a
  '96': g
  '97': e
  '98': ' '
  '99': a
  '100': s
  '101': ' '
  '102': c
  '103': o
  '104': n
  '105': t
  '106': e
  '107': x
  '108': t
  '109': ','
  '110': ' '
  '111': a
  '112': s
  '113': s
  '114': u
  '115': m
  '116': i
  '117': n
  '118': g
  '119': ' '
  '120': a
  '121': n
  '122': ' '
  '123': o
  '124': r
  '125': a
  '126': c
  '127': l
  '128': e
  '129': ' '
  '130': r
  '131': e
  '132': t
  '133': r
  '134': i
  '135': e
  '136': v
  '137': a
  '138': l
  '139': ' '
  '140': s
  '141': y
  '142': s
  '143': t
  '144': e
  '145': m
  '146': .
- '0': C
  '1': o
  '2': u
  '3': n
  '4': t
  '5': e
  '6': r
  '7': f
  '8': a
  '9': c
  '10': t
  '11': u
  '12': a
  '13': l
  '14': ' '
  '15': a
  '16': u
  '17': g
  '18': m
  '19': e
  '20': n
  '21': t
  '22': a
  '23': t
  '24': i
  '25': o
  '26': n
  '27': ' '
  '28': a
  '29': s
  '30': ' '
  '31': u
  '32': s
  '33': e
  '34': d
  '35': ' '
  '36': i
  '37': n
  '38': ' '
  '39': D
  '40': i
  '41': s
  '42': e
  '43': n
  '44': t
  '45': Q
  '46': A
  '47': ' '
  '48': d
  '49': o
  '50': e
  '51': s
  '52': ' '
  '53': n
  '54': o
  '55': t
  '56': ' '
  '57': a
  '58': p
  '59': p
  '60': l
  '61': y
  '62': ' '
  '63': t
  '64': o
  '65': ' '
  '66': a
  '67': l
  '68': l
  '69': ' '
  '70': q
  '71': u
  '72': e
  '73': s
  '74': t
  '75': i
  '76': o
  '77': n
  '78': s
  '79': ':'
  '80': ' '
  '81': i
  '82': t
  '83': ' '
  '84': r
  '85': e
  '86': q
  '87': u
  '88': i
  '89': r
  '90': e
  '91': s
  '92': ' '
  '93': n
  '94': a
  '95': m
  '96': e
  '97': d
  '98': '-'
  '99': e
  '100': n
  '101': t
  '102': i
  '103': t
  '104': y
  '105': ' '
  '106': a
  '107': n
  '108': s
  '109': w
  '110': e
  '111': r
  '112': s
  '113': ','
  '114': ' '
  '115': s
  '116': o
  '117': ' '
  '118': q
  '119': u
  '120': e
  '121': s
  '122': t
  '123': i
  '124': o
  '125': n
  '126': ' '
  '127': t
  '128': y
  '129': p
  '130': e
  '131': s
  '132': ' '
  '133': s
  '134': u
  '135': c
  '136': h
  '137': ' '
  '138': a
  '139': s
  '140': ' '
  '141': B
  '142': o
  '143': o
  '144': l
  '145': e
  '146': a
  '147': n
  '148': ' '
  '149': q
  '150': u
  '151': e
  '152': s
  '153': t
  '154': i
  '155': o
  '156': n
  '157': s
  '158': ' '
  '159': a
  '160': r
  '161': e
  '162': ' '
  '163': o
  '164': u
  '165': t
  '166': ' '
  '167': o
  '168': f
  '169': ' '
  '170': s
  '171': c
  '172': o
  '173': p
  '174': e
  '175': .
links_extra:
  code: https://github.com/ellaneeman/disent_qa
---
