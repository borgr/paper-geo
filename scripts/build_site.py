#!/usr/bin/env python3
"""Generate the published site into build/site/.

Static HTML, no JavaScript. AI crawlers largely do not execute JS, so anything
that needs a script to appear is invisible to them regardless of how it ranks in
Google.

Output:
    index.html                  entity home: Person JSON-LD + sameAs
    papers/index.html           paper index
    papers/<slug>/index.html    per paper: ScholarlyArticle JSON-LD, highwire
                                meta, visible abstract, Q&A, claims, citation
    papers/<slug>/llms.txt      the sidecar as plain text
    guides/index.html           the guide repos -- question-shaped content
    llms.txt                    site index
    sitemap.xml
    paper-geo.json              ownership manifest for collaborators
    .nojekyll                   serve generated dirs verbatim

Papers owned by a collaborator get an index entry linking to THEIR canonical
page and no page of our own -- see docs/COLLAB.md.

Usage:
    python scripts/build_site.py [--deploy]
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import BUILD, DATA, load_config, paper_doi, read_yaml  # noqa: E402
from ownership import write_manifest  # noqa: E402

OUT = os.path.join(BUILD, "site")
E = html.escape


def read_sidecar(slug: str) -> dict:
    """Front matter + body from data/sidecars/<slug>.md."""
    path = os.path.join(DATA, "sidecars", f"{slug}.md")
    if not os.path.exists(path):
        return {}
    import yaml
    text = open(path).read()
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        return {}
    fm = yaml.safe_load(m.group(1)) or {}
    fm["_body"] = m.group(2).strip()
    return fm


def page(title: str, body: str, *, head: str = "", canonical: str = "") -> str:
    """One minimal, no-JS document shell."""
    can = f'\n  <link rel="canonical" href="{E(canonical)}">' if canonical else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{E(title)}</title>{can}
{head}  <style>
    body {{ max-width: 46rem; margin: 2rem auto; padding: 0 1rem;
            font: 16px/1.6 Georgia, "Times New Roman", serif; color: #1a1a1a; }}
    h1, h2, h3 {{ font-family: -apple-system, system-ui, sans-serif; line-height: 1.25; }}
    h1 {{ font-size: 1.6rem; margin-bottom: .25rem; }}
    .sub {{ color: #555; font-size: 1.05rem; margin-top: 0; }}
    .meta {{ color: #555; font-size: .92rem; }}
    a {{ color: #06c; }}
    dl.qa dt {{ font-weight: 600; margin-top: 1rem; font-family: -apple-system, sans-serif; }}
    dl.qa dd {{ margin: .3rem 0 0 0; }}
    .scope {{ color: #444; font-size: .94rem; }}
    pre {{ background: #f6f6f4; padding: .8rem; overflow-x: auto; font-size: .84rem; }}
    ul.links {{ list-style: none; padding: 0; }}
    ul.links li {{ display: inline-block; margin: 0 .8rem .3rem 0; }}
    footer {{ margin-top: 3rem; border-top: 1px solid #ddd; padding-top: .8rem;
              font-size: .85rem; color: #666; }}
  </style>
</head>
<body>
{body}
</body>
</html>
"""


def jsonld(obj: dict) -> str:
    """Serialize with json.dumps, never by string concatenation.

    Titles and abstracts in this corpus contain raw LaTeX (Q\\({}^{\\mbox{2}}\\),
    $\\alpha$), and a hand-built JSON string leaves those backslashes unescaped --
    which silently produces invalid JSON-LD that no consumer can read. Escaping
    </ as <\\/ additionally stops a stray closing tag inside a string from ending
    the script element early.
    """
    body = json.dumps(obj, indent=2, ensure_ascii=False).replace("</", "<\\/")
    return f'  <script type="application/ld+json">\n{body}\n  </script>\n'


