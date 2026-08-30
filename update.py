#!/usr/bin/env python3
"""paper-geo: one command, re-runnable, safe to schedule.

    python update.py                 # refresh everything read-only, report what needs you
    python update.py --refresh-bib   # read the bibliography from its local checkout
    python update.py --apply         # additionally write the approved repo and link changes
    python update.py --step collect  # run a single step

Who does what:

  * Code, no human in it: collect, repos, links, ownership, audit, validate, render.
    All re-derived from public sources.
  * A model's judgement, handed back rather than published: propose (repo labels) and
    draft (sidecars). Both write where nothing reads until promoted.
  * Reserved for the author: accepting a sidecar draft, which publishes an assertion
    under their name, and any write that leaves this machine.

Rules every step keeps, because this is meant to be re-run for years: read-only unless
--apply; idempotent, with human decisions read from data/overrides.yaml or a `reviewed`
flag rather than clobbered; a source outage costs one field, not the run; and new papers
and repos surface themselves in the report with what they still need.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from common import (DATA, DECLINE_STAMP, health_report,  # noqa: E402
                    load_config, read_yaml)
from worklist import (arxiv_journal_refs, arxiv_name_typos,  # noqa: E402
                      arxiv_ownership, hf_pages, identity_surfaces,
                      repo_gaps, same_or_different, scholar_gaps,
                      scholar_split_records, sidecar_drafts, starving_papers,
                      upstream_gaps, wikidata_coauthors, wikidata_orgs,
                      wikidata_people, wikipedia_checks)

STEPS = ("collect", "repos", "propose", "draft", "links", "ownership", "audit",
         "validate", "render", "worklist")


FAILED: list[tuple[str, int]] = []


def run(argv: list[str], cwd: str | None = None) -> int:
    """Run one step, recording a non-zero exit in `FAILED`.

    Every script here refuses rather than writing a false-empty when a source will not
    answer, and three of them say so in as many words. That refusal only counts for
    something if the run carries it forward. `WORKLIST.md` is rebuilt at the end from
    whatever `build/` holds, so a step that died after an earlier run wrote its file leaves
    a section reading as current on last week's data, which `built` cannot see because the
    file is there and parses.
    """
    print(f"\n$ {' '.join(argv)}", flush=True)
    code = subprocess.call(argv, cwd=cwd or ROOT)
    if code:
        FAILED.append((" ".join(argv[1:]) or argv[0], code))
        print(f"  ^ exited {code}", file=sys.stderr, flush=True)
    return code


def step_collect(cfg, args) -> None:
    """Rebuild data/papers.yaml from bibliography + S2 + arXiv + HF."""
    if args.refresh_bib:
        # The bibliography checkout is read on disk, never run. Its own pipeline commits and
        # pushes -- to GitHub and to Overleaf -- so driving it from here would publish to a repo
        # this project does not own. Reading the working copy rather than the last pushed version
        # is the half that was wanted: a refresh done over there is visible here immediately.
        path = cfg["sources"].get("publications_path")
        if path and os.path.isdir(path):
            print(f"  reading the bibliography from {path} (its working tree, not the\n"
                  f"  pushed copy). Refresh it there first if you want new entries: "
                  f"cd {path} && python update.py")
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

    Runs the Hugging Face pass again even though collect.py just fetched the same pages, at
    ~30s in a multi-minute run, so both hand-worked lists come from one moment in time.

    The Scholar diff belongs here rather than in `collect`, since it audits the collector's
    output against a list the collector cannot see -- a paper that never entered, and a
    paper the authorship gate dropped. Report-only, and it never stops the run, because
    Google answers a crawler with a challenge page often enough.
    """
    run([sys.executable, "scripts/audit_identity.py"])
    run([sys.executable, "scripts/scholar_check.py"])
    # After the Scholar diff, which is the only source of the per-row citation counts
    # its first pass compares against.
    run([sys.executable, "scripts/scholar_strays.py", "--quiet"])
    run([sys.executable, "scripts/identity_tasks.py"])
    # Reads the paper items live, so it has to follow any run that created some.
    run([sys.executable, "scripts/wikidata_coauthors.py", "--quiet"])
    # Reads the paper items too, and its second pass needs the group items the first pass
    # asked for, so it is re-run every time rather than once.
    run([sys.executable, "scripts/wikidata_orgs.py", "--quiet"])
    # Reads the co-author cache written above, so it runs after it and never before.
    run([sys.executable, "scripts/wikidata_people.py", "--quiet"])
    # Wikipedia is read here for the same reason as the rest of this step: it is a surface we
    # do not control, and the only actions available on it are proposals an editor may
    # decline, so what is open has to be re-read rather than remembered.
    run([sys.executable, "scripts/wikipedia_tasks.py"])


