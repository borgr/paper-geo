#!/usr/bin/env python3
"""Machine-visibility audit for a researcher's paper corpus.

For every paper: is there an arXiv id, does arXiv carry journal-ref + DOI,
is there an HTML (LaTeXML) rendering, is there a Hugging Face paper page,
and is authorship claimed there.
"""
import json, time, urllib.request, urllib.parse, xml.etree.ElementTree as ET, sys, os

OUT = os.path.dirname(os.path.abspath(__file__))
S2_AUTHORS = ["41019330", "2283849613"]
UA = {"User-Agent": "geo-audit/1.0 (research metadata audit)"}


def get(url, timeout=40, retries=6):
    delay = 4
    for attempt in range(retries):
        try:
            return urllib.request.urlopen(
                urllib.request.Request(url, headers=UA), timeout=timeout).read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < retries - 1:
                time.sleep(delay)
                delay *= 2
                continue
            raise


def s2_papers():
    papers = {}
    for aid in S2_AUTHORS:
        url = (f"https://api.semanticscholar.org/graph/v1/author/{aid}/papers"
               f"?fields=title,year,externalIds,citationCount,venue,abstract&limit=500")
        for p in json.loads(get(url))["data"]:
            key = (p.get("title") or "").strip().lower()
            if key and key not in papers:
                p["_s2_author"] = aid
                papers[key] = p
        time.sleep(1)
    return list(papers.values())


def arxiv_meta(ids):
    """Batch-query the arXiv API for journal_ref / doi presence."""
    ns = {"a": "http://www.w3.org/2005/Atom", "ar": "http://arxiv.org/schemas/atom"}
    out = {}
    for i in range(0, len(ids), 40):
        chunk = ids[i:i + 40]
        url = f"http://export.arxiv.org/api/query?id_list={','.join(chunk)}&max_results=40"
        root = ET.fromstring(get(url))
        for e in root.findall("a:entry", ns):
            raw = e.find("a:id", ns).text.split("/abs/")[-1]
            base = raw.rsplit("v", 1)[0] if "v" in raw.split("/")[-1] else raw
            out[base] = {
                "journal_ref": e.find("ar:journal_ref", ns) is not None,
                "doi": e.find("ar:doi", ns) is not None,
                "comment": (e.find("ar:comment", ns).text or "").replace("\n", " ")
                           if e.find("ar:comment", ns) is not None else "",
                "version": raw,
            }
        time.sleep(3)
    return out


def head_ok(url):
    try:
        req = urllib.request.Request(url, headers=UA, method="HEAD")
        return urllib.request.urlopen(req, timeout=20).status == 200
    except Exception:
        return False


def hf_paper(aid):
    try:
        d = json.loads(get(f"https://huggingface.co/api/papers/{aid}", timeout=20))
        authors = d.get("authors", [])
        return {"indexed": True, "upvotes": d.get("upvotes", 0),
                "claimed": sum(1 for a in authors if a.get("user")),
                "authors": len(authors)}
    except Exception:
        return {"indexed": False}


def main():
    papers = s2_papers()
    print(f"corpus: {len(papers)} unique papers across {len(S2_AUTHORS)} S2 author records",
          file=sys.stderr)
    arx = [p["externalIds"]["ArXiv"] for p in papers
           if (p.get("externalIds") or {}).get("ArXiv")]
    print(f"with arXiv id: {len(arx)}", file=sys.stderr)
    meta = arxiv_meta(arx)

    rows = []
    for p in papers:
        ext = p.get("externalIds") or {}
        aid = ext.get("ArXiv")
        r = {"title": p.get("title"), "year": p.get("year"),
             "citations": p.get("citationCount"), "venue": p.get("venue"),
             "arxiv": aid, "doi": bool(ext.get("DOI")), "acl": ext.get("ACL"),
             "s2_author_record": p["_s2_author"],
             "has_abstract": bool(p.get("abstract"))}
        if aid:
            m = meta.get(aid, {})
            r["arxiv_journal_ref"] = m.get("journal_ref")
            r["arxiv_doi"] = m.get("doi")
            r["arxiv_comment"] = m.get("comment", "")
            r["arxiv_html"] = head_ok(f"https://arxiv.org/html/{aid}")
            hf = hf_paper(aid)
            r["hf_indexed"] = hf["indexed"]
            r["hf_claimed"] = hf.get("claimed", 0)
            time.sleep(0.2)
        rows.append(r)

    with open(os.path.join(OUT, "audit.json"), "w") as f:
        json.dump(rows, f, indent=1)

    n = len(rows)
    ax = [r for r in rows if r.get("arxiv")]
    def pct(k, d): return f"{k}/{d} ({100*k/d:.0f}%)" if d else "n/a"
    print("\n=== MACHINE-VISIBILITY AUDIT ===")
    print(f"papers                             {n}")
    print(f"  on S2 record A / B               {sum(1 for r in rows if r['s2_author_record']==S2_AUTHORS[0])} / {sum(1 for r in rows if r['s2_author_record']==S2_AUTHORS[1])}")
    print(f"  no abstract in S2                {pct(sum(1 for r in rows if not r['has_abstract']), n)}")
    print(f"  with arXiv id                    {pct(len(ax), n)}")
    print(f"  arXiv: NO journal-ref            {pct(sum(1 for r in ax if r.get('arxiv_journal_ref') is False), len(ax))}")
    print(f"  arXiv: NO DOI field              {pct(sum(1 for r in ax if r.get('arxiv_doi') is False), len(ax))}")
    print(f"  arXiv: NO HTML rendering         {pct(sum(1 for r in ax if r.get('arxiv_html') is False), len(ax))}")
    print(f"  HF paper page missing            {pct(sum(1 for r in ax if r.get('hf_indexed') is False), len(ax))}")
    print(f"  HF page w/ 0 claimed authors     {pct(sum(1 for r in ax if r.get('hf_indexed') and not r.get('hf_claimed')), len(ax))}")
    print("\nTop-cited papers missing arXiv journal-ref (worst offenders):")
    for r in sorted([r for r in ax if r.get("arxiv_journal_ref") is False],
                    key=lambda r: -(r["citations"] or 0))[:12]:
        print(f"  {r['citations']:>5} cites  {r['arxiv']:12} {(r['title'] or '')[:58]}")


if __name__ == "__main__":
    main()
