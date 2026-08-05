#!/usr/bin/env python3
"""Validate data files against schema/*.json.

Runs as the last step of update.py so a malformed hand edit or a bad model
proposal fails loudly rather than propagating into published metadata.

Falls back to a small built-in checker when jsonschema is not installed, so the
pipeline still catches the mistakes that actually happen (wrong type, unknown
field, bad topic format) without adding a hard dependency.

Usage:
    python scripts/validate.py [--strict]
"""
from __future__ import annotations

import argparse
import difflib
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA, ROOT, load_config, norm_name, read_yaml  # noqa: E402

SCHEMA_DIR = os.path.join(ROOT, "schema")


def load_schema(name: str) -> dict:
    with open(os.path.join(SCHEMA_DIR, f"{name}.schema.json")) as f:
        return json.load(f)


def with_jsonschema(doc, schema, label: str) -> list[str]:
    import jsonschema
    v = jsonschema.Draft202012Validator(schema)
    errs = []
    for e in sorted(v.iter_errors(doc), key=lambda e: list(e.path)):
        where = "/".join(str(x) for x in e.path) or "(root)"
        errs.append(f"{label}: {where}: {e.message}")
    return errs


TOPIC_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,49}$")


# ---------------------------------------------------------------- regressions
#
# One check per bug that has actually shipped. These run UNCONDITIONALLY: the
# original design put them in a jsonschema-absent fallback, so installing
# jsonschema silently skipped them -- which is why a duplicate slug reached
# production and quietly cost one paper its page.

_LATEX_RESIDUE = re.compile(r"[{}$\\]")
_PRIVATE_BIB = re.compile(r"^\s*pretitle\s*=", re.M)


def regressions(papers: list[dict], repos: list[dict]) -> list[str]:
    errs = []

    # Bug: two truncated titles produced the same slug, so one paper's generated
    # page overwrote the other's. Silent -- 134 pages where 135 were expected.
    seen = {}
    for p in papers:
        if p.get("slug") in seen:
            errs.append(f"papers.yaml: duplicate slug {p['slug']!r} "
                        f"({seen[p['slug']]!r} and {p.get('title', '')[:40]!r}) -- "
                        "one page would overwrite the other")
        seen[p.get("slug")] = p.get("title", "")[:40]

    # Bug: LaTeX braces and math wrappers leaked into page headings and into
    # citation_title, i.e. into the field Scholar matches on.
    for p in papers:
        for f in ("title_display", "venue_display"):
            if p.get(f) and _LATEX_RESIDUE.search(p[f]):
                errs.append(f"papers.yaml: {p.get('slug')}: {f} still contains LaTeX "
                            f"markup: {p[f][:56]!r}")

    # Bug: a private LaTeX macro from the source bibliography shipped in published
    # BibTeX, handing readers an entry that fails to compile.
    for p in papers:
        if p.get("bibtex") and _PRIVATE_BIB.search(p["bibtex"]):
            errs.append(f"papers.yaml: {p.get('slug')}: published BibTeX still "
                        "contains a private `pretitle` field")

    # Bug: the topics API call was built comma-joined, which the endpoint rejects
    # 422. Guard the data side; the call construction is covered by selftest().
    for r in repos:
        for t in r.get("topics") or []:
            if "," in str(t) or " " in str(t):
                errs.append(f"repos.yaml: {r.get('repo')}: topic {t!r} contains a "
                            "comma or space -- the topics endpoint rejects it")

    # Bug: a paper claimed by two parties would get two canonical pages, which is
    # the duplicate-title failure this whole mechanism exists to avoid.
    for p in papers:
        if p.get("owner_conflict"):
            errs.append(f"papers.yaml: {p.get('slug')}: claimed by "
                        f"{p['owner_conflict']} -- resolve before publishing")
    return errs


