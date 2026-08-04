# Can we tell whether this works?

Three questions. Two are cheaply and reliably measurable. One — the causal one —
mostly is not, at this scale, and this file says so rather than dressing up an
underpowered design.

| | Question | Instrument | Verdict |
|---|---|---|---|
| **A** | Did the work get done, and is it still done? | counters + validator | **Build it.** Deterministic, free, runs every time |
| **C** | Is the work described *correctly* right now? | claim-fidelity scoring | **Build it.** Diagnostic, not causal — produces a worklist |
| **B** | Did our changes *cause* more citations? | a controlled comparison | **Probably don't.** One design survives scrutiny; even it is marginal |

**A is not evidence for B.** "103 papers now have a journal-ref" is a completed
task. Most published GEO case studies stop at A and present it as B.

---

## Why B is hard here — the arithmetic

The earlier version of this file proposed randomising at the paper level:
sidecar half the corpus, hold half back, compare. That design does not survive
a power calculation.

Suppose the base rate of "your paper is cited in the answer" is 15%, and the
treatment lifts it to 25% — a large effect, +67% relative. With 65 papers per arm:

```
pooled p = 0.20,  SE = sqrt(2 · 0.2 · 0.8 / 65) = 0.070
z = 0.10 / 0.070 = 1.43        ->  power ≈ 30%
n needed for 80% power         ≈  250 papers per arm
```

So: **underpowered by about 4×, for an effect larger than anyone should expect.**

The "1,000 triples per round" framing in the earlier draft was misleading, and
worth correcting explicitly. The unit looks like (paper × question × engine), but
whether a paper gets cited is overwhelmingly a *paper-level* property, so the
intra-cluster correlation is high. With 16 observations per paper and ICC ≈ 0.5,
the variance inflation is `1 + 15(0.5) = 8.5`, and the effective sample size
collapses back to roughly the number of papers. Counting triples does not buy
power when the outcome is a property of the cluster.

The other three objections are also correct, and two of them are fatal:

| Objection | Verdict |
|---|---|
| Can't compare to the past — AI search barely existed then | **Correct.** No historical baseline is usable. Only same-session comparisons work |
| Papers differ too much to compare to each other | **Correct in practice.** Randomisation handles this in expectation, but not at n=65 |
| Compare to other authors? | **Fatal.** Author prominence dwarfs any metadata effect. Do not attempt this |

---

## The one design where the confounds actually cancel

If B is worth anything here, it is this: **move the randomisation below the
paper.**

Write sidecars for *every* paper — you want them regardless. But have each
sidecar's Q&A block cover only a **random half of that paper's questions**. Then
compare `cited` on covered vs uncovered questions **within the same paper**.

Why this fixes the objections:

- Paper prominence, citation count, venue, topic, year, and the whole "me factor"
  are **identical across arms** — they are the same paper. They difference out
  instead of needing to be balanced.
- The unit is a question, not a paper: ~135 papers × 6 questions ≈ 800 questions,
  ~400 per arm, with the contrast taken *within* cluster. This is a paired design,
  so the dominant variance component is removed rather than inflating the estimate.
- Nothing is withheld permanently. You add the uncovered questions afterwards.
- **Spillover biases toward null.** An uncovered question may still be helped by
  the page existing at all, which makes the estimate conservative — the good
  direction for a bet you might otherwise want to believe.

Honest assessment: this is powered for something like a 7–10 percentage-point
within-paper difference, not for a subtle one. It is the only version I would
report, and it is nearly free because the sidecars are work you want anyway. If
that doesn't clear your bar, **skip B.** Choosing not to run a study that would
be uninterpretable is the right call, not a gap.

### What the experiment costs, if the treatment works

The right way to decide is: assume the treatment works, and price the experiment.

**The naive cost looks bad and isn't the real one.** "Half the questions uncovered
for the duration" sounds like forfeiting half the benefit. It isn't, for four
reasons:

1. **Only the marginal layer is withheld.** Every paper still gets its page,
   JSON-LD, links map, abstract, canonical claim sentence, and misreadings. The
   randomised element is *which specific questions get explicit Q&A coverage* — the
   top layer, not the bulk.
2. **Spillover.** An uncovered question is still served by the page's abstract and
   claims, so the control arm is partial-treatment, not zero. (Which is also why
   the estimate is conservative.)
3. **It's a delay, not a forfeit.** After the experiment you add the uncovered
   questions. Against papers with 5–20 year lifespans, delaying half the Q&A
   coverage by one quarter is a rounding error.
4. **It can ride the rollout you were already doing.** You are going to write 135
   sidecars incrementally over months regardless — you will *have* partial coverage
   during that window whether or not you call it an experiment. Randomising which
   questions come first costs approximately nothing extra.

Put a number on it: ~135 papers × ~4 months × half coverage ≈ 270 paper-months of
half-coverage, against a corpus lifetime on the order of 16,000 paper-months.
**Under 2% of lifetime coverage, and recoverable.**

**The real costs are elsewhere, and they're the ones to weigh:**

