# SAU-BENCH-BUG-20261115-as-written-skeletons-lost: The skeleton revisit trigger cannot be measured on fixtures 0001 to 0004

**Date Discovered:** 2026-11-15
**Severity:** LOW
**Status:** OPEN
**Label:** [ticket]
**Found by:** owner, stated in task `pages-local`; confirmed by Claude Code with `git log --all` (no fixture JSON was ever committed)
**Filed by:** Claude Code

## Problem
`bench/README.md`, workflow step 5, says to commit each fixture JSON as `fetch_sources.py`
wrote it, before any edit, so `git diff` later shows what the labeler changed. For 0001 to
0004 that commit never happened. The as-written skeletons were kept in a scratch folder that
is now lost. The JSON committed in task `pages-local` is the edited, labeled version.

## Why it matters
The README's revisit trigger for the skeletons reads: "if, on the first 20 fixtures, the diff
from step 5 shows the boundaries or `cited_urls` changed on more than one skeleton in three,
the skeletons cost more than they save". With no as-written JSON, that diff does not exist
for 0001 to 0004. The trigger can only be measured on fixtures from 0005 on.

## Fix
From 0005 on, commit the as-written JSON first, as step 5 says. Count the trigger over the
first 20 fixtures that have an as-written commit, and say in the count that 0001 to 0004 are
left out and why. Close this ticket when that count is reported.

## Related
`bench/README.md` "Workflow" step 5 and "The second labeling pass",
SAU-BENCH-ENH-20261103-abbreviation-split, SAU-BENCH-ENH-20261103-claude-chip-format.
