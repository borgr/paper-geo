#!/usr/bin/env python3
"""paper-geo: one command, re-runnable, safe to schedule.

    python update.py                 # refresh everything read-only, report what needs you
    python update.py --refresh-bib   # also re-run the publications pipeline first
    python update.py --apply         # additionally write the approved repo and link changes
    python update.py --step collect  # run a single step

Setting this up was the one-time cost. The steady state is this command: code
refreshes everything derivable, a model drafts what needs judgement, and the run
ends by handing one link to a human. Who does what, and why:

  * Code, no human in it: collect, repos, links, ownership, audit, validate, render.
    All of it is re-derived from public sources, so a human in the loop would be a
    human retyping what a fetch already knows.
  * A model's judgement, handed back rather than published: propose (repo labels)
    and draft (sidecars). Both write to places nothing reads until promoted.
  * Reserved for the author, and only these two: accepting a sidecar draft, which
    publishes an assertion under the author's name, and any write that leaves
    this machine.

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
import glob
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from common import DATA, is_preprint_venue, load_config, read_yaml  # noqa: E402
from sweep_github import ZENODO_KINDS  # noqa: E402

STEPS = ("collect", "repos", "propose", "draft", "links", "ownership", "audit",
         "validate", "render", "worklist")


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


def step_draft(cfg, args) -> None:
    """Draft sidecars for the next batch of papers that have none.

    Batched rather than exhaustive, at `--draft-batch` papers per run. Drafting is the
    one step with a real per-paper cost -- it fetches each paper's rendered full text
    -- and an unbounded first run would fetch a hundred of them in one go. A bounded
    batch makes the number fall on its own across runs and keeps a new paper's draft
    arriving automatically, which is the property that matters for a pipeline meant to
    be re-run for years.
    """
    if args.draft_batch <= 0:
        print("  (skipped: --draft-batch 0)")
        return
    run([sys.executable, "scripts/draft_sidecars.py",
         "--limit", str(args.draft_batch)])


def step_links(cfg, args) -> None:
    """Deduce each paper's code repo and project page from its own full text.

    Read-only here: it refreshes `data/paper_code.yaml` and reports what it would
    publish to Hugging Face, but nothing leaves the machine without --apply. Placed
    after `draft` so it reuses the full text that step just cached, though it will
    fetch its own for a paper the batch has not reached yet.
    """
    run([sys.executable, "scripts/paper_code.py"])


def step_ownership(cfg, args) -> None:
    """Reconcile with collaborators on who owns each paper's canonical page."""
    argv = [sys.executable, "scripts/ownership.py", "--manifest"]
    run(argv)


def step_audit(cfg, args) -> None:
    """Live-read the identity surfaces we do not control and regenerate the payloads.

    Runs the Hugging Face pass too, even though collect.py just fetched the same
    pages. The duplication costs ~30s in a multi-minute run and buys the guarantee
    that the two hand-worked lists came from one moment in time; deciding at read
    time which of two differently-aged sources is fresher is how a worklist starts
    sending you back to pages you already did.

    The Scholar diff belongs here rather than in `collect`, because it audits the
    collector's *output* against a list the collector cannot see. Its whole job is to
    catch what no self-consistency check can: a paper that never entered, and a paper
    the authorship gate dropped. Report-only, and it never stops the run -- Google has
    no API for this and answers a crawler with a challenge page often enough that
    treating a bad afternoon as a failed run would be wrong.
    """
    run([sys.executable, "scripts/audit_identity.py"])
    run([sys.executable, "scripts/scholar_check.py"])
    run([sys.executable, "scripts/identity_tasks.py"])


def step_validate(cfg, args) -> None:
    """Fail loudly on a malformed hand edit or a bad model proposal.

    Fixes the corpus sizes stated in the docs rather than reporting them: one new
    paper made seven prose sentences wrong at once, which is a chore, not a
    judgement. The three sentences whose count feeds a sum are still reported,
    because there the arithmetic has to be redone by someone who can read it.

    The only step that can stop the run, and only on a structural failure: `render`
    and `worklist` both read `data/` and present it, so a schema violation or a
    dangling claim id would otherwise become a page that looks reviewable. A stale
    count in a prose sentence exits 0 and the run continues.
    """
    if run([sys.executable, "scripts/validate.py", "--fix-counts"]):
        raise SystemExit("\nvalidate failed -- fix the problems above and re-run. "
                         "Nothing after this step is trustworthy.")


def step_render(cfg, args) -> None:
    """Rebuild the local site, so the run ends in something a human can look at.

    A local write only: `build/site/` is regenerated from `data/` every time, and
    publishing stays a separate explicit `build_site.py --deploy`. It belongs in the
    loop because every other step ends in a file *about* the corpus, and this one ends
    in the corpus as a reader meets it -- which is the artifact worth handing back.
    Rendering after `validate` is deliberate: a schema failure should stop the run
    before it produces a page that looks reviewable.
    """
    run([sys.executable, "scripts/build_site.py"])


