#!/usr/bin/env python3
"""Build a starter bundle so a colleague can fork this and run it on their own corpus.

The repetitive part of "can you do this for X too?" is the lookup, not the setup: which
Semantic Scholar records are theirs, whether those records are split, what their DBLP pid is,
whether an ORCID already exists under that name. All public, none of it needing the colleague
present -- so the bundle asks only for the residue nobody else can answer.

    python scripts/handover.py "Tamar Rott Shaham" --github tamarott \\
        --homepage https://tamarott.github.io

Reads `handover/<slug>/facts.yaml` if it exists and merges it over what the lookup found. Some
facts are only on a homepage or a co-author's Scholar page; put them there rather than editing
the output, which the next run reverts.

Writes `handover/<slug>/`:

    config.yaml   the blocks to paste over the fork's own, every unknown left `null`
                  with a `# CONFIRM` comment naming who can answer it
    README.md     what to do with it, in order, with the two commands inline
    MESSAGE.md    the note to send them with it, counts filled in from the lookup
    records.json  what was fetched, so a wrong guess in config.yaml can be traced to
                  the record it came from

**It decides nothing.** Every field it cannot derive from a public record is `null` --
including `site.repo`, where deploying over an existing GitHub Pages site replaces that site,
so the consequence is spelled out rather than filled with the obvious guess.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import textwrap
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import ROOT, get_json, norm_name, write_json  # noqa: E402

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


def facts(out_dir: str) -> dict:
    """Hand-found values, keyed like config.yaml. An input to the generator, never output."""
    import yaml
    p = os.path.join(out_dir, "facts.yaml")
    return (yaml.safe_load(open(p)) if os.path.exists(p) else None) or {}


def yaml_value(v) -> str:
    """Render a scalar or list the way the surrounding config.yaml renders them.

    Includes its own leading space or newline so a list does not leave a trailing space
    behind on the key's line.
    """
    def scalar(x) -> str:
        # Quote anything a YAML reader would take apart -- a colon starts a mapping, a hash
        # starts a comment, and a comma inside a flow context ends the item.
        return json.dumps(x) if isinstance(x, str) and re.search(r"[:#,]|^[@\[{]", x) else str(x)

    if isinstance(v, list):
        if any(isinstance(x, dict) for x in v):
            import yaml
            body = yaml.safe_dump(v, sort_keys=False, allow_unicode=True).rstrip()
            return "\n" + "\n".join("    " + ln for ln in body.splitlines())
        return "".join(f"\n    - {scalar(x)}" for x in v) or " []"
    return " " + scalar(v)


def config_text(name: str, found: dict, github: str | None, homepage: str | None,
                extra: dict | None = None) -> str:
    extra = extra or {}
    ex_id, ex_ident = (extra.get("ids") or {}), (extra.get("identity") or {})
    recs = found["semantic_scholar"]
    # The lookup matches the current name exactly, so a record filed under a former name is
    # invisible to it and has to be named by hand -- and it matters, because an unmerged old
    # record is a second author page splitting the citation count.
    ids = [str(r["authorId"]) for r in recs] + [str(i) for i in ex_id.get(
        "semantic_scholar_extra") or []]

    def field(block: dict, key: str, fallback: str) -> str:
        """A hand-found value if there is one, else the CONFIRM line asking for it."""
        return f"{key}:{yaml_value(block[key])}" if key in block else f"{key}: {fallback}"

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
    surname = " ".join(name.split()[1:])
    variants = yaml_value(ex_ident.get("name_variants")
                          or [name, f"{surname}, {name.split()[0]}", f"{name[0]}. {surname}"])
    typos = yaml_value(ex_ident.get("name_typos") or [])
    f_email = field(ex_ident, 'email', 'null                    # CONFIRM')
    f_job_title = field(ex_ident, 'job_title', 'null                # CONFIRM')
    f_affiliations = field(ex_ident, 'affiliations', '[]               # CONFIRM')
    f_education = field(ex_ident, 'education', '[]                  # CONFIRM')
    f_google_scholar = field(ex_id, 'google_scholar', 'null           # CONFIRM: the ?user= value on your Scholar profile URL')
    f_huggingface = field(ex_id, 'huggingface', 'null              # CONFIRM')
    f_linkedin = field(ex_id, 'linkedin', 'null                 # CONFIRM')
    f_openreview = field(ex_id, 'openreview', 'null               # CONFIRM: the ~Name_Surname1 form on openreview.net')
    f_bluesky = field(ex_id, 'bluesky', 'null                  # CONFIRM')
    f_wikidata = field(ex_id, 'wikidata',
                       "null                 # created later by scripts/wikidata_apply.py")
    f_twitter = field(ex_id, 'twitter', 'null                  # CONFIRM')
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
  name_variants:{variants}
  # CONFIRM, and leave empty unless sure. A string here is published to Wikidata as a
  # search alias, so it earns its place only if it already appears in a printed citation
  # or is a standard alternative transliteration of the same name, and it resolves to
  # nobody else. A surname-only or initials-only form always belongs to somebody --
  # never list one.
  name_typos:{typos}
  {orc_line}
  canonical_url: {homepage or 'null                 # CONFIRM: the one URL that goes everywhere'}
  other_pages: []
  # CONFIRM: cut this to what the work is actually about, heaviest first, and rewrite the
  # phrasing. These are the two-word phrases the titles repeat more than once -- evidence
  # of subject matter, not keywords. A keyword is something a person types into a search
  # box; several of these will not be.
  keywords: []
{chr(10).join('  #   - ' + k for k in kw)}
  {f_email}
  image: null                    # CONFIRM: a photo self-hosted under static/, not a CDN path
  {f_job_title}
  {f_affiliations}
  {f_education}

ids:{split}  semantic_scholar: {json.dumps(ids)}
  semantic_scholar_primary: {json.dumps(str(ids[0])) if ids else 'null   # CONFIRM'}
  # Filled by the first `python scripts/audit_identity.py`, which reconciles OpenAlex
  # against the papers the collector found. Guessing them here would pin the wrong record.
  openalex: []
  openalex_duplicates: []
  {f_google_scholar}
  dblp: {found['dblp_name'] or 'null                     # CONFIRM'}
  dblp_pid: {found['dblp_pid'] or 'null                 # CONFIRM'}
  github: {github or 'null                   # CONFIRM'}
  {f_huggingface}
  {f_wikidata}
  {f_linkedin}
  {f_openreview}
  {f_bluesky}
  mastodon: null                 # CONFIRM
  {f_twitter}
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


def dry_run(bundle: str, name: str) -> str | None:
    """Run the whole pipeline against their ids in a scratch tree; keep its worklist.

    The bundle otherwise says what paper-geo *would* find. This shows what it does find, so
    they open one file and read their own gap list -- which arXiv submissions have no
    journal-ref, which Hugging Face paper pages are unclaimed -- before deciding whether this
    is worth their afternoon.

    Everything happens under `build/`, gitignored and disposable. `bootstrap_fork` empties the
    previous author's judgement out of the copy first, so nothing can leak one person's
    decisions into another person's worklist.
    """
    import shutil
    import subprocess
    import yaml
    scratch = os.path.join(ROOT, "build", "handover-" + os.path.basename(bundle))
    shutil.rmtree(scratch, ignore_errors=True)
    shutil.copytree(ROOT, scratch, ignore=shutil.ignore_patterns(
        ".git", "build", "handover", "__pycache__", ".venv", "*.pyc"))

    def step(argv, label):
        r = subprocess.call(argv, cwd=scratch)
        if r != 0:
            print(f"  dry run stopped at {label} (exit {r}); {scratch} left in place",
                  file=sys.stderr)
        return r == 0

    if not step([sys.executable, "scripts/bootstrap_fork.py", "--yes"], "bootstrap"):
        return None
    cfg_path = os.path.join(scratch, "config.yaml")
    cfg = yaml.safe_load(open(cfg_path))
    for k, v in (yaml.safe_load(open(os.path.join(bundle, "config.yaml"))) or {}).items():
        cfg.setdefault(k, {}).update(v) if isinstance(v, dict) else cfg.__setitem__(k, v)
    # Not a real handle, and the collaboration step only uses it to tell their repos from
    # everyone else's. A leftover value here would mine the wrong person's GitHub.
    cfg["collaboration"]["me"] = cfg["ids"].get("github") or "unknown"
    cfg["sources"]["publications_path"] = None
    yaml.safe_dump(cfg, open(cfg_path, "w"), sort_keys=False, allow_unicode=True)

    if not step([sys.executable, "update.py"], "update"):
        return None
    src = os.path.join(scratch, "WORKLIST.md")
    if not os.path.exists(src):
        return None
    dst = os.path.join(bundle, "WORKLIST-preview.md")
    head = (f"<!-- Generated by `python scripts/handover.py \"{name}\" --dry-run`. A "
            f"preview: what one\n     `python update.py` finds for {name} from public "
            f"records alone, with none of\n     the CONFIRM values in config.yaml filled "
            f"in yet. Every count here is a floor. -->\n\n")
    open(dst, "w").write(head + open(src).read())
    return dst


def message_text(name: str, found: dict) -> str:
    """The note to actually send them, so the bundle is not a directory with no covering letter.

    Generated for the same reason as everything else here: the counts in it are the
    lookup's, so the message cannot claim a corpus size the bundle does not contain, and
    re-running after a new paper appears updates the note along with the config.
    """
    first = (name.split() or [name])[0]
    recs = found["semantic_scholar"]
    # Wrapped here rather than in the template: the counts are interpolated, so the line
    # lengths are not known until they are filled in, and a mail body with one 300-column
    # paragraph in the middle reads as machine-written -- which is the one thing this note
    # cannot afford to look like.
    split = (" records, and the tooling merges the two rather than asking you to pick one"
             if len(recs) == 2 else
             f" records, which the tooling merges rather than asking you to pick one"
             if len(recs) > 2 else " record")
    looked_up = textwrap.fill(
        f"Everything specific to you is already looked up -- "
        f"{found['paper_count']} papers across {len(recs)} Semantic Scholar{split}, "
        f"your DBLP pid, your ORCID. What it deliberately did not do is decide "
        f"anything: every value only you can answer is left blank and marked CONFIRM.",
        width=88)
    return f"""\
