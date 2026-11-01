# SAU-CI-BUG-20261101-ci-fixture-check: A pull request with a wrong evidence span is not failed, though CONTRIBUTING.md says it is

**Date Discovered:** 2026-11-01
**Severity:** MEDIUM
**Status:** RESOLVED
**Label:** [ticket]
**Found by:** Claude Code, read in `CONTRIBUTING.md`, `PROJECT.md` and `.github/workflows/ci.yml`
**Filed by:** Claude Code

## Problem
`CONTRIBUTING.md` says every evidence span must appear verbatim in the stored page, and "A
script checks this and the pull request fails if it does not." CI did not run any such script,
and the check suite in `PROJECT.md` did not list it. CI also ran only on pushes to `main` and
on pull requests, so a push to a task branch ran nothing.

## Why it matters
A contributor reads that the check exists and trusts it. A fixture with a span that is not on
its page could be merged, and the engine would be scored against it.

## Resolution
Owner approved on 2026-11-01. CI now runs on every push to any branch and on pull requests. A
`bench checks` job runs `python3 bench/tools/check_fixtures.py` and its tests,
`python3 -m unittest bench/tools/test_check_fixtures.py`. Both lines are in the check suite in
`PROJECT.md`.

## Related
SAU-CI-ENH-20261101-check-suite-three-places.
