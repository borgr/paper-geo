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
  by DBLP    the string matches a human item by name, and exactly one such item states a
             DBLP author id whose page lists this same paper. DBLP separates its own
             namesakes, so a shared publication is a shared person and this batches too.
  by name    the string matches a human item and nothing else agrees. A namesake matches
             exactly as well, so these are listed one at a time for you to confirm and are
             never batched.

Three gaps ride along in the same batch, because they are the same items and none of them
needs a judgement either.

  P1433  none of the 108 says where it was published, so nothing joins a paper to its
         venue. The name is in the corpus, and three guards keep a well-matching name from
         being the wrong answer. Only a proceedings or a journal is a target, since a
         conference name matches the event just as readily and P1433 wants the publication.
         A candidate whose title names a volume the matched name does not is refused, or a
         short paper lands among the long ones. And a dated volume has to agree with the
         paper's year, because Wikidata carries aliases that do not.
  P407   none says what language it is in, and every paper in the corpus is English.
  P953   none links a free copy. Only the publisher-hosted URL earns one, since a doi.org
         or arxiv.org link restates P356 or P818.

    python scripts/wikidata_coauthors.py --apply

writes the identifier-matched half through the API, one edit per paper item. The rest stays
a paste, because picking between two items that carry the same name is judgement.

Creates no item about anybody. Items for people who have none are out of scope by policy
rather than by omission -- Wikidata notability wants "serious and publicly available
references", and a co-author with no record of their own has none that does not originate
with us.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
import textwrap
import unicodedata
import time
import urllib.error
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (BUILD, DATA, TASKS, get, get_json, get_status,  # noqa: E402
                    norm_name, read_yaml, write_json)
from wikidata_apply import logged_in, snak  # noqa: E402

