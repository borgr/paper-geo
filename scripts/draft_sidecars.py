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
import glob
import hashlib
import inspect
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import yaml  # noqa: E402

from common import BUILD, DATA, ROOT, get, load_config, read_yaml, rules_block  # noqa: E402
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
]


def emit_tasks(pairs: list[tuple[dict, str]], cfg) -> str:
    os.makedirs(BUILD, exist_ok=True)
    tasks = [{"slug": p["slug"], "title": p.get("title_display") or p["title"],
              "evidence": ev, "sidecar": None}
             for p, ev in pairs]
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



def call_api(pairs: list[tuple[dict, str]], cfg) -> tuple[dict, str, "Callable"]:
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
    TOOL = {"tools": [{"name": "sidecar", "description": "The sidecar for this paper.",
                       "input_schema": sch}],
            "tool_choice": {"type": "tool", "name": "sidecar"}}
    # (what the request adds, how the reply is read, what to call it when refused).
    RUNGS = [({"output_config": {"effort": eff,
                                 "format": {"type": "json_schema", "schema": sch}}},
              "schema", "structured output"),
             ({"output_config": {"effort": eff}, **TOOL},
              "tool", f"a forced tool call at {eff} effort"),
             (TOOL, "tool", "a forced tool call"),
             ({}, "text", "a plain request")]
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

    def ask(user: str, label: str) -> dict | None:
        """One completion, or None with the reason printed. `label` is for the reader."""
        nonlocal rung, worked
        while True:
            extra, how_out, _ = RUNGS[rung]
            req = dict(model=cfg["llm"]["model"],
                       max_tokens=cfg["llm"].get("max_tokens", API_MAX_TOKENS),
                       system=sys_prompt,
                       messages=[{"role": "user", "content":
                                  user + (JSON_ONLY if how_out == "text" else "")}])
            try:
                msg = send(req, extra)
                worked = True
                break
            except Exception as e:                    # noqa: BLE001 -- any 4xx means no
                # Only ever climb down before the first success. Once one request has gone
                # through, the endpoint's dialect is settled and a failure is a failure --
                # retrying it unenforced would quietly turn a rate limit into an
                # undecoded draft.
                if worked or rung + 1 >= len(RUNGS):
                    print(f"  failed: {label} -- {type(e).__name__}: {str(e)[:200]}",
                          file=sys.stderr)
                    return None
                rung += 1
                print(f"  {label}: the endpoint refused {RUNGS[rung - 1][2]}; "
                      f"retrying with {RUNGS[rung][2]}", file=sys.stderr)
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
        # `_first_json` rather than `json.loads` even on the enforced rung: it reads a bare
        # object identically, and on an unenforced one the object arrives inside a fence.
        sc = _first_json(text)
        if sc is None:
            print(f"  no JSON object in the reply: {label} ({len(text)} chars)",
                  file=sys.stderr)
        return sc

    # Left at 0, which `fits` reads as "do not truncate the paper". Unlike the
    # OpenAI-compatible path, `max_tokens` here is a reply budget rather than part of a
    # sum with the prompt, and the input window is an order of magnitude larger than any
    # paper plus its sidecar -- so a repair round gets the whole text, tables included.
    ask.window = 0

    for p, ev in pairs:
        sc = ask(USER.format(evidence=ev), p["slug"])
        if sc is None:
            continue
        out[p["slug"]] = sc
        print(f"  ok  {p['slug']}  ({len(sc.get('claims') or [])} claims, "
              f"{len(sc.get('qa') or [])} question groups)")
    return out, (f"{cfg['llm']['model']} via the Anthropic API, {eff} effort "
                 f"({ENFORCED[RUNGS[rung][1]]})"), ask


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
ENV_BASE, ENV_MODEL = "PAPER_GEO_LLM_BASE_URL", "PAPER_GEO_LLM_MODEL"
ENV_KEY, ENV_HEADER = "PAPER_GEO_LLM_API_KEY", "PAPER_GEO_LLM_KEY_HEADER"


def _first_json(text: str):
    """The first complete JSON object in a response, or None.

    Needed because a model without enforced decoding wraps the object in a ``` fence,
    or prefaces it, or emits a reasoning trace first. Brace-matching rather than a
    regex, since claim text legitimately contains braces.
    """
    start = text.find("{")
    while start != -1:
        depth, instr, esc = 0, False, False
        for i in range(start, len(text)):
            c = text[i]
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                instr = not instr
            elif not instr and c == "{":
                depth += 1
            elif not instr and c == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i + 1])
                    except json.JSONDecodeError:
                        break
        start = text.find("{", start + 1)
    return None


