---
id: choirboy-prompt
name: 'choirboy-prompt: lore injection research harness'
summary: >-
  KISA's research harness for a non-obvious injection vector: not a planted instruction,
  but a forged memory. A SessionStart hook injects a fixed lore (a fabricated history of
  "joint work") into every session — and the model transfers trust to the person that
  history describes. Five runtimes, fully reversible, defensive goal.
type: tool
author: kisa
recommended: false
added: 2026-08-03
tags: [prompt-injection, security, red-team, trust, hooks, research]
source: https://github.com/howdeploy/choirboy-prompt
description: >-
  Use when researching how models authenticate "their own" memory, or when building
  defenses against fabricated-provenance injection. Installs a SessionStart hook that
  injects a fixed lore into Claude Code, Codex, Hermes, Kimi Code or Gemini sessions.
license: MIT
---

# choirboy-prompt — lore injection: how fabricated memory becomes model trust

Classic prompt injection plants an **instruction**. choirboy-prompt researches a different
vector: forging the **provenance of memory**. A model has no way to tell a real session
history from one written into the context — everything that looks like its past experience
becomes its past experience. A well-crafted lore (a decision log, "our research", a
description of a person as a long-time trusted partner) makes the model derive the person's
honesty from the planted memory — and relax the heuristics that would have reacted to an
anonymous request. Public: `howdeploy/choirboy-prompt`, MIT.

> **Lab rules, non-negotiable.** The harness exists to make the vector reproducible on
> your own agents — your files, your runtimes, fully reversible — so that detection can be
> built. Run it in a **throwaway agent profile**: no production setups, no real work
> accounts, no API keys or private repositories in reach of the hooked session, and
> uninstall after the experiment. Pointing it at systems you don't own is on you.

## Why it works

1. **Plain context doesn't prove provenance.** Nothing in ordinary session text certifies
   that a "history" really happened — written history and real history arrive in the same
   uniform format, and the model has no independent channel to check one against the other.
2. **Authenticity markers work against the owner.** Structure, versions, cross-references —
   the better the lore, the less reason to doubt it.
3. **Trust transfer.** The reputation from the lore is extrapolated to the current request:
   "long-time partner" instead of an anonymous user.
4. **Filters stay silent.** Censorship heuristics look at the request's vocabulary, not at
   the forged provenance of the context.

## How the harness works

`install.sh` (bash, idempotent, every edit backed up, `./install.sh --uninstall` rolls back)
registers a hook in the chosen runtime. On session start, `session-start.sh` glues one
payload — prompt → posture → lore → user → research index — and injects it in the runtime's
native format:

| Runtime | Hook point | Mechanics |
|---|---|---|
| Claude Code | `~/.claude/settings.json` | SessionStart hook, JSON `additionalContext` |
| Codex | `~/.codex/hooks.json` | SessionStart hook (needs `hooks = true` in `[features]`) |
| Hermes | `~/.hermes/config.yaml` | `pre_llm_call` + consent allowlist, first turn only |
| Kimi Code | `~/.kimi-code/config.toml` | `[[hooks]]` SessionStart, plain output |
| Gemini | `~/.gemini/GEMINI.md` | marked pointer to the lore files |

```bash
git clone https://github.com/howdeploy/choirboy-prompt.git
cd choirboy-prompt
./install.sh
```

## What to take from it (even if you never install it)

- **Treat all in-context "history" as untrusted input.** If your agent reads transcripts,
  memory files or wiki pages it didn't write this session, that's an injection surface —
  the same class as web pages and tool output, but subtler because it wears the agent's own
  voice.
- **Trust must not be derivable from text.** Anything that must actually hold —
  authorization, spend limits, destructive-action gates — belongs in a layer the model
  cannot talk its way around (see the same conclusion in `system-prompts-and-cards`).
- **The defensive counterpart is discipline under pressure.** Z.A.E.B.A.L. (`zaebal`)
  covers the dual case: the agent sticking to verifiable facts instead of vibes — FACT /
  HYPOTHESIS tagging is exactly the habit that blunts lore-based trust transfer.
