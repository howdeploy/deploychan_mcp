---
id: yandex-mini1-reference-stack
name: KISA's Mini 1 stack — custom wake detection on the native audio path
summary: >-
  How the reference YNDX-0004 actually works: a custom ARMv7 TensorFlow Lite Micro
  runner beside Quasar, processed microphone IPC instead of exclusive ALSA capture,
  host GigaAM and supervision, native playback, isolation and separate rollback layers.
type: knowledge
author: kisa
recommended: false
added: 2026-10-27
tags: [yandex, mini1, reference-stack, microwakeword, tflite, runner, quasar, vqe, alsa, microphone, rollback]
---

# The reference installation, not a replacement firmware

This is the concrete architecture used by KISA, checked against the local source
tree on 27 October 2026. The maintenance record identifies a first-generation
Yandex Station Mini **YNDX-0004**, firmware **1.320.4.20.3512123772.20251028**.
Its kernel is aarch64 but its userspace is 32-bit; the custom executable is a
statically linked **ARMv7 EABI5** binary. Kernel architecture alone is not the
correct target for building it. This guide does not establish compatibility with
another firmware, Mini 2/3 or a different speaker.

The key distinction: we added our own wake/command detector **alongside the native
audio stack**. We did not replace its microphone driver or remove the native
spotter. The stock word "Алиса" remains a fallback trigger. Vendor cloud access
is separately disabled; local capture, processing and playback remain useful.

## Three different approaches

| Approach | What changes | Audio ownership and consequences |
|---|---|---|
| Replace the model inside the stock spotter | Supply a model compatible with that exact vendor engine, frontend and loader | Native audio ownership stays intact. A Kaldi `.nnet` recipe, if verified for that engine, belongs here; an arbitrary `.tflite` file cannot be substituted for it. This project did not train or install a replacement Kaldi model. |
| Our side-by-side detector | Add a custom TFLite Micro executable and streaming model; consume native processed audio and supervise sessions from the PC | Quasar continues to own hardware capture and VQE. Our process subscribes to its local IPC; it does not need to release ALSA. Existing local playback, volume, Bluetooth and mute behavior are retained. |
| Replace the audio/assistant daemon and capture ALSA directly | Select or implement another capture and playback owner | This is a different integration. It must account for exclusive device ownership, microphone array processing, echo cancellation, mute, playback and lifecycle. Stopping a vendor process is not an equivalent shortcut for our stack. |

We chose the second approach to reuse the speaker's working audio processing and
hardware controls, run a small detector on its limited CPU, and keep general
Russian ASR and agent work on a more capable PC. It avoids rebuilding the entire
audio service. The trade-off is dependence on the vendor's firmware-specific IPC
and on a live host supervisor; this is not a PC-independent assistant.

## End-to-end data path

```text
Mini 1 microphones -> native capture/VQE -> vqe_0 PCM, 16 kHz mono S16LE
  |-> local IPC :9850 -> ARM TFLite Micro frontend/model/router -> wake/route events
  `-> separate IPC subscription over ADB -> host RAM pre-roll -> VAD -> GigaAM
       -> exact host commands OR selected agent / focused-field dictation

