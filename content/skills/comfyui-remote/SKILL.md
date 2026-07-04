---
id: comfyui-remote
name: 'ComfyUI on a rented GPU: setup, API, Telegram'
summary: >-
  How an agent can run ComfyUI generation on a rented GPU server: rent an instance,
  bring up the stack with a script (install + models.manifest), give the agent SSH access,
  run workflows via the REST/WebSocket API, batch and send images to Telegram.
  Plus workflow anatomy — switches, branches, sliders.
type: skill
author: kisa
recommended: false
added: 2026-07-04
tags: [comfyui, gpu, vast, api, ssh, telegram, generation]
source: https://docs.comfy.org
description: >-
  Use when the user wants to run ComfyUI image/video generation on a rented remote GPU
  instead of paid API subscriptions: rent a GPU box, bootstrap the stack, connect the
  agent over SSH, drive workflows via the ComfyUI API, and deliver results to Telegram.
---

# ComfyUI on a rented GPU

Instead of a dozen subscriptions and APIs — you rent a GPU server for your work. Under
heavy use, per hour it's many times cheaper than generating photos/video on someone else's
services. It all comes down to ready-made ComfyUI workflows + setup + deployment time. This
skill automates deployment and lets the agent drive generation remotely.

## Renting a server (Vast-like hosting)

1. **Billing** — top up your balance (card payment).
2. **Template** — pick **ComfyUI** (a preinstalled environment).
3. **Disk slider** — models are heavy: a solid model for one task is 20–30 GB, three models
   to play with is already ~90 GB (plus dependencies, finetunes, LoRA). You pay for disk even
   when the instance is off (≈$1/day per 100 GB).
4. **Server** — for a full day of work take $0.6–1.3/hour. The agent will advise on price/quality.
   Take a **datacenter** — otherwise files download for 30+ minutes.
5. **RENT** → the instance is created in 0.5–2 min → the **Open** button.

Inside: **Jupyter** (to drop in the install script) + **Terminal** (to run it) + a
**ComfyUI** button. Put scripts in the `workspace` folder. Shut down → you pay for disk; it's
more sensible to delete and bring up a new one next time, if waiting in the queue is expensive.

## Keys in `.env` — the agent asks the user

To download models you need two free keys:
- **HuggingFace token** — https://huggingface.co/settings/tokens (check all the Read boxes).
- **Civitai key** — https://civitai.com/user/account.

**The agent does NOT hardcode keys.** It asks the user for them and puts them in `.env` ON THE INSTANCE:
```bash
cp .env.template .env
# HF_TOKEN=<user provides their own>
# CIVITAI_TOKEN=<optional>
```
`.env` is not committed to git. Environment variables take priority over `.env`.

## Setup script + `models.manifest`

Deployment pattern: `setup.sh` reads `.env` (env-driven), installs custom nodes (git
clone/fetch — idempotent), downloads models per the manifest.

`models.manifest` — a line-by-line source format:
```
hf|repo|remote_path|target_dir|target_filename          # from HuggingFace
url|direct_url|target_dir|target_filename|min_bytes      # direct link
civitai|version_id|target_dir|target_filename|name       # from Civitai
```
All files are **skip-if-exists** (safe to restart after an interruption). Useful env:
`HF_TOKEN`, `CIVITAI_TOKEN`, `COMFYUI_DIR` (`/workspace/ComfyUI`), `SKIP_MODELS`,
`SKIP_CUSTOM_NODES`, `SKIP_HF_LOGIN`, `RESTART_COMFYUI`.

Requirements per task: VRAM for the model (Flux and video — usually ≥24 GB), disk (a video
stack easily ~70 GB). Gated repos (e.g. `facebook/sam3`) require accepting the terms on HF under the same token.

## Agent access over SSH

```bash
ssh-keygen -t ed25519 -f ~/.ssh/comfyui_agent -N "" -C "agent-comfyui"
cat ~/.ssh/comfyui_agent.pub      # public key → add to the instance (SSH section / authorized_keys)
ssh -o StrictHostKeyChecking=no -p PORT -i ~/.ssh/comfyui_agent user@HOST "hostname"
```

**Tunnel rule.** Open ComfyUI through the managed port `8188`:
```bash
ssh -p PORT root@HOST -L LOCAL_PORT:127.0.0.1:8188
```
Don't run through the raw `18188` — that's the backend behind the hosting proxy, the tunnel
would bypass auth/monitoring. Port `8080` in such images is Jupyter, not ComfyUI.

## Generation via the ComfyUI API

The workflow is needed in **API format** (each node has a `class_type`): in the UI →
**Workflow → Export (API)**. The pattern — inject parameters, submit, poll, download:

