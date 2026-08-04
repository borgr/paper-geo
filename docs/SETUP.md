# The one-time checklist

Do these once, in this order, before touching any per-paper work. They're
independent of this tool — it just generates the payloads and tracks what's left.

Ordered by leverage ÷ effort. Items 1–3 fix *who you are* across every index, and
nothing downstream works properly until identity resolves to one person.

Two commands support this page:

```bash
python scripts/identity_tasks.py     # writes the payloads into ../tasks/
python scripts/audit_identity.py     # live-reads ORCID, arXiv, Wikidata, HF: what is still open
```

The audit is the one to re-run. Every box below is checkable from public APIs
without a login, even though every *fix* needs one — so you can always tell what is
actually done rather than what you remember doing.

---

## 1. ORCID — populate it, then wire it everywhere

**Why first:** it's the lever for items 2 and 6. Semantic Scholar disambiguates on
ORCID, arXiv builds a public author page from it, and OpenAlex is running
ORCID-driven merges of split author profiles. Fixing ORCID makes those fix
themselves — and keeps them fixed after future re-clustering.

- [ ] Have an ORCID iD (free, 2 minutes) — <https://orcid.org/register>
- [ ] **Set default visibility to *Everyone*** — *Account settings → Visibility
      preferences* — **before** importing anything. Only the public API is readable
      by Semantic Scholar, OpenAlex and Crossref; a record whose works are set to
      *trusted parties* looks identical to an empty one from outside, and you will
      not notice.
- [ ] **Turn on auto-update** for **Crossref** and **DataCite**: *Works → Search &
      link*, authorise both, and grant standing permission. Covers only works whose
      deposited metadata already contains your iD, so this fixes the *future*.
      Published DOIs are Crossref; arXiv DOIs are DataCite — you want both.
- [ ] **Link your arXiv account to your ORCID** —
      <https://arxiv.org/user/confirm_orcid_id>. Two payoffs: it puts your iD into
      arXiv's DataCite metadata, which is what makes DataCite auto-update fire on
      future preprints, and it creates the public author page in item 2.
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
- [ ] **Fill the profile fields that are actually facets**, not decoration:
      - *Also known as* — every form your name appears in. This is what a
        disambiguation model matches when a citation uses a variant.
      - *Websites & social links* — your **canonical URL**, and nothing that
        competes with it. If an old site-builder page is listed here, replace it: it
        competes for the same identity, and Wix/Squarespace/Notion pages are
        JS-rendered, so AI crawlers that don't run JavaScript see an empty document.
      - *Keywords* — 5–10 phrases someone would actually type. Not coined names.
      - *Employment* and *Education* — what powers institutional disambiguation.
- [ ] Put your iD in your email signature and on every paper you submit. That's the
      mechanism that makes auto-update work without you.

**Wizards that will disappoint you, and why:** *Scopus* looks empty because Scopus
indexes little arXiv/ACL content and the wizard needs a Scopus Author ID you may not
have. **dblp is not an ORCID wizard at all** — dblp only *ingests* iDs (harvested
from publisher metadata and the ORCID dump) and never pushes works out, so there's
no connect button to find. dblp is excellent and irrelevant to this step.

## 2. arXiv — claim your papers, then use the author page you get for free

Most people stop at "I have papers on arXiv" and miss that arXiv tracks, separately,
which papers *your account* is registered as an author on — its **authority
records**. For anyone with co-authors, that set is usually a fraction of their
corpus, because it defaults to whoever pressed submit.

- [ ] **Claim ownership of every paper you co-authored.** Two routes:
      *with the paper password* (it's in the submitter's acceptance email — ask the
      submitting co-author) at <https://arxiv.org/auth/need-paper-password>, instant;
      or *without it* at <https://arxiv.org/auth/request-ownership>, which arXiv
      staff verify in a couple of days and needs no co-author involvement. For a long
      tail of old papers the second is less work: submit them in a batch and forget.
      `tasks/arxiv_ownership.md` lists exactly which papers are missing, citation-ordered.
- [ ] **Then use the author page.** Once ORCID is linked,
      `https://arxiv.org/a/<your-orcid>` is a public publication list *on arxiv.org*
      — plus an Atom feed (`.atom2`) and an embeddable `myarticles` widget for your
      own site. A high-crawl-authority domain listing your papers, for zero ongoing
      work. It is built from the authority records, so it's only as complete as the
      step above.
