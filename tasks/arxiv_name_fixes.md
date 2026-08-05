# arXiv author-name problems

Checked **105** arXiv records against your name variants: **2 misspelled**, **0 missing you entirely**.

This is upstream of everything else. Hugging Face, Semantic Scholar, OpenAlex
and Google Scholar all build author identity from arXiv metadata, so a name
that is wrong here is wrong in all of them at once — and it does not read as a
typo to them, it reads as a different person, who then owns that paper's
citations and cannot be merged into you.

## Misspelled — 2

Fix the author list in the arXiv metadata. You must own the paper first
(`arxiv_ownership.md`); metadata changes go through *Update this article*
on your submission page. A name correction is a metadata edit, not a new
version of the paper.

Note the ordering trap: <https://arxiv.org/auth/request-ownership> matches
your name against the author list, and on these papers that list is the
thing that is wrong — so the request can bounce. If it does, ask the
submitting co-author for the paper password instead
(<https://arxiv.org/auth/need-paper-password>), which does not name-match.

- [ ] [`2410.10783`](https://arxiv.org/abs/2410.10783) — reads **Leshem Chosen** — LiveXiv -- A Multi-Modal Live Benchmark Based on Arxiv Paper
- [ ] [`2409.02228`](https://arxiv.org/abs/2409.02228) — reads **Leshem Chosen** — Unforgettable Generalization in Language Models

