#!/usr/bin/env python3
"""Validate data files against schema/*.json.

Runs as the last step of update.py so a malformed hand edit or a bad model
proposal fails loudly rather than propagating into published metadata.

Falls back to a small built-in checker when jsonschema is not installed, so the
pipeline still catches the mistakes that actually happen (wrong type, unknown
field, bad topic format) without adding a hard dependency.

Two kinds of problem, two exit codes, because they deserve different reactions.
A *structural* problem -- schema violation, dangling claim id, missing prompt block
-- means something downstream is already broken, so it exits 1 and stops the caller.
A stale corpus size in a prose sentence, or a sidecar outside the shape bands, exits 0
and is merely reported: the page still renders correctly, so halting a run over it
would only teach the author to skip validation. `--strict` collapses the distinction,
for CI -- and `draft_sidecars.py --accept` treats the shape tier as fatal, because
accepting is the moment the claims become an assertion under the author's name.

Usage:
    python scripts/validate.py [--fix-counts] [--strict]
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
from common import (DATA, QA_ROLES, ROOT, answered_by, load_config,  # noqa: E402
                    norm_name, phrasings, read_yaml, rules_block)

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
    # An affiliation may be a name or a mapping, and the two readers of it must not
    # disagree. `org_name` feeds the byline, the ORCID employment diff and the Wikidata
    # P108 lookup, so a mapping leaking through it publishes `{'name': 'IBM Research'}`
    # as visible text and breaks the ORCID comparison at the same time; `org_ld` feeds
    # JSON-LD, where a dropped identifier is invisible on the page and the whole reason
    # the mapping form exists. Neither failure is visible in the config file.
    from common import org_name
    from build_site import org_ld
    aff = {"name": "Weizmann Institute of Science", "url": "https://www.weizmann.ac.il/",
           "ror": "0316ej306", "wikidata": "Q4182"}
    if org_name(aff) != aff["name"] or org_name(aff["name"]) != aff["name"]:
        errs.append(f"common.org_name regressed on a mapping affiliation: "
                    f"{org_name(aff)!r} -- this string is published as page text")
    ld = org_ld(aff)
    want_same = ["https://ror.org/0316ej306", "https://www.wikidata.org/wiki/Q4182"]
    if ld.get("sameAs") != want_same or ld.get("url") != aff["url"]:
        errs.append(f"build_site.org_ld dropped an affiliation identifier: {ld!r}")
    if org_ld("IBM Research") != {"@type": "Organization", "name": "IBM Research"}:
        errs.append("build_site.org_ld no longer accepts a bare affiliation name")
    # A ROR id given as a full URL used to build https://ror.org/https://ror.org/... .
    # check_affiliations rejects that in config, but org_ld is what publishes it.
    if org_ld({"name": "x", "ror": "https://ror.org/0316ej306"})["sameAs"] != want_same[:1]:
        errs.append("build_site.org_ld doubles the ROR prefix on a URL-shaped id")
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


OVERRIDE_KEYS = {"force_merge", "force_distinct", "also_mine", "extra_arxiv",
                 "extra_openreview", "drop", "hf_claim_requested", "fields", "absent"}


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


def check_slug_history() -> list[str]:
    """A retired URL must point at a live page or at nothing, never at a dead end.

    `build_site.py` writes a redirect only when the target is live, so a target that
    left the corpus -- because the paper was dropped, or renamed by hand without
    re-pointing -- makes the entry inert: no redirect, no error, and a URL that is
    published and indexed starts 404ing with nothing in the build saying so. The
    chain re-pointing in `collect.py` repairs this automatically for renames, but only
    for papers it can still see; a dropped target it cannot.

    `null` is the way to say a 404 is intended, so it passes. Everything else that
    resolves nowhere is reported, with the two honest fixes named.
    """
    hist = (read_yaml(os.path.join(DATA, "slug_history.yaml")) or {}).get("retired")
    papers = (read_yaml(os.path.join(DATA, "papers.yaml")) or {}).get("papers") or []
    if not (hist and papers):
        return []
    live = {p.get("slug") for p in papers}
    return [f"slug_history.yaml: `{old}` redirects to `{new}`, which is not a paper"
            " -- point it at a live slug, or set it to null if the URL is meant to 404"
            for old, new in sorted(hist.items()) if new is not None and new not in live]


def check_wikidata_created() -> list[str]:
    """The created-item ledger must point at live slugs and look like QIDs.

    A slug that has left the corpus is the failure worth catching. The ledger is what
    stops `wikidata_apply.py --papers` recreating an item the query service has not
    indexed yet, and it does that by slug -- so a renamed paper stops matching its own
    entry and the next run mints a second item for it. Duplicate publication items are
    the one mistake here that somebody else has to clean up.

    `slug_history.yaml` is honoured, because a rename that went through the chain is
    exactly the case that must not be reported: the old slug still resolves.
    """
    items = (read_yaml(os.path.join(DATA, "wikidata_created.yaml")) or {}).get("items")
    papers = (read_yaml(os.path.join(DATA, "papers.yaml")) or {}).get("papers") or []
    if not (items and papers):
        return []
    hist = (read_yaml(os.path.join(DATA, "slug_history.yaml")) or {}).get("retired") or {}
    live = {p.get("slug") for p in papers} | {k for k, v in hist.items() if v}
    errs = []
    for slug, qid in sorted(items.items()):
        if not re.fullmatch(r"Q[1-9][0-9]*", str(qid)):
            errs.append(f"wikidata_created.yaml: `{slug}` -> `{qid}` is not a QID")
        if slug not in live:
            errs.append(
                f"wikidata_created.yaml: `{slug}` is not a paper, so the item "
                f"`{qid}` no longer suppresses anything and the next "
                f"`wikidata_apply.py --papers` may create a duplicate. Point the key at "
                f"the paper's current slug, or add the rename to slug_history.yaml")
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


def check_affiliations() -> list[str]:
    """Affiliation entries must be a bare name or `{name, url, ror, wikidata}`.

    The two failure modes are both silent in a way the site only shows after a deploy.
    A misspelled key -- `wikdata`, `ROR`, `link` -- is dropped by `org_ld` and the
    identifier simply never appears, so the entry looks upgraded in the config and is
    still a bare name in the published JSON-LD. And a malformed identifier is worse than
    a missing one: these values are pasted into `https://ror.org/$1` and
    `https://www.wikidata.org/wiki/$1`, so a QID with a stray character or a ROR id
    copied as a full URL builds a `sameAs` that either 404s or, if it resolves, asserts
    that he belongs to some other organisation. Checked by shape only -- whether Q4182 is
    the right institution is a question about the world, not about the file.
    """
    allowed = {"name", "url", "ror", "wikidata"}
    errs = []
    for a in (load_config() or {}).get("identity", {}).get("affiliations") or []:
        if isinstance(a, str):
            continue
        if not isinstance(a, dict) or not (a.get("name") or "").strip():
            errs.append(f"config.yaml: affiliation {a!r} has no name")
            continue
        who = a.get("name")
        for k in set(a) - allowed:
            errs.append(
                f"config.yaml: affiliation {who!r} has unknown key `{k}`. Accepted keys "
                f"are {', '.join(sorted(allowed))}; an unknown one is dropped silently "
                "and the entry publishes as a bare name.")
        if a.get("ror") and not re.fullmatch(r"0[0-9a-hj-km-np-tv-z]{6}[0-9]{2}", str(a["ror"])):
            errs.append(
                f"config.yaml: affiliation {who!r} has ror `{a['ror']}`, which is not a "
                "ROR id. The id is the 9-character path from the URL -- 0316ej306, not "
                "https://ror.org/0316ej306 -- because the URL is built from it.")
        if a.get("wikidata") and not re.fullmatch(r"Q[1-9][0-9]*", str(a["wikidata"])):
            errs.append(
                f"config.yaml: affiliation {who!r} has wikidata `{a['wikidata']}`, which "
                "is not a QID. Expected the form Q4182.")
        if a.get("url") and not str(a["url"]).startswith(("http://", "https://")):
            errs.append(
                f"config.yaml: affiliation {who!r} has url `{a['url']}`, which is not "
                "absolute. Organisation URLs are published as given, not resolved "
                "against your own site.")
    return errs


def read_sidecars(paths: list[str] | None = None) -> tuple[list[tuple[str, dict]], list[str]]:
    """Parse front matter once for the three checks that need it.

    Returns the files that parsed and errors for the ones that did not, so a broken file
    is reported exactly once instead of once per check.
    """
    try:
        import yaml
    except ImportError:
        return [], []
    out, errs = [], []
    for path in paths or sorted(glob.glob(os.path.join(DATA, "sidecars", "*.md"))):
        name = os.path.basename(path)
        # A leading HTML comment is dropped first so this works unchanged on a draft,
        # which carries the `<!-- DRAFT -->` banner: `--accept` has to be able to run
        # every check on the file it is about to promote, not on the promoted copy.
        text = re.sub(r"\A\s*<!--.*?-->\s*", "", open(path).read(), flags=re.S)
        m = re.match(r"^---\n(.*?)\n---\n?", text, re.S)
        if not m:
            errs.append(f"{name}: no YAML front matter delimited by ---")
            continue
        try:
            out.append((name, yaml.safe_load(m.group(1)) or {}))
        except yaml.YAMLError as e:
            errs.append(f"{name}: unparseable front matter: {e}")
    return out, errs


def check_sidecars(entries: list[tuple[str, dict]]) -> list[str]:
    """Structural checks: schema-valid front matter, and claim ids that resolve."""
    errs = []
    for name, fm in entries:
        try:
            import jsonschema  # noqa: F401
            errs += with_jsonschema(fm, load_schema("sidecar"), name)
        except ImportError:
            for req in ("one_liner", "claims"):
                if not fm.get(req):
                    errs.append(f"{name}: missing required field {req!r}")
        # The check jsonschema cannot do: every qa answer must name a real claim.
        ids = {c.get("id") for c in (fm.get("claims") or []) if isinstance(c, dict)}
        for i, qa in enumerate(fm.get("qa") or []):
            for a in answered_by(qa):
                if a not in ids:
                    errs.append(f"{name}: qa[{i}] answered_by unknown claim id {a!r}")
            if not phrasings(qa):
                errs.append(f"{name}: qa[{i}] has no question phrasings")
    return errs


# ------------------------------------------------------------------- shape tier
#
# The bands in docs/SIDECAR.md §2 rule 9, which JSON Schema cannot express: they are
# about how many of a thing there are and how they relate to each other, not about
# types. Non-fatal on purpose -- a page with 22 claims renders correctly and is merely
# worse, and the 19 existing drafts predate the bands. `--accept` is where it bites.
#
# Two kinds of number live here. `CLAIMS` and `ROLES_FILLED` are design decisions from §2,
# and the current drafts are meant to violate them: a paper has a handful of findings, so
# 17 claims is one finding split three ways and the fix is redrafting, not a wider band.
# The length and count caps are the opposite -- each is the 90th percentile of what the
# 317 already-drafted claims do, because a cap set through the middle of honest practice
# is one the author learns to ignore, and then the bands stop being read at all.

CLAIMS = (5, 15)
CLAIM_TEXT = (60, 450)
# The scope floor was 80, and rule 31 is what showed 80 to be wrong. It was set from a
# corpus whose scopes all carried a trailing "..., demonstrating robust performance"; with
# that clause deleted as the rule asks, 18 scopes in the corpus fall between 47 and 74
# chars and every one of them is a real single-clause condition -- "Llama3-8B models
# finetuned with LoRA on NLI tasks", "LoRA ranks ranging from 4 to 768 on the per-task
# vision benchmark". So the two rules together demanded the padding back, which is
# exactly the failure decision C2 in docs/SIDECAR.md rejected a scope *template* to
# avoid. 40 is under the shortest honest scope in the corpus and above the vacuous ones
# the floor was for ("Further research is needed", "Vision encoders only"), and the
# content of a bad scope is caught by rule 22 and rule 31 rather than by its length.
CLAIM_SCOPE = (40, 800)
# Deliberately generous: a question group is query surface, and more real phrasings of a
# real question is the whole point. The ceiling only catches a run of invented questions.
QA_GROUPS = (4, 20)
# How many of the four `QA_ROLES` a group has to fill. There is no upper band any more --
# the roles are a closed set, so four is the ceiling by construction, and the old 2-4 count
# could be satisfied by three rewordings of one sentence. `plain` is separately required:
# it is the route a reader who has not read the paper can follow, and it is the phrasing
# published as the group's heading.
ROLES_FILLED = 2
MISREADINGS_MAX = 14
TERMINOLOGY_MAX = 13


def tokens(s: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", str(s).lower())


def coined_forms(coined: str) -> list[list[str]]:
    """Token sequences that count as naming the paper's own coinage.

    The whole name, plus any acronym-shaped part of it: a question phrased around
    `TIES` alone is as unreachable as one phrased around `TIES-Merging`. `Merging` is
    not acronym-shaped and is exactly the word a stranger would type, so it does not
    count -- which is the distinction the check exists to make.
    """
    forms = [tokens(coined)]
    for part in re.split(r"[\s/-]+", str(coined)):
        if len(part) >= 3 and (part.isupper() or re.search(r"[a-z][A-Z]", part)):
            forms.append(tokens(part))
    return [f for f in forms if f]


def says(phrase: str, form: list[list[str]]) -> bool:
    """Whether any form appears as a contiguous run of whole tokens.

    Whole tokens rather than a substring, or `properties` would count as `TIES`.
    """
    hay = tokens(phrase)
    return any(hay[i:i + len(f)] == f
               for f in form for i in range(len(hay) - len(f) + 1))


def check_sidecar_shape(entries: list[tuple[str, dict]]) -> list[str]:
    """The bands and the coverage rules -- docs/SIDECAR.md §4 rows 12-19."""
    errs = []
    for name, fm in entries:
        def bad(msg: str) -> None:
            errs.append(f"{name}: {msg}")

        claims = [c for c in (fm.get("claims") or []) if isinstance(c, dict)]
        qa = [g for g in (fm.get("qa") or []) if isinstance(g, dict)]
        kinds = [c.get("kind") or "result" for c in claims]
        n_ctx = kinds.count("context")

        lo, hi = CLAIMS
        if claims and not lo <= len(claims) <= hi:
            bad(f"{len(claims)} claims, outside the {lo}-{hi} band -- each claim "
                "competes with its siblings on its own page")
        if claims and not n_ctx:
            bad("no `kind: context` claim. Nothing here answers 'what should I read "
                "about X', which is the question class with the query volume")
        elif n_ctx > len(claims) - n_ctx:
            bad(f"{n_ctx} of {len(claims)} claims are `kind: context` -- `result` has "
                "to outnumber `context`, or the page is about its own importance")

        for c in claims:
            where = f"claim {c.get('id', '?')!r}"
            for field, (flo, fhi) in (("text", CLAIM_TEXT), ("scope", CLAIM_SCOPE)):
                n = len(str(c.get(field) or "").strip())
                if n and not flo <= n <= fhi:
                    bad(f"{where}: {field} is {n} chars, outside {flo}-{fhi}")

        lo, hi = QA_GROUPS
        if not qa:
            # Every other question rule below is guarded by `if qa`, so before this line
            # a sidecar with no questions at all passed all of them -- the FAQ surface,
            # the entry-point rule and the orphan check alike. Invisible while only one
            # model wrote drafts, because it always wrote questions; open-weight models
            # asked to fill the same schema return claims and stop, since `qa` is not in
            # the schema's `required` and nothing made them.
            bad("no `qa` groups at all -- the questions are half of what a sidecar "
                f"publishes, and the band is {lo}-{hi}")
        elif not lo <= len(qa) <= hi:
            bad(f"{len(qa)} qa groups, outside the {lo}-{hi} band")
        for i, g in enumerate(qa):
            ask = g.get("ask") if isinstance(g.get("ask"), dict) else {}
            # A group still carrying `unsorted` predates the roles, and its phrasings were
            # migrated without being classified -- see `common.phrasings`. Asking it for
            # `plain` would be asking the author to re-review 1263 groups they already
            # accepted, so the only thing checked here is that the bucket is not empty; the
            # roles bite on the redraft, where a model fills them.
            legacy = [x for x in (ask.get("unsorted") or []) if str(x).strip()]
            filled = [r for r in QA_ROLES if str(ask.get(r) or "").strip()]
            if legacy:
                if not (filled or legacy):
                    bad(f"qa[{i}]: no phrasings at all")
                continue
            if not filled:
                bad(f"qa[{i}]: no phrasings at all")
            elif "plain" not in filled:
                bad(f"qa[{i}]: no `plain` phrasing -- the roles filled are "
                    f"{', '.join(filled)}, and none of them is the wording someone who "
                    f"has not read the paper would type")
            elif len(filled) < ROLES_FILLED:
                bad(f"qa[{i}]: only `plain` is filled -- one question needs at least "
                    f"{ROLES_FILLED} of {len(QA_ROLES)} routes ("
                    f"{', '.join(QA_ROLES)}), and they have to differ in vocabulary "
                    f"rather than in word order")
            for r in filled:
                if not str(ask[r]).strip().endswith("?"):
                    bad(f"qa[{i}]: `{r}` is not a question -- every role is a natural "
                        f"question ending in `?`, never a keyword string")

        # Coverage. A claim nothing points at renders with no route to it, and a general
        # question with no `context` claim to answer it cannot be asked at all.
        ctx_ids = {c.get("id") for c, k in zip(claims, kinds) if k == "context"}
        answered = {a for g in qa for a in answered_by(g)}
        if qa and ctx_ids and not (answered & ctx_ids):
            bad("no qa group is answered by a `context` claim -- the entry-point "
                "question is the one required question class")
        orphans = [c.get("id") for c in claims if c.get("id") not in answered]
        if qa and orphans:
            bad(f"{len(orphans)} claim(s) no question points at: "
                f"{', '.join(str(o) for o in orphans[:6])}")

        if fm.get("coined"):
            if not fm.get("gloss"):
                bad(f"coins {fm['coined']!r} with no `gloss` -- a coined name has no "
                    "lexical route from what people actually type")
            forms = coined_forms(fm["coined"])
            for i, g in enumerate(qa):
                qs = phrasings(g)
                shared = [f for f in forms if all(says(q, [f]) for q in qs)]
                if qs and shared:
                    # The matched form, not the whole coinage: `coined_forms` also matches
                    # an acronym-shaped part, so "Global-MMLU" flagged phrasings whose only
                    # offence was the word `MMLU` -- and a model told to remove
                    # "Global-MMLU" from a phrasing that never contained it rewrote the
                    # question, changed nothing the check reads, and had the rewrite
                    # reverted. Name the string that has to go.
                    # Rendered from the coinage as written, not from its tokens: the
                    # tokens are lowercased and space-joined, so `MMLU` printed as
                    # 'm m l u' and named nothing anyone could search for or remove.
                    labels = {tuple(tokens(fm["coined"])): str(fm["coined"])}
                    for part in re.split(r"[\s/-]+", str(fm["coined"])):
                        labels.setdefault(tuple(tokens(part)), part)
                    said = labels.get(tuple(shared[0]), " ".join(shared[0]))
                    also = "" if said == str(fm["coined"]) \
                        else f" (part of {fm['coined']!r})"
                    bad(f"qa[{i}]: every phrasing contains {said!r}{also} -- at "
                        "least one has to be answerable by someone who has never "
                        "heard the name")

        for field, cap in (("misreadings", MISREADINGS_MAX),
                           ("terminology", TERMINOLOGY_MAX)):
            n = len(fm.get(field) or [])
            if n > cap:
                bad(f"{n} {field} entries (max {cap}) -- past that they are invented "
                    "rather than observed")

        # A misreading is retrieved and quoted like any other line on the page, so one
        # phrased as a question hands an engine the wrong belief with no correction
        # attached to it. State the correction: not "does it work on long inputs?" but
        # "it is not evaluated above 4k tokens".
        for i, m in enumerate(fm.get("misreadings") or []):
            if str(m).strip().endswith("?"):
                bad(f"misreadings[{i}] is a question -- state the correction instead, "
                    "or the quotable sentence is the misreading itself")
    return errs


# -------------------------------------------------------------- readability tier
#
# The ways a well-formed sidecar is still a bad passage to retrieve, each one measured
# over the drafted corpus before being written down. They are not in the shape tier, and
# the reason is which files each tier reaches: `validate.py` globs `data/sidecars/*.md`,
# so the shape tier judges the author's *published* words, and `--strict` makes it
# fatal. These findings are about what to write next, not about retracting what is
# already out, so they run at `--accept` -- where the author can still take the note or
# override it with `--anyway` -- and on the review page, where he reads the draft.
#
# A sentence limit rather than only the character band, because the band measures the
# wrong thing: 450 chars admits one 79-word sentence, and that is the actual defect.
# Splitting it costs no content, so unlike the character ceilings these are not the
# 90th percentile of current practice -- current practice fails them, by design.

CLAIM_SENTENCES = 2
CLAIM_SENTENCE_WORDS = 32
# Each colon, semicolon or dash past the first is where a second proposition was bolted
# on rather than made its own claim. One is the normal "finding: the number".
CLAIM_SEPARATORS = 1

# The `FAQPage` answer `build_site.py` publishes is the claim, then the literal words
# "Holds for:", then the whole scope. So a scope longer than its claim makes the answer
# mostly caveat -- and it fails in both directions at once, since an extractive
# summariser quotes the front and drops exactly the part that was there to protect the
# claim, while the embedding of the whole answer drifts toward hedging vocabulary. 290 of
# 325 drafted scopes are longer than their claim; one runs 14 sentences against a
# 348-character claim. Three conditions is the ceiling because a fourth means the claim
# was stated more broadly than it holds, and narrowing the claim is the better fix.
SCOPE_SENTENCES = 3
# Below this a scope cannot be the thing the ratio rule guards against. The rule is that a
# scope must not be longer than its claim, because the published `FAQPage` answer is the
# claim then "Holds for:" then all of the scope, and the measured pathology was scopes of
# 426-798 chars at a median 1.5x their claim -- an answer that is mostly caveat. Read
# without a floor it also fires on 103 chars against 91, which is not that pathology, and
# combined with the 80-char band floor it leaves an 11-character target on a short claim:
# unhittable, so a model told to shorten oscillates between the two rules and a reviewer
# reads "scope too short" and "scope too long" about the same field on consecutive runs.
# Measured across all 344 claims in the live sidecars and drafts, the floor excuses 6 and
# still flags 237 of 243 -- every one of the 30 in the two published files included.
SCOPE_RATIO_FLOOR = 160

# Half of a page's `result` claims must state a figure. A number is what makes a passage
# worth quoting rather than paraphrasing, and a paraphrase is a citation lost. Measured
# by `figures`, so a model name (`T5`, `ViT-L/14`) does not count as a magnitude. The
# median drafted page reaches 61% and the weakest 33%. Never satisfiable by inventing
# one: `check_claim_numbers` would catch that, and it is fatal at `--accept`.
RESULT_FIGURES = 0.5

# A paper cannot be asked for magnitudes it never reported. SERRANT is an
# annotation-scheme paper: one distinct figure in its entire text, against a median of
# 154 across the corpus and 18 for the next-lowest paper. Its claims say what the tool
# does to an edit -- demonstrated, so `result`, but with nothing measured -- and the
# coverage rule was therefore unsatisfiable there by any honest means. Years are
# excluded from the count because every paper's citation list carries dozens of them.
PAPER_FIGURES_FLOOR = 10

# A reference with no antecedent on screen. Both halves of a question's job fail on
# one: nobody queries "a model like this", and a `FAQPage` answer is extracted with no
# page around it, so the words have nothing to point at. Deliberately narrow -- a
# pronoun bound to a noun inside the same question ("compare models by their skill
# profile") is ordinary English and must not fire, so only two shapes count: a
# demonstrative that no noun precedes, and `it`/`they` as the opening subject.
_UNBOUND = re.compile(
    r"\blike th(?:is|ese|ose)\b"
    r"|\bth(?:is|ese|ose)\s+(?:paper|work|study|method|approach|framework|model|"
    r"result|technique|trick|setup|finding|idea|dataset|benchmark|system|thing)s?\b"
    r"|\b(?:is|are|was|were|does|do|did|has|have|had|can|could|would|will|should)\s+"
    r"th(?:is|ese|ose)\b"
    r"|\bth(?:is|ese|ose)\b\s*[?,.]|\bth(?:is|ese|ose)\b$"
    # "the authors of Global-MMLU" names them, so only the unattached form counts.
    r"|\bthe authors?\b(?!\s+of\b)"
    r"|\bhere\b\s*\??$"
    # Expletive `it` is not a reference: "is it enough to train only B" has no antecedent
    # to want, and the infinitive it anticipates is what tells them apart -- so the
    # exemption keys on that adjective rather than on the infinitive sitting flush against
    # it. "Is it worth the extra bookkeeping to keep every checkpoint's loss?" is the same
    # dummy subject with a noun phrase in between, and requiring `<adj> to` adjacent
    # flagged 21 of those across the corpus. Reaching forward for the `to` instead would
    # have exempted "does it generalize to new tasks", which is a real reference to nothing
    # and has to keep failing -- so the list of predicates is closed and short.
    r"|^(?:is|are|was|were|does|do|did|has|have|can|could|would|will|should)\s+"
    r"(?:it|they|its|their)\b(?!\s+\w+\s+that\b)"
    r"(?!\s+(?:worth|better|best|enough|possible|feasible|safe|true|ok|okay|necessary"
    r"|useful|worthwhile|harder|easier|hard|cheaper|faster|fine|reasonable|realistic"
    r"|practical|advisable|common|normal|standard|sensible|risky|wise)\b)", re.I)

# The same failure one step subtler, and the one the demonstrative rules miss entirely:
# a definite noun phrase whose referent is the paper the reader is not looking at.
# "Is there a guarantee that the estimator is correct?" contains no demonstrative and no
# pronoun, and is still unanswerable and unmatchable -- *which* estimator is the whole
# question. Only the bare form counts, `the` immediately followed by the role noun: a
# qualifier in between is what makes it specific, so "the anchor-point method" and "the
# best active-learning strategy" are exactly the phrasings this must leave alone.
_BARE_DEFINITE = re.compile(
    r"\bthe\s+(?:estimator|correction|method|approach|framework|algorithm|model|models"
    r"|pipeline|metric|technique|system|procedure|setup|dataset|benchmark|corpus"
    r"|suite|study|experiment|experiments|finding|findings|task|game|challenge"
    r"|paper|work|authors?|tool|score|scores)\b"
    # A relative clause binds it as well as an adjective does: "the models I merge" and
    # "the model they came from" both say which, and both are the natural English.
    r"(?!\s+(?:I|we|you|they|that|which|who|whose)\b)", re.I)

# ...unless the question names something a query would contain. A capitalised token past
# the first word, a coined name, a digit: any of them gives "the model" something on
# screen to attach to, and firing anyway would push drafters toward vaguer questions
# rather than more specific ones. The first word is excluded because every question
# starts capitalised.
_NAMES_SOMETHING = re.compile(r"\S+\s+.*?\b[A-Z][A-Za-z0-9]*[A-Z0-9][A-Za-z0-9-]*\b"
                              r"|\S+\s+.*?\b[A-Z][a-z]{2,}\b|\d")

# A claim that enumerates its parts. Matches "(1) ... (2)", "(i) ... (ii)" and
# "(a) ... (b)" only: a bare "1." never appears mid-sentence in the corpus, and a lone
# "(1)" with no second item is a citation or a footnote marker rather than a list.
_ENUMERATES = re.compile(r"(\(\s*(?:1|i|a)\s*\)).{5,}?(\(\s*(?:2|ii|b)\s*\))", re.I | re.S)

# How close two published sentences may be before they are the same sentence, compared on
# content words so that punctuation and casing cannot hide identity.
_SAME_TEXT = 0.9


def _words(s) -> list[str]:
    return re.sub(r"[^a-z0-9 ]", " ", str(s or "").lower()).split()


# A scope opening by saying what kind of claim it qualifies. It is published after the
# literal words "Holds for:", so this is the one thing there that cannot parse.
# `holds` is the failure mode of telling a drafter to complete "Holds for:" -- it writes
# "Holds for: Holds by construction", which the fixed list of classifying nouns misses.
_CLASSIFIES = re.compile(
    r"^\s*(?:holds?\b|applies\b"
    r"|th(?:is|ese|at)\s+(?:is|are)\b"
    r"|it\s+is\s+(?:a|an|the)\b"
    r"|an?\s+(?:claim|description|counting|framing|reading|statement|definition|"
    r"design|property|consequence|restatement|algebraic|entry|observation|"
    r"characterisation|characterization|judgement|judgment)\b"
    r"|the\s+(?:paper's|claim|point)\s+)", re.I)

# A scope clause that restates what the result shows instead of bounding it. Rule 3 has
# always ruled this out in prose -- "a restatement of the finding does not belong here" --
# and nothing enforced it, so the class survived every check: "merging 2 to 11 tasks,
# showing consistent performance improvements" bounds the claim in its first half and then
# asserts it again in the second, published after "Holds for:" as if it were a condition.
#
# Two shapes, measured across the 344 live and drafted scopes. The trailing participial
# comment (", demonstrating ...") is 18 of them, all in drafts from one model, which is
# why it reads as a habit rather than as English a scope needs. The participles are
# restricted to *reporting* verbs and to the -ing form on purpose: three near misses in
# the corpus are real conditions using the same verbs in a finite or past form -- "which
# was pretrained with decay, showed less of the adverse effect", "shown as two heatmaps
# per model rather than a table", "established before any merging happens". The second
# shape is a showing verb plus an upshot noun anywhere in the field, for the same clause
# written without the comma; its noun list is closed so that "shows no effect below 1B",
# which is the condition the rule is asking for, cannot match.
_UPSHOT_PARTICIPLE = (r"showing|demonstrating|highlighting|illustrating|underscoring"
                      r"|confirming|indicating|proving|emphasi[sz]ing|reflecting"
                      r"|suggesting|validating|establishing|revealing")
_UPSHOT_NOUN = (r"benefits?|effectiveness|importance|advantages?|superiority|impact|value"
                r"|utility|necessity|robustness|generality|strength")
_SHOWS_UPSHOT = re.compile(
    rf"[,;]\s*(?:and\s+|thus\s+|thereby\s+|so\s+)?(?:{_UPSHOT_PARTICIPLE})\b"
    rf"|\b(?:show\w*|demonstrat\w+|highlight\w+|illustrat\w+)\s+"
    rf"(?:the\s+|that\s+|its\s+|their\s+)?(?:{_UPSHOT_NOUN})\b", re.I)

# A `result` claim's scope naming the analysis instead of its conditions: "the analysis of
# sign conflicts and their impact on merging" as the bound on "resolving sign conflicts is
# crucial". It parses after "Holds for:" and it is falsifiable by nothing -- and what it
# does say is already in `evidence`, which is the field for where in the paper the result
# lives. The real bound for that claim is the sweep: which models, which values of k.
# 8 of 344 scopes open this way, 5 of them on `result` claims; the other 3 are `context`
# claims reading "the context of merging LoRA models, as of publication in 2025", which is
# left alone because a `context` claim has no measurement to state conditions on and §2
# names the publication date as its honest bound.
_NAMES_THE_ANALYSIS = re.compile(
    r"^\s*(?:the\s+)?(?:analys[ei]s|study|experiments?|evaluation|investigation|discussion"
    r"|examination|ablation)\s+(?:of|in|on)\b", re.I)

# The subset of the above that is the renderer's own prefix, written into the field. A
# separate pattern rather than a branch on the match text, because "Holds for models
# above 1B" and "This is a description of the algorithm" need opposite advice.
_PREFIX_DOUBLED = re.compile(r"^\s*(?:holds?\s+(?:for|only|in|when|under|true)"
                             r"|applies\s+(?:to|only|when|in|under))\b", re.I)

# Claim text that opens by talking about the paper instead of naming its object. Rule 2
# has said since the file existed that a claim may not lean on "we" or "this paper";
# nothing enforced it, and 8% of drafts open exactly that way -- "The paper proves...",
# "The contribution is a frame as much as a method". Extracted alone that says nothing
# about *which* paper, and it spends the quotable front on commentary. Only the
# unambiguous heads are listed: "the prevailing practice -- reading a hidden
# representation directly --" names its subject in the appositive and must not fire.
_ABOUT_PAPER = re.compile(
    r"^\s*(?:th(?:e|is)\s+(?:paper|study|authors?)(?:'s)?\b"
    r"|the\s+(?:contribution|diagnosis|takeaway|framing|point)\b"
    r"|an?\s+(?:key\s+)?(?:contribution|diagnosis|framing)\b"
    r"|what\s+th(?:e|is)\s+paper\b)", re.I)

# The author's voice, anywhere in a claim rather than only at its front. Same rule, same
# reason: the claim is retrieved with no byline attached to it. `us` is deliberately not
# in here: case-insensitively it matches the "US" of "US Law" and "the US concentration",
# and a claim that says "us" without also saying "we" or "our" does not occur.
_FIRST_PERSON = re.compile(r"\b(?:we|our)\b", re.I)

# A `result` claim that describes how a component is built instead of asserting what was
# found. "Q² works in three steps: mark every named entity..." is true, is in the paper,
# and answers no question a reader arrives with -- it is a method section compressed, and
# retrieved on its own it gives a summariser machinery to paraphrase and nothing to quote.
#
# Deliberately a small allowlist of construction frames rather than the absence of a
# finding, because the absence test cannot be made to work: measured over every sidecar
# and draft, "no figure and no comparative word" flags 12 claims of which 5 are findings
# (a proved consistency theorem, "expert labelers named source reliability first"). The
# frames below flag 8 and all 8 are descriptions. The cost is recall, and the loss is
# knowable: a description carrying a contrast escapes, because "rather than" trips
# `_ASSERTS`. So this catches the clear cases and rule 2 of `docs/SIDECAR.md` carries the
# rest -- which is the right split, since the judgement is what a reader wanted to know
# and no regex holds that.
_DESCRIBES = re.compile(
    r"\bworks? by\b|\bin (?:two|three|four|five|2|3|4|5) steps\b|\bconsists? of\b"
    r"|\b(?:is|are) (?:implemented|distributed as|formatted|computed|defined|structured"
    r"|clustered|factorised|factorized|thresholded|encoded|represented|parameterised"
    r"|parameterized|fed)\b"
    r"|\bshares? all parameters\b|\btrains? (?:a|an|the|one|two)\b|\bemits?\b"
    r"|\bare determined by\b|\bby modell?ing\b|\bproceeds\b|\bpasses?\b.*\bthrough\b", re.I)

# ...unless the same sentence also does a claim's job. A magnitude is not enough on its
# own -- a dimension count sits happily inside a description -- so what counts is the
# vocabulary of a result: a comparison, an outcome verb, or a negation.
_ASSERTS = re.compile(
    r"\b(?:better|worse|best|worst|higher|lower|faster|slower|stronger|weaker|than|beats?"
    r"|outperform\w*|improv\w+|degrad\w+|gain\w*|drops?|dropped|fail\w*|reach\w+|matched"
    r"|exceed\w*|proved|proves|shows?|showed|found|find|no|not|never|only|enough"
    r"|suffice\w*)\b", re.I)

# A definition or a correction that points at the page around it. Terminology is
# published as a schema.org `DefinedTerm` inside a `DefinedTermSet`, so the definition
# travels with nothing but the term beside it: "the metric for every merging table here"
# then defines nothing. A misreading renders as a bare list item and an llms.txt bullet,
# with the same consequence. 30% of drafted definitions and 15% of misreadings dangle.
#
# The two patterns differ on purpose. A definition has no business naming the paper at
# all -- the enclosing set is already titled "Terminology in <paper title>", so
# "This paper's shorthand for..." is both dangling and redundant. A misreading legitimately
# says what the paper does and does not state ("the paper does not say whether human
# matches were used"), so only the words with no possible referent are barred there.
_DEIXIS_TERM = re.compile(
    r"\bhere\b|\b(?:we|our)\b|\bth(?:is|e)\s+(?:paper|work|study)(?:'s)?\b"
    r"|\bthe\s+authors?\b", re.I)
_DEIXIS_MISREADING = re.compile(r"\bhere\b|\b(?:we|our)\b", re.I)


# A period that ends one of these ends a word, not a sentence. Initials are handled by
# shape (`H.` in "H. Natarajan") rather than listed, since the set of names is open.
# How a sentence may start: an optional quote or bracket, then a letter or a digit. A
# lowercase opener is deliberate -- "t-SNE plots show..." and "pyFranc is trained on..."
# are sentences, and requiring a capital swallowed them into the sentence before.
_OPENS = re.compile(r'["\'(\[]*[A-Za-z0-9]')

# Words that open a sentence and cannot be a surname. The initials rule below joins
# "H." to "Natarajan" so a person's initial does not end a sentence, and it read the
# matrix in "freezing B and tuning A. The guarantee holds..." the same way -- gluing two
# sentences into one and reporting the pair as a 36-word sentence that does not exist.
_OPENER = re.compile(r"(?:The|This|These|That|Those|It|Its|They|We|There|An?|And|But|In|"
                     r"On|For|At|By|With|When|Where|While|Both|All|Each|No|Not|Such)\b")

_ABBREV = ("et al.", "e.g.", "i.e.", "cf.", "vs.", "approx.", "ca.", "resp.", "Fig.",
           "Tab.", "Eq.", "Sec.", "App.", "No.", "Dr.", "Prof.", "St.", "Mr.", "Ms.")

# Matched with a boundary in front, never with `endswith`: "fine-tuned LLMs." ends
# with "Ms." as a string, so a real sentence break was read as an honorific and the
# two sentences after it were counted as one 39-word sentence.
_ABBREV_RE = re.compile(r"(?:^|[\s(\[])(?:%s)$"
                        % "|".join(re.escape(a) for a in _ABBREV))


def sentences(s) -> list[str]:
    """A field split where a reader would pause.

    Over-splitting is not the harmless direction it looks like. The word cap it feeds is
    kinder for a wrong split, but the *sentence-count* cap is stricter -- and unfixably so:
    "Project Debater debated debate champion H. Natarajan" counted as two sentences, so a
    two-sentence claim was reported as three and no rewording short of dropping the man's
    initial could clear it. A drafting model asked to fix that spends a round and reverts.
    """
    parts = [x for x in re.split(r"(?<=[.;!?])\s+", str(s or "").strip()) if x]
    out: list[str] = []
    for part in parts:
        # What follows decides as much as what precedes. A period before something that
        # cannot open a sentence is an abbreviation the list above has not heard of:
        # "Non-term. < Dep. < SRL < RC < NER < Co-ref. < SPR." is one ordering of seven
        # task names and it split into four, so a two-sentence claim was reported as five
        # with no rewording available short of renaming the tasks. Only after a period --
        # a semicolon genuinely separates the conditions a scope lists, and the scope
        # checks are built on counting them.
        after_dot = out and out[-1].endswith((".", "!", "?"))
        # A quotation mark still open carries the punctuation inside it. Papers are named
        # in a claim by their titles, and a title ending in a question mark -- "Will it
        # Merge? On The Causes of Model Mergeability" -- split in the middle of its own
        # name, which spent one of the two sentences a claim is allowed on half a title.
        in_quote = out and out[-1].count('"') % 2
        joined = out and (in_quote
                          or (after_dot and not _OPENS.match(part))
                          or _ABBREV_RE.search(out[-1])
                          or (re.search(r"(?:^|[\s(\[])[A-Z]\.$", out[-1])
                              and not _OPENER.match(part)))
        if joined:
            out[-1] = f"{out[-1]} {part}"
        else:
            out.append(part)
    return out


def readability(fm: dict, slug: str | None = None) -> list[tuple[str, str, str]]:
    """Every readability finding on one sidecar, as (kind, locus, message).

    `kind` says which field the finding is about -- `claim`, `question`, `term`,
    `misreading` or `page` -- and `locus` is the thing's own handle: a claim's `id`, a
    question's or misreading's text, a term's name, and the empty string for a
    page-level finding that belongs to no single field. A caller can therefore put each
    finding next to what it is about. `check_readability` flattens the same list for a
    terminal and `draft_sidecars.checked` buckets it for the review page -- one check,
    two renderings, which is the only arrangement where the page and the command cannot
    disagree.
    """
    out = []
    for c in (fm.get("claims") or []):
        if not isinstance(c, dict):
            continue
        at = ("claim", str(c.get("id") or "?"))
        text = str(c.get("text") or "").strip()
        ss = sentences(text)
        if len(ss) > CLAIM_SENTENCES:
            out.append((*at, f"text is {len(ss)} sentences (max {CLAIM_SENTENCES}) -- "
                            "a third sentence is a second claim"))
        for s in ss:
            n = len(s.split())
            if n > CLAIM_SENTENCE_WORDS:
                out.append((*at, f"a {n}-word sentence (max {CLAIM_SENTENCE_WORDS}) -- "
                                f"split it, the front of a claim is what gets quoted: "
                                f"“{' '.join(s.split()[:9])}...”"))
        seps = len(re.findall(r"(?: -- | [-–—] |: |; )", text))
        if seps > CLAIM_SEPARATORS:
            out.append((*at, f"{seps} stacked colons/dashes in text (max "
                            f"{CLAIM_SEPARATORS}) -- each one past the first is a "
                            "second finding that should be its own claim"))
        m = _ABOUT_PAPER.match(text) or _FIRST_PERSON.search(text)
        if m:
            out.append((*at, f"text leans on {m.group(0).strip()!r} -- a claim is "
                            "retrieved with no title and no byline beside it, so name "
                            "the object instead of the paper that reports it"))
        if (c.get("kind") or "result") == "result":
            m = _DESCRIBES.search(text)
            if m and not _ASSERTS.search(text):
                out.append((*at, f"{m.group(0).strip()!r} describes how the thing is built, "
                                "and the claim asserts no finding -- say what the reader "
                                "learns from it, and move the construction into "
                                "`terminology` or drop it"))

        scope = str(c.get("scope") or "").strip()
        conds = sentences(scope)
        if len(conds) > SCOPE_SENTENCES:
            out.append((*at, f"scope is {len(conds)} sentences (max {SCOPE_SENTENCES}) -- "
                            "the published answer is the claim then \"Holds for:\" then "
                            "all of this, so a fourth condition means the claim was "
                            "stated more broadly than it holds: narrow the claim"))
        if scope and len(scope) > len(text) and len(scope) >= SCOPE_RATIO_FLOOR:
            out.append((*at, f"scope is longer than the claim it bounds ({len(scope)} vs "
                            f"{len(text)} chars) -- that makes the published answer "
                            "mostly caveat, and the caveat is the half a summariser "
                            "drops anyway"))
        if (c.get("kind") or "result") == "result" and _NAMES_THE_ANALYSIS.match(scope):
            out.append((*at, "scope names the analysis the claim came from rather than what "
                             "bounds it -- where it lives in the paper is `evidence`'s job. "
                             "Give the conditions the measurement ran under: which models, "
                             "which datasets, which values swept"))
        if m := _SHOWS_UPSHOT.search(scope):
            tail = scope[m.start():].lstrip(",; ")
            out.append((*at, f"scope comments on what the result shows -- \u201c{tail}\u201d "
                             "is the claim again, not a condition on it. Ask what would "
                             "have to change for the claim to be false; if the rest of the "
                             "scope already says that, delete this clause"))
        for i, s in enumerate(conds):
            if not _CLASSIFIES.match(s):
                continue
            where = "opens by" if i == 0 else f"sentence {i + 1} of scope is"
            head = f"“{' '.join(s.split()[:9])}...”"
            if _PREFIX_DOUBLED.match(s):
                # Same pattern, different mistake, and they were reported as one: a scope
                # reading "Holds for the TextArena dataset, ..." is not classifying the
                # claim at all, it is repeating the two words the renderer already puts
                # in front of it. Told it classifies, a reader goes looking for a
                # judgement to delete and finds a correct condition. Two of the three
                # open-weight models drafted every scope this way -- the rule states
                # where the field is published and they read that as text to include.
                out.append((*at, f"scope {where} repeating the \"Holds for:\" prefix the "
                                 "page adds -- delete those words and start at the "
                                 f"condition: {head}"))
            else:
                out.append((*at, f"scope {where} classifying the claim, and scope is "
                                 'published after the words "Holds for:" -- give the '
                                 f"condition instead: {head}"))

    # One scope reused word for word across claims, which means it is not a scope: the
    # field bounds *this* finding, and a bound that is true of every claim on the page is
    # the paper's setting, which the page states once already. Cheap to check and it was
    # never going to fire on a careful draft -- zero repeats across all 20 live sidecars
    # and drafts. It fires on the thing that produces it: a model rewriting scopes to
    # satisfy a finding lands on one phrasing that clears the check and pastes it
    # everywhere, so this is the check that catches a fix from being cosmetic.
    seen: dict = {}
    for c in (fm.get("claims") or []):
        if isinstance(c, dict) and (sc := re.sub(r"\s+", " ", str(c.get("scope") or "")).strip()):
            seen.setdefault(sc.lower(), []).append(str(c.get("id")))
    for sc, who in seen.items():
        if len(who) > 1:
            out.append(("page", "", f"{len(who)} claims share one scope verbatim "
                        f"({', '.join(who)}) -- a condition true of every claim is the "
                        f"paper's setting, not this claim's bound: “{sc[:60]}...”"))

    # A claim that enumerates. One of 343 claims in the corpus does this -- the pure-Qwen
    # KnOTS draft's context claim, "The key contributions are: (1) a method to align task
    # updates ... and (2) a new benchmark for measuring generality" -- and it is the
    # abstract's contributions bullet pasted into a field that publishes one assertion.
    # Two claims wearing one id: retrieved alone it answers neither question well, and the
    # sentence-count rule misses it because the enumeration is a single sentence. Rare
    # enough to be worth a check only because the check costs two lines and the signal has
    # no legitimate case -- a numbered list is never the shortest way to say one thing.
    for c in (fm.get("claims") or []):
        if isinstance(c, dict) and (m := _ENUMERATES.search(str(c.get("text") or ""))):
            out.append(("claim", str(c.get("id") or "?"),
                        f"text enumerates ({m.group(1).strip()} ... {m.group(2).strip()}) "
                        "-- that is two claims sharing one id, and each is retrieved alone. "
                        "Split it, and give each half its own scope and evidence"))

    # The one-liner repeating a claim. Also one case, also the pure-Qwen draft, where
    # `one_liner` and the first claim were the same 126 characters. Both are published --
    # the one-liner as the page's description, the claim in the claim list and in an
    # `acceptedAnswer` -- so the page states one sentence three times, and the duplicate
    # spends one of the 5-15 claim slots saying nothing new. The threshold is high on
    # purpose: a one-liner sharing a claim's subject and verb is expected, and only
    # near-identity is the defect.
    ol = " ".join(_words(fm.get("one_liner")))
    for c in (fm.get("claims") or []):
        if not isinstance(c, dict) or not ol:
            continue
        same = difflib.SequenceMatcher(None, ol, " ".join(_words(c.get("text")))).ratio()
        if same > _SAME_TEXT:
            out.append(("page", "", f"`one_liner` is claim {c.get('id')!r} again, and both "
                        "are published -- the one-liner as the page's description and the "
                        "claim in its own list. Say the paper's point in the one-liner and "
                        "let the claim carry the measurement, or drop the claim and spend "
                        "the slot on one the page does not have"))

    # Page-level, so it has no single locus. Counted over `result` claims only: a
    # `context` claim asserts where the work sits and usually has no number to carry.
    res = [c for c in (fm.get("claims") or [])
           if isinstance(c, dict) and (c.get("kind") or "result") == "result"]
    withnum = [c for c in res if quotable(c.get("text"))]
    if res and len(withnum) < RESULT_FIGURES * len(res) and paper_reports_figures(slug):
        # Names the claims, because a page-level finding with no locus is a finding the
        # repair round cannot act on: the model was told half its claims want a magnitude
        # and had to guess which half, so it changed none of them. The ids are the whole
        # difference between "raise your coverage" and "these seven claims dropped a number".
        bare = ", ".join(str(c.get("id")) for c in res if not quotable(c.get("text")))
        out.append(("page", "", f"only {len(withnum)} of {len(res)} result claims state a "
                    f"figure (want {RESULT_FIGURES:.0%}) -- go back to the tables for the "
                    "magnitudes these claims dropped, or fold two number-free claims into "
                    f"the measured claim they are both circling. Never invent one. "
                    f"Number-free: {bare}"))

    # `or {}` covers a missing field but not a wrong-typed one, and a model that hands back
    # `terminology` as a string -- one live draft came back with the whole mapping flattened
    # into `{"term", "definition", "term", ...}` -- made this line raise AttributeError.
    # A check that raises tells the reader nothing, and it took the review page down with
    # it. The wrong type is already reported by `check_sidecar_shape`, so there is nothing
    # to add here beyond not crashing.
    terms = fm.get("terminology")
    for term, definition in (terms.items() if isinstance(terms, dict) else ()):
        m = _DEIXIS_TERM.search(str(definition))
        if m:
            out.append(("term", str(term), f"definition says {m.group(0).strip()!r} -- it is "
                        "published as a DefinedTerm with nothing but the term beside it, so "
                        "define what the word means, not its role on this page"))

    for mis in (fm.get("misreadings") or []):
        m = _DEIXIS_MISREADING.search(str(mis))
        if m:
            out.append(("misreading", str(mis), f"{m.group(0).strip()!r} has nothing to point "
                        "at once this bullet is extracted on its own -- name the thing"))

    for g in (fm.get("qa") or []):
        if not isinstance(g, dict):
            continue
        for q in phrasings(g):
            # The bare-definite rule yields to a question that names something, which
            # the demonstrative rules must not: "does this method beat MMLU baselines"
            # names a benchmark and is still unanswerable about *which* method.
            m = _UNBOUND.search(str(q)) or (
                None if _NAMES_SOMETHING.search(str(q)) else _BARE_DEFINITE.search(str(q)))
            if m:
                out.append(("question", str(q), f"{m.group(0).strip()!r} has no antecedent in the "
                                    "question, so it matches no query and cannot be "
                                    "quoted alone -- name the subject"))
    return out


def check_readability(entries: list[tuple[str, dict]]) -> list[str]:
    """Claims a reader has to re-read, and passages that say nothing once extracted.

    Kept out of `validate.py`'s own run on purpose -- see the tier note above.
    """
    def line(name, kind, at, msg):
        if kind == "page":
            return f"{name}: {msg}"
        if kind in ("question", "misreading"):
            return f"{name}: {at} -- {msg}"
        return f"{name}: {kind} {at!r}: {msg}"

    return [line(name, kind, at, msg)
            for name, fm in entries
            for kind, at, msg in readability(fm, slug_of(name))]


def outdated_live(entries: list[tuple[str, dict]]) -> dict[str, int]:
    """Live sidecars today's accept-time checks would refuse: slug -> finding count.

    The accept tier is fatal at `--accept` and never consulted again, which is right for
    a draft and leaves a hole behind a published one. A sidecar accepted before a rule
    existed keeps its old shape for good, and it is the shape the site publishes: both
    live files predate the scope rules, and between them every one of their 30 scopes is
    longer than the claim it bounds -- the one thing the `FAQPage` answer is built out of.

    Reported and re-queued, not made fatal. The remedy is a re-draft and an accept, and a
    gate that fails until those happen blocks every unrelated commit; `pending()` reads
    this instead, so the papers come back round as drafts on their own.
    """
    return {slug_of(name): n
            for name, fm in entries if (n := len(readability(fm, slug_of(name))))}


# --------------------------------------------------------------- accept-time tier

_GROUPED = r"\d{1,3}(?:,\d{3})+"
_PLAIN = r"\d+(?:\.\d+)?"
# A figure as an author writes one. The grouped form comes first so `1,600` is one
# figure rather than the pair (1, 600), and the two lookbehinds drop digits that belong
# to a name rather than to a measurement: `T5` glues to a letter, and `ViT-L/14`,
# `Llama3-8B` and `top-5` glue on through a hyphen or slash. Those are things the paper
# refers to, not quantities it reports, and checking them fills the review with lines
# whose answer is always yes.
_FIGURE = re.compile(rf"(?<![A-Za-z0-9.])(?<![A-Za-z0-9][-/])({_GROUPED}|{_PLAIN})")


def canon(tok: str) -> str:
    """One figure, one spelling: 1,600 is 1600, and 4.60 is 4.6."""
    tok = tok.replace(",", "")
    return tok.rstrip("0").rstrip(".") or "0" if "." in tok else tok


def figures(s: str) -> list[str]:
    """The figures a claim states, canonicalised, in order and without repeats.

    Bare single digits are dropped, and dropping them costs nothing: every paper's own
    text contains each of them (its section headings alone guarantee it), so such a
    figure can never fail the check. Keeping them only fills the review with lines whose
    answer is already known -- and leaving the blindness undocumented is worse than
    saying here that a claim's `n LoRA models` and its `by 7 points` are both unchecked.
    """
    return list(dict.fromkeys(canon(t) for t in _FIGURE.findall(str(s))
                              if not (len(t) == 1 and t.isdigit())))


def quotable(s: str) -> list[str]:
    """The figures a claim states, counting the bare single digits `figures` drops.

    Two questions, two answers. `figures` feeds `check_claim_numbers`, which asks whether
    a figure can be checked against the paper, and a bare digit cannot be -- every paper's
    own text contains all ten. Coverage asks something else: whether the claim carries a
    magnitude a reader would quote rather than paraphrase. `4 families`, `7
    embedding-based routers` and `9 modal verbs` are exactly that, and on a survey or an
    annotation-scheme paper they are the only kind of magnitude there is. One shared
    definition reported 0 of 9 result claims on two pages whose every claim states a count.
    """
    return list(dict.fromkeys(canon(t) for t in _FIGURE.findall(str(s))))


def slug_of(name: str) -> str:
    """A sidecar's slug from its filename, which is how the fulltext cache is keyed."""
    return name[:-3] if name.endswith(".md") else name


