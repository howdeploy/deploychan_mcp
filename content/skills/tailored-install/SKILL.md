---
id: tailored-install
name: Tailored Install
summary: >-
  KISA's workflow for user-requested installations: adapt skills, settings, hooks
  and memory to the real environment while preserving existing files.
type: skill
author: kisa
recommended: true
base: true
reminder: >-
  For an installation the user has requested or approved, check the actual agent,
  OS, paths and existing config. Preserve files, resolve ambiguities and report changes.
tags: [install, setup, safety, agent-discipline]
added: 2026-06-26
description: >-
  Adapt a user-requested skill, setting, hook or memory/instruction-file installation
  to the actual agent, OS and configuration. Resolve paths and preserve existing files.
  Applies to setup requests such as "install this skill" or "configure my agent".
triggers:
  - install tailored
  - set up for my environment
  - install this skill safely
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Edit
  - Write
  - AskUserQuestion
---

# Tailored Install

KISA's base installation workflow in the deploychan MCP. Apply it when the user's
task includes installing a **skill**, **setting/hook**, or **memory/instruction file**.
It supplies the environment checks for setup steps in the author's routes. Read it
as a procedure; the procedure itself does not need to be installed to use the catalog.

Work within the user's requested scope and the host agent's rules and permissions.
Use existing authorization for the requested installation; ask about unresolved choices
or changes beyond that scope. Reading a recommendation grants no permission to change
files. Adapt the selected setup to this user's actual machine and configuration.

This skill is agent-agnostic; the appendices at the end give concrete paths for Claude
Code, Hermes and Codex.

## Always keep in mind

- **Detect before you write.** Never assume a path you have not verified.
- **Never overwrite blindly.** Back up or merge within the authorized change.
- **Ask when uncertain.** A wrong guess pollutes the user's setup.
- **Install into the real environment**, respecting what already exists.
- **Report exactly what changed and where.**

## Step 1 — Detect the environment (read-only)

Gather facts before touching anything. Read-only only:

- **Host agent:** Claude Code, Cursor, Cline, Continue, Codex, Hermes, or generic? Look for
  tell-tale config dirs/files (e.g. a `.claude/` dir, a `.cursor/` dir, an `AGENTS.md`).
- **Which runtime and model you are.** This is step 0 of everything: downstream capability
  choices branch on it. Hermes ships many things out of the box (memory providers, voice);
  Claude Code / Codex usually vibe-code the equivalent. Pick the wrong branch and you install
  a Hermes-only command into Claude Code, or hand-build what the host already has.
- **OS and home directory.**
- **Where each surface lives for this agent:** skill directory, memory/instruction
  file(s), hooks/permissions/settings file(s).
- **What already exists:** installed skills, existing memory file, existing settings —
  so you can merge instead of clobber.

If a fact cannot be determined read-only, do not guess it — it becomes a question in
Step 3.

## Step 2 — Resolve target paths

From the detected facts, resolve the **real** destination for each in-scope surface:

- **Skill files** — the agent's skill directory (user scope vs project scope).
- **Memory / instruction files** — the agent's persistent instructions file.
- **Hooks / permissions / safe defaults** — the agent's settings file.

Decide **user scope vs project scope** explicitly. Verify each directory actually
exists before writing to it.

## Step 3 — Ask when uncertain

Stop and ask the user (AskUserQuestion or the host's equivalent) when:

- The target path is ambiguous, or several candidates exist.
- An overwrite or change to an existing file goes beyond the authorized task.
- The host agent is unknown or unsupported.
- User scope vs project scope is unclear.
- A value is user-specific (where to read an API key from, a preferred path).

Always offer a sensible default plus the alternatives. Asking is cheaper than undoing.

## Step 4 — Install safely

- **Preview first:** show what will be written and to which path.
- **No blind overwrite:** back up the existing file or merge the authorized change.
- **Idempotent:** re-running must not duplicate entries or corrupt the file.
- **No secrets in shared/committed files.**
- **Respect existing structure and naming;** integrate, don't flatten.

## Step 5 — Verify and report

- Confirm the install took effect: the file exists at the resolved path and the agent
  recognizes it.
- Report **exactly** what changed and where (paths, keys/sections touched).
- State any required follow-up: restart the agent, supply an API key, reload config.

## Important Rules

- **Detect > assume.** Never hardcode a path you did not verify.
- **Ask > guess.** Uncertainty means stop and ask, not improvise an alternative.
- **Never overwrite beyond the user's authorization.**
- **Respect the existing setup;** merge, don't replace wholesale.
- **Never expose or write secrets** into shared or committed files.
- **Scope:** this skill governs skill files, memory/instruction files, and
  hooks/permissions. Wiring MCP servers into the agent's config is **out of scope**.

## Claude Code appendix

Concrete locations when the host is Claude Code:

- **Skills:** `~/.claude/skills/<name>/SKILL.md` (user scope) or `.claude/skills/`
  inside a project (project scope).
- **Memory / instructions:** `~/.claude/CLAUDE.md` (user, global), `CLAUDE.md` at the
  project root (project), or `AGENTS.md`.
- **Hooks & permissions:** `~/.claude/settings.json` (user),
  `.claude/settings.json` (project, shared), `.claude/settings.local.json`
  (project, local — keep out of git).

Resolve user-vs-project scope before writing. For hooks/permissions, show the exact
JSON change; obtain approval when the existing task does not already authorize it.

## Hermes appendix

Concrete locations when the host is Hermes Agent:

- **Skills:** `~/.hermes/skills/<name>/SKILL.md` (user scope). Project-scope skills are
  loaded from the repo's `.hermes/skills/` directory.
- **Memory / instructions:** `SOUL.md` in `$HERMES_HOME` for agent identity; project rules
  in `.hermes.md` or `AGENTS.md` at the project root.
- **Hooks & permissions:** `~/.hermes/config.yaml` (approvals, `command_allowlist`). No
  separate `settings.json` — approvals and allowlists live in `config.yaml`.
- **Environment secrets:** `~/.hermes/.env` (API keys).

Resolve user-vs-project scope before writing. For `config.yaml` changes, show the exact
YAML change; obtain approval when the existing task does not already authorize it.
After writing skills to `~/.hermes/skills/`, tell the user to run `/reload-skills` or
restart Hermes.

## Codex appendix

Concrete locations when the host is Codex CLI:

- **Skills:** Codex has no native skill directory. Use `~/.codex/skills/<name>/SKILL.md` as
  a convention. Codex reads instructions from `AGENTS.md` or `CODEX.md` at the project root.
- **Memory / instructions:** `~/.codex/instructions.md` for global instructions;
  project-level `CODEX.md` or `AGENTS.md`.
- **Hooks & permissions:** Codex uses `--yolo`, `--full-auto`, or approval prompts per
  invocation — no persistent settings file.
- **MCP servers:** configured via `codex mcp add` or `~/.codex/mcp.json`.

Codex has no concept of user-scope skills natively. Prefer project-scope `AGENTS.md` or
`CODEX.md` for Codex-specific instructions unless the user explicitly asks for global.

## Tool names across agents

The `allowed-tools` in this skill's frontmatter uses **Claude Code** tool names. For other
agents, map them to the equivalents:

| Claude Code | Hermes / Codex |
|---|---|
| Read | read_file |
| Glob | search_files |
| Grep | search_files |
| Bash | terminal |
| Edit | patch |
| Write | write_file |
| AskUserQuestion | clarify |