def due_followups() -> list[str]:
    """Surface anything in data/followups.yaml that has come due.

    The reminder problem, solved the only way that survives: the next run is the
    reminder. A cron entry or a chat reminder lives in one process and dies with it,
    and a calendar entry keeps the date but loses the reason -- which for these items
    is the whole content, since each one is "the wait is over, so now X is possible".
    Here the date and the reason are in the repo together, and every `update.py`
    checks them.

    Items not yet due are listed too, compactly. Knowing that nothing is due *and*
    what is coming is the difference between a clear page and a page that is merely
    silent.
    """
    import datetime
    items = (read_yaml(os.path.join(DATA, "followups.yaml")) or {}).get("followups") or []
    if not items:
        return []
    today = datetime.date.today()

    def as_date(v):
        return v if isinstance(v, datetime.date) else datetime.date.fromisoformat(str(v))

    due = sorted((i for i in items if as_date(i["due"]) <= today), key=lambda i: i["due"])
    later = sorted((i for i in items if as_date(i["due"]) > today), key=lambda i: i["due"])
    out = []
    # `owner: agent` items are separated out rather than listed with the rest. They are
    # not tasks for the reader -- they need a date to have passed and then a pipeline
    # run, no decision -- and mixing the two kinds is how a checklist teaches its reader
    # that most lines on it are not for them.
    for owner, head, blurb in (
            ("human", "Due now", "Each of these was waiting on something outside this "
                                 "repo that should have landed by now."),
            ("agent", "Due now — for the pipeline, not for you",
             "Unblocked by the calendar, not by a decision. Say the word, or they run "
             "on the next pass; nothing here needs you except a look at the result.")):
        group = [i for i in due if (i.get("owner") or "human") == owner]
        if not group:
            continue
        out += [f"## {head} ({len(group)})", "",
                f"From `data/followups.yaml`. {blurb}", ""]
        for i in group:
            d = as_date(i["due"])
            out += [f"- [ ] **{d.isoformat()}** ({(today - d).days} days ago) — "
                    f"{' '.join(str(i['what']).split())}",
                    f"      → {' '.join(str(i.get('then') or '').split())}"]
            if i.get("check"):
                out += [f"      `{i['check']}`"]
        out += [""]
    if later:
        out += ["## Waiting on the outside world", "",
                *[f"- **{as_date(i['due']).isoformat()}** — "
                  f"{' '.join(str(i['what']).split())}"
                  + ("  *(then mine to run, not yours)*"
                     if (i.get("owner") or "human") == "agent" else "")
                  for i in later], ""]
    return out


def apply_declines(lines: list[str]) -> list[str]:
    """Drop what data/declines.yaml says has been decided against.

    The worklist is generated from live state, which means it cannot tell "not done
    yet" from "looked at and declined" -- so a decision to skip something reappears
    every run as though it were still open. Two of the sections are like this by
    design: the 64 missing journal-refs are worth doing for the top dozen and not the
    tail, and the OpenAlex duplicates are best left to resolve themselves. A list that
    keeps asking for what you have already ruled out is a list you stop reading.

    A post-filter over the rendered markdown rather than a check inside each of the
    fifteen emitters: one place to read, and a decline is matched on the text the
    reader saw, so what it removes is exactly what was there.

      sections: ["OpenAlex"]        # any heading containing this, and its body
      items:    ["2306.01708"]      # any list item containing this
      deferred: [{match: "Repo labels", until: "the papers are settled"}]

    `items` matches any bullet, not only `- [ ]` ones. It used to require the checkbox,
    which quietly meant the sections that list papers rather than tasks -- the drafting
    queue, the dated waiting list -- could not be declined at all: the decision had
    nowhere to go, so the line came back every run.

    `deferred` is the third state, and it needs to exist because "not now" is neither
    "open" nor "declined": the section is real work that will be done, just not
    before something else. Dropping it loses the reminder, leaving it at the top
    competes with the work that comes first. So it moves to the bottom, intact, under
    the condition that releases it -- still generated from live state, so it stays
    accurate while it waits, and no session has to stay alive to remember it.

    What was hidden is reported at the bottom of the file rather than silently
    dropped: a decline is a decision, and a decision that leaves no trace is
    indistinguishable from a bug that ate a task.
    """
    d = read_yaml(os.path.join(DATA, "declines.yaml")) or {}
    secs = [s for s in (d.get("sections") or []) if s]
    items = [i for i in (d.get("items") or []) if i]
    defs = [x for x in (d.get("deferred") or []) if (x or {}).get("match")]
    if not (secs or items or defs):
        return lines
    out, dropped_secs, dropped_items = [], [], 0
    held: list[str] = []              # deferred sections, in the order they appeared
    held_secs: list[str] = []
    hold_at = 0                       # heading depth currently being held, 0 = none
    skip_at = 0                       # heading depth currently being skipped, 0 = none
    for ln in lines:
        # Both levels: the four identity surfaces are `###` under one `##`, so declining
        # OpenAlex must remove a subsection without taking ORCID with it -- and
        # declining the `##` above it must take every `###` inside, which is why the
        # depth is tracked rather than a flag.
        depth = (len(ln) - len(ln.lstrip("#"))) if re.match(r"##+ \S", ln) else 0
        if depth:
            if skip_at and depth > skip_at:
                continue
            if hold_at and depth > hold_at:
                held.append(ln)
                continue
            hit = next((s for s in secs if s.lower() in ln.lower()), None)
            dfr = next((x for x in defs if x["match"].lower() in ln.lower()), None)
            skip_at, hold_at = (depth if hit else 0), (depth if dfr else 0)
            if hit:
                dropped_secs.append(ln.lstrip("# ").strip())
                continue
            if dfr:
                # Demoted one level: it sits under the "Deferred" heading now, and a
                # `##` inside a `##` would read as a sibling of the work that is open.
                held_secs.append(ln.lstrip("# ").strip())
                held += ["", f"#{ln}", "",
                         f"*Deferred until {dfr.get('until', 'you say otherwise')}.*"]
                continue
        if skip_at:
            continue
        if hold_at:
            held.append(ln)
            continue
        if ln.lstrip().startswith("- ") and any(i in ln for i in items):
            dropped_items += 1
            continue
        out.append(ln)

    # A heading that counts its own subsections ("Identity surfaces (4 open)") now
    # counts one that is no longer there, and a header disagreeing with the list under
    # it is exactly the kind of small wrongness that makes a reader stop trusting the
    # rest of the page. Recount from what survived.
    for i, ln in enumerate(out):
        m = re.match(r"(## .*\()(\d+)( open\))", ln)
        if not m:
            continue
        n = 0
        for l in out[i + 1:]:
            if l.startswith("## "):
                break
            n += bool(re.match(r"###+ \S", l))
        out[i] = f"{m.group(1)}{n}{m.group(3)}{ln[m.end():]}"

    if held:
        out += ["", "## Deferred", "",
                "Real work, parked on purpose. Regenerated from live state like",
                "everything else, so it stays accurate while it waits.", *held, ""]

    hid = []
    if dropped_secs:
        hid.append(f"{len(dropped_secs)} section"
                   f"{'s' * (len(dropped_secs) != 1)} ({'; '.join(dropped_secs)})")
    if dropped_items:
        hid.append(f"{dropped_items} individual item"
                   f"{'s' * (dropped_items != 1)}")
    note = []
    if hid:
        note.append(f"hidden: {' and '.join(hid)}")
    if held_secs:
        note.append(f"deferred to the bottom: {'; '.join(held_secs)}")
    return out + ["---", "", f"*Per `data/declines.yaml` — {'. '.join(note)}. "
                             f"Delete a line there to have it asked normally again.*", ""]