def paper_reports_figures(slug: str | None) -> bool:
    """Whether the paper reports enough figures for coverage to be a fair ask of it."""
    if not slug:
        return True
    path = os.path.join(ROOT, "build", "fulltext", f"{slug}.txt")
    if not os.path.exists(path):
        # No text to judge by. The checks that need the fulltext already say so, and
        # guessing here would either excuse every page or flag every page.
        return True
    have = {f for f in figures_in(open(path).read())
            if len(f) > 1 and not re.fullmatch(r"(?:19|20)\d\d", f)}
    return len(have) >= PAPER_FIGURES_FLOOR


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
            # Some extractors break the heading across lines -- `1\n\nIntroduction` --
            # which the same-line form above cannot see, and every "Section N" pointer
            # in such a paper then reads as a citation to a section that does not
            # exist. The title's capital is what separates a heading from a table cell:
            # `1` above `0.42` is data, `1` above `Introduction` is a section.
            pat += rf"|^[ \t]*{re.escape(num)}[ \t]*\n+[ \t]*[A-Z]"
        out.append((f"{kind} {num}", re.compile(pat, re.I | re.M)))
    return out


# A line-number gutter, as a PDF extractor hands it over: the numbers a review-copy
# template prints down the margin arrive inline, as one long ascending run. Consecutive
# and ascending is the whole test, because that is what a gutter is and what a table of
# measurements never is -- a table of integer counts survives, so the check keeps erring
# toward accepting a real figure.
_INT_RUN = re.compile(r"(?<![\w.])\d{1,4}(?:\s+\d{1,4}){4,}(?![\w.])")
_GUTTER_RUN = 5


