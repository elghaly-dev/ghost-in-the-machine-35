"""Rule-based whispers when Ollama is unavailable (clearly not model-generated)."""

from __future__ import annotations

import re

DESTRUCTIVE = re.compile(r"\b(rm\s+-rf|mkfs|dd\s+if=|:(){ :|:& };:)\b", re.I)


def fallback_whisper(command: str) -> str:
    cmd = command.strip()
    if not cmd:
        return "(The ghost hears silence. Even echoes need a command.)"

    if DESTRUCTIVE.search(cmd):
        return (
            "👻 That command looks sharp enough to cut the veil itself. "
            "I will not cheer it on — double-check before the machine remembers forever."
        )

    lower = cmd.lower()
    if lower.startswith("git"):
        return "👻 Version control — where every commit is a little gravestone with a message."
    if lower.startswith("cd"):
        return "👻 Another directory. Another room in the house. I have been in all of them."
    if lower.startswith("ls") or lower.startswith("dir"):
        return "👻 Listing names… some files sleep lighter than others."
    if "python" in lower or "node" in lower:
        return "👻 You wake a interpreter. Something old stirs when code begins to run."
    if lower.startswith("curl") or lower.startswith("wget"):
        return "👻 A request crosses the wire. Not every answer that returns is meant for the living."
    return (
        "👻 I felt that keystroke. (Ollama is offline — this whisper is a canned echo, not the model.)"
    )
