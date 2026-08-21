---
key: hershcovich2019semeval
one_liner: SemEval-2019 Task 1 is a shared task on parsing text into UCCA semantic graphs
  in English, German and French, with 8 submitted systems, a French track containing only
  15 training sentences, and the TUPA transition-based parser as baseline.
claims:
- id: best-english-wiki
  kind: result
  text: On the English-Wiki in-domain track of SemEval-2019 Task 1, HLT@SUDA reached 77.4
    labeled F1 over all edges in the closed track and 80.5 in the open track. The TUPA baseline
    scored 72.8 and 73.5 in those tracks.
  scope: Labeled F1 over primary and remote edges together, English Wikipedia UCCA corpus
    test set; the open-track score uses BERT, which the closed track disallowed.
  evidence: Table 4
- id: best-german
  kind: result
  text: German-20K UCCA parsing reached 83.2 labeled F1 in the closed track and 84.9 in the
    open track (HLT@SUDA), above the TUPA baseline's 73.1 and 79.1.
  scope: German Twenty Thousand Leagues corpus, 5,211 training sentences; open track allowed
    any external resource.
  evidence: Table 4
- id: french-low-resource
  kind: result
  text: With only 15 annotated French training sentences, the best system in the French-20K
    track reached 75.2 labeled F1, versus 48.7 for the TUPA baseline (HLT@SUDA, second place;
    CUNY-PekingU ranked first).
  scope: French Twenty Thousand Leagues corpus, open track only; English and German UCCA annotation,
    multilingual embeddings and unannotated English-French parallel text were permitted.
  evidence: Table 4
- id: baseline-beaten-everywhere
  kind: result
  text: At least one submitted system beat the TUPA baseline in every one of the 7 competitions
    of SemEval-2019 Task 1, spanning English in-domain, English out-of-domain, German and
    French settings.
  scope: 4 settings times 2 tracks minus the French closed track; CUNY-PekingU was disqualified
    from the open tracks after using evaluation data in training.
  evidence: Table 4
- id: out-of-domain-drop
  kind: result
  text: Moving from in-domain English Wikipedia to out-of-domain 20K Leagues text costs the
    best UCCA parser about 4 to 5 labeled F1. HLT@SUDA scores 72.7 closed and 76.7 open on
    English-20K, versus 77.4 and 80.5 on English-Wiki.
  scope: Both settings train on English Wikipedia UCCA; the out-of-domain test set is 492
    sentences of literary prose.
  evidence: Table 4
- id: remote-edges-hard
  kind: result
  text: Remote edges in UCCA remain far harder to parse than primary edges. The best English-Wiki
    closed-track system scores 52.2 labeled F1 on remote edges against 77.9 on primary edges.
  scope: English Wikipedia closed track; several submitted systems (DANGNT@UIT.VNU-HCM, GCN-Sem,
    UC Davis) produced no remote edges at all and score 0 there.
  evidence: Table 4
- id: category-difficulty
  kind: result
  text: Across all tracks of SemEval-2019 Task 1, Relator edges were the easiest UCCA category
    to parse and Ground edges the hardest. The best labeled F1 reaches 93 on Relators, while
    several systems score 0 on Ground.
  scope: Per-category labeled F1 for the 8 submitted systems plus the TUPA baseline; Ground
    is 0.03% to 0.57% of edges in the corpora.
  evidence: Figure 3
- id: winner-scene-boundaries
  kind: result
  text: The winning HLT@SUDA system's largest per-category advantage was on Parallel Scene
    and Linker edges, indicating that identifying Scene boundaries separated it most from
    the other UCCA parsers.
  scope: Per-category labeled F1 comparison across tracks; HLT@SUDA converts UCCA graphs to
    constituency trees and uses BERT in the open tracks.
  evidence: Figure 3
- id: conversion-approach-wins
  kind: result
  text: The top-scoring approach in 6 of the 7 tracks of SemEval-2019 Task 1 converted UCCA
    graphs into constituency trees rather than parsing the DAG directly with a transition
    system. Remote and discontinuous edges were recovered by classification in a multi-task
    framework.
  scope: HLT@SUDA took first place in the 6 English and German tracks and second in the French
    open track, where CUNY-PekingU's TUPA ensemble ranked first.
  evidence: Table 4
