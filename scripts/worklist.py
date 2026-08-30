"""Every section of `WORKLIST.md`, one function each.

A section takes the state a step left in `build/` plus the corpus, and returns the lines it
prints or nothing at all. Nothing here reads a network or writes a file, so a section is
callable from a test with a dict. `update.step_worklist` holds the order they print in.

An empty return is the report that the section is done -- see the page's own opening line.
"""
import glob
import os
import re
import textwrap

from common import (DATA, ROOT, clipped, has_live_sidecar, is_preprint_venue, norm_title,
                    plural, read_overrides, read_yaml, synth_bibtex, title_of)
from sweep_github import ZENODO_KINDS

def held_until(fragment: str) -> str | None:
    """The date a not-yet-due follow-up may remove the work in a section, or None.

    `covers` on a follow-up lists heading fragments. A section that matches one is work
    an outside process is scheduled to do instead, so the section says so and the date
    stays in `data/followups.yaml` alone.
    """
    import datetime
    items = (read_yaml(os.path.join(DATA, "followups.yaml")) or {}).get("followups") or []
    today = datetime.date.today()
    for i in items:
        d = i["due"]
        d = d if isinstance(d, datetime.date) else datetime.date.fromisoformat(str(d))
        if d > today and fragment in (i.get("covers") or []):
            return d.isoformat()
    return None


def by_citations(papers: list[dict], pred, n: int = 8) -> list[dict]:
    """The `n` papers matching `pred`, most-cited first."""
    return sorted([p for p in papers if pred(p)],
                  key=lambda p: -(p.get("citations") or 0))[:n]


def scholar_gaps(sc: dict, cfg: dict | None = None) -> list[str]:
    """The worklist section for `build/scholar_diff.json`, or nothing.

    First on the page when it is there, ahead of every fix to a paper we do have.
    Everything else on this list improves how a paper is presented; this list is
    papers that are not presented at all, and no amount of work on the other sections
    reaches them. It is also the only section whose items are *upstream of the
    pipeline* -- the fix is an edit to the source bibliography, not to anything here.

    One subsection per `_bucket` function below, in the order they print. Each returns
    nothing when its bucket is empty, so a bucket with no work cannot print a heading and
    the whole section disappears when every bucket is empty.
    """
    if not sc:
        return []
    if not sc.get("scholar_answered", True):
        return _scholar_refused(sc)
    # `stale` says which side of a title variant is behind. `bib` is one edit upstream,
    # `open` is a judgement, and `scholar` is neither -- editing that row changes what
    # Scholar displays, not which citations cluster under it. `unknown` means arXiv was
    # never asked, and is named rather than dropped, because both headings below claim to
    # know what arXiv holds.
    var = sc.get("title_variants") or []
    buckets = [
        _gate_excluded(sc.get("gate_dropped") or []),
        _absent_from_bib([r for r in (sc.get("not_in_corpus") or [])
                          if (r.get("kind") or "paper") == "paper"], cfg),
        _not_on_profile(sc.get("not_on_scholar") or [], sc),
        _bib_behind_arxiv([v for v in var if v.get("stale") == "bib"]),
        _no_arxiv_titles([v for v in var if v.get("stale") == "unknown"]),
        _title_is_a_ruling([v for v in var if v.get("stale") == "open"]),
        _listed_twice(sc.get("scholar_duplicates") or [], sc),
    ]
    if not any(buckets):
        return []
    return _coverage_top(sc) + [ln for b in buckets for ln in b]


def _cites(n) -> str:
    """`1 cite`, `0 cites` -- a citation count, agreeing, and reading 0 when absent."""
    return plural(n or 0, "cite")


def _scholar_refused(sc: dict) -> list[str]:
    """A blockquote saying the coverage section is missing rather than empty.

    Without it the section is simply absent, which on a page of open items reads as
    Scholar agreeing with the corpus. Every bucket rests on a title being absent from the
    profile listing, and none of them can be computed from a listing that did not arrive.
    """
    got = sc.get("scholar_rows") or 0
    why = (f"{got} row(s) arrived and then a page refused. Every bucket here rests on "
           "a title being absent from the listing, so a listing missing a page is no "
           "more usable than none."
           if got else
           "Scholar refuses most machines most of the time, and a refusal says nothing "
           "about the corpus.")
    # The last two lines are not wrapped. A command or a markdown link split across a
    # newline is a link the reader has to repair before they can use it.
    lead = (f"**Google Scholar did not answer this run, so the coverage section is "
            f"missing rather than empty.** {why}")
    return [f"> {ln}" for ln in textwrap.wrap(lead, 76)] + [
        "> Re-run `python update.py --step audit`. What the Semantic Scholar author",
        "> record could answer is in [tasks/identity_audit.md](tasks/identity_audit.md).",
        ""]


def _coverage_top(sc: dict) -> list[str]:
    """The heading, and the two numbers that measure Scholar rather than this list."""
    # No total in the heading. `declines.yaml` filters this file *after* it is built, so a
    # count of the buckets below is a count of papers that may no longer be under them.
    return ["## Coverage: Google Scholar and the corpus disagree",
            "",
            f"Scholar lists **{sc.get('scholar_rows')}** works and matched "
            f"**{sc.get('matched')}** of the corpus's **{sc.get('corpus')}**. Scholar is",
            "the one list of your papers that is built by a different process, so it is the",
            "only check that can see a paper this pipeline never received.", "",
            # Backticks, never a markdown link. `build/` is gitignored, so a link there is
            # dead for every reader of this page on GitHub and after a clone. What makes it
            # openable is the command that writes it, which is why that is named instead.
            "Every bucket in full, including what is truncated below, is in",
            "`build/scholar_diff.json` on the machine that last ran the audit. `build/` is",
            "gitignored, so `python update.py --step audit` is the one command between a",
            "fresh clone and the file.", ""]


def _gate_excluded(gate: list[dict]) -> list[str]:
    """Rows Scholar says are the author's that `build/not_mine.json` rejected."""
    if not gate:
        return []
    L = [f"### {plural(len(gate), 'paper')} the authorship gate excluded  — a bug, or a "
         f"wrong Scholar row", "",
         "Scholar says these are yours and `build/not_mine.json`, written by the",
         "same run and gitignored like the rest of `build/`, says they are not.",
         "One of the two is wrong. If the paper is yours, add its title under",
         "`also_mine` in [`data/overrides.yaml`](data/overrides.yaml); if Scholar has",
         "merged a namesake's paper into your profile, delete it there, because a",
         "wrong row misleads every human who reads it too.", ""]
    return L + [f"- [ ] {_cites(r.get('citations'))} — {clipped(r.get('title') or '', 66)}"
                for r in gate] + [""]


def _absent_from_bib(miss: list[dict], cfg: dict | None) -> list[str]:
    """Papers Scholar lists that never reached the corpus, and where to add them."""
    if not miss:
        return []
    L = [f"### {plural(len(miss), 'paper')} absent from the source bibliography", "",
         "Not in the corpus and not rejected — they never arrived. The bibliography",
         "is this pipeline's only input, so the fix is one entry there; adding them",
         "to `data/` would be overwritten on the next run. A BibTeX entry for each,",
         "resolved from arXiv, Crossref or Semantic Scholar where any of them has",
         "it, is in [`tasks/bib_missing.md`](tasks/bib_missing.md) — check the",
         "author list before pasting: it is the index's, not yours.", ""]
    # Derived from `sources.bibtex_url` rather than written out, because the one
    # external file this whole pipeline depends on is the one link worth never
    # letting drift. raw.githubusercontent -> the GitHub editor for the same file.
    edit = re.sub(r"^https://raw\.githubusercontent\.com/([^/]+/[^/]+)/(.+)$",
                  r"https://github.com/\1/edit/\2",
                  ((cfg or {}).get("sources") or {}).get("bibtex_url") or "")
    if edit.startswith("https://github.com/"):
        L += [f"Edit it here: <{edit}>", ""]
    L += [f"- [ ] {_cites(r.get('citations'))} — {r.get('year') or '????'} — "
          f"{clipped(r.get('title') or '', 60)}" for r in miss[:12]]
    if len(miss) > 12:
        L += [f"- … and {len(miss) - 12} more in `build/scholar_diff.json`"]
    return L + [""]


