# ORCID is missing 16 of your papers

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
| 1 | 112 | Model merging with SVD to tie the Knots | `10.48550/arXiv.2410.19735` |
| 2 | 33 | BabyLM Turns 3: Call for papers for the 2025 BabyLM workshop | `10.48550/arXiv.2502.10645` |
| 3 | 5 | Do LLMs Benefit From Their Own Words? | `10.48550/arXiv.2602.24287` |
| 4 | 3 | CUBE: A Standard for Unifying Agent Benchmarks | `10.48550/arXiv.2603.15798` |
| 5 | 3 | Mediocrity is the key for LLM as a Judge Anchor Selection | `10.18653/V1/2026.ACL-LONG.706` |
| 6 | 3 | MINDGAMES: A Live Arena for Evaluating Social and Strategic Reas | `10.48550/arXiv.2605.29512` |
| 7 | 2 | SemEval 2019 Shared Task: Cross-lingual Semantic Parsing with UC | `10.48550/arXiv.1805.12386` |
| 8 | 1 | BabyLM Turns 4 and Goes Multilingual: Call for Papers for the 20 | `10.48550/arXiv.2602.20092` |
| 9 | 1 | Every Eval Ever: A Unifying Schema and Community Repository for  | `10.48550/arXiv.2606.14516` |
| 10 | 1 | Automated Discovery Has No Universally Superior Harness | `10.48550/arXiv.2607.18235` |
| 11 | 0 | Resolving Interference (RI): Disentangling Models for Improved M | `10.48550/arXiv.2603.13467` |
| 12 | 0 | Instructions Shape Production of Language, not Processing | `10.48550/arXiv.2605.11206` |
| 13 | 0 | Growing Pains: Extensible and Efficient LLM Benchmarking Via Fix | `10.48550/arXiv.2604.12843` |
| 14 | 0 | Evaluation Cards: An Interpretive Layer for AI Evaluation Report | `10.48550/arXiv.2606.09809` |
| 15 | 0 | Cross-Lingual Exploration for Parametric Knowledge | `10.48550/arXiv.2606.24579` |
| 16 | 0 | Stop Guessing When to Stop Testing: Efficient Model Evaluation w | `10.18653/v1/2026.findings-acl.43` |

Then re-run the audit: the *ORCID holds your papers* row is the check.

