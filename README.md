# NightWatch

By Wyndham Heaven (elghaly)

NightWatch is a local-first morning report tool, built for the Hacktoberfest Open-Source AI Challenge 2026, Week 4: "Ghost in the Machine".

While the owner sleeps, the Faithful Servant keeps watch over a server log file. Each morning it writes one short report with two clearly separated sections:

1. **Story — a tale (fiction).** A short ghost story woven from the night's log lines, written by a local open-weight model (Gemma 3 1B through Ollama).
2. **Facts — parsed from the log.** A plain summary of real parsed events: total lines, counts by level, and the top error lines.

## Honesty note

The story is fiction. The facts are parsed from the log lines. Fiction is never presented as fact: both sections carry their labels on every run.

## Privacy

Nothing leaves the machine. The only network call NightWatch makes is to a local Ollama server on localhost. No paid APIs, no accounts, no keys.

## Setup

Requires Python 3.10+ and Ollama.

```bash
pip install -r requirements.txt
ollama pull gemma3:1b
```

## Run

```bash
python main.py --once
```

By default it reads `data/sample_logs/` and writes `data/output/report.md`. Point it at your own file like this:

```bash
python main.py --once --logs path/to/night.log --out path/to/report.md
```

To run without a model (for a shape check only), set `NIGHTWATCH_MOCK_MODEL=1`. The story in that mode is a fixed placeholder tale, still labeled fiction.

## Tests

```bash
python -m pytest
```

Tests mock the model call; no Ollama server is needed for them.

## Home

https://github.com/elghaly-dev/ghost-in-the-machine-35

Made with our Faithful Servant and checked by a human.