def _not_on_profile(gone: list[dict], sc: dict) -> list[str]:
    """The corpus's papers whose title is not in the profile listing.

    The mirror of `_absent_from_bib`. The listing shows one title per record, so a paper
    Scholar has folded into another record is indistinguishable here from one Scholar does
    not have, and the heading claims only what the check knows.
    """
    if not gone:
        return []
    cit = sum(p.get("citations") or 0 for p in gone)
    # An upper bound, never a loss. On a merged record the citations are present, counted,
    # and on the surviving title.
    total = ([f"Together these carry **{cit} citations** in the corpus. Treat that as",
              "the most this could be worth, not as citations you are missing — on a",
              "merged record they are already counted under the surviving title."]
             if cit else [])
    L = [f"### {plural(len(gone), 'paper')} whose title does not appear on your Scholar "
         "profile",
         "",
         "That is all this check knows, and the heading says so deliberately. It reads",
         "the profile listing, which shows **one title per record** — so a paper Scholar",
         "has folded into another record is indistinguishable here from a paper Scholar",
         "does not have. Both look like a title that is not in the list.",
         "",
         "**So check for a merge before adding anything.** Scholar merges a call for",
         "papers into the findings paper of the same workshop, and a preprint into its",
         "retitled successor — the citations are all on the surviving record, which is",
         "the outcome you want. Adding the folded paper by hand does not recover",
         "anything; it creates a second record that splits future citations.",
         "",
         "Open <https://scholar.google.com/citations?user="
         f"{sc.get('scholar_profile')}&view_op=list_works&sortby=pubdate> and look for",
         "the related record — the findings paper, the newer title. If your paper is",
         "inside it, decline the line here and you will not be asked again. Only if",
         "nothing on the profile covers it is *+ → Add article manually* the fix."]
    L += total + ["",
                  "Declining is one line in [`data/declines.yaml`](data/declines.yaml)"
                  " under `items:`.", ""]
    for p in gone:
        ref = (f" <https://arxiv.org/abs/{p['arxiv']}>" if p.get("arxiv")
               else f" <https://doi.org/{p['doi']}>" if p.get("doi")
               else f" <{p['url']}>" if p.get("url") else "")
        L += [f"- [ ] {_cites(p.get('citations'))} — {p.get('year') or '????'} — "
              f"{clipped(title_of(p), 58)}{ref}"]
    return L + [""]


def _bib_behind_arxiv(fix: list[dict]) -> list[str]:
    """Title variants arXiv confirms Scholar on, so the .bib entry is the stale side."""
    if not fix:
        return []
    L = [f"### {plural(len(fix), 'paper')} whose bibliography title is behind arXiv", "",
         "arXiv states the title Scholar shows, so the source entry is the stale",
         "one and there is nothing to decide: correct the title in the source",
         "bibliography and re-run. Until then the two surfaces answer a title query",
         "differently, which is the exact failure this repo exists to prevent.", ""]
    return L + [f"- [ ] `{v.get('slug')}`\n"
                f"      - arXiv and Scholar: {clipped(v.get('scholar') or '', 56)}\n"
                f"      - the .bib entry:    {clipped(v.get('corpus') or '', 56)}"
                for v in fix] + [""]


def _no_arxiv_titles(blind: list[dict]) -> list[str]:
    """One line saying which side is behind cannot be known without arXiv's own titles."""
    if not blind:
        return []
    return [f"{plural(len(blind), 'paper')} under two titles are not split between the "
            "two headings here, because `build/title_diffs.json` is not there and arXiv's "
            "own titles are the only thing that separates them. Run `python update.py "
            "--step collect` and this run again.", ""]


def _title_is_a_ruling(call: list[dict]) -> list[str]:
    """Title variants arXiv confirms neither of, so which is canonical is a judgement."""
    if not call:
        return []
    L = [f"### {plural(len(call), 'paper')} under two titles, with no arXiv record to "
         "break the tie", "",
         "Same paper, two names, and arXiv confirms neither — so this one is a",
         "judgement. Decide which is canonical and set it in",
         "[`data/overrides.yaml`](data/overrides.yaml).", ""]
    return L + [f"- [ ] `{v.get('slug')}`\n"
                f"      - scholar: {clipped(v.get('scholar') or '', 64)}\n"
                f"      - corpus:  {clipped(v.get('corpus') or '', 64)}"
                for v in call] + [""]


def _listed_twice(dup: list[dict], sc: dict) -> list[str]:
    """Papers with two rows on the profile, and the sort that puts the two side by side."""
    if not dup:
        return []
    L = [f"### {plural(len(dup), 'paper')} listed twice on Scholar", "",
         "Two rows for one paper splits its citation count, and nothing here can fix",
         "it: tick both rows and press *Merge*. Both titles are below, because on the",
         "profile they sort apart and neither reads as the other's duplicate.", "",
         "Open <https://scholar.google.com/citations?user="
         f"{sc.get('scholar_profile')}&view_op=list_works&sortby=title>.", ""]
    for d in dup:
        L += [f"- [ ] `{d.get('slug')}`",
              f"      - one row: {(d.get('corpus') or '')[:64]}",
              f"      - the other: {(d.get('scholar') or '')[:64]}"
              + (f" — <{d['scholar_url']}>" if d.get("scholar_url") else "")]
    return L + [""]


def scholar_split_records(st: dict) -> list[str]:
    """The worklist section for `build/scholar_strays.json`, or nothing.

    Only the two passes whose remedy is one merge each. The `not in the bibliography`
    pass lands in `tasks/scholar_strays.md` and not here -- it is a list to read, not a
    list of edits, and most of its rows are other people.
    """
    rows = [dict(r, kind="undercount") for r in st.get("undercounted") or []]
    rows += [dict(r, kind="name form") for r in st.get("typo_records") or []
             if r.get("matched")]
    rows += [dict(r, kind="split", gap=sum(x["citations"] for x in r["records"][1:]))
             for r in st.get("split_records") or []]
    if not rows:
        return []
    rows.sort(key=lambda r: -(r.get("gap") or r.get("citations") or 0))
    at_stake = sum(r.get("gap") or r.get("citations") or 0 for r in rows)
    L = [f"## Citations on a Scholar record you cannot see ({len(rows)}, "
         f"~{at_stake} citations)", "",
         "Scholar indexes preprints and theses the APIs do not, so a profile row should",
         "always count *more* than OpenAlex and Semantic Scholar. Where it counts less,",
         "the rest of the count is on a second record Scholar parsed out of somebody's",
         "reference list — a mangled title, a misspelled author, initials only. Merging",
         "the two adds those citations to yours.", "",
         "OpenAlex holding one title twice is the same fault from the other side. A parser",
         "that split the record there usually split it at Scholar too, and the count on",
         "the smaller copy is what a merge recovers.", "",
         "Each row is a search. Open it, and if a result is your paper under a second",
         "record, tick your own row and that one on your profile and press *Merge*. A",
         "gap can also be plain indexing lag, so read the result before merging: a wrong",
         "merge attaches somebody else's paper to your name.", "",
         "Full detail, including the 200-odd records filed under an initials-only form of",
         "your name: [`tasks/scholar_strays.md`](tasks/scholar_strays.md).", ""]
    for r in rows[:15]:
        gap = r.get("gap") or r.get("citations") or 0
        why = (f"Scholar {r['scholar_citations']} vs {r['index_citations']} at the APIs"
               if r["kind"] == "undercount" else
               f"filed as *{r.get('searched_as')}* at {r.get('index')}"
               if r["kind"] == "name form" else
               f"{len(r['records'])} OpenAlex records for one title")
        L += [f"- [ ] **{gap} citations** — {clipped(r.get('title') or '', 64)}",
              f"      - {why}",
              f"      - [search Scholar for it]({r['search']})"]
    if len(rows) > 15:
        L.append(f"- … and {len(rows) - 15} more in "
                 "[`tasks/scholar_strays.md`](tasks/scholar_strays.md), same order")
    return L + [""]


def wikidata_coauthors(st: dict) -> list[str]:
    """The worklist section for `build/wikidata_coauthors.json`, or nothing.

    Only the strings a name is all there is to go on. The rest -- an ORCID or a DBLP page
    matched, a venue resolved, a language read off the bibliography -- is written by
    `scripts/wikidata_coauthors.py --apply` and reported here without a checkbox.
    """
    left = (st.get("review") or 0) + (st.get("leftover") or 0)
    batch = (st.get("edits") or 0) + (st.get("venues") or 0) + (st.get("fills") or 0)
    # No section when only the batchable half is outstanding: this page asks the author for
    # things, and a statement `--apply` writes is not one of them.
    if not left:
        return []
    L = [f"## Wikidata author strings ({left} by hand)", "",
         "Every paper item lists you as *author* and each co-author as *author name",
         "string*, which is a literal nothing can join on — so each item hangs off your",
         "item alone. Resolving a string to that person's own item is what connects them,",
         "and many independent paths into your item is the point of having them at all.", ""]
    L += [f"- [ ] **{left} strings across {st.get('papers_left', 0)} papers** — one "
          "Author Disambiguator pass per paper, most-cited first",
          "      - the links, and the candidate items found for each name: "
          "[`tasks/wikidata_coauthors.md`](tasks/wikidata_coauthors.md)"]
    if st.get("dropped"):
        L += [f"      - {st['dropped']} name matches are left out as namesakes, on a "
              "stated occupation nothing like research"]
    if batch:
        L += ["",
              f"{batch} more statement{'s' * (batch != 1)} need no decision from you — an "
              "ORCID or a DBLP",
              "page matched the name, or the value came straight from the bibliography.",
              "`python scripts/wikidata_coauthors.py --apply` writes them."]
    return L + [""]


