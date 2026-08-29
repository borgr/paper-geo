"""Shared utilities: config loading, polite HTTP, BibTeX parsing, title matching.

Also `rules_block`, which is how the model-facing prompts get their rules: the docs
are the source, the scripts read them. See its docstring.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import time
import unicodedata
import urllib.error
import urllib.request

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
BUILD = os.path.join(ROOT, "build")
# Committed, unlike BUILD: these are the payloads a human works through over days,
# so they have to survive a clean checkout and be readable on the web.
TASKS = os.path.join(ROOT, "tasks")
# arXiv's API answers Atom, and every caller here needs both prefixes: `ar:` carries
# journal_ref and doi, which is most of what a run wants from arXiv.
ARXIV_NS = {"a": "http://www.w3.org/2005/Atom", "ar": "http://arxiv.org/schemas/atom"}
UA = {"User-Agent": "paper-geo/0.1 (+https://github.com/borgr/paper-geo)"}


def load_config(path: str | None = None) -> dict:
    """`config.yaml`, with one field the environment may override.

    `llm.mode` is `skill` (queue a JSON task file for an agent session to fill) or `api`
    (call Anthropic directly), and $PAPER_GEO_LLM_MODE overrides it so CI, which has no
    session to fill a task file, does not need a committed file edited.

    That one field only. A general env-overrides-config mechanism would invite putting a
    secret in `config.yaml` and overriding it there.
    """
    with open(path or os.path.join(ROOT, "config.yaml")) as f:
        cfg = yaml.safe_load(f)
    if (mode := os.environ.get("PAPER_GEO_LLM_MODE", "").strip()) in ("skill", "api"):
        cfg.setdefault("llm", {})["mode"] = mode
    return cfg


PROMPT_START = "<!-- prompt:start -->"
PROMPT_END = "<!-- prompt:end -->"
PROMPT_MIN = 400          # chars; below this the block is a stub, not a rule set


def rules_block(doc: str) -> str:
    """The rules a model is sent, read out of the doc that documents them.

    The text between the two markers is the only copy, so editing the doc changes what the
    model is told in the same commit. Raises rather than degrades, because a model given no
    rules still returns confident-looking JSON and the failure would surface only as slowly
    worsening drafts. `validate.py check_prompt_blocks` catches a missing marker earlier.
    """
    path = os.path.join(ROOT, doc)
    try:
        with open(path) as f:
            text = f.read()
    except OSError as e:
        raise RuntimeError(f"{doc} is the source of a model prompt and is unreadable: {e}")
    a = text.find(PROMPT_START)
    b = text.find(PROMPT_END, a + 1)
    if a < 0 or b < 0:
        raise RuntimeError(
            f"{doc} is missing its {PROMPT_START} / {PROMPT_END} markers. They delimit "
            f"the rules sent to the model; without them the prompt would have no rules.")
    block = text[a + len(PROMPT_START):b].strip()
    if len(block) < PROMPT_MIN:
        raise RuntimeError(
            f"{doc}: the prompt block is {len(block)} chars, under the {PROMPT_MIN} "
            f"minimum. Either it was emptied by accident or the rules moved.")
    return block


HEALTH = os.path.join(BUILD, "health.json")
# A source has to miss for this long, with something still trying it, before a run says
# anything. Under it, a failure is weather: `get` already retried six times with
# exponential backoff, the steps degrade, and the next run picks the paper back up.
# Over it, the source is not flaky, it is gone -- and the reason to wait days rather
# than runs is that some of these are only asked once a week.
DEAD_DAYS = 6
# A source that has never once answered is a different diagnosis: almost always a URL
# that moved, an endpoint that now needs a key, or a config field nobody filled. No
# point waiting a week to say so, but one bad afternoon should not say it either.
NEVER_DAYS = 2
# Consecutive recorded failures, with no success between them, before a source counts as
# failing rather than busy. The thresholds above are in days, which is the right clock
# for "has it come back" and the wrong one for "is it working". Deliberately small: `get`
# retries six times with exponential backoff before recording one failure, so three of
# these is ~18 attempts, and any success resets the counter.
FAILING_NOW = 3


def source_key(url: str) -> str:
    """Host plus the shape of the path, with identifiers collapsed to `*`.

    Host alone would be wrong here, and specifically wrong for the source that caused
    this: `api.semanticscholar.org` serves an author endpoint that answers reliably and
    a search endpoint that 429s at every anonymous caller. Recorded per host, the
    working half hides the broken half and the ledger reports a source as healthy while
    a step that depends on it never once succeeds.
    """
    m = re.match(r"https?://([^/?#]+)([^?#]*)", url)
    if not m:
        return url[:60]
    segs = []
    for s in m.group(2).split("/"):
        if not s:
            continue
        # An identifier is anything that names one record rather than one endpoint.
        segs.append("*" if (re.search(r"\d", s) and not re.fullmatch(r"v[\d.]+", s))
                    or len(s) > 24 else s)
    return m.group(1) + "/" + "/".join(segs[:5])


def _health() -> dict:
    try:
        with open(HEALTH) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def note_fetch(url: str, ok: bool, why: str = "") -> None:
    """Record that a source answered, or did not. See `health_report`.

    Kept in `build/` -- derived, gitignored, rebuilt from nothing after a clean clone. An
    observed fact about one machine's network has no business in a committed file.

    `why` is the status code or exception name behind a failure, because a 429 (a source
    working correctly and refusing our pace) and a 404 (a source that moved) need opposite
    responses and both otherwise read as "never once answered".
    """
    h, key, today = _health(), source_key(url), time.strftime("%Y-%m-%d")
    r = h.setdefault(key, {"ok": 0, "fail": 0, "first_seen": today,
                           "last_ok": None, "last_fail": None})
    r["ok" if ok else "fail"] += 1
    r["last_ok" if ok else "last_fail"] = today
    # Consecutive failures since the last success -- the only one of the three counters that
    # answers "is it failing *now*". A ratio over the cumulative `ok`/`fail` fires on
    # arxiv.org/html/* (449 ok, 86 old fails, healthy today) and stays silent on a source
    # refusing every call since yesterday. Self-populating, so an older ledger reads as 0.
    r["since_ok"] = 0 if ok else r.get("since_ok", 0) + 1
    if not ok and why:
        r["last_error"] = why
    elif ok:
        # Cleared on success: `last_error` answers "what would fix this source", and a source
        # that just answered has nothing to fix. Left set, the ledger reported `last_error: 429`
        # after a run of three clean calls and no failures -- a ledger that is silent gets
        # checked, one that is confidently wrong gets believed. Nothing is lost, since both
        # readers of the field sit inside `health_report`'s `not r["ok"]` branch.
        r.pop("last_error", None)
    try:
        write_json(HEALTH, h, indent=1, sort_keys=True)
    except OSError:
        pass          # a ledger that cannot be written must not break the run it watches


def _days_since(day: str | None) -> float:
    if not day:
        return float("inf")
    try:
        return (time.time() - time.mktime(time.strptime(day, "%Y-%m-%d"))) / 86400
    except ValueError:
        return float("inf")


def health_report() -> list[str]:
    """Sources that look broken rather than busy, worst first. Empty when all is well.

    The distinction this exists to draw: a source that fails sometimes needs nothing
    said about it, and a source that has failed every time for a week needs fixing.
    Reporting every failure would train the reader to skip the line, which is how the
    permanent one gets missed -- so the rule is deliberately slow, and silence here is
    a claim that every source has answered recently.
    """
    out = []
    for key, r in sorted(_health().items()):
        if not r.get("fail"):
            continue
        quiet, tried = _days_since(r.get("last_ok")), _days_since(r.get("last_fail"))
        if tried > 1:
            continue          # nothing has asked lately, so nothing is known
        if not r.get("ok") and _days_since(r.get("first_seen")) >= NEVER_DAYS:
            # A source that only ever refused our pace is not broken, and telling the
            # reader to check whether it still exists sends them to look at a working
            # URL. It has one fix and the generic advice does not name it.
            if r.get("last_error") in ("429", "503"):
                out.append(f"{key}: rate-limited every time since {r['first_seen']} "
                           f"({r['fail']} attempts, HTTP {r['last_error']}) -- the URL is "
                           f"fine; this one needs an API key or a slower `PACE` entry")
            else:
                out.append(
                    f"{key}: {r['fail']} attempts since {r['first_seen']}, never once "
                    f"answered"
                    + (f" (last: {r['last_error']})" if r.get("last_error") else "")
                    + " -- check the URL, the key, and whether it still exists")
        elif r.get("since_ok", 0) >= FAILING_NOW:
            # The gap both branches around this one left open, and it was live: the S2
            # search endpoint had answered 3 times, failed 18, and was refusing every call
            # -- and this function printed nothing, because it had answered *once* (so not
            # the branch above) and had answered *recently* (so not the branch below).
            since = r["since_ok"]
            out.append(f"{key}: {since} consecutive failures, nothing succeeding since "
                       f"{r.get('last_ok') or 'ever'}"
                       + (f", HTTP {r['last_error']}" if r.get("last_error") else "")
                       + " -- failing now, not busy"
                       + (" -- needs a key or a slower `PACE` entry"
                          if r.get("last_error") in ("429", "503") else ""))
        elif r.get("ok") and quiet >= DEAD_DAYS:
            out.append(f"{key}: last answered {r['last_ok']}, failing since -- "
                       f"{r['fail']} failure{'s' * (r['fail'] != 1)} against "
                       f"{r['ok']} success{'es' * (r['ok'] != 1)}")
    return out


# Minimum seconds between two requests to one host, applied inside `get` rather than at
# the call sites: the limit belongs to the host, and no single caller can see the others.
#
#   1.05s  Semantic Scholar's introductory limit is one request per second across all
#          endpoints, shared across the whole key -- or, keyless, across every anonymous
#          caller. A key raises the ceiling; it does not remove it.
#   3s     arXiv's stated delay for programmatic access. `export.arxiv.org` is a
#          different host and keeps its own explicit sleep.
# OpenAlex and Crossref answer 429 to a burst rather than queueing it, and `get`'s
# backoff then spends up to four minutes per URL -- a 113-paper loop stops being a
# slow run and becomes a run that never ends.
PACE = {"api.semanticscholar.org": 1.05, "arxiv.org": 3.0,
        "api.openalex.org": 0.2, "api.crossref.org": 0.2, "dblp.org": 4.0}
# Both read a contact address out of the User-Agent and serve it from a separate
# pool. The address is `identity.email` from `config.yaml`, which is already public.
POLITE = ("api.openalex.org", "api.crossref.org")
_last_hit: dict[str, float] = {}
_CONTACT: str | None = None
# host -> seconds until its budget resets. OpenAlex meters its search endpoints: a
# `.search:` filter costs 10 credits against a free daily 1000 ($0.10), so the 113rd
# per-paper query of a day is refused however slowly it is paced. The refusal is a 429
# whose `retryAfter` is hours, so retrying it is the one case where backoff cannot win
# and every later call to the same host is already answered.
_BUDGET_OUT: dict[str, int] = {}


def host_of(url: str) -> str:
    return (re.match(r"https?://([^/?#]+)", url) or [None, ""])[1]


def budget_reset(host: str) -> int | None:
    """Seconds until `host`'s metered budget resets, or None if it has not refused us."""
    return _BUDGET_OUT.get(host)


