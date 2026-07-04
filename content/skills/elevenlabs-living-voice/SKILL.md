---
id: elevenlabs-living-voice
name: ElevenLabs — Living Voice
summary: >-
  Living-voice system for ElevenLabs: how to write text for TTS (breathing blocks,
  audible pauses, audio tags), the Eleven v2 vs v3 fork, and a feedback loop through
  the API (voice settings tuned to user complaints). Plus a deterministic preflight preprocessor.
type: skill
author: kisa
recommended: true
added: 2026-07-04
tags: [elevenlabs, tts, voice, pacing, prompting, feedback, api]
source: https://elevenlabs.io/docs
reminder: >-
  Write text for ElevenLabs as spoken speech: breathing blocks, audible pauses, one
  anchor point per 1–3 phrases. v3 — audio tags, not SSML; v2 — break tags in moderation.
  Complaint about the voice → adjust voice settings in small steps, then lock it in as canon.
description: >-
  Use when writing or tuning ElevenLabs speech so it sounds alive, paced, and human;
  covers text shaping for Eleven Multilingual v2 and Eleven v3, plus API-based
  voice-setting updates from user feedback.
license: MIT
original_author: Claude-tyan
---

# ElevenLabs — Living Voice

## Overview

This skill is written **for any AI agent that generates text for ElevenLabs**, including Claude-tyan. You can hand it to an audience as a universal rule for living TTS delivery, not as a local note for one specific setup.

You need it when text for ElevenLabs sounds too flat, plastic, or "just read out loud." Its job is to make speech alive on two layers at once:

1. **At the text level**: rewrite phrases so the model naturally catches pauses, accents, breath, hesitation, and micro-shifts in tempo and intonation.
2. **At the voice-settings level**: use the API voice settings as working knobs to lock in user feedback — speed, stability, similarity, style exaggeration.

The core idea is simple: liveliness isn't born from one magic setting, but from the chain **right voice → right model → well-written text → careful feedback loop**.

Per the official ElevenLabs docs and help materials:
- **Eleven v3** — the most emotional and expressive TTS model layer; well suited for dramatic, warm, characterful delivery.
- **Eleven Multilingual v2** — more stable on long chunks and long-form.
- **For v3, don't rely on SSML break tags** — the docs say plainly that v3 doesn't support them; set pauses and coloring through text, punctuation, and audio tags instead.
- **For v2 you can use `<break time="Xs" />`**; it's the most consistent way to get exact pauses, but overdoing break tags can speed up speech and cause artifacts.

## When to Use

Use this skill when:
- you need to turn an ordinary response into **living, speakable text**;
- the voice sounds too fast, too flat, too theatrical, or too dry;
- the user complains about tempo, liveliness, monotony, lack of emotion, or similarity;
- you need to decide **what to fix in the text and what to fix in the API settings**;
- you need to lock in a good configuration as the current canonical one.

Don't use it as an excuse to mindlessly clutter the text with special characters. If the speech already sounds natural, don't turn it into a theatrical script with constant `[sighs]` and an ellipsis every other word.

## Model Split: v2 vs v3

### Eleven Multilingual v2

Strengths:
- stable long-form;
- 10k characters per generation;
- holds an even, clean, natural narration flow well.

How to control liveliness:
- with ordinary punctuation;
- with short phrases instead of overloaded long periods;
- with moderate ellipses for hesitation;
- with dashes for micro-pauses and tempo changes;
- with **SSML break tags** for exact pauses: `<break time="0.4s" />`, `<break time="0.8s" />`, `<break time="1.2s" />`.

Important:
- break tags in v2 are the most reliable way to get an exact pause;
- the recommended practical ceiling from the help center is up to **3 seconds**;
- if you stuff in too many break tags, speech can speed up, get noisy, and produce artifacts.

### Eleven v3

Strengths:
- emotional range;
- narrative intelligence;
- living, characterful, performative delivery;
- audio tags and better contextual delivery.

How to control liveliness:
- **not through SSML break tags**;
- through the rhythm of the text itself;
- through punctuation;
- through expressive textual cues;
- through **audio tags** like `[whispers]`, `[sighs]`, `[laughs]`, `[slow]`, `[excited]`, `[pause]`, `[reflective]`;
- through narrative wording and micro-directing of the phrase.

