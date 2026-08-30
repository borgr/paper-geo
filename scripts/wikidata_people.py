"""Create Wikidata items for the co-authors who have an ORCID and no item.

97 of the 156 co-author ORCIDs in the corpus belong to nobody Wikidata has an item for,
and that absence is what leaves most name mentions unresolvable. `wikidata_coauthors.py`
states `author` by matching an ORCID against the item that claims it, so a match needs an
item on the other side.

    python scripts/wikidata_people.py            # what would be created, and from what
    python scripts/wikidata_people.py --apply    # create them

Each item is built from the person's own ORCID record -- the name they publish under, the
organisation they say employs them now, the works they list. Nothing is taken from a name
match, so a namesake cannot end up in the batch.

A person is only created when Wikidata has no human item under that name at all. Where one
exists and states no ORCID it is very often the same person reached by a different route,
and a second item for somebody who already has one is the one mistake here that somebody
else has to clean up. Those are held back and listed instead.

Read-only until `--apply`, which creates the items through the API and writes each QID to
`data/wikidata_people_created.yaml` before the next one starts. `tasks/wikidata_people.qs`
is the same batch as QuickStatements text, for a revoked credential.

Nothing follows by hand. The new items claim their ORCIDs, so the next
`wikidata_coauthors.py` run matches them and writes the `author` statements itself.
"""

import argparse
import datetime
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import (BUILD, DATA, TASKS, clipped, get_status, host_of, read_yaml,
                    write_json, write_task, write_yaml)
from wikidata_coauthors import (CACHE, SCHOLARLY, batched, fill,  # noqa: F401
                               items_block, items_by_orcid, qid_of, researchers,
                               title_key, values, wdqs_quiet)
from wikidata_apply import (CAL, Session, create_items,  # noqa: F401
                            logged_in, recorded)
from wikidata_orgs import labels_of

WIKI = "https://www.wikidata.org/w/api.php"
LEDGER = "wikidata_people_created.yaml"
# Which existing item a held co-author is, answered by hand in data/overrides.yaml.
DECIDED = "wikidata_people"
LEDGER_NOTE = (
    "People `scripts/wikidata_people.py --apply` created, ORCID -> QID. A receipt, not a "
    "decision. Wikidata's query service lags hours behind an edit, so for those hours this "
    "file is the only thing that knows the item exists -- without it a second run creates "
    "the person twice, and a duplicate human item is the one mistake here somebody else "
    "has to clean up. Never edit by hand.")
CACHE_PEOPLE = "orcid_records.json"
CACHE_DAYS = 30
# Bump to re-ask when `record` starts reading a different field.
SHAPE = 3
# What a same-name item states about itself, beside its description -- occupation,
# educated at, employer. Enough to tell a naturalist from an NLP researcher.
FACTS = ("occupations", "education", "employers")
# The occupation every item carries, and the class of the subject itself.
HUMAN, RESEARCHER = "Q5", "Q1650915"
REF_URL, REF_DATE = "S854", "S813"


def wanted() -> dict[str, int]:
    """ORCID to how many corpus papers carry it, for the ORCIDs no item claims.

    Read from the co-author job's cache, which `update.py` refreshes just before this
    runs.
    """
    with open(os.path.join(BUILD, CACHE)) as f:
        cache = json.load(f)
    claimed = dict(cache.get("by_orcid") or {})
    claimed.update(recorded(os.path.join(DATA, LEDGER)))
    out: dict[str, int] = {}
    for names in (cache.get("orcids") or {}).values():
        for orcid in (names or {}).values():
            if not claimed.get(orcid):
                out[orcid] = out.get(orcid, 0) + 1
    return out


def record(orcid: str) -> dict:
    """What the two public records for one ORCID say, reduced to what an item needs.

    ORCID is authoritative on the name and the employer, and both can be private there --
    a locked-down record can still belong to somebody with hundreds of papers. OpenAlex
    answers for the same ORCID and is asked as well, so a private work list does not read
    as an empty one.

    `partial` is set when either side did not answer. Everything here reads an absence as a
    statement -- no works means this ORCID publishes nothing, so leave the person out -- and
    OpenAlex refuses the whole day once its budget is spent, which would drop half the
    co-authors from a run and cache that answer for a month.
    """
    st, t = get_status("https://pub.orcid.org/v3.0/%s/record" % orcid,
                       accept="application/json")
    if isinstance(t, bytes):
        t = t.decode("utf-8", "replace")
    d = json.loads(t or "{}")
    name = (d.get("person") or {}).get("name") or {}
    def val(k):
        return ((name.get(k) or {}) or {}).get("value") or ""
    acts = d.get("activities-summary") or {}
    now = []
    for group in ((acts.get("employments") or {}).get("affiliation-group") or []):
        for s in group.get("summaries") or []:
            e = s.get("employment-summary") or {}
            # A closed employment is where they used to be, which does not describe them.
            if not e.get("end-date"):
                now.append(((e.get("organization") or {}).get("name") or "").strip())
    # Newest first, and only a couple: the point is to show what field this record is in,
    # which the author reads against the co-author they remember. A title also carries a
    # year often enough to sort on, and an untitled group is dropped by the `if v`.
    dated = []
    for group in ((acts.get("works") or {}).get("group") or []):
        for w in group.get("work-summary") or []:
            v = ((w.get("title") or {}).get("title") or {}).get("value")
            y = (((w.get("publication-date") or {}).get("year") or {}).get("value") or "")
            if v:
                dated.append((y, v))
            break
    # `authors/orcid:<id>`, not `authors/https://orcid.org/<id>`: OpenAlex prices the
    # second form and refuses it for the rest of the day once the budget is spent, while
    # the canonical by-id form is free and answers the same record (measured).
    oa_st, oa_raw = get_status("https://api.openalex.org/authors/orcid:" + orcid,
                               accept="application/json")
    oa = (json.loads(oa_raw or b"{}") if oa_st == 200 else {}) or {}
    return {"partial": st != 200 or oa_st != 200,
            "label": val("credit-name") or " ".join(
                x for x in (val("given-names"), val("family-name")) if x).strip(),
            "openalex_label": oa.get("display_name") or "",
            "employers": sorted({o for o in now if o}),
            "openalex_employers": sorted({(i.get("display_name") or "").strip()
                                          for i in oa.get("last_known_institutions") or []
                                          if i.get("display_name")}),
            "works": len(((acts.get("works") or {}).get("group") or [])),
            "work_titles": [v for _y, v in sorted(dated, reverse=True)[:2]],
            "openalex_works": oa.get("works_count") or 0}


