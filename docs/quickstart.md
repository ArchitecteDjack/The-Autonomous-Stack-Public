# Quickstart

## Free Sample Agent

```bash
git clone https://github.com/ArchitecteDjack/The-Autonomous-Stack-Public.git
cd The-Autonomous-Stack-Public/free-sample
bash install.sh --no-service
bash smoke_test.sh
```

Then enqueue and run a task:

```bash
python3 agent.py enqueue --text "hello world" --transform upper
python3 agent.py run --once
python3 agent.py status
```

Expected result: the task is completed and returns `HELLO WORLD`.

The default path is deterministic and does not require an API key. If Claude Code, Kimi Code, or Codex CLI is already installed and authenticated, `llm_adapter.py` can use it for optional reasoning.

For a systemd installation on Debian/Ubuntu, review the installer first and then run:

```bash
sudo bash install.sh
```

The included service is a oneshot demonstrator, not a permanently running production daemon.
