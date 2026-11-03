# SAU-BENCH-BUG-20261103-stored-page-hash-unchecked: A stored page can change after it was fetched and every check still passes

**Date Discovered:** 2026-11-03
**Severity:** HIGH
**Status:** RESOLVED
**Label:** [ticket]
**Found by:** Claude Code, measured with `sha256sum` against `0001.json` on 2026-11-03
**Filed by:** Claude Code

## Problem
`fetch_sources.py` records a sha256 of every page it stores, but nothing read it. On
2026-11-03 the owner's `bench/fixtures/0001.sources/1.html` (NHS, ibuprofen for adults) no
longer matched its record:

- recorded in `0001.json`: `6a84246a7d944bf25446aa5c6b50d286c31e4ded1eee38e27e8817c9309147ad`
- file on disk: `556968cb7dbac49e6e4b04f0bd2e6babd4cba7d2863c1a30d81c5e575fe44c1f`

The file was modified at 12:06 UTC, two minutes after the 12:04 fetch, grew to 65,199 bytes,
starts with a byte-order mark, and is laid out like Prettier output. `check_fixtures.py`
passed, because the verbatim rule ignores whitespace and a reformat keeps the text.

## Why it matters
The stored page is the evidence a label is checked against, and the reason sources are kept
with the fixture. A page that is no longer what was fetched makes "label against what you
fetched" untrue, and nobody would know.

## Resolution
Task `chip-scope`: `check_fixtures.py` now hashes every `sources` entry that has a `sha256`,
whether or not a claim cites it, and fails naming the file on a mismatch or a missing file.
Entries without a `sha256` (the guide's shape does not require one) are not hash-checked. The
summary line counts the hashes checked. The owner deletes `1.html` and fetches it again.

## Related
SAU-BENCH-BUG-20261103-editor-rewrites-stored-page, SAU-BENCH-BUG-20261103-git-normalizes-stored-pages.
