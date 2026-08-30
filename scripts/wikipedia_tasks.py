#!/usr/bin/env python3
"""Where Wikipedia already talks about this work, and whether it gets it right.

Wikipedia carries roughly half the citations in ChatGPT answers, and is the one surface
where acting on that leverage directly is forbidden:

    WP:COI       you do not edit an article you have a stake in.
    WP:SELFCITE  you do not add citations to your own work. Excessive self-citation is
                 spam whether or not the work is good.

So the scope is corrections only. Everything asked for depends on someone else having
written about the work first:

    1. articles that mention the author        -- check the description is right
    2. articles that mention a coined term     -- same, per term
    3. field articles for the declared topics  -- the COI-free contribution, improved with
                                                  other people's sources
    4. coinages absent from Wikipedia          -- listed, explicitly nothing to do

An insertion is never asked for, and an article about your own coinage is the spam case.

Usage:
    python scripts/wikipedia_tasks.py
"""
from __future__ import annotations

import argparse
import glob
import html
import os
import re
import sys
import urllib.parse

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (DATA, ROOT, TASKS, load_config, read_papers, replied, write_json,  # noqa: E402
                    write_task)

API = "https://en.wikipedia.org/w/api.php"
OUT = os.path.join(TASKS, "wikipedia.md")
# The worklist section is emitted by update.py, which cannot re-run these ~100 API calls, so
# the few actionable items are handed over as data. `tasks/wikipedia.md` stays the full read.
STATE = os.path.join(ROOT, "build", "wikipedia_state.json")

# Names no search can use, which case-sensitive matching below cannot rescue. Two kinds:
# an ordinary word ("Genie", "Choice"), matching thousands of unrelated articles; and a
# coinage colliding with an established term from another field -- `E-values` is a
# reinforcement-learning quantity in DORA and the statistics notion on Wikipedia, so every
# match is a false positive and nothing downstream can tell them apart.
AMBIGUOUS = re.compile(r"^(genie|choice|version|fusing|cube|sloth|e-values|dora)$", re.I)


# Set to the first call Wikipedia did not answer. Every section of this page is built from
# the absence of a hit, so a run that could not read the API writes a page saying there is
# nothing to check -- indistinguishable from a clean run, and nothing on it is wrong enough
# to notice. `main` writes nothing while this is set, and later calls stop being sent.
_refused = ""


def api(**params) -> dict:
    """One `action=query` call, `{}` if it did not answer.

    `action=query` answers 200 for a title that does not exist, with `missing` on the page,
    so any other status is the API refusing rather than reporting.
    """
    global _refused
    if _refused:
        return {}
    q = urllib.parse.urlencode(dict(params, action="query", format="json", formatversion="2"))
    _st, d, why = replied(f"{API}?{q}")
    if why:
        _refused = f"{params} -> {why}"
    return d or {}


def exists(title: str) -> dict | None:
    """The article whose title is exactly this string, or None.

    Redirects are deliberately *not* followed and the title is compared with its case
    intact. Both matter: following redirects reported "DORA" as an existing article about
    the EU Digital Operational Resilience Act, and a case-insensitive compare reported
    "ColD Fusion" as covered by the article on cold fusion. A near-miss here is worse than
    a miss, because it silently drops the item.
    """
    d = api(prop="info|pageprops", inprop="url", titles=title)
    for p in (d.get("query") or {}).get("pages") or []:
        # A redirect page and a disambiguation page both "exist" while holding no content,
        # and reporting either as coverage drops the item for good.
        if p.get("missing") or "redirect" in p or "disambiguation" in (p.get("pageprops") or {}):
            continue
        if p.get("title") == title:
            return p
    return None


