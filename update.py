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
import glob
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from common import (DATA, has_live_sidecar, health_report, is_preprint_venue,  # noqa: E402
                    load_config, norm_title, read_yaml, synth_bibtex)
from sweep_github import ZENODO_KINDS  # noqa: E402

STEPS = ("collect", "repos", "propose", "draft", "links", "ownership", "audit",
         "validate", "render", "worklist")


def run(argv: list[str], cwd: str | None = None) -> int:
    print(f"\n$ {' '.join(argv)}", flush=True)
    return subprocess.call(argv, cwd=cwd or ROOT)


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

    Runs the Hugging Face pass again even though collect.py just fetched the same pages: ~30s
    in a multi-minute run, in exchange for both hand-worked lists coming from one moment in
    time. Deciding at read time which of two differently-aged sources is fresher is how a
    worklist starts sending you back to pages you already did.

    The Scholar diff belongs here rather than in `collect`, because it audits the collector's
    *output* against a list the collector cannot see: a paper that never entered, and a paper
    the authorship gate dropped. Report-only, and it never stops the run -- Google answers a
    crawler with a challenge page often enough that treating that as a failed run would be
    wrong.
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


def held_until(fragment: str) -> str | None:
    """The date a not-yet-due follow-up may remove the work in a section, or None.

    `covers` on a follow-up lists heading fragments. A section that matches one is work
    an outside process is scheduled to do instead, so the section says so and the date
    stays in `data/followups.yaml` alone.
    """
    import datetime
    items = (read_yaml(os.path.join(DATA, "followups.yaml")) or {}).get("followups") or []
    today = datetime.date.today()
    for i in items:
        d = i["due"]
        d = d if isinstance(d, datetime.date) else datetime.date.fromisoformat(str(d))
        if d > today and fragment in (i.get("covers") or []):
            return d.isoformat()
    return None


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
STAMP = "<!-- declines -->"

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
                   "there is no write API behind either surface — and both are ordered so",
                   "that stopping early still captures most of the value."]),
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
    ("Wikidata author strings", "run",
     "paste `tasks/wikidata_coauthors.qs` into QuickStatements. Those authors were "
     "matched ORCID to ORCID with no name compared, so the batch is the one Wikidata "
     "edit on this page that needs no judgement from you"),
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

    `apply_declines` takes a section out of `WORKLIST.md`, but the `tasks/` file that section
    handed you was written by an earlier step that knows nothing about the decision -- so it
    stays in the repo telling a reader to fill in a form the author ruled out.
    `tasks/openalex_merge.md` is the live case.

    The paths come out of the hidden text itself -- every section with a payload names its file
    in its own body -- so a section declined in future needs no wiring. Re-derived every run,
    and the marker makes a second run replace the banner rather than stack a copy on it, so
    deleting the line in `declines.yaml` removes it again.

    Not a deletion: the routes and identifiers are the work, and `deferred:` means the decision
    will be revisited. Only `sections:` and `deferred:` paths reach here -- a section that
    vanished because every *item* in it was declined is not stamped, since `common.declined`
    already filters those row by row.
    """
    done = []
    for path, why in [*((p, ("off", w)) for p, w in off.items()),
                      *((p, ("later", d)) for p, d in later.items())]:
        full = os.path.join(ROOT, path)
        if not os.path.exists(full):
            continue                  # the section names a file this run did not write
        with open(full) as f:
            body = f.read()
        if body.startswith(STAMP):
            body = body.split("\n\n", 1)[-1]
        kind, w = why
        if kind == "off":
            head = [STAMP,
                    f"> **Declined.** [`data/declines.yaml`](../data/declines.yaml) has "
                    f"`{w}` under `sections:`, so `WORKLIST.md` no longer lists this and "
                    f"nothing below is being asked of you.",
                    "> Delete that line to have it asked normally again."]
        else:
            head = [STAMP,
                    f"> **Deferred until {w.get('until', 'you say otherwise')}.** Parked "
                    f"on purpose in [`data/declines.yaml`](../data/declines.yaml), not "
                    f"declined — this is real work, just not before the rest.",
                    "> It is at the bottom of `WORKLIST.md` under *Deferred*."]
        with open(full, "w") as f:
            f.write("\n".join(head) + "\n\n" + body)
        done.append(path)
    return sorted(done)


def apply_declines(lines: list[str]) -> list[str]:
    """Drop what data/declines.yaml says has been decided against.

    The worklist is generated from live state, so it cannot tell "not done yet" from "looked at
    and declined", and a skipped decision reappears every run as though it were open.

    A post-filter over the rendered markdown rather than a check in each of the fifteen
    emitters: one place to read, and a decline matches the text the reader saw.

      sections: ["OpenAlex"]        # any heading containing this, and its body
      items:    ["2306.01708"]      # any list item containing this
      deferred: [{match: "Repo labels", until: "the papers are settled"}]

    `items` matches any bullet, not only `- [ ]` ones, so the sections that list papers rather
    than tasks can be declined too. `deferred` is a third state -- real work, not before
    something else -- and that section moves to the bottom intact, under the condition that
    releases it, still generated from live state so it stays accurate while it waits.

    Two things are reported rather than done silently: what was hidden, because a decision that
    leaves no trace is indistinguishable from a bug that ate a task; and patterns that matched
    nothing, which means either a typo or work that got done.
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

    # A section that lost its last item goes with it: a heading, four paragraphs of
    # instructions and a citation total standing over an empty list reads as an open task,
    # which is the one thing this file must not contain. Only sections that *had* items -- a
    # heading whose body is prose and a pointer has nothing to count.
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
            dropped_secs.append(head.lstrip("# ").strip() + " — every item declined")
            del out[i:j]

    # A subsection heading that counts its own list ("3 papers absent from the source
    # bibliography") over a list some of whose items were declined. The count is the
    # emitter's `pl(n)` and cannot just be dropped -- it is what tells you the size of the
    # job before reading it -- so recount it here, where what survived is known.
    #
    # Only when the number *was* the length of the list: a heading opening with a digit that
    # means something else ("2 of your 5 repos") is not a count of the bullets under it.
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
    # Reported here as well as stamped there, because the file is committed: a reader who
    # only ever opens `tasks/` should find the decision, and a reader who only ever opens
    # this one should know a file changed under them.
    stamped = stamp_payloads(off, later)
    if stamped:
        note.append("marked in " + ", ".join(f"`{p}`" for p in stamped))
    tail = [f"*Per `data/declines.yaml` — {'. '.join(note) or 'nothing hidden'}. "
            f"Delete a line there to have it asked normally again.*"]
    dead = [p for p in secs + items + [x["match"] for x in defs] if p not in used]
    if dead:
        tail += ["", "*Matching nothing this run, so doing nothing: "
                 + ", ".join(f"`{p}`" for p in dead)
                 + ". Either the work got done, or the pattern misses its line — titles"
                   " are truncated in this file, so a pattern aimed past the cut never"
                   " matches. Check before trusting it as declined.*"]
    return out + ["---", "", *tail, ""]


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


