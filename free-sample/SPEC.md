# SPEC — Free Sample Agent v1.0

## Objective

Demonstrate the v3 "turnkey & honest" pack structure with a small, real agent: a
file-backed task queue feeding a deterministic text-transform pipeline.

---

## Configurable parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `SAMPLE_QUEUE_PATH` | env str | `sample_queue.json` | Path to the JSON queue file |
| `transform` | str | `upper` | Operation: `upper`, `lower`, `reverse`, `wordcount` |
| `PACK_LLM` | env str | auto-detected | Force a BYO-LLM CLI: `claude`, `kimi`, or `codex` |

---

## Interfaces

### Input

- CLI: `python agent.py enqueue --text "<string>" --transform <name>`.
- Queue file: a JSON array of task objects (`task_id`, `text`, `transform`, `status`).

### Output

- Structured JSON printed to stdout per processed task.
- The queue file updated atomically with each task's `status` and `result`.

---

## Dependencies

- Python >= 3.10.
- **No third-party packages — Python stdlib only.** The optional LLM is your own
  CLI (Claude Code / Kimi Code / Codex), called as a subprocess via
  `llm_adapter.py` — no SDK, no API key.
- systemd (optional, one-shot unit included).

---

## Security

- No network calls in the deterministic core.
- No secrets stored; BYO-LLM uses your already-authenticated CLI.
- Queue writes are atomic (temp file + `os.replace`).

---

## Scope (honest)

This is a **free sample**. It shows how the paid packs are built; it is not a
full business product. The paid packs add real domain logic, richer queues
(SQLite, retries, dead-letter, cron), and complete prompt libraries.
