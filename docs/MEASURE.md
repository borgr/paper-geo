# Does any of this work?

Three different questions, three different instruments. Conflating them is the
main way GEO work becomes unfalsifiable.

| | Question | Instrument | Trustworthy? |
|---|---|---|---|
| **A** | Did the work get done? | `update.py` counters | Yes — deterministic |
| **B** | Is the work retrieved and cited? | prompt-space panel | Yes, with matched controls |
| **C** | Is the work described *correctly*? | claim-fidelity scoring | Yes — and it's the novel part |

**A is not evidence for B.** "103 papers now have a journal-ref" is a completed
task, not an outcome. Most published GEO case studies stop at A and present it as
B, which is why the field's evidence base is so thin.

---

## A. Infrastructure counters (already running)

Every `update.py` run prints them and `WORKLIST.md` records what's left. Track the
series over time; a regression means something upstream broke.

Diff two runs to see movement:

```bash
git -C . log --oneline -- data/papers.yaml    # each run is a commit
git diff HEAD~1 HEAD -- data/papers.yaml
```

Cost: free. Interpretation: unambiguous. Value as evidence of impact: zero.

---

## B. The prompt-space panel — a real experiment is available here

The design that makes this worth doing: **you have 135 papers, so you have an N.**
Almost nobody attempting GEO does, which is why almost nobody has run a controlled
test. This is the part worth writing up.

### Design

**Unit of analysis:** a (paper, question, engine) triple.

**Treatment:** the sidecar + generated page + Q&A block. Assign at the *paper*
level, stratified by citation-count decile and publication year, half treated and
half held back. Roll the control arm in later — the point of holding it back is
having a same-period comparison, not withholding permanently.

**Why stratify:** citation count is the dominant confound for every outcome here.
An unstratified split would mostly measure "famous papers get cited more".

**Prompts:** 3–5 questions per paper, written from the sidecar's `qa.q` list —
which means writing the sidecars *first*, for both arms, and only publishing the
treated arm's pages. Otherwise the prompt set is contaminated by knowing which
papers you optimised.

**Engines:** ChatGPT (Bing), Claude (Brave), Perplexity (own index), Google AI
Mode. They use different retrieval backends, so per-engine reporting is mandatory
— a pooled number hides the only interesting variation.

**Outcomes, per triple:**

| Outcome | Coding |
|---|---|
| `cited` | your work appears in the citations at all — the retrieval question |
| `primary` | it's the main source of the answer — the selection question |
| `correct` | the claim attributed to you matches your sidecar — the fidelity question |
| `surface` | which URL got cited (arXiv / your site / GitHub / HF / third party) |

`surface` is worth its own attention: it tells you *which* of your surfaces is
doing the work, which no amount of theory will.

**Cadence:** monthly, same day of month, all arms in the same session. Engines
change under you constantly; a matched same-session comparison is the only way to
get a usable baseline out of a moving target.

### Confounds to state rather than pretend away

- **No stable baseline.** Engines change weekly. This is why treatment and control
  must be measured in the *same session*, never against a historical number.
- **No blinding.** The treatment is public. Nothing to do about it; state it.
- **Non-independence.** Papers by the same author on the same topic aren't
  independent draws. Cluster by topic in any test.
- **Sample size.** ~65 treated papers × 4 questions × 4 engines ≈ 1,000 triples per
  round. Enough for a moderate effect, underpowered for a small one. Say so.
- **The prompt set is yours.** You chose questions your work answers. That inflates
  absolute rates and is fine for a treated-vs-control *difference*, but the absolute
  numbers are not generalizable and shouldn't be quoted as if they were.

### What would falsify the whole approach

Worth writing down in advance so the answer means something:

- No `cited` difference between arms after two rounds → the paper-level work
  (Tier 2 of STUDY.md) doesn't move retrieval, and effort should go to Tier 3
  (Wikipedia, READMEs, third-party coverage).
- `cited` improves but `correct` doesn't → the pages are being retrieved and the
  claims ignored. The sidecar format is wrong, not the idea.
- Both improve equally in both arms → something else changed (an engine update,
  a citation milestone). The control arm is what lets you see this at all.

---

## C. Claim fidelity — the distinctive measurement

For work already well known, the failure mode isn't being unfindable. It's being
found and described wrongly: overstated, mis-scoped, or credited to the wrong
sub-claim. Nobody measures this, and the sidecar is the only lever on it.

**Method.** For each paper with a sidecar, ask each engine: *"What did <paper>
find, and under what conditions does it hold?"* Score the answer against the
sidecar's `claims`:

| Score | Meaning |
|---|---|
| 2 | claim correct **and** scope correct |
| 1 | claim correct, scope dropped or overstated |
| 0 | claim wrong, or attributed to the wrong finding |

Scope-dropping is the interesting cell. LLM summaries overstate scientific
conclusions ~5× more often than human ones, so a shift from 1 → 2 is the effect
this whole approach is really claiming, and it's measurable in a way "visibility"
isn't.

Score with a model against the sidecar, then hand-verify a stratified 20% — the
grader is the measurement instrument and needs its own validation.

---

## What can be automated, and what can't

`measure/visibility.py` (not yet written) can: build the prompt set from the
sidecars, hit engines with an API where one exists, record `cited` / `primary` /
`surface` by URL matching, store one row per triple, diff against last month.

It can't: judge `correct` without a grader you've validated, or use ChatGPT's and
Google AI Mode's consumer surfaces, which have no API for this. Those need manual
runs or a browser harness — budget for it, and report which engines were sampled
how.

---

## Cheap instruments worth adding now

- **Referrer analytics** on the site (Plausible or GA4). Referrals from
  `chatgpt.com`, `perplexity.ai`, `claude.ai`, `gemini.google.com` are ground truth
  that an AI answer sent a human to you. Caveat: AI answers frequently don't get
  clicked, so this floors the effect badly — treat a rise as evidence, a flat line
  as uninformative.
- **Scholar / S2 / OpenAlex counters over time**, already collected. Slow, heavily
  confounded, and not attributable to this work — useful as a sanity check that
  nothing broke, not as an outcome.
- **Crawler hits.** GitHub Pages gives no logs. Putting Cloudflare in front would
  show `GPTBot`, `ClaudeBot`, `PerplexityBot`, `OAI-SearchBot` by user-agent —
  the earliest possible signal that P1 has noticed a new page, weeks before any
  answer cites it. Cheapest high-value addition on this list.

---

## Honest prior

Tier 0 and Tier 1 of [../STUDY.md](../STUDY.md) rest on platform documentation and
directly measured gaps — those will work, and B/C are not really needed to justify
them. Tier 2 (pages, sidecars, Q&A) is a plausible transfer from consumer-product
GEO experiments to scholarly retrieval, and that transfer is **untested**. Tier 3
has the best observational evidence and the worst automatability.

So the measurement plan is aimed squarely at Tier 2, because that's the part that
could be wrong. If it is wrong, the experiment says so within two rounds, and the
effort moves to Tier 3.
