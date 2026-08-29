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
import textwrap

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from common import (DATA, DECLINE_STAMP, clipped, has_live_sidecar,  # noqa: E402
                    health_report, is_preprint_venue, load_config, norm_title,
                    read_yaml, synth_bibtex)
from sweep_github import ZENODO_KINDS  # noqa: E402

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
    if not sc.get("scholar_answered", True):
        # Without this the section is simply absent, which on a page of open items reads
        # as Scholar agreeing with the corpus. Every bucket below rests on a title being
        # absent from the profile listing, and none of them can be computed from a
        # listing that did not arrive.
        got = sc.get("scholar_rows") or 0
        why = (f"{got} row(s) arrived and then a page refused. Every bucket here rests on "
               "a title being absent from the listing, so a listing missing a page is no "
               "more usable than none."
               if got else
               "Scholar refuses most machines most of the time, and a refusal says nothing "
               "about the corpus.")
        # The last two lines are not wrapped. A command or a markdown link split across a
        # newline is a link the reader has to repair before they can use it.
        lead = (f"**Google Scholar did not answer this run, so the coverage section is "
                f"missing rather than empty.** {why}")
        return [f"> {ln}" for ln in textwrap.wrap(lead, 76)] + [
            "> Re-run `python update.py --step audit`. What the Semantic Scholar author",
            "> record could answer is in [tasks/identity_audit.md](tasks/identity_audit.md).",
            ""]
    gate, miss = sc.get("gate_dropped") or [], sc.get("not_in_corpus") or []
    miss = [r for r in miss if (r.get("kind") or "paper") == "paper"]
    dup = sc.get("scholar_duplicates") or []
    # A title variant is only work when nobody has already decided it. arXiv holds the current
    # title and the run has fetched it, so `stale` says which side is behind: `bib` is one edit
    # upstream, `open` is a judgement, and `scholar` is neither -- editing that row changes
    # what Scholar displays, not which citations cluster under it.
    #
    # Named rather than excluded. The heading below states that arXiv has no record for these,
    # so a label meaning "arXiv was never asked" must not fall in by not being on the deny list.
    var = sc.get("title_variants") or []
    fix = [v for v in var if v.get("stale") == "bib"]
    call = [v for v in var if v.get("stale") == "open"]
    blind = [v for v in var if v.get("stale") == "unknown"]
    # The mirror image of `not_in_corpus`, and the half that was computed but never
    # printed: papers this pipeline has and the profile does not. It belongs on the page
    # for the same reason as its opposite -- Scholar is the surface most people actually
    # read, and a paper absent from it is absent from where the citations accrue.
    gone = sc.get("not_on_scholar") or []
    if not (gate or miss or fix or call or dup or gone or blind):
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
         # Backticks, never a markdown link. `build/` is gitignored, so a link there is
         # dead for every reader of this page on GitHub and after a clone. What makes it
         # openable is the command that writes it, which is why that is named instead.
         "Every bucket in full, including what is truncated below, is in",
         "`build/scholar_diff.json` on the machine that last ran the audit. `build/` is",
         "gitignored, so `python update.py --step audit` is the one command between a",
         "fresh clone and the file.", ""]
    if gate:
        L += [f"### {pl(len(gate))} the authorship gate excluded  — a bug, or a "
              f"wrong Scholar row", "",
              "Scholar says these are yours and `build/not_mine.json`, written by the",
              "same run and gitignored like the rest of `build/`, says they are not.",
              "One of the two is wrong. If the paper is yours, add its title under",
              "`also_mine` in [`data/overrides.yaml`](data/overrides.yaml); if Scholar has",
              "merged a namesake's paper into your profile, delete it there, because a",
              "wrong row misleads every human who reads it too.", ""]
        L += [f"- [ ] {cites(r.get('citations'))} — {clipped(r.get('title') or '', 66)}"
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
              f"{clipped(r.get('title') or '', 60)}" for r in miss[:12]]
        if len(miss) > 12:
            L += [f"- … and {len(miss) - 12} more in `build/scholar_diff.json`"]
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
                  f"{clipped(p.get('title_display') or p.get('title') or '', 58)}{ref}"]
        L += [""]
    if fix:
        L += [f"### {pl(len(fix))} whose bibliography title is behind arXiv", "",
              "arXiv states the title Scholar shows, so the source entry is the stale",
              "one and there is nothing to decide: correct the title in the source",
              "bibliography and re-run. Until then the two surfaces answer a title query",
              "differently, which is the exact failure this repo exists to prevent.", ""]
        L += [f"- [ ] `{v.get('slug')}`\n"
              f"      - arXiv and Scholar: {clipped(v.get('scholar') or '', 56)}\n"
              f"      - the .bib entry:    {clipped(v.get('corpus') or '', 56)}"
              for v in fix] + [""]
    if blind:
        L += [f"{pl(len(blind))} under two titles are not split between the two headings "
              "here, because `build/title_diffs.json` is not there and arXiv's own titles "
              "are the only thing that separates them. Run `python update.py --step "
              "collect` and this run again.", ""]
    if call:
        L += [f"### {pl(len(call))} under two titles, with no arXiv record to break the "
              f"tie", "",
              "Same paper, two names, and arXiv confirms neither — so this one is a",
              "judgement. Decide which is canonical and set it in",
              "[`data/overrides.yaml`](data/overrides.yaml).", ""]
        L += [f"- [ ] `{v.get('slug')}`\n"
              f"      - scholar: {clipped(v.get('scholar') or '', 64)}\n"
              f"      - corpus:  {clipped(v.get('corpus') or '', 64)}" for v in call] + [""]
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


