# Hugging Face paper pages

Live as of the last `python scripts/audit_identity.py` (or `hf_papers.py --live`): **102 claimed**, **0 pending**, **2 to claim**, **0 to index**, **1 blocked upstream**.

Indexing and claiming both need a logged-in browser. An unauthenticated visit
to a paper URL returns 404 and creates nothing (verified on 50 papers — 0
created), which is why this is a list and not a script.

## Claim — 2 pages that exist but are not linked to you

On each page: find your name in the author list and use the claim control
next to it. This is what joins the paper to your HF profile, and what
makes your models and datasets cross-list on it.

- [ ]   18 cites — <https://hf.co/papers/2410.10783> — LiveXiv - A Multi-Modal live benchmark based on Arxiv papers content
- [ ]    4 cites — <https://hf.co/papers/2409.02228> — Unforgettable Generalization in Language Models

## Blocked upstream — 1 pages you cannot claim

No author string on these pages resembles your name, so there is no claim
control to press. Hugging Face copies its author list from arXiv, so the
fix is on arXiv, not here — see `arxiv_name_fixes.md`. Once the arXiv
metadata is corrected these move to the claim list on a later run.

- [ ] <https://hf.co/papers/2507.08924> — From KMMLU-Redux to Pro: A Professional Korean Benchmark Sui
      HF lists: Seokhee Hong, Sunkyoung Kim, Guijin Son, Soyeon Kim, Yeonjung Hong, Jinsik Lee

