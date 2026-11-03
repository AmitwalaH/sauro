# SAU-BENCH-ENH-20261103-unlabeled-claims-in-baseline: The benchmark could score the engine against claims nobody has labeled yet

**Date Discovered:** 2026-11-03
**Severity:** MEDIUM
**Status:** OPEN
**Label:** [ticket]
**Found by:** Claude Code, read in code while changing `bench/tools/check_fixtures.py`
**Filed by:** Claude Code

## Problem
Since task `fixture-tooling`, `check_fixtures.py` lets a claim have `label: null` and still
pass CI, so half-labeled fixtures can be merged. The benchmark gate in task 3
(`sauro-bench --check-baseline`) does not exist yet. If it reads every claim, an unlabeled
claim is either counted as a miss or crashes the run, and the precision and recall in
`bench/baseline.json` describe labels nobody gave.

## Why it matters
The baseline is a judge. A number computed partly over unlabeled claims would be published in
the README as the engine's accuracy, and it would move every time someone labels a claim.

## Options
1. `sauro-bench` skips unlabeled claims and prints how many it skipped. Recommended.
2. `sauro-bench` refuses to record a baseline while any claim is unlabeled.

## Related
Task 3 (engine and bench). `bench/tools/check_fixtures.py`, `bench/README.md`.
