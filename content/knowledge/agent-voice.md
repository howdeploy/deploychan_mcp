---
id: agent-voice
name: Agent voice — make it reply out loud
summary: >-
  How to give your agent voice output. Hermes configures it natively via profiles
  and TTS providers (Groq, ElevenLabs); Claude Code and Codex vibe-code their own
  solution on a hook.
type: knowledge
author: kisa
recommended: false
added: 2026-07-04
tags: [voice, tts, hermes, setup, agent]
source: https://mcp.deploychan.webcam/docs
---

# Agent voice

A living agent isn't just text. Voice makes it human. The implementation depends on the
client: Hermes has voice out of the box; Claude Code / Codex have no native support — you
vibe-code it.

> This is about **output** voice (TTS). The reverse task — transcribing incoming voice into
> text (STT, e.g. Telegram voice messages) — lives in the `voice-transcription` knowledge:
> free to start on Groq.

**What the agent should do:** ask whether the person wants voice, pick a provider (quality
or speed/price), and set it up — natively if it's Hermes, or build a custom solution if it's
Claude Code / Codex.

**Ready-made discipline.** You don't need to reinvent living delivery for ElevenLabs — install
the `elevenlabs-living-voice` skill (`get_skill`): how to write text for TTS (breathing blocks,
pauses, audio tags), the Eleven v2 / v3 fork, and how to tune voice settings based on user
feedback. Plus a preflight script that cleans text before synthesis.

## Hermes — configures it natively

In Hermes, voice runs through profiles and TTS providers. The working combo for a "living"
agent is **ElevenLabs** (quality) or **Groq** (fast and cheap). Plus machine vision (for
example, DeepSeek can "see" images) — the agent doesn't just talk, it also looks. Configuration
lives in the Hermes config; provider keys go in `~/.hermes/.env`.

## Claude Code / Codex — vibe-code their own

There's no native voice. The solution is built by the agent itself:

1. Take a TTS API: ElevenLabs / Groq / OpenAI TTS. The key goes in `.env` (not in a shared file).
2. Write a small script: response text → TTS request → audio → playback
   (`ffplay`/`afplay`/`paplay`).
3. Hang it on a **hook** (for example, the response-completion event in Claude Code) so the
   voiceover fires automatically rather than on command.

This is exactly the case where "Claude Code explains that you need to vibe-code something
custom" — and does it itself, tailored to the person's environment.

## In practice

- **Blocked services.** ElevenLabs and Stripe flag public VPNs. If a provider isn't available
  from your region — spin up your own VPN on a VPS (for example, with the Xrayebator script) and
  route through it.
- **Choosing a provider.** Need the most natural voice possible — ElevenLabs. Need cheap and
  fast in the background — Groq. Ask the person what matters more, and configure to match.

Voice makes the agent alive. The last layer of the route is memory: so it forgets nothing and
grows over time.