# `insource:` searches the wikitext, so a snippet is source and not rendered text. Left as
# it arrives, a quotable sentence reads as `[[IBM]]'s Grand Challenge, [[Project Debater]]`
# and an outline row as `*** [[Machine learning]] *`.
MARKUP = [(re.compile(r"<ref[^>]*>.*?</ref>|<[^>]*>", re.S), ""),
          (re.compile(r"\{\{[^{}]*(\}\})?"), " "),
          # A hit can land *inside* a citation or an infobox, where the snippet carries no
          # `{{` for the rule above to find -- `m|first4=Roy|last5=Bogin|first5=Ben`. Those
          # runs go, which leaves nothing the name or the term is in, and the row drops. A
          # name in a reference's author list is a citation of the work, not a claim about
          # it, so there is nothing there to check. `=` is required, so a table cell stays.
          (re.compile(r"\|\s*[A-Za-z][\w -]*\s*=\s*[^|]*"), " "),
          (re.compile(r"\[\[[^\]|]*\|([^\]|]*)\]\]"), r"\1"),
          (re.compile(r"\[\[([^\]|]*)\]\]"), r"\1"),
          (re.compile(r"'{2,}|\[\[|\]\]|\{\{|\}\}"), ""),
          (re.compile(r"(^|\s)[*#:;]+(\s|$)"), " ")]


def snippet(h: dict) -> str:
    """A search hit's matched text, unescaped and folded onto one line, still wikitext."""
    return " ".join(html.unescape(h.get("snippet") or "").split())


def plain(text: str) -> str:
    """Wikitext with its markup removed, so the line can be read as a sentence.

    Unescaped again at the end: an article source that writes `&ndash;` literally arrives
    from the API escaped twice.
    """
    for pat, rep in MARKUP:
        text = pat.sub(rep, text)
    return " ".join(html.unescape(text).split())


# A match that reaches an article's footer is in its see-also list or its categories, where
# the term is one bare link among others and nothing is stated about it to check. `==` and
# `Category:` occur nowhere else.
FOOTER = re.compile(r"==\s*(references|see also|external links|further reading|notes|"
                    r"bibliography)|\bCategor(y|ies):", re.I)


def saying(text: str, term: str) -> str:
    """The sentence of `text` that names `term`, else its first sentence, on one line."""
    flat = " ".join(html.unescape(text).split())
    return next((s for s in re.split(r"(?<=[.!?]) +", flat) if term in s),
                flat.split(". ")[0])


def mentions(term: str, limit: int = 5) -> list[dict]:
    """Articles whose text contains this term with its capitalisation intact.

    Each hit carries `says`, the text around the match, so the description can be judged
    without opening the article.

    Wikipedia's search is case-insensitive and has no case-sensitive operator, so the
    filter is applied to the returned snippet. `ColD Fusion` and `Q^2` only mean anything
    as written; matched loosely they resolve to cold fusion and to a mathematical symbol.
    """
    out = []
    for h in search(f'insource:"{term}"', limit=limit * 4):
        # Cleaned before the test, not after: the API wraps every matched word in a
        # `searchmatch` span, so a two-word term is not contiguous in the raw snippet.
        snip = plain(snippet(h))
        # In-domain as well as case-exact: `RLCR` matched five articles about sculpture and
        # a rotisserie oven, and an accuracy check aimed at "Brushstrokes in Flight" is not
        # a task, it is a reason to stop trusting the page.
        if term in snip and not FOOTER.search(snip) and in_domain(h["title"]):
            out.append(dict(h, says=snip))
    return out[:limit]


def search(expr: str, limit: int = 20) -> list[dict]:
    d = api(list="search", srsearch=expr, srlimit=limit, srnamespace=0)
    return ((d.get("query") or {}).get("search") or [])


DOMAIN = re.compile(r"artificial intelligence|machine learning|neural network|"
                    r"natural language processing|language model|deep learning", re.I)


def intro(title: str) -> str:
    """An article's lead section as plain text, `""` if the API does not answer."""
    d = api(prop="extracts", exintro=1, explaintext=1, titles=title)
    for p in (d.get("query") or {}).get("pages") or []:
        return p.get("extract") or ""
    return ""


def in_domain(title: str) -> bool:
    """Is this article actually about this field, or a same-words article from another one?

    Wikipedia's search for a keyword with no article of its own returns the closest title,
    and "closest" is lexical: *model merging* resolved to Newell-Daganzo merge model (traffic
    flow) and *efficient evaluation* to Lazy evaluation (programming languages). Both would
    then have been offered as places to propose a benchmark. The intro paragraph is checked
    for a field term instead, which is cheap and rejects exactly those two.
    """
    return bool(DOMAIN.search(intro(title)))


