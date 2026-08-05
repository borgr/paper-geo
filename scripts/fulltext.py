#!/usr/bin/env python3
"""Resolve a paper's full text from whatever source actually has it.

The first version of this read one field, `links.html` -- arXiv's LaTeXML rendering,
with ar5iv behind it. That covers 105 of 117 papers and produces nothing at all for the
other 12, so a sidecar for `active-learning-for-bert-an-empirical-study` (244 citations)
was drafted from 1568 characters of metadata while an open-access PDF of the paper sat
one URL away on the ACL Anthology. "No full text" was a property of the code, not of
the paper.

So this is a chain, tried in order, stopping at the first source that returns something
long enough to be a paper:

  0. data/fulltext/<slug>.pdf|.txt   a file you put there yourself
  1. links.html                     arXiv LaTeXML / ar5iv -- real HTML, best text
  2. ACL Anthology PDF              from links.acl_anthology, or derived from a
                                    10.18653/... DOI
  3. links.arxiv_pdf                when the HTML rendering is missing or a stub
  4. Unpaywall best_oa_location     the OA aggregator publishers report to
  5. Semantic Scholar openAccessPdf a second aggregator, different coverage
  6. Europe PMC full text           for the biomedical-indexed ones
  7. OpenReview PDF                 last, because it 403s every non-browser client
                                    (checked: any UA, no cookie). Kept in the chain
                                    anyway -- it costs one request that is not
                                    retried, it is the only source for a few
                                    workshop papers, and the block is theirs to
                                    lift, not a bug here.

Local first on purpose. A file in `data/fulltext/` is a deliberate act: it means the
public chain came up short and the author, who holds the PDF, decided to supply it.
That directory is gitignored -- a publisher PDF is not ours to redistribute, and what
gets published from it is a distillation, never the text.

Why so many sources rather than one good one: each covers a different slice, and the
slices are the shape of one person's corpus. ACL Anthology has the *ACL papers and
nothing else. Unpaywall knows what publishers have deposited and misses preprints in
odd places. Semantic Scholar's crawler finds PDFs Unpaywall has no record of. Europe
PMC has the Nature paper's abstract that nobody else exposes. Any single one of them
leaves a hole, and a hole here means a sidecar drafted from a title.

Two entry points:

    resolve(p)           -> (text, source_label)   cached under build/fulltext/
    resolve_abstract(p)  -> (abstract, source)     for records with no abstract at all

    python scripts/fulltext.py --report          what each paper's text came from
    python scripts/fulltext.py --slug S --show   resolve one, print the first lines
"""
from __future__ import annotations

import argparse
import html as _html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import (BUILD, DATA, get, get_json, load_config, paper_doi,  # noqa: E402
                   read_yaml)

CACHE = os.path.join(BUILD, "fulltext")
LOCAL = os.path.join(DATA, "fulltext")
INDEX = os.path.join(CACHE, "sources.json")

# Below this, HTML that came back is not a paper: arXiv answers a request for an
# unrendered id with a stub page rather than a 404, and a paywalled DOI resolves to a
# landing page. Length is the only signal the two share, and a short abstract-only text
# is worse than useless because it reads like success while silently capping every
# claim's evidence.
MIN_CHARS = 4000

# A PDF is held to a much lower bar, because the stub problem is specific to HTML: a
# response whose first bytes are %PDF- *is* the document, so a short one is a short
# paper, not a failure. Two-page shared-task calls and workshop reports are exactly the
# records that were coming back empty under one shared threshold. Below this even a real
# PDF is a title page or a scan that extracted nothing.
MIN_PDF_CHARS = 1200


# --------------------------------------------------------------- text extraction

_TAG = re.compile(r"<(script|style)\b.*?</\1>|<[^>]+>", re.S | re.I)
_WS = re.compile(r"[ \t\r\f\v]+")


def html_to_text(raw: bytes) -> str:
    """Crude HTML -> text. Enough for a model, and it adds no dependency.

    Block tags become newlines before tags are stripped, because the alternative runs a
    table caption into the sentence after it and the model then attributes a number to
    the wrong result.
    """
    s = raw.decode("utf-8", "replace")
    s = re.sub(r"(?i)</(p|div|li|tr|h[1-6]|figcaption|caption|section)>", "\n", s)
    s = re.sub(r"(?i)<br\s*/?>", "\n", s)
    s = _TAG.sub(" ", s)
    s = _html.unescape(s)
    s = _WS.sub(" ", s)
    return re.sub(r"\n\s*\n+", "\n\n", s).strip()


