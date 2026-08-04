"""Shared utilities: config loading, polite HTTP, BibTeX parsing, title matching."""
from __future__ import annotations

import json
import os
import re
import time
import unicodedata
import urllib.error
import urllib.request

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
BUILD = os.path.join(ROOT, "build")
UA = {"User-Agent": "paper-geo/0.1 (+https://github.com/borgr/paper-geo)"}


def load_config(path: str | None = None) -> dict:
    with open(path or os.path.join(ROOT, "config.yaml")) as f:
        return yaml.safe_load(f)


def get(url: str, timeout: int = 40, retries: int = 6, accept: str | None = None) -> bytes:
    """GET with exponential backoff on 429/503. Returns b'' on final failure."""
    headers = dict(UA)
    if accept:
        headers["Accept"] = accept
    delay = 4.0
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            return urllib.request.urlopen(req, timeout=timeout).read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < retries - 1:
                time.sleep(delay)
                delay *= 2
                continue
            return b""
        except Exception:
            if attempt < retries - 1:
                time.sleep(delay)
                delay *= 2
                continue
            return b""
    return b""


def get_json(url: str, **kw) -> dict | list | None:
    raw = get(url, accept="application/json", **kw)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


# ---------------------------------------------------------------- BibTeX

_ENTRY = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", re.M)


def _split_entries(text: str) -> list[tuple[str, str, str, str]]:
    """Yield (type, key, body, raw) by brace-matching from each @type{key, header.

    `raw` is the verbatim entry text. We publish that byte-for-byte rather than
    regenerating BibTeX from parsed fields: a regenerated citation key would
    differ from the one people have already cited, and one canonical citation
    string everywhere is worth more than a tidier one.
    """
    out = []
    for m in _ENTRY.finditer(text):
        depth, i = 1, m.end()
        while i < len(text) and depth:
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
            i += 1
        out.append((m.group(1).lower(), m.group(2), text[m.end():i - 1],
                    text[m.start():i]))
    return out


_FIELD = re.compile(r"(\w+)\s*=\s*", re.M)


def _parse_fields(body: str) -> dict:
    """Parse `field = {value}` / `field = "value"` / `field = bareword`."""
    fields, pos = {}, 0
    while True:
        m = _FIELD.search(body, pos)
        if not m:
            break
        name, i = m.group(1).lower(), m.end()
        while i < len(body) and body[i].isspace():
            i += 1
        if i >= len(body):
            break
        if body[i] == "{":
            depth, j = 1, i + 1
            while j < len(body) and depth:
                if body[j] == "{":
                    depth += 1
                elif body[j] == "}":
                    depth -= 1
                j += 1
            val, pos = body[i + 1:j - 1], j
        elif body[i] == '"':
            j = i + 1
            while j < len(body) and body[j] != '"':
                j += 2 if body[j] == "\\" else 1
            val, pos = body[i + 1:j], j + 1
        else:
            j = i
            while j < len(body) and body[j] not in ",\n":
                j += 1
            val, pos = body[i:j], j
        fields[name] = " ".join(val.split())
    return fields


def parse_bibtex(text: str) -> list[dict]:
    """Return [{key, type, raw, <fields>}] for every entry."""
    entries = []
    for etype, key, body, raw in _split_entries(text):
        e = _parse_fields(body)
        e["key"], e["type"], e["raw"] = key, etype, raw
        entries.append(e)
    return entries


# ---------------------------------------------------------------- matching

_LATEX = re.compile(r"\\[a-zA-Z]+\s*|[{}$\\]")
_NONWORD = re.compile(r"[^a-z0-9]+")


def norm_title(s: str | None) -> str:
    """Aggressive normalization for cross-source title matching."""
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = _LATEX.sub(" ", s).lower()
    return _NONWORD.sub("", s)


