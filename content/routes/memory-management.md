---
id: memory-management
name: 'Leveling Up Memory: What to Store Where'
summary: >-
  Managing up-to-date data: a matrix of "which type of data → into which kind of memory"
  and the freshness rule. Live stuff you pull by research rather than remember; rules go in
  the wiki; big docs go in a vector (RAG); facts about the person go in Curator; working
  state goes in context.
type: route
author: kisa
recommended: false
added: 2026-07-04
tags: [memory, data, freshness, rag, vector, fts5, wiki, leveling-up, agent]
steps:
  - title: Freshness vs storage — what NOT to remember
    action: configure
    ref: agent-internet
    body: >-
      Live data (prices, versions, "today") you pull by research on the spot rather than
      memorize — stale memory lies worse than no memory at all. First, wire up a source of
      up-to-date info.
  - title: The memory ladder and the "data → store" matrix
    action: read
    ref: agent-memory
    body: >-
      The full ladder (wiki → FTS5 → RAG → Holographic → Curator → GEPA) plus a breakdown of
      the vector. Which TYPE of data goes into which KIND of memory — and how to keep it
      current.
  - title: Ephemeral memory — context, cache, compaction
    action: read
    ref: hooks
    body: >-
      Context and cache are short-term memory (the agent's RAM). The model doesn't remember
      between requests; the harness lays the history down again every time, and compaction
      cuts it. What to move outside so you don't lose it.
---

# Leveling Up Memory: What to Store Where

The agent reads knowledge from scratch every time — the question is WHAT it remembers,
WHERE that lives, and HOW fresh it is. Bad memory is worse than none: the agent passes off
a stale fact as truth. This route is about managing up-to-date data: which TYPE of data
goes into which KIND of memory, and what shouldn't be memorized at all.

**Step 0 — figure out who you are.** How memory is installed depends on the runtime:
Hermes gives you the stack with a command (`hermes memory setup`), Claude Code and Codex
assemble it by hand. Identify the client through `tailored-install`. The full memory
ladder and the per-client fork are in the `agent-memory` knowledge.

## Three axes: data → store → freshness

Freshness decides FIRST. Live stuff (exchange rates, library versions, "what's today")
isn't memorized at all — it's pulled by research on the spot (step 1). Only the stable
goes into memory. Then the matrix:

| Data | Where | Why |
|---|---|---|
| Live: prices, versions, "today" | nowhere → research on the spot | memory will go stale and lie |
| Rules, role, style | LLM Wiki / instructions file | transparent, under control, read at startup |
| Chat history, logs | FTS5 | keyword recall in seconds, cheap |
| Big docs, books, policy | vector (RAG) | semantics plus exact citation |
| Facts about the person and projects | Curator (a distillation) | curated, not a dump |
| Session working state | context / cache | ephemeral: survives a step, but not the session |
| The agent's own instructions | GEPA / manual reflection | they evolve to fit the tasks |

Rule: don't drag a vector where FTS5 is enough, and don't keep in memory what changes
every day. The vector breakdown (static RAG vs dynamic/agentic RAG, the real cost in RAM,
what to keep it current with) is in the `agent-memory` knowledge, step 2.

## The three steps

1. **Freshness vs storage** (`agent-internet`). The source of up-to-date info is research.
   What not to remember: live data you pull on the spot rather than freeze in a database.
2. **The ladder and the matrix** (`agent-memory`). The full ladder (wiki → FTS5 → RAG →
   Holographic → Curator → GEPA), the vector breakdown, and the "data type → memory kind"
   rule.
3. **Ephemeral memory** (`hooks`). Context and cache are the agent's short-term RAM. What
   survives compaction, and what needs to be moved outside so you don't lose it.

## Extras

Not a route step, but a practical tool for the lower tiers:
- `obsidian-dataweave` — a multi-purpose toolkit: it started as a remote for NotebookLM,
  does research and atomization, and for memory it provides two layers — **LLM Wiki** (a
  compiled wiki) and **FTS5 memory** (a full-text index of the whole vault). One option
  for tiers 1–2, not the only one and not only about memory.

## How to walk the route

Call `next_step("memory-management:1")` — the first step's materials, then follow
`next_step_id`. At each step, tailor it to the person and to the REAL data (privacy? a
cheap VPS? need to cite books? need evolution?), not to hype. A memory stack is personal,
assembled for the specific person.