def wikidata_people(st: dict) -> list[str]:
    """The worklist section for `build/wikidata_people.json`, or nothing.

    Only the people no public record decides. Creating the rest, and adding the ORCID to the
    item a shared paper or employer identifies, is `scripts/wikidata_people.py --apply`.
    """
    held = sorted(st.get("held_people") or [],
                  key=lambda x: (-x.get("papers", 0), x["label"]))
    if not held:
        return []
    L = [f"## Co-authors who may already have a Wikidata item ({len(held)})", "",
         "Wikidata carries a human item under each of these names and none of them states an",
         "ORCID, so each is either this co-author reached from a paper rather than a profile",
         "or somebody else of the same name. Under each name is what every candidate item",
         "says about itself, the ones stating a research occupation first. The answer is",
         "which line is them, or `new` if none is.",
         "",
         "Each name also carries what its ORCID record states. That identifier came from",
         "OpenAlex reading a paper whose own metadata names no author identifiers, so on a",
         "common name it can be a namesake's — a record listing papers in another field",
         "entirely is one, and the answer for it is `no`, which drops the ORCID for good.",
         "",
         "Paste into [`data/overrides.yaml`](data/overrides.yaml) under `wikidata_people`,",
         "correcting the QIDs that are wrong:",
         "",
         "```yaml",
         "wikidata_people:"]
    for p in held:
        rest = [n["qid"] for n in p["namesakes"][1:4]]
        # The alternatives inline, because the first candidate is the likeliest and not the
        # answer -- a block pasted unread would put an ORCID on a racing cyclist.
        L.append(f"  {p['orcid']}: {p['namesakes'][0]['qid']}   # {p['label']}"
                 + (" — or " + ", ".join(rest) if rest else "")
                 + (", …" if len(p["namesakes"]) > 4 else "")
                 + ", or new, or no")
    L += ["```", ""]
    for p in held:
        papers = p.get("papers", 0)
        L.append(f"- [ ] **{p['label']}** ({papers} paper{'' if papers == 1 else 's'} with "
                 f"you) — [their ORCID record](https://orcid.org/{p['orcid']}) states "
                 f"{p.get('record_says') or 'nothing public beyond the name'}")
        for n in p["namesakes"]:
            L.append(f"  - [{n['qid']}](https://www.wikidata.org/wiki/{n['qid']}) — "
                     f"{n.get('says') or 'states nothing beyond the name'}")
    L += ["",
          "Nothing else follows by hand. The next run adds the ORCID to the item named, or",
          "creates a separate one, and writes the *author* statements from it."]
    if st.get("decided"):
        L += ["",
              f"{st['decided']} more needed no answer -- a paper or an employer both records",
              "name says which item they are, and "
              "[`tasks/wikidata_people.md`](tasks/wikidata_people.md)",
              "lists which and why."]
    return L + [""]


def wikidata_orgs(st: dict) -> list[str]:
    """The worklist section for `build/wikidata_orgs.json`, or nothing.

    Only the two things a public page cannot settle -- a name matching several items, and a
    fact only the author knows. Creating the items and writing the edges into them is
    `scripts/wikidata_orgs.py --apply`, reported here without a checkbox.
    """
    asks = (st.get("ambiguous") or []), (st.get("needs") or 0)
    if not any(asks):
        return []
    L = ["## Wikidata items for the groups", "",
         "Some of the work in the corpus is run by groups Wikidata has no item for, so a",
         "paper cannot say what it is part of and a group cannot say what it produced.",
         "Every statement written cites the public page it came from.", ""]
    if st.get("ambiguous"):
        L += [f"- [ ] **{len(st['ambiguous'])} names match more than one item** — pick the "
              "right one by hand, or the group has an item already",
              "      - the candidates: "
              "[`tasks/wikidata_orgs.md`](tasks/wikidata_orgs.md)"]
    if st.get("needs"):
        L += [f"- [ ] **{st['needs']} statements wait on a fact only you have** — "
              "add them to [`data/wikidata_orgs.yaml`](data/wikidata_orgs.yaml)",
              "      - each one, and why the public pages do not settle it: "
              "[`tasks/wikidata_orgs.md`](tasks/wikidata_orgs.md)"]
    todo = (len(st.get("create") or []), st.get("edges") or 0)
    if any(todo):
        names = [st["state"][s].get("label") or s for s in st.get("create") or []]
        L += ["",
              ("%s and %d edge%s into them wait on nothing"
               % (", ".join(names) or "No item", todo[1], "s" * (todo[1] != 1))
               if todo[0] else
               "%d edge%s into those items wait on nothing"
               % (todo[1], "s" * (todo[1] != 1))) + " —",
              "`python scripts/wikidata_orgs.py --apply` creates and writes them."]
    return L + [""]


def upstream_gaps(papers: list[dict], cfg) -> list[str]:
    """Papers the corpus has only because an override put them there, and the field
    corrections it carries privately.

    `extra_arxiv` and `extra_openreview` cover the interval before the entry lands in the
    bibliography, and both files say to delete the line after. Nothing else reports them,
    since the Scholar block finds missing papers by diffing Scholar against the corpus and an
    override closes exactly that gap.

    `_override` is provenance. `collect.py` sets it on records it adds from an override and it
    disappears once the bibliography's own entry merges, so a paper still carrying it is still
    absent upstream. The second and third blocks read `overrides.yaml` too, for lines left
    behind after a paste lands and for `fields:` corrections upstream has not absorbed.
    """
    L = []
    pend = sorted((p for p in papers if p.get("_override")),
                  key=lambda p: -(p.get("citations") or 0))
    edit = re.sub(r"^https://raw\.githubusercontent\.com/([^/]+/[^/]+)/(.+)$",
                  r"https://github.com/\1/edit/\2",
                  ((cfg or {}).get("sources") or {}).get("bibtex_url") or "")
    if pend:
        L += [f"## {len(pend)} paper{'s' * (len(pend) != 1)} in the corpus that the "
              f"bibliography does not have", "",
              "Added by `extra_arxiv` or `extra_openreview` in",
              "[`data/overrides.yaml`](data/overrides.yaml), so each has a page and a "
              "canonical",
              "URL already — this is not about the site. It is that the bibliography is this",
              "pipeline's only real input, and every run these papers depend on a line in an",
              "override file instead. Paste the entry upstream and delete that line.", ""]
        if edit.startswith("https://github.com/"):
            L += [f"Edit the bibliography here: <{edit}>", ""]
    for p in pend[:5]:
        # Synthesised from the fetched record, which is why the citation key is not one to
        # keep: the bibliography assigns keys, and the reason these records carry no
        # `bibtex` of their own is that an invented key competing with the published one
        # is the split this project exists to avoid. Paste the fields, not the key.
        L += [f"- [ ] **{clipped(title_of(p), 66)}** — "
              f"`{p['_override']}`, {p.get('citations') or 0} cites", "",
              "  ```bibtex", *(f"  {ln}" for ln in synth_bibtex(p).splitlines()),
              "  ```", ""]
    if len(pend) > 5:
        L += [f"- … and {len(pend) - 5} more, listed in `data/overrides.yaml`", ""]

    # A line is spent when the corpus has its paper *without* the marker: the record came
    # from the bibliography this run, so the override added nothing. Matched on the same
    # keys `collect.py` adds by -- an arXiv id, a normalised title -- so a line that never
    # resolved to a paper at all is not reported here as done. That one is already loud:
    # the collector prints `! extra_openreview: OpenReview has no accepted paper titled`.
    ov = read_overrides()
    from_bib = [p for p in papers if not p.get("_override")]
    ids = {p["arxiv"] for p in from_bib if p.get("arxiv")}
    titles = {norm_title(p.get("title") or "") for p in from_bib}
    spent = [("extra_arxiv", str(i).strip()) for i in (ov.get("extra_arxiv") or [])
             if str(i).strip() in ids]
    spent += [("extra_openreview", str(t).strip())
              for t in (ov.get("extra_openreview") or [])
              if norm_title(str(t).strip()) in titles]
    if spent:
        L += [f"## {len(spent)} override line{'s' * (len(spent) != 1)} the bibliography "
              f"has made redundant", "",
              "The good outcome, and the last step of it. Each of these is in",
              "[`data/overrides.yaml`](data/overrides.yaml) to cover the interval before the",
              "paper reached the bibliography, and the bibliography now has it — the corpus",
              "record carries its published citation key. Deleting the line changes no",
              "output; leaving it means the next reader cannot tell which lines are still",
              "load-bearing, which is how a stopgap becomes part of the design.", ""]
        for k, v in spent:
            # Whole, not clipped: this is the line to find and delete, so a fragment of it
            # is not something the reader can search for.
            L.append(f"- [ ] `{k}:` delete `{v}`")
        L.append("")

    # A `fields:` correction the bibliography could carry itself. Matched on the value
    # anywhere in the entry rather than on a field name, because a venue lives in
    # `booktitle` in one entry and `institution` in the next -- the ICML position paper's
    # venue is already upstream under `institution`, and only its DOI and URL are missing.
    BIBFIELD = {"doi": "doi", "url": "url", "year": "year", "venue": "booktitle"}
    by_slug = {p.get("slug"): p for p in papers}
    priv = []                     # one row per paper -- one visit to one entry
    for slug, fix in (ov.get("fields") or {}).items():
        rec = by_slug.get(slug) or {}
        bib = (rec.get("bibtex") or "").lower()
        want = [(f, str(v)) for f, v in (fix or {}).items() if v and str(v).lower() not in bib]
        if want:
            priv.append((rec, slug, want))
    if priv:
        n = sum(len(w) for _r, _s, w in priv)
        # Both numbers, because they differ and the reader can see only one of them: two
        # corrections in one entry is one visit, and a header saying 2 above a single
        # checkbox reads as a miscount.
        L += [f"## {n} field correction{'s' * (n != 1)} the bibliography does not carry "
              f"({len(priv)} entr{'y' if len(priv) == 1 else 'ies'})", "",
              "`fields:` in [`data/overrides.yaml`](data/overrides.yaml) corrects these for",
              "the corpus and nothing else. Scholar, Semantic Scholar and OpenAlex read the",
              "paper's own record, so a correction that stays here is one they never get.",
              "Add them to the entry upstream, then delete the override lines.", ""]
        if edit.startswith("https://github.com/"):
            L += [f"Edit the bibliography here: <{edit}>", ""]
        for rec, slug, want in priv:
            title = clipped(title_of(rec) or slug, 60)
            key = rec.get("key") or ""
            L += [f"- [ ] **{title}**" + (f" — entry `{key}`" if key else ""), "",
                  "  ```bibtex"]
            L += [f"  {BIBFIELD[f]:<12} = {{{v}}}," if f in BIBFIELD
                  else f"  % {f} = {v}   <- field name depends on the entry type"
                  for f, v in want]
            L += ["  ```", ""]
    return L


