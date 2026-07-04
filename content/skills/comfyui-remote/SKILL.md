---
id: comfyui-remote
name: 'ComfyUI на арендованном GPU: сетап, API, Telegram'
summary: >-
  Как агенту гонять генерацию в ComfyUI на арендованном GPU-сервере: арендовать
  инстанс, поднять стек скриптом (install + models.manifest), дать агенту SSH-доступ,
  запускать воркфлоу через REST/WebSocket API, батчить и слать картинки в Telegram.
  Плюс анатомия воркфлоу — переключатели, развилки, ползунки.
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

# ComfyUI на арендованном GPU

Вместо десятка подписок и API — арендуешь GPU-сервер под свою работу. При плотной работе
за час это в разы дешевле, чем генерить фото/видео на чужих сервисах. Всё упирается в
готовые воркфлоу ComfyUI + сетап + время на развёртку. Этот скилл автоматизирует развёртку
и даёт агенту рулить генерацией удалённо.

## Аренда сервера (Vast-подобный хостинг)

1. **Billing** — пополни баланс (оплата картой).
2. **Template** — выбери **ComfyUI** (предустановленная среда).
3. **Ползунок диска** — модели тяжёлые: солидная модель под одну задачу 20–30 ГБ, три модели
   на потыкать — уже ~90 ГБ (плюс зависимости, файнтюны, LoRA). За диск платишь и когда инстанс
   выключен (≈$1/сутки за 100 ГБ).
4. **Сервер** — под целый день работы бери $0.6–1.3/час. Агент подскажет цена/качество. Бери
   **датацентр** — иначе файлы качаются по 30+ минут.
5. **RENT** → инстанс создаётся 0.5–2 мин → кнопка **Open**.

Внутри: **Jupyter** (закинуть скрипт установки) + **Terminal** (запустить его) + кнопка
**ComfyUI**. Скрипты кладём в папку `workspace`. Выключить → платишь за диск; логичнее удалить
и поднять новый в след. раз, если ждать очередь дорого.

## Ключи в `.env` — агент спрашивает у пользователя

Для скачивания моделей нужны два бесплатных ключа:
- **HuggingFace token** — https://huggingface.co/settings/tokens (проставь все Read-галки).
- **Civitai key** — https://civitai.com/user/account.

**Агент НЕ хардкодит ключи.** Он спрашивает их у пользователя и кладёт в `.env` НА ИНСТАНСЕ:
```bash
cp .env.template .env
# HF_TOKEN=<пользователь даёт свой>
# CIVITAI_TOKEN=<опционально>
```
`.env` в git не коммитится. Переменные окружения имеют приоритет над `.env`.

## Сетап-скрипт + `models.manifest`

Паттерн развёртки: `setup.sh` читает `.env` (env-driven), ставит custom nodes (git
clone/fetch — идемпотентно), качает модели по манифесту.

`models.manifest` — построчный формат источников:
```
hf|repo|remote_path|target_dir|target_filename          # с HuggingFace
url|direct_url|target_dir|target_filename|min_bytes      # прямая ссылка
civitai|version_id|target_dir|target_filename|name       # с Civitai
```
Все файлы **skip-if-exists** (безопасно перезапускать после обрыва). Полезные env:
`HF_TOKEN`, `CIVITAI_TOKEN`, `COMFYUI_DIR` (`/workspace/ComfyUI`), `SKIP_MODELS`,
`SKIP_CUSTOM_NODES`, `SKIP_HF_LOGIN`, `RESTART_COMFYUI`.

Требования под задачу: VRAM под модель (Flux и видео — обычно ≥24 ГБ), диск (video-стек
легко ~70 ГБ). Gated-репо (напр. `facebook/sam3`) требуют принять условия на HF под тем же токеном.

## Доступ агенту по SSH

```bash
ssh-keygen -t ed25519 -f ~/.ssh/comfyui_agent -N "" -C "agent-comfyui"
cat ~/.ssh/comfyui_agent.pub      # публичный ключ → добавить в инстанс (SSH-раздел / authorized_keys)
ssh -o StrictHostKeyChecking=no -p PORT -i ~/.ssh/comfyui_agent user@HOST "hostname"
```

