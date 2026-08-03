---
id: zapret2agent
name: 'Zapret2agent: DPI bypass configured by talking to an agent'
summary: >-
  KISA's wrapper over zapret2 (bol-van's low-level DPI bypass): instead of hand-editing
  iptables and nfqws, you talk to Claude Code — it diagnoses the system, picks a bypass
  strategy via blockcheck, and walks you through install step by step. Confirmation before
  every system operation, automatic backups, 5-minute rollback timer.
type: tool
author: kisa
recommended: false
added: 2026-08-03
tags: [dpi, zapret, censorship, linux, iptables, claude-code, network]
source: https://github.com/howdeploy/Zapret2agent
description: >-
  Use when sites are throttled or blocked by DPI on a Linux machine and the user wants
  zapret2 installed and tuned without learning nfqws/iptables. Claude Code-native
  (CLAUDE.md + five skills), compatible with Codex CLI via AGENTS.md.
license: MIT
---

# Zapret2agent — DPI bypass configured by talking to an agent

zapret2 is a powerful low-level DPI-bypass tool — and its setup (nfqws, iptables, strategy
selection) is exactly the kind of arcane sysadmin work most people bounce off. Zapret2agent
wraps it in an agent: you say "install / configure / fix", the agent diagnoses the system
and does it step by step, explaining each one. You don't need to know what DPI, nfqws or
iptables are. Public: `howdeploy/Zapret2agent`, MIT.

## What's inside

Three layers:

- **CLAUDE.md** — the agent's instructions: behavior, dialogue protocol, safety rules. Read
  automatically by Claude Code at launch; Codex CLI reads the same guidance via `AGENTS.md`.
- **`.claude/skills/`** — five skills with detailed procedures: `zapret-diagnose`,
  `zapret-install`, `zapret-config`, `zapret-manage`, `zapret-modes`.
- **`scripts/`** — bash/python for the reliable parts: system diagnostics, config backups,
  blockcheck result parsing, strategy application.

Capabilities: OS/kernel/firewall/VPN/DNS-poisoning diagnostics, clean install through a
guided dialog, automatic bypass-strategy selection via blockcheck, two modes (**direct
bypass** without a VPN / **tunnel protection** alongside one), VPN-client detection
(Throne, Nekoray, Hiddify, v2rayA, AmneziaVPN, Clash, sing-box, WireGuard, OpenVPN),
service and domain-list management, a full TSPU seed blocklist with auto-merge.

## Safety model

- Before **every** system operation (iptables, systemctl, config writes) the agent shows
  the exact command and waits for confirmation. No "yes" — nothing runs.
- Changing iptables/nftables automatically starts a **5-minute rollback timer**: if things
  go wrong, the rules revert by themselves.
- `/opt/zapret2/config` is backed up before every change.

## Install

Linux only (Ubuntu, Fedora, Arch, Manjaro — zapret2 uses Linux netfilter; macOS/Windows are
not supported). Needs Claude Code installed and authorized, plus git, bash, curl, sudo, ip.

```bash
git clone https://github.com/howdeploy/Zapret2agent.git
cd Zapret2agent
claude
```

`bash install.sh --global` registers the skills globally so Claude Code can manage zapret
from any folder. The repo also advertises a `curl | bash` one-liner — skip it: this thing
rewrites your firewall and system services, so clone the repo, read `install.sh` and the
skills first, then run them locally.

## Why this is in deploychan

The network layer of the `durable-ai-account` / `agent-internet` story has three KISA
tools for three different jobs: **Xrayebator** (`xrayebator`) — your own VPN exit on a VPS,
**Proxyebator** (`proxyebator`) — a masked SOCKS5 tunnel behind a domain, and
**Zapret2agent** — no server at all, it makes DPI ignore you on your own machine. It's also
a live example of the pattern this server preaches: take a hostile, expert-only tool and
make it operable by an agent through instructions + skills + scripts.
