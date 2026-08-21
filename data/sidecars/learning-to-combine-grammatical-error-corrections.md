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
- ask:
    plain: how can several grammar checking programs be pooled into one better corrector without
      touching their code?
    jargon: what work introduces system-agnostic combination of GEC outputs using only M2
      edit files?
    task: how do I combine the outputs of several grammatical error correction tools that
      I only have text output from?
    practitioner: I have three grammar correctors and no access to their models, is there
      published research telling me how to fuse their corrections?
  answered_by:
  - context-blackbox
  - context-direct-f
- ask:
    plain: does pooling the corrections of several grammar checkers beat just using the strongest
      one?
    jargon: what F-0.5 does learned per-error-type edit selection reach over BEA 2019 shared
      task system outputs?
    task: how much score can I gain on the BEA 2019 test set by combining published system
      outputs instead of training a better model?
    practitioner: if I already have the best available grammar correction system, is it worth
      combining it with weaker ones?
  answered_by:
  - open-phase-sota
  - precision-gain-shared-task
- ask:
    plain: when you have several neural models correcting the same sentence, is picking corrections
      per error type better than averaging the models?
    jargon: does per-error-type edit selection outperform decoder-side average ensembling
      of 4 RNN Nematus GEC models?
    task: how should I combine 4 neural grammar correction checkpoints, ensemble decoding
      or output-level edit selection?
    practitioner: should I ensemble my grammar correction models at decoding time or combine
      their corrected sentences afterwards?
  answered_by:
  - beats-ensemble
- ask:
    plain: when several grammar correction tools are pooled, does accuracy go up only because
      fewer corrections are made?
    jargon: does per-error-type combination of neural GEC, spellchecking and masked-LM systems
      raise precision and recall together?
    task: how do I add a spellchecker and a weak corrector to my neural grammar correction
      models without losing recall?
    practitioner: will adding a weak grammar correction component to my pipeline drag down
      the corrections I already get right?
  answered_by:
  - combination-raises-both
  - offtheshelf-gain
- ask:
    plain: do consumer grammar checking tools add anything to a research grammar correction
      system?
    jargon: what does adding off-the-shelf checkers as black boxes contribute to a restricted-track
      GEC combination?
    task: how do I get extra F-0.5 out of commercial grammar checkers alongside my own trained
      corrector?
    practitioner: is it worth paying for a commercial grammar checker to plug into my correction
      pipeline?
  answered_by:
  - offtheshelf-gain
- ask:
    plain: can one grammar checker be improved just by ignoring the mistake categories it
      handles badly?
    jargon: how much F-0.5 does per-error-type filtering of a single GEC system's edits recover?
    task: how do I raise a single grammar corrector's score without retraining it?
    practitioner: if I only have one grammar correction tool, is discarding its weak error
      types worth doing?
  answered_by:
  - single-system-filtering
- ask:
    plain: if two grammar checkers suggest the same fix, is that fix more likely to be right?
    jargon: how does precision on common edits compare with standalone precision for neural
      GEC and a commercial checker on R:OTHER?
    task: how do I decide when to keep only the corrections that two systems agree on?
    practitioner: should I only apply the grammar corrections my two tools both propose?
  answered_by:
  - agreement-precision
- ask:
    plain: is the improvement from pooling two grammar checkers a fluke of how the tuning
      data was split?
    jargon: how much does the F-0.5 gain from a 2-system GEC combination vary across random
      dev-set fold partitions?
    task: how do I check that a gain from combining two correction systems is not an artefact
      of my dev-set split?
    practitioner: can I trust the gain I measure from combining two grammar correctors on
      one dev split?
  answered_by:
  - pair-stability
- ask:
    plain: which spelling correction tool fixes learner writing mistakes best?
    jargon: how does a frequency-and-Levenshtein spellchecker score on R:SPELL edits against
      JamSpell, Norvig and Enchant?
    task: how do I get the strongest spelling correction component for a grammatical error
      correction pipeline?
    practitioner: should I build my own word-frequency spellchecker or install an existing
      one for correcting learner English?
  answered_by:
  - spellchecker-spelling
- ask:
    plain: can a pretrained language model fix grammar mistakes on its own by guessing masked
      words?
    jargon: what F-0.5 does iterative masked-LM querying of BERT reach as a standalone GEC
      system?
    task: how well can I correct grammatical errors by repeatedly masking tokens and taking
      BERT's predictions?
    practitioner: should I expect a masked language model alone to work as a grammar corrector?
  answered_by:
  - bert-negative
- ask:
    plain: can artificially corrupted sentences stand in for real annotated writing errors
      when training a corrector?
    jargon: how does synthetic error generation over in-domain W&I sentences compare with
      real W&I training data for a Nematus GEC model?
    task: how do I train a grammar correction model when I have little annotated learner data,
      and does the source text domain matter?
    practitioner: should I generate millions of synthetic errors from generic text or a smaller
      amount from in-domain sentences?
  answered_by:
  - synthetic-domain
- ask:
    plain: does piling on more learner-writing corpora help a grammar correction model, or
      does it swamp the data you care about?
    jargon: what happens to Nematus GEC F-0.5 when Lang8, FCE and NUCLE are added to W&I with
      and without upsampling?
    task: how do I mix extra grammatical error correction corpora into my training data without
      losing target-domain accuracy?
    practitioner: should I add Lang8, FCE and NUCLE to my W&I training set, and do I need
      to upsample W&I?
  answered_by:
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