WDQS = "https://query.wikidata.org/sparql"
API = "https://www.wikidata.org/w/api.php"
DISAMBIG = "https://author-disambiguator.toolforge.org"
# A resolved string does not come back and an item's own statements change slowly, so the
# cost of a stale answer is one wasted row rather than a wrong edit. Long enough that the
# pass is free on a normal run, short enough that a name resolved elsewhere drops out.
CACHE_DAYS = 30
CACHE = "wikidata_coauthors_cache.json"
# A DBLP page is fetched once and kept far longer than the rest, because a publication list
# only grows. A stale entry can miss a confirmation and cannot produce a wrong one.
DBLP_CACHE = "dblp_titles.json"
DBLP_DAYS = 90
DBLP_SHAPE = 1
# Pages per run. DBLP answers a paced request in about a second and drops the connection
# for minutes if pushed, so a first run on a fresh cache would otherwise hold every other
# job up behind it. An author whose page is not read yet keeps their strings on the review
# list, which is where they already were.
DBLP_PER_RUN = 40
# Bumped when the cache layout changes, so an old file is re-asked rather than misread.
SHAPE = 8


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
    """Per paper item, the P2093 strings left, the P50 items present, and which of the
    properties this pass fills are already there.

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
                    strings.append({"name": name, "ordinal": ordinal, "id": s["id"]})
            out[qid] = {"strings": strings, "venue": bool(c.get("P1433")),
                        "has": {p for p in FILLS if c.get(p)}, "p50": {
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
    """ORCID to the single Wikidata item stating it. An ORCID two items claim is dropped.

    The receipts in `data/wikidata_people_created.yaml` are read as well. The query service
    lags hours behind a creation, so an item this repo just made answers here immediately
    rather than on the run after next.
    """
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
    led = read_yaml(os.path.join(DATA, "wikidata_people_created.yaml")) or {}
    named = led.get("labels") or {}
    want = set(orcids)
    for o, q in (led.get("items") or {}).items():
        if o in want:
            found.setdefault(o, set()).add(q)
            labels[q] = labels.get(q) or named.get(q, "")
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


# Properties this pass can fill without a judgement call. P407 because every paper in the
# corpus is in English, P953 because the bibliography carries a free full-text URL.
FILLS = ("P407", "P953")
ENGLISH = "Q1860"
# A URL that only restates an identifier the item already has is not worth a statement.
MIRRORS = ("doi.org", "arxiv.org")

# What P1433 accepts, in the order a tie is broken. Its value-type constraint wants a
# publication, so a conference item is never a valid target however well its name matches.
# `academic journal` is a sibling of `scientific journal` rather than a subclass, so a
# journal like Nature Machine Intelligence is invisible without it.
PUBLICATION_TYPES = ("Q1143604", "Q5633421", "Q737498")
# Searched anyway, so a name that only matches the event can say so instead of vanishing.
EVENT_TYPES = ("Q2020153", "Q47258130")


# The failure mode of a name match is a namesake, and `occupation` is the one structured
# statement that separates a footballer from a researcher. Roots rather than a list of
# labels, so the classification follows Wikidata's own subclass tree as it grows.
RESEARCH_ROOTS = ("Q1650915", "Q3400985", "Q901", "Q81096", "Q1622272")


def dblp_ids(qids: list[str]) -> dict[str, str]:
    """Item to the DBLP author id it states, empty string for one that states none."""
    out = {q: "" for q in qids}
    for i in range(0, len(qids), 200):
        vals = " ".join("wd:" + q for q in qids[i:i + 200])
        for r in sparql("SELECT ?p ?d WHERE { VALUES ?p {%s} ?p wdt:P2456 ?d }" % vals):
            out[qid_of(r["p"]["value"])] = r["d"]["value"]
    return out


def title_key(text: str) -> str:
    """A title reduced to what two catalogues can agree on."""
    return re.sub(r"[^a-z0-9]+", " ",
                  unicodedata.normalize("NFKD", text or "").lower()).strip()


def dblp_pages(look: dict, refresh: bool) -> dict[str, list[str]]:
    """Name candidate item to the reduced titles its DBLP author page lists.

    One page per author, DBLP_PER_RUN of them per run, each written to the cache as it
    arrives so the next run carries on from there.
    """
    qids = sorted({c["qid"] for cs in (look.get("by_name") or {}).values() for c in cs})
    if not qids:
        return {}
    path = os.path.join(BUILD, DBLP_CACHE)
    try:
        with open(path) as f:
            cache = json.load(f)
    except (OSError, ValueError):
        cache = {}
    fresh = (datetime.date.today() - datetime.timedelta(days=DBLP_DAYS)).isoformat()
    if refresh or cache.get("shape") != DBLP_SHAPE or cache.get("asked", "") < fresh:
        cache = {"shape": DBLP_SHAPE, "asked": datetime.date.today().isoformat(),
                 "pids": {}, "titles": {}}
    pids, titles = cache.setdefault("pids", {}), cache.setdefault("titles", {})
    ask = sorted(set(qids) - set(pids))
    if ask:
        pids.update(dblp_ids(ask))
        write_json(path, cache)
    left = sorted({pids[q] for q in qids if pids.get(q)} - set(titles))
    if len(left) > DBLP_PER_RUN:
        print("  dblp: %d author page(s), %d of them left for the next run"
              % (len(left), len(left) - DBLP_PER_RUN))
    for n, d in enumerate(left[:DBLP_PER_RUN], 1):
        code, page = get_status("https://dblp.org/pid/%s.xml" % d)
        if not page and code not in (404, 410):
            continue
        # 404 and 410 are answers, so they are cached as "this page lists nothing". Retrying
        # a disabled author page costs a paced fetch every run and never converges.
        titles[d] = sorted({title_key(x) for x in
                            re.findall(r"<title>(.*?)</title>",
                                       page.decode("utf-8", "replace"), re.S)} - {""})
        write_json(path, cache)
        if n % 10 == 0:
            print("  dblp: %d author pages read" % n)
    return {q: titles[pids[q]] for q in qids if titles.get(pids.get(q) or "")}


def researchers(qids: list[str]) -> set[str]:
    """The items that could plausibly have written a paper in this corpus.

    An item states an occupation under `RESEARCH_ROOTS`, or states none at all -- a missing
    statement is not evidence against, and 185 of the candidates have no occupation.
    """
    stated, research = set(), set()
    roots = " ".join("wd:" + q for q in RESEARCH_ROOTS)
    for i in range(0, len(qids), 200):
        vals = " ".join("wd:" + q for q in qids[i:i + 200])
        for r in sparql("SELECT ?p WHERE { VALUES ?p {%s} ?p wdt:P106 [] }" % vals):
            stated.add(qid_of(r["p"]["value"]))
        for r in sparql("SELECT DISTINCT ?p WHERE { VALUES ?p {%s} VALUES ?r {%s} "
                        "?p wdt:P106/wdt:P279* ?r }" % (vals, roots)):
            research.add(qid_of(r["p"]["value"]))
    return (set(qids) - stated) | research


def year_of(row: dict) -> int:
    """The year in a SPARQL row's optional `date` binding, or 0."""
    try:
        return int(row["date"]["value"][:4])
    except (KeyError, TypeError, ValueError):
        return 0


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
            "SELECT ?name ?p ?pLabel ?t ?date WHERE { VALUES ?name { %s } "
            "{ ?p rdfs:label ?name } UNION { ?p skos:altLabel ?name } "
            "?p wdt:P31/wdt:P279* ?t . VALUES ?t { %s } "
            "OPTIONAL { ?p wdt:P577 ?date } "
            'SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }'
            % (vals, types))
        for r in rows_:
            qid, t = qid_of(r["p"]["value"]), qid_of(r["t"]["value"])
            got = out.setdefault(r["name"]["value"], [])
            cand = next((c for c in got if c["qid"] == qid), None)
            if cand is None:
                cand = {"qid": qid, "label": r.get("pLabel", {}).get("value", ""),
                        "year": year_of(r), "types": []}
                got.append(cand)
            if t not in cand["types"]:
                cand["types"].append(t)
    return out


