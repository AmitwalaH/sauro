# SAU-BENCH-BUG-20261115-fixture-file-names-unchecked: A file name in a fixture can point outside its folder

**Date Discovered:** 2026-11-15
**Severity:** MEDIUM
**Status:** OPEN
**Label:** [ticket]
**Found by:** Claude Code, read in the source on 2026-11-15
**Filed by:** Claude Code

## Problem
The fixture JSON says where each stored page lives, in `sources[].file` and
`fetch_failures[].file`. Since Q25, maintainers will run the tools on fixtures from pull
requests whose pages they do not have. Two places trust the name:
- `fetch_sources.py`, in `run`: a retried failed URL reuses `fetch_failures[].file` and writes
  the new body to `<id>.sources/<file>`. A name such as `../../x.html` writes outside the
  folder.
- `check_fixtures.py`, in `source_files` and the hash loop: it reads `<id>.sources/<file>`. A
  name such as `../0002.sources/1.html` checks a span against another fixture's page. That is
  the mistake SAU-BENCH-ENH-20261101-source-page-mapping was fixed to prevent.

Task `pages-local` guards the new refetch path only: `refetch_absent` refuses a name that is
not a plain file name.

## Why it matters
The first is a write outside the repo folder by a tool a maintainer runs. The second lets a
fixture pass with evidence from the wrong page.

## Fix
One rule, in one place: a stored file name must be a plain file name. `check_fixtures.py`
fails a fixture that breaks it. `fetch_sources.py` uses the same function before any write.

## Related
SAU-BENCH-ENH-20261101-source-page-mapping, SAU-BENCH-BUG-20261115-new-page-takes-recorded-name.