def selftest() -> list[str]:
    """Assertions about code paths that broke once and are not data-visible."""
    errs = []
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from sweep_github import gh_topics_args
    args = gh_topics_args(["a-b", "c"])
    if args != ["-f", "names[]=a-b", "-f", "names[]=c"]:
        errs.append(f"sweep_github.gh_topics_args regressed: {args!r} -- a "
                    "comma-joined value is rejected 422 by the topics endpoint")
    from common import clean_latex, clean_bibtex, norm_title, slugify
    if clean_latex("{DORA} The $x$ Explorer") != "DORA The x Explorer":
        errs.append("common.clean_latex regressed on braces or math")
    # Co-author names are published in JSON-LD, highwire tags and the page body, so a
    # LaTeX accent that survives into the output misspells a real person everywhere at
    # once. `\i` is the dangerous one: dotless i exists only to carry an accent, and
    # deleting it as a stray command silently removes the vowel rather than the mark --
    # `Garc{\'{\i}}a` came out `Garc\'a`, which is not a smaller error than `Garca`.
    for src, want in ((r"Iker Garc{\'{\i}}a{-}Ferrero", "Iker García-Ferrero"),
                      (r"Afra Feyza Aky{\"{u}}rek", "Afra Feyza Akyürek"),
                      (r'Ekin Aky{"{u}}rek', "Ekin Akyürek"),
                      (r"Erd{\H{o}}s and Stan{\v{c}}{\'{\i}}k",
                       "Erdős and Stančík"),
                      (r"Fran{\c{c}}ois", "François")):
        if clean_latex(src) != want:
            errs.append(f"common.clean_latex mangles an accented name: "
                        f"{clean_latex(src)!r} (want {want!r})")
    # `\emph` and friends must still lose the command and keep the text -- the accent
    # pass runs first and must not have made a letter command look like an accent.
    if clean_latex(r"a \emph{real} \& proper 50\% case") != "a real & proper 50% case":
        errs.append("common.clean_latex regressed on ordinary commands or escapes")
    # A bibliography entry whose `{\textdollar}` lost its backslash to a tab leaves the
    # word `extdollar` behind, and that word reached a published URL. It has to vanish
    # from all three derived strings or they disagree about which paper this is -- the
    # first fix cleaned only the display title, so the slug kept it.
    mangled = "{ extdollar}Q2{ extdollar}: Evaluating"
    for fn, want in ((clean_latex, "Q2: Evaluating"), (slugify, "q2-evaluating"),
                     (norm_title, "q2evaluating")):
        if fn(mangled) != want:
            errs.append(f"common.{fn.__name__} leaves mangled LaTeX in: "
                        f"{fn(mangled)!r} (want {want!r})")
    if slugify("extra credit") != "extra-credit":
        errs.append("common.strip_mangled is eating ordinary words starting with 'ext'")
    # A slug is a published URL. Braces protect capitals inside a word, so replacing
    # them with a separator splits the exact token someone would search for: nine live
    # URLs read `findings-of-the-b-aby-lm-challenge`, none containing `babylm`.
    for src, want in ((r"Findings of the {B}aby{LM} Challenge", "findings-of-the-babylm-challenge"),
                      (r"Compress then Serve: Lo{RA} Adapters", "compress-then-serve-lora-adapters"),
                      (r"M{\'{\i}}rian Silva", "mirian-silva"),
                      (r"a \emph{spaced} command", "a-spaced-command")):
        if slugify(src) != want:
            errs.append(f"common.slugify regressed: {slugify(src)!r} (want {want!r})")
    # The two spellings of one title -- damaged in the .bib, and repaired upstream --
    # have to slug identically, or fixing the bibliography moves a live URL as a side
    # effect. A superscript two is the digit two as far as an address is concerned.
    if slugify(r"Q\({}^{\mbox{2}}\): Evaluating") != slugify(mangled):
        errs.append("common.slugify: repairing the Q2 title upstream moves its URL")
    # Published BibTeX is the exception: repair the command rather than delete it, or
    # the entry someone copies has a literal tab in it and renders `extdollarQ2`.
    fixed = clean_bibtex("@a{k,\n  title={{ extdollar}Q2{ extdollar}: T}\n}")
    if "extdollar" not in fixed or "\\textdollar" not in fixed:
        errs.append(f"common.clean_bibtex no longer repairs mangled LaTeX: {fixed!r}")
    if "pretitle" in clean_bibtex("@a{k,\n  pretitle={\\COL},\n  title={T}\n}"):
        errs.append("common.clean_bibtex no longer strips pretitle")
    # A retitled preprint shares its arXiv id with the published version and nothing
    # else. The title-similarity pass scores that pair near zero, so identifier
    # equality has to merge it on its own -- it did not, once, and the corpus carried
    # two pages for one paper with the citations split between them.
    from collect import dedupe
    out, n_merged, _flagged = dedupe([
        {"title": "All Neural Networks are Created Equal", "arxiv": "1905.10854",
         "citations": 1},
        {"title": "Let's Agree to Agree: Neural Networks Share Classification Order",
         "arxiv": "1905.10854", "citations": 64, "venue": "ICML"},
        {"title": "Something Else Entirely", "arxiv": "2104.08202"},
    ])
    if len(out) != 2 or n_merged != 1:
        errs.append(f"collect.dedupe stopped merging on a shared arXiv id: "
                    f"{len(out)} records out, {n_merged} merged (want 2, 1)")
    elif max(p.get("citations") or 0 for p in out) != 64:
        errs.append("collect.dedupe merged the arXiv pair but lost the citation count")
    # A force_merge group whose aliases now normalize to one record used to fold that
    # record into itself and then drop it -- one correct human decision deleted one
    # paper from the corpus, with no warning anywhere.
    from collect import apply_overrides
    kept = apply_overrides([{"title": "{ extdollar}Q2{ extdollar}: T", "key": "k1"}],
                           {"force_merge": [["Q2: T", "{ extdollar}Q2{ extdollar}: T"]]})
    if len(kept) != 1:
        errs.append(f"collect.apply_overrides dropped a paper on a self-merging "
                    f"force_merge group: {len(kept)} records out (want 1)")
    # The venue is published in the page body, in JSON-LD `isPartOf` and in the highwire
    # tag Scholar matches citations on, so a 110-character truncation of a proceedings
    # name is a metadata defect on three surfaces at once. These are the real strings the
    # sources return, and each one broke a different way while this was being written.
    from common import short_venue
    for src, year, want in (
            # The acronym is in the string, and the pattern also fits a word that is not
            # one: "... Systems 36: Annual Conference on ... Systems 2023" -> Systems 2023.
            ("Advances in Neural Information Processing Systems 36: Annual Conference "
             "on Neural Information Processing Systems 2023, NeurIPS 2023, December 10 "
             "- 16, 2023, New Orleans, LA, USA", 2023, "NeurIPS 2023"),
            # Spelled out, with no year anywhere in it: the year has to come from the paper.
            ("The Thirty-ninth Annual Conference on Neural Information Processing "
             "Systems", 2025, "NeurIPS 2025"),
            # A journal is not named by the year of its issue.
            ("Trans. Assoc. Comput. Linguistics", 2025, "TACL"),
            # Joint conference: the name we recognize is the tail, so the head is a second
            # conference and stays. Both spellings of the join give one output.
            ("Proceedings of the 2024 Joint International Conference on Computational "
             "Linguistics, Language Resources and Evaluation, LREC/COLING 2024, 20-25 "
             "May, 2024, Torino, Italy", 2024, "LREC-COLING 2024"),
            # ... whereas a leading acronym owns the venue and the tail is a subtitle
            # (NAACL-HLT) or the host conference a workshop ran at (*SEM@NAACL-HLT).
            ("Proceedings of the 2021 Conference of the North American Chapter of the "
             "Association for Computational Linguistics: Human Language Technologies, "
             "NAACL-HLT 2021, Online, June 6-11, 2021", 2021, "NAACL 2021"),
            ("Proceedings of the 11th Joint Conference on Lexical and Computational "
             "Semantics, *SEM@NAACL-HLT 2022, Seattle, WA, July 14-15, 2022",
             2022, "*SEM 2022"),
            # Tracks are not the main conference and must survive the compression.
            ("Findings of the Association for Computational Linguistics: EMNLP 2020, "
             "Online Event, 16-20 November 2020", 2020, "Findings of EMNLP 2020"),
            ("Proceedings of the 63rd Annual Meeting of the Association for "
             "Computational Linguistics (Volume 3: System Demonstrations)",
             2025, "ACL 2025 (Demo)"),
            # Acronym in trailing parentheses, year in front.
            ("2025 IEEE 18th International Conference on Cloud Computing (CLOUD)",
             2025, "CLOUD 2025"),
            # Every spelling of "preprint" collapses, because build_site drops the
            # highwire tag for a venue it recognizes as one -- and it recognizes "arXiv"
            # but not "arXiv preprint arXiv:2408.12259".
            ("arXiv preprint arXiv:2408.12259", 2024, "arXiv"),
            ("CoRR", 2024, "arXiv"),
            # Nothing recognized: keep what the source said rather than publish a guess.
            ("Journal of Memory and Language", 2024, "Journal of Memory and Language"),
            ("NeurIPS 2024 Competition Track", 2024, "NeurIPS 2024 Competition Track")):
        got = short_venue(src, year=year)
        if got != want:
            errs.append(f"common.short_venue regressed: {got!r} (want {want!r}) "
                        f"for {src[:60]!r}")
    # Which highwire tag the venue gets. The entry type is unreliable in exactly the
    # direction that matters: `@article` + `journal={ICLR}` is common, `@inproceedings`
    # on a journal paper is not.
    from common import venue_is_conference
    for venue, typ, want in (("ICML 2025", "article", True),
                             ("SurgLLM@ICML", "misc", True),
                             ("EACL", None, True),
                             ("LREC-COLING 2024", "article", True),
                             ("TACL", "article", False),
                             ("Nature", "article", False),
                             ("Journal of Memory and Language", "article", False),
                             ("arXiv", "inproceedings", False)):
        if venue_is_conference(venue, typ) != want:
            errs.append(f"common.venue_is_conference({venue!r}, {typ!r}) is "
                        f"{not want} -- Scholar would file this under the wrong tag")
    return errs


