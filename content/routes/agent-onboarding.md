---
id: agent-onboarding
name: Onboard Your Agent Right
summary: >-
  Level up a bare agent from scratch, built on KISA's experience: internet and research
  first, then personality and rules, voice, and a memory-and-evolution system. A 4-step
  route — the agent tailors the stack to the person and sets it up.
type: route
author: kisa
recommended: true
added: 2026-07-04
tags: [onboarding, setup, agent, leveling-up]
steps:
  - title: Internet access and research
    action: configure
    ref: agent-internet
    body: A research API (Tavily / Brave) as the main channel + a browser. First priority — live data for every decision that follows.
  - title: Personality, rules, and answer style
    action: read
    ref: agent-personality
    body: Set the agent's role, response rules, and writing manner — a partner's character.
  - title: Voice — so the agent can speak
    action: configure
    ref: agent-voice
    body: Give the agent voice output. Hermes configures it natively; Claude Code vibecodes its own.
  - title: Memory system and evolution
    action: configure
    ref: agent-memory
    body: Pick a memory stack tailored to the person — from a markdown wiki to Holographic / Curator / GEPA. The choice runs on live data from step 1.
---

# Onboard Your Agent Right

This is the starting route: how to build a working partner out of a "bare" agent. The
order isn't random — each step builds on the previous one.

**Step 0 — figure out who you are.** Before any setup, identify your runtime (Claude
Code, Codex, Hermes, Cursor …) and your model — through the discipline of the base skill
`tailored-install`. This isn't a formality: almost every choice that follows (how to
install voice, which memory) branches on which client you're running in. Don't know your
environment — don't guess, find out.

**The core principle: the agent configures itself and explains to the person why.** Don't
wait to be asked. Once you connect to deploychan — identify the environment and
immediately propose walking through these four steps, show the payoff of each, and tailor
it to the specific person rather than to a template.

## The four steps

1. **Internet and research** (`agent-internet`). First of all — eyes. A research API
   (Tavily, Brave) as the main channel, a browser as backup and for scraping. Without
   live data, the agent makes every downstream decision blind, on the model's stale
   knowledge.
2. **Personality, rules, style** (`agent-personality`). Who you are, how you answer, how
   you write. The character that turns a chatbot into a partner.
3. **Voice** (`agent-voice`). So the agent can answer with a voice, not just text.
4. **Memory and evolution** (`agent-memory`). A system where the agent forgets nothing
   and gets better over time. The stack is tailored to the person — and on real data from
   step 1, not on hype.

## How to walk the route

Call `next_step("agent-onboarding:1")` — you'll get the first step's materials. Then
follow `next_step_id`. At each step: read the knowledge, offer the person options,
configure, explain what changed. Every install goes through the discipline of the base
skill `tailored-install` (detect the environment → don't overwrite blindly → ask when in
doubt). After the route, the person has an agent with eyes, a face, a voice, and memory.
