---
id: gstack
name: 'gstack: рабочий контур для Claude Code (+ gbrowser)'
summary: >-
  gstack — опенсорс-набор Гарри Тана: скиллы-режимы для Claude Code (планирование,
  ревью, QA, шип) поверх персистентного headless-браузера gbrowser (/browse). Что это,
  как ставится, ключевые команды. Честно: это Claude-Code-набор, не мультиагент.
type: tool
author: third_party
recommended: false
added: 2026-07-04
tags: [gstack, gbrowser, claude-code, workflow, qa, browser]
source: https://github.com/garrytan/gstack
---

# gstack: рабочий контур для Claude Code (+ gbrowser)

gstack (`garrytan/gstack`, MIT) — не новая модель и не фреймворк агента, а **workflow-слой
для Claude Code**. Пакует доставку софта в набор скиллов-режимов: планирование, ревью, QA,
шип, браузер, ретро. Идея — дать Claude Code явные роли (CEO / дизайнер / eng-manager /
release-manager / QA) вместо одного размытого системного промпта.

**Честная оговорка про мультиагентность.** gstack — Claude-Code-нативный: ставится в
`~/.claude/skills/`, читает `CLAUDE.md`, команды идут как слэш-скиллы Claude Code. Это НЕ
мультиагентный инструмент. Внутри есть `/codex` (делегировать задачу Codex) и gbrain
(кросс-машинная память), но сам контур заточен под Claude Code. Подаю как есть, без
искусственного «мультиагентим».

## gbrowser — персистентный браузер (`/browse`)

Главный технический компонент. gstack держит **долгоживущий headless-Chromium** поверх
localhost HTTP: cookies, вкладки, `localStorage`, состояние логина переживают между командами.
Агент логинится, кликает по приложению, снимает скриншоты, инспектит поломки. Это тот самый
браузер, которым удобно дорендеривать JS-страницы и скрапить (канал 2 из гайда `agent-internet`).

`/qa` строится поверх: анализирует дифф ветки → находит затронутые роуты → тестит именно их
против локального приложения. Не отдельный ручной прогон, а привязка QA к изменениям в коде.

## Установка

```bash
git clone --single-branch --depth 1 https://github.com/garrytan/gstack ~/.claude/skills/gstack
cd ~/.claude/skills/gstack && ./setup
```

Затем добавь секцию `## gstack` в `CLAUDE.md` (использовать `/browse` для веба + список
скиллов). Без этой секции Claude может «не видеть» скиллы.

## Ключевые скиллы

- **Планирование/стратегия:** `/office-hours` (продуктовые идеи), `/plan-ceo-review` (скоуп),
  `/plan-eng-review` (архитектура), `/plan-design-review`, `/autoplan` (весь пайплайн ревью).
- **Код/баги:** `/review` (дифф перед мержем), `/investigate` (баги, «почему сломалось»).
- **QA/браузер:** `/browse` (открыть/тестить сайт), `/qa` (тест по диффу), `/qa-only` (только
  репорт), `/design-review` (визуальный аудит живого сайта).
- **Шип:** `/ship` (PR/деплой), `/land-and-deploy` (мерж + деплой + проверка), `/canary`.
- **Прочее:** `/codex` (делегировать Codex), `/learn`, `/retro`, `/document-*`.

Роутинг живёт в `CLAUDE.md`: запрос матчится на скилл (баг → `/investigate`, «does this work»
→ `/qa`, ревью → `/review`, шип → `/ship`).

## Зачем это в deploychan

Для агента-потребителя главное из gstack — **gbrowser**: персистентный браузер под QA и
скрапинг JS-страниц (тот самый «канал 2» из гайда `agent-internet`). Остальные скиллы —
методология рабочего контура под Claude Code: явные роли вместо одного промпта, QA привязан
к диффу, шип одной командой.
