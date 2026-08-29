#!/usr/bin/env python3
"""Draft a sidecar per paper from the paper itself, for a human to verify.

A sidecar is the one per-paper input nothing else here can derive: the claims in quotable
form, the scope conditions each holds under, the terms of art used in a non-obvious
sense, and the misreadings worth pre-empting. It is what decides whether an engine
describes the work *correctly* rather than merely finds it.

The claims, magnitudes, scope conditions and coined terms are all in the paper, so this
drafts them. What the author uniquely holds is whether a draft got them right, and which
misreading actually keeps happening -- so the author verifies.

Drafts land in `data/sidecars/drafts/<slug>.md`, never in `data/sidecars/`. Nothing reads
the drafts directory: the site, the validator, the fidelity check and the coverage count
all glob `data/sidecars/*.md` one level up. An unverified draft therefore cannot reach a
published page by accident, which is what makes bulk drafting safe. Promotion is explicit:

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

The nine drafting steps are sections of one prompt, not nine turns: every mode sends the
same system prompt and schema and reads back one object. Nothing here needs tool use or a
multi-turn agent.

`--repair N` (api and openai) hands the model back what the checks found, with the paper,
up to N times, stopping as soon as a round stops reducing the count. Measured on one
paper: 20 findings, then 5, then 2. In `skill` mode the second pass is the agent session
reading `--review`.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import yaml  # noqa: E402

from llm import JSON_ONLY, decodable, first_json, with_retries  # noqa: E402
from llm import client as llm_client  # noqa: E402
from common import (BUILD, DATA, README_NAMES, ROOT, get_status,  # noqa: E402
                    has_live_sidecar, load_config, phrasings, qa_loci, read_yaml,
                    rules_block, write_json)
from fulltext import LIMIT as FULLTEXT_LIMIT  # noqa: E402
from fulltext import cut_chars  # noqa: E402
from fulltext import resolve as resolve_fulltext  # noqa: E402
from sidecar_io import (CACHE, RULES_DOC, draft_path, draft_paths,  # noqa: E402
                        held, live_path, live_paths, read_front_matter, restamp, schema,
                        spec_sha, validate_draft, write_draft)
from sidecar_repair import mend, repair, reroute  # noqa: E402
from sidecar_review import review, show, suspects, write_review_page  # noqa: E402

TASKS = os.path.join(BUILD, "sidecar_tasks.json")

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

    Nothing is cached unless GitHub answered about every name. A 404 says the repo carries
    no README under that name. A refusal says nothing, and caching it would hold every
    later draft to the paper's own wording for as long as the cache lives.
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
    text, refused = "", False
    for branch in ("main", "master"):
        for name in README_NAMES:
            # retries=2: a repo whose default branch is `master` 404s on every name on the
            # way here, and the shared backoff would spend minutes discovering that.
            st, raw = get_status(f"https://raw.githubusercontent.com/{owner_repo}/"
                                 f"{branch}/{name}", timeout=30, retries=2, probe=True)
            if st == 200 and raw:
                text = raw.decode("utf-8", "replace")
                break
            refused = refused or st not in (404, 410)
        if text:
            break
    if text or not refused:
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

    Section and figure numbers, so `evidence:` can cite one that exists -- a Limitations
    claim citing Section 7 of a six-section paper is fatal at `--accept`. Captions too, since
    they carry the magnitudes and the full text is truncated head-and-tail, so a caption in
    the middle of a long paper is what the model never sees.

    Approximate, and safe in the direction it errs. PDF text loses column order, so a caption
    can arrive scrambled and a heading can be missed. Nothing here is authority --
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


def pending(papers: list[dict], do_all: bool, limit: int | None) -> list[dict]:
    """Papers with no live sidecar and no current draft, most cited first.

    A draft written against an acceptability spec that has since moved counts as no draft:
    `--accept` refuses it, and until this check existed nothing noticed, which is how 17
    unacceptable drafts came to sit in that directory with no run replacing them.

    A *live* sidecar today's checks would refuse counts the same way, and it is the file the
    site builds from. Excluding every paper with a live sidecar made acceptance permanent,
    so the two accepted before the scope rules existed were the only files no run could
    reach. The replacement draft is marked as such and needs `--accept --replace`.
    """
    live = {os.path.basename(f)[:-3] for f in live_paths()}
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

    The skip is the point. A paper no open source will give us has nothing to draft from but
    its title, and a sidecar written from a title is a page of confident guesses published
    under the author's name.

    The limit applies *after* the text check: filter-then-limit would let the same handful of
    unreachable papers fill every batch forever.

    Nothing is remembered as hopeless. Each is retried next run, so a source added to
    fulltext.py rescues yesterday's empty paper, and `data/fulltext/<slug>.pdf` takes effect
    the moment it appears.
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

    A paper re-queued by `--all` usually has something on disk: an unaccepted draft, or a
    live sidecar a later rule now finds fault with. Handed an empty `sidecar` field the only
    job available is writing the paper up from scratch, so a live file whose single finding
    is one sentence leaning on "The study" gets replaced wholesale, discarding ten claims a
    person had already checked. Seeded with the standing text and the findings against it,
    the job is a repair instead.

    The draft is preferred over the live file when both exist: it is newer, and it is the one
    `--ingest` will overwrite.
    """
    for path in (draft_path(slug),
                 live_path(slug)):
        if os.path.exists(path):
            fm, unread = read_front_matter(path)
            if fm:
                errs, qual = validate_draft(path, note=False)
                return fm, [str(x).split(".md: ")[-1] for x in errs + qual]
            if unread:
                # Said out loud, because the empty `sidecar` below is the from-scratch job
                # this docstring is about, and the file it would replace is on disk.
                print(f"  {os.path.relpath(path, ROOT)}: {unread} -- drafting this paper "
                      f"from scratch rather than repairing it", file=sys.stderr)
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
    write_json(
        TASKS,
        {"_contract": CONTRACT, "system": system_prompt(),
         "user_template": USER, "schema": schema(), "tasks": tasks}, indent=1)
    return TASKS


