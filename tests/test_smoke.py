#!/usr/bin/env python3
"""The cheap checks that catch a broken repo before a run does.

There were no tests here for a long time, and the argument against them was that this
project is mostly string-munging over live HTTP: the interesting failures are wrong
prose and absent sources, and neither is unit-testable. That argument holds for the
*content*. It does not hold for the *wiring*, and the wiring is where the real bugs
were:

  - a worklist section that counted the same seventeen papers twice
  - `--refresh-bib` invoking a pipeline in a repo this project does not own
  - three HTTP paths that never reached the health ledger
  - two scripts referenced in four docs after being deleted

Every one of those is a claim about how the parts connect, and every one is checkable
in under a second without touching the network. That is what this file is: no mocks,
no fixtures, no coverage target. It answers one question -- *would `python update.py`
even get off the ground* -- and it is what CI runs on every push.

    python -m unittest discover -s tests        # or just: python tests/test_smoke.py

Deliberately not here: anything that fetches. A test that needs Semantic Scholar to be
up is a test that fails for reasons the committer cannot fix, and a suite that goes red
for weather is a suite people stop reading -- the same failure mode the health ledger
exists to avoid one layer up.
"""
from __future__ import annotations

import ast
import datetime
import importlib
import json
import contextlib
import copy
import io
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.parse
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

# Every module that is part of the program, by the directory it lives in. `update.py`
# is listed by hand because it is the only top-level one and importing it by filename
# needs the same path insert the file itself does.
SCRIPT_DIRS = ("scripts", "measure")
# Hand-written prose. `WORKLIST.md` is generated and checked too when it exists (see
# test_generated_worklist_links), because a bad path emitted by the worklist writer is
# exactly the sort of thing nobody notices in generated output.
DOCS = ("README.md", "SKILL.md", "RUN.md", "BACKLOG.md", "CLAUDE.md",
        "docs/RULES.md", "docs/SIDECAR.md", "docs/SETUP.md", "docs/EVIDENCE.md")


def modules() -> list[tuple[str, str]]:
    """(import name, path) for every module in the program."""
    out = [("update", os.path.join(ROOT, "update.py"))]
    for d in SCRIPT_DIRS:
        for f in sorted(os.listdir(os.path.join(ROOT, d))):
            if f.endswith(".py") and not f.startswith("_"):
                out.append((f[:-3], os.path.join(ROOT, d, f)))
    return out


def source(path: str) -> str:
    with open(path, encoding="utf8") as f:
        return f.read()


class TestEveryModuleImports(unittest.TestCase):
    """The floor: a module that will not import cannot be a step.

    Worth its own test rather than relying on `--help` below, because the failure
    messages are completely different -- a NameError at import time is a typo, and a
    subprocess exiting 1 is anything at all.
    """

    def test_imports(self):
        # measure/ shares module names with nothing, but it is not on sys.path, so add
        # it here rather than making the modules themselves care where they are run from.
        sys.path.insert(0, os.path.join(ROOT, "measure"))
        sys.path.insert(0, ROOT)
        for name, path in modules():
            with self.subTest(module=name):
                try:
                    importlib.import_module(name)
                except Exception as e:                              # noqa: BLE001
                    self.fail(f"{os.path.relpath(path, ROOT)} does not import: "
                              f"{type(e).__name__}: {e}")


class TestEveryJsonFileIsWrittenThroughOnePlace(unittest.TestCase):
    """`common.write_json` creates the directory, so no caller has to remember to.

    There were nineteen `os.makedirs(BUILD, exist_ok=True)` lines guarding a `json.dump`,
    two of which also leaked the file handle. A new one is a missing directory away from a
    step that fails on a fresh clone, which is exactly what CI does not have.
    """

    def test_nothing_but_common_calls_json_dump(self):
        for name, path in modules():
            if os.path.basename(path) == "common.py":
                continue
            with self.subTest(module=name):
                self.assertNotIn("json.dump(", source(path),
                                 "write the file with common.write_json instead")


class TestNoSyntaxWarnings(unittest.TestCase):
    """Compile every module with the syntax warnings promoted to errors.

    Added because writing the config scan below surfaced `\\COL` inside a non-raw
    docstring in `common.py` -- an invalid escape sequence, silent on this interpreter,
    a `SyntaxWarning` on 3.12, and an error in some later one. Nothing in the project
    was watching for it, and it is the cheapest possible check: the compiler already
    knows, it just had nobody to tell.
    """

    def test_compiles_clean(self):
        import warnings
        for name, path in modules():
            with self.subTest(module=name), warnings.catch_warnings():
                warnings.simplefilter("error", SyntaxWarning)
                warnings.simplefilter("error", DeprecationWarning)
                try:
                    compile(source(path), path, "exec")
                except (SyntaxWarning, DeprecationWarning) as e:
                    self.fail(f"{os.path.relpath(path, ROOT)}: {e}")


class TestEveryCliAnswersHelp(unittest.TestCase):
    """`--help` exercises argparse construction, which import alone does not.

    Only the modules that actually build a parser. `identity_tasks.py` takes no
    arguments and has a `__main__` guard, so passing it `--help` would not print help
    -- it would regenerate every payload under `tasks/`. Detecting the parser from the
    source is the difference between a test and a side effect.
    """

    def test_help(self):
        for name, path in modules():
            if "add_argument" not in source(path):
                continue
            with self.subTest(module=name):
                r = subprocess.run([sys.executable, path, "--help"], cwd=ROOT,
                                   capture_output=True, text=True, timeout=120)
                self.assertEqual(r.returncode, 0,
                                 f"{os.path.relpath(path, ROOT)} --help exited "
                                 f"{r.returncode}:\n{r.stderr[-2000:]}")
                self.assertIn("usage", r.stdout.lower(),
                              f"{os.path.relpath(path, ROOT)} --help printed no usage")


class TestUpdateWiring(unittest.TestCase):
    """`STEPS` and the `step_*` functions have to agree, in both directions.

    A name in `STEPS` with no function is a crash on `--step`; a function with no name
    in `STEPS` is a step that silently never runs in a full pass, which is the worse of
    the two because nothing reports it.
    """

    def setUp(self):
        sys.path.insert(0, ROOT)
        self.update = importlib.import_module("update")
        self.tree = ast.parse(source(os.path.join(ROOT, "update.py")))

    def test_steps_have_functions(self):
        for name in self.update.STEPS:
            self.assertTrue(callable(getattr(self.update, f"step_{name}", None)),
                            f"STEPS names {name!r} but there is no step_{name}()")

    def test_functions_are_in_steps(self):
        defined = {n.name[5:] for n in ast.walk(self.tree)
                   if isinstance(n, ast.FunctionDef) and n.name.startswith("step_")}
        self.assertEqual(defined, set(self.update.STEPS),
                         "step_* functions and STEPS disagree; the difference is a step "
                         "that never runs or a name that crashes --step")

    def test_step_order_is_the_documented_one(self):
        # The order is load-bearing: `links` reuses the full text `draft` cached,
        # `validate` must precede `render` so a schema failure cannot produce a page
        # that looks reviewable, and `worklist` is last because it reports on all of it.
        self.assertLess(self.update.STEPS.index("validate"),
                        self.update.STEPS.index("render"))
        self.assertEqual(self.update.STEPS[-1], "worklist")


class TestReferencedScriptsExist(unittest.TestCase):
    """Every `scripts/x.py` named anywhere -- code, prose, generated output -- is real.

    This is the test that would have caught deleting a script that four documents still
    told the reader to run. It covers prose deliberately: a command in RUN.md is not
    documentation of the program, it is an instruction someone will paste, so a stale
    one is a broken feature and not a typo.
    """

    PAT = re.compile(r"\b((?:scripts|measure)/[A-Za-z_][A-Za-z0-9_]*\.py)")

    def files(self):
        for name, path in modules():
            yield path
        for d in DOCS + ("WORKLIST.md",):
            p = os.path.join(ROOT, d)
            if os.path.exists(p):
                yield p
        tasks = os.path.join(ROOT, "tasks")
        for f in sorted(os.listdir(tasks)) if os.path.isdir(tasks) else []:
            if f.endswith(".md"):
                yield os.path.join(tasks, f)

    def test_all_exist(self):
        bad = []
        for path in self.files():
            for ref in sorted(set(self.PAT.findall(source(path)))):
                if not os.path.exists(os.path.join(ROOT, ref)):
                    bad.append(f"{os.path.relpath(path, ROOT)} -> {ref}")
        self.assertEqual(bad, [], "references to scripts that do not exist:\n  "
                                  + "\n  ".join(bad))


class TestDocLinksResolve(unittest.TestCase):
    """Relative markdown links in the hand-written docs point at files that exist.

    Only relative ones: an external URL that rots is a fact about the internet and
    belongs to the health ledger, not to a test that must pass offline.
    """

    PAT = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")

    def links(self, doc: str):
        base = os.path.dirname(os.path.join(ROOT, doc))
        for target in self.PAT.findall(source(os.path.join(ROOT, doc))):
            if re.match(r"^(https?:|mailto:|#)", target):
                continue
            yield target, os.path.normpath(os.path.join(base, target.split("#")[0]))

    def test_targets_exist(self):
        bad = [f"{doc} -> {target}" for doc in DOCS
               for target, path in self.links(doc) if not os.path.exists(path)]
        self.assertEqual(bad, [], "dangling relative links:\n  " + "\n  ".join(bad))

    def test_anchors_exist(self):
        """A `#section` that no heading produces lands the reader at the top silently.

        Slugified the way GitHub does it -- lowercase, drop everything that is not
        alphanumeric, space or hyphen, spaces to hyphens -- which is why an em-dash in a
        heading leaves a double hyphen in the anchor.
        """
        def slugs(path):
            out = set()
            for line in source(path).splitlines():
                if m := re.match(r"#{1,6}\s+(.*)", line):
                    t = re.sub(r"[^\w\s-]", "", m.group(1).lower(), flags=re.UNICODE)
                    out.add(re.sub(r"\s", "-", t.strip()))
            return out

        bad = []
        for doc in DOCS:
            for target, path in self.links(doc):
                if "#" not in target or not os.path.exists(path):
                    continue
                anchor = target.split("#", 1)[1]
                if path.endswith(".md") and anchor not in slugs(path):
                    bad.append(f"{doc} -> {target}")
        self.assertEqual(bad, [], "links to headings that do not exist:\n  "
                                  + "\n  ".join(bad))


class TestGeneratedWorklistLinks(unittest.TestCase):
    """The same link check against `WORKLIST.md`, which is written by code.

    Separate from the doc test because this one is about the emitter, not the prose: the
    paths in the worklist are built by string concatenation in `update.py`, including one
    long `docs/SETUP.md#...` anchor split across two source lines.
    """

    def test_links(self):
        path = os.path.join(ROOT, "WORKLIST.md")
        if not os.path.exists(path):
            self.skipTest("WORKLIST.md not generated yet")
        bad = []
        for target in TestDocLinksResolve.PAT.findall(source(path)):
            # `file:` is skipped and not resolved: the only one is the sidecar review
            # page, which lives under the gitignored `build/`, so it is absent from a
            # fresh clone and from CI while the worklist that links it is committed.
            # Asserting it exists would fail everywhere except the machine that last ran
            # `update.py`. `test_the_review_page_link_is_the_path_the_code_writes` covers
            # the failure this one cannot -- the emitter pointing somewhere wrong.
            if re.match(r"^(https?:|mailto:|file:|#)", target):
                continue
            if not os.path.exists(os.path.join(ROOT, target.split("#")[0])):
                bad.append(target)
        self.assertEqual(bad, [], f"WORKLIST.md links to missing files: {bad}")

    def test_the_review_page_link_is_the_path_the_code_writes(self):
        """The one link in the worklist that no existence check can reach.

        It is built by concatenation in `update.py` and consumed by a human clicking it,
        so a stale or misspelled path fails silently -- the click opens nothing and the
        review does not happen. Comparing against the constant catches the two ways that
        happens: the emitter drifting, and the page moving.
        """
        path = os.path.join(ROOT, "WORKLIST.md")
        if not os.path.exists(path):
            self.skipTest("WORKLIST.md not generated yet")
        import sidecar_review
        text = source(path)
        links = re.findall(r"file://(\S*?)[)>#]", text)
        for got in links:
            self.assertEqual(got, sidecar_review.REVIEW_PAGE,
                             "the worklist links a file:// path that is not the review "
                             "page the drafter writes")
        # Without this the test passes on a worklist that dropped the link entirely,
        # which is the same failure as linking the wrong path: nothing to click.
        if "## Sidecar drafts awaiting" in text:
            self.assertTrue(links, "a section asks for a sidecar review but links no "
                                   "review page, so reading means running --show per paper")


class TestWorkflowsInvokeRealCommands(unittest.TestCase):
    """Every `python …` line in a workflow names a real script and real flags.

    A workflow is the one caller nobody runs by hand, so a stale flag in one sits there
    until the monthly run fails at 06:37 on a morning nobody is looking. Writing these
    files produced exactly that bug twice -- `sweep_github.py apply` silently needs
    `--yes`, and a first draft called the script directly instead of going through
    `update.py --apply`, which would have skipped the Hugging Face half of the same job.

    Flags are checked against `add_argument` in the target's source rather than by running
    it: this has to work offline, and `--help` is already covered above.
    """

    CMD = re.compile(r"\bpython3? ((?:scripts/|measure/)?[\w/]+\.py)([^\n|;&]*)")

    def workflows(self):
        d = os.path.join(ROOT, ".github", "workflows")
        for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            if f.endswith((".yml", ".yaml")):
                yield os.path.join(d, f)

    def test_parse(self):
        import yaml
        for path in self.workflows():
            with self.subTest(workflow=os.path.basename(path)):
                doc = yaml.safe_load(source(path))
                self.assertIn("jobs", doc)
                # YAML 1.1 reads a bare `on:` key as the boolean True. Harmless to Actions,
                # confusing to anything else that reads these files, so assert the trigger
                # is found under one of the two spellings rather than only the string.
                self.assertTrue(doc.get("on") or doc.get(True), f"{path}: no triggers")

    def test_commands_and_flags(self):
        bad = []
        for path in self.workflows():
            body = re.sub(r"\$\{\{[^}]*\}\}", "STUB", source(path))
            for script, rest in self.CMD.findall(body):
                where = f"{os.path.basename(path)}: python {script}"
                target = os.path.join(ROOT, script)
                if not os.path.exists(target):
                    bad.append(f"{where} -- no such file")
                    continue
                known = source(target)
                for flag in re.findall(r"(?<!\w)--[a-z][a-z0-9-]*", rest):
                    if f'"{flag}"' not in known and f"'{flag}'" not in known:
                        bad.append(f"{where} {flag} -- not an argument of that script")
        self.assertEqual(bad, [], "workflows call things that do not exist:\n  "
                                  + "\n  ".join(bad))

    def test_requirements_covers_what_the_workflows_install(self):
        """The dependency list is one file, and the workflows install from it.

        `pip install <name>` written straight into a workflow is how a dependency ends up
        declared in two places and then in neither. One exception is allowed and is named
        in requirements.txt itself, because it is only needed by one optional path.
        """
        reqs = source(os.path.join(ROOT, "requirements.txt"))
        for path in self.workflows():
            for line in source(path).splitlines():
                if m := re.search(r"pip install (?!-r )([\w-]+)", line):
                    self.assertIn(m.group(1), reqs,
                                  f"{os.path.basename(path)} installs {m.group(1)!r} but "
                                  f"requirements.txt does not mention it")


class TestPromptsCarryTheirRules(unittest.TestCase):
    """The docs that are program input still contain a prompt block.

    `validate.py` checks this too, and on purpose: there it fails the run that made the
    edit, here it fails the push. The failure being caught twice is the point -- a doc
    edit that empties a prompt produces drafts written against no rules at all, and
    nothing about the output looks wrong.
    """

    def test_blocks(self):
        from common import rules_block
        from validate import PROMPT_DOCS
        for doc, what, reader in PROMPT_DOCS:
            with self.subTest(doc=doc):
                self.assertGreater(len(rules_block(doc)), 200,
                                   f"{doc} ({what}) has no usable prompt block; "
                                   f"{reader} reads it")

    def test_the_index_above_the_block_has_a_row_per_step(self):
        """§2's index is an index, and an index that has drifted is worse than none.

        It exists because the prompt is one long block and a reader could not see what
        step 4 was for without reading step 4. The cost of that convenience is a second
        place where the steps are listed, so the count is checked rather than trusted:
        a tenth step added to the prompt fails here until it appears in the table.
        """
        from common import ROOT, rules_block
        with open(os.path.join(ROOT, "docs", "SIDECAR.md"), encoding="utf-8") as fh:
            head = fh.read().split("<!-- prompt:start -->")[0]
        # From the index's own header, so the pipeline table further up -- also numbered
        # rows, also above the block -- is not mistaken for it.
        head = head.split("| Step | Writes |")[-1]
        steps = re.findall(r"^\*\*(\d+)\.", rules_block("docs/SIDECAR.md"), re.M)
        rows = re.findall(r"^\| (\d+) \|", head, re.M)
        self.assertEqual(steps, rows,
                         f"§2's prompt has steps {steps} and its index lists {rows}")