def scholar_split_records(st: dict) -> list[str]:
    """The worklist section for `build/scholar_strays.json`, or nothing.

    Only the two passes whose remedy is one merge each. The `not in the bibliography`
    pass lands in `tasks/scholar_strays.md` and not here -- it is a list to read, not a
    list of edits, and most of its rows are other people.
    """
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
         "OpenAlex holding one title twice is the same fault from the other side. A parser",
         "that split the record there usually split it at Scholar too, and the count on",
         "the smaller copy is what a merge recovers.", "",
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
        L += [f"- [ ] **{gap} citations** — {clipped(r.get('title') or '', 64)}",
              f"      - {why}",
              f"      - [search Scholar for it]({r['search']})"]
    if len(rows) > 15:
        L.append(f"- … and {len(rows) - 15} more in "
                 "[`tasks/scholar_strays.md`](tasks/scholar_strays.md), same order")
    return L + [""]


def wikidata_coauthors(st: dict) -> list[str]:
    """The worklist section for `build/wikidata_coauthors.json`, or nothing.

    Only the strings a name is all there is to go on. The rest -- an ORCID or a DBLP page
    matched, a venue resolved, a language read off the bibliography -- is written by
    `scripts/wikidata_coauthors.py --apply` and reported here without a checkbox.
    """
    left = (st.get("review") or 0) + (st.get("leftover") or 0)
    batch = (st.get("edits") or 0) + (st.get("venues") or 0) + (st.get("fills") or 0)
    # No section when only the batchable half is outstanding: this page asks the author for
    # things, and a statement `--apply` writes is not one of them.
    if not left:
        return []
    L = [f"## Wikidata author strings ({left} by hand)", "",
         "Every paper item lists you as *author* and each co-author as *author name",
         "string*, which is a literal nothing can join on — so each item hangs off your",
         "item alone. Resolving a string to that person's own item is what connects them,",
         "and many independent paths into your item is the point of having them at all.", ""]
    L += [f"- [ ] **{left} strings across {st.get('papers_left', 0)} papers** — one "
          "Author Disambiguator pass per paper, most-cited first",
          "      - the links, and the candidate items found for each name: "
          "[`tasks/wikidata_coauthors.md`](tasks/wikidata_coauthors.md)"]
    if st.get("dropped"):
        L += [f"      - {st['dropped']} name matches are left out as namesakes, on a "
              "stated occupation nothing like research"]
    if batch:
        L += ["",
              f"{batch} more statement{'s' * (batch != 1)} need no decision from you — an "
              "ORCID or a DBLP",
              "page matched the name, or the value came straight from the bibliography.",
              "`python scripts/wikidata_coauthors.py --apply` writes them."]
    return L + [""]