def records(orcids: list[str], refresh: bool) -> dict[str, dict]:
    """ORCID to its reduced record, cached in `build/` for CACHE_DAYS."""
    path = os.path.join(BUILD, CACHE_PEOPLE)
    try:
        with open(path) as f:
            cache = json.load(f)
    except (OSError, ValueError):
        cache = {}
    fresh = (datetime.date.today() - datetime.timedelta(days=CACHE_DAYS)).isoformat()
    if refresh or cache.get("shape") != SHAPE or cache.get("asked", "") < fresh:
        cache = {"shape": SHAPE, "asked": datetime.date.today().isoformat(), "records": {}}
    got = cache.setdefault("records", {})
    out = dict(got)
    for orcid in orcids:
        if orcid not in out:
            r = record(orcid)
            out[orcid] = r
            # Used this run, never written: a record built on a fetch that did not happen
            # would answer for CACHE_DAYS as though the source had said nothing.
            if not r["partial"]:
                got[orcid] = {k: v for k, v in r.items() if k != "partial"}
    write_json(path, cache, indent=1, sort_keys=True)
    return out


def plain(name: str) -> str:
    """An institution name without OpenAlex's disambiguating country, or "" if it has none.

    OpenAlex writes "IBM (United States)", which is no Wikidata label and no alias -- so the
    name resolves to nothing, and the parenthetical reaches a description meant to read the
    way the rest of Wikidata does.
    """
    m = re.fullmatch(r"(.+?) \([^()]+\)", name.strip())
    return m.group(1) if m else ""


def spellings(name: str) -> list[str]:
    """Every spelling of an institution name worth matching, the name as written first.

    ORCID writes "The Hebrew University of Jerusalem" where Wikidata drops the article, and
    OpenAlex writes "IBM (United States)" where Wikidata has "IBM".
    """
    n = " ".join(name.split())
    return [n] + [v for v in (n[4:] if n.startswith("The ") else "", plain(n)) if v]


def employer_items(names: list[str]) -> dict[str, str]:
    """Organisation name to the single organisation item carrying it as a label or alias.


    An institution is not a person, so an exact match is safe here in a way it never is
    for a co-author. A name two items carry is dropped, as is one no item carries -- the
    employer then goes unstated rather than guessed at.
    """
    forms = {n: spellings(n) for n in names}
    every = sorted({f for fs in forms.values() for f in fs})
    hits: dict[str, set[str]] = {}
    for r in batched(every, lambda fs:
                     "SELECT ?n ?i WHERE { VALUES ?n {%s} "
                     "{ ?i rdfs:label ?n } UNION { ?i skos:altLabel ?n } "
                     "?i wdt:P31/wdt:P279* wd:Q43229 }" % values(fs)):
        hits.setdefault(r["n"]["value"], set()).add(qid_of(r["i"]["value"]))
    # The name as written is read first, and a rewritten form only where it answered
    # nothing. Pooling them would drop a name whose two forms are two organisations.
    one = {}
    for n, fs in forms.items():
        answered = next((hits[f] for f in fs if hits.get(f)), set())
        if len(answered) == 1:
            one[n] = next(iter(answered))
    # Wikidata's own label rather than ORCID's wording, so the description reads the way
    # the rest of Wikidata does.
    live = labels_of(sorted(set(one.values())))
    return {n: {"qid": q, "label": live.get(q) or n} for n, q in one.items()}


def cased(rec: dict) -> str:
    """The person's name in the form to label an item with.

    ORCID stores whatever the person typed, so "mohit bansal", "YANGSIBO HUANG" and
    "Mathieu LAURIERE" all occur -- a shouted surname beside a normal given name is the
    common form, and a middle initial is not one of these. OpenAlex normalises the same name from publisher metadata and answers for
    those. A name ORCID already cases like a name is left exactly as given, since no rule
    handles "van der Maaten" and "McDonald" at once.
    """
    orcid_name = " ".join((rec.get("label") or "").split())
    words = orcid_name.split()
    raw = orcid_name and (orcid_name == orcid_name.lower()
                          or any(w.isalpha() and w.isupper() and len(w) > 1
                                 for w in words))
    return (" ".join((rec.get("openalex_label") or "").split()) if raw
            else orcid_name) or " ".join((rec.get("openalex_label") or "").split())


