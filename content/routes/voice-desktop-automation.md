---
id: voice-desktop-automation
name: Build a voice-controlled Linux desktop around local transcription
summary: >-
  Add exact voice commands, focused-field dictation and application bridges to an
  existing wake/ASR stack. Preserve lock-screen boundaries, cancellation and reliable
  optional speech without adding an LLM round trip to every desktop action.
type: route
author: kisa
recommended: false
added: 2026-10-27
tags: [linux, voice, gigaam, automation, clipboard, workspaces, media, leveling-up]
steps:
  - title: Select the host route and keep activation ownership clear
    action: read
    ref: voice-input-and-desktop-routing
    body: >-
      Identify the active compositor, user session, ASR service and text destination.
      Retain the existing speaker activation if it works; host commands do not need
      a new on-device model for every desktop application.
  - title: Implement a small typed command surface
    action: configure
    ref: voice-desktop-control
    body: >-
      Match complete aliases for numbered workspaces, media and bounded brightness.
      Use native IPC and installed application identities, consume acknowledged
      commands, and return meaningful unsupported/failed outcomes.
  - title: Add application-specific behavior through a bridge
    action: configure
    ref: voice-input-and-desktop-routing
    body: >-
      Use typed commands for an avatar's dance, portrait, surface sitting, edge hiding
      and display selection. Activation of a pose/state belongs to the application;
      a coordinate change or an accepted request alone is insufficient evidence.
  - title: Support dictation and locked-screen operation deliberately
    action: configure
    ref: voice-desktop-control
    body: >-
      Select agent or focused-field mode explicitly. Insert a completed transcript
      through clipboard with focus checks, no implicit Enter, and deterministic
      paragraph phrases. Waking a screen preserves its password/lock boundary.
  - title: Add optional spoken results and measure the actual delay
    action: read
    ref: buffered-agent-voice
    body: >-
      Speak only when requested. Use the selected voice and volume, a bounded queue,
      early provider synthesis, complete-recording playback and confirmed stop.
      Consult voice-pipeline-latency-and-lessons before claiming latency improvements.
---

# Desktop automation route

This route can reuse a speaker, a desktop microphone or another authorized audio
source. The device-local detector and host action parser are separate components.
Start with a few reversible actions; add vocabulary based on actual misses and
confusions rather than trying to anticipate every possible phrase.
