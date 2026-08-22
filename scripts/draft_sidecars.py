#!/usr/bin/env python3
"""Draft a sidecar per paper from the paper itself, for a human to verify.

A sidecar is the one per-paper input nothing else in this repo can derive: the claims
in quotable form, the scope conditions each holds under, the terms of art used in a
non-obvious sense, and the misreadings worth pre-empting. It is also what decides
whether an engine describes the work *correctly* rather than merely finds it.

The earlier framing of this file was that only the author could supply that, so 116 of
117 papers had none and the worklist asked for ten minutes each -- nineteen hours of
work that would never be done. That framing was wrong in a specific way: a claim with
its magnitude, a scope condition, and a definition of a coined term are all *in the
paper*. What the author uniquely holds is the judgement about whether a draft got them
right, and which misreading is the one that actually keeps happening.

So this drafts, and the human verifies. That is a different task and a much smaller
one: reading a page of extracted claims and correcting them is minutes, and it starts
from the paper's own numbers rather than from a blank file.

Drafts land in `data/sidecars/drafts/<slug>.md`, never in `data/sidecars/`. Nothing
reads the drafts directory -- the site, the validator, the fidelity check and the
coverage count all glob `data/sidecars/*.md` one level up. An unverified draft
therefore cannot reach a published page by accident, which is the property that makes
drafting safe to do in bulk. Promotion is explicit:

    python scripts/draft_sidecars.py                    # queue drafts for the 20 most cited
    python scripts/draft_sidecars.py --ingest            # fold agent answers into drafts/
    python scripts/draft_sidecars.py --review            # what is drafted, what is live
    python scripts/draft_sidecars.py --accept <slug>     # promote one, after you edited it
    python scripts/draft_sidecars.py --accept-all        # promote every draft

Three modes, and `--mode` overrides the configured one for a single run:

  llm.mode: skill  (default)  writes build/sidecar_tasks.json for an agent session to
                              fill in. No API key. This is the paper-geo skill's path.
  llm.mode: api               one Anthropic Messages call per paper, schema-enforced.
  llm.mode: openai            one chat completion per paper against any OpenAI-compatible
                              endpoint -- a local server, a gateway, an open-weight
                              model. Endpoint and model come from the environment and
                              never from config.yaml, which is committed and public.

The nine drafting steps are sections of one prompt, not nine turns: every mode above
sends the same system prompt and the same schema and reads back one object. Nothing
here needs tool use or a multi-turn agent, which is why `api` and `openai` exist.

`--repair N` is available in both `api` and `openai` mode, and it is the difference
between a draft and an acceptable one: the loop hands the model back what the checks
found, with the paper, up to N times, stopping as soon as a round stops reducing the
count. Measured on one paper: 20 findings, then 5, then 2. `skill` mode has no
equivalent, because the second pass there is the agent session reading `--review`.
"""
from __future__ import annotations

import argparse
import collections
import glob
import hashlib
import inspect
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import yaml  # noqa: E402

from llm import decodable, first_json, with_retries  # noqa: E402
from llm import client as llm_client  # noqa: E402
from common import (BUILD, DATA, QA_ROLES, ROOT, answered_by, get,  # noqa: E402
                    has_live_sidecar, load_config, phrasings, qa_loci, read_yaml,
                    rules_block)
from fulltext import LIMIT as FULLTEXT_LIMIT  # noqa: E402
from fulltext import cut_chars  # noqa: E402
from fulltext import resolve as resolve_fulltext  # noqa: E402

SIDECARS = os.path.join(DATA, "sidecars")
DRAFTS = os.path.join(SIDECARS, "drafts")
CACHE = os.path.join(BUILD, "fulltext")
TASKS = os.path.join(BUILD, "sidecar_tasks.json")

RULES_DOC = "docs/SIDECAR.md"

FRAMING = """You extract, from a paper, the small set of statements that decide whether \
an answer engine describes it correctly. You are drafting for the paper's own author, \
who will verify and correct every line.

The rules below are the repo's own spec for this artifact, read verbatim from \
{doc} §2. Follow them in the order given.

"""

USER = """Draft the sidecar for this paper.

{evidence}

Return JSON matching the schema."""


def system_prompt() -> str:
    """The framing plus the rules, which live in the doc rather than here.

    This file used to carry its own prose copy of the rules while docs/SIDECAR.md
    carried a second and the schema descriptions a third; the three had already
    drifted. Now there is one copy, and `common.rules_block` raises if it is gone.
    """
    return FRAMING.format(doc=RULES_DOC) + rules_block(RULES_DOC)


def spec_sha() -> str:
    """Short hash of everything that decides whether a draft is acceptable.

    Not the rules doc alone. The rule that rejected all 17 drafts this repo had
    accumulated -- every sidecar needs at least one `kind: context` claim -- lives in
    `validate.check_sidecar_shape`, in code, with the prose untouched. A stamp over the
    prose would have moved on a typo fix and held still through the one change that
    mattered. So: the rules the model is sent, the schema it fills, and the source of
    every function that judges the result -- `readability` included, because a draft
    written before the sentence caps existed is exactly a draft `--accept` now refuses.
    """
    from validate import (check_claim_evidence, check_claim_numbers, check_sidecar_shape,
                          readability)
    parts = (rules_block(RULES_DOC),
             json.dumps(schema(), sort_keys=True),
             inspect.getsource(check_sidecar_shape),
             inspect.getsource(check_claim_numbers),
             inspect.getsource(check_claim_evidence),
             inspect.getsource(readability))
    return hashlib.sha256("\n".join(parts).encode()).hexdigest()[:12]


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:12]


STAMP = re.compile(r"^Stamp: spec=(\S+) checks=(\S+) body=(\S+)$", re.M)


def stamp_of(path: str) -> tuple[str, str, str] | None:
    """(spec, checks, body) as recorded when this draft was written, or None if unstamped."""
    m = STAMP.search(open(path).read())
    return (m.group(1), m.group(2), m.group(3)) if m else None


def body_of(path: str) -> str:
    """The draft's front matter verbatim -- everything a person would edit."""
    m = re.search(r"^---\n(.*?)^---\n", open(path).read(), re.S | re.M)
    return m.group(1) if m else ""


def uncommitted(path: str) -> bool:
    """Does this file differ from the last commit? True if git cannot say.

    The fallback for drafts written before stamping existed, and a good signal in its
    own right: an uncommitted change to a draft means somebody is in the middle of
    editing it right now.
    """
    try:
        return subprocess.call(["git", "diff", "--quiet", "HEAD", "--", path],
                               cwd=ROOT, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL) != 0
    except OSError:
        return True


def edited(path: str) -> bool:
    """Has a person changed this draft since the drafter wrote it?

    The question that decides whether a re-draft may overwrite it, and the reason the
    stamp carries a body hash at all. Their edits are the review this whole step exists
    to collect; a queue that silently replaced them would destroy the only thing here
    that cannot be re-derived.

    An unstamped draft has to be answered from outside the file, and git answers it: a
    committed draft nobody has touched since is the drafter's own output, and replacing
    it costs a `git checkout` to undo. Treating unstamped as edited instead would have
    been the safe-looking choice and the wrong one -- it would freeze exactly the 17
    drafts this check exists to unfreeze.
    """
    st = stamp_of(path)
    if st is None:
        return uncommitted(path)
    return st[2] != sha(body_of(path))


def stale(path: str, spec: str) -> str | None:
    """Why this draft is out of date, or None if it still matches its own spec.

    Two ways, and they are worth telling apart when reporting to a person. "spec moved"
    means the rules changed under a draft that was fine when written -- not the model's
    fault and nothing for the author to read. "now failing" means the spec is the same
    one and the checks stopped passing, which is a bug in this repo, because the only
    other thing that could have changed is the paper's cached text.
    """
    st = stamp_of(path)
    if st is None:
        return "written before drafts recorded their spec"
    if st[0] != spec:
        return "spec moved"
    if st[1] == "pass" and any(validate_draft(path, note=False)):
        return "now failing"
    return None


# --------------------------------------------------------------- evidence

def fulltext(p: dict, cfg: dict, limit: int = FULLTEXT_LIMIT) -> tuple[str, str]:
    """The paper's text and where it came from. See scripts/fulltext.py for the chain.

    The abstract alone produces claims with no magnitudes and no scope -- the two fields
    that carry the whole value. So this is worth a fetch per paper, and worth trying
    more than one source: this used to read arXiv's HTML rendering only, which meant the
    12 papers that were never on arXiv got a draft written from their titles.
    """
    return resolve_fulltext(p, cfg, limit=limit)


def readme(p: dict, limit: int = 6000) -> str:
    """The code repo's README, when there is one. Cached alongside the full text.

    Worth the fetch for one field in particular: a method's *name* and how the authors
    themselves gloss it usually reads better in the README than in the paper, and
    `terminology` is exactly the field that wants the authors' own gloss.
    """
    repo = (p.get("links") or {}).get("code") or p.get("hf_github_repo")
    if not repo or "github.com" not in repo:
        return ""
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f"{p['slug']}.readme.txt")
    if os.path.exists(path):
        with open(path) as f:
            return f.read()[:limit]
    owner_repo = repo.rstrip("/").split("github.com/")[-1].removesuffix(".git")
    text = ""
    for branch in ("main", "master"):
        for name in ("README.md", "readme.md"):
            # retries=2: a repo whose default branch is `master` 404s twice on the way
            # here, and the shared backoff would spend two minutes discovering that.
            raw = get(f"https://raw.githubusercontent.com/{owner_repo}/"
                      f"{branch}/{name}", timeout=30, retries=2)
            if raw:
                text = raw.decode("utf-8", "replace")
                break
        if text:
            break
    with open(path, "w") as f:
        f.write(text)
    return text[:limit]


_CAPTION = re.compile(r"^[ \t]*(Figure|Fig\.|Table)[ \t]*(\d+)[ \t]*[:.]?[ \t]*(.{0,180})", re.M)
_SECTION = re.compile(r"^[ \t]*(\d+(?:\.\d+){0,2})[ \t]*\n*[ \t]*([A-Z][^\n]{0,70})", re.M)
_APPENDIX = re.compile(r"\bAppendix[ \t]+([A-Z](?:\.\d+)*)")
# Above this, a line-leading numeral is a page number or a math expression rather than a
# section: measured, `55` and `212` are what a real paper's text offers at line start.
_SECTION_MAX = 20
_CAPTIONS_CHARS = 4000


def _runs(nums) -> str:
    """`1-8, 11, 13` from a set of numerals, which is the form a person checks against."""
    xs = sorted({int(n) for n in nums})
    out, i = [], 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[j + 1] == xs[j] + 1:
            j += 1
        out.append(str(xs[i]) if j == i else f"{xs[i]}-{xs[j]}")
        i = j + 1
    return ", ".join(out) or "(none found)"


def inventory(text: str) -> str:
    """What the paper's own numbering contains, lifted out of the text ahead of drafting.

    Two jobs, both of them code doing work the model was doing badly by hand.

    The pointer list is the one that pays. `evidence:` is a citation into the paper, and a
    citation to a section that does not exist is the error class `validate` makes fatal at
    `--accept` -- caught once already, a Limitations claim citing Section 7 of a paper
    whose last section is 6. Discovering that at review time is a round trip; handing over
    the real numbering costs nothing and removes the guess.

    The captions are lifted because they are where magnitudes live and because the full
    text is *truncated* -- beginning and end kept -- so a caption in the middle of a long
    paper is exactly what the model never sees. Half of a page's result claims must state
    a figure, and this is the densest source of them in any paper.

    Approximate, and safe in the direction it errs: PDF text loses column order, so a
    caption can arrive scrambled and a heading can be missed. Nothing here is authority --
    `check_claim_evidence` verifies pointers against the text independently.
    """
    from validate import deline
    text = deline(text)
    figs, tabs, caps, seen = set(), set(), [], set()
    for kind, num, rest in _CAPTION.findall(text):
        (tabs if kind == "Table" else figs).add(num)
        label = f"{'Table' if kind == 'Table' else 'Figure'} {num}"
        if label not in seen:
            seen.add(label)
            caps.append(f"{label}: {' '.join(rest.split())}")
    secs = sorted({s for s, _ in _SECTION.findall(text)
                   if int(s.split(".")[0]) <= _SECTION_MAX},
                  key=lambda s: [int(x) for x in s.split(".")])
    parts = [f"sections numbered in the text: {', '.join(secs) or '(none found)'}",
             f"figures: {_runs(figs)}",
             f"tables: {_runs(tabs)}",
             f"appendices: {', '.join(sorted(set(_APPENDIX.findall(text)))) or '(none found)'}",
             "Cite only pointers from these lists. A claim's `evidence` naming a section "
             "the paper does not have is rejected at accept time."]
    if caps:
        body, used = [], 0
        for c in caps:
            if used + len(c) > _CAPTIONS_CHARS:
                body.append(f"... {len(caps) - len(body)} more captions not shown")
                break
            body.append(c)
            used += len(c)
        parts += ["", "figure and table captions (where the magnitudes are, and the part "
                      "the truncation above may have cut):", *body]
    return "\n".join(parts)


def evidence(p: dict, cfg: dict, no_fulltext: bool = False) -> str:
    from validate import deline
    ft, ft_source = ("", "") if no_fulltext else fulltext(p, cfg)
    rm = "" if no_fulltext else readme(p)
    parts = [f"title: {p.get('title_display') or p['title']}",
             f"authors: {', '.join(p.get('authors') or []) or '(unknown)'}",
             f"venue: {p.get('venue_display') or p.get('venue') or '(preprint)'}",
             f"year: {p.get('year') or '?'}",
             f"citations: {p.get('citations') or 0}",
             f"arxiv: {p.get('arxiv') or '(none)'}",
             f"authors' own note: {p.get('arxiv_comment') or '(none)'}",
             f"code: {(p.get('links') or {}).get('code') or '(none known)'}", "",
             "abstract:",
             (p.get("abstract") or "(none)").strip(), ""]
    if ft:
        # Say which it is. The label used to read "truncated" unconditionally, so a dump
        # cut before the results section looked the same as a complete paper and there
        # was nothing to notice.
        cut = cut_chars(ft)
        how = (f"shortened to {len(ft):,} of {len(ft) + cut:,} characters, "
               "beginning and end kept, the gap marked in place"
               if cut else f"complete, {len(ft):,} characters")
        parts += ["what the paper's own numbering contains:", inventory(ft), "",
                  # Delined for the same reason the checkers deline: a PDF's line-number
                  # gutter is a column of numerals with no meaning, and a drafter reading
                  # `47` beside a sentence has been handed a magnitude that is not one.
                  # Generation and checking now read the same text.
                  f"full text (from {ft_source}; {how}):", deline(ft), ""]
    else:
        parts += ["full text: NOT AVAILABLE from any open source. Draft from the "
                  "abstract only,",
                  "and keep claims to what it states -- do not supply magnitudes it "
                  "does not give.", ""]
    if rm:
        parts += ["code README (for the authors' own naming and framing, truncated):",
                  rm]
    return "\n".join(parts)


# --------------------------------------------------------------- queue / write

def schema() -> dict:
    with open(os.path.join(ROOT, "schema", "sidecar.schema.json")) as f:
        s = json.load(f)
    # The same file the validator uses, minus the two meta keys the Messages API
    # rejects. One definition rather than two that drift.
    return {k: v for k, v in s.items() if k not in ("$schema", "$id")}


def held(spec: str) -> dict[str, str]:
    """Drafts a re-run must not touch: {slug: why}. Everything else is re-queueable.

    A draft holds its slot while it is current, and also while it is stale but
    hand-edited -- the second case is the one worth being careful about, because those
    are the two facts that conflict. The spec moved, so the file cannot be accepted as
    it stands; and a person has been in it, so nothing here may overwrite it. The way
    out is theirs to choose, so it gets reported rather than resolved.
    """
    out = {}
    for f in sorted(glob.glob(os.path.join(DRAFTS, "*.md"))):
        slug, why = os.path.basename(f)[:-3], stale(f, spec)
        if not why:
            out[slug] = "current"
        elif edited(f):
            out[slug] = f"{why}, and you have edited it"
    return out