def fallback_repos(doc) -> list[str]:
    """Type and shape checks for when jsonschema is unavailable."""
    schema = load_schema("repos")
    allowed = set(schema["$defs"]["repo"]["properties"])
    kinds = set(schema["$defs"]["repo"]["properties"]["kind"]["enum"])
    errs = []
    seen = set()
    for r in doc.get("repos", []):
        name = r.get("repo", "(no repo field)")
        for k in set(r) - allowed:
            errs.append(f"repos.yaml: {name}: unknown field {k!r}")
        if name in seen:
            errs.append(f"repos.yaml: {name}: duplicate entry")
        seen.add(name)
        if "/" not in str(name):
            errs.append(f"repos.yaml: {name}: repo must be owner/name")
        t = r.get("topics")
        if t is not None:
            if not isinstance(t, list):
                errs.append(f"repos.yaml: {name}: topics must be a list")
            else:
                if len(t) > 8:
                    errs.append(f"repos.yaml: {name}: {len(t)} topics (max 8) -- "
                                "padding a topic list is keyword stuffing")
                if len(set(t)) != len(t):
                    errs.append(f"repos.yaml: {name}: duplicate topics")
                for x in t:
                    if not TOPIC_RE.match(str(x)):
                        errs.append(f"repos.yaml: {name}: invalid topic {x!r} "
                                    "(lowercase, digits, hyphens; <=50 chars)")
        if r.get("kind") and r["kind"] not in kinds:
            errs.append(f"repos.yaml: {name}: kind {r['kind']!r} not in {sorted(kinds)}")
        d = r.get("description")
        if d and len(d) > 160:
            errs.append(f"repos.yaml: {name}: description {len(d)} chars (max 160)")
        if r.get("write_citation_cff") and not r.get("paper_slug"):
            errs.append(f"repos.yaml: {name}: write_citation_cff needs a paper_slug")
    return errs


