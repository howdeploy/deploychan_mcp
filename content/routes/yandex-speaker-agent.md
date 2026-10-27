---
id: yandex-speaker-agent
name: Turn an owned Yandex speaker into an agent terminal
summary: >-
  A model-aware route from feasibility and recoverable access to local wake detection,
  Russian transcription, host commands and reliable spoken replies. Based on Mini 1
  experience, with explicit limits for other models.
type: route
author: kisa
recommended: false
added: 2026-10-27
tags: [yandex, speaker, mini1, root, voice, agent, leveling-up, recovery]
steps:
  - title: Decide whether this exact device and host can support the goal
    action: read
    ref: yandex-speaker-feasibility
    body: >-
      Identify model, firmware, access and recovery. Separate on-speaker functions
      from host/cloud work. Return ready, conditional or research-required with a
      concrete next step; do not promise that another model's recipe will work.
  - title: Establish access with a bounded bootstrap and a way back
    action: configure
    ref: yandex-speaker-bringup
    body: >-
      Follow the current enthusiast instructions for the selected revision. Preserve
      original network settings, prepare maintenance and backup, restore household
      DNS and distinguish persistent SSH from a replacement assistant daemon.
  - title: Capture and inspect the processed audio path
    action: read
    ref: yandex-mini1-reference-stack
    body: >-
      Read the concrete Mini 1 architecture and compare stock-model replacement,
      a side-by-side detector and full daemon replacement. Our runner subscribes to
      Quasar :9850 vqe_0; it does not free ALSA. Establish matching runtime/model,
      host supervision and rollback requirements before training or deeper edits.
  - title: Train activation and a small command vocabulary
    action: configure
    ref: local-voice-command-training
    body: >-
      Separate the wake span from the command body, preserve pre-roll, collect ready-
      signalled examples and retain negatives/held-out cases. Deploy matching model,
      native router and supervisor instead of requiring an accidental second wake word.
  - title: Route general dictation and host commands
    action: configure
    ref: voice-desktop-control
    body: >-
      Use host ASR, exact command matching and typed application adapters. Keep
      speaker-local actions local; route remaining text to the selected agent or
      focused field without automatically sending a message.
  - title: Give the agent a reliable, interruptible voice
    action: configure
    ref: buffered-agent-voice
    body: >-
      Reuse the chosen provider session, start the first prepared phrase early,
      collect the complete recording, then use native playback. Confirm stop through
      the processed audio path and retire the cancelled queue and late text.
  - title: Measure the complete interaction and record the unknowns
    action: read
    ref: voice-pipeline-latency-and-lessons
    body: >-
      Separate ASR, agent, connection, first PCM, full WAV and audible start. Retain
      failures through a proxy and the limits of user-reported timing. Run paid,
      microphone, playback and reboot checks only within the user's chosen scope.
---

# Speaker-to-agent route

Use this route for an owned speaker. Its access reference is
[Yandex Station Extended](https://hackalice.me/), maintained in
[Marker284/yandex-station-extended](https://github.com/Marker284/yandex-station-extended).
The agent integration and lessons here are KISA's work; do not attribute those custom
handlers to the community firmware project or present this as a replacement ROM.

Start from the relevant step if access or ASR already works. A route supplies the
sequence and the knowledge; it does not install private binaries, reproduce a personal
agent session, authorize a reset or promise compatibility with every speaker.
