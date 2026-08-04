# The one-time checklist

Do these once, in this order, before touching any per-paper work. They're
independent of this tool — it just generates the payloads and tracks what's left.

Ordered by leverage ÷ effort. Items 1–4 are the ones that pay for the rest: they
fix *who you are* across every index, and nothing downstream works properly until
identity resolves to one person.

`python scripts/identity_tasks.py` writes the payload for 1, 2, 3 and 5 into
[`../tasks/`](../tasks/).

---

## 1. ORCID — populate it, then wire it everywhere

**Why first:** it's the lever for items 2 and 5. Semantic Scholar disambiguates on
ORCID, and OpenAlex is running ORCID-driven merges of split author profiles. Fixing
ORCID makes those two more likely to fix themselves — and keeps them fixed after
future re-clustering.

- [ ] Have an ORCID iD (free, 2 minutes) — <https://orcid.org/register>
- [ ] **Turn on auto-update** for **Crossref** and **DataCite**: *Works → Search &
      link*, authorise both, and grant standing permission. Covers only works whose
      deposited metadata already contains your iD, so this fixes the *future*.
      Published DOIs are Crossref; arXiv DOIs are DataCite — you want both.
- [ ] **Link your arXiv account to your ORCID** —
      <https://arxiv.org/user/confirm_orcid_id>. This is what puts your iD into
      arXiv's DataCite metadata, which is what makes DataCite auto-update work on
      future preprints. arXiv also says it prefers ORCID over its internal author
      identifiers.
- [ ] **Fill the backlog.** Three routes, in order of how well they work:
      1. *Add DOI* (**most reliable**) — resolves server-side against
         Crossref/DataCite and creates a properly-sourced work. One at a time;
         `tasks/orcid_dois.txt` is citation-ordered so stopping early still helps.
      2. *Search & link → Crossref Metadata Search* — the standard route, but the
         wizard is genuinely flaky and can hang. If it does, don't fight it.
      3. *Add works → Add BibTeX*, using `tasks/orcid_import.bib`. ORCID **groups
         works that share an identifier**, so a DOI-bearing entry merges with the
         registry copy when auto-update later finds it rather than showing as a
         duplicate. The file is split: DOI-bearing entries first (safe), then the
         handful without a DOI (nothing to group on — those can stand alone).
- [ ] Put your iD in your email signature and on every paper you submit. That's the
      mechanism that makes auto-update work without you.

**Wizards that will disappoint you, and why:** *Scopus* looks empty because Scopus
indexes little arXiv/ACL content and the wizard needs a Scopus Author ID you may not
have. **dblp is not an ORCID wizard at all** — dblp only *ingests* iDs (harvested
from publisher metadata and the ORCID dump) and never pushes works out, so there's
no connect button to find. dblp is excellent and irrelevant to this step.

## 2. One profile per index

- [ ] **Semantic Scholar:** claim your author page. If you have more than one page,
      claim **only** the primary — their docs prohibit holding two claims. There's
      no self-service merge, but a claimed page's *Edit Author Page → Add Papers*
      pulls papers across one at a time: choose *"the author is correct, but the
      paper is missing from my author page"*. `tasks/s2_merge.md` lists them
      citation-ordered. Support can merge for you, but quote your ORCID — that's the
      argument they can act on mechanically.
- [ ] **Google Scholar:** profile public, verified institutional email, photo, and
      correct affiliation. Merge duplicate entries; add missing articles by hand.
- [ ] **OpenAlex:** check for split profiles. Prefer fixing ORCID over filing
      anything — see item 5.
- [ ] **dblp:** check your author page isn't split across name variants, and that
      no one else's work is on it. Corrections take 8+ weeks, so file early.