class TestOneBadPaperCannotEndTheRun(unittest.TestCase):
    """A drafting run is durable per paper, and that only means something if the paper
    that cannot be written is the only casualty. A reply with `claims` as a JSON string
    raised inside validate_draft and ended a 96-paper pass 55 papers in."""

    def test_handed_survives_a_failing_draft(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import draft_sidecars as D
        seen = []

        def on_draft(slug, sc, how, ask):
            seen.append(slug)
            if slug == "bad":
                raise AttributeError("'str' object has no attribute 'get'")

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            for slug in ("first", "bad", "third"):
                D.handed(on_draft, slug, {}, "a model", None)
        self.assertEqual(seen, ["first", "bad", "third"], "the run stopped at the bad paper")
        self.assertIn("--slug bad", buf.getvalue(),
                      "a paper that could not be written has to say how to re-draft it")

    def test_a_json_string_array_is_recovered(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import sidecar_io as D
        claims = [{"id": "a", "kind": "result", "text": "x", "scope": "y",
                   "evidence": "Table 1"}]
        got = D.unstructure({"claims": json.dumps(claims)}, D.schema())
        self.assertEqual(got["claims"], claims)
        # Not recoverable is not the same as recovered wrongly: it stays put and stays a
        # finding rather than becoming a guess.
        self.assertEqual(D.unstructure({"claims": "prose, not JSON"},
                                       D.schema())["claims"], "prose, not JSON")


class TestFindingsCollapseToTheRuleTheyBroke(unittest.TestCase):
    """`--review` counts findings by rule, and the counting is only useful if two
    instances of one rule collapse to one line. Every part of a finding that names the
    instance -- the draft's path, the claim id, the character counts, the ids listed after
    the fix -- has to come off, and an earlier version that split on the first colons left
    a row that was nothing but a list of claim ids."""

    SAME = [
        ["a.md: claim 'one': a 43-word sentence (max 32) -- split it, the front of a claim",
         "b.md: claim 'two': a 51-word sentence (max 32) -- split it, the front of a claim"],
        ["a.md: page: only 4 of 11 result claims state a figure (want 50%) -- go back to "
         "the tables. Number-free: alpha, beta, gamma",
         "b.md: page: only 2 of 9 result claims state a figure (want 50%) -- go back to "
         "the tables. Number-free: delta"],
        ["a.md: claim 'x': scope is longer than the claim it bounds (410 vs 300 chars) -- cut",
         "b.md: claim 'y': scope is longer than the claim it bounds (900 vs 120 chars) -- cut"],
    ]

    def test_one_rule_is_one_row(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        from sidecar_repair import rule_of
        for group in self.SAME:
            got = {rule_of(f) for f in group}
            self.assertEqual(len(got), 1, f"one rule split into {got}")
            rule = got.pop()
            self.assertNotIn(".md", rule, f"the draft path survived into {rule!r}")
            self.assertTrue(rule.strip(), "the rule collapsed to nothing")
        self.assertNotEqual(rule_of(self.SAME[0][0]), rule_of(self.SAME[2][0]),
                            "two different rules collapsed into one row")


class TestEveryCheckSurvivesAnOffSchemaDraft(unittest.TestCase):
    """No accept-time check may raise on a draft whose fields are the wrong type.

    A forced tool call returns whatever it returns, and the schema is checked after the
    reply is already on disk -- so every check reads documents the schema would reject.
    This has now bitten twice. `terminology` came back as a list, and `readability` raised
    AttributeError; the guard I added for it suppressed the whole tier, which was worse.
    Then `terminology` came back as a string and `readability` raised again, this time
    taking the review page down and leaving a zero-byte file where the previous good page
    had been.

    The shape of the fix that lasts is not a wider try/except -- it is that a check reports
    a wrong type instead of dying on it, which is what `check_sidecar_shape` is for. So
    this feeds each check every field wrong-typed at once and asks only that it return.
    """

    HOSTILE = [
        {"one_liner": ["a", "list"], "claims": "not a list", "qa": {"a": "dict"},
         "misreadings": "a string", "terminology": "a string"},
        {"one_liner": None, "claims": [None, "text", 7], "qa": ["a string"],
         "misreadings": [{"text": "an object"}], "terminology": ["a", "list"]},
        {"claims": [{"id": None, "text": None, "scope": 3, "evidence": []}],
         "qa": [{"ask": None, "answered_by": "not a list"}], "terminology": {"t": None}},
        {},
    ]

    def test_no_check_raises(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import validate as V
        checks = [("readability", lambda e: V.readability(e[0][1])),
                  ("check_sidecar_shape", V.check_sidecar_shape),
                  ("check_claim_numbers", V.check_claim_numbers),
                  ("check_claim_evidence", V.check_claim_evidence)]
        for i, fm in enumerate(self.HOSTILE):
            entry = [("a-paper.md", fm)]
            for name, run in checks:
                try:
                    run(entry)
                except Exception as e:                       # noqa: BLE001 -- the point
                    self.fail(f"{name} raised {type(e).__name__} on hostile draft {i} "
                              f"({e}) -- report the wrong type, do not raise on it")


class TestTheReadabilityRulesStillFire(unittest.TestCase):
    """The one tier `validate.py --strict` cannot cover, covered here instead.

    `check_readability` runs only at `--accept` and on the review page, because
    `validate.py` reads the author's published sidecars and a long sentence there is not
    a reason to retract a page. That exemption is also how the tier could quietly stop
    working: nothing in the committed data has to violate it, so no run would notice a
    regex that stopped matching. So the fixtures below are the rules -- one sidecar that
    breaks each, one that breaks none.
    """

    BAD = {
        "claims": [{
            "id": "overloaded",
            # 43 words, which is the median of the 324 drafted claims, in one sentence
            # with three findings stacked behind separators -- the exact drafted shape.
            "text": "The method raises exact-match accuracy by 4.6 points over the "
                    "fine-tuned baseline on the WMT16 English-German test set, and the "
                    "gain holds at every model scale tested: it is largest at 7B, "
                    "smallest at 125M, and absent below that -- which is the pattern "
                    "the authors attribute to capacity rather than to data.",
            "scope": "This is a description of the published algorithm, so it is as "
                     "reliable as reading it. Holds for encoder-decoder models only.",
        }, {
            "id": "about-the-paper",
            # Rule 2's self-containment bullet, which nothing enforced until the GEO
            # pass, plus a scope longer than the claim and one condition over the cap.
            "text": "The paper proves the reward is maximised by the wanted behaviour.",
            "scope": "Bounded scoring rules only, and only for the two-outcome case. "
                     "Verified numerically at five arms and at ten. The extension to "
                     "continuous outcomes is not attempted anywhere in the paper. "
                     "Nothing is claimed about unbounded rules.",
        }, {
            "id": "first-person",
            "text": "We find that merged models trail multitask training.",
            # The trailing clause is the whole of rule 31: a condition, then the claim
            # said a second time in the field that exists to bound it.
            "scope": "Vision encoders only, demonstrating the benefits of merging.",
        }, {
            "id": "names-the-analysis",
            # Rule 32: where the result lives is `evidence`, and this bounds nothing.
            # No figure in the text, so the page-level coverage rule still fires: three of
            # the four result claims here are meant to be missing their magnitude.
            "text": "Trimming the smallest parameter changes leaves merged accuracy "
                    "unchanged on the eleven-task suite.",
            "scope": "the analysis of redundant parameters and their impact on merging.",
        }, {
            "id": "enumerates",
            # Rule 33, and the shape it actually arrives in: the abstract's contributions
            # bullet, which is one sentence and so slips past the sentence-count cap.
            "text": "The key contributions are: (1) a method that aligns task updates "
                    "from separately finetuned models, and (2) a benchmark that measures "
                    "whether the merged model is general.",
            "scope": "LoRA adapters over eight vision datasets, merged without any "
                     "held-out data to tune the merge on.",
        }],
        # Rule 34: the same sentence published twice, once as the page's description and
        # once as a claim. Copied off `enumerates` so one fixture claim carries both.
        "one_liner": "The key contributions are: (1) a method that aligns task updates "
                     "from separately finetuned models, and (2) a benchmark that measures "
                     "whether the merged model is general.",
        # One of three result claims carries a figure, so the page-level rule fires too.
        "qa": [{"ask": {"plain": "How much data does it take to fit a model like this?",
                        "jargon": "Was this validated on more than one dataset?",
                        "task": "What do the authors recommend?"},
                "answered_by": ["overloaded"]}],
        "misreadings": ["Low agreement here is not weak annotation."],
        "terminology": {"normalized accuracy": "The metric for every merging table here."},
    }
    GOOD = {
        "one_liner": "A trimming rule and a sign vote let several fine-tuned models be "
                     "averaged without the largest updates cancelling each other out.",
        "claims": [{
            "id": "clean",
            "text": "The method raises exact-match accuracy by 4.6 points over the "
                    "fine-tuned baseline on the WMT16 English-German test set. The gain "
                    "is largest at 7B and absent below 125M parameters.",
            "scope": "Encoder-decoder models above 125M parameters; no effect measured "
                     "below that, and only the WMT16 English-German pair was tested.",
        }],
        "qa": [{"ask": {"plain": "How much data does it take to fit a latent-skill "
                                 "model of arena outcomes?",
                        "jargon": "Was the WMT16 result replicated on another language "
                                  "pair?"},
                "answered_by": ["clean"]}],
    }

    def test_each_rule_catches_its_own_violation(self):
        from validate import check_readability
        found = " ".join(check_readability([("bad.md", self.BAD)]))
        for want, rule in (("-word sentence", "the sentence-length cap"),
                           ("stacked colons", "the separator cap"),
                           ("classifying the claim", "the scope-opening rule"),
                           ("like this", "the unbound-reference rule"),
                           ("leans on 'The paper'", "the claim self-containment rule"),
                           ("leans on 'We'", "the same rule on first person"),
                           ("scope is 4 sentences", "the scope condition cap"),
                           ("longer than the claim it bounds", "the scope proportion rule"),
                           ("comments on what the result shows", "the scope-restatement rule"),
                           ("names the analysis the claim came from",
                            "the scope-names-the-analysis rule"),
                           ("text enumerates", "the enumerated-claim rule"),
                           ("`one_liner` is claim", "the one-liner-is-not-a-claim rule"),
                           ("result claims state a figure", "the page-level figure rule"),
                           ("define what the word means", "the terminology deixis rule"),
                           ("nothing to point at", "the misreading deixis rule")):
            with self.subTest(rule=rule):
                self.assertIn(want, found, f"{rule} stopped firing: {found!r}")

    def test_a_clean_sidecar_is_left_alone(self):
        """The half that decides whether the rules are usable rather than just strict.

        A check that fires on well-written text is one the author overrides with
        `--anyway` every time, and then the tier is decoration.
        """
        from validate import check_readability
        self.assertEqual(check_readability([("good.md", self.GOOD)]), [])

    def test_a_pronoun_with_an_antecedent_is_not_a_finding(self):
        """The distinction the rule is actually about, and the one easy to over-enforce.

        "their" here points at "adapters", inside the question -- so the question stands
        alone and banning it would push the drafter into stilted English for nothing.
        """
        from validate import check_readability
        ok = {"qa": [{"ask": {"plain": "How do you merge LoRA adapters without mixing "
                                       "up their factorizations?",
                              "practitioner": "Can I compare two models by their skill "
                                              "profile?"}}]}
        self.assertEqual(check_readability([("ok.md", ok)]), [])

    def test_a_misreading_may_still_say_what_the_paper_does_not_state(self):
        """Why `_DEIXIS_MISREADING` is narrower than `_DEIXIS_TERM`, in a test.

        A correction's whole job can be to say what the paper leaves open, so "the paper"
        is load-bearing there and only the words with no possible referent are barred. A
        definition is the opposite case: it is published as a `DefinedTerm` inside a set
        already titled after the paper, so naming the paper is both dangling and
        redundant.
        """
        from validate import check_readability
        ok = {"misreadings": ["The dataset contains matches involving human players, and "
                              "the paper does not state whether they were used."]}
        self.assertEqual(check_readability([("ok.md", ok)]), [])

    def test_a_scope_may_say_what_a_result_shows_about_a_condition(self):
        """Why rule 31's noun list is closed, in a test.

        "shows no effect below 1B" is the shape the rule exists to get instead of a
        restatement, and it opens with the same verb -- so a catch-all after any showing
        verb would flag the model answer as the pathology.
        """
        from validate import check_readability
        ok = {"claims": [{"id": "c", "kind": "result",
                          "text": "Merging raises accuracy by 4.6 points on WMT16 "
                                  "English-German over the fine-tuned baseline.",
                          "scope": "Encoder-decoder models at 7B, which shows no effect "
                                   "below 125M parameters and was tested on one pair."}]}
        self.assertEqual(check_readability([("ok.md", ok)]), [])

    def test_a_bare_definite_is_caught_and_a_named_subject_is_not(self):
        """The subtlest form of the unbound-reference rule, and its escape hatch.

        "Is there a guarantee that the estimator is correct?" has no demonstrative and no
        pronoun, so every other rule passes it, and *which* estimator is the whole
        question. The escape hatch matters as much as the rule: the moment a question
        names something a query would contain, "the method" has a referent on screen, and
        firing anyway would push a drafter toward vaguer questions rather than sharper
        ones.
        """
        from validate import check_readability
        bad = {"qa": [{"ask": {"plain": "Is there a guarantee that the estimator is "
                                        "correct?",
                               "jargon": "How does the approach handle ties?"}}]}
        found = " ".join(check_readability([("bad.md", bad)]))
        for want in ("'the estimator' has no antecedent", "'the approach' has no antecedent"):
            with self.subTest(want=want):
                self.assertIn(want, found)
        ok = {"qa": [{"ask": {"plain": "Does the anchor-point method apply to prompt "
                                       "selection?",
                              "practitioner": "Do the models I merge have to be related "
                                              "to my task?",
                              "jargon": "What do the authors of Global-MMLU recommend?",
                              "task": "Is it enough to train only the B matrix in "
                                      "LoRA?"}}]}
        self.assertEqual(check_readability([("ok.md", ok)]), [])

    def test_a_generic_definite_about_a_reader_s_own_model_is_not_a_reference(self):
        """The nouns that mean "this paper's one" are flagged; the generic ones are not.

        The list used to hold model, task, corpus, dataset, benchmark and score, and on the
        rerouted corpus that fired 68 times on ordinary English -- "help the model
        generalize" means *a* model. It also fought the `plain` role head-on, because the
        escape hatch keys on a capitalised token and `plain` is forbidden to carry a coined
        name, so the sharpest plain phrasings were the ones it flagged.
        """
        from validate import check_readability
        ok = {"qa": [{"ask": {
            "plain": "Does training only one of a low-rank adapter's two matrices help "
                     "the model generalize?",
            "task": "how do I set up a confidence reward so the model cannot game it by "
                    "giving up on the answer?",
            "jargon": "does agreement between benchmarks depend on whether the models "
                      "compared are weak or state of the art?",
            "practitioner": "how do I stop my correlation numbers from swinging around "
                            "when I change the setup?"}}]}
        self.assertEqual(check_readability([("ok.md", ok)]), [])

    def test_a_noun_already_in_the_question_is_its_own_antecedent(self):
        """A demonstrative eight words after the noun it points at is bound, not dangling."""
        from validate import check_readability
        ok = {"qa": [{"ask": {
            "plain": "if a model of game results uses several hidden abilities, are those "
                     "abilities pinned down uniquely?",
            "jargon": "how does resolving cross-task interference change sensitivity to "
                      "merging hyperparameters, and can those hyperparameters be tuned on "
                      "unlabeled data?"}}]}
        self.assertEqual(check_readability([("ok.md", ok)]), [])
        # ...and a demonstrative with nothing before it still fails.
        bad = {"qa": [{"ask": {"plain": "do these layer shortcuts only work on one small "
                                        "model?"}}]}
        self.assertTrue(check_readability([("bad.md", bad)]))

    def test_a_claim_that_only_describes_construction_is_caught(self):
        """Rule 30, and the two things it must not do.

        A `result` claim walking through how a component is assembled answers no query --
        the reader who would type its words has already read the paper. The rule is a
        small allowlist of construction frames rather than the absence of a finding,
        because the absence test misclassifies findings: measured over every sidecar here,
        "no figure and no comparative" flags a proved consistency theorem. So the two
        negative cases below are the design, not leniency -- a mechanism sentence that
        also states an outcome is a claim, and a `context` claim's job is to say what the
        work is.
        """
        from validate import check_readability
        bad = {"claims": [{
            "id": "pipeline",
            "text": "Q2 works in three steps: mark every named entity in the response as "
                    "an informative span, generate a question for each, and answer it "
                    "against the knowledge the response was grounded in.",
            "scope": "Knowledge-grounded dialogue with a written grounding document, and "
                     "English responses only.",
        }]}
        self.assertIn("describes how the thing is built",
                      " ".join(check_readability([("bad.md", bad)])))
        ok = {"claims": [{
            "id": "asserts-an-outcome",
            "text": "RLCR consists of a correctness reward plus a Brier-score term, and it "
                    "improves calibration error by 12 points without costing accuracy.",
            "scope": "Two reasoning benchmarks at 7B, with the confidence read from the "
                     "model's own stated number rather than from its logits.",
        }, {
            "id": "context-may-say-what-the-work-is",
            "kind": "context",
            "text": "Q2 is the reference for automatic factual-consistency evaluation of "
                    "knowledge-grounded dialogue, and it consists of question generation "
                    "followed by question answering.",
            "scope": "As of publication in 2021, for English dialogue grounded in a "
                     "written document; nothing in the paper certifies this positioning.",
        }]}
        self.assertEqual([f for f in check_readability([("ok.md", ok)])
                          if "describes how" in f], [])


class TestARepairRoundCannotAnswerWithAnEmptySidecar(unittest.TestCase):
    """Deleting the claims satisfies almost every check, and used to score as a fix.

    Live case, `on-the-weaknesses-of-reinforcement-learning-for-neural-machi`: round 1 was
    shown 17 findings and replied with a sidecar holding none of the paper's 12 claims and
    none of its 8 question groups. That scores 2 -- 'claims' is required, and there are no
    question groups -- so the loop kept it and stopped, and a finished draft became an
    empty one nobody would have noticed until they opened it.
    """

    def test_a_collapsed_reply_is_named_and_refused(self):
        import sidecar_repair as D
        full = {"claims": [{"id": str(i)} for i in range(12)],
                "qa": [{"ask": {"plain": "a?", "jargon": "b?"}} for _ in range(8)]}
        self.assertIsNone(D.shrunk(full, full))
        # Merging two overlapping claims is a legitimate fix, so it must still pass.
        self.assertIsNone(D.shrunk(full, {**full, "claims": full["claims"][:9]}))
        for gone, want in (({"claims": [], "qa": []}, "12 of 12 claims"),
                           ({**full, "claims": full["claims"][:2]}, "10 of 12 claims"),
                           ({**full, "qa": []}, "8 of 8 qa")):
            with self.subTest(want=want):
                self.assertEqual(want, D.shrunk(full, gone))

    def test_the_loop_keeps_the_draft_it_was_given(self):
        import sidecar_io
        import sidecar_repair as D
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)
        old, sidecar_io.DRAFTS = sidecar_io.DRAFTS, tmp
        self.addCleanup(lambda: setattr(sidecar_io, "DRAFTS", old))
        sidecar = copy.deepcopy(TestATargetedRepairTouchesOnlyWhatBroke.SIDECAR)
        path = D.write_draft("a-paper", sidecar, "a fake model")
        was = open(path, encoding="utf-8").read()

        def again(prompt, label, want=None):
            return {"one_liner": sidecar["one_liner"], "claims": [], "qa": []}

        again.window = 0
        D.repair("a-paper", 3, again, "", "a fake model")
        self.assertEqual(was, open(path, encoding="utf-8").read(),
                         "the collapsed reply must not reach the file at all")


class TestEveryFindingNamesSomethingFixable(unittest.TestCase):
    """A finding a rewrite cannot clear costs a repair round and gets reverted.

    Both cases below were found by `--mend`, which reverts a rewrite that does not clear
    its own complaint and so surfaces the complaints that nothing can clear. They are
    checker bugs, not model failures: one counted a name's initial as a sentence boundary,
    the other told the model to remove a string the field did not contain.
    """

    def test_an_initial_is_not_the_end_of_a_sentence(self):
        import validate as V
        two = ("Project Debater's public debut on 11 February 2019 debated debate champion "
               "H. Natarajan on whether preschool should be subsidized. The pre-debate "
               "audience vote was 79% in favour.")
        self.assertEqual(2, len(V.sentences(two)),
                         "a two-sentence claim reported as three is unfixable: the only "
                         "rewrite that clears it drops the person's initial")
        self.assertEqual(2, len(V.sentences("Merging helps, see Fig. 3 for the per-task "
                                            "breakdown. It does not help below 125M.")))
        # Still splits where a reader pauses, which is the whole point of the cap.
        self.assertEqual(3, len(V.sentences("One thing. Then another! And a third?")))

    def test_the_coined_name_check_names_the_string_that_has_to_go(self):
        import validate as V
        fm = {"coined": "Global-MMLU", "gloss": "A multilingual MMLU with cultural "
                                                "sensitivity labels.",
              "claims": [],
              "qa": [{"ask": {"plain": "What fraction of MMLU questions need cultural "
                                       "knowledge?",
                              "jargon": "Is MMLU culturally biased?"}}]}
        found = [f for f in V.check_sidecar_shape([("d.md", fm)])
                 if "every phrasing" in f]
        self.assertTrue(found)
        # It matched the acronym part, so that is what it must name -- and it must be
        # readable, not the check's own lowercased tokens.
        self.assertIn("'MMLU' (part of 'Global-MMLU')", found[0])
        self.assertNotIn("m m l u", found[0])


class TestATargetedRepairTouchesOnlyWhatBroke(unittest.TestCase):
    """`--mend` sends the model the offending fields and splices its rewrites back.

    Whole-sidecar repair plateaus, and the plateau has a mechanism: the model is handed the
    entire draft and returns an entire draft, so a round can break a claim it was not asked
    about while fixing the one it was, and the loop then stops because the count stopped
    falling. Measured over 35 papers: 18 kept a residue, and 9 of those stopped on exactly
    that plateau. Here the reply cannot reach a field that was not complained about -- so
    the invariants worth testing are that the locus map keeps pointing at the right strings,
    that a splice leaves every other byte alone, and that a patch which does not help is
    thrown away rather than written.
    """

    SIDECAR = {
        "one_liner": "A trimming rule and a sign vote let several fine-tuned models be "
                     "averaged without the largest updates cancelling each other out.",
        "claims": [{
            "id": "too-long",
            # 37 words in one sentence: the single most common finding in the corpus.
            "text": "The method raises exact-match accuracy by 4.6 points over the "
                    "fine-tuned baseline on the WMT16 English-German test set, and the "
                    "gain holds at every model scale tested, being largest at 7B and "
                    "absent below 125M parameters everywhere.",
            "scope": "Encoder-decoder models above 125M parameters; no effect measured "
                     "below that, and only the WMT16 English-German pair was tested.",
        }, {
            "id": "clean",
            "text": "Trimming the smallest parameter changes leaves merged accuracy "
                    "unchanged. The eleven-task suite shows no drop of 0.2 points or more.",
            "scope": "LoRA adapters over eight vision datasets, merged without any "
                     "held-out data to tune the merge on.",
        }],
        "qa": [{"ask": {"plain": "How much data does it take to fit a model like this?",
                        "jargon": "Was this validated on more than one dataset?"},
                "answered_by": ["clean"]}],
        "misreadings": ["Low agreement here is not weak annotation."],
        "terminology": {"normalized accuracy": "The metric for every merging table here."},
    }
    SPLIT = ("The method raises exact-match accuracy by 4.6 points over the fine-tuned "
             "baseline on the WMT16 English-German test set. The gain is largest at 7B "
             "and absent below 125M parameters.")

    def setUp(self):
        import sidecar_io
        import sidecar_repair as D
        self.D = D
        self.tmp = tempfile.mkdtemp()
        self._drafts = sidecar_io.DRAFTS
        sidecar_io.DRAFTS = self.tmp
        self.addCleanup(lambda: setattr(sidecar_io, "DRAFTS", self._drafts))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.path = D.write_draft("a-paper", copy.deepcopy(self.SIDECAR), "a fake model")

    def _findings(self):
        return [str(x).split(".md: ")[-1]
                for x in sum(self.D.validate_draft(self.path, note=False), [])]

    def _asker(self, fixes):
        """A backend's request function, as `mend` uses it: called, and read for .window."""
        calls = []

        def again(prompt, label, want=None):
            calls.append((prompt, label, want))
            return {"fixes": fixes}

        again.window = 0
        return again, calls

    def test_the_locus_map_points_at_the_strings_the_checks_complain_about(self):
        """Both finding dialects, and the page-level one that must stay unaddressed."""
        fm = self.D.front_matter(self.path)
        for finding, want in [
            # Names its field.
            ("claim 'x': a 33-word sentence (max 32) -- split it", "claim/x/text"),
            ("claim 'x': text is 5 sentences (max 2)", "claim/x/text"),
            ("claim 'x': states 29, which is not in the paper's own text",
             "claim/x/text"),
            # The same check, in the wording it actually emits: no colon after the id.
            ("claim 'x' states 29, 30, which are not in the paper's own text",
             "claim/x/text"),
            ("claim 'x': text leans on 'The study' -- name the object instead",
             "claim/x/text"),
            ("claim 'x': scope is longer than the claim it bounds (205 vs 200 chars)",
             "claim/x/scope"),
            ("claim 'x': scope is 4 sentences (max 3)", "claim/x/scope"),
            # A group-level finding aims at whichever route the group leads with, read
            # off the draft -- so a finding about a group that is not there places
            # nowhere rather than at a locus the patcher would then fail to find.
            ("qa[0]: every phrasing contains 'BabyLM Interaction track'",
             "qa/0/ask/plain"),
            ("qa[7]: every phrasing contains 'BabyLM Interaction track'", None),
            ("term 'normalized accuracy': definition says 'here'",
             "term/normalized accuracy"),
            # Opens with the offending string, so it is found by looking it up.
            ("Was this validated on more than one dataset? -- 'Was this' has no "
             "antecedent in the question", "qa/0/ask/jargon"),
            ("Low agreement here is not weak annotation. -- 'here' has nothing to point "
             "at once this bullet is extracted on its own", "misreadings/0"),
            # About the set, not a field: fixing it needs the other claims in view.
            ("only 3 of 9 result claims state a figure (want 50%)", None),
            ("2 claims, outside the 5-15 band", None),
            ("no `kind: context` claim", None),
            ("1 claim(s) no question points at: too-long", None),
        ]:
            with self.subTest(finding=finding[:48]):
                self.assertEqual(want, self.D.where(finding, fm))

    def test_the_figure_floor_names_its_own_claims_and_spread_reads_them_off(self):
        """The one page-level finding with a computable set of fields, taken from its text."""
        finding = ("only 3 of 9 result claims state a figure (want 50%) -- go back to the "
                   "tables for the magnitudes these claims dropped, or fold two number-free "
                   "claims into the measured claim they are both circling. Never invent "
                   "one. Number-free: too-long, clean, third-one")
        self.assertEqual(["claim/too-long/text", "claim/clean/text",
                          "claim/third-one/text"], self.D.spread(finding))
        # Every other page-level finding stays a page-level finding.
        for other in ("2 claims, outside the 5-15 band", "no `kind: context` claim",
                      "1 claim(s) no question points at: too-long",
                      "5 of 5 claims are `kind: context`"):
            with self.subTest(finding=other):
                self.assertEqual([], self.D.spread(other))

    def test_added_magnitudes_are_kept_as_one_group_or_not_at_all(self):
        """No single added figure clears a ratio, so the group is one transaction."""
        fm = copy.deepcopy(self.SIDECAR)
        # Four result claims, one with a figure: 25%, under the floor.
        fm["claims"] = [{"id": "has-one",
                         "text": "Merging eight adapters costs 3.1 points of accuracy.",
                         "scope": "Vision adapters merged without held-out data."},
                        {"id": "bare-a", "text": "Trimming small updates leaves accuracy "
                                                 "unchanged across the suite.",
                         "scope": "Encoder-decoder models, one language pair."},
                        {"id": "bare-b", "text": "Sign agreement matters more than "
                                                 "magnitude when updates conflict.",
                         "scope": "Adapters trained from one shared checkpoint."},
                        {"id": "bare-c", "text": "The merge needs no data to tune it.",
                         "scope": "Held-out-free merging over eight vision datasets."}]
        fm["qa"] = [{"ask": {"plain": "How much accuracy does merging eight adapters "
                                      "cost?",
                             "jargon": "What does trimming small updates do to "
                                       "accuracy?"},
                     "answered_by": ["has-one", "bare-a"]}]
        self.path = self.D.write_draft("a-paper", fm, "a fake model")
        before = self._findings()
        floor = [f for f in before if "result claims state a figure" in f]
        self.assertTrue(floor, "the fixture is meant to trip the figure floor")
        self.assertEqual(["claim/bare-a/text", "claim/bare-b/text", "claim/bare-c/text"],
                         self.D.spread(floor[0]))

        again, calls = self._asker([
            {"at": "claim/bare-a/text",
             "new": "Trimming small updates leaves accuracy unchanged, within 0.2 points."},
            {"at": "claim/bare-b/text",
             "new": "Sign agreement recovers 2.4 of the 3.1 points magnitude alone loses."},
            {"at": "claim/bare-c/text",
             "new": "The merge needs 0 held-out examples to tune it."}])
        left = self.D.mend("a-paper", again, "the paper's text", "a fake model")
        got = self.D.front_matter(self.path)
        self.assertEqual([], [f for f in self._findings()
                              if "result claims state a figure" in f])
        self.assertEqual(len(before) - 1, left, "the floor cleared, nothing else broke")
        self.assertIn("0.2 points", self.D.at(got, "claim/bare-a/text"))
        self.assertIn("0 held-out", self.D.at(got, "claim/bare-c/text"))
        # The claim that already had a number was never in the group, so it never moved.
        self.assertEqual(fm["claims"][0]["text"], self.D.at(got, "claim/has-one/text"))
        self.assertEqual(1, len(calls), "one call for the draft, group included")
        self.assertIn("claim/bare-b/text", calls[0][0])

    def test_a_group_that_does_not_clear_the_floor_goes_back_whole(self):
        """Two of three rewritten is still under the floor, so all three revert."""
        fm = copy.deepcopy(self.SIDECAR)
        fm["claims"] = [{"id": f"bare-{k}", "text": f"Claim {k} says something measured "
                                                    f"without saying how much.",
                         "scope": "Encoder-decoder models above 125M parameters, one pair."}
                        for k in "abcd"]
        fm["qa"] = [{"ask": {"plain": "What does claim a say happens without a "
                                      "magnitude?",
                             "jargon": "Which claim reports no measured amount at "
                                       "all?"},
                     "answers": ["bare-a", "bare-b"]}]
        self.path = self.D.write_draft("a-paper", fm, "a fake model")
        before = self._findings()
        was = open(self.path, encoding="utf-8").read()
        # One field answered, and it cannot move a 1-of-4 ratio past 50% on its own.
        again, _ = self._asker([{"at": "claim/bare-a/text",
                                 "new": "Claim a raises accuracy by 4.6 points."}])
        left = self.D.mend("a-paper", again, "the paper's text", "a fake model")
        self.assertEqual(len(before), left)
        self.assertEqual(was, open(self.path, encoding="utf-8").read(),
                         "a group that did not clear the floor leaves no trace")

    def test_every_field_is_sent_the_rules_its_rewrite_has_to_pass(self):
        """A fix that clears the complaint and breaks a neighbouring rule is wasted work."""
        again, calls = self._asker([])
        self.D.mend("a-paper", again, "the paper's text", "a fake model")
        prompt = calls[0][0]
        self.assertIn("at most 2 sentences", prompt)
        self.assertIn("no sentence over 32 words", prompt)
        self.assertIn("Compress rather than split", prompt)
        # The limits are the checks' own numbers, not a second copy of them.
        from validate import CLAIM_SENTENCE_WORDS, SCOPE_SENTENCES
        self.assertIn(f"over {CLAIM_SENTENCE_WORDS} words",
                      self.D.limits("claim/x/text"))
        self.assertIn(f"most {SCOPE_SENTENCES} sentences", self.D.limits("claim/x/scope"))
        self.assertIn("answerable on its own", self.D.limits("qa/0/ask/plain"))
        # And the role is named back, so a one-field rewrite knows which route it is on.
        self.assertIn("first person", self.D.limits("qa/0/ask/practitioner"))

    def test_a_quoting_finding_is_not_guessed_at_without_the_draft(self):
        """`where` has no way to place one from the string alone, and does not try."""
        self.assertIsNone(self.D.where("Was this validated? -- 'Was this' has no "
                                       "antecedent in the question"))

    def test_a_string_in_two_places_is_left_for_the_whole_sidecar_repair(self):
        fm = {"qa": [{"ask": {"plain": "What is it?"}},
                     {"ask": {"plain": "What is it?"}}]}
        self.assertIsNone(self.D._quoting(fm, "What is it?"))

    def test_a_locus_round_trips_and_a_stale_one_refuses(self):
        fm = self.D.front_matter(self.path)
        for locus in ("claim/too-long/text", "claim/clean/scope", "qa/0/ask/jargon",
                      "misreadings/0", "term/normalized accuracy"):
            with self.subTest(locus=locus):
                self.assertIsInstance(self.D.at(fm, locus), str)
                self.assertTrue(self.D.put(fm, locus, "rewritten"))
                self.assertEqual("rewritten", self.D.at(fm, locus))
        for gone in ("claim/nope/text", "claim/clean/kind", "qa/9/ask/plain",
                     "qa/0/ask/task", "qa/0/ask/unsorted/9",
                     "misreadings/9", "term/nope", "one_liner"):
            with self.subTest(locus=gone):
                self.assertIsNone(self.D.at(fm, gone))
                self.assertFalse(self.D.put(fm, gone, "rewritten"))

    def test_a_fix_that_helps_is_spliced_in_and_nothing_else_moves(self):
        before = self._findings()
        long_one = [f for f in before if "37-word sentence" in f]
        self.assertTrue(long_one, "the fixture is meant to carry the length finding")
        again, calls = self._asker([{"at": "claim/too-long/text", "new": self.SPLIT}])
        left = self.D.mend("a-paper", again, "the paper's text", "a fake model")

        self.assertEqual(len(before) - 1, left, "one finding fixed, none introduced")
        fm = self.D.front_matter(self.path)
        self.assertEqual(self.SPLIT, self.D.at(fm, "claim/too-long/text"))
        # The point of the whole exercise: every other field still holds what it held.
        was = self.D.front_matter(self.D.write_draft("untouched",
                                                     copy.deepcopy(self.SIDECAR), "x"))
        for locus in ("claim/too-long/scope", "claim/clean/text", "claim/clean/scope",
                      "qa/0/ask/plain", "qa/0/ask/jargon", "misreadings/0",
                      "term/normalized accuracy"):
            with self.subTest(locus=locus):
                self.assertEqual(self.D.at(was, locus), self.D.at(fm, locus))
        self.assertEqual(self.SIDECAR["one_liner"], fm["one_liner"])
        self.assertEqual(self.SIDECAR["claims"][1], fm["claims"][1])

        prompt, label, want = calls[0]
        self.assertEqual(1, len(calls), "one call per draft, not one per field")
        self.assertIn("claim/too-long/text", prompt, "the locus is what comes back in `at`")
        self.assertIn("the paper's text", prompt, "a finding asking for a magnitude needs "
                      "the paper, exactly as in whole-sidecar repair")
        self.assertNotIn("clean", prompt, "a field nobody complained about is not sent")
        self.assertEqual(self.D.PATCH_SCHEMA, want,
                         "the reply is held to the patch shape, not the sidecar's")

    def test_a_fix_that_does_not_help_is_thrown_away(self):
        """Splicing cannot regress an untouched field, but it can trade one finding for
        another inside the field it touches -- a sentence cut under the length floor."""
        was = open(self.path, encoding="utf-8").read()
        before = self._findings()
        again, _ = self._asker([{"at": "claim/too-long/text",
                                 "new": "It works well and the gain holds at every model "
                                        "scale tested, being largest at 7B and absent "
                                        "below 125M parameters, which the authors put "
                                        "down to capacity rather than to data volume."}])
        left = self.D.mend("a-paper", again, "", "a fake model")
        self.assertEqual(len(before), left)
        self.assertEqual(was, open(self.path, encoding="utf-8").read(),
                         "a patch that did not reduce the count leaves the draft alone")

    def test_one_wording_pasted_across_two_fields_is_refused(self):
        """The pathology `validate.py`'s shared-scope check was added for, caught earlier."""
        was = open(self.path, encoding="utf-8").read()
        same = "Encoder-decoder models above 125M parameters only."
        again, _ = self._asker([{"at": "claim/too-long/scope", "new": same},
                                {"at": "claim/clean/scope", "new": same}])
        self.D.mend("a-paper", again, "", "a fake model")
        self.assertEqual(was, open(self.path, encoding="utf-8").read())

    def test_one_useless_rewrite_does_not_cost_the_others(self):
        """A patch is accepted field by field, not all-or-nothing.

        Live case: 6 fields rewritten, 1 finding cleared -- so 5 rewrites were churn a
        human would have had to re-read, and under all-or-nothing acceptance a single bad
        field would instead have thrown away every good one.
        """
        before = self._findings()
        again, _ = self._asker([
            {"at": "claim/too-long/text", "new": self.SPLIT},
            # Rewords the misreading without giving 'here' an antecedent, so its own
            # finding survives and the rewrite has bought nothing.
            {"at": "misreadings/0", "new": "Low agreement here is not weak annotation "
                                          "of the data."}])
        left = self.D.mend("a-paper", again, "", "a fake model")
        self.assertEqual(len(before) - 1, left)
        fm = self.D.front_matter(self.path)
        self.assertEqual(self.SPLIT, self.D.at(fm, "claim/too-long/text"),
                         "the fix that worked is kept")
        self.assertEqual(self.SIDECAR["misreadings"][0], self.D.at(fm, "misreadings/0"),
                         "the rewrite that did not clear its own finding is reverted")

    def test_a_locus_nobody_complained_about_is_ignored(self):
        was = open(self.path, encoding="utf-8").read()
        again, _ = self._asker([{"at": "claim/clean/text", "new": "Anything at all."},
                                {"at": "one_liner", "new": "Anything at all."}])
        self.D.mend("a-paper", again, "", "a fake model")
        self.assertEqual(was, open(self.path, encoding="utf-8").read(),
                         "the reply can only reach fields the checker named")

    def test_a_clean_draft_costs_nothing(self):
        def refuse(*a, **k):                       # pragma: no cover -- must not be called
            raise AssertionError("a clean draft must not be sent to a model")

        refuse.window = 0
        self.D.write_draft("a-paper", copy.deepcopy(self.SIDECAR), "a fake model")
        if not self._findings():
            self.assertEqual(0, self.D.mend("a-paper", refuse))


class TestEveryBackendCanBeRepaired(unittest.TestCase):
    """`--repair` must work on whichever model the researcher actually has.

    The loop that takes a draft from 55 findings to zero is backend-agnostic by
    construction -- `repair(slug, rounds, again, evidence)` only ever calls
    `again(prompt, label)` and reads `again.window`. But it is reachable only if the
    drafting call *returns* that closure, and for a while `call_api` returned the drafts
    alone, so `--repair` printed "needs --mode openai" and the strongest model the config
    can name produced the least finished draft. Nothing in the loop caused that; one
    return signature did. So the invariant under test is the signature, on every backend
    `main` can dispatch to.
    """

    def _fake(self, name, mod):
        real = sys.modules.get(name)
        sys.modules[name] = mod
        self.addCleanup(lambda: sys.modules.__setitem__(name, real)
                        if real is not None else sys.modules.pop(name, None))

    CFG = {"llm": {"model": "claude-opus-5", "effort": "low", "max_tokens": 4096}}
    PAIRS = [({"slug": "a-paper"}, "the paper's text")]
    REPLY = '{"one_liner": "x", "claims": [], "qa": []}'

    def test_the_anthropic_path_hands_back_a_repairable_asker(self):
        import contextlib, types
        block = types.SimpleNamespace(type="text", text=self.REPLY)
        msg = types.SimpleNamespace(stop_reason="end_turn", content=[block])

        # A context manager, because the request is streamed: the SDK refuses a
        # non-streaming call whose max_tokens implies over ten minutes of generation,
        # which is every drafting call at the configured 32k.
        @contextlib.contextmanager
        def stream(**kw):
            yield types.SimpleNamespace(get_final_message=lambda: msg)

        messages = types.SimpleNamespace(stream=stream)
        mod = types.SimpleNamespace(
            Anthropic=lambda *a, **k: types.SimpleNamespace(messages=messages))
        self._fake("anthropic", mod)
        import draft_sidecars as D
        self._assert_triple(D.call_api(self.PAIRS, self.CFG))

    def test_the_openai_path_hands_back_a_repairable_asker(self):
        import types
        choice = types.SimpleNamespace(finish_reason="stop",
                                       message=types.SimpleNamespace(content=self.REPLY))
        completions = types.SimpleNamespace(create=lambda **kw: types.SimpleNamespace(
            choices=[choice]))
        client = types.SimpleNamespace(
            chat=types.SimpleNamespace(completions=completions),
            models=types.SimpleNamespace(list=lambda: []))
        import draft_sidecars as D
        self._fake("openai", types.SimpleNamespace(OpenAI=lambda **k: client))
        import llm
        for var, val in ((llm.ENV_BASE, "https://example.invalid/v1"),
                         (llm.ENV_MODEL, "some/model")):
            old = os.environ.get(var)
            os.environ[var] = val
            self.addCleanup(lambda v=var, o=old: os.environ.__setitem__(v, o)
                            if o is not None else os.environ.pop(v, None))
        self._assert_triple(D.call_openai(self.PAIRS, self.CFG))

    def _assert_triple(self, got):
        self.assertEqual(3, len(got), "a drafting backend returns (drafts, how, asker); "
                         "returning the drafts alone is what made --repair "
                         "openai-only")
        drafts, how, asker = got
        self.assertEqual({"a-paper"}, set(drafts))
        self.assertTrue(str(how).strip(), "provenance is written into every draft header")
        # The two things `repair` uses, and nothing else.
        self.assertTrue(callable(asker))
        self.assertIsInstance(getattr(asker, "window", None), int,
                              "`repair` reads .window to decide how much of the paper "
                              "fits in a repair prompt")
        self.assertEqual(json.loads(self.REPLY), asker("a prompt", "a label"))

    def test_main_dispatches_both_modes_through_one_path(self):
        """And the caller unpacks the triple once, rather than per backend.

        Two call sites is how the signatures drifted apart in the first place.
        """
        import draft_sidecars as D
        src = source(D.__file__)
        self.assertNotIn("answers = call_api(", src,
                         "call_api's result is unpacked as a triple like call_openai's")
        self.assertIn("caller = call_api if mode == \"api\" else call_openai", src)


class TestTheEvidencePackHandsOverThePapersNumbering(unittest.TestCase):
    """What the drafter is given before it writes, which is where `code > agent` lands.

    Rule 1 used to tell a model to "locate the tables and figures carrying the results".
    Enumerating labels in text is code's work, and doing it in code buys two things a
    prompt cannot: the pointer list is exact, so a claim citing a section the paper does
    not have becomes avoidable rather than caught at review; and captions survive the
    full text's truncation, which is what removes them from a long paper's middle.
    """

    PAPER = "\n".join([
        "1", "", "Introduction", "Prose about the setting.",
        "2", "", "Method", "More prose.",
        "2.1", "", "Estimator", "Detail.",
        # A page number and a math expression, which is what a real extraction offers at
        # line start and what the section cap is there to exclude.
        "212", "", "Bounded by the display above.",
        "Figure 1: Accuracy against sample size on MMLU, 14 models.",
        "Table 3: Per-scenario error at 100 examples.",
        "We refer to Appendix B for the proof.",
    ])

    def test_the_pointers_it_lists_are_the_ones_the_paper_has(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import draft_sidecars
        inv = draft_sidecars.inventory(self.PAPER)
        self.assertIn("1, 2, 2.1", inv)
        self.assertNotIn("212", inv)
        self.assertIn("figures: 1", inv)
        self.assertIn("tables: 3", inv)
        self.assertIn("appendices: B", inv)

    def test_it_carries_the_captions_where_the_magnitudes_are(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import draft_sidecars
        inv = draft_sidecars.inventory(self.PAPER)
        self.assertIn("Accuracy against sample size on MMLU, 14 models", inv)
        self.assertIn("Per-scenario error at 100 examples", inv)

    def test_the_drafter_reads_the_same_stripped_text_the_checkers_do(self):
        """A gutter numeral in the prompt is a magnitude the model was handed by mistake.

        `check_claim_numbers` and `check_claim_evidence` both `deline` before looking, so
        a figure the drafter copied out of a line-number column is a claim the accept gate
        rejects for a number the paper does not contain. Generation and checking have to
        read the same text, and this is the assertion that they do.
        """
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import draft_sidecars
        src = source(os.path.join(ROOT, "scripts", "draft_sidecars.py"))
        tree = ast.parse(src)
        fn = next(f for f in ast.walk(tree)
                  if isinstance(f, ast.FunctionDef) and f.name == "evidence")
        called = {n.func.id for n in ast.walk(fn)
                  if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        self.assertIn("deline", called,
                      "evidence() stopped stripping the gutter, so the prompt now carries "
                      "numerals the accept gate will reject")
        self.assertIn("inventory", called)


class TestConfigHasWhatTheStepsIndex(unittest.TestCase):
    """Every `cfg["a"]["b"]` in the program resolves in `config.yaml`.

    A missing key is a KeyError several minutes into a run, after the network work is
    already spent -- and the first version of this test asserted a hand-written list of
    keys, which was wrong on its second entry (`ids.orcid`; ORCID lives under
    `identity`). So the list is read out of the source instead. `cfg` is the only name
    `load_config()` is ever assigned to, in all 16 places, which is what makes the scan
    exact rather than a heuristic.

    Only hard subscripts. A `.get()` is the author saying the key is optional, and this
    test has no business overruling that.
    """

    def keys(self):
        for _, path in modules():
            for node in ast.walk(ast.parse(source(path))):
                # cfg["a"]["b"] parses as Subscript(Subscript(Name)), so match the outer
                # one and walk in. One level (cfg["ids"]) is checked too.
                if not isinstance(node, ast.Subscript) or not isinstance(node.slice, ast.Constant):
                    continue
                inner, chain = node, []
                while isinstance(inner, ast.Subscript) and isinstance(inner.slice, ast.Constant):
                    chain.insert(0, inner.slice.value)
                    inner = inner.value
                if isinstance(inner, ast.Name) and inner.id == "cfg":
                    yield os.path.relpath(path, ROOT), tuple(chain)

    def test_indexed_keys_exist(self):
        from common import load_config
        cfg, bad, seen = load_config(), [], set()
        for where, path in self.keys():
            if path in seen or not all(isinstance(k, str) for k in path):
                continue
            seen.add(path)
            node, shown = cfg, "".join(f'["{k}"]' for k in path)
            for k in path:
                if not isinstance(node, dict) or k not in node:
                    bad.append(f"{where}: cfg{shown}")
                    break
                node = node[k]
        self.assertEqual(bad, [], "config.yaml is missing keys the code indexes:\n  "
                                  + "\n  ".join(sorted(bad)))
        self.assertGreater(len(seen), 15, "the config scan found almost nothing, so it "
                                          "is probably matching the wrong thing")


class TestLedgerAdviceMatchesTheEvidence(unittest.TestCase):
    """The health ledger's advice has to fit what it actually recorded.

    Fits this file's charter -- pure functions over one dict, no network -- and the bug
    is a wiring bug: for four months the ledger told the reader to "check the URL, the
    key, and whether it still exists" about `api.semanticscholar.org/graph/v1/paper/*`,
    whose URL is correct, which plainly still exists, and which was answering 429 to
    every anonymous caller on the internet. Advice that sends someone to inspect a
    working URL is worse than no line at all, because they conclude the ledger is wrong
    about everything.
    """

    def setUp(self):
        import common
        self.common = common
        self.dir = tempfile.mkdtemp()
        self.saved, common.HEALTH = common.HEALTH, os.path.join(self.dir, "health.json")

    def tearDown(self):
        self.common.HEALTH = self.saved
        shutil.rmtree(self.dir, ignore_errors=True)

    def write(self, **rec) -> list[str]:
        """One ledger record, first seen nine days ago and failing as of today.

        Every default is overridable -- `ok` and `fail` included, which they were not when
        the only cases needed a never-answered source.
        """
        old = time.strftime("%Y-%m-%d", time.localtime(time.time() - 9 * 86400))
        base = {"ok": 0, "fail": 9, "first_seen": old, "last_ok": None,
                "last_fail": time.strftime("%Y-%m-%d")}
        with open(self.common.HEALTH, "w") as f:
            json.dump({"example.org/thing": {**base, **rec}}, f)
        return self.common.health_report()

    def test_a_rate_limited_source_is_not_reported_as_missing(self):
        line = self.write(last_error="429")
        self.assertEqual(len(line), 1, line)
        self.assertIn("rate-limited", line[0])
        self.assertNotIn("whether it still exists", line[0])
        self.assertIn("429", line[0])

    def test_a_genuinely_absent_source_still_says_so_and_names_the_error(self):
        line = self.write(last_error="404")
        self.assertEqual(len(line), 1, line)
        self.assertIn("never once answered", line[0])
        self.assertIn("404", line[0])

    def test_note_fetch_records_the_reason_only_for_failures(self):
        self.common.note_fetch("https://example.org/thing", False, "429")
        with open(self.common.HEALTH) as f:
            self.assertEqual("429", json.load(f)["example.org/thing"]["last_error"])
        self.common.note_fetch("https://example.org/thing", True, "ignored")
        with open(self.common.HEALTH) as f:
            r = json.load(f)["example.org/thing"]
        # Two claims, and the second one used to be false. A success does not record its
        # own `why`, and it clears the failure's -- a reason survives only as long as it
        # is still the answer to "what would fix this". The counters keep the history;
        # `last_error` is about now.
        self.assertEqual((r["ok"], r["fail"]), (1, 1))
        self.assertNotIn("last_error", r)

    def test_a_source_failing_right_now_is_reported_even_though_it_answered(self):
        """The case both day-based branches let through, taken from a real ledger.

        `api.semanticscholar.org/.../paper/search` stood at ok=3, fail=18, last_error=429,
        refusing every call -- and this function printed nothing. It had answered once, so
        the never-answered branch skipped it; it had answered *yesterday*, so the six-day
        silence branch skipped it too. Both thresholds ask "has it come back", and neither
        asks "is it working".
        """
        yday = time.strftime("%Y-%m-%d", time.localtime(time.time() - 86400))
        line = self.write(ok=3, fail=18, last_ok=yday, last_error="429",
                          since_ok=self.common.FAILING_NOW)
        self.assertEqual(len(line), 1, line)
        self.assertIn("failing now, not busy", line[0])
        self.assertIn("needs a key", line[0])

    def test_one_success_makes_it_busy_again(self):
        """A hiccup that recovered must not be reported, or the line stops being read."""
        yday = time.strftime("%Y-%m-%d", time.localtime(time.time() - 86400))
        for n in (self.common.FAILING_NOW - 1, 0):
            line = self.write(ok=3, fail=18, last_ok=yday, last_error="429", since_ok=n)
            self.assertEqual([], line, f"since_ok={n} should be weather, got {line}")

    def test_a_legacy_ledger_with_no_counter_is_not_an_alarm(self):
        """`since_ok` postdates the ledger, so its absence has to read as zero."""
        yday = time.strftime("%Y-%m-%d", time.localtime(time.time() - 86400))
        self.assertEqual([], self.write(ok=3, fail=18, last_ok=yday, last_error="429"))

    def test_note_fetch_resets_the_counter_on_success(self):
        for _ in range(4):
            self.common.note_fetch("https://example.org/thing", False, "429")
        with open(self.common.HEALTH) as f:
            self.assertEqual(4, json.load(f)["example.org/thing"]["since_ok"])
        self.common.note_fetch("https://example.org/thing", True)
        with open(self.common.HEALTH) as f:
            self.assertEqual(0, json.load(f)["example.org/thing"]["since_ok"])


class TestAStrayCopyIsNotEveryPaperSharingAToken(unittest.TestCase):
    """The two ways `scholar_strays.py` reports work nobody needs to do.

    Both fired on the first live run. The gap pass has to stay directional -- Scholar
    counting *more* than the APIs is the normal case and reporting it would list the
    whole profile. And Crossref's `query.author` is a loose bibliographic search rather
    than an author filter, so "Leshem Chosen" answered with a 1970s plant-senescence
    paper by Y Leshem; the searched form has to actually be on the record.
    """

    PAPERS = [{"slug": "a", "title": "A Paper About Things", "citations": 100},
              {"slug": "b", "title": "Another Paper Entirely", "citations": 10}]

    def test_only_a_gap_in_scholars_favour_is_silence(self):
        import scholar_strays as ss
        diff = {"paired": [
            {"slug": "a", "scholar_citations": 40, "scholar_url": "u"},   # 60 missing
            {"slug": "b", "scholar_citations": 99, "scholar_url": "u"}]}  # Scholar ahead
        got = ss.undercounted(self.PAPERS, diff)
        self.assertEqual([r["slug"] for r in got], ["a"])
        self.assertEqual(got[0]["gap"], 60)

    def test_a_small_or_proportionally_tiny_gap_is_indexing_lag(self):
        import scholar_strays as ss
        diff = {"paired": [
            {"slug": "a", "scholar_citations": 98, "scholar_url": "u"},   # 2, under GAP_MIN
            {"slug": "b", "scholar_citations": 9, "scholar_url": "u"}]}   # 1, under both
        self.assertEqual(ss.undercounted(self.PAPERS, diff), [])

    def test_the_searched_name_has_to_be_on_the_record(self):
        import scholar_strays as ss
        cfg = {"identity": {"name": "Leshem Choshen",
                            "name_variants": ["Choshen, Leshem"],
                            "name_typos": ["Leshem Chosen"]}}
        loose = [{"index": "Crossref", "url": "x", "doi": "10.1/x",
                  "title": "Plant senescence processes and free radicals",
                  "year": 1988, "citations": 138, "authors": "Y Leshem",
                  "author_list": ["Y Leshem"]}]
        real = [{"index": "Crossref", "url": "y", "doi": "10.1/y",
                 "title": "A Paper About Things", "year": 2024, "citations": 5,
                 "authors": "Leshem Chosen", "author_list": ["Leshem Chosen"]}]
        calls = []

        def fake(name, mailto, batch):
            calls.append(name)
            return [dict(r) for r in batch] if name == "Leshem Chosen" else []

        ss._openalex_by_name = lambda n, m: fake(n, m, loose)
        ss._crossref_by_name = lambda n, m: fake(n, m, real)
        try:
            got = ss.typo_records(cfg, self.PAPERS, None)
        finally:
            importlib.reload(ss)
        self.assertEqual([r["title"] for r in got], ["A Paper About Things"])
        self.assertEqual(got[0]["matched"], "a")


class TestTheSplitPassResumesTomorrow(unittest.TestCase):
    """111 papers against 100 free queries a day, so the cache is the pass, not a speedup.

    None of it runs for real until the credits reset, which is precisely why it is pinned
    here: a resume that silently re-asks every paper never finishes, and one that never
    re-asks keeps reporting a split after OpenAlex merges it. The same scarcity is why the
    title rule is applied to the cache on the way out and not only to the answer on the
    way in.
    """

    def _module(self, cache, answers):
        import scholar_strays as ss
        importlib.reload(ss)
        self.addCleanup(importlib.reload, ss)
        d = tempfile.mkdtemp()
        with open(os.path.join(d, "openalex_splits.json"), "w") as f:
            json.dump(cache, f)
        ss.BUILD = d
        asked = []

        def fake(url):
            asked.append(url)
            return answers.pop(0) if answers else {}

        ss.lookup = fake
        ss.budget_reset = lambda _h: None
        return ss, asked, d

    def _papers(self, n):
        return [{"slug": f"p{i}", "title": f"A sufficiently long paper title number {i}",
                 "title_display": f"Paper {i}"} for i in range(n)]

    def test_a_fresh_answer_is_not_paid_for_twice(self):
        today = datetime.date.today().isoformat()
        ss, asked, _d = self._module({"p0": {"asked": today, "records": []}}, [{"results": []}])
        out = ss.split_records(self._papers(2), None)
        self.assertEqual(len(asked), 1, "re-asked a paper answered today")
        self.assertEqual(out["checked"], 2)
        self.assertEqual(out["total"], 2)

    def test_a_stale_answer_is_asked_again(self):
        old = (datetime.date.today() - datetime.timedelta(days=400)).isoformat()
        ss, asked, _d = self._module({"p0": {"asked": old, "records": []}}, [{"results": []}])
        ss.split_records(self._papers(1), None)
        self.assertEqual(len(asked), 1, "a year-old answer was reused")

    def test_two_matching_records_are_a_split_and_one_is_not(self):
        title = "A sufficiently long paper title number 0"
        twice = {"results": [{"id": "https://openalex.org/W1", "display_name": title,
                              "cited_by_count": 9, "publication_year": 2024},
                             {"id": "https://openalex.org/W2", "display_name": title,
                              "cited_by_count": 4, "publication_year": 2024}]}
        once = {"results": [{"id": "https://openalex.org/W3", "display_name": title,
                             "cited_by_count": 1, "publication_year": 2024}]}
        ss, _a, d = self._module({}, [twice, once])
        out = ss.split_records(self._papers(2), None)
        self.assertEqual([r["slug"] for r in out["rows"]], ["p0"])
        self.assertEqual([r["citations"] for r in out["rows"][0]["records"]], [9, 4],
                         "records are not ordered by citations")
        with open(os.path.join(d, "openalex_splits.json")) as f:
            self.assertEqual(sorted(json.load(f)), ["p0", "p1"], "the cache did not persist")

    def test_a_search_that_did_not_answer_is_not_cached_as_no_split(self):
        """A cache entry stamped with today's date and no records stops the paper being
        asked again for CACHE_DAYS, so one refusal reports it unsplit for two months."""
        ss, asked, d = self._module({}, [None, {"results": []}])
        out = ss.split_records(self._papers(2), None)
        self.assertEqual(2, len(asked), "stopped asking after a refusal")
        with open(os.path.join(d, "openalex_splits.json")) as f:
            self.assertEqual(["p1"], sorted(json.load(f)), "a refusal was cached")
        self.assertEqual(1, out["checked"])
        self.assertEqual(2, out["total"])

    def test_the_partial_count_is_read_off_the_papers_not_the_credits(self):
        """The credits can run out on the last paper, leaving nothing to resume, and a
        plain refusal leaves papers unchecked with credits to spare."""
        import scholar_strays as ss
        for oa, want in ((({"checked": 5, "total": 5, "budget_reset": 900}), None),
                         (({"checked": 3, "total": 5, "budget_reset": 900}), "tomorrow"),
                         (({"checked": 3, "total": 5, "budget_reset": None}),
                          "did not answer for the rest")):
            text = self._page(ss, {"openalex": oa})
            if want is None:
                self.assertNotIn("**Partial", text, str(oa))
            else:
                self.assertIn("**Partial: 3 of 5 papers checked.**", text)
                self.assertIn(want, text)

    def test_a_source_that_did_not_answer_is_not_a_finding_of_none(self):
        """Every section here reports what it did not find, so a refused source reads as a
        clean result. The meter wording asserts Crossref answered with nothing, which holds
        only when OpenAlex alone went quiet."""
        import scholar_strays as ss
        text = self._page(ss, {})
        self.assertIn("None found at OpenAlex or Crossref.", text)
        text = self._page(ss, {"silent": ["api.crossref.org"]})
        self.assertNotIn("None found at OpenAlex or Crossref.", text)
        self.assertIn("api.crossref.org did not answer this run", text)
        meter = {"silent": ["api.openalex.org"], "openalex": {"budget_reset": 900}}
        self.assertIn("OpenAlex refused every query", self._page(ss, meter))
        both = dict(meter, silent=["api.crossref.org", "api.openalex.org"])
        text = self._page(ss, both)
        self.assertNotIn("Nothing at Crossref", text)
        self.assertIn("api.crossref.org and api.openalex.org did not answer", text)

    def test_a_refusal_is_recorded_against_its_host_and_reaches_the_page(self):
        """`silent` in build/scholar_strays.json is how the page knows an empty section is
        not a finding, so the whole path from the status to the wording is one run."""
        import scholar_strays as ss
        importlib.reload(ss)
        self.addCleanup(importlib.reload, ss)
        for st in (0, 429, 500):
            ss._silent.clear()
            with mock.patch.object(ss, "get_status", lambda _u, **kw: (st, b"")):
                self.assertIsNone(ss.lookup("https://api.crossref.org/works?rows=1"))
            self.assertEqual({"api.crossref.org"}, ss._silent, "status %s answered" % st)
        ss._silent.clear()
        with mock.patch.object(ss, "get_status",
                               lambda _u, **kw: (200, b'{"message": {"items": []}}')):
            self.assertEqual({"message": {"items": []}},
                             ss.lookup("https://api.crossref.org/works"))
        self.assertEqual(set(), ss._silent)

        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        with mock.patch.object(ss, "BUILD", d), mock.patch.object(ss, "TASKS", d), \
             mock.patch.object(ss, "get_status", lambda _u, **kw: (500, b"")), \
             mock.patch.object(sys, "argv", ["scholar_strays.py", "--quiet", "--limit", "1"]):
            self.assertEqual(0, ss.main())
        with open(os.path.join(d, "scholar_strays.json")) as f:
            self.assertIn("api.openalex.org", json.load(f)["silent"])
        with open(os.path.join(d, "scholar_strays.md")) as f:
            self.assertIn("did not answer this run", f.read())

    def _page(self, ss, over):
        """`tasks/scholar_strays.md` for a state with nothing found, written to a tempdir."""
        state = {"scholar_answered": True, "openalex_skipped": False, "undercounted": [],
                 "typo_records": [], "split_records": [], "openalex": {}, "silent": []}
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        with mock.patch.object(ss, "TASKS", d):
            return open(ss.write_page(dict(state, **over))).read()

    def test_a_record_with_a_word_the_title_lacks_is_a_different_paper(self):
        import scholar_strays as ss
        want = ss.title_tokens("Efficient Benchmarking (of Language Models)")
        self.assertTrue(ss.same_work(want, "Efficient Benchmarking of Language Models"))
        for other in ["Benchmarking Large-Language Models for Resource-Efficient Medical "
                      "AI for Edge Deployment",
                      "Efficient Benchmarking of Language Model Pruning",
                      "Inherent Biases in Efficient Benchmarking of Language Models and "
                      "Text Simplification"]:
            self.assertFalse(ss.same_work(want, other), other)

    def test_a_title_cut_short_is_still_the_same_paper(self):
        import scholar_strays as ss
        full = ("On the Weaknesses of Reinforcement Learning for Neural Machine "
                "Translation")
        want = ss.title_tokens(full)
        self.assertTrue(ss.same_work(want, full))
        self.assertTrue(ss.same_work(want, full[:full.index(" Translation")]))
        self.assertFalse(ss.same_work(want, "On the Weaknesses of Reinforcement Learning"))
        self.assertFalse(ss.same_work(want, None))
        self.assertFalse(ss.same_work(ss.title_tokens(""), full))

    def test_a_cached_answer_is_filtered_again_before_it_is_reported(self):
        title = "A sufficiently long paper title number 0"
        today = datetime.date.today().isoformat()
        cached = {"p0": {"asked": today, "records": [
            {"id": "W1", "title": title, "citations": 9, "year": 2024},
            {"id": "W2", "title": title + " and its consequences", "citations": 4,
             "year": 2024}]}}
        ss, asked, _d = self._module(cached, [])
        out = ss.split_records(self._papers(1), None)
        self.assertEqual(asked, [], "re-asked a paper answered today")
        self.assertEqual(out["rows"], [],
                         "a record naming a different paper was reported as a split")

    def test_the_pass_stops_at_the_first_refusal_and_keeps_what_it_paid_for(self):
        ss, asked, d = self._module({}, [{"results": []}])
        ss.budget_reset = lambda _h: (None if len(asked) < 2 else 26000)
        out = ss.split_records(self._papers(6), None)
        self.assertEqual(len(asked), 2, f"kept asking after a refusal: {asked}")
        self.assertEqual(out["budget_reset"], 26000)
        self.assertEqual((out["checked"], out["total"]), (1, 6),
                         "the partial notice would misreport how far it got")
        with open(os.path.join(d, "openalex_splits.json")) as f:
            self.assertEqual(list(json.load(f)), ["p0"], "the paid-for answer was dropped")


class TestTheReadmeSiteExampleIsTheRealOne(unittest.TestCase):
    """The README's example paper URL has to be the one this config would publish.

    It is the first concrete thing a reader clicks, and a stale one is worse than none
    -- it teaches a URL shape that no longer exists. Derived here rather than trusted,
    because `site.base_url` is a config field and the README is prose.
    """

    def test_the_example_url_is_built_from_config_and_a_real_paper(self):
        import common
        cfg = common.load_config()
        site = cfg["site"]
        readme = open(os.path.join(common.ROOT, "README.md")).read()
        prefix = site["base_url"].rstrip("/") + site["papers_path"].rstrip("/") + "/"
        found = re.findall(re.escape(prefix) + r"([a-z0-9-]+)/", readme)
        self.assertTrue(found, f"README shows no paper URL under {prefix}")
        slugs = {p["slug"] for p in
                 common.read_yaml(os.path.join(common.DATA, "papers.yaml"))["papers"]}
        for slug in found:
            self.assertIn(slug, slugs, "README links a paper the corpus does not have")

    def test_the_bare_site_link_is_the_configured_one(self):
        import common
        base = common.load_config()["site"]["base_url"].rstrip("/")
        readme = open(os.path.join(common.ROOT, "README.md")).read()
        self.assertIn(base, readme, "README names no published site")


class TestAMeteredRefusalIsNotRetried(unittest.TestCase):
    """A 429 that means "no credits" has to end the host, not start a backoff.

    OpenAlex bills `.search:` filters against a free daily 100 and answers the 101st
    with a 429 whose `retryAfter` is hours. `get`'s backoff read that as congestion and
    spent up to four minutes per URL, so a 113-paper loop became a run with no end --
    live for 31 minutes before it was killed, having written nothing.
    """

    def _refusal(self, url, remaining="0", body=b""):
        import email.message
        h = email.message.Message()
        h["x-ratelimit-remaining-usd"] = remaining
        h["x-ratelimit-reset"] = "26000"
        return urllib.error.HTTPError(url, 429, "Too Many Requests", h, io.BytesIO(body))

    def _run(self, err):
        import common
        common._BUDGET_OUT.clear()
        self.addCleanup(common._BUDGET_OUT.clear)
        calls = []

        def fake(req, timeout=None):
            calls.append(req.full_url)
            raise err

        with mock.patch.object(common.urllib.request, "urlopen", fake), \
             mock.patch.object(common.time, "sleep", lambda _s: None):
            first = common.get("https://api.openalex.org/works?filter=title.search:a")
            second = common.get("https://api.openalex.org/works?filter=title.search:b")
        return calls, first, second

    def test_the_host_is_dropped_after_one_refusal(self):
        import common
        calls, first, second = self._run(
            self._refusal("https://api.openalex.org/works?filter=title.search:a"))
        self.assertEqual(first, b"")
        self.assertEqual(second, b"", "a second URL on a spent host still asked")
        self.assertEqual(len(calls), 1, f"retried a refusal that cannot succeed: {calls}")
        self.assertEqual(common.budget_reset("api.openalex.org"), 26000)

    def test_a_free_url_on_the_same_host_still_runs(self):
        """The budget is per endpoint. A DOI lookup costs nothing and keeps answering."""
        import common
        common._BUDGET_OUT.clear()
        self.addCleanup(common._BUDGET_OUT.clear)
        common._BUDGET_OUT["api.openalex.org"] = 26000
        calls = []

        def fake(req, timeout=None):
            calls.append(req.full_url)
            return io.BytesIO(b"{}")

        with mock.patch.object(common.urllib.request, "urlopen", fake):
            self.assertEqual(common.get("https://api.openalex.org/works/doi:10.1/x"), b"{}")
            self.assertEqual(common.get("https://api.openalex.org/works?filter=title.search:a"),
                             b"")
        self.assertEqual(len(calls), 1, f"the priced URL was still fetched: {calls}")

    def test_a_plain_429_is_still_retried(self):
        import common
        calls, _f, _s = self._run(
            self._refusal("https://api.openalex.org/works?filter=title.search:a",
                          remaining="0.05", body=b"slow down"))
        self.assertGreater(len(calls), 2, "congestion has to keep its backoff")
        self.assertIsNone(common.budget_reset("api.openalex.org"))


class TestPacedHostsAreTheOnesWeHammer(unittest.TestCase):
    """Every host this program fetches in a per-paper loop needs a `PACE` entry.

    The failure it catches is silent and was live: `collect.py` slept 3s between arXiv
    API pages and then probed `arxiv.org/html/<id>` once per paper with no sleep at all,
    so one step was polite and rude to the same host in the same run. Pacing lives in
    `common.PACE` precisely because no single call site can see the others -- which also
    means no single call site can be trusted to notice when it is the one bursting.
    """

    def test_every_per_paper_host_is_paced(self):
        from common import PACE
        for host in ("arxiv.org", "api.semanticscholar.org",
                     "api.openalex.org", "api.crossref.org"):
            self.assertIn(host, PACE, f"{host} is fetched once per paper and unpaced")
            self.assertGreater(PACE[host], 0.0, f"{host}'s gap is not a real gap")

    def test_arxiv_and_s2_ask_for_a_full_second(self):
        from common import PACE
        for host in ("arxiv.org", "api.semanticscholar.org"):
            self.assertGreaterEqual(PACE[host], 1.0, f"{host}'s gap is not a real gap")

    def test_the_polite_pool_hosts_send_a_contact_address(self):
        """OpenAlex and Crossref read it out of the User-Agent, not out of the query."""
        import common
        for host in common.POLITE:
            self.assertIn(host, common.PACE, f"{host} is in the polite pool but unpaced")
        self.assertTrue(common._contact(), "identity.email is what the polite pool reads")


class TestARearrangedTitleIsTheSamePaper(unittest.TestCase):
    """`title_tokens` has to be loose enough to catch a swap and tight enough to be safe.

    Both halves matter and they pull opposite ways, which is why this is pinned rather
    than eyeballed. Loose enough: the audit reported "Tie the KnOTS: Model Merging with
    SVD" as a work it could not place, against a corpus holding "Model merging with SVD
    to tie the Knots" -- and told the reader to *check before deleting* a paper there was
    never any reason to doubt. Tight enough matters more: a wrong match makes a stray
    disappear from the report, and the stray that motivated the check in the first place
    was an authorship claim on "Attention is all you need". A miss costs a minute of
    reading; a false match is silent.
    """

    def test_a_reordered_title_matches(self):
        from common import norm_title, title_tokens
        a, b = "Tie the KnOTS: Model Merging with SVD", "Model merging with SVD to tie the Knots"
        # Both of the checks that run before this one have to fail, or the fallback is
        # not what resolves the live case and this test proves nothing.
        self.assertNotEqual(norm_title(a), norm_title(b))
        self.assertFalse(norm_title(a) in norm_title(b) or norm_title(b) in norm_title(a),
                         "containment already caught it -- the token fallback is untested")
        self.assertEqual(title_tokens(a), title_tokens(b))

    def test_one_different_content_word_is_enough_to_refuse(self):
        from common import title_tokens
        for a, b, why in [
                ("Attention is all you need", "Model merging with SVD to tie the Knots",
                 "an unrelated famous paper"),
                # Live near-miss: two BabyLM records whose subject matter genuinely
                # differs. A stemming or overlap-based matcher absorbs this pair.
                ("Insights from the first BabyLM Challenge: Training sample-efficient "
                 "language models on a developmentally plausible corpus",
                 "Findings of the BabyLM Challenge: Sample-Efficient Pretraining over a "
                 "Developmentally Plausible Corpus", "insights/training vs findings"),
                ("TIES-Merging: Resolving Interference When Merging Models",
                 "Resolving Interference (RI): Disentangling Models for Improved Model "
                 "Merging", "same topic, different papers")]:
            self.assertNotEqual(title_tokens(a), title_tokens(b), why)

    def test_no_two_real_corpus_titles_collide(self):
        """The guard the matcher cannot enforce for itself.

        Set equality is only safe while no two papers *of yours* share a content-word
        set; if two ever do, `orcid_strays` drops that key rather than guessing, so the
        failure is a silent return to "cannot place" rather than a wrong match. This
        measures the real corpus so the day it stops holding is a red test and not a
        surprise.
        """
        from common import DATA, read_yaml, title_tokens
        papers = read_yaml(os.path.join(DATA, "papers.yaml"))["papers"]
        seen = {}
        for p in papers:
            t = title_tokens(p["title"])
            if len(t) >= 4:
                seen.setdefault(t, []).append(p["title"])
        clash = [v for v in seen.values() if len(v) > 1]
        self.assertEqual([], clash, f"{len(clash)} pair(s) of your own titles collide")


class TestAnIndexAnswerNeedsMoreThanWordOverlap(unittest.TestCase):
    """The gate between "an index returned this" and "this is your paper".

    `same_paper` compares two titles already known to be yours, so a wrong pair costs one
    line a reader dismisses. The resolvers ask arXiv, Crossref, OpenReview and Semantic
    Scholar's search endpoint, which answer from the whole literature, and there the same
    threshold costs a stranger's paper pasted into your bibliography under your name.
    `same_work` is the tighter gate those four use, and both directions are live cases:
    the two refusals below were real acceptances before it existed, and the four matches
    are retitles the loose gate is there to catch.
    """

    def test_a_prepended_word_changes_the_subject(self):
        from scholar_check import same_paper, same_work
        for query, indexed in [
                # Word overlap cannot separate these: 2 of 4 content words and 3 of 5 are
                # present, both at or over the 0.5 threshold. What separates them is that
                # the extra words went in *front*, where they do not qualify a title but
                # replace its subject -- "Tensor Product Attention" is not "Attention".
                ("Attention is all you need",
                 "Tensor Product Attention Is All You Need"),
                ("An autonomous debating system",
                 "A superpersuasive autonomous policy debating system")]:
            self.assertTrue(same_paper(query, indexed),
                            "the loose gate no longer takes this, so the tight gate is "
                            "not what is being measured")
            self.assertFalse(same_work(query, indexed),
                             f"{indexed!r} would enter the bibliography as {query!r}")

    def test_a_real_retitle_still_resolves(self):
        from scholar_check import same_work
        for a, b, why in [
                # Every legitimate variant keeps its opening word. A dropped subtitle,
                ("Genie: Achieving Human Parity in Content-Grounded Datasets Generation",
                 "Genie: Achieving Human Parity", "subtitle dropped"),
                # a venue retitle that appends,
                ("The Mighty ToRR: A Benchmark for Table Reasoning and Robustness",
                 "The Mighty ToRR: A Benchmark for Table Reasoning and Robustness in "
                 "LLMs", "camera-ready appended two words"),
                # and the live competition report, where "Competition:" is inserted after
                # the head rather than before it -- which is why the rule is the first
                # content word and not a character prefix, a rule this pair would fail.
                ("Llm merging: Building llms efficiently through merging",
                 "LLM Merging Competition: Building LLMs Efficiently through Merging",
                 "a word inserted after the head"),
                ("Global PIQA: Evaluating Commonsense Reasoning Across 100+ Languages "
                 "and Cultures",
                 "Global PIQA: Evaluating Physical Commonsense Reasoning Across 100+ "
                 "Languages and Cultures", "a word dropped mid-title")]:
            self.assertTrue(same_work(a, b), why)

    def test_the_four_open_indexes_all_use_the_tight_gate(self):
        """A fifth resolver added tomorrow has to be the tight kind too.

        Structural because it is the mistake that already happened once in this file:
        `from_openreview` was written against `same_paper` like the three resolvers
        beside it, and made two false authorship claims on its first live run. Reading
        the source is the only way to catch the next one before it fetches anything.
        """
        from common import ROOT
        src = source(os.path.join(ROOT, "scripts", "scholar_check.py"))
        for fn in ("from_arxiv", "from_crossref", "from_openreview"):
            body = src.split(f"\ndef {fn}(", 1)[1].split("\ndef ", 1)[0]
            self.assertIn("same_work(", body, f"{fn} decides on the loose gate")
            self.assertNotIn("same_paper(", body, f"{fn} decides on the loose gate")
        # `from_s2_search` reads a search answer through `from_s2`, which serves both
        # candidate sets, so its tightening is the flag rather than the call.
        body = src.split("\ndef from_s2_search(", 1)[1].split("\ndef ", 1)[0]
        self.assertIn("strict=True", body, "the S2 search endpoint answers loosely")

    def test_a_covers_fragment_names_a_section_that_exists(self):
        """A typo in `covers` silently drops the hold, leaving the section asking.

        The fragment is matched against a heading, so nothing fails loudly when it stops
        matching one. Every fragment has to be a heading the plan already knows about.
        """
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        import update
        from common import ROOT, read_yaml
        items = (read_yaml(os.path.join(ROOT, "data", "followups.yaml"))
                 or {}).get("followups") or []
        known = {frag for frag, _tier, _cost in update.PLAN}
        for i in items:
            for frag in (i.get("covers") or []):
                self.assertIn(frag, known,
                              f"{i['due']} covers a section the plan does not name")

    def test_the_claimed_s2_record_wins_over_the_unclaimed_one(self):
        """A merged paper must stop counting as split, whatever order the ids sit in.

        `collect` walks `ids.semantic_scholar` and tags each paper with the record it
        came from. A paper pulled onto the claimed page is still listed on the
        unclaimed one, so it arrives twice; an unguarded assignment lets whichever id
        is configured last decide, and the worklist re-asks for all 34 merges forever.
        """
        from common import ROOT
        src = source(os.path.join(ROOT, "scripts", "collect.py"))
        guard = ('if p.get("s2_author_record") != '
                 'cfg["ids"]["semantic_scholar_primary"]:')
        before = src.split('p["s2_author_record"] = aid', 1)[0]
        self.assertIn(guard, before[-200:],
                      "the assignment is not guarded by the primary record")

    def test_every_open_index_is_named_when_it_had_nothing(self):
        """`UNRESOLVED` has to name the indexes actually asked, not a stale list.

        The names were written twice -- once in `resolve`, once in the `bib_missing.md`
        header -- and adding OpenReview updated only one, so the file a human reads went
        on saying "not in all three indexes" after four were asked. One list now, and
        this is what keeps a second copy from growing back.
        """
        import ast
        import re as _re
        from scholar_check import OPEN_INDEXES, S2_RECORD
        from common import ROOT
        path = os.path.join(ROOT, "scripts", "scholar_check.py")
        src = source(path)
        self.assertGreaterEqual(len(OPEN_INDEXES), 4)
        for _, name in OPEN_INDEXES:
            self.assertEqual(1, src.count(f'"{name}"'), f"{name} is spelled twice")
        self.assertEqual(1, src.count(f'"{S2_RECORD}"') + src.count(f"'{S2_RECORD}'"))
        # Emitted text only, which is what a hard-coded count would go stale in. Prose
        # is exempt on purpose: the comment above `OPEN_INDEXES` quotes the wrong
        # sentence in order to explain it, and a plain substring search over the file
        # cannot tell that apart from the file emitting it.
        tree = ast.parse(src)
        docs = {id(n.body[0].value) for n in ast.walk(tree)
                if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef,
                                  ast.AsyncFunctionDef))
                and n.body and isinstance(n.body[0], ast.Expr)
                and isinstance(n.body[0].value, ast.Constant)
                and isinstance(n.body[0].value.value, str)}
        for n in ast.walk(tree):
            if (isinstance(n, ast.Constant) and isinstance(n.value, str)
                    and id(n) not in docs):
                self.assertIsNone(
                    _re.search(r"all (two|three|four|five) indexes", n.value),
                    f"line {n.lineno} emits a resolver count that goes stale silently")


class TestASubmissionIsNotAPublication(unittest.TestCase):
    """OpenReview hosts the submission, not only the paper.

    Every other index this program asks holds published work, so a title match there is
    evidence of publication. OpenReview also holds what was withdrawn, desk-rejected and
    still under review -- and a note in any of those states has a real title, real
    authors and a `venue` string reading *ICLR 2026 Conference Withdrawn Submission*.
    Rendered as `@inproceedings{booktitle = {ICLR 2026}}`, that is a claim the paper
    appeared at ICLR, which it did not and now never will.

    The one rule works because OpenReview names every non-accepted state the same way:
    the `venueid`'s last path segment ends in `Submission`. Pinned here against the live
    shapes the two API sweeps returned, because the rule is inferred from that naming
    convention rather than from anything documented -- if it changes, the failure is a
    withdrawn paper in a bibliography, and nothing downstream would question it.
    """

    def test_no_venue_state_gets_in(self):
        from scholar_check import published
        for vid, venue in [
                ("ICLR.cc/2026/Conference/Withdrawn_Submission",
                 "ICLR 2026 Conference Withdrawn Submission"),
                ("ICLR.cc/2025/Conference/Desk_Rejected_Submission",
                 "ICLR 2025 Conference Desk Rejected Submission"),
                ("NeurIPS.cc/2024/Conference/Rejected_Submission",
                 "NeurIPS 2024 Conference Rejected Submission"),
                # Still under review: the plain group, and the venue string that names
                # the state instead of the venue.
                ("ICLR.cc/2026/Conference/Submission", "Submitted to ICLR 2026"),
                # And the notes that leave the id off entirely.
                ("", "Submitted to ACL ARR 2025 February"),
                ("", "")]:
            self.assertFalse(published({"venueid": {"value": vid},
                                        "venue": {"value": venue}}),
                             f"{venue or vid!r} is not a publication")

    def test_an_accepted_paper_gets_in(self):
        from scholar_check import published
        for vid, venue in [
                ("ICLR.cc/2024/Conference", "ICLR 2024 Poster"),
                # The live case this was written for.
                ("NeurIPS.cc/2025/Workshop/LLM_Evaluation",
                 "NeurIPS 2025 LLM Evaluation Workshop"),
                ("EWRL/2025/Workshop", "EWRL 2025"),
                # A dblp mirror, which is a journal and typed `article` -- see below.
                ("dblp.org/journals/CORR/2021", "CoRR 2021")]:
            self.assertTrue(published({"venueid": {"value": vid},
                                       "venue": {"value": venue}}),
                            f"{venue!r} is a publication and would be refused")

    def test_a_journal_note_is_not_proceedings(self):
        """The other axis of the same mistake: asserting a venue that does not exist.

        Nearly everything OpenReview hosts itself is a conference or workshop paper, so
        `inproceedings` is the right default -- but a note mirrored from dblp or
        deposited as a public article is a journal, and `inproceedings` there invents
        proceedings, the way a withdrawn submission invents an acceptance.
        """
        from common import ROOT
        src = source(os.path.join(ROOT, "scripts", "scholar_check.py"))
        body = src.split("\ndef from_openreview(", 1)[1].split("\ndef ", 1)[0]
        for marker in ("/journals/", "Public_Article", '"article"'):
            self.assertIn(marker, body, f"{marker} no longer routes to a journal type")


class TestAStopgapCannotGoQuiet(unittest.TestCase):
    """`extra_arxiv`, `extra_openreview` and `fields:` have a stated lifetime, so something
    has to watch both ends of it.

    They exist because a paper the bibliography has not received yet has no page at all,
    and the fix is one entry upstream -- after which the line here is dead weight. Both
    transitions are silent by default, in opposite ways. While the paper is missing
    upstream, the Scholar block cannot report it: that block finds bibliography gaps by
    diffing Scholar against the corpus, and the override has already closed the gap. Once
    the paste lands, the paper correctly stops being reported -- and the line it leaves
    behind is announced once, on stderr, in a five-minute run. The live `extra_arxiv` id
    got there exactly that way, which is what this pins. `fields:` is the same shape --
    Scholar, Semantic Scholar and OpenAlex read the paper's own record, so a correction
    that stays here reaches the corpus and nothing else.
    """

    def _render(self, papers, overrides):
        """`upstream_gaps` against a synthetic corpus and a synthetic overrides file."""
        import tempfile
        import update
        from common import write_yaml
        with tempfile.TemporaryDirectory() as d:
            write_yaml(os.path.join(d, "overrides.yaml"), overrides)
            old, update.DATA = update.DATA, d
            try:
                return "\n".join(update.upstream_gaps(papers, {}))
            finally:
                update.DATA = old

    def test_a_paper_only_an_override_supplies_is_reported(self):
        out = self._render(
            [{"slug": "s", "title": "A Statistical Framework for Game-Based AI Evaluation",
              "authors": ["Felipe Maia Polo", "Leshem Choshen"], "year": 2025,
              "venue": "NeurIPS 2025 LLM Evaluation Workshop", "type": "inproceedings",
              "url": "https://openreview.net/forum?id=1VWfIsRdZA",
              "_override": "extra_openreview"}],
            {"extra_openreview": ["A Statistical Framework for Game-Based AI Evaluation"]})
        self.assertIn("the bibliography does not have", out)
        self.assertIn("A Statistical Framework", out)
        # Pasteable, or the reader has to reconstruct the entry from the site.
        self.assertIn("```bibtex", out)
        self.assertIn("@inproceedings", out)
        self.assertNotIn("redundant", out, "the line is still load-bearing")

    def test_the_line_is_reported_once_its_paper_arrives(self):
        # Same id, no marker: the record came from the bibliography this run, so the
        # override supplied nothing and the line is spent.
        out = self._render(
            [{"slug": "s", "title": "Growing Pains", "arxiv": "2604.12843",
              "key": "habba2026growing", "_override": None}],
            {"extra_arxiv": ["2604.12843"]})
        self.assertIn("redundant", out)
        self.assertIn("2604.12843", out)
        self.assertNotIn("the bibliography does not have", out,
                         "the gap is closed -- reporting it again asks for a done paste")

    def test_a_line_whose_paper_never_resolved_is_not_called_done(self):
        """The two failures a single "is it in the corpus" check would conflate.

        A title that OpenReview has no accepted paper for adds nothing to the corpus
        either -- and reporting *that* as redundant would tell the reader to delete the
        line, discarding the request. It stays unreported here, because the collector
        already refuses it loudly by name on the run that tried.
        """
        out = self._render(
            [{"slug": "s", "title": "Some other paper", "arxiv": "2101.00001",
              "_override": None}],
            {"extra_openreview": ["A paper OpenReview does not have"],
             "extra_arxiv": ["2604.12843"]})
        self.assertEqual("", out)

    def test_a_field_correction_upstream_does_not_have_is_reported(self):
        """A `fields:` value the entry lacks, with the line to paste."""
        out = self._render(
            [{"slug": "s", "title": "Position: Agentic Systems Should be General",
              "key": "bandel2026agentic", "_override": None,
              "bibtex": "@inproceedings{bandel2026agentic,\n  title = {Position},\n"
                        "  institution = {International Conference on Machine Learning},\n"
                        "  year = {2026},\n}"}],
            {"fields": {"s": {"doi": "10.2139/ssrn.6176178",
                              "venue": "International Conference on Machine Learning"}}})
        self.assertIn("1 field correction the bibliography does not carry", out)
        self.assertIn("doi          = {10.2139/ssrn.6176178},", out)
        # The venue is already upstream under `institution`, so asking for it again is a
        # done paste. Matching is on the value anywhere in the entry, not on a field name.
        self.assertNotIn("booktitle", out)

    def test_a_correction_the_entry_already_carries_is_not_reported(self):
        out = self._render(
            [{"slug": "s", "title": "Knots", "key": "k2025knots", "_override": None,
              "bibtex": "@article{k2025knots,\n  year = {2025},\n  doi = {10.1/x},\n}"}],
            {"fields": {"s": {"year": 2025, "doi": "10.1/X"}}})
        self.assertNotIn("field correction", out)

    def test_the_live_file_has_no_spent_lines(self):
        """And the report is empty right now, which is the only state worth committing.

        A committed override that the corpus proves redundant is a line every future
        reader has to re-derive the status of.
        """
        from common import DATA, read_yaml
        papers = read_yaml(os.path.join(DATA, "papers.yaml"))["papers"]
        ov = read_yaml(os.path.join(DATA, "overrides.yaml")) or {}
        self.assertNotIn("redundant", self._render(papers, ov))


class TestARewriteDoesNotUnclaimYourPapers(unittest.TestCase):
    """A claim lives in a file the collector regenerates wholesale, so it needs carrying.

    `ownership.py` recovers our own claim by reading the value already in `papers.yaml`
    -- there is nowhere else it is written down. `collect.py` rebuilds that file from live
    sources, so without this the sequence is: claim a paper, run the loop, the reconcile
    finds no `self` to recover, the paper goes back to `unclaimed`, and the manifest peers
    read to avoid building a second canonical page for it loses the claim for good. Found
    by committing exactly that: a collect-only run had dropped `owner` and `owner_source`
    from every paper, and the only reason nothing was lost is that nothing is claimed yet.
    """

    def _carry(self, prev, fresh):
        import tempfile
        from collect import carry_claims
        from common import write_yaml
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "papers.yaml")
            write_yaml(path, {"papers": prev})
            carry_claims(fresh, path)
            return fresh

    def test_our_own_claim_survives(self):
        got = self._carry([{"slug": "p", "owner": "Me", "owner_source": "self"}],
                          [{"slug": "p", "title": "freshly collected"}])
        self.assertEqual("self", got[0]["owner_source"])
        self.assertEqual("Me", got[0]["owner"])

    def test_a_peers_page_survives_until_ownership_runs_again(self):
        """Because `render` reads `canonical_page` to decide not to compete.

        Between a collect and the next ownership run, a missing `canonical_page` is a
        second page for a paper a co-author already publishes -- the duplication the whole
        mechanism exists to prevent, and the one thing here that is expensive to undo.
        """
        got = self._carry(
            [{"slug": "p", "owner": "A Peer", "owner_source": "peer",
              "canonical_page": "https://peer.example/p"}],
            [{"slug": "p", "title": "freshly collected"}])
        self.assertEqual("https://peer.example/p", got[0]["canonical_page"])
        self.assertEqual("peer", got[0]["owner_source"])

    def test_carrying_never_overwrites_what_this_run_derived(self):
        got = self._carry([{"slug": "p", "owner": "A Peer", "owner_source": "peer"}],
                          [{"slug": "p", "owner": "Me", "owner_source": "self"}])
        self.assertEqual("self", got[0]["owner_source"])
        # And a paper that is new this run has nothing to carry, rather than inheriting a
        # neighbour's claim.
        self.assertEqual([{"slug": "new"}],
                         self._carry([{"slug": "p", "owner_source": "self"}],
                                     [{"slug": "new"}]))

    def test_an_unclaimed_paper_is_carried_too_so_the_diff_stays_empty(self):
        """`owner: null` is not a claim, and dropping it is still wrong.

        `ownership.py` leaves both keys off an unclaimed paper, but a hand-set `owner:
        null` still has to survive a collect: a carry that tests truthiness drops it and
        every collect-only run shows a removed line per paper, all meaning nothing.
        """
        got = self._carry([{"slug": "p", "owner": None, "owner_source": "unclaimed"}],
                          [{"slug": "p", "title": "freshly collected"}])
        self.assertIn("owner", got[0])
        self.assertIsNone(got[0]["owner"])

    def test_ownership_still_reads_the_field_this_protects(self):
        """The coupling is invisible from either file alone, so it is asserted.

        If `ownership.py` ever recovers the self-claim from somewhere else, this carry is
        dead weight and should go. If it still reads `papers.yaml`, deleting the carry
        re-arms the bug -- and nothing else in the suite would say so.
        """
        from common import ROOT
        body = source(os.path.join(ROOT, "scripts", "ownership.py"))
        body = body.split("\ndef reconcile(", 1)[1].split("\ndef ", 1)[0]
        self.assertIn('owner_source") == "self"', body)
        from collect import CARRIED
        self.assertIn("owner_source", CARRIED)


class TestTheItemIsNotAskedForWhatItAlreadyHas(unittest.TestCase):
    """The follow-up file is a diff, and the only way to see that is to render one.

    The block it emits was a standing table of four statements, so it asked for the same
    four whether or not the item carried them -- and it does carry all four, which made
    a done item read as open work forever. That is the failure `code > agent > human`
    exists to prevent: the item is readable by API, so nothing about it belongs in a
    list a human is asked to check.
    """

    def _block(self, has, unqualified, orc=None):
        from audit_identity import disambiguating_statements
        g = {"qid": "Q1", "has": has, "unqualified": unqualified}
        ident = {"name": "Ada Lovelace", "affiliations": [{"name": "Somewhere"}],
                 "education": [{"institution": "Somewhere", "degree": "PhD"}]}
        return "\n".join(disambiguating_statements(g, ident, "Ada", "Lovelace", orc))

    def test_a_complete_item_gets_no_table(self):
        out = self._block({"P735": ["x"], "P734": ["x"], "P69": ["x"], "P108": ["x"]}, [])
        self.assertEqual("", out)

    def test_only_the_absent_statements_are_listed(self):
        out = self._block({"P735": ["x"], "P69": ["x"]}, [])
        self.assertIn("`P734`", out)
        self.assertIn("`P108`", out)
        self.assertNotIn("`P735`", out)
        self.assertNotIn("`P69`", out)

    def test_a_date_orcid_states_is_not_asked_for(self):
        """The split that decides who does the work, and the reason it is measured here.

        A start time on the ORCID record is one `wikidata_apply.py --apply` away, so
        putting it on the page would be asking for an edit the code makes. An employment
        ORCID does not list has no public date at all, and that one is the author's.
        """
        orc = {"employment_rows": [{"org": "Dated Lab", "start": 2016, "end": None,
                                    "role": None}]}
        out = self._block({"P735": ["x"], "P734": ["x"], "P69": ["x"], "P108": ["x"]},
                          [("P108", "Q2", "Dated Lab"), ("P108", "Q3", "Undated Lab")],
                          orc)
        self.assertIn("wikidata_apply.py --apply", out)
        self.assertIn("Dated Lab", out.split("## Employers only you can date")[0])
        yours = out.split("## Employers only you can date")[1]
        self.assertIn("Undated Lab", yours)
        self.assertNotIn("Dated Lab", yours)


class TestOneAffiliationSpreadOverSeveralOrcidRows(unittest.TestCase):
    """ORCID keeps one row per appointment, so the degree and its dates are separate.

    Reading the first matching row got the PhD from `config.yaml` and missed the 2023 end
    date sitting on the other row for the same university. Merging is what makes the
    qualifier set complete rather than nearly so.
    """

    def test_the_earliest_start_the_latest_end_and_every_role(self):
        from common import affil_index
        got = affil_index([
            {"org": "The Hebrew University of Jerusalem", "start": 2016, "end": None,
             "role": None},
            {"org": "Hebrew University of Jerusalem", "start": None, "end": 2023,
             "role": "PhD"},
        ])
        self.assertEqual(["hebrew university of jerusalem"], list(got))
        e = got["hebrew university of jerusalem"]
        self.assertEqual((2016, 2023, ["PhD"]), (e["start"], e["end"], e["roles"]))

    def test_a_row_with_no_organisation_is_dropped(self):
        from common import affil_index
        self.assertEqual({}, affil_index([{"org": None, "start": 2016}]))


class TestBothWikidataWritersDescribeTheSameItem(unittest.TestCase):
    """Two ways to create a paper item, and the danger is not that one is wrong.

    A QuickStatements batch needs no stored credential and is the fallback if the bot
    password is revoked; `wikidata_apply.py --papers` writes the same items through the
    API. The failure mode of two emitters is that they *disagree*, so the `.qs` file a
    human reads before pasting describes items other than the ones the API path creates
    -- and on a wiki, undoing the wrong one is a deletion request rather than a click.
    Both render `audit_identity.paper_item`, which is what makes them agree; this
    measures the agreement over the real corpus rather than trusting the arrangement.
    """

    def _items(self):
        from common import DATA, read_yaml, load_config
        from audit_identity import paper_item
        papers = read_yaml(os.path.join(DATA, "papers.yaml"))["papers"]
        cfg = load_config()
        return [(p, paper_item(p, cfg)) for p in papers]

    def test_the_batch_and_the_api_carry_the_same_facts(self):
        import re as _re
        from wikidata_apply import item_json
        for p, it in self._items():
            if not it:
                continue
            j = item_json(it)
            # The QuickStatements rendering of this one item, without writing a file:
            # every value the batch would paste, pulled out of the API payload's twin.
            qs = {"P31": it["instance_of"], "P1476": it["title"]}
            got = {}
            for c in j["claims"]:
                pid = c["mainsnak"]["property"]
                dv = c["mainsnak"]["datavalue"]["value"]
                if pid in ("P31", "P50"):
                    got.setdefault(pid, []).append(dv["id"])
                elif pid == "P1476":
                    got[pid] = dv["text"]
                elif pid == "P577":
                    got[pid] = dv["time"]
                else:
                    got.setdefault(pid, []).append(dv)
            self.assertEqual([qs["P31"]], got["P31"], p["slug"])
            self.assertEqual(qs["P1476"], got["P1476"], p["slug"])
            self.assertEqual([it["doi"]] if it["doi"] else [], got.get("P356", []),
                             p["slug"])
            self.assertEqual([it["arxiv"]] if it["arxiv"] else [], got.get("P818", []),
                             p["slug"])
            if it["year"]:
                self.assertEqual(f"+{it['year']}-00-00T00:00:00Z", got["P577"], p["slug"])
                self.assertEqual(9, [c for c in j["claims"]
                                     if c["mainsnak"]["property"] == "P577"
                                     ][0]["mainsnak"]["datavalue"]["value"]["precision"],
                                 "precision 9 is a year; anything finer is invented")
            # Every author, in order, and each one ordinal-qualified: an item whose
            # author order is lost is not a smaller version of the paper, it is a
            # different claim about who wrote it.
            authors = [c for c in j["claims"]
                       if c["mainsnak"]["property"] in ("P50", "P2093")]
            self.assertEqual(len(it["authors"]), len(authors), p["slug"])
            self.assertEqual([str(a["ordinal"]) for a in it["authors"]],
                             [c["qualifiers"]["P1545"][0]["datavalue"]["value"]
                              for c in authors], p["slug"])
            self.assertLessEqual(len(j["labels"]["en"]["value"]), 250,
                                 "Wikidata rejects the label and the batch stops here")
            self.assertFalse(_re.search(r'(?<!\\)"', it["label"] + it["title"]),
                             "a bare quote ends the QuickStatements value early")

    def test_a_paper_with_no_identifier_is_not_created(self):
        """No DOI and no arXiv id means no item, from either writer.

        Not a formatting convenience. An external identifier is what puts a publication
        item uncontroversially in scope, and it is also the key coverage is measured on
        -- so an item created without one cannot be recognised by a later run, and might
        already exist under a title nothing here can match.
        """
        from audit_identity import paper_item
        from common import load_config
        cfg = load_config()
        self.assertIsNone(paper_item(
            {"slug": "x", "title": "A paper nobody registered", "authors": ["A B"],
             "year": 2025}, cfg))
        # And the corpus really contains such papers, so the None branch is reached on a
        # live run rather than only in this test. If this ever goes red, every paper has
        # an identifier -- a better state than the one this line was written in, and the
        # right response is to delete the line.
        self.assertTrue(any(it is None for _, it in self._items()),
                        "every paper now has an identifier; this assertion has no job "
                        "left, delete it")

    def test_a_recorded_item_is_not_created_twice(self):
        """The receipt that closes the query service's lag.

        Coverage is measured by SPARQL, and the scholarly query service trails an edit by
        long enough that the next scheduled run cannot see what this one created. Without
        the ledger it would create the item again, which is the one failure here that
        cannot be undone with a click. Written per item, because the run that most needs
        it is the one that dies mid-batch.
        """
        import tempfile
        import audit_identity as ai
        with tempfile.TemporaryDirectory() as d:
            old, ai.CREATED = ai.CREATED, os.path.join(d, "wikidata_created.yaml")
            try:
                self.assertEqual({}, ai.created_items(), "a missing ledger is empty")
                ai.record_created("some-paper", "Q123")
                ai.record_created("other-paper", "Q456")
                # Re-recording the same pair is what an interrupted-then-resumed run
                # does, and it must not append a second line.
                ai.record_created("some-paper", "Q123")
                self.assertEqual({"some-paper": "Q123", "other-paper": "Q456"},
                                 ai.created_items())
            finally:
                ai.CREATED = old
        # The fold-in itself: coverage adds the ledger to what SPARQL found, so a
        # recorded slug lands in `present` and never in `absent`, which is the list both
        # writers create from.
        src = source(os.path.join(ai.ROOT, "scripts", "audit_identity.py"))
        body = src.split("\ndef wikidata_paper_coverage(", 1)[1].split("\ndef ", 1)[0]
        self.assertIn("created_items()", body, "coverage ignores the ledger")
        self.assertIn("setdefault", body, "the ledger must not overwrite a live answer")


class TestEveryOpenItemIsWorkableWhereItStands(unittest.TestCase):
    """The contract in `CLAUDE.md`: a destination, the instruction, the payload inline.

    Two of the three are checkable mechanically, and they are the two that rotted. A
    section used to say "the URLs are in `tasks/s2_merge.md`" or "-> ACL 2025", which
    reads as complete and is not: the reader still has to open a second file to find out
    what to paste, or work out for themselves what arXiv wants in a field this code
    already knows the value of. So: a section that asks for something has to name where,
    and a section that asks for nothing has no business on the page at all.
    """

    def sections(self):
        """The live worklist as (heading, body-lines), `##` and `###` alike."""
        path = os.path.join(ROOT, "WORKLIST.md")
        if not os.path.exists(path):
            self.skipTest("no WORKLIST.md yet; run python update.py")
        out, opened = [("(preamble)", [])], []
        for ln in source(path).splitlines():
            if re.match(r"#{2,3} \S", ln):
                # A `##` owns its `###`s. Not a nicety: `drop_hollow` keeps a parent
                # whose child asks, so scoring a parent on the prose above its first
                # child would fail every section that is structured that way.
                opened = [(ln, [])] if ln.startswith("## ") else [*opened[:1], (ln, [])]
                out += opened[-1:]
            for _, body in opened or out[-1:]:
                body.append(ln)
        return out

    def test_a_section_that_asks_says_where_to_act(self):
        """A checkbox with no destination in sight is a chore with no address."""
        for head, body in self.sections():
            if not any(l.startswith("- [ ]") for l in body):
                continue
            text = "\n".join(body)
            self.assertTrue(re.search(r"https?://|`(?:data|tasks|scripts)/|`python ", text),
                            f"{head!r} asks for something but names no URL, no path and no "
                            f"command -- so there is nowhere to go and do it")

    def test_nothing_on_the_page_asks_for_nothing(self):
        """`drop_hollow`, checked against the file it ran on.

        The first line of the file promises open items only. A heading left standing
        over declined children broke that promise for the whole page, not just its own
        section, which is why this is asserted on the output rather than on the pass.
        """
        import update
        parent = ""
        for head, body in self.sections():
            if head.startswith("## "):
                parent = head
            # Mirrors `drop_hollow`: a `##` that asks for nothing on purpose keeps its
            # children too, since what is parked there is prose until it is unparked.
            if head == "(preamble)" or any(k in parent + head for k in update.KEEPS):
                continue
            self.assertTrue(any(update.ASKS.search(l) for l in body),
                            f"{head!r} has no checkbox and no command block: it asks for "
                            f"nothing, and `drop_hollow` should have taken it out")

    def test_a_parent_survives_on_its_children(self):
        """The `##`/`###` case, which the live file cannot exercise both ways."""
        import update
        quiet = {"say": lambda *_: None}
        kept = update.drop_hollow(["## Parent", "prose", "### Child", "- [ ] do it"], **quiet)
        self.assertIn("## Parent", kept)
        self.assertNotIn("## Parent", update.drop_hollow(
            ["## Parent", "prose", "### Child", "more prose"], **quiet))


class TestNoItemAsksForAWikidataWriteTheCodeCanDo(unittest.TestCase):
    """`CLAUDE.md` puts Wikidata on this side of the line, `--apply` and all.

    Three sections used to hand over a QuickStatements batch -- author statements matched
    ORCID to ORCID, a venue resolved, a language read off the bibliography -- none of
    which is a judgement anyone has to make. The same rows go out through the API
    instead, and the emitters keep only what a public record cannot settle.
    """

    def test_no_open_item_hands_over_a_quickstatements_batch(self):
        path = os.path.join(ROOT, "WORKLIST.md")
        if not os.path.exists(path):
            self.skipTest("no WORKLIST.md yet; run python update.py")
        for ln in source(path).splitlines():
            if ln.lstrip().startswith(("- [ ]", "- [x]")):
                self.assertNotRegex(ln, r"(?i)quickstatements|\.qs\b",
                                    "an item asks for a paste of statements "
                                    "`--apply` writes")

    def test_a_batch_with_nothing_by_hand_is_no_section_at_all(self):
        """The section exists to ask, so a run with only writable rows left prints none."""
        import update
        self.assertEqual([], update.wikidata_coauthors(
            {"edits": 4, "venues": 2, "fills": 1, "review": 0, "leftover": 0}))
        self.assertEqual([], update.wikidata_orgs(
            {"create": ["a"], "edges": 9, "state": {"a": {"label": "A"}}}))

    def test_what_the_code_writes_is_still_reported_without_a_checkbox(self):
        """Silence would read as done. The count stays, the ask goes."""
        import update
        out = "\n".join(update.wikidata_coauthors(
            {"edits": 4, "review": 1, "leftover": 0, "papers_left": 1}))
        self.assertIn("4 more statement", out)
        self.assertIn("--apply", out)
        self.assertEqual(1, out.count("- [ ]"), out)


class TestTheWorklistSaysWhatToDoFirst(unittest.TestCase):
    """A page of eighteen well-explained items still does not say where to start.

    Each section argues its own case, and none of them can order the page, because none
    knows what else is open -- so the constraints lived inline ("do this before the rest
    of this section", "highest leverage on this page") and reconstructing the order meant
    reading all three hundred lines.
    """

    def _plan(self, lines):
        import update
        out = update.next_steps(lines)
        i = out.index("## Start here")
        j = next(k for k in range(i + 1, len(out)) if out[k].startswith("## "))
        return out[i:j]

    def test_only_the_sections_that_are_open_are_planned(self):
        """The whole point of a generated plan: a section that is done is not in it."""
        plan = "\n".join(self._plan(["# T", "", "## ORCID is missing 1 of your 113 papers",
                                     "", "## Papers whose full text nothing can fetch (1)"]))
        self.assertIn("ORCID is missing 1 of your 113 papers", plan)
        self.assertIn("Papers whose full text nothing can fetch (1)", plan)
        self.assertNotIn("Wikidata", plan, "planned a section this run did not render")

    def test_the_plan_carries_the_headings_own_counts(self):
        """Not a second copy of the numbers.

        A plan that recomputed "108 papers" would drift from the heading that computes it
        for real, and the reader would have two numbers and no way to tell which is live.
        """
        plan = "\n".join(self._plan(["# T", "", "## Wikidata — 41 of your papers have no item"]))
        self.assertIn("**Wikidata — 41 of your papers have no item**", plan)

    def test_nothing_is_planned_when_nothing_is_open(self):
        lines = ["# T", "", "## Waiting on the outside world", ""]
        import update
        self.assertEqual(lines, update.next_steps(lines))

    def test_every_heading_is_either_a_step_or_declared_not_one(self):
        """The one coupling that can rot silently.

        `PLAN` is keyed on heading fragments, so a section added or reworded later is
        simply absent from the plan -- no error, no empty line, nothing to notice. This
        asserts against the live file: every heading in it is matched by a `PLAN` entry
        or named in `NOT_STEPS`, so the choice has to be made rather than defaulted.
        """
        import update
        path = os.path.join(ROOT, "WORKLIST.md")
        if not os.path.exists(path):
            self.skipTest("no WORKLIST.md yet; run python update.py")
        known = [f for f, _, _ in update.PLAN] + list(update.NOT_STEPS)
        for ln in source(path).splitlines():
            if not re.match(r"##+ \S", ln) or ln == "## Start here":
                continue
            self.assertTrue(any(k.lower() in ln.lower() for k in known),
                            f"{ln!r} is in neither PLAN nor NOT_STEPS, so the plan at the "
                            f"top of WORKLIST.md silently leaves it out")


class TestADeclinedSectionTakesItsPayloadWithIt(unittest.TestCase):
    """The worklist hides a section; the file that section handed you is committed.

    `tasks/` is in the repo on purpose, so it is browsable -- which is also why a payload
    there outlives the decision that retired it. `tasks/openalex_merge.md` is the live
    case: `sections: OpenAlex` has been declined for a while and that file went on telling
    a reader to go fill in the correction form. `common.declined` closed the same hole for
    `items:`; this is the section-level half.
    """

    def _stamp(self, body, off=None, later=None):
        """`stamp_payloads` against a throwaway `tasks/` tree, returning the file's text."""
        import tempfile
        import update
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "tasks"))
            path = os.path.join(d, "tasks", "thing.md")
            with open(path, "w") as f:
                f.write(body)
            old, update.ROOT = update.ROOT, d
            try:
                got = update.stamp_payloads(off or {}, later or {})
                with open(path) as f:
                    return got, f.read()
            finally:
                update.ROOT = old

    def test_a_declined_sections_payload_names_the_decision(self):
        got, out = self._stamp("# The form\n\nGo fill it in.\n",
                               off={"tasks/thing.md": "OpenAlex"})
        self.assertEqual(["tasks/thing.md"], got)
        self.assertIn("**Declined.**", out)
        self.assertIn("`OpenAlex`", out, "a banner with no pattern sends you off to grep")
        self.assertIn("# The form", out, "the routes in the file are still the work")

    def test_a_deferred_sections_payload_carries_the_condition(self):
        """Not the same message: deferred work is work, and the reader needs the trigger."""
        _, out = self._stamp(
            "# Zenodo\n", later={"tasks/thing.md": {"until": "a paper is cited"}})
        self.assertIn("Deferred until a paper is cited", out)
        self.assertNotIn("**Declined.**", out)

    def test_stamping_twice_does_not_stack_two_banners(self):
        """`--step worklist` twice without the step that rewrites `tasks/` in between."""
        import update
        _, out = self._stamp(f"{update.STAMP}\n> **Declined.** an older wording\n\n# Form\n",
                             off={"tasks/thing.md": "OpenAlex"})
        self.assertEqual(1, out.count(update.STAMP))
        self.assertNotIn("older wording", out)
        self.assertIn("# Form", out)

    def test_a_named_file_that_was_not_written_is_skipped(self):
        """A section can name a payload a degraded run never got to write."""
        got, out = self._stamp("# Form\n", off={"tasks/absent.md": "OpenAlex"})
        self.assertEqual([], got)
        self.assertEqual("# Form\n", out)

    def test_every_real_payload_extension_is_matchable(self):
        """The paths come out of rendered prose, so the pattern is the whole coupling.

        A new payload written with an extension `PAYLOAD` does not know about would be
        pointed at by the worklist, hidden with its section, and never stamped -- silently,
        which is the failure mode this whole mechanism is about.
        """
        import update
        from common import ROOT
        for name in os.listdir(os.path.join(ROOT, "tasks")):
            self.assertEqual([f"tasks/{name}"], update.PAYLOAD.findall(f"tasks/{name}"),
                             f"PAYLOAD does not match tasks/{name}")


class TestAcceptanceIsNotPermanent(unittest.TestCase):
    """A published sidecar the current rules would refuse comes back round as a draft.

    Acceptance used to be terminal: `pending()` skipped every paper with a live sidecar,
    and the accept-time checks are consulted only by `--accept`, so a file accepted before
    a rule existed was the one thing in the repo that no run could reach and no check
    would look at again -- while being the file the site builds from. Both live sidecars
    were in that state.
    """

    def test_a_refused_live_sidecar_is_queued_again(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import validate
        from draft_sidecars import held, pending, spec_sha
        entries, _ = validate.read_sidecars()
        stale = set(validate.outdated_live(entries))
        if not stale:
            self.skipTest("every live sidecar passes the current accept-time checks")
        papers = [{"slug": s, "citations": 1} for s in stale]
        # `do_all=True` is what isolates the rule under test: it drops the current-draft
        # exemption and leaves only the live-sidecar exclusion, which is the thing that
        # used to make acceptance permanent. Asserted unconditionally, because once a
        # replacement draft exists for every refused sidecar -- the good state -- the
        # default path legitimately queues nothing and would assert nothing.
        self.assertEqual(stale, {p["slug"] for p in pending(papers, True, None)})
        # And the other half of the same rule: a refused sidecar whose replacement draft
        # is already written and waiting is not queued again, because re-queueing it
        # would overwrite a current draft with a fresh call to the model.
        self.assertEqual(stale - set(held(spec_sha())),
                         {p["slug"] for p in pending(papers, False, None)})

    def test_a_passing_live_sidecar_stays_accepted(self):
        """The other half, and the one that keeps this from re-drafting everything: a
        live file the checks pass is done, and a run must not queue it."""
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import validate
        from draft_sidecars import pending
        entries, _ = validate.read_sidecars()
        ok = {n[:-3] for n, _ in entries} - set(validate.outdated_live(entries))
        if not ok:
            self.skipTest("no live sidecar currently passes, so nothing to hold back")
        self.assertEqual([], pending([{"slug": s, "citations": 1} for s in ok], False, None))


class TestReviewPageShowsEachThingOnce(unittest.TestCase):
    """The review page pairs claims with questions, and pays for it exactly once.

    Reviewing is the only job on the worklist that is reading, so what the page costs a
    reader is the thing to protect. It went out once printing each claim's questions above
    it, which put 2-4 near-identical blocks on the page for every claim that answers more
    than one question -- 212 of 318 of them -- and the same question above claims far
    apart, because ordering claims by their *first* question cannot group the second. The
    fix was to walk the questions and render each claim under the first one that asks for
    it, with a one-line link under the rest. That property is invisible in the code and
    obvious on the page, which is the kind that regresses, so it is asserted here.

    A build artifact, so it is checked when present and skipped otherwise: the gates run
    after `update.py`, and CI builds before it tests.
    """

    def test_no_question_or_claim_is_rendered_twice(self):
        page = os.path.join(ROOT, "build", "sidecar_review.html")
        if not os.path.exists(page):
            self.skipTest("build/sidecar_review.html not built")
        with open(page, encoding="utf-8") as fh:
            html = fh.read()
        sections = html.split("<div class=paper ")[1:]
        if not sections:
            # A page with no sections is the normal state right after any check function is
            # edited: `spec_sha` moves, every draft is stale, and the page says so instead of
            # rendering them. Failing here would make editing a rule fail the gates.
            self.skipTest("no fresh drafts on the review page")
        for sec in sections:
            slug = sec.split("'")[1]
            qs = re.findall(r"<p class=ask id[^>]*>(.*?)</p>", sec, re.S)
            ids = re.findall(r"<div class=id>\[[a-z]+\] ([^ <·]+)", sec)
            for label, got in (("question", qs), ("claim", ids)):
                dupes = {x for x in got if got.count(x) > 1}
                self.assertFalse(dupes, f"{slug}: {label} rendered more than once: "
                                        f"{[re.sub('<.*?>', '', d)[:60] for d in dupes]}")

    def test_every_claim_appears_somewhere(self):
        """Grouping by question can drop a claim no question points at. That claim is
        still published in the claim list, so a page that silently omits it hides the
        one thing the author has to decide about it."""
        page = os.path.join(ROOT, "build", "sidecar_review.html")
        if not os.path.exists(page):
            self.skipTest("build/sidecar_review.html not built")
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        from sidecar_io import draft_path
        from sidecar_review import checked
        with open(page, encoding="utf-8") as fh:
            html = fh.read()
        built = os.path.getmtime(page)
        for sec in html.split("<div class=paper ")[1:]:
            slug = sec.split("'")[1]
            d = checked(slug)
            if not isinstance(d, dict):
                continue
            # A claim can be missing from the page for two reasons, and only one of them
            # is a bug: the renderer dropped it, or the draft was rewritten after the page
            # was built. Comparing a fresh draft against a stale page reports the second as
            # the first -- which it did, twice, during a re-drafting pass. Rebuild with
            # `--review` to bring a skipped paper back under the check.
            draft = draft_path(slug)
            if os.path.exists(draft) and os.path.getmtime(draft) > built:
                continue
            shown = set(re.findall(r"<div class=id>\[[a-z]+\] ([^ <·]+)", sec))
            for c in d["claims"]:
                self.assertIn(str(c["id"]), shown,
                              f"{slug}: claim {c['id']} is on no surface of the page")


class TestAClippedTitleStillReads(unittest.TestCase):
    """A row is scanned against what the destination shows it, so a title cut mid-word is a
    title the reader cannot match. `Numerica` reads as a different paper from `Numerical`,
    and 40-odd emitter rows used to cut on the character count alone.
    """

    def test_the_cut_lands_on_a_space_and_says_it_happened(self):
        from common import clipped
        self.assertEqual("NumeroLogic: Number Encoding for Enhanced LLMs'…",
                         clipped("NumeroLogic: Number Encoding for Enhanced LLMs' "
                                 "Numerical Reasoning", 56))
        self.assertEqual("short enough", clipped("short enough", 56))
        self.assertEqual("", clipped(None))
        # One word longer than the whole width is an identifier or a URL, not a title, and
        # the hard cut is the only thing left to do with it.
        self.assertEqual("AAAAAAAAAAAAAAAAAAA…", clipped("A" * 40, 20))

    def test_a_payload_the_reader_has_to_match_is_never_clipped(self):
        """Some rows carry a value rather than a label, and a clip breaks them. The decision
        here is whether two titles name one paper, so a clip could fall exactly where they
        differ. The override line to delete is the same case and is left whole too."""
        import update
        long = ("Deliberately Long Title That Runs Past Any Sensible Row Width So The "
                "Clip Would Fire Here")
        out = "\n".join(update.same_or_different(
            [{"slug": "a", "title": long, "similar_but_distinct": [long + " Two"]}]))
        self.assertIn(long + "`", out)
        self.assertIn(long + " Two`", out)
        self.assertNotIn("…", out)


class TestGeneratedFilesRenderTitles(unittest.TestCase):
    """No generated file may print a title's raw BibTeX form.

    30 of 112 titles carry LaTeX -- `{B}aby{LM}`, `{BERT:}`, `Q\\({}^{\\mbox{2}}\\)` --
    and `collect.py` already resolves every one of them into `title_display`. Reading
    that field is a convention, spelled `p.get("title_display") or p["title"]` at 28
    sites, and a convention held only by memory is one an emitter can drop without
    anything noticing: eight of them had, and `WORKLIST.md` shipped
    `Q\\({}^{\\mbox{2}}\\): Evaluating Factual Consistency` in a committed file.

    Checked against the corpus rather than by pattern-matching for braces, which the
    generated files contain legitimately -- in fenced commands, in `{owner}/{repo}`
    placeholders, in the arXiv DOI template. A 30-character prefix of a real raw title
    cannot appear by coincidence.

    `build/sidecar_review.html` is covered here too, and it is the reason the count
    above moved: three of its emitters read `title` directly, so the one page whose
    whole purpose is the author reading claims against a paper named the paper in
    BibTeX. It is a build artifact rather than a committed file, so it is checked when
    present and skipped when the tree has not been built -- which is enough, because
    the gates run after `update.py` and CI builds before it tests.
    """

    def test_no_raw_latex_title_reaches_a_generated_file(self):
        import glob
        from common import DATA, ROOT, read_yaml
        papers = read_yaml(os.path.join(DATA, "papers.yaml"))["papers"]
        # Only papers whose rendering actually differs, and only where the prefix that
        # would land in a file is itself distinctive.
        probes = {p["title"][:30]: p["slug"] for p in papers
                  if (p.get("title_display") or p["title"]) != p["title"]
                  and re.search(r"[{}\\]", p["title"][:30])}
        self.assertTrue(probes, "no LaTeX titles in the corpus -- this test proves nothing")
        files = ([os.path.join(ROOT, "WORKLIST.md"),
                  os.path.join(ROOT, "build", "sidecar_review.html")]
                 + sorted(glob.glob(os.path.join(ROOT, "tasks", "*.md"))))
        leaks = []
        for f in files:
            if not os.path.exists(f):
                continue
            with open(f, encoding="utf-8") as fh:
                body = fh.read()
            leaks += [f"{os.path.relpath(f, ROOT)}: {slug}"
                      for raw, slug in probes.items() if raw in body]
        self.assertEqual([], leaks, f"{len(leaks)} raw title(s) reached a generated file")


class TestModelTextIsLabelledBeforeItIsPublished(unittest.TestCase):
    """`sweep_github diff` is the only moment a person sees a public write coming.

    RUN.md §11 argues that model-written topics and descriptions may publish unreviewed
    *because* the diff says which ones they are. If the marker stops appearing the
    argument quietly becomes false, and the output still looks perfectly reasonable --
    a diff showing a value with no provenance reads as a fact.
    """

    def test_unread_model_text_is_marked(self):
        from sweep_github import _provenance
        r = {"llm_proposal": {"topics": ["nlp"], "description": "x",
                              "confidence": "medium"}}
        self.assertIn("model", _provenance(r, "topics"))
        self.assertIn("unread", _provenance(r, "topics"))
        self.assertIn("medium", _provenance(r, "topics"))

    def test_reviewed_and_derived_fields_are_not_blamed_on_the_model(self):
        from sweep_github import _provenance
        p = {"llm_proposal": {"topics": ["nlp"], "confidence": "high"}}
        self.assertIn("you edited", _provenance({**p, "reviewed": True}, "topics"))
        # Derived from papers.yaml, so reviewing it here would be reviewing the wrong file.
        self.assertEqual("", _provenance(p, "homepage"))
        # No proposal for this field: nothing to attribute.
        self.assertEqual("", _provenance(p, "description"))


class TestAVisibleQuestionIsAlsoAMachineReadableOne(unittest.TestCase):
    """The questions block is the most retrievable thing on a paper page.

    It is also the easiest to render as decoration. For a year it went out as a plain
    `<dl>`: up to twenty questions in the words a reader actually types, and nothing on
    the page said they were questions. A parser saw paragraphs. So the coupling worth
    holding is not "FAQPage exists somewhere" but "every question the page shows is one
    a parser can find", which is what silently stops being true when the renderer and
    the markup drift apart.
    """

    def _cfg(self):
        from common import load_config
        return load_config()

    def _sidecar(self):
        return {
            "one_liner": "x",
            "claims": [{"id": "c1", "text": "The claim, stated plainly." * 3,
                        "scope": "Holds under these conditions." * 4}],
            "qa": [{"ask": {"plain": "Does it work?",
                            "jargon": "Is it known to work?"},
                    "answered_by": ["c1"]}],
            "terminology": {"widget": "a thing"},
        }

    def test_every_rendered_question_is_in_the_faq_markup(self):
        import json
        import re
        import build_site
        p = {"slug": "s", "title": "T", "authors": ["A"], "year": 2024, "venue": "V"}
        html = build_site.paper_page(p, self._sidecar(), self._cfg())
        asked = [q for q in ("Does it work?", "Is it known to work?") if q in html]
        self.assertEqual(2, len(asked), "the renderer stopped showing the phrasings")
        blocks = [json.loads(b.replace("<\\/", "</")) for b in
                  re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]
        faq = [b for b in blocks if b.get("@type") == "FAQPage"]
        self.assertEqual(1, len(faq), "a page with questions emitted no FAQPage")
        names = [faq[0]["mainEntity"][0]["name"], *faq[0]["mainEntity"][0]["alternateName"]]
        for q in asked:
            self.assertIn(q, names, f"{q!r} is on the page but not in the FAQ markup")

    def test_a_page_with_no_sidecar_emits_no_empty_faq(self):
        """An FAQPage with nothing in it is a claim to answer questions we have not answered."""
        import json
        import re
        import build_site
        p = {"slug": "s", "title": "T", "authors": ["A"], "year": 2024, "venue": "V"}
        html = build_site.paper_page(p, {}, self._cfg())
        types = [json.loads(b.replace("<\\/", "</")).get("@type") for b in
                 re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]
        self.assertNotIn("FAQPage", types)
        self.assertNotIn("DefinedTermSet", types)


class TestLowConfidenceLabelsAreNotPublished(unittest.TestCase):
    """The model's one way to say "I am guessing" has to reach a decision.

    `confidence` is required by the proposal schema, and for a while nothing read it --
    so a thin-README guess was collected and then promoted exactly like a certain
    answer. This is the check that it is wired to something.
    """

    def test_low_confidence_is_not_promoted(self):
        from propose_topics import promote
        rows = [{"repo": "a/b", "llm_proposal": {"topics": ["guessed"],
                                                 "description": "guessed",
                                                 "confidence": "low"}}]
        promote(rows, ["a/b"])
        self.assertNotIn("topics", rows[0], "a low-confidence guess was published")
        self.assertNotIn("description", rows[0])

    def test_high_confidence_still_is(self):
        from propose_topics import promote
        rows = [{"repo": "a/b", "llm_proposal": {"topics": ["nlp"], "description": "d",
                                                 "confidence": "high"}}]
        promote(rows, ["a/b"])
        self.assertEqual(["nlp"], rows[0]["topics"])

    def test_a_refused_guess_does_not_vanish_from_the_output(self):
        """The gate above creates a silence, and the silence has to be broken.

        `pending()` skips a row that has a proposal and `promote()` refuses a low one, so
        the row is bare and nothing asks about it again. Both are right; the run reporting
        "nothing to propose" and stopping there is not. This is the check that the pair
        is reported rather than merely correct.
        """
        from propose_topics import declined_to_guess, pending
        low = {"repo": "a/thin", "llm_proposal": {"topics": [], "description": "",
                                                  "confidence": "low"}}
        rows = [low,
                # Half-labelled: a description and no topics. This is the live shape of
                # two of the three, and requiring *both* to be missing hid them.
                {"repo": "a/half", "description": "d", "topics": [],
                 "llm_proposal": {"topics": [], "confidence": "low"}},
                {"repo": "a/done", "topics": ["nlp"], "description": "d",
                 "llm_proposal": {"topics": ["nlp"], "confidence": "high"}},
                {"repo": "a/frozen", "reviewed": True,
                 "llm_proposal": {"topics": [], "confidence": "low"}}]
        self.assertEqual([], pending(rows, False), "a proposed row came back as work")
        self.assertEqual(["a/thin", "a/half"], declined_to_guess(rows))
        # Once it has both, it is no longer stuck -- whatever the old confidence said.
        low["topics"] = ["nlp"]
        low["description"] = "d"
        self.assertEqual(["a/half"], declined_to_guess(rows))


class TestARejectedTopicStaysRejected(unittest.TestCase):
    """Deleting a topic has to be a decision, not a deletion that the next run undoes.

    This was live and dated: `nlp-free` was invented for one repo, correctly removed from
    its `topics`, and left in that row's `llm_proposal`, so the next `--ingest` would copy
    it back. The failure is invisible in the moment -- the file simply grows a topic
    nobody chose -- which is why it needs a test rather than vigilance.
    """

    def test_declined_topics_survive_a_re_promote(self):
        from propose_topics import promote
        rows = [{"repo": "a/b", "declined_topics": ["invented"],
                 "llm_proposal": {"topics": ["real", "invented"], "confidence": "high"}}]
        promote(rows, ["a/b"])
        self.assertEqual(["real"], rows[0]["topics"])

    def test_the_live_decline_is_recorded_in_the_data(self):
        """The fix is only worth having if the one known rejection is written down."""
        from common import read_yaml
        rows = read_yaml(os.path.join(ROOT, "data", "repos.yaml"))["repos"]
        for r in rows:
            proposed = set((r.get("llm_proposal") or {}).get("topics") or [])
            live = set(r.get("topics") or [])
            declined = set(r.get("declined_topics") or [])
            if not live:
                continue        # never promoted, so absence is not yet a decision
            self.assertEqual(set(), proposed - live - declined,
                             f"{r['repo']}: proposed topics are neither published nor "
                             f"declined, so the next --ingest will publish them")


class TestAWrongIdentifierIsNotAMissingPaper(unittest.TestCase):
    """The ORCID failure that made both of its own symptoms unfixable.

    ORCID groups works that share an external identifier, and the audit used to read one
    title per group. So a work carrying *another paper's* DOI was filed inside that
    paper's group and its own title was never compared to anything. Live case: put-code
    222829712, "Resolving Interference (RI)" (2026), carrying TIES-Merging's
    `10.48550/ARXIV.2306.01708`. The record held RI the whole time, and the audit
    reported it as **missing from ORCID** while reporting the TIES group as **listed
    twice** -- and both offered fixes made the record worse, since adding RI creates a
    second copy and merging the group destroys a distinct paper.

    Two properties are pinned here because each was broken on its own:
    reading every work in a group, and separating a real duplicate from one ORCID has
    already folded. Fixing the first broke the second -- "listed twice" went from 1 to 6
    -- because works that share a group display as a single entry with "N versions" and
    nothing downstream double-counts them.
    """

    CORPUS = [{"slug": "ties", "title": "TIES-Merging: Resolving Interference When "
                                        "Merging Models",
               "doi": "10.52202/075280-0310", "arxiv": "2306.01708"},
              {"slug": "ri", "title": "Resolving Interference (RI): Disentangling "
                                      "Models for Improved Model Merging",
               "doi": "10.48550/ARXIV.2603.13467", "arxiv": "2603.13467"}]

    def strays(self, work_titles):
        from audit_identity import orcid_strays
        return orcid_strays({"work_titles": work_titles, "works": len(work_titles)},
                            self.CORPUS)

    def test_the_live_case_is_reported_as_misfiled_not_as_missing(self):
        # Both works in ORCID group 0, because that is what sharing an identifier does.
        _stray, dups, have, misfiled, _vers = self.strays([
            ("TIES-Merging: Resolving Interference When Merging Models", "1",
             [("doi", "10.48550/arxiv.2306.01708")], 0),
            ("Resolving Interference (RI): Disentangling Models for Improved Model "
             "Merging", "222829712", [("doi", "10.48550/ARXIV.2306.01708")], 0)])
        self.assertEqual({"ties", "ri"}, have,
                         "RI is on the record, so it must not report as missing")
        self.assertEqual(1, len(misfiled))
        title, put, _ids, right, wrong = misfiled[0]
        self.assertEqual("222829712", put)
        self.assertEqual("ri", right["slug"], "the title says which paper it really is")
        self.assertEqual("ties", wrong["slug"], "the identifier says whose DOI it holds")
        self.assertIn("Resolving Interference (RI)", title)
        self.assertEqual({}, dups, "one group is not the profile showing a paper twice")

    def test_an_identifier_still_beats_a_loose_title_match(self):
        """Identifier-first is the rule; the exact-title conflict is the one exception.

        A dropped subtitle or a preprint/proceedings retitle is the ordinary drift that
        matching on identifiers exists to survive, so it must not be read as a misfiling.
        """
        _s, _d, have, misfiled, _v = self.strays([
            ("TIES-Merging: Resolving Interference", "1",
             [("doi", "10.52202/075280-0310")], 0)])
        self.assertEqual([], misfiled, "a shortened title is drift, not a wrong DOI")
        self.assertEqual({"ties"}, have)

    def test_two_groups_are_a_duplicate_and_one_group_is_not(self):
        same = self.strays([("TIES-Merging: Resolving Interference When Merging Models",
                             "1", [("doi", "10.52202/075280-0310")], 0),
                            ("TIES-Merging: Resolving Interference When Merging Models",
                             "2", [("arxiv", "2306.01708")], 0)])
        self.assertEqual({}, same[1], "ORCID already folded these into one entry")
        self.assertEqual({"ties"}, set(same[4]), "worth a mention, not a fix")

        split = self.strays([("TIES-Merging: Resolving Interference When Merging Models",
                              "1", [("doi", "10.52202/075280-0310")], 0),
                             ("TIES-Merging: Resolving Interference When Merging Models",
                              "2", [("arxiv", "2306.01708")], 1)])
        self.assertEqual({"ties"}, set(split[1]),
                         "two groups show as two works, so every service counts both")
        self.assertEqual({}, split[4])


class TestDecliningTheLastItemTakesTheSection(unittest.TestCase):
    """A heading with instructions and no items reads as an open task.

    Live: all five "not on your Scholar profile" papers turned out to be Scholar merges
    and were declined, which left the heading, four paragraphs telling the reader to go
    and check the profile, and a citation total standing over an empty list -- in a file
    whose first line promises open items only.

    The other half is the guard: a section whose body is prose and a pointer legitimately
    has nothing to count, and dropping those would take most of the page.
    """

    def declined(self, rules, lines):
        """`apply_declines` over a rules file written here, not `data/declines.yaml`.

        Reading the live file made these tests assertions about which papers Leshem has
        decided about, which is not what they are checking -- and the first version
        failed exactly that way, on a fixture bullet that no live pattern matched.
        """
        import update
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "declines.yaml"), "w", encoding="utf-8") as fh:
                fh.write(rules)
            keep, update.DATA = update.DATA, d
            try:
                return update.apply_declines(lines)
            finally:
                update.DATA = keep

    def test_a_section_emptied_by_declines_is_removed(self):
        lines = self.declined(
            'items: ["2306.01708"]\n',
            ["## Kept", "", "prose that is not a list", "",
             "### Emptied", "", "why you should care", "",
             "- [ ] 2306.01708 -> NeurIPS 2023", "",
             "### Survives", "", "- [ ] 9999.99999 -> somewhere", ""])
        # Body only. What was removed is named in the report below the rule, and has to
        # be: hiding a section silently is the failure this whole mechanism avoids.
        body, report = "\n".join(lines).split("---", 1)
        self.assertNotIn("Emptied", body)
        self.assertNotIn("why you should care", body)
        self.assertIn("Emptied — every item declined", report)
        self.assertIn("Kept", body)
        self.assertIn("prose that is not a list", body)
        self.assertIn("Survives", body)

    def test_a_heading_that_counts_its_list_is_recounted(self):
        """A count in a heading is a promise about the list under it.

        Live: two of the three papers missing from the bibliography were declined, and
        the heading went on reading "3 papers absent from the source bibliography" over a
        single bullet. The filter runs after the emitters, so only the filter can fix it
        -- and the outer heading dropped its total for exactly this reason, which a
        subsection's cannot do: the number is what tells you the size of the job.
        """
        lines = self.declined(
            'items: ["bbbb", "cccc"]\n',
            ["## Coverage", "",
             "### 3 papers absent from the source bibliography", "",
             "- [ ] 1 cite — aaaa", "- [ ] 2 cites — bbbb", "- [ ] 3 cites — cccc", "",
             "### 2 works on your ORCID carry another paper's identifier", "",
             "- [ ] put-code 1", "- [ ] put-code 2", ""])
        body = "\n".join(lines).split("---", 1)[0]
        self.assertIn("### 1 paper absent from the source bibliography", body)
        self.assertNotIn("3 papers absent", body)
        # Untouched: nothing was declined under it, so its count was never wrong.
        self.assertIn("### 2 works on your ORCID", body)

    def test_a_number_that_is_not_the_count_is_left_alone(self):
        """The guard on the recount, which is the half that can do damage.

        Rewriting a heading that merely opens with a digit turns a correct sentence into
        a wrong one, so the rule is narrow: the number has to have been the length of the
        list before the filter ran.
        """
        lines = self.declined(
            'items: ["bbbb"]\n',
            ["## H", "", "### 7 of your repos are unlabelled", "",
             "- [ ] aaaa", "- [ ] bbbb", ""])
        self.assertIn("### 7 of your repos are unlabelled", "\n".join(lines))

    def test_a_pattern_that_matches_nothing_says_so(self):
        """The mirror of the above, and the bug that produced it.

        Declines match the rendered text, which is what makes them exact and also what
        makes them brittle: titles are truncated in the worklist, so a pattern aimed at
        the tail of one silently matches nothing. Four of the five Scholar declines took
        and the fifth did not, and nothing said which.
        """
        lines = self.declined(
            'items: ["2306.01708", "Call for Participation"]\n',
            ["## H", "", "- [ ] 2306.01708 -> NeurIPS", ""])
        tail = "\n".join(lines).split("Matching nothing this run")
        self.assertEqual(len(tail), 2, "the dead pattern was not reported at all")
        self.assertIn("`Call for Participation`", tail[1])
        self.assertNotIn("`2306.01708`", tail[1],
                         "a pattern that did its job must not be listed as dead")


