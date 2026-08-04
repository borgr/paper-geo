#!/usr/bin/env python3
"""Build data/papers.yaml: one record per paper, merged from every source.

Sources, in precedence order for any conflicting field:
  1. enhanced.bib   (the author's own curated bibliography — venue truth)
  2. Semantic Scholar (abstracts, citation counts, cross-ids)
  3. arXiv API      (journal-ref / DOI presence — i.e. what needs fixing)
  4. Hugging Face   (paper-page existence and authorship claims)

Everything downstream (site, CITATION.cff, worklist, Wikidata) reads only this
file, so a source outage degrades one field rather than the whole pipeline.

Usage:
    python scripts/collect.py [--offline] [--no-arxiv] [--no-hf]
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import time
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (DATA, arxiv_id, clean_bibtex, clean_latex, get, get_json,  # noqa: E402
                    load_config, norm_title, parse_bibtex, read_yaml, short_venue,
                    slugify, split_authors, write_yaml)

ARXIV_NS = {"a": "http://www.w3.org/2005/Atom", "ar": "http://arxiv.org/schemas/atom"}


def from_bibtex(cfg) -> list[dict]:
    raw = get(cfg["sources"]["bibtex_url"]).decode("utf-8", "replace")
    if not raw:
        sys.exit("could not fetch bibtex_url")
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


def build_links(papers: list[dict]) -> None:
    """Resolve every surface a paper has into one `links` map.

    This is what a JSON-LD `sameAs` array consumes, and it is the difference
    between an engine treating five URLs as five unrelated pages and treating
    them as one work with five locations. Identifiers stay the source of truth;
    these are derived from them on every run, so they can never drift.

    `links_extra` in the paper's sidecar is for what cannot be derived: project
    page, talk video, slides, poster, leaderboard, blog post.
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
            meta[base] = {
                "arxiv_journal_ref": jr.text.strip() if jr is not None else None,
                "arxiv_doi": doi.text.strip() if doi is not None else None,
                "arxiv_comment": " ".join((com.text or "").split()) if com is not None else None,
            }
        time.sleep(3)
    for p in papers:
        if p.get("arxiv"):
            p.update(meta.get(p["arxiv"], {}))
            # HTML exists for LaTeX submissions from late 2023 on, and arXiv is
            # gradually backfilling older ones -- so False means "not yet", not
            # "never". There is no author-facing way to request it; the only lever is
            # a submission whose LaTeX converts. ar5iv covers the gap meanwhile.
            p["arxiv_html"] = bool(get(f"https://arxiv.org/html/{p['arxiv']}", retries=1))
            # Note: the arXiv DataCite DOI (10.48550/arXiv.<id>) is deliberately NOT
            # written here. Storing it would let it shadow a publisher DOI that shows
            # up later, and it is derivable from the id anyway -- so it is computed at
            # the point of use by common.paper_doi(). papers.yaml holds only what a
            # source actually asserted.


def merge_hf(papers: list[dict], cfg) -> None:
    """HF paper pages carry claim state AND the paper->repo/model/dataset links."""
    me = cfg["ids"]["huggingface"]
    for p in papers:
        if not p.get("arxiv"):
            continue
        d = get_json(f"https://huggingface.co/api/papers/{p['arxiv']}", retries=1)
        if d is None:
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
    v = (p.get("venue") or "").strip().lower()
    return v in ("", "corr", "arxiv", "arxiv.org") or v.startswith("arxiv")


def dedupe(papers: list[dict]) -> tuple[list[dict], int, int]:
    """Merge exact/near-exact duplicates; flag the uncertain band for review.

    Bibliographies routinely hold both the DBLP CoRR preprint entry and the
    published entry for one paper. Publishing two pages for one paper is exactly
    the duplicate-title failure Scholar's docs warn about, so they must be one
    record here. Merged records keep the published venue and the preprint's
    arXiv id and abstract.
    """
    import difflib

    norms = [norm_title(p.get("title")) for p in papers]
    parent = list(range(len(papers)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    flagged = 0
    for i in range(len(papers)):
        for j in range(i + 1, len(papers)):
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
        base = dict(max(published or members, key=lambda m: len(m.get("venue") or "")))
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
        members = [m for m in members if m is not None]
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
            p.setdefault("overridden_fields", []).append(k)
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
    args = ap.parse_args()
    cfg = load_config()
    out = os.path.join(DATA, "papers.yaml")

    if args.offline:
        papers = (read_yaml(out) or {}).get("papers", [])
    else:
        print("bibtex ...", file=sys.stderr)
        papers = from_bibtex(cfg)
        print(f"  {len(papers)} entries", file=sys.stderr)
        print("semantic scholar ...", file=sys.stderr)
        merge_s2(papers, cfg)
        if not args.no_arxiv:
            print("arxiv ...", file=sys.stderr)
            merge_arxiv(papers)
            print("abstract backfill ...", file=sys.stderr)
            backfill_abstracts(papers)
        print("dedupe ...", file=sys.stderr)
        papers, n_merged, n_flagged = dedupe(papers)
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
        p["venue_display"] = short_venue(p.get("venue"))
        if p.get("bibtex"):
            p["bibtex"] = clean_bibtex(p["bibtex"])
        p.pop("_norm", None)
        # DBLP escapes underscores for LaTeX; that leaks into URLs and breaks them.
        for f in ("url", "doi"):
            if p.get(f):
                p[f] = p[f].replace("\\_", "_").replace("\\&", "&").replace("\\%", "%")
    papers.sort(key=lambda p: (-(p.get("citations") or 0), -(p.get("year") or 0)))

    sidecar_dir = os.path.join(DATA, "sidecars")
    for p in papers:
        p["has_sidecar"] = os.path.exists(os.path.join(sidecar_dir, f"{p['slug']}.md"))

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
    print(f"  verbatim bibtex captured      {c(lambda p: p.get('bibtex'), papers)}/{n}")
    print(f"  crawlable HTML surface        {c(lambda p: (p.get('links') or {}).get('html'), papers)}/{n}"
          f"  (ar5iv fallback: {c(lambda p: (p.get('links') or {}).get('html_source') == 'ar5iv', papers)})")
    print(f"  sidecars written              {c(lambda p: p['has_sidecar'], papers)}/{n}")


if __name__ == "__main__":
    main()