def publications(cands: list[dict]) -> list[dict]:
    """The candidates that are publications rather than conference events.

    An unlabelled item is dropped even when it is typed as a publication -- a bare stub is
    not something the reader can check the paste against.
    """
    return [c for c in cands
            if set(c["types"]) & set(PUBLICATION_TYPES) and c["label"]
            and not c["label"].startswith("Q")]


def proceedings_of(events: list[str]) -> dict[str, list[dict]]:
    """Conference item to the proceedings volumes published from it (P4745, reversed).

    A corpus venue name like `EMNLP 2023` matches the conference and not the volume, which
    is the name nobody writes. The conference item knows its own volumes, so this is the
    route from one to the other.
    """
    out: dict[str, list[dict]] = {}
    for i in range(0, len(events), 60):
        vals = " ".join("wd:" + q for q in events[i:i + 60])
        for r in sparql(
                "SELECT ?c ?p ?pLabel ?t ?date WHERE { VALUES ?c { %s } "
                "?p wdt:P4745 ?c . ?p wdt:P31/wdt:P279* ?t . VALUES ?t { %s } "
                "OPTIONAL { ?p wdt:P577 ?date } "
                'SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }'
                % (vals, " ".join("wd:" + t for t in PUBLICATION_TYPES))):
            got = out.setdefault(qid_of(r["c"]["value"]), [])
            qid, t = qid_of(r["p"]["value"]), qid_of(r["t"]["value"])
            cand = next((c for c in got if c["qid"] == qid), None)
            if cand is None:
                cand = {"qid": qid, "label": r.get("pLabel", {}).get("value", ""),
                        "year": year_of(r), "types": []}
                got.append(cand)
            if t not in cand["types"]:
                cand["types"].append(t)
    return out


