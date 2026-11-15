# SAU-BENCH-ENH-20261115-spike1-sample-size: Spike 1 had 6 labeled pages, too few to decide trigger 1

**Date Discovered:** 2026-11-15
**Severity:** MEDIUM
**Status:** RESOLVED
**Label:** [decision]
**Found by:** Claude Code, measured on 2026-11-15 by running spike 1's span collection on the
fixtures without any extractor
**Filed by:** Claude Code

## Problem
Trigger 1 in `PROJECT.md` names 50 pages. The spike plan expected 20. On 2026-11-15 there were
16 stored pages, and only 6 carried a labeled span. The 6 are 5 distinct articles (see
SAU-BENCH-BUG-20261115-same-article-stored-twice), and 3 of them use the same NHS template.

With 6 pages the agreement rate can only be 0, 17, 33, 50, 67, 83 or 100%. One page decides
whether the 70% falsifier fires.

## Why it matters
A language choice for the engine would rest on one page.

## Options
1. Run now, report it as provisional, and trigger 1 stays not decided whatever the number.
2. Run now and let the 70% rule decide as written.
3. Do not run until more pages are labeled.

## Resolution
Owner chose option 1 on 2026-11-15 (Q42). The run gave 67% for `dom_smoothie` and trigger 1 is
not decided.

Still open: re-run spike 1 once at least 20 pages carry a labeled span, after the owner's blind
second pass, with the deciding candidate named before the run.

## Related
`docs/extraction-spike.md` "Result", SAU-CORE-ENH-20261115-spike1-decider,
SAU-CORE-ENH-20261115-evidence-outside-main-content.
