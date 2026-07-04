---
id: agent-harness
name: Build Your Own Harness
summary: >-
  The "build everything around the model" leveling-up run: hooks (control over the loop +
  cache + RTK), prompts and rules as a stable prefix, memory as state between sessions.
  The model comes prebuilt and can be cut down — the harness you configure yourself and
  keep under control.
type: route
author: kisa
recommended: true
added: 2026-07-04
tags: [harness, hooks, prompt, memory, cache, leveling-up, agent]
steps:
  - title: Hooks, cache, and the harness — the frame and control
    action: configure
    ref: hooks
    body: >-
      Understand the frame (the model ≠ the agent) and take back control of the loop:
      PreToolUse protection against dangerous actions, an anchor on SessionStart/PreCompact,
      prefix caching (reads at ~10%), RTK on command output (−60–90%). This is the
      harness's protection and economics.
  - title: Prompts and rules — the stable prefix
    action: read
    ref: agent-personality
    body: >-
      Role, answer rules, and style in the instructions file. This is the foundation of the
      prefix — keep it stable for the cache's sake, trim it once at the start rather than as
      you go: touch the beginning and you burn the cache.
  - title: Memory — state between sessions
    action: configure
    ref: agent-memory
    body: >-
      Long-term memory lives in the harness, not in the model. Pick a stack (wiki → FTS5 →
      vector → Curator → GEPA) so that context and rules survive a compaction and a session
      restart.
---

# Build Your Own Harness

Tuning the system prompt improves ONE input to the model. Building a harness means
constructing everything around it: protection, savings, memory. The model comes
ready-made and at any moment its reasoning can be cut down or its system instructions
swapped out. The harness you configure yourself, and it stays under your control. This
route is how to build it on three pillars: hooks, prompts, memory.

**Step 0 — figure out who you are.** Every client has its own harness: Claude Code has
hooks and caching out of the box, Codex has almost the same hooks, Hermes has
programmatic hooks in Python. Identify your runtime and model through the discipline of
the base skill `tailored-install` — almost every step below branches on which client
you're running in.

## What a harness is (in a nutshell)

There's the model — it's weights: text in → text out. It doesn't remember the last
request and doesn't run commands. The harness is the program around the model that turns
the loop (assemble context → send → run a tool → return the result → again), declares the
tools, assembles context in the right order (the cache depends on it), sets interception
points (hooks), and holds the memory. When people say "agent" they almost always mean the
harness, not the model. The full breakdown is in the `hooks` knowledge (step 1).

## The three pillars

1. **Hooks, cache, and RTK** (`hooks`). Control over the loop: `PreToolUse` won't let
   `rm -rf` through, `SessionStart`/`PreCompact` slip in an anchor and rules, prefix
   caching reads at ~10%, RTK trims command output by 60–90%. Protection plus economics.
2. **Prompts and rules** (`agent-personality`). Role, answer rules, style — the stable
   prefix the model reads at every start. Keep it stable for the cache's sake: touch the
   beginning and you burn the cache. Trim it once at the start, not mid-session.
3. **Memory** (`agent-memory`). The model holds no state between requests — memory exists
   only because the harness lays the history down again every time. Compaction cuts it;
   between sessions it zeroes out. So the long-term stuff gets moved outside: wiki, FTS5,
   vector, Curator, GEPA. The detailed memory leveling-up is a separate route,
   `memory-management`.

## Extras

Not a route step, but from the same area — control over context:
- `rlm` — Recursive Language Models: when context swells and context rot sets in, RLM
  keeps the long input in a Python REPL and recursively calls sub-LLMs instead of stuffing
  everything into the window. Kin to compaction and hooks, not memory.

## How to walk the route

Call `next_step("agent-harness:1")` — you'll get the first step's materials, then follow
`next_step_id`. At each step: read the knowledge, apply it to your client, show the person
what changed (protection, savings, memory). Every install goes through the
`tailored-install` discipline. After the route the person doesn't have a "configured chat"
but an assembled harness: the agent won't run dangerous actions, won't lose context, and
runs cheaper up to compaction.