def pending(papers: list[dict], do_all: bool, limit: int | None) -> list[dict]:
    """Papers with no live sidecar and no current draft, most cited first.

    A draft written against an acceptability spec that has since moved counts as no
    draft. It was written to different rules, `--accept` refuses it, and until this
    check existed nothing in the pipeline noticed -- which is how 17 drafts came to sit
    in that directory, not one of them acceptable, with no run ever replacing them.

    And a *live* sidecar that today's checks would refuse counts the same way, for the
    same reason and with more at stake: it is the file the site builds from. Excluding
    every paper with a live sidecar made acceptance permanent, so the two accepted before
    the scope rules existed were the only two files in the repo that no run could reach
    and no check would ever look at again. The draft that comes back is marked as
    replacing the live one and needs `--accept --replace`, which is machinery that
    already existed with nothing able to reach it.
    """
    live = {os.path.basename(f)[:-3] for f in glob.glob(os.path.join(SIDECARS, "*.md"))}
    from validate import outdated_live, read_sidecars
    live -= set(outdated_live(read_sidecars()[0]))
    keep = {} if do_all else held(spec_sha())
    out = [p for p in sorted(papers, key=lambda q: -(q.get("citations") or 0))
           if p["slug"] not in live and p["slug"] not in keep]
    return out[:limit] if limit else out


NO_TEXT = "full text: NOT AVAILABLE"   # what evidence() writes when the chain came up dry


def with_evidence(cands: list[dict], cfg, no_fulltext: bool,
                  limit: int | None) -> tuple[list[tuple[dict, str]], list[dict]]:
    """Resolve evidence in citation order; take the first `limit` papers that have text.

    The skip is the point. A paper no open source will give us has nothing to draft from
    but its title, and a sidecar written from a title is a page of confident guesses
    published under the author's name -- the one output here that is worse than no page.

    Applying the limit *after* the text check rather than before is what keeps the batch
    moving: filter-then-limit would let the same handful of unreachable papers fill every
    batch forever, so the reachable ones behind them would never get drafted.

    Nothing is remembered as hopeless. Each is retried on the next run, because a source
    added to fulltext.py today should rescue a paper that came up empty yesterday, and
    `data/fulltext/<slug>.pdf` should take effect the moment it appears.
    """
    ok: list[tuple[dict, str]] = []
    skipped: list[dict] = []
    for p in cands:
        ev = evidence(p, cfg, no_fulltext)
        if not no_fulltext and NO_TEXT in ev:
            skipped.append(p)
            continue
        ok.append((p, ev))
        if limit and len(ok) >= limit:
            break
    return ok, skipped


CONTRACT = [
    "Fill each task's `sidecar` object against `schema`. That is the whole job:",
    "everything else in this repo is code re-deriving public facts.",
    "Do not hand-edit data/*.yaml -- a hand edit to a derived file is undone by the",
    "next run. Do not run --accept: an accepted sidecar is an assertion under the",
    "author's name. Do not write outward (--apply, --deploy): those are public records.",
    "If a task's evidence says the full text is NOT AVAILABLE, draft nothing for it.",
    "A task whose `sidecar` is already filled carries `findings`: text that has been",
    "reviewed, and what today's checks say is wrong with it. Fix exactly those and",
    "change nothing else -- every other field is text a person has already read.",
]


def standing(slug: str) -> tuple[dict | None, list[str]]:
    """The text already written for this paper, and what today's checks say about it.

    A paper re-queued by `--all` almost always has something on disk: a draft nobody has
    accepted, or a live sidecar that a rule written after it was accepted now finds
    fault with. Handed an empty `sidecar` field, the only job available is to write the
    paper up again from scratch -- so a live file whose single finding is one sentence
    leaning on "The study" would be replaced wholesale, throwing away ten claims a
    person had already read and checked to fix a phrase. Seeded with the standing text
    and the findings against it, the job is the repair the `api` path has always had
    (`REPAIR`), and the review that has been done survives it.

    The draft is preferred over the live file when both exist: the draft is the newer of
    the two, and it is the one `--ingest` will overwrite.
    """
    for path in (os.path.join(DRAFTS, f"{slug}.md"),
                 os.path.join(SIDECARS, f"{slug}.md")):
        if os.path.exists(path):
            fm = front_matter(path)
            if fm:
                errs, qual = validate_draft(path, note=False)
                return fm, [str(x).split(".md: ")[-1] for x in errs + qual]
    return None, []


def emit_tasks(pairs: list[tuple[dict, str]], cfg) -> str:
    os.makedirs(BUILD, exist_ok=True)
    tasks = []
    for p, ev in pairs:
        fm, found = standing(p["slug"])
        t = {"slug": p["slug"], "title": p.get("title_display") or p["title"],
             "evidence": ev, "sidecar": fm}
        if fm is not None:
            # A group still in `unsorted` is not a clean group: it is a group written
            # before `ask` had named roles, exempted from the shape checks only so
            # migrating 1263 of them did not require guessing which route each phrasing
            # took. So it produces no finding, and saying "already clean" here would
            # send the one job a redraft exists to do back as nothing to do.
            legacy = sum(1 for g in (fm.get("qa") or [])
                         if isinstance(g.get("ask"), dict) and g["ask"].get("unsorted"))
            if legacy:
                found = found + [
                    f"{legacy} of {len(fm['qa'])} qa groups still hold their phrasings in "
                    f"`ask.unsorted` -- rewrite each group's `ask` as the roles "
                    f"(`plain` required, plus every other role that is a real question) "
                    f"and delete `unsorted`. Change no claim."]
            t["findings"] = found
            t["job"] = ("repair" if found else "already clean -- leave it alone")
        tasks.append(t)
    with open(TASKS, "w") as f:
        json.dump({"_contract": CONTRACT, "system": system_prompt(),
                   "user_template": USER, "schema": schema(), "tasks": tasks},
                  f, indent=1)
    return TASKS


# A sidecar is a large structured object, and reasoning tokens are drawn from the same
# budget: serialised, the existing pages run 30k-42k characters, so six of them exceed
# 8192 output tokens on their own before any thinking. A truncated response is not
# recoverable and, worse, arrives as invalid JSON -- which reads as "the model wrote
# something malformed" when it wrote something correct and got cut off.
API_MAX_TOKENS = 32000

# Appended to the user message on any endpoint that would not decode against the schema
# for us. One copy because three call sites need the identical sentence: a drafting call
# and a repair call on the OpenAI-compatible path, and both on the Anthropic path once a
# gateway turns out to reject `output_config.format`.
JSON_ONLY = "\n\nReturn one JSON object matching the schema. No prose, no fence."

# How each rung of the Anthropic ladder gets its shape guarantee, in the words the draft
# header and the retry line both use. "the model was told to" is the one that is not a
# guarantee, and it says so.
ENFORCED = {"schema": "schema-enforced", "tool": "schema-enforced via a forced tool call",
            "text": "unenforced, parsed from text"}



def call_api(pairs: list[tuple[dict, str]], cfg,
             on_draft=None) -> tuple[dict, str, "Callable"]:
    """One Messages API call per paper, validated against the sidecar schema.

    Returns the same triple as `call_openai` -- drafts, a provenance line, and the
    one-paper request as a closure -- so `repair` drives either backend. It used to
    return only the drafts, which quietly made `--repair` an open-weights-only feature:
    the loop that takes a draft from 55 findings to 0 was unavailable on the strongest
    model the config can name, and the researcher with the better model got the worse
    draft. Nothing about the loop was ever backend-specific; only this signature was.
    """
    try:
        import anthropic
    except ImportError:
        sys.exit("pip install anthropic, or set llm.mode: skill in config.yaml")
    client = anthropic.Anthropic()
    sch, out, sys_prompt = schema(), {}, system_prompt()
    eff = cfg["llm"].get("effort", "medium")
    # What the request adds, and how the sidecar comes back out of the reply. Tried in
    # order; the rung that works is remembered for the rest of the run.
    #
    # api.anthropic.com accepts the first. A gateway in front of the same model may not:
    # `ANTHROPIC_BASE_URL` pointed at a proxy answered `output_config.format: Extra inputs
    # are not permitted` with a 400. Hence a ladder rather than one fallback -- a forced
    # tool call is schema enforcement by another route, it predates structured output by
    # two years, and proxies pass it through, so a researcher whose access runs through one
    # still gets a decoded sidecar rather than whatever the model felt like emitting.
    #
    # `effort` rides along on every rung that will take it, because it is orthogonal to how
    # the shape is guaranteed and it is the setting that decides how hard the model thinks
    # about nine coupled fields. It was on the first rung only, which meant the rung that
    # actually carried the first live run silently dropped it and drafted at whatever the
    # endpoint defaults to -- the configured value applying on the one path that did not
    # work. Rung 3 exists for an endpoint that rejects `output_config` outright rather than
    # just its `format`, so losing effort costs the tool call rather than the other way
    # round. The last rung asks in the prompt and parses, which is a real result and is
    # labelled as one in the draft header.
    def rungs_for(want: dict, name: str, what: str) -> list:
        """The same four rungs around whichever shape this call asks for.

        A factory rather than one list built at the top, because `--mend` asks the same
        endpoint for a patch -- a handful of rewritten strings -- and enforcing the sidecar
        schema on that reply would reject every valid answer.
        """
        tool = {"tools": [{"name": name, "description": what, "input_schema": want}],
                "tool_choice": {"type": "tool", "name": name}}
        return [({"output_config": {"effort": eff,
                                    "format": {"type": "json_schema", "schema": want}}},
                 "schema", "structured output"),
                ({"output_config": {"effort": eff}, **tool},
                 "tool", f"a forced tool call at {eff} effort"),
                (tool, "tool", "a forced tool call"),
                ({}, "text", "a plain request")]
    # (what the request adds, how the reply is read, what to call it when refused).
    RUNGS = rungs_for(sch, "sidecar", "The sidecar for this paper.")
    rung, worked = 0, False

    def send(req: dict, extra: dict):
        """The request, streamed and accumulated back into one message.

        Streamed rather than `create()` because the SDK refuses any non-streaming call
        whose `max_tokens` implies more than ten minutes of generation -- at 32k it
        raises before sending anything. The alternative was capping the reply near 21k
        tokens, which is a limit on how long a sidecar may be, set by a client-side
        timeout heuristic.
        """
        try:
            with client.messages.stream(**req, **extra) as run:
                return run.get_final_message()
        except TypeError:                             # an SDK too old for the kwarg
            with client.messages.stream(**req, extra_body=extra) as run:
                return run.get_final_message()

    def ask(user: str, label: str, want: dict | None = None) -> dict | None:
        """One completion, or None with the reason printed. `label` is for the reader.

        `want` overrides the shape the reply is held to, for a caller that is not asking
        for a whole sidecar. The rung stays where the run found it -- the dialect the
        endpoint speaks is a property of the endpoint, not of what is being asked for.
        """
        nonlocal rung, worked
        ladder = RUNGS if want is None else rungs_for(want, "patch",
                                                      "The rewritten fields.")
        while True:
            extra, how_out, _ = ladder[rung]
            req = dict(model=cfg["llm"]["model"],
                       max_tokens=cfg["llm"].get("max_tokens", API_MAX_TOKENS),
                       system=sys_prompt,
                       messages=[{"role": "user", "content":
                                  user + (JSON_ONLY if how_out == "text" else "")}])
            try:
                msg = with_retries(lambda: send(req, extra), label)
                worked = True
                break
            except Exception as e:                    # noqa: BLE001 -- any 4xx means no
                # Whatever reaches here either is not the connection's fault or has
                # already been retried, so it is a real refusal.
                #
                # Only ever climb down before the first success. Once one request has gone
                # through, the endpoint's dialect is settled and a failure is a failure --
                # retrying it unenforced would quietly turn a rate limit into an
                # undecoded draft.
                if worked or rung + 1 >= len(ladder):
                    print(f"  failed: {label} -- {type(e).__name__}: {str(e)[:200]}",
                          file=sys.stderr)
                    return None
                rung += 1
                print(f"  {label}: the endpoint refused {ladder[rung - 1][2]}; "
                      f"retrying with {ladder[rung][2]}", file=sys.stderr)
        if msg.stop_reason == "refusal":
            print(f"  refused: {label}", file=sys.stderr)
            return None
        if msg.stop_reason == "max_tokens":
            # Named separately from a parse failure because the fix is different: raise
            # `llm.max_tokens`, do not go looking for a malformed field.
            print(f"  truncated at max_tokens: {label} -- raise llm.max_tokens "
                  f"(now {req['max_tokens']})", file=sys.stderr)
            return None
        if how_out == "tool":
            sc = next((b.input for b in msg.content if b.type == "tool_use"), None)
            if sc is None:
                print(f"  the forced tool call came back as prose: {label}",
                      file=sys.stderr)
            return sc
        text = next((b.text for b in msg.content if b.type == "text"), "")
        # `llm.first_json` rather than `json.loads` even on the enforced rung: it reads a bare
        # object identically, and on an unenforced one the object arrives inside a fence.
        sc = first_json(text)
        if sc is None:
            print(f"  no JSON object in the reply: {label} ({len(text)} chars)",
                  file=sys.stderr)
        return sc

    # Left at 0, which `fits` reads as "do not truncate the paper". Unlike the
    # OpenAI-compatible path, `max_tokens` here is a reply budget rather than part of a
    # sum with the prompt, and the input window is an order of magnitude larger than any
    # paper plus its sidecar -- so a repair round gets the whole text, tables included.
    ask.window = 0
    ask.wants_schema = True

    def provenance() -> str:
        """Where this draft came from, as of the rung currently working.

        A function rather than a string built at the end, because `on_draft` writes each
        draft as it lands and the header has to name the rung that produced *it*.
        """
        return (f"{cfg['llm']['model']} via the Anthropic API, {eff} effort "
                f"({ENFORCED[RUNGS[rung][1]]})")

    for p, ev in pairs:
        sc = ask(USER.format(evidence=ev), p["slug"])
        if sc is None:
            continue
        out[p["slug"]] = sc
        print(f"  ok  {p['slug']}  ({shape(sc, 'claims')} claims, "
              f"{shape(sc, 'qa')} question groups)")
        handed(on_draft, p["slug"], sc, provenance(), ask)
    return out, provenance(), ask


def handed(on_draft, slug: str, sc: dict, how: str, ask) -> None:
    """Hand one finished paper to the caller, and survive a paper that cannot be handed.

    Both backends give each draft away the moment it parses, so the run's work is durable
    per paper rather than per batch. That guarantee only holds if one bad paper cannot end
    the run: a reply with `claims` as a JSON string reached `validate_draft`, raised
    AttributeError, and killed a 96-paper pass 55 papers in -- every finished draft was
    already on disk, but the 41 that had not been asked for yet were simply not drafted.
    """
    if not on_draft:
        return
    try:
        on_draft(slug, sc, how, ask)
    except Exception as e:                              # noqa: BLE001 -- one paper, not the run
        print(f"      {slug} could not be written or checked ({type(e).__name__}: {e})"
              f" -- re-draft it with --slug {slug}")


def shape(sc: dict, field: str) -> str:
    """How many of `field` there are, or what came back instead of a list of them."""
    v = sc.get(field)
    return str(len(v)) if isinstance(v, list) else f"{type(v).__name__}, not a list of"


