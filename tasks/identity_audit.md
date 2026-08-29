# Identity audit

Live read of the surfaces you do not control. Regenerate with
`python scripts/audit_identity.py`. Every row is checkable without a login,
which is why it can be re-run — the fixes all need one.

| surface | state | |
|---|---|---|
| ORCID works (public) | 116 | ok |
| ORCID holds your papers | 113 of 114 | **fix** |
| ORCID identifiers point at the right paper | 116 of 116 works | ok |
| ORCID canonical URL | present | ok |
| ORCID name variants | 2 listed | ok |
| ORCID keywords | 13 of 13 | ok |
| ORCID lists other personal pages | 1 of 1 | ok |
| ORCID employment | 3 listed, 0 missing | ok |
| ORCID education | 2 listed, 0 missing, 0 incomplete, 1 institution-asserted | ok |
| ORCID works added by Crossref/DataCite | 0 | nothing yet |
| arXiv registered author | 105 of 106 | **fix** |
| Wikidata author item | Q140867203 | ok |
| Wikidata item complete | 0 gaps | ok |
| Wikidata paper items | 113 of 114 | optional |
| HF pages indexed | 106 of 106 | ok |
| HF pages claimed | 105 of 106 claimable | **fix** |
| arXiv records misspelling your name | 0 of 106 read | ok |
| arXiv records omitting you | 0 of 106 read | ok |
| ORCID works we cannot place | 2 | **check** |
| ORCID works ORCID already merged | 6 | optional |
| Semantic Scholar records | 2 | **fix** |

## Crossref / DataCite auto-update: no evidence it is live

All 116 public works are **self-asserted** — the `source` on every
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

- *employment* — Weizmann Institute of Science · no role title · 2026–present
- *employment* — Massachusetts Institute of Technology · Postdoctoral Researcher · 2023–present
- *employment* — IBM Research · no role title · 2016–present
- *education* — The Hebrew University of Jerusalem · no degree stated · 2016–present · asserted by The Hebrew University of Jerusalem
- *education* — Hebrew University of Jerusalem · PhD · ?–2023

**One education entry your institution asserted, not you.** This one is
not a task, it is a decision — and the default is to leave it.

- The Hebrew University of Jerusalem — no degree in the Role field, no end year — asserted by **The Hebrew University of Jerusalem** (put-code `16591121`)

ORCID shows no *Edit* control on an entry someone else asserted, only
*Delete*, so it cannot be corrected in place. The three routes, in the
order worth trying them:

1. **Leave it.** An institution-asserted affiliation is the strongest form
   this section takes: the university's own ORCID integration vouched for
   it, and consumers can see that in the source line. A thinner entry from
   a better source beats a complete one you typed yourself.
2. **Add your own alongside it.** *Education → + Add* with the degree in
   *Role* and the real end year. ORCID groups affiliations by organization,
   so yours joins theirs as a second source on the same block rather than
   displacing it. This is the fix that costs nothing and loses nothing.
3. **Ask them to correct it** — whoever runs the ORCID integration, usually
   the library or the research office. Slow, and the only route that
   changes what the institution asserts.

Do not delete it and re-add your own: that trades a vouched-for entry for a
self-asserted one, which is a downgrade in exactly the signal this section
exists to provide.

## arXiv: 1 papers you are not registered as author on

The biggest finding here, and a prerequisite rather than a task: you cannot
add a journal-ref to a paper you do not own. Full list and both claim
routes: [arxiv_ownership.md](arxiv_ownership.md).

## Wikidata paper coverage: 113 of 114

Matched on DOI and arXiv id, not on name. This number matters because it
decides which Wikidata job is worth doing: relinking author strings on
items that already exist, or creating the items. At this coverage it is
the second, and there is nothing to relink until they exist.
One trap worth writing down — scholarly articles were moved out of
Wikidata's main query graph, so a publication query against
`query.wikidata.org` returns zero rows with a 200, and looks like an
answer. This uses `query-scholarly.wikidata.org`.

## Hugging Face: 0 to index, 1 to claim, 0 blocked

Live counts, not the ones cached in `papers.yaml`. Lists:
[hf_worklist.md](hf_worklist.md).

## 2 works on your ORCID we cannot place

Not necessarily wrong, which is why this is *check* and not *fix*: a paper
missing from your bibliography looks exactly like a work that is not yours.

Matched against the corpus by identifier, then by title, then by the title's
content words with the order discarded — so a paper retitled between preprint
and proceedings, or rearranged around its colon, no longer lands here. What
reaches this list carries no identifier ORCID could group on, which is also
why nothing else can place it.

Two things end up here and they have opposite fixes. A paper of yours the
bibliography never held is fixed **upstream, in the bibliography** — deleting
it from ORCID loses a real work. Anything that is not a paper (a workshop
listing, a proceedings volume) is a deletion. Titles and put-codes:
[orcid_remove.md](orcid_remove.md).

## 1 of your papers is missing from ORCID

Measured by identifier, not by counting: each of these has no work group on
the record carrying its DOI or arXiv id.

This is the row that matters most on the page and the one a works *count*
hides. ORCID is the key Semantic Scholar disambiguates on and the key OpenAlex
is running profile merges from, so a paper absent here is a paper those two
have no authoritative reason to attach to you — which is the same failure the
split S2 record is made of.

Highest citations first; the full list with DOIs is
[orcid_missing.md](orcid_missing.md).

- [ ]    0 cites — Skill Issue: Are Skills Language-Invariant in LLMs?

