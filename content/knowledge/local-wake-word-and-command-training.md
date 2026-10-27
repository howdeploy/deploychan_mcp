---
id: local-wake-word-and-command-training
name: Train a wake word and short commands as separate decisions
summary: >-
  Build a bounded local command layer with shared acoustic computation, clear wake/body
  boundaries, real voice examples, negative and held-out cases, and a matched model/runtime
  deployment. Avoid teaching an accidental second wake word.
type: knowledge
author: kisa
recommended: false
added: 2026-10-27
tags: [wake-word, kws, microwakeword, training, mini1, tensorflow-lite, commands, stop]
source: https://github.com/kahrendt/microWakeWord
---

# Separate activation from the command body

[microWakeWord](https://github.com/kahrendt/microWakeWord) is a wake-word training
framework, not a general command recognizer. This project used a custom derivative
with shared features and a small multi-output network; that extension is project code,
not a built-in guarantee of the upstream package. For a large vocabulary, evaluate
a purpose-built keyword/command recognizer or host ASR instead of multiplying models.

The reference Mini 1 network has six outputs: activation, quieter, louder, Bluetooth
on, Bluetooth off and stop. Its exported model is about 91 kB, with a tensor arena
around 30 kB. An offline ARM run took roughly 2.6 ms per 30 ms audio step; that is
neither live end-to-end latency nor proof that any requested 20-command vocabulary fits.

## The boundary bug to avoid

Training every action only as `WAKE + command`, while runtime first consumes `WAKE`,
can leave a classifier expecting another wake word. Users then discover that
`WAKE, WAKE louder` works while `WAKE louder` fails. A longer synonym may happen to
work because its timing differs. Do not diagnose that as merely poor pronunciation.

Use an explicit activation/session state machine. Preserve pre-roll and account for
the detected wake span rather than cutting at the time the classifier reports it.
Train/evaluate the actual body window the runtime supplies. Once activated, accept
the command without requiring the name again. An exact successful local command
consumes that request; it must not also become agent dictation.

| Evaluation case | Expected decision |
|---|---|
| Wake and short action in one breath | One activation, one action |
| Wake, pause, action without another name | Action inside the bounded continuation window |
| Action without activation | No ordinary action |
| Repeated wake before the action | No duplicate action |
| Dictation mentioning a command | Dictation, no action |
| Similar words and background speech | No activation/action unless criteria are met |

## Collect examples without timing traps

Create a recording session, confirm that the capture process is actually ready, then
tell the user recording has started. Do not start a short timer and leave the user
reading a long prompt. Disable command execution and text delivery for the capture;
give a clear end signal. Distinguish a silent file from a late start or a transport fault.

Collect short and longer aliases in normal, faster, quieter and distant speech.
Include confusable negatives and ordinary dictation that contains action words.
Keep separate speaker/session recordings for training and validation. Synthetic
speech and augmentation increase variety; they do not replace the user's voice or
make a reused tuning set independent validation.

When enough recordings already exist, inspect the crop, model scores, competing
class, margins, silence gate, state transitions and deployment before asking the
user to repeat the entire dataset. Replay the same saved WAV on host and target ARM
with the actual router. Any fixtures standing in for VAD/ASR must be stated.

## Stop is a separate interaction contract

The accepted design uses a short preceding pause for a stop word, allowing dictation
to contain that word as part of a sentence. Preserve this choice unless the user
explicitly chooses a different trade-off. A tiny on-device classifier detects only
its trained phrases; a host ASR fallback can support additional exact aliases.
Do not claim that an untrained synonym is autonomous on the speaker.

During agent playback, treat acoustic model detections as candidates and confirm
them through the processed echo-cancelled microphone path before accepting stop.
Read `buffered-speech-and-cancellation` for the playback-specific protocol.

## Deploy a compatible set

Version and preserve model, metadata, preprocessing, native router/protocol and host
supervisor together. Keep a matched rollback set. Do not swap one binary and assume
that another version's control bytes or output labels mean the same thing.
Verify only within the user's permitted test boundary; a host score or a successful
copy does not prove live speaker recognition. Record missed actions and false actions
separately rather than reporting a universal accuracy percentage.
