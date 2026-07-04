---
id: nixos-agent-environment
name: 'Агент на NixOS: окружение и рабочие паттерны'
summary: >-
  Как агент выживает и работает на NixOS: coreutils нет в PATH → Python-фолбэк,
  реальные бинарники в /run/current-system/sw/bin, симлинк /bin/bash, и управление
  Hermes (подключение MCP через mcp_servers, pty для интерактива, рестарт gateway).
type: knowledge
author: kisa
recommended: false
added: 2026-07-04
tags: [nixos, agent, hermes, environment, python]
source: https://mcp.deploychan.webcam/docs
---

# Агент на NixOS: окружение и рабочие паттерны

NixOS — декларативная, store-based файловая система. Обычные POSIX-утилиты
(`cat`, `ls`, `find`, `grep`, `which`, `rm`) **не гарантированы в PATH**. Агент,
привыкший к обычному Linux, спотыкается на первой же команде. Ниже — надёжные обходы,
проверенные на живой системе.

## Python как универсальный фолбэк

Python 3 на NixOS есть всегда. Нет утилиты — бери Python.

| Утилита | В PATH? | Замена |
|---|---|---|
| `cat` | Нет | `python3 -c "print(open('f').read())"` |
| `ls` | Нет | `python3 -c "import os; print(os.listdir('.'))"` |
| `find` | Нет | `python3` с `os.walk()` |
| `rm` | Нет | `python3 -c "import os; os.remove('f')"` |
| `grep` | Нет | инструмент `search_files` или поиск строк в Python |
| `which` | Нет | не нужен — используй `python3` |
| `df` | Нет | `/run/current-system/sw/bin/df -h` |
| `free` | Нет | `/run/current-system/sw/bin/free -h` |

## Файловые операции

### Записать файл
```bash
python3 << 'PYEOF'
with open('/path/to/file', 'w') as f:
    f.write("content here")
PYEOF
```

### Прочитать файл
```bash
python3 -c "print(open('/path/to/file').read())"
```

### Проверить существование
```bash
python3 -c "import os; p='/path/to/file'; print(f'exists={os.path.exists(p)}, size={os.path.getsize(p)}')"
```

### Создать директории
```bash
python3 -c "import os; os.makedirs('/path/to/dir', exist_ok=True)"
```

## Системный discovery

Реальные бинарники живут в `/nix/store/` и доступны через `/run/current-system/sw/bin/`:
```bash
/run/current-system/sw/bin/nixos-version
/run/current-system/sw/bin/df -h / /home
/run/current-system/sw/bin/free -h
/run/current-system/sw/bin/systemctl --user list-units --type=service
```

## Подводные камни

1. **Никогда не считай, что coreutils в PATH.** Используй явные пути или Python.
2. **Инструмент `write_file` может падать** — он шеллит на `cat`/`rm`.
3. **`/bin/bash` не существует.** Симлинк: `sudo ln -sf /run/current-system/sw/bin/bash /bin/bash`
4. **Чистота NixOS** — `/bin`, `/usr/bin`, `/usr/local/bin` часто пусты. Реальные бинарники в `/nix/store/`, доступны через `/run/current-system/sw/bin/`.
5. **`nix-shell` медленный** — для разовых задач бери Python, а не nix-shell.

## Hermes на NixOS

### Подключить MCP-сервер
```bash
hermes mcp add SERVER_NAME --url https://mcp.example.com/mcp
```
Интерактивные промпты: auth=N, key=Enter, tools=Y. Нужен `pty=true`.

**Подводный камень — секции конфига.** `hermes config set mcp.*` пишет в секцию `mcp:`,
а `hermes mcp add` — в `mcp_servers:`. Hermes читает из `mcp_servers:`. Используй
`hermes mcp add`, а не ручную правку `mcp:`.

### Интерактивные команды Hermes
Для `hermes mcp add`, `hermes setup` и подобных используй `pty=true` — они дёргают
`getpass`, который падает без TTY.

### Рестарт gateway
Нельзя рестартить из своей же агент-сессии. Используй отдельный терминал или cronjob:
```
cronjob(action='create', schedule='every 1h', no_agent=True,
    script='systemctl --user restart hermes-gateway')
```

### Внешние install-скрипты
Многие тулзы хардкодят `/bin/bash`. Обход:
```bash
sudo ln -sf /run/current-system/sw/bin/bash /bin/bash
```
Временно — только на время установки.
