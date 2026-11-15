# Spike 1: Rust extraction vs trafilatura

**Status:** run on 16 real pages on 2026-11-15. **Provisional.** The pre-registered sections
below are kept as written on 2026-11-01. What changed since then is listed at the top of
"Result". The result comes only from a run of `run.py` on the stored pages.

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

Run by Claude Code on 2026-11-15 at 09:38 UTC, on fixtures 0001 to 0004 at commit `6640ae9`.
`check_fixtures.py --require-pages` passed first: 32 spans, 16 hashes, 0 failures. The owner
re-ran on 2026-11-15 and diff against Claude Code's output printed IDENTICAL (Q44).

The scratch folder `~/code/scratch/sauro-extraction/` is kept, not deleted as "Where the code
lives" says, for the re-run at 20 labeled pages (Q48). Its `fixtures-0001-0004/` folder links
to only the fixtures measured here, so this result can be reproduced after more fixtures land.

**Provisional.** Trigger 1 stays not decided whatever the number (owner decision Q42).

### Changed since pre-registration

- 16 stored pages, not 20. Only 6 carry a labeled span, so one page moves agreement by about
  17 points. The 6 are 5 distinct articles: `0001/6.html` and `0004/2.html` are the same NHS
  page fetched under two URLs. Their rendered text is identical, and so is every extractor's
  output on them.
- 32 claims with a span give 31 span-page pairs, because `0003-09` and `0003-10` share one
  span and `run.py` counts a span once per page.
- Candidates added by the task file: `rs-trafilatura` and `readex`. All four Rust candidates
  are measured (Q40). Only `dom_smoothie` decides the falsifier. The other three are
  descriptive (Q41).
- Columns added to `run.py`: lost spans per extractor, share of page text kept, versions read
  from `Cargo.lock` and the installed package, and a deduplicated agreement line. Nothing the
  pre-registered harness printed changed. The original `run.py` was run on the same pages and
  its 16 table rows and 6 summary lines match the new output exactly.
- A smoke test (`smoke_test.py`, 7 tests) checks the added columns on a synthetic fixture,
  with a stub giving each Rust extractor a different known output.
- trafilatura was installed with `pip install --target ./pylib`. This machine has no
  `python3-venv`.
- `readex` 0.19.2 runs its Trafilatura port by default, not its Readability port. So two Rust
  candidates are Trafilatura ports and two are Readability ports.

### Per extractor

Spans kept are measured against the labels directly: the span is in the extractor's output,
whitespace ignored. Agreement is the owner's rule from 2026-11-01. Share is extracted
characters over the page's rendered text characters, whitespace ignored, as a median.

| Extractor | Version | Kind | Spans kept of 31 | Agrees, of 6 pages | Agrees, deduplicated, of 5 | Share, all 16 pages | Share, 6 labeled pages | Failed |
|---|---|---|---|---|---|---|---|---|
| `trafilatura` (Python) | 2.3.1, lxml 6.1.3 | reference | 24 | reference | reference | 0.67 | 0.66 | 0 |
| `dom_smoothie` | 0.19.0 | Readability.js port | 22 | **4 (67%)** | 3 (60%) | 0.63 | 0.76 | 0 |
| `readability` | 0.3.0 | arc90 Readability port | 18 | 3 (50%) | 2 (40%) | 0.63 | 0.73 | 0 |
| `rs-trafilatura` | 0.2.2 | Trafilatura port | 26 | 6 (100%) | 5 (100%) | 0.66 | 0.78 | 0 |
| `readex` | 0.19.2 | Trafilatura port | 24 | 6 (100%) | 5 (100%) | 0.65 | 0.65 | 0 |

Build notes, all on rustc 1.99.1 with default options and comments off:
- All four Rust crates built with no warning. None failed on any page.
- `rs-trafilatura` embeds XGBoost models for page-type classification and a quality score.
  Inference is local and the output was identical across runs. It is not an LLM. About 16,000
  downloads, one author, accuracy claims self-reported.
- `readex` has 497 downloads and its releases date from May 2026.
- `readability` 0.3.0 has had no release since 2023-12-20.

No extractor keeps almost everything. The highest median share on labeled pages is 0.78, so
keeping more spans did not come from keeping the whole page.

The run was repeated and the output was byte-identical. Every miss was checked against the
extractor's output with letters and digits only, after NFKC. None was a span kept but
reformatted. The longest part of any lost span found in the output was at most 54% of it.

### Misses, per page

Pages not listed lost no span for any extractor. Each miss sat in a page module, not in body
prose. The element is named; no page text is quoted beyond the fixture spans.