# Set to the first search-index call Wikidata did not answer. An item nobody found is an
# item this pass creates, so `main` creates nothing while this or `wdqs_quiet()` is set.
_refused = ""


def asked(url: str) -> dict:
    """One `w/api.php` call, `{}` if it did not answer, with the refusal recorded.

    The API answers 200 with an empty `search` for a name it carries no item under, so any
    other status is a refusal rather than a report.
    """
    global _refused
    st, raw = get_status(url, accept="application/json")
    try:
        d = json.loads(raw) if st == 200 and raw else None
    except ValueError:
        d = None
    if d is None:
        _refused = _refused or f"{host_of(url)} -> HTTP {st}"
    return d or {}


def namesakes(labels: list[str]) -> dict[str, list[dict]]:
    """Name to every human item carrying it, with the ORCID and description each states.

    Asked of the search index rather than the query service, for two reasons the query
    service cannot cover: it matches every language and every alias, so an item labelled
    only in German still answers, and it is live, where the query service lags hours behind
    a creation.

    Each item carries what it states about itself under `FACTS`, so a namesake can be told
    from the co-author without opening it.

    Reports rather than decides -- `keeps` reads the answer.
    """
    found: dict[str, set[str]] = {}
    for n in labels:
        d = asked(WIKI + "?action=wbsearchentities&type=item&language=en"
                  "&uselang=en&limit=20&format=json&search=" + urllib.parse.quote(n))
        for h in d.get("search") or []:
            for form in (h.get("label"), h.get("match", {}).get("text"),
                         h.get("aliases", [None])[0]):
                if form and form.strip().lower() == n.lower():
                    found.setdefault(n, set()).add(h["id"])
                    break
    qids = sorted({q for qs in found.values() for q in qs})
    seen: dict[str, dict] = {}
    for i in range(0, len(qids), 50):
        d = asked(WIKI + "?action=wbgetentities&props=claims|descriptions"
                  "&languages=en&format=json&ids=" + "|".join(qids[i:i + 50]))
        for q, e in (d.get("entities") or {}).items():
            cl = e.get("claims") or {}
            if not any((c["mainsnak"].get("datavalue") or {}).get("value", {}).get("id") == HUMAN
                       for c in cl.get("P31") or []):
                continue
            orcid = ""
            for c in cl.get("P496") or []:
                orcid = (c["mainsnak"].get("datavalue") or {}).get("value") or ""
            seen[q] = {"qid": q, "orcid": orcid,
                       "description": (e.get("descriptions", {}).get("en") or {}).get("value", ""),
                       "occupations": points_at(cl, "P106"),
                       "education": points_at(cl, "P69"),
                       "employers": points_at(cl, "P108")}
    live = labels_of(sorted({q for it in seen.values() for k in FACTS for q in it[k]}))
    for it in seen.values():
        for k in FACTS:
            # Empty where the query service has no label yet, which is what a brand-new item
            # looks like. `summary` leaves those out rather than printing a bare QID.
            it[k] = {q: live.get(q) or "" for q in it[k]}
    return {n: [seen[q] for q in sorted(qs) if q in seen]
            for n, qs in found.items() if any(q in seen for q in qs)}


def points_at(claims: dict, prop: str) -> list[str]:
    """The item QIDs one property's statements point at."""
    out = []
    for c in claims.get(prop) or []:
        q = ((c["mainsnak"].get("datavalue") or {}).get("value") or {}).get("id")
        if q:
            out.append(q)
    return out


def about(qids: list[str]) -> dict[str, dict]:
    """Per same-name item, the papers it is an author of and whether it could be a researcher.

    Two query-service reads for the whole set, so the cost does not grow with the number of
    people asked about.
    """
    if not qids:
        return {}
    plausible = researchers(qids)
    titles: dict[str, list[str]] = {}
    for r in batched(qids, lambda qs:
                     "SELECT ?p ?t WHERE { VALUES ?p {%s} ?w wdt:P50 ?p . "
                     "?w rdfs:label ?t FILTER(LANG(?t) = 'en') }" % items_block(qs),
                     size=50, endpoint=SCHOLARLY):
        titles.setdefault(qid_of(r["p"]["value"]), []).append(r["t"]["value"])
    return {q: {"works": sorted(set(titles.get(q) or [])), "research": q in plausible}
            for q in qids}


def coauthored() -> dict[str, set[str]]:
    """ORCID to the reduced titles of the corpus papers whose author list it is on.

    The co-author cache already resolved each name on each paper to an ORCID, so this only
    turns that inside out. Reduced with `title_key`, because a Wikidata paper title and a
    bibliography one differ in punctuation and case and in nothing else.
    """
    with open(os.path.join(BUILD, CACHE)) as f:
        by_slug = (json.load(f).get("orcids") or {})
    titles = {p["slug"]: title_key(p.get("title") or "")
              for p in ((read_yaml(os.path.join(DATA, "papers.yaml")) or {}).get("papers")
                        or [])}
    out: dict[str, set[str]] = {}
    for slug, names in by_slug.items():
        for orcid in (names or {}).values():
            if titles.get(slug):
                out.setdefault(orcid, set()).add(titles[slug])
    return out


