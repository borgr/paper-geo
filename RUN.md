# Running it

One command, four clocks, and two things that need a person. Read-only by default:
nothing leaves your machine without `--apply`, `--deploy` or `--yes`.

The rules the output has to satisfy are [docs/RULES.md](docs/RULES.md); the sidecar
spec is [docs/SIDECAR.md](docs/SIDECAR.md); an agent's procedure is
[SKILL.md](SKILL.md). This file is the operating design and the human's terminal
guide, in that order.

---

## 1. Four clocks, not one

Almost every mistake in a project like this comes from running the wrong clock's
work.

| Clock | Trigger | What runs | Who |
|---|---|---|---|
| **Every run** | monthly, or after any change | `python update.py` — all ten steps, read-only | code, unattended |
| **On new material** | a paper posted, a repo created | `python update.py --refresh-bib`, then §5 | code, then a human once |
| **On a hand-back** | the run reports a draft or a proposal | fill the task file, `--ingest`, then the author accepts | a model, then the author |
| **On a decision** | a rule or a format is wrong | change the rule *and* its enforcement, together | a human, deliberately |

Nothing that publishes is on any of them. `--apply` and `--deploy` sit outside all
four on purpose.

## 2. Every run

```bash
python update.py                     # read-only: refresh everything, report what needs a human
python scripts/sweep_github.py diff  # exactly what would change on GitHub
python update.py --apply             # write the repo labels and the paper links
```

Ten steps, each independently re-runnable with `--step <name>`, each read-only. What
matters per step is not what it does but **what it will not do** — that column is the
contract.

| Step | Reads | Writes | Will not |
|---|---|---|---|
| `collect` | bib, Semantic Scholar, arXiv, HF | `data/papers.yaml` | overwrite anything in `overrides.yaml` |
| `repos` | GitHub | `data/repos.yaml` | touch a row with `reviewed: true` |
| `propose` | `data/repos.yaml` | `build/llm_tasks.json` | write to GitHub |
| `draft` | each paper's full text | `data/sidecars/drafts/` | write where the site can read it |
| `links` | full text, `data/papers.yaml` | `data/paper_code.yaml` | change a row with `reviewed: true`, or push to HF |
| `ownership` | collaborators' manifests | `paper-geo.json` | claim a paper someone else owns |
| `audit` | ORCID, arXiv, Wikidata, HF, S2 | `tasks/*` | edit any of those surfaces |
| `validate` | every data file + the docs | doc count sentences | fix a count that feeds an arithmetic claim |
| `render` | `data/` | `build/site/` | publish |
| `worklist` | all of the above + `followups`, `declines` | `WORKLIST.md` | list anything already done |