# A sidecar is a large structured object, and reasoning tokens are drawn from the same
# budget: serialised, the existing pages run 30k-42k characters, so six of them exceed
# 8192 output tokens on their own before any thinking. A truncated response is not
# recoverable and, worse, arrives as invalid JSON -- which reads as "the model wrote
# something malformed" when it wrote something correct and got cut off.
API_MAX_TOKENS = 32000

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
    # Four ways to guarantee the reply's shape, tried in order; the rung that works is
    # remembered for the rest of the run. api.anthropic.com accepts the first, and a
    # gateway in front of the same model may not -- a proxy behind `ANTHROPIC_BASE_URL`
    # answered `output_config.format: Extra inputs are not permitted` with a 400. A forced
    # tool call is schema enforcement by another route and proxies pass it through; rung 3
    # is for an endpoint that rejects `output_config` outright; the last rung asks in the
    # prompt and parses, which is a weaker result and is labelled as one in the header.
    #
    # `effort` rides along on every rung that will take it: it is orthogonal to how the
    # shape is guaranteed, and it decides how hard the model thinks about nine coupled
    # fields. Leave it off a rung and that rung silently drafts at the endpoint's default.
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
                # Whatever reaches here either is not the connection's fault or has already been
                # retried, so it is a real refusal. Only ever climb down before the first success:
                # once one request has gone through the endpoint's dialect is settled, and retrying
                # unenforced would turn a rate limit into an undecoded draft.
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


# An OpenAI-compatible backend, for gateways and open-weight models. Env vars rather than
# config keys because `config.yaml` is committed and public, while an inference gateway's
# URL may be internal to whoever runs this -- so it cannot be committed by accident.
#
#   PAPER_GEO_LLM_BASE_URL   the /v1 base, e.g. https://<gateway>/<model-slug>/v1
#   PAPER_GEO_LLM_MODEL      the model id the body must carry (often vendor-prefixed)
#   PAPER_GEO_LLM_API_KEY    the key, if the gateway wants one
#   PAPER_GEO_LLM_KEY_HEADER optional header name to send the key under, for gateways
#                            that authenticate on a custom header instead of Bearer
def call_openai(pairs, cfg, on_draft=None) -> tuple[dict, str, "object"]:
    """One chat completion per paper against an OpenAI-compatible endpoint.

    Returns (answers, provenance). The same prompt and schema as the Anthropic path -- the
    rules are the variable under test and the model is not, so nothing here rewords
    anything.

    Schema enforcement is attempted, not required: vLLM-backed gateways accept
    `response_format: json_schema`, others reject it with a 400, and refusing to run on those
    would rule out the open models this backend exists to try. So enforce if allowed,
    otherwise ask in the prompt and parse what comes back -- and record which happened,
    because "the model produced a valid sidecar" and "the decoder could not produce anything
    else" are different results.
    """
    client, model = llm_client(model_default=cfg["llm"].get("model_openai"),
                               context="llm.mode: openai")

    # A hosted open-weight model's context window has to hold prompt and reply together --
    # unlike the Anthropic path, `max_tokens` is part of that sum, and Qwen 2.5 72B at 32768
    # rejected a batch outright because a paper's evidence runs ~10.6k tokens against a
    # 32000-token reservation. So ask `/v1/models` what the window is and reserve what is
    # left; a gateway that does not answer leaves the configured number alone.
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
        src = draft_path(slug)
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
        dst = live_path(slug)
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
                 for f in draft_paths()]
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
        legacy, unread = [], []
        for f in live_paths():
            fm, why = read_front_matter(f)
            if fm is None:
                unread.append(f"{os.path.basename(f)[:-3]} ({why})")
            elif any(isinstance(g.get("ask"), dict) and g["ask"].get("unsorted")
                     for g in (fm.get("qa") or [])):
                legacy.append(os.path.basename(f)[:-3])
        if unread:
            # Separate from the line below, which says a sidecar was read and holds no
            # `unsorted` group. These were not read.
            print(f"not checked for `unsorted` groups: {', '.join(unread)}", file=sys.stderr)
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
                  for f in draft_paths()]
        want = args.mend or drafts
        unknown = [s for s in want if s not in drafts]
        if unknown:
            print(f"no draft for: {', '.join(unknown)}", file=sys.stderr)
        # Checked before any paper is fetched: a clean draft needs neither its text nor a
        # call, and over a whole corpus that is most of them.
        todo = [s for s in want if s in drafts
                and sum(len(x) for x in
                        validate_draft(draft_path(s), note=False))]
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
            errs, qual = validate_draft(draft_path(slug), note=False)
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
