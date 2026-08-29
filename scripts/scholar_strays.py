#!/usr/bin/env python3
"""Find copies of your papers that Google Scholar indexed as separate records.

Scholar parses references out of PDFs, so one paper can enter its index several times
-- under a mangled title, a misspelled author, or an initials-only author list. Each
copy holds its own citations, and only the copy on your profile counts. Scholar's
merge tool fixes it, one paper at a time, and the hard part is knowing what to look
for: the stray copy is not on your profile, so nothing on the profile names it.

Three passes, cheapest first, each producing search strings to paste into Scholar:

    undercounted   A profile row whose Scholar count is *below* an API index's count.
                   Scholar indexes preprints, theses and slides that the APIs do not,
                   so it normally counts more. Counting less means the rest of its
                   count is sitting on a record you cannot see.
    typo records   Works filed under a name in `identity.name_typos`, or under an
                   initials-only form, at OpenAlex and Crossref. A hit whose title
                   matches the corpus is a stray copy; a hit whose title does not is
                   either someone else or a paper the bibliography never received.
    split records  More than one OpenAlex record for one corpus title. OpenAlex and
                   Scholar mis-split on the same mangled metadata, so an OpenAlex
                   split is a cheap proxy for a Scholar split that needs no scraping.

Read-only. No login, no scraping of search results -- every fetch is a public API.
The `undercounted` pass needs `build/scholar_diff.json` from `scholar_check.py`;
without it that pass is skipped and says so.

Writes build/scholar_strays.json and tasks/scholar_strays.md.

Usage:
    python scripts/scholar_strays.py
    python scripts/scholar_strays.py --quiet          # write the files, print counts
    python scripts/scholar_strays.py --skip-openalex  # the two cheap passes only
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
import textwrap
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (BUILD, DATA, ROOT, TASKS, budget_reset, clean_latex, get_json,  # noqa: E402
                    load_config, name_match, norm_title, read_yaml, title_tokens,
                    write_json)

# Below this the gap is indexing lag rather than a split record. Both conditions have
# to hold: two citations is noise on a 200-cite paper, and 20% is noise on a 3-cite one.
# An OpenAlex split gets merged, so a cached answer that is never re-asked would keep
# reporting one long after it is gone.
CACHE_DAYS = 60
GAP_MIN = 3
GAP_FRAC = 0.15


def scholar_query(title: str) -> str:
    """The Scholar search that surfaces every copy of one paper, stray ones included.

    Phrase-quoted, and stripped of the BibTeX brace protection that survives into
    `title` -- Scholar treats a literal `{LLM}s` as part of the phrase and matches
    nothing.
    """
    plain = clean_latex(title or "").replace("{", "").replace("}", "")
    return ("https://scholar.google.com/scholar?q="
            + urllib.parse.quote(f'"{" ".join(plain.split())}"'))


def undercounted(papers, diff) -> list[dict]:
    """Profile rows counting fewer citations than an API index does.

    Returns one row per paper, worst gap first. Empty when scholar_diff.json has no
    `paired` list, which is what an old file or a challenged profile fetch looks like.
    """
    by_slug = {p.get("slug"): p for p in papers if p.get("slug")}
    out = []
    for r in diff.get("paired") or []:
        p = by_slug.get(r.get("slug"))
        if not p:
            continue
        sc = r.get("scholar_citations") or 0
        api = p.get("citations") or 0
        gap = api - sc
        if gap >= GAP_MIN and api and gap / api >= GAP_FRAC:
            out.append({"slug": r["slug"],
                        "title": p.get("title_display") or p.get("title"),
                        "scholar_citations": sc, "index_citations": api, "gap": gap,
                        "scholar_url": r.get("scholar_url"),
                        "search": scholar_query(p.get("title_display") or p.get("title"))})
    return sorted(out, key=lambda r: -r["gap"])


def initials_forms(name: str) -> list[str]:
    """`Leshem Choshen` -> the initials-only forms a reference list prints.

    Not asserted anywhere -- these are search keys, and an initials-only form can
    belong to somebody else, which is why every hit is reported for a human to read
    rather than acted on.
    """
    parts = [w for w in name.split() if w]
    if len(parts) < 2:
        return []
    first, last = parts[0], parts[-1]
    return [f"{first[0]}. {last}", f"{first[0]} {last}", f"{last}, {first[0]}."]


def _openalex_by_name(name: str, mailto: str | None) -> list[dict]:
    q = ("https://api.openalex.org/works?per-page=100&filter=raw_author_name.search:"
         + urllib.parse.quote(name)
         + "&select=id,doi,display_name,publication_year,cited_by_count,authorships")
    d = get_json(q + (f"&mailto={mailto}" if mailto else ""))
    out = []
    for w in (d or {}).get("results") or []:
        raw = ", ".join(a.get("raw_author_name") or "" for a in w.get("authorships") or [])
        out.append({"index": "OpenAlex", "url": w.get("id"), "doi": w.get("doi"),
                    "title": w.get("display_name"), "year": w.get("publication_year"),
                    "citations": w.get("cited_by_count") or 0, "authors": raw[:200],
                    "author_list": [a.get("raw_author_name") or ""
                                    for a in w.get("authorships") or []]})
    return out


def _crossref_by_name(name: str, mailto: str | None) -> list[dict]:
    q = ("https://api.crossref.org/works?rows=100&select=DOI,title,author,"
         "is-referenced-by-count,issued&query.author=" + urllib.parse.quote(name))
    d = get_json(q + (f"&mailto={mailto}" if mailto else ""))
    out = []
    for w in ((d or {}).get("message") or {}).get("items") or []:
        raw = ", ".join(f"{a.get('given', '')} {a.get('family', '')}".strip()
                        for a in w.get("author") or [])
        yr = ((w.get("issued") or {}).get("date-parts") or [[None]])[0][0]
        out.append({"index": "Crossref", "url": f"https://doi.org/{w.get('DOI')}",
                    "doi": w.get("DOI"), "title": (w.get("title") or [None])[0],
                    "year": yr, "citations": w.get("is-referenced-by-count") or 0,
                    "authors": raw[:200],
                    "author_list": [f"{a.get('given', '')} {a.get('family', '')}".strip()
                                    for a in w.get("author") or []]})
    return out


def typo_records(cfg, papers, mailto) -> list[dict]:
    """Works filed under a misspelled or initials-only form of the name.

    A record is reported only when no author string on it is an exact asserted form of
    the name -- otherwise every correctly-filed paper of yours comes back, because a
    reference list that prints `Choshen, L.` alongside the right spelling is normal.

    The two key kinds are weighted differently, because their false-positive rates are
    nothing alike. A string in `name_typos` resolves to you and nobody else, so a hit is
    reported whether or not its title is in the corpus. An initials-only form belongs to
    other people too, so a hit is reported only when its title matches a paper you
    already have -- which makes it a duplicate record rather than a name collision.
    """
    ident = cfg["identity"]
    asserted = [ident["name"], *(ident.get("name_variants") or [])]
    keys = [(k, "typo") for k in (ident.get("name_typos") or [])]
    for v in asserted:
        keys += [(k, "initials") for k in initials_forms(v)]
    keys = [(k, w) for k, w in dict(keys).items() if k]
    by_norm = {norm_title(p.get("title")): p for p in papers}
    seen, out = set(), []
    for key, weight in keys:
        for rec in _openalex_by_name(key, mailto) + _crossref_by_name(key, mailto):
            ident_key = (rec.get("doi") or "").lower() or norm_title(rec["title"])
            if not ident_key or ident_key in seen:
                continue
            hit = by_norm.get(norm_title(rec["title"]))
            authors = rec.pop("author_list")
            # Crossref's `query.author` is a loose bibliographic search, not an author
            # filter: "Leshem Chosen" returns anything carrying either token, including
            # a 1970s paper by Y Leshem. The searched form has to actually be on the
            # record, or the pass reports strangers.
            if not any(name_match(a, [key]) == "exact" for a in authors):
                continue
            if any(name_match(a, asserted) == "exact" for a in authors):
                continue                       # correctly filed under a form you assert
            if weight == "initials" and not hit:
                continue                       # an initials form is somebody else too
            seen.add(ident_key)
            out.append(dict(rec, searched_as=key, weight=weight,
                            matched=hit.get("slug") if hit else None,
                            search=scholar_query(rec["title"] or "")))
    return sorted(out, key=lambda r: -(r.get("citations") or 0))


def same_work(want: set[str], title: str | None) -> bool:
    """Whether a record OpenAlex returned names this corpus paper or a different one.

    `want` is the corpus title's content words. A record may drop words, since a
    truncated title is the mangling this pass looks for, and may not add any.
    """
    got = title_tokens(title or "")
    return bool(want) and not got - want and len(want & got) / len(want) > 0.8


def split_records(papers, mailto, limit=None) -> dict:
    """Corpus titles that OpenAlex holds more than one record for.

    Returns `rows`, `budget_reset`, `checked` and `total`. One metered search per paper
    against a free daily allowance of 100, so a full corpus takes more than one day:
    every answer is cached in `build/openalex_splits.json` for CACHE_DAYS and a run
    resumes at the first paper without a fresh one. `budget_reset` is the seconds until more credits, or None
    if the pass finished.

    A split at OpenAlex is not itself a Scholar problem -- it is evidence that the
    paper's metadata is mangled in a way Scholar splits on too, and the search string is
    the same either way.
    """
    cache_path = os.path.join(BUILD, "openalex_splits.json")
    try:
        with open(cache_path) as f:
            cache = json.load(f)
    except (OSError, ValueError):
        cache = {}
    fresh = (datetime.date.today() - datetime.timedelta(days=CACHE_DAYS)).isoformat()
    asked = 0
    for p in papers[:limit]:
        title, slug = p.get("title") or "", p.get("slug")
        if len(title) < 25 or (cache.get(slug) or {}).get("asked", "") >= fresh:
            continue
        q = ("https://api.openalex.org/works?per-page=25&select=id,display_name,"
             "cited_by_count,publication_year&filter=title.search:"
             + urllib.parse.quote(" ".join(title.split()[:12])))
        d = get_json(q + (f"&mailto={mailto}" if mailto else ""))
        if budget_reset("api.openalex.org") is not None:
            break
        asked += 1
        want = title_tokens(title)
        cache[slug] = {
            "asked": datetime.date.today().isoformat(),
            "records": [{"url": w.get("id"), "title": w.get("display_name"),
                         "year": w.get("publication_year"),
                         "citations": w.get("cited_by_count") or 0}
                        for w in (d or {}).get("results") or []
                        if same_work(want, w.get("display_name"))]}
    if asked:
        write_json(cache_path, cache, indent=1)

    # Filtered again on the way out, so tightening the rule takes effect on the next run
    # instead of after a second day of credits.
    def records(p):
        want = title_tokens(p.get("title") or "")
        return sorted((w for w in (cache.get(p.get("slug")) or {}).get("records") or []
                       if same_work(want, w.get("title"))),
                      key=lambda w: -w["citations"])

    out = [{"slug": p.get("slug"),
            "title": p.get("title_display") or p.get("title"),
            "records": records(p),
            "search": scholar_query(p.get("title_display") or p.get("title"))}
           for p in papers[:limit] if len(records(p)) > 1]
    checkable = [p for p in papers[:limit] if len(p.get("title") or "") >= 25]
    return {"rows": sorted(out, key=lambda r: -sum(x["citations"] for x in r["records"])),
            "budget_reset": budget_reset("api.openalex.org"),
            "checked": len([p for p in checkable
                            if (cache.get(p.get("slug")) or {}).get("asked", "") >= fresh]),
            "total": len(checkable)}


# OpenAlex bills `.search:` filters against a free daily allowance, so a run can be
# half-sighted rather than clean and every section that reads OpenAlex has to say which
# it was.
METER = ("meters its search endpoint at 100 free queries a day, and today's are spent.")
HALF_BLIND = [textwrap.fill(
    f"Nothing at Crossref, and OpenAlex refused every query: it {METER} This pass saw "
    "one of its two sources.", 78, break_on_hyphens=False)]


def out_of_credit(state: dict) -> bool:
    return (state.get("openalex") or {}).get("budget_reset") is not None


HOW = [
    "Every row below is a search string. Paste it into Scholar, and if a result is your",
    "paper under a second record, use *Merge* from your profile -- tick your own row and",
    "the stray, then merge. Scholar keeps the citations of both.",
    "",
    "Nothing here is certain. An initials-only author form belongs to other people too,",
    "and a citation gap can be indexing lag. Read the row before merging: a wrong merge",
    "attaches someone else's paper to your name and is worse than the split.",
]


def write_page(state: dict) -> str:
    L = ["# Citations Scholar is holding on a record you cannot see", "",
         "Generated by `python scripts/scholar_strays.py`.", "", *HOW, ""]
    u = state["undercounted"]
    L += [f"## Profile rows counting fewer citations than the APIs ({len(u)})", ""]
    if not state["scholar_answered"]:
        L += ["Skipped: `build/scholar_diff.json` has no per-row counts yet. Run",
              "`python scripts/scholar_check.py` first -- the profile fetch is the only",
              "source for them.", ""]
    elif not u:
        L += ["None. Every profile row counts at least as many citations as OpenAlex and",
              "Semantic Scholar do, which is the expected direction.", ""]
    else:
        L += ["Scholar indexes preprints and theses the APIs do not, so it should always",
              "count more. Where it counts less, the difference is on another record.", "",
              "| gap | Scholar | index | paper | search |", "|---|---|---|---|---|"]
        for r in u:
            L.append(f"| {r['gap']} | {r['scholar_citations']} | {r['index_citations']} "
                     f"| {(r['title'] or '')[:60]} | [search]({r['search']}) |")
        L.append("")

    t = state["typo_records"]
    stray = [r for r in t if r.get("matched")]
    other = [r for r in t if not r.get("matched")]
    L += [f"## Copies of your papers filed under another form of your name ({len(stray)})",
          ""]
    if stray:
        L += ["The title matches a paper you have, so this record is a duplicate of it.",
              "", "| cites | filed as | paper | record | search |", "|---|---|---|---|---|"]
        for r in stray:
            L.append(f"| {r['citations']} | {r['searched_as']} | `{r['matched']}` "
                     f"| [{r['index']}]({r['url']}) | [search]({r['search']}) |")
        L.append("")
    elif out_of_credit(state):
        L += [*HALF_BLIND, ""]
    else:
        L += ["None found at OpenAlex or Crossref.", ""]

    L += [f"## Filed under your name forms but not in the bibliography ({len(other)})", ""]
    if not other and out_of_credit(state):
        L += [*HALF_BLIND, ""]
    elif other:
        L += ["Either somebody else with a similar name, or a paper the bibliography never",
              "received. Only the second kind is yours to act on, and it goes into",
              "`orig.bib`, never into the output.", "",
              "| cites | filed as | recorded authors | title | record |",
              "|---|---|---|---|---|"]
        for r in other[:40]:
            L.append(f"| {r['citations']} | {r['searched_as']} "
                     f"| {(r['authors'] or '')[:50]} | {(r['title'] or '')[:50]} "
                     f"| [{r['index']}]({r['url']}) |")
        if len(other) > 40:
            L.append(f"| … | | | {len(other) - 40} more in "
                     "`build/scholar_strays.json` | |")
        L.append("")
    else:
        L += ["None.", ""]

    s = state["split_records"]
    oa = state.get("openalex") or {}
    L += [f"## Papers OpenAlex holds twice ({len(s)})", ""]
    partial = out_of_credit(state) and not state["openalex_skipped"]
    if partial:
        L += [textwrap.fill(
            f"**Partial: {oa.get('checked')} of {oa.get('total')} papers checked.** "
            f"OpenAlex {METER} Every answer is cached, so re-running "
            "`python scripts/scholar_strays.py` tomorrow resumes where this one stopped.",
            78, break_on_hyphens=False), ""]
    if state["openalex_skipped"]:
        L += ["Skipped with `--skip-openalex`.", ""]
    elif s:
        L += ["A paper split at OpenAlex is usually split at Scholar too, for the same",
              "reason: the metadata a parser read differs between copies.", ""]
        for r in s:
            L.append(f"- [ ] `{r['slug']}` — [search Scholar]({r['search']})")
            for x in r["records"]:
                L.append(f"      - {x['citations']} cites — {(x['title'] or '')[:70]} "
                         f"— <{x['url']}>")
        L.append("")
    elif not partial:
        L += ["None. Every corpus title resolves to one OpenAlex record.", ""]

    os.makedirs(TASKS, exist_ok=True)
    path = os.path.join(TASKS, "scholar_strays.md")
    with open(path, "w") as f:
        f.write("\n".join(L) + "\n")
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--skip-openalex", action="store_true",
                    help="skip the one-fetch-per-paper split-record pass")
    ap.add_argument("--limit", type=int, default=None,
                    help="papers to check in the split-record pass")
    args = ap.parse_args()

    cfg = load_config()
    papers = (read_yaml(os.path.join(DATA, "papers.yaml")) or {}).get("papers") or []
    mailto = (cfg.get("identity") or {}).get("email")
    try:
        with open(os.path.join(BUILD, "scholar_diff.json")) as f:
            diff = json.load(f)
    except (OSError, ValueError):
        diff = {}

    state = {"scholar_answered": bool(diff.get("paired")),
             "openalex_skipped": args.skip_openalex,
             "undercounted": undercounted(papers, diff),
             "typo_records": typo_records(cfg, papers, mailto),
             "split_records": [], "openalex": {}}
    if not args.skip_openalex:
        sp = split_records(papers, mailto, args.limit)
        state["split_records"], state["openalex"] = sp.pop("rows"), sp
    state["openalex"]["budget_reset"] = budget_reset("api.openalex.org")
    write_json(os.path.join(BUILD, "scholar_strays.json"), state, indent=1)
    path = write_page(state)

    stray = [r for r in state["typo_records"] if r.get("matched")]
    at_stake = (sum(r["gap"] for r in state["undercounted"])
                + sum(r["citations"] for r in stray))
    print(f"scholar strays: {len(state['undercounted'])} undercounted row(s), "
          f"{len(stray)} name-form duplicate(s), "
          f"{len(state['split_records'])} OpenAlex split(s) — "
          f"~{at_stake} citations at stake")
    if not args.quiet:
        print(f"  wrote {os.path.relpath(path, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
