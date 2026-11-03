# SAU-BENCH-BUG-20261103-page-encoding: A correct span can fail the check on a page that is not UTF-8

**Date Discovered:** 2026-11-03
**Severity:** LOW
**Status:** OPEN
**Label:** [ticket]
**Found by:** Claude Code, read in code. Not seen on a real page yet.
**Filed by:** Claude Code

## Problem
`fetch_sources.py` stores each page's raw bytes. `check_fixtures.py` reads every stored page
as UTF-8 with `errors="replace"` (`check_fixtures.py`, in `check_fixture`), and so does
`fetch_sources.py` when it tests for empty text. A page served as `windows-1252` or
`iso-8859-1` loses its accented letters and curly quotes. A labeler copies "café" from the
browser, the stored page reads "caf�", and a correct span fails.

`docs/extraction-spike.md` lists this under "Limits". Nothing records the page's encoding, so
it cannot be fixed later without fetching again.

## Why it matters
The labeler sees a failure on a span that is on the page, and is tempted to edit the span to
please the script. That is the failure the verbatim rule was written to prevent.

## Options
1. `fetch_sources.py` records the `Content-Type` charset in each `sources` entry, and
   `check_fixtures.py` decodes with it when present. Recommended. Two files, one rule.
2. Leave it, and treat each failure by hand when it shows up.

## Related
SAU-BENCH-ENH-20261101-verbatim-definition, `docs/extraction-spike.md`.
