---
id: obsidian-dataweave
name: 'ObsidianDataWeave: NotebookLM, атомизация и LLM Wiki'
summary: >-
  Скилл KISA: превращает Claude Code / Codex в пульт NotebookLM + импорт .docx с
  Zettelkasten-атомизацией + скомпилированный LLM Wiki-слой + FTS5-память по всему
  Obsidian vault. Всё программно, всё в твой vault, без внешних зависимостей поиска.
type: skill
author: kisa
recommended: false
added: 2026-07-04
tags: [obsidian, notebooklm, zettelkasten, llm-wiki, fts5, memory, notes]
source: https://github.com/howdeploy/ObsidianDataWeave
description: >-
  Use when the user wants to control NotebookLM programmatically, import .docx into an
  Obsidian vault as atomic Zettelkasten notes, build a compiled LLM Wiki layer, or
  full-text-search the whole vault. Claude Code and Codex both supported.
license: MIT
---

# ObsidianDataWeave

Превращает Claude Code и Codex в полноценный пульт управления NotebookLM и твоим Obsidian
vault. Запускаешь deep research, управляешь источниками, вытаскиваешь заметки из нотбуков —
всё одной командой на естественном языке. Параллельно импортирует `.docx` из Google Drive и
атомизирует их в Zettelkasten-заметки с MOC, тегами и вики-ссылками. Поверх — изолированный
**LLM Wiki**-слой (скомпилированная база по Карпати), и **FTS5-память** — полнотекстовый
индекс всего vault без единой внешней зависимости. Публичный: `howdeploy/ObsidianDataWeave`, MIT.

Оба клиента поддержаны: Claude Code (скилл) и Codex (`AGENTS.md`).

## Четыре слоя

1. **NotebookLM → Obsidian.** Программный контроль NotebookLM через `notebooklm-py` как
   библиотеку (не CLI — строго one-shot, без retry-дупликации). Deep/fast research, управление
   источниками, дедуп, извлечение заметок и атомизация в vault.
2. **.docx → Obsidian.** Импорт из Google Drive (rclone) → парс → атомизация → запись.
3. **LLM Wiki.** Скомпилированная вики поверх атомарных заметок: накапливается через явный
   merge (не RAG, не пересчёт на каждый запрос), связана `[[вики-ссылками]]`.
4. **FTS5-память.** Локальный полнотекстовый индекс всего vault на stdlib SQLite, bm25 +
   сниппеты, обновляется сам после каждой записи. Поиск для агентов.

## Установка

```bash
git clone https://github.com/howdeploy/ObsidianDataWeave.git
cd ObsidianDataWeave
bash install.sh --vault-path "/путь/к/вашему/vault"
```

Установщик проверит Python 3.10+, поставит зависимости (`python-docx`, `pyyaml`), создаст
`config.toml` с путём к vault, зарегистрирует навык глобально в `~/.claude/skills/obsidian-dataweave/`
и допишет блок в `~/.claude/CLAUDE.md`. После установки навык работает из любой директории.

Режимы: `--mode claude` (по умолчанию), `--mode codex` (проверка `AGENTS.md`), `--mode local`
(только зависимости + config). Обновление идемпотентно: `git pull && bash install.sh`.

## Как пользоваться

После установки просто говоришь агенту на естественном языке:

| Что сказать | Что произойдёт |
|---|---|
| `process МойДокумент.docx` | Скачать → разобрать → атомизировать → записать в vault |
| `обработай заметку "Название"` | Enrich или atomize существующей заметки |
| `обработай контакты "Контакты"` | Заметка с контактами → персональные карточки + Networking MOC |
| `запусти ресерч в ноутбуке "<id>" "<запрос>"` | Deep research в NotebookLM через API |
| `почисти дубли в ноутбуке "<id>"` | Дедуп источников в нотбуке |
| `создай вики "<slug>"` | Скелет новой LLM Wiki-space (project/corpus, RU/EN) |
| `собери вики "<slug>"` | Скомпилировать сырьё в страницы (guard на `[[wikilinks]]`) |
| `найди в заметках "<запрос>"` | FTS5-поиск по всему vault (bm25 + сниппеты) |

Режимы обработки: **Enrich** (короткая заметка → теги/ссылки/расширение, 1→1), **Atomize**
(длинная → атомарные заметки + MOC, 1→N), **Contacts** (контакты → карточки + Networking MOC).

## LLM Wiki

Третий слой знаний — скомпилированная вики в стиле Карпати. Живёт в изолированной папке
`<vault>/LLM Wiki/<slug>/`; атомарные заметки туда не попадают. Накапливается через явный
merge: существующие `[[вики-ссылки]]` обязаны сохраняться, иначе compile падает с
`WIKI_LINKS_LOST`. Два режима: **project** (фиксированные core-страницы: overview,
architecture, components, workflows, glossary…) и **corpus** (растут только entities/concepts).

```bash
python3 scripts/wiki_init.py demo --mode project --title "Demo Project"
python3 scripts/wiki_ingest.py demo path/to/article.md --kind articles
python3 scripts/wiki_compile.py demo --since-last-compile
python3 scripts/wiki_lint.py demo --strict
```

Все скрипты пишут через единственный writer `vault_writer.py` — атомарные пайплайны и wiki
делят одну точку записи.

## NotebookLM: первый вход

Сессия Google сохраняется в `~/.notebooklm/storage_state.json` — вход одноразовый.
```bash
python3 -m venv .venv
.venv/bin/python scripts/notebooklm_setup.py --skip-login
# в ОТДЕЛЬНОМ окне терминала (нужен настоящий TTY):
.venv/bin/notebooklm login   # войти в Google в Chromium → вернуться → ENTER
```
Дальше: `process_notebook.py <notebook_id>` (id — последний сегмент URL нотбука),
`research_notebook.py run "<id>" "<query>" --mode deep`.

## Требования

- Python 3.10+ (рекомендуется 3.11+), [rclone](https://rclone.org/) с доступом к Google Drive
  (для `.docx`), Claude Code или Codex.
- SQLite с FTS5 (stdlib `sqlite3`) — отдельная СУБД не нужна; проверяет `doctor.py`.
- **Плагины Obsidian:** [Local REST API](https://github.com/coddingtonbear/obsidian-local-rest-api)
  (HTTP-интерфейс к vault) + [MCP Obsidian](https://github.com/MarkusPfundstein/mcp-obsidian)
  (MCP-мост Claude Code ↔ Obsidian).

Смежное: [NotebookLM++](https://github.com/howdeploy/notebooklmplusplus) — Chrome-расширение
для массового импорта источников в NotebookLM (веб, YouTube, плейлисты, PDF-снимки).