def fallback_papers(doc) -> list[str]:
    allowed = set(load_schema("papers")["$defs"]["paper"]["properties"])
    errs, seen = [], set()
    for p in doc.get("papers", []):
        slug = p.get("slug", "(no slug)")
        for k in set(p) - allowed:
            errs.append(f"papers.yaml: {slug}: unknown field {k!r}")
        if slug in seen:
            errs.append(f"papers.yaml: {slug}: duplicate slug")
        seen.add(slug)
        if not p.get("title"):
            errs.append(f"papers.yaml: {slug}: no title")
        ax = p.get("arxiv")
        if ax and not re.match(r"^\d{4}\.\d{4,5}$", str(ax)):
            errs.append(f"papers.yaml: {slug}: malformed arxiv id {ax!r}")
    return errs


OVERRIDE_KEYS = {"force_merge", "force_distinct", "also_mine", "extra_arxiv", "drop",
                 "hf_claim_requested", "fields", "absent"}


def check_overrides() -> list[str]:
    """A misspelled override key does nothing, silently, and looks done.

    `overrides.yaml` is the one file that is pure human intent -- every entry is a
    judgement no source could supply. It is read with `.get(name)`, so a key the code
    does not know is not an error but a no-op: the correction sits in the file, in git,
    looking authoritative, and changes nothing. The failure has no symptom to notice,
    which is what makes it worth a check rather than care.
    """
    ov = read_yaml(os.path.join(DATA, "overrides.yaml"))
    if not isinstance(ov, dict):
        return []
    errs = []
    for k in sorted(set(ov) - OVERRIDE_KEYS):
        if k.startswith("_"):          # `_comment` and friends are deliberate
            continue
        near = [c for c in OVERRIDE_KEYS
                if difflib.SequenceMatcher(None, k, c).ratio() > 0.7]
        errs.append(f"overrides.yaml: nothing reads `{k}`, so it has no effect"
                    + (f" -- did you mean `{near[0]}`?" if near else
                       f" (known keys: {', '.join(sorted(OVERRIDE_KEYS))})"))
    # A slug in `fields` that matches no paper is the same class of silent no-op: the
    # hand correction is applied by slug, and a slug moves when a title is corrected.
    papers = (read_yaml(os.path.join(DATA, "papers.yaml")) or {}).get("papers") or []
    if papers:
        live = {p.get("slug") for p in papers}
        hist = (read_yaml(os.path.join(DATA, "slug_history.yaml")) or {}).get("retired") or {}
        for slug in (ov.get("fields") or {}):
            if slug in live:
                continue
            moved = hist.get(slug)
            errs.append(f"overrides.yaml: `fields` has no paper with slug `{slug}`"
                        + (f" -- it moved to `{moved}`, update the key" if moved else
                           " -- the correction is not being applied"))
    return errs


