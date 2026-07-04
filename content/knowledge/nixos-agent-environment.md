---
id: nixos-agent-environment
name: 'The agent on NixOS: environment and working patterns'
summary: >-
  How the agent survives and works on NixOS: coreutils aren't in PATH → Python
  fallback, the real binaries in /run/current-system/sw/bin, the /bin/bash
  symlink, and managing Hermes (connecting MCP via mcp_servers, pty for
  interactive prompts, restarting the gateway).
type: knowledge
author: kisa
recommended: false
added: 2026-07-04
tags: [nixos, agent, hermes, environment, python]
source: https://mcp.deploychan.webcam/docs
---

# The agent on NixOS: environment and working patterns

NixOS is a declarative, store-based filesystem. The usual POSIX utilities
(`cat`, `ls`, `find`, `grep`, `which`, `rm`) are **not guaranteed to be in PATH**. An agent
used to ordinary Linux trips on the very first command. Below — reliable workarounds,
tested on a live system.

## Python as the universal fallback

Python 3 is always present on NixOS. No utility — reach for Python.

| Utility | In PATH? | Replacement |
|---|---|---|
| `cat` | No | `python3 -c "print(open('f').read())"` |
| `ls` | No | `python3 -c "import os; print(os.listdir('.'))"` |
| `find` | No | `python3` with `os.walk()` |
| `rm` | No | `python3 -c "import os; os.remove('f')"` |
| `grep` | No | the `search_files` tool or string search in Python |
| `which` | No | not needed — use `python3` |
| `df` | No | `/run/current-system/sw/bin/df -h` |
| `free` | No | `/run/current-system/sw/bin/free -h` |

## File operations

### Write a file
```bash
python3 << 'PYEOF'
with open('/path/to/file', 'w') as f:
    f.write("content here")
PYEOF
```

### Read a file
```bash
python3 -c "print(open('/path/to/file').read())"
```

### Check existence
```bash
python3 -c "import os; p='/path/to/file'; print(f'exists={os.path.exists(p)}, size={os.path.getsize(p)}')"
```

### Create directories
```bash
python3 -c "import os; os.makedirs('/path/to/dir', exist_ok=True)"
```

## System discovery

The real binaries live in `/nix/store/` and are reachable via `/run/current-system/sw/bin/`:
```bash
/run/current-system/sw/bin/nixos-version
/run/current-system/sw/bin/df -h / /home
/run/current-system/sw/bin/free -h
/run/current-system/sw/bin/systemctl --user list-units --type=service
```

## Pitfalls

1. **Never assume coreutils are in PATH.** Use explicit paths or Python.
2. **The `write_file` tool may fail** — it shells out to `cat`/`rm`.
3. **`/bin/bash` doesn't exist.** Symlink it: `sudo ln -sf /run/current-system/sw/bin/bash /bin/bash`
4. **NixOS cleanliness** — `/bin`, `/usr/bin`, `/usr/local/bin` are often empty. The real binaries are in `/nix/store/`, reachable via `/run/current-system/sw/bin/`.
5. **`nix-shell` is slow** — for one-off tasks reach for Python, not nix-shell.

## Hermes on NixOS

### Connect an MCP server
```bash
hermes mcp add SERVER_NAME --url https://mcp.example.com/mcp
```
Interactive prompts: auth=N, key=Enter, tools=Y. Needs `pty=true`.

**Pitfall — config sections.** `hermes config set mcp.*` writes to the `mcp:` section,
while `hermes mcp add` writes to `mcp_servers:`. Hermes reads from `mcp_servers:`. Use
`hermes mcp add`, not a manual edit of `mcp:`.

### Interactive Hermes commands
For `hermes mcp add`, `hermes setup` and the like, use `pty=true` — they call
`getpass`, which fails without a TTY.

### Restarting the gateway
You can't restart it from your own agent session. Use a separate terminal or a cronjob:
```
cronjob(action='create', schedule='every 1h', no_agent=True,
    script='systemctl --user restart hermes-gateway')
```

### External install scripts
Many tools hardcode `/bin/bash`. Workaround:
```bash
sudo ln -sf /run/current-system/sw/bin/bash /bin/bash
```
Temporary — only for the duration of the install.