- id: corpus-structural-stats
  kind: result
  text: 'The UCCA corpora used in SemEval-2019 Task 1 are sparse in the structures that make
    parsing hard: remote edges are 2.60% to 3.21% of all edges. Discontinuous non-terminals
    range from 1.71% in English-Wiki to 8.87% in German-20K, and reentrant non-terminals from
    0.31% to 1.84%.'
  scope: English-Wiki, English-20K, French-20K and German-20K corpora, UCCA foundational layer
    only, with Time and Quantifier labels replaced by Adverbial and Elaborator.
  evidence: Table 3
- id: task-context
  kind: context
  text: SemEval-2019 Task 1 established a public multilingual benchmark for UCCA semantic
    parsing. It released the English Wikipedia and English, French and German Twenty Thousand
    Leagues corpora, an official evaluation script, and a cross-lingual low-resource French
    track.
  scope: UCCA foundational layer only, the only layer with annotated corpora as of 2019; English,
    German and French; before the task TUPA was the only available UCCA parser.
- id: cross-lingual-transfer-context
  kind: context
  text: SemEval-2019 Task 1 provides evidence that cross-lingual transfer is an effective
    route to UCCA parsing in languages with almost no annotation, exploiting UCCA's tendency
    to be preserved under translation. The task is a starting point for work on low-resource
    semantic parsing.
  scope: Demonstrated for French with 15 training sentences and helped German as well; the
    source languages were English and German, and the target corpus was a translation of the
    same book, so results may not extend to typologically distant languages or unrelated domains.
qa:
- ask:
    plain: which shared task released multilingual data and scores for parsing sentences into
      meaning graphs?
    jargon: what benchmark exists for cross-lingual UCCA semantic graph parsing with an official
      evaluation script?
    task: where can I find annotated corpora and a scoring script to start working on multilingual
      semantic graph parsing?
    practitioner: if I want to benchmark my semantic parser across several languages, which
      shared task data should I use?
  answered_by:
  - task-context
  - cross-lingual-transfer-context
- ask:
    plain: how accurately can software turn English Wikipedia sentences into meaning graphs?
    jargon: what labeled F1 did the top UCCA parsers reach on the English-Wiki in-domain track,
      and did they clear the TUPA baseline?
    task: how good a score should I expect to have to reach on English UCCA parsing to be
      competitive?
    practitioner: is the transition-based TUPA parser still the strongest option for English
      UCCA, or did submitted systems beat it?
  answered_by:
  - best-english-wiki
  - baseline-beaten-everywhere
- ask:
    plain: can a parser learn to build meaning graphs for a language with only a handful of
      annotated sentences?
    jargon: how well does cross-lingual transfer support UCCA parsing in a low-resource French
      setting with 15 in-language training sentences?
    task: how do I build a semantic parser for a language where I can only afford to annotate
      a few dozen sentences?
    practitioner: should I annotate more data in my target language or rely on transfer from
      English for semantic parsing?
  answered_by:
  - french-low-resource
  - cross-lingual-transfer-context
- ask:
    plain: how much worse do meaning-graph parsers get on text from a different genre than
      they were trained on?
    jargon: what is the in-domain to out-of-domain labeled F1 drop for UCCA parsers between
      Wikipedia and 20K Leagues text?
    task: how much accuracy should I budget for if I run an English UCCA parser on text outside
      Wikipedia?
    practitioner: can I trust published English UCCA parsing scores if my documents are literary
      rather than encyclopedic?
  answered_by:
  - out-of-domain-drop
- ask:
    plain: how well do parsers recover the extra links that let a sentence's meaning graph
      share one word between two parts?
    jargon: how do UCCA parsers score on remote edges relative to primary edges, and how frequent
      are remote and reentrant structures in the corpora?
    task: if I need reentrant and remote links in my semantic parses, how reliable are current
      UCCA parsers at producing them?
    practitioner: is it worth handling remote edges in my UCCA parser, or are they too rare
      and too inaccurate to matter?
  answered_by:
  - remote-edges-hard
  - corpus-structural-stats
- ask:
    plain: which kinds of semantic relations are hardest for parsers to label correctly?
    jargon: how does per-category labeled F1 vary across UCCA edge categories such as Relator
      and Ground?
    task: which UCCA categories should I expect my parser to fail on when I inspect its per-label
      errors?
    practitioner: if my application depends on a specific UCCA relation type, can I count
      on a parser getting that label right?
  answered_by:
  - category-difficulty
