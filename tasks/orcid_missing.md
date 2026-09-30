# ORCID is missing 4 of your papers

Regenerated live by `python scripts/audit_identity.py`. Matched by DOI and
arXiv id against the work groups on the record, so this is absence and not a
title-matching guess.

**Fix it with the narrowed BibTeX, not the full import.** `tasks/orcid_missing.bib`
holds exactly these entries. Uploading `orcid_import.bib` again would re-add
the works already there under arXiv DOIs, and ORCID cannot group a work
carrying only the arXiv DOI with the same work carrying only the publisher
DOI — that is where the *listed twice* entries in `orcid_remove.md` came from.

On <https://orcid.org/my-orcid#works>: *Works* → **+ Add** → *Add BibTeX* →
choose `tasks/orcid_missing.bib` → review the list → *Add all*.

| # | cites | title | identifier |
|---|---|---|---|
| 1 | 1 | Skill Issue: Are Skills Language-Invariant in LLMs? | `10.48550/arXiv.2608.25832` |
| 2 | 0 | Last Translation Benchmark | `10.48550/arxiv.2609.04173` |
| 3 | 0 | User Feedback Provides a Unique Signal that LLMs Can not Detect | `10.48550/arXiv.2609.02859` |
| 4 | 0 | Why Pretraining Fails to Share Cross-Lingual Knowledge | `10.48550/arXiv.2609.19291` |

Then re-run the audit: the *ORCID holds your papers* row is the check.