# An OpenAI-compatible backend, for gateways and open-weight models. Three env vars
# rather than config keys, and that split is deliberate: `config.yaml` is committed and
# public, while an inference gateway's URL may be internal to whoever is running this.
# So the endpoint is env-only and nothing about it can be committed by accident.
#
#   PAPER_GEO_LLM_BASE_URL   the /v1 base, e.g. https://<gateway>/<model-slug>/v1
#   PAPER_GEO_LLM_MODEL      the model id the body must carry (often vendor-prefixed)
#   PAPER_GEO_LLM_API_KEY    the key, if the gateway wants one
#   PAPER_GEO_LLM_KEY_HEADER optional header name to send the key under, for gateways
#                            that authenticate on a custom header instead of Bearer
def call_openai(pairs, cfg, on_draft=None) -> tuple[dict, str, "object"]:
    """One chat completion per paper against an OpenAI-compatible endpoint.

    Returns (answers, provenance). The same prompt and the same schema as the Anthropic
    path -- the point of this backend is that the rules are the variable under test and
    the model is not, so nothing here may reword anything.

    Schema enforcement is attempted and not required. vLLM-backed gateways accept
    `response_format: json_schema` and decode against it; others reject the field with a
    400, and refusing to run on those would make this backend useless for exactly the
    open models it exists to try. So: enforce if the endpoint allows it, otherwise ask
    in the prompt and parse what comes back -- and say which happened, because "the
    model produced a valid sidecar" and "the decoder could not produce anything else"
    are different results.
    """
    client, model = llm_client(model_default=cfg["llm"].get("model_openai"))

    # A hosted open-weight model has a context window the request has to fit inside, and
    # unlike the Anthropic path `max_tokens` is not a budget but part of that sum: Qwen
    # 2.5 72B at 32768 rejected the whole batch outright, because a paper's evidence runs
    # ~10.6k tokens and the reply was asked to reserve 32000. So ask the endpoint what it
    # can hold and reserve what is left. `/v1/models` is the only source for it, it is one
    # call, and a gateway that does not answer just leaves the configured number alone.
    window = None
    try:
        window = max((getattr(m, "max_model_len", None) or 0) for m in client.models.list())
    except Exception:                                # noqa: BLE001 -- optional refinement
        pass

    sch, out, sys_prompt = schema(), {}, system_prompt()
    enforced = None

    def ask(user: str, label: str, want_schema: dict | None = None) -> dict | None:
        """One completion, or None with the reason printed. `label` is for the reader.

        Extracted so the repair round below reuses the request exactly -- same schema,
        same window arithmetic, same fallback when the gateway will not enforce. A repair
        that quietly ran unguided while the draft was guided would compare two things.

        `want_schema` replaces the shape the reply is held to, for `--mend`, which asks for
        a patch rather than a whole sidecar.
        """
        nonlocal enforced
        msgs = [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user}]
        want = cfg["llm"].get("max_tokens", API_MAX_TOKENS)
        if window:
            # 3.2 chars per token is deliberately pessimistic for English prose, so the
            # estimate errs toward reserving less and getting a truncation warning rather
            # than toward a 400 that drops the paper entirely.
            used = int(sum(len(m["content"]) for m in msgs) / 3.2) + 512
            want = max(2048, min(want, window - used))
        req = dict(model=model, messages=msgs, max_tokens=want,
                   temperature=cfg["llm"].get("temperature", 0.2), seed=48)
        shape_of = sch if want_schema is None else want_schema
        rf = {"type": "json_schema",
              "json_schema": {"name": "sidecar" if want_schema is None else "patch",
                              "schema": decodable(shape_of), "strict": True}}
        try:
            r = with_retries(
                lambda: client.chat.completions.create(**req, response_format=rf), label)
            enforced = True if enforced is None else enforced
        except Exception as e:                        # noqa: BLE001 -- any 4xx means no
            if enforced:                              # it worked before, so this is real
                print(f"  failed: {label} -- {type(e).__name__}", file=sys.stderr)
                return None
            enforced = False
            try:
                r = with_retries(lambda: client.chat.completions.create(**req), label)
            except Exception as e2:                   # noqa: BLE001
                print(f"  failed: {label} -- {type(e2).__name__}: "
                      f"{str(e2)[:160]}", file=sys.stderr)
                return None
        ch = r.choices[0]
        if ch.finish_reason == "length":
            print(f"  truncated at max_tokens: {label} -- raise llm.max_tokens "
                  f"(now {req['max_tokens']})", file=sys.stderr)
            return None
        text = ch.message.content or ""
        sc = first_json(text)
        if sc is None:
            print(f"  no JSON object in the reply: {label} ({len(text)} chars)",
                  file=sys.stderr)
        return sc

    def provenance() -> str:
        how = "schema-enforced" if enforced else "unenforced, parsed from text"
        return f"{model} via an OpenAI-compatible endpoint ({how})"

    for p, ev in pairs:
        sc = ask(USER.format(evidence=ev)
                 + JSON_ONLY,
                 p["slug"])
        if sc is None:
            continue
        out[p["slug"]] = sc
        print(f"  ok  {p['slug']}  ({shape(sc, 'claims')} claims, "
              f"{shape(sc, 'qa')} question groups)")
        handed(on_draft, p["slug"], sc, provenance(), ask)
    # The window travels with the closure because `repair` has to fit a paper into what is
    # left of it and has no other way to know how big it is. An attribute rather than a
    # third return value: every caller wants the request, one wants its budget.
    ask.window = window or 0
    ask.wants_schema = True
    return out, provenance(), ask


HEADER = """<!-- DRAFT — not published, not read by anything that builds the site.

Drafted by `python scripts/draft_sidecars.py` from {source}. Every claim, number
and scope condition below is a machine's reading of the paper and needs your eyes.
{banner}
What to check, in the order it pays:

1. Each claim's NUMBER and BASELINE. A magnitude attributed to the wrong baseline is
   the one error here that is worse than saying nothing, because it is quotable.
2. Each SCOPE. This is the field summarisers drop, so it is the field this file exists
   for. If a scope reads like a disclaimer, replace it with the condition that
   actually bounds the result.
3. The MISREADINGS. A drafted misreading is a guess about your readers; you know which
   one keeps happening.
4. `one_liner`: the sentence you will reuse verbatim in the README, the model card and
   the talk abstract. Make it yours.

{promote}
{stamp}
-->
"""
_PROMOTE_NEW = "Then promote it:  python scripts/draft_sidecars.py --accept {slug}\n"
# Accepting over a reviewed sidecar is the one destructive path in this script, so the
# banner is at the top of the file rather than something the reader discovers from an
# error at accept time -- and the diff is named before the checklist, because here the
# comparison *is* the review. A live sidecar may be worded by the author, and a model's
# version being more complete does not make it better where the author was already
# right.
_BANNER_REPLACE = """
THIS PAPER ALREADY HAS A LIVE SIDECAR, and this draft would replace it. Start here:

  diff data/sidecars/{slug}.md data/sidecars/drafts/{slug}.md

Anything the live file says in your own words is worth keeping over a rewrite of the
same point, so read that diff before the checklist below.
"""
_PROMOTE_REPLACE = ("Then, if the replacement is the one you want:\n\n"
                    "  python scripts/draft_sidecars.py --accept {slug} --replace\n")


REPAIR = ("Here is the paper, a sidecar you drafted from it, and the findings an "
          "automated checker raised against the sidecar. Fix exactly what the findings "
          "name and change nothing else: keep every claim id, keep the questions pointing "
          "where they point. Go back to the paper for anything a finding asks you to add "
          "-- a magnitude belongs to a table you can re-read, and a scope below the length "
          "floor is short because the real conditions were dropped, not because the paper "
          "has none. Every number you write must appear in the paper's own text; if it is "
          "genuinely not there, leave that claim alone rather than inventing one -- an "
          "unfixed finding is a smaller problem than a wrong number."
          "\n\nPAPER:\n{evidence}\n\nSIDECAR:\n{sidecar}\n\nFINDINGS:\n{findings}"
          + JSON_ONLY)


REPAIR_REPLY_TOKENS = 8000       # room a rewritten sidecar needs, measured on a 16-claim one


def fits(evidence: str, sidecar: str, window: int) -> str:
    """As much of the paper as leaves the model room to answer, head and tail.

    A repair prompt is the only one here that carries the paper *and* a full sidecar, and
    on a 32k window those two do not both fit: TIES-Merging's text is 74k chars, which
    left 2048 tokens for a reply that needs about four thousand, so round one came back
    truncated and the loop dutifully kept the draft it had been asked to fix. Silent, and
    it looked like a model that had nothing to add.

    Head and tail rather than the first N chars, because the findings that need the paper
    are the ones asking for a magnitude, and magnitudes are in the tables -- which are at
    the end, exactly where a front-truncation cuts. The middle is the related work and the
    method prose, which the claims are already written from.
    """
    if not evidence or not window:
        return evidence
    room = int((window - len(sidecar) / 3.2 - REPAIR_REPLY_TOKENS - 4000) * 3.2)
    if room >= len(evidence):
        return evidence
    if room < 4000:                      # nothing useful survives; answer from the sidecar
        return ""
    head = int(room * 0.45)
    return (evidence[:head] + "\n\n[... middle of the paper omitted to leave room for "
            "your answer; the tables are below ...]\n\n" + evidence[-(room - head):])


# How much of a sidecar a repair round may drop and still be believed. A round that
# genuinely merges two overlapping claims removes one; a round that has given up removes
# most of them, and scores well for it.
KEEPS = 0.6


def shrunk(before: dict, after: dict) -> str | None:
    """What a reply dropped wholesale, or None if it kept the sidecar it was given."""
    for field in ("claims", "qa"):
        was, now = len(before.get(field) or []), len(after.get(field) or [])
        if was and now < max(1, int(was * KEEPS)):
            return f"{was - now} of {was} {field}"
    return None


def repair(slug: str, rounds: int, again, evidence: str = "",
           source: str = "a model") -> int:
    """Re-ask the model to fix what the checker found, up to `rounds` times.

    This is the answer to "can a smaller model do this if the job is broken up". It can,
    and the split that pays is not nine calls for nine fields -- it is one draft plus a
    critique it did not write. Measured on Qwen 2.5 72B, one paper: 20 findings, then 5,
    then 2 after two rounds, with no rule reworded. The remaining two are the honest ones,
    where the fix is a magnitude from a table the model will not invent.

    `again(prompt_extra)` is the caller's own one-paper call, so this function knows
    nothing about which backend it is driving.

    `evidence` is the same paper text the draft was written from, and it is what decides
    which findings are fixable. Without it the loop can only re-word what it already
    wrote, so every finding that asks for a fact -- a magnitude a claim dropped, the real
    conditions behind a scope that came out under the length floor -- was unfixable by
    construction, and the loop's honest answer was to leave it. Measured on the two
    published sidecars: the residue after three blind rounds was 3 and 5 findings, and
    all of it was of that kind.

    Stops early when a round stops helping, because a round that does not reduce the count
    is a round spending tokens to reword: the loop optimises against proxies, and past the
    point where it is still fixing things, what it does instead is satisfy them. The
    shared-scope check in `validate.py` exists because this loop found that edge -- it
    converged on one scope that cleared the wording rules and pasted it across eight
    claims, which is a fix to the checker's eye and a regression to a reader's.
    """
    path = os.path.join(DRAFTS, f"{slug}.md")
    best = None
    for r in range(rounds):
        errs, qual = validate_draft(path, note=False)
        n = len(errs) + len(qual)
        if best is not None and n >= best:
            print(f"    round {r + 1}: {n} finding(s), no better than {best} -- stopping")
            break
        best = n
        if not n:
            break
        fm = front_matter(path) or {}
        found = "\n".join(f"- {str(x).split('.md: ')[-1]}" for x in errs + qual)
        ev = fits(evidence, json.dumps(fm), getattr(again, "window", 0))
        sc = again(REPAIR.format(evidence=ev or "(not available on this run)",
                                 sidecar=json.dumps(fm, ensure_ascii=False, indent=1),
                                 findings=found), f"{slug} repair {r + 1}")
        if sc is None:
            print(f"    round {r + 1}: no usable reply, keeping the draft as it stands")
            break
        # Deleting the content is the cheapest way to satisfy a checker, and the loop had no
        # defence against it: one round answered 17 findings with a sidecar holding none of
        # the paper's 12 claims and none of its 8 question groups, scored 2, and was kept
        # because 2 < 17. A round may merge or split claims; it may not drop the sidecar on
        # the floor. Refused before it is written, so the draft on disk never passes through
        # the collapsed state.
        gone = shrunk(fm, sc)
        if gone:
            print(f"    round {r + 1}: the reply dropped {gone} -- refused, kept the "
                  f"{n}-finding draft")
            break
        was = open(path, encoding="utf-8").read()
        # `source` is threaded in rather than read back off the draft: the model's name
        # lives in the header comment, not in the front matter, so the old
        # `fm.get('_source')` never found anything and every repaired draft recorded
        # "a model" -- losing the one fact the header exists to keep.
        rnd = "round" if r == 0 else "rounds"
        write_draft(slug, sc, f"{source} + {r + 1} repair {rnd}")
        after = sum(len(x) for x in validate_draft(path, note=False))
        if after > n:
            # Keep the better draft. The early stop above only skips the *next* round, so
            # a final round that overshoots still landed on disk and replaced the draft it
            # was meant to improve -- live case: 15 -> 7 -> 4 -> 6, and the 6 was what was
            # left for the reviewer. The overshoot is the loop's characteristic failure
            # rather than bad luck: told a scope is too long it cuts, and cutting past the
            # floor trades one finding for another, so the round both fixes and breaks.
            open(path, "w", encoding="utf-8").write(was)
            print(f"    round {r + 1}: {n} finding(s) -> {after}, worse -- kept the "
                  f"{n}-finding draft")
            break
        print(f"    round {r + 1}: {n} finding(s) -> {after}")
    return sum(len(x) for x in validate_draft(path, note=False))


MEND = """Below are individual fields from one paper's sidecar, each with the checker's
complaint about it. Rewrite only the fields listed, and only as much of each as the
complaint requires.

{evidence}

FIELDS TO FIX (JSON):
{pieces}

Rules for your answer:
- Return one entry per field you fixed, with `at` copied exactly as given and `new` holding
  the complete rewritten value of that field -- not a diff, not a fragment.
- Each field carries the `limits` its rewritten value must satisfy. A rewrite that clears the
  complaint and breaks one of those is thrown away, so read them before you write.
- Keep the meaning. A shorter sentence that drops the paper's magnitude is not a fix.
- Never give two fields the same text. If a scope is too long, shorten that scope; do not
  replace it with wording you used elsewhere.
- Where the complaint is that a name or a phrase must not appear, the rewritten value must
  not contain it -- say what the thing is instead of naming it.
- A complaint that a claim states no magnitude is fixed with a number the paper itself
  reports, copied from the text above. Never round one, derive one, or supply one from
  memory: a figure that is not in the paper is a worse finding than the one you were asked
  to fix. Leave the field out if the paper gives none for that claim.
- Leave out any field you cannot fix without inventing something the paper does not say.
"""

# Every value a locus can name is a plain string, so the patch schema needs no `oneOf` --
# which matters because the enforcing rungs run in strict mode and reject a union.
PATCH_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["fixes"],
    "properties": {"fixes": {
        "type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["at", "new"],
            "properties": {
                "at": {"type": "string",
                       "description": "The locus, copied exactly from the field given."},
                "new": {"type": "string",
                        "description": "The whole rewritten value of that field."}}}}},
}


ROUTES = """Below is one paper's claims and its question groups. Every group's phrasings
were written before `ask` had named roles, so they sit in `unsorted`: two or three
rewordings of one sentence, most of them third person and built around the paper's own
vocabulary. Rewrite each group's `ask` as the roles.

You are not writing new questions. Each group already asks something, and its answer is
fixed -- the claims listed under `answered_by`. Keep asking that, in four vocabularies.

CLAIMS (the answers, and the only things a question may be answered by):
{claims}

GROUPS TO REROUTE (JSON):
{groups}

Rules for your answer:
- One entry per group, with `index` copied exactly as given.
- `plain` is required. Fill every other role that is a real question for that group, and
  leave a role out rather than padding it with a reworded copy of another -- an empty role
  is the honest answer where no such person exists.
- Keep the subject. A group answered by a claim about out-of-domain generalization must
  still be about out-of-domain generalization in all four roles.
- The existing phrasings are given as evidence of what the group asks, not as text to
  edit. A role that reads as a light rewording of one of them has done nothing.
- Never state an answer, a magnitude, or a claim. These are queries.

The question rules the phrasings are judged by follow, from {doc}. Only those apply to
you: you are changing no claim, and the schema accepts nothing but `ask` roles.

{rules}
"""

ROUTES_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["groups"],
    "properties": {"groups": {
        "type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["index", "plain"],
            "properties": {
                "index": {"type": "integer",
                          "description": "The group index, copied exactly as given."},
                "plain": {"type": "string",
                          "description": "Someone who has not read the paper, in their "
                                         "own words: no jargon, no coined name."},
                "jargon": {"type": "string",
                           "description": "A specialist, in the field's own terms."},
                # "Someone describing what they are trying to do" is what this said, and
                # 59 replies obliged with a description: "I am choosing sizes for my
                # preliminary runs and want to know how large the biggest one needs to be."
                # A field description is an instruction, so it has to ask for the question.
                "task": {"type": "string",
                         "description": "The same question asked in terms of what they "
                                        "are trying to do -- still one question, ending "
                                        "in '?', never a statement of what they are "
                                        "doing."},
                "practitioner": {"type": "string",
                                 "description": "Someone deciding, in the first person. "
                                                "Leave out if there is no such question."},
            }}}},
}


