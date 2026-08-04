# Working with collaborators

Duplicating a **pointer** to a paper page is pure gain. Duplicating the **page**
splits authority and can trip Scholar's duplicate-title drop. So exactly one party
owns each paper's canonical page and sidecar, and everyone else links to it.
Background: [SHARED.md §10](SHARED.md#10-duplication-which-kind-helps-which-kind-hurts).

## The protocol

Deliberately dumb — no server, no registry, no accounts. Each participant
publishes a static JSON file at a stable URL saying which papers they claim.

```
https://borgr.github.io/paper-geo.json
```

```json
{
  "paper_geo_manifest": 1,
  "owner": "borgr",
  "name": "Leshem Choshen",
  "orcid": "0000-0002-0085-6496",
  "canonical_url": "https://borgr.github.io",
  "claims": [
    {
      "ids": ["doi:10.52202/075280-0310", "arxiv:2306.01708"],
      "title": "TIES-Merging: Resolving Interference When Merging Models",
      "canonical_page": "https://borgr.github.io/papers/ties-merging-.../",
      "has_sidecar": true
    }
  ]
}
```

List your collaborators' manifest URLs in `config.yaml`:

```yaml
collaboration:
  me: borgr
  peers:
    - https://coauthor.github.io/paper-geo.json
```

Then every run reconciles automatically:

| Situation | What happens locally |
|---|---|
| A peer claims it | `canonical_page` → theirs; we generate a **link**, not a page |
| We claim it | we own it: generate the page, own the sidecar |
| Nobody claims it | left unclaimed, with a suggested owner. **We never auto-claim** |
| Two parties claim it | **flagged, never auto-resolved** — this is the exact harm being prevented |

```bash
python scripts/ownership.py              # fetch peers, reconcile, report
python scripts/ownership.py --manifest   # write ours for peers to read
python scripts/ownership.py --claim-all  # claim everything still unclaimed
```

Not auto-claiming is the important default. Silently claiming a paper a co-author
is about to claim is precisely how two canonical pages come to exist.

A peer who doesn't run this tool at all can hand-write six lines of JSON and
participate. That's the point of keeping the format this thin.

## Who should own a paper

Advisory, and the tool only ever suggests:

- **First or corresponding author**, usually — they wrote the claims and can rank
  which limitation actually binds.
- **Whoever has the stronger web presence**, when that differs sharply. The
  canonical page benefits from sitting on the better-crawled domain.
- **A project site**, for a multi-paper project (BabyLM, TextArena, EvalEval). One
  site owning a coherent cluster beats the same pages scattered across authors.
- **You**, for anything nobody else will maintain. An unmaintained canonical page
  is worse than no canonical page.

## What everyone else does — and it's most of the value

Non-owners are not passive. Per paper they should:

1. **Link** to the canonical page from their README, personal site, and profile.
2. **Reuse the claim sentence verbatim** from the owner's sidecar. Not a
   paraphrase — a paraphrase creates a competing near-duplicate of the same
   finding (SHARED.md §5).
3. **List the paper** in their own ORCID / Semantic Scholar / DBLP. This is the
   scholarly graph, where every co-author listing a paper is expected and correct.
   It is not duplication.
4. **Not** publish their own page for it.

Items 1 and 2 are where the gain comes from. See below.

## How much better is this than "only one person runs the code"?

Honestly: **for coverage, not at all. For inbound pointers and for damage
prevention, materially.** Worth separating, because the answer differs by paper.

**No gain (be clear about this).** If you run it on your whole corpus and no
collaborator ever runs anything, every one of your papers already has a canonical
page. The protocol adds nothing to coverage. "One person runs it" is simpler and
equivalent.

**Real gain 1 — inbound pointers.** With the protocol, a 5-author paper's canonical
page is linked from 5 independent accounts and domains instead of 1. Independent
mentions correlate with AI-Overview visibility at 0.664 vs 0.218 for backlinks
**[C, vendor-chained]** — so this is the strong kind of asset, and it is the *only*
way to get it, because you cannot post in someone else's README. Scales with
author count: negligible for a solo paper, largest for your big multi-author
collaborations.

**Real gain 2 — claim corroboration.** N co-authors asserting the identical claim
sentence is N independent sources agreeing, which is the mechanism RAG systems
actually reward. Unreachable without coordination, because it requires the *same
words*.

**Real gain 3 — preventing a harm, which may be the biggest.** Without an
agreement, the failure mode isn't inaction, it's a co-author independently
spinning up their own page for the same paper. Then you have two competing
canonical pages, split authority, and a duplicate-title risk. The protocol's
primary function may simply be that it stops the practice from hurting as it
spreads.

**Where it pays, concretely.** Use it for multi-author flagship papers with active
co-authors — the top of `WORKLIST.md`. Don't bother negotiating over the long
tail; claim those yourself and move on. Ten negotiated papers is a good outcome;
135 is a waste of everyone's afternoon.

## Sidecars specifically

One sidecar per paper, **one owner**, shared rather than forked. Two co-authors
independently writing claims for the same paper is the fragmentation problem
multiplied by author count — the worst version of this, because the claims are the
one thing that must be word-identical.

If a co-author wants to contribute claims, they should PR the owner's sidecar, not
write their own.