def person_jsonld(cfg) -> dict:
    ident, ids = cfg["identity"], cfg["ids"]
    same = [f"https://orcid.org/{ident['orcid']}",
            f"https://github.com/{ids['github']}",
            f"https://huggingface.co/{ids['huggingface']}",
            f"https://scholar.google.com/citations?user={ids['google_scholar']}",
            f"https://www.semanticscholar.org/author/{ids['semantic_scholar_primary']}",
            f"https://dblp.org/search?q={ids['dblp'].replace(' ', '+')}",
            f"https://openalex.org/{ids['openalex'][0].rsplit('/', 1)[-1]}",
            f"https://aclanthology.org/people/{ident['name'].lower().replace(' ', '-')}/"]
    if ids.get("linkedin"):
        same.append(f"https://www.linkedin.com/in/{ids['linkedin']}/")
    if ids.get("wikidata"):
        same.append(f"https://www.wikidata.org/wiki/{ids['wikidata']}")
    # Other personal pages belong here rather than being quietly retired. sameAs is
    # the assertion "these URLs are the same person", which is what stops a second
    # homepage being read as a second candidate identity. Omitting it does not make
    # the page go away; it just leaves the two unlinked.
    same += list(ident.get("other_pages") or [])
    return {
        "@context": "https://schema.org",
        "@type": "Person",
        "@id": ident["canonical_url"].rstrip("/") + "/#person",
        "name": ident["name"],
        "alternateName": ident["name_variants"],
        "identifier": f"https://orcid.org/{ident['orcid']}",
        "url": ident["canonical_url"],
        "email": f"mailto:{ident['email']}",
        "jobTitle": ident["job_title"],
        "affiliation": [{"@type": "Organization", "name": a}
                        for a in ident["affiliations"]],
        "sameAs": same,
    }


def article_jsonld(p: dict, sc: dict, cfg) -> dict:
    ident = cfg["identity"]
    base = cfg["site"]["base_url"].rstrip("/") + cfg["site"]["papers_path"]
    authors = []
    for a in p.get("authors") or []:
        node = {"@type": "Person", "name": a}
        if a == ident["name"]:
            node["@id"] = f"https://orcid.org/{ident['orcid']}"
        authors.append(node)
    links = dict(p.get("links") or {})
    links.update(sc.get("links_extra") or {})
    same = sorted(u for k, u in links.items()
                  if k != "html_source" and str(u).startswith("http"))
    d = {
        "@context": "https://schema.org",
        "@type": "ScholarlyArticle",
        "@id": f"{base}/{p['slug']}/#article",
        "name": p.get("title_display") or p["title"],
        "headline": p.get("title_display") or p["title"],
        "author": authors,
        "isAccessibleForFree": True,
    }
    if p.get("year"):
        d["datePublished"] = str(p["year"])
    if p.get("venue"):
        d["isPartOf"] = {"@type": "Periodical", "name": p.get("venue_display") or p["venue"][:250]}
    # paper_doi() rather than p["doi"]: an arXiv-only paper still has a resolvable
    # DataCite DOI, and identifier is how a consumer joins this page to a record it
    # already holds.
    if paper_doi(p):
        d["identifier"] = f"https://doi.org/{paper_doi(p)}"
    if p.get("abstract"):
        d["abstract"] = p["abstract"]
    if sc.get("one_liner"):
        d["description"] = " ".join(sc["one_liner"].split())
    if links.get("code"):
        d["codeRepository"] = links["code"]
    if same:
        d["sameAs"] = same
    if sc.get("claims"):
        # Each claim with its scope, as a machine-readable assertion rather than
        # only as prose a summariser has to re-derive.
        d["about"] = [{"@type": "Thing",
                       "name": " ".join(c["text"].split()),
                       "description": "Holds for: " + " ".join(c["scope"].split())}
                      for c in sc["claims"]]
    return d


