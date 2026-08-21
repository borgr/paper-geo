Subject: a re-runnable GEO/SEO setup for your papers, if you want it

Hi Tamar,

I built a thing for my own papers and it generalises, so here is a starter bundle set up
for yours. The short version: it re-derives your bibliography from public records on every
run, builds a small site where each paper has a page carrying structured data an answer
engine can read, and then hands you a worklist of only the gaps no code can close.

Everything specific to you is already looked up -- 29 papers across 2 Semantic Scholar
records, and the tooling merges the two rather than asking you to pick one, your DBLP
pid, your ORCID. What it deliberately did not do is decide anything: every value only
you can answer is left blank and marked CONFIRM.

  https://github.com/borgr/paper-geo/tree/main/handover/tamar-rott-shaham

Start with README.md in that folder; it is four commands, in order. The one to read twice
is `python scripts/bootstrap_fork.py --yes`, which empties my judgement out of the fork --
inheriting my decision files would publish my decisions, including decisions not to
publish something, under your name.

It touches no account of yours. Fetching and building are automatic; every outward write
(deploy the site, edit Wikidata, accept an AI-drafted description) is a separate command
you run on purpose. The single judgement call is which GitHub Pages repo the site deploys
to, left blank because deploying over a repo that already serves your homepage replaces
that homepage.

Happy to run the first pass with you if that is easier than reading a README.

Leshem
