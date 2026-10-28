---
title: "Hacktoberfest Open-Source AI Challenge Week 4: Ghost in the Machine"
published: false
tags: devchallenge, hf26challenge, hacktoberfest, ai, opensource, python, ollama
cover_image:
---

Hacktoberfest Open-Source AI Challenge: Ghost in the Machine Submission 👻🌼

## What I Built

**Ghost35** — a possessed terminal companion that uses **Ollama** and an **open-weight** model to whisper back when you *type* shell commands (it never runs them for you). It also drafts a **virtual ofrenda** remembrance from short notes, tying Halloween spookiness to Día de los Muertos memory-keeping.

I read the Week 4 prompt’s “haunted terminal” idea literally: the ghost lives in the machine that already listens to your keystrokes — your shell — but here it only comments on what you show it.

## Demo

Ghost35 is **local-first** (no deploy URL in this entry).

**How to reproduce:**

1. Clone https://github.com/elghaly-dev/ghost-in-the-machine-35
2. Install [Ollama](https://ollama.com) and run `ollama pull llama3.2` (or set `GHOST35_MODEL` to a model you already have).
3. Run:

```bash
python3 -m ghost35 doctor
python3 -m ghost35 demo
python3 -m ghost35 remember --name "YOUR_NAME_HERE" --notes "A few favorites or memories"
```

**Owner:** replace this section with a link to your **video walkthrough** or embedded terminal recording before publishing. Do not claim a deploy you have not verified.

## Code

Repository: https://github.com/elghaly-dev/ghost-in-the-machine-35

Stack: Python 3.10+, Ollama HTTP API (`/api/chat`), stdlib HTTP client. Optional offline fallbacks are labeled in the CLI output.

## How I Built It

- **Ollama** — local inference server for open-weight models.
- **Default model:** `llama3.2` (configurable via `GHOST35_MODEL`).
- **Prompts** in `ghost35/prompts.py` — system instructions for whispers and ofrenda drafts.
- **CLI** — `whisper`, `session`, `remember`, `demo`, and `doctor` subcommands.
- **Tests** — pytest covers demo flow and offline fallback wording.

The open model is not decoration: every “live” whisper and remembrance draft goes through Ollama when it is reachable. If Ollama is down, the tool says so and uses small rule-based templates instead of pretending.

## Why Does Open Innovation Matter?

Closed hosted chat APIs would send every command string and remembrance note to someone else’s server. For a project about **ghosts in your machine** and **family memory**, that felt wrong.

Running Ollama locally means:

- Command history and remembrance notes stay on **your** disk unless you publish them.
- The project can run **without cloud inference** after the model is downloaded.
- I can **change models or prompts** without renegotiating with a vendor.

Trade-offs are real: you need disk space and a machine that can run the model; smaller models may write uneven prose. Open weights let me accept those trade-offs consciously instead of hiding them behind a API bill.

## My Agent Session

Optional for judges: add a DevRelay or agent session link here if you have one. **UNKNOWN** — not included in this draft.

## The Spirit of It

The line between past and present thins this week — Halloween on the 31st, Día de los Muertos right after. Ghost35 is my small ritual: let the machine speak, but keep the voice **yours**, running on hardware you control, remembering people you choose to name.

---

**Partner categories:** not targeted in this entry unless the owner adds meaningful partner tech before publish. **UNKNOWN** for category list unless you extend the project.
