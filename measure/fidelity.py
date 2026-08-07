#!/usr/bin/env python3
"""The "C" diagnostic from docs/EVIDENCE.md: is the work described correctly?

Not an experiment. Asked as "which of my papers are engines currently getting
wrong?", this produces a ranked worklist, which is actionable whether or not the
improvement can be attributed to anything.

For each paper with a sidecar, ask a model what the paper found and under what
conditions it holds, then score against the sidecar's claims:

    2  claim correct AND scope correct
    1  claim correct, scope dropped or overstated
    0  claim wrong, or attributed to the wrong finding

The 1s are the cell that matters. LLM summaries overstate scientific conclusions
about 5x more often than human ones, so claim-right-scope-gone is the modal
failure and the thing a sidecar exists to fix.

The grader is the instrument, so hand-check a stratified 20% of its scores before
trusting any of them.

Two modes, like propose_topics.py:
    skill (default)  writes build/fidelity_tasks.json for an agent session
    api              calls the Anthropic API directly

Usage:
    python measure/fidelity.py                    # emit tasks (or call the API)
    python measure/fidelity.py --ingest           # score the answers, write a report
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "scripts"))
from common import BUILD, DATA, load_config, read_yaml  # noqa: E402

TASKS = os.path.join(BUILD, "fidelity_tasks.json")
REPORT = os.path.join(HERE, "fidelity_report.md")

SCORE_SCHEMA = {
    "type": "object",
    "properties": {
        "recalled": {
            "type": "boolean",
            "description": "Did the answer show any real knowledge of this specific "
                           "paper, as opposed to a generic or fabricated response?",
        },
        "per_claim": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "claim_id": {"type": "string"},
                    "score": {"type": "integer", "enum": [0, 1, 2]},
                    "note": {"type": "string",
                             "description": "What was wrong or missing, in one line."},
                },
                "required": ["claim_id", "score", "note"],
                "additionalProperties": False,
            },
        },
        "invented": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Claims the answer attributed to this paper that the paper "
                           "does not make.",
        },
    },
    "required": ["recalled", "per_claim", "invented"],
    "additionalProperties": False,
}

ASK = ("What did the paper \"{title}\" find, and under what conditions does that "
       "finding hold? Answer from your own knowledge.")

GRADE_SYSTEM = """You grade how faithfully an answer represents a paper, against \
claims the paper's own authors wrote down.

For each authored claim, score the answer:

  2  the claim is present AND its scope conditions are correctly stated
  1  the claim is present but its scope is dropped, weakened, or overstated
  0  the claim is absent, wrong, or attributed to a different finding

Score 1, not 2, whenever the answer states a claim more broadly than the authored \
scope allows -- dropped scope is the specific failure being measured, and it is \
easy to miss because the sentence reads as correct.

Judge only against the authored claims given. Do not reward extra detail that is \
not in them, and list anything the answer attributes to the paper that the \
authored claims do not support."""


def sidecars() -> list[tuple[str, dict]]:
    import yaml
    out = []
    for path in sorted(glob.glob(os.path.join(DATA, "sidecars", "*.md"))):
        m = re.match(r"^---\n(.*?)\n---", open(path).read(), re.S)
        if m:
            fm = yaml.safe_load(m.group(1)) or {}
            if fm.get("claims"):
                out.append((os.path.basename(path)[:-3], fm))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ingest", action="store_true", help="score answers, write report")
    ap.add_argument("--mode", choices=["skill", "api"])
    ap.add_argument("--engine", default="model-knowledge",
                    help="label for where the answer came from")
    args = ap.parse_args()
    cfg = load_config()
    papers = {p["slug"]: p for p in
              (read_yaml(os.path.join(DATA, "papers.yaml")) or {})["papers"]}
    sc = sidecars()
    if not sc:
        sys.exit("no sidecars with claims yet -- nothing to check fidelity against")

    if not args.ingest:
        tasks = []
        for slug, fm in sc:
            p = papers.get(slug, {})
            tasks.append({
                "slug": slug,
                "engine": args.engine,
                "ask": ASK.format(title=p.get("title_display") or p.get("title") or slug),
                "authored_claims": [{"claim_id": c["id"], "text": " ".join(c["text"].split()),
                                     "scope": " ".join(c["scope"].split())}
                                    for c in fm["claims"]],
                "answer": None,   # fill in: what the engine actually said
                "score": None,    # fill in against SCORE_SCHEMA
            })
        os.makedirs(BUILD, exist_ok=True)
        with open(TASKS, "w") as f:
            json.dump({"grade_system": GRADE_SYSTEM, "schema": SCORE_SCHEMA,
                       "tasks": tasks}, f, indent=1)
        print(f"wrote {TASKS}: {len(tasks)} paper(s)")
        print("For each task: put the engine's answer in `answer`, grade it into "
              "`score`, then run --ingest.")
        return

    if not os.path.exists(TASKS):
        sys.exit(f"no {TASKS} -- run without --ingest first")
    doc = json.load(open(TASKS))
    rows, tally = [], {0: 0, 1: 0, 2: 0}
    for t in doc["tasks"]:
        s = t.get("score")
        if not s:
            continue
        for c in s.get("per_claim", []):
            tally[c["score"]] = tally.get(c["score"], 0) + 1
            rows.append((t["slug"], t["engine"], c["claim_id"], c["score"], c["note"]))
        for inv in s.get("invented", []):
            rows.append((t["slug"], t["engine"], "(invented)", 0, inv))

    total = sum(tally.values())
    L = ["# Claim fidelity", "",
         "Generated by `measure/fidelity.py`. A diagnostic, not an experiment: this",
         "is a list of papers to fix, not a p-value.", "",
         f"Claims scored: {total}", ""]
    if total:
        L += [f"- **2 — claim and scope correct:** {tally.get(2,0)} "
              f"({100*tally.get(2,0)/total:.0f}%)",
              f"- **1 — claim correct, scope dropped:** {tally.get(1,0)} "
              f"({100*tally.get(1,0)/total:.0f}%)  ← the cell sidecars exist to move",
              f"- **0 — claim wrong or misattributed:** {tally.get(0,0)} "
              f"({100*tally.get(0,0)/total:.0f}%)", ""]
    L += ["## Worst first", "", "| paper | engine | claim | score | note |",
          "|---|---|---|---|---|"]
    for slug, eng, cid, score, note in sorted(rows, key=lambda r: r[3]):
        L.append(f"| {slug} | {eng} | {cid} | {score} | {note.replace('|', '/')} |")
    L += ["", "## Before trusting these numbers", "",
          "Hand-check a stratified 20% of the scores. The grader is the measurement",
          "instrument and needs its own validation; an unvalidated grader produces",
          "a confident report about nothing."]
    with open(REPORT, "w") as f:
        f.write("\n".join(L) + "\n")
    print(f"wrote {REPORT}: {total} claims scored")
    if total:
        print(f"  correct with scope {tally.get(2,0)} | scope dropped {tally.get(1,0)} "
              f"| wrong {tally.get(0,0)}")


if __name__ == "__main__":
    main()