def venue_forms(paper: dict) -> list[str]:
    """The names one paper's venue is looked up under, most canonical first.

    The short form is what the site displays, and the bibliography's own string is what
    Wikidata labels a volume with. Its BibTeX braces come off, and cutting at the first
    comma drops the `, Singapore, December 6-10, 2023` tail that no label carries.
    """
    out = []
    for f in ([(paper.get("venue_display") or "").strip()]
              + [(paper.get("venue") or "").replace("{", "").replace("}", "").strip()]):
        for form in (f, f.split(", ")[0]):
            # arXiv is a preprint repository and P818 already carries the ID, so P1433 does
            # not point at it however well the name matches an item.
            if form and not form.lower().startswith("arxiv") and form not in out:
                out.append(form)
    return out


# Words that mark one volume of a conference apart from another. A candidate whose label
# carries one of these is a specific volume, and only a name that carries it too can pick it.
VOLUME_WORDS = ("volume 1", "volume 2", "volume 3", "volume 4", "long papers",
                "short papers", "system demonstrations", "demonstrations",
                "student research workshop", "tutorial", "industry track", "findings")


def volume_named(text: str) -> set[str]:
    """The volume-distinguishing words a title carries."""
    low = text.lower()
    return {w for w in VOLUME_WORDS if w in low}


def right_year(cand: dict, year) -> bool:
    """Whether a dated volume belongs to the same year as the paper.

    Wikidata carries bad aliases -- the CoNLL 2020 proceedings answers to `CoNLL 2024` --
    and the year is the one thing a volume can be checked on against the bibliography. A
    journal states no publication year and is waved through.
    """
    if not cand.get("year") or not year:
        return True
    return abs(int(cand["year"]) - int(year)) <= 1


def is_findings(paper: dict) -> bool:
    """Whether the paper appeared in a Findings volume rather than the main proceedings.

    The ACL Anthology puts it in the identifier itself, as `2024.findings-emnlp.12`, which
    is what separates two volumes of one conference that the venue name cannot.
    """
    return "findings" in (str(paper.get("url") or "")
                          + str(paper.get("doi") or "")).lower()


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


def full_text(paper: dict) -> str:
    """The paper's free full-text URL, or "" when the item already implies it.

    A doi.org or arxiv.org link restates P356 or P818, so only a publisher-hosted copy --
    the ACL Anthology, OpenReview, the proceedings site -- earns a P953.
    """
    url = (paper.get("url") or "").strip()
    host = urllib.parse.urlparse(url).netloc.lower()
    if not host or any(host.endswith(m) for m in MIRRORS):
        return ""
    return "https://" + url.split("://", 1)[1] if url.startswith("http://") else url


def lookups(names: list[str], papers: list[dict], refresh: bool) -> dict:
    """The network answers this pass needs, cached in `build/` for CACHE_DAYS.

    Returns `orcids` (name to ORCID), `by_orcid` (ORCID to item), `by_name` (name to
    candidate items), `venues` (venue name to candidate items) and `proceedings` (a
    conference item to its volumes). Re-asked together, so a cached set is internally
    consistent. `dblp` rides along from a file of its own, on its own longer clock.
    """
    path = os.path.join(BUILD, CACHE)
    try:
        with open(path) as f:
            cache = json.load(f)
    except (OSError, ValueError):
        cache = {}
    fresh = (datetime.date.today() - datetime.timedelta(days=CACHE_DAYS)).isoformat()
    if (refresh or cache.get("shape") != SHAPE
            or cache.get("asked", "") < fresh or cache.get("names") != names):
        orcids = openalex_orcids(papers)
        cache = {"shape": SHAPE, "asked": datetime.date.today().isoformat(),
                 "names": names, "orcids": orcids,
                 "by_orcid": items_by_orcid(
                     sorted({o for m in orcids.values() for o in m.values()})),
                 "by_name": items_by_name(names),
                 "venues": venue_items(
                     sorted({f for p in papers for f in venue_forms(p)}))}
        cache["research"] = sorted(researchers(sorted(
            {c["qid"] for cs in cache["by_name"].values() for c in cs})))
        cache["proceedings"] = proceedings_of(sorted(
            {c["qid"] for cs in cache["venues"].values() for c in cs
             if not publications([c])}))
        write_json(path, cache, indent=1, sort_keys=True)
    cache["dblp"] = dblp_pages(cache, refresh)
    return cache


