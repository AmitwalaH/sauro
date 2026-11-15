# SAU-BENCH-ENH-20261115-assistant-proposed-first-pass: The first labels on fixtures 0001 to 0004 were proposed by an AI, which the labeling guide forbids

**Date Discovered:** 2026-11-15
**Severity:** HIGH
**Status:** RESOLVED
**Label:** [decision]
**Found by:** Claude Code, read in `bench/LABELING.md` and measured in the fixture notes
**Filed by:** Claude Code

## Problem
`bench/LABELING.md`, "Quality rules", says: "Do not use an AI to label. The labels are the
thing the engine is judged by. If an AI writes them, the benchmark is an AI grading itself."
The foundation task says Claude Code "never fills in a label".

The first-pass labels on fixtures 0001 to 0004 (45 claims) did not come from the owner alone.
Provenance, as stated by the owner on 2026-11-15 (Q27):
- 34 claims, in 0002, 0003 and 0004: proposed by the assistant, accepted by the owner. Each
  `labeler_note` says "Label proposed by assistant, accepted by owner 2026-11-15; first pass."
- 9 claims in 0001 (`0001-01`, `-02`, `-03`, `-06`, `-07`, `-08`, `-10`, `-11`, `-12`), all
  `unverifiable`, `no_citation`: assigned mechanically by the assistant. Their notes do not
  say so.
- 2 claims in 0001 (`0001-14`, `0001-15`): proposed by the assistant and typed by the owner.
  Their notes do not say so.
- No claim was labeled by the owner alone.

Counted on 2026-11-15: 34 of 45 notes carry the provenance sentence, not all 45 as the task
file said. Notes are not edited (off-limits); this ticket is the record for the other 11.

## Why it matters
If these labels became the baseline, the engine would be scored against what an AI thought,
which is the failure the guide's rule exists to prevent.

## Options
1. Commit the fixtures with their provenance recorded, as an exception with conditions.
2. Hold the commit until the owner's blind second pass.

## Resolution
Owner chose option 1 on 2026-11-15 (Q26 a), with two conditions:
1. Fixtures 0001 to 0004 stay `"reviewed": false`.
2. No baseline is recorded or published from these labels. The owner's blind second pass
   produces the real labels.

The second pass is the owner re-labeling without looking at the first pass (foundation Q1).

## Related
`bench/LABELING.md` "Quality rules", task `foundation` Q1, SAU-BENCH-ENH-20261103-unlabeled-claims-in-baseline.
