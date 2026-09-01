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
import base64
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
# All three, so the suite runs the same whether it is discovered or the file is run
# directly. `update.py` lives at the root and `fidelity.py` under `measure/`, and without
# these two a direct run errored on 17 tests that only `discover` could import.
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "measure"))

# Every module that is part of the program, by the directory it lives in. `update.py`
# is listed by hand because it is the only top-level one and importing it by filename
# needs the same path insert the file itself does.
SCRIPT_DIRS = ("scripts", "measure")
# Hand-written prose. `WORKLIST.md` is generated and checked too when it exists (see
# test_generated_worklist_links), because a bad path emitted by the worklist writer is
# exactly the sort of thing nobody notices in generated output.
DOCS = ("README.md", "SKILL.md", "RUN.md", "BACKLOG.md", "CLAUDE.md",
        "docs/RULES.md", "docs/SIDECAR.md", "docs/SETUP.md", "docs/EVIDENCE.md")


_LEDGER = {}


def setUpModule():
    """Point the health ledger at a scratch file for the whole suite.

    `common.note_fetch` writes through the module-level `common.HEALTH`, so any test that
    reaches a fetch path with only `urlopen` mocked records its fake failures in the real
    `build/health.json`. That ledger is what `health_report` reads to decide a source is
    dead, and a test's invented 429s are indistinguishable there from a live outage.
    """
    import common
    _LEDGER["dir"] = tempfile.mkdtemp()
    _LEDGER["was"] = common.HEALTH
    common.HEALTH = os.path.join(_LEDGER["dir"], "health.json")


def tearDownModule():
    import common
    common.HEALTH = _LEDGER["was"]
    shutil.rmtree(_LEDGER["dir"], ignore_errors=True)


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


@contextlib.contextmanager
def answering(status, body: bytes = b"", mods=()):
    """Every read answers `status` and `body`, or whatever `status` returns when it is
    callable.

    A reader that goes through `common.replied` reaches the seam in `common`; one that calls
    `get_status` itself reaches the name its own module imported, which is a separate object.
    Patching one of the two leaves the other module's reads live, so `mods` names any module
    whose own copy has to answer too.
    """
    import common
    f = status if callable(status) else (lambda _u, **kw: (status, body))
    with contextlib.ExitStack() as stack:
        for m in (common,) + tuple(mods):
            if hasattr(m, "get_status"):
                stack.enter_context(mock.patch.object(m, "get_status", f))
        yield


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

    def test_a_failed_write_leaves_the_previous_file_readable(self):
        """It writes beside the target and renames.

        A run killed mid-dump left a truncated file, and the next `json.load` throws one
        away wholesale. For `build/openalex_splits.json` that is a day of OpenAlex
        credits, since the search endpoint is metered at 100 queries.
        """
        import common
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "cache.json")
            common.write_json(path, {"kept": 1})
            with self.assertRaises(TypeError):
                common.write_json(path, {"kept": 1, "unserializable": object()})
            with open(path) as fh:
                self.assertEqual({"kept": 1}, json.load(fh),
                                 "the previous file survives a dump that raised")
            self.assertEqual(["cache.json"], sorted(os.listdir(d)),
                             "and no .tmp is left behind")


class TestAConcurrentRunDoesNotCostADayOfOpenAlexCredits(unittest.TestCase):
    """`split_records` re-reads its cache before writing it.

    Two entry points reach it, `scholar_strays.py` and `update.py --step audit`, and each
    loads the whole cache at the top. Whichever wrote second replaced the other's answers
    with the view it had loaded. OpenAlex meters the search endpoint at 100 queries a day,
    so a dropped entry is a day of waiting to win it back.
    """

    TITLE = "A Title Long Enough To Clear The Twenty Five Character Floor"

    def test_an_entry_another_run_cached_meanwhile_survives(self):
        import scholar_strays as S
        with tempfile.TemporaryDirectory() as d:
            cache = os.path.join(d, "openalex_splits.json")

            def lookup(url):
                """Stands in for the fetch, and writes as a second run would while it is
                in flight."""
                with open(cache, "w") as fh:
                    json.dump({"another-run": {"asked": "2999-01-01", "search": "x",
                                               "records": []}}, fh)
                return {"results": [{"id": "https://openalex.org/W1",
                                     "display_name": self.TITLE,
                                     "publication_year": 2020, "cited_by_count": 3}]}

            with mock.patch.object(S, "BUILD", d), \
                 mock.patch.object(S, "lookup", lookup), \
                 mock.patch.object(S, "budget_reset", lambda host: None):
                S.split_records([{"slug": "s1", "title": self.TITLE}], "")
            with open(cache) as fh:
                got = json.load(fh)
        self.assertIn("s1", got, "this run's own answer is written")
        self.assertIn("another-run", got,
                      "and the concurrent run's answer is not overwritten")


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


class TestEverySectionIsWired(unittest.TestCase):
    """No module defines a function, or imports one, that nothing goes on to name.

    Both halves of a dropped page section are invisible in the output: a section nothing
    calls prints nothing, and a section printing nothing is what a finished section looks
    like -- so the page reports the work as done. Emptying an emitter's return breaks no
    other test, which is why this reads the call graph instead.
    """

    MODULES = ["update.py"] + sorted(
        os.path.join(d, os.path.basename(p)) for d in ("scripts", "measure")
        for p in glob.glob(os.path.join(ROOT, d, "*.py")))

    def tree(self, rel):
        return ast.parse(source(os.path.join(ROOT, rel)))

    @staticmethod
    def _own(scope):
        """The nodes of one scope, stopping at every nested function and class."""
        out, todo = [], list(ast.iter_child_nodes(scope))
        while todo:
            n = todo.pop()
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda,
                              ast.ClassDef)):
                continue
            out.append(n)
            todo += list(ast.iter_child_nodes(n))
        return out

    def names(self, rel):
        """Every bare name `rel` reads while nothing nearer than an import defines it.

        A read inside a function that assigns, loops over, or takes that name as an argument
        reaches the local and is not counted. An import is the one binding that does count,
        wherever it sits: `update.py` imports `held` inside the function that calls it.
        """
        tree, used = self.tree(rel), set()
        for scope in [tree] + [n for n in ast.walk(tree) if isinstance(
                n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef))]:
            own = self._own(scope)
            bound = {n.id for n in own
                     if isinstance(n, ast.Name) and not isinstance(n.ctx, ast.Load)}
            bound |= {n.name for n in own if isinstance(n, ast.ExceptHandler) and n.name}
            if not isinstance(scope, (ast.Module, ast.ClassDef)):
                bound |= {a.arg for a in ast.walk(scope.args) if isinstance(a, ast.arg)}
            # `global x` in a function is a statement that the module-level name is the one
            # being written, so a read there does reach the import.
            bound -= {x for n in own if isinstance(n, (ast.Global, ast.Nonlocal))
                      for x in n.names}
            used |= {n.id for n in own if isinstance(n, ast.Name)
                     and isinstance(n.ctx, ast.Load)} - bound
        return used

    def test_no_section_is_orphaned(self):
        reached = set().union(*(self.names(rel) for rel in self.MODULES))
        for rel in self.MODULES:
            defined = {n.name for n in self.tree(rel).body
                       if isinstance(n, ast.FunctionDef)}
            self.assertEqual(set(), defined - reached,
                             f"{rel} defines a function nothing names, which is the shape "
                             "a dropped section call leaves behind")

    def test_no_section_is_imported_and_dropped(self):
        local = {os.path.basename(p)[:-3] for p in self.MODULES}
        for rel in self.MODULES:
            src, used = source(os.path.join(ROOT, rel)).splitlines(), self.names(rel)
            for n in ast.walk(self.tree(rel)):
                if not isinstance(n, ast.ImportFrom) or n.module not in local:
                    continue
                # `# noqa: F401` marks a deliberate re-export, which nothing here names
                # on purpose -- the importers reach it as `<module>.<name>`.
                if "noqa: F401" in src[n.lineno - 1]:
                    continue
                for a in n.names:
                    self.assertIn(a.asname or a.name, used,
                                  f"{rel} imports {a.name} from {n.module} and never "
                                  "names it, which is what a dropped call leaves behind")


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


class TestEveryRunnableScriptIsInTheReference(unittest.TestCase):
    """Every script with a `__main__` block appears in RUN.md's command reference.

    The test above checks the other direction, so a script could be written, wired and
    never mentioned -- which is how `bootstrap_fork.py`, the first thing a fork has to
    run, stayed unreachable from every page a new reader starts at.
    """

    def test_all_listed(self):
        run = source(os.path.join(ROOT, "RUN.md"))
        ref = run[run.index("## 12. Command reference"):]
        missing = []
        for _, path in modules():
            if 'if __name__ == "__main__":' not in source(path):
                continue
            rel = os.path.relpath(path, ROOT)
            if rel not in ref:
                missing.append(rel)
        self.assertEqual(missing, [], "runnable scripts missing from RUN.md §12:\n  "
                                      + "\n  ".join(missing))


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

    def test_nothing_links_into_the_gitignored_build_directory(self):
        """`test_links` only catches this where the file happens to be absent.

        It is present on the machine that ran `update.py` and gone everywhere else, so a
        link there passes locally and fails in CI. The shape is what is wrong, so checking
        the shape fails in both places. Backticks and the command that writes the file.
        """
        path = os.path.join(ROOT, "WORKLIST.md")
        if not os.path.exists(path):
            self.skipTest("WORKLIST.md not generated yet")
        self.assertEqual([], re.findall(r"\]\((build/[^)]*)\)", source(path)))

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


class TestNobodyReDerivesARootPathByHand(unittest.TestCase):
    """`common.py` exports ROOT, DATA, BUILD and TASKS, and every script imports them.

    `sweep_github.phase_apply` reached `build/` as `DATA/../build` instead, which is the
    same directory by a route nothing else in the repo takes -- so a grep for what writes
    under `build/` missed it, and moving either constant would have left it behind.
    """

    def test_no_script_walks_up_out_of_a_root_it_already_has(self):
        offenders = []
        for rel in sorted(glob.glob(os.path.join(ROOT, "scripts", "*.py"))) + \
                [os.path.join(ROOT, "update.py")]:
            for i, ln in enumerate(source(rel).splitlines(), 1):
                if re.search(r'os\.path\.join\([A-Z_]+,\s*"\.\."', ln):
                    offenders.append(f"{os.path.relpath(rel, ROOT)}:{i}")
        self.assertEqual([], offenders,
                         "these re-derive a path `common.py` already exports")