def _pdftotext() -> str | None:
    """poppler's pdftotext if it is installed. Not a dependency, just preferred.

    It keeps reading order and column layout far better than the pure-Python readers,
    which matters for exactly the content we are here for: a two-column results table
    extracted in the wrong order pairs each number with its neighbour's row label.
    """
    return shutil.which("pdftotext") or next(
        (c for c in ("/opt/homebrew/bin/pdftotext", "/usr/local/bin/pdftotext",
                     "/usr/bin/pdftotext") if os.path.exists(c)), None)


def pdf_to_text(raw: bytes) -> str:
    """PDF bytes -> text, via pdftotext if present, else pypdf, else nothing.

    Deliberately no hard dependency. A missing extractor degrades this source to
    "unavailable" and the chain moves on, which is the same outcome as a 404 -- while a
    `pip install` in the middle of a rerun is a failure the whole pipeline stops for.
    """
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "paper.pdf")
        with open(src, "wb") as f:
            f.write(raw)
        exe = _pdftotext()
        if exe:
            out = os.path.join(d, "paper.txt")
            try:
                subprocess.run([exe, "-q", "-nopgbrk", src, out],
                               check=True, timeout=180,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                with open(out, errors="replace") as f:
                    return clean_pdf_text(f.read())
            except Exception:
                pass
        try:
            import pypdf
            r = pypdf.PdfReader(src)
            return clean_pdf_text("\n".join(
                (pg.extract_text() or "") for pg in r.pages))
        except Exception:
            return ""


_HYPHEN_BREAK = re.compile(r"(\w)-\n(\w)")


def clean_pdf_text(s: str) -> str:
    """Undo the two artefacts of PDF extraction that change meaning, not just looks.

    Line-end hyphenation is the one that matters: `evalu-\\nation` left as-is becomes two
    tokens, so a search for the term inside the paper misses, and a model quoting the
    sentence reproduces the break. The rest is whitespace.
    """
    s = s.replace("\x0c", "\n\n")
    s = _HYPHEN_BREAK.sub(r"\1\2", s)
    s = _WS.sub(" ", s)
    return re.sub(r"\n\s*\n+", "\n\n", s).strip()


_REFS = re.compile(r"^\s*(references|bibliography)\s*$", re.I | re.M)


def drop_references(s: str) -> str:
    """Cut the bibliography, which is the largest block of numbers that are not ours.

    Worth doing beyond saving budget: a truncation limit spent on other people's titles
    is a limit not spent on the appendix tables, and a model reading a reference list
    can attribute a cited paper's result to this one.

    Only a heading in the last 40% counts, so a paper that says "References" in an
    early section title does not get beheaded.
    """
    hits = [m.start() for m in _REFS.finditer(s) if m.start() > len(s) * 0.6]
    return s[:hits[-1]].rstrip() if hits else s


# --------------------------------------------------------------- source chain

def _anthology_id(p: dict, doi: str | None) -> str | None:
    """The Anthology paper id, from the link if we have it or from the ACL DOI if not.

    Both spellings appear in the corpus, and the DOI fallback is not a nicety: the third
    BabyLM findings paper has `10.18653/v1/2025.babylm-main.28` and no anthology link,
    which is the whole paper reachable from a field we already store.
    """
    url = (p.get("links") or {}).get("acl_anthology")
    if url:
        return url.rstrip("/").split("/")[-1].removesuffix(".pdf")
    if doi and doi.lower().startswith("10.18653/v1/"):
        return doi.split("/", 2)[2]
    return None


def _openreview_id(p: dict) -> str | None:
    for url in ((p.get("links") or {}).get("publisher"), p.get("url")):
        m = re.search(r"openreview\.net/(?:forum|pdf)\?id=([\w-]+)", url or "")
        if m:
            return m.group(1)
    return None


def _unpaywall_pdf(doi: str, email: str) -> str | None:
    """Unpaywall's own best guess at where the free copy is.

    The email is required by the API and is not a credential -- it is the same address
    printed on every one of these papers, and it exists so a maintainer can be told
    when a client misbehaves.
    """
    d = get_json(f"https://api.unpaywall.org/v2/{doi}?email={email}", retries=3)
    if not isinstance(d, dict):
        return None
    locs = [d.get("best_oa_location")] + list(d.get("oa_locations") or [])
    for loc in locs:
        if isinstance(loc, dict):
            u = loc.get("url_for_pdf") or (
                loc.get("url") if str(loc.get("url") or "").endswith(".pdf") else None)
            if u:
                return u
    return None


def _s2_keys(p: dict, doi: str | None) -> list[str]:
    """Every way to name this paper to Semantic Scholar, most specific first.

    The bare paper id matters more than it looks: the records with no DOI and no arXiv id
    are precisely the ones the rest of the chain cannot reach, and for several of them an
    S2 id is the only identifier we hold. Never a title search -- a fuzzy hit here would
    attach a stranger's paper to his page.
    """
    s2 = (p.get("links") or {}).get("semantic_scholar", "").rstrip("/").split("/")[-1]
    return ([f"DOI:{doi}"] if doi else []) \
        + ([f"arXiv:{p['arxiv']}"] if p.get("arxiv") else []) \
        + ([s2] if s2.isdigit() else [])


def _s2_pdf(p: dict, doi: str | None) -> str | None:
    for key in _s2_keys(p, doi):
        d = get_json(f"https://api.semanticscholar.org/graph/v1/paper/{key}"
                     f"?fields=openAccessPdf", retries=3)
        url = ((d or {}).get("openAccessPdf") or {}).get("url") \
            if isinstance(d, dict) else None
        if url:
            return url
    return None


def _epmc_record(doi: str) -> dict | None:
    """Europe PMC's record for a DOI. Holds the abstract even when the text is closed."""
    d = get_json("https://www.ebi.ac.uk/europepmc/webservices/rest/search"
                 f'?query=DOI:"{doi}"&format=json&resultType=core&pageSize=1',
                 retries=3)
    hits = ((d or {}).get("resultList") or {}).get("result") or []
    return hits[0] if hits else None


def _candidates(p: dict, cfg: dict):
    """(name, kind, url) for every place this paper's text might be, best first.

    A generator, and that is load-bearing: the API lookups happen only when the
    consumer asks for the next candidate, so a paper whose arXiv HTML renders costs
    zero requests to Unpaywall, Semantic Scholar and Europe PMC.
    """
    L = p.get("links") or {}
    doi = paper_doi(p)
    email = ((cfg.get("identity") or {}).get("email") or "").strip()

    if L.get("html"):
        yield ("arxiv-html", "html", L["html"])
    aid = _anthology_id(p, doi)
    if aid:
        yield ("acl-anthology", "pdf", f"https://aclanthology.org/{aid}.pdf")
    if L.get("arxiv_pdf"):
        yield ("arxiv-pdf", "pdf", L["arxiv_pdf"])
    if p.get("arxiv"):
        # The versionless PDF path 404s for some older ids while `...v1` serves fine
        # (1805.12386 is one: 404 unversioned, 200 at v1). Only reached after the
        # unversioned URL has already failed, so it costs nothing normally -- and when it
        # does fire, v1 may be an earlier version than the record describes, which is
        # still a better basis for a claim than the title alone.
        yield ("arxiv-pdf-v1", "pdf", f"https://arxiv.org/pdf/{p['arxiv']}v1")
    if doi and email:
        u = _unpaywall_pdf(doi, email)
        if u:
            yield ("unpaywall", "pdf", u)
    u = _s2_pdf(p, doi)
    if u:
        yield ("semantic-scholar", "pdf", u)
    if doi:
        rec = _epmc_record(doi)
        if rec and rec.get("inEPMC") == "Y" and rec.get("pmcid"):
            yield ("europe-pmc", "html",
                   "https://www.ebi.ac.uk/europepmc/webservices/rest/"
                   f"{rec['pmcid']}/fullTextXML")
    orid = _openreview_id(p)
    if orid:
        yield ("openreview", "pdf", f"https://openreview.net/pdf?id={orid}")


def _local(slug: str) -> tuple[str, str] | None:
    for ext in ("txt", "md", "pdf"):
        path = os.path.join(LOCAL, f"{slug}.{ext}")
        if not os.path.exists(path):
            continue
        with open(path, "rb") as f:
            raw = f.read()
        text = pdf_to_text(raw) if ext == "pdf" else raw.decode("utf-8", "replace")
        if text.strip():
            return text, f"data/fulltext/{slug}.{ext}"
    return None


def _fetch(kind: str, url: str) -> tuple[str, int]:
    """(text, the length it has to clear). The threshold travels with the response.

    Decided by the magic bytes rather than by the URL: a `.pdf` link that answers with a
    Cloudflare interstitial must be judged as the HTML it is, and a DOI that redirects to
    a real PDF gets the PDF's lower bar.
    """
    raw = get(url, timeout=90, retries=3)
    if not raw:
        return "", MIN_CHARS
    if raw[:5] == b"%PDF-":
        return pdf_to_text(raw), MIN_PDF_CHARS
    return html_to_text(raw), MIN_CHARS


# --------------------------------------------------------------- cache

def _read_json(path: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return {}


def _remember(slug: str, source: str, chars: int) -> None:
    os.makedirs(CACHE, exist_ok=True)
    idx = _read_json(INDEX)
    idx[slug] = {"source": source, "chars": chars}
    with open(INDEX, "w") as f:
        json.dump(idx, f, indent=1, sort_keys=True)


def source_of(slug: str) -> str:
    return (_read_json(INDEX).get(slug) or {}).get("source") or "(unrecorded)"


NONE = "(none found)"


def found(source: str) -> bool:
    """Did the chain actually land somewhere? The recorded source, not the length.

    Length stopped being the test once PDFs got their own threshold: a real two-page
    shared-task call is shorter than an arXiv stub page, so `chars` can no longer tell
    success from failure. What can is the name of the source that answered.
    """
    return bool(source) and source not in (NONE, "(unrecorded)")


def resolve(p: dict, cfg: dict | None = None, limit: int = 60000,
            refetch: bool = False, quiet: bool = True) -> tuple[str, str]:
    """(text, where it came from) for one paper. Cached under build/fulltext/<slug>.txt.

    Cached because a re-draft after a prompt change must not re-download 117 papers, and
    because arXiv asks for exactly that restraint. A cached *failure* is not honoured:
    the old code wrote an empty file when a fetch failed and then returned it forever, so
    every later run skipped the paper it had learned nothing about. A miss is retried,
    which is what lets a source added today fix a paper that came up empty yesterday.

    Truncated at the end: front matter and results are what matter, and the references
    are already gone.
    """
    cfg = cfg or load_config()
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f"{p['slug']}.txt")
    if os.path.exists(path) and not refetch:
        with open(path) as f:
            cached = f.read()
        src = source_of(p["slug"])
        # Long-and-unattributed is honoured too, for the caches written before this file
        # recorded a source. Re-fetching 105 papers to learn what we already have would
        # be the rude version of a migration -- and the attribution is not a guess: the
        # implementation that wrote those files could read one field and no other, so a
        # long cache with no recorded source came from links.html. Labelled `inferred`
        # regardless, because a reader should be able to tell a reconstruction from a
        # fetch that actually happened.
        if cached and len(cached) >= MIN_CHARS and not found(src):
            url = (p.get("links") or {}).get("html")
            src = f"arxiv-html {url} (inferred)" if url else "(unrecorded)"
            _remember(p["slug"], src, len(cached))
        if cached and (found(src) or len(cached) >= MIN_CHARS):
            return cached[:limit], src

    got = _local(p["slug"])
    if got:
        text, source = got
    else:
        text, source = "", ""
        for name, kind, url in _candidates(p, cfg):
            if not quiet:
                print(f"    try {name}: {url}", file=sys.stderr)
            cand, floor = _fetch(kind, url)
            cand = drop_references(cand)
            if len(cand) >= floor:
                text, source = cand, f"{name} {url}"
                break

    with open(path, "w") as f:
        f.write(text)
    _remember(p["slug"], source or NONE, len(text))
    return text[:limit], source or NONE


# --------------------------------------------------------------- abstracts

def _strip_jats(s: str) -> str:
    s = re.sub(r"(?i)<(title|h\d)[^>]*>\s*abstract\s*</\1>", " ", s or "")
    return _WS.sub(" ", _html.unescape(_TAG.sub(" ", s))).strip()


def resolve_abstract(p: dict) -> tuple[str, str] | None:
    """An abstract for a record that has none, from the metadata APIs.

    Separate from `resolve` because it answers a different question and has a different
    bar. `collect.py` gets abstracts from arXiv, which leaves the never-preprinted
    papers empty -- and an empty abstract is close to unretrievable in embedding search
    and makes the paper's own page thin enough that Scholar may not index it. The Nature
    debating-system paper is the case: no OA full text anywhere legitimate, but Europe
    PMC publishes the abstract, and Crossref has it as JATS.
    """
    doi = paper_doi(p)
    # An id we already hold, never a title search. A fuzzy title match here would
    # publish another paper's abstract on his page, which is the one error in this file
    # that is worse than the empty field it fixes.
    for key in _s2_keys(p, doi):
        d = get_json("https://api.semanticscholar.org/graph/v1/paper/"
                     f"{key}?fields=abstract", retries=3)
        if isinstance(d, dict) and (d.get("abstract") or "").strip():
            return " ".join(d["abstract"].split()), "semantic-scholar"
    if not doi:
        return None
    rec = _epmc_record(doi)
    if rec and (rec.get("abstractText") or "").strip():
        return _strip_jats(rec["abstractText"]), "europe-pmc"
    d = get_json(f"https://api.crossref.org/works/{doi}", retries=3)
    abst = ((d or {}).get("message") or {}).get("abstract")
    if abst:
        return _strip_jats(abst), "crossref"
    oa = get_json(f"https://api.openalex.org/works/doi:{doi}", retries=3)
    inv = (oa or {}).get("abstract_inverted_index")
    if isinstance(inv, dict) and inv:
        # OpenAlex ships abstracts word -> [positions] to sidestep redistribution
        # limits. Inverting it back is lossless for our purposes and is what every
        # client does.
        words = sorted(((i, w) for w, ps in inv.items() for i in ps))
        return " ".join(w for _, w in words), "openalex"
    return None


# --------------------------------------------------------------- cli

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--report", action="store_true",
                    help="one line per paper: chars and where the text came from")
    ap.add_argument("--slug", nargs="+", help="resolve exactly these papers")
    ap.add_argument("--refetch", action="store_true", help="ignore the cache")
    ap.add_argument("--show", type=int, default=0, metavar="N",
                    help="print the first N characters of each resolved text")
    ap.add_argument("--abstracts", action="store_true",
                    help="show what resolve_abstract() finds for records with none")
    args = ap.parse_args()

    cfg = load_config()
    papers = (read_yaml(os.path.join(DATA, "papers.yaml")) or {}).get("papers", [])
    by_slug = {p["slug"]: p for p in papers}

    if args.abstracts:
        for p in papers:
            if (p.get("abstract") or "").strip():
                continue
            got = resolve_abstract(p)
            print(f"{p['slug']}\n  "
                  + (f"{got[1]}: {got[0][:200]}..." if got else "(nothing)"))
        return

    todo = ([by_slug[s] for s in args.slug if s in by_slug] if args.slug
            else sorted(papers, key=lambda q: -(q.get("citations") or 0)))
    if args.report and not args.slug:
        print(f"{'chars':>7}  {'source':<18} slug")
    missing = []
    for p in todo:
        text, source = resolve(p, cfg, refetch=args.refetch,
                               quiet=not (args.slug or args.show))
        if not found(source):
            missing.append(p["slug"])
        print(f"{len(text):>7}  {source.split()[0][:18]:<18} {p['slug']}")
        if args.show:
            print("  | " + "\n  | ".join(text[:args.show].splitlines()[:40]))
    print(f"\n{len(todo) - len(missing)}/{len(todo)} papers resolved to a text",
          file=sys.stderr)
    if missing:
        print("No open copy found for:", file=sys.stderr)
        for slug in missing:
            print(f"  {slug}", file=sys.stderr)
        print("Put the PDF at data/fulltext/<slug>.pdf (gitignored) and rerun.",
              file=sys.stderr)


if __name__ == "__main__":
    main()