def scholar_gaps(sc: dict, cfg: dict | None = None) -> list[str]:
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
    miss = [r for r in miss if (r.get("kind") or "paper") == "paper"]
    dup = sc.get("scholar_duplicates") or []
    # A title variant is only work when nobody has already decided it. arXiv holds the current
    # title and the run has fetched it, so `stale` says which side is behind: `bib` is one edit
    # upstream, `open` is a judgement, and `scholar` is neither -- editing that row changes
    # what Scholar displays, not which citations cluster under it.
    var = sc.get("title_variants") or []
    fix = [v for v in var if v.get("stale") == "bib"]
    call = [v for v in var if v.get("stale") not in ("bib", "scholar")]
    # The mirror image of `not_in_corpus`, and the half that was computed but never
    # printed: papers this pipeline has and the profile does not. It belongs on the page
    # for the same reason as its opposite -- Scholar is the surface most people actually
    # read, and a paper absent from it is absent from where the citations accrue.
    gone = sc.get("not_on_scholar") or []
    if not (gate or miss or fix or call or dup or gone):
        return []

    def pl(n: int, word: str = "paper") -> str:
        return f"{n} {word}{'s' * (n != 1)}"

    def cites(n) -> str:
        return f"{n or 0} cite{'s' * ((n or 0) != 1)}"

    # No total in the heading: it summed six buckets, and `declines.yaml` filters this file
    # *after* it is built, so declining a bucket left a heading counting papers no longer under
    # it and no way to recount an ad-hoc phrasing. The two numbers in the body measure Scholar
    # rather than this list, and each subsection carries its own count.
    L = ["## Coverage: Google Scholar and the corpus disagree",
         "",
         f"Scholar lists **{sc.get('scholar_rows')}** works and matched "
         f"**{sc.get('matched')}** of the corpus's **{sc.get('corpus')}**. Scholar is",
         "the one list of your papers that is built by a different process, so it is the",
         "only check that can see a paper this pipeline never received.", "",
         # Was `build/scholar_diff.json` in backticks, which is a filename you cannot
         # open: `build/` is gitignored, so it is absent on GitHub and absent after a
         # clone, and it is where every "full detail" pointer on this page led. Naming
         # the command that makes it is the difference between a dead end and a step.
         "Every bucket in full, including what is truncated below:",
         "[`build/scholar_diff.json`](build/scholar_diff.json) — local only, because",
         "`build/` is not committed. `python update.py --step audit` writes it, and after",
         "a fresh clone that is the one command between you and the file.", ""]
    if gate:
        L += [f"### {pl(len(gate))} the authorship gate excluded  — a bug, or a "
              f"wrong Scholar row", "",
              "Scholar says these are yours and"
              " [`build/not_mine.json`](build/not_mine.json) — written by the same run,",
              "local only — says they are not.",
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
              "to `data/` would be overwritten on the next run. A BibTeX entry for each,",
              "resolved from arXiv, Crossref or Semantic Scholar where any of them has",
              "it, is in [`tasks/bib_missing.md`](tasks/bib_missing.md) — check the",
              "author list before pasting: it is the index's, not yours.", ""]
        # Derived from `sources.bibtex_url` rather than written out, because the one
        # external file this whole pipeline depends on is the one link worth never
        # letting drift. raw.githubusercontent -> the GitHub editor for the same file.
        edit = re.sub(r"^https://raw\.githubusercontent\.com/([^/]+/[^/]+)/(.+)$",
                      r"https://github.com/\1/edit/\2",
                      ((cfg or {}).get("sources") or {}).get("bibtex_url") or "")
        if edit.startswith("https://github.com/"):
            L += [f"Edit it here: <{edit}>", ""]
        L += [f"- [ ] {cites(r.get('citations'))} — {r.get('year') or '????'} — "
              f"{(r.get('title') or '')[:60]}" for r in miss[:12]]
        if len(miss) > 12:
            L += [f"- … and {len(miss) - 12} more in "
                  f"[`build/scholar_diff.json`](build/scholar_diff.json)"]
        L += [""]
    if gone:
        cit = sum(p.get("citations") or 0 for p in gone)
        # Stated as an upper bound, not as a loss. The old wording called these citations
        # "absent from the profile", which is exactly the inference this section can no
        # longer make: on a merged record the citations are present, counted, and on the
        # surviving title. Claiming a loss made the sum an argument for adding papers that
        # were already there.
        held = ([f"Together these carry **{cit} citations** in the corpus. Treat that as",
                 "the most this could be worth, not as citations you are missing — on a",
                 "merged record they are already counted under the surviving title."]
                if cit else [])
        L += [f"### {pl(len(gone))} whose title does not appear on your Scholar profile",
              "",
              "That is all this check knows, and the heading says so deliberately. It reads",
              "the profile listing, which shows **one title per record** — so a paper Scholar",
              "has folded into another record is indistinguishable here from a paper Scholar",
              "does not have. Both look like a title that is not in the list.",
              "",
              "**So check for a merge before adding anything.** Scholar merges a call for",
              "papers into the findings paper of the same workshop, and a preprint into its",
              "retitled successor — the citations are all on the surviving record, which is",
              "the outcome you want. Adding the folded paper by hand does not recover",
              "anything; it creates a second record that splits future citations.",
              "",
              "Open <https://scholar.google.com/citations?user="
              f"{sc.get('scholar_profile')}&view_op=list_works&sortby=pubdate> and look for",
              "the related record — the findings paper, the newer title. If your paper is",
              "inside it, decline the line here and you will not be asked again. Only if",
              "nothing on the profile covers it is *+ → Add article manually* the fix."]
        L += held + ["",
                     "Declining is one line in [`data/declines.yaml`](data/declines.yaml)"
                     " under `items:`.", ""]
        for p in gone:
            ref = (f" <https://arxiv.org/abs/{p['arxiv']}>" if p.get("arxiv")
                   else f" <https://doi.org/{p['doi']}>" if p.get("doi")
                   else f" <{p['url']}>" if p.get("url") else "")
            L += [f"- [ ] {cites(p.get('citations'))} — {p.get('year') or '????'} — "
                  f"{(p.get('title_display') or p.get('title') or '')[:58]}{ref}"]
        L += [""]
    if fix:
        L += [f"### {pl(len(fix))} whose bibliography title is behind arXiv", "",
              "arXiv states the title Scholar shows, so the source entry is the stale",
              "one and there is nothing to decide: correct the title in the source",
              "bibliography and re-run. Until then the two surfaces answer a title query",
              "differently, which is the exact failure this repo exists to prevent.", ""]
        L += [f"- [ ] `{v.get('slug')}`\n"
              f"      - arXiv and Scholar: {(v.get('scholar') or '')[:56]}\n"
              f"      - the .bib entry:    {(v.get('corpus') or '')[:56]}"
              for v in fix] + [""]
    if call:
        L += [f"### {pl(len(call))} under two titles, with no arXiv record to break the "
              f"tie", "",
              "Same paper, two names, and arXiv confirms neither — so this one is a",
              "judgement. Decide which is canonical and set it in",
              "[`data/overrides.yaml`](data/overrides.yaml).", ""]
        L += [f"- [ ] `{v.get('slug')}`\n"
              f"      - scholar: {(v.get('scholar') or '')[:64]}\n"
              f"      - corpus:  {(v.get('corpus') or '')[:64]}" for v in call] + [""]
    if dup:
        L += [f"### {pl(len(dup))} listed twice on Scholar", "",
              "Two rows for one paper splits its citation count, and nothing here can fix",
              "it: tick both rows and press *Merge*. Both titles are below, because on the",
              "profile they sort apart and neither reads as the other's duplicate.", "",
              "Open <https://scholar.google.com/citations?user="
              f"{sc.get('scholar_profile')}&view_op=list_works&sortby=title>.", ""]
        for d in dup:
            L += [f"- [ ] `{d.get('slug')}`",
                  f"      - one row: {(d.get('corpus') or '')[:64]}",
                  f"      - the other: {(d.get('scholar') or '')[:64]}"
                  + (f" — <{d['scholar_url']}>" if d.get("scholar_url") else "")]
        L += [""]
    return L


