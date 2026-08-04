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
| employer | `P108` | MIT-IBM Watson AI Lab | `Q49108` |
| employer | `P108` | IBM Research | `Q3146518` |
| employer | `P108` | Weizmann Institute of Science | `Q4182` |
| Google Scholar author ID | `P1960` | 8b8IhUYAAAAJ |  |
| Semantic Scholar author ID | `P4012` | 41019330 |  |
| OpenAlex ID | `P10283` | A5040286212 |  |
| DBLP author ID | `P2456` | Leshem_Choshen |  |
| GitHub username | `P2037` | borgr |  |
| Hugging Face user ID | `P12201` | borgr |  |
| LinkedIn personal profile ID | `P6634` | leshemchoshen |  |

Identifier values (ORCID, the author IDs) are plain strings — Wikidata
validates the format and will refuse a malformed one, which is a useful check
that the id in `config.yaml` is right.

## 4. Record the result

Copy the new Q-number from the URL into `config.yaml` → `ids.wikidata`, then
`python scripts/build_site.py --deploy`. It lands in the site's `sameAs` array,
which is what lets an engine fuse the Wikidata item with your pages.

## 5. Worth ten more minutes: link your existing paper items

Some of your papers already exist as Wikidata items, imported from Crossref,
carrying your name as *author name string* (`P2093`) — a bare string, not a
link. Replacing those with *author* (`P50`) pointing at your new item is what
turns the item from an isolated record into a hub that resolves.

The tool for this is Author Disambiguator:
<https://author-disambiguator.toolforge.org> — search your name, it lists every
paper item with a matching name string and reassigns them in bulk.

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
