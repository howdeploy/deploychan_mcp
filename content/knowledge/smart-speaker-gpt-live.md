---
id: smart-speaker-gpt-live
name: Connect a smart speaker to GPT-Live — Mini 1 experiment and integration approach
summary: >-
  Use an accessible smart speaker as the microphone and playback endpoint for GPT-Live.
  KISA's Mini 1 experiment explains native echo processing, host WebRTC, explicit
  delegation to a selected Codex agent, transcript filtering and unresolved audio gaps.
type: knowledge
author: kisa
recommended: false
added: 2026-11-10
tags: [smart-speaker, yandex, mini1, gpt-live, chatgpt, codex, realtime, webrtc, opus, voice, delegation, experiment]
source: https://developers.openai.com/api/docs/guides/live
---

# A smart speaker can be an audio endpoint for GPT-Live

An agent can help a user connect a compatible, accessible smart speaker to a
live voice model. The speaker supplies microphones, audio processing and playback;
a host computer handles networking and the agent connection. The model does not
need to run on the speaker. This is a useful option to investigate when a user
wants to talk through an existing device and explicitly pass work to a coding agent.

KISA implemented this approach on one first-generation Yandex Station Mini,
with a Linux host, during November 2026. The source and experiment
notes were reviewed for this guide on **10 November 2026**. Live conversations
were exercised, but audible dropouts remained open in the latest recorded test.
This is an experimental integration report and a reproduction plan, not a
finished installer or proof that every smart speaker supports the same access.
The custom bridge source and private installation artifacts are not bundled here.

## Choose the connection independently of the speaker