def _contact() -> str:
    """`identity.email`, or `""`. Cached: `get` asks once per request."""
    global _CONTACT
    if _CONTACT is None:
        _CONTACT = ((load_config().get("identity") or {}).get("email") or "").strip()
    return _CONTACT


def _pace(url: str) -> None:
    host = host_of(url)
    gap = PACE.get(host)
    if not gap:
        return
    wait = gap - (time.monotonic() - _last_hit.get(host, 0.0))
    if wait > 0:
        time.sleep(wait)
    # Stamped after the wait, so the clock starts when the request leaves rather than
    # when it was queued.
    _last_hit[host] = time.monotonic()


def metered(url: str) -> bool:
    """Whether this URL spends credits, as opposed to being free on the same host.

    OpenAlex prices per endpoint, not per host: a `.search:` filter costs credits and a
    `/works/doi:` lookup is free and keeps answering after the credits are gone. Only
    the priced shape is worth skipping once a host has refused one. Read from the query
    string alone, so a DOI with `search` in it stays free.
    """
    return "search" in url.partition("?")[2].lower()


def _out_of_budget(e: urllib.error.HTTPError) -> bool:
    """A 429 that says the day's credits are spent, and records when they return."""
    h = e.headers or {}
    spent = (h.get("x-ratelimit-remaining-usd") == "0"
             or b"Insufficient budget" in (e.read() if e.fp else b""))
    if not spent:
        return False
    reset = h.get("x-ratelimit-reset") or ""
    _BUDGET_OUT[host_of(e.url)] = int(reset) if str(reset).isdigit() else 0
    return True


