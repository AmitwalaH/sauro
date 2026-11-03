"""Turn a saved AI answer into a fixture skeleton that check_fixtures.py accepts.

Usage: python3 bench/tools/fetch_sources.py bench/fixtures/0001.sources

Reads 0001.sources/answer.md, fetches every URL in it once, stores each response body in
0001.sources/ as <n>.html (or <n>.<ext>), and writes bench/fixtures/0001.json with:
- `sources`: the pages that were stored, in the shape bench/LABELING.md defines, plus the
  HTTP status, the final URL after redirects and a sha256 of the body.
- `fetch_failures`: the URLs that gave no usable page, with the facts of why. These are
  kept out of `sources`, so check_fixtures.py never accepts a span from a failed page.
- `claims`: one skeleton per sentence, every label null. The script never writes a label.

A rerun fetches only URLs that have no stored page yet, including ones that failed before.
It never fetches a stored page again, never touches `claims` once the fixture exists, and
never writes a fixture marked reviewed.

The sentence split is crude on purpose, because the labeler merges and splits by hand: a
break after ". ", "? " or "! " followed by a capital, and at every line break.
"""

import datetime
import hashlib
import http.client
import json
import mimetypes
import os
import re
import socket
import sys
import urllib.error
import urllib.request
from pathlib import Path

from check_fixtures import page_text, squash

# The fetch policy. PROJECT.md "Fetch policy" repeats these values; change both together.
TIMEOUT_SECONDS = 20
RETRIES = 0  # Extra attempts after a failure. None by default: a rerun is the retry.
MAX_BODY_BYTES = 10 * 1024 * 1024

# A 200 body this small is almost never the article. It is a bot check, a consent wall or
# an app shell. The labeler opens the stored body and picks the reason code.
SMALL_BODY_BYTES = 500

# Honest, so a site that blocks scripts can block this one. sauro does not evade blocks.
USER_AGENT = "sauro-fetch/0.1 (+https://github.com/AmitwalaH/sauro)"

HEADER_FIELDS = ("model", "domain", "asked_on", "question")

# Up to whitespace, a closing square bracket, a quote or an angle bracket.
URL_RE = re.compile(r"https?://[^\s\]\"'<>]+")
TRAILING_PUNCTUATION = ".,:;!?"

SENTENCE_BREAK = re.compile(r"(?<=[.?!])\s+(?=[A-Z])")

# The citation chip a chat UI shows after a passage: a bare domain line, then maybe "+2".
CHIP_DOMAIN = re.compile(r"^[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$")
CHIP_COUNT = re.compile(r"^\+\d+$")
SOURCES_SHOWN = "sources shown:"


class AnswerError(Exception):
    pass


def extract_urls(text):
    """Every URL in text, once each, in order. Trailing punctuation is not part of a URL."""
    urls = []
    for raw in URL_RE.findall(text):
        url = raw
        while url:
            if url[-1] in TRAILING_PUNCTUATION:
                url = url[:-1]
            # A ")" belongs to the URL only when it closes a "(" inside it, as on Wikipedia.
            elif url.endswith(")") and url.count(")") > url.count("("):
                url = url[:-1]
            else:
                break
        if url not in urls:
            urls.append(url)
    return urls


def read_answer(path):
    """Return (header dict, answer text after the --- line)."""
    if not path.is_file():
        raise AnswerError(f"{path}: no answer.md")
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    try:
        sep = next(i for i, line in enumerate(lines) if line.strip() == "---")
    except StopIteration:
        raise AnswerError(f"{path}: no --- line between the header and the answer") from None
    header = {}
    for line in lines[:sep]:
        key, _, value = line.partition(":")
        header[key.strip()] = value.strip()
    missing = [f for f in HEADER_FIELDS if not header.get(f)]
    if missing:
        raise AnswerError(f"{path}: header is missing {', '.join(missing)}")
    return header, "".join(lines[sep + 1:])


def skeleton_claims(fixture_id, answer):
    """One label-null claim per sentence, with cited_urls filled by the rules in the README."""
    body, shown = answer, []
    lines = answer.splitlines(keepends=True)
    marks = [i for i, line in enumerate(lines) if line.strip().lower() == SOURCES_SHOWN]
    if marks:
        body = "".join(lines[:marks[-1]])
        shown = extract_urls("".join(lines[marks[-1] + 1:]))

    sentences, chip_targets = [], []
    after_chip = False
    for line in body.splitlines():
        line = line.strip()
        if not line:
            continue
        if CHIP_DOMAIN.match(line):
            if sentences and len(sentences) - 1 not in chip_targets:
                chip_targets.append(len(sentences) - 1)
            after_chip = True
            continue
        if after_chip and CHIP_COUNT.match(line):
            continue
        after_chip = False
        sentences.extend(s for s in (p.strip() for p in SENTENCE_BREAK.split(line)) if s)
    if not sentences:
        raise AnswerError("answer is empty")

    cited = [extract_urls(s) for s in sentences]
    if shown:
        for i in chip_targets or [len(sentences) - 1]:
            cited[i] += [u for u in shown if u not in cited[i]]

    claims = [{
        "claim_id": f"{fixture_id}-{n:02d}",
        "text": text,
        "cited_urls": urls,
        "label": None,
        "reason_code": None,
        "evidence_span": None,
        "evidence_location": None,
        "labeler_note": None,
        "hard": False,
    } for n, (text, urls) in enumerate(zip(sentences, cited), 1)]
    return claims, len(chip_targets)