The [official GPT-Live guide](https://developers.openai.com/api/docs/guides/live)
describes a voice conversation with a separate delegated backend. WebRTC carries
audio tracks and a control data channel. Client delegation lets an application
connect its own agent or service. Realtime is a related alternative for a voice
agent whose tools and turns stay in that session; see the
[Realtime overview](https://developers.openai.com/api/docs/guides/realtime).

There are two integration choices:

| Path | What the recipient needs | Evidence boundary |
| --- | --- | --- |
| Existing Codex Live session | An installed Codex version exposing the required Live interface, its existing authenticated session, and a loaded selected chat | This is the path implemented in the Mini experiment. Its app-server events and experimental settings must be checked against the recipient's installed version. |
| Application using the public GPT-Live API | A trusted host/server, the recipient's OpenAI project access and credentials, audio transport and a delegated backend | This is a documented route for a new integration, not the API-authenticated path tested on this Mini. Verify current availability and billing before a paid call. |

Codex login and public API project credentials are different integration inputs.
Do not extract a user's login tokens or assume that a ChatGPT subscription supplies
API credit. Keep project keys on the trusted server and use the current official
connection flow. Model selection, availability and charges must come from current
documentation and the recipient's account, not this dated experiment.

## Preserve the working speaker audio path

For Mini 1, the existing processed microphone stream was already available through
firmware-specific Quasar IPC. The custom detector and host bridge consume that
stream while the native audio stack keeps ownership of capture, VQE echo processing,
mute and playback. See `yandex-mini1-reference-stack` for the access and runtime
architecture and `yandex-speaker-access-and-recovery` for its recovery boundaries.

```text
Speaker microphones -> native capture / VQE -> host processed PCM
  -> WebRTC microphone track -> GPT-Live

GPT-Live audio -> WebRTC / Opus receive -> bounded PCM buffer / resampler
  -> one LAN playback stream -> native speaker player

Live control events -> host delegation gate -> selected coding-agent chat
Agent result -> existing return connection -> Live spoken response
```

The reference microphone path is 16 kHz mono S16LE. The host media adapter handles
negotiated audio, decoding and resampling; do not feed arbitrary RTP/Opus bytes to
a PCM player. Preserve the native echo reference during playback. A disconnected
reference ends the call rather than silently falling back to raw microphone input.

For another device, first identify the exact model/firmware, recoverable access,
processed microphone output, playback input and echo-reference path. A Bluetooth
speaker output alone does not establish access to its microphone array. Root access
alone does not establish a usable full-duplex audio path either. Prefer an existing
supported audio interface when available; do not apply a Mini firmware recipe to
an unrelated model. Without these capabilities, report the specific missing path.

## Keep conversation separate from permission to run a task

Ordinary conversation must not silently become a coding-agent prompt. In this
experiment, a completed user utterance must begin with an explicit delegation
phrase, such as "передай агенту", followed by the task in the same utterance.
The local gate supplies that approved task to the selected agent, replaces any
model-invented task text, consumes permission once and rejects duplicate IDs.
New speech clears unused permission. A conversation prompt alone is insufficient.

The reference implementation adds a loopback WebSocket relay for the Live control
channel. It consumes ordinary transcript events instead of forwarding them into
Codex history, and admits only explicitly approved delegations. A denied delegation
gets a control acknowledgement so Live can continue talking. Agent results use
the existing reverse connection. This local transcript filter does not imply
that the upstream provider receives no speech or retains no data.

The relay forwards the existing authenticated control connection without reading
the credential store. It binds to loopback, uses a private per-user URL token,
and admits only the current marked Mini call. The inspected Codex integration uses
an experimental control-channel URL setting; treat it as a version-dependent
implementation detail, not a stable public configuration contract. Do not repoint every native
Live session before accounting for the relay's shared availability dependency.

Starting a call waits for the marked control channel to attach before forwarding
microphone audio. Reading a new setting back is insufficient when a loaded owner
has cached the old URL. One selected chat must have exactly one loaded owner;
changing selection closes the old call. Reopen an old owner only at an authorized
boundary, without interrupting its active agent work automatically.

Exact home, stop and end commands remain in the local control monitor. General
dictation dispatch is blocked during Live to prevent duplicate submissions. Stop
interrupts playback; ending the conversation closes Live while keeping the chosen
terminal chat. Cancelling speech is separate from cancelling an already delegated
agent task. Keep the existing agent's permissions and confirmation behavior.

## What the recorded experiment established

The following are historical observations from **9 November 2026**, not checks
rerun for this publication:

| Evidence | What it establishes | What it leaves open |
| --- | --- | --- |
| Local notes report 45 gateway, bridge and routing checks with a mocked upstream | Simulated transcript filtering, explicit delegation, duplicate suppression and agent result return | Actual provider event ordering and end-to-end delivery in a real conversation |
| Fresh stock Codex app-server configuration probes read the shared relay setting without creating a call | A custom Codex fork was unnecessary for the inspected integration | Attachment by older loaded owners and compatibility with other versions |
| Services returned ready after restart with Live inactive | Startup and ordinary connections recovered | Audible Live quality, cancellation and reconnect during a call |
| User listening test: 2–7 clean words, then robotic speech and dropouts | A real audio session ran and had an audible defect | A stable full conversation or a demonstrated acoustic fix |
| A trace recorded 68 lost packets out of 6,459 expected, decoded PCM gaps up to 428 ms and 102 speech-adjacent buffer starvations | Transport/decoder/playback gaps were observed while one player remained open | The sole root cause or proof that every starvation was audible |

Subsequent code introduced a per-call Opus receiver, packet reordering/recovery
and bounded buffering. The latest notes leave that revision's acoustic result
unconfirmed. PLC/FEC attempts are not proof of recovered speech. Idle-silence
underflows alone cannot identify the cause. Do not describe this as solved jitter,
guaranteed latency or a production-ready hands-free assistant.

Live uses one continuous native player/stream per call, rather than restarting
playback for each phrase. It is a separate mode from `buffered-speech-and-cancellation`,
where ElevenLabs produces a complete WAV before playback. The two modes must not
compete for the speaker; Live does not need ElevenLabs as another synthesis stage.

## Reproduce and evaluate on the recipient's installation

Use this as a proposed test sequence. Run microphone, playback, paid calls and
device/service changes only within the user's requested scope; publishing this
guide did not execute these checks again.

1. Establish the exact device, host, access/recovery path and audio capabilities.
   Select existing Codex Live or a public API application. Identify missing runtime
   adapters instead of pretending the private reference binaries were installed.
2. Establish microphone delivery, native playback and echo-reference continuity
   separately. Record formats and resampling boundaries; preserve mute and volume.
3. Start one explicitly requested call. Confirm actual control attachment, audio
   receipt and the selected agent owner, not merely a successful configuration read.
4. Listen through a full answer, silence and another turn. Exercise interruption,
   stop and end. Compare packet loss, PCM gaps and buffer depth against the audible
   defect; measure speech-to-audible-response latency separately from service startup.
5. Check that ordinary speech, quoted examples and unsolicited model delegations
   create no agent task. Explicitly delegate one bounded task, verify it arrives
   once in the chosen chat, and hear the returned result. Check new speech clears
   unused permission and selection changes cannot deliver to the previous chat.
6. End the call and verify microphone forwarding, LAN playback and temporary
   resources close. Check the agreed reconnect/restart behavior and normal dictation.
   Report implemented, simulated, physically exercised and unresolved parts separately.

Share aggregate counters, architecture and outcomes. Exclude recordings, transcripts,
account/device identifiers, local addresses, personal paths, session IDs, tokens,
keys, configuration dumps and firmware backups. Keep diagnostic logs free of speech
content and authenticated URLs. A code release would need its own review; this
guide publishes the method and the limits of the experiment.