def where_at(n: dict) -> dict[str, str]:
    """Every institution a same-name item names, as employer and as alma mater alike.

    ORCID names where somebody works and the item often names where they studied, which for
    one researcher is frequently the same place. Neither role is the claim being tested --
    the claim is that both records put this name at this institution.
    """
    return {**(n.get("employers") or {}), **(n.get("education") or {})}


def verdict(p: dict, mine: set[str]) -> dict:
    """Which same-name item this person is, where the public records settle it.

    `{"qid": …}` names the item to put their ORCID on, `{}` leaves the answer to a person.
    The `why` is printed by both task pages.

    Only ever the same-person direction. An ORCID statement is undone by removing it, where a
    second item for somebody who already has one takes an administrator to merge, so nothing
    here concludes that a namesake is a namesake -- an occupation outside `RESEARCH_ROOTS`
    reads that way and is not, because the subclass tree has holes (statistician reaches no
    root at all).
    """
    same = [n for n in p["namesakes"] if not n["orcid"]]
    shared = {n["qid"]: next((w for w in n.get("works") or [] if title_key(w) in mine), "")
              for n in same}
    for n in same:
        if shared[n["qid"]]:
            return {"qid": n["qid"],
                    "why": 'it is stated as an author of "%s"' % shared[n["qid"]]}
    at = {q for _label, q, _ref in p["employers"]}
    both = [n for n in same if at & set(where_at(n))]
    if len(same) == 1 and len(both) == 1:
        named = where_at(both[0])
        return {"qid": both[0]["qid"],
                "why": "it and their ORCID record name the same institution, "
                       + ", ".join(sorted(named[q] for q in at & set(named)))}
    return {}


def summary(n: dict) -> str:
    """What a same-name item states about itself, on one line, for a reader deciding."""
    desc = n.get("description") or ""
    bits = [desc] if desc else []
    for k, lead in (("occupations", ""), ("education", "studied at "), ("employers", "at ")):
        # A description of "statistician" beside an occupation of statistician is one fact.
        vals = sorted(v for v in (n.get(k) or {}).values()
                      if v and v.lower() not in desc.lower())
        if vals:
            bits.append(lead + ", ".join(vals))
    works = n.get("works") or []
    if works:
        bits.append('%d paper%s including "%s"'
                    % (len(works), "" if len(works) == 1 else "s", works[0]))
    return " · ".join(bits) or "states nothing beyond the name"


def sorted_out(ok: list[dict], answered: dict[str, str]) -> tuple[list, list, list]:
    """The three fates of a co-author with an ORCID: create, link, or still ask.

    An answer given by hand overrides the hold it was asked about. `no` says the ORCID is a
    namesake's, so that person is in none of the three and is never asked about again.

    Raises on anything else written under `wikidata_people`, because a typo reads as `no` and
    drops somebody silently, which is the one outcome the output cannot be told apart from.
    """
    bad = {o: v for o, v in answered.items()
           if not (re.fullmatch(r"Q[1-9]\d*", str(v)) or v in ("new", "no"))}
    if bad:
        raise ValueError("data/overrides.yaml %s: %s is not a QID, `new` or `no`"
                         % (DECIDED, ", ".join("%s: %s" % kv for kv in sorted(bad.items()))))
    return ([p for p in ok if not p["namesakes"] or answered.get(p["orcid"]) == "new"],
            [(p, answered[p["orcid"]]) for p in ok
             if p["namesakes"] and (answered.get(p["orcid"]) or "").startswith("Q")],
            [p for p in ok if p["namesakes"] and not answered.get(p["orcid"])])


def decided() -> dict[str, str]:
    """ORCID to the answer given by hand for a held person.

    A QID puts the ORCID on that item, `new` creates one, and `no` says the identifier
    belongs to a namesake rather than to the co-author, which drops the person from every
    list here — no item created, no statement written, and no question asked again.
    """
    return ((read_yaml(os.path.join(DATA, "overrides.yaml")) or {}).get(DECIDED) or {})


def linked(p: dict, day: str) -> dict:
    """A `wbeditentity` payload adding this person's ORCID to the item they turned out to be."""
    return {"claims": [c for c in payload(p, day)["claims"]
                       if c["mainsnak"]["property"] == "P496"]}


def keeps(p: dict, same: list[dict]) -> list[dict]:
    """The same-name items that stop this person being created, or nothing.

    An item stating no ORCID is very often this person reached from a source that gave no
    identifier, and a second item for somebody who already has one can only be undone by an
    administrator. An item stating an ORCID states a different one, since ours matched
    nothing on the way in, so that one is somebody else.

    An item sharing the label and description is held whatever it states, because Wikidata
    refuses a duplicate pair. Which detail separates two same-name researchers with the same
    employer is not a call to make from a name.
    """
    return [s for s in same
            if not s["orcid"] or s["description"] == p["description"]]