def split_authors(bibtex_author: str | None) -> list[str]:
    """`Last, First and Other, Name` -> ['First Last', 'Name Other']."""
    if not bibtex_author:
        return []
    out = []
    for a in re.split(r"\s+and\s+", bibtex_author):
        a = " ".join(a.replace("{", "").replace("}", "").split())
        if "," in a:
            last, _, first = a.partition(",")
            a = f"{first.strip()} {last.strip()}".strip()
        if a:
            out.append(a)
    return out


# Every external id we hold, mapped to the Wikidata property that is *typed* for it.
#
# The point of the table is that none of these belong in `official website` (P856).
# P856 takes exactly one value -- the canonical URL -- and a profile URL dropped in
# beside it does not become queryable, it just adds a second candidate homepage. The
# typed property is strictly better: it renders as a link anyway, it is validated
# against a format constraint, tools like Scholia and Author Disambiguator traverse
# it, and a SPARQL query can hop from the id to the record. So "should arXiv go in
# too?" resolves to: yes, but as an identifier, and only where a property exists.
#
# arXiv is the instructive exception. P4594 exists but its format is the *legacy*
# author id (`choshen_l_1`); neither plausible legacy id resolves for this account,
# because arXiv's current author identity is the ORCID link. P496 already carries it,
# and arxiv.org/a/<orcid> is derived from that -- so there is nothing to add.
WD_IDENTIFIERS = [
    ("P496", "ORCID iD", lambda c: c["identity"]["orcid"]),
    ("P1960", "Google Scholar author ID", lambda c: c["ids"]["google_scholar"]),
    ("P4012", "Semantic Scholar author ID", lambda c: c["ids"]["semantic_scholar_primary"]),
    ("P10283", "OpenAlex ID", lambda c: (c["ids"]["openalex"] or [None])[0]),
    ("P2456", "DBLP author ID", lambda c: (c["ids"]["dblp"] or "").replace(" ", "_")),
    ("P2037", "GitHub username", lambda c: c["ids"]["github"]),
    ("P12201", "Hugging Face user ID", lambda c: c["ids"].get("huggingface")),
    ("P6634", "LinkedIn personal profile ID", lambda c: c["ids"].get("linkedin")),
    ("P8964", "OpenReview.net profile ID", lambda c: c["ids"].get("openreview")),
    ("P856", "official website", lambda c: c["identity"]["canonical_url"]),
]


def norm_name(s: str) -> str:
    """Fold a personal name for comparison: accents, punctuation, case, spacing."""
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return " ".join(re.sub(r"[^\w\s]", " ", s).lower().split())


def name_match(candidate: str, variants) -> str:
    """Classify an author string against your known name forms.

    Returns "exact", "near", or "" — and the middle value is the one that earns this
    function's existence. Two of these papers carry "Leshem Chosen" in the *arXiv*
    metadata, one character off, which means every index built from arXiv metadata
    files them under a person who does not otherwise exist. That is not a cosmetic
    typo: it is an identity split, and it is invisible to an exact-match check, which
    reports the author as simply absent and sends you looking for the wrong problem.

    "near" is deliberately narrow -- same first name and a surname within one or two
    characters, or a whole-string similarity above .88. A looser rule starts matching
    genuine other people, and a false "that is you" is worse here than a miss.
    """
    import difflib

    c = norm_name(candidate)
    if not c:
        return ""
    for v in variants:
        n = norm_name(v)
        if not n:
            continue
        if c == n:
            return "exact"
        # "Choshen, Leshem" vs "Leshem Choshen": order carries no information here.
        if sorted(c.split()) == sorted(n.split()):
            return "exact"
        cp, np_ = c.split(), n.split()
        if cp and np_ and cp[0] == np_[0] and cp[-1] != np_[-1]:
            r = difflib.SequenceMatcher(None, cp[-1], np_[-1]).ratio()
            if r >= 0.8 and abs(len(cp[-1]) - len(np_[-1])) <= 2:
                return "near"
        if difflib.SequenceMatcher(None, c, n).ratio() >= 0.88:
            return "near"
    return ""