def scholar_split_records() -> list[str]:
    """The worklist section for `build/scholar_strays.json`, or nothing.

    Only the two passes whose remedy is one merge each. The `not in the bibliography`
    pass lands in `tasks/scholar_strays.md` and not here -- it is a list to read, not a
    list of edits, and most of its rows are other people.
    """
    try:
        with open(os.path.join(ROOT, "build", "scholar_strays.json")) as f:
            st = json.load(f)
    except (OSError, ValueError):
        return []
    rows = [dict(r, kind="undercount") for r in st.get("undercounted") or []]
    rows += [dict(r, kind="name form") for r in st.get("typo_records") or []
             if r.get("matched")]
    rows += [dict(r, kind="split", gap=sum(x["citations"] for x in r["records"][1:]))
             for r in st.get("split_records") or []]
    if not rows:
        return []
    rows.sort(key=lambda r: -(r.get("gap") or r.get("citations") or 0))
    at_stake = sum(r.get("gap") or r.get("citations") or 0 for r in rows)
    L = [f"## Citations on a Scholar record you cannot see ({len(rows)}, "
         f"~{at_stake} citations)", "",
         "Scholar indexes preprints and theses the APIs do not, so a profile row should",
         "always count *more* than OpenAlex and Semantic Scholar. Where it counts less,",
         "the rest of the count is on a second record Scholar parsed out of somebody's",
         "reference list — a mangled title, a misspelled author, initials only. Merging",
         "the two adds those citations to yours.", "",
         "Each row is a search. Open it, and if a result is your paper under a second",
         "record, tick your own row and that one on your profile and press *Merge*. A",
         "gap can also be plain indexing lag, so read the result before merging: a wrong",
         "merge attaches somebody else's paper to your name.", "",
         "Full detail, including the 200-odd records filed under an initials-only form of",
         "your name: [`tasks/scholar_strays.md`](tasks/scholar_strays.md).", ""]
    for r in rows[:15]:
        gap = r.get("gap") or r.get("citations") or 0
        why = (f"Scholar {r['scholar_citations']} vs {r['index_citations']} at the APIs"
               if r["kind"] == "undercount" else
               f"filed as *{r.get('searched_as')}* at {r.get('index')}"
               if r["kind"] == "name form" else
               f"{len(r['records'])} OpenAlex records for one title")
        L += [f"- [ ] **{gap} citations** — {(r.get('title') or '')[:64]}",
              f"      - {why}",
              f"      - [search Scholar for it]({r['search']})"]
    if len(rows) > 15:
        L.append(f"- … and {len(rows) - 15} more in "
                 "[`tasks/scholar_strays.md`](tasks/scholar_strays.md), same order")
    return L + [""]


def wikidata_coauthors() -> list[str]:
    """The worklist section for `build/wikidata_coauthors.json`, or nothing.

    Ranked by the batch first, because that half needs no judgement at all.
    """
    try:
        with open(os.path.join(ROOT, "build", "wikidata_coauthors.json")) as f:
            st = json.load(f)
    except (OSError, ValueError):
        return []
    left = (st.get("review") or 0) + (st.get("leftover") or 0)
    if not (st.get("edits") or left or st.get("venues") or st.get("fills")):
        return []
    L = [f"## Wikidata author strings ({st.get('edits', 0)} batchable, "
         f"{left} by hand)", "",
         "Every paper item lists you as *author* and each co-author as *author name",
         "string*, which is a literal nothing can join on — so each item hangs off your",
         "item alone. Resolving a string to that person's own item is what connects them,",
         "and many independent paths into your item is the point of having them at all.", ""]
    if st.get("edits"):
        L += [f"- [ ] **{st['edits']} authors, no judgement needed** — paste "
              "[`tasks/wikidata_coauthors.qs`](tasks/wikidata_coauthors.qs) into "
              "QuickStatements",
              "      - each one matched ORCID to ORCID, with no name compared"]
    if st.get("venues"):
        L += [f"- [ ] **{st['venues']} papers get their venue** — in the same paste, "
              "*published in* pointing at the proceedings volume or journal",
              "      - resolved from the venue name already in the bibliography"]
    if st.get("fills"):
        L += [f"- [ ] **{st['fills']} language and full-text statements** — also in that "
              "paste, *language of work* and *full work available at*",
              "      - both taken straight from the bibliography"]
    if left:
        L += [f"- [ ] **{left} strings across {st.get('papers_left', 0)} papers** — one "
              "Author Disambiguator pass per paper, most-cited first",
              "      - the links, and the candidate items found for each name: "
              "[`tasks/wikidata_coauthors.md`](tasks/wikidata_coauthors.md)"]
        if st.get("dropped"):
            L += [f"      - {st['dropped']} name matches are left out as namesakes, on a "
                  "stated occupation nothing like research"]
    return L + [""]


def wikidata_people() -> list[str]:
    """The worklist section for `build/wikidata_people.json`, or nothing.

    Only the people the code cannot decide about. Creating the rest, and adding their
    ORCIDs, is `scripts/wikidata_people.py --apply`.
    """
    try:
        with open(os.path.join(ROOT, "build", "wikidata_people.json")) as f:
            st = json.load(f)
    except (OSError, ValueError):
        return []
    held = [p for p in st.get("held_people") or [] if len(p["namesakes"]) == 1]
    if not held:
        return []
    many = len(st.get("held_people") or []) - len(held)
    L = [f"## Co-authors who may already have a Wikidata item ({len(held)})", "",
         "Wikidata has one human item under each of these names and it states no ORCID, so",
         "it is either this co-author reached from a paper rather than a profile, or a",
         "namesake. Open the item, and if the papers on it are theirs write the answer into",
         "[`data/overrides.yaml`](data/overrides.yaml) under `wikidata_people`:",
         "",
         "```yaml",
         "wikidata_people:"]
    held.sort(key=lambda x: (-x.get("papers", 0), x["label"]))
    for p in held:
        L.append(f"  {p['orcid']}: {p['namesakes'][0]['qid']}   "
                 f"# {p['label']}, or `new` if that item is somebody else")
    L += ["```", ""]
    for p in held:
        n = p["namesakes"][0]
        papers = p.get("papers", 0)
        L.append(f"- [ ] **{p['label']}** ({papers} paper{'' if papers == 1 else 's'} with "
                 f"you) — [{n['qid']}](https://www.wikidata.org/wiki/{n['qid']}) against "
                 f"[their ORCID record](https://orcid.org/{p['orcid']}), {p['description']}")
    L += ["",
          "Nothing else follows by hand. The next run adds the ORCID to the item, or creates a",
          "separate one, and writes the *author* statements from it."]
    if many:
        L += ["",
              f"{many} more names collide with several items each, which no glance settles. "
              "Those wait for",
              "a bibliography match rather than a decision."]
    return L + [""]