# LaTeX's own thousands separators, as the extractor hands them over: `25{,}000`, and the
# spacing macros `\,` and `\;` used the same way. Nine of the cached papers write their
# numbers like this, and until they were folded down a claim's 25,000 was reported as "not in
# the paper" about a paper that states it twice -- a false positive on the one rule with no
# exceptions, which is the rule that can least afford them.
_TEX_THOUSANDS = re.compile(r"(?<=\d)(?:\{,\}|\\[,;:]|\\ )(?=\d{3}\b)")


def deline(text: str) -> str:
    """The paper's text with line-number gutters dropped and its numbers written plainly.

    A gutter verifies almost any small integer -- `1 2 3 ... 36` contains 22, 30 and 36 --
    so leaving it in makes `check_claim_numbers` pass a figure the paper never states,
    and makes the review quote the gutter instead of the sentence. Both failures are
    silent, which is why this runs on the text rather than on the finding.
    """
    text = _TEX_THOUSANDS.sub(",", text)
    def keep(m: re.Match) -> str:
        toks, out, run = m.group(0).split(), [], []
        for t in toks + ["x"]:
            if run and t.isdigit() and int(t) == int(run[-1]) + 1:
                run.append(t)
                continue
            if len(run) < _GUTTER_RUN:
                out += run
            run = [t] if t.isdigit() else []
        return " " + " ".join(out) + " "
    return _INT_RUN.sub(keep, text)


