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
from common import (BUILD, ROOT, TASKS, budget_reset, clean_latex, host_of,  # noqa: E402
                    load_config, name_match, norm_title, read_papers, replied, title_of,
                    title_tokens, write_json, write_task)

# Below this the gap is indexing lag rather than a split record. Both conditions have
# to hold: two citations is noise on a 200-cite paper, and 20% is noise on a 3-cite one.
# An OpenAlex split gets merged, so a cached answer that is never re-asked would keep
# reporting one long after it is gone.
CACHE_DAYS = 60
GAP_MIN = 3
GAP_FRAC = 0.15

# Hosts that did not answer this run. Each of the three passes reports what it did not find,
# so a source that refused reads as a clean result -- and the split pass would cache that
# clean result against the paper for CACHE_DAYS.
_silent: set[str] = set()

# Hosts that rejected the request. A 400 is this code handing OpenAlex a query it will not
# parse, and it comes back the same on every re-run, so telling a reader to re-run leaves
# them retrying forever. Read separately -- see `blind`.
_rejected: set[str] = set()


def lookup(url: str) -> dict | None:
    """One JSON lookup, None if it did not answer, with the host recorded against the run.

    Both indexes answer 200 with an empty result set for a name they do not have, so any
    other status is a refusal rather than a report. A 400 goes to `_rejected` and every
    other refusal to `_silent`, which is the difference between a query to fix and a run
    to repeat.
    """
    st, d, why = replied(url)
    if why:
        (_rejected if st == 400 else _silent).add(host_of(url))
    return d


def scholar_query(title: str) -> str:
    """The Scholar search that surfaces every copy of one paper, stray ones included.

    Phrase-quoted, and stripped of the BibTeX brace protection that survives into
    `title` -- Scholar treats a literal `{LLM}s` as part of the phrase and matches
    nothing.
    """
    plain = clean_latex(title or "").replace("{", "").replace("}", "")
    return ("https://scholar.google.com/scholar?q="
            + urllib.parse.quote(f'"{" ".join(plain.split())}"'))


# `?`, `,` and `*` each come back HTTP 400 inside a `.search:` filter value, percent-encoded
# or not, and `|` parses as OR -- which changes the search rather than failing it.
RESERVED = "?,*|"


def searchable(text: str, words: int = 0) -> str:
    """`text` as a `.search:` filter value, cut to the first `words` words when given.

    A filter matches tokens, so the characters OpenAlex reserves were never part of the
    match and dropping them narrows nothing.
    """
    out = "".join(" " if c in RESERVED else c for c in text).split()
    return " ".join(out[:words] if words else out)


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
                        "title": title_of(p),
                        "scholar_citations": sc, "index_citations": api, "gap": gap,
                        "scholar_url": r.get("scholar_url"),
                        "search": scholar_query(title_of(p))})
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
         + urllib.parse.quote(searchable(name))
         + "&select=id,doi,display_name,publication_year,cited_by_count,authorships")
    d = lookup(q + (f"&mailto={mailto}" if mailto else ""))
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
    d = lookup(q + (f"&mailto={mailto}" if mailto else ""))
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
    against a free daily allowance of 100, so a full corpus takes more than one day.
    Every answer is cached in `build/openalex_splits.json` for CACHE_DAYS and a run
    resumes at the first paper without a fresh one. A search that did not answer is not
    cached, so an outage costs a retry rather than CACHE_DAYS of reporting no split.

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

    def answered(p) -> bool:
        """Whether the cache already holds the answer to the question this run would ask.

        An entry asked under a different search string answers a different question, so a
        change to `searchable` re-asks exactly the papers it changed and leaves the rest.
        """
        e = cache.get(p.get("slug")) or {}
        return (e.get("asked", "") >= fresh
                and e.get("search") == searchable(p.get("title") or "", 12))

    asked: set[str] = set()
    for p in papers[:limit]:
        title, slug = p.get("title") or "", p.get("slug")
        if len(title) < 25 or answered(p):
            continue
        ask = searchable(title, 12)
        q = ("https://api.openalex.org/works?per-page=25&select=id,display_name,"
             "cited_by_count,publication_year&filter=title.search:"
             + urllib.parse.quote(ask))
        d = lookup(q + (f"&mailto={mailto}" if mailto else ""))
        if budget_reset("api.openalex.org") is not None:
            break
        if d is None:
            # Caching this would stamp the paper as asked today with no split found, and
            # nothing would ask again for CACHE_DAYS. The budget case above resumes
            # tomorrow; any other refusal is retried on the next run.
            continue
        asked.add(slug)
        want = title_tokens(title)
        cache[slug] = {
            "asked": datetime.date.today().isoformat(), "search": ask,
            "records": [{"url": w.get("id"), "title": w.get("display_name"),
                         "year": w.get("publication_year"),
                         "citations": w.get("cited_by_count") or 0}
                        for w in (d or {}).get("results") or []
                        if same_work(want, w.get("display_name"))]}
    if asked:
        # Re-read before writing. Another run reaching here -- `update.py --step audit`
        # does -- may have cached papers this one never asked about, and a plain overwrite
        # drops them, which costs a day of credits to win back.
        try:
            with open(cache_path) as f:
                merged = json.load(f)
        except (OSError, ValueError):
            merged = {}
        merged.update({s: cache[s] for s in asked})
        write_json(cache_path, merged, indent=1)

    # Filtered again on the way out, so tightening the rule takes effect on the next run
    # instead of after a second day of credits.
    def records(p):
        want = title_tokens(p.get("title") or "")
        return sorted((w for w in (cache.get(p.get("slug")) or {}).get("records") or []
                       if same_work(want, w.get("title"))),
                      key=lambda w: -w["citations"])

    out = [{"slug": p.get("slug"),
            "title": title_of(p),
            "records": records(p),
            "search": scholar_query(title_of(p))}
           for p in papers[:limit] if len(records(p)) > 1]
    checkable = [p for p in papers[:limit] if len(p.get("title") or "") >= 25]
    return {"rows": sorted(out, key=lambda r: -sum(x["citations"] for x in r["records"])),
            "budget_reset": budget_reset("api.openalex.org"),
            "checked": len([p for p in checkable if answered(p)]),
            "total": len(checkable)}


