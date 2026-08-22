#!/usr/bin/env python3
"""What a human sees before promoting anything: the terminal views and the review page.

Three read-only surfaces over the same data:

    checked / show    one paper in the terminal, with every finding and the quote behind
                      each number
    suspects          the drafts whose text most looks like the paper was not read
    review_page       one HTML page over every paper -- live, drafted, neither --
                      written into build/, never published

Nothing here writes a sidecar. Promotion is `draft_sidecars.py --accept`.
"""
from __future__ import annotations

import collections
import os
import re
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


from common import (BUILD, ROOT, answered_by, has_live_sidecar,  # noqa: E402
                    phrasings, qa_loci, read_yaml)
from sidecar_io import (CACHE, draft_path, draft_paths, front_matter, held,  # noqa: E402
                        live_path, live_paths, oneline, quote, spec_sha, stale,
                        validate_draft)
from sidecar_repair import at, rule_of  # noqa: E402


def checked(slug: str) -> dict | str:
    """A draft with every claim already checked against the paper, or why it cannot be.

    The one review a human owes is asserting each line in public, and what makes that a
    minutes-long job is having the claim, its scope, the pointer it cites and the paper's
    own sentence for each figure in one place -- rather than the PDF open in another window,
    which is the friction that left 116 of 117 papers without a sidecar.

    Returns the checking, not a rendering of it, because there are two readers: a terminal
    (`show`) and a browser (`review_page`). Two renderers over one check is the only
    arrangement where they cannot disagree about a number.
    """
    path, live = draft_path(slug), False
    if not os.path.exists(path):
        path, live = live_path(slug), True
    if not os.path.exists(path):
        return f"no draft and no live sidecar for {slug}"
    fm = front_matter(path)
    if fm is None:
        return f"{os.path.relpath(path, ROOT)}: unreadable front matter"

    from validate import (deline, evidence_pointers, figures, figures_in, readability,
                          rounds_to, values_in)
    # Bucketed by what each finding is about, so the renderers put it next to the
    # sentence rather than in a list at the bottom that reads as someone else's problem.
    prose = {}
    for kind, at, msg in readability(fm):
        prose.setdefault((kind, at), []).append(msg)
    cache = os.path.join(CACHE, f"{slug}.txt")
    text = deline(open(cache, errors="replace").read()) if os.path.exists(cache) else ""
    have, vals = (figures_in(text), values_in(text)) if text else (set(), [])
    flat = re.sub(r"\s+", " ", text)

    # Which questions retrieve each claim, joined claim-major on purpose. A published answer
    # is a question followed by claim text and scope, so the instinct is to group by question
    # -- but 212 of 318 claims answer more than one, so that page renders two thirds of them
    # twice and invites accepting a claim in one place while flagging the same words in
    # another. Only each question's canonical first phrasing: the paraphrase set is its own
    # check, in the questions section, where the axes are comparable.
    asks: dict = {}
    for gi, g in enumerate(fm.get("qa") or []):
        first = (phrasings(g) or [None])[0]
        for a in answered_by(g):
            asks.setdefault(a, []).append((gi, oneline(first)))
    answered = set(asks)
    claims = []
    for c in fm.get("claims") or []:
        kind = c.get("kind") or "result"
        row = {"kind": kind, "id": c.get("id"),
               "evidence": c.get("evidence") or ("--" if kind == "context" else "MISSING"),
               "text": oneline(c.get("text")), "scope": oneline(c.get("scope")),
               "orphan": c.get("id") not in answered, "pointers": [], "figures": [],
               "asked": asks.get(c.get("id"), []),
               "prose": prose.get(("claim", str(c.get("id") or "?")), [])}
        if text:
            row["pointers"] = [(label, bool(pat.search(text)))
                               for label, pat in evidence_pointers(c.get("evidence") or "")]
            for n in figures(row["text"] + " " + row["scope"]):
                if n.isdigit() and 1900 <= int(n) <= 2099:
                    continue
                # The paper's own words around the figure, so the author checks the
                # number against the sentence it came from, not against a page number.
                row["figures"].append((n, quote(flat, n)
                                       if (n in have or rounds_to(n, vals)) else None))
        claims.append(row)

    # Left in the drafted order, which is the order the sidecar file has and therefore the
    # order the site publishes: both renderers walk the questions instead, so a sort here
    # would only reorder the orphan list while looking like it decided the page.
    return {"slug": slug, "path": os.path.relpath(path, ROOT), "has_text": bool(text),
            "live": live, "one_liner": oneline(fm.get("one_liner")),
            "claims": claims, "qa": fm.get("qa") or [],
            "prose_q": {k[1]: v for k, v in prose.items() if k[0] == "question"},
            # Same bucketing for the fields below the claims, each keyed by the handle
            # the renderers already print: a misreading by its own text, a term by its
            # name. `prose_page` belongs to no field, so it is a bare list.
            "prose_m": {k[1]: v for k, v in prose.items() if k[0] == "misreading"},
            "prose_t": {k[1]: v for k, v in prose.items() if k[0] == "term"},
            "prose_page": [m for k, v in prose.items() if k[0] == "page" for m in v],
            "misreadings": fm.get("misreadings") or [],
            "terminology": fm.get("terminology") or {}}


