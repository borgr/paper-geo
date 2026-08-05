# Identity audit

Live read of the surfaces you do not control. Regenerate with
`python scripts/audit_identity.py`. Every row is checkable without a login,
which is why it can be re-run — the fixes all need one.

| surface | state | |
|---|---|---|
| ORCID works (public) | 117 of 117 | ok |
| ORCID canonical URL | present | ok |
| ORCID name variants | 2 listed | ok |
| ORCID keywords | 13 of 13 | ok |
| ORCID lists other personal pages | 1 of 1 | ok |
| ORCID employment | 1 listed, 3 missing | **fix** |
| ORCID education | 1 listed, 0 missing, 1 incomplete | **fix** |
| ORCID works added by Crossref/DataCite | 0 | nothing yet |
| arXiv registered author | 105 of 105 | ok |
| Wikidata author item | Q140867203 | ok |
| Wikidata item complete | 4 gaps | **fix** |
| Wikidata paper items | 3 of 117 | optional |
| HF pages indexed | 105 of 105 | ok |
| HF pages claimed | 103 of 105 claimable | **fix** |
| arXiv records misspelling your name | 2 | **fix** |
| arXiv records omitting you | 0 | ok |
| ORCID works that are not yours | 13 | **fix** |
| ORCID works we cannot place | 3 | **check** |
| Semantic Scholar records | 2 | **fix** |

## Crossref / DataCite auto-update: no evidence it is live

All 117 public works are **self-asserted** — the `source` on every
one of them is your own name. A work that Crossref or DataCite adds carries
*their* name instead, so this row is the only public read on whether those
connections exist. It is currently reading zero.

**Zero is the expected reading today, and that is the trap.** Auto-update is
not a sync and it does not backfill: it fires only when a *newly deposited*
record already contains your iD. So a granted permission and a permission
that never completed look identical until your next paper is published —
months from now, with nothing to connect the silence to the click.

Two checks separate them, both two minutes:

1. **Was the permission actually granted?** *ORCID → Account settings →
   Trusted parties*. `Crossref Metadata Search` and `DataCite` should each
   be listed there with permission to add and update your works. The wizards
   send you off to `search.crossref.org` / DataCite's own site, which is what
   makes this ambiguous: landing there proves the redirect worked, not that
   you came back and completed the OAuth grant. If they are absent from
   Trusted parties, nothing was granted — redo *Works → Search & link*.
2. **Is your iD in the deposits at all?** Permissions cannot help if
   publishers never put your iD in the metadata they deposit. Search a recent
   published DOI at <https://search.crossref.org> and look for your ORCID in
   the author list. Absent means the fix is upstream: supply your iD in the
   submission system for every future paper. That single habit is what makes
   auto-update work without you.

Re-run this audit after the next publication lands. A non-zero count here is
the proof; until then, Trusted parties is the evidence.

## ORCID employment and education are thinner than your record

These two sections are what institutional disambiguation matches on — the
signal that separates you from a namesake when the name alone cannot. They
are also the sections nothing ever fills for you.

Currently on the record:

- *employment* — Massachusetts Institute of Technology · Postdoctoral Researcher · 2023–present
- *education* — The Hebrew University of Jerusalem · no degree stated · 2016–present

**Affiliations in `config.yaml` with no employment entry.** Each is one
form under *Employment → + Add*. Worth the two minutes each: a paper
carrying an affiliation your ORCID never mentions is a paper a
disambiguator has one less reason to attach to you.

- [ ] MIT-IBM Watson AI Lab
- [ ] IBM Research
- [ ] Weizmann Institute of Science

**Education entries that state less than they should.** ORCID's education
*Role* field is where the degree goes (`PhD`), and an entry with no end
year reads as *still enrolled*. Left as-is next to a postdoc employment,
the record contradicts itself about what you currently are — and it is a
human-obvious inconsistency that a machine reads literally.

- [ ] The Hebrew University of Jerusalem — no degree in the Role field, no end year

## Wikidata item Q140867203 exists — a correction and 1 identifier to add

An alias was stored as one string with its markdown intact (``L. Choshen``), so it matches nothing. Fix that first.

Full diff, plus what the measured paper coverage means for the Author Disambiguator pass: [wikidata_followup.md](wikidata_followup.md).

## Wikidata paper coverage: 3 of 117

Matched on DOI and arXiv id, not on name. This number matters because it
decides which Wikidata job is worth doing: relinking author strings on
items that already exist, or creating the items. At this coverage it is
the second, and the first cannot pay for the 50 edits QuickStatements
needs. One trap worth writing down — scholarly articles were moved out of
Wikidata's main query graph, so a publication query against
`query.wikidata.org` returns zero rows with a 200, and looks like an
answer. This uses `query-scholarly.wikidata.org`.

An opt-in batch for the 114 missing items is in `tasks/wikidata_papers.qs`; read the cautions in [wikidata_followup.md](wikidata_followup.md) before running it.

## Hugging Face: 0 to index, 2 to claim, 0 blocked

Live counts, not the ones cached in `papers.yaml`. Lists:
[hf_worklist.md](hf_worklist.md).

## 13 works on your ORCID are not yours

Imported from the bibliography before the collector checked author names —
a CV bibliography holds the works it *cites* as well as the works it lists.
ORCID is read as your authorship claim by Semantic Scholar, OpenAlex and
publisher systems, so this is worth clearing before anything else on this
page. One deletion each, put-codes included:
[orcid_remove.md](orcid_remove.md).

## arXiv metadata misspells your name on 2 papers

Upstream of every other surface here — Hugging Face, Semantic Scholar,
OpenAlex and Scholar all read arXiv's author list, so one wrong character
creates one wrong author in all of them, holding citations that cannot be
merged back. Details and the fix order:
[arxiv_name_fixes.md](arxiv_name_fixes.md).

