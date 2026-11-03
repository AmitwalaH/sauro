# SAU-CI-ENH-20261101-check-suite-three-places: `make check` does not run the same checks as CI

**Date Discovered:** 2026-11-01
**Severity:** LOW
**Status:** OPEN
**Label:** [ticket]
**Found by:** Claude Code, read in `PROJECT.md`, `Makefile` and `.github/workflows/ci.yml`, re-measured 2026-11-01 after the CI change
**Filed by:** Claude Code

## Problem
The check suite is written in three places: the "Commands" block in `PROJECT.md`, the `check`
target in the `Makefile`, and the steps in `ci.yml`. They have already drifted. On
2026-11-01, `PROJECT.md` and CI run `check_fixtures.py` and its tests, but `make check` runs
only fmt, clippy and test.

2026-11-03, task `fixture-tooling`: the gap widens. `PROJECT.md` and CI now also run
`python3 -m unittest bench/tools/test_fetch_sources.py`, so `make check` misses three Python
lines instead of two. The `Makefile` was not in that task's approved file list.

## Why it matters
Someone who runs `make check` sees green and pushes, then CI goes red on a check they did not
know existed. Each new check has to be added three times, and the next one will be missed
somewhere.

## Options
1. Make `make check` the one list, and have CI call `make check`. `PROJECT.md` then says "run
   `make check`". Recommended.
2. Keep three lists and add a review step to compare them. Cheap now, drifts again later.

## Related
SAU-CI-BUG-20261101-ci-fixture-check.
