# SAU-BENCH-ENH-20261103-abbreviation-split: A sentence with "U.S." becomes two claims

**Date Discovered:** 2026-11-03
**Severity:** LOW
**Status:** OPEN
**Label:** [ticket]
**Found by:** Claude Code, read in the 0002 skeletons and measured with a grep over every saved
`answer.md` on 2026-11-03
**Filed by:** Claude Code, a second session preparing fixtures 0002 to 0004 on the owner's
instruction (fixture prep), committed in task `chip-scope`

## Problem
The 0002 answer says "The figure comes from the U.S. FDA and from the European Food Safety
Authority, which found ...". `fetch_sources.py` breaks after `. ` when a capital follows, so the
skeletons were two claims: `0002-03` "The figure comes from the U.S." and `0002-04` "FDA and
from the European Food Safety Authority, ...". Neither half can be labeled alone. The labeler
merged them by hand into `0002-03`.

`bench/README.md` documents this as a known limit of the crude split ("So "Dr. Smith" splits
wrongly"). So it is the rule working as written, not a bug.

Measured on 2026-11-03: a grep for an initialism (`U.S.`) or a common abbreviation (`Dr.`,
`Mr.`, `St.`, `vs.`, `etc.`, `e.g.`, `i.e.`, `No.`, `Fig.`, and others) followed by a space and
a capital found 1 hit in the 8 saved answers (0001 to 0008), the one above. The grep only
knows the abbreviations listed, so it can miss others.

## Why it matters
Each wrong split costs one hand merge. It also counts toward the skeleton revisit trigger in
`bench/README.md` (boundaries changed on more than one skeleton in three). One hit in eight
answers does not justify a change yet.

## Options
1. Leave it. The labeler merges by hand and the revisit trigger decides. Recommended for now.
2. Do not split after a token of single capitals joined by full stops (`U.S.`, `U.K.`, `E.U.`).
   One rule in the splitter, one test. Risk: a sentence that really ends in "U.S." stays joined
   to the next one.
3. Add a short list of abbreviations that never end a sentence. More cases, but the list then
   has to be kept up to date.

Revisit when: a second answer in the first 20 fixtures needs this merge.

## Related
`bench/README.md` "How the skeletons are made", SAU-BENCH-ENH-20261103-claude-chip-format.
`fetch_sources.py` has uncommitted changes from other work on this branch at the time of filing.
