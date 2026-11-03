# Contributing to sauro

Thank you for looking. This file says how contributions get in. It is short on purpose.

## Before you write code

1. Read [`SCOPE.md`](SCOPE.md). If your idea is in the non-goals, it will be closed with a
   link there. Open a discussion first if you think a non-goal is wrong.
2. Read [`PROJECT.md`](PROJECT.md) for the stack, the layout, the check suite and what is
   frozen.
3. Look in [`tickets/`](tickets/) and open issues. Most work starts from a ticket.

## The most useful contribution: a wrong verdict

sauro is measured by its benchmark. If sauro gives a verdict you can show is wrong, that is a
bug in the engine or a gap in the labeling guide, and either one matters more than a feature.
Open an issue with the "Wrong verdict" template. Include the claim, the URL, what sauro said,
what you think it should say, and the span from the page that proves it.

## Benchmark fixtures

Fixtures in `bench/fixtures/` are labeled by hand under [`bench/LABELING.md`](bench/LABELING.md).

- Do not label with an AI. The labels are what the engine is judged by.
- Every supported, partial or contradicted label needs an `evidence_span` that appears
  verbatim in the stored page. A script checks this and the pull request fails if it does not.
- Fixtures marked `"reviewed": true` are frozen. A label change needs its own pull request with
  the reason in the description.
- The baseline file `bench/baseline.json` is never edited by hand. If your change moves the
  numbers, say so in the pull request, and a maintainer re-records it.

## Code

- Run the check suite in `PROJECT.md` before you open a pull request and paste the results in
  the description. Green means every line green or every red named.
- One decision per pull request. A pull request that fixes a bug and refactors a module is two
  pull requests.
- Tests check real output. A test that searches the source for a word is not a test.
- Write the test first and say in the pull request what it failed on before the fix.
- Comments say why, not what.
- No new dependency without a line in the pull request saying what it replaces and why the
  existing code could not do it.
- Plain English in docs and messages. Short sentences. No em dashes.

## Pull request description

Use the template. The parts that matter: what someone sees before and after, what else the
change touches, what you chose not to fix, and the check results.

## Commits

Keep the message format in `PROJECT.md`. Nobody commits to `main` directly, including
maintainers. Pull requests are merged with a merge commit, so every commit on your branch lands
on main as is; keep each one clean.

## Questions

Open a discussion. If you are not sure whether something is a bug, a decision or out of scope,
ask. A question costs a minute.