def show(slug: str) -> None:
    """`checked` for a terminal."""
    d = checked(slug)
    if isinstance(d, str):
        return print(d)

    print(f"\n{d['path']}")
    print("one_liner: " + d["one_liner"])
    if not d["has_text"]:
        print("  (no cached full text -- figures and pointers cannot be checked here)")
    for m in d["prose_page"]:
        print(f"  WHOLE PAGE  {m}")

    def one_claim(c) -> None:
        orphan = "   (no question points here)" if c["orphan"] else ""
        print(f"\n    [{c['kind']}] {c['id']}   evidence: {c['evidence']}{orphan}")
        print("    " + c["text"])
        print("    Holds for: " + c["scope"])
        if also := [q for gi, q in c["asked"] if gi != c["asked"][0][0]]:
            for q in also:
                print(f"    also answers: {q}")
        for m in c["prose"]:
            print(f"    READS BADLY  {m}")
        for label, ok in c["pointers"]:
            print(f"    {'ok' if ok else 'NOT FOUND'}: the paper's own text "
                  f"mentions {label}")
        for n, sentence in c["figures"]:
            note = sentence or "NOT IN THE PAPER -- correct it or drop the figure"
            print(f"    {n:>9}  {note}")

    # Question, then the claim published as its answer -- same order as the review page,
    # and for the same reason: a claim read without the question it answers is read
    # without its subject. Each claim printed once, since two thirds of them answer more
    # than one question.
    by_id, drawn = {str(c["id"]): c for c in d["claims"]}, set()
    for i, g in enumerate(d["qa"]):
        qs = phrasings(g)
        print(f"\n  Q{i + 1}. {qs[0] if qs else '(no question text)'}"
              + (f"   (+{len(qs) - 1} more phrasing(s))" if len(qs) > 1 else ""))
        for m in (qs and d["prose_q"].get(str(qs[0])) or []):
            print(f"      UNANSWERABLE ALONE  {m}")
        if not answered_by(g):
            print("      nothing answers this -- point it at a claim or drop it")
        for a in answered_by(g):
            c = by_id.get(str(a))
            if c is None:
                print(f"      points at {a}, which is not a claim id")
            elif str(a) in drawn:
                print(f"      ^ {a} -- shown above, under its first question")
            else:
                drawn.add(str(a))
                one_claim(c)

    if orphans := [c for c in d["claims"] if str(c["id"]) not in drawn]:
        print(f"\n  NO QUESTION POINTS AT THESE ({len(orphans)})")
        for c in orphans:
            one_claim(c)

    for i, g in enumerate(d["qa"]):
        if len(phrasings(g)) > 1:
            print(f"\n  Q{i + 1} phrasings:")
            for role, q in qa_loci(g):
                label = role.split("/")[1] if role.startswith("ask/") else role
                print(f"      {label if label != 'unsorted' else '(unsorted)':13} {q}")
                for m in d["prose_q"].get(str(q)) or []:
                    print(f"        UNANSWERABLE ALONE  {m}")

    # Printed only when something is wrong with them: a correct misreading or definition
    # is already in the draft the author is reading beside this output.
    for mis, why in d["prose_m"].items():
        print(f"\n  misreading: {mis}")
        for m in why:
            print(f"      DANGLES  {m}")
    for term, why in d["prose_t"].items():
        print(f"\n  term: {term}")
        for m in why:
            print(f"      DANGLES  {m}")


REVIEW_PAGE = os.path.join(BUILD, "sidecar_review.html")