def figures_in(text: str) -> set[str]:
    r"""Every reading of every number in the paper's own text.

    Both readings, because a comma between digits is ambiguous and nothing local
    resolves it: `1,600` is one number, while the LaTeX set `\{200,400,800,1600\}` --
    which is what the extractor actually hands us -- is four. Indexing both makes the
    check ask whether a figure is in the paper under *any* reading, which errs toward
    accepting. That is the right direction here: a false positive spends the author's
    attention on a correct number, and enough of those get the whole check ignored.
    """
    return ({canon(t) for t in re.findall(_PLAIN, text)}
            | {canon(t) for t in re.findall(_GROUPED, text)}
            # Result tables conventionally drop the leading zero on a correlation, so
            # `.435` in the paper and `0.435` in the claim are the same figure.
            | {canon("0" + t) for t in re.findall(r"(?<![\d.])\.\d+", text)})


def values_in(text: str) -> list[float]:
    """The same numbers as floats, for the rounding tolerance below."""
    out = []
    for t in re.findall(_PLAIN, text) + re.findall(r"(?<![\d.])\.\d+", text):
        try:
            out.append(float(t))
        except ValueError:
            pass
    return out


def rounds_to(target: str, values: list[float]) -> bool:
    """Whether some figure in the paper rounds to the one the claim states.

    A claim says `74.5` where Table 5 says `74.46`. That is the same number written for
    a sentence instead of a table, and refusing it would make the check fire on almost
    every honest claim -- the drafts round routinely, and correctly. Rounding to the
    claim's own stated precision is the whole tolerance: `74.9` does not round to
    `74.5`, and neither does a figure the drafter computed rather than read.

    A figure declares its own precision, so trailing zeros count as a claim of
    approximation in the other direction: `14,000` matches the paper's `14,042`. Only
    from the hundreds up, because `10` almost always means ten and not twelve.
    """
    try:
        want = float(target)
    except ValueError:
        return False
    if "." in target:
        dp = len(target.split(".")[1])
    else:
        zeros = len(target) - len(target.rstrip("0"))
        dp = -zeros if zeros >= 2 else 0
    return any(abs(round(v, dp) - want) < 1e-9 for v in values)


