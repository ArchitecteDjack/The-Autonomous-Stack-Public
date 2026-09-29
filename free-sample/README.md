# Free Sample Agent v1.0

> A free, deliberately minimal — but **real** — agent so you can inspect the
> quality and structure of these packs before buying a paid one. It runs, it
> processes a queue, it produces output. Offline by default, smarter with a
> BYO-LLM CLI.

---

## Why this pack exists

Every paid pack here follows the same "v3 turnkey & honest" standard. This free
sample lets you (or your buyer-agent) **see that standard in action** — the file
layout, the BYO-LLM adapter, the install script, the offline tests — without
paying. What you inspect here is what you get, scaled up, in the paid packs.

It is honest about being small: a tiny file-backed task queue feeding a
deterministic text-transform pipeline. No fake claims, no hidden API keys.

---

## What it does

- A JSON-file task queue (`enqueue` → `run` → `status`).
- Four deterministic transforms: `upper`, `lower`, `reverse`, `wordcount`.
- Optional LLM reasoning via a connected CLI (Claude Code / Kimi Code / Codex),
  using the `Transformer` prompt in `PROMPTS.md`. No API key needed.
- Atomic queue writes (temp file + `os.replace`) — no partial writes on crash.

## What it does NOT do

- It is **not** a production business product — it is a structural sample.
- No PDF/DOCX/HTML conversion, no ERP/CRM connectors, no external network calls.

---

## Quickstart

```bash
# 1) Install (Debian/Ubuntu, one-shot)
sudo bash install.sh            # or: bash install.sh --no-service

# 2) Verify offline (no API keys)
bash smoke_test.sh

# 3) Use it
python3 agent.py enqueue --text "hello world" --transform upper
python3 agent.py run --once
python3 agent.py status
```

---

## LLM vs deterministic

| Mode | Needs a CLI? | Behaviour |
|------|--------------|-----------|
| Deterministic (default) | No | Applies the transform locally; always works. |
| BYO-LLM | Yes (claude/kimi/codex) | Reasons about the task via `PROMPTS.md`, falls back to deterministic if unavailable. |

Connect a CLI once and the agent gets smarter; without one it still works.
See `CUSTOMIZE.md` to plug in your own transforms or data.

---

## Files

- `agent.py` — entrypoint (queue + transforms + OODA-style cycle).
- `llm_adapter.py` — BYO-LLM CLI adapter (no API key).
- `PROMPTS.md` — the single `Transformer` prompt, loaded by `agent.py`.
- `install.sh` + `agent-sample-free-v1.service` — one-shot Debian install.
- `test_agent.py` / `smoke_test.sh` — offline test suite (exit 0, no keys).
- `CUSTOMIZE.md`, `SPEC.md`, `SOUL.md`, `CHECKLIST.md`, `CHANGELOG.md` — docs.

---

## License

Released under the MIT License. The paid packs carry their own per-purchase license.

```text
MIT License

Copyright (c) 2026 ArchitecteDjack

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
