---
id: agentation
name: 'Agentation: visual feedback for your agent'
summary: >-
  Agentation is an agent-agnostic visual feedback tool: click an element on the
  page, write a note, get the exact selector/position/component tree, and hand it to
  any agent (Claude Code, Codex, Cursor…) or via MCP. Requires only React ≥ 18. Kills
  the guess-which-element game.
type: tool
author: third_party
recommended: true
added: 2026-07-04
tags: [agentation, visual-feedback, react, agent, design]
source: https://www.agentation.com
---

# Agentation: visual feedback for your agent

Editing design blind is Russian roulette: "the blue button in the sidebar" — and the agent
guesses. Agentation turns a click on an element into **structured context** the agent
understands precisely. You click an element on your running page, write a note — and the
agent gets:

- the **CSS selector** you can `grep` the codebase with;
- the **source file path** — the agent jumps straight to the right line;
- the **React component tree** — it understands the hierarchy;
- the **computed styles** — it understands the current look;
- **your note** with intent and priority.

Instead of "the blue button in the sidebar" you give `.sidebar > button.primary` — and the agent hits the mark.

## Agent-agnostic — this isn't a Claude Code thing

Straight from the repo: Agentation is an **agent-agnostic visual feedback tool**. The output
pastes into **Claude Code, Codex, Cursor, or any AI tool** with access to your codebase. Two
delivery methods:

1. **Copy-paste** — hit "copy", the structured markdown flies to your clipboard, paste it
   into your agent's chat.
2. **MCP** — connect the Agentation MCP server and no copy-paste needed: the agent sees what
   you're pointing at itself. Say "fix note 3" and it picks it up.

## Requirement — React ≥ 18 only

The only hard requirement — the app must be on **React ≥ 18**. Any React stack works:
no-build (UMD), Vite, Next.js. The claim "works only with Next.js" is wrong — that's just one
option. The tool is desktop-only.

## Install (for your agent)

```bash
npx skills add benjitaylor/agentation
```
`skills` (`vercel-labs/skills`) installs the skill into **any of 70+ supported agents** — at
install time you pick YOURS (Claude Code / Codex / Cursor / Windsurf…), then the recommended
options and Yes. The skill pulls in and configures the utility itself. Running the skill in
your agent kicks off the install of the actual tool you'll be working with.

Tip: install the skill BEFORE you assemble your agent pipeline — otherwise the binding can
get lost, and you'll have to ask the agent to fix it separately.

## How to use

1. Start your web project (the agent can do it itself, or by hand).
2. In the bottom-right corner — the edit menu icon. Click to activate.
3. Hover over an element — you see the object's highlighted area.
4. Click the element → write a note → **Add**.
5. Hit "copy" → paste into the agent (or, with MCP, just "fix note N").

All changes on the site are visible in real time — you can pile up notes and polish every
pixel and every letter as much as you need. The gear opens settings (webhooks, note color) —
the defaults are usually enough.

## Example pipeline

Agentation fits well into multi-agent orchestration. An example role split (any agents — what
matters is that the "designer" has the agentation skill installed):

- **Architect agent** — studies the spec, asks questions, writes the architecture with comments.
- **Developer agent (full-stack)** — writes all the code.
- **Designer/QA agent** — debugs features, hunts bugs, and fixes the design through Agentation,
  getting exact selectors and positions.

This way every element is refined with precision, not by guesswork.

## Pitfalls

- **MCP isn't picked up until the agent restarts.** The agent will honestly warn you that it
  can't receive edits automatically until it's restarted.
- **Sometimes you need to tell it to apply an edit again** — otherwise, for example, text can
  "fly off" too far. Keep an eye on changes and check with the agent so there are no conflicts.
- Install the skill ahead of time (see above) so the feature doesn't "get lost" when assembling the pipeline.

The combo of "direct requests to the agent + precise pointers through Agentation" lets you
polish every element of the interface.
