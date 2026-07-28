---
id: obsidian-dataweave
name: 'ObsidianDataWeave: NotebookLM, Atomization, and LLM Wiki'
summary: >-
  KISA's skill: turns Claude Code / Codex into a NotebookLM control panel + .docx import
  with Zettelkasten atomization + a compiled LLM Wiki layer + FTS5 memory across the whole
  Obsidian vault. All programmatic, all into your vault, with no external search dependencies.
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

Turns Claude Code and Codex into a full control panel for NotebookLM and your Obsidian
vault. You run deep research, manage sources, and pull notes out of notebooks — all with a
single natural-language command. In parallel, it imports `.docx` from Google Drive and
atomizes them into Zettelkasten notes with a MOC, tags, and wikilinks. On top — an isolated
**LLM Wiki** layer (a compiled base in the Karpathy style), and **FTS5 memory** — a full-text
index of the entire vault without a single external dependency. Public: `howdeploy/ObsidianDataWeave`, MIT.

Both clients are supported natively: Claude Code (a global skill) and Codex Desktop / CLI / IDE
(a native global skill of its own).

## Four Layers

1. **NotebookLM → Obsidian.** Programmatic control of NotebookLM through `notebooklm-py` as
   a library (not the CLI — strictly one-shot, no retry duplication). Deep/fast research, source
   management, dedup, note extraction, and atomization into the vault.
2. **.docx → Obsidian.** Import from Google Drive (rclone) → parse → atomize → write.
3. **LLM Wiki.** A compiled wiki on top of the atomic notes: it accumulates through an explicit
   merge (not RAG, not a recompute on every query), linked with `[[wikilinks]]`.
4. **FTS5 memory.** A local full-text index of the whole vault on stdlib SQLite, bm25 +
   snippets, auto-updates after every write. Search for agents.

## Installation

```bash
git clone https://github.com/howdeploy/ObsidianDataWeave.git
cd ObsidianDataWeave
bash install.sh --vault-path "/path/to/your/vault"
```

Or hand the agent this one line and it does the rest: *"clone
https://github.com/howdeploy/ObsidianDataWeave.git and run `bash install.sh --vault-path
"/path/to/vault"` in the cloned directory"*.

The installer checks for Python 3.10+, installs the dependencies (`python-docx`, `pyyaml`), and
creates a `config.toml` with the vault path. After installation the skill works from any directory.

| Mode | Flag | What it registers |
|---|---|---|
| **claude** (default) | `--mode claude` | A global skill in `~/.claude/skills/obsidian-dataweave/` plus a block appended to `~/.claude/CLAUDE.md` |
| **codex** | `--mode codex` | A native global skill in `~/.agents/skills/obsidian-dataweave/` for Codex Desktop / CLI / IDE |
| **local** | `--mode local` | Dependencies and config only |

Updating is idempotent — `git pull && bash install.sh`. Skill symlinks refresh themselves,
`migrate.py` appends new config sections (`[memory]`, for instance) and rolls out the FTS5 memory
index. Your `config.toml` and your vault are never overwritten.

## How to Use

After installation, just tell the agent in natural language:

| What to say | What happens |
|---|---|
| `process MyDocument.docx` | Download → parse → atomize → write into the vault |
| `process note "Title"` | Enrich or atomize an existing note |
| `process contacts "Contacts"` | A note with contacts → personal cards + Networking MOC |
| `run research in notebook "<id>" "<query>"` | Deep research in NotebookLM via the API |
| `clean duplicates in notebook "<id>"` | Dedup sources in the notebook |
| `create wiki "<slug>"` | Skeleton of a new LLM Wiki space (project/corpus, RU/EN) |
| `build wiki "<slug>"` | Compile the raw material into pages (guard on `[[wikilinks]]`) |
| `search notes "<query>"` | FTS5 search across the whole vault, notes + wiki (bm25 + snippets) |
| `rebuild the memory index` | Full FTS5 rebuild (`memory_index.py build`) |
| `dedup --dry-run` | Show vault duplicates without touching anything |

Processing modes: **Enrich** (short note → tags/links/expansion, 1→1), **Atomize**
(long → atomic notes + MOC, 1→N), **Contacts** (contacts → cards + Networking MOC).

## LLM Wiki

The third knowledge layer is a compiled wiki in the Karpathy style. It lives in the isolated folder
`<vault>/LLM Wiki/<slug>/`; atomic notes don't go there. It accumulates through an explicit
merge: existing `[[wikilinks]]` must be preserved, otherwise compile fails with
`WIKI_LINKS_LOST`. Two modes: **project** (fixed core pages: overview,
architecture, components, workflows, glossary…) and **corpus** (only entities/concepts grow).

```bash
python3 scripts/wiki_init.py demo --mode project --title "Demo Project"
python3 scripts/wiki_ingest.py demo path/to/article.md --kind articles
python3 scripts/wiki_compile.py demo --since-last-compile
python3 scripts/wiki_lint.py demo --strict
```

All scripts write through a single writer, `vault_writer.py` — the atomic pipelines and the wiki
share one write point.

## NotebookLM: First Login

The Google session is saved in `~/.notebooklm/storage_state.json` — login is one-time.
```bash
python3 -m venv .venv
.venv/bin/python scripts/notebooklm_setup.py --skip-login
# in a SEPARATE terminal window (needs a real TTY):
.venv/bin/notebooklm login   # log in to Google in Chromium → come back → ENTER
```

Two traps worth naming to the person up front. The venv is **mandatory** on Arch / Manjaro /
Debian — the system `pip` is blocked by PEP 668, and installing onto the system Python fails.
And `notebooklm login` must not be run through the `!` prefix inside Claude Code or Codex: that
session has no interactive stdin, so it dies with `Aborted!` while waiting for ENTER.
Then: `process_notebook.py <notebook_id>` (id is the last segment of the notebook URL),
`research_notebook.py run "<id>" "<query>" --mode deep`.

## Requirements

- Python 3.10+ (3.11+ recommended), [rclone](https://rclone.org/) with access to Google Drive
  (for `.docx`), Claude Code or Codex.
- SQLite with FTS5 (stdlib `sqlite3`) — no separate DBMS needed; `doctor.py` checks this.
- **Obsidian plugins:** [Local REST API](https://github.com/coddingtonbear/obsidian-local-rest-api)
  (HTTP interface to the vault) + [MCP Obsidian](https://github.com/MarkusPfundstein/mcp-obsidian)
  (MCP bridge Claude Code ↔ Obsidian).

Related: [NotebookLM++](https://github.com/howdeploy/notebooklmplusplus) — a Chrome extension
for bulk-importing sources into NotebookLM (web, YouTube, playlists, PDF snapshots).
