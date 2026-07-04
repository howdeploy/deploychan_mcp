---
id: nixos-nix-ld-electron
name: 'NixOS: nix-ld and Electron apps'
summary: >-
  How to get Electron/Chromium apps running on NixOS via nix-ld: the full list
  of runtime dependencies, NIXOS_OZONE_WL for Wayland, launching Hermes Desktop
  with voice, and per-tool SOCKS5 proxying (including Zen Browser).
type: knowledge
author: kisa
recommended: false
added: 2026-07-04
tags: [nixos, nix-ld, electron, hermes, proxy]
source: https://mcp.deploychan.webcam/docs
---

# Electron apps on NixOS (nix-ld)

Electron/Chromium apps are unpatched binaries: they look for libraries in
`/usr/lib/`, which doesn't exist on NixOS. The fix — `nix-ld` with a full set of runtime deps.

## Full set of Electron/Chromium runtime dependencies

```nix
programs.nix-ld.libraries = with pkgs; [
    glib gtk3 nspr nss cups dbus at-spi2-core
    cairo pango gdk-pixbuf libdrm libxkbcommon
    libxshmfence libpulseaudio libgbm expat wayland
    zlib libpng libjpeg libwebp
    xorg.libxcb xorg.libXcomposite xorg.libXdamage
];
```

(First `programs.nix-ld.enable = true;` — see the `nixos-administration` guide.)

## Wayland integration
```nix
environment.sessionVariables.NIXOS_OZONE_WL = "1";
```

For niri:
```kdl
environment { NIXOS_OZONE_WL "1" }
```

## Hermes Desktop on NixOS

### Prerequisites
1. Electron deps via nix-ld (above)
2. `NIXOS_OZONE_WL=1`
3. Voice: `portaudio` + `ffmpeg` in systemPackages, `LD_LIBRARY_PATH=/run/current-system/sw/lib`

### Autostart in niri
```kdl
spawn-at-startup "hermes" "desktop"
window-rule {
    match app-id="Hermes"
    open-maximized true
}
```

### Voice support
```bash
# In the Hermes venv
uv pip install -e ".[voice]"
```
Config:
```yaml
stt:
  enabled: true
  provider: groq   # or local
```
Env: `GROQ_API_KEY=<key>` in `~/.hermes/.env`

## Per-tool SOCKS5 proxy

The system proxy at `127.0.0.1:10808` is set per tool individually:
```bash
ALL_PROXY=socks5://127.0.0.1:10808 <command>
```

Zen Browser: write to `prefs.js`:
```
user_pref("network.proxy.type", 1);
user_pref("network.proxy.socks", "127.0.0.1");
user_pref("network.proxy.socks_port", 10808);
user_pref("network.proxy.socks_version", 5);
user_pref("network.proxy.socks_remote_dns", true);
```

Python tools: install `httpx[socks]` in the venv.
