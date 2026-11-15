# SAU-BENCH-ENH-20261115-baseline-without-pages: The benchmark gate planned for task 3 cannot run on CI, because CI has no pages

**Date Discovered:** 2026-11-15
**Severity:** HIGH
**Status:** OPEN
**Label:** [decision]
**Found by:** Claude Code, read in `PROJECT.md` against owner decision Q25
**Filed by:** Claude Code

## Problem
`PROJECT.md` plans `cargo run -p sauro-bench -- --check-baseline` in the check suite from
task 3. The engine reads a claim's cited page and reports a verdict, and the baseline compares
those verdicts with the labels. Since Q25, CI has the fixture JSON but no pages. So on CI the
engine has nothing to read, and the frozen `bench/baseline.json` cannot be checked there.
Revisit triggers 1 and 2 in `PROJECT.md` also need the pages.

## Why it matters
The baseline is the judge for every engine change. If it only runs on one machine, an engine
regression can merge with CI green.

## Options
1. The baseline check runs only on the labeler's machine, before each engine change lands.
   No infrastructure. The judge depends on a person remembering, like the span check.
2. CI reads the pages from a private store. See SAU-BENCH-ENH-20261115-private-page-store.
   Deterministic and complete.
3. CI refetches the pages and scores only fixtures whose spans are all still found in the
   refetched pages. On 2026-11-15 all 32 spans were still found though 15 of 16 pages had
   changed bytes. Not deterministic: the numbers move when sites change, so it cannot gate a
   frozen baseline.

Recommendation, for the owner to decide before task 3 starts: option 2, because it is the
only one that keeps the baseline a deterministic judge on CI. Not decided here.

## Related
SAU-BENCH-ENH-20261115-pages-local, SAU-BENCH-ENH-20261115-private-page-store,
SAU-BENCH-ENH-20261115-assistant-proposed-first-pass (no baseline from the first-pass labels),
SAU-BENCH-ENH-20261103-unlabeled-claims-in-baseline.
