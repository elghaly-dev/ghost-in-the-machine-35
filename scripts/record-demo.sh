#!/usr/bin/env bash
# Optional: record a terminal demo for the DEV post (owner runs locally).
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m ghost35 demo
python3 -m ghost35 remember --name "Grandma's radio" --notes "She hummed along to static between stations."
