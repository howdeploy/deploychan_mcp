"""Tests for content ingestion and catalog generation."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from server import config, db, ingest, tools


def test_ingest_counts(seeded):
    s = seeded["summary"]
    assert s["items"] == 4
    assert s["by_type"] == {"skill": 1, "knowledge": 1, "route": 1, "tool": 1}
    assert s["route_steps"] == 2
    # Catalog excludes the base skill -> 3 showcase items.
    assert s["catalog_items"] == 3


def test_catalog_json(seeded):
    catalog = json.loads((seeded["web_dir"] / "catalog.json").read_text(encoding="utf-8"))
    ids = {i["id"] for i in catalog["items"]}
    assert "tailored-install" not in ids  # base skill hidden from the catalog
    assert ids == {"prompt", "route-zero", "tavily-setup"}
    assert catalog["connect"]["clients"]["claude-code"].startswith("claude mcp add")
    assert catalog["profile"]["name"] == "KISA"
    assert "generated" in catalog


def test_step_ids_are_namespaced(seeded):
    from server import config, db

    conn = db.connect_ro(config.DB_PATH)
    try:
        rows = conn.execute("SELECT step_id, ref FROM route_steps ORDER BY idx").fetchall()
    finally:
        conn.close()
    assert [r["step_id"] for r in rows] == ["route-zero:1", "route-zero:2"]
    assert [r["ref"] for r in rows] == ["prompt", "tavily-setup"]


def test_bad_ref_aborts(tmp_path: Path):
    content = tmp_path / "content"
    (content / "routes").mkdir(parents=True)
    (content / "routes" / "broken.md").write_text(
        "---\nid: broken\nname: Broken\nsummary: x\ntype: route\nadded: 2026-01-01\n"
        "steps:\n  - title: Go\n    ref: does-not-exist\n---\n",
        encoding="utf-8",
    )
    with pytest.raises(SystemExit):
        ingest.run_ingest(content_dir=content, db_path=tmp_path / "d.db", web_dir=tmp_path / "w")


def test_missing_required_field_aborts(tmp_path: Path):
    content = tmp_path / "content"
    (content / "knowledge").mkdir(parents=True)
    (content / "knowledge" / "nosummary.md").write_text(
        "---\nid: nosummary\nname: No Summary\ntype: knowledge\nadded: 2026-01-01\n---\nbody\n",
        encoding="utf-8",
    )
    with pytest.raises(SystemExit):
        ingest.run_ingest(content_dir=content, db_path=tmp_path / "d.db", web_dir=tmp_path / "w")


def test_russian_text_is_searchable_via_fts5(tmp_path: Path, corpus: Path, monkeypatch):
    (corpus / "i18n.ru.yml").write_text(
        "prompt:\n"
        "  name: Анатомия промпта\n"
        "  summary: Как устроены роли и ограничения агента.\n"
        "  search: Как задать поведение, обязанности и запреты кодинг-агента.\n"
        "route-zero:\n"
        "  name: От нуля до вайбкодинга\n"
        "  summary: Маршрут для прокачки coding-агента.\n",
        encoding="utf-8",
    )

    db_path = tmp_path / "russian.db"
    ingest.run_ingest(content_dir=corpus, db_path=db_path, web_dir=tmp_path / "web")
    monkeypatch.setattr(config, "DB_PATH", db_path)

    assert [hit["id"] for hit in tools.search_knowledge("обязанности и запреты")] == ["prompt"]
    assert tools.onboard("прокачка агента")["route_id"] == "route-zero"


def test_production_russian_search_covers_every_item():
    content_dir = Path(__file__).resolve().parents[1] / "content"
    item_ids = {item_id for _, item_id, _ in ingest._discover(content_dir)}
    localized = ingest._load_i18n_ru(content_dir)

    assert set(localized) == item_ids
    assert all((localized[item_id].get("search") or "").strip() for item_id in item_ids)


def test_ingest_migrates_the_legacy_fts_schema(tmp_path: Path, corpus: Path):
    db_path = tmp_path / "legacy.db"
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "CREATE VIRTUAL TABLE items_fts USING fts5("
            "name, summary, tags, body, name_ru, summary_ru, body_ru, id UNINDEXED, "
            "tokenize = 'unicode61 remove_diacritics 2')"
        )
    finally:
        conn.close()

    ingest.run_ingest(content_dir=corpus, db_path=db_path, web_dir=tmp_path / "web")

    conn = db.connect_ro(db_path)
    try:
        columns = [row["name"] for row in conn.execute("PRAGMA table_info(items_fts)")]
        rows = conn.execute("SELECT COUNT(*) AS count FROM items_fts").fetchone()["count"]
    finally:
        conn.close()

    assert columns == [
        "name", "summary", "tags", "body", "name_ru", "summary_ru", "search_ru", "id"
    ]
    assert rows == 4