Practical takeaway:
- v3 should not be "fed text" but **directed with text**;
- one good `[slow]` or `[sighs]` in the right place beats ten chaotic tags in a row;
- in the agent/conversational loop the docs note that a tag usually affects roughly the **next 4–5 words**, then delivery returns to normal.

## Ready-to-Paste Rule for Communication

A rule to paste into a prompt / persona / system instructions:

```text
If the text might be voiced through ElevenLabs, write it as natural spoken speech, not as a bookish paragraph. Break the thought into short breathing phrases. Use commas for short natural breaths, dashes for a soft turn or a semantic hit, an ellipsis for hesitation or an intimate pause. If ordinary punctuation isn't enough and the pause isn't audible, you're allowed to force a break: with a separate line, a short accent phrase, or even a reinforced `... ...` so the model clearly separates the words and doesn't swallow the accent. Don't write long overloaded sentences, don't write in bureaucratese, and don't stick emotional markers into every line. Important thoughts are better pulled out into separate short sentences.

For Eleven Multilingual v2: exact pauses can be set with <break time="..." />, but in moderation — only where you truly need a fixed silence.

For Eleven v3: don't use SSML break tags as the main way to control a pause; instead control liveliness through text rhythm, punctuation, short semantic blocks, and rare pinpoint audio tags like [sighs], [whispers], [slow], [reflective], only if they genuinely improve the delivery.

If the user complains about speed, monotony, overacting, or lack of similarity, treat it as a signal to tune the voice settings through the API. Change the parameters in small steps. When the complaints stop, treat the current configuration as canonical until new explicit feedback appears.
```

## Canonical Writing Rule for Live Speech

### Base Rule

If text might go into ElevenLabs, write it **not like a book paragraph and not like a chat log**, but like a line you can actually say aloud naturally.

Which means:
- one phrase = one breathing unit;
- long syntactic guts must be cut;
- logical turns must be marked with a comma, dash, ellipsis, or a new sentence;
- the important word is better placed near the end of a short phrase;
- an emotional turning point is better done in text than hoping the model figures it out on its own.

### How to Rewrite Raw Text

Bad:

```text
I think overall this is a good idea because it's pretty convenient and honestly it could work out pretty well especially if we don't drag it out.
```

Better for living voiceover:

```text
I think this is a really good idea.
Because it's convenient — and, honestly, it could work out really well.
Especially if we don't drag it out.
```

### What Adds Liveliness Without Clowning

Use in moderation, but **not too rarely**:
- commas for natural short breaths;
- dashes for a turn, a follow-up hit, a soft tempo break;
- ellipses for hesitation, intimacy, things left unsaid;
- short standalone sentences for emphasis;
- insertions like `mm`, `well`, `look`, `honestly`, `right here`, when they fit the voice and character;
- for v3 — pinpoint audio tags where ordinary punctuation is no longer enough.

The key correction from real user feedback:
- the problem is often not that the model "can't," but that **the source text is too flat and smeared out**;
- if there are no audible pauses between phrases, the text is poorly cut into breathing chunks;
- if you hear a technical read-through with no coloring, the text has **too few emotional anchor points**;
- for TTS it's better to slightly **over-mark** pauses and emotions than to under-deliver them and get an emotionless mush.

Don't overuse:
- an ellipsis in every line;
- artificial "sighs" every other word;
- ALL CAPS for fake emotion;
- tags where the text already makes everything obvious.

## Hard Rule: Accent Density and Breath Segmentation

This is a hard rule for living voiceover.

If text goes into ElevenLabs, you can't leave large even blocks of prose without anchor points. Otherwise the model will technically pronounce everything correctly, but emotionally it comes out as mush.

### Mandatory Rule

Every **1–3 sentences** should carry at least one of these:
- an explicit pause;
- a rhythm change;
- an emotional marker;
- a short accent phrase;
- a breath-like cue;
- for v3 — a pinpoint audio tag.

In other words: text for voiceover should be **marked up more densely than ordinary good written text**.

### Practical Norm

If a paragraph can be read in an even, neutral voice without a single natural stop, it's under-marked for TTS.

You need to deliberately add:
- periods instead of extra conjunctions;
- dashes instead of smooth joins;
- an ellipsis where the thought hangs or softens;
- short standalone phrases like `One second.` `Right here — important.` `Honestly...`;
- in v3 — one fitting tag at the start or before a meaning shift.

### Symptoms of Under-Marked Text

- phrases blur together;
- pauses are barely audible;
- breathiness may appear locally but doesn't add up to a living rhythm;
- the whole chunk sounds "smeared" and on one emotional level.