Two invariants hold it together, and both are design rather than trivia. **Nothing
derived is ever hand-edited** — a hand edit survives until the next run and then
vanishes, which is worse than failing because it looks like it worked; hand edits go
to the decision files in [RULES.md §7](docs/RULES.md#7-record-every-decision-or-lose-it).
And **every step degrades rather than fails** — a source outage costs one field, not
the run, which is what makes the loop safe to schedule (`llm.mode: api` in
`config.yaml` for the two model steps).

Monthly is plenty. Add `--refresh-bib` when your bibliography has new entries and
lives in a local checkout of the `publications` repo (`sources.publications_path`).

### What a human reads, in order

The run ends by handing back three things, and the order is the design: look at the
product, then make a decision, then publish.

1. **The rendered site**, `build/site/index.html` — the only artifact that shows the
   corpus as a reader meets it. A report cannot tell you that a page reads badly.
2. **`WORKLIST.md`**, open items only, ranked by citations. A section that is absent
   is done; that absence *is* the report, which is why nothing static is written into
   it. `## Deferred` at the bottom is real work with a release condition.
3. **The two gates**, if anything is ready: `sweep_github.py diff` then
   `update.py --apply`, and `build_site.py --deploy`.

What is yours and what is not: eight of the ten steps are code re-deriving public
facts, and a human in them is a human retyping a fetch. Two are a model's reading,
which is why they land as drafts that nothing publishes. That leaves exactly two
things for you, and both are decisions rather than typing — accepting a sidecar
draft, because it becomes an assertion under your name, and anything that writes
outward.

### Two ways a refresh talks back

**It may refuse to write.** Every source can fail, and a failed fetch returns an
empty field rather than an error — one dead API costs one field instead of the whole
run. The cost of that choice is that a bad afternoon at Semantic Scholar looks
exactly like a good one, and the next commit makes the loss permanent. So the
collector compares each run against **the last commit** and stops if coverage fell
sharply:

```
REFUSING TO WRITE -- this run has much less data than the last commit:
  abstract: 116 -> 61 (-55)
```

Look at the `!` lines above it for the source that failed, and rerun. If the drop is
real — a big merge, papers dropped on purpose — say so with
`python scripts/collect.py --allow-shrink`. `--no-arxiv` and `--no-hf` imply it,
since a skip you asked for is not news.

**It may report `title differs from arXiv`.** The details are in
`build/title_diffs.json`. This is a review item, not an error, and **either side can
be the stale one**: arXiv v2 sometimes retitles a paper your bibliography still has
under its v1 name, and your bibliography sometimes has the correct title while arXiv
never got updated. Read the pair and fix whichever is wrong — upstream in the `.bib`
if it is yours, or by posting a new arXiv version if it is theirs.

## 3. Sidecars: verify a draft, don't write one

The sidecar decides whether models describe your work *correctly*. It used to be
described as the one thing only you could write — which, at ten minutes each, meant
nobody wrote any. Most of it is in the paper: a claim with its magnitude, the
condition it holds under, the definition of a term you coined. So it is drafted from
the paper's own full text, and your job is the part that genuinely needs you —
checking the numbers, sharpening the scope, and saying which misreading actually
keeps happening.

```bash
python scripts/draft_sidecars.py                      # queue the most-cited
python scripts/draft_sidecars.py --ingest             # fold the answers into drafts/
python scripts/draft_sidecars.py --review             # what is drafted vs live
python scripts/draft_sidecars.py --show <slug>        # every claim beside its evidence
$EDITOR data/sidecars/drafts/<slug>.md                # correct it
python scripts/draft_sidecars.py --accept <slug>      # promote it, checked
```

`--show` is the review itself, and it is the reason this takes minutes rather than an
hour: each claim printed with its scope, whether the paper really has the table or
section it cites, and the paper's own sentence around every number it states. What it
prints is what you would otherwise get by keeping the PDF open in another window.

`update.py` drafts a batch (default 10, `--draft-batch N`) every run, so a new
paper's draft arrives on its own. Drafts live in `data/sidecars/drafts/` and
**nothing reads them** — the site, the validator, the fidelity check and the coverage
count all glob `data/sidecars/*.md` one level up, so a draft cannot reach a published
page by accident.

`--accept` refuses twice over. A structural failure means the file is broken. A
quality finding — a band in [SIDECAR §2](docs/SIDECAR.md) broken, or a figure that is
not in the paper — means it is well-formed and says something you would not want to
have said, and accepting is the moment those become your assertion in public. That
tier is only reported when `validate.py` runs; here it stops the promotion. Override
it with `--anyway`, which promotes and prints each problem it ignored.

**A draft is only as good as the text behind it.** Each is written from the paper's
own full text, resolved through whichever open source has it — arXiv's HTML
rendering, the ACL Anthology, Unpaywall, Semantic Scholar, Europe PMC, the arXiv
PDF. That chain reaches all but a handful; for the rest there is no public copy at
all, and a draft written from a title is exactly the kind of page that quotes a
number you never published:

```bash
python scripts/fulltext.py --report          # per-paper: which source answered, how long
```

Anything it lists as thin you can fix in one step: drop the PDF you already have into
`data/fulltext/<slug>.pdf` and re-run. That directory is checked *first* and is
gitignored on purpose — a publisher's PDF is not yours to redistribute and a public
repo is redistribution, so only the sidecar distilled from it gets published. See
[`data/fulltext/README.md`](data/fulltext/README.md).

Do them in citation order. Twenty verified sidecars beat a hundred rushed ones.

## 4. Labelling repos

Default mode is `skill`: the `propose` step writes `build/llm_tasks.json` and stops.
Fill each task's `proposal` object against the embedded schema, then:

```bash
python scripts/propose_topics.py --ingest
python scripts/sweep_github.py diff    # exactly what would change
python update.py --apply               # write it
```

The labelling rules are [RULES.md §11.2](docs/RULES.md#112-labelling-topics-and-descriptions),
which is also where the prompt gets them. `reviewed: true` on a repo freezes it
against every future proposal.

## 5. A new paper just went up

```bash
python update.py --refresh-bib      # picks it up; tells you what it still needs
```

Then, highest value first:

1. **Claim it on arXiv**, unless you were the submitter — ownership defaults to
   whoever pressed submit. `tasks/arxiv_ownership.md` says whether you own it; if
   not, ask the submitting co-author for the paper password
   (<https://arxiv.org/auth/need-paper-password>, instant) or file
   <https://arxiv.org/auth/request-ownership>. Step 3 is blocked until this lands.
2. **Index its Hugging Face paper page.** `python scripts/hf_papers.py --live`
   writes `tasks/hf_worklist.md` (and `build/hf_worklist.html` to click through);
   log in to HF first, then `python scripts/hf_papers.py --verify`. This cannot be
   automated — an unauthenticated visit creates nothing.
3. **Once it has a venue, add the journal-ref on arXiv.** `WORKLIST.md` gives the
   link and the venue string. One web form per paper; no API exists. This is what
   Scholar matches citations on, so it is worth more than it looks.
4. **Verify its drafted sidecar** (§3) — a run will have drafted it.
5. **Check its code repo and project page.** Both are deduced from the paper's own
   full text by the `links` step; `data/paper_code.yaml` says what it found and how
   sure it was. Correct the row, set `reviewed: true` to freeze it, and
   `python update.py --apply` pushes the accepted ones to the Hugging Face paper
   page. For the repo's own topics and description, §4.
6. **Rebuild and deploy** the site.

Only items 1–3 need a human, and all three are account actions no code can take.
Everything else arrives on its own, which is the property the whole design is for.

## 6. Working with co-authors

The rule and the reasoning are [RULES.md §12](docs/RULES.md#12-co-authors). The
commands:

```bash
python scripts/ownership.py               # fetch peers, reconcile, report
python scripts/ownership.py --manifest    # write ours for peers to read
python scripts/ownership.py --claim-all   # claim everything still unclaimed
python scripts/build_site.py --deploy     # publishes it at /paper-geo.json
```

If you are first to claim a paper, tell your co-authors two things: your manifest
URL, e.g. `https://borgr.github.io/paper-geo.json`, which they add to their
`config.yaml` under `collaboration.peers`; and where the sidecar lives, so they can
PR claims into it rather than writing their own. If someone else owns a paper, add
their manifest to your `peers` and the tool defers — it sets `canonical_page` from
their manifest and publishes a link, not a competing page. If two of you claim the
same paper, `ownership.py` flags it and refuses to guess; the one who lets go
switches to a link.

## 7. The one-time identity fixes

The account-level checklist — ORCID, Semantic Scholar, Google Scholar, Wikidata,
Hugging Face, the canonical URL — is [docs/SETUP.md](docs/SETUP.md). It is
independent of this tool and pays for everything else, so do it first.

```bash
python scripts/audit_identity.py     # what is still open, read live, no login
python scripts/scholar_check.py      # what Scholar has that the corpus does not
python scripts/identity_tasks.py     # the payload for each fix
```

The audit is the one to re-run: it reads ORCID, arXiv's authority records, Wikidata
and Hugging Face through public APIs and writes
[`tasks/identity_audit.md`](tasks/identity_audit.md). Every row is checkable without
a login even though every *fix* needs one — so you can tell what is actually done
rather than what you remember doing.

`scholar_check.py` answers a different question, and it is the only thing here that
can: **is a paper missing entirely?** Every other check reads the corpus and asks
whether it is well-formed. This one reads a list built by a different process and
asks whether the corpus is *complete* — which catches the two failures nothing else
can see, a paper absent from the source bibliography and a paper the authorship gate
excluded. Its findings open [WORKLIST.md](WORKLIST.md) when there are any, because a
paper that is not there at all outranks every improvement to one that is.

`identity_tasks.py` writes the payloads into [`tasks/`](tasks/), committed on purpose
since these are lists a human works through over days:

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
others — Semantic Scholar disambiguates on it, and OpenAlex runs ORCID-driven merges
of split profiles — and arXiv ownership is a hard prerequisite for every
journal-ref.

## 8. Checking whether it worked

```bash
python measure/check_structure.py          # is the work done, and still done?
python measure/check_structure.py --links  # + every URL resolves (slow)
python measure/fidelity.py                 # are engines describing papers correctly?
```

`check_structure.py` reports coverage (a work queue) and pass/fail checks (real
regressions: invalid JSON-LD, missing highwire tags, duplicate titles, pages that
need JavaScript, a blocked crawler, a claim sentence that drifted between surfaces).
`fidelity.py` scores what engines say about each paper against your own claims: 2 =
claim and scope right, 1 = claim right and scope dropped, 0 = wrong. The 1s are the
point. Hand-check 20% of the grades before trusting the report.

Neither answers "did this cause more citations".
[docs/EVIDENCE.md](docs/EVIDENCE.md) explains why that question is close to
unanswerable at this corpus size, and what the one defensible design would be.

## 9. Setup, once

```bash
pip install pyyaml jsonschema          # jsonschema is optional but catches more
gh auth login                          # the sweep and the deploy use the gh CLI
```

Then edit [`config.yaml`](config.yaml): your name and name variants, ORCID, email,
canonical URL, and the id for each index (Semantic Scholar, OpenAlex, Google
Scholar, DBLP, GitHub, Hugging Face, Wikidata). That file is the only place anything
about you appears — and it is committed, so no secret goes in it. The Wikidata bot
password lives in an environment variable or the gitignored `.wikidata_bot`.

## 10. Command reference

| Command | Does | Writes anything? |
|---|---|---|
| `update.py` | all ten steps | no |
| `update.py --step <name>` | one step | no |
| `update.py --refresh-bib` | refresh the bibliography first | no |
| `update.py --apply` | + push approved repo changes and paper links | **yes, GitHub + Hugging Face** |
| `scripts/collect.py` | rebuild `papers.yaml` | local only |
| `scripts/collect.py --allow-shrink` | + write even if coverage dropped sharply | local only |
| `scripts/sweep_github.py propose\|diff\|apply` | repo topics, descriptions, `CITATION.cff` | apply: **yes** |
| `scripts/propose_topics.py [--ingest]` | label repos with a model | local only |
| `scripts/draft_sidecars.py [--ingest\|--review\|--show\|--accept [--anyway]]` | draft sidecars for you to verify | local only |
| `scripts/fulltext.py [--report\|--slug\|--refetch]` | resolve each paper's full text; report thin ones | cache only |
| `scripts/paper_code.py [--apply] [--slug]` | deduce the code repo and project page from the paper's own text | apply: **yes, Hugging Face** |
| `scripts/ownership.py [--manifest] [--claim-all]` | reconcile with co-authors | local only |
| `scripts/links_block.py propose\|diff\|apply` | links block in paper-code READMEs | apply: **yes** |
| `scripts/build_site.py [--deploy]` | generate the site | deploy: **yes** |
| `scripts/hf_papers.py [--live] [--verify]` | HF worklist / re-check | local only |
| `scripts/audit_identity.py [--no-hf]` | live-read ORCID, arXiv, Wikidata, HF, S2 | local only |
| `scripts/scholar_check.py [--quiet]` | diff your Google Scholar profile against the corpus — the only check that can see a paper the pipeline never received | local only |
| `scripts/identity_tasks.py` | payloads for the one-time identity fixes | local only |
| `scripts/wikidata_apply.py [--apply] [--check-account]` | apply the Wikidata diff | apply: **yes, Wikidata** |
| `scripts/validate.py [--fix-counts] [--strict]` | schema check + shipped-bug regressions + selftest; `--fix-counts` refreshes the corpus sizes stated in the docs. Exits 1 on a structural failure (which stops `update.py`), 0 on a stale count; `--strict` makes both fatal | `--fix-counts`: the doc sentences |
| `measure/check_structure.py [--links]` | the "A" checks | no |
| `measure/fidelity.py [--ingest]` | the "C" diagnostic | no |
