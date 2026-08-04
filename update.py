#!/usr/bin/env python3
"""paper-geo: one command, re-runnable, safe to schedule.

    python update.py                 # refresh everything read-only, report what needs you
    python update.py --refresh-bib   # also re-run the publications pipeline first
    python update.py --apply         # additionally write the approved repo changes
    python update.py --step collect  # run a single step

Design rules, because this is meant to be re-run for years:

  * Read-only by default. Nothing leaves this machine unless you pass --apply.
  * Idempotent. Every step is safe to run twice; steps that would clobber a human
    decision read data/overrides.yaml (papers) or the `reviewed` flag (repos).
  * Degrading, not failing. A source outage costs one field, not the run.
  * New work surfaces itself. New papers and new repos appear in the report with
    what they still need, so a rerun months from now tells you what changed.

Mirrors the convention of borgr/publications/update.py: one master script that
runs the steps in order and then tells you what a human still has to do.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from common import DATA, load_config, read_yaml  # noqa: E402

STEPS = ("collect", "repos", "propose", "ownership", "validate", "worklist")


def run(argv: list[str], cwd: str | None = None) -> int:
    print(f"\n$ {' '.join(argv)}", flush=True)
    return subprocess.call(argv, cwd=cwd or ROOT)


def step_collect(cfg, args) -> None:
    """Rebuild data/papers.yaml from bibliography + S2 + arXiv + HF."""
    if args.refresh_bib:
        path = cfg["sources"].get("publications_path")
        if path and os.path.isdir(path):
            # publications owns the bibliography; let it refresh itself first so
            # newly-published venues land in enhanced.bib before we read it.
            run([sys.executable, "update.py"], cwd=path)
        else:
            print("  (sources.publications_path not set -- reading bib over HTTP)")
    run([sys.executable, "scripts/collect.py"])


def step_repos(cfg, args) -> None:
    """Refresh GitHub repo state, preserving prior edits."""
    run([sys.executable, "scripts/sweep_github.py", "propose"])


def step_propose(cfg, args) -> None:
    """Ask a model to label repos that still lack topics or a description."""
    run([sys.executable, "scripts/propose_topics.py"])


def step_ownership(cfg, args) -> None:
    """Reconcile with collaborators on who owns each paper's canonical page."""
    argv = [sys.executable, "scripts/ownership.py", "--manifest"]
    run(argv)


def step_validate(cfg, args) -> None:
    """Fail loudly on a malformed hand edit or a bad model proposal."""
    run([sys.executable, "scripts/validate.py"])