class TestADeclineReachesThePayloadsToo(unittest.TestCase):
    """A decision recorded once has to stop the question everywhere it is asked.

    `apply_declines` filters `WORKLIST.md` after rendering, which for a while was the
    whole mechanism -- so the summary stopped asking and the payload under it did not.
    Live: "LLM Merging" was ruled out of the bibliography on purpose, and
    `tasks/orcid_remove.md` went on printing it under *check before deleting*, which
    reads as "nobody has looked at this yet".
    """

    def test_the_generators_read_the_same_patterns_the_worklist_does(self):
        from common import DATA, declined, read_yaml
        items = (read_yaml(os.path.join(DATA, "declines.yaml")) or {}).get("items") or []
        if not items:
            self.skipTest("nothing declined, so there is nothing to reach")
        for pat in items:
            self.assertEqual(declined(f"prefix {pat} suffix"), pat)
        self.assertIsNone(declined("a title nobody has ruled out"))
        self.assertIsNone(declined(None), "an absent title must not raise")

    def test_matching_survives_a_change_of_case(self):
        """The trap this was: `items:` was the one case-sensitive matcher in the repo.

        The patterns are titles typed from whichever surface the decision was made on,
        and Scholar title-cases what BibTeX does not -- so `"Llm merging"`, copied from
        the Scholar row, silently missed ORCID's `"LLM Merging"`.
        """
        from common import declined
        pat = "Llm merging"
        if declined(f"x {pat} y") != pat:
            self.skipTest(f"{pat!r} is no longer declined")
        self.assertEqual(declined("LLM Merging: Building LLMs Efficiently"), pat)


