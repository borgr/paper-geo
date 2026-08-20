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
page and no page of our own -- see docs/RULES.md §12.

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
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (BUILD, DATA, ROOT, is_preprint_venue,  # noqa: E402
                    load_config, norm_title, note_fetch, org_name, paper_doi,
                    read_yaml, slugify, social_url, venue_is_conference)
from ownership import write_manifest  # noqa: E402

OUT = os.path.join(BUILD, "site")
# Files the site must serve that nothing here generates -- ownership proofs, mostly.
STATIC = os.path.join(ROOT, "static")
E = html.escape


def _host(url: str) -> str:
    """`https://bsky.app/profile/x` -> `bsky.app/profile/x`, for link text.

    Link text matters more than usual on an identity page: a row of bare domains
    reads as a list of profiles, while a row of full URLs reads as noise, and the
    scheme carries no information a reader wants.
    """
    return re.sub(r"^https?://(www\.)?", "", url).rstrip("/")


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


def verification_meta(cfg) -> str:
    """Search Console / Bing ownership meta tags, on the homepage only.

    Generated rather than pasted, because `--deploy` deletes everything in the Pages
    repo before copying build/site over it. A verification file dropped in by hand
    survives until the next run and then silently disappears, at which point the
    property un-verifies and the reports stop -- with nothing to connect the two
    events. Anything that must persist has to be produced here.

    The meta-tag method is used for both services in preference to their file
    methods: one config value each, one place to look, and it cannot be orphaned by
    a rename.
    """
    v = (cfg.get("site") or {}).get("verification") or {}
    out = ""
    if v.get("google"):
        out += f'  <meta name="google-site-verification" content="{E(v["google"])}">\n'
    if v.get("bing"):
        out += f'  <meta name="msvalidate.01" content="{E(v["bing"])}">\n'
    return out


def year_sections(papers: list) -> list:
    """Every paper under its year, newest year first, most cited first within a year.

    Two orderings of one complete list, rather than one ordering twice: an agent asking
    what this author works on now reads the years, and one asking which work carries
    weight reads /papers/. The citation count decides the order inside a year and is not
    printed -- it comes from Semantic Scholar, is a fraction of the Google Scholar number
    a reader would compare it against, and a number that invites that comparison and
    loses it is worse than no number.
    """
    out = []
    for year in sorted({p.get("year") or 0 for p in papers}, reverse=True):
        of_year = [p for p in papers if (p.get("year") or 0) == year]
        out.append(f"<h3>{year or 'Undated'}</h3><ul>")
        for p in sorted(of_year, key=lambda q: -(q.get("citations") or 0)):
            title = p.get("title_display") or p["title"]
            href = p.get("canonical_page") or f"/papers/{p['slug']}/"
            out.append(f'<li><a href="{E(href)}">{E(title)}</a> '
                       f'<span class="meta">{E(venue_of(p))}</span></li>')
        out.append("</ul>")
    return out


def venue_of(p: dict) -> str:
    """How a paper's venue is named in a list: the short form, never the full proceedings
    title. `venue` carries what the bibliography holds -- "Advances in Neural Information
    Processing Systems 36: Annual Conference on ... December 10 - 16, 2023" -- which a
    60-character truncation turned into "Advances in Neural Information Processing Systems
    36: Annual C". `venue_display` is the same fact as a reader states it: "NeurIPS 2023".
    """
    return str(p.get("venue_display") or p.get("venue") or "preprint")[:60]


