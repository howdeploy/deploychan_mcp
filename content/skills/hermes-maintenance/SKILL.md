---
id: hermes-maintenance
name: Diagnose and repair Hermes Agent
summary: >-
  Route Hermes failures to the right repair: identify the running profile and release,
  resolve prompt and skill-writing conflicts, reduce catalog overhead without losing
  procedures, audit software execution and reported outcomes, repair checkpoint failures,
  and measure latency before tuning.
type: skill
author: kisa
recommended: false
added: 2026-10-18
tags: [hermes, maintenance, troubleshooting, skills, context, checkpoints, upgrades, performance, audit, logs]
source: https://github.com/NousResearch/hermes-agent
description: >-
  Use for diagnosing, repairing or optimizing a Hermes installation, especially after
  an update, skill-library changes, instruction conflicts, software failures or repeated
  checkpoint errors; also audit agent claims against retained tool and log evidence.
  Do not apply as a mandatory preflight for unrelated tasks performed by Hermes.
triggers:
  - repair Hermes skills or instruction conflicts
  - diagnose Hermes after an update
  - fix repeated Hermes checkpoint failures
  - investigate slow Hermes tasks
  - audit Hermes software launches and unreported failures
reminder: A changed file is not a changed running process or a refreshed conversation prompt; verify each relevant layer separately.
---

# Hermes maintenance

Work on the requested installation and symptom. An audit does not authorize changing
settings; a repair does not authorize deleting procedures, clearing conversations,
rewriting identity or disabling unrelated automation. Preserve existing authorization
and verification limits. This skill adds no requirement for extra agents or model calls.

## Select a branch

Retrieve only the relevant guide through this MCP's `get_item(item_id)`:

| Symptom | Item to retrieve |
|---|---|
| Wrong profile, stale code/prompt, update conflict or suspected bad commit | `hermes-runtime-and-upgrades` |
| Uncertain software availability, launch history, silent failures or unsupported agent claims | `hermes-runtime-and-upgrades` |
| Skills multiply, lose categories, disappear, or contradict memory/project instructions | `hermes-skills-and-context` |
| Checkpoint failures, missing paths, unexpected Git work or long task latency | `hermes-checkpoints-and-latency` |

For an ordered maintenance engagement, retrieve route `hermes-repair-and-optimization`
with `get_item`, or use `onboard` with a Hermes repair goal and follow its returned IDs.
Routes are optional navigation; a known fault can go directly to its branch.

## Shared procedure

1. Identify the live gateway, its checkout, interpreter, effective Hermes home, profile,
   working directory and terminal backend. Compare these with the files being inspected.
2. Preserve the exact failing operation and error. Distinguish a source defect,
   configuration choice, stale process, stale session, missing prerequisite and unproven
   hypothesis. For a historical audit, correlate saved calls/results and logs within a
   stated time range, and compare them with the agent's reports. Separate attempts,
   confirmed success/failure and unknown outcomes. A commit title or an agent's
   explanation does not establish a cause.
3. Read the installed implementation and relevant release documentation. Find every
   caller or writer of the affected resource before changing a shared policy.
4. Make the smallest authorized correction. Preserve a rollback artifact and unrelated
   dirty changes. Repair writer policy before reorganizing a library that can regrow.
5. Apply the change at the required layer: configuration reload, idle graceful restart,
   or a new conversation. Do not assume all three are interchangeable.
6. Verify the requested behavior with permitted evidence. Separate static inspection,
   helper-level checks, live process state and a real end-to-end task. Never claim an
   unperformed test; report pending activation or verification explicitly.

## Completion

Report the target profile/release, demonstrated cause, changed files/settings, activation
state, actual evidence, rollback location and remaining limitation. For optimization,
compare the same task boundaries and distinguish index size, model time, tool time and
post-response background work. Do not promise faster answers from fewer skill names alone.
