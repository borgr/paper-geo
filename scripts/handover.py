#!/usr/bin/env python3
"""Build a starter bundle so a colleague can fork this and run it on their own corpus.

The repetitive part of "can you do this for X too?" is not the setup, it is the lookup:
which Semantic Scholar records are theirs, whether those records are split, what their
DBLP pid is, whether an ORCID already exists under that name. All of that is public and
none of it needs the colleague present, so it is code's job -- and the residue, the values
only they can answer, is what the bundle asks for.

    python scripts/handover.py "Tamar Rott Shaham" --github tamarott \
        --homepage https://tamarott.github.io

Writes `handover/<slug>/`:

    config.yaml   the blocks to paste over the fork's own, every unknown left `null`
                  with a `# CONFIRM` comment naming who can answer it
    README.md     what to do with it, in order, with the two commands inline
    records.json  what was actually fetched, so a wrong guess in config.yaml can be
                  traced to the record it came from rather than re-litigated by hand

**It decides nothing.** Every field it cannot derive from a public record is `null`. The
one field that is a judgement rather than a lookup -- `site.repo`, because deploying over
an existing GitHub Pages site replaces that site -- is `null` with the consequence spelled
out, not filled with the obvious guess. Guessing it wrong overwrites a colleague's
homepage on the first `--deploy`.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import ROOT, get_json, norm_name  # noqa: E402

S2 = "https://api.semanticscholar.org/graph/v1"
# Words that carry no facet when they appear in a title. Not a general stoplist: these are
# the ones that turn up in every ML title and would otherwise be every colleague's top
# "keyword", which is worse than an empty list because it looks derived.
DULL = set("""a an and are as at be by can do does for from how in into is it its of on or
the to via with we our new using toward towards do does not what when where which why your
using use used learning model models language large deep neural network networks approach
method methods framework study analysis paper towards case""".split())


def s2_records(name: str) -> list[dict]:
    """Every Semantic Scholar author record matching the name, largest corpus first."""
    q = urllib.parse.quote(name)
    d = get_json(f"{S2}/author/search?query={q}&limit=20&fields="
                 f"name,paperCount,citationCount,hIndex,homepage,externalIds") or {}
    want = norm_name(name)
    out = [a for a in (d.get("data") or []) if norm_name(a.get("name") or "") == want]
    return sorted(out, key=lambda a: -(a.get("paperCount") or 0))


def s2_papers(author_id: str) -> list[dict]:
    d = get_json(f"{S2}/author/{author_id}/papers?limit=500&fields="
                 f"title,year,citationCount,externalIds") or {}
    return d.get("data") or []


def dblp_pid(name: str) -> tuple[str | None, str | None]:
    """(dblp name, pid) -- the pid is what `audit_identity` needs; the name is the label."""
    d = get_json("https://dblp.org/search/author/api?format=json&q="
                 + urllib.parse.quote(name)) or {}
    hits = ((d.get("result") or {}).get("hits") or {}).get("hit") or []
    want = norm_name(name)
    for h in hits:
        info = h.get("info") or {}
        author = info.get("author") or ""
        if norm_name(author) == want:
            m = re.search(r"/pid/(\S+)$", info.get("url") or "")
            return author, (m.group(1) if m else None)
    return None, None


def orcids(name: str) -> list[dict]:
    """ORCID records under this name. More than one means a human has to pick."""
    parts = name.split()
    q = f"family-name:{parts[-1]} AND given-names:{parts[0]}"
    d = get_json("https://pub.orcid.org/v3.0/expanded-search/?q="
                 + urllib.parse.quote(q)) or {}
    out = []
    for r in d.get("expanded-result") or []:
        full = f"{r.get('given-names') or ''} {r.get('family-names') or ''}".strip()
        if norm_name(full) == norm_name(name):
            out.append({"orcid": r.get("orcid-id"), "name": full,
                        "institutions": r.get("institution-name") or []})
    return out


def keyword_candidates(titles: list[str], n: int = 12) -> list[str]:
    """Two-word phrases the corpus repeats. Candidates for a human to cut, not keywords.

    ORCID keywords and Scholar's five interest slots are searchable facets, so the test is
    whether someone would type the phrase -- which is a judgement about the field, not a
    frequency. Emitted commented out for exactly that reason.
    """
    freq: dict[str, int] = {}
    for t in titles:
        words = [w for w in re.findall(r"[A-Za-z][A-Za-z-]+", (t or "").lower())]
        for a, b in zip(words, words[1:]):
            if a in DULL or b in DULL:
                continue
            freq[f"{a} {b}"] = freq.get(f"{a} {b}", 0) + 1
    return [k for k, v in sorted(freq.items(), key=lambda kv: (-kv[1], kv[0])) if v > 1][:n]


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def config_text(name: str, found: dict, github: str | None, homepage: str | None) -> str:
    recs = found["semantic_scholar"]
    ids = [r["authorId"] for r in recs]
    split = ("\n  # %d records under this name, which is the same split this repo already\n"
             "  # handles for its own author: %s. The largest is primary; the others are\n"
             "  # merged by `audit_identity.py`, which needs all of them listed.\n"
             % (len(recs), ", ".join(f"{r['authorId']} ({r.get('paperCount')} papers)"
                                     for r in recs))) if len(recs) > 1 else "\n"
    orc = found["orcid"]
    orc_line = (f"orcid: {orc[0]['orcid']}    # CONFIRM it is yours -- matched on name "
                f"only ({', '.join(orc[0]['institutions'])})" if len(orc) == 1 else
                "orcid: null                  # CONFIRM: "
                + (f"{len(orc)} ORCID records match this name -- "
                   f"{', '.join(o['orcid'] for o in orc)}" if orc
                   else "no ORCID found under this name; register one at orcid.org"))
    kw = found["keyword_candidates"]
    return f"""\
