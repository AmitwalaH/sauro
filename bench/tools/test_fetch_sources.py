"""Tests for fetch_sources.py. Each test writes an answer.md and runs the script on it.

Run from the repo root: python3 -m unittest bench/tools/test_fetch_sources.py

No test fetches a real URL. Pages come from a local http.server on 127.0.0.1, so the real
urllib path runs: statuses, redirects, timeouts. Only the DNS failure is mocked, because a
real lookup would leave the machine.
"""

import contextlib
import hashlib
import io
import json
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import fetch_sources  # noqa: E402

ARTICLE = (
    "<html><head><title>Ibuprofen</title></head><body><article>"
    "<p>Ibuprofen can raise blood pressure in some patients.</p>"
    + "<p>Most people do not notice it, and the effect is small and reversible.</p>" * 10
    + "</article></body></html>"
).encode()

OTHER = ARTICLE.replace(b"Ibuprofen can", b"Paracetamol can")

JS_ONLY = (
    "<html><head><script>" + "var x = 1;" * 80 + "</script></head>"
    "<body><div id=app></div></body></html>"
).encode()

PDF = b"%PDF-1.4\n" + b"0" * 800

HEADER = """model: claude
domain: health
asked_on: 2026-11-03
question: Is it safe?
---
"""


class Server:
    """A local web server. routes maps a path to (status, content type, body, extra headers)."""

    def __init__(self):
        self.routes = {}
        self.hits = {}
        self.agents = []
        self.delay = {}
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                outer.hits[self.path] = outer.hits.get(self.path, 0) + 1
                outer.agents.append(self.headers.get("User-Agent"))
                time.sleep(outer.delay.get(self.path, 0))
                status, ctype, body, extra = outer.routes.get(
                    self.path, (404, "text/html", b"<p>no such page</p>", {}))
                try:
                    self.send_response(status)
                    self.send_header("Content-Type", ctype)
                    self.send_header("Content-Length", str(len(body)))
                    for k, v in extra.items():
                        self.send_header(k, v)
                    self.end_headers()
                    self.wfile.write(body)
                except (BrokenPipeError, ConnectionResetError):
                    pass  # the client gave up, as in the timeout test

            def log_message(self, *args):
                pass

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.base = f"http://127.0.0.1:{self.httpd.server_address[1]}"
        threading.Thread(target=self.httpd.serve_forever, args=(0.01,), daemon=True).start()

    def page(self, path, body=ARTICLE, status=200, ctype="text/html; charset=utf-8", **extra):
        self.routes[path] = (status, ctype, body, extra)
        return self.base + path

    def stop(self):
        self.httpd.shutdown()
        self.httpd.server_close()


class FetchSourcesBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.fixtures = Path(self.tmp.name)
        self.src = self.fixtures / "0001.sources"
        self.src.mkdir()
        self.server = Server()

    def tearDown(self):
        self.server.stop()
        self.tmp.cleanup()

    def write_answer(self, body, header=HEADER):
        (self.src / "answer.md").write_text(header + body, encoding="utf-8")

    def run_script(self):
        """Run main() in this process, so constants can be patched. Returns (code, output)."""
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = fetch_sources.main(["fetch_sources.py", str(self.src)])
        return code, out.getvalue()

    def fixture(self):
        return json.loads((self.fixtures / "0001.json").read_text(encoding="utf-8"))

    def run_ok(self):
        code, out = self.run_script()
        self.assertEqual(code, 0, out)
        return self.fixture(), out

    def texts(self, fx):
        return [c["text"] for c in fx["claims"]]

    def urls_by_text(self, fx):
        return {c["text"]: c["cited_urls"] for c in fx["claims"]}


