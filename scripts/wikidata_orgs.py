#!/usr/bin/env python3
"""Build the Wikidata items for the collectives this work belongs to.

Several projects in the corpus are run by groups Wikidata has no item for, so the papers
cannot say what they are part of and the groups cannot say what they produced. The groups
themselves are describable from public pages -- a website, a GitHub organisation, an ACL
Anthology venue with three proceedings volumes -- which is what Wikidata notability asks
for.

`data/wikidata_orgs.yaml` describes each item and cites a URL for every statement. This
reads it, checks Wikidata for what is already there, and writes a QuickStatements batch.

    python scripts/wikidata_orgs.py

Two passes over the same file, and which one runs is decided per item by whether Wikidata
already has it.

  create   no item carries the label or an alias, so the batch is a CREATE followed by
           the labelled statements and their references.
  connect  the item exists, so the batch is the edges into it from items that already
           exist -- `main subject` on each corpus paper about it, `organizer` on each
           event it ran. QuickStatements cannot use a just-created item as a value, so
           these wait for the second run and are skipped once present.

Every QID in the file is read back live and its label compared against the `note` beside
it, so a mistyped value is a failure here rather than a wrong statement on Wikidata.

    python scripts/wikidata_orgs.py --apply

does the same through the API instead, and records what it made in
`data/wikidata_orgs_created.yaml`.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
import time
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import BUILD, DATA, TASKS, read_yaml, write_yaml  # noqa: E402
from wikidata_coauthors import fill, qid_of, sparql  # noqa: E402
from wikidata_apply import CAL, create_items, logged_in  # noqa: E402

ORGS = "wikidata_orgs.yaml"
LEDGER = "wikidata_orgs_created.yaml"
LEDGER_NOTE = (
    "Groups `scripts/wikidata_orgs.py --apply` created, slug -> QID. A receipt, not a "
    "decision. Wikidata's query service lags hours behind an edit, so until it catches up "
    "this file is the only thing that knows the item exists. Never edit by hand.")
# Reference URL and the date it was read, stated on every generated statement.
REF_URL = "S854"
REF_DATE = "S813"


def described(path: str) -> dict:
    """The `items` mapping in the description file, keyed by slug."""
    return (read_yaml(path) or {}).get("items") or {}


def value_qids(items: dict) -> list[str]:
    """Every QID the file names as a statement value, a qualifier value, or an edge subject."""
    out = set()
    for it in items.values():
        for s in it.get("statements") or []:
            out |= {str(x["v"]) for x in [s] + (s.get("q") or [])
                    if str(x["v"]).startswith("Q")}
        out |= {e["qid"] for e in it.get("organizer_of") or []}
    return sorted(out)


def labels_of(qids: list[str]) -> dict[str, str]:
    """QID to its live English label, for the QIDs that have one."""
    out = {}
    for i in range(0, len(qids), 200):
        vals = " ".join("wd:" + q for q in qids[i:i + 200])
        for r in sparql("SELECT ?i ?l WHERE { VALUES ?i {%s} "
                        "?i rdfs:label ?l FILTER(LANG(?l) = 'en') }" % vals):
            out[qid_of(r["i"]["value"])] = r["l"]["value"]
    return out


def mistyped(items: dict, live: dict[str, str]) -> list[str]:
    """Statements and qualifiers whose `note` does not match the live label of their QID."""
    bad = []
    for slug, it in sorted(items.items()):
        for s in it.get("statements") or []:
            for x in [s] + (s.get("q") or []):
                v, note = str(x["v"]), x.get("note")
                if v.startswith("Q") and note and live.get(v, "").lower() != note.lower():
                    bad.append(f"{slug} {x['p']} {v} says {note!r}, "
                               f"Wikidata says {live.get(v) or 'nothing'!r}")
    return bad


def found(items: dict) -> dict[str, list[str]]:
    """Slug to the items whose label or alias is exactly one of its names.

    An exact match is the test rather than a search, so a group with a similarly named
    workshop item is not mistaken for the group.
    """
    names = {slug: [it["label"]] + list(it.get("aliases") or [])
             for slug, it in items.items()}
    every = sorted({n for ns in names.values() for n in ns})
    hits: dict[str, set[str]] = {}
    for i in range(0, len(every), 100):
        vals = " ".join('"%s"@en' % n.replace('"', '\\"') for n in every[i:i + 100])
        for r in sparql("SELECT ?n ?i WHERE { VALUES ?n {%s} "
                        "{ ?i rdfs:label ?n } UNION { ?i skos:altLabel ?n } }" % vals):
            hits.setdefault(r["n"]["value"], set()).add(qid_of(r["i"]["value"]))
    return {slug: sorted({q for n in ns for q in hits.get(n, ())})
            for slug, ns in names.items()}


def edges_present(pairs: list[tuple[str, str, str]]) -> set[tuple[str, str, str]]:
    """The (subject, property, object) triples that Wikidata already states."""
    if not pairs:
        return set()
    # Each property is asked on its own, since one `VALUES` block cannot bind a property
    # path.
    got = set()
    for prop in sorted({p for _, p, _ in pairs}):
        subj = sorted({s for s, p, _ in pairs if p == prop})
        for i in range(0, len(subj), 200):
            vals = " ".join("wd:" + s for s in subj[i:i + 200])
            for r in sparql("SELECT ?s ?o WHERE { VALUES ?s {%s} ?s wdt:%s ?o }"
                            % (vals, prop)):
                got.add((qid_of(r["s"]["value"]), prop, qid_of(r["o"]["value"])))
    return got & set(pairs)


def edges_for(it: dict, qid: str, ledger: dict) -> list[tuple[str, str, str]]:
    """The inbound edges this item should carry, as (subject, property, object).

    `qid` is empty until the item exists, which leaves the object empty and the edge
    waiting rather than dropping it from the page.
    """
    out = [(e["qid"], "P664", qid) for e in it.get("organizer_of") or []]
    out += [(ledger[s], "P921", qid) for s in it.get("subject_of") or [] if s in ledger]
    return out


def edge_names(it: dict, ledger: dict) -> dict[str, str]:
    """Subject QID to what it is, so an edge reads as more than two identifiers."""
    out = {e["qid"]: e.get("note") or e["qid"] for e in it.get("organizer_of") or []}
    return out | {ledger[s]: s for s in it.get("subject_of") or [] if s in ledger}


def ref(url: str, day: str) -> list[str]:
    return [REF_URL, '"%s"' % url, REF_DATE, "+%sT00:00:00Z/11" % day]


def snak(pid: str, v: str) -> dict:
    """One `wbeditentity` snak from the three value forms `data/wikidata_orgs.yaml` uses.

    A QID, a quoted string, or a date with the precision after a slash the way
    QuickStatements writes it.
    """
    v = str(v)
    if v.startswith("Q"):
        dv = {"value": {"entity-type": "item", "id": v}, "type": "wikibase-entityid"}
    elif v.startswith("+"):
        stamp, _, prec = v.partition("/")
        dv = {"value": {"time": stamp, "timezone": 0, "before": 0, "after": 0,
                        "precision": int(prec or 11), "calendarmodel": CAL},
              "type": "time"}
    else:
        dv = {"value": v.strip('"'), "type": "string"}
    return {"snaktype": "value", "property": pid, "datavalue": dv}


def item_payload(it: dict, day: str) -> dict:
    """One described group as a `wbeditentity` payload, statements sourced as written."""
    claims = []
    for s in it["statements"]:
        c = {"mainsnak": snak(s["p"], s["v"]), "type": "statement", "rank": "normal",
             "references": [{"snaks": {
                 "P854": [snak("P854", '"%s"' % s["ref"])],
                 "P813": [snak("P813", "+%sT00:00:00Z/11" % day)]}}]}
        quals = {}
        for x in s.get("q") or []:
            quals.setdefault(x["p"], []).append(snak(x["p"], x["v"]))
        if quals:
            c["qualifiers"] = quals
        claims.append(c)
    return {"labels": {"en": {"language": "en", "value": it["label"]}},
            "descriptions": {"en": {"language": "en", "value": it["description"]}},
            "aliases": {"en": [{"language": "en", "value": a}
                               for a in it.get("aliases") or []]},
            "claims": claims}


def batch(items: dict, state: dict, day: str) -> list[str]:
    """QuickStatements lines: a CREATE per absent item, an edge per missing connection."""
    L = []
    for slug, it in sorted(items.items()):
        st = state[slug]
        if not st["qid"]:
            L.append("CREATE")
            L.append("\t".join(["LAST", "Len", '"%s"' % it["label"]]))
            L.append("\t".join(["LAST", "Den", '"%s"' % it["description"]]))
            for a in it.get("aliases") or []:
                L.append("\t".join(["LAST", "Aen", '"%s"' % a]))
            for s in it["statements"]:
                quals = [c for x in s.get("q") or [] for c in (x["p"], str(x["v"]))]
                L.append("\t".join(["LAST", s["p"], str(s["v"])]
                                   + quals + ref(s["ref"], day)))
            continue
        for subj, prop, obj in st["missing"]:
            L.append("\t".join([subj, prop, obj]))
    return L


def state_of(items: dict, ledger: dict, receipts: dict | None = None) -> dict[str, dict]:
    """Per slug, the QID Wikidata already has, its ambiguity, and the edges still absent.

    `receipts` is `data/wikidata_orgs_created.yaml`, and everything it names counts as
    present. The query service lags hours behind an edit, so a second run that reads only
    Wikidata would create the group again and restate every edge.
    """
    hits = found(items)
    receipts = receipts or {}
    made = receipts.get("items") or {}
    out = {}
    for slug, it in items.items():
        qids = hits.get(slug) or made.get(slug) and [made[slug]] or []
        qid = qids[0] if len(qids) == 1 else ""
        edges = edges_for(it, qid, ledger)
        out[slug] = {"qid": qid, "ambiguous": qids if len(qids) > 1 else [],
                     "edges": edges, "missing": edges if qid else [],
                     "names": edge_names(it, ledger)}
    have = edges_present([e for st in out.values() for e in st["missing"]])
    have |= {tuple(e.split()) for e in receipts.get("edges") or []}
    for st in out.values():
        st["missing"] = [e for e in st["missing"] if e not in have]
    return out


def write_page(items: dict, state: dict, qs_path: str | None) -> str:
    L = ["# Wikidata items for the groups", "",
         fill("Generated by `python scripts/wikidata_orgs.py` from "
              "`data/wikidata_orgs.yaml`. Several projects in the corpus are run by groups "
              "Wikidata has no item for, so the papers cannot say what they are part of. "
              "Each statement below cites the public page it came from."), ""]
    if qs_path:
        L += [fill("Paste [`%s`](%s) into [QuickStatements]"
                   "(https://quickstatements.toolforge.org/#/batch). Creating an item goes "
                   "out under your name, so this is the one step that is yours."
                   % (os.path.basename(qs_path), os.path.basename(qs_path))), ""]
    for slug, it in sorted(items.items()):
        st = state[slug]
        where = (f"[{st['qid']}](https://www.wikidata.org/wiki/{st['qid']})" if st["qid"]
                 else "does not exist yet")
        L += [f"## {it['label']}", "", f"- {where}",
              f"- *{it['description']}*"]
        if st["ambiguous"]:
            L.append("- **more than one item carries this name** — resolve by hand: "
                     + ", ".join(f"[{q}](https://www.wikidata.org/wiki/{q})"
                                 for q in st["ambiguous"]))
        L.append("")
        if not st["qid"]:
            L += ["| property | value | source |", "| --- | --- | --- |"]
            for s in it["statements"]:
                v = s.get("note") or str(s["v"]).strip('"')
                for x in s.get("q") or []:
                    v += ", %s %s" % (x["p"], x.get("note") or x["v"])
                L.append(f"| {s['p']} | {v} | [{s['ref']}]({s['ref']}) |")
            L.append("")
        edges = st["missing"] if st["qid"] else st["edges"]
        if edges:
            L += [fill("These existing items point at it, in the batch on the run after "
                       "it has a QID -- QuickStatements cannot use an item it just created "
                       "as a value." if not st["qid"] else
                       "These existing items point at it, and are in the batch above."),
                  ""]
            for subj, prop, _ in edges:
                L.append(f"- [{st['names'].get(subj, subj)}]"
                         f"(https://www.wikidata.org/wiki/{subj}) → {prop}")
            L.append("")
        elif st["qid"] and st["edges"]:
            L += ["Every edge into it is already stated.", ""]
        for n in it.get("needs") or []:
            L.append(fill("- **needs a fact only you have** — " + " ".join(n.split())))
        if it.get("needs"):
            L.append("")
    page = os.path.join(TASKS, "wikidata_orgs.md")
    with open(page, "w") as f:
        f.write("\n".join(L).rstrip() + "\n")
    return page


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--apply", action="store_true",
                    help="create the absent items and add the missing edges through the API")
    args = ap.parse_args()
    items = described(os.path.join(DATA, ORGS))
    if not items:
        if not args.quiet:
            print("no groups described in data/%s" % ORGS)
        return 0

    ledger = ((read_yaml(os.path.join(DATA, "wikidata_created.yaml")) or {})
              .get("items") or {})
    live = labels_of(value_qids(items))
    bad = mistyped(items, live)
    bad += ["%s subject_of names %s, which no item was created for" % (slug, s)
            for slug, it in sorted(items.items())
            for s in it.get("subject_of") or [] if s not in ledger]
    if bad:
        print("data/%s does not check out:" % ORGS)
        for b in bad:
            print("  " + b)
        return 1

    state = state_of(items, ledger, read_yaml(os.path.join(DATA, LEDGER)) or {})
    day = datetime.date.today().isoformat()
    qs = batch(items, state, day)
    qs_path = os.path.join(TASKS, "wikidata_orgs.qs")
    if qs:
        with open(qs_path, "w") as f:
            f.write("\n".join(qs) + "\n")
    elif os.path.exists(qs_path):
        os.remove(qs_path)
    page = write_page(items, state, qs_path if qs else None)

    for slug, st in state.items():
        st["label"] = items[slug]["label"]
    out = {"asked": day, "items": len(items),
           "create": [s for s, st in state.items() if not st["qid"]],
           "edges": sum(len(st["missing"]) for st in state.values()),
           "ambiguous": [s for s, st in state.items() if st["ambiguous"]],
           "needs": sum(len(it.get("needs") or []) for it in items.values()),
           "state": state}
    os.makedirs(BUILD, exist_ok=True)
    with open(os.path.join(BUILD, "wikidata_orgs.json"), "w") as f:
        json.dump(out, f, indent=1)
    if not args.quiet:
        print("%d described: %d to create, %d edges into existing items"
              % (len(items), len(out["create"]), out["edges"]))
        print("wrote %s%s" % (page, " and " + qs_path if qs else ""))
    if not args.apply:
        return 0
    return apply_batch(items, state, day)


def apply_batch(items: dict, state: dict, day: str) -> int:
    """Create the absent items, then add the edges into items that already exist."""
    make = [(slug, items[slug]["label"], item_payload(items[slug], day))
            for slug in sorted(items) if not state[slug]["qid"]]
    edges = [(slug, e) for slug in sorted(items) for e in state[slug]["missing"]]
    if not (make or edges):
        print("nothing to create and no edges missing")
        return 0
    s = logged_in()
    print("acting as %s" % s.user)
    made = len(make) and create_items(
        s, make, os.path.join(DATA, LEDGER),
        "create item for a group in the corpus, from its own site", LEDGER_NOTE)
    if make:
        print("%d/%d created" % (made, len(make)))
    ok = 0
    # Each edge is written down as it lands, in the same file as a creation and for the same
    # reason: the query service will not report it for hours, and the next run must not add
    # it a second time.
    path = os.path.join(DATA, LEDGER)
    for i, (slug, (subj, prop, obj)) in enumerate(edges, 1):
        try:
            s.edit("wbcreateclaim", entity=subj, property=prop, snaktype="value",
                   value=json.dumps({"entity-type": "item", "id": obj}),
                   summary="connect %s to the group it belongs to (paper-geo)" % subj)
            d = read_yaml(path) or {}
            d.setdefault("edges", []).append("%s %s %s" % (subj, prop, obj))
            write_yaml(path, d)
            ok += 1
            print("  %d/%d %s %s %s" % (i, len(edges), subj, prop, obj))
        except (RuntimeError, urllib.error.URLError) as e:
            print("  %d/%d FAILED %s %s %s\n     %s" % (i, len(edges), subj, prop, obj, e))
        time.sleep(1.5)
    if edges:
        print("%d/%d edges added" % (ok, len(edges)))
    return 0 if made == len(make) and ok == len(edges) else 1


if __name__ == "__main__":
    raise SystemExit(main())
