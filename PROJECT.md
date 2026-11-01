# Project card: sauro

Read `METHOD.md` first. This card says where we are. It changes when the project does.

**Last updated:** 2026-11-01 (project start, nothing built yet)

## What sauro is

A deterministic citation checker for AI answers. Given a sentence written by a model and the
page it cites, sauro finds the matching span in the page and reports one of four states:
Supported, Partial, Contradicted, Unverifiable. It always shows the span it matched. It never
reports a verdict it cannot show evidence for.

One engine, three surfaces: a Rust library, a CLI, and an MCP server plus skill for Claude Code
and other agents. See `SCOPE.md` for what it is not.

## Repo

- GitHub: `github.com/AmitwalaH/sauro`
- Default branch: `main`. Nobody commits to `main` directly.
- Task branches: `task/<YYYY-MM-DD>-<slug>`. One task file per branch.
- License: Apache-2.0

## Commit policy for Claude Code (narrow, mechanical)

Rule 1 of the method allows a project card to define this. These are the only conditions under
which Claude Code may commit. If any condition is unclear, rule 1 applies as written: no commit.

1. Only on a branch named `task/<YYYY-MM-DD>-<slug>` that matches the open task file.
2. Only after the full check suite below is green and the results are pasted in the report.
3. Never push. Never commit to `main`. Never amend, rebase, squash, cherry-pick, or merge.
4. Commit message format, exactly:
   ```
   <area>: <what changed, user-visible, one line>

   Task: tasks/<task file name>
   Checks: <suite result in one line>
   ```
   Areas: core, cli, mcp, skill, bench, docs, ci.
5. One commit per completed step, not per file.

Pushing, opening pull requests, and merging are always done by a person.

## Stack

Decided 2026-11-01. Revisit triggers below.

| Part | Choice | Notes |
|---|---|---|
| Engine | Rust crate `sauro-core` | Deterministic. No LLM calls inside the core. |
| Fetching | `reqwest` | Timeouts and retries defined in one place. |
| HTML parsing | `scraper`, `html5ever` | |
| Main content extraction | Rust readability crate, to be chosen in spike 1 | See revisit trigger 1. |
| Sentence splitting | `unicode-segmentation` plus our own rule set | Rules live in one file. |
| Fuzzy alignment | `strsim` or `rapidfuzz` | |
| Snapshots and hashes | `rusqlite`, `blake3` | |
| Reports | `serde` JSON, plus a plain text renderer | |
| CLI | Rust, `clap`, single static binary | |
| MCP server | TypeScript, `@modelcontextprotocol/sdk`, shells out to the CLI | Thin. No logic. |
| Skill | `SKILL.md` installable with `npx skills add` | Tells Claude when to run the CLI. |
| Benchmark | JSON fixtures in `bench/`, frozen baseline file | Baseline is a judge. See rule 2. |
| Labeling tooling | Python scripts in `bench/tools/` | Tooling only, never the engine. |
| CI | GitHub Actions | |
| Build | Docker image for reproducible builds | |

Not in v1, by decision: PDF sources, embedding or semantic fallback, any web UI, any browser
extension, any cloud LLM dependency. Each is a ticket, not a feature.

## Revisit triggers (the things that would make a stack choice wrong)

1. **Extraction quality.** Spike 1 compares the Rust extractor and Python `trafilatura` on the
   first 50 fixture pages. If Rust agrees on fewer than 70%, the engine moves to Python.
2. **Engine viability.** If by the end of task 3 the CLI cannot give a correct four-state
   verdict on 30 of the first 50 fixtures, the language choice is wrong. Stop and decide.
3. **Semantic fallback.** If more than 15% of benchmark claims stay unmatched by exact and
   fuzzy alignment, open the embedding ticket.

## Layout (planned, created in task 1)

```
sauro/
  METHOD.md
  PROJECT.md
  SCOPE.md
  LICENSE
  README.md
  tasks/              one file per task
  tickets/            one file per finding
  crates/
    sauro-core/       the engine
    sauro-cli/        the binary
  mcp/                TypeScript MCP server
  skill/              SKILL.md
  bench/
    LABELING.md       the labeling guide, the contract for every fixture
    fixtures/         one JSON file per AI answer, hand-labeled
    baseline.json     frozen. Precision and recall per state. See frozen things.
    tools/            Python helpers for labeling and reporting, with their tests
  .github/workflows/
```

## Commands (the check suite)

Run all of these before touching anything and paste the results. Run them again at the end.

```bash
cargo fmt --all -- --check
cargo clippy --all-targets --all-features -- -D warnings
cargo test --all
python3 bench/tools/check_fixtures.py
python3 -m unittest bench/tools/test_check_fixtures.py
cargo run -p sauro-bench -- --check-baseline     # from task 3 onward
cd mcp && npm test                                # from task 4 onward
```

Nothing is green until every line is green or the red is named and explained.

## Frozen things

- `bench/baseline.json`: precision, recall and confusion matrix per state over all fixtures.
  Re-recorded only under method Step 11, one value at a time, with a dated note in
  `bench/BASELINE_LOG.md`.
- `bench/fixtures/*.json`: labels are frozen once reviewed. A label change is its own commit
  with a reason.

## Off-limits

- `bench/LABELING.md` after task 1 is approved. Changes go through a `[decision]`.
- Any file in `bench/fixtures/` that is marked `"reviewed": true`.
- The commit policy above. It is not edited by Claude Code.

## Tickets

Prefix `SAU`. Categories: `CORE`, `CLI`, `MCP`, `SKILL`, `BENCH`, `DOCS`, `CI`.
File name: `SAU-{CAT}-{BUG|ENH}-{YYYYMMDD}-{slug}.md` in `tickets/`.

## Environment

Owner works on Windows 11, Ubuntu on WSL, Docker, VS Code with the WSL extension, Claude Code.
The repo lives inside the Ubuntu filesystem, never under `/mnt/c/`.

## Failing by design

None yet.