def orcid_missing_items(slugs: list[str], by_slug: dict) -> list[str]:
    """The missing papers, with the entry ORCID will import shown per paper.

    ORCID's BibTeX route takes a *file*, so the payload the reader needs at hand is a path --
    but a file they cannot see the inside of is one they have to open in another tab before
    putting it on their own record. So up to three entries are shown inline, which is the
    length at which this reads as "check these" instead of "scroll past this". Above that,
    titles and citations only: the decision has collapsed into one upload, and
    `tasks/orcid_missing.md` carries the per-paper detail.
    """
    rows = [by_slug.get(s) or {"slug": s} for s in slugs]
    if len(rows) > 3:
        return ([f"- [ ] {p.get('citations') or 0} cites — "
                 f"{clipped(p.get('title') or p['slug'], 66)}" for p in rows[:8]]
                + ([f"- … and {len(rows) - 8} more in "
                    "[`tasks/orcid_missing.md`](tasks/orcid_missing.md)"]
                   if len(rows) > 8 else []))
    out = []
    for p in rows:
        out += [f"- [ ] **{clipped(p.get('title') or p['slug'], 66)}** — "
                f"{p.get('citations') or 0} cites — what the file will add:", "",
                "  ```bibtex",
                *(f"  {ln}" for ln in (p.get("bibtex") or synth_bibtex(p)).strip().splitlines()),
                "  ```", ""]
    return out


def wikipedia_checks(wiki: dict) -> list[str]:
    """Articles that name the author or a coined term, each with the sentence saying so.

    Read from `build/wikipedia_state.json` because the ~100 API calls behind it belong to
    the audit step. One row per article rather than per term: the row is a page to read,
    and the quoted line under it is what makes reading optional.
    """

    def arts(v):
        """`(title, says)` pairs, tolerating a state file written before `says` existed."""
        return [(a, "") if isinstance(a, str) else (a.get("title") or "", a.get("says") or "")
                for a in v or []]

    rows = [(t, t, s) for t, s in arts(wiki.get("already_mentions"))]
    rows += [(c["term"], a, s) for c in wiki.get("checks") or []
             for a, s in arts(c.get("articles"))]
    if not rows:
        return []
    L = [f"## Wikipedia mentions {len({t for t, _a, _s in rows})} of your coinages across "
         f"{len({a for _t, a, _s in rows})} article(s) — check the facts", "",
         "Wikipedia carries roughly half the citations in AI answers, and WP:COI",
         "means you may not edit these. What you *can* do is the thing only an",
         "author can: notice that a description is wrong. The quoted line is what the",
         "article says — if it reads correctly, tick it and move on, which is the",
         "expected outcome.",
         "",
         "A correction goes on the talk page, with the corrected value and the page",
         "or table it comes from. Never in the article, and never a citation of your",
         "own work — that is the edit that gets reverted on sight.", ""]
    for term, art, says in rows:
        q = art.replace(" ", "_")
        # An article naming the author is its own subject, so naming it twice reads as noise.
        what = "" if term == art else f"**{term}** in "
        L.append(f"- [ ] {what}[{art}](https://en.wikipedia.org/wiki/{q}) "
                 f"([talk](https://en.wikipedia.org/wiki/Talk:{q}))")
        if says:
            L.append(f"  > {says}")
    return L + ["",
                f"The {wiki.get('absent', 0)} coinages Wikipedia does not mention are "
                f"listed in",
                "[`tasks/wikipedia.md`](tasks/wikipedia.md) as deliberately not "
                "actionable, along with",
                "the field articles you could improve with other people's sources.", ""]


def sidecar_drafts(papers: list[dict]) -> list[str]:
    """Drafts waiting to be read, and papers with no draft yet.

    Two different asks, and conflating them is what made this section unusable: verifying a
    draft is minutes, writing one from a blank file is not. Regenerates the review page as a
    side effect, so the link it prints is this run's.
    """
    by_slug = {p["slug"]: p for p in papers}
    L = []
    # Two different asks, and conflating them is what made this section unusable:
    # verifying a draft is minutes, writing one from a blank file is not. Drafts are
    # in data/sidecars/drafts/ and nothing reads them until you promote one.
    drafted = sorted(os.path.basename(f)[:-3] for f in
                     glob.glob(os.path.join(DATA, "sidecars", "drafts", "*.md")))
    # A draft written against rules that have since moved is not work for a person: it
    # cannot be accepted as it stands, so it does not belong in the verification section
    # above. It belongs with the undrafted papers below, because the remedy is identical
    # -- re-run the drafter -- and giving it a heading of its own would report the same
    # seventeen papers twice under two different counts.
    from sidecar_io import held, spec_sha
    from sidecar_review import write_review_page
    keep = held(spec_sha())
    stale_drafts = [s for s in drafted if s not in keep]
    drafted = [s for s in drafted if s in keep]
    no_side = [p for p in papers if not has_live_sidecar(p["slug"])]
    if drafted:
        # One page with every draft on it, already checked, regenerated by this run. The
        # review is the only item on this worklist that is reading rather than pasting,
        # and a command per paper is the wrong shape for reading: it should be a link.
        page = write_review_page(papers)
        L += [f"## Sidecar drafts awaiting your verification ({len(drafted)})", "",
                  "Drafted from each paper's own full text: claims with their magnitudes,",
                  "scope conditions, terminology and likely misreadings. Every number is a",
                  "machine's reading and needs your eyes — but you are correcting a page,",
                  "not writing one.",
                  "",
                  "**Read " + (f"all {len(drafted)}" if len(drafted) > 1 else "it")
                  + " here — one page, no commands:**",
                  f"<file://{page}>",
                  "",
                  "This run generated it. Every figure a draft states is printed beside the",
                  "paper's own sentence containing that number, and anything the paper does",
                  "not say is flagged in red at the top of the page and again on the claim —",
                  "so the check is comparing two lines, never opening a PDF. The only thing",
                  "left is `--accept`, which is below and which publishes the page under your",
                  "name.", ""]
        for slug in sorted(drafted, key=lambda s: -((by_slug.get(s) or {})
                                                    .get("citations") or 0))[:10]:
            p = by_slug.get(slug) or {}
            # A draft for a paper that already has a live sidecar is a replacement, and
            # that changes what reviewing it means: you are comparing two readings, one
            # of which is already published, rather than checking a new page. `--accept`
            # refuses it without `--replace` for the same reason.
            mark = "  **replaces the live sidecar**" if has_live_sidecar(slug) else ""
            title = title_of(p) or slug
            L.append(f"- [ ] **{clipped(title, 60)}** — "
                         f"{p.get('citations') or 0} cites{mark}")
            L.append(f"      - read: [in the review page](file://{page}#{slug}) · "
                         f"[raw draft](data/sidecars/drafts/{slug}.md)")
            L.append(f"      - publish: `python scripts/draft_sidecars.py --accept "
                         f"{slug}{' --replace' if has_live_sidecar(slug) else ''}`")
        L.append("")
    todraft = [p for p in no_side if p["slug"] not in set(drafted)]
    if todraft:
        # The stale count is stated here, not given a section, so that somebody who
        # opens data/sidecars/drafts/ and finds files in it is not left wondering why
        # they are missing from the list above.
        stale_note = ([f"{len(stale_drafts)} of these already have a draft file on disk,"
                       " written against sidecar rules",
                       "that have since changed. `--accept` refuses them and the next run"
                       " overwrites",
                       "them, so do not spend an evening reading one; they need the same"
                       " re-run as the rest.", ""] if stale_drafts else [])
        L += [f"## Sidecars not yet drafted ({len(todraft)}/{len(papers)})", ""] \
                 + stale_note + \
                 ["**Not yours.** Drafting reads each paper's full text and writes claims,",
                  "scope and glosses into a draft file — agent work, and the queue drains",
                  "when you ask an agent for a batch or when a full run takes one. It is here",
                  "so the number is visible, not so you will do it. What comes back is the",
                  "section above, and that one is yours.",
                  "",
                  "```bash",
                  "python scripts/draft_sidecars.py --review      # every paper: live, draft,"
                  " or neither",
                  "python scripts/draft_sidecars.py --limit 20    # queue the next 20 (then"
                  " an agent fills them)",
                  "python scripts/draft_sidecars.py --ingest      # fold the answers in",
                  "```", "",
                  # "How do I find them" was a fair question: this section listed six
                  # titles and named no file, no slug and no way to see the other hundred.
                  # The slug is the handle every command above takes and the filename every
                  # sidecar has, so it is what the list has to carry.
                  "`--review` is the whole list; the six below are the top of it by",
                  "citations, which is where drafting pays. A draft lands in",
                  "`data/sidecars/drafts/<slug>.md` and nothing reads it until you",
                  "`--accept` it, which moves it to `data/sidecars/<slug>.md` — the",
                  "published one, and the only one the site builds from.", "",
                  "`update.py` also drafts a batch on every run, so this number falls on",
                  "its own.", ""]
        for p in sorted(todraft, key=lambda p: -(p.get("citations") or 0))[:6]:
            L.append(f"- `{p['slug']}` — {p.get('citations') or 0} cites — "
                         f"{clipped(title_of(p), 56)}")
        L.append("")
    return L


