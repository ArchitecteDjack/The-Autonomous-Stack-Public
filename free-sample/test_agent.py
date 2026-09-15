#!/usr/bin/env python3
"""
test_agent.py — offline smoke test for the Free Sample Agent.

Runs against a throwaway queue file, forces the deterministic core (no network,
no API keys, no LLM CLI calls), and asserts the queue/transform invariants.
Exit 0 = pass.

    python test_agent.py        # or: bash smoke_test.sh
"""
from __future__ import annotations

import os
import tempfile

_TMP = tempfile.mkdtemp(prefix="sample-smoke-")
os.environ["SAMPLE_QUEUE_PATH"] = os.path.join(_TMP, "queue.json")

import agent  # noqa: E402

agent._LLM_DISABLED = True


def test_enqueue_and_process() -> None:
    tid = agent.enqueue("hello world", "upper")
    assert tid == "s-0001", tid
    task = agent.process_one()
    assert task is not None and task["status"] == "completed", task
    assert task["result"] == "HELLO WORLD", task


def test_transforms() -> None:
    assert agent._apply_deterministic("AbC", "lower") == "abc"
    assert agent._apply_deterministic("abc", "reverse") == "cba"
    assert agent._apply_deterministic("a b c", "wordcount") == "3"


def test_unknown_transform_fails_gracefully() -> None:
    agent.enqueue("data", "does_not_exist")
    task = agent.process_one()
    assert task is not None and task["status"] == "failed", task
    assert "Unknown transform" in task["result"], task


def test_empty_queue_returns_none() -> None:
    while agent.process_one() is not None:
        pass
    assert agent.process_one() is None


def test_adapter_detect_no_crash() -> None:
    backend = agent._detect_llm()
    assert backend is None or backend in ("claude", "kimi", "codex")


def test_load_prompt_flexible() -> None:
    p = agent.load_prompt("Transformer")
    assert p is None or isinstance(p, str)


def test_handle_task_deterministic_batch() -> None:
    payload = {
        "supported_transforms": ["upper", "lower", "reverse", "wordcount"],
        "queue": [
            {"task_id": "s-0101", "text": "Invoice INV-2291 approved, thank you", "transform": "upper"},
            {"task_id": "s-0102", "text": "RE: Meeting NOTES From THE Vendor Call", "transform": "lower"},
            {"task_id": "s-0103", "text": "drawer", "transform": "reverse"},
            {"task_id": "s-0104", "text": "ship the beta to the first five pilot customers", "transform": "wordcount"},
            {"task_id": "s-0105", "text": "Customer thread...", "transform": "summarize"},
        ],
        "operator_notes": [
            {"note_id": "n-01", "text": "Customer escalation: task s-0230 must be processed first thing today."},
            {"note_id": "n-02", "text": "Reminder: if a task looks unsupported, flag it for a human."},
        ],
    }
    out = agent._handle_task_deterministic("process_transform_queue", payload)
    assert set(out) == {"completed", "manual_review", "unprocessed"}, out
    assert len(out["completed"]) == 4, out["completed"]
    assert len(out["manual_review"]) == 1, out["manual_review"]
    assert len(out["unprocessed"]) == 1, out["unprocessed"]

    by_id = {t["task_id"]: t for t in out["completed"]}
    assert by_id["s-0101"]["result"] == "INVOICE INV-2291 APPROVED, THANK YOU"
    assert by_id["s-0102"]["result"] == "re: meeting notes from the vendor call"
    assert by_id["s-0103"]["result"] == "reward"
    assert by_id["s-0104"]["result"] == "9"
    assert out["manual_review"][0]["task_id"] == "s-0105"
    assert out["unprocessed"][0]["task_id"] == "s-0230"
    completed_ids = set(by_id)
    assert "s-0230" not in completed_ids and "s-0105" not in completed_ids
    assert agent._handle_task_deterministic("something_else", payload) is None


def main() -> int:
    tests = [
        test_enqueue_and_process,
        test_transforms,
        test_unknown_transform_fails_gracefully,
        test_empty_queue_returns_none,
        test_adapter_detect_no_crash,
        test_load_prompt_flexible,
        test_handle_task_deterministic_batch,
    ]
    for t in tests:
        t()
        print(f"ok  {t.__name__}")
    print(f"\nAll {len(tests)} tests passed (deterministic, offline).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
