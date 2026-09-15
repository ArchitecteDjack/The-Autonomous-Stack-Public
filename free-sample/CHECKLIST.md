# CHECKLIST — Free Sample Agent v1.0

> Minimal deploy checklist for the free sample agent.

- [ ] 1. Check Python version
      `python3 --version  # >= 3.10`

- [ ] 2. Install (one-shot)
      `sudo bash install.sh`   (or `bash install.sh --no-service`)

- [ ] 3. Run the offline test suite
      `bash smoke_test.sh`   (or `python3 test_agent.py`)

- [ ] 4. Enqueue a task
      `python3 agent.py enqueue --text "hello world" --transform upper`

- [ ] 5. Process the queue
      `python3 agent.py run --once`

- [ ] 6. Check queue status + LLM backend
      `python3 agent.py status`

- [ ] 7. (Optional) Connect a BYO-LLM CLI
      `claude` / `kimi-code` / `codex`, or set `PACK_LLM`

- [ ] 8. (Optional) Customize a transform
      see `CUSTOMIZE.md`
