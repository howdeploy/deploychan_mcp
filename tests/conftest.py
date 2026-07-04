"""Shared fixtures: a tiny content corpus ingested into a temp DB."""

from __future__ import annotations

from pathlib import Path

import pytest

from server import config, ingest

SKILL_MD = """\
---
id: tailored-install
name: Tailored Install
summary: Install skills tailored to THIS user's environment.
type: skill
author: kisa
recommended: true
base: true
reminder: Detect the environment before writing. Never overwrite blindly.
tags: [install, setup]
added: 2026-06-26
allowed-tools: [Read, Bash, Write]
triggers: [install tailored]
---
# Tailored Install
Detect, then install idempotently.
"""

KNOWLEDGE_MD = """\
---
id: prompt
name: Anatomy of a prompt
summary: How KISA structures prompts for a coding agent.
type: knowledge
author: kisa
recommended: true
tags: [prompt]
added: 2026-06-25
source: "YouTube: KISA"
---
# Anatomy of a prompt
Roles, context, constraints. Hooks remind the agent of system instructions.
"""

ROUTE_MD = """\
---
id: route-zero
name: From zero to vibe-coding
summary: Steps from installing an agent to shipping.
type: route
author: kisa
recommended: true
tags: [onboarding]
added: 2026-06-30
steps:
  - title: Read the prompt anatomy
    action: read
    ref: prompt
    body: Understand how prompts are structured.
  - title: Install Tavily
    action: install
    ref: tavily-setup
---
# From zero to vibe-coding
"""

TOOL_MD = """\
---
id: tavily-setup
name: Tavily Setup
summary: Connect Tavily search to your agent.
type: tool
author: third_party
tags: [search]
added: 2026-07-01
source: "https://tavily.com"
---
# Tavily Setup
Install steps for Tavily.
"""

META_YML = """\
connect:
  url: https://mcp.deploychan.webcam/mcp
  transport: http
clients:
  claude-code: "claude mcp add --transport http deploychan https://mcp.deploychan.webcam/mcp"
profile:
  name: KISA
  links:
    telegram: https://t.me/deployladeploy
"""


def write_corpus(root: Path) -> None:
    (root / "skills" / "tailored-install").mkdir(parents=True)
    (root / "skills" / "tailored-install" / "SKILL.md").write_text(SKILL_MD, encoding="utf-8")
    (root / "knowledge").mkdir()
    (root / "knowledge" / "prompt.md").write_text(KNOWLEDGE_MD, encoding="utf-8")
    (root / "routes").mkdir()
    (root / "routes" / "route-zero.md").write_text(ROUTE_MD, encoding="utf-8")
    (root / "tools").mkdir()
    (root / "tools" / "tavily-setup.md").write_text(TOOL_MD, encoding="utf-8")
    (root / "meta.yml").write_text(META_YML, encoding="utf-8")


@pytest.fixture
def corpus(tmp_path: Path):
    content = tmp_path / "content"
    content.mkdir()
    write_corpus(content)
    return content


@pytest.fixture
def seeded(tmp_path: Path, corpus: Path, monkeypatch):
    """Ingest the corpus into a temp DB and point the tools at it."""
    db_path = tmp_path / "data" / "deploychan.db"
    web_dir = tmp_path / "web"
    summary = ingest.run_ingest(content_dir=corpus, db_path=db_path, web_dir=web_dir)
    monkeypatch.setattr(config, "DB_PATH", db_path)
    return {"db_path": db_path, "web_dir": web_dir, "summary": summary}
