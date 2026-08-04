# Wikidata follow-up — [Q140867203](https://www.wikidata.org/wiki/Q140867203)

Label **Leshem Choshen** · description *AI for humanity researcher*

Live diff against `config.yaml`. Re-run `python scripts/audit_identity.py`
after editing to confirm each line cleared.

## Fix first: an alias was stored as one string

Wikidata holds this as a single *also known as* value:

```
`Choshen, Leshem`, `L. Choshen`
```

That is one alias whose text happens to contain backticks and a comma,
not two aliases — so a citation reading *Choshen, Leshem* matches nothing.
The aliases box takes one name per entry.

On <https://www.wikidata.org/wiki/Q140867203>: click the *also known as* area,
delete that entry, then add each of these as its own alias:

- [ ] `Choshen, Leshem`
- [ ] `L. Choshen`

## Duplicate statements to remove

The editor does not warn when the same value is added twice, and the item
page renders the two identically, so this is only visible from the API.

- [ ] `P108` = `Q117720866` appears 2× — delete all but one (<https://www.wikidata.org/wiki/Q140867203#P108>)

## Identifiers to add

Each of these has a *typed* property, which is why none of them belong in
`official website`. A typed identifier is format-validated, renders as a
link anyway, and is traversable: Scholia, Author Disambiguator and any
SPARQL query can hop from it to the record. A bare URL is none of those.

Add with *+ Add statement* → type the property name → paste the value.

- [ ] **Hugging Face user ID** (`P12201`) = `borgr`
- [ ] **LinkedIn personal profile ID** (`P6634`) = `leshemchoshen`

- [ ] **OpenReview.net profile ID** (`P8964`) — fill `ids.openreview` in `config.yaml` first. Open your OpenReview profile and copy the `~Name1` from the URL; it is left blank rather than guessed because a duplicate profile would make the guess wrong, and a wrong identifier is worse than a missing one.

## Worth adding while you are in the editor

Not identifiers — statements that help a disambiguator separate you from a
namesake, which is the whole job of this item.

| property | | value | why |
|---|---|---|---|
| given name | `P735` | Leshem | lets a query match the name parts separately from the label string |
| family name | `P734` | Choshen | same |
| educated at | `P69` | your PhD institution | the single strongest disambiguating fact about a researcher |
| employer | `P108` | with *start time* qualifiers | turns three flat affiliations into a career an engine can order |

Skip date of birth, sex or gender, and image. None of them help retrieval
and all of them are personal data you would then be maintaining.

## Then: link your papers to the item

This is the step that turns the item from an isolated record into something
that resolves — and it is also how the account reaches the 50 edits that
unlock QuickStatements, so it is not a separate chore.

**Why it matters.** Dozens of your papers already exist as Wikidata items,
imported from Crossref. They carry your name as `author name string` (P2093)
— a bare text field. Nothing connects those items to you. Replacing the
string with `author` (P50) pointing at Q140867203 is what makes the item a hub:
afterwards a single query returns your corpus, Scholia renders a profile page
from it, and the papers inherit your identifiers.

**The tool.** <https://author-disambiguator.toolforge.org>

1. *Log in* (top right) — it edits on your behalf, so this is required, and
   it is why the edits count toward your 50.
2. Paste `Q140867203` into **Author details / Q-number** and submit. You land on a
   page listing every paper item whose `P2093` string matches your name.
3. Each row has a checkbox and shows the paper title plus its other authors.
   Tick the ones that are yours. **Read the co-author list rather than the
   title** — a namesake shows up as a paper you do not recognise, and the
   co-authors are the fastest tell.
4. Press the button at the bottom to move the ticked ones from `P2093` to
   `P50`. One edit per paper.
5. Repeat for each name variant — the tool searches one string at a time, so
   `Leshem Choshen` and `L. Choshen` are two separate passes.

Twenty minutes gets you past 50 edits with real work rather than filler.
After four days the account is autoconfirmed and `wikidata.qs` will run.

**One caution.** Do not use the tool's *create missing author item* button
while your own item exists — that is how duplicate author items appear.
Always point rows at Q140867203.