def highwire(p: dict, cfg) -> str:
    """Google Scholar's preferred metadata scheme.

    All three of citation_title / citation_author / citation_publication_date must
    be present or Scholar processes the page as if it had no meta tags at all.

    citation_pdf_url is deliberately omitted: Scholar requires the linked PDF to
    sit in the same subdirectory as the HTML abstract, and ours lives on arXiv. An
    unsatisfiable tag is worse than no tag, so the PDF is a visible link only.
    """
    if not (p.get("title") and p.get("authors") and p.get("year")):
        return ""
    out = [f'  <meta name="citation_title" content="{E(p.get("title_display") or p["title"])}">']
    for a in p["authors"]:
        out.append(f'  <meta name="citation_author" content="{E(a)}">')
    out.append(f'  <meta name="citation_publication_date" content="{p["year"]}">')
    venue = p.get("venue_display") or p.get("venue") or ""
    if venue and venue.lower() not in ("corr", "arxiv", "arxiv.org"):
        tag = ("citation_conference_title" if p.get("type") == "inproceedings"
               else "citation_journal_title")
        out.append(f'  <meta name="{tag}" content="{E(venue)}">')
    if paper_doi(p):
        out.append(f'  <meta name="citation_doi" content="{E(paper_doi(p))}">')
    if p.get("arxiv"):
        out.append(f'  <meta name="citation_arxiv_id" content="{E(p["arxiv"])}">')
    if p.get("abstract"):
        out.append(f'  <meta name="citation_abstract" content="{E(p["abstract"][:2000])}">')
    return "\n".join(out) + "\n"


LINK_LABELS = {
    "arxiv": "arXiv", "arxiv_pdf": "PDF", "html": "HTML", "doi": "DOI",
    "acl_anthology": "ACL Anthology", "semantic_scholar": "Semantic Scholar",
    "huggingface": "Hugging Face", "alphaxiv": "alphaXiv",
    "publisher": "Publisher", "code": "Code", "data": "Data",
    "models": "Models", "project": "Project page", "video": "Talk",
    "slides": "Slides", "poster": "Poster", "blog": "Blog post",
    "leaderboard": "Leaderboard", "demo": "Demo",
}


def link_list(links: dict) -> str:
    items = []
    for k, u in links.items():
        if k == "html_source" or not str(u).startswith("http"):
            continue
        items.append(f'<li><a href="{E(u)}">{E(LINK_LABELS.get(k, k))}</a></li>')
    return f'<ul class="links">{"".join(items)}</ul>' if items else ""


