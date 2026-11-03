# SAU-BENCH-BUG-20261103-editor-rewrites-stored-page: Opening a stored page in the editor can rewrite it

**Date Discovered:** 2026-11-03
**Severity:** MEDIUM
**Status:** RESOLVED
**Label:** [ticket]
**Found by:** Claude Code, read in the file. The cause is a guess, not observed.
**Filed by:** Claude Code

## Problem
`bench/fixtures/0001.sources/1.html` changed after it was fetched (recorded sha256
`6a84246a7d944bf25446aa5c6b50d286c31e4ded1eee38e27e8817c9309147ad`, on disk
`556968cb7dbac49e6e4b04f0bd2e6babd4cba7d2863c1a30d81c5e575fe44c1f`). It was opened in VS Code
just before, and is now laid out like Prettier output: attributes on their own lines, `/>`
endings. The first guess was format-on-save; the note below shows that guess was probably
wrong. It also gained a byte-order mark, which Prettier does not usually add; that part is
unexplained.

## Why it matters
Any save of a stored page rewrites the evidence. See
SAU-BENCH-BUG-20261103-stored-page-hash-unchecked for why that matters.

## Resolution
Task `chip-scope`. The fix is the read-only rule: `.vscode/settings.json` sets
`files.readonlyInclude` for `bench/fixtures/*.sources/*.html`, so VS Code cannot save a stored
page at all, whether by a format command, a keystroke or auto-save. `answer.md` stays
editable, because the owner writes it by hand.

The same file also turns off format-on-save, final-newline insertion and trailing-whitespace
trimming for HTML, Markdown and JSON. That was added first, on the guess that format-on-save
caused the rewrite. It is kept as a second layer for `answer.md` and fixture JSON, which are
not read-only.

Not covered: stored pages that are not `.html` (a `.pdf` or `.bin`), other editors, and
tools outside the editor. The sha256 check in `check_fixtures.py` catches whatever still
gets through.

## Note, 2026-11-03, after the settings landed
Read in the owner's editor settings: the user level makes Prettier the default formatter for
HTML, sets `files.autoSave` to `afterDelay` with a 10 ms delay, and does not set
`editor.formatOnSave`, which is off by default. Auto-save after a delay does not run
format-on-save. So the likely path was a manual Format Document, or any keystroke, saved
10 ms later. That is inferred, not observed. If so, the format-on-save settings would not
have blocked it, which is why the read-only rule above is the fix. `files.readonlyInclude`
exists in the installed VS Code build. The owner approved it as Q24.

## Related
SAU-BENCH-BUG-20261103-stored-page-hash-unchecked.
