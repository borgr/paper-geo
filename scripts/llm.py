#!/usr/bin/env python3
"""The one place an LLM gateway is configured, retried, and parsed.

Two callers: `draft_sidecars.py` writes sidecars, `measure/fidelity.py` measures how
well engines describe them. Both talk to an OpenAI-compatible endpoint named entirely
by environment variables -- never `config.yaml`, which is committed and public, and an
internal gateway's URL is not.

    PAPER_GEO_LLM_BASE_URL   endpoint, e.g. https://host/some-model/v1
    PAPER_GEO_LLM_MODEL      model id sent in the request body
    PAPER_GEO_LLM_API_KEY    optional; "unused" when the gateway wants a header instead
    PAPER_GEO_LLM_KEY_HEADER optional header name to send the key under, for gateways
                             that do not use `Authorization: Bearer`

What each caller keeps for itself: how many requests to make, what shape to ask for,
and what to do when the endpoint will not enforce a schema.
"""
from __future__ import annotations

import json
import os
import sys
import time

ENV_BASE, ENV_MODEL = "PAPER_GEO_LLM_BASE_URL", "PAPER_GEO_LLM_MODEL"
ENV_KEY, ENV_HEADER = "PAPER_GEO_LLM_API_KEY", "PAPER_GEO_LLM_KEY_HEADER"

# Three tries spaced 5s, 10s, 15s: enough for a blip, short enough that a real outage
# surfaces as a failure rather than as a run that appears to hang.
TRANSIENT_TRIES = 3

# Matched by type name because transport errors arrive unwrapped from httpx on a streamed
# request (`RemoteProtocolError` is not an `anthropic` class), and by status code for the
# server-side ones. A 400 must never be retried.
_TRANSIENT_NAMES = {"APIConnectionError", "APITimeoutError", "RemoteProtocolError",
                    "ReadError", "ReadTimeout", "WriteError", "ConnectError",
                    "ConnectTimeout", "RemoteDisconnected", "IncompleteRead",
                    "InternalServerError", "RateLimitError", "OverloadedError"}
_TRANSIENT_STATUS = {408, 409, 429, 500, 502, 503, 504, 529}


def _transient(e: Exception) -> bool:
    """True where retrying could help: the connection died or the endpoint said busy."""
    if type(e).__name__ in _TRANSIENT_NAMES:
        return True
    if getattr(e, "status_code", None) in _TRANSIENT_STATUS:
        return True
    # httpx wraps the socket error in its own class; the cause is where the name lives.
    return type(e.__cause__).__name__ in _TRANSIENT_NAMES if e.__cause__ else False


def with_retries(call, label: str):
    """Run one request, retrying only the failures that are the connection's fault.

    Re-raises whatever the last attempt raised rather than returning None, so each
    caller's own handling -- climbing the dialect ladder, dropping to an unenforced
    request -- still runs on a failure that retrying cannot fix.
    """
    for tries in range(TRANSIENT_TRIES + 1):
        try:
            return call()
        except Exception as e:                        # noqa: BLE001 -- re-raised below
            if not _transient(e) or tries >= TRANSIENT_TRIES:
                raise
            wait = (tries + 1) * 5
            print(f"  {label}: {type(e).__name__} -- retry {tries + 1} of "
                  f"{TRANSIENT_TRIES} in {wait}s", file=sys.stderr)
            time.sleep(wait)


def client(spec: str | None = None, model_default: str | None = None,
           context: str = ""):
    """An OpenAI-compatible client and the model id to send, or exit saying what is missing.

    `spec` is `MODEL_ID` or `MODEL_ID@BASE_URL`. The second form is needed because a
    per-model gateway carries the model in the URL path and the slug is not derivable from
    the body id (`granite-3-3-8b-instruct` in the path, `ibm-granite/granite-3.3-8b-instruct`
    in the body), so naming a second model means naming its base URL too.

    `context` names the flag or mode that asked, so the exit message says what to drop.
    """
    try:
        from openai import OpenAI
    except ImportError:
        sys.exit("pip install openai")
    want, _, override = (spec or "").partition("@")
    base = override or os.environ.get(ENV_BASE)
    model = want or os.environ.get(ENV_MODEL) or model_default
    if not base or not model:
        sys.exit(f"{context}{' ' if context else ''}needs ${ENV_BASE} and ${ENV_MODEL} "
                 f"in the environment (never committed -- see scripts/llm.py)")
    key = os.environ.get(ENV_KEY, "unused")
    headers = {os.environ[ENV_HEADER]: key} if os.environ.get(ENV_HEADER) else None
    return OpenAI(base_url=base, api_key=key, default_headers=headers), model


def first_json(text: str):
    """The first complete JSON object in a response, or None.

    Needed because a model without enforced decoding wraps the object in a ``` fence,
    or prefaces it, or emits a reasoning trace first. Brace-matching rather than a
    regex, since claim text legitimately contains braces.
    """
    start = text.find("{")
    while start != -1:
        depth, instr, esc = 0, False, False
        for i in range(start, len(text)):
            c = text[i]
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                instr = not instr
            elif not instr and c == "{":
                depth += 1
            elif not instr and c == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i + 1])
                    except json.JSONDecodeError:
                        break
        start = text.find("{", start + 1)
    return None


# Keywords a constrained-decoding backend cannot compile. vLLM's grammar backends accept a
# `response_format` containing them and then quietly decode unguided, which is the worst
# available outcome: measured against Granite 3.3 8B, the full schema produced claims keyed
# `statement`/`magnitude`/`unit` -- invented fields, valid JSON, nothing the repo can read.
# Nothing is lost by dropping them, because the only conditional in the sidecar schema is
# "a `result` claim needs `evidence`", which `validate.py` enforces on the draft afterwards.
_UNDECODABLE = ("allOf", "anyOf", "oneOf", "not", "if", "then", "else")


# Appended to the user message when the endpoint will not decode against the schema.
JSON_ONLY = "\n\nReturn one JSON object matching the schema. No prose, no fence."


def decodable(node):
    """The schema with conditional keywords removed, for guided decoding only."""
    if isinstance(node, dict):
        return {k: decodable(v) for k, v in node.items() if k not in _UNDECODABLE}
    if isinstance(node, list):
        return [decodable(x) for x in node]
    return node
