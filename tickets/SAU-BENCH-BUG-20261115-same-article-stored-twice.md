# SAU-BENCH-BUG-20261115-same-article-stored-twice: One article is stored twice and counted as two pages

**Date Discovered:** 2026-11-15
**Severity:** LOW
**Status:** OPEN
**Label:** [ticket]
**Found by:** Claude Code, measured on 2026-11-15 while counting pages for spike 1
**Filed by:** Claude Code

## Problem
`0001.sources/6.html` and `0004.sources/2.html` are the same NHS page, "ibuprofen for adults".
The URLs differ only by a tracking parameter: `0001` cites it with `?rfsn=6242243.0924357`.
The bytes differ, so the sha256 values differ, but the rendered text is identical. All five
extractors in spike 1 gave identical output on the two files.

Anything that counts pages counts this article twice. In spike 1 the 6 labeled pages are 5
articles.

## Why it matters
Each fixture's claims are fine. The cost is in per-page measures: with few pages, a duplicate
moves a percentage by a whole page, and two near-copies look like two independent tests.

## Options
1. Report per-page measures also with duplicates merged, as spike 1's `run.py` now does. No
   tool change.
2. `check_fixtures.py` lists stored pages across fixtures with identical rendered text, as
   information, not a failure.
3. `fetch_sources.py` strips known tracking parameters before fetching. That changes which URL
   is recorded, which `cited_urls` must match, so it needs care.

Recommendation: option 2. It reads only, it catches copies however the URLs differ, and it
makes the count visible where the benchmark is built.

## Related
`docs/extraction-spike.md` "Result", SAU-BENCH-ENH-20261115-spike1-sample-size.