def tidy(lines: list[str]) -> list[str]:
    """Insert the blank line markdown needs before a heading.

    Fifteen emitters build this file and each ends its block with whatever it ended
    with, so one that finished on a `- [ ]` line put a `###` heading directly after it
    -- and a heading with no blank line above it renders *inside* the list, which is
    how the Semantic Scholar section spent a while looking like a bullet of the ORCID
    one. Fixing it here rather than in each emitter means the sixteenth cannot
    reintroduce it, and it is mechanical, so it is fixed rather than reported.
    """
    out: list[str] = []
    for ln in lines:
        if re.match(r"#{2,} \S", ln) and out and out[-1].strip():
            out.append("")
        out.append(ln)
    return out


def scholar_gaps(sc: dict) -> list[str]:
    """The worklist section for `build/scholar_diff.json`, or nothing.

    First on the page when it is there, ahead of every fix to a paper we do have.
    Everything else on this list improves how a paper is presented; this list is
    papers that are not presented at all, and no amount of work on the other sections
    reaches them. It is also the only section whose items are *upstream of the
    pipeline* -- the fix is an edit to the source bibliography, not to anything here.
    """
    if not sc:
        return []
    gate, miss = sc.get("gate_dropped") or [], sc.get("not_in_corpus") or []
    miss = [r for r in miss if r.get("kind") != "not a paper"]
    var, dup = sc.get("title_variants") or [], sc.get("scholar_duplicates") or []
    if not (gate or miss or var or dup):
        return []

    def pl(n: int, word: str = "paper") -> str:
        return f"{n} {word}{'s' * (n != 1)}"

    def cites(n) -> str:
        return f"{n or 0} cite{'s' * ((n or 0) != 1)}"

    L = [f"## Coverage: Google Scholar and the corpus disagree on "
         f"{pl(len(gate) + len(miss) + len(var) + len(dup))}", "",
         f"Scholar lists **{sc.get('scholar_rows')}** works and matched "
         f"**{sc.get('matched')}** of the corpus's **{sc.get('corpus')}**. Scholar is",
         "the one list of your papers that is built by a different process, so it is the",
         "only check that can see a paper this pipeline never received. Full detail:",
         "`build/scholar_diff.json`.", ""]
    if gate:
        L += [f"### {pl(len(gate))} the authorship gate excluded  — a bug, or a "
              f"wrong Scholar row", "",
              "Scholar says these are yours and `build/not_mine.json` says they are not.",
              "One of the two is wrong. If the paper is yours, add its title under",
              "`also_mine` in [`data/overrides.yaml`](data/overrides.yaml); if Scholar has",
              "merged a namesake's paper into your profile, delete it there, because a",
              "wrong row misleads every human who reads it too.", ""]
        L += [f"- [ ] {cites(r.get('citations'))} — {(r.get('title') or '')[:66]}"
              for r in gate] + [""]
    if miss:
        L += [f"### {pl(len(miss))} absent from the source bibliography", "",
              "Not in the corpus and not rejected — they never arrived. The bibliography",
              "is this pipeline's only input, so the fix is one entry there; adding them",
              "to `data/` would be overwritten on the next run.", ""]
        L += [f"- [ ] {cites(r.get('citations'))} — {r.get('year') or '????'} — "
              f"{(r.get('title') or '')[:60]}" for r in miss[:12]]
        if len(miss) > 12:
            L += [f"- … and {len(miss) - 12} more in `build/scholar_diff.json`"]
        L += [""]
    if var:
        L += [f"### {pl(len(var))} under two titles", "",
              "Same paper, two names — usually a preprint and its retitled published",
              "version. Decide which is canonical and set it in",
              "[`data/overrides.yaml`](data/overrides.yaml); until then the two surfaces",
              "answer a title query differently, which is the exact failure this repo",
              "exists to prevent.", ""]
        L += [f"- [ ] `{v.get('slug')}`\n"
              f"      - scholar: {(v.get('scholar') or '')[:64]}\n"
              f"      - corpus:  {(v.get('corpus') or '')[:64]}" for v in var] + [""]
    if dup:
        L += [f"### {pl(len(dup))} listed twice on Scholar", "",
              "Two rows for one paper splits its citation count. Nothing in this repo can",
              "fix it: *select both on your profile → Merge*.", ""]
        L += [f"- [ ] `{d.get('slug')}` — the second row reads "
              f"{(d.get('scholar') or '')[:52]!r}" for d in dup] + [""]
    return L


