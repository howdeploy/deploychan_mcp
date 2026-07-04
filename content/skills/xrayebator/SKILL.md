---
id: xrayebator
name: 'Xrayebator: your own VPN on a VPS (Xray Reality)'
summary: >-
  KISA's skill: an interactive manager for an Xray Reality VPN on your own VPS. VLESS +
  REALITY — traffic indistinguishable from ordinary HTTPS, no domain or certificate, bypasses
  DPI. Transport profiles, adding clients, HAPP subscription. So the agent runs research and
  the browser through its own clean exit, past the blocks.
type: skill
author: kisa
recommended: false
added: 2026-07-04
tags: [vpn, xray, reality, vless, vps, censorship, proxy]
source: https://github.com/howdeploy/Xrayebator
description: >-
  Use when the user needs their own VPN/proxy on a VPS to bypass regional blocks or DPI so
  research APIs and browsers work through a clean exit. One-script Xray VLESS+REALITY
  installer and client manager.
license: MIT
---

# Xrayebator — your own VPN on a VPS (Xray Reality)

A single script spins up and manages an **Xray Reality VPN** on your VPS. The tech is **VLESS +
REALITY**: traffic is indistinguishable from an ordinary HTTPS connection to a real site, with no
domain or certificate of your own. Ordinary protocols (OpenVPN, WireGuard, Shadowsocks) get
caught by DPI on their signature; REALITY masquerades as legitimate TLS to someone else's site —
and so it doesn't get flagged by packet inspection. Public: `howdeploy/Xrayebator` (v2.0), MIT.

> **Legality.** Your own VPN for privacy and access to your own services is legitimate in many
> countries, but not everywhere. This is for personal access and research, not for breaking the
> law. Check your local rules; responsibility for use is on the user.

## Why this is in deploychan

Some services are unavailable from your region or flag public VPNs. The `agent-internet` and
`agent-voice` guides point right at this: research APIs, the browser, ElevenLabs, Stripe may not
work from within your region. Xrayebator gives you **your own clean exit** — the agent runs
research and the browser through your VPS, not through a flagged public VPN. Your own VPN = your
own control.

## Install and management

The script is interactive — run it on a clean VPS as root:

```bash
git clone https://github.com/howdeploy/Xrayebator.git
cd Xrayebator
sudo bash xrayebator
```

First run — installation (installs Xray-core, generates Reality keys, brings up the node). Every
subsequent run — a management menu:

- **Install** — deploy Xray Reality on this VPS.
- **Add client** — generate a new client (VLESS link + QR).
- **Remove** — remove a client or tear down Xray.

Keys and config live in `/usr/local/etc/xray/`. Masking is configured via the SNI list (which
real site the connection mimics).

## Transport profiles

v2.0 supports several combinations for different network and DPI conditions:

- **VLESS + TCP + Reality + Vision** — the baseline, the most stable.
- **+ Mux / + uTLS** — multiplexing and TLS-fingerprint spoofing.
- **VLESS + XHTTP + Reality** — an HTTP wrapper, more resilient where TCP gets cut.
- **VLESS + gRPC + Reality** — gRPC transport (careful, slower).
- **VLESS PQ encryption** (`mlkem768x25519plus`) — post-quantum encryption.

Plus a **HAPP subscription** and multi-route profiles: the client gets a subscription rather than
a single link.

## Clients

Import the generated VLESS link or scan the QR:

| Platform | App |
|---|---|
| Android | v2rayNG, NekoBox, Hiddify, HAPP |
| iOS/macOS | Shadowrocket, V2BOX, Streisand, HAPP |
| Windows | v2rayN, Hiddify |
| Linux | v2rayA, Nekoray, Hiddify |

## In practice

- Take a VPS in a clean datacenter, outside the blocked region.
- Don't put detectable protocols (OpenVPN/WireGuard) on the same VPS — some providers ban a VPS
  that's been spotted using them. REALITY doesn't require that.
- Pick your SNI masking to match a site reachable from your region: if the current one gets
  blocked, you switch the SNI to another and the connection looks legitimate again.
- Your own VPN is what the "agent + research/browser" combo needs: set up the exit, and
  `ALL_PROXY` / the system proxy route the agent's traffic through the clean exit.
