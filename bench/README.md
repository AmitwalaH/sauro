# Benchmark fixtures

How a saved AI answer becomes a labeled fixture. The labels follow `LABELING.md`, which is the
contract. This file only covers the tooling.

## Workflow

1. Make `bench/fixtures/0001.sources/` and save the answer in it as `answer.md` (format below).
2. Run `python3 bench/tools/fetch_sources.py bench/fixtures/0001.sources`.
3. It fetches every URL once, stores each page in `0001.sources/`, and writes `0001.json`.
4. Read what it prints. Every failed fetch is listed, and is also in `fetch_failures`.
5. Commit `0001.json` as written, before any edit, so `git diff` later shows what you changed.
6. Open `0001.json`. Merge, split and drop claims, and fix `cited_urls`, under `LABELING.md`.
7. Label every claim under `LABELING.md`. The script writes `label: null` and nothing else.
8. Run `python3 bench/tools/check_fixtures.py`. It fails on any span not in its cited page.
9. It reports unlabeled claims as a count, not a failure, so a half-done set passes CI.
10. A null label in a fixture marked `"reviewed": true` fails.

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
  `+2` line, is a chip. Chip lines are not claims. Every URL under `sources shown:` attaches to
  the sentence right before each chip. With no chip, they attach to the last claim. With more
  than one chip, every chip gets every URL and the script prints a warning, because nothing
  says which URL belongs to which chip. Prune `cited_urls` by hand.
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
fetches a stored page again, because your labels were made against it. It never touches
`claims` once `0001.json` exists, and it refuses to write a fixture marked reviewed.

## The second labeling pass

When you re-label a fixture without looking at the first pass, a claim boundary you would draw
differently is not a label disagreement. Record it on the claim as `"hard": true` with a note,
and list boundary disagreements separately from label agreement.

**Revisit trigger for the skeletons:** if, on the first 20 fixtures, the diff from step 5
shows the boundaries or `cited_urls` changed on more than one skeleton in three, the
skeletons cost more than they save. Then the split moves back to the labeler.