| Page | Claim | Span | Lost by | Where the span sits |
|---|---|---|---|---|
| `0002/6.html` | 0002-08 | The pregnancy limit is 200 mg per day because caffeine crosses the placenta and a fetus lacks the enzymes to break it down. | `dom_smoothie`, `readability` | A key takeaways list box at the top of the article |
| `0002/6.html` | 0002-15 | A single large coffeehouse brew or cold brew can contain 250–330 mg | `dom_smoothie`, `readability` | Same box |
| `0002/6.html` | 0002-16 | average five-hour half-life means a 200 mg coffee at 3 p.m. still leaves roughly 50 mg circulating in your blood at 1 a.m. | `dom_smoothie`, `readability` | Same box |
| `0003/3.html` | 0003-01 | Often, symptoms of type 2 diabetes are subtle or absent | all five | A Questions and Answers block, an `<aside>` accordion inside the article body |
| `0003/3.html` | 0003-03 | they typically include increased thirst, increased urination | all five | Same `<aside>` |
| `0003/3.html` | 0003-08 | blurred vision | all five | Same `<aside>` |
| `0003/3.html` | 0003-09, 0003-10 | Other early signs could be slow-healing sores, numbness and tingling in your hands and feet, and recurrent genital infections. | all five | Same `<aside>` |
| `0003/3.html` | 0003-12 | If you have signs of insulin resistance, such as diseases of the heart and blood vessels | all five | Same `<aside>` |
| `0003/3.html` | 0003-05, 0003-06, 0003-07, 0003-11 | (four spans in the article body) | `readability` | Article body. `readability` kept 0 of 9 spans on this page and 0.11 of its text. |
| `0004/1.html` | 0004-04 | do not take more than 8 tablets or capsules in 24 hours | `trafilatura`, `readex` | A collapsed `<details>` expander |
| `0004/2.html` | 0004-05 | take them up to 3 times a day | `trafilatura`, `readex` | A collapsed `<details>` expander |
| `0004/3.html` | 0004-01 | In fact, they are often taken together because they work in different ways to provide better pain relief than either medicine alone. | `dom_smoothie`, `readability` | An introduction block above the main body |

`dom_smoothie` disagrees with trafilatura on `0002/6.html` and `0004/3.html`. On both, the
other Readability port loses the same spans and both Trafilatura ports keep them. On the NHS
pages trafilatura loses a span in a `<details>` expander and `dom_smoothie` keeps it, which
the agreement rule counts in `dom_smoothie`'s favour.

Five of 31 spans (16%) are lost by every extractor, Python included. All five are in one
`<aside>` on one page. A matcher that reads only extracted text could not show evidence for
those claims. See SAU-CORE-ENH-20261115-evidence-outside-main-content. The caveat below says
this count overstates the evidence lost.

### Caveat, 2026-11-15: the Questions and Answers block on `0003/3.html`

The owner checked `0003/3.html` in a browser on 2026-11-15. The five spans lost by every
extractor sit in a Questions and Answers block. It is visible inline in the article, with
answers from named doctors, so it is page content a reader sees. The first version of this
Result said the block was outside the article body. It is inside it, in an `<aside>` within
the article body; that was read off a shortened element path, and the misses table is
corrected.

But the article body also states equivalent evidence for several of the lost spans, for
example "your kidneys work harder to remove it", "This pulls fluids from your tissues, making
you dehydrated" and "Symptoms can come on slowly". The assistant-proposed spans were taken from
the Q and A block. Measured on 2026-11-15: each of these three phrases appears once in the
stored page, in the article body and not in the block, and every extractor keeps all three
except `readability` 0.3.0.

So the count of 5 of 31 spans lost by every extractor overstates the evidence lost. The true
figure needs the owner's blind pass. See SAU-BENCH-BUG-20261115-first-pass-labels-0003-known-wrong.

### Did the prediction hold?

- "`dom_smoothie` agrees on at least 70% of labeled pages": **no.** 4 of 6, 67%.
- "`readability` 0.3.0 agrees on fewer pages than `dom_smoothie`": **yes.** 3 of 6 against 4.
- **The falsifier fired as written.** `dom_smoothie` agrees on fewer than 70% of labeled
  pages. 67% is also inside the 60% to 80% band that "Limits" calls not decided, and one page
  either way moves it to 50% or 83%.

### Limits of this result

- 6 labeled pages, 5 distinct articles, 4 fixtures, all in the health domain. Three of the 6
  pages use the same NHS template.
- The labels are the first pass, proposed by an assistant and accepted by the owner, and not
  reviewed. See SAU-BENCH-ENH-20261115-assistant-proposed-first-pass.
- **The spans lean toward prose and main content (Q43).** The assistant read each page as
  text with tags, scripts and styles removed, the same rule as `page_text`. Its search printed
  only sentences under 330 characters, which filtered out long navigation runs. This bias
  favours every extractor, so the spans kept above are likely higher than on spans chosen
  without that filter.
- One page, `0003/3.html`, holds 5 of trafilatura's 7 misses. The ground-truth counts rest
  on it, and its first-pass labels are known to be wrong in places (see the caveat above).

## Recommendation

For the owner to decide. Trigger 1 stays not decided (Q42).

1. **Do not move the engine to Python on this result.** The falsifier fired for
   `dom_smoothie`. But both of its misses are behaviour it shares with the other Readability
   port, and both Rust Trafilatura ports agree on 6 of 6. `rs-trafilatura` kept more spans
   than Python trafilatura, 26 against 24. On these pages the gap is between algorithms, not
   languages. This is descriptive only, because `rs-trafilatura` and `readex` were not
   pre-registered to decide (Q41).
2. **Decide SAU-CORE-ENH-20261115-evidence-outside-main-content before trigger 1 is
   measured again.** If the engine matches against the full rendered text, extractor choice
   matters much less and trigger 1 measures the wrong thing.
3. **Re-run once at least 20 labeled pages exist**, after the owner's blind second pass, with
   a new pre-registered question that names the deciding candidate before the run. See
   SAU-BENCH-ENH-20261115-spike1-sample-size.

It depends on: the spans being representative of what users cite, which the prose bias and
the single domain both weaken.

Revisit trigger: a re-run on 20 or more labeled pages, the blind second pass changing any
span on these pages, or a Rust Trafilatura port losing a span that Python trafilatura keeps.