def rows(papers: list[dict], created: dict, look: dict) -> list[dict]:
    """One row per paper item with strings left to resolve, most-cited first.

    Each row's `edits` are safe to batch, every one settled by an identifier or by a shared
    publication record and none by a name. Its `review` entries matched on a name alone and
    carry every candidate item, because picking between them is judgement.
    `leftover` counts the strings that matched neither, which is most of them -- a person
    whose item is labelled differently from the byline, or who has no item. Those rows still
    belong on the page, because Author Disambiguator matches name forms that an exact label
    query cannot and it works a whole paper at a time.
    """
    by_slug = {p["slug"]: p for p in papers}
    venues = look.get("venues") or {}
    procs = look.get("proceedings") or {}
    state = item_state(sorted(created.values()))
    plausible = set(look.get("research") or [])
    dblp = look.get("dblp") or {}
    out = []
    for slug, qid in created.items():
        p, st = by_slug.get(slug), state.get(qid)
        if not p or not st:
            continue
        edits, review, leftover, dropped = [], [], [], 0
        known = (look["orcids"] or {}).get(slug) or {}
        here = title_key(p.get("title_display") or p.get("title"))
        for s in st["strings"]:
            orcid = next((known[k] for k in keys_for(s["name"]) if k in known), None)
            hit = (look["by_orcid"] or {}).get(orcid or "")
            if hit and hit["qid"] not in st["p50"]:
                edits.append(dict(s, qid=hit["qid"], label=hit["label"], orcid=orcid,
                                  via="ORCID %s" % orcid))
                continue
            if hit:
                continue
            named = [c for c in (look["by_name"] or {}).get(s["name"]) or []
                     if c["qid"] not in st["p50"]]
            # A candidate whose stated occupation is nothing like research is a namesake,
            # not a lead, and the long tail of these is what makes a name unreadable.
            cands = [c for c in named if c["qid"] in plausible]
            dropped += len(named) - len(cands)
            # DBLP disambiguates its own author pages, so a candidate whose page lists this
            # very paper wrote it rather than merely sharing a name with whoever did. Two
            # such candidates mean DBLP holds one person under two ids, which is a merge and
            # not a choice, so the string stays a question.
            shared = [c for c in cands if here in (dblp.get(c["qid"]) or ())]
            if here and len(shared) == 1:
                edits.append(dict(s, qid=shared[0]["qid"],
                                  label=shared[0].get("label") or s["name"],
                                  orcid=shared[0].get("orcid") or "",
                                  via="DBLP, which lists this paper on their page"))
                continue
            (review if cands else leftover).append(dict(s, candidates=cands))
        vname = (p.get("venue_display") or "").strip()
        fills = {}
        if "P407" not in st["has"]:
            fills["P407"] = ENGLISH
        url = full_text(p)
        if url and "P953" not in st["has"]:
            fills["P953"] = '"%s"' % url
        vcands, venue = [], None
        # Each form is tried on its own and the first that settles wins. Pooling them makes
        # the display name and the bibliography's name look like two rival volumes.
        for form in venue_forms(p):
            raw = venues.get(form) or []
            cands = publications(raw)
            if not cands:
                # The name matched the conference and not its volume, so ask the conference.
                found = is_findings(p)
                cands = publications([v for c in raw
                                      for v in (procs.get(c["qid"]) or [])
                                      if ("Findings" in v["label"]) == found])
            # A label naming a volume the form does not name is a guess. `Proceedings of
            # the 56th Annual Meeting of the ACL` is an alias of the Long Papers volume, so
            # a short paper matching on it would be filed in the wrong book.
            named = volume_named(form)
            cands = [c for c in cands if volume_named(c["label"]) <= named
                     and right_year(c, p.get("year"))]
            if not cands:
                continue
            vcands = vcands or cands
            venue = pick_venue(cands)
            if venue:
                break
        # An item stating a venue is settled, whichever way this pass read the name. Both the
        # answer and the candidates go, or the paper comes back next run as a question about
        # something it already says.
        if st["venue"]:
            venue, vcands = None, []
        if edits or review or leftover or venue or fills or vcands:
            out.append({"slug": slug, "qid": qid, "fills": fills,
                        "title": p.get("title_display") or p.get("title"),
                        "citations": p.get("citations") or 0,
                        "edits": edits, "review": review,
                        "leftover": len(leftover), "dropped": dropped,
                        "venue_name": vname,
                        "venue": venue,
                        "venue_candidates": [] if venue else vcands})
    return sorted(out, key=lambda r: -r["citations"])


