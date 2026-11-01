# SAU-CI-ENH-20261101-pin-rust-toolchain: CI can turn red with no code change when a new Rust release ships

**Date Discovered:** 2026-11-01
**Severity:** LOW
**Status:** OPEN
**Label:** [ticket]
**Found by:** Claude Code, read in `.github/workflows/ci.yml`
**Filed by:** Claude Code

## Problem
CI installs `dtolnay/rust-toolchain@stable` and runs clippy with `-D warnings`. The repo has
no `rust-toolchain.toml`. When a new stable release adds or tightens a clippy lint, CI goes red
on code that did not change. Locally the owner has 1.99.1 (measured 2026-11-01), so local and
CI results can also differ.

## Why it matters
A red that nobody caused costs time and teaches people to ignore red. It also works against
the project's aim of reproducible builds.

## Options
1. Add `rust-toolchain.toml` pinning a version, with rustfmt and clippy components, and bump
   it on purpose in its own change. Recommended.
2. Keep `stable` and accept the occasional surprise.

## Related
`PROJECT.md` stack row "Build: Docker image for reproducible builds".