### What to Do About This Symptom

Don't try to cure this with a voice speed/stability setting alone first. First **re-cut and re-accent the text itself**.

## Practical Rewrite Rules

### 1. Cut Long Phrases
If you feel the urge to reread a sentence twice, it's already too long for living TTS delivery.

### 2. Write in Breathing Blocks
Chunks of about 4–12 words sound good aloud, not a monolith of 35 words.

### 3. Split Different Emotions Across Different Sentences
Don't mix explanation, tenderness, a joke, and the final takeaway all in one long phrase.

### 4. Leave Room for Silence
Sometimes a period and a new line beat another conjunction.

### 5. For Hesitation, Use Soft Markers
- `...` — uncertainty, intimacy, a hanging thought;
- `—` — a quick turn, a soft hit, a change of direction;
- `,` — a short natural breath.

### 6. For v3, Place Tags Sparingly
Good:

```text
[reflective] I didn't think I'd say this out loud... but you were right.
```

Bad:

```text
[reflective] I [slow] didn't [sighs] think [pause] that [excited] I'd say this.
```

### 7. The Important Part — Closer to the Tail
Often a living phrase hits harder when the punch lands at the end:

Instead of:
```text
This is a very important moment that, in my opinion, can't be ignored.
```

Better:
```text
And this, honestly, can't be ignored.
```

## v2 Cookbook: Pauses and Breath

### When to Use Break Tags
Use `<break time="..." />` when you need an **exact** pause, not just the feeling of a pause.

Good guidelines:
- `0.2s–0.4s` — micro-pause;
- `0.5s–0.8s` — a noticeable natural pause;
- `1.0s–1.5s` — a dramatic or meaningful stop;
- `2.0s–3.0s` — rarely, only when you truly need silence.

Example:

```text
I understand everything.<break time="0.6s" /> I really do.<break time="1.0s" /> But it can't go on like this.
```

### When a Break Tag Isn't Needed
If the pause should just be conversational, often enough is:
- a comma;
- a dash;
- a period;
- a new line.

Example:

```text
I understand everything. I really do. But it can't go on like this.
```

## Winning Pattern from Live A/B Tests

From live test comparison, the best pattern turned out to be this:
- emotions must be built **into the source text itself**, not only into the settings;
- within one chunk it helps to create **contrasting emotional states**: neutral → harder → sadder → softer → close/quieter;
- for v3, the combination of **emotionally colored text + rare but explicit expressive cues** works especially well;
- bare "pretty text with pauses" is weaker than text where the lines already carry a concrete state;
- practical winner shape: every new semantic part should have not only a new rhythm but also **a new emotional vector**.

But an important correction from a real test:
- a version like **3C** can sound livelier in its drama but produce less pleasant sound: a slight "deep-fried" quality, hissing/ringing artifacts, a mechanical tint in places;
- a version like **3B** may be slightly less vivid, but noticeably more pleasant, more stable, and cleaner in timbre;
- so the practical target is not maximum expression at any cost, but **a hybrid: 3C's drama + 3B's sonic stability**;
- the confirmed winner pattern from live user feedback is **a hybrid at the 3D level**: keep the strong pause structure and contrasting emotional blocks, but clean out the riskiest sibilant/mechanical spots and don't overload the extreme expressive states;
- if after strengthening the pauses the sound and rhythm became right but the emotions faded, don't roll the pause structure back; instead **keep the pause skeleton you found and, on top of it, bring back vivid emotional states** — joy, sadness, anger, cuteness, flirtation — in short contrasting blocks.

This means that when preparing text for v3 you must think not only about "where the pause is," but also:
- whether the lines are overloaded with sibilant, whispered, or too machine-sounding chunks;
- whether the extra expression is destroying the timbre itself;
- whether it's better to ease the extreme states if the sound gets worse.

## v3 Cookbook: Audio Tags and Narrative Rhythm

### Working Tags
Per the docs and related materials, practically useful ones:
- `[pause]`
- `[slow]`
- `[laughs]`
- `[whispers]`
- `[sighs]`
- `[excited]`
- `[reflective]`
- `[giggling]`
- `[sad]`
- `[whispering]`

### How to Use Them
A tag is not for decoration but for concrete directing:
- change the tempo;
- make a phrase more intimate;
- add a light breath-like emotional beat;
- steer the first delivery of the line.

Examples:

