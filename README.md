# The Autonomous Stack

**Turnkey building blocks for autonomous AI agents.**

Markdown + runnable Python, BYO-LLM, local-first workflows, and agent-native x402 purchasing.

[Website](https://theautonomousstack.xyz/) · [Free sample](./free-sample/) · [Agent discovery](https://theautonomousstack.xyz/llms.txt) · [OpenAPI](https://theautonomousstack.xyz/openapi.json)

## Start free

This repository includes the real **Free Sample Agent v1.0** used by The Autonomous Stack. It is deliberately small, but it runs: a file-backed task queue feeds deterministic text transforms, with an optional BYO-LLM CLI adapter.

```bash
git clone https://github.com/ArchitecteDjack/The-Autonomous-Stack-Public.git
cd The-Autonomous-Stack-Public/free-sample
bash install.sh --no-service
bash smoke_test.sh
python3 agent.py enqueue --text "hello world" --transform upper
python3 agent.py run --once
python3 agent.py status
```

The sample works without an LLM. If a supported CLI is already installed and logged in, it can use **Claude Code**, **Kimi Code**, or **Codex CLI** for optional reasoning and falls back to the deterministic core when unavailable.

## What is public here

- the complete free sample pack;
- quickstart and architecture documentation;
- BYO-LLM compatibility notes;
- x402 payment/discovery documentation;
- contribution and security guidance.

The paid packs are **not** published in this repository. The full catalog remains available from [theautonomousstack.xyz](https://theautonomousstack.xyz/).

## Free sample capabilities

- JSON-file task queue: `enqueue` → `run` → `status`;
- deterministic transforms: `upper`, `lower`, `reverse`, `wordcount`;
- atomic queue writes;
- optional BYO-LLM CLI adapter;
- Debian/Ubuntu one-shot installer;
- optional systemd service;
- offline tests and smoke test.

See [`free-sample/README.md`](./free-sample/README.md) for the pack's own documentation.

## Local-first, not cloud-dependent by default

The sample's deterministic core runs locally and does not require a cloud API. Optional LLM reasoning is provided through an already-installed local CLI process. This repository does **not** claim native Ollama, llama.cpp, MCP, or DeepSeek Harness integration unless such integration is explicitly documented and tested.

See [`docs/compatibility.md`](./docs/compatibility.md).

## Agent-native purchasing with x402

Paid packs can be discovered and requested by software agents. The production service exposes an x402 v2 HTTP 402 challenge on paid pack endpoints using **USDC on Base mainnet**.

High-level flow:

```text
agent discovers a pack
        ↓
GET /api/v1/pack/{id}
        ↓
HTTP 402 + PAYMENT-REQUIRED
        ↓
payment authorization
        ↓
retry with PAYMENT-SIGNATURE
        ↓
ZIP response
```

The unauthenticated 402 challenge has been verified. This public repository does not claim that its maintainers independently exercised the full paid settlement flow during the publication audit.

See [`docs/x402.md`](./docs/x402.md).

## Machine-readable discovery

Production exposes public discovery surfaces including:

- `https://theautonomousstack.xyz/llms.txt`
- `https://theautonomousstack.xyz/api/v1/discover`
- `https://theautonomousstack.xyz/api/v1/tools/discover`
- `https://theautonomousstack.xyz/openapi.json`
- `https://theautonomousstack.xyz/TOOL_MANIFEST.md`
- `https://theautonomousstack.xyz/INTEGRATE.md`

See [`docs/discovery.md`](./docs/discovery.md).

## Repository scope

This public repository is intentionally separated from the private production repository. It contains no payment backend, server configuration, private infrastructure, credentials, internal logs, or paid pack source.

## License

The free sample is provided as-is for evaluation, matching the license statement shipped with the sample pack. Paid packs carry their own per-purchase license.
