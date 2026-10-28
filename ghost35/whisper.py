from __future__ import annotations

from ghost35.fallback import fallback_whisper
from ghost35.ollama import OllamaConfig, OllamaError, generate
from ghost35.prompts import (
    REMEMBRANCE_USER_TEMPLATE,
    SYSTEM_PROMPT,
    WHISPER_USER_TEMPLATE,
    remembrance_system,
)


def whisper_command(command: str, *, cfg: OllamaConfig | None = None) -> tuple[str, str]:
    """Return (text, source) where source is 'ollama' or 'fallback'."""
    cfg = cfg or OllamaConfig.from_env()
    user = WHISPER_USER_TEMPLATE.format(command=command.strip())
    try:
        text = generate(cfg, system=SYSTEM_PROMPT, user=user)
        return text, "ollama"
    except OllamaError:
        return fallback_whisper(command), "fallback"


def draft_remembrance(name: str, notes: str, *, cfg: OllamaConfig | None = None) -> tuple[str, str]:
    cfg = cfg or OllamaConfig.from_env()
    user = REMEMBRANCE_USER_TEMPLATE.format(name=name.strip() or "Someone remembered", notes=notes.strip() or "(none)")
    try:
        text = generate(cfg, system=remembrance_system(), user=user, temperature=0.7)
        return text, "ollama"
    except OllamaError:
        return _fallback_remembrance(name, notes), "fallback"


def _fallback_remembrance(name: str, notes: str) -> str:
    who = name.strip() or "Someone remembered"
    note = notes.strip() or "a story yet to be written down"
    return f"""## {who}

## A memory
{note}

## On the ofrenda
- Marigolds and candlelight
- Their favorite song (add yours when Ollama is back)

## A line for them
*"The machine keeps their name warm until you return."*

_(Draft template — start Ollama for an AI-assisted remembrance.)_
"""