def get_status(url: str, timeout: int = 40, retries: int = 6,
               accept: str | None = None) -> tuple[int, bytes]:
    """GET with exponential backoff on 429/503, as (HTTP status, body).

    The status is 0 when no reply arrived at all -- a timeout, a refused connection, or
    a host already over its metered budget -- so a caller can tell the server saying
    "this record is gone" from the fetch not happening. The body is b'' on any failure.

    `S2_API_KEY` in the environment is sent to Semantic Scholar. Without it the caller
    shares one rate-limit pool with every anonymous client, and a 429 there makes an
    audit report "no index has this paper" about a paper an index has. Environment
    only, never `config.yaml` -- that file is committed.
    """
    headers = dict(UA)
    if any(h in url for h in POLITE) and _contact():
        headers["User-Agent"] += f" mailto:{_contact()}"
    key = os.environ.get("S2_API_KEY", "").strip()
    if key and "api.semanticscholar.org" in url:
        headers["x-api-key"] = key
    if accept:
        headers["Accept"] = accept
    if host_of(url) in _BUDGET_OUT and metered(url):
        # Noted, not silent: `health_report` reads absence of a line as "every source
        # answered recently", and skipping 111 fetches is the opposite of that.
        note_fetch(url, False, "429 budget")
        return 0, b""
    delay = 4.0
    for attempt in range(retries):
        try:
            _pace(url)
            req = urllib.request.Request(url, headers=headers)
            r = urllib.request.urlopen(req, timeout=timeout)
            body = r.read()
            note_fetch(url, True)
            return getattr(r, "status", 200) or 200, body
        except urllib.error.HTTPError as e:
            if e.code == 429 and _out_of_budget(e):
                note_fetch(url, False, "429 budget")
                return 0, b""
            if e.code in (429, 503) and attempt < retries - 1:
                time.sleep(delay)
                delay *= 2
                continue
            # A 404 or 410 on a URL naming one record is the server answering the question about
            # that record, so the ledger counts it as the host working. On a URL with no
            # identifier in it the same code means the endpoint itself is gone, which is what the
            # ledger exists to notice. `source_key` draws that line: identifiers collapse to `*`.
            note_fetch(url, e.code in (404, 410) and "*" in source_key(url), str(e.code))
            return e.code, b""
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay)
                delay *= 2
                continue
            note_fetch(url, False, type(e).__name__)
            return 0, b""
    note_fetch(url, False)
    return 0, b""


def get(url: str, **kw) -> bytes:
    """The body from `get_status`, b'' on any failure."""
    return get_status(url, **kw)[1]


def get_json(url: str, **kw) -> dict | list | None:
    raw = get(url, accept="application/json", **kw)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


# ---------------------------------------------------------------- the gh CLI

def gh(*args: str, check: bool = False, timeout: int = 60) -> tuple[int, str]:
    """Run `gh` and return (exit code, output) -- stdout when it worked, stderr when not.

    Goes through the CLI rather than the REST API so it inherits the user's login and
    rate limit. `check=True` raises RuntimeError instead of returning a non-zero code.
    No `gh` on PATH always raises, whatever `check` says: an empty answer would read as
    "GitHub says no" and callers act on that.
    """
    try:
        r = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError as e:
        raise RuntimeError("gh is not installed -- see https://cli.github.com") from e
    except (OSError, subprocess.TimeoutExpired) as e:
        if check:
            raise RuntimeError(f"gh {' '.join(args)}: {type(e).__name__}") from e
        return 1, f"{type(e).__name__}: {e}"
    if r.returncode and check:
        raise RuntimeError(r.stderr.strip() or f"gh {' '.join(args)} failed")
    return r.returncode, (r.stdout if r.returncode == 0 else r.stderr)


def gh_text(*args: str, timeout: int = 60) -> str:
    """`gh` stdout, or "" for any failure -- for reads where absent and broken are the same."""
    code, out = gh(*args, timeout=timeout)
    return "" if code else out


def gh_json(*args: str, timeout: int = 60):
    """Parsed `gh api` output, or None if the call failed or the body was not JSON."""
    code, out = gh(*args, timeout=timeout)
    if code:
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return None


# ---------------------------------------------------------------- BibTeX

_ENTRY = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", re.M)


def _split_entries(text: str) -> list[tuple[str, str, str, str]]:
    """Yield (type, key, body, raw) by brace-matching from each @type{key, header.

    `raw` is the verbatim entry text. We publish that byte-for-byte rather than
    regenerating BibTeX from parsed fields: a regenerated citation key would
    differ from the one people have already cited, and one canonical citation
    string everywhere is worth more than a tidier one.
    """
    out = []
    for m in _ENTRY.finditer(text):
        depth, i = 1, m.end()
        while i < len(text) and depth:
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
            i += 1
        out.append((m.group(1).lower(), m.group(2), text[m.end():i - 1],
                    text[m.start():i]))
    return out


_FIELD = re.compile(r"(\w+)\s*=\s*", re.M)


def _parse_fields(body: str) -> dict:
    """Parse `field = {value}` / `field = "value"` / `field = bareword`."""
    fields, pos = {}, 0
    while True:
        m = _FIELD.search(body, pos)
        if not m:
            break
        name, i = m.group(1).lower(), m.end()
        while i < len(body) and body[i].isspace():
            i += 1
        if i >= len(body):
            break
        if body[i] == "{":
            depth, j = 1, i + 1
            while j < len(body) and depth:
                if body[j] == "{":
                    depth += 1
                elif body[j] == "}":
                    depth -= 1
                j += 1
            val, pos = body[i + 1:j - 1], j
        elif body[i] == '"':
            j = i + 1
            while j < len(body) and body[j] != '"':
                j += 2 if body[j] == "\\" else 1
            val, pos = body[i + 1:j], j + 1
        else:
            j = i
            while j < len(body) and body[j] not in ",\n":
                j += 1
            val, pos = body[i:j], j
        fields[name] = " ".join(val.split())
    return fields


def parse_bibtex(text: str) -> list[dict]:
    """Return [{key, type, raw, <fields>}] for every entry."""
    entries = []
    for etype, key, body, raw in _split_entries(text):
        e = _parse_fields(body)
        e["key"], e["type"], e["raw"] = key, etype, raw
        entries.append(e)
    return entries


# ---------------------------------------------------------------- matching

_LATEX = re.compile(r"\\[a-zA-Z]+\s*|[{}$\\]")
# The same two halves separately, because they want different replacements: a removed
# *command* leaves a word boundary behind (`a\,b` is two words), a removed *brace* does
# not (`{B}aby{LM}` is one). `_LATEX` collapses both to a space, which is only safe for
# callers that go on to delete every separator. See `slugify`.
_LATEX_CMD = re.compile(r"\\[a-zA-Z]+\s*")
_LATEX_PUNCT = re.compile(r"[{}$\\]")
_NONWORD = re.compile(r"[^a-z0-9]+")

