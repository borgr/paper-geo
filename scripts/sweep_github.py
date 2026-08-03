#!/usr/bin/env python3
"""Repo metadata sweep: topics, descriptions, homepage, CITATION.cff.

Three-phase by design, because this writes to public repos:

    propose  ->  data/repos.yaml   (generated; you edit it)
    diff     ->  show exactly what would change on GitHub
    apply    ->  write it (requires --yes)

Topics are GitHub's primary discovery facet and this account currently has zero
on every repo. Forks are skipped: they are not yours to describe.

Usage:
    python scripts/sweep_github.py propose
    python scripts/sweep_github.py diff
    python scripts/sweep_github.py apply --yes
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import BUILD, DATA, load_config, norm_title, read_yaml, write_yaml  # noqa: E402

# Controlled vocabulary: GitHub topics must be lowercase, dashed, <=50 chars.
# Matched case-insensitively against repo name + description + README.
VOCAB = {
    "nlp": ["nlp", "natural language", "language model", "linguistic"],
    "large-language-models": ["llm", "large language model", "gpt", "language model"],
    "evaluation": ["eval", "benchmark", "metric", "leaderboard", "assess"],
    "benchmark": ["benchmark", "leaderboard", "arena"],
    "model-merging": ["merg", "fusion", "model soup", "weight averag"],
    "machine-learning": ["machine learning", "deep learning", "neural", "training"],
    "reinforcement-learning": ["reinforcement", " rl ", "policy gradient", "reward"],
    "datasets": ["dataset", "corpus", "data release", "crowdsourc"],
    "pretraining": ["pretrain", "pre-train", "babylm", "sample-efficient"],
    "scaling-laws": ["scaling law", "scaling", "compute budget"],
    "model-compression": ["compress", "lossless", "quantiz", "zipnn"],
    "text-games": ["text game", "textarena", "game", "agent arena"],
    "agents": ["agent", "agentic", "tool use"],
    "multilinguality": ["multilingual", "cross-lingual", "language coverage"],
    "human-feedback": ["human feedback", "preference", "annotat", "rlhf"],
    "interpretability": ["interpret", "probing", "weight space", "representation"],
    "research-tools": ["guide", "tips", "tutorial", "template", "skill"],
    "reproducibility": ["reproduc", "replicat", "artifact"],
}


def gh(*args: str) -> str:
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr.strip() or f"gh {' '.join(args)} failed")
    return r.stdout


def gh_json(path: str, jq: str | None = None):
    args = ["api", path]
    if jq:
        args += ["-q", jq]
    return gh(*args)


def list_repos(cfg) -> list[dict]:
    user = cfg["ids"]["github"]
    out, page = [], 1
    while True:
        raw = gh_json(f"users/{user}/repos?per_page=100&page={page}")
        batch = json.loads(raw)
        if not batch:
            break
        out += batch
        page += 1
    keep = [r for r in out
            if (cfg["github_sweep"]["include_forks"] or not r["fork"])
            and r["name"] not in cfg["github_sweep"]["exclude"]
            and not r["archived"]]
    return keep


def readme_text(full_name: str) -> str:
    for name in ("README.md", "README.rst", "README.txt", "readme.md"):
        try:
            b64 = gh_json(f"repos/{full_name}/contents/{name}", ".content")
            import base64
            return base64.b64decode(b64).decode("utf-8", "replace")[:20000]
        except RuntimeError:
            continue
    return ""


def suggest_topics(name: str, desc: str, readme: str, base: list[str]) -> list[str]:
    hay = f" {name} {desc} {readme} ".lower().replace("-", " ")
    hits = [t for t, kws in VOCAB.items() if any(k in hay for k in kws)]
    # GitHub caps topics at 20; keep the sweep conservative and human-editable.
    return sorted(set(base + hits))[:12]


def link_papers(repos: list[dict], papers: list[dict]) -> dict[str, dict]:
    """Match repos to papers via HF's githubRepo field and name similarity."""
    by_repo: dict[str, dict] = {}
    for p in papers:
        url = p.get("hf_github_repo") or ""
        m = re.search(r"github\.com/([^/]+/[^/#?\s]+)", url)
        if m:
            by_repo[m.group(1).lower().removesuffix(".git")] = p
    out = {}
    for r in repos:
        p = by_repo.get(r["full_name"].lower())
        if p is None:
            # fall back to slug containment, e.g. repo 'zipnn' <-> paper slug 'zipnn-...'
            n = norm_title(r["name"])
            if len(n) >= 4:
                for cand in papers:
                    if n and n in norm_title(cand.get("title")):
                        p = cand
                        break
        if p:
            out[r["full_name"]] = p
    return out


