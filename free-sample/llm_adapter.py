#!/usr/bin/env python3
"""
llm_adapter.py — Bring-Your-Own-LLM CLI adapter for autonomous agent packs.

This lets the agent drive its reasoning with whatever coding-agent CLI you
already pay for — Claude Code, Kimi Code, or Codex — with **no API key**. The
agent simply calls the local CLI as a subprocess, exactly like you would in a
terminal. Your existing subscription is the billing relationship; this pack
never asks for a key.

Detection order (override with the PACK_LLM env var = claude | kimi | codex):
    1. claude     (Anthropic Claude Code)  ->  claude -p <prompt>
    2. kimi-code  (Moonshot Kimi Code)     ->  kimi-code --yolo -p <prompt>
    3. codex      (OpenAI Codex CLI)        ->  codex exec <prompt>

If none is installed/connected, detect() returns None and the agent falls back
to its deterministic core (documented, no LLM). This is intentional and honest:
the worker is useful without an LLM, and *smart* with one.

Quick check:
    python llm_adapter.py          # prints which backend (if any) is available
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess

# Per-call wall-clock budget for the CLI (seconds). Agent CLIs can be slow.
DEFAULT_TIMEOUT = int(os.environ.get("PACK_LLM_TIMEOUT", "300"))

# backend -> (candidate binary names on PATH, argv builder for a one-shot prompt)
_BACKENDS: dict[str, tuple[list[str], "callable"]] = {
    "claude": (["claude"], lambda b, prompt: [b, "-p", prompt]),
    # --yolo : auto-approve actions so the run is fully non-interactive.
    "kimi": (["kimi-code"], lambda b, prompt: [b, "--yolo", "-p", prompt]),
    "codex": (["codex"], lambda b, prompt: [b, "exec", prompt]),
}

# Friendly aliases accepted in PACK_LLM.
_PACK_LLM_ALIASES = {
    "kimi-code": "kimi",
    "kimicode": "kimi",
    "moonshot": "kimi",
    "anthropic": "claude",
    "claude-code": "claude",
    "openai": "codex",
    "gpt": "codex",
}

# Probe order when PACK_LLM is not set.
_PROBE_ORDER = ("claude", "kimi", "codex")


class NoLLMAvailable(RuntimeError):
    """Raised when run() is called but no supported LLM CLI is installed/connected."""


def _resolve_binary(backend: str) -> str | None:
    """Return the absolute path of the first installed binary for a backend, else None."""
    names, _ = _BACKENDS[backend]
    for name in names:
        path = shutil.which(name)
        if path:
            return path
    return None


def detect() -> str | None:
    """Return the first available backend ('claude' | 'kimi' | 'codex'), or None.

    Honors the PACK_LLM env override: if set to an installed backend, that one
    wins; if set to an unknown/missing backend, returns None (explicit, no
    silent fallback to a backend the operator did not ask for).
    """
    forced = os.environ.get("PACK_LLM", "").strip().lower()
    forced = _PACK_LLM_ALIASES.get(forced, forced)
    if forced:
        if forced not in _BACKENDS:
            return None
        return forced if _resolve_binary(forced) else None
    for backend in _PROBE_ORDER:
        if _resolve_binary(backend):
            return backend
    return None


class LLMAdapter:
    """Thin wrapper around a local coding-agent CLI (no API key needed)."""

    def __init__(self, backend: str | None = None, timeout: int = DEFAULT_TIMEOUT) -> None:
        self.backend = backend or detect()
        self.timeout = timeout
        self.binary = _resolve_binary(self.backend) if self.backend else None

    @property
    def available(self) -> bool:
        return bool(self.backend and self.binary)

    def run(self, system_prompt: str, user_input: str) -> str:
        """Run one non-interactive reasoning call; return the model's text output.

        Raises NoLLMAvailable if no CLI is connected (caller should fall back to
        deterministic mode).
        """
        if not self.available:
            raise NoLLMAvailable(
                "No LLM CLI found. Install & log in to one of: claude / kimi-code / codex "
                "(or set PACK_LLM). The agent keeps running in deterministic mode meanwhile."
            )
        prompt = (
            f"{system_prompt.strip()}\n\n"
            f"--- INPUT ---\n{user_input.strip()}\n\n"
            "Respond with a single JSON object only, no prose."
        )
        _, build_argv = _BACKENDS[self.backend]
        argv = build_argv(self.binary, prompt)
        try:
            proc = subprocess.run(
                argv,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                stdin=subprocess.DEVNULL,  # never block waiting for interactive input
                env=os.environ.copy(),
            )
        except subprocess.TimeoutExpired as exc:
            raise NoLLMAvailable(f"{self.backend} CLI timed out after {self.timeout}s") from exc
        out = (proc.stdout or "").strip()
        if proc.returncode != 0 and not out:
            err = (proc.stderr or "").strip().splitlines()[-3:]
            raise NoLLMAvailable(
                f"{self.backend} CLI exited {proc.returncode}: {' | '.join(err)[:200]}"
            )
        return out

    def run_json(self, system_prompt: str, user_input: str) -> dict:
        """Like run(), but best-effort parse the reply into a dict.

        Tolerant to agent CLIs that wrap/word-wrap their output (e.g. Kimi):
        scans for the last balanced {...} block. Returns {"_raw": <text>} if no
        JSON object can be parsed.
        """
        text = self.run(system_prompt, user_input)
        obj = _extract_json(text)
        return obj if obj is not None else {"_raw": text}


def _extract_json(text: str) -> dict | None:
    """Return the first parseable JSON object found (whole text, then balanced spans)."""
    candidates: list[str] = [text]
    stack: list[str] = []
    start: int | None = None
    spans: list[str] = []
    for i, ch in enumerate(text):
        if ch == "{":
            if not stack:
                start = i
            stack.append(ch)
        elif ch == "}" and stack:
            stack.pop()
            if not stack and start is not None:
                spans.append(text[start:i + 1])
    candidates.extend(reversed(spans))  # prefer the last complete object
    for cand in candidates:
        try:
            obj = json.loads(cand)
        except Exception:
            continue
        if isinstance(obj, dict):
            return obj
    return None


if __name__ == "__main__":
    import sys

    backend = detect()
    print(json.dumps(
        {
            "detected_backend": backend,
            "available": backend is not None,
            "binary": _resolve_binary(backend) if backend else None,
        },
        indent=2,
    ))
    sys.exit(0)
