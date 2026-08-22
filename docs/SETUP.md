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

Several steps below finish somewhere else, days or months later: arXiv staff verify
an ownership claim by hand, a Wikidata account autoconfirms after four days, ORCID's
auto-update and the ORCID-driven author merges at Semantic Scholar and OpenAlex run on
nobody's published schedule.

Put each one in `data/followups.yaml` with an absolute `due` date, what you are waiting
for, and what becomes possible when it lands. `update.py` prints anything due at the top
of `WORKLIST.md`, so the next run is the reminder.

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

      The usual objection to BibTeX import — self-asserted works are lower-trust and
      can duplicate what auto-update later adds — applies only to entries with **no
      identifier**, because ORCID *groups works that share one*. So every entry in the
      generated file that can carry a DOI does, with missing ones filled from arXiv's
      own DataCite DOI (`10.48550/arXiv.<id>`, registered for **every** arXiv paper
      back to the oldest ids). DOI-bearing entries come first; the handful with no
      identifier anywhere are last, and are the only ones worth importing by hand.
      **Once the upload lands**, `audit_identity.py` reads the public works count back
      and reports it. Two fields the import does not fill are worth the same session:
      the **canonical URL** in *Websites & social links*, and the **keywords**.
- [ ] **Check the record for works that are not yours** after any bulk import, and
      after every auto-update window. ORCID is read as *your assertion* by Semantic
      Scholar, OpenAlex, Crossref and publishers' submission systems, so a stray work
      is a false authorship claim that propagates — and a CV bibliography contains the
      works you *cite*, so an import built from one carries them in.
      `audit_identity.py` diffs the live record against `data/papers.yaml` and writes
      `tasks/orcid_remove.md` with the put-code for each stray, since similar titles
      are impossible to tell apart in the *Works → ⋮ → Delete* UI.
- [ ] `tasks/orcid_dois.txt` is the same works one at a time. Keep it for spot-fixing
      a single record; it is not the bulk route.
- [ ] *Search & link → Crossref Metadata Search* — the wizard everyone recommends. It
      is genuinely flaky and can hang. If it does, don't fight it; the upload above
      already covers the same works.