def citation_cff(paper: dict, repo: dict, cfg) -> str:
    """CITATION.cff renders GitHub's 'Cite this repository' widget and is
    machine-readable, giving a bidirectional repo<->paper link."""
    ident = cfg["identity"]
    lines = ["cff-version: 1.2.0",
             'message: "If you use this software or its results, please cite the paper below."',
             "authors:"]
    for a in paper.get("authors") or [ident["name"]]:
        parts = a.split()
        given, family = " ".join(parts[:-1]) or parts[0], parts[-1]
        lines.append(f'  - given-names: "{given}"')
        lines.append(f'    family-names: "{family}"')
        if a == ident["name"] and ident.get("orcid"):
            lines.append(f'    orcid: "https://orcid.org/{ident["orcid"]}"')
    lines += [f'title: "{repo["name"]}"', "preferred-citation:",
              "  type: " + ("conference-paper" if paper.get("type") == "inproceedings"
                            else "article"),
              f'  title: "{(paper.get("title") or "").replace(chr(34), chr(39))}"',
              "  authors:"]
    for a in paper.get("authors") or [ident["name"]]:
        parts = a.split()
        lines.append(f'    - given-names: "{" ".join(parts[:-1]) or parts[0]}"')
        lines.append(f'      family-names: "{parts[-1]}"')
    if paper.get("year"):
        lines.append(f'  year: {paper["year"]}')
    if paper.get("venue"):
        lines.append(f'  collection-title: "{paper["venue"][:180].replace(chr(34), chr(39))}"')
    if paper.get("doi"):
        lines.append(f'  doi: "{paper["doi"]}"')
    if paper.get("arxiv"):
        lines.append(f'  url: "https://arxiv.org/abs/{paper["arxiv"]}"')
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------ phases

# Fields the human (or the model) owns. On re-propose these are carried forward
# from the existing repos.yaml rather than regenerated, so a rerun never clobbers
# a decision someone already made. Everything else is refreshed from GitHub.
_OWNED = ("description", "topics", "homepage", "kind", "generic_gloss",
          "write_citation_cff", "skip", "reviewed", "llm_proposal", "notes")


def phase_propose(cfg) -> None:
    """Refresh live GitHub state; preserve every human/model-owned field.

    Re-runnable: new repos get a fresh entry, existing entries keep their edits.
    This is why the sweep can be wired into a scheduled update without risk.
    """
    papers = (read_yaml(os.path.join(DATA, "papers.yaml")) or {}).get("papers", [])
    out = os.path.join(DATA, "repos.yaml")
    prior = {r["repo"]: r for r in (read_yaml(out) or {}).get("repos", [])}
    repos = list_repos(cfg)
    linked = link_papers(repos, papers)
    site = cfg["site"]["base_url"]
    proposal, added = [], []
    for r in sorted(repos, key=lambda r: -r["stargazers_count"]):
        was = prior.get(r["full_name"], {})
        p = linked.get(r["full_name"])
        entry = {
            # --- refreshed from GitHub every run ---
            "repo": r["full_name"],
            "stars": r["stargazers_count"],
            "current_description": r["description"],
            "current_topics": r["topics"],
            "current_homepage": r["homepage"] or None,
            "paper": p["title"] if p else was.get("paper"),
            "paper_slug": p["slug"] if p else was.get("paper_slug"),
        }
        # --- owned fields: carried forward, defaulted only when absent ---
        for f in _OWNED:
            if f in was:
                entry[f] = was[f]
        entry.setdefault("description", r["description"])
        entry.setdefault("topics", [])
        entry.setdefault("homepage", r["homepage"] or
                         (f"{site}/papers/{p['slug']}/" if p else None))
        entry.setdefault("write_citation_cff", bool(p))
        entry.setdefault("skip", False)
        entry.setdefault("reviewed", False)
        if not was:
            added.append(r["full_name"])
        proposal.append(entry)

    write_yaml(out, {
        "generated_by": "scripts/sweep_github.py propose",
        "note": ("Edit freely -- re-running propose preserves description, topics, "
                 "homepage, kind, skip and reviewed. Set `reviewed: true` to freeze "
                 "a repo against future model proposals. Then run: diff, apply."),
        "repos": proposal,
    })
    need_desc = [r["repo"] for r in proposal if not r.get("description")]
    no_topics = [r["repo"] for r in proposal if not r.get("topics")]
    print(f"wrote {out}: {len(proposal)} repos ({len(added)} new)")
    if added:
        print(f"  new since last run:  {', '.join(added)}")
    print(f"  linked to a paper:   {sum(1 for r in proposal if r.get('paper'))}")
    print(f"  reviewed (frozen):   {sum(1 for r in proposal if r.get('reviewed'))}")
    print(f"  still need topics:   {len(no_topics)}")
    print(f"  still need a description: {len(need_desc)}")
    if no_topics or need_desc:
        print("\nnext: python scripts/propose_topics.py")