# paper-geo starter identity: {name}
#
# Generated by `scripts/handover.py` from public records. Every value is either a
# published fact with the record it came from in records.json, or `null` with a
# `# CONFIRM` note saying who can answer it. Nothing here is a decision.
#
# Paste these blocks over the same blocks in the fork's config.yaml, keeping that file's
# surrounding comments -- they document what each key means and are not about a person.

identity:
  name: {name}
  name_variants:
    - {name}
    - {' '.join(name.split()[1:])}, {name.split()[0]}
    - {name[0]}. {' '.join(name.split()[1:])}
  # CONFIRM, and leave empty unless sure. A string here is published to Wikidata as a
  # search alias, so it earns its place only if it already appears in a printed citation
  # and belongs to nobody else. A surname-only or initials-only form always belongs to
  # somebody -- never list one.
  name_typos: []
  {orc_line}
  canonical_url: {homepage or 'null                 # CONFIRM: the one URL that goes everywhere'}
  other_pages: []
  # CONFIRM: cut this to what the work is actually about, heaviest first, and rewrite the
  # phrasing. These are the two-word phrases the titles repeat more than once -- evidence
  # of subject matter, not keywords. A keyword is something a person types into a search
  # box; several of these will not be.
  keywords: []
{chr(10).join('  #   - ' + k for k in kw)}
  email: null                    # CONFIRM
  image: null                    # CONFIRM: a photo self-hosted under static/, not a CDN path
  job_title: null                # CONFIRM
  affiliations: []               # CONFIRM
  education: []                  # CONFIRM

ids:{split}  semantic_scholar: {json.dumps([str(i) for i in ids])}
  semantic_scholar_primary: {json.dumps(str(ids[0])) if ids else 'null   # CONFIRM'}
  # Filled by the first `python scripts/audit_identity.py`, which reconciles OpenAlex
  # against the papers the collector found. Guessing them here would pin the wrong record.
  openalex: []
  openalex_duplicates: []
  google_scholar: null           # CONFIRM: the ?user= value on your Scholar profile URL
  dblp: {found['dblp_name'] or 'null                     # CONFIRM'}
  dblp_pid: {found['dblp_pid'] or 'null                 # CONFIRM'}
  github: {github or 'null                   # CONFIRM'}
  huggingface: null              # CONFIRM
  wikidata: null                 # created later by scripts/wikidata_apply.py
  linkedin: null                 # CONFIRM
  openreview: null               # CONFIRM: the ~Name_Surname1 form on openreview.net
  bluesky: null                  # CONFIRM
  mastodon: null                 # CONFIRM
  twitter: null                  # CONFIRM
  scopus: null
  researcherid: null

sources:
  bibtex_url: null               # CONFIRM: a raw .bib URL, if you keep one
  acl_anthology_person: null     # CONFIRM: https://aclanthology.org/people/<name>/, if any

site:
  # The one judgement in this file, left blank on purpose. `build_site.py --deploy` writes
  # the whole of this repo, so pointing it at a Pages repo that already serves a
  # hand-written page replaces that page. Either name a new repo here, or name the
  # existing one having decided that is what you want.
  repo: null                     # CONFIRM -- see above before filling it
  base_url: {homepage or 'null                 # CONFIRM: must match canonical_url'}
  papers_path: /papers
  ar5iv_fallback: true
  verification:
    google: null                 # Search Console > Add property > URL prefix > HTML tag
    bing: null                   # msvalidate.01, from Add site > HTML Meta Tag
  # A github.io host answers IndexNow with 403 UserForbiddedToAccessSite, so on Pages this
  # stays null. Set it only on a domain you control.
  indexnow_key: null

github_sweep:
  include_forks: false
  base_topics: []
  exclude: []
"""


def readme_text(name: str, found: dict) -> str:
    recs = found["semantic_scholar"]
    n_papers = found["paper_count"]
    n_arxiv = found["arxiv_count"]
    return f"""\
# paper-geo for {name}

