---
id: model-picks-2026-08
name: "KISA's model picks, August 2026: open weights won this round"
summary: >-
  Dated snapshot of what KISA actually runs: Kimi K3 full-time (first open-weights model at
  the western level — cancelled the $200 Claude Code subscription over it), DeepSeek V4
  Flash for speed and prompt work, Krea2 for local photorealistic images with Russian text.
  Plus how to squeeze working rules out of published system instructions.
type: knowledge
author: kisa
recommended: false
added: 2026-08-03
tags: [models, opinion, kimi, deepseek, krea, open-weights, vast-ai, review]
source: 'Telegram: https://t.me/deployladeploy (posts of 2026-07-28 … 2026-08-03)'
---

# KISA's model picks, August 2026

Opinion pieces age fast — treat this as a **dated snapshot** (2026-08-03), not eternal
truth, and everything below as **personal field impressions**, not measurements. The
through-line of the season: **open weights caught up**, and the trend is against the
corporations. On 2026-08-03 I cancelled the $200/month Claude Code subscription (paid
since April; on this account since December 2025). 100% of my tasks are now covered by
**ChatGPT 5.6 SOL, Kimi K3, and a bit of DeepSeek V4**.

## Kimi K3 — the main workhorse

- The first Chinese open-weights model you can use **full-time, including vibe coding** —
  no daily friction, it's genuinely good. Benchmarks (which I hate) put it above Opus; more
  importantly, the fact of an *open* model at this level fixes a high vibe-coding bar in
  open source for good.
- The catch is hardware. Officially confirmed: 2.8T parameters, MXFP4 — roughly 1–1.5 TB
  of weights before overhead, so no single node of ordinary cards swallows it whole; real
  setups split across GPUs and/or offload. My channel ballpark (an offer snapshot, not a
  verified config): eight RTX PRO 6000 Blackwell (768 GB VRAM) at **$20–70/hour**, lighter
  cards (5090, 6000 ADA) at **$0.40–1.1/hour on vast.ai** — prices move weekly, re-check
  before renting. Any distilled cut still costs you a kidney.
- The utopia worth walking toward: optimization that puts this class of model at
  **$200–400/month on rented iron**. We're not there; the intermediate steps are pleasant.

## Read the system instructions, not just the benchmarks

Kimi didn't publish a classic system card with K3 — they published **open weights and the
system instructions**. That's not less information, it's different information, and it's
directly actionable (the general method is in `system-prompts-and-cards`):

- *Switching models mid-chat degrades work* — so don't.
- *K3 tends to do disputed work at its own discretion* — so my agents carry an explicit
  rule: "agree everything with me first."
- The same trick applies to every model that ships instructions or a spec: extract the
  optimal task-framing, the documented hallucination behavior, the persuasion boundaries —
  and load the conclusions into your agent's rules, not into your memory.

## DeepSeek V4 Flash (update) — the speedster

- My impressions: above the current Pro on the benchmarks I saw quoted, cheaper and faster.
  In Hermes CLI the output is so fast the terminal flickers; it holds context and hops
  between folders cleanly. On xhigh thinking it reportedly out-codes the Pro (chat-room
  reports, not my measurement).
- Trusting by nature — trivially writes lore and fake documents at light speed. That's
  exactly why it's my pick for **prompt research** (the choirboy-prompt line of work), and
  it means you verify its factual claims twice in normal work.
- Vibe-coding: okay-ish in my runs. Scripts and hooks can be entrusted to it;
  architecture — not yet.
- Open weights, same story as K3: not for home machines, rent the iron.

## Krea2 — local photorealism, finally with Russian text

- What I see in my own generations: skin pores, white hairs, light blemishes; camera
  simulation in the spirit of the better closed models; handles 3D and 2D styles.
  Essentially Anima arriving through another door. Officially the repo confirms open
  RAW/Turbo weights — the quality judgements here are mine, not theirs.
- Closed in May, full weights out June 23 — and the community predictably turned it into an
  adult-content combine. I officially condemn all that filth, of course. The honest point:
  **uncensored models are simply better to work with** — no corporate hoops, no "unethical"
  refusals, no copyright panic. Adults will sort out personal use themselves.
- Killer detail for us: in my tests it writes **legible Russian text** into images —
  something neither Nano Banana nor GPT Image 2 managed properly when I tried.

## What this means for picking a stack

- If you're paying for one subscription out of habit, re-check: the "open weights need a
  datacenter" excuse is now a pricing question, not a capability question.
- Split work by temperament, not by brand loyalty: a fast trusting model for drafts and
  prompt research, a heavy open model for the main line, a local image model when you don't
  want a corporation watching your prompts.
- For actually running any of this on rented GPUs — the `comfyui-remote` skill covers the
  agent-driven GPU workflow end to end.
