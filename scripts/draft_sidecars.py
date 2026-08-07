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

Two modes, matching propose_topics.py:

  llm.mode: skill  (default)  writes build/sidecar_tasks.json for an agent session to
                              fill in. No API key. This is the paper-geo skill's path.
  llm.mode: api               calls the Anthropic API directly, for unattended reruns.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shutil
import sys

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


def evidence(p: dict, cfg: dict, no_fulltext: bool = False) -> str:
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
        parts += [f"full text (from {ft_source}; {how}):", ft, ""]
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


def pending(papers: list[dict], do_all: bool, limit: int | None) -> list[dict]:
    """Papers with no live sidecar and no draft yet, most cited first."""
    live = {os.path.basename(f)[:-3] for f in glob.glob(os.path.join(SIDECARS, "*.md"))}
    drafted = {os.path.basename(f)[:-3] for f in glob.glob(os.path.join(DRAFTS, "*.md"))}
    out = [p for p in sorted(papers, key=lambda q: -(q.get("citations") or 0))
           if p["slug"] not in live and (do_all or p["slug"] not in drafted)]
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


def call_api(pairs: list[tuple[dict, str]], cfg) -> dict:
    """One Messages API call per paper, validated against the sidecar schema."""
    try:
        import anthropic
    except ImportError:
        sys.exit("pip install anthropic, or set llm.mode: skill in config.yaml")
    client = anthropic.Anthropic()
    sch, out, sys_prompt = schema(), {}, system_prompt()
    for p, ev in pairs:
        req = dict(model=cfg["llm"]["model"], max_tokens=8192, system=sys_prompt,
                   messages=[{"role": "user", "content": USER.format(evidence=ev)}])
        oc = {"effort": cfg["llm"].get("effort", "medium"),
              "format": {"type": "json_schema", "schema": sch}}
        try:
            msg = client.messages.create(**req, output_config=oc)
        except TypeError:
            msg = client.messages.create(**req, extra_body={"output_config": oc})
        if msg.stop_reason == "refusal":
            print(f"  refused: {p['slug']}", file=sys.stderr)
            continue
        text = next((b.text for b in msg.content if b.type == "text"), "")
        try:
            out[p["slug"]] = json.loads(text)
            print(f"  ok  {p['slug']}  ({len(out[p['slug']].get('claims') or [])} claims)")
        except json.JSONDecodeError:
            print(f"  unparseable: {p['slug']}", file=sys.stderr)
    return out


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

{promote}-->
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


def write_draft(slug: str, sidecar: dict, source: str) -> str:
    os.makedirs(DRAFTS, exist_ok=True)
    path = os.path.join(DRAFTS, f"{slug}.md")
    body = yaml.safe_dump(sidecar, sort_keys=False, allow_unicode=True,
                          default_flow_style=False, width=88)
    live = os.path.exists(os.path.join(SIDECARS, f"{slug}.md"))
    banner = _BANNER_REPLACE.format(slug=slug) if live else ""
    promote = (_PROMOTE_REPLACE if live else _PROMOTE_NEW).format(slug=slug)
    with open(path, "w") as f:
        f.write(HEADER.format(source=source, banner=banner, promote=promote)
                + "---\n" + body + "---\n")
    return path


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


def validate_draft(path: str) -> tuple[list[str], list[str]]:
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
    except Exception as e:
        errs.append(f"{path}: {str(e).splitlines()[0]}")
    ids = {c.get("id") for c in (fm.get("claims") or [])}
    for qa in fm.get("qa") or []:
        for a in qa.get("answers") or []:
            if a not in ids:
                errs.append(f"{path}: qa answer `{a}` is not a claim id")

    from validate import check_claim_numbers, check_sidecar_shape
    entry = [(os.path.basename(path), fm)]
    quality = check_sidecar_shape(entry)
    numbers, no_text = check_claim_numbers(entry)
    quality += numbers
    if no_text:
        # Not a failure, and not silent either: the rule with no exceptions is the one
        # that must never quietly stop running.
        print(f"      note: no cached full text, so the figures in this draft were "
              f"not checked (python scripts/fulltext.py --slug {os.path.basename(path)[:-3]})")
    return errs, quality


def oneline(s) -> str:
    """A folded YAML scalar as one terminal line."""
    return re.sub(r"\s+", " ", str(s or "")).strip()


_KINDS = {"table": r"tab(?:le)?", "tab": r"tab(?:le)?",
          "figure": r"fig(?:ure)?", "fig": r"fig(?:ure)?",
          "section": r"(?:section|sec|§)", "sec": r"(?:section|sec|§)",
          "appendix": r"appendix", "app": r"appendix",
          "equation": r"(?:equation|eq)", "eq": r"(?:equation|eq)"}
# A pointer's kind, then its number. Appendices are lettered at least as often as they
# are numbered, and only appendices are, so the letter form is admitted for them alone --
# otherwise every `Fig a` and `sec. b` typo becomes a pointer to go hunting for.
_POINTER = re.compile(
    r"\b(table|figure|fig|tab|section|sec|equation|eq)\.?\s*([0-9]+(?:\.[0-9]+)*[a-z]?)\b"
    r"|\b(appendix|app)\.?\s*([0-9]+(?:\.[0-9]+)*|[A-Z](?:\.[0-9]+)*)\b", re.I)
# Kinds a paper also prints as a bare heading number.
_HEADED = ("section", "sec", "appendix", "app", "equation", "eq")


