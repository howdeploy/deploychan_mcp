---
id: codex-desktop-linux
name: ChatGPT Desktop for Linux (codex-desktop-linux)
summary: >-
  KISA's field-tested guide to the unofficial ChatGPT Desktop for Linux (Chat, Work, and
  Codex), built locally from OpenAI's upstream macOS DMG. How to install (native package /
  Nix / AppImage), and how to bring the GPT-5.6 Sol / Terra / Luna model picker back into the
  UI via the opt-in ui-tweaks feature.
type: tool
author: third_party
recommended: true
added: 2026-07-10
tags: [chatgpt, codex, linux, desktop, install, nix, gpt-5.6]
source: https://github.com/ilysenko/codex-desktop-linux
---

# ChatGPT Desktop for Linux (codex-desktop-linux)

The official ChatGPT desktop app ships for macOS and Windows only. `codex-desktop-linux` is
an unofficial Linux build wrapper that converts the upstream macOS `Codex.dmg` into a runnable
Linux Electron app — Chat, Work, and Codex in one window. It builds native `.deb`, `.rpm`, and
`.pkg.tar.zst` packages, supports AppImage self-builds and Nix, and runs on both Wayland and
X11.

Repo: `https://github.com/ilysenko/codex-desktop-linux`

## Install

Start from a checkout for native packages and AppImage:

```bash
git clone https://github.com/ilysenko/codex-desktop-linux.git
cd codex-desktop-linux
```

| Distro | Path |
|---|---|
| Debian / Ubuntu / Pop!_OS / Mint | `make bootstrap-native` (builds + installs a `.deb`) |
| Fedora / openSUSE | `make bootstrap-native` (builds + installs an `.rpm`) |
| Arch / Manjaro / EndeavourOS | `make bootstrap-native` (builds + installs a pacman package) |
| NixOS / Nix | `nix run github:ilysenko/codex-desktop-linux` |
| Atomic / other | `make build-app && make appimage` (local self-build, no bundled updater) |

The installer downloads or reuses the DMG, extracts the Electron app, applies Linux
compatibility patches, rebuilds native modules, and packages the result.

**The Codex CLI is required at runtime.** The first launch can install `@openai/codex` with
the bundled `npm`, or you manage it yourself. If you install it manually, include optional
dependencies so the Linux platform binary is present:

```bash
npm i -g --include=optional @openai/codex
```

Pin a specific binary with `CODEX_CLI_PATH=/path/to/codex` when the GUI can't find it.

## The GPT-5.6 Sol problem — and the fix (field-tested)

**Symptom:** the CLI can select `gpt-5.6-sol` (also `-terra`, `-luna`), but the Desktop model
picker doesn't show them.

**Cause:** the local app-server already returns those models with `hidden: false`, but the
Desktop frontend filters them out through a stale `available_models` whitelist. So the model
exists on the backend and the picker hides it. This is not an account problem and not a Linux
bug — it's an out-of-date model list in the UI.

**Fix:** it landed in PR #756 as the opt-in `ui-tweaks` feature. Optional Linux features live
in `linux-features/` and stay disabled unless you turn them on before building.

1. Enable the feature in the local, git-ignored feature config
   (`linux-features/features.json`):

   ```json
   {
     "enabled": ["ui-tweaks"]
   }
   ```

2. Rebuild a fresh client and run it:

   ```bash
   nix develop -c make build-app-fresh
   nix develop -c make run-app
   ```

   (The plain `make build-app-fresh` / `make run-app` targets work too; the `nix develop -c`
   wrapper just runs them inside the flake's dev shell.)

**Why plain `nix run github:ilysenko/codex-desktop-linux` does NOT include this patch:**
`ui-tweaks` is disabled by default and has no separate Nix output yet. You have to enable the
feature and rebuild the client yourself, as above.

**Caveat — read this.** The patch only makes Sol *visible* in the UI. Final access to the model
still depends on your OpenAI account entitlement. Rebuilding the wrapper does not unlock model
rollouts — those stay controlled by OpenAI per account.

## Importing a pet (a lesson learned)

When a locally-imported pet failed while every other pet worked, the fault was the **imported
file**, not the Linux overlay. Two client-side mistakes: it couldn't handle a
temporary signed link to the original, and it accepted a plain single PNG as a finished sprite
sheet without checking dimensions, grid, or alpha. Before installing, the client should reject
an unsuitable PNG with a clear error. (Sprite-sheet format: see the `chatgpt-work-pets` note.)

## Troubleshooting (highlights)

| Problem | First thing to try |
|---|---|
| `/tmp` mounted `noexec` | Set `TMPDIR` and `XDG_CACHE_HOME` to executable dirs under `$HOME` |
| Blank window / stuck splash | Check `~/.cache/codex-desktop/launcher.log`; is port `5175` in use? |
| CLI not found | Set `CODEX_CLI_PATH`, or install `@openai/codex` with optional deps |
| UI oversized / blurry (HiDPI) | `CODEX_FORCE_DEVICE_SCALE_FACTOR=1 ./codex-app/start.sh` |
| Wayland / GPU hang | `CODEX_LINUX_RENDERING_MODE=wayland-gpu ./codex-app/start.sh` |

Full list lives in the repo's `docs/troubleshooting.md`.
