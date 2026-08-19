<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from claude-opus-5 via the Anthropic API, high effort (schema-enforced via a forced tool call) + 1 repair round. Every claim, number
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

Then promote it:  python scripts/draft_sidecars.py --accept learning-to-combine-grammatical-error-corrections

Stamp: spec=74e012ff9654 checks=pass body=73d1aaeed1f7
-->
---
one_liner: A black-box combination method for Grammatical Error Correction that splits two
  systems' edits into agreed and disagreed subsets, then solves a convex program per error
  type to pick which subsets to keep so that F-0.5 is maximized directly.
key: kantor2019combine
claims:
- id: open-phase-sota
  kind: result
  text: Combining four released BEA 2019 shared task system outputs as black boxes reaches
    F-0.5 72.84 on the test set, a 3.7 point gain over the best standalone system (UEDIN-MS,
    69.47). Combining only UEDIN-MS with Kakao&Brain reaches 73.18.
  scope: BEA 2019 shared task test set, open phase; selection variables fitted on the entire
    shared task dev set; the four systems were UEDIN-MS, Kakao&Brain, Shuyao and CAMB-CUED,
    whose outputs the teams released after the test phase.
  evidence: Table 10
- id: precision-gain-shared-task
  kind: result
  text: Combining BEA 2019 shared task systems raises precision from 72.28 to 78.74 on the
    test set, a 6.5 point improvement over the best standalone system, while recall falls
    from 60.12 to 56.04.
  scope: BEA 2019 test set, 4 combined systems (UEDIN-MS, Kakao&Brain, Shuyao, CAMB-CUED);
    optimization targets F-0.5, which weights precision over recall.
  evidence: Table 10
- id: beats-ensemble
  kind: result
  text: Combining 4 RNN Nematus models by error-type edit selection reaches F-0.5 0.3508 against
    0.3122 for Nematus's built-in average ensembling of the same 4 models, a gain of almost
    4 points.
  scope: 4 RNN-based Nematus models differing only in random initialization, scored on one
    random half of the W&I dev set with selection variables fitted on the other half.
  evidence: Table 9
- id: combination-raises-both
  kind: result
  text: Iteratively combining 4 Nematus models, a spellchecker and a BERT-based system raises
    F-0.5 from 0.3429 for the best standalone Nematus to 0.4051. Precision and recall improve
    together, from 0.4839 to 0.5029 and from 0.1583 to 0.2278.
  scope: W&I dev set, restricted track submission; the spellchecker alone scores F-0.5 0.1242
    and the BERT system 0.0135, yet both still add to the combination.
  evidence: Table 7
- id: offtheshelf-gain
  kind: result
  text: Adding LanguageTool, Grammarly and JamSpell as black boxes to the restricted-track
    combination raises F-0.5 from 0.4051 to 0.4375, about 9 points above the best standalone
    off-the-shelf system (Grammarly, 0.3612).
  scope: W&I dev set; Grammarly outputs were collected manually through its free web interface
    taking the top suggestion per correction, since it exposes no programmatic API.
  evidence: Table 8
- id: single-system-filtering
  kind: result
  text: Discarding a single system's predictions on error types where it performs poorly gives
    small F-0.5 gains. LanguageTool rises from 0.2107 to 0.2355, Grammarly from 0.3627 to
    0.3754 and Nematus from 0.373 to 0.3761.
  scope: W&I dev set, filtering fitted on one random half and reported on the other; gains
    are minor for the two stronger systems and largest for the weakest one.
  evidence: Table 6
- id: agreement-precision
  kind: result
  text: 'Edits proposed by both Nematus and Grammarly are far more precise than edits from
    either alone: for R:OTHER, precision is 0.67 on common edits versus 0.17 and 0.28 standalone.
    The optimizer therefore keeps only the agreed edits for that error type.'
  scope: W&I dev set, the 10 most frequent error types over the Nematus–Grammarly pair; agreement
    does not help every type, and for R:PUNCT and R:VERB:TENSE the intersection subset is
    dropped entirely.
  evidence: Table 1
