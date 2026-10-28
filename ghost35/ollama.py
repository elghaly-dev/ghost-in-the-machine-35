from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_BASE = "http://127.0.0.1:11434"
DEFAULT_MODEL = "llama3.2"


@dataclass(frozen=True)
class OllamaConfig:
    base_url: str
    model: str
    timeout_seconds: float

    @classmethod
    def from_env(cls) -> OllamaConfig:
        return cls(
            base_url=os.environ.get("OLLAMA_HOST", DEFAULT_BASE).rstrip("/"),
            model=os.environ.get("GHOST35_MODEL", DEFAULT_MODEL),
            timeout_seconds=float(os.environ.get("GHOST35_TIMEOUT", "120")),
        )


class OllamaError(RuntimeError):
    pass


def _post_json(url: str, payload: dict[str, Any], timeout: float) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise OllamaError(f"Ollama HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise OllamaError(f"Cannot reach Ollama at {url}: {exc.reason}") from exc

    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise OllamaError(f"Invalid JSON from Ollama: {body[:200]}") from exc


def list_models(cfg: OllamaConfig) -> list[str]:
    url = f"{cfg.base_url}/api/tags"
    req = Request(url, method="GET")
    try:
        with urlopen(req, timeout=cfg.timeout_seconds) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except (URLError, HTTPError) as exc:
        raise OllamaError(f"Cannot list models: {exc}") from exc
    models = payload.get("models") or []
    return [m.get("name", "") for m in models if m.get("name")]


def generate(
    cfg: OllamaConfig,
    *,
    system: str,
    user: str,
    temperature: float = 0.85,
) -> str:
    url = f"{cfg.base_url}/api/chat"
    payload = {
        "model": cfg.model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "stream": False,
        "options": {"temperature": temperature},
    }
    result = _post_json(url, payload, cfg.timeout_seconds)
    message = result.get("message") or {}
    content = (message.get("content") or "").strip()
    if not content:
        raise OllamaError("Ollama returned an empty message.")
    return content
