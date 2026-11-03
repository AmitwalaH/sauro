"""Check that every evidence_span in bench/fixtures appears verbatim in a stored page.

This is the rule in bench/LABELING.md, "Quality rules": every supported, partial and
contradicted label has a non-null evidence_span that appears verbatim in the stored page.

Usage: python3 bench/tools/check_fixtures.py [fixtures_dir]
Exit 0 when every span is found, 1 otherwise. Reads only. Never writes a fixture.

What "verbatim" means here, because a labeler copies from the page as a browser shows it:
- The page is compared as text: tags removed, entities decoded, script and style dropped.
- All whitespace is ignored on both sides, so line breaks in the HTML, inline tags and
  paragraph breaks do not matter. Every other character must match exactly.

A span is checked against the claim's own cited pages only. Each cited URL resolves to a
stored file through the fixture's `sources` list, and every one must resolve.

A claim with `label: null` is not yet labeled. It is counted and not checked, so a
half-labeled fixture set still passes. A null label in a fixture marked reviewed fails.

A `sources` entry with a `sha256` must still match its stored file byte for byte, whether or
not a claim cites it. An editor or git can rewrite a page without changing its text, and
then the stored page is no longer what was fetched.
"""

import hashlib
import json
import sys
from html.parser import HTMLParser
from pathlib import Path

LABELS = {"supported", "partial", "contradicted", "unverifiable"}
NEEDS_SPAN = {"supported", "partial", "contradicted"}

# Text inside these is never shown to a reader, so a span found only there is not evidence.
HIDDEN_TAGS = {"script", "style"}


class _TextCollector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.hidden_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in HIDDEN_TAGS:
            self.hidden_depth += 1

    def handle_endtag(self, tag):
        if tag in HIDDEN_TAGS and self.hidden_depth:
            self.hidden_depth -= 1

    def handle_data(self, data):
        if not self.hidden_depth:
            self.parts.append(data)


def page_text(html):
    """The text a reader sees in the page, before whitespace is removed."""
    collector = _TextCollector()
    collector.feed(html)
    collector.close()
    return "".join(collector.parts)


def squash(text):
    """Remove all whitespace, so spans compare on their characters only."""
    return "".join(text.split())


def source_files(fixture, fixture_path):
    """Map each URL in the fixture's sources list to its stored page file."""
    sources_dir = fixture_path.with_suffix(".sources")
    return {s["url"]: sources_dir / s["file"] for s in fixture["sources"]}


def check_fixture(path):
    """Return (claims, unlabeled claims, spans, hashes checked, failure lines) for one fixture."""
    try:
        fixture = json.loads(path.read_text(encoding="utf-8"))
        claims = fixture["claims"]
        files = source_files(fixture, path)
    except (ValueError, KeyError, TypeError) as e:
        return 0, 0, 0, 0, [f"{path.name}: cannot read fixture: {e}"]

    pages = {}  # file path to squashed text, so each page is parsed once
    failures = []
    spans = unlabeled = hashes = 0

    for s in fixture["sources"]:
        if "sha256" not in s:
            continue
        stored = path.with_suffix(".sources") / s["file"]
        where = f"{stored.parent.name}/{stored.name}"
        if not stored.is_file():
            failures.append(f"{path.name}: stored page missing: {where}")
        elif hashlib.sha256(stored.read_bytes()).hexdigest() != s["sha256"]:
            failures.append(f"{path.name}: {where} does not match its sha256, "
                            "so it changed after it was fetched")
        else:
            hashes += 1

    for c in claims:
        cid = c.get("claim_id", f"{path.stem}-?")
        label = c.get("label")
        span = c.get("evidence_span")

        if label is None:
            unlabeled += 1
            if fixture.get("reviewed") is True:
                failures.append(f"{cid}: label is null in a reviewed fixture")
            continue
        if label not in LABELS:
            failures.append(f"{cid}: unknown label {label!r}")
            continue
        if span is None:
            if label in NEEDS_SPAN:
                failures.append(f"{cid}: label {label} needs an evidence_span")
            continue
        if not squash(span):
            failures.append(f"{cid}: evidence_span is empty")
            continue

        spans += 1
        urls = c.get("cited_urls") or []
        if not urls:
            failures.append(f"{cid}: has an evidence_span but no cited URL")
            continue
        unlisted = [u for u in urls if u not in files]
        if unlisted:
            failures.append(f"{cid}: cited URL not in sources: {unlisted[0]}")
            continue
        missing = [files[u] for u in urls if not files[u].is_file()]
        if missing:
            where = f"{missing[0].parent.name}/{missing[0].name}"
            failures.append(f"{cid}: stored page missing: {where}")
            continue
        for u in urls:
            if files[u] not in pages:
                html = files[u].read_text(encoding="utf-8", errors="replace")
                pages[files[u]] = squash(page_text(html))
        if not any(squash(span) in pages[files[u]] for u in urls):
            failures.append(f"{cid}: evidence_span not found in its cited page")

    return len(claims), unlabeled, spans, hashes, failures


def main(argv):
    default = Path(__file__).resolve().parent.parent / "fixtures"
    fixtures_dir = Path(argv[1]) if len(argv) > 1 else default
    files = sorted(fixtures_dir.glob("*.json"))

    total_claims = total_unlabeled = total_spans = total_hashes = 0
    failures = []
    for path in files:
        n_claims, n_unlabeled, n_spans, n_hashes, fails = check_fixture(path)
        total_claims += n_claims
        total_unlabeled += n_unlabeled
        total_spans += n_spans
        total_hashes += n_hashes
        failures.extend(fails)

    for line in failures:
        print(f"FAIL {line}")
    # The counts are printed so a run that found nothing cannot be mistaken for a pass.
    print(
        f"checked {len(files)} fixtures, {total_claims} claims, {total_unlabeled} unlabeled, "
        f"{total_spans} spans, {total_hashes} hashes "
        f"in {fixtures_dir}: {len(failures)} failures"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
