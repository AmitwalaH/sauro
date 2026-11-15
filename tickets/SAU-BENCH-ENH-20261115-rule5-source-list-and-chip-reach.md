# SAU-BENCH-ENH-20261115-rule5-source-list-and-chip-reach: Fixtures 0005 to 0008 follow three citation rules the labeling guide does not state

**Date Discovered:** 2026-11-15
**Severity:** MEDIUM
**Status:** RESOLVED
**Label:** [decision]
**Found by:** Claude Code, read in `bench/LABELING.md` rule 5 while preparing fixtures 0005 to 0008
**Filed by:** Claude Code

## Problem
`bench/LABELING.md` is the contract every fixture is labeled by. Rule 5 states owner decision
Q15 and the heading rule, nothing more. On 2026-11-15 the owner decided three more points, and
fixtures 0005 to 0008 were prepared under them. None of the three is in the guide yet:

1. **Source list without markers (Q50).** An end-of-answer source list with no inline markers
   covers every body claim. Without it, rule 4 makes every claim in such an answer
   `unverifiable`, `no_citation`. Effect measured on 2026-11-15: all 22 kept claims in 0007
   (Gemini) and 0008 (Perplexity) cite the listed URLs instead of carrying `no_citation`.
2. **Sub-titles do not stop a chip (Q52).** Read literally, the heading rule makes a short
   sub-title such as `Extreme heat` a heading, so a chip at the end of a numbered section
   would reach back only to the last sub-title. Effect: in 0005, claims 0005-17, -21, -24 and
   -27 are covered by the section's `ipcc.ch +1` chip instead of carrying `no_citation`.
   Image captions were treated the same way.
3. **Nearest boundary (owner, 2026-11-15, unnumbered).** With several chips in one section,
   each chip covers back to the previous chip or the heading, whichever is nearer. Rule 5 as
   written lets every chip reach back to the heading. Effect: in 0006, 13 claims lost URLs
   from later chips (0006-09 to -11, -18 to -20, -22, -24, -29 to -31). Consecutive chip lines
   with no claim between them still count as one chip, as `bench/README.md` says.

Measured by running the prep script and a hand-written second reader against the as-written
skeletons; both agree on every kept claim.

## Why it matters
A second labeler who reads only the guide would attach URLs differently on 39 claims in these
four fixtures. Their labels would then disagree for a reason that is not about the evidence,
and the two-labeler agreement count in the guide's quality rules would be wrong.

## Options
1. Add the three points to rule 5 in their own commit, as was done for Q15 (task
   `chip-scope`, Q16).
2. Record them in `bench/README.md` only. Cheaper, but the README covers tooling, not the
   contract, so a labeler can miss them.

Recommendation: 1.

## Resolution
Owner chose 1 on 2026-11-15 (task `2026-11-15-fixtures-0005-0008`). Rule 5 now states all
three points, in commit c92250e. For Q50 it also says that each claim gets every listed URL,
that the labeler prunes them and says so in `labeler_note`, and that results are also
reported under a strict sentence-local reading. It also says that chip lines with no claim
between them are one chip, which `bench/README.md` already said for the tooling; without it,
"chip to chip" would leave the first of two adjacent chips covering nothing.

Not covered here: `fetch_sources.py` still follows the old reach, see
SAU-BENCH-ENH-20261115-skeleton-rule5-reach. A chip whose source was not recovered is
SAU-BENCH-ENH-20261115-chip-source-not-recovered (Q51).

## Related
`bench/LABELING.md` rule 4 and 5, SAU-BENCH-ENH-20261103-claude-chip-format, task
`2026-11-15-fixtures-0005-0008` (Q49 to Q52).
