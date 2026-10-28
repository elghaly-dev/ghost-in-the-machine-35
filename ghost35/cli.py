from __future__ import annotations

import argparse
import sys
from textwrap import indent

from ghost35 import __version__
from ghost35.demo import run_demo
from ghost35.ollama import OllamaConfig, OllamaError, list_models
from ghost35.whisper import draft_remembrance, whisper_command

GHOST_PREFIX = "👻 "


def _print_whisper(text: str, source: str) -> None:
    label = "whisper (Ollama)" if source == "ollama" else "whisper (offline fallback)"
    print(f"{GHOST_PREFIX}[{label}]")
    print(indent(text.strip(), prefix="   "))


def cmd_whisper(args: argparse.Namespace) -> int:
    text, source = whisper_command(args.command)
    _print_whisper(text, source)
    return 0


def cmd_session(args: argparse.Namespace) -> int:
    for command in args.command:
        text, source = whisper_command(command)
        print(f"\n$ {command}")
        _print_whisper(text, source)
    return 0


def cmd_remember(args: argparse.Namespace) -> int:
    text, source = draft_remembrance(args.name, args.notes)
    header = "ofrenda draft (Ollama)" if source == "ollama" else "ofrenda draft (offline template)"
    print(f"{GHOST_PREFIX}[{header}]\n")
    print(text)
    return 0


def cmd_doctor(_: argparse.Namespace) -> int:
    cfg = OllamaConfig.from_env()
    print(f"Ghost35 {__version__}")
    print(f"Ollama base: {cfg.base_url}")
    print(f"Model:       {cfg.model}")
    try:
        models = list_models(cfg)
    except OllamaError as exc:
        print(f"Status:      unreachable ({exc})")
        print("Install Ollama from https://ollama.com and run: ollama pull " + cfg.model)
        return 1
    print(f"Status:      reachable ({len(models)} model(s) listed)")
    if cfg.model not in models and not any(m.startswith(cfg.model.split(":")[0]) for m in models):
        print(f"Warning:     '{cfg.model}' not in tag list — run: ollama pull {cfg.model}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ghost35",
        description="Ghost in the Machine — open-weight whispers for your terminal (Ollama).",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_whisper = sub.add_parser("whisper", help="Comment on a single shell command")
    p_whisper.add_argument("command", help="Command the user typed (not executed)")
    p_whisper.set_defaults(func=cmd_whisper)

    p_session = sub.add_parser("session", help="Whisper after each command in a list")
    p_session.add_argument("command", nargs="+", help="Commands to comment on")
    p_session.set_defaults(func=cmd_session)

    p_remember = sub.add_parser("remember", help="Draft a virtual ofrenda remembrance")
    p_remember.add_argument("--name", required=True, help="Who is being remembered")
    p_remember.add_argument(
        "--notes",
        default="",
        help="Optional memories, favorites, or phrases",
    )
    p_remember.set_defaults(func=cmd_remember)

    p_demo = sub.add_parser("demo", help="Run the scripted demo (uses Ollama when available)")
    p_demo.set_defaults(func=lambda _a: run_demo())

    p_doctor = sub.add_parser("doctor", help="Check Ollama connectivity and model tag")
    p_doctor.set_defaults(func=cmd_doctor)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
