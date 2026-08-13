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

## On ORCID, unknown to us (2)

Not necessarily wrong — a paper missing from the bibliography looks exactly
like this. **Check before deleting.** If it is yours, the fix is upstream in
the bibliography, not here.

These are matched by identifier first (the group's DOI or arXiv id), then by
title, then by the title's content words with the order discarded — so a paper
retitled between preprint and proceedings, or rearranged around its colon, no
longer lands here. A work reaching this section carries *no* identifier ORCID
could group on — which is also why nothing else can place it.

- High-dimensional Learning Dynamics 2024: The Emergence of Structure and Reasoning Workshop at ICML24  (`222732427`)
- Insights from the first BabyLM Challenge: Training sample-efficient language models on a developmentally plausible corpus  (`222732476`)

## On ORCID, deliberately not in the bibliography (1)

**Nothing to do.** Each of these is a work you decided not to add to the
source bibliography, so it can never match a corpus paper and would sit under
*check before deleting* forever -- asking you to redo the thinking that
produced the decision. The decision itself is the line quoted after each one,
in [`data/declines.yaml`](../data/declines.yaml); delete that line and the work
moves back up to the section above.

Leave them on ORCID. A work being outside a CV bibliography says nothing about
whether it is yours, and these are.

- LLM Merging: Building LLMs Efficiently through Merging  (`222732439`) — declined as `Llm merging`
