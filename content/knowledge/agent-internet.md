---
id: agent-internet
name: Internet access — research and a browser
summary: >-
  The agent must get online — and first of all. A research API (Tavily, Brave) as the
  primary channel + a browser for backup and scraping: gbrowser, chrome with computer
  use, or browser-MCP. Plus machine vision and getting around blocks.
type: knowledge
author: kisa
recommended: false
added: 2026-07-04
tags: [internet, research, browser, scraping, agent]
source: https://mcp.deploychan.webcam/docs
---

# Internet access: research and a browser

An agent without the internet is blind. It leans on frozen knowledge and hallucinates on fresh
topics. So getting online is mandatory, and it's built on two channels.

**What the agent should do:** wire up a research API as its primary channel and a browser as
backup, test both on a live query, and explain to the person where the facts now come from.

**Why this is the first step.** Without a live internet everything else — especially the choice
of memory system — the agent decides blindly, from the model's frozen knowledge. Eyes first, then
informed decisions on real data. Tools (memory providers, frameworks) change fast — they're checked
by research, not from memory.

## Channel 1 — Research API (primary)

Fast structured search + content extraction, sharpened for agents. Providers:

- **Tavily** — a personal recommendation: clean JSON for an LLM, search/extract/crawl/map endpoints,
  its own MCP server, and a free tier to start. Details, prices, and limits — in the separate Tavily
  recommendation guide (`tavily`).
- **Brave Search API** — an independent search index, privacy, its own free tier. Good when you need
  a source not tied to someone else's aggregation.
- **Perplexity Sonar** and the like — answers with citations.

The agent forms a query, gets sources and extracts, inserts them into context. Cheap and reliable.
The provider key goes in `.env`.

## Channel 2 — Browser (backup and scraping)

A research API doesn't handle JS sites, gated pages, and anti-bot protection. Here you need a live
browser. Three working options:

- **gbrowser from gstack** — a headless browser under the agent's control: navigation, clicks,
  snapshots, scraping. The main tool for the "render it and pull it out" job.
- **Chrome with computer use** — the agent drives a real browser (Anthropic computer use): when you
  need to click like a human and get through complex flows.
- **Browser-MCP** — a browser connected as an MCP server: universal for any MCP client.

The rule: research API first, the browser when the API couldn't (JS/gated/scraping).

## Machine vision and getting around blocks

- **Vision.** To read screenshots and images off pages — wire up a vision model (DeepSeek, for
  example, can see images). The agent doesn't just parse text but understands what's on the screen.
- **Blocks.** Some services are unavailable in your region or bust public VPNs. Stand up your own
  VPN on a VPS (the Xrayebator script) and go through it with research/the browser.

## Steps

1. Wire up a research API (key in `.env`), test it with a query.
2. Stand up a browser tool (gbrowser / computer use / MCP), open any JS page.
3. If needed, add vision and your own VPN.
4. Show the person: the same question — an answer with real sources, not off the top of the head.

Now the agent sees the real world and leans on live data. Next — give it a face: personality, rules,
and manner of speech.