# Upstream damage, not LaTeX: a title holds `{ extdollar}` where `{\textdollar}` was
# meant, because whatever wrote the .bib read the `\t` as a tab and lost the backslash and
# the command's leading `t` with it. Stripped here rather than at each call site, so the
# token vanishes from the slug, the display title and the matching key together -- strip
# it in one place only and the three disagree about the paper. `\\?t?` matches the intact
# `{\textdollar}` too, so a repaired bibliography keeps working.
_MANGLED = re.compile(
    r"\{\s*\\?t?ext(dollar|backslash|asciitilde|asciicircum|underscore)\s*\}")


def strip_mangled(s: str) -> str:
    return _MANGLED.sub("", s)


def repair_mangled(s: str) -> str:
    r"""Put the backslash back: `{ extdollar}` -> `{\textdollar}`.

    For the one place the token must not simply disappear -- the published BibTeX,
    which is verbatim so that the citation key people already cite stays intact.
    Verbatim is right for the key and wrong for a corrupted command: shipped as-is,
    anyone who copies the entry gets a title reading `extdollarQ2extdollar` and a
    literal tab inside a field. Restoring the command keeps the author's intent (a
    `$` glyph in the title) and changes nothing else about the entry.
    """
    return _MANGLED.sub(lambda m: "{\\text" + m.group(1) + "}", s)


