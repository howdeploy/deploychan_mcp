---
id: hermes-checkpoints-and-latency
name: Hermes checkpoint failures and task latency
summary: >-
  Diagnose shadow-Git snapshots that repeatedly fail on missing paths, permissions,
  oversized files or nested repositories; repair scope and staging before disabling
  protection; then separate model, tool, checkpoint and background latency.
type: knowledge
author: kisa
recommended: false
added: 2026-10-18
tags: [hermes, checkpoints, rollback, git, filesystem, performance, latency, tps, compression]
source: https://hermes-agent.nousresearch.com/docs/user-guide/checkpoints-and-rollback
---

# Checkpoint failures and latency

Use this branch for repeated snapshot errors, unexpected Git work, stale project
paths or slow tasks. Navigate the installed checkpoint implementation, not the user's
ordinary repository workflow. Hermes can use private shadow Git storage even when
the user never maintains a Git repository for the agent.

## Determine whether usable snapshots exist

Inspect the selected profile's checkpoint config, project registrations, ledgers and
storage. Measure bytes on disk and available snapshot refs/trees, not just log lines.
A directory, blob, timestamp or ledger entry is not necessarily a restorable snapshot.

Separate successful snapshots, failed attempts, orphaned objects and pruned history.
Current store size after auto-pruning cannot establish historical growth. Repeated
errors do not establish a timer-based job: checkpoint attempts may be attached to
file changes or destructive terminal operations. Count and classify actual events;
do not convert their spacing into an invented scheduler interval.

To determine when a setting was enabled, compare retained configs and trustworthy
earlier observations. A first observed `enabled: true` is an upper date bound, not the
exact enabling time or author. An inherited old default may explain the value without
any explicit user command. State what the available history cannot establish.

## Diagnose the path before retrying

| Path state | Correct investigation |
|---|---|
| Project directory no longer exists | Validate its registration and owner; stop pointless retries against stale metadata, without deleting unrelated snapshot history |
| New file does not yet exist | Snapshot its intended existing parent/project before mutation; absence is a legitimate pre-change state |
| File was deleted or renamed | Preserve deletion/rename semantics and reconcile the prior index; do not drop the operation merely because exists() is false |
| Host path exists, sandbox path does not | Resolve backend/mount translation and the executor's actual filesystem |
| File is unreadable | Record an explicit exclusion or actionable failure; do not broaden permissions across unrelated files |
| File exceeds configured cap | Exclude before Git stages its contents, and reconcile a previously staged version |

Do not fix all missing-file cases with an early `if not exists: return`. That would
remove valid rollback coverage for file creation and deletion. Do not loop on an
unchanged filesystem failure hoping the model will infer a new solution. Retain the
implementation's per-operation/turn attempt boundary and make skipped coverage visible.

## Repair snapshot scope and staging

Source entry point in the baseline layout: `tools/checkpoint_manager.py`; inspect
`ensure_checkpoint`, project/root resolution, staging, snapshot and restore callers.

1. Resolve the nearest intended project or explicitly registered root. A common
   workspace may be a container of independent projects. Its `.git` or stale broad
   registration must not silently capture every sibling project. Conversely, an
   explicit operation on the workspace itself may legitimately require broad scope.
2. Enumerate eligible files **before** `git add`. A post-staging size check is too late
   to prevent reading large/unreadable files and retaining large Git objects.
3. Apply file-size/readability policy before staging; reconcile removed and excluded
   paths in an existing index. Preserve a later race check if a file grows after
   enumeration, plus existing locks, isolated Git configuration and error handling.
4. Handle names literally with NUL-delimited paths and literal pathspec behavior.
   Spaces, bracket characters, newlines and non-UTF-8 bytes must not become patterns
   or shell syntax.
5. Distinguish nested repositories with a valid HEAD from unborn repositories. A
   nested repo without a commit must not abort the entire parent snapshot. If it is
   excluded, label that exclusion; for gitlinks, do not claim nested working files
   were captured. Do not recursively snapshot an unrelated repository without scope.
6. Preserve creation, deletion and selected-file restore behavior. Do not apply an
   old restore patch blindly to a newer implementation with different selection rules.

Checkpoint metadata cleanup, deleting an unwanted project and fixing staging are
different actions. Removing one broken project does not repair generic staging;
disabling checkpoints is not a repair when the user wants rollback protection.

