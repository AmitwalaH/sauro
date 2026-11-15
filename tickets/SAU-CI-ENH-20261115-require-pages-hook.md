# SAU-CI-ENH-20261115-require-pages-hook: A fixture with a wrong span can be committed if the labeler forgets one command

**Date Discovered:** 2026-11-15
**Severity:** MEDIUM
**Status:** OPEN
**Label:** [ticket]
**Found by:** Claude Code, read in code and measured on a copy of the fixtures without pages
**Filed by:** Claude Code

## Problem
Since Q25, stored pages are not in git. On a copy of fixtures 0001 to 0004 without pages,
measured 2026-11-15, `check_fixtures.py` prints `0 hashes, 16 pages absent, 32 spans
unchecked: 0 failures` and passes. So CI checks no span against its page and no page against
its sha256. The only full check is `check_fixtures.py --require-pages` on the labeler's
machine, and only if the labeler remembers to run it.

## Why it matters
A span typed wrong, or a page edited by a tool, now reaches main with CI green. The benchmark
then scores the engine against evidence that is not on the page.

## Options
1. A git pre-commit hook that runs `check_fixtures.py --require-pages` whenever a commit
   stages a file under `bench/fixtures/`. It belongs with the git-gate hook port the owner
   approved as its own task (foundation Q4). Recommended.
2. A CI check that each changed fixture carries a stamp written by a local `--require-pages`
   run. More moving parts, and a stamp can be copied.
3. A private page store CI can read. See SAU-BENCH-ENH-20261115-private-page-store.

A hook can be skipped with `--no-verify`, so it reduces forgetting, not intent.

## Related
SAU-BENCH-ENH-20261115-pages-local, task `foundation` Q4, SAU-CI-BUG-20261101-ci-fixture-check.