_CSS = """
:root { --bg:#fff; --fg:#1a1a1a; --dim:#5c5c5c; --line:#e3e3e3; --card:#fafafa;
        --bad:#a3122a; --badbg:#fdeef1; --ok:#1c6b3c; --warn:#8a5a00; --warnbg:#fdf6e7; }
/* Three states, not two: an explicit choice stamps data-theme on the root, and the
   default "system" setting stamps nothing. The media query is guarded so a chosen light
   theme beats a dark OS, and repeated under the stamp so a chosen dark theme beats a
   light one -- which matters wherever this page is viewed inside a host that themes it. */
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) { --dark: 1;
          --bg:#16181c; --fg:#e8e8e8; --dim:#a0a0a0; --line:#2e3238; --card:#1d2025;
          --bad:#ff8fa3; --badbg:#3a1520; --ok:#7ddaa0; --warn:#e8c07a; --warnbg:#3a2f14; } }
:root[data-theme="dark"] { --dark: 1;
        --bg:#16181c; --fg:#e8e8e8; --dim:#a0a0a0; --line:#2e3238; --card:#1d2025;
        --bad:#ff8fa3; --badbg:#3a1520; --ok:#7ddaa0; --warn:#e8c07a; --warnbg:#3a2f14; }
* { box-sizing:border-box }
body { background:var(--bg); color:var(--fg); margin:0 auto; padding:2rem 1.25rem 6rem;
       max-width:52rem; font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif }
h1 { font-size:1.5rem; margin:0 0 .25rem } h2 { font-size:1.2rem; margin:2.5rem 0 .25rem }
h3 { font-size:.95rem; margin:1.75rem 0 .5rem; color:var(--dim);
     text-transform:uppercase; letter-spacing:.06em }
a { color:inherit } code,kbd { font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace }
.sub { color:var(--dim); margin:0 0 2rem }
.paper { border-top:2px solid var(--fg); padding-top:1rem; margin-top:3rem }
.one { font-size:1.05rem; margin:.5rem 0 1rem }
.cmd { background:var(--card); border:1px solid var(--line); border-radius:6px;
       padding:.6rem .75rem; overflow-x:auto; white-space:pre }
.claim { background:var(--card); border:1px solid var(--line); border-left:3px solid var(--line);
         border-radius:6px; padding:.75rem .9rem; margin:.6rem 0 }
.claim.context { border-left-color:var(--dim) }
.claim.flagged { border-left-color:var(--bad) }
.id { color:var(--dim); font:12px/1.4 ui-monospace,Menlo,monospace }
.scope { color:var(--dim); font-size:.9rem; margin:.4rem 0 0 }
.checks { margin:.55rem 0 0; padding:0; list-style:none; font-size:.85rem }
.checks li { padding:.15rem 0 }
.checks a { text-decoration:underline; text-decoration-color:var(--dim);
            text-underline-offset:2px }
.n { display:inline-block; min-width:3.5rem; font:12px ui-monospace,Menlo,monospace;
     color:var(--fg) }
.bad { color:var(--bad); background:var(--badbg); padding:.1rem .3rem; border-radius:3px }
.ok { color:var(--ok) } .warn { color:var(--warn) } .dim { color:var(--dim) }
.ask { margin:2rem 0 .5rem; font-weight:600; font-size:1.02rem }
.ask:first-of-type { margin-top:1rem }
.again { margin:.6rem 0 .6rem 1rem; font-size:.9rem; color:var(--dim) }
.again a { color:var(--fg) }
.asked { color:var(--dim); font-size:.85rem; margin:.45rem 0 0 }
.q { margin:.5rem 0 1rem } .q li { color:var(--dim) }
.q b { color:var(--fg); font-weight:600 }
table { border-collapse:collapse; width:100%; font-size:.9rem }
td { border-top:1px solid var(--line); padding:.45rem .5rem; vertical-align:top }
td:first-child { white-space:nowrap; color:var(--fg); font-weight:600; width:11rem }
.note { background:var(--warnbg); border:1px solid var(--line); border-radius:6px;
        padding:.75rem .9rem; color:var(--fg); font-size:.9rem }
.toc { padding-left:1.2rem } .toc li { margin:.2rem 0 }
.sus { padding-left:1.2rem; margin:.35rem 0 .9rem; font-size:.9rem; color:var(--dim) }
.sus li { margin:.15rem 0 }
"""


def _flags(d: dict) -> list[str]:
    """Everything on one draft that a reader should not have to hunt for."""
    out = []
    figs = sum(1 for c in d["claims"] for n, s in c["figures"] if s is None)
    ptrs = sum(1 for c in d["claims"] for _, ok in c["pointers"] if not ok)
    orph = sum(1 for c in d["claims"] if c["orphan"])
    hard = sum(1 for c in d["claims"] if c["prose"])
    vague = len(d["prose_q"])
    loose = len(d["prose_m"]) + len(d["prose_t"])
    if hard:
        out.append(f"{hard} claim{'s' if hard > 1 else ''} to shorten or split")
    if vague:
        out.append(f"{vague} question{'s' if vague > 1 else ''} with nothing to point at")
    if loose:
        out.append(f"{loose} definition{'s' if loose > 1 else ''} or misreading"
                   f"{'s' if loose > 1 else ''} that dangle once extracted")
    out += d["prose_page"]
    if figs:
        out.append(f"{figs} figure{'s' if figs > 1 else ''} not in the paper")
    if ptrs:
        out.append(f"{ptrs} pointer{'s' if ptrs > 1 else ''} the paper does not mention")
    if orph:
        out.append(f"{orph} claim{'s' if orph > 1 else ''} no question points at")
    if not d["has_text"]:
        out.append("no cached full text, so nothing here was checked against the paper")
    return out