def step_validate(cfg, args) -> None:
    """Fail loudly on a malformed hand edit or a bad model proposal.

    Fixes the corpus sizes stated in the docs rather than reporting them -- one new paper made
    seven prose sentences wrong at once. The three sentences whose count feeds a sum are still
    only reported, because there the arithmetic has to be redone by someone who can read it.

    The only step that can stop the run, and only on a structural failure: `render` and
    `worklist` both read `data/` and present it, so a schema violation or a dangling claim id
    would become a page that looks reviewable. A stale count exits 0 and the run continues.
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

    The next run is the reminder. A cron entry or a chat reminder lives in one process and dies
    with it, and a calendar entry keeps the date but loses the reason -- which for these items
    is the whole content, since each one is "the wait is over, so now X is possible". Here the
    date and the reason are in the repo together.

    Items not yet due are listed too, compactly: knowing that nothing is due *and* what is
    coming is the difference between a clear page and a page that is merely silent.
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


PAYLOAD = re.compile(r"tasks/[\w.]+\.(?:md|bib|txt|qs)")

# The order to work the open sections in, and what each one costs. Three tiers, because
# the question a reader actually arrives with is not "what is most important" -- the
# sections are already citation-ranked for that -- but "what can I finish with the time
# I have in front of me right now", and the three answers are a command, a minute, and
# an afternoon.
TIERS = (
    ("run", ["**A command, and nothing to decide.** Any day, in any order: these drain",
             "backlogs the rest of the page is waiting on, and the run does the work."]),
    ("minute", ["**One edit each, and each one closes a section outright.** This is where",
                "the page gets visibly shorter."]),
    ("afternoon", ["**As much as you have patience for.** Per-paper clicking, because",
                   "no write API can make the judgement each one needs — and every section",
                   "is ordered so that stopping early still captures most of the value."]),
)
# Matched on a fragment of the heading rather than carrying its own copy of the counts:
# the line the reader sees is the section's own heading, so "108 papers" cannot drift
# into "104 papers" here. An entry whose section is absent this run is absent from the
# plan -- the same live-state contract as the rest of the file.
PLAN = (
    ("Wikidata —", "run",
     "`python scripts/wikidata_apply.py --papers --limit 10`, repeated. The monthly CI "
     "leg refuses to touch new papers while a backlog this size exists, so this is the "
     "one item that turns maintenance back on"),
    ("Wikidata author strings", "afternoon",
     "one Author Disambiguator pass per paper, most-cited first, at the link the section "
     "gives for each. Everything an ORCID or a DBLP author page could settle is already on "
     "Wikidata, so what is left is the part where the name is all there is to go on"),
    ("Co-authors who may already have a Wikidata item", "minute",
     "pick the line that is them and paste the QID into `data/overrides.yaml`, or `new` "
     "where none is. What every candidate item states about itself is in the section, so "
     "most rows need nothing opened, and answering the top few is worth doing on its own "
     "— each answer "
     "turns one co-author into `author` statements on the papers you share"),
    ("Sidecar drafts awaiting your verification", "minute",
     "read the draft and `--accept` it. The only place on this page where your "
     "judgement is the input rather than the check, because accepting publishes an "
     "assertion under your name"),
    ("carries another paper's identifier", "minute",
     "one ORCID edit, and it has to come before the other two ORCID sections: a wrong "
     "DOI is what makes one paper read as missing and another as duplicated"),
    ("papers twice", "minute",
     "one ORCID edit: add the DOI to the entry you are keeping"),
    ("ORCID is missing", "minute",
     "one BibTeX upload. Highest leverage on the page — Semantic Scholar and OpenAlex "
     "both re-cluster off ORCID, so this is the fix that makes other sections shrink "
     "without you"),
    ("the bibliography does not have", "minute",
     "one paste into `orig.bib`. The pipeline's only real input is that file, and the "
     "override line standing in for it goes on the next run"),
    ("field corrections the bibliography does not carry", "minute",
     "one paste per line, into the entry `orig.bib` already has for that paper. Every "
     "line is given ready to drop in, and the override lines go after. Worth more than "
     "its size — Scholar, "
     "Semantic Scholar and OpenAlex all read the paper's own record, and none of them "
     "reads this repo"),
    ("full text nothing can fetch", "minute",
     "drop the PDF you already have into `data/fulltext/` (gitignored, so it stays on "
     "your machine and only the sidecar it produces is committed)"),
    ("arXiv journal-ref", "afternoon",
     "save <https://arxiv.org/user> and feed it to `identity_tasks.py --user-page` "
     "first: two minutes, once, and it turns every hunt-by-eye row into a one-click "
     "link. Then the top few and stop — that section argues its own case honestly"),
    ("Wikipedia mentions", "minute",
     "read each article and tick it if it is right. Only a wrong description is work, and "
     "it goes on the talk page -- you may not edit these, and a correct mention needs "
     "nothing from you"),
    ("Semantic Scholar —", "afternoon",
     "one paste per paper into the Add Papers form, highest-citation first; every URL "
     "is in the section — read its first paragraph first, because a dated follow-up may "
     "do all of it for you"),
    ("Citations on a Scholar record you cannot see", "afternoon",
     "one search each, and a merge only where the result really is your paper. The "
     "biggest single gap on the page, and the only section where the payoff is "
     "citations you already earned rather than a surface that reads better"),
    ("listed twice on Scholar", "minute",
     "tick both rows on your Scholar profile and press *Merge*; both titles and the "
     "link to the second row are in the section"),
    ("Hugging Face paper page missing", "minute",
     "open each link while logged in — the visit is the action, there is no form. "
     "Nothing happens logged out, so log in first or the clicking is wasted"),
    ("Hugging Face page indexed but not claimed", "minute",
     "one claim request per link, then wait: the author→user link only appears once "
     "moderation grants it. Record what you asked for under `hf_claim_requested` so it "
     "does not come back onto the list while it is pending"),
    ("does not appear on your Scholar profile", "minute",
     "check the profile for a record Scholar folded this paper into before adding "
     "anything — a merged paper looks identical here to a missing one, and adding it "
     "by hand splits future citations. Decline the line if a related record covers it"),
)
# Headings that are not work: context, containers, and the parked list. Every heading must
# appear here or in the plan -- the test asserts it, so a section added later cannot
# quietly miss the plan.
#
# `Due now` is a clock, not a task: its items are dated pointers into the sections below,
# so ranking it too lists the same work twice.
#
# `Sidecars not yet drafted` is the agent's job under `CLAUDE.md`'s code > agent > human
# ranking. What is the author's is the draft that comes out, one section above it.
NOT_STEPS = ("Due now", "Waiting on the outside world", "Coverage:", "Identity surfaces",
             "Deferred", "Artifacts with no citation route", "Sidecars not yet drafted",
             "Repo labels awaiting your review")


def next_steps(lines: list[str]) -> list[str]:
    """The whole file with an ordered plan inserted at the top.

    No section can answer the question the reader actually opens the file with -- *what do I do
    next, and can I finish it now?* -- because none of them knows what else is open. Each plan
    line is the section's own heading, the route into it, and the cost. No instruction is
    repeated: a second copy of an instruction goes stale while looking authoritative.

    A post-pass over the rendered text, after `apply_declines`, so a declined or deferred
    section cannot be listed here as the next thing to do.
    """
    heads = [l for l in lines if re.match(r"##+ \S", l)]
    n, body = 0, []
    for tier, blurb in TIERS:
        got = []
        for frag, t, route in PLAN:
            if t != tier:
                continue
            h = next((x for x in heads if frag.lower() in x.lower()), None)
            if h:
                n += 1
                got.append(f"{n}. **{h.lstrip('# ').strip()}** — {route}.")
        if got:
            body += ["", *blurb, "", *got]
    if not body:
        return lines
    block = ["## Start here", "",
             "The page below is ordered by leverage and citation count, which is the right",
             "order to read it in and not the order to work it in. This is that order, with",
             "what each item costs — the one thing a section cannot say about itself,",
             "because it does not know what else is open. Each line names the section that",
             "holds the instructions; nothing here repeats them.", *body, ""]
    i = next((k for k, l in enumerate(lines) if l.startswith("## ")), len(lines))
    return lines[:i] + block + lines[i:]


def stamp_payloads(off: dict[str, str], later: dict[str, dict]) -> list[str]:
    """Put the decision at the top of the payload file a hidden section pointed at.

    `apply_declines` removes the section from `WORKLIST.md`, and the `tasks/` file it handed
    the reader stays in the repo -- `tasks/openalex_merge.md` is the live case. The paths are
    re-derived every run from the hidden text itself, where every section with a payload
    names its own file, so a section declined in future needs no wiring.

    Markdown payloads only, and `common.write_task` is how a generator re-run keeps the
    banner it finds. The marker means a second run replaces the banner rather than stacking a
    copy, and clearing `declines.yaml` removes it again. Nothing is deleted, since the routes
    and identifiers are the work. Only `sections:` and `deferred:` paths arrive here -- a
    section that emptied item by item is already filtered by `common.declined`.
    """
    done = []
    for path, why in [*((p, ("off", w)) for p, w in off.items()),
                      *((p, ("later", d)) for p, d in later.items())]:
        full = os.path.join(ROOT, path)
        if not os.path.exists(full):
            continue                  # the section names a file this run did not write
        # Markdown only. The other three extensions `PAYLOAD` matches are pasted somewhere
        # whole -- a QuickStatements batch, an ORCID BibTeX import, a list of DOIs -- and a
        # blockquote at the top of one of those is a line the far end tries to parse.
        if not path.endswith(".md"):
            continue
        with open(full) as f:
            body = f.read()
        if body.startswith(DECLINE_STAMP):
            body = body.split("\n\n", 1)[-1]
        kind, w = why
        if kind == "off":
            head = [DECLINE_STAMP,
                    f"> **Declined.** [`data/declines.yaml`](../data/declines.yaml) has "
                    f"`{w}` under `sections:`, so `WORKLIST.md` no longer lists this and "
                    f"nothing below is being asked of you.",
                    "> Delete that line to have it asked normally again."]
        else:
            head = [DECLINE_STAMP,
                    f"> **Deferred until {w.get('until', 'you say otherwise')}.** Parked "
                    f"on purpose in [`data/declines.yaml`](../data/declines.yaml), not "
                    f"declined — this is real work, just not before the rest.",
                    "> It is at the bottom of `WORKLIST.md` under *Deferred*."]
        with open(full, "w") as f:
            f.write("\n".join(head) + "\n\n" + body)
        done.append(path)
    return sorted(done)


def apply_declines(lines: list[str]) -> list[str]:
    """Drop from the rendered worklist what data/declines.yaml has decided against.

      sections: ["OpenAlex"]        # any heading containing this, and its body
      items:    ["2306.01708"]      # any list item containing this
      deferred: [{match: "Repo labels", until: "the papers are settled"}]

    `items` matches any bullet, not only `- [ ]` ones, so a section listing papers rather
    than tasks can be declined too. A `deferred` section is real work waiting on something
    else, and moves to the bottom intact under the condition that releases it, still
    generated from live state.

    Reports what it hid, and which patterns matched nothing.
    """
    d = read_yaml(os.path.join(DATA, "declines.yaml")) or {}
    secs = [s for s in (d.get("sections") or []) if s]
    items = [i for i in (d.get("items") or []) if i]
    defs = [x for x in (d.get("deferred") or []) if (x or {}).get("match")]
    if not (secs or items or defs):
        return lines
    out, dropped_secs, dropped_items = [], [], 0
    used: set[str] = set()            # patterns that actually removed or moved something
    here = None                       # heading the current line sits under
    emptied: list[str] = []           # headings that lost an item to `items:`
    # Per heading: bullets it had before filtering, and bullets taken off it. Enough to
    # recount a heading that counts its own list, and enough to know not to -- a number
    # that did not match the list in the first place is not this filter's to rewrite.
    seen_n: dict[str, int] = {}
    cut_n: dict[str, int] = {}
    held: list[str] = []              # deferred sections, in the order they appeared
    held_secs: list[str] = []
    hold_at = 0                       # heading depth currently being held, 0 = none
    skip_at = 0                       # heading depth currently being skipped, 0 = none
    # `tasks/` files named inside a section that is being hidden or held, and the pattern
    # that did it -- so `stamp_payloads` can say so at the top of the file itself.
    off: dict[str, str] = {}
    later: dict[str, dict] = {}
    skip_pat, hold_dfr = "", {}
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
            skip_pat, hold_dfr = hit or "", dfr or {}
            here = ln
            if hit:
                used.add(hit)
                dropped_secs.append(ln.lstrip("# ").strip())
                continue
            if dfr:
                used.add(dfr["match"])
                # Demoted one level: it sits under the "Deferred" heading now, and a
                # `##` inside a `##` would read as a sibling of the work that is open.
                held_secs.append(ln.lstrip("# ").strip())
                held += ["", f"#{ln}", "",
                         f"*Deferred until {dfr.get('until', 'you say otherwise')}.*"]
                continue
        if skip_at:
            off.update({p: skip_pat for p in PAYLOAD.findall(ln)})
            continue
        if hold_at:
            later.update({p: hold_dfr for p in PAYLOAD.findall(ln)})
            held.append(ln)
            continue
        if ln.lstrip().startswith("- "):
            if here:
                seen_n[here] = seen_n.get(here, 0) + 1
            # Case-insensitively, like the two heading matchers above and like
            # `common.declined`, which reads the same patterns for the `tasks/` files.
            # It used to be the one case-sensitive matcher in the file, so `"Llm
            # merging"` -- typed from the Scholar row, which is where the decision was
            # made -- silently missed `"LLM Merging"` everywhere else.
            hit_i = next((i for i in items if i.lower() in ln.lower()), None)
            if hit_i:
                used.add(hit_i)
                dropped_items += 1
                if here:
                    cut_n[here] = cut_n.get(here, 0) + 1
                    if here not in emptied:
                        emptied.append(here)
                continue
        out.append(ln)

    dropped_secs += drop_emptied(out, emptied)
    recount_lists(out, seen_n, cut_n)
    recount_open(out)

    if held:
        out += ["", "## Deferred", "",
                "Real work, parked on purpose. Regenerated from live state like",
                "everything else, so it stays accurate while it waits.", *held, ""]

    dead = [p for p in secs + items + [x["match"] for x in defs] if p not in used]
    return out + ["---", "", *declines_note(dropped_secs, dropped_items, held_secs,
                                            off, later, dead), ""]


def drop_emptied(out: list[str], emptied: list[str]) -> list[str]:
    """Delete, in place, the headings that lost their last item. Returns what went.

    A heading, four paragraphs of instructions and a citation total standing over an empty
    list reads as an open task, which is the one thing this file must not contain. Only
    sections that *had* items -- a heading whose body is prose and a pointer has nothing
    to count.
    """
    gone = []
    for head in emptied:
        try:
            i = out.index(head)
        except ValueError:
            continue                  # its own `sections:` entry removed it already
        depth = len(head) - len(head.lstrip("#"))
        j = next((k for k in range(i + 1, len(out))
                  if re.match(r"##+ \S", out[k])
                  and len(out[k]) - len(out[k].lstrip("#")) <= depth), len(out))
        if not any(l.lstrip().startswith("- ") for l in out[i + 1:j]):
            gone.append(head.lstrip("# ").strip() + " — every item declined")
            del out[i:j]
    return gone


def recount_lists(out: list[str], seen_n: dict[str, int], cut_n: dict[str, int]) -> None:
    """Rewrite, in place, a heading stating the length of its own filtered list.

    "3 papers absent from the source bibliography" over a list some of whose items were
    declined. The count is the emitter's `pl(n)` and cannot just be dropped -- it is what
    tells you the size of the job before reading it.

    Only when the number *was* the length of the list: a heading opening with a digit that
    means something else ("2 of your 5 repos") is not a count of the bullets under it.
    """
    for head, cut in cut_n.items():
        m = re.match(r"(#+ )(\d+) ([A-Za-z]+)(?= |$)", head)
        if not m or int(m.group(2)) != seen_n.get(head):
            continue
        try:
            i = out.index(head)
        except ValueError:
            continue                  # the section went with its last item
        n = seen_n[head] - cut
        # The noun the emitters put after the count is `pl()`'s, so it is regular and a
        # trailing `s` is the plural rather than part of the word.
        stem = m.group(3)[:-1] if m.group(3).endswith("s") else m.group(3)
        out[i] = f"{m.group(1)}{n} {stem}{'s' * (n != 1)}{head[m.end():]}"


def recount_open(out: list[str]) -> None:
    """Rewrite, in place, a heading counting its own subsections ("Identity surfaces (4 open)").

    A header disagreeing with the list under it is exactly the kind of small wrongness that
    makes a reader stop trusting the rest of the page.
    """
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


def declines_note(dropped_secs: list[str], dropped_items: int, held_secs: list[str],
                  off: dict[str, str], later: dict[str, dict],
                  dead: list[str]) -> list[str]:
    """The footnote saying what `data/declines.yaml` hid, and which patterns did nothing."""
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
    # Reported here as well as stamped there, because the file is committed: a reader who
    # only ever opens `tasks/` should find the decision, and a reader who only ever opens
    # this one should know a file changed under them.
    stamped = stamp_payloads(off, later)
    if stamped:
        note.append("marked in " + ", ".join(f"`{p}`" for p in stamped))
    tail = [f"*Per `data/declines.yaml` — {'. '.join(note) or 'nothing hidden'}. "
            f"Delete a line there to have it asked normally again.*"]
    if dead:
        tail += ["", "*Matching nothing this run, so doing nothing: "
                 + ", ".join(f"`{p}`" for p in dead)
                 + ". Either the work got done, or the pattern misses its line — titles"
                   " are truncated in this file, so a pattern aimed past the cut never"
                   " matches. Check before trusting it as declined.*"]
    return tail


# Sections that ask for nothing on purpose, and are worth their space anyway: one says
# what is already in flight so it is not started again, the other holds work that is
# real but parked, and each of its children carries its own command.
KEEPS = ("Waiting on the outside world", "Deferred", "Start here")
# What "asks for something" looks like in the rendered page: a checkbox, or a fenced
# block holding a command or a payload. Deliberately *not* a backticked command inside
# prose -- that is how the Coverage section read as actionable while asking for nothing:
# its only command regenerates the local file it points at.
ASKS = re.compile(r"^\s*(?:- \[ \]|```)")


def drop_hollow(lines: list[str], say=print) -> list[str]:
    """Remove a section that no longer asks for anything.

    `declines.yaml` filters this file item by item, which is the right granularity, and it
    leaves a parent heading standing over the hole -- a heading, two measurements and a pointer
    to a file in gitignored `build/`, on a page whose first line promises open items only.

    Judged on the checkbox, the command or the pasteable payload rather than on prose, because
    prose is what a hollow section is made of. A parent survives on its children: a `##` whose
    `###` still asks is not hollow.
    """
    blocks: list[tuple[str, list[str]]] = [("", [])]
    for ln in lines:
        if re.match(r"#{2,3} \S", ln):
            blocks.append((ln, [ln]))
        else:
            blocks[-1][1].append(ln)
    keep, kept_parent = [False] * len(blocks), False
    for i, (head, body) in enumerate(blocks):
        if head.startswith("## ") or not head:
            kept_parent = any(k in head for k in KEEPS)
        keep[i] = (not head or kept_parent or any(ASKS.search(l) for l in body))
        # A `##` inherits from the `###`s that follow it, before the next `##`.
        if keep[i] and head.startswith("### "):
            for j in range(i - 1, 0, -1):
                if blocks[j][0].startswith("## "):
                    keep[j] = True
                    break
    gone = [b[0] for b, k in zip(blocks, keep) if not k]
    if gone:
        say("  hollow, dropped: " + "; ".join(h.lstrip("# ").strip() for h in gone))
    out = []
    for i, (_, body) in enumerate(blocks):
        if keep[i]:
            out += body
    return out


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


UNBUILT: list[str] = []


def built(name: str) -> dict:
    """What a step left in `build/`, `{}` if it has not run or wrote something unreadable.

    Records the miss in `UNBUILT`, which `unbuilt_note` puts on the page. Every section built
    from one of these files treats an empty read as nothing to report, so a step that did not
    run removes its whole section from a page whose first line says an absent section is done.
    """
    try:
        with open(os.path.join(ROOT, "build", name)) as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        why = "not there" if isinstance(e, FileNotFoundError) else "there and unreadable"
        UNBUILT.append(f"`build/{name}` ({why})")
        return {}


def failed_note() -> list[str]:
    """One line naming the steps of this run that did not finish, or nothing."""
    if not FAILED:
        return []
    one = len(FAILED) == 1
    return [f"> **{'A step' if one else f'{len(FAILED)} steps'} of this run did not "
            f"finish.** {', '.join(f'`{c}` (exit {n})' for c, n in FAILED)}. Whatever rests "
            f"on {'it' if one else 'them'} below was built from what the last run that did "
            f"finish left behind, so {'that section may be' if one else 'those sections may be'} "
            f"behind rather than done. The run's own output says what refused.", ""]


def unbuilt_note() -> list[str]:
    """One line naming what the sections below were built without, or nothing."""
    if not UNBUILT:
        return []
    one = len(UNBUILT) == 1
    return [f"> **{'A file' if one else f'{len(UNBUILT)} files'} this page is built from could "
            f"not be read.** {', '.join(UNBUILT)}. "
            f"{'The section it feeds is' if one else 'The sections they feed are'} absent here "
            f"for want of input rather than because {'it holds' if one else 'they hold'} "
            f"nothing. A full `python update.py` writes {'it' if one else 'them'} first.", ""]


def step_worklist(cfg, args) -> None:
    """Report what still needs the account owner, ranked by leverage.

    Open items only, and gated on live audit state: a section appears while there is something
    to do, and its absence is the report that it is done. Each item says what is open, why it is
    worth doing, and which section of `docs/SETUP.md` explains how -- the how-to stays there,
    where it is general and true whoever runs it.

    The body is one call per section, in the order the page prints them.
    """
    papers = (read_yaml(os.path.join(DATA, "papers.yaml")) or {}).get("papers", [])
    repos = (read_yaml(os.path.join(DATA, "repos.yaml")) or {}).get("repos", [])
    ident, ids = cfg["identity"], cfg["ids"]
    # Written by the audit step. Absent (audit skipped) = fall back to stored state
    # rather than guessing, and `unbuilt_note` says on the page which ones were absent.
    UNBUILT.clear()
    state = built("identity_state.json")
    scholar = built("scholar_diff.json")
    unowned = set(state.get("arxiv_unowned") or [])

    lines = ["# What still needs you", "",
             "Regenerated by `python update.py`. **Open items only** — a section that is",
             "not here is done, and nothing on this page is a general instruction. The",
             "how-to for every item below is [docs/SETUP.md](docs/SETUP.md); the live",
             "reading of each external surface is [tasks/identity_audit.md](tasks/identity_audit.md).", ""]
    lines += due_followups()
    lines += scholar_gaps(scholar, cfg)
    lines += scholar_split_records(built("scholar_strays.json"))
    lines += wikidata_coauthors(built("wikidata_coauthors.json"))
    lines += wikidata_orgs(built("wikidata_orgs.json"))
    lines += wikidata_people(built("wikidata_people.json"))
    lines += upstream_gaps(papers, cfg)

    lines += identity_surfaces(papers, state, ids)

    # Nothing here asks for an insertion -- see the docstring of scripts/wikipedia_tasks.py
    # for why the propose-a-mention version was dropped.
    lines += wikipedia_checks(built("wikipedia_state.json"))

    lines += arxiv_name_typos(papers, state)
    lines += arxiv_ownership(state, ident, unowned)
    lines += arxiv_journal_refs(papers, scholar, unowned)

    lines += hf_pages(papers, state)

    lines += same_or_different(papers)

    lines += sidecar_drafts(papers)
    lines += starving_papers(papers)

    lines += repo_gaps(repos)

    lines = next_steps(tidy(drop_hollow(apply_declines(lines))))
    # Last, because `built` is called all the way down this function. Inserted above the
    # first heading so it sits with the promise it qualifies -- the opening line saying a
    # section that is not here is done.
    if note := failed_note() + unbuilt_note():
        i = next((k for k, l in enumerate(lines) if l.startswith("## ")), len(lines))
        lines[i:i] = note
        if FAILED:
            print("  did not finish: " + "; ".join(f"{c} (exit {n})" for c, n in FAILED))
        if UNBUILT:
            print("  built without: " + "; ".join(UNBUILT))

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

    # Before the worklist, because a source that stopped answering makes every count
    # below it an undercount, and a reader who does not know that reads the run as
    # having found less to do rather than as having looked at less.
    broken = health_report()
    if broken:
        print("\nSOURCES THAT ARE NOT COMING BACK ON THEIR OWN:")
        for line in broken:
            print(f"  {line}")
        print("  Every step degraded around these, so the counts below are floors, not "
              "totals.\n  Ledger: build/health.json")

    index = os.path.join(ROOT, "build", "site", "index.html")
    if os.path.exists(index):
        print("\nThe run's output, as a reader meets it:")
        print(f"  file://{index}")

    lines = []
    worklist = os.path.join(ROOT, "WORKLIST.md")
    if os.path.exists(worklist):
        # Checkboxes, not headings, and only the ones above `## Deferred`. Counting `## `
        # counted the two headings that exist to say there is nothing to do -- the dated
        # waiting list and the deferred pile -- so the first number of the run was both
        # the wrong unit and inflated by the sections promising the least.
        n = 0
        with open(worklist) as f:
            for l in f:
                if l.startswith("## Deferred"):
                    break
                n += l.lstrip().startswith("- [ ] ")
        lines.append(f"  WORKLIST.md              {n} thing{'s' * (n != 1)} only you can do, "
                     f"ranked by citations")
    # Only the drafts a person could actually accept. Counting the stale ones here is
    # how this line came to promise 17 evenings of work that would each have ended in a
    # refused `--accept`. See sidecar_io.held.
    from sidecar_io import held, spec_sha
    drafts = [s for s in held(spec_sha()) if s]
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
                    help="read the bibliography from the local publications checkout "
                         "(needs sources.publications_path); never writes to it")
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
    if FAILED:
        # After `closing`, so the page and the summary are still written. A partial run is
        # worth reading, it is just not worth reporting as a clean one.
        raise SystemExit("\n%d step(s) did not finish: %s"
                         % (len(FAILED),
                            ", ".join(f"{c} (exit {n})" for c, n in FAILED)))


if __name__ == "__main__":
    main()
