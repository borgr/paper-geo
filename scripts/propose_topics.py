#!/usr/bin/env python3
"""Propose GitHub topics + one-line descriptions for repos, using a model.

A wrong topic is worse than no topic: it misleads retrieval and reads as
careless, so the model is told to omit rather than guess.

Two modes, set by `llm.mode` in config.yaml:

  skill  (default)  Writes build/llm_tasks.json and stops. An agent session
                    reads it, fills in `proposal` for each task, and runs
                    `--ingest`. No API key required.
  api               Calls the Anthropic API directly. Needed for unattended
                    reruns; requires ANTHROPIC_API_KEY or an `ant auth login`
                    profile.

Idempotent by design: only repos whose proposal is missing or stale are sent.
Anything you edited by hand and marked `reviewed: true` in data/repos.yaml is
never overwritten, so this is safe to re-run whenever new repos appear.

Usage:
    python scripts/propose_topics.py                 # emit tasks (or call the API)
    python scripts/propose_topics.py --ingest        # fold answers back in
    python scripts/propose_topics.py --all           # re-propose even reviewed repos
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (BUILD, DATA, gh_text, load_config, read_yaml,  # noqa: E402
                    rules_block, write_yaml)

SCHEMA = {
    "type": "object",
    "properties": {
        "description": {
            "type": "string",
            "description": ("One line, under 120 chars, saying what this repo IS and "
                            "what it's for. No marketing. If the repo backs a paper, "
                            "name the method or artifact in plain words."),
        },
        "topics": {
            "type": "array",
            "items": {"type": "string"},
            "description": ("3-8 GitHub topics: lowercase, dashes, no spaces. Only "
                            "topics you are confident about from the evidence given. "
                            "Prefer widely-used terms other people search for over "
                            "coined project names. Omit rather than guess."),
        },
        "generic_gloss": {
            "type": "string",
            "description": ("If the repo name is a coined name (TextArena, ZipNN, DOVE, "
                            "ColPret), the plain-language phrase someone would actually "
                            "search for instead. Empty string if the name is already "
                            "descriptive."),
        },
        "kind": {
            "type": "string",
            "enum": ["paper-code", "guide", "tool", "dataset", "website", "teaching", "other"],
            "description": "What kind of repo this is.",
        },
        "confidence": {
            "type": "string",
            "enum": ["high", "medium", "low"],
            "description": "How sure you are. Use low when the README is thin or absent.",
        },
    },
    "required": ["description", "topics", "generic_gloss", "kind", "confidence"],
    "additionalProperties": False,
}

RULES_DOC = "docs/RULES.md"

FRAMING = """You label GitHub repositories belonging to an academic researcher so \
that both GitHub search and AI answer engines can find them.

The rules below are the repo's own labelling rules, read verbatim from {doc} §11.2.

