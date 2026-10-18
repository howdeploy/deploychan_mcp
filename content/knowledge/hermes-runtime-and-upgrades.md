---
id: hermes-runtime-and-upgrades
name: Hermes runtime identity, upgrades and commit regressions
summary: >-
  Diagnose the correct Hermes process, profile and source revision; preserve local fixes
  across updates; distinguish known upstream repairs from unproven commit attribution;
  audit software launches and log evidence against agent claims; and verify code,
  configuration and conversation activation separately.
type: knowledge
author: kisa
recommended: false
added: 2026-10-18
tags: [hermes, runtime, profiles, upgrades, commits, regressions, prompt, troubleshooting, software, logs, audit]
source: https://github.com/NousResearch/hermes-agent
---

# Runtime identity, upgrades and regressions

Use this branch for a repair that appears correct on disk but has no visible effect,
an update conflict, a suspected bad commit, or an audit of what the agent actually
launched, observed and reported.
Technical navigation below is anchored to the **v0.22.2-era source layout**, not a claim
that this is the latest release or that every listed defect affects every installation.

## Establish the actual target

Collect only non-secret identity and operational metadata:

- Service/container and live PID; checkout path, HEAD, dirty paths and launcher.
- Effective Hermes home and profile, interpreter/dependency environment and platform.
- Conversation/session identity, working directory, terminal backend and its filesystem.
- Whether several profiles share the checkout but keep separate homes/configuration.

Use the installed gateway's read-only control interface or status command. In this
layout `gateway/control_socket.py` exposes `identify` and `status`. A service name,
directory name or CLI run in another shell is not proof of the gateway's profile.
Do not dump process environments, auth files or complete configs into a report.

Check host and sandbox paths separately. A path existing on the SSH host does not
prove it is mounted into a Docker/SSH terminal backend. A backend warning does not
prove the whole gateway is offline; inspect the affected subsystem.

## Audit operational history and agent claims

Start read-only. Auditing whether software worked does not authorize launching it,
opening a browser, installing dependencies or retrying an external action. Record the
question's scope: current state, a named session, or retained history over a stated time
range. A historical question cannot be answered solely from the current tool list or
today's process state.

### Separate capability states

| State | Evidence to seek | Limit of the conclusion |
|---|---|---|
| Declared or configured | Tool schema, plugin/MCP config, selected backend | Does not prove installation, connectivity or execution |
| Present or registered | Executable/package or runtime tool registration | Does not prove the correct profile/backend can use it |
| Attempted | Saved tool call with its arguments and matching identity | Does not prove dispatch reached the application |
| Started or attached | Process/connection/handshake evidence from the intended runtime | Does not prove a usable application or successful operation |
| Operation succeeded | Matching tool result and relevant application state/readback | Does not prove completion of every task requirement |
| Task outcome verified | Evidence for the requested result on the same object/revision | Does not establish all earlier or future runs succeeded |

These states need not be a local process-launch sequence: a tool can attach to an
existing browser or use a remote service. Diagnose the actual transport and execution
boundary. A failure before dispatch is an attempted tool operation, not proof that the
application itself started and crashed.

### Reconstruct the evidence chain

1. Inspect the relevant retained tool-call/result records and gateway/platform logs.
   Follow application, service or container logs only for the affected operation.
   Resolve schema/paths from the installed release; do not assume the latest session
   belongs to the profile under investigation.
2. Correlate by session/turn/call ID, tool name, backend and target identity. Use
   timestamps with timezone as supporting evidence, accounting for clock differences;
   temporal proximity alone is not a reliable call/result join. Keep missing pairs,
   truncated records, rotated logs and unavailable sources explicitly unknown.
3. Record the operation, stage reached, returned status/exit code, exact error class
   and a short redacted evidence pointer. Distinguish startup, dependency, permission,
   authentication, transport, timeout and task-level failures. Do not infer a root
   cause merely from an agent's paraphrase of an error.
4. Compare observed events with the agent's progress updates and final answer for
   the same task. Check whether claims of availability, successful execution, absence
   of attempts, repair or completion were supported at the time they were made.
5. Summarize attempts, confirmed successes, confirmed failures and unknown outcomes
   separately. State the selection rule, inspected count, time range and coverage gaps.
   A recent sample is not the entire history; incomplete entries are not successes or
   failures. Count distinct operations rather than duplicated log emissions.

Absence of a success in the inspected records supports only that bounded conclusion.
It does not prove the tool never worked. A current working application also does not
erase past failures. Use time-scoped findings instead of unqualified "never", "always"
or "fully working" claims. Do not treat a corrected historical answer as proof that
the underlying capability has been repaired.

### Surface material failures without flooding the user

Report a capability failure when it blocks the requested result, changes the execution
path or verification coverage materially, or produces repeated failures without progress.
State what failed, its effect on the task, the fallback actually used and what remains
unverified. A successful fallback does not establish that the original tool worked.

Do not turn every transient, recovered error into an alert. Group unchanged recurring
failures into one actionable update and a clear handoff limitation. Stop blind retries
of the same known failing path; diagnose or use an authorized fallback. This is task
reporting guidance, not authorization to add persistent monitoring or notifications.

For an audit finding, distinguish an unsupported claim, an omitted material failure and
missing evidence. Do not infer intentional concealment from incomplete reporting.
Retain only minimal redacted evidence in shared artifacts, not raw private transcripts,
page contents, credentials or full logs.

