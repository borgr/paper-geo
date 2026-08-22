#!/usr/bin/env python3
"""Agree with collaborators on who owns each paper's canonical page.

The problem: duplicating a *pointer* to a paper page is pure gain (independent
corroboration from another domain), but duplicating the *page itself* splits
authority and can trip Scholar's documented duplicate-title drop. So exactly one
party must own each paper's canonical page and sidecar, and everyone else links.

The mechanism is deliberately dumb: each participant publishes a static JSON
manifest at a stable URL listing the papers they claim. Every run fetches each
peer's manifest and:

  * paper claimed by a peer   -> set canonical_page to theirs, link-only locally
  * paper claimed by us       -> we own it; generate the page and the sidecar
  * claimed by nobody         -> unclaimed; suggest an owner, claim nothing
  * claimed by two or more    -> FLAG. Never auto-resolved -- a duplicated
                                 canonical page is exactly the harm this prevents

No server, no registry, no account. A peer who doesn't run this tool at all can
hand-write six lines of JSON and participate.

Usage:
    python scripts/ownership.py            # fetch peers, reconcile, report
    python scripts/ownership.py --manifest # write our own manifest for peers
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import BUILD, DATA, get_json, load_config, read_yaml, write_yaml  # noqa: E402

MANIFEST_VERSION = 1


def paper_ids(p: dict) -> list[str]:
    """Identifiers a manifest may be keyed by, most authoritative first."""
    out = []
    if p.get("doi"):
        out.append(f"doi:{p['doi'].lower()}")
    if p.get("arxiv"):
        out.append(f"arxiv:{p['arxiv']}")
    if p.get("acl"):
        out.append(f"acl:{p['acl']}")
    return out


def write_manifest(cfg, papers: list[dict]) -> str:
    """Publish what we claim, so peers can defer to us (and vice versa)."""
    me = cfg["collaboration"]["me"]
    base = cfg["site"]["base_url"].rstrip("/") + cfg["site"]["papers_path"]
    claims = []
    for p in papers:
        # Only papers actually owned, and `owner: None` is not one of them -- accepted, a corpus
        # with no owners set published 111 claims that this domain maintains the canonical page
        # for papers nobody agreed it owns, including ones where `default_owner_rule:
        # first_author` points at somebody else. Unclaimed has to mean unclaimed.
        if p.get("owner") != me:
            continue
        if p.get("canonical_page"):
            continue
        ids = paper_ids(p)
        if not ids:
            continue
        claims.append({
            "ids": ids,
            "title": p["title"],
            "canonical_page": f"{base}/{p['slug']}/",
            "has_sidecar": bool(p.get("has_sidecar")),
        })
    doc = {
        "paper_geo_manifest": MANIFEST_VERSION,
        "owner": me,
        "name": cfg["identity"]["name"],
        "orcid": cfg["identity"].get("orcid"),
        "canonical_url": cfg["identity"]["canonical_url"],
        "note": ("Papers whose canonical page and sidecar this owner maintains. "
                 "Link to canonical_page rather than publishing a competing page; "
                 "reuse the claim wording from the sidecar verbatim. "
                 "https://github.com/borgr/paper-geo"),
        "claims": claims,
    }
    out_dir = os.path.join(BUILD, "site")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "paper-geo.json")
    with open(path, "w") as f:
        json.dump(doc, f, indent=1)
    return path


def fetch_peers(cfg) -> dict[str, dict]:
    """id -> {owner, canonical_page, source_url}, from every peer manifest."""
    claimed: dict[str, dict] = {}
    for url in cfg["collaboration"].get("peers") or []:
        doc = get_json(url)
        if not doc or not doc.get("paper_geo_manifest"):
            print(f"  ! unreadable or not a manifest: {url}", file=sys.stderr)
            continue
        owner = doc.get("owner") or url
        for c in doc.get("claims") or []:
            for i in c.get("ids") or []:
                prev = claimed.get(i)
                if prev and prev["owner"] != owner:
                    prev.setdefault("conflict_with", []).append(owner)
                else:
                    claimed[i] = {"owner": owner,
                                  "canonical_page": c.get("canonical_page"),
                                  "source_url": url}
        print(f"  {owner}: {len(doc.get('claims') or [])} claims  ({url})")
    return claimed


def suggest_owner(p: dict, cfg) -> str | None:
    """Advisory only: who *should* own this, if nobody has claimed it."""
    if cfg["collaboration"].get("default_owner_rule") != "first_author":
        return None
    authors = p.get("authors") or []
    return authors[0] if authors else None


def reconcile(cfg, papers: list[dict], claimed: dict[str, dict]) -> dict:
    me = cfg["collaboration"]["me"]
    stats = {"ours": 0, "peer": 0, "unclaimed": 0, "conflict": 0}
    for p in papers:
        hit = next((claimed[i] for i in paper_ids(p) if i in claimed), None)
        if hit and hit.get("conflict_with"):
            p["owner_conflict"] = sorted({hit["owner"], *hit["conflict_with"]})
            p["owner_source"] = "peer"
            stats["conflict"] += 1
            continue
        p.pop("owner_conflict", None)
        if hit and hit["owner"] != me:
            p["owner"] = hit["owner"]
            p["owner_source"] = "peer"
            p["canonical_page"] = hit["canonical_page"]
            stats["peer"] += 1
        elif p.get("owner") == me or p.get("owner_source") == "self":
            p["owner"], p["owner_source"] = me, "self"
            p["canonical_page"] = None
            stats["ours"] += 1
        else:
            # Unclaimed. We do NOT auto-claim: silently claiming a paper a
            # co-author is about to claim is how two canonical pages happen.
            p["owner"] = None
            p["owner_source"] = "unclaimed"
            stats["unclaimed"] += 1
    return stats


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", action="store_true",
                    help="also write our own manifest for peers to read")
    ap.add_argument("--claim-all", action="store_true",
                    help="claim every currently-unclaimed paper for us")
    args = ap.parse_args()
    cfg = load_config()
    path = os.path.join(DATA, "papers.yaml")
    doc = read_yaml(path)
    if not doc:
        sys.exit("no data/papers.yaml -- run scripts/collect.py first")
    papers = doc["papers"]
    me = cfg["collaboration"]["me"]

    peers = cfg["collaboration"].get("peers") or []
    print(f"peers configured: {len(peers)}")
    claimed = fetch_peers(cfg) if peers else {}

    if args.claim_all:
        for p in papers:
            if not p.get("owner") and not any(i in claimed for i in paper_ids(p)):
                p["owner"], p["owner_source"] = me, "self"

    stats = reconcile(cfg, papers, claimed)
    write_yaml(path, doc)

    print(f"\nours: {stats['ours']}   peer-owned: {stats['peer']}   "
          f"unclaimed: {stats['unclaimed']}   CONFLICTS: {stats['conflict']}")
    if not peers:
        # Otherwise this step reports "unclaimed: 112" on every run for ever and there
        # is no way to tell, from the output, whether that is a finding or the resting
        # state. It is the resting state: with nobody to coordinate with there is
        # nothing to reconcile, and unclaimed is the correct answer, not a backlog.
        print("  No peers configured, so there is nothing to reconcile and nothing to "
              "claim: this\n  step is idle by design. It starts doing work when a "
              "coauthor publishes a manifest\n  and you add its URL to "
              "`collaboration.peers` in config.yaml. To publish yours:\n  "
              "python scripts/ownership.py --manifest")
    if stats["conflict"]:
        print("\nConflicts -- two parties claim the same paper. Resolve by talking to "
              "them; whoever keeps it, the other switches to a link:")
        for p in papers:
            if p.get("owner_conflict"):
                print(f"  {p['title'][:60]}  claimed by {p['owner_conflict']}")
    if stats["unclaimed"] and peers:
        print("\nUnclaimed, with a suggested owner (first author). Nothing is claimed "
              "automatically -- agree, then run with --claim-all or set owner by hand:")
        for p in sorted([p for p in papers if p.get("owner_source") == "unclaimed"],
                        key=lambda p: -(p.get("citations") or 0))[:10]:
            print(f"  {(p.get('citations') or 0):>5} cites  {p['title'][:52]:<54} "
                  f"-> {suggest_owner(p, cfg)}")

    if args.manifest:
        path_m = write_manifest(cfg, papers)
        n = len(json.load(open(path_m))["claims"])
        print(f"\nwrote {path_m}: {n} claim(s)")
        if not n:
            # Not a failure, and worth a sentence rather than a silent empty file: with
            # no peers there is nobody to coordinate with, and claiming ownership of a
            # coauthored paper is a thing to do on purpose, not by default.
            print("  Nothing is claimed, so the manifest is empty. That is the correct "
                  "state until you\n  agree ownership with a coauthor: set `owner` on "
                  "those papers, or claim the ones\n  where you are the corresponding "
                  "author with `--claim-all`.")
        print("Publish it at "
              f"{cfg['site']['base_url'].rstrip('/')}/paper-geo.json and give peers "
              "that URL for their config.")


if __name__ == "__main__":
    main()
