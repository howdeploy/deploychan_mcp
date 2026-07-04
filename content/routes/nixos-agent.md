---
id: nixos-agent
name: Get Your Agent Running on NixOS
summary: >-
  A route for anyone running a coding agent on NixOS: survive the declarative environment
  (no coreutils → Python fallback), enable nix-ld for binaries and Electron, and set up
  the system and desktop. Assembled from KISA's real daily-driving experience.
type: route
author: kisa
recommended: false
added: 2026-07-04
tags: [nixos, agent, hermes, leveling-up, setup]
steps:
  - title: The environment and working patterns
    action: read
    ref: nixos-agent-environment
    body: Survive NixOS — no coreutils on PATH, the Python fallback, real binaries in /run/current-system/sw/bin, wiring up MCP, and managing Hermes.
  - title: nix-ld and Electron apps
    action: configure
    ref: nixos-nix-ld-electron
    body: Enable nix-ld, feed it the Electron/Chromium runtime deps, and bring up Hermes Desktop with voice and a proxy.
  - title: Administration and the desktop
    action: configure
    ref: nixos-administration
    body: The config-edit-and-rebuild cycle, the desktop stack (waybar/niri/fuzzel/dunst/GTK), EFI, serial, mounting an HDD, and NOPASSWD rebuild for an autonomous agent.
---

# Get Your Agent Running on NixOS

NixOS breaks agents used to ordinary Linux: no `cat`/`ls`/`find` on PATH, unpatched
binaries crash without their libraries, interactive commands hang without a TTY. This
route is how to work through that step by step and end up with a working agent on NixOS.
Assembled from real daily-driving experience, not from documentation.

> **Ordering with the universal route.** On NixOS? Bring up the environment first (step
> 1) — without it, the universal `agent-onboarding` route (personality → internet → voice
> → memory) will keep tripping over missing coreutils and broken binaries. Platform
> first, the agent's character second. This does NOT mean nixos-agent matters more for
> everyone: it's only for those actually on NixOS.

## The three steps

1. **Environment and patterns** (`nixos-agent-environment`). Python as the universal
   fallback, real binaries via `/run/current-system/sw/bin`, the `/bin/bash` symlink,
   wiring up MCP, and managing Hermes (`mcp_servers`, `pty`, restarting the gateway).
2. **nix-ld and Electron** (`nixos-nix-ld-electron`). Enable `nix-ld`, provide the
   Electron/Chromium runtime deps, `NIXOS_OZONE_WL` for Wayland, and bring up Hermes
   Desktop with voice.
3. **Administration and the desktop** (`nixos-administration`). The declarative
   edit-and-`nixos-rebuild` cycle, the desktop stack, EFI/serial/HDD, and autonomous
   rebuild for the agent.

## Extras

Not route steps, but from the same NixOS pack — as needed:
- `nixos-streaming` — desktop streaming (Sunshine/Moonlight, all the way to a Samsung
  TV).
- `niri-hotkeys` — a reference for niri hotkeys.

## How to walk it

Call `next_step("nixos-agent:1")` — you'll get the first step's materials, then follow
`next_step_id`. At each step, read the knowledge and apply it to your own machine:
replace the placeholders (`YOUR_USER`, `YOUR_HOSTNAME`, `YOUR_UUID`, `<NIXOS_IP>`) with
your own values. Every install goes through the discipline of the base skill
`tailored-install`.