def reroute(slug: str, again, source: str = "a model") -> tuple[int, int]:
    """Rewrite one live sidecar's `ask` blocks as the named roles. Nothing else moves.

    The narrowest possible redraft, and narrow on purpose. A full redraft of an accepted
    sidecar is a claim rewrite -- run once on `fusing-finetuned-models`, it returned 9
    claims where the author had verified 11, with a different `one_liner` and different
    misreadings. Migrating 113 papers that way would discard every figure that has been
    checked against its paper and ask for all of it to be checked again, to fix questions.

    So the model never sees the paper here: the claims *are* the answers, the group already
    says what it asks, and what is missing is only the vocabulary each kind of person would
    have typed. Returns `(groups rerouted, findings left on the draft)`.
    """
    # The draft when one exists, since that is what `--accept` will promote; the live file
    # otherwise.
    fm = next((front_matter(path) for path in (os.path.join(DRAFTS, f"{slug}.md"),
                                              os.path.join(SIDECARS, f"{slug}.md"))
               if os.path.exists(path)), None)
    if not fm:
        return 0, 0
    groups = fm.get("qa") or []
    todo = [i for i, g in enumerate(groups)
            if isinstance(g.get("ask"), dict) and g["ask"].get("unsorted")]
    if not todo:
        return 0, 0
    claims = "\n".join(f"[{c['id']}] ({c.get('kind')}) {oneline(c.get('text'))}"
                       for c in (fm.get("claims") or []))
    pieces = json.dumps([{"index": i, "answered_by": groups[i].get("answered_by"),
                          "asks_now": groups[i]["ask"]["unsorted"]} for i in todo],
                        ensure_ascii=False, indent=1)
    got = again(ROUTES.format(claims=claims, groups=pieces, doc=RULES_DOC,
                             rules=rules_block(RULES_DOC)), f"{slug} reroute",
                ROUTES_SCHEMA)
    back = (got or {}).get("groups")
    if not isinstance(back, list):
        print(f"    reroute: no usable reply, leaving {slug} as it stands")
        return 0, 0
    done = 0
    for item in back:
        if not isinstance(item, dict) or item.get("index") not in todo:
            continue
        ask = {r: " ".join(str(item[r]).split()) for r in QA_ROLES
               if isinstance(item.get(r), str) and item[r].strip()}
        # `plain` missing means the one required route did not come back, and a group with
        # only `jargon` filled is worse than the legacy group it would replace: legacy is
        # exempt from the shape checks, so the file would go from passing to failing while
        # losing the phrasings it had. Leave those groups in `unsorted` for the next pass.
        if "plain" not in ask:
            continue
        groups[item["index"]]["ask"] = ask
        done += 1
    if not done:
        return 0, 0
    write_draft(slug, fm, source + " + rerouted questions")
    errs, qual = validate_draft(os.path.join(DRAFTS, f"{slug}.md"), note=False)
    return done, len(errs) + len(qual)


def where(finding: str, fm: dict | None = None) -> str | None:
    """The single field a finding is about, as a locus, or None if it is about no one field.

    A locus is `claim/<id>/text`, `claim/<id>/scope`, `qa/<i>/ask/<role>`,
    `qa/<i>/ask/unsorted/<j>`, `misreadings/<i>` or
    `term/<name>` -- a path whose leaf is always a string, which is what lets the patch
    schema stay a flat list of replacements with no union in it.

    Two kinds of finding are addressable, and they say so differently. Most name their
    field: `claim 'x': ...`, `term 'y': ...` -- and one of them, the invented-figure check,
    without the colon (`claim 'x' states 29`), which is why the separator is optional here;
    while it was not, three drafts kept a finding a single rewrite would have cleared. The
    self-containment checks instead open with the offending string itself, followed by ` -- `
    and the complaint, so those are located by looking the string up in the draft -- which
    needs `fm`, and without it they come back None rather than guessed at.

    None is the useful half of this function: a finding about the whole set of claims -- band
    counts, an orphan claim -- must not be answered by rewriting whichever claim it was
    handed. Where the set itself is computable, `spread` names it instead, and the caller
    sends those fields over as one group.
    """
    m = re.match(r"^claim '([^']+)'(?:: | )(.*)", finding)
    if m:
        cid, rest = m.groups()
        if rest.startswith("scope"):
            return f"claim/{cid}/scope"
        if re.match(r"^(a \d+-word sentence|text is \d+ sentences|text leans on"
                    r"|states )", rest):
            return f"claim/{cid}/text"
        return None
    m = re.match(r"^qa\[(\d+)\]: every phrasing contains", finding)
    if m:
        i = int(m.group(1))
        groups = (fm or {}).get("qa") or []
        loci = qa_loci(groups[i]) if i < len(groups) else []
        return f"qa/{i}/{loci[0][0]}" if loci else None
    m = re.match(r"^term '([^']+)': ", finding)
    if m:
        return f"term/{m.group(1)}"
    if fm is not None and " -- " in finding:
        return _quoting(fm, finding.split(" -- ")[0].strip())
    return None



TOGETHER = ("this claim states no magnitude, and fewer than half of this page's result "
            "claims do -- add the figure the paper reports for this claim, or leave this "
            "field out")


def spread(finding: str) -> list[str]:
    """The fields a page-level finding is about, when the set of them is computable.

    `where` returns None for the figure floor because no single claim is at fault, and that
    was read as "not mendable" for too long: the *set* is exactly known -- every `result`
    claim that states no figure -- and it is the largest family left in the corpus, 9 of the
    18 drafts still carrying findings. Handing them over together is safe here for a reason
    that does not generalise: a number invented to satisfy this is caught by
    `check_claim_numbers` against the paper's own text, and mend reverts the whole group
    when the count does not fall.
    """
    m = re.match(r"^only \d+ of \d+ result claims state a figure.*?Number-free: (.+)$",
                 finding, re.S)
    if m:
        # Read off the finding rather than recomputed from `fm`: the check already names the
        # claims that dropped a number, and a second implementation of "states a figure"
        # here would drift from `figures` the first time either changes.
        return [f"claim/{cid.strip()}/text" for cid in m.group(1).split(",") if cid.strip()]
    return []

def _quoting(fm: dict, value: str) -> str | None:
    """The locus of a question phrasing or misreading bullet whose text is exactly `value`.

    None when two fields hold the same string: a fix aimed at one of them would be spliced
    into whichever was found first, and a duplicate is its own finding anyway.
    """
    hits = [f"qa/{i}/{suffix}"
            for i, group in enumerate(fm.get("qa") or [])
            for suffix, phrasing in qa_loci(group)
            if phrasing == value]
    hits += [f"misreadings/{i}" for i, bullet in enumerate(fm.get("misreadings") or [])
             if bullet == value]
    return hits[0] if len(hits) == 1 else None


def _walk(fm: dict, locus: str):
    """(container, key) for a locus, or None if the draft no longer has that field.

    Findings are read off the draft on disk a moment before this runs, so a miss means the
    locus was parsed wrong rather than that the draft moved -- either way the caller drops
    that field instead of guessing where it went.
    """
    part = locus.split("/")
    if part[0] == "claim" and len(part) == 3:
        for c in fm.get("claims") or []:
            if isinstance(c, dict) and str(c.get("id")) == part[1] and part[2] in c:
                return c, part[2]
        return None
    # `qa/<i>/ask/<role>` patches a role in place; `qa/<i>/ask/unsorted/<j>` patches one
    # legacy phrasing. Both leaves are strings, which is what keeps the patch schema a flat
    # list of replacements -- see `where`.
    if part[0] == "qa" and part[2:3] == ["ask"] and len(part) in (4, 5):
        groups = fm.get("qa") or []
        try:
            ask = groups[int(part[1])]["ask"]
            if len(part) == 4 and part[3] in QA_ROLES and isinstance(ask[part[3]], str):
                return ask, part[3]
            if len(part) == 5 and part[3] == "unsorted":
                legacy, j = ask["unsorted"], int(part[4])
                if isinstance(legacy, list) and isinstance(legacy[j], str):
                    return legacy, j
        except (ValueError, IndexError, KeyError, AttributeError, TypeError):
            return None
    if part[0] == "misreadings" and len(part) == 2:
        bullets = fm.get("misreadings")
        try:
            i = int(part[1])
            if isinstance(bullets, list) and isinstance(bullets[i], str):
                return bullets, i
        except (ValueError, IndexError, TypeError):
            return None
    if part[0] == "term":
        # Split once from the left, so a term containing a slash still resolves.
        name = locus.split("/", 1)[1]
        terms = fm.get("terminology")
        if isinstance(terms, dict) and isinstance(terms.get(name), str):
            return terms, name
    return None


def at(fm: dict, locus: str) -> str | None:
    """The string a locus points at, or None."""
    spot = _walk(fm, locus)
    if not spot:
        return None
    box, key = spot
    value = box[key]
    return value if isinstance(value, str) else None


def put(fm: dict, locus: str, value: str) -> bool:
    """Write one string back where it came from. False if the locus does not resolve."""
    spot = _walk(fm, locus)
    if not spot:
        return False
    box, key = spot
    box[key] = value
    return True


def limits(locus: str) -> str:
    """The rules the rewritten value still has to pass, in the words of the checks.

    Without this the most common finding in the corpus was also the least fixable. A claim
    whose first sentence runs 36 words is already two sentences long, so splitting it makes
    three and trades the length finding for a structure one; the rewrite gets reverted, and
    the draft plateaus on a finding a five-word compression would have cleared. The model was
    not failing to write -- it was not told which way was out.
    """
    from validate import (CLAIM_SENTENCE_WORDS, CLAIM_SENTENCES, CLAIM_SEPARATORS,
                          SCOPE_RATIO_FLOOR, SCOPE_SENTENCES)
    if locus.endswith("/text"):
        return (f"at most {CLAIM_SENTENCES} sentences, no sentence over "
                f"{CLAIM_SENTENCE_WORDS} words, at most {CLAIM_SEPARATORS} semicolon or "
                f"dash. Compress rather than split if splitting would make a third "
                f"sentence, and keep every figure.")
    if locus.endswith("/scope"):
        return (f"at most {SCOPE_SENTENCES} sentences, and no longer than the claim it "
                f"bounds unless the claim is under {SCOPE_RATIO_FLOOR} characters. It is "
                f"published after the words \"Holds for:\", so give the condition, not a "
                f"description of the claim.")
    if locus.startswith("qa/"):
        role = locus.split("/")[-1]
        which = {"plain": "in the words of someone who has not read the paper, with no "
                          "jargon and no coined name",
                 "jargon": "in the field's own vocabulary",
                 "task": "phrased as the thing they are trying to do",
                 "practitioner": "in the first person, deciding whether to use this"}
        return ("a question someone would type, ending in `?`, answerable on its own with "
                "no paper title beside it, so every reference in it has to name what it "
                "points at"
                + (f" -- and this one is the `{role}` route, so keep it {which[role]}."
                   if role in which else "."))
    return "keep it a single plain string, and keep the meaning."


def mend(slug: str, again, evidence: str = "", source: str = "a model") -> int:
    """Fix what is fixable one field at a time, and keep the result only if it helped.

    The difference from `repair` is what the model is shown and what it is allowed to
    return. `repair` hands over the whole sidecar and takes a whole sidecar back, so a round
    can regress a claim it was not asked about while fixing the one it was -- measured as
    the plateau this loop stops on, where the count stops falling because each round trades
    one finding for another. Here the model sees only the offending strings, and the reply
    is a list of `(locus, new value)` pairs that are spliced back into the draft the rest of
    which cannot move.

    Returns the finding count the draft is left with, mended or not.
    """
    path = os.path.join(DRAFTS, f"{slug}.md")
    errs, qual = validate_draft(path, note=False)
    before = len(errs) + len(qual)
    if not before:
        return 0
    fm = front_matter(path) or {}
    jobs: dict[str, list[str]] = {}
    crowd: dict[str, list[str]] = {}
    for finding in (str(x).split(".md: ")[-1] for x in errs + qual):
        locus = where(finding, fm)
        if locus and at(fm, locus) is not None:
            jobs.setdefault(locus, []).append(finding)
            continue
        for locus in spread(finding):
            if at(fm, locus) is not None:
                crowd.setdefault(locus, []).append(TOGETHER)
    # A field named by a finding of its own is fixed on its own terms; the group is only for
    # the fields nothing else complained about.
    crowd = {locus: found for locus, found in crowd.items() if locus not in jobs}
    if not jobs and not crowd:
        print(f"    mend: none of the {before} finding(s) is about a single field")
        return before
    fields = [{"at": locus, "now": at(fm, locus), "wrong": found, "limits": limits(locus)}
              for locus, found in list(jobs.items()) + list(crowd.items())]
    pieces = json.dumps(fields, ensure_ascii=False, indent=1)
    ev = fits(evidence, pieces, getattr(again, "window", 0))
    got = again(MEND.format(evidence=("THE PAPER:\n" + ev) if ev
                            else "(the paper's text is not available on this run)",
                            pieces=pieces), f"{slug} mend", PATCH_SCHEMA)
    fixes = (got or {}).get("fixes")
    if not isinstance(fixes, list):
        print(f"    mend: no usable reply, keeping the draft as it stands")
        return before
    new: dict[str, str] = {}
    for fix in fixes:
        locus = (fix or {}).get("at") if isinstance(fix, dict) else None
        value = fix.get("new") if isinstance(fix, dict) else None
        if (locus in jobs or locus in crowd) and isinstance(value, str) and value.strip() \
                and value.strip() != at(fm, locus):
            new[locus] = value.strip()
    # One replacement text landing at two loci is the pathology `validate.py`'s shared-scope
    # check was added for: told several scopes are too long, a model can answer with one
    # wording that clears the rules and paste it into all of them. Drop the whole group
    # rather than pick a winner -- there is no way to tell which one it was written for.
    seen: dict[str, list[str]] = {}
    for locus, value in new.items():
        seen.setdefault(value, []).append(locus)
    for value, loci in seen.items():
        if len(loci) > 1:
            print(f"    mend: dropped {len(loci)} field(s) given identical text "
                  f"({', '.join(loci)})")
            for locus in loci:
                del new[locus]
    if not new:
        print(f"    mend: nothing usable came back, keeping the {before}-finding draft")
        return before
    singles = {locus: value for locus, value in new.items() if locus in jobs}
    bulk = {locus: value for locus, value in new.items() if locus in crowd}
    # Each field's rewrite stands or falls on its own, spliced and checked one at a time.
    # Accepting or rejecting the patch as a whole loses both ways: it threw away five good
    # fixes because a sixth traded one finding for another, and it kept five rewrites that
    # changed nothing because a sixth happened to help. Live case: 6 fields rewritten, 1
    # finding cleared, 5 of the rewrites pointless churn in a draft a human then has to
    # re-read.
    kept, undone, count = [], [], before
    for locus, value in singles.items():
        snapshot, held = open(path, encoding="utf-8").read(), at(fm, locus)
        put(fm, locus, value)
        write_draft(slug, fm, f"{source} + a targeted repair")
        errs, qual = validate_draft(path, note=False)
        found = [str(x).split(".md: ")[-1] for x in errs + qual]
        mine = [f for f in found if where(f, fm) == locus]
        # Cleared its own complaint, and cost nothing anywhere else. The second half is
        # what catches a fix that reads as an improvement and breaks a rule next door --
        # a scope cut under the length floor, a claim whose figure went with the sentence.
        if not mine and len(found) < count:
            kept.append(locus)
            count = len(found)
        else:
            put(fm, locus, held)
            open(path, "w", encoding="utf-8").write(snapshot)
            undone.append(locus)
    # The group is the one exception, and it has to be: no single added magnitude clears a
    # ratio finding, so field-by-field verification would revert every one of them and the
    # largest family of findings in the corpus would stay untouched. So they stand or fall
    # together, and the falling half matters -- a magnitude the paper does not contain shows
    # up as its own finding, the count fails to drop, and the whole group goes back.
    if bulk:
        snapshot = open(path, encoding="utf-8").read()
        held = {locus: at(fm, locus) for locus in bulk}
        for locus, value in bulk.items():
            put(fm, locus, value)
        write_draft(slug, fm, f"{source} + a targeted repair")
        errs, qual = validate_draft(path, note=False)
        found = [str(x).split(".md: ")[-1] for x in errs + qual]
        mine = [f for f in found if where(f, fm) in bulk]
        if not mine and len(found) < count:
            kept += list(bulk)
            count = len(found)
        else:
            for locus, was in held.items():
                put(fm, locus, was)
            open(path, "w", encoding="utf-8").write(snapshot)
            undone += list(bulk)
    if undone:
        print(f"    mend: {len(undone)} rewrite(s) did not fix what was asked, reverted "
              f"({', '.join(undone)})")
    if not kept:
        print(f"    mend: nothing usable came back, keeping the {before}-finding draft")
        return before
    print(f"    mend: {before} finding(s) -> {count} "
          f"({len(kept)} of {len(jobs) + len(crowd)} field(s) rewritten)")
    return count


