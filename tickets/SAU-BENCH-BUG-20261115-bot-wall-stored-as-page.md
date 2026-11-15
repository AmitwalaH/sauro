# SAU-BENCH-BUG-20261115-bot-wall-stored-as-page: A bot check page is stored as a good source

**Date Discovered:** 2026-11-15
**Severity:** LOW
**Status:** OPEN
**Label:** [ticket]
**Found by:** Claude Code, measured on 2026-11-15 while counting pages for spike 1
**Filed by:** Claude Code

## Problem
`bench/fixtures/0004.sources/4.html` (boots.com) is a bot check page. Its title is "Pardon Our
Interruption". It was stored with `fetch_status` 200 as a good page. It is 5,851 bytes and its
rendered text is 577 characters, whitespace ignored.

`fetch_sources.py` flags a 200 body as a wall only below `SMALL_BODY_BYTES = 500`. This one is
larger, so it passed.

The labeler note on `0004-07` calls it "an empty shell". The claim is `unverifiable`,
`not_in_source`. `bench/LABELING.md` also has `blocked` ("Paywall, login, bot check"). The
claim cites five pages and the others loaded, so which code fits is a label question for the
owner's blind pass. Nothing was changed.

## Why it matters
The labeler is told the page is good and has to notice it is not. Any per-page measure counts
it as an article: in spike 1 every extractor "kept" 0.64 to 0.68 of the wall's text.

## Options
1. Also flag a 200 page whose `<title>` matches a short list of known wall titles. Cheap, and
   it misses walls not on the list.
2. Flag a 200 page whose rendered text, without `<head>`, is under some small number of
   characters. Catches more, and needs a second threshold chosen from data.
3. Leave it to the labeler and add a line to `bench/README.md`.

Recommendation: option 2, measured on the pages fetched so far before choosing the number. It
shares the fix for SAU-BENCH-BUG-20261103-app-shell-with-title-passes.

## Related
SAU-BENCH-BUG-20261103-app-shell-with-title-passes, `docs/extraction-spike.md` "Result".
