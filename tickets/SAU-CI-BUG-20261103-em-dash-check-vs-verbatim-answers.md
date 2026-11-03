# SAU-CI-BUG-20261103-em-dash-check-vs-verbatim-answers: CI goes red as soon as a saved AI answer is committed

**Date Discovered:** 2026-11-03
**Severity:** MEDIUM
**Status:** RESOLVED
**Label:** [decision]
**Found by:** Claude Code, measured by running the CI em dash grep on the working tree
**Filed by:** Claude Code

## Problem
The `docs checks` job in `.github/workflows/ci.yml` fails on any em dash in any `*.md` file in
the repo. `bench/README.md` tells the labeler to paste the AI answer verbatim into
`answer.md`. AI answers use em dashes. On 2026-11-03 the grep matched the owner's uncommitted
`0002.sources/answer.md`, `0003.sources/answer.md` and `0004.sources/answer.md`, nine lines in
all. Once any of them is committed, every push is red.

## Why it matters
Removing the dashes breaks "verbatim", and the claim text would no longer match what the user
saw. Living with a red docs job teaches people to ignore red.

## Options
1. Exclude `bench/fixtures/` from the em dash grep (`--exclude-dir=fixtures`, or a path
   filter). The style rule is for files we write, and the answers are data. Recommended.
2. Save answers as `answer.txt` instead of `answer.md`. Also works, but changes the format
   the owner already uses in four fixtures.
3. Replace em dashes in answers. Breaks the verbatim rule. Not recommended.

## Resolution
Owner chose option 1 on 2026-11-03. The grep in the `docs checks` job of `ci.yml` is now
`grep -rn --include='*.md' --exclude-dir=fixtures $'\xe2\x80\x94' .`. Tested on a scratch
copy of the tree: an em dash planted in `bench/fixtures/0009.sources/answer.md` is skipped,
and one planted in a root `NOTE.md` still fails the check. The exclusion skips any directory
named `fixtures`, not only `bench/fixtures/`.

## Related
`bench/README.md` "answer.md", task `fixture-tooling` (the `ci.yml` edit there was limited to
the bench job).
