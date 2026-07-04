---
id: nixos-administration
name: 'NixOS: system administration'
summary: >-
  Practical guide to administering NixOS: declarative config-workflow and
  rebuild, nix-ld for unpatched binaries, LD_LIBRARY_PATH for Python ctypes,
  desktop stack (waybar/niri/fuzzel/dunst/swayosd/GTK), EFI, serial, HDD
  mounting, screenshots, fastfetch and NOPASSWD-rebuild for an autonomous agent.
type: knowledge
author: kisa
recommended: false
added: 2026-07-04
tags: [nixos, administration, nix-ld, waybar, niri, desktop]
source: https://mcp.deploychan.webcam/docs
---

# NixOS administration

Everything is declarative: the system is built from config, not patched live. Below —
the edit workflow, nix-ld, desktop integration, and NixOS-specific gotchas.

> **Essential vs taste.** For the agent the ESSENTIALS are the edit/rebuild cycle, nix-ld,
> `LD_LIBRARY_PATH`, serial permissions, EFI, HDD mounting, autonomous rebuild. Everything about
> STYLING (Waybar, Niri, Fuzzel, Dunst, SwayOSD, GTK, wallpaper, Fastfetch) is KISA's PERSONAL
> taste (Catppuccin Mocha), marked "taste · example". This is NOT an instruction to the agent, but
> an example of "what's possible". The agent replicates ITS OWN user's taste, not a copy of this one.

## Basic cycle: editing the system config

> **About the `cat`/`ls`/`cp` below.** In the user's interactive shell, coreutils are usually present.
> But an agent in a non-interactive context may not have them in PATH (see `nixos-agent-environment`):
> in that case use the full path (`/run/current-system/sw/bin/cat`) or a Python fallback. Don't blindly
> assume bare `cat`/`ls` — the examples below are for illustration.

### 1. Read the current config
```bash
cat /etc/nixos/configuration.nix
```

### 2. Apply changes (targeted edit)
```bash
# Copy to temp (a patch tool may refuse on /etc/nixos/*)
sudo cp /etc/nixos/configuration.nix /tmp/configuration.nix
sudo chmod 666 /tmp/configuration.nix
# ... edit /tmp/configuration.nix ...
sudo cp /tmp/configuration.nix /etc/nixos/configuration.nix
```

### 3. Verify and rebuild
```bash
sudo nixos-rebuild dry-build   # build the config WITHOUT applying — catches errors early
sudo nixos-rebuild switch      # apply
```
After switch, make sure the needed services came up:
```bash
systemctl status <service>            # system service
systemctl --user status <service>     # user service (e.g. waybar, hermes-gateway)
```

### Alternative: flake-based system
```bash
cd /etc/nixos
sudo nix flake update
sudo nixos-rebuild switch --flake .#YOUR_HOSTNAME
```

## nix-ld: shared libraries for unpatched binaries

NixOS doesn't put libraries in `/usr/lib/`. Unpatched binaries (Electron apps,
prebuilt CLI tools, proprietary software) crash with `cannot open shared object file`.

### Enable
```nix
programs.nix-ld.enable = true;
```

### Add missing libraries
```nix
programs.nix-ld.libraries = with pkgs; [
    glib gtk3 nspr nss cups dbus at-spi2-core
    cairo pango gdk-pixbuf libdrm libxkbcommon
    libxshmfence libpulseaudio libgbm expat wayland
    zlib libpng libjpeg libwebp
    xorg.libxcb xorg.libXcomposite xorg.libXdamage
];
```

### Find the path to a package's library
```bash
nix eval --raw nixpkgs#glib.outPath
# Avoid '-bin' packages — they have no /lib
```

## Shared libraries for Python ctypes

Python packages that use `ctypes.util.find_library` (e.g. `sounddevice`) fail to find
libraries on NixOS — even when they're installed.

### Fix: add LD_LIBRARY_PATH
```nix
environment.sessionVariables.LD_LIBRARY_PATH = "/run/current-system/sw/lib";
```

## Desktop — personal taste (example, not instruction)

