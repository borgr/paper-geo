#!/usr/bin/env python3
"""Reading, writing and staleness for one sidecar file.

The layer `draft_sidecars.py`, `sidecar_repair.py` and `sidecar_review.py` all sit on:
where the files live, what shape one must have, whether a draft was written against the
current rules, and how to put one on disk without losing the author's edits.

A sidecar is a `.md` whose front matter is the artifact. `write_draft` dumps that YAML at
width 88, so string values wrap and cannot be patched by substitution -- go through
`front_matter()`, edit the object, and write it back.
"""
from __future__ import annotations

import glob
import hashlib
import inspect
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import yaml  # noqa: E402

from common import BUILD, DATA, ROOT, answered_by, rules_block  # noqa: E402

SIDECARS = os.path.join(DATA, "sidecars")
DRAFTS = os.path.join(SIDECARS, "drafts")
CACHE = os.path.join(BUILD, "fulltext")   # extracted paper text, from fulltext.py


RULES_DOC = "docs/SIDECAR.md"


def draft_path(slug: str) -> str:
    """Path to `slug`'s draft, whether or not it exists."""
    return os.path.join(DRAFTS, f"{slug}.md")


def live_path(slug: str) -> str:
    """Path to `slug`'s published sidecar, whether or not it exists."""
    return os.path.join(SIDECARS, f"{slug}.md")


def draft_paths() -> list[str]:
    """Every draft on disk, sorted."""
    return sorted(glob.glob(os.path.join(DRAFTS, "*.md")))


def live_paths() -> list[str]:
    """Every published sidecar on disk, sorted."""
    return sorted(glob.glob(os.path.join(SIDECARS, "*.md")))


def spec_sha() -> str:
    """Short hash of everything that decides whether a draft is acceptable.

    The rules the model is sent, the schema it fills, and the *source* of every function
    that judges the result -- `readability` included, because a draft written before the
    sentence caps existed is exactly a draft `--accept` now refuses.

    Not the rules doc alone: the rule that rejected all 17 accumulated drafts (every sidecar
    needs a `kind: context` claim) lives in `validate.check_sidecar_shape`, in code, with
    the prose untouched. A stamp over the prose would move on a typo and hold still through
    that.
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

    Decides whether a re-draft may overwrite it. Their edits are the review this whole step
    exists to collect, and the only thing here that cannot be re-derived.

    An unstamped draft is answered from git instead: a committed draft nobody has touched is
    the drafter's own output, and replacing it costs a `git checkout` to undo. Treating
    unstamped as edited would freeze exactly the 17 drafts this exists to unfreeze.
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
    for f in draft_paths():
        slug, why = os.path.basename(f)[:-3], stale(f, spec)
        if not why:
            out[slug] = "current"
        elif edited(f):
            out[slug] = f"{why}, and you have edited it"
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

{promote}
{stamp}
-->
"""
_PROMOTE_NEW = "Then promote it:  python scripts/draft_sidecars.py --accept {slug}\n"
# Accepting over a reviewed sidecar is the one destructive path here, so the banner sits
# at the top of the file rather than in an error at accept time -- and the diff comes
# before the checklist, because here the comparison *is* the review. A live sidecar may be
# worded by the author, and a more complete draft is not better where he was already right.
_BANNER_REPLACE = """
THIS PAPER ALREADY HAS A LIVE SIDECAR, and this draft would replace it. Start here:

  diff data/sidecars/{slug}.md data/sidecars/drafts/{slug}.md

Anything the live file says in your own words is worth keeping over a rewrite of the
same point, so read that diff before the checklist below.
"""
_PROMOTE_REPLACE = ("Then, if the replacement is the one you want:\n\n"
                    "  python scripts/draft_sidecars.py --accept {slug} --replace\n")


def unstructure(value, spec: dict):
    """Put a reply back into the shape the schema asked for, where that is lossless.

    A forced tool call over-structures. `misreadings` is declared as an array of plain
    strings, and one live pass returned it as `[{"text": "The 0.77 accuracy ..."}]` in one
    draft and as a string exploded character by character (`{"0": "T", "1": "h", ...}`) in
    two more. Each is a string wearing an object and each converts back exactly.

    Narrow by design. It turns an object into the string the schema already required, and
    only when the object holds nothing the string does not. Anything else is returned
    untouched, since a shape code cannot unambiguously recover is a finding for the author.
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
    path = draft_path(slug)
    body = yaml.safe_dump(sidecar, sort_keys=False, allow_unicode=True,
                          default_flow_style=False, width=88)
    live = os.path.exists(live_path(slug))
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

    `spec_sha` hashes the source of every function that judges a draft, so editing any
    check -- even adding a rule the drafts already satisfy -- marks all of them "spec
    moved". The only way back was `--ingest`, which rewrites front matter from the task file
    and destroys the author's review. This is the third option.

    It refuses a draft that does not currently pass, and that restriction is the safety
    property: a stamp is what makes `pending` skip a slug and `held` keep it, so stamping a
    failing draft would park it where nothing queues it and nothing reports it.
    """
    spec, done, refused = spec_sha(), [], []
    for f in draft_paths():
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


def read_front_matter(path: str) -> tuple[dict | None, str]:
    """The front matter of one sidecar, and what stopped it being read.

    `({...}, "")` when it parsed. `(None, why)` for a file with no `---` block and for one
    whose YAML will not parse -- two states with different remedies, since the first is a
    file nothing has drafted and the second is one somebody edited by hand.
    """
    with open(path) as f:
        m = re.search(r"^---\n(.*?)^---\n", f.read(), re.S | re.M)
    if not m:
        return None, "no YAML front matter"
    try:
        return yaml.safe_load(m.group(1)) or {}, ""
    except yaml.YAMLError as e:
        return None, f"unparseable front matter: {e}"


def front_matter(path: str) -> dict | None:
    """The front matter of one sidecar, `None` for a file with none and for broken YAML.

    Use `read_front_matter` wherever `None` would be reported as a clean or finished state.
    """
    return read_front_matter(path)[0]


def validate_draft(path: str, note: bool = True) -> tuple[list[str], list[str]]:
    """Check one draft before promoting it. Returns (structural, quality).

    Both refuse promotion, and they are returned apart because they mean different
    things. A structural error means the file is broken and the site would render it
    wrong. A quality finding -- a band violation, a figure that is not in the paper --
    means the file is well-formed and says something the author would not want to have
    said. Accepting is the moment those become an assertion under their name, which is
    why the tier that `validate.py` reports and shrugs at is fatal here.
    """
    fm, why = read_front_matter(path)
    if fm is None:
        return [f"{path}: {why}"], []
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
    # Each check runs inside its own guard, so a check that cannot read the draft becomes one
    # finding instead of taking the tier down with it. Not the same as skipping the quality
    # tier when the schema rejected the document: four drafts with one schema error and ten
    # readability findings each then reported one finding, were repaired against it, and were
    # stamped `checks=1`. A tier that goes quiet is worse than one that dies, because the
    # count it reports is believable.
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
