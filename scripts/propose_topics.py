#!/usr/bin/env python3
"""Propose GitHub topics + one-line descriptions for repos, using a model.

Replaces the keyword matcher, which mislabelled roughly a third of repos
(grammatical-error-correction tagged `model-merging`, a sentence-similarity
metric tagged `pretraining`). A wrong topic is worse than no topic: it misleads
retrieval and reads as careless.

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
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import BUILD, DATA, load_config, read_yaml, write_yaml  # noqa: E402

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

SYSTEM = """You label GitHub repositories belonging to an academic researcher so \
that both GitHub search and AI answer engines can find them.

Two things matter more than sounding good:

1. Accuracy over coverage. A wrong topic actively misleads retrieval. If the \
evidence does not support a label, leave it out and set confidence lower. An \
empty-ish but correct set beats a full but wrong one.

2. Search vocabulary, not project vocabulary. Use the words someone who does not \
already know this project would type. Coined names are for branding; generic \
phrasing is what gets retrieved.

Judge only from the evidence provided. Do not infer a research area from the \
author's other work, and do not assume a repo is paper code because the author \
is a researcher — many are guides, teaching material, or small utilities."""


def gh(*args: str) -> str:
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    return "" if r.returncode else r.stdout


def evidence(repo: dict) -> str:
    """Assemble what the model gets to see. Kept small and factual."""
    name = repo["repo"]
    readme = ""
    for fn in ("README.md", "README.rst", "readme.md", "README.txt"):
        b64 = gh("api", f"repos/{name}/contents/{fn}", "-q", ".content")
        if b64:
            try:
                readme = base64.b64decode(b64).decode("utf-8", "replace")[:6000]
                break
            except Exception:
                pass
    files = gh("api", f"repos/{name}/contents", "-q", ".[].name") or ""
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


def emit_tasks(todo: list[dict]) -> str:
    os.makedirs(BUILD, exist_ok=True)
    path = os.path.join(BUILD, "llm_tasks.json")
    tasks = [{"repo": r["repo"], "evidence": evidence(r), "proposal": None} for r in todo]
    with open(path, "w") as f:
        json.dump({"system": SYSTEM, "schema": SCHEMA, "tasks": tasks}, f, indent=1)
    return path


def call_api(todo: list[dict], cfg) -> None:
    """Label each repo with one Messages API call, validated against SCHEMA."""
    try:
        import anthropic
    except ImportError:
        sys.exit("pip install anthropic, or set llm.mode: skill in config.yaml")

    client = anthropic.Anthropic()          # resolves key or `ant auth login` profile
    model = cfg["llm"]["model"]
    effort = cfg["llm"].get("effort", "medium")
    for r in todo:
        req = dict(
            model=model,
            # Thinking is on by default on Opus 5 and counts against max_tokens,
            # so leave real headroom above the size of the JSON itself.
            max_tokens=4096,
            system=SYSTEM,
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
        text = next((b.text for b in msg.content if b.type == "text"), "")
        try:
            r["llm_proposal"] = json.loads(text)
            print(f"  ok  {r['repo']}: {r['llm_proposal']['topics']}")
        except json.JSONDecodeError:
            print(f"  unparseable: {r['repo']}", file=sys.stderr)


def ingest(repos: list[dict]) -> int:
    """Fold build/llm_tasks.json answers into repos.yaml."""
    path = os.path.join(BUILD, "llm_tasks.json")
    if not os.path.exists(path):
        sys.exit(f"no {path} -- run without --ingest first")
    with open(path) as f:
        answers = {t["repo"]: t.get("proposal") for t in json.load(f)["tasks"]}
    by_name = {r["repo"]: r for r in repos}
    n = 0
    for name, proposal in answers.items():
        if proposal and name in by_name:
            by_name[name]["llm_proposal"] = proposal
            n += 1
    return n


def promote(repos: list[dict]) -> None:
    """Copy llm_proposal into the fields the sweep actually applies.

    Never overwrites a reviewed repo, and never blanks an existing value with an
    empty proposal -- so a bad or partial model answer degrades to "no change".
    """
    for r in repos:
        p = r.get("llm_proposal") or {}
        if r.get("reviewed") or not p:
            continue
        if p.get("topics"):
            r["topics"] = sorted(set(p["topics"]))[:12]
        if p.get("description"):
            r["description"] = p["description"]
        if p.get("kind"):
            r["kind"] = p["kind"]
        if p.get("generic_gloss"):
            r["generic_gloss"] = p["generic_gloss"]


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
        n = ingest(repos)
        promote(repos)
        write_yaml(path, doc)
        print(f"ingested {n} proposals into {path}")
        print("next: python scripts/sweep_github.py diff")
        return

    todo = pending(repos, args.all)
    if not todo:
        print("nothing to propose -- every repo is reviewed or already proposed")
        return
    mode = args.mode or cfg["llm"]["mode"]
    if mode == "api":
        print(f"labelling {len(todo)} repos via {cfg['llm']['model']} ...")
        call_api(todo, cfg)
        promote(repos)
        write_yaml(path, doc)
        print(f"wrote {path}\nnext: python scripts/sweep_github.py diff")
    else:
        out = emit_tasks(todo)
        print(f"wrote {out}: {len(todo)} repos need labels")
        print("Fill in each task's `proposal` object against the embedded schema, then:")
        print("  python scripts/propose_topics.py --ingest")


if __name__ == "__main__":
    main()