def starving_papers(papers: list[dict]) -> list[str]:
    """Papers no fetcher can reach the text of, so no sidecar can ever be drafted for them.

    Upstream of `sidecar_drafts`: without this they sit in "not yet drafted" looking like a
    queue. The whole task is putting a PDF in `data/fulltext/`.
    """
    L = []
    # Papers whose text no fetcher can reach, upstream of the two sidecar sections above: a
    # sidecar is drafted from full text, so these can never be drafted and would otherwise sit
    # in "not yet drafted" looking like a queue. A paper the pipeline cannot read is a task,
    # and the whole task is putting a file somewhere.
    starved = []
    for p in papers:
        if os.path.exists(os.path.join(ROOT, "data", "sidecars", f"{p['slug']}.md")):
            continue
        if any(os.path.exists(os.path.join(ROOT, "data", "fulltext", p["slug"] + e))
               for e in (".pdf", ".txt")):
            continue
        f = os.path.join(ROOT, "build", "fulltext", f"{p['slug']}.txt")
        try:
            if os.path.getsize(f) >= 2000:
                continue
        except OSError:
            pass
        starved.append(p)
    if starved:
        L += [f"## Papers whose full text nothing can fetch ({len(starved)})", "",
                  "Every one of these is a real paper that is not on arXiv, so there is no",
                  "HTML rendering and no open PDF to extract — a Nature paywall, an Elsevier",
                  "page that serves an open-access licence to browsers and 403s to everything",
                  "else, an SSRN download behind a click. They are not slow, they are blocked,",
                  "and no rerun will change that.",
                  "",
                  # Said as a count, not as "all three": this list shrinks as the PDFs
                  # land and grows when a paywalled paper enters the corpus, and prose
                  # with a number frozen into it is how a generated file starts
                  # disagreeing with its own heading.
                  f"You are an author on {'it' if len(starved) == 1 else 'each of them'}, "
                  f"so you already have the PDF{'s' * (len(starved) != 1)}. Drop "
                  f"{'it' if len(starved) == 1 else 'each one'} in as",
                  "`data/fulltext/<slug>.pdf` — the directory is gitignored, so the PDF stays",
                  "on your machine and only the sidecar it produces is committed. That path is",
                  "read before any network source, so the next run picks it up and the paper",
                  "joins the drafting queue.", ""]
        for p in sorted(starved, key=lambda p: -(p.get("citations") or 0)):
            title = clipped(title_of(p), 60)
            L.append(f"- [ ] **{title}** "
                         f"— {p.get('citations') or 0} cites, "
                         f"{p.get('venue_display') or 'no venue'}")
            # Where the file is, not just where it goes. "You already have the PDF" is
            # true and still leaves a search: the page this project already knows the URL
            # of is the page the PDF is one click behind.
            src = p.get("url") or p.get("openreview") or p.get("doi_url") or (
                f"https://doi.org/{p['doi']}" if p.get("doi") else "")
            L.append(f"      - get it from <{src}>" if src else
                         "      - no landing page known — wherever your own copy is")
            L.append(f"      - save it as `data/fulltext/{p['slug']}.pdf`")
        L.append("")
    return L


def identity_surfaces(papers: list[dict], state: dict, ids: dict) -> list[str]:
    """One section per external surface with something open, or one line saying none has.

    Each surface below returns (predicate, heading, body). Built as data so adding a surface
    is one entry in the list, and so a surface with nothing open cannot print a heading. They
    are defined after this function, in the order they print.
    """
    by_slug = {p["slug"]: p for p in papers}
    surfaces = [
        orcid_missing(state, papers, by_slug),
        orcid_wrong_works(state),
        orcid_misfiled(state, by_slug),
        orcid_duplicates(state),
        orcid_facets(state),
        s2_second_record(papers, ids),
        wikidata_statement_gaps(state),
        wikidata_missing_papers(state),
        openalex_duplicate_profiles(ids),
    ]
    open_items = [(h, b) for pred, h, b in surfaces if pred]
    if not open_items:
        return ["## Identity surfaces", "",
                "Nothing open. ORCID, Semantic Scholar, Wikidata and OpenAlex all match",
                "`config.yaml` as of the last audit.", ""]
    L = [f"## Identity surfaces ({len(open_items)} open)", "",
         "Each is blocked on an account you are logged into, not on knowing what to",
         "do. `python scripts/identity_tasks.py` regenerates every payload under",
         "`tasks/` — committed, so browsable on GitHub.", ""]
    for h, b in open_items:
        L += [h, ""] + b
    return L


def orcid_missing(state: dict, papers: list[dict], by_slug: dict) -> tuple[bool, str, list[str]]:
    """The papers absent from the ORCID record, as one BibTeX upload."""
    o_miss = state.get("orcid_missing_papers") or []
    body = [
        "Highest leverage on this page. Semantic Scholar's disambiguation and",
        "OpenAlex's profile merges are both ORCID-driven, so this is the one fix that",
        "makes the others more likely to fix themselves.", "",
        "One upload, not one form per paper. At <https://orcid.org/my-orcid#works>:",
        "*+ Add → Add BibTeX → Choose file* →",
        "[`tasks/orcid_missing.bib`](tasks/orcid_missing.bib) (only the missing ones) or",
        "[`tasks/orcid_import.bib`](tasks/orcid_import.bib) (all of them; ORCID groups on",
        "shared identifiers, so re-importing what is already there merges rather than",
        "duplicates). It previews the entries and you confirm — nothing lands unseen.",
        "Why it matters, once:",
        "[docs/SETUP.md §1](docs/SETUP.md#1-orcid--populate-it-then-wire-it-everywhere).", "",
    ] + orcid_missing_items(o_miss, by_slug)
    return (bool(o_miss),
            f"### ORCID is missing {len(o_miss)} of your {len(papers)} papers", body)


def orcid_wrong_works(state: dict) -> tuple[bool, str, list[str]]:
    """Works the ORCID record claims that are not the author's."""
    o_conf = state.get("orcid_strays_confirmed") or []
    head = (f"### ORCID lists {len(o_conf)} work that is not yours" if len(o_conf) == 1 else
            f"### ORCID lists {len(o_conf)} works that are not yours")
    body = [
        "A wrong work on your record is worse than a missing one: it is the thing that",
        "makes an automated merge distrust the record. *Works → the entry → Delete.*",
        "Put-codes and titles: `tasks/orcid_remove.md`.", "",
    ]
    return bool(o_conf), head, body