class TestNoBatchCreatesASecondAuthorItem(unittest.TestCase):
    """`tasks/wikidata.qs` opened with an unconditional `CREATE`.

    Once the author item existed -- the normal state, recorded in `config.yaml` as
    `ids.wikidata` -- running the file that the top of `WORKLIST.md` pointed at would
    have created a *second* Leshem Choshen on Wikidata. Duplicate items need a merge
    request rather than an edit to undo, and QuickStatements cannot warn about it because
    from its side a second create is a valid request.

    Addressed to the QID instead, the same statements are a safe top-up: QuickStatements
    skips a statement that is already present.
    """

    def test_the_batch_targets_the_existing_item(self):
        from common import load_config
        qid = (load_config().get("ids") or {}).get("wikidata")
        if not qid:
            self.skipTest("no author item recorded yet, so CREATE is correct")
        with open(os.path.join(ROOT, "tasks", "wikidata.qs"), encoding="utf-8") as fh:
            body = fh.read()
        self.assertNotIn("CREATE", body, "this would make a second person on Wikidata")
        self.assertNotIn("LAST\t", body, "LAST addresses the last created item")
        self.assertIn(f"{qid}\t", body)
        # Len/Den overwrite rather than add, so a top-up batch must not carry them: it
        # would silently revert a label or description someone improved by hand.
        for cmd in ("\tLen\t", "\tDen\t"):
            self.assertNotIn(cmd, body, f"{cmd.strip()} overwrites on an existing item")


