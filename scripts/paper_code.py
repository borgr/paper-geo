"""Deduce each paper's own code repo and project page, and publish both to HF.

The site renders `links.code`, which Hugging Face's `githubRepo` filled on 19 of 105 arXiv
papers. Every other paper's repo is in its own full text, in first person ("we release our
code at") -- and that phrasing is what separates the paper's own repo from the ten it cites,
since `huggingface/transformers` appears in a BabyLM footnote too.

Three passes, and only the first may decide on its own:

  1. `github.com/...` in the full text with a first-person release phrase in front of it,
     confirmed by GitHub returning 200. Two corroborations are also checked: the repo
     owner's login against the author list, and the description or README against the
     paper title.
  2. Anything weaker -- no release phrase, or several equal candidates -- goes to the
     report for a human, never to Hugging Face.
  3. Papers whose text names no repo are listed too, since silence in a report reads as
     "covered".

`projectPage` is deduced the same way, for papers whose artifact is a website, leaderboard
or dataset viewer. There is no `gh api` for the open web, so confirmation is the page
itself: reachable, and naming the paper. The two decisions are independent.

Two classes of URL are dropped before scoring, because both would score like the real repo:
a double-blind review mirror (`anonymous.4open.science/r/...`), which is deleted after
review, and the arXiv/venue/licence links every paper carries. See ANON_RX and
PAGE_SKIP_HOSTS.

Decisions land in data/paper_code.yaml, committed and hand-editable, so `--apply` stays
idempotent. `reviewed: true` freezes a row *and* makes its `repo`/`project_page` the URLs
that get pushed, so a hand-written link wins and deleting the key means "no link, on
purpose". Nothing reaches Hugging Face without `--apply`.

    python scripts/paper_code.py                # deduce, write the yaml, print a diff
    python scripts/paper_code.py --apply        # POST the accepted links to HF
    python scripts/paper_code.py --slug <slug>  # one paper, verbosely

HF's endpoint is POST /api/papers/{arxiv_id}/links -- the arXiv id is the "paper object ID"
that works, and the only id any read endpoint exposes. Writing needs a token whose user is a
confirmed author on the paper.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (DATA, ROOT, gh, gh_status, load_config, note_fetch,  # noqa: E402
                    read_yaml, write_json, write_yaml)
from fulltext import resolve as resolve_fulltext  # noqa: E402

BUILD = os.path.join(ROOT, "build")
FULLTEXT = os.path.join(BUILD, "fulltext")
DECISIONS = os.path.join(DATA, "paper_code.yaml")
GH_CACHE = os.path.join(BUILD, "github_repos.json")
# Why each row came out the way it did: the score and the reasons behind it. Derived,
# regenerated every run, and therefore not in the committed decision file -- see
# save_decisions.
WHY = os.path.join(BUILD, "paper_code_why.json")

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

# A URL a paper published *for review*, not for readers. Under double-blind these are the
# release sentence's whole content ("our code is available at anonymous.4open.science/r/
# xyz"), so they score exactly like the real thing while being certain to be wrong: the
# mirror is deleted after the review cycle. The camera-ready names the real repo; if the
# extracted text predates it, no link is the correct answer.
ANON_RX = re.compile(r"anonymous|4open\.science|double[-\s]?blind|anon\.github", re.I)

# ---- project pages -----------------------------------------------------------------
# The other link HF stores, and it matters for a different reason than the repo: a paper
# whose artifact is a website, a leaderboard or a dataset viewer has no repo worth
# linking, and the page is where a reader who believes the result goes.
#
# There is no `gh api` for the open web, so the confirmation is the page itself -- fetch
# it and require that it names the paper. A stronger check than the repo path gets, and it
# has to be, because the candidate space is every URL in the document.
PAGE_CACHE = os.path.join(BUILD, "project_pages.json")
PAGE_RX = re.compile(r"https?://([\w.-]+\.[a-z]{2,})(/[^\s)\]}>,;\"'\\]*)?", re.I)

# Hosts every paper in the corpus links to no matter what it released: the paper's own
# identity records, the venue, the tools, the licence boilerplate. None is ever a
# project page, and each sits inside sentences that read like release sentences.
PAGE_SKIP_HOSTS = (
    "arxiv.org", "doi.org", "aclanthology.org", "openreview.net", "semanticscholar.org",
    "ssrn.com", "springer", "sciencedirect", "elsevier", "nature.com", "acm.org",
    "ieee.org", "wiley", "jstor", "biorxiv", "researchgate", "academia.edu",
    "github.com", "gitlab", "bitbucket", "sourceforge",
    "wandb.ai", "colab.research.google.com", "drive.google.com", "docs.google.com",
    "forms.gle", "forms.office", "twitter.com", "x.com", "linkedin", "youtube",
    "youtu.be", "reddit.com", "discord", "slack.com",
    "wikipedia.org", "wikimedia", "creativecommons.org", "gnu.org", "opensource.org",
    "ctan.org", "latex-project", "tug.org", "stackoverflow", "stackexchange",
    "orcid.org", "zenodo.org", "figshare", "dataverse", "osf.io",
    "python.org", "pypi.org", "pytorch.org", "tensorflow.org", "numpy.org",
    "scipy.org", "matplotlib.org", "w3.org", "schema.org", "json-schema.org",
    "apache.org", "readthedocs", "npmjs", "docker.com", "archive.org", "web.archive",
    "openai.com", "anthropic.com", "google.com", "microsoft.com", "nvidia.com",
    "meta.com", "cloud.google", "aws.amazon", "azure",
    # Shorteners. Even when one points at the paper's own page, the link HF would store
    # is a redirect owned by someone else that can rot or be repointed; the destination
    # is usually also named in the text, and that is the one to publish.
    "bit.ly", "tinyurl", "t.co", "goo.gl", "is.gd", "ow.ly", "shorturl", "rb.gy",
)

# Words that corroborate nothing. A URL "sharing a word with the title" is evidence
# only when the word is the paper's, so `unige.ch/.../research-material` matching on
# "and" has to not count.
STOP_TOKS = {"and", "the", "for", "with", "from", "using", "use", "via", "into", "over",
             "this", "that", "what", "when", "how", "why", "more", "than", "our", "all",
             "its", "can", "are", "not", "new", "based", "toward", "towards", "your",
             "their", "does", "was", "were", "but", "you", "his", "her", "who", "them",
             "paper", "study", "research", "www", "com", "org", "net", "http", "https",
             "html", "index", "page", "site", "home", "main", "docs", "doc", "info"}
# Hugging Face is both: `/datasets/x/y` and `/spaces/x/y` are exactly the kind of page
# this field is for, while `/papers/`, `/docs/` and `/blog/` are not the paper's own.
HF_PAGE_OK = ("/datasets/", "/spaces/", "/collections/")
HF_PAGE_NO = ("/papers/", "/docs/", "/blog/", "/learn/", "/models?", "/join", "/login")
# A path ending in a file extension is an asset the paper cites, not a page it built.
PAGE_FILE_RX = re.compile(
    r"\.(pdf|png|jpe?g|gif|svg|zip|t?gz|tar|csv|tsv|json|jsonl|ya?ml|bib|txt|xlsx?|"
    r"pptx?|docx?|mp4|wav|bin|ckpt|pt|h5)$", re.I)


class RepoFacts:
    """GitHub's answer about one `owner/name`, cached across runs.

    Only a definite answer is cached. See `get`.
    """

    def __init__(self) -> None:
        self.cache: dict = {}
        if os.path.exists(GH_CACHE):
            try:
                with open(GH_CACHE, encoding="utf-8") as fh:
                    self.cache = json.load(fh)
            except (json.JSONDecodeError, OSError):
                self.cache = {}
        # An entry written before this file told a 404 apart from a refusal is dropped
        # rather than trusted, since a poisoned one is indistinguishable from an honest one
        # and re-asking costs a single call. Repo facts gained `status` and READMEs became a
        # dict, so an entry still in the old shape is exactly the one to drop.
        self.cache = {k: v for k, v in self.cache.items() if isinstance(v, dict)
                      and (k.startswith("readme:") or v.get("exists") or "status" in v)}

    def save(self) -> None:
        write_json(GH_CACHE, self.cache, indent=1, sort_keys=True)

    def get(self, full: str) -> dict:
        """`{exists, status, ...}` for one repo, from the cache when it is there.

        A refusal is not cached, so the next run asks again. Caching one would drop the
        paper's code link for good, since the cache is consulted before GitHub is.
        """
        if full in self.cache:
            return self.cache[full]
        code, out = gh("api", f"repos/{full}")
        d = None
        if not code:
            try:
                d = json.loads(out)
            except json.JSONDecodeError:
                d = None
        st = 200 if d is not None else gh_status(out)
        note_fetch(f"https://api.github.com/repos/{full}", d is not None,
                   f"HTTP {st}" if st else "no reply")
        if d is None:
            fact = {"exists": False, "status": st}
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
                    "topics": d.get("topics") or [], "status": 200}
        # A rate limit, an expired token and a dropped connection all leave `gh` with
        # nothing to parse, and 404 is the only status that means the repo is not there.
        if st in (200, 404, 410):
            self.cache[full] = fact
        return fact

    def readme(self, full: str) -> str:
        """The repo's README, or "". Same caching rule as `get`.

        The README is the back-link corroboration, so caching a refusal as "no README"
        would hold the candidate at `review` for ever.
        """
        key = f"readme:{full}"
        hit = self.cache.get(key)
        if isinstance(hit, dict):
            return hit["text"]
        code, out = gh("api", f"repos/{full}/readme")
        d = None
        if not code:
            try:
                d = json.loads(out)
            except json.JSONDecodeError:
                d = None
        text = ""
        if d and d.get("content"):
            try:
                text = base64.b64decode(d["content"]).decode("utf-8", "replace")
            except (ValueError, binascii.Error):
                text = ""
        text = text[:20000]
        if d is not None or gh_status(out) in (404, 410):
            self.cache[key] = {"text": text}
        return text


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
        if ANON_RX.search(owner) or ANON_RX.search(name):
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


class PageFacts:
    """What one URL answers, cached across runs. Same contract as `RepoFacts`."""

    def __init__(self) -> None:
        self.cache: dict = {}
        if os.path.exists(PAGE_CACHE):
            try:
                with open(PAGE_CACHE, encoding="utf-8") as fh:
                    self.cache = json.load(fh)
            except (json.JSONDecodeError, OSError):
                self.cache = {}

    def save(self) -> None:
        write_json(PAGE_CACHE, self.cache, indent=1, sort_keys=True)

    def get(self, url: str) -> dict:
        if url in self.cache:
            return self.cache[url]
        fact = {"exists": False, "text": ""}
        req = urllib.request.Request(url, headers={
            # Two of these hosts serve a bot-check to the default urllib agent. A
            # normal browser string is not evasion here: it is a public page whose
            # own paper asks readers to visit it.
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"})
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                fact = {"exists": 200 <= r.status < 300, "status": r.status,
                        "final": r.geturl(),
                        "text": r.read(400_000).decode("utf-8", "replace")}
        except urllib.error.HTTPError as e:
            fact = {"exists": False, "status": e.code, "text": ""}
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
            fact = {"exists": False, "status": str(e)[:80], "text": ""}
        # The body is only ever read for the title check, so keep a stripped copy
        # rather than 400KB of markup in a cache that is committed to nothing but is
        # read on every rerun.
        fact["text"] = " ".join(re.sub(r"<[^>]+>", " ", fact["text"]).split()).lower()[:20000]
        # Only a definite answer is cached. A 404 or a 403 is the server speaking and
        # will say the same thing tomorrow; a timeout or a DNS failure is this machine's
        # afternoon, and caching it turns one bad moment into "that project page does
        # not exist", permanently, with no run ever asking again. Three of the 103 probes
        # in this cache were exactly that, one of them a page that is plainly up.
        definite = isinstance(fact.get("status"), int) and fact["status"] < 500
        # Deliberately not recorded in the health ledger. These URLs are lifted out of paper
        # full text, so "does it resolve" is the question being asked, not a precondition for
        # asking it -- a 404 is this probe succeeding. Recorded, one paper's `iclrgithub.io`
        # typo becomes a permanent ledger line reading "never once answered", and `source_key`
        # cannot collapse a hostname, so every mangled URL earns its own line forever. The
        # GitHub API this step also calls *is* a source and is still recorded, below.
        if definite:
            self.cache[url] = fact
        return fact


def page_candidates(paper: dict, text: str, repo_url: str | None) -> list[dict]:
    """Every plausible project-page URL in the text, scored for being this paper's."""
    title_toks = name_tokens(paper.get("title_display") or paper.get("title"))
    n = max(len(text), 1)
    found: dict[str, dict] = {}
    for m in PAGE_RX.finditer(text):
        host, path = m.group(1).lower(), STRIP_RX.sub("", m.group(2) or "")
        url = f"https://{host}{path}"
        if any(h in host for h in PAGE_SKIP_HOSTS) or ANON_RX.search(url):
            continue
        if "huggingface.co" in host and not (
                any(p in path for p in HF_PAGE_OK)
                and not any(p in path for p in HF_PAGE_NO)):
            continue
        if PAGE_FILE_RX.search(path) or len(path) > 120:
            continue
        if repo_url and url.rstrip("/").lower() == repo_url.rstrip("/").lower():
            continue
        pos = m.start()
        before = text[max(0, pos - WINDOW):pos]
        c = found.setdefault(url, {"page": url, "hits": 0, "release": False,
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
        score = 4 if c["release"] else 0
        # A host or path built out of the paper's own words -- `rl-calibration.github.io`
        # for a calibration paper. This is where a project page most resembles a repo
        # named after the paper, and it is the corroboration that survives a site whose
        # landing page is a single JS bundle with no readable text.
        toks = name_tokens(c["page"].replace("/", " ").replace(".", " ")) - STOP_TOKS
        shared = toks & title_toks
        # Either signal means the text is making a claim about this URL. Neither means
        # the paper simply cited a site -- spacy.io, a Kaggle dataset it trained on, the
        # BNC's homepage. Those are not project-page candidates at any score, and left
        # in they turn the review list into something no one reads.
        c["own"] = bool(c["release"] or shared)
        if shared:
            score += 2
            c["why"].append(f"URL shares '{'/'.join(sorted(shared))}' with the title")
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
    return sorted([c for c in found.values() if c["own"]], key=lambda c: -c["score"])


HF_SIB_RX = re.compile(r"huggingface\.co/(datasets|spaces)/([^/]+)/([^/?#]+)", re.I)


def hf_siblings(url: str, title_toks: set[str]) -> tuple[list[str], str]:
    """Other datasets or spaces by the same owner that also look like this paper's.

    Returns (siblings, refusal), where the refusal is "" when Hugging Face answered. An
    owner who publishes nothing else and an index that would not load both come back with
    no siblings, and only the first one means the page is unambiguous.

    Global PIQA released a parallel split and a non-parallel one, as two dataset repos;
    the extracted text names one. Picking that one as *the* project page would publish a
    subset as the whole, and the text cannot settle it because the other name is not in
    the text. The owner's index is, so ask that instead. Same shape as the repo path's
    "the paper releases more than one repo" rule: not resolved by a score, deferred.
    """
    m = HF_SIB_RX.search(url)
    if not m:
        return [], ""
    kind, owner, name = m.group(1), m.group(2), m.group(3)
    api = f"https://huggingface.co/api/{kind}?author={owner}&limit=200"
    try:
        with urllib.request.urlopen(api, timeout=25) as r:
            items = json.load(r)
        note_fetch(api, True)
    except urllib.error.HTTPError as e:
        # No 404 exemption here, unlike the per-repo reads. This endpoint answers `[]` for
        # an owner it has never heard of, so any status at all is the endpoint not working.
        note_fetch(api, False)
        return [], f"HTTP {e.code}"
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        note_fetch(api, False)
        return [], "no reply"
    # A sibling has to be a variant of *this* artifact, not just another dataset the
    # owner happens to publish -- `commoncrawl` publishes dozens, and matching on a
    # title word alone makes every one of them look like a competing project page.
    # Sharing a word with the accepted name is what distinguishes `global-piqa-parallel`
    # from `global-piqa-nonparallel`.
    own = name_tokens(name.replace("-", " ").replace("_", " ")) - STOP_TOKS
    out = []
    for it in items if isinstance(items, list) else []:
        rid = it.get("id") or ""
        short = rid.split("/")[-1]
        if short.lower() == name.lower():
            continue
        toks = name_tokens(short.replace("-", " ").replace("_", " ")) - STOP_TOKS
        if toks & title_toks and toks & own:
            out.append(f"https://huggingface.co/{kind}/{rid}")
    return out, ""


def confirm_page(c: dict, paper: dict, pages: PageFacts) -> dict:
    """Fetch the page and ask whether it names the paper."""
    f = pages.get(c["page"])
    c["exists"] = bool(f.get("exists"))
    if not c["exists"]:
        c["why"].append(f"unreachable ({f.get('status')}) -- rejected")
        c["score"] -= 10
        return c
    title = (paper.get("title_display") or paper.get("title") or "").lower()
    title_key = " ".join(re.sub(r"[^a-z0-9 ]", " ", title).split()[:5])
    body = f.get("text") or ""
    if title_key and title_key in body:
        c["score"] += 3
        c["why"].append("the page names the paper")
    elif paper.get("arxiv") and paper["arxiv"] in body:
        c["score"] += 3
        c["why"].append("the page cites the arXiv id")
    elif len(body) < 200:
        # A page that renders its content with JS answers 200 with nothing in it. That
        # is not evidence against, but it is not the confirmation either, so it goes to
        # review rather than being accepted on the release phrase alone.
        c["why"].append("page has no readable text (client-rendered?) -- unconfirmed")
    return c


def confirm(c: dict, paper: dict, facts: RepoFacts) -> dict:
    """Ask GitHub whether the repo exists and whether it points back at the paper."""
    f = facts.get(c["repo"])
    c["exists"] = f.get("exists", False)
    if not c["exists"]:
        # A repo GitHub says is gone and a repo GitHub would not talk about are both
        # unconfirmed, so neither is accepted. Only the first is a reason to stop looking,
        # and saying "404" for the second sends the reader to delete a working link.
        st = f.get("status")
        c["why"].append("GitHub 404 -- rejected" if st in (404, 410, None) else
                        f"GitHub would not answer (HTTP {st or 'no reply'}) -- "
                        "retried next run")
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


def deduce(papers: list[dict], only: str | None, facts: RepoFacts,
           pages: PageFacts) -> dict:
    cfg = load_config()
    out = {}
    for p in papers:
        if only and p["slug"] != only:
            continue
        path = os.path.join(FULLTEXT, p["slug"] + ".txt")
        text = ""
        if os.path.exists(path) and os.path.getsize(path) > 0:
            text = open(path, errors="replace").read()
        else:
            # Fetch it rather than fall back to the abstract. The cache is filled by the
            # drafting step, which is batched by citations, so a paper published last
            # week is the last one it reaches -- and a new paper is exactly the case
            # where nobody has linked the repo yet. Cached after the first fetch, so
            # this costs one request per paper, once, ever.
            try:
                text, _ = resolve_fulltext(p, cfg)
            except Exception as e:                      # noqa: BLE001
                print(f"  ({p['slug']}: no full text -- {e})", file=sys.stderr)
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
            # Which of two released repos is *the* code link is a judgment call about what a
            # reader wants first -- the BabyLM findings paper released a preprocessor, an
            # evaluation pipeline and a submissions archive. Deciding it by score is guessing
            # with a number attached, so two repos means review.
            #
            # Two tells: two release sentences, or two live repos under one owner. The second
            # catches what the first misses -- BabyLM names four `babylm/*` repos and writes a
            # release sentence for one of them.
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
        # The project page is decided the same way and independently: a paper can have
        # a page and no repo, which is most of the reason this half exists.
        repo_url = ("https://github.com/" + top["repo"]) if top else None
        pc = page_candidates(p, text, repo_url)
        for c in pc[:3]:
            confirm_page(c, p, pages)
        pc.sort(key=lambda c: -c["score"])
        ptop = pc[0] if pc else None
        pverdict = "none"
        if ptop and ptop.get("exists") and ptop["score"] >= ACCEPT:
            prunner = pc[1]["score"] if len(pc) > 1 else -99
            sibs, quiet = hf_siblings(
                ptop["page"], name_tokens(p.get("title_display") or p.get("title")))
            if sibs:
                ptop["siblings"] = sibs[:4]
                ptop["why"].append(f"the same owner publishes {len(sibs)} more for this "
                                   f"paper -- which is the page is yours to pick")
            elif quiet:
                # Held, because `--apply` POSTs an accepted page to Hugging Face and this
                # is the only check that a multi-part release is not being published as
                # one part of itself.
                ptop["why"].append(f"Hugging Face would not list the owner's other "
                                   f"releases ({quiet}) -- held, retried next run")
            pverdict = ("accept" if ptop["score"] - prunner >= 2 and not sibs and not quiet
                        else "review")
        elif ptop and ptop.get("exists") and ptop["score"] > 0:
            pverdict = "review"
        out[p["slug"]] = {"paper": p, "verdict": verdict, "cands": cands,
                          "page_verdict": pverdict, "pages": pc}
    return out


def effective(slug: str, r: dict, prev: dict) -> dict:
    """What this run actually stands behind for one paper, deduction and hand edit both.

    One function so the report and `--apply` cannot disagree: a row the author decided
    has to read as decided, not sit in "your call, never pushed" while `--apply` quietly
    publishes it. `frozen` is what makes the two verdicts mean different things -- a
    frozen `accept` is a person's judgment, an unfrozen one is this script's.
    """
    keep = prev.get(slug) or {}
    top = r["cands"][0] if r["cands"] else None
    ptop = r["pages"][0] if r["pages"] else None
    if keep.get("reviewed"):
        # The stored verdicts are authoritative, and the two fields are independent:
        # freezing a row to settle its project page must not also publish whatever repo
        # the deduction had left in `review`. Anything other than `accept` on a frozen
        # row is a decision not to publish, so it also drops out of the review list --
        # which is the point of freezing: a settled question stops being asked.
        return {"frozen": True,
                "verdict": "accept" if keep.get("verdict") == "accept"
                           and keep.get("repo") else "none",
                "repo": keep.get("repo") or None,
                "page_verdict": "accept" if keep.get("page_verdict") == "accept"
                                and keep.get("project_page") else "none",
                "page": keep.get("project_page") or None,
                # No score on a frozen row, either field: the number is this script's
                # confidence in its own deduction, and a person has overridden it. The
                # report prints the `*` instead, which is the fact that matters.
                "score": None, "pscore": None}
    return {"frozen": False,
            "verdict": r["verdict"],
            "repo": ("https://github.com/" + top["repo"]) if top else None,
            "page_verdict": r["page_verdict"],
            "page": ptop["page"] if ptop else None,
            "score": top["score"] if top else 0,
            "pscore": ptop["score"] if ptop else 0}


def load_decisions() -> dict:
    d = read_yaml(DECISIONS) or {}
    return d.get("papers") or {}


def save_decisions(papers: list[dict], results: dict, prev: dict) -> None:
    """Write data/paper_code.yaml, preserving anything marked reviewed by hand.

    The row is a decision -- which URL, and whether a person has settled it -- so `git log` on
    this file answers "what did we decide about this paper". `score` and `why` are the run's
    audit trail and churn whenever a README changes upstream, so they go to
    build/paper_code_why.json, regenerated with everything else in `build/` and still there when
    the report says "review" and you want to know why.
    """
    rows, why = {}, {}
    for slug, r in results.items():
        keep = prev.get(slug) or {}
        if keep.get("reviewed"):
            rows[slug] = {k: v for k, v in keep.items() if k not in ("score", "why",
                                                                     "page_why")}
            continue
        top = r["cands"][0] if r["cands"] else None
        row = {"verdict": r["verdict"]}
        if top and r["verdict"] in ("accept", "review"):
            row["repo"] = "https://github.com/" + top["repo"]
            why.setdefault(slug, {})["repo"] = {"score": top["score"],
                                                "why": top["why"][:4]}
        if r["verdict"] == "review" and len(r["cands"]) > 1:
            row["other_candidates"] = ["https://github.com/" + c["repo"]
                                       for c in r["cands"][1:4] if c.get("exists")]
        if keep.get("repo") and keep.get("repo") != row.get("repo"):
            row["was"] = keep["repo"]
        ptop = r["pages"][0] if r["pages"] else None
        if ptop and r["page_verdict"] in ("accept", "review"):
            row["page_verdict"] = r["page_verdict"]
            row["project_page"] = ptop["page"]
            why.setdefault(slug, {})["page"] = {"score": ptop["score"],
                                                "why": ptop["why"][:4]}
            if ptop.get("siblings"):
                row["other_pages"] = ptop["siblings"]
            elif r["page_verdict"] == "review" and len(r["pages"]) > 1:
                row["other_pages"] = [c["page"] for c in r["pages"][1:4]
                                      if c.get("exists")]
        rows[slug] = row
    for slug, keep in prev.items():           # never drop a hand decision
        rows.setdefault(slug, {k: v for k, v in keep.items()
                              if k not in ("score", "why", "page_why")})
    write_json(
        WHY,
        {"generated_by": "scripts/paper_code.py -- the audit trail behind "
                         "data/paper_code.yaml. Derived, so not committed.",
         "papers": dict(sorted(why.items()))}, indent=1)
    write_yaml(DECISIONS, {
        "generated_by": "scripts/paper_code.py -- `reviewed: true` freezes a row and "
                        "makes its `repo`/`project_page` the URLs --apply pushes, so a "
                        "hand-written one wins over anything deduced; delete the key to "
                        "mean 'no link, deliberately'",
        "note": "verdict: accept = pushed to HF by --apply. review = needs your eyes. "
                "none = the paper names no repo of its own. `page_verdict` and "
                "`project_page` are the same decision for HF's other link field, "
                "decided independently -- a paper can have a page and no repo. Why a "
                "row came out this way, with its score, is in "
                "build/paper_code_why.json: derived, rewritten every run, so this file "
                "stays a record of decisions rather than of readings.",
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


def hf_get(arxiv: str) -> tuple[dict | None, str]:
    """HF's record for one paper, or None, with a refusal that is "" when HF answered.

    A paper HF has not indexed comes back (None, ""). A paper it would not talk about
    comes back with the reason, and no caller may read that as a record carrying no
    links: the upvote counts and the existing githubRepo/projectPage links are here.
    """
    url = f"https://huggingface.co/api/papers/{arxiv}"
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            doc = json.load(r)
        note_fetch(url, True)
        return doc, ""
    except urllib.error.HTTPError as e:
        # A 404 is HF saying this paper is not indexed, which is a real answer about
        # this paper rather than a fault in the source. Counting it as a failure would
        # bury the host in failures the moment a run touches a few unindexed papers.
        note_fetch(url, e.code == 404)
        return None, "" if e.code == 404 else f"HTTP {e.code}"
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        note_fetch(url, False)
        return None, "no reply"


def hf_put_links(arxiv: str, repo: str | None, page: str | None, token: str) -> str:
    """POST both link fields. Whichever one is not being changed is echoed back from
    HF's live record deliberately -- both are nullable and omitting one may clear it,
    which would trade one link for the other."""
    body = {}
    if repo:
        body["githubRepo"] = repo
    if page:
        body["projectPage"] = page
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


def push(results: dict, eff: dict, token: str) -> None:
    """POST every accepted link to Hugging Face, one paper at a time.

    Reached only from `--apply`, so every line printed here is a public write.
    """
    pushed = skipped = failed = 0

    def wanted(slug: str, r: dict) -> tuple[str | None, str | None]:
        """The repo and page this run would publish for one paper, or None each.

        A row marked `reviewed: true` *is* the decision, so its own `repo` and
        `project_page` are what get pushed -- including a URL that appears nowhere in
        the deduction, which is the point: the right project page is often a site the
        paper mentions once and the detector ranks second. A frozen row with the key
        deleted means "deliberately no link", and nothing is pushed for it.
        """
        e = eff[slug]
        return (e["repo"] if e["verdict"] == "accept" else None,
                e["page"] if e["page_verdict"] == "accept" else None)

    def same(a: str | None, b: str | None) -> bool:
        # HF lowercases the URL it stores, so a case-sensitive comparison re-POSTs a
        # link that is already there and gets a 409 back.
        return bool(a) and (b or "").rstrip("/").lower() == a.rstrip("/").lower()

    no_arxiv, refused = [], []
    for slug, r in sorted(results.items(),
                          key=lambda x: -(x[1]["paper"].get("citations") or 0)):
        p = r["paper"]
        repo, page = wanted(slug, r)
        if not (repo or page):
            continue
        if not p.get("arxiv"):
            # HF's endpoint is keyed on the arXiv id, so there is no page to write to.
            # Say so rather than skipping quietly: the link is real and does reach the
            # site, which reads this file directly, and a silent skip reads as "no link".
            no_arxiv.append(slug)
            continue
        live, quiet = hf_get(p["arxiv"])
        if quiet:
            # Nothing is pushed. `hf_put_links` echoes back the field it is not changing
            # out of this record, because omitting one may clear it -- so a POST built on
            # a refused read is exactly how one link gets traded for the other.
            refused.append(f"{slug} ({quiet})")
            continue
        live = live or {}
        new_repo = repo if repo and not same(repo, live.get("githubRepo")) else None
        new_page = page if page and not same(page, live.get("projectPage")) else None
        if not (new_repo or new_page):
            skipped += 1
            continue
        res = hf_put_links(p["arxiv"],
                           new_repo or live.get("githubRepo"),
                           new_page or live.get("projectPage"), token)
        # 409 is HF saying the link is already there -- the same outcome as a skip, not
        # a failure. It happens when its stored URL differs only in case.
        if "already linked to this paper" in res:
            skipped += 1
            continue
        ok = res.startswith("ok")
        pushed += ok
        failed += not ok
        what = " + ".join(x for x in (new_repo and "repo", new_page and "page") if x)
        print(f"{'->' if ok else '!!'} {p['arxiv']:<12} {what:<11} "
              f"{(new_repo or new_page):<52} {res}")
        time.sleep(0.5)
    print(f"\npushed {pushed}, already correct {skipped}, failed {failed}")
    if refused:
        print(f"HF would not say what is already linked ({len(refused)}), so nothing was "
              f"pushed for them; retried next run: " + ", ".join(sorted(refused)))
    if no_arxiv:
        print(f"not on arXiv, so HF has no page to link ({len(no_arxiv)}); the link is "
              f"on the site: " + ", ".join(sorted(no_arxiv)))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="POST accepted links to Hugging Face")
    ap.add_argument("--slug", help="one paper only")
    args = ap.parse_args()

    papers = (read_yaml(os.path.join(DATA, "papers.yaml")) or {}).get("papers") or []
    facts = RepoFacts()
    pages = PageFacts()
    prev = load_decisions()
    results = deduce(papers, args.slug, facts, pages)
    facts.save()
    pages.save()

    eff = {s: effective(s, r, prev) for s, r in results.items()}
    acc = [(s, results[s]) for s, e in eff.items() if e["verdict"] == "accept"]
    rev = [(s, results[s]) for s, e in eff.items() if e["verdict"] == "review"]
    non = [(s, results[s]) for s, e in eff.items() if e["verdict"] == "none"]

    def line(slug, r):
        p, e = r["paper"], eff[slug]
        have = (p.get("hf_github_repo") or "").rstrip("/").lower()
        mark = "*" if e["frozen"] else (
            "=" if have and e["repo"] and e["repo"].lower().endswith(
                have.split("github.com/")[-1]) else " ")
        return (f"{mark} {p.get('citations') or 0:>4} cites  {slug[:52]:<52} "
                f"{e['repo'] or '-':<52} "
                f"{'your decision' if e['frozen'] else 'score ' + str(e['score'])}")

    # "will publish" is a description of what --apply would do, not a queue of things
    # waiting on the reader: nothing in this list needs them, and the ones marked '*' are
    # rows they already reviewed. Saying so is the difference between a settled list and
    # a 39-item chore.
    print(f"== will publish on --apply ({len(acc)})  -- nothing here needs you. "
          f"'*' = you already reviewed it,\n   the rest earned it with a release phrase "
          f"plus corroboration")
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

    pacc = [s for s, e in eff.items() if e["page_verdict"] == "accept"]
    prev_ = [s for s, e in eff.items() if e["page_verdict"] == "review"]
    cites = lambda s: -(results[s]["paper"].get("citations") or 0)  # noqa: E731
    print(f"\n== project page, will publish on --apply ({len(pacc)})  -- nothing here "
          f"needs you. '*' = you\n   already reviewed it, the rest reachable and naming "
          f"the paper")
    for s in sorted(pacc, key=cites):
        e = eff[s]
        print(f"{'*' if e['frozen'] else ' '} {-cites(s):>4} cites  {s[:52]:<52} "
              f"{e['page']:<52} "
              f"{'' if e['frozen'] else 'score ' + str(e['pscore'])}")
    print(f"\n== project page, review ({len(prev_)})  -- your call, never pushed")
    for s in sorted(prev_, key=cites):
        r = results[s]
        print(f"  {-cites(s):>4} cites  {s[:52]:<52} {eff[s]['page']:<52} "
              f"score {eff[s]['pscore']}")
        print(f"{'':>62}{'; '.join(r['pages'][0]['why'][:2])[:110]}")

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
    push(results, eff, token)


if __name__ == "__main__":
    main()