def wikidata_people(st: dict) -> list[str]:
    """The worklist section for `build/wikidata_people.json`, or nothing.

    Only the people no public record decides. Creating the rest, and adding the ORCID to the
    item a shared paper or employer identifies, is `scripts/wikidata_people.py --apply`.
    """
    held = sorted(st.get("held_people") or [],
                  key=lambda x: (-x.get("papers", 0), x["label"]))
    if not held:
        return []
    L = [f"## Co-authors who may already have a Wikidata item ({len(held)})", "",
         "Wikidata carries a human item under each of these names and none of them states an",
         "ORCID, so each is either this co-author reached from a paper rather than a profile",
         "or somebody else of the same name. Under each name is what every candidate item",
         "says about itself, the ones stating a research occupation first. The answer is",
         "which line is them, or `new` if none is.",
         "",
         "Each name also carries what its ORCID record states. That identifier came from",
         "OpenAlex reading a paper whose own metadata names no author identifiers, so on a",
         "common name it can be a namesake's — a record listing papers in another field",
         "entirely is one, and the answer for it is `no`, which drops the ORCID for good.",
         "",
         "Paste into [`data/overrides.yaml`](data/overrides.yaml) under `wikidata_people`,",
         "correcting the QIDs that are wrong:",
         "",
         "```yaml",
         "wikidata_people:"]
    for p in held:
        rest = [n["qid"] for n in p["namesakes"][1:4]]
        # The alternatives inline, because the first candidate is the likeliest and not the
        # answer -- a block pasted unread would put an ORCID on a racing cyclist.
        L.append(f"  {p['orcid']}: {p['namesakes'][0]['qid']}   # {p['label']}"
                 + (" — or " + ", ".join(rest) if rest else "")
                 + (", …" if len(p["namesakes"]) > 4 else "")
                 + ", or new, or no")
    L += ["```", ""]
    for p in held:
        papers = p.get("papers", 0)
        L.append(f"- [ ] **{p['label']}** ({papers} paper{'' if papers == 1 else 's'} with "
                 f"you) — [their ORCID record](https://orcid.org/{p['orcid']}) states "
                 f"{p.get('record_says') or 'nothing public beyond the name'}")
        for n in p["namesakes"]:
            L.append(f"  - [{n['qid']}](https://www.wikidata.org/wiki/{n['qid']}) — "
                     f"{n.get('says') or 'states nothing beyond the name'}")
    L += ["",
          "Nothing else follows by hand. The next run adds the ORCID to the item named, or",
          "creates a separate one, and writes the *author* statements from it."]
    if st.get("decided"):
        L += ["",
              f"{st['decided']} more needed no answer -- a paper or an employer both records",
              "name says which item they are, and "
              "[`tasks/wikidata_people.md`](tasks/wikidata_people.md)",
              "lists which and why."]
    return L + [""]


def wikidata_orgs(st: dict) -> list[str]:
    """The worklist section for `build/wikidata_orgs.json`, or nothing.

    Only the two things a public page cannot settle -- a name matching several items, and a
    fact only the author knows. Creating the items and writing the edges into them is
    `scripts/wikidata_orgs.py --apply`, reported here without a checkbox.
    """
    asks = (st.get("ambiguous") or []), (st.get("needs") or 0)
    if not any(asks):
        return []
    L = ["## Wikidata items for the groups", "",
         "Some of the work in the corpus is run by groups Wikidata has no item for, so a",
         "paper cannot say what it is part of and a group cannot say what it produced.",
         "Every statement written cites the public page it came from.", ""]
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
    todo = (len(st.get("create") or []), st.get("edges") or 0)
    if any(todo):
        names = [st["state"][s].get("label") or s for s in st.get("create") or []]
        L += ["",
              ("%s and %d edge%s into them wait on nothing"
               % (", ".join(names) or "No item", todo[1], "s" * (todo[1] != 1))
               if todo[0] else
               "%d edge%s into those items wait on nothing"
               % (todo[1], "s" * (todo[1] != 1))) + " —",
              "`python scripts/wikidata_orgs.py --apply` creates and writes them."]
    return L + [""]