def check_claim_numbers(entries: list[tuple[str, dict]]) -> tuple[list[str], list[str]]:
    """Every figure in a claim must appear in the paper's own text.

    The one rule in docs/SIDECAR.md with no exceptions, and the only one that needs an
    artifact outside the repo: `build/fulltext/<slug>.txt`, which is gitignored and may
    simply be absent. A missing cache is returned separately rather than passed as a
    check, because silently skipping is how a rule stops being a rule -- the caller
    says so out loud.

    Years are exempt. A date is a fact about the world that a reader can check
    elsewhere, and a paper's body text often never states its own year.
    """
    errs, skipped = [], []
    for name, fm in entries:
        path = os.path.join(ROOT, "build", "fulltext", f"{name[:-3]}.txt")
        if not os.path.exists(path):
            skipped.append(name)
            continue
        with open(path, errors="replace") as fh:
            text = deline(fh.read())
        have, vals = figures_in(text), values_in(text)
        for c in (fm.get("claims") or []):
            if not isinstance(c, dict):
                continue
            # Both fields at once, reported once: `text` and `scope` usually carry the
            # same figure, and saying so twice makes one mistake look like two.
            stated = figures(f"{c.get('text') or ''} {c.get('scope') or ''}")
            missing = [n for n in stated
                       if n not in have
                       and not (n.isdigit() and 1900 <= int(n) <= 2099)
                       and not rounds_to(n, vals)]
            if missing:
                errs.append(
                    f"{name}: claim {c.get('id', '?')!r} states "
                    f"{', '.join(missing)}, which {'is' if len(missing) == 1 else 'are'}"
                    " not in the paper's own text -- correct it or drop the figure")
    return errs, skipped


