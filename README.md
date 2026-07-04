# deploychan MCP

Public remote-MCP server that packages **KISA's curated vibe-coding experience** —
knowledge, ready-made skills, leveling-up routes and recommendations — and serves it to any
coding agent over one URL.

- **Endpoint:** `https://mcp.deploychan.webcam/mcp`
- **Transport:** Streamable HTTP · **Access:** public, read-only, no login, no keys
- **License:** MIT · everything (site, server, database) is open source

> Point your agent at the endpoint and it gets `search_knowledge`, `list_skills`,
> `get_skill`, `onboard`, `next_step`, and `list_recommended`.

## Connect

**Claude Code**
```bash
claude mcp add --transport http deploychan https://mcp.deploychan.webcam/mcp
```

**Codex** (`~/.codex/config.toml`)
```toml
[mcp_servers.deploychan]
url = "https://mcp.deploychan.webcam/mcp"
transport = "http"
```

**Hermes / generic** (`mcp.json`)
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

## What the agent gets

| Facet | Tools | What it returns |
|---|---|---|
| Knowledge | `search_knowledge(query)` | Relevant fragments from KISA's notes and guides. |
| Skills | `list_skills()` · `get_skill(id)` | Ready-made packs: steps, config, checklist. |
| Leveling up | `onboard(goal)` · `next_step(step_id)` | An ordered route for a goal; materials per step. |
| Recommended | `list_recommended()` | KISA's curated cross-type picks. |

## Self-hosting

The whole thing is open source. Run your own instance — locally or on a VPS — with your own
content.

```bash
git clone https://github.com/howdeploy/deploychan_mcp
cd deploychan_mcp
docker compose up -d --build
# -> your MCP: http://localhost:8080/mcp
```

The server binds to loopback (`127.0.0.1:8080`) on purpose — put a reverse proxy (TLS +
rate-limiting) in front for a public deployment.

## Content

All content is hand-curated markdown with YAML frontmatter under `content/`:

```
content/skills/<id>/SKILL.md   # installable skill pack
content/knowledge/<id>.md      # a note / guide (full-text searchable)
content/routes/<id>.md         # a leveling-up route (ordered steps)
content/tools/<id>.md          # guide for installing a third-party tool
content/meta.yml               # endpoint, connect snippets, profile
```

`ingest` loads `content/` into SQLite + FTS5 and generates `web/catalog.json` for the site:

```bash
python -m server.ingest
```

Search is full-text only (FTS5) — offline, no embeddings, no API keys. Everything in
`content/` is public; never put private data there.

## Development

```bash
pip install -e ".[dev]"
python -m server.ingest      # build the DB + catalog
pytest                        # run the tests
python -m server.app          # serve locally at http://localhost:8080/mcp
```

## Security

Read-only by design: the server serves content and runs nothing on your machine. No login,
no keys, no request-history storage. Skills are shell commands and configs the agent runs
**on your machine** — read what a skill does before you approve it, and treat third-party
skills as untrusted code.
