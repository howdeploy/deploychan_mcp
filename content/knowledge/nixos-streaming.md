---
id: nixos-streaming
name: 'NixOS: desktop streaming (Sunshine/Moonlight)'
summary: >-
  A real, working desktop-streaming setup on NixOS: Sunshine as host, Moonlight
  as client. PC↔PC, second monitor, and sideloading Moonlight onto a Samsung TV
  (Tizen) via Docker + sdb. Plus why Sunshine+Moonlight beats RDP/VNC.
type: knowledge
author: kisa
recommended: false
added: 2026-07-04
tags: [nixos, streaming, sunshine, moonlight, samsung, tizen]
source: https://mcp.deploychan.webcam/docs
---

# Sunshine + Moonlight — desktop streaming on NixOS

Working use case: stream a NixOS desktop to another PC or a TV with low latency.
Host — **Sunshine**, client — **Moonlight**. Below — how to stand it up,
including sideloading onto a Samsung TV.

## Enable Sunshine

```nix
services.sunshine = {
  enable = true;
  autoStart = true;
  capSysAdmin = true;
  openFirewall = true;   # ports 47984-48010
};
users.users.YOUR_USER.extraGroups = [ "uinput" "input" ];
boot.kernelModules = [ "uinput" ];
```

After `nixos-rebuild switch` it's a systemd user service. The web UI is at
`https://localhost:47990`.

## Moonlight — PC ↔ PC client

- Download Moonlight: https://moonlight-stream.org
- Auto-discovers Sunshine on the LAN, or add it manually: `<NIXOS_IP>:47989`
- Pairing: Moonlight shows a PIN → open `https://<NIXOS_IP>:47990` → PIN tab → enter it
- Launch "Desktop" for a full Wayland stream

### Second monitor
Launch Moonlight fullscreen on the second monitor. The mouse/keyboard from the client PC
control the NixOS desktop.

### Moonlight hotkeys
| Keys | Action |
|---|---|
| Ctrl+Alt+Shift+X | Toggle fullscreen |
| Ctrl+Alt+Shift+Z | Toggle input capture |
| Ctrl+Alt+Shift+Q | Quit the session |
| Ctrl+Alt+Shift+S | Stats overlay |

### Pitfalls
- Exclusive fullscreen grabs both monitors → Moonlight Settings → Display → target monitor
- Win combos get intercepted by the client OS → enable "Capture system keyboard shortcuts"

## Moonlight on a Samsung TV (Tizen)

There's no official app in the Samsung Store — install it by sideloading a WGT package.

### Method A: Docker (easiest)
```bash
docker run -it --rm ghcr.io/oneliberty/moonlight-chrome-tizen:samsung_wasm
sdb connect <TV_IP>
tizen install -n Moonlight.wgt
```

### Prerequisites
1. Developer Mode on the TV: Apps → press `12345` → enable → set Host PC IP
2. The TV must allow remote installation
3. SDB port: `26101`

### Prebuilt builds
- OneLiberty/moonlight-chrome-tizen (Tizen 5.5+)
- brightcraft/moonlight-tizen (HDR, 4K, 120/144fps)

## Why Sunshine+Moonlight over the alternatives
- RDP/VNC: worse latency, no Wayland support
- Barrier/Input Leap: share input, but not video
- <5ms encode + <2ms network + <5ms decode at 60fps