def at_sentence(links: dict, phrase: str) -> str:
    """The paper's own HTML, scrolled to the phrase -- or "" if it cannot be linked.

    A text fragment rather than a section anchor, because the anchor ids of an arXiv or
    ar5iv rendition are generated and change between versions, while the sentence is the
    thing being checked. A fragment that fails to match costs nothing: the browser opens the
    paper at the top.

    Only the review page links these. On a published page the same link once per claim adds
    no retrievable fact to a passage that already carries the citation.
    """
    url = links.get("html") or links.get("arxiv_pdf") or links.get("publisher")
    if not url or "/html/" not in url:
        return ""
    # The window a quote comes from is cut mid-word at both ends, so the first and last
    # tokens are dropped: a fragment matches on an exact substring, and half a word
    # never does.
    words = re.sub(r"\s+", " ", phrase.strip().strip(".")).split()
    if len(words) > 3:
        words = words[1:-1]
    if not words:
        return ""
    return url + "#:~:text=" + urllib.parse.quote(" ".join(words[:12]))


def review_page(papers: list[dict]) -> str:
    """Every fresh draft, checked, as one self-contained page to read in a browser.

    `--show` puts the same thing in a terminal, one slug at a time. This exists because
    reviewing is the only job on the worklist that is reading rather than pasting, and
    asking someone to run a command per paper to read prose is the wrong shape: the
    reading should be a link. Written to build/ and never to build/site/, because these
    are claims the author has not accepted and `--deploy` must not be able to reach them.
    """
    from html import escape as e

    by_slug = {p.get("slug"): p for p in papers}
    on_disk = sorted(os.path.basename(p)[:-3] for p in draft_paths())
    keep = held(spec_sha())
    fresh = [s for s in on_disk if s in keep]
    stale = [s for s in on_disk if s not in keep]
    fresh.sort(key=lambda s: -((by_slug.get(s) or {}).get("citations") or 0))

    done = [d for d in (checked(s) for s in fresh) if isinstance(d, dict)]
    out = ["<!doctype html><meta charset=utf-8>",
           "<meta name=viewport content='width=device-width,initial-scale=1'>",
           f"<title>Sidecar drafts to review ({len(done)})</title>", f"<style>{_CSS}</style>",
           f"<h1>{len(done)} sidecar draft{'s' if len(done) != 1 else ''} to review</h1>"]

    if not done:
        out.append("<p class=sub>Nothing is waiting. Queue more with "
                   "<code>python scripts/draft_sidecars.py --limit 20</code>.</p>")
    else:
        out += ["<p class=sub>Generated by the last run — reading this is the whole "
                "review. Each figure is shown beside the paper's own sentence, so the "
                "check is comparing two lines, not opening a PDF. Accepting is the one "
                "act that publishes an assertion under your name.</p>",
                "<h3>On this page</h3><ol class=toc>"]
        for d in done:
            p = by_slug.get(d["slug"]) or {}
            bad = _flags(d)
            out.append(f"<li><a href='#{e(d['slug'])}'>"
                       f"{e((p.get('title_display') or p.get('title') or d['slug'])[:70])}"
                       f"</a> — {p.get('citations') or 0} cites"
                       + (f" · <span class=bad>{e('; '.join(bad))}</span>" if bad else "")
                       + "</li>")
        out.append("</ol>")

    for d in done:
        p = by_slug.get(d["slug"]) or {}
        slug = d["slug"]
        out += [f"<div class=paper id='{e(slug)}'>",
                f"<h2>{e(p.get('title_display') or p.get('title') or slug)}</h2>",
                f"<p class=sub>{p.get('citations') or 0} cites · "
                f"<code>{e(d['path'])}</code></p>"]
        if bad := _flags(d):
            out.append("<p class=note><b>Before accepting:</b> "
                       + e("; ".join(bad)) + ".</p>")
        # Nothing here refuses the draft, which is exactly why it belongs on the page: the
        # checks have finished and a reader is about to put their name on prose no rule can
        # judge. `--suspect` ranks the same signals across drafts; here they name the claim.
        score, look = suspicion(d["path"])
        if score:
            out += ["<p class=note><b>Worth a second look:</b></p><ul class=sus>"]
            out += [f"<li>{e(line)}</li>" for line in look]
            out.append("</ul>")
        out.append(f"<p class=one>{e(d['one_liner'])}</p>")
        out.append("<div class=cmd>python scripts/draft_sidecars.py --accept "
                   + e(slug) + (" --replace" if has_live_sidecar(slug) else "") + "</div>")

        # One question, then the claims published as its answer, then the next -- each claim
        # rendered once. Printing a claim's question lines above itself made a page of
        # near-identical blocks differing by one line, and sorting by a claim's *first* question
        # cannot group its second, so the same question reappeared far apart. Under a later
        # question an already-shown claim is a one-line link: this answer also carries that
        # question, at the size that fact deserves.
        def claim_html(c) -> list[str]:
            bad_here = (any(sn is None for _, sn in c["figures"])
                        or any(not ok for _, ok in c["pointers"]) or c["prose"])
            cls = "claim" + (" context" if c["kind"] == "context" else "") \
                          + (" flagged" if bad_here else "")
            also = [f"<a href='#{e(slug)}-q{gi}'>{e(q)}</a>"
                    for gi, q in c["asked"] if gi != c["asked"][0][0]]
            block = [f"<div class='{cls}' id='{e(slug)}-{e(str(c['id']))}'>",
                     f"<div class=id>[{c['kind']}] {e(str(c['id']))} · cites "
                     f"{e(str(c['evidence']))}"
                     + ("  · no question points here" if c["orphan"] else "") + "</div>",
                     f"<div>{e(c['text'])}</div>",
                     f"<p class=scope><b>Holds for.</b> {e(c['scope'])}</p>"]
            if also:
                block.append("<p class=asked>also answers: " + " · ".join(also) + "</p>")
            if c["prose"]:
                block.append("<ul class=checks>")
                block += [f"<li><span class=bad>reads badly</span> "
                          f"<span class=dim>{e(m)}</span></li>" for m in c["prose"]]
                block.append("</ul>")
            if c["pointers"] or c["figures"]:
                block.append("<ul class=checks>")
                links = p.get("links") or {}
                for label, ok in c["pointers"]:
                    href = at_sentence(links, label) if ok else ""
                    shown = f"<a href='{e(href)}'>{e(label)}</a>" if href else e(label)
                    block.append(f"<li><span class={'ok' if ok else 'bad'}>"
                                 f"{'the paper mentions' if ok else 'THE PAPER NEVER MENTIONS'}"
                                 f"</span> {shown}</li>")
                for n, sentence in c["figures"]:
                    if sentence is None:
                        block.append(f"<li><span class=n>{e(n)}</span> "
                                     f"<span class=bad>not in the paper — correct it or "
                                     f"drop the figure</span></li>")
                    else:
                        # The quote itself is the link, so checking a figure against the
                        # paper's sentence and then against the paper costs one click
                        # rather than a search in another window.
                        href = at_sentence(links, sentence)
                        body = f"<span class=dim>{e(sentence)}</span>"
                        block.append(f"<li><span class=n>{e(n)}</span> "
                                     + (f"<a href='{e(href)}'>{body}</a>" if href else body)
                                     + "</li>")
                block.append("</ul>")
            block.append("</div>")
            return block

        by_id = {str(c["id"]): c for c in d["claims"]}
        out += [f"<h3>Answers ({len(d['qa'])} questions, {len(d['claims'])} claims)</h3>",
                "<p class=sub>One question, then the claim published as its answer — the "
                "shape a reader meets it in. Two things to check per claim, and they fail "
                "differently: the <b>text</b> must be true and carry its own subject, "
                "since it is quoted with no title beside it; and <b>Holds for</b> must "
                "name the condition that would make it false if changed — the models, the "
                "languages, the sizes, the year. A scope that is a hedge "
                "(\u201cfurther work is needed\u201d), a restatement of the claim, or a "
                "judgement about the claim\u2019s reliability is the one to rewrite.</p>"]
        drawn: set = set()
        for gi, g in enumerate(d["qa"]):
            qs = phrasings(g)
            extra = (f" <span class=dim>+{len(qs) - 1} phrasing"
                     f"{'s' if len(qs) > 2 else ''}</span>") if len(qs) > 1 else ""
            why = "".join(f"<br><span class=bad>unanswerable alone</span> "
                          f"<span class=dim>{e(m)}</span>"
                          for m in (d["prose_q"].get(str(qs[0])) or []) if qs)
            head = e(qs[0]) if qs else "(no question text)"
            out.append(f"<p class=ask id='{e(slug)}-q{gi}'>{head}{extra}{why}</p>")
            answers = answered_by(g)
            if not answers:
                out.append("<p class=note>Nothing answers this — either point it at a "
                           "claim or drop the question.</p>")
            for a in answers:
                c = by_id.get(str(a))
                if c is None:
                    out.append(f"<p class=note>points at <code>{e(str(a))}</code>, "
                               "which is not a claim id.</p>")
                elif str(a) in drawn:
                    out.append(f"<p class=again>↑ <a href='#{e(slug)}-{e(str(a))}'>"
                               f"{e(oneline(c['text'])[:90])}…</a> "
                               f"<span class=dim>shown above, under its first question"
                               f"</span></p>")
                else:
                    drawn.add(str(a))
                    out += claim_html(c)

        if orphans := [c for c in d["claims"] if str(c["id"]) not in drawn]:
            out += [f"<h3>No question points at these ({len(orphans)})</h3>",
                    "<p class=sub>Published in the claim list and reachable by nothing a "
                    "visitor would type. Give each one a question, fold it into a claim "
                    "that has one, or drop it.</p>"]
            for c in orphans:
                out += claim_html(c)

        if d["qa"]:
            out += ["<h3>The four routes to each question</h3>",
                    "<p class=sub>The answers are above. What is left to read here is "
                    "whether each labelled route is really a different route — "
                    "<b>plain</b> in the words of someone who has not read the paper, "
                    "<b>jargon</b> in the field\u2019s own vocabulary, <b>task</b> as the "
                    "thing they are trying to do, <b>practitioner</b> in the first person "
                    "and deciding. Three rewordings of one sentence match one query; "
                    "three vocabularies match three. Anything marked "
                    "<b>unsorted</b> predates the routes and is what a redraft "
                    "replaces.</p>"]
            for gi, g in enumerate(d["qa"]):
                out.append("<ul class=q>")
                for i, (role, q) in enumerate(qa_loci(g)):
                    why = d["prose_q"].get(str(q)) or []
                    label = role.split("/")[1] if role.startswith("ask/") else role
                    out.append(f"<li><span class=dim>{e(label)}</span> "
                               f"{'<b>' if not i else ''}{e(q)}"
                               f"{'</b>' if not i else ''}"
                               + "".join(f"<br><span class=bad>unanswerable alone</span> "
                                         f"<span class=dim>{e(m)}</span>" for m in why)
                               + "</li>")
                out.append("</ul>")

        # Both blocks below are published as standalone fragments -- a misreading as its
        # own list item, a term as a `DefinedTerm` with nothing beside it -- so the note
        # goes inline, under the words that dangle.
        if d["misreadings"]:
            out.append(f"<h3>Misreadings it heads off ({len(d['misreadings'])})</h3><ul>")
            for m in d["misreadings"]:
                why = d["prose_m"].get(str(m)) or []
                out.append(f"<li>{e(oneline(m))}"
                           + "".join(f"<br><span class=bad>dangles alone</span> "
                                     f"<span class=dim>{e(w)}</span>" for w in why)
                           + "</li>")
            out.append("</ul>")

        if d["terminology"]:
            out.append(f"<h3>Terminology ({len(d['terminology'])})</h3><table>")
            for k, v in d["terminology"].items():
                why = d["prose_t"].get(str(k)) or []
                out.append(f"<tr><td>{e(str(k))}</td><td>{e(oneline(v))}"
                           + "".join(f"<br><span class=bad>dangles alone</span> "
                                     f"<span class=dim>{e(w)}</span>" for w in why)
                           + "</td></tr>")
            out.append("</table>")
        out.append("</div>")

    # The published ones, for the other reason to open this page: not "what must I
    # check" but "what does an accepted sidecar actually look like". They are already
    # rendered into the site, so link the built page rather than restating it here.
    live = sorted(os.path.basename(f)[:-3] for f in live_paths())
    if live:
        out += [f"<h2>{len(live)} already published</h2>",
                "<p class=sub>Accepted, and rendered into the site — this is what a paper "
                "page looks like once it has a sidecar, which is the comparison worth "
                "making against a page that has none.</p><ul>"]
        for s in live:
            p = by_slug.get(s) or {}
            built = os.path.join(BUILD, "site", "papers", s, "index.html")
            title = e((p.get("title_display") or p.get("title") or s)[:70])
            if os.path.exists(built):
                out.append(f"<li><a href='file://{e(built)}'>{title}</a> · "
                           f"<a href='file://{e(os.path.dirname(built))}/llms.txt'>llms.txt"
                           f"</a></li>")
            else:
                out.append(f"<li>{title} <span class=dim>— not built yet; "
                           f"run <code>python update.py --step render</code></span></li>")
        out.append("</ul>")

    if stale:
        out += [f"<h2>{len(stale)} stale draft{'s' if len(stale) > 1 else ''} — do not "
                f"read</h2>",
                "<p class=sub>Written against sidecar rules that have since changed. "
                "<code>--accept</code> refuses them and the next drafting run replaces "
                "them, so reading one is wasted effort.</p><ul>"]
        out += [f"<li class=id>{e(s)}</li>" for s in stale]
        out.append("</ul>")

    return "\n".join(out) + "\n"


