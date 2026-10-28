---
id: kisa-linux-setup
name: Set up KISA's Linux desktop on your own machine
summary: >-
  A route from environment inventory to an adapted ShojiWM/Quickshell desktop,
  including application mappings, optional widgets, wallpaper runtime and handoff.
type: route
author: kisa
recommended: false
added: 2026-10-28
tags: [linux, desktop, dotfiles, kisa-stack, shojiwm, quickshell, installation, wallpaper, adaptation]
steps:
  - title: Establish the machine and requested desktop
    action: read
    ref: kisa-dotfiles
    body: >-
      Read the actual dotfiles checkout and pins. Identify distro, GPU, session,
      outputs, XDG paths and existing configs. Resolve complete desktop versus
      selected components and the recipient's application/integration preferences.
  - title: Resolve dependencies and application mappings
    action: read
    ref: kisa-linux-desktop
    body: >-
      Follow the capability table and repository dependency docs. Trace selected
      apps through dock, launcher, binds, autostart and helpers. Translate package
      capabilities for the distro; do not install the reference package inventory.
  - title: Prepare the pinned stack and recoverable configuration
    action: configure
    ref: kisa-dotfiles
    body: >-
      Within authorization, prepare the pinned compositor, launcher and Qt assets.
      Preserve existing customizations, inspect backups and installer preview, then
      apply selected components. Adapt monitor, input, app, shell and service paths.
  - title: Complete the selected wallpaper and widget chains
    action: configure
    ref: kisa-linux-desktop
    body: >-
      For animation, supply the complete private engine/CEF/mpv and owned content.
      For MateEngine, use the matching Linux bridge. Keep account widgets opt-in.
      Resolve gaps or agree on alternatives; never silently present fallback as success.
  - title: Activate at the agreed boundary and report evidence
    action: read
    ref: kisa-dotfiles
    body: >-
      Perform only authorized activation and checks. Distinguish source, build and
      live behavior; leave tests to the user when requested. Report every selected
      feature, blockers, unverified behavior, source pins and backup/restore paths.
---

# Set up my desktop for another person

Use this route for a new installation or a broad adaptation of KISA's dotfiles.
For one broken component, load `kisa-dotfiles` and its relevant repository docs
directly. This route preserves the user's chosen scope and permissions; it does
not turn a request to read the guide into permission to install or log out.

The older NixOS/niri route in this MCP is a separate setup. Do not mix its configs
into ShojiWM merely because the recipient uses NixOS.