The sections from here down to "EFI boot order" (Waybar, Niri, Fuzzel, Dunst, SwayOSD, GTK,
wallpaper), plus Fastfetch below, are STYLING to KISA's taste (Catppuccin Mocha). An example
of "what's possible", NOT a requirement for the agent. The agent replicates ITS OWN user's taste.

## Waybar on NixOS (taste · example)

### Enable
```nix
programs.waybar.enable = true;
```

Config files:
- `~/.config/waybar/config` — JSONC, module layout
- `~/.config/waybar/style.css` — CSS styling

### Nerd Fonts
```nix
fonts.packages = with pkgs; [
    nerd-fonts.jetbrains-mono
];
```

### Pill layout (Catppuccin Mocha)
Transparent bar, each module its own "pill" with a border:

```css
window#waybar { background: transparent; }
#workspaces {
    background: #1E1E2E;
    border: 1px solid #313244;
    border-radius: 10px;
    padding: 0 8px;
    margin: 4px 12px 4px 0;
}
#clock {
    background: #1E1E2E;
    border: 1px solid #45475A;
    border-radius: 10px;
    padding: 0 20px;
    margin: 4px 0;
    font-weight: 700;
}
#cpu, #memory, #pulseaudio, #backlight, #battery, #network {
    background: #1E1E2E;
    border: 1px solid #313244;
    border-radius: 10px;
    padding: 0 10px;
    margin: 4px 1px;
}
```

### Clock format (version-dependent!)
| Waybar version | Format |
|---|---|
| ≤ 0.9.x | `"%H:%M"` |
| ≥ 0.11 | `"{0:%H:%M}"` — the positional `0:` is mandatory |

### Memory icon
Use `` (nf-oct-memory, U+E266) — Octicons, the most stable across Nerd Fonts versions.

### wpctl volume — ALWAYS cap it
```bash
wpctl set-volume -l 1.0 @DEFAULT_AUDIO_SINK@ 5%+
```

### Hover effects (subtle, no 3D/inversion)
```css
#workspaces button { transition: none; }
#workspaces button:not(.active):hover {
    background: #313244; color: #A6ADC8; box-shadow: none;
}
#workspaces button.active:hover {
    background: #b89ae8; color: #1E1E2E; box-shadow: none;
}
```

### Tooltip styling
```css
tooltip {
    background: rgba(30, 30, 46, 0.94);
    border: 1px solid #CBA6F7;
    border-radius: 10px;
    padding: 8px 12px;
}
```

## Focus ring in Niri

```kdl
layout {
    focus-ring {
        width 2
        active-color "#CBA6F7"     # Mauve
        inactive-color "#313244"   # Surface0
    }
}
```

**Use `layout { focus-ring { ... } }`, NOT `borders { ... }`** — the old syntax
leads to the config being silently rejected.

## Fuzzel launcher

Config: `~/.config/fuzzel/fuzzel.ini`

```ini
[main]
font=JetBrains Mono Nerd Font:size=14
width=40
lines=12
border-radius=10
border-width=2

[colors]
background=1E1E2Eff
text=CDD6F4ff
match=CBA6F7ff
selection=CBA6F7ff
selection-text=1E1E2Eff
border=CBA6F7ff
```

**PITFALL:** `launch-prefix=app` silently breaks app launching. Remove it.

## Dunst notification daemon

```ini
[global]
    font = JetBrains Mono Nerd Font 10
    geometry = "250x5-12-36"
    padding = 6
    horizontal_padding = 8
    max_icon_size = 24
    mouse_left_click = close_current
```

Install: `nix profile install nixpkgs#dunst` or add to `environment.systemPackages`.

## SwayOSD — volume/brightness OSD

```nix
environment.systemPackages = with pkgs; [ swayosd ];
```

Autostart in niri: `spawn-at-startup "swayosd-server"`

Integration in waybar (instead of raw wpctl):
```json
"pulseaudio": {
    "on-click": "swayosd-client --output-volume mute-toggle",
    "on-scroll-up": "swayosd-client --output-volume raise",
    "on-scroll-down": "swayosd-client --output-volume lower"
}
```

**PITFALL:** `swayosd-client` is unavailable until `nixos-rebuild switch`.

