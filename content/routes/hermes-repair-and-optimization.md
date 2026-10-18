---
id: hermes-repair-and-optimization
name: Repair and optimize a Hermes installation
summary: >-
  A symptom-driven route through runtime identity, release regressions, automatic skill
  writers, context ownership, library structure, software/log audits, checkpoint failures
  and measured latency.
  Keep working capabilities and verify activation rather than stopping at file edits.
type: route
author: kisa
recommended: false
added: 2026-10-18
tags: [hermes, repair, optimization, troubleshooting, skills, checkpoints, regression, leveling-up, audit, logs]
steps:
  - title: Identify the live target and the maintenance boundary
    action: read
    ref: hermes-maintenance
    body: >-
      Confirm which profile, process and checkout serve the affected conversation.
      Separate explanation, audit, repair and deletion authority. Take only the branches
      relevant to the symptom; this route does not impose a full audit on a small fix.
  - title: Audit operational history, version drift and update conflicts
    action: read
    ref: hermes-runtime-and-upgrades
    body: >-
      Select the relevant branch. For software-history questions, correlate actual
      attempts/results and logs, distinguish startup from successful work, and compare
      the evidence with what the agent reported. State the time range and unknowns;
      do not launch software merely to audit history. For update faults, record release,
      HEAD, dirty changes and interpreter, check known fixes, and attribute a regression
      only with a failing/passing boundary. Preserve local behavior through API moves.
  - title: Control skill writers and resolve instruction ownership
    action: configure
    ref: hermes-skills-and-context
    body: >-
      Trace foreground guidance, post-response review, curator, archival and install/sync
      paths. Apply the user's chosen writing policy consistently while preserving reading
      and unrelated memory behavior. Put identity, user facts, project rules and procedures
      in their actual owners; check the generated prompt for contradictions.
  - title: Reorganize the library without losing procedures
    action: configure
    ref: hermes-skills-and-context
    body: >-
      Inventory active entries, categories, archives, aliases and supporting files. Merge
      only workflows with compatible triggers and outcomes, keep references on demand,
      repair renamed paths and automation references, and measure the renderer's actual
      index. Missing usage evidence is not permission to delete a capability.
  - title: Repair checkpoint scope and repeated filesystem failures
    action: configure
    ref: hermes-checkpoints-and-latency
    body: >-
      Distinguish a missing project from a legitimate new or deleted file. Inspect shadow
      Git scope, unreadable and oversized files, nested repositories and repeated setup.
      Fix the shared snapshot path; keep checkpoints when the user wants rollback.
  - title: Activate and verify the smallest repair
    action: read
    ref: hermes-runtime-and-upgrades
    body: >-
      Wait for a safe restart boundary if required, verify the new process and platform
      connection, and refresh a pinned conversation prompt when necessary. Confirm the
      requested behavior with permitted checks and record what remains unverified.
  - title: Measure latency before further tuning
    action: read
    ref: hermes-checkpoints-and-latency
    body: >-
      Separate model calls, context delivery, tools, checkpoints and background passes.
      Use display features supported by the chosen surface; do not mistake rolling TPS
      for complete task throughput or a configured compression threshold for its effective
      runtime value. Stop when the requested fault and performance question are resolved.
---

# Hermes repair and optimization

Start from the observed symptom. The order matters when changing several layers:
establish the actual runtime, resolve policy and writer conflicts, then reorganize
content, repair filesystem behavior and measure the resulting work.

This route contains reusable diagnosis and repair instructions, not an exported user
installation. It has no private prompts, conversations, account settings or incident
examples. Its source-code locations are navigation hints for the v0.22.2-era layout;
resolve them against the installed release before editing.

Use `next_step(step_id)` with IDs returned by the MCP. For a known problem, load the
relevant knowledge item directly instead of reading the whole route.
