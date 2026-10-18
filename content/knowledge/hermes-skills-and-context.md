---
id: hermes-skills-and-context
name: Hermes skill writers, catalog structure and context ownership
summary: >-
  Trace every skill writer before reorganizing a Hermes library, fix conflicting
  foreground and background instructions, preserve procedural resources, repair
  category and index discovery, and distinguish identity, memory, project rules and wiki.
type: knowledge
author: kisa
recommended: false
added: 2026-10-18
tags: [hermes, skills, curator, background-review, memory, soul, agents, categories, context]
source: https://hermes-agent.nousresearch.com/docs/user-guide/features/skills
---

# Skill writers, structure and context ownership

Use this branch for spontaneous skill growth, repeated library rewrites, a misleading
skill index, missing procedures or conflicting instructions. Resolve the live profile
first through `hermes-runtime-and-upgrades`. Do not impose one installation's taxonomy,
count target or writing policy on every Hermes user.

## Diagnose the writer before cleaning the result

Several independent paths can change procedural content:

| Writer or mechanism | What to inspect |
|---|---|
| Main conversation | Skill-manager tool, terminal/file writes, skill-creation nudges and system guidance |
| Post-response review | Whether it requests skill changes, memory changes or both; which model/process runs it |
| Curator | Enabled/paused state, LLM consolidation and non-LLM archival separately |
| Install, seeding and import | Startup/update bundled seeding, external roots and extension-owned installation |
| Sync or proposal paths | Presence in this release, origin, load-time writes and automatic change proposals |
| Manual tooling or another process | CLI install, repository pulls and shared library writers |

Post-response review and periodic curator are different mechanisms. Disabling one
does not disable the other; disabling LLM consolidation may leave automatic archival
active. Memory review is another policy and need not be removed to stop skill changes.
Background duration after delivery cannot explain the user's preceding wait.

Source navigation in the v0.22.2-era layout: `agent/turn_finalizer.py`, `agent/curator.py`,
`agent/agent_init.py`, `run_agent.py`, `tools/skill_manager_tool.py`,
`tools/skill_provenance.py`, `tools/skills_tool.py`, and any still-present
`tools/skills_sync.py`. Follow current callers; removed subsystems should stay removed.

If the user chooses manual-only skill maintenance, enforce that policy across the
supported automatic entry points and the actual storage mutation boundary. Carry an
explicit operation origin across tool/worker boundaries; reject a background write
before mutation. Do not infer trusted origin from model-written text. Use native
settings when available; downstream flags such as a local `allow_automatic_writes`
extension are not guaranteed upstream configuration keys.

Retain ordinary skill reading and authorized foreground editing. A skill-tool guard
does not sandbox an agent's arbitrary terminal writes: document that boundary rather
than claiming filesystem immutability.

## Resolve the prompt contradiction at its owner

A common conflict combines a manual-only skill rule with unconditional guidance to
record every learned procedure or correction in a skill. Removing a background nudge
does not repair this foreground instruction.

Trace `agent/prompt_builder.py::build_memory_guidance`, `SKILLS_GUIDANCE` and the active
`agent/system_prompt.py` guidance assembly. Find every exported/cached variant and
which combinations of memory/profile/skill-manager availability load it. Change the
shared generator rather than adding a competing rule to every individual skill.

For manual-only policy, make creation, update and deletion conditional on the current
user task explicitly authorizing the change. Learning during an unrelated task is not
itself that authorization. Preserve the distinction between procedural knowledge and
compact cross-session facts. Read the generated guidance, then verify the relevant
session activation; source text alone is insufficient.

## Put information in the correct file

