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

## Listed twice (4 papers, 8 entries)

One paper, two ORCID works. ORCID groups works that share an external
identifier; these pairs share none, because one entry carries the publisher
DOI and the other carries arXiv's `10.48550/arXiv.<id>` DOI. The titles
differ too — usually a preprint title that changed on acceptance, or a
subtitle typed into one entry and not the other — so they do not even look
like the same paper on the page.

**Merge them; do not delete either.** The two entries carry different
titles, and both titles are real: one is what the paper was called as a
preprint and the other is what it was called on acceptance. Deleting the
preprint entry throws away a title that is cited in the wild and an
identifier that resolves — so the merge keeps more than it costs, and the
extra work is one field.

ORCID has no merge button, and does not need one: it groups works that share
an external identifier. Put the *other* entry's DOI on the entry you keep
and the pair folds into a single work with a version selector, both titles
and both DOIs intact. Nothing is deleted, so nothing can be lost by getting
it wrong.

For each row: open the **keep** entry (its put-code is the last path segment
at <https://orcid.org/my-orcid#works>), then *Edit* → **+ Add identifier** →
type `doi` → paste the value in the last column → *Save*. The two entries
collapse on the next page load.

| paper | keep (published, has the venue) | folds in | DOI to add to the keep entry |
|---|---|---|---|
| Can You Trust Your Metric? Automatic Concate | `222732438` — Can You Trust Your Metric? Aut | `222732471` — How Safe is Your Safety Metric | `10.48550/arXiv.2408.12259` |
| TIES-Merging: Resolving Interference When Me | `222732361` — TIES-Merging: Resolving Interf | `222732441` — Resolving Interference When Me | `10.48550/ARXIV.2306.01708` |
| Enhancing the Transformer Decoder with Trans | `222732435` — Enhancing the Transformer Deco | `222732428` — Transition based Graph Decoder | `10.48550/arXiv.2101.12640` |
| Inherent Biases in Reference-based Evaluatio | `222732470` — Inherent Biases in Reference-b | `222732469` — Inherent Biases in Reference-b | `10.48550/arXiv.1804.11254` |

If you would rather have one entry than a grouped pair, delete the
**folds in** one instead — *Works* → the entry → **⋮ / Actions** →
*Delete*. Same number of clicks, and the preprint title stops being
findable on your record.