## Four layers of activation

| Layer | Evidence | What it does not prove |
|---|---|---|
| File | Current bytes/diff and effective config source | Running Python imported the edit |
| Process | New process/launcher identity and healthy platform connection | Existing session replaced its frozen prompt |
| Session | Actual assembled/stored prompt, tools and source snapshot | Every possible task behaves correctly |
| Task | Observed requested behavior and delivered result | Unrelated workloads or profiles are repaired |

Where sessions store `system_prompt_hash`, follow it to `system_prompts`; a NULL legacy
`sessions.system_prompt` is not evidence of an empty prompt. Read the selected rows
without editing prompt hashes or transcripts to force activation. Minimize exposure of
private prompt text; a local equality check or presence flag is usually enough.

Newly imported code may require a gateway restart; session-pinned identity, memory or
guidance may require a new conversation as well. A restart does not repair contradictory
text. Conversely, `/new` cannot make a process import code that it still holds in memory.
Use installed lifecycle semantics rather than assuming every setting has the same cache.

## Upgrade without losing local behavior

1. Inspect tracked and untracked changes before updating. Preserve source patches,
   selected profile files, skill assets and a rollback manifest outside the active catalog.
   State any unreadable exclusions; an incomplete archive is not a full backup.
2. Choose the supported release/distribution path using installed help and matching
   docs. A packaged install, source checkout and old virtualenv are different owners.
3. Review removed/moved APIs before porting patches. For the PM-managed layout use the
   matching managed launcher/dependencies; an old `venv/bin/python` may be rollback-only.
4. Port each behavioral invariant to its new shared call site. Do not copy an old
   monolithic `run_agent.py` over refactored modules or resurrect removed services.
5. Preserve unrelated dirty changes and other profiles. If local and upstream code
   overlap, resolve the semantic conflict and document which implementation wins.
6. Reach an idle/drained boundary and use the native graceful restart when needed.
   Verify process identity and the intended platform connection. Avoid force-killing
   a running task or using a restart command that targets another gateway instance.

An update may restore bundled content, alter defaults or change hook names. Recheck
automatic skill writers and output-transform registrations after activation rather
than assuming the previous local patch survived.

## Commit-aware diagnosis

Preserve `git status`, `git diff`, release/HEAD and the exact symptom. Use path-specific
`git log`, `git show` and ancestry checks to determine whether a repair is present.
For an ambiguous regression, compare known-good and known-bad behavior in an isolated
checkout with the same sanitized prerequisites, where execution is authorized. Do not
bisect a busy production checkout or reset unrelated work.

| Public revision | Established meaning | Required follow-up |
|---|---|---|
| [c098b2bf1d](https://github.com/NousResearch/hermes-agent/commit/c098b2bf1ddad46c24c6ec01f5d8754555d23f6d) | Fixes a running process's skills-index cache remaining stale after another process changes a skill | Check inclusion and file-signature invalidation; it does not imply an existing conversation refreshes all prompt content |
| [64ad33e32d](https://github.com/NousResearch/hermes-agent/commit/64ad33e32d) | Removes Skill Sync and the organization mirror from core | Treat old sync settings/patches as migration work, not evidence that the removed service should be recreated |
| [e3d2e57c9e](https://github.com/NousResearch/hermes-agent/commit/e3d2e57c9e) | Broadens background review beyond curator-managed skills | Inspect the actual writer scope when enforcing a manual-only policy; this feature is not automatically a bug |
| [v0.22.2](https://github.com/NousResearch/hermes-agent/tree/v0.22.2) | Source baseline for the checkpoint staging/scope and contradictory-guidance repair paths described in these guides | Verify the current implementation; this baseline does not establish the introducing commit or an upstream fix |

Do not publish a first-bad SHA without evidence. Distinguish an upstream fix, behavior
change, local merge mistake, inherited config and a verified regression. When the
introducing commit is unknown, say so and identify the failing function and baseline.
Keep a local repair marked local until its upstream equivalent is verified.

## Optional reviewers and final delivery

A reviewer plugin, a tool-routing MCP server and an output-transform hook are separate
mechanisms. Inspect enabled plugins, `required_output_validator`, registered
`transform_llm_output` callbacks and the platform delivery path. An MCP entry alone
does not prove every answer is reviewed or rewritten.

For an optional quality reviewer, preserve an explicit degraded-delivery behavior when
it times out; a quality outage should not silently lose a completed answer. Mandatory
authorization controls have their own policy and must not be bypassed. Never attribute
rewriting without comparing the relevant stages, or introduce a hidden editor as a fix
for slow replies.

## Completion evidence

Record the demonstrated cause, minimal diff, target profile/release, required activation,
observed activation, rollback path and verification boundary. A static repair, helper
probe, platform reconnection and an end-to-end task are distinct claims. A successful
helper must not be reported as a live conversation test.

Read next only if relevant: `hermes-skills-and-context` for writer/prompt conflicts;
`hermes-checkpoints-and-latency` for filesystem failures and timing.

Primary references: [updating](https://hermes-agent.nousresearch.com/docs/getting-started/updating),
[profiles](https://hermes-agent.nousresearch.com/docs/user-guide/profiles), and the
[documentation index](https://hermes-agent.nousresearch.com/docs/llms.txt). Resolve exact
commands and source locations against the selected installed release.
