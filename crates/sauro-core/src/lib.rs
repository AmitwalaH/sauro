//! sauro-core: the deterministic engine behind sauro.
//!
//! Given a sentence written by a model and the page it cites, the engine will find the
//! matching span in the page and report one of four states: Supported, Partial,
//! Contradicted, Unverifiable. It always returns the span it matched, and it never calls
//! an LLM, so the same input gives the same output every time.
//!
//! Nothing is implemented yet. The benchmark comes first. See `SCOPE.md` and
//! `bench/LABELING.md` in the repository.