class Skeletons(FetchSourcesBase):
    def test_one_null_skeleton_per_sentence_with_every_guide_field(self):
        self.write_answer("Ibuprofen is an NSAID. It is sold as Advil.\n\nIs it safe? Mostly.\n")
        fx, _ = self.run_ok()
        self.assertEqual(self.texts(fx),
                         ["Ibuprofen is an NSAID.", "It is sold as Advil.", "Is it safe?", "Mostly."])
        self.assertEqual([c["claim_id"] for c in fx["claims"]],
                         ["0001-01", "0001-02", "0001-03", "0001-04"])
        for c in fx["claims"]:
            self.assertEqual(c, {
                "claim_id": c["claim_id"], "text": c["text"], "cited_urls": [],
                "label": None, "reason_code": None, "evidence_span": None,
                "evidence_location": None, "labeler_note": None, "hard": False,
            })

    def test_split_rule_is_the_crude_one(self):
        # Splits on ". ", "? ", "! " before a capital, and on every line break. Nothing else.
        self.write_answer(
            "Doses vary, e.g. in older adults. Ask first!\n"
            "What are the risks?\n"
            "Heading without a full stop\n"
            "- Take it with food.\n"
            "It costs 3.5 dollars. done.\n")
        fx, _ = self.run_ok()
        self.assertEqual(self.texts(fx), [
            "Doses vary, e.g. in older adults.", "Ask first!", "What are the risks?",
            "Heading without a full stop", "- Take it with food.", "It costs 3.5 dollars. done.",
        ])

    def test_header_maps_to_fixture_fields_and_question_stays_in_answer_md(self):
        body = "Ibuprofen is an NSAID.\n\nsources shown:\n"
        self.write_answer(body, header=HEADER.replace("model: claude", "model: gpt"))
        fx, _ = self.run_ok()
        self.assertEqual(fx["id"], "0001")
        self.assertEqual(fx["source_model"], "gpt")
        self.assertEqual(fx["domain"], "health")
        self.assertEqual(fx["collected_on"], "2026-11-03")
        self.assertEqual(fx["answer_text"], body)
        self.assertIs(fx["reviewed"], False)
        self.assertNotIn("question", fx)
        self.assertEqual(list(fx), ["id", "source_model", "domain", "collected_on", "answer_text",
                                    "sources", "fetch_failures", "claims", "reviewed"])

    def test_empty_answer_writes_nothing(self):
        self.write_answer("\n")
        code, out = self.run_script()
        self.assertEqual(code, 1)
        self.assertIn("answer is empty", out)
        self.assertFalse((self.fixtures / "0001.json").exists())

    def test_missing_header_field_writes_nothing(self):
        self.write_answer("Ibuprofen is an NSAID.\n", header=HEADER.replace("domain: health\n", ""))
        code, out = self.run_script()
        self.assertEqual(code, 1)
        self.assertIn("domain", out)
        self.assertFalse((self.fixtures / "0001.json").exists())

    def test_missing_separator_writes_nothing(self):
        self.write_answer("Ibuprofen is an NSAID.\n", header=HEADER.replace("---\n", ""))
        code, out = self.run_script()
        self.assertEqual(code, 1)
        self.assertIn("---", out)
        self.assertFalse((self.fixtures / "0001.json").exists())