"""

CONTRACT = [
    "Fill each task's `proposal` object against `schema`, then run --ingest.",
    "Do not hand-edit data/repos.yaml -- the next run re-derives it from GitHub.",
    "Do not write outward: `sweep_github.py apply` and `update.py --apply` are the",
    "author's, and both are gated on reading `sweep_github.py diff` first.",
]


def system_prompt() -> str:
    """The framing plus the rules, which live in docs/RULES.md §11.2, not here.

    Same one-source rule as draft_sidecars.py: the doc is the only copy, so editing
    the rules changes the prompt in the same commit. Raises if the markers are gone.
    """
    return FRAMING.format(doc=RULES_DOC) + rules_block(RULES_DOC)


def evidence(repo: dict) -> str:
    """Assemble what the model gets to see. Kept small and factual."""
    name = repo["repo"]
    readme = ""
    for fn in ("README.md", "README.rst", "readme.md", "README.txt"):
        b64 = gh_text("api", f"repos/{name}/contents/{fn}", "-q", ".content")
        if b64:
            try:
                readme = base64.b64decode(b64).decode("utf-8", "replace")[:6000]
                break
            except Exception:
                pass
    files = gh_text("api", f"repos/{name}/contents", "-q", ".[].name") or ""
    parts = [
        f"repo name: {name.split('/')[-1]}",
        f"current description: {repo.get('current_description') or '(none)'}",
        f"stars: {repo.get('stars', 0)}",
        f"linked paper: {repo.get('paper') or '(none known)'}",
        f"top-level files: {', '.join(files.split()[:25]) or '(none)'}",
        "",
        "README (truncated):",
        readme.strip() or "(no README)",
    ]
    return "\n".join(parts)


def pending(repos: list[dict], do_all: bool) -> list[dict]:
    """Repos needing a proposal. `reviewed: true` is a permanent opt-out."""
    out = []
    for r in repos:
        if r.get("skip"):
            continue
        if r.get("reviewed") and not do_all:
            continue
        if r.get("llm_proposal") and not do_all:
            continue
        out.append(r)
    return out


def declined_to_guess(repos: list[dict]) -> list[str]:
    """Repos still missing a label that the labeller refused to invent one for.

    Missing *either* topics or a description, matching `sweep_github.py`'s own count of what
    needs labelling. Two of the three live cases have a description and no topics, so
    requiring both reported one repo where there are three.

    They are stuck where two correct decisions meet: `pending()` skips a row that already has
    a proposal, and `promote()` refuses a `confidence: low` one -- so the row keeps its
    non-answer and stays bare. Neither half is wrong; going quiet about the result is, since
    `propose` printed "nothing to propose" while three repos had no label at all.

    Deliberately not fixed by re-proposing them. The model's answer was that the evidence does
    not support a label, and the evidence is a README, so asking again costs a call for the
    same answer. The fix is upstream and it is a paragraph of prose.
    """
    return [r["repo"] for r in repos
            if not r.get("skip") and not r.get("reviewed")
            and (not r.get("topics") or not r.get("description"))
            and (r.get("llm_proposal") or {}).get("confidence") == "low"]


def emit_tasks(todo: list[dict]) -> str:
    os.makedirs(BUILD, exist_ok=True)
    path = os.path.join(BUILD, "llm_tasks.json")
    tasks = [{"repo": r["repo"], "evidence": evidence(r), "proposal": None} for r in todo]
    with open(path, "w") as f:
        json.dump({"_contract": CONTRACT, "system": system_prompt(),
                   "schema": SCHEMA, "tasks": tasks}, f, indent=1)
    return path


def call_api(todo: list[dict], cfg) -> list[str]:
    """Label each repo with one Messages API call, validated against SCHEMA.

    Returns the repos it wrote a proposal for -- not the ones it was asked about, since
    a refusal or unparseable answer leaves the row's previous proposal standing, and
    promoting that again is the bug `promote()` exists to avoid.
    """
    try:
        import anthropic
    except ImportError:
        sys.exit("pip install anthropic, or set llm.mode: skill in config.yaml")

    client = anthropic.Anthropic()          # resolves key or `ant auth login` profile
    model = cfg["llm"]["model"]
    effort = cfg["llm"].get("effort", "medium")
    sys_prompt = system_prompt()
    done = []
    for r in todo:
        req = dict(
            model=model,
            # Thinking is on by default on Opus 5 and counts against max_tokens,
            # so leave real headroom above the size of the JSON itself.
            max_tokens=4096,
            system=sys_prompt,
            messages=[{"role": "user",
                       "content": f"Label this repository.\n\n{evidence(r)}"}],
        )
        oc = {"effort": effort,
              "format": {"type": "json_schema", "schema": SCHEMA}}
        try:
            msg = client.messages.create(**req, output_config=oc)
        except TypeError:
            # Older SDKs do not type output_config; the wire field is the same.
            msg = client.messages.create(**req, extra_body={"output_config": oc})
        if msg.stop_reason == "refusal":
            print(f"  refused: {r['repo']}", file=sys.stderr)
            continue
        if msg.stop_reason == "max_tokens":
            # Distinct from a parse failure: truncated JSON is invalid JSON, and
            # "unparseable" sends the reader looking for a bad field that is not there.
            print(f"  truncated at max_tokens: {r['repo']}", file=sys.stderr)
            continue
        text = next((b.text for b in msg.content if b.type == "text"), "")
        try:
            r["llm_proposal"] = json.loads(text)
            print(f"  ok  {r['repo']}: {r['llm_proposal']['topics']}")
            done.append(r["repo"])
        except json.JSONDecodeError:
            print(f"  unparseable: {r['repo']}", file=sys.stderr)
    return done


def ingest(repos: list[dict]) -> list[str]:
    """Fold build/llm_tasks.json answers into repos.yaml.

    Returns the repos whose proposal actually *changed*, which is exactly the set
    `promote()` is allowed to touch. Changed rather than present: build/llm_tasks.json
    outlives the run that produced it, so a second `--ingest` sees the same answers
    again, and treating those as new is what let a promotion overwrite a hand edit made
    in between. Re-ingesting an unchanged file is now a no-op, which is what idempotent
    means here.
    """
    path = os.path.join(BUILD, "llm_tasks.json")
    if not os.path.exists(path):
        sys.exit(f"no {path} -- run without --ingest first")
    with open(path) as f:
        answers = {t["repo"]: t.get("proposal") for t in json.load(f)["tasks"]}
    by_name = {r["repo"]: r for r in repos}
    done = []
    for name, proposal in answers.items():
        r = by_name.get(name)
        if proposal and r is not None and r.get("llm_proposal") != proposal:
            r["llm_proposal"] = proposal
            done.append(name)
    return done


def promote(repos: list[dict], fresh: list[str]) -> int:
    """Copy a just-arrived llm_proposal into the fields the sweep actually applies.

    Only the repos named in `fresh` -- the ones whose proposal changed in this run. Promoting
    every row on every ingest silently undid hand edits: deleting a wrong topic from
    repos.yaml left `llm_proposal` untouched, so the next unrelated ingest copied it back.
    Editing the file is the cheapest way to correct a label and has to survive with no
    bookkeeping; `reviewed: true` freezes a row against future proposals, which is a different
    thing.

    Never overwrites a reviewed repo, and never blanks an existing value with an empty
    proposal, so a bad or partial answer degrades to "no change".

    `confidence: low` is not promoted -- it is the model's one channel for saying "the README
    is thin, I am guessing". The proposal still lands in `llm_proposal`, so the row keeps
    showing up as needing a label instead of quietly acquiring a guessed one.
    """
    want, n = set(fresh), 0
    for r in repos:
        p = r.get("llm_proposal") or {}
        if r.get("reviewed") or not p or r.get("repo") not in want:
            continue
        if p.get("confidence") == "low":
            print(f"  low confidence, not promoted: {r['repo']}")
            continue
        if p.get("topics"):
            # `declined_topics` is the only durable record of a topic a human rejected. Deleting it
            # from `topics` is not: a deletion cannot be distinguished from a topic never proposed,
            # so the next ingest puts it back -- which happened to `nlp-free` on DORA.
            declined = set(r.get("declined_topics") or [])
            keep = sorted(set(p["topics"]) - declined)[:12]
            for t in sorted(set(p["topics"]) & declined):
                print(f"  declined earlier, not promoted: {r['repo']} '{t}'")
            r["topics"] = keep
        if p.get("description"):
            r["description"] = p["description"]
        if p.get("kind"):
            r["kind"] = p["kind"]
        if p.get("generic_gloss"):
            r["generic_gloss"] = p["generic_gloss"]
        n += 1
    return n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ingest", action="store_true",
                    help="fold build/llm_tasks.json answers back into repos.yaml")
    ap.add_argument("--all", action="store_true",
                    help="re-propose every repo, including reviewed ones")
    ap.add_argument("--mode", choices=["skill", "api"], help="override config llm.mode")
    args = ap.parse_args()

    cfg = load_config()
    path = os.path.join(DATA, "repos.yaml")
    doc = read_yaml(path)
    if not doc:
        sys.exit("no data/repos.yaml -- run: python scripts/sweep_github.py propose")
    repos = doc["repos"]

    if args.ingest:
        fresh = ingest(repos)
        n = promote(repos, fresh)
        write_yaml(path, doc)
        print(f"ingested {len(fresh)} proposals into {path}, {n} promoted "
              f"(reviewed rows are frozen; a hand edit stands until that repo is "
              f"re-proposed)")
        print("next: python scripts/sweep_github.py diff")
        return

    todo = pending(repos, args.all)
    if not todo:
        print("nothing to propose -- every repo is reviewed or already proposed")
        stuck = declined_to_guess(repos)
        if stuck:
            by_name = {r["repo"]: r for r in repos}
            print(f"\n{len(stuck)} are still unlabelled, because the labeller declined "
                  f"to guess:")
            for n in stuck:
                r = by_name[n]
                lack = ", ".join(w for w, have in (("topics", r.get("topics")),
                                                   ("description", r.get("description")))
                                 if not have)
                print(f"  {n:<20} no {lack}")
            print("Thin or absent README, and the line above is why they will not come "
                  "back\nas work: the proposal counts as answered. Write a README and the "
                  "next\nproposal has something to read -- or `--all` to ask again "
                  "regardless.")
        return
    mode = args.mode or cfg["llm"]["mode"]
    if mode == "api":
        print(f"labelling {len(todo)} repos via {cfg['llm']['model']} ...")
        promote(repos, call_api(todo, cfg))
        write_yaml(path, doc)
        print(f"wrote {path}\nnext: python scripts/sweep_github.py diff")
    else:
        out = emit_tasks(todo)
        print(f"wrote {out}: {len(todo)} repos need labels")
        print("Fill in each task's `proposal` object against the embedded schema, then:")
        print("  python scripts/propose_topics.py --ingest")


if __name__ == "__main__":
    main()