- id: pair-stability
  kind: result
  text: Combining Nematus with Grammarly gives an average F-0.5 improvement of 6.2 points
    over the better of the two systems. The standard deviation across 10 different random
    dev-set fold partitions is 0.28 points.
  scope: W&I dev set split randomly in two, selection variables fitted on one half and scored
    on the other, repeated over 10 partitions.
  evidence: Section 5.4
- id: spellchecker-spelling
  kind: result
  text: A heuristic spellchecker built from Gutenberg word counts, a LibreOffice dictionary
    and Levenshtein-distance-1 candidates reaches F-0.5 0.6378 on R:SPELL edits, above Norvig
    (0.5882), JamSpell (0.5599) and Enchant (0.3544).
  scope: R:SPELL error category only on the W&I dev set; over all error categories the same
    spellchecker scores F-0.5 0.1198, below JamSpell's 0.1593.
  evidence: Table 3
- id: bert-negative
  kind: result
  text: Iteratively querying BERT as a masked language model to propose GEC edits scores F-0.5
    0.0135 as a standalone system. Confidence thresholds between 0.6 and 0.98 gave unsatisfying
    results, and fine-tuning the masked LM on synthetic errors did not help.
  scope: W&I dev set; the submitted variant was restricted to replacement edits inside predefined
    interchangeable word sets, ignoring insertions and deletions and excluding R:PUNCT; the
    system still contributed when combined with others.
  evidence: Table 7
- id: synthetic-domain
  kind: result
  text: Nematus trained on synthetic errors generated over in-domain W&I gold sentences reaches
    F-0.5 0.1919, close to the 0.232 obtained from the real W&I train set. 7,000,000 synthetic
    Gutenberg sentences reach only 0.1294.
  scope: W&I dev set; errors were generated by applying W&I corrections backwards while matching
    the observed distribution of edits per sentence; more Gutenberg data did not help (650,000
    sentences scored 0.1483).
  evidence: Table 5
- id: upsampling
  kind: result
  text: Adding Lang8, FCE and NUCLE to W&I training data only helps Nematus when W&I is upsampled
    10 times. F-0.5 goes from 0.232 (W&I alone) to 0.225 (plus Lang8 and FCE) to 0.333 (upsampled
    W&I plus all three).
  scope: Transformer Nematus with the WMT17 recommended hyperparameters, evaluated on the
    W&I dev set under the BEA 2019 restricted-track data.
  evidence: Table 4
- id: context-blackbox
  kind: context
  text: The BEA 2019 system paper 'Learning to combine Grammatical Error Corrections' introduces
    automatic, system-agnostic combination for Grammatical Error Correction. It learns per
    error type which systems' edits to keep from outputs alone, not from model internals or
    hand-written pipelines.
  scope: As of 2019; earlier GEC combination work existed but was ad-hoc — pipelining, per-phenomenon
    assignment, or rescoring hybrids tailored to the specific systems used — and required
    manual adjustment for each new set of systems.
  evidence: Section 4
- id: context-direct-f
  kind: context
  text: Framing GEC system combination as a convex program over per-error-type edit-subset
    selection variables makes it possible to optimize the corpus-level F-beta score directly,
    using only M2 edit files from each system.
  scope: Requires a dev set with gold M2 annotations from the same distribution as the test
    data, and an error-type classifier such as ERRANT; combining more than 2 systems is iterative.
  evidence: Section 4
qa:
- q:
  - How can I combine the outputs of several grammatical error correction systems?
  - Is there a way to merge GEC system outputs without access to their internals?
  - What should I read about combining grammar correction systems as black boxes?
  answers:
  - context-blackbox
  - context-direct-f
- q:
  - Does combining GEC systems actually beat the best single system?
  - How much does black-box combination improve F-0.5 on the BEA 2019 shared task?
  - What was the top score in the BEA 2019 open phase?
  answers:
  - open-phase-sota
  - precision-gain-shared-task
- q:
  - Is learned edit selection better than average ensembling for neural GEC models?
  - How does combining Nematus RNN models compare with Nematus's built-in ensemble?
  - Does ensembling hurt recall in grammatical error correction?
  answers:
  - beats-ensemble
