# Wikidata follow-up — [Q140867203](https://www.wikidata.org/wiki/Q140867203)

Label **Leshem Choshen** · description *AI Technologies for Humanity researcher*

Live diff against `config.yaml`. Re-run `python scripts/audit_identity.py`
after editing to confirm each line cleared.

## Fix first: an alias was stored as one string

Wikidata holds this as a single *also known as* value:

```
`L. Choshen`
`Choshen, Leshem`
```

That is one alias whose text happens to contain backticks and a comma,
not two aliases — so a citation reading *Choshen, Leshem* matches nothing.
The aliases box takes one name per entry.

On <https://www.wikidata.org/wiki/Q140867203>: click the *also known as* area,
delete that entry, then add each of these as its own alias:

- [ ] `Choshen, Leshem`
- [ ] `L. Choshen`
- [ ] `Leshem Chosen`
- [ ] `Lesham Choshen`

## Identifiers to add

Each of these has a *typed* property, which is why none of them belong in
`official website`. A typed identifier is format-validated, renders as a
link anyway, and is traversable: Scholia, Author Disambiguator and any
SPARQL query can hop from it to the record. A bare URL is none of those.

Add with *+ Add statement* → type the property name → paste the value.

- [ ] **Mastodon address** (`P4033`) = `LChoshen@sigmoid.social`
- [ ] **X username** (`P2002`) = `LChoshen`
- [ ] **DBLP author ID** (`P2456`) reads `Leshem_Choshen` — expected `218/5237`

`P2456` is the reason for the warning triangle on the item. It takes
DBLP's *pid* — the numeric path in `dblp.org/pid/218/5237` — not the
name-shaped URL DBLP also answers on. Wikidata builds the link by
substituting the value into `dblp.org/pid/$1`, so a name value both
trips the format constraint and produces a 404. Constraint violations
do not block saving, which is why it saved and then complained.

*0 references* on that statement is not the warning and is not a
problem: external identifiers are normally unsourced, since the
identifier resolving is the source. Ignore it.

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

**Measured this run: 3 of 111 have a Wikidata item.**
(Matched on DOI and arXiv id across 110 papers that carry one
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

**It will not get you to 50 edits.** The autoconfirmed threshold was going to
be paid for by this step. With a handful of linkable items it cannot be, so
either make the 50 elsewhere or skip QuickStatements and edit by hand —
the item's own statements are a 15-minute job either way.

**Creating the missing items — optional, and read this first.**

`tasks/wikidata_papers.qs` holds a QuickStatements batch for
107 papers: title, publication date, DOI or arXiv id, and the author
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

