---
id: zaebal
name: 'Z.A.E.B.A.L.: profanity-triggered self-audit for agents'
summary: >-
  KISA's plugin: user frustration becomes an operational signal. Profanity at the agent
  fires an escalation protocol — stop, two independent auditors, an inventory of beliefs,
  and at level 3 an external auditor (a different CLI) reads the transcript from outside.
  Python stdlib only; Claude Code, Codex, Kimi CLI, OpenCode. RU/EN/ZH detection.
type: skill
author: kisa
recommended: true
added: 2026-08-03
tags: [self-audit, hooks, escalation, debugging, agent, protocol]
source: https://github.com/howdeploy/Z.A.E.B.A.L
description: >-
  Use when the agent loops on the same mistake and the user is visibly frustrated.
  Z.A.E.B.A.L. treats profanity as an audit signal: stop, disprove the wrong belief,
  escalate repeated failures to an external auditor. Installs as hooks in four agent hosts.
reminder: >-
  An agent that has already erred cannot trust its own self-check. The loop is almost
  always one wrong belief treated as fact — find and disprove THAT, not the symptoms.
  "Written ≠ took effect": verify the act of consumption, not the act of writing.
triggers: [self-audit, agent keeps failing, user frustrated, zaebal]
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
  micro-test, a run, logs. This kills ~90% of "lying" cases.
- **First plausible hypothesis.** A lone agent fixates on the first version. That's why
  auditors get raw artifacts, not the agent's interpretation — and why there are two of
  them: independent versions disprove each other's dead ends.

## The escalation ladder

Detection covers Russian, English and Chinese profanity (including leetspeak), classifies
intent (praise with profanity like "fucking great, it works" **closes** an incident instead
of opening one), and tracks a per-session streak in a 30-minute window:

| Level | Streak weight | What happens |
|---|---:|---|
| **L1** | 1–1.5 | STOP. Two independent internal sub-agent auditors, belief inventory (every statement tagged FACT — confirmed by execution — or HYPOTHESIS), micro-plan, notify the human. |
| **L2** | 2–3.5 | Remove unverified assumptions, compare the work verbatim against the original request. |
| **L3** | 4+ | FULL STOP of all agents and background work. External auditor (Claude / Codex / Kimi / OpenCode CLI) delivers a verdict; work resumes only after explicit human acknowledgment. |

Recovery is explicit only: "continue", "продолжай", "по плану". A calm message — or even new
logs and evidence — does **not** lift the stop. The protocol is discipline-based: there is
no technical tool lock (a blocking mutation lock was researched for all four hosts and is
feasible, but deliberately not shipped yet — the human keeps final control).

> **The external auditor sees your context.** At L3 the auditor CLI receives a transcript
> tail plus repository evidence — which may contain private code, tokens and secrets, and a
> cross-vendor auditor sends that to **another provider**. The telemetry note
> (`incidents.jsonl` holds no message contents) does not cover the audit payload itself.
> The defaults are the safe end: same-vendor auditor, L3 only. If the code or the
> conversation is sensitive, keep it that way or set `"auditor": "none"` — and never point
> a cross-vendor audit at a repository you wouldn't paste into that vendor's chat.

Fail-open by design: a malformed payload, missing auditor or timeout never breaks the host
session. Telemetry (trigger, auditor, verdict — no message contents) lands in
`~/.zaebal/incidents.jsonl`.

## Install

Requirements: `python3`, plus at least one supported agent CLI if external auditing is on.

```bash
git clone https://github.com/howdeploy/Z.A.E.B.A.L.git
cd Z.A.E.B.A.L
chmod +x install.sh && ./install.sh
```

The installer detects available hosts and updates only the relevant user config:

| Host | Integration | Default auditor |
|---|---|---|
| Claude Code | `UserPromptSubmit` in `~/.claude/settings.json` | `claude -p`, read-only tools |
| Codex CLI | `UserPromptSubmit` in `~/.codex/hooks.json` | `codex exec --sandbox read-only` |
| Kimi CLI | hook in `~/.kimi-code/config.toml` | `kimi -p` |
| OpenCode | plugin `~/.config/opencode/plugins/zaebal.ts` | `opencode run` |

Settings live in `~/.zaebal/config.json`: pick the auditor (`"same"` or cross-vendor —
Claude auditing Codex is a good pattern), which levels call it (`audit_levels`, default
`[3]`), timeout, transcript tail size. Wordlists are plain text under `core/wordlists/`.

## Why this is in deploychan

This is the missing fourth pillar of the `agent-harness` route: hooks control the loop,
prompts set the rules, memory holds state — and Z.A.E.B.A.L. catches the case where all
three are fine but the agent is confidently building on a wrong belief. It turns the user's
frustration (which would otherwise just be swearing into the void) into a structured audit
with an external pair of eyes.
