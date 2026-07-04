---
id: voice-transcription
name: 'Voice transcription (STT): start free with Groq'
summary: >-
  Voice to text for your agent (Telegram voice messages → text). Free to start: Groq Whisper,
  free tier 2000 requests/day. Paid quality upgrade — gpt-4o-mini-transcribe via Nous
  (~$0.19/hour), without a separate OpenAI key. Who needs what and how to turn it on.
type: knowledge
author: kisa
recommended: false
added: 2026-07-04
tags: [voice, stt, transcription, whisper, groq, openai, hermes, agent]
source: https://console.groq.com/docs/speech-to-text
---

# Voice transcription (STT)

The flip side of voice: the agent doesn't talk, the agent LISTENS. You send a voice message in
Telegram — the agent transcribes it to text and works with it. This is STT (speech-to-text). The
`agent-voice` knowledge is about output (TTS); this one is about input.

## Start — Groq Whisper, FREE

There's one obvious entry point: **Groq gives Whisper away for free**. Free tier — **2000
transcription requests per day**. For personal voice and Telegram that's ZERO cost; outgrowing
the limit by hand is nearly impossible.

- `whisper-large-v3-turbo` — fast (228× realtime, an hour of audio in ~15 sec), multilingual.
  Take it by default.
- `whisper-large-v3` — slightly more accurate, slower (217×), files up to 100 MB.
- Billing (if you ever exceed free) — minimum 10 sec per request.

Groq is **compatible with the OpenAI API**: same client, you swap `base_url` to Groq and the key
(`GROQ_API_KEY`) — you don't rewrite the transcription code. The key is free at console.groq.com.

One downside: on mixed technical ru/en speech the quality is **weaker**. Good enough for quick
notes; if you need accuracy — upgrade below.

## Quality upgrade — OpenAI STT (when Groq can't keep up)

You pay ONLY when free Groq isn't good enough on quality. Best price/quality —
**`gpt-4o-mini-transcribe`**: on mixed ru/en technical speech it's the most intelligible of all,
and it costs a laughable amount.

| Model | Price | Per hour | Quality (test on ru/en speech) |
|---|---|---|---|
| **Groq `whisper-large-v3-turbo`** | **free** (2000/day) | **$0** | ok for notes, weaker on mixed |
| Groq `whisper-large-v3` | free / $0.111/hour | $0.111 | weaker |
| **OpenAI `gpt-4o-mini-transcribe`** | $0.003/min | **~$0.19** | best in test |
| OpenAI `gpt-4o-transcribe` | $0.006/min | ~$0.38 | better than Groq, worse than mini |
| OpenAI `whisper-1` | $0.006/min | $0.36 | weak |

Even 100 hours of voice per month on `gpt-4o-mini-transcribe` is ~$18–19. Per hour of audio —
less than 20 cents. For personal volume — fractions of a cent per voice message.

**Via Nous (for Hermes) — no separate OpenAI billing.** The Nous gateway runs OpenAI audio
through your Nous subscription: you don't set up an OpenAI API key, everything on one bill. The
markup is **~+5%** over OpenAI's official prices (measured by KISA; the gateway's official pitch
is "one subscription instead of five" — Nous doesn't publicly publish a separate STT price line).
+5% is ~$0.20 per hour instead of $0.19. Not a drama.

## How to turn it on (by client)

**Hermes** — the provider is switched via config:
```bash
# free start:
hermes config set stt.provider groq          # GROQ_API_KEY in ~/.hermes/.env
# quality upgrade via Nous:
hermes config set stt.provider openai
hermes config set stt.openai.model gpt-4o-mini-transcribe
hermes gateway restart
```

**Claude Code / Codex** — no native STT, you build it yourself (like voice in `agent-voice`):
1. Provider key in `.env` (`GROQ_API_KEY` or `OPENAI_API_KEY`), not in a shared file.
2. Script: audio → transcription endpoint (Groq, OpenAI-compatible, or OpenAI) → text.
3. Hang it on a **hook**: incoming voice message → transcript → into the agent's context
   automatically.

## Takeaway

Start with free Groq turbo — it covers personal voice without spending a dime. Pay for
`gpt-4o-mini-transcribe` (via Nous if you're on Hermes) only when Groq's quality on your speech
genuinely gets in the way. Free first — money for quality, and only when you need it.
