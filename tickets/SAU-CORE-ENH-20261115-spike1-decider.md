# SAU-CORE-ENH-20261115-spike1-decider: With four Rust candidates, which one decides trigger 1

**Date Discovered:** 2026-11-15
**Severity:** MEDIUM
**Status:** RESOLVED
**Label:** [decision]
**Found by:** Claude Code, read in `docs/extraction-spike.md` and the task file
**Filed by:** Claude Code

## Problem
The spike 1 falsifier was written on 2026-11-01 and names one candidate: `dom_smoothie`. The
task file of 2026-11-15 added `rs-trafilatura` and `readex`. The question was whether the best
of several Rust candidates should decide trigger 1.

## Why it matters
Choosing the best of three after seeing the results, on 6 labeled pages, is selection after
the fact. It would make the pre-registration worth nothing.

## Options
1. As pre-registered: `dom_smoothie` decides. The others are descriptive only.
2. The best Rust candidate decides.
3. The owner names one secondary candidate before the run.

## Resolution
Owner chose option 1 on 2026-11-15 (Q41). In the run `dom_smoothie` agreed on 4 of 6 pages and
the falsifier fired. `rs-trafilatura` and `readex` agreed on 6 of 6, and that stays
descriptive. A Rust Trafilatura port deciding trigger 1 needs a new pre-registered question on
fresh pages.

## Related
`docs/extraction-spike.md` "Result", SAU-BENCH-ENH-20261115-spike1-sample-size.
