#!/usr/bin/env python3
"""Resolve the author name strings on our Wikidata paper items into author items.

Every paper item this project created states you as `author` (P50) and every co-author as
`author name string` (P2093). Depositing a string is correct -- pointing P50 at a guessed
person welds someone else's item to your paper -- but leaving it there costs the thing the
items were created for. A string is a literal nothing can join on, so each of the 108 items
hangs off your item alone. Upgrading a string to P50 is routine Wikidata maintenance, it
asserts nothing that is not already printed on the paper, and it turns one-spoke items into
a neighbourhood with many independent paths back to you.

Two passes, and the difference between them is the whole design.

  by ORCID   the paper's OpenAlex record carries the co-author's ORCID, and exactly one
             Wikidata item states that ORCID (P496). Identifier to identifier with no name
             in the middle, so it is emitted as a batch to paste.
  by name    the string matches the label or an alias of a human item. A namesake matches
             exactly as well, so these are listed one at a time for you to confirm and are
             never batched.

A second, unrelated gap rides along because it is the same batch and the same items. None of
the 108 states `published in` (P1433), so nothing joins a paper to the venue that published
it. The venue name is in the corpus already, so this needs no guessing beyond one rule --
P1433 takes a publication, and a conference name matches the conference event as readily as
the proceedings volume, so only a proceedings or a journal is ever a target.

Creates no item about anybody and writes nothing to Wikidata. Items for people who have
none are out of scope by policy, not by omission -- Wikidata notability wants "serious and
publicly available references", and a co-author with no record of their own has none that
does not originate with us.
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
from common import (BUILD, DATA, TASKS, get, get_json, norm_name,  # noqa: E402
                    read_yaml)

WDQS = "https://query.wikidata.org/sparql"
API = "https://www.wikidata.org/w/api.php"
DISAMBIG = "https://author-disambiguator.toolforge.org"
# A resolved string does not come back and an item's own statements change slowly, so the
# cost of a stale answer is one wasted row rather than a wrong edit. Long enough that the
# pass is free on a normal run, short enough that a name resolved elsewhere drops out.
CACHE_DAYS = 30
CACHE = "wikidata_coauthors_cache.json"
# Bumped when the cache layout changes, so an old file is re-asked rather than misread.
SHAPE = 4


def sparql(query: str) -> list[dict]:
    """Rows of a SPARQL query against WDQS, or `[]` if it did not answer."""
    raw = get(f"{WDQS}?" + urllib.parse.urlencode({"query": query}),
              accept="application/sparql-results+json")
    try:
        return json.loads(raw)["results"]["bindings"]
    except (ValueError, KeyError, TypeError):
        return []


def qid_of(uri: str) -> str:
    return uri.rsplit("/", 1)[1]


def item_state(qids: list[str]) -> dict[str, dict]:
    """Per paper item, the P2093 strings left, the P50 items present, and whether P1433 is.

    Read live rather than from `paper_item`, because the question is what the item says
    now. A string somebody else resolved last week is not work.
    """
    out: dict[str, dict] = {}
    for i in range(0, len(qids), 40):
        d = get_json(f"{API}?action=wbgetentities&format=json&props=claims&ids="
                     + "|".join(qids[i:i + 40]))
        for qid, it in ((d or {}).get("entities") or {}).items():
            c = it.get("claims") or {}
            strings = []
            for s in c.get("P2093") or []:
                name = (s["mainsnak"].get("datavalue") or {}).get("value")
                ordinal = next((q["datavalue"]["value"] for q in
                                (s.get("qualifiers") or {}).get("P1545") or []), "")
                if name:
                    strings.append({"name": name, "ordinal": ordinal})
            out[qid] = {"strings": strings, "venue": bool(c.get("P1433")), "p50": {
                (s["mainsnak"].get("datavalue") or {}).get("value", {}).get("id")
                for s in c.get("P50") or []}}
    return out


def keys_for(name: str) -> list[str]:
    """The forms one printed name is matched under, most specific first.

    Two: the whole name folded, and first initial plus surname. The second is what lets the
    `Colin A. Raffel` on a paper meet the `Colin Raffel` in an index, and it is only safe
    because these keys are compared inside one paper's author list, where two people
    sharing an initial and a surname does not happen.
    """
    parts = norm_name(name).split()
    out = [" ".join(parts)]
    if len(parts) > 1:
        out.append(f"{parts[0][0]} {parts[-1]}")
    return out


def openalex_orcids(papers: list[dict]) -> dict[str, dict[str, str]]:
    """Per paper slug, the ORCIDs its OpenAlex record carries, keyed by `keys_for`.

    By-id lookups only, which are free where OpenAlex meters its search endpoints. A key
    that two ORCIDs in the same paper answer to is dropped rather than guessed at.
    """
    out: dict[str, dict[str, str]] = {}
    for p in papers:
        doi = p.get("doi") or (f"10.48550/arXiv.{p['arxiv']}" if p.get("arxiv") else None)
        if not doi:
            continue
        d = get_json("https://api.openalex.org/works/doi:"
                     + urllib.parse.quote(str(doi)) + "?select=authorships")
        seen: dict[str, set[str]] = {}
        for a in (d or {}).get("authorships") or []:
            au = a.get("author") or {}
            orcid, name = au.get("orcid"), au.get("display_name")
            if orcid and name:
                for k in keys_for(name):
                    seen.setdefault(k, set()).add(orcid.rsplit("/", 1)[1])
        got = {k: next(iter(v)) for k, v in seen.items() if len(v) == 1}
        if got:
            out[p["slug"]] = got
    return out


def items_by_orcid(orcids: list[str]) -> dict[str, dict]:
    """ORCID to the single Wikidata item stating it. An ORCID two items claim is dropped."""
    found: dict[str, set] = {}
    labels: dict[str, str] = {}
    for i in range(0, len(orcids), 150):
        vals = " ".join('"%s"' % o for o in orcids[i:i + 150])
        for r in sparql("SELECT ?o ?p ?pLabel WHERE { VALUES ?o { %s } ?p wdt:P496 ?o . "
                        'SERVICE wikibase:label { bd:serviceParam wikibase:language "en". '
                        "} }" % vals):
            q = qid_of(r["p"]["value"])
            found.setdefault(r["o"]["value"], set()).add(q)
            labels[q] = r.get("pLabel", {}).get("value", q)
    return {o: {"qid": next(iter(qs)), "label": labels.get(next(iter(qs)), "")}
            for o, qs in found.items() if len(qs) == 1}


def items_by_name(names: list[str]) -> dict[str, list[dict]]:
    """Name string to every human item whose label or alias is exactly that string."""
    out: dict[str, list[dict]] = {}
    for i in range(0, len(names), 120):
        vals = " ".join('"%s"@en' % n.replace('"', "") for n in names[i:i + 120])
        rows = sparql(
            "SELECT ?name ?p ?d ?orcid WHERE { VALUES ?name { %s } "
            "{ ?p rdfs:label ?name } UNION { ?p skos:altLabel ?name } ?p wdt:P31 wd:Q5 . "
            'OPTIONAL { ?p schema:description ?d FILTER(lang(?d) = "en") } '
            "OPTIONAL { ?p wdt:P496 ?orcid } }" % vals)
        for r in rows:
            cand = {"qid": qid_of(r["p"]["value"]),
                    "description": r.get("d", {}).get("value", ""),
                    "orcid": r.get("orcid", {}).get("value", "")}
            got = out.setdefault(r["name"]["value"], [])
            if cand["qid"] not in {c["qid"] for c in got}:
                got.append(cand)
    return out


# P1433 wants the publication, and a conference name matches the event as well as its
# proceedings. Ordered by preference, so the first type a candidate has decides it.
# What P1433 accepts, in the order a tie is broken. Its value-type constraint wants a
# publication, so a conference item is never a valid target however well its name matches.
PUBLICATION_TYPES = ("Q1143604", "Q5633421")
# Searched anyway, so a name that only matches the event can say so instead of vanishing.
EVENT_TYPES = ("Q2020153", "Q47258130")


def venue_items(names: list[str]) -> dict[str, list[dict]]:
    """Venue name to every journal, proceedings or conference item labelled with it.

    Each candidate carries every one of these types it has, since a volume is often also a
    `version, edition or translation` and a journal often also `open-access journal`.
    """
    out: dict[str, list[dict]] = {}
    for i in range(0, len(names), 60):
        vals = " ".join('"%s"@en' % n.replace('"', "") for n in names[i:i + 60])
        types = " ".join("wd:" + t for t in PUBLICATION_TYPES + EVENT_TYPES)
        rows_ = sparql(
            "SELECT ?name ?p ?pLabel ?t WHERE { VALUES ?name { %s } "
            "{ ?p rdfs:label ?name } UNION { ?p skos:altLabel ?name } "
            "?p wdt:P31/wdt:P279* ?t . VALUES ?t { %s } "
            'SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }'
            % (vals, types))
        for r in rows_:
            qid, t = qid_of(r["p"]["value"]), qid_of(r["t"]["value"])
            got = out.setdefault(r["name"]["value"], [])
            cand = next((c for c in got if c["qid"] == qid), None)
            if cand is None:
                cand = {"qid": qid, "label": r.get("pLabel", {}).get("value", ""),
                        "types": []}
                got.append(cand)
            if t not in cand["types"]:
                cand["types"].append(t)
    return out


def publications(cands: list[dict]) -> list[dict]:
    """The candidates that are publications rather than conference events."""
    return [c for c in cands if set(c["types"]) & set(PUBLICATION_TYPES)]


def pick_venue(cands: list[dict]) -> dict | None:
    """The one candidate P1433 should point at, or None if the name does not settle.

    A proceedings volume outranks a journal, which is how a proceedings sitting beside its
    own conference item resolves. Two candidates of the same rank stay a question, and a
    name that matched only the conference event has no answer here at all.
    """
    for t in PUBLICATION_TYPES:
        same = [c for c in cands if t in c["types"]]
        if len(same) == 1:
            return same[0]
        if same:
            return None
    return None


def lookups(names: list[str], papers: list[dict], refresh: bool) -> dict:
    """The network answers this pass needs, cached in `build/` for CACHE_DAYS.

    Returns `orcids` (name to ORCID), `by_orcid` (ORCID to item), `by_name` (name to
    candidate items) and `venues` (venue name to candidate items). Re-asked together, so a
    cached set is internally consistent.
    """
    path = os.path.join(BUILD, CACHE)
    try:
        with open(path) as f:
            cache = json.load(f)
    except (OSError, ValueError):
        cache = {}
    fresh = (datetime.date.today() - datetime.timedelta(days=CACHE_DAYS)).isoformat()
    if (not refresh and cache.get("shape") == SHAPE
            and cache.get("asked", "") >= fresh and cache.get("names") == names):
        return cache
    orcids = openalex_orcids(papers)
    cache = {"shape": SHAPE, "asked": datetime.date.today().isoformat(), "names": names,
             "orcids": orcids,
             "by_orcid": items_by_orcid(
                 sorted({o for m in orcids.values() for o in m.values()})),
             "by_name": items_by_name(names),
             "venues": venue_items(sorted({(p.get("venue_display") or "").strip()
                                           for p in papers} - {"", "arXiv"}))}
    os.makedirs(BUILD, exist_ok=True)
    with open(path, "w") as f:
        json.dump(cache, f, indent=1, sort_keys=True)
    return cache


def rows(papers: list[dict], created: dict, look: dict) -> list[dict]:
    """One row per paper item with strings left to resolve, most-cited first.

    Each row's `edits` are ORCID-matched and safe to batch. Its `review` entries matched on
    a name alone and carry every candidate item, because picking between them is judgement.
    `leftover` counts the strings that matched neither, which is most of them -- a person
    whose item is labelled differently from the byline, or who has no item. Those rows still
    belong on the page, because Author Disambiguator matches name forms that an exact label
    query cannot and it works a whole paper at a time.
    """
    by_slug = {p["slug"]: p for p in papers}
    venues = look.get("venues") or {}
    state = item_state(sorted(created.values()))
    out = []
    for slug, qid in created.items():
        p, st = by_slug.get(slug), state.get(qid)
        if not p or not st:
            continue
        edits, review, leftover = [], [], []
        known = (look["orcids"] or {}).get(slug) or {}
        for s in st["strings"]:
            orcid = next((known[k] for k in keys_for(s["name"]) if k in known), None)
            hit = (look["by_orcid"] or {}).get(orcid or "")
            if hit and hit["qid"] not in st["p50"]:
                edits.append(dict(s, qid=hit["qid"], label=hit["label"], orcid=orcid))
                continue
            if hit:
                continue
            cands = [c for c in (look["by_name"] or {}).get(s["name"]) or []
                     if c["qid"] not in st["p50"]]
            (review if cands else leftover).append(dict(s, candidates=cands))
        vname = (p.get("venue_display") or "").strip()
        vcands = publications(venues.get(vname) or [])
        venue = pick_venue(vcands) if vname and not st["venue"] else None
        if edits or review or leftover or venue or (vcands and not st["venue"]):
            out.append({"slug": slug, "qid": qid,
                        "title": p.get("title_display") or p.get("title"),
                        "citations": p.get("citations") or 0,
                        "edits": edits, "review": review,
                        "leftover": len(leftover),
                        "venue_name": vname,
                        "venue": venue,
                        "venue_candidates": [] if venue else vcands})
    return sorted(out, key=lambda r: -r["citations"])


def batch(rows_: list[dict]) -> list[str]:
    """QuickStatements lines for every ORCID-matched edit.

    Two lines per author. The first states P50 with the printed name kept as an `object
    named as` (P1932) qualifier and the original series ordinal; the second drops the
    string the P50 replaces, which is the swap Author Disambiguator performs by hand.

    One more line per paper whose venue resolved to a single publication item.
    """
    L = []
    for r in rows_:
        if r.get("venue"):
            L.append("\t".join([r["qid"], "P1433", r["venue"]["qid"]]))
        for e in r["edits"]:
            add = [r["qid"], "P50", e["qid"]]
            if e["ordinal"]:
                add += ["P1545", '"%s"' % e["ordinal"]]
            add += ["P1932", '"%s"' % e["name"].replace('"', "'")]
            L.append("\t".join(add))
            L.append("\t".join(["-" + r["qid"], "P2093", '"%s"' % e["name"].replace('"', "'")]))
    return L


def fill(text: str) -> str:
    return textwrap.fill(text, 78, break_on_hyphens=False)


def write_page(rows_: list[dict], qs_path: str | None) -> str:
    n_edits = sum(len(r["edits"]) for r in rows_)
    n_review = sum(len(r["review"]) for r in rows_)
    venues = [r for r in rows_ if r.get("venue")]
    v_ask = [r for r in rows_ if r.get("venue_candidates")]
    L = ["# Wikidata co-authors", "",
         fill("Generated by `python scripts/wikidata_coauthors.py`. Every paper item this "
              "project created lists you as *author* and every co-author as *author name "
              "string*, which is a literal the knowledge graph cannot join on. Resolving "
              "a string to the author's own item is routine Wikidata maintenance and it "
              "is what connects these items to anything other than you."), "",
         fill("Nothing here creates an item for anyone. A co-author with no item stays a "
              "string, which is the correct end state for them."), ""]

    L += [f"## Venues ({len(venues)})", ""]
    if venues:
        L += [fill("None of these items says where it was published, so nothing joins a "
                   "paper to its venue. The name came from the corpus and resolved to one "
                   "publication item, so these are in the batch below with the authors."),
              ""]
        seen = {}
        for r in venues:
            seen.setdefault((r["venue"]["qid"], r["venue"]["label"]), []).append(r)
        for (qid, label), rs in sorted(seen.items(), key=lambda kv: -len(kv[1])):
            L.append(f"- {len(rs)} paper(s) → [{label}]"
                     f"(https://www.wikidata.org/wiki/{qid})")
        L.append("")
    else:
        L += ["None to add.", ""]
    if v_ask:
        L += [fill(f"{len(v_ask)} paper(s) have a venue name that matched more than one "
                   "publication item, usually two volumes of one proceedings. Those need "
                   "the right volume picked by hand. A paper whose venue matched only the "
                   "conference itself is not listed — P1433 wants the publication, and the "
                   "proceedings volume for it does not exist yet."), ""]
        for r in v_ask[:8]:
            cands = ", ".join(f"[{c['label']}]"
                              f"(https://www.wikidata.org/wiki/{c['qid']})"
                              for c in r["venue_candidates"][:3])
            L.append(f"- [ ] {(r['title'] or '')[:44]} — *{r['venue_name']}* → {cands}")
        L.append("")

    L += [f"## Matched by ORCID ({n_edits})", ""]
    if n_edits:
        L += [fill("The paper's OpenAlex record gives the co-author's ORCID and exactly "
                   "one Wikidata item states that ORCID. No name was compared, so these "
                   "need no judgement."), ""]
        if qs_path:
            L += [fill(f"Paste [`{os.path.relpath(qs_path)}`]({os.path.relpath(qs_path)}) "
                       "into <https://quickstatements.toolforge.org/#/batch>. Each author "
                       "is two lines, one adding *author* with the printed name kept as "
                       "an *object named as* qualifier, one dropping the string it "
                       "replaces."), ""]
        for r in rows_:
            if not r["edits"]:
                continue
            L.append(f"- [ ] **{r['citations']} citations** — {(r['title'] or '')[:64]}")
            for e in r["edits"]:
                L.append(f"      - {e['name']} → [{e['label'] or e['qid']}]"
                         f"(https://www.wikidata.org/wiki/{e['qid']}) "
                         f"(ORCID {e['orcid']})")
        L.append("")
    else:
        L += [fill("None. Either every ORCID-carrying co-author is already resolved, or "
                   "OpenAlex holds no ORCID for the ones that are not."), ""]

    todo = [r for r in rows_ if r["review"] or r["leftover"]]
    n_left = sum(r["leftover"] for r in todo)
    L += [f"## Remaining, one paper at a time ({len(todo)} papers, "
          f"{n_review + n_left} strings)", ""]
    if todo:
        L += [fill("The *disambiguate* link opens Author Disambiguator on the paper item. "
                   "It matches name forms an exact label search cannot -- a byline reading "
                   "*Colin A. Raffel* against an item labelled *Colin Raffel* -- and it "
                   "writes the swap correctly, so it is the tool for everything the batch "
                   "above could not do without guessing."), "",
              fill("Where a name is followed by candidate items, those are exact label or "
                   "alias matches found here. A namesake matches identically, so open the "
                   "item and check the person before accepting. Two candidates on one name "
                   "sometimes means two items for one person, which is a merge rather than "
                   "a choice."), ""]
        for r in todo[:20]:
            unresolved = len(r["review"]) + r["leftover"]
            L.append(f"- [ ] **{r['citations']} citations** — {(r['title'] or '')[:60]} "
                     f"— {unresolved} left — "
                     f"[disambiguate]({DISAMBIG}/work_item_oauth.php?id={r['qid']})")
            for v in r["review"][:4]:
                cands = ", ".join(
                    f"[{c['qid']}](https://www.wikidata.org/wiki/{c['qid']})"
                    + (f" — {c['description'][:44]}" if c["description"] else "")
                    for c in v["candidates"][:3])
                more = (f" … +{len(v['candidates']) - 3}" if len(v["candidates"]) > 3
                        else "")
                L.append(f"      - {v['name']} → {cands}{more}")
        if len(todo) > 20:
            L.append(f"- … and {len(todo) - 20} more papers, same order, in "
                     "`build/wikidata_coauthors.json`")
        L.append("")
    else:
        L += ["None. Every author string on every item is resolved.", ""]

    path = os.path.join(TASKS, "wikidata_coauthors.md")
    with open(path, "w") as f:
        f.write("\n".join(L) + "\n")
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--refresh", action="store_true",
                    help="re-ask OpenAlex and WDQS instead of reading the cache")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    papers = (read_yaml(os.path.join(DATA, "papers.yaml")) or {}).get("papers") or []
    created = ((read_yaml(os.path.join(DATA, "wikidata_created.yaml")) or {})
               .get("items") or {})
    if not created:
        if not args.quiet:
            print("no paper items yet -- run wikidata_apply.py --papers first")
        return 0

    state = item_state(sorted(created.values()))
    names = sorted({s["name"] for st in state.values() for s in st["strings"]})
    look = lookups(names, papers, args.refresh)
    rows_ = rows(papers, created, look)

    qs = batch(rows_)
    qs_path = os.path.join(TASKS, "wikidata_coauthors.qs")
    if qs:
        with open(qs_path, "w") as f:
            f.write("\n".join(qs) + "\n")
    elif os.path.exists(qs_path):
        # A batch of edits keyed to statements that may already be gone. Pasting a stale
        # copy re-adds a P50 somebody removed on purpose.
        os.remove(qs_path)
    page = write_page(rows_, qs_path if qs else None)

    out = {"asked": look.get("asked"), "strings": len(names),
           "venues": len([r for r in rows_ if r.get("venue")]),
           "venues_ask": len([r for r in rows_ if r.get("venue_candidates")]),
           "edits": sum(len(r["edits"]) for r in rows_),
           "review": sum(len(r["review"]) for r in rows_),
           "leftover": sum(r["leftover"] for r in rows_),
           "papers_left": len([r for r in rows_ if r["review"] or r["leftover"]]),
           "items": len(created), "rows": rows_}
    os.makedirs(BUILD, exist_ok=True)
    with open(os.path.join(BUILD, "wikidata_coauthors.json"), "w") as f:
        json.dump(out, f, indent=1)
    if not args.quiet:
        print(f"{out['strings']} name strings on {out['items']} items: "
              f"{out['edits']} resolvable by ORCID, "
              f"{out['review'] + out['leftover']} left across "
              f"{out['papers_left']} papers")
        print(f"venues: {out['venues']} resolved, {out['venues_ask']} ambiguous")
        print(f"wrote {os.path.relpath(page)}"
              + (f" and {os.path.relpath(qs_path)}" if qs else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