| Owner | Intended role | Delivery to verify |
|---|---|---|
| `$HERMES_HOME/SOUL.md` | Agent identity and communication style | Independent system-prompt identity source |
| `memories/USER.md` | Durable user-profile facts/preferences | Session memory snapshot |
| `memories/MEMORY.md` | Compact persistent facts and standing context | Session memory snapshot and configured budget |
| Project `.hermes.md` / `AGENTS.md` / compatibility file | Repository instructions, paths and conventions | Actual context-file precedence and discovery |
| `skills/.../SKILL.md` | Reusable task procedure with a clear trigger/outcome | Short discoverable index, then on-demand procedure |
| Skill references/scripts/assets | Conditional detail and executable/data resources | Read or execute only the relevant resource |
| Wiki or external knowledge store | Larger project history, agreements and research | Relevant retrieval; existence is not automatic prompt inclusion |
| Session history | Prior conversation and transient work | Targeted retrieval rather than permanent duplication |

Do not move personality or private relationship agreements into a procedural skill to
make them load everywhere. Do not use memory as a full manual, or assume every wiki
page is injected automatically. An absent AGENTS.md is not automatically damage:
check which context file the installed release actually selects. Do not recreate an
old file with guessed obligations. Current documentation describes precedence, but
verify the installed implementation and delivered prompt when diagnosing a conflict.

## Inventory before merging or removing skills

Build a local manifest of actual active roots, category directories, entry metadata,
archive markers, references, scripts, assets, aliases/bundles and scheduled callers.
Keep private contents out of public reports. Distinguish active entries from files in
backups, archives and plugin/vendor trees; raw SKILL.md count is not the active catalog.

For a category/index problem, inspect both the loader and renderer:

- In the baseline layout, a category can come from the relative directory path;
  root-level entries may appear as `general`. Adding an invented frontmatter field
  will not fix a renderer that does not read it.
- `DESCRIPTION.md` can label a category. Its existence, platform/tool requirements,
  disabled names, duplicate names and multiple roots all affect discovery.
- A running index cache and a session-pinned prompt are separate caches. Check the
  cross-process invalidation fix described in `hermes-runtime-and-upgrades` before
  inventing another cache workaround.
- Built-in seeding/import can restore unwanted root-level entries. Fix the responsible
  path or its selected configuration before repeating manual recategorization.

Uncategorized is not synonymous with useless. Missing usage telemetry is not proof
that a capability is unwanted. Ask about genuinely optional removals when intent is
unknown; preserve the procedure while awaiting that decision.

## Consolidate by retrieval need

Choose an entry boundary by compatible triggers and outcomes. Merge duplicate or
closely related workflows when one concise dispatcher can select the relevant detail.
Keep distinct outcomes separate when merging would make the trigger ambiguous. A
single catch-all skill and hundreds of tiny always-visible entries can both be costly.

Keep the entry short; move mode-specific procedures to referenced sections/files.
Do not preload every reference, copy a global checklist into every procedure, or add
mandatory delegation/research passes to simple work. Retain concrete requirements that
matter to the actual procedure.

Preserve supporting files by hash before/after relocation. Maintain an old-to-new map;
repair relative/absolute references, imports and script resource paths. Where the
runtime supports aliases/bundles, verify their resolution and scheduled/slash callers;
do not describe a downstream alias implementation as a stock Hermes feature. Do not
silently change automation prompts just to conceal a broken rename.

An archive placeholder is not a recovered procedure. Restore content from a verified
source when preservation is required. A pruning marker after context compression also
requires reloading the relevant original before relying on it.

## Measure and verify

Use the installed catalog tool and prompt renderer to measure unique visible names,
categories, description lengths and the **rendered** skills block. Description limits
are version/policy-specific; a local short cap is not a universal Hermes requirement.
Keep index size, total library bytes, loaded procedure bytes and full prompt tokens
separate. A smaller catalog does not by itself prove lower latency or cost.

Within the authorized verification scope, check policy across foreground/background
origins, preserved reading, disabled archival/seeding where requested, renamed callers
and a newly assembled prompt. Do not require a real model request or production write
merely to prove that a guard rejects a forbidden operation.

Further reading: [skills](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills),
[creating skills](https://hermes-agent.nousresearch.com/docs/developer-guide/creating-skills),
[file ownership](https://hermes-agent.nousresearch.com/docs/user-guide/which-file-does-what),
and [curator](https://hermes-agent.nousresearch.com/docs/user-guide/features/curator).
