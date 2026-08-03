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