def paper_page(p: dict, sc: dict, cfg) -> str:
    ident = cfg["identity"]
    base = cfg["site"]["base_url"].rstrip("/") + cfg["site"]["papers_path"]
    url = f"{base}/{p['slug']}/"
    links = dict(p.get("links") or {})
    links.update(sc.get("links_extra") or {})

    disp = p.get("title_display") or p["title"]
    b = [f"<h1>{E(disp)}</h1>"]
    if sc.get("gloss"):
        b.append(f'<p class="sub">{E(sc["gloss"])}</p>')
    meta = " · ".join(x for x in [", ".join(p.get("authors") or []),
                                  p.get("venue_display") or "", str(p.get("year") or "")] if x)
    b.append(f'<p class="meta">{E(meta)}</p>')
    b.append(link_list(links))

    if sc.get("one_liner"):
        b.append("<h2>In one sentence</h2>")
        b.append(f"<p>{E(' '.join(sc['one_liner'].split()))}</p>")

    # Abstract must be visible with no gate: Scholar requires it, and it is the
    # only body text on a paper that has no sidecar yet.
    if p.get("abstract"):
        b.append("<h2>Abstract</h2>")
        b.append(f"<p>{E(p['abstract'])}</p>")

    claims = {c["id"]: c for c in (sc.get("claims") or []) if c.get("id")}
    if sc.get("qa"):
        b.append("<h2>Questions this paper answers</h2>")
        b.append('<dl class="qa">')
        for qa in sc["qa"]:
            for q in qa.get("q") or []:
                b.append(f"<dt>{E(q)}</dt>")
            for cid in qa.get("answers") or []:
                c = claims.get(cid)
                if not c:
                    continue
                # The claim text verbatim, never paraphrased into the answer.
                b.append(f"<dd>{E(' '.join(c['text'].split()))}"
                         f'<br><span class="scope">Holds for: '
                         f"{E(' '.join(c['scope'].split()))}</span></dd>")
        b.append("</dl>")

    if claims:
        b.append("<h2>Claims and scope</h2><ul>")
        for c in claims.values():
            ev = f" <span class=\"meta\">({E(c['evidence'])})</span>" if c.get("evidence") else ""
            b.append(f"<li>{E(' '.join(c['text'].split()))}{ev}<br>"
                     f'<span class="scope">Scope: {E(" ".join(c["scope"].split()))}</span></li>')
        b.append("</ul>")

    if sc.get("misreadings"):
        b.append("<h2>Common misreadings</h2><ul>")
        for m in sc["misreadings"]:
            b.append(f"<li>{E(m)}</li>")
        b.append("</ul>")

    if sc.get("terminology"):
        b.append("<h2>Terminology in this paper</h2><dl>")
        for t, d in sc["terminology"].items():
            b.append(f"<dt><em>{E(t)}</em></dt><dd>{E(' '.join(str(d).split()))}</dd>")
        b.append("</dl>")

    if sc.get("_body"):
        b.append(f"<h2>Notes</h2>\n<p>{E(sc['_body'])}</p>")

    if p.get("bibtex"):
        b.append("<h2>How to cite</h2>")
        b.append(f"<pre>{E(p['bibtex'].strip())}</pre>")

    # A literal "References" heading is one of Scholar's PDF-layout fallback cues.
    b.append("<h2>References</h2>")
    b.append(f'<p>See the full reference list in the '
             f'<a href="{E(links.get("html") or links.get("arxiv") or url)}">paper</a>.</p>')

    b.append(f'<footer><a href="{E(cfg["site"]["base_url"])}">{E(ident["name"])}</a> · '
             f'<a href="llms.txt">llms.txt</a></footer>')

    head = highwire(p, cfg) + jsonld(article_jsonld(p, sc, cfg))
    return page(f"{p['title']} — {ident['name']}", "\n".join(b),
                head=head, canonical=url)


def paper_llms_txt(p: dict, sc: dict, cfg) -> str:
    """The sidecar as plain text: author-written orientation, not a crawler directive."""
    L = [f"# {p.get('title_display') or p['title']}", ""]
    if sc.get("gloss"):
        L += [sc["gloss"], ""]
    L += [f"Authors: {', '.join(p.get('authors') or [])}",
          f"Venue: {p.get('venue') or 'preprint'} ({p.get('year') or 'n.d.'})", ""]
    if sc.get("one_liner"):
        L += ["## What this paper shows", " ".join(sc["one_liner"].split()), ""]
    if sc.get("claims"):
        L.append("## Claims, with scope")
        for c in sc["claims"]:
            L += [f"- {' '.join(c['text'].split())}",
                  f"  Scope: {' '.join(c['scope'].split())}"]
            if c.get("evidence"):
                L.append(f"  Evidence: {c['evidence']}")
        L.append("")
    if sc.get("misreadings"):
        L += ["## Common misreadings"] + [f"- {m}" for m in sc["misreadings"]] + [""]
    if sc.get("terminology"):
        L.append("## Terminology")
        for t, d in sc["terminology"].items():
            L.append(f"- {t}: {' '.join(str(d).split())}")
        L.append("")
    if not sc:
        L += ["## Abstract", p.get("abstract") or "(none available)", ""]
    links = dict(p.get("links") or {})
    links.update(sc.get("links_extra") or {})
    L.append("## Links")
    for k, u in links.items():
        if k != "html_source":
            L.append(f"- {LINK_LABELS.get(k, k)}: {u}")
    if p.get("bibtex"):
        L += ["", "## How to cite", p["bibtex"].strip()]
    return "\n".join(L) + "\n"