def check_name_lists() -> list[str]:
    """`name_typos` must stay disjoint from `name_variants`, and both from `name`.

    The lists look interchangeable and are not. `name_variants` are asserted outward --
    ORCID also-known-as, schema.org alternateName, the Wikidata label -- while
    `name_typos` are matched and published only as Wikidata aliases. Copying a typo into
    the variants list would assert a misspelling as a name he goes by, and would also
    switch off the check that finds it: `name_match` reports a near-miss as a typo to
    fix upstream, and a listed variant scores `exact` instead. Both failures are silent,
    and the second one is worse -- the arXiv record stays wrong and stops being
    reported, which is the whole identity split this repo exists to close.
    """
    cfg = load_config()
    ident = (cfg or {}).get("identity") or {}
    variants = {norm_name(v) for v in ident.get("name_variants") or []}
    variants.add(norm_name(ident.get("name") or ""))
    errs = []
    for t in ident.get("name_typos") or []:
        if norm_name(t) in variants:
            errs.append(
                f"config.yaml: `{t}` is in both name_typos and name_variants/name. "
                "As a variant it is asserted as a name you use, and it stops being "
                "reported as a typo to fix upstream. Keep it in one list only.")
    return errs


def check_sidecars() -> list[str]:
    """Cross-check sidecars: valid front matter, and claim ids that resolve."""
    try:
        import yaml
    except ImportError:
        return []
    errs = []
    for path in sorted(glob.glob(os.path.join(DATA, "sidecars", "*.md"))):
        name = os.path.basename(path)
        text = open(path).read()
        m = re.match(r"^---\n(.*?)\n---\n?", text, re.S)
        if not m:
            errs.append(f"{name}: no YAML front matter delimited by ---")
            continue
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError as e:
            errs.append(f"{name}: unparseable front matter: {e}")
            continue
        try:
            import jsonschema
            errs += with_jsonschema(fm, load_schema("sidecar"), name)
        except ImportError:
            for req in ("one_liner", "claims"):
                if not fm.get(req):
                    errs.append(f"{name}: missing required field {req!r}")
        # The check jsonschema cannot do: every qa answer must name a real claim.
        ids = {c.get("id") for c in (fm.get("claims") or []) if isinstance(c, dict)}
        for i, qa in enumerate(fm.get("qa") or []):
            for a in (qa.get("answers") or []):
                if a not in ids:
                    errs.append(f"{name}: qa[{i}] answers unknown claim id {a!r}")
            if not (qa.get("q") or []):
                errs.append(f"{name}: qa[{i}] has no question phrasings")
    return errs


