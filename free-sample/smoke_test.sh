#!/usr/bin/env bash
# smoke_test.sh — run the offline test suite (deterministic, no API keys).
set -euo pipefail
cd "$(dirname "$0")"
PY="python3"
[ -x venv/bin/python ] && PY="venv/bin/python"
"$PY" test_agent.py
