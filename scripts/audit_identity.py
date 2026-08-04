#!/usr/bin/env python3
"""Audit the identity surfaces you do not control, against what they should say.

Everything else in this repo checks *our* artifacts. This checks the five external
surfaces that decide whether a retrieval system can resolve you to one person, by
reading their public APIs -- no login, no key, read-only:

    ORCID          public works count, researcher URLs, name variants, keywords
    arXiv          which papers your account is actually registered as author on
    Wikidata       whether an author item carrying your ORCID exists yet
    Hugging Face   which paper pages exist, and which you have claimed
    Semantic Sch.  how the corpus is split across author records

The arXiv check is the one worth the network round-trip. Linking ORCID to arXiv
gives you a public list at arxiv.org/a/<orcid> built from arXiv's *authority
records* -- papers your account is registered as an author on. For a co-authored
corpus that is usually a fraction of your papers, and it is also the gate on
editing them: you cannot add a journal-ref to a paper you do not own. So this
diff is a prerequisite list, not a vanity metric.

Writes tasks/identity_audit.md and tasks/arxiv_ownership.md.

Usage:
    python scripts/audit_identity.py             # everything (~40s, HF dominates)
    python scripts/audit_identity.py --no-hf     # skip the per-paper HF checks
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import BUILD, DATA, ROOT, get, get_json, load_config, read_yaml  # noqa: E402

TASKS = os.path.join(ROOT, "tasks")
ATOM = {"a": "http://www.w3.org/2005/Atom"}
_ABS = re.compile(r"abs/([0-9]{4}\.[0-9]{4,5}|[a-z\-]+/[0-9]{7})")


def orcid_public(orcid: str) -> dict:
    """Read the public ORCID record.

    The public API is what Semantic Scholar, OpenAlex and Crossref see. An item
    whose visibility is "trusted parties" is invisible here -- so a works count of
    0 does not distinguish "empty" from "private", and both fail identically.
    """
    d = get_json(f"https://pub.orcid.org/v3.0/{orcid}/record") or {}
    act, person = d.get("activities-summary") or {}, d.get("person") or {}
    urls = [(u.get("url-name"), (u.get("url") or {}).get("value"))
            for u in ((person.get("researcher-urls") or {}).get("researcher-url") or [])]
    return {
        "works": len((act.get("works") or {}).get("group") or []),
        "employments": len((act.get("employments") or {}).get("affiliation-group") or []),
        "educations": len((act.get("educations") or {}).get("affiliation-group") or []),
        "urls": urls,
        "other_names": [n.get("content") for n in
                        ((person.get("other-names") or {}).get("other-name") or [])],
        "keywords": [k.get("content") for k in
                     ((person.get("keywords") or {}).get("keyword") or [])],
        "biography": bool(person.get("biography")),
        "reachable": bool(d),
    }


def arxiv_registered(orcid: str) -> set[str] | None:
    """arXiv ids your account is registered as an author on.

    Read from the Atom flavour of arxiv.org/a/<orcid>: the HTML page 303-redirects
    and is JS-free, but the feed is the parseable one. None means the page does not
    exist yet, which happens when the ORCID is not linked to an arXiv account.
    """
    raw = get(f"https://arxiv.org/a/{orcid}.atom2", retries=2)
    if not raw:
        return None
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        # An unlinked ORCID serves the arXiv 404 page, which is HTML, not Atom.
        return None
    out = set()
    for e in root.findall("a:entry", ATOM):
        m = _ABS.search((e.findtext("a:id", "", ATOM) or ""))
        if m:
            out.add(m.group(1))
    return out


def wikidata_item(cfg) -> str | None:
    """Find an author item by any identifier we already know, not by name.

    Name search on Wikidata returns paper items that merely mention you, which is
    the failure mode that made this look done once already. Statement search is
    exact: either an item claims the identifier or none does.
    """
    ident, ids = cfg["identity"], cfg["ids"]
    probes = [("P496", ident["orcid"]), ("P4012", ids["semantic_scholar_primary"]),
              ("P1960", ids["google_scholar"]), ("P2037", ids["github"])]
    for prop, val in probes:
        q = quote(f'haswbstatement:"{prop}={val}"')
        j = get_json("https://www.wikidata.org/w/api.php?action=query&list=search"
                     f"&srsearch={q}&srlimit=5&format=json") or {}
        for hit in ((j.get("query") or {}).get("search") or []):
            return hit["title"]
    return None


def hf_state(papers, me: str) -> tuple[list, list, list]:
    """Live per-paper Hugging Face state: (no page, page but unclaimed, claimed).

    Deliberately live rather than read from papers.yaml. This list is worked by
    hand over days, and a stale copy sends you back to pages you already did --
    which is exactly what happened the first time.
    """
    me = me.lower()
    missing, unclaimed, claimed = [], [], []
    for p in papers:
        j = get_json(f"https://huggingface.co/api/papers/{p['arxiv']}", retries=1)
        if j is None:
            missing.append(p)
        elif any((a.get("user") or {}).get("user", "").lower() == me
                 for a in (j.get("authors") or [])):
            claimed.append(p)
        else:
            unclaimed.append(p)
        time.sleep(0.2)
    return missing, unclaimed, claimed


def hf_worklist_file(missing, unclaimed, claimed) -> str:
    """The two Hugging Face lists, in full, committed so they diff between runs.

    Both lists in one file and in full: the previous version printed a truncated
    top-12, which reads as "that is all of it".

    Only ever called with live state. Writing a cached view into the same file would
    quietly replace checked numbers with older ones, and the file gives no hint which
    it is holding.
    """
    def rows(group):
        return [f"- [ ] {p.get('citations') or 0:>4} cites — "
                f"<https://hf.co/papers/{p['arxiv']}> — "
                f"{(p.get('title_display') or p['title'])[:70]}" for p in group]

    path = os.path.join(TASKS, "hf_worklist.md")
    L = ["# Hugging Face paper pages", "",
         "Live as of the last `python scripts/audit_identity.py` (or "
         "`hf_papers.py --live`): "
         f"**{len(claimed)} claimed**, **{len(unclaimed)} to claim**, "
         f"**{len(missing)} to index**.", "",
         "Both steps need a logged-in browser. An unauthenticated visit to a paper URL",
         "returns 404 and creates nothing (verified on 50 papers — 0 created), which is",
         "why this is a list and not a script.", "",
         "A claim needs admin approval, so a paper you have already requested still",
         "appears below until it is validated — your name will show with no linked user",
         "until then. That is pending, not failed.", "",
         f"## Index — {len(missing)} papers with no page yet", "",
         "Log in to Hugging Face, then open each link. The visit is what creates the",
         "page. Nothing else to fill in.", ""]
    L += rows(missing)
    L += ["", f"## Claim — {len(unclaimed)} pages that exist but are not linked to you", "",
          "On each page: find your name in the author list and use the claim control",
          "next to it. This is what joins the paper to your HF profile, and what makes",
          "your models and datasets cross-list on it.", ""]
    L += rows(unclaimed)
    with open(path, "w") as f:
        f.write("\n".join(L) + "\n")
    return path


def _rows(group, extra=lambda p: "") -> list[str]:
    return [f"- [ ] {p.get('citations') or 0:>4} cites — "
            f"[`{p['arxiv']}`](https://arxiv.org/abs/{p['arxiv']}) "
            f"{(p.get('title_display') or p['title'])[:72]}{extra(p)}"
            for p in group]


def arxiv_ownership_file(cfg, papers, registered: set[str] | None) -> tuple[str, int]:
    ident = cfg["identity"]
    path = os.path.join(TASKS, "arxiv_ownership.md")
    if registered is None:
        body = ["# arXiv ownership", "",
                f"`https://arxiv.org/a/{ident['orcid']}` does not resolve yet. Link your",
                "arXiv account to your ORCID first: <https://arxiv.org/user/confirm_orcid_id>",
                "then re-run `python scripts/audit_identity.py`."]
        with open(path, "w") as f:
            f.write("\n".join(body) + "\n")
        return path, 0

    seen, gap = set(), []
    for p in sorted(papers, key=lambda p: -(p.get("citations") or 0)):
        a = p["arxiv"]
        if a in seen:
            continue
        seen.add(a)
        if a not in registered:
            gap.append(p)
    L = [f"# arXiv: claim ownership of {len(gap)} papers", "",
         f"Registered as author on **{len(registered)}** of **{len(seen)}** arXiv papers.",
         f"Public list: <https://arxiv.org/a/{ident['orcid']}>", "",
         "## Why this is first, not last",
         "",
         "Two things depend on it, and both are invisible until you look:",
         "",
         "1. **You cannot add a journal-ref or DOI to a paper you do not own.** The",
         "   journal-ref list further down `WORKLIST.md` is *blocked* on this for any",
         "   paper here — and journal-ref is what Google Scholar matches citations on.",
         f"2. `https://arxiv.org/a/{ident['orcid']}` is a public, indexable publication",
         "   list on arxiv.org, with an Atom feed and an embeddable widget. Right now it",
         "   shows less than half your corpus, on a domain with far more crawl authority",
         "   than any personal site.",
         "",
         "arXiv's own January 2026 endorsement-policy post recommends claiming ownership",
         "of every paper you co-authored, so this is the documented intent, not a hack.",
         "",
         "## Two routes",
         "",
         "**With the paper password (instant).** The password is in the submitter's",
         "acceptance email. Ask the submitting co-author for it, then enter the arXiv id",
         "and password at <https://arxiv.org/auth/need-paper-password>.",
         "",
         "**Without it (a couple of days).** <https://arxiv.org/auth/request-ownership>",
         "— arXiv staff verify manually. No co-author involvement needed, so for a long",
         "tail of old papers this is the path of least effort: submit them in a batch and",
         "forget about it.",
         "",
         "If a paper is already in your owned list but you are not listed as an author,",
         "that is a different form: <https://arxiv.org/auth/change-author-status>.",
         "",
         "For your own future submissions: share the paper password with every co-author",
         "in the announcement email. It costs nothing and saves them this page.",
         "",
         f"## The {len(gap)} papers, citation-ordered", ""]
    L += _rows(gap)
    with open(path, "w") as f:
        f.write("\n".join(L) + "\n")
    return path, len(gap)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-hf", action="store_true",
                    help="skip the per-paper Hugging Face checks (the slow part)")
    args = ap.parse_args()
    cfg = load_config()
    ident, ids = cfg["identity"], cfg["ids"]
    papers = (read_yaml(os.path.join(DATA, "papers.yaml")) or {})["papers"]
    # One row per arXiv id, not per record: a few papers legitimately carry two
    # records (a retitled version), and checking the same page twice reads as two
    # separate jobs on a worklist worked by hand.
    ax, seen = [], set()
    for p in sorted(papers, key=lambda p: -(p.get("citations") or 0)):
        if p.get("arxiv") and p["arxiv"] not in seen:
            seen.add(p["arxiv"])
            ax.append(p)
    os.makedirs(TASKS, exist_ok=True)

    print("reading ORCID ...", flush=True)
    orc = orcid_public(ident["orcid"])
    print("reading arXiv authority records ...", flush=True)
    reg = arxiv_registered(ident["orcid"])
    print("searching Wikidata by identifier ...", flush=True)
    wd = wikidata_item(cfg)
    # --no-hf means "leave the HF artifacts alone", not "regenerate them from cache".
    # Writing the cached view here would silently overwrite a freshly-checked
    # worklist with older numbers, which is worse than not writing at all.
    missing = unclaimed = claimed = None
    hf_path = None
    if not args.no_hf:
        print(f"checking {len(ax)} Hugging Face paper pages ...", flush=True)
        missing, unclaimed, claimed = hf_state(ax, ids["huggingface"])
        hf_path = hf_worklist_file(missing, unclaimed, claimed)

    ax_path, n_gap = arxiv_ownership_file(cfg, ax, reg)

    # --- the audit report -------------------------------------------------------
    canon = ident["canonical_url"].rstrip("/")
    url_vals = [u for _, u in orc["urls"] if u]
    has_canon = any(canon in (u or "").rstrip("/") for u in url_vals)
    missing_variants = [v for v in ident["name_variants"]
                        if v != ident["name"] and v not in orc["other_names"]]

    def status(ok: bool) -> str:
        return "ok" if ok else "**fix**"

    L = ["# Identity audit", "",
         "Live read of the surfaces you do not control. Regenerate with",
         "`python scripts/audit_identity.py`. Every row is checkable without a login,",
         "which is why it can be re-run — the fixes all need one.", "",
         "| surface | state | |", "|---|---|---|",
         f"| ORCID works (public) | {orc['works']} of {len(papers)} | {status(orc['works'] > 0)} |",
         f"| ORCID canonical URL | {'present' if has_canon else 'absent'} | {status(has_canon)} |",
         f"| ORCID name variants | {len(orc['other_names'])} listed | {status(not missing_variants)} |",
         f"| ORCID keywords | {len(orc['keywords'])} | {status(bool(orc['keywords']))} |",
         f"| ORCID employment/education | {orc['employments']}/{orc['educations']} | {status(orc['employments'] > 0)} |",
         f"| arXiv registered author | {len(reg) if reg is not None else '—'} of {len({p['arxiv'] for p in ax})} | {status(n_gap == 0)} |",
         f"| Wikidata author item | {wd or 'none'} | {status(bool(wd))} |"]
    if missing is not None:
        L += [f"| HF pages indexed | {len(ax) - len(missing)} of {len(ax)} | {status(not missing)} |",
              f"| HF pages claimed | {len(claimed)} of {len(ax) - len(missing)} | {status(not unclaimed)} |"]
    L += [f"| Semantic Scholar records | {len(ids['semantic_scholar'])} | "
          f"{status(len(ids['semantic_scholar']) == 1)} |", ""]

    if orc["works"] == 0:
        L += ["## ORCID has 0 public works", "",
              "Note the *public*: an item set to “trusted parties” is invisible to the",
              "public API, which is the only thing Semantic Scholar, OpenAlex and Crossref",
              "read. So before importing, set **Account settings → Visibility preferences**",
              "to *Everyone*, or the import lands somewhere nothing can see.",
              "", "Then `tasks/orcid_dois.txt` (Add DOI) or `tasks/orcid_import.bib`", ""]
    if not has_canon:
        L += ["## ORCID researcher URLs point somewhere else", "",
              "Listed: " + (", ".join(f"`{u}`" for u in url_vals) or "none") + "  ",
              f"Expected: `{canon}`", "",
              "Two separate problems if one of those is a site-builder page. It competes",
              "with your canonical URL for the same identity — engines cannot fuse two",
              "candidate homepages — and Wix/Squarespace/Notion pages are JS-rendered, so",
              "AI crawlers that do not execute JavaScript see an empty document. Add the",
              "canonical URL, and either delete the other or make it redirect.", ""]
    if missing_variants:
        L += ["## ORCID name variants not listed", "",
              "*Also known as* is what a disambiguation model matches on when a citation",
              "uses a different form. Add: " +
              ", ".join(f"`{v}`" for v in missing_variants), ""]
    if not orc["keywords"]:
        L += ["## ORCID keywords empty", "",
              "Free, and one of the few facets ORCID exposes for subject search. 5–10",
              "phrases someone would type, not coined names.", ""]
    if reg is not None and n_gap:
        L += [f"## arXiv: {n_gap} papers you are not registered as author on", "",
              "The biggest finding here, and a prerequisite rather than a task: you cannot",
              "add a journal-ref to a paper you do not own. Full list and both claim",
              "routes: [arxiv_ownership.md](arxiv_ownership.md).", ""]
    if not wd:
        L += ["## No Wikidata author item", "",
              "Searched by ORCID (P496), Semantic Scholar (P4012), Google Scholar (P1960)",
              "and GitHub (P2037) — no item claims any of them. Name search is not used",
              "here on purpose: it returns *paper* items that merely mention you.",
              "", "Walkthrough: [wikidata_manual.md](wikidata_manual.md).", ""]
    if unclaimed:
        L += [f"## Hugging Face: {len(missing)} to index, {len(unclaimed)} to claim", "",
              "Live counts, not the ones cached in `papers.yaml`. Lists:",
              "[hf_worklist.md](hf_worklist.md).", ""]

    path = os.path.join(TASKS, "identity_audit.md")
    with open(path, "w") as f:
        f.write("\n".join(L) + "\n")

    # Counts for WORKLIST.md, in build/ because they are observed state: entirely
    # re-derivable from the live APIs, so committing them would be storing someone
    # else's data and letting it go stale. Absent file = the section is skipped.
    os.makedirs(BUILD, exist_ok=True)
    state_path = os.path.join(BUILD, "identity_state.json")
    state = {}
    if args.no_hf:
        # Carry the previous HF lists through untouched rather than dropping them:
        # this run made no claim about Hugging Face either way, and dropping them
        # would silently demote WORKLIST.md back to the collector's cached flags.
        try:
            with open(state_path) as f:
                prev = json.load(f)
            state = {k: prev[k] for k in ("hf_missing", "hf_unclaimed") if k in prev}
        except (OSError, ValueError):
            pass
    else:
        state = {"hf_missing": [p["arxiv"] for p in missing],
                 "hf_unclaimed": [p["arxiv"] for p in unclaimed]}
    state.update({"orcid_public_works": orc["works"],
                  "orcid_has_canonical_url": has_canon,
                  "orcid_missing_variants": missing_variants,
                  "orcid_keywords": len(orc["keywords"]),
                  "arxiv_registered": len(reg) if reg is not None else None,
                  "arxiv_total": len({p["arxiv"] for p in ax}),
                  "arxiv_unowned": [p["arxiv"] for p in ax
                                    if reg is not None and p["arxiv"] not in reg],
                  "wikidata": wd})
    with open(state_path, "w") as f:
        json.dump(state, f, indent=1)

    wrote = [path, ax_path] + ([hf_path] if hf_path else [])
    print("\nwrote " + "\n      ".join(wrote))
    for line in L:
        if line.startswith("| ") and "---" not in line:
            print("  " + line)


if __name__ == "__main__":
    main()
