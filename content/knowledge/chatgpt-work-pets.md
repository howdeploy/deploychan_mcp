---
id: chatgpt-work-pets
name: 'Building a ChatGPT pet: the Work sprite sheet, done right'
summary: >-
  How an agent builds a desktop pet inside ChatGPT Work (5.6): the work-pets skills plus
  imagegen, the exact sprite-atlas format (one transparent PNG, 1536x1872, an 8x9 grid of
  192x208 cells), the animation discipline that keeps the character calm and consistent, and
  the file-handoff mistakes that quietly break the import.
type: knowledge
author: kisa
recommended: false
added: 2026-07-10
tags: [pets, chatgpt, work, sprite-sheet, imagegen, animation]
---

# Building a ChatGPT pet: the Work sprite sheet, done right

A pet is a small animated character that lives in the app. Under the hood it is one thing
and one thing only: a **sprite sheet** — a single image cut into a grid of frames, where
each row is a state (idle, running, waving …) and each column is a frame of that state's
animation. Get the grid right and the pet just works. Get it wrong and the app either
rejects the file or renders a jittery mess. This note is the hard-won recipe, including the
mistakes that cost a full rebuild.

## The skills that build it

Inside ChatGPT Work, four profile skills do the work:

- `work-pets:create-pet` — create a new pet.
- `work-pets:update-pet` — validate and repair an existing pet.
- `work-pets:pets` — activate and download.
- `imagegen` — draw the character and the frames.

`create-pet` and `imagegen` do the making; `update-pet` is the validator you run **before**
you trust a file; `pets` activates and pulls the finished result.

## The one format that matters

The current, correct format is a single transparent PNG:

- **Canvas:** exactly `1536 x 1872` pixels.
- **Grid:** `8 x 9` — 8 columns, 9 rows.
- **Cell:** `192 x 208` pixels each (8 x 192 = 1536, 9 x 208 = 1872 — it has to divide evenly).
- **Rows = states.** The nine rows are: idle, run right, run left, wave, jump, error, wait,
  work, and result-check (verify).
- **Columns = frames.** The eight cells in a row are the animation frames for that one state.

Hard requirements the app's validator enforces on the **final** file:

- PNG in **RGBA** (real alpha channel, not a flattened background).
- **Exactly** `1536 x 1872`.
- An `8 x 9` grid of `192 x 208` cells.
- No larger than **20 MiB**.
- Empty cells **fully transparent** — no stray pixels, no off-white fill.

## Animation discipline — the part everyone gets wrong

The first version failed not on the format but on the *drawing*. The trap is taking each
state too literally and turning it into a different **scene**: a tablet here, a laptop there,
a sitting pose somewhere else. Each cell then looks like a separate illustration, and the
result reads like a flipbook of unrelated pictures — a "flipping filmstrip." Symptoms:

- neighbouring frames don't line up visually;
- the character's scale and position drift from frame to frame;
- some states carry far too much movement;
- the header needs a **calm, stable idle**, not a parade of different poses.

The rule: **one and the same character, one scale, one baseline**, and inside each state
only a **small, sequential** movement. The person in cell 1 is the person in cell 8 — same
size, same feet on the same line, just a step of motion between them. Idle especially should
barely move; it is the resting face of the pet, not a show.

## Where the file handoff breaks

Two failures sank the first attempt, and neither was about art:

1. **Not validating the final bytes.** The atlas was never run through the *same strict
   validator the app requires* before handoff. Validate the finished file, not the plan.
2. **A temporary link.** The file was passed as an expiring signed URL. Those links die, so
   the local agent couldn't download the original. It was then handed an ordinary PNG and
   mistakenly used *that* single image as if it were the finished sprite sheet — no grid, no
   alpha, wrong size.

So: hand over a **stable, ready sprite sheet** (a real file, not an expiring link), and
verify it passes the validator first. And the client side has a duty too — before installing,
it must **reject an unsuitable PNG with a clear error**, checking dimensions, grid, and alpha,
rather than importing a random image blind. When the other pets work and only one is broken,
the fault is the imported file, not the overlay.

For reference, the current server-side pet passes this validator cleanly. That is the bar.
Match it, validate the final bytes, hand off a real atlas — and the pet installs on the first
try.

**One caveat on the format.** The `1536x1872` / 8-frames layout above is the ChatGPT Work
authoring canvas. The `petdex` consumer used by Codex, Claude Code, and Hermes
(`crafter-station/petdex`) is a **transposed** grid — states as rows, **6** frames per state on
a 1100 ms loop — and renders only a subset of rows. If your pet also has to run there, author
to what that runtime actually slices; don't pour work into frames or rows it never shows. See
`pet-sprite-generation` for the full spec and a generation pipeline.