def unstructure(value, spec: dict):
    """Put a reply back into the shape the schema asked for, where that is lossless.

    A forced tool call over-structures. `misreadings` is declared as an array of plain
    strings, and in one live pass three drafts came back with it as an array of objects:
    `[{"text": "The 0.77 accuracy ..."}]` in one, and a string exploded character by
    character into `{"0": "T", "1": "h", "2": "e", ...}` in two more. Every one of those is
    a string wearing an object, every one converts back exactly, and left alone each costs
    a schema error -- which, before the tier was isolated, silently suppressed nine other
    findings on the same draft.

    So this is deliberately narrow: it only ever turns an object into the string the schema
    already required, and only when the object holds nothing the string does not. Anything
    else is returned untouched, because a shape the schema rejects and code cannot
    unambiguously recover is a finding for the author, not a guess for the code.
    """
    if not isinstance(spec, dict):
        return value
    kind = spec.get("type")
    if kind == "string" and isinstance(value, dict) and value:
        keys = list(value)
        if all(str(k).isdigit() for k in keys) and all(isinstance(v, str) for v in value.values()):
            return "".join(value[k] for k in sorted(keys, key=lambda k: int(k)))
        if len(keys) == 1 and isinstance(value[keys[0]], str):
            return value[keys[0]]
        text = value.get("text")
        if isinstance(text, str):
            return text
        return value
    if kind in ("array", "object") and isinstance(value, str):
        # A whole array handed back as a JSON string. One live reply returned `claims` as
        # 7618 characters of JSON text, which read as 7618 claims and then raised on the
        # first character. `json.loads` either produces exactly the type the schema asked
        # for -- in which case nothing was guessed -- or it does not and the string stays
        # put as a finding.
        try:
            got = json.loads(value)
        except (ValueError, TypeError):
            return value
        if isinstance(got, list if kind == "array" else dict):
            return unstructure(got, spec)
        return value
    if kind == "array" and isinstance(value, list):
        return [unstructure(v, spec.get("items") or {}) for v in value]
    if kind == "object" and isinstance(value, dict):
        props = spec.get("properties") or {}
        extra = spec.get("additionalProperties")
        out = {}
        for k, v in value.items():
            sub = props.get(k) or (extra if isinstance(extra, dict) else {})
            out[k] = unstructure(v, sub or {})
        return out
    return value


def write_draft(slug: str, sidecar: dict, source: str) -> str:
    # Every path that writes a draft comes through here -- the drafting call, each repair
    # round, --restamp -- so one call covers all of them.
    sidecar = unstructure(sidecar, schema())
    os.makedirs(DRAFTS, exist_ok=True)
    path = os.path.join(DRAFTS, f"{slug}.md")
    body = yaml.safe_dump(sidecar, sort_keys=False, allow_unicode=True,
                          default_flow_style=False, width=88)
    live = os.path.exists(os.path.join(SIDECARS, f"{slug}.md"))
    banner = _BANNER_REPLACE.format(slug=slug) if live else ""
    promote = (_PROMOTE_REPLACE if live else _PROMOTE_NEW).format(slug=slug)
    stamp = f"Stamp: spec={spec_sha()} checks=? body={sha(body)}"
    with open(path, "w") as f:
        f.write(HEADER.format(source=source, banner=banner, promote=promote,
                              stamp=stamp) + "---\n" + body + "---\n")
    # The checks have to run against the written file, so the stamp is finished in
    # place. Recording the verdict is what makes "the rules moved under this draft"
    # distinguishable later from "the model wrote a draft that never passed".
    n = sum(len(x) for x in validate_draft(path, note=False))
    text = open(path).read().replace("checks=?", "checks=pass" if not n else f"checks={n}")
    with open(path, "w") as f:
        f.write(text)
    return path


def restamp(slugs: list[str] | None = None) -> tuple[list[str], list[tuple[str, str]]]:
    """Re-check drafts as they stand and rewrite their stamps. Returns (done, refused).

    The operation that was missing, and the gap was structural: `spec_sha` hashes the
    source of every function that judges a draft, so editing any check -- even adding a
    rule that the drafts already satisfy -- marks all of them "spec moved". The only way
    back was `--ingest`, which rewrites front matter from the task file and destroys the
    author's review, which is the one thing here that cannot be re-derived. So a checker
    edit either cost the review or left the drafts parked; this is the third option.

    It refuses a draft that does not currently pass, and that restriction is the whole
    safety property. A stamp is what makes `pending` skip a slug and `held` keep it, so
    stamping a failing draft would park it where nothing queues it and nothing reports it.
    A draft that fails the new rules should stay stale until somebody fixes it or replaces
    it -- which is what `held` already says out loud.
    """
    spec, done, refused = spec_sha(), [], []
    for f in sorted(glob.glob(os.path.join(DRAFTS, "*.md"))):
        slug = os.path.basename(f)[:-3]
        if slugs and slug not in slugs:
            continue
        n = sum(len(x) for x in validate_draft(f, note=False))
        if n:
            # "left stale" was wrong for most of these: a draft can carry findings and
            # still be stamped against the current spec, and 24 of 43 refusals were that
            # -- current drafts with open findings, which is the ordinary state of a draft
            # waiting to be read, not something a re-draft would fix.
            why = f"{n} finding(s) against the current checks"
            refused.append((slug, why if stale(f, spec) else f"{why} -- not stale, yours"))
            continue
        text = open(f).read()
        want = f"Stamp: spec={spec} checks=pass body={sha(body_of(f))}"
        if STAMP.search(text):
            text = STAMP.sub(want, text, count=1)
        else:
            refused.append((slug, "no Stamp line to rewrite -- re-draft it instead"))
            continue
        with open(f, "w") as fh:
            fh.write(text)
        done.append(slug)
    return done, refused


def ingest(papers: list[dict]) -> int:
    if not os.path.exists(TASKS):
        sys.exit(f"no {TASKS} -- run without --ingest first")
    with open(TASKS) as f:
        d = json.load(f)
    n = 0
    for t in d["tasks"]:
        if not t.get("sidecar"):
            continue
        write_draft(t["slug"], t["sidecar"], "build/sidecar_tasks.json")
        n += 1
    unfilled = [t["slug"] for t in d["tasks"] if not t.get("sidecar")]
    if unfilled:
        print(f"  {len(unfilled)} task(s) still unanswered: "
              f"{', '.join(unfilled[:4])}{' ...' if len(unfilled) > 4 else ''}")
    return n


def front_matter(path: str) -> dict | None:
    m = re.search(r"^---\n(.*?)^---\n", open(path).read(), re.S | re.M)
    if not m:
        return None
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return None


def validate_draft(path: str, note: bool = True) -> tuple[list[str], list[str]]:
    """Check one draft before promoting it. Returns (structural, quality).

    Both refuse promotion, and they are returned apart because they mean different
    things. A structural error means the file is broken and the site would render it
    wrong. A quality finding -- a band violation, a figure that is not in the paper --
    means the file is well-formed and says something the author would not want to have
    said. Accepting is the moment those become an assertion under their name, which is
    why the tier that `validate.py` reports and shrugs at is fatal here.
    """
    with open(path) as f:
        text = f.read()
    m = re.search(r"^---\n(.*?)^---\n", text, re.S | re.M)
    if not m:
        return [f"{path}: no YAML front matter"], []
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        return [f"{path}: unparseable front matter: {e}"], []
    errs = []
    try:
        import jsonschema
        jsonschema.validate(fm, schema())
    except ImportError:
        for k in ("one_liner", "claims"):
            if not fm.get(k):
                errs.append(f"{path}: missing required `{k}` (install jsonschema "
                            f"for the full check)")
    except jsonschema.ValidationError as e:
        # `json_path` because the message alone ("is not of type 'object'") does not say
        # which field, and the first thing the reader needs is where to look.
        errs.append(f"{path}: {e.json_path}: {e.message.splitlines()[0]}")
    except Exception as e:
        errs.append(f"{path}: {str(e).splitlines()[0]}")
    # isinstance on every element, because this reads a document the schema has only just
    # rejected: one draft came back with `claims` as a string, `c.get` raised on the first
    # character, and the exception escaped validate_draft and killed a 96-paper run 55
    # papers in. The wrong type is already the schema finding above; here it only has to
    # not crash.
    claims = fm.get("claims")
    ids = {c.get("id") for c in (claims if isinstance(claims, list) else [])
           if isinstance(c, dict)}
    groups = fm.get("qa")
    for qa in (groups if isinstance(groups, list) else []):
        if not isinstance(qa, dict):
            continue
        for a in answered_by(qa):
            if a not in ids:
                errs.append(f"{path}: qa answer `{a}` is not a claim id")

    from validate import (check_claim_evidence, check_claim_numbers, check_readability,
                          check_sidecar_shape)
    entry = [(os.path.basename(path), fm)]
    # Each check runs inside its own guard, and a check that cannot read the draft becomes
    # one finding instead of taking the tier down with it. Two failures got here the long
    # way round. First, a draft with `terminology` as a list made `readability` raise
    # AttributeError, and a check that crashes reports nothing at all. Then the fix for
    # that -- skip the quality tier whenever the schema rejected the document -- turned out
    # far worse than the crash: four drafts in a live run carried one schema error each and
    # nine or ten readability findings, reported one finding, were repaired against that
    # one, and got stamped `checks=1`. A tier that goes quiet is more dangerous than a tier
    # that dies, because the count it reports is believable.
    quality, no_text = [], False
    for run in (lambda: check_sidecar_shape(entry),
                lambda: check_readability(entry),
                lambda: check_claim_numbers(entry),
                lambda: check_claim_evidence(entry)):
        try:
            got = run()
        except Exception as e:                        # noqa: BLE001 -- a check, not the run
            quality.append(f"{path}: {getattr(run, '__name__', 'a check')} could not read "
                           f"this draft ({type(e).__name__}: {e}) -- fix the schema "
                           f"finding above and it will run")
            continue
        if isinstance(got, tuple):                    # (findings, papers with no text)
            quality += got[0]
            no_text = no_text or bool(got[1])
        else:
            quality += got
    if no_text and note:
        # Not a failure, and not silent either: the rule with no exceptions is the one
        # that must never quietly stop running.
        print(f"      note: no cached full text, so the figures in this draft were "
              f"not checked (python scripts/fulltext.py --slug {os.path.basename(path)[:-3]})")
    return errs, quality


def oneline(s) -> str:
    """A folded YAML scalar as one terminal line."""
    return re.sub(r"\s+", " ", str(s or "")).strip()



def quote(flat: str, figure: str) -> str:
    """A window of the paper's text around where a figure appears.

    Found by value and not by string, because the claim may legitimately have rounded: a
    claim's `74.5` has to point at the paper's `74.46`, and a window around the first
    bare `74` in the paper would show a sentence with nothing to do with the number.
    """
    from validate import canon, rounds_to
    for m in re.finditer(r"(?<![A-Za-z0-9.])(\d[\d,]*(?:\.\d+)?|\.\d+)", flat):
        tok = m.group(1)
        plain = tok.replace(",", "")
        forms = {canon(tok)} | ({canon("0" + plain)} if plain.startswith(".") else set())
        try:
            val = float("0" + plain if plain[0] == "." else plain)
        except ValueError:
            continue
        if figure not in forms and not rounds_to(figure, [val]):
            continue
        lo, hi = max(0, m.start() - 55), min(len(flat), m.end() + 55)
        return f"...{flat[lo:hi].strip()}..."
    return "(in the paper)"


def checked(slug: str) -> dict | str:
    """A draft with every claim already checked against the paper, or why it cannot be.

    The one review a human owes is asserting each line in public, and what makes that a
    minutes-long job rather than an hour is having the claim, its scope, the pointer it
    cites and the paper's own sentence for each figure in one place -- otherwise
    reviewing means holding the PDF open in another window, which is the friction that
    left 116 of 117 papers without a sidecar.

    Returns the checking, not a rendering of it, because there are two readers: a
    terminal (`show`) and a browser (`review_page`). Two renderers over one check is the
    only arrangement where the page and the command cannot disagree about a number.
    """
    path = os.path.join(DRAFTS, f"{slug}.md")
    if not os.path.exists(path):
        path = os.path.join(SIDECARS, f"{slug}.md")
    if not os.path.exists(path):
        return f"no draft and no live sidecar for {slug}"
    fm = front_matter(path)
    if fm is None:
        return f"{os.path.relpath(path, ROOT)}: unreadable front matter"

    from validate import (deline, evidence_pointers, figures, figures_in, readability,
                          rounds_to, values_in)
    # Bucketed by what each finding is about, so the renderers put it next to the
    # sentence rather than in a list at the bottom that reads as someone else's problem.
    prose = {}
    for kind, at, msg in readability(fm):
        prose.setdefault((kind, at), []).append(msg)
    cache = os.path.join(CACHE, f"{slug}.txt")
    text = deline(open(cache, errors="replace").read()) if os.path.exists(cache) else ""
    have, vals = (figures_in(text), values_in(text)) if text else (set(), [])
    flat = re.sub(r"\s+", " ", text)

    # Which questions retrieve each claim, joined this way round on purpose. A published
    # answer is a question followed by claim text and scope, so the reader's instinct is
    # to review it grouped by question -- but 212 of 318 claims across the live sidecars
    # and drafts answer more than one, so that page renders two thirds of them twice and
    # invites accepting a claim in one place while flagging the same words in another.
    # Claim-major with its questions attached shows the same pairing, once per claim.
    #
    # Only each question's first phrasing, which is the canonical one: the paraphrase set
    # is its own check and stays in the questions section, where the axes are comparable.
    asks: dict = {}
    for gi, g in enumerate(fm.get("qa") or []):
        first = (phrasings(g) or [None])[0]
        for a in answered_by(g):
            asks.setdefault(a, []).append((gi, oneline(first)))
    answered = set(asks)
    claims = []
    for c in fm.get("claims") or []:
        kind = c.get("kind") or "result"
        row = {"kind": kind, "id": c.get("id"),
               "evidence": c.get("evidence") or ("--" if kind == "context" else "MISSING"),
               "text": oneline(c.get("text")), "scope": oneline(c.get("scope")),
               "orphan": c.get("id") not in answered, "pointers": [], "figures": [],
               "asked": asks.get(c.get("id"), []),
               "prose": prose.get(("claim", str(c.get("id") or "?")), [])}
        if text:
            row["pointers"] = [(label, bool(pat.search(text)))
                               for label, pat in evidence_pointers(c.get("evidence") or "")]
            for n in figures(row["text"] + " " + row["scope"]):
                if n.isdigit() and 1900 <= int(n) <= 2099:
                    continue
                # The paper's own words around the figure, so the author checks the
                # number against the sentence it came from, not against a page number.
                row["figures"].append((n, quote(flat, n)
                                       if (n in have or rounds_to(n, vals)) else None))
        claims.append(row)

    # Left in the drafted order, which is the order the sidecar file has and therefore the
    # order the site publishes: both renderers walk the questions instead, so a sort here
    # would only reorder the orphan list while looking like it decided the page.
    return {"slug": slug, "path": os.path.relpath(path, ROOT), "has_text": bool(text),
            "live": path.startswith(SIDECARS), "one_liner": oneline(fm.get("one_liner")),
            "claims": claims, "qa": fm.get("qa") or [],
            "prose_q": {k[1]: v for k, v in prose.items() if k[0] == "question"},
            # Same bucketing for the fields below the claims, each keyed by the handle
            # the renderers already print: a misreading by its own text, a term by its
            # name. `prose_page` belongs to no field, so it is a bare list.
            "prose_m": {k[1]: v for k, v in prose.items() if k[0] == "misreading"},
            "prose_t": {k[1]: v for k, v in prose.items() if k[0] == "term"},
            "prose_page": [m for k, v in prose.items() if k[0] == "page" for m in v],
            "misreadings": fm.get("misreadings") or [],
            "terminology": fm.get("terminology") or {}}


