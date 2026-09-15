# Architecture

The public Free Sample Agent is intentionally small and inspectable.

```text
CLI input
  ↓
file-backed JSON task queue
  ↓
agent loop
  ├─ deterministic transform
  └─ optional BYO-LLM CLI reasoning
  ↓
structured result
  ↓
atomic queue update
```

The deterministic core supports `upper`, `lower`, `reverse`, and `wordcount`. Optional reasoning is delegated to an already-installed Claude Code, Kimi Code, or Codex CLI through `llm_adapter.py`; if no supported CLI is available, the agent falls back to deterministic behaviour.

The public repository is deliberately separate from The Autonomous Stack production backend. Payment infrastructure, private deployment configuration, premium packs, credentials, and internal services are not part of this repository.
