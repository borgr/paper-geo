# Wikidata: create the author item by hand

**Do this instead of QuickStatements if your account is new.**
QuickStatements requires an *autoconfirmed* account — 4 days old and 50 edits
— and fails with an authorisation error rather than saying so. Creating an item
through the normal editor has no such requirement. `wikidata.qs` stays in this
directory for when the account qualifies, or for a second person's item.

Fifteen minutes, once.

## 1. Check it does not already exist

<https://www.wikidata.org/wiki/Special:Search?search=haswbstatement%3AP496%3D0000-0002-0085-6496>

Empty result means no item claims your ORCID. Searching your *name* instead is
misleading — it returns paper items that merely list you as an author string,
which looks like a hit and is not one.

## 2. Create the item

<https://www.wikidata.org/wiki/Special:NewItem>

- **Label:** `Leshem Choshen`
- **Description:** `researcher in natural language processing`
  (a description is what separates you from a namesake; it must not repeat the
  label, and Wikidata rejects an item whose label+description pair already
  exists)
- **Aliases** — add each as its own entry, not one comma-joined string:
    - Choshen, Leshem
    - L. Choshen

## 3. Add these statements

In the editor, click *+ Add statement*, type the **property name** — it
autocompletes — then the value. The P/Q numbers are only to confirm the
autocomplete resolved to the right thing.

| property | | value | |
|---|---|---|---|
| instance of | `P31` | human | `Q5` |
| occupation | `P106` | researcher | `Q1650915` |
| occupation | `P106` | computer scientist | `Q82594` |
| field of work | `P101` | natural language processing | `Q30642` |
| field of work | `P101` | machine learning | `Q2539` |
| ORCID iD | `P496` | 0000-0002-0085-6496 |  |
| official website | `P856` | https://borgr.github.io |  |
| employer | `P108` | Weizmann Institute of Science | `Q4182` |
| employer | `P108` | MIT-IBM Watson AI Lab | `Q117720866` |
| employer | `P108` | IBM Research | `Q3146518` |
| educated at | `P69` | Hebrew University of Jerusalem | `Q174158` |
|   ↳ qualifier: academic degree | `P512` | PhD | `Q752297` |
| Google Scholar author ID | `P1960` | 8b8IhUYAAAAJ |  |
| Semantic Scholar author ID | `P4012` | 41019330 |  |
| OpenAlex ID | `P10283` | A5040286212 |  |
| DBLP author ID | `P2456` | 218/5237 |  |
| GitHub username | `P2037` | borgr |  |
| Hugging Face user ID | `P12201` | borgr |  |
| LinkedIn personal profile ID | `P6634` | leshemchoshen |  |
| OpenReview.net profile ID | `P8964` | ~Leshem_Choshen1 |  |
| Mastodon address | `P4033` | LChoshen@sigmoid.social |  |
| X username | `P2002` | LChoshen |  |

Identifier values (ORCID, the author IDs) are plain strings — Wikidata
validates the format and **warns** on a malformed one rather than refusing it,
so the statement saves and then sits there with a yellow triangle. Two that
catch people, because the wrong value looks entirely reasonable:

- **DBLP author ID** is the numeric pid (`218/5237`), *not* your name. The
  property's formatter URL is `dblp.org/pid/$1`, so a name-shaped value builds
  a link that 404s — which is what the constraint warning is telling you. Read
  the number off your own dblp page's URL.
- **Mastodon address** is `user@server`, with **no** leading `@`, even though
  that is the form your own profile shows you.

### Rows marked *qualifier*

A qualifier is a statement *on* a statement, not a new one: add the parent row
first, then click *+ add qualifier* underneath it. The academic-degree row
belongs inside the `educated at` statement, so the item says "PhD, from there"
rather than two disconnected facts.

### educated at vs employer — the one people get wrong

**A postdoc is employment, not education.** You were not enrolled, no degree
was awarded, and the institution was paying you. It goes in `employer` (P108),
optionally qualified with `position held` (P39) = *postdoctoral researcher*
(`Q1125292`); putting it in `educated at` asserts a degree you do not hold. The
test is just: was a degree awarded? PhD, MSc, BSc → P69. Postdoc, visiting
researcher, internship, fellowship → P108.

Both are worth having, for different reasons. P108 is what institutional
disambiguation matches on, so it should agree with ORCID's *Employment* exactly.
P69 is what connects you to older papers carrying a student affiliation, which
is the period where a namesake is hardest to tell apart from you.

## 4. Record the result

Copy the new Q-number from the URL into `config.yaml` → `ids.wikidata`, then
`python scripts/build_site.py --deploy`. It lands in the site's `sameAs` array,
which is what lets an engine fuse the Wikidata item with your pages.

## 5. Your paper items: measure first, because the standard advice may not apply

The advice you will find everywhere is: your papers already exist as items
auto-imported from Crossref, carrying your name as *author name string*
(`P2093`) rather than a link, and <https://author-disambiguator.toolforge.org>
reassigns them to *author* (`P50`) → your item in bulk. Where that holds it is
the best ten minutes on this page — it turns an isolated item into a hub, and
the edits carry you to autoconfirmed as a by-product.

**Check whether it holds before planning around it.** `audit_identity.py` looks
up every paper's DOI and reports how many are in Wikidata; the search below is
the by-hand version of the other half — items with your name as a *string*.

<https://www.wikidata.org/wiki/Special:Search?search=haswbstatement%3AP2093%3DLeshem%20Choshen>

Wikidata's coverage of CS literature is **sporadic rather than a pipeline**: the
systematic Crossref imports ran years ago, publisher DOIs fare far better than
arXiv DataCite ones, and a recent item is as likely to be one interested human's
work as a bot's. A corpus that is mostly preprints and ACL Anthology papers can
sit in the single digits — and then there is nothing for Author Disambiguator to
reassign, no `P2093` strings to upgrade, and no free route to 50 edits.

**If the count is low, that is a decision point, not a failure.** Creating items
for your own papers is ~2 minutes each and it is the only remaining path to
autoconfirmed. Worth it if you want a queryable graph of the corpus; not worth it
merely to unlock QuickStatements, since everything on *this* page is 15 minutes
by hand and that is where the identity gain is. Either way, link the items that
*do* exist: open each, and on its `author name string` statement for you, replace
it with `author` → your Q-number.

## Is this legitimate?

Yes, and it is worth knowing why so you are not uneasy about it. Wikidata's
notability policy is not Wikipedia's: criterion 2 admits any *clearly
identifiable entity that can be described using serious and publicly available
references*, and criterion 3 admits items that *fulfil a structural need*. An
author item with an ORCID and published papers is squarely both — and hundreds
of thousands exist already, mostly auto-created from ORCID and Crossref.
Unlike Wikipedia there is no prohibition on creating an item about yourself.
The requirement is accuracy, not distance, which is why the statements above
are identifiers and affiliations only: nothing about importance, nothing
unsourced, nothing a reader could not verify.
