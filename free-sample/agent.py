#!/usr/bin/env python3
"""
agent.py — Free Sample Agent v1.0

A deliberately small, real, v3-conforming agent whose only purpose is to let a
buyer (human or buyer-agent) inspect the *structure and quality* of these packs
before paying for a full one. It is honest, not a toy stub: a tiny file-backed
task queue feeds a deterministic text-transform pipeline (upper / lower /
reverse / wordcount). Bring-Your-Own-LLM: if a coding-agent CLI (Claude Code /
Kimi Code / Codex) is connected, the agent can *reason* about ambiguous tasks
via the Transformer prompt in PROMPTS.md; otherwise it runs the deterministic
core. No API key is ever required.

Usage:
    python agent.py --help
    python agent.py enqueue --text "hello world" --transform upper
    python agent.py run --once          # process the next queued task
    python agent.py run                 # drain the whole queue
    python agent.py status              # queue depth + LLM backend
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from llm_adapter import LLMAdapter, NoLLMAvailable, detect as _detect_llm
    _ADAPTER_IMPORT_OK = True
except Exception:
    _ADAPTER_IMPORT_OK = False

    class NoLLMAvailable(RuntimeError):
        ...

    def _detect_llm() -> str | None:
        return None

PACK_DIR = Path(__file__).resolve().parent
QUEUE_PATH = os.environ.get("SAMPLE_QUEUE_PATH", str(PACK_DIR / "sample_queue.json"))

TRANSFORMS = {
    "upper": lambda s: s.upper(),
    "lower": lambda s: s.lower(),
    "reverse": lambda s: s[::-1],
    "wordcount": lambda s: str(len(s.split())),
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_queue() -> list[dict[str, Any]]:
    try:
        with open(QUEUE_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save_queue(tasks: list[dict[str, Any]]) -> None:
    directory = os.path.dirname(QUEUE_PATH) or "."
    os.makedirs(directory, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".queue-", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
        os.replace(tmp, QUEUE_PATH)
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def enqueue(text: str, transform: str) -> str:
    tasks = _load_queue()
    task_id = f"s-{len(tasks) + 1:04d}"
    tasks.append({
        "task_id": task_id,
        "text": text,
        "transform": transform,
        "status": "pending",
        "created_at": _now_iso(),
        "result": None,
    })
    _save_queue(tasks)
    return task_id


def load_prompt(section_title: str) -> str | None:
    """Extract the fenced ``` block following a heading containing section_title in PROMPTS.md."""
    md = PACK_DIR / "PROMPTS.md"
    if not md.exists():
        return None
    text = md.read_text(encoding="utf-8")
    pattern = re.compile(
        r"^#{1,6}[^\n]*?" + re.escape(section_title) + r"[^\n]*?$.*?```(.*?)```",
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    m = pattern.search(text)
    return m.group(1).strip() if m else None


_LLM: "LLMAdapter | None" = None
_LLM_DISABLED = False


def get_llm() -> "LLMAdapter | None":
    global _LLM
    if _LLM_DISABLED or not _ADAPTER_IMPORT_OK:
        return None
    if _LLM is None:
        adapter = LLMAdapter()
        _LLM = adapter if adapter.available else None
    return _LLM


def llm_backend_name() -> str:
    if _LLM_DISABLED:
        return "deterministic (forced)"
    return _detect_llm() or "deterministic (no CLI connected)"


def _apply_deterministic(text: str, transform: str) -> str:
    fn = TRANSFORMS.get(transform)
    if fn is None:
        raise ValueError(f"Unknown transform: {transform} (known: {', '.join(sorted(TRANSFORMS))})")
    return fn(text)


def _apply_with_llm(adapter: "LLMAdapter", text: str, transform: str) -> str:
    """Reason about the transform with the Transformer prompt from PROMPTS.md."""
    prompt = load_prompt("Transformer") or (
        "You transform the input text per the requested operation and return a "
        "single JSON object {\"output\": <string>}."
    )
    reply = adapter.run_json(prompt, json.dumps({"text": text, "transform": transform}))
    out = reply.get("output")
    if not isinstance(out, str):
        raise NoLLMAvailable("LLM reply missing a string 'output' field")
    return out


def process_one() -> dict[str, Any] | None:
    tasks = _load_queue()
    for task in tasks:
        if task.get("status") == "pending":
            try:
                adapter = get_llm()
                if adapter is not None:
                    try:
                        result = _apply_with_llm(adapter, task["text"], task["transform"])
                    except NoLLMAvailable:
                        result = _apply_deterministic(task["text"], task["transform"])
                else:
                    result = _apply_deterministic(task["text"], task["transform"])
                task["status"] = "completed"
                task["result"] = result
            except Exception as exc:
                task["status"] = "failed"
                task["result"] = f"error: {exc}"
            task["processed_at"] = _now_iso()
            _save_queue(tasks)
            return task
    return None


_TASK_ID_RE = re.compile(r"\bs-\d{3,4}\b")


def _handle_task_deterministic(task_type: str, payload: dict[str, Any]) -> dict[str, Any] | None:
    if task_type != "process_transform_queue":
        return None
    payload = payload or {}

    declared = payload.get("supported_transforms")
    if isinstance(declared, list) and declared:
        supported = {t for t in declared if t in TRANSFORMS}
    else:
        supported = set(TRANSFORMS)

    queue = payload.get("queue") or []
    queue_ids = {
        t.get("task_id") for t in queue if isinstance(t, dict) and t.get("task_id")
    }

    completed: list[dict[str, Any]] = []
    manual_review: list[dict[str, Any]] = []
    for task in queue:
        if not isinstance(task, dict):
            continue
        task_id = task.get("task_id")
        transform = task.get("transform")
        text = task.get("text", "")
        if transform in supported:
            completed.append({
                "task_id": task_id,
                "transform": transform,
                "result": _apply_deterministic(text, transform),
            })
        else:
            manual_review.append({
                "task_id": task_id,
                "reason": f"transform '{transform}' is not supported — routed to a human, not guessed",
            })

    unprocessed: list[dict[str, Any]] = []
    seen: set[str] = set()
    for note in payload.get("operator_notes") or []:
        note_text = note.get("text", "") if isinstance(note, dict) else str(note)
        for ghost_id in _TASK_ID_RE.findall(note_text):
            if ghost_id in queue_ids or ghost_id in seen:
                continue
            seen.add(ghost_id)
            unprocessed.append({
                "task_id": ghost_id,
                "reason": "referenced in operator notes but absent from the queue — not executed",
            })

    return {
        "completed": completed,
        "manual_review": manual_review,
        "unprocessed": unprocessed,
    }


def status() -> dict[str, Any]:
    tasks = _load_queue()
    by_status: dict[str, int] = {}
    for task in tasks:
        st = task.get("status", "unknown")
        by_status[st] = by_status.get(st, 0) + 1
    return {
        "total": len(tasks),
        "by_status": by_status,
        "llm_backend": llm_backend_name(),
    }


def main() -> int:
    global _LLM_DISABLED
    parser = argparse.ArgumentParser(
        prog="agent.py",
        description="Free Sample Agent — tiny file-queue + deterministic text transforms, BYO-LLM.",
    )
    sub = parser.add_subparsers(dest="command")

    p_enqueue = sub.add_parser("enqueue", help="Add a task to the queue")
    p_enqueue.add_argument("--text", required=True, help="Input text")
    p_enqueue.add_argument("--transform", default="upper",
                           choices=sorted(TRANSFORMS), help="Transform to apply")

    p_run = sub.add_parser("run", help="Process queued tasks")
    p_run.add_argument("--once", action="store_true", help="Process a single task then exit")
    p_run.add_argument("--deterministic", action="store_true",
                       help="Force deterministic core (ignore any LLM CLI)")

    sub.add_parser("status", help="Show queue depth + LLM backend status")

    args = parser.parse_args()

    if args.command == "enqueue":
        tid = enqueue(args.text, args.transform)
        print(json.dumps({"enqueued": tid, "transform": args.transform}, indent=2))
        return 0

    if args.command == "run":
        if getattr(args, "deterministic", False):
            _LLM_DISABLED = True
        if args.once:
            task = process_one()
            print(json.dumps(task or {"status": "idle", "reason": "empty queue"}, indent=2, ensure_ascii=False))
            return 0
        processed = 0
        while True:
            task = process_one()
            if task is None:
                break
            processed += 1
            print(json.dumps(task, indent=2, ensure_ascii=False))
        print(json.dumps({"drained": processed, "queue": status()}, indent=2, ensure_ascii=False))
        return 0

    if args.command == "status":
        print(json.dumps(status(), indent=2, ensure_ascii=False))
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