# OpenAlex bills `.search:` filters against a free daily allowance, so a run can be
# half-sighted rather than clean and every section that reads OpenAlex has to say which
# it was.
METER = ("meters its search endpoint at 100 free queries a day, and today's are spent.")
HALF_BLIND = [textwrap.fill(
    f"Nothing at Crossref, and OpenAlex refused every query. It {METER} This pass saw "
    "one of its two sources.", 78, break_on_hyphens=False)]


def out_of_credit(state: dict) -> bool:
    return (state.get("openalex") or {}).get("budget_reset") is not None


def blind(silent: list[str], rejected: list[str] = ()) -> list[str]:
    """The stand-in for a count of nothing, when nothing is not what a source said.

    A rejected query says re-running is not the fix, because it comes back rejected. The
    fix is `searchable`, which is where a character the filter reserves gets dropped.
    """
    if rejected:
        return [textwrap.fill(
            f"{' and '.join(rejected)} rejected the query, so an empty list here is not a "
            "finding. Re-running repeats the rejection -- the search string carries a "
            "character the filter reserves, which `searchable` is meant to drop.", 78,
            break_on_hyphens=False)]
    return [textwrap.fill(
        f"{' and '.join(silent)} did not answer this run, so an empty list here is not a "
        "finding. Re-run `python scripts/scholar_strays.py`.", 78,
        break_on_hyphens=False)]


HOW = [
    "Every row below is a search string. Paste it into Scholar, and if a result is your",
    "paper under a second record, use *Merge* from your profile -- tick your own row and",
    "the stray, then merge. Scholar keeps the citations of both.",
    "",
    "Nothing here is certain. An initials-only author form belongs to other people too,",
    "and a citation gap can be indexing lag. Read the row before merging: a wrong merge",
    "attaches someone else's paper to your name and is worse than the split.",
]


def _no_answer(state: dict) -> list[str] | None:
    """Why a name-form section is empty because a source did not answer.

    None when every source answered, which is when an empty section means the search
    found nothing.
    """
    silent, rejected = state.get("silent") or [], state.get("rejected") or []
    # The budget wording asserts Crossref answered with nothing, which only one of these
    # two states supports.
    if out_of_credit(state) and "api.crossref.org" not in silent:
        return [*HALF_BLIND, ""]
    if silent or rejected:
        return [*blind(silent, rejected), ""]
    return None


def _undercounted(state: dict) -> list[str]:
    """Profile rows whose Scholar count is below what the APIs already found."""
    u = state["undercounted"]
    L = [f"## Profile rows counting fewer citations than the APIs ({len(u)})", ""]
    if not state["scholar_answered"]:
        return L + ["Skipped: `build/scholar_diff.json` has no per-row counts yet. Run",
                    "`python scripts/scholar_check.py` first -- the profile fetch is the only",
                    "source for them.", ""]
    if not u:
        return L + ["None. Every profile row counts at least as many citations as OpenAlex and",
                    "Semantic Scholar do, which is the expected direction.", ""]
    L += ["Scholar indexes preprints and theses the APIs do not, so it should always",
          "count more. Where it counts less, the difference is on another record.", "",
          "| gap | Scholar | index | paper | search |", "|---|---|---|---|---|"]
    L += [f"| {r['gap']} | {r['scholar_citations']} | {r['index_citations']} "
          f"| {(r['title'] or '')[:60]} | [search]({r['search']}) |" for r in u]
    return L + [""]