def states(rec: dict) -> str:
    """What the ORCID record itself says, on one line, beside the same-name candidates.

    The ORCID on a co-author's name came from OpenAlex reading a paper whose own metadata
    carries no author identifiers, so on a common name it can be a namesake's. A record
    listing emergency-medicine papers under a name on an evaluation paper says so at a
    glance, where the bare identifier says nothing either way.
    """
    bits = list(rec.get("employers") or [])[:2]
    bits += ['"%s"' % clipped(t, 58) for t in (rec.get("work_titles") or [])[:2]]
    if not bits:
        bits = ["%d work(s), no employer and no title" % (rec.get("works") or 0)
                if rec.get("works") else "nothing public beyond the name"]
    return " · ".join(bits)


def described(orcid: str, rec: dict, employers: dict[str, dict]) -> dict:
    """One person's item, or the reason the public records do not describe a person.

    `works` names the page that shows they publish, which is what `occupation` rests on.
    The employer is what makes two same-name researchers distinguishable, and Wikidata
    refuses a label and description pair that already exists. ORCID's answer is taken
    first, and OpenAlex stands in only where it names exactly one institution. Each carries
    whichever of the two said it.
    """
    # A record built on a fetch that did not happen settles nothing, so the two outcomes
    # that rest on a record being silent are deferred to a run where both sides answered.
    # A person the record does describe stands either way, because ORCID answers for the
    # name and the employer and OpenAlex only ever stands in where ORCID is silent.
    out = "later" if rec.get("partial") else "skip"
    label = cased(rec)
    if not label:
        return {"orcid": orcid, out: "neither ORCID nor OpenAlex gives a name"}
    who = "https://orcid.org/" + orcid
    oa = "https://openalex.org/authors/https://orcid.org/" + orcid
    if rec.get("works"):
        works = who
    elif rec.get("openalex_works"):
        works = oa
    else:
        return {"orcid": orcid, out: "no works on either record"}
    at = [dict(employers[e], ref=who) for e in rec["employers"] if e in employers]
    # OpenAlex lists every institution its own author disambiguation has seen, so more than
    # one means it is unsure and none of them can be stated -- the list for one co-author
    # here spans three continents. A single entry is its confident answer and is used.
    oa_at = rec.get("openalex_employers") or []
    if not at and len(oa_at) == 1 and oa_at[0] in employers:
        at = [dict(employers[oa_at[0]], ref=oa)]
    # The description is free text where `employer` needs an item to point at, so an
    # employer Wikidata has never heard of still distinguishes two same-name researchers.
    said = (rec["employers"] or (oa_at if len(oa_at) == 1 else []) or [""])[0]
    where = at[0]["label"] if at else (plain(said) or said)
    return {"orcid": orcid, "label": label, "works": works,
            "description": "researcher at " + where if where else "researcher",
            "record_says": states(rec),
            "partial": bool(rec.get("partial")),
            "unnamed": sorted({n for n in rec["employers"] + oa_at if n not in employers}),
            "employers": [(e["label"], e["qid"], e["ref"]) for e in at]}


def batch(people: list[dict], day: str) -> list[str]:
    """QuickStatements lines: one CREATE per person, each statement sourced to the record
    that said it."""
    L = []
    def ref(url):
        return [REF_URL, '"%s"' % url, REF_DATE, "+%sT00:00:00Z/11" % day]
    for p in people:
        who = "https://orcid.org/" + p["orcid"]
        L.append("CREATE")
        L.append("\t".join(["LAST", "Len", '"%s"' % p["label"]]))
        L.append("\t".join(["LAST", "Den", '"%s"' % p["description"]]))
        L.append("\t".join(["LAST", "P31", HUMAN] + ref(who)))
        L.append("\t".join(["LAST", "P106", RESEARCHER] + ref(p["works"])))
        L.append("\t".join(["LAST", "P496", '"%s"' % p["orcid"]] + ref(who)))
        for _, qid, src in p["employers"]:
            L.append("\t".join(["LAST", "P108", qid] + ref(src)))
    return L


def payload(p: dict, day: str) -> dict:
    """One person as a `wbeditentity` payload, each statement carrying its source."""
    def ref(url):
        return [{"snaks": {"P854": [{"snaktype": "value", "property": "P854",
                                     "datavalue": {"value": url, "type": "string"}}],
                           "P813": [{"snaktype": "value", "property": "P813",
                                     "datavalue": {"value": {
                                         "time": "+%sT00:00:00Z" % day, "timezone": 0,
                                         "before": 0, "after": 0, "precision": 11,
                                         "calendarmodel": CAL}, "type": "time"}}]}}]

    def claim(pid, dv, dtype, url):
        return {"mainsnak": {"snaktype": "value", "property": pid,
                             "datavalue": {"value": dv, "type": dtype}},
                "type": "statement", "rank": "normal", "references": ref(url)}

    who = "https://orcid.org/" + p["orcid"]
    claims = [claim("P31", {"entity-type": "item", "id": HUMAN}, "wikibase-entityid", who),
              claim("P106", {"entity-type": "item", "id": RESEARCHER},
                    "wikibase-entityid", p["works"]),
              claim("P496", p["orcid"], "string", who)]
    claims += [claim("P108", {"entity-type": "item", "id": qid}, "wikibase-entityid", src)
               for _, qid, src in p["employers"]]
    return {"labels": {"en": {"language": "en", "value": p["label"]}},
            "descriptions": {"en": {"language": "en", "value": p["description"]}},
            "claims": claims}