def check_claim_evidence(entries: list[tuple[str, dict]]) -> tuple[list[str], list[str]]:
    """Every `Table 2` / `Section 6.2` a claim cites must be a part the paper has.

    The same class of error as a wrong figure, and treated the same way: `evidence` is
    what makes a claim checkable, so a pointer into a section that does not exist is
    worse than no pointer at all -- it sends the one reader who verifies to the wrong
    place and reads, to everyone else, as diligence. A real one caught it on the first
    run: a Limitations claim cited "Section 7" of a paper whose last section is 6.

    Only the pointer's existence is checked, never that the part supports the claim.
    That needs a reader, and this check does not pretend otherwise.
    """
    errs, skipped = [], []
    for name, fm in entries:
        path = os.path.join(ROOT, "build", "fulltext", f"{name[:-3]}.txt")
        if not os.path.exists(path):
            skipped.append(name)
            continue
        with open(path, errors="replace") as fh:
            text = deline(fh.read())
        for c in (fm.get("claims") or []):
            if not isinstance(c, dict):
                continue
            gone = [label for label, pat in evidence_pointers(c.get("evidence") or "")
                    if not pat.search(text)]
            if gone:
                errs.append(
                    f"{name}: claim {c.get('id', '?')!r} cites {', '.join(gone)}, which "
                    f"the paper never mentions -- correct the pointer or drop it")
    return errs, skipped


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
    ("SKILL.md", "{papers} papers and {repos} repos", ""),
    ("SKILL.md", "Only 1 of {repos} repos maps", ""),
    ("docs/RULES.md", "1 of {repos} repos maps to a paper", ""),
    ("docs/EVIDENCE.md", "unanswerable at {papers} papers", ""),
    ("docs/EVIDENCE.md", "~{papers} papers × 6 questions", "recompute the question total"),
    ("docs/EVIDENCE.md", "~{papers} papers × ~4 months", "recompute the paper-months"),
    ("docs/EVIDENCE.md", "sidecars for {papers} papers", "recompute the hours"),
    ("RUN.md", "{unlabelled} of {repos} repos", ""),
)