def wikidata_orgs() -> list[str]:
    """The worklist section for `build/wikidata_orgs.json`, or nothing."""
    try:
        with open(os.path.join(ROOT, "build", "wikidata_orgs.json")) as f:
            st = json.load(f)
    except (OSError, ValueError):
        return []
    if not (st.get("create") or st.get("edges") or st.get("ambiguous")):
        return []
    names = [st["state"][s].get("label") or s for s in st.get("create") or []]
    L = [f"## Wikidata items for the groups ({len(st.get('create') or [])} to create)", "",
         "Some of the work in the corpus is run by groups Wikidata has no item for, so a",
         "paper cannot say what it is part of and a group cannot say what it produced.",
         "Every statement in the batch cites the public page it came from.", ""]
    if st.get("create"):
        L += [f"- [ ] **create {', '.join(names)}** — paste "
              "[`tasks/wikidata_orgs.qs`](tasks/wikidata_orgs.qs) into QuickStatements",
              "      - the statements and their sources, and the facts still missing: "
              "[`tasks/wikidata_orgs.md`](tasks/wikidata_orgs.md)"]
    if st.get("edges"):
        L += [f"- [ ] **{st['edges']} edges into those items** — in the same paste, "
              "*main subject* on each paper about them and *organizer* on each event",
              "      - resolved through the item ledger, so nothing to look up"]
    if st.get("ambiguous"):
        L += [f"- [ ] **{len(st['ambiguous'])} names match more than one item** — pick the "
              "right one by hand, or the group has an item already",
              "      - the candidates: "
              "[`tasks/wikidata_orgs.md`](tasks/wikidata_orgs.md)"]
    if st.get("needs"):
        L += [f"- [ ] **{st['needs']} statements wait on a fact only you have** — "
              "add them to [`data/wikidata_orgs.yaml`](data/wikidata_orgs.yaml)",
              "      - each one, and why the public pages do not settle it: "
              "[`tasks/wikidata_orgs.md`](tasks/wikidata_orgs.md)"]
    return L + [""]


def upstream_gaps(papers: list[dict], cfg) -> list[str]:
    """Papers the corpus has only because an override put them there.

    `extra_arxiv` and `extra_openreview` are stopgaps covering the interval before the entry
    lands in the bibliography, and both files say to delete the line after. Nothing else can
    report them: the Scholar block finds missing papers by diffing Scholar against the corpus,
    and an override closes exactly that gap.

    `_override` is provenance, not a decision -- `collect.py` sets it on records it adds from an
    override, and it disappears once the bibliography's own entry merges, so a paper still
    carrying it is still absent upstream.

    The second half reads `overrides.yaml` as well as the corpus, for the override lines left
    behind after the paste lands.
    """
    L = []
    pend = sorted((p for p in papers if p.get("_override")),
                  key=lambda p: -(p.get("citations") or 0))
    edit = re.sub(r"^https://raw\.githubusercontent\.com/([^/]+/[^/]+)/(.+)$",
                  r"https://github.com/\1/edit/\2",
                  ((cfg or {}).get("sources") or {}).get("bibtex_url") or "")
    if pend:
        L += [f"## {len(pend)} paper{'s' * (len(pend) != 1)} in the corpus that the "
              f"bibliography does not have", "",
              "Added by `extra_arxiv` or `extra_openreview` in",
              "[`data/overrides.yaml`](data/overrides.yaml), so each has a page and a "
              "canonical",
              "URL already — this is not about the site. It is that the bibliography is this",
              "pipeline's only real input, and every run these papers depend on a line in an",
              "override file instead. Paste the entry upstream and delete that line.", ""]
        if edit.startswith("https://github.com/"):
            L += [f"Edit the bibliography here: <{edit}>", ""]
    for p in pend[:5]:
        # Synthesised from the fetched record, which is why the citation key is not one to
        # keep: the bibliography assigns keys, and the reason these records carry no
        # `bibtex` of their own is that an invented key competing with the published one
        # is the split this project exists to avoid. Paste the fields, not the key.
        L += [f"- [ ] **{(p.get('title_display') or p.get('title') or '')[:66]}** — "
              f"`{p['_override']}`, {p.get('citations') or 0} cites", "",
              "  ```bibtex", *(f"  {ln}" for ln in synth_bibtex(p).splitlines()),
              "  ```", ""]
    if len(pend) > 5:
        L += [f"- … and {len(pend) - 5} more, listed in `data/overrides.yaml`", ""]

    # A line is spent when the corpus has its paper *without* the marker: the record came
    # from the bibliography this run, so the override added nothing. Matched on the same
    # keys `collect.py` adds by -- an arXiv id, a normalised title -- so a line that never
    # resolved to a paper at all is not reported here as done. That one is already loud:
    # the collector prints `! extra_openreview: OpenReview has no accepted paper titled`.
    ov = read_yaml(os.path.join(DATA, "overrides.yaml")) or {}
    from_bib = [p for p in papers if not p.get("_override")]
    ids = {p["arxiv"] for p in from_bib if p.get("arxiv")}
    titles = {norm_title(p.get("title") or "") for p in from_bib}
    spent = [("extra_arxiv", str(i).strip()) for i in (ov.get("extra_arxiv") or [])
             if str(i).strip() in ids]
    spent += [("extra_openreview", str(t).strip())
              for t in (ov.get("extra_openreview") or [])
              if norm_title(str(t).strip()) in titles]
    if spent:
        L += [f"## {len(spent)} override line{'s' * (len(spent) != 1)} the bibliography "
              f"has made redundant", "",
              "The good outcome, and the last step of it. Each of these is in",
              "[`data/overrides.yaml`](data/overrides.yaml) to cover the interval before the",
              "paper reached the bibliography, and the bibliography now has it — the corpus",
              "record carries its published citation key. Deleting the line changes no",
              "output; leaving it means the next reader cannot tell which lines are still",
              "load-bearing, which is how a stopgap becomes part of the design.", ""]
        for k, v in spent:
            L.append(f"- [ ] `{k}:` delete `{v[:60]}`")
        L.append("")
    return L


def orcid_missing_items(slugs: list[str], by_slug: dict) -> list[str]:
    """The missing papers, with the entry ORCID will import shown per paper.

    ORCID's BibTeX route takes a *file*, so the payload the reader needs at hand is a path --
    but a file they cannot see the inside of is one they have to open in another tab before
    putting it on their own record. So up to three entries are shown inline, which is the
    length at which this reads as "check these" instead of "scroll past this". Above that,
    titles and citations only: the decision has collapsed into one upload, and
    `tasks/orcid_missing.md` carries the per-paper detail.
    """
    rows = [by_slug.get(s) or {"slug": s} for s in slugs]
    if len(rows) > 3:
        return ([f"- [ ] {p.get('citations') or 0} cites — "
                 f"{(p.get('title') or p['slug'])[:66]}" for p in rows[:8]]
                + ([f"- … and {len(rows) - 8} more in "
                    "[`tasks/orcid_missing.md`](tasks/orcid_missing.md)"]
                   if len(rows) > 8 else []))
    out = []
    for p in rows:
        out += [f"- [ ] **{(p.get('title') or p['slug'])[:66]}** — "
                f"{p.get('citations') or 0} cites — what the file will add:", "",
                "  ```bibtex",
                *(f"  {ln}" for ln in (p.get("bibtex") or synth_bibtex(p)).strip().splitlines()),
                "  ```", ""]
    return out


