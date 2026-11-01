# Spike 1: Rust extraction vs trafilatura

**Status:** harness built and smoke-tested on 2026-11-01. **Not run on real pages.**
The result and the recommendation below are blank until the owner has stored the 20 fixture
pages in `bench/fixtures/`. They must not be filled in from anything except a run of `run.py`
on those pages.

## Where the code lives

Outside the repo, at `~/code/scratch/sauro-extraction/` on the owner's machine. It is
throwaway, imported by nothing, and is deleted when the spike is done. Only this report is
kept. The folder holds:

- `Cargo.toml` and `src/main.rs`: a binary `extract` that prints the main text one Rust
  extractor finds in one page. Its own empty workspace, so cargo never treats it as part of
  sauro.
- `run.py`: the driver. It runs trafilatura, calls `extract` for each Rust candidate, and
  prints the table and the summary. It imports `page_text`, `squash` and `source_files` from
  `bench/tools/check_fixtures.py`, so "the span is in this text" and "this URL is that file"
  mean the same thing in the spike as in the benchmark.
- `requirements.txt`: `trafilatura==2.3.1`.

## Question

Does a Rust main-content extractor keep the labeled evidence as well as Python `trafilatura`
does? This decides revisit trigger 1 in `PROJECT.md`: if Rust agrees on fewer than 70% of
pages, the engine moves to Python.

## Candidates

| Extractor | Version | Notes |
|---|---|---|
| `trafilatura` (Python) | 2.3.1 | The reference. Comments turned off, because `LABELING.md` says a span in a user comment is not in the source. Everything else default. |
| `dom_smoothie` (Rust) | 0.19.0 | A port of Mozilla Readability.js. Default config. |
| `readability` (Rust) | 0.3.0 | A port of the older arc90 readability. Default features off, so no HTTP client. |

## What is measured

For each stored page listed in a fixture's `sources`:

1. **Spans on the page.** The `evidence_span` of every supported, partial or contradicted
   claim whose `cited_urls` resolve to this page through `sources`, and that appears in the
   page. "Appears" is the verbatim rule in `bench/LABELING.md`: rendered text, all whitespace
   ignored.
2. **Spans kept.** For each extractor, how many of those spans appear in its output, by the
   same rule.
3. **Word F1 against trafilatura.** Bag-of-words overlap. A description only. No threshold is
   applied to it.

**What "agrees" means**, decided by the owner on 2026-11-01: on a page with at least one
labeled span, the Rust extractor agrees if it keeps every labeled span that trafilatura keeps.
Keeping more than trafilatura still counts as agreement. Pages with no labeled span are listed
but not counted.

## Prediction, written before any real run

A guess, not a measurement: `dom_smoothie` agrees on at least 70% of labeled pages, and
`readability` 0.3.0 agrees on fewer pages than `dom_smoothie`, because it ports an older
algorithm.

## Falsifier

`dom_smoothie` agrees on fewer than 70% of labeled pages. Then trigger 1 fires for the best
Rust candidate we have, and the language choice goes back to the owner.

## How to run

First check the labels. A span that is not in its page is a labeling error, not an extraction
result:

```bash
cd ~/code/sauro
python3 bench/tools/check_fixtures.py
```

Build the Rust side:

```bash
cd ~/code/scratch/sauro-extraction
cargo build --release
```

Install trafilatura one of two ways.

With a virtual environment (on Ubuntu this needs the `python3-venv` package):

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python run.py
```

Without one, into a plain folder:

```bash
python3 -m pip install --target ./pylib -r requirements.txt
PYTHONPATH=./pylib python3 run.py
```

`run.py` reads the sauro repo from `$SAURO_REPO`, default `~/code/sauro`, and its
`bench/fixtures/`. Give another fixtures folder as the first argument to override that. Paste
the table and the summary under "Result".

## Smoke test, 2026-11-01

A synthetic fixture with two stored pages that both contain the same article, a comment, a
nav and a footer. Only page `a` is cited, with one span in the article and one in the comment.
All three extractors ran, kept the article span and dropped the comment. Page `b` got 0 spans,
because no claim cites it. An earlier run with a stub that made the Rust extractors return
nothing or fail showed agreement falling to 0 of 1, with the failure counted. This shows the
harness works. **It says nothing about the question**, because the page was written to be easy.

## Limits

- 20 fixtures, not the 50 pages trigger 1 names. With about 20 labeled pages, one page moves
  agreement by about 5 points. A result between 60% and 80% should be read as "not decided".
- trafilatura is a reference, not ground truth. Where it drops a span and Rust keeps it, Rust
  is counted as agreeing.
- Pages are read as UTF-8. A page stored in another encoding may lose characters and fail a
  span for that reason alone. `check_fixtures.py` would show this first.
- Both Rust extractors get a placeholder base URL. They only use it to resolve links.

## Result

Blank until the owner has stored the 20 pages and run `run.py`.

## Recommendation

None until the result exists.
