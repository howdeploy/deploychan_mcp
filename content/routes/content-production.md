---
id: content-production
name: Level Up for Content Production
summary: >-
  Turn an agent into a content partner: rent GPU muscle for generation, learn the
  prompting that makes images land, give the output a living voice, assemble video in
  code, and publish to Telegram as a custom-emoji mosaic. A 6-step route — the agent
  picks which media branches the person actually needs and sets them up.
type: route
author: kisa
recommended: true
added: 2026-08-02
tags: [content, generation, imagegen, video, voice, telegram, publishing, leveling-up]
steps:
  - title: Identify the environment first
    action: configure
    ref: tailored-install
    body: Step 0 of every install. Find out the runtime and model before touching anything — how ComfyUI, voice and video get wired in all branch on the client the agent runs in.
  - title: GPU muscle for generation
    action: configure
    ref: comfyui-remote
    body: Rent a GPU instance and stand up ComfyUI on it — install script, model manifest, SSH access, REST/WebSocket API. Local hardware is the usual ceiling on content work; this removes it.
  - title: Prompting that actually lands
    action: read
    ref: comfyui-prompt-craft
    body: Renting the GPU is the easy half. This is scene logic, lighting, LoRA stacking and the dataset clichés to avoid — the difference between a plastic generation and a usable one.
  - title: Give it a living voice
    action: configure
    ref: elevenlabs-living-voice
    body: Voiceover for the content — text written as spoken speech (breathing blocks, audible pauses, audio tags) plus a feedback loop through the API. Optional branch, skip for silent formats.
  - title: Video assembled in code
    action: configure
    ref: remotion
    body: Compose video as React instead of by hand in an editor. Programmatic, repeatable, diffable — the format an agent can actually iterate on. Optional branch.
  - title: Publish it to Telegram
    action: configure
    ref: telegram-custom-emoji-mosaic
    body: Ship the finished image into a channel post as a real custom-emoji mosaic. Requires Premium on the bot owner's account — check that before promising it.
---

# Level Up for Content Production

This is the content branch of the catalog. Where `agent-onboarding` builds a working
partner, this route builds a partner that **makes things** — images, voice, video, and
posts that ship.

The order is a pipeline, not a checklist: capability first, then craft, then the output
formats, then publication. Each step is usable on its own, but the payoff compounds.

**The agent tailors this, it does not recite it.** Ask what the person actually
produces before proposing all six steps. Somebody making channel art needs steps 0, 1, 2
and 5 and should never be walked through Remotion. Somebody making narrated shorts needs
0, 3 and 4 and may not need ComfyUI at all. Proposing every step to everybody is how a
route becomes noise.

## The six steps

1. **Environment** (`tailored-install`). Which runtime, which model. Every later choice
   branches on it. Don't guess — find out.
2. **Remote GPU** (`comfyui-remote`). Generation capability that isn't capped by the
   person's laptop. Instance, stack, models, API access.
3. **Prompt craft** (`comfyui-prompt-craft`). The knowledge that turns that capability
   into output worth posting.
4. **Voice** (`elevenlabs-living-voice`). Narration that sounds alive rather than read
   aloud. Optional.
5. **Video** (`remotion`). Motion graphics as code, iterable by an agent. Optional.
6. **Publishing** (`telegram-custom-emoji-mosaic`). The last mile — a finished image
   posted as a genuine custom-emoji mosaic, not a file attachment.

## Where this route stops

It covers making and shipping the artifact. It does not cover distribution strategy,
posting cadence, or audience growth — those are the person's call, not the agent's.
