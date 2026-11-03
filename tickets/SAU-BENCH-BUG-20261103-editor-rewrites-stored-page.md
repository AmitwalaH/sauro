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
endings. The likely cause is format-on-save. It also gained a byte-order mark, which format
on save does not usually add; that part is unexplained.

## Why it matters
Any save of a stored page rewrites the evidence. See
SAU-BENCH-BUG-20261103-stored-page-hash-unchecked for why that matters.

## Resolution
Task `chip-scope`: `.vscode/settings.json` turns off format-on-save, final-newline insertion
and trailing-whitespace trimming for HTML, Markdown and JSON. VS Code cannot scope settings
to a folder, so they are set per language. The only HTML in the repo is stored pages; the
Markdown and JSON rules also cover our own docs.

Not covered: the byte-order mark, a user-level `files.encoding` setting, other editors, and
saving by hand. `files.readonlyInclude` for `bench/fixtures/*.sources/*.html` would block
every save of a stored page; it was not in the task, so it is offered, not done. The sha256
check catches whatever still gets through.

## Note, 2026-11-03, after the settings landed
Read in the owner's editor settings: the user level makes Prettier the default formatter for
HTML, sets `files.autoSave` to `afterDelay` with a 10 ms delay, and does not set
`editor.formatOnSave`, which is off by default. Auto-save after a delay does not run
format-on-save. So the likely path was a manual Format Document, or any keystroke, saved
10 ms later. That is inferred, not observed. If so, the format-on-save settings above do not
block it. `files.readonlyInclude` exists in the installed VS Code build and would. Whether
this ticket is truly resolved is for the owner to decide.

## Related
SAU-BENCH-BUG-20261103-stored-page-hash-unchecked.
