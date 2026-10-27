---
id: buffered-agent-voice
name: Speak through a buffered, interruptible agent voice service
description: >-
  Deliver explicitly requested agent speech, or maintain its TTS/playback lifecycle:
  warm provider connection, early phrase flush, complete-recording playback and
  confirmed cancellation. Use with an identified service and audio device.
summary: >-
  Keep low-latency text submission separate from reliable audio delivery. Preserve the
  chosen voice, proxy and volume; prevent intermediate segment completion, speaker
  echo or late queued text from truncating or replaying an answer.
type: skill
author: kisa
recommended: false
added: 2026-10-27
tags: [tts, elevenlabs, voice, proxy, buffering, cancellation, speaker, latency]
source: https://elevenlabs.io/docs/eleven-api/guides/how-to/websockets/realtime-tdd
reminder: Speak only when requested; first PCM is not audible start, and a model stop candidate is not a confirmed cancellation.
---

# Buffered agent speech

Identify the user's actual voice service, output device, selected voice/model, proxy,
current volume, cancellation path and conversation binding. This skill contains no
personal profile, API key, device address or ready-made session attachment. For the
implementation details retrieve `buffered-speech-and-cancellation` through Deploychan
MCP, and `voice-pipeline-latency-and-lessons` for measurement/negative evidence.

## Deliver an explicitly requested answer

- Reuse the existing private service interface and warm connection. Do not create
  a new script/session or restart a daemon just to speak one reply.
- Prepare a direct, natural first sentence and a short complete answer. Avoid
  Markdown, paths, URLs and tool logs in speech. A short conversation may be a few
  sentences; a work summary states the result and a useful next step. Do not pad
  the first sentence with filler to reach a provider text threshold.
- Use one bounded request or single-use permission for the identified conversation,
  then submit the final speech text promptly. Do not mix two submission methods for
  the same answer or enable automatic narration for subsequent unrelated tasks.
- Preserve current speaker volume and mute. Do not change computer volume or the
  chosen voice/model/proxy unless that is part of the user's task.
- Treat queue acceptance as acceptance only. State verified playback/listening
  evidence when available; do not retry an ambiguous paid request automatically.

## Maintain the transport without regressing reliability

Keep input text incremental. Force generation after the first prepared phrase,
continue text on the same provider socket and flush the remainder only if nonempty.
For a ready text request use one input segment/flush. Handle intermediate audio-final
boundaries without discarding later text or returning the connection to another job
early. Keep frame alignment, length limits, timeouts and cleanup through cancellation.

Prepare and validate the full private WAV before starting the native device player.
This deliberately avoids the proxy-sensitive live playback that failed in the case
study. Do not remove buffering merely to improve the first-PCM number. Check the
actual [TTD protocol](https://elevenlabs.io/docs/api-reference/text-to-dialogue/ttd-websocket)
instead of copying fields from a different TTS WebSocket API.

Keep a single lifecycle owner for current/queued speech. An accepted stop retires
the job and obsolete queue; late text cannot revive it or steal the next permission.
At awaited handoffs, recheck cancellation before playback. During own audio, confirm
acoustic stop candidates through the verified processed microphone path. Do not
silently fall back to raw microphone or disable all human interruption.

Tie LEDs to actual capture/playback, release them at their end, and preserve the
physical microphone mute indication. Preserve the pause policy selected by the user
and separate a new confirmed stop from stale state or transport failure.

## Handoff

Report changed layers, actual service activation, measured boundaries and what the
listener still needs to check. Paid calls, microphone recording, playback, hardware
reboots and model/voice comparison follow the user's authorization; maintaining the
code does not imply permission for a surprise audible or paid test.