class TestAGateThatRejectedNothingSaysNothing(unittest.TestCase):
    """`build/not_mine.json` was written only on runs that rejected something.

    Nothing removed it afterwards, so a run that rejected nothing left the previous run's
    list standing and both readers took it as this run's decision.
    `scholar_check.attributed_gaps` drops a gap whose title the file names, and
    `orcid_audit.orcid_strays` tags a stray `confirmed` on the strength of it, which
    `WORKLIST.md` reports as "the collector rejected each of these because no form of your
    name appears" -- a sentence about a paper the current gate never saw.
    """

    CFG = {"identity": {"name_variants": ["Leshem Choshen", "L. Choshen"]}}
    MINE = {"title": "A paper of mine", "key": "a",
            "authors": ["Leshem Choshen", "Omri Abend"]}
    THEIRS = {"title": "Somebody else's paper", "key": "b",
              "authors": ["Ada Lovelace", "Alan Turing"]}

    def _gate(self, papers, d):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import collect
        with mock.patch.object(collect, "BUILD", d):
            return collect.authorship_gate(papers, self.CFG, {})

    def _dir(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        return d, os.path.join(d, "not_mine.json")

    def test_a_run_that_rejects_something_writes_the_list(self):
        d, f = self._dir()
        kept, rejected = self._gate([self.MINE, self.THEIRS], d)
        self.assertEqual((1, 1), (len(kept), len(rejected)))
        self.assertEqual(["Somebody else's paper"],
                         [r["title"] for r in json.load(open(f))])

    def test_a_run_that_rejects_nothing_clears_the_last_run_s_list(self):
        """The whole defect. Same directory, two runs, and the second disagrees."""
        d, f = self._dir()
        self._gate([self.MINE, self.THEIRS], d)
        self.assertTrue(os.path.exists(f))
        self._gate([self.MINE], d)
        self.assertFalse(os.path.exists(f),
                         "the gate rejected nothing and the last run's rejects stand")

    def test_a_gate_that_has_never_rejected_leaves_no_file(self):
        d, f = self._dir()
        self.assertEqual(([], []), tuple(map(list, self._gate([], d))))
        self.assertFalse(os.path.exists(f))

    def test_the_file_is_still_what_the_two_readers_read(self):
        """The removal only matters while something takes the file as current state."""
        for rel in ("scripts/scholar_check.py", "scripts/orcid_audit.py"):
            self.assertIn("not_mine.json", source(os.path.join(ROOT, rel)),
                          f"{rel} no longer reads the file, so check what does")


class TestAQuietArxivDropsNobodyQuietly(unittest.TestCase):
    """The authorship gate drops a paper on one arXiv read, and filed the drop as checked.

    `reject_confidence` exists to say which drops a reviewer can skip. "checked: arXiv's
    full author list does not contain your name" was printed whenever the paper had an arXiv
    id, answered or not -- so a refused read produced the one label that says nobody needs to
    read this row. The same read decides `links.html`, which is on the built site.
    """

    def _c(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import collect
        return collect

    CFG = {"identity": {"name_variants": ["Leshem Choshen", "L. Choshen"]}}

    def _gated(self, c, answers):
        """Run the gate over one consortium paper, returning its reject row."""
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        p = {"title": "A shared task report", "key": "k", "arxiv": "2401.00001",
             "authors": ["The BigScience Workshop"]}
        with mock.patch.object(c, "BUILD", d), \
             mock.patch.object(c, "get_status", lambda u, **kw: answers(u)):
            kept, rejected = c.authorship_gate([p], self.CFG, {})
        self.assertEqual(([], 1), (kept, len(rejected)))
        return rejected[0]

    def test_an_unread_author_list_is_not_a_list_without_your_name(self):
        c = self._c()
        for st in (0, 429, 500):
            with mock.patch.object(c, "get_status", lambda _u, **kw: (st, b"")):
                self.assertIsNone(c.arxiv_authors("2401.00001"))
            row = self._gated(c, lambda _u, st=st: (st, b""))
            self.assertTrue(row.get("arxiv_silent"), "status %s read as an answer" % st)
            self.assertTrue(c.reject_confidence(row).startswith("unverified"),
                            "status %s filed as checked: %s"
                            % (st, c.reject_confidence(row)))

    def test_an_author_list_arxiv_did_give_is_still_filed_as_checked(self):
        """The unverified label is for a read that did not happen. A list arXiv served that
        genuinely lacks the name is a fact, and marking it unverified would put every drop
        in front of a reviewer."""
        c = self._c()
        feed = ('<feed xmlns="http://www.w3.org/2005/Atom">'
                '<entry><id>http://arxiv.org/abs/2401.00001v1</id>'
                '<author><name>Ada Example</name></author>'
                '<author><name>Grace Example</name></author></entry></feed>')
        row = self._gated(c, lambda _u: (200, feed.encode()))
        self.assertNotIn("arxiv_silent", row)
        self.assertTrue(c.reject_confidence(row).startswith("checked"),
                        c.reject_confidence(row))

    def test_a_refused_html_probe_is_not_a_paper_without_html(self):
        """`arxiv_html: False` sends `links.html` to ar5iv and counts the paper as missing
        HTML. papers.yaml holds only what a source asserted, and a refused probe asserts
        nothing."""
        c = self._c()
        for st, want in ((0, None), (429, None), (500, None), (404, False), (200, True)):
            p = {"arxiv": "2401.00001", "title": "t"}
            with mock.patch.object(c, "get", lambda *a, **kw: b""), \
                 mock.patch.object(c, "get_status", lambda _u, **kw: (st, b"")), \
                 mock.patch.object(c.time, "sleep", lambda _n: None):
                c.merge_arxiv([p])
            self.assertEqual(want, p.get("arxiv_html"),
                             "status %s wrote %r" % (st, p.get("arxiv_html")))


class TestAQuietGithubIsNotARepoWithNoReadme(unittest.TestCase):
    """`readme` caches what it fetched, and it used to cache an empty result too.

    `with_evidence` says the opposite for the full text -- "nothing is remembered as
    hopeless. Each is retried next run" -- and the README path had no such retry. One refusal
    held every later draft of that paper to the paper's own wording, because the cache file
    is the whole of the freshness check.
    """

    def _ds(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import draft_sidecars
        return draft_sidecars

    def _fetched(self, ds, answers):
        """Run `readme` against a cache dir of its own, returning (text, cached-or-None)."""
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        p = {"slug": "s", "links": {"code": "https://github.com/o/r"}}
        with mock.patch.object(ds, "CACHE", d), \
             mock.patch.object(ds, "get_status", lambda u, **kw: answers(u)):
            text = ds.readme(p)
        path = os.path.join(d, "s.readme.txt")
        if not os.path.exists(path):
            return text, None
        with open(path) as f:
            return text, f.read()

    def test_a_refusal_is_not_cached_as_a_repo_with_no_readme(self):
        ds = self._ds()
        for st in (0, 429, 500):
            text, cached = self._fetched(ds, lambda _u, st=st: (st, b""))
            self.assertEqual("", text)
            self.assertIsNone(cached, "status %s was cached as no README" % st)

    def test_a_404_on_every_name_is_cached_as_a_repo_with_no_readme(self):
        """Eight fetches that all answered are an answer, and re-asking every run would
        spend eight requests per paper on a repo that has none."""
        ds = self._ds()
        text, cached = self._fetched(ds, lambda _u: (404, b""))
        self.assertEqual("", text)
        self.assertEqual("", cached, "a repo GitHub answered about is re-fetched every run")

    def test_a_readme_under_any_of_the_names_is_found(self):
        """Three call sites read a README and each carried its own shorter list of names.
        `ibm/benchbench` has only `README.rst`, which is how its 1,486 bytes of the authors'
        own naming reached no draft."""
        from common import README_NAMES
        ds = self._ds()
        self.assertEqual(README_NAMES, ds.README_NAMES)
        for name in README_NAMES:
            text, cached = self._fetched(
                ds, lambda u, n=name: (200, b"# gloss") if u.endswith("/" + n)
                else (404, b""))
            self.assertEqual("# gloss", text, "%s was never asked for" % name)
            self.assertEqual("# gloss", cached)

    def test_a_readme_found_after_a_refusal_is_still_cached(self):
        """The refusal only matters when nothing was found. A `master`-default repo whose
        `main` fetches were refused still has its README once `master` answers."""
        ds = self._ds()
        text, cached = self._fetched(
            ds, lambda u: (200, b"# gloss") if "/master/README.md" in u else (500, b""))
        self.assertEqual("# gloss", text)
        self.assertEqual("# gloss", cached)


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


class LedgerCase(unittest.TestCase):
    """A `common.HEALTH` ledger in a tempdir, one record at a time. No tests of its own."""

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

    def record(self, url: str, code: int, **kw) -> dict:
        """`get_status` against a host that answers only with `code`. Returns its ledger row."""
        err = urllib.error.HTTPError(url, code, "no", {}, None)

        def raise_it(*a, **k):
            raise err

        with mock.patch.object(self.common.urllib.request, "urlopen", raise_it), \
                mock.patch.object(self.common, "_pace", lambda u: None), \
                mock.patch.object(self.common.time, "sleep", lambda n: None):
            self.common.get_status(url, retries=1, **kw)
        with open(self.common.HEALTH) as f:
            rows = json.load(f)
        self.assertEqual(len(rows), 1, rows)
        return next(iter(rows.values()))


class TestLedgerAdviceMatchesTheEvidence(LedgerCase):
    """The health ledger's advice has to fit what it actually recorded.

    Fits this file's charter -- pure functions over one dict, no network -- and the bug
    is a wiring bug: for four months the ledger told the reader to "check the URL, the
    key, and whether it still exists" about `api.semanticscholar.org/graph/v1/paper/*`,
    whose URL is correct, which plainly still exists, and which was answering 429 to
    every anonymous caller on the internet. Advice that sends someone to inspect a
    working URL is worse than no line at all, because they conclude the ledger is wrong
    about everything.
    """

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


class TestAGoneRecordIsNotABrokenHost(LedgerCase):
    """A 404 or 410 about one record is the host working, and the path does not always show it.

    `source_key` collapses a path segment to `*` on a digit or over 24 characters, and the
    ledger trusted that alone to tell a record from an endpoint. So DBLP's honest 410 for
    `pid/t/JoshuaBTenenbaum.xml` -- no digit, 20 characters -- and GitHub's 404 for a
    `README.md` in a repo carrying `README.rst` both landed as the host failing, and
    `closing()` printed two working sources under "not coming back on their own". Advice
    that sends someone to inspect a working URL is worse than no line at all.
    """

    GONE = "https://dblp.org/pid/t/JoshuaBTenenbaum.xml"

    def test_a_probe_reads_a_gone_record_as_the_host_answering(self):
        row = self.record(self.GONE, 410, probe=True)
        self.assertEqual((row["ok"], row["fail"]), (1, 0))
        self.assertEqual([], self.common.health_report())

    def test_without_the_probe_the_same_answer_is_a_failing_host(self):
        row = self.record(self.GONE, 410)
        self.assertEqual((row["ok"], row["fail"]), (0, 1))

    def test_an_identifier_in_the_path_still_speaks_for_itself(self):
        """`probe` adds a way to say it. It does not replace the one already there."""
        row = self.record("https://api.crossref.org/works/10.1/x", 404)
        self.assertEqual((row["ok"], row["fail"]), (1, 0))

    def test_a_probe_does_not_excuse_a_host_that_broke(self):
        """Only 404 and 410 are answers. Everything else is the fetch not happening."""
        row = self.record(self.GONE, 500, probe=True)
        self.assertEqual((row["ok"], row["fail"]), (0, 1))
        self.assertEqual(row["last_error"], "500")

    def test_the_two_record_reads_declare_themselves(self):
        want = {"scripts/wikidata_coauthors.py": "dblp.org/pid",
                "scripts/draft_sidecars.py": "raw.githubusercontent.com"}
        for rel, host in want.items():
            calls = [n for n in ast.walk(ast.parse(source(os.path.join(ROOT, rel))))
                     if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "get_status"
                     and host in ast.unparse(n)]
            self.assertTrue(calls, f"{rel} no longer reads {host} through get_status")
            for c in calls:
                self.assertIn("probe=True", ast.unparse(c),
                              f"{rel} asks about one record but the ledger will read a "
                              f"404 there as {host} being down")


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
        ss, asked, _d = self._module(
            {"p0": {"asked": today, "search": self._papers(1)[0]["title"], "records": []}},
            [{"results": []}])
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

    def test_a_character_the_filter_reserves_never_reaches_the_query(self):
        """`?`, `,` and `*` come back HTTP 400 from a `.search:` filter, encoded or not, and
        `|` parses as OR -- a different search rather than a failed one. A filter matches
        tokens, so dropping them costs no words."""
        import scholar_strays as ss
        self.assertEqual("Skill Issue Are Skills Language-Invariant in LLMs",
                         ss.searchable("Skill Issue? Are Skills, Language-Invariant in LLMs"))
        papers = [{"slug": "p0", "title_display": "P",
                   "title": "Instructions? Shape, Production of Language* not|Processing here"}]
        ss, asked, _d = self._module({}, [{"results": []}])
        ss.split_records(papers, None)
        self.assertEqual(1, len(asked))
        got = urllib.parse.unquote(asked[0].split("title.search:", 1)[1])
        self.assertEqual("Instructions Shape Production of Language not Processing here", got)

    def test_an_answer_to_a_different_query_is_not_this_papers_answer(self):
        """The cache holds the search string it answered, so a change to `searchable` re-asks
        exactly the papers whose query it changed. Without it a paper stays stamped with the
        answer to a query nobody asks any more, which reads as OpenAlex holding one record."""
        today = datetime.date.today().isoformat()
        title = self._papers(1)[0]["title"]
        for search, want in ((title, 0), ("A different question entirely", 1), (None, 1)):
            entry = {"asked": today, "records": []}
            if search is not None:
                entry["search"] = search
            ss, asked, _d = self._module({"p0": entry}, [None])
            out = ss.split_records(self._papers(1), None)
            self.assertEqual(want, len(asked), "search=%r" % search)
            self.assertEqual(1 - want, out["checked"], "search=%r" % search)

    def test_a_rejected_query_is_not_a_quiet_host_and_no_re_run_fixes_it(self):
        """A 400 is a malformed query, and it comes back on every re-run. Told to re-run, a
        reader retries forever and the section stays empty as though OpenAlex had answered."""
        import scholar_strays as ss
        importlib.reload(ss)
        self.addCleanup(importlib.reload, ss)
        with answering(400, mods=(ss,)):
            self.assertIsNone(ss.lookup("https://api.openalex.org/works?filter=x"))
        self.assertEqual({"api.openalex.org"}, ss._rejected)
        self.assertEqual(set(), ss._silent, "a rejected query was reported as an outage")
        text = self._page(ss, {"rejected": ["api.openalex.org"]})
        self.assertIn("Re-running repeats the rejection", text)
        self.assertNotIn("Re-run `python scripts/scholar_strays.py`", text)
        partial = {"rejected": ["api.openalex.org"],
                   "openalex": {"checked": 3, "total": 5, "budget_reset": None}}
        self.assertIn("rejected the query for the rest", self._page(ss, partial))

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
            with answering(st, mods=(ss,)):
                self.assertIsNone(ss.lookup("https://api.crossref.org/works?rows=1"))
            self.assertEqual({"api.crossref.org"}, ss._silent, "status %s answered" % st)
        ss._silent.clear()
        with answering(200, b'{"message": {"items": []}}', mods=(ss,)):
            self.assertEqual({"message": {"items": []}},
                             ss.lookup("https://api.crossref.org/works"))
        self.assertEqual(set(), ss._silent)

        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        with mock.patch.object(ss, "BUILD", d), mock.patch.object(ss, "TASKS", d), \
             answering(500, mods=(ss,)), \
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
        cached = {"p0": {"asked": today, "search": title, "records": [
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


class TestTheSuiteCannotWriteTheRealLedger(unittest.TestCase):
    """`setUpModule`'s redirect has to still be in force.

    Several tests reach a fetch path with only `urlopen` mocked, so their invented 429s go
    through the real `note_fetch`. Losing the redirect puts those back in
    `build/health.json`, where `health_report` reads them as a source that has stopped
    answering -- and nothing about the suite passing would say so.
    """

    def test_the_ledger_is_outside_the_repo(self):
        import common
        self.assertFalse(os.path.abspath(common.HEALTH).startswith(ROOT + os.sep),
                         "the suite is writing the repo's own health ledger: %s"
                         % common.HEALTH)


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

        import common
        import worklist
        with tempfile.TemporaryDirectory() as d:
            common.write_yaml(os.path.join(d, "overrides.yaml"), overrides)
            # `common.DATA`, since `read_overrides` resolves the name there. Patching
            # `worklist.DATA` leaves the live `data/overrides.yaml` in play and passes
            # anyway, against Leshem's own papers.
            old, common.DATA = common.DATA, d
            try:
                return "\n".join(worklist.upstream_gaps(papers, {}))
            finally:
                common.DATA = old

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
        from wikidata_audit import disambiguating_statements
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
    Both render `wikidata_audit.paper_item`, which is what makes them agree; this
    measures the agreement over the real corpus rather than trusting the arrangement.
    """

    def _items(self):
        from common import DATA, read_yaml, load_config
        from wikidata_audit import paper_item
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
        from wikidata_audit import paper_item
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
        import wikidata_audit as ai
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
        src = source(os.path.join(ai.ROOT, "scripts", "wikidata_audit.py"))
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

    def test_the_ask_is_counted_in_papers_because_one_pass_answers_a_whole_paper(self):
        """976 strings is 107 visits to one form, so the heading counting strings read 9x."""
        import update
        out = "\n".join(update.wikidata_coauthors(
            {"review": 233, "leftover": 743, "papers_left": 107,
             "papers_with_candidates": 77, "dropped": 166}))
        self.assertIn("## Wikidata author strings (107 papers by hand)", out)
        self.assertNotIn("976", out)
        self.assertIn("233 strings on 77 papers", out)
        # The half with no candidate is the larger one and most of it is not work at all.
        # Rolled into one total it reads as 743 unanswered questions.
        self.assertIn("743 have no item under that exact name", out)

    def test_one_statement_needs_and_two_statements_need(self):
        """Every count here trends to 1 as the work gets done, so it reads at 1 or never."""
        import update
        one = "\n".join(update.wikidata_coauthors(
            {"edits": 1, "review": 1, "leftover": 0, "papers_left": 1,
             "papers_with_candidates": 1}))
        self.assertIn("1 more statement needs no decision", one)
        many = "\n".join(update.wikidata_coauthors(
            {"edits": 2, "review": 1, "leftover": 0, "papers_left": 1,
             "papers_with_candidates": 1}))
        self.assertIn("2 more statements need no decision", many)


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


class TestHalfAProfileIsNotTheWholeProfile(unittest.TestCase):
    """`scholar_rows` stopped paging on a refused page and returned the prefix.

    The caller then computed `not_on_scholar` -- corpus papers whose title is not in the
    listing -- against that prefix, and wrote `scholar_answered: True` over it. The
    profile pages at 100 and this corpus is 114, so one lost second page put every paper
    on it under a `WORKLIST.md` heading asking the author to add papers Scholar already
    has. A first-page refusal was caught; a later one was indistinguishable from the end
    of the table.
    """

    def _sc(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import scholar_check
        return scholar_check

    @staticmethod
    def _page(n, first=0):
        row = ('<tr class="gsc_a_tr"><a class="gsc_a_at" '
               'href="?citation_for_view=x:{i}">Paper {i}</a></tr>')
        return "".join(row.format(i=first + i) for i in range(n))

    def _rows(self, pages):
        """`pages[start]` is what the profile answers for that offset, "" for a refusal."""
        sc = self._sc()
        with mock.patch.object(sc, "fetch", lambda uid, start: pages.get(start, "")), \
                mock.patch.object(sc.time, "sleep"):
            return sc.scholar_rows("u")

    def test_a_short_last_page_is_a_whole_read(self):
        rows, whole = self._rows({0: self._page(100), 100: self._page(16, 100)})
        self.assertTrue(whole)
        self.assertEqual(116, len(rows))

    def test_a_page_that_refuses_part_way_is_not_a_whole_read(self):
        """The defect. 100 rows of 116, and nothing said the 16 were unread."""
        rows, whole = self._rows({0: self._page(100)})
        self.assertEqual(100, len(rows))
        self.assertFalse(whole, "a prefix of the profile came back as the whole profile")

    def test_a_refused_page_is_asked_for_again(self):
        """The profile answered once, so one page refusing is worth a retry."""
        sc = self._sc()
        pages = {0: self._page(100), 100: self._page(16, 100)}
        tries = {"n": 0}

        def flaky(uid, start):
            if start and (tries.__setitem__("n", tries["n"] + 1) or tries["n"] < 3):
                return ""
            return pages[start]

        with mock.patch.object(sc, "fetch", flaky), mock.patch.object(sc.time, "sleep"):
            rows, whole = sc.scholar_rows("u")
        self.assertTrue(whole, "one refused page ended the read with two tries unspent")
        self.assertEqual(116, len(rows))

    def test_a_first_page_refusal_reads_nothing(self):
        self.assertEqual(([], False), self._rows({}))

    def test_a_prefix_reaches_the_same_branch_as_a_refusal(self):
        """Structural, because the branch sits behind a live profile fetch in `main`.

        Both buckets the branch skips rest on a title being absent from the listing, so a
        prefix cannot produce either of them honestly.
        """
        tree = ast.parse(source(os.path.join(ROOT, "scripts", "scholar_check.py")))
        main = next(n for n in ast.walk(tree)
                    if isinstance(n, ast.FunctionDef) and n.name == "main")
        tests = [ast.unparse(n.test) for n in ast.walk(main) if isinstance(n, ast.If)]
        self.assertIn("not rows or not whole", tests,
                      "a partly-read profile is treated as a fully-read one")

    def test_a_refusal_says_so_on_the_page(self):
        import update
        out = "\n".join(update.scholar_gaps({"scholar_answered": False,
                                             "scholar_rows": 0}))
        self.assertTrue(out, "the section is absent, which reads as Scholar agreeing")
        self.assertIn("update.py --step audit", out, "no way back to an answer")
        part = "\n".join(update.scholar_gaps({"scholar_answered": False,
                                              "scholar_rows": 100}))
        self.assertIn("100 row(s)", part, "the page does not say how much did arrive")

    def test_an_answered_profile_still_gets_its_section(self):
        """And so does a build file written before the flag existed."""
        import update
        var = [{"slug": "b", "stale": "open", "scholar": "Theirs", "corpus": "Ours"}]
        for sc in ({"title_variants": var},
                   {"title_variants": var, "scholar_answered": True}):
            out = "\n".join(update.scholar_gaps(sc))
            self.assertIn("- [ ] `b`", out)
            self.assertNotIn("did not answer this run", out)


class TestAnUnfetchedArxivTitleIsNotAgreement(unittest.TestCase):
    """`scholar_check.stale_side` decides which of two titles is behind on one build file.

    `collect.py` wrote `build/title_diffs.json` only when it found a disagreement, and
    `arxiv_titles` returned `{}` for a file that is not there -- so a run of the audit step
    alone, on a machine where collect had never run, made every paper carrying an arXiv id
    come back `scholar`, whose printed line is "kept an older title than arXiv and the
    corpus -- nothing to fix". arXiv had not been asked at all.

    `build/` is gitignored, so a fresh clone is exactly that machine.
    """

    def _sc(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import scholar_check
        return scholar_check

    def test_no_evidence_is_its_own_outcome(self):
        sc = self._sc()
        paper = {"slug": "s", "arxiv": "2501.00001", "title": "Ours"}
        self.assertEqual("unknown", sc.stale_side("Theirs", paper, None)[0],
                         "an unfetched arXiv was read as arXiv agreeing with the corpus")
        self.assertEqual("scholar", sc.stale_side("Theirs", paper, {})[0])
        self.assertEqual("bib", sc.stale_side("Theirs", paper, {"s": "Theirs"})[0])
        self.assertEqual("open", sc.stale_side("Theirs", paper, {"s": "A third name"})[0])

    def test_an_absent_build_file_is_not_an_empty_one(self):
        import tempfile
        sc = self._sc()
        with tempfile.TemporaryDirectory() as d:
            old, sc.BUILD = sc.BUILD, d
            try:
                self.assertIsNone(sc.arxiv_titles(), "a missing file read as full agreement")
                with open(os.path.join(d, "title_diffs.json"), "w") as f:
                    f.write("[]")
                self.assertEqual({}, sc.arxiv_titles())
            finally:
                sc.BUILD = old

    def test_collect_writes_the_file_even_with_nothing_to_report(self):
        """Which is what makes absence mean the step has not run.

        Structural, because the write sits at the end of `main()` behind a live fetch of
        every arXiv id in the corpus.
        """
        tree = ast.parse(source(os.path.join(ROOT, "scripts", "collect.py")))
        guarded = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.If):
                continue
            for inner in ast.walk(node):
                if (isinstance(inner, ast.Call) and getattr(inner.func, "id", "") == "write_json"
                        and any(isinstance(a, ast.Constant) and a.value == "title_diffs.json"
                                for a in ast.walk(inner))):
                    guarded.append(node.lineno)
        self.assertEqual([], guarded, "title_diffs.json is written conditionally again")

    def test_the_worklist_does_not_call_it_a_missing_arxiv_record(self):
        """The heading states arXiv has no record, so only `open` may reach it."""
        import update
        var = [{"slug": "a", "stale": "unknown", "scholar": "Theirs", "corpus": "Ours"},
               {"slug": "b", "stale": "open", "scholar": "Theirs", "corpus": "Ours"}]
        out = "\n".join(update.scholar_gaps({"title_variants": var}))
        self.assertIn("no arXiv record to break the tie", out)
        self.assertIn("- [ ] `b`", out)
        self.assertNotIn("- [ ] `a`", out, "arXiv was never asked about this one")
        self.assertIn("title_diffs.json", out, "and it vanished without a word")


class TestAnAbsentStateFileIsNotAnEmptySection(unittest.TestCase):
    """`WORKLIST.md` opens by promising that a section absent from it is done.

    Each section is built from one file in `build/`, and every one of them reads an empty
    file as nothing to report. So a step that did not run, or that crashed mid-write, takes
    its whole section off the page -- and the opening line then calls it done. `build/` is
    gitignored, so `python update.py --step worklist` on a fresh clone is that run.
    """

    def _u(self):
        import update
        update.UNBUILT.clear()
        return update

    def test_a_missing_file_is_recorded(self):
        import tempfile
        u = self._u()
        with tempfile.TemporaryDirectory() as d:
            old, u.ROOT = u.ROOT, d
            try:
                self.assertEqual({}, u.built("scholar_diff.json"))
            finally:
                u.ROOT = old
        self.assertEqual(["`build/scholar_diff.json` (not there)"], u.UNBUILT)
        self.assertIn("scholar_diff.json", u.unbuilt_note()[0])

    def test_a_half_written_file_says_so(self):
        """A crashed write is not a step that never ran, and the remedy differs."""
        import tempfile
        u = self._u()
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "build"))
            with open(os.path.join(d, "build", "wikidata_people.json"), "w") as f:
                f.write('{"people": [{"name": "A')
            old, u.ROOT = u.ROOT, d
            try:
                self.assertEqual({}, u.built("wikidata_people.json"))
            finally:
                u.ROOT = old
        self.assertEqual(["`build/wikidata_people.json` (there and unreadable)"], u.UNBUILT)

    def test_a_clean_run_says_nothing(self):
        self.assertEqual([], self._u().unbuilt_note())

    def test_the_note_names_every_file_and_the_fix(self):
        u = self._u()
        u.UNBUILT += ["`build/a.json` (not there)", "`build/b.json` (not there)"]
        note = u.unbuilt_note()[0]
        u.UNBUILT.clear()
        self.assertTrue(note.startswith("> "), "not a blockquote, so it reads as body text")
        for want in ("2 files", "build/a.json", "build/b.json", "python update.py"):
            self.assertIn(want, note)

    def test_every_build_read_happens_before_the_note(self):
        """`built` is called all the way down `step_worklist`.

        One added below the note would collect a miss nothing goes on to report, which is
        the silence this class exists to remove.
        """
        tree = ast.parse(source(os.path.join(ROOT, "update.py")))
        fn = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "step_worklist")
        def calls(name):
            return [n.lineno for n in ast.walk(fn) if isinstance(n, ast.Call)
                    and (getattr(n.func, "id", "") == name
                         or getattr(n.func, "attr", "") == name)]
        note, reads, clear = calls("unbuilt_note"), calls("built"), calls("clear")
        self.assertEqual(1, len(note), "the note is emitted once or not at all")
        self.assertTrue(reads, "no build/ read left in the worklist step")
        self.assertLess(max(reads), note[0], "a state file is read after the note is built")
        self.assertTrue(clear and min(clear) < min(reads),
                        "UNBUILT is not cleared, so one run reports the last run's misses")


class TestAStepThatCrashedIsNotAStepThatFoundNothing(unittest.TestCase):
    """`run` discarded the exit code at sixteen of its seventeen call sites.

    A step that died left the pipeline going, and `step_worklist` rebuilt the page at the
    end from whatever `build/` holds -- so a section came back reading as current on the
    last run's data and `python update.py` exited 0. `built` cannot see this one: the file
    is there and parses. Four of the step scripts return 1 precisely so a refusal is not
    read as "nothing left", which only counts if the run carries it forward.
    """

    def _u(self):
        import update
        update.FAILED.clear()
        update.UNBUILT.clear()
        return update

    def test_a_step_that_exits_non_zero_is_recorded_with_its_code(self):
        u = self._u()
        code = u.run([sys.executable, "-c", "raise SystemExit(3)"])
        self.assertEqual(3, code, "the caller can still read it")
        self.assertEqual([("-c raise SystemExit(3)", 3)], u.FAILED)
        u.FAILED.clear()

    def test_a_step_that_succeeds_records_nothing(self):
        u = self._u()
        self.assertEqual(0, u.run([sys.executable, "-c", "pass"]))
        self.assertEqual([], u.FAILED)

    def test_a_clean_run_says_nothing(self):
        self.assertEqual([], self._u().failed_note())

    def test_the_note_names_every_step_its_code_and_what_that_means(self):
        u = self._u()
        u.FAILED += [("scripts/collect.py", 2), ("scripts/wikidata_people.py --quiet", 1)]
        note = u.failed_note()[0]
        u.FAILED.clear()
        self.assertTrue(note.startswith("> "), "not a blockquote, so it reads as body text")
        for want in ("2 steps", "scripts/collect.py", "(exit 2)",
                     "scripts/wikidata_people.py --quiet", "(exit 1)", "may be behind"):
            self.assertIn(want, note)

    def test_one_failed_step_reads_as_one(self):
        u = self._u()
        u.FAILED.append(("scripts/collect.py", 2))
        note = u.failed_note()[0]
        u.FAILED.clear()
        self.assertIn("A step of this run did not finish", note)
        self.assertNotIn("1 steps", note)

    def test_nothing_runs_a_step_around_the_recording(self):
        """`subprocess` is reached once, inside `run`.

        A second launch site would be a step whose crash is invisible again, and the
        symptom is a stale section on a page that exited 0, which looks like nothing.
        """
        tree = ast.parse(source(os.path.join(ROOT, "update.py")))
        wrapper = next(n for n in ast.walk(tree)
                       if isinstance(n, ast.FunctionDef) and n.name == "run")
        inside = {id(n) for n in ast.walk(wrapper)}
        stray = [n.lineno for n in ast.walk(tree)
                 if isinstance(n, ast.Attribute) and getattr(n.value, "id", "") == "subprocess"
                 and id(n) not in inside]
        self.assertEqual([], stray, "update.py launches a step outside `run`")

    def test_the_run_exits_non_zero_but_only_after_the_page_is_written(self):
        """A partial run is worth reading. It is just not worth reporting as a clean one."""
        tree = ast.parse(source(os.path.join(ROOT, "update.py")))
        main = next(n for n in ast.walk(tree)
                    if isinstance(n, ast.FunctionDef) and n.name == "main")
        closing = [n.lineno for n in ast.walk(main) if isinstance(n, ast.Call)
                   and getattr(n.func, "id", "") == "closing"]
        guard = [n for n in ast.walk(main) if isinstance(n, ast.If)
                 and ast.unparse(n.test) == "FAILED"]
        self.assertTrue(closing, "main no longer writes the page")
        self.assertTrue(guard, "nothing in main reads FAILED, so a failed run still exits 0")
        raises = [n.lineno for g in guard for n in ast.walk(g)
                  if isinstance(n, ast.Raise) and "SystemExit" in ast.unparse(n)]
        self.assertTrue(raises, "FAILED is read but the run still exits 0")
        self.assertTrue(all(r > max(closing) for r in raises),
                        "main gives up before writing the page it did build")

    def test_the_page_itself_carries_the_note(self):
        """A note nothing splices in is a note only the terminal scrollback holds."""
        tree = ast.parse(source(os.path.join(ROOT, "update.py")))
        fn = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "step_worklist")
        self.assertIn("failed_note()", ast.unparse(fn))

    def test_a_failed_run_still_reports_what_it_could_not_read(self):
        """The two notes stack. Neither is a substitute for the other."""
        u = self._u()
        u.FAILED.append(("scripts/collect.py", 2))
        u.UNBUILT.append("`build/a.json` (not there)")
        note = "\n".join(u.failed_note() + u.unbuilt_note())
        u.FAILED.clear()
        u.UNBUILT.clear()
        self.assertIn("did not finish", note)
        self.assertIn("could not be read", note)


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
        from common import DECLINE_STAMP
        _, out = self._stamp(f"{DECLINE_STAMP}\n> **Declined.** an older wording\n\n# Form\n",
                             off={"tasks/thing.md": "OpenAlex"})
        self.assertEqual(1, out.count(DECLINE_STAMP))
        self.assertNotIn("older wording", out)
        self.assertIn("# Form", out)

    def test_a_named_file_that_was_not_written_is_skipped(self):
        """A section can name a payload a degraded run never got to write."""
        got, out = self._stamp("# Form\n", off={"tasks/absent.md": "OpenAlex"})
        self.assertEqual([], got)
        self.assertEqual("# Form\n", out)

    def test_a_paste_in_payload_is_never_stamped(self):
        """A `.qs`, `.bib`, or `.txt` payload is pasted somewhere whole.

        `PAYLOAD` matches all four extensions because the worklist links all four, so a
        declined section naming a QuickStatements batch used to get a markdown blockquote
        prepended to it -- three lines QuickStatements reads as commands. The decision is
        recorded in `declines.yaml` and in the worklist either way.
        """
        import tempfile

        import update
        for name in ("batch.qs", "import.bib", "dois.txt"):
            with tempfile.TemporaryDirectory() as d:
                os.makedirs(os.path.join(d, "tasks"))
                path = os.path.join(d, "tasks", name)
                with open(path, "w") as f:
                    f.write("Q1\tP31\tQ5\n")
                old, update.ROOT = update.ROOT, d
                try:
                    got = update.stamp_payloads({f"tasks/{name}": "Wikidata"}, {})
                finally:
                    update.ROOT = old
                self.assertEqual([], got, f"stamped tasks/{name}")
                with open(path) as f:
                    self.assertEqual("Q1\tP31\tQ5\n", f.read())

    def test_a_regenerated_payload_keeps_the_banner(self):
        """The generators run before the worklist step, so they meet a banner from last run.

        A plain overwrite drops it, and the file spends the rest of the run asking for work
        that was declined -- which is what `tasks/openalex_merge.md` did.
        """
        import tempfile

        from common import DECLINE_STAMP, write_task
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "thing.md")
            with open(path, "w") as f:
                f.write(f"{DECLINE_STAMP}\n> **Declined.** `OpenAlex`\n\n# Old body\n")
            write_task(path, ["# New body", "", "Route 1."])
            with open(path) as f:
                out = f.read()
        self.assertTrue(out.startswith(DECLINE_STAMP), "the banner was overwritten")
        self.assertIn("`OpenAlex`", out)
        self.assertIn("# New body", out)
        self.assertNotIn("# Old body", out)

    def test_every_markdown_payload_is_written_through_write_task(self):
        """So the next generator added does not silently drop the banner.

        Per file rather than per call: a module that writes two payloads and routes one of
        them past `write_task` gets through here, which is what the two tests above cover for
        the mechanism itself.
        """
        offenders = []
        for path in sorted(glob.glob(os.path.join(ROOT, "scripts", "*.py"))):
            src = source(path)
            if not re.search(r'os\.path\.join\(TASKS, "[\w.]+\.md"\)|TASKS, name\)', src) \
                    and 'OUT = os.path.join(TASKS' not in src:
                continue
            if "write_task" not in src:
                offenders.append(os.path.relpath(path, ROOT))
        self.assertEqual([], offenders, "writes a tasks/*.md without keeping its banner")

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
        from orcid_audit import orcid_strays
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

    def test_a_heading_that_counts_its_subsections_is_recounted(self):
        """"Identity surfaces (4 open)" over three surfaces is a header the reader can see
        is wrong, which is what stops them trusting the counts they cannot see.
        """
        lines = self.declined(
            'sections: ["OpenAlex"]\n',
            ["## Identity surfaces (4 open)", "",
             "### ORCID", "", "- [ ] one thing", "",
             "### OpenAlex", "", "- [ ] a split", "",
             "### arXiv", "", "- [ ] another thing", "",
             "### Wikidata", "", "- [ ] a third", "",
             "## Repos (2 open)", "", "### Labels", "", "- [ ] label a/b", ""])
        body = "\n".join(lines).split("---", 1)[0]
        self.assertIn("## Identity surfaces (3 open)", body)
        self.assertNotIn("(4 open)", body)
        # The count below the declined one is its own section's, so it must not move.
        self.assertIn("## Repos (1 open)", body)

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


class TestAGeneratedTaskFileSaysWhatWroteIt(unittest.TestCase):
    """`tasks/*.md` are generated and tracked, and eight of them named no writer.

    `CLAUDE.md` forbids hand-editing them, and a tracked markdown file that says nothing
    about where it came from reads like one that may be edited -- with the edit lost at the
    next run and nothing said. The `.qs`, `.bib` and `.txt` payloads stay exempt: each is
    pasted somewhere whole, so a line of prose on top of one would go with it.
    """

    def _v(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import validate
        return validate

    def test_every_task_file_in_the_repo_names_its_writer(self):
        self.assertEqual([], self._v().check_task_provenance())

    def test_the_check_runs_in_the_strict_gate(self):
        """A check nothing calls is a check that passes."""
        tree = ast.parse(source(os.path.join(ROOT, "scripts", "validate.py")))
        main = next(n for n in ast.walk(tree)
                    if isinstance(n, ast.FunctionDef) and n.name == "main")
        self.assertIn("check_task_provenance()", ast.unparse(main))

    def test_a_file_that_names_nothing_is_caught(self):
        v = self._v()
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "tasks"))
            with open(os.path.join(d, "tasks", "t.md"), "w") as f:
                f.write("# A task\n\nOpen the form and paste each row.\n")
            with mock.patch.object(v, "ROOT", d):
                errs = v.check_task_provenance()
        self.assertEqual(1, len(errs), errs)
        self.assertIn("tasks/t.md", errs[0])

    def test_a_payload_pasted_whole_is_exempt(self):
        """A `Generated by` line on one of these would be pasted into ORCID with it."""
        v = self._v()
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "tasks"))
            for name in ("p.qs", "p.bib", "p.txt"):
                with open(os.path.join(d, "tasks", name), "w") as f:
                    f.write("Q1\tP31\tQ5\n")
            with mock.patch.object(v, "ROOT", d):
                self.assertEqual([], v.check_task_provenance())

    def test_a_command_the_banner_names_does_not_count(self):
        """The banner is written by the worklist step, not by whatever generates the file.

        A decline reason that happens to name a command would otherwise satisfy the check
        on behalf of a file that still says nothing about where it came from.
        """
        v = self._v()
        banner = ("<!-- declines -->\n> **Declined.** Re-run `python scripts/w.py` to see.\n"
                  "> Delete that line to have it asked again.\n\n")
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "tasks"))
            os.makedirs(os.path.join(d, "scripts"))
            open(os.path.join(d, "scripts", "w.py"), "w").close()
            t = os.path.join(d, "tasks", "t.md")
            with open(t, "w") as f:
                f.write(banner + "# A task\n\nOpen the form and paste each row.\n")
            with mock.patch.object(v, "ROOT", d):
                errs = v.check_task_provenance()
                self.assertEqual(1, len(errs), errs)
                # And the same file, with the line where it belongs, is clean under a banner.
                with open(t, "w") as f:
                    f.write(banner + "# A task\n\nGenerated by `python scripts/w.py`.\n")
                self.assertEqual([], v.check_task_provenance())

    def test_a_writer_that_is_not_in_the_repo_is_caught(self):
        """A renamed script leaves the line pointing at a command that cannot be run."""
        v = self._v()
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "tasks"))
            with open(os.path.join(d, "tasks", "t.md"), "w") as f:
                f.write("# A task\n\nGenerated by `python scripts/gone.py`.\n")
            with mock.patch.object(v, "ROOT", d):
                errs = v.check_task_provenance()
        self.assertEqual(1, len(errs), errs)
        self.assertIn("not in the repo", errs[0])

    def test_no_task_writer_bypasses_write_task(self):
        """`write_task` keeps the declines banner a worklist run put on the payload.

        `sweep_github.zenodo_candidates` wrote `tasks/zenodo.md` with a plain `open(...)`,
        so every `propose` run stripped the banner marking that work deferred and the file
        went back to asking for it until the next full run put the banner back.
        """
        bad = []
        for rel in sorted(glob.glob(os.path.join(ROOT, "scripts", "*.py"))) + \
                [os.path.join(ROOT, "update.py")]:
            tree = ast.parse(source(rel))
            for fn in ast.walk(tree):
                if not isinstance(fn, ast.FunctionDef):
                    continue
                # Names this function set to a `tasks/*.md` path, so the `.qs`, `.bib` and
                # `.txt` payloads written plainly right beside them are left alone.
                md = {t.id for a in ast.walk(fn) if isinstance(a, ast.Assign)
                      for t in a.targets if isinstance(t, ast.Name)
                      and re.search(r"\btasks\b|\bTASKS\b", ast.unparse(a.value))
                      and re.search(r"""\.md['"]\)?$""", ast.unparse(a.value))}
                for c in ast.walk(fn):
                    if (isinstance(c, ast.Call) and getattr(c.func, "id", "") == "open"
                            and len(c.args) > 1 and getattr(c.args[0], "id", "") in md
                            and getattr(c.args[1], "value", "") == "w"):
                        bad.append(f"{os.path.basename(rel)}:{c.lineno} {fn.name}")
        self.assertEqual([], bad, "these write a tasks/*.md payload without write_task")


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

    def test_a_file_it_cannot_read_is_not_silently_replaced(self):
        """The from-scratch job is still the right one, and the run now says why."""
        import draft_sidecars
        import sidecar_io
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "drafts"))
            with open(os.path.join(d, "p.md"), "w") as f:
                f.write("---\nclaims: [1,\n  qa: {\n---\n")
            err = io.StringIO()
            with mock.patch.object(sidecar_io, "SIDECARS", d), \
                 mock.patch.object(sidecar_io, "DRAFTS", os.path.join(d, "drafts")), \
                 contextlib.redirect_stderr(err):
                self.assertEqual((None, []), draft_sidecars.standing("p"))
        self.assertIn("unparseable front matter", err.getvalue())
        self.assertIn("p.md", err.getvalue())

    def test_a_paper_with_nothing_on_disk_is_drafted_from_scratch(self):
        import draft_sidecars
        import sidecar_io
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(sidecar_io, "SIDECARS", d), \
                 mock.patch.object(sidecar_io, "DRAFTS", d):
                self.assertEqual((None, []), draft_sidecars.standing("absent"))


class TestBrokenFrontMatterIsNotAMissingFile(unittest.TestCase):
    """`front_matter` returned `None` for a file with no `---` block and for broken YAML.

    The remedies differ. The first is a paper nothing has drafted; the second is a sidecar
    somebody hand-edited, and the callers that read `None` as the first went on to redraft
    it from scratch, skip it, or rank it as clean. `read_front_matter` keeps them apart and
    those callers now say which one they met.
    """

    def _io(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import sidecar_io
        return sidecar_io

    def _write(self, d, body):
        path = os.path.join(d, "s.md")
        with open(path, "w") as f:
            f.write(body)
        return path

    def test_the_three_outcomes(self):
        io_ = self._io()
        with tempfile.TemporaryDirectory() as d:
            got = io_.read_front_matter(self._write(d, "---\none_liner: x\n---\nbody\n"))
            self.assertEqual(({"one_liner": "x"}, ""), got)

            fm, why = io_.read_front_matter(self._write(d, "no front matter here\n"))
            self.assertIsNone(fm)
            self.assertEqual("no YAML front matter", why)

            fm, why = io_.read_front_matter(self._write(d, "---\na: [1,\n b: {\n---\n"))
            self.assertIsNone(fm)
            self.assertIn("unparseable front matter", why)
            self.assertNotEqual("no YAML front matter", why,
                                "a hand-edited file reads as one nothing has drafted")

    def test_the_collapsing_wrapper_still_collapses(self):
        """Six callers use it, and for four of them `None` is the right single answer."""
        io_ = self._io()
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual({"one_liner": "x"},
                             io_.front_matter(self._write(d, "---\none_liner: x\n---\n")))
            self.assertIsNone(io_.front_matter(self._write(d, "nothing\n")))
            self.assertIsNone(io_.front_matter(self._write(d, "---\na: [1,\n---\n")))

    def test_the_draft_check_names_which_one_it_met(self):
        """One parse feeds both, so the two messages cannot drift apart."""
        io_ = self._io()
        with tempfile.TemporaryDirectory() as d:
            errs, qual = io_.validate_draft(self._write(d, "nothing\n"), note=False)
            self.assertEqual([], qual)
            self.assertIn("no YAML front matter", errs[0])
            errs, _ = io_.validate_draft(self._write(d, "---\na: [1,\n---\n"), note=False)
            self.assertIn("unparseable front matter", errs[0])

    def test_an_unreadable_draft_is_not_ranked_clean(self):
        """`suspicion` reads fields, so an empty read scores 0 -- its nothing-wrong rank."""
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import sidecar_review
        with tempfile.TemporaryDirectory() as d:
            score, why = sidecar_review.suspicion(self._write(d, "---\na: [1,\n---\n"))
        self.assertGreater(score, 0, "an unreadable draft ranked as one with nothing wrong")
        self.assertIn("unparseable front matter", why[0])

    def test_a_missing_parser_is_not_a_clean_corpus(self):
        """`validate.read_sidecars` returned `([], [])` when PyYAML was absent.

        Every sidecar check runs over what it returns, so `--strict` passed with none of
        them run. PyYAML is in `requirements.txt` and `common` imports it at module scope,
        so the handler could not fire -- and if it ever could, silence is the wrong answer.
        """
        tree = ast.parse(source(os.path.join(ROOT, "scripts", "validate.py")))
        fn = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "read_sidecars")
        for node in ast.walk(fn):
            if isinstance(node, ast.ExceptHandler):
                self.assertNotIn("ImportError", ast.unparse(node.type or ast.Constant("")),
                                 "a missing parser reports every sidecar as fine again")


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
                               return_value={"repos": [entry]}), \
             mock.patch.object(sweep_github, "read_papers", return_value=[paper]), \
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
        # By module, not by function name: the review page is built by one renderer per
        # block and which of them holds the claim list is an internal arrangement. What
        # must not happen is a call from anything that writes into `build/site/`.
        callers = set()
        for path in glob.glob(os.path.join(ROOT, "scripts", "*.py")):
            with open(path, encoding="utf-8") as fh:
                tree = ast.parse(fh.read())
            if any(isinstance(n, ast.Call) and getattr(n.func, "id", "") == "at_sentence"
                   for n in ast.walk(tree)):
                callers.add(os.path.basename(path))
        self.assertEqual({"sidecar_review.py"}, callers)



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


class TestOneObjectIsPickedOutOfWhateverTheModelSaid(unittest.TestCase):
    """`llm.first_json` is the only reader of an unconstrained reply, so it is the only
    thing standing between a fenced or prefaced object and a lost paper's worth of claims.
    """

    def setUp(self):
        import llm
        self.f = llm.first_json

    def test_the_object_is_found_through_whatever_surrounds_it(self):
        for text in ('{"a": 1}', '```json\n{"a": 1}\n```', 'Let me think. {"a": 1}',
                     '{"a": 1}\n\nThat is my answer.', '  \n{"a": 1}  '):
            self.assertEqual({"a": 1}, self.f(text), text)

    def test_a_brace_inside_claim_text_does_not_end_the_object(self):
        self.assertEqual({"t": 'a set {1, 2}'}, self.f('{"t": "a set {1, 2}"}'))
        self.assertEqual({"t": 'he said "hi{" then left'},
                         self.f('{"t": "he said \\"hi{\\" then left"}'))
        self.assertEqual({"t": "\\"}, self.f('{"t": "\\\\"}'))

    def test_the_first_candidate_that_parses_wins(self):
        # A reasoning trace mentioning {something} before the answer, and an unclosed
        # object the model abandoned -- both are skipped rather than returned as None.
        self.assertEqual({"a": 2}, self.f('maybe {like this} -- no: {"a": 2}'))
        self.assertEqual({"b": 3}, self.f('{"a": 1\nscratch that\n{"b": 3}'))
        self.assertEqual({"a": 1}, self.f('{"a": 1} {"b": 2}'))
        self.assertEqual({}, self.f("{{}"))          # outer never closes, inner does

    def test_nothing_usable_is_none_rather_than_a_crash(self):
        for text in ("", "{", "}", "no json here", '{"a": 1', "I cannot answer."):
            self.assertIsNone(self.f(text), text)


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
                with answering(st):
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
            with answering(200, b'{"result": {}}'):
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
                with answering(st):
                    self.assertEqual({}, w.api(titles="Project Debater"))
                self.assertTrue(w._refused, "status %s passed as an answer" % st)
                # One refusal stands for the run: the rest of the ~100 calls are not sent.
                import common
                with mock.patch.object(common, "get_status",
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
            with answering(200, b'{"query": {"pages": []}}'):
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

    def test_one_item_typed_twice_is_one_candidate(self):
        """A row arrives per type, so a volume that is also a `version, edition or
        translation` comes back twice. Left unmerged it is two candidates of equal rank,
        which is the shape this class treats as a question the author has to answer."""
        wc = self._module()
        # The third row repeats a type: `P31/P279*` reaches one supertype once per P31 value
        # the item carries, so the same pair comes back more than once.
        rows = [{"name": {"value": "TACL"}, "p": {"value": "http://www.wikidata.org/entity/Q9"},
                 "pLabel": {"value": "TACL"}, "t": {"value": t}, "date": {"value": "2013-01-01"}}
                for t in ("http://www.wikidata.org/entity/Q5633421",
                          "http://www.wikidata.org/entity/Q773668",
                          "http://www.wikidata.org/entity/Q5633421")]
        got = wc.typed_items(rows, lambda r: r["name"]["value"])
        self.assertEqual([{"qid": "Q9", "label": "TACL", "year": 2013,
                           "types": ["Q5633421", "Q773668"]}], got["TACL"])
        self.assertEqual("Q9", wc.pick_venue(wc.publications(got["TACL"]))["qid"])


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

        wc.answered = lambda q, endpoint="", retries=6: (fake(q), "")
        self.assertEqual(wc.researchers(["Q1", "Q2"]), {"Q1", "Q2"})

    def test_an_item_whose_only_occupation_is_unrelated_is_dropped(self):
        wc = self._module()

        def fake(q):
            if "P106 []" in q:
                return [{"p": {"value": "http://www.wikidata.org/entity/Q%d" % i}}
                        for i in (1, 2)]
            return [{"p": {"value": "http://www.wikidata.org/entity/Q1"}}]

        wc.answered = lambda q, endpoint="", retries=6: (fake(q), "")
        self.assertEqual(wc.researchers(["Q1", "Q2"]), {"Q1"})

    def test_the_roots_are_asked_of_wikidatas_own_subclass_tree(self):
        wc = self._module()
        seen = []
        wc.answered = lambda q, endpoint="", retries=6: (seen.append(q) or [], "")
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


class TestThePastedAnswerIsNeverAnObviousNamesake(unittest.TestCase):
    """The paste block pre-fills a QID and the author corrects it, so the pre-fill has to be
    the likeliest answer rather than whatever came first. Live, three of the twenty-two names
    had no research candidate at all and were pre-filled with an actor, a writer, and a
    businessman."""

    def _wl(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import worklist
        return worklist

    def _person(self, *namesakes):
        return {"orcid": "0000-0001-0000-0009", "label": "Ada Lovelace", "papers": 3,
                "record_says": "nothing public beyond the name",
                "namesakes": [dict({"qid": q, "says": "says " + q}, research=r)
                              for q, r in namesakes]}

    def test_a_research_candidate_is_pre_filled_and_the_rest_are_offered(self):
        wl = self._wl()
        self.assertEqual("Q1", wl.prefill([{"qid": "Q1", "research": True},
                                           {"qid": "Q2", "research": False}]))
        self.assertEqual("Q1", wl.prefill([{"qid": "Q1", "research": False},
                                           {"qid": "Q2", "research": True}]),
                         "the list is already sorted research-first, so the pre-fill is the "
                         "first entry whenever any candidate qualifies")

    def test_no_research_candidate_pre_fills_new(self):
        wl = self._wl()
        self.assertEqual("new", wl.prefill([{"qid": "Q1", "research": False},
                                            {"qid": "Q2"}]))
        self.assertEqual("new", wl.prefill([{"qid": "Q1"}]))

    def test_the_line_offers_every_candidate_it_did_not_pre_fill(self):
        wl = self._wl()
        out = "\n".join(wl.wikidata_people(
            {"held_people": [self._person(("Q1", True), ("Q2", False), ("Q3", False))]}))
        self.assertIn("  0000-0001-0000-0009: Q1   # Ada Lovelace — or Q2, Q3, or new, or no",
                      out)
        out = "\n".join(wl.wikidata_people(
            {"held_people": [self._person(("Q1", False), ("Q2", False))]}))
        self.assertIn("  0000-0001-0000-0009: new   # Ada Lovelace — or Q1, Q2, or new, or no",
                      out,
                      "a candidate dropped from the pre-fill has to still be offered")

    def test_a_long_list_still_says_there_are_more(self):
        wl = self._wl()
        out = "\n".join(wl.wikidata_people(
            {"held_people": [self._person(*[("Q%d" % i, False) for i in range(1, 7)])]}))
        self.assertIn("  0000-0001-0000-0009: new   # Ada Lovelace — or Q1, Q2, Q3, …, "
                      "or new, or no", out)


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

    def test_openalexs_country_never_reaches_a_wikidata_description(self):
        """OpenAlex writes "IBM (United States)" for the same employer Wikidata calls IBM.
        The parenthetical is its own disambiguation, so an item resolved through it reads
        the way Wikidata reads, and an unresolved name loses it before being written."""
        wp = self._job()
        self.assertEqual("IBM", wp.plain("IBM (United States)"))
        self.assertEqual("", wp.plain("Weizmann Institute of Science"))
        self.assertEqual("", wp.plain("University of North Carolina (UNC) Chapel Hill"))
        rec = self._rec(employers=[], openalex_employers=["IBM (United States)"])
        emp = {"IBM (United States)": {"qid": "Q37156", "label": "IBM"}}
        self.assertEqual("researcher at IBM",
                         wp.described("0000-0001-0000-0007", rec, emp)["description"])
        self.assertEqual("researcher at Gaia Dynamics",
                         wp.described("0000-0001-0000-0008",
                                      self._rec(employers=[],
                                                openalex_employers=["Gaia Dynamics (Israel)"]),
                                      {})["description"])

    def test_the_name_as_written_outranks_the_form_it_was_rewritten_to(self):
        """Both forms are asked because either can be the one Wikidata carries. Pooling the
        answers would drop an employer whose two forms are two organisations, where the name
        the record actually used answered on its own."""
        wp = self._job()
        rows = [{"n": {"value": "Coherent (United States)"},
                 "i": {"value": "http://www.wikidata.org/entity/Q1"}},
                {"n": {"value": "Coherent"},
                 "i": {"value": "http://www.wikidata.org/entity/Q2"}},
                {"n": {"value": "Coherent"},
                 "i": {"value": "http://www.wikidata.org/entity/Q3"}}]
        with mock.patch.object(wp, "batched",
                              lambda items, ask, size=100, endpoint="": rows), \
             mock.patch.object(wp, "labels_of", lambda q: {"Q1": "Coherent Corp."}):
            got = wp.employer_items(["Coherent (United States)"])
        self.assertEqual({"Coherent (United States)":
                          {"qid": "Q1", "label": "Coherent Corp."}}, got)

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

    def _search(self, name, qids):
        """`wbsearchentities` answering with a label-exact hit per QID."""
        return {"search": [{"id": q, "label": name} for q in qids]}

    def _human(self, death=None):
        """An entity claiming to be a human, optionally with a date of death."""
        cl = {"P31": [{"mainsnak": {"datavalue": {"value": {"id": "Q5"}}}}]}
        if death:
            cl["P570"] = [{"mainsnak": {"datavalue": {"value": {"time": death}}}}]
        return {"claims": cl, "descriptions": {}}

    def test_a_death_date_is_read_only_when_it_precedes_the_corpus(self):
        wp = self._job()
        early = {"P570": [{"mainsnak": {"datavalue": {"value":
                                                     {"time": "+1590-01-07T00:00:00Z"}}}}]}
        late = {"P570": [{"mainsnak": {"datavalue": {"value":
                                                    {"time": "+2020-01-07T00:00:00Z"}}}}]}
        bce = {"P570": [{"mainsnak": {"datavalue": {"value":
                                                   {"time": "-0044-03-15T00:00:00Z"}}}}]}
        self.assertEqual(1590, wp.died_before(early, 2018))
        self.assertIsNone(wp.died_before(late, 2018), "a death after the first paper is not "
                                                      "evidence about anything")
        self.assertEqual(44, wp.died_before(bce, 2018))
        self.assertIsNone(wp.died_before({}, 2018))
        self.assertIsNone(wp.died_before({"P570": [{"mainsnak": {}}]}, 2018),
                          "a statement with no value is not a date")

    def test_corpus_start_is_the_earliest_paper(self):
        wp = self._job()
        with mock.patch.object(wp, "read_papers",
                               lambda: [{"year": 2021}, {"year": 2018}, {}, {"year": 2026}]):
            self.assertEqual(2018, wp.corpus_start())
        with mock.patch.object(wp, "read_papers", lambda: []):
            self.assertEqual(0, wp.corpus_start(), "an empty corpus cannot rule anybody out")

    def test_somebody_already_dead_is_not_a_candidate(self):
        """Live: this search offered a theologian who died in 1590 for Jacob Andreas, and
        pre-filled a man who died in 2010 as the answer for Eli Schwartz."""
        wp = self._job()
        ents = {"Q1": self._human(), "Q2": self._human("+1590-01-07T00:00:00Z"),
                "Q3": self._human("+2010-08-31T00:00:00Z"),
                "Q4": self._human("+2021-01-01T00:00:00Z")}
        with mock.patch.object(wp, "asked",
                               lambda url: self._search("Jacob Andreas", list(ents))), \
                mock.patch.object(wp, "entities", lambda qids, props, langs="": ents), \
                mock.patch.object(wp, "labels_of", lambda qids: {}), \
                mock.patch.object(wp, "corpus_start", lambda: 2018):
            got = wp.namesakes(["Jacob Andreas"])
        self.assertEqual(["Q1", "Q4"], [n["qid"] for n in got["Jacob Andreas"]],
                         "a candidate dead before the first paper is still on the page")

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

    def test_where_they_studied_is_the_same_institution_as_where_they_work(self):
        """The item names an alma mater where ORCID names an employer, which for a researcher
        is one place often enough to be the strongest thing either record says. Both put this
        name at this institution, and neither role is the claim being tested."""
        wp = self._job()
        p = self._held(
            employers=[("Hebrew University of Jerusalem", "Q174158", "https://orcid.org/x")],
            item={"education": {"Q174158": "Hebrew University of Jerusalem"}})
        got = wp.verdict(p, set())
        self.assertEqual("Q7", got.get("qid"), got)
        self.assertIn("Hebrew University of Jerusalem", got["why"])

    def test_a_second_same_name_item_leaves_the_institution_unanswered(self):
        """One name, two items, and an institution match on one of them. Which of the two
        the shared institution belongs to is not settled by a name."""
        wp = self._job()
        p = self._held(
            employers=[("Hebrew University of Jerusalem", "Q174158", "https://orcid.org/x")],
            item={"education": {"Q174158": "Hebrew University of Jerusalem"}})
        p["namesakes"].append(dict(p["namesakes"][0], qid="Q8", education={}))
        self.assertEqual({}, wp.verdict(p, set()))

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
                              "namesakes": [{"qid": "Q125454034", "says": "AI researcher",
                                             "research": True},
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
        # Patched on `wikidata_coauthors`, which owns the one `w/api.php` reader both the
        # search and the entity read go through. Patching `wp` leaves both live.
        wc = sys.modules["wikidata_coauthors"]
        with answering(fake, mods=(wc,)):
            return wp.namesakes(sorted({n for n in answers}))

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


class TestAQuietItemIsNotAnItemWithNoStatements(unittest.TestCase):
    """`wikidata_apply` replaces a wrong identifier by removing it and creating the right
    one, two calls rather than an in-place edit. The removal reads which statements the item
    carries, and `[]` means it carries none of them -- so a read that did not answer leaves
    the wrong value in place beside the new one, and the audit then reports the pair as a
    duplicate somebody has to unpick by hand.
    """

    def _wa(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import wikidata_apply
        return wikidata_apply

    def test_the_statements_to_remove_are_not_read_as_none(self):
        wa = self._wa()
        for st in (0, 429, 500):
            with answering(st, mods=(wa,)):
                with self.assertRaises(RuntimeError) as e:
                    wa.claim_guids("Q117220720", "P496")
            self.assertIn("could not read", str(e.exception),
                          "status %s read as no statement" % st)
        body = json.dumps({"entities": {"Q1": {"claims": {"P496": [
            {"id": "Q1$abc", "mainsnak": {"datavalue": {"value": "0000-0001-2345-6789"}}}]}}}})
        with answering(200, body.encode(), mods=(wa,)):
            self.assertEqual([("Q1$abc", "0000-0001-2345-6789")],
                             wa.claim_guids("Q1", "P496"))
        # An item that really carries none of them still answers with none of them.
        empty = json.dumps({"entities": {"Q1": {"claims": {}}}})
        with answering(200, empty.encode(), mods=(wa,)):
            self.assertEqual([], wa.claim_guids("Q1", "P496"))

    def test_an_unread_account_is_not_a_four_day_old_one(self):
        """Both halves of autoconfirmed fail the same way, which is why this prints the
        numbers rather than a verdict -- and every one of them would be blank."""
        wa = self._wa()
        for st in (0, 429, 500):
            with answering(st, mods=(wa,)):
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    code = wa.check_account("Ktilana")
            self.assertEqual(1, code, "status %s reported an account" % st)
            self.assertIn("did not answer", out.getvalue())
            self.assertNotIn("need 50", out.getvalue())


class TestOneReaderForEveryJsonSource(unittest.TestCase):
    """`common.replied` is the one place a JSON read decides whether it got an answer.

    Every source here answers 200 with an empty result for something it does not carry, so
    a caller that cannot tell an empty answer from an unreadable one reports the absence as
    a finding. The reason travels with the data for exactly that reason.
    """

    def test_an_answer_that_stopped_is_not_the_status_that_carried_it(self):
        """A body cut off mid-JSON arrives under HTTP 200. Named by its status, the reason a
        page prints for carrying last run's counts is a status that means the call worked."""
        import common
        with answering(200, b'{"entities": {"Q1"'):
            st, d, why = common.replied("https://example.org/x")
        self.assertEqual((200, None), (st, d))
        self.assertEqual("an answer that stopped after 18 bytes", why)
        with answering(503, b""):
            self.assertEqual((503, None, "HTTP 503"), common.replied("https://example.org/x"))
        # A body that never started arrives under 200 as well, so neither shape may be
        # named by the status a reader would take for success.
        with answering(200, b""):
            self.assertEqual((200, None, "an empty body under HTTP 200"),
                             common.replied("https://example.org/x"))
        with answering(200, b'{"ok": []}'):
            self.assertEqual((200, {"ok": []}, ""), common.replied("https://example.org/x"))

    def test_an_answer_that_stopped_reaches_the_reason_each_page_prints(self):
        """Each caller prefixes its own context onto the reason, so a truncation has to be a
        refusal in all of them. Read as an answer it is an empty result set, which is what
        every one of these pages is built out of."""
        import handover
        import ownership
        import wikipedia_tasks
        cut = b'{"query": {"pages"'
        for mod, latch, call in (
                (wikipedia_tasks, "_refused", lambda m: m.api(titles="Sloth")),
                (handover, "_refused", lambda m: m.dblp_pid("Ada Example Lovelace")),
                (ownership, "_quiet", lambda m: m.fetch_peers(
                    {"collaboration": {"peers": ["https://peer.example/m.json"]}})),
        ):
            old = getattr(mod, latch)
            try:
                setattr(mod, latch, "")
                with answering(200, cut):
                    call(mod)
                self.assertIn("stopped after 18 bytes", getattr(mod, latch),
                              "%s read a cut-off body as an answer" % mod.__name__)
            finally:
                setattr(mod, latch, old)


class TestEveryFetchReachesTheHealthLedger(unittest.TestCase):
    """A direct `urllib.request.urlopen` has to call `note_fetch` about what happened.

    `data/health.yaml` is how a source that quietly stopped answering becomes visible, and
    the symptom of a path that skips it is a whole worklist section absent -- which reads as
    "nothing to report". Three such paths were found and fixed by hand once. This is the
    same finding as a check, so the fourth one fails here instead.

    Anything going through `common.get_status` is covered by that function's own call. The
    exemptions below are the two cases where a fetch genuinely is not a source read, and
    each has to stay justified -- an exemption that is no longer needed fails too.

    Per function, not per branch. A fetcher that records one outcome and not another gets
    past this, so the branch coverage is on the tests for that function.
    """

    EXEMPT = {
        "scripts/paper_code.py:hf_put_links":
            "a POST under the author's token, so there is no source whose health it "
            "measures -- its return string is reported per paper instead",
        "scripts/paper_code.py:PageFacts.get":
            "URLs lifted out of paper full text, where a 404 is the probe succeeding. "
            "One mistyped URL in one paper would otherwise earn a permanent ledger line",
    }

    @staticmethod
    def _calls(node, dotted: str) -> bool:
        for n in ast.walk(node):
            if not isinstance(n, ast.Call):
                continue
            f, parts = n.func, []
            while isinstance(f, ast.Attribute):
                parts.append(f.attr)
                f = f.value
            if isinstance(f, ast.Name):
                parts.append(f.id)
            if ".".join(reversed(parts)) == dotted:
                return True
        return False

    def _fetchers(self):
        """(qualified name, path) for every function that opens a URL itself."""
        out = []
        for path in sorted(glob.glob(os.path.join(ROOT, "scripts", "*.py"))
                           + glob.glob(os.path.join(ROOT, "measure", "*.py"))
                           + [os.path.join(ROOT, "update.py")]):
            rel = os.path.relpath(path, ROOT)
            tree = ast.parse(source(path))
            stack = [(tree, "")]
            while stack:
                node, prefix = stack.pop()
                for child in node.body:
                    if isinstance(child, ast.ClassDef):
                        stack.append((child, prefix + child.name + "."))
                    elif isinstance(child, ast.FunctionDef):
                        stack.append((child, prefix + child.name + "."))
                        if self._calls(child, "urllib.request.urlopen"):
                            out.append((f"{rel}:{prefix}{child.name}", child))
        # An outer function is credited to whichever inner one does the opening.
        inner = {q for q, n in out}
        return [(q, n) for q, n in out
                if not any(o != q and o.startswith(q + ".") for o in inner)]

    def test_every_fetch_records_what_happened(self):
        missing = {q for q, n in self._fetchers() if not self._calls(n, "note_fetch")}
        self.assertEqual(set(self.EXEMPT), missing,
                         "left out of data/health.yaml, or exempt without needing to be")


class TestARefusedSparqlChunkIsNotAMissingItem(unittest.TestCase):
    """`wikidata_audit.wikidata_paper_coverage` asks in chunks of 50 and used to treat one
    refused chunk as fifty papers with no Wikidata item.

    `absent` is what `wikidata_apply.py --papers --apply` turns into item creations and what
    `tasks/wikidata_papers.qs` holds as a paste-in batch, so a chunk that timed out minted a
    duplicate publication item for every paper in it. Merging one needs somebody else, which
    makes this the one write in the repo that cannot be undone from here.
    """

    PAPERS = [{"slug": "has-item", "arxiv": "2501.00001"},
              {"slug": "refused", "arxiv": "2501.00002"},
              {"slug": "really-absent", "arxiv": "2501.00003"}]

    @staticmethod
    def _ai():
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import wikidata_audit
        return wikidata_audit

    @staticmethod
    def _bindings(*pairs):
        return {"results": {"bindings": [
            {"v": {"value": v}, "item": {"value": "http://www.wikidata.org/entity/" + q}}
            for v, q in pairs]}}

    def _cov(self, answers):
        """One chunk per paper, so `answers` maps an arXiv id to its reply or None."""
        ai = self._ai()
        with mock.patch.object(ai, "created_items", lambda: {}), \
             mock.patch.object(ai, "get_json",
                               lambda url, **k: next(v for key, v in answers.items()
                                                     if key in url)):
            return ai.wikidata_paper_coverage(self.PAPERS, chunk=1)

    def test_a_refused_chunk_is_unchecked_rather_than_absent(self):
        cov = self._cov({"2501.00001": self._bindings(("2501.00001", "Q1")),
                         "2501.00002": None,
                         "2501.00003": self._bindings()})
        self.assertEqual(["has-item"], [p["slug"] for p, _q in cov["present"]])
        self.assertEqual(["really-absent"], [p["slug"] for p in cov["absent"]],
                         "a refused chunk would be created as a duplicate item")
        self.assertEqual(["refused"], [p["slug"] for p in cov["unchecked"]])
        self.assertEqual((2, 3), (cov["checked"], cov["total"]))

    def test_a_created_item_counts_even_inside_a_refused_chunk(self):
        """The scholarly endpoint indexes a new item hours late, so the ledger outranks it."""
        ai = self._ai()
        with mock.patch.object(ai, "created_items", lambda: {"refused": "Q9"}), \
             mock.patch.object(ai, "get_json", lambda url, **k: None
                               if "2501.00002" in url else self._bindings()):
            cov = ai.wikidata_paper_coverage(self.PAPERS, chunk=1)
        self.assertEqual([("refused", "Q9")], [(p["slug"], q) for p, q in cov["present"]])
        self.assertEqual([], [p["slug"] for p in cov["unchecked"]])

    def test_nothing_answering_still_returns_nothing(self):
        self.assertEqual({}, self._cov(dict.fromkeys(
            ("2501.00001", "2501.00002", "2501.00003"))))


class TestARefusedHuggingFaceReadIsNotAnAnswer(unittest.TestCase):
    """`paper_code.hf_siblings` and `paper_code.hf_get` both returned emptiness on failure.

    Siblings exist to *defer*: an owner publishing two datasets for one paper means nobody
    can tell from a score which is the project page. A refused index looked like an owner
    with nothing else, so the candidate was accepted and `--apply` POSTed one split of a
    multi-part release as the whole of it.

    `hf_get` is worse, because `hf_put_links` echoes the field it is not changing back out
    of the record it reads -- both fields are nullable and omitting one may clear it. On a
    refused read that echo is None, so a push meant to add a project page deletes the repo
    link that was already there.
    """

    PAGE = "https://huggingface.co/datasets/o/global-piqa"

    def _pc(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import paper_code
        return paper_code

    @staticmethod
    def _answer(payload):
        class R:
            def read(self):
                return json.dumps(payload).encode()

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False
        return lambda *a, **k: R()

    @staticmethod
    def _raise(exc):
        def boom(*a, **k):
            raise exc
        return boom

    def _cases(self):
        """(urlopen stand-in, expected refusal) for an answer, a status, and no reply."""
        return ((self._raise(urllib.error.HTTPError(self.PAGE, 429, "slow down", {}, None)),
                 "HTTP 429"),
                (self._raise(urllib.error.URLError("no such host")), "no reply"))

    def test_hf_siblings_says_when_the_owner_index_would_not_load(self):
        pc = self._pc()
        with mock.patch.object(pc, "note_fetch", lambda *a, **k: None):
            listing = [{"id": "o/global-piqa"}, {"id": "o/global-piqa-parallel"}]
            with mock.patch("urllib.request.urlopen", self._answer(listing)):
                sibs, quiet = pc.hf_siblings(self.PAGE, {"global", "piqa"})
            self.assertEqual((["https://huggingface.co/datasets/o/global-piqa-parallel"], ""),
                             (sibs, quiet))
            for opener, want in self._cases():
                with mock.patch("urllib.request.urlopen", opener):
                    sibs, quiet = pc.hf_siblings(self.PAGE, {"global", "piqa"})
                self.assertEqual(([], want), (sibs, quiet))

    def test_a_refused_owner_index_holds_the_page_for_review(self):
        """The whole point of siblings is deferral, so a refusal must defer too."""
        pc = self._pc()
        paper = {"slug": "s", "title": "Global PIQA", "abstract": "we release it"}

        def run(answer):
            with mock.patch.object(pc, "resolve_fulltext", lambda *a, **k: ("", None)), \
                 mock.patch.object(pc, "candidates", lambda *a, **k: []), \
                 mock.patch.object(pc, "page_candidates",
                                   lambda *a, **k: [{"page": self.PAGE, "score": 9,
                                                     "why": []}]), \
                 mock.patch.object(pc, "confirm_page",
                                   lambda c, *a, **k: c.update(exists=True) or c), \
                 mock.patch.object(pc, "hf_siblings", lambda *a, **k: answer):
                return pc.deduce([paper], None, None, None)["s"]["page_verdict"]

        self.assertEqual("accept", run(([], "")))
        self.assertEqual("review", run((["https://huggingface.co/datasets/o/x"], "")))
        self.assertEqual("review", run(([], "HTTP 429")),
                         "a refused sibling index was read as an unambiguous page")

    def test_hf_get_separates_not_indexed_from_would_not_say(self):
        pc = self._pc()
        with mock.patch.object(pc, "note_fetch", lambda *a, **k: None):
            with mock.patch("urllib.request.urlopen", self._answer({"upvotes": 3})):
                self.assertEqual(({"upvotes": 3}, ""), pc.hf_get("2501.00001"))
            gone = urllib.error.HTTPError(self.PAGE, 404, "nope", {}, None)
            with mock.patch("urllib.request.urlopen", self._raise(gone)):
                # A 404 is HF saying the paper is not indexed, which is an answer.
                self.assertEqual((None, ""), pc.hf_get("2501.00001"))
            for opener, want in self._cases():
                with mock.patch("urllib.request.urlopen", opener):
                    self.assertEqual((None, want), pc.hf_get("2501.00001"))

    def test_push_sends_nothing_for_a_paper_hf_would_not_read_out(self):
        """Because the POST has to echo back the link it is not changing."""
        pc = self._pc()
        results = {"s": {"paper": {"arxiv": "2501.00001", "citations": 1}}}
        eff = {"s": {"verdict": "accept", "repo": "https://github.com/o/n",
                     "page_verdict": "none", "page": None}}
        for got, sent in ((({"githubRepo": None}, ""), 1), ((None, ""), 1),
                          ((None, "HTTP 429"), 0), ((None, "no reply"), 0)):
            calls = []
            with mock.patch.object(pc, "hf_get", lambda *a, **k: got), \
                 mock.patch.object(pc, "hf_put_links",
                                   lambda *a, **k: calls.append(a) or "ok 200"), \
                 mock.patch.object(pc.time, "sleep", lambda _s: None), \
                 contextlib.redirect_stdout(io.StringIO()) as out:
                pc.push(results, eff, "t")
            self.assertEqual(sent, len(calls), "hf_get %r pushed %d" % (got, len(calls)))
            if not sent:
                self.assertIn("would not say what is already linked", out.getvalue())


class TestAQuietGitHubIsNotAReadmeToCreate(unittest.TestCase):
    """`links_block.fetch_readme` returned ("", None) for a repo with no README and for a
    repo GitHub would not talk about.

    `diff` then tells the author a repo they maintain has no README, and `apply --yes` sends
    a create for a file that is already there. GitHub rejects that with a 422, so the cost
    is a wasted write against a public repo and a wrong report -- and the report is the half
    they act on.
    """

    NOT_FOUND = (1, "gh: Not Found (HTTP 404)")
    RATE = (1, "gh: API rate limit exceeded for user ID 1. (HTTP 403)")
    NO_REPLY = (1, "dial tcp: lookup api.github.com: no such host")

    def _lb(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import links_block
        return links_block

    def test_only_a_404_reads_as_a_repo_with_no_readme(self):
        lb = self._lb()
        for answer, quiet in ((self.NOT_FOUND, ""), (self.RATE, "HTTP 403"),
                              (self.NO_REPLY, "HTTP no reply")):
            with mock.patch.object(lb, "gh", lambda *a, **k: answer):
                text, sha, got = lb.fetch_readme("o/n")
            self.assertEqual(("", None), (text, sha))
            self.assertEqual(quiet, got, "%r read as %r" % (answer[1][:40], got))

    def test_a_readme_that_answers_carries_its_sha(self):
        lb = self._lb()
        out = base64.b64encode(b"# hi").decode() + "|abc123"
        with mock.patch.object(lb, "gh", lambda *a, **k: (0, out)):
            self.assertEqual(("# hi", "abc123", ""), lb.fetch_readme("o/n"))


class TestAQuietGitHubIsNotAMissingRepo(unittest.TestCase):
    """`paper_code.RepoFacts` cached "no such repo" for every failed `gh` call.

    `gh_json` returns None for a 404, a rate limit, an expired token and a dropped
    connection alike, and the fact went into `build/github_repos.json` whatever the reason.
    The cache is consulted before GitHub is, so one refused minute dropped a paper's code
    link permanently and `confirm` reported it to the reader as "GitHub 404".
    """

    NOT_FOUND = (1, "gh: Not Found (HTTP 404)")
    RATE = (1, "gh: API rate limit exceeded for user ID 1. (HTTP 403)")
    NO_REPLY = (1, "dial tcp: lookup api.github.com: no such host")
    REPO = (0, json.dumps({"full_name": "o/n", "description": "d", "private": False}))

    def _pc(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import paper_code
        return paper_code

    def _facts(self, pc, answer):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        with mock.patch.object(pc, "GH_CACHE", os.path.join(d, "gh.json")), \
             mock.patch.object(pc, "note_fetch", lambda *a, **k: None), \
             mock.patch.object(pc, "gh", lambda *a, **k: answer):
            f = pc.RepoFacts()
            fact = f.get("o/n")
        return f, fact

    def test_only_a_404_is_remembered_as_no_such_repo(self):
        pc = self._pc()
        for answer, st, cached in ((self.NOT_FOUND, 404, True),
                                   (self.RATE, 403, False),
                                   (self.NO_REPLY, 0, False)):
            f, fact = self._facts(pc, answer)
            self.assertFalse(fact["exists"])
            self.assertEqual(st, fact["status"])
            self.assertEqual(cached, "o/n" in f.cache,
                             "HTTP %s cached as %s" % (st, "an answer" if cached else "one"))

    def test_a_repo_that_answers_is_remembered(self):
        pc = self._pc()
        f, fact = self._facts(pc, self.REPO)
        self.assertTrue(fact["exists"])
        self.assertEqual(200, fact["status"])
        self.assertIn("o/n", f.cache)

    def test_a_cache_written_before_the_status_existed_is_dropped(self):
        """Those entries are indistinguishable from the poisoned ones, so none is trusted.

        The live cache holds README text under `readme:` beside the repo facts, so the
        filter has to survive an entry that is not a dict at all.
        """
        pc = self._pc()
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        path = os.path.join(d, "gh.json")
        with io.open(path, "w", encoding="utf-8") as fh:
            json.dump({"gone/x": {"exists": False},
                       "kept/y": {"exists": False, "status": 404},
                       "live/z": {"exists": True, "stars": 3},
                       "readme:old/s": "# a README, cached as a bare string",
                       "readme:new/s": {"text": "# a README"}}, fh)
        with mock.patch.object(pc, "GH_CACHE", path):
            self.assertEqual({"kept/y", "live/z", "readme:new/s"},
                             set(pc.RepoFacts().cache))

    def test_a_refused_readme_read_is_not_a_repo_without_one(self):
        """The README is the back-link corroboration, so caching a refusal as "no README"
        holds the candidate at review for ever."""
        pc = self._pc()
        body = json.dumps({"content": base64.b64encode(b"# hi").decode()})
        for answer, text, cached in (((0, body), "# hi", True),
                                     (self.NOT_FOUND, "", True),
                                     (self.RATE, "", False),
                                     (self.NO_REPLY, "", False)):
            d = tempfile.mkdtemp()
            self.addCleanup(shutil.rmtree, d, True)
            with mock.patch.object(pc, "GH_CACHE", os.path.join(d, "gh.json")), \
                 mock.patch.object(pc, "gh", lambda *a, **k: answer):
                f = pc.RepoFacts()
                self.assertEqual(text, f.readme("o/n"))
                self.assertEqual(cached, "readme:o/n" in f.cache,
                                 "%r cached as an answer" % (answer[1][:40],))

    def test_confirm_does_not_report_a_refusal_as_a_404(self):
        """The reader acts on this line. "404" on a live repo is a delete-it instruction."""
        pc = self._pc()

        class F:
            def __init__(self, st):
                self.st = st

            def get(self, _full):
                return {"exists": False, "status": self.st}

        for st, frag in ((404, "GitHub 404"), (403, "would not answer (HTTP 403)"),
                         (0, "would not answer (HTTP no reply)")):
            c = pc.confirm({"repo": "o/n", "why": [], "score": 0}, {"title": "T"}, F(st))
            self.assertFalse(c["exists"])
            self.assertTrue(any(frag in w for w in c["why"]),
                            "HTTP %s reported as %r" % (st, c["why"]))


class TestAQuietHostIsNotADeadLink(unittest.TestCase):
    """`check_structure --links` called anything that did not return a body dead.

    With `retries=1`, one 503 was enough to report a working canonical URL as rot -- the
    opposite direction from the rest of this sweep, and the same root cause. Rot is a 404
    or a 410. Everything else is the host declining to say.
    """

    def _cs(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        sys.path.insert(0, os.path.join(ROOT, "measure"))
        import check_structure
        return check_structure

    PAPERS = [{"links": {"html": "https://a.example/x", "code": "https://b.example/y"}}]

    def _run(self, cs, answers):
        out, results = io.StringIO(), []
        with mock.patch.object(cs, "get_status", lambda u, **kw: (answers(u), b"")), \
             contextlib.redirect_stdout(out):
            cs.links(self.PAPERS, results)
        return results[0]

    def test_a_host_that_would_not_answer_is_not_rot(self):
        cs = self._cs()
        for st in (0, 429, 500, 403):
            r = self._run(cs, lambda _u, st=st: st)
            self.assertTrue(r["ok"], "status %s reported as rot" % st)
            self.assertIn("0 of 2 checked", r["detail"])
            self.assertIn("would not answer", r["detail"])

    def test_a_404_is_still_rot(self):
        cs = self._cs()
        r = self._run(cs, lambda u: 404 if "a.example" in u else 200)
        self.assertFalse(r["ok"])
        self.assertIn("1 dead", r["detail"])
        self.assertIn("2 of 2 checked", r["detail"])

    def test_every_link_answering_reads_as_checked(self):
        cs = self._cs()
        r = self._run(cs, lambda _u: 200)
        self.assertTrue(r["ok"])
        self.assertEqual("2 of 2 checked", r["detail"])


class TestAQuietArxivIsNotACleanAuthorList(unittest.TestCase):
    """Both arXiv name rows in the worklist table read `0` when arXiv served nothing.

    `arxiv_name_file` already declines to accuse on an unread record -- "silence beats a
    false accusation" -- but the table printed the resulting zeros beside **ok**, which is
    the same shape a corpus with no name problems has.
    """

    def _a(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import audit_identity
        return audit_identity

    # A body on every status, including the refusals. That is the case the status check is
    # for: an empty body already fails to parse, but a 503 maintenance page or a 429 served
    # from a cache can be a whole valid feed, and reading it counts a record as checked.
    FEED = ('<feed xmlns="http://www.w3.org/2005/Atom"><entry>'
            '<id>http://arxiv.org/abs/2401.00001v1</id>'
            '<author><name>Leshem Choshen</name></author></entry></feed>')

    def test_an_unread_record_is_not_a_record_with_your_name_right(self):
        a = self._a()
        papers = [{"arxiv": "2401.00001", "title": "T", "slug": "s"}]
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        for st, n_read in ((0, 0), (429, 0), (500, 0), (200, 1)):
            with mock.patch.object(a, "TASKS", d), \
                 mock.patch.object(a, "get_status",
                                   lambda _u, st=st, **kw: (st, self.FEED.encode())), \
                 mock.patch.object(a.time, "sleep", lambda _n: None):
                _path, typo, absent, got = a.arxiv_name_file(papers, ["Leshem Choshen"])
            self.assertEqual(([], []), (typo, absent))
            self.assertEqual(n_read, got, "status %s reported %d read" % (st, got))


class TestAQuietPeerDoesNotHandOverItsPapers(unittest.TestCase):
    """`ownership` reconciles papers.yaml from the peer manifests it could read.

    A peer whose manifest did not answer is absent from `claimed`, which is the same shape
    as a peer claiming nothing -- so `reconcile` strips the owner recorded last run and
    `render` builds our own canonical page for their paper. Splitting a canonical page in
    two is the harm the module's own docstring names.
    """

    CFG = {"collaboration": {"me": "us", "peers": ["https://peer.example/paper-geo.json"]}}
    MANIFEST = {"paper_geo_manifest": 1, "owner": "them",
                "claims": [{"ids": ["10.1/x"], "canonical_page": "https://peer.example/x"}]}

    def _o(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import ownership
        return ownership

    def test_a_refused_manifest_is_not_a_peer_claiming_nothing(self):
        o = self._o()
        old = o._quiet
        try:
            for st in (0, 429, 500):
                o._quiet = ""
                with answering(st):
                    self.assertEqual({}, o.fetch_peers(self.CFG))
                self.assertTrue(o.quiet(), "status %s passed as an answer" % st)
            for st in (404, 410):
                o._quiet = ""
                with answering(st):
                    self.assertEqual({}, o.fetch_peers(self.CFG))
                self.assertEqual("", o.quiet(),
                                 "status %s is an answer and must not stop the run" % st)
            o._quiet = ""
            body = json.dumps(self.MANIFEST).encode()
            with answering(200, body):
                self.assertEqual("them", o.fetch_peers(self.CFG)["10.1/x"]["owner"])
            self.assertEqual("", o.quiet())
        finally:
            o._quiet = old

    def test_papers_yaml_is_not_rewritten_from_a_manifest_that_did_not_answer(self):
        """The write is what matters. Losing `owner: them` here is a second canonical page
        for a paper somebody else owns."""
        o = self._o()
        for quiet, expect_write in (("peer.example -> HTTP 500", False), ("", True)):
            d = tempfile.mkdtemp()
            self.addCleanup(shutil.rmtree, d, True)
            doc = {"papers": [{"slug": "x", "title": "Their paper", "doi": "10.1/x",
                               "citations": 1, "owner": "them", "owner_source": "peer"}]}
            written = []
            with mock.patch.object(o, "DATA", d), \
                 mock.patch.object(o, "load_config", lambda: self.CFG), \
                 mock.patch.object(o, "read_yaml", lambda _p: doc), \
                 mock.patch.object(o, "fetch_peers", lambda _c: {}), \
                 mock.patch.object(o, "quiet", lambda: quiet), \
                 mock.patch.object(o, "write_yaml", lambda p, d_: written.append(p)), \
                 mock.patch.object(sys, "argv", ["ownership.py", "--claim-all"]):
                with contextlib.redirect_stdout(io.StringIO()):
                    if expect_write:
                        o.main()
                    else:
                        with self.assertRaises(SystemExit) as cm:
                            o.main()
                        self.assertIn("did not answer (peer.example -> HTTP 500)",
                                      str(cm.exception))
            self.assertEqual(expect_write, bool(written),
                             "a quiet peer's paper was reconciled" if quiet else
                             "an answered run wrote nothing")
            p = doc["papers"][0]
            if expect_write:
                # An answered run that finds no claim releases the paper. `--claim-all` reads
                # the record before `reconcile` does, so it does not grab one just released.
                self.assertEqual((None, None), (p.get("owner"), p.get("owner_source")))
            else:
                self.assertEqual(("them", "peer"), (p.get("owner"), p.get("owner_source")),
                                 "a refused read released a peer's paper")


class TestAQuietWikidataDoesNotBlankALabel(unittest.TestCase):
    """`wd_labels` bypassed `wd_asked`, so its refusal never reached `carry_wikidata`.

    Every other Wikidata read in `wikidata_audit` records that it did not answer, and
    `carry_wikidata` puts the last run's counts back on the strength of it. This one call
    was the exception, and a run refused only here reported a worklist row naming a bare
    QID with nothing saying why.
    """

    def _a(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import wikidata_audit
        return wikidata_audit

    def test_a_refused_label_read_is_recorded_like_every_other(self):
        a = self._a()
        old = a._wd_quiet
        try:
            a._wd_quiet = ""
            with answering(500, mods=(a,)):
                self.assertEqual({}, a.wd_labels(["Q1"]))
            self.assertEqual("HTTP 500", a._wd_quiet, "the refusal was never recorded")
            a._wd_quiet = ""
            body = json.dumps({"entities": {"Q1": {"labels": {"en": {"value": "IBM"}}}}})
            with answering(200, body.encode(), mods=(a,)):
                self.assertEqual({"Q1": "IBM"}, a.wd_labels(["Q1"]))
            self.assertEqual("", a._wd_quiet)
        finally:
            a._wd_quiet = old


class TestAQuietWikidataLeavesTheWorkOnThePage(unittest.TestCase):
    """Two more pages built entirely from what Wikidata says is still missing.

    `item_state` leaves out an item it could not read and `rows` skips a paper it has no
    state for, so a refusal reads as a paper with every author resolved. `wikidata_orgs`
    reads the same way twice over -- no item under this label, no edge stated -- which is the
    state that creates the group a second time and restates every edge it already carries.
    """

    def _mods(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import wikidata_coauthors as wc
        import wikidata_orgs as wo
        return wc, wo

    def test_an_item_that_was_not_read_is_not_an_item_with_nothing_left(self):
        wc, _ = self._mods()
        old = wc._api_quiet
        try:
            for st in (0, 429, 500):
                wc._api_quiet = ""
                with answering(st, mods=(wc,)):
                    self.assertEqual({}, wc.item_state(["Q1"]))
                self.assertTrue(wc.api_quiet(), "status %s passed as an answer" % st)
            wc._api_quiet = ""
            body = json.dumps({"entities": {"Q1": {"claims": {}}}}).encode()
            with answering(200, body, mods=(wc,)):
                self.assertIn("Q1", wc.item_state(["Q1"]))
            self.assertEqual("", wc.api_quiet())
        finally:
            wc._api_quiet = old

    def test_no_coauthor_page_is_written_from_a_read_that_did_not_answer(self):
        """The batch file is deleted when there is nothing to batch, so a quiet run takes a
        valid pasteable batch with it."""
        wc, _ = self._mods()
        old = wc._api_quiet
        try:
            for quiet, want in (("www.wikidata.org -> HTTP 500", 1), ("", 0)):
                wc._api_quiet = ""
                d = tempfile.mkdtemp()
                self.addCleanup(shutil.rmtree, d, True)
                with open(os.path.join(d, "wikidata_coauthors.qs"), "w") as f:
                    f.write("Q1\tP50\tQ2\n")
                with mock.patch.object(wc, "TASKS", d), \
                     mock.patch.object(wc, "BUILD", d), \
                     mock.patch.object(wc, "read_yaml", lambda p: {"items": {"s1": "Q1"}}), \
                     mock.patch.object(wc, "read_papers", lambda: [
                         {"slug": "s1", "title": "T", "citations": 1}]), \
                     mock.patch.object(wc, "item_state", lambda q: {}), \
                     mock.patch.object(wc, "lookups", lambda n, p, r: {"asked": "d"}), \
                     mock.patch.object(wc, "api_quiet", lambda: quiet), \
                     mock.patch.object(wc, "wdqs_quiet", lambda: ""), \
                     mock.patch.object(sys, "argv", ["wikidata_coauthors.py", "--quiet"]):
                    self.assertEqual(want, wc.main())
                kept = os.path.exists(os.path.join(d, "wikidata_coauthors.qs"))
                self.assertEqual(bool(quiet), kept,
                                 "a quiet read deleted the batch" if quiet else
                                 "the stale batch outlived a run that found nothing")
        finally:
            wc._api_quiet = old

    def test_no_group_is_created_from_a_read_that_did_not_answer(self):
        """Both of `wikidata_orgs`'s reads are checked, because the first one's refusal reads
        as a QID with no label and stops the run at `mistyped` with a page of wrong rows."""
        _, wo = self._mods()
        items = {"g": {"label": "A Coalition", "statements": [
            {"p": "P31", "v": "Q43229", "note": "organization"}]}}
        # `labels_of` answers here, so a run that gets past the second guard would reach the
        # writes rather than stopping at `mistyped`.
        live = {"Q43229": "organization"}
        for goes_quiet_on in (1, 2):
            d = tempfile.mkdtemp()
            self.addCleanup(shutil.rmtree, d, True)
            asked = []
            out = io.StringIO()
            with mock.patch.object(wo, "TASKS", d), \
                 mock.patch.object(wo, "BUILD", d), \
                 mock.patch.object(wo, "described", lambda p: items), \
                 mock.patch.object(wo, "read_yaml", lambda p: {}), \
                 mock.patch.object(wo, "labels_of", lambda q: live), \
                 mock.patch.object(wo, "state_of", lambda *a: {}), \
                 mock.patch.object(wo, "wdqs_quiet",
                                   lambda: (asked.append(1), "query.wikidata.org -> HTTP 500"
                                            if len(asked) >= goes_quiet_on else "")[1]), \
                 mock.patch.object(sys, "argv", ["wikidata_orgs.py", "--quiet"]):
                with contextlib.redirect_stderr(out):
                    code = wo.main()
            self.assertEqual(1, code, "guard %d did not stop the run" % goes_quiet_on)
            self.assertIn("did not answer (query.wikidata.org -> HTTP 500)", out.getvalue())
            self.assertEqual([], os.listdir(d), "guard %d wrote a batch" % goes_quiet_on)


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
        ask = (lambda c: "SELECT ?x WHERE {}")
        for st in (0, 429, 500):
            wc._quiet = ""
            with answering(st, mods=(wc,)):
                self.assertEqual([], wc.batched(["a"], ask))
            self.assertTrue(wc.wdqs_quiet(), "status %s passed as an answer" % st)
        wc._quiet = ""
        empty = b'{"results": {"bindings": []}}'
        with answering(200, empty, mods=(wc,)):
            self.assertEqual([], wc.batched(["a"], ask))
        self.assertEqual("", wc.wdqs_quiet())

    def test_a_batch_too_large_to_come_back_whole_is_asked_again_in_halves(self):
        """A `VALUES` batch matching many items produces more rows than the response body
        carries, and the cut-off arrives as HTTP 200 with a matching `Content-Length`. The
        rows are there to be had in a smaller ask, so a batch is halved before the service
        is called quiet -- and what is reported names the truncation rather than the 200."""
        wc, _ = self._mods()
        importlib.reload(wc)
        self.addCleanup(importlib.reload, wc)
        def answer(url, **kw):
            asked = url.count("%22") // 2
            if asked > 2:
                return 200, b'{"results": {"bindi'
            rows = ", ".join('{"n": {"value": "%d"}}' % i for i in range(asked))
            return 200, ('{"results": {"bindings": [%s]}}' % rows).encode()
        with answering(answer, mods=(wc,)):
            rows = wc.batched(["a", "b", "c", "d"], lambda c: wc.values(c), size=4)
        self.assertEqual(4, len(rows), "a halved batch lost rows")
        self.assertEqual("", wc.wdqs_quiet(), "a batch that answered in halves was called quiet")
        wc._quiet = ""
        with mock.patch.object(wc, "get_status",
                               lambda _u, **kw: (200, b'{"results": {"bindi')):
            self.assertEqual([], wc.batched(["a", "b"], lambda c: wc.values(c)))
        self.assertIn("stopped after 19 bytes", wc.wdqs_quiet())

    def test_the_chunks_that_did_answer_are_not_returned_as_the_whole_answer(self):
        """Half the rows read as all of them is the same mistake as no rows read as none:
        a caller drops an employer, or writes a name Wikidata already carries, from a
        result that is short for a reason nothing to do with what Wikidata holds."""
        wc, _ = self._mods()
        importlib.reload(wc)
        self.addCleanup(importlib.reload, wc)
        one = b'{"results": {"bindings": [{"n": {"value": "x"}}]}}'
        with mock.patch.object(wc, "get_status",
                               lambda url, **kw: (200, one) if "%22a%22" in url else (0, b"")):
            self.assertEqual([], wc.batched(["a", "b"], lambda c: wc.values(c), size=1))
        self.assertTrue(wc.wdqs_quiet())

    def test_a_name_with_a_quote_in_it_is_asked_for_as_written(self):
        """Dropping the quote asks about a different name and reads the answer as this one's."""
        wc, _ = self._mods()
        self.assertEqual('"Bar\\"s" "a\\\\b"', wc.values(['Bar"s', "a\\b"], ""))
        self.assertEqual('"IBM"@en', wc.values(["IBM"]))
        self.assertEqual("wd:Q1 wd:Q2", wc.items_block(["Q1", "Q2"]))

    def test_a_search_index_that_did_not_answer_is_not_a_name_nobody_carries(self):
        wc, _ = self._mods()
        old = wc._api_quiet
        try:
            for st in (0, 429, 500):
                wc._api_quiet = ""
                with answering(st, mods=(wc,)):
                    self.assertEqual({}, wc.asked(wc.API + "?search=Ada"))
                self.assertTrue(wc.api_quiet(), "status %s passed as an answer" % st)
            wc._api_quiet = ""
            with answering(200, b'{"search": []}', mods=(wc,)):
                self.assertEqual({"search": []}, wc.asked(wc.API + "?search=Ada"))
            self.assertEqual("", wc.api_quiet())
        finally:
            wc._api_quiet = old

    def test_an_error_body_is_not_wikidata_carrying_nothing(self):
        """The API answers HTTP 200 with an `error` object when it declines -- read-only,
        maxlag, a malformed batch. Parsed as an answer it has no `entities`, which every
        caller here reads as the item stating nothing and writes over."""
        wc, _ = self._mods()
        old = wc._api_quiet
        try:
            wc._api_quiet = ""
            body = b'{"error": {"code": "readonly", "info": "The wiki is in read-only mode"}}'
            with answering(200, body, mods=(wc,)):
                self.assertEqual({}, wc.entities(["Q1"], "claims"))
            self.assertIn("readonly", wc.api_quiet())
        finally:
            wc._api_quiet = old

    def test_a_batch_of_items_too_large_to_come_back_whole_is_asked_again_in_halves(self):
        """50 items of claims run to 160 KB, and a body too large to deliver arrives cut off
        under HTTP 200 rather than refused -- the same shape that stopped the query service.
        The items are there to be had in a smaller ask, so a chunk is halved first."""
        wc, _ = self._mods()
        old = wc._api_quiet
        try:
            wc._api_quiet = ""

            def answer(url, **kw):
                ids = url.rsplit("ids=", 1)[1].split("|")
                if len(ids) > 2:
                    return 200, b'{"entities": {"Q1"'
                ents = ", ".join('"%s": {"claims": {}}' % q for q in ids)
                return 200, ('{"entities": {%s}}' % ents).encode()
            with answering(answer, mods=(wc,)):
                got = wc.entities(["Q1", "Q2", "Q3", "Q4"], "claims", size=4)
            self.assertEqual(4, len(got), "a halved batch lost items")
            self.assertEqual("", wc.api_quiet(), "a batch that answered in halves was quiet")
            wc._api_quiet = ""
            with answering(200, b'{"entities": {"Q1"', mods=(wc,)):
                self.assertEqual({}, wc.entities(["Q1", "Q2"], "claims"))
            self.assertIn("stopped after 18 bytes", wc.api_quiet())
        finally:
            wc._api_quiet = old

    def test_the_items_that_did_answer_are_not_returned_as_every_item(self):
        """An item left out of the result is an item stating nothing, so half a batch read as
        all of it drops an employer statement or writes a name Wikidata already carries."""
        wc, _ = self._mods()
        old = wc._api_quiet
        try:
            wc._api_quiet = ""
            one = b'{"entities": {"Q1": {"claims": {}}}}'
            with answering(lambda u, **kw: (200, one) if "Q1" in u else (0, b""),
                           mods=(wc,)):
                self.assertEqual({}, wc.entities(["Q1", "Q2"], "claims", size=1))
            self.assertTrue(wc.api_quiet())
        finally:
            wc._api_quiet = old

    def test_no_batch_is_written_from_a_read_that_did_not_answer(self):
        """A quiet read gives `items_by_orcid` and `namesakes` nothing, which is the exact
        state that creates an item. So the run has to end before the batch is written --
        `--apply` reads the same list `main` writes."""
        wc, wp = self._mods()
        rec = {"partial": False, "label": "Ada Example Lovelace", "openalex_label": "",
               "employers": [], "openalex_employers": [], "works": 3, "work_titles": [],
               "openalex_works": 0}
        orcid = "0000-0001-5522-1351"
        old = wc._api_quiet
        try:
            for quiet in ("query.wikidata.org -> HTTP 500", ""):
                wc._api_quiet = ""
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
            wc._api_quiet = old

    def test_no_employer_is_retracted_from_a_read_that_did_not_answer(self):
        """`resync` asks again after `main` checked, so the outage can start in between.
        `stale` retracts an employer statement missing from the employers it was given, and
        a query service that went quiet gives it none of them."""
        wc, wp = self._mods()
        rec = {"partial": False, "label": "Ada Example Lovelace", "openalex_label": "",
               "employers": ["Weizmann Institute of Science"], "openalex_employers": [],
               "works": 3, "work_titles": [], "openalex_works": 0}
        orcid = "0000-0001-5522-1351"
        led = {"items": {orcid: "Q1"}, "labels": {"Q1": "Ada Example Lovelace"}}
        old = wc._api_quiet
        try:
            wc._api_quiet = ""
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
            wc._api_quiet = old

    def test_a_lookup_that_resolved_nothing_is_not_the_records_dropping_the_employer(self):
        """The statement names an item where the records name a string, so a retraction rests
        on every institution in the records having resolved. One that did not leaves this run
        unable to tell an employer the records dropped from one it could not look up -- and
        the two seen so far were a property-path query answering short, and an item somebody
        had removed the English label from."""
        _, wp = self._mods()
        rec = {"partial": False, "label": "Ada Example Lovelace", "openalex_label": "",
               "employers": ["McGill University", "Mila - Quebec AI Institute"],
               "openalex_employers": [], "works": 3, "work_titles": [], "openalex_works": 0}
        emp = {"McGill University": {"qid": "Q201492", "label": "McGill University"}}
        p = wp.described("0000-0001-5522-1351", rec, emp)
        self.assertEqual(["Mila - Quebec AI Institute"], p["unnamed"])
        self.assertEqual([], self._removed(wp.stale(p, self._item("Q49110"), "2026-08-29")),
                         "an institution nothing resolved retracted a statement")
        both = wp.described("0000-0001-5522-1351", rec,
                            dict(emp, **{"Mila - Quebec AI Institute":
                                         {"qid": "Q30289943", "label": "Mila"}}))
        self.assertEqual([], both["unnamed"])
        self.assertEqual([], self._removed(wp.stale(both, self._item("Q201492"),
                                                    "2026-08-29")),
                         "an employer the records still name was retracted")
        self.assertEqual([{"id": "Q1$x", "remove": ""}],
                         self._removed(wp.stale(both, self._item("Q49110"), "2026-08-29")),
                         "every name resolved, so an employer neither names is gone")
        gone = dict(rec, employers=["McGill University"])
        self.assertEqual([{"id": "Q1$x", "remove": ""}],
                         self._removed(wp.stale(wp.described("0000-0001-5522-1351", gone, emp),
                                                self._item("Q49110"), "2026-08-29")))

    def test_a_record_whose_source_went_quiet_retracts_no_employer(self):
        """ORCID answers for the employer and OpenAlex only ever stands in where ORCID is
        silent, which is enough to describe somebody and not enough to retract: an ORCID that
        did not answer is silent in exactly the same way as one that has nothing to say."""
        wc, wp = self._mods()
        rec = {"partial": True, "label": "", "openalex_label": "Ada Example Lovelace",
               "employers": [], "openalex_employers": ["Boston University"],
               "works": 0, "work_titles": [], "openalex_works": 7}
        orcid = "0000-0001-5522-1351"
        emp = {"Boston University": {"qid": "Q49110", "label": "Boston University"}}
        p = wp.described(orcid, rec, emp)
        self.assertEqual((True, []), (p["partial"], p["unnamed"]))
        self.assertEqual([], self._removed(wp.stale(p, self._item("Q174158"), "2026-08-29")),
                         "a source that went quiet retracted a statement")
        led = {"items": {orcid: "Q1"}, "labels": {"Q1": "Ada Example Lovelace"}}
        old = wc._api_quiet
        try:
            wc._api_quiet = ""
            edits = []
            session = mock.Mock()
            session.edit.side_effect = lambda *a, **kw: edits.append(kw)
            with mock.patch.object(wp, "read_yaml", lambda p: led), \
                 mock.patch.object(wp, "records", lambda o, r: {orcid: rec}), \
                 mock.patch.object(wp, "employer_items", lambda n: emp), \
                 mock.patch.object(wp, "asked",
                                   lambda u: {"entities": {"Q1": self._item("Q201492")}}), \
                 mock.patch.object(wp, "wdqs_quiet", lambda: ""):
                wp.resync(session, "2026-08-29")
            self.assertEqual([], [k for k in edits if "remove" in k.get("data", "")],
                             "a quiet source retracted a statement through resync")
        finally:
            wc._api_quiet = old

    def test_a_person_neither_record_names_is_left_out_of_the_resync(self):
        """`described` returns a reason rather than a person when nothing gives a name, and
        `resync` reads the reason instead of the keys a person would have had."""
        wc, wp = self._mods()
        rec = {"partial": True, "label": "", "openalex_label": "",
               "employers": [], "openalex_employers": [], "works": 0,
               "work_titles": [], "openalex_works": 0}
        orcid = "0000-0001-5522-1351"
        self.assertIn("later", wp.described(orcid, rec, {}))
        led = {"items": {orcid: "Q1"}, "labels": {"Q1": "Ada Example Lovelace"}}
        old = wc._api_quiet
        try:
            wc._api_quiet = ""
            session = mock.Mock()
            with mock.patch.object(wp, "read_yaml", lambda p: led), \
                 mock.patch.object(wp, "records", lambda o, r: {orcid: rec}), \
                 mock.patch.object(wp, "employer_items", lambda n: {}), \
                 mock.patch.object(wp, "asked",
                                   lambda u: {"entities": {"Q1": self._item("Q49110")}}), \
                 mock.patch.object(wp, "wdqs_quiet", lambda: ""):
                self.assertEqual((0, 0), wp.resync(session, "2026-08-29"))
            self.assertEqual([], session.edit.call_args_list)
        finally:
            wc._api_quiet = old

    def test_the_records_wording_of_an_institution_is_asked_as_wikidata_spells_it(self):
        """ORCID writes the article Wikidata drops and OpenAlex adds a country, so a name is
        asked for in every spelling, the one the record used first."""
        _, wp = self._mods()
        self.assertEqual(["IBM (United States)", "IBM"], wp.spellings("IBM (United States)"))
        self.assertEqual(["The Hebrew University of Jerusalem",
                          "Hebrew University of Jerusalem"],
                         wp.spellings("The Hebrew University of Jerusalem"))
        self.assertEqual(["Weizmann Institute of Science"],
                         wp.spellings("  Weizmann Institute   of Science "))

    def _removed(self, data: dict) -> list[dict]:
        """The retractions in a `stale` payload, apart from the statements it adds."""
        return [c for c in data.get("claims") or [] if "remove" in c]

    def _item(self, qid: str) -> dict:
        """A live item carrying one employer statement, referenced to the person's ORCID."""
        return {"labels": {"en": {"language": "en", "value": "Ada Example Lovelace"}},
                "descriptions": {"en": {"language": "en",
                                        "value": "researcher at McGill University"}},
                "claims": {"P108": [{"id": "Q1$x",
                                     "mainsnak": {"property": "P108", "datavalue":
                                                  {"value": {"id": qid}}},
                                     "references": [{"snaks": {"P854": [{"datavalue":
                                         {"value": "https://orcid.org/0000-0001-5522-1351"}
                                     }]}}]}]}}


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


class TestARefusalReachesTheRunThatCalledIt(unittest.TestCase):
    """`update.run` records a non-zero exit in `FAILED`, and that is the whole path by which
    one script's refusal reaches the person reading `WORKLIST.md`. A `main` that returns 1
    under a bare `main()` exits 0, so the refusal stops inside the function that raised it
    and the run reports the step as done.
    """

    def test_every_main_that_returns_a_code_hands_it_to_the_interpreter(self):
        for path in sorted(glob.glob(os.path.join(ROOT, "scripts", "*.py"))):
            src = source(path)
            fns = [f for f in ast.parse(src).body
                   if isinstance(f, ast.FunctionDef) and f.name == "main"]
            if not fns:
                continue
            codes = {n.value.value for n in ast.walk(fns[0])
                     if isinstance(n, ast.Return) and isinstance(n.value, ast.Constant)} - {None}
            if not codes:
                continue
            _, mark, tail = src.partition('if __name__ == "__main__":')
            self.assertRegex(
                mark + tail, r"(sys\.exit|raise SystemExit)\(main\(\)\)",
                "%s: main returns %s and nothing carries it out, so a caller reads success"
                % (os.path.relpath(path, ROOT), sorted(codes)))


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
        with answering(429, b'{"error": "Rate limit exceeded"}', mods=(ai,)):
            refused = ai.orcid_public("0000-0002-3491-0632")
        with answering(0, mods=(ai,)):
            silent = ai.orcid_public("0000-0002-3491-0632")
        with answering(200, json.dumps(read).encode(), mods=(ai,)):
            empty = ai.orcid_public("0000-0002-3491-0632")
        self.assertEqual((False, 429), (refused["reachable"], refused["status"]))
        self.assertEqual((False, 0), (silent["reachable"], silent["status"]))
        self.assertEqual((True, 0), (empty["reachable"], empty["works"]))

    def test_the_audit_stops_rather_than_reporting_the_corpus_as_absent(self):
        """`orcid_strays` matches corpus papers against that record, so an unread one makes
        every paper a gap. The guard runs before anything is written, so the last run's
        numbers stand."""
        src = source(os.path.join(ROOT, "scripts", "audit_identity.py"))
        after = src.split('orc = orcid_public(ident["orcid"])', 1)[1]
        guard = after[:after.index("return None") + 11]
        self.assertIn('if not orc["reachable"]:', guard)
        # Nothing may be written between the read and the guard, or the run that could not
        # read the record still leaves its conclusions on disk.
        for writes in ("open(", "write_json", "write_yaml", "_file("):
            self.assertNotIn(writes, guard)
        # `read_surfaces` says so by returning nothing, so `main` has to stop on that before
        # it writes a page of its own.
        bail = src.split("r = read_surfaces(cfg, args)", 1)[1].lstrip()
        self.assertTrue(bail.startswith("if r is None:\n        return 1"), bail[:120])

    def test_only_a_404_writes_the_flag_that_puts_a_page_on_the_worklist(self):
        """`hf_indexed: False` lives in the committed `data/papers.yaml` and the worklist
        turns it into "visit this page", so it may only be written when Hugging Face says
        it has no page. On any other non-answer the last run's flag stands."""
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import collect
        cfg = {"ids": {"huggingface": "someone"}}
        for st in (0, 429, 500):
            with answering(st, mods=(collect,)):
                p = {"slug": "a", "arxiv": "2401.00001"}
                collect.merge_hf([p], cfg)
            self.assertNotIn("hf_indexed", p, "status %s wrote the flag" % st)
        with answering(404, mods=(collect,)):
            p = {"slug": "a", "arxiv": "2401.00001"}
            collect.merge_hf([p], cfg)
        self.assertIs(False, p["hf_indexed"])


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

    def _wd(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import wikidata_audit
        return wikidata_audit

    def _answering(self, ai, status, body=b""):
        return answering(status, body, mods=(ai,))

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
        ai = self._wd()
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

    def test_a_feed_that_stopped_mid_document_is_not_an_unlinked_orcid(self):
        """This author's feed runs to 245 KB, past the size at which a body has come back cut
        off, and a cut-off feed fails to parse exactly as the HTML 404 page does. Read as
        unlinked it says the author registered nothing and puts every paper up to claim."""
        ai = self._ai()
        cut = b'<?xml version="1.0" encoding="UTF-8"?>\n<feed xmlns="http://www.w3.org/2005'
        with self._answering(ai, 200, cut):
            self.assertIsNone(ai.arxiv_registered("0000-0002-0085-6496"),
                              "a feed that stopped read as an unlinked ORCID")
        page = (b'<!DOCTYPE html>\n<html><head><meta charset="utf-8">'
                b"<title>404 Not Found</title></head><body>Not Found<br></body></html>")
        with self._answering(ai, 200, page):
            self.assertEqual(set(), ai.arxiv_registered("0000-0002-0085-6496"),
                             "the arXiv 404 page read as an outage")

    def test_an_arxiv_batch_too_large_to_come_back_whole_is_asked_again_in_halves(self):
        """50 entries carry 50 abstracts and run to 120 KB. Dropped instead of halved, 50
        papers go unchecked for a misspelled author name and no count on the page says so.
        A refusal is not halved -- a smaller ask does not answer it."""
        ai = self._ai()
        feed = ('<feed xmlns="http://www.w3.org/2005/Atom">%s</feed>')
        entry = ('<entry><id>http://arxiv.org/abs/%s</id>'
                 '<author><name>Leshem Choshen</name></author></entry>')
        ids = ["2401.0000%d" % i for i in range(4)]
        calls = []

        def answer(url, **kw):
            got = url.split("id_list=", 1)[1].split("&")[0].split(",")
            calls.append(got)
            if len(got) > 2:
                return 200, b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>'
            return 200, (feed % "".join(entry % i for i in got)).encode()

        with mock.patch.object(ai, "get_status", answer), \
             mock.patch.object(ai.time, "sleep", lambda _s: None):
            got = ai.arxiv_author_strings(ids, batch=4)
        self.assertEqual(sorted(ids), sorted(got), "a halved batch lost papers")
        calls.clear()

        def refuse(url, **kw):
            calls.append(url.split("id_list=", 1)[1].split("&")[0].split(","))
            return 500, b""

        with mock.patch.object(ai, "get_status", refuse), \
             mock.patch.object(ai.time, "sleep", lambda _s: None):
            self.assertEqual({}, ai.arxiv_author_strings(ids, batch=4))
        self.assertEqual([ids], calls, "a refusal was asked again in smaller pieces")

    def test_a_wikidata_answer_that_stopped_is_not_reported_as_http_200(self):
        """A body cut off mid-JSON arrives under HTTP 200, so the reason the worklist prints
        for carrying last run's counts would be a status that means the call succeeded."""
        ai = self._wd()
        old = ai._wd_quiet
        try:
            ai._wd_quiet = ""
            with self._answering(ai, 200, b'{"entities": {"Q1"'):
                self.assertEqual({}, ai.wd_asked("https://www.wikidata.org/w/api.php?x=1"))
            self.assertEqual("an answer that stopped after 18 bytes", ai._wd_quiet)
            ai._wd_quiet = ""
            with self._answering(ai, 503, b""):
                self.assertEqual({}, ai.wd_asked("https://www.wikidata.org/w/api.php?x=1"))
            self.assertEqual("HTTP 503", ai._wd_quiet)
        finally:
            ai._wd_quiet = old

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


class TestTheSuiteCollectsAllOfItself(unittest.TestCase):
    """A `__main__` block anywhere but last silently shortens the suite that runs after it."""

    def test_nothing_is_defined_after_the_main_block(self):
        src = source(os.path.abspath(__file__).replace(".pyc", ".py"))
        body = ast.parse(src).body
        guards = [i for i, n in enumerate(body) if isinstance(n, ast.If)
                  and '__main__' in ast.dump(n.test)]
        self.assertEqual([len(body) - 1], guards,
                         "a `__main__` block mid-file makes a direct run collect only the "
                         "classes above it -- 255 of 448, reported as 17 errors")


class TestAFilledInFidelityRunIsNotOverwritten(unittest.TestCase):
    """A blank task file and a filled-in one are the same shape, so the loss left no trace.

    98 graded papers went that way once, and `measure/fidelity_report.md` still describes
    answers the tasks file no longer holds.
    """

    class Args:
        def __init__(self, **kw):
            self.__dict__.update(dict(engine="e", limit=None, mode=None, force=False,
                                      answer_model=None, grade_model=None), **kw)

    def emit(self, answer, **kw):
        import fidelity
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d)
        path = os.path.join(d, "tasks.json")
        with open(path, "w") as f:
            json.dump({"tasks": [{"slug": "a", "answer": answer, "score": None}]}, f)
        with mock.patch.object(fidelity, "TASKS", path), \
                contextlib.redirect_stdout(io.StringIO()):
            fidelity.emit([("a", {"claims": []})], {}, self.Args(**kw))
        with open(path) as f:
            return json.load(f)

    def test_answers_already_pasted_in_stop_a_re_emit(self):
        with self.assertRaises(SystemExit) as e:
            self.emit("what the engine said")
        self.assertIn("1 answer(s)", str(e.exception))
        # Both ways out, because the refusal is the first time anybody learns the file is
        # precious: score what is there, or say discard it and mean it.
        self.assertIn("--ingest", str(e.exception))
        self.assertIn("--force", str(e.exception))

    def test_force_says_discard_them_and_means_it(self):
        self.assertEqual([None], [t["answer"] for t in self.emit("said", force=True)["tasks"]])

    def test_a_blank_file_is_overwritten_without_a_word(self):
        for blank in (None, "", "   "):
            self.assertEqual([None],
                             [t["answer"] for t in self.emit(blank)["tasks"]], repr(blank))

    def test_nothing_that_is_not_a_tasks_file_counts_as_answers(self):
        import fidelity
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d)
        junk = os.path.join(d, "junk.json")
        with open(junk, "w") as f:
            f.write("not json at all")
        self.assertEqual(0, fidelity.answered(junk))
        self.assertEqual(0, fidelity.answered(os.path.join(d, "absent.json")))


class TestTheShrinkGuardNamesWhatWentDown(LedgerCase):
    """`collect.refuse_shrink` stops a run that lost data, and says which source lost it.

    Live: Semantic Scholar's author record went down mid-run, arXiv ids fell 106 -> 48
    and abstracts 113 -> 88, and the guard's advice was "check the '!' lines above". That
    one line was forty lines up the scroll by then, and the reader who cannot find it has
    no way to tell an outage from a real shrink -- which is the difference between
    rerunning and `--allow-shrink`, and `--allow-shrink` on an outage is permanent.
    """

    def _mods(self):
        """`collect` and `common`, with the per-run tally empty."""
        import collect
        self.common._RUN_FAILS.clear()
        self.addCleanup(self.common._RUN_FAILS.clear)
        return collect, self.common

    def _refuse(self, collect, allow=False):
        """The guard's exit message over a corpus that lost half its arXiv ids."""
        was = [{"slug": str(i), "arxiv": "2501.0000%d" % i, "title": "t"} for i in range(30)]
        now = [dict(p, arxiv=None) for p in was]
        with self.assertRaises(SystemExit) as e:
            collect.refuse_shrink(was, now, allow)
        return str(e.exception)

    def test_a_failed_source_is_named_with_its_count(self):
        collect, common = self._mods()
        for i in (1, 2):
            common.note_fetch("https://api.semanticscholar.org/graph/v1/author/%d" % i,
                              False, "429")
        common.note_fetch("https://api.semanticscholar.org/graph/v1/paper/batch", False, "503")
        common.note_fetch("https://export.arxiv.org/api/query", True)
        out = self._refuse(collect)
        # The whole rendered line, both ways round: a count that does not accumulate and a
        # plural that does not agree both read as a plausible message and say the wrong thing.
        self.assertIn("  api.semanticscholar.org/graph/v1/author/* -- 2 failed calls, last 429",
                      out)
        self.assertIn("  api.semanticscholar.org/graph/v1/paper/batch -- 1 failed call, last 503",
                      out)
        self.assertNotIn("export.arxiv.org", out, "a source that answered was blamed")

    def test_a_clean_run_says_so_rather_than_blaming_the_network(self):
        """The branch that matters most, because it is the one where --allow-shrink is right."""
        collect, _ = self._mods()
        out = self._refuse(collect)
        self.assertIn("not an outage", out)
        self.assertIn("--allow-shrink", out)

    def test_the_flag_lets_the_write_through(self):
        collect, _ = self._mods()
        was = [{"slug": str(i), "arxiv": "2501.0000%d" % i} for i in range(30)]
        collect.refuse_shrink(was, [dict(p, arxiv=None) for p in was], True)

    def test_a_success_does_not_clear_the_failure(self):
        """A source that failed 58 calls and answered twice is exactly the live case."""
        collect, common = self._mods()
        common.note_fetch("https://api.semanticscholar.org/graph/v1/author/1", False, "429")
        common.note_fetch("https://api.semanticscholar.org/graph/v1/author/1", True)
        self.assertEqual([("api.semanticscholar.org/graph/v1/author/*", 1, "429")],
                         common.run_failures())
        self.assertIn("api.semanticscholar.org/graph/v1/author/*", self._refuse(collect))

    def test_the_worst_source_is_first(self):
        collect, common = self._mods()
        for _ in range(3):
            common.note_fetch("https://api.crossref.org/works", False, "503")
        common.note_fetch("https://api.openalex.org/works", False, "429")
        self.assertEqual([("api.crossref.org/works", 3, "503"),
                          ("api.openalex.org/works", 1, "429")], common.run_failures())


if __name__ == "__main__":
    unittest.main(verbosity=2)
