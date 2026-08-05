# ORCID: works to remove

Works on the record that are not in `data/papers.yaml`. Regenerated live by
`python scripts/audit_identity.py`; the file is empty when the record is clean.

**How this happens.** The bibliography this tool reads is a CV bibliography, so
it contains the works the CV *cites* as well as the works it lists. Those were
included in the bulk import before the collector learned to check author names.
The import is one click and the removal is one click *per work*, which is the
whole reason this page exists rather than the check being left to import time.

**Why it matters more than it looks.** ORCID is not a private list. Semantic
Scholar, OpenAlex, Crossref and publisher submission systems read it as your
assertion of authorship, and a claim on a famous paper is the kind of error
someone eventually notices and reads uncharitably.

## Confirmed not yours (13)

The collector rejected each of these because no form of your name appears
in the author list from any source. Delete them.

On <https://orcid.org/my-orcid#works>: *Works* → find the title → the
**⋮ / Actions** menu on that entry → *Delete*. There is no multi-select, so
it is one at a time. Sorting by *Date added* groups the whole import
together, which makes them faster to find than searching by title.

| # | title | ORCID put-code |
|---|---|---|
| 1 | The Heuristic Core: Understanding Subnetwork Generalization in Pretrained Lang | `222732429` |
| 2 | A framework for few-shot language model evaluation | `222732431` |
| 3 | DenseFormer: Enhancing Information Flow in Transformers via Depth Weighted Ave | `222732440` |
| 4 | Super Tiny Language Models | `222732415` |
| 5 | The llama 3 herd of models | `222732462` |
| 6 | Not all layers are equally as important: Every Layer Counts BERT | `222732473` |
| 7 | Holistic evaluation of language models | `222732409` |
| 8 | Model soups: averaging weights of multiple fine-tuned models improves accuracy | `222732433` |
| 9 | Merging models with fisher-weighted averaging | `222732410` |
| 10 | Attention is all you need | `222732451` |
| 11 | Mapping the early language environment using all-day recordings and automated  | `222732425` |
| 12 | Sapiens: A brief history of humankind | `222732453` |
| 13 | European public acceptance of euthanasia: socio-demographic and cultural facto | `222732414` |

The put-code is the record's internal id, shown in the URL when you open a
work. It is here so you can confirm you are deleting the right entry when two
titles are similar.

## On ORCID, unknown to us (3)

Not necessarily wrong — a paper missing from the bibliography looks exactly
like this. **Check before deleting.** If it is yours, the fix is upstream in
the bibliography, not here.

- Resolving Interference When Merging Models  (`222732441`)
- Transition based Graph Decoder for Neural Machine Translation  (`222732428`)
- Inherent Biases in Reference-based Evaluation for Grammatical Error
                  Correction and Text Simplification  (`222732469`)
