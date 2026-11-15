"""Tests for check_fixtures.py. Each test builds a fixtures dir and runs the script on it.

Run from the repo root: python3 -m unittest bench/tools/test_check_fixtures.py
"""

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "check_fixtures.py"

URL_A = "https://example.org/a"
URL_B = "https://example.org/b"

PAGE = """<html><head><title>T</title>
<script>var secret = "only in a script tag";</script>
<style>.x { content: "only in a style tag"; }</style></head>
<body><nav>Home</nav>
<article>
<p>Ibuprofen can raise blood pressure in <em>some</em> patients, according to
the <a href="/x">study</a>, and the effect is &ldquo;small&rdquo; &amp; reversible.</p>
<p>Most people
do not notice it.</p>
</article></body></html>"""

OTHER_PAGE = "<p>Something else entirely.</p>"


def claim(cid, label, span, reason="exact", urls=(URL_A,)):
    return {
        "claim_id": cid,
        "text": "x",
        "cited_urls": list(urls),
        "label": label,
        "reason_code": reason,
        "evidence_span": span,
        "evidence_location": None,
        "labeler_note": "x",
        "hard": False,
    }


class CheckFixtures(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def add(self, fid, claims, pages=None, sources=None, reviewed=False, hashed=False):
        """Write a fixture. pages maps url to html; each is stored and listed in sources.

        hashed adds a sha256 of each stored file, as fetch_sources.py writes it.
        """
        pages = {URL_A: PAGE} if pages is None else pages
        src_dir = self.dir / f"{fid}.sources"
        listed = []
        for i, (url, html) in enumerate(pages.items()):
            name = f"page{i}.html"
            src_dir.mkdir(exist_ok=True)
            (src_dir / name).write_bytes(html.encode("utf-8"))
            listed.append({"url": url, "file": name, "fetched_on": "2026-11-01"})
            if hashed:
                listed[-1]["sha256"] = hashlib.sha256(html.encode("utf-8")).hexdigest()
        fixture = {
            "id": fid,
            "source_model": "claude",
            "domain": "health",
            "collected_on": "2026-11-01",
            "answer_text": "x",
            "sources": listed if sources is None else sources,
            "claims": claims,
            "reviewed": reviewed,
        }
        (self.dir / f"{fid}.json").write_text(json.dumps(fixture), encoding="utf-8")

    def run_script(self, *flags):
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(self.dir), *flags], capture_output=True, text=True
        )

    def assert_passes(self, *flags):
        r = self.run_script(*flags)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r

    def assert_fails_naming(self, needle, *flags):
        r = self.run_script(*flags)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn(needle, r.stdout)

    def remove_page(self, fid, name):
        """What a clone looks like under Q25: the JSON is there, the stored page is not."""
        (self.dir / f"{fid}.sources" / name).unlink()

    # What "verbatim" means: rendered text, whitespace ignored.

    def test_span_as_seen_in_browser_passes(self):
        # Crosses inline tags, two entities, and a line break inside the HTML.
        self.add("0001", [
            claim("0001-01", "supported",
                  "Ibuprofen can raise blood pressure in some patients, according to the study,"
                  " and the effect is “small” & reversible."),
            claim("0001-02", "partial", "Most people do not notice it.", "hedge_dropped"),
        ])
        r = self.assert_passes()
        self.assertIn("1 fixtures", r.stdout)
        self.assertIn("2 spans", r.stdout)

    def test_span_spanning_two_paragraphs_passes(self):
        self.add("0001", [claim("0001-01", "supported", "& reversible. Most people do not")])
        self.assert_passes()

    def test_span_not_in_page_fails(self):
        self.add("0001", [claim("0001-01", "supported", "Ibuprofen always raises blood pressure.")])
        self.assert_fails_naming("0001-01")

    def test_one_changed_word_fails(self):
        self.add("0001", [claim("0001-01", "contradicted", "Most people do notice it.", "negated")])
        self.assert_fails_naming("0001-01")

    def test_span_only_in_script_or_style_fails(self):
        self.add("0001", [
            claim("0001-01", "supported", "only in a script tag"),
            claim("0001-02", "supported", "only in a style tag"),
        ])
        r = self.run_script()
        self.assertEqual(r.returncode, 1)
        self.assertIn("0001-01", r.stdout)
        self.assertIn("0001-02", r.stdout)

    # Which labels need a span.

    def test_supported_without_span_fails(self):
        self.add("0001", [claim("0001-01", "supported", None)])
        self.assert_fails_naming("0001-01")

    def test_empty_span_fails(self):
        self.add("0001", [claim("0001-01", "partial", "   ")])
        self.assert_fails_naming("0001-01")

    def test_unknown_label_fails(self):
        # A typo must not skip the span check.
        self.add("0001", [claim("0001-01", "Supported", "not in the page at all")])
        self.assert_fails_naming("0001-01")

    def test_unverifiable_without_span_passes(self):
        self.add("0001", [claim("0001-01", "unverifiable", None, "no_citation", urls=())])
        self.assert_passes()

    def test_unverifiable_with_unstored_url_passes(self):
        # A 404 has no stored page, so its URL need not resolve to a file.
        self.add("0001", [claim("0001-01", "unverifiable", None, "fetch_failed", urls=(URL_B,))])
        self.assert_passes()

    # label: null means "not yet labeled". It is counted, not failed, until the fixture is
    # reviewed.

    def test_unlabeled_claim_passes_and_is_counted(self):
        self.add("0001", [
            claim("0001-01", None, None, None),
            claim("0001-02", None, None, None),
            claim("0001-03", "supported", "Most people do not notice it."),
        ])
        r = self.assert_passes()
        self.assertIn("3 claims, 2 unlabeled, 1 spans", r.stdout)

    def test_unlabeled_claim_is_not_span_checked(self):
        # A labeler may paste a span before choosing a label. No label, no check yet.
        self.add("0001", [claim("0001-01", None, "not in the page at all", None)])
        r = self.assert_passes()
        self.assertIn("1 unlabeled, 0 spans", r.stdout)

    def test_labeled_bad_span_still_fails_beside_unlabeled(self):
        self.add("0001", [
            claim("0001-01", None, None, None),
            claim("0001-02", "supported", "Ibuprofen always raises blood pressure."),
        ])
        r = self.run_script()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("0001-02", r.stdout)
        self.assertNotIn("0001-01", r.stdout)
        self.assertIn("1 unlabeled", r.stdout)

    def test_unlabeled_claim_in_reviewed_fixture_fails(self):
        # A reviewed fixture is frozen, so it cannot be half-labeled.
        self.add("0001", [
            claim("0001-01", "supported", "Most people do not notice it."),
            claim("0001-02", None, None, None),
        ], reviewed=True)
        self.assert_fails_naming("0001-02: label is null in a reviewed fixture")

    # A stored page must still be the bytes that were fetched, when sources records a sha256.

    def test_matching_sha256_passes_and_is_counted(self):
        self.add("0001", [claim("0001-01", "supported", "Most people do not notice it.")],
                 pages={URL_A: PAGE, URL_B: OTHER_PAGE}, hashed=True)
        r = self.assert_passes()
        self.assertIn("1 spans, 2 hashes", r.stdout)

    def test_page_changed_after_fetch_fails_naming_the_file(self):
        self.add("0001", [claim("0001-01", "supported", "Most people do not notice it.")],
                 pages={URL_A: PAGE, URL_B: OTHER_PAGE}, hashed=True)
        # An editor reformats the second page. Its text, and so every span, is unchanged.
        page = self.dir / "0001.sources" / "page1.html"
        page.write_bytes(b"\xef\xbb\xbf" + page.read_bytes().replace(b"<p>", b"<p>\n  "))
        self.assert_fails_naming(
            "0001.json: 0001.sources/page1.html does not match its sha256")

    def test_line_ending_rewrite_fails(self):
        # What git does with text=auto eol=lf to a page served with CRLF line endings.
        crlf = PAGE.replace("\n", "\r\n")
        self.add("0001", [claim("0001-01", "unverifiable", None, "not_in_source")],
                 pages={URL_A: crlf}, hashed=True)
        page = self.dir / "0001.sources" / "page0.html"
        page.write_bytes(page.read_bytes().replace(b"\r\n", b"\n"))
        self.assert_fails_naming("0001.sources/page0.html does not match its sha256")

    def test_hash_is_checked_on_pages_no_claim_cites(self):
        self.add("0001", [claim("0001-01", None, None, None)], hashed=True)
        (self.dir / "0001.sources" / "page0.html").write_text("changed", encoding="utf-8")
        self.assert_fails_naming("0001.sources/page0.html does not match its sha256")

    def test_hashed_page_missing_on_disk_fails(self):
        # Under Q25 a missing page fails only when the labeler asks for every page.
        self.add("0001", [claim("0001-01", None, None, None)], hashed=True)
        (self.dir / "0001.sources" / "page0.html").unlink()
        self.assert_fails_naming("0001.json: stored page missing: 0001.sources/page0.html",
                                 "--require-pages")

    def test_source_without_sha256_is_not_hash_checked(self):
        # The guide's sources shape has no sha256, so a hand-made entry is still valid.
        self.add("0001", [claim("0001-01", "supported", "Most people do not notice it.")])
        r = self.assert_passes()
        self.assertIn("0 hashes", r.stdout)

    # A span is checked against the claim's own cited page, through the sources list.

    def test_span_in_other_page_of_same_fixture_fails(self):
        self.add("0001", [claim("0001-01", "supported", "Most people do not notice it.",
                                urls=(URL_B,))],
                 pages={URL_A: PAGE, URL_B: OTHER_PAGE})
        self.assert_fails_naming("0001-01")

    def test_span_in_second_cited_page_passes(self):
        self.add("0001", [claim("0001-01", "supported", "Most people do not notice it.",
                                urls=(URL_B, URL_A))],
                 pages={URL_A: PAGE, URL_B: OTHER_PAGE})
        self.assert_passes()

    def test_cited_url_missing_from_sources_fails(self):
        self.add("0001", [claim("0001-01", "supported", "Most people do not notice it.",
                                urls=(URL_B,))])
        self.assert_fails_naming("0001-01")

    def test_span_without_cited_url_fails(self):
        self.add("0001", [claim("0001-01", "supported", "Most people do not notice it.", urls=())])
        self.assert_fails_naming("0001-01: has an evidence_span but no cited URL")

    def test_listed_file_missing_on_disk_fails(self):
        # Under Q25 a missing page fails only when the labeler asks for every page.
        self.add("0001", [claim("0001-01", "supported", "Most people do not notice it.")],
                 sources=[{"url": URL_A, "file": "gone.html", "fetched_on": "2026-11-01"}])
        self.assert_fails_naming("0001-01", "--require-pages")

    def test_missing_sources_list_fails_naming_file(self):
        self.add("0001", [claim("0001-01", "supported", "Most people do not notice it.")])
        path = self.dir / "0001.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        del data["sources"]
        path.write_text(json.dumps(data), encoding="utf-8")
        self.assert_fails_naming("0001.json")

    def test_span_from_other_fixture_page_fails(self):
        self.add("0001", [claim("0001-01", "supported", "Most people do not notice it.")])
        self.add("0002", [claim("0002-01", "supported", "Most people do not notice it.")],
                 pages={URL_A: OTHER_PAGE})
        self.assert_fails_naming("0002-01")

    # Pages absent from disk (Q25: stored pages are not in git, so CI has none of them).

    def test_all_pages_present_counts_zero_absent(self):
        self.add("0001", [claim("0001-01", "supported", "Most people do not notice it.")],
                 hashed=True)
        r = self.assert_passes()
        self.assertIn("1 spans, 1 hashes, 0 pages absent, 0 spans unchecked", r.stdout)

    def test_absent_page_is_counted_not_failed(self):
        self.add("0001", [claim("0001-01", "supported", "Most people do not notice it.")],
                 hashed=True)
        self.remove_page("0001", "page0.html")
        r = self.assert_passes()
        self.assertIn("1 spans, 0 hashes, 1 pages absent, 1 spans unchecked", r.stdout)
        self.assertNotIn("FAIL", r.stdout)

    def test_require_pages_fails_on_an_absent_page_nothing_cites(self):
        # No sha256 and no claim cites it, so only the flag can notice it is gone.
        self.add("0001", [claim("0001-01", "supported", "Most people do not notice it.")],
                 pages={URL_A: PAGE, URL_B: OTHER_PAGE})
        self.remove_page("0001", "page1.html")
        self.assert_passes()
        self.assert_fails_naming("0001.json: stored page missing: 0001.sources/page1.html",
                                 "--require-pages")

    def test_require_pages_passes_when_every_page_is_there(self):
        self.add("0001", [claim("0001-01", "supported", "Most people do not notice it.")],
                 hashed=True)
        r = self.assert_passes("--require-pages")
        self.assertIn("1 hashes, 0 pages absent, 0 spans unchecked", r.stdout)

    def test_span_found_in_present_page_is_checked_beside_an_absent_one(self):
        # A wrong fix that skips the claim whenever any cited page is absent says "1 unchecked".
        self.add("0001", [claim("0001-01", "supported", "Most people do not notice it.",
                                urls=(URL_A, URL_B))],
                 pages={URL_A: PAGE, URL_B: OTHER_PAGE})
        self.remove_page("0001", "page1.html")
        r = self.assert_passes()
        self.assertIn("1 pages absent, 0 spans unchecked", r.stdout)

    def test_span_not_in_present_page_is_unchecked_when_another_cited_page_is_absent(self):
        # The span may be on the absent page, so this is not evidence of a wrong span.
        self.add("0001", [claim("0001-01", "supported", "Most people do not notice it.",
                                urls=(URL_B, URL_A))],
                 pages={URL_A: PAGE, URL_B: OTHER_PAGE})
        self.remove_page("0001", "page0.html")
        r = self.assert_passes()
        self.assertIn("1 pages absent, 1 spans unchecked", r.stdout)

    def test_span_not_in_its_only_present_page_still_fails_beside_absent_pages(self):
        # Another claim's absent page must not switch off the check for this one.
        self.add("0001", [claim("0001-01", "supported", "Most people do not notice it.",
                                urls=(URL_B,)),
                          claim("0001-02", "supported", "Most people do not notice it.")],
                 pages={URL_A: PAGE, URL_B: OTHER_PAGE})
        self.remove_page("0001", "page0.html")
        self.assert_fails_naming("0001-01: evidence_span not found in its cited page")

    def test_present_page_is_hash_checked_beside_an_absent_one(self):
        self.add("0001", [claim("0001-01", None, None, None)],
                 pages={URL_A: PAGE, URL_B: OTHER_PAGE}, hashed=True)
        self.remove_page("0001", "page0.html")
        (self.dir / "0001.sources" / "page1.html").write_text("changed", encoding="utf-8")
        self.assert_fails_naming("0001.sources/page1.html does not match its sha256")

    def test_require_pages_fails_a_span_whose_cited_page_is_absent(self):
        self.add("0001", [claim("0001-01", "supported", "Most people do not notice it.")],
                 hashed=True)
        self.remove_page("0001", "page0.html")
        self.assert_fails_naming("0001-01: stored page missing: 0001.sources/page0.html",
                                 "--require-pages")

    # Checks that need no page still run when every page is absent, as on CI.

    def check_without_pages(self, claims, needle, reviewed=False):
        self.add("0001", claims, reviewed=reviewed, hashed=True)
        self.remove_page("0001", "page0.html")
        self.assert_fails_naming(needle)

    def test_unknown_label_fails_without_pages(self):
        self.check_without_pages([claim("0001-01", "true", "Most people do not notice it.")],
                                 "0001-01: unknown label 'true'")

    def test_missing_span_fails_without_pages(self):
        self.check_without_pages([claim("0001-01", "partial", None)],
                                 "0001-01: label partial needs an evidence_span")

    def test_cited_url_not_in_sources_fails_without_pages(self):
        self.check_without_pages(
            [claim("0001-01", "supported", "Most people do not notice it.", urls=(URL_B,))],
            "0001-01: cited URL not in sources")

    def test_null_label_in_reviewed_fixture_fails_without_pages(self):
        self.check_without_pages([claim("0001-01", None, None, None)],
                                 "0001-01: label is null in a reviewed fixture", reviewed=True)

    # The script itself.

    def test_bad_json_fails_naming_file(self):
        (self.dir / "0003.json").write_text("{not json", encoding="utf-8")
        self.assert_fails_naming("0003.json")

    def test_empty_dir_says_zero(self):
        r = self.assert_passes()
        self.assertIn("0 fixtures", r.stdout)

    def test_does_not_modify_fixtures(self):
        self.add("0001", [claim("0001-01", "supported", "not in page")])
        before = (self.dir / "0001.json").read_bytes()
        self.run_script()
        self.assertEqual((self.dir / "0001.json").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
