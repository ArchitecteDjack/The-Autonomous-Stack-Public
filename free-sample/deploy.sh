#!/usr/bin/env bash
# Compatibility entrypoint: install.sh owns the one-shot Debian deployment.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
bash "$SCRIPT_DIR/install.sh" "$@"
