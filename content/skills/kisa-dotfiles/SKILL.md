---
id: kisa-dotfiles
name: kisa-dotfiles
summary: >-
  Adapt KISA's Linux desktop dotfiles to the recipient's hardware, applications
  and distribution, completing dependency, widget and wallpaper integration.
type: skill
author: kisa
recommended: false
added: 2026-10-28
tags: [linux, desktop, dotfiles, kisa-stack, shojiwm, quickshell, installation, wallpaper]
source: https://github.com/howdeploy/kisa-stack/tree/main/dotfiles
description: >-
  Install, adapt, update or repair howdeploy/kisa-stack desktop dotfiles for a
  user's Linux machine: ShojiWM, Quickshell, Walker, applications, widgets and
  animated wallpapers. Use for reproducing KISA's desktop or fixing an incomplete
  deployment; not for unrelated Linux administration or coding-agent configuration.
triggers:
  - adapt KISA dotfiles for my machine
  - install kisa-stack desktop
  - fix missing widgets or animated wallpapers in KISA desktop
reminder: Trace each requested feature through configuration, dependencies, local inputs and activation; copying files is not a verified deployment.
---

# Adapt KISA desktop dotfiles

Work on [howdeploy/kisa-stack/dotfiles](https://github.com/howdeploy/kisa-stack/tree/main/dotfiles).
Preserve the requested desktop and the recipient's working environment. The guide
does not grant extra permissions, require tests or authorize session restarts.

## Read and establish the target

- Read the selected checkout's `dotfiles/README.md`, `AGENTS.md`, `sources.json`
  and `docs/install.md`. Record revision, dirty state and intended destination:
  publication source or installed configuration. They are separate copies.
- Retrieve `kisa-linux-desktop` through this MCP's `get_item` for the detailed
  guide. Without MCP access, use the repository docs directly; do not require a
  new MCP connection to use this skill. Read component docs as needed.
- Establish the actual distro, package manager, GPU/driver, RAM, active session,
  home/XDG directories, monitor modes/scales, layouts and existing configs.
  Verify unknown facts read-only; ask about unresolved user preferences.
- Confirm complete desktop versus components and requested animation, MateEngine,
  applications and integrations. Preserve existing authorization; do not ask again
  for steps already authorized, or infer install authority from a catalog lookup.

## Resolve every selected feature

Keep a small table: feature, required dependency/local input, actual evidence,
planned adaptation and status. Follow references into source when docs do not
explain the behavior. Do not stop at copying a config or hiding an error.

| Area | Required check |
| --- | --- |
| Base stack | Pinned howdeploy/ShojiWM fork/SDK lock APIs; compatible Quickshell/Qt modules; Elephant providers; patched Walker; generated Qt shaders |
| Applications | Dock/favorites, hotkeys, autostart and helper callers; actual executable/arguments, desktop ID, app ID and icon; preferred terminal and file manager |
| Hardware | Actual output names, scale, geometry, input layout, GPU support; never transplant the author's kernel, NVIDIA package or monitor names |
| Widgets | Requested preset membership, dependency/CLI protocol and explicit enable flag; account/session collectors stay opt-in |
| Wallpaper | Selected engine executable, full CEF/private mpv runtime and patches, owned assets, matching library paths; static fallback disclosed |
| Lock/screensaver | PAM service, generic compositor API, optional matching MateEngine Linux bridge; preview is not authentication |

Use `dependencies/README.md` and curated profiles as requirements. Reference
package inventories are not install scripts. On another distribution translate
capabilities and verify current availability; do not paste Arch package commands.
If a preferred app differs, update all affected callers and launch conventions.
Do not silently delete requested widgets/features to avoid resolving dependencies.

## Apply the adaptation within scope

1. Describe the files and components to change. Preserve unrelated dirty work.
   Inspect existing targets and prepare recoverable backups before replacement.
2. Follow `docs/install.md` for dependency/build order. Run builds or checks only
   when authorized. Do not substitute stock upstream binaries for required forks
   or apply already integrated patches twice.
3. Use the existing installer preview and selected components before an authorized
   `--apply`; never run the user-file installer as root. Inspect its preservation
   rules: whole-directory backups do not merge all prior customizations.
4. Adapt local output, input, application, shell, polkit, wallpaper and XDG paths.
   Preserve shader ABIs, widget preset membership and lock authentication behavior.
   Keep credentials and account/session state out of the public checkout.
5. Activate only at an authorized boundary. Config copying does not install the
   private wallpaper runtime, build a MateEngine bridge or restart an old process.

Missing inputs are explicit blockers. Explain the missing capability and complete
independent work; ask for a user decision only where the result needs one. Keep a
requested feature until it works or the user agrees to an alternative.

## Verify and hand off accurately

Use permitted evidence for each selected feature. If authorized, exercise actual
launches/controls, wallpaper playback and resource trends; treat lock/unlock and
DPMS as deliberate recovery-aware checks. Do not launch checks reserved to the user.

Report source pins, installed paths, changed app mappings, chosen integrations,
backup/restore locations and activation steps. Mark each feature as verified,
configured but unverified, blocked, or omitted by user choice. State checks that
were not performed. A successful copy/build or historical author's result is not
proof that the recipient's complete desktop works.