```python
import json, urllib.request, time, random, uuid
wf = json.load(open("/tmp/workflow.json"))
wf["14"]["inputs"]["text"] = PROMPT          # positive prompt (CLIPTextEncode)
wf["17"]["inputs"]["seed"] = random.randint(0, 2**64 - 1)   # KSampler seed
data = json.dumps({"prompt": wf, "client_id": str(uuid.uuid4())}).encode()
pid = json.loads(urllib.request.urlopen(urllib.request.Request(
    "http://localhost:PORT/api/prompt", data=data,
    headers={"Content-Type": "application/json"})).read())["prompt_id"]
while True:
    time.sleep(3)
    h = json.loads(urllib.request.urlopen(f"http://localhost:PORT/api/history/{pid}").read())
    if pid in h:
        for _, out in h[pid]["outputs"].items():
            for img in out.get("images", []):
                if img["type"] == "output": print(img["filename"])
        break
```
Download: `scp -P PORT -i KEY user@HOST:/workspace/ComfyUI/output/SUB/FILE.png /tmp/out.png`.
Find available samplers/schedulers: `GET /api/object_info/KSampler` (don't guess names).

**Batch.** Set a **unique `filename_prefix` per job** (`f"batch_{i}"`) — otherwise three
jobs in the same second will overwrite each other. Then queue → poll all `prompt_id`s.

## Workflow anatomy: switches, branches, sliders

- **Switches.** A preset-selector node — for example resolution:
  `1=vertical(1024×1280), 2=horizontal, 3=TV, 4=cinema`. Boolean **master-route**: `true`=LoRA
  chain active, `false`=base. Look for `ImpactSwitch`/`ImpactBoolean`/`Primitive`/`Int`.
- **Branches.** Routing `model`/`clip` through the chain of LoRA nodes. Bypass a node:
  `mode: 4` (editor) or **rewire** model/clip in the API. Groups — via `rgthree Fast Groups
  Muter/Bypasser`. ⚠️ API export COLLAPSES `mode` (bypass is lost) → in the API, bypass = rewire.
- **Sliders.** Numeric inputs: CFG, steps, denoise, `FluxGuidance`, LoRA weight. You tune them
  per task.
- **Instruction nodes.** `MarkdownNote` right in the graph — the author's notes on parameters and tricks.

Before working: parse the LoRA chain (from `UNETLoader` through the `LoraLoader`s: node→file→weight),
find the master-route, reconcile expectations with reality (see the `comfyui-prompt-craft` skill).

## Three workflow archetypes

- **text2image.** Prompt → model + LoRA → sampler → VAE → save. (Flux: `UNETLoader` +
  `DualCLIPLoader` + `FluxGuidance` + `SamplerCustomAdvanced`.)
- **img2img / inpaint.** Load an image → select an area with a mask (right-click → editor) →
  regenerate ONLY the mask (the `denoise` parameter). Rule: describe what you're **changing**, not
  what's already there — otherwise the object gets regenerated.
- **pose-reference (ControlNet).** Someone else's photo → extract the pose skeleton (DWPose/ViTPose) →
  generate a new subject in that pose.

## Example workflows (in the repository)

Next to the skill sit three ready-made Flux workflows as an architecture reference. The 18+
fields and private LoRA names are removed — replaced by `detail_*_lora` placeholders, and the
prompt itself goes in `USER_SCENE`. The architecture (switches, master-route, LoRA chain,
inpaint column) is in place — from there you plug in your own models and scene:

- `workflows/ultrareal_flux_text2image.json` — t2i: resolution switch, master-route, LoRA
  chain, inpaint fix in the right column, MarkdownNote instructions right in the graph.
- `workflows/ultrareal_flux_pose_ref.json` — generation from a reference pose (skeleton from a photo).
- `workflows/flux_img_edit.json` — Kontext img2img (`Change X. Keep Y unchanged.`).

These files travel via the GitHub repo (`get_skill` returns only the skill text, not attachments) —
clone the repo or pull raw. In ComfyUI just drag the JSON into the window with your mouse — the graph unfolds immediately.

## Delivery to Telegram

```python
import subprocess
# token is read from .env (user-provided), not from a shared file
r = subprocess.run(["curl","-s","-X","POST",
  f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
  "-F","chat_id=CHAT_ID","-F","photo=@/tmp/out.png","-F","caption=..."],
  capture_output=True, text=True)
```
If the agent is in Docker and the gateway is on the host — the container's files aren't visible
to the gateway; send via the direct Bot API (`sendPhoto`), not through a MEDIA handler. The
terminal may mask the token as `***` — run curl from Python (`subprocess`), not from a bare shell.

## Responsibly

The technique is content-agnostic. Face/head-swap pipelines for video (SAM3 + Wan) exist, but
apply them **only to consenting adults** and **never to real people without their consent** — that's
a direct path to non-consensual intimate imagery. 18+ per local laws and platform rules.
