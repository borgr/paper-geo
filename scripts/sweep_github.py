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
import base64
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (BUILD, DATA, ROOT, clean_latex, gh, gh_json, gh_text,  # noqa: E402
                    load_config, norm_title, paper_doi, read_papers, read_yaml, title_of,
                    write_task, write_yaml)

# Topics and descriptions are decided in `propose_topics.py`, not here. A reader auditing
# "how does a public topic get chosen?" opens this file first, which is why the note
# outlives the keyword table that used to sit here -- substring matching over name +
# description + README was also the wrong tool: `merg` matched *emergent*, `interpret`
# matched *interpreter*, and `training` matched every ML README there is.


def gh_or_none(*args: str) -> str | None:
    """`gh` output, or None where a 404 is the answer rather than a failure."""
    return gh_text(*args).strip() or None


def gh_topics_args(topics: list[str]) -> list[str]:
    """One -f per topic. A comma-joined value is rejected 422 by the endpoint,
    which validates each name individually. Asserted in validate.py selftest."""
    args = []
    for t in topics:
        args += ["-f", f"names[]={t}"]
    return args


def list_repos(cfg) -> list[dict]:
    user = cfg["ids"]["github"]
    out, page = [], 1
    while True:
        # `check=True` puts `gh`'s own reason in the log and is what keeps the line below
        # from reading a failed page as the last one. An empty return here means "you own no
        # repos", and a sweep over that changes nothing while reporting success.
        batch = gh_json("api", f"users/{user}/repos?per_page=100&page={page}", check=True)
        if not batch:
            break
        out += batch
        page += 1
    keep = [r for r in out
            if (cfg["github_sweep"]["include_forks"] or not r["fork"])
            and r["name"] not in cfg["github_sweep"]["exclude"]
            and not r["archived"]]
    return keep


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


def live_cff(name: str) -> str | None:
    """The repo's CITATION.cff exactly as it stands now, or None if it has none."""
    b = gh_or_none("api", f"repos/{name}/contents/CITATION.cff", "--jq", ".content")
    return base64.b64decode(b).decode("utf-8", "replace") if b else None


def _cff_str(v) -> str:
    """A YAML double-quoted scalar's contents: no LaTeX, no quote that would end it."""
    return clean_latex(str(v or "")).replace('"', "'")


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
              # `title_display` and `venue_display` are the de-LaTeXed forms the site
              # publishes; `title`/`venue` are the bibliography's, braces and all. This
              # file goes to a public repo and is parsed by GitHub, Zenodo and every
              # citation manager, so "{DORA} The Explorer" and "{ICLR} 2018" would have
              # shipped the brace convention into other people's bibliographies.
              f'  title: "{_cff_str(title_of(paper))}"',
              "  authors:"]
    for a in paper.get("authors") or [ident["name"]]:
        parts = a.split()
        lines.append(f'    - given-names: "{" ".join(parts[:-1]) or parts[0]}"')
        lines.append(f'      family-names: "{parts[-1]}"')
    if paper.get("year"):
        lines.append(f'  year: {paper["year"]}')
    if paper.get("venue") or paper.get("venue_display"):
        venue = _cff_str(paper.get("venue_display") or paper.get("venue"))
        lines.append(f'  collection-title: "{venue[:180]}"')
    if paper_doi(paper):
        lines.append(f'  doi: "{paper_doi(paper)}"')
    if paper.get("arxiv"):
        lines.append(f'  url: "https://arxiv.org/abs/{paper["arxiv"]}"')
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------ phases

# Fields the human (or the model) owns. On re-propose these are carried forward
# from the existing repos.yaml rather than regenerated, so a rerun never clobbers
# a decision someone already made. Everything else is refreshed from GitHub.
_OWNED = ("description", "topics", "declined_topics", "homepage", "kind",
          "generic_gloss", "write_citation_cff", "skip", "reviewed", "llm_proposal",
          "notes", "zenodo_doi")


