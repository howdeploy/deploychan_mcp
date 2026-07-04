---
id: gstack
name: 'gstack: a working loop for Claude Code (+ gbrowser)'
summary: >-
  gstack — Garry Tan's open-source kit: mode-skills for Claude Code (planning,
  review, QA, ship) on top of the persistent headless browser gbrowser (/browse). What it
  is, how to install it, the key commands. Honestly: it's a Claude Code kit, not a
  multi-agent system.
type: tool
author: third_party
recommended: false
added: 2026-07-04
tags: [gstack, gbrowser, claude-code, workflow, qa, browser]
source: https://github.com/garrytan/gstack
---

# gstack: a working loop for Claude Code (+ gbrowser)

gstack (`garrytan/gstack`, MIT) isn't a new model or an agent framework — it's a **workflow
layer for Claude Code**. It packages software delivery into a set of mode-skills: planning,
review, QA, ship, browser, retro. The idea — give Claude Code explicit roles
(CEO / designer / eng-manager / release-manager / QA) instead of one blurry system prompt.

**An honest caveat about multi-agent.** gstack is Claude-Code-native: it installs into
`~/.claude/skills/`, reads `CLAUDE.md`, and its commands run as Claude Code slash-skills. It
is NOT a multi-agent tool. Inside there's `/codex` (delegate a task to Codex) and gbrain
(cross-machine memory), but the loop itself is built for Claude Code. I'm presenting it
as-is, without artificially "making it multi-agent".

## gbrowser — the persistent browser (`/browse`)

The main technical component. gstack keeps a **long-lived headless Chromium** over localhost
HTTP: cookies, tabs, `localStorage`, and login state survive between commands. The agent logs
in, clicks around the app, takes screenshots, inspects breakages. This is the very browser
that's handy for rendering out JS pages and scraping (channel 2 from the `agent-internet` guide).

`/qa` is built on top: it analyzes the branch diff → finds the affected routes → tests
exactly those against the local app. Not a separate manual run, but QA tied to the changes in the code.

## Install

```bash
git clone --single-branch --depth 1 https://github.com/garrytan/gstack ~/.claude/skills/gstack
cd ~/.claude/skills/gstack && ./setup
```

Then add a `## gstack` section to `CLAUDE.md` (use `/browse` for the web + the list of
skills). Without this section, Claude may "not see" the skills.

## Key skills

- **Planning/strategy:** `/office-hours` (product ideas), `/plan-ceo-review` (scope),
  `/plan-eng-review` (architecture), `/plan-design-review`, `/autoplan` (the whole review pipeline).
- **Code/bugs:** `/review` (diff before merge), `/investigate` (bugs, "why it broke").
- **QA/browser:** `/browse` (open/test a site), `/qa` (test by diff), `/qa-only` (report
  only), `/design-review` (visual audit of a live site).
- **Ship:** `/ship` (PR/deploy), `/land-and-deploy` (merge + deploy + verify), `/canary`.
- **Misc:** `/codex` (delegate to Codex), `/learn`, `/retro`, `/document-*`.

Routing lives in `CLAUDE.md`: a request matches to a skill (bug → `/investigate`, "does this work"
→ `/qa`, review → `/review`, ship → `/ship`).

## Why this is in deploychan

For the consumer agent, the main thing from gstack is **gbrowser**: a persistent browser for
QA and scraping JS pages (that same "channel 2" from the `agent-internet` guide). The rest of
the skills are a working-loop methodology for Claude Code: explicit roles instead of one
prompt, QA tied to the diff, ship in one command.
