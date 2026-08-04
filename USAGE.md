# How to use this

Three things you'll actually do: the routine refresh, adding a new paper, and
writing a sidecar. Everything else is a variation.

Read-only by default. Nothing leaves your machine without `--apply`, `--deploy`,
or `--yes`.

---

## Once, at setup

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

Six steps, each safe to re-run, in order: rebuild `data/papers.yaml` from your
bibliography + Semantic Scholar + arXiv + Hugging Face → refresh repo state →
label anything unlabelled → reconcile paper ownership with collaborators →
validate against the schemas → regenerate `WORKLIST.md`.

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

---

## A new paper just went up

```bash
python update.py --refresh-bib      # picks it up; tells you what it still needs
```

Then, in this order — highest value first:

1. **Index its Hugging Face paper page.** `python scripts/hf_papers.py` writes
   `build/hf_worklist.html`; log in to HF, click through it, then
   `python scripts/hf_papers.py --verify`. This can't be automated — an
   unauthenticated visit creates nothing.
2. **Once it has a venue, add the journal-ref on arXiv.** `WORKLIST.md` gives you
   the link and the venue string. One web form per paper; no API exists. This is
   what Scholar matches citations on, so it's worth more than it looks.
3. **Write the sidecar** (below).
4. **If it has a repo:** `python update.py --step repos`, label it, then
   `sweep_github.py diff` → `apply`.
5. **Rebuild and deploy** the site.

---

## Writing a sidecar

The only hand-written per-paper input, ~10 minutes, and the part that decides
whether models describe your work *correctly*.

```bash
cp data/sidecars/ties-merging-*.md data/sidecars/<slug>.md   # worked example
$EDITOR data/sidecars/<slug>.md
python scripts/validate.py                                    # checks the schema
python scripts/build_site.py --deploy
```

Slugs come from `data/papers.yaml`. Schema:
[`schema/sidecar.schema.json`](schema/sidecar.schema.json). Rules:
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

Do them in citation order. Twenty good sidecars beat 135 rushed ones.

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
  `force_distinct`, `drop`, or a per-slug field fix.
- **Repos** → set `reviewed: true` on the entry in `data/repos.yaml`. That freezes
  it against all future proposals.

And fix it upstream too where you can, so the correction propagates to Scholar,
Semantic Scholar, and OpenAlex instead of only to you.

---

## Command reference

| Command | Does | Writes anything? |
|---|---|---|
| `update.py` | all six steps | no |
| `update.py --step <name>` | one step | no |
| `update.py --refresh-bib` | refresh the bibliography first | no |
| `update.py --apply` | + push approved repo changes | **yes, GitHub** |
| `scripts/collect.py` | rebuild `papers.yaml` | local only |
| `scripts/sweep_github.py propose\|diff\|apply` | repo topics, descriptions, `CITATION.cff` | apply: **yes** |
| `scripts/propose_topics.py [--ingest]` | label repos with a model | local only |
| `scripts/ownership.py [--manifest] [--claim-all]` | reconcile with co-authors | local only |
| `scripts/links_block.py propose\|diff\|apply` | links block in paper-code READMEs | apply: **yes** |
| `scripts/build_site.py [--deploy]` | generate the site | deploy: **yes** |
| `scripts/hf_papers.py [--verify]` | HF worklist / re-check | no |
| `scripts/validate.py` | schema check | no |
| `measure/check_structure.py [--links]` | the "A" checks | no |
| `measure/fidelity.py [--ingest]` | the "C" diagnostic | no |