def arxiv_id(entry: dict) -> str | None:
    """Extract a bare arXiv id from eprint / url / doi fields."""
    if entry.get("eprint") and (entry.get("eprinttype", "arxiv").lower() == "arxiv"
                                or entry.get("archiveprefix", "").lower() == "arxiv"):
        return entry["eprint"].split("v")[0]
    for field in ("url", "doi", "note"):
        v = entry.get(field) or ""
        m = re.search(r"(?:arxiv\.org/(?:abs|pdf)/|arXiv[.:]|arXiv\.)(\d{4}\.\d{4,5})", v, re.I)
        if m:
            return m.group(1)
    return None


def paper_doi(p: dict) -> str | None:
    """The best DOI for a paper, falling back to its arXiv DataCite DOI.

    arXiv registers a DataCite DOI for every paper at 10.48550/arXiv.<id>, including
    the oldest ids. That matters well beyond tidiness: ORCID *groups* works that share
    an identifier, so an entry carrying a DOI merges with the registry-sourced copy
    instead of becoming a second record, and "Add DOI" can only resolve an entry that
    has one. A paper with no DOI anywhere is the only kind that can duplicate.

    Preference order is publisher DOI, then whatever DOI the author registered with
    arXiv, then the arXiv DOI itself -- most specific claim first.
    """
    if p.get("doi"):
        return p["doi"]
    if p.get("arxiv_doi"):
        return p["arxiv_doi"]
    return f"10.48550/arXiv.{p['arxiv']}" if p.get("arxiv") else None


_MATH = {r"\({}^{\mbox{2}}\)": "\u00b2", r"\({}^{\mbox{3}}\)": "\u00b3",
         r"$^2$": "\u00b2", r"$^3$": "\u00b3", "{ extdollar}": "$"}


def clean_latex(s: str | None) -> str:
    """Human-readable text from a BibTeX field.

    Titles arrive with protective braces ({DORA}), math wrappers, and escaped
    ampersands. Leaving those in means they show up in the page heading, the
    highwire citation_title, and the JSON-LD -- i.e. in exactly the fields Scholar
    matches on. The raw form is still published verbatim in the BibTeX block, so
    nothing is lost by cleaning the display copy.
    """
    if not s:
        return ""
    for k, v in _MATH.items():
        s = s.replace(k, v)
    s = re.sub(r"\\[a-zA-Z]+\{([^{}]*)\}", r"\1", s)   # \emph{x} -> x
    s = re.sub(r"\\[a-zA-Z]+\s?", "", s)                # stray \command
    s = s.replace("{", "").replace("}", "")
    s = s.replace("\\&", "&").replace("\\_", "_").replace("\\%", "%").replace("$", "")
    return " ".join(s.split())


def short_venue(v: str | None, limit: int = 110) -> str:
    """Trim a venue at a word boundary, never mid-word."""
    v = clean_latex(v)
    if len(v) <= limit:
        return v
    cut = v[:limit].rsplit(" ", 1)[0].rstrip(" ,;:-")
    return cut + "\u2026"


def clean_bibtex(raw: str | None) -> str:
    """Published BibTeX: verbatim, minus fields that only work in one person's build.

    `pretitle={\COL\META}` is a private macro from the source bibliography's own
    CV template. Publishing it verbatim hands readers an entry that fails to
    compile, which defeats the point of publishing a citation at all. Everything
    else -- crucially the citation key -- is untouched.
    """
    if not raw:
        return ""
    out = re.sub(r"^\s*pretitle\s*=\s*\{[^{}]*\}\s*,?\s*\n?", "", raw,
                 flags=re.M)
    return re.sub(r"\n\s*\n+", "\n", out).strip()


def slugify(s: str, maxlen: int = 60) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = _LATEX.sub(" ", s).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:maxlen].rstrip("-")


def write_yaml(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        yaml.safe_dump(obj, f, sort_keys=False, allow_unicode=True, width=100)


def read_yaml(path: str, default=None):
    if not os.path.exists(path):
        return default
    with open(path) as f:
        return yaml.safe_load(f)
