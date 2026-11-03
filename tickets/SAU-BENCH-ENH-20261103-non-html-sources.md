# SAU-BENCH-ENH-20261103-non-html-sources: A cited PDF is stored as a source, but no label rule covers it

**Date Discovered:** 2026-11-03
**Severity:** LOW
**Status:** OPEN
**Label:** [decision]
**Found by:** Claude Code, read in code and `SCOPE.md`. Measured with a test page, not a real one.
**Filed by:** Claude Code

## Problem
When an AI cites a PDF, `fetch_sources.py` stores it as `<n>.pdf` and lists it in `sources`,
because it was a good 200 response. `check_fixtures.py` reads it as text, so no span copied
from it can match. `SCOPE.md` puts PDF sources out of v1, and `LABELING.md` has no reason
code for "the page is a PDF". The labeler has to pick between `other` and a wrong code.

## Why it matters
Different labelers will pick different codes for the same case, and that shows up as label
disagreement that is really a gap in the guide.

## Options
1. `fetch_sources.py` records a non-HTML response as a failure with reason `not_html`, kept
   out of `sources`. The guide says to label it `unverifiable`, `other`, with a note.
   Recommended, because it keeps `sources` to pages a span can be checked against.
2. Keep storing it in `sources`. The guide adds the rule for `other`.
3. Add a reason code `not_html` to the guide. That is a change to the frozen guide.

## Related
`SCOPE.md` non-goals, `bench/README.md` "Failed fetches".
