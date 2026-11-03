# SAU-BENCH-BUG-20261103-app-shell-with-title-passes: A JavaScript-only page is stored as a good source when it has a title

**Date Discovered:** 2026-11-03
**Severity:** LOW
**Status:** OPEN
**Label:** [ticket]
**Found by:** Claude Code, measured by running `fetch_sources.py` on a scratch copy of the
owner's `0002.sources/answer.md` on 2026-11-03
**Filed by:** Claude Code

## Problem
An earlier version of `0002.sources/answer.md` listed a `chatgpt.com/c/...` URL. It returned
200 with a 652 KB body whose only visible text is its `<title>`, "ChatGPT", seven characters.
`fetch_sources.py` flags HTML with no rendered text as `empty_text`, but the rendered text
from `check_fixtures.page_text` includes the title. So the page went into `sources` as a good
page. The owner has since removed that URL.

## Why it matters
The labeler opens a page with nothing to label and must notice it is `js_only`. The script
was meant to tell them. The spike would also count it as a page.

## Options
1. For the `empty_text` test only, ignore text inside `<head>`. One change in
   `fetch_sources.py`, and `page_text` stays as the verbatim rule needs it. Recommended.
2. Flag rendered text under some small number of characters. A second threshold to choose.

## Related
`bench/README.md` "Failed fetches", SAU-BENCH-ENH-20261101-verbatim-definition.
