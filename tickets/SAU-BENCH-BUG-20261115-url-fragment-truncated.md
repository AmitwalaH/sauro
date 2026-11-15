# SAU-BENCH-BUG-20261115-url-fragment-truncated: A shown URL with a quote or a final full stop is stored shorter than the user saw it

**Date Discovered:** 2026-11-15
**Severity:** LOW
**Status:** OPEN
**Label:** [ticket]
**Found by:** Claude Code, measured by comparing each `sources shown:` line in 0005 to 0008
with the URLs recorded in the fixture JSON
**Filed by:** Claude Code

## Problem
Two of the 22 URLs under `sources shown:` in fixtures 0005 to 0008 are not recorded as shown.
Both are in 0007 and both carry a text fragment (`#:~:text=`) from the Gemini sources panel:

- The gktoday.in URL contains `tower's`. `URL_RE` in `bench/tools/fetch_sources.py` (line 56)
  stops at a quote, so the recorded URL ends at `launch%20tower` and loses 70 characters.
- The spacepolicyonline.com URL ends in `DATE.`. The trailing-punctuation rule drops the full
  stop, so the recorded URL loses 1 character.

The fetch is not affected: a fragment is never sent to the server. The JSON key simply is not
the string the user saw, and any later comparison of `answer.md` with the JSON by string
finds a mismatch.

## Why it matters
Small today. It matters once anything maps a citation in the answer to its `sources` entry by
exact string, for example a check that every shown URL is recorded.

## Options
1. Strip the `#...` fragment from every URL before it is recorded, and keep the full shown
   URL in `answer.md` only. Simple, and fragments carry no page identity.
2. Let quotes inside a fragment belong to the URL. Fixes this case, keeps the fragment, and
   makes the URL rule harder to read.

Recommendation: 1, test first. Recorded URLs in fixtures already committed are not changed.

## Related
`bench/README.md` "How the skeletons are made" (URLs), fixture 0007.