**Правило туннеля.** ComfyUI открывай через управляемый порт `8188`:
```bash
ssh -p PORT root@HOST -L LOCAL_PORT:127.0.0.1:8188
```
Не гоняй через сырой `18188` — это backend за прокси хостинга, туннель обойдёт auth/monitoring.
Порт `8080` в таких образах — это Jupyter, а не ComfyUI.

## Генерация через ComfyUI API

Воркфлоу нужен в **API-формате** (у каждой ноды есть `class_type`): в UI → **Workflow →
Export (API)**. Паттерн — инжект параметров, submit, poll, скачивание:

```python
import json, urllib.request, time, random, uuid
wf = json.load(open("/tmp/workflow.json"))
wf["14"]["inputs"]["text"] = PROMPT          # позитивный промпт (CLIPTextEncode)
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
Скачать: `scp -P PORT -i KEY user@HOST:/workspace/ComfyUI/output/SUB/FILE.png /tmp/out.png`.
Узнать доступные семплеры/scheduler'ы: `GET /api/object_info/KSampler` (не гадай имена).

**Батч.** Ставь **уникальный `filename_prefix` на каждую джобу** (`f"batch_{i}"`) — иначе три
джобы в одну секунду перезапишут друг друга. Затем queue → poll всех `prompt_id`.

## Анатомия воркфлоу: переключатели, развилки, ползунки

- **Переключатели (switch).** Нода-селектор пресета — например резолюция:
  `1=вертикаль(1024×1280), 2=гориз, 3=TV, 4=cinema`. Boolean **master-route**: `true`=цепочка
  LoRA активна, `false`=база. Ищи `ImpactSwitch`/`ImpactBoolean`/`Primitive`/`Int`.
- **Развилки (branch).** Маршрутизация `model`/`clip` через цепочку LoRA-нод. Байпас ноды:
  `mode: 4` (editor) или **rewire** model/clip в API. Группы — через `rgthree Fast Groups
  Muter/Bypasser`. ⚠️ API-экспорт СХЛОПЫВАЕТ `mode` (байпас теряется) → в API байпас = rewire.
- **Ползунки (slider).** Числовые входы: CFG, steps, denoise, `FluxGuidance`, вес LoRA. Крутишь
  под задачу.
- **Узлы-инструкции.** `MarkdownNote` прямо в графе — заметки автора о параметрах и фишках.

Перед работой: распарси цепочку LoRA (от `UNETLoader` через `LoraLoader`'ы: нода→файл→вес),
найди master-route, сверь ожидания с реальностью (см. скилл `comfyui-prompt-craft`).

## Три архетипа воркфлоу

- **text2image.** Промпт → модель + LoRA → sampler → VAE → save. (Flux: `UNETLoader` +
  `DualCLIPLoader` + `FluxGuidance` + `SamplerCustomAdvanced`.)
- **img2img / inpaint.** Загрузить картинку → выделить область маской (ПКМ → редактор) →
  регенерация ТОЛЬКО маски (параметр `denoise`). Правило: описывай что **меняешь**, а не что
  уже есть — иначе объект перегенерится.
- **pose-reference (ControlNet).** Чужое фото → извлечь скелет позы (DWPose/ViTPose) →
  генерация нового субъекта в этой позе.

## Доставка в Telegram

```python
import subprocess
# токен читается из .env (пользователь дал), не из общего файла
r = subprocess.run(["curl","-s","-X","POST",
  f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
  "-F","chat_id=CHAT_ID","-F","photo=@/tmp/out.png","-F","caption=..."],
  capture_output=True, text=True)
```
Если агент в Docker, а gateway на хосте — файлы контейнера не видны gateway'ю; шли через прямой
Bot API (`sendPhoto`), а не через MEDIA-хэндлер. Терминал может маскировать токен как `***` —
гони curl из Python (`subprocess`), а не голым shell.

## Ответственно

Техника контент-агностична. Пайплайны замены лица/головы в видео (SAM3 + Wan) существуют, но
применяй их **только к совершеннолетним по согласию** и **никогда к реальным людям без их
согласия** — это прямой путь к несогласованным интимным изображениям. 18+ по местным законам
и правилам площадок.