def stale(p: dict, live: dict, day: str) -> dict:
    """A `wbeditentity` payload bringing one created item in line with the rules, or {}.

    Both directions, because a rule that improves also retracts. Three things have to hold
    before an employer statement is removed. The reference on it names this person's own
    ORCID, since somebody else's statement is not ours to touch. Both records answered, so
    a source that went quiet is not read as the person having left. And every institution
    the records name resolved to an item, because the statement is named by an item where
    the records name a string -- one name this run could not resolve is a run that cannot
    tell a retracted employer from an unresolved one.
    """
    data: dict = {}
    have = {}
    for c in (live.get("claims") or {}).get("P108") or []:
        v = (c["mainsnak"].get("datavalue") or {}).get("value") or {}
        urls = [s["datavalue"]["value"] for r in c.get("references") or []
                for s in r.get("snaks", {}).get("P854") or []]
        have[v.get("id")] = (c["id"], urls)
    if p["label"] != (live.get("labels", {}).get("en") or {}).get("value"):
        data["labels"] = {"en": {"language": "en", "value": p["label"]}}
    if p["description"] != (live.get("descriptions", {}).get("en") or {}).get("value"):
        data["descriptions"] = {"en": {"language": "en", "value": p["description"]}}
    want = {q: src for _, q, src in p["employers"]}
    claims = [c for c in payload(p, day)["claims"]
              if c["mainsnak"]["property"] == "P108"
              and c["mainsnak"]["datavalue"]["value"]["id"] not in have]
    claims += [{"id": guid, "remove": ""} for q, (guid, urls) in have.items()
               if q not in want and not p["partial"] and not p["unnamed"]
               and any(p["orcid"] in u for u in urls)]
    if claims:
        data["claims"] = claims
    return data


