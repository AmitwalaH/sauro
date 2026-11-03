# SAU-BENCH-ENH-20261103-unchecked-model-and-domain: A typo in a fixture's model or domain passes every check

**Date Discovered:** 2026-11-03
**Severity:** LOW
**Status:** OPEN
**Label:** [ticket]
**Found by:** Claude Code, read in code while writing `bench/tools/fetch_sources.py`
**Filed by:** Claude Code

## Problem
`answer.md` says `model: Claude` or `domain: heath`. `fetch_sources.py` copies the value into
`source_model` and `domain` as written. `check_fixtures.py` never reads either field. So the
typo passes CI and stays.

## Why it matters
`LABELING.md` sets coverage targets by domain and by model ("at least 10 fixtures from each of
three different models"). A typo puts a fixture in a bucket of its own, and the coverage count
is wrong without anyone seeing it.

## Options
1. `check_fixtures.py` fails on a value outside the sets in `LABELING.md`. The sets live in
   one place in that script. Recommended.
2. Leave it to review.

## Related
`bench/LABELING.md` "What a fixture is" and "What the first 100 fixtures should cover".
