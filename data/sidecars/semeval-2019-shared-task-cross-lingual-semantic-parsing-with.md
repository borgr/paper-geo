---
key: hershcovich2018semeval
one_liner: The SemEval 2019 Task 1 call for participation defines cross-lingual UCCA semantic
  parsing in English, German and French, with four settings (English in-domain and out-of-domain,
  German in-domain, French with no training data), DAG F1 scoring, and the TUPA transition-based
  parser as baseline.
links_extra:
  competition: https://competitions.codalab.org/competitions/19160
  corpora: https://github.com/UniversalConceptualCognitiveAnnotation
  parser: https://github.com/huji-nlp/tupa
  task summary paper: https://arxiv.org/abs/1903.02953
claims:
- id: task-context
  kind: context
  text: SemEval 2019 Task 1 established a shared task on parsing into UCCA (Universal Conceptual
    Cognitive Annotation) in English, German and French. It extends the semantic parsing shared-task
    tradition of SDP and AMR to a scheme with reentrancy, discontinuity and non-terminal semantic
    units.
  scope: A call for participation issued in 2018, before the competition ran; the actual task
    results and participating systems are reported separately in the SemEval 2019 Task 1 summary
    paper.
- id: crosslingual-context
  kind: context
  text: The SemEval 2019 UCCA task is a reference point for cross-lingual semantic parsing
    with almost no target-language training data. Its French setting deliberately provides
    only development and test sets, expecting cross-lingual transfer or structure projection
    over a parallel corpus.
  scope: One language triple (English, German, French) and one representation scheme (UCCA
    foundational layer); the low-resource design applies only to the French setting, while
    English and German have training data.
- id: settings
  text: 'SemEval 2019 Task 1 evaluates UCCA parsers in 4 settings: English in-domain, English
    out-of-domain, German in-domain and French with no training data. The settings are split
    into open and closed tracks for a total of 7 competitions, and a team may enter between
    1 and 7 of them.'
  evidence: Section 6
  scope: The French setting is open-track only, as no pilot study existed for it; closed-track
    systems may use only the distributed gold UCCA annotation plus spaCy annotation and fastText
    embeddings.
  kind: result
- id: corpora-size
  text: The English Wiki UCCA corpus used for SemEval 2019 Task 1 contains 5225 sentences
    and about 160K tokens. The German 20K Leagues corpus contributes 6004 sentences and about
    136K tokens across train, development and test.
  evidence: Section 4 and Table 1
  scope: Counts cover the UCCA foundational layer only, the sole layer with annotated corpora
    at the time; the English 20K Leagues out-of-domain test set adds about 12K tokens and
    French has development and test sets only.
  kind: result
- id: graph-stats
  text: 'UCCA graphs are only mildly non-tree-like: in the English Wiki training set 1.75%
    of edges are remote, while 2.38% of nodes are reentrant, 0.54% discontinuous and 0.52%
    implicit.'
  evidence: Table 1
  scope: English Wiki training split, counts excluding the root node; across the other splits
    and languages remote edges range from 1.00% to 2.36% and implicit nodes reach 1.56%.
  kind: result
- id: tupa-baseline
  text: TUPA with a BiLSTM classifier reaches 73.6% labeled F1 on primary edges and 51.5%
    on remote edges on the English Wiki in-domain UCCA test set. The sparse-perceptron variant
    reaches only 64.1% primary and 16% remote F1.
  evidence: Table 2
  scope: Version 1.2 of the English Wiki test set; labeled precision, recall and F1 over edges
    with matching yields and labels, disregarding implicit nodes.
  kind: result
- id: ensemble-poe
  text: An ensemble of 3 BiLSTM TUPA models combined by Product of Experts gives the best
    in-domain primary-edge score in the UCCA pilot task at 75% F1. It does not improve remote
    edges, scoring 48.7% F1 versus 51.5% for a single BiLSTM model.
  evidence: Table 2
  scope: Unpublished pilot experiment on v1.2 of the English Wiki test set; the 3 models differ
    only in random seed. Out-of-domain the ensemble reaches 69.6% primary and 28% remote F1
    on the 20K Leagues test set.
  kind: result
- id: conversion-tree
  text: Converting UCCA to bilexical trees and parsing with a stack-LSTM dependency parser
    reaches 69.9% labeled F1 on primary edges in the English in-domain pilot setting. It produces
    no remote edges at all, because its output is a tree.
  evidence: Table 2
  scope: v1.2 of the English Wiki test set; the bilexical tree conversion caps recoverable
    primary structure at a 91% F1 upper bound. DAGParser, TurboParser, UPARSE and MaltParser
    score lower on primary edges.
  kind: result
- id: mtl-gains
  text: Multitask learning with Universal Dependencies as auxiliary task raises TUPA's remote-edge
    labeled F1 from 13.9% to 20.3% on French and from 27.1% to 35.5% on German UCCA test data.
    Primary-edge F1 rises from 67.6% to 70.1% on French and 72.5% to 73.2% on German.
  evidence: Table 3
  scope: v1.0 of the French 20K Leagues test set and v0.9 of the German 20K Leagues test set,
    both trained in-domain despite the small French corpus; only UD is used as auxiliary task
    for these two languages.
  kind: result
- id: dag-f1
  text: SemEval 2019 Task 1 scores UCCA parses with DAG F1, counting two edges as matching
    when their child nodes cover the same set of tokens and carry the same label. DAG F1 reduces
    to standard parsing F1 when both graphs are trees.
  evidence: Section 6
  scope: The official measure disregards implicit nodes; an extension matching implicit units
    by parent yield is proposed but is not the scored default. Fine-grained scores are also
    reported per category set.
  kind: result