def show(slug: str) -> None:
    """`checked` for a terminal."""
    d = checked(slug)
    if isinstance(d, str):
        return print(d)

    print(f"\n{d['path']}")
    print("one_liner: " + d["one_liner"])
    if not d["has_text"]:
        print("  (no cached full text -- figures and pointers cannot be checked here)")
    for m in d["prose_page"]:
        print(f"  WHOLE PAGE  {m}")

    def one_claim(c) -> None:
        orphan = "   (no question points here)" if c["orphan"] else ""
        print(f"\n    [{c['kind']}] {c['id']}   evidence: {c['evidence']}{orphan}")
        print("    " + c["text"])
        print("    Holds for: " + c["scope"])
        if also := [q for gi, q in c["asked"] if gi != c["asked"][0][0]]:
            for q in also:
                print(f"    also answers: {q}")
        for m in c["prose"]:
            print(f"    READS BADLY  {m}")
        for label, ok in c["pointers"]:
            print(f"    {'ok' if ok else 'NOT FOUND'}: the paper's own text "
                  f"mentions {label}")
        for n, sentence in c["figures"]:
            note = sentence or "NOT IN THE PAPER -- correct it or drop the figure"
            print(f"    {n:>9}  {note}")

    # Question, then the claim published as its answer -- same order as the review page,
    # and for the same reason: a claim read without the question it answers is read
    # without its subject. Each claim printed once, since two thirds of them answer more
    # than one question.
    by_id, drawn = {str(c["id"]): c for c in d["claims"]}, set()
    for i, g in enumerate(d["qa"]):
        qs = phrasings(g)
        print(f"\n  Q{i + 1}. {qs[0] if qs else '(no question text)'}"
              + (f"   (+{len(qs) - 1} more phrasing(s))" if len(qs) > 1 else ""))
        for m in (qs and d["prose_q"].get(str(qs[0])) or []):
            print(f"      UNANSWERABLE ALONE  {m}")
        if not answered_by(g):
            print("      nothing answers this -- point it at a claim or drop it")
        for a in answered_by(g):
            c = by_id.get(str(a))
            if c is None:
                print(f"      points at {a}, which is not a claim id")
            elif str(a) in drawn:
                print(f"      ^ {a} -- shown above, under its first question")
            else:
                drawn.add(str(a))
                one_claim(c)

    if orphans := [c for c in d["claims"] if str(c["id"]) not in drawn]:
        print(f"\n  NO QUESTION POINTS AT THESE ({len(orphans)})")
        for c in orphans:
            one_claim(c)

    for i, g in enumerate(d["qa"]):
        if len(phrasings(g)) > 1:
            print(f"\n  Q{i + 1} phrasings:")
            for role, q in qa_loci(g):
                label = role.split("/")[1] if role.startswith("ask/") else role
                print(f"      {label if label != 'unsorted' else '(unsorted)':13} {q}")
                for m in d["prose_q"].get(str(q)) or []:
                    print(f"        UNANSWERABLE ALONE  {m}")

    # Printed only when something is wrong with them: a correct misreading or definition
    # is already in the draft the author is reading beside this output.
    for mis, why in d["prose_m"].items():
        print(f"\n  misreading: {mis}")
        for m in why:
            print(f"      DANGLES  {m}")
    for term, why in d["prose_t"].items():
        print(f"\n  term: {term}")
        for m in why:
            print(f"      DANGLES  {m}")


REVIEW_PAGE = os.path.join(BUILD, "sidecar_review.html")

_CSS = """
:root { --bg:#fff; --fg:#1a1a1a; --dim:#5c5c5c; --line:#e3e3e3; --card:#fafafa;
        --bad:#a3122a; --badbg:#fdeef1; --ok:#1c6b3c; --warn:#8a5a00; --warnbg:#fdf6e7; }
/* Three states, not two: an explicit choice stamps data-theme on the root, and the
   default "system" setting stamps nothing. The media query is guarded so a chosen light
   theme beats a dark OS, and repeated under the stamp so a chosen dark theme beats a
   light one -- which matters wherever this page is viewed inside a host that themes it. */
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) { --dark: 1;
          --bg:#16181c; --fg:#e8e8e8; --dim:#a0a0a0; --line:#2e3238; --card:#1d2025;
          --bad:#ff8fa3; --badbg:#3a1520; --ok:#7ddaa0; --warn:#e8c07a; --warnbg:#3a2f14; } }
:root[data-theme="dark"] { --dark: 1;
        --bg:#16181c; --fg:#e8e8e8; --dim:#a0a0a0; --line:#2e3238; --card:#1d2025;
        --bad:#ff8fa3; --badbg:#3a1520; --ok:#7ddaa0; --warn:#e8c07a; --warnbg:#3a2f14; }
* { box-sizing:border-box }
body { background:var(--bg); color:var(--fg); margin:0 auto; padding:2rem 1.25rem 6rem;
       max-width:52rem; font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif }
h1 { font-size:1.5rem; margin:0 0 .25rem } h2 { font-size:1.2rem; margin:2.5rem 0 .25rem }
h3 { font-size:.95rem; margin:1.75rem 0 .5rem; color:var(--dim);
     text-transform:uppercase; letter-spacing:.06em }
a { color:inherit } code,kbd { font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace }
.sub { color:var(--dim); margin:0 0 2rem }
.paper { border-top:2px solid var(--fg); padding-top:1rem; margin-top:3rem }
.one { font-size:1.05rem; margin:.5rem 0 1rem }
.cmd { background:var(--card); border:1px solid var(--line); border-radius:6px;
       padding:.6rem .75rem; overflow-x:auto; white-space:pre }
.claim { background:var(--card); border:1px solid var(--line); border-left:3px solid var(--line);
         border-radius:6px; padding:.75rem .9rem; margin:.6rem 0 }
.claim.context { border-left-color:var(--dim) }
.claim.flagged { border-left-color:var(--bad) }
.id { color:var(--dim); font:12px/1.4 ui-monospace,Menlo,monospace }
.scope { color:var(--dim); font-size:.9rem; margin:.4rem 0 0 }
.checks { margin:.55rem 0 0; padding:0; list-style:none; font-size:.85rem }
.checks li { padding:.15rem 0 }
.checks a { text-decoration:underline; text-decoration-color:var(--dim);
            text-underline-offset:2px }
.n { display:inline-block; min-width:3.5rem; font:12px ui-monospace,Menlo,monospace;
     color:var(--fg) }
.bad { color:var(--bad); background:var(--badbg); padding:.1rem .3rem; border-radius:3px }
.ok { color:var(--ok) } .warn { color:var(--warn) } .dim { color:var(--dim) }
.ask { margin:2rem 0 .5rem; font-weight:600; font-size:1.02rem }
.ask:first-of-type { margin-top:1rem }
.again { margin:.6rem 0 .6rem 1rem; font-size:.9rem; color:var(--dim) }
.again a { color:var(--fg) }
.asked { color:var(--dim); font-size:.85rem; margin:.45rem 0 0 }
.q { margin:.5rem 0 1rem } .q li { color:var(--dim) }
.q b { color:var(--fg); font-weight:600 }
table { border-collapse:collapse; width:100%; font-size:.9rem }
td { border-top:1px solid var(--line); padding:.45rem .5rem; vertical-align:top }
td:first-child { white-space:nowrap; color:var(--fg); font-weight:600; width:11rem }
.note { background:var(--warnbg); border:1px solid var(--line); border-radius:6px;
        padding:.75rem .9rem; color:var(--fg); font-size:.9rem }
.toc { padding-left:1.2rem } .toc li { margin:.2rem 0 }
.sus { padding-left:1.2rem; margin:.35rem 0 .9rem; font-size:.9rem; color:var(--dim) }
.sus li { margin:.15rem 0 }
"""


def _flags(d: dict) -> list[str]:
    """Everything on one draft that a reader should not have to hunt for."""
    out = []
    figs = sum(1 for c in d["claims"] for n, s in c["figures"] if s is None)
    ptrs = sum(1 for c in d["claims"] for _, ok in c["pointers"] if not ok)
    orph = sum(1 for c in d["claims"] if c["orphan"])
    hard = sum(1 for c in d["claims"] if c["prose"])
    vague = len(d["prose_q"])
    loose = len(d["prose_m"]) + len(d["prose_t"])
    if hard:
        out.append(f"{hard} claim{'s' if hard > 1 else ''} to shorten or split")
    if vague:
        out.append(f"{vague} question{'s' if vague > 1 else ''} with nothing to point at")
    if loose:
        out.append(f"{loose} definition{'s' if loose > 1 else ''} or misreading"
                   f"{'s' if loose > 1 else ''} that dangle once extracted")
    out += d["prose_page"]
    if figs:
        out.append(f"{figs} figure{'s' if figs > 1 else ''} not in the paper")
    if ptrs:
        out.append(f"{ptrs} pointer{'s' if ptrs > 1 else ''} the paper does not mention")
    if orph:
        out.append(f"{orph} claim{'s' if orph > 1 else ''} no question points at")
    if not d["has_text"]:
        out.append("no cached full text, so nothing here was checked against the paper")
    return out


def at_sentence(links: dict, phrase: str) -> str:
    """The paper's own HTML, scrolled to the phrase — or "" if it cannot be linked.

    A text fragment rather than a section anchor, because the anchor ids of an arXiv or
    ar5iv rendition are generated and change between versions, while the sentence is the
    thing being checked. A fragment that fails to match costs nothing: the browser opens
    the paper at the top, which is where a "read the paper" link would have gone anyway.

    Only the review page links these. On a published page the same link, repeated once
    per claim, would add no retrievable fact to a passage that already carries the
    citation -- the paper is linked once, canonically, and that is the useful count.
    """
    url = links.get("html") or links.get("arxiv_pdf") or links.get("publisher")
    if not url or "/html/" not in url:
        return ""
    # The window a quote comes from is cut mid-word at both ends, so the first and last
    # tokens are dropped: a fragment matches on an exact substring, and half a word
    # never does.
    words = re.sub(r"\s+", " ", phrase.strip().strip(".")).split()
    if len(words) > 3:
        words = words[1:-1]
    if not words:
        return ""
    return url + "#:~:text=" + urllib.parse.quote(" ".join(words[:12]))