def sidecar_terms() -> dict[str, list[str]]:
    """`coined` name -> every paper slug that coins it.

    Every slug, not the first one found: one term is coined by a paper and then carried by
    its follow-ups, and picking the alphabetically-first sidecar silently attached "BabyLM
    Challenge" to the 2nd-edition call for papers, whose citation count is a fraction of
    the original's. The caller picks the most-cited, which is the one a weight judgement
    would be made on.
    """
    out: dict[str, list[str]] = {}
    for path in sorted(glob.glob(os.path.join(DATA, "sidecars", "*.md"))):
        m = re.match(r"^---\n(.*?)\n---", open(path).read(), re.S)
        fm = yaml.safe_load(m.group(1)) if m else None
        if not fm or not fm.get("coined"):
            continue
        # "DCT (Deductive Closure Training)" is two searchable names and the expansion is
        # the one an encyclopaedia would use; splitting on the bracket alone left the
        # bracket attached ("PkE (peakiness effect").
        for name in re.split(r"\s*/\s*|\s*[(),]\s*", fm["coined"]):
            name = name.strip()
            # A bracket also holds qualifiers that are not names of anything.
            if len(name) > 2 and not re.match(r"^\d|edition$|^v\d", name):
                out.setdefault(name, []).append(os.path.basename(path)[:-3])
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-citations", type=int, default=20,
                    help="ignore coinages below this, to keep the absent-from-Wikipedia "
                         "list to the terms anyone might plausibly have written about")
    args = ap.parse_args()
    cfg = load_config()
    ident = cfg["identity"]
    papers = {p["slug"]: p for p in read_papers()}
    surname = ident["name"].split()[-1]

    L = ["# Wikipedia", "",
         "Generated by `python scripts/wikipedia_tasks.py`. Every item here is a check on",
         "something *someone else* wrote. Nothing on this page edits an article, adds a",
         "citation to your own work, or asks for a mention that nobody independent thought",
         "was due -- WP:COI and WP:SELFCITE, and see the module docstring for why the",
         "insert-a-mention version of this page was dropped.", ""]

    # 1. Where the author is named. Being an author makes you the best-placed person to
    #    notice a misstatement and the worst-placed one to fix it, so it is a talk-page item
    #    -- but a correction of fact is the proposal editors accept most readily.
    mine = []
    for h in search(f'insource:"{surname}" insource:"arxiv"', limit=30):
        snip = plain(snippet(h))
        # The same two rejections `mentions` applies: the name has to survive the markup
        # strip, and a footer match is a category line rather than a description.
        if surname.lower() in snip.lower() and not FOOTER.search(snip):
            mine.append(dict(h, says=snip))
    L += [f"## Articles that mention {surname} ({len(mine)})", ""]
    if mine:
        L += ["Read each one and check it describes the work correctly. If it does, there is",
              "nothing to do. If it does not, the talk page gets the correction and the page",
              "or table it comes from -- never the article itself. The quoted line is the",
              "text that names you, excerpted by the search, so it may start mid-sentence.",
              ""]
        for h in mine:
            q = urllib.parse.quote(h["title"].replace(" ", "_"))
            L.append(f"- [ ] [{h['title']}](https://en.wikipedia.org/wiki/{q}) — "
                     f"[talk](https://en.wikipedia.org/wiki/Talk:{q})")
            if h["says"]:
                L.append(f"  > {h['says']}")
        L.append("")
    else:
        L += ["None found. That is the expected state and not a gap to close.", ""]

    # 2. Coined terms someone else has written up. Independent uptake is the whole
    #    qualification: it is what makes the check a check rather than a plug.
    terms = sidecar_terms()
    checks, absent = [], []
    for term, slugs in sorted(terms.items()):
        cands = [papers[sl] for sl in slugs if sl in papers]
        p = max(cands, key=lambda x: x.get("citations") or 0) if cands else None
        if not p or AMBIGUOUS.match(term) or (p.get("citations") or 0) < args.min_citations:
            continue
        # An exact-title article still has to be about this field: `Sloth` is the animal and
        # `E-values` is a statistics article, and neither is a description of this work to
        # check. Same guard as `mentions` applies to the same failure.
        art = exists(term)
        lead = intro(art["title"]) if art else ""
        art = dict(art, says=saying(lead, term)) if DOMAIN.search(lead) else None
        found = ([art] if art else []) + [h for h in mentions(term)
                                          if not art or h["title"] != art["title"]]
        (checks.append((term, p, found)) if found else absent.append((term, p)))

    L += [f"## Coined here and written up by someone else ({len(checks)})", ""]
    if checks:
        L += ["The article exists or the term appears in one, so the description is not",
              "yours and may be wrong. Same rule: read it, and only raise a talk-page item",
              "if it misstates the work. The quoted line is what that article says about the",
              "term — enough to tick most rows without opening anything.", ""]
        for term, p, found in sorted(checks, key=lambda t: -(t[1].get("citations") or 0)):
            L.append(f"- **{term}** ({p.get('citations') or 0} citations)")
            for h in found:
                q = urllib.parse.quote(h["title"].replace(" ", "_"))
                L.append(f"  - [ ] [{h['title']}](https://en.wikipedia.org/wiki/{q}) — "
                         f"[talk](https://en.wikipedia.org/wiki/Talk:{q})")
                if h.get("says"):
                    L.append(f"    > {h['says']}")
        L.append("")
    else:
        L += ["None.", ""]

    # 3. The COI-free contribution, and the only item on this page that helps the topic
    #    questions a paper page cannot answer.
    L += ["## Topic articles in your fields", "",
          "Improve these with *other people's* sources. Nothing about your own work, no",
          "citation of it. Unlike everything above, this needs no permission and no",
          "disclosure -- it is ordinary editing in an area you know.", ""]
    for kw in ident.get("keywords") or []:
        art = exists(kw) or exists(kw[0].upper() + kw[1:])
        if art:
            L.append(f"- [{art['title']}]({art['fullurl']}) — {art.get('length', 0):,} bytes")
            continue
        near = search(kw, limit=1)
        if near and in_domain(near[0]["title"]):
            t = near[0]["title"]
            L.append(f"- *{kw}* — no article under that title; the nearest field article is "
                     f"[{t}](https://en.wikipedia.org/wiki/"
                     f"{urllib.parse.quote(t.replace(' ', '_'))})")
        else:
            L.append(f"- *{kw}* — no article, and nothing in this field close to it")

    L += ["", f"## Absent from Wikipedia ({len(absent)}) — nothing to do", "",
          "Coined here, above the citation floor, and nobody independent has written them",
          "up. Deliberately not actionable: proposing the mention yourself is the request",
          "that gets declined, and writing the article yourself is the spam case. They",
          "become checks in section 2 if someone else ever writes about them.", ""]
    for term, p in sorted(absent, key=lambda t: -(t[1].get("citations") or 0)):
        L.append(f"- {term} — {p.get('citations') or 0} citations")

    if _refused:
        # Every list above is empty because the API did not answer, not because there is
        # nothing to check, and the worklist section is built from the state file.
        print(f"wikipedia did not answer ({_refused}), so "
              f"{os.path.relpath(OUT, ROOT)} and {os.path.relpath(STATE, ROOT)} are left "
              f"as the last run read them", file=sys.stderr)
        raise SystemExit(1)

    write_json(
        STATE,
        {"checks": [{"term": t, "citations": p.get("citations") or 0,
                     "articles": [{"title": h["title"], "says": h.get("says") or ""}
                                  for h in f_]}
                    for t, p, f_ in checks],
         "already_mentions": [{"title": h["title"], "says": h["says"]} for h in mine],
         "absent": len(absent)}, indent=1)
    os.makedirs(TASKS, exist_ok=True)
    write_task(OUT, L)
    print(f"wrote {os.path.relpath(OUT, ROOT)}: {len(mine)} article(s) naming you, "
          f"{len(checks)} term(s) to check, {len(absent)} left alone")


if __name__ == "__main__":
    main()
