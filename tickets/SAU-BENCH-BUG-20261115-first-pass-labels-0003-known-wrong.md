# SAU-BENCH-BUG-20261115-first-pass-labels-0003-known-wrong: Some first-pass labels on fixture 0003 are known to be wrong

**Date Discovered:** 2026-11-15
**Severity:** HIGH
**Status:** OPEN
**Label:** [ticket]
**Found by:** The owner, walked: `0003.sources/3.html` checked in a browser on 2026-11-15.
Claude Code measured the labels and where each phrase sits in the stored page.
**Filed by:** Claude Code

## Problem
The first-pass labels on fixture 0003 were proposed by an assistant and accepted by the owner
(SAU-BENCH-ENH-20261115-assistant-proposed-first-pass). Some are wrong:

- `0003-03` is `partial`, `scope_shift`, and `0003-04` is `unverifiable`, `not_in_source`. The
  page body supports both.
- `0003-10` is probably wrong too.
- The spans and notes on `0003-01`, `0003-08` and `0003-09` point at the page's Questions and
  Answers block, when the article body has the evidence.

Cause, as the owner states it: the assistant's keyword search showed only the first match per
word, so it missed later matches in the body and took spans from the Q and A block.

Measured on 2026-11-15: the labels above are as stated in `bench/fixtures/0003.json`. The owner's
example body phrases ("your kidneys work harder to remove it", "This pulls fluids from your
tissues, making you dehydrated", "Symptoms can come on slowly") each appear once in the stored
page, in the article body, not in the Q and A block.

Not fixed here. The fixtures are `"reviewed": false`, and the owner's blind second pass
replaces these labels. No label, span or note was changed.

## A gap in `bench/LABELING.md`
The page embeds a Questions and Answers block from the publisher. It is visible inline in the
article. Its answers are attributed to named clinicians, and one answer is from a patient, not
a clinician (measured by the role words on each attribution, no names recorded).

The guide says a span "in a user comment, a sidebar, or a quoted tweet, not the article" is
not in the source. It does not say whether an embedded publisher Q and A block is the article
or a sidebar. The block is marked up as an `<aside>`, the usual element for a sidebar, yet a
reader sees it as part of the article. Nor does the guide say whether an answer from a patient
counts like an answer from a clinician, or like a user comment.

This decides whether every extractor in spike 1 was wrong or right to drop the block.
`bench/LABELING.md` is off-limits, so a change goes through a `[decision]`.

Options for that decision:
1. A publisher's Q and A block shown in the article is the article. Every answer in it counts.
2. It is the article, but an answer from a patient is treated like a user comment and is not
   in the source.
3. It is a sidebar and is not in the source.

Recommendation: option 2. The publisher chose to show the block inline, so a reader takes it as
the page speaking. A patient's answer is closest to the comment rule the guide already has.

## Why it matters
These labels feed spike 1's ground-truth counts, and any baseline built from them. Wrong
`unverifiable` labels would score a correct engine as wrong. Spans pointing at the Q and A
block made spike 1 count evidence as lost when the body still had it.

## Related
SAU-BENCH-ENH-20261115-assistant-proposed-first-pass,
SAU-CORE-ENH-20261115-evidence-outside-main-content, `docs/extraction-spike.md` "Caveat,
2026-11-15", `bench/LABELING.md` "The hard cases, decided in advance".
