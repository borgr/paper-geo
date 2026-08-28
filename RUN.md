# Running it

One command, four clocks, and two things that need a person. Read-only by default:
nothing leaves your machine without `--apply`, `--deploy` or `--yes`.

The rules the output has to satisfy are [docs/RULES.md](docs/RULES.md); the sidecar
spec is [docs/SIDECAR.md](docs/SIDECAR.md); an agent's procedure is
[SKILL.md](SKILL.md).

---

## 1. Four clocks, not one

| Clock | Trigger | What runs | Who |
|---|---|---|---|
| **Every run** | the 1st of the month, or after any change | `python update.py` — all ten steps, read-only. Runs itself: [`update.yml`](.github/workflows/update.yml) | code, unattended |
| **On new material** | a paper posted, a repo created | `python update.py --refresh-bib`, then §5 | code, then a human once |
| **On a hand-back** | the run reports a draft or a proposal | fill the task file, `--ingest`, then the author accepts | a model, then the author |
| **On a decision** | a rule or a format is wrong | change the rule *and* its enforcement, together | a human, deliberately |

Nothing that publishes is on any of them. `--apply`, `--deploy` and the **Run
workflow** button sit outside all four: they are a human deciding that now is the
moment. §10.

## 2. Every run

```bash
python update.py                     # read-only: refresh everything, report what needs a human
python scripts/sweep_github.py diff  # exactly what would change on GitHub
python update.py --apply             # write the repo labels and the paper links
```

Ten steps, each independently re-runnable with `--step <name>`, each read-only. The
`Will not` column is the contract.

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

