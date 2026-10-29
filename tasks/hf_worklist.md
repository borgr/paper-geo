# Hugging Face paper pages

Live as of the last `python scripts/audit_identity.py` (`--no-names` skips the slow half): **105 claimed**, **0 pending**, **4 to claim**, **2 to index**, **1 blocked upstream**.

Indexing and claiming both need a logged-in browser. An unauthenticated visit
to a paper URL returns 404 and creates nothing (verified on 50 papers — 0
created), which is why this is a list and not a script.

## Index — 2 papers with no page yet

Log in to Hugging Face, then open each link. The visit is what creates
the page. Nothing else to fill in.

- [ ]    0 cites — <https://hf.co/papers/2609.02859> — User Feedback Provides a Unique Signal that LLMs Can not Detect
- [ ]    0 cites — <https://hf.co/papers/2609.19291> — Why Pretraining Fails to Share Cross-Lingual Knowledge

## Claim — 4 pages that exist but are not linked to you

On each page: find your name in the author list and use the claim control
next to it. This is what joins the paper to your HF profile, and what
makes your models and datasets cross-list on it.

- [ ]    1 cites — <https://hf.co/papers/2608.25832> — Skill Issue: Are Skills Language-Invariant in LLMs?
- [ ]    0 cites — <https://hf.co/papers/2609.04173> — Last Translation Benchmark
- [ ]    0 cites — <https://hf.co/papers/2609.37236> — Asking for What Was Never Requested: Horizontal and Vertical…
- [ ]    0 cites — <https://hf.co/papers/2610.29722> — Retrieval Augmented Generation Compositionality

## Blocked upstream — 1 pages you cannot claim

No author string on these pages resembles your name, so there is no claim
control to press. Hugging Face copies its author list from arXiv, so the
fix is on arXiv, not here — see `arxiv_name_fixes.md`. Once the arXiv
metadata is corrected these move to the claim list on a later run.

- <https://hf.co/papers/2602.16429> — TabAgent: Distilling LLM Agent Components into Cheap…
      HF lists: Ido Levy, Eilam Shapira, Yinon Goldshtein, Avi Yaeli, Nir Mashkif, Segev Shlomov

