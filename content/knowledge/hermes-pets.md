---
id: hermes-pets
name: 'Pets in Hermes: install, hatch, and the profile trap'
summary: >-
  Running petdex mascots in the Hermes agent: update to get the bundled petdex skill, install
  and select a pet, generate your own with /hatch, fix the tiny default scale, and the gotcha
  that the default profile lives in ~/.hermes while named profiles live under
  ~/.hermes/profiles/<name>/.
type: knowledge
author: kisa
recommended: false
added: 2026-07-10
tags: [pets, hermes, petdex, hatch, cli]
source: https://hermes-agent.nousresearch.com/docs/user-guide/skills/bundled/productivity/productivity-petdex
---

# Pets in Hermes: install, hatch, and the profile trap

Hermes can render an animated mascot — a "pet" — in the terminal and desktop. It runs on the
**petdex** skill. This note is the practical path: get the feature, install a pet, generate
your own, size it correctly, and avoid the one trap that bites when you run multiple profiles.

## First: update — the feature is newer than your install

If `hermes pets` doesn't exist, your Hermes is simply too old — Pets shipped later. Update:

```bash
hermes update
```

In the field this moved v0.16.0 -> v0.18.2 and pulled in, together: the `hermes pets` engine,
the `pillow` library (it decodes the sprites), and the **bundled `petdex` skill** plus a couple
of other bundled skills. Key point: **petdex is a bundled skill — it arrives with the update.
You do not install it separately.** After updating:

```bash
hermes pets list          # browse the gallery (3421 pets in the field)
hermes pets doctor        # checks pets dir + terminal graphics; installed: 0 at first
```

## Two surfaces: slash commands vs the CLI

**In a running session / desktop — use slash commands.** This is the everyday surface when
Hermes is open; you don't type `hermes pets` inside a session:

- `/pet` — toggle the pet pane
- `/pet list` — show installed pets
- `/pet <slug>` — adopt a specific pet
- `/pet scale <n>` — resize
- `/hatch <description>` (alias `/generate-pet`) — generate a new pet

**In the terminal — the `hermes pets` CLI** is the full management surface: `list`,
`install`, `select`, `show`, `off`, `scale`, `remove`, `doctor`, plus `hermes config set
display.pet.*`. (Note: `install`, `doctor`, `remove`, and `show` are documented as `hermes
pets ...` CLI commands; the documented slash set is `/pet [list|<slug>]`, `/pet scale`, and
`/hatch`.)

## Install a pet

```bash
hermes pets install boba --select
```

`--select` makes the pet active immediately — it writes `display.pet.enabled: true` and
`display.pet.slug: boba` to `config.yaml`. Without `--select` the pet just downloads into the
profile's `pets/` directory but stays inactive. Verify with `hermes pets doctor` -> `✓ ready`.

## Generate your own with /hatch

`/hatch <description>` from inside a session builds a brand-new pet. In the field it runs as a
two-step flow (this two-step shape is field-tested, not spelled out in the public docs):

1. **Base drafts** — several cheap, prompt-only variants are generated; you pick one.
2. **Hatch** — the chosen draft becomes a *reference image*, and one frame per state (idle,
   thinking, run, wave, failed, jump) is generated from it, then sliced into an `8 x 9` sprite
   sheet.

This needs an image provider with **reference-image** support. Nous Portal and OpenRouter are
the documented backends; OpenAI-compatible endpoints work via a custom provider. The result is
saved as a valid petdex atlas and shows up in `hermes pets list --installed`.

## Fix the size (scale)

The default `display.pet.scale` is **0.33**, so the native `192 x 208` frames render tiny.
Bump it:

```bash
hermes config set display.pet.scale 1.0     # range 0.1 - 3.0
```

or `/pet scale 1.0` inside a session. In the field the change applied **immediately** — the
agent set it and the new size showed at once, no restart needed. (If a given setup doesn't pick
it up live, restart Hermes / the desktop.)

## The profile trap

Hermes profiles have an asymmetric layout, and this is where pets get lost:

- The **default** profile lives directly in `~/.hermes/` — so `~/.hermes/pets/` and
  `~/.hermes/config.yaml`.
- **Named** profiles live under `~/.hermes/profiles/<name>/` — so
  `~/.hermes/profiles/helper/pets/` and `~/.hermes/profiles/helper/config.yaml`.

Pets are profile-aware, and a **locally generated** pet exists only in the profile that hatched
it — it is not in the public petdex manifest. So `hermes --profile default pets install ella`
**fails** for a pet you made yourself. To move it across profiles, copy the directory and set
the config by hand:

```bash
# Ella was hatched in the helper profile:
ls ~/.hermes/profiles/helper/pets/ella/

# The default profile uses ~/.hermes/ directly:
mkdir -p ~/.hermes/pets
cp -r ~/.hermes/profiles/helper/pets/ella ~/.hermes/pets/ella

hermes --profile default config set display.pet.slug ella
hermes --profile default config set display.pet.enabled true
hermes --profile default config set display.pet.scale 1.0
```

Mind the asymmetric paths when copying — that is the whole trap.

## Cheat sheet

| Action | Command |
|---|---|
| Browse the gallery | `hermes pets list [query]` |
| Install | `hermes pets install <slug> --select` |
| Switch pet (in session) | `/pet <slug>` |
| Resize | `/pet scale 0.5` or `hermes config set display.pet.scale <0.1-3.0>` |
| Turn off | `/pet off` |
| Generate your own (in session) | `/hatch <description>` |
| Diagnose | `hermes pets doctor` |
| Preview | `hermes pets show --cycle --once` |
| Another profile | `hermes --profile <name> pets ...` |
