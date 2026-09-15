---
title: "CUSTOMIZE - Plug in your own transform"
tags: [customize, sample, quickstart]
---

# CUSTOMIZE.md — Plug in your own work

This free sample ships four demo transforms (`upper`, `lower`, `reverse`,
`wordcount`). Here is where you plug in *your* logic — in about 5 minutes.

## Option A — deterministic transform (no LLM, full control)

1. Open `agent.py`, find the `TRANSFORMS` dict near the top.
2. Add your own entry mapping a name to a function:
   ```python
   TRANSFORMS["slugify"] = lambda s: "-".join(s.lower().split())
   ```
3. Enqueue and run it:
   ```bash
   python agent.py enqueue --text "Hello World" --transform slugify
   python agent.py run --once
   ```

## Option B — let the LLM do the work (bring-your-own CLI)

1. Connect a CLI once (`claude` / `kimi-code` / `codex`) — see README. No API key.
2. Edit the **Transformer** prompt in `PROMPTS.md` to describe your operation and
   the fields it may use. `agent.py` loads it automatically (`load_prompt`).
3. Enqueue any task — the LLM reads the input and returns the result. If no CLI
   is connected, the deterministic core (Option A) runs instead.

## Try it

```bash
python agent.py enqueue --text "hello world" --transform upper
python agent.py run --once
python agent.py status
```

Your agent runs with your data in 5 minutes.
