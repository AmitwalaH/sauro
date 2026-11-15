# SAU-BENCH-ENH-20261115-pages-local: Copies of other people's web pages would be published in a public repo

**Date Discovered:** 2026-11-15
**Severity:** HIGH
**Status:** RESOLVED
**Label:** [decision]
**Found by:** owner, before the first fixture commit
**Filed by:** Claude Code

## Problem
Each fixture stores the pages its claims cite, byte for byte, in `bench/fixtures/<id>.sources/`.
Fixtures 0001 to 0004 hold 16 such pages, 2,762,481 bytes in all (measured 2026-11-15). They
are copies of third-party sites: NHS, Mayo Clinic, WebMD and others. Committing them puts full
copies of those pages in a public repo under an Apache-2.0 project. No page had been
committed on any branch when this was decided (checked with `git log --all`).

## Why it matters
Publishing someone's page is a different act from reading it. The labels only need the page
to be checkable, not to be republished.

## Options
1. Commit the pages. Anyone can re-check every span and hash, and CI checks them. This relies
   on a fair-use style argument for each page.
2. Commit pointers and hashes only. The JSON keeps URL, fetch date, sha256 and the evidence
   span. The page stays on the labeler's machine. CI can no longer check a span against its
   page.

What other datasets do, from a brief look on 2026-11-15. This is not legal advice.
- Common Crawl publishes full copies of crawled pages. Wikipedia describes it as distributed
  from the US under fair use claims, and Common Crawl's own FAQ says the data cannot be
  republished unless fair use allows it.
- LAION-5B publishes URLs, captions and metadata, not the images. Its blog says the metadata
  is CC-BY 4.0 while the images keep their own copyright. Users fetch the images themselves
  with img2dataset. LAION staff expected about 20% of LAION-400M links to be dead.

The research summary above comes from secondary sources and the projects' own pages. No court
ruling was found on either practice.

## Resolution
Owner chose option 2 on 2026-11-15 (Q25). Task `pages-local`:
- `.gitignore` ignores every file under `bench/fixtures/*.sources/` except `answer.md`.
- `check_fixtures.py` counts an absent page instead of failing it, and `--require-pages`
  makes it a failure. The labeler runs that before a fixture commit.
- `fetch_sources.py` fetches an absent page back under its recorded name. It never writes
  the JSON.

Measured the cost on 2026-11-15: refetching the 16 pages fetched on 2026-11-03 gave 15 that
no longer match their sha256 byte for byte. All 32 evidence spans were still found in the
refetched pages. So a refetch restores the text a label rests on, today, but not the page that
was labeled. Only the labeler's copy can do that.

What is weaker now:
- CI no longer checks spans or hashes. See SAU-CI-ENH-20261115-require-pages-hook.
- The labeler's disk is the only full copy. See SAU-BENCH-ENH-20261115-private-page-store.
- The benchmark gate in task 3 needs pages. See SAU-BENCH-ENH-20261115-baseline-without-pages.
- `bench/LABELING.md` still says pages are "stored next to the fixture" so labels "can be
  re-checked against the same page later". That stays true on the labeler's machine. It is
  not edited (off-limits).

## Related
SAU-BENCH-BUG-20261103-stored-page-hash-unchecked, SAU-BENCH-BUG-20261103-git-normalizes-stored-pages,
SAU-CI-BUG-20261101-ci-fixture-check (its "the pull request fails" no longer holds on CI).

Sources:
- https://en.wikipedia.org/wiki/Common_Crawl
- https://commoncrawl.atlassian.net/wiki/spaces/CRWL/pages/2850820/Frequently+Asked+Questions
- https://laion.ai/blog/laion-5b/
- https://arxiv.org/pdf/2210.08402
- https://huggingface.co/datasets/laion/laion400m/discussions/8
