# SAU-BENCH-ENH-20261115-skeleton-rule5-reach: The skeleton script still follows the old rule 5, so most cited_urls are fixed by hand

**Date Discovered:** 2026-11-15
**Severity:** MEDIUM
**Status:** OPEN
**Label:** [ticket]
**Found by:** Claude Code, measured by comparing the as-written skeletons of 0005 to 0008
(commit e100ec6) with the prepared fixtures (commit 67631df)
**Filed by:** Claude Code

## Problem
Rule 5 in `bench/LABELING.md` changed in commit c92250e: chip to chip reach, sub-titles and
captions do not stop a chip, and a source list without markers covers every body claim.
`bench/tools/fetch_sources.py` still attaches URLs by the older rule, and it does not know
Claude's dotless chips (SAU-BENCH-ENH-20261103-claude-chip-format) or numbered headings
(SAU-BENCH-BUG-20261115-numbered-heading-split). With no chip it gives every listed URL to
the last skeleton only.

Measured on 2026-11-15 over 0005 to 0008 (129 skeletons):

| | Count |
|---|---|
| Skeletons deleted as non-claims | 58 of 129 |
| Kept claims with a wrong boundary (`0007-07`, `-08`, `-09`) | 3 of 71 |
| Kept claims whose `cited_urls` changed by hand | 46 of 71 |

Per fixture, `cited_urls` changed on 7 of 29 kept claims (0005), 18 of 20 (0006), 14 of 14
(0007) and 7 of 8 (0008).

## Why it matters
`bench/README.md` sets a revisit trigger: if boundaries or `cited_urls` change on more than
one skeleton in three over the first 20 fixtures, the skeletons cost more than they save. On
these four, deletions alone are 45%. Most of the `cited_urls` changes come from rules the
script does not implement yet, not from the splitter, so the trigger mixes two causes.

## Options
1. Bring `fetch_sources.py` up to rule 5 as it now reads, test first: chip to chip, sub-titles
   and captions not stopping a chip, source list with no markers covering every claim,
   dotless chips, numbered headings. Then measure again on 0009 to 0020.
2. Let the trigger fire now and move the split back to the labeler, as the README says.

Recommendation: 1, then measure. The deletions, mostly headings and chip lines, cost little
by hand; the `cited_urls` changes are the expensive part and are the part a script can do.

## Related
`bench/README.md` "How the skeletons are made" and its revisit trigger,
SAU-BENCH-ENH-20261115-rule5-source-list-and-chip-reach,
SAU-BENCH-ENH-20261103-claude-chip-format, SAU-BENCH-BUG-20261115-numbered-heading-split,
SAU-BENCH-ENH-20261103-abbreviation-split.
