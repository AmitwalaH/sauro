# sauro

Deterministic citation checker for AI answers.

Give sauro a sentence an AI wrote and the page it cited. sauro fetches the page, finds the
closest matching span, and reports one of four states, always with the evidence it matched:

| State | Meaning |
|---|---|
| Supported | The page says this, with the same strength |
| Partial | The page says something close, but the claim overstates, narrows, or shifts it |
| Contradicted | The page says the opposite, or gives a conflicting number |
| Unverifiable | sauro could not get or read the page, or the claim has no citation |

sauro checks whether the source says it. It does not judge whether the source is right. It
never reports a verdict it cannot show evidence for. No LLM runs inside the core, so the same
input gives the same output every time.

**Status: not usable yet.** The first task is the benchmark, not the engine. See
[`SCOPE.md`](SCOPE.md) for what sauro will and
will not do.

## Planned surfaces

- A Rust library, `sauro-core`
- A CLI, `sauro`, as a single static binary
- An MCP server and a skill, so Claude Code and similar agents can check their own citations
- A GitHub Action that fails a pull request on a citation that rots or contradicts

## How this repo works

Where the project stands is in
[`PROJECT.md`](PROJECT.md). Findings go in [`tickets/`](tickets/). The labeling guide that
every benchmark fixture follows is [`bench/LABELING.md`](bench/LABELING.md).

## Contributing and security

See [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`SECURITY.md`](SECURITY.md). sauro is licensed
under the [Apache License 2.0](LICENSE).