def build(cfg) -> dict:
    papers = [p for p in (read_yaml(os.path.join(DATA, "papers.yaml")) or {})["papers"]]
    repos = (read_yaml(os.path.join(DATA, "repos.yaml")) or {}).get("repos", [])
    ident = cfg["identity"]
    site = cfg["site"]["base_url"].rstrip("/")
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, ".nojekyll"), "w").close()

    stats = {"pages": 0, "with_sidecar": 0, "peer_owned": 0}
    urls = [site + "/", f"{site}/papers/", f"{site}/guides/"]
    index_rows, llms = [], []

    for p in sorted(papers, key=lambda p: (-(p.get("citations") or 0))):
        ptitle = p.get("title_display") or p["title"]
        title, slug = ptitle, p["slug"]
        if p.get("canonical_page"):
            # Owned by a collaborator: link to theirs, publish nothing competing.
            index_rows.append(f'<li>{E(title)} — canonical page: '
                              f'<a href="{E(p["canonical_page"])}">{E(p["owner"] or "co-author")}</a></li>')
            stats["peer_owned"] += 1
            continue
        sc = read_sidecar(slug)
        if sc:
            stats["with_sidecar"] += 1
        d = os.path.join(OUT, "papers", slug)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w") as f:
            f.write(paper_page(p, sc, cfg))
        with open(os.path.join(d, "llms.txt"), "w") as f:
            f.write(paper_llms_txt(p, sc, cfg))
        stats["pages"] += 1
        urls.append(f"{site}/papers/{slug}/")
        cites = p.get("citations")
        index_rows.append(
            f'<li><a href="/papers/{E(slug)}/">{E(title)}</a> '
            f'<span class="meta">{E(str(p.get("venue") or "preprint")[:60])}'
            f'{f" · {cites} citations" if cites else ""}</span></li>')
        llms.append(f"- [{title}]({site}/papers/{slug}/llms.txt)"
                    + (f" — {' '.join(sc['one_liner'].split())}" if sc.get("one_liner") else ""))

    # ---- paper index
    with open(os.path.join(OUT, "papers", "index.html"), "w") as f:
        f.write(page(f"Papers — {ident['name']}",
                     f"<h1>Papers</h1>\n<ul>\n{chr(10).join(index_rows)}\n</ul>\n"
                     f'<footer><a href="/">{E(ident["name"])}</a></footer>',
                     canonical=f"{site}/papers/"))

    # ---- guides: question-shaped content, its own page shape
    guides = [r for r in repos if r.get("kind") == "guide" and not r.get("skip")]
    g = ["<h1>Guides</h1>",
         "<p>Practical guides, each answering one question.</p>", "<ul>"]
    for r in sorted(guides, key=lambda r: r["repo"]):
        u = r.get("homepage") or f"https://github.com/{r['repo']}"
        g.append(f'<li><a href="{E(u)}">{E(r["repo"].split("/")[-1])}</a> — '
                 f'{E(r.get("description") or "")}</li>')
    g += ["</ul>", f'<footer><a href="/">{E(ident["name"])}</a></footer>']
    os.makedirs(os.path.join(OUT, "guides"), exist_ok=True)
    with open(os.path.join(OUT, "guides", "index.html"), "w") as f:
        f.write(page(f"Guides — {ident['name']}", "\n".join(g),
                     canonical=f"{site}/guides/"))

    # ---- entity home
    home = [f"<h1>{E(ident['name'])}</h1>",
            f'<p class="sub">{E(ident["job_title"])} · '
            f'{E(", ".join(ident["affiliations"]))}</p>',
            f'<p class="meta">ORCID <a href="https://orcid.org/{ident["orcid"]}">'
            f'{ident["orcid"]}</a> · <a href="mailto:{E(ident["email"])}">'
            f'{E(ident["email"])}</a></p>',
            f'<p><a href="/papers/">{stats["pages"]} papers</a> · '
            f'<a href="/guides/">{len(guides)} guides</a> · '
            f'<a href="https://github.com/{cfg["ids"]["github"]}">code</a> · '
            f'<a href="/llms.txt">llms.txt</a></p>',
            "<h2>Most cited</h2><ul>"]
    for p in sorted(papers, key=lambda p: -(p.get("citations") or 0))[:10]:
        ptitle = p.get("title_display") or p["title"]
        href = p.get("canonical_page") or f"/papers/{p['slug']}/"
        home.append(f'<li><a href="{E(href)}">{E(ptitle)}</a> '
                    f'<span class="meta">{p.get("citations") or 0} citations</span></li>')
    home.append("</ul>")
    with open(os.path.join(OUT, "index.html"), "w") as f:
        f.write(page(ident["name"], "\n".join(home),
                     head=jsonld(person_jsonld(cfg)),
                     canonical=site + "/"))

    # ---- site llms.txt
    with open(os.path.join(OUT, "llms.txt"), "w") as f:
        f.write(f"""# {ident['name']}

{ident['job_title']} at {', '.join(ident['affiliations'])}.
ORCID {ident['orcid']} · {ident['email']}

Each paper below has a plain-text page stating what it shows, the conditions the
claim holds under, and common misreadings -- written by the author, not extracted.

## Papers
{chr(10).join(llms)}

## Guides
{chr(10).join(f"- [{r['repo'].split('/')[-1]}]({r.get('homepage') or 'https://github.com/' + r['repo']}) — {r.get('description') or ''}" for r in sorted(guides, key=lambda r: r['repo']))}
""")

    # ---- sitemap
    with open(os.path.join(OUT, "sitemap.xml"), "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                + "".join(f"  <url><loc>{E(u)}</loc></url>\n" for u in urls)
                + "</urlset>\n")

    # ---- robots: explicitly welcome the AI crawlers
    with open(os.path.join(OUT, "robots.txt"), "w") as f:
        f.write("User-agent: *\nAllow: /\n\n"
                "# AI crawlers are welcome; blocking them removes this site from the\n"
                "# retrieval path of ChatGPT, Claude, Perplexity and Google AI Mode.\n"
                + "".join(f"User-agent: {b}\nAllow: /\n\n" for b in
                          ("GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot",
                           "Claude-SearchBot", "PerplexityBot", "Google-Extended"))
                + f"Sitemap: {site}/sitemap.xml\n")

    write_manifest(cfg, papers)
    return stats


