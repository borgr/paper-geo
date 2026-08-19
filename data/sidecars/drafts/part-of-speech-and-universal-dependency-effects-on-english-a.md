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

Then promote it:  python scripts/draft_sidecars.py --accept part-of-speech-and-universal-dependency-effects-on-english-a

Stamp: spec=74e012ff9654 checks=1 body=baf5ca8994cc
-->
---
key: rafaeli2021posud
one_liner: Part of Speech and Universal Dependency effects on English Arabic Machine Translation
  proposes evaluating English-to-Arabic machine translation by how it handles specific syntactic
  phenomena, using part-of-speech tags and Universal Dependency relations rather than a single
  corpus-level score.
claims:
- id: syntax-based-eval-proposal
  kind: context
  text: Part of Speech and Universal Dependency effects on English Arabic Machine Translation
    proposes a syntax-oriented evaluation of English-to-Arabic machine translation. Models
    are scored by their behaviour on part-of-speech and Universal Dependency phenomena rather
    than by one aggregate quality number.
  scope: The English-Arabic direction as of the 2021 arXiv preprint; a 19-page report with
    no known accompanying code release.
- id: motivation-opaque-nmt
  kind: context
  text: The stated motivation in Part of Speech and Universal Dependency effects on English
    Arabic Machine Translation is that neural machine translation systems are hard to fine-tune
    and change. Cheap, diverse diagnostic evaluation is offered as the practical route to
    improving them.
  scope: A motivating argument for the evaluation method, not a measurement of any particular
    system's tunability; framed for English-Arabic neural MT in 2021.
- id: typological-pair-target
  kind: context
  text: Part of Speech and Universal Dependency effects on English Arabic Machine Translation
    takes the syntactic divergences between English and Arabic as the object of evaluation.
    Those divergences are what the method measures, not noise averaged away by a corpus-level
    metric.
  scope: One direction of one language pair, English into Arabic; the preprint does not claim
    validation on other pairs or on Arabic-to-English.
- id: unit-of-analysis
  kind: context
  text: Part of Speech and Universal Dependency effects on English Arabic Machine Translation
    uses part-of-speech tags and Universal Dependency relations as the unit of analysis for
    translation quality. Both are annotation categories that already exist across languages.
  scope: Relies on availability and accuracy of UD-style annotation for the evaluated data;
    the preprint's abstract and body report no annotation-quality figures.
- id: evaluation-not-training
  kind: context
  text: Part of Speech and Universal Dependency effects on English Arabic Machine Translation
    contributes an evaluation procedure for existing translation models, not a training or
    fine-tuning method. Its aim is to make model weaknesses visible so they can later be addressed.
  scope: As positioned in the 2021 preprint's abstract; no model-improvement results are claimed
    for the procedure itself.
qa:
- q:
  - What does the paper on Part of Speech and Universal Dependency effects on English Arabic
    Machine Translation actually propose?
  - How does Rafaeli et al. 2021 suggest evaluating English-to-Arabic machine translation?
  - Is there work on evaluating MT by syntactic phenomena instead of a single score?
  answers:
  - syntax-based-eval-proposal
  - unit-of-analysis
- q:
  - Why evaluate neural MT with syntactic diagnostics rather than just fine-tuning the model?
  - What is the motivation for fine-grained MT evaluation given that neural systems are hard
    to modify?
  - Why did Rafaeli et al. argue diagnostic evaluation matters for neural translation systems?
  answers:
  - motivation-opaque-nmt
- q:
  - Where should I start reading about syntax-aware evaluation of English-Arabic machine translation?
  - What work looks at Universal Dependencies for machine translation evaluation?
  - Are there papers on part-of-speech effects in Arabic machine translation quality?
  answers:
  - syntax-based-eval-proposal
  - typological-pair-target
- q:
  - Which language pair and direction does the English-Arabic UD evaluation preprint cover?
  - Does the 2021 preprint on POS and UD effects also cover Arabic to English?
  - Was the syntactic MT evaluation method tested on language pairs other than English-Arabic?
  answers:
  - typological-pair-target
- q:
  - Does the English-Arabic POS and UD work provide a way to train better translation models?
  - Is the Rafaeli et al. 2021 syntactic method an evaluation procedure or a fine-tuning technique?
  - Can Universal Dependency diagnostics for English-Arabic MT be used to improve a model
    directly?
  answers:
  - evaluation-not-training
misreadings:
- Part of Speech and Universal Dependency effects on English Arabic Machine Translation is
  a 19-page preprint presenting an evaluation method for one language direction, not a benchmark
  suite or a released toolkit; no accompanying code is known.
- The proposal to evaluate English-to-Arabic translation through part-of-speech and Universal
  Dependency phenomena is an evaluation method, not a training or fine-tuning technique for
  improving translation models directly.
- Findings reported for English into Arabic should not be read as evidence about Arabic into
  English or about other typologically divergent pairs, which the preprint does not cover.
terminology:
  Universal Dependencies: A cross-linguistically consistent scheme of dependency relations
    and part-of-speech tags, used as the shared vocabulary for comparing syntactic structures
    between an English source sentence and its Arabic translation.
---