def write_review_page(papers: list[dict]) -> str:
    # Build first, write second. `open(..., "w")` truncates on the way in, so building the
    # page inside the `with` meant one draft that made a check raise left a zero-byte
    # review page behind -- the previous good page destroyed by the run that failed to
    # replace it.
    html = review_page(papers)
    os.makedirs(BUILD, exist_ok=True)
    with open(REVIEW_PAGE, "w") as fh:
        fh.write(html)
    return REVIEW_PAGE


# A claim can only say these if the paper earned them: each asserts standing relative to
# other work, or a proof, which no table can settle -- and a model reaches for them when
# it is summarising an abstract's ambition instead of a result.
#
# Deliberately narrow. `always`, `never`, `any` and `guarantee` were in the list and every
# hit was ordinary English ("essentially the 0.54 of always picking the first candidate").
# Words like those flag every page, which is the same as no ranking.
LOUD = re.compile(r"\b(first|best|state[- ]of[- ]the[- ]art|sota|novel|prove[nsd]?"
                  r"|optimal|universal|unprecedented)\b", re.I)

# Words long enough that finding them in the paper means something. Four letters and under
# are function words and shared vocabulary, and counting them puts every claim near 100%.
_LONG = re.compile(r"[a-z][a-z0-9-]{4,}")

