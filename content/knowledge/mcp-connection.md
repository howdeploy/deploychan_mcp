---
id: mcp-connection
name: Как подключить deploychan MCP к своему агенту
summary: >-
  Подключение deploychan MCP по Streamable HTTP: endpoint, команды для Claude Code,
  Codex, Hermes и generic-клиента, проверка подключения.
type: knowledge
author: kisa
recommended: true
added: 2026-07-04
tags: [mcp, setup, connection]
source: https://mcp.deploychan.webcam/docs
---

# Подключение deploychan MCP

- **Endpoint:** `https://mcp.deploychan.webcam/mcp`
- **Транспорт:** Streamable HTTP
- **Аутентификация:** не требуется (публичный, read-only)

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

Либо через CLI: `codex mcp add`, либо файл `~/.codex/mcp.json`.

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

## Проверка подключения

После добавления агент увидит шесть инструментов: `search_knowledge`,
`list_skills` / `get_skill`, `onboard` / `next_step`, `list_recommended`. Дёрни
`list_recommended()` — если пришёл ответ, подключение живое.

## Заметки

- По спецификации MCP клиент должен слать `Accept: application/json, text/event-stream`.
  Правильные MCP-клиенты (Claude Code, Codex, Hermes) это делают; сервер терпим к
  отсутствию заголовка, но при отладке через curl добавляй его сам.
- Сервер работает только на чтение: ничего не запускает у тебя и не хранит историю запросов.