# Keywords a constrained-decoding backend cannot compile. vLLM's grammar backends accept
# a `response_format` containing them and then quietly decode unguided, which is the worst
# available outcome: measured against Granite 3.3 8B, the full schema produced claims keyed
# `statement`/`magnitude`/`unit` -- invented fields, valid JSON, nothing the repo can read
# -- while the same request with these keywords removed produced the schema's own keys.
#
# Nothing is lost by dropping them here. The only conditional in the sidecar schema is
# "a `result` claim needs `evidence`", and that is a schema-tier rule `validate.py`
# enforces on the draft afterwards, where a violation is a finding rather than a token
# the decoder should never have been allowed to emit.
_UNDECODABLE = ("allOf", "anyOf", "oneOf", "not", "if", "then", "else")


def decodable(node):
    """The schema with conditional keywords removed, for guided decoding only."""
    if isinstance(node, dict):
        return {k: decodable(v) for k, v in node.items() if k not in _UNDECODABLE}
    if isinstance(node, list):
        return [decodable(x) for x in node]
    return node


def call_openai(pairs, cfg) -> tuple[dict, str, "object"]:
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
    try:
        from openai import OpenAI
    except ImportError:
        sys.exit("pip install openai, or set llm.mode: skill in config.yaml")
    base = os.environ.get(ENV_BASE)
    model = os.environ.get(ENV_MODEL) or cfg["llm"].get("model_openai")
    if not base or not model:
        sys.exit(f"llm.mode: openai needs ${ENV_BASE} and ${ENV_MODEL} in the "
                 f"environment (the endpoint is never committed -- see call_openai)")
    key = os.environ.get(ENV_KEY, "unused")
    headers = {os.environ[ENV_HEADER]: key} if os.environ.get(ENV_HEADER) else None
    client = OpenAI(base_url=base, api_key=key, default_headers=headers)

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

    def ask(user: str, label: str) -> dict | None:
        """One completion, or None with the reason printed. `label` is for the reader.

        Extracted so the repair round below reuses the request exactly -- same schema,
        same window arithmetic, same fallback when the gateway will not enforce. A repair
        that quietly ran unguided while the draft was guided would compare two things.
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
        rf = {"type": "json_schema",
              "json_schema": {"name": "sidecar", "schema": decodable(sch), "strict": True}}
        try:
            r = client.chat.completions.create(**req, response_format=rf)
            enforced = True if enforced is None else enforced
        except Exception as e:                        # noqa: BLE001 -- any 4xx means no
            if enforced:                              # it worked before, so this is real
                print(f"  failed: {label} -- {type(e).__name__}", file=sys.stderr)
                return None
            enforced = False
            try:
                r = client.chat.completions.create(**req)
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
        sc = _first_json(text)
        if sc is None:
            print(f"  no JSON object in the reply: {label} ({len(text)} chars)",
                  file=sys.stderr)
        return sc

    for p, ev in pairs:
        sc = ask(USER.format(evidence=ev)
                 + JSON_ONLY,
                 p["slug"])
        if sc is None:
            continue
        out[p["slug"]] = sc
        print(f"  ok  {p['slug']}  ({len(sc.get('claims') or [])} claims, "
              f"{len(sc.get('qa') or [])} question groups)")
    how = "schema-enforced" if enforced else "unenforced, parsed from text"
    # The window travels with the closure because `repair` has to fit a paper into what is
    # left of it and has no other way to know how big it is. An attribute rather than a
    # third return value: every caller wants the request, one wants its budget.
    ask.window = window or 0
    return out, f"{model} via an OpenAI-compatible endpoint ({how})", ask


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


def write_draft(slug: str, sidecar: dict, source: str) -> str:
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
            refused.append((slug, f"{n} finding(s) against the current checks"))
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
    errs, typed = [], True
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
        typed = False
    except Exception as e:
        errs.append(f"{path}: {str(e).splitlines()[0]}")
    ids = {c.get("id") for c in (fm.get("claims") or [])}
    for qa in fm.get("qa") or []:
        for a in qa.get("answers") or []:
            if a not in ids:
                errs.append(f"{path}: qa answer `{a}` is not a claim id")

    if not typed:
        # The quality tier reads a sidecar's fields at their declared types -- terminology
        # as a mapping, claims as a list of objects -- and a document the schema just
        # rejected may not have those types at all. An endpoint that would not decode
        # against the schema returned `terminology` as a list, and the readability rules
        # raised AttributeError halfway through the run: a check that crashes reports
        # nothing, including about the fields that were fine. The schema finding above
        # already names the field and the expected type, and it is fatal here, so there is
        # nothing the quality tier could add that the author would act on first.
        return errs, []

    from validate import (check_claim_evidence, check_claim_numbers, check_readability,
                          check_sidecar_shape)
    entry = [(os.path.basename(path), fm)]
    quality = check_sidecar_shape(entry) + check_readability(entry)
    numbers, no_text = check_claim_numbers(entry)
    quality += numbers + check_claim_evidence(entry)[0]
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
        first = ((g.get("q") or [None])[0])
        for a in g.get("answers") or []:
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
        qs = [q for q in (g.get("q") or []) if q]
        print(f"\n  Q{i + 1}. {qs[0] if qs else '(no question text)'}"
              + (f"   (+{len(qs) - 1} more phrasing(s))" if len(qs) > 1 else ""))
        for m in (qs and d["prose_q"].get(str(qs[0])) or []):
            print(f"      UNANSWERABLE ALONE  {m}")
        if not (g.get("answers") or []):
            print("      nothing answers this -- point it at a claim or drop it")
        for a in g.get("answers") or []:
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
        if len(g.get("q") or []) > 1:
            print(f"\n  Q{i + 1} phrasings:")
            for q in g["q"]:
                print(f"      {q}")
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
@media (prefers-color-scheme: dark) {
  :root { --bg:#16181c; --fg:#e8e8e8; --dim:#a0a0a0; --line:#2e3238; --card:#1d2025;
          --bad:#ff8fa3; --badbg:#3a1520; --ok:#7ddaa0; --warn:#e8c07a; --warnbg:#3a2f14; } }
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
        out.append(f"<p class=one>{e(d['one_liner'])}</p>")
        out.append("<div class=cmd>python scripts/draft_sidecars.py --accept "
                   + e(slug) + (" --replace" if p.get("has_sidecar") else "") + "</div>")

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
            qs = [x for x in (g.get("q") or []) if x]
            extra = (f" <span class=dim>+{len(qs) - 1} phrasing"
                     f"{'s' if len(qs) > 2 else ''}</span>") if len(qs) > 1 else ""
            why = "".join(f"<br><span class=bad>unanswerable alone</span> "
                          f"<span class=dim>{e(m)}</span>"
                          for m in (d["prose_q"].get(str(qs[0])) or []) if qs)
            head = e(qs[0]) if qs else "(no question text)"
            out.append(f"<p class=ask id='{e(slug)}-q{gi}'>{head}{extra}{why}</p>")
            answers = [a for a in (g.get("answers") or [])]
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
            out += ["<h3>Paraphrase check</h3>",
                    "<p class=sub>The answers are above. What is left to read here is "
                    "whether the 2\u20134 phrasings of one question vary the way real "
                    "queries do — wording, specificity, the terms someone who has not "
                    "read the paper would use — rather than restating each other.</p>"]
            for gi, g in enumerate(d["qa"]):
                out.append("<ul class=q>")
                for i, q in enumerate(g.get("q") or []):
                    why = d["prose_q"].get(str(q)) or []
                    out.append(f"<li>{'<b>' if not i else ''}{e(q)}"
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
    os.makedirs(BUILD, exist_ok=True)
    with open(REVIEW_PAGE, "w") as fh:
        fh.write(review_page(papers))
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
    print(f"no sidecar, no draft "
          f"{len([p for p in papers if p['slug'] not in live]) - len(drafted)}")
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
        answers, how, asker = caller(pairs, cfg)
        for slug, sc in answers.items():
            write_draft(slug, sc, how)
        print(f"\nwrote {len(answers)} draft(s) to data/sidecars/drafts/")
        if args.repair and asker:
            print(f"\nrepairing against the checks, up to {args.repair} round(s):")
            ev = {p["slug"]: e for p, e in pairs}
            for slug in answers:
                left = repair(slug, args.repair, asker, ev.get(slug, ""), how)
                print(f"  {slug}: {left} finding(s) left for you")
        print("Next: python scripts/draft_sidecars.py --review")
    else:
        path = emit_tasks(pairs, cfg)
        print(f"wrote {path}")
        print("Fill each task's `sidecar` field (the paper-geo skill does this), then:")
        print("  python scripts/draft_sidecars.py --ingest")


if __name__ == "__main__":
    main()
