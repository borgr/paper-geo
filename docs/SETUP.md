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
- [ ] **Fill the backlog in ONE upload.** *Works → + Add → Add BibTeX* →
      `tasks/orcid_import.bib`. Do not work through the DOI form 100 times.

      The standard advice prefers *Add DOI* because self-asserted BibTeX works are
      lower-trust and can duplicate what auto-update later adds. That objection is
      real but **narrow: it only applies to entries with no identifier**, because
      ORCID *groups works that share one*. So the generated file removes the failure
      mode instead of accepting it — every entry that can carry a DOI now does, with
      missing ones filled from arXiv's own DataCite DOI (`10.48550/arXiv.<id>`, which
      arXiv registers for **every** paper, back to the oldest ids). DOI-bearing
      entries come first; the handful with no identifier anywhere are last, and
      those are the only ones worth importing by hand or skipping.
- [ ] `tasks/orcid_dois.txt` is the same works one at a time. Keep it for spot-fixing
      a single record; it is not the bulk route.
- [ ] *Search & link → Crossref Metadata Search* — the wizard everyone recommends. It
      is genuinely flaky and can hang. If it does, don't fight it; the upload above
      already covers the same works.
- [ ] **Fill the profile fields that are actually facets**, not decoration:
      - *Also known as* — every form your name appears in. This is what a
        disambiguation model matches when a citation uses a variant.
      - *Websites & social links* — the **canonical URL must be present**. A second
        personal page (a site builder, a lab page) is not a problem *because it
        exists* — it's a problem when the canonical one is missing and the two are
        never declared to be the same person. List both, canonical first, and make
        sure each site links to the other. See §5.
      - *Keywords* — 5–10 phrases someone would actually type. Not coined names, and
        not single words: `model merging` is a query, `merging` isn't. Derive them
        from what you actually publish on rather than what you'd like to be known
        for — the point is matching real queries, not positioning.
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
- [ ] **HTML rendering: mostly not actionable, and worth knowing why so you don't
      spend time on it.** arXiv renders LaTeX to HTML for submissions from late 2023
      on and is *gradually backfilling* the older corpus, so a paper without HTML
      today may get it later. But there is **no author-facing way to request it** —
      no form, no button. The only thing that reliably produces HTML is a submission
      whose LaTeX converts, which means:
      - **Don't post a new version just to get HTML.** Extra versions fragment
        citation matching, and that costs more than the HTML gains. If you're posting
        a v2 anyway (camera-ready, corrections), preview the HTML while you're there.
      - **Future submissions:** follow arXiv's LaTeX best-practice guide and preview
        the conversion at submission — unsupported packages are what break it. This is
        the only point where you have real leverage.
      - **Existing HTML that renders badly** can be reported in-page (the *Open
        Issue* button, or `Ctrl+?`). That's a genuine fix, unlike requesting new HTML.
      - **Papers with no HTML:** ar5iv (`ar5iv.org/abs/<id>`) is the community
        fallback and this tool already links it automatically on every such paper, so
        the crawler-readable version exists whether or not arXiv gets there.
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
- [ ] **Google Scholar** — five concrete things, in order of payoff:
      1. **The five *interests*.** These are links, not tags: each one is a browsable
         Scholar page and they drive "related authors". Empty is the common state and
         a pure loss. Use the top five of `identity.keywords`.
      2. **Profile public** (it defaults to private) and email verified against the
         institutional domain — that's what makes the profile authoritative for the
         name.
      3. **Merge duplicate entries.** Select the duplicates → *Merge*. Scholar splits
         preprint and published records when the journal-ref is missing, which is the
         same root cause as the arXiv work in §2 — fix it there and fewer appear here.
      4. **Homepage = the canonical URL**, and affiliation matching ORCID's employment.
      5. Turn on *email alerts for new citations* — not visibility, but it's how you
         notice a mis-attributed paper early, while it's still one record.
- [ ] **OpenAlex:** check for split profiles. Prefer fixing ORCID over filing
      anything — see item 6.
- [ ] **dblp:** check your author page isn't split across name variants, and that
      no one else's work is on it. Corrections take 8+ weeks, so file early.
- [ ] **OpenReview:** it looks complete because submissions populate it, but the
      fields that matter for identity are the ones *you* type and nothing fills:
      ORCID, DBLP, Semantic Scholar, GitHub, homepage, and **every name variant plus
      every past email**. Those emails are what merge your duplicate `~Name1` /
      `~Name2` profiles, which is the failure mode here — check for a second profile
      under an old institutional address. Also confirm *Expertise* is filled, and that
      the affiliation history has no gaps (it's used for conflict-of-interest, so gaps
      cause real problems beyond retrieval). The API is behind a bot challenge, so
      this one can't be audited from here — check it by hand at
      <https://openreview.net/profile>.
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
- [ ] **Getting to 50 edits is not a chore you do separately.** The follow-up below
      *is* the 50 edits: reassigning your papers from author-name-string to author
      link is one edit per paper, and you have well over 50 papers. So the order is
      create the item by hand → work Author Disambiguator → you are autoconfirmed as
      a side effect, with QuickStatements available for any future batch. Nothing
      needs to be padded, and no make-work edits — those are frowned on anyway.
- [ ] Record the new Q-number in `config.yaml` → `ids.wikidata` and rebuild, so it
      lands in the site's `sameAs` array.