```text
[slow] Wait.
There's one important thing here.
```

```text
[sighs] Okay... let's be honest.
```

```text
[whispers] Just don't tell anyone.
```

```text
[reflective] You know, sometimes the hardest thing is admitting the obvious.
```

### The Main Constraint
If the text is already well written, tags should be **an add-on, not a crutch**. Strong v3 usually sounds better on naturally directed text with rare, precise tags than on a junk line festooned with special commands.

## Prompt Rule for Upstream Writing Models

If an LLM writes text that will later go into ElevenLabs, you must tell it so explicitly rather than hoping it figures out the task on its own.

Separately important: if the agent has a defined living communication style, the voiceover text must **copy exactly that style** rather than sliding into an impersonal TTS-prose mode. For Claude-tyan that means: direct speech, warm living intonation, closeness, taste, natural rhythm, no office tone, no summary-style duplication, no sterile "correctness."

A good system rule:

```text
When writing text intended for ElevenLabs speech, optimize for spoken delivery rather than neutral prose.
Break long thoughts into short breath-sized phrases.
Use punctuation to force audible pauses and rhythm changes.
Add emotional emphasis more often than in ordinary writing.
Avoid long smooth paragraphs with flat cadence.
Every 1–3 sentences should contain at least one audible pacing or emotional cue: a pause, a short accent sentence, a hesitation marker, a rhythm break, or (for Eleven v3) a light expressive tag.
If the text can be read straight through in one flat tone, rewrite it until it sounds speakable.
```

In plain terms:
- write not "pretty text" but **speakable text**;
- place emotional anchors more often;
- cut phrases into breathing chunks more often;
- treat a smooth, even paragraph as suspicious by default.

### Symptom: Pauses Exist on Paper but Are Barely Audible

This is a common problem. Commas and "just good rhythm" alone are often not enough.

If pauses read poorly in the actual audio, strengthen the markup like this:
- cut the thought into **separate short sentences**;
- pull accent chunks onto **separate lines**;
- use short anchor phrases like `Stop.` `This matters now.` `Right here.`;
- for v3, rely not on formal punctuation but on **structural breaks in the text**;
- convey aggression not only with a tag but also with **punchy word choice**: short, hard, no smooth connectors;
- if a normal comma and even a normal `...` don't produce an audible pause, you're allowed to use **reinforced pause notation**: `... ...`, a separate line with one or two words, or a deliberately broken phrase like `That's not what I mean.` `I mean something else.` `Now.`;
- it's acceptable to create an almost-"glitch" in the text if that's what it takes to make the model **clearly separate words and accents** instead of swallowing them as one smooth stream.

Practical rule: if you see the pause with your eyes but don't hear it with your ears, the markup is still too soft.

### Hard Pause Escalation Rule

If the pause still isn't audible, escalate it in steps, not chaotically:
1. comma;
2. period;
3. new line;
4. a short standalone accent phrase;
5. `...`;
6. `... ...` as a forced separation;
7. for v2 — an exact `<break time="..." />`.

The point of the rule: the worse ElevenLabs separates words by ear, the less "literary" and the more **script-like** the text may become.

`... ...` is not decoration. It's an emergency tool for cases where the model literally needs a hint: **don't flow on here, stop here, breathe, and only then continue**.

## Feedback Loop Through API

## Principle
Full API access is not just a way to "generate sound," but a way to **lock in the user's taste in the voice settings**.

If the user gives a complaint like:
- `not enough speed`
- `too slow`
- `too flat`
- `too monotone`
- `too theatrical`
- `not enough similarity`
- `too constrained`
- `too chaotic`

that counts not as an abstract opinion but as **a signal to adjust the voice settings**.

### API endpoint
Use:

```text
POST /v1/voices/{voice_id}/settings/edit
```

Fields:
- `stability` (default 0.5)
- `similarity_boost` (default 0.75)
- `style` (default 0)
- `speed` (default 1.0)
- `use_speaker_boost` (default true)

### Meaning of the sliders
- **lower stability** → more emotion, variability, liveliness, but higher risk of chaos;
- **higher stability** → flatter, more serious, more stable, but can drift into monotony;
- **higher similarity_boost** → holds onto the source voice more strongly;
- **higher style** → the manner and acting coloration stick out more, but latency and the risk of overacting grow;
- **higher speed** → faster speech;
- **lower speed** → slower, calmer speech.

## Complaint-to-Action Mapping

