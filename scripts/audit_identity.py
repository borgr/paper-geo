#!/usr/bin/env python3
"""Audit the identity surfaces you do not control, against what they should say.

Everything else in this repo checks *our* artifacts. This checks the five external
surfaces that decide whether a retrieval system can resolve you to one person, by
reading their public APIs -- no login, no key, read-only:

    ORCID          public works count, researcher URLs, name variants, keywords
    arXiv          which papers your account is actually registered as author on
    Wikidata       whether an author item carrying your ORCID exists yet
    Hugging Face   which paper pages exist, and which you have claimed
    Semantic Sch.  how the corpus is split across author records
    arXiv metadata whether its author list spells your name right at all

The arXiv check is the one worth the network round-trip. Linking ORCID to arXiv
gives you a public list at arxiv.org/a/<orcid> built from arXiv's *authority
records* -- papers your account is registered as an author on. For a co-authored
corpus that is usually a fraction of your papers, and it is also the gate on
editing them: you cannot add a journal-ref to a paper you do not own. So this
diff is a prerequisite list, not a vanity metric.

Writes tasks/identity_audit.md, tasks/arxiv_ownership.md, tasks/hf_worklist.md and
tasks/arxiv_name_fixes.md.

Usage:
    python scripts/audit_identity.py               # everything (~60s, HF dominates)
    python scripts/audit_identity.py --no-hf       # skip the per-paper HF checks
    python scripts/audit_identity.py --no-names    # skip the arXiv author-name check
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (BUILD, DATA, ROOT, WD_IDENTIFIERS, get, get_json,  # noqa: E402
                    load_config, name_match, norm_name, read_yaml)

TASKS = os.path.join(ROOT, "tasks")
ATOM = {"a": "http://www.w3.org/2005/Atom"}
_ABS = re.compile(r"abs/([0-9]{4}\.[0-9]{4,5}|[a-z\-]+/[0-9]{7})")


def orcid_public(orcid: str) -> dict:
    """Read the public ORCID record.

    The public API is what Semantic Scholar, OpenAlex and Crossref see. An item
    whose visibility is "trusted parties" is invisible here -- so a works count of
    0 does not distinguish "empty" from "private", and both fail identically.
    """
    d = get_json(f"https://pub.orcid.org/v3.0/{orcid}/record") or {}
    act, person = d.get("activities-summary") or {}, d.get("person") or {}
    urls = [(u.get("url-name"), (u.get("url") or {}).get("value"))
            for u in ((person.get("researcher-urls") or {}).get("researcher-url") or [])]
    return {
        "works": len((act.get("works") or {}).get("group") or []),
        "employments": len((act.get("employments") or {}).get("affiliation-group") or []),
        "educations": len((act.get("educations") or {}).get("affiliation-group") or []),
        "urls": urls,
        "other_names": [n.get("content") for n in
                        ((person.get("other-names") or {}).get("other-name") or [])],
        "keywords": [k.get("content") for k in
                     ((person.get("keywords") or {}).get("keyword") or [])],
        "biography": bool(person.get("biography")),
        "reachable": bool(d),
    }


def arxiv_registered(orcid: str) -> set[str] | None:
    """arXiv ids your account is registered as an author on.

    Read from the Atom flavour of arxiv.org/a/<orcid>: the HTML page 303-redirects
    and is JS-free, but the feed is the parseable one. None means the page does not
    exist yet, which happens when the ORCID is not linked to an arXiv account.
    """
    raw = get(f"https://arxiv.org/a/{orcid}.atom2", retries=2)
    if not raw:
        return None
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        # An unlinked ORCID serves the arXiv 404 page, which is HTML, not Atom.
        return None
    out = set()
    for e in root.findall("a:entry", ATOM):
        m = _ABS.search((e.findtext("a:id", "", ATOM) or ""))
        if m:
            out.add(m.group(1))
    return out


def wikidata_item(cfg) -> str | None:
    """Find an author item by any identifier we already know, not by name.

    Name search on Wikidata returns paper items that merely mention you, which is
    the failure mode that made this look done once already. Statement search is
    exact: either an item claims the identifier or none does.
    """
    ident, ids = cfg["identity"], cfg["ids"]
    probes = [("P496", ident["orcid"]), ("P4012", ids["semantic_scholar_primary"]),
              ("P1960", ids["google_scholar"]), ("P2037", ids["github"])]
    for prop, val in probes:
        q = quote(f'haswbstatement:"{prop}={val}"')
        j = get_json("https://www.wikidata.org/w/api.php?action=query&list=search"
                     f"&srsearch={q}&srlimit=5&format=json") or {}
        for hit in ((j.get("query") or {}).get("search") or []):
            return hit["title"]
    return None




def wikidata_gaps(qid: str, cfg) -> dict:
    """Diff a live Wikidata item against the identifiers config says it should carry.

    Worth checking rather than assuming, because hand-created items acquire two
    specific defects that are invisible on the page: a statement added twice (the
    editor does not warn), and an alias pasted as one string when it was meant as
    several -- markdown backticks and all, which is what happened here. Both are
    silent: the item looks complete and queries against it come back wrong.
    """
    d = get_json(f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json") or {}
    ent = ((d.get("entities") or {}).get(qid)) or {}
    if not ent:
        return {}
    vals: dict[str, list[str]] = {}
    for pid, claims in (ent.get("claims") or {}).items():
        for c in claims:
            v = ((c.get("mainsnak") or {}).get("datavalue") or {}).get("value")
            if isinstance(v, dict):
                v = v.get("id") or v.get("text") or v.get("amount") or ""
            vals.setdefault(pid, []).append(str(v))

    missing, wrong, dupes = [], [], []
    for pid, label, pick in WD_IDENTIFIERS:
        want = pick(cfg)
        if not want:
            continue
        have = vals.get(pid) or []
        if not have:
            missing.append((pid, label, want))
        elif not any(str(want).rstrip("/") == h.rstrip("/") for h in have):
            wrong.append((pid, label, want, have))
    for pid, have in vals.items():
        for v in {h for h in have if have.count(h) > 1}:
            dupes.append((pid, v, have.count(v)))

    aliases = [a.get("value", "") for a in ((ent.get("aliases") or {}).get("en") or [])]
    # An alias carrying a backtick or a comma-plus-quote came from pasting a markdown
    # table cell into the single-alias box, so several names became one string that
    # matches nothing.
    bad_aliases = [a for a in aliases if "`" in a or a.count(",") > 1]
    want_aliases = [v for v in cfg["identity"]["name_variants"]
                    if v != cfg["identity"]["name"]
                    and not any(norm_name(v) == norm_name(a) for a in aliases)]
    return {"qid": qid, "missing": missing, "wrong": wrong, "dupes": dupes,
            "aliases": aliases, "bad_aliases": bad_aliases,
            "want_aliases": want_aliases,
            "n_p856": len(vals.get("P856") or []),
            "label": (ent.get("labels") or {}).get("en", {}).get("value", ""),
            "description": (ent.get("descriptions") or {}).get("en", {}).get("value", "")}


# Hugging Face records a per-author `status` beside the linked user. These two mean
# the link is live; anything else with a user attached is a claim in flight.
HF_CLAIM_DONE = {"claimed_verified", "admin_assigned"}


def hf_state(papers, me: str, variants) -> dict[str, list]:
    """Live per-paper Hugging Face state, by what you can actually do about it.

    Five buckets, because "not claimed" was hiding three different situations and
    only one of them is a click:

        missing    no page at all -- visit it while logged in
        unclaimed  page exists, your name is in the author list, no user linked
        pending    you are linked but status is not yet verified -- wait, do not redo
        blocked    no author string resembles your name, so there is no claim control
                   to press: the upstream metadata is wrong and that is the real task
        claimed    done

    Splitting out `pending` stops the worklist from re-listing claims already in
    moderation, which reads as "your click did not work". Splitting out `blocked`
    matters more: those pages cannot be claimed at all, so leaving them among the
    clicks makes the list end in three items that never complete.

    Deliberately live rather than read from papers.yaml. This list is worked by
    hand over days, and a stale copy sends you back to pages you already did --
    which is exactly what happened the first time.
    """
    me = me.lower()
    out = {k: [] for k in ("missing", "unclaimed", "pending", "blocked", "claimed")}
    for p in papers:
        j = get_json(f"https://huggingface.co/api/papers/{p['arxiv']}", retries=1)
        if j is None:
            out["missing"].append(p)
            continue
        authors = j.get("authors") or []
        mine = [a for a in authors if (a.get("user") or {}).get("user", "").lower() == me]
        if mine:
            done = any((a.get("status") or "") in HF_CLAIM_DONE for a in mine)
            out["claimed" if done else "pending"].append(p)
        elif any(name_match(a.get("name") or "", variants) for a in authors):
            out["unclaimed"].append(p)
        else:
            p = dict(p)
            p["hf_authors"] = [a.get("name") or "" for a in authors]
            out["blocked"].append(p)
        time.sleep(0.2)
    return out


def hf_worklist_file(st: dict) -> str:
    """Every Hugging Face bucket, in full, committed so it diffs between runs.

    All buckets in one file and in full: the previous version printed a truncated
    top-12, which reads as "that is all of it".

    Only ever called with live state. Writing a cached view into the same file would
    quietly replace checked numbers with older ones, and the file gives no hint which
    it is holding.
    """
    def rows(group):
        return [f"- [ ] {p.get('citations') or 0:>4} cites — "
                f"<https://hf.co/papers/{p['arxiv']}> — "
                f"{(p.get('title_display') or p['title'])[:70]}" for p in group]

    n = {k: len(v) for k, v in st.items()}
    path = os.path.join(TASKS, "hf_worklist.md")
    L = ["# Hugging Face paper pages", "",
         "Live as of the last `python scripts/audit_identity.py` (or "
         "`hf_papers.py --live`): "
         f"**{n['claimed']} claimed**, **{n['pending']} pending**, "
         f"**{n['unclaimed']} to claim**, **{n['missing']} to index**, "
         f"**{n['blocked']} blocked upstream**.", "",
         "Indexing and claiming both need a logged-in browser. An unauthenticated visit",
         "to a paper URL returns 404 and creates nothing (verified on 50 papers — 0",
         "created), which is why this is a list and not a script.", ""]
    if n["missing"]:
        L += [f"## Index — {n['missing']} papers with no page yet", "",
              "Log in to Hugging Face, then open each link. The visit is what creates",
              "the page. Nothing else to fill in.", ""] + rows(st["missing"]) + [""]
    if n["unclaimed"]:
        L += [f"## Claim — {n['unclaimed']} pages that exist but are not linked to you", "",
              "On each page: find your name in the author list and use the claim control",
              "next to it. This is what joins the paper to your HF profile, and what",
              "makes your models and datasets cross-list on it.", ""]
        L += rows(st["unclaimed"]) + [""]
    if n["pending"]:
        L += [f"## Pending — {n['pending']} claims in moderation", "",
              "Your user is linked but the status is not verified yet. Nothing to do;",
              "listed only so a re-run does not look like the claim failed.", ""]
        L += rows(st["pending"]) + [""]
    if n["blocked"]:
        L += [f"## Blocked upstream — {n['blocked']} pages you cannot claim", "",
              "No author string on these pages resembles your name, so there is no claim",
              "control to press. Hugging Face copies its author list from arXiv, so the",
              "fix is on arXiv, not here — see `arxiv_name_fixes.md`. Once the arXiv",
              "metadata is corrected these move to the claim list on a later run.", ""]
        for p in st["blocked"]:
            L.append(f"- [ ] <https://hf.co/papers/{p['arxiv']}> — "
                     f"{(p.get('title_display') or p['title'])[:60]}")
            L.append(f"      HF lists: {', '.join(p.get('hf_authors') or [])[:150]}")
        L.append("")
    with open(path, "w") as f:
        f.write("\n".join(L) + "\n")
    return path


def wikidata_followup_file(g: dict, cfg) -> str:
    """What is left to do on an item that already exists.

    Separate from wikidata_manual.md, which is about creating one. Once the item is
    there the remaining work is different in kind -- corrections, typed identifiers,
    and linking papers to it -- and mixing the two makes the creation guide look
    unfinished forever.
    """
    ident = cfg["identity"]
    q = g["qid"]
    L = [f"# Wikidata follow-up — [{q}](https://www.wikidata.org/wiki/{q})", "",
         f"Label **{g['label']}** · description *{g['description']}*", "",
         "Live diff against `config.yaml`. Re-run `python scripts/audit_identity.py`",
         "after editing to confirm each line cleared.", ""]

    if g["bad_aliases"]:
        L += ["## Fix first: an alias was stored as one string", "",
              "Wikidata holds this as a single *also known as* value:", ""]
        # Shown in a fenced block, not backticks: the value *contains* backticks, so
        # inline code would break exactly in the paragraph explaining the breakage.
        L += ["```"] + list(g["bad_aliases"]) + ["```"]
        L += ["", "That is one alias whose text happens to contain backticks and a comma,",
              "not two aliases — so a citation reading *Choshen, Leshem* matches nothing.",
              "The aliases box takes one name per entry.", "",
              f"On <https://www.wikidata.org/wiki/{q}>: click the *also known as* area,",
              "delete that entry, then add each of these as its own alias:", ""]
        L += [f"- [ ] `{v}`" for v in ident["name_variants"] if v != ident["name"]]
        L += [""]
    elif g["want_aliases"]:
        L += ["## Aliases to add", "",
              "*Also known as* is what matches a citation that uses a different form.", ""]
        L += [f"- [ ] `{v}`" for v in g["want_aliases"]] + [""]

    if g["dupes"]:
        L += ["## Duplicate statements to remove", "",
              "The editor does not warn when the same value is added twice, and the item",
              "page renders the two identically, so this is only visible from the API.", ""]
        for pid, val, n in g["dupes"]:
            L.append(f"- [ ] `{pid}` = `{val}` appears {n}× — delete all but one "
                     f"(<https://www.wikidata.org/wiki/{q}#{pid}>)")
        L.append("")

    if g["n_p856"] > 1:
        L += ["## More than one official website", "",
              f"`P856` has {g['n_p856']} values. It should have exactly one, the canonical",
              f"URL (`{ident['canonical_url']}`). A second URL here is a second candidate",
              "homepage, which is the thing the canonical URL exists to prevent. Other",
              "pages belong in `described at URL` (P973) or in their own identifier",
              "property — see the table below.", ""]

    if g["missing"] or g["wrong"]:
        L += ["## Identifiers to add", "",
              "Each of these has a *typed* property, which is why none of them belong in",
              "`official website`. A typed identifier is format-validated, renders as a",
              "link anyway, and is traversable: Scholia, Author Disambiguator and any",
              "SPARQL query can hop from it to the record. A bare URL is none of those.",
              "", "Add with *+ Add statement* → type the property name → paste the value.",
              ""]
        for pid, label, want in g["missing"]:
            L.append(f"- [ ] **{label}** (`{pid}`) = `{want}`")
        for pid, label, want, have in g["wrong"]:
            L.append(f"- [ ] **{label}** (`{pid}`) reads `{', '.join(have)}` — "
                     f"expected `{want}`")
        L.append("")
    if not cfg["ids"].get("openreview"):
        L += ["- [ ] **OpenReview.net profile ID** (`P8964`) — fill "
              "`ids.openreview` in `config.yaml` first. Open your OpenReview profile "
              "and copy the `~Name1` from the URL; it is left blank rather than guessed "
              "because a duplicate profile would make the guess wrong, and a wrong "
              "identifier is worse than a missing one.", ""]

    L += ["## Worth adding while you are in the editor", "",
          "Not identifiers — statements that help a disambiguator separate you from a",
          "namesake, which is the whole job of this item.", "",
          "| property | | value | why |",
          "|---|---|---|---|",
          "| given name | `P735` | Leshem | lets a query match the name parts "
          "separately from the label string |",
          "| family name | `P734` | Choshen | same |",
          "| educated at | `P69` | your PhD institution | the single strongest "
          "disambiguating fact about a researcher |",
          "| employer | `P108` | with *start time* qualifiers | turns three flat "
          "affiliations into a career an engine can order |",
          "", "Skip date of birth, sex or gender, and image. None of them help retrieval",
          "and all of them are personal data you would then be maintaining.", "",
          "## Then: link your papers to the item", "",
          "This is the step that turns the item from an isolated record into something",
          "that resolves — and it is also how the account reaches the 50 edits that",
          "unlock QuickStatements, so it is not a separate chore.", "",
          "**Why it matters.** Dozens of your papers already exist as Wikidata items,",
          "imported from Crossref. They carry your name as `author name string` (P2093)",
          "— a bare text field. Nothing connects those items to you. Replacing the",
          "string with `author` (P50) pointing at " + q + " is what makes the item a hub:",
          "afterwards a single query returns your corpus, Scholia renders a profile page",
          "from it, and the papers inherit your identifiers.", "",
          "**The tool.** <https://author-disambiguator.toolforge.org>", "",
          "1. *Log in* (top right) — it edits on your behalf, so this is required, and",
          "   it is why the edits count toward your 50.",
          f"2. Paste `{q}` into **Author details / Q-number** and submit. You land on a",
          "   page listing every paper item whose `P2093` string matches your name.",
          "3. Each row has a checkbox and shows the paper title plus its other authors.",
          "   Tick the ones that are yours. **Read the co-author list rather than the",
          "   title** — a namesake shows up as a paper you do not recognise, and the",
          "   co-authors are the fastest tell.",
          "4. Press the button at the bottom to move the ticked ones from `P2093` to",
          "   `P50`. One edit per paper.",
          "5. Repeat for each name variant — the tool searches one string at a time, so",
          "   `Leshem Choshen` and `L. Choshen` are two separate passes.", "",
          "Twenty minutes gets you past 50 edits with real work rather than filler.",
          "After four days the account is autoconfirmed and `wikidata.qs` will run.", "",
          "**One caution.** Do not use the tool's *create missing author item* button",
          "while your own item exists — that is how duplicate author items appear.",
          f"Always point rows at {q}.", ""]

    path = os.path.join(TASKS, "wikidata_followup.md")
    with open(path, "w") as f:
        f.write("\n".join(L) + "\n")
    return path


def arxiv_author_strings(ids: list[str], batch: int = 50) -> dict[str, list[str]]:
    """arXiv's own author list for each id, batched.

    The API takes up to 100 ids per `id_list` query, so the whole corpus is two or
    three requests rather than one per paper -- which matters because arXiv asks for
    a 3-second gap between calls, and 105 sequential requests would be five minutes.
    """
    out: dict[str, list[str]] = {}
    for i in range(0, len(ids), batch):
        chunk = ids[i:i + batch]
        raw = get("https://export.arxiv.org/api/query?id_list="
                  f"{','.join(chunk)}&max_results={len(chunk)}", retries=3)
        if not raw:
            continue
        try:
            root = ET.fromstring(raw)
        except ET.ParseError:
            continue
        for e in root.findall("a:entry", ATOM):
            m = _ABS.search(e.findtext("a:id", "", ATOM) or "")
            if not m:
                continue
            out[m.group(1)] = [a.findtext("a:name", "", ATOM) or ""
                               for a in e.findall("a:author", ATOM)]
        time.sleep(3)
    return out


def arxiv_name_file(papers, variants) -> tuple[str, int, int]:
    """Papers whose arXiv author list misspells or omits your name.

    Worth a dedicated check because arXiv metadata is *upstream* of nearly every
    index in this repo: Hugging Face, Semantic Scholar, OpenAlex and Google Scholar
    all read it. A one-character typo there does not degrade gracefully -- it creates
    a second author who owns that paper's citations and cannot be merged with you,
    and no amount of work on the pages downstream repairs it.

    Two failure modes, different fixes, so they are reported separately:
      typo    a near-miss author string -- correct it in the arXiv metadata
      absent  no resembling string at all -- the submitter left you off the paper
    """
    found = arxiv_author_strings([p["arxiv"] for p in papers])
    typo, absent = [], []
    for p in papers:
        names = found.get(p["arxiv"])
        if not names:
            continue  # not retrievable this run; silence beats a false accusation
        kinds = {name_match(n, variants): n for n in names}
        if "exact" in kinds:
            continue
        p = dict(p)
        p["arxiv_authors"] = names
        if "near" in kinds:
            p["near_miss"] = kinds["near"]
            typo.append(p)
        else:
            absent.append(p)

    path = os.path.join(TASKS, "arxiv_name_fixes.md")
    L = ["# arXiv author-name problems", "",
         f"Checked **{len(found)}** arXiv records against your name variants: "
         f"**{len(typo)} misspelled**, **{len(absent)} missing you entirely**.", "",
         "This is upstream of everything else. Hugging Face, Semantic Scholar, OpenAlex",
         "and Google Scholar all build author identity from arXiv metadata, so a name",
         "that is wrong here is wrong in all of them at once — and it does not read as a",
         "typo to them, it reads as a different person, who then owns that paper's",
         "citations and cannot be merged into you.", ""]
    if typo:
        L += [f"## Misspelled — {len(typo)}", "",
              "Fix the author list in the arXiv metadata. You must own the paper first",
              "(`arxiv_ownership.md`); metadata changes go through *Update this article*",
              "on your submission page. A name correction is a metadata edit, not a new",
              "version of the paper.", "",
              "Note the ordering trap: <https://arxiv.org/auth/request-ownership> matches",
              "your name against the author list, and on these papers that list is the",
              "thing that is wrong — so the request can bounce. If it does, ask the",
              "submitting co-author for the paper password instead",
              "(<https://arxiv.org/auth/need-paper-password>), which does not name-match.",
              ""]
        for p in typo:
            L.append(f"- [ ] [`{p['arxiv']}`](https://arxiv.org/abs/{p['arxiv']}) — "
                     f"reads **{p['near_miss']}** — "
                     f"{(p.get('title_display') or p['title'])[:60]}")
        L.append("")
    if absent:
        L += [f"## Missing you entirely — {len(absent)}", "",
              "arXiv's author list for these does not contain anything close to your",
              "name. Either the submitter left you off, or the bibliography entry points",
              "at the wrong arXiv id — check which before asking anyone to change",
              "anything. If the paper is genuinely yours, only the submitter can add you;",
              "an ownership request will fail the name match.", ""]
        for p in absent:
            L.append(f"- [ ] [`{p['arxiv']}`](https://arxiv.org/abs/{p['arxiv']}) — "
                     f"{(p.get('title_display') or p['title'])[:60]}")
            L.append(f"      arXiv lists: {', '.join(p['arxiv_authors'])[:150]}")
        L.append("")
    if not (typo or absent):
        L += ["Nothing to fix — every retrieved record names you exactly.", ""]
    with open(path, "w") as f:
        f.write("\n".join(L) + "\n")
    return path, len(typo), len(absent)


def _rows(group, extra=lambda p: "") -> list[str]:
    return [f"- [ ] {p.get('citations') or 0:>4} cites — "
            f"[`{p['arxiv']}`](https://arxiv.org/abs/{p['arxiv']}) "
            f"{(p.get('title_display') or p['title'])[:72]}{extra(p)}"
            for p in group]


def arxiv_ownership_file(cfg, papers, registered: set[str] | None) -> tuple[str, int]:
    ident = cfg["identity"]
    path = os.path.join(TASKS, "arxiv_ownership.md")
    if registered is None:
        body = ["# arXiv ownership", "",
                f"`https://arxiv.org/a/{ident['orcid']}` does not resolve yet. Link your",
                "arXiv account to your ORCID first: <https://arxiv.org/user/confirm_orcid_id>",
                "then re-run `python scripts/audit_identity.py`."]
        with open(path, "w") as f:
            f.write("\n".join(body) + "\n")
        return path, 0

    seen, gap = set(), []
    for p in sorted(papers, key=lambda p: -(p.get("citations") or 0)):
        a = p["arxiv"]
        if a in seen:
            continue
        seen.add(a)
        if a not in registered:
            gap.append(p)
    L = [f"# arXiv: claim ownership of {len(gap)} papers", "",
         f"Registered as author on **{len(registered)}** of **{len(seen)}** arXiv papers.",
         f"Public list: <https://arxiv.org/a/{ident['orcid']}>", "",
         "## Why this is first, not last",
         "",
         "Two things depend on it, and both are invisible until you look:",
         "",
         "1. **You cannot add a journal-ref or DOI to a paper you do not own.** The",
         "   journal-ref list further down `WORKLIST.md` is *blocked* on this for any",
         "   paper here — and journal-ref is what Google Scholar matches citations on.",
         f"2. `https://arxiv.org/a/{ident['orcid']}` is a public, indexable publication",
         "   list on arxiv.org, with an Atom feed and an embeddable widget. Right now it",
         "   shows less than half your corpus, on a domain with far more crawl authority",
         "   than any personal site.",
         "",
         "arXiv's own January 2026 endorsement-policy post recommends claiming ownership",
         "of every paper you co-authored, so this is the documented intent, not a hack.",
         "",
         "## Two routes",
         "",
         "**With the paper password (instant).** The password is in the submitter's",
         "acceptance email. Ask the submitting co-author for it, then enter the arXiv id",
         "and password at <https://arxiv.org/auth/need-paper-password>.",
         "",
         "**Without it (a couple of days).** <https://arxiv.org/auth/request-ownership>",
         "— arXiv staff verify manually. No co-author involvement needed, so for a long",
         "tail of old papers this is the path of least effort: submit them in a batch and",
         "forget about it.",
         "",
         "If a paper is already in your owned list but you are not listed as an author,",
         "that is a different form: <https://arxiv.org/auth/change-author-status>.",
         "",
         "For your own future submissions: share the paper password with every co-author",
         "in the announcement email. It costs nothing and saves them this page.",
         "",
         f"## The {len(gap)} papers, citation-ordered", ""]
    L += _rows(gap)
    with open(path, "w") as f:
        f.write("\n".join(L) + "\n")
    return path, len(gap)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-hf", action="store_true",
                    help="skip the per-paper Hugging Face checks (the slow part)")
    ap.add_argument("--no-names", action="store_true",
                    help="skip the arXiv author-name check (needs ~3s per 50 papers)")
    args = ap.parse_args()
    cfg = load_config()
    ident, ids = cfg["identity"], cfg["ids"]
    papers = (read_yaml(os.path.join(DATA, "papers.yaml")) or {})["papers"]
    # One row per arXiv id, not per record: a few papers legitimately carry two
    # records (a retitled version), and checking the same page twice reads as two
    # separate jobs on a worklist worked by hand.
    ax, seen = [], set()
    for p in sorted(papers, key=lambda p: -(p.get("citations") or 0)):
        if p.get("arxiv") and p["arxiv"] not in seen:
            seen.add(p["arxiv"])
            ax.append(p)
    os.makedirs(TASKS, exist_ok=True)

    print("reading ORCID ...", flush=True)
    orc = orcid_public(ident["orcid"])
    print("reading arXiv authority records ...", flush=True)
    reg = arxiv_registered(ident["orcid"])
    print("searching Wikidata by identifier ...", flush=True)
    wd = wikidata_item(cfg) or ids.get("wikidata")
    wd_path, wd_gaps = None, {}
    if wd:
        wd_gaps = wikidata_gaps(wd, cfg)
        if wd_gaps:
            wd_path = wikidata_followup_file(wd_gaps, cfg)
    # --no-hf means "leave the HF artifacts alone", not "regenerate them from cache".
    # Writing the cached view here would silently overwrite a freshly-checked
    # worklist with older numbers, which is worse than not writing at all.
    variants = [ident["name"]] + list(ident.get("name_variants") or [])
    hf = None
    hf_path = None
    if not args.no_hf:
        print(f"checking {len(ax)} Hugging Face paper pages ...", flush=True)
        hf = hf_state(ax, ids["huggingface"], variants)
        hf_path = hf_worklist_file(hf)

    name_path = n_typo = n_absent = None
    if not args.no_names:
        print("checking arXiv author lists for your name ...", flush=True)
        name_path, n_typo, n_absent = arxiv_name_file(ax, variants)

    ax_path, n_gap = arxiv_ownership_file(cfg, ax, reg)
    # Papers arXiv says you own that the bibliography does not mention. Usually a new
    # paper the .bib has not caught up with, occasionally an ownership claim on
    # someone else's paper -- either way it is the one direction of this diff that
    # nothing else in the repo would ever surface.
    stray = sorted((reg or set()) - {p["arxiv"] for p in ax})

    # --- the audit report -------------------------------------------------------
    canon = ident["canonical_url"].rstrip("/")
    url_vals = [u for _, u in orc["urls"] if u]
    has_canon = any(canon in (u or "").rstrip("/") for u in url_vals)
    missing_variants = [v for v in ident["name_variants"]
                        if v != ident["name"] and v not in orc["other_names"]]
    # Other personal pages count as satisfied when *listed*, not when removed: a
    # second page declared to be the same person fuses with the canonical one, and
    # only an undeclared one competes with it.
    other_pages = [u for u in (ident.get("other_pages") or [])
                   if not any(u.rstrip("/") in (v or "").rstrip("/") for v in url_vals)]
    want_kw = [k for k in (ident.get("keywords") or [])
               if k.lower() not in {k2.lower() for k2 in orc["keywords"]}]

    def status(ok: bool) -> str:
        return "ok" if ok else "**fix**"

    L = ["# Identity audit", "",
         "Live read of the surfaces you do not control. Regenerate with",
         "`python scripts/audit_identity.py`. Every row is checkable without a login,",
         "which is why it can be re-run — the fixes all need one.", "",
         "| surface | state | |", "|---|---|---|",
         f"| ORCID works (public) | {orc['works']} of {len(papers)} | {status(orc['works'] > 0)} |",
         f"| ORCID canonical URL | {'present' if has_canon else 'absent'} | {status(has_canon)} |",
         f"| ORCID name variants | {len(orc['other_names'])} listed | {status(not missing_variants)} |",
         f"| ORCID keywords | {len(orc['keywords'])} of "
         f"{len(ident.get('keywords') or [])} | {status(not want_kw)} |",
         f"| ORCID lists other personal pages | "
         f"{len((ident.get('other_pages') or [])) - len(other_pages)} of "
         f"{len(ident.get('other_pages') or [])} | {status(not other_pages)} |",
         f"| ORCID employment/education | {orc['employments']}/{orc['educations']} | {status(orc['employments'] > 0)} |",
         # Intersection, not len(reg): the feed also lists papers that are not in the
         # bibliography at all, and counting those made the row read "105 of 105" while
         # still flagging a gap.
         f"| arXiv registered author | {len({p['arxiv'] for p in ax} & (reg or set()))}"
         f" of {len({p['arxiv'] for p in ax})} | {status(n_gap == 0)} |",
         f"| Wikidata author item | {wd or 'none'} | {status(bool(wd))} |"]
    if wd_gaps:
        n_wd = (len(wd_gaps["missing"]) + len(wd_gaps["wrong"]) + len(wd_gaps["dupes"])
                + len(wd_gaps["bad_aliases"]) + len(wd_gaps["want_aliases"]))
        L.append(f"| Wikidata item complete | {n_wd} gaps | {status(not n_wd)} |")
    if hf is not None:
        # Claimable, not total: three of these pages carry no author string resembling
        # your name, so they cannot be claimed at all. Scoring them against the total
        # leaves a row that can never reach "ok" and gives no hint why.
        claimable = len(ax) - len(hf["missing"]) - len(hf["blocked"])
        L += [f"| HF pages indexed | {len(ax) - len(hf['missing'])} of {len(ax)} | "
              f"{status(not hf['missing'])} |",
              f"| HF pages claimed | {len(hf['claimed'])} of {claimable} claimable | "
              f"{status(not hf['unclaimed'])} |"]
        if hf["pending"]:
            L.append(f"| HF claims in moderation | {len(hf['pending'])} | waiting |")
        if hf["blocked"]:
            L.append(f"| HF pages not claimable (name wrong upstream) | "
                     f"{len(hf['blocked'])} | see arXiv row |")
    if n_typo is not None:
        L.append(f"| arXiv records misspelling your name | {n_typo} | {status(not n_typo)} |")
        L.append(f"| arXiv records omitting you | {n_absent} | {status(not n_absent)} |")
    if stray:
        L.append(f"| arXiv papers missing from your bibliography | {len(stray)} | "
                 f"**check** |")
    L += [f"| Semantic Scholar records | {len(ids['semantic_scholar'])} | "
          f"{status(len(ids['semantic_scholar']) == 1)} |", ""]

    if orc["works"] == 0:
        L += ["## ORCID has 0 public works", "",
              "Note the *public*: an item set to “trusted parties” is invisible to the",
              "public API, which is the only thing Semantic Scholar, OpenAlex and Crossref",
              "read. So before importing, set **Account settings → Visibility preferences**",
              "to *Everyone*, or the import lands somewhere nothing can see.",
              "",
              "Then one upload: *Works → + Add → Add BibTeX* → `tasks/orcid_import.bib`.",
              "Not the DOI form 100 times — every entry in that file now carries a DOI",
              "(missing ones filled from arXiv), and ORCID groups works by identifier, so",
              "the whole file merges with the registry copies instead of duplicating them.",
              ""]
    if not has_canon:
        L += ["## ORCID researcher URLs point somewhere else", "",
              "Listed: " + (", ".join(f"`{u}`" for u in url_vals) or "none") + "  ",
              f"Expected: `{canon}`", "",
              "Two separate problems if one of those is a site-builder page. It competes",
              "with your canonical URL for the same identity — engines cannot fuse two",
              "candidate homepages — and Wix/Squarespace/Notion pages are JS-rendered, so",
              "AI crawlers that do not execute JavaScript see an empty document. Add the",
              "canonical URL, and either delete the other or make it redirect.", ""]
    if missing_variants:
        L += ["## ORCID name variants not listed", "",
              "*Also known as* is what a disambiguation model matches on when a citation",
              "uses a different form. Add: " +
              ", ".join(f"`{v}`" for v in missing_variants), ""]
    if want_kw:
        L += ["## ORCID keywords to add", "",
              "One of the few facets ORCID exposes for subject search, and free. Multi-word",
              "phrases someone would actually type — `model merging` is a query, `merging`",
              "is not — and no coined names, which have no lexical path from any real",
              "question. The same list fills Google Scholar's five interest slots (pick the",
              "top five). Edit `config.yaml` → `identity.keywords` to change it.", "",
              *[f"- [ ] {k}" for k in want_kw], ""]
    if other_pages:
        L += ["## Other personal pages not declared on ORCID", "",
              "Not a demand to delete them. A second page is only a problem while nothing",
              "says it is the same person — then two candidate homepages compete. Listing it",
              "in *Websites & social links* next to the canonical URL is what fuses them.", "",
              *[f"- [ ] {u}" for u in other_pages], ""]
    if reg is not None and n_gap:
        L += [f"## arXiv: {n_gap} papers you are not registered as author on", "",
              "The biggest finding here, and a prerequisite rather than a task: you cannot",
              "add a journal-ref to a paper you do not own. Full list and both claim",
              "routes: [arxiv_ownership.md](arxiv_ownership.md).", ""]
    if wd_gaps and (wd_gaps["missing"] or wd_gaps["wrong"] or wd_gaps["dupes"]
                    or wd_gaps["bad_aliases"] or wd_gaps["want_aliases"]):
        bad = wd_gaps["bad_aliases"]
        L += [f"## Wikidata item {wd} exists — {'a correction and ' if bad else ''}"
              f"{len(wd_gaps['missing'])} identifiers to add", ""]
        if bad:
            L += ["An alias was stored as one string with its markdown intact "
                  f"(`{bad[0][:60]}`), so it matches nothing. Fix that first.", ""]
        L += ["Full diff, plus the Author Disambiguator walkthrough that both links your",
              "papers and clears the 50-edit gate: "
              "[wikidata_followup.md](wikidata_followup.md).", ""]
    if stray:
        L += [f"## {len(stray)} arXiv papers you own are not in your bibliography", "",
              "Read off `arxiv.org/a/<orcid>`, which is the only place this shows up: the",
              "collector starts from the .bib, so a paper missing there is invisible to",
              "every other check here. Add it to the bibliography (or, if the claim was a",
              "mistake, unclaim it on arXiv).", "",
              *[f"- [ ] <https://arxiv.org/abs/{a}>" for a in stray], ""]
    if not wd:
        L += ["## No Wikidata author item", "",
              "Searched by ORCID (P496), Semantic Scholar (P4012), Google Scholar (P1960)",
              "and GitHub (P2037) — no item claims any of them. Name search is not used",
              "here on purpose: it returns *paper* items that merely mention you.",
              "", "Walkthrough: [wikidata_manual.md](wikidata_manual.md).", ""]
    if hf and (hf["missing"] or hf["unclaimed"] or hf["blocked"]):
        L += [f"## Hugging Face: {len(hf['missing'])} to index, "
              f"{len(hf['unclaimed'])} to claim, {len(hf['blocked'])} blocked", "",
              "Live counts, not the ones cached in `papers.yaml`. Lists:",
              "[hf_worklist.md](hf_worklist.md).", ""]
    if n_typo:
        L += [f"## arXiv metadata misspells your name on {n_typo} papers", "",
              "Upstream of every other surface here — Hugging Face, Semantic Scholar,",
              "OpenAlex and Scholar all read arXiv's author list, so one wrong character",
              "creates one wrong author in all of them, holding citations that cannot be",
              "merged back. Details and the fix order:",
              "[arxiv_name_fixes.md](arxiv_name_fixes.md).", ""]

    path = os.path.join(TASKS, "identity_audit.md")
    with open(path, "w") as f:
        f.write("\n".join(L) + "\n")

    # Counts for WORKLIST.md, in build/ because they are observed state: entirely
    # re-derivable from the live APIs, so committing them would be storing someone
    # else's data and letting it go stale. Absent file = the section is skipped.
    os.makedirs(BUILD, exist_ok=True)
    state_path = os.path.join(BUILD, "identity_state.json")
    state = {}
    if args.no_hf:
        # Carry the previous HF lists through untouched rather than dropping them:
        # this run made no claim about Hugging Face either way, and dropping them
        # would silently demote WORKLIST.md back to the collector's cached flags.
        try:
            with open(state_path) as f:
                prev = json.load(f)
            state = {k: prev[k] for k in
                     ("hf_missing", "hf_unclaimed", "hf_pending", "hf_blocked")
                     if k in prev}
        except (OSError, ValueError):
            pass
    else:
        state = {"hf_missing": [p["arxiv"] for p in hf["missing"]],
                 "hf_unclaimed": [p["arxiv"] for p in hf["unclaimed"]],
                 "hf_pending": [p["arxiv"] for p in hf["pending"]],
                 "hf_blocked": [p["arxiv"] for p in hf["blocked"]]}
    state.update({"orcid_public_works": orc["works"],
                  "orcid_has_canonical_url": has_canon,
                  "orcid_missing_variants": missing_variants,
                  "orcid_keywords": len(orc["keywords"]),
                  "orcid_missing_keywords": want_kw,
                  "orcid_missing_other_pages": other_pages,
                  "arxiv_registered": len(reg) if reg is not None else None,
                  "arxiv_total": len({p["arxiv"] for p in ax}),
                  "arxiv_unowned": [p["arxiv"] for p in ax
                                    if reg is not None and p["arxiv"] not in reg],
                  "arxiv_stray": stray,
                  "wikidata": wd,
                  "wikidata_gaps": (len(wd_gaps.get("missing") or [])
                                    + len(wd_gaps.get("wrong") or [])
                                    + len(wd_gaps.get("dupes") or [])
                                    + len(wd_gaps.get("bad_aliases") or [])
                                    + len(wd_gaps.get("want_aliases") or []))
                  if wd_gaps else None})
    with open(state_path, "w") as f:
        json.dump(state, f, indent=1)

    wrote = [path, ax_path] + [q for q in (hf_path, name_path, wd_path) if q]
    print("\nwrote " + "\n      ".join(wrote))
    for line in L:
        if line.startswith("| ") and "---" not in line:
            print("  " + line)


if __name__ == "__main__":
    main()