Subject: a re-runnable GEO/SEO setup for your papers, if you want it

Hi {first},

I built a thing for my own papers and it generalises, so here is a starter bundle set up
for yours. The short version: it re-derives your bibliography from public records on every
run, builds a small site where each paper has a page carrying structured data an answer
engine can read, and then hands you a worklist of only the gaps no code can close.

{looked_up}

  https://github.com/borgr/paper-geo/tree/main/handover/{slugify(name)}

Start with README.md in that folder; it is four commands, in order. The one to read twice
is `python scripts/bootstrap_fork.py --yes`, which empties my judgement out of the fork --
inheriting my decision files would publish my decisions, including decisions not to
publish something, under your name.

It touches no account of yours. Fetching and building are automatic; every outward write
(deploy the site, edit Wikidata, accept an AI-drafted description) is a separate command
you run on purpose. The single judgement call is which GitHub Pages repo the site deploys
to, left blank because deploying over a repo that already serves your homepage replaces
that homepage.

Happy to run the first pass with you if that is easier than reading a README.

Leshem
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
    ap.add_argument("--dry-run", action="store_true",
                    help="also run the whole pipeline against their ids in a scratch "
                         "tree under build/, and keep its worklist as WORKLIST-preview.md")
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
    extra = facts(d)
    with open(os.path.join(d, "config.yaml"), "w") as f:
        f.write(config_text(args.name, found, args.github, args.homepage, extra))
    with open(os.path.join(d, "README.md"), "w") as f:
        f.write(readme_text(args.name, found))
    with open(os.path.join(d, "MESSAGE.md"), "w") as f:
        f.write(message_text(args.name, found))
    write_json(os.path.join(d, "records.json"), found, indent=1)
    print(f"wrote {os.path.relpath(d, ROOT)}/ -- config.yaml, README.md, "
          f"MESSAGE.md, records.json")
    todo = sum(1 for line in open(os.path.join(d, "config.yaml")) if "CONFIRM" in line)
    print(f"  {len(recs)} S2 record(s), {found['arxiv_count']} arXiv papers, "
          f"{todo} value(s) left for them to confirm")
    if extra:
        print(f"  merged {os.path.relpath(d, ROOT)}/facts.yaml over the lookup")
    if args.dry_run:
        preview = dry_run(d, args.name)
        if preview:
            n = sum(1 for line in open(preview) if line.startswith("- [ ]"))
            print(f"  wrote {os.path.relpath(preview, ROOT)}: {n} open item(s) the "
                  f"pipeline already found for them")


if __name__ == "__main__":
    main()
