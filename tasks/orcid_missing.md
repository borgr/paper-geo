# ORCID is missing 1 of your papers

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
| 1 | 0 | Resolving Interference (RI): Disentangling Models for Improved M | `10.48550/ARXIV.2603.13467` |

Then re-run the audit: the *ORCID holds your papers* row is the check.

