# Papers on your Scholar profile that the bibliography does not have

Written by `scripts/scholar_check.py`. Each entry below is a paper Google Scholar
attributes to you and [`https://raw.githubusercontent.com/borgr/publications/master/orig.bib`](https://raw.githubusercontent.com/borgr/publications/master/orig.bib) does not contain, so the pipeline never
received it and no amount of work inside this repo will produce a page for it.

**The fix is upstream, and it is one paste.** Add the entries you want to the source
bibliography, then `python update.py --refresh-bib`. Nothing here writes to that repo:
it is your publication list, and what belongs on it is a claim about your own work.

Two things to check per entry, because neither is decidable from a Scholar row.
**Is it yours** — Scholar merges a namesake's paper into a profile now and then, and a
wrong entry here would become a page under your name. A resolved entry is weaker
evidence than it looks: arXiv and Crossref match on title alone and know nothing about
whose paper it is. **Is the entry right** — a resolved entry carries the index's author
list and venue, not yours; a stub carries only what Scholar displayed, which is a
truncated author list and a venue string that is sometimes an arXiv id.

Patents, theses, blog posts and proceedings volumes never reach this file -- the check
classifies those and reports them apart. An entry marked `UNRESOLVED` was looked for in
all three indexes and found in none, which for a proceedings-only paper usually means
nobody registered it anywhere machine-readable. Pasting that stub as it stands would
put a `TODO` in your bibliography.


## A Statistical Framework for Game-Based AI Evaluation

- 1 citation, 2025, Scholar says *NeurIPS 2025 Workshop on Evaluating the Evolving LLM Lifecycle: Benchmarks …, 2025*
- [the Scholar row](https://scholar.google.com/citations?view_op=view_citation&hl=en&user=8b8IhUYAAAAJ&citation_for_view=8b8IhUYAAAAJ:geHnlv5EZngC)
- **UNRESOLVED** — not in your Semantic Scholar author record, arXiv, Crossref or Semantic Scholar search.

```bibtex
@misc{TODO,
  title        = {A Statistical Framework for Game-Based AI Evaluation},
  year         = {2025},
  note         = {TODO: authors, venue, DOI}
}
```


---

Also absent, and deliberately: *Llm merging: Building llms efficiently through merging*, *True or false? faithful summarization with attribution*. Declined in [`data/declines.yaml`](../data/declines.yaml) — delete the line there and the entry comes back with a resolved BibTeX block like the ones above.