def orcid_misfiled(state: dict, by_slug: dict) -> tuple[bool, str, list[str]]:
    """Works whose identifier belongs to a different paper.

    Prints before the duplicate and the missing-paper surfaces, because it is what puts
    entries in them and each of their obvious fixes makes it worse.
    """
    o_bad = state.get("orcid_misfiled_ids") or []

    def item(b: dict) -> list[str]:
        """One misfiled identifier, carrying every value the edit needs -- the put-code, the
        identifier to take off, and the one to put on.
        """
        p = by_slug.get(b.get("should_be")) or {}
        title = title_of(p) or b.get("should_be") or "?"
        out = [f"- [ ] **{clipped(title, 66)}** — put-code `{b['put']}`"]
        doi = b.get("carried_doi")
        if doi:
            # Linked, because the link is the evidence: following the identifier that is
            # on your own record lands on a paper that is not this one.
            out.append(f"      - remove `{doi}` — it resolves to "
                       f"[{clipped(b.get('carried_title') or 'another paper', 44)}]"
                       f"(https://doi.org/{doi}), a different paper")
        else:
            out.append("      - remove the identifier it carries: "
                       f"`{', '.join(b.get('carries') or ['?'])}`")
        if b.get("should_carry"):
            out.append(f"      - add `{b['should_carry']}` — the DOI of the paper this "
                       f"entry actually is")
        elif p.get("arxiv"):
            out.append(f"      - add the arXiv id `{p['arxiv']}`, identifier type "
                       f"`arxiv`. This paper has no DOI, and an entry carrying no "
                       f"identifier at all is what makes ORCID read it as missing")
        else:
            out.append("      - add nothing — this paper has neither a DOI nor an arXiv "
                       "id, so taking the wrong one off is the whole fix")
        return out + [""]

    head = (f"### {len(o_bad)} work on your ORCID carries another paper's identifier"
            if len(o_bad) == 1 else
            f"### {len(o_bad)} works on your ORCID carry another paper's identifier")
    body = [
        "**Do this before the rest of this section.** A work whose DOI belongs to a",
        "different paper is filed by ORCID into *that* paper's group — grouping is on",
        "shared identifiers and there is nothing else it can go on. So the real paper",
        "ends up with no identifier on the record and reads as missing, the group that",
        "absorbed it reads as listed twice, and both of the obvious fixes make it",
        "worse: adding the paper creates a second copy, merging the group destroys a",
        "distinct work.", "",
        "Each item below is one edit, and every value it needs is in the item — the",
        "work to open, the identifier to take off it, the one to put on. Open",
        "<https://orcid.org/my-orcid#works>, find the work by its title, then the pencil",
        "icon → under *Identifiers* replace the DOI → *Save changes*. **Edit it; do not",
        "delete and re-add** — the put-code is what carries the entry's citations and its",
        "source attribution, and a new entry starts with neither.", "",
        "The carried DOI is linked so you can see for yourself that it resolves to",
        "somebody else's paper before you touch anything. Nothing else needs deleting:",
        "one identifier is replaced by another and the work itself stays.", "",
    ] + [ln for b in o_bad for ln in item(b)]
    return bool(o_bad), head, body


def orcid_duplicates(state: dict) -> tuple[bool, str, list[str]]:
    """Papers the ORCID record holds as two groups, to be merged rather than deleted."""
    o_dupg = state.get("orcid_duplicate_groups") or []
    o_bad = state.get("orcid_misfiled_ids") or []

    def item(r: dict) -> list[str]:
        """One duplicate pair: which entry to open, and the one value to paste."""
        if r.get("doi"):
            return [f"- [ ] **{clipped(r['title'], 60)}** — open put-code `{r['keep']}` "
                    f"(*{clipped(r['keep_title'], 38)}*) and add the DOI `{r['doi']}`, which is "
                    f"the one on put-code `{r['folds']}` (*{clipped(r['folds_title'], 38)}*)", ""]
        # No arXiv-DOI entry, or more than two: naming every entry is the honest form,
        # because which one has the venue is a judgement and this is not making it.
        return [f"- [ ] **{clipped(r['title'], 60)}** — {len(r['entries'])} entries: "
                + "; ".join(f"`{e['put']}` ({e['doi'] or 'no DOI'})"
                            for e in r["entries"])
                + ". Open whichever has the venue and add one of the others' DOIs.", ""]

    body = [
        "ORCID groups works that share an identifier. Two groups for one paper means",
        "one copy carries the arXiv DataCite DOI (`10.48550/arXiv.<id>`) and the other",
        "the publisher DOI, so they share no key.", "",
        "**Merge, do not delete.** Both titles are real — one is the preprint's, one is",
        "what the paper was called on acceptance — and adding one entry's DOI to the",
        "other folds them into a single work carrying both, with no entry losing its",
        "citations or its source attribution. Open the **keep** entry at",
        "<https://orcid.org/my-orcid#works>, the pencil icon → **+ Add identifier** →",
        "type `doi` → paste the value below → *Save*. The pair collapses on the next",
        "page load.", "",
    ] + [ln for r in (state.get("orcid_duplicate_pairs") or []) for ln in item(r)] + [
        "Delete instead only if you would rather have one entry than a grouped pair —",
        "same number of clicks, and the preprint title stops being findable on your",
        "record.",
        "",
        # Points at the section above when there is one, and at the audit when there is not.
        # A "do that first" whose target is not on the page is an instruction the reader has
        # to go and look for, and the answer is usually "there was nothing".
        ("**Do the misfiled-identifier section above first.**" if o_bad else
         "If [the misfiled-identifier section](tasks/identity_audit.md) ever has"
         " anything in it, do that first."),
        "A work carrying the wrong DOI lands in another paper's group and shows up",
        "here as a duplicate that merging would destroy.", "",
    ]
    return bool(o_dupg), f"### ORCID lists {len(o_dupg)} of your papers twice", body


def orcid_facets(state: dict) -> tuple[bool, str, list[str]]:
    """The ORCID fields beside works -- other names, keywords, websites, canonical URL."""
    facets = ((state.get("orcid_missing_variants") or [])
              + (state.get("orcid_missing_keywords") or [])
              + (state.get("orcid_missing_other_pages") or [])
              + ([] if state.get("orcid_has_canonical_url", True) else ["canonical URL"]))
    body = [
        "Separate from works, and two minutes: *Also known as*, *Keywords*, *Websites*.",
        "Exactly which are missing, with the values ready to paste:",
        "`tasks/identity_audit.md`.", "",
    ]
    return bool(facets), f"### ORCID facet fields ({len(facets)} still empty)", body


def s2_second_record(papers: list[dict], ids: dict) -> tuple[bool, str, list[str]]:
    """The papers Semantic Scholar files under an author record other than the claimed one.

    Names the papers and not just their count, because the URL to paste into the Add Papers
    form is a field on each one.
    """
    strays = sorted([p for p in papers if p.get("s2_author_record") in
                     [a for a in ids["semantic_scholar"]
                      if a != ids["semantic_scholar_primary"]]],
                    key=lambda p: -(p.get("citations") or 0))
    held = held_until("Semantic Scholar —")
    body = [
        "Every S2-backed tool (Elicit, Consensus, SciSpace, most literature agents)",
        "resolves you to one page, so each currently sees about half the corpus.",
        "Support has already been asked to merge the two records and declined, so the",
        "self-service route is the only one: a claimed page can pull papers across one",
        "at a time.", "",
    ] + ([
        f"**Worth waiting until {held} before starting.**",
        "S2 re-clusters authors off ORCID, the ORCID record already asserts every",
        "paper here, and re-clustering would move all of them at no cost to you. It",
        "cannot merge the two records, so the second one stays either way — but the",
        "pastes below may be work that does itself.", "",
    ] if held else []) + [
        f"1. Open your claimed page: <https://www.semanticscholar.org/author/"
        f"{ids['semantic_scholar_primary']}>",
        "2. *Edit Author Page → Add Papers*.",
        "3. Paste a paper's S2 URL, pick it, and choose *the author is correct, but the",
        "   paper is missing from my author page*. Changes appear in about 24 hours.",
        "",
        "Highest-citation first, so stopping early still captures most of the loss.",
        "**Do not claim the second page as well** — a second claimed record is harder to",
        "undo than an unclaimed one, and it makes the split look deliberate.", "",
    ] + [
        f"- [ ] {p.get('citations') or 0} cites — "
        f"{clipped(title_of(p), 56)} — "
        + (f"<https://www.semanticscholar.org/paper/{p['s2_corpus_id']}>"
           if p.get("s2_corpus_id") else
           "**no S2 id known** — search the title on the Add Papers form")
        for p in strays[:12]
    ] + ([f"- … and {len(strays) - 12} more in "
          "[`tasks/s2_merge.md`](tasks/s2_merge.md), same order"]
         if len(strays) > 12 else []) + [""]
    return (len(strays) > 0,
            f"### Semantic Scholar — {len(strays)} papers on a second author record", body)


def wikidata_statement_gaps(state: dict) -> tuple[bool, str, list[str]]:
    """Statements missing from the author's own Wikidata item."""
    body = [
        "Now automatic, and it does **not** need an autoconfirmed account — that is a",
        "QuickStatements rule, not a MediaWiki one. Create a bot password once at",
        "<https://www.wikidata.org/wiki/Special:BotPasswords> (grants: edit existing",
        "pages, create/edit pages), export `WIKIDATA_BOT_USER` and",
        "`WIKIDATA_BOT_PASSWORD`, then:", "",
        "```bash",
        "python scripts/wikidata_apply.py            # dry run: exactly what changes",
        "python scripts/wikidata_apply.py --apply    # write it",
        "```", "",
    ]
    return (bool(state.get("wikidata_gaps")),
            f"### Wikidata — {state.get('wikidata_gaps')} statement gaps on "
            f"{state.get('wikidata') or 'your item'}", body)