class TestAGutterIsNotEvidence(unittest.TestCase):
    """A review-copy line-number margin verified almost any figure a draft could state.

    PDF extraction hands the margin over inline, so `check_claim_numbers` was reading
    `1 2 3 ... 40` as the paper stating 12, 30 and 40, and the review page was quoting
    the margin instead of the sentence. Both failures are silent, and neither shows up in
    committed data -- only in whichever paper happens to be typeset that way.

    The other direction matters as much: a table of integer measurements must survive,
    because dropping it would reject a figure the paper really does state.
    """

    def test_a_gutter_run_is_dropped(self):
        from validate import deline, figures_in
        gutter = " ".join(str(n) for n in range(1, 41))
        self.assertNotIn("30", figures_in(deline(f"Some prose. {gutter} More prose.")))

    def test_a_table_of_counts_survives(self):
        from validate import deline, figures_in
        # Not consecutive, so not a gutter -- these are counts a claim may cite.
        kept = figures_in(deline("Sizes 12 40 7 33 91 18 across the six splits."))
        for n in ("12", "40", "33", "91"):
            self.assertIn(n, kept)

    def test_latex_thousands_separators_fold_down(self):
        from validate import deline, figures_in
        # How nine of the cached papers actually write their numbers. Unfolded, a claim citing
        # 25,000 was told the figure "is not in the paper" about a paper that states it twice.
        text = deline(r"grew to 25{,}000 and 55{,}000 chars, or 1\,600 items")
        for n in ("25000", "55000", "1600"):
            self.assertIn(n, figures_in(text), n)
        # `values_in` reads only the plain form, so the exact-match path above is what
        # clears a grouped figure -- the rounding tolerance never sees 25,000 either way.

    def test_a_brace_that_is_not_a_separator_is_left_alone(self):
        from validate import deline
        # Only a `{,}` sitting between a digit and exactly three digits is a separator.
        self.assertEqual("set {,} of 12 items", deline("set {,} of 12 items"))

    def test_a_short_run_survives(self):
        from validate import deline
        # Four ascending integers are a sequence in a sentence, not a margin.
        self.assertIn("2 3 4 5", deline("Dimensions 2 3 4 5 were tried."))

    def test_the_number_checker_reads_the_stripped_text(self):
        import validate
        gutter = " ".join(str(n) for n in range(1, 41))
        sidecar = {"claims": [{"id": "c", "kind": "result",
                               "text": "The model was trained on 30 tasks.",
                               "scope": "One benchmark.", "evidence": "Table 1."}]}
        was = validate.ROOT
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, "build", "fulltext"))
            path = os.path.join(tmp, "build", "fulltext", "p.txt")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(f"Prose about tasks. {gutter} More prose.")
            validate.ROOT = tmp
            try:
                errs, skipped = validate.check_claim_numbers([("p.md", sidecar)])
            finally:
                validate.ROOT = was
        self.assertFalse(skipped)
        self.assertTrue(any("30" in e for e in errs), errs)


class TestAPersonWhoLandsHereIsSentOnward(unittest.TestCase):
    """The canonical URL is the machine anchor, so people arrive here by mistake.

    Every registry that a human clicks -- Scholar's Homepage field, ORCID, arXiv -- holds
    this URL, because a machine anchor has to be one URL and never change. The cost is paid
    by the visitor, so the note is on the home page as a box and in every other page's
    footer, since search lands people on a paper far more often than on a home page.
    """

    def test_the_box_names_the_personal_site(self):
        import build_site
        out = build_site.human_note({"other_pages": ["https://example.wixsite.com/someone"]},
                                    box=True)
        self.assertIn("Human?", out)
        self.assertIn("example.wixsite.com/someone", out)
        self.assertIn('rel="me"', out, "it is an identity claim as well as navigation")

    def test_no_second_page_means_no_note_rather_than_an_empty_one(self):
        import build_site
        self.assertEqual("", build_site.human_note({}, box=True))
        self.assertEqual("", build_site.human_note({"other_pages": []}, box=False))


class TestNoLatexLeavesInACitationFile(unittest.TestCase):
    """CITATION.cff is written into a public repo and parsed by other people's tools.

    The bibliography protects capitalization with braces -- `{DORA} The Explorer`,
    `{ICLR} 2018` -- and this file was built from those raw fields, so the brace
    convention would have travelled into GitHub's cite widget, Zenodo, and every
    citation manager that reads it. The display fields are the de-LaTeXed ones.
    """

    def test_the_paper_title_and_venue_arrive_de_latexed(self):
        import sweep_github
        cff = sweep_github.citation_cff(
            {"title": "{DORA} The Explorer", "title_display": "DORA The Explorer",
             "venue": "6th International Conference on Learning Representations, {ICLR} 2018",
             "venue_display": "ICLR 2018", "year": 2018, "type": "inproceedings",
             "authors": ["Leshem Choshen"]},
            {"full_name": "borgr/DORA", "name": "DORA"},
            {"identity": {"name": "Leshem Choshen", "orcid": "0000-0002-0085-6496"}})
        self.assertNotIn("{", cff)
        self.assertIn('title: "DORA The Explorer"', cff)
        self.assertIn('collection-title: "ICLR 2018"', cff)

    def test_a_quote_cannot_end_the_scalar_it_sits_in(self):
        import sweep_github
        cff = sweep_github.citation_cff(
            {"title_display": 'A "quoted" title', "authors": ["Leshem Choshen"]},
            {"full_name": "a/b", "name": "b"}, {"identity": {"name": "Leshem Choshen"}})
        self.assertIn("A 'quoted' title", cff)


class TestAPeriodBeforeASymbolIsNotASentenceEnd(unittest.TestCase):
    """The sentence count is the one cap a rewording cannot always clear.

    "One attainable order is Non-term. < Dep. < SRL < RC < NER < Co-ref. < SPR." is one
    ordering of seven abbreviated task names. It split into four, so a two-sentence claim
    was reported as five and nothing short of renaming the tasks would have fixed it. The
    period is decided by what follows as well as what precedes -- but a lowercase opener
    is a real sentence, since identifiers start them.
    """

    def test_an_abbreviated_enumeration_stays_one_sentence(self):
        from validate import sentences
        self.assertEqual(2, len(sentences(
            "Probing BERT-base gives 196 rankings. One attainable order is "
            "Non-term. < Dep. < SRL < RC < NER < Co-ref. < SPR.")))

    def test_a_sentence_may_start_lowercase(self):
        from validate import sentences
        self.assertEqual(2, len(sentences(
            "High scores partly reflect training overlap. pyFranc is trained on UDHR.")))
        self.assertEqual(2, len(sentences(
            "Same-class examples move closer together. t-SNE plots show it.")))

    def test_an_initial_still_does_not_split(self):
        from validate import sentences
        self.assertEqual(1, len(sentences(
            "Project Debater debated champion H. Natarajan and won.")))

    def test_an_abbreviation_needs_a_boundary_in_front_of_it(self):
        from validate import sentences
        # "fine-tuned LLMs." ends with the string "Ms.", so `endswith` read a real
        # sentence break as an honorific and reported the two sentences after it as one
        # 39-word sentence.
        self.assertEqual(2, len(sentences(
            "The report studies overfitting in fine-tuned LLMs. It pairs an open task "
            "set with a closed one.")))
        self.assertEqual(1, len(sentences("We follow Tenney et al. (2019a) here.")))

    def test_a_title_keeps_its_own_question_mark(self):
        from validate import sentences
        # A paper is named in a claim by its title, and "Will it Merge? On The Causes of
        # Model Mergeability" split in the middle of its own name -- spending one of the
        # two sentences a claim gets on half a title.
        self.assertEqual(2, len(sentences(
            '"Will it Merge? On The Causes of Model Mergeability" gives merging a '
            'per-update notion. The question shifts to which updates merge at all.')))

    def test_a_matrix_named_a_is_not_somebodys_initial(self):
        from validate import sentences
        # The initials rule glued "...and tuning A." to "The guarantee holds...", and the
        # pair was reported as a 36-word sentence that is really 27 and 9.
        self.assertEqual(2, len(sentences(
            "Freezing B and tuning A. The guarantee holds as d/r grows.")))


class TestARequeuedPaperIsRepairedNotRewritten(unittest.TestCase):
    """`--all` re-queues papers that already have text, and text is the reviewed part.

    Thirteen live sidecars carry findings against rules written after they were accepted,
    and eight of those are a single sentence over the word limit. Queued with an empty
    `sidecar` field the only job on offer was writing the paper up again from scratch --
    discarding ten claims a person had read to fix one phrase. The task now arrives
    seeded with what stands and the findings against it.
    """

    def test_the_standing_text_and_its_findings_are_handed_over(self):
        import draft_sidecars
        import sidecar_io
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "drafts"))
            with open(os.path.join(d, "p.md"), "w") as f:
                f.write("---\none_liner: x\nclaims: []\n---\n")
            with mock.patch.object(sidecar_io, "SIDECARS", d), \
                 mock.patch.object(sidecar_io, "DRAFTS",
                                   os.path.join(d, "drafts")), \
                 mock.patch.object(draft_sidecars, "validate_draft",
                                   return_value=(["p.md: broken"], ["p.md: too long"])):
                fm, found = draft_sidecars.standing("p")
        self.assertEqual("x", fm["one_liner"])
        self.assertEqual(["broken", "too long"], found)

    def test_a_paper_with_nothing_on_disk_is_drafted_from_scratch(self):
        import draft_sidecars
        import sidecar_io
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(sidecar_io, "SIDECARS", d), \
                 mock.patch.object(sidecar_io, "DRAFTS", d):
                self.assertEqual((None, []), draft_sidecars.standing("absent"))


class TestACitationFileIsWrittenOnlyWhenItWouldChange(unittest.TestCase):
    """`write_citation_cff` says a file is wanted, not that the live one is wrong.

    Announcing a change on the flag alone left `diff` permanently at one pending repo,
    so a settled run and a run with real work in it printed the same thing, and every
    apply rewrote bytes that already matched. And when a file does need replacing, the
    Contents API rejects the PUT without the existing blob's sha (422, `"sha" wasn't
    supplied`) -- which is how borgr/DORA kept a braced title through the run meant to
    fix it, every write after the first having failed unnoticed.
    """

    def _changes_with_live(self, live_body):
        import sweep_github
        entry = {"repo": "a/b", "write_citation_cff": True, "paper_slug": "s"}
        paper = {"slug": "s", "title_display": "T", "authors": ["Leshem Choshen"]}
        with mock.patch.object(sweep_github, "read_yaml",
                               side_effect=[{"repos": [entry]}, {"papers": [paper]}]), \
             mock.patch.object(sweep_github, "list_repos",
                               return_value=[{"full_name": "a/b", "name": "b",
                                              "topics": [], "description": None,
                                              "homepage": None}]), \
             mock.patch.object(sweep_github, "live_cff", return_value=live_body):
            return list(sweep_github._changes(
                {"identity": {"name": "Leshem Choshen"},
                 "site": {"base_url": "https://x", "papers_path": "/papers/"}}))

    def test_a_matching_file_is_not_a_change(self):
        import sweep_github
        want = sweep_github.citation_cff(
            {"slug": "s", "title_display": "T", "authors": ["Leshem Choshen"]},
            {"full_name": "a/b", "name": "b"}, {"identity": {"name": "Leshem Choshen"}},
            {"repo": "a/b", "write_citation_cff": True, "paper_slug": "s"})
        self.assertEqual([], self._changes_with_live(want))

    def test_a_stale_or_absent_file_is_a_change_and_carries_its_body(self):
        got = self._changes_with_live('title: "{DORA}"\n')
        self.assertEqual(1, len(got))
        self.assertIn("CITATION.cff", got[0][2])
        self.assertIn('title: "T"', got[0][0]["_cff_body"])
        self.assertEqual(1, len(self._changes_with_live(None)))


class TestALiveSidecarIsAskedOfTheDisk(unittest.TestCase):
    """`papers.yaml`'s has_sidecar is only rewritten by the online collect step.

    So between promoting a draft and the next network run -- exactly when somebody
    re-reads the worklist to see what promoting did -- it says the opposite of the truth.
    It claimed 111 of 113 papers still needed drafting on a corpus where all 113 were
    live, and printed `--accept` lines without the `--replace` those files require.
    """

    def test_the_field_is_ignored_in_favour_of_the_file(self):
        import common
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "data", "sidecars"))
            open(os.path.join(d, "data", "sidecars", "here.md"), "w").close()
            with mock.patch.object(common, "ROOT", d):
                self.assertTrue(common.has_live_sidecar("here"))
                self.assertFalse(common.has_live_sidecar("gone"))


