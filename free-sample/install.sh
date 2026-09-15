#!/usr/bin/env bash
#
# install.sh — one-shot installer for the Free Sample Agent on a Debian/Ubuntu VM.
#
#   sudo bash install.sh            # full: system deps + venv + systemd service
#   bash install.sh --no-service    # venv only (run the agent by hand)
#
# Bring-Your-Own-LLM: if you have a Claude Code / Kimi Code / Codex CLI logged in,
# the agent can reason with it (no API key). Otherwise it runs a deterministic
# core. The installer is idempotent — safe to re-run.
#
set -euo pipefail

PACK_DIR="$(cd "$(dirname "$0")" && pwd)"
PACK_ID="$(basename "$PACK_DIR")"
SERVICE_NAME="$PACK_ID"
WITH_SERVICE=1
[ "${1:-}" = "--no-service" ] && WITH_SERVICE=0

RUN_USER="${SUDO_USER:-$(id -un)}"
RUN_HOME="$(getent passwd "$RUN_USER" 2>/dev/null | cut -d: -f6)"
[ -z "${RUN_HOME:-}" ] && RUN_HOME="$HOME"

echo "== ${PACK_ID} installer =="
echo "Pack dir : $PACK_DIR"
echo "User     : $RUN_USER (home: $RUN_HOME)"

# 1) System dependencies (idempotent). Needs root for apt; degrade gracefully.
if command -v apt-get >/dev/null 2>&1; then
  if [ "$(id -u)" = "0" ]; then
    apt-get update -qq || true
    apt-get install -y -qq python3 python3-venv python3-pip >/dev/null
    echo "system deps ready (python3, venv, pip)"
  else
    echo "not root — skipping apt; ensure python3-venv & python3-pip are installed"
  fi
fi

# 2) Virtualenv + Python deps
if [ ! -d "$PACK_DIR/venv" ]; then
  python3 -m venv "$PACK_DIR/venv"
fi
"$PACK_DIR/venv/bin/pip" install --upgrade pip -q
"$PACK_DIR/venv/bin/pip" install -r "$PACK_DIR/requirements.txt" -q
echo "venv ready"

# Resolve the runnable entrypoint from the pack manifest (defaults to agent.py).
ENTRY="$("$PACK_DIR/venv/bin/python" -c \
  "import json,sys;print(json.load(open(sys.argv[1])).get('code_entrypoint') or 'agent.py')" \
  "$PACK_DIR/${PACK_ID}.json" 2>/dev/null || echo agent.py)"
[ -f "$PACK_DIR/$ENTRY" ] || ENTRY="agent.py"

# 3) Detect a connected LLM CLI
BACKEND="$("$PACK_DIR/venv/bin/python" "$PACK_DIR/llm_adapter.py" 2>/dev/null \
  | python3 -c 'import sys,json;print(json.load(sys.stdin).get("detected_backend") or "")' 2>/dev/null || true)"
if [ -n "$BACKEND" ]; then
  echo "LLM backend detected: $BACKEND — the agent can reason with your subscription"
else
  cat <<'EOF'
No LLM CLI detected — the agent runs in deterministic mode (fully functional).
   To enable LLM reasoning, install & log in to ONE of these (no API key needed):
     - Claude Code : npm i -g @anthropic-ai/claude-code  &&  claude     (/login)
     - Kimi Code   : https://platform.moonshot.ai         &&  kimi-code
     - Codex CLI   : npm i -g @openai/codex               &&  codex login
   Then re-run this installer, or set PACK_LLM=claude|kimi|codex.
EOF
fi

# 4) systemd service (root + systemctl required). This sample runs a single drain
#    pass and exits (Type=oneshot) — it is a demonstrator, not a long-lived daemon.
if [ "$WITH_SERVICE" = "1" ] && command -v systemctl >/dev/null 2>&1 && [ "$(id -u)" = "0" ]; then
  UNIT="/etc/systemd/system/${SERVICE_NAME}.service"
  cat > "$UNIT" <<EOF
[Unit]
Description=Free Sample Agent (${PACK_ID})
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=${RUN_USER}
WorkingDirectory=${PACK_DIR}
Environment=PATH=${RUN_HOME}/.local/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=${PACK_DIR}/venv/bin/python ${PACK_DIR}/${ENTRY} run

[Install]
WantedBy=multi-user.target
EOF
  systemctl daemon-reload
  systemctl enable "$SERVICE_NAME"
  echo "service '${SERVICE_NAME}' installed (run: systemctl start ${SERVICE_NAME})"
else
  echo "systemd step skipped (need root + systemctl, or --no-service). Run manually:"
  echo "   ${PACK_DIR}/venv/bin/python ${PACK_DIR}/agent.py run"
fi

echo "== Done =="