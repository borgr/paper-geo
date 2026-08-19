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

Then promote it:  python scripts/draft_sidecars.py --accept semeval-2019-task-1-cross-lingual-semantic-parsing-with-ucca

Stamp: spec=74e012ff9654 checks=pass body=52c06780dd79
-->
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
- q:
  - What is a good benchmark for multilingual semantic parsing into graph representations?
  - Where should I start reading about UCCA parsing?
  - Which shared task evaluated cross-lingual UCCA semantic parsing?
  answers:
  - task-context
  - cross-lingual-transfer-context
- q:
  - How well can parsers produce UCCA graphs for English?
  - What were the best English UCCA parsing scores in SemEval-2019 Task 1?
  - How much did submitted systems beat the TUPA baseline on English Wikipedia?
  answers:
  - best-english-wiki
  - baseline-beaten-everywhere
- q:
  - Can you parse semantics in a language with almost no annotated training data?
  - How well did French UCCA parsing work with only 15 training sentences?
  - Does cross-lingual transfer help low-resource semantic parsing?
  answers:
  - french-low-resource
  - cross-lingual-transfer-context
- q:
  - How much does out-of-domain text hurt UCCA parsers?
  - What is the in-domain versus out-of-domain gap for English UCCA parsing?
  answers:
  - out-of-domain-drop
- q:
  - Why are reentrancies and DAG structures hard for semantic parsers?
  - How well do UCCA parsers handle remote edges?
  - Did any SemEval-2019 Task 1 systems simply skip remote edges?
  answers:
  - remote-edges-hard
  - corpus-structural-stats
- q:
  - Which UCCA semantic categories are hardest to predict?
  - What did per-category F1 in SemEval-2019 Task 1 show about Ground and Relator edges?
  - Is the Process versus State distinction hard for parsers?
  answers:
  - category-difficulty
- q:
  - What parsing architecture won SemEval-2019 Task 1?
  - Is it better to convert semantic graphs to constituency trees than to parse them directly?
  - What did the HLT@SUDA UCCA parser do differently from the other systems?
  answers:
  - conversion-approach-wins
  - winner-scene-boundaries
- q:
  - How large are the UCCA annotated corpora, and how frequent are discontinuous and reentrant
    structures?
  - What fraction of UCCA edges are remote?
  - How much German UCCA training data was available for SemEval-2019 Task 1?
  answers:
  - corpus-structural-stats
  - best-german
- q:
  - What is the difference between the open and closed tracks in SemEval-2019 Task 1?
  - Which external resources were UCCA parsers allowed to use?
  answers:
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