class TestTheHomePageListsEveryPaper(unittest.TestCase):
    """No top-ten, and no printed citation counts.

    The readers this site is built for fetch one URL far more often than they crawl, and
    the URL they hold is this one -- it is the canonical anchor in ORCID, Scholar, arXiv
    and every sameAs. A ten-item list left the rest of the corpus reachable only by a
    second hop a single-fetch reader never takes. The count still orders the list; it is
    not shown, because the Semantic Scholar number a reader would compare against Google
    Scholar's is a fraction of it.
    """

    def _papers(self):
        return [{"slug": "a", "title": "Old but cited", "year": 2019, "citations": 300,
                 "venue_display": "ACL 2019"},
                {"slug": "b", "title": "New and cited", "year": 2026, "citations": 4,
                 "venue_display": "ICML 2026"},
                {"slug": "c", "title": "New and not", "year": 2026,
                 "venue_display": "arXiv"}]

    def test_every_paper_is_on_it_newest_year_first(self):
        import build_site
        html = "\n".join(build_site.year_sections(self._papers()))
        for t in ("Old but cited", "New and cited", "New and not"):
            self.assertIn(t, html)
        self.assertLess(html.index("2026"), html.index("2019"))
        self.assertLess(html.index("New and cited"), html.index("New and not"),
                        "within a year the count still decides the order")

    def test_the_count_orders_the_list_but_is_never_printed(self):
        import build_site
        html = "\n".join(build_site.year_sections(self._papers()))
        self.assertNotIn("citations", html)
        self.assertNotIn("300", html)

    def test_a_venue_is_named_the_way_a_reader_names_it(self):
        import build_site
        long = ("Advances in Neural Information Processing Systems 36: Annual Conference "
                "on Neural Information Processing Systems 2023, NeurIPS 2023, New Orleans")
        self.assertEqual("NeurIPS 2023",
                         build_site.venue_of({"venue": long, "venue_display": "NeurIPS 2023"}))
        # No short form on the record: short_venue recovers the acronym from the
        # proceedings title rather than truncating it mid-word, which is what a blind
        # 60-character cut used to publish ("...Systems 36: Annual C").
        self.assertEqual("NeurIPS 2023", build_site.venue_of({"venue": long}))
        self.assertEqual("preprint", build_site.venue_of({}))


class TestAnArxivLandingPageIsNotAPaper(unittest.TestCase):
    """The abstract page has to be refused by what it says, not by how long it is.

    One paper's landing page came to 4,344 characters -- title, full abstract, author list,
    site chrome -- and so cleared the 4,000-character stub floor, which sent a sidecar to be
    drafted from an abstract. Every claim on it was `context`, because the text held no
    result to state. Raising the floor would reject real two-page papers instead.
    """

    def test_the_landing_page_is_refused_so_the_chain_reaches_the_pdf(self):
        import fulltext
        html = ("<html><body>Title: A Paper. View a PDF of the paper titled A Paper, by "
                "Someone. Abstract: " + "words " * 900 + "</body></html>").encode()
        with mock.patch.object(fulltext, "get", return_value=html):
            text, floor = fulltext._fetch("html", "https://arxiv.org/abs/2106.00745")
        self.assertEqual("", text, "a landing page must not be accepted as a paper")
        self.assertGreater(len(fulltext.html_to_text(html)), fulltext.MIN_CHARS,
                           "and length alone would have accepted it")

    def test_a_rendered_paper_is_still_accepted(self):
        import fulltext
        html = ("<html><body>1 Introduction " + "content " * 900 + "</body></html>").encode()
        with mock.patch.object(fulltext, "get", return_value=html):
            text, _ = fulltext._fetch("html", "https://arxiv.org/html/2106.00745")
        self.assertIn("Introduction", text)


class TestAQuoteLinksIntoThePaper(unittest.TestCase):
    """The review page's quotes are links; the published page's are not.

    Two separate decisions. Linking on the review page is free -- `review_page` writes
    outside `build/site/`, so `--deploy` cannot reach it -- and it turns checking a claim
    from a search into a click. Publishing the same link once per claim would add no
    retrievable fact to a passage that already carries the canonical paper link, so
    `at_sentence` is called from the review page only.

    A fragment needs the paper's own HTML. An OpenReview or PDF-only paper has nowhere to
    scroll to, and the honest answer there is no link rather than a broken one.
    """

    HTML = {"html": "https://arxiv.org/html/2402.14992v2"}

    def test_a_fragment_is_built_for_an_html_paper(self):
        from sidecar_review import at_sentence
        url = at_sentence(self.HTML, "ing examples per scenario are enough to estima")
        self.assertTrue(url.startswith(self.HTML["html"] + "#:~:text="), url)
        # First and last tokens go: a window cut mid-word never matches as a substring.
        self.assertNotIn("ing", urllib.parse.unquote(url.split("text=")[1]).split())
        self.assertIn("scenario", urllib.parse.unquote(url.split("text=")[1]))

    def test_a_paper_with_no_html_gets_no_link(self):
        from sidecar_review import at_sentence
        self.assertEqual("", at_sentence({"openreview": "https://openreview.net/f"}, "x y z"))
        self.assertEqual("", at_sentence({"arxiv_pdf": "https://arxiv.org/pdf/1.pdf"}, "x y z"))
        self.assertEqual("", at_sentence(self.HTML, "   "))

    def test_only_the_review_page_links_quotes(self):
        # Module-level functions only, so a call inside a nested helper is attributed to
        # the function that owns it: `review_page` builds a helper per claim block, and
        # walking every def counts that helper as a second caller.
        callers = set()
        for path in glob.glob(os.path.join(ROOT, "scripts", "*.py")):
            with open(path, encoding="utf-8") as fh:
                tree = ast.parse(fh.read())
            callers |= {fn.name for fn in tree.body
                        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef))
                        for n in ast.walk(fn)
                        if isinstance(n, ast.Call)
                        and getattr(n.func, "id", "") == "at_sentence"}
        self.assertEqual({"review_page"}, callers)


if __name__ == "__main__":
    unittest.main(verbosity=2)


class TestADroppedConnectionIsNotARefusal(unittest.TestCase):
    """One `RemoteProtocolError` mid-stream used to spend a paper's whole repair budget."""

    def setUp(self):
        import llm
        self.L = llm
        # Named, not imported: `httpx` is not a CI requirement -- it arrives with the
        # `anthropic` SDK, which only the api backend needs -- and the predicate matches on
        # the type's *name* precisely so it need not import the transport library. Standing
        # these up by hand tests the mechanism the drafter actually uses.
        self.err = {n: type(n, (Exception,), {})
                    for n in ("RemoteProtocolError", "ConnectError", "ConnectTimeout",
                              "ReadError")}
        self.slept = []
        self._real = llm.time.sleep
        llm.time.sleep = self.slept.append

    def tearDown(self):
        self.L.time.sleep = self._real

    def test_a_transport_error_is_retried_and_then_succeeds(self):
        calls = []

        def flaky():
            calls.append(1)
            if len(calls) < 3:
                raise self.err["RemoteProtocolError"]("incomplete chunked read")
            return "a reply"

        self.assertEqual(self.L.with_retries(flaky, "a-paper repair 1"), "a reply")
        self.assertEqual(len(calls), 3)
        self.assertEqual(self.slept, [5, 10])         # backs off, does not hammer

    def test_a_refusal_is_not_retried(self):
        calls = []

        def refused():
            calls.append(1)
            raise ValueError("400: unknown field `output_config`")

        with self.assertRaises(ValueError):
            self.L.with_retries(refused, "a-paper")
        self.assertEqual(len(calls), 1)               # the ladder gets to climb immediately
        self.assertEqual(self.slept, [])

    def test_a_permanent_outage_gives_up_and_re_raises(self):
        calls = []

        def dead():
            calls.append(1)
            raise self.err["ConnectError"]("no route to host")

        with self.assertRaises(self.err["ConnectError"]):
            self.L.with_retries(dead, "a-paper")
        self.assertEqual(len(calls), self.L.TRANSIENT_TRIES + 1)

    def test_which_failures_count_as_the_connections_fault(self):
        wrapped = RuntimeError("stream died")
        wrapped.__cause__ = self.err["ReadError"]("peer went away")
        for e in (self.err["RemoteProtocolError"]("x"), self.err["ConnectTimeout"]("x"), wrapped,
                  type("Busy", (Exception,), {"status_code": 529})()):
            self.assertTrue(self.L._transient(e), f"{type(e).__name__} should be retried")
        for e in (ValueError("bad schema"), KeyError("claims"),
                  type("Bad", (Exception,), {"status_code": 400})()):
            self.assertFalse(self.L._transient(e), f"{type(e).__name__} must not be retried")


class TestACountIsAMagnitudeForCoverage(unittest.TestCase):
    """A survey states its findings as counts, and the coverage rule could not see them.

    `figures` drops bare single digits because `check_claim_numbers` cannot verify one --
    every paper's own text contains all ten. Figure *coverage* asks a different question:
    whether the claim carries a number a reader would quote. Sharing the one definition
    reported "0 of 9 result claims state a figure" on a survey whose claims say 4 families,
    7 embedding-based routers and 5 classifier-based ones, with no honest repair available.
    """

    def test_a_bare_digit_counts_for_coverage_and_not_for_verification(self):
        from validate import figures, quotable
        self.assertEqual(figures("MoErging methods fall into 4 families"), [])
        self.assertEqual(quotable("MoErging methods fall into 4 families"), ["4"])

    def test_a_page_whose_claims_all_state_counts_is_not_flagged(self):
        from validate import check_readability
        ok = {"claims": [{"id": f"c{i}", "kind": "result",
                          "text": f"The taxonomy names {i} routing families.",
                          "scope": "The methods catalogued in the survey."}
                         for i in range(2, 6)]}
        found = [f for f in check_readability([("ok.md", ok)])
                 if "state a figure" in f]
        self.assertEqual(found, [])

    def test_a_multi_digit_number_is_still_required_to_be_checkable(self):
        """The verification path must not inherit the looser definition."""
        from validate import figures
        self.assertEqual(figures("accuracy rose to 63.45%"), ["63.45"])


class TestAPaperWithNoMeasurementsIsNotAskedForFigures(unittest.TestCase):
    """SERRANT reports one distinct figure in its entire text.

    It is an annotation-scheme paper: its claims say what the tool does to an edit, which
    is demonstrated rather than measured, so they are `result` claims with nothing to
    quote. The corpus median is 154 distinct figures and the next-lowest paper has 18, so
    a floor separates that one paper from every other without excusing any of them.
    """

    def _fulltext(self, slug, text):
        import validate as V
        d = os.path.join(V.ROOT, "build", "fulltext")
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, f"{slug}.txt")
        self.addCleanup(lambda: os.path.exists(path) and os.remove(path))
        with open(path, "w") as f:
            f.write(text)

    def test_a_paper_that_reports_nothing_exempts_its_page(self):
        from validate import paper_reports_figures
        self._fulltext("_t_scheme", "A rule-based classifier (Bryant et al., 2017).")
        self.assertFalse(paper_reports_figures("_t_scheme"))

    def test_citation_years_are_not_reported_figures(self):
        from validate import paper_reports_figures
        self._fulltext("_t_years", " ".join(f"(Author et al., {y})"
                                           for y in range(1995, 2025)))
        self.assertFalse(paper_reports_figures("_t_years"))

    def test_a_paper_with_results_is_still_asked(self):
        from validate import paper_reports_figures
        self._fulltext("_t_results", " ".join(f"{n}.5% accuracy" for n in range(30, 60)))
        self.assertTrue(paper_reports_figures("_t_results"))

    def test_an_uncached_paper_is_asked_rather_than_excused(self):
        from validate import paper_reports_figures
        self.assertTrue(paper_reports_figures("_t_no_such_slug_at_all"))
        self.assertTrue(paper_reports_figures(None))


class TestAForkKeepsTheCommentsAndDropsTheDecisions(unittest.TestCase):
    """The reset has to lose one researcher's judgement and keep the file's meaning.

    Both halves are load-bearing. An emptied file that also loses its comment block
    leaves the fork with a `declines.yaml` whose semantics nobody can recover; a file
    that keeps its contents publishes someone else's decision to skip a paper.
    """

    def test_the_leading_comment_block_survives(self):
        from bootstrap_fork import header
        text = "# what this is\n# and why\n\nitems: [a]\n# not a header comment\n"
        self.assertEqual(header(text), "# what this is\n# and why\n")

    def test_documentation_strings_stay_and_data_goes(self):
        import yaml
        from bootstrap_fork import rewrite
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "declines.yaml")
            open(p, "w").write("# why this file exists\nnote: read me\n"
                               "sections: [worklist]\nitems: [one, two]\n")
            rewrite(p, {"sections": [], "items": []})
            out = open(p).read()
            self.assertIn("# why this file exists", out)
            got = yaml.safe_load(out)
            self.assertEqual(got, {"note": "read me", "sections": [], "items": []})

    def test_every_emptied_key_exists_in_the_real_file(self):
        """A key renamed in `data/` and not here would be silently left populated."""
        import yaml
        from bootstrap_fork import EMPTY
        for name, empties in EMPTY.items():
            path = os.path.join(ROOT, "data", name)
            if not os.path.exists(path):
                continue
            doc = yaml.safe_load(open(path)) or {}
            for key, blank in empties.items():
                self.assertIn(key, doc, f"data/{name}: {key} no longer exists")
                self.assertIsInstance(doc[key], type(blank),
                                      f"data/{name}: {key} is not a {type(blank).__name__}")


class TestAHandoverBundleDecidesNothing(unittest.TestCase):
    """The bundle exists to do a colleague's lookups, not to make their choices.

    The dangerous field is `site.repo`: `build_site.py --deploy` writes the whole repo, so
    a guessed Pages repo replaces whatever page is already served there. The obvious guess
    -- the homepage they already have -- is exactly the wrong one.
    """

    FOUND = {
        "name": "Ada Example Lovelace",
        "semantic_scholar": [{"authorId": "1", "paperCount": 9, "citationCount": 40},
                             {"authorId": "2", "paperCount": 1, "citationCount": 3}],
        "dblp_name": "Ada Example Lovelace", "dblp_pid": "999/1234",
        "orcid": [{"orcid": "0000-0001-0000-0001", "name": "Ada Example Lovelace",
                   "institutions": ["Somewhere"]}],
        "paper_count": 10, "arxiv_count": 7,
        "keyword_candidates": ["analytical engine"], "top_papers": [],
    }

    def _cfg(self):
        import yaml
        from handover import config_text
        return yaml.safe_load(config_text(self.FOUND["name"], self.FOUND,
                                          "adaex", "https://adaex.github.io"))

    def test_the_deploy_target_is_never_guessed(self):
        self.assertIsNone(self._cfg()["site"]["repo"])

    def test_a_found_record_is_filled_in_rather_than_asked_for(self):
        cfg = self._cfg()
        self.assertEqual(cfg["ids"]["semantic_scholar"], ["1", "2"])
        self.assertEqual(cfg["ids"]["semantic_scholar_primary"], "1")
        self.assertEqual(cfg["ids"]["dblp_pid"], "999/1234")
        self.assertEqual(cfg["identity"]["orcid"], "0000-0001-0000-0001")

    def test_a_multiword_surname_keeps_its_words_together(self):
        """`Rott Shaham, Tamar` is the citation form; `Rott, Shaham, Tamar` is two people."""
        self.assertIn("Rott Shaham, Tamar", self._variants("Tamar Rott Shaham"))

    def _variants(self, name):
        import yaml
        from handover import config_text
        found = dict(self.FOUND, name=name)
        return yaml.safe_load(config_text(name, found, None, None))["identity"]["name_variants"]

    def test_keyword_candidates_are_suggestions_not_keywords(self):
        """Emitted commented out: a keyword is a phrase someone types, not a frequent one."""
        from handover import config_text
        text = config_text(self.FOUND["name"], self.FOUND, None, None)
        self.assertIn("#   - analytical engine", text)
        self.assertEqual(self._cfg()["identity"]["keywords"], [])

    def test_ambiguous_orcid_becomes_a_question(self):
        import yaml
        from handover import config_text
        found = dict(self.FOUND, orcid=[{"orcid": "0000-0001-0000-0001", "name": "x",
                                         "institutions": []},
                                        {"orcid": "0000-0001-0000-0002", "name": "x",
                                         "institutions": []}])
        text = config_text(found["name"], found, None, None)
        self.assertIsNone(yaml.safe_load(text)["identity"]["orcid"])
        self.assertIn("0000-0001-0000-0002", text)

    def test_a_lookup_that_did_not_answer_is_not_a_fact_about_them(self):
        """An empty result reads as a fact in all four lookups -- no ORCID under this name,
        no DBLP page, no arXiv papers -- and the bundle is a note the author sends. So a
        refusal writes nothing rather than a bundle that tells a colleague to register the
        ORCID they have had for ten years."""
        import handover

        def refuse(no):
            """A lookup that answers or refuses, setting `_refused` the way `fetched` does."""
            def f(*a, **kw):
                handover._refused = "example.org -> HTTP 500" if no else ""
                return [] if no else [{"authorId": "1", "paperCount": 9}]
            return f

        old = handover._refused
        try:
            for st in (0, 429, 500):
                handover._refused = ""
                with mock.patch.object(handover, "get_status", lambda _u, **kw: (st, b"")):
                    self.assertEqual([], handover.orcids("Ada Example Lovelace"))
                    self.assertEqual((None, None), handover.dblp_pid("Ada Example Lovelace"))
                self.assertTrue(handover._refused, "status %s passed as an answer" % st)

            # Both guards, each reached the way a run reaches it: Semantic Scholar refusing,
            # which decides whether there is a corpus at all, and Semantic Scholar answering
            # while ORCID refuses, where the absence has already been read into `found`.
            for s2_refused in (True, False):
                handover._refused = ""
                with tempfile.TemporaryDirectory() as d:
                    argv = ["handover.py", "Ada Example Lovelace", "--out", d]
                    with mock.patch.object(sys, "argv", argv), \
                         mock.patch.object(handover, "s2_records", refuse(s2_refused)), \
                         mock.patch.object(handover, "s2_papers", lambda a: []), \
                         mock.patch.object(handover, "dblp_pid", lambda n: (None, None)), \
                         mock.patch.object(handover, "orcids", refuse(True)):
                        with self.assertRaises(SystemExit) as e:
                            handover.main()
                    self.assertIn("did not answer", str(e.exception.code))
                    self.assertEqual([], os.listdir(d), "a refusal wrote a bundle")

            handover._refused = ""
            with mock.patch.object(handover, "get_status",
                                   lambda _u, **kw: (200, b'{"result": {}}')):
                self.assertEqual((None, None), handover.dblp_pid("Ada Example Lovelace"))
            self.assertEqual("", handover._refused)
        finally:
            handover._refused = old


class TestAnalyticsIsOptAndWhitelisted(unittest.TestCase):
    """The one config value that becomes executable script on every published page.

    So the failure modes are worth pinning: silently emitting nothing when a provider was
    named, and accepting a provider name nobody wrote a snippet for.
    """

    def test_no_provider_emits_nothing(self):
        from build_site import analytics_snippet
        self.assertEqual(analytics_snippet({}), "")
        self.assertEqual(analytics_snippet({"site": {"analytics": {"provider": None}}}), "")

    def test_a_named_provider_without_its_value_is_an_error(self):
        """Not a silent no-op: a site that thinks it has analytics and does not is worse."""
        from build_site import analytics_snippet
        with self.assertRaises(SystemExit):
            analytics_snippet({"site": {"analytics": {"provider": "plausible"}}})

    def test_an_unknown_provider_is_an_error(self):
        from build_site import analytics_snippet
        with self.assertRaises(SystemExit):
            analytics_snippet({"site": {"analytics": {"provider": "matomo",
                                                     "domain": "x.example"}}})

    def test_the_value_is_escaped_into_the_snippet(self):
        from build_site import analytics_snippet
        out = analytics_snippet({"site": {"analytics": {"provider": "plausible",
                                                       "domain": 'a"b'}}})
        self.assertIn("plausible.io/js/script.js", out)
        self.assertNotIn('data-domain="a"b"', out)

    def test_it_reaches_every_page_not_just_the_homepage(self):
        """Unlike the verification tags, which are homepage-only by design."""
        import build_site
        with mock.patch.object(build_site, "_ANALYTICS", '  <script defer id="t"></script>\n'):
            self.assertIn('id="t"', build_site.page("t", "<p>b</p>"))


class TestWikipediaAsksOnlyForCorrections(unittest.TestCase):
    """The surface with the most leverage and the least room to act on it.

    Wikipedia carries roughly half the citations in ChatGPT answers, and WP:COI plus
    WP:SELFCITE forbid the author from adding anything. The emitter's whole scope is
    therefore checks on what other people wrote, and these tests hold that line -- both
    against drifting back toward asking for an insertion, and against the quieter failure of
    a confident wrong match, since a page that sends you to check "Brushstrokes in Flight"
    stops being read.
    """

    def _mod(self):
        import wikipedia_tasks
        return wikipedia_tasks

    def test_a_case_insensitive_match_is_not_coverage(self):
        """`ColD Fusion` is not covered by the article on cold fusion."""
        w = self._mod()
        with mock.patch.object(w, "search", lambda q, limit=20: [
                {"title": "Cold fusion", "snippet": "the <b>cold fusion</b> claim"}]), \
             mock.patch.object(w, "in_domain", lambda t: True):
            self.assertEqual(w.mentions("ColD Fusion"), [])

    def test_a_match_outside_the_field_is_not_a_check(self):
        """`RLCR` matched five sculptures and a rotisserie oven."""
        w = self._mod()
        with mock.patch.object(w, "search", lambda q, limit=20: [
                {"title": "Brushstrokes in Flight", "snippet": "RLCR"}]), \
             mock.patch.object(w, "in_domain", lambda t: False):
            self.assertEqual(w.mentions("RLCR"), [])

    def test_a_redirect_or_disambiguation_page_is_not_an_article(self):
        """`DORA` resolved to an EU regulation and silently dropped the item."""
        w = self._mod()
        pages = [{"title": "DORA", "redirect": True}]
        with mock.patch.object(w, "api", lambda **kw: {"query": {"pages": pages}}):
            self.assertIsNone(w.exists("DORA"))
        pages[0] = {"title": "DORA", "pageprops": {"disambiguation": ""}}
        with mock.patch.object(w, "api", lambda **kw: {"query": {"pages": pages}}):
            self.assertIsNone(w.exists("DORA"))

    def test_a_coinage_colliding_with_an_established_term_is_skipped(self):
        """`E-values` is a reinforcement learning quantity here, statistics on Wikipedia."""
        w = self._mod()
        for term in ("E-values", "Sloth", "Genie", "DORA"):
            self.assertTrue(w.AMBIGUOUS.match(term), term)

    def test_a_two_word_term_survives_the_search_match_spans(self):
        """The API wraps every matched word separately, so the term is not contiguous."""
        w = self._mod()
        raw = ("in partnership with [[IBM]]'s \"[[<span class=\"searchmatch\">Project</span> "
               "<span class=\"searchmatch\">Debater</span>]]\".")
        with mock.patch.object(w, "search", lambda q, limit=20: [
                {"title": "Open to Debate", "snippet": raw}]), \
             mock.patch.object(w, "in_domain", lambda t: True):
            got = w.mentions("Project Debater")
        self.assertEqual(1, len(got))
        self.assertEqual('in partnership with IBM\'s "Project Debater".', got[0]["says"])

    def test_the_quoted_line_is_wikitext_no_longer(self):
        """`insource:` matches source, and a row is only worth reading if it reads."""
        w = self._mod()
        # `&ndash;` written literally in an article arrives escaped twice, so `snippet` and
        # `plain` unescape once each.
        self.assertEqual("Automated reasoning Machine learning Project Debater (2018) – x",
                         w.plain("*** [[Automated reasoning]] *** [[Machine learning]] * "
                                 "[[Project Debater]] (2018) &ndash; x"))
        self.assertEqual("published in Nature",
                         w.plain("published in \'\'[[Nature (journal)|Nature]]\'\'"))
        self.assertEqual("Similarly, PromptEval estimates",
                         w.plain('<ref name="auto" /> Similarly, PromptEval estimates'))
        self.assertEqual("Roy Bogin – joined",
                         w.plain(w.snippet({"snippet": "Roy Bogin &amp;ndash; joined"})))

    def test_a_name_inside_a_citation_or_an_infobox_is_not_a_claim_to_check(self):
        """A row quoting `m|first4=Roy|last5=Bogin` asks nothing answerable. The match is in
        a reference's author list or an infobox field, which cites the work rather than
        describing it, and the snippet carries no `{{` for the template rule to find."""
        w = self._mod()
        self.assertEqual("m |l", w.plain("m|first4=Roy|last5=Bogin|first5=Ben|"
                                        "last7=Choshen|first7=Leshem|l"))
        with mock.patch.object(w, "search", lambda q, limit=20: [
                {"title": "Noam Slonim",
                 "snippet": "Jerusalem | known_for = Project Debater | awards = IBM"}]), \
             mock.patch.object(w, "in_domain", lambda t: True):
            self.assertEqual([], w.mentions("Project Debater"))
        # A table cell is content and stays: no `name = value`, so nothing matches.
        self.assertEqual("| Project Debater || 2018 || IBM",
                         w.plain("| Project Debater || 2018 || IBM"))

    def test_a_see_also_link_or_a_category_is_not_a_claim_to_check(self):
        """A footer match is one bare link among others. An outline entry with a gloss is a
        description and stays, which is what separates the two."""
        w = self._mod()
        with mock.patch.object(w, "search", lambda q, limit=20: [
                {"title": "Artificial intelligence and moral enhancement",
                 "snippet": "Multi-agent systems [[Project Debater]] ==References== "
                            "[[Category:Bioethics]]"}]), \
             mock.patch.object(w, "in_domain", lambda t: True):
            self.assertEqual([], w.mentions("Project Debater"))
        with mock.patch.object(w, "search", lambda q, limit=20: [
                {"title": "Outline of artificial intelligence",
                 "snippet": "* [[Project Debater]] (2018) – artificially intelligent "
                            "computer system"}]), \
             mock.patch.object(w, "in_domain", lambda t: True):
            self.assertEqual(1, len(w.mentions("Project Debater")))

    def test_every_worklist_row_carries_what_the_article_says(self):
        """A row asking whether a description is wrong, without the description, is a bug.

        The reader cannot judge six articles they have to open first, and the text is in
        hand either way -- the search returns it with the hit.
        """
        import update
        out = "\n".join(update.wikipedia_checks(
            {"already_mentions": [{"title": "Argument technology", "says": "names you here"}],
             "checks": [{"term": "PromptEval", "citations": 85,
                         "articles": [{"title": "Prompt engineering",
                                       "says": "PromptEval estimates performance"}]}],
             "absent": 35}))
        self.assertIn("2 of your coinages across 2 article(s)", out)
        self.assertIn("  > names you here", out)
        self.assertIn("  > PromptEval estimates performance", out)
        self.assertIn("**PromptEval** in [Prompt engineering]", out)
        # An article that mentions the author *is* the row's subject, so it is not labelled
        # with itself.
        self.assertNotIn("**Argument technology** in", out)
        self.assertIn("wikipedia.org/wiki/Talk:Prompt_engineering", out)

    def test_a_state_file_written_before_the_text_existed_still_renders(self):
        import update
        out = "\n".join(update.wikipedia_checks(
            {"already_mentions": ["Argument technology"], "checks": []}))
        self.assertIn("[Argument technology](https://en.wikipedia.org/wiki/", out)

    def test_no_insertion_is_ever_asked_for(self):
        """The whole page is checks. A drafted request to add a mention is the regression."""
        text = open(os.path.join(ROOT, "tasks", "wikipedia.md")).read().lower()
        for banned in ("edit coi", "suggested addition", "== ", "propose a mention"):
            self.assertNotIn(banned, text, f"{banned!r} is back in tasks/wikipedia.md")
        for banned in ("{{edit coi", "suggested addition"):
            self.assertNotIn(banned, open(os.path.join(ROOT, "WORKLIST.md")).read().lower())

    def test_an_unread_api_does_not_write_a_page_saying_there_is_nothing_to_check(self):
        """Every section of this page is built from the absence of a hit, so a refused run
        would report each one as clear -- articles naming the author, coinages written up
        elsewhere, field articles to improve -- and move every coinage to the list that says
        nothing is to be done. Nothing on that page reads as wrong."""
        w = self._mod()
        old = w._refused
        try:
            for st in (0, 429, 500):
                w._refused = ""
                with mock.patch.object(w, "get_status", lambda _u, **kw: (st, b"")):
                    self.assertEqual({}, w.api(titles="Project Debater"))
                self.assertTrue(w._refused, "status %s passed as an answer" % st)
                # One refusal stands for the run: the rest of the ~100 calls are not sent.
                with mock.patch.object(w, "get_status",
                                       lambda _u, **kw: self.fail("kept fetching")):
                    self.assertEqual({}, w.api(titles="Sloth"))
            with tempfile.TemporaryDirectory() as d:
                out, state = os.path.join(d, "wikipedia.md"), os.path.join(d, "s.json")
                with mock.patch.object(w, "OUT", out), \
                     mock.patch.object(w, "STATE", state), \
                     mock.patch.object(sys, "argv", ["wikipedia_tasks.py"]):
                    with self.assertRaises(SystemExit) as e:
                        w.main()
                self.assertEqual(1, e.exception.code)
                self.assertEqual([], os.listdir(d), "a refusal wrote a page")
            w._refused = ""
            with mock.patch.object(w, "get_status",
                                   lambda _u, **kw: (200, b'{"query": {"pages": []}}')):
                self.assertEqual({"query": {"pages": []}}, w.api(titles="Sloth"))
            self.assertEqual("", w._refused)
        finally:
            w._refused = old


class TestAQuestionGroupIsAFormNotAList(unittest.TestCase):
    """The `q: [a, b, c]` shape and what replaced it.

    The old rule said "2-4 paraphrases, and vary them deliberately", which is a rule that
    names what to cover and then leaves the drafter to decide whether it did. It produced
    3692 phrasings, 90% third person and mostly rewordings of one sentence, every one of
    them satisfying the letter of it. So a group is now four named routes -- and the
    regression to guard is not a formatting one: it is a rule going back to describing a
    thing nobody has to fill in.
    """

    def _shape(self, group: dict) -> str:
        import validate as V
        fm = {"claims": [{"id": "c1", "kind": "result", "text": "x", "scope": "y"}],
              "qa": [dict(group, answered_by=["c1"])]}
        errs = V.check_sidecar_shape([("d.md", fm)])
        # Only the question-group complaints. A one-claim fixture also trips the claim
        # bands, and asserting on the whole string would pass for the wrong reason.
        return " ".join(e for e in errs if "qa[" in e)

    def test_a_keyword_string_is_refused_and_a_question_is_not(self):
        """Q1, as a check. A phrasing is published twice -- as page text and as a
        `Question.name` -- and a keyword string is penalised in the first place and
        unreadable in the second."""
        bad = self._shape({"ask": {"plain": "ties merging retraining required",
                                   "jargon": "task vector interference"}})
        self.assertIn("not a question", bad)
        self.assertEqual("", self._shape(
            {"ask": {"plain": "why does averaging fine-tuned weights hurt performance?",
                     "jargon": "what causes degradation when task vectors are added?"}}))

    def test_one_route_is_not_enough_and_plain_is_the_one_required(self):
        """Q2 and Q3 as structure: the floor is `plain` plus one other vocabulary."""
        self.assertIn("only `plain` is filled", self._shape(
            {"ask": {"plain": "what makes two fine-tuned models mergeable?"}}))
        self.assertIn("no `plain` phrasing", self._shape(
            {"ask": {"jargon": "what predicts task-vector interference?",
                     "practitioner": "should I merge my own adapters?"}}))

    def test_a_legacy_group_is_exempt_until_it_is_redrafted(self):
        """D5's rule, applied to the roles: 1263 groups were migrated without guessing
        which route each phrasing took, so asking them for `plain` would be asking the
        author to re-review what they already accepted."""
        self.assertEqual("", self._shape(
            {"ask": {"unsorted": ["Why do some finetuned models merge well?",
                                  "What determines whether merging succeeds?"]}}))

    def test_no_live_sidecar_still_carries_the_old_shape(self):
        import glob
        import re

        import yaml
        for path in sorted(glob.glob(os.path.join(ROOT, "data", "sidecars", "*.md"))):
            m = re.search(r"^---\n(.*?)^---\n", open(path).read(), re.S | re.M)
            fm = yaml.safe_load(m.group(1)) or {}
            for i, g in enumerate(fm.get("qa") or []):
                where = f"{os.path.basename(path)} qa[{i}]"
                self.assertNotIn("q", g, f"{where} still holds `q`")
                self.assertNotIn("answers", g, f"{where} still holds `answers`")
                self.assertIn("ask", g, where)

    def test_the_drafter_is_told_the_form_rather_than_the_coverage(self):
        """The prompt is read verbatim from docs/SIDECAR.md §2, so the rule lives there or
        it does not bind the model at all."""
        from common import QA_ROLES, rules_block
        block = rules_block("docs/SIDECAR.md")
        for role in QA_ROLES:
            self.assertIn(f"`{role}`", block, f"the prompt never names the {role} route")
        self.assertIn("Never emit `unsorted`", block)
        self.assertNotIn("2–4 paraphrases", block)

    def test_a_dummy_it_is_not_an_unbound_reference(self):
        """The self-containment check exists to catch a reference with nothing on screen
        to point at. Expletive `it` points at nothing by construction -- the infinitive
        that follows is the subject -- and the corpus pass flagged 21 of those because
        the exemption required the adjective to sit flush against the `to`."""
        from validate import _UNBOUND
        for q in ("Is it worth keeping every checkpoint's loss to fit a scaling law?",
                  "Is it better to train several small models or fewer large ones?",
                  "Is it true that merging always beats ensembling?"):
            self.assertIsNone(_UNBOUND.search(q), q)
        for q in ("Does it generalize to new tasks?", "Do they overlap?",
                  "Does it work on the models that I merge?"):
            self.assertIsNotNone(_UNBOUND.search(q), q)

    def test_the_task_role_is_asked_not_described(self):
        """The rules block has to ask `task` for a question, because it is read as an order.

        It used to gloss the role as "someone describing what they are trying to do", and
        72 of the first rerouted groups obliged with a description ending in a period --
        a sentence about a person, which nobody types into a search box. The role rules
        live in one place, so this is the one place that can be wrong.
        """
        from common import rules_block
        block = rules_block("docs/SIDECAR.md")
        self.assertNotIn("someone describing what they are trying to do", block)
        self.assertIn("natural question, ending in `?`", block)
        self.assertIn("period is a statement", block)

    def test_the_reroute_prompt_keeps_no_copy_of_the_question_rules(self):
        """`--reroute` reads the same block, so the two can never disagree."""
        import sidecar_repair as D
        self.assertIn("{rules}", D.ROUTES)
        self.assertNotIn("ending in `?`", D.ROUTES.replace("{rules}", ""))