class Urls(FetchSourcesBase):
    def test_trimming_rule(self):
        cases = {
            "see ([nhs.uk](https://www.nhs.uk/medicines/ibuprofen/)).":
                ["https://www.nhs.uk/medicines/ibuprofen/"],
            "See https://en.wikipedia.org/wiki/Ibuprofen_(drug).":
                ["https://en.wikipedia.org/wiki/Ibuprofen_(drug)"],
            "kidneys (https://example.org/kidney?x=1&y=2).": ["https://example.org/kidney?x=1&y=2"],
            'quoted "https://example.org/q" and <https://example.org/a>, then':
                ["https://example.org/q", "https://example.org/a"],
            "twice https://example.org/a and https://example.org/a!": ["https://example.org/a"],
            "no url here": [],
        }
        for text, want in cases.items():
            with self.subTest(text=text):
                self.assertEqual(fetch_sources.extract_urls(text), want)

    def test_inline_url_attaches_to_its_own_sentence(self):
        a = self.server.page("/a")
        self.write_answer(f"Ibuprofen raises blood pressure ([nhs.uk]({a})). It is an NSAID.\n")
        fx, _ = self.run_ok()
        self.assertEqual(self.urls_by_text(fx), {
            f"Ibuprofen raises blood pressure ([nhs.uk]({a})).": [a],
            "It is an NSAID.": [],
        })

    def test_chip_lines_are_not_claims_and_block_urls_go_to_sentence_before_chip(self):
        a, b = self.server.page("/a"), self.server.page("/b", OTHER)
        self.write_answer(
            "Ibuprofen is an NSAID.\n\nIt can raise blood pressure.\n\nnhs.uk\n+2\n\n"
            f"Tell me your medicine.\n\nsources shown:\n{a}\n{b}\n")
        fx, out = self.run_ok()
        self.assertEqual(self.urls_by_text(fx), {
            "Ibuprofen is an NSAID.": [],
            "It can raise blood pressure.": [a, b],
            "Tell me your medicine.": [],
        })
        self.assertNotIn("warning", out)

    def test_chip_count_after_a_blank_line_and_number_lines_are_not_chips(self):
        a = self.server.page("/a")
        self.write_answer(f"It can raise it.\nnhs.uk\n\n+2\n3.5\nAsk.\n\nsources shown:\n{a}\n")
        fx, _ = self.run_ok()
        self.assertEqual(self.urls_by_text(fx), {"It can raise it.": [a], "3.5": [], "Ask.": []})

    def test_chip_without_plus_count(self):
        a = self.server.page("/a")
        self.write_answer(f"It can raise blood pressure.\nnhs.uk\nAsk a doctor.\n\nsources shown:\n{a}\n")
        fx, _ = self.run_ok()
        self.assertEqual(self.urls_by_text(fx),
                         {"It can raise blood pressure.": [a], "Ask a doctor.": []})

    def test_no_chip_attaches_block_to_last_claim(self):
        a = self.server.page("/a")
        self.write_answer(f"First point.\n\nLast point.\n\nsources shown:\n{a}\n")
        fx, _ = self.run_ok()
        self.assertEqual(self.urls_by_text(fx), {"First point.": [], "Last point.": [a]})

    def test_two_chips_attach_every_block_url_to_both_and_warn(self):
        a, b = self.server.page("/a"), self.server.page("/b", OTHER)
        self.write_answer(
            f"First point.\nnhs.uk\n+1\nSecond point.\nkidney.org\nThird point.\n\n"
            f"sources shown:\n{a}\n{b}\n")
        fx, out = self.run_ok()
        self.assertEqual(self.urls_by_text(fx), {
            "First point.": [a, b], "Second point.": [a, b], "Third point.": []})
        self.assertIn("warning: 2 citation chips", out)

    def test_inline_and_block_url_merge_without_duplicates(self):
        a, b = self.server.page("/a"), self.server.page("/b", OTHER)
        self.write_answer(f"It can raise it ({a}).\nnhs.uk\n\nsources shown:\n{b}\n{a}\n")
        fx, _ = self.run_ok()
        self.assertEqual(self.urls_by_text(fx), {f"It can raise it ({a}).": [a, b]})
        self.assertEqual(self.server.hits, {"/a": 1, "/b": 1})