# Every place the docs state the size of the corpus itself, as a format string over
# the live counts. Subset counts ("50 papers with no Hugging Face page", "60 of the 90
# repos are forks") are deliberately absent: those describe one finding at one moment,
# while these describe the corpus and so go stale on any run that merges a duplicate or
# picks up a new paper. Three of them were still claiming 135 papers at 115.
#
# A reword breaks this check rather than silently disabling it, which is the intended
# trade: the fix is to update the sentence or update this list, and either way somebody
# has looked. Lines carrying arithmetic derived from the count are marked -- swapping
# the number there without redoing the sum produces a confidently wrong page.
DOC_COUNTS = (
    ("README.md", "corpus ({papers} papers, {repos} repos)", ""),
    ("SKILL.md", "| {papers} papers. Claims", ""),
    ("SKILL.md", "| {repos} repos. Topics", ""),
    ("SKILL.md", "Only 1 of {repos} repos maps", ""),
    ("USAGE.md", "unanswerable at {papers} papers", ""),
    ("docs/PAPERS.md", "{papers} papers. Read", ""),
    ("docs/REPOS.md", "1 of {repos} repos maps to a paper", ""),
    ("docs/MEASURE.md", "~{papers} papers × 6 questions", "recompute the question total"),
    ("docs/MEASURE.md", "~{papers} papers × ~4 months", "recompute the paper-months"),
    ("docs/MEASURE.md", "sidecars for {papers} papers", "recompute the hours"),
)


def check_doc_counts(papers: list[dict], repos: list[dict]) -> list[str]:
    """Catch a doc that still states an old corpus size. See DOC_COUNTS."""
    counts = {"papers": len(papers), "repos": len(repos)}
    if not counts["papers"] or not counts["repos"]:
        return []            # a failed read is already reported by the schema pass
    errs = []
    for fname, template, note in DOC_COUNTS:
        path = os.path.join(ROOT, fname)
        if not os.path.exists(path):
            continue
        want = template.format(**counts)
        if want in open(path).read():
            continue
        tail = f"; {note}" if note else ""
        errs.append(f"{fname}: stale corpus size -- expected {want!r}. Update the "
                    f"sentence (or DOC_COUNTS in scripts/validate.py){tail}")
    return errs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true",
                    help="exit non-zero on any problem (use in CI)")
    args = ap.parse_args()

    have_js = True
    try:
        import jsonschema  # noqa: F401
    except ImportError:
        have_js = False

    errs: list[str] = []
    docs = {}
    for name, fname, fb in (("repos", "repos.yaml", fallback_repos),
                            ("papers", "papers.yaml", fallback_papers)):
        doc = read_yaml(os.path.join(DATA, fname))
        docs[name] = doc
        if doc is None:
            continue
        errs += (with_jsonschema(doc, load_schema(name), fname) if have_js
                 else fb(doc))
    # Always, regardless of jsonschema: these encode bugs that have shipped.
    errs += regressions((docs.get("papers") or {}).get("papers", []),
                        (docs.get("repos") or {}).get("repos", []))
    errs += selftest()
    errs += check_sidecars()
    errs += check_overrides()
    errs += check_name_lists()
    errs += check_doc_counts((docs.get("papers") or {}).get("papers", []),
                             (docs.get("repos") or {}).get("repos", []))

    if not have_js:
        print("note: jsonschema not installed -- using the built-in subset of checks")
    if errs:
        print(f"\n{len(errs)} problem(s):")
        for e in errs[:60]:
            print(f"  {e}")
        if len(errs) > 60:
            print(f"  ... and {len(errs) - 60} more")
        sys.exit(1 if args.strict else 0)
    print("data files valid")


if __name__ == "__main__":
    main()