- id: applications
  text: 'UCCA-based evaluation measures already exist for 3 text-to-text generation tasks:
    HUME for machine translation, SAMSA for text simplification and USim for grammatical error
    correction. All 3 depend on UCCA structures obtained by annotation or parsing.'
  evidence: Section 3
  scope: HUME is a human evaluation measure over 4 language pairs; SAMSA and USim were the
    first structural measure for simplification and the first reference-less meaning-preservation
    complement for grammatical error correction respectively, as of 2018.
  kind: result
qa:
- q:
  - What is a good starting point for reading about UCCA semantic parsing?
  - Which shared task covers cross-lingual semantic parsing with UCCA?
  - Where did the SemEval task on UCCA parsing come from?
  answers:
  - task-context
  - crosslingual-context
- q:
  - Which languages and settings does the SemEval 2019 UCCA parsing task cover?
  - How many tracks and competitions were there in SemEval 2019 Task 1?
  - What is the difference between the open and closed track in the UCCA parsing shared task?
  answers:
  - settings
- q:
  - How much annotated UCCA data is available for English, German and French?
  - What is the size of the Wiki and 20K Leagues UCCA corpora?
  - Is there training data for French UCCA parsing?
  answers:
  - corpora-size
  - crosslingual-context
- q:
  - How often do reentrant, discontinuous and implicit units actually occur in UCCA corpora?
  - What fraction of UCCA edges are remote edges?
  - How non-tree-like are UCCA graphs in practice?
  answers:
  - graph-stats
- q:
  - How well does TUPA parse UCCA in English?
  - What baseline scores should a UCCA parser beat?
  - What F1 does the transition-based UCCA parser get on the English Wiki test set?
  answers:
  - tupa-baseline
- q:
  - Does ensembling help UCCA parsing?
  - Do multiple BiLSTM models combined by Product of Experts improve remote-edge prediction?
  answers:
  - ensemble-poe
- q:
  - Can existing dependency or constituency parsers be reused for UCCA parsing via format
    conversion?
  - How well do conversion-based approaches work for UCCA parsing?
  - Why can a tree parser not recover UCCA remote edges?
  answers:
  - conversion-tree
- q:
  - Does multitask learning help low-resource semantic parsing into UCCA?
  - How much does using Universal Dependencies as an auxiliary task help French and German
    UCCA parsing?
  - What improves remote-edge parsing for languages with little UCCA data?
  answers:
  - mtl-gains
- q:
  - How are UCCA parses evaluated?
  - What is DAG F1 and how is edge matching defined for UCCA?
  - Does the UCCA shared-task scoring measure handle implicit units?
  answers:
  - dag-f1
- q:
  - What is UCCA used for besides parsing research?
  - Which evaluation measures for generation tasks are built on UCCA?
  - Why would better UCCA parsers help machine translation or simplification evaluation?
  answers:
  - applications
misreadings:
- The arXiv document 1805.12386 is a call for participation, not a report of SemEval 2019
  Task 1 outcomes; the participating systems and official results appear in the separate task
  summary paper at arXiv:1903.02953.
- The scores in the pilot task tables are baseline results from prior TUPA work and conversion-based
  parsers, not results submitted by shared-task participants.
- The French setting of SemEval 2019 Task 1 provides no training data, so the French numbers
  reported for TUPA come from a pilot experiment that split the small French 20K Leagues corpus,
  and are not obtained under the shared task's own zero-training-data condition.
- The shared task targets only UCCA's foundational layer, the single layer for which annotated
  corpora existed, not the full multi-layer UCCA scheme.
- 'High primary-edge F1 does not imply the harder structures are solved: remote-edge F1 stays
  far lower, and tree-based conversion approaches score 0 on remote edges.'
terminology:
  UCCA: Universal Conceptual Cognitive Annotation, a cross-linguistically applicable semantic
    representation scheme that encodes utterances as directed acyclic graphs whose terminals
    are text tokens and whose non-terminals are semantic units, built on Basic Linguistic
    Theory typology.
  remote edge: In UCCA, an edge that lets a unit participate in more than one super-ordinate
    relation, creating reentrancy and turning the graph into a DAG, as opposed to primary
    edges which form a tree in each layer.
  implicit unit: A node in a UCCA graph with no corresponding token in the text, such as the
    unexpressed agent of a predicate.
  Scene: 'The basic notion of UCCA''s foundational layer: a state, action, movement or other
    relation evolving in time, containing one main relation marked as a Process or a State
    plus one or more Participants.'
  DAG F1: The harmonic mean of labeled precision and recall over graph edges, where two edges
    match if their child nodes have identical sets of leaf (token) descendants and identical
    labels; it collapses to ordinary parsing F1 when both graphs are trees.
  TUPA: A neural transition-based parser for UCCA that produces directed acyclic graphs, used
    as the baseline system for SemEval 2019 Task 1.
  closed track: A shared-task submission condition permitting only the distributed gold UCCA
    annotation in the target language plus specified automatic resources — spaCy POS tags,
    dependency relations and named entities, and fastText word embeddings.
  20K Leagues corpus: An English-French-German parallel UCCA corpus based on Twenty Thousand
    Leagues Under the Sea, manually annotated for the whole book on the German side and for
    the first five chapters on the English and French sides.
---