# Matched on a prefix, not whole: "saturated" against a paper that says "saturates" is the
# same word, and whole-word matching charged 1,428 claims for English morphology. Measured
# over all of them, the prefix lifts the median claim from 0.87 to 0.91 and the bottom decile
# from 0.71 to 0.78 -- the floor below is that decile, so this ranks the tail rather than a
# quarter of every page.
_STEM = 6
GROUNDED = 0.78


def grounded(text: str, low: str) -> float:
    """The share of a claim's longer words that occur in the paper's own text.

    A blunt instrument on purpose. It cannot tell a legitimate paraphrase from an invention,
    and it is not a check for that reason -- no draft is refused over it. What it does do is
    rank, and ranking is the whole job here: a reviewer with an evening has to spend it on
    the drafts most likely to be wrong, and a claim written in words the paper never uses is
    the cheapest available signal of one.
    """
    words = set(_LONG.findall(text.lower()))
    hit = [w for w in words if (w[:_STEM] if len(w) > _STEM else w) in low]
    return len(hit) / len(words) if words else 1.0


def suspicion(path: str) -> tuple[int, list[str]]:
    """(score, reasons) -- how likely a passing draft is to say something the paper does not.

    The checks answer "is this well-formed and are its numbers in the paper". Nothing answers
    "is this true", and nothing code-only can. So this ranks instead of judging, and every
    reason it gives names the field to read and what to read it against.
    """
    from validate import deline, figures, figures_in, rounds_to, values_in
    fm = front_matter(path) or {}
    slug = os.path.basename(path)[:-3]
    cached = os.path.join(CACHE, f"{slug}.txt")
    score, why = 0, []
    if not os.path.exists(cached):
        # The strongest signal available, and the one a reader would never guess: the figure
        # rule is the one rule with no exceptions, and here it did not run at all.
        return 4, ["no cached paper text, so not one figure in this draft was checked "
                   f"(python scripts/fulltext.py --slug {slug})"]
    with open(cached, errors="replace") as fh:
        text = deline(fh.read())
    low, have, vals = text.lower(), figures_in(text), values_in(text)
    loud, round_only, thin = [], [], []
    for c in (fm.get("claims") or []):
        if not isinstance(c, dict):
            continue
        cid, body = c.get("id"), str(c.get("text") or "")
        for word in sorted({m.group(0).lower() for m in LOUD.finditer(body)}):
            if word not in low:
                loud.append(f"claim '{cid}' says '{word}' and the paper's text never does")
        for n in figures(body):
            if n not in have and rounds_to(n, vals):
                round_only.append(f"claim '{cid}': the paper does not state {n}, only a "
                                  f"value that rounds to it")
        share = grounded(body, low)
        if share < GROUNDED:
            thin.append((share, f"claim '{cid}': {share:.0%} of its words appear in the "
                                f"paper -- read it against the paper's own sentence"))
    # Capped per family, and ordered by what a reader can act on. Uncapped, a long page of
    # thinly-worded claims outranks a short page that says the paper proved something it
    # never claims -- and the second is the one that must not go out under a name. The
    # families are also weighted apart for the same reason: an unearned "first" is a
    # sentence to delete, a low word overlap is a sentence to read.
    thin = [line for _, line in sorted(thin)]
    for weight, cap, lines in ((2, 2, loud), (1, 2, round_only), (1, 3, thin)):
        score += weight * min(cap, len(lines))
        why += lines[:cap] if len(lines) <= cap else \
            lines[:cap] + [f"... and {len(lines) - cap} more like the last one"]
    head = open(path, encoding="utf-8").read()[:2000]
    if "targeted repair" in head:
        score += 1
        why.append("some fields here are a machine's second wording, spliced in to clear a "
                   "check and not read since")
    return score, why