def evidence_pointers(s: str) -> list[tuple[str, re.Pattern]]:
    """Each 'Table 2' / 'Fig. 4b' / 'Appendix A' in an evidence string, and how to find it.

    Papers abbreviate their own cross-references inconsistently -- `Table 2`, `Tab. 2`,
    `table 2` -- so the pointer is matched by kind and number rather than verbatim.
    """
    out = []
    for m in _POINTER.finditer(str(s)):
        kind, num = (m.group(1), m.group(2)) if m.group(1) else (m.group(3), m.group(4))
        pat = rf"{_KINDS[kind.lower()]}\.?\s*{re.escape(num)}\b"
        # Two ways a paper names its own parts, and section pointers need the second one.
        # Inline is the cross-reference ("as shown in Table 2"); the heading form is the
        # part itself, printed as a bare number -- extracted text renders section 3.1 as
        # `3.1 LoRA models are difficult to merge`, and never as `Section 3.1`, so
        # checking the inline form alone failed every section pointer in the corpus.
        if kind.lower() in _HEADED:
            pat += rf"|^[ \t]*{re.escape(num)}[ \t]+\S"
        out.append((f"{kind} {num}", re.compile(pat, re.I | re.M)))
    return out


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


def show(slug: str) -> None:
    """Print each claim beside the evidence it cites, for the one review a human owes.

    Accepting a sidecar is the author asserting every line of it in public, and the
    thing that makes that reviewable in minutes rather than an hour is having the claim,
    its scope, the pointer it cites, and the paper's own sentence for each figure in one
    place. Otherwise reviewing means holding the PDF open in another window, which is
    the friction that left 116 of 117 papers without a sidecar.
    """
    path = os.path.join(DRAFTS, f"{slug}.md")
    if not os.path.exists(path):
        path = os.path.join(SIDECARS, f"{slug}.md")
    if not os.path.exists(path):
        return print(f"no draft and no live sidecar for {slug}")
    fm = front_matter(path)
    if fm is None:
        return print(f"{path}: unreadable front matter")

    from validate import figures, figures_in, rounds_to, values_in
    cache = os.path.join(CACHE, f"{slug}.txt")
    text = open(cache, errors="replace").read() if os.path.exists(cache) else ""
    have, vals = (figures_in(text), values_in(text)) if text else (set(), [])
    flat = re.sub(r"\s+", " ", text)

    print(f"\n{os.path.relpath(path, ROOT)}")
    print("one_liner: " + oneline(fm.get("one_liner")))
    if not text:
        print("  (no cached full text -- figures and pointers cannot be checked here)")

    answered = {a for g in (fm.get("qa") or []) for a in (g.get("answers") or [])}
    for c in fm.get("claims") or []:
        kind = c.get("kind") or "result"
        ev = c.get("evidence") or ("--" if kind == "context" else "MISSING")
        orphan = "" if c.get("id") in answered else "   (no question points here)"
        print(f"\n  [{kind}] {c.get('id')}   evidence: {ev}{orphan}")
        print("    " + oneline(c.get("text")))
        print("    scope: " + oneline(c.get("scope")))
        if not text:
            continue
        for label, pat in evidence_pointers(c.get("evidence") or ""):
            print(f"    {'ok' if pat.search(text) else 'NOT FOUND'}: the paper's own "
                  f"text mentions {label}")
        for n in figures(oneline(c.get("text")) + " " + oneline(c.get("scope"))):
            if n.isdigit() and 1900 <= int(n) <= 2099:
                continue
            if not (n in have or rounds_to(n, vals)):
                print(f"    {n:>9}  NOT IN THE PAPER -- correct it or drop the figure")
                continue
            # The paper's own words around the figure, so the author checks the number
            # against the sentence it came from rather than against a page number.
            print(f"    {n:>9}  {quote(flat, n)}")

    for i, g in enumerate(fm.get("qa") or []):
        print(f"\n  q{i + 1} -> {', '.join(g.get('answers') or []) or '(nothing)'}")
        for q in g.get("q") or []:
            print(f"      {q}")


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
    print(f"live sidecars      {len(live)}")
    print(f"drafts awaiting you {len(drafted)}")
    print(f"no sidecar, no draft {len([p for p in papers if p['slug'] not in live]) - len(drafted)}")
    if drafted:
        print("\nDrafts, most cited first — read, edit, then --accept:")
        rows = sorted(drafted, key=lambda f: -(
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
    ap.add_argument("--show", nargs="+", metavar="SLUG",
                    help="print each claim beside the evidence it cites, and the "
                         "paper's own sentence for every figure it states")
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
    args = ap.parse_args()

    cfg = load_config()
    papers = (read_yaml(os.path.join(DATA, "papers.yaml")) or {}).get("papers", [])

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
        print("Next: python scripts/draft_sidecars.py --review")
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

    if cfg["llm"]["mode"] == "api":
        answers = call_api(pairs, cfg)
        for slug, sc in answers.items():
            write_draft(slug, sc, f"the Anthropic API ({cfg['llm']['model']})")
        print(f"\nwrote {len(answers)} draft(s) to data/sidecars/drafts/")
        print("Next: python scripts/draft_sidecars.py --review")
    else:
        path = emit_tasks(pairs, cfg)
        print(f"wrote {path}")
        print("Fill each task's `sidecar` field (the paper-geo skill does this), then:")
        print("  python scripts/draft_sidecars.py --ingest")


if __name__ == "__main__":
    main()
