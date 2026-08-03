"""SQLite + FTS5 schema and connection helpers. See docs/CONTRACT.md §3.

Runtime is read-only: ``ingest`` (offline) is the only writer. The server opens the DB
immutable/read-only, so many concurrent readers never contend and the process cannot
mutate the database — a security and concurrency property, not just a convention.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from .config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    id           TEXT PRIMARY KEY,
    type         TEXT NOT NULL CHECK(type IN ('skill','knowledge','route','tool')),
    author       TEXT NOT NULL DEFAULT 'kisa' CHECK(author IN ('kisa','third_party')),
    name         TEXT NOT NULL,
    summary      TEXT NOT NULL DEFAULT '',
    body         TEXT NOT NULL DEFAULT '',
    recommended  INTEGER NOT NULL DEFAULT 0,
    is_base      INTEGER NOT NULL DEFAULT 0,
    added        TEXT,
    source       TEXT,
    reminder     TEXT,
    tags         TEXT NOT NULL DEFAULT '[]',
    extra        TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS route_steps (
    step_id   TEXT PRIMARY KEY,
    route_id  TEXT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    idx       INTEGER NOT NULL,
    title     TEXT NOT NULL,
    action    TEXT,
    ref       TEXT,
    body      TEXT NOT NULL DEFAULT '',
    UNIQUE(route_id, idx)
);

CREATE VIRTUAL TABLE IF NOT EXISTS items_fts USING fts5(
    name, summary, tags, body, name_ru, summary_ru, search_ru, id UNINDEXED,
    tokenize = 'unicode61 remove_diacritics 2'
);
"""

# Column layout the FTS index must have. The Russian columns sit AFTER ``body`` so the
# positional ``snippet(items_fts, 3, ...)`` in tools.py keeps pointing at the English body.
_FTS_COLUMNS = ("name", "summary", "tags", "body", "name_ru", "summary_ru", "search_ru", "id")


def connect_rw(path: Path | str = DB_PATH) -> sqlite3.Connection:
    """Open a read-write connection (used only by ingest)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def connect_ro(path: Path | str = DB_PATH) -> sqlite3.Connection:
    """Open a read-only, immutable connection (used by the server per request).

    ``immutable=1`` tells SQLite the file will not change while open: no locking, no
    ``-wal``/``-shm`` files, fastest possible concurrent reads. Valid because ingest only
    runs at startup, before any worker serves traffic; a re-ingest requires a restart.
    """
    uri = f"file:{Path(path)}?mode=ro&immutable=1"
    conn = sqlite3.connect(uri, uri=True, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    _migrate_fts(conn)
    conn.executescript(SCHEMA)


def _migrate_fts(conn: sqlite3.Connection) -> None:
    """Drop items_fts when its column layout is stale, so the schema below can recreate it.

    ``CREATE VIRTUAL TABLE IF NOT EXISTS`` silently keeps an existing index with the old
    columns, and ingest only DELETEs rows — so without this a schema change would leave the
    index permanently missing the new columns. Dropping is safe: ingest rebuilds the whole
    index from content/ on every run.
    """
    row = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='items_fts'"
    ).fetchone()
    if row is None:
        return
    sql = row["sql"] if isinstance(row, sqlite3.Row) else row[0]
    if any(col not in sql for col in _FTS_COLUMNS):
        conn.execute("DROP TABLE items_fts")