class TestAFailedGhReadIsNotAnEmptyOne(unittest.TestCase):
    """The three `gh` failure policies stay distinct, and none of them invents an answer.

    There were four hand-written `subprocess.run(["gh", ...])` wrappers, each with its own
    idea of failure: one returned `""`, one returned `None`, one raised, one handed back the
    exit code. Consolidating them is only safe if the policies survive, and the dangerous
    direction is the write path silently reading nothing -- `list_repos` returning `[]` on a
    failed page reads as "you own no repos" and a sweep over that changes nothing while
    reporting success.
    """

    def test_the_read_helpers_report_absence_and_the_write_path_raises(self):
        import common
        import sweep_github
        real = common.gh
        common.gh = lambda *a, **kw: (_ for _ in ()).throw(
            RuntimeError("boom")) if kw.get("check") else (1, "404")
        try:
            self.assertEqual(common.gh_text("api", "x"), "")
            self.assertIsNone(common.gh_json("api", "x"))
            with self.assertRaises(RuntimeError):
                common.gh("api", "x", check=True)
            with self.assertRaises(RuntimeError):
                sweep_github.list_repos({"ids": {"github": "nobody"}})
        finally:
            common.gh = real

    def test_a_missing_gh_binary_raises_even_on_a_read(self):
        """No `gh` installed is not an answer, so it stops the run instead of reading empty."""
        import common
        with mock.patch("subprocess.run", side_effect=FileNotFoundError("gh")):
            for call in (lambda: common.gh("api", "x"),
                         lambda: common.gh_text("api", "x"),
                         lambda: common.gh_json("api", "x")):
                with self.assertRaises(RuntimeError):
                    call()

    def test_only_common_runs_the_gh_binary(self):
        """One implementation, so a timeout or a policy change lands everywhere at once."""
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        offenders = []
        for path in sorted(glob.glob(os.path.join(root, "scripts", "*.py"))
                           + glob.glob(os.path.join(root, "measure", "*.py"))):
            if os.path.basename(path) in ("common.py", "build_site.py"):
                continue          # build_site clones a repo, it does not read the API
            if re.search(r'subprocess\.\w+\(\s*\[\s*"gh"', open(path).read()):
                offenders.append(os.path.basename(path))
        self.assertEqual(offenders, [], "re-implements common.gh")


class TestASidecarPathHasOneOwner(unittest.TestCase):
    """`sidecar_io` builds every sidecar path, so repointing one directory moves all four.

    The four modules each hold their own `DRAFTS`, so a second module joining the slug
    itself reads its own copy: repointing `sidecar_io.DRAFTS` would then leave that
    module writing into `data/sidecars/drafts/` while everything else used the temp dir.
    """

    def test_only_sidecar_io_joins_a_slug_onto_a_sidecar_directory(self):
        joiner = re.compile(r"os\.path\.join\(\s*(DRAFTS|SIDECARS)\b")
        for path in sorted(glob.glob(os.path.join(ROOT, "scripts", "*.py"))):
            if os.path.basename(path) == "sidecar_io.py":
                continue
            with open(path, encoding="utf-8") as fh:
                hits = joiner.findall(fh.read())
            self.assertEqual([], hits,
                             f"{os.path.basename(path)} builds its own sidecar path -- "
                             f"use sidecar_io.draft_path/live_path/draft_paths/live_paths")


class TestCoauthorResolutionBatchesOnlyIdentifierMatches(unittest.TestCase):
    """The one rule this pass cannot get wrong.

    A P50 pointing at the wrong person welds a stranger's item to your paper, and the batch
    is pasted without review. So the batch may contain only matches an outside record made
    -- ORCID to ORCID, or a DBLP author page listing this same paper -- and a name that
    nothing but its own spelling supports stays on the review list however obvious it looks.
    """

    def _module(self):
        import wikidata_coauthors as wc
        importlib.reload(wc)
        self.addCleanup(importlib.reload, wc)
        return wc

    def _fixture(self, wc, strings, p50=(), orcids=None, by_orcid=None, by_name=None,
                 dblp=None):
        # Venue and every fillable property already stated, so these tests are only about
        # authors.
        wc.item_state = lambda _q: {"Q1": {"strings": strings, "p50": set(p50),
                                           "venue": True, "has": set(wc.FILLS)}}
        papers = [{"slug": "s1", "title": "T", "citations": 5}]
        look = {"orcids": {"s1": orcids or {}}, "by_orcid": by_orcid or {},
                "by_name": by_name or {}, "dblp": dblp or {},
                # Every name candidate plausible, so the occupation prune is not in play.
                "research": [c["qid"] for cs in (by_name or {}).values() for c in cs]}
        return wc.rows(papers, {"s1": "Q1"}, look)

    def test_a_name_match_never_reaches_the_batch(self):
        wc = self._module()
        rows = self._fixture(
            wc, [{"name": "Ada Lovelace", "ordinal": "2"}],
            by_name={"Ada Lovelace": [{"qid": "Q7259", "description": "mathematician",
                                       "orcid": ""}]})
        self.assertEqual(rows[0]["edits"], [])
        self.assertEqual(len(rows[0]["review"]), 1)
        self.assertEqual(wc.batch(rows), [])

    def test_a_dblp_page_listing_this_paper_settles_the_name(self):
        """The one name match that is not a name match: DBLP separates its own namesakes."""
        wc = self._module()
        rows = self._fixture(
            wc, [{"name": "Ada Lovelace", "ordinal": "2", "id": "Q1$a"}],
            by_name={"Ada Lovelace": [{"qid": "Q7259", "description": "", "orcid": ""}]},
            dblp={"Q7259": ["t"]})
        self.assertEqual([e["qid"] for e in rows[0]["edits"]], ["Q7259"])
        self.assertEqual(rows[0]["review"], [])
        self.assertTrue(rows[0]["edits"][0]["via"].startswith("DBLP"),
                        "the page says which record settled it, so the two are told apart")

    def test_a_dblp_page_without_this_paper_settles_nothing(self):
        wc = self._module()
        rows = self._fixture(
            wc, [{"name": "Ada Lovelace", "ordinal": "2", "id": "Q1$a"}],
            by_name={"Ada Lovelace": [{"qid": "Q7259", "description": "", "orcid": ""}]},
            dblp={"Q7259": ["some other paper"]})
        self.assertEqual(rows[0]["edits"], [])
        self.assertEqual(len(rows[0]["review"]), 1)

    def test_two_pages_listing_this_paper_stay_a_question(self):
        """One person under two DBLP ids is a merge, and merging is not this pass's call."""
        wc = self._module()
        rows = self._fixture(
            wc, [{"name": "Ada Lovelace", "ordinal": "2", "id": "Q1$a"}],
            by_name={"Ada Lovelace": [{"qid": "Q7259", "description": "", "orcid": ""},
                                      {"qid": "Q7260", "description": "", "orcid": ""}]},
            dblp={"Q7259": ["t"], "Q7260": ["t"]})
        self.assertEqual(rows[0]["edits"], [])
        self.assertEqual(len(rows[0]["review"]), 1)

    def test_a_paper_with_no_title_confirms_nothing(self):
        """An empty title reduces to an empty key, which would match every author page."""
        wc = self._module()
        wc.item_state = lambda _q: {"Q1": {
            "strings": [{"name": "Ada Lovelace", "ordinal": "2", "id": "Q1$a"}],
            "p50": set(), "venue": True, "has": set(wc.FILLS)}}
        rows = wc.rows([{"slug": "s1", "title": "", "citations": 5}], {"s1": "Q1"},
                       {"orcids": {}, "by_orcid": {},
                        "by_name": {"Ada Lovelace": [{"qid": "Q7259", "description": "",
                                                      "orcid": ""}]},
                        "research": ["Q7259"], "dblp": {"Q7259": [""]}})
        self.assertEqual(rows[0]["edits"], [])

    def test_a_dblp_page_the_server_says_is_gone_is_not_asked_for_again(self):
        """DBLP answers 410 for an author page it has disabled, and that is an answer.

        Cached as "lists nothing", the page leaves the queue. Treated as a failed fetch it
        stays in it, costing one paced request every run for a page that will never load.
        """
        wc = self._module()
        with tempfile.TemporaryDirectory() as d:
            wc.BUILD = d
            asked = []

            def fetch(url, **_kw):
                asked.append(url)
                return (410, b"") if "Gone" in url else (200, b"<title>A Paper</title>")

            wc.get_status = fetch
            wc.dblp_ids = lambda qids: {"Q1": "g/Gone", "Q2": "h/Here"}
            look = {"by_name": {"Ada Lovelace": [{"qid": "Q1"}, {"qid": "Q2"}]}}
            first = wc.dblp_pages(look, False)
            self.assertEqual(len(asked), 2)
            self.assertEqual(first, {"Q2": ["a paper"]}, "an empty page is no evidence")
            with open(os.path.join(d, wc.DBLP_CACHE)) as f:
                self.assertEqual(json.load(f)["titles"]["g/Gone"], [])
            self.assertEqual(wc.dblp_pages(look, False), first)
            self.assertEqual(len(asked), 2, "re-asked for a page the server said was gone")

    def test_a_dblp_page_that_did_not_answer_is_asked_for_again(self):
        wc = self._module()
        with tempfile.TemporaryDirectory() as d:
            wc.BUILD = d
            asked = []

            def fetch(url, **_kw):
                asked.append(url)
                return 0, b""

            wc.get_status = fetch
            wc.dblp_ids = lambda qids: {"Q1": "t/Timeout"}
            look = {"by_name": {"Ada Lovelace": [{"qid": "Q1"}]}}
            self.assertEqual(wc.dblp_pages(look, False), {})
            self.assertEqual(wc.dblp_pages(look, False), {})
            self.assertEqual(len(asked), 2, "gave up on a page that never answered")

    def test_an_orcid_match_survives_a_middle_initial_on_the_byline(self):
        wc = self._module()
        rows = self._fixture(
            wc, [{"name": "Colin A. Raffel", "ordinal": "4"}],
            orcids={"colin raffel": "0000-0002-0000-0001",
                    "c raffel": "0000-0002-0000-0001"},
            by_orcid={"0000-0002-0000-0001": {"qid": "Q9", "label": "Colin Raffel"}})
        self.assertEqual([e["qid"] for e in rows[0]["edits"]], ["Q9"])
        lines = wc.batch(rows)
        self.assertEqual(lines[0].split("\t")[:3], ["Q1", "P50", "Q9"])
        # The printed byline is kept as `object named as`, so the swap loses nothing.
        self.assertIn("Colin A. Raffel", lines[0])
        self.assertEqual(lines[1], '-Q1\tP2093\t"Colin A. Raffel"')

    def test_an_author_already_stated_is_not_proposed_again(self):
        wc = self._module()
        rows = self._fixture(
            wc, [{"name": "Tal Linzen", "ordinal": "3"}], p50=("Q90253205",),
            orcids={"tal linzen": "0000-0003-0435-6912", "t linzen": "0000-0003-0435-6912"},
            by_orcid={"0000-0003-0435-6912": {"qid": "Q90253205", "label": "Tal Linzen"}})
        self.assertEqual(rows, [])

    def test_a_string_matching_nothing_still_gets_its_paper_listed(self):
        wc = self._module()
        rows = self._fixture(wc, [{"name": "Nobody At All", "ordinal": "5"}])
        self.assertEqual(rows[0]["leftover"], 1)
        self.assertEqual((rows[0]["edits"], rows[0]["review"]), ([], []))

    @contextlib.contextmanager
    def _answering(self, wc, status, body):
        old = wc.get_status
        wc.get_status = lambda _u, **kw: (status, json.dumps(body).encode())
        try:
            yield
        finally:
            wc.get_status = old

    def test_two_orcids_under_one_key_in_one_paper_are_dropped(self):
        wc = self._module()
        with self._answering(wc, 200, {"authorships": [
                {"author": {"display_name": "Jian Li",
                            "orcid": "https://orcid.org/0000-0002-0000-0002"}},
                {"author": {"display_name": "Jian Li",
                            "orcid": "https://orcid.org/0000-0002-0000-0003"}}]}):
            self.assertEqual(wc.openalex_orcids([{"slug": "s1", "doi": "10.1/x"}]), ({}, []))

    def test_the_ambiguous_key_is_only_used_inside_one_paper(self):
        wc = self._module()
        with self._answering(wc, 200, {"authorships": [{"author": {
                "display_name": "Ada Lovelace",
                "orcid": "https://orcid.org/0000-0002-0000-0004"}}]}):
            got, refused = wc.openalex_orcids([{"slug": "s1", "doi": "10.1/x"},
                                               {"slug": "s2", "arxiv": "2401.00001"}])
        self.assertEqual(sorted(got), ["s1", "s2"])
        self.assertEqual(sorted(got["s1"]), ["a lovelace", "ada lovelace"])
        self.assertEqual([], refused)

    def test_the_cache_never_regresses_on_a_day_openalex_is_down(self):
        """The map is cached for CACHE_DAYS, so an empty answer written once is an empty
        co-author pass for a month. A refused paper keeps what the cache had, and the clock
        does not advance, so the next run asks again rather than trusting today's silence."""
        wc = self._module()
        stubs = {"openalex_orcids": lambda _p: ({}, ["s1"]),
                 "items_by_orcid": lambda _o: {}, "items_by_name": lambda _n: {},
                 "venue_items": lambda _v: {}, "researchers": lambda _q: [],
                 "proceedings_of": lambda _q: {}, "publications": lambda _c: [],
                 "dblp_pages": lambda _c, _r: {}}
        was = {k: getattr(wc, k) for k in stubs}
        with tempfile.TemporaryDirectory() as d:
            build = wc.BUILD
            try:
                wc.BUILD = d
                for k, v in stubs.items():
                    setattr(wc, k, v)
                with open(os.path.join(d, wc.CACHE), "w") as f:
                    json.dump({"shape": wc.SHAPE, "asked": "2026-08-01", "names": [],
                               "orcids": {"s1": {"ada lovelace": "0000-0002-0000-0004"}}}, f)
                got = wc.lookups([], [{"slug": "s1", "doi": "10.1/x"}], refresh=True)
                with open(os.path.join(d, wc.CACHE)) as f:
                    kept = json.load(f)
            finally:
                wc.BUILD = build
                for k, v in was.items():
                    setattr(wc, k, v)
        self.assertEqual({"ada lovelace": "0000-0002-0000-0004"}, got["orcids"]["s1"])
        self.assertEqual("2026-08-01", kept["asked"])

    def test_a_metered_refusal_does_not_empty_the_map_it_seeds_everything_from(self):
        """This map names every ORCID the rest of the pass works on, and OpenAlex refuses
        all day once its budget is spent. A refused paper is named rather than counted as
        having no authors, so the caller can keep what it already had."""
        wc = self._module()
        with self._answering(wc, 429, {"error": "Rate limit exceeded"}):
            self.assertEqual(({}, ["s1", "s2"]), wc.openalex_orcids(
                [{"slug": "s1", "doi": "10.1/x"}, {"slug": "s2", "arxiv": "2401.00001"}]))


class TestVenueResolutionTargetsAPublication(unittest.TestCase):
    """P1433 takes a publication, and its value-type constraint says so.

    A conference name matches the conference event as readily as the proceedings volume,
    and the batch is pasted unread, so an event must never become a target. Two candidates
    of equal rank stay a question rather than resolving to whichever row came back first.
    """

    def _module(self):
        import wikidata_coauthors as wc
        importlib.reload(wc)
        self.addCleanup(importlib.reload, wc)
        return wc

    def test_a_conference_event_is_not_a_candidate_at_all(self):
        wc = self._module()
        event = [{"qid": "Q9", "label": "EMNLP 2024", "types": ["Q2020153"]}]
        self.assertEqual(wc.publications(event), [])
        self.assertIsNone(wc.pick_venue(wc.publications(event)))

    def test_a_proceedings_beside_its_own_conference_resolves(self):
        wc = self._module()
        cands = [{"qid": "Q8", "label": "ACL 2019", "types": ["Q2020153"]},
                 {"qid": "Q9", "label": "Proceedings of ACL 2019", "types": ["Q1143604"]}]
        self.assertEqual(wc.pick_venue(wc.publications(cands))["qid"], "Q9")

    def test_two_proceedings_volumes_stay_a_question(self):
        wc = self._module()
        cands = [{"qid": "Q8", "label": "Volume 1", "types": ["Q1143604"]},
                 {"qid": "Q9", "label": "Demonstrations", "types": ["Q1143604"]}]
        self.assertIsNone(wc.pick_venue(cands))

    def test_a_proceedings_outranks_a_journal_of_the_same_name(self):
        wc = self._module()
        cands = [{"qid": "Q8", "label": "X", "types": ["Q5633421"]},
                 {"qid": "Q9", "label": "X", "types": ["Q1143604", "Q3331189"]}]
        self.assertEqual(wc.pick_venue(cands)["qid"], "Q9")

    def test_a_journal_under_a_subtype_still_counts_as_one(self):
        wc = self._module()
        cands = [{"qid": "Q9", "label": "TACL", "types": ["Q5633421", "Q773668"]}]
        self.assertEqual(wc.pick_venue(wc.publications(cands))["qid"], "Q9")


class TestFullTextUrlSkipsIdentifierMirrors(unittest.TestCase):
    """P953 is worth a statement only when it adds a copy the item does not already imply.

    A doi.org link restates P356 and an arxiv.org link restates P818, so both are dropped.
    Everything kept is normalised to https, since the corpus carries a few http URLs from
    proceedings sites that have served https for years.
    """

    def _module(self):
        import wikidata_coauthors as wc
        importlib.reload(wc)
        self.addCleanup(importlib.reload, wc)
        return wc

    def test_a_doi_or_arxiv_link_earns_nothing(self):
        wc = self._module()
        for url in ("https://doi.org/10.18653/v1/2020.emnlp-main.638",
                    "https://arxiv.org/abs/2401.00001", "http://www.arxiv.org/abs/1"):
            self.assertEqual(wc.full_text({"url": url}), "", url)

    def test_a_publisher_copy_is_kept(self):
        wc = self._module()
        self.assertEqual(wc.full_text({"url": "https://aclanthology.org/2023.conll-babylm.1"}),
                         "https://aclanthology.org/2023.conll-babylm.1")

    def test_http_becomes_https(self):
        wc = self._module()
        self.assertEqual(wc.full_text({"url": "http://papers.nips.cc/paper/1"}),
                         "https://papers.nips.cc/paper/1")

    def test_a_missing_url_is_not_a_statement(self):
        wc = self._module()
        for p in ({}, {"url": ""}, {"url": "   "}, {"url": "not a url"}):
            self.assertEqual(wc.full_text(p), "", p)


class TestVenueGuardsRejectAPlausibleWrongVolume(unittest.TestCase):
    """The batch is pasted unread, so a venue may only resolve on evidence.

    Two ways a well-matching name is still the wrong answer. A conference publishes several
    volumes and an alias of one of them is often the conference's plain name, so a short
    paper matching on that name would be filed among the long papers. And Wikidata carries
    bad aliases — the CoNLL 2020 proceedings answers to `CoNLL 2024` — which the volume's
    own publication year catches.
    """

    def _module(self):
        import wikidata_coauthors as wc
        importlib.reload(wc)
        self.addCleanup(importlib.reload, wc)
        return wc

    def test_a_volume_the_name_does_not_name_is_refused(self):
        wc = self._module()
        plain = "Proceedings of the 56th Annual Meeting of the ACL"
        vol1 = "Proceedings of the 56th Annual Meeting of the ACL (Volume 1: Long Papers)"
        self.assertEqual(wc.volume_named(plain), set())
        self.assertFalse(wc.volume_named(vol1) <= wc.volume_named(plain))
        self.assertTrue(wc.volume_named(vol1) <= wc.volume_named(vol1))

    def test_a_volume_from_the_wrong_year_is_refused(self):
        wc = self._module()
        self.assertFalse(wc.right_year({"year": 2020}, 2024))
        self.assertTrue(wc.right_year({"year": 2024}, 2024))
        self.assertTrue(wc.right_year({"year": 2023}, 2024), "December editions slip a year")

    def test_an_undated_journal_is_waved_through(self):
        wc = self._module()
        self.assertTrue(wc.right_year({"year": 0}, 2024))
        self.assertTrue(wc.right_year({}, 2024))
        self.assertTrue(wc.right_year({"year": 2020}, None))

    def test_venue_forms_are_tried_canonical_first_and_never_arxiv(self):
        wc = self._module()
        got = wc.venue_forms({
            "venue_display": "Findings of EMNLP 2023",
            "venue": "Findings of the {ACL}: {EMNLP} 2023, Singapore, December 6-10, 2023"})
        self.assertEqual(got[0], "Findings of EMNLP 2023")
        self.assertIn("Findings of the ACL: EMNLP 2023", got)
        self.assertEqual(wc.venue_forms({"venue_display": "arXiv", "venue": "arXiv.org"}), [])

    def test_findings_is_read_off_the_anthology_identifier(self):
        wc = self._module()
        self.assertTrue(wc.is_findings({"doi": "10.18653/v1/2023.findings-emnlp.95"}))
        self.assertFalse(wc.is_findings({"doi": "10.18653/v1/2023.emnlp-main.90"}))

    def test_an_unlabelled_stub_is_not_a_target(self):
        wc = self._module()
        stub = [{"qid": "Q135923323", "label": "", "types": ["Q1143604"]}]
        self.assertEqual(wc.publications(stub), [])


class TestTheAuthorSwapIsOneEdit(unittest.TestCase):
    """The `P50` and the removal of the `P2093` it replaces must land together.

    Either alone leaves the paper crediting the same person twice or crediting nobody, so
    the two go in one atomic payload and the paste form states the same thing.
    """

    _ROW = {"qid": "Q1", "slug": "a-paper", "venue": {"qid": "Q9"},
            "fills": {"P407": "Q1860", "P953": '"https://x.example/p.pdf"'},
            "edits": [{"qid": "Q7", "name": "A B", "ordinal": "3", "id": "Q1$abc"}]}

    def _module(self):
        import wikidata_coauthors as wc
        return wc

    def test_the_add_and_the_removal_are_in_one_payload(self):
        wc = self._module()
        claims = wc.payload(self._ROW)["claims"]
        adds = [c for c in claims if "mainsnak" in c]
        self.assertEqual([c["mainsnak"]["property"] for c in adds],
                         ["P1433", "P407", "P953", "P50"])
        self.assertEqual([c for c in claims if "remove" in c],
                         [{"id": "Q1$abc", "remove": ""}])

    def test_the_printed_name_and_the_ordinal_ride_along(self):
        wc = self._module()
        q = [c for c in wc.payload(self._ROW)["claims"]
             if c.get("mainsnak", {}).get("property") == "P50"][0]["qualifiers"]
        self.assertEqual(q["P1932"][0]["datavalue"]["value"], "A B")
        self.assertEqual(q["P1545"][0]["datavalue"]["value"], "3")

    def test_the_api_and_the_paste_state_the_same_thing(self):
        wc = self._module()
        lines = wc.batch([self._ROW])
        props = [li.split("\t")[1] for li in lines]
        self.assertEqual(props, ["P1433", "P407", "P953", "P50", "P2093"])
        self.assertTrue(lines[-1].startswith("-Q1\t"), "the paste removes the string too")
        self.assertEqual(len(wc.payload(self._ROW)["claims"]), len(lines))

    def test_a_paper_that_already_states_its_venue_is_not_asked_about(self):
        """The regression that turned 33 resolved venues into 32 questions."""
        wc = self._module()
        wc.item_state = lambda _q: {"Q1": {"strings": [], "venue": True,
                                           "has": {"P407", "P953"}, "p50": set()}}
        look = {"venues": {}, "proceedings": {}, "orcids": {}, "by_orcid": {},
                "by_name": {}, "research": []}
        rows = wc.rows([{"slug": "a", "title": "A", "venue_display": "Some Proceedings"}],
                       {"a": "Q1"}, look)
        self.assertEqual(rows, [], "nothing is open on it, so it is off the page")

    def test_a_row_with_nothing_to_write_is_no_edit(self):
        wc = self._module()
        self.assertEqual(wc.payload({"qid": "Q1", "slug": "a", "fills": {}, "edits": []}), {})


class TestGroupItemsAreCreatedOnceAndOnlyOnEvidence(unittest.TestCase):
    """The batch creates public items under the author's name, so three things must hold.

    A group Wikidata already has must never be created twice, an edge must never be
    restated, and a QID whose label does not match the note beside it must stop the run
    rather than ship. Every statement also has to name the page it came from, because that
    is what Wikidata notability asks for.
    """

    def _module(self):
        import wikidata_orgs as wo
        importlib.reload(wo)
        self.addCleanup(importlib.reload, wo)
        return wo

    _ITEM = {"label": "EvalEval Coalition", "description": "research coalition",
             "aliases": ["EvalEval"],
             "statements": [{"p": "P31", "v": "Q20747412", "note": "research consortium",
                             "ref": "https://evalevalai.com/"}],
             "organizer_of": [{"qid": "Q131426993", "note": "the 2024 workshop"}],
             "subject_of": ["a-paper"]}

    def test_an_existing_group_is_connected_rather_than_created(self):
        wo = self._module()
        wo.found = lambda _i: {"g": ["Q999"]}
        wo.edges_present = lambda _p: set()
        st = wo.state_of({"g": self._ITEM}, {"a-paper": "Q1"})
        self.assertEqual(st["g"]["qid"], "Q999")
        lines = wo.batch({"g": self._ITEM}, st, "2026-08-28")
        self.assertNotIn("CREATE", lines)
        self.assertIn("Q131426993\tP664\tQ999", lines)
        self.assertIn("Q1\tP921\tQ999", lines)

    def test_an_absent_group_is_created_and_its_edges_wait(self):
        wo = self._module()
        wo.found = lambda _i: {"g": []}
        wo.edges_present = lambda _p: set()
        st = wo.state_of({"g": self._ITEM}, {"a-paper": "Q1"})
        lines = wo.batch({"g": self._ITEM}, st, "2026-08-28")
        self.assertEqual(lines[0], "CREATE")
        self.assertEqual(st["g"]["missing"], [])
        self.assertTrue(any(li.startswith("LAST\tP31\tQ20747412") for li in lines))
        self.assertFalse(any("P664" in li for li in lines), "no edge before the QID exists")

    def test_an_edge_already_stated_is_not_restated(self):
        wo = self._module()
        wo.found = lambda _i: {"g": ["Q999"]}
        wo.edges_present = lambda _p: {("Q131426993", "P664", "Q999")}
        st = wo.state_of({"g": self._ITEM}, {"a-paper": "Q1"})
        self.assertEqual(st["g"]["missing"], [("Q1", "P921", "Q999")])

    def test_an_edge_this_repo_just_added_is_not_added_again(self):
        wo = self._module()
        wo.found = lambda _i: {"g": ["Q999"]}
        # The query service has not caught up, so it reports the edge as absent.
        wo.edges_present = lambda _p: set()
        st = wo.state_of({"g": self._ITEM}, {"a-paper": "Q1"},
                         {"edges": ["Q131426993 P664 Q999"]})
        self.assertEqual(st["g"]["missing"], [("Q1", "P921", "Q999")])

    def test_two_items_carrying_the_name_stay_a_question(self):
        wo = self._module()
        wo.found = lambda _i: {"g": ["Q998", "Q999"]}
        wo.edges_present = lambda _p: set()
        st = wo.state_of({"g": self._ITEM}, {})
        self.assertEqual(st["g"]["qid"], "")
        self.assertEqual(st["g"]["ambiguous"], ["Q998", "Q999"])
        self.assertEqual(wo.batch({"g": self._ITEM}, st, "2026-08-28")[0], "CREATE")

    def test_a_qid_whose_label_contradicts_its_note_is_caught(self):
        wo = self._module()
        self.assertEqual(wo.mistyped({"g": self._ITEM},
                                     {"Q20747412": "research consortium"}), [])
        bad = wo.mistyped({"g": self._ITEM}, {"Q20747412": "institutions of the EU"})
        self.assertEqual(len(bad), 1)
        self.assertIn("Q20747412", bad[0])
        self.assertEqual(len(wo.mistyped({"g": self._ITEM}, {})), 1,
                         "a QID with no label at all is not a pass")

    def test_every_shipped_statement_cites_a_page(self):
        wo = self._module()
        items = wo.described(os.path.join(ROOT, "data", "wikidata_orgs.yaml"))
        self.assertTrue(items)
        for slug, it in items.items():
            for s in it["statements"]:
                self.assertTrue(str(s.get("ref", "")).startswith("https://"),
                                f"{slug} {s['p']} has no source")
        lines = wo.batch(items, {s: {"qid": "", "missing": []} for s in items},
                         "2026-08-28")
        for li in lines:
            if li.startswith("LAST\tP"):
                self.assertIn("\tS854\t", li, li)


class TestNamesakesAreLeftOffThePageNotGuessedAt(unittest.TestCase):
    """Occupation prunes the candidate lists a human reads, and nothing else.

    A name match to an actor or a footballer is a coincidence, and the long tail of those is
    what makes a common name unreadable — one string in the corpus matched 132 items. The
    prune may only ever shorten that list: an item stating no occupation is kept, because a
    missing statement is not evidence against, and the ORCID-matched batch is untouched.
    """

    def _module(self):
        import wikidata_coauthors as wc
        importlib.reload(wc)
        self.addCleanup(importlib.reload, wc)
        return wc

    def test_an_item_with_no_occupation_survives(self):
        wc = self._module()
        asked = []

        def fake(q):
            asked.append(q)
            if "P106 []" in q:
                return [{"p": {"value": "http://www.wikidata.org/entity/Q2"}}]
            return [{"p": {"value": "http://www.wikidata.org/entity/Q2"}}]

        wc.sparql = fake
        self.assertEqual(wc.researchers(["Q1", "Q2"]), {"Q1", "Q2"})

    def test_an_item_whose_only_occupation_is_unrelated_is_dropped(self):
        wc = self._module()

        def fake(q):
            if "P106 []" in q:
                return [{"p": {"value": "http://www.wikidata.org/entity/Q%d" % i}}
                        for i in (1, 2)]
            return [{"p": {"value": "http://www.wikidata.org/entity/Q1"}}]

        wc.sparql = fake
        self.assertEqual(wc.researchers(["Q1", "Q2"]), {"Q1"})

    def test_the_roots_are_asked_of_wikidatas_own_subclass_tree(self):
        wc = self._module()
        seen = []
        wc.sparql = lambda q: seen.append(q) or []
        wc.researchers(["Q1"])
        tree = [q for q in seen if "P279*" in q]
        self.assertEqual(len(tree), 1)
        for root in wc.RESEARCH_ROOTS:
            self.assertIn("wd:" + root, tree[0])

    def test_a_pruned_name_becomes_a_disambiguator_pass_not_a_lost_string(self):
        wc = self._module()
        wc.item_state = lambda _q: {"Q1": {"strings": [{"name": "A Namesake", "ordinal": "1"}],
                                           "p50": set(), "venue": True,
                                           "has": set(wc.FILLS)}}
        look = {"orcids": {"s1": {}}, "by_orcid": {},
                "by_name": {"A Namesake": [{"qid": "Q8", "description": "footballer",
                                            "orcid": ""}]},
                "research": []}
        rows = wc.rows([{"slug": "s1", "title": "T", "citations": 5}], {"s1": "Q1"}, look)
        self.assertEqual(rows[0]["review"], [])
        self.assertEqual(rows[0]["leftover"], 1, "the string is still open, just unlisted")
        self.assertEqual(rows[0]["dropped"], 1)

    def test_the_prune_never_reaches_the_batch(self):
        wc = self._module()
        rows = [{"qid": "Q1", "fills": {}, "venue": None, "review": [], "dropped": 9,
                 "edits": [{"qid": "Q7", "ordinal": "1", "name": "A Namesake"}]}]
        self.assertEqual(wc.batch(rows), [
            "Q1\tP50\tQ7\tP1545\t\"1\"\tP1932\t\"A Namesake\"",
            "-Q1\tP2093\t\"A Namesake\""])


