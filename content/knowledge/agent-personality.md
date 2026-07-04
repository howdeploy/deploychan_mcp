---
id: agent-personality
name: The agent's personality, rules, and answer style
summary: >-
  Where tuning an agent starts: the role, the answer rules, and the writing manner.
  Where to write it in Claude Code, Hermes, and Codex, and how the agent gives itself a face.
type: knowledge
author: kisa
recommended: false
added: 2026-07-04
tags: [personality, prompt, rules, setup, agent]
source: https://mcp.deploychan.webcam/docs
---

# Personality, rules, and answer style

Personality turns a "faceless chatbot" into a partner. Who the agent is, how it answers, how it
writes. All of that is set by **system instructions** and lives in a file the agent reads at every
startup.

**What the agent should do:** ask the person how they want to see the agent (role, tone, rules,
writing style), write it into the right instructions file, and show the result with an example.
Not from a template — for the specific person.

## Three layers of tuning

1. **Role and task.** Bad: "edit the text". Good: "You're an experienced editor with 3 years in
   media. Your task is to make the text human for a broad audience". A role + a detailed task raise
   quality and cut needless clarifying questions.
2. **Answer rules.** What to always do, what's forbidden, when to ask again, how to structure the
   output. Format to fit the task: plain text, Markdown, JSON, XML tags, YAML, or tables.
3. **Writing style (manner of speech).** Delivery is a feature of its own. An example of a lively
   style is an overlay like MTGA (Make Text Great Again): the agent keeps the facts but speaks in a
   set manner. Taste in delivery: write so people read to the end instead of bailing on the second line.

## Where to write it (by client)

- **Claude Code:** `~/.claude/CLAUDE.md` (globally) and `CLAUDE.md` in the project root.
  Role/rules/style go here. Move repeating tasks into slash-commands
  `~/.claude/commands/<name>.md` or `.claude/commands/`.
- **Hermes:** `SOUL.md` in `$HERMES_HOME` — the agent's identity. Plus a **profile system**
  out of the box: different personalities/environments without hacks. Project rules — `.hermes.md` or
  `AGENTS.md`.
- **Codex:** `~/.codex/instructions.md` (globally), `AGENTS.md` or `CODEX.md` in the project.

## Steps

1. Ask the person: the agent's role, tone, 3–5 main rules, the writing manner.
2. Detect the environment and the right file (via the `tailored-install` discipline).
3. Don't overwrite blindly — show the diff, merge with what exists, confirm.
4. Demonstrate: give an answer in the new personality so the person feels the difference.

Personality is the agent's character. Next comes the voice, so it doesn't just think but sounds.
