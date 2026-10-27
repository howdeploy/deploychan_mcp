---
id: voice-desktop-control
name: Add typed voice control and focused dictation to Linux
description: >-
  Implement or repair host-side voice routing after ASR: exact desktop/application
  commands, clipboard dictation, mode switching and locked-screen behavior. Reuse an
  existing wake detector rather than retraining it for every PC action.
summary: >-
  A deterministic Linux control layer for workspaces, media, brightness, application
  launch/close and avatar bridges, with focus-aware paste, explicit formatting and
  separate accepted/completed outcomes.
type: skill
author: kisa
recommended: false
added: 2026-10-27
tags: [linux, voice, gigaam, dictation, clipboard, ipc, media, mateengine, automation]
source: https://github.com/salute-developers/GigaAM
reminder: Match complete supported phrases, consume handled commands, and keep a paste distinct from sending a message or unlocking a session.
---

# Host voice control

Read the existing activation, ASR, stop and delivery paths before editing. Keep the
user's current speaker trigger and text destination. Retrieve
`voice-input-and-desktop-routing` through Deploychan MCP for application examples.

1. Identify the real user session, compositor, player, display identities and installed
   application entrypoints. Keep one warm ASR service; distinguish inference from
   endpointing and transport. Do not change microphone routing just to add a parser.
2. Add exact normalized command aliases. For numbered targets support cardinal and
   ordinal forms and both natural word orders; include the user's short form.
   Dictation containing the same words must not execute an action.
3. Map to typed, bounded adapters. Use compositor IPC, the actual media player's
   supported controls, stable monitor identity with bounded brightness, and graceful
   application launch/close. Select installed releases by parsed versions and policy.
4. For application bridges, define an action, typed target and request ID. Keep
   accepted, completed, unsupported and failed states distinct. An avatar's sitting,
   hiding, dance selection or portrait mode is an application transition, not merely
   a coordinate change. A renderer-specific path cannot be guessed from another app.
5. Consume a handled action before agent delivery. Report failure through the existing
   notification/status channel; do not also forward the command as a normal prompt.
6. For dictation, provide an explicit target-mode hotkey/status. Capture and recheck
   the focused field, put the completed text on the clipboard and invoke the permitted
   paste mechanism. Never add Enter/send without the user's requested workflow.
   Support an explicit paragraph phrase with a literal escape if desired.
7. While locked, distinguish blanking from suspension/network loss. Keep permitted
   media/display-wake controls in the session service. Show the password screen
   rather than bypassing the lock; do not paste private text into an unverified field.

Keep spoken acknowledgements optional and explicitly requested, except for the
user's chosen short device cues. Respect current volume and stop behavior. A failing
next-track action can be a missing website Media Session handler, not a recognition
problem; a partial paste can be focus/clipboard policy, not a reason to retrain speech.

Deliver supported phrases and adapters, actual loaded service/configuration, failure
status and remaining manual checks. Do not run a demonstration, change a working
service or send a message merely because this skill was read.