- ask:
    plain: what design did the winning system use to turn sentences into meaning graphs, and
      how did it differ from the rest?
    jargon: did tree conversion with multi-task recovery of remote edges outperform transition-based
      DAG parsing in SemEval-2019 Task 1?
    task: should I build a semantic graph parser by converting graphs to constituency trees
      or by parsing the graph directly with a transition system?
    practitioner: I already have a strong constituency parser, is converting UCCA graphs to
      trees a better bet than writing a DAG parser?
  answered_by:
  - conversion-approach-wins
  - winner-scene-boundaries
- ask:
    plain: how much annotated German data was available for meaning-graph parsing, and how
      often do awkward structures like crossing branches appear?
    jargon: what are the corpus statistics for remote edges, discontinuous and reentrant non-terminals
      in the UCCA treebanks, and what German labeled F1 followed?
    task: how do I judge whether the German UCCA training data is large and varied enough
      to train a parser on?
    practitioner: is there enough German UCCA annotation for me to expect usable parsing accuracy?
  answered_by:
  - corpus-structural-stats
  - best-german
- ask:
    plain: does letting a parser use extra pretrained resources change how well it builds
      meaning graphs?
    jargon: how do closed-track and open-track labeled F1 scores compare for UCCA parsing
      on English-Wiki and German-20K?
    task: how much accuracy do I gain by allowing external embeddings and pretrained models
      in a UCCA parser?
    practitioner: if I am restricted to the provided training data only, how much UCCA parsing
      accuracy am I giving up?
  answered_by:
  - best-english-wiki
  - best-german
terminology:
  UCCA: Universal Conceptual Cognitive Annotation, a cross-linguistically applicable semantic
    representation scheme that encodes utterances as directed acyclic graphs whose terminals
    are tokens and whose non-terminals are semantic units.
  Scene: 'In UCCA, the basic unit of analysis: a state, action, movement or other relation
    evolving in time, containing one main relation marked Process or State plus one or more
    Participants.'
  remote edge: In UCCA, an edge that lets a unit participate in more than one super-ordinate
    relation, creating reentrancy and turning the otherwise tree-shaped annotation into a
    directed acyclic graph.
  closed track: A SemEval-2019 Task 1 submission setting restricted to the distributed gold
    UCCA annotation in the target language plus spaCy automatic annotations and fastText embeddings.
  open track: A SemEval-2019 Task 1 submission setting permitting any additional resource,
    including UCCA annotation in other languages and pretrained models such as BERT or ELMo,
    provided no extra gold annotation of the same text is used.
  TUPA: A transition-based DAG parser with a BiLSTM classifier, the only UCCA parser available
    when SemEval-2019 Task 1 was announced and its official baseline.
  cross-lingual parsing: In SemEval-2019 Task 1, parsing text in one language into a meaning
    representation using annotated resources from other languages, as opposed to producing
    a representation whose labels are in another language.
misreadings:
- 'The 75.2 labeled F1 on French does not mean a parser learned UCCA from 15 sentences alone:
  the French track was open-only, and the winning systems used English and German UCCA annotation,
  multilingual embeddings, and the parallel English-French text.'
- The high German scores are not evidence that German is easier than English; the German-20K
  setting has 5,211 in-domain training sentences and is evaluated on the same literary corpus,
  whereas the comparable English out-of-domain setting trains on Wikipedia.
- A system reporting 0 remote-edge F1 in Table 4 did not fail at reentrancy detection; DANGNT@UIT.VNU-HCM
  and GCN-Sem deliberately ignored remote edges and never produce them.
- CUNY-PekingU's first place in the French open track stands, but its open-track results in
  other tracks were disqualified after it was discovered that some evaluation data had been
  used for training.
- SemEval-2019 Task 1 covers only UCCA's foundational layer, not the full multi-layer scheme;
  it was the only layer with annotated corpora at the time.
- GCN-Sem's relatively low official scores should not be read as the model failing at semantic
  parsing, since its scores on the UCCA test sets converted to bi-lexical CoNLL-U were rather
  high, implicating the lossy conversion.
---