def _changes(cfg):
    prop = (read_yaml(os.path.join(DATA, "repos.yaml")) or {}).get("repos", [])
    for r in prop:
        if r.get("skip"):
            continue
        ch = {}
        if r.get("topics") and sorted(r["topics"]) != sorted(r["current_topics"] or []):
            ch["topics"] = r["topics"]
        if r.get("description") and r["description"] != r["current_description"]:
            ch["description"] = r["description"]
        home = r.get("homepage")
        if home and home != r["current_homepage"]:
            site = cfg["site"]["base_url"] + cfg["site"]["papers_path"]
            page = os.path.join(BUILD, "site", "papers",
                                (r.get("paper_slug") or ""), "index.html")
            if home.startswith(site) and not os.path.exists(page):
                r.setdefault("_deferred", []).append(
                    "homepage: waiting on build_site.py to generate the paper page")
            else:
                ch["homepage"] = home
        if r.get("write_citation_cff") and r.get("paper_slug"):
            ch["CITATION.cff"] = r["paper_slug"]
        if ch:
            yield r, ch


def phase_diff(cfg) -> None:
    n = 0
    for r, ch in _changes(cfg):
        n += 1
        print(f"\n{r['repo']}  (★{r['stars']})")
        for k, v in ch.items():
            if k == "topics":
                cur = sorted(r["current_topics"] or [])
                print(f"  topics:      {cur or '[]'}  ->  {sorted(v)}")
            elif k == "CITATION.cff":
                print(f"  CITATION.cff: + cites '{r['paper'][:56]}'")
            else:
                print(f"  {k}: {r['current_' + k]!r}  ->  {v!r}")
    print(f"\n{n} repos would change. Nothing has been written.")


def phase_apply(cfg, yes: bool) -> None:
    if not yes:
        sys.exit("refusing to write to public repos without --yes")
    papers = {p["slug"]: p for p in
              (read_yaml(os.path.join(DATA, "papers.yaml")) or {}).get("papers", [])}
    repos = {r["full_name"]: r for r in list_repos(cfg)}
    for r, ch in _changes(cfg):
        name = r["repo"]
        try:
            if "topics" in ch:
                gh("api", "-X", "PUT", f"repos/{name}/topics",
                   "-f", "names[]=" + ",".join(ch["topics"]))
            patch = {k: ch[k] for k in ("description", "homepage") if k in ch}
            for k, v in patch.items():
                gh("api", "-X", "PATCH", f"repos/{name}", "-f", f"{k}={v}")
            if "CITATION.cff" in ch:
                p, repo = papers.get(r["paper_slug"]), repos.get(name)
                if p and repo:
                    body = citation_cff(p, repo, cfg)
                    path = os.path.join(BUILDCFF := os.path.join(DATA, "..", "build",
                                                                 "citation_cff"), f"{r['paper_slug']}.cff")
                    os.makedirs(BUILDCFF, exist_ok=True)
                    with open(path, "w") as f:
                        f.write(body)
                    gh("api", "-X", "PUT", f"repos/{name}/contents/CITATION.cff",
                       "-f", "message=Add CITATION.cff (paper-geo)",
                       "-f", f"content={__import__('base64').b64encode(body.encode()).decode()}")
            print(f"  ok  {name}: {', '.join(ch)}")
        except RuntimeError as e:
            print(f"  FAIL {name}: {e}", file=sys.stderr)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("phase", choices=["propose", "diff", "apply"])
    ap.add_argument("--yes", action="store_true", help="required for apply")
    a = ap.parse_args()
    cfg = load_config()
    {"propose": lambda: phase_propose(cfg),
     "diff": lambda: phase_diff(cfg),
     "apply": lambda: phase_apply(cfg, a.yes)}[a.phase]()


if __name__ == "__main__":
    main()
