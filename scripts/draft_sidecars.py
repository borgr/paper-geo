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

from common import BUILD, DATA, ROOT, get, load_config, read_yaml  # noqa: E402
from fulltext import resolve as resolve_fulltext  # noqa: E402

SIDECARS = os.path.join(DATA, "sidecars")
DRAFTS = os.path.join(SIDECARS, "drafts")
CACHE = os.path.join(BUILD, "fulltext")
TASKS = os.path.join(BUILD, "sidecar_tasks.json")

SYSTEM = """You extract, from a paper, the small set of statements that decide whether \
an answer engine describes it correctly. You are drafting for the paper's own author, \
who will verify and correct every line, so the useful output is precise and checkable \
rather than complete and smooth.

What you produce is consumed two ways: rendered on the paper's canonical page, and \
retrieved as isolated passages by retrieval-augmented systems. The second is what \
drives every rule below.

CLAIMS are the core. Each one:
- is self-contained. It will be retrieved alone, with no title and no surrounding \
paragraph, so it must name the object, the finding, and the magnitude in one sentence. \
No "we", no "this paper", no pronoun pointing outside the sentence.
- carries the number the paper reports, with its unit and its baseline. "improves \
accuracy" is worthless; "raises exact-match by 4.6 points over the fine-tuned \
baseline on the WMT16 en-de test set" is a claim. If the paper does not state a \
magnitude for a finding, say so in the text rather than inventing one.
- has a SCOPE: the conditions under which it holds, and where it does not. This is \
content, not a disclaimer. "Further research is needed" is worthless. "Holds for \
models above 1B parameters; the 125M model shows no effect" is scope. Summarisers \
drop scope far more often than they drop findings, which is exactly why it is \
written separately and adjacent.
- cites where it comes from in EVIDENCE: "Table 2", "Figure 4b", "Section 5.1".

QA pairs point at claim ids. Never restate a claim in an answer -- a restated claim is \
a second, drifting copy of the author's own finding, and the two then compete. Give \
2-4 genuine PARAPHRASES per question, in the vocabulary someone who has not read the \
paper would use, because engines fan one query into many synthetic sub-queries and you \
cannot know which phrasing wins. Never a question whose answer is not adjacent.

MISREADINGS are stated as corrections, not questions: what people wrongly conclude, \
and what is actually true. Only include one if the paper gives you a reason to expect \
it -- a result that is easy to over-generalise, a negative result, a method whose name \
suggests more than it does.

TERMINOLOGY is only for terms this paper uses in a non-obvious sense, or coins. Not a \
glossary of the field.

Accuracy over coverage, everywhere. Three claims you can point at a table for are \
worth more than eight that read well. If the evidence you were given does not support \
something, leave it out. Never infer results from the title, the venue, or what \
similar papers usually find."""

USER = """Draft the sidecar for this paper.

{evidence}

Return JSON matching the schema. Rules that are easy to get backwards:
- `answers` holds claim IDS from your own `claims` list, never prose.
- `one_liner` is the sentence the author will reuse verbatim everywhere; make it \
quotable and specific, under 320 characters.
- `coined` and `gloss` only if the paper actually coins a name.
- Leave a field out rather than filling it with something you cannot support."""


# --------------------------------------------------------------- evidence

def fulltext(p: dict, cfg: dict, limit: int = 60000) -> tuple[str, str]:
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
        parts += [f"full text (from {ft_source}, truncated):", ft, ""]
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


def emit_tasks(pairs: list[tuple[dict, str]], cfg) -> str:
    os.makedirs(BUILD, exist_ok=True)
    tasks = [{"slug": p["slug"], "title": p.get("title_display") or p["title"],
              "evidence": ev, "sidecar": None}
             for p, ev in pairs]
    with open(TASKS, "w") as f:
        json.dump({"system": SYSTEM, "user_template": USER,
                   "schema": schema(), "tasks": tasks}, f, indent=1)
    return TASKS


def call_api(pairs: list[tuple[dict, str]], cfg) -> dict:
    """One Messages API call per paper, validated against the sidecar schema."""
    try:
        import anthropic
    except ImportError:
        sys.exit("pip install anthropic, or set llm.mode: skill in config.yaml")
    client = anthropic.Anthropic()
    sch, out = schema(), {}
    for p, ev in pairs:
        req = dict(model=cfg["llm"]["model"], max_tokens=8192, system=SYSTEM,
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

Then promote it:  python scripts/draft_sidecars.py --accept {slug}
-->
"""


def write_draft(slug: str, sidecar: dict, source: str) -> str:
    os.makedirs(DRAFTS, exist_ok=True)
    path = os.path.join(DRAFTS, f"{slug}.md")
    body = yaml.safe_dump(sidecar, sort_keys=False, allow_unicode=True,
                          default_flow_style=False, width=88)
    with open(path, "w") as f:
        f.write(HEADER.format(slug=slug, source=source) + "---\n" + body + "---\n")
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


def validate_draft(path: str) -> list[str]:
    """Schema-check one draft, and check claim ids resolve, before promoting it."""
    with open(path) as f:
        text = f.read()
    m = re.search(r"^---\n(.*?)^---\n", text, re.S | re.M)
    if not m:
        return [f"{path}: no YAML front matter"]
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        return [f"{path}: unparseable front matter: {e}"]
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
    return errs


def accept(slugs: list[str]) -> int:
    """Promote drafts into data/sidecars/, refusing anything that fails the schema."""
    n = 0
    for slug in slugs:
        src = os.path.join(DRAFTS, f"{slug}.md")
        if not os.path.exists(src):
            print(f"  no draft for {slug}")
            continue
        errs = validate_draft(src)
        if errs:
            print(f"  {slug}: NOT promoted --")
            for e in errs:
                print(f"      {e}")
            continue
        dst = os.path.join(SIDECARS, f"{slug}.md")
        if os.path.exists(dst):
            print(f"  {slug}: a live sidecar already exists; not overwriting")
            continue
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
            errs = validate_draft(f)
            flag = "  [schema errors]" if errs else ""
            print(f"  {(p.get('citations') or 0):>5} cites  {slug}{flag}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ingest", action="store_true",
                    help="fold build/sidecar_tasks.json answers into drafts/")
    ap.add_argument("--review", action="store_true", help="what is drafted vs live")
    ap.add_argument("--accept", nargs="+", metavar="SLUG", help="promote these drafts")
    ap.add_argument("--accept-all", action="store_true", help="promote every draft")
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
    if args.accept_all:
        slugs = [os.path.basename(f)[:-3]
                 for f in glob.glob(os.path.join(DRAFTS, "*.md"))]
        print(f"promoting {len(slugs)} draft(s):")
        print(f"\n{accept(slugs)} promoted.")
        return
    if args.accept:
        print(f"\n{accept(args.accept)} promoted.")
        return
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
