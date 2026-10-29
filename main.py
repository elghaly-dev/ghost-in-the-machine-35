#!/usr/bin/env python3
"""NightWatch: a local-first morning report from a night's log lines.

While the owner sleeps, the Faithful Servant keeps watch over a log file.
Each morning it writes one short report with two clearly separated
sections:

1. Story -- a tale (fiction) woven from the night's log lines.
2. Facts -- a plain summary of real parsed events.

Privacy: the only network call this tool makes is to a local Ollama
server on localhost. Nothing is sent anywhere else.
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

DEFAULT_MODEL = "gemma3:1b"
DEFAULT_OLLAMA_URL = "http://localhost:11434"

LEVELS = ("INFO", "WARN", "ERROR", "DEBUG", "TRACE")

LINE_RE = re.compile(
    r"^(?:(?P<ts>\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})\s+)?"
    r"(?P<level>INFO|WARN|WARNING|ERROR|DEBUG|TRACE)?\s*:?\s*(?P<msg>.*)$"
)


def parse_log_text(text):
    """Parse log text into counts by level and ranked error lines."""
    by_level = Counter()
    error_messages = Counter()
    total = 0
    for raw in text.splitlines():
        if not raw.strip():
            continue
        total += 1
        match = LINE_RE.match(raw)
        level = (match.group("level") or "OTHER").upper()
        if level == "WARNING":
            level = "WARN"
        if level not in LEVELS:
            level = "OTHER"
        by_level[level] += 1
        if level in ("ERROR", "WARN"):
            message = match.group("msg").strip()
            if message:
                error_messages[message] += 1
    ranked = sorted(error_messages.items(), key=lambda item: (-item[1], item[0]))[:5]
    return {
        "total_lines": total,
        "by_level": dict(by_level),
        "top_errors": [{"count": count, "message": msg} for msg, count in ranked],
    }


def read_logs(logs_path):
    """Read one log file, or every .log file in a folder. Returns (texts, names).

    Only file basenames are kept, so no local paths leak into the report.
    """
    path = Path(logs_path)
    if path.is_dir():
        files = sorted(path.glob("*.log"))
    elif path.is_file():
        files = [path]
    else:
        raise FileNotFoundError(f"log path not found: {logs_path}")
    texts = []
    names = []
    for log_file in files:
        texts.append(log_file.read_text(encoding="utf-8", errors="replace"))
        names.append(log_file.name)
    return texts, names


def summarize(texts):
    """Merge parsed results from several log texts into one summary."""
    by_level = Counter()
    error_messages = Counter()
    total = 0
    for text in texts:
        parsed = parse_log_text(text)
        total += parsed["total_lines"]
        by_level.update(parsed["by_level"])
        for item in parsed["top_errors"]:
            error_messages[item["message"]] += item["count"]
    ranked = sorted(error_messages.items(), key=lambda item: (-item[1], item[0]))[:5]
    return {
        "total_lines": total,
        "by_level": dict(sorted(by_level.items())),
        "top_errors": [{"count": count, "message": msg} for msg, count in ranked],
    }


def story_prompt(summary):
    """Build the prompt for the local model from parsed facts only."""
    lines = [f"total lines: {summary['total_lines']}"]
    for level, count in summary["by_level"].items():
        lines.append(f"{level}: {count}")
    for item in summary["top_errors"]:
        lines.append(f"top error ({item['count']} times): {item['message']}")
    facts = "\n".join(lines)
    return (
        "Write a short ghost tale, four to six sentences, inspired by "
        "these log facts from one night. The tale is fiction: a faithful "
        "servant keeps watch through the night while the owner sleeps. "
        "Do not claim any of it really happened, and do not add new "
        "incidents beyond these facts.\n\n" + facts
    )


def mock_story(summary):
    """A fixed placeholder tale for shape checks, built from real counts."""
    by_level = summary["by_level"]
    info = by_level.get("INFO", 0)
    warn = by_level.get("WARN", 0)
    error = by_level.get("ERROR", 0)
    return (
        "The Faithful Servant kept watch through the night while the owner "
        f"slept. The machine murmured {info} calm lines, {warn} warnings, "
        f"and {error} errors into the dark, and the Servant wrote them all "
        "down before dawn. Nothing stirred that was not already written, "
        "and the morning found the watch complete."
    )


def generate_story(summary, model=DEFAULT_MODEL, base_url=DEFAULT_OLLAMA_URL):
    """Ask the local model for the night's tale. One function, one call site.

    Set NIGHTWATCH_MOCK_MODEL=1 to get the placeholder tale instead, for
    shape checks when no model is present.
    """
    if os.environ.get("NIGHTWATCH_MOCK_MODEL") == "1":
        return mock_story(summary)
    payload = json.dumps(
        {
            "model": model,
            "prompt": story_prompt(summary),
            "stream": False,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, OSError, ValueError) as exc:
        raise RuntimeError(f"could not reach the local model: {exc}") from exc
    text = (data.get("response") or "").strip()
    if not text:
        raise RuntimeError("the local model returned an empty story")
    return text


def build_report(summary, story, source_names):
    """Render the report. The fiction label and the facts label are always on."""
    out = []
    out.append("# NightWatch morning report")
    out.append("")
    out.append("## Story -- a tale (fiction)")
    out.append("")
    out.append(
        "The story below is fiction. It is a tale woven from the night's "
        "log lines, not a record of real events."
    )
    out.append("")
    out.append(story)
    out.append("")
    out.append("## Facts -- parsed from the log")
    out.append("")
    out.append("The facts below are parsed from real log lines. They are not fiction.")
    out.append("")
    out.append(f"- Total lines: {summary['total_lines']}")
    out.append("- Counts by level:")
    if summary["by_level"]:
        for level, count in summary["by_level"].items():
            out.append(f"  - {level}: {count}")
    else:
        out.append("  - none")
    out.append("- Top error lines:")
    if summary["top_errors"]:
        for item in summary["top_errors"]:
            out.append(f"  - ({item['count']}x) {item['message']}")
    else:
        out.append("  - none")
    if source_names:
        out.append(f"- Sources: {', '.join(source_names)}")
    out.append("")
    out.append(
        "Honesty note: the story is fiction; the facts are parsed from the log lines."
    )
    return "\n".join(out) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="NightWatch: a morning report from a night's logs."
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="run a single report now (the only mode for now)",
    )
    parser.add_argument(
        "--logs",
        default=None,
        help="a log file or a folder of .log files (default: data/sample_logs)",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="where to write the report (default: data/output/report.md)",
    )
    args = parser.parse_args(argv)

    base = Path(__file__).resolve().parent
    logs_path = Path(args.logs) if args.logs else base / "data" / "sample_logs"
    out_path = Path(args.out) if args.out else base / "data" / "output" / "report.md"

    try:
        texts, names = read_logs(logs_path)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    summary = summarize(texts)
    model = os.environ.get("NIGHTWATCH_MODEL", DEFAULT_MODEL)
    base_url = os.environ.get("NIGHTWATCH_OLLAMA_URL", DEFAULT_OLLAMA_URL)
    try:
        story = generate_story(summary, model=model, base_url=base_url)
    except RuntimeError as exc:
        print(f"warning: {exc}", file=sys.stderr)
        story = (
            "No story was written for this run: the local model could not be "
            "reached. Start Ollama, pull gemma3:1b, and run again."
        )
    report = build_report(summary, story, names)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")
    print(f"wrote {out_path}")
    print(f"lines: {summary['total_lines']}, levels: {summary['by_level']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
