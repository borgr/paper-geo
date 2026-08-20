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

Two modes:
    skill (default)  writes build/fidelity_tasks.json to fill in by hand -- the only
                     way to measure the engines this project exists to influence, since
                     AI Overviews and AI Mode have no API
    api              asks and grades through the gateway in $PAPER_GEO_LLM_*, unattended.
                     Measures open-weight model knowledge rather than a search engine's
                     answer, which is a weaker proxy for the target and a real baseline.

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
from common import BUILD, DATA, ROOT, load_config, read_yaml  # noqa: E402

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
# The same env-only contract as `draft_sidecars.call_openai`, imported rather than
# restated so there is one place a gateway is configured. `config.yaml` is committed and
# public; an inference gateway's URL may not be, so none of it is ever a config key.
#
# Two calls per paper, and the separation between them is the whole measurement:
#
#   answer  the title and nothing else. The model must not see the sidecar, or it would
#           be scored on reading comprehension instead of on what it knows.
#   grade   the answer plus the authored claims, held to SCORE_SCHEMA.
#
# So `--answer-model` and `--grade-model` are separate flags. Pointing both at one model
# lets it mark its own homework, which is worth knowing about rather than forbidding:
# the report says which model played which role.


def _client(model_env: str | None):
    """An OpenAI-compatible client and the model id to send, or exit saying what is missing."""
    from draft_sidecars import ENV_BASE, ENV_MODEL, ENV_KEY, ENV_HEADER
    try:
        from openai import OpenAI
    except ImportError:
        sys.exit("pip install openai")
    base, model = os.environ.get(ENV_BASE), model_env or os.environ.get(ENV_MODEL)
    if not base or not model:
        sys.exit(f"--mode api needs ${ENV_BASE} and ${ENV_MODEL} in the environment "
                 f"(never committed -- see draft_sidecars.call_openai)")
    key = os.environ.get(ENV_KEY, "unused")
    headers = {os.environ[ENV_HEADER]: key} if os.environ.get(ENV_HEADER) else None
    # A per-model gateway puts the model slug in the path, so a second model means a
    # second base URL. Substituting the slug we were given keeps one env var enough.
    if model_env and os.environ.get(ENV_MODEL):
        base = base.replace(os.environ[ENV_MODEL].split("/")[-1], model_env.split("/")[-1])
    return OpenAI(base_url=base, api_key=key, default_headers=headers), model


def _chat(client, model: str, msgs: list[dict], label: str, want: dict | None = None):
    """One completion. Returns text, or the parsed object when `want` is a schema.

    Schema enforcement is attempted and not required, for the same reason as the drafting
    path: a gateway that rejects `response_format` would otherwise be unusable, and the
    open models this exists to try are exactly the ones behind such gateways.
    """
    from draft_sidecars import _first_json, decodable, with_retries
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
    return _first_json(text) if want is not None else text


def run_api(tasks: list[dict], answer_model: str | None, grade_model: str | None) -> None:
    """Fill `answer` and `score` on every task in place, one paper at a time."""
    ac, am = _client(answer_model)
    gc, gm = _client(grade_model) if grade_model else (ac, am)
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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ingest", action="store_true", help="score answers, write report")
    ap.add_argument("--mode", choices=["skill", "api"])
    ap.add_argument("--engine", default="model-knowledge",
                    help="label for where the answer came from")
    ap.add_argument("--answer-model", help="model id to ask (--mode api); defaults to "
                                          "$PAPER_GEO_LLM_MODEL")
    ap.add_argument("--grade-model", help="model id to grade with (--mode api); defaults "
                                         "to the answering model, which marks its own work")
    ap.add_argument("--limit", type=int, help="first N papers only, for a smoke run")
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
        if args.limit:
            tasks = tasks[:args.limit]
        if args.mode == "api":
            run_api(tasks, args.answer_model, args.grade_model)
        os.makedirs(BUILD, exist_ok=True)
        with open(TASKS, "w") as f:
            json.dump({"grade_system": GRADE_SYSTEM, "schema": SCORE_SCHEMA,
                       "tasks": tasks}, f, indent=1)
        print(f"wrote {TASKS}: {len(tasks)} paper(s)")
        if args.mode == "api":
            print(f"Now: python {os.path.relpath(__file__, ROOT)} --ingest")
        else:
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