def write_page(people: list[dict], held: list[dict], skipped: list[dict],
               decisions: list[dict], papers: dict[str, int], qs_path: str | None,
               later: list[dict] | None = None) -> str:
    L = ["# Wikidata items for the co-authors", "",
         fill("Generated by `python scripts/wikidata_people.py`. A co-author with an ORCID "
              "and no Wikidata item cannot be an `author` statement on the papers you "
              "share, so each one below gets an item."), ""]
    if people:
        L += [fill("`--apply` creates them, and the ledger it writes lets the next "
                   "co-author run resolve each ORCID to its new item hours before the "
                   "query service reports it."
                   + (" [`%s`](%s) is the same batch for QuickStatements."
                      % (os.path.basename(qs_path), os.path.basename(qs_path))
                      if qs_path else "")), "",
              fill("Every value comes from a public record about that person. The name and "
                   "the employer are what they say on ORCID, and *publishes* is the page "
                   "that supports calling them a researcher -- ORCID where their work list "
                   "is public, OpenAlex where it is not. Anyone neither record names is "
                   "left out rather than guessed at."), "",
              "| name | ORCID | described as | employer | publishes | papers with you |",
              "| --- | --- | --- | --- | --- | --- |"]
        for p in sorted(people, key=lambda x: -papers.get(x["orcid"], 0)):
            emp = ", ".join(f"[{n}](https://www.wikidata.org/wiki/{q})"
                            for n, q, _ in p["employers"]) or "—"
            src = "ORCID" if p["works"].startswith("https://orcid.org/") else "OpenAlex"
            L.append(f"| {p['label']} | [{p['orcid']}](https://orcid.org/{p['orcid']}) "
                     f"| {p['description']} | {emp} | [{src}]({p['works']}) "
                     f"| {papers.get(p['orcid'], 0)} |")
    else:
        L += [fill("Every one of them has an item already. What is left is below, where a "
                   "name Wikidata already carries needs an answer no record settles.")]
    L.append("")
    if held:
        L += [f"## Already have a same-name item ({len(held)})", "",
              fill("Wikidata has a human item under each of these names. Where it states "
                   "no ORCID it is often this same person, reached from a paper rather "
                   "than from a profile -- so the right edit is to put the ORCID on that "
                   "item, and creating a second one would split a person in two. Where the "
                   "name has many bearers, nothing here settles which is which."), ""]
        for p in sorted(held, key=lambda x: -papers.get(x["orcid"], 0)):
            near = [n for n in p["namesakes"] if not n["orcid"]]
            L.append(f"- **{p['label']}** "
                     f"([{p['orcid']}](https://orcid.org/{p['orcid']}), "
                     f"{papers.get(p['orcid'], 0)} papers with you) — "
                     f"{len(p['namesakes'])} item(s) carry the name, "
                     f"{len(near)} of them stating no ORCID")
            L.append(f"  - that ORCID record states {p.get('record_says') or 'nothing'}")
            for n in p["namesakes"][:8]:
                L.append(f"  - [{n['qid']}](https://www.wikidata.org/wiki/{n['qid']}) — "
                         f"{n['says']}")
            if len(p["namesakes"]) > 8:
                L.append(f"  - … {len(p['namesakes']) - 8} more")
        L.append("")
    if decisions:
        L += [f"## Answered from the records ({len(decisions)})", "",
              fill("A paper, or an institution both records name, means the same-name item "
                   "is this person, so the ORCID goes on it -- `--apply` adds it. The other "
                   "direction is never concluded here: a second item for somebody who "
                   "already has one takes an administrator to merge, and a stated occupation "
                   "is not enough to risk it."), ""]
        for d in sorted(decisions, key=lambda x: -papers.get(x["orcid"], 0)):
            v = d["verdict"]
            L.append(f"- **{d['label']}** — "
                     f"[{v['qid']}](https://www.wikidata.org/wiki/{v['qid']}), "
                     f"because {v['why']}")
        L.append("")
    if skipped:
        L += [f"## Left out ({len(skipped)})", "",
              fill("Not enough on the public record to describe a person, so an item would "
                   "be an identifier and nothing else."), ""]
        for p in sorted(skipped, key=lambda x: x["orcid"]):
            L.append(f"- [{p['orcid']}](https://orcid.org/{p['orcid']}) — {p['skip']}")
        L.append("")
    if later:
        L += [f"## Not asked yet ({len(later)})", "",
              fill("One of the two records did not answer this run, and these are the "
                   "outcomes that rest on a record being silent. Nothing is concluded "
                   "about them and nothing is cached, so the next run asks again."), ""]
        for p in sorted(later, key=lambda x: x["orcid"]):
            L.append(f"- [{p['orcid']}](https://orcid.org/{p['orcid']}) — would be "
                     f"*{p['later']}*, on a record that answered")
        L.append("")
    page = os.path.join(TASKS, "wikidata_people.md")
    write_task(page, "\n".join(L).rstrip() + "\n")
    return page


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--apply", action="store_true",
                    help="create the items through the API rather than only describing them")
    ap.add_argument("--limit", type=int, help="create at most this many, for a first look")
    ap.add_argument("--refresh", action="store_true",
                    help="re-ask ORCID rather than reading the cache")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    try:
        papers = wanted()
    except (OSError, ValueError):
        print("run scripts/wikidata_coauthors.py first -- its cache is what names the "
              "ORCIDs to look up")
        return 1
    recs = records(sorted(papers), args.refresh)
    # Asked live rather than trusted from the cache, so a person who got an item since the
    # last pass is not created twice.
    claimed = items_by_orcid(sorted(papers))
    todo = [o for o in sorted(papers) if not claimed.get(o)]
    employers = employer_items(sorted({e for o in todo for e in
                                       recs[o]["employers"] + (recs[o].get("openalex_employers") or [])}))
    made = [described(o, recs[o], employers) for o in todo]
    ok = [p for p in made if not ("skip" in p or "later" in p)]
    taken = namesakes(sorted({p["label"] for p in ok}))
    for p in ok:
        p["namesakes"] = keeps(p, taken.get(p["label"]) or [])
    facts = about(sorted({n["qid"] for p in ok for n in p["namesakes"]}))
    for p in ok:
        for n in p["namesakes"]:
            n.update(facts.get(n["qid"]) or {"works": [], "research": True})
            # Written into the state so the worklist prints the same line as the task page.
            n["says"] = summary(n)
        # The likely answer first: an item stating an occupation nothing like research is
        # still shown, because the tree that says so has holes.
        p["namesakes"].sort(key=lambda n: (not n["research"], n["qid"]))
    answered = decided()
    mine = coauthored()
    # A hold the records themselves settle is not a question. Answered here rather than
    # asked, and only where an answer given by hand has not already said otherwise.
    for p in ok:
        v = verdict(p, mine.get(p["orcid"]) or set()) if p["namesakes"] else {}
        if v and not answered.get(p["orcid"]):
            p["verdict"] = v
            answered[p["orcid"]] = v["qid"]
    try:
        people, link, held = sorted_out(ok, answered)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1
    skipped = [p for p in made if "skip" in p]
    later = [p for p in made if "later" in p]
    for p in ok:
        p["papers"] = papers.get(p["orcid"], 0)
    quiet = _refused or wdqs_quiet()
    if quiet:
        # Every list here rests on a Wikidata read. A refusal reads as no item stating this
        # ORCID and no item under this name, which is the exact state this pass creates an
        # item for -- and a second item for somebody who already has one can only be undone
        # by an administrator.
        print("wikidata did not answer (%s), so nothing is written and nothing is created"
              % quiet, file=sys.stderr)
        return 1
    day = datetime.date.today().isoformat()
    lines = batch(people, day)
    qs = os.path.join(TASKS, "wikidata_people.qs")
    if lines:
        with open(qs, "w") as f:
            f.write("\n".join(lines) + "\n")
    elif os.path.exists(qs):
        os.remove(qs)
    decisions = [p for p in ok if p.get("verdict")]
    page = write_page(people, held, skipped, decisions, papers, qs if lines else None,
                      later)
    write_json(
        os.path.join(BUILD, "wikidata_people.json"),
        {"asked": day, "create": len(people), "held": len(held),
         "skipped": len(skipped), "later": len(later), "decided": len(decisions),
         "mentions": sum(papers[p["orcid"]] for p in people),
         "people": people, "held_people": held,
         "decisions": [{"label": p["label"], "orcid": p["orcid"], "papers": p["papers"],
                        "verdict": p["verdict"]} for p in decisions]},
        indent=1, sort_keys=True)
    if not args.quiet:
        print("%d co-author ORCIDs with no item: %d to create, %d already have a "
              "same-name item, %d left out%s"
              % (len(todo), len(people), len(held), len(skipped),
                 ", %d not asked (a source did not answer)" % len(later) if later else ""))
        for p in sorted(ok, key=lambda x: x["label"]):
            if p.get("verdict"):
                print("  %s is %s — %s"
                      % (p["label"], p["verdict"]["qid"], p["verdict"]["why"]))
        print("wrote %s%s" % (page, " and " + qs if lines else ""))
    if not args.apply:
        return 0
    s = logged_in()
    print("acting as %s" % s.user)
    made, wanted_n = 0, 0
    if people:
        make = people[:args.limit] if args.limit else people
        wanted_n = len(make)
        made = create_items(
            s, [(p["orcid"], p["label"], payload(p, day)) for p in make],
            os.path.join(DATA, LEDGER),
            "create item for a co-author, from their ORCID record", LEDGER_NOTE)
        print("%d/%d created" % (made, wanted_n))
    if link:
        print("adding the ORCID to %d same-name item(s)" % len(link))
        add_orcids(s, link, day)
    fixed, off = resync(s, day)
    if off:
        print("%d/%d already-created items brought up to date" % (fixed, off))
    return 0 if made == wanted_n and fixed == off else 1


