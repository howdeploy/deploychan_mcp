---
id: tailored-install
name: Tailored Install
summary: >-
  Install skills, settings, hooks and memory tailored to THIS user's environment:
  detect context, respect existing files, ask before overwriting.
type: skill
author: kisa
recommended: true
base: true
reminder: >-
  Before installing anything, detect the user's actual environment (agent, OS, paths,
  existing config). Never overwrite blindly. Ask when uncertain. Report what changed.
tags: [install, setup, safety, agent-discipline]
added: 2026-06-26
description: >-
  Use BEFORE installing any skill, setting, hook, or memory/instruction file into a
  user's setup. Detects the target environment, resolves real paths, asks when unsure,
  installs idempotently without overwriting, and verifies. Use when: "install this
  skill", "set this up for me", "add this to my agent", "configure my agent".
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

The base skill of the deploychan MCP. Whenever you (a connected agent) are about to
install a **skill**, **setting/hook**, or **memory/instruction file** for a user, run
this discipline first. It is the implicit **step 0 of every leveling-up route**:
"install X" always means "install X tailored to THIS user's machine" — not into a
template, not into assumed paths.

This skill is agent-agnostic; a Claude Code appendix at the end gives concrete paths.

## Always keep in mind

- **Detect before you write.** Never assume a path you have not verified.
- **Never overwrite blindly.** Back up or merge, then confirm.
- **Ask when uncertain.** A wrong guess pollutes the user's setup.
- **Install into the real environment**, respecting what already exists.
- **Report exactly what changed and where.**

## Step 1 — Detect the environment (read-only)

Gather facts before touching anything. Read-only only:

- **Host agent:** Claude Code, Cursor, Cline, Continue, or generic? Look for tell-tale
  config dirs/files (e.g. a `.claude/` dir, a `.cursor/` dir, an `AGENTS.md`).
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
- An existing file would be overwritten or its meaning changed.
- The host agent is unknown or unsupported.
- User scope vs project scope is unclear.
- A value is user-specific (where to read an API key from, a preferred path).

Always offer a sensible default plus the alternatives. Asking is cheaper than undoing.

## Step 4 — Install safely

- **Preview first:** show what will be written and to which path.
- **No blind overwrite:** back up the existing file or merge into it, then confirm.
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
- **Never overwrite without explicit confirmation.**
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

Confirm user-vs-project scope before writing. For hooks/permissions, show the exact
JSON change and confirm before applying.
