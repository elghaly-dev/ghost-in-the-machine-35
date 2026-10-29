"""Tests for NightWatch. The model call is always mocked here; no Ollama
server is needed to run this suite."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import main


def test_parse_counts_by_level():
    text = (
        "2026-10-27 01:00:00 INFO host-alpha.example worker started\n"
        "2026-10-27 01:01:00 WARN host-alpha.example retry 1 for job nightly-check\n"
        "2026-10-27 01:02:00 ERROR host-alpha.example job failed: timeout\n"
        "2026-10-27 01:03:00 DEBUG host-alpha.example cache size 512 entries\n"
    )
    parsed = main.parse_log_text(text)
    assert parsed["total_lines"] == 4
    assert parsed["by_level"] == {"DEBUG": 1, "ERROR": 1, "INFO": 1, "WARN": 1}


def test_warning_normalized_to_warn():
    parsed = main.parse_log_text("2026-10-27 01:00:00 WARNING host-alpha.example slow disk\n")
    assert parsed["by_level"] == {"WARN": 1}


def test_lines_without_level_count_as_other():
    parsed = main.parse_log_text("just some plain text\n2026-10-27 01:00:00 INFO ok\n")
    assert parsed["total_lines"] == 2
    assert parsed["by_level"]["OTHER"] == 1
    assert parsed["by_level"]["INFO"] == 1


def test_top_error_lines_ranked():
    text = (
        "2026-10-27 01:00:00 ERROR host-alpha.example connection refused\n"
        "2026-10-27 01:01:00 ERROR host-alpha.example connection refused\n"
        "2026-10-27 01:02:00 WARN host-alpha.example retry 1\n"
        "2026-10-27 01:03:00 ERROR host-alpha.example disk full\n"
    )
    parsed = main.parse_log_text(text)
    top = parsed["top_errors"]
    assert top[0] == {"count": 2, "message": "host-alpha.example connection refused"}
    assert len(top) == 3


def test_empty_log_gives_zeros():
    parsed = main.parse_log_text("")
    assert parsed["total_lines"] == 0
    assert parsed["by_level"] == {}
    assert parsed["top_errors"] == []


def test_report_labels_fiction_and_facts():
    summary = {
        "total_lines": 3,
        "by_level": {"ERROR": 1, "INFO": 2},
        "top_errors": [{"count": 1, "message": "host-alpha.example job failed"}],
    }
    report = main.build_report(summary, "A tale.", ["night.log"])
    assert "## Story -- a tale (fiction)" in report
    assert "The story below is fiction" in report
    assert "## Facts -- parsed from the log" in report
    assert "parsed from real log lines" in report
    assert "A tale." in report
    assert "- Total lines: 3" in report
    assert "host-alpha.example job failed" in report
    assert "Sources: night.log" in report


def test_mock_story_mentions_servant(monkeypatch):
    monkeypatch.setenv("NIGHTWATCH_MOCK_MODEL", "1")
    summary = {"total_lines": 5, "by_level": {"ERROR": 1, "INFO": 3, "WARN": 1}, "top_errors": []}
    story = main.generate_story(summary)
    assert "Faithful Servant" in story


def test_generate_story_calls_localhost_only(monkeypatch):
    seen = {}

    class FakeResponse:
        def __init__(self, payload):
            self._payload = payload

        def read(self):
            return json.dumps(self._payload).encode("utf-8")

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    def fake_urlopen(request, timeout=None):
        seen["url"] = request.full_url
        seen["body"] = json.loads(request.data.decode("utf-8"))
        return FakeResponse({"response": "A spooky tale."})

    monkeypatch.delenv("NIGHTWATCH_MOCK_MODEL", raising=False)
    monkeypatch.setattr(main.urllib.request, "urlopen", fake_urlopen)
    summary = {"total_lines": 1, "by_level": {"INFO": 1}, "top_errors": []}
    story = main.generate_story(summary)
    assert story == "A spooky tale."
    assert "localhost" in seen["url"]
    assert "11434" in seen["url"]
    assert seen["body"]["model"] == "gemma3:1b"


def test_cli_end_to_end_mocked(monkeypatch, tmp_path):
    monkeypatch.setenv("NIGHTWATCH_MOCK_MODEL", "1")
    log = tmp_path / "night.log"
    log.write_text(
        "2026-10-27 01:00:00 INFO host-alpha.example worker started\n"
        "2026-10-27 01:01:00 ERROR host-alpha.example job failed: timeout\n",
        encoding="utf-8",
    )
    out = tmp_path / "report.md"
    code = main.main(["--once", "--logs", str(log), "--out", str(out)])
    assert code == 0
    report = out.read_text(encoding="utf-8")
    assert "## Story -- a tale (fiction)" in report
    assert "## Facts -- parsed from the log" in report
    assert "Faithful Servant" in report
    assert "- Total lines: 2" in report


def test_cli_reads_folder_of_logs(monkeypatch, tmp_path):
    monkeypatch.setenv("NIGHTWATCH_MOCK_MODEL", "1")
    (tmp_path / "a.log").write_text("2026-10-27 01:00:00 INFO one\n", encoding="utf-8")
    (tmp_path / "b.log").write_text("2026-10-27 01:00:00 INFO two\n", encoding="utf-8")
    out = tmp_path / "report.md"
    code = main.main(["--once", "--logs", str(tmp_path), "--out", str(out)])
    assert code == 0
    assert "- Total lines: 2" in out.read_text(encoding="utf-8")


def test_missing_log_path_returns_error_code(tmp_path):
    code = main.main(
        ["--once", "--logs", str(tmp_path / "nope.log"), "--out", str(tmp_path / "r.md")]
    )
    assert code == 2
