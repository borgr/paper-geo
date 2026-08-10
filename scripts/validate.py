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
from common import DATA, ROOT, load_config, norm_name, read_yaml, rules_block  # noqa: E402

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
            for a in (qa.get("answers") or []):
                if a not in ids:
                    errs.append(f"{name}: qa[{i}] answers unknown claim id {a!r}")
            if not (qa.get("q") or []):
                errs.append(f"{name}: qa[{i}] has no question phrasings")
    return errs


# ------------------------------------------------------------------- shape tier
#
# The bands in docs/SIDECAR.md §2 rule 9, which JSON Schema cannot express: they are
# about how many of a thing there are and how they relate to each other, not about
# types. Non-fatal on purpose -- a page with 22 claims renders correctly and is merely
# worse, and the 19 existing drafts predate the bands. `--accept` is where it bites.
#
# Two kinds of number live here. `CLAIMS` and `PHRASINGS` are design decisions from §2,
# and the current drafts are meant to violate them: a paper has a handful of findings, so
# 17 claims is one finding split three ways and the fix is redrafting, not a wider band.
# The length and count caps are the opposite -- each is the 90th percentile of what the
# 317 already-drafted claims do, because a cap set through the middle of honest practice
# is one the author learns to ignore, and then the bands stop being read at all.

CLAIMS = (5, 15)
CLAIM_TEXT = (60, 450)
CLAIM_SCOPE = (80, 800)
# Deliberately generous: a question group is query surface, and more real phrasings of a
# real question is the whole point. The ceiling only catches a run of invented questions.
QA_GROUPS = (4, 20)
PHRASINGS = (2, 4)
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
        if qa and not lo <= len(qa) <= hi:
            bad(f"{len(qa)} qa groups, outside the {lo}-{hi} band")
        lo, hi = PHRASINGS
        for i, g in enumerate(qa):
            n = len(g.get("q") or [])
            if n and not lo <= n <= hi:
                bad(f"qa[{i}]: {n} phrasings, outside {lo}-{hi}")

        # Coverage. A claim nothing points at renders with no route to it, and a general
        # question with no `context` claim to answer it cannot be asked at all.
        ctx_ids = {c.get("id") for c, k in zip(claims, kinds) if k == "context"}
        answered = {a for g in qa for a in (g.get("answers") or [])}
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
                qs = g.get("q") or []
                if qs and all(says(q, forms) for q in qs):
                    bad(f"qa[{i}]: every phrasing contains {fm['coined']!r} -- at "
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
        text = open(path, errors="replace").read()
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
