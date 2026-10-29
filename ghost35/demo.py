from __future__ import annotations

from ghost35.whisper import whisper_command

DEMO_COMMANDS = [
    "ls -la",
    "git status",
    "python -m ghost35 doctor",
]


def run_demo() -> int:
    print("=== Ghost35 demo (commands are not executed) ===\n")
    for command in DEMO_COMMANDS:
        text, source = whisper_command(command)
        print(f"$ {command}")
        label = "Ollama" if source == "ollama" else "fallback"
        print(f"👻 [{label}] {text}\n")
    print("=== end demo ===")
    return 0
