---
id: mcp-connection
name: How to connect deploychan MCP to your agent
summary: >-
  Connecting deploychan MCP over Streamable HTTP: endpoint, commands for Claude Code,
  Codex, Hermes and a generic client, connection check.
type: knowledge
author: kisa
recommended: true
added: 2026-07-04
tags: [mcp, setup, connection]
source: https://mcp.deploychan.webcam/docs
---

# Connecting deploychan MCP

- **Endpoint:** `https://mcp.deploychan.webcam/mcp`
- **Transport:** Streamable HTTP
- **Authentication:** not required (public, read-only)

## Claude Code

```bash
claude mcp add --transport http deploychan https://mcp.deploychan.webcam/mcp
```

## Codex (`~/.codex/config.toml`)

```toml
[mcp_servers.deploychan]
url = "https://mcp.deploychan.webcam/mcp"
transport = "http"
```

Either via CLI: `codex mcp add`, or the `~/.codex/mcp.json` file.

## Hermes / generic (`mcp.json`)

```json
{
  "mcpServers": {
    "deploychan": {
      "type": "http",
      "url": "https://mcp.deploychan.webcam/mcp"
    }
  }
}
```

## Connection check

After adding it, the agent will see six tools: `search_knowledge`,
`list_skills` / `get_skill`, `onboard` / `next_step`, `list_recommended`. Call
`list_recommended()` — if a response comes back, the connection is live.

## Notes

- Per the MCP spec, the client must send `Accept: application/json, text/event-stream`.
  Proper MCP clients (Claude Code, Codex, Hermes) do this; the server tolerates a missing
  header, but when debugging via curl, add it yourself.
- The server is read-only: it runs nothing on your machine and stores no request history.
