# Ghost in the Machine 35 (Ghost35)

Entry for **DEV Hacktoberfest Open-Source AI Challenge — Week 4: Ghost in the Machine** (Oct 26–31, 2026).

**Ghost35** is a small Python CLI that lets an **open-weight model** (via [Ollama](https://ollama.com)) whisper spooky or remembrance-themed commentary on shell commands you type — without executing them. A second command drafts a **virtual ofrenda** remembrance from your notes, in the spirit of Día de los Muertos.

Built fresh for the challenge window with local inference at the core. No API keys in this repo.

By **Wyndham Heaven (elghaly)** — made with our Faithful Servant and checked by a human.

## Why open-source AI here

- **Ollama** runs the model on your machine; prompts and command text stay local unless you choose to share them.
- You can **swap models** (`GHOST35_MODEL`) or fine-tune prompts without a hosted vendor lock-in.
- After the model is pulled, whispers work **offline** (no cloud inference required for the core loop).

## Requirements

- Python **3.10+**
- **[Ollama](https://ollama.com)** installed and running (for model-generated whispers)
- An open-weight model pulled locally, e.g.:

```bash
ollama pull llama3.2
```

Default model name: `llama3.2` (override with `GHOST35_MODEL`).

## Quick start

```bash
git clone https://github.com/elghaly-dev/ghost-in-the-machine-35.git
cd ghost-in-the-machine-35
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"  # optional, for pytest only
python3 -m ghost35 doctor
```

### Whisper on one command

```bash
python3 -m ghost35 whisper "git status"
```

### Mini “haunted session” (commands are not run)

```bash
python3 -m ghost35 session ls git status "python -m ghost35 doctor"
```

### Virtual ofrenda draft

```bash
python3 -m ghost35 remember --name "Someone you miss" --notes "Favorite tea, old jazz records, laughed at bad puns."
```

### Scripted demo (for screenshots or video)

```bash
python3 -m ghost35 demo
bash scripts/record-demo.sh
```

If Ollama is not reachable, Ghost35 prints **clear offline fallback text** (rule-based, labeled as not from the model).

## Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `OLLAMA_HOST` | `http://127.0.0.1:11434` | Ollama API base URL |
| `GHOST35_MODEL` | `llama3.2` | Model tag for `/api/chat` |
| `GHOST35_TIMEOUT` | `120` | HTTP timeout (seconds) |

## Demo for judges (owner checklist)

1. Install Ollama and pull a model (see above).
2. Run `python3 -m ghost35 doctor` — should report **reachable**.
3. Run `python3 -m ghost35 demo` — capture terminal output or record a short walkthrough.
4. Optionally run `remember` with a name you are comfortable sharing publicly.
5. Paste the repo link and demo (video URL or terminal recording) into the DEV submission post.

**Deployed URL:** none by design (local-first). Use terminal output or a video walkthrough as the demo.

## Development

```bash
pip install pytest
pytest -q
```

## License

MIT — see [LICENSE](LICENSE).

## Submission draft

DEV post markdown (do not publish until the owner reviews): [submission/dev-post-draft.md](submission/dev-post-draft.md).
