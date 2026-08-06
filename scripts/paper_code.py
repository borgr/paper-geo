"""Deduce each paper's own code repository and publish it to its HF paper page.

A code link is the single most useful thing a paper page can carry that a citation
cannot: it is what a reader who believes the result reaches for next, and what an
assistant answering "is there an implementation?" needs to find. The site already
renders one -- `links.code` in build_site.py -- but it is fed from exactly one place,
Hugging Face's `githubRepo` field, which was set on 19 of 105 arXiv papers. Every
other paper's repo was sitting in its own full text, unread.

So: read it. The paper says where its code is, in the abstract or a first-page
footnote, in first person ("we release our code at"). That phrasing is the whole
signal, and it is what separates the paper's own repo from the ten others it cites
-- `huggingface/transformers` appears in a BabyLM footnote too, and linking that
would be worse than linking nothing.

Three passes, and only the first is allowed to decide on its own:

  1. `github.com/...` in the full text with a first-person release phrase in front of
     it, confirmed by GitHub returning 200. Two independent corroborations are
     available and both are checked: whether the repo owner's login looks like one of
     the authors, and whether the repo's own description or README names the paper.
  2. Anything weaker -- a URL with no release phrase, or several candidates with
     equal claim -- goes to the report for a human, never to Hugging Face.
  3. Papers where the text names no repo at all are listed too. Silence in a report
     reads as "covered", and most of these genuinely have no public code.

Decisions land in data/paper_code.yaml, committed and hand-editable, so a correction
outlives the run that made it and `--apply` stays idempotent. Nothing reaches Hugging
Face without `--apply`.

    python scripts/paper_code.py                # deduce, write the yaml, print a diff
    python scripts/paper_code.py --apply        # POST the accepted links to HF
    python scripts/paper_code.py --slug <slug>  # one paper, verbosely

HF's endpoint is POST /api/papers/{arxiv_id}/links, which the docs describe as taking
a "paper object ID"; the arXiv id is what works, and it is the only id any read
endpoint exposes. Writing needs a token whose user is a confirmed author on the paper.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA, ROOT, read_yaml, write_yaml  # noqa: E402

BUILD = os.path.join(ROOT, "build")
FULLTEXT = os.path.join(BUILD, "fulltext")
DECISIONS = os.path.join(DATA, "paper_code.yaml")
GH_CACHE = os.path.join(BUILD, "github_repos.json")

# A URL, and how much text before it we read for intent. 160 chars is about two lines
# of a footnote: long enough to catch "our code and data are publicly available at",
# short enough that the previous sentence's subject does not leak in.
URL_RX = re.compile(r"github\.com/([A-Za-z0-9][\w.-]*)/([\w.-]+)")
WINDOW = 160

# First person, and about *release*. "See github.com/x" and "built on github.com/y"
# deliberately do not match: the paper is pointing at someone else's work.
RELEASE_RX = re.compile(
    r"\b("
    r"our\s+(code|data|dataset|implementation|repo\w*|models?|artifacts?|benchmark)"
    r"|we\s+(release|publish|provide|open[-\s]?source|share|make)"
    r"|(code|data|dataset|implementation|models?|weights|benchmark|scripts?)"
    r"\s+(and\s+\w+\s+)?(is|are|can\s+be|will\s+be)?\s*"
    r"(publicly\s+|freely\s+)?(available|released|found|accessible)"
    r"|available\s+(at|from|on)\b"
    r"|released\s+(at|on|under)\b"
    r"|(code|data|repository|repo)\s*:"
    r")", re.I)

# The other half of intent: whose code it is. "Using their code from github.com/..."
# sits inside a release-shaped sentence ("we release ... for ease of reproducibility")
# and is exactly the repo you must not link -- it belongs to the paper being compared
# against. Checked close to the URL, where attribution actually happens.
CREDIT_RX = re.compile(
    r"\b(their|his|her|its)\s+(code|implementation|repo\w*|data|toolkit)"
    r"|\bcode\s+(from|of|by)\b"
    r"|\b(proposed|provided|released|introduced|published|developed|maintained)\s+by\b"
    r"|\b(based\s+on|built\s+on|adapted\s+from|taken\s+from|borrowed\s+from|fork\s+(at|of))\b"
    r"|\bwe\s+(use|used|adopt|adopted|follow|followed)\s+(the\s+)?"
    r"(code|implementation|toolkit|library|scripts?)\b", re.I)
CREDIT_WINDOW = 90

# Trailing junk that ends up glued to a URL by PDF and HTML extraction alike.
STRIP_RX = re.compile(r"[.,;:)\]}>'\"]+$")
SKIP_OWNERS = {
    # Hosts of tools every paper in this corpus uses. None of these is ever the
    # paper's own repo, and each appears in a footnote that reads like a release
    # sentence ("our scripts are based on ...").
    "huggingface", "eleutherai", "pytorch", "tensorflow", "google", "google-research",
    "facebookresearch", "openai", "microsoft", "nvidia", "scikit-learn", "numpy",
    "pandas-dev", "allenai", "bigscience-workshop", "argilla-io", "explosion",
    "nltk", "stanfordnlp", "spacy-io", "keras-team", "apache", "kubernetes",
}
SKIP_NAMES = {"transformers", "datasets", "tokenizers", "peft", "trl", "accelerate",
              "lm-evaluation-harness", "evaluate", "diffusers"}


def gh_json(path: str) -> dict | None:
    """One GitHub API read through `gh`, so it inherits the user's rate limit."""
    try:
        out = subprocess.run(["gh", "api", path], capture_output=True, text=True,
                             timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if out.returncode != 0:
        return None
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError:
        return None


class RepoFacts:
    """GitHub's answer about one `owner/name`, cached across runs."""

    def __init__(self) -> None:
        self.cache: dict = {}
        if os.path.exists(GH_CACHE):
            try:
                self.cache = json.load(open(GH_CACHE))
            except (json.JSONDecodeError, OSError):
                self.cache = {}

    def save(self) -> None:
        os.makedirs(BUILD, exist_ok=True)
        json.dump(self.cache, open(GH_CACHE, "w"), indent=1, sort_keys=True)

    def get(self, full: str) -> dict:
        if full in self.cache:
            return self.cache[full]
        d = gh_json(f"repos/{full}")
        if d is None:
            fact = {"exists": False}
        else:
            # The README is the other half of the bidirectional check: a repo that
            # names the paper is not a coincidence. Base64 costs nothing to skip --
            # `gh api` renders the raw file when asked for the HTML media type, but
            # the description alone is often enough, so only fetch when needed.
            fact = {"exists": True,
                    "full_name": d.get("full_name") or full,
                    "description": d.get("description") or "",
                    "homepage": d.get("homepage") or "",
                    "stars": d.get("stargazers_count") or 0,
                    "fork": bool(d.get("fork")),
                    "archived": bool(d.get("archived")),
                    # `gh` reads as you, so a repo you collaborate on answers 200 and
                    # looks public from here. Hugging Face -- and every reader -- gets
                    # a 404, and its API rejects the link outright.
                    "private": bool(d.get("private")),
                    "topics": d.get("topics") or []}
        self.cache[full] = fact
        return fact

    def readme(self, full: str) -> str:
        key = f"readme:{full}"
        if key in self.cache:
            return self.cache[key]
        d = gh_json(f"repos/{full}/readme")
        text = ""
        if d and d.get("content"):
            import base64
            try:
                text = base64.b64decode(d["content"]).decode("utf-8", "replace")
            except Exception:
                text = ""
        self.cache[key] = text[:20000]
        return self.cache[key]


def name_tokens(s: str) -> set[str]:
    return {w for w in re.split(r"[^a-z0-9]+", (s or "").lower()) if len(w) > 2}


def author_logins(authors: list[str]) -> set[str]:
    """Fragments of an author's name that a GitHub login plausibly contains."""
    out: set[str] = set()
    for a in authors or []:
        parts = [re.sub(r"[^a-z]", "", p.lower()) for p in str(a).split()]
        parts = [p for p in parts if len(p) > 2]
        out |= set(parts)
        if len(parts) >= 2:
            out.add(parts[0] + parts[-1])
            out.add(parts[0][0] + parts[-1])
            out.add(parts[-1] + parts[0][0])
    return out


def candidates(paper: dict, text: str) -> list[dict]:
    """Every github.com/owner/name in the text, scored for being *this paper's*."""
    title_toks = name_tokens(paper.get("title_display") or paper.get("title"))
    logins = author_logins(paper.get("authors"))
    n = max(len(text), 1)
    found: dict[str, dict] = {}
    for m in URL_RX.finditer(text):
        owner, name = m.group(1), STRIP_RX.sub("", m.group(2))
        if name.endswith(".git"):
            name = name[:-4]
        if not name or owner.lower() in SKIP_OWNERS or name.lower() in SKIP_NAMES:
            continue
        full = f"{owner}/{name}"
        pos = m.start()
        before = text[max(0, pos - WINDOW):pos]
        c = found.setdefault(full, {"repo": full, "hits": 0, "release": False,
                                    "first_pos": pos / n, "why": []})
        c["hits"] += 1
        credited = CREDIT_RX.search(text[max(0, pos - CREDIT_WINDOW):pos])
        if credited:
            c["credited_elsewhere"] = credited.group(0)
        elif RELEASE_RX.search(before):
            if not c["release"]:
                c["why"].append("release phrase: ..." + " ".join(before.split())[-70:])
            c["release"] = True
        c["first_pos"] = min(c["first_pos"], pos / n)

    for c in found.values():
        owner, name = c["repo"].split("/", 1)
        score = 0
        if c["release"]:
            score += 4
        # An owner login that looks like an author, or like you.
        ol = owner.lower()
        if ol == "borgr" or any(t and t in ol for t in logins if len(t) > 3):
            score += 2
            c["why"].append(f"owner {owner} matches an author name")
        # A repo named after the paper -- its title words, or the artifact it coined.
        nt = name_tokens(name)
        if nt & title_toks:
            score += 2
            c["why"].append(f"repo name shares '{'/'.join(sorted(nt & title_toks))}' "
                            f"with the title")
        if c["first_pos"] < 0.20:
            score += 1
            c["why"].append(f"appears {c['first_pos']:.0%} into the text")
        if c["hits"] > 2:
            score += 1
        if c["first_pos"] > 0.85 and not c["release"]:
            score -= 3
            c["why"].append("late in the text with no release phrase (bibliography?)")
        if c.get("credited_elsewhere"):
            score -= 3
            c["why"].append(f"text credits it to someone else: "
                            f"'{c['credited_elsewhere']}'")
        c["score"] = score
    return sorted(found.values(), key=lambda c: -c["score"])


def confirm(c: dict, paper: dict, facts: RepoFacts) -> dict:
    """Ask GitHub whether the repo exists and whether it points back at the paper."""
    f = facts.get(c["repo"])
    c["exists"] = f.get("exists", False)
    if not c["exists"]:
        c["why"].append("GitHub 404 -- rejected")
        c["score"] -= 10
        return c
    if f.get("private"):
        c["exists"] = False
        c["private"] = True
        c["why"].append("repo is private -- readers get a 404 and HF rejects the link")
        c["score"] -= 10
        return c
    c["stars"] = f.get("stars", 0)
    c["fork"] = f.get("fork", False)
    # The repo's own metadata naming the paper is the strongest single confirmation,
    # because it cannot happen by accident.
    title = (paper.get("title_display") or paper.get("title") or "").lower()
    title_key = " ".join(re.sub(r"[^a-z0-9 ]", " ", title).split()[:5])
    hay = (f.get("description", "") + " " + f.get("homepage", "") + " "
           + " ".join(f.get("topics", []))).lower()
    if title_key and title_key in hay:
        c["score"] += 3
        c["why"].append("repo description names the paper")
    elif paper.get("arxiv") and paper["arxiv"] in hay:
        c["score"] += 3
        c["why"].append("repo description cites the arXiv id")
    else:
        rd = facts.readme(c["repo"]).lower()
        if title_key and title_key in rd:
            c["score"] += 3
            c["why"].append("README names the paper")
        elif paper.get("arxiv") and paper["arxiv"] in rd:
            c["score"] += 3
            c["why"].append("README cites the arXiv id")
    if c.get("fork"):
        c["score"] -= 1
        c["why"].append("is a fork")
    return c


ACCEPT = 6   # release phrase (4) plus any one corroboration, or two corroborations.


def deduce(papers: list[dict], only: str | None, facts: RepoFacts) -> dict:
    out = {}
    for p in papers:
        if only and p["slug"] != only:
            continue
        path = os.path.join(FULLTEXT, p["slug"] + ".txt")
        text = ""
        if os.path.exists(path) and os.path.getsize(path) > 0:
            text = open(path, errors="replace").read()
        # The abstract is worth appending even when the full text is present: the
        # extractor sometimes drops the abstract block, and that is where the release
        # sentence usually lives.
        text = (p.get("abstract") or "") + "\n" + str(p.get("arxiv_comment") or "") \
            + "\n" + text
        cands = candidates(p, text)
        for c in cands[:4]:
            confirm(c, p, facts)
        cands.sort(key=lambda c: -c["score"])
        top = cands[0] if cands else None
        verdict = "none"
        if top and top["score"] >= ACCEPT and top.get("exists"):
            runner = cands[1]["score"] if len(cands) > 1 else -99
            # A paper that released two things named two repos, and which of them is
            # *the* code link is a judgment call about what a reader wants first --
            # the BabyLM findings paper released a dataset preprocessor, an evaluation
            # pipeline and a submissions archive. Deciding that by score would be
            # guessing with a number attached.
            # Two tells for "more than one repo": two release sentences, or two live
            # repos under the same owner. The second catches the case the first misses
            # -- the BabyLM findings paper names four `babylm/*` repos and writes a
            # release sentence for only one of them, which is not a reason to believe
            # that one is the link a reader wants first.
            owners: dict[str, int] = {}
            for c in cands:
                if c.get("exists") and c["score"] >= 0:
                    owners[c["repo"].split("/")[0]] = \
                        owners.get(c["repo"].split("/")[0], 0) + 1
            multi = (sum(1 for c in cands if c.get("release") and c.get("exists")) > 1
                     or owners.get(top["repo"].split("/")[0], 0) > 1)
            verdict = "accept" if top["score"] - runner >= 2 and not multi else "review"
            if multi:
                top["why"].append("the paper releases more than one repo -- "
                                  "which is the code link is yours to pick")
        elif top and top.get("exists") and top["score"] > 0:
            verdict = "review"
        out[p["slug"]] = {"paper": p, "verdict": verdict, "cands": cands}
    return out


def load_decisions() -> dict:
    d = read_yaml(DECISIONS) or {}
    return d.get("papers") or {}


def save_decisions(papers: list[dict], results: dict, prev: dict) -> None:
    """Write data/paper_code.yaml, preserving anything marked reviewed by hand."""
    rows = {}
    for slug, r in results.items():
        keep = prev.get(slug) or {}
        if keep.get("reviewed"):
            rows[slug] = keep
            continue
        top = r["cands"][0] if r["cands"] else None
        row = {"verdict": r["verdict"]}
        if top and r["verdict"] in ("accept", "review"):
            row["repo"] = "https://github.com/" + top["repo"]
            row["score"] = top["score"]
            row["why"] = top["why"][:4]
        if r["verdict"] == "review" and len(r["cands"]) > 1:
            row["other_candidates"] = ["https://github.com/" + c["repo"]
                                       for c in r["cands"][1:4] if c.get("exists")]
        if keep.get("repo") and keep.get("repo") != row.get("repo"):
            row["was"] = keep["repo"]
        rows[slug] = row
    for slug, keep in prev.items():           # never drop a hand decision
        rows.setdefault(slug, keep)
    write_yaml(DECISIONS, {
        "generated_by": "scripts/paper_code.py -- `reviewed: true` freezes a row",
        "note": "verdict: accept = pushed to HF by --apply. review = needs your eyes. "
                "none = the paper names no repo of its own.",
        "papers": dict(sorted(rows.items())),
    })


def hf_token() -> str | None:
    for env in ("HF_TOKEN", "HUGGINGFACE_HUB_TOKEN"):
        if os.environ.get(env):
            return os.environ[env]
    path = os.path.expanduser("~/.cache/huggingface/token")
    if os.path.exists(path):
        t = open(path).read().strip()
        return t or None
    return None


def hf_get(arxiv: str) -> dict | None:
    try:
        with urllib.request.urlopen(
                f"https://huggingface.co/api/papers/{arxiv}", timeout=30) as r:
            return json.load(r)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return None


def hf_put_links(arxiv: str, repo: str, keep_project: str | None, token: str) -> str:
    """POST the repo link. `projectPage` is echoed back deliberately -- the field is
    nullable and omitting it may clear it, which would trade one link for another."""
    body = {"githubRepo": repo}
    if keep_project:
        body["projectPage"] = keep_project
    req = urllib.request.Request(
        f"https://huggingface.co/api/papers/{arxiv}/links",
        data=json.dumps(body).encode(), method="POST",
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return f"ok {r.status}"
    except urllib.error.HTTPError as e:
        return f"HTTP {e.code} {e.read()[:200].decode('utf-8', 'replace')}"
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return f"error {e}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="POST accepted links to Hugging Face")
    ap.add_argument("--slug", help="one paper only")
    ap.add_argument("--include-review", action="store_true",
                    help="with --apply, also push rows a human marked reviewed")
    args = ap.parse_args()

    papers = (read_yaml(os.path.join(DATA, "papers.yaml")) or {}).get("papers") or []
    facts = RepoFacts()
    prev = load_decisions()
    results = deduce(papers, args.slug, facts)
    facts.save()

    acc = [(s, r) for s, r in results.items() if r["verdict"] == "accept"]
    rev = [(s, r) for s, r in results.items() if r["verdict"] == "review"]
    non = [(s, r) for s, r in results.items() if r["verdict"] == "none"]

    def line(slug, r):
        p, top = r["paper"], (r["cands"][0] if r["cands"] else None)
        have = (p.get("hf_github_repo") or "").lower()
        mark = "=" if have and top and have.endswith(top["repo"].lower()) else " "
        return (f"{mark} {p.get('citations') or 0:>4} cites  {slug[:52]:<52} "
                f"{'https://github.com/' + top['repo'] if top else '-':<52} "
                f"score {top['score'] if top else 0}")

    print(f"== accept ({len(acc)})  -- release phrase plus corroboration")
    for s, r in sorted(acc, key=lambda x: -(x[1]["paper"].get("citations") or 0)):
        print(line(s, r))
    print(f"\n== review ({len(rev)})  -- your call, never pushed")
    for s, r in sorted(rev, key=lambda x: -(x[1]["paper"].get("citations") or 0)):
        print(line(s, r))
        for c in r["cands"][1:3]:
            if c.get("exists"):
                print(f"{'':>64}alt https://github.com/{c['repo']} (score {c['score']})")
    priv = [(s, r) for s, r in results.items()
            if any(c.get("private") for c in r["cands"])]
    if priv:
        print(f"\n== names a private repo ({len(priv)})  -- make it public and rerun")
        for s, r in priv:
            for c in r["cands"]:
                if c.get("private"):
                    print(f"  {s[:52]:<52} https://github.com/{c['repo']}")

    print(f"\n== no repo named in the text ({len(non)})")
    for s, r in sorted(non, key=lambda x: -(x[1]["paper"].get("citations") or 0))[:12]:
        print(f"  {r['paper'].get('citations') or 0:>4} cites  {s}")
    if len(non) > 12:
        print(f"  ... and {len(non) - 12} more")

    save_decisions(papers, results, prev)
    print(f"\nwrote {os.path.relpath(DECISIONS, ROOT)}")

    if not args.apply:
        print("\nNothing has left this machine. To publish the accepted links:")
        print("  python scripts/paper_code.py --apply")
        return

    token = hf_token()
    if not token:
        sys.exit("no HF token: set HF_TOKEN or log in with `hf auth login`")
    pushed = skipped = failed = 0
    todo = list(acc)
    if args.include_review:
        todo += [(s, r) for s, r in rev if (prev.get(s) or {}).get("reviewed")]
    for slug, r in todo:
        p, top = r["paper"], r["cands"][0]
        if not p.get("arxiv"):
            continue
        url = "https://github.com/" + top["repo"]
        live = hf_get(p["arxiv"]) or {}
        # HF lowercases the URL it stores, so a case-sensitive comparison re-POSTs a
        # link that is already there and gets a 409 back.
        if (live.get("githubRepo") or "").rstrip("/").lower() == url.rstrip("/").lower():
            skipped += 1
            continue
        res = hf_put_links(p["arxiv"], url, live.get("projectPage"), token)
        # 409 is HF saying the link is already there -- the same outcome as a skip, not
        # a failure. It happens when its stored URL differs only in case.
        if "already linked to this paper" in res:
            skipped += 1
            continue
        ok = res.startswith("ok")
        pushed += ok
        failed += not ok
        print(f"{'->' if ok else '!!'} {p['arxiv']:<12} {url:<52} {res}")
        time.sleep(0.5)
    print(f"\npushed {pushed}, already correct {skipped}, failed {failed}")


if __name__ == "__main__":
    main()