Host TTS -> complete prepared WAV -> LAN transport/FIFO -> native AudioFilePlayer
Host supervisor <-> ARM loopback control socket, forwarded through ADB
```

The host is Linux with GigaAM v3 e2e-RNN-T on an RTX 4060 in this installation.
That GPU is an observed configuration, not a universal minimum requirement.
The speaker handles wake and a small vocabulary; it does not run GigaAM or an LLM.
Host services are `alice-local-voice.service` and `alice-agent-speech.service`.
The old cloud-transcript bridge must not run concurrently with the local bridge.

Speech uses the host's existing ElevenLabs `eleven_v4` session, explicitly requested
per answer, with provider PCM buffered into a complete validated WAV before native
playback. Keeping synthesis streaming but playback buffered was chosen after audible
cuts through the configured proxy. ASR stays on the PC; agent/TTS provider calls are
a separate cloud dependency. Denying the speaker's WAN does not make those host calls
offline. See `buffered-speech-and-cancellation` for the complete speech lifecycle.

## Microphone access: subscribe rather than free ALSA

On the speaker, connect to TCP **127.0.0.1:9850**. The host uses an ADB forward
from its loopback port **19850** to that same remote port. These are different
subscriptions to the processed stream; wake detection does not hand over the
hardware microphone to the host after a trigger.

For the corresponding firmware, subscribe to the main audio channel by writing
these **nine bytes once** after connecting:

```text
05 00 00 00 fa 09 02 0a 00
```

The first four bytes are the little-endian payload length; the remainder encodes
`QuasarMessage.io_channel_request` field 159, `request_main` field 1, empty message.
Incoming frames also have a four-byte unsigned little-endian length followed by
protobuf payload. Perform complete reads: TCP reads do not preserve message boundaries.
The reference native reader rejects zero lengths and frames above 512 KiB.

The decoder accepts either direct audio field **158**, or the observed envelope
with message kind **253 = 158** and body **252**. Inside the audio body, repeated
field **1** holds channels; channel field **2** is the name, **3** the audio bytes,
**7** the sample rate and **8** the channel count. Select **`vqe_0`**, require
**16000 Hz, one channel**, and interpret its bytes as PCM S16LE. Validate lengths,
reject ambiguous/duplicate selected channels and mixed or incomplete envelopes.
Do not send protobuf bytes directly to ASR as if they were PCM.

`Device or resource busy` from an independent ALSA recorder does not establish a
need to kill Quasar. Our path leaves that device owner running. In particular,
the reference installation retains `platformd` and `mediad` for audio processing
and playback. If :9850 or `vqe_0` is absent, inspect the exact firmware and audio
services; do not assume that this guide's protocol exists on the new target.

The host receiver is connected continuously and retains **three seconds of
pre-roll in RAM**. A wake event arms the phrase buffer including that history;
VAD endpoints the utterance and GigaAM transcribes it. It does not reopen ALSA,
restart the capture service or wait for the detector to release the microphone.
Capture/transport failure blocks delivery of an incomplete phrase.

## Model, training and executable are separate artifacts

Training uses a microWakeWord-derived TensorFlow/Keras pipeline, synthetic Russian
Piper examples, augmentation and real recordings. It exports a **stateful streaming
INT8 `.tflite`** model. This is not a Kaldi `.nnet` model and upstream microWakeWord
does not supply our Mini 1 IPC adapter, command router or PC supervisor.

The current reference has one shared acoustic backbone and six independent outputs,
in this order: `wake`, `quieter`, `louder`, `bluetooth_on`, `bluetooth_off`, `stop`.
An activation opens a bounded session for ordinary local commands. A recognized local
action consumes its request instead of also becoming agent dictation. Stop has a
separate interaction contract; see `local-wake-word-and-command-training` and
`buffered-speech-and-cancellation`.

The native frontend uses 30 ms windows, a 10 ms feature step and 40 filterbank
channels over 125–7500 Hz, with its configured noise reduction, PCAN and log scaling.
The model consumes three feature frames per inference step (30 ms), INT8 input
`[1,3,40]`, and returns UINT8 scores. Preserve streaming state, exact frontend
parameters and quantization with the model; matching the filename or tensor shape
alone does not make another wake model compatible.

Paths below identify files in the reference **`yandex-station` source tree**.
They are an artifact inventory, not download URLs or files supplied by this MCP:

| Artifact | Reference path and purpose |
|---|---|
| Native executable | `voice/wakeword/native-probe-armv7`, static ARMv7 TFLite Micro runner |
| Native source | `voice/wakeword/native_probe.cc`, with `live_audio.h`, `command_route.h` and `local_controls.h` in the same directory |
| Build recipe | `voice/wakeword/build-native.sh`; requires the ARMv7 musl toolchain, vendored TFLite Micro library and microfrontend/KissFFT sources |
| Model and labels | `voice/wakeword/ru_controls_v1.tflite` and `ru_controls_v1.json`; the historical filename currently describes six outputs and supervisor protocol 2 |
| Host supervision | `voice/custom_wake.py`; installs matching artifacts, maintains control/heartbeat and correlates request IDs |
| Audio and native control | `voice/audio_ipc.py`, `voice/quasar_ipc.py`, `voice/bridge.py`, `voice/native_alice.py` |
| Training stages | `voice/wakeword/pilot.py`, `train_controls.py`, `train_composable.py`, `finetune_stop.py`; these are project-specific stages, not interchangeable upstream commands |

The MCP currently distributes the explanation and protocol, **not a downloadable
source/binary/model bundle**. Exact reproduction therefore also requires obtaining
a matched release of these artifacts, or implementing equivalent adapters from the
described contract. Do not tell a user that fetching this guide installed the runner,
that the named files exist on their machine, or that installing upstream microWakeWord
alone reproduces this stack. Personal recordings and credentials are not prerequisites
to distribute with an implementation.

## Live runner lifecycle and host control

The reference host checks SHA256, uploads the executable/model into
`/tmp/mini1-codex-wake/` under digest-based names and starts the equivalent of:

```text
native-probe-armv7 --live ru_controls_v1.tflite
```

This line describes the runner's CLI, not a complete standalone launch recipe.
It subscribes to microphone IPC, opens another **loopback-only dynamic TCP port**,
and prints `MWW_LISTENING:<port>`. The host forwards that port with ADB, connects
within ten seconds and then receives `MWW_READY`. It sends heartbeat/state about
every 100 ms. The runner exits if the supervisor disconnects or heartbeat is absent
for five seconds. The dynamic control port is separate from audio :9850 and native
Quasar control :9875 (forwarded to host :19875).

Important protocol-2 controls and events:

- `H` heartbeat; `B/C` block/allow new wake events, preserving the open-session rules.
- `P/S` playback state, `E/e` own-audio echo guard, `A/a` host processing state.
- `MWW_WAKE <seq> <score>` opens capture; `MWW_ASR <seq>` permits ASR but does not
  by itself permit final delivery. After an isolated name the host sends `R<seq>\n`
  and waits for `MWW_CONTINUE`; before final dictation it sends `F<seq>\n` and waits
  for the decision. `MWW_ROUTE` remains authoritative for the session outcome.
- `X` requests the local stop path after host ASR confirmation. During own playback,
  model-only stop detections remain candidates; a confirmed stop clears the owned
  playback/queued voice work, not unrelated processes or accepted agent tasks.

All controls must match the deployed protocol and model label order. Physical mute
has priority; the reference runner observes GPIO414, clears detector state on mute
changes, and the host clears captured/pre-roll audio. During playback, the host
also validates aligned native `vqe_0`, `raw_sync_mic_main`, `raw_spk_0`, `raw_spk_1`
channels to establish the echo-cancelled stop path. Raw mic capture is not substituted
for native VQE when that check fails.
For this full channel group, the host uses the all-channels subscription
`05 00 00 00 fa 09 02 12 00` instead of the main-only subscription above. Each of
the four selected channels must have aligned 256-sample/512-byte blocks at 16 kHz.

## What was disabled, and what rollback means

No audio task was removed from `launch.json` to make this capture path work.
The removed task was **`updater_switcher`**, an OTA measure independent of wake
detection. The installation also has separate OTA script/key changes; these do not
belong to a microphone-unlock procedure. Never distribute another device's complete
`launch.json`, account data or factory identity as a rollback file.

The host sends native `AliceCapability` **DISCONNECT (11)** and suppresses vendor
dialogs through **STOP_CONVERSATION (3)**, silent **CANCEL_DIALOG_AND_CLEAR_QUEUE (6)**
and, when needed, **STOP_TTS (14)**. These are runtime controls, not deletion of the
spotter. Separately, owned IPv4/IPv6 routing table **210**, priority **10420**, denies
direct WAN traffic while explicit earlier rules preserve the selected LAN. A boot
script restores this policy before networking/Quasar; stopping the PC bridge does
not restore internet access. Adapt LAN exceptions before applying this to a new subnet.
The reference also sets `common.wifiReseter.noInternet.intervalSec=0` in `quasar.cfg`:
otherwise the stock no-internet recovery can reset Wi-Fi and interrupt this deliberately
offline audio link. Preserve this device's original config for a separate rollback.

Rollback has distinct layers:

1. **Custom detector/host bridge:** stop its owning host service and close supervision;
   the ARM helper exits, while vendor audio processes remain. `/tmp` artifacts are
   volatile and the supervisor uploads them again after a reboot. Reverting a detector
   version requires a matched model/metadata/runtime/supervisor set.
2. **Vendor connectivity:** separately reverse the owned isolation policy and its
   boot hook if vendor cloud operation is wanted. Merely stopping the bridge leaves
   WAN denied; the runtime DISCONNECT may also need clearing, for example by a reboot
   after the intended network policy has been restored. Cloud recovery was not
   separately accepted in the reference maintenance record.
3. **OTA/maintenance:** restore only this device's saved originals if that is the
   chosen goal. Stopping the detector does not undo OTA changes, SSH or boot hooks.

## Reproduction order

1. Identify device/firmware, establish recoverable access and preserve originals using
   `yandex-speaker-access-and-recovery`. Pick our side-by-side architecture explicitly.
2. Establish that the native processed audio subscription exists before training a
   new wake word. Preserve the native audio services; direct ALSA capture is another path.
3. Obtain or implement the matched native runner/model/frontend and host supervisor.
   Configure your own speaker address, LAN policy and agent target; do not copy personal
   session IDs, keys or absolute paths. Train your chosen word for that runtime.
4. Connect continuous capture and pre-roll, session decisions, host VAD/GigaAM and
   deterministic routing. Keep local volume/Bluetooth on the speaker when that is the goal.
5. Add native playback, cancellation and mute handling using
   `buffered-speech-and-cancellation`; then add startup/reconnect and documented rollback.

Within the receiving user's permitted checks, distinguish audio-transport readiness,
runner readiness, a recognized wake, complete dictation and audible playback. None
alone proves the whole stack. This guide's source inspection did not run microphone,
playback, reboot or compatibility checks on another device.