def step_worklist(cfg, args) -> None:
    """Report what still needs the account owner, ranked by leverage.

    Open items only, and gated on live audit state: a section appears while there is something
    to do, and its absence is the report that it is done. Each item says what is open, why it is
    worth doing, and which section of `docs/SETUP.md` explains how.

    The how-to lives in SETUP.md, which is general, published and true whoever runs it.
    Printing it here instead went stale -- a static recipe cannot know that steps 1-4 are
    finished -- and buried the three lines that were open in four hundred that were not.
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
    lines += scholar_gaps(scholar, cfg)
    lines += scholar_split_records()
    lines += wikidata_coauthors()
    lines += wikidata_orgs()
    lines += wikidata_people()
    lines += upstream_gaps(papers, cfg)

    # The papers themselves and not just their count: the URL to paste into the Add
    # Papers form is a field on each one, so a section that reports only how many there
    # are has sent the reader to a second file for the one thing it is asking them to do.
    strays = sorted([p for p in papers if p.get("s2_author_record") in
                     [a for a in ids["semantic_scholar"]
                      if a != ids["semantic_scholar_primary"]]],
                    key=lambda p: -(p.get("citations") or 0))
    n_strays = len(strays)

    # Each entry: (predicate, heading, body lines). Built as data so the whole
    # identity block is one loop and adding a surface is one tuple -- the previous
    # version inlined every surface unconditionally, which is how it went stale.
    o_miss = state.get("orcid_missing_papers") or []
    o_conf = state.get("orcid_strays_confirmed") or []
    o_dupg = state.get("orcid_duplicate_groups") or []
    o_bad = state.get("orcid_misfiled_ids") or []
    facets = ((state.get("orcid_missing_variants") or [])
              + (state.get("orcid_missing_keywords") or [])
              + (state.get("orcid_missing_other_pages") or [])
              + ([] if state.get("orcid_has_canonical_url", True) else ["canonical URL"]))
    by_slug = {p["slug"]: p for p in papers}

    def misfiled_item(b: dict) -> list[str]:
        """One misfiled ORCID identifier, carrying every value the edit needs.

        This section used to say what the failure was, then send you to
        `tasks/identity_audit.md` for the put-code, the DOI to take off and the DOI to
        put on. Three values, one line each, and the file that has them is a second file
        -- so the item on the page you are working from named none of them and the
        instruction "replace the DOI" had no object.
        """
        p = by_slug.get(b.get("should_be")) or {}
        title = p.get("title_display") or p.get("title") or b.get("should_be") or "?"
        out = [f"- [ ] **{title[:66]}** — put-code `{b['put']}`"]
        doi = b.get("carried_doi")
        if doi:
            # Linked, because the link is the evidence: following the identifier that is
            # on your own record lands on a paper that is not this one.
            out.append(f"      - remove `{doi}` — it resolves to "
                       f"[{(b.get('carried_title') or 'another paper')[:44]}]"
                       f"(https://doi.org/{doi}), a different paper")
        else:
            out.append("      - remove the identifier it carries: "
                       f"`{', '.join(b.get('carries') or ['?'])}`")
        if b.get("should_carry"):
            out.append(f"      - add `{b['should_carry']}` — the DOI of the paper this "
                       f"entry actually is")
        elif p.get("arxiv"):
            out.append(f"      - add the arXiv id `{p['arxiv']}`, identifier type "
                       f"`arxiv`. This paper has no DOI, and an entry carrying no "
                       f"identifier at all is what makes ORCID read it as missing")
        else:
            out.append("      - add nothing — this paper has neither a DOI nor an arXiv "
                       "id, so taking the wrong one off is the whole fix")
        return out + [""]

    def dup_item(r: dict) -> list[str]:
        """One ORCID duplicate pair: which entry to open, and the one value to paste."""
        if r.get("doi"):
            return [f"- [ ] **{r['title'][:60]}** — open put-code `{r['keep']}` "
                    f"(*{r['keep_title'][:38]}*) and add the DOI `{r['doi']}`, which is "
                    f"the one on put-code `{r['folds']}` (*{r['folds_title'][:38]}*)", ""]
        # No arXiv-DOI entry, or more than two: naming every entry is the honest form,
        # because which one has the venue is a judgement and this is not making it.
        return [f"- [ ] **{r['title'][:60]}** — {len(r['entries'])} entries: "
                + "; ".join(f"`{e['put']}` ({e['doi'] or 'no DOI'})"
                            for e in r["entries"])
                + ". Open whichever has the venue and add one of the others' DOIs.", ""]

    # Absent from Wikidata and not creatable: no DOI, no arXiv id, so no key to check
    # against. Named here rather than inline because the difference between the two
    # counts is the only honest way to say why the command below creates fewer items
    # than the paragraph above it describes.
    wd_nokey = ((state.get("wikidata_papers_absent") or 0)
                - (state.get("wikidata_papers_creatable") or 0))

    ident_items = [
        (bool(o_miss),
         f"### ORCID is missing {len(o_miss)} of your {len(papers)} papers",
         ["Highest leverage on this page. Semantic Scholar's disambiguation and",
          "OpenAlex's profile merges are both ORCID-driven, so this is the one fix that",
          "makes the others more likely to fix themselves.", "",
          "One upload, not one form per paper. At <https://orcid.org/my-orcid#works>:",
          "*+ Add → Add BibTeX → Choose file* →",
          "[`tasks/orcid_missing.bib`](tasks/orcid_missing.bib) (only the missing ones) or",
          "[`tasks/orcid_import.bib`](tasks/orcid_import.bib) (all of them; ORCID groups on",
          "shared identifiers, so re-importing what is already there merges rather than",
          "duplicates). It previews the entries and you confirm — nothing lands unseen.",
          "Why it matters, once:",
          "[docs/SETUP.md §1](docs/SETUP.md#1-orcid--populate-it-then-wire-it-everywhere).", ""]
         + orcid_missing_items(o_miss, by_slug)),
        (bool(o_conf),
         f"### ORCID lists {len(o_conf)} work that is not yours"
         if len(o_conf) == 1 else
         f"### ORCID lists {len(o_conf)} works that are not yours",
         ["A wrong work on your record is worse than a missing one: it is the thing that",
          "makes an automated merge distrust the record. *Works → the entry → Delete.*",
          "Put-codes and titles: `tasks/orcid_remove.md`.", ""]),
        # Before the duplicate and the missing-paper sections, because it is what puts
        # entries in them -- and it was the one **fix** in the audit table that this page
        # never listed, so the only way to meet it was to open `identity_audit.md` on
        # your own initiative. A worklist that omits the item it tells you to do first is
        # worse than one that omits it silently.
        (bool(o_bad),
         f"### {len(o_bad)} work on your ORCID carries another paper's identifier"
         if len(o_bad) == 1 else
         f"### {len(o_bad)} works on your ORCID carry another paper's identifier",
         ["**Do this before the rest of this section.** A work whose DOI belongs to a",
          "different paper is filed by ORCID into *that* paper's group — grouping is on",
          "shared identifiers and there is nothing else it can go on. So the real paper",
          "ends up with no identifier on the record and reads as missing, the group that",
          "absorbed it reads as listed twice, and both of the obvious fixes make it",
          "worse: adding the paper creates a second copy, merging the group destroys a",
          "distinct work.", "",
          "Each item below is one edit, and every value it needs is in the item — the",
          "work to open, the identifier to take off it, the one to put on. Open",
          "<https://orcid.org/my-orcid#works>, find the work by its title, then the pencil",
          "icon → under *Identifiers* replace the DOI → *Save changes*. **Edit it; do not",
          "delete and re-add** — the put-code is what carries the entry's citations and its",
          "source attribution, and a new entry starts with neither.", "",
          "The carried DOI is linked so you can see for yourself that it resolves to",
          "somebody else's paper before you touch anything. Nothing else needs deleting:",
          "one identifier is replaced by another and the work itself stays.", ""]
         + [ln for b in o_bad for ln in misfiled_item(b)]),
        (bool(o_dupg),
         f"### ORCID lists {len(o_dupg)} of your papers twice",
         ["ORCID groups works that share an identifier. Two groups for one paper means",
          "one copy carries the arXiv DataCite DOI (`10.48550/arXiv.<id>`) and the other",
          "the publisher DOI, so they share no key.", "",
          "**Merge, do not delete.** Both titles are real — one is the preprint's, one is",
          "what the paper was called on acceptance — and adding one entry's DOI to the",
          "other folds them into a single work carrying both, with no entry losing its",
          "citations or its source attribution. Open the **keep** entry at",
          "<https://orcid.org/my-orcid#works>, the pencil icon → **+ Add identifier** →",
          "type `doi` → paste the value below → *Save*. The pair collapses on the next",
          "page load.", ""]
         + [ln for r in (state.get("orcid_duplicate_pairs") or []) for ln in dup_item(r)]
         + ["Delete instead only if you would rather have one entry than a grouped pair —",
            "same number of clicks, and the preprint title stops being findable on your",
            "record.",
            "",
          # Points at the section above when there is one, and at the audit when there is
          # not. A "do that first" whose target is not on the page is an instruction the
          # reader has to go and look for, and the answer is usually "there was nothing".
          ("**Do the misfiled-identifier section above first.**" if o_bad else
           "If [the misfiled-identifier section](tasks/identity_audit.md) ever has"
           " anything in it, do that first."),
          "A work carrying the wrong DOI lands in another paper's group and shows up",
          "here as a duplicate that merging would destroy.", ""]),
        (bool(facets),
         f"### ORCID facet fields ({len(facets)} still empty)",
         ["Separate from works, and two minutes: *Also known as*, *Keywords*, *Websites*.",
          "Exactly which are missing, with the values ready to paste:",
          "`tasks/identity_audit.md`.", ""]),
        (n_strays > 0,
         f"### Semantic Scholar — {n_strays} papers on a second author record",
         (["Every S2-backed tool (Elicit, Consensus, SciSpace, most literature agents)",
           "resolves you to one page, so each currently sees about half the corpus.",
           "Support has already been asked to merge the two records and declined, so the",
           "self-service route is the only one: a claimed page can pull papers across one",
           "at a time.", ""]
          + ([f"**Worth waiting until {held_until('Semantic Scholar —')} before starting.**",
              "S2 re-clusters authors off ORCID, the ORCID record already asserts every",
              "paper here, and re-clustering would move all of them at no cost to you. It",
              "cannot merge the two records, so the second one stays either way — but the",
              "pastes below may be work that does itself.", ""]
             if held_until("Semantic Scholar —") else []) + [
          f"1. Open your claimed page: <https://www.semanticscholar.org/author/"
          f"{ids['semantic_scholar_primary']}>",
          "2. *Edit Author Page → Add Papers*.",
          "3. Paste a paper's S2 URL, pick it, and choose *the author is correct, but the",
          "   paper is missing from my author page*. Changes appear in about 24 hours.",
          "",
          "Highest-citation first, so stopping early still captures most of the loss.",
          "**Do not claim the second page as well** — a second claimed record is harder to",
          "undo than an unclaimed one, and it makes the split look deliberate.", ""])
         + [f"- [ ] {p.get('citations') or 0} cites — "
            f"{(p.get('title_display') or p['title'])[:56]} — "
            + (f"<https://www.semanticscholar.org/paper/{p['s2_corpus_id']}>"
               if p.get("s2_corpus_id") else
               "**no S2 id known** — search the title on the Add Papers form")
            for p in strays[:12]]
         + ([f"- … and {len(strays) - 12} more in "
             "[`tasks/s2_merge.md`](tasks/s2_merge.md), same order"]
            if len(strays) > 12 else []) + [""]),
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
        (bool(state.get("wikidata_papers_creatable")),
         f"### Wikidata — {state.get('wikidata_papers_creatable')} of your papers "
         f"have no item",
         # Listed under "only you can do this" for the decision, not the labour -- these are
         # permanent pages on a wiki that is not yours, and the undo is a deletion request
         # rather than a click.
         #
         # The count is `creatable`, not `absent`: a paper with neither a DOI nor an arXiv id
         # stays absent, and a heading of 109 over a command that creates 108 is a count that
         # does not match its list.
         ["Same bot password, and the same statements as the QuickStatements batch in",
          "`tasks/wikidata_papers.qs` — which is now only the fallback. This is where",
          f"`{state.get('wikidata') or 'your author item'}` gets the incoming author",
          "links that make a Scholia profile and a SPARQL-answerable corpus exist at",
          "all.", ""]
         + ([f"{wd_nokey} more have no item either and are not in the command below:",
             "they carry neither a DOI nor an arXiv id, so there is no key to check",
             "Wikidata against and creating one risks a duplicate nobody can find. They",
             "arrive here once the paper is deposited anywhere.", ""]
            if wd_nokey > 0 else [])
         + [
          "```bash",
          "python scripts/wikidata_apply.py --papers                    # what it would create",
          "python scripts/wikidata_apply.py --papers --apply --limit 10  # ten of them",
          "```", "",
          "In batches, and this is the reason: ten items finds a wrong statement on item",
          "3 rather than on item 103, and an item is harder to retract than anything else",
          "here. Each one is recorded in `data/wikidata_created.yaml` as it lands, so",
          "stopping and resuming creates nothing twice — the query service lags hours",
          "behind the edit and that file is what covers the gap.", "",
          "Once this list is empty the monthly CI run keeps up with new papers by itself.",
          "It refuses while a backlog exists, so it is doing nothing until you start.",
          "Cautions worth reading once: [`tasks/wikidata_followup.md`]"
          "(tasks/wikidata_followup.md).", ""]),
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

    # Wikipedia: corrections only. Read from build/wikipedia_state.json because the ~100 API
    # calls behind it belong to the audit step, not to rendering the worklist. Nothing here
    # asks for an insertion -- see the docstring of scripts/wikipedia_tasks.py for why the
    # propose-a-mention version was dropped.
    try:
        with open(os.path.join(ROOT, "build", "wikipedia_state.json")) as f:
            wiki = json.load(f)
    except (OSError, ValueError):
        wiki = {}
    wiki_items = [(t, [t]) for t in wiki.get("already_mentions") or []]
    wiki_items += [(c["term"], c["articles"]) for c in wiki.get("checks") or []]
    if wiki_items:
        n_arts = len({a for _t, arts in wiki_items for a in arts})
        lines += [f"## Wikipedia mentions {len(wiki_items)} of your coinages across "
                  f"{n_arts} article(s) — check the facts", "",
                  "Wikipedia carries roughly half the citations in AI answers, and WP:COI",
                  "means you may not edit these. What you *can* do is the thing only an",
                  "author can: notice that a description is wrong. If it reads correctly,",
                  "tick it and move on — that is the expected outcome.",
                  "",
                  "A correction goes on the talk page, with the corrected value and the page",
                  "or table it comes from. Never in the article, and never a citation of your",
                  "own work — that is the edit that gets reverted on sight.", ""]
        for term, arts in wiki_items:
            links = ", ".join(f"[{a}](https://en.wikipedia.org/wiki/{a.replace(' ', '_')}) "
                              f"([talk](https://en.wikipedia.org/wiki/Talk:"
                              f"{a.replace(' ', '_')}))" for a in arts)
            lines.append(f"- [ ] **{term}** — {links}")
        lines += ["",
                  f"The {wiki.get('absent', 0)} coinages Wikipedia does not mention are "
                  f"listed in",
                  "[`tasks/wikipedia.md`](tasks/wikipedia.md) as deliberately not "
                  "actionable, along with",
                  "the field articles you could improve with other people's sources.", ""]

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

    def subm_ids() -> list[str]:
        """The five-minute step that turns "find the row" into a link, or nothing.

        The submission id the journal-ref form is addressed by appears on exactly one page in the
        world, your own articles list, and `robots.txt` disallows it -- so the only route is a copy
        of the page saved by hand, and the only reason to save it is that it removes a search from
        every one of sixty rows. Stated as a step of its own, rather than as a closing sentence,
        which is where a prerequisite goes to be skipped.

        Empty once every listed paper has an id -- empty rather than "all done", which would be one
        more line asserting that something you cannot see is fine.
        """
        want = [str(p["arxiv"]) for p in papers if needs_jr(p)]
        have = read_yaml(os.path.join(DATA, "arxiv_submissions.yaml")) or {}
        n = sum(1 for a in want if a in have)
        if not want or n >= len(want):
            return []
        # Agrees with itself at n == 1, which is the number this actually runs at: two
        # ids got cached while the ingester was being tested, so the first thing anyone
        # reads under this heading is the sentence about the other sixty.
        one = n == 1
        return [
            f"**Five minutes first, if you are doing more than a couple.** {n} of the",
            f"{len(want)} rows {'has' if one else 'have'} a direct link into "
            f"{'its' if one else 'their'} own form;",
            f"the other {len(want) - n} have to be found by eye on that list. The id the",
            "form is addressed by is only ever shown on your own articles page, and arXiv's",
            "`robots.txt` disallows fetching it — so the route is a copy you save:",
            "",
            "1. Sign in and open <https://arxiv.org/user>.",
            "2. Save the page — ⌘S, *Page Source* is enough.",
            "3. `python scripts/identity_tasks.py --user-page ~/Downloads/arxiv-user.html`",
            "",
            "Submission ids never change, so this is once and not per run, and nothing is",
            "requested on your behalf at any point — the code reads the file you saved.",
            "After it, every entry in [`tasks/arxiv_jref.md`](tasks/arxiv_jref.md) opens",
            "its own form.",
            "",
        ]

    missing_jr = top(needs_jr, 12)
    if missing_jr:
        blocked = sum(1 for p in papers if p.get("arxiv") in unowned and needs_jr(p))
        # The cost line comes first and is measured, because the earlier version of this
        # section led with "Google Scholar keeps two records" and that turned out to be
        # the weakest of the three reasons *for this corpus*: the profile has almost no
        # split pairs. Selling the strongest-sounding argument rather than the true one
        # is how a list of 64 items gets read once and never again.
        dups = len(scholar.get("scholar_duplicates") or [])
        seen_n = scholar.get("corpus")
        split = ([f"   Measured on your own profile: **{dups} split pair"
                  f"{'s' * (dups != 1)} out of {seen_n}**, so for this",
                  "   corpus that is mostly already handled — do not do this for that reason."]
                 if seen_n else
                 ["   Scholar appears to have merged most of yours already, so this is not "
                  "the reason to do it."])
        lines += [f"## arXiv journal-ref missing ({sum(1 for p in papers if needs_jr(p))} papers)",
                  "",
                  "**It is a metadata edit, not a new version.** No recompile, no file upload,",
                  "no new version number, no re-announcement — v2 stays v2, per arXiv's own",
                  "help page. That is the whole cost, about a minute each, and it is worth",
                  "knowing because the size of this list is not the size of the job.",
                  "",
                  "The form is per-paper and lives behind your account: open",
                  "<https://arxiv.org/user>, find the row, follow its *journal ref* link.",
                  "There is no paste-an-identifier page — `/jref` on its own redirects to that",
                  "list — which is also why no script can do this for you.",
                  ""] + subm_ids() + [
                  "**What it buys, honestly ranked.**",
                  "",
                  "1. *Weak here.* Scholar merges preprint and published versions largely on",
                  "   venue agreement, and a venue-less arXiv record can stay a separate",
                  "   cluster with the citations split across the two."] + split + [
                  "2. **The arXiv DataCite record gains a `container-title`.** This is the real",
                  "   one and it is not visible on Scholar at all: that field is what flows to",
                  "   OpenAlex, to ORCID auto-update, and to every Crossref-derived tool, and",
                  "   a venue-less record is filtered out by anything ranking on venue.",
                  "3. **Answer engines cite venue as authority.** \"Published at ACL 2024\" in",
                  "   the metadata is what makes a model's answer name the venue instead of",
                  "   calling it a preprint.",
                  "",
                  "**Recommendation:** the top few, when you are already logged in, and stop.",
                  "There is no write API, so the clicking is the one part of this list code",
                  "cannot take off you — but the typing is not: both field values are below,",
                  "per paper, built from the publisher's own bibtex. The same for all",
                  f"{sum(1 for p in papers if needs_jr(p))} is in "
                  "[`tasks/arxiv_jref.md`](tasks/arxiv_jref.md).",
                  ""]
        if blocked:
            lines += [f"**{blocked} of these are marked (blocked)**: you are not a registered",
                      "author on them, so the form will refuse. Claim ownership first (above).",
                      ""]
        # The two field values inline rather than a pointer to `tasks/arxiv_jref.md`. A row
        # saying only "-> ACL 2025" leaves the reader to work out what arXiv wants in a field it
        # calls `Journal-ref:`, and the answer is a citation string this code already builds from
        # the publisher's bibtex. The section they work from has to be the one that knows it.
        from identity_tasks import journal_doi, journal_ref  # noqa: E402
        subs = read_yaml(os.path.join(DATA, "arxiv_submissions.yaml")) or {}
        for p in missing_jr:
            flag = "  **(blocked)**" if p["arxiv"] in unowned else ""
            title = (p.get("title_display") or p["title"]).strip()
            lines.append(f"- [ ] **{p.get('citations') or 0} cites** — {title}{flag}")
            sub = subs.get(p["arxiv"])
            # Nested bullets rather than indented prose: a continuation line at this
            # indent is a lazy paragraph continuation, so the form link rendered glued to
            # the end of the title.
            lines.append(f"      - the form: <https://arxiv.org/submit/{sub}/jref>" if sub else
                         f"      - the form: find `{p['arxiv']}` on <https://arxiv.org/user> "
                         f"→ its *journal ref* link "
                         f"([abs](https://arxiv.org/abs/{p['arxiv']}))")
            if jr := journal_ref(p):
                lines.append(f"      - `Journal-ref:` `{jr}`")
            else:
                # Said rather than omitted: an absent line reads as "nothing to paste",
                # and the reader types the venue name, which is not a journal-ref.
                venue = p.get("venue_display") or p.get("venue") or "?"
                lines.append(f"      - `Journal-ref:` — not derivable from the bibliography "
                             f"(venue is *{venue}*); type the proceedings title yourself")
            doi = journal_doi(p)
            lines.append(f"      - `Journal version DOI:` `{doi}`" if doi else
                         "      - `Journal version DOI:` — none minted, leave blank")
        lines += ["", "`Report number:` stays blank on all of them: it means an "
                  "*institutional* preprint", "number (a lab's own report series) and none "
                  "of these has one.", ""]

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
                  "Full list, clickable: `tasks/hf_worklist.md`. Re-read the pages live",
                  "after a session of clicking: `python scripts/audit_identity.py "
                  "--no-names`.",
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
                lines.append(f"- [ ] `{(p.get('title_display') or p['title'])[:64]}`"
                             f"  vs  `{o[:64]}`")
        lines.append("")

    # Two different asks, and conflating them is what made this section unusable:
    # verifying a draft is minutes, writing one from a blank file is not. Drafts are
    # in data/sidecars/drafts/ and nothing reads them until you promote one.
    drafted = sorted(os.path.basename(f)[:-3] for f in
                     glob.glob(os.path.join(DATA, "sidecars", "drafts", "*.md")))
    # A draft written against rules that have since moved is not work for a person: it
    # cannot be accepted as it stands, so it does not belong in the verification section
    # above. It belongs with the undrafted papers below, because the remedy is identical
    # -- re-run the drafter -- and giving it a heading of its own would report the same
    # seventeen papers twice under two different counts.
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from sidecar_io import held, spec_sha
    from sidecar_review import write_review_page
    keep = held(spec_sha())
    stale_drafts = [s for s in drafted if s not in keep]
    drafted = [s for s in drafted if s in keep]
    no_side = [p for p in papers if not has_live_sidecar(p["slug"])]
    if drafted:
        # One page with every draft on it, already checked, regenerated by this run. The
        # review is the only item on this worklist that is reading rather than pasting,
        # and a command per paper is the wrong shape for reading: it should be a link.
        page = write_review_page(papers)
        lines += [f"## Sidecar drafts awaiting your verification ({len(drafted)})", "",
                  "Drafted from each paper's own full text: claims with their magnitudes,",
                  "scope conditions, terminology and likely misreadings. Every number is a",
                  "machine's reading and needs your eyes — but you are correcting a page,",
                  "not writing one.",
                  "",
                  "**Read " + (f"all {len(drafted)}" if len(drafted) > 1 else "it")
                  + " here — one page, no commands:**",
                  f"<file://{page}>",
                  "",
                  "This run generated it. Every figure a draft states is printed beside the",
                  "paper's own sentence containing that number, and anything the paper does",
                  "not say is flagged in red at the top of the page and again on the claim —",
                  "so the check is comparing two lines, never opening a PDF. The only thing",
                  "left is `--accept`, which is below and which publishes the page under your",
                  "name.", ""]
        for slug in sorted(drafted, key=lambda s: -((by_slug.get(s) or {})
                                                    .get("citations") or 0))[:10]:
            p = by_slug.get(slug) or {}
            # A draft for a paper that already has a live sidecar is a replacement, and
            # that changes what reviewing it means: you are comparing two readings, one
            # of which is already published, rather than checking a new page. `--accept`
            # refuses it without `--replace` for the same reason.
            mark = "  **replaces the live sidecar**" if has_live_sidecar(slug) else ""
            title = p.get("title_display") or p.get("title") or slug
            lines.append(f"- [ ] **{title[:60]}** — "
                         f"{p.get('citations') or 0} cites{mark}")
            lines.append(f"      - read: [in the review page](file://{page}#{slug}) · "
                         f"[raw draft](data/sidecars/drafts/{slug}.md)")
            lines.append(f"      - publish: `python scripts/draft_sidecars.py --accept "
                         f"{slug}{' --replace' if has_live_sidecar(slug) else ''}`")
        lines.append("")
    todraft = [p for p in no_side if p["slug"] not in set(drafted)]
    if todraft:
        # The stale count is stated here, not given a section, so that somebody who
        # opens data/sidecars/drafts/ and finds files in it is not left wondering why
        # they are missing from the list above.
        stale_note = ([f"{len(stale_drafts)} of these already have a draft file on disk,"
                       " written against sidecar rules",
                       "that have since changed. `--accept` refuses them and the next run"
                       " overwrites",
                       "them, so do not spend an evening reading one; they need the same"
                       " re-run as the rest.", ""] if stale_drafts else [])
        lines += [f"## Sidecars not yet drafted ({len(todraft)}/{len(papers)})", ""] \
                 + stale_note + \
                 ["**Not yours.** Drafting reads each paper's full text and writes claims,",
                  "scope and glosses into a draft file — agent work, and the queue drains",
                  "when you ask an agent for a batch or when a full run takes one. It is here",
                  "so the number is visible, not so you will do it. What comes back is the",
                  "section above, and that one is yours.",
                  "",
                  "```bash",
                  "python scripts/draft_sidecars.py --review      # every paper: live, draft,"
                  " or neither",
                  "python scripts/draft_sidecars.py --limit 20    # queue the next 20 (then"
                  " an agent fills them)",
                  "python scripts/draft_sidecars.py --ingest      # fold the answers in",
                  "```", "",
                  # "How do I find them" was a fair question: this section listed six
                  # titles and named no file, no slug and no way to see the other hundred.
                  # The slug is the handle every command above takes and the filename every
                  # sidecar has, so it is what the list has to carry.
                  "`--review` is the whole list; the six below are the top of it by",
                  "citations, which is where drafting pays. A draft lands in",
                  "`data/sidecars/drafts/<slug>.md` and nothing reads it until you",
                  "`--accept` it, which moves it to `data/sidecars/<slug>.md` — the",
                  "published one, and the only one the site builds from.", "",
                  "`update.py` also drafts a batch on every run, so this number falls on",
                  "its own.", ""]
        for p in sorted(todraft, key=lambda p: -(p.get("citations") or 0))[:6]:
            lines.append(f"- `{p['slug']}` — {p.get('citations') or 0} cites — "
                         f"{(p.get('title_display') or p['title'])[:56]}")
        lines.append("")

    # Papers whose text no fetcher can reach, upstream of the two sidecar sections above: a
    # sidecar is drafted from full text, so these can never be drafted and would otherwise sit
    # in "not yet drafted" looking like a queue. A paper the pipeline cannot read is a task,
    # and the whole task is putting a file somewhere.
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
                  # Said as a count, not as "all three": this list shrinks as the PDFs
                  # land and grows when a paywalled paper enters the corpus, and prose
                  # with a number frozen into it is how a generated file starts
                  # disagreeing with its own heading.
                  f"You are an author on {'it' if len(starved) == 1 else 'each of them'}, "
                  f"so you already have the PDF{'s' * (len(starved) != 1)}. Drop "
                  f"{'it' if len(starved) == 1 else 'each one'} in as",
                  "`data/fulltext/<slug>.pdf` — the directory is gitignored, so the PDF stays",
                  "on your machine and only the sidecar it produces is committed. That path is",
                  "read before any network source, so the next run picks it up and the paper",
                  "joins the drafting queue.", ""]
        for p in sorted(starved, key=lambda p: -(p.get("citations") or 0)):
            lines.append(f"- [ ] **{(p.get('title_display') or p.get('title') or '')[:60]}** "
                         f"— {p.get('citations') or 0} cites, "
                         f"{p.get('venue_display') or 'no venue'}")
            # Where the file is, not just where it goes. "You already have the PDF" is
            # true and still leaves a search: the page this project already knows the URL
            # of is the page the PDF is one click behind.
            src = p.get("url") or p.get("openreview") or p.get("doi_url") or (
                f"https://doi.org/{p['doi']}" if p.get("doi") else "")
            lines.append(f"      - get it from <{src}>" if src else
                         "      - no landing page known — wherever your own copy is")
            lines.append(f"      - save it as `data/fulltext/{p['slug']}.pdf`")
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

    lines = next_steps(tidy(drop_hollow(apply_declines(lines))))

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
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
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


if __name__ == "__main__":
    main()
