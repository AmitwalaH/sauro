"""Check that every evidence_span in bench/fixtures appears verbatim in a stored page.

This is the rule in bench/LABELING.md, "Quality rules": every supported, partial and
contradicted label has a non-null evidence_span that appears verbatim in the stored page.

Usage: python3 bench/tools/check_fixtures.py [fixtures_dir] [--require-pages]
Exit 0 when nothing failed, 1 otherwise. Reads only. Never writes a fixture.

Stored pages are not in git (owner decision Q25), so a clone, and CI, has the fixture JSON
and no pages. A page listed in `sources` but absent from disk is counted, not failed: its
hash check is skipped, and so is a span check that could only pass on that page. A span
found in another cited page that is present still counts as checked. Every check that needs
no page still runs. `--require-pages` makes each absent page a failure; the labeler runs it
before committing a fixture. A page that is present is checked in full either way.

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

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
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


@dataclass
class Counts:
    claims: int = 0
    unlabeled: int = 0
    spans: int = 0
    hashes: int = 0
    absent: int = 0  # pages listed in sources but not on disk
    unchecked: int = 0  # spans that could only be checked on an absent page

    def add(self, other):
        for name in vars(self):
            setattr(self, name, getattr(self, name) + getattr(other, name))


def where(file):
    """A stored page's name as the failure lines show it, such as 0001.sources/2.html."""
    return f"{file.parent.name}/{file.name}"


def check_fixture(path, require_pages=False):
    """Check one fixture. Return a Counts and the failure lines."""
    counts = Counts()
    try:
        fixture = json.loads(path.read_text(encoding="utf-8"))
        claims = fixture["claims"]
        files = source_files(fixture, path)
    except (ValueError, KeyError, TypeError) as e:
        return counts, [f"{path.name}: cannot read fixture: {e}"]

    pages = {}  # file path to squashed text, so each page is parsed once
    failures = []
    counts.claims = len(claims)

    for s in fixture["sources"]:
        stored = path.with_suffix(".sources") / s["file"]
        if not stored.is_file():
            counts.absent += 1
            if require_pages:
                failures.append(f"{path.name}: stored page missing: {where(stored)}")
            continue
        if "sha256" not in s:
            continue
        if hashlib.sha256(stored.read_bytes()).hexdigest() != s["sha256"]:
            failures.append(f"{path.name}: {where(stored)} does not match its sha256, "
                            "so it changed after it was fetched")
        else:
            counts.hashes += 1

    for c in claims:
        cid = c.get("claim_id", f"{path.stem}-?")
        label = c.get("label")
        span = c.get("evidence_span")

        if label is None:
            counts.unlabeled += 1
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

        counts.spans += 1
        urls = c.get("cited_urls") or []
        if not urls:
            failures.append(f"{cid}: has an evidence_span but no cited URL")
            continue
        unlisted = [u for u in urls if u not in files]
        if unlisted:
            failures.append(f"{cid}: cited URL not in sources: {unlisted[0]}")
            continue
        present = [files[u] for u in urls if files[u].is_file()]
        missing = [files[u] for u in urls if not files[u].is_file()]
        for f in present:
            if f not in pages:
                html = f.read_text(encoding="utf-8", errors="replace")
                pages[f] = squash(page_text(html))
        if any(squash(span) in pages[f] for f in present):
            continue
        if not missing:
            failures.append(f"{cid}: evidence_span not found in its cited page")
        elif require_pages:
            failures.append(f"{cid}: stored page missing: {where(missing[0])}")
        else:
            # The span may be on the absent page, so this is no evidence either way.
            counts.unchecked += 1

    return counts, failures


def main(argv):
    default = Path(__file__).resolve().parent.parent / "fixtures"
    parser = argparse.ArgumentParser(description="Check fixture labels and evidence spans.")
    parser.add_argument("fixtures_dir", nargs="?", type=Path, default=default)
    parser.add_argument("--require-pages", action="store_true",
                        help="fail on any stored page that is absent; run before a fixture commit")
    args = parser.parse_args(argv[1:])
    files = sorted(args.fixtures_dir.glob("*.json"))

    total = Counts()
    failures = []
    for path in files:
        counts, fails = check_fixture(path, args.require_pages)
        total.add(counts)
        failures.extend(fails)

    for line in failures:
        print(f"FAIL {line}")
    # The counts are printed so a run that found nothing cannot be mistaken for a pass, and
    # so a run that could not see the pages says how much it did not check.
    print(
        f"checked {len(files)} fixtures, {total.claims} claims, {total.unlabeled} unlabeled, "
        f"{total.spans} spans, {total.hashes} hashes, {total.absent} pages absent, "
        f"{total.unchecked} spans unchecked in {args.fixtures_dir}: {len(failures)} failures"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