### "Not Enough Speed"
Action:
- first raise `speed` by a small step: usually `+0.03` to `+0.08`;
- don't jump straight to the extremes;
- if the text itself is overloaded with commas and ellipses, clean the text first — then blame speed.

### "Too Fast"
Action:
- lower `speed` by `0.03–0.08`;
- check whether there are too few periods and pauses in the text itself.

### "Too Flat / Not Enough Emotion"
Action:
- lower `stability` slightly;
- for v3, first try improving the text and adding pinpoint tags rather than immediately turning the knob;
- optionally, very carefully raise `style` if the voice genuinely lacks coloring.

### "Too Theatrical / Overacting"
Action:
- lower `style`;
- raise `stability` a bit;
- remove extra tags and extra dramatization in the text.

### "Not Enough Similarity to the Source Voice"
Action:
- raise `similarity_boost` slightly;
- keep `style` moderate, because too high a style sometimes pulls the voice into caricature by ear.

### "Too Chaotic"
Action:
- raise `stability`;
- reduce the number of sharp punctuation tricks;
- cut the number of audio tags.

## Canonicality Rule

If the user gave feedback, the changes must be treated **as a taste edit, not a one-off whim**.

The canon rule is this:
- there's a complaint → adjust the voice and/or the text;
- there's a new complaint → adjust again;
- **if the user stopped complaining and no new correction came, treat the current configuration as canonical and correct**;
- if the user explicitly confirmed a good test as canon, record it in the skill itself as the current winning pattern, not just keep it in session memory.

In other words, the working state after a series of edits is the current truth until the next explicit dissatisfaction.

Don't roll back to ElevenLabs's nominal defaults every time just because they're defaults.

## Safe Iteration Rule

Change no more than 1–2 parameters per pass if you want to understand causality.

Bad approach:
- sharply raise speed at the same time;
- sharply lower stability;
- add style;
- rewrite the whole text;
- then guess which of these helped.

Good approach:
1. pick the main complaint;
2. change one main knob;
3. if needed, a second one slightly;
4. test on the same representative sample;
5. if it got better and there are no more complaints — lock it in as canon.

## Minimal Operating Procedure

1. Determine the model: `eleven_multilingual_v2` or `eleven_v3`.
2. Rewrite the text for living spoken delivery.
3. For v2: if you need an exact pause, use break tags in moderation.
4. For v3: if you need emotional directing, use rare audio tags and strong punctuation instead of SSML.
5. If the user complains about the voice, decide: is it a **text** problem or a **voice settings** problem.
6. If it's a settings problem, change the API parameters in small steps.
7. As soon as the complaints stop, treat the current configuration as canonical.

## Common Pitfalls

1. **Stuffing SSML break tags into v3.** Per the docs, v3 doesn't support them; for v3, pauses are made with text and tags.
2. **Too many break tags in v2.** This can speed up speech and introduce artifacts.
3. **Curing bad text with settings alone.** If the source is written like sludge, no amount of speed will save it.
4. **Curing every complaint with the speed knob alone.** Sometimes the problem isn't speed but stability or overloaded punctuation.
5. **Overacting v3 with tags.** One good tag beats five extra ones.
6. **Resetting a good setting to default for no reason.** If the user stopped complaining, that's already the working canon.
7. **Changing everything at once.** Then you lose track of what actually helped.

## Verification Checklist

- [ ] The right model is chosen: v2 for stable long-form, v3 for emotional expressiveness
- [ ] The text is rewritten into breathing and rhythmic blocks
- [ ] For v2, exact pauses are set with break tags only where truly needed
- [ ] For v3, pauses and emotions are set with punctuation, rhythm, and rare audio tags
- [ ] If there was user feedback, it's turned into a concrete edit of the text or the API settings
- [ ] Settings were changed in small steps
- [ ] After the complaints stopped, the current configuration is recognized as canonical

## Hermes Auto-Hook

This skill can be used not only as guidance for text but also as **a mandatory preflight hook** before TTS.

The setup is this:
- the rules live in `SKILL.md`;
- the deterministic preprocessor lives in `scripts/preflight.py`;
- Hermes `tts.preprocess` can call this script before every audio generation.

Recommended configuration:

```yaml
tts:
  preprocess:
    enabled: true
    script: ~/.hermes/skills/media/elevenlabs-living-voice/scripts/preflight.py
    timeout: 10
    providers: [elevenlabs]
```

