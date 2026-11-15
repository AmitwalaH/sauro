# SAU-BENCH-BUG-20261115-new-page-takes-recorded-name: On a clone, a new URL's page can be saved over the file name of an existing source

**Date Discovered:** 2026-11-15
**Severity:** HIGH
**Status:** OPEN
**Label:** [ticket]
**Found by:** Claude Code, measured by running `fetch_sources.run` with a mocked fetch on 2026-11-15
**Filed by:** Claude Code

## Problem
Steps, on a clone of a fixture that is not reviewed:
1. `0001.json` lists URL A as `1.html`. The page is absent, as on every clone since Q25.
2. The refetch of A fails, for example the site now returns 404. `1.html` stays absent.
3. The labeler adds URL B to `answer.md` and runs `fetch_sources.py` again.
4. B's page is stored as `1.html`, and `sources` now maps both A and B to `1.html`.

Measured output: `https://a.example/x -> 1.html`, `https://b.example/y -> 1.html`, and
`1.html` holds B's page.

Cause: `next_free_number` in `bench/tools/fetch_sources.py` picks the next number from the
files on disk. It assumes every recorded file is on disk, which stopped being true with Q25.
The bug is older than task `pages-local`. Before that task a clone refetched nothing, so the
clash was certain on any new URL. The refetch from that task makes it rarer, not impossible.

## Why it matters
A's claims would then be checked against B's page. With a sha256 recorded, `check_fixtures.py`
fails on A's hash on the labeler's machine, so it is caught there. On CI the page is absent
and nothing fails.

## Fix
`next_free_number` also counts the file names recorded in `sources` and `fetch_failures`.
One function, plus a test that runs the steps above.

## Related
SAU-BENCH-ENH-20261115-pages-local, `test_new_url_on_rerun_never_takes_a_stored_page_file`
(covers the case where the page is present).
