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
from common import (BUILD, DATA, ROOT, load_config, norm_title, paper_doi,  # noqa: E402
                    read_yaml, write_yaml)

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


def gh_topics_args(topics: list[str]) -> list[str]:
    """One -f per topic. A comma-joined value is rejected 422 by the endpoint,
    which validates each name individually. Asserted in validate.py selftest."""
    args = []
    for t in topics:
        args += ["-f", f"names[]={t}"]
    return args


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


def citation_cff(paper: dict, repo: dict, cfg, entry: dict | None = None) -> str:
    """CITATION.cff renders GitHub's 'Cite this repository' widget and is
    machine-readable, giving a bidirectional repo<->paper link.

    `repo` is live GitHub state; `entry` is the repos.yaml intent, which is where a
    hand-recorded Zenodo DOI lives. Two arguments rather than one because only the
    second survives a rerun.
    """
    entry = entry or {}
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
    lines.append(f'title: "{repo["name"]}"')
    # The repo's own DOI at top level, the paper's under preferred-citation. Both,
    # not one: the widget hands out the paper citation, which is what you want cited,
    # while the concept DOI still makes the software itself resolvable and archived.
    if entry.get("zenodo_doi"):
        lines.append(f'doi: "{entry["zenodo_doi"]}"')
    lines += ["preferred-citation:",
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
    if paper_doi(paper):
        lines.append(f'  doi: "{paper_doi(paper)}"')
    if paper.get("arxiv"):
        lines.append(f'  url: "https://arxiv.org/abs/{paper["arxiv"]}"')
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------ phases

# Fields the human (or the model) owns. On re-propose these are carried forward
# from the existing repos.yaml rather than regenerated, so a rerun never clobbers
# a decision someone already made. Everything else is refreshed from GitHub.
_OWNED = ("description", "topics", "homepage", "kind", "generic_gloss",
          "write_citation_cff", "skip", "reviewed", "llm_proposal", "notes",
          "zenodo_doi")


# Repo kinds where a Zenodo DOI is the only citation route that will ever exist.
# A `paper-code` repo already has one -- the paper -- and a second citable object
# splits the citations it would have received, which is the argument against
# archiving code that a paper already covers. These have no paper to split from.
ZENODO_KINDS = {"tool", "guide"}


def zenodo_candidates(cfg) -> tuple[str, int]:
    """Repos worth a Zenodo DOI, which is a narrower set than "repos".

    The useful question is not "is this good work" but "if someone wanted to cite
    this, what would they cite". For a repo attached to a paper the answer already
    exists. For a tool or a guide with no paper there is no answer at all, and a
    Zenodo DOI is what creates one: a fixed version, an archived snapshot that
    survives the repo being renamed or deleted, and a DataCite record that
    propagates into OpenAlex and ORCID -- which is the part that matters here,
    because it puts the artifact in the same graph as your papers instead of in a
    separate one that only GitHub can see.

    Deliberately not automated further. Zenodo's GitHub integration only archives a
    *release*, so the human step is tagging one, and a repo you would not tag is a
    repo you should not archive.
    """
    repos = (read_yaml(os.path.join(DATA, "repos.yaml")) or {}).get("repos", [])
    cand = [r for r in repos
            if not r.get("skip") and not r.get("paper_slug")
            and r.get("kind") in ZENODO_KINDS
            and not r.get("zenodo_doi")]
    tasks = os.path.join(ROOT, "tasks")
    os.makedirs(tasks, exist_ok=True)
    path = os.path.join(tasks, "zenodo.md")
    L = ["# Zenodo: give the artifacts with no paper a citable identity", "",
         f"{len(cand)} repos qualify. The filter is `kind` in "
         f"{sorted(ZENODO_KINDS)} **and** no linked paper: a repo whose paper exists",
         "already has a citation route, and minting a second one splits the citations",
         "between two identifiers.", "",
         "Whether anyone cites a tool or a guide is a fair objection, and the honest",
         "answer is that some will not. The DOI still does two things that do not",
         "depend on being cited: it makes the artifact resolvable after the repo moves",
         "or disappears, and it puts a record into DataCite, which flows to OpenAlex",
         "and to your ORCID works list — so the artifact joins the same graph as your",
         "papers rather than living only on GitHub.", "",
         "Do this once per repo, at a moment when it is in a state you would not mind",
         "being permanent — the archive is a snapshot of the release, not of `main`:",
         "", "1. <https://zenodo.org/account/settings/github/> — sign in **with GitHub**",
         "   (a separate Zenodo account cannot see your repos), flip the repo on.",
         "2. Tag a release on GitHub. Nothing is archived until you do; the switch only",
         "   arms the webhook.",
         "3. Zenodo mints two DOIs. Use the **concept DOI** everywhere — it always",
         "   resolves to the newest version, so it does not go stale on the next release.",
         "4. Fix the record's metadata once: authors with ORCIDs, a license, and the",
         "   repo URL under *Related identifiers*.",
         "5. Put the concept DOI in `data/repos.yaml` as `zenodo_doi:` — that both",
         "   removes it from this list and lets `CITATION.cff` carry it.", ""]
    for r in cand:
        L.append(f"- [ ] **{r['repo']}** ({r.get('kind')}) — "
                 f"{(r.get('description') or '')[:80]}")
    if not cand:
        L.append("Nothing outstanding.")
    with open(path, "w") as f:
        f.write("\n".join(L) + "\n")
    return path, len(cand)


def phase_propose(cfg) -> None:
    """Refresh the repo LIST; store intent only.

    Observed GitHub state (stars, current description, current topics) is
    deliberately NOT stored. It already lives on GitHub, it changes constantly --
    so storing it makes every run produce a noisy diff -- and a stored copy goes
    stale, which means `diff` would compare against a snapshot instead of reality.
    `diff` fetches live state at the moment it runs.

    Re-runnable: new repos get a fresh entry, existing entries keep their edits.
    """
    papers = (read_yaml(os.path.join(DATA, "papers.yaml")) or {}).get("papers", [])
    out = os.path.join(DATA, "repos.yaml")
    prior = {r["repo"]: r for r in (read_yaml(out) or {}).get("repos", [])}
    repos = list_repos(cfg)
    linked = link_papers(repos, papers)
    site = cfg["site"]["base_url"]
    proposal, added, gone = [], [], []
    for r in sorted(repos, key=lambda r: -r["stargazers_count"]):
        name = r["full_name"]
        entry = dict(prior.get(name) or {})
        entry["repo"] = name
        p = linked.get(name)
        if p:
            entry["paper_slug"] = p["slug"]
        entry.setdefault("description", r["description"])
        entry.setdefault("topics", [])
        entry.setdefault("homepage", r["homepage"] or
                         (f"{site}/papers/{p['slug']}/" if p else None))
        entry.setdefault("write_citation_cff", bool(p))
        entry.setdefault("write_links_block", bool(p))
        entry.setdefault("skip", False)
        entry.setdefault("reviewed", False)
        # Drop observed-state fields left over from older runs of this script.
        for stale in ("stars", "current_description", "current_topics",
                      "current_homepage", "paper"):
            entry.pop(stale, None)
        if name not in prior:
            added.append(name)
        proposal.append(entry)
    gone = [n for n in prior if n not in {r["repo"] for r in proposal}]

    write_yaml(out, {
        "generated_by": "scripts/sweep_github.py propose",
        "note": ("Desired state, not observed state -- live GitHub values are fetched "
                 "at diff time. Edit freely; re-running propose preserves every field "
                 "here. Set `reviewed: true` to freeze a repo against future model "
                 "proposals. Schema: schema/repos.schema.json"),
        "repos": proposal,
    })
    print(f"wrote {out}: {len(proposal)} repos ({len(added)} new)")
    if added:
        print(f"  new since last run: {', '.join(added)}")
    if gone:
        print(f"  no longer present (kept in file): {', '.join(gone)}")
    print(f"  reviewed (frozen):  {sum(1 for r in proposal if r.get('reviewed'))}")
    zpath, nz = zenodo_candidates(cfg)
    print(f"  artifacts with no citation route: {nz} -> {os.path.relpath(zpath, ROOT)}")
    need = [r["repo"] for r in proposal if not r.get("topics") or not r.get("description")]
    print(f"  need topics or a description: {len(need)}")
    if need:
        print("\nnext: python scripts/propose_topics.py")


def _changes(cfg):
    """Yield (entry, live, changes) by comparing desired state to LIVE GitHub state."""
    prop = (read_yaml(os.path.join(DATA, "repos.yaml")) or {}).get("repos", [])
    live = {r["full_name"]: r for r in list_repos(cfg)}
    for r in prop:
        cur = live.get(r["repo"])
        if r.get("skip") or cur is None:
            continue
        ch = {}
        if r.get("topics") and sorted(r["topics"]) != sorted(cur["topics"] or []):
            ch["topics"] = r["topics"]
        if r.get("description") and r["description"] != cur["description"]:
            ch["description"] = r["description"]
        home = r.get("homepage")
        if home and home != (cur["homepage"] or None):
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
            yield r, cur, ch


def phase_diff(cfg) -> None:
    n = 0
    for r, cur, ch in _changes(cfg):
        n += 1
        print(f"\n{r['repo']}  (★{cur['stargazers_count']}, live)")
        for k, v in ch.items():
            if k == "topics":
                print(f"  topics:      {sorted(cur['topics'] or []) or '[]'}  ->  {sorted(v)}")
            elif k == "CITATION.cff":
                print(f"  CITATION.cff: + cites paper '{r['paper_slug']}'")
            elif k == "description":
                print(f"  description: {cur['description']!r}")
                print(f"            -> {v!r}")
            else:
                print(f"  {k}: {cur.get(k)!r}  ->  {v!r}")
    print(f"\n{n} repos would change. Nothing has been written.")


def phase_apply(cfg, yes: bool) -> None:
    if not yes:
        sys.exit("refusing to write to public repos without --yes")
    papers = {p["slug"]: p for p in
              (read_yaml(os.path.join(DATA, "papers.yaml")) or {}).get("papers", [])}
    repos = {r["full_name"]: r for r in list_repos(cfg)}
    for r, cur, ch in _changes(cfg):
        name = r["repo"]
        try:
            if "topics" in ch:
                gh("api", "-X", "PUT", f"repos/{name}/topics",
                   *gh_topics_args(ch["topics"]))
            patch = {k: ch[k] for k in ("description", "homepage") if k in ch}
            for k, v in patch.items():
                gh("api", "-X", "PATCH", f"repos/{name}", "-f", f"{k}={v}")
            if "CITATION.cff" in ch:
                p, repo = papers.get(r["paper_slug"]), repos.get(name)
                if p and repo:
                    body = citation_cff(p, repo, cfg, r)
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
