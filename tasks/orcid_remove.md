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
| 1 | MINDGAMES: A Live Arena for Evaluating Social and Strategic Reasoning in Multi | `222829710` |

The put-code is the record's internal id, shown in the URL when you open a
work. It is here so you can confirm you are deleting the right entry when two
titles are similar.

## On ORCID, unknown to us (4)

Not necessarily wrong — a paper missing from the bibliography looks exactly
like this. **Check before deleting.** If it is yours, the fix is upstream in
the bibliography, not here.

These are matched by identifier first (the group's DOI or arXiv id) and only
then by title, so a paper retitled between preprint and proceedings no longer
lands here. A work reaching this section carries *no* identifier ORCID could
group on — which is also why nothing else can place it.

- Tie the KnOTS: Model Merging with SVD  (`222732423`)
- High-dimensional Learning Dynamics 2024: The Emergence of Structure and Reasoning Workshop at ICML24  (`222732427`)
- Insights from the first BabyLM Challenge: Training sample-efficient language models on a developmentally plausible corpus  (`222732476`)
- LLM Merging: Building LLMs Efficiently through Merging  (`222732439`)
