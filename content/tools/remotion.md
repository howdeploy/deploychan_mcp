---
id: remotion
name: 'Remotion: видео на React руками агента'
summary: >-
  Remotion — React-фреймворк для программного создания видео. Любой кодинг-агент
  (Claude Code, Codex, OpenCode, Cursor) пишет motion-графику по текстовому промпту.
  Установка Node 22 LTS, create-video, скилл под выбранного агента, workflow в Studio,
  рендер и референс-пайплайны.
type: tool
author: third_party
recommended: true
added: 2026-07-04
tags: [remotion, video, react, agent, motiongraphics]
source: https://www.remotion.dev/docs/ai/coding-agents
---

# Remotion: видео на React руками агента

Remotion — React-фреймворк для **программного** создания видео. Анимация — это код,
а не таймлайн. В связке с кодинг-агентом ты описываешь ролик словами, агент пишет React,
и на выходе получается настоящий MP4. За 4–15 итераций собирается современный монтаж с
нуля, без навыков видео.

**Мультиагентность:** по официальным докам Remotion работает с кодинг-агентами
**Claude Code, Codex, OpenCode** (и Cursor). Скилл ставится под любого из них — выбираешь
при установке. Ниже — инструкции для агента, не для конкретного клиента.

## Предусловия

1. **Node.js 22 LTS** (именно LTS, не «Current» — Remotion 4.x ломается на нестабильных
   версиях: зависания `npm run dev`, `ERR_MODULE_NOT_FOUND`, ошибки ESM/CommonJS).
2. Установленный кодинг-агент (Claude Code / Codex / OpenCode / Cursor…).

### Установка Node 22 LTS
- **Windows:** `winget install OpenJS.NodeJS.LTS` (или установщик с nodejs.org). Пути без
  пробелов/кириллицы. Если скрипты не идут: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`.
- **macOS:** через Homebrew — `brew install node@22`. При ошибках нативной сборки:
  `xcode-select --install`.
- **Linux (nvm):**
  ```bash
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
  source ~/.bashrc   # или ~/.zshrc
  nvm install 22 && nvm use 22 && nvm alias default 22
  ```

## Создать проект

```bash
npx create-video@latest
```
Рекомендуемые ответы: шаблон **Blank**, **TailwindCSS — yes**, **install Skills — yes**.
Создаст папку проекта со структурой:

```
public/   — твои ассеты (картинки, аудио, видео, шрифты, референсы)
src/      — код (агент пишет сюда)
out/      — готовые MP4 после рендера
```
Плюс файл инструкций, который агент читает при старте (`CLAUDE.md` / `AGENTS.md` — под
твой агент). Референсы клади в `public/` — агент прочитает изображение и повторит стиль.

## Поставить скилл Remotion (под своего агента)

```bash
npx skills add remotion-dev/skills
```
`skills` — открытая экосистема (`vercel-labs/skills`), ставит в **любой из 70+ агентов**
(Claude Code, Codex, Cursor, OpenCode, Windsurf, Gemini…). При установке выбери СВОЙ агент,
scope (глобально — чтобы работать из любого проекта) и подтверди рекомендованные опции.
Скилл — это инструкция, обучающая агента писать корректный Remotion-код (правильные
анимационные примитивы, тайминги, spring-анимации, чистую структуру композиций).

Проверка (для Claude Code — путь примера): `ls .claude/skills/remotion/` → там `SKILL.md`.
У других агентов путь свой (Cursor — `.cursor/rules`, универсальный fallback — `~/.agents/skills/`).

## Workflow

```bash
npm install
npm run dev        # Studio на http://localhost:3000 (порт может отличаться)
```
Дальше — промпт агенту. Рабочий паттерн из трёх шагов:
1. **Планирование** — агент задаёт уточняющие вопросы по ассетам и задумке.
2. **Сценарий** — агент кратко описывает будущий ролик, ты вносишь правки.
3. **Сборка** — агент пишет готовое решение.

В Studio виден предпросмотр по слоям. Любой аспект агент может переписать — всё анимация
файлами, не готовое видео. Каждый отрезок имеет число кадров: описывай отрезки/кадры/время,
чтобы точечно править. Изменения в Studio применяются мгновенно, без перезагрузки страницы.

Музыка в фоне — например через генеративные сервисы (Suno и подобные).

## Рендер

Либо командой/агентом напрямую, либо кнопкой в Studio (кнопка даёт больше контроля над
процессом).

## Квирки по ОС
- **Linux/Wayland (headless):** Remotion рендерит через Chromium. Может понадобиться
  `export DISPLAY=:0` или `npx remotion render ... --gl=angle`. Свой Chromium:
  `export REMOTION_CHROME_EXECUTABLE=$(which chromium)`. Depsы Chromium (Ubuntu/Debian):
  `libnss3 libatk-bridge2.0-0 libdrm2 libxcomposite1 libxdamage1 libxrandr2 libgbm1
  libasound2 libpango-1.0-0 libcairo2 libatspi2.0-0 libcups2 libxkbcommon0`. Шрифты
  (иначе квадратики): `noto-fonts`/`fonts-noto` + liberation.
- **macOS (Apple Silicon):** ARM поддержан из коробки. Свой Chrome:
  `export REMOTION_CHROME_EXECUTABLE="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"`.
- **IPv6:** если превью не открывается — запуск строго на IPv4 помогает.

## Референс-пайплайны

Не изобретай с нуля — возьми готовое за основу и попроси агента построить своё:

- **claude-remotion-kickstart** (jhartquist) — шаблон: 14 компонентов, слэш-команды, MCP
  (Replicate для картинок/видео, ElevenLabs для озвучки, Deepgram для транскрипции).
  Форкаешь через «Use this template», добавляешь API-ключи в env:
  ```bash
  export REPLICATE_API_TOKEN=...    # /generate-image, /generate-video
  export DEEPGRAM_API_KEY=...       # /transcribe
  export ELEVENLABS_API_KEY=...     # озвучка через MCP
  ```
- **video_explainer** (prajwal-y) — полный пайплайн на Python: документ (PDF/MD/URL) →
  скрипт → TTS → анимации (React .tsx пишет агент) → рендер. Синхронизация голоса с кадрами.
  ```bash
  git clone https://github.com/prajwal-y/video_explainer.git && cd video_explainer
  python -m venv .venv && source .venv/bin/activate
  pip install -e . && cd remotion && npm install && cd ..
  python -m src.cli create my-video
  python -m src.cli generate my-video   # весь пайплайн
  python -m src.cli render my-video     # MP4
  ```

**Главный инсайт:** сначала вайбкодь сам пайплайн, а уже на нём вайбкодь конкретные ролики.
