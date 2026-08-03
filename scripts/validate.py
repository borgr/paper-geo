#!/usr/bin/env python3
"""Validate data files against schema/*.json.

Runs as the last step of update.py so a malformed hand edit or a bad model
proposal fails loudly rather than propagating into published metadata.

Falls back to a small built-in checker when jsonschema is not installed, so the
pipeline still catches the mistakes that actually happen (wrong type, unknown
field, bad topic format) without adding a hard dependency.

Usage:
    python scripts/validate.py [--strict]
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA, ROOT, read_yaml  # noqa: E402

SCHEMA_DIR = os.path.join(ROOT, "schema")


def load_schema(name: str) -> dict:
    with open(os.path.join(SCHEMA_DIR, f"{name}.schema.json")) as f:
        return json.load(f)


def with_jsonschema(doc, schema, label: str) -> list[str]:
    import jsonschema
    v = jsonschema.Draft202012Validator(schema)
    errs = []
    for e in sorted(v.iter_errors(doc), key=lambda e: list(e.path)):
        where = "/".join(str(x) for x in e.path) or "(root)"
        errs.append(f"{label}: {where}: {e.message}")
    return errs


TOPIC_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,49}$")


def fallback_repos(doc) -> list[str]:
    """The checks that catch real mistakes, without the dependency."""
    schema = load_schema("repos")
    allowed = set(schema["$defs"]["repo"]["properties"])
    kinds = set(schema["$defs"]["repo"]["properties"]["kind"]["enum"])
    errs = []
    seen = set()
    for r in doc.get("repos", []):
        name = r.get("repo", "(no repo field)")
        for k in set(r) - allowed:
            errs.append(f"repos.yaml: {name}: unknown field {k!r}")
        if name in seen:
            errs.append(f"repos.yaml: {name}: duplicate entry")
        seen.add(name)
        if "/" not in str(name):
            errs.append(f"repos.yaml: {name}: repo must be owner/name")
        t = r.get("topics")
        if t is not None:
            if not isinstance(t, list):
                errs.append(f"repos.yaml: {name}: topics must be a list")
            else:
                if len(t) > 8:
                    errs.append(f"repos.yaml: {name}: {len(t)} topics (max 8) -- "
                                "padding a topic list is keyword stuffing")
                if len(set(t)) != len(t):
                    errs.append(f"repos.yaml: {name}: duplicate topics")
                for x in t:
                    if not TOPIC_RE.match(str(x)):
                        errs.append(f"repos.yaml: {name}: invalid topic {x!r} "
                                    "(lowercase, digits, hyphens; <=50 chars)")
        if r.get("kind") and r["kind"] not in kinds:
            errs.append(f"repos.yaml: {name}: kind {r['kind']!r} not in {sorted(kinds)}")
        d = r.get("description")
        if d and len(d) > 160:
            errs.append(f"repos.yaml: {name}: description {len(d)} chars (max 160)")
        if r.get("write_citation_cff") and not r.get("paper_slug"):
            errs.append(f"repos.yaml: {name}: write_citation_cff needs a paper_slug")
    return errs


def fallback_papers(doc) -> list[str]:
    allowed = set(load_schema("papers")["$defs"]["paper"]["properties"])
    errs, seen = [], set()
    for p in doc.get("papers", []):
        slug = p.get("slug", "(no slug)")
        for k in set(p) - allowed:
            errs.append(f"papers.yaml: {slug}: unknown field {k!r}")
        if slug in seen:
            errs.append(f"papers.yaml: {slug}: duplicate slug")
        seen.add(slug)
        if not p.get("title"):
            errs.append(f"papers.yaml: {slug}: no title")
        ax = p.get("arxiv")
        if ax and not re.match(r"^\d{4}\.\d{4,5}$", str(ax)):
            errs.append(f"papers.yaml: {slug}: malformed arxiv id {ax!r}")
    return errs


def check_sidecars() -> list[str]:
    """Cross-check sidecars: valid front matter, and claim ids that resolve."""
    try:
        import yaml
    except ImportError:
        return []
    errs = []
    for path in sorted(glob.glob(os.path.join(DATA, "sidecars", "*.md"))):
        name = os.path.basename(path)
        text = open(path).read()
        m = re.match(r"^---\n(.*?)\n---\n?", text, re.S)
        if not m:
            errs.append(f"{name}: no YAML front matter delimited by ---")
            continue
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError as e:
            errs.append(f"{name}: unparseable front matter: {e}")
            continue
        try:
            import jsonschema
            errs += with_jsonschema(fm, load_schema("sidecar"), name)
        except ImportError:
            for req in ("one_liner", "claims"):
                if not fm.get(req):
                    errs.append(f"{name}: missing required field {req!r}")
        # The check jsonschema cannot do: every qa answer must name a real claim.
        ids = {c.get("id") for c in (fm.get("claims") or []) if isinstance(c, dict)}
        for i, qa in enumerate(fm.get("qa") or []):
            for a in (qa.get("answers") or []):
                if a not in ids:
                    errs.append(f"{name}: qa[{i}] answers unknown claim id {a!r}")
            if not (qa.get("q") or []):
                errs.append(f"{name}: qa[{i}] has no question phrasings")
    return errs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true",
                    help="exit non-zero on any problem (use in CI)")
    args = ap.parse_args()

    have_js = True
    try:
        import jsonschema  # noqa: F401
    except ImportError:
        have_js = False

    errs: list[str] = []
    for name, fname, fb in (("repos", "repos.yaml", fallback_repos),
                            ("papers", "papers.yaml", fallback_papers)):
        doc = read_yaml(os.path.join(DATA, fname))
        if doc is None:
            continue
        errs += (with_jsonschema(doc, load_schema(name), fname) if have_js
                 else fb(doc))
    errs += check_sidecars()

    if not have_js:
        print("note: jsonschema not installed -- using the built-in subset of checks")
    if errs:
        print(f"\n{len(errs)} problem(s):")
        for e in errs[:60]:
            print(f"  {e}")
        if len(errs) > 60:
            print(f"  ... and {len(errs) - 60} more")
        sys.exit(1 if args.strict else 0)
    print("data files valid")


if __name__ == "__main__":
    main()