def step_worklist(cfg, args) -> None:
    """Report what only a human can do, ranked by citations."""
    papers = (read_yaml(os.path.join(DATA, "papers.yaml")) or {}).get("papers", [])
    repos = (read_yaml(os.path.join(DATA, "repos.yaml")) or {}).get("repos", [])
    ident, ids = cfg["identity"], cfg["ids"]

    def top(pred, n=8):
        return sorted([p for p in papers if pred(p)],
                      key=lambda p: -(p.get("citations") or 0))[:n]

    lines = ["# What still needs a human", "",
             "Regenerate with `python update.py`. Ordered by leverage.", ""]

    n_strays = sum(1 for p in papers
                    if p.get("s2_author_record") in
                    [a for a in ids["semantic_scholar"] if a != ids["semantic_scholar_primary"]])
    lines += [
        "## Once-only identity fixes",
        "",
        "Run `python scripts/identity_tasks.py` first -- it writes the payload for each",
        "of these into `tasks/` -- committed, so browsable on GitHub. Every one is",
        "blocked on a logged-in account you own, not on knowing what to do.",
        "",
        "### 1. Populate ORCID  — do this one first",
        "",
        f"`{ident['orcid']}` currently lists **0 works**. This is the highest-leverage",
        "item on the page, because it is also the lever for the other three: Semantic",
        "Scholar's disambiguation uses ORCID, and OpenAlex is actively running",
        "ORCID-driven merges of split profiles. Fixing ORCID makes both of those more",
        "likely to fix themselves, and keeps them fixed.",
        "",
        "Order matters, and the docs are easy to misread:",
        "",
        "1. **Turn on auto-update** for Crossref and DataCite — *Works → Search &",
        "   link*, authorise both, grant standing permission. Covers only works whose",
        "   deposited metadata already carries your iD, so this fixes the *future*.",
        "   Published DOIs are Crossref; arXiv DOIs are DataCite — you want both.",
        "2. **Link your arXiv account to ORCID** —",
        "   <https://arxiv.org/user/confirm_orcid_id>. This is what puts your iD into",
        "   arXiv's DataCite metadata, which is what makes step 1 work on future",
        "   preprints.",
        "3. **Fill the backlog.** *Add DOI* is the reliable route: it resolves",
        "   server-side against Crossref/DataCite and creates a properly-sourced work.",
        f"   `tasks/orcid_dois.txt` has the {sum(1 for p in papers if p.get('doi'))} DOIs,",
        "   citation-ordered, so stopping early still captures most of the value.",
        "4. **Or bulk-import** `tasks/orcid_import.bib` via *Add works → Add BibTeX*.",
        "   Less risky than it first appears: ORCID **groups works that share an",
        "   identifier**, so a DOI-bearing entry merges with the registry copy when",
        "   auto-update later finds it rather than showing as a duplicate. The file is",
        "   split — DOI-bearing entries first, then the few without a DOI, which are",
        "   the only ones with nothing to group on.",
        "",
        "**If the wizards misbehave, that is expected, not you:** the *Crossref",
        "Metadata Search* wizard is genuinely flaky and hangs. *Scopus* looks empty",
        "because Scopus indexes little arXiv/ACL content and the wizard wants a Scopus",
        "Author ID you may not have. **dblp has no connect button because dblp is not",
        "an ORCID wizard** — it only ingests iDs harvested from publisher metadata and",
        "the ORCID dump, and never pushes works out. Skip all three and use *Add DOI*",
        "or the BibTeX import.",
        "",
        "I cannot do this for you: writing to an ORCID record needs an OAuth token with",
        "`/activities/update` scope, which only you can grant. The public API is",
        "read-only.",
        "",
        f"### 2. Semantic Scholar — {n_strays} papers on the wrong record",
        "",
        f"Claimed: <https://www.semanticscholar.org/author/{ids['semantic_scholar_primary']}>  ",
        " ".join(f"Secondary: <https://www.semanticscholar.org/author/{a}>"
                 for a in ids["semantic_scholar"]
                 if a != ids["semantic_scholar_primary"]),
        "",
        "**Do we have to?** It is the single biggest retrieval loss on this page: every",
        "Semantic-Scholar-backed tool — Elicit, Consensus, SciSpace, most literature",
        "agents — resolves an author to one page, so each of them currently sees about",
        "half your corpus and ranks both halves lower.",
        "",
        "**Is there a way, given support ignored you?** Yes, and it does not need them.",
        "There is no self-service *merge*, but a claimed page can pull papers across:",
        "",
        "1. Open the claimed page → **Edit Author Page** → **Add Papers**.",
        "2. Paste the paper's S2 URL, select it, choose *the author is correct, but the*",
        "   *paper is missing from my author page*, Submit. ~24h to appear.",
        "3. Repeat. `tasks/s2_merge.md` lists all of them citation-ordered with URLs,",
        "   so stopping early still captures most of the loss.",
        "",
        "Do **not** claim the second page as well — their docs prohibit holding two",
        "claims, and it makes the split harder to undo later. If you want to chase",
        "support again, the durable argument is the ORCID: quote it and ask them to",
        "merge on that basis.",
        "",
        "### 3. Create a Wikidata item",
        "",
        "**Is this an acceptable use?** Yes. Wikidata's notability policy is not",
        "Wikipedia's: criterion 2 admits any *clearly identifiable entity describable",
        "with serious, publicly available references*, and criterion 3 admits items that",
        "*fulfil a structural need* — which is exactly what an author item with an ORCID",
        "and published papers is. Hundreds of thousands of researcher items exist,",
        "mostly auto-created from ORCID and Crossref. Unlike Wikipedia there is no",
        "prohibition on creating an item about yourself; the requirement is accuracy,",
        "not distance. `tasks/wikidata.qs` therefore contains identifiers and",
        "affiliations only — no claims about importance, nothing unsourced.",
        "",
        "**What I need from you:** a logged-in Wikidata account. Then:",
        "",
        "1. Log in at <https://www.wikidata.org>.",
        "2. Open <https://quickstatements.toolforge.org/#/batch>, authorise it once.",
        "3. Paste `tasks/wikidata.qs`, run it, and copy the new Q-number.",
        "4. Put that Q-number in `config.yaml` → `ids.wikidata` and redeploy; it then",
        "   appears in the site's `sameAs` array.",
        "",
        "**Why it is not automatic:** Wikidata writes require an authenticated account,",
        "and an unattended bot account needs community approval. Creating an item about",
        "yourself should also be a decision you make knowingly rather than one a script",
        "makes for you.",
        "",
        f"### 4. OpenAlex — {len(ids.get('openalex_duplicates') or [])} duplicate profiles",
        "",
        "Lowest priority: the duplicates hold a handful of works between them against",
        "140+ on the main profile, so this is tidying.",
        "",
        "**Preferred route: do nothing here and fix ORCID.** OpenAlex disambiguation is",
        "ORCID-driven and they are currently running ORCID-based merges of split",
        "profiles, so this may resolve itself.",
        "",
        "**If you want it now:** the *Fixing Author Profiles* form linked from",
        "<https://help.openalex.org/hc/en-us/articles/27714298573719-Fix-errors-in-OpenAlex>",
        "can merge profiles, set the display name, and remove wrong works.",
        "`tasks/openalex_merge.md` has the exact profile IDs to paste.",
        "`support@openalex.org` is the fallback.",
        "",
    ]
    missing_jr = top(lambda p: p.get("arxiv") and not p.get("arxiv_journal_ref"), 12)
    if missing_jr:
        lines += [f"## arXiv journal-ref missing ({sum(1 for p in papers if p.get('arxiv') and not p.get('arxiv_journal_ref'))} papers)",
                  "",
                  "Scholar matches citations and merges preprint/published versions on exactly "
                  "these fields. No write API -- one web form each, so do them by citation count.",
                  ""]
        for p in missing_jr:
            venue = (p.get("venue") or "?")[:52]
            lines.append(f"- [ ] `{p['arxiv']}` ({p.get('citations') or 0} cites) -> {venue}  "
                         f"<https://arxiv.org/abs/{p['arxiv']}>")
        lines.append("")

    no_hf = top(lambda p: p.get("arxiv") and p.get("hf_indexed") is False, 10)
    if no_hf:
        lines += [f"## Hugging Face paper page missing ({sum(1 for p in papers if p.get('hf_indexed') is False and p.get('arxiv'))})",
                  "",
                  "Reflects the last `collect.py` run -- re-run it before working this",
                  "list or you will redo what you already did.",
                  "",
                  "`python scripts/hf_papers.py` writes a clickable list to",
                  "`build/hf_worklist.html`. An unauthenticated visit creates nothing",
                  "(verified: 0 of 50), so log in to Hugging Face first, then click",
                  "through. Afterwards: `python scripts/hf_papers.py --verify`.",
                  ""]
        for p in no_hf:
            lines.append(f"- [ ] <https://hf.co/papers/{p['arxiv']}>  ({p.get('citations') or 0} cites)")
        lines.append("")

    unclaimed = top(lambda p: p.get("hf_indexed") and not p.get("hf_claimed_by_me"), 10)
    if unclaimed:
        lines += [f"## Hugging Face page indexed but not claimed by you ({sum(1 for p in papers if p.get('hf_indexed') and not p.get('hf_claimed_by_me'))})",
                  "",
                  "Claims need admin approval, so a request you have already submitted",
                  "still shows here until it is validated -- your name will have no",
                  "linked user until then. Re-run `collect.py` before assuming one",
                  "failed.",
                  ""]
        for p in unclaimed:
            lines.append(f"- [ ] <https://hf.co/papers/{p['arxiv']}>  ({p.get('citations') or 0} cites)")
        lines.append("")

    review = [p for p in papers if p.get("similar_but_distinct")]
    if review:
        lines += ["## Same paper or different? (decide once in data/overrides.yaml)", ""]
        for p in review:
            for o in p["similar_but_distinct"]:
                lines.append(f"- [ ] `{p['title'][:64]}`  vs  `{o[:64]}`")
        lines.append("")

    no_side = [p for p in papers if not p.get("has_sidecar")]
    if no_side:
        lines += [f"## Sidecars not written ({len(no_side)}/{len(papers)})", "",
                  "The one input no tool can supply: claims, scope conditions, terminology, "
                  "common misreadings. ~10 min each; do them by citation count.", ""]
        for p in sorted(no_side, key=lambda p: -(p.get("citations") or 0))[:10]:
            lines.append(f"- [ ] `data/sidecars/{p['slug']}.md`  ({p.get('citations') or 0} cites) "
                         f"{p['title'][:56]}")
        lines.append("")

    pend = [r for r in repos if not r.get("reviewed") and not r.get("skip")]
    if pend:
        lines += [f"## Repo labels awaiting your review ({len(pend)}/{len(repos)})", "",
                  "Check `data/repos.yaml`, fix anything wrong, set `reviewed: true` to freeze "
                  "it, then `python scripts/sweep_github.py diff`.", ""]

    out = os.path.join(ROOT, "WORKLIST.md")
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nwrote {out}")
    print("\n".join(l for l in lines if l.startswith("## ")))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", choices=STEPS, help="run one step instead of all")
    ap.add_argument("--refresh-bib", action="store_true",
                    help="run the publications pipeline first (needs sources.publications_path)")
    ap.add_argument("--apply", action="store_true",
                    help="also push approved repo changes to GitHub")
    args = ap.parse_args()
    cfg = load_config()

    fns = {"collect": step_collect, "repos": step_repos, "propose": step_propose,
           "ownership": step_ownership, "validate": step_validate,
           "worklist": step_worklist}
    for name in ([args.step] if args.step else STEPS):
        print(f"\n{'=' * 62}\n== {name}\n{'=' * 62}")
        fns[name](cfg, args)

    if args.apply:
        print(f"\n{'=' * 62}\n== apply (writes to GitHub)\n{'=' * 62}")
        run([sys.executable, "scripts/sweep_github.py", "apply", "--yes"])
    else:
        print("\nRead-only run. Review data/repos.yaml and WORKLIST.md, then:")
        print("  python scripts/sweep_github.py diff      # see exactly what would change")
        print("  python update.py --apply                 # write it")


if __name__ == "__main__":
    main()