def wikidata_missing_papers(state: dict) -> tuple[bool, str, list[str]]:
    """Papers with no Wikidata item, which is the author's call and not only their labour.

    These are permanent pages on a wiki that is not the author's, and the undo is a deletion
    request rather than a click. The count is `creatable` rather than `absent`: a paper with
    neither a DOI nor an arXiv id has no key to check Wikidata against, and the difference is
    reported in the body so the heading and the command under it cannot disagree.
    """
    creatable = state.get("wikidata_papers_creatable")
    nokey = (state.get("wikidata_papers_absent") or 0) - (creatable or 0)
    body = [
        "Same bot password, and the same statements as the QuickStatements batch in",
        "`tasks/wikidata_papers.qs` — which is now only the fallback. This is where",
        f"`{state.get('wikidata') or 'your author item'}` gets the incoming author",
        "links that make a Scholia profile and a SPARQL-answerable corpus exist at",
        "all.", "",
    # Phrased without a subject verb so one paper and forty read the same, since the count
    # reaches 1 as the backlog drains and every agreement here would then be wrong.
    ] + ([
        f"{nokey} more with no item, and not in the command below: no DOI and no",
        "arXiv id, so there is no key to check Wikidata against and creating an item",
        "risks a duplicate nobody can find. Each arrives here once it is deposited",
        "anywhere.", "",
    ] if nokey > 0 else []) + [
        "```bash",
        "python scripts/wikidata_apply.py --papers                    # what it would create",
        "python scripts/wikidata_apply.py --papers --apply --limit 10  # ten of them",
        "```", "",
        "In batches, and this is the reason: ten items finds a wrong statement on item",
        "3 rather than on item 103, and an item is harder to retract than anything else",
        "here. Each one is recorded in `data/wikidata_created.yaml` as it lands, so",
        "stopping and resuming creates nothing twice — the query service lags hours",
        "behind the edit and that file is what covers the gap.", "",
        "Once this list is empty the monthly CI run keeps up with new papers by itself.",
        "It refuses while a backlog exists, so it is doing nothing until you start.",
        "Cautions worth reading once: [`tasks/wikidata_followup.md`]"
        "(tasks/wikidata_followup.md).", "",
    ]
    return (bool(creatable),
            f"### Wikidata — {creatable} of your papers "
            f"{'has' if creatable == 1 else 'have'} no item", body)


def openalex_duplicate_profiles(ids: dict) -> tuple[bool, str, list[str]]:
    """OpenAlex author profiles that should be one."""
    dupes = ids.get("openalex_duplicates") or []
    body = [
        "Lowest priority, and the preferred route is to do nothing here: OpenAlex",
        "disambiguation is ORCID-driven and they are running ORCID-based merges, so",
        "fixing ORCID above may resolve it. If you want it now, the profile IDs to",
        "paste into their *Fix errors* form are in `tasks/openalex_merge.md`.", "",
    ]
    return bool(dupes), f"### OpenAlex — {len(dupes)} duplicate profiles", body


def arxiv_name_typos(papers: list[dict], state: dict) -> list[str]:
    """Papers whose arXiv author list misspells the name, first because everything else reads it.

    Hugging Face, Semantic Scholar, OpenAlex and Scholar all build author identity from arXiv,
    so a wrong character there creates a second author downstream that cannot be merged.
    """
    by_slug = {p["slug"]: p for p in papers}
    L = []
    typos = state.get("arxiv_name_typos") or []
    if typos:
        L += [f"## arXiv spells your name wrong on {len(typos)} papers  — "
                  f"do this before anything downstream", "",
                  "The only item here that is upstream of every other surface. Hugging",
                  "Face, Semantic Scholar, OpenAlex and Google Scholar all build author",
                  "identity from arXiv's author list, so one wrong character does not",
                  "degrade gracefully — it creates a second author who holds that paper's",
                  "citations and cannot be merged into you. Work on the downstream pages",
                  "does not repair it.", "",
                  "A name correction is a **metadata edit**, not a new version: *Update this",
                  "article* on your submission page. You must own the paper first — and note",
                  "the trap: <https://arxiv.org/auth/request-ownership> matches your name",
                  "against the author list, which on these papers is the thing that is",
                  "wrong, so the request can bounce. If it does, ask the submitting",
                  "co-author for the paper password",
                  "(<https://arxiv.org/auth/need-paper-password>), which does not",
                  "name-match.", ""]
        for t in typos:
            p = by_slug.get(t.get("slug")) or {}
            L.append(f"- [ ] [`{t['arxiv']}`](https://arxiv.org/abs/{t['arxiv']}) — "
                         f"reads **{t.get('reads')}** — {clipped(p.get('title') or '', 52)}")
        L += ["", "Full detail: `tasks/arxiv_name_fixes.md`.", ""]
    return L


def arxiv_ownership(state: dict, ident: dict, unowned: set) -> list[str]:
    """arXiv papers the author is not registered as owner of.

    Upstream of the journal-ref section, which the form refuses on a paper you do not own.
    """
    L = []
    if state.get("arxiv_registered") is not None and unowned:
        L += [f"## arXiv: claim ownership of {len(unowned)} papers  — before the journal-refs",
                  "",
                  f"Registered as author on **{state['arxiv_registered']}** of "
                  f"**{state['arxiv_total']}** arXiv papers. arXiv tracks this separately from",
                  "authorship: it defaults to whoever pressed submit, so a co-authored corpus",
                  "is mostly not yours as far as arXiv is concerned. Two consequences:",
                  "",
                  "1. **You cannot edit a paper you do not own**, so the journal-ref section",
                  "   below is blocked on this for those papers.",
                  f"2. <https://arxiv.org/a/{ident['orcid']}> — the public author page you get",
                  "   from linking ORCID, with an Atom feed and an embeddable widget — lists",
                  "   only the papers you own.",
                  "",
                  "Instant with the paper password (ask the submitting co-author; it is in",
                  "their acceptance email): <https://arxiv.org/auth/need-paper-password>.",
                  "Without it, <https://arxiv.org/auth/request-ownership> — staff verify in a",
                  "couple of days, no co-author needed, so batch the long tail there.",
                  "",
                  "Full list, citation-ordered: `tasks/arxiv_ownership.md`.",
                  ""]
    return L


def _needs_jr(p: dict) -> bool:
    """Is this paper published, on arXiv, and still declaring no venue there?

    A paper with no published venue has no journal-ref to declare, and listing it invited
    exactly the wrong edit: two entries read `-> ArXiv` and `-> CoRR`, which are the *absence*
    of a venue written out as if it were one.
    """
    return bool(p.get("arxiv") and not p.get("arxiv_journal_ref")
                and p.get("venue") and not is_preprint_venue(p["venue"]))


def _jref_submission_step(papers: list[dict]) -> list[str]:
    """The five-minute step that turns "find the row" into a link, or nothing.

    The submission id the journal-ref form is addressed by appears on exactly one page in the
    world, your own articles list, and `robots.txt` disallows it -- so the only route is a copy
    of the page saved by hand, and the only reason to save it is that it removes a search from
    every one of sixty rows. Stated as a step of its own, rather than as a closing sentence,
    which is where a prerequisite goes to be skipped.

    Empty once every listed paper has an id -- empty rather than "all done", which would be one
    more line asserting that something you cannot see is fine.
    """
    want = [str(p["arxiv"]) for p in papers if _needs_jr(p)]
    have = read_yaml(os.path.join(DATA, "arxiv_submissions.yaml")) or {}
    n = sum(1 for a in want if a in have)
    if not want or n >= len(want):
        return []
    # Agrees with itself at n == 1, which is the number this actually runs at: two
    # ids got cached while the ingester was being tested, so the first thing anyone
    # reads under this heading is the sentence about the other sixty.
    one = n == 1
    return [
        f"**Five minutes first, if you are doing more than a couple.** {n} of the",
        f"{len(want)} rows {'has' if one else 'have'} a direct link into "
        f"{'its' if one else 'their'} own form;",
        f"the other {len(want) - n} have to be found by eye on that list. The id the",
        "form is addressed by is only ever shown on your own articles page, and arXiv's",
        "`robots.txt` disallows fetching it — so the route is a copy you save:",
        "",
        "1. Sign in and open <https://arxiv.org/user>.",
        "2. Save the page — ⌘S, *Page Source* is enough.",
        "3. `python scripts/identity_tasks.py --user-page ~/Downloads/arxiv-user.html`",
        "",
        "Submission ids never change, so this is once and not per run, and nothing is",
        "requested on your behalf at any point — the code reads the file you saved.",
        "After it, every entry in [`tasks/arxiv_jref.md`](tasks/arxiv_jref.md) opens",
        "its own form.",
        "",
    ]


