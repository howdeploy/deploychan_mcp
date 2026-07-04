---
id: comfyui-prompt-craft
name: 'Prompt craft for ComfyUI generation'
summary: >-
  How to write prompts for generative models (Flux and Anima-like) in ComfyUI: two
  formats (Danbooru tags vs literary text), composition principles, anti-patterns and
  their fixes, samplers per LoRA, animation prompts. A practice-tested approach.
type: skill
author: kisa
recommended: false
added: 2026-07-04
tags: [comfyui, prompting, flux, lora, generation, animation]
source: https://mcp.deploychan.webcam/docs
description: >-
  Use when writing prompts for ComfyUI image or video models: choosing tags vs literary
  format, fixing composition and anatomy artifacts, picking samplers per LoRA, and writing
  short movement prompts for video. Neutral examples only.
---

# Prompt craft for ComfyUI generation

A prompting approach, practice-tested on Flux and Anima-like models. The examples below
are neutral; the technique applies to any content.

## Two prompt formats

| Format | When | Example |
|---|---|---|
| **Danbooru tags** | simple scenes, portraits, standard poses | `1girl, blonde hair, sitting, park` |
| **Literary text** | complex poses, unusual angles, many planes | `A girl sits on the edge of a bench, adjusting her hair, seen from above` |

**Key insight:** the literary format instantly solves composition that tags can't
handle — the model understands spatial relationships better in free text. **Flux** is
especially fond of literary descriptions along the lines of "a girl stands among bushes
in the middle of the street", NOT a comma-separated list of words. Caveat: some LoRA are
trained only on tags — test your own stack.

## Quality prefix

```text
masterpiece, best quality, newest, highres
```
Avoid `score_5`, `score_6`, `year 2025` — these are artifacts of other people's LoRA.

## Principles (critical)

1. **Composition goes in the first 3–4 tags.** Angle and pose BEFORE appearance:
   `profile, from side, sitting on chair` → then hair, clothes.
2. **One tag per concept.** Not five synonyms for an angle — just one (`from below`).
3. **Negatives DON'T work.** The model doesn't understand `no door`. Describe what SHOULD
   be in frame, not what shouldn't.
4. **Remove the conflict, don't compensate.** A tag conflicts → delete it. "Fixing" tags
   bloat the prompt and spawn new conflicts.
5. **Overloaded → rewrite from scratch.** Don't patch a bloated prompt — reset to 15–20 key tags.
6. **Literary drifts into photorealism → fall back to tags.** If 2+ attempts produce photos
   or break anatomy — return to Danbooru tags (they're more reliable for simple/medium scenes).
7. **Numbers in tags break the counter.** `double bun` → `hair bun, two buns`. Don't mix `solo` and `1girl`.

## Anti-patterns and fixes (neutral)

| Problem | Cause | Fix |
|---|---|---|
| Two characters instead of one | `double bun` (the word "double") or `solo`+`1girl` | `hair bun, two buns`; remove `solo` |
| Character with back to the window | `front lighting` + `sunlight from window` conflict | remove `front lighting` |
| Full body instead of close-up | `sneakers`, `asphalt`, `full body` pull the frame out | remove shoes/ground, keep `close-up` |
| Red instead of orange | `red hair` | `dyed hair, orange hair` |
| Character on the couch instead of the floor | `sitting on floor, leaning against couch` | `sitting on armrest`; remove `couch` |
| Twintails → huge bows | `twintails` triggers decorative ribbons | `low twintails, small hair tie, elastic hair tie` |
| Crouching instead of standing | `standing` without qualification | `standing straight, upright` |
| Photorealism from literary | photo terms: `shot, camera, cinematic, overhead` | describe the scene: `seen from above, looking down at` |
| Name collision in a batch | identical `filename_prefix` within a second | unique prefix per job: `batch_{i}` |

## Samplers per LoRA

Each LoRA has its own optimal sampler / scheduler / CFG — this is part of the setup, not a detail:

| Sampler | Scheduler | CFG | Note |
|---|---|---|---|
| `er_sde` | `simple` | 4.5 | base set of style LoRA |
| `sa_solver_pece` | `simple` | 4 | Flat Color / Blending stack |
| `euler_ancestral` | `beta` | 3.5–4 | detail LoRA |
| `euler` | `normal` | 1 | Turbo-LoRA (8–12 steps) |

Get exact sampler names via the API (`GET /api/object_info/KSampler`), don't guess:
`euler_a` does NOT exist → the correct one is `euler_ancestral`; `dpm++ 2M` → `dpmpp_2m`.

## Check the workflow BEFORE the prompt

Workflows get updated — the LoRA chain and node numbers change. At the start of a session:

1. Load the current **API workflow** (JSON).
2. **Parse the LoRA chain** — from the base model (`UNETLoader`) through all the `LoraLoader`s:
   node → file → weight → purpose.
3. **Find the master-route** — `ImpactBoolean`/`ImpactSwitch`, check the status (base or LoRA chain).
4. **Reconcile expectations with reality** — what the user thinks is active vs what's actually in the topology.
5. The `SaveImage` node **changes ID between versions** — always check before setting `filename_prefix`.

## Animation prompts (video)

Short movement descriptions for video models:

- **ULTRA-SHORT.** 2–4 sentences. Only movement facts, no retelling of the scene — the video model
  already has the source image.
- **Subject + verb.** "She breathes. The hand rises. The ice rings." — bare kinetic phrases.
- **Explicit causality.** "The hand tucks a strand behind the ear, then lowers. The strand slips out."
- **No shimmer.** `shimmers`, `flickers` → a flash at frame boundaries.

Negative for video:
```text
frame flicker, flash, brightness pulse, extra fingers, fused fingers, morphing hands, hair duplication, inconsistent lighting
```

Example (neutral):
```text
She breathes slowly, swaying slightly — the ice in the glass clinks. She blinks. Her hand rises,
tucks a strand behind her ear, lowers. The strand slips out and falls onto her cheek. Her hand reaches
up to fix it again.
```

## 18+

The models and technique support 18+ content. Apply it only to consenting adults, not to
real people without their consent. Comply with local laws and platform rules.