- [ ] **Fill the profile fields that are actually facets**, not decoration:
      - *Also known as* — every form your name appears in. This is what a
        disambiguation model matches when a citation uses a variant. Real variants
        only here; misspellings go somewhere else, see
        [Misspellings of your name](#misspellings-of-your-name-are-a-separate-list).
      - *Websites & social links* — the **canonical URL must be present**. A second
        personal page (a site builder, a lab page) is not a problem *because it
        exists* — it's a problem when the canonical one is missing and the two are
        never declared to be the same person. List both, canonical first, and make
        sure each site links to the other. See §5.
      - *Keywords* — the whole of `identity.keywords`; ORCID sets no cap. How to
        choose them, and the four other places they belong, is a section of its
        own: [Keywords](#keywords-choosing-them-and-where-they-go).
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
- [ ] **HTML rendering: mostly not actionable.** arXiv renders LaTeX to HTML for
      submissions from late 2023 on and is *gradually backfilling* the older corpus,
      but there is **no author-facing way to request it** — no form, no button. The
      only thing that reliably produces HTML is a submission whose LaTeX converts:
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
         a pure loss. Use the top five of `identity.keywords` — and *ranked*, because
         five slots against a longer list makes this a choice rather than a list.
         See [Keywords](#keywords-choosing-them-and-where-they-go).
      2. **Profile public** (it defaults to private) and email verified against the
         institutional domain — that's what makes the profile authoritative for the
         name.
      3. **Merge duplicate entries.** Select the duplicates → *Merge*. Scholar splits
         preprint and published records when the journal-ref is missing, which is the
         same root cause as the arXiv work in §2 — fix it there and fewer appear here.
      4. **Homepage = the canonical URL** — the machine anchor (§5), not the
         site-builder page, even though this is one of the few identity fields a human
         clicks. One sympathetic exception recreates the two competing homepages §5
         exists to prevent; serve the human case with a prominent link to the human
         site at the top of the canonical page instead. Affiliation should match
         ORCID's employment exactly.
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
- [ ] Record the new Q-number in `config.yaml` → `ids.wikidata` and rebuild, so it
      lands in the site's `sameAs` array.
- [ ] **Measure how many of your papers are already there before planning any work on
      them.** `audit_identity.py` checks every paper's DOI against Wikidata and reports
      the count. Do this first: the standard advice for this step assumes an answer
      that is often wrong.

      That advice is that your papers already exist as items auto-imported from
      Crossref, carrying your name as a plain *author name string* (`P2093`) rather
      than a link, and that <https://author-disambiguator.toolforge.org> upgrades
      those to *author* (`P50`) → your Q-number in bulk. Where true it is the best
      thing on this page: one edit per paper, and it earns autoconfirmed status as a
      side effect. But Wikidata's coverage of CS literature is **sporadic, not a
      pipeline** — the systematic Crossref imports ran years ago and publisher DOIs
      fare far better than arXiv-DataCite-only ones — so a corpus of mostly preprints
      and ACL-Anthology papers can have single-digit coverage, leaving Author
      Disambiguator nothing to operate on.

      One trap if you measure it yourself: Wikidata **split its query service**,
      moving scholarly articles out of the main graph. A publication query against
      `query.wikidata.org` now returns zero rows with an HTTP 200, which reads as
      "none of my papers are there". Publication SPARQL belongs at
      `query-scholarly.wikidata.org`. The audit uses that endpoint; so must any query
      you write.
- [ ] **Decide about autoconfirmed only after that count.** With low coverage,
      creating items for your own papers is the only route to 50 edits. Worth it if
      you want a queryable graph of your corpus; not worth it just to unlock
      QuickStatements, since the author item itself is ~15 minutes by hand. Never pad
      with make-work edits — nothing downstream reads edit count.
- [ ] **If you decide yes, the audit writes the batch.** `tasks/wikidata_papers.qs`
      holds one `CREATE` per missing paper with a DOI or arXiv id — title, date,
      identifier, and the author list with you linked and co-authors as strings.
      Note the ordering, which is circular and easy to miss: the batch runs in
      QuickStatements, which needs autoconfirmed, which needs the 50 edits. So the
      first ~50 items go in through the web form (no gate), and the batch does the
      rest. Preview the first ten rows before releasing the whole thing; items are
      permanent and far harder to clean up than anything in this repo.

## Misspellings of your name are a separate list

If you have co-authors, some published record of yours misspells your name. A
one-character slip does not degrade gracefully: it creates a second author who owns
that paper's citations and cannot be merged with you. Two different jobs follow, and
the mistake is doing only the first.

- [ ] **Fix it upstream wherever it is still writable.** arXiv metadata first — it is
      what Hugging Face, Semantic Scholar, OpenAlex and Google Scholar all build author
      identity from, so one edit there corrects every index at once. `tasks/
      arxiv_name_fixes.md` lists which of your records are wrong and what each one
      reads. Then the publisher's record via Crossref, if the venue will do it.
- [ ] **Then accept that some of them are permanent, and route around those.** A typo
      in someone *else's* reference list is not yours to fix and never will be. Those
      strings will be resolved by tools for as long as the citing paper exists.
- [ ] **Publish the misspellings as Wikidata aliases — and nowhere else.** An alias
      there is a lookup key, not an assertion about spelling, and their guidelines name
      common misspellings as a reason to add one. So a reconciler holding `Leshem
      Chosen` from a 2024 citation lands on your item instead of inventing an author.
      Put them in `identity.name_typos` in `config.yaml` and the audit adds them.
- [ ] **Do not put them in ORCID's *also known as*, in your site's schema.org
      `alternateName`, or in your `name_variants`.** Those three are *assertions* — they
      say this is a form of your name that you use, which is false and reads as sloppy
      on a public profile. And a typo listed as a known variant stops being reported as
      a typo, so the upstream record it came from never gets fixed. That is why this
      tool keeps two lists that look interchangeable and are not: `name_variants` are
      asserted, `name_typos` are only matched and aliased. `validate.py` fails if a
      string ends up in both.
- [ ] **One test before adding a string: does it collide with a real person?** A
      mangled given name or a one-letter surname slip is usually nobody. Initials-only
      or surname-only forms are usually somebody, and belong on neither list.

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
- [ ] **Zenodo ↔ GitHub.** This turns code into a citable object with DataCite
      metadata, so it enters OpenAlex and can accrue citations of its own instead of
      being an untracked URL in a footnote.

      **Which repos, though** — the deciding question is not "is there a paper" but
      *"is there anything citable here that the paper's own citation does not already
      cover?"* Three cases, and only one of them is a clear yes:

      - **Artifact with no paper of its own** — a tool, a harness, a dataset loader, a
        set of trained checkpoints. **Yes, always.** Without a DOI this work can only
        appear as a bare URL in someone's footnote, which no index counts, so its
        citations do not exist as data.
      - **Code that implements a paper you also published** — *usually not needed*: a
        second DOI for the same contribution gives citers two things to cite and
        splits the count. Do it anyway when reproducibility depends on the exact code
        state (people need to cite a *version*, not the paper), or when a venue or
        funder requires a deposited artifact. Then set `preferred-citation` in
        `CITATION.cff` to the **paper**, so GitHub's "Cite this repository" widget
        hands out the paper citation while the Zenodo DOI stays available for anyone
        citing the code. The tool writes that field for you.
      - **Scratch, coursework, forks, one-off scripts** — no. Zenodo records are
        permanent and cannot be withdrawn on a whim.

      You do not have to sort your own repos into those three cases. The sweep does
      it from `kind` and whether a paper is linked, and writes the first case to
      `tasks/zenodo.md` on every run; recording the concept DOI as `zenodo_doi:` in
      `data/repos.yaml` is what takes a repo off that list and puts the DOI into its
      `CITATION.cff`.

      Exact steps, because the ordering trips people:
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
         is what joins code and paper in DataCite, and it does not fill itself in. It
         is also what makes the two-DOI case above harmless: once the link exists, an
         index can see one contribution with two representations rather than two
         unrelated objects.
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
- [ ] A sidecar: claims, scope conditions, terminology, common misreadings — the only
      lever on being described *correctly*. `python scripts/draft_sidecars.py` drafts
      it from the paper; you check the numbers and the scope, then `--accept`.

---

## Which link goes where

The answer is different per field. Four rules cover every case below:

1. **A field that holds exactly one URL gets the canonical URL. No exceptions.** Its
   value comes from being the same string in every registry; the first sympathetic
   exception ("but humans read this one") is what recreates two competing homepages.
2. **A field that holds many URLs gets everything, canonical first.** A second
   personal page is only a problem while nothing says the two are the same person.
   Listing both *is* the statement that fixes it.
3. **A typed identifier field gets the bare id, never a URL.** `borgr`, not
   `https://github.com/borgr`. Typed fields are format-validated and traversable by
   tools; a URL pasted into one either fails validation or silently degrades to text.
4. **A per-paper surface gets per-paper links.** A repo's website field pointing at
   your homepage wastes the one slot that could have pointed at the paper. Your
   homepage is reachable from the paper page anyway.

| where | field | what goes in it |
|---|---|---|
| **ORCID** | *Websites & social links* (many) | canonical URL first, then the human site, then GitHub, Scholar, Semantic Scholar, LinkedIn, HF. This is the one profile that should hold *all* of them — every other service reads ORCID, so it is the hub rather than another leaf. |
| **Google Scholar** | *Homepage* (one) | canonical URL. Rule 1 — see §3.4 for why, since this is the field where the temptation is strongest. |
| **Semantic Scholar** | claimed page → homepage | canonical URL. Plus your ORCID, which is the field their disambiguation actually consumes. |
| **arXiv** | — | nothing to paste. There is no author URL field; the ORCID link (§1) is the mechanism, and `arxiv.org/a/<orcid>` is the page you get out. Embed its `myarticles` widget on your own site if you want the flow reversed. |
| **GitHub profile** | *Website* (one) + *Social accounts* (4) | canonical URL in Website; Scholar, ORCID, LinkedIn, HF in the four social slots. Almost nobody fills those four, and they render as icons that both humans and crawlers follow. |
| **GitHub repo** | *About → Website* (one) | **the paper's page on your site** — not your homepage. Rule 4. For a repo with no paper, your homepage is the fallback. |
| **GitHub repo** | README, near the top | the arXiv `abs` link, the paper page, and the Zenodo badge if there is one. The arXiv link is load-bearing beyond being a link: **the HF Hub parses the id out of the README and cross-lists your repo on the paper page automatically**, so this one line buys a backlink from a domain you do not control. |
| **GitHub repo** | `CITATION.cff` | the paper DOI under `preferred-citation`, and the Zenodo concept DOI at top level if it exists. Generated for you. |
| **OpenReview** | *Homepage, ORCID, DBLP, Semantic Scholar, GitHub, LinkedIn* | all of them. These are typed fields, they are empty by default, and submissions never fill them — this is the profile that looks complete and is not. |
| **LinkedIn** | *Contact info → Websites* (3) + *Featured* | canonical URL, human site, Scholar. |
| **Wikidata** | `P856` *official website* (one) | canonical URL, and **only** that. Everything else has a typed property — see `tasks/wikidata_followup.md`. This is rule 3 at its starkest: a profile URL added beside P856 does not become queryable, it just adds a second candidate homepage. |
| **Wikidata** | typed identifier properties | ORCID, Scholar, Semantic Scholar, OpenAlex, DBLP, GitHub, HF, LinkedIn, OpenReview — as bare ids. Generated into `tasks/wikidata_manual.md`. |
| **HF profile** | homepage / GitHub / X fields | canonical URL and the ids. |
| **HF model / dataset card** | README body + frontmatter | the paper page, the arXiv link (same auto-extraction as above), the code repo. Per-paper surface, so per-paper links. |
| **Zenodo record** | *Related identifiers* | the paper DOI as `is supplement to`, and the repo URL. §7. |
| **Your site** | JSON-LD `sameAs` | every profile above, automatically, from `config.yaml`. Nothing to do by hand — which is the reason `config.yaml` is worth keeping accurate even for ids you think are dormant. |
| **The paper PDF itself** | footnote on page 1 | the code repo and the paper page. The only one of these a reader ever sees, and the only one you cannot retrofit after publication. |

The rows that say *generated* are done by `identity_tasks.py` / `sweep_github.py` /
`build_site.py`; the rest are logins, and `audit_identity.py` checks the ones with a
public API afterwards.

## Keywords: choosing them, and where they go

**What makes one good.** A keyword is a *query*, not a label. Five tests, in
descending order of how often they change an answer:

1. **Would someone who does not already know your work type it?** This is the test
   that rules out coined names. `TIES-Merging` is not a keyword, it is an alias — it
   belongs in a paper's `aliases` field, where the tool pairs it with a generic gloss.
   `model merging` is what gets typed.
2. **Is it more than one word?** Single words are ambiguous and you will not win them.
   `evaluation` competes with the entire internet; `evaluation of language models` is
   a phrase with an actual population of authors, and you can be near the top of it.
3. **Do you have a *cluster* of papers on it?** These are comparative facets — a
   Scholar interest is a browsable page that ranks everyone who claimed it. One paper
   puts you at the bottom of that page, which is worse than absent because it spends a
   slot. Ten puts you near the top. Count before adding.
4. **Is it the field's term or yours?** Where two names exist for the same thing, the
   one with more papers wins, even if the other is better. You are matching queries,
   not naming things.
5. **Is it mid-abstraction?** `natural language processing` is unwinnable but earns
   membership in the right neighbourhood, so one or two of those are worth having.
   `reference-free MT evaluation with pretrained metrics` is precise and nobody types
   it. The bulk should sit in between.

**Is more better? No — and for different reasons in each place.** Google Scholar takes
five and they are links, so `identity.keywords` has to be *ranked*: a new keyword can
only get in by displacing one that would have ranked. ORCID has no cap, but keywords
there feed disambiguation rather than ranking: a profile claiming thirty things matches
all of them weakly, which is the opposite of the goal. Ten to fifteen is where each
still carries weight. On the site itself, padding is keyword stuffing, which is
measured-negative — see [EVIDENCE.md](EVIDENCE.md).

**What you are most likely missing** is not a phrase but a *cluster*: five or more of
your papers that no current keyword covers. Two passes over your own bibliography —
for each keyword, count the papers it plausibly covers and cut anything at one; then
look for a subject with several papers and no keyword pointing at it. Two things to
weigh while you are there:

- **Overlap eats the Scholar five.** Near-synonyms are separate facets in ORCID and
  near-duplicates in the Scholar five: if three or four of your list are variations on
  one subject, most of your profile ends up saying one thing. Consolidate deliberately
  for the five, keep the variants everywhere with no cap.
- **Dropping a topic you have stopped working on is a real trade, not a tidy-up.** A
  cluster of older papers is exactly where you rank highest, because the field moved
  on and you are still on the page. Currency is a fine reason to drop one; just make
  it a decision rather than a side effect of updating the list.

**Where they go** — the same set, five different shapes:

| where | how many | shape |
|---|---|---|
| **Google Scholar** *interests* | exactly 5, ranked | one per slot, verbatim, lowercase as written |
| **ORCID** *Keywords* | all of them | one per entry — **not** one comma-joined string, which is the same mistake that broke the Wikidata aliases |
| **OpenReview** *Expertise* | all of them | each with the years you worked on it; the years are a field there and they are used |
| **LinkedIn** *Skills* + headline | top ~5 | Skills is a matched facet there, not decoration |
| **Your site** `Person.knowsAbout` | all of them | automatic, from `config.yaml` |

Two places they should **not** go: GitHub repo topics, which are per-repo and describe
that code rather than you, and the body text of any page, which is stuffing. And
`identity.keywords` in `config.yaml` is the single source — edit there, re-run
`audit_identity.py`, and it will tell you which of the above are out of date.

---

## How to tell any of it landed

You can't measure citations caused (see [EVIDENCE.md](EVIDENCE.md) for why, at this
sample size). You *can* measure the two stages before that, which is where the
failures actually are:

**Works today, no domain needed:**

These two are the only free way to distinguish **"nobody asks"** from **"nobody can
see it"** — opposite problems with opposite fixes. Fifteen minutes, once.

- [ ] **Google Search Console.** <https://search.google.com/search-console>
      1. *Add property* → **URL prefix** (not Domain — Domain verification needs DNS,
         which you do not control on `*.github.io`) → your `identity.canonical_url`,
         exactly as it appears in `config.yaml`, trailing slash included. A prefix
         property only reports on URLs that start with the string you typed, so
         `http` vs `https` or a missing slash silently reports on nothing.
      2. Choose the **HTML tag** method and copy just the `content="..."` value — the
         token, not the whole tag.
      3. Paste it into `config.yaml` → `site.verification.google`, then
         `python scripts/build_site.py --deploy`.
      4. Wait for the deploy (a minute or two), then press *Verify*.
      5. *Sitemaps* → submit `sitemap.xml`. Generated already, so it is one paste.

      **Through the config, not by hand:** `--deploy` empties the Pages repo before
      copying `build/site` into it, so an HTML file you upload yourself vanishes at the
      next deploy and the property silently un-verifies. Deploy *before* pressing
      Verify — the tag has to be live first.

      What you get: *Pages* gives crawled-vs-indexed per URL — the one report that
      would tell you whether every paper page is being crawled and then dropped, which
      no other tool here can see. *Performance* gives the real queries that surfaced
      them.
- [ ] **Bing Webmaster Tools.** <https://www.bing.com/webmasters>
      1. *Add site* → try **Import from Google Search Console** first; if it works,
         you are done and can skip the rest.
      2. Otherwise add the same canonical URL manually, take the **HTML Meta Tag**
         token, and put it in `site.verification.bing` — same generate-and-deploy
         sequence as above. Both tokens can be set in one pass.
      3. Submit the same `sitemap.xml`.

      Worth more than Bing's search share suggests: **ChatGPT's search grounding leans
      on Bing's index**, so a page missing here is missing from an answer engine you
      actually care about — and this is the only place that will tell you.
- [x] **IndexNow — wired, and refused by this host.** Nothing for you to do until the
      site has a custom domain (see below). Instead of waiting to be crawled, the
      deploy *tells* Bing, Yandex, Seznam and Naver (not Google, which does not
      participate) which URLs changed, and they fetch within minutes to days.

      No account, no application. The key is any 8–128 characters of `[A-Za-z0-9-]`
      you pick yourself, and what proves control is serving it at
      `<base_url>/<key>.txt`, which `build_site.py` writes on every build.
      `site.indexnow_key` is therefore in `config.yaml` and committed on purpose: the
      key is *meant* to be public, and the worst a stranger who copies it can do is
      ask Bing to recrawl pages that are already yours.

      A `*.github.io` subdomain cannot prove control that way, because the domain is
      GitHub's. The key file serves 200 and matches, and IndexNow answers
      `403 UserForbiddedToAccessSite` to the batch and single-URL endpoints alike.
      `--deploy` says so in one line and carries on; it is not a state to retry. Bing,
      Yandex and Seznam still reach these URLs from the sitemap, slower. A custom
      domain turns this on with no further work — the key file is already published.

      What it buys: a rebuild that adds thirty paper pages at once is the case organic
      discovery handles worst. It changes *when* a page becomes eligible, not how it
      ranks.
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

Evidence for each: [EVIDENCE.md](EVIDENCE.md).
