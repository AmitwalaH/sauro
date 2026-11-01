# Labeling guide

This is the contract. Every fixture is labeled by this guide and the engine is measured against
those labels. If the guide is ambiguous, the labels are ambiguous, and then the benchmark means
nothing. So this file is written first and frozen after task 1.

**Version:** 0.1 draft, 2026-11-01. Not yet frozen.

## What a fixture is

One AI answer, as the user saw it, with its citations. Split into claims. Each claim gets one
label and, where a span exists, the exact span from the source.

```json
{
  "id": "0001",
  "source_model": "unknown | gpt | claude | gemini | perplexity | other",
  "domain": "health | news | school | code | finance | other",
  "collected_on": "2026-11-01",
  "answer_text": "the full answer, verbatim",
  "claims": [
    {
      "claim_id": "0001-01",
      "text": "the single sentence being checked",
      "cited_urls": ["https://..."],
      "label": "supported | partial | contradicted | unverifiable",
      "reason_code": "see table",
      "evidence_span": "verbatim text from the page, or null",
      "evidence_location": "a short note on where in the page, or null",
      "labeler_note": "why, in one sentence",
      "hard": false
    }
  ],
  "reviewed": false
}
```

The page content is stored next to the fixture as `0001.sources/<hash>.html` with the fetch
date, so labels can be re-checked against the same page later.

## How to split an answer into claims

1. One sentence is one claim. Split on sentence boundaries, not on commas.
2. A sentence with two checkable facts and one citation is still one claim. Label it on the
   weaker fact. Note the second fact in `labeler_note`.
3. Sentences that are not factual (greetings, "I hope this helps", questions back to the user,
   instructions like "consult your doctor") are dropped. They are not claims.
4. A sentence with no citation anywhere near it is a claim with label `unverifiable` and
   reason code `no_citation`. Do not go looking for a source.
5. A citation attaches to the sentence it follows, and to the sentence before that one only if
   the citation sits at the end of a paragraph that is clearly one point.

## How to label

Read the whole source page first. Then for each claim, in this order:

1. Can you find a span that is about the same thing? If no span exists at all, and the page
   loaded fine, the label is `unverifiable` with reason code `not_in_source`.
2. Does the span say the same thing, with the same strength? Then `supported`. Copy the span
   verbatim into `evidence_span`.
3. Does the span say a weaker, narrower, or hedged version of the claim, or the claim adds a
   number, a population, or a recommendation the span does not contain? Then `partial`. Copy
   the span. Say in the note what the claim added or dropped.
4. Does the span say the opposite, give a conflicting number, or does the page quote the
   claim only in order to disagree with it? Then `contradicted`. Copy the span.
5. Could you not read the page? Then `unverifiable` with the right reason code.

Pick the span that is the best single piece of evidence. If the support is spread over a
paragraph, copy the smallest window that holds all of it, and set `hard` to true.

## Reason codes

| Code | Used with | Meaning |
|---|---|---|
| `exact` | supported | Span matches nearly word for word |
| `paraphrase` | supported | Same meaning, different words |
| `hedge_dropped` | partial | Source says "may", "some", "can"; claim says it flatly |
| `scope_shift` | partial | Claim changes who, where, or when |
| `number_changed` | partial or contradicted | A quantity differs. Contradicted if the difference changes the conclusion |
| `recommendation_added` | partial | Claim adds advice the source does not give |
| `negated` | contradicted | Source says the opposite |
| `quoted_to_disagree` | contradicted | Source quotes the claim as a view it rejects |
| `not_in_source` | unverifiable | Page loaded, nothing on the topic |
| `no_citation` | unverifiable | Claim has no URL |
| `fetch_failed` | unverifiable | 404, timeout, DNS |
| `blocked` | unverifiable | Paywall, login, bot check |
| `js_only` | unverifiable | Page is empty without JavaScript |
| `other` | any | Explain in the note |

## The hard cases, decided in advance

These are the places a labeler will hesitate. The decision is made here so it is made once.

- **The claim is true in the world but not on the page.** Label by the page. `unverifiable`,
  `not_in_source`. sauro checks citations, not reality. See `SCOPE.md`.
- **The span is in a user comment, a sidebar, or a quoted tweet, not the article.** Treat it
  as not in the source. The article is the source.
- **The source hedges and the claim hedges the same way.** `supported`.
- **The source gives a range and the claim gives a number inside the range.** `partial`,
  `scope_shift`. The claim is more precise than the evidence.
- **The source gives a number and the claim rounds it.** 31% to "about 30%": `supported`.
  31% to "a third": `supported`. 31% to "most": `contradicted`, `number_changed`.
- **The claim blends two sources and cites one.** Label against the cited one only.
- **The page changed between the AI's answer and your fetch.** Label against what you fetched.
  Note it. This is why sources are stored with the fixture.
- **You cannot decide between two labels after reading twice.** Pick the weaker one (the
  order is supported, partial, contradicted for strength of agreement), set `hard` to true,
  and write both options in the note. These are reviewed together.

## Quality rules

- Label from the stored page, not from memory of the page.
- Never label from the AI's own summary of the source.
- Do not use an AI to label. The labels are the thing the engine is judged by. If an AI writes
  them, the benchmark is an AI grading itself.
- Every `supported`, `partial`, and `contradicted` label must have a non-null
  `evidence_span` that appears verbatim in the stored page. A script checks this.
- Two labelers for the first 20 fixtures. Disagreements are findings. If more than 3 of 20
  claims disagree after discussion, this guide is not clear enough and gets revised before any
  more labeling.

## What the first 100 fixtures should cover

Aim for roughly: 30 health, 20 news, 20 school or general knowledge, 15 code or technical,
15 finance or legal. At least 10 fixtures from each of three different models. At least 15
claims in each of the four states, so no state is measured on a handful.
