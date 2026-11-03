# SAU-BENCH-BUG-20261103-git-normalizes-stored-pages: Committing a stored page with CRLF line endings changes it, and CI then fails its hash

**Date Discovered:** 2026-11-03
**Severity:** HIGH
**Status:** OPEN
**Label:** [decision]
**Found by:** Claude Code, measured in a throwaway git repo on 2026-11-03
**Filed by:** Claude Code

## Problem
`.gitattributes` starts with `* text=auto eol=lf`. Git stores every text file with LF line
endings and checks it out that way. Some sites serve CRLF. On 2026-11-03 four of the owner's
stored pages had CRLF lines: `0001.sources/3.html` (624), `0002.sources/3.html` (1964),
`0002.sources/4.html` (1), `0004.sources/4.html` (145).

Measured: `0001.sources/3.html` copied into a fresh repo with the same `.gitattributes`,
committed, then cloned. Before: sha256 `c3fe8723de21d663...`, which is what `0001.json`
records. After clone: `7777af6cd369ba9f...`, with 0 CRLF lines left. Git warns "CRLF will be
replaced by LF the next time Git touches it", and the owner's own working copy keeps CRLF, so
the check passes locally and fails in CI.

## Why it matters
The page in the repo is no longer the page that was fetched, which is the same harm as an
editor rewrite. And since task `chip-scope`, `check_fixtures.py` fails the fixture in CI on a
fresh checkout. This must be settled before any fixture with a CRLF page is committed.

## Options
1. Add `bench/fixtures/*.sources/** -text` to `.gitattributes`, so git stores stored pages
   byte for byte. Recommended. Pages already committed would need re-adding, but none are yet.
2. Have `fetch_sources.py` hash the body after converting CRLF to LF. Hides the change
   instead of preventing it, and the stored page still differs from the fetched bytes.
3. Store pages with a `.bin` extension. Git treats them as binary, but they stop opening as
   HTML.

## Related
SAU-BENCH-BUG-20261103-stored-page-hash-unchecked. `.gitattributes` was not in task
`chip-scope`'s approved file list.
