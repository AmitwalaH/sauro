# SAU-BENCH-ENH-20261101-verbatim-definition: The labeling guide does not say what "verbatim" means

**Date Discovered:** 2026-11-01
**Severity:** MEDIUM
**Status:** RESOLVED
**Label:** [decision]
**Found by:** Claude Code, read in `bench/LABELING.md` while writing `check_fixtures.py`
**Filed by:** Claude Code

## Problem
`LABELING.md` requires every evidence span to appear "verbatim" in the stored page, and a
script checks it. A labeler copies the span from the page as the browser shows it. The stored
file is HTML. A span that crosses `<em>` or a link, contains `&amp;`, or crosses a line break
in the HTML is not in the raw file byte for byte. The guide did not say which of these counts.

## Why it matters
Too strict, and correct labels fail the check, so labelers start editing spans to please the
script. Too loose, and a span that is not really on the page passes. Either way the benchmark
measures something other than what it says.

## Options (for decisions)
1. Match the raw HTML. Rejects most correct spans that cross a tag or an entity.
2. Match the rendered text exactly. Rejects spans that cross a line break in the HTML.
3. Match the rendered text (tags removed, entities decoded, script and style dropped) with all
   whitespace ignored, every other character matching. Recommended.

## Resolution
Owner chose option 3 on 2026-11-01. The definition is in `LABELING.md` under "Quality rules".
`check_fixtures.py` implements it, and its tests fail on raw HTML matching, on whitespace
sensitive matching, and on counting text inside script or style.

## Related
SAU-BENCH-ENH-20261101-source-page-mapping.
