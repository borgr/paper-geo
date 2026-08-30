#!/usr/bin/env python3
"""Handing a draft back to the model with what the checks found.

Two loops, both driven by `validate.py`'s findings and both bounded:

    repair   rewrite the whole sidecar, up to N rounds, stopping when a round stops
             reducing the finding count
    mend     ask for a patch against named loci instead, for when one field is wrong and
             a rewrite would churn the rest

Plus `reroute`, which rewrites only the question groups through the four reader routes.
The locus helpers (`where`, `at`, `put`, `limits`, `spread`) address one field inside the
front matter by a dotted path, so a repair can fix one claim's scope and leave every
other line byte-identical.
"""
from __future__ import annotations

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


from common import QA_ROLES, qa_loci, rules_block  # noqa: E402
from llm import JSON_ONLY  # noqa: E402
from sidecar_io import (RULES_DOC, draft_path, front_matter, held,  # noqa: E402
                        live_path, oneline, read_front_matter, validate_draft,
                        write_draft)

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

    A repair prompt is the only one carrying the paper *and* a full sidecar, which on a 32k
    window do not both fit: TIES-Merging's text is 74k chars, leaving 2048 tokens for a
    reply needing about four thousand, so round one came back truncated and the loop kept
    the draft it was asked to fix.

    Head and tail rather than the first N chars, because the findings that need the paper
    ask for a magnitude, and magnitudes are in the tables at the end. The middle is related
    work and method prose, which the claims are already written from.
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

    Returns the number of findings left on the draft. `again(prompt_extra)` is the caller's
    own one-paper call, so this knows nothing about which backend it drives.

    `evidence` is the paper text the draft was written from, and it decides which findings
    are fixable. Without it the loop can only re-word what it already wrote, so a finding
    asking for a fact -- a dropped magnitude, the real conditions behind a thin scope --
    stays open by construction.

    Stops when a round stops reducing the count, past which the loop optimises against the
    proxies rather than fixing anything.
    """
    path = draft_path(slug)
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
        # Deleting the content is the cheapest way to satisfy a checker: one round answered 17
        # findings with a sidecar holding none of the paper's 12 claims and none of its 8 question
        # groups, and was kept because 2 < 17. A round may merge or split claims; it may not drop
        # the sidecar on the floor. Refused before it is written, so the draft on disk never
        # passes through the collapsed state.
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
            # Keep the better draft. The early stop above only skips the *next* round, so a final
            # round that overshoots still lands on disk and replaces what it was meant to improve
            # (15 -> 7 -> 4 -> 6, and the 6 is what the reviewer gets). Overshoot is the loop's
            # characteristic failure: told a scope is too long it cuts, and cutting past the floor
            # trades one finding for another.
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

    Narrow on purpose. A full redraft of an accepted sidecar is a claim rewrite -- run once
    on `fusing-finetuned-models`, it returned 9 claims where the author had verified 11,
    with a different `one_liner` and different misreadings. Migrating 113 papers that way
    would discard every figure already checked against its paper, to fix questions.

    So the model never sees the paper: the claims *are* the answers and the group already
    says what it asks, so what is missing is only the vocabulary each kind of person would
    have typed. Returns `(groups rerouted, findings left on the draft)`.
    """
    # The draft when one exists, since that is what `--accept` will promote; the live file
    # otherwise.
    path = next((f for f in (draft_path(slug), live_path(slug)) if os.path.exists(f)), None)
    fm, unread = read_front_matter(path) if path else (None, "")
    if unread:
        print(f"    {os.path.basename(path)}: {unread} -- rerouting nothing in it",
              file=sys.stderr)
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
    errs, qual = validate_draft(draft_path(slug), note=False)
    return done, len(errs) + len(qual)


def where(finding: str, fm: dict | None = None) -> str | None:
    """The single field a finding is about, as a locus, or None if it is about no one field.

    A locus is `claim/<id>/text`, `claim/<id>/scope`, `qa/<i>/ask/<role>`,
    `qa/<i>/ask/unsorted/<j>`, `misreadings/<i>` or `term/<name>`, always a path whose leaf
    is a string.

    Most findings name their field (`claim 'x': ...`), with the colon optional because the
    invented-figure check omits it (`claim 'x' states 29`). The self-containment checks
    instead open with the offending string, then ` -- `, then the complaint, so those are
    located by looking the string up in `fm`, and return None without it. A finding about
    the whole set of claims returns None too, and `spread` names that set where it can.
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

    `where` returns None for the figure floor because no single claim is at fault, but the
    set is exactly known -- every `result` claim stating no figure -- and it is the largest
    family left in the corpus. Handing them over together is safe here for a reason that
    does not generalise: a number invented to satisfy this is caught by
    `check_claim_numbers` against the paper's text, and mend reverts the whole group when
    the count does not fall.
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


def spliced(slug: str, fm: dict, path: str, source: str) -> list[str]:
    """Write the draft as it now stands and return what validate says about it.

    Each finding is shorn of its `<slug>.md: ` prefix, which is how `where` reads them.
    """
    write_draft(slug, fm, f"{source} + a targeted repair")
    errs, qual = validate_draft(path, note=False)
    return [str(x).split(".md: ")[-1] for x in errs + qual]


def mend(slug: str, again, evidence: str = "", source: str = "a model") -> int:
    """Fix what is fixable one field at a time, and keep the result only if it helped.

    `repair` hands over the whole sidecar and takes a whole sidecar back, so a round can
    regress a claim it was not asked about -- which is the plateau that loop stops on. Here
    the model sees only the offending strings and returns `(locus, new value)` pairs spliced
    into a draft the rest of which cannot move.

    Returns the finding count the draft is left with, mended or not.
    """
    path = draft_path(slug)
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
    # Judging the patch whole loses both ways: it discards five good fixes because a sixth
    # traded one finding for another, and keeps five rewrites that changed nothing because a
    # sixth happened to help -- churn in a draft a human then has to re-read.
    kept, undone, count = [], [], before
    for locus, value in singles.items():
        snapshot, held = open(path, encoding="utf-8").read(), at(fm, locus)
        put(fm, locus, value)
        found = spliced(slug, fm, path, source)
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
        found = spliced(slug, fm, path, source)
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
