---
id: voice-input-and-desktop-routing
name: Route local dictation to applications and typed desktop actions
summary: >-
  Keep wake detection on the speaker, transcribe Russian with host GigaAM, and route exact
  commands or clipboard dictation without an LLM round trip. Covers Linux adapters,
  application control bridges, focus, locked screens and truthful acknowledgements.
type: knowledge
author: kisa
recommended: false
added: 2026-10-27
tags: [gigaam, asr, linux, dictation, clipboard, routing, media, workspaces, mateengine]
source: https://github.com/salute-developers/GigaAM
---

# Put each decision on the layer that needs it

The reference architecture keeps activation on the Mini 1 and runs Russian
[GigaAM](https://github.com/salute-developers/GigaAM) ASR on the Linux PC. This
installation selected v3 e2e-RNN-T; model choice and accelerator placement belong to
the user's hardware assessment, not to a universal installation command.

Load the model once in a service. When appropriate, use synthetic silence to warm
initialization before publishing readiness; do not silently record the microphone for
a warm-up. Bound recording length, silence endpointing, concurrent inference and queue
age. Record inference time separately from wake, endpointing and delivery time.

## Routing order

1. Honor an accepted cancellation and discard its obsolete recording/results.
2. Normalize text conservatively, then match complete supported command forms.
3. Execute a typed host action, or route remaining text to the selected dictation target.

Use full-utterance matches with explicit aliases. Do not execute a shell fragment
extracted by a language model from arbitrary dictation. `Explain volume` and
`write the word quieter` are ordinary text, even though they contain command words.
An acknowledged local action consumes the utterance and does not also enter chat.
Unknown names and failed actions should produce a useful status instead of silent success.

The destination agent also needs an interaction policy: incoming transcripts during
an explicitly announced demonstration are not automatically new assignments to that
agent. Preserve its background task until the user deliberately changes the scope.
Do not compensate for every leaked command by launching the application from chat.

## Useful adapters

| Intent | Adapter and important boundary |
|---|---|
| Workspace by number | Actual compositor IPC; cardinal/ordinal aliases and both word orders |
| Pause/resume/next/previous | MPRIS/player control; confirm the selected player's capabilities |
| Monitor brightness | Existing brightness/DDC helper; stable display identity, bounded percentage |
| Open/close an application | Desktop entry or installed application API; graceful close and profile identity |
| Avatar dance/portrait/placement | Private application IPC with typed actions and acknowledgement |
| Wake display | Session/compositor power control; retain the lock screen |

Browser media pause can work while next-track does not: a media widget cannot invent
the website's missing Media Session handlers. Fix that boundary rather than retrying
the same unsupported action. Similarly, moving an avatar to panel coordinates is not
the same as activating its sitting animation; edge hiding is an application state,
not an arbitrary off-screen position. Convert global/monitor/window coordinates once
in the owning application and make the bridge return the actual accepted action.

In the CanvasTTY integration, application launch resolved the permitted installed
AppImage version. In the MateEngine integration, an application bridge handled dance
selection, portrait mode, surface attachment and edge hiding. A portable command
contract can look like this; it is an illustrative schema, not a claim about a stock
MateEngine API or a bundled executable in this pack:

```json
{"request_id":"demo-1","action":"avatar.place","target":{"surface":"panel","monitor":"left"}}
```

The application validates the action/target, converts coordinates in its own geometry
space and activates the corresponding animation state. Its reply distinguishes
`accepted` from an observed `completed` result. The ASR router consumes that request
once and exposes an error if the bridge lacks the requested capability.

For AppImages, select an installed executable by a parsed release version, not
lexicographic filename order. Preserve the user's chosen release/prerelease policy.
Launch outside a short-lived voice-service process so a bridge restart does not kill
the app. An application request or PID is not proof that its window rendered correctly.

## Dictation into the focused application

Offer an explicit mode switch, such as a user-selected hotkey, between agent delivery
and focused-field dictation. Capture the intended target and recheck focus before
delivery. Use the desktop's permitted clipboard/paste mechanism; do not send a chat
message or press Enter merely because text was dictated. Clipboard insertion avoids
per-character synthetic typing but does not itself bypass desktop permission or focus
restrictions. Report failure/partial insertion honestly and offer a manual paste.

An explicit formatting phrase can insert a paragraph deterministically. Use a clear
phrase such as `new paragraph`, with an escape for mentioning it literally. A long
pause can suggest paragraph structure, but should not erase text or unexpectedly end
the entire utterance. Keep formatting separate from command authorization.

## When the screen is locked

Identify whether the PC is merely blanked, locked, suspended or has lost networking.
A user-session service should remain available while locked, but display wake, media
control and text insertion have different policies. Waking the password screen does
not authorize unlocking it. Do not insert private dictation into an unverified or
protected field. Distinguish an ASR failure, false stop, stale target, transport error
and actual insertion error using one request identifier across the route.

This pack provides the implementation pattern. Personal application paths, private
control sockets and a direct attachment to a particular agent conversation must be
discovered and configured for the receiving user.
