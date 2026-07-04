---
id: remotion
name: 'Remotion: React video built by your agent'
summary: >-
  Remotion is a React framework for creating video programmatically. Any coding agent
  (Claude Code, Codex, OpenCode, Cursor) writes motion graphics from a text prompt.
  Installing Node 22 LTS, create-video, a skill for your chosen agent, the Studio workflow,
  rendering, and reference pipelines.
type: tool
author: third_party
recommended: true
added: 2026-07-04
tags: [remotion, video, react, agent, motiongraphics]
source: https://www.remotion.dev/docs/ai/coding-agents
---

# Remotion: React video built by your agent

Remotion is a React framework for creating video **programmatically**. Animation is code,
not a timeline. Paired with a coding agent, you describe the clip in words, the agent writes
React, and out comes a real MP4. In 4–15 iterations you assemble a modern edit from scratch,
with no video skills.

**Multi-agent:** per the official docs, Remotion works with the coding agents
**Claude Code, Codex, OpenCode** (and Cursor). The skill installs for any of them — you
choose at install time. Below are instructions for the agent, not for a specific client.

## Prerequisites

1. **Node.js 22 LTS** (LTS specifically, not "Current" — Remotion 4.x breaks on unstable
   versions: `npm run dev` hangs, `ERR_MODULE_NOT_FOUND`, ESM/CommonJS errors).
2. An installed coding agent (Claude Code / Codex / OpenCode / Cursor…).

### Installing Node 22 LTS
- **Windows:** `winget install OpenJS.NodeJS.LTS` (or the installer from nodejs.org). Paths
  without spaces/Cyrillic. If scripts won't run: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`.
- **macOS:** via Homebrew — `brew install node@22`. On native-build errors:
  `xcode-select --install`.
- **Linux (nvm):**
  ```bash
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
  source ~/.bashrc   # or ~/.zshrc
  nvm install 22 && nvm use 22 && nvm alias default 22
  ```

## Create a project

```bash
npx create-video@latest
```
Recommended answers: **Blank** template, **TailwindCSS — yes**, **install Skills — yes**.
It creates a project folder with the structure:

```
public/   — your assets (images, audio, video, fonts, references)
src/      — code (the agent writes here)
out/      — finished MP4s after rendering
```
Plus an instructions file the agent reads at startup (`CLAUDE.md` / `AGENTS.md` — depending
on your agent). Put references in `public/` — the agent will read the image and reproduce the style.

## Install the Remotion skill (for your agent)

```bash
npx skills add remotion-dev/skills
```
`skills` is an open ecosystem (`vercel-labs/skills`) that installs into **any of 70+ agents**
(Claude Code, Codex, Cursor, OpenCode, Windsurf, Gemini…). At install time pick YOUR agent,
the scope (global — to work from any project), and confirm the recommended options. The skill
is an instruction set that teaches the agent to write correct Remotion code (the right
animation primitives, timings, spring animations, clean composition structure).

Check (for Claude Code — example path): `ls .claude/skills/remotion/` → `SKILL.md` is in there.
Other agents have their own path (Cursor — `.cursor/rules`, universal fallback — `~/.agents/skills/`).

## Workflow

```bash
npm install
npm run dev        # Studio at http://localhost:3000 (port may differ)
```
Then — a prompt to the agent. A working three-step pattern:
1. **Planning** — the agent asks clarifying questions about the assets and the concept.
2. **Script** — the agent briefly describes the future clip, you make edits.
3. **Build** — the agent writes the finished solution.

In Studio you see a layered preview. The agent can rewrite any aspect — it's all animation as
files, not a finished video. Each segment has a frame count: describe segments/frames/time to
edit precisely. Changes in Studio apply instantly, without a page reload.

Background music — for example via generative services (Suno and the like).

## Render

Either via a command/the agent directly, or with the button in Studio (the button gives more
control over the process).

## OS-specific quirks
- **Linux/Wayland (headless):** Remotion renders through Chromium. You may need
  `export DISPLAY=:0` or `npx remotion render ... --gl=angle`. Your own Chromium:
  `export REMOTION_CHROME_EXECUTABLE=$(which chromium)`. Chromium deps (Ubuntu/Debian):
  `libnss3 libatk-bridge2.0-0 libdrm2 libxcomposite1 libxdamage1 libxrandr2 libgbm1
  libasound2 libpango-1.0-0 libcairo2 libatspi2.0-0 libcups2 libxkbcommon0`. Fonts
  (otherwise little squares): `noto-fonts`/`fonts-noto` + liberation.
- **macOS (Apple Silicon):** ARM supported out of the box. Your own Chrome:
  `export REMOTION_CHROME_EXECUTABLE="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"`.
- **IPv6:** if the preview won't open — running strictly on IPv4 helps.

## Reference pipelines

Don't reinvent from scratch — take something ready as a base and ask the agent to build its own:

- **claude-remotion-kickstart** (jhartquist) — a template: 14 components, slash commands, MCP
  (Replicate for images/video, ElevenLabs for voiceover, Deepgram for transcription).
  Fork it via "Use this template", add API keys to env:
  ```bash
  export REPLICATE_API_TOKEN=...    # /generate-image, /generate-video
  export DEEPGRAM_API_KEY=...       # /transcribe
  export ELEVENLABS_API_KEY=...     # voiceover via MCP
  ```
- **video_explainer** (prajwal-y) — a full pipeline in Python: document (PDF/MD/URL) →
  script → TTS → animations (the agent writes React .tsx) → render. Voice synced to frames.
  ```bash
  git clone https://github.com/prajwal-y/video_explainer.git && cd video_explainer
  python -m venv .venv && source .venv/bin/activate
  pip install -e . && cd remotion && npm install && cd ..
  python -m src.cli create my-video
  python -m src.cli generate my-video   # the whole pipeline
  python -m src.cli render my-video     # MP4
  ```

**The key insight:** first vibecode the pipeline itself, then vibecode the specific clips on top of it.
