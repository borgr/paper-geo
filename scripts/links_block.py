#!/usr/bin/env python3
"""Maintain a generated links block in paper-code READMEs.

Three reasons a repo should carry the paper's whole link set, not just an arXiv
link: Hugging Face extracts the arXiv id and auto-cross-lists the repo on the
paper page; GitHub is heavily crawled, so a README link to the canonical paper
page is a real retrieval edge; and asserting the same link set on a second
high-authority domain is the corroboration mechanism.

The block lives between markers so it regenerates without touching hand-written
prose. Where the same paper has repos owned by several people, every block points
at the SAME canonical page -- never one page per owner.

    propose -> build/readme_blocks/<repo>.md   (review these)
    diff    -> show what would change
    apply   -> commit to each repo (requires --yes)

Usage:
    python scripts/links_block.py propose
    python scripts/links_block.py diff
    python scripts/links_block.py apply --yes
"""
from __future__ import annotations

import argparse
import base64
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_site import LINK_LABELS, read_sidecar  # noqa: E402
from common import BUILD, DATA, gh, load_config, read_yaml  # noqa: E402

START = "<!-- paper-geo:links:start -->"
END = "<!-- paper-geo:links:end -->"
OUT = os.path.join(BUILD, "readme_blocks")
ORDER = ["paper_page", "arxiv", "html", "doi", "acl_anthology", "publisher",
         "huggingface", "semantic_scholar", "alphaxiv", "arxiv_pdf", "code",
         "data", "models", "project", "video", "slides", "poster", "leaderboard",
         "demo"]


def render(p: dict, sc: dict, cfg) -> str:
    """The block. Claim sentence first, then links, then the citation."""
    links = dict(p.get("links") or {})
    links.update(sc.get("links_extra") or {})
    # The canonical page: ours, or a collaborator's if they own it.
    page = p.get("canonical_page") or (
        cfg["site"]["base_url"].rstrip("/") + cfg["site"]["papers_path"]
        + f"/{p['slug']}/")
    links["paper_page"] = page
    LINK_LABELS.setdefault("paper_page", "Paper page")

    L = [START, "", f'## {p.get("title_display") or p["title"]}', ""]
    if sc.get("one_liner"):
        # Verbatim from the sidecar, never reworded: the same sentence on a second
        # domain is corroboration; a paraphrase is a competing near-duplicate.
        L += [" ".join(sc["one_liner"].split()), ""]
    elif p.get("venue"):
        L += [f"Published in {p.get('venue_display') or p['venue']}"
              + (f" ({p['year']})." if p.get("year") else "."), ""]
    ordered = [k for k in ORDER if k in links] + \
              [k for k in links if k not in ORDER and k != "html_source"]
    L.append(" · ".join(f"[{LINK_LABELS.get(k, k)}]({links[k]})" for k in ordered))
    if p.get("bibtex"):
        L += ["", "<details><summary>Cite</summary>", "",
              "```bibtex", p["bibtex"].strip(), "```", "", "</details>"]
    L += ["", END]
    return "\n".join(L)


def splice(readme: str, block: str) -> str:
    """Insert or replace the block, leaving everything else byte-identical."""
    if START in readme and END in readme:
        return re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block,
                      readme, flags=re.S)
    if not readme.strip():
        return block + "\n"
    # After the first heading if there is one, else at the top.
    lines = readme.split("\n")
    for i, ln in enumerate(lines):
        if ln.startswith("# "):
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            return "\n".join(lines[:j] + [block, ""] + lines[j:])
    return block + "\n\n" + readme


def targets(cfg):
    papers = {p["slug"]: p for p in
              (read_yaml(os.path.join(DATA, "papers.yaml")) or {})["papers"]}
    for r in (read_yaml(os.path.join(DATA, "repos.yaml")) or {}).get("repos", []):
        if r.get("skip") or not r.get("write_links_block"):
            continue
        p = papers.get(r.get("paper_slug") or "")
        if p:
            yield r, p


def fetch_readme(repo: str) -> tuple[str, str | None]:
    for name in ("README.md", "readme.md", "README.rst"):
        code, out = gh("api", f"repos/{repo}/contents/{name}", "-q", ".content+\"|\"+.sha")
        if code == 0 and "|" in out:
            b64, sha = out.rsplit("|", 1)
            return base64.b64decode(b64).decode("utf-8", "replace"), sha.strip()
    return "", None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("phase", choices=["propose", "diff", "apply"])
    ap.add_argument("--yes", action="store_true")
    a = ap.parse_args()
    cfg = load_config()
    os.makedirs(OUT, exist_ok=True)
    n = 0

    for r, p in targets(cfg):
        repo = r["repo"]
        block = render(p, read_sidecar(p["slug"]), cfg)
        if a.phase == "propose":
            path = os.path.join(OUT, repo.replace("/", "__") + ".md")
            with open(path, "w") as f:
                f.write(block + "\n")
            print(f"  {repo} -> {path}")
            n += 1
            continue

        readme, sha = fetch_readme(repo)
        new = splice(readme, block)
        if new == readme:
            continue
        n += 1
        if a.phase == "diff":
            had = START in readme
            print(f"\n{repo}  ({'update' if had else 'insert'} block, "
                  f"README {'exists' if sha else 'MISSING -- would be created'})")
            for ln in block.split("\n")[:9]:
                print(f"  + {ln}")
            print("  + ...")
        else:
            if not a.yes:
                sys.exit("refusing to write to public repos without --yes")
            args = ["api", "-X", "PUT", f"repos/{repo}/contents/README.md",
                    "-f", "message=Add paper links block (paper-geo)",
                    "-f", "content=" + base64.b64encode(new.encode()).decode()]
            if sha:
                args += ["-f", f"sha={sha}"]
            code, out = gh(*args)
            print(f"  {'ok  ' if code == 0 else 'FAIL'} {repo}"
                  + ("" if code == 0 else f": {out.strip()[:120]}"))

    if a.phase == "propose":
        print(f"\nwrote {n} block(s) to {OUT}. Review, then: diff, apply --yes")
    elif a.phase == "diff":
        print(f"\n{n} README(s) would change. Nothing has been written.")


if __name__ == "__main__":
    main()
