"""Runtime configuration, driven by environment variables.

Every path and network setting is overridable so the same code runs locally, in Docker,
and on a self-hosted VPS without edits.
"""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _path(env: str, default: Path) -> Path:
    val = os.environ.get(env)
    return Path(val) if val else default


# Source content, generated web artifacts, and the SQLite database.
CONTENT_DIR = _path("DEPLOYCHAN_CONTENT_DIR", ROOT / "content")
WEB_DIR = _path("DEPLOYCHAN_WEB_DIR", ROOT / "web")
DB_PATH = _path("DEPLOYCHAN_DB_PATH", ROOT / "data" / "deploychan.db")

# Network. The app binds inside the container; the reverse proxy sits in front.
HOST = os.environ.get("DEPLOYCHAN_HOST", "0.0.0.0")
PORT = int(os.environ.get("DEPLOYCHAN_PORT", "8080"))
MCP_PATH = os.environ.get("DEPLOYCHAN_MCP_PATH", "/mcp")

# Default number of results for search_knowledge.
SEARCH_DEFAULT_LIMIT = 5
SEARCH_MAX_LIMIT = 20


def allowed_hosts() -> list[str]:
    """Host header allow-list for DNS-rebinding protection (see docs/CONTRACT.md §9).

    Includes the public domain plus localhost variants for local testing. Override with
    ``DEPLOYCHAN_ALLOWED_HOSTS`` (comma-separated) when self-hosting on another domain.
    """
    # TrustedHostMiddleware strips the port from the Host header, so list bare hosts only.
    raw = os.environ.get(
        "DEPLOYCHAN_ALLOWED_HOSTS",
        "mcp.deploychan.webcam,localhost,127.0.0.1",
    )
    return [h.strip() for h in raw.split(",") if h.strip()]
