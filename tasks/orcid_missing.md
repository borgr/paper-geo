# ORCID is missing 11 of your papers

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
| 1 | 26 | Proceedings of the 59th Annual Meeting of the Association for… | `10.18653/v1/2021.acl-tutorials` |
| 2 | 4 | Proceedings of the Second Workshop on Fact Extraction and… | `10.18653/v1/d19-66` |
| 3 | 3 | Proceedings of the 5th Workshop on Structured Prediction for… | `10.18653/v1/2021.spnlp-1` |
| 4 | 2 | TabAgent: Distilling LLM Agent Components into Cheap Classifiers | `10.48550/arXiv.2602.16429` |
| 5 | 2 | Proceedings of the 17th International Conference on Parsing… | `10.18653/v1/2021.iwpt-1` |
| 6 | 1 | Skill Issue: Are Skills Language-Invariant in LLMs? | `10.48550/arXiv.2608.25832` |
| 7 | 0 | Last Translation Benchmark | `10.48550/arxiv.2609.04173` |
| 8 | 0 | User Feedback Provides a Unique Signal that LLMs Can not Detect | `10.48550/arXiv.2609.02859` |
| 9 | 0 | Why Pretraining Fails to Share Cross-Lingual Knowledge | `10.48550/arXiv.2609.19291` |
| 10 | 0 | Asking for What Was Never Requested: Horizontal and Vertical… | `10.48550/arxiv.2609.37236` |
| 11 | 0 | Retrieval Augmented Generation Compositionality | `10.48550/arXiv.2610.29722` |

Then re-run the audit: the *ORCID holds your papers* row is the check.

