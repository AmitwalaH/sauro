# SAU-CORE-ENH-20261115-evidence-outside-main-content: Every extractor drops evidence that sits in a page module a reader sees

**Date Discovered:** 2026-11-15
**Severity:** HIGH
**Status:** OPEN
**Label:** [decision]
**Found by:** Claude Code, measured on 2026-11-15 by running spike 1 on the 16 stored pages
**Filed by:** Claude Code

## Problem
In spike 1, 5 of 31 labeled spans (16%) were lost by every extractor measured: Python
trafilatura and all four Rust candidates. All five are in one Questions and Answers block on
`0003.sources/3.html`, an `<aside>` accordion inside the article body. The best single
extractor, `rs-trafilatura`, kept 26 of 31, and those five are the ones it lost. (The first
version of this ticket said the block was outside the article body. That was wrong; corrected
2026-11-15 after the owner checked the page in a browser.)

The 5 of 31 overstates the evidence lost. The article body states equivalent evidence for
several of those claims, and the extractors keep it. The spans were taken from the Q and A
block by the assistant-proposed first pass. See
SAU-BENCH-BUG-20261115-first-pass-labels-0003-known-wrong and the caveat in
`docs/extraction-spike.md`. Whether the block counts as the source at all is an open gap in
`bench/LABELING.md`, recorded in that ticket.

Other misses also sat in page modules, and the two extractor families lose different ones. The
Readability ports drop a key takeaways list box and an introduction block. The Trafilatura
family drops a collapsed `<details>` expander. So no choice of extractor keeps all of the
evidence.

How the spans were chosen favours extractors (Q43): they lean toward prose. On spans chosen
another way, losses are likely higher.

## Why it matters
sauro promises it never reports a verdict it cannot show evidence for. If the engine matches
only against extracted text, a claim whose evidence is in an aside or an expander gets
Unverifiable while the page does support it. A user would read that as the source not saying
it, which is false.

## Options
1. Match against the full rendered text, the same rule as `page_text` that the labels are
   defined on. Extraction is not used to decide. Keeps all evidence by construction. More
   navigation and boilerplate text to search, so a short span is more likely to match in the
   wrong place. That needs measuring.
2. Match against extracted text first, and fall back to the full rendered text when nothing
   matches, showing the user the span came from outside the article. Keeps the evidence, and
   two code paths.
3. Match against extracted text only, and pick the extractor that loses least. Simplest, and
   loses 16% of spans on this data whatever the choice.

Recommendation: option 1, measured first. A spike can count how often a span matches more
than once in the full text, against the extracted text. It depends on the false-match rate
being low enough. Decide this before re-running trigger 1: under option 1 the extractor choice
matters much less, and trigger 1 would measure the wrong thing.

## Related
`docs/extraction-spike.md` "Result" and "Recommendation", SAU-BENCH-ENH-20261115-spike1-sample-size.

Two lines in `PROJECT.md` assume extraction is a stage of the engine and change with this
decision: the stack row "Main content extraction: Rust readability crate", which names the
family that lost the most spans in spike 1, and revisit trigger 1.