def step_worklist(cfg, args) -> None:
    """Report what still needs the account owner, ranked by leverage.

    Open items only. An earlier version printed the whole evergreen recipe for each
    identity surface on every run -- the full ORCID import procedure, the Wikidata
    walkthrough -- regardless of whether any of it was still undone. Two things went
    wrong with that. It went stale, because a static recipe cannot know that steps 1-4
    are finished; and it buried the three lines that were actually open in four hundred
    that were not, so the file stopped being read.

    So the split: **the how-to lives in `docs/SETUP.md`**, which is general, published,
    and true whoever runs it. This file is generated, personal, and gated on live audit
    state -- a section appears only while there is something to do, and its absence is
    the report that it is done. Each item says what is open, why it is worth doing, and
    which section of SETUP.md explains how.
    """
    papers = (read_yaml(os.path.join(DATA, "papers.yaml")) or {}).get("papers", [])
    repos = (read_yaml(os.path.join(DATA, "repos.yaml")) or {}).get("repos", [])
    ident, ids = cfg["identity"], cfg["ids"]
    # Written by the audit step. Absent (audit skipped) = fall back to stored state
    # rather than guessing, and say so where it matters.
    state, scholar = {}, {}
    try:
        with open(os.path.join(ROOT, "build", "identity_state.json")) as f:
            state = json.load(f)
    except (OSError, ValueError):
        pass
    try:
        with open(os.path.join(ROOT, "build", "scholar_diff.json")) as f:
            scholar = json.load(f)
    except (OSError, ValueError):
        pass
    unowned = set(state.get("arxiv_unowned") or [])

    def top(pred, n=8):
        return sorted([p for p in papers if pred(p)],
                      key=lambda p: -(p.get("citations") or 0))[:n]

    lines = ["# What still needs you", "",
             "Regenerated by `python update.py`. **Open items only** — a section that is",
             "not here is done, and nothing on this page is a general instruction. The",
             "how-to for every item below is [docs/SETUP.md](docs/SETUP.md); the live",
             "reading of each external surface is [tasks/identity_audit.md](tasks/identity_audit.md).", ""]
    lines += due_followups()
    lines += scholar_gaps(scholar)

    n_strays = sum(1 for p in papers
                    if p.get("s2_author_record") in
                    [a for a in ids["semantic_scholar"] if a != ids["semantic_scholar_primary"]])

    # Each entry: (predicate, heading, body lines). Built as data so the whole
    # identity block is one loop and adding a surface is one tuple -- the previous
    # version inlined every surface unconditionally, which is how it went stale.
    o_miss = state.get("orcid_missing_papers") or []
    o_conf = state.get("orcid_strays_confirmed") or []
    o_dupg = state.get("orcid_duplicate_groups") or []
    facets = ((state.get("orcid_missing_variants") or [])
              + (state.get("orcid_missing_keywords") or [])
              + (state.get("orcid_missing_other_pages") or [])
              + ([] if state.get("orcid_has_canonical_url", True) else ["canonical URL"]))
    by_slug = {p["slug"]: p for p in papers}
    ident_items = [
        (bool(o_miss),
         f"### ORCID is missing {len(o_miss)} of your {len(papers)} papers",
         ["Highest leverage on this page. Semantic Scholar's disambiguation and",
          "OpenAlex's profile merges are both ORCID-driven, so this is the one fix that",
          "makes the others more likely to fix themselves.", "",
          "One upload, not one form per paper: *Works → + Add → Add BibTeX* →",
          "**`tasks/orcid_missing.bib`** (only the missing ones) or",
          "`tasks/orcid_import.bib` (all of them; ORCID groups on shared identifiers, so",
          "re-importing what is already there merges rather than duplicates).",
          "Full list with citations: `tasks/orcid_missing.md`. How and why:",
          "[docs/SETUP.md §1](docs/SETUP.md#1-orcid--populate-it-then-wire-it-everywhere).", ""]
         + [f"- [ ] {(by_slug.get(s) or {}).get('citations') or 0} cites — "
            f"{((by_slug.get(s) or {}).get('title') or s)[:66]}"
            for s in o_miss[:8]]
         + ([f"- … and {len(o_miss) - 8} more in `tasks/orcid_missing.md`"]
            if len(o_miss) > 8 else [])),
        (bool(o_conf),
         f"### ORCID lists {len(o_conf)} work that is not yours"
         if len(o_conf) == 1 else
         f"### ORCID lists {len(o_conf)} works that are not yours",
         ["A wrong work on your record is worse than a missing one: it is the thing that",
          "makes an automated merge distrust the record. *Works → the entry → Delete.*",
          "Put-codes and titles: `tasks/orcid_remove.md`.", ""]),
        (bool(o_dupg),
         f"### ORCID lists {len(o_dupg)} of your papers twice",
         ["ORCID groups works that share an identifier. Two groups for one paper means",
          "one copy carries the arXiv DataCite DOI (`10.48550/arXiv.<id>`) and the other",
          "the publisher DOI, so they share no key. Fix by adding the *missing* DOI to",
          "either copy — the groups then fuse — or by deleting the sparser copy.",
          "Both put-codes per pair: `tasks/orcid_remove.md`.", ""]),
        (bool(facets),
         f"### ORCID facet fields ({len(facets)} still empty)",
         ["Separate from works, and two minutes: *Also known as*, *Keywords*, *Websites*.",
          "Exactly which are missing, with the values ready to paste:",
          "`tasks/identity_audit.md`.", ""]),
        (n_strays > 0,
         f"### Semantic Scholar — {n_strays} papers on a second author record",
         ["Every S2-backed tool (Elicit, Consensus, SciSpace, most literature agents)",
          "resolves you to one page, so each currently sees about half the corpus.",
          "There is no self-service merge, but a claimed page can pull papers across:",
          "*Edit Author Page → Add Papers*. Citation-ordered list with URLs:",
          "`tasks/s2_merge.md`, so stopping early still captures most of the loss.",
          "Do not claim the second page as well.", ""]),
        (bool(state.get("wikidata_gaps")),
         f"### Wikidata — {state.get('wikidata_gaps')} statement gaps on "
         f"{state.get('wikidata') or 'your item'}",
         ["Now automatic, and it does **not** need an autoconfirmed account — that is a",
          "QuickStatements rule, not a MediaWiki one. Create a bot password once at",
          "<https://www.wikidata.org/wiki/Special:BotPasswords> (grants: edit existing",
          "pages, create/edit pages), export `WIKIDATA_BOT_USER` and",
          "`WIKIDATA_BOT_PASSWORD`, then:", "",
          "```bash",
          "python scripts/wikidata_apply.py            # dry run: exactly what changes",
          "python scripts/wikidata_apply.py --apply    # write it",
          "```", ""]),
        (bool(ids.get("openalex_duplicates")),
         f"### OpenAlex — {len(ids.get('openalex_duplicates') or [])} duplicate profiles",
         ["Lowest priority, and the preferred route is to do nothing here: OpenAlex",
          "disambiguation is ORCID-driven and they are running ORCID-based merges, so",
          "fixing ORCID above may resolve it. If you want it now, the profile IDs to",
          "paste into their *Fix errors* form are in `tasks/openalex_merge.md`.", ""]),
    ]
    open_items = [(h, b) for pred, h, b in ident_items if pred]
    if open_items:
        lines += [f"## Identity surfaces ({len(open_items)} open)", "",
                  "Each is blocked on an account you are logged into, not on knowing what to",
                  "do. `python scripts/identity_tasks.py` regenerates every payload under",
                  "`tasks/` — committed, so browsable on GitHub.", ""]
        for h, b in open_items:
            lines += [h, ""] + b
    else:
        lines += ["## Identity surfaces", "",
                  "Nothing open. ORCID, Semantic Scholar, Wikidata and OpenAlex all match",
                  "`config.yaml` as of the last audit.", ""]

    typos = state.get("arxiv_name_typos") or []
    if typos:
        lines += [f"## arXiv spells your name wrong on {len(typos)} papers  — "
                  f"do this before anything downstream", "",
                  "The only item here that is upstream of every other surface. Hugging",
                  "Face, Semantic Scholar, OpenAlex and Google Scholar all build author",
                  "identity from arXiv's author list, so one wrong character does not",
                  "degrade gracefully — it creates a second author who holds that paper's",
                  "citations and cannot be merged into you. Work on the downstream pages",
                  "does not repair it.", "",
                  "A name correction is a **metadata edit**, not a new version: *Update this",
                  "article* on your submission page. You must own the paper first — and note",
                  "the trap: <https://arxiv.org/auth/request-ownership> matches your name",
                  "against the author list, which on these papers is the thing that is",
                  "wrong, so the request can bounce. If it does, ask the submitting",
                  "co-author for the paper password",
                  "(<https://arxiv.org/auth/need-paper-password>), which does not",
                  "name-match.", ""]
        for t in typos:
            p = by_slug.get(t.get("slug")) or {}
            lines.append(f"- [ ] [`{t['arxiv']}`](https://arxiv.org/abs/{t['arxiv']}) — "
                         f"reads **{t.get('reads')}** — {(p.get('title') or '')[:52]}")
        lines += ["", "Full detail: `tasks/arxiv_name_fixes.md`.", ""]

    if state.get("arxiv_registered") is not None and unowned:
        lines += [f"## arXiv: claim ownership of {len(unowned)} papers  — before the journal-refs",
                  "",
                  f"Registered as author on **{state['arxiv_registered']}** of "
                  f"**{state['arxiv_total']}** arXiv papers. arXiv tracks this separately from",
                  "authorship: it defaults to whoever pressed submit, so a co-authored corpus",
                  "is mostly not yours as far as arXiv is concerned. Two consequences:",
                  "",
                  "1. **You cannot edit a paper you do not own**, so the journal-ref section",
                  "   below is blocked on this for those papers.",
                  f"2. <https://arxiv.org/a/{ident['orcid']}> — the public author page you get",
                  "   from linking ORCID, with an Atom feed and an embeddable widget — lists",
                  "   only the papers you own.",
                  "",
                  "Instant with the paper password (ask the submitting co-author; it is in",
                  "their acceptance email): <https://arxiv.org/auth/need-paper-password>.",
                  "Without it, <https://arxiv.org/auth/request-ownership> — staff verify in a",
                  "couple of days, no co-author needed, so batch the long tail there.",
                  "",
                  "Full list, citation-ordered: `tasks/arxiv_ownership.md`.",
                  ""]

    # A paper with no published venue has no journal-ref to declare, and listing it here
    # invited exactly the wrong edit: two entries read `-> ArXiv` and `-> CoRR`, which are
    # the *absence* of a venue written out as if it were one.
    def needs_jr(p) -> bool:
        return bool(p.get("arxiv") and not p.get("arxiv_journal_ref")
                    and p.get("venue") and not is_preprint_venue(p["venue"]))

    missing_jr = top(needs_jr, 12)
    if missing_jr:
        blocked = sum(1 for p in papers if p.get("arxiv") in unowned and needs_jr(p))
        lines += [f"## arXiv journal-ref missing ({sum(1 for p in papers if needs_jr(p))} papers)",
                  "",
                  "**What it buys.** A preprint with no journal-ref is, to every indexer, a",
                  "paper with no venue. Three concrete consequences:",
                  "",
                  "1. **Google Scholar keeps two records.** It merges preprint and published",
                  "   versions largely on venue agreement; without a journal-ref the arXiv",
                  "   record is a separate cluster, and the citations split across the two.",
                  "   Merging them is what moves a paper up its own search results.",
                  "2. **The arXiv DataCite record gains a `container-title`**, which is what",
                  "   flows to OpenAlex, ORCID auto-update and Crossref-derived tools. A",
                  "   venue-less record is filtered out by anything ranking on venue.",
                  "3. **Answer engines cite venue as authority.** \"Published at ACL 2024\" in",
                  "   the metadata is what makes a model's answer name the venue instead of",
                  "   calling it a preprint.",
                  "",
                  "**Recommendation:** do not work the whole list. Do the top ~15 by citations",
                  "and stop — that is where the citation-splitting actually costs something.",
                  "There is no write API, so it is one *Journal ref* form per paper on your",
                  "submission page (a metadata edit, not a new version).",
                  ""]
        if blocked:
            lines += [f"**{blocked} of these are marked (blocked)**: you are not a registered",
                      "author on them, so the form will refuse. Claim ownership first (above).",
                      ""]
        for p in missing_jr:
            # The citation form, which is what to type into the form: the full proceedings
            # name truncated to fit this line is not a bibliographic reference.
            venue = p.get("venue_display") or p.get("venue") or "?"
            flag = "  **(blocked)**" if p["arxiv"] in unowned else ""
            lines.append(f"- [ ] `{p['arxiv']}` ({p.get('citations') or 0} cites) -> {venue}  "
                         f"<https://arxiv.org/abs/{p['arxiv']}>{flag}")
        lines.append("")

    # Prefer the audit's live sets over the collector's cached flags where present:
    # this list is worked by hand over days, and a stale copy sends you back to
    # pages you already did -- which is what happened the first time round.
    hf_missing = set(state.get("hf_missing") or [])
    hf_unclaimed = set(state.get("hf_unclaimed") or [])
    live_hf = state.get("hf_missing") is not None

    no_hf = top(lambda p: (p["arxiv"] in hf_missing) if live_hf
                else (p.get("arxiv") and p.get("hf_indexed") is False), 10)
    if no_hf:
        n = len(hf_missing) if live_hf else sum(
            1 for p in papers if p.get("hf_indexed") is False and p.get("arxiv"))
        lines += [f"## Hugging Face paper page missing ({n})",
                  "",
                  "Log in to Hugging Face first: an unauthenticated visit creates nothing",
                  "(verified, 0 of 50). Visiting the URL while logged in *is* the action --",
                  "there is no form.",
                  "",
                  "Full list: `tasks/hf_worklist.md`. Clickable, and re-checked live:",
                  "`python scripts/hf_papers.py --live`.",
                  ""]
        for p in no_hf:
            lines.append(f"- [ ] <https://hf.co/papers/{p['arxiv']}>  ({p.get('citations') or 0} cites)")
        lines.append("")

    unclaimed = top(lambda p: (p["arxiv"] in hf_unclaimed) if live_hf
                    else (p.get("hf_indexed") and not p.get("hf_claimed_by_me")), 10)
    if unclaimed:
        n = len(hf_unclaimed) if live_hf else sum(
            1 for p in papers if p.get("hf_indexed") and not p.get("hf_claimed_by_me"))
        lines += [f"## Hugging Face page indexed but not claimed by you ({n})",
                  "",
                  "Claims go through moderation and Hugging Face only publishes the",
                  "author→user link once it is granted, so a request already submitted is",
                  "invisible from outside and would otherwise be listed here again. If you",
                  "have already asked for one of these, add its arXiv id to",
                  "`hf_claim_requested` in `data/overrides.yaml` and it moves to *pending*",
                  "in `tasks/hf_worklist.md` instead of back onto this list.",
                  "",
                  "Full list and the other buckets: `tasks/hf_worklist.md`.",
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

    # Two different asks, and conflating them is what made this section unusable:
    # verifying a draft is minutes, writing one from a blank file is not. Drafts are
    # in data/sidecars/drafts/ and nothing reads them until you promote one.
    drafted = sorted(os.path.basename(f)[:-3] for f in
                     glob.glob(os.path.join(DATA, "sidecars", "drafts", "*.md")))
    no_side = [p for p in papers if not p.get("has_sidecar")]
    if drafted:
        lines += [f"## Sidecar drafts awaiting your verification ({len(drafted)})", "",
                  "Drafted from each paper's own full text: claims with their magnitudes,",
                  "scope conditions, terminology and likely misreadings. Every number is a",
                  "machine's reading and needs your eyes — but you are correcting a page,",
                  "not writing one. Each file opens with what to check, in the order it pays.",
                  "",
                  "```bash",
                  "python scripts/draft_sidecars.py --review          # what is drafted",
                  "python scripts/draft_sidecars.py --accept <slug>   # promote, after editing",
                  "```", ""]
        for slug in sorted(drafted, key=lambda s: -((by_slug.get(s) or {})
                                                    .get("citations") or 0))[:10]:
            p = by_slug.get(slug) or {}
            # A draft for a paper that already has a live sidecar is a replacement, and
            # that changes what reviewing it means: you are comparing two readings, one
            # of which is already published, rather than checking a new page. `--accept`
            # refuses it without `--replace` for the same reason.
            mark = "  **replaces the live sidecar**" if p.get("has_sidecar") else ""
            lines.append(f"- [ ] `data/sidecars/drafts/{slug}.md`  "
                         f"({p.get('citations') or 0} cites) "
                         f"{(p.get('title') or '')[:56]}{mark}")
        lines.append("")
    todraft = [p for p in no_side if p["slug"] not in set(drafted)]
    if todraft:
        lines += [f"## Sidecars not yet drafted ({len(todraft)}/{len(papers)})", "",
                  "Nothing to do by hand here — this is a run, not a task:",
                  "",
                  "```bash",
                  "python scripts/draft_sidecars.py --limit 20   # queue the next 20",
                  "python scripts/draft_sidecars.py --ingest     # fold the answers in",
                  "```", "",
                  "`update.py` also drafts a batch on every run, so this number falls on",
                  "its own. The top of the list, by citations, is where it pays:", ""]
        for p in sorted(todraft, key=lambda p: -(p.get("citations") or 0))[:6]:
            lines.append(f"- {p.get('citations') or 0} cites — {p['title'][:66]}")
        lines.append("")

    # Papers whose text no fetcher can reach. Upstream of the two sidecar sections
    # above: a sidecar is drafted from a paper's own full text, so a paper with none
    # can never be drafted and would otherwise sit in "not yet drafted" for ever,
    # looking like a queue that had not got to it yet. The distinction worth drawing
    # is between a paper the pipeline has not read and one it cannot -- the second is
    # a task, and the whole task is putting a file somewhere.
    starved = []
    for p in papers:
        if os.path.exists(os.path.join(ROOT, "data", "sidecars", f"{p['slug']}.md")):
            continue
        if any(os.path.exists(os.path.join(ROOT, "data", "fulltext", p["slug"] + e))
               for e in (".pdf", ".txt")):
            continue
        f = os.path.join(ROOT, "build", "fulltext", f"{p['slug']}.txt")
        try:
            if os.path.getsize(f) >= 2000:
                continue
        except OSError:
            pass
        starved.append(p)
    if starved:
        lines += [f"## Papers whose full text nothing can fetch ({len(starved)})", "",
                  "Every one of these is a real paper that is not on arXiv, so there is no",
                  "HTML rendering and no open PDF to extract — a Nature paywall, an Elsevier",
                  "page that serves an open-access licence to browsers and 403s to everything",
                  "else, an SSRN download behind a click. They are not slow, they are blocked,",
                  "and no rerun will change that.",
                  "",
                  "You already have all three PDFs. Drop each one in as",
                  "`data/fulltext/<slug>.pdf` — the directory is gitignored, so the PDF stays",
                  "on your machine and only the sidecar it produces is committed. That path is",
                  "read before any network source, so the next run picks it up and the paper",
                  "joins the drafting queue.", ""]
        for p in sorted(starved, key=lambda p: -(p.get("citations") or 0)):
            lines.append(f"- [ ] `data/fulltext/{p['slug']}.pdf` — "
                         f"{p.get('citations') or 0} cites, {p.get('venue_display') or 'no venue'}"
                         f" — {(p.get('title_display') or p.get('title') or '')[:52]}")
        lines.append("")

    # Artifacts that are not papers and have no paper: a tool or a guide nobody can
    # cite because there is nothing to cite. Listed low, because a Zenodo DOI is the
    # cheapest item here and also the least likely to change what an engine returns.
    zcand = [r for r in repos if not r.get("skip") and not r.get("paper_slug")
             and r.get("kind") in ZENODO_KINDS and not r.get("zenodo_doi")]
    if zcand:
        lines += [f"## Artifacts with no citation route ({len(zcand)})", "",
                  "Tools and guides with no linked paper. A Zenodo release DOI gives each a",
                  "citable, archived identity and a DataCite record that reaches OpenAlex",
                  "and your ORCID works list — so they stop being GitHub-only objects.",
                  "Steps, and the honest case for skipping some: `tasks/zenodo.md`.", ""]

    pend = [r for r in repos if not r.get("reviewed") and not r.get("skip")]
    if pend:
        lines += [f"## Repo labels awaiting your review ({len(pend)}/{len(repos)})", "",
                  "Check `data/repos.yaml`, fix anything wrong, set `reviewed: true` to freeze "
                  "it, then `python scripts/sweep_github.py diff`.", ""]

    lines = tidy(apply_declines(lines))

    out = os.path.join(ROOT, "WORKLIST.md")
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nwrote {out}")
    print("\n".join(l for l in lines if l.startswith("## ")))


def closing(args) -> None:
    """The end of a run: what is left for a human, and the one link to look at.

    Written as a short list of places rather than a list of tasks, because the tasks
    are already ranked in WORKLIST.md and repeating them here would give a reader two
    lists to reconcile. The site link goes first: a page is the only form in which you
    can see whether the run produced something you would want your name on.
    """
    print(f"\n{'=' * 62}\n== what is left for you\n{'=' * 62}")

    index = os.path.join(ROOT, "build", "site", "index.html")
    if os.path.exists(index):
        print("\nThe run's output, as a reader meets it:")
        print(f"  file://{index}")

    lines = []
    worklist = os.path.join(ROOT, "WORKLIST.md")
    if os.path.exists(worklist):
        with open(worklist) as f:
            n = sum(1 for l in f if l.startswith("## "))
        lines.append(f"  WORKLIST.md              {n} thing{'s' * (n != 1)} only you can do, "
                     f"ranked by citations")
    drafts = glob.glob(os.path.join(DATA, "sidecars", "drafts", "*.md"))
    if drafts:
        lines.append(f"  data/sidecars/drafts/    {len(drafts)} sidecar draft"
                     f"{'s' * (len(drafts) != 1)} to verify -- nothing reads these until "
                     f"you run `--accept <slug>`")
    backlog = os.path.join(ROOT, "BACKLOG.md")
    if os.path.exists(backlog):
        with open(backlog) as f:
            n = sum(1 for l in f if l.lstrip().startswith("- [ ]"))
        # The one list here that nothing can re-derive, so the one that can be
        # forgotten. Counted rather than quoted: the tasks are in the file, and a
        # second copy of them in the run's output is a second copy to keep true.
        lines.append(f"  BACKLOG.md               {n} parked task{'s' * (n != 1)} -- "
                     f"decisions and code, not account work")

    if lines:
        print("\nWaiting on your judgement:")
        print("\n".join(lines))

    if args.apply:
        return
    print("\nNothing above has left this machine. When it looks right:")
    print("  python scripts/sweep_github.py diff      # see exactly what would change")
    print("  python update.py --apply                 # write the repo changes")
    print("  python scripts/build_site.py --deploy    # publish the site")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", choices=STEPS, help="run one step instead of all")
    ap.add_argument("--refresh-bib", action="store_true",
                    help="run the publications pipeline first (needs sources.publications_path)")
    ap.add_argument("--apply", action="store_true",
                    help="also push approved repo changes to GitHub")
    ap.add_argument("--draft-batch", type=int, default=10, metavar="N",
                    help="sidecars to draft per run (default 10, 0 to skip the step)")
    args = ap.parse_args()
    cfg = load_config()

    fns = {"collect": step_collect, "repos": step_repos, "propose": step_propose,
           "draft": step_draft, "links": step_links,
           "ownership": step_ownership, "audit": step_audit,
           "validate": step_validate, "render": step_render, "worklist": step_worklist}
    for name in ([args.step] if args.step else STEPS):
        print(f"\n{'=' * 62}\n== {name}\n{'=' * 62}")
        fns[name](cfg, args)

    if args.apply:
        print(f"\n{'=' * 62}\n== apply (writes to GitHub and Hugging Face)\n{'=' * 62}")
        run([sys.executable, "scripts/sweep_github.py", "apply", "--yes"])
        run([sys.executable, "scripts/paper_code.py", "--apply"])
    closing(args)


if __name__ == "__main__":
    main()
