#!/usr/bin/env python3
"""What can honestly be done on Wikipedia, and the exact text to paste where.

Wikipedia is the single most-cited domain in AI answers -- about 48% of top citations in
ChatGPT -- so it is the highest-leverage surface in this project and the one where acting
on that leverage directly is forbidden. Two rules decide everything here:

    WP:COI       you do not edit an article you have a stake in; you propose on its talk
                 page and let an uninvolved editor decide.
    WP:SELFCITE  you do not add citations to your own work. Excessive self-citation is
                 spam whether or not the work is good.

So this script never writes anything, and it never asks for an article edit. It produces
three things, in `tasks/wikipedia.md`:

    1. articles that already cite you    -- a factual-accuracy check, which is the one
                                            place your involvement is an asset
    2. proposals worth making            -- a paste-ready talk-page section per coined
                                            term, with {{edit COI}} and the disclosure
                                            already written
    3. what is deliberately not asked    -- topics with no article, where "write it
                                            yourself" is exactly the spam case

Nothing here is a decision the author is obliged to make. A proposal an uninvolved editor
declines is the system working; that is the price of the surface being trustworthy enough
to be worth 48% of citations in the first place.

Usage:
    python scripts/wikipedia_tasks.py
    python scripts/wikipedia_tasks.py --min-citations 100
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import urllib.parse

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import BUILD, DATA, ROOT, TASKS, get_json, load_config, read_yaml  # noqa: E402

API = "https://en.wikipedia.org/w/api.php"
OUT = os.path.join(TASKS, "wikipedia.md")
# The worklist section is emitted by update.py, which cannot re-run these ~100 API calls, so
# the few actionable items are handed over as data. `tasks/wikipedia.md` stays the full read.
STATE = os.path.join(ROOT, "build", "wikipedia_state.json")

# A coined name that is also an ordinary word makes any search meaningless -- "Genie" and
# "Choice" match thousands of articles about nothing to do with this corpus. Case-sensitive
# matching (below) catches most of these; these are the ones it cannot.
AMBIGUOUS = re.compile(r"^(genie|choice|version|fusing|cube)$", re.I)


def api(**params) -> dict:
    params.update(action="query", format="json", formatversion="2")
    q = urllib.parse.urlencode(params)
    return get_json(f"{API}?{q}") or {}


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


def mentions(term: str, limit: int = 5) -> list[dict]:
    """Articles whose text contains this term with its capitalisation intact.

    Wikipedia's search is case-insensitive and has no case-sensitive operator, so the
    filter is applied to the returned snippet. `ColD Fusion` and `Q^2` only mean anything
    as written; matched loosely they resolve to cold fusion and to a mathematical symbol.
    """
    out = []
    for h in search(f'insource:"{term}"', limit=limit * 4):
        snip = re.sub(r"<[^>]+>", "", h.get("snippet") or "")
        if term in snip:
            out.append(h)
    return out[:limit]


def search(expr: str, limit: int = 20) -> list[dict]:
    d = api(list="search", srsearch=expr, srlimit=limit, srnamespace=0)
    return ((d.get("query") or {}).get("search") or [])


DOMAIN = re.compile(r"artificial intelligence|machine learning|neural network|"
                    r"natural language processing|language model|deep learning", re.I)


def in_domain(title: str) -> bool:
    """Is this article actually about this field, or a same-words article from another one?

    Wikipedia's search for a keyword with no article of its own returns the closest title,
    and "closest" is lexical: *model merging* resolved to Newell-Daganzo merge model (traffic
    flow) and *efficient evaluation* to Lazy evaluation (programming languages). Both would
    then have been offered as places to propose a benchmark. The intro paragraph is checked
    for a field term instead, which is cheap and rejects exactly those two.
    """
    d = api(prop="extracts", exintro=1, explaintext=1, titles=title)
    for p in (d.get("query") or {}).get("pages") or []:
        return bool(DOMAIN.search(p.get("extract") or ""))
    return False


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


def one_liner(slug: str) -> str | None:
    path = os.path.join(DATA, "sidecars", f"{slug}.md")
    m = re.match(r"^---\n(.*?)\n---", open(path).read(), re.S) if os.path.exists(path) else None
    return ((yaml.safe_load(m.group(1)) or {}).get("one_liner") if m else None)


STOP = set("of and the for in a to on with is are that this we our its from as by at be "
           "can not but their which what when than then does do".split())


def queries(text: str) -> list[str]:
    """Two search strings for one paper, because Wikipedia's search ANDs every word.

    A paper title pasted whole matches nothing at all -- "Findings of the BabyLM Challenge:
    Sample-efficient pretraining on a developmentally plausible corpus" returns zero
    articles, which is why an earlier version reported no host for the corpus's three
    most-cited coinages. The `OR` form is noisy on its own and is filtered by the candidate
    set and `in_domain` downstream.
    """
    words: list[str] = []
    for word in re.findall(r"[A-Za-z][A-Za-z-]{3,}", (text or "").lower()):
        if word not in STOP and word not in words:
            words.append(word)
    return [" ".join((text or "").split()[:12]), " OR ".join(words[:6])]


def host_for(texts: list[str], hosts: dict[str, str]) -> str | None:
    """An article that could host a mention, or None. Candidates are ranked, not invented.

    Preference order, and each step exists because the one before it was not enough:

      1. an article for one of this author's own `identity.keywords` -- the safest host,
         since it is a topic they demonstrably work in
      2. any article the paper retrieves that is itself about this field, checked with
         `in_domain`. Needed because the keyword list covers only part of the corpus, and
         because it finds the *specific* host when one exists -- Global-MMLU's is the
         article on MMLU, which no keyword would ever have named.

    Everything else is None, and None means "nothing to do" rather than "least-bad guess".
    An unrestricted top-search-result version of this proposed adding BlendNet to the
    article on Syrah, the grape; `in_domain` is what makes step 2 safe from that.
    """
    titles, fallback = set(hosts.values()), None
    for text in texts:
        for q in queries(text):
            for h in search(q, limit=6):
                if h["title"] in titles:
                    return h["title"]
                if fallback is None and in_domain(h["title"]):
                    fallback = h["title"]
    return fallback


def cite(p: dict) -> str:
    bits = [", ".join((p.get("authors") or [])[:4]) + (" et al." if len(p.get("authors") or []) > 4 else "")]
    bits.append(f'"{p.get("title_display") or p.get("title")}"')
    if p.get("venue"):
        bits.append(str(p["venue"]))
    if p.get("year"):
        bits.append(str(p["year"]))
    url = (f"https://doi.org/{p['doi']}" if p.get("doi") else
           f"https://arxiv.org/abs/{p['arxiv']}" if p.get("arxiv") else None)
    return ". ".join(b for b in bits if b) + (f". {url}" if url else "")


def proposal_body(term: str, p: dict, gloss: str | None) -> list[str]:
    """The talk-page section itself, ready to paste, disclosure and all.

    Written in the third person and without an opinion on whether it belongs: the whole
    point of proposing rather than editing is that the weight judgement is not the author's
    to make, and a proposal that argues its own DUE case reads as advocacy -- which is how a
    COI request gets declined on sight regardless of the work behind it.
    """
    sentence = (gloss or "").strip().rstrip(".")
    return [
        f"== {term} ==", "{{edit COI|answered=no}}",
        "I have a conflict of interest: I am an author of the paper below, so I am",
        "proposing this here rather than editing the article, per WP:COI and WP:SELFCITE.",
        "",
        "Suggested addition, wherever editors judge it fits:",
        f": {sentence}." if sentence else ": (one sentence, third person, no adjectives)",
        "",
        f"Source: {cite(p)}",
        f"Cited {p.get('citations') or 0} times per Semantic Scholar as of this posting,",
        "offered only as context for a weight judgement I should not be making myself.",
        "I have no view on whether this meets WP:DUE and will not edit the article.",
        "~~~~"]


def proposal(term: str, p: dict, host: str, gloss: str | None) -> list[str]:
    """The same text, folded into the task file behind a summary."""
    return [f"<details><summary>talk-page text for <b>{host}</b></summary>", "", "```wikitext",
            *proposal_body(term, p, gloss), "```", "</details>", ""]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--propose-above", type=int, default=150,
                    help="only terms above this many citations get a paste-ready talk-page "
                         "payload; the rest are listed and left alone")
    ap.add_argument("--min-citations", type=int, default=50,
                    help="a coined name is only proposed above this many citations -- not "
                         "a quality bar, a WP:DUE proxy an uninvolved editor can check")
    args = ap.parse_args()
    cfg = load_config()
    ident = cfg["identity"]
    papers = {p["slug"]: p for p in
              (read_yaml(os.path.join(DATA, "papers.yaml")) or {})["papers"]}
    surname = ident["name"].split()[-1]

    L = ["# Wikipedia", "",
         "Generated by `python scripts/wikipedia_tasks.py`. Nothing here edits an article,",
         "and nothing here adds a citation to your own work -- see WP:COI and WP:SELFCITE.",
         "Every item is either a factual check or a talk-page proposal an uninvolved editor",
         "is free to decline.", ""]

    # 1. Where you are already cited. Your involvement makes you the best-placed person to
    #    notice a misstatement and the worst-placed one to fix it, so this is a talk-page
    #    item too -- but a correction of fact is the proposal editors accept most readily.
    hits = search(f'insource:"{surname}" insource:"arxiv"', limit=30)
    mine = [h for h in hits if surname.lower() in (h.get("snippet") or "").lower()]
    L += [f"## Articles that already mention {surname} ({len(mine)})", ""]
    if mine:
        L += ["Check each one describes the work correctly. A wrong summary of your own "
              "paper is the",
              "one COI case where speaking up is unambiguously helpful -- on the talk page, "
              "with the",
              "correction and the page or table it comes from.", ""]
        for h in mine:
            t = h["title"]
            L.append(f"- [{t}](https://en.wikipedia.org/wiki/{urllib.parse.quote(t.replace(' ', '_'))}) "
                     f"— [talk](https://en.wikipedia.org/wiki/Talk:{urllib.parse.quote(t.replace(' ', '_'))})")
        L.append("")
    else:
        L += ["None found by full-text search. That is the expected state and not a gap to "
              "close: a", "citation added by you would be the thing the rules forbid.", ""]

    # The candidate hosts, resolved once: the articles for the fields this author actually
    # works in. A proposal is only ever aimed at one of these.
    kw_articles, kw_near, kw_missing = {}, {}, []
    for kw in ident.get("keywords") or []:
        art = exists(kw) or exists(kw[0].upper() + kw[1:])
        if art:
            kw_articles[kw] = art
            continue
        found = search(kw, limit=1)
        # No article under the keyword itself is the common case ("efficient evaluation" is
        # a phrase, not a topic). The nearest article is still a real host candidate, but
        # only once it has been checked to be about this field at all.
        if found and in_domain(found[0]["title"]):
            kw_near[kw] = found[0]["title"]
        else:
            kw_missing.append(kw)
    hosts = {kw: a["title"] for kw, a in kw_articles.items()} | dict(kw_near)

    # 2. Coined names above the citation floor, with no mention anywhere on Wikipedia.
    terms = sidecar_terms()
    L += ["## Talk-page proposals", ""]
    proposed = 0
    thin, actionable = [], []
    for term, slugs in sorted(terms.items()):
        cands = [papers[s] for s in slugs if s in papers]
        p = max(cands, key=lambda x: x.get("citations") or 0) if cands else None
        if not p or AMBIGUOUS.match(term):
            continue
        slug = p["slug"]
        if (p.get("citations") or 0) < args.min_citations:
            continue
        art = exists(term)
        if art:
            L += [f"### {term} — an article holds this exact title", "",
                  f"[{art['title']}]({art['fullurl']}) — {art.get('length', 0):,} bytes. It "
                  f"may be about this work or about an", "unrelated subject of the same name "
                  "(`E-values` is a statistics article, not the paper's",
                  "sense). Read it; the only item here is a talk-page correction if it "
                  "describes", "the work and gets it wrong.", ""]
            continue
        found = mentions(term)
        if found:
            L += [f"### {term} — already mentioned", "",
                  *(f"- [{h['title']}](https://en.wikipedia.org/wiki/"
                    f"{urllib.parse.quote(h['title'].replace(' ', '_'))})" for h in found),
                  "", "Check each mention is accurate rather than adding another.", ""]
            continue
        gloss = one_liner(slug)
        # Every paper that coins the term, most-cited first: a follow-up paper's title can
        # retrieve nothing while the original's retrieves the right article.
        host_title = host_for([f"{c.get('title') or ''} {one_liner(c['slug']) or ''}"
                               for c in sorted(cands, key=lambda x: -(x.get('citations') or 0))],
                              hosts)
        if not host_title or (p.get("citations") or 0) < args.propose_above:
            # Listed, not proposed. A payload aimed at a weak host, or at a term with little
            # outside uptake, is a proposal that gets declined -- and a run of declined COI
            # requests is how an editor learns to stop reading yours. The bar is deliberately
            # a citation count and not a judgement of the work.
            thin.append((term, p, host_title))
            continue
        L += [f"### {term} — not on Wikipedia", ""]
        actionable.append({"term": term, "host": host_title, "slug": slug,
                           "citations": p.get("citations") or 0,
                           "payload": "\n".join(proposal_body(term, p, gloss)),
                           "talk": f"https://en.wikipedia.org/wiki/Talk:"
                                   f"{urllib.parse.quote(host_title.replace(' ', '_'))}"
                                   f"?action=edit&section=new"})
        if True:
            q = urllib.parse.quote(host_title.replace(" ", "_"))
            L += [f"Best-matching article in this field: "
                  f"[{host_title}](https://en.wikipedia.org/wiki/{q}) — "
                  f"[open a new talk-page section](https://en.wikipedia.org/wiki/Talk:{q}"
                  f"?action=edit&section=new)", "",
                  "That is a word-overlap match, not an argument that it belongs there. Read "
                  "the article", "first; if the term has no natural home in it, the right "
                  "action is none.", ""]
            L += proposal(term, p, host_title, gloss)
        proposed += 1

    if thin:
        L += ["### Below the bar, listed only", "",
              f"Coined here, absent from Wikipedia, and not worth a COI request: either "
              f"under {args.propose_above} citations,",
              "or with no article in this field that could host a mention. Nothing to do "
              "unless someone", "else writes about them first.", ""]
        for term, p, host in sorted(thin, key=lambda t: -(t[1].get("citations") or 0)):
            # No host title printed even when one was found: below the bar the item is not
            # actionable, and a wrong-looking suggestion next to it ("MoErging -> Forest
            # informatics") only invites someone to act on it.
            L.append(f"- **{term}** — {p.get('citations') or 0} citations")
        L.append("")

    # 3. Topic articles for the fields he works in -- the honest, non-COI contribution, and
    #    the reason it stays a human item.
    L += ["## Topic articles in your fields", "",
          "The COI-free contribution: improve these with *other people's* sources. Nothing",
          "about your own work, no citation of it. This is also the only item on this page",
          "that helps the topic queries a paper page cannot answer.", ""]
    for kw, art in kw_articles.items():
        L.append(f"- [{art['title']}]({art['fullurl']}) — {art.get('length', 0):,} bytes")
    for kw, t in kw_near.items():
        L.append(f"- *{kw}* — no article under that title; the field article nearest it is "
                 f"[{t}](https://en.wikipedia.org/wiki/"
                 f"{urllib.parse.quote(t.replace(' ', '_'))})")
    for kw in kw_missing:
        L.append(f"- *{kw}* — no article, and nothing in this field close to it")
    L += ["", "## What this page will never ask for", "",
          "- **Creating an article about your own method or benchmark.** That is the spam",
          "  case, whatever the citation count says.",
          "- **Adding a citation to your own paper.** WP:SELFCITE, and it is the single",
          "  most-reverted kind of edit an academic makes.",
          "- **Editing an article that discusses your work.** Propose on the talk page and",
          "  let someone uninvolved decide, including deciding against you.", ""]

    os.makedirs(BUILD, exist_ok=True)
    with open(STATE, "w") as f:
        json.dump({"proposals": actionable,
                   "already_mentions": [h["title"] for h in mine],
                   "below_bar": len(thin)}, f, indent=1)
    os.makedirs(TASKS, exist_ok=True)
    open(OUT, "w").write("\n".join(L) + "\n")
    print(f"wrote {os.path.relpath(OUT, ROOT)}: {len(mine)} existing mention(s), "
          f"{proposed} proposal(s) drafted, {len(thin)} left alone")


if __name__ == "__main__":
    main()