def upstream_gaps(papers: list[dict], cfg) -> list[str]:
    """Papers the corpus has only because an override put them there, and the field
    corrections it carries privately.

    `extra_arxiv` and `extra_openreview` cover the interval before the entry lands in the
    bibliography, and both files say to delete the line after. Nothing else reports them,
    since the Scholar block finds missing papers by diffing Scholar against the corpus and an
    override closes exactly that gap.

    `_override` is provenance. `collect.py` sets it on records it adds from an override and it
    disappears once the bibliography's own entry merges, so a paper still carrying it is still
    absent upstream. The second and third blocks read `overrides.yaml` too, for lines left
    behind after a paste lands and for `fields:` corrections upstream has not absorbed.
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
        L += [f"- [ ] **{clipped(p.get('title_display') or p.get('title') or '', 66)}** — "
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
            # Whole, not clipped: this is the line to find and delete, so a fragment of it
            # is not something the reader can search for.
            L.append(f"- [ ] `{k}:` delete `{v}`")
        L.append("")

    # A `fields:` correction the bibliography could carry itself. Matched on the value
    # anywhere in the entry rather than on a field name, because a venue lives in
    # `booktitle` in one entry and `institution` in the next -- the ICML position paper's
    # venue is already upstream under `institution`, and only its DOI and URL are missing.
    BIBFIELD = {"doi": "doi", "url": "url", "year": "year", "venue": "booktitle"}
    by_slug = {p.get("slug"): p for p in papers}
    priv = []                     # one row per paper -- one visit to one entry
    for slug, fix in (ov.get("fields") or {}).items():
        rec = by_slug.get(slug) or {}
        bib = (rec.get("bibtex") or "").lower()
        want = [(f, str(v)) for f, v in (fix or {}).items() if v and str(v).lower() not in bib]
        if want:
            priv.append((rec, slug, want))
    if priv:
        n = sum(len(w) for _r, _s, w in priv)
        # Both numbers, because they differ and the reader can see only one of them: two
        # corrections in one entry is one visit, and a header saying 2 above a single
        # checkbox reads as a miscount.
        L += [f"## {n} field correction{'s' * (n != 1)} the bibliography does not carry "
              f"({len(priv)} entr{'y' if len(priv) == 1 else 'ies'})", "",
              "`fields:` in [`data/overrides.yaml`](data/overrides.yaml) corrects these for",
              "the corpus and nothing else. Scholar, Semantic Scholar and OpenAlex read the",
              "paper's own record, so a correction that stays here is one they never get.",
              "Add them to the entry upstream, then delete the override lines.", ""]
        if edit.startswith("https://github.com/"):
            L += [f"Edit the bibliography here: <{edit}>", ""]
        for rec, slug, want in priv:
            title = clipped(rec.get("title_display") or rec.get("title") or slug, 60)
            key = rec.get("key") or ""
            L += [f"- [ ] **{title}**" + (f" — entry `{key}`" if key else ""), "",
                  "  ```bibtex"]
            L += [f"  {BIBFIELD[f]:<12} = {{{v}}}," if f in BIBFIELD
                  else f"  % {f} = {v}   <- field name depends on the entry type"
                  for f, v in want]
            L += ["  ```", ""]
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
                 f"{clipped(p.get('title') or p['slug'], 66)}" for p in rows[:8]]
                + ([f"- … and {len(rows) - 8} more in "
                    "[`tasks/orcid_missing.md`](tasks/orcid_missing.md)"]
                   if len(rows) > 8 else []))
    out = []
    for p in rows:
        out += [f"- [ ] **{clipped(p.get('title') or p['slug'], 66)}** — "
                f"{p.get('citations') or 0} cites — what the file will add:", "",
                "  ```bibtex",
                *(f"  {ln}" for ln in (p.get("bibtex") or synth_bibtex(p)).strip().splitlines()),
                "  ```", ""]
    return out


def wikipedia_checks(wiki: dict) -> list[str]:
    """Articles that name the author or a coined term, each with the sentence saying so.

    Read from `build/wikipedia_state.json` because the ~100 API calls behind it belong to
    the audit step. One row per article rather than per term: the row is a page to read,
    and the quoted line under it is what makes reading optional.
    """

    def arts(v):
        """`(title, says)` pairs, tolerating a state file written before `says` existed."""
        return [(a, "") if isinstance(a, str) else (a.get("title") or "", a.get("says") or "")
                for a in v or []]

    rows = [(t, t, s) for t, s in arts(wiki.get("already_mentions"))]
    rows += [(c["term"], a, s) for c in wiki.get("checks") or []
             for a, s in arts(c.get("articles"))]
    if not rows:
        return []
    L = [f"## Wikipedia mentions {len({t for t, _a, _s in rows})} of your coinages across "
         f"{len({a for _t, a, _s in rows})} article(s) — check the facts", "",
         "Wikipedia carries roughly half the citations in AI answers, and WP:COI",
         "means you may not edit these. What you *can* do is the thing only an",
         "author can: notice that a description is wrong. The quoted line is what the",
         "article says — if it reads correctly, tick it and move on, which is the",
         "expected outcome.",
         "",
         "A correction goes on the talk page, with the corrected value and the page",
         "or table it comes from. Never in the article, and never a citation of your",
         "own work — that is the edit that gets reverted on sight.", ""]
    for term, art, says in rows:
        q = art.replace(" ", "_")
        # An article naming the author is its own subject, so naming it twice reads as noise.
        what = "" if term == art else f"**{term}** in "
        L.append(f"- [ ] {what}[{art}](https://en.wikipedia.org/wiki/{q}) "
                 f"([talk](https://en.wikipedia.org/wiki/Talk:{q}))")
        if says:
            L.append(f"  > {says}")
    return L + ["",
                f"The {wiki.get('absent', 0)} coinages Wikipedia does not mention are "
                f"listed in",
                "[`tasks/wikipedia.md`](tasks/wikipedia.md) as deliberately not "
                "actionable, along with",
                "the field articles you could improve with other people's sources.", ""]


def sidecar_drafts(papers: list[dict]) -> list[str]:
    """Drafts waiting to be read, and papers with no draft yet.

    Two different asks, and conflating them is what made this section unusable: verifying a
    draft is minutes, writing one from a blank file is not. Regenerates the review page as a
    side effect, so the link it prints is this run's.
    """
    by_slug = {p["slug"]: p for p in papers}
    L = []
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
        L += [f"## Sidecar drafts awaiting your verification ({len(drafted)})", "",
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
            L.append(f"- [ ] **{clipped(title, 60)}** — "
                         f"{p.get('citations') or 0} cites{mark}")
            L.append(f"      - read: [in the review page](file://{page}#{slug}) · "
                         f"[raw draft](data/sidecars/drafts/{slug}.md)")
            L.append(f"      - publish: `python scripts/draft_sidecars.py --accept "
                         f"{slug}{' --replace' if has_live_sidecar(slug) else ''}`")
        L.append("")
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
        L += [f"## Sidecars not yet drafted ({len(todraft)}/{len(papers)})", ""] \
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
            L.append(f"- `{p['slug']}` — {p.get('citations') or 0} cites — "
                         f"{clipped(p.get('title_display') or p['title'], 56)}")
        L.append("")
    return L


def starving_papers(papers: list[dict]) -> list[str]:
    """Papers no fetcher can reach the text of, so no sidecar can ever be drafted for them.

    Upstream of `sidecar_drafts`: without this they sit in "not yet drafted" looking like a
    queue. The whole task is putting a PDF in `data/fulltext/`.
    """
    L = []
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
        L += [f"## Papers whose full text nothing can fetch ({len(starved)})", "",
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
            title = clipped(p.get("title_display") or p.get("title") or "", 60)
            L.append(f"- [ ] **{title}** "
                         f"— {p.get('citations') or 0} cites, "
                         f"{p.get('venue_display') or 'no venue'}")
            # Where the file is, not just where it goes. "You already have the PDF" is
            # true and still leaves a search: the page this project already knows the URL
            # of is the page the PDF is one click behind.
            src = p.get("url") or p.get("openreview") or p.get("doi_url") or (
                f"https://doi.org/{p['doi']}" if p.get("doi") else "")
            L.append(f"      - get it from <{src}>" if src else
                         "      - no landing page known — wherever your own copy is")
            L.append(f"      - save it as `data/fulltext/{p['slug']}.pdf`")
        L.append("")
    return L


def arxiv_name_typos(papers: list[dict], state: dict) -> list[str]:
    """Papers whose arXiv author list misspells the name, first because everything else reads it.

    Hugging Face, Semantic Scholar, OpenAlex and Scholar all build author identity from arXiv,
    so a wrong character there creates a second author downstream that cannot be merged.
    """
    by_slug = {p["slug"]: p for p in papers}
    L = []
    typos = state.get("arxiv_name_typos") or []
    if typos:
        L += [f"## arXiv spells your name wrong on {len(typos)} papers  — "
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
            L.append(f"- [ ] [`{t['arxiv']}`](https://arxiv.org/abs/{t['arxiv']}) — "
                         f"reads **{t.get('reads')}** — {clipped(p.get('title') or '', 52)}")
        L += ["", "Full detail: `tasks/arxiv_name_fixes.md`.", ""]
    return L


def arxiv_ownership(state: dict, ident: dict, unowned: set) -> list[str]:
    """arXiv papers the author is not registered as owner of.

    Upstream of the journal-ref section, which the form refuses on a paper you do not own.
    """
    L = []
    if state.get("arxiv_registered") is not None and unowned:
        L += [f"## arXiv: claim ownership of {len(unowned)} papers  — before the journal-refs",
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
    return L


def arxiv_journal_refs(papers: list[dict], scholar: dict, unowned: set) -> list[str]:
    """Published papers whose arXiv record still declares no venue, both field values inline.

    A metadata edit rather than a new version, about a minute each, and there is no write API
    -- so the clicking is the reader's and the typing is not.
    """
    L = []
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

    missing_jr = by_citations(papers, needs_jr, 12)
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
        L += [f"## arXiv journal-ref missing ({sum(1 for p in papers if needs_jr(p))} papers)",
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
            L += [f"**{blocked} of these are marked (blocked)**: you are not a registered",
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
            L.append(f"- [ ] **{p.get('citations') or 0} cites** — {title}{flag}")
            sub = subs.get(p["arxiv"])
            # Nested bullets rather than indented prose: a continuation line at this
            # indent is a lazy paragraph continuation, so the form link rendered glued to
            # the end of the title.
            L.append(f"      - the form: <https://arxiv.org/submit/{sub}/jref>" if sub else
                         f"      - the form: find `{p['arxiv']}` on <https://arxiv.org/user> "
                         f"→ its *journal ref* link "
                         f"([abs](https://arxiv.org/abs/{p['arxiv']}))")
            if jr := journal_ref(p):
                L.append(f"      - `Journal-ref:` `{jr}`")
            else:
                # Said rather than omitted: an absent line reads as "nothing to paste",
                # and the reader types the venue name, which is not a journal-ref.
                venue = p.get("venue_display") or p.get("venue") or "?"
                L.append(f"      - `Journal-ref:` — not derivable from the bibliography "
                             f"(venue is *{venue}*); type the proceedings title yourself")
            doi = journal_doi(p)
            L.append(f"      - `Journal version DOI:` `{doi}`" if doi else
                         "      - `Journal version DOI:` — none minted, leave blank")
        L += ["", "`Report number:` stays blank on all of them: it means an "
                  "*institutional* preprint", "number (a lab's own report series) and none "
                  "of these has one.", ""]
    return L


def hf_pages(papers: list[dict], state: dict) -> list[str]:
    """The two Hugging Face buckets: no paper page at all, and a page nobody has claimed.

    Ten most-cited each, with the bucket's full size in the heading. `tasks/hf_worklist.md`
    carries the rest.
    """
    # Prefer the audit's live sets over the collector's cached flags where present:
    # this list is worked by hand over days, and a stale copy sends you back to
    # pages you already did -- which is what happened the first time round.
    live = state.get("hf_missing") is not None
    buckets = [
        (set(state.get("hf_missing") or []),
         lambda p: p.get("arxiv") and p.get("hf_indexed") is False,
         "Hugging Face paper page missing",
         ["Log in to Hugging Face first: an unauthenticated visit creates nothing",
          "(verified, 0 of 50). Visiting the URL while logged in *is* the action --",
          "there is no form.",
          "",
          "Full list, clickable: `tasks/hf_worklist.md`. Re-read the pages live",
          "after a session of clicking: `python scripts/audit_identity.py --no-names`."]),
        (set(state.get("hf_unclaimed") or []),
         lambda p: p.get("hf_indexed") and not p.get("hf_claimed_by_me"),
         "Hugging Face page indexed but not claimed by you",
         ["Claims go through moderation and Hugging Face only publishes the",
          "author→user link once it is granted, so a request already submitted is",
          "invisible from outside and would otherwise be listed here again. If you",
          "have already asked for one of these, add its arXiv id to",
          "`hf_claim_requested` in `data/overrides.yaml` and it moves to *pending*",
          "in `tasks/hf_worklist.md` instead of back onto this list.",
          "",
          "Full list and the other buckets: `tasks/hf_worklist.md`."]),
    ]
    L = []
    for ids, cached, head, why in buckets:
        shown = by_citations(papers, (lambda p, i=ids: p["arxiv"] in i) if live else cached, 10)
        if not shown:
            continue
        n = len(ids) if live else sum(1 for p in papers if cached(p))
        L += [f"## {head} ({n})", ""] + why + [""]
        L += [f"- [ ] <https://hf.co/papers/{p['arxiv']}>  ({p.get('citations') or 0} cites)"
              for p in shown] + [""]
    return L


def repo_gaps(repos: list[dict]) -> list[str]:
    """Repos with no citation route, and repos whose labels nobody has signed off.

    Last on the page: a Zenodo DOI is the cheapest item here and the least likely to
    change what an engine returns.
    """
    L = []
    zcand = [r for r in repos if not r.get("skip") and not r.get("paper_slug")
             and r.get("kind") in ZENODO_KINDS and not r.get("zenodo_doi")]
    if zcand:
        L += [f"## Artifacts with no citation route ({len(zcand)})", "",
              "Tools and guides with no linked paper. A Zenodo release DOI gives each a",
              "citable, archived identity and a DataCite record that reaches OpenAlex",
              "and your ORCID works list — so they stop being GitHub-only objects.",
              "Steps, and the honest case for skipping some: `tasks/zenodo.md`.", ""]

    pend = [r for r in repos if not r.get("reviewed") and not r.get("skip")]
    if pend:
        L += [f"## Repo labels awaiting your review ({len(pend)}/{len(repos)})", "",
              "Check `data/repos.yaml`, fix anything wrong, set `reviewed: true` to freeze "
              "it, then `python scripts/sweep_github.py diff`.", ""]
    return L


def by_citations(papers: list[dict], pred, n: int = 8) -> list[dict]:
    """The `n` papers matching `pred`, most-cited first."""
    return sorted([p for p in papers if pred(p)],
                  key=lambda p: -(p.get("citations") or 0))[:n]


def same_or_different(papers: list[dict]) -> list[str]:
    """Title pairs close enough that one of them may be the other, for one decision each.

    Both titles whole rather than clipped to a row width: the decision is whether they name
    one paper, and a clip can fall exactly where they differ.
    """
    review = [p for p in papers if p.get("similar_but_distinct")]
    if not review:
        return []
    L = ["## Same paper or different? (decide once in data/overrides.yaml)", ""]
    for p in review:
        for o in p["similar_but_distinct"]:
            L.append(f"- [ ] `{p.get('title_display') or p['title']}`  vs  `{o}`")
    return L + [""]


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
        out = [f"- [ ] **{clipped(title, 66)}** — put-code `{b['put']}`"]
        doi = b.get("carried_doi")
        if doi:
            # Linked, because the link is the evidence: following the identifier that is
            # on your own record lands on a paper that is not this one.
            out.append(f"      - remove `{doi}` — it resolves to "
                       f"[{clipped(b.get('carried_title') or 'another paper', 44)}]"
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
            return [f"- [ ] **{clipped(r['title'], 60)}** — open put-code `{r['keep']}` "
                    f"(*{clipped(r['keep_title'], 38)}*) and add the DOI `{r['doi']}`, which is "
                    f"the one on put-code `{r['folds']}` (*{clipped(r['folds_title'], 38)}*)", ""]
        # No arXiv-DOI entry, or more than two: naming every entry is the honest form,
        # because which one has the venue is a judgement and this is not making it.
        return [f"- [ ] **{clipped(r['title'], 60)}** — {len(r['entries'])} entries: "
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
            f"{clipped(p.get('title_display') or p['title'], 56)} — "
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
         f"{'has' if state.get('wikidata_papers_creatable') == 1 else 'have'} no item",
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
         # Phrased without a subject verb so one paper and forty read the same, since the
         # count reaches 1 as the backlog drains and every agreement here would then be wrong.
         + ([f"{wd_nokey} more with no item, and not in the command below: no DOI and no",
             "arXiv id, so there is no key to check Wikidata against and creating an item",
             "risks a duplicate nobody can find. Each arrives here once it is deposited",
             "anywhere.", ""]
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