# Docs a model is actually sent, and the section of each that it is sent. See
# common.rules_block: the doc is the only copy of those rules, so deleting a marker
# would silently produce a prompt with no rules in it.
PROMPT_DOCS = (
    ("docs/SIDECAR.md", "§2, the sidecar drafting rules", "scripts/draft_sidecars.py"),
    ("docs/RULES.md", "§11.2, the repo labelling rules", "scripts/propose_topics.py"),
)


def check_prompt_blocks() -> list[str]:
    """Fail the run, not the next draft, if a prompt block went missing.

    `rules_block` already raises when a marker is gone, but it raises at drafting time
    -- which in `skill` mode is a session that has already started. This is the same
    check one layer earlier, so a doc edit that breaks a prompt is caught by the
    validate step of the run that made it.
    """
    errs = []
    for doc, what, reader in PROMPT_DOCS:
        try:
            rules_block(doc)
        except RuntimeError as e:
            errs.append(f"{e} ({what}; read by {reader})")
    return errs


def count_pattern(template: str) -> re.Pattern:
    """The same sentence with any number in the count's place.

    Built from the template rather than written twice, so the pattern cannot drift
    from the string the check looks for.
    """
    parts = re.split(r"(\{papers\}|\{repos\}|\{unlabelled\})", template)
    return re.compile("".join(r"\d+" if p.startswith("{") else re.escape(p)
                              for p in parts))


