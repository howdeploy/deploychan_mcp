---
id: zaebal
name: 'Z.A.E.B.A.L.: profanity-triggered self-audit for agents'
summary: >-
  KISA's plugin: user frustration becomes an operational signal. Profanity at the agent
  triggers a session-history audit with two independent internal auditors and an optional
  external CLI auditor. Python 3.10+ stdlib only; RU/EN/ZH detection. Codex hook setup
  supports native Windows and Linux; Linux adapters also cover Claude Code, Kimi and OpenCode.
type: skill
author: kisa
recommended: true
added: 2026-08-03
tags: [self-audit, hooks, escalation, debugging, agent, protocol, windows, linux, codex]
source: https://github.com/howdeploy/Z.A.E.B.A.L
description: >-
  Use when the agent loops on the same mistake and the user is visibly frustrated.
  Z.A.E.B.A.L. treats profanity as an audit signal: stop, disprove the wrong belief,
  escalate repeated failures to an external auditor. Also use for requested hook setup
  on Linux or Windows. Select the target process OS and install only the requested host.
reminder: >-
  An agent that has already erred cannot trust its own self-check. The loop is almost
  always one wrong belief treated as fact — find and disprove THAT, not the symptoms.
  "Written ≠ took effect": verify the act of consumption, not the act of writing.
triggers: [self-audit, agent keeps failing, user frustrated, zaebal, Windows hook setup, Linux hook setup]
license: MIT
---

# Z.A.E.B.A.L. — profanity-triggered self-audit

**Z**aebal? **A**udit. **E**rrors. **B**reak. **A**nalyze. **L**eave no assumption.

When a coding agent gets stuck, it repeats the same action with small variations — because
one underlying belief about the task or the codebase is wrong, and the agent treats that
belief as fact. Another self-check just reproduces the mistake. Z.A.E.B.A.L. plugs a
feedback loop into the user-message boundary: **profanity and direct complaints become an
audit signal**, repeated signals escalate, and at the top level an **external auditor**
(the same or a cross-vendor CLI) reads the transcript and repository evidence from outside.
Public: `howdeploy/Z.A.E.B.A.L`, MIT, Python standard library only.