## Remove repeated setup from the hot path

Measure environment preparation separately from the Git subprocess. In PM-managed
installations, reconstructing tool/dependency environments for every Git invocation
can dominate a short snapshot operation even when Git itself is fast.

If demonstrated, resolve the immutable base Git environment once per snapshot/restore
operation and pass/reuse it through that operation. Keep a copy for each caller,
clear operation-local context in finally, and preserve isolation/locks. Do not turn it
into an unbounded process-wide environment cache that leaks between profiles, contexts
or later credential changes. Recheck restore and store-initialization paths as well as
snapshot creation.

Relevant verification, when authorized, uses isolated storage: ordinary create/restore,
missing project, file creation/deletion, unreadable and oversized files, nested repos,
literal names and one environment resolution per operation. Inspect Git objects as
well as the final tree: excluded large content should not already be in object storage.
Do not use a production rollback as an incidental smoke check.

## Attribute task latency to the correct stage

Record a comparable timeline from request receipt to delivered answer. Distinguish
model-call count and duration, tool dispatch/results, checkpoint work, context lookup,
compression and post-response tasks. Repeated broad session searches and large tool
results can add sequential model turns; a short relevant knowledge pointer may avoid
that work. Do not silently persist new user memory to obtain that pointer.

Input-token totals can include reused/cached prefixes. They are not automatically
uncached billed tokens. Static index characters, provider tokens and unique content
are different measurements. A short edit can still require expensive long-context
calls; prove the contribution before changing model or compression policy.

For the **inspected v0.22.2 Telegram implementation**:

| Desired visibility | Supported path or limitation |
|---|---|
| Tool names and destination previews | `display.platforms.telegram.tool_progress`: all or verbose; configure preview length and labels |
| Periodic elapsed status | `long_running_notifications` and `agent.gateway_notify_interval`; status uses elapsed whole minutes |
| Total completed-turn time | runtime_footer enabled with the `latency` field |
| TPS | Available through supported CLI/TUI/Desktop status fields, not a Telegram footer field |
| Per-tool duration | API run events include tool.completed duration; Telegram's progress renderer does not render it |

Global settings can be overridden by platform settings. Telegram verbose shows fuller
arguments, not a full per-tool timing profiler. An API run event stream is not a
confirmed passive attachment to an arbitrary existing Telegram task. Source navigation:
`gateway/run_turn_runner.py`, `gateway/run_turn.py`, `gateway/runtime_footer.py`,
`gateway/platforms/api_server_runs.py`, `tui_gateway/server.py`, `agent/turn_usage.py`.

In the inspected CLI/TUI/Desktop accounting, TPS aggregates output tokens over the
durations of up to ten recent model calls. It includes API waiting and is not pure
decode speed, instantaneous TPS or complete task throughput. Future releases may add
surfaces; check the actual renderer before promising a setting.

## Compression is not automatically a defect

Inspect the effective parsed policy for the current provider/model, including absolute
token caps and special overrides. In the inspected release, the historically named
`codex_gpt55_autoraise` can apply beyond the model implied by its name and raise a
configured lower trigger to 0.85. This is documented behavior, not proof of a bug.

Earlier compression means more frequent compression and less retained raw history;
later compression keeps more context. Neither is universally faster or better. Do not
disable the override because a config file shows a different number, or blame a delay
on compression when no compression event occurred. Compare actual long-session data
and preserve native policy unless evidence and the user's goal justify tuning.

## Completion evidence

Report the failing operation, affected scope, successful snapshot/restore evidence if
performed, exclusions, storage growth and activation status. For latency, identify what
was timed and what was not. Stop repeating broad checks after the relevant evidence is
sufficient; unresolved voice pronunciation, long-task steering or compression behavior
remain separate questions unless the user requested them.

Primary references: [checkpoints](https://hermes-agent.nousresearch.com/docs/user-guide/checkpoints-and-rollback),
[display configuration](https://hermes-agent.nousresearch.com/docs/user-guide/configuration),
and [compression/caching](https://hermes-agent.nousresearch.com/docs/developer-guide/context-compression-and-caching).
These guides describe failure mechanisms and repair paths, not a shipped universal patch.