- q:
  - Does combining GEC systems improve precision at the cost of recall?
  - Can adding a weak grammar correction system still help a combination?
  - What happens when a spellchecker and a BERT-based corrector are combined with Nematus
    models?
  answers:
  - combination-raises-both
  - offtheshelf-gain
- q:
  - Do commercial tools like Grammarly help when combined with a research GEC system?
  - Is there value in adding off-the-shelf grammar checkers to a neural GEC system?
  answers:
  - offtheshelf-gain
- q:
  - Can filtering a single GEC system's error types improve its score?
  - Does throwing away predictions on error types a corrector is bad at help?
  - How large is the gain from error-type filtering of one grammar correction system?
  answers:
  - single-system-filtering
- q:
  - Are grammar corrections that two systems agree on more likely to be right?
  - How much more precise are edits proposed by both Nematus and Grammarly?
  - Should I keep only the corrections that multiple systems propose?
  answers:
  - agreement-precision
- q:
  - How stable is the gain from combining two GEC systems across dev-set splits?
  - Does the improvement from combining Nematus and Grammarly depend on how the dev set is
    split?
  answers:
  - pair-stability
- q:
  - Which spellchecker is best for correcting spelling errors in learner English?
  - How does a simple frequency-plus-edit-distance spellchecker compare to JamSpell and Norvig?
  - Does a good spellchecker also give a good overall grammatical error correction score?
  answers:
  - spellchecker-spelling
- q:
  - Does BERT work well as a standalone grammatical error corrector?
  - Can a masked language model be queried iteratively to fix grammar errors?
  - What went wrong when BERT was applied directly to GEC?
  answers:
  - bert-negative
- q:
  - Does synthetic error generation replace real annotated GEC data?
  - Does the domain of synthetic grammatical errors matter more than the amount?
  - How well does a GEC model trained only on artificially corrupted text do?
  answers:
  - synthetic-domain
- q:
  - Does adding Lang8, FCE and NUCLE help a transformer GEC model?
  - Why upsample the in-domain W&I training set when training a GEC system?
  - What training data mix worked best for Nematus on the W&I dev set?
  answers:
  - upsampling
misreadings:
- 'The spellchecker described in ''Learning to combine Grammatical Error Corrections'' is
  better only at spelling: it wins on R:SPELL edits (F-0.5 0.6378) but scores below JamSpell
  when all error categories are measured (0.1198 vs 0.1593).'
- The BERT-based corrector is a negative result, not a working GEC system — as a standalone
  corrector it reaches F-0.5 0.0135, and the value reported for it is that combination can
  still extract signal from such a weak component.
- The combination method does not require access to model probabilities, logits or training
  data; it operates on M2 edit files produced by each system, which is why commercial tools
  reached only through a web interface can be included.
- The 3.7 point F-0.5 gain reported for combining BEA 2019 shared task systems is a gain over
  the best single participating system, not over an existing combination baseline.
- 'Combining more systems is not monotonically better: combining all 4 released shared task
  systems scores F-0.5 72.84, slightly below the 73.18 obtained by combining just the two
  strongest.'
- Synthetic error generation did not match training on real annotated data — synthetic in-domain
  W&I data reached F-0.5 0.1919 against 0.232 for the real W&I train set, and the paper did
  not enter the low-resource track.
terminology:
  selection variable: A value between 0 and 1 per (error type, edit subset) pair in the combination
    method, giving the probability that an edit of that error type falling in that subset
    is kept in the merged output; in practice rounded to 0 or 1.
  edit subset: A partition of two systems' proposed corrections into edits unique to system
    1, edits unique to system 2, and edits both systems propose, so that every edit belongs
    to exactly one subset.
  iterative combination: Extending pairwise system combination to N systems by combining two
    systems, then treating that merged output as a system to combine with the next, which
    avoids the tiny statistics of 2^N subsets but can overfit the development set.
  M2 file: The standard Grammatical Error Correction annotation format listing, for each source
    sentence, the corrections applied to it, and sufficient to compare a system's edits against
    gold edits.
  black-box combination: Merging grammatical error correction systems using only their corrected
    output text, with no access to model parameters, probabilities or training data.
---
