# paper-geo

**How do you make your papers and code findable — and correctly described — by AI
answer engines and scholarly indexes?** This is a pipeline that audits the gap, fixes
the automatable part, and hands you a ranked list of what only you can do.

GEO stands for generative engine optimization, which is SEO's counterpart for tools
that answer in prose instead of returning a list of links. The goal is not to rank. It
is to be retrieved, and then described accurately, by whatever writes the answer.

Built for one researcher's corpus (114 papers, 33 repos) and config-driven, so it runs
for yours too. [Set it up for your own papers](#set-it-up-for-your-own-papers) is the
five-step version of that.

## Start here

Python 3.10 or newer, two packages from `requirements.txt`, and everything else from
the standard library. The GitHub steps shell out to the
[`gh` CLI](https://cli.github.com), so install that and run `gh auth login` once.
Without it the `repos` step reports a failure and the other nine carry on.

```bash
git clone https://github.com/borgr/paper-geo && cd paper-geo
pip install -r requirements.txt
python update.py
```

That runs against the corpus already in `data/`, which is the quickest way to see the
output before deciding whether you want it for your own. It writes only inside this
checkout — `data/` holds the derived records, `build/` is gitignored scratch plus the
rendered site, `tasks/` holds files to paste or upload by hand, and `WORKLIST.md` is
the ranked list of what is left. No write reaches GitHub, arXiv, ORCID or Hugging Face
until you pass `--apply` or `--deploy`.

Then read two files. **`WORKLIST.md`** is what needs you — its first screen is a
ranked start-here list and the 500 lines under it are the reference for each item.
**`build/site/index.html`** is the corpus as a reader meets it. [RUN.md](RUN.md) is
the manual for everything after that.

## Set it up for your own papers

Five steps, in order. None of them changes anything outside your own clone, so a wrong
answer here costs a re-run and nothing else.

**1. Fork [borgr/paper-geo](https://github.com/borgr/paper-geo) and clone your fork**,
then `pip install -r requirements.txt`.

**2. Empty the previous author's data.** This is the step that matters.

```bash
python scripts/bootstrap_fork.py         # prints what it would do, changes nothing
python scripts/bootstrap_fork.py --yes   # do it
```

`data/` holds three kinds of file and all three have to go.

- **Rebuilt from public sources** — `papers.yaml`, `repos.yaml`, `fulltext/`. Deleting
  them costs one slow run and nothing else.
- **Notes on what was already done** — `slug_history.yaml`, `wikidata_created.yaml`,
  `arxiv_submissions.yaml`. True about the other person and false about you. Left in
  place, they point your paper URLs at pages that person retired, and skip creating
  Wikidata items you do not have.
- **Their decisions** — `paper_code.yaml`, `overrides.yaml`, `declines.yaml`,
  `followups.yaml`, `sidecars/`. One researcher's judgement about their own work,
  several of them decisions *not* to publish something. Left in place, they publish
  that judgement under your name and nothing downstream can tell the difference.

The comment block at the head of each file survives, so you can still read what the
file is for.

**3. Put yourself in `config.yaml`.** `identity` and `ids` are who you are.
`sources.bibtex_url` points at your own `.bib`, and setting it to `null` is fine —
`collect` then seeds the corpus from your Semantic Scholar author record instead.
`site.repo` and `site.base_url` decide where the site lands, and
[Where the site ends up](#where-the-site-ends-up) is worth reading before you set
`site.repo`, because deploying over a Pages repo that already serves a page replaces
that page.

**4. Check nothing of theirs survived.**

```bash
python scripts/bootstrap_fork.py --check
```

Run this after step 3 and do not skip it. It prints every `config.yaml` line still
carrying the previous author's name, ORCID, ids or URLs, and exits non-zero if it
finds any. Nothing else in the repo can catch a leftover — for the previous author
those values were correct, so no other check treats them as wrong.

**5. Build.**

```bash
python update.py
```

If the run stops with `REFUSING TO WRITE`, pass `python scripts/collect.py
--allow-shrink` once and then go back to `python update.py`. That guard fires when a
run holds much less than the last one, which is what a dead API looks like from the
inside, and it cannot tell that from a corpus you replaced on purpose. Usually it
stays quiet, because a corpus with none of the previous author's papers in it is read
as a first run rather than as a loss.

Then work through [docs/SETUP.md](docs/SETUP.md), a one-time checklist for the
*surfaces* — the pages and records other people host about your work, meaning ORCID,
Google Scholar, Wikidata, arXiv and Hugging Face. Its first three items make every
index agree on who you are, and nothing after that works properly until they do.

To hand a colleague a bundle with their own records already looked up, `python
scripts/handover.py "Their Name"` builds one —
[handover/tamar-rott-shaham/](handover/tamar-rott-shaham/) is what it produces.

## Where the site ends up

The generator writes into `build/site/` and publishes to GitHub Pages, so **you do not
need a domain to have somewhere to point at**. Without a dedicated domain, Pages
serves a `<user>.github.io` repo at that name. For this corpus that is
[borgr.github.io](https://borgr.github.io), with one page per paper beneath it.

    https://borgr.github.io/papers/tinybenchmarks-evaluating-llms-with-fewer-examples/

`site.repo` and `site.base_url` in `config.yaml` set both of those. Every address in
the output is built from them — the canonical URL of each page, the sitemap, and the
identifier inside each page's machine-readable block — so moving to a custom domain
later is one config change and a rebuild.

## Your first hour

**One sidecar, end to end.** A **sidecar** is a short companion page stating one
paper's own claims, the scope each holds in, and the ways it gets misread. It is the
only thing here that changes what an answer engine *says* about your work rather than
whether it finds it, and it is the one piece nobody can write for you — confirming a
number and naming the misreading that keeps happening needs the author.

Start with your most-cited paper.

```bash
python scripts/fulltext.py --report               # did this paper's text resolve?
python scripts/draft_sidecars.py --limit 1        # draft the top of the queue
python scripts/draft_sidecars.py --show <slug>    # every claim beside the paper's own sentence
$EDITOR data/sidecars/drafts/<slug>.md            # fix the numbers, sharpen the scope
python scripts/draft_sidecars.py --accept <slug>  # promote it, checked
python update.py --step render
python scripts/build_site.py --deploy             # now it is public
```

Two things can stop you. If `--report` calls this paper thin, drop the PDF you already
have into `data/fulltext/<slug>.pdf` and re-run, because no text means no draft. If
the drafting step asks for a model, [RUN.md §9](RUN.md#9-setup-once) has the three
ways to give it one, and the default needs no API key.

Then repeat in citation order. Twenty verified sidecars beat a hundred rushed ones.
[RUN.md §3](RUN.md#3-sidecars-verify-a-draft-dont-write-one) is the full loop,
including `--mend`, which fixes what the checks flag, and `--suspect`, which decides
what to read first.

## The one-time work, in order of impact

Separate from the per-paper loop above, and done once. Every item is somebody else's
website, so this is clicking rather than running, and [docs/SETUP.md](docs/SETUP.md)
has the actual steps. The order is leverage over effort. The first three make every
index agree on who you are, and nothing after them works properly until they do — a
sidecar published under an identity that resolves to two people still gets attributed
to the wrong person.

1. **[ORCID, populated and wired everywhere](docs/SETUP.md#1-orcid--populate-it-then-wire-it-everywhere)** — Semantic Scholar and OpenAlex both re-cluster off ORCID, so this is the fix that makes other problems shrink without you.
2. **[arXiv, papers claimed](docs/SETUP.md#2-arxiv--claim-your-papers-then-use-the-author-page-you-get-for-free)** — the author page you get for free is a surface you do not have to host, and the journal reference is what Scholar matches citations on.
3. **[One profile per index](docs/SETUP.md#3-one-profile-per-index)** — two records for one person split the citation count between them, which is what the baseline below found.
4. **[A Wikidata item](docs/SETUP.md#4-wikidata--a-free-entity-anchor)** — the entity anchor several answer engines resolve names against, and free.
5. **[One canonical URL](docs/SETUP.md#5-one-canonical-url--and-what-to-do-with-the-page-humans-actually-visit)** — every index pointing at the same page instead of five.
6. **[OpenAlex duplicates, merged](docs/SETUP.md#6-openalex-duplicates)** — same split as item 3, in the index most literature agents query.
7. **[Code and artifacts](docs/SETUP.md#7-code-and-artifacts)** — repo topics, a description, a DOI for anything worth citing on its own.

Stopping after item 3 is reasonable. A corpus with those done and a page per paper is
findable and correctly attributed, which is most of the value here.

## What you are up against

Three separate systems have to find your work, and each one gets there a different
way. Web crawlers (Bing → ChatGPT, Brave → Claude, Perplexity, Google), the scholarly
graph (Scholar, Semantic Scholar, OpenAlex, DBLP — what Elicit, Consensus, and most
literature agents actually query), and the text that models are trained on. Optimizing
for one does little for the others, and most advice online treats them as one thing.

For work that is already well known, the failure mode is usually not being unfindable.
It's being found and described **wrongly** — overstated, mis-scoped, or credited to
the wrong result. LLM summaries overstate scientific conclusions about 5× more often
than human ones do
([Peters & Chin-Yee 2025](docs/EVIDENCE.md#5-machine-readable-science-the-frontier-this-bets-on)).
No index can fix that for you; publishing your own claims and scope conditions is the
only lever.

## What it does

```bash
python update.py                     # read-only: refresh everything, report what needs you
python scripts/sweep_github.py diff  # exactly what would change on GitHub
python update.py --apply             # write it
```

Ten steps, each re-runnable on its own with `--step <name>`.

| | |
|---|---|
| `collect` | one record per paper, from your bibliography plus Semantic Scholar, arXiv and Hugging Face |
| `repos` | refresh the state of every code repo |
| `propose` | suggest GitHub topics for repos that have none |
| `draft` | draft the next batch of [sidecars](#your-first-hour) from each paper's full text |
| `links` | work out each paper's code repo and project page |
| `ownership` | settle with co-authors who owns what |
| `audit` | check the surfaces nobody here controls — ORCID, Scholar, Wikidata, arXiv, Hugging Face |
| `validate` | check every record and sidecar against the schema |
| `render` | build the site into `build/site/` |
| `worklist` | rank what only a person can do into `WORKLIST.md` |

Eight of the ten steps need nothing from you. `propose` and `draft` hand back drafts
that stay unpublished until you say otherwise. The whole run is read-only unless you
pass `--apply`, and every change that leaves your own clone goes through `propose →
diff → apply`.

What the first run found on this corpus: two Semantic Scholar author records splitting
the publication list in half, an ORCID with zero works, no Wikidata item, 94% of arXiv
records missing a journal-ref (which is what Scholar matches citations on), nearly
half the papers with no Hugging Face page, zero GitHub topics across every repo, and a
venue name sitting in an index as a paper title. The full baseline is
[docs/EVIDENCE.md §6](docs/EVIDENCE.md#6-the-baseline-what-the-corpus-looked-like-before-any-of-this).

## Documentation

Seven files, and each rule has exactly one of them as its home. Edit two of them with
care. The drafting rules in `docs/SIDECAR.md` §2 and the labelling rules in
`docs/RULES.md` §11.2 are not descriptions of a prompt, they are the prompt, read out
of the markdown when the model is called. Rewording them changes what the model is
told.

| | |
|---|---|
| [RUN.md](RUN.md) | **how to run it** — how often to run what, what each step will not do, adding a new paper, sidecars, co-authors |
| [docs/RULES.md](docs/RULES.md) | **the rules, once** — identity, how text is split up, coined names, papers, repos, co-authors, and what is actually enforced |
| [docs/SIDECAR.md](docs/SIDECAR.md) | the per-paper sidecar — the drafting prompt, the checkable rules, and the format decisions still open |
| [docs/SETUP.md](docs/SETUP.md) | **the one-time checklist** — ORCID, Scholar, Wikidata, HF, in order |
| [docs/EVIDENCE.md](docs/EVIDENCE.md) | what is known about AI answer-engine retrieval, graded by how strong the evidence is, including what had no effect, and how to tell if this worked |
| [BACKLOG.md](BACKLOG.md) | what we parked on purpose — the only file here that no script generates |
| [SKILL.md](SKILL.md) | agent entry point (Claude Code skill) — the contract, the loop, the stop conditions |

## Design rules

- **Identifiers are the truth and URLs are worked out from them.** A URL you store
  goes stale on its own.
- **Human decisions are recorded, not remembered.** Everything is re-derived each run,
  so a judgment call goes in `data/overrides.yaml`, a `reviewed: true` flag, or
  `data/declines.yaml` — or it silently reverts. Deciding *not* to do something is a
  decision too, which is what the last of those is for.
- **Flag, don't auto-merge.** Two records that might be the same paper are reported
  for you to judge, never merged for you. Expect real duplicates in that list. The
  check that keeps "BabyLM Turns 3" and "Turns 4" apart is the same one that puts them
  there, and a wrong merge costs far more to undo than a wrong flag costs to read.
- **Accuracy over coverage.** A wrong topic or a padded claim is worse than an absent
  one. Repeating keywords to game retrieval has been measured to make it *worse*.
- **Read-only by default.** A write here lands on a public record that other people's
  tools read, so nothing goes out until you pass `--apply`.

## Not this

No hidden text, no instructions aimed at automated readers, no keyword stuffing, no
extra preprint mirrors, no citation-count games. Some of those have been measured to
backfire, and the rest break scholarly norms. The overlap between "helps machines find
your work" and "is honest scholarship" is large, and this stays inside it.

## Status

All of it runs. See [RUN.md](RUN.md).

Collecting and deduplicating the corpus, the override files, repo labelling and the
GitHub sweep, sorting out ownership with collaborators, the site generator (one page
per paper, each carrying a `ScholarlyArticle` block of machine-readable metadata, the
`citation_*` meta tags Google Scholar reads, a plain-text `llms.txt` summary, plus a
sitemap and a robots file), the links block in each code README, the Hugging Face
worklist, schema validation, and the two scripts in `measure/`.

Three things are left to a person on purpose. Adding the journal reference to an arXiv
record, because arXiv has no write API for it. Getting a paper indexed on Hugging Face
and claiming authorship of it, because both need a logged-in browser. And *accepting*
a sidecar — `scripts/draft_sidecars.py` drafts the claims from the paper, but only an
author can confirm a number and say which limitation actually matters, so drafts wait
in `data/sidecars/drafts/` until you promote one.

## License

Code is [MIT](LICENSE). The prose and data — this documentation, the per-paper
sidecars, and the records under `data/` — are
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), so reuse either with
attribution. A paper's own full text is neither, which is why `data/fulltext/` is
gitignored and never published.