## GTK theming (without home-manager)

```nix
environment.systemPackages = with pkgs; [
    (catppuccin-gtk.override {
        variant = "mocha";
        accents = ["mauve"];
        size = "standard";
    })
];
environment.sessionVariables.GTK_THEME = "catppuccin-mocha-mauve-standard";
```

**IMPORTANT:** bare `catppuccin-gtk` defaults to frappe/blue. Use `.override`.

## Swaybg — wallpaper for niri

```bash
nix profile install nixpkgs#swaybg
```

In the niri config:
```kdl
spawn-at-startup "swaybg" "-i" "/path/to/wallpaper.png" "-m" "fill"
```

## EFI boot order

```bash
sudo efibootmgr                           # list
sudo efibootmgr --bootorder 0001,0000     # reorder (NixOS first)
```

## Serial device permissions

```nix
users.users.YOUR_USER.extraGroups = [ "dialout" ];
```

Or via udev (no session restart needed):
```nix
services.udev.extraRules = ''
  SUBSYSTEM=="tty", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="5740", MODE:="0666"
  SUBSYSTEM=="usb", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="5740", MODE:="0666", GROUP="dialout"
'';
```

**Use `:=`, not `=`** — system rules override a plain `=`.
(VID `0483` / PID `5740` is an STMicroelectronics USB-CDC serial; a FlipperZero, for example, identifies the same way.)

Check permissions and the VID/PID of a plugged-in device:
```bash
ls -la /dev/ttyACM0                                          # expect crw-rw-rw-
udevadm info -a -n /dev/ttyACM0 | grep -E 'idVendor|idProduct' | head -2
```

## HDD auto-mount (NTFS)

```bash
sudo blkid /dev/sda2    # get the UUID
```

```nix
fileSystems."/mnt/data" = {
    device = "/dev/disk/by-uuid/YOUR_UUID";
    fsType = "ntfs-3g";
    options = ["uid=1000" "gid=100" "noatime"];
};
```

## Screenshots: Grim + Slurp + Satty

```kdl
Print        { screenshot; }
Mod+Shift+S  { spawn "sh" "-c" "grim -g \"$(slurp)\" - | satty -f -"; }
```

## Fastfetch (taste · example)

```jsonc
{
  "logo": { "source": "NixOS_small", "padding": { "top": 1, "left": 2 } },
  "display": { "separator": " \u001b[38;2;203;166;247m→\u001b[0m ", "key": { "width": 12 } },
  "modules": [
    {"type": "title", "keyColor": "#CBA6F7"},
    {"type": "separator"},
    {"type": "os", "keyColor": "#CBA6F7"},
    {"type": "cpu", "keyColor": "#CBA6F7"},
    {"type": "gpu", "keyColor": "#CBA6F7"},
    {"type": "memory", "keyColor": "#CBA6F7"},
    {"type": "disk", "keyColor": "#CBA6F7"},
    {"type": "localip", "keyColor": "#CBA6F7"}
  ]
}
```

## Rebuild by the agent's own hand (full autonomy, deliberate risk)

To let the agent run `nixos-rebuild switch` itself without a password:
```nix
security.sudo.extraRules = [{
    users = ["YOUR_USER"];
    commands = [{ command = "ALL"; options = ["NOPASSWD"]; }];
}];
```

**This is a deliberate choice, not an oversight.** `command = "ALL"` + NOPASSWD gives the agent
passwordless `sudo` over EVERYTHING. That's by design — for the sake of FULL agent autonomy on
YOUR OWN personal machine, with the risks accepted: a mistaken or compromised agent gets root
in full. This is NOT for work, shared, or production machines.

Want less risk — narrow it to a single command (the agent will only be able to rebuild the system):
```nix
commands = [{ command = "/run/current-system/sw/bin/nixos-rebuild"; options = ["NOPASSWD"]; }];
```

## See also
- `nixos-agent-environment` — the agent's environment and working patterns on NixOS
- `nixos-nix-ld-electron` — Electron apps and dependencies
- `nixos-streaming` — Sunshine/Moonlight
- `niri-hotkeys` — niri hotkeys