def batch(rows_: list[dict]) -> list[str]:
    """QuickStatements lines for every ORCID-matched edit.

    Two lines per author. The first states P50 with the printed name kept as an `object
    named as` (P1932) qualifier and the original series ordinal; the second drops the
    string the P50 replaces, which is the swap Author Disambiguator performs by hand.

    One more line per paper whose venue resolved to a single publication item, and one per
    property in `FILLS` the item is missing.
    """
    L = []
    for r in rows_:
        if r.get("venue"):
            L.append("\t".join([r["qid"], "P1433", r["venue"]["qid"]]))
        for prop, val in sorted((r.get("fills") or {}).items()):
            L.append("\t".join([r["qid"], prop, val]))
        for e in r["edits"]:
            add = [r["qid"], "P50", e["qid"]]
            if e["ordinal"]:
                add += ["P1545", '"%s"' % e["ordinal"]]
            add += ["P1932", '"%s"' % e["name"].replace('"', "'")]
            L.append("\t".join(add))
            L.append("\t".join(["-" + r["qid"], "P2093", '"%s"' % e["name"].replace('"', "'")]))
    return L


def payload(r: dict) -> dict:
    """One paper item's whole batch as a `wbeditentity` payload, or {}.

    Everything for one item in a single edit, which matters most for the author swap: the
    `P50` and the removal of the `P2093` it replaces are one statement of the same fact, and
    an interrupted run that landed only one of them leaves the paper either crediting nobody
    or crediting the same person twice.
    """
    claims = []
    if r.get("venue"):
        claims.append(statement(snak("P1433", r["venue"]["qid"])))
    for prop, val in sorted((r.get("fills") or {}).items()):
        claims.append(statement(snak(prop, val)))
    for e in r["edits"]:
        quals = {"P1932": [snak("P1932", e["name"])]}
        if e["ordinal"]:
            quals["P1545"] = [snak("P1545", e["ordinal"])]
        claims.append(statement(snak("P50", e["qid"]), quals))
        claims.append({"id": e["id"], "remove": ""})
    return {"claims": claims} if claims else {}


def statement(main: dict, quals: dict | None = None) -> dict:
    c = {"mainsnak": main, "type": "statement", "rank": "normal"}
    if quals:
        c["qualifiers"] = quals
    return c


