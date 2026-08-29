#!/usr/bin/env python3
"""Build data/papers.yaml: one record per paper, merged from every source.

Sources, in precedence order for any conflicting field:
  1. orig.bib         the author's curated bibliography -- venue truth
  2. Semantic Scholar abstracts, citation counts, cross-ids
  3. arXiv API        journal-ref / DOI presence
  4. Hugging Face     paper-page existence and authorship claims

Everything downstream -- site, CITATION.cff, worklist, Wikidata -- reads only this
file, so a source outage costs one field rather than the whole pipeline.

Usage:
    python scripts/collect.py [--offline] [--no-arxiv] [--no-hf]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (ARXIV_NS, BUILD, DATA, ROOT, arxiv_id,  # noqa: E402
                    authors_truncated, clean_bibtex, clean_latex, get, get_json,
                    get_status, is_preprint_venue, load_config, name_match, norm_title,
                    parse_bibtex, read_yaml, short_venue, slugify, split_authors,
                    write_json, write_yaml)
# The only OpenReview reader in the repo. Imported rather than reimplemented because the
# filters are the load-bearing part -- a strict title match, an author list, and a venue
# that is not a withdrawn or still-under-review submission -- and a second copy of them
# here would be a second set of rules for admitting a paper to the corpus.
from scholar_check import from_openreview  # noqa: E402



_ARXIV_DOI = re.compile(r"^10\.48550/arxiv\.(\d{4}\.\d{4,5})", re.I)


def unfold_arxiv_dois(papers: list[dict]) -> int:
    """`10.48550/arXiv.2510.24081` in a `doi` field *is* an arXiv id. Store it as one.

    Sets `arxiv` from the DataCite form where it is empty, so dedupe can match on the id
    instead of falling back to titles, and returns how many were unfolded. `doi` is left
    as the source gave it; a publisher DOI never matches.
    """
    n = 0
    for p in papers:
        if p.get("arxiv"):
            continue
        m = _ARXIV_DOI.match(str(p.get("doi") or ""))
        if m:
            p["arxiv"] = m.group(1)
            n += 1
    return n


SLUG_HISTORY = os.path.join(DATA, "slug_history.yaml")


def _slug_identity(p: dict) -> str | None:
    """A key for "the same paper" that survives the title changing.

    `arxiv:<id>`, folding the DataCite DOI form into it, else `doi:` or `key:`, else None
    for a paper with no stable identifier -- which is then not paired at all rather than
    paired by title.
    """
    if p.get("arxiv"):
        return f"arxiv:{p['arxiv']}"
    m = _ARXIV_DOI.match(str(p.get("doi") or ""))
    if m:
        return f"arxiv:{m.group(1)}"
    for f in ("doi", "key"):
        if p.get(f):
            return f"{f}:{p[f]}"
    return None


COVERAGE = {
    "papers": lambda p: True,
    "with an arXiv id": lambda p: p.get("arxiv"),
    "with an abstract": lambda p: p.get("abstract"),
    "with verbatim bibtex": lambda p: p.get("bibtex"),
    "with authors": lambda p: p.get("authors"),
    "with a venue": lambda p: p.get("venue"),
}
# How far each may fall before the run is treated as damage rather than a change. Not
# zero: merging two records into one is a *good* shrink, and it takes a paper off every
# count at once. Ten is above any plausible run of real merges and far below what a
# failed source costs -- Semantic Scholar alone supplies most of the abstracts.
SHRINK_TOLERANCE = 10


def coverage_alarms(prev: list[dict], papers: list[dict]) -> tuple[list[str], list[str]]:
    """This run's per-field coverage against the last committed one. (report, alarms)

    `report` is a line per field that moved; `alarms` is a line per field that fell by
    more than SHRINK_TOLERANCE, which stops the run before it overwrites papers.yaml
    (`--allow-shrink` overrides). A dead source returns empty rather than raising, so
    without this a bad afternoon at one API looks exactly like success.
    """
    report, alarms = [], []
    for label, pred in COVERAGE.items():
        was, now = sum(1 for p in prev if pred(p)), sum(1 for p in papers if pred(p))
        if was != now:
            report.append(f"    {label}: {was} -> {now} ({now - was:+d})")
        if was - now > SHRINK_TOLERANCE:
            alarms.append(f"{label} fell {was - now} ({was} -> {now})")
    return report, alarms


def _committed_papers(papers_path: str) -> list[dict]:
    """The papers list from the last committed papers.yaml -- "what is published".

    Not the working copy: a rerun that is never committed publishes nothing, and two
    local runs in a row would make the second's baseline the first's output, forgetting
    the slug that is actually live. Falls back to the working copy when git is
    unavailable or the file is not committed yet.
    """
    try:
        out = subprocess.run(["git", "show", f"HEAD:{os.path.relpath(papers_path, ROOT)}"],
                             cwd=ROOT, capture_output=True, text=True, timeout=30)
        if out.returncode == 0 and out.stdout.strip():
            return (yaml.safe_load(out.stdout) or {}).get("papers") or []
    except (OSError, subprocess.SubprocessError, yaml.YAMLError):
        pass
    return (read_yaml(papers_path) or {}).get("papers") or []


CARRIED = ("owner", "owner_source", "canonical_page", "owner_conflict")


def carry_claims(papers: list[dict], papers_path: str) -> int:
    """Keep the ownership fields this file does not derive, across the rewrite.

    Copies the CARRIED keys from the working copy of papers.yaml onto records that lack
    them, and returns how many papers gained one. `ownership.py` re-derives them, but it
    recovers our own claim by reading the value already there -- so dropping them resets
    the paper to `unclaimed` and loses the co-author page `render` links to instead of
    publishing a competing one.

    Presence of the key is the test, not its truth: `owner: null` is `unclaimed`.
    """
    prev = {p["slug"]: p for p in (read_yaml(papers_path) or {}).get("papers") or []
            if p.get("slug")}
    n = 0
    for p in papers:
        was = prev.get(p.get("slug"))
        if not was:
            continue
        got = [k for k in CARRIED if k in was and k not in p]
        for k in got:
            p[k] = was[k]
        n += bool(got)
    return n


def record_slug_moves(papers: list[dict], papers_path: str) -> int:
    """Remember every URL this run retires, so build_site.py can redirect it.

    Compares the committed papers.yaml with this run by identifier and appends old -> new
    to data/slug_history.yaml for each slug that moved and is not still live, re-pointing
    chains so two renames land on a live page. Returns the number of moves.

    papers.yaml is regenerated wholesale, so the old slug is the one fact that cannot be
    recomputed from the sources -- and a published URL that stops being generated is a 404
    on the next deploy.
    """
    prev = _committed_papers(papers_path)
    if not prev:                      # first run, or no committed copy to compare to
        return 0
    now = {i: p["slug"] for p in papers if (i := _slug_identity(p))}
    hist = read_yaml(SLUG_HISTORY) or {}
    retired = dict(hist.get("retired") or {})
    live = set(now.values())
    moves = 0
    for p in prev:
        i = _slug_identity(p)
        old, new = p.get("slug"), now.get(i) if i else None
        if not (i and old and new) or old == new or old in live:
            continue
        retired[old] = new
        moves += 1
    # Re-point chains: anything that used to land on `old` now lands where `old` went.
    for src, dst in list(retired.items()):
        seen = {src}
        while dst in retired and dst not in seen:
            seen.add(dst)
            dst = retired[dst]
        retired[src] = dst
    retired = {k: v for k, v in retired.items() if k not in live and k != v}
    if retired != (hist.get("retired") or {}):
        write_yaml(SLUG_HISTORY, {
            "_comment": "Retired paper URLs -> the slug that replaced them. Written by "
                        "scripts/collect.py, read by scripts/build_site.py, which turns "
                        "each into a redirect stub. Append-only: deleting a line 404s a "
                        "URL that is already published and indexed. A null target means "
                        "the opposite on purpose -- the page was dropped and no successor "
                        "is honest, so the URL is meant to 404; write it as null rather "
                        "than removing the line, so a deliberate removal cannot be "
                        "mistaken for a redirect that broke.",
            "retired": dict(sorted(retired.items())),
        })
    return moves


# The last bibliography that was successfully read. Derived, so it lives in build/ and
# a clean clone simply has no fallback until its first good run.
BIB_CACHE = os.path.join(BUILD, "bibliography.bib")


def bibtex_source(cfg) -> tuple[str, str]:
    """The bibliography text, from the local checkout if there is one.

    `--refresh-bib` runs the publications pipeline, which rewrites its bib *on
    disk*. Reading over HTTP afterwards returned the last pushed copy instead --
    so a refresh appeared to do nothing, and the one case the flag exists for was
    the one case it did not serve. Prefer the working tree, fall back to HTTP.
    """
    url = cfg["sources"]["bibtex_url"]
    if not url:
        # A fork whose author keeps no .bib is the ordinary case, not an error: merge_s2
        # appends every paper on the S2 author record, so the corpus arrives anyway.
        return "", ""
    path = cfg["sources"].get("publications_path")
    if path:
        local = os.path.join(os.path.expanduser(path), os.path.basename(url))
        if os.path.isfile(local):
            with open(local, encoding="utf-8", errors="replace") as f:
                return f.read(), local
    raw = get(url).decode("utf-8", "replace")
    if raw:
        try:
            os.makedirs(BUILD, exist_ok=True)
            with open(BIB_CACHE, "w") as f:
                f.write(raw)
        except OSError:
            pass
        return raw, url
    # The one step whose failure used to end the run. Every other step degrades, and
    # this one had the least excuse not to: the corpus is a hundred-odd stable records
    # read over the network on every run, so a dropped connection took out repos,
    # drafting, the audit, the site and the worklist -- none of which needed the
    # network at all -- and left the reader with an error instead of a run.
    if os.path.isfile(BIB_CACHE):
        with open(BIB_CACHE, encoding="utf-8", errors="replace") as f:
            return f.read(), BIB_CACHE
    return "", url


def from_bibtex(cfg) -> list[dict]:
    raw, origin = bibtex_source(cfg)
    if not raw and not origin:
        print("  no sources.bibtex_url -- seeding the corpus from the Semantic Scholar "
              "author record instead", file=sys.stderr)
        return []
    if not raw:
        sys.exit(f"could not read bibliography from {origin}, and no cached copy in "
                 f"{os.path.relpath(BIB_CACHE, ROOT)}. Nothing downstream can run "
                 f"without the corpus, so this is the one failure that stops a run.")
    if origin == BIB_CACHE:
        print(f"  bibliography: {cfg['sources']['bibtex_url']} did not answer -- using "
              f"the copy from the last run. Anything added since is missing here.")
    print(f"  bibliography: {origin}")
    papers = []
    for e in parse_bibtex(raw):
        title = e.get("title")
        if not title:
            continue
        venue = e.get("booktitle") or e.get("journal") or e.get("publisher")
        papers.append({
            "key": e["key"],
            "slug": slugify(title),
            "title": title,
            "authors": split_authors(e.get("author")),
            "authors_truncated": authors_truncated(e.get("author")) or None,
            "year": int(e["year"]) if (e.get("year") or "").isdigit() else None,
            "venue": venue,
            "type": e["type"],
            "doi": e.get("doi"),
            "arxiv": arxiv_id(e),
            "url": e.get("url"),
            "abstract": e.get("abstract"),
            # Verbatim, not regenerated -- the citation we publish must be the
            # one people already cite. Feeds the page's cite block and CITATION.cff.
            "bibtex": e.get("raw"),
            "_norm": norm_title(title),
        })
    return papers


def from_arxiv_ids(papers: list[dict], ids: list[str]) -> int:
    """Add papers by bare arXiv id, from `overrides.extra_arxiv`. Returns how many.

    A stopgap for the interval before the bibliography carries the entry, so the paper has
    a page, a canonical URL and a sitemap entry meanwhile. The record is fetched, never
    typed. Ids the bibliography has caught up with are reported, so the list gets emptied
    rather than accumulated -- `arxiv_stray` in build/identity_state.json is where its
    candidates come from.
    """
    have = {p["arxiv"] for p in papers if p.get("arxiv")}
    # An id the bibliography now carries is the good outcome -- it is what this list is
    # waiting for -- but skipping it silently is how a stopgap becomes permanent. Said
    # once, here, because this is the only code that can tell.
    for i in ids:
        if str(i).strip() in have:
            print(f"  overrides.extra_arxiv: the bibliography has {i} now -- delete "
                  f"that line", file=sys.stderr)
    # str(): an unquoted `2604.12843` in YAML is a float, and a float here would both
    # fail to join and, worse, silently drop a trailing zero from the id.
    want = [s for i in ids if (s := str(i).strip()) and s not in have]
    if not want:
        return 0
    raw = get(f"http://export.arxiv.org/api/query?id_list={','.join(want)}"
              f"&max_results={len(want)}")
    if not raw:
        print("  ! arXiv unavailable; extra_arxiv ids skipped this run", file=sys.stderr)
        return 0
    n = 0
    for e in ET.fromstring(raw).findall("a:entry", ARXIV_NS):
        tail = e.find("a:id", ARXIV_NS).text.split("/abs/")[-1]
        ax = tail.rsplit("v", 1)[0] if "v" in tail.split("/")[-1] else tail
        title = " ".join((e.find("a:title", ARXIV_NS).text or "").split())
        if not title:
            continue
        summ = e.find("a:summary", ARXIV_NS)
        pub = e.find("a:published", ARXIV_NS)
        jr = e.find("ar:journal_ref", ARXIV_NS)
        papers.append({
            "key": f"arxiv{ax.replace('.', '')}",
            "slug": slugify(title),
            "title": title,
            "authors": [a.find("a:name", ARXIV_NS).text
                        for a in e.findall("a:author", ARXIV_NS)],
            "year": int(pub.text[:4]) if pub is not None else None,
            "venue": jr.text.strip() if jr is not None else None,
            "type": "misc",
            "doi": None,
            "arxiv": ax,
            "url": f"https://arxiv.org/abs/{ax}",
            "abstract": " ".join((summ.text or "").split()) if summ is not None else None,
            # No `bibtex` key: a BibTeX entry we generate would compete with the one
            # the bibliography will publish later, and two citation keys for one paper
            # is the split this whole project exists to avoid. The page renders its
            # cite block from the fields instead.
            "bibtex": None,
            "_override": "extra_arxiv",
            "_norm": norm_title(title),
        })
        n += 1
    missing = set(want) - {p.get("arxiv") for p in papers}
    if missing:
        print(f"  ! extra_arxiv ids arXiv did not return: {', '.join(sorted(missing))}",
              file=sys.stderr)
    return n


def from_openreview_titles(papers: list[dict], titles: list[str]) -> int:
    """Add papers by title from OpenReview, from `overrides.extra_openreview`.

    `extra_arxiv`'s sibling for papers with no identifier to key on: a workshop paper is
    often neither preprinted nor given a DOI. Keyed by title because OpenReview's `notes`
    endpoint needs a token while `notes/search` answers anyone; `from_openreview` matches
    strictly and refuses a withdrawn or under-review submission. Returns how many were
    added, and reports titles the bibliography now has.
    """
    have = {p["_norm"] for p in papers if p.get("_norm")}
    n = 0
    for t in titles:
        t = str(t).strip()
        if not t:
            continue
        if norm_title(t) in have:
            print(f"  overrides.extra_openreview: the bibliography has "
                  f"{t[:52]!r} now -- delete that line", file=sys.stderr)
            continue
        rec, _, answered = from_openreview(t)
        if not rec:
            print(f"  ! extra_openreview: OpenReview "
                  f"{'has no accepted paper titled' if answered else 'did not answer for'}"
                  f" {t[:52]!r}", file=sys.stderr)
            continue
        papers.append({
            "key": f"openreview{rec['openreview']}",
            "slug": slugify(rec["title"]),
            "title": rec["title"],
            "authors": rec["authors"],
            "year": int(rec["year"]) if (rec.get("year") or "").isdigit() else None,
            "venue": rec["venue"],
            "type": rec["type"],
            "doi": None,
            "arxiv": None,
            "url": rec["url"],
            "abstract": rec.get("abstract"),
            # No `bibtex`, for the reason `from_arxiv_ids` gives: a key we invent would
            # compete with the one the bibliography publishes later, and two citation
            # keys for one paper is the split this project exists to avoid.
            "bibtex": None,
            "_override": "extra_openreview",
            "_norm": norm_title(rec["title"]),
        })
        n += 1
    return n


def build_links(papers: list[dict]) -> None:
    """Resolve every surface a paper has into one `links` map, in place.

    Derived from the identifiers on every run, so they cannot drift. This is what the
    page's JSON-LD `sameAs` consumes -- the difference between five unrelated URLs and one
    work with five locations. `links_extra` in the sidecar is for what cannot be derived:
    project page, talk video, slides, poster, leaderboard.
    """
    for p in papers:
        L: dict[str, str] = {}
        ax = p.get("arxiv")
        if ax:
            L["arxiv"] = f"https://arxiv.org/abs/{ax}"
            L["arxiv_pdf"] = f"https://arxiv.org/pdf/{ax}"
            # Post-2023 submissions get a LaTeXML HTML rendering; ar5iv covers the
            # rest. Either way every paper ends up with a crawlable HTML surface,
            # which a PDF-only paper does not have.
            L["html"] = (f"https://arxiv.org/html/{ax}" if p.get("arxiv_html")
                         else f"https://ar5iv.labs.arxiv.org/html/{ax}")
            L["html_source"] = "arxiv" if p.get("arxiv_html") else "ar5iv"
            L["huggingface"] = f"https://huggingface.co/papers/{ax}"
            L["alphaxiv"] = f"https://www.alphaxiv.org/abs/{ax}"
        if p.get("doi"):
            L["doi"] = f"https://doi.org/{p['doi']}"
        if p.get("acl"):
            L["acl_anthology"] = f"https://aclanthology.org/{p['acl']}/"
        if p.get("s2_corpus_id"):
            L["semantic_scholar"] = f"https://www.semanticscholar.org/paper/{p['s2_corpus_id']}"
        if p.get("url") and p["url"] not in L.values():
            L["publisher"] = p["url"]
        if p.get("hf_github_repo"):
            L["code"] = p["hf_github_repo"]
        p["links"] = L


def add_deduced_links(papers: list[dict]) -> None:
    """Fill `links.code` and `links.project` from data/paper_code.yaml where still empty.

    Accepted rows only, and never over a value Hugging Face already gave -- that is the
    one a reader can also see on the paper page. Lets a repo pushed today reach the site
    without waiting for an online collect.
    """
    by_slug = (read_yaml(os.path.join(DATA, "paper_code.yaml")) or {}).get("papers") or {}
    for p in papers:
        r = by_slug.get(p.get("slug")) or {}
        L = p.setdefault("links", {})
        if r.get("verdict") == "accept" and r.get("repo") and not L.get("code"):
            L["code"] = r["repo"]
        if r.get("page_verdict") == "accept" and r.get("project_page"):
            L.setdefault("project", r["project_page"])


def merge_s2(papers: list[dict], cfg) -> None:
    by_norm = {p["_norm"]: p for p in papers}
    for aid in cfg["ids"]["semantic_scholar"]:
        url = (f"https://api.semanticscholar.org/graph/v1/author/{aid}/papers"
               "?fields=title,year,externalIds,citationCount,venue,abstract,"
               "authors,openAccessPdf&limit=500")
        d = get_json(url)
        if not d:
            print(f"  ! S2 author {aid} unavailable", file=sys.stderr)
            continue
        for sp in d.get("data", []):
            n = norm_title(sp.get("title"))
            p = by_norm.get(n)
            if p is None:                      # in S2 but not in the curated bib
                p = {"key": None, "slug": slugify(sp.get("title") or ""),
                     "title": sp.get("title"), "authors": [], "year": sp.get("year"),
                     "venue": sp.get("venue"), "type": None, "doi": None,
                     "arxiv": None, "url": None, "abstract": None, "_norm": n,
                     "only_in_s2": True}
                papers.append(p)
                by_norm[n] = p
            ext = sp.get("externalIds") or {}
            # A paper pulled onto the claimed page stays listed on the unclaimed one
            # too, so it arrives from both fetches. The claimed record wins whatever
            # order the ids are configured in -- otherwise every paper the author
            # merges reads as still-split and the worklist asks for it again.
            if p.get("s2_author_record") != cfg["ids"]["semantic_scholar_primary"]:
                p["s2_author_record"] = aid
            p["citations"] = sp.get("citationCount")
            p.setdefault("acl", ext.get("ACL"))
            p["arxiv"] = p.get("arxiv") or ext.get("ArXiv")
            p["doi"] = p.get("doi") or ext.get("DOI")
            p["abstract"] = p.get("abstract") or sp.get("abstract")
            p["s2_corpus_id"] = ext.get("CorpusId")
            # S2-only records arrive with no authors from the bibliography, which
            # leaves them without the three highwire tags Scholar requires.
            if not p.get("authors"):
                p["authors"] = [a["name"] for a in (sp.get("authors") or [])
                                if a.get("name")]
        time.sleep(2)


def merge_arxiv(papers: list[dict]) -> None:
    """Flag which arXiv records are missing journal-ref / DOI / HTML."""
    ids = sorted({p["arxiv"] for p in papers if p.get("arxiv")})
    meta = {}
    for i in range(0, len(ids), 40):
        chunk = ids[i:i + 40]
        raw = get(f"http://export.arxiv.org/api/query?id_list={','.join(chunk)}"
                  f"&max_results={len(chunk)}")
        if not raw:
            print(f"  ! arXiv batch {i} unavailable", file=sys.stderr)
            continue
        for e in ET.fromstring(raw).findall("a:entry", ARXIV_NS):
            tail = e.find("a:id", ARXIV_NS).text.split("/abs/")[-1]
            base = tail.rsplit("v", 1)[0] if "v" in tail.split("/")[-1] else tail
            jr = e.find("ar:journal_ref", ARXIV_NS)
            doi = e.find("ar:doi", ARXIV_NS)
            com = e.find("ar:comment", ARXIV_NS)
            ti = e.find("a:title", ARXIV_NS)
            meta[base] = {
                "arxiv_journal_ref": jr.text.strip() if jr is not None else None,
                "arxiv_doi": doi.text.strip() if doi is not None else None,
                "arxiv_comment": " ".join((com.text or "").split()) if com is not None else None,
                # Compared against ours, then discarded -- see `title_diffs`.
                "_arxiv_title": " ".join((ti.text or "").split()) if ti is not None else None,
            }
        time.sleep(3)
    for p in papers:
        if p.get("arxiv"):
            p.update(meta.get(p["arxiv"], {}))
            # HTML exists for LaTeX submissions from late 2023 on, and arXiv is backfilling
            # older ones -- so False means "not yet", not "never". There is no author-facing way
            # to request it; ar5iv covers the gap meanwhile.
            #
            # Asked only while the answer can still change: `True` is kept without re-asking,
            # `False` and missing are re-probed every run because backfill lands. That is the
            # difference between 321 requests a run and the few dozen still open.
            #
            # Written only when arXiv answered. `False` sends `links.html` to ar5iv and
            # counts the paper as missing HTML, and papers.yaml holds only what a source
            # actually asserted -- a refused probe asserts nothing.
            if not p.get("arxiv_html"):
                st, _ = get_status(f"https://arxiv.org/html/{p['arxiv']}", retries=3)
                if st == 200 or st in (404, 410):
                    p["arxiv_html"] = st == 200
            # Note: the arXiv DataCite DOI (10.48550/arXiv.<id>) is deliberately NOT
            # written here. Storing it would let it shadow a publisher DOI that shows
            # up later, and it is derivable from the id anyway -- so it is computed at
            # the point of use by common.paper_doi(). papers.yaml holds only what a
            # source actually asserted.


def merge_hf(papers: list[dict], cfg) -> None:
    """HF paper pages carry claim state AND the paper->repo/model/dataset links.

    `hf_indexed: False` is written only on a 404, which is Hugging Face saying it has no
    page for that arXiv id. Any other non-answer leaves whatever the last run learned in
    place: the flag lives in `data/papers.yaml` and the worklist turns a False into "visit
    this page", so a run during an outage would ask for every page in the corpus.
    """
    me = cfg["ids"]["huggingface"]
    for p in papers:
        if not p.get("arxiv"):
            continue
        st, raw = get_status(f"https://huggingface.co/api/papers/{p['arxiv']}", retries=1,
                             accept="application/json")
        try:
            d = json.loads(raw) if st == 200 and raw else None
        except ValueError:
            d = None
        if d is None:
            if st in (404, 410):
                p["hf_indexed"] = False
        else:
            authors = d.get("authors", [])
            users = {(a.get("user") or {}).get("user") for a in authors}
            p["hf_indexed"] = True
            p["hf_upvotes"] = d.get("upvotes", 0)
            p["hf_claimed_authors"] = sum(1 for a in authors if a.get("user"))
            # The actionable bit is whether *you* claimed it, not how many did.
            p["hf_claimed_by_me"] = me in users
            p["hf_github_repo"] = d.get("githubRepo")
            p["hf_github_stars"] = d.get("githubStars")
            p["hf_n_models"] = d.get("numTotalModels")
            p["hf_n_datasets"] = d.get("numTotalDatasets")
        time.sleep(0.2)


def backfill_abstracts(papers: list[dict]) -> None:
    """A record with no abstract is near-unretrievable in embedding search, and
    Scholar requires a visible abstract on the landing page. arXiv has them."""
    need = sorted({p["arxiv"] for p in papers
                   if p.get("arxiv") and not p.get("abstract")})
    if not need:
        return
    got = {}
    for i in range(0, len(need), 40):
        chunk = need[i:i + 40]
        raw = get(f"http://export.arxiv.org/api/query?id_list={','.join(chunk)}"
                  f"&max_results={len(chunk)}")
        if not raw:
            print(f"  ! arXiv batch {i} unavailable; {len(chunk)} abstract(s) still "
                  f"missing", file=sys.stderr)
            continue
        for e in ET.fromstring(raw).findall("a:entry", ARXIV_NS):
            tail = e.find("a:id", ARXIV_NS).text.split("/abs/")[-1]
            base = tail.rsplit("v", 1)[0] if "v" in tail.split("/")[-1] else tail
            summ = e.find("a:summary", ARXIV_NS)
            if summ is not None and summ.text:
                got[base] = " ".join(summ.text.split())
        time.sleep(3)
    for p in papers:
        if p.get("arxiv") in got and not p.get("abstract"):
            p["abstract"] = got[p["arxiv"]]
            p["abstract_source"] = "arxiv"


def backfill_abstracts_offarxiv(papers: list[dict]) -> None:
    """Fetch abstracts for the papers arXiv has none of, in place.

    Runs after the arXiv pass and only where it left `abstract` empty, because arXiv is
    one batch request for forty papers and these are four APIs for one. Sources are in
    scripts/fulltext.py: Semantic Scholar, Europe PMC, Crossref JATS, OpenAlex. Sets
    `abstract_source` to whichever answered.
    """
    from fulltext import resolve_abstract
    for p in papers:
        if (p.get("abstract") or "").strip():
            continue
        got = resolve_abstract(p)
        if got:
            p["abstract"], p["abstract_source"] = got
            print(f"  abstract from {got[1]}: {p['slug']}", file=sys.stderr)


_ORDINALS = ("second", "third", "fourth", "fifth", "2nd", "3rd", "4th", "5th")


def _discriminators(title: str) -> tuple:
    """Tokens that must match before two similar titles may be merged.

    'BabyLM Turns 3' vs 'Turns 4' and 'BabyLM Challenge' vs 'Second BabyLM
    Challenge' are near-identical strings and completely different papers, so
    digits and ordinal words are treated as hard discriminators.
    """
    t = (title or "").lower()
    return (tuple(sorted(re.findall(r"\d+", t))),
            tuple(sorted(w for w in _ORDINALS if re.search(rf"\b{w}\b", t))))


def _is_preprint(p: dict) -> bool:
    v = (p.get("venue") or "").strip()
    return not v or is_preprint_venue(v)


def dedupe(papers: list[dict], prefer: list[str] | None = None) -> tuple[list[dict], int, int]:
    """Merge exact/near-exact duplicates; flag the uncertain band for review.

    Bibliographies routinely hold both the DBLP CoRR preprint entry and the
    published entry for one paper. Publishing two pages for one paper is exactly
    the duplicate-title failure Scholar's docs warn about, so they must be one
    record here. Merged records keep the published venue and the preprint's
    arXiv id and abstract.
    """
    import difflib

    want_title = {norm_title(t) for t in (prefer or [])}
    norms = [norm_title(p.get("title")) for p in papers]
    parent = list(range(len(papers)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    # Identifiers first, without consulting titles at all: one arXiv id is one paper,
    # however differently two sources spell it. A retitled preprint ("All Neural Networks
    # are Created Equal" -> "Let's Agree to Agree") shares 1905.10854 and scores nowhere
    # near the title threshold below, so the similarity pass cannot see the pair. This is
    # not a judgment call, which is why it runs before the band that needs one.
    for field in ("arxiv", "doi"):
        seen: dict[str, int] = {}
        for i, p in enumerate(papers):
            v = p.get(field)
            if not v:
                continue
            k = str(v).strip().lower()
            if k in seen:
                parent[find(i)] = find(seen[k])
            else:
                seen[k] = i

    flagged = 0
    for i in range(len(papers)):
        for j in range(i + 1, len(papers)):
            if find(i) == find(j):
                continue
            a, b = norms[i], norms[j]
            if not a or not b or abs(len(a) - len(b)) > 20:
                continue
            ratio = difflib.SequenceMatcher(None, a, b).ratio()
            if ratio < 0.90:
                continue
            same_ord = _discriminators(papers[i]["title"]) == _discriminators(papers[j]["title"])
            ids_agree = (papers[i].get("arxiv") and papers[i]["arxiv"] == papers[j].get("arxiv")) or \
                        (papers[i].get("doi") and papers[i]["doi"] == papers[j].get("doi"))
            if same_ord and (ratio >= 0.97 or ids_agree):
                parent[find(i)] = find(j)
            else:
                papers[i].setdefault("similar_but_distinct", []).append(papers[j]["title"])
                papers[j].setdefault("similar_but_distinct", []).append(papers[i]["title"])
                flagged += 1

    groups: dict[int, list[dict]] = {}
    for i, p in enumerate(papers):
        groups.setdefault(find(i), []).append(p)

    merged_out, n_merged = [], 0
    for members in groups.values():
        if len(members) == 1:
            merged_out.append(members[0])
            continue
        n_merged += len(members) - 1
        # Published entry wins for identity; preprint contributes arXiv + abstract.
        published = [m for m in members if not _is_preprint(m)]
        pool = published or members
        # A title named first in a force_merge group outranks venue length: that list
        # exists because the automatic choice was wrong, and the title decides both the
        # slug and every page heading.
        pick = [m for m in pool if norm_title(m.get("title")) in want_title]
        base = dict(max(pick or pool, key=lambda m: len(m.get("venue") or "")))
        for m in members:
            for k, v in m.items():
                if v in (None, "", [], {}):
                    continue
                if base.get(k) in (None, "", [], {}):
                    base[k] = v
                elif k == "citations":
                    base[k] = max(base[k] or 0, v or 0)
        base["merged_from"] = sorted({m["key"] for m in members if m.get("key")})
        merged_out.append(base)

    return merged_out, n_merged, flagged


def apply_overrides(papers: list[dict], ov: dict) -> list[dict]:
    """Apply data/overrides.yaml: force merges/splits, drops, field fixes.

    Runs after dedupe so it can override both what dedupe merged and what it
    refused to merge. Without this, every rerun would re-flag the same pairs and
    re-introduce the same known-bad records.
    """
    ov = ov or {}
    by_norm = {norm_title(p.get("title")): p for p in papers}

    # 1. force_merge: fold every listed alias into the first title in the group.
    dropped: set[int] = set()
    for group in ov.get("force_merge") or []:
        members = [by_norm.get(norm_title(t)) for t in group]
        # Two aliases can resolve to the SAME record, when dedupe already merged them or a
        # normalization fix folded their titles together. Without de-duplicating by identity
        # the record lands in `members[1:]` as well as being the base, so it is merged into
        # itself and dropped -- the paper vanishes because a human wrote down a correct merge.
        uniq: list[dict] = []
        for m in members:
            if m is not None and not any(m is u for u in uniq):
                uniq.append(m)
        members = uniq
        if len(members) < 2:
            continue
        base = members[0]
        for m in members[1:]:
            for k, v in m.items():
                if v in (None, "", [], {}):
                    continue
                if base.get(k) in (None, "", [], {}):
                    base[k] = v
                elif k == "citations":
                    base[k] = max(base[k] or 0, v or 0)
            dropped.add(id(m))
        base["merged_from"] = sorted(set(base.get("merged_from") or [])
                                     | {m["key"] for m in members if m.get("key")})
        base["merged_by_override"] = True

    # 2. force_distinct: suppress the flag for pairs a human confirmed differ.
    confirmed = {tuple(sorted(norm_title(t) for t in pair))
                 for pair in (ov.get("force_distinct") or [])}
    for p in papers:
        keep = []
        for other in p.get("similar_but_distinct") or []:
            pair = tuple(sorted([norm_title(p.get("title")), norm_title(other)]))
            if pair not in confirmed:
                keep.append(other)
        if p.get("similar_but_distinct"):
            if keep:
                p["similar_but_distinct"] = keep
            else:
                p.pop("similar_but_distinct")

    # 3. drop: known metadata damage.
    drop_norm = {norm_title(t) for t in (ov.get("drop") or [])}
    out = [p for p in papers
           if id(p) not in dropped and norm_title(p.get("title")) not in drop_norm]

    # 4. Clear review flags that point at titles no longer present as separate
    #    records -- a force_merge resolves the flag, so leaving it would keep the
    #    same pair in the review queue on every future run.
    live = {norm_title(p.get("title")) for p in out}
    for p in out:
        keep = [t for t in (p.get("similar_but_distinct") or [])
                if norm_title(t) in live]
        if p.get("similar_but_distinct"):
            if keep:
                p["similar_but_distinct"] = keep
            else:
                p.pop("similar_but_distinct")

    # 5. fields: per-slug hand corrections, applied last.
    fields = ov.get("fields") or {}
    for p in out:
        for k, v in (fields.get(p.get("slug")) or {}).items():
            p[k] = v
            # Sorted set, not append: on the `--offline` path the record already carries
            # the list from the previous run, and appending would grow it every rerun.
            p["overridden_fields"] = sorted(set(p.get("overridden_fields") or []) | {k})
        # An override only reaches what is derived after this point. `venue_display` and
        # `title_display` are, so they pick the correction up; `links` is built with the record,
        # long before this runs, so an overridden `url` silently did nothing. Re-derive that one
        # link here, on the same condition the original build uses.
        if "url" in (p.get("overridden_fields") or []) and p.get("url"):
            L = p.setdefault("links", {})
            if p["url"] not in L.values():
                L["publisher"] = p["url"]
    return out


# An "author" that is really an organisation. A consortium paper deposited under
# "MINDGAMES Organizer & Participation Teams" is a complete one-entry author list as
# far as any parser can tell, so nothing marks it truncated -- and a 53-author paper
# then fails the name gate with no signal that the list was never a list of people.
# That is the one shape where a paper of yours is silently dropped, so it is named.
CORPORATE_AUTHOR = re.compile(
    r"\b(teams?|organi[sz]ers?|organi[sz]ing|consortium|collaborations?|committee|"
    r"participants?|participation|working group|workshop|challenge|shared task|"
    r"community|initiative|contributors|the authors)\b", re.I)


def corporate_authors(authors: list[str]) -> list[str]:
    """Author strings that name a group rather than a person."""
    return [a for a in authors if CORPORATE_AUTHOR.search(a)]


def arxiv_authors(ax: str) -> list[str] | None:
    """The complete author list for one arXiv id.

    `[]` means arXiv answered and has no entry under that id. `None` means it did not
    answer -- which `authorship_gate` has to tell apart, since it drops a paper on this.
    """
    st, raw = get_status(f"http://export.arxiv.org/api/query?id_list={ax}&max_results=1")
    if st != 200 or not raw:
        return None if st != 404 else []
    try:
        e = ET.fromstring(raw).find("a:entry", ARXIV_NS)
    except ET.ParseError:
        return None
    if e is None:
        return []
    return [" ".join((a.findtext("a:name", default="", namespaces=ARXIV_NS)).split())
            for a in e.findall("a:author", ARXIV_NS)]


def authorship_gate(papers: list[dict], cfg: dict, ov: dict) -> list[dict]:
    """Keep only papers whose author list names you in some form. (kept, rejected)

    `bibtex_url` is a CV bibliography, so it also carries the works the CV *cites*.
    Without this gate every consumer inherits them: a canonical page for someone else's
    paper, an `orcid_import.bib` asserting you wrote it, an arXiv ownership request a
    human has to reject. Excluding is the safe default because the errors are not
    symmetric -- a missed paper of yours costs one page, a claimed paper of someone
    else's is a false authorship assertion in a public registry.

    Rejects go to build/not_mine.json for review. A short or consortium author list is
    checked against arXiv first, and only on papers about to be dropped. A reject whose
    arXiv check did not answer carries `arxiv_silent`, so it is not filed as checked. To
    keep one regardless, record its title under `also_mine` in data/overrides.yaml.
    """
    variants = cfg["identity"]["name_variants"]
    keep_norm = {norm_title(t) for t in (ov.get("also_mine") or [])}
    kept, rejected, silent = [], [], set()
    for p in papers:
        authors = p.get("authors") or []
        marks = {name_match(a, variants) for a in authors}
        # `and others` in the source is not evidence of absence, and neither is a
        # one-entry list naming a consortium. Mass-authored papers are the ones where
        # an author is most dependent on the index knowing they were on it, so spend
        # one request and ask arXiv, which lists everybody.
        corp = corporate_authors(authors)
        if not marks & {"exact", "near"} and p.get("arxiv"):
            full = arxiv_authors(p["arxiv"])
            if full is None:
                silent.add(p["arxiv"])
            elif full and len(full) > len(authors):
                p["authors_from_arxiv"] = {"was": len(authors), "now": len(full),
                                           "why": "consortium author" if corp else
                                                  "list was short"}
                p["authors"] = authors = full
                p.pop("authors_truncated", None)
                marks = {name_match(a, variants) for a in authors}
        if "exact" in marks or "near" in marks:
            # A near match means the *source* misspells you. Keep the paper -- it is
            # yours -- and carry the flag so the audit can chase the upstream fix.
            if "exact" not in marks:
                p["name_misspelled_upstream"] = [a for a in authors
                                                 if name_match(a, variants) == "near"]
            kept.append(p)
        elif norm_title(p.get("title")) in keep_norm:
            p["authorship_override"] = True
            kept.append(p)
        else:
            rejected.append(p)
    for p in rejected:
        if p.get("arxiv") in silent:
            p["arxiv_silent"] = True
    # Removed when there is nothing to write, because both readers take this file as what
    # the gate decided *this* run. `scholar_check.attributed_gaps` drops a gap whose title
    # the file names, and `audit_identity.orcid_strays` tags a stray `confirmed` on the
    # strength of it, which `WORKLIST.md` reports as "the collector rejected each of these".
    # Left standing after a run that rejected nothing, it puts last run's answer behind both.
    not_mine = os.path.join(BUILD, "not_mine.json")
    if rejected:
        # `n_authors` and `confidence` are the two facts a reviewer needs and the old
        # four-name sample hid: it printed "authors: 4" for a 561-author paper, so every
        # row looked like a small paper whose list might be truncated. `confidence` says
        # which rows are a judgement and which are a fact, so a reviewer reads three rows
        # instead of sixteen.
        write_json(
            not_mine,
            [{"title": p.get("title"), "key": p.get("key"),
              "confidence": reject_confidence(p),
              "arxiv": p.get("arxiv"), "doi": p.get("doi"),
              "n_authors": len(p.get("authors") or []),
              "corporate_author": corporate_authors(p.get("authors") or []),
              "authors_sample": (p.get("authors") or [])[:4],
              "to_keep_anyway": "add the title under `also_mine` in "
                                "data/overrides.yaml"}
             for p in rejected], indent=1)
    elif os.path.exists(not_mine):
        os.remove(not_mine)
    return kept, rejected


def reject_confidence(p: dict) -> str:
    """How much a rejection is worth a human's time.

    Not every drop is equally safe. Where arXiv confirmed the full list and your name is
    absent, the answer is a fact and nobody needs to read it. Where the only author
    string names a group and there is no arXiv id to expand it, the gate dropped a paper
    on no evidence about who wrote it -- which is the exact shape that lost MindGames.
    An arXiv id that did not answer is the same shape, and reads as checked without this.
    """
    if p.get("arxiv_silent"):
        return "unverified: arXiv did not answer, so its full author list was never read"
    if corporate_authors(p.get("authors") or []) and not p.get("arxiv"):
        return "unverified: group name for an author, and no arXiv id to expand it"
    if p.get("arxiv"):
        return "checked: arXiv's full author list does not contain your name"
    return "not checked: no arXiv id, but the author list names people"


def title_diffs(papers: list[dict]) -> list[dict]:
    """Papers whose stored title is not the one arXiv is serving today.

    A review list, not an error: sometimes ours is the published retitle and arXiv is the
    stale side. Each row carries both titles plus the words unique to each, so a reader
    can tell a retitle from a typo without diffing long strings by eye. Written to
    build/, since it is a statement about a source at a moment.
    """
    out = []
    for p in papers:
        ax = p.get("_arxiv_title")
        if not ax or not p.get("title") or norm_title(ax) == norm_title(p["title"]):
            continue
        # `norm_title` drops the spaces too, so it cannot be split into words. `slugify`
        # normalizes the same way (LaTeX, accents, math) but keeps token boundaries; the
        # length cap has to go, since it exists for URLs and would truncate the diff.
        def words(s): return set(slugify(s, maxlen=10 ** 6).split("-"))
        a, b = words(ax), words(p["title"])
        out.append({"arxiv": p.get("arxiv"), "slug": p.get("slug"), "key": p.get("key"),
                    "ours": p["title"], "arxiv_says": ax,
                    # Word-level, so a reader can see at a glance whether this is a
                    # retitle or a typo without diffing two long strings by eye.
                    "only_in_ours": sorted(b - a), "only_on_arxiv": sorted(a - b)})
    return out


def flag_problems(papers: list[dict]) -> None:
    """Flag records that look like metadata damage rather than real papers."""
    # The documented Scholar/S2 failure mode: a venue name extracted as a title.
    VENUE_WORDS = ("journal of", "proceedings of", "transactions on",
                   "conference on", "advances in")
    for p in papers:
        t = (p.get("title") or "").lower()
        problems = []
        if any(t.startswith(w) for w in VENUE_WORDS) and not p.get("arxiv"):
            problems.append("title looks like a venue name, not a paper title")
        if not p.get("year"):
            problems.append("no year")
        if not p.get("authors") and not p.get("only_in_s2"):
            problems.append("no authors parsed")
        if problems:
            p["metadata_problems"] = problems


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true",
                    help="only re-derive from the existing papers.yaml")
    ap.add_argument("--no-arxiv", action="store_true")
    ap.add_argument("--no-hf", action="store_true")
    ap.add_argument("--allow-shrink", action="store_true",
                    help="write even if coverage dropped sharply vs the last commit")
    args = ap.parse_args()
    # `--no-arxiv` / `--no-hf` skip a source on purpose, so the drop they cause is not
    # news; the guard exists for the outage you did not ask for.
    args.allow_shrink = args.allow_shrink or args.no_arxiv or args.no_hf
    cfg = load_config()
    out = os.path.join(DATA, "papers.yaml")

    if args.offline:
        papers = (read_yaml(out) or {}).get("papers", [])
        # Hand decisions are re-applied on this path too: `--offline` is a rerun, and
        # overrides.yaml promises a judgment call survives every rerun. Without this, editing
        # `fields` and re-deriving prints the usual summary while papers.yaml comes out byte
        # for byte unchanged. The merge and drop passes are no-ops on already-merged records,
        # so only the field corrections bite.
        papers = apply_overrides(papers, read_yaml(os.path.join(DATA, "overrides.yaml")) or {})
    else:
        print("bibtex ...", file=sys.stderr)
        papers = from_bibtex(cfg)
        print(f"  {len(papers)} entries", file=sys.stderr)
        # Before the merges, so an id added here gets the same S2 counts, dedupe and
        # authorship check as a bibliography entry -- including being rejected if it
        # turns out not to be yours.
        ov_early = read_yaml(os.path.join(DATA, "overrides.yaml")) or {}
        n_extra = from_arxiv_ids(papers, ov_early.get("extra_arxiv") or [])
        if n_extra:
            print(f"  + {n_extra} from overrides.extra_arxiv", file=sys.stderr)
        n_or = from_openreview_titles(papers, ov_early.get("extra_openreview") or [])
        if n_or:
            print(f"  + {n_or} from overrides.extra_openreview", file=sys.stderr)
        print("semantic scholar ...", file=sys.stderr)
        merge_s2(papers, cfg)
        if not args.no_arxiv:
            print("arxiv ...", file=sys.stderr)
            merge_arxiv(papers)
            print("abstract backfill ...", file=sys.stderr)
            backfill_abstracts(papers)
        n_ax = unfold_arxiv_dois(papers)
        if n_ax:
            print(f"  recovered {n_ax} arXiv id(s) encoded as a DataCite DOI",
                  file=sys.stderr)
        print("dedupe ...", file=sys.stderr)
        # overrides.yaml documents that the first title in a force_merge group wins for
        # display, and that has to reach dedupe rather than only apply_overrides: once
        # identifiers merge a group here, apply_overrides never sees two records to
        # choose between, and the LaTeX-mangled variant can win the title by accident.
        _ov = read_yaml(os.path.join(DATA, "overrides.yaml")) or {}
        papers, n_merged, n_flagged = dedupe(
            papers, prefer=[g[0] for g in (_ov.get("force_merge") or []) if g])
        print(f"  merged {n_merged} duplicate records; flagged {n_flagged} similar-but-distinct pairs",
              file=sys.stderr)
        if not args.no_hf:
            print("hugging face ...", file=sys.stderr)
            merge_hf(papers, cfg)
        build_links(papers)
        flag_problems(papers)
        ov = read_yaml(os.path.join(DATA, "overrides.yaml")) or {}
        before = len(papers)
        papers = apply_overrides(papers, ov)
        print(f"  overrides: {before - len(papers)} records folded or dropped", file=sys.stderr)
        # After the merges, not before: Semantic Scholar routinely supplies a fuller
        # author list than the bibliography, and gating on the short list would drop
        # papers that are yours for want of metadata we were about to fetch anyway.
        papers, not_mine = authorship_gate(papers, cfg, ov)
        for p in papers:
            if p.get("authors_from_arxiv"):
                a = p["authors_from_arxiv"]
                print(f"  authorship: kept {p.get('title', '')[:48]!r} -- arXiv lists "
                      f"{a['now']} authors, the source listed {a['was']} "
                      f"({a['why']})", file=sys.stderr)
        if not_mine:
            # The unverified ones named separately. The rest are a fact arXiv confirmed;
            # these are a guess the gate had no way to check, and burying them in a count
            # of sixteen is what made the last one invisible. The reason comes from
            # `reject_confidence`, so the row here and the row in not_mine.json cannot
            # disagree about why a paper was dropped.
            blind = [p for p in not_mine
                     if reject_confidence(p).startswith("unverified")]
            print(f"  authorship: {len(not_mine)} records have no form of your name "
                  f"and were excluded -- review build/not_mine.json", file=sys.stderr)
            for p in blind:
                print(f"    unverified drop: {p.get('title', '')[:56]!r} -- "
                      f"{reject_confidence(p).split(': ', 1)[1]}", file=sys.stderr)
        # After the merges and the gate, deliberately: this is four API calls per paper,
        # and a record that is about to be folded into its arXiv twin or excluded as
        # someone else's should not cost any of them.
        print("abstracts for the non-arXiv papers ...", file=sys.stderr)
        backfill_abstracts_offarxiv(papers)

    # Slugs are truncated, so two long titles can collide -- which silently made
    # one paper overwrite the other's page. Disambiguate deterministically (year,
    # then a title hash) so a slug never changes between runs.
    import hashlib
    from collections import Counter
    counts = Counter(p["slug"] for p in papers)
    for p in papers:
        if counts[p["slug"]] > 1:
            base = p["slug"]
            cand = f"{base}-{p['year']}" if p.get("year") else base
            if sum(1 for q in papers if q is not p and q["slug"] == base
                   and q.get("year") == p.get("year")):
                cand = f"{base}-{hashlib.sha1(p['title'].encode()).hexdigest()[:6]}"
            p["slug"] = cand

    for p in papers:
        # Display copies. The raw title stays in `title` for matching against
        # sources; everything user- or crawler-facing uses these.
        p["title_display"] = clean_latex(p.get("title")) or p.get("title")
        p["venue_display"] = short_venue(p.get("venue"), year=p.get("year"))
        if p.get("bibtex"):
            p["bibtex"] = clean_bibtex(p["bibtex"])
        p.pop("_norm", None)
        # DBLP escapes underscores for LaTeX; that leaks into URLs and breaks them.
        for f in ("url", "doi"):
            if p.get(f):
                p[f] = p[f].replace("\\_", "_").replace("\\&", "&").replace("\\%", "%")
    papers.sort(key=lambda p: (-(p.get("citations") or 0), -(p.get("year") or 0)))

    # After the slug disambiguation above, which is what this looks up by, and in both
    # branches: --offline is the rerun that picks up a link deduced since the last
    # online collect.
    add_deduced_links(papers)

    sidecar_dir = os.path.join(DATA, "sidecars")
    for p in papers:
        p["has_sidecar"] = os.path.exists(os.path.join(sidecar_dir, f"{p['slug']}.md"))

    baseline = _committed_papers(out)
    # A fresh fork commits the previous author's papers.yaml, so the first run here would
    # "lose" a hundred papers it never had and refuse to write -- the guard firing on the
    # one run that cannot possibly be an outage. Two corpora that share no slug at all are
    # two different people, not a source failure.
    if baseline and not ({p["slug"] for p in baseline} & {p["slug"] for p in papers}):
        print(f"  the committed papers.yaml holds {len(baseline)} paper(s) with no slug in "
              f"common with this run -- a different author's corpus, so it is not a "
              f"baseline. Treating this as a first run.", file=sys.stderr)
        baseline = []
    report, alarms = coverage_alarms(baseline, papers)
    if report:
        print("  coverage vs the last commit:", file=sys.stderr)
        print("\n".join(report), file=sys.stderr)
    if alarms and not args.allow_shrink:
        sys.exit("\n".join([
            "", "REFUSING TO WRITE -- this run has much less data than the last commit:",
            *(f"  {a}" for a in alarms), "",
            "That is what a source outage looks like, and writing would make the loss",
            "permanent on the next commit. Check the '!' lines above for a failed fetch",
            "and rerun. If the shrink is real (a big merge, papers dropped on purpose):",
            "  python scripts/collect.py --allow-shrink", ""]))

    tdiffs = title_diffs(papers)
    for p in papers:
        p.pop("_arxiv_title", None)
    # Written even when empty, so an absent file means this step has not run rather than
    # "arXiv agrees with every title we hold". `scholar_check.stale_side` decides which of
    # two titles is behind on this file, and an empty dict is its most reassuring answer.
    write_json(os.path.join(BUILD, "title_diffs.json"), tdiffs, indent=2,
               ensure_ascii=False)

    n_retired = record_slug_moves(papers, out)
    if n_retired:
        print(f"  slugs moved: {n_retired} (old URLs recorded in data/slug_history.yaml)",
              file=sys.stderr)

    # Last, so it is carrying over the records that are actually about to be written.
    n_own = carry_claims(papers, out)
    if n_own:
        print(f"  ownership carried over: {n_own} papers (re-derived by "
              f"`update.py --step ownership`)", file=sys.stderr)

    write_yaml(out, {"generated_by": "scripts/collect.py", "papers": papers})

    n = len(papers)
    ax = [p for p in papers if p.get("arxiv")]
    def c(pred, pool): return sum(1 for p in pool if pred(p))
    print(f"\nwrote {out}: {n} papers")
    print(f"  with arXiv id                 {len(ax)}/{n}")
    if not args.no_arxiv:
        print(f"  arXiv missing journal-ref     {c(lambda p: not p.get('arxiv_journal_ref'), ax)}/{len(ax)}")
        print(f"  arXiv missing HTML            {c(lambda p: p.get('arxiv_html') is False, ax)}/{len(ax)}")
    if not args.no_hf:
        print(f"  HF page missing               {c(lambda p: p.get('hf_indexed') is False, ax)}/{len(ax)}")
        print(f"  HF page not claimed by me     {c(lambda p: p.get('hf_indexed') and not p.get('hf_claimed_by_me'), ax)}/{len(ax)}")
        print(f"  HF knows a github repo        {c(lambda p: p.get('hf_github_repo'), ax)}/{len(ax)}")
    print(f"  no abstract anywhere          {c(lambda p: not p.get('abstract'), papers)}/{n}")
    print(f"  flagged metadata problems     {c(lambda p: p.get('metadata_problems'), papers)}/{n}")
    print(f"  merged duplicate records      {c(lambda p: p.get('merged_from'), papers)} groups")
    print(f"  similar-but-distinct flags    {c(lambda p: p.get('similar_but_distinct'), papers)}/{n}  (review these)")
    if tdiffs:
        print(f"  title differs from arXiv      {len(tdiffs)}/{len(ax)}  "
              f"(review build/title_diffs.json -- either side can be the stale one)")
    print(f"  verbatim bibtex captured      {c(lambda p: p.get('bibtex'), papers)}/{n}")
    print(f"  crawlable HTML surface        {c(lambda p: (p.get('links') or {}).get('html'), papers)}/{n}"
          f"  (ar5iv fallback: {c(lambda p: (p.get('links') or {}).get('html_source') == 'ar5iv', papers)})")
    print(f"  sidecars written              {c(lambda p: p['has_sidecar'], papers)}/{n}")


if __name__ == "__main__":
    main()
