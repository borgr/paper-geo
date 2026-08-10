# Wikidata follow-up — [Q140867203](https://www.wikidata.org/wiki/Q140867203)

Label **Leshem Choshen** · description *Israeli computer scientists and researcher*

Live diff against `config.yaml`. Re-run `python scripts/audit_identity.py`
after editing to confirm each line cleared.

## Worth adding while you are in the editor

Not identifiers — statements that help a disambiguator separate you from a
namesake, which is the whole job of this item.

| property | | value | why |
|---|---|---|---|
| given name | `P735` | Leshem | lets a query match the name parts separately from the label string |
| family name | `P734` | Choshen | same |
| educated at | `P69` | Hebrew University of Jerusalem (PhD) | the single strongest disambiguating fact about a researcher |
| employer | `P108` | with *start time* qualifiers | turns flat affiliations into a career an engine can order |

`educated at` is for degree-granting study only. A postdoc goes in `employer`
(`P108`), optionally qualified with *position held* (`P39`) = `Q1125292`
(postdoctoral researcher) — no degree was awarded, and the institution was
paying you. The test is just: was a degree awarded?

Skip date of birth, sex or gender, and image. None of them help retrieval
and all of them are personal data you would then be maintaining.

## Then: your papers

**Measured this run: 3 of 112 have a Wikidata item.**
(Matched on DOI and arXiv id across 111 papers that carry one
— exact keys, so this is coverage and not a name-search guess.)

- [Q106097217](https://www.wikidata.org/wiki/Q106097217) — An autonomous debating system
- [Q131458005](https://www.wikidata.org/wiki/Q131458005) — ColD Fusion: Collaborative Descent for Distributed Multitask Finetunin
- [Q131458863](https://www.wikidata.org/wiki/Q131458863) — Cluster & Tune: Boost Cold Start Performance in Text Classification

Two facts follow from that number, and both cut against the usual advice.

**Author Disambiguator is nearly empty for you.** Its job is to convert an
`author name string` (P2093) into `author` (P50) pointing at Q140867203. That only
works on items that already exist, so it can reach at most those listed
above. It is worth one pass — <https://author-disambiguator.toolforge.org>,
log in, paste `Q140867203` into *Author details*, tick rows whose **co-author list**
matches (the title is the weaker tell against a namesake), submit. Repeat per
name variant; it searches one string at a time. Do not press *create missing
author item* while your item exists — that is how duplicate author items
appear.

**It will not get you to 50 edits.** Worth saying because the autoconfirmed
threshold QuickStatements needs — 4 days old and 50 edits — looks like
something this step would pay for, and with a handful of linkable items it
cannot. Whether you still owe them is one command rather than an assumption:
`python scripts/wikidata_apply.py --check-account`. If you do, either make the
50 elsewhere or skip QuickStatements and edit by hand — the item's own
statements are a 15-minute job either way.

**Creating the missing items — optional, and read this first.**

`tasks/wikidata_papers.qs` holds a QuickStatements batch for
108 papers: title, publication date, DOI or arXiv id, and the author
list with you as `author` → Q140867203 and co-authors as `author name string`
with position qualifiers. Only papers carrying a DOI or arXiv id are
included — a resolvable identifier is what puts a publication item
clearly in scope, and it is the key the batch was deduplicated on.

Honest accounting before you run it: this buys a Scholia profile, a
SPARQL-answerable corpus, and an authorship graph — real, but a weaker
surface than arXiv, ORCID or your own pages. It costs an autoconfirmed
account, a batch review, and permanent public items. Items created here
are much harder to clean up than a page in this repo. Run it in
QuickStatements with the batch preview open, on the first ten rows,
before releasing the rest.

One gap the dedup cannot cover: a paper item that exists with neither a
DOI nor an arXiv id would not have matched, so it could be recreated.
Searching the exact title in Wikidata's own search box is the check.