def _fold_title(s: str) -> str:
    """Accents, LaTeX and case removed; word boundaries still standing."""
    s = unicodedata.normalize("NFKD", strip_mangled(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return _LATEX.sub(" ", s).lower()


def norm_title(s: str | None) -> str:
    """Aggressive normalization for cross-source title matching."""
    if not s:
        return ""
    return _NONWORD.sub("", _fold_title(s))


# Function words, dropped before comparing two titles as sets. Small on purpose: every
# word removed is one less thing that has to agree, so the list holds only words that
# carry no subject matter and can legitimately differ between two renderings of the same
# title. `to` is what forced this -- it is the single word separating
# "Model merging with SVD to tie the Knots" from "Tie the KnOTS: Model Merging with SVD".
_STOP = frozenset("a an the of for to in on with and or from at by as is are be via "
                  "using".split())


def title_tokens(s: str | None) -> frozenset:
    """A title's subject-matter words, order and punctuation discarded.

    For the one mismatch `norm_title` cannot absorb, the same title *rearranged* -- it
    compares word order as though it were content.

    Set equality and no stemming, so a difference of one content word declines, singular
    against plural included. The errors are not symmetric. A missed match reports a paper you
    wrote as a possible stray and costs a minute of reading, while a wrong match silently
    drops a real stray. Callers must also refuse a short title, where a small set collides by
    accident.
    """
    return frozenset(_NONWORD.sub(" ", _fold_title(s or "")).split()) - _STOP


def split_authors(bibtex_author: str | None) -> list[str]:
    """`Last, First and Other, Name` -> ['First Last', 'Name Other'].

    LaTeX is stripped rather than having its braces removed. A CV bibliography
    highlights its owner's own name -- `\\textbf{\\emph{Leshem Choshen*}}` -- and
    brace-removal alone leaves `\\textbf\\emphLeshem Choshen*`, which matches no name
    anywhere. That turns the one author every downstream check looks for into the one
    author it cannot find, on exactly the papers the highlighting marks as yours.
    Corresponding-author daggers and asterisks go too; they are notation, not name.
    """
    if not bibtex_author:
        return []
    out = []
    for a in re.split(r"\s+and\s+", bibtex_author):
        a = clean_latex(a).strip(" *†‡§^")
        # BibTeX's `and others` is "et al.", not a person. It was being published as
        # an author named "others", and on a 97-author paper truncated to ten it also
        # hid the one author this repo exists to find. Callers detect the truncation
        # with authors_truncated() and go to a source that lists everyone.
        if a.lower() in ("others", "et al", "et al."):
            continue
        if "," in a:
            last, _, first = a.partition(",")
            a = f"{first.strip()} {last.strip()}".strip()
        if a:
            out.append(" ".join(a.split()))
    return out


def authors_truncated(bibtex_author: str | None) -> bool:
    """True when a BibTeX author field ends in `and others` — i.e. et al."""
    return bool(re.search(r"\band\s+others\s*$", (bibtex_author or "").strip(), re.I))


# Every external id we hold, mapped to the Wikidata property that is *typed* for it.
#
# None of these belong in `official website` (P856), which takes exactly one value. A
# typed identifier renders as a link anyway, is validated against a format constraint, is
# traversed by Scholia and Author Disambiguator, and can be reached from SPARQL.
#
# arXiv has no row: P4594 wants the *legacy* author id (`choshen_l_1`), and arXiv's
# current author identity is the ORCID link P496 already carries.
#
# Social handles are here as join keys -- what connects the account that announced a paper
# to the author of the paper. Only accounts you control and post research from: a
# statement here asserts as fact that this account speaks for your work.
WD_IDENTIFIERS = [
    ("P496", "ORCID iD", lambda c: c["identity"]["orcid"]),
    ("P1960", "Google Scholar author ID", lambda c: c["ids"]["google_scholar"]),
    ("P4012", "Semantic Scholar author ID", lambda c: c["ids"]["semantic_scholar_primary"]),
    ("P10283", "OpenAlex ID", lambda c: (c["ids"]["openalex"] or [None])[0]),
    # The pid path (`218/5237`), never the name. P2456's format constraint is numeric
    # and its formatter URL is dblp.org/pid/$1, so a name-shaped value is both a
    # constraint warning on the item and a link that 404s.
    ("P2456", "DBLP author ID", lambda c: c["ids"].get("dblp_pid")),
    ("P2037", "GitHub username", lambda c: c["ids"]["github"]),
    ("P12201", "Hugging Face user ID", lambda c: c["ids"].get("huggingface")),
    ("P6634", "LinkedIn personal profile ID", lambda c: c["ids"].get("linkedin")),
    ("P8964", "OpenReview.net profile ID", lambda c: c["ids"].get("openreview")),
    ("P12361", "Bluesky handle", lambda c: c["ids"].get("bluesky")),
    # `user@server`, no leading @ -- P4033's format constraint rejects the `@user@server`
    # form people paste from their own profile.
    ("P4033", "Mastodon address", lambda c: (c["ids"].get("mastodon") or "").lstrip("@")
     or None),
    ("P2002", "X username", lambda c: c["ids"].get("twitter")),
    ("P1153", "Scopus author ID", lambda c: c["ids"].get("scopus")),
    ("P1053", "ResearcherID", lambda c: c["ids"].get("researcherid")),
    ("P856", "official website", lambda c: c["identity"]["canonical_url"]),
]

# Where the social handles live as URLs, for the site's `sameAs` and its rel="me"
# links. Mastodon is the reason the rel="me" pass exists at all: it verifies a link
# back from the profile only if the page links to the profile with rel="me", so this
# is one of the few places where a markup attribute produces a visible badge on a
# surface you do not control. The same convention is what IndieAuth consumers read.
SOCIAL_URLS = {
    "bluesky": lambda v: f"https://bsky.app/profile/{v}",
    "twitter": lambda v: f"https://x.com/{v}",
    "linkedin": lambda v: f"https://www.linkedin.com/in/{v}",
    "github": lambda v: f"https://github.com/{v}",
    # `@user@server` -> https://server/@user
    "mastodon": lambda v: "https://{}/@{}".format(*reversed(v.lstrip("@").split("@", 1))),
}


def social_url(kind: str, value: str | None) -> str | None:
    """Profile URL for a handle, or None. Unknown kinds and empty values yield None."""
    if not value or kind not in SOCIAL_URLS:
        return None
    try:
        return SOCIAL_URLS[kind](value.strip())
    except (IndexError, TypeError):
        return None


def org_name(a) -> str:
    """The name of an affiliation entry, which may be a bare string or a mapping.

    `identity.affiliations` accepts both: a plain name, or `{name, url, ror, wikidata}`
    for an organisation whose identity is worth stating. Everything that only needs the
    name -- the page byline, the ORCID employment diff, the Wikidata P108 lookup -- goes
    through here so that adding a URL to one entry cannot turn its name into a dict
    rendered as `{'name': ...}` in published text.
    """
    return a if isinstance(a, str) else str((a or {}).get("name") or "")


def norm_name(s: str) -> str:
    """Fold a personal name for comparison: accents, punctuation, case, spacing."""
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return " ".join(re.sub(r"[^\w\s]", " ", s).lower().split())


def name_match(candidate: str, variants) -> str:
    """Classify an author string against your known name forms: "exact", "near", or "".

    "near" is same first name with a surname within one or two characters, or whole-string
    similarity above .88 -- deliberately narrow, since a false "that is you" is worse than a
    miss. It earns its place because two of these papers carry "Leshem Chosen" in their arXiv
    metadata, so every arXiv-derived index files them under a person who does not exist, and
    an exact-match check would report the author as simply absent.
    """
    import difflib

    c = norm_name(candidate)
    if not c:
        return ""
    for v in variants:
        n = norm_name(v)
        if not n:
            continue
        if c == n:
            return "exact"
        # "Choshen, Leshem" vs "Leshem Choshen": order carries no information here.
        if sorted(c.split()) == sorted(n.split()):
            return "exact"
        cp, np_ = c.split(), n.split()
        if cp and np_ and cp[0] == np_[0] and cp[-1] != np_[-1]:
            r = difflib.SequenceMatcher(None, cp[-1], np_[-1]).ratio()
            if r >= 0.8 and abs(len(cp[-1]) - len(np_[-1])) <= 2:
                return "near"
        if difflib.SequenceMatcher(None, c, n).ratio() >= 0.88:
            return "near"
    return ""


def arxiv_id(entry: dict) -> str | None:
    """Extract a bare arXiv id from eprint / url / doi / venue fields.

    `journal` and `booktitle` are in the list because `journal = {arXiv preprint
    arXiv:2408.12259}` is what Google Scholar's BibTeX export writes for a preprint, and
    it is the only place that id appears in the entry. Missing it costs the whole paper:
    no arXiv id means no abstract, no full text, no HTML rendering and no links -- which
    is exactly what happened to "Can You Trust Your Metric?", whose id was sitting in
    its venue string while its record carried none.
    """
    if entry.get("eprint") and (entry.get("eprinttype", "arxiv").lower() == "arxiv"
                                or entry.get("archiveprefix", "").lower() == "arxiv"):
        return entry["eprint"].split("v")[0]
    for field in ("url", "doi", "note", "journal", "booktitle"):
        v = entry.get(field) or ""
        m = re.search(r"(?:arxiv\.org/(?:abs|pdf)/|arXiv[.:]|arXiv\.)(\d{4}\.\d{4,5})", v, re.I)
        if m:
            return m.group(1)
    return None


def paper_doi(p: dict) -> str | None:
    """The best DOI for a paper, falling back to its arXiv DataCite DOI.

    Most specific claim first -- publisher DOI, then whatever DOI the author registered with
    arXiv, then arXiv's own 10.48550/arXiv.<id>, which exists for every paper including the
    oldest ids.

    ORCID *groups* works that share an identifier, so an entry carrying a DOI merges with the
    registry-sourced copy instead of becoming a second record. A paper with no DOI anywhere
    is the only kind that can duplicate.
    """
    if p.get("doi"):
        return p["doi"]
    if p.get("arxiv_doi"):
        return p["arxiv_doi"]
    return f"10.48550/arXiv.{p['arxiv']}" if p.get("arxiv") else None


# `{ extdollar}` used to be mapped here to `$` (and then dropped with the other `$`).
# That fixed the display title only, which is why the mangled word was still in the
# slug and in the matching key. `strip_mangled` now handles it for all three.
_MATH = {r"\({}^{\mbox{2}}\)": "\u00b2", r"\({}^{\mbox{3}}\)": "\u00b3",
         r"$^2$": "\u00b2", r"$^3$": "\u00b3"}

# LaTeX accents -> Unicode, resolved before any command-stripping runs. `\i` is dotless i,
# a letter command, so clean_latex's stray-`\command` rule would delete it and take the
# vowel with it (`Garc{\'{\i}}a` -> `Garca`); `\'` and `\"` are punctuation commands no
# rule there matches. These are co-author names, published in JSON-LD `author.name`, in
# `citation_author` tags and in the page body.
_LATEX_LETTERS = {"i": "i", "j": "j", "l": "\u0142", "L": "\u0141", "o": "\u00f8",
                  "O": "\u00d8", "ss": "\u00df", "aa": "\u00e5", "AA": "\u00c5",
                  "ae": "\u00e6", "AE": "\u00c6", "oe": "\u0153", "OE": "\u0152",
                  "dh": "\u00f0", "DH": "\u00d0", "th": "\u00fe", "TH": "\u00de"}
_LETTER_RE = re.compile(r"\\(ss|aa|AA|ae|AE|oe|OE|dh|DH|th|TH|i|j|l|L|o|O)(?![a-zA-Z])")

_ACCENT_MARKS = {"'": "\u0301", "`": "\u0300", '"': "\u0308", "^": "\u0302",
                 "~": "\u0303", "=": "\u0304", ".": "\u0307", "u": "\u0306",
                 "v": "\u030c", "H": "\u030b", "r": "\u030a", "c": "\u0327",
                 "k": "\u0328", "d": "\u0323", "b": "\u0331"}
# Punctuation accents take an optional brace (`\'e`, `\'{e}`); letter-named ones
# require it (`\v{s}`), so that `\c` cannot swallow the `c` of a real command.
_ACCENT_RE = re.compile(r"""\\(['`"^~=.])\s*\{?([a-zA-Z])\}?"""
                        r"|\\([uvHrckdb])\s*\{([a-zA-Z])\}")
# Same lost backslash as `{ extdollar}` below, in an accent: `Aky{"{u}}rek`. Both
# spellings of that name are in the bibliography, so without this one person is
# published as two. The full brace-quote-brace-letter shape never occurs as real
# quotation, which is what makes it safe to read as damage.
_LOST_ACCENT_RE = re.compile(r"""\{(['`"^~])\{([a-zA-Z])\}\}""")


def _accent(m: re.Match) -> str:
    sym, ch = (m.group(1), m.group(2)) if m.group(1) else (m.group(3), m.group(4))
    return unicodedata.normalize("NFC", ch + _ACCENT_MARKS[sym])


def latex_accents(s: str) -> str:
    r"""`Garc{\'{\i}}a` -> `Garc\u00eda`, `Aky{\"{u}}rek` -> `Aky\u00fcrek`."""
    s = _LOST_ACCENT_RE.sub(lambda m: "{\\" + m.group(1) + "{" + m.group(2) + "}}", s)
    s = _LETTER_RE.sub(lambda m: _LATEX_LETTERS[m.group(1)], s)
    return _ACCENT_RE.sub(_accent, s)


def clean_latex(s: str | None) -> str:
    """Human-readable text from a BibTeX field.

    Titles arrive with protective braces ({DORA}), math wrappers, and escaped
    ampersands. Leaving those in means they show up in the page heading, the
    highwire citation_title, and the JSON-LD -- i.e. in exactly the fields Scholar
    matches on. The raw form is still published verbatim in the BibTeX block, so
    nothing is lost by cleaning the display copy.
    """
    if not s:
        return ""
    s = strip_mangled(s)
    for k, v in _MATH.items():
        s = s.replace(k, v)
    s = latex_accents(s)                                # before anything deletes \i
    s = re.sub(r"\\[a-zA-Z]+\{([^{}]*)\}", r"\1", s)   # \emph{x} -> x
    s = re.sub(r"\\[a-zA-Z]+\s?", "", s)                # stray \command
    s = s.replace("{", "").replace("}", "")
    s = s.replace("\\&", "&").replace("\\_", "_").replace("\\%", "%").replace("$", "")
    return " ".join(s.split())


# The acronym a venue is actually known by, keyed on a phrase that identifies it.
# Longest phrase wins, so "Findings of the Association for Computational Linguistics"
# is not read as plain ACL. DBLP writes the acronym into the string itself (`{ACL}
# 2026`), which needs no table; these are the sources that spell it out instead --
# ACL Anthology, Semantic Scholar, OpenReview.
_VENUE_ACRONYM = {
    "conference on empirical methods in natural language processing": "EMNLP",
    "north american chapter of the association for computational linguistics": "NAACL",
    "conference on computational natural language learning": "CoNLL",
    "annual meeting of the association for computational linguistics": "ACL",
    "conference of the association for computational linguistics": "ACL",
    "international conference on learning representations": "ICLR",
    "conference on neural information processing systems": "NeurIPS",
    "advances in neural information processing systems": "NeurIPS",
    "international conference on machine learning": "ICML",
    "international conference on computational linguistics": "COLING",
    "language resources and evaluation conference": "LREC",
    "conference on artificial intelligence": "AAAI",
    "joint conference on lexical and computational semantics": "*SEM",
    "international workshop on semantic evaluation": "SemEval",
    "annual meeting of the cognitive science society": "CogSci",
    "transactions of the association for computational linguistics": "TACL",
    "trans. assoc. comput. linguistics": "TACL",
    "transactions on machine learning research": "TMLR",
    "trans. mach. learn. res.": "TMLR",
    "journal of machine learning research": "JMLR",
    "conference on language modeling": "COLM",
    "european chapter of the association for computational linguistics": "EACL",
}
# A journal is not named by the year of its issue the way a conference is.
_NO_YEAR = ("TACL", "TMLR", "JMLR", "Nature", "arXiv")
# Which means the rest of the table is conferences and workshops, by construction.
_CONFERENCE_ACRONYMS = frozenset(a for a in _VENUE_ACRONYM.values() if a not in _NO_YEAR)
# Whole-string names, where a substring match would be wrong or ambiguous.
_VENUE_EXACT = {"nat.": "Nature", "science": "Science"}
# Every way the sources spell "this is a preprint": DBLP's `CoRR`, Semantic Scholar's
# `ArXiv`, and the `arXiv preprint arXiv:2408.12259` that bibliographies write by hand.
# Worth collapsing, because build_site suppresses the highwire citation tag for a venue
# it recognizes as a preprint, and it recognizes "arXiv" but not "arXiv preprint arXiv:...".
_PREPRINT_VENUE = re.compile(
    r"(corr|arxiv(\.org)?( preprint)?)([\s:]*(arxiv:)?(abs/)?[\d.v/]+)?$", re.I)
# Tracks worth keeping: a Findings paper and a main-conference paper are not the same
# line on a CV, and a demo is not a long paper.
_VENUE_TRACK = ((r"\bfindings\b", "Findings of {}"),
                (r"system demonstrations?\b|\bdemo track\b", "{} (Demo)"),
                (r"\btutorial", "{} (Tutorials)"))
# `{ACL} 2026`, `LREC-COLING 2024`, `*SEM@NAACL-HLT 2022`. The lookbehind, rather than
# \b, is what lets a leading `*` into the acronym and keeps the match from starting
# halfway through a hyphenated one.
_ACRONYM_YEAR = re.compile(
    r"(?<![\w*@/-])(\*?[A-Z][A-Za-z]{1,9}(?:[-/@][A-Za-z*-]{2,12})?)[\s,]+"
    r"((?:19|20)\d{2})\b")
_PAREN_ACRONYM = re.compile(r"\((\*?[A-Z][A-Za-z]{1,9}(?:[-/@][A-Za-z*-]{2,12})?)\)")
_YEAR = re.compile(r"\b(?:19|20)\d{2}\b")
# Long enough that the string cannot already be in citation form -- an acronym, a year
# and a couple of words fit in 40 characters. Below it, extra words are load-bearing
# ("NeurIPS 2024 Competition Track") and compressing to the acronym would lose them.
_LONG_VENUE = 40


def venue_is_conference(v: str | None, entry_type: str | None = None) -> bool:
    """Whether to cite this venue as a conference rather than as a journal.

    A conference entry type is believed. `@article` is not, because bibliographies routinely
    type a conference paper as `@article` with `journal={ICLR}` and six entries here do. Two
    things override the type, a venue named by its year and a venue containing a known
    conference acronym.

    Scholar matches citations on separate citation_conference_title and citation_journal_title
    tags, so a wrong answer misfiles the paper. Cases in `validate.py`.
    """
    v = clean_latex(v)
    # Before the type, because `@inproceedings` with an arXiv venue is an entry written
    # in advance of the acceptance it is hoping for. The venue is the reliable half.
    if not v or is_preprint_venue(v):
        return False
    if str(entry_type or "").lower() in ("inproceedings", "incollection", "conference",
                                        "proceedings"):
        return True
    return bool(_YEAR.search(v[-4:])) or any(
        t in _CONFERENCE_ACRONYMS for t in re.split(r"[\s@/,-]+", v))


def is_preprint_venue(v: str | None) -> bool:
    """True for every way the sources spell "not published anywhere yet".

    One definition, because three places act on it: the deduper (which venue wins when
    a preprint and a published record merge), the highwire tags (Scholar should not be
    told a paper appeared in a journal called `arXiv preprint arXiv:2408.12259`), and
    the display string.
    """
    return bool(_PREPRINT_VENUE.fullmatch(clean_latex(v).lower()))


def canonical_venue(v: str | None, year: int | str | None = None) -> str:
    """"ACL 2026", not "Proceedings of the 64th Annual Meeting of the ..., San Diego".

    The full proceedings name is what DBLP, the ACL Anthology and Semantic Scholar give, and
    it is the wrong string to publish. It reaches the venue field on every paper page, JSON-LD
    `isPartOf`, and the `citation_conference_title` tag Scholar matches on, where a
    110-character truncation reads as broken metadata.

    Returns "" when nothing is confidently recognized, so the caller keeps the original
    rather than publishing a guess.
    """
    s = clean_latex(v)
    if not s:
        return ""
    low = s.lower()
    if _PREPRINT_VENUE.fullmatch(low):
        return "arXiv"
    if low in _VENUE_EXACT:
        return _VENUE_EXACT[low]
    # The spelled-out name first. It is unambiguous, so it wins over the acronym-shaped
    # text in the string -- which is how "Advances in Neural Information Processing
    # Systems 36: ... Systems 2023" used to come out as "Systems 2023".
    phrase = max((p for p in _VENUE_ACRONYM if p in low), key=len, default="")
    acro = _VENUE_ACRONYM.get(phrase, "")
    tok = ""
    if len(s) > _LONG_VENUE:
        # DBLP writes the acronym into the string itself. Two uppercase letters is what
        # separates an acronym from a word the pattern happens to fit ("Systems 2023").
        m = _ACRONYM_YEAR.search(s) or _PAREN_ACRONYM.search(s)
        if m and sum(c.isupper() for c in m.group(1)) >= 2:
            tok = m.group(1)
    if acro and tok and len(tok) > len(acro) and tok.lower().endswith(acro.lower()):
        # The name we know sits at the *end* of a longer token, so what precedes it is a
        # co-equal conference and belongs in the venue: LREC-COLING, not COLING. When it
        # sits at the start the tail is a subtitle or a host ("NAACL-HLT" -> NAACL,
        # "SemEval@NAACL-HLT" -> SemEval), and only the head is the venue.
        acro = tok.replace("/", "-")
    elif not acro:
        acro = tok
    if not acro:
        return ""
    if acro not in _NO_YEAR:
        ym = _YEAR.search(s)
        acro = f"{acro} {ym.group(0) if ym else year or ''}".strip()
    for pat, tmpl in _VENUE_TRACK:
        if re.search(pat, low):
            return tmpl.format(acro)
    return acro


def short_venue(v: str | None, limit: int = 110, year: int | str | None = None) -> str:
    """The venue as it is cited: an acronym if we recognize one, else trimmed."""
    v = clean_latex(v)
    canon = canonical_venue(v, year)
    if canon:
        return canon
    if len(v) <= limit:
        return v
    cut = v[:limit].rsplit(" ", 1)[0].rstrip(" ,;:-")
    return cut + "\u2026"


def clean_bibtex(raw: str | None) -> str:
    r"""Published BibTeX: verbatim, minus fields that only work in one person's build.

    `pretitle={\COL\META}` is a private macro from the source bibliography's own
    CV template. Publishing it verbatim hands readers an entry that fails to
    compile, which defeats the point of publishing a citation at all. Everything
    else -- crucially the citation key -- is untouched.
    """
    if not raw:
        return ""
    out = re.sub(r"^\s*pretitle\s*=\s*\{[^{}]*\}\s*,?\s*\n?", "", raw,
                 flags=re.M)
    out = repair_mangled(out)
    return re.sub(r"\n\s*\n+", "\n", out).strip()


def synth_bibtex(p: dict) -> str:
    """Build a BibTeX entry for a paper that has none.

    A paper only carries a `bibtex` field if it came from the bibliography, so anything
    filtering on `p.get("bibtex")` silently drops the ones discovered on arXiv or Semantic
    Scholar -- which have every field a citation needs and no entry text.

    The citation key is derived, so it is not the key anyone already cites. That is why
    `clean_bibtex` passes the bibliography's own text through untouched where there is some.
    """
    kind = {"inproceedings": "inproceedings", "article": "article",
            "incollection": "incollection"}.get(p.get("type") or "", "article")
    first = ((p.get("authors") or ["anon"])[0].split()[-1] or "anon").lower()
    key = re.sub(r"[^a-z0-9]", "", first) + str(p.get("year") or "") + \
        re.sub(r"[^a-z0-9]", "", (p.get("title") or "").split(" ")[0].lower())[:8]
    rows = [("author", " and ".join(p.get("authors") or [])),
            ("title", p.get("title") or ""),
            ("year", str(p.get("year") or "")),
            ("booktitle" if kind == "inproceedings" else "journal", p.get("venue") or ""),
            ("doi", paper_doi(p) or ""),
            ("url", p.get("url") or "")]
    if p.get("arxiv"):
        rows += [("eprint", str(p["arxiv"])), ("archivePrefix", "arXiv")]
    body = ",\n".join(f"  {k:<12} = {{{v}}}" for k, v in rows if v)
    return f"@{kind}{{{key},\n{body}\n}}"


def plural(n: int, one: str, many: str | None = None) -> str:
    """`3 papers`, `1 paper` -- a count and its noun, agreeing.

    Small, and worth having because of *when* a hardcoded plural goes wrong. Every count in
    the audit reports something left to do, so each trends to 1 and then to 0 as the work gets
    done, and the wording reads correctly for as long as the surface is broken. These files
    are committed and browsable on GitHub.
    """
    return f"{n} {one if n == 1 else (many or one + 's')}"


def slugify(s: str, maxlen: int = 60) -> str:
    """A slug is a published URL, so this has to be stable across a *fix* upstream.

    Callers pass the raw BibTeX title, so LaTeX is resolved here rather than in the display
    path. Two rules, both checked in `validate.py`, and either one broken moves a live URL.

    Math resolves first. `{\\textdollar}Q2{\\textdollar}` and `Q\\({}^{\\mbox{2}}\\)` are the
    damaged and the repaired form of one title, and both must give `q2-...` rather than
    `q-2-...`. Accents likewise, or `M{\\'{\\i}}rian` slugs to `m-rian`.

    Braces are dropped, not spaced. BibTeX braces protect capitals *inside* a word --
    `{B}aby{LM}`, `Lo{RA}`, `Com{PEFT}` -- so a separator splits it into
    `findings-of-the-b-aby-lm-challenge`. `norm_title` escapes this by dropping every
    non-word character afterwards. A slug keeps hyphens, so the difference reaches the URL.
    """
    s = strip_mangled(s or "")
    for k, v in _MATH.items():
        s = s.replace(k, v)
    s = unicodedata.normalize("NFKD", latex_accents(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = _LATEX_CMD.sub(" ", s)
    s = _LATEX_PUNCT.sub("", s).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:maxlen].rstrip("-")


def write_yaml(path: str, obj) -> None:
    if d := os.path.dirname(path):
        os.makedirs(d, exist_ok=True)
    with open(path, "w") as f:
        yaml.safe_dump(obj, f, sort_keys=False, allow_unicode=True, width=100)


def write_json(path: str, obj, **kw) -> None:
    """`json.dump` to `path`, creating its directory. Every build and cache file goes
    through this, so no caller can leave the directory out."""
    if d := os.path.dirname(path):
        os.makedirs(d, exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, **kw)


def read_yaml(path: str, default=None):
    if not os.path.exists(path):
        return default
    with open(path) as f:
        return yaml.safe_load(f)


def has_live_sidecar(slug: str) -> bool:
    """Whether `data/sidecars/<slug>.md` exists right now, asked of the disk.

    `papers.yaml` carries a `has_sidecar` field, rewritten only by `collect`, which needs the
    network -- so between promoting a draft and the next online run, which is exactly when
    somebody re-reads the worklist to see what promoting did, the field says the opposite of
    the truth. It reported 111 of 113 papers still needing drafting on a corpus where all 113
    were live. A filesystem fact costing one stat call is read, not remembered.
    """
    return os.path.exists(os.path.join(ROOT, "data", "sidecars", f"{slug}.md"))


def declined(text: str | None) -> str | None:
    """The `data/declines.yaml` `items:` pattern this text was declined by, if any.

    Returns the pattern rather than a bool, so the caller can print *which* decision this
    was. Case-insensitive, unlike the sections matcher, because the patterns are titles typed
    by hand against whichever surface showed them and Scholar title-cases what BibTeX does
    not.

    Every generator reads this, not only `apply_declines`. That one filters `WORKLIST.md`
    after rendering, so on its own a decision reaches the summary and none of the payload
    files under `tasks/`.
    """
    if not text:
        return None
    low = text.lower()
    for pat in (read_yaml(os.path.join(DATA, "declines.yaml")) or {}).get("items") or []:
        if str(pat).lower() in low:
            return str(pat)
    return None


# ------------------------------------------------------------------ question groups
#
# A question group is a form, not a list: each named role is a different *lexical* route
# to the same answer, so a missing route is a visibly empty field rather than a rule the
# drafter believes it satisfied.
#
#   plain         someone who has not read the paper, in their own words
#   jargon        the field's vocabulary, the way a specialist would type it
#   task          the thing they are trying to do ("how do I merge two adapters")
#   practitioner  first person, deciding ("should I use this for my model")
#
# `unsorted` is the legacy bucket: phrasings written before the roles existed. A draft may
# not emit it, and a redraft of any paper empties it -- so it shrinks and never grows.

QA_ROLES = ("plain", "jargon", "task", "practitioner")


def phrasings(group: dict) -> list[str]:
    """Every phrasing in a question group, roles first in `QA_ROLES` order.

    The first element is the canonical one -- the phrasing published as the group's heading
    and the one a `FAQPage.name` would carry -- which is why `plain` leads: of the four
    routes it is the one a reader who has not read the paper can follow.
    """
    if not isinstance(group, dict):
        return []
    ask = group.get("ask")
    if not isinstance(ask, dict):
        return []
    out = [ask[r] for r in QA_ROLES if isinstance(ask.get(r), str) and ask[r].strip()]
    out += [p for p in (ask.get("unsorted") or []) if isinstance(p, str) and p.strip()]
    return out


def answered_by(group: dict) -> list[str]:
    """The claim ids a question group points at, or an empty list."""
    if not isinstance(group, dict):
        return []
    ids = group.get("answered_by")
    return [a for a in ids if isinstance(a, str)] if isinstance(ids, list) else []


def qa_loci(group: dict) -> list[tuple[str, str]]:
    """`(locus_suffix, phrasing)` for each phrasing, in the order `phrasings` returns them.

    The suffix is what goes after `qa/<i>/`, so a caller that knows the group index can
    build a patch locus without knowing whether the phrasing sits in a role or in the
    legacy bucket.
    """
    if not isinstance(group, dict):
        return []
    ask = group.get("ask") if isinstance(group.get("ask"), dict) else {}
    out = [(f"ask/{r}", ask[r]) for r in QA_ROLES
           if isinstance(ask.get(r), str) and ask[r].strip()]
    out += [(f"ask/unsorted/{j}", p) for j, p in enumerate(ask.get("unsorted") or [])
            if isinstance(p, str) and p.strip()]
    return out
