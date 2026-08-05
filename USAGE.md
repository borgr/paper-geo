# How to use this

Three things you'll actually do: the routine refresh, adding a new paper, and
verifying a drafted sidecar. Everything else is a variation.

Read-only by default. Nothing leaves your machine without `--apply`, `--deploy`,
or `--yes`.

---

## Once, at setup

The account-level checklist — ORCID, Semantic Scholar, Google Scholar, Wikidata,
Hugging Face, canonical URL — is [docs/SETUP.md](docs/SETUP.md). Do that first; it
is independent of this tool and pays for everything else. Below is just the tool.

```bash
pip install pyyaml jsonschema          # jsonschema is optional but catches more
gh auth login                          # the sweep and deploy use the gh CLI
```

Edit [`config.yaml`](config.yaml): your name and name variants, ORCID, email,
canonical URL, and the id for each index (Semantic Scholar, OpenAlex, Google
Scholar, DBLP, GitHub, Hugging Face, Wikidata). That file is the only place
anything about you appears.

---

## The routine refresh

```bash
python update.py
```

Eight steps, each safe to re-run, in order: rebuild `data/papers.yaml` from your
bibliography + Semantic Scholar + arXiv + Hugging Face → refresh repo state →
label anything unlabelled → draft the next batch of sidecars → reconcile paper
ownership with collaborators → live-read the identity surfaces → validate against
the schemas → regenerate `WORKLIST.md`.

Then look at two files and act:

```bash
cat WORKLIST.md                        # what only you can do, ranked by citations
python scripts/sweep_github.py diff    # exactly what would change on GitHub
python update.py --apply               # write the repo changes
python scripts/build_site.py --deploy  # rebuild and publish the site
```

Monthly is plenty. Run `--refresh-bib` first if your bibliography lives in a local
checkout of the `publications` repo and has new entries:

```bash
python update.py --refresh-bib         # needs sources.publications_path in config
```

### Two ways a refresh talks back

**It may refuse to write.** Every source can fail, and a failed fetch returns an
empty field rather than an error — one dead API costs you one field instead of the
whole run. The cost of that choice is that a bad afternoon at Semantic Scholar looks
exactly like a good one, and the next commit makes the loss permanent. So the
collector compares each run against **the last commit** and stops if coverage fell
sharply:

```
REFUSING TO WRITE -- this run has much less data than the last commit:
  abstract: 116 -> 61 (-55)
```

Look at the `!` lines above it for the source that failed and rerun. If the drop is
real — a big merge, papers dropped on purpose — say so:

```bash
python scripts/collect.py --allow-shrink
```

`--no-arxiv` and `--no-hf` imply it, since a skip you asked for is not news.

**It may report `title differs from arXiv`.** The details are in
`build/title_diffs.json`. This is a review item, not an error, and **either side can
be the stale one**: arXiv v2 sometimes retitles a paper your bibliography still has
under its v1 name, and your bibliography sometimes has the correct title while arXiv
never got updated. Read the pair and fix whichever is wrong — upstream in the `.bib`
if it is yours, or by posting a new arXiv version if it is theirs.

---

## A new paper just went up

```bash
python update.py --refresh-bib      # picks it up; tells you what it still needs
```

Then, in this order — highest value first:

1. **Claim it on arXiv**, unless you were the submitter. `tasks/arxiv_ownership.md`
   says whether you own it; if not, ask the submitting co-author for the paper
   password (<https://arxiv.org/auth/need-paper-password>, instant) or file
   <https://arxiv.org/auth/request-ownership>. Everything in step 3 is blocked
   until this lands.
2. **Index its Hugging Face paper page.** `python scripts/hf_papers.py --live`
   writes `tasks/hf_worklist.md` (and `build/hf_worklist.html` to click through);
   log in to HF first, then `python scripts/hf_papers.py --verify`. This can't be
   automated — an unauthenticated visit creates nothing.
3. **Once it has a venue, add the journal-ref on arXiv.** `WORKLIST.md` gives you
   the link and the venue string. One web form per paper; no API exists. This is
   what Scholar matches citations on, so it's worth more than it looks — and it
   needs step 1.
4. **Verify its drafted sidecar** (below) — `update.py` will have drafted it.
5. **If it has a repo:** `python update.py --step repos`, label it, then
   `sweep_github.py diff` → `apply`.
6. **Rebuild and deploy** the site.

---

## Sidecars: verify a draft, don't write one

The sidecar decides whether models describe your work *correctly*, and it used to be
described here as the one thing only you could write — which, at ten minutes each,
meant nobody wrote any. Most of it is in the paper: a claim with its magnitude, the
condition it holds under, the definition of a term you coined. So it is drafted for
you, and your job is the part that genuinely needs you — checking the numbers,
sharpening the scope, and saying which misreading actually keeps happening.

```bash
python scripts/draft_sidecars.py                      # queue the 20 most-cited
python scripts/draft_sidecars.py --ingest             # fold the answers into drafts/
python scripts/draft_sidecars.py --review             # what is drafted vs live
$EDITOR data/sidecars/drafts/<slug>.md                # correct it
python scripts/draft_sidecars.py --accept <slug>      # promote it, schema-checked
python scripts/build_site.py --deploy
```

Drafts live in `data/sidecars/drafts/` and **nothing reads them** — the site, the
validator, the fidelity check and the coverage count all glob `data/sidecars/*.md` one
level up. So a draft cannot reach a published page by accident, and `--accept` refuses
to promote one that fails the schema. Every draft opens with what to check, in the
order it pays.

`update.py` drafts a batch (default 10, `--draft-batch N`) on every run, so a new
paper's draft arrives on its own.

To write one from scratch instead: copy `data/sidecars/ties-merging-*.md` as the
worked example. Slugs come from `data/papers.yaml`; schema:
[`schema/sidecar.schema.json`](schema/sidecar.schema.json); rules:
[`docs/PAPERS.md`](docs/PAPERS.md).

The three that are easy to get backwards:

- **Paraphrase the questions, 2–4 phrasings each.** Engines fan a query into many
  sub-queries and you can't guess which phrasing wins.
- **Never paraphrase a claim.** `qa` entries point at claim *ids*; the renderer
  emits each claim verbatim. A restated claim is a second, drifting copy of your
  own finding.
- **Never a question without its answer adjacent.** A question-only passage
  matches the query and then loses the citation, because the answer isn't in the
  chunk.

Do them in citation order. Twenty verified sidecars beat 117 rushed ones.

---

## Working with co-authors

The rule: **share the source, duplicate the pointer, never duplicate the page.**
Linking to a paper page from many places helps; publishing many pages for one
paper splits authority and risks Scholar dropping it as a duplicate.

### If you're first to claim a paper

You own its canonical page and its sidecar.

```bash
python scripts/ownership.py --claim-all   # claim everything still unclaimed
python scripts/ownership.py --manifest    # regenerate the public manifest
python scripts/build_site.py --deploy     # publishes it at /paper-geo.json
```

Then tell your co-authors two things:

1. Your manifest URL, e.g. `https://borgr.github.io/paper-geo.json` — they add it
   to their `config.yaml` under `collaboration.peers`.
2. Where the sidecar lives, so they can PR claims into it rather than writing
   their own.

What you're asking them to do: **link** to your paper page, and **reuse your claim
sentence verbatim** in their README and site. Not paraphrase it — the identical
sentence from a second person is corroboration; a reworded one is a competitor.

### If someone else already owns a paper

Add their manifest to your config and let the tool defer:

```yaml
collaboration:
  peers:
    - https://coauthor.github.io/paper-geo.json
```

```bash
python scripts/ownership.py            # sets canonical_page from their manifest
python scripts/build_site.py --deploy  # publishes a LINK, not a competing page
```

Then, per shared paper: link to their page from your README and site, reuse their
claim sentence verbatim, and list the paper in your own ORCID / Semantic Scholar /
DBLP — that last one is the scholarly graph, where every co-author listing a paper
is correct and expected.

If two of you claim the same paper, `ownership.py` flags it and refuses to guess.
Decide between you; the one who lets go switches to a link.

**Where this is worth the conversation:** multi-author flagship papers with active
co-authors. For the long tail, claim them yourself and move on. Ten negotiated
papers is a good outcome.

---

## The one-time identity fixes

```bash
python scripts/audit_identity.py     # what is still open, read live, no login
python scripts/identity_tasks.py     # the payload for each fix
```

The audit is the one to re-run: it reads ORCID, arXiv's authority records, Wikidata
and Hugging Face through their public APIs and writes
[`tasks/identity_audit.md`](tasks/identity_audit.md). Every row is checkable without
a login even though every *fix* needs one — so you can tell what is actually done
rather than what you remember doing.

`identity_tasks.py` writes the payloads into [`tasks/`](tasks/) — committed on
purpose, since these are lists a human works through over days:

| file | for |
|---|---|
| `orcid_dois.txt` | ORCID *Add DOI*, citation-ordered — the reliable route |
| `orcid_import.bib` | ORCID *Add BibTeX*, DOI-bearing entries first |
| `wikidata_manual.md` | creating the author item by hand — **start here** |
| `wikidata.qs` | the same item as a batch; needs an autoconfirmed account |
| `s2_merge.md` | papers to pull onto the claimed Semantic Scholar page |
| `openalex_merge.md` | what to paste into the OpenAlex correction form |
| `arxiv_ownership.md` | arXiv papers you are not a registered author on |
| `arxiv_name_fixes.md` | arXiv records that misspell or omit your name |
| `hf_worklist.md` | HF pages to index, then to claim |
| `orcid_remove.md` | works on your ORCID that are not yours, with put-codes |
| `wikidata_followup.md` | corrections and additions to an item that exists |
| `wikidata_papers.qs` | items for papers Wikidata lacks — opt-in, read it first |
| `zenodo.md` | tools and guides with no paper, so no citable form |

Order: **ORCID first**, then arXiv ownership. ORCID is the lever for two of the
others — Semantic Scholar disambiguates on it, and OpenAlex is running ORCID-driven
merges of split profiles — and arXiv ownership is a hard prerequisite for every
journal-ref. The full checklist, with the reasoning and the routes that don't work,
is [`docs/SETUP.md`](docs/SETUP.md).

## Checking whether it's working

```bash
python measure/check_structure.py          # is the work done, and still done?
python measure/check_structure.py --links  # + every URL resolves (slow)
python measure/fidelity.py                 # are engines describing papers correctly?
```

`check_structure.py` reports coverage (a work queue) and pass/fail checks (real
regressions: invalid JSON-LD, missing highwire tags, duplicate titles, pages that
need JavaScript, a blocked crawler, a claim sentence that drifted between
surfaces).

`fidelity.py` scores what engines say about each paper against your own claims:
2 = claim and scope right, 1 = claim right and scope dropped, 0 = wrong. The 1s
are the point. Hand-check 20% of the grades before trusting the report.

Neither answers "did this cause more citations". [`docs/MEASURE.md`](docs/MEASURE.md)
explains why that question is close to unanswerable at 135 papers, and what the one
defensible design would be if you want it.

---

## When something keeps coming back

If the same item reappears in `WORKLIST.md` every month, it needs a recorded
decision, not another look:

- **Papers** → [`data/overrides.yaml`](data/overrides.yaml): `force_merge`,
  `force_distinct`, `drop`, or a per-slug field fix. Any URL a run retires leaves a
  redirect behind it automatically (refresh + canonical → the surviving page), so
  neither consolidating two pages nor correcting a title 404s a URL someone already
  linked to. The record is [`data/slug_history.yaml`](data/slug_history.yaml), written
  by `collect.py` and read by `build_site.py`; it is append-only, because deleting a
  line breaks a published address. `validate.py` will tell you if a `fields:` key
  points at a slug that has since moved.
- **Repos** → set `reviewed: true` on the entry in `data/repos.yaml`. That freezes
  it against all future proposals.

And fix it upstream too where you can, so the correction propagates to Scholar,
Semantic Scholar, and OpenAlex instead of only to you.

---

## Command reference

| Command | Does | Writes anything? |
|---|---|---|
| `update.py` | all eight steps | no |
| `update.py --step <name>` | one step | no |
| `update.py --refresh-bib` | refresh the bibliography first | no |
| `update.py --apply` | + push approved repo changes | **yes, GitHub** |
| `scripts/collect.py` | rebuild `papers.yaml` | local only |
| `scripts/collect.py --allow-shrink` | + write even if coverage dropped sharply | local only |
| `scripts/sweep_github.py propose\|diff\|apply` | repo topics, descriptions, `CITATION.cff` | apply: **yes** |
| `scripts/propose_topics.py [--ingest]` | label repos with a model | local only |
| `scripts/draft_sidecars.py [--ingest\|--review\|--accept]` | draft sidecars for you to verify | local only |
| `scripts/ownership.py [--manifest] [--claim-all]` | reconcile with co-authors | local only |
| `scripts/links_block.py propose\|diff\|apply` | links block in paper-code READMEs | apply: **yes** |
| `scripts/build_site.py [--deploy]` | generate the site | deploy: **yes** |
| `scripts/hf_papers.py [--live] [--verify]` | HF worklist / re-check | local only |
| `scripts/audit_identity.py [--no-hf]` | live-read ORCID, arXiv, Wikidata, HF, S2 | local only |
| `scripts/identity_tasks.py` | payloads for the one-time identity fixes | local only |
| `scripts/wikidata_apply.py [--apply] [--check-account]` | apply the Wikidata diff | apply: **yes, Wikidata** |
| `scripts/validate.py` | schema check + shipped-bug regressions + selftest | no |
| `measure/check_structure.py [--links]` | the "A" checks | no |
| `measure/fidelity.py [--ingest]` | the "C" diagnostic | no |
