---
id: niri-hotkeys
name: 'Niri: hotkeys and config'
summary: >-
  A niri hotkey reference + practice: the built-in overlay of all binds
  (Mod+Shift+/), how the agent edits binds in config.kdl with live-reload, and
  the critical Super/WIN conflict when streaming to a PC (Wayland won't hand Win
  to the client) with a fix via Sunshine.
type: knowledge
author: kisa
recommended: false
added: 2026-07-04
tags: [nixos, niri, wayland, hotkeys, compositor, streaming, config]
source: https://github.com/niri-wm/niri/wiki/Configuration:-Key-Bindings
---

# Niri hotkeys

Niri is a scrollable tiling Wayland compositor. `Mod` = Super.

## Cheat sheet: overlay with every hotkey

Can't remember a bind — don't guess. niri has a built-in **Important Hotkeys**: press **`Mod+Shift+/`**
(Super+Shift+Slash) — a list of the important binds pops up. The same one shows at session start.

- Spawn binds in the overlay are unnamed unless you set a title. Give them a name with the
  `hotkey-overlay-title="..."` property (niri v25.02+); to hide a bind from the list — `hotkey-overlay-title=null`.
  Titles support Pango markup.
- Need SEARCH over binds rather than a static list — install the fuzzel menu from the community scripts
  `heyoeyo/niri_tweaks`: it parses `config.kdl` and gives fuzzy search over every hotkey.

## Focus
| Hotkey | Action |
|---|---|
| Mod+Arrows or H/J/K/L | Focus a column/window |
| Mod+Home/End | To start/end of column |

## Move
| Hotkey | Action |
|---|---|
| Mod+Shift+←→ or H/L | Move column |
| Mod+Shift+↑↓ or K/J | Move window within column |

## Resize
| Hotkey | Action |
|---|---|
| Mod+R | Column width |
| Mod+Shift+R | Window height |
| Mod+Ctrl+R | Reset height |
| Mod+F | Maximize column |
| Mod+Shift+F | Fullscreen |
| Mod+Shift+T | Floating window |

## Workspaces
| Hotkey | Action |
|---|---|
| Mod+1-4 | Switch to workspace |
| Mod+Shift+1-4 | Move column to workspace |
| Mod+Ctrl+↑↓ | Move to workspace |
| Mod+Ctrl+J/K | Focus between workspaces |

## Launch
| Hotkey | Action |
|---|---|
| Mod+Return | Terminal |
| Mod+D | Launcher (fuzzel) |
| Mod+B | Browser |

## System
| Hotkey | Action |
|---|---|
| Mod+Shift+E | Exit niri |
| Print | Screenshot the whole screen |
| Mod+Shift+S | Screenshot a region → annotate |

## Language
| Hotkey | Action |
|---|---|
| Shift+Alt | Switch layout |

## Config location
- `~/.config/niri/config.kdl`
- Reload: `niri msg action load-config-file`
- Focus ring: `layout { focus-ring { width 2 active-color "#CBA6F7" inactive-color "#313244" } }`

## How to change hotkeys (agent instructions)

Binds live in the `binds { }` section of `~/.config/niri/config.kdl`. Each is a hotkey followed by
ONE action in braces:

```kdl
binds {
    Mod+Return hotkey-overlay-title="Terminal" { spawn "alacritty"; }
    Mod+D { spawn "fuzzel"; }
    Mod+Shift+E { quit; }
}
```

- A hotkey = modifiers joined by `+` and an XKB key name at the end. Modifiers: `Ctrl`/`Control`,
  `Shift`, `Alt`, `Super`/`Win`, `Mod`. `Mod` = Super (reconfigurable).
- **Apply:** niri re-reads the config on save (auto-reload) or manually with
  `niri msg action load-config-file`. Parsing runs on a separate thread, no freeze.
- **GOTCHA:** the `binds { }` section does NOT pull in defaults if you omit it — edit the
  existing one, don't replace it with an empty one, or you'll lose all binds.
- Give new spawn binds a `hotkey-overlay-title` right away, otherwise they're unnamed in the overlay.

## Streaming: the Super/WIN conflict (important)

You stream the niri desktop to a PC via Sunshine/Moonlight — the hotkeys don't fire. The cause is
technical, not a config bug: **Wayland won't hand the Win key to the client** (verbatim from the Sunshine
docs). Super pressed on the PC client is intercepted by the client ITSELF (it opens the Windows Start
menu) and never reaches the host. And all niri binds hang off `Mod`=Super → you can't enter them from the PC.

What to do:
- **Sunshine `key_rightalt_to_key_win`** — the host treats right Alt as the Windows key. Press Right Alt on
  the client → niri sees Super, the binds work.
- Or **duplicate the key binds onto a non-Super modifier** (Alt/Ctrl) specifically for streaming.
- Moonlight can toggle capture of system combos (`Ctrl+Alt+Shift+Z`), but Win is a special case.

More on desktop streaming itself — the `nixos-streaming` knowledge item.

## Pitfalls
- KDL parsing is strict — invalid blocks lead to the config being silently rejected
- Keep a working backup: `~/.config/niri/config.kdl.bak`
- Binaries from `nix profile` need FULL paths in `spawn-at-startup`
