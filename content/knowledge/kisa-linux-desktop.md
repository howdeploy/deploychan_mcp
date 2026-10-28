---
id: kisa-linux-desktop
name: KISA's Linux desktop setup and adaptation guide
summary: >-
  Deploy KISA's ShojiWM and Quickshell dotfiles on your own Linux machine:
  resolve dependencies and application IDs, preserve existing configs, build
  the pinned wallpaper runtime, and distinguish installation from verified behavior.
type: knowledge
author: kisa
recommended: false
added: 2026-10-28
tags: [linux, desktop, dotfiles, kisa-stack, shojiwm, quickshell, wallpaper, installation, adaptation]
source: https://github.com/howdeploy/kisa-stack/tree/main/dotfiles
---

# My Linux desktop: adapt the whole chain

I publish my desktop in [kisa-stack/dotfiles](https://github.com/howdeploy/kisa-stack/tree/main/dotfiles).
It contains a ShojiWM compositor configuration, a Quickshell panel/dock/locker,
Walker, shaders, wallpaper helpers and optional widgets. It is a maintained source
setup, not an image of my machine. My installed-application inventory is context,
not a command to install every package I happen to use.

When someone asks an agent to set this up, I expect it to follow each selected
feature through configuration, dependencies, launch and local inputs. Copying QML
and saying "done" leaves people with broken buttons and missing wallpaper engines.
Adapt the setup to the person while preserving the features they requested.

Through this MCP, retrieve skill `kisa-dotfiles` for the working procedure or route
`kisa-linux-setup` for the ordered setup. Neither reading a guide nor enabling a
catalog entry authorizes system changes. Follow the user's existing authorization.

## Read the current source before choosing commands

Start with `dotfiles/README.md`, `dotfiles/AGENTS.md`, `dotfiles/sources.json` and
`dotfiles/docs/install.md` in the selected checkout. Record its commit and dirty
state. Read the component docs below only when relevant. A published pin says
which source to build; it does not prove which binary the recipient is running.

The reference platform recorded on 2026-10-28 is Manjaro/Arch. Other distributions
need equivalent capabilities and supported library versions, not pasted `pacman`
commands. Resolve current package availability using the recipient's distribution
and primary project documentation. NixOS needs a declarative adaptation; this is
not the separate older niri/NixOS configuration in this catalog.

| Selected feature | Source of truth and required adaptation |
| --- | --- |
| Compositor and lock API | `sources.json`, `scripts/build-shojiwm.sh`, `docs/fork.md`; use the pinned howdeploy/ShojiWM integration fork, not an arbitrary upstream package |
| Panel, dock, settings | `config/shoji-shell/`, `docs/configuration.md`; match Quickshell modules and Qt versions, fonts, icons, local commands and outputs |
| Launcher | `scripts/build-walker.sh`, `config/walker/`, `config/elephant/`; the patched Walker theme needs its matching binary and Elephant providers/user service |
| Shader assets | `scripts/build-shaders.sh`, `docs/shaders.md`; Qt `.qsb` files are generated, not shipped; compositor GLSL uses a different ABI |
| Applications | `dependencies/README.md`, curated profiles, dock, favorites and TSX bindings; resolve actual desktop-entry IDs, executables and arguments |
| Wallpaper engine | `docs/wallpaper-engine.md`, private runtime builder and pinned patches; needs engine/CEF/mpv plus the user's own content |
| MateEngine on lock | `docs/mateengine.md`, `docs/lock-scene.md`; requires matching Linux app bridge and compositor, not just QML |
| Account/session widgets | `docs/widgets.md`, `integrations.env.example`, collectors; independent opt-in, supported CLI protocol and the recipient's credentials |

All paths above are relative to `dotfiles/`. If a document, dependency or source
cannot be accessed, name the missing input; do not replace it with a guessed API.

## Find the recipient's actual environment

Use available read-only evidence for distribution, home/XDG paths, GPU/driver,
RAM, display outputs/modes/scales, input layouts and the active desktop/session.
Remote-shell environment variables alone may describe an older login. Inspect
the running compositor and its config path when access permits. Do not invent
monitor names, enforce my keyboard layouts or copy my GPU/kernel packages.

Agree on the desired features: complete desktop or selected components, static
or animated wallpaper, optional MateEngine, preferred terminal/file manager and
account widgets. Infer facts from the machine; ask only about preferences or
material choices that remain unresolved. Preserve the current recovery desktop.

For each selected component, keep a compact table of requirement, local evidence,
necessary change and status. Distinguish a missing package, unsupported version,
missing generated asset, disabled integration and missing owned content. Those
are different faults and need different fixes.

## Applications are part of the configuration

Trace dock pins, Walker favorites, hotkeys, autostart/services and helper scripts.
An app's executable, Wayland app ID and `.desktop` ID are not interchangeable.
Check installed desktop entries and their `Exec`/`Icon` values, including Flatpak
exports if selected, rather than guessing from a package name.

For example, choosing a different terminal requires checking the terminal hotkey,
launcher `terminal=true` behavior, helper invocations and flags. Renaming one
Ghostty reference does not complete the adaptation. Keep native app-icon lookup.
An unavailable personal app should be installed within scope, replaced by the
user's chosen equivalent, or explicitly left unavailable. Do not silently remove
a requested workflow to make a launch appear successful.

Review curated `arch.txt`, optional `arch-wallpaper.txt` and `arch-integrations.txt`
separately. The `reference-*` inventories include unrelated applications, kernels,
drivers and a recovery desktop; never feed those inventories to a package manager.
Foreign pacman entries are not proof that an AUR package exists. Do not copy
account profiles, launch arguments containing secrets or my private home paths.

## Install sources, generated assets and local settings at the right layer

Follow the checkout's installation guide in dependency order: prerequisites,
pinned compositor, patched launcher and Qt shaders, optional wallpaper runtime,
then user-file preview and application. The build helpers print install commands;
read them and respect build, system-install and session-change authorization.
Do not run tests, builds or graphical checks if the user has reserved them.

`scripts/install.py` defaults to a preview. `--apply` changes user files; it is not
a package installer. `--component` selects scope. The wallpaper runtime is a
separate component with a required `--wallpaper-bundle`. The default config copy
does not build or install that runtime. Never run the user-file installer as root.

The installer copies rather than symlinks configuration. Adapt the installed copy
for the recipient, or explicitly target a distributable source change. Inspect
existing files first: the installer backs up whole component directories and
preserves specific local state files, not every customization. Read its current
behavior and backup manifest before applying over an existing setup. Keep a
recoverable backup of local changes; do not assume automatic merging or rollback.

Adapt output selection/scaling, layouts, shell choice, polkit/NetworkManager secret
agent paths, application IDs and wallpaper locations. Preserve XDG resolution and
the generated `shoji_wm` runtime link. Do not modify `/usr/lib` to customize styling
or overwrite an unrelated desktop's portal/credential configuration.

## Animated wallpapers and locking are a chain, not a checkbox

The private builder supplies a complete engine/CEF and patched mpv. Follow the
current pins and patch order. The media polling/D-Bus fix and the mpv OpenGL-fence
fix address different causes; upstream inclusion depends on the selected revision.
Do not double-apply a patch already present. An arbitrary system engine fallback
does not establish that either fix is installed.

The recipient supplies their own Steam/Wallpaper Engine assets and Workshop data.
MateEngine additionally requires the matching Linux build, bridge and owned inputs
described in its guide. Neither is bundled with dotfiles. Resolve the actual
selected executable and private library path, not merely an installed package name.

If assets, runtime or hardware support are missing, report the exact gap. A static
wallpaper is a valid chosen mode or disclosed fallback, not proof that animated
wallpapers work. Keep requested animation/screen-saver behavior in scope until it
works or the user agrees to a different result. Avoid duplicate engine processes
or separate polling loops as a workaround for a lifecycle bug.

The locker uses PAM and the compositor's session-lock API. Animated wallpaper and
MateEngine backgrounds remain underneath the password UI; they do not authenticate
or receive password input. The unlock wave needs matching compositor support.
Do not weaken authentication to work around a distro mismatch. First lock/unlock,
idle/DPMS and multi-output checks require a deliberate user-authorized session
with a recovery path. A preview does not verify password authentication.

## Optional widgets and honest completion

The public first-run preset is empty and integrations are independently off. A
preset selects placement; a flag, dependency and supported provider protocol make
an integration available. Existing CLI authentication is not permission to enable
it. Preserve both QML and collector opt-in gates, including session/history readers.
Keep local credentials, `integrations.env`, caches and session databases private.

Completion means every selected feature has an explicit disposition: configured
and verified, configured but unverified, blocked with a concrete cause, or omitted
by the user's choice. Do not declare success because a process started. When
authorized, check the actual app launch, icons, controls, media, output behavior,
wallpaper playback and resource trend for the selected scope. Resource claims need
a duration, workload and process set, including engine children; do not promise a
RAM saving from my historical observations or confuse stable memory with low memory.

Report the checkout/pins, installed paths, changes to app mappings, enabled
integrations, backup/restore locations, activation steps and remaining gaps.
Separate source review, build success and the recipient's runtime verification.
The publication's `docs/validation.md` records limitations; my local acceptance
does not validate a fresh machine or every newly published source combination.
