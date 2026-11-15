# SAU-BENCH-ENH-20261115-question-not-exact-prompt: The question line in 0002 to 0004 is not the prompt the owner typed

**Date Discovered:** 2026-11-15
**Severity:** LOW
**Status:** OPEN
**Label:** [ticket]
**Found by:** the owner, stated in task `2026-11-15-fixtures-0005-0008`; the lines read in each
`answer.md` by Claude Code
**Filed by:** Claude Code

## Problem
`bench/README.md` says the `question:` header holds "the exact question". As stated by the
owner on 2026-11-15, the prompts for fixtures 0002, 0003 and 0004 also carried "pls search the
web and list source urls". The `question:` lines hold only the plain question, for example
0002 "How much caffeine per day is considered safe for adults?". Fixtures 0005 to 0008 used
the plain question, so their lines are exact. 0001 was not named.

## Why it matters
An instruction to search and list URLs changes how an assistant cites, and so how many claims
have a citation at all. Comparing citation behaviour across fixtures, or across models, mixes
two kinds of prompt without saying so.

## Options
1. Add an optional `prompt:` header for the text as typed, kept when it differs from
   `question:`, and fill it for 0002 to 0004 in a later task. `read_answer` already accepts
   extra header keys. The README states the field.
2. Change the `question:` lines in 0002 to 0004 to the typed prompt. One field, but the
   question then no longer reads as a question.

Recommendation: 1. Owner to confirm 0001.

## Related
`bench/README.md` "answer.md".
