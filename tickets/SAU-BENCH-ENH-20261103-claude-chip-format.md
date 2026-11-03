# SAU-BENCH-ENH-20261103-claude-chip-format: Claude's citation chips become claims and its sources land on the wrong sentence

**Date Discovered:** 2026-11-03
**Severity:** MEDIUM
**Status:** OPEN
**Label:** [decision]
**Found by:** Claude Code, measured by running `fetch_sources.py` on a scratch copy of the
owner's `0002.sources/answer.md` (model: claude) on 2026-11-03
**Filed by:** Claude Code

## Problem
The chip rule decided at checkpoint 1 recognises a bare domain line such as `nhs.uk`, as the
ChatGPT answer in 0001 shows. The Claude answer in 0002 shows chips as site names with no
dot: `acibademinternational`, `newhope`. It also has a `Sources:` block of page titles,
separate from the `sources shown:` URLs. The script therefore:

- makes each chip word a claim (`0002-05` "acibademinternational", `0002-06` "newhope"),
- makes each title line a claim (`0002-20` "Sources:" to `0002-26`),
- finds no chip, so attaches every `sources shown:` URL to the last claim, which is a title
  line.

Measured on that copy: 26 skeletons, of which 7 are chip words and 7 are the `Sources:` block
(`0002-20` to `0002-26`; "How Much Caffeine Is Too Much? Your Daily Limit" also splits in two).
The labeler deletes those 14 and moves every URL by hand.

Separately, the titles under `Sources:` (New Hope, Acibadem, Tasting Table, Corner Coffee,
Philadelphia Magazine) do not name the same sites as the `sources shown:` URLs (fda.gov,
caffeineinformer, upmc, baristalife, nutritionaloutlook). That is a question about the saved
answer, not the script.

## Why it matters
The skeletons are meant to save typing. On Claude answers they add work, and they put
citations on lines that are not claims. That is exactly the revisit trigger in
`bench/README.md`.

## Options
1. Extend the chip rule. A line of a single lowercase word with no spaces and no full stop,
   directly after a sentence, is a chip. A `Sources:` line and everything after it, up to
   `sources shown:`, is not claims. Risk: a one-word answer line is read as a chip.
2. Owner deletes chip lines and the title block from `answer.md` when saving, and the README
   says so. No code change, but `answer_text` is then not verbatim.
3. Leave it. The labeler fixes 0002-style fixtures by hand, and the revisit trigger decides.

Recommendation: 1, after the owner has saved two or three more Claude answers to confirm the
chip shape is stable.

## Related
`bench/README.md` "How the skeletons are made", task `fixture-tooling` Q11.
