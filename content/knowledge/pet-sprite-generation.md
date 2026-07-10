---
id: pet-sprite-generation
name: 'Generating a pet sprite sheet: let AI draw, not assemble'
summary: >-
  How to make a custom agent pet by delegating the art to an image model (e.g. ChatGPT
  imagegen) while keeping the sprite-sheet geometry deterministic. The core rule: the model is
  the artist, never the editor or validator. Covers the real petdex atlas spec, the
  one-shot-sheet failure, a strip-per-state pipeline, animation-as-phases, and fixing only
  broken rows.
type: knowledge
author: kisa
recommended: true
added: 2026-07-10
tags: [pets, petdex, sprite-sheet, imagegen, animation, hermes, codex]
source: https://github.com/crafter-station/petdex
---

# Generating a pet sprite sheet: let AI draw, not assemble

Swapping an agent's pet for a custom one sounds like a pure art task — describe a character,
let an image model draw it, ship it. It isn't. A pet is a **sprite sheet**: a grid of frames
cut on exact pixel boundaries, where each row is a state and each column is a frame of that
state's animation. The art is the easy half. The half that breaks is the **geometry** — and
that half must never be left to the image model.

**The one rule, learned the hard way: the model is the artist, not the editor and not the
validator.** Let it draw. Do not let it lay out the final pixel grid, slice frames, judge
transparency, or decide scale. Those stay deterministic.

## The target format (petdex)

The sprite format used by Codex, Claude Code, OpenCode, Gemini CLI, and Hermes comes from
`crafter-station/petdex`. **[Documented]**

- A pet is a `pet.json` plus a `spritesheet.{webp,png}`.
- Grid: **72 frames of 192×208** — the petdex README states **8 rows × 9 cols**.
- **Rows are the states:** `idle, wave, run, failed, review, jump, extra1, extra2`. The runtime
  maps rows to agent-activity hooks.
- **6 frames per state, at a 1100 ms loop.** The desktop floater renders idle at scale 0.7.

**Reality check — don't over-produce. [Documented + Field]** Only ~6 of the columns are used,
and a consumer typically renders a *subset* of the rows (Hermes drives idle, wave, run, failed,
review). If you author a fuller sheet — extra rows, 8 frames instead of 6 — the surplus is
simply never shown. Note also a geometry caveat: some authoring tools (e.g. ChatGPT Work) build
a transposed `1536×1872` canvas with the states as **columns**; a field-built sheet in that
layout passed a Hermes validator, so conventions differ between the petdex-canonical grid and
what a given build consumes. **Confirm the exact grid your target app slices before you draw a
single frame** — this is where the effort gets wasted.

## Why you can't generate the whole sheet in one shot

The first instinct — ask the model for the entire filled grid at once — fails on geometry, not
art. The app slices the canvas into fixed `192×208` cells, but the model doesn't respect pixel
boundaries: the character lands *between* the expected cut lines. The app then shows cropped
pieces of neighbouring frames, and in motion the pet looks like one long sliding filmstrip.

On top of that come the usual generative defects when a model is asked to fill a grid:
- fixed features drift frame to frame (eye colour, facial detail, hair, outfit);
- the character changes scale between cells;
- body parts jump instead of moving sequentially;
- stray light artifacts appear;
- you get a set of *similar illustrations* instead of true phases of one animation.

Conclusion: even when the output *looks* like a grid, the model isn't accurate enough on pixel
boundaries. The grid is not the model's job.

## The pipeline that works

Split the work in two: **the model draws, a deterministic assembler builds.**

1. **Pick a canonical reference.** Use the best existing variant of the character as the single
   visual anchor — the one that best preserves its face, features, and style. Every state is
   generated against it.
2. **Generate one state at a time, as a horizontal strip** of poses — not the whole sheet.
3. **Use a bright, solid chroma-key background.** Remove it after generation.
4. **Let a deterministic assembler do the geometry:** find the individual poses in the strip,
   clean chroma-key remnants, align poses within the row, choose **one scale for the whole
   row**, place each pose into its `192×208` cell, assemble the exact canvas, save PNG **and**
   WebP, and verify transparency and frame borders.
5. **Slice by actual transparent gaps, not equal division.** Poses that spill across equal
   segments break a naive "cut into N equal parts" — extract frames by the real transparent
   gaps between characters instead.

Because the grid coordinates no longer depend on where the generator happened to place the
character, the sliding-filmstrip failure simply can't recur.

## Direct the animation as phases, not pictures

Describe each state as **eight sequential phases of one action**, not eight separate images.
Explicitly forbid reverse motion, direction flips, and pose resets that aren't in the scenario.

- **A falling state** is a single directed action: lose balance → lean further one way → body
  drops forward → knees fold → hands reach the ground → contact → inertia absorbed → low final
  pose, with **no** snapping back. The classic "neural-slop" version leans right, then left,
  then right — rocking in place instead of falling. Physics has causality; enforce it.
- **Idle should barely move.** It's the resting face of the pet. Keep the eyes open for most of
  the cycle and let a blink occupy only a small part of the sequence (e.g. open, open, open,
  lids lowering, closed, reopening, calm, calm). Pin the character's fixed features so they
  don't drift, and forbid bright spots that read as eye artifacts.
- **Watch a state that reads too big.** If a row visually dominates even while staying inside
  its cells, scale the whole row down at assembly time — no regeneration needed.

## Fix only broken rows

After reviewing the animations **in motion** (not just the static sheet), change **only** the
rows that are actually wrong. Regenerating a good row is a net risk: it can shift the face,
proportions, eye colours, poses, or outfit. In practice, the unchanged rows across two revisions
came out **byte-identical** — proof that a targeted fix never touched the already-accepted
animations. Keep the previous good version as a backup before any change.

## Validate the way the app does

Check every frame for: an image present in the cell; no touching of cell borders; no cropped
body parts; no coloured residue in fully-transparent pixels; identical grid geometry; the exact
canvas size; and correct PNG/WebP decoding by the target engine. Run the **same validator and
the same slicing** the target app uses — a sheet that looks right but slices wrong is still
broken. A final sheet that clears the app's own validator with no warnings, and whose active
files checksum-match the project files, is the only "done" that counts.

## The takeaway

Generation and animation are different problems. A grid of individually-pretty frames is not an
animation; between frames you must preserve causality, direction, inertia, scale, anchor point,
and every fixed feature of the character. The reliable division of labour: **the model is the
artist; the grid, the slicing, the transparency, the scale, and the validation stay
deterministic.**