class TestPeopleItemsRestOnPublicRecordsNotOnNames(unittest.TestCase):
    """Creating a person is the most public thing this repo generates, so the batch may
    only carry people two public records describe, and only once each."""

    def _job(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import wikidata_people as wp
        return wp

    def _rec(self, **kw):
        base = {"label": "Ada Lovelace", "openalex_label": "", "employers": [],
                "works": 3, "openalex_works": 0}
        return dict(base, **kw)

    def test_a_private_work_list_is_not_an_empty_one(self):
        wp = self._job()
        rec = self._rec(works=0, openalex_works=613)
        got = wp.described("0000-0001-5522-1351", rec, {})
        self.assertNotIn("skip", got)
        # The occupation has to point at the record that actually shows the publishing.
        self.assertIn("openalex.org", got["works"])

    def test_nobody_neither_record_names_reaches_the_batch(self):
        wp = self._job()
        got = wp.described("0000-0000-0000-0000",
                           self._rec(label="", openalex_label=""), {})
        self.assertIn("skip", got)
        self.assertEqual(wp.batch([], "2026-08-28"), [])

    def test_a_person_with_no_works_anywhere_is_left_out(self):
        wp = self._job()
        got = wp.described("0000-0000-0000-0001",
                           self._rec(works=0, openalex_works=0), {})
        self.assertIn("skip", got)

    def test_an_unmatched_employer_is_described_but_not_stated(self):
        """`employer` has to point at an item, so an organisation Wikidata has never heard
        of cannot be stated. The description is free text and still says where they are,
        which is what separates two researchers of the same name."""
        wp = self._job()
        rec = self._rec(employers=["Some Lab Nobody Has An Item For"])
        got = wp.described("0000-0001-0000-0002", rec, {})
        self.assertEqual(got["employers"], [])
        self.assertEqual(got["description"], "researcher at Some Lab Nobody Has An Item For")
        self.assertNotIn("P108", "\n".join(wp.batch([got], "2026-08-28")))

    def test_an_employer_openalex_is_unsure_about_is_not_used_at_all(self):
        """OpenAlex lists every institution its disambiguation has seen. More than one
        means it is unsure, and picking from the list put a finance institute in India on
        a Hugging Face researcher."""
        wp = self._job()
        rec = self._rec(employers=[], openalex_employers=["Hugging Face", "Inria"])
        got = wp.described("0000-0001-6500-6030", rec,
                           {"Hugging Face": {"qid": "Q108943604", "label": "Hugging Face"}})
        self.assertEqual(got["employers"], [])
        self.assertEqual(got["description"], "researcher")

    def test_the_employer_reads_the_way_wikidata_names_it(self):
        wp = self._job()
        rec = self._rec(employers=["The Hebrew University of Jerusalem"])
        emp = {"The Hebrew University of Jerusalem":
               {"qid": "Q174158", "label": "Hebrew University of Jerusalem"}}
        got = wp.described("0000-0003-4311-3876", rec, emp)
        self.assertEqual(got["description"], "researcher at Hebrew University of Jerusalem")
        self.assertIn("LAST\tP108\tQ174158", "\n".join(wp.batch([got], "2026-08-28")))

    def test_somebody_who_got_an_item_since_the_last_pass_is_not_created_twice(self):
        wp = self._job()
        cache = {"by_orcid": {"0000-0000-0000-0003": {"qid": "Q9"}},
                 "orcids": {"s1": {"a b": "0000-0000-0000-0003",
                                   "c d": "0000-0000-0000-0004"}}}
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, wp.CACHE), "w") as f:
                json.dump(cache, f)
            with mock.patch.object(wp, "BUILD", d):
                self.assertEqual(wp.wanted(), {"0000-0000-0000-0004": 1})

    def test_every_statement_in_the_batch_carries_a_source(self):
        wp = self._job()
        got = wp.described("0000-0001-0000-0005", self._rec(), {})
        lines = wp.batch([got], "2026-08-28")
        self.assertTrue(lines and lines[0] == "CREATE")
        for line in lines:
            if line.startswith("LAST\tP"):
                self.assertIn("\tS854\t", line, line)
                self.assertIn("\tS813\t", line, line)

    def _held(self, **kw):
        """One held person with one same-name item, as `main` assembles them."""
        n = {"qid": "Q7", "orcid": "", "description": "researcher", "works": [],
             "research": True, "occupations": {}, "education": {}, "employers": {}}
        n.update(kw.pop("item", {}))
        return dict({"orcid": "0000-0001-0000-0009", "label": "Ada Lovelace",
                     "description": "researcher at Somewhere", "employers": [],
                     "namesakes": [n]}, **kw)

    def test_a_paper_they_share_says_which_item_they_are(self):
        """The one signal that needs no judgement: the item is stated as an author of a paper
        this ORCID is on, so it is them."""
        wp = self._job()
        p = self._held(item={"works": ["Fusing Finetuned Models for Better Pretraining"]})
        got = wp.verdict(p, {wp.title_key("Fusing finetuned models for better pretraining")})
        self.assertEqual("Q7", got["qid"])
        self.assertIn("Fusing Finetuned Models", got["why"])

    def test_an_employer_both_records_name_says_the_same(self):
        wp = self._job()
        p = self._held(employers=[("IBM Research", "Q3146518", "https://orcid.org/x")],
                       item={"employers": {"Q3146518": "IBM Research"}})
        got = wp.verdict(p, set())
        self.assertEqual("Q7", got["qid"])
        self.assertIn("IBM Research", got["why"])

    def test_nothing_here_ever_concludes_that_a_namesake_is_one(self):
        """An occupation nothing like research reads as a different person and is not enough
        to act on. Adding an ORCID is undone by removing it, where a second item for somebody
        who has one takes an administrator to merge -- and the tree that classifies an
        occupation has holes, statistician reaching no research root at all."""
        wp = self._job()
        p = self._held(item={"description": "businessman", "research": False,
                            "occupations": {"Q43845": "businessperson"}})
        self.assertEqual({}, wp.verdict(p, {"a shared paper nobody claims"}))

    def test_an_item_that_states_an_orcid_is_never_linked_to(self):
        """It states a different ORCID, ours having matched nothing on the way in. It is held
        because the label and description collide, which is not a reason to edit it."""
        wp = self._job()
        p = self._held(employers=[("IBM Research", "Q3146518", "https://orcid.org/x")],
                       item={"orcid": "0000-0002-0000-0000", "works": ["A Shared Paper"],
                             "employers": {"Q3146518": "IBM Research"}})
        self.assertEqual({}, wp.verdict(p, {wp.title_key("A Shared Paper")}))

    def test_a_value_the_query_service_has_no_label_for_is_left_out(self):
        """A bare QID in a line meant to be read is noise, and the item is linked anyway."""
        wp = self._job()
        line = wp.summary({"description": "statistician", "works": [],
                           "occupations": {"Q2732142": "statistician"},
                           "education": {}, "employers": {"Q138498667": ""}})
        self.assertEqual("statistician", line)
        self.assertEqual("states nothing beyond the name",
                         wp.summary({"description": "", "works": [], "occupations": {},
                                     "education": {}, "employers": {}}))

    def test_every_candidate_row_says_what_that_item_states(self):
        """A row asking which same-name item is them, without saying what any of them says,
        is 22 people to look up. The text is in hand either way -- the same call that finds
        the candidates returns it."""
        import update
        out = "\n".join(update.wikidata_people(
            {"decided": 2,
             "held_people": [{"label": "Jacob Andreas", "orcid": "0000-0002-3141-5845",
                              "papers": 10, "description": "researcher",
                              "namesakes": [{"qid": "Q125454034", "says": "AI researcher"},
                                            {"qid": "Q112760940", "says": "actor"}]}]}))
        self.assertIn("may already have a Wikidata item (1)", out)
        self.assertIn("- [Q125454034](https://www.wikidata.org/wiki/Q125454034) — "
                      "AI researcher", out)
        self.assertIn("— actor", out)
        # The first candidate is the likeliest and not the answer, so the alternatives are
        # in the block a reader pastes rather than only in the rows above it.
        self.assertIn("  0000-0002-3141-5845: Q125454034   # Jacob Andreas — or "
                      "Q112760940, or new", out)
        self.assertIn("2 more needed no answer", out)

    def test_a_state_file_written_before_the_evidence_existed_still_renders(self):
        import update
        out = "\n".join(update.wikidata_people(
            {"held_people": [{"label": "Ada Lovelace", "orcid": "0000-0001-0000-0009",
                              "papers": 1, "namesakes": [{"qid": "Q7"}]}]}))
        self.assertIn("states nothing beyond the name", out)
        self.assertNotIn("needed no answer", out)

    def test_the_real_batch_creates_a_human_researcher_with_the_orcid_on_it(self):
        path = os.path.join(ROOT, "tasks", "wikidata_people.qs")
        if not os.path.exists(path):
            self.skipTest("no batch generated")
        with open(path) as f:
            text = f.read()
        blocks = [b for b in text.split("CREATE\n") if b.strip()]
        self.assertTrue(blocks)
        for b in blocks:
            self.assertIn("LAST\tP31\tQ5\t", b)
            self.assertIn("LAST\tP106\tQ1650915\t", b)
            self.assertRegex(b, r"LAST\tP496\t\"\d{4}-\d{4}-\d{4}-\d{3}[\dX]\"")

    def test_a_namesake_stating_another_orcid_is_somebody_else(self):
        """Ours matched no item on the way in, so an item stating an ORCID states a
        different one and does not stop the creation."""
        wp = self._job()
        p = {"description": "researcher at Somerville"}
        self.assertEqual(wp.keeps(p, [{"qid": "Q1", "orcid": "0000-0001-8071-4828",
                                       "description": "researcher"}]), [])

    def test_a_namesake_stating_no_orcid_stops_the_creation(self):
        """The same person reached from a source that gave no identifier looks exactly
        like this, and a duplicate human item is not ours to undo."""
        wp = self._job()
        got = wp.keeps({"description": "researcher"},
                       [{"qid": "Q2", "orcid": "", "description": "physicist"}])
        self.assertEqual([s["qid"] for s in got], ["Q2"])

    def test_a_name_and_description_wikidata_would_refuse_is_held_first(self):
        """Wikidata rejects a label and description pair that already exists. Two
        same-name researchers with no employer between them are that pair."""
        wp = self._job()
        got = wp.keeps({"description": "researcher"},
                       [{"qid": "Q3", "orcid": "0000-0002-0982-9785",
                         "description": "researcher"}])
        self.assertEqual([s["qid"] for s in got], ["Q3"])

    def _searched(self, wp, answers):
        """`namesakes` run against canned API responses instead of the live wiki."""
        def fake(url, **kw):
            if "wbsearchentities" in url:
                name = urllib.parse.unquote(url.split("search=")[1])
                return 200, json.dumps({"search": [{"id": q, "label": lab}
                                                   for q, lab, _ in answers.get(name, [])]})
            ids = url.split("ids=")[1].split("&")[0].split("|")
            claim = {"Q5": lambda: {"mainsnak": {"datavalue": {
                "value": {"id": "Q5"}}}}}
            out = {}
            for q in ids:
                human = any(q == a[0] and a[2] for v in answers.values() for a in v)
                out[q] = {"claims": {"P31": [claim["Q5"]()]} if human else {}}
            return 200, json.dumps({"entities": out})
        old, wp.get_status = wp.get_status, fake
        try:
            return wp.namesakes(sorted({n for n in answers}))
        finally:
            wp.get_status = old

    def test_a_namesake_is_held_whatever_it_says_the_person_does(self):
        """The occupation on an item is no evidence about who it is. One co-author's item
        says businessman and it is still him, so any same-name human item holds."""
        wp = self._job()
        got = self._searched(wp, {"Prateek Yadav": [("Q102070311", "Prateek Yadav", True)]})
        self.assertEqual([n["qid"] for n in got["Prateek Yadav"]], ["Q102070311"])

    def test_a_same_name_item_that_is_not_a_person_does_not_hold(self):
        """An album or a company sharing a name says nothing about the person."""
        wp = self._job()
        self.assertEqual(
            self._searched(wp, {"Ada Lovelace": [("Q999999", "Ada Lovelace", False)]}), {})

    def test_a_namesake_under_a_different_spelling_still_holds(self):
        """Profiles write one name several ways, and the search index answers for the
        forms a query on the English label cannot see."""
        wp = self._job()
        got = self._searched(wp, {"Mohit Bansal": [("Q67386311", "mohit bansal", True)]})
        self.assertEqual([n["qid"] for n in got["Mohit Bansal"]], ["Q67386311"])

    def test_a_name_typed_in_one_case_is_labelled_in_the_other(self):
        """ORCID stores whatever the person typed. A label is a name, so a record giving
        one case takes OpenAlex's form, and a name already cased as a name is left alone."""
        wp = self._job()
        self.assertEqual(wp.cased(self._rec(label="mohit bansal",
                                            openalex_label="Mohit Bansal")), "Mohit Bansal")
        self.assertEqual(wp.cased(self._rec(label="YANGSIBO HUANG",
                                            openalex_label="Yangsibo Huang")), "Yangsibo Huang")
        self.assertEqual(wp.cased(self._rec(label="Ludwig van Beethoven",
                                            openalex_label="Ludwig Van Beethoven")),
                         "Ludwig van Beethoven")
        self.assertEqual(wp.cased(self._rec(label="Kirtana  Sunil Phatnani")),
                         "Kirtana Sunil Phatnani")

    def test_the_api_payload_and_the_paste_form_state_the_same_thing(self):
        """Two ways out of one batch, so a revoked credential does not change what lands."""
        wp = self._job()
        p = {"orcid": "0000-0002-1825-0097", "label": "Ada Lovelace",
             "description": "researcher at Somerville",
             "works": "https://orcid.org/0000-0002-1825-0097",
             "employers": [("Somerville", "Q123", "https://orcid.org/0000-0002-1825-0097")]}
        d = wp.payload(p, "2026-08-28")
        self.assertEqual(d["labels"]["en"]["value"], "Ada Lovelace")
        self.assertEqual(d["descriptions"]["en"]["value"], "researcher at Somerville")
        got = [(c["mainsnak"]["property"],
                c["mainsnak"]["datavalue"]["value"].get("id")
                if isinstance(c["mainsnak"]["datavalue"]["value"], dict)
                else c["mainsnak"]["datavalue"]["value"]) for c in d["claims"]]
        self.assertEqual(got, [("P31", "Q5"), ("P106", "Q1650915"),
                               ("P496", "0000-0002-1825-0097"), ("P108", "Q123")])
        for c in d["claims"]:
            snaks = c["references"][0]["snaks"]
            self.assertTrue(snaks["P854"][0]["datavalue"]["value"])
            self.assertEqual(snaks["P813"][0]["datavalue"]["value"]["precision"], 11)
        line = "\n".join(wp.batch([p], "2026-08-28"))
        self.assertIn('Len\t"Ada Lovelace"', line)
        self.assertIn("LAST\tP108\tQ123\t", line)

    def test_an_employer_only_openalex_knows_is_sourced_to_openalex(self):
        """ORCID's employment section is often empty and OpenAlex still knows where the
        person last published from. Whichever record said it is the one cited."""
        wp = self._job()
        rec = self._rec(employers=[], openalex_employers=["University of Washington"])
        p = wp.described("0000-0002-5830-9508", rec,
                         {"University of Washington": {"qid": "Q219563",
                                                       "label": "University of Washington"}})
        self.assertEqual(p["description"], "researcher at University of Washington")
        self.assertEqual(p["employers"], [("University of Washington", "Q219563",
                                           "https://openalex.org/authors/"
                                           "https://orcid.org/0000-0002-5830-9508")])
        got = [c for c in wp.payload(p, "2026-08-28")["claims"]
               if c["mainsnak"]["property"] == "P108"]
        self.assertIn("openalex.org",
                      got[0]["references"][0]["snaks"]["P854"][0]["datavalue"]["value"])


class TestAQuietWikidataCreatesNobody(unittest.TestCase):
    """Nothing this repo does is harder to undo than creating a person twice.

    Both reads that decide it -- no item states this ORCID, no item carries this name --
    report an absence, and every way of not answering reports the same absence. A second
    item for somebody who already has one takes an administrator to merge, where every other
    mistake here is a statement somebody can remove.
    """

    def _mods(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import wikidata_coauthors as wc
        import wikidata_people as wp
        return wc, wp

    def test_a_query_that_did_not_answer_is_recorded_beside_its_empty_result(self):
        """`[]` is also what a query answers with when nothing matches."""
        wc, _ = self._mods()
        importlib.reload(wc)
        self.addCleanup(importlib.reload, wc)
        for st in (0, 429, 500):
            wc._quiet = ""
            with mock.patch.object(wc, "get_status", lambda _u, **kw: (st, b"")):
                self.assertEqual([], wc.sparql("SELECT ?x WHERE {}"))
            self.assertTrue(wc.wdqs_quiet(), "status %s passed as an answer" % st)
        wc._quiet = ""
        empty = b'{"results": {"bindings": []}}'
        with mock.patch.object(wc, "get_status", lambda _u, **kw: (200, empty)):
            self.assertEqual([], wc.sparql("SELECT ?x WHERE {}"))
        self.assertEqual("", wc.wdqs_quiet())

    def test_a_search_index_that_did_not_answer_is_not_a_name_nobody_carries(self):
        _, wp = self._mods()
        old = wp._refused
        try:
            for st in (0, 429, 500):
                wp._refused = ""
                with mock.patch.object(wp, "get_status", lambda _u, **kw: (st, b"")):
                    self.assertEqual({}, wp.asked(wp.WIKI + "?search=Ada"))
                self.assertTrue(wp._refused, "status %s passed as an answer" % st)
            wp._refused = ""
            with mock.patch.object(wp, "get_status",
                                   lambda _u, **kw: (200, b'{"search": []}')):
                self.assertEqual({"search": []}, wp.asked(wp.WIKI + "?search=Ada"))
            self.assertEqual("", wp._refused)
        finally:
            wp._refused = old

    def test_no_batch_is_written_from_a_read_that_did_not_answer(self):
        """A quiet read gives `items_by_orcid` and `namesakes` nothing, which is the exact
        state that creates an item. So the run has to end before the batch is written --
        `--apply` reads the same list `main` writes."""
        _, wp = self._mods()
        rec = {"partial": False, "label": "Ada Example Lovelace", "openalex_label": "",
               "employers": [], "openalex_employers": [], "works": 3, "work_titles": [],
               "openalex_works": 0}
        orcid = "0000-0001-5522-1351"
        old = wp._refused
        try:
            for quiet in ("query.wikidata.org -> HTTP 500", ""):
                wp._refused = ""
                d = tempfile.mkdtemp()
                self.addCleanup(shutil.rmtree, d, True)
                with mock.patch.object(wp, "TASKS", d), \
                     mock.patch.object(wp, "BUILD", d), \
                     mock.patch.object(wp, "wanted", lambda: {orcid: 2}), \
                     mock.patch.object(wp, "records", lambda o, r: {orcid: rec}), \
                     mock.patch.object(wp, "items_by_orcid", lambda o: {}), \
                     mock.patch.object(wp, "employer_items", lambda n: {}), \
                     mock.patch.object(wp, "namesakes", lambda n: {}), \
                     mock.patch.object(wp, "about", lambda q: {}), \
                     mock.patch.object(wp, "coauthored", lambda: {}), \
                     mock.patch.object(wp, "wdqs_quiet", lambda: quiet), \
                     mock.patch.object(sys, "argv", ["wikidata_people.py", "--quiet"]):
                    code = wp.main()
                if quiet:
                    self.assertEqual(1, code)
                    self.assertEqual([], os.listdir(d), "a quiet read wrote a batch")
                else:
                    self.assertEqual(0, code)
                    with open(os.path.join(d, "wikidata_people.qs")) as f:
                        self.assertIn("CREATE", f.read())
        finally:
            wp._refused = old

    def test_no_employer_is_retracted_from_a_read_that_did_not_answer(self):
        """`resync` asks again after `main` checked, so the outage can start in between.
        `stale` retracts an employer statement missing from the employers it was given, and
        a query service that went quiet gives it none of them."""
        _, wp = self._mods()
        rec = {"partial": False, "label": "Ada Example Lovelace", "openalex_label": "",
               "employers": ["Weizmann Institute of Science"], "openalex_employers": [],
               "works": 3, "work_titles": [], "openalex_works": 0}
        orcid = "0000-0001-5522-1351"
        led = {"items": {orcid: "Q1"}, "labels": {"Q1": "Ada Example Lovelace"}}
        old = wp._refused
        try:
            wp._refused = ""
            edits = []
            session = mock.Mock()
            session.edit.side_effect = lambda *a, **kw: edits.append(kw)
            with mock.patch.object(wp, "read_yaml", lambda p: led), \
                 mock.patch.object(wp, "records", lambda o, r: {orcid: rec}), \
                 mock.patch.object(wp, "employer_items", lambda n: {}), \
                 mock.patch.object(wp, "asked", lambda u: {"entities": {"Q1": {}}}), \
                 mock.patch.object(wp, "wdqs_quiet",
                                   lambda: "query.wikidata.org -> HTTP 500"):
                self.assertEqual((0, 0), wp.resync(session, "2026-08-29"))
            self.assertEqual([], edits, "a quiet read retracted a statement")
        finally:
            wp._refused = old


class TestACoauthorOrcidIsShownForWhatItSays(unittest.TestCase):
    """Every one of those ORCIDs came from OpenAlex resolving a bare name.

    Crossref carries no author identifiers for the ACL Anthology, arXiv, and MIT Press
    DOIs in this corpus, so nothing confirms the match and on a common name it lands on a
    namesake -- one of them is a pediatric emergency physician. No join settles it: the
    person's own work list overlaps the candidate item's authored works for none of the 22,
    and all 22 records list no employer. So the row prints what the ORCID record itself
    states, where a paper in an unrelated field is visible without opening anything.
    """

    def _job(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import wikidata_people as wp
        return wp

    def test_the_line_names_the_field_the_record_is_in(self):
        wp = self._job()
        self.assertEqual(
            'University of California, San Francisco · "Research Dissemination Strategies '
            'in Pediatric Emergency…"',
            wp.states({"employers": ["University of California, San Francisco"],
                       "work_titles": ["Research Dissemination Strategies in Pediatric "
                                       "Emergency Medicine"]}))

    def test_a_record_with_nothing_on_it_says_so_rather_than_reading_as_blank(self):
        wp = self._job()
        self.assertEqual("4 work(s), no employer and no title", wp.states({"works": 4}))
        self.assertEqual("nothing public beyond the name", wp.states({}))

    def test_the_worklist_row_carries_it_instead_of_a_bare_link(self):
        import update
        out = "\n".join(update.wikidata_people(
            {"held_people": [{"label": "Michelle Lin", "papers": 4,
                              "orcid": "0000-0002-8376-107X", "namesakes": [{"qid": "Q7"}],
                              "record_says": "UCSF · \"Pediatric Emergency Medicine\""}]}))
        self.assertIn("states UCSF · \"Pediatric Emergency Medicine\"", out)
        self.assertIn("`no`", out)

    def test_no_drops_the_orcid_out_of_all_three_fates(self):
        """`new` overrides the hold, a QID links to it, and `no` is neither -- so nothing is
        created, nothing is written, and the name is never asked about again."""
        wp = self._job()
        ok = [{"orcid": "A", "namesakes": [{"qid": "Q1"}]},
              {"orcid": "B", "namesakes": [{"qid": "Q2"}]},
              {"orcid": "C", "namesakes": [{"qid": "Q3"}]},
              {"orcid": "D", "namesakes": []}]
        people, link, held = wp.sorted_out(ok, {"A": "no", "B": "new", "C": "Q3"})
        self.assertEqual(["B", "D"], [p["orcid"] for p in people])
        self.assertEqual([("C", "Q3")], [(p["orcid"], q) for p, q in link])
        self.assertEqual([], held)

    def test_a_typo_stops_the_run_rather_than_reading_as_no(self):
        """`No`, `none`, `q125454034` all mean nothing here. Treated as `no` they would drop
        a co-author silently, and the output cannot be told from a correct one."""
        wp = self._job()
        with self.assertRaises(ValueError) as e:
            wp.sorted_out([{"orcid": "A", "namesakes": [{"qid": "Q1"}]}], {"A": "None"})
        self.assertIn("is not a QID, `new` or `no`", str(e.exception))

    def test_a_refused_fetch_defers_the_verdict_instead_of_leaving_somebody_out(self):
        """"Left out" and "no works on either record" are claims about what the records say.

        Neither is available when one of them did not answer, so both wait for a run where
        both did. A record that does describe a person still does, because ORCID answers for
        the name and the employer and OpenAlex only stands in where ORCID is silent.
        """
        wp = self._job()
        blank = {"label": "", "openalex_label": "", "employers": [], "works": 0,
                 "openalex_works": 0}
        self.assertEqual("neither ORCID nor OpenAlex gives a name",
                         wp.described("A", dict(blank, partial=True), {})["later"])
        self.assertEqual("no works on either record",
                         wp.described("B", dict(blank, label="Ada Lovelace",
                                                partial=True), {})["later"])
        self.assertNotIn("skip", wp.described("B", dict(blank, partial=True), {}))
        got = wp.described("C", dict(blank, label="Ada Lovelace", works=3, partial=True), {})
        self.assertNotIn("later", got)
        self.assertEqual("Ada Lovelace", got["label"])

    def test_the_page_says_they_were_not_asked_rather_than_not_describable(self):
        wp = self._job()
        with tempfile.TemporaryDirectory() as d:
            real = wp.TASKS
            try:
                wp.TASKS = d
                page = wp.write_page([], [], [], [], {}, None,
                                     [{"orcid": "0000-0001-0000-0000",
                                       "later": "no works on either record"}])
                with open(page) as f:
                    text = f.read()
            finally:
                wp.TASKS = real
        self.assertIn("## Not asked yet (1)", text)
        self.assertIn("would be *no works on either record*, on a record that answered", text)
        self.assertNotIn("Left out", text)

    def test_a_refusal_is_used_this_run_and_never_written_to_the_cache(self):
        """OpenAlex is metered and answers 429 for the rest of the day once the budget is
        spent. Read as an empty record that is 22 co-authors dropped, and cached it is 22
        dropped for CACHE_DAYS."""
        wp = self._job()
        with tempfile.TemporaryDirectory() as d:
            real_build, real_record = wp.BUILD, wp.record
            try:
                wp.BUILD = d
                wp.record = lambda o: {"partial": o == "B", "label": o, "works": 0,
                                       "openalex_works": 0}
                got = wp.records(["A", "B"], refresh=True)
                self.assertEqual({"A", "B"}, set(got))
                with open(os.path.join(d, wp.CACHE_PEOPLE)) as f:
                    kept = json.load(f)["records"]
            finally:
                wp.BUILD, wp.record = real_build, real_record
        self.assertEqual(["A"], sorted(kept))
        self.assertNotIn("partial", kept["A"])


class TestAnUnreadRecordIsNotAnEmptyOne(unittest.TestCase):
    """`get`/`get_json` collapse every failure to `b''`/`None`, so a caller reading an
    absence as a statement reports a source's silence as its answer. `common.get_status`
    keeps the distinction, and these are the three places where getting it wrong is
    expensive: a thirty-day cache, a report the author acts on, and a page of people.
    """

    def test_the_audit_tells_a_refusal_from_a_record_with_nothing_on_it(self):
        """A works count of 0 already means either empty or private. Unread is the third
        case and the only one that must not be reported, because half of what the audit
        prints is read from this record."""
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import audit_identity as ai
        read = {"person": {}, "activities-summary": {"works": {"group": []}}}
        old = ai.get_status
        try:
            ai.get_status = lambda _u, **kw: (429, b'{"error": "Rate limit exceeded"}')
            refused = ai.orcid_public("0000-0002-3491-0632")
            ai.get_status = lambda _u, **kw: (0, b"")
            silent = ai.orcid_public("0000-0002-3491-0632")
            ai.get_status = lambda _u, **kw: (200, json.dumps(read).encode())
            empty = ai.orcid_public("0000-0002-3491-0632")
        finally:
            ai.get_status = old
        self.assertEqual((False, 429), (refused["reachable"], refused["status"]))
        self.assertEqual((False, 0), (silent["reachable"], silent["status"]))
        self.assertEqual((True, 0), (empty["reachable"], empty["works"]))

    def test_the_audit_stops_rather_than_reporting_the_corpus_as_absent(self):
        """`orcid_strays` matches corpus papers against that record, so an unread one makes
        every paper a gap. The guard runs before anything is written, so the last run's
        numbers stand."""
        src = source(os.path.join(ROOT, "scripts", "audit_identity.py"))
        after = src.split('orc = orcid_public(ident["orcid"])', 1)[1]
        guard = after[:after.index("return 1") + 8]
        self.assertIn('if not orc["reachable"]:', guard)
        # Nothing may be written between the read and the guard, or the run that could not
        # read the record still leaves its conclusions on disk.
        for writes in ("open(", "write_json", "write_yaml", "_file("):
            self.assertNotIn(writes, guard)

    def test_only_a_404_writes_the_flag_that_puts_a_page_on_the_worklist(self):
        """`hf_indexed: False` lives in the committed `data/papers.yaml` and the worklist
        turns it into "visit this page", so it may only be written when Hugging Face says
        it has no page. On any other non-answer the last run's flag stands."""
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import collect
        cfg = {"ids": {"huggingface": "someone"}}
        old = collect.get_status
        try:
            for st in (0, 429, 500):
                collect.get_status = lambda _u, **kw: (st, b"")
                p = {"slug": "a", "arxiv": "2401.00001"}
                collect.merge_hf([p], cfg)
                self.assertNotIn("hf_indexed", p, "status %s wrote the flag" % st)
            collect.get_status = lambda _u, **kw: (404, b"")
            p = {"slug": "a", "arxiv": "2401.00001"}
            collect.merge_hf([p], cfg)
            self.assertIs(False, p["hf_indexed"])
        finally:
            collect.get_status = old


class TestAPricedCallIsNotRetriedOnAHostThatSaidNo(unittest.TestCase):
    """Once OpenAlex has refused one call for want of credits, every priced call that day
    is refused too, and `metered` is what decides which to stop sending. It has to name
    the free shapes exactly: too narrow wastes a round trip per call, too wide suppresses
    the by-id lookups that keep answering with $0 left.
    """

    def test_every_list_query_is_priced_and_every_by_id_path_is_free(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import common
        for url in ("https://api.openalex.org/works?filter=title.search:merging+models",
                    "https://api.openalex.org/works?per-page=100"
                    "&filter=raw_author_name.search:Choshen",
                    "https://api.openalex.org/works?per-page=1"
                    "&filter=author.orcid:0000-0003-4311-3876"):
            self.assertTrue(common.metered(url), url)
        for url in ("https://api.openalex.org/works/doi:10.18653/v1/2023.acl-long.1",
                    "https://api.openalex.org/authors/orcid:0000-0003-4311-3876",
                    "https://api.openalex.org/works/doi:10.1/a-search-for-meaning"):
            self.assertFalse(common.metered(url), url)

    def test_no_script_asks_for_an_author_by_the_form_openalex_prices(self):
        """`authors/https://orcid.org/<id>` is priced and `authors/orcid:<id>` is free, and
        both answer the same record. The priced one carries no query string, so `metered`
        cannot see it and the call is sent and refused once the day's credits are spent."""
        for path in sorted(glob.glob(os.path.join(ROOT, "scripts", "*.py"))):
            src = source(path)
            for line in src.splitlines():
                if "api.openalex.org/authors/" in line:
                    self.assertIn("authors/orcid:", line,
                                  "%s asks by a priced form" % os.path.basename(path))


class TestTheAuditKeepsThePagesItCouldNotRead(unittest.TestCase):
    """Three of this audit's outputs are the author's payload rather than a summary: the
    Hugging Face index list, the arXiv claim list, and the unowned count the worklist
    counts down. Each was built from a fetch whose failure looked like an answer, so an
    outage turned "the whole corpus" into a to-do list.
    """

    def _ai(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import audit_identity
        return audit_identity

    @contextlib.contextmanager
    def _answering(self, ai, status, body=b""):
        old = ai.get_status
        ai.get_status = lambda _u, **kw: (status, body)
        try:
            yield
        finally:
            ai.get_status = old

    def test_only_a_404_puts_a_paper_on_the_list_of_pages_to_go_and_create(self):
        ai = self._ai()
        papers = [{"arxiv": "2401.00001", "title": "A", "slug": "a"}]
        for st in (0, 429, 500, 503):
            with self._answering(ai, st):
                got = ai.hf_state(papers, "someone", ["Some One"])
            self.assertEqual([], got["missing"], "status %s asked for a visit" % st)
            self.assertEqual(1, len(got["refused"]), "status %s was not named" % st)
        with self._answering(ai, 404):
            got = ai.hf_state(papers, "someone", ["Some One"])
        self.assertEqual(1, len(got["missing"]))
        self.assertEqual([], got["refused"])

    def test_an_unread_wikidata_item_is_not_an_item_with_no_gaps(self):
        """Both readings report an absence -- no item claims this identifier, this item
        states no gaps -- so a refusal reads as an author item in order. The worklist builds
        its two Wikidata sections from the counts, and `None` takes them away."""
        ai = self._ai()
        old = ai._wd_quiet
        try:
            cfg = {"identity": {"orcid": "0000-0002-3491-0632"},
                   "ids": {"semantic_scholar_primary": "1", "google_scholar": "g",
                           "github": "borgr"}}
            for st in (0, 429, 500):
                ai._wd_quiet = ""
                with self._answering(ai, st):
                    self.assertIsNone(ai.wikidata_item(cfg))
                    self.assertEqual({}, ai.wikidata_gaps("Q123", cfg))
                self.assertTrue(ai._wd_quiet, "status %s passed as an answer" % st)
                # The counts this run has are all None; last run's stand instead.
                state = {"wikidata_gaps": None, "wikidata_papers_present": None,
                         "wikidata_papers_absent": None, "wikidata_papers_creatable": None}
                prev = {"wikidata_gaps": 4, "wikidata_papers_present": 12,
                        "wikidata_papers_absent": 105, "wikidata_papers_creatable": 104}
                self.assertTrue(ai.carry_wikidata(state, prev))
                self.assertEqual(prev, state, "status %s blanked the section" % st)

            ai._wd_quiet = ""
            with self._answering(ai, 200, b'{"query": {"search": []}}'):
                self.assertIsNone(ai.wikidata_item(cfg))
            self.assertEqual("", ai._wd_quiet)
            state = {"wikidata_gaps": 0}
            self.assertEqual("", ai.carry_wikidata(state, {"wikidata_gaps": 4}))
            self.assertEqual({"wikidata_gaps": 0}, state, "this run's reading was replaced")
        finally:
            ai._wd_quiet = old

    def test_an_unread_arxiv_feed_is_not_an_unlinked_orcid(self):
        """A 404 is arXiv saying the author page does not exist, which is what the "link
        your account first" page is for. Anything else is arXiv not answering."""
        ai = self._ai()
        with self._answering(ai, 404):
            self.assertEqual(set(), ai.arxiv_registered("0000-0002-3491-0632"))
        for st in (0, 429, 500):
            with self._answering(ai, st):
                self.assertIsNone(ai.arxiv_registered("0000-0002-3491-0632"),
                                  "status %s read as unlinked" % st)

    def test_nothing_is_written_over_the_claim_list_when_arxiv_is_silent(self):
        ai = self._ai()
        cfg = {"identity": {"orcid": "0000-0002-3491-0632"}}
        papers = [{"arxiv": "2401.00001", "title": "A", "citations": 1}]
        with tempfile.TemporaryDirectory() as d:
            old = ai.TASKS
            ai.TASKS = d
            try:
                path, gap = ai.arxiv_ownership_file(cfg, papers, None)
                self.assertEqual((None, None), (path, gap))
                self.assertEqual([], os.listdir(d), "a refusal wrote a page")
                path, gap = ai.arxiv_ownership_file(cfg, papers, set())
                self.assertEqual(0, gap)
                self.assertIn("does not resolve yet", open(path).read())
            finally:
                ai.TASKS = old
