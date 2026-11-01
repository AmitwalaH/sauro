# SAU-BENCH-ENH-20261101-source-page-mapping: A stored page cannot be linked to the URL it was fetched from

**Date Discovered:** 2026-11-01
**Severity:** HIGH
**Status:** RESOLVED
**Label:** [decision]
**Found by:** Claude Code, read in `bench/LABELING.md` while writing `check_fixtures.py`
**Filed by:** Claude Code

## Problem
A labeler stores each cited page next to the fixture. `LABELING.md` named the file
`0001.sources/<hash>.html` but did not say what is hashed or with which algorithm. It said the
page is stored "with the fetch date" but not where. So nothing linked a claim's cited URL to
its stored file.

Because of that, the first version of `check_fixtures.py` looked for a span in any page of the
fixture. A span copied from the wrong page of the same fixture would have passed.

## Why it matters
The benchmark would accept a label checked against a page the claim never cited. The engine
would then be scored against evidence that is not the claim's evidence.

## Options (for decisions)
1. Name each file by a hash of its URL. Needs an agreed algorithm and URL normalization, and
   the fetch date still needs a home.
2. A `sources` list in each fixture, `[{"url", "file", "fetched_on"}]`. Explicit, no hash
   convention, and the fetch date has a field. Recommended.
3. Keep matching against any page in the fixture. Simplest, but it is the weakness above.

## Resolution
Owner chose option 2 on 2026-11-01. `LABELING.md` now describes the `sources` list and
replaces the `<hash>.html` sentence. `check_fixtures.py` checks each span against the claim's
own cited pages through `sources`, and fails when a cited URL is not listed or its file is
missing. A URL that could not be fetched needs no entry, because its claim is `unverifiable`
with no span.

## Related
SAU-BENCH-ENH-20261101-verbatim-definition, `docs/extraction-spike.md`.
