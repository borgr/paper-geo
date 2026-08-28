"""Create Wikidata items for the co-authors who have an ORCID and no item.

97 of the 156 co-author ORCIDs in the corpus belong to nobody Wikidata has an item for,
and that absence is what leaves most name mentions unresolvable. `wikidata_coauthors.py`
states `author` by matching an ORCID against the item that claims it, so a match needs an
item on the other side.

    python scripts/wikidata_people.py

Each item is built from the person's own ORCID record -- the name they publish under, the
organisation they say employs them now, the works they list. Nothing is taken from a name
match, so a namesake cannot end up in the batch.

Writes a QuickStatements batch to paste and nothing else. Once pasted, the next
`wikidata_coauthors.py` run finds the new items by ORCID and the `author` statements
follow without another decision.
"""

import argparse
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import BUILD, TASKS, get, get_json
from wikidata_coauthors import CACHE, fill, items_by_orcid, qid_of, sparql
from wikidata_orgs import labels_of

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
    claimed = cache.get("by_orcid") or {}
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


def described(orcid: str, rec: dict, employers: dict[str, dict]) -> dict:
    """One person's item, or the reason the public records do not describe a person.

    `works` names the page that shows they publish, which is what `occupation` rests on.
    """
    label = rec.get("label") or rec.get("openalex_label")
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


def write_page(people: list[dict], skipped: list[dict], papers: dict[str, int],
               qs_path: str) -> str:
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
    people = [p for p in made if "skip" not in p]
    skipped = [p for p in made if "skip" in p]
    day = datetime.date.today().isoformat()
    lines = batch(people, day)
    qs = os.path.join(TASKS, "wikidata_people.qs")
    if lines:
        with open(qs, "w") as f:
            f.write("\n".join(lines) + "\n")
    elif os.path.exists(qs):
        os.remove(qs)
    page = write_page(people, skipped, papers, qs)
    with open(os.path.join(BUILD, "wikidata_people.json"), "w") as f:
        json.dump({"asked": day, "create": len(people), "skipped": len(skipped),
                   "mentions": sum(papers[p["orcid"]] for p in people),
                   "people": people}, f, indent=1, sort_keys=True)
    if not args.quiet:
        print("%d co-author ORCIDs with no item: %d to create, %d left out"
              % (len(todo), len(people), len(skipped)))
        print("wrote %s%s" % (page, " and " + qs if lines else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
