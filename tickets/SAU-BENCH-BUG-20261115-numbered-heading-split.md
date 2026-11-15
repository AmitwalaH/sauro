# SAU-BENCH-BUG-20261115-numbered-heading-split: A numbered heading such as "1. The world..." is not seen as a heading, so a chip reaches too far back

**Date Discovered:** 2026-11-15
**Severity:** LOW
**Status:** OPEN
**Label:** [ticket]
**Found by:** Claude Code, read in the 0005 skeletons and measured by calling
`fetch_sources.SENTENCE_BREAK` and `is_heading` on the line
**Filed by:** Claude Code

## Problem
The 0005 answer (ChatGPT) has numbered section headings: "1. The world is likely to reach
1.5°C in the 2030s", "2. What happens if we cross 1.5°C?", "3. ...", "4. ...". The splitter
in `bench/tools/fetch_sources.py` breaks after `. ` when a capital follows (line 59), so each
heading became two skeletons: `0005-09` "1." and `0005-10` "The world is likely ...", and the
same for -15/-16, -31/-32 and -40/-41.

`is_heading` (line 78) accepts a line only if it holds one sentence. Measured: the split gives
`['1.', 'The world is likely to reach 1.5°C in the 2030s']` and `is_heading` returns False. So
the script did not stop the first `ipcc.ch` chip at that heading. The chip reached back to the
heading above it, and `0005-06`, `-07` and `-08` got the IPCC URL although their section has no
chip. The URLs were removed by hand in the prepared fixture.

## Why it matters
Each wrong scope is a hand fix and counts toward the skeleton revisit trigger. A labeler who
misses it would label three uncited claims against a page they were never cited to.

## Options
1. Do not break after a leading list number (`^\d+\.` at the start of a line). One rule in the
   splitter, one test that "1. The world ..." stays one line and is a heading. Recommended.
2. Leave it and fix by hand. ChatGPT numbers its sections often, so it will recur.

## Related
`bench/README.md` "How the skeletons are made", SAU-BENCH-ENH-20261103-abbreviation-split,
SAU-BENCH-ENH-20261115-skeleton-rule5-reach.
