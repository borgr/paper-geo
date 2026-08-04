# Identity audit

Live read of the surfaces you do not control. Regenerate with
`python scripts/audit_identity.py`. Every row is checkable without a login,
which is why it can be re-run — the fixes all need one.

| surface | state | |
|---|---|---|
| ORCID works (public) | 117 of 135 | ok |
| ORCID canonical URL | absent | **fix** |
| ORCID name variants | 2 listed | ok |
| ORCID keywords | 0 of 11 | **fix** |
| ORCID lists other personal pages | 1 of 1 | ok |
| ORCID employment/education | 1/1 | ok |
| arXiv registered author | 104 of 105 | **fix** |
| Wikidata author item | Q140867203 | ok |
| Wikidata item complete | 6 gaps | **fix** |
| HF pages indexed | 105 of 105 | ok |
| HF pages claimed | 102 of 104 claimable | **fix** |
| HF pages not claimable (name wrong upstream) | 1 | see arXiv row |
| arXiv records misspelling your name | 2 | **fix** |
| arXiv records omitting you | 1 | **fix** |
| arXiv papers missing from your bibliography | 1 | **check** |
| Semantic Scholar records | 2 | **fix** |

## ORCID researcher URLs point somewhere else

Listed: `https://ktilana.wixsite.com/leshem-choshen`, `https://twitter.com/LChoshen`  
Expected: `https://borgr.github.io`

Two separate problems if one of those is a site-builder page. It competes
with your canonical URL for the same identity — engines cannot fuse two
candidate homepages — and Wix/Squarespace/Notion pages are JS-rendered, so
AI crawlers that do not execute JavaScript see an empty document. Add the
canonical URL, and either delete the other or make it redirect.

## ORCID keywords to add

One of the few facets ORCID exposes for subject search, and free. Multi-word
phrases someone would actually type — `model merging` is a query, `merging`
is not — and no coined names, which have no lexical path from any real
question. The same list fills Google Scholar's five interest slots (pick the
top five). Edit `config.yaml` → `identity.keywords` to change it.

- [ ] natural language processing
- [ ] artificial intelligence
- [ ] evaluation of language models
- [ ] model merging
- [ ] benchmark reliability
- [ ] language model pretraining
- [ ] human feedback
- [ ] language acquisition
- [ ] efficient pretraining
- [ ] machine translation evaluation
- [ ] efficient evaluation

## arXiv: 1 papers you are not registered as author on

The biggest finding here, and a prerequisite rather than a task: you cannot
add a journal-ref to a paper you do not own. Full list and both claim
routes: [arxiv_ownership.md](arxiv_ownership.md).

## Wikidata item Q140867203 exists — a correction and 2 identifiers to add

An alias was stored as one string with its markdown intact (``Choshen, Leshem`, `L. Choshen``), so it matches nothing. Fix that first.

Full diff, plus the Author Disambiguator walkthrough that both links your
papers and clears the 50-edit gate: [wikidata_followup.md](wikidata_followup.md).

## 1 arXiv papers you own are not in your bibliography

Read off `arxiv.org/a/<orcid>`, which is the only place this shows up: the
collector starts from the .bib, so a paper missing there is invisible to
every other check here. Add it to the bibliography (or, if the claim was a
mistake, unclaim it on arXiv).

- [ ] <https://arxiv.org/abs/2604.12843>

## Hugging Face: 0 to index, 2 to claim, 1 blocked

Live counts, not the ones cached in `papers.yaml`. Lists:
[hf_worklist.md](hf_worklist.md).

## arXiv metadata misspells your name on 2 papers

Upstream of every other surface here — Hugging Face, Semantic Scholar,
OpenAlex and Scholar all read arXiv's author list, so one wrong character
creates one wrong author in all of them, holding citations that cannot be
merged back. Details and the fix order:
[arxiv_name_fixes.md](arxiv_name_fixes.md).

