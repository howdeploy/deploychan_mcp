---
id: local-voice-command-training
name: Train and integrate local wake words and short commands
description: >-
  Train or repair a small device-local wake/command detector with shared acoustic
  computation, real examples, independent evaluation and correct activation/body
  routing. Use for finite command vocabularies, not general speech transcription.
summary: >-
  Diagnose the wake/body boundary before retraining, record ready-signalled examples,
  keep negative and held-out speech, and deploy the model with its matching router
  and supervisor while preserving local actions and ordinary dictation.
type: skill
author: kisa
recommended: false
added: 2026-10-27
tags: [wake-word, kws, training, microwakeword, mini1, commands, stop]
source: https://github.com/kahrendt/microWakeWord
reminder: One activation must open the command body; do not train a second required wake word into every action.
---

# Local wake and command work

Use the user's chosen word, device and interaction contract. For the rationale and
case matrix retrieve `local-wake-word-and-command-training` from Deploychan MCP;
upstream [microWakeWord](https://github.com/kahrendt/microWakeWord) covers wake-model
training, while any multi-command head/router extension must be implemented separately.

For KISA's actual Mini 1 stack also retrieve `yandex-mini1-reference-stack` before
choosing the runtime or capture method. It specifies the side-by-side ARM TFLite
Micro runner, Quasar :9850 `vqe_0` subscription, supervisor lifecycle and artifact
inventory. Do not assume a downloadable runner is included, propose a Kaldi `.nnet`
as a compatible substitute, or remove native audio services to free ALSA for this path.

## Diagnose before requesting another recording

Read frontend shape/rate, label order, actual model path, native runtime, supervisor
and crop/endpoint logic. Determine whether inference is on the speaker or host.
Trace one failed phrase from audio through candidate scores to execution/dictation.
Check wake consumption, pre-roll, body-window boundaries, confidence/margin, pause
gate and a stale deployment before attributing every miss to the training samples.

Use a shared frontend/network when it suits a small vocabulary. Do not present that
custom adaptation as generic ASR or promise capacity for an arbitrary number of commands.
Desktop actions can use host ASR and a deterministic parser without expanding this model.

## Collect and evaluate

1. Establish capture readiness; then tell the user to speak. Preserve a session ID,
   label, intended phrase, source recording and train/validation assignment.
2. During collection disable effects and outgoing agent dictation. Collect normal,
   fast, quiet and distant variants, short/long aliases, confusable negatives and
   ordinary sentences mentioning the action words. Keep recordings private.
3. Retain independent recordings outside training. Record when tuning against a
   validation set turns it into a regression set; do not claim independent accuracy.
4. Evaluate both one-breath and wake/pause/body forms, repeated wake, bare commands,
   command mentions and silence. Compare the same WAV on host and target runtime.
   State any simulated VAD/ASR events. Respect the user's limits on test execution.

## Integrate the accepted interaction

One wake opens a bounded continuation session. Accept a body without another name,
consume a successful local command and send only ordinary dictation onward. Keep
volume/Bluetooth execution and short cues on the device when local autonomy is the
goal; do not silently substitute a chat agent issuing ADB commands.

Stop words have a separate pause/false-positive trade-off. Preserve the selected
policy. During own playback, acoustic detections are candidates until the processed
audio/ASR confirmation accepts stop; see `buffered-speech-and-cancellation` for the
state/queue requirements. Preserve physical mute priority and current volume.

Version and deploy the model, labels, frontend, native protocol and host handling as
a compatible set with rollback. Report the actually loaded version, misses/false
actions and authorized verification; a successful build or copy alone is not completion.