- [ ] **Add journal-ref and DOI after publication.** <https://arxiv.org/jref>. This
      is what Google Scholar matches citations on, and what merges a paper's preprint
      and published records into one entry instead of two. No write API — one web
      form each. **You can only do this on papers you own**, which is why claiming
      comes first.
- [ ] **Share the paper password with all co-authors** on your own future
      submissions. Costs nothing, and saves each of them the claim form.
- [ ] **Check the HTML rendering.** arXiv renders LaTeX submissions to HTML and is
      backfilling the older corpus; where it exists it's linked under the PDF on the
      abstract page. HTML is what a crawler that doesn't parse PDFs can read. You can
      preview it during submission — worth a look, since unsupported LaTeX packages
      are what break conversion. For older papers with no HTML, ar5iv
      (`ar5iv.org/abs/<id>`) is the community fallback, and this tool links it
      automatically.
- [ ] **Pick the license deliberately on new submissions.** arXiv's default
      perpetual non-exclusive license grants distribution rights to arXiv and
      *limits re-use by anyone else*; CC BY permits redistribution and derivative
      use. The choice is **irrevocable per version**, so it's a decision to make at
      submission, not later. Weigh it against your publisher's terms — this is a
      rights question first and a reach question second.

## 3. One profile per index

- [ ] **Semantic Scholar:** claim your author page. If you have more than one page,
      claim **only** the primary — their docs prohibit holding two claims. There's
      no self-service merge, but a claimed page's *Edit Author Page → Add Papers*
      pulls papers across one at a time: choose *"the author is correct, but the
      paper is missing from my author page"*. `tasks/s2_merge.md` lists them
      citation-ordered. Support can merge for you, but quote your ORCID — that's the
      argument they can act on mechanically.
- [ ] **Google Scholar:** profile public, verified institutional email, photo,
      correct affiliation, homepage = your canonical URL. Merge duplicate entries and
      add missing articles by hand. Fill the five *interests* — they're a real facet,
      linked and searchable, and they drive "related authors".
- [ ] **OpenAlex:** check for split profiles. Prefer fixing ORCID over filing
      anything — see item 6.
- [ ] **dblp:** check your author page isn't split across name variants, and that
      no one else's work is on it. Corrections take 8+ weeks, so file early.
- [ ] **OpenReview:** fill the ORCID, DBLP and homepage fields, and list name
      variants. It's where submissions and reviews live in ML, and its profile data
      propagates into venue metadata.