def check_doc_counts(papers: list[dict], repos: list[dict], fix: bool = False) -> list[str]:
    """Catch a doc that still states an old corpus size. See DOC_COUNTS.

    With `fix`, rewrites the number in place for the lines that carry nothing but the
    count -- a new paper is a fact about the corpus, and retyping it in seven files is
    the kind of chore that gets skipped until the docs are wrong. The lines marked with
    a note are left as errors on purpose: their number feeds an arithmetic result on the
    same line, so substituting it without redoing the sum is how a page becomes
    confidently wrong.
    """
    # `unlabelled` is how many repos carry labels nobody has read. RUN.md §11 argues from
    # that number -- publishing unreviewed model text is worth it *because* the alternative
    # leaves this many repos bare -- so the argument stops holding the day it drifts.
    counts = {"papers": len(papers), "repos": len(repos),
              "unlabelled": sum(1 for r in repos
                                if not r.get("reviewed") and not r.get("skip"))}
    if not counts["papers"] or not counts["repos"]:
        return []            # a failed read is already reported by the schema pass
    errs = []
    for fname, template, note in DOC_COUNTS:
        path = os.path.join(ROOT, fname)
        if not os.path.exists(path):
            # Not skipped: a missing target means this row silently stopped checking
            # anything, which is how a renamed doc keeps a stale number forever.
            errs.append(f"{fname}: DOC_COUNTS names a file that does not exist. "
                        f"Point the row at the file the sentence moved to, or drop it "
                        f"(scripts/validate.py DOC_COUNTS)")
            continue
        want = template.format(**counts)
        text = open(path).read()
        if want in text:
            continue
        if fix and not note:
            fixed, n = count_pattern(template).subn(want, text)
            if n:
                with open(path, "w") as f:
                    f.write(fixed)
                print(f"  {fname}: updated {n} sentence"
                      f"{'s' * (n != 1)} to {want!r}")
                continue
        tail = f"; {note}" if note else ""
        errs.append(f"{fname}: stale corpus size -- expected {want!r}. Update the "
                    f"sentence (or DOC_COUNTS in scripts/validate.py){tail}")
    return errs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true",
                    help="exit non-zero on any problem (use in CI)")
    ap.add_argument("--fix-counts", action="store_true",
                    help="rewrite the corpus sizes stated in the docs (not the "
                         "lines whose number feeds a sum -- those stay errors)")
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
    sidecars, unparseable = read_sidecars()
    errs += unparseable + check_sidecars(sidecars)
    errs += check_overrides()
    errs += check_slug_history()
    errs += check_wikidata_created()
    errs += check_name_lists()
    errs += check_affiliations()
    errs += check_prompt_blocks()
    # Kept separate from the rest: a stale number in a sentence and a sidecar outside the
    # bands are the two problem classes that do not mean something is broken. See the
    # module docstring.
    soft = check_doc_counts((docs.get("papers") or {}).get("papers", []),
                            (docs.get("repos") or {}).get("repos", []),
                            fix=args.fix_counts)
    soft += check_sidecar_shape(sidecars)
    number_errs, no_text = check_claim_numbers(sidecars)
    soft += number_errs
    soft += check_claim_evidence(sidecars)[0]

    if not have_js:
        print("note: jsonschema not installed -- using the built-in subset of checks")
    if no_text:
        # Said out loud every run: this is the one rule with no exceptions, and it is
        # also the only one that can quietly stop running because a build artifact is
        # missing. `python scripts/fulltext.py` restores it.
        print(f"note: no cached full text for {len(no_text)} of {len(sidecars)} "
              f"sidecars, so their numbers were not checked "
              f"({', '.join(n[:-3] for n in no_text[:3])}"
              f"{', ...' if len(no_text) > 3 else ''})")
    if old := outdated_live(sidecars):
        # Every run, next to the other note: this is drift in what is already published,
        # so it should not need someone to go looking for it.
        print(f"note: {len(old)} of {len(sidecars)} live sidecar(s) carry "
              f"{sum(old.values())} finding(s) against accept-time rules written after "
              f"they were accepted, so a re-draft is queued for them "
              f"({', '.join(f'{k} ({v})' for k, v in sorted(old.items()))})")
    problems = errs + soft
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for e in problems[:60]:
            print(f"  {e}")
        if len(problems) > 60:
            print(f"  ... and {len(problems) - 60} more")
        sys.exit(1 if (errs or args.strict) else 0)
    print("data files valid")


if __name__ == "__main__":
    main()
