<!-- declines -->
> **Deferred until an artifact is cited or asked about somewhere you can see it, or the paper work is done.** Parked on purpose in [`data/declines.yaml`](../data/declines.yaml), not declined — this is real work, just not before the rest.
> It is at the bottom of `WORKLIST.md` under *Deferred*.

# Zenodo: give the artifacts with no paper a citable identity

13 repos qualify. The filter is `kind` in ['guide', 'tool'] **and** no linked paper: a repo whose paper exists
already has a citation route, and minting a second one splits the citations
between two identifiers.

Whether anyone cites a tool or a guide is a fair objection, and the honest
answer is that some will not. The DOI still does two things that do not
depend on being cited: it makes the artifact resolvable after the repo moves
or disappears, and it puts a record into DataCite, which flows to OpenAlex
and to your ORCID works list — so the artifact joins the same graph as your
papers rather than living only on GitHub.

Do this once per repo, at a moment when it is in a state you would not mind
being permanent — the archive is a snapshot of the release, not of `main`:

1. <https://zenodo.org/account/settings/github/> — sign in **with GitHub**
   (a separate Zenodo account cannot see your repos), flip the repo on.
2. Tag a release on GitHub. Nothing is archived until you do; the switch only
   arms the webhook.
3. Zenodo mints two DOIs. Use the **concept DOI** everywhere — it always
   resolves to the newest version, so it does not go stale on the next release.
4. Fix the record's metadata once: authors with ORCIDs, a license, and the
   repo URL under *Related identifiers*.
5. Put the concept DOI in `data/repos.yaml` as `zenodo_doi:` — that both
   removes it from this list and lets `CITATION.cff` carry it.

- [ ] **borgr/arXiv_stuck** (guide) — An arXiv moderator's explanation of why submissions get held, stuck, or rejected
- [ ] **borgr/ATProto-links-bot** (tool) — Relays paper links shared in the CoLab Discord to Bluesky and Semble, via a sche
- [ ] **borgr/facultips** (guide) — A guide to applying for tenure-track faculty positions: research and teaching st
- [ ] **borgr/gcn_tf** (tool) — TensorFlow implementation of a labelled, gated syntactic graph convolutional net
- [ ] **borgr/grant_search** (tool) — Agentic skill for finding AI research grants and funding calls.
- [ ] **borgr/paper-geo** (tool) — Make your papers and code findable, and correctly described, by AI answer engine
- [ ] **borgr/paper-sharpener** (tool) — Agentic Claude Code skills for academic writing: review simulation, revision, an
- [ ] **borgr/paper_updated** (guide) — A curated list of ways to keep up with newly published research papers.
- [ ] **borgr/PoissonBinomial** (tool) — Python module computing Poisson binomial PMF, CDF, mean and standard deviation v
- [ ] **borgr/post** (guide) — A guide to finding and applying for a good postdoc position.
- [ ] **borgr/social-follow** (tool) — Follows research collaborators across Bluesky, Twitter/X and LinkedIn from a CSV
- [ ] **borgr/tutEval** (guide) — Materials for the LREC-COLING 2024 tutorial on evaluating large language models:
- [ ] **borgr/wit3scripts** (tool) — Wrapper scripts for preprocessing the WIT3 multilingual TED-talk translation cor