def deploy(cfg) -> None:
    """Push build/site into the Pages repo as a single commit."""
    repo = cfg["site"]["repo"]
    work = os.path.join(BUILD, "deploy")
    if os.path.isdir(work):
        shutil.rmtree(work)
    if subprocess.call(["gh", "repo", "clone", repo, work, "--", "--depth", "1"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL):
        sys.exit(f"could not clone {repo}")
    for name in os.listdir(work):
        if name != ".git":
            path = os.path.join(work, name)
            shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)
    for name in os.listdir(OUT):
        src, dst = os.path.join(OUT, name), os.path.join(work, name)
        shutil.copytree(src, dst) if os.path.isdir(src) else shutil.copy2(src, dst)
    subprocess.call(["git", "add", "-A"], cwd=work)
    if subprocess.call(["git", "diff", "--cached", "--quiet"], cwd=work) == 0:
        print("site unchanged; nothing to deploy")
        return
    subprocess.call(["git", "commit", "-q", "-m", "Rebuild site (paper-geo)"], cwd=work)
    if subprocess.call(["git", "push", "-q"], cwd=work):
        sys.exit("push failed")
    print(f"deployed to {cfg['site']['base_url']}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--deploy", action="store_true", help="push to the Pages repo")
    args = ap.parse_args()
    cfg = load_config()
    s = build(cfg)
    print(f"built {OUT}")
    print(f"  paper pages          {s['pages']}")
    print(f"  of those, with sidecar {s['with_sidecar']}")
    print(f"  linked to a peer's canonical page {s['peer_owned']}")
    if args.deploy:
        deploy(cfg)


if __name__ == "__main__":
    main()
