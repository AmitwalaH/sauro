# Scope

This file says what sauro does and what it refuses to do. A feature request that lands in the
non-goals is closed with a link here, not debated.

## The one problem

Given a sentence S written by a model and a document D the model cited for it, decide whether
D licenses S, and show the span in D that proves it.

Four states, and only four:

| State | Meaning | Example |
|---|---|---|
| Supported | D contains a span that says what S says, with the same certainty and polarity | S: "Ibuprofen can raise blood pressure." D: "Ibuprofen can raise blood pressure in some patients." |
| Partial | D contains a span on the same point, but S overstates, narrows, or shifts it | S: "Ibuprofen raises blood pressure." D: "may raise blood pressure in some patients." |
| Contradicted | D contains a span that says the opposite, or a conflicting number | S: "recommends avoiding NSAIDs." D: "talk to your doctor before using NSAIDs." |
| Unverifiable | sauro could not get or read D, or S has no citation | Paywall, 404, bot block, JS-only page, no URL given |

Unverifiable is never collapsed into Contradicted. "I could not check" and "this is wrong" are
different facts and the user needs to know which one they have.

## Goals for v1

- Rust library with one public function: claim plus document in, verdict plus span plus
  confidence out. Same input, same output, every time.
- CLI that takes a file of AI output with URLs, fetches, checks, and prints a report.
- Snapshot and hash of every fetched page, so a verdict is reproducible later.
- A benchmark of hand-labeled real AI answers, with precision and recall per state published
  in the README and enforced in CI.
- MCP server and skill so Claude Code and similar agents can check their own citations before
  replying.
- GitHub Action so a repo can fail a pull request on a citation that rots or contradicts.

## Non-goals, written down so nobody has to argue

- **Judging whether the source itself is true.** sauro checks that the source says it, not
  that the source is right. A supported claim from a bad source is still Supported.
- **Detecting AI-generated text.** Not this project.
- **A reliability score, truth score, or trust percentage.** These are unfalsifiable and they
  are what makes the existing tools untrustworthy.
- **A web UI or browser extension.** Decided 2026-11-01 by the owner.
- **Calling a cloud LLM from the core.** The core is deterministic. A local model may be added
  later for claim splitting, behind a flag, and must still return the evidence span.
- **PDF sources in v1.** Two-column PDFs scramble text order and poison alignment. Ticket.
- **Non-English sources in v1.** Alignment across languages needs translation. Ticket.
- **Checking claims without a citation.** No URL means Unverifiable. sauro does not go and
  search for one.
- **Fetching through paywalls, logins, or bot blocks.** Those are Unverifiable with a reason
  code. sauro does not evade them.

## The rule under all of it

sauro may never be more confident than the evidence it can display. When in doubt it says it
could not tell, and shows what it found.