def review_page(papers: list[dict]) -> str:
    """Every fresh draft, checked, as one self-contained page to read in a browser.

    `--show` puts the same thing in a terminal, one slug at a time. This exists because
    reviewing is the only job on the worklist that is reading rather than pasting, and
    asking someone to run a command per paper to read prose is the wrong shape: the
    reading should be a link. Written to build/ and never to build/site/, because these
    are claims the author has not accepted and `--deploy` must not be able to reach them.
    """
    from html import escape as e

    by_slug = {p.get("slug"): p for p in papers}
    on_disk = sorted(os.path.basename(p)[:-3] for p in glob.glob(os.path.join(DRAFTS, "*.md")))
    keep = held(spec_sha())
    fresh = [s for s in on_disk if s in keep]
    stale = [s for s in on_disk if s not in keep]
    fresh.sort(key=lambda s: -((by_slug.get(s) or {}).get("citations") or 0))

    done = [d for d in (checked(s) for s in fresh) if isinstance(d, dict)]
    out = ["<!doctype html><meta charset=utf-8>",
           "<meta name=viewport content='width=device-width,initial-scale=1'>",
           f"<title>Sidecar drafts to review ({len(done)})</title>", f"<style>{_CSS}</style>",
           f"<h1>{len(done)} sidecar draft{'s' if len(done) != 1 else ''} to review</h1>"]

    if not done:
        out.append("<p class=sub>Nothing is waiting. Queue more with "
                   "<code>python scripts/draft_sidecars.py --limit 20</code>.</p>")
    else:
        out += ["<p class=sub>Generated by the last run — reading this is the whole "
                "review. Each figure is shown beside the paper's own sentence, so the "
                "check is comparing two lines, not opening a PDF. Accepting is the one "
                "act that publishes an assertion under your name.</p>",
                "<h3>On this page</h3><ol class=toc>"]
        for d in done:
            p = by_slug.get(d["slug"]) or {}
            bad = _flags(d)
            out.append(f"<li><a href='#{e(d['slug'])}'>"
                       f"{e((p.get('title_display') or p.get('title') or d['slug'])[:70])}"
                       f"</a> — {p.get('citations') or 0} cites"
                       + (f" · <span class=bad>{e('; '.join(bad))}</span>" if bad else "")
                       + "</li>")
        out.append("</ol>")

    for d in done:
        p = by_slug.get(d["slug"]) or {}
        slug = d["slug"]
        out += [f"<div class=paper id='{e(slug)}'>",
                f"<h2>{e(p.get('title_display') or p.get('title') or slug)}</h2>",
                f"<p class=sub>{p.get('citations') or 0} cites · "
                f"<code>{e(d['path'])}</code></p>"]
        if bad := _flags(d):
            out.append("<p class=note><b>Before accepting:</b> "
                       + e("; ".join(bad)) + ".</p>")
        # Nothing here refuses the draft, which is exactly why it belongs on the page: the
        # checks have finished and a reader is about to put their name on prose no rule can
        # judge. `--suspect` ranks the same signals across drafts; here they name the claim.
        score, look = suspicion(d["path"])
        if score:
            out += ["<p class=note><b>Worth a second look:</b></p><ul class=sus>"]
            out += [f"<li>{e(line)}</li>" for line in look]
            out.append("</ul>")
        out.append(f"<p class=one>{e(d['one_liner'])}</p>")
        out.append("<div class=cmd>python scripts/draft_sidecars.py --accept "
                   + e(slug) + (" --replace" if has_live_sidecar(slug) else "") + "</div>")

        # One question, then the claims published as its answer, then the next question.
        # Each claim is rendered once: a claim answering three questions used to print its
        # three question lines above itself, and with two thirds of claims shared that
        # made a page of near-identical blocks differing by one line -- and the same
        # question reappeared above claims far apart, since sorting by a claim's *first*
        # question cannot group its second. Under a later question a claim already shown
        # is a one-line link to it, which is the fact the reader needs there (this answer
        # is also carrying that question) at the size that fact deserves.
        def claim_html(c) -> list[str]:
            bad_here = (any(sn is None for _, sn in c["figures"])
                        or any(not ok for _, ok in c["pointers"]) or c["prose"])
            cls = "claim" + (" context" if c["kind"] == "context" else "") \
                          + (" flagged" if bad_here else "")
            also = [f"<a href='#{e(slug)}-q{gi}'>{e(q)}</a>"
                    for gi, q in c["asked"] if gi != c["asked"][0][0]]
            block = [f"<div class='{cls}' id='{e(slug)}-{e(str(c['id']))}'>",
                     f"<div class=id>[{c['kind']}] {e(str(c['id']))} · cites "
                     f"{e(str(c['evidence']))}"
                     + ("  · no question points here" if c["orphan"] else "") + "</div>",
                     f"<div>{e(c['text'])}</div>",
                     f"<p class=scope><b>Holds for.</b> {e(c['scope'])}</p>"]
            if also:
                block.append("<p class=asked>also answers: " + " · ".join(also) + "</p>")
            if c["prose"]:
                block.append("<ul class=checks>")
                block += [f"<li><span class=bad>reads badly</span> "
                          f"<span class=dim>{e(m)}</span></li>" for m in c["prose"]]
                block.append("</ul>")
            if c["pointers"] or c["figures"]:
                block.append("<ul class=checks>")
                links = p.get("links") or {}
                for label, ok in c["pointers"]:
                    href = at_sentence(links, label) if ok else ""
                    shown = f"<a href='{e(href)}'>{e(label)}</a>" if href else e(label)
                    block.append(f"<li><span class={'ok' if ok else 'bad'}>"
                                 f"{'the paper mentions' if ok else 'THE PAPER NEVER MENTIONS'}"
                                 f"</span> {shown}</li>")
                for n, sentence in c["figures"]:
                    if sentence is None:
                        block.append(f"<li><span class=n>{e(n)}</span> "
                                     f"<span class=bad>not in the paper — correct it or "
                                     f"drop the figure</span></li>")
                    else:
                        # The quote itself is the link, so checking a figure against the
                        # paper's sentence and then against the paper costs one click
                        # rather than a search in another window.
                        href = at_sentence(links, sentence)
                        body = f"<span class=dim>{e(sentence)}</span>"
                        block.append(f"<li><span class=n>{e(n)}</span> "
                                     + (f"<a href='{e(href)}'>{body}</a>" if href else body)
                                     + "</li>")
                block.append("</ul>")
            block.append("</div>")
            return block

        by_id = {str(c["id"]): c for c in d["claims"]}
        out += [f"<h3>Answers ({len(d['qa'])} questions, {len(d['claims'])} claims)</h3>",
                "<p class=sub>One question, then the claim published as its answer — the "
                "shape a reader meets it in. Two things to check per claim, and they fail "
                "differently: the <b>text</b> must be true and carry its own subject, "
                "since it is quoted with no title beside it; and <b>Holds for</b> must "
                "name the condition that would make it false if changed — the models, the "
                "languages, the sizes, the year. A scope that is a hedge "
                "(\u201cfurther work is needed\u201d), a restatement of the claim, or a "
                "judgement about the claim\u2019s reliability is the one to rewrite.</p>"]
        drawn: set = set()
        for gi, g in enumerate(d["qa"]):
            qs = phrasings(g)
            extra = (f" <span class=dim>+{len(qs) - 1} phrasing"
                     f"{'s' if len(qs) > 2 else ''}</span>") if len(qs) > 1 else ""
            why = "".join(f"<br><span class=bad>unanswerable alone</span> "
                          f"<span class=dim>{e(m)}</span>"
                          for m in (d["prose_q"].get(str(qs[0])) or []) if qs)
            head = e(qs[0]) if qs else "(no question text)"
            out.append(f"<p class=ask id='{e(slug)}-q{gi}'>{head}{extra}{why}</p>")
            answers = answered_by(g)
            if not answers:
                out.append("<p class=note>Nothing answers this — either point it at a "
                           "claim or drop the question.</p>")
            for a in answers:
                c = by_id.get(str(a))
                if c is None:
                    out.append(f"<p class=note>points at <code>{e(str(a))}</code>, "
                               "which is not a claim id.</p>")
                elif str(a) in drawn:
                    out.append(f"<p class=again>↑ <a href='#{e(slug)}-{e(str(a))}'>"
                               f"{e(oneline(c['text'])[:90])}…</a> "
                               f"<span class=dim>shown above, under its first question"
                               f"</span></p>")
                else:
                    drawn.add(str(a))
                    out += claim_html(c)

        if orphans := [c for c in d["claims"] if str(c["id"]) not in drawn]:
            out += [f"<h3>No question points at these ({len(orphans)})</h3>",
                    "<p class=sub>Published in the claim list and reachable by nothing a "
                    "visitor would type. Give each one a question, fold it into a claim "
                    "that has one, or drop it.</p>"]
            for c in orphans:
                out += claim_html(c)

        if d["qa"]:
            out += ["<h3>The four routes to each question</h3>",
                    "<p class=sub>The answers are above. What is left to read here is "
                    "whether each labelled route is really a different route — "
                    "<b>plain</b> in the words of someone who has not read the paper, "
                    "<b>jargon</b> in the field\u2019s own vocabulary, <b>task</b> as the "
                    "thing they are trying to do, <b>practitioner</b> in the first person "
                    "and deciding. Three rewordings of one sentence match one query; "
                    "three vocabularies match three. Anything marked "
                    "<b>unsorted</b> predates the routes and is what a redraft "
                    "replaces.</p>"]
            for gi, g in enumerate(d["qa"]):
                out.append("<ul class=q>")
                for i, (role, q) in enumerate(qa_loci(g)):
                    why = d["prose_q"].get(str(q)) or []
                    label = role.split("/")[1] if role.startswith("ask/") else role
                    out.append(f"<li><span class=dim>{e(label)}</span> "
                               f"{'<b>' if not i else ''}{e(q)}"
                               f"{'</b>' if not i else ''}"
                               + "".join(f"<br><span class=bad>unanswerable alone</span> "
                                         f"<span class=dim>{e(m)}</span>" for m in why)
                               + "</li>")
                out.append("</ul>")

        # Both blocks below are published as standalone fragments -- a misreading as its
        # own list item, a term as a `DefinedTerm` with nothing beside it -- so the note
        # goes inline, under the words that dangle.
        if d["misreadings"]:
            out.append(f"<h3>Misreadings it heads off ({len(d['misreadings'])})</h3><ul>")
            for m in d["misreadings"]:
                why = d["prose_m"].get(str(m)) or []
                out.append(f"<li>{e(oneline(m))}"
                           + "".join(f"<br><span class=bad>dangles alone</span> "
                                     f"<span class=dim>{e(w)}</span>" for w in why)
                           + "</li>")
            out.append("</ul>")

        if d["terminology"]:
            out.append(f"<h3>Terminology ({len(d['terminology'])})</h3><table>")
            for k, v in d["terminology"].items():
                why = d["prose_t"].get(str(k)) or []
                out.append(f"<tr><td>{e(str(k))}</td><td>{e(oneline(v))}"
                           + "".join(f"<br><span class=bad>dangles alone</span> "
                                     f"<span class=dim>{e(w)}</span>" for w in why)
                           + "</td></tr>")
            out.append("</table>")
        out.append("</div>")

    # The published ones, for the other reason to open this page: not "what must I
    # check" but "what does an accepted sidecar actually look like". They are already
    # rendered into the site, so link the built page rather than restating it here.
    live = sorted(os.path.basename(f)[:-3] for f in glob.glob(os.path.join(SIDECARS, "*.md")))
    if live:
        out += [f"<h2>{len(live)} already published</h2>",
                "<p class=sub>Accepted, and rendered into the site — this is what a paper "
                "page looks like once it has a sidecar, which is the comparison worth "
                "making against a page that has none.</p><ul>"]
        for s in live:
            p = by_slug.get(s) or {}
            built = os.path.join(BUILD, "site", "papers", s, "index.html")
            title = e((p.get("title_display") or p.get("title") or s)[:70])
            if os.path.exists(built):
                out.append(f"<li><a href='file://{e(built)}'>{title}</a> · "
                           f"<a href='file://{e(os.path.dirname(built))}/llms.txt'>llms.txt"
                           f"</a></li>")
            else:
                out.append(f"<li>{title} <span class=dim>— not built yet; "
                           f"run <code>python update.py --step render</code></span></li>")
        out.append("</ul>")

    if stale:
        out += [f"<h2>{len(stale)} stale draft{'s' if len(stale) > 1 else ''} — do not "
                f"read</h2>",
                "<p class=sub>Written against sidecar rules that have since changed. "
                "<code>--accept</code> refuses them and the next drafting run replaces "
                "them, so reading one is wasted effort.</p><ul>"]
        out += [f"<li class=id>{e(s)}</li>" for s in stale]
        out.append("</ul>")

    return "\n".join(out) + "\n"


def write_review_page(papers: list[dict]) -> str:
    # Build first, write second. `open(..., "w")` truncates on the way in, so building the
    # page inside the `with` meant one draft that made a check raise left a zero-byte
    # review page behind -- the previous good page destroyed by the run that failed to
    # replace it.
    html = review_page(papers)
    os.makedirs(BUILD, exist_ok=True)
    with open(REVIEW_PAGE, "w") as fh:
        fh.write(html)
    return REVIEW_PAGE


def accept(slugs: list[str], replace: bool = False, anyway: bool = False) -> int:
    """Promote drafts into data/sidecars/, refusing anything that fails a check.

    An existing live sidecar is never overwritten without `--replace`, because a
    redraft of a paper that already has one is the one case where accepting blind
    destroys reviewed work: the live file is what the site, the validator and the
    fidelity check read, and its wording may be the author's rather than a model's.
    `--replace` is the opt-in, and it prints the git command that shows what changed.
    """
    n = 0
    for slug in slugs:
        src = os.path.join(DRAFTS, f"{slug}.md")
        if not os.path.exists(src):
            print(f"  no draft for {slug}")
            continue
        errs, quality = validate_draft(src)
        if quality and not anyway:
            errs += quality + [
                "the above are quality findings, not broken structure. Fix them, or "
                f"promote as-is with `--accept {slug} --anyway`"]
        elif quality:
            print(f"  {slug}: promoted with {len(quality)} known problem(s):")
            for q in quality:
                print(f"      ignored: {q}")
        if errs:
            print(f"  {slug}: NOT promoted --")
            for e in errs:
                print(f"      {e}")
            continue
        dst = os.path.join(SIDECARS, f"{slug}.md")
        if os.path.exists(dst) and not replace:
            print(f"  {slug}: a live sidecar already exists; not overwriting.\n"
                  f"      This draft is a *replacement*. Compare them first:\n"
                  f"        diff data/sidecars/{slug}.md {os.path.relpath(src, ROOT)}\n"
                  f"      then, if the replacement is the one you want:\n"
                  f"        python scripts/draft_sidecars.py --accept {slug} --replace")
            continue
        if os.path.exists(dst):
            print(f"  {slug}: replacing the live sidecar "
                  f"(recover the old one with `git diff data/sidecars/{slug}.md`)")
        # Strip the DRAFT banner on the way out. It is addressed to the reviewer, and a
        # promoted sidecar has been reviewed -- leaving it in would make every published
        # sidecar claim to be unverified.
        with open(src) as f:
            text = f.read()
        text = re.sub(r"^<!-- DRAFT.*?-->\n+", "", text, flags=re.S)
        with open(dst, "w") as f:
            f.write(text)
        os.remove(src)
        print(f"  promoted {slug} -> data/sidecars/{slug}.md")
        n += 1
    return n


# A claim can only say these if the paper earned them: each asserts standing relative to
# other work or a proof, neither of which any table can settle, and a model reaches for them
# when it is summarising an abstract's ambition instead of a result.
#
# Deliberately narrow, after reading what a wider list caught. `always`, `never`, `any` and
# `guarantee` were in it and every hit was ordinary English -- "essentially the 0.54 of always
# picking the first candidate" describes a majority baseline, and a claim that calls a proved
# theorem a guarantee is paraphrasing correctly. Words like those turn the ranking into a
# list of every page, which is the same as no ranking.
LOUD = re.compile(r"\b(first|best|state[- ]of[- ]the[- ]art|sota|novel|prove[nsd]?"
                  r"|optimal|universal|unprecedented)\b", re.I)

# Words long enough that finding them in the paper means something. Four letters and under
# are function words and shared vocabulary, and counting them puts every claim near 100%.
_LONG = re.compile(r"[a-z][a-z0-9-]{4,}")

# Matched on a prefix, not whole: "saturated" against a paper that says "saturates" is the
# same word, and whole-word matching charged 1,428 claims for English morphology. Measured
# over all of them, the prefix lifts the median claim from 0.87 to 0.91 and the bottom decile
# from 0.71 to 0.78 -- the floor below is that decile, so this ranks the tail rather than a
# quarter of every page.
_STEM = 6
GROUNDED = 0.78


def grounded(text: str, low: str) -> float:
    """The share of a claim's longer words that occur in the paper's own text.

    A blunt instrument on purpose. It cannot tell a legitimate paraphrase from an invention,
    and it is not a check for that reason -- no draft is refused over it. What it does do is
    rank, and ranking is the whole job here: a reviewer with an evening has to spend it on
    the drafts most likely to be wrong, and a claim written in words the paper never uses is
    the cheapest available signal of one.
    """
    words = set(_LONG.findall(text.lower()))
    hit = [w for w in words if (w[:_STEM] if len(w) > _STEM else w) in low]
    return len(hit) / len(words) if words else 1.0


def suspicion(path: str) -> tuple[int, list[str]]:
    """(score, reasons) -- how likely a passing draft is to say something the paper does not.

    The checks answer "is this well-formed and are its numbers in the paper". Nothing answers
    "is this true", and nothing code-only can. So this ranks instead of judging, and every
    reason it gives names the field to read and what to read it against.
    """
    from validate import deline, figures, figures_in, rounds_to, values_in
    fm = front_matter(path) or {}
    slug = os.path.basename(path)[:-3]
    cached = os.path.join(CACHE, f"{slug}.txt")
    score, why = 0, []
    if not os.path.exists(cached):
        # The strongest signal available, and the one a reader would never guess: the figure
        # rule is the one rule with no exceptions, and here it did not run at all.
        return 4, ["no cached paper text, so not one figure in this draft was checked "
                   f"(python scripts/fulltext.py --slug {slug})"]
    with open(cached, errors="replace") as fh:
        text = deline(fh.read())
    low, have, vals = text.lower(), figures_in(text), values_in(text)
    loud, round_only, thin = [], [], []
    for c in (fm.get("claims") or []):
        if not isinstance(c, dict):
            continue
        cid, body = c.get("id"), str(c.get("text") or "")
        for word in sorted({m.group(0).lower() for m in LOUD.finditer(body)}):
            if word not in low:
                loud.append(f"claim '{cid}' says '{word}' and the paper's text never does")
        for n in figures(body):
            if n not in have and rounds_to(n, vals):
                round_only.append(f"claim '{cid}': the paper does not state {n}, only a "
                                  f"value that rounds to it")
        share = grounded(body, low)
        if share < GROUNDED:
            thin.append((share, f"claim '{cid}': {share:.0%} of its words appear in the "
                                f"paper -- read it against the paper's own sentence"))
    # Capped per family, and ordered by what a reader can act on. Uncapped, a long page of
    # thinly-worded claims outranks a short page that says the paper proved something it
    # never claims -- and the second is the one that must not go out under a name. The
    # families are also weighted apart for the same reason: an unearned "first" is a
    # sentence to delete, a low word overlap is a sentence to read.
    thin = [line for _, line in sorted(thin)]
    for weight, cap, lines in ((2, 2, loud), (1, 2, round_only), (1, 3, thin)):
        score += weight * min(cap, len(lines))
        why += lines[:cap] if len(lines) <= cap else \
            lines[:cap] + [f"... and {len(lines) - cap} more like the last one"]
    head = open(path, encoding="utf-8").read()[:2000]
    if "targeted repair" in head:
        score += 1
        why.append("some fields here are a machine's second wording, spliced in to clear a "
                   "check and not read since")
    return score, why


def suspects(papers: list[dict], top: int) -> None:
    """The drafts worth an evening, worst first. Only ones a reader can actually accept."""
    spec = spec_sha()
    keep = held(spec)
    ranked = []
    for f in sorted(glob.glob(os.path.join(DRAFTS, "*.md"))):
        slug = os.path.basename(f)[:-3]
        if slug not in keep or any(validate_draft(f, note=False)):
            continue
        score, why = suspicion(f)
        if score:
            ranked.append((score, slug, why))
    ranked.sort(key=lambda r: (-r[0], r[1]))
    cites = {p["slug"]: p.get("citations") or 0 for p in papers}
    print(f"{len(ranked)} of the drafts that pass every check still have something a "
          f"reader would want to see, worst first:\n")
    for score, slug, why in ranked[:top]:
        print(f"  {score:>3}  {slug}  ({cites.get(slug, 0)} cites)")
        for line in why:
            print(f"       - {line}")
        print()
    if len(ranked) > top:
        print(f"  ... {len(ranked) - top} more, --suspect 0 for all of them")
    print(f"  file://{os.path.join(BUILD, 'sidecar_review.html')}")


