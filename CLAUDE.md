# Working rules for this repo

## The one that governs everything else: an item is a destination, an instruction, and a payload

`WORKLIST.md` is the only file that asks the author for anything, and every open item in
it has to be workable without leaving the page. That means three things, and an item
missing any of them is a bug in the emitter, not a gap for the reader to close:

1. **A destination.** The exact URL to act at — deep-linked to the form or the record
   where possible, never just the site's front door — or the exact path in this repo.
   "Open ORCID" is not a destination; `https://orcid.org/my-orcid#works` is.
2. **The instruction, if it is more than open-and-paste.** The clicks in order, named
   the way the page names them (*Works → + Add → Add BibTeX*). If it *is*
   open-and-paste, say nothing: a step the reader can see is a step that wastes them.
3. **The payload, inline.** Every value they would otherwise have to look up or
   retype: the BibTeX, the DOI to remove and the one to add, the journal-ref string,
   the put-code, the URL to paste. A pointer to a file under `tasks/` is a supplement,
   never the only copy — opening a second file to find out what to type is the failure
   this rule exists to prevent.

The reader's whole job should be clicking and pasting. Anything that can be derived,
fetched, built, or checked is the code's job — see the ranking below.

## Do the work before asking

Before an item reaches `WORKLIST.md`, exhaust the cheaper routes in this order:

    code > agent > human

- **Code.** If a public source can answer it, fetch it. If a value can be built from
  the bibliography, build it. Anything the author would type, type it for them into the
  item.
- **Agent.** Soft text only — sidecar claims, scope, glosses, repo labels. Lands as a
  draft nothing reads until promoted.
- **Human.** What is left is exactly two kinds of act: something behind an account with
  no write API (an arXiv form, an ORCID edit, an S2 author page), and approving what
  would go out under the author's name. Nothing else belongs on the page.

An item that says "check X" or "look at Y" has skipped a step. Say what is wrong, where,
and what the corrected value is.

## Run the code yourself

Every `python` command in this repo that is read-only or writes only into `build/`,
`tasks/`, or a draft directory is yours to run, not the author's — and running it is
how you find out whether the item you are about to write is even still open. The only
commands reserved for the author: `--accept` on a sidecar draft, `sweep_github.py
apply`, `build_site.py --deploy`, and `wikidata_apply.py --apply`. Ask before those.

## Where things live

- `WORKLIST.md`, `tasks/*`, `build/*` are **generated**. Never hand-edit one; fix the
  emitter in `update.py` or the script under `scripts/` and re-run.
- Decisions the author makes go in `data/overrides.yaml`, `data/declines.yaml`, or a
  `reviewed:` flag — never into a generated file, which the next run overwrites.
- `docs/SETUP.md` is the general how-to, read once. It never carries this author's
  particular open items; those are only ever in `WORKLIST.md`.
- Nothing writes to `borgr/publications`, including its metadata. Paste-it-yourself
  only, with the entry given inline.

## Secrets

`config.yaml` is committed and public. Credentials live in env vars or a gitignored
file (`WIKIDATA_BOT_USER` / `WIKIDATA_BOT_PASSWORD`, or `.wikidata_bot`). Never echo a
key's value — its length or `grep -l` is enough. `site.indexnow_key` is public by design.

## Gates before a commit

    python scripts/validate.py --strict
    python -m unittest discover -s tests

Both are what CI runs, offline, no secrets. No attribution footers in commits or PRs.
