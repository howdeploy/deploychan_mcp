---
id: buffered-speech-and-cancellation
name: Reliable agent speech with early synthesis and confirmed cancellation
summary: >-
  Stream text into a warm ElevenLabs session, flush the first prepared phrase, collect a
  complete WAV before native playback, and prevent speaker echo from cancelling its own
  answer. Keep queue, stop, LEDs and physical mute tied to the correct lifecycle.
type: knowledge
author: kisa
recommended: false
added: 2026-10-27
tags: [elevenlabs, tts, websocket, pcm, proxy, cancellation, vqe, echo, mini1, latency]
source: https://elevenlabs.io/docs/eleven-api/guides/how-to/websockets/realtime-tdd
---

# Overlap text and synthesis; finish the recording before playback

This is the selected design after audible cuts and missing beginnings in live audio
playback through a fixed proxy. The exact responsible network hop was not established.
The resulting architecture intentionally separates **streaming text/generation** from
**streaming audible playback**. It keeps the former and buffers the latter.

```text
explicit speech request -> incremental final-answer text -> phrase preparation
  -> one warm TTD WebSocket -> provider PCM -> conversion/limiter
  -> complete private WAV -> one-use LAN delivery -> native speaker FilePlayer
```

Only the user's requested spoken answer reaches this pipeline. Commentary, reasoning,
tool output, old history and unrelated conversations do not. Use a bounded, expiring,
single-use speech request rather than automatically narrating every finished task.

## One provider session and an early first phrase

The [TTD WebSocket guide](https://elevenlabs.io/docs/eleven-api/guides/how-to/websockets/realtime-tdd)
documents a text buffer of roughly 40 characters and 8 words and a `flush` control
that forces generation without closing the connection. A first phrase below the
threshold can otherwise wait while the agent writes the remainder.

In the reference implementation, send the first prepared phrase and immediately
flush it. Continue sending later text on the same connection; flush the remainder
once when input ends, only if more text was sent. Fully supplied text is one part
and needs one flush. Do not flush every token or repeatedly flush an empty buffer.

The receiver must handle intermediate `is_final_audio_for_turn` boundaries. Completion
of the first audio segment cannot finish the whole answer while text is still open.
Track sent segment boundaries, received completions and text-source completion;
retain PCM alignment, report missing/invalid audio and wait for the remaining segment.
An interrupted or uncertain paid request is never silently replayed. Verify the actual
provider's boundary behavior before claiming general compatibility.

Use one serialized session and its existing private request socket, not a new provider
connection for each phrase. In this implementation a heartbeat is sent every 8 seconds;
the guide documents a 20-second idle receive timeout. Warmth avoids connection setup,
not synthesis itself. A fixed proxy is explicitly configured; transport failure does
not silently fall back to a different/direct route. Keep keys and proxy credentials
in private host storage and out of logs, skills and public sample configs.

## Bound and validate the complete recording

The selected provider output is PCM 24 kHz mono, converted to 48 kHz stereo S16LE for
the Mini 1 native path. Choose the actual device format; do not copy this to another
model blindly. Use a limiter and a validated gain instead of raising mixer volume.

Collect into a private temporary WAV with a bounded duration. Before handoff, finish
and validate headers, format, nonempty data, frame alignment and the declared frame
count. Provider failure or cancellation leaves no partially playable answer. Deliver
only to the intended LAN receiver through an unguessable one-use endpoint and clean
up the owned player, FIFO, network tasks and temporary files on every outcome.

The reference Mini needed its native FilePlayer: a direct ALSA experiment showed PCM
activity but produced only a click/cut to the listener. Activity counters are not an
audible acceptance test. Preserve current speaker volume, hardware mute and the user's
chosen ceiling. A redundant host volume round trip before synthesis was removed;
the device-side playback check/guard remains. Rejection there can occur after synthesis
has already been paid for. This is the selected trade-off, not a universal policy.

## Make stop transactional

Give a speech controller ownership of the queued job until playback completes, not
merely until text ends. On an accepted stop, advance a cancellation epoch and discard
the interrupted job and its older queued work. Retire its message ID so late text
cannot consume a new permission. Recheck cancellation after awaited handoffs and
before starting the native player. Stop/clean up owned resources without cancelling
unrelated audio or a later, explicitly requested answer.

During the speaker's own audio, the tiny acoustic model reports a **candidate** only.
Confirm the stop from the processed microphone/VQE path before executing it. Own TTS
can contain `stop` or sound like it. A candidate is not an accepted stop, a cue or
permission to clear the queue. Preserve the agreed preceding-pause policy and exact
ASR stop aliases; a normal dictation sentence may contain those same words.

For the inspected Mini 1 transport, consume the complete expected reference/microphone
channel group with consistent format. Native timestamps were zero placeholders and
could not establish alignment. Do not silently substitute raw microphone when the
processed/reference path fails. An extra cold Speex stage failed at playback startup
in this project and was removed; synthetic echo attenuation had not predicted that
behavior. That observation is not a claim that every other AEC is unsuitable.

## Signals and acceptance

LEDs follow actual recording and actual playback events. Text preparation, inference,
agent work and queue cleanup do not keep the ring lit. Physical microphone mute keeps
its priority red indication. A successful accepted stop may issue a short native cue
at the current volume; at zero it is necessarily silent. Acceptance status and cue
playback failure must remain distinguishable.

Keep a verified cancellation path ready before speech begins. Separate playback
failure from a matching newly confirmed stop for that same speaker; stale stop state
must not mask a transport error. With authorized tests, check own-voice phrases that
contain stop words, real human interruption, no late queue replay and ordinary
dictation immediately afterwards. User listening evidence and transport logs answer
different questions. See `voice-pipeline-latency-and-lessons` for measured boundaries.
