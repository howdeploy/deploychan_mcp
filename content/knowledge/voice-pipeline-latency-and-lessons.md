---
id: voice-pipeline-latency-and-lessons
name: Measure voice latency and preserve the failed experiments
summary: >-
  Separate recognition, agent preparation, proxy connection, synthesis, WAV completion
  and physical playback. Interpret warm-session measurements correctly and retain the
  negative evidence behind buffering, native playback and echo-safe stop handling.
type: knowledge
author: kisa
recommended: false
added: 2026-10-27
tags: [voice, latency, benchmarking, elevenlabs, proxy, gigaam, tts, measurements]
source: https://elevenlabs.io/docs/api-reference/text-to-dialogue/ttd-websocket
---

# Measure the boundary the user actually experiences

Use monotonic timestamps and one request identifier from activation through accepted
input, text generation, synthesis and playback. A worker's first-text timestamp omits
the user's recording, ASR, agent reasoning and tool calls. First received PCM is not
the moment the physical speaker starts talking, especially with complete-WAV playback.

| Stage | Record separately |
|---|---|
| Input | Wake, speech start/end, endpoint/VAD, ASR warm-up and inference |
| Routing | Matched action or text destination, delivery acknowledgement |
| Agent | Request received, first final text, final text completed, any tools |
| Provider | Queue/lock wait, proxy/TLS/WebSocket setup, first text, first flush, input end |
| Audio | First PCM, final segment boundaries, all audio complete, converted WAV ready |
| Speaker | Receiver ready, native playback start/end, accepted stop and cleanup |

## Dated observations, not performance promises

October 2026 observations from one Mini 1/Linux installation:

- A separate three-request TTD benchmark used the chosen v4 voice, PCM 24 kHz and a
  fixed proxy. Cold connection setup was about **2.23 s**. First PCM followed flush
  in roughly **1.27–1.33 s**. Full synthesis took **3.32–4.59 s** for recordings
  about **7.4–7.6 s** long. There were no retries in those three requests.
- Warm connection reuse removed the measured setup cost; it did not demonstrate
  faster inference. Local `send()` duration did not measure server receipt time.
- A longer subsequent answer had first provider PCM at **1.58 s**, a complete WAV
  at **8.40 s**, and native playback at **8.69 s**, relative to the service's first
  accepted text. That run demonstrates that generation overlapped the open text
  input. It does not identify a steady-state median or the time from user speech.
- A later demonstration was perceived by the user as starting in **2–3 s**. That
  specific observation was not independently reconciled against its runtime timing
  log. Preserve it as user feedback, not a guaranteed or fully measured latency.
- Individual warm host ASR examples took about **0.31–0.36 s** for inference.
  Endpointing and delivery are additional stages; those numbers do not describe
  complete speech-to-action latency or a benchmark on arbitrary GPUs.

Three requests or one good demo cannot establish p95, startup reliability, model
ranking or a sustained throughput target. A cold handshake combines several steps;
its 2.23 s does not by itself measure RTT or prove that a geographic endpoint is faster.

## Why the selected playback design changed

Live provider audio through the proxy produced user-observed cuts, missing beginnings
and silence. The responsible provider/proxy/network/player contribution was not
isolated. The chosen mitigation was full recording preparation before audible output.
Keep that negative experience in a guide; do not recommend returning to immediate
network-fragment playback as an already verified improvement.

Native playback succeeded where an earlier direct ALSA path only clicked. A synthetic
echo experiment reported strong attenuation, yet its cold additional Speex stage
allowed own speech to trigger stop at startup. Native VQE plus candidate/confirmed-stop
separation fixed the demonstrated interruption/self-cancellation cases. None of these
results proves every future phrase or every speaker model is covered.

The acoustic classifier alone must not directly stop its own TTS. Conversely, simply
disabling all stop detection during playback removes the user's ability to interrupt.
Keep confirmation and queue cancellation, not either of those shortcuts.

## Next optimization choices

First remove accidental serialization: load ASR once, reuse a provider connection,
send prepared phrases promptly and force the first short buffer when appropriate.
In an earlier trace, first text preceded final flush by **866 ms**. That gap suggested
avoidable waiting; it did not prove the server was idle or guarantee the same reduction
in completed-WAV playback time. Early flush can alter prosody at the join.

Compare a different model, shorter spoken responses, network routing or an explicit
playback buffer only after selecting that change with the user. The official TTD guide
includes a one-voice v4 Turbo example; it was not substituted for the accepted voice/model
in this project. Treat published inference figures as different from measured end-to-end
latency. Do not launch paid benchmarks, reconnect routes or change the voice simply
because the user asked for an explanation.

Save both failures and successes with the same measurement boundaries. Keep source
recordings private, retain regression cases, and state the difference between an
offline check, a protocol simulation and a human listening test.