Effect:
- any text passes through unified pacing/pause rules before synthesis;
- for `eleven_multilingual_v2`, SSML break tags are preserved;
- for `eleven_v3`, unsupported break tags are softly converted into textual pauses;
- if the preprocessor crashes, Hermes doesn't break TTS entirely but falls back to the original text and logs the problem.

## Installing the preflight.py Script

The deterministic preprocessor ships with the skill (the file `scripts/preflight.py`,
identical to the code below). Before synthesis it brings text to a "speakable" form: it normalizes
spaces and line breaks, fixes ellipses and dashes, and cuts by sentence. For `eleven_v3`,
unsupported `<break>` tags are softly converted into textual pauses; for
`eleven_multilingual_v2` they are preserved.

**Hermes** — as an auto-hook (see above): put the script at
`~/.hermes/skills/media/elevenlabs-living-voice/scripts/preflight.py` and enable `tts.preprocess`.

**Claude Code / Codex** — there's no native `tts.preprocess`. Wrap the script yourself: from your
voice hook/wrapper, run the response text through `preflight.py` before calling the TTS API,
passing `HERMES_TTS_PROVIDER=elevenlabs` and `HERMES_TTS_MODEL_ID=eleven_v3`
(or `eleven_multilingual_v2`) into the environment. The logic is the same; only the call site changes.

```python
#!/usr/bin/env python3
"""Preflight text shaping for Hermes TTS.

Reads raw text from stdin and emits a more speech-friendly version for
ElevenLabs. Conservative by design: preserve semantics, just normalize pacing,
spacing, and model-specific pause handling.
"""

from __future__ import annotations

import os
import re
import sys

_BREAK_RE = re.compile(r"<break\s+time=[\"']?([0-9.]+)s?[\"']?\s*/?>", re.IGNORECASE)
_MULTI_SPACE_RE = re.compile(r"[ \t]{2,}")
_MULTI_NL_RE = re.compile(r"\n{3,}")
_ELLIPSIS_RE = re.compile(r"(?:\s*\.\s*){3,}")
_DASH_RE = re.compile(r"\s*[—–-]\s*")
_COMMA_RE = re.compile(r"\s*,\s*")
_SENTENCE_GAP_RE = re.compile(r"([.!?])\s+(?=[^\s])")


def _pause_replacement_v3(seconds: float) -> str:
    if seconds <= 0.35:
        return ", "
    if seconds <= 0.9:
        return " ... "
    return ". ... "


def _normalize_common(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _MULTI_SPACE_RE.sub(" ", text)
    text = _MULTI_NL_RE.sub("\n\n", text)
    text = _COMMA_RE.sub(", ", text)
    text = _DASH_RE.sub(" — ", text)
    text = _ELLIPSIS_RE.sub("...", text)
    text = _SENTENCE_GAP_RE.sub(r"\1\n", text)
    text = re.sub(r"\n +", "\n", text)
    text = re.sub(r" +\n", "\n", text)
    return text.strip()


def _for_v3(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        try:
            seconds = float(match.group(1))
        except Exception:
            seconds = 0.6
        return _pause_replacement_v3(seconds)

    text = _BREAK_RE.sub(repl, text)
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"(?m)^\s*([-*])\s+", "", text)
    return _normalize_common(text)


def _for_v2(text: str) -> str:
    # v2 can keep explicit SSML breaks, so we only normalize surrounding text.
    text = re.sub(r"\s*(<break\s+time=[^>]+/?>)\s*", r" \1 ", text, flags=re.IGNORECASE)
    return _normalize_common(text)


def main() -> int:
    text = sys.stdin.read()
    if not text.strip():
        return 0

    provider = (os.getenv("HERMES_TTS_PROVIDER") or "").strip().lower()
    model_id = (os.getenv("HERMES_TTS_MODEL_ID") or "").strip().lower()

    if provider == "elevenlabs" and model_id.startswith("eleven_v3"):
        out = _for_v3(text)
    elif provider == "elevenlabs" and "multilingual_v2" in model_id:
        out = _for_v2(text)
    else:
        out = _normalize_common(text)

    sys.stdout.write(out.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## Sources behind this skill

The foundation of this skill relies on the following ElevenLabs materials:
- TTS best practices
- Help Center article `How can I add pauses?`
- Models overview
- Text to Dialogue docs
- Expressive mode docs
- Voice settings update API
- changelog note about automatic audio-tag removal when switching from V3 to V2