def extension(content_type):
    mime = (content_type or "").split(";")[0].strip().lower()
    if mime in ("text/html", "application/xhtml+xml", ""):
        return ".html"
    return mimetypes.guess_extension(mime) or ".bin"


def fetch(url):
    """Fetch url, with RETRIES extra attempts after a failure. Returns what fetch_once does."""
    for _ in range(RETRIES + 1):
        result = fetch_once(url)
        if result[4] is None:
            break
    return result


def fetch_once(url):
    """Fetch url once. Return (status, final url, content type, body bytes or None, reason).

    reason is None for a usable page, otherwise a short fact for the labeler.
    """
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as resp:
            status, final, ctype = resp.status, resp.geturl(), resp.headers.get("Content-Type")
            body = resp.read(MAX_BODY_BYTES + 1)
    except urllib.error.HTTPError as e:
        try:
            body = e.read(MAX_BODY_BYTES + 1)
        except (OSError, http.client.HTTPException):
            body = b""
        if len(body) > MAX_BODY_BYTES:
            body = b""
        return e.code, e.url, e.headers.get("Content-Type"), body or None, "http_error"
    except urllib.error.URLError as e:
        if isinstance(e.reason, socket.gaierror):
            return None, None, None, None, "dns_failed"
        if isinstance(e.reason, TimeoutError):
            return None, None, None, None, "timeout"
        return None, None, None, None, "connection_failed"
    except TimeoutError:  # a read that stalls after the connection was made
        return None, None, None, None, "timeout"
    except (OSError, http.client.HTTPException):
        return None, None, None, None, "connection_failed"

    if len(body) > MAX_BODY_BYTES:
        return status, final, ctype, None, "too_large"
    if status != 200:
        return status, final, ctype, body or None, "http_error"
    if not body:
        return status, final, ctype, None, "empty_body"
    if len(body) < SMALL_BODY_BYTES:
        return status, final, ctype, body, "small_body"
    if extension(ctype) == ".html" and not squash(page_text(body.decode("utf-8", "replace"))):
        return status, final, ctype, body, "empty_text"
    return status, final, ctype, body, None


def next_free_number(src_dir):
    used = [int(p.stem) for p in src_dir.iterdir() if p.stem.isdigit()]
    return max(used, default=0) + 1


def write_json(path, data):
    # Write then rename, so a crash never leaves a half-written fixture with labels in it.
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def run(src_dir):
    """Build or update the fixture for one <id>.sources directory. Returns the output lines."""
    if src_dir.suffix != ".sources":
        raise AnswerError(f"{src_dir}: give the <id>.sources directory that holds answer.md")
    fixture_id = src_dir.stem
    fixture_path = src_dir.with_suffix(".json")
    header, answer = read_answer(src_dir / "answer.md")

    if fixture_path.exists():
        try:
            fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        except ValueError as e:
            raise AnswerError(f"{fixture_path.name}: cannot read fixture: {e}") from None
        if fixture.get("reviewed") is True:
            raise AnswerError(f"{fixture_path.name} is reviewed, so it is frozen. Nothing written.")
        chips = None
    else:
        claims, chips = skeleton_claims(fixture_id, answer)
        fixture = {
            "id": fixture_id,
            "source_model": header["model"],
            "domain": header["domain"],
            "collected_on": header["asked_on"],
            "answer_text": answer,
            "sources": [],
            "fetch_failures": [],
            "claims": claims,
            "reviewed": False,
        }
    fixture.setdefault("fetch_failures", [])

    stored = {s["url"] for s in fixture["sources"]}
    old_failures = {f["url"]: f for f in fixture["fetch_failures"]}
    todo = [u for u in extract_urls(answer) if u not in stored]
    today = datetime.date.today().isoformat()

    out, failures = [], []
    for url in todo:
        status, final, ctype, body, reason = fetch(url)
        name = None
        if body is not None:
            # A retried URL reuses its old failure file, which no source points to.
            old = old_failures.get(url, {}).get("file")
            name = old if old and Path(old).suffix == extension(ctype) else (
                f"{next_free_number(src_dir)}{extension(ctype)}")
            (src_dir / name).write_bytes(body)
        if reason is None:
            fixture["sources"].append({
                "url": url, "file": name, "fetched_on": today, "fetch_status": status,
                "final_url": final, "sha256": hashlib.sha256(body).hexdigest(),
            })
        else:
            failures.append({
                "url": url, "fetched_on": today, "fetch_status": status, "final_url": final,
                "reason": reason, "bytes": None if body is None else len(body), "file": name,
            })
            out.append(f"fetch failed: {url}: {reason}" + (f" (HTTP {status})" if status else ""))
    # Failures not retried this run stay; retried ones are replaced by this run's result.
    fixture["fetch_failures"] = [f for f in fixture["fetch_failures"]
                                 if f["url"] not in todo] + failures

    write_json(fixture_path, fixture)
    if chips and chips > 1:
        out.append(f"warning: {chips} citation chips; every sources-shown URL was attached "
                   "to the sentence before each one. Prune cited_urls by hand.")
    out.append(f"{fixture_path.name}: {len(todo)} fetched, {len(todo) - len(failures)} stored, "
               f"{len(failures)} failed, {len(stored)} already stored, "
               f"{len(fixture['claims'])} claims")
    return out


def main(argv):
    if len(argv) != 2:
        print("usage: python3 bench/tools/fetch_sources.py bench/fixtures/<id>.sources")
        return 1
    try:
        lines = run(Path(argv[1]))
    except AnswerError as e:
        print(f"error: {e}")
        return 1
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