def _duplicate_rows(stray: list[dict], state: dict) -> list[str]:
    """Records under another form of the name whose title is a paper in the corpus."""
    L = [f"## Copies of your papers filed under another form of your name ({len(stray)})",
         ""]
    if not stray:
        return L + (_no_answer(state) or ["None found at OpenAlex or Crossref.", ""])
    L += ["The title matches a paper you have, so this record is a duplicate of it.",
          "", "| cites | filed as | paper | record | search |", "|---|---|---|---|---|"]
    L += [f"| {r['citations']} | {r['searched_as']} | `{r['matched']}` "
          f"| [{r['index']}]({r['url']}) | [search]({r['search']}) |" for r in stray]
    return L + [""]


def _unrecorded_rows(other: list[dict], state: dict) -> list[str]:
    """Records under a form of the name whose title is in no paper the corpus has."""
    L = [f"## Filed under your name forms but not in the bibliography ({len(other)})", ""]
    if not other:
        return L + (_no_answer(state) or ["None.", ""])
    L += ["Either somebody else with a similar name, or a paper the bibliography never",
          "received. Only the second kind is yours to act on, and it goes into",
          "`orig.bib`, never into the output.", "",
          "| cites | filed as | recorded authors | title | record |",
          "|---|---|---|---|---|"]
    L += [f"| {r['citations']} | {r['searched_as']} "
          f"| {(r['authors'] or '')[:50]} | {(r['title'] or '')[:50]} "
          f"| [{r['index']}]({r['url']}) |" for r in other[:40]]
    if len(other) > 40:
        L.append(f"| … | | | {len(other) - 40} more in "
                 "`build/scholar_strays.json` | |")
    return L + [""]


def _split_rows(state: dict) -> list[str]:
    """Corpus papers OpenAlex holds under more than one record, and how far it got."""
    s, oa = state["split_records"], state.get("openalex") or {}
    L = [f"## Papers OpenAlex holds twice ({len(s)})", ""]
    # Counted rather than read off the budget: the credits can run out on the last paper,
    # which leaves nothing to resume, and a plain refusal leaves papers unchecked with
    # credits to spare.
    partial = (not state["openalex_skipped"]
               and (oa.get("checked") or 0) < (oa.get("total") or 0))
    if partial:
        spent = out_of_credit(state)
        why = ("OpenAlex rejected the query for the rest, which a re-run repeats."
               if "api.openalex.org" in (state.get("rejected") or [])
               else f"OpenAlex {METER}" if spent
               else "OpenAlex did not answer for the rest.")
        L += [textwrap.fill(
            f"**Partial: {oa.get('checked')} of {oa.get('total')} papers checked.** {why} "
            f"Every answer is cached, so re-running `python scripts/scholar_strays.py` "
            f"{'tomorrow ' if spent else ''}resumes where this one stopped.",
            78, break_on_hyphens=False), ""]
    if state["openalex_skipped"]:
        return L + ["Skipped with `--skip-openalex`.", ""]
    if s:
        L += ["A paper split at OpenAlex is usually split at Scholar too, for the same",
              "reason: the metadata a parser read differs between copies.", ""]
        for r in s:
            L.append(f"- [ ] `{r['slug']}` — [search Scholar]({r['search']})")
            L += [f"      - {x['citations']} cites — {(x['title'] or '')[:70]} "
                  f"— <{x['url']}>" for x in r["records"]]
        return L + [""]
    if not partial:
        return L + ["None. Every corpus title resolves to one OpenAlex record.", ""]
    return L


def summary_line(state: dict) -> str:
    """The closing count, keeping the two kinds of citation figure apart.

    An undercounted row is measured against the Scholar profile itself. The other two
    passes read a duplicate record at an API and take its count as an estimate of the
    Scholar record behind it, which nothing here has seen.
    """
    und = state.get("undercounted") or []
    stray = [r for r in state.get("typo_records") or [] if r.get("matched")]
    splits = state.get("split_records") or []
    inferred = (sum(r["citations"] for r in stray)
                + sum(x["citations"] for r in splits for x in r["records"][1:]))
    return (f"scholar strays: {len(und)} undercounted row(s), {len(stray)} name-form "
            f"duplicate(s), {len(splits)} OpenAlex split(s) — "
            f"{sum(r['gap'] for r in und)} citations measured at Scholar, "
            f"{inferred} more inferred from a duplicate record")


def write_page(state: dict) -> str:
    """Write `tasks/scholar_strays.md`, one section per kind of stray, and return its path."""
    t = state["typo_records"]
    L = (["# Citations Scholar is holding on a record you cannot see", "",
          "Generated by `python scripts/scholar_strays.py`.", "", *HOW, ""]
         + _undercounted(state)
         + _duplicate_rows([r for r in t if r.get("matched")], state)
         + _unrecorded_rows([r for r in t if not r.get("matched")], state)
         + _split_rows(state))
    os.makedirs(TASKS, exist_ok=True)
    path = os.path.join(TASKS, "scholar_strays.md")
    write_task(path, L)
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
    papers = read_papers()
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
    state["silent"] = sorted(_silent)
    state["rejected"] = sorted(_rejected)
    write_json(os.path.join(BUILD, "scholar_strays.json"), state, indent=1)
    path = write_page(state)

    print(summary_line(state))
    if not args.quiet:
        print(f"  wrote {os.path.relpath(path, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