# Repo kinds where a Zenodo DOI is the only citation route that will ever exist.
# A `paper-code` repo already has one -- the paper -- and a second citable object
# splits the citations it would have received, which is the argument against
# archiving code that a paper already covers. These have no paper to split from.
ZENODO_KINDS = {"tool", "guide"}


def zenodo_candidates(cfg) -> tuple[str, int]:
    """Repos worth a Zenodo DOI, which is a narrower set than "repos".

    The question is not "is this good work" but "if someone wanted to cite this, what would
    they cite". For a repo attached to a paper the answer exists. For a tool or guide with no
    paper there is none, and a Zenodo DOI creates one: a fixed version, an archived snapshot
    surviving a rename or deletion, and a DataCite record that propagates into OpenAlex and
    ORCID -- which puts the artifact in the same graph as the papers.

    Not automated further: Zenodo's GitHub integration only archives a *release*, so the human
    step is tagging one, and a repo you would not tag is a repo you should not archive.
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
         "Generated by `python scripts/sweep_github.py propose`.", "",
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
    write_task(path, L)
    return path, len(cand)


def phase_propose(cfg) -> None:
    """Refresh the repo LIST; store intent only.

    Observed GitHub state (stars, current description, current topics) is deliberately not
    stored: it already lives on GitHub, it changes constantly so storing it makes every run
    produce a noisy diff, and a stored copy goes stale -- `diff` would compare against a
    snapshot instead of reality. `diff` fetches live state when it runs.

    Re-runnable: new repos get a fresh entry, existing entries keep their edits.
    """
    papers = read_papers()
    out = os.path.join(DATA, "repos.yaml")
    prior = {r["repo"]: r for r in (read_yaml(out) or {}).get("repos", [])}
    repos = list_repos(cfg)
    linked = link_papers(repos, papers)
    site = cfg["site"]["base_url"]
    proposal, added, gone = [], [], []
    # By name, not by stars. Row *order* keyed on a live counter stores observed state
    # positionally, which the loop below already refuses to do when it drops `stars`. One repo
    # gaining a star rewrites the file as a 30-line move, so `git log data/repos.yaml` can no
    # longer answer "what changed about my repos". Nothing reads these rows positionally.
    for r in sorted(repos, key=lambda r: r["full_name"].lower()):
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
    # Reviewed and skipped rows are excluded, or the count could never reach zero. A settled
    # "nothing to say" -- the three early-exploratory repos, now `skip: true` with the reason
    # in `notes` -- reported as an open item forever is how a number stops being read.
    need = [r["repo"] for r in proposal
            if not r.get("reviewed") and not r.get("skip")
            and (not r.get("topics") or not r.get("description"))]
    print(f"  need topics or a description: {len(need)}")
    if need:
        print("\nnext: python scripts/propose_topics.py")


def _changes(cfg):
    """Yield (entry, live, changes) by comparing desired state to LIVE GitHub state."""
    prop = (read_yaml(os.path.join(DATA, "repos.yaml")) or {}).get("repos", [])
    live = {r["full_name"]: r for r in list_repos(cfg)}
    papers = {p["slug"]: p for p in read_papers()}
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
            # Rendered and compared, not announced: the flag says a file is wanted, not
            # that the one on the repo is wrong. Announcing on the flag alone made the
            # diff unable to ever reach zero -- so a run with nothing left to do looked
            # identical to a run with work in it -- and made every apply rewrite bytes
            # that already matched.
            p = papers.get(r["paper_slug"])
            if p:
                body = citation_cff(p, cur, cfg, r)
                if body != live_cff(r["repo"]):
                    ch["CITATION.cff"] = r["paper_slug"]
                    r["_cff_body"] = body
        if ch:
            yield r, cur, ch


def _provenance(r: dict, field: str) -> str:
    """Who wrote the value about to be published, and has anyone read it.

    The `--yes` flag is the only moment a person is in the loop, and until this was
    printed the diff showed the value without saying where it came from -- so the gate
    asked for a judgment while withholding the one fact the judgment turns on. `topics`
    and `description` are a model's prose; `homepage` and `CITATION.cff` are re-derived
    from `papers.yaml`, and reviewing those means reviewing the bibliography, not this.
    """
    if field not in ("topics", "description"):
        return ""
    if r.get("reviewed"):
        return "  [you edited this]"
    p = r.get("llm_proposal") or {}
    if (p.get(field) or None) is None:
        return ""
    return f"  [model, {p.get('confidence') or 'no confidence'}, unread]"


def phase_diff(cfg) -> None:
    # Materialized, not iterated twice: `_changes` re-lists every repo from the API.
    changes = list(_changes(cfg))
    n = 0
    for r, cur, ch in changes:
        n += 1
        print(f"\n{r['repo']}  (★{cur['stargazers_count']}, live)")
        for k, v in ch.items():
            src = _provenance(r, k)
            if k == "topics":
                print(f"  topics:      {sorted(cur['topics'] or []) or '[]'}  ->  "
                      f"{sorted(v)}{src}")
            elif k == "CITATION.cff":
                print(f"  CITATION.cff: + cites paper '{r['paper_slug']}'")
            elif k == "description":
                print(f"  description: {cur['description']!r}")
                print(f"            -> {v!r}{src}")
            else:
                print(f"  {k}: {cur.get(k)!r}  ->  {v!r}")
    unread = sum(1 for r, _, ch in changes
                 if any(_provenance(r, k).endswith("unread]") for k in ch))
    print(f"\n{n} repos would change. Nothing has been written.")
    if unread:
        # Said plainly rather than turned into a gate. A topic or a description is undone
        # by one API call and GitHub keeps no history of either, so the cost of a wrong
        # one is a minute; blocking on review instead would leave 29 of 31 repos
        # unlabelled indefinitely, which is the larger error. RUN.md §11 is where
        # that trade is written down.
        print(f"{unread} carry model-written text nobody has read. Publishing them is the "
              f"default; edit repos.yaml to change one, `reviewed: true` to freeze it.")


def phase_apply(cfg, yes: bool) -> None:
    if not yes:
        sys.exit("refusing to write to public repos without --yes")
    for r, cur, ch in _changes(cfg):
        name = r["repo"]
        # check=True on every write: a silent no-op here reports a repo as swept.
        try:
            if "topics" in ch:
                gh("api", "-X", "PUT", f"repos/{name}/topics",
                   *gh_topics_args(ch["topics"]), check=True)
            patch = {k: ch[k] for k in ("description", "homepage") if k in ch}
            for k, v in patch.items():
                gh("api", "-X", "PATCH", f"repos/{name}", "-f", f"{k}={v}",
                   check=True)
            if "CITATION.cff" in ch:
                body = r.get("_cff_body")
                if body:
                    path = os.path.join(BUILD, "citation_cff",
                                        f"{r['paper_slug']}.cff")
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                    with open(path, "w") as f:
                        f.write(body)
                    # The Contents API refuses a PUT over an existing file without its
                    # blob sha ("\"sha\" wasn't supplied", 422). Every write after the
                    # first one failed on that, which is how borgr/DORA kept a file with
                    # LaTeX braces in the title through the run that was meant to fix it.
                    sha = gh_or_none("api", f"repos/{name}/contents/CITATION.cff",
                                     "--jq", ".sha")
                    args = ["-f", f"message={'Update' if sha else 'Add'} CITATION.cff "
                            f"(paper-geo)",
                            "-f", f"content={base64.b64encode(body.encode()).decode()}"]
                    if sha:
                        args += ["-f", f"sha={sha}"]
                    gh("api", "-X", "PUT", f"repos/{name}/contents/CITATION.cff",
                       *args, check=True)
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