def add_orcids(s, link: list[tuple[dict, str]], day: str) -> int:
    """Add each person's ORCID to the item said to be theirs.

    Recorded in the same ledger as a creation, which means the same thing either way: this
    ORCID now resolves to this item, hours before the query service says so.
    """
    path = os.path.join(DATA, LEDGER)
    d = read_yaml(path) or {}
    ok = 0
    for p, qid in link:
        # The summary is the only trace an edit leaves for whoever reviews it, so it names
        # the record that settled it where one did, and the override file otherwise.
        why = ("add ORCID, %s (paper-geo)" % p["verdict"]["why"] if p.get("verdict")
               else "add ORCID from data/overrides.yaml (paper-geo)")
        try:
            s.edit("wbeditentity", id=qid, data=json.dumps(linked(p, day)),
                   summary=why)
            d.setdefault("items", {})[p["orcid"]] = qid
            d.setdefault("labels", {})[qid] = p["label"]
            write_yaml(path, d)
            ok += 1
            print("  %s — %s" % (qid, p["label"]))
        except (RuntimeError, urllib.error.URLError) as e:
            print("  FAILED %s — %s\n     %s" % (qid, p["label"], e))
        time.sleep(1.5)
    return ok


def resync(s, day: str) -> tuple[int, int]:
    """Bring the items this repo already created in line with the current rules.

    The rules keep improving -- a name read as shouting, an employer OpenAlex was unsure
    about -- and an item created under an older reading would otherwise stay wrong. Every
    change is derived the same way a creation is, so this needs no separate decision.
    """
    led = read_yaml(os.path.join(DATA, LEDGER)) or {}
    mine = led.get("items") or {}
    if not mine:
        return 0, 0
    recs = records(sorted(mine), False)
    employers = employer_items(sorted({e for r in recs.values() for e in
                                       r["employers"] + (r.get("openalex_employers") or [])}))
    ids = sorted(set(mine.values()))
    live = {}
    for i in range(0, len(ids), 50):
        d = asked(WIKI + "?action=wbgetentities&format=json&languages=en"
                  "&props=labels|descriptions|claims&ids=" + "|".join(ids[i:i + 50]))
        live.update(d.get("entities") or {})
    # Read again here rather than trusting `main`'s check, because these three reads are
    # this function's own. `stale` retracts an employer statement that is not in the
    # employers it was given, and a query service that went quiet gives it none of them.
    quiet = _refused or wdqs_quiet()
    if quiet:
        print("  wikidata did not answer (%s), so nothing is edited" % quiet)
        return 0, 0
    todo = []
    for orcid, qid in sorted(mine.items()):
        p = described(orcid, recs[orcid], employers)
        # `later` as well as `skip`: a record built on a source that did not answer would
        # correct a description, and retract an employer, from half the evidence.
        if "skip" in p or "later" in p or qid not in live:
            continue
        data = stale(p, live[qid], day)
        if data:
            todo.append((qid, p["label"], data))
    ok = 0
    for i, (qid, label, data) in enumerate(todo, 1):
        try:
            s.edit("wbeditentity", id=qid, data=json.dumps(data),
                   summary="update from the ORCID and OpenAlex records (paper-geo)")
            ok += 1
            print("  %d/%d %s — %s %s" % (i, len(todo), qid, label, sorted(data)))
        except (RuntimeError, urllib.error.URLError) as e:
            print("  %d/%d FAILED — %s %s\n     %s" % (i, len(todo), qid, label, e))
        time.sleep(1.5)
    return ok, len(todo)


if __name__ == "__main__":
    raise SystemExit(main())
