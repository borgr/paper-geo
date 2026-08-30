#!/usr/bin/env python3
"""The "C" diagnostic from docs/EVIDENCE.md: is the work described correctly?

Not an experiment. It answers "which of my papers are engines currently getting wrong?"
and produces a ranked worklist.

For each paper with a sidecar, ask a model what the paper found and under what conditions
it holds, then score against the sidecar's claims:

    2  claim correct AND scope correct
    1  claim correct, scope dropped or overstated
    0  claim wrong, or attributed to the wrong finding

The 1s are the cell that matters: LLM summaries overstate scientific conclusions about 5x
more often than human ones, so claim-right-scope-gone is the modal failure and the thing a
sidecar exists to fix.

The grader is the instrument. Hand-check a stratified 20% of its scores before trusting
any of them.

Two modes:
    skill (default)  writes build/fidelity_tasks.json to fill in by hand -- the only way
                     to measure the engines this project targets, since AI Overviews and
                     AI Mode have no API
    api              asks and grades through the gateway in $PAPER_GEO_LLM_*, unattended.
                     Measures open-weight model knowledge, a weaker proxy and a real
                     baseline.

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
from common import BUILD, DATA, ROOT, read_papers, title_of, write_json  # noqa: E402
from llm import client, decodable, first_json, with_retries  # noqa: E402

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


# --------------------------------------------------------------------- the gateway
#
# Two calls per paper, and the separation between them is the measurement:
#
#   answer  the title and nothing else. The model must not see the sidecar, or it would
#           be scored on reading comprehension instead of on what it knows.
#   grade   the answer plus the authored claims, held to SCORE_SCHEMA.
#
# Hence separate `--answer-model` and `--grade-model`. Pointing both at one model lets it
# mark its own homework; the report says which model played which role.


def _chat(client, model: str, msgs: list[dict], label: str, want: dict | None = None):
    """One completion. Returns text, or the parsed object when `want` is a schema.

    Schema enforcement is attempted and not required: a gateway that rejects
    `response_format` would otherwise be unusable, and the open models this exists to try
    are exactly the ones behind such gateways.
    """
    req = dict(model=model, messages=msgs, max_tokens=2048, temperature=0.0, seed=48)
    if want is not None:
        rf = {"type": "json_schema",
              "json_schema": {"name": "score", "schema": decodable(want), "strict": True}}
        try:
            r = with_retries(lambda: client.chat.completions.create(**req,
                                                                   response_format=rf), label)
        except Exception:                            # noqa: BLE001 -- any 4xx means no
            r = with_retries(lambda: client.chat.completions.create(**req), label)
    else:
        r = with_retries(lambda: client.chat.completions.create(**req), label)
    text = r.choices[0].message.content or ""
    return first_json(text) if want is not None else text


def run_api(tasks: list[dict], answer_model: str | None, grade_model: str | None) -> None:
    """Fill `answer` and `score` on every task in place, one paper at a time."""
    ac, am = client(answer_model, context="--mode api")
    gc, gm = client(grade_model, context="--grade-model") if grade_model else (ac, am)
    for t in tasks:
        try:
            t["answer"] = _chat(ac, am, [{"role": "user", "content": t["ask"]}], t["slug"])
            t["engine"] = am
            key = json.dumps(t["authored_claims"], indent=1)
            t["score"] = _chat(gc, gm, [{"role": "system", "content": GRADE_SYSTEM},
                                        {"role": "user",
                                         "content": f"Answer to grade:\n{t['answer']}\n\n"
                                                    f"Authored claims:\n{key}"}],
                               f"grade:{t['slug']}", want=SCORE_SCHEMA)
            t["graded_by"] = gm
            n = len((t.get("score") or {}).get("per_claim") or [])
            print(f"  ok  {t['slug'][:52]:52} {n} claim(s) scored")
        except Exception as e:                       # noqa: BLE001 -- one paper, not the run
            print(f"  --  {t['slug'][:52]:52} {type(e).__name__}: {str(e)[:80]}",
                  file=sys.stderr)


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


def answered(path: str) -> int:
    """How many answers a tasks file already holds. 0 for a file that is not one."""
    try:
        with open(path) as f:
            return sum(1 for t in json.load(f)["tasks"] if (t.get("answer") or "").strip())
    except (OSError, ValueError, KeyError, TypeError):
        return 0


def emit(sc: list, papers: dict, args) -> None:
    """`build/fidelity_tasks.json`, one task per sidecar, `answer` and `score` left blank.

    `--mode api` fills both in before the file is written. Without it the file is the whole
    point: AI Overviews and AI Mode have no API, so the only way to measure the engines this
    project targets is a person pasting into the two blank fields.
    """
    # A blank task file is the same size and shape as a filled-in one, so overwriting a run
    # somebody spent an afternoon pasting into left no trace and no error. It happened once,
    # to 98 graded papers whose report is still in the repo describing answers nothing holds.
    held = answered(TASKS)
    if held and not args.force:
        sys.exit(f"{TASKS} already holds {held} answer(s). Score them with --ingest, or "
                 f"pass --force to throw them away and ask again.")
    tasks = []
    for slug, fm in sc:
        p = papers.get(slug, {})
        tasks.append({
            "slug": slug,
            "engine": args.engine,
            "ask": ASK.format(title=title_of(p) or slug),
            "authored_claims": [{"claim_id": c["id"], "text": " ".join(c["text"].split()),
                                 "scope": " ".join(c["scope"].split())}
                                for c in fm["claims"]],
            "answer": None,   # fill in: what the engine actually said
            "score": None,    # fill in against SCORE_SCHEMA
        })
    if args.limit:
        tasks = tasks[:args.limit]
    if args.mode == "api":
        run_api(tasks, args.answer_model, args.grade_model)
    write_json(
        TASKS,
        {"grade_system": GRADE_SYSTEM, "schema": SCORE_SCHEMA,
         "tasks": tasks}, indent=1)
    print(f"wrote {TASKS}: {len(tasks)} paper(s)")
    if args.mode == "api":
        print(f"Now: python {os.path.relpath(__file__, ROOT)} --ingest")
    else:
        print("For each task: put the engine's answer in `answer`, grade it into "
              "`score`, then run --ingest.")


def scored(doc: dict) -> tuple[list, dict, dict]:
    """One row per scored claim, the tally over the three scores, and the run's counts.

    The counts also carry `total`, `papers` and `floor`, so the report and the console line
    read the same numbers rather than each deriving them.
    """
    rows, tally = [], {0: 0, 1: 0, 2: 0}
    recalled, graded, invented, ungraded, unanswered = 0, 0, 0, [], []
    engines, graders = set(), set()
    for t in doc["tasks"]:
        s = t.get("score")
        if not (t.get("answer") or "").strip():
            unanswered.append(t["slug"])
            continue
        if not s:
            # An answer with no score is not a paper that scored nothing -- it is a paper
            # the grader failed on, and dropping it silently shrinks the denominator while
            # the report still reads as covering the corpus.
            ungraded.append(t["slug"])
            continue
        graded += 1
        recalled += bool(s.get("recalled"))
        engines.add(t.get("engine") or "?")
        graders.add(t.get("graded_by") or "?")
        for c in s.get("per_claim", []):
            tally[c["score"]] = tally.get(c["score"], 0) + 1
            rows.append((t["slug"], t["engine"], c["claim_id"], c["score"], c["note"]))
        for inv in s.get("invented", []):
            invented += 1
            rows.append((t["slug"], t["engine"], "(invented)", 0, inv))
    n = {"graded": graded, "recalled": recalled, "invented": invented,
         "ungraded": ungraded, "unanswered": unanswered, "engines": engines,
         "graders": graders, "total": sum(tally.values()), "papers": len(doc["tasks"])}
    # What the table is depends on recall. With papers recognised, the scores rank them by
    # how badly they are described and that ranking is the product. With almost none, every
    # paper scores the same 0 and the ranking is noise -- so the report has to say it
    # measured a floor rather than hand over a worklist ordered by nothing.
    n["floor"] = graded and recalled <= max(2, 0.05 * graded)
    return rows, tally, n


def _summary(tally: dict, n: dict) -> list[str]:
    """The counts, who produced them, and the share at each of the three scores."""
    graded, total = n["graded"], n["total"]
    L = ["# Claim fidelity", "",
         "Generated by `measure/fidelity.py`. A diagnostic, not an experiment.", "",
         f"- Papers asked: **{n['papers']}**",
         f"- Answered and graded: **{graded}**",
         f"- Showed real knowledge of the paper (`recalled`): **{n['recalled']}**"
         + (f" — {100*n['recalled']/graded:.0f}%" if graded else ""),
         f"- Claims scored: **{total}**",
         f"- Claims the answer invented: **{n['invented']}**", ""]
    if n["engines"]:
        L += [f"Answered by `{', '.join(sorted(n['engines']))}`, graded by "
              f"`{', '.join(sorted(n['graders']))}`.", ""]
    if total:
        L += [f"- **2 — claim and scope correct:** {tally.get(2,0)} "
              f"({100*tally.get(2,0)/total:.0f}%)",
              f"- **1 — claim correct, scope dropped:** {tally.get(1,0)} "
              f"({100*tally.get(1,0)/total:.0f}%)  ← the cell sidecars exist to move",
              f"- **0 — claim wrong or misattributed:** {tally.get(0,0)} "
              f"({100*tally.get(0,0)/total:.0f}%)", ""]
    return L


def _floor_note(n: dict) -> list[str]:
    """Why a run nothing recognised is a baseline and not a ranking. Empty above the floor."""
    if not n["floor"]:
        return []
    graded, total = n["graded"], n["total"]
    return ["## This is a floor, not a worklist", "",
            f"{graded - n['recalled']} of {graded} papers were not recognised at all, and "
            f"the answers are not blank -- they are",
            f"fluent, specific and about papers that do not exist: {n['invented']} invented "
            f"claims against",
            f"{total} authored ones. So the per-claim table below ranks nothing, because "
            f"every paper",
            "scored the same score. What the run establishes is a baseline -- this engine "
            "cannot",
            "describe this corpus unaided -- which is the gap the pages exist to close.", "",
            "For a ranking instead, ask an engine that retrieves. Answers have to be able "
            "to differ",
            "before their scores can.", ""]


def _excluded(n: dict) -> list[str]:
    """The papers the numbers above leave out, named, with the denominator they are out of."""
    L = []
    if n["ungraded"]:
        L += ["## Answered but not graded", "",
              f"{len(n['ungraded'])} paper(s) got an answer the grader returned no usable "
              f"score for. They are excluded",
              f"from every number above, so those counts are over {n['graded']} papers, "
              f"not {n['papers']}.", ""]
        L += [f"- `{s}`" for s in n["ungraded"]] + [""]
    if n["unanswered"]:
        L += ["## No answer", "",
              f"{len(n['unanswered'])} paper(s) produced no answer at all (a gateway error, "
              "usually).", ""]
        L += [f"- `{s}`" for s in n["unanswered"]] + [""]
    return L


def _table(rows: list, n: dict) -> list[str]:
    """A row per scored claim, worst first, and what to do before believing any of it."""
    # At the floor a row per claim is ~1200 lines saying "not recognised". The invented
    # claims differ from each other and are the only part of such a run that carries
    # information, so the table narrows to them -- and states how many rows it dropped,
    # because a cap that does not announce itself reads as "this is everything".
    shown = [r for r in rows if r[2] == "(invented)"] if n["floor"] else rows
    L = ["## What it said instead" if n["floor"] else "## Worst first", ""]
    if n["floor"]:
        L += [f"Only the invented claims. The other {len(rows) - len(shown)} rows score the "
              f"corpus against a model that",
              "does not know it, so their order carries nothing to work down.", ""]
    L += ["| paper | engine | claim | score | note |", "|---|---|---|---|---|"]
    for slug, eng, cid, score, note in sorted(shown, key=lambda r: r[3]):
        L.append(f"| {slug} | {eng} | {cid} | {score} | {note.replace('|', '/')} |")
    return L + ["", "## Before trusting these numbers", "",
                "Hand-check a stratified 20% of the scores. The grader is the measurement",
                "instrument and needs its own validation; an unvalidated grader produces",
                "a confident report about nothing."]


def _say(tally: dict, n: dict) -> None:
    """The console line, and on stderr the papers the report had to leave out."""
    print(f"wrote {REPORT}: {n['total']} claims scored over {n['graded']} of "
          f"{n['papers']} paper(s)")
    if n["total"]:
        print(f"  correct with scope {tally.get(2,0)} | scope dropped {tally.get(1,0)} "
              f"| wrong {tally.get(0,0)} | invented {n['invented']}")
    if n["graded"]:
        print(f"  recognised the paper at all: {n['recalled']}/{n['graded']}")
    if n["ungraded"]:
        print(f"  {len(n['ungraded'])} answered but ungraded, excluded from the above",
              file=sys.stderr)
    if n["unanswered"]:
        print(f"  {len(n['unanswered'])} never answered", file=sys.stderr)


def ingest() -> None:
    """`measure/fidelity_report.md` from the filled-in answers, in four parts.

    The counts, why a run that recognised nothing is a floor, the papers left out of the
    counts, and the per-claim table.
    """
    if not os.path.exists(TASKS):
        sys.exit(f"no {TASKS} -- run without --ingest first")
    doc = json.load(open(TASKS))
    rows, tally, n = scored(doc)
    with open(REPORT, "w") as f:
        f.write("\n".join(_summary(tally, n) + _floor_note(n) + _excluded(n)
                          + _table(rows, n)) + "\n")
    _say(tally, n)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ingest", action="store_true", help="score answers, write report")
    ap.add_argument("--mode", choices=["skill", "api"])
    ap.add_argument("--engine", default="model-knowledge",
                    help="label for where the answer came from")
    ap.add_argument("--answer-model", help="MODEL_ID[@BASE_URL] to ask (--mode api); "
                                          "defaults to $PAPER_GEO_LLM_MODEL")
    ap.add_argument("--grade-model", help="MODEL_ID[@BASE_URL] to grade with (--mode api); "
                                         "defaults to the answerer, which marks its own work")
    ap.add_argument("--limit", type=int, help="first N papers only, for a smoke run")
    ap.add_argument("--force", action="store_true",
                    help="overwrite a tasks file that already holds answers")
    args = ap.parse_args()
    papers = {p["slug"]: p for p in read_papers()}
    sc = sidecars()
    if not sc:
        sys.exit("no sidecars with claims yet -- nothing to check fidelity against")
    ingest() if args.ingest else emit(sc, papers, args)


if __name__ == "__main__":
    main()