def human_note(ident: dict, *, box: bool) -> str:
    """"You probably wanted the personal site" -- the one thing a person needs from here.

    This site exists to be read by machines: it is the canonical URL in ORCID, Scholar,
    arXiv and every JSON-LD sameAs, which is exactly why a person following any of those
    fields lands on it by accident. Answering that with a link styled like navigation was
    not enough -- it read as one more entry in a list of profiles. So the home page says it
    in a box, in the words the visitor is already thinking, and every other page repeats it
    in one line of its footer, because search sends people to a paper page far more often
    than to a home page.
    """
    pages = ident.get("other_pages") or []
    if not pages:
        return ""
    links = " · ".join(f'<a rel="me" href="{E(u)}">{E(_host(u))}</a>' for u in pages)
    if box:
        return (f'<p class="human"><b>Human?</b> You probably wanted the personal site: '
                f'{links}<br><span class="meta">These pages are written for search engines '
                f'and answer engines -- one page per paper, with its claims, scope and '
                f'sources in a form a machine can quote.</span></p>')
    return f'<span class="meta">Human? You probably wanted {links}</span>'


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
    .lead {{ font-size: 1.05rem; margin: .6rem 0; }}
    a {{ color: #06c; }}
    dl.qa dt {{ font-weight: 600; margin-top: 1rem; font-family: -apple-system, sans-serif; }}
    dl.qa dd {{ margin: .3rem 0 0 0; }}
    .scope {{ color: #444; font-size: .94rem; }}
    pre {{ background: #f6f6f4; padding: .8rem; overflow-x: auto; font-size: .84rem; }}
    ul.links {{ list-style: none; padding: 0; }}
    ul.links li {{ display: inline-block; margin: 0 .8rem .3rem 0; }}
    footer {{ margin-top: 3rem; border-top: 1px solid #ddd; padding-top: .8rem;
              font-size: .85rem; color: #666; }}
    .human {{ background: #fbf7e8; border: 1px solid #e4d9b0; border-radius: 4px;
              padding: .7rem .9rem; margin: 1rem 0; font-size: 1.02rem; }}
    .human b {{ font-family: -apple-system, system-ui, sans-serif; }}
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


def org_ld(a) -> dict:
    """An affiliation as a schema.org Organization, with identifiers when it has them.

    A bare name is a string a disambiguator has to guess at -- "IBM Research" is
    thousands of people and several legal entities. A name plus a `url`, and better a
    plus a ROR id, is an entity: ROR is the identifier Crossref, DataCite and OpenAlex
    use for institutions, so it is the affiliation key that other databases can join on
    rather than string-match. `sameAs` carries them because that is the property whose
    meaning is "this URL denotes this thing".

    Kept optional per entry. A guessed lab URL is worse than a bare name, on the same
    logic as the social handles: a wrong identifier asserts a relationship to the wrong
    organisation, while a missing one only fails to assert a real one.
    """
    if isinstance(a, str):
        return {"@type": "Organization", "name": a}
    out = {"@type": "Organization", "name": str(a.get("name") or "")}
    if a.get("url"):
        out["url"] = a["url"]
    same = ([f"https://ror.org/{a['ror'].split('/')[-1]}"] if a.get("ror") else []) \
        + ([f"https://www.wikidata.org/wiki/{a['wikidata']}"] if a.get("wikidata") else [])
    if same:
        out["sameAs"] = same
    return out


def person_jsonld(cfg) -> dict:
    ident, ids = cfg["identity"], cfg["ids"]
    same = [f"https://orcid.org/{ident['orcid']}",
            f"https://github.com/{ids['github']}",
            f"https://huggingface.co/{ids['huggingface']}",
            f"https://scholar.google.com/citations?user={ids['google_scholar']}",
            f"https://www.semanticscholar.org/author/{ids['semantic_scholar_primary']}",
            # The pid page, not a search URL: `sameAs` asserts "this URL is this
            # person", and a search results page is not a person -- it is a query that
            # can return two people tomorrow.
            (f"https://dblp.org/pid/{ids['dblp_pid']}.html" if ids.get("dblp_pid")
             else f"https://dblp.org/search?q={ids['dblp'].replace(' ', '+')}"),
            f"https://openalex.org/{ids['openalex'][0].rsplit('/', 1)[-1]}",
            f"https://aclanthology.org/people/{ident['name'].lower().replace(' ', '-')}/"]
    if ids.get("linkedin"):
        same.append(f"https://www.linkedin.com/in/{ids['linkedin']}/")
    if ids.get("wikidata"):
        same.append(f"https://www.wikidata.org/wiki/{ids['wikidata']}")
    if ids.get("openreview"):
        same.append(f"https://openreview.net/profile?id={ids['openreview']}")
    # Social profiles, for the same reason as the scholarly ones but a weaker claim:
    # they say the account posting about a paper is its author. Null-skipped, so an
    # unfilled handle costs nothing and a wrong one is never invented.
    same += [u for k in ("bluesky", "mastodon", "twitter")
             if (u := social_url(k, ids.get(k)))]
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
        # Resolved against the site root so config can hold a repo-relative path: the
        # file lives in static/ precisely so it is not a third-party URL that can rot,
        # and schema.org wants an absolute one.
        **({"image": ident["image"] if "//" in ident["image"] else
            ident["canonical_url"].rstrip("/") + "/" + ident["image"].lstrip("/")}
           if ident.get("image") else {}),
        "jobTitle": ident["job_title"],
        "affiliation": [org_ld(a) for a in ident["affiliations"]],
        # Distinct from affiliation for the same reason Wikidata separates P69 from
        # P108: a postdoc is employment, and alumniOf claims a degree. Only entries
        # under identity.education land here.
        "alumniOf": [{"@type": "CollegeOrUniversity", "name": e["institution"]}
                     for e in (ident.get("education") or []) if e.get("institution")],
        # The same list that goes into ORCID's Keywords and Scholar's five interests.
        # knowsAbout is the schema.org field for it, and this is the one surface where
        # we control the markup completely -- so if the phrases are worth choosing at
        # all, leaving them out here is the cheapest omission on the list. It is also
        # the honest place for the full set: Scholar takes five, and the other six say
        # something true about the corpus that would otherwise go unstated anywhere.
        "knowsAbout": list(ident.get("keywords") or []),
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


def faq_jsonld(p: dict, sc: dict, cfg) -> dict | None:
    """The questions block as FAQPage, which is the only part of it a parser can read.

    A sidecar carries up to twenty question groups of up to four phrasings each -- the
    closest thing on the page to the words a reader actually types, and the reason the
    block exists. Rendered as a <dl> it is prose; as FAQPage it is a question with an
    answer attached, which is what a retrieval system indexes and what a summariser
    quotes instead of re-deriving.

    One Question per group rather than per phrasing: the phrasings are the same question
    asked differently, so they belong in alternateName, and duplicating the node once per
    wording would inflate the graph with answers that are byte-identical.
    """
    claims = {c["id"]: c for c in (sc.get("claims") or []) if c.get("id")}
    base = cfg["site"]["base_url"].rstrip("/") + cfg["site"]["papers_path"]
    url = f"{base}/{p['slug']}/"
    entities = []
    for qa in sc.get("qa") or []:
        phrasings = [" ".join(q.split()) for q in (qa.get("q") or []) if q.strip()]
        answers = [claims[cid] for cid in (qa.get("answers") or []) if cid in claims]
        if not phrasings or not answers:
            continue
        # The claim verbatim with its scope, never a paraphrase: the scope is the half
        # that stops the answer being quoted past what the paper supports.
        text = "\n\n".join(f"{' '.join(c['text'].split())} "
                           f"Holds for: {' '.join(c['scope'].split())}" for c in answers)
        node = {"@type": "Question",
                "name": phrasings[0],
                "answerCount": 1,
                "acceptedAnswer": {"@type": "Answer", "text": text, "url": url}}
        if len(phrasings) > 1:
            node["alternateName"] = phrasings[1:]
        entities.append(node)
    if not entities:
        return None
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "@id": f"{url}#faq", "url": url,
            "name": f"Questions answered by {p.get('title_display') or p['title']}",
            "mainEntity": entities}


def terms_jsonld(p: dict, sc: dict, cfg) -> dict | None:
    """Terminology as DefinedTerm, not as a bare Thing.

    These entries exist because a term means something narrower in this paper than in
    the field, and DefinedTermSet is the vocabulary for exactly that -- a definition
    that belongs to a named source rather than a floating label.
    """
    terms = sc.get("terminology") or {}
    if not terms:
        return None
    base = cfg["site"]["base_url"].rstrip("/") + cfg["site"]["papers_path"]
    url = f"{base}/{p['slug']}/"
    return {
        "@context": "https://schema.org", "@type": "DefinedTermSet",
        "@id": f"{url}#terms", "url": url,
        "name": f"Terminology in {p.get('title_display') or p['title']}",
        "hasDefinedTerm": [
            {"@type": "DefinedTerm", "name": t,
             "description": " ".join(str(d).split()),
             "inDefinedTermSet": f"{url}#terms"}
            for t, d in terms.items()],
    }


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
    if venue and not is_preprint_venue(venue):
        tag = ("citation_conference_title"
               if venue_is_conference(venue, p.get("type")) else "citation_journal_title")
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

    # Optional author prose from below the sidecar's front matter. Escaped, not
    # rendered as markdown -- blank lines split paragraphs and nothing else is
    # interpreted, so a stray character in a hand-written note cannot break the page.
    if sc.get("_body"):
        b.append("<h2>Notes from the author</h2>")
        for para in re.split(r"\n\s*\n", sc["_body"].strip()):
            b.append(f"<p>{E(' '.join(para.split()))}</p>")

    if p.get("bibtex"):
        b.append("<h2>How to cite</h2>")
        b.append(f"<pre>{E(p['bibtex'].strip())}</pre>")

    # A literal "References" heading is one of Scholar's PDF-layout fallback cues.
    b.append("<h2>References</h2>")
    b.append(f'<p>See the full reference list in the '
             f'<a href="{E(links.get("html") or links.get("arxiv") or url)}">paper</a>.</p>')

    b.append(f'<footer><a href="{E(cfg["site"]["base_url"])}">{E(ident["name"])}</a> · '
             f'<a href="llms.txt">llms.txt</a><br>{human_note(ident, box=False)}</footer>')

    head = highwire(p, cfg) + jsonld(article_jsonld(p, sc, cfg))
    for extra in (faq_jsonld(p, sc, cfg), terms_jsonld(p, sc, cfg)):
        if extra:
            head += jsonld(extra)
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
    if sc.get("_body"):
        L += ["## Notes from the author", sc["_body"].strip(), ""]
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


def retired_slugs(papers: list[dict]) -> dict[str, str]:
    """Paper URLs a merge retired -> the slug that replaced them.

    A merge is the moment two pages become one, which is the point of the exercise.
    But the alias's URL may already be published, linked and indexed, and GitHub
    Pages has no server-side redirect -- so simply not writing the directory turns a
    consolidation into a 404 and discards whatever standing the old URL had. That is
    the opposite of what a merge is for. A zero-delay meta refresh plus a canonical
    naming the survivor is the redirect a static host can express, and the pair is
    what crawlers read as one; a bare 404 tells them nothing about the successor.

    Derived from the merge record each paper already carries (`merged_from` titles
    resolved through the same slugify the live pages use), never from what happens to
    be deployed: the same inputs have to produce the same site on every rerun.

    A merge is not the only way a URL retires, though, and the others cannot be
    re-derived from anything: correcting a title upstream or improving `slugify` moves
    a page whose old address exists nowhere in the current inputs. `collect.py` records
    those as it makes them, so they are read from disk here and unioned in.
    """
    live = {p["slug"] for p in papers}
    hist = read_yaml(os.path.join(DATA, "slug_history.yaml")) or {}
    out: dict[str, str] = {k: v for k, v in (hist.get("retired") or {}).items()
                           if v in live and k not in live}
    ov = read_yaml(os.path.join(DATA, "overrides.yaml")) or {}
    for group in ov.get("force_merge") or []:
        norms = {norm_title(t) for t in group}
        survivor = next((p for p in papers if norm_title(p.get("title")) in norms), None)
        if not survivor:
            continue
        for t in group:
            s = slugify(t)
            if s and s not in live and s != survivor["slug"]:
                out[s] = survivor["slug"]
    return out


def redirect_stub(site: str, new_slug: str, title: str) -> str:
    """A static-host redirect: refresh + canonical, and a link for anyone without JS."""
    href = f"/papers/{new_slug}/"
    return (f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            f'<meta http-equiv="refresh" content="0; url={href}">\n'
            f'<link rel="canonical" href="{site}/papers/{new_slug}/">\n'
            f'<title>Moved — {E(title)}</title>\n</head>\n<body>\n'
            f'<p>This paper is now at <a href="{href}">{E(title)}</a>.</p>\n'
            f'</body>\n</html>\n')


def build(cfg) -> dict:
    papers = [p for p in (read_yaml(os.path.join(DATA, "papers.yaml")) or {})["papers"]]
    repos = (read_yaml(os.path.join(DATA, "repos.yaml")) or {}).get("repos", [])
    ident = cfg["identity"]
    site = cfg["site"]["base_url"].rstrip("/")
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, ".nojekyll"), "w").close()

    stats = {"pages": 0, "with_sidecar": 0, "peer_owned": 0, "redirects": 0}
    urls = [site + "/", f"{site}/papers/", f"{site}/guides/"]
    index_rows, llms, questions = [], [], []

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
        index_rows.append(
            f'<li><a href="/papers/{E(slug)}/">{E(title)}</a> '
            f'<span class="meta">{E(venue_of(p))}</span></li>')
        llms.append(f"- [{title}]({site}/papers/{slug}/llms.txt)"
                    + (f" — {' '.join(sc['one_liner'].split())}" if sc.get("one_liner") else ""))
        # A question index, collected here so the root file can be matched on the words
        # a reader types rather than on 113 titles. First phrasing only: the rest are the
        # same question, and this file is an index, not the answer.
        for qa in sc.get("qa") or []:
            first = next((" ".join(q.split()) for q in (qa.get("q") or []) if q.strip()), "")
            if first:
                questions.append(f"- {first} — [{title}]({site}/papers/{slug}/llms.txt)")

    # ---- redirects for URLs a merge retired. Deliberately absent from the sitemap
    # and from the index: a sitemap should list only canonical URLs, and a redirect
    # listed as content invites an engine to index the stub instead of the paper.
    by_slug = {p["slug"]: p for p in papers}
    for old, new in retired_slugs(papers).items():
        d = os.path.join(OUT, "papers", old)
        os.makedirs(d, exist_ok=True)
        surv = by_slug.get(new) or {}
        with open(os.path.join(d, "index.html"), "w") as f:
            f.write(redirect_stub(site, new, surv.get("title_display")
                                  or surv.get("title") or "this paper"))
        stats["redirects"] += 1

    # ---- paper index
    with open(os.path.join(OUT, "papers", "index.html"), "w") as f:
        f.write(page(f"Papers — {ident['name']}",
                     f'<h1>Papers</h1>\n<p class="meta">All {stats["pages"] + stats["peer_owned"]} '
                     f'papers, most cited first. <a href="/">The same list by year</a> · '
                     f'<a href="/llms.txt">the same list with a one-line summary of each</a></p>\n'
                     f"<ul>\n{chr(10).join(index_rows)}\n</ul>\n"
                     f'<footer><a href="/">{E(ident["name"])}</a><br>'
                     f'{human_note(ident, box=False)}</footer>',
                     canonical=f"{site}/papers/"))

    # ---- guides: question-shaped content, its own page shape
    guides = [r for r in repos if r.get("kind") == "guide" and not r.get("skip")]
    g = ["<h1>Guides</h1>",
         "<p>Practical guides, each answering one question.</p>", "<ul>"]
    for r in sorted(guides, key=lambda r: r["repo"]):
        u = r.get("homepage") or f"https://github.com/{r['repo']}"
        g.append(f'<li><a href="{E(u)}">{E(r["repo"].split("/")[-1])}</a> — '
                 f'{E(r.get("description") or "")}</li>')
    g += ["</ul>", f'<footer><a href="/">{E(ident["name"])}</a><br>'
                    f'{human_note(ident, box=False)}</footer>']
    os.makedirs(os.path.join(OUT, "guides"), exist_ok=True)
    with open(os.path.join(OUT, "guides", "index.html"), "w") as f:
        f.write(page(f"Guides — {ident['name']}", "\n".join(g),
                     canonical=f"{site}/guides/"))

    # ---- entity home
    home = [f"<h1>{E(ident['name'])}</h1>",
            f'<p class="sub">{E(ident["job_title"])} · '
            f'{E(", ".join(org_name(a) for a in ident["affiliations"]))}</p>']
    # The canonical URL is the machine anchor, so it is the URL in every registry --
    # including the ones a human clicks, like Scholar's Homepage field. That decision
    # is only defensible if the first thing on this page sends a person onward, since
    # otherwise the field that a human follows lands them on a machine-facing index.
    # One link, above the fold, costs the machine anchor nothing and costs the visitor
    # one hop; rel="me" makes it an identity statement too, not just navigation.
    home.append(human_note(ident, box=True))
    home += [f'<p class="meta">ORCID <a rel="me" href="https://orcid.org/{ident["orcid"]}">'
             f'{ident["orcid"]}</a> · <a href="mailto:{E(ident["email"])}">'
             f'{E(ident["email"])}</a></p>',
             f'<p><a href="/papers/">{stats["pages"]} papers</a> · '
             f'<a href="/guides/">{len(guides)} guides</a> · '
             f'<a href="https://github.com/{cfg["ids"]["github"]}">code</a> · '
             f'<a href="/llms.txt">llms.txt</a></p>']
    # rel="me" on every profile we hold. Mastodon reads it to show a verified badge
    # on the profile itself -- a rare case where markup here changes what appears on
    # a surface we do not control -- and IndieAuth consumers read it as the same
    # bidirectional claim that sameAs makes in JSON-LD, for consumers that do not
    # parse JSON-LD.
    rel_me = [u for k in ("bluesky", "mastodon", "twitter", "linkedin", "github")
              if (u := social_url(k, cfg["ids"].get(k)))]
    if rel_me:
        home.append('<p class="meta">'
                    + " · ".join(f'<a rel="me" href="{E(u)}">{E(_host(u))}</a>'
                                 for u in rel_me) + "</p>")
    # Every paper, not a top ten. The readers this page is built for fetch exactly one
    # URL far more often than they crawl: this one, because it is the canonical anchor in
    # ORCID, Scholar, arXiv and every sameAs. A ten-item list left the other 103 papers
    # reachable only by a second hop a single-fetch reader never takes -- and truncation
    # is the one thing on a page this small that has a real cost, since the whole list is
    # 12 KB. Ordered newest-first here and most-cited-first at /papers/, so the two
    # complete lists answer two different questions instead of restating one.
    home.append(f'<h2>Papers</h2><p class="meta">All {len(papers)} papers, newest first. '
                f'<a href="/papers/">The same list by citation count</a> · '
                f'<a href="/llms.txt">the same list with a one-line summary of each</a></p>')
    home += year_sections(papers)
    with open(os.path.join(OUT, "index.html"), "w") as f:
        f.write(page(ident["name"], "\n".join(home),
                     head=jsonld(person_jsonld(cfg)) + verification_meta(cfg),
                     canonical=site + "/"))

    # ---- site llms.txt
    with open(os.path.join(OUT, "llms.txt"), "w") as f:
        f.write(f"""# {ident['name']}

{ident['job_title']} at {', '.join(org_name(a) for a in ident['affiliations'])}.
ORCID {ident['orcid']} · {ident['email']}

Each paper below has a plain-text page stating what it shows, the conditions the
claim holds under, and common misreadings -- written by the author, not extracted.

## Papers
{chr(10).join(llms)}
{f'''
## Questions these papers answer

Each line is a question one of the papers below states an answer to, with the page
that answers it. The answer and the conditions it holds under are on that page.

{chr(10).join(sorted(questions))}
''' if questions else ''}
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

    # ---- IndexNow key file
    write_indexnow_key(cfg)

    stats["static"] = copy_static()
    write_manifest(cfg, papers)
    return stats


def copy_static() -> int:
    """Copy `static/` into the built site verbatim, last, so it wins any collision.

    This exists because a deploy already destroyed something. `--deploy` empties the
    Pages repo before copying `build/site` into it, so anything that got there by hand
    is deleted by the next run: `googlea3fc3aa9969d1cda.html`, the Search Console
    ownership file, was added by hand on 2026-05-08 and removed by the first deploy
    after it. Nothing announces that -- verification lapses silently weeks later, and
    the cause is a commit that looks like every other rebuild.

    A generated HTML tag is still the better verification method where a service offers
    one (`site.verification`), because it needs no file at all. But some services only
    offer a file, and an author will always eventually be asked to host one. So the
    rule is: a file the site must serve that this repo does not generate goes in
    `static/`, and then it is as durable as the generator itself.
    """
    if not os.path.isdir(STATIC):
        return 0
    n = 0
    for root, _, files in os.walk(STATIC):
        rel = os.path.relpath(root, STATIC)
        dst_dir = OUT if rel == "." else os.path.join(OUT, rel)
        os.makedirs(dst_dir, exist_ok=True)
        for name in files:
            if name == ".DS_Store":
                continue
            shutil.copy2(os.path.join(root, name), os.path.join(dst_dir, name))
            n += 1
    return n


def write_indexnow_key(cfg) -> None:
    """The `<key>.txt` file IndexNow requires, generated for the same reason the
    verification tags are: `--deploy` empties the Pages repo, so a file uploaded by
    hand disappears on the next run and every submission afterwards fails with a
    403 that names no cause.

    IndexNow is a push: instead of waiting for a crawler, you tell Bing (and Yandex,
    Seznam, Naver -- Google does not participate) that a URL changed, and it fetches
    within minutes to days. Two reasons it is worth the twenty lines here. Bing's
    index is what ChatGPT's search grounding leans on, so it is the one crawler where
    faster inclusion reaches an answer engine rather than only a search results page.
    And a rebuild that adds thirty paper pages at once is exactly the case organic
    discovery handles worst -- a new sitemap entry on a low-traffic site can wait
    weeks. Nothing about it affects ranking; it affects *when* the page is eligible.
    """
    key = ((cfg.get("site") or {}).get("indexnow_key") or "").strip()
    if not key:
        return
    with open(os.path.join(OUT, f"{key}.txt"), "w") as f:
        f.write(key + "\n")


def submit_indexnow(cfg) -> None:
    """POST the whole sitemap URL list to IndexNow. Called from --deploy only.

    Submitting after the deploy, never before: the endpoint verifies the key file is
    live on the site and rejects the batch otherwise, and a URL submitted before it
    exists is a fetch of a 404. Failures print and return -- this is an optimisation
    on crawl latency, and it must never be able to fail a build.
    """
    site_cfg = cfg.get("site") or {}
    key = (site_cfg.get("indexnow_key") or "").strip()
    if not key:
        print("indexnow: no site.indexnow_key set; skipping "
              "(any 8-128 chars of [A-Za-z0-9-] works -- `python -c \"import uuid; "
              "print(uuid.uuid4().hex)\"`)")
        return
    base = site_cfg["base_url"].rstrip("/")
    sitemap = os.path.join(OUT, "sitemap.xml")
    urls = re.findall(r"<loc>([^<]+)</loc>", open(sitemap).read()) if \
        os.path.exists(sitemap) else []
    if not urls:
        return
    host = re.sub(r"^https?://", "", base).split("/")[0]
    payload = json.dumps({"host": host, "key": key,
                          "keyLocation": f"{base}/{key}.txt",
                          "urlList": urls[:10000]}).encode()
    req = urllib.request.Request("https://api.indexnow.org/IndexNow", data=payload,
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        code = urllib.request.urlopen(req, timeout=30).status
        note_fetch("https://api.indexnow.org/IndexNow", True)
        print(f"indexnow: submitted {len(urls)} URLs (HTTP {code})")
    except Exception as e:
        # 403 means the key file is not reachable yet -- usually Pages has not
        # finished publishing. Harmless once: the next deploy resubmits. Harmless
        # for ever is a different thing, and only the ledger can tell which one this
        # is -- a key file that never became reachable means no deploy has ever been
        # submitted, and the message here reads the same on the first day as on the
        # hundredth.
        note_fetch("https://api.indexnow.org/IndexNow", False)
        print(f"indexnow: not submitted ({e}). Retry after the deploy is live.")


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
    submit_indexnow(cfg)


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
    if s["redirects"]:
        print(f"  redirects from retired URLs   {s['redirects']}")
    if s.get("static"):
        print(f"  files copied from static/     {s['static']}")
    if args.deploy:
        deploy(cfg)


if __name__ == "__main__":
    main()
