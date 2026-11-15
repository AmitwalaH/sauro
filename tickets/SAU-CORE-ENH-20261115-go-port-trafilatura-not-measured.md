# SAU-CORE-ENH-20261115-go-port-trafilatura-not-measured: The Rust crate `trafilatura` was not measured in spike 1

**Date Discovered:** 2026-11-15
**Severity:** LOW
**Status:** OPEN
**Label:** [ticket]
**Found by:** Claude Code, web search on 2026-11-15 during spike 1 Step 3
**Filed by:** Claude Code

## Problem
crates.io has a Rust crate named `trafilatura`, a port of go-trafilatura. It is a different
project from `rs-trafilatura`. Its own table reports a balanced F-score close to Python
trafilatura's. That is self-reported and was not checked here.

Spike 1 did not measure it, by owner decision Q40: four candidates were enough, and each extra
candidate is another forking path on 6 labeled pages.

## Why it matters
If a Rust extractor is chosen later, this is a candidate nobody has looked at. It is not a
reason to re-run spike 1 now.

## Options
1. Add it as a candidate when spike 1 is re-run on 20 or more labeled pages, named before the
   run.
2. Drop it.

Recommendation: option 1, if the re-run still compares extractors at all. See
SAU-CORE-ENH-20261115-evidence-outside-main-content first.

## Related
`docs/extraction-spike.md`, SAU-BENCH-ENH-20261115-spike1-sample-size.
