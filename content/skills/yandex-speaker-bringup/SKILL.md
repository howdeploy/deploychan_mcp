---
id: yandex-speaker-bringup
name: Bring up an owned Yandex speaker for an agent
description: >-
  Assess and set up an owned Yandex speaker as an agent audio terminal: model/firmware
  compatibility, bounded root bootstrap, persistent maintenance, private backup and
  intentional isolation. Use for device bring-up or its recovery, not ordinary desktop commands.
summary: >-
  A recoverable, model-specific bring-up workflow using the Yandex Station Extended
  community reference; avoids household DNS dependence, blind flashing and unsupported
  claims about USB or raw NAND restore.
type: skill
author: kisa
recommended: false
added: 2026-10-27
tags: [yandex, mini1, root, adb, ssh, recovery, voice, hardware]
source: https://hackalice.me/
reminder: Identify model and firmware first; a working shell is not a verified recovery image or a replacement assistant.
---

# Speaker bring-up

Use the exact user-owned target and requested features. The reference experience is
Mini 1 YNDX-0004; other models require their own compatibility evidence. This skill
is a procedure, not a bundled exploit/firmware installer.

1. Identify hardware label, current build, power/data connection, host OS, router
   control and existing access. State which functions require the PC or a provider.
   If connected to Deploychan MCP, retrieve `yandex-speaker-feasibility` for the matrix.
2. Read the current [community root instructions](https://hackalice.me/start/root/)
   and matching device page. Preserve network settings and explain any required reset.
   Do not update or reset an unidentified device just to see whether access appears.
3. Prepare the chosen local/scoped bootstrap and verify it is ready before directing
   the user to change DNS or connect the speaker. Record each original setting and
   corresponding undo step. Confirm real requests/access, not only service status.
4. Inspect and apply the appropriate [SSH/update procedure](https://hackalice.me/start/ssh/)
   within authorization. Protect maintenance access from untrusted networks and
   record actual persistence. Do not copy immutable markers or scripts across models.
5. Acquire private, versioned backup evidence. Preserve identity/geometry, tools,
   hashes and incomplete reads. Distinguish corrected logical NAND, raw/OOB dumps,
   USB ADB and hardware recovery. Do not write bootloader or factory identity as
   a routine bring-up step. Details: `yandex-speaker-access-and-recovery` via MCP.
6. Restore original household DNS and retire bootstrap services at a safe boundary.
   Keep device isolation and LAN maintenance separate. Inspect boot restoration,
   IPv6 and vendor error behavior instead of assuming a firewall creates a local assistant.
7. Verify an agreed reboot/recovery boundary only when authorized. Record actual
   access, service restoration and retained volume/settings; leave unperformed
   recovery tests explicitly unverified.

Use [community recovery](https://hackalice.me/start/recovery/) for model-specific
rollback. A replacement assistant daemon, BetterYAM and USB-host/AirPlay recipes are
optional migrations/features; do not install them just because root is available.

Deliver a short feasibility/access report, private backup location, changes and
rollback, user actions still required, and the next audio/agent integration step.
Never publish the backup, device identity, account data, LAN addressing or credentials.
