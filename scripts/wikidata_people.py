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
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import BUILD, DATA, TASKS, get, get_json
from wikidata_coauthors import CACHE, fill, items_by_orcid, qid_of, sparql  # noqa: F401
from wikidata_apply import CAL, create_items, logged_in, recorded  # noqa: F401
from wikidata_orgs import labels_of

WIKI = "https://www.wikidata.org/w/api.php"
LEDGER = "wikidata_people_created.yaml"
LEDGER_NOTE = (
    "People `scripts/wikidata_people.py --apply` created, ORCID -> QID. A receipt, not a "
    "decision. Wikidata's query service lags hours behind an edit, so for those hours this "
    "file is the only thing that knows the item exists -- without it a second run creates "
    "the person twice, and a duplicate human item is the one mistake here somebody else "
    "has to clean up. Never edit by hand.")
CACHE_PEOPLE = "orcid_records.json"
CACHE_DAYS = 30
# Bump to re-ask when `record` starts reading a different field.
SHAPE = 1
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
    """
    t = get("https://pub.orcid.org/v3.0/%s/record" % orcid, accept="application/json")
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
    oa = get_json("https://api.openalex.org/authors/https://orcid.org/" + orcid) or {}
    return {"label": val("credit-name") or " ".join(
                x for x in (val("given-names"), val("family-name")) if x).strip(),
            "openalex_label": oa.get("display_name") or "",
            "employers": sorted({o for o in now if o}),
            "works": len(((acts.get("works") or {}).get("group") or [])),
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
    for orcid in orcids:
        if orcid not in got:
            got[orcid] = record(orcid)
    with open(path, "w") as f:
        json.dump(cache, f, indent=1, sort_keys=True)
    return got


def employer_items(names: list[str]) -> dict[str, str]:
    """Organisation name to the single organisation item carrying it as a label or alias.


    An institution is not a person, so an exact match is safe here in a way it never is
    for a co-author. A name two items carry is dropped, as is one no item carries -- the
    employer then goes unstated rather than guessed at.
    """
    # ORCID records often write "The Hebrew University of Jerusalem" where Wikidata drops
    # the article, so both forms are asked and the answers pooled.
    forms = {n: {n} | ({n[4:]} if n.startswith("The ") else set()) for n in names}
    every = sorted({f for fs in forms.values() for f in fs})
    hits: dict[str, set[str]] = {}
    for i in range(0, len(every), 100):
        vals = " ".join('"%s"@en' % f.replace('"', '\\"') for f in every[i:i + 100])
        for r in sparql("SELECT ?n ?i WHERE { VALUES ?n {%s} "
                        "{ ?i rdfs:label ?n } UNION { ?i skos:altLabel ?n } "
                        "?i wdt:P31/wdt:P279* wd:Q43229 }" % vals):
            hits.setdefault(r["n"]["value"], set()).add(qid_of(r["i"]["value"]))
    got = {n: {q for f in fs for q in hits.get(f, ())} for n, fs in forms.items()}
    one = {n: next(iter(q)) for n, q in got.items() if len(q) == 1}
    # Wikidata's own label rather than ORCID's wording, so the description reads the way
    # the rest of Wikidata does.
    live = labels_of(sorted(set(one.values())))
    return {n: {"qid": q, "label": live.get(q) or n} for n, q in one.items()}


def cased(rec: dict) -> str:
    """The person's name in the form to label an item with.

    ORCID stores whatever the person typed, so "mohit bansal" and "YANGSIBO HUANG" both
    occur. OpenAlex normalises the same name from publisher metadata, so it answers for
    those; a name ORCID already cases like a name is left exactly as given, since no rule
    handles "van der Maaten" and "McDonald" at once.
    """
    orcid_name = " ".join((rec.get("label") or "").split())
    raw = orcid_name and (orcid_name == orcid_name.lower()
                          or orcid_name == orcid_name.upper())
    return (" ".join((rec.get("openalex_label") or "").split()) if raw
            else orcid_name) or " ".join((rec.get("openalex_label") or "").split())


def namesakes(labels: list[str]) -> dict[str, list[dict]]:
    """Name to every human item carrying it, with the ORCID and description each states.

    Asked of the search index rather than the query service, for two reasons the query
    service cannot cover: it matches every language and every alias, so an item labelled
    only in German still answers, and it is live, where the query service lags hours behind
    a creation.

    Reports rather than decides -- `keeps` reads the answer.
    """
    found: dict[str, set[str]] = {}
    for n in labels:
        d = json.loads(get(WIKI + "?action=wbsearchentities&type=item&language=en"
                           "&uselang=en&limit=20&format=json&search="
                           + urllib.parse.quote(n)) or "{}")
        for h in d.get("search") or []:
            for form in (h.get("label"), h.get("match", {}).get("text"),
                         h.get("aliases", [None])[0]):
                if form and form.strip().lower() == n.lower():
                    found.setdefault(n, set()).add(h["id"])
                    break
    qids = sorted({q for qs in found.values() for q in qs})
    seen: dict[str, dict] = {}
    for i in range(0, len(qids), 50):
        d = json.loads(get(WIKI + "?action=wbgetentities&props=claims|descriptions"
                           "&languages=en&format=json&ids=" + "|".join(qids[i:i + 50])) or "{}")
        for q, e in (d.get("entities") or {}).items():
            cl = e.get("claims") or {}
            if not any((c["mainsnak"].get("datavalue") or {}).get("value", {}).get("id") == HUMAN
                       for c in cl.get("P31") or []):
                continue
            orcid = ""
            for c in cl.get("P496") or []:
                orcid = (c["mainsnak"].get("datavalue") or {}).get("value") or ""
            seen[q] = {"qid": q, "orcid": orcid,
                       "description": (e.get("descriptions", {}).get("en") or {}).get("value", "")}
    return {n: [seen[q] for q in sorted(qs) if q in seen]
            for n, qs in found.items() if any(q in seen for q in qs)}


def keeps(p: dict, same: list[dict]) -> list[dict]:
    """The same-name items that stop this person being created, or nothing.

    Two reasons to stop, and the second is Wikidata's own rule rather than a judgement:

    An item stating no ORCID is very often this person reached from a source that gave no
    identifier, and a second item for somebody who already has one is the mistake here only
    an administrator can undo. An item stating an ORCID states a different one -- ours
    matched nothing on the way in -- so that one is somebody else.

    Wikidata refuses a label and description pair that already exists, so an item sharing
    both is held whatever it states. Two same-name researchers with no distinguishing
    employer between them cannot both be described as "researcher", and choosing which
    detail separates them is not a call to make from a name.
    """
    return [s for s in same
            if not s["orcid"] or s["description"] == p["description"]]


def described(orcid: str, rec: dict, employers: dict[str, dict]) -> dict:
    """One person's item, or the reason the public records do not describe a person.

    `works` names the page that shows they publish, which is what `occupation` rests on.
    """
    label = cased(rec)
    if not label:
        return {"orcid": orcid, "skip": "neither ORCID nor OpenAlex gives a name"}
    if rec.get("works"):
        works = "https://orcid.org/" + orcid
    elif rec.get("openalex_works"):
        works = "https://openalex.org/authors/https://orcid.org/" + orcid
    else:
        return {"orcid": orcid, "skip": "no works on either record"}
    at = [employers[e] for e in rec["employers"] if e in employers]
    return {"orcid": orcid, "label": label, "works": works,
            "description": "researcher at " + at[0]["label"] if at else "researcher",
            "employers": [(e["label"], e["qid"]) for e in at]}


def batch(people: list[dict], day: str) -> list[str]:
    """QuickStatements lines: one CREATE per person, sourced to their ORCID record."""
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
        for _, qid in p["employers"]:
            L.append("\t".join(["LAST", "P108", qid] + ref(who)))
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
    claims += [claim("P108", {"entity-type": "item", "id": qid}, "wikibase-entityid", who)
               for _, qid in p["employers"]]
    return {"labels": {"en": {"language": "en", "value": p["label"]}},
            "descriptions": {"en": {"language": "en", "value": p["description"]}},
            "claims": claims}


def write_page(people: list[dict], held: list[dict], skipped: list[dict],
               papers: dict[str, int], qs_path: str) -> str:
    L = ["# Wikidata items for the co-authors", "",
         fill("Generated by `python scripts/wikidata_people.py`. Each person below has an "
              "ORCID and no Wikidata item, which is why their name cannot be turned into "
              "an `author` statement on the papers you share."), "",
         fill("Paste [`%s`](%s) into [QuickStatements]"
              "(https://quickstatements.toolforge.org/#/batch). Creating an item goes out "
              "under your name, so this is the one step that is yours. Nothing else is "
              "needed afterwards -- the next run finds the new items by ORCID and writes "
              "the `author` statements itself."
              % (os.path.basename(qs_path), os.path.basename(qs_path))), "",
         fill("Every value comes from a public record about that person. The name and the "
              "employer are what they say on ORCID, and *publishes* is the page that "
              "supports calling them a researcher -- ORCID where their work list is "
              "public, OpenAlex where it is not. Anyone neither record names is left out "
              "rather than guessed at."), "",
         "| name | ORCID | described as | employer | publishes | papers with you |",
         "| --- | --- | --- | --- | --- | --- |"]
    for p in sorted(people, key=lambda x: -papers.get(x["orcid"], 0)):
        emp = ", ".join(f"[{n}](https://www.wikidata.org/wiki/{q})"
                        for n, q in p["employers"]) or "—"
        src = "ORCID" if p["works"].startswith("https://orcid.org/") else "OpenAlex"
        L.append(f"| {p['label']} | [{p['orcid']}](https://orcid.org/{p['orcid']}) "
                 f"| {p['description']} | {emp} | [{src}]({p['works']}) "
                 f"| {papers.get(p['orcid'], 0)} |")
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
                     f"{len(near)} of them stating no ORCID: "
                     + ", ".join(f"[{n['qid']}](https://www.wikidata.org/wiki/{n['qid']})"
                                 for n in p["namesakes"][:8])
                     + (" …" if len(p["namesakes"]) > 8 else ""))
        L.append("")
    if skipped:
        L += [f"## Left out ({len(skipped)})", "",
              fill("Not enough on the public record to describe a person, so an item would "
                   "be an identifier and nothing else."), ""]
        for p in sorted(skipped, key=lambda x: x["orcid"]):
            L.append(f"- [{p['orcid']}](https://orcid.org/{p['orcid']}) — {p['skip']}")
        L.append("")
    page = os.path.join(TASKS, "wikidata_people.md")
    with open(page, "w") as f:
        f.write("\n".join(L).rstrip() + "\n")
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
    employers = employer_items(sorted({e for o in todo for e in recs[o]["employers"]}))
    made = [described(o, recs[o], employers) for o in todo]
    ok = [p for p in made if "skip" not in p]
    taken = namesakes(sorted({p["label"] for p in ok}))
    for p in ok:
        p["namesakes"] = keeps(p, taken.get(p["label"]) or [])
    people = [p for p in ok if not p["namesakes"]]
    held = [p for p in ok if p["namesakes"]]
    skipped = [p for p in made if "skip" in p]
    day = datetime.date.today().isoformat()
    lines = batch(people, day)
    qs = os.path.join(TASKS, "wikidata_people.qs")
    if lines:
        with open(qs, "w") as f:
            f.write("\n".join(lines) + "\n")
    elif os.path.exists(qs):
        os.remove(qs)
    page = write_page(people, held, skipped, papers, qs)
    with open(os.path.join(BUILD, "wikidata_people.json"), "w") as f:
        json.dump({"asked": day, "create": len(people), "held": len(held),
                   "skipped": len(skipped),
                   "mentions": sum(papers[p["orcid"]] for p in people),
                   "people": people, "held_people": held}, f, indent=1, sort_keys=True)
    if not args.quiet:
        print("%d co-author ORCIDs with no item: %d to create, %d already have a "
              "same-name item, %d left out"
              % (len(todo), len(people), len(held), len(skipped)))
        print("wrote %s%s" % (page, " and " + qs if lines else ""))
    if not args.apply:
        return 0
    if not people:
        print("nothing to create")
        return 0
    make = people[:args.limit] if args.limit else people
    s = logged_in()
    print("creating %d as %s" % (len(make), s.user))
    made = create_items(
        s, [(p["orcid"], p["label"], payload(p, day)) for p in make],
        os.path.join(DATA, LEDGER),
        "create item for a co-author, from their ORCID record", LEDGER_NOTE)
    print("%d/%d created" % (made, len(make)))
    return 0 if made == len(make) else 1


if __name__ == "__main__":
    raise SystemExit(main())