- [ ] **ACL Anthology** (or your field's equivalent): confirm your person page
      exists and is not duplicated.

## 4. Wikidata — a free entity anchor

**Is this legitimate?** Yes. Wikidata's notability policy is not Wikipedia's:
criterion 2 admits any *clearly identifiable entity describable with serious,
publicly available references*; criterion 3 admits items that fulfil a *structural
need*. An author item with an ORCID and published papers is squarely both, and
hundreds of thousands exist, mostly auto-created from ORCID and Crossref. Unlike
Wikipedia there's no prohibition on creating an item about yourself — the
requirement is accuracy, not distance.

- [ ] Create a Wikidata account.
- [ ] **Create the item by hand**, following `tasks/wikidata_manual.md`:
      <https://www.wikidata.org/wiki/Special:NewItem>, then add the statements from
      the table. ~15 minutes. Identifiers and affiliations only — nothing about
      importance, nothing unsourced.
- [ ] *Not* QuickStatements, at least not at first: it requires an **autoconfirmed**
      account (4 days old, 50 edits) and fails with an authorisation error rather
      than telling you why. `tasks/wikidata.qs` is there for when you qualify.
- [ ] Record the new Q-number in `config.yaml` → `ids.wikidata` and rebuild, so it
      lands in the site's `sameAs` array.
- [ ] **Follow-up worth doing:** some of your papers probably already exist as
      Wikidata items imported from Crossref, with your name as a plain *author name
      string* (`P2093`) rather than a link. Upgrading those to *author* (`P50`)
      pointing at your Q-number is what turns an isolated item into a hub that
      resolves. <https://author-disambiguator.toolforge.org> does it in bulk.

## 5. One canonical URL, and make it machine-readable

- [ ] Pick one URL and never change it. Static hosting beats a site builder here:
      AI crawlers largely don't execute JavaScript, so a JS-rendered page can rank
      fine in Google and be **empty** to Claude or Perplexity.
- [ ] Put that exact string in ORCID, Semantic Scholar, Google Scholar, arXiv,
      GitHub, OpenReview, LinkedIn, and every JSON-LD `sameAs`. Same string
      everywhere — this is what lets engines fuse the identity.
- [ ] **Retire or redirect the old ones.** A second personal page is not extra
      coverage, it's a second candidate identity for the same person.
- [ ] `Person` JSON-LD with `sameAs` listing every profile. Check for placeholder
      values; a stub site with `you@example.com` in its structured data is asserting
      something false.
- [ ] `robots.txt` that allows `GPTBot`, `OAI-SearchBot`, `ClaudeBot`,
      `PerplexityBot`, `Google-Extended`. Check your **CDN/WAF too** — a permissive
      robots.txt with a blocking firewall rule is the common silent failure.
- [ ] `sitemap.xml`.
- [ ] One name form everywhere. `Jane Q. Smith` and `J. Smith` are two people to a
      disambiguation model.

## 6. OpenAlex duplicates

- [ ] Prefer doing nothing and finishing item 1: their merges are ORCID-driven.
- [ ] If you want it now, the *Fixing Author Profiles* form linked from
      <https://help.openalex.org/hc/en-us/articles/27714298573719-Fix-errors-in-OpenAlex>
      merges profiles, sets the display name, and removes wrong works.
      `tasks/openalex_merge.md` has the IDs. `support@openalex.org` is the fallback.

## 7. Code and artifacts

- [ ] GitHub topics and a real one-line description on every non-fork repo. Topics
      are GitHub's primary discovery facet and most accounts have none. 3–8 per
      repo, accurate; **omit rather than guess** — a wrong topic misleads retrieval,
      and padding the list is keyword stuffing.
- [ ] `CITATION.cff` on every repo backing a paper. GitHub renders a "Cite this
      repository" widget from it and it's machine-readable.
- [ ] The paper's arXiv link in the repo README — Hugging Face extracts the id and
      cross-lists the repo on the paper page automatically.
- [ ] **Zenodo ↔ GitHub**, for repos that are a research artifact rather than
      scratch: switch the repo on in Zenodo, cut a release, and every future release
      gets a DOI plus a concept DOI covering all versions. That makes the code a
      citable object with DataCite metadata — so it enters OpenAlex and can accrue
      citations of its own, instead of being an untracked URL in a footnote.
- [ ] Hugging Face: claim your account, then index and claim a paper page per arXiv
      paper. **Requires a logged-in browser** — an unauthenticated visit creates
      nothing. `tasks/hf_worklist.md`, regenerated live by `audit_identity.py`.
- [ ] Model and dataset cards that link the paper.

## 8. Per-paper, from here on

- [ ] arXiv journal-ref and DOI once published (item 2).
- [ ] A generic gloss beside every coined name. `TIES-Merging`, `ZipNN`, `DOVE` have
      no lexical path from the question anyone actually types.
- [ ] One canonical sentence per finding, reused **verbatim** in the paper, README,
      model card, and talk abstract. Rewording each time fragments the signal.
- [ ] A sidecar: claims, scope conditions, terminology, common misreadings. The only
      part no tool can write, and the only lever on being described *correctly*.

---

## How to tell any of it landed

You can't measure citations caused (see [MEASURE.md](MEASURE.md) for why, at this
sample size). You *can* measure the two stages before that, which is where the
failures actually are:

- [ ] **Google Search Console** and **Bing Webmaster Tools** — verify the site,
      submit the sitemap. Both then tell you whether pages are crawled and indexed
      at all, which is the difference between "nobody asks" and "nobody can see it".
      Bing matters beyond Bing: several answer engines read its index.
- [ ] **Crawler logs.** GitHub Pages gives you none. Putting the site behind
      Cloudflare's free tier gets you per-user-agent request logs — the only direct
      evidence of whether `GPTBot`, `ClaudeBot` and `PerplexityBot` fetch your pages,
      and the fastest way to catch a WAF rule quietly blocking them.
- [ ] `python measure/check_structure.py` for our own artifacts, and
      `python scripts/audit_identity.py` for the external ones.

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