Two invariants. **Nothing derived is ever hand-edited** — a hand edit survives until
the next run and then vanishes; hand edits go to the decision files in
[RULES.md §7](docs/RULES.md#7-record-every-decision-or-lose-it). And **every step
degrades rather than fails** — a source outage costs one field, not the run, which is
what makes the loop safe to schedule (`llm.mode: api` in `config.yaml` for the two
model steps).

Monthly is plenty. Add `--refresh-bib` when your bibliography has new entries and
lives in a local checkout of the `publications` repo (`sources.publications_path`):
it reads that working tree instead of the copy last pushed to GitHub. It does not
refresh the bibliography itself — that repo owns its own pipeline. Refresh it there
first if you need to.

### What a human reads, in order

1. **The rendered site**, `build/site/index.html` — the only artifact that shows the
   corpus as a reader meets it.
2. **`WORKLIST.md`**, open items only, ranked by citations. An absent section is done.
   `## Deferred` at the bottom is real work with a release condition.
3. **The two gates**, if anything is ready: `sweep_github.py diff` then
   `update.py --apply`, and `build_site.py --deploy`.

Two things are yours, and both are decisions rather than typing: accepting a sidecar
draft, because it becomes an assertion under your name, and anything that writes
outward. The other eight steps are code re-deriving public facts.

### Two ways a refresh talks back

**It may refuse to write.** The collector compares each run against **the last
commit** and stops if coverage fell sharply:

```
REFUSING TO WRITE -- this run has much less data than the last commit:
  abstract: 116 -> 61 (-55)
```

Look at the `!` lines above it for the source that failed, and rerun. If the drop is
real — a big merge, papers dropped on purpose — say so with
`python scripts/collect.py --allow-shrink`. `--no-arxiv` and `--no-hf` imply it.

**It may report `title differs from arXiv`.** The pairs are in
`build/title_diffs.json`. A review item, not an error, and **either side can be the
stale one**: arXiv v2 sometimes retitles a paper your bibliography still has under its
v1 name, and sometimes your bibliography is right and arXiv was never updated. Fix
whichever is wrong — upstream in the `.bib` if it is yours, or by posting a new arXiv
version if it is theirs.

### When a source stops answering

`build/health.json` records, per source, how often it answered, when it last did, and
what the last failure was. The closing report prints a line only when a source looks
*broken* rather than busy, so **silence there is a claim that everything answered
recently**.

| Line | What it means | What to do |
|---|---|---|
| `rate-limited every time since …` | the URL is fine and the host is refusing our pace | get the key, or slow the host down in `common.PACE` — unless the error reads `429 budget`, which is a metered endpoint out of credits until it resets and needs no change |
| `never once answered` (with the last error named) | the URL moved, the endpoint went away, or a config field is empty | check the URL; the error in brackets says which |
| `last answered <date>, failing since` | it worked and stopped | usually upstream; if it persists, the field it feeds is stale |

Thresholds: six consecutive days of failure before "failing since" appears, two before
"never once answered", and nothing at all about a source nothing has asked about in
over a day.

The ledger does not record whether the things it checks exist. A 404 on a URL naming
one record — a paper arXiv does not have, a repo HF never indexed — is counted as a
success. URLs scraped out of paper full text are not in the ledger at all; a project
page that does not resolve is a finding about the paper, not an outage.

## 3. Sidecars: verify a draft, don't write one

The sidecar decides whether models describe your work *correctly*. Most of it is in
the paper — a claim with its magnitude, the condition it holds under, the definition
of a term you coined — so it is drafted from the paper's own full text. Your job is
checking the numbers, sharpening the scope, and saying which misreading actually keeps
happening.

```bash
python scripts/draft_sidecars.py                      # queue the most-cited
python scripts/draft_sidecars.py --ingest             # fold the answers into drafts/
python scripts/draft_sidecars.py --review             # what is drafted vs live
python scripts/draft_sidecars.py --mend               # fix what the checks still flag
python scripts/draft_sidecars.py --suspect            # which drafts to read first
python scripts/draft_sidecars.py --show <slug>        # every claim beside its evidence
$EDITOR data/sidecars/drafts/<slug>.md                # correct it
python scripts/draft_sidecars.py --accept <slug>      # promote it, checked
```

`--mend` runs before you read anything. It takes each draft that still carries a
finding, sends the model *only* the claims, scopes and question phrasings the checker
complained about, and splices the rewrites back into a draft whose other fields cannot
move — keeping a rewrite only if the finding count actually dropped. Measured over 35
papers, half kept a residue; 83% of that residue is a single field the checker can
name, and the rest is about the set of claims as a whole and stays yours.

`--suspect` ranks what no finding can catch: how much of each claim's vocabulary occurs
in the paper at all, whether a claim asserts standing ("first", "best", "novel",
"proves") the paper's own text never asserts, whether a figure only matches after
rounding, and whether the page has no cached full text at all. Read from the top and
stop when the reasons stop looking like reasons. The same lines appear on each draft's
card in the review page, naming the claim to read. Low word overlap is usually a
legitimate paraphrase — this orders your evening, it does not accuse.

`--show` is the review itself: each claim printed with its scope, whether the paper
really has the table or section it cites, and the paper's own sentence around every
number it states.

`update.py` drafts a batch (default 10, `--draft-batch N`) every run, so a new paper's
draft arrives on its own. Drafts live in `data/sidecars/drafts/` and **nothing reads
them** — the site, the validator, the fidelity check and the coverage count all glob
`data/sidecars/*.md` one level up, so a draft cannot reach a published page by
accident.

`--accept` refuses twice over. A structural failure means the file is broken. A quality
finding — a band in [SIDECAR §2](docs/SIDECAR.md) broken, or a figure that is not in
the paper — means it is well-formed and says something you would not want to have said.
That tier is only reported when `validate.py` runs; here it stops the promotion.
Override with `--anyway`, which promotes and prints each problem it ignored.

**A draft is only as good as the text behind it.** Full text is resolved through
whichever open source has it — arXiv's HTML rendering, the ACL Anthology, Unpaywall,
Semantic Scholar, Europe PMC, the arXiv PDF. That chain reaches all but a handful.

```bash
python scripts/fulltext.py --report          # per-paper: which source answered, how long
```

Anything it lists as thin you fix in one step: drop the PDF you already have into
`data/fulltext/<slug>.pdf` and re-run. That directory is checked *first* and is
gitignored — a publisher's PDF is not yours to redistribute, so only the sidecar
distilled from it gets published. See
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
2. **Index its Hugging Face paper page.** `WORKLIST.md` and `tasks/hf_worklist.md`
   give the link; log in to HF first, because an unauthenticated visit returns 404 and
   creates nothing (verified on 50 pages, 0 created). Visiting the URL while logged in
   *is* the action — there is no form and no API.
   `python scripts/audit_identity.py --no-names` re-reads the pages afterwards.
3. **Once it has a venue, add the journal-ref on arXiv.** `WORKLIST.md` gives the link
   and the venue string. One web form per paper; no API exists. This is what Scholar
   matches citations on.
4. **Verify its drafted sidecar** (§3) — a run will have drafted it.
5. **Check its code repo and project page.** Both are deduced from the paper's own
   full text by the `links` step; `data/paper_code.yaml` says what it found and how
   sure it was. Correct the row, set `reviewed: true` to freeze it, and
   `python update.py --apply` pushes the accepted ones to the Hugging Face paper
   page. For the repo's own topics and description, §4.
6. **Rebuild and deploy** the site.

Only items 1–3 need a human, and all three are account actions no code can take.

## 6. Working with co-authors

The rule is [RULES.md §12](docs/RULES.md#12-co-authors). The commands:

```bash
python scripts/ownership.py               # fetch peers, reconcile, report
python scripts/ownership.py --manifest    # write ours for peers to read
python scripts/ownership.py --claim-all   # claim everything still unclaimed
python scripts/build_site.py --deploy     # publishes it at /paper-geo.json
```

If you are first to claim a paper, tell your co-authors two things: your manifest URL,
e.g. `https://borgr.github.io/paper-geo.json`, which they add to their `config.yaml`
under `collaboration.peers`; and where the sidecar lives, so they can PR claims into it
rather than writing their own. If someone else owns a paper, add their manifest to your
`peers` and the tool defers — it sets `canonical_page` from their manifest and publishes
a link, not a competing page. If two of you claim the same paper, `ownership.py` flags
it and refuses to guess; the one who lets go switches to a link.

### Their names on your Wikidata items

Every paper item this project created states you as *author* (P50) and every co-author as
*author name string* (P2093). That is the right thing to deposit — a P50 aimed at a guessed
person welds someone else's item to your paper — and the wrong thing to leave, because a
string is a literal nothing can join on. Until they are resolved each item hangs off your
item alone.

`wikidata_coauthors.py` splits the job in two by how much trust the match deserves. Where
the paper's OpenAlex record carries a co-author's ORCID and exactly one Wikidata item
states that ORCID, the match is identifier to identifier with no name in the middle, and it
goes into `tasks/wikidata_coauthors.qs` for QuickStatements. Everything else is listed per
paper with an [Author Disambiguator](https://author-disambiguator.toolforge.org) link,
because a name string matches a namesake exactly as well as the right person.

Nothing here creates an item for anybody. A co-author with no item stays a string, which is
their correct end state — Wikidata notability asks for serious, publicly available
references, and an item made to hold an edge back to you is not that.

## 7. The one-time identity fixes

The account-level checklist — ORCID, Semantic Scholar, Google Scholar, Wikidata,
Hugging Face, the canonical URL — is [docs/SETUP.md](docs/SETUP.md). It is independent
of this tool and pays for everything else, so do it first.

```bash
python scripts/audit_identity.py     # what is still open, read live, no login
python scripts/scholar_check.py      # what Scholar has that the corpus does not
python scripts/scholar_strays.py     # citations sitting on a Scholar record you cannot see
python scripts/identity_tasks.py     # the payload for each fix
python scripts/identity_tasks.py --user-page ~/Downloads/arxiv-user.html   # once, see below
```

`audit_identity.py` is the one to re-run: it reads ORCID, arXiv's authority records,
Wikidata and Hugging Face through public APIs and writes
[`tasks/identity_audit.md`](tasks/identity_audit.md). Every row is checkable without a
login even though every *fix* needs one.

`scholar_check.py` answers the one question nothing else here can: **is a paper missing
entirely?** Every other check reads the corpus and asks whether it is well-formed. This
one reads a list built by a different process, so it catches a paper absent from the
source bibliography and a paper the authorship gate excluded. Its findings open
[WORKLIST.md](WORKLIST.md) when there are any.

`scholar_strays.py` answers a narrower question and needs `scholar_check.py` to have
run first. Scholar indexes preprints, theses and slides the APIs do not, so a profile
row should always count *more* citations than OpenAlex and Semantic Scholar do. A row
counting less means Scholar parsed a second record for that paper out of somebody's
reference list and the citations are accruing there. The remedy is Scholar's own merge,
and the output is one phrase-quoted search per row.

Its last pass asks OpenAlex once per paper, and OpenAlex meters search queries: 100 a
day free, then a 429 until midnight UTC. So the pass is partial by design — answers
cache in `build/openalex_splits.json`, the task file says how far it got, and running
it again the next day resumes there. `--skip-openalex` drops the pass entirely.

`identity_tasks.py` writes the payloads into [`tasks/`](tasks/), committed on purpose
since these are lists a human works through over days — plus one from
`scholar_check.py`:

| file | for |
|---|---|
| `bib_missing.md` | papers to add to the source bibliography, BibTeX already resolved |
| `orcid_dois.txt` | ORCID *Add DOI*, citation-ordered — the reliable route |
| `orcid_import.bib` | ORCID *Add BibTeX*, DOI-bearing entries first |
| `wikidata_manual.md` | creating the author item by hand — **start here** |
| `wikidata.qs` | the same item as a batch; needs an autoconfirmed account |
| `wikidata_coauthors.md` | co-author strings on your paper items and the items they resolve to |
| `wikidata_coauthors.qs` | the ORCID-matched half of that as a batch, safe to paste unread |
| `s2_merge.md` | papers to pull onto the claimed Semantic Scholar page |
| `scholar_strays.md` | Scholar searches that surface a second record for one paper, from `scholar_strays.py` |
| `openalex_merge.md` | what to paste into the OpenAlex correction form |
| `arxiv_ownership.md` | arXiv papers you are not a registered author on |
| `arxiv_jref.md` | the journal-ref and published DOI to type into each arXiv listing |
| `arxiv_name_fixes.md` | arXiv records that misspell or omit your name |
| `hf_worklist.md` | HF pages to index, then to claim |
| `orcid_remove.md` | works on your ORCID that are not yours, with put-codes |
| `wikidata_followup.md` | corrections and additions to an item that exists |
| `wikidata_papers.qs` | items for papers Wikidata lacks — opt-in, read it first |
| `zenodo.md` | tools and guides with no paper, so no citable form |

Order: **ORCID first**, then arXiv ownership. Semantic Scholar disambiguates on ORCID
and OpenAlex runs ORCID-driven merges of split profiles; arXiv ownership is a hard
prerequisite for every journal-ref.

### The arXiv journal-ref list is clicks, not API

No library or agent can fill this form: arXiv's API is read-only with no
metadata-write endpoint at any access level; their `robots.txt` disallows `/user`,
the only page mapping an arXiv id to the submission id the form needs; and `/jref`
takes no identifier.

So code decides *which* papers and *what to type*, and you click. Every field value is
in [`tasks/arxiv_jref.md`](tasks/arxiv_jref.md) — the journal-ref built from the
publisher's own BibTeX, the published DOI (never the `10.48550/arXiv.…` one), and why
`Report number:` stays blank on all of them.

One optional step makes that file link straight to each paper's form instead of to the
abs page. Sign in, open <https://arxiv.org/user>, save the page, and:

```bash
python scripts/identity_tasks.py --user-page ~/Downloads/arxiv-user.html
```

It reads the file you saved — no request is made on your behalf — and caches the ids in
`data/arxiv_submissions.yaml`, so this is once, not per run.

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
[docs/EVIDENCE.md](docs/EVIDENCE.md) covers why that question is close to unanswerable
at this corpus size, and what the one defensible design would be.

## 9. Setup, once

```bash
pip install -r requirements.txt        # two packages; everything else is stdlib
gh auth login                          # the sweep and the deploy use the gh CLI
```

Then edit [`config.yaml`](config.yaml): your name and name variants, ORCID, email,
canonical URL, and the id for each index (Semantic Scholar, OpenAlex, Google Scholar,
DBLP, GitHub, Hugging Face, Wikidata). That file is the only place anything about you
appears — and it is committed, so no secret goes in it.

Two optional environment variables, both secrets:

```bash
export S2_API_KEY=…      # free, https://www.semanticscholar.org/product/api
```

Without it, Semantic Scholar is reached through a rate-limit pool shared with every
anonymous caller; when its search refuses, the Scholar check cannot resolve a missing
paper and has to report that no index has it. The other is `WIKIDATA_BOT_PASSWORD`,
read from the environment or the gitignored `.wikidata_bot` and used only by
`wikidata_apply.py`, the one script that logs in anywhere.

## 10. Unattended: what GitHub Actions does

| Workflow | Trigger | Does | Writes outward? |
|---|---|---|---|
| [`check.yml`](.github/workflows/check.yml) | every push and PR | `validate.py --strict`, then the smoke suite, on 3.10 and 3.12 | no — and no network at all |
| [`update.yml`](.github/workflows/update.yml) | 1st of the month, 06:37 UTC | `python update.py`, commit what changed | no |
| [`update.yml`](.github/workflows/update.yml) | **Run workflow** button | the same, plus every tick-box you leave ticked | **yes** |

`check.yml` is offline on purpose: everything that needs the network is in the other
file, where a source failing is reported rather than fatal.

The scheduled leg of `update.yml` re-derives and commits, and does nothing else — no
model calls, no outward writes, no money. The button leg is the same run with the
writes turned on, and its defaults are ticked by how hard each one is to take back:
Wikidata (every edit a public revision with a one-click undo), repo metadata and
Hugging Face links (own accounts, one API call to replace), the site deploy (a full
rebuild from committed data). Untick any of them and the rest still runs.

**No leg accepts a sidecar draft.** `--accept-all` exists and CI does not call it: a
wrong repo topic is one call to fix, and a wrong sentence about a result that an answer
engine has already quoted cannot be un-quoted.

### Secrets

Repository → Settings → Secrets and variables → Actions. Every one is optional, and a
missing one silently skips the step that needed it rather than failing the run — which
is what makes a dispatch from a fork a dry run.

| Secret | Needed for | Without it |
|---|---|---|
| `S2_API_KEY` | every leg | the anonymous rate-limit pool; the audit starts reporting papers as unindexed that are indexed |
| `GH_TOKEN` | repo metadata, HF links, site deploy | those three skip. Must be a PAT — the built-in `GITHUB_TOKEN` cannot push to the Pages repo, which is a different repository |
| `WIKIDATA_BOT_USER`, `WIKIDATA_BOT_PASSWORD` | the Wikidata tick-box | it skips |
| `ANTHROPIC_API_KEY` | drafting sidecars unattended | nothing is drafted, and nothing is queued either |

### What a runner cannot do

**Google Scholar.** `scholar_check.py` is fetched from a datacenter IP, and Scholar
answers those with a challenge page rather than a profile. No fix short of a
self-hosted runner.

The unattended run asks the narrower half of the same question against Semantic
Scholar's author record, which answers from anywhere: *is there a paper an index
attributes to you that the bibliography has never received?* It finds strictly less —
measured on this corpus, Scholar finds three absent papers and this finds none of them,
because S2's author record does not hold them either. What it reliably catches is a
**new** paper that reached an index and not the bibliography. So the unattended run can
say *no new paper went missing*, and only a run from a desk can say *nothing is
missing*. Run `scholar_check.py` locally when you think of it; nothing else depends on
it being fresh.

**Remember anything.** `build/` is gitignored, and the health ledger is the one file
there that is memory rather than output — it distinguishes "arXiv did not answer just
now" from "arXiv has not answered since June". It rides in the Actions cache, and the
run also uploads it as an artifact, kept 90 days, next to whatever the task files
contained.

## 11. What publishes without you, and how to take it back

The policy is **publish by default and leave a human to check**. The line is not
outward-versus-local. It is:

> Does this write assert a **fact re-derived** from a public source, or a **claim someone
> interpreted**?

A re-derived fact is safe unattended: the next run derives it again and a wrong one
self-corrects. An interpreted claim does not — nothing recomputes it, and if an answer
engine repeats it there is no edit that reaches the repetition. So every gate that
matters sits on claims.

| Surface | Asserts | Written by | Read by a human first | Undo |
|---|---|---|---|---|
| Sidecar claims (site, `links_block`) | an interpreted claim | model, then you | **always** — `--accept`, one paper at a time | none once quoted |
| `CITATION.cff` | derived from `papers.yaml` | code | no | permanent in git history |
| Links block in a README | accepted sidecar + derived links | code | the sidecar was | revert; stays in history |
| HF paper-page links (`paper_code.py --apply`) | "this repo is this paper's code" | code, from the paper's own text | no | edit the HF page |
| Repo topics / description / homepage | an interpreted claim | **model** | **no** — 29 of 33 repos | one API call; GitHub keeps no history |
| Paper pages on the site | derived + accepted claims | code | the claims were | re-deploy, minutes; caches days |
| Wikidata statements | derived identifiers | code | no | one-click undo, full public history |
| IndexNow ping | nothing — a notification | code | no | nothing to retract |

Three rows need more than a table row.

**Repo topics and descriptions are the deliberate exception.** They are an interpreted
claim published unread, which the line above would gate. It is not gated: the undo is
one API call against your own repo, GitHub keeps no history of either field, and gating
would leave 29 of 33 repos unlabelled indefinitely. `diff` marks which values are
model-written and unread, so the `--yes` moment has that fact. To change one, edit
`data/repos.yaml`; to freeze a row against future proposals, set `reviewed: true`. A
`confidence: low` proposal is never promoted.

**The paper→code link is stronger than it looks.** Of the 32 unreviewed accepted links,
**30 are backed by the paper's own full text naming that URL** ("our code is available
at…"), which is a re-derived fact. The other two were inferred from an author's GitHub
handle plus a shared word, and both carry independent corroboration — the repo's own
README or description names the paper. `verdict: accept` requires the top candidate to
beat the runner-up by a margin, so a single weak candidate with no competition can clear
it; the full-text evidence is what makes that safe in practice.
`build/paper_code_why.json` holds the evidence for every row.

**What a human catches is a wrong *kind* of claim, not a wrong URL.** An `awesome-`
list is a companion resource, and calling it `codeRepository` for a survey with no code
is a category error the match rule cannot see; likewise whether a fork is *this*
paper's fork. Roughly one row in thirty. Make the check a habit rather than a gate.

**Do not automate `--accept`.** It is the only gate on the only surface with no undo,
and the one place the review is genuinely cheap.

## 12. Command reference

| Command | Does | Writes anything? |
|---|---|---|
| `update.py` | all ten steps | no |
| `update.py --step <name>` | one step | no |
| `update.py --refresh-bib` | read the bibliography from its local checkout | no |
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
| `scripts/audit_identity.py [--no-hf]` | live-read ORCID, arXiv, Wikidata, HF, S2 | local only |
| `scripts/scholar_check.py [--quiet]` | diff your Google Scholar profile against the corpus — the only check that can see a paper the pipeline never received | local only |
| `scripts/scholar_strays.py [--quiet] [--skip-openalex] [--limit N]` | copies of your papers that Scholar indexed separately, found by citation gap against the APIs; needs `scholar_check.py` first, and its OpenAlex pass resumes across days | local only |
| `scripts/identity_tasks.py [--user-page FILE]` | payloads for the one-time identity fixes; `--user-page` reads a saved copy of your arXiv articles list so the journal-ref list can deep-link each form | local only |
| `scripts/wikidata_apply.py [--apply] [--check-account]` | apply the Wikidata diff | apply: **yes, Wikidata** |
| `scripts/wikidata_coauthors.py [--quiet] [--refresh]` | co-author name strings on your paper items, matched to author items by ORCID where one exists and by name where it does not; needs paper items to exist | local only |
| `scripts/validate.py [--fix-counts] [--strict]` | schema check + shipped-bug regressions + selftest; `--fix-counts` refreshes the corpus sizes stated in the docs. Exits 1 on a structural failure (which stops `update.py`), 0 on a stale count; `--strict` makes both fatal | `--fix-counts`: the doc sentences |
| `measure/check_structure.py [--links]` | the "A" checks | no |
| `measure/fidelity.py [--ingest]` | the "C" diagnostic | no |
| `python -m unittest discover -s tests` | the wiring: every module imports, every CLI builds its parser, `STEPS` and the `step_*` functions agree, nothing in the code or the prose names a file that is gone | no, and no network |