def apply_rows(s, rows_: list[dict]) -> tuple[int, int]:
    """Write each row's batch, one edit per paper item."""
    todo = [(r, payload(r)) for r in rows_]
    todo = [(r, d) for r, d in todo if d]
    ok = 0
    for i, (r, data) in enumerate(todo, 1):
        try:
            s.edit("wbeditentity", id=r["qid"], data=json.dumps(data),
                   summary="resolve author name strings matched by ORCID or by a shared "
                           "DBLP publication, and fill the "
                           "venue, language and full text from the bibliography (paper-geo)")
            ok += 1
            print("  %d/%d %s — %d statement(s), %s"
                  % (i, len(todo), r["qid"], len(data["claims"]), r["slug"]))
        except (RuntimeError, urllib.error.URLError) as e:
            print("  %d/%d FAILED %s — %s\n     %s" % (i, len(todo), r["qid"], r["slug"], e))
        time.sleep(1.5)
    return ok, len(todo)


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

    fills = [r for r in rows_ if r.get("fills")]
    if fills:
        n_lang = sum(1 for r in fills if "P407" in r["fills"])
        n_url = sum(1 for r in fills if "P953" in r["fills"])
        L += [f"## Language and full text ({n_lang + n_url})", "",
              fill(f"Also in the same paste, and also nothing to decide. {n_lang} item(s) "
                   f"do not say what language the paper is in, and {n_url} carry no link to "
                   "a free copy — the publisher-hosted one, since a doi.org or arxiv.org "
                   "link only restates an identifier the item already has."), ""]

    n_dblp = sum(1 for r in rows_ for e in r["edits"] if e["via"].startswith("DBLP"))
    L += [f"## Settled by a record rather than a name ({n_edits})", ""]
    if n_edits:
        L += [fill("Two kinds of evidence and no name compared in either, so none of "
                   f"these needs a judgement. {n_edits - n_dblp} came from the paper's "
                   "OpenAlex record giving the co-author's ORCID, with exactly one "
                   f"Wikidata item stating it. {n_dblp} came from DBLP, where exactly one "
                   "candidate's author page lists this same paper -- DBLP separates its "
                   "own namesakes, so a shared publication is a shared person."), ""]
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
                         f"({e['via']})")
        L.append("")
    else:
        L += [fill("None left. Every co-author an ORCID or a DBLP page could reach is "
                   "already resolved."), ""]

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
        dropped = sum(r.get("dropped") or 0 for r in rows_)
        if dropped:
            L += [fill("%d name matches are not listed. Each states an occupation nothing "
                       "like research -- footballer, actor, politician -- so the name is a "
                       "coincidence. An item stating no occupation at all is still listed."
                       % dropped), ""]
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
    ap.add_argument("--apply", action="store_true",
                    help="write the identifier-matched batch through the API")
    ap.add_argument("--limit", type=int, default=0,
                    help="with --apply, stop after this many paper items")
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
           "fills": sum(len(r.get("fills") or {}) for r in rows_),
           "venues_ask": len([r for r in rows_ if r.get("venue_candidates")]),
           "edits": sum(len(r["edits"]) for r in rows_),
           "dblp": sum(1 for r in rows_ for e in r["edits"]
                       if e["via"].startswith("DBLP")),
           "review": sum(len(r["review"]) for r in rows_),
           "leftover": sum(r["leftover"] for r in rows_),
           "papers_left": len([r for r in rows_ if r["review"] or r["leftover"]]),
           "dropped": sum(r.get("dropped") or 0 for r in rows_),
           "items": len(created), "rows": rows_}
    write_json(os.path.join(BUILD, "wikidata_coauthors.json"), out, indent=1)
    if not args.quiet:
        print(f"{out['strings']} name strings on {out['items']} items: "
              f"{out['edits'] - out['dblp']} settled by ORCID, {out['dblp']} by a shared "
              f"DBLP publication, {out['review'] + out['leftover']} left across "
              f"{out['papers_left']} papers")
        print(f"venues: {out['venues']} resolved, {out['venues_ask']} ambiguous; "
              f"{out['fills']} language and full-text statements")
        print(f"wrote {os.path.relpath(page)}"
              + (f" and {os.path.relpath(qs_path)}" if qs else ""))
    if not args.apply or not qs:
        return 0
    s = logged_in()
    print("acting as %s" % s.user)
    done, want = apply_rows(s, rows_[:args.limit] if args.limit else rows_)
    print("%d/%d items written" % (done, want))
    return 0 if done == want else 1


if __name__ == "__main__":
    sys.exit(main())