The upstream [installation router](https://github.com/howdeploy/Z.A.E.B.A.L/blob/main/skills/zaebal/SKILL.md)
and [Windows/Linux change](https://github.com/howdeploy/Z.A.E.B.A.L/pull/2) are the
source for the platform instructions below. Fetch the skill and runtime from the same
repository revision; downloading just the skill folder does not install a working hook.

## Why it works

The named failure patterns (collected from real session postmortems):

- **The wrong belief is invisible to the agent.** It doesn't loop from inattention — it has
  sincerely stopped understanding the problem. The protocol's goal is not "find the
  mismatch" but **find and disprove the wrong belief**.
- **"Written ≠ took effect".** A classic: the agent wrote a config/hook/instruction file and
  assumes it works because the file exists — while the harness reads it from a different
  path. Verify the act of *consumption*, not the act of writing.
- **Sycophancy vs hallucinated correctness.** Agreeing under pressure and abandoning a
  working solution — or defending broken code with invented facts. The cure for both:
  **execution over intuition**. Defending code with verbal arguments is forbidden — only a
  micro-test, a run, logs.
- **First plausible hypothesis.** A lone agent fixates on the first version. That's why
  auditors get raw artifacts, not the agent's interpretation — and why there are two of
  them: independent versions disprove each other's dead ends.
- **Missing session history.** Read the original request through the trigger, locate the
  first divergence, and correlate it with diffs, commits and actual test/error output.
  A transcript excerpt is orientation; read the full source when its path is available.
  Mark causal conclusions unverified when missing history could change them.

## The escalation ladder

Detection covers Russian, English and Chinese profanity (including leetspeak), classifies
intent, and tracks a per-session streak in a 30-minute window. Praise with profanity
such as "fucking great, it works" is silent and adds no weight; it does **not** close an
active incident or acknowledge recovery.

| Level | Streak weight | What happens |
|---|---:|---|
| **L1** | 0.5–1.5 | STOP. Read the session chronology, run two independent internal audits when policy permits, inventory beliefs and prepare a micro-plan. |
| **L2** | 2–3.5 | Repeat the independent audits, check the previous audit and compare the work against the original request. |
| **L3** | 4+ | Stop non-audit work; run internal audits and attempt the configured external audit. Resume only after explicit human acknowledgment. |

Directed complaints add `1.0`; ambiguous profanity adds `0.5`. If internal auditors
cannot be launched, state the degraded mode. An external verdict exists only inside
`<zaebal-verdict>` and remains a hypothesis to verify; internal sub-agents are not external.
For a false trigger, run the exact tokenized `--dismiss-trigger` command supplied by the
hook. This retracts only that trigger; replay is a no-op.

Recovery is explicit only: "continue", "продолжай", "по плану". A calm message — or even new
logs and evidence — does **not** lift the stop. The protocol is discipline-based: there is
no technical tool lock (a blocking mutation lock was researched for all four hosts and is
feasible, but deliberately not shipped yet — the human keeps final control).

> **The external auditor sees your context.** At L3 the auditor CLI receives a transcript
> source/excerpt plus repository evidence — which may contain private code, tokens and secrets, and a
> cross-vendor auditor sends that to **another provider**. The telemetry note
> (`incidents.jsonl` holds no message contents) does not cover the audit payload itself.
> The defaults are the safe end: same-vendor auditor, L3 only. If the code or the
> conversation is sensitive, keep it that way or set `"auditor": "none"` — and never point
> a cross-vendor audit at a repository you wouldn't paste into that vendor's chat.

Fail-open by design: a malformed payload, missing auditor or timeout never breaks the host
session. Telemetry (trigger, auditor, verdict — no message contents) lands in
`~/.zaebal/incidents.jsonl`.

## Install

Use an existing Python **3.10+** and the full repository. Reading this catalog entry or
using the audit protocol does not itself authorize installation. For a requested setup,
determine the OS of the **target agent process** once; a process inside WSL follows Linux
instructions, while a native Windows process follows Windows instructions.

```bash
git clone https://github.com/howdeploy/Z.A.E.B.A.L.git
cd Z.A.E.B.A.L
```

Read only the selected platform reference from that same checkout:

- [Native Windows](https://github.com/howdeploy/Z.A.E.B.A.L/blob/main/skills/zaebal/references/install-windows.md):
  no WSL, Bash or Linux packages required.
- [Linux, including WSL](https://github.com/howdeploy/Z.A.E.B.A.L/blob/main/skills/zaebal/references/install-linux.md):
  no Windows tools required.

For **Codex on native Windows**, run from the repository in PowerShell:

```powershell
py -3 scripts/install_codex_hook.py --platform windows
```

For **Codex on Linux**, run:

```bash
python3 scripts/install_codex_hook.py --platform linux
```

Use the discovered Python executable if its command differs. The helper honors
`CODEX_HOME` and saves an absolute interpreter/runtime command in `hooks.json`. It
preserves unrelated hooks, settings and incident history, prints a unique config backup,
and replaces its own entry on repeated setup. `--config` and `--dest` select custom paths.
Close editors changing `hooks.json` during setup; concurrent helper runs are serialized,
while external editors do not share that coordination.

Support boundaries and auditor defaults:

| Host | Integration | Default auditor |
|---|---|---|
| Codex | Native Windows/Linux helper; `UserPromptSubmit` in `CODEX_HOME/hooks.json`, default `~/.codex/hooks.json` | `codex exec --sandbox read-only` |
| Claude Code | Existing Linux adapter; `~/.claude/settings.json` | `claude -p`, read-only tools |
| Kimi CLI | Existing Linux adapter; `$KIMI_CODE_HOME/config.toml`, default `~/.kimi-code/config.toml` | Refused by default: no enforced read-only mode |
| OpenCode | Existing Linux adapter; `~/.config/opencode/plugins/zaebal.ts` | Refused by default: no enforced read-only mode |

Native Windows integration for Claude, Kimi and OpenCode is **not established** by this
helper. For another Linux host, read only its adapter and the matching `install.sh`
section. The legacy `./install.sh` installs every detected host; use it only when all
those integrations were requested.

## Verify, update and remove

Run the platform smoke suite from the checkout with the selected Python:

```bash
python3 -X utf8 -m unittest discover -s tests -p test_cross_platform.py
```

On native Windows use `py -3 -X utf8 -m unittest discover -s tests -p test_cross_platform.py`.
The suite uses temporary configuration/state, executes the registered command, and makes
no paid model calls. It covers Unicode paths, escalation, acknowledgment, concurrent state
writes, false-trigger rollback, custom auditor arguments and installer preservation.

Verify live host activation separately after setup: review/trust the hook if the host
requires it, start a fresh session, confirm a controlled complaint injects the protocol
and ordinary input stays silent. A passing standalone command does not prove host loading.
If this check is unavailable, report "command smoke passed; host activation unverified".

Update by repeating setup from one matching new checkout. Add `--remove` to the same
Codex setup command to unregister only that hook, repeating custom path arguments.
Runtime, settings and history remain. The legacy `./uninstall.sh` removes all integrations
and data; it is not the single-host removal path.

## Configure the auditor

Settings live in `~/.zaebal/config.json` and take effect on the next trigger:

- `auditor`: `"same"` by default; choose a supported CLI or `"none"` to disable it.
- `audit_levels`: `[3]`; `auditor_timeout_sec`: `90`.
- `transcript_tail_chars`: `12000`; `agent_context_tail_chars`: `2500`. These are
  orientation excerpts; the readable transcript source remains authoritative.
- `auditor_command`: a legacy POSIX command string or an argv array. Prefer an array for
  Windows paths with spaces/backslashes; the prompt is appended as the final argument.
- `allow_unsafe_auditor`: `false`. Built-in Kimi/OpenCode auditors are refused because
  they lack enforced read-only modes; use Claude/Codex or a sandboxed custom command.

The shared core uses native `msvcrt` locking on Windows and `fcntl` on Unix, atomic state
replacement and UTF-8 streams. Both platforms share the audit protocol, wordlists and
state format. Wordlists live under `core/wordlists/`.

## Why this is in deploychan

This is the missing fourth pillar of the `agent-harness` route: hooks control the loop,
prompts set the rules, memory holds state — and Z.A.E.B.A.L. catches the case where all
three are fine but the agent is confidently building on a wrong belief. It turns the user's
frustration (which would otherwise just be swearing into the void) into a structured audit
with an external pair of eyes.