class Fetching(FetchSourcesBase):
    def test_page_is_stored_raw_with_status_final_url_date_and_hash(self):
        a = self.server.page("/a")
        self.write_answer(f"It can raise it ({a}).\n")
        fx, _ = self.run_ok()
        self.assertEqual((self.src / "1.html").read_bytes(), ARTICLE)
        [s] = fx["sources"]
        self.assertEqual(s["url"], a)
        self.assertEqual(s["file"], "1.html")
        self.assertRegex(s["fetched_on"], r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual(s["fetch_status"], 200)
        self.assertEqual(s["final_url"], a)
        self.assertEqual(s["sha256"], hashlib.sha256(ARTICLE).hexdigest())
        self.assertEqual(fx["fetch_failures"], [])

    def test_redirect_records_final_url(self):
        target = self.server.page("/final")
        start = self.server.page("/start", b"", status=302, Location="/final")
        self.write_answer(f"It can raise it ({start}).\n")
        fx, _ = self.run_ok()
        [s] = fx["sources"]
        self.assertEqual((s["url"], s["final_url"]), (start, target))
        self.assertEqual((self.src / s["file"]).read_bytes(), ARTICLE)

    def test_non_html_keeps_its_extension(self):
        a = self.server.page("/doc", PDF, ctype="application/pdf")
        self.write_answer(f"It can raise it ({a}).\n")
        fx, _ = self.run_ok()
        self.assertEqual(fx["sources"][0]["file"], "1.pdf")

    def test_files_numbered_in_order_of_first_appearance(self):
        a, b = self.server.page("/a"), self.server.page("/b", OTHER)
        self.write_answer(f"One ({b}). Two ({a}). Three ({b}).\n")
        fx, _ = self.run_ok()
        self.assertEqual([(s["url"], s["file"]) for s in fx["sources"]],
                         [(b, "1.html"), (a, "2.html")])

    def test_user_agent_is_honest(self):
        a = self.server.page("/a")
        self.write_answer(f"It can raise it ({a}).\n")
        self.run_ok()
        self.assertTrue(self.server.agents[0].startswith("sauro-fetch/"), self.server.agents)

    def failure(self, fx, url):
        [f] = [f for f in fx["fetch_failures"] if f["url"] == url]
        self.assertNotIn(url, [s["url"] for s in fx["sources"]])
        return f

    def test_http_error_is_a_failure_with_its_body_kept_aside(self):
        a = self.server.page("/gone", b"<p>Not found</p>" * 40, status=404)
        self.write_answer(f"It can raise it ({a}).\n")
        fx, out = self.run_ok()
        f = self.failure(fx, a)
        self.assertEqual((f["reason"], f["fetch_status"], f["file"]), ("http_error", 404, "1.html"))
        self.assertEqual((self.src / "1.html").read_bytes(), b"<p>Not found</p>" * 40)
        self.assertRegex(f["fetched_on"], r"^\d{4}-\d{2}-\d{2}$")
        self.assertIn(a, out)

    def test_small_body_is_a_failure(self):
        a = self.server.page("/wall", b"<html>Just a moment...</html>")
        self.write_answer(f"It can raise it ({a}).\n")
        fx, _ = self.run_ok()
        f = self.failure(fx, a)
        self.assertEqual((f["reason"], f["fetch_status"], f["bytes"]), ("small_body", 200, 29))

    def test_body_of_exactly_the_limit_is_not_small(self):
        a = self.server.page("/a", b"x" * fetch_sources.SMALL_BODY_BYTES, ctype="text/plain")
        self.write_answer(f"It can raise it ({a}).\n")
        fx, _ = self.run_ok()
        self.assertEqual([s["url"] for s in fx["sources"]], [a])

    def test_empty_body_is_a_failure_with_no_file(self):
        a = self.server.page("/empty", b"")
        self.write_answer(f"It can raise it ({a}).\n")
        fx, _ = self.run_ok()
        f = self.failure(fx, a)
        self.assertEqual((f["reason"], f["file"]), ("empty_body", None))
        self.assertEqual(list(self.src.iterdir()), [self.src / "answer.md"])

    def test_html_with_no_rendered_text_is_a_failure(self):
        a = self.server.page("/app", JS_ONLY)
        self.write_answer(f"It can raise it ({a}).\n")
        fx, _ = self.run_ok()
        self.assertEqual(self.failure(fx, a)["reason"], "empty_text")

    def test_timeout_is_one_attempt_and_a_failure(self):
        a = self.server.page("/slow")
        self.server.delay["/slow"] = 1.0
        self.write_answer(f"It can raise it ({a}).\n")
        with mock.patch.object(fetch_sources, "TIMEOUT_SECONDS", 0.2):
            fx, _ = self.run_ok()
        f = self.failure(fx, a)
        self.assertEqual((f["reason"], f["fetch_status"], f["file"]), ("timeout", None, None))
        self.assertEqual(self.server.hits["/slow"], 1)

    def test_server_error_is_not_retried(self):
        a = self.server.page("/flaky", b"<p>oops</p>", status=503)
        self.write_answer(f"It can raise it ({a}).\n")
        fx, _ = self.run_ok()
        self.assertEqual(self.failure(fx, a)["fetch_status"], 503)
        self.assertEqual(self.server.hits["/flaky"], 1)

    def test_retries_constant_is_used(self):
        a = self.server.page("/flaky", b"<p>oops</p>", status=503)
        self.write_answer(f"It can raise it ({a}).\n")
        with mock.patch.object(fetch_sources, "RETRIES", 1):
            self.run_ok()
        self.assertEqual(self.server.hits["/flaky"], 2)

    def test_body_over_the_cap_is_a_failure_and_not_stored(self):
        a = self.server.page("/big", b"x" * 2000)
        self.write_answer(f"It can raise it ({a}).\n")
        with mock.patch.object(fetch_sources, "MAX_BODY_BYTES", 1000):
            fx, _ = self.run_ok()
        f = self.failure(fx, a)
        self.assertEqual((f["reason"], f["file"]), ("too_large", None))
        self.assertEqual(list(self.src.iterdir()), [self.src / "answer.md"])

    def test_dns_failure(self):
        self.write_answer("It can raise it (https://no-such-host.example/a).\n")
        err = urllib.error.URLError(socket.gaierror(-2, "Name or service not known"))
        with mock.patch.object(fetch_sources.urllib.request, "urlopen", side_effect=err):
            fx, _ = self.run_ok()
        f = self.failure(fx, "https://no-such-host.example/a")
        self.assertEqual((f["reason"], f["fetch_status"]), ("dns_failed", None))

    def test_connection_refused(self):
        # A port that was just closed refuses the connection.
        s = socket.socket()
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
        s.close()
        url = f"http://127.0.0.1:{port}/a"
        self.write_answer(f"It can raise it ({url}).\n")
        fx, _ = self.run_ok()
        self.assertEqual(self.failure(fx, url)["reason"], "connection_failed")

    def test_written_fixture_passes_check_fixtures(self):
        # The contract between the two scripts: a fresh fixture, with a failure in it, passes.
        a, gone = self.server.page("/a"), self.server.page("/gone", b"<p>x</p>" * 100, status=404)
        self.write_answer(f"One ({a}). Two ({gone}).\nThree.\n")
        self.run_ok()
        r = subprocess.run([sys.executable, str(TOOLS / "check_fixtures.py"), str(self.fixtures)],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("1 fixtures, 3 claims, 3 unlabeled, 0 spans", r.stdout)


class Rerun(FetchSourcesBase):
    def test_rerun_keeps_hand_edited_claims_and_labels(self):
        a = self.server.page("/a")
        self.write_answer(f"One ({a}). Two.\n")
        fx, _ = self.run_ok()
        fx["claims"] = [dict(fx["claims"][0], text="One, merged by hand.", label="supported",
                             evidence_span="Most people do not notice it")]
        (self.fixtures / "0001.json").write_text(json.dumps(fx), encoding="utf-8")
        again, _ = self.run_ok()
        self.assertEqual(again["claims"], fx["claims"])

    def test_rerun_never_refetches_a_stored_page(self):
        a = self.server.page("/a")
        self.write_answer(f"One ({a}).\n")
        self.run_ok()
        self.server.page("/a", OTHER)
        fx, _ = self.run_ok()
        self.assertEqual(self.server.hits["/a"], 1)
        self.assertEqual((self.src / "1.html").read_bytes(), ARTICLE)
        self.assertEqual(len(fx["sources"]), 1)

    def test_rerun_retries_a_failed_url_and_moves_it_to_sources(self):
        a = self.server.page("/a", b"<p>busy</p>" * 60, status=503)
        self.write_answer(f"One ({a}).\n")
        fx, _ = self.run_ok()
        self.assertEqual(len(fx["fetch_failures"]), 1)
        self.server.page("/a")
        fx, _ = self.run_ok()
        self.assertEqual(fx["fetch_failures"], [])
        self.assertEqual([(s["url"], s["file"]) for s in fx["sources"]], [(a, "1.html")])
        self.assertEqual((self.src / "1.html").read_bytes(), ARTICLE)

    def test_new_url_on_rerun_never_takes_a_stored_page_file(self):
        a, b = self.server.page("/a"), self.server.page("/b", OTHER)
        self.write_answer(f"One ({a}).\n")
        self.run_ok()
        # The owner adds a URL before the first one. File 1.html must stay a's page.
        self.write_answer(f"Zero ({b}). One ({a}).\n")
        fx, _ = self.run_ok()
        self.assertEqual({s["url"]: s["file"] for s in fx["sources"]}, {a: "1.html", b: "2.html"})
        self.assertEqual((self.src / "1.html").read_bytes(), ARTICLE)
        self.assertEqual((self.src / "2.html").read_bytes(), OTHER)

    def test_reviewed_fixture_is_never_written_or_fetched(self):
        a = self.server.page("/a", status=503)
        self.write_answer(f"One ({a}).\n")
        fx, _ = self.run_ok()
        fx["reviewed"] = True
        path = self.fixtures / "0001.json"
        path.write_text(json.dumps(fx), encoding="utf-8")
        before = path.read_bytes()
        self.server.page("/a")
        code, out = self.run_script()
        self.assertEqual(code, 1)
        self.assertIn("reviewed", out)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(self.server.hits["/a"], 1)

    def test_rerun_with_nothing_new_fetches_nothing(self):
        a = self.server.page("/a")
        self.write_answer(f"One ({a}).\n")
        self.run_ok()
        _, out = self.run_ok()
        self.assertEqual(self.server.hits["/a"], 1)
        self.assertRegex(out, r"0 fetched")


class Script(unittest.TestCase):
    def test_runs_as_a_script_from_any_directory(self):
        # The README tells people to run it by path, so the import of check_fixtures must work.
        with tempfile.TemporaryDirectory() as d:
            r = subprocess.run([sys.executable, str(TOOLS / "fetch_sources.py"), d + "/none.sources"],
                               capture_output=True, text=True, cwd=d)
        self.assertEqual(r.returncode, 1)
        self.assertIn("answer.md", r.stdout + r.stderr)
        self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
