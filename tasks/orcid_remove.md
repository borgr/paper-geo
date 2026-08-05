# ORCID: works to remove

Works on the record that are not in `data/papers.yaml`. Regenerated live by
`python scripts/audit_identity.py`; the file is empty when the record is clean.

**How this happens.** The bibliography this tool reads is a CV bibliography, so
it contains the works the CV *cites* as well as the works it lists. Those were
included in the bulk import before the collector learned to check author names.
The import is one click and the removal is one click *per work*, which is the
whole reason this page exists rather than the check being left to import time.

**Why it matters more than it looks.** ORCID is not a private list. Semantic
Scholar, OpenAlex, Crossref and publisher submission systems read it as your
assertion of authorship, and a claim on a famous paper is the kind of error
someone eventually notices and reads uncharitably.

## Confirmed not yours (1)

The collector rejected each of these because no form of your name appears
in the author list from any source. Delete them.

On <https://orcid.org/my-orcid#works>: *Works* → find the title → the
**⋮ / Actions** menu on that entry → *Delete*. There is no multi-select, so
it is one at a time. Sorting by *Date added* groups the whole import
together, which makes them faster to find than searching by title.

| # | title | ORCID put-code |
|---|---|---|
| 1 | DenseFormer: Enhancing Information Flow in Transformers via Depth Weighted Ave | `222732440` |

The put-code is the record's internal id, shown in the URL when you open a
work. It is here so you can confirm you are deleting the right entry when two
titles are similar.

## Listed twice (3 papers, 6 entries)

One paper, two ORCID works. ORCID groups works that share an external
identifier; these pairs share none, because one entry carries the publisher
DOI and the other carries arXiv's `10.48550/arXiv.<id>` DOI. The titles
differ too — usually a preprint title that changed on acceptance, or a
subtitle typed into one entry and not the other — so they do not even look
like the same paper on the page.

**Delete the preprint entry, keep the published one.** The published entry
carries the venue, and the venue is what a disambiguator matches on. Nothing
is lost: the arXiv version stays reachable from the paper page, and if
DataCite auto-update later re-adds it, it will arrive with your iD attached
and can be left alone.

**Or, if you would rather keep both visible:** open the published entry,
*Add identifier* → type `doi`, value = the arXiv DOI below. Two identifiers
on one work is what makes ORCID fold the group. More clicks, same result.

| paper | keep | delete |
|---|---|---|
| TIES-Merging: Resolving Interference When Me | `222732441` — Resolving Interference When Mergin | `222732361` — TIES-Merging: Resolving Interferen |
| Enhancing the Transformer Decoder with Trans | `222732435` — Enhancing the Transformer Decoder  | `222732428` — Transition based Graph Decoder for |
| Inherent Biases in Reference-based Evaluatio | `222732470` — Inherent Biases in Reference-based | `222732469` — Inherent Biases in Reference-based |

The order in the table is the order the record returns them, *not* which to
delete — open both put-codes and delete the one whose *Source* line shows no
venue. Deleting is *Works* → the entry → **⋮ / Actions** → *Delete*.
