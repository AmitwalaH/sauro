# SAU-BENCH-ENH-20261115-chip-source-not-recovered: 21 claims were cited by a source we never got, and the guide has no label for that

**Date Discovered:** 2026-11-15
**Severity:** MEDIUM
**Status:** OPEN
**Label:** [ticket]
**Found by:** Claude Code, read in the 0005 and 0006 answers and their `sources shown:` lists
while preparing those fixtures
**Filed by:** Claude Code

## Problem
A chat chip can name more sources than the panel lets you copy. Then a claim is cited, but
`cited_urls` does not hold every page it was cited to. In fixtures 0005 and 0006 this is 21
claims, all left at label null with the note "chip source not recovered" (owner decision Q51):

- 0005, three `ipcc.ch +1` chips: 0005-11 to -14, -17, -21, -24, -27, -30, -33, -35 to -39
  (15 claims). The one recovered URL, the IPCC summary, returned 403. The `+1` source is
  unknown each time.
- 0005, the `Consilium Data` chip: 0005-42 to -44 (3 claims). No URL was recovered at all.
- 0006, the `SureCloud +2` chip: 0006-09 to -11 (3 claims). SureCloud was recovered; the two
  other sources were not.

Neither mechanical label fits. `blocked` would ignore a cited page we never had, and
`no_citation` would say there was no citation when the user saw one.

## Why it matters
These claims are 21 of 62 null claims in 0005 to 0008. Left at null, they never enter the
benchmark. Labeled against the recovered page only, a claim the missing source supports
would read as `unverifiable`, and the engine would be scored against an incomplete citation.

## Options
1. Try to recover the URLs first: reopen the chats and read each chip's hover or panel. If
   the chats are gone, go to 2.
2. Add a reason code, such as `source_not_recovered`, used with `unverifiable`. It needs a
   `[decision]`, because `bench/LABELING.md` is the contract.
3. Label against the recovered pages only, and mark the claim `hard` with a note. No guide
   change, but the label then depends on which sources the panel happened to show.

Recommendation: 1, then 2 for whatever is still missing.

## Related
`bench/LABELING.md` reason codes, SAU-BENCH-ENH-20261115-rule5-source-list-and-chip-reach,
task `2026-11-15-fixtures-0005-0008` (Q51).