def _jref_intro(papers: list[dict], scholar: dict) -> list[str]:
    """The heading, what the edit costs, and the three things it buys, honestly ranked.

    The cost line comes first and is measured, because the earlier version of this section led
    with "Google Scholar keeps two records" and that turned out to be the weakest of the three
    reasons *for this corpus*: the profile has almost no split pairs. Selling the
    strongest-sounding argument rather than the true one is how a list of 64 items gets read
    once and never again.
    """
    n = sum(1 for p in papers if _needs_jr(p))
    dups = len(scholar.get("scholar_duplicates") or [])
    seen_n = scholar.get("corpus")
    split = ([f"   Measured on your own profile: **{dups} split pair"
              f"{'s' * (dups != 1)} out of {seen_n}**, so for this",
              "   corpus that is mostly already handled — do not do this for that reason."]
             if seen_n else
             ["   Scholar appears to have merged most of yours already, so this is not "
              "the reason to do it."])
    return [f"## arXiv journal-ref missing ({n} papers)",
            "",
            "**It is a metadata edit, not a new version.** No recompile, no file upload,",
            "no new version number, no re-announcement — v2 stays v2, per arXiv's own",
            "help page. That is the whole cost, about a minute each, and it is worth",
            "knowing because the size of this list is not the size of the job.",
            "",
            "The form is per-paper and lives behind your account: open",
            "<https://arxiv.org/user>, find the row, follow its *journal ref* link.",
            "There is no paste-an-identifier page — `/jref` on its own redirects to that",
            "list — which is also why no script can do this for you.",
            ""] + _jref_submission_step(papers) + [
            "**What it buys, honestly ranked.**",
            "",
            "1. *Weak here.* Scholar merges preprint and published versions largely on",
            "   venue agreement, and a venue-less arXiv record can stay a separate",
            "   cluster with the citations split across the two."] + split + [
            "2. **The arXiv DataCite record gains a `container-title`.** This is the real",
            "   one and it is not visible on Scholar at all: that field is what flows to",
            "   OpenAlex, to ORCID auto-update, and to every Crossref-derived tool, and",
            "   a venue-less record is filtered out by anything ranking on venue.",
            "3. **Answer engines cite venue as authority.** \"Published at ACL 2024\" in",
            "   the metadata is what makes a model's answer name the venue instead of",
            "   calling it a preprint.",
            "",
            "**Recommendation:** the top few, when you are already logged in, and stop.",
            "There is no write API, so the clicking is the one part of this list code",
            "cannot take off you — but the typing is not: both field values are below,",
            "per paper, built from the publisher's own bibtex. The same for all",
            f"{n} is in "
            "[`tasks/arxiv_jref.md`](tasks/arxiv_jref.md).",
            ""]


def _jref_blocked_note(blocked: int) -> list[str]:
    """The papers whose form will refuse, because arXiv does not list you as an author."""
    if not blocked:
        return []
    return [f"**{blocked} of these are marked (blocked)**: you are not a registered",
            "author on them, so the form will refuse. Claim ownership first (above).",
            ""]


def _jref_rows(missing_jr: list[dict], unowned: set) -> list[str]:
    """One paper per bullet, with the form link and both field values under it.

    The two field values inline rather than a pointer to `tasks/arxiv_jref.md`. A row saying
    only "-> ACL 2025" leaves the reader to work out what arXiv wants in a field it calls
    `Journal-ref:`, and the answer is a citation string this code already builds from the
    publisher's bibtex. The section they work from has to be the one that knows it.
    """
    from identity_tasks import journal_doi, journal_ref  # noqa: E402
    subs = read_yaml(os.path.join(DATA, "arxiv_submissions.yaml")) or {}
    L = []
    for p in missing_jr:
        flag = "  **(blocked)**" if p["arxiv"] in unowned else ""
        title = (title_of(p)).strip()
        L.append(f"- [ ] **{p.get('citations') or 0} cites** — {title}{flag}")
        sub = subs.get(p["arxiv"])
        # Nested bullets rather than indented prose: a continuation line at this
        # indent is a lazy paragraph continuation, so the form link rendered glued to
        # the end of the title.
        L.append(f"      - the form: <https://arxiv.org/submit/{sub}/jref>" if sub else
                 f"      - the form: find `{p['arxiv']}` on <https://arxiv.org/user> "
                 f"→ its *journal ref* link "
                 f"([abs](https://arxiv.org/abs/{p['arxiv']}))")
        if jr := journal_ref(p):
            L.append(f"      - `Journal-ref:` `{jr}`")
        else:
            # Said rather than omitted: an absent line reads as "nothing to paste",
            # and the reader types the venue name, which is not a journal-ref.
            venue = p.get("venue_display") or p.get("venue") or "?"
            L.append(f"      - `Journal-ref:` — not derivable from the bibliography "
                     f"(venue is *{venue}*); type the proceedings title yourself")
        doi = journal_doi(p)
        L.append(f"      - `Journal version DOI:` `{doi}`" if doi else
                 "      - `Journal version DOI:` — none minted, leave blank")
    return L


# `Report number:` means an *institutional* preprint number, a lab's own report series,
# and nothing in this corpus has one -- so it is answered once here rather than per row.
_JREF_FOOTER = ["", "`Report number:` stays blank on all of them: it means an "
                    "*institutional* preprint", "number (a lab's own report series) and none "
                    "of these has one.", ""]


def arxiv_journal_refs(papers: list[dict], scholar: dict, unowned: set) -> list[str]:
    """Published papers whose arXiv record still declares no venue, both field values inline.

    A metadata edit rather than a new version, about a minute each, and there is no write API
    -- so the clicking is the reader's and the typing is not.

    Four parts in the order they print: why the edit is cheap and what it buys, the papers
    whose form will refuse, a bullet per paper, and one line about the field nobody has to
    fill in.
    """
    missing_jr = by_citations(papers, _needs_jr, 12)
    if not missing_jr:
        return []
    blocked = sum(1 for p in papers if p.get("arxiv") in unowned and _needs_jr(p))
    return (_jref_intro(papers, scholar) + _jref_blocked_note(blocked)
            + _jref_rows(missing_jr, unowned) + _JREF_FOOTER)


def hf_pages(papers: list[dict], state: dict) -> list[str]:
    """The two Hugging Face buckets: no paper page at all, and a page nobody has claimed.

    Ten most-cited each, with the bucket's full size in the heading. `tasks/hf_worklist.md`
    carries the rest.
    """
    # Prefer the audit's live sets over the collector's cached flags where present:
    # this list is worked by hand over days, and a stale copy sends you back to
    # pages you already did -- which is what happened the first time round.
    live = state.get("hf_missing") is not None
    buckets = [
        (set(state.get("hf_missing") or []),
         lambda p: p.get("arxiv") and p.get("hf_indexed") is False,
         "Hugging Face paper page missing",
         ["Log in to Hugging Face first: an unauthenticated visit creates nothing",
          "(verified, 0 of 50). Visiting the URL while logged in *is* the action --",
          "there is no form.",
          "",
          "Full list, clickable: `tasks/hf_worklist.md`. Re-read the pages live",
          "after a session of clicking: `python scripts/audit_identity.py --no-names`."]),
        (set(state.get("hf_unclaimed") or []),
         lambda p: p.get("hf_indexed") and not p.get("hf_claimed_by_me"),
         "Hugging Face page indexed but not claimed by you",
         ["Claims go through moderation and Hugging Face only publishes the",
          "author→user link once it is granted, so a request already submitted is",
          "invisible from outside and would otherwise be listed here again. If you",
          "have already asked for one of these, add its arXiv id to",
          "`hf_claim_requested` in `data/overrides.yaml` and it moves to *pending*",
          "in `tasks/hf_worklist.md` instead of back onto this list.",
          "",
          "Full list and the other buckets: `tasks/hf_worklist.md`."]),
    ]
    L = []
    for ids, cached, head, why in buckets:
        shown = by_citations(papers, (lambda p, i=ids: p["arxiv"] in i) if live else cached, 10)
        if not shown:
            continue
        n = len(ids) if live else sum(1 for p in papers if cached(p))
        L += [f"## {head} ({n})", ""] + why + [""]
        L += [f"- [ ] <https://hf.co/papers/{p['arxiv']}>  ({p.get('citations') or 0} cites)"
              for p in shown] + [""]
    return L


def repo_gaps(repos: list[dict]) -> list[str]:
    """Repos with no citation route, and repos whose labels nobody has signed off.

    Last on the page: a Zenodo DOI is the cheapest item here and the least likely to
    change what an engine returns.
    """
    L = []
    zcand = [r for r in repos if not r.get("skip") and not r.get("paper_slug")
             and r.get("kind") in ZENODO_KINDS and not r.get("zenodo_doi")]
    if zcand:
        L += [f"## Artifacts with no citation route ({len(zcand)})", "",
              "Tools and guides with no linked paper. A Zenodo release DOI gives each a",
              "citable, archived identity and a DataCite record that reaches OpenAlex",
              "and your ORCID works list — so they stop being GitHub-only objects.",
              "Steps, and the honest case for skipping some: `tasks/zenodo.md`.", ""]

    pend = [r for r in repos if not r.get("reviewed") and not r.get("skip")]
    if pend:
        L += [f"## Repo labels awaiting your review ({len(pend)}/{len(repos)})", "",
              "Check `data/repos.yaml`, fix anything wrong, set `reviewed: true` to freeze "
              "it, then `python scripts/sweep_github.py diff`.", ""]
    return L


def same_or_different(papers: list[dict]) -> list[str]:
    """Title pairs close enough that one of them may be the other, for one decision each.

    Both titles whole rather than clipped to a row width: the decision is whether they name
    one paper, and a clip can fall exactly where they differ.
    """
    review = [p for p in papers if p.get("similar_but_distinct")]
    if not review:
        return []
    L = ["## Same paper or different? (decide once in data/overrides.yaml)", ""]
    for p in review:
        for o in p["similar_but_distinct"]:
            L.append(f"- [ ] `{title_of(p)}`  vs  `{o}`")
    return L + [""]