- [ ] **ACL Anthology** (or your field's equivalent): confirm your person page
      exists and is not duplicated.

## 3. Wikidata — a free entity anchor

**Is this legitimate?** Yes. Wikidata's notability policy is not Wikipedia's:
criterion 2 admits any *clearly identifiable entity describable with serious,
publicly available references*; criterion 3 admits items that fulfil a *structural
need*. An author item with an ORCID and published papers is squarely both, and
hundreds of thousands exist, mostly auto-created from ORCID and Crossref. Unlike
Wikipedia there's no prohibition on creating an item about yourself — the
requirement is accuracy, not distance.

- [ ] Create a Wikidata account.
- [ ] Paste `tasks/wikidata.qs` into
      <https://quickstatements.toolforge.org/#/batch> and run it. Identifiers and
      affiliations only — nothing about importance, nothing unsourced.
- [ ] Record the new Q-number in `config.yaml` → `ids.wikidata` and rebuild, so it
      lands in the site's `sameAs` array.
- [ ] **Follow-up worth doing:** some of your papers probably already exist as
      Wikidata items imported from Crossref, with your name as a plain *author name
      string* (`P2093`) rather than a link to you. Upgrading those to `author`
      (`P50`) pointing at your Q-number is what turns the item into a real
      disambiguation anchor.

## 4. One canonical URL, and make it machine-readable

- [ ] Pick one URL and never change it. Static hosting beats a site builder here:
      AI crawlers largely don't execute JavaScript, so a JS-rendered page can rank
      fine in Google and be **empty** to Claude or Perplexity.
- [ ] Put that exact string in ORCID, Semantic Scholar, Google Scholar, arXiv,
      GitHub, LinkedIn, and every JSON-LD `sameAs`. Same string everywhere — this is
      what lets engines fuse the identity.
- [ ] `Person` JSON-LD with `sameAs` listing every profile. Check for placeholder
      values; a stub site with `you@example.com` in its structured data is asserting
      something false.
- [ ] `robots.txt` that allows `GPTBot`, `OAI-SearchBot`, `ClaudeBot`,
      `PerplexityBot`, `Google-Extended`. Check your **CDN/WAF too** — a permissive
      robots.txt with a blocking firewall rule is the common silent failure.
- [ ] `sitemap.xml`.
- [ ] One name form everywhere. `Jane Q. Smith` and `J. Smith` are two people to a
      disambiguation model.

## 5. OpenAlex duplicates

- [ ] Prefer doing nothing and finishing item 1: their merges are ORCID-driven.
- [ ] If you want it now, the *Fixing Author Profiles* form linked from
      <https://help.openalex.org/hc/en-us/articles/27714298573719-Fix-errors-in-OpenAlex>
      merges profiles, sets the display name, and removes wrong works.
      `tasks/openalex_merge.md` has the IDs. `support@openalex.org` is the fallback.

## 6. Code and artifacts

- [ ] GitHub topics and a real one-line description on every non-fork repo. Topics
      are GitHub's primary discovery facet and most accounts have none. 3–8 per
      repo, accurate; **omit rather than guess** — a wrong topic misleads retrieval,
      and padding the list is keyword stuffing.
- [ ] `CITATION.cff` on every repo backing a paper. GitHub renders a "Cite this
      repository" widget from it and it's machine-readable.
- [ ] The paper's arXiv link in the repo README — Hugging Face extracts the id and
      cross-lists the repo on the paper page automatically.
- [ ] Hugging Face: claim your account, then index and claim a paper page per arXiv
      paper. **Requires a logged-in browser** — an unauthenticated visit creates
      nothing.
- [ ] Model and dataset cards that link the paper.

## 7. Per-paper, from here on

- [ ] arXiv **journal-ref and DOI** once a paper is published. No write API, one web
      form each — and this is what Google Scholar matches citations on, so it's
      worth more than it looks.
- [ ] A generic gloss beside every coined name. `TIES-Merging`, `ZipNN`, `DOVE` have
      no lexical path from the question anyone actually types.
- [ ] One canonical sentence per finding, reused **verbatim** in the paper, README,
      model card, and talk abstract. Rewording each time fragments the signal.
- [ ] A sidecar: claims, scope conditions, terminology, common misreadings. The only
      part no tool can write, and the only lever on being described *correctly*.

---

## What not to bother with

Measured null or negative, so skip regardless of who recommends it:

- keyword stuffing, or padding topic lists
- `llms.txt` as a *crawler protocol* (Google: zero effect). The author-written
  content artifact is a different thing wearing the same name
- reformatting for "AI readability" — sectioned vs dense prose measured null
- backlink building as the primary lever
- extra preprint mirrors — multiplies versions and defeats the matching that merges
  a paper's preprint and published records
- anything invisible to humans: hidden text, instructions aimed at automated
  readers. Retraction-adjacent, and it doesn't work

Evidence for each: [../STUDY.md](../STUDY.md).
