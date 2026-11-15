# Benchmark fixtures

How a saved AI answer becomes a labeled fixture. The labels follow `LABELING.md`, which is the
contract. This file only covers the tooling.

## Workflow

1. Make `bench/fixtures/0001.sources/` and save the answer in it as `answer.md` (format below).
2. Run `python3 bench/tools/fetch_sources.py bench/fixtures/0001.sources`.
3. It fetches every URL once, stores each page in `0001.sources/`, and writes `0001.json`.
4. Read what it prints. Every failed fetch is listed, and is also in `fetch_failures`.
5. Commit `0001.json` as written, before any edit, so `git diff` later shows what you changed.
   Stage it by name with `0001.sources/answer.md`. The stored pages are never committed.
6. Open `0001.json`. Merge, split and drop claims, and fix `cited_urls`, under `LABELING.md`.
7. Label every claim under `LABELING.md`. The script writes `label: null` and nothing else.
8. Run `python3 bench/tools/check_fixtures.py --require-pages`. It fails on any span not in
   its cited page, and on any stored page that is missing. It must pass before every commit
   that adds or changes a fixture.
9. It reports unlabeled claims as a count, not a failure, so a half-done set passes CI.
10. A null label in a fixture marked `"reviewed": true` fails.

## Stored pages stay local

The pages in `0001.sources/` are copies of other people's websites. They are not committed to
this public repo (owner decision Q25, ticket `SAU-BENCH-ENH-20261115-pages-local`). The repo
holds `0001.json` and `answer.md`. The JSON records each page's URL, fetch date and sha256,
and every evidence span. `.gitignore` keeps everything else in `*.sources/` out of git.

So CI has no pages. On CI, `check_fixtures.py` still runs every check that needs no page:
known label, a span where the label needs one, cited URLs listed in `sources`, no null label
in a reviewed fixture. It cannot check a span against its page or a page against its sha256.
It counts what it skipped, as `N pages absent, N spans unchecked`, and passes. That is why
step 8 runs with `--require-pages` on the labeler's machine, where the pages are.

To get the pages on a fresh clone, run `fetch_sources.py` on the fixture directory, as in
step 2. It fetches each page listed in `sources` that is missing, stores it under its
recorded file name, and prints whether it matches the recorded sha256. It writes only the
page, never the JSON, so it works on a reviewed fixture too.

A refetched page usually does not match. Sites change their HTML all the time, often only in
scripts, ads or tracking. Measured on 2026-11-15: of 16 pages fetched on 2026-11-03, 15 no
longer matched byte for byte, yet all 32 evidence spans were still found in them. A mismatch
means the page is not the one that was labeled. `check_fixtures.py` then fails on its hash,
and that failure is correct. Do not relabel against a refetched page, and never change a
recorded sha256 to match. A span that is still found tells you that passage is still there,
not that the page is the same. Delete the refetched page to go back to "absent". Only the
labeler's own copy can pass `--require-pages`, so keep it backed up.

## answer.md

```
model: gpt | claude | gemini | perplexity
domain: health | news | school | code | finance
asked_on: 2026-11-03
question: <the exact question>
---
<the answer, pasted verbatim, including every URL the model showed>
sources shown:
<one URL per line, from the chat's source panel, if it has one>
```

`model` becomes `source_model`, `asked_on` becomes `collected_on`, and the fixture id is the
directory name. `question` has no field in the fixture; it stays in `answer.md`. An empty
answer, a missing header field or a missing `---` line writes nothing.

## How the skeletons are made

The rules are crude on purpose. You fix them by hand in step 6, so they only save typing.

- **Sentences.** A break after `. `, `? ` or `! ` when a capital follows, and at every line
  break. So "Dr. Smith" splits wrongly, a hard-wrapped paragraph comes out in pieces, and a
  heading becomes its own claim. Merge, split or drop them.
- **URLs.** `http://` or `https://` up to whitespace, `]`, a quote or `<>`. Trailing
  `. , : ; ! ?` is dropped, and a trailing `)` is dropped unless it closes a `(` inside the
  URL, so `.../Ibuprofen_(drug)` survives and `(https://x.org/a).` loses `).`.
- **Inline URLs** go into `cited_urls` of the sentence they appear in.
- **Citation chips.** A line that is a bare domain, such as `nhs.uk`, optionally followed by a
  `+2` line, is a chip. Chip lines are not claims. A chip covers every claim from the previous
  heading down to the chip, or from the start of the answer if there is no heading above it
  (owner decision Q15). Every URL under `sources shown:` attaches to every covered claim. The
  heading gets no URLs; its skeleton stays so the numbering is stable, and you drop it. With
  no chip, the URLs attach to the last claim. With more than one chip, each chip's claims get
  every URL and the script prints a warning, because nothing says which URL belongs to which
  chip. Prune `cited_urls` by hand. Each covered claim is still labeled on its own.
- **Headings.** A heading is a line holding one sentence that ends in `?` or has no terminal
  punctuation, such as `What are the risks?` or `## Risks`. Trailing `*`, `_`, quotes and
  closing brackets are looked past. A line ending in `:` is a lead-in, not a heading, and
  belongs to the section above it.
- Claim ids are `0001-01`, `0001-02`, and so on. Renumber them if you merge or split.

## Failed fetches

A failed URL is kept out of `sources`, so no span can be checked against it. Its entry in
`fetch_failures` records facts: `fetch_status` (HTTP status or null), `final_url`, `reason`,
`bytes`, and `file` when a body came back. Open that file before you pick a reason code.

| `reason` | What happened | Usual reason code in `LABELING.md` |
|---|---|---|
| `dns_failed`, `connection_failed`, `timeout` | No response | `fetch_failed` |
| `http_error` with 404, 410 or 5xx | The server said no page | `fetch_failed` |
| `http_error` with 401, 402, 403, 429 or 451 | The server refused | `blocked`, after reading the stored body |
| `empty_body` | A 200 with nothing in it | `fetch_failed` |
| `small_body` | A 200 under 500 bytes | `blocked` if it is a bot check, consent or login wall; `js_only` if it is an app shell |
| `empty_text` | HTML with no visible text | `js_only`, after reading the stored body |
| `too_large` | Over the size cap, not stored | `other`, with a note |

The table is a starting point. The guide decides. The fetch policy (timeout, retries, size cap)
is in `PROJECT.md`. The script sends an honest User-Agent and never tries to get past a block.

A non-HTML page, such as a PDF, is stored and listed in `sources`. `check_fixtures.py` reads it
as text, so a span copied from it will not match.

## Running it again

A rerun fetches only URLs with no stored page yet, which retries the ones that failed. It never
fetches a stored page again, because your labels were made against it. A page listed in
`sources` but missing from disk is fetched back under its recorded name, as above. It never
touches `claims` once `0001.json` exists. It leaves `0001.json` alone when nothing new was
fetched. On a fixture marked reviewed it only puts back missing pages and never writes the
JSON.

## The second labeling pass

When you re-label a fixture without looking at the first pass, a claim boundary you would draw
differently is not a label disagreement. Record it on the claim as `"hard": true` with a note,
and list boundary disagreements separately from label agreement.

**Revisit trigger for the skeletons:** if, on the first 20 fixtures, the diff from step 5
shows the boundaries or `cited_urls` changed on more than one skeleton in three, the
skeletons cost more than they save. Then the split moves back to the labeler.