A generated starter bundle. `config.yaml` here holds the blocks to paste into a fork of
[paper-geo](https://github.com/borgr/paper-geo); everything in it is either a public fact
or a `# CONFIRM` line naming a value only you can supply. It decides nothing on your
behalf -- in particular `site.repo` is blank, because deploying over a GitHub Pages repo
that already serves a page replaces that page.

## What the lookup already found

- **{len(recs)} Semantic Scholar record(s)**: {', '.join(f"`{r['authorId']}` ({r.get('paperCount')} papers, {r.get('citationCount')} citations)" for r in recs)}.
  {'Two records for one person is the ordinary case and this repo handles it; both are listed so the merge can happen.' if len(recs) > 1 else 'One record, which is the easy case.'}
- **{n_papers} papers**, {n_arxiv} of them with an arXiv id. The collector reaches an arXiv
  paper on its own; the remainder need either a DOI or a line in `data/overrides.yaml`.
- **DBLP**: {f"`{found['dblp_pid']}`" if found['dblp_pid'] else 'no matching author page found.'}
- **ORCID**: {', '.join(o['orcid'] for o in found['orcid']) or 'none under this name.'}

`records.json` holds the raw responses, so any value above can be traced rather than
re-argued.

## Setup, in order

1. Fork `borgr/paper-geo` and clone it.
2. Empty the previous author's judgement out of `data/`, which is the step that matters:

       python scripts/bootstrap_fork.py --yes

   It deletes what the first run rebuilds, wipes the receipts that would otherwise
   redirect your URLs to someone else's retired pages, and empties the decision files
   (`paper_code.yaml`, `overrides.yaml`, `declines.yaml`, `followups.yaml`, `sidecars/`)
   while keeping the comment block at the head of each, which is how you find out what
   the file is for. Inheriting those files publishes another researcher's decisions --
   including decisions not to publish something -- under your name.
3. Paste the blocks from this `config.yaml` over the same blocks in the fork's
   `config.yaml`, then work through every `# CONFIRM`.
4. Check nothing of the previous author's is left:

       python scripts/bootstrap_fork.py --check

   It exits non-zero and prints each `config.yaml` line still carrying their name, ORCID,
   ids or URLs. No other check in the repo catches those, because for them they were right.
5. Build:

       python update.py

   Read `WORKLIST.md` when it finishes. It asks only for things no code can do: account
   actions behind a login, and approving text that would go out under your name.

## What it will and will not do for you

It re-derives your bibliography from public sources every run, builds a site with
per-paper structured data, and writes a worklist of the gaps. It does not touch any of
your accounts: every outward write (`--deploy`, `--apply`, `--accept`) is a separate
command you run deliberately.
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("name", help="the colleague's name, spelled as their papers spell it")
    ap.add_argument("--github", help="GitHub handle, if known")
    ap.add_argument("--homepage", help="their existing homepage URL, if any")
    ap.add_argument("--out", default=os.path.join(ROOT, "handover"),
                    help="directory to write <slug>/ into")
    args = ap.parse_args()

    recs = s2_records(args.name)
    if not recs:
        sys.exit(f"no Semantic Scholar author record matches {args.name!r} exactly. "
                 f"Check the spelling their papers use -- the lookup is name-exact on "
                 f"purpose, since a fuzzy match here would build a bundle around somebody "
                 f"else's corpus.")
    papers = s2_papers(recs[0]["authorId"])
    dname, pid = dblp_pid(args.name)
    found = {
        "name": args.name,
        "semantic_scholar": recs,
        "dblp_name": dname,
        "dblp_pid": pid,
        "orcid": orcids(args.name),
        "paper_count": sum(r.get("paperCount") or 0 for r in recs),
        "arxiv_count": sum(1 for p in papers
                           if (p.get("externalIds") or {}).get("ArXiv")),
        "keyword_candidates": keyword_candidates([p.get("title") for p in papers]),
        "top_papers": [{"year": p.get("year"), "citations": p.get("citationCount"),
                        "arxiv": (p.get("externalIds") or {}).get("ArXiv"),
                        "title": p.get("title")}
                       for p in sorted(papers,
                                       key=lambda p: -(p.get("citationCount") or 0))[:15]],
    }
    d = os.path.join(args.out, slugify(args.name))
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "config.yaml"), "w") as f:
        f.write(config_text(args.name, found, args.github, args.homepage))
    with open(os.path.join(d, "README.md"), "w") as f:
        f.write(readme_text(args.name, found))
    with open(os.path.join(d, "records.json"), "w") as f:
        json.dump(found, f, indent=1)
    print(f"wrote {os.path.relpath(d, ROOT)}/ -- config.yaml, README.md, records.json")
    todo = sum(1 for line in open(os.path.join(d, "config.yaml")) if "CONFIRM" in line)
    print(f"  {len(recs)} S2 record(s), {found['arxiv_count']} arXiv papers, "
          f"{todo} value(s) left for them to confirm")


if __name__ == "__main__":
    main()
