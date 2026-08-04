# Identity audit

Live read of the surfaces you do not control. Regenerate with
`python scripts/audit_identity.py`. Every row is checkable without a login,
which is why it can be re-run — the fixes all need one.

| surface | state | |
|---|---|---|
| ORCID works (public) | 0 of 135 | **fix** |
| ORCID canonical URL | absent | **fix** |
| ORCID name variants | 0 listed | **fix** |
| ORCID keywords | 0 | **fix** |
| ORCID employment/education | 1/1 | ok |
| arXiv registered author | 48 of 105 | **fix** |
| Wikidata author item | none | **fix** |
| Semantic Scholar records | 2 | **fix** |

## ORCID has 0 public works

Note the *public*: an item set to “trusted parties” is invisible to the
public API, which is the only thing Semantic Scholar, OpenAlex and Crossref
read. So before importing, set **Account settings → Visibility preferences**
to *Everyone*, or the import lands somewhere nothing can see.

Then `tasks/orcid_dois.txt` (Add DOI) or `tasks/orcid_import.bib`

## ORCID researcher URLs point somewhere else

Listed: `https://ktilana.wixsite.com/leshem-choshen`, `https://twitter.com/LChoshen`  
Expected: `https://borgr.github.io`

Two separate problems if one of those is a site-builder page. It competes
with your canonical URL for the same identity — engines cannot fuse two
candidate homepages — and Wix/Squarespace/Notion pages are JS-rendered, so
AI crawlers that do not execute JavaScript see an empty document. Add the
canonical URL, and either delete the other or make it redirect.

## ORCID name variants not listed

*Also known as* is what a disambiguation model matches on when a citation
uses a different form. Add: `Choshen, Leshem`, `L. Choshen`

## ORCID keywords empty

Free, and one of the few facets ORCID exposes for subject search. 5–10
phrases someone would type, not coined names.

## arXiv: 57 papers you are not registered as author on

The biggest finding here, and a prerequisite rather than a task: you cannot
add a journal-ref to a paper you do not own. Full list and both claim
routes: [arxiv_ownership.md](arxiv_ownership.md).

## No Wikidata author item

Searched by ORCID (P496), Semantic Scholar (P4012), Google Scholar (P1960)
and GitHub (P2037) — no item claims any of them. Name search is not used
here on purpose: it returns *paper* items that merely mention you.

Walkthrough: [wikidata_manual.md](wikidata_manual.md).

