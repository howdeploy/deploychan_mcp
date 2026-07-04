---
id: tavily
name: Tavily — a research API for agents
summary: >-
  KISA's personal pick: Tavily as the main research API for your agent. What it is,
  the endpoints, its own MCP server, current prices and limits (credit model), how to
  connect, and where to save.
type: tool
author: third_party
recommended: true
added: 2026-07-04
tags: [research, tavily, api, search, tool, internet]
source: https://docs.tavily.com/documentation/api-credits
---

# Tavily — a research API for agents

Personal recommendation: if your agent needs one main channel to the internet — take
**Tavily**. It's a search API tuned for LLMs: it returns not raw HTML but clean, structured
sources and extracts that drop straight into context. Native integration with LangChain,
LlamaIndex, function calling — and its own MCP server, so it connects to Claude Code, Cursor,
Windsurf with almost no code.

> The prices and limits below are from the official page `docs.tavily.com/documentation/api-credits`
> at the time of writing (2026-07). Pricing changes — check their site before paying.

## What it can do (endpoints)

- **Search** — web search, clean JSON for LLMs. The primary tool.
- **Extract** — pull content from specific URLs.
- **Crawl** — traverse a site per instructions and gather pages.
- **Map** — build a site map (the link structure).
- **Research** — a ready-made research task (a deep pass).

SDKs: Python (`pip install tavily-python`, `from tavily import TavilyClient`) and
JavaScript (`npm i @tavily/core`). A key of the form `tvly-...` goes in `.env`
(`TAVILY_API_KEY`), not in a shared committed file.

## Credit model

You pay not per request but per **credit**. The cost of a request depends on the endpoint and the depth:

- **Search:** basic — 1 credit, advanced — 2 credits.
- **Extract:** ~1 credit per 5 URLs (basic), ~2 credits per 5 URLs (advanced).
- **Crawl:** mapping + extraction (e.g. 10 pages basic ≈ 3 credits).
- **Research:** dynamic — `model=mini` 4–110 credits, `model=pro` 15–250 per request.

## Pricing

| Plan | Credits/mo | Price | Per credit |
|---|---|---|---|
| Researcher | 1 000 | Free | — |
| Project | 4 000 | $30 | $0.0075 |
| Bootstrap | 15 000 | $100 | $0.0067 |
| Startup | 38 000 | $220 | $0.0058 |
| Growth | 100 000 | $500 | $0.005 |
| Pay-as-you-go | as used | $0.008 / credit | $0.008 |
| Enterprise | custom | custom | custom |

## Limits

- **Free:** 1 000 credits per month, **no card**. Resets on the 1st of each month.
  For a personal agent and development this is usually enough.
- **Rate limit:** there's a per-minute request limit (429 when exceeded) — add retries with
  exponential backoff. The exact RPM depends on whether it's a dev or prod key; check the
  Rate Limits page in their docs.
- The pricier the plan, the lower the per-credit price and the higher the limits.

## How to connect

1. Sign up at `tavily.com`, grab a `tvly-...` key (no card needed).
2. Put `TAVILY_API_KEY` in `.env`.
3. Either install the SDK (`pip install tavily-python`) or connect the **Tavily MCP server** to
   your client (Claude Code / Cursor / Windsurf) — then search becomes a native tool for the agent.
4. Verify with a live request: the same question — an answer with real sources.

## How to save

- Keep `search` on `basic` (1 credit), bump to `advanced` (2) only when basic falls short.
- `Research` is expensive (up to 250 credits) — call it deliberately, not for every little thing.
- Cache responses to repeated queries so you don't burn credits for nothing.

Tavily is the main research channel from the "Getting online" guide. The browser (gbrowser /
computer use / MCP) stays as a backup for JS sites and gated pages.
