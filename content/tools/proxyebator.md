---
id: proxyebator
name: 'Proxyebator: masked SOCKS5 tunnel on a VPS, one script'
summary: >-
  KISA's script: a VPS + a domain becomes a SOCKS5 proxy whose traffic reads as ordinary
  HTTPS to basic DPI. nginx serves a decoy site on 443, a secret path proxies a WebSocket
  tunnel (Chisel or wstunnel) with a Let's Encrypt certificate. Server and client modes in
  one script; designed to be deployed by an AI assistant.
type: tool
author: kisa
recommended: false
added: 2026-08-03
tags: [proxy, socks5, websocket, chisel, wstunnel, vps, censorship, nginx]
source: https://github.com/howdeploy/Proxyebator
description: >-
  Use when the user has a VPS and a domain and needs a masked proxy without Xray: traffic
  looks like plain HTTPS to a decoy site, the tunnel hides in a WebSocket on a secret
  nginx path. One bash script, server and client modes.
license: MIT
---

# Proxyebator — a masked SOCKS5 tunnel on a VPS, one script

One script, one domain: a **SOCKS5 proxy whose traffic looks like ordinary HTTPS**. nginx
serves a decoy site on 443 with a real Let's Encrypt certificate; a secret path (e.g.
`/abc123ef/`) proxies a WebSocket tunnel to **Chisel** (server-side SOCKS5, authfile) or
**wstunnel** (client-side SOCKS5, secret-path auth) on loopback. DPI sees a normal
web server. Public: `howdeploy/Proxyebator`, MIT.

Sibling of `xrayebator` — the trade-off: Xray REALITY needs **no domain** and is the
stronger disguise; Proxyebator **requires a domain** but is simpler, single-script, and its
SOCKS5 endpoint drops straight into browsers, `ALL_PROXY` and tools like the
`chrome-proxy-english-signup` trick.

## Before you start

1. **A Linux VPS** (Debian/Ubuntu/CentOS/Alma/Rocky/Fedora/Arch, amd64 or arm64) with root
   and open ports 80 + 443.
2. **A domain** — the cheapest one works ($1–2/year). **Mandatory**: without it certbot
   can't issue TLS, and without TLS the WebSocket is naked to DPI.
3. **An A-record** pointing at the server. If the domain sits behind Cloudflare, the project
   README insists on **grey cloud (DNS only)**, reporting that the proxied orange cloud
   broke its WebSocket roughly every ~100 seconds. Treat that as the author's field report,
   not a law: Cloudflare officially supports proxied WebSockets, and tunneled traffic with
   keepalives (Chisel's default is 25 s) often survives it. Grey cloud is still the
   lower-friction choice — just know the trade-off is empirical, not absolute.

## Install — designed to be handed to an agent

The repo ships a copy-paste brief for an AI assistant with SSH access: download
`proxyebator.sh` on the server, run

```bash
sudo ./proxyebator.sh server --domain YOURDOMAIN.COM --tunnel chisel
```

and wait for `=== ALL CHECKS PASSED ===` (the script self-verifies). The client side runs
on your machine and raises a local SOCKS5 on `127.0.0.1:1080`:

```bash
./proxyebator.sh client        # interactive: asks for host, path and password
curl --socks5-hostname localhost:1080 https://ifconfig.me   # must return the VPS IP
```

Prefer the interactive client (or `--pass`) over the one-argument `wss://user:TOKEN@host/...`
URL form: a token in the command line lands in shell history and process listings.

One honest calibration: "indistinguishable from ordinary HTTPS" is the goal, not a
guarantee — what you actually get is traffic that is **harder for basic DPI to classify**,
behind a real certificate and a real site. A determined censor with active probing is a
different opponent; Xray REALITY (`xrayebator`) is built for that one.

The service runs as `nobody` via systemd; the backend binds to `127.0.0.1` only. Config
persists in `/etc/proxyebator/server.conf`; `verify` and `uninstall` modes included
(`--yes` to skip confirmations).

## Useful flags

`--tunnel chisel|wstunnel` (default chisel), `--masquerade stub|proxy|static` (what the
decoy site does), `--socks-port` (client side, default 1080), `--port` (default 443).

## Why this is in deploychan

Third leg of KISA's network toolkit, next to `xrayebator` (own VPN, no domain needed) and
`zapret2agent` (no server at all — DPI bypass on your own machine). The `agent-internet`
and `durable-ai-account` guides assume the agent has a clean exit; Proxyebator is the
lightest way to get one when you already pay for a domain. The install-via-agent brief in
its README is also a neat pattern: a task specification a user pastes into any assistant,
and the assistant deploys the whole thing over SSH.
