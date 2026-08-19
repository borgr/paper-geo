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
import importlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.parse

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
        import draft_sidecars
        text = source(path)
        links = re.findall(r"file://(\S*?)[)>#]", text)
        for got in links:
            self.assertEqual(got, draft_sidecars.REVIEW_PAGE,
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
        "qa": [{"q": ["How much data does it take to fit a model like this?",
                      "Was this validated on more than one dataset?",
                      "What do the authors recommend?"],
                "answers": ["overloaded"]}],
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
        "qa": [{"q": ["How much data does it take to fit a latent-skill model of arena "
                      "outcomes?",
                      "Was the WMT16 result replicated on another language pair?"],
                "answers": ["clean"]}],
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
        ok = {"qa": [{"q": ["How do you merge LoRA adapters without mixing up their "
                            "factorizations?",
                            "Can I compare two models by their skill profile?"]}]}
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
        bad = {"qa": [{"q": ["Is there a guarantee that the estimator is correct?",
                             "How are the model parameters estimated?"]}]}
        found = " ".join(check_readability([("bad.md", bad)]))
        for want in ("'the estimator' has no antecedent", "'the model' has no antecedent"):
            with self.subTest(want=want):
                self.assertIn(want, found)
        ok = {"qa": [{"q": ["Does the anchor-point method apply to prompt selection?",
                            "Do the models I merge have to be related to my task?",
                            "What do the authors of Global-MMLU recommend?",
                            "Is it enough to train only the B matrix in LoRA?"]}]}
        self.assertEqual(check_readability([("ok.md", ok)]), [])

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


class TestPacedHostsAreTheOnesWeHammer(unittest.TestCase):
    """Every host this program fetches in a per-paper loop needs a `PACE` entry.

    The failure it catches is silent and was live: `collect.py` slept 3s between arXiv
    API pages and then probed `arxiv.org/html/<id>` once per paper with no sleep at all,
    so one step was polite and rude to the same host in the same run. Pacing lives in
    `common.PACE` precisely because no single call site can see the others -- which also
    means no single call site can be trusted to notice when it is the one bursting.
    """

    def test_arxiv_and_s2_are_paced(self):
        from common import PACE
        for host in ("arxiv.org", "api.semanticscholar.org"):
            self.assertIn(host, PACE, f"{host} is fetched once per paper and unpaced")
            self.assertGreaterEqual(PACE[host], 1.0, f"{host}'s gap is not a real gap")


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
    """`extra_arxiv` and `extra_openreview` have a stated lifetime, so something has to
    watch both ends of it.

    They exist because a paper the bibliography has not received yet has no page at all,
    and the fix is one entry upstream -- after which the line here is dead weight. Both
    transitions are silent by default, in opposite ways. While the paper is missing
    upstream, the Scholar block cannot report it: that block finds bibliography gaps by
    diffing Scholar against the corpus, and the override has already closed the gap. Once
    the paste lands, the paper correctly stops being reported -- and the line it leaves
    behind is announced once, on stderr, in a five-minute run. The live `extra_arxiv` id
    got there exactly that way, which is what this pins.
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

        It is what `ownership.py` writes for `unclaimed`, so a carry that tests
        truthiness leaves the key out, the next step puts it back, and every collect-only
        run shows a removed line per paper -- 113 of them, all meaning nothing. The point
        of the file's history is to say what changed about the papers.
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
        self.assertTrue(sections, "no paper sections on the review page")
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
        from draft_sidecars import checked
        with open(page, encoding="utf-8") as fh:
            html = fh.read()
        for sec in html.split("<div class=paper ")[1:]:
            slug = sec.split("'")[1]
            d = checked(slug)
            if not isinstance(d, dict):
                continue
            shown = set(re.findall(r"<div class=id>\[[a-z]+\] ([^ <·]+)", sec))
            for c in d["claims"]:
                self.assertIn(str(c["id"]), shown,
                              f"{slug}: claim {c['id']} is on no surface of the page")


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
            "qa": [{"q": ["Does it work?", "Is it known to work?"], "answers": ["c1"]}],
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
        from draft_sidecars import at_sentence
        url = at_sentence(self.HTML, "ing examples per scenario are enough to estima")
        self.assertTrue(url.startswith(self.HTML["html"] + "#:~:text="), url)
        # First and last tokens go: a window cut mid-word never matches as a substring.
        self.assertNotIn("ing", urllib.parse.unquote(url.split("text=")[1]).split())
        self.assertIn("scenario", urllib.parse.unquote(url.split("text=")[1]))

    def test_a_paper_with_no_html_gets_no_link(self):
        from draft_sidecars import at_sentence
        self.assertEqual("", at_sentence({"openreview": "https://openreview.net/f"}, "x y z"))
        self.assertEqual("", at_sentence({"arxiv_pdf": "https://arxiv.org/pdf/1.pdf"}, "x y z"))
        self.assertEqual("", at_sentence(self.HTML, "   "))

    def test_only_the_review_page_links_quotes(self):
        with open(os.path.join(ROOT, "scripts", "draft_sidecars.py"), encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
        # Module-level functions only, so a call inside a nested helper is attributed to
        # the function that owns it. The property being protected is which *surface* links
        # -- `review_page` builds a helper per claim block, and walking every def counted
        # that helper as a second caller and failed on a refactor that changed no surface.
        callers = {fn.name for fn in tree.body
                   if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef))
                   for n in ast.walk(fn)
                   if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "at_sentence"}
        self.assertEqual({"review_page"}, callers)


if __name__ == "__main__":
    unittest.main(verbosity=2)