| Cost | Size |
|---|---|
| Measurement labour | The dominant one. 2 rounds × ~800 questions × 4 engines, and two engines have no API for this — manual runs or a browser harness. Tens of hours, or a build |
| Discipline | Recording the assignment and not back-filling early. Cheap but easy to fumble |
| **Mis-reading a null** | The real hazard. At ~50% power a null is weak evidence, and it would be easy to conclude "Tier 2 doesn't work" when the honest statement is "no *large* effect detected" |

**And the payoff if it doesn't work:** you stop writing sidecars for 135 papers
(~22 hours) and stop maintaining them indefinitely, and you redirect that effort to
Tier 3 where the observational evidence is better. That asymmetry is what makes a
cheap version worth it.

**Recommendation.** Run a deliberately reduced version: randomise question coverage
on the **top ~40 papers only** — the ones you'd sidecar first anyway — for two
rounds, and treat it as a go/no-go pilot rather than an estimate. Powered for
roughly a 12–15pp difference, so it detects "this clearly helps" and nothing
subtler. Pre-commit in writing to reading a null as *no large effect*, not *no
effect*. If even that feels like overhead, skip it — the cost of skipping is that
Tier 2 stays an honest bet, which is a defensible position to hold in public.

**Free second contrast, no extra work:** you will roll sidecars out over time
anyway. Randomise the *order within each citation tier* instead of strictly by
citation count. You still do high-citation papers early, but you get
contemporaneous treated/untreated pairs matched on tier — a stepped-wedge design
for the price of shuffling a list.

### If you skip B

Then the honest framing of the whole project is: Tier 0 and Tier 1 of
[../STUDY.md](../STUDY.md) rest on platform documentation and directly measured
gaps and need no experiment. Tier 2 (pages, sidecars, Q&A) is a **bet on a
plausible mechanism**, held because it is cheap and because its secondary payoff
(fidelity, measured by C) is real and separately checkable. Say that in public
rather than implying a result nobody has.

---

## A. Structural and format checks — build these

Cheap, deterministic, and they cover exactly what you said: format and structure.
They verify the work exists and stays existing, which is a real class of failure
(metadata gets reverted, pages 404, an index re-splits a profile).

Already running, printed by every `update.py`:

- coverage counters: journal-ref, HTML surface, HF page, sidecar, verbatim BibTeX
- `scripts/validate.py` against `schema/*.json` — malformed edits fail loudly
- the cross-check jsonschema can't express: every `qa.answers` id resolves to a
  real claim

Worth adding, all mechanical:

| Check | Catches |
|---|---|
| Every URL in `links` returns 200 | link rot, ar5iv outages, moved publisher pages |
| Highwire tags present and complete on each generated page | Scholar silently ignoring a page for a missing mandatory tag |
| JSON-LD parses and validates as `ScholarlyArticle` | markup errors that make structured data worthless |
| `sameAs` on the site ⊇ `links` in the data | a surface we know about but never asserted |
| Abstract visible without JS on each page | the SPA failure mode — fine in Google, empty to Claude |
| Robots/CDN allow `GPTBot`, `OAI-SearchBot`, `ClaudeBot`, `PerplexityBot` | silent exclusion from three of four engines |
| One canonical page per paper, no duplicate titles across our own surfaces | Scholar's documented duplicate-title drop |
| Claim text identical across page, README, and model card | corroboration fragmenting through drift |

That last one is the interesting structural test: it enforces the "say it the same
way" rule mechanically instead of by discipline.

---

## C. Claim fidelity — build this, but as a diagnostic

Reframing from the earlier draft, because it matters: **C does not need to be an
experiment to be useful.** Asked as "which of my papers are currently being
described wrongly?", it produces a ranked worklist — actionable regardless of
whether we can attribute the improvement to anything.

Method: for each paper with a sidecar, ask each engine *"What did <paper> find,
and under what conditions does it hold?"* Score against the sidecar's `claims`:

| Score | Meaning |
|---|---|
| 2 | claim correct **and** scope correct |
| 1 | claim correct, scope dropped or overstated |
| 0 | claim wrong, or attributed to the wrong finding |

The 1s are the interesting cell — claim right, scope gone. That is the documented
failure mode (LLM summaries overstate scientific conclusions ~5× more often than
human ones) and it is the thing the sidecar is actually for.

Grade with a model against the sidecar, then hand-check a stratified 20%: the
grader is the instrument and needs its own validation before its output means
anything.

Run it on the top 20 papers, monthly. Output: a list of papers to fix, not a
p-value. If a paper scores 0 repeatedly, that is a concrete bug in how the work is
represented, and worth chasing independent of any theory about why.

---

## Cheap instruments worth adding regardless

- **Crawler hits.** Cloudflare in front of the site would show `GPTBot`,
  `ClaudeBot`, `PerplexityBot`, `OAI-SearchBot` by user-agent — the earliest
  possible signal that a page has been noticed, weeks before any answer cites it.
  Highest value per unit of effort on this list. GitHub Pages gives no logs.
- **Referrer analytics** (Plausible/GA4). Referrals from `chatgpt.com`,
  `perplexity.ai`, `claude.ai` are ground truth that an AI answer sent a human to
  you. AI answers frequently aren't clicked, so a rise is evidence and a flat line
  is uninformative.
- **Scholar / S2 / OpenAlex counters over time.** Already collected. Slow, heavily
  confounded, not attributable. Useful as a tripwire that something broke, not as
  an outcome.