def suspects(papers: list[dict], top: int) -> None:
    """The drafts worth an evening, worst first. Only ones a reader can actually accept."""
    spec = spec_sha()
    keep = held(spec)
    ranked = []
    for f in draft_paths():
        slug = os.path.basename(f)[:-3]
        if slug not in keep or any(validate_draft(f, note=False)):
            continue
        score, why = suspicion(f)
        if score:
            ranked.append((score, slug, why))
    ranked.sort(key=lambda r: (-r[0], r[1]))
    cites = {p["slug"]: p.get("citations") or 0 for p in papers}
    print(f"{len(ranked)} of the drafts that pass every check still have something a "
          f"reader would want to see, worst first:\n")
    for score, slug, why in ranked[:top]:
        print(f"  {score:>3}  {slug}  ({cites.get(slug, 0)} cites)")
        for line in why:
            print(f"       - {line}")
        print()
    if len(ranked) > top:
        print(f"  ... {len(ranked) - top} more, --suspect 0 for all of them")
    print(f"  file://{os.path.join(BUILD, 'sidecar_review.html')}")


def review(papers: list[dict]) -> None:
    live = {os.path.basename(f)[:-3] for f in live_paths()}
    drafted = draft_paths()
    by_slug = {p["slug"]: p for p in papers}
    spec = spec_sha()
    # `keep` before the counts: a stale draft is not work for the reader, so counting it
    # under "awaiting you" asks for an evening that ends in an accept that refuses.
    keep = held(spec)
    obsolete = [os.path.basename(f)[:-3] for f in drafted
                if os.path.basename(f)[:-3] not in keep]
    stale_note = f"   ({len(obsolete)} stale, see below)" if obsolete else ""
    print(f"live sidecars        {len(live)}")
    print(f"drafts awaiting you  {len(drafted) - len(obsolete)}{stale_note}")
    # Subtracting the draft count printed -2, because the two re-drafts of live sidecars
    # are counted in both sets. Count the papers with neither instead.
    have = live | {os.path.basename(f)[:-3] for f in drafted}
    print(f"no sidecar, no draft "
          f"{len([p for p in papers if p['slug'] not in have])}")
    if obsolete:
        print(f"\n{len(obsolete)} draft(s) written against rules that have since changed. "
              f"Do not read these;\nthe next run replaces them:\n  "
              + ", ".join(obsolete[:6]) + (" ..." if len(obsolete) > 6 else ""))
        print("  python scripts/draft_sidecars.py --limit 0")
    stuck = {s: w for s, w in keep.items() if w != "current"}
    for s, w in stuck.items():
        print(f"\n{s}: {w}. Nothing will overwrite your edits. Either accept what you\n"
              f"  have with --anyway, or re-draft it yourself with --slug {s}.")
    # Only the ones it is worth spending an evening on. Listing a stale draft here under
    # "read, edit, then --accept" would contradict the paragraph above it.
    yours = [f for f in drafted if os.path.basename(f)[:-3] in keep]
    if yours:
        print(f"\nRead all {len(yours)} in a browser, already checked against each paper:"
              f"\n  file://{write_review_page(papers)}")
        print("\nDrafts, most cited first — read, edit, then --accept:")
        counts = collections.Counter()
        rows = sorted(yours, key=lambda f: -(
            (by_slug.get(os.path.basename(f)[:-3]) or {}).get("citations") or 0))
        for f in rows:
            slug = os.path.basename(f)[:-3]
            p = by_slug.get(slug) or {}
            errs, quality = validate_draft(f)
            flag = "  [schema errors]" if errs else ""
            if quality:
                flag += f"  [{len(quality)} to fix -- see --show {slug}]"
            # Say so here rather than at --accept time: a redraft of a paper that
            # already has a reviewed sidecar is read differently from a first draft,
            # and the difference should be visible while deciding what to read.
            if slug in live:
                flag += "  [REPLACES the live sidecar -- needs --replace]"
            print(f"  {(p.get('citations') or 0):>5} cites  {slug}{flag}")
            for e in errs + quality:
                counts[rule_of(e)] += 1
        if counts:
            # Per-paper counts say which evening to spend; this says which rule the
            # drafting keeps losing, which is the only one of the two that can be acted
            # on in the rules block every draft is written against. Derived on the way
            # past, printed, never stored -- it is a fact about this run.
            print("\nRules the open findings hit, most often first:")
            for rule, n in counts.most_common(6):
                print(f"  {n:>4}  {rule}")
            print("  A rule near the top of that list is a rules-block problem, not a "
                  "per-paper one:\n  docs/SIDECAR.md \u00a72 is what every draft was "
                  "written against.")