- [ ] **Follow-up worth doing:** some of your papers probably already exist as
      Wikidata items imported from Crossref, with your name as a plain *author name
      string* (`P2093`) rather than a link. Upgrading those to *author* (`P50`)
      pointing at your Q-number is what turns an isolated item into a hub that
      resolves. <https://author-disambiguator.toolforge.org> does it in bulk.

## 5. One canonical URL — and what to do with the page humans actually visit

The canonical URL is the **machine anchor**: the string that goes in every identity
field so engines fuse the profiles. That is a different job from *where you send
humans*, and conflating the two is what makes this question feel unanswerable.

- [ ] **Pick the machine anchor on stability, not content.** It must be a URL you
      will never change, on hosting that serves real HTML. A site builder loses on
      both counts — not because it's bad, but because "might be replaced one day" is
      disqualifying for a string you're about to write into a dozen registries.
- [ ] **Keep the human site.** A second page is not a penalty. It becomes one only
      while nothing declares the two to be the same person, because then an engine
      has two candidate homepages and no basis to merge them.
- [ ] **Declare the link, in both directions.** List the human site in `sameAs`
      (`identity.other_pages` in `config.yaml` does this automatically) and in ORCID
      *Websites & social links* next to the canonical URL. Then add a plain
      `<a href>` from the human site back to the canonical one. Two links and the
      competition stops.
- [ ] **Check what a crawler actually sees on the site-builder page** before assuming
      it carries your content. Fetch it with JavaScript disabled and count the text.
      The failure is worse than "fewer words": nav items are frequently rendered as
      *unlinked text*, so a crawler cannot even discover the Publications page —
      there are no `href`s to follow, and the content is unreachable rather than
      merely thin.
- [ ] **Worth ~$10/year:** a domain you own, pointed at the static site. It makes the
      canonical URL survive every future platform change, and it's also the
      prerequisite for crawler logs (see the measurement section) — a
      `*.github.io` subdomain can't be put behind a CDN, so you can't see who
      fetched it.
- [ ] Put the canonical string in ORCID, Semantic Scholar, Google Scholar, arXiv,
      GitHub, OpenReview, LinkedIn, and every JSON-LD `sameAs`. Identical each time.
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
      scratch. This turns code into a citable object with DataCite metadata, so it
      enters OpenAlex and can accrue citations of its own instead of being an
      untracked URL in a footnote. Exact steps, because the ordering trips people:
      1. Sign in to <https://zenodo.org> **with GitHub** (that's what creates the
         link; a separate Zenodo account won't see your repos).
      2. <https://zenodo.org/account/settings/github/> → find the repo → flip the
         switch **on**. Nothing is archived yet; the switch installs a webhook.
      3. **Then** cut a GitHub release (`Releases → Draft a new release`, tag it,
         publish). The webhook only fires on releases created *after* the switch —
         existing tags are not picked up, which is the step people miss.
      4. Zenodo mints **two** DOIs: one for that release, and a **concept DOI** that
         always resolves to the newest version. Cite the concept DOI in the paper and
         README; cite the version DOI when reproducibility depends on exact code.
      5. Add the concept DOI to `CITATION.cff` (`doi:`) and put Zenodo's badge in the
         README. GitHub then renders "Cite this repository" with the DOI in it.
      6. Fix the Zenodo record's metadata once — authors with ORCIDs, license, and the
         **related identifier** `is supplement to` → your paper's DOI. That last field
         is what joins code and paper in DataCite, and it does not fill itself in.
      - Skip this for scratch repos. A DOI on abandoned code is noise, and every
        record is permanent.
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

**Works today, no domain needed:**

- [ ] **Google Search Console** — verify by adding the HTML-tag or file to the site
      (works fine on `*.github.io`), submit `sitemap.xml`. Then *Pages* tells you
      crawled-vs-indexed per URL, and *Performance* gives real queries that surfaced
      your pages. This is the difference between "nobody asks" and "nobody can see
      it", and they are opposite problems.
- [ ] **Bing Webmaster Tools** — same, and it matters beyond Bing: several answer
      engines read Bing's index, so a page missing here is missing from them too. It
      can import the Search Console verification, so this is two minutes.
- [ ] **Analytics won't answer this.** Google Analytics, Plausible, Cloudflare Web
      Analytics are all JavaScript beacons, and the crawlers you care about don't run
      JavaScript — so they are invisible in exactly the tool you'd reach for. Same
      trap for a tracking-pixel image: most AI crawlers fetch the HTML and no
      subresources, so the pixel never loads and the log stays empty. **An empty log
      would read as "no crawlers came" when it means "the method can't see them".**

**Needs a custom domain (~$10/year), and this is the only way to get real crawler
evidence:**

- [ ] **Server-side request logs, via a CDN in front of the site.** GitHub Pages
      exposes no logs, and you **cannot** put a `*.github.io` subdomain behind
      Cloudflare — proxying requires controlling the domain's nameservers. So the
      sequence is: buy a domain → point it at GitHub Pages (custom domain in repo
      settings) → move DNS to Cloudflare's free plan → proxy on.
- [ ] What you get for that: Cloudflare's free tier includes **AI Crawl Control**
      (formerly AI Audit), a per-crawler view of which AI services fetched which
      paths. That is direct evidence `GPTBot` / `ClaudeBot` / `PerplexityBot` /
      `OAI-SearchBot` reached your pages — plus the fastest way to catch a firewall
      rule silently blocking them, which is the common silent failure and is
      undetectable from outside.
- [ ] The domain pays for itself twice: it also makes the canonical URL survive any
      future hosting change (§5), which a platform subdomain does not.

**Local, every run:**

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
