# Identity audit

Live read of the surfaces you do not control. Regenerate with
`python scripts/audit_identity.py`. Every row is checkable without a login,
which is why it can be re-run — the fixes all need one.

| surface | state | |
|---|---|---|
| ORCID works (public) | 0 of 135 | **fix** |
| ORCID canonical URL | absent | **fix** |
| ORCID name variants | 2 listed | ok |
| ORCID keywords | 0 of 10 | **fix** |
| ORCID lists other personal pages | 1 of 1 | ok |
| ORCID employment/education | 1/1 | ok |
| arXiv registered author | 48 of 105 | **fix** |
| Wikidata author item | none | **fix** |
| Semantic Scholar records | 2 | **fix** |

## ORCID has 0 public works

Note the *public*: an item set to “trusted parties” is invisible to the
public API, which is the only thing Semantic Scholar, OpenAlex and Crossref
read. So before importing, set **Account settings → Visibility preferences**
to *Everyone*, or the import lands somewhere nothing can see.

Then one upload: *Works → + Add → Add BibTeX* → `tasks/orcid_import.bib`.
Not the DOI form 100 times — every entry in that file now carries a DOI
(missing ones filled from arXiv), and ORCID groups works by identifier, so
the whole file merges with the registry copies instead of duplicating them.

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
- [ ] evaluation of language models
- [ ] model merging
- [ ] benchmark reliability
- [ ] language model pretraining
- [ ] human feedback
- [ ] language acquisition
- [ ] grammatical error correction
- [ ] machine translation evaluation
- [ ] efficient evaluation

## arXiv: 57 papers you are not registered as author on

The biggest finding here, and a prerequisite rather than a task: you cannot
add a journal-ref to a paper you do not own. Full list and both claim
routes: [arxiv_ownership.md](arxiv_ownership.md).

## No Wikidata author item

Searched by ORCID (P496), Semantic Scholar (P4012), Google Scholar (P1960)
and GitHub (P2037) — no item claims any of them. Name search is not used
here on purpose: it returns *paper* items that merely mention you.

Walkthrough: [wikidata_manual.md](wikidata_manual.md).

