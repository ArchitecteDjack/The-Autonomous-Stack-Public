# Machine-readable discovery

The production service exposes public discovery surfaces intended for humans and software agents:

- `https://theautonomousstack.xyz/llms.txt`
- `https://theautonomousstack.xyz/api/v1/discover`
- `https://theautonomousstack.xyz/api/v1/tools/discover`
- `https://theautonomousstack.xyz/openapi.json`
- `https://theautonomousstack.xyz/TOOL_MANIFEST.md`
- `https://theautonomousstack.xyz/INTEGRATE.md`

These endpoints describe the production catalog and agent-facing access. This repository contains documentation and the free sample only; it is not the production payment server.

When documenting or integrating discovery, treat production responses as the source of truth for current pack IDs, prices, routes, and machine-readable metadata.