def review(papers: list[dict]) -> None:
    live = {os.path.basename(f)[:-3] for f in glob.glob(os.path.join(SIDECARS, "*.md"))}
    drafted = sorted(glob.glob(os.path.join(DRAFTS, "*.md")))
    by_slug = {p["slug"]: p for p in papers}
    spec = spec_sha()
    # `keep` before the counts: a stale draft is not work for the reader, so counting it
    # under "awaiting you" asks for an evening that ends in an accept that refuses.
    keep = held(spec)
    obsolete = [os.path.basename(f)[:-3] for f in drafted
                if os.path.basename(f)[:-3] not in keep]
    stale_note = f"   ({len(obsolete)} stale, see below)" if obsolete else ""
    print(f"live sidecars        {len(live)}")
    print(f"drafts awaiting you  {len(drafted) - len(obsolete)}{stale_note}")
    # Subtracting the draft count printed -2, because the two re-drafts of live sidecars
    # are counted in both sets. Count the papers with neither instead.
    have = live | {os.path.basename(f)[:-3] for f in drafted}
    print(f"no sidecar, no draft "
          f"{len([p for p in papers if p['slug'] not in have])}")
    if obsolete:
        print(f"\n{len(obsolete)} draft(s) written against rules that have since changed. "
              f"Do not read these;\nthe next run replaces them:\n  "
              + ", ".join(obsolete[:6]) + (" ..." if len(obsolete) > 6 else ""))
        print("  python scripts/draft_sidecars.py --limit 0")
    stuck = {s: w for s, w in keep.items() if w != "current"}
    for s, w in stuck.items():
        print(f"\n{s}: {w}. Nothing will overwrite your edits. Either accept what you\n"
              f"  have with --anyway, or re-draft it yourself with --slug {s}.")
    # Only the ones it is worth spending an evening on. Listing a stale draft here under
    # "read, edit, then --accept" would contradict the paragraph above it.
    yours = [f for f in drafted if os.path.basename(f)[:-3] in keep]
    if yours:
        print(f"\nRead all {len(yours)} in a browser, already checked against each paper:"
              f"\n  file://{write_review_page(papers)}")
        print("\nDrafts, most cited first — read, edit, then --accept:")
        counts = collections.Counter()
        rows = sorted(yours, key=lambda f: -(
            (by_slug.get(os.path.basename(f)[:-3]) or {}).get("citations") or 0))
        for f in rows:
            slug = os.path.basename(f)[:-3]
            p = by_slug.get(slug) or {}
            errs, quality = validate_draft(f)
            flag = "  [schema errors]" if errs else ""
            if quality:
                flag += f"  [{len(quality)} to fix -- see --show {slug}]"
            # Say so here rather than at --accept time: a redraft of a paper that
            # already has a reviewed sidecar is read differently from a first draft,
            # and the difference should be visible while deciding what to read.
            if slug in live:
                flag += "  [REPLACES the live sidecar -- needs --replace]"
            print(f"  {(p.get('citations') or 0):>5} cites  {slug}{flag}")
            for e in errs + quality:
                counts[rule_of(e)] += 1
        if counts:
            # Per-paper counts say which evening to spend; this says which rule the
            # drafting keeps losing, which is the only one of the two that can be acted
            # on in the rules block every draft is written against. Derived on the way
            # past, printed, never stored -- it is a fact about this run.
            print("\nRules the open findings hit, most often first:")
            for rule, n in counts.most_common(6):
                print(f"  {n:>4}  {rule}")
            print("  A rule near the top of that list is a rules-block problem, not a "
                  "per-paper one:\n  docs/SIDECAR.md \u00a72 is what every draft was "
                  "written against.")


def rule_of(finding: str) -> str:
    """Collapse a finding down to the rule it broke, so findings can be counted.

    A finding names its locus and its magnitude -- claim id, character counts, the
    offending phrase -- and all three are what make two instances of one rule look like
    two rules. Dropping them is what turns 86 findings into the six rules behind them.
    """
    msg = re.sub(r"^.*?\.md: ", "", finding)            # the draft's path
    msg = re.sub(r"^(claim|term|misreading|qa\[\d+\]|page|\$\.[\w.\[\]]+)"
                 r"(?: '[^']*'| \d+)?: ", "", msg)      # the locus inside it
    msg = re.split(r" -- ", msg)[0]                     # the fix, which names the instance
    msg = re.sub(r"'[^']*'", "'...'", msg)              # claim ids, quoted phrases
    return re.sub(r"\b\d+(?:\.\d+)?%?\b", "N", msg)[:72]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ingest", action="store_true",
                    help="fold build/sidecar_tasks.json answers into drafts/")
    ap.add_argument("--review", action="store_true", help="what is drafted vs live")
    ap.add_argument("--restamp", nargs="*", metavar="SLUG",
                    help="re-check drafts in place and rewrite their stamps: what to run "
                         "after editing a check, so a rule change does not cost the "
                         "reviewing already done. Refuses any draft that now fails. "
                         "No slugs means every draft")
    ap.add_argument("--show", nargs="+", metavar="SLUG",
                    help="print each claim beside the evidence it cites, and the "
                         "paper's own sentence for every figure it states")
    ap.add_argument("--suspect", nargs="?", const=10, type=int, metavar="N",
                    help="rank the drafts that pass every check by how likely they are to "
                         "say something the paper does not, worst first, with the field to "
                         "read and what to read it against. 0 means all of them")
    ap.add_argument("--page", action="store_true",
                    help="write build/sidecar_review.html -- every draft, checked, as "
                         "one page to read in a browser instead of one --show per paper")
    ap.add_argument("--accept", nargs="+", metavar="SLUG", help="promote these drafts")
    ap.add_argument("--accept-all", action="store_true", help="promote every draft")
    ap.add_argument("--anyway", action="store_true",
                    help="with --accept: promote despite band or figure findings, "
                         "listing what was ignored")
    # Deliberately not honoured by --accept-all: replacing a reviewed sidecar is a
    # per-paper decision, and a flag that quietly applies it to every draft in the
    # directory is how one keystroke overwrites work nobody asked to revisit.
    ap.add_argument("--replace", action="store_true",
                    help="with --accept: overwrite a live sidecar with the redraft")
    ap.add_argument("--limit", type=int, default=20,
                    help="how many papers to queue (default 20, 0 = all)")
    ap.add_argument("--all", action="store_true",
                    help="re-queue papers that already have a draft")
    ap.add_argument("--no-fulltext", action="store_true",
                    help="abstract only; no paper fetches")
    ap.add_argument("--slug", nargs="+", help="queue exactly these papers")
    ap.add_argument("--mode", choices=("skill", "api", "openai"),
                    help="override llm.mode for this run, without editing config.yaml")
    # Per-run rather than per-repo: the committed default is what a fork inherits, and
    # `medium` is the right one to inherit, but a corpus-wide pass whose drafts will be
    # published under the author's name is worth more thinking than a single spot-check.
    ap.add_argument("--effort", choices=("low", "medium", "high"),
                    help="override llm.effort for this run (api mode)")
    ap.add_argument("--mend", nargs="*", metavar="SLUG",
                    help="fix existing drafts one field at a time: send the model only the "
                         "claims and phrasings the checker complained about, splice its "
                         "rewrites back, and keep them only if the count dropped. No slugs "
                         "means every draft that still carries a finding. api and openai "
                         "modes")
    ap.add_argument("--reroute", nargs="*", metavar="SLUG",
                    help="rewrite live sidecars' question groups as the named `ask` roles "
                         "and nothing else: the model is shown the claims and what each "
                         "group already asks, never the paper, so no claim can move. No "
                         "slugs means every sidecar still holding phrasings in "
                         "`ask.unsorted`. api and openai modes")
    ap.add_argument("--repair", type=int, default=0, metavar="N",
                    help="after drafting, show the model its own findings and ask it to "
                         "fix them, up to N times. Stops early when a round stops "
                         "reducing the count. api and openai modes")
    args = ap.parse_args()

    cfg = load_config()
    papers = (read_yaml(os.path.join(DATA, "papers.yaml")) or {}).get("papers", [])

    if args.page:
        print(f"file://{write_review_page(papers)}")
        return
    if args.restamp is not None:
        done, refused = restamp(args.restamp or None)
        print(f"re-stamped {len(done)} draft(s) against the current spec"
              + (f": {', '.join(done)}" if done else ""))
        for slug, why in refused:
            print(f"  left stale: {slug} -- {why}")
        return
    if args.review:
        return review(papers)
    if args.suspect is not None:
        return suspects(papers, args.suspect or 10 ** 6)
    if args.show:
        for slug in args.show:
            show(slug)
        return
    # A refusal exits non-zero. Promotion is the step a wrapper or a later command is
    # entitled to depend on, and a refused accept that exits 0 reads as a successful one.
    if args.accept_all:
        slugs = [os.path.basename(f)[:-3]
                 for f in glob.glob(os.path.join(DRAFTS, "*.md"))]
        print(f"promoting {len(slugs)} draft(s):")
        n = accept(slugs, anyway=args.anyway)
        print(f"\n{n} promoted.")
        sys.exit(0 if n == len(slugs) else 1)
    if args.accept:
        n = accept(args.accept, replace=args.replace, anyway=args.anyway)
        print(f"\n{n} promoted.")
        sys.exit(0 if n == len(args.accept) else 1)
    if args.ingest:
        n = ingest(papers)
        print(f"wrote {n} draft(s) to data/sidecars/drafts/")
        # Regenerated here rather than left for the next full run: a draft that exists
        # and a review page that does not know about it is the one state where reading
        # the page would silently miss work.
        print(f"Read them: file://{write_review_page(papers)}")
        return

    if args.reroute is not None:
        mode = args.mode or cfg["llm"]["mode"]
        if mode not in ("api", "openai"):
            sys.exit("--reroute needs a model it can call: --mode api or --mode openai")
        if args.effort:
            cfg["llm"]["effort"] = args.effort
        legacy = []
        for f in sorted(glob.glob(os.path.join(SIDECARS, "*.md"))):
            fm = front_matter(f) or {}
            if any(isinstance(g.get("ask"), dict) and g["ask"].get("unsorted")
                   for g in (fm.get("qa") or [])):
                legacy.append(os.path.basename(f)[:-3])
        want = args.reroute or legacy
        unknown = [s for s in want if s not in legacy]
        if unknown:
            print(f"nothing to reroute in: {', '.join(unknown)}", file=sys.stderr)
        todo = [s for s in want if s in legacy]
        if not todo:
            print("Nothing to reroute: no sidecar still holds phrasings in `ask.unsorted`.")
            return
        caller = call_api if mode == "api" else call_openai
        # No paper text is fetched at all -- see `reroute`. Over 113 papers that is the
        # difference between a pass that takes minutes and one that re-resolves every PDF.
        _, how, asker = caller([], cfg)
        print(f"rerouting {len(todo)} sidecar(s) with {how}")
        moved = clean = 0
        for slug in todo:
            done, found = reroute(slug, asker, how)
            if not done:
                print(f"  --  {slug[:56]:56} nothing usable came back")
                continue
            moved += done
            clean += not found
            print(f"  {'ok ' if not found else '   '} {slug[:56]:56} {done} group(s)"
                  + (f", {found} finding(s) to fix" if found else ""))
        print(f"\n{moved} group(s) rerouted; {clean} of {len(todo)} draft(s) clean")
        print(f"Read them: file://{write_review_page(papers)}")
        return

    if args.mend is not None:
        mode = args.mode or cfg["llm"]["mode"]
        if mode not in ("api", "openai"):
            sys.exit("--mend needs a model it can call: --mode api or --mode openai")
        if args.effort:
            cfg["llm"]["effort"] = args.effort
        drafts = [os.path.basename(f)[:-3]
                  for f in sorted(glob.glob(os.path.join(DRAFTS, "*.md")))]
        want = args.mend or drafts
        unknown = [s for s in want if s not in drafts]
        if unknown:
            print(f"no draft for: {', '.join(unknown)}", file=sys.stderr)
        # Checked before any paper is fetched: a clean draft needs neither its text nor a
        # call, and over a whole corpus that is most of them.
        todo = [s for s in want if s in drafts
                and sum(len(x) for x in
                        validate_draft(os.path.join(DRAFTS, f"{s}.md"), note=False))]
        if not todo:
            print("Nothing to mend: every draft asked for is clean.")
            return
        by_slug = {p["slug"]: p for p in papers}
        print(f"mending {len(todo)} draft(s); resolving each paper's text first...")
        pairs, _ = with_evidence([by_slug[s] for s in todo if s in by_slug],
                                 cfg, args.no_fulltext, None)
        ev = {p["slug"]: e for p, e in pairs}
        caller = call_api if mode == "api" else call_openai
        # An empty batch: this is how a backend is asked for its request function without
        # drafting anything, and the provenance it returns names the rung it settled on.
        _, how, asker = caller([], cfg)
        before = after = 0
        for slug in todo:
            print(f"  {slug}")
            errs, qual = validate_draft(os.path.join(DRAFTS, f"{slug}.md"), note=False)
            before += len(errs) + len(qual)
            after += mend(slug, asker, ev.get(slug, ""), how)
        print(f"\n{before} finding(s) -> {after} across {len(todo)} draft(s)")
        print(f"Read them: file://{write_review_page(papers)}")
        return

    # An explicit --slug is an instruction, not a candidate list: no limit and no
    # text-availability skip, because "draft this one anyway" is a legitimate thing to
    # ask for a paper whose text you know is unreachable.
    if args.slug:
        by_slug = {p["slug"]: p for p in papers}
        cands, limit = [by_slug[s] for s in args.slug if s in by_slug], None
        missing = [s for s in args.slug if s not in by_slug]
        if missing:
            print(f"unknown slug(s): {', '.join(missing)}", file=sys.stderr)
    else:
        cands, limit = pending(papers, args.all, None), args.limit or None
    if not cands:
        print("Nothing to draft: every paper has a sidecar or a draft.")
        print("  python scripts/draft_sidecars.py --review")
        return

    print(f"resolving each paper's full text, most cited first "
          f"(up to {limit or len(cands)})...")
    pairs, skipped = with_evidence(cands, cfg, args.no_fulltext,
                                   None if args.slug else limit)
    if skipped:
        print(f"\nskipped {len(skipped)} with no text from any open source -- drop a PDF "
              f"in data/fulltext/<slug>.pdf and rerun, or force one with --slug:")
        for p in skipped[:8]:
            print(f"  {(p.get('citations') or 0):>5} cites  {p['slug']}")
        if len(skipped) > 8:
            print(f"  ... and {len(skipped) - 8} more (python scripts/fulltext.py --report)")
    if not pairs:
        print("\nNothing draftable in this batch.")
        return

    print(f"\n{len(pairs)} paper(s) to draft:")
    for p, _ in pairs[:8]:
        print(f"  {(p.get('citations') or 0):>5} cites  {p['slug']}")
    if len(pairs) > 8:
        print(f"  ... and {len(pairs) - 8} more")
    print()

    mode = args.mode or cfg["llm"]["mode"]
    if args.effort:
        cfg["llm"]["effort"] = args.effort
    if mode in ("api", "openai"):
        caller = call_api if mode == "api" else call_openai
        ev = {p["slug"]: e for p, e in pairs}

        def landed(slug, sc, how_now, again):
            """Write this draft, and repair it, before the next paper is asked for.

            The batch used to be held in memory until the last paper came back, and only
            then written and only then repaired. Over 111 papers that is hours during
            which a crash, a Ctrl-C or a closed laptop throws away every finished draft
            -- and the papers are drafted most-cited first, so the ones lost are the ones
            that mattered most. Each paper is now durable the moment it exists.
            """
            write_draft(slug, sc, how_now)
            if args.repair:
                left = repair(slug, args.repair, again, ev.get(slug, ""), how_now)
                print(f"      {left} finding(s) left for you")

        if args.repair:
            print(f"drafting, then repairing each against the checks, up to "
                  f"{args.repair} round(s) per paper:")
        answers, how, asker = caller(pairs, cfg, landed)
        print(f"\nwrote {len(answers)} draft(s) to data/sidecars/drafts/")
        print("Next: python scripts/draft_sidecars.py --review")
    else:
        path = emit_tasks(pairs, cfg)
        print(f"wrote {path}")
        print("Fill each task's `sidecar` field (the paper-geo skill does this), then:")
        print("  python scripts/draft_sidecars.py --ingest")


if __name__ == "__main__":
    main()
