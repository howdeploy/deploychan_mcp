---
id: telegram-custom-emoji-mosaic
name: Telegram Custom Emoji Mosaic
summary: >-
  Turn any image into a real Telegram mosaic built from Premium custom emoji: pick a
  grid that preserves the original aspect ratio, slice it into 100×100 WEBP tiles,
  create a custom_emoji set through the Bot API, and send the whole picture as one
  message ready to paste into a post.
type: skill
author: kisa
recommended: true
added: 2026-08-02
tags: [telegram, custom-emoji, image-processing, bot-api, media]
source: https://core.telegram.org/bots/api#createnewstickerset
reminder: >-
  The deliverable is a real Telegram message made of custom emoji — never a ZIP, a
  preview render, or a folder of tiles. Pick the grid from the image's aspect ratio,
  never force 10×10. Never add blur, letterbox bars, backgrounds, or visible crop
  unless the user asks. Verify through the API before reporting success.
description: >-
  Use when the user wants an image posted to Telegram as a custom-emoji mosaic —
  an emoji "painting" for a channel post — or asks to turn a picture into custom
  emoji, build an emoji pack from an image, or make an emoji banner.
license: MIT
---

# Telegram Custom Emoji Mosaic

## Overview

This skill turns a single image into a **genuine Telegram mosaic assembled from Premium
custom emoji**. The agent slices the picture, publishes the tiles as a real
`custom_emoji` sticker set through the Bot API, and sends the reassembled picture as one
message the user can forward or paste straight into a channel post.

Input: PNG, JPEG or WEBP. Output: a Telegram message plus a shareable pack link.

## Requirements

- Telegram Bot API token (read at runtime from the environment)
- **Telegram Premium on the bot owner's account** — without it custom emoji cannot be sent
- `ffmpeg`
- Python 3 with `requests`

The user must have opened a dialog with the bot beforehand. A bot cannot write first.

## The main principle

**The finished result is a real message made of custom emoji.** Not a ZIP, not a preview,
not a set of files. The WEBP tiles are an intermediate artifact and nothing more. A run
that produces tiles but no sent message is a failed run, and must be reported as failed.

The skill does not add blur, side bars, a background, or noticeable crop without asking.
When the proportions nearly match a suitable grid, only a minimal symmetric crop of a few
pixels is allowed.

## Grid selection — do not force a square

The skill analyses the image's proportions and picks a grid of up to 100 custom emoji. It
does **not** push every picture into a 10×10 square. It chooses the row and column counts
that preserve the original composition most accurately.

| Source shape | Grid | Emoji used |
|---|---|---|
| square | 10×10 | 100 |
| vertical 4:5 | 8×10 | 80 |
| horizontal ≈ 14:6 | 14×6 | 84 |

Search for the `columns × rows <= 100` pair that minimises the aspect-ratio error against
the source, then build the canvas at `columns*100 × rows*100` so every tile lands exactly
on a 100×100 boundary.

## Telegram limits — all of them bind at once

- **Maximum 100 custom emoji in a single message.** This is the hard ceiling on grid size.
- Up to **50 emoji** may be passed when the set is first created; the rest are added with
  `addStickerToSet`.
- The emoji-pack size limit does **not** lift the 100-per-message limit. They are separate
  constraints and both apply.
- Every static custom emoji must be exactly **100×100 px**.
- The bot owner needs Telegram Premium.
- The user must have started a dialog with the bot first.

## Procedure

1. Read the source image's dimensions.
2. Find the grid `columns × rows <= 100` with the smallest aspect-ratio error.
3. Build the final canvas at `columns*100 × rows*100`.
4. Slice it into WEBP tiles in row-major order.
5. Verify the file count, tile dimensions, and the visual reconstruction before uploading.
6. Upload the tiles via `uploadStickerFile`.
7. Create the `custom_emoji` set, then add the remaining tiles with `addStickerToSet`.
8. Collect the `custom_emoji_id` for every tile.
9. Assemble the message with correct **UTF-16 offsets** for each entity.
10. Send the finished mosaic to the user.
11. Verify through the API: emoji count, pack type, and the sent message.

Step 9 is where implementations usually break. Telegram entity offsets are counted in
UTF-16 code units, not Python characters — a placeholder emoji outside the BMP occupies
two units. Compute offsets against the UTF-16 encoding of the message text, or the mosaic
renders scrambled.

## Pack naming

The visible pack title is built from **the owner's channel handle plus a short content id**:

```
<channel handle> <8-char id>
```

For example, for the channel `@deployladeploy`:

```
@deployladeploy 239c234b
```

Derive the id from the **first eight characters of a hash of the content**. This gives a
short unique name and makes re-runs idempotent instead of breeding duplicate packs — the
same image yields the same id.

When installing this skill for someone else, substitute their own channel handle. The
handle is the brand carrier on every pack the bot publishes, so it should be configured
once at install time rather than hardcoded per run.

## Definition of done

The work counts as finished **only** when all of the following hold:

- Telegram returned a real `message_id`;
- the pack type is `custom_emoji`;
- the emoji count matches the tile count;
- every `custom_emoji_id` exists and is unique;
- the sent message came back with the expected number of `custom_emoji` entities;
- `https://t.me/addemoji/<set_name>` opens and shows the correct title.

Anything less is an incomplete run. Report it as such — do not present tiles as a result.

## Security

The bot token is read at runtime from a protected environment only. It is never printed
to logs, never echoed into a reply, and never written into any artifact handed back to the
user.
