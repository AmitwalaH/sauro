# SAU-BENCH-ENH-20261115-private-page-store: The only full copy of the evidence is on one laptop

**Date Discovered:** 2026-11-15
**Severity:** MEDIUM
**Status:** OPEN
**Label:** [decision]
**Found by:** Claude Code, measured on 2026-11-15
**Filed by:** Claude Code

## Problem
Since Q25, stored pages live only on the labeler's machine. For fixtures 0001 to 0004 that is
16 pages, 2,762,481 bytes. A refetch does not bring them back: on 2026-11-15, 15 of the 16
pages fetched on 2026-11-03 no longer matched their sha256. If the copy is lost:
- No fixture can pass `check_fixtures.py --require-pages` again, so no label can be changed
  under the README workflow.
- A second labeler cannot see the page the first one labeled.
- CI cannot check spans or hashes at all. See SAU-CI-ENH-20261115-require-pages-hook.

The owner made a local backup on 2026-11-15.

## Why it matters
The pages are the evidence every label rests on. Losing them is losing the benchmark's
ability to be re-checked.

## Options
1. A private store the owner controls, such as a private git repo or bucket, holding
   `<id>.sources/` byte for byte. CI reads it with a secret, so CI runs `--require-pages`
   again. Nothing is published. Needs one secret and one CI step.
2. Local backups only, by the owner, on a schedule. No infrastructure. CI stays weak, and a
   second labeler still needs the pages handed over.
3. Record a Wayback Machine snapshot URL for each page at fetch time. The `id_` URL form
   returns the archived bytes without rewriting. Untested here: the archive's capture is a
   different fetch from ours, so its bytes would likely not match our sha256 either.

Recommendation: option 1. It restores the CI judge, gives a second labeler the same pages, and
is the backup, in one place. It depends on the owner being comfortable that a private store
is not "publishing" under Q25.

## Related
SAU-BENCH-ENH-20261115-pages-local, SAU-BENCH-ENH-20261115-baseline-without-pages.
